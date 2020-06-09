"""This module only contrains the handler class for status requests"""
import logging
from typing import Mapping
from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from papi.exceptions import InvalidTaskIdError
from papi.db import DB
from papi.ssh import Ssh

class Status(Resource):
    """Class to handle status GET request send to paramiko"""

    def __init__(self, database: DB, ssh: Ssh, config: Mapping):
        """Constructor for API ressource rooted at /status/<id>

            Parameters:
                database (DB): Database Object used for communication with sqlite3 db
                ssh (Ssh): SSH Object used for communication with ssh endpoint
        """
        self.logger = logging.getLogger('papi.handler.Submit')
        self.database = database
        self.ssh = ssh
        self.config = config

    def __do(self, task_id: int):
        status_message = {'message': ''}
        status = ''
        if task_id <= 0:
            raise InvalidTaskIdError(f'Invalid task id: {task_id}')

        try:
            db_entry = self.database.get_task(task_id)
        except Exception as exception:
            self.logger.error(exception)
            raise exception

        task_id = db_entry.id
        status = db_entry.state

        if status in ['queued']:
            pass
        elif status in ['running', 'executed', 'archiving', 'aggregating']:
            status = 'running'
        elif status == 'failed':
            slurm_jobs = self.database.get_slurm_jobs(task_id=task_id)
            status_message['message'] = f"Slurm job(s) {slurm_jobs} failed"
        elif status == 'finished':
            status_message = {"message": str(status_message),
                              "result_path":
                                  "/dss/dssfs01/pn56go/pn56go-dss-0000/process/UC5/results/test",
                              "result_webdav":
                                  "http://lobcder.process-project.eu:32432/lrzcluster/results/test"
                             }

        else:
            status_message['message'] = f"Unknown Task state '{status}'"
            self.logger.error(status_message)
            status = 'failed'
        return status, status_message

    #@jwt_required
    def get(self, task_id: int):
        """Executed on HTTP GET send to API Endpoint /status/<id>

            Parameters:
                task_id (int): Remote task id.
                               Corresponding internal task id is in sqlite3db.

            Returns:
                json(str): JSON string with Success or Error response returned in HTTP Response
        """

        status_message = ''
        try:
            status, status_message = self.__do(task_id)
        except Exception as exception: #pylint: disable=broad-except
            status = 'error'
            status_message = str(exception)
            self.logger.error(status_message)

        json = jsonify({'status': status,
                        'message': status_message})
        return json
