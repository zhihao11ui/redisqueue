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
do_live_testing = False
live_host = 'localhost'
live_port = 6379
live_pass = None

from redisqueue import AbstractTask, QueueNotConnectedError, TaskAlreadyInQueueException, RedisQueue
from redisqueue.mock import MockRedisQueue
import pytest
import hashlib


mock_queue = MockRedisQueue()


class MockTask(AbstractTask):

    def __init__(self, mock_data, unique=False):
        super().__init__(unique)
        self.mock_data = mock_data

    def unique_hash(self):
        return hashlib.sha1(self.mock_data.encode('utf-8')).hexdigest()


def test_mock_queue_connection():
    assert mock_queue.connected is False

    with pytest.raises(QueueNotConnectedError):
        mock_queue.put(MockTask("nothing"))

    with pytest.raises(QueueNotConnectedError):
        mock_queue.get()

    with pytest.raises(QueueNotConnectedError):
        mock_queue.qsize()

    mock_queue.connect()
    assert mock_queue.connected is True


def test_mock_queue_put_get():
    assert mock_queue.qsize() == 0

    task = MockTask("mock_queue_payload")
    mock_queue.put(task)
    assert mock_queue.qsize() == 1

    returned_task = mock_queue.get()
    assert isinstance(returned_task, MockTask) is True
    assert returned_task.uid == task.uid
    assert returned_task.unique_hash() == task.unique_hash()
    assert mock_queue.qsize() == 0


def test_mock_queue_unique():
    assert mock_queue.qsize() == 0

    task = MockTask("thisIsUnique")
    task.unique = True
    task2 = MockTask("thisIsUnique")
    task2.unique = True

    assert task.unique_hash() == task2.unique_hash()

    mock_queue.put(task)
    with pytest.raises(TaskAlreadyInQueueException):
        mock_queue.put(task2)

    task3 = MockTask("thisIsNotUnique")
    task3.unique = True
    mock_queue.put(task3)
    assert mock_queue.qsize() == 2

@pytest.mark.skipif(do_live_testing is False, reason='Live Redis testing not enabled.')
def test_live_queue():
    live_queue = RedisQueue("test_queue", namespace="pytest")
    assert live_queue.connected is False

    task = MockTask("thisIsUnique")
    task2 = MockTask("thisIsUnique")

    assert live_queue.connect(host=live_host, port=live_port, password=live_pass) is True
    assert live_queue.connected is True

    live_queue.clear()
    assert live_queue.qsize == 0

    live_queue.put(task)
    assert live_queue.qsize == 1

    live_queue.put(task2)
    assert live_queue.qsize == 2

    new_task = live_queue.get()
    assert isinstance(new_task, MockTask)
    assert new_task.uid == task.uid

    live_queue.clear()

    task.unique = True
    task2.unique = True

    assert task.unique_hash() == task2.unique_hash()

    live_queue.put(task)

    with pytest.raises(TaskAlreadyInQueueException):
        live_queue.put(task2)

    assert live_queue.qsize == 1

    live_queue.clear()