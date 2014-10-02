__author__ = 'Jeff Kehler'

from . import RedisQueue, QueueNotConnectedError, TaskAlreadyInQueueException
import pickle


class MockRedisQueue(RedisQueue):

    def __init__(self, queue_name="mock_queue", namespace="mock_queue"):
        super().__init__(queue_name, namespace)
        self._items = []
        self._item_lock = []

    def connect(self, **kwargs):
        self.connected = True

        return self.connected

    def clear(self):
        self._items = []
        self._item_lock = []

    def qsize(self):
        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        return len(self._items)

    def put(self, task):
        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        if task.unique is True:
            if task.unique_hash() not in self._item_lock:
                self._item_lock.append(task.unique_hash())
            else:
                raise TaskAlreadyInQueueException('Task already in Queue [{hash}]'.format(hash=task.unique_hash()))

        self._items.append(pickle.dumps(task))

        return True

    def get(self, block=True, timeout=None):
        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        if self.qsize() == 0:
            return None

        task = pickle.loads(self._items.pop())

        if task.unique:
            self._item_lock.remove(task.unique_hash())

        return task