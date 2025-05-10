from driver_score.db.engine import session_scope
from driver_score.db.models import Driver, Run

from ..run.schemas import RunSchema


class DriverService:
    def __init__(self, driver_id: int) -> None:
        self.driver_id = driver_id

    async def persist_driver_to_db(self) -> None:
        """
        Persist a driver to the database.

        Args:
            driver_id (int): The ID of the driver to be persisted.

        Returns:
            None: This function does not return anything.

        This function creates a new `Driver` object with the given `driver_id` and adds it to the database session.

        Example:
            >>> driver_service = DriverService(12345)
            >>> await driver_service.persist_driver_to_db()
        """
        with session_scope() as session:
            driver = Driver(driver_id=self.driver_id)
            session.add(driver)

    async def get_current_driver(self) -> Driver | None:
        """
        Asynchronously retrieves a driver object from the database by its ID.

        :param driver_id: The ID of the driver to retrieve.
        :type driver_id: int
        :return: A Driver object if found, None otherwise.
        :rtype: Driver | None

        Example:
            >>> driver_service = DriverService(12345)
            >>> driver = await driver_service.get_current_driver()
            >>> print(driver.name)
            John Doe
        """
        with session_scope() as session:
            driver = session.query(Driver).filter(Driver.driver_id == self.driver_id).first()
            return driver

    async def get_runs(self) -> list[RunSchema]:
        with session_scope() as session:
            filters = [Run.driver_id == self.driver_id]
            runs = session.query(Run).filter(*filters).all()

            runs = [RunSchema.model_validate(run) for run in runs]
            return runs
