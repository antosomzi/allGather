import logging.config

import yaml

with open("configs/log_conf.yaml") as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
