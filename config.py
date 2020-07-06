# -*- coding: utf-8 -*-
"""Central configuration file

This module holds an immutable dict with a basic configuration

Attributes:
    CONFIG (ImmutableDict): A dict with the config parameters
        Consists of sub-dicts with a config corresponding
        to the appropriate module. E. g. CONFIG['SSH'] is
        used for ssh module configuration.

"""
import logging
from distutils import util

CONFIG = {
    'DEBUG': {
        'ENABLED':  True,
        'LEVEL':    logging.INFO,
    },
    'SSH': {
        'HOSTNAME':         '',
        'PORT':             22,
        'USERNAME':         '',
        'PASSWORD':         None,
        'KEY_FILENAME':     'keys/id_ecdsa',
        'STATUS_COMMAND':   "status",
        'CHECK_COMMAND':    "check",
        'SUBMIT_COMMAND':   "submit",
        'COLLECT_COMMAND':  "collect",
        'ARCHIVE_COMMAND':  "archive",
    },
    'DB': {
        'TYPE':     'sqlite3',
        'FILENAME': 'db/db.sqlite3',
    },
    'PAPI': {
        'BASE_DIR': '',
        'JWT_REQUIRED': True,
        'SLEEP_TIMER': 10,
        'HTTP': {
            'HOSTNAME':             '0.0.0.0',
            'PORT':                 5000,
            'OK_RESP_CODE':         200,
            'CLIENT_ERR_RESP_CODE': 400,
            'JWT_ALGORITHM':        'ES256',
            'JWT_SECRET_KEY':       'keys/public.pem',
            'JWT_AUTH_PREFIX':      'Bearer',
            'JWT_CLAIM':            'jti',
        },
        'SUBMIT_FIELDS_REQUIRED': {'irrigation': util.strtobool,
                                   'seeding_date': str,
                                   'nutrition_factor': float,
                                   'phenology_factor':float
                                  },
    },
}
logging.basicConfig(filename='/var/log/papi/papi.log', level=CONFIG['DEBUG']['LEVEL'], format="%(asctime)s - %(name)s - %(levelname)s - %(threadName)s:%(message)s")

