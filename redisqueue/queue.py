__author__ = 'Jeff Kehler'

import json
import redis
from .job import Job
from .task import Task

class Queue:

    def __init__(self, queue_name, namespace='queue'):

        self.__db = None
        self._connected = False
        self._key = '%s:%s' % (namespace, queue_name)
        self._lock_key = '%s:%s:lock'

    def connect(self, **kwargs):
        self.__db = redis.Redis(**kwargs)
        try:
            info = self.__db.info()
            self._connected = True
        except redis.ConnectionError:
            print('Failed to connect to Redis server.')
            return False

        return True

    @property
    def qsize(self):
        if not self._connected:
            raise ConnectionError("Queue is not Connected")

        try:
            size = self.__db.llen(self._key)
        except redis.ConnectionError as e:
            raise ConnectionError(repr(e))

        return size

    def put(self, task):
        if not self._connected:
            raise ConnectionError("Queue is not Connected")

        try:
            job = Job(self.__db)
            task.uid = job.uid
            if task.unique:
                # first lets check if we have this hash already in our queue
                if not self.__db.sismember(self._lock_key, task.hash):
                    self.__db.sadd(self._lock_key, task.hash)
                else:
                    raise Exception('Task already in Queue')

            self.__db.lpush(self._key, task.json)

        except Exception as e:
            return False

        return job

    def get(self, block=True, timeout=None):
        if not self._connected:
            raise ConnectionError("Queue is not Connected")

        if block:
            payload = self.__db.brpop(self._key, timeout=timeout)
        else:
            payload = self.__db.rpop(self._key)

        if not payload:
            return None

        task = Task(json.loads(payload[1].decode('utf-8')))

        # check if we have a lock for this task and remove it as well
        self.__db.srem(self._lock_key, task.hash)

        return task

    def send(self, task, result, expire=60):
        """
        Sends the result back to the producer. This should be called if only you
        want to return the result in async manner.

        :arg task: ::class:`~redis-queue.task.Task` object
        :arg result: Result data to be send back. Requires a Dict object.
        :arg expire: Time in seconds after the key expires. Default is 60 seconds.

        """

        if isinstance(result, dict):
            self.__db.lpush(task.uid, json.dumps(result))
            self.__db.expire(task.uid, expire)
            return True

        return False
