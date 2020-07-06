"""This module only contrains the handler class for submit requests"""

import logging
from typing import Mapping
from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from papi.exceptions import (MissingInputParameterError, MissingPayloadError,
                             InputParameterMalformedError)
from papi.util import parse_slurm_output
from papi.db import SlurmJob, DB
from random import randrange
from papi.ssh import Ssh
class Submit(Resource):
    """Class to handle submit POST request send to paramiko"""

    def __init__(self, database: DB, ssh: Ssh, config: Mapping):
        """Constructor for API ressource rooted at /submit/<id>

            Parameters:
                database (DB): Database Object used for communication with sqlite3 db
                ssh (Ssh): SSH Object used for communication with ssh endpoint
        """
        self.config = config
        self.fields_required = self.config['SUBMIT_FIELDS_REQUIRED']
        self.logger = logging.getLogger('papi.handler.Submit')
        self.database = database
        self.ssh = ssh
        self.jwt_required = self.config['JWT_REQUIRED']

    def submit_task_finished(self, return_value: int, stdout: str, stderr: str, task_id: int):
        """Callback for sshRunner
            This Callback is executed after an slurm submit task is executed
            Its main purpose is to update the database with values returned by ssh

            Paramters:
                return_valse: exit code as reported by ssh (paramiko)
                stdout: stdout as reported by ssh
                stderr: stderr as reported by ssh
                task_id: task id of the assoziated task
        """
        slurm_job_id = -1
        cluster = ''
        if return_value != 0:
            self.logger.error("Error wrapper script returned "
                              "a non zero exit code: '%s' output: '%s'",\
                              str(return_value), str(stderr))
        else:
            slurm_job_id, cluster = parse_slurm_output(stdout)
            self.logger.info("Task execution of task '%s' is finished. "
                             "Running on cluster '%s' with id '%d'",\
                             str(task_id), str(cluster), slurm_job_id)
        self.database.add_slurm_job(SlurmJob(job_id=slurm_job_id, cluster=cluster,\
                                    job_type='main', ssh_rc=return_value,\
                                    ssh_stdout=stdout, ssh_stderr=stderr, task_id=task_id))
        self.database.set_task_state(task_id, 'running')

    def __do(self):
        payload = ''
        try:
            payload = request.json
        except Exception:
            raise MissingPayloadError("Missing JSON payload in HTTP request")

        for param in self.fields_required:
            if param not in payload:
                raise MissingInputParameterError((f"Missing required Parameter: "
                                                  f"{param} got: '{payload}'"))
            try:
                payload[param] = self.fields_required[param](payload[param])
            except Exception as exception:
                raise InputParameterMalformedError(f"Parameter {param}: '{exception}'")

        if 'debug' in payload:
            task = self.database.add_task(payload, debug=True)
        else:
            task = self.database.add_task(payload)

        try:
            self.logger.debug("JSON Payload: '%s'", str(payload))
            params = self.database.get_param_from_task(task)
            if 'debug' not in payload:
                self.ssh.submit_task(task.id, params, self.submit_task_finished)
        except Exception as exception:
            self.logger.error(exception)
            raise exception
        return task.id

    #@jwt_required
    def post(self):
        """Executed on HTTP POST send to API Endpoint /submit/

            Returns:
                json(str): JSON string with Success or Error response returned in HTTP Response
        """

        status_message = ''
        status = 'created'
        code = self.config['HTTP']['OK_RESP_CODE']
        try:
            status_message = self.__do()
        except Exception as exception: #pylint: disable=broad-except
            status = 'error'
            status_message = str(exception)
            code = self.config['HTTP']['CLIENT_ERR_RESP_CODE']

        json = jsonify({'status': status,
                        'message': status_message})
        json.status_code = code
        return json
