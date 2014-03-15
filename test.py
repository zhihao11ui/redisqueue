__author__ = 'Jeff Kehler'


from redisqueue import Queue, Task

queue = Queue('test')
queue.connect()

mydict = {}
mydict['do'] = 'me'
task = Task(mydict)

queue.put(task)

# task = Task({'do': 'to'})
# task.unique = True
# queue.put(task)

#print(queue.qsize)

#item = queue.get()
#
# print(item.payload)
# print(task.hash)