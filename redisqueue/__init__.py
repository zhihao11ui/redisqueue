# -*- coding: utf-8 -*-
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Jeff Kehler'
__license__ = 'MIT'
__status__ = 'Development'
__version__ = '0.1.1'

import redis
import logging
import uuid
import pickle


class RedisQueue:

    def __init__(self, queue_name, namespace='redisqueue'):
        """
        Create a Redis Queue

        :param queue_name: Name of the queue
        :param namespace: Unique namespace for the queue
        """

        self.__db = None
        self.connected = False
        self.name = queue_name
        self.namespace = namespace
        self.logger = logging.getLogger(self.__class__.__qualname__)
        self._key = '%s:%s' % (namespace, queue_name)
        self._lock_key = '%s:%s:lock' % (namespace, queue_name)

        self.logger.debug("Initializing Queue [key:{key}, lock_key:{lock_key}]".format(
            key=self._key, lock_key=self._lock_key))

    def connect(self, **kwargs):
        """
        Connect to the Redis Server

        :param kwargs: Parameters passed directly to redis library
        :return: Boolean indicating if connection successful

        :kwarg host: Hostname of the Redis server
        :kwarg port: Port of the Redis server
        :kwarg password: Auth key for the Redis server
        """

        self.__db = redis.Redis(**kwargs)
        try:
            info = self.__db.info()
            self.connected = True
        except redis.ConnectionError as e:
            self.logger.error("Failed to connect to Redis server: ", e)
            raise QueueNotConnectedError(e)

        return True

    def clear(self):
        """
        Clear all Tasks in the queue.
        """

        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        self.__db.delete(self._key)
        self.__db.delete(self._lock_key)

    @property
    def qsize(self):
        """
        Returns the number of items currently in the queue

        :return: Integer containing size of the queue
        :exception: ConnectionError if queue is not connected
        """
        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        try:
            size = self.__db.llen(self._key)
        except redis.ConnectionError as e:
            raise ConnectionError(repr(e))

        return size

    def put(self, task):
        """
        Inserts a Task into the queue

        :param task: :class:`~redisqueue.AbstractTask` instance
        :return: Boolean insert success state
        :exception: ConnectionError if queue is not connected
        """

        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        if task.unique:
            # first lets check if we have this hash already in our queue
            if not self.__db.sismember(self._lock_key, task.unique_hash()):
                self.__db.sadd(self._lock_key, task.unique_hash())
            else:
                raise TaskAlreadyInQueueException('Task already in Queue [{hash}]'.format(hash=task.unique_hash()))

        self.__db.lpush(self._key, pickle.dumps(task))

        return True

    def get(self, block=True, timeout=None):
        """
        Get a Task from the queue

        :param block: Block application until a Task is received
        :param timeout: Timeout after n seconds
        :return: :class:`~redisqueue.AbstractTask` instance
        :exception: ConnectionError if queue is not connected
        """

        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        if block:
            payload = self.__db.brpop(self._key, timeout=timeout)
        else:
            payload = self.__db.rpop(self._key)

        if not payload:
            return None

        task = pickle.loads(payload[1])

        # if task was marked as unique then lets remove the unique_hash from lock table
        if task.unique:
            self.__db.srem(self._lock_key, task.unique_hash())

        return task


class AbstractTask(object):
    def __init__(self, unique):
        """
        Abstract Task object to insert into Queue.

        This class should be subclassed to implement whatever features your Task needs

        :param unique: Boolean if Task should be unique
        """

        self.uid = uuid.uuid4().urn
        self.unique = unique

    @property
    def unique_hash(self):
        """
        Computes a hash for unique tasks. This method needs to be implemented

        :return: Computed Hash
        """

        raise NotImplementedError("unique_hash Method not implemented")


class QueueNotConnectedError(Exception):
    pass


class TaskAlreadyInQueueException(Exception):
    pass