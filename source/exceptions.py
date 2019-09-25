from datetime import datetime

#Used for incorrect values
class CustomException(Exception):
    def __init__(self, msg1): 
        super().__init__(msg1)
        self._msg1 = msg1           #Msg1 is for staff
        self._msg2 = str()          #Msg2 is for user

    def log(self, errType=""):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        print(f'{errType}: {dt_string}: {self._msg1}')
        return self._msg2

class builtInException(CustomException):
    def __init__(self, exc):
        super().__init__(str(exc))
        self._msg2 = "The system has encountered an unrecoverable error in an internal function. Please contact support if the issue persists."

class systemException(CustomException):
    def __init__(self, msg1="A built-in exception was encountered"):
        super().__init__(msg1)
        self._msg2 = "The system has encountered an unrecoverable error in an internal function. Please contact support if the issue persists."

class mixedException(CustomException):
    def __init__(self, msg1, msg2):
        super().__init__(msg1)
        self._msg2 = msg2