import logging
import os
import tempfile
from datetime import datetime
from pathlib import Path

from dynaconf import LazySettings

settings = LazySettings(
    settings_files=["configs/settings.yaml"],
    envvar_prefix=False,
    environments=True,
    load_dotenv=True,
)

logging_level = os.environ["LOGGING_LEVEL"] if "LOGGING_LEVEL" in os.environ else logging.INFO

DRIVER_SCORE_LOG_DIR = Path(tempfile.gettempdir()) / "driver-score"
DRIVER_SCORE_LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = DRIVER_SCORE_LOG_DIR / f"{datetime.now().strftime(settings.LOG_FORMAT)}.log"

logging.basicConfig(
    level=logging_level,
    # format="%(asctime)s - %(name)s:%(lineno)d - [%(levelname)s] - %(message)s",
    format="%(name)s:%(lineno)d - %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, mode="w"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)
