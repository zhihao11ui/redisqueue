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
do_live_testing = True
live_host = 'localhost'
live_port = 6379
live_pass = None

from redisqueue import AbstractTask, QueueNotConnectedError
from redisqueue import TaskAlreadyInQueueException, RedisQueue
from redisqueue.mock import MockRedisQueue
import pytest
import hashlib


class MockTask(AbstractTask):

    def __init__(self, mock_data=None, unique=False):
        super(MockTask, self).__init__(mock_data, unique)

    def unique_hash(self):
        return hashlib.sha1(self.uri.encode('utf-8')).hexdigest()


mock_queue = MockRedisQueue('mock_queue', MockTask)


def test_mock_queue_connection():
    assert mock_queue.connected is False

    with pytest.raises(QueueNotConnectedError):
        mock_queue.put(MockTask())

    with pytest.raises(QueueNotConnectedError):
        mock_queue.get()

    with pytest.raises(QueueNotConnectedError):
        mock_queue.qsize()

    mock_queue.connect()
    assert mock_queue.connected is True


def test_mock_queue_put_get():
    assert mock_queue.qsize() == 0

    task = MockTask()
    task.uri = "my_uri"
    mock_queue.put(task)
    assert mock_queue.qsize() == 1

    returned_task = mock_queue.get()
    assert isinstance(returned_task, MockTask) is True
    assert returned_task.uid == task.uid
    assert returned_task.unique_hash() == task.unique_hash()
    assert returned_task.uri == "my_uri"
    assert mock_queue.qsize() == 0


def test_mock_queue_unique():
    assert mock_queue.qsize() == 0

    task = MockTask()
    task.unique = True
    task.uri = 'unique1'
    task2 = MockTask()
    task2.unique = True
    task2.uri = 'unique1'

    assert task.unique_hash() == task2.unique_hash()

    mock_queue.put(task)
    with pytest.raises(TaskAlreadyInQueueException):
        mock_queue.put(task2)

    task3 = MockTask()
    task3.unique = True
    task3.uri = 'unique2'
    mock_queue.put(task3)
    assert mock_queue.qsize() == 2


def test_mock_queue_get_put_same_task():
    mock_queue.clear()

    task = MockTask()
    task.test = 'my_test'
    mock_queue.put(task)

    assert mock_queue.qsize() == 1

    my_task = mock_queue.get()
    assert my_task.test == 'my_test'
    assert mock_queue.qsize() == 0

    mock_queue.put(my_task)
    assert mock_queue.qsize() == 1


@pytest.mark.skipif(do_live_testing is False,
                    reason='Live Redis testing not enabled.')
def test_live_queue():
    live_queue = RedisQueue("test_queue", MockTask, namespace="pytest")
    assert live_queue.connected is False

    task = MockTask()
    task2 = MockTask()

    task.uri = 'thisIsUnique'
    task2.uri = 'thisIsUnique'

    assert live_queue.connect(host=live_host, port=live_port,
                              password=live_pass) is True
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
    assert new_task.uri == 'thisIsUnique'

    live_queue.clear()

    task.unique = True
    task2.unique = True

    assert task.unique_hash() == task2.unique_hash()

    live_queue.put(task)

    with pytest.raises(TaskAlreadyInQueueException):
        live_queue.put(task2)

    assert live_queue.qsize == 1

    live_queue.clear()

    # test getting and putting the same task into the queue
    assert live_queue.qsize == 0

    live_queue.put(task)
    my_task = live_queue.get()
    live_queue.put(my_task)

    assert live_queue.qsize == 1
