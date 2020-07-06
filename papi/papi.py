"""This module models a papi (process-api) instance.

    It initialises the following objects:
        db: The Database handler
        ssh: The SSH handler
        runner: An asynchronous runner used to query slurm via ssh
                The runner checks the state of running slurm jobs and keeps the database in sync
"""

import logging
from werkzeug.datastructures import ImmutableDict
from flask import Flask
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from .db.viwa_db import ViwaDb
from .ssh import Ssh
from .async_runner import AsyncRunner

class Papi:
    """A single instance of the API

        Starts necessary parts of the module
    """
    def __init__(self, config: ImmutableDict):
        """Constructor for the API endpoint

            Parameters:
                port (str): Used portnumber for the HTTP server
                ssh_hostname (str): Hostname of the SSH endpoint where jobs are submitted
                ssh_username (str): Username of the SSH endpoint where jobs are submitted
                ssh_password (str): Password of the SSH endpoint where jobs are submitted
                debug (bool): Debug Flag makes output more verbose
                keyfile (str): Filename of the RSA key used for auth
                dbfile (str): Filename of the sq lite3 db used for storing job id associations
        """
        self.config = config['PAPI']
        self.database = ViwaDb(config['DB'])
        self.ssh = Ssh(config['SSH'], self.database)
        self.app = Flask(__name__)
        self.logger = logging.getLogger('papi.Papi')
        self.runner = AsyncRunner(self.ssh, self.database, self.config['SLEEP_TIMER'])
        self.app.debug = config['DEBUG']['ENABLED']
        self.__jwt()
        self.api = Api(self.app)
        self.runner.run()

    def __jwt(self):
        self.app.config['JWT_PUBLIC_KEY'] = self.open_pub_key(self.config['HTTP']['JWT_SECRET_KEY'])
        self.app.config['JWT_ALGORITHM'] = self.config['HTTP']['JWT_ALGORITHM']
        self.app.config['JWT_IDENTITY_CLAIM'] = self.config['HTTP']['JWT_CLAIM']
        return JWTManager(self.app)

    def open_pub_key(self, filename: str):
        """Try to open the RSA public key used to API Auth.
           Raises an exception or returns the pubkey"""
        content = ''
        try:
            with open(filename, "r") as file_handle:
                content = file_handle.read()
        except FileNotFoundError:
            self.logger.warning("Exception on opening public key file (file not found): '%s'",\
                                str(filename))
            raise
        except:
            self.logger.error("Unhandled Error on opening public key file: '%s'", str(filename))
            raise
        return content

    def add_resource(self, res: Resource, path: str):
        """Wrapper Function to add API Endpoint

            Parameters:
                res (Class(Ressource)): Ressource class which is
                                        inherits from Ressource class
                                        defined in flask_restful.
                path (str): API path which executes the defined res class

            Returns:
                None
        """
        self.api.add_resource(res, path, resource_class_args=(self.database, self.ssh, self.config))
