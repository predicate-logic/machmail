# -*- coding: utf-8 -*-

"""Prevent multiple copies of the script from running.
"""
import fcntl
import sys
import os
import tempfile
import logging
from data_receipt_log_extract.util.log import setup_logging

setup_logging()
log = logging.getLogger('default')


def create_mutex_file():
    """Create file that only allows one copy of the script to run.
    """
    # create lock file
    pid_file = os.path.normpath(tempfile.gettempdir() + '/' +
                                os.path.splitext(
                                    os.path.abspath(__file__))[0].
                                replace("/", "-").replace(":", "").
                                replace("\\", "-") + '.lock')

    fp = open(pid_file, 'w')

    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        log.info("Created mutex file: {}".format(pid_file))

    except IOError:
        log.error("Multiple copies of script are not allowed to run "
                  "without the --force_run flag.")
        sys.exit(-1)
