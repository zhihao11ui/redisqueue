__author__ = 'Jeff Kehler'

import uuid
import json

class Job:

    def __init__(self, db):
        self.__db = db
        self.__result = None
        self.uid = uuid.uuid4().urn

    @property
    def result(self):
        if self.__result:
            return self.__result
        result = self.__db.rpop(self.uid)
        if result:
            self.__db.delete(self.uid)
            self.__result = json.loads(result)
            return self.__result
        else:
            return None

    def wait(self, wait_time=0):
        if self.__result:
            return True
