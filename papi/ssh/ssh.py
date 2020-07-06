"""This module models a common API for ssh access to the lrz cluster.

    Classes:
        ssh: Used for standard blocking ssh connections
        sshRunner: Asynchronous fifo based non-blocking ssh connections
                   It is used for long running ssh connections, which are checked periodically
"""
import logging
import os
from typing import Mapping
import paramiko
from papi.db import DB
from .ssh_reader import SshReader

class Ssh:
    """Main ssh Interface"""
    def __init__(self, config: Mapping, db: DB):
        self.config = config
        self.database = db
        self.logger = logging.getLogger('papi.Ssh')
        self.ssh_reader = SshReader()
        self.key_filename = self.config['KEY_FILENAME']
        if os.path.isfile(self.key_filename):
            self.__key_filename = self.key_filename

    def __get_ssh_client(self, timeout=None):
        """Returns a default paramiko ssh client"""
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.load_system_host_keys()
        ssh_client.connect(self.config['HOSTNAME'], self.config['PORT'], self.config['USERNAME'],\
                           self.config['PASSWORD'], key_filename=self.__key_filename,\
                           timeout=timeout)
        return ssh_client

    def __execute(self, command: str, callback, task_id=0) -> int:
        """ Executes an arbitrary command via ssh and returns the stdout output

            Parameters:
                command(str): Command to execute

            Returns:
                result: stdout of executed ssh remote cmd

        """
        self.logger.debug("Send async ssh cmd: '%s', callback: '%s'", str(command), str(callback))
        ssh_client = self.__get_ssh_client()
        self.ssh_reader.add_object(ssh_client, command, callback, task_id)
        return 0

    def __execute_blocking(self, command, timeout=None):
        """ Executes an arbitrary command via ssh and returns the stdout output

            Parameters:
                command(str): Command to execute

            Returns:
                result: stdout of executed ssh remote cmd
        """
        self.logger.debug("Send blocking ssh cmd: '%s'", str(command))
        ssh_client = self.__get_ssh_client(timeout=timeout)
        (_, stdout, _) = ssh_client.exec_command(command, timeout=timeout)
        result = stdout.read()
        ssh_client.close()
        return result.decode('utf-8')

    def submit_task(self, task_id: int, params: str, callback):
        """Executes command defined in config dictionary to submit a task and returns the output"""
        cmd = self.config['SUBMIT_COMMAND'] + " " + params
        return self.__execute(cmd, callback, task_id)

    def check_task(self, slurm_job_id, cluster_name, timeout=None):
        """Executes command defined in dictionary.
            Used to get the status of a task and returns the output
        """
        cmd = f"{self.config['CHECK_COMMAND']} {cluster_name} {slurm_job_id}"
        return self.__execute_blocking(cmd, timeout=timeout)

    def collect_task(self, task, callback) -> int:
        """Callback function after collect sbatch call is finished"""
        params = self.database.get_param_from_task(task)
        cmd = f"{self.config['COLLECT_COMMAND']} {params}"
        return self.__execute(cmd, callback, task.id)

    def archive_task(self, task, callback) -> int:
        """Callback function after archive sbatch call is finished"""
        params = self.database.get_param_from_task(task)
        cmd = f"{self.config['ARCHIVE_COMMAND']} {params}"
        return self.__execute(cmd, callback, task.id)
