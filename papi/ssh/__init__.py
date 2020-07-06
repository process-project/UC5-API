"""This module models a common API for ssh access to the lrz cluster.

    Classes:
        ssh: Used for standard blocking ssh connections
        sshRunner: Asynchronous fifo based non-blocking ssh connections
                   It is used for long running ssh connections, which are checked periodically
"""
from .ssh import Ssh
