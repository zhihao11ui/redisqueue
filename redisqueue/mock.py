# -*- coding: utf-8 -*-
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'Jeff Kehler'

from . import RedisQueue, QueueNotConnectedError, TaskAlreadyInQueueException


class MockRedisQueue(RedisQueue):

    def __init__(self, queue_name, task_class, namespace="mock_queue"):
        super(MockRedisQueue, self).__init__(queue_name, task_class, namespace)
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
                raise TaskAlreadyInQueueException(
                    'Task already in Queue [{hash}]'.format(
                        hash=task.unique_hash()))

        self._items.append(task.to_json())

        return True

    def get(self, block=True, timeout=None):
        if not self.connected:
            raise QueueNotConnectedError("Queue is not Connected")

        if self.qsize() == 0:
            return None

        task = self.task_class(self._items.pop())

        if task.unique:
            self._item_lock.remove(task.unique_hash())

        return task
