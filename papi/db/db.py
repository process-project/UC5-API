"""Database interface class and table definition classes"""
import logging
from werkzeug.datastructures import ImmutableDict
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, Boolean
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import scoped_session
from papi.exceptions import NonExistingTaskEntryError
from .db_init import Base

class Task(Base):
    #pylint: disable=too-few-public-methods
    """Database table with tasks

    A tasks is a single submit request to the API
    """
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    state = Column(String, default='queued')
    debug = Column(Boolean, default=False)

    def __repr__(self):
        return "<Task(state='%s')>" % (self.state)

class SlurmJob(Base):
    #pylint: disable=too-few-public-methods
    """Database table with slurm jobs

        A slurm job should always be associated with a task
    """
    __tablename__ = 'slurm_jobs'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer)
    cluster = Column(String)
    job_type = Column(String)
    ssh_rc = Column(Integer)
    ssh_stdout = Column(String)
    ssh_stderr = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.id'))

    def __repr__(self):
        return (f"<SlurmJob(type='{self.job_type}', job_id='{self.job_id}',"
                f"cluster='{self.cluster}', rc='{self.ssh_rc}')>")

class DB:
    """Interface class for database related stuff"""

    def __init__(self, config: ImmutableDict):
        self.config = config
        self.logger = logging.getLogger('papi.db')
        self.db_file = self.config['BASE_DIR'] + self.config['FILENAME']
        self.logger.info(f'Opening db File {self.db_file}')
        self.session = self.__session()

    def __session(self):
        engine = create_engine(f'sqlite:////{self.db_file}', echo=False)
        Base.metadata.create_all(engine)
        session_factory = sessionmaker(bind=engine)
        return scoped_session(session_factory)

    def _add_and_commit(self, obj):
        session = self.session()
        session.add(obj)
        session.commit()
        session.refresh(obj)
        self.session.remove()
        return obj

    def get_task(self, task_id: int):
        """Get a single task by id

        Returns a task or raises an exception if no
        such tasks exists in the database
        """
        session = self.session()
        query = session.query(Task).filter_by(id=task_id)
        try:
            res = query.one()
            self.session.remove()
            return res
        except NoResultFound:
            self.session.remove()
            raise NonExistingTaskEntryError((f"error remote task id {str(task_id)}"
                                             f" does not exists in database"))

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
        """Default implementation of get_param_from_task"""
        #pylint: disable=no-self-use
        self.logger.warning("get_param_from_task for %s NYI", str(task))

    def add_task(self, payload, debug=False):
        """ Add task to database

            Parameters:
                payload: Payload send via JSON in HTTP request
        """
        task = Task(debug=debug)
        return self._add_and_commit(task)

    def set_task_state(self, task_id: int, state: str):
        """Set the state of a task

            This function persists a new state for a given task in the database

            Parameters:
                task_id: id of task to set
                state: String of the new state
        """
        session = self.session()
        task = session.query(Task).filter_by(id=task_id).one()
        task.state = state
        session.commit()
        self.session.remove()

    def get_slurm_jobs(self, task_id=None):
        """Returns a list of jobs for a given task

        Parameters:
            task_id: Limits slurm jobs to a given task
        """
        session = self.session()
        query = session.query(Task, SlurmJob).\
                filter(Task.id == SlurmJob.task_id)
        if task_id is not None:
            query = query.filter(Task.id == task_id)
        res = query.all()
        self.session.remove()
        return res

    def add_slurm_job(self, slurm_job: SlurmJob):
        """Adds a new slurm job to the databse

            Stores a new slurm job in the databse after this job was batched

            Parameters:
                task_id: Task id of the task relevant for the slurm job
                slurm_job: SlurmJob object of the slurm job as reported by sbatch
                cluster: Name of the execution cluster as reported by slurm
                job_type: Type of the job, can be either 'main' or 'aggregation'
                    Main jobs are jobs used for generation the simulation data
                    aggregation jobs are jobs used to aggregate the data into
                    a downloadable file
                ssh_rc: Return code of the ssh command
                ssh_stdout: stdout of the ssh command
                ssh_stderr: stderr of the ssh command
        """
        return self._add_and_commit(slurm_job)
