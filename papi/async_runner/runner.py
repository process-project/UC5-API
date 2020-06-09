"""This module contains classes for an asynchronous thread
    The thread periodically checks the database for unfinished tasks
    If an unfinished task is encountered the slurm frontend of the cluster
    is checked for the jobs state.

    Unfinished tasks are defined as tasks which have executed
    a slurm job which is not finished yet
"""
from threading import Thread
import time
import socket
import logging
from typing import Mapping, Dict, Any
from papi.util import parse_sacct_output, parse_slurm_output
from papi.ssh import Ssh
from papi.db import SlurmJob, DB

def joblist_to_dict(joblist: list):
    """Converts a list of jobs to a dict"""
    parsed_list: Dict[str, Any] = {}
    for job in joblist:
        cluster_name = job.SlurmJob.cluster
        if cluster_name not in parsed_list:
            parsed_list[cluster_name] = {}
        parsed_list[cluster_name][str(job.SlurmJob.job_id)] = job
    return parsed_list

class AsyncRunner:
    """The main class for the asynchronous thread."""
    def __init__(self, ssh: Ssh, database: DB, sleep_timer: int):
        self.ssh = ssh
        self.database = database
        self.sleep_timer = sleep_timer
        self.logger = logging.getLogger('papi.async_runner')
        self.thread = Thread(target=self.main_loop)

    def __check_tasklist(self, joblist: Mapping, next_state: str):
        for cluster in joblist:
            csl = ','.join(list(joblist[cluster]))
            try:
                res = parse_sacct_output(self.ssh.check_task(csl, cluster, timeout=10))
            except socket.timeout:
                self.logger.error("Timeout in ssh.check_task")
                return
            for job in res:
                task = joblist[cluster][str(job)].Task
                state = str(res[job]['State'])
                task_id = task.id

                self.logger.info("Task '%s' has state '%s'", str(job), str(state))
                if state == 'COMPLETED':
                    self.database.set_task_state(task_id, next_state)
                    if next_state == 'executed':
                        self.ssh.collect_task(task, self.collect_callback)
                    elif next_state == 'archiving':
                        self.ssh.archive_task(task, self.archive_callback)
                elif state == 'FAILED':
                    self.database.set_task_state(task_id, 'failed')
                elif state in ['RUNNING', 'PENDING']:
                    pass
                else:
                    self.logger.error("Unknown State: '%s' for task '%s'", str(state), str(job))

    def __work(self):
        joblist = self.database.get_tasks_by_state('running', successful_only=True)
        self.__check_tasklist(joblist_to_dict(joblist), 'executed')

        joblist = self.database.get_tasks_by_state('aggregating', successful_only=True)
        self.__check_tasklist(joblist_to_dict(joblist), 'archiving')

        joblist = self.database.get_tasks_by_state('archived', successful_only=True)
        self.__check_tasklist(joblist_to_dict(joblist), 'finished')

    def collect_callback(self, return_value: int, stdout: str, stderr: str, task_id: int):
        """Callback as registered on the sshReader

            This callback is executed once the ssh command with the sbatch is executed

            Parameters:
                return_value: Return code of the sbatch command
                stdout: stdout of the sbatch command
                stderr: stderr of the sbatch command
                task_id: task id of the assoziated task
        """
        slurm_job_id = -1
        cluster = ''
        if return_value != 0:
            self.logger.error("Error wrapper script returned a"
                              "non zero exit code: %d output: '%s'",\
                              return_value, str(stderr))
        else:
            slurm_job_id, cluster = parse_slurm_output(stdout)
            self.logger.info("Task execution of task '%s' is finished. "
                             "Running on cluster '%s' with id '%d'",\
                             task_id, str(cluster), slurm_job_id)

        self.database.add_slurm_job(SlurmJob(job_id=slurm_job_id, cluster=cluster,\
                                    job_type='aggregation', ssh_rc=return_value,\
                                    ssh_stdout=stdout, ssh_stderr=stderr, task_id=task_id))
        self.database.set_task_state(task_id, 'aggregating')

    def archive_callback(self, return_value: int, stdout: str, stderr: str, task_id: int):
        """Callback as registered on the sshReader

            This callback is executed once the ssh command with the sbatch is executed

            Parameters:
                return_value: Return code of the sbatch command
                stdout: stdout of the sbatch command
                stderr: stderr of the sbatch command
                task_id: task id of the assoziated task
        """
        slurm_job_id = -1
        cluster = ''
        if return_value != 0:
            self.logger.error("Error wrapper script returned a"
                              "non zero exit code: %d output: '%s'",\
                              return_value, str(stderr))
        else:
            slurm_job_id, cluster = parse_slurm_output(stdout)
            self.logger.info("Task execution of task '%s' is finished. "
                             "Running on cluster '%s' with id '%d'",\
                             task_id, str(cluster), slurm_job_id)

        self.database.add_slurm_job(SlurmJob(job_id=slurm_job_id, cluster=cluster,\
                                    job_type='archive', ssh_rc=return_value,\
                                    ssh_stdout=stdout, ssh_stderr=stderr, task_id=task_id))
        self.database.set_task_state(task_id, 'archived')


    def main_loop(self):
        """Thread Waitloop"""
        while True:
            self.__work()
            time.sleep(self.sleep_timer)

    def run(self):
        """Starts the thread instance"""
        self.thread.start()
