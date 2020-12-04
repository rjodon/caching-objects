"""
Create an odered dict with time limits on each of its content
"""
import sched
import time
import threading
import queue
from collections import OrderedDict
from operator import itemgetter


class PeriodicScheduler(object):
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def setup(self, interval, action, actionargs=()):
        action(*actionargs)
        self.scheduler.enter(interval, 1, self.setup, (interval, action, actionargs))

    def run(self):
        self.scheduler.run(blocking=True)


class OrderedDictTL(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_timer_started = False
        self.queue = queue.Queue()
        self.queue.put(self)
        self.queue.put(self)
        #
        self.t = threading.Thread(target=self.scheduled_prune, daemon=True)
        self.t.start()

    def __getitem__(self, key):
        _ = self.queue.get()
        self = self.queue.get()
        value = super().__getitem__(key)
        value[0] = time.time() + value[1]   # update next expiring time
        self.expiracy_sorted = OrderedDict(sorted(self.items(), key=itemgetter(1)))
        self.queue.put(self.expiracy_sorted)
        self.queue.put(self)
        return value

    def __setitem__(self, key, value):
        _ = self.queue.get()
        self = self.queue.get()
        if key in self:
            self.__getitem__(key)           # will only update expiracy
            return
        # .      when expires            expiry    content
        value = [time.time() + value[0], value[0], value[1]]
        super().__setitem__(key, value)
        self.expiracy_sorted = OrderedDict(sorted(self.items(), key=itemgetter(1)))

        self.queue.put(self.expiracy_sorted)
        self.queue.put(self)

    def __del__(self):
        self.t.join(0)

    @staticmethod
    def prune_expired(queue):
        print("watcher")
        now = time.time()
        expiracy_sorted = queue.get()
        obj = queue.get()
        to_prune = []
        for k, v in expiracy_sorted.items():
            if now >= v[0]:
                to_prune.append(k)
            else:
                break
        for k in to_prune:
            queue.put(expiracy_sorted)
            queue.put(obj)
            obj.pop(k)
            expiracy_sorted.pop(k)
            print("{} expired".format(k))
        queue.put(expiracy_sorted)
        queue.put(obj)
        print("watcher: ", expiracy_sorted)
        print("watcher: ", obj)

    def scheduled_prune(self):
        ps = PeriodicScheduler()
        ps.setup(1, self.prune_expired, actionargs=(self.queue,))
        ps.run()


pages = OrderedDictTL()
pages['a'] = [10, "content a"]
print("a added")
time.sleep(2)
pages['b'] = [6, "content b"]
print("b added")
pages['c'] = [2, "content c"]
print("c added")
time.sleep(3)
pages['b']
print("page b accessed")

del pages

try:
    while True:
        pass
except KeyboardInterrupt:
    print(pages)