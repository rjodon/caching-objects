 """
 Timed cache - Version with threading Timer
 """
import time
from collections import OrderedDict
from threading import Timer, Lock


page_cache = OrderedDict()


class Periodic:
    """
    A periodic task running in threading.Timers
    """

    def __init__(self, interval, function, *args, **kwargs):
        self._lock = Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        if kwargs.pop('autostart', True):
            self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


def prune_expired():
    now = time.time()
    to_prune = []
    for k, v in page_cache.items():
        if now - v[1]  > v[0]:
            to_prune.append(k)
    for k in to_prune:
        page_cache.pop(k)
        print("{} expired".format(k))


scheduler = Periodic(0.5, prune_expired)

page_cache['a'] = [10, time.time(), "content a"]
time.sleep(2)
page_cache['b'] = [6, time.time(), "content b"]
time.sleep(2)
page_cache['c'] = [6, time.time(), "content c"]
time.sleep(2)
page_cache['d'] = [6, time.time(), "content d"]
time.sleep(2)
page_cache['e'] = [4, time.time(), "content e"]

try:
    while True:
        pass
except KeyboardInterrupt:
    pass