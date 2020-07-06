"""Asynchronous ssh reader

    This module is used to keep track of a fifo queue of non blocking ssh sessions
    each ssh session executes a command. When a command is finished executing
    the stdin, stderr and rc of the executed command is fetched and send to a registered callback
"""
import time
import threading
import select
import logging

class SshConnection:
    """A single ssh command

    SshConnections are stored in a pool and checked for execution
    """
    def __init__(self, task_id: int, ssh, stdin: str, stdout: str, stderr: str, callback):
        #pylint: disable=too-many-arguments
        self.task_id = task_id
        self.ssh = ssh
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.callback = callback
        self.logger = logging.getLogger('papi.ssh.SshConnection')

    def get_id(self):
        """Returns task id which is relevant to the given ssh connection"""
        return self.task_id

    def finalize(self):
        """Finalizer executed after the ssh command is terminated"""
        self.ssh.close()

class SshReader:
    """The asynchronous thread used for observation of a pool of SshConnection objects"""
    def __init__(self):
        self.queue = []
        self.logger = logging.getLogger('papi.ssh.SshReader')
        self.thread = threading.Thread(target=self.main_loop)
        self.thread.start()

    def __remove(self, ssh_connection):
        """Remove object from queue"""
        ssh_connection.finalize()
        self.queue.remove(ssh_connection)

    def add_object(self, ssh, command, callback, task_id):
        """Creates a new SshConnection object and add it to the queue"""
        (stdin, stdout, stderr) = ssh.exec_command(command)
        self.queue.append(SshConnection(task_id, ssh, stdin, stdout, stderr, callback))

    def __work(self):
        if len(self.queue) > 0:
            for i in self.queue:
                if i.stdout.channel.exit_status_ready():
                    exit_status = i.stdout.channel.recv_exit_status()
                    self.logger.info("SSH Reader got exit code: '%s'", str(exit_status))
                    stdout = ''
                    stderr = ''
                    if i.stdout.channel.recv_ready():
                        read_list, _, _ = select.select([i.stdout.channel], [], [], 0.0)
                        if len(read_list) > 0:
                            stdout = i.stdout.channel.recv(1024).decode('utf-8')
                    if i.stdout.channel.recv_stderr_ready():
                        read_list, _, _ = select.select([i.stdout.channel], [], [], 0.0)
                        if len(read_list) > 0:
                            stderr = i.stdout.channel.recv_stderr(1024).decode('utf-8')
                            self.logger.error(stderr)
                    i.callback(exit_status, stdout, stderr, i.task_id)
                    self.__remove(i)

    def main_loop(self):
        """Loops over the queue and checks for terminated ssh commands

            When a ssh command is terminated the stdout, stderr and rc is fetched.
            Afterwards the registered callback is executed
        """
        self.logger.info("start ssh read thread")
        while True:
            self.__work()
            time.sleep(1)
