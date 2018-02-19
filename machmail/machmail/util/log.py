"""
Setup logging.
"""

import os
import sys
import json
import logging
import logging.config

def setup_logging(config='default.json', level=logging.WARN,
                  env_key='LOG_CFG'):
    """Setup logging configuration.

    You can overide the logging definition JSON file used by
    setting the ``LOG_CFG`` environment variable.  For example:
    ``LOG_CFG=./log_config.json python foo.py``
    """

    # assuming default.json is in the current directory of the log.py
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config)

    # get env var in case it has been overridden
    value = os.getenv(env_key, None)

    # if env var override default path
    if value:
        path = value

    # parse logging config file
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)

    # warn if logging config isn't found
    else:
        print >> sys.stderr, ("Missing log_config.json.  Defaulting to "
                              "logging.basicConfig.")
        logging.basicConfig(level=level)
