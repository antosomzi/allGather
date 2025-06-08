from sqlalchemy import join, select

from driver_score.core.database import get_db_session
from driver_score.core.models import Driver, RoadCharacteristic, Run, Score

from .schema import PivotTableByRCRangeSchema, PivotTableByRCTypeSchema


class SummaryService:
    def __init__(self) -> None:
        pass

    async def get_summary_by_RC_range(self) -> list[PivotTableByRCRangeSchema]:
        with get_db_session() as session:
            result = session.execute(
                select(
                    Driver.name,
                    Run.run_id,
                    Score.score,
                    Score.timestamp,
                    (1 / RoadCharacteristic.curvature).label("radius"),
                ).select_from(
                    join(Driver, Run, Driver.driver_id == Run.driver_id)
                    .join(Score, Run.run_id == Score.run_id)
                    .join(
                        RoadCharacteristic,
                        (Run.run_id == RoadCharacteristic.run_id) & (Score.timestamp == RoadCharacteristic.timestamp),
                    )
                )
            ).all()

            summaries = []

            def get_RC_range_from_radius(radius: float):
                if radius < 100:
                    return "<100ft"
                elif radius < 200:
                    return "100-200ft"
                elif radius < 400:
                    return "200-400ft"
                elif radius < 800:
                    return "400-800ft"
                elif radius < 1600:
                    return "800-1600ft"
                elif radius < 3200:
                    return "1600-3200ft"
                else:
                    return ">3200ft"

            for name, run_id, score, timestamp, radius in result:
                if name is None:
                    continue

                summary = PivotTableByRCRangeSchema(
                    driver_name=name,
                    run_id=run_id,
                    RC_range=get_RC_range_from_radius(radius),
                    # TODO: Remove later and put it in model service
                    score=max(0, min(100, int(score))),
                )
                summaries.append(summary)

            return summaries

    async def get_summary_by_RC_type(self) -> list[PivotTableByRCTypeSchema]:
        pass
