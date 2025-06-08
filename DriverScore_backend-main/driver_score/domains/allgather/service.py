import logging
import tarfile
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import magic
import numpy as np
import pandas as pd
from fastapi import HTTPException, UploadFile, status
from scipy.spatial.transform import Rotation

from driver_score.core.database import db_engine, get_db_session
from driver_score.core.models import CollectedDataFile, GpsSample, ImuSample, UploadLog
from driver_score.settings import settings

from ..driver.service import DriverService
from ..run.service import RunService
from .constant import CalibrationStatus, CollectedDataType

logger = logging.getLogger(__name__)


class AllGatherService:
    def __init__(self, run_id: str):
        self.run_id = run_id

    async def extract_and_store_file(self, file: UploadFile):
        """
        Extracts and stores the contents of an uploaded file.

        Args:
            file (UploadFile): The uploaded file.

        Returns:
            str: The timestamp folder where the file was extracted to.

        Raises:
            HTTPException: If the uploaded file is not a ZIP archive.
        """
        contents = await file.read()

        # Check if the MIME type is that of a ZIP file
        mime_type = magic.from_buffer(contents, mime=True)
        if mime_type not in [
            "application/zip",
            "application/gzip",
            "application/x-gzip",
        ]:
            raise HTTPException(
                status_code=400, detail=f"Uploaded file is not a ZIP archive. Found {mime_type} instead!"
            )

        timestamp_folder = AllGatherService._extract_zip_file(file=file, contents=contents, mime_type=mime_type)
        return timestamp_folder

    async def upload_smartphone_data(self, filename: str, timestamp_folder: Path) -> None:
        """
        Uploads smartphone data, processes it, updates the database, and logs processing status.

        Args:
            filename (str): The name of the file being uploaded.
            timestamp_folder (Path): The folder containing the uploaded file and its timestamp.

        Returns:
            None
        """
        # Currently assuming user upload and collection is same, will change later
        # if collector user information is passed through zip
        upload_file_created_on = self._get_file_created_on(timestamp_folder)
        user_id = int(next(timestamp_folder.iterdir()).name)

        # Persist driver into DB
        driver_service = DriverService(driver_id=user_id)
        if (await driver_service.get_current_driver()) is None:
            await driver_service.persist_driver_to_db()

        # Persist run into DB
        run_service = RunService(run_id=self.run_id)
        # TODO: Pass session into parameters list to have control over transaction.
        # TODO: For example, we can rollback everything if a file is not uploaded successfully.
        await run_service.persist_run_to_db(driver_id=user_id, start_time=upload_file_created_on)

        with get_db_session() as session:
            db_upload_log = UploadLog(
                uploaded_by=user_id,
                uploaded_on=datetime.now(),
                upload_status="PROCESSING",
                log_message="Input data is has been saved and is being unpacked",
                file_name=filename,
            )
            session.add(db_upload_log)

        if self._check_duplicate_upload(user_id, filename, upload_file_created_on):
            with get_db_session() as session:
                db_upload_log = UploadLog(
                    uploaded_by=user_id,
                    uploaded_on=datetime.now(),
                    upload_status="DUPLICATE FILE",
                    log_message="This file has already been uploaded and processed in the past",
                    file_name=filename,
                )
                session.add(db_upload_log)

            raise HTTPException(status.HTTP_409_CONFLICT, detail="File already exists!")

        # TODO: Update other fields of the Collected_Data_File table
        file_id = None
        with get_db_session() as session:
            db_collected_file = CollectedDataFile(
                # device_type=1,  # 1 for smartphone device
                file_name=filename,
                collected_by=user_id,
                collected_on=upload_file_created_on,
                # uploaded_by=user_id,
                # uploaded_on=datetime.now(),
                # proc_status="UPLOAD",
            )
            session.add(db_collected_file)
            file_id = db_collected_file.file_id

        # ensuring uploaded zip file has correct folder structure
        nan_imei_folder = self._check_uploaded_folder_structure(timestamp_folder, user_id, filename)

        # Proccessing all of the data within the uploaded zip and calling the
        # appropriate functions based on type of data (GPS, acceleration, etc)
        try:
            calibration_status = CalibrationStatus.GOOD_CALIBRATION

            for data_folder in nan_imei_folder.iterdir():
                if data_folder.name == CollectedDataType.CALIBRATION.value:
                    calibration_folder = data_folder
                    # ! Cannot reuse timestamp because calibration is done before timer starts
                    calibration_csv = next(calibration_folder.iterdir())

                    if calibration_csv.exists():
                        transform, flattened = AllGatherService._reformat_phone_calib_data(calibration_csv)
                        if transform is None and flattened is None:
                            logger.info("Improperly formatted transformation matrix")
                            calibration_status = CalibrationStatus.IMPROPER_CALIBRATION
                            continue
                    else:
                        calibration_status = CalibrationStatus.NO_CALIBRATION

                if data_folder.name == CollectedDataType.CAMERA.value:
                    continue

                if data_folder.name == CollectedDataType.ACCELERATION.value:
                    # open file and check to see if it has orientation header. If so skip the first line when uploading to pandas df
                    acc_folder = data_folder
                    timestamp = timestamp_folder.name
                    acc_csv = acc_folder / f"{timestamp}_acc.csv"

                    with open(acc_csv) as data_file:
                        first_line = data_file.readline()
                        skip_first = "orientation" in first_line
                        df = pd.read_csv(acc_csv, skiprows=1) if skip_first else pd.read_csv(acc_csv)

                    imu_df = self._reformat_phone_imu(df, file_id)
                    imu_df["run_id"] = self.run_id

                    if calibration_status == CalibrationStatus.GOOD_CALIBRATION:
                        imu_df = self._apply_calibration_transform(transform, imu_df)

                    imu_df.to_sql(ImuSample.__tablename__, con=db_engine, if_exists="append", index=False)

                elif data_folder.name == CollectedDataType.LOCATION.value:
                    location_folder = data_folder
                    timestamp = timestamp_folder.name
                    gps_csv = location_folder / f"{timestamp}_loc.csv"
                    df = pd.read_csv(gps_csv)
                    gdf = self._reformat_phone_gps(df)
                    gdf.to_postgis(
                        GpsSample.__tablename__,
                        db_engine,
                        if_exists="append",
                        index=False,
                    )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error in format of CSV data, reading/transforming CSV data or writing data to DB, deleting collected file. Detail: {e}",
            )
            # TODO: Update error checking later
        #     if db_upload_log.upload_status == "Processing":
        #         db_upload_log.upload_status = "ERROR"
        #         db_upload_log.log_message = (
        #             "An error has occured in reading the CSV data and writing said data to the database"
        #         )
        #         db.add(db_upload_log)
        #     db.delete(db_collected_file)
        #     db.commit()
        #     return "Fail"
        # db_upload_log.upload_status = "SUCCESS"
        # db_upload_log.log_message = "File has been successfully processed and uploaded into the database"
        # db.add(db_upload_log)
        # db.commit()

    def _check_duplicate_upload(self, user_id: str, filename: str, timestamp: datetime) -> bool:
        """Function for getting the created date of an uploaded file from the first"""
        return False
        with get_db_session() as session:
            results = (
                session.query(CollectedDataFile)
                .filter(
                    CollectedDataFile.collected_by == user_id,
                    CollectedDataFile.file_name == filename,
                    CollectedDataFile.collected_on == timestamp,
                )
                .all()
            )
            return bool(results)

    def _get_file_created_on(self, folder: Path) -> datetime:
        """Get the created date of an uploaded file from the first"""
        date_format = settings.COLLECTED_DATA_FOLDER_FORMAT
        return datetime.strptime(str(folder.name), date_format)

    def _check_uploaded_folder_structure(self, timestamp_folder: Path, user_id: str, filename: str) -> Path | None:
        try:
            driver_id_folder = next(timestamp_folder.iterdir())
            nan_imei_folder = next(driver_id_folder.iterdir())

            collected_data_folder_names = [data_folder.name for data_folder in nan_imei_folder.iterdir()]
            if len(set(collected_data_folder_names).intersection({"acceleration", "location"})) != 2:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Require AT LEAST acceleration and location folders!",
                )

            for data_folder in nan_imei_folder.iterdir():
                len_data_folder = len(list(data_folder.iterdir()))

                if len_data_folder != 1:
                    with get_db_session() as session:
                        log_message = f"{data_folder} must only have EXACTLY ONE .csv file!"
                        db_upload_log = UploadLog(
                            uploaded_by=user_id,
                            uploaded_on=datetime.now(),
                            upload_status="ERROR",
                            log_message=log_message,
                            file_name=filename,
                        )
                        session.add(db_upload_log)

                    raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=log_message)

        except Exception as e:
            # TODO: Replace with logger + logic seems weird, look into it later
            print(str(e))
            print("Error in verifying file structure of input")
            print("Deleting collected file from DB")
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid folder structure. Detail: {e}")
            # if db_upload_log.upload_status == "Processing":
            #     db_upload_log.upload_status = "ERROR"
            #     db_upload_log.log_message = "An error has occured in verifying the file structure of the zip"
            #     db.add(db_upload_log)

            # db.delete(db_collected_file)
            # db.commit()

        return nan_imei_folder

    def _reformat_phone_gps(self, df):
        """
        Function for formatting gps data collected from smartphones
        Includes getting rid of duplicate gps data and correcting column names
        Also transforms input dataframe into geodataframe to include geometry column
        """

        df = df.drop(["timestamp_utc_gps"], axis=1)
        df["run_id"] = self.run_id
        df = df.drop_duplicates(
            subset=[
                "latitude_dd",
                "longitude_dd",
                "altitude_m",
                "bearing_deg",
                "accuracy_m",
                " speed_ms",
                " speed_accuracy_ms",
            ],
            keep="first",
        )

        df = df.rename(
            columns={
                "timestamp_utc_local": "timestamp",
                "latitude_dd": "latitude",
                "longitude_dd": "longitude",
                "altitude_m": "altitude",
                "bearing_deg": "heading",
                "accuracy_m": "pos_accuracy",
                " speed_ms": "velocity",
                " speed_accuracy_ms": "vel_accuracy",
            }
        )
        df["timestamp"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(x / 1000.0))
        self._validate_data(df)
        gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df["longitude"], df["latitude"]), crs=4326)
        return gdf

    def _reformat_phone_imu(self, df: pd.DataFrame, file_id: int) -> pd.DataFrame:
        """
        Formats the smartphone IMU data DataFrame by renaming columns and applying necessary conversions.

        Parameters:
        - df (pd.DataFrame): The input DataFrame containing smartphone IMU data.
        - file_id (int): The ID of the file associated with the data.

        Returns:
        - pd.DataFrame: The formatted DataFrame after column renaming and timestamp conversion.
        """
        df = df.drop(
            ["timestamp_nanosecond", "sensor_timestamp_milliseconds", "bbi", "rotation_cos_theta_by_2"],
            axis=1,
            errors="ignore",
        )
        # TODO: Fix file_id
        # df["file_id"] = file_id

        # ask about inclination, rotation_cos_theta_by_2, and bbi columns
        df = df.rename(
            columns={
                "local_timestamp_milliseconds": "timestamp",
                "accel_x_mps2": "acceleration_x_ms2",
                "accel_y_mps2": "acceleration_y_ms2",
                "accel_z_mps2": "acceleration_z_ms2",
                "angvelocity_x_radps": "angular_velocity_x_rads",
                "angvelocity_y_radps": "angular_velocity_y_rads",
                "angvelocity_z_radps": "angular_velocity_z_rads",
                "yaw": "yaw_rad",
                "pitch": "pitch_rad",
                "roll": "roll_rad",
            }
        )
        df["timestamp"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(x / 1000.0))
        self._validate_data(df)
        return df

    def _validate_data(self, df: pd.DataFrame) -> None:
        """
        Checking if the csv data is valid, or if it could have been corrupted by being edited in excel.
        """
        if len(df["timestamp"]) - len(df["timestamp"].drop_duplicates()) >= len(df["timestamp"]) * 0.5:
            log_message = "Acceleration/IMU data or location/GPS data is not present in zip file"
            # with get_db_session() as session:
            #     # TODO: Update later. Probably will need to store user_id and file_name as attributes for log
            #     db_upload_log = UploadLog(
            #         uploaded_by=user_id,
            #         uploaded_on=datetime.now(),
            #         upload_status="ERROR",
            #         log_message=log_message,
            #         file_name=filename,
            #     )
            #     session.add(db_upload_log)
            raise ValueError(log_message)

    def _apply_calibration_transform(self, transform, imu_df):
        """
        Applies a calibration transform to the given inertial measurement unit (IMU) data frame.

        Parameters:
            transform: The calibration transformation matrix.
            imu_df: The IMU data frame containing columns: acceleration_x_ms2, acceleration_y_ms2, acceleration_z_ms2,
                     angular_velocity_x_rads, angular_velocity_y_rads, angular_velocity_z_rads,
                     rotation_x_sin_theta_by_2, rotation_y_sin_theta_by_2, rotation_z_sin_theta_by_2.

        Returns:
            The IMU data frame with the calibration transform applied.
        """
        imu_df[["acceleration_x_ms2", "acceleration_y_ms2", "acceleration_z_ms2"]] = imu_df.apply(
            lambda x: AllGatherService._matrix_transform(
                x["acceleration_x_ms2"], x["acceleration_y_ms2"], x["acceleration_z_ms2"], transform
            ),
            axis=1,
            result_type="expand",
        )

        imu_df[["angular_velocity_x_rads", "angular_velocity_y_rads", "angular_velocity_z_rads"]] = imu_df.apply(
            lambda x: AllGatherService._matrix_transform(
                x["angular_velocity_x_rads"], x["angular_velocity_y_rads"], x["angular_velocity_z_rads"], transform
            ),
            axis=1,
            result_type="expand",
        )

        imu_df[["rotation_x_sin_theta_by_2", "rotation_y_sin_theta_by_2", "rotation_z_sin_theta_by_2"]] = imu_df.apply(
            lambda x: AllGatherService._matrix_transform(
                x["rotation_x_sin_theta_by_2"],
                x["rotation_y_sin_theta_by_2"],
                x["rotation_z_sin_theta_by_2"],
                transform,
            ),
            axis=1,
            result_type="expand",
        )
        return imu_df

    @staticmethod
    def _matrix_transform(x, y, z, transform):
        """
        Applies a matrix transformation to the input x, y, z coordinates using the provided transform matrix.

        Parameters:
            x: The x coordinate.
            y: The y coordinate.
            z: The z coordinate.
            transform: The transformation matrix.

        Returns:
            A list of transformed coordinates.
        """
        return list(transform.apply(np.array([x, y, z])))

    @staticmethod
    def _reformat_phone_calib_data(calibration_csv):
        def get_local_z_vects(calibration_file: str) -> tuple[np.ndarray, np.ndarray]:
            df = pd.read_csv(calibration_file)
            g_meas = df.iloc[:, 2:5].to_numpy()
            unit_g_meas = (g_meas.T / (np.linalg.norm(g_meas, axis=1))).T
            local_z = unit_g_meas.sum(axis=0) / np.linalg.norm(unit_g_meas.sum(axis=0))

            return local_z, unit_g_meas

        def get_transformation(local_z) -> Rotation:
            unit_local_z = local_z / np.linalg.norm(local_z)
            unit_new_z = np.array([0.0, 0.0, 1.0])
            dot_product = np.dot(unit_new_z, unit_local_z)
            angle = np.arccos(dot_product)

            vect = np.cross(unit_local_z, unit_new_z)
            vect = vect / np.linalg.norm(vect)

            return Rotation.from_rotvec(angle * vect)

        local_z, unit_g = get_local_z_vects(calibration_csv)
        transform = get_transformation(local_z)
        transform_matrix = transform.as_matrix()

        if transform_matrix.shape != (3, 3):
            return None, None
        flattened = transform_matrix.flatten().tolist()
        if len(flattened) != 9:
            return None, None

        return transform, flattened

    @staticmethod
    def _extract_zip_file(file: UploadFile, contents: bytes, mime_type: str) -> Path:
        temp_dir_path = Path(tempfile.mkdtemp())

        # Write the uploaded file to a temporary file within the temp directory
        temp_file_path = temp_dir_path / str(file.filename)
        with open(str(temp_file_path), "wb") as temp_file:
            temp_file.write(contents)

        # Extract the .tar.gz file
        if mime_type in ["application/gzip", "application/x-gzip"]:
            with tarfile.open(str(temp_file_path), "r:gz") as tar:
                tar.extractall(path=temp_dir_path)

        if mime_type in ["application/zip"]:
            with zipfile.ZipFile(str(temp_file_path), "r") as zip_ref:
                zip_ref.extractall(temp_dir_path)

        # Delete temp file
        temp_file_path.unlink()

        # Move up one more leve
        return next(temp_dir_path.iterdir())
