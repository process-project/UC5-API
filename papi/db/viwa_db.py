"""Viwa use case specific db implementation"""
import re
from sqlalchemy import Column, Integer, String, Boolean, Float
from .db import DB, SlurmJob
from .db_init import Base

def normalize_seeding_date(seeding_date):
    """normalizes a seeding date to get rid of '-' and '+' chars in the input"""
    seeding_date = seeding_date.lstrip()
    if seeding_date[0] == '-':
        regex = re.search(r"^-([\d]+) days", seeding_date)
        if regex is not None:
            s_date = f"sub{regex.group(1)}days"
            return s_date
    elif seeding_date[0] == '+':
        regex = re.search(r"^+([\d]+) days", seeding_date)
        if regex is not None:
            s_date = f"add{regex.group(1)}days"
            return s_date
    return seeding_date

class Task(Base):
    #pylint: disable=too-few-public-methods
    """Database table with tasks

    A tasks is a single submit request to the API
    """
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    seeding_date = Column(String, nullable=False)
    irrigation = Column(Boolean, nullable=False)
    nutrition_factor = Column(Float, nullable=False)
    phenology_factor = Column(Float, nullable=False)
    state = Column(String, default='queued')

    def __repr__(self):
        return "<Task(state='%s')>" % (self.state)

class ViwaDb(DB):
    """Viwa use case specific db implementation"""
    def __init__(self, config):
        DB.__init__(self, config)

    def add_task(self, payload, debug=False):
        #pylint: disable=arguments-differ
        """ Add task to database

            Parameters:
                payload: Payload send via JSON in HTTP request
        """
        if debug:
            task = Task(seeding_date=normalize_seeding_date(payload['seeding_date']),
                    irrigation=payload['irrigation'],
                    nutrition_factor=payload['nutrition_factor'],
                    phenology_factor=payload['phenology_factor'],
                    debug=debug,
                    state='finished')
        else:
            task = Task(seeding_date=normalize_seeding_date(payload['seeding_date']),
                    irrigation=payload['irrigation'],
                    nutrition_factor=payload['nutrition_factor'],
                    phenology_factor=payload['phenology_factor'],
                    debug=debug)

        return self._add_and_commit(task)

    def get_tasks_by_state(self, state: str, successful_only=False):
        """Returns a list of task in a given state

            Parameters:
            state: limit query to a state.
            successful_only: Only query jobs which where successfully scheduled
        """
        session = self.session()
        query = session.query(Task, SlurmJob).\
                filter(Task.id == SlurmJob.task_id).\
                filter(Task.state == state)
        if successful_only:
            query = query.filter(SlurmJob.job_id != -1)
        res = query.all()
        self.session.remove()
        return res

    def get_param_from_task(self, task):
        """Converts a string or dict of params to ssh params"""
        params = str(task.phenology_factor)
        params += " "
        params += str(task.nutrition_factor)
        params += " "
        if task.irrigation:
            params += "1"
        else:
            params += "0"
        params += " "
        params += str(task.seeding_date)
        params += " "
        params += str(task.id)
        return params
