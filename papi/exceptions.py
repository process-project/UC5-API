"""Module with custom exceptions used in the API"""

class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self):
        #pylint: disable=useless-super-delegation
        super().__init__()

class TaskIdNanError(Error):
    """Exception raised for task_ids which are no numbers

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        #pylint: disable=super-init-not-called
        self.expression = expression
        self.message = message

class InvalidTaskIdError(Error):
    """Exception raised for task_ids is invalid

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        #pylint: disable=super-init-not-called
        self.message = message


class MissingInputParameterError(Error):
    """Exception raised for missing input paramter in json

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        #pylint: disable=super-init-not-called
        self.message = message

class InputParameterMalformedError(Error):
    """Exception raised for invalid input parameter type

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        #pylint: disable=super-init-not-called
        self.message = message

class MissingPayloadError(Error):
    """Exception raised for missing json payload in request

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        #pylint: disable=super-init-not-called
        self.message = message

class NonExistingTaskEntryError(Error):
    """Exception raised for missing task entry in database

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        #pylint: disable=super-init-not-called
        self.message = message


class TaskAlreadyExistsError(Error):
    """Exception raised for task already submitted and stored in database

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        #pylint: disable=super-init-not-called
        self.message = message
