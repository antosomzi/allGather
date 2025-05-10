import numpy as np

from driver_score.db.engine import session_scope
from driver_score.db.models import Score

from ..allgather.schemas import GpsSampleSchema, ImuSampleSchema
from .schemas import DriverScoreInSchema


class DriverScoreModelService:
    def __init__(self, window_length: int = 10):
        self.window_length = window_length

    def calculate_scores(
        self, gps_samples: list[GpsSampleSchema], imu_samples: list[ImuSampleSchema]
    ) -> list[DriverScoreInSchema]:
        """
        get the run data from db

        get the RC data from db

        resample and perpare data (get IMU and GPS and RC in the same frquency)

        loop over all GPS points, and invoke calculate_score
        becase calculate_score may require multiple data points (n data point)
        each loop will provide the n data points to the function
        """

        n_samples = len(gps_samples)
        scores: list[DriverScoreInSchema | None] = [None] * n_samples

        for i in range(self.window_length, n_samples):
            # get input_data using a rolling window.
            velocities_in_window = [gps_sample.velocity for gps_sample in gps_samples[i - 10 : i]]
            acc_in_window = [
                (imu_sample.acceleration_x_ms2, imu_sample.acceleration_y_ms2, imu_sample.acceleration_z_ms2)
                for imu_sample in imu_samples[i - 10 : i]
            ]
            score = DriverScoreModelService._calculate_score(vel=velocities_in_window, acc=acc_in_window)
            scores[i] = DriverScoreInSchema(timestamp=gps_samples[i].timestamp, score=score)

        # ? Backfill the first window_len scores
        nearest_score = scores[self.window_length].score
        for i in range(self.window_length):
            timestamp = gps_samples[i].timestamp
            scores[i] = DriverScoreInSchema(timestamp=timestamp, score=nearest_score)

        return scores

    @staticmethod
    def _calculate_score(acc: list, vel: list, gyro: list = None, RC: list = None, VC=0.0, dt=1) -> float:
        """
        Author: Vicky
        Calculates the driver score based on accelerometer, gyroscope, velocity, and other parameters.

        Parameters:
        - acc (list): n x 3 IMU's acceleration list (calibrated, filted, and down sample)
        - gyro (list): n x 3 IMU's angular velocity list (calibrated, filted, and down sample)
        - Vel (list): n x 1 GPS's Velocity list
        - RC (list): n x 4 Roadway characteristic list [Curvature, Speed Limit, Superelevation, Slope]
        - n (int): length of the input data (range 10 to m).
        - VC (float): Vehicle Suspension coefficient (roll rate) (defult as 0.0)
        - dt (int, optional): sampeling duration (default as 1 seconds).

        Returns:
        Score: The calculated driver score.
        Score_T: The calculated driver score on the tangent direction.
        Score_R: The calculated driver score on the radial direction.

        Score Definition (Thresthold may change after more testing)
        Score < 0.8 :  Safe, (may be can consider 0.7-0.8 as riskey score)
        0.8 < Score < 1 : Dangerous, may lock up front wheels.
        1 < Score < 1.5 : Normal car can't reach this score. (Still possible if driving good passenger car in good whether conditions.)
        Score > 1.5 : There may be some coefficient error (You Will see score > 1.5 now because the coefficient hadn't be fixed righr now.)
        """
        # Acc limited, asssume on the horizontal plane
        V = vel[0] * 2.2369  # to mph
        if np.isnan(V):
            return np.nan

        Fd_x = 4 * (10**-5) * V * V - 0.0064 * V + 0.6701  # X direction skidding Friction
        Fs_m_x = 1 * (10**-5) * V * V - 0.0019 * V + 0.7507  # X direction maximum Friction (-2StDev)
        Fs_M_x = -2 * (10**-6) * V * V - 0.0018 * V + 1.1391  # X direction maximum Friction (+2StDev)
        Fd_y = 6 * (10**-6) * V * V - 0.0025 * V + 0.6449  # Y direction skidding Friction
        Fs_m_y = -1 * (10**-6) * V * V - 0.0009 * V + 0.614  # Y direction maximum Friction (-2StDev)
        Fs_M_y = 2 * (10**-5) * V * V - 0.0039 * V + 0.9676  # Y direction maximum Friction (+2StDev)

        # No RC Input
        ax = np.abs(acc[0][0] / acc[0][2])
        ay = np.abs(acc[0][1] / acc[0][2])
        Score_d = np.sqrt((ax / Fd_x) ** 2 + (ay / Fd_y) ** 2)
        Score_m = np.sqrt((ax / Fs_m_x) ** 2 + (ay / Fs_m_y) ** 2)
        Score_M = np.sqrt((ax / Fs_M_x) ** 2 + (ay / Fs_M_y) ** 2)
        if Score_d < 1:
            Score = 100 - 50 * Score_d
        elif Score_m < 1:
            Score = 50 - 25 * (Score_d - 1) / (Score_d / Score_m - 1)
        elif Score_M < 1:
            Score = 25 - 25 * (Score_m - 1) / (Score_m / Score_M - 1)
        else:
            Score = (Score_M - 1) * 100

        return Score

    async def persist_scores_into_db(self, run_id: str, scores: list[DriverScoreInSchema]) -> None:
        with session_scope() as session:
            for score in scores:
                score = Score(run_id=run_id, timestamp=score.timestamp, score=score.score)
                session.add(score)
