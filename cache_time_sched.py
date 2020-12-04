"""
Timed cache - Version with scheduler
"""
import sched
import time
import threading
import queue
from collections import OrderedDict
from operator import itemgetter



page_cache = OrderedDict()
q = queue.Queue()


class PeriodicScheduler(object):
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def setup(self, interval, action, actionargs=()):
        action(*actionargs)
        self.scheduler.enter(interval, 1, self.setup, (interval, action, actionargs))

    def run(self):
        self.scheduler.run(blocking=True)


def prune_expired(queue):
    print("toc")
    now = time.time()
    to_prune = []
    cache = q.get()
    for k, v in cache.items():
        print(k)
        if now >= v[0]:
            to_prune.append(k)
        else:
            break
    for k in to_prune:
        cache.pop(k)
        print("{} expired".format(k))
    q.put(cache)


def scheduled_prune(queue):
    ps = PeriodicScheduler()
    ps.setup(1, prune_expired, actionargs=(queue, ))
    ps.run()


q.put(page_cache)

t = threading.Thread(target=scheduled_prune, args=(q,), daemon=True)
t.start()


print("tic")

page = q.get()
page['a'] = [10 + time.time(), "content a"]
page = OrderedDict(sorted(page.items(), key=itemgetter(1)))
print(page)
q.put(page)
time.sleep(2)

page = q.get()
page['b'] = [10 + time.time(), "content b"]
page = OrderedDict(sorted(page.items(), key=itemgetter(1)))
print(page)
q.put(page)
time.sleep(2)

page = q.get()
page['c'] = [6 + time.time(), "content c"]
page = OrderedDict(sorted(page.items(), key=itemgetter(1)))
print(page)
q.put(page)
time.sleep(2)

page = q.get()
page['d'] = [6 + time.time(), "content d"]
page = OrderedDict(sorted(page.items(), key=itemgetter(1)))
print(page)
q.put(page)
time.sleep(2)

page = q.get()
page['e'] = [4 + time.time(), "content e"]
page = OrderedDict(sorted(page.items(), key=itemgetter(1)))
print(page)
q.put(page)


try:
    while True:
        pass
except KeyboardInterrupt:
    print(q.get())