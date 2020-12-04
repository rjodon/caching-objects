"""
Create an odered dict with time limits on each of its content
"""
import sched
import time
import threading
import queue
from collections import OrderedDict
from operator import itemgetter

stop_timer = False


class PeriodicScheduler(object):
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)

    def setup(self, interval, action, actionargs=()):
        print("Setup in")
        if actionargs[1].empty() is False:
            stop_timer = actionargs[1].get()
        else:
            stop_timer = False
        print("Setup: ", stop_timer or False)
        if stop_timer is False:
            action(actionargs[0])
            self.actionargs = actionargs
            self.interval = interval
            self.scheduler.enter(self.interval, 0, self.setup, (self.interval, action, self.actionargs))

    def run(self):
        self.scheduler.run(blocking=True)


class OrderedDictTL(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_timer_started = False
        self.queue = queue.Queue()
        self.queue.put(self)
        self.queue.put(self)
        self.stopqueue = queue.Queue()
        self.t = None

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
        self.startstoptimer_if_needed()
        if key in self:
            self.__getitem__(key)           # will only update expiracy
            return
        # .      when expires            expiry    content
        value = [time.time() + value[0], value[0], value[1]]
        super().__setitem__(key, value)
        self.expiracy_sorted = OrderedDict(sorted(self.items(), key=itemgetter(1)))

        self.queue.put(self.expiracy_sorted)
        self.queue.put(self)

    def pop(self, key):
        r = super().pop(key)
        if len(self) == 0:
            self.startstoptimer_if_needed(stop=True)
        return r

    def startstoptimer_if_needed(self, stop=False):
        if self.t is None:
            self.stopqueue.put(False)
            self.t = threading.Thread(target=self.scheduled_prune, args=(self.queue,), daemon=False)
            print("starting")
            self.t.start()
        if stop is True:
            self.stopqueue.put(True)
            print("stopping")
            self.t.join(timeout=5)
            self.t = None

    @staticmethod
    def prune_expired(queue):
        print("watcher")
        now = time.time()
        expiracy_sorted = queue.get()
        obj = queue.get()
        to_prune = []
        print(expiracy_sorted)
        for k, v in expiracy_sorted.items():
            if now >= v[0]:
                to_prune.append(k)
            else:
                break
        print(to_prune)
        for k in to_prune:
            queue.put(expiracy_sorted)
            queue.put(obj)
            obj.pop(k)
            print("{} expired".format(k))
        expiracy_sorted = OrderedDict(sorted(obj.items(), key=itemgetter(1)))
        queue.put(expiracy_sorted)
        queue.put(obj)

    def scheduled_prune(self, stop_timer):
        self.ps = PeriodicScheduler()
        self.ps.setup(interval=1, action=self.prune_expired, actionargs=[self.queue, self.stopqueue])
        self.ps.run()


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

try:
    while True:
        pass
except KeyboardInterrupt:
    print(pages)