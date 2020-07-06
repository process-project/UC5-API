"""This module contains classes for an asynchronous thread
    The thread periodically checks the database for unfinished tasks
    If an unfinished task is encountered the slurm frontend of the cluster
    is checked for the jobs state.

    Unfinished tasks are defined as tasks which have executed
    a slurm job which is not finished yet
"""
from .runner import AsyncRunner
