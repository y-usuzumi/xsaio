#!/usr/bin/env python3
import time
import queue
import heapq
import select
from .log import def_log


def norm_delay(t):
    return t / 1000


class _Timeout:
    """EventLoop的超时任务。严重借鉴了Tornado框架的对应实现
    """
    def __init__(self, deadline, callback, is_periodic=False, delay=None):
        self._deadline = deadline
        self._callback = callback
        self._is_periodic = is_periodic
        self._delay = delay

    @property
    def deadline(self):
        return self._deadline

    @property
    def callback(self):
        return self._callback

    @property
    def is_periodic(self):
        return self._is_periodic

    @property
    def delay(self):
        return self._delay

    def __lt__(self, other):
        """创建最小堆时，用于按deadline进行排序
        """
        return self.deadline < other.deadline

    def __repr__(self):
        return "<Timeout is_periodic=%s deadline=%s>" % (self.is_periodic, self.deadline)


class EventLoop:
    """事件循环
    """
    def __init__(self, *, impl):
        self._event_queue = queue.Queue()
        self._next_tick_event_queue = queue.Queue()
        self._time = None
        self._timeouts = []
        self._fd_handlers = {}
        self._impl = impl

    def next_tick(self):
        self._time = time.time()
        due_timeouts = []
        while self._timeouts:
            curr_timeout = self._timeouts[0]
            if curr_timeout.deadline <= self._time:
                timeout = heapq.heappop(self._timeouts)
                if curr_timeout.callback:
                    due_timeouts.append(timeout)
                    if timeout.is_periodic:
                        next_timeout = _Timeout(
                            timeout.deadline + timeout.delay,
                            timeout.callback,
                            is_periodic=True,
                            delay=timeout.delay
                        )
                        heapq.heappush(self._timeouts, next_timeout)
                        heapq.heapify(self._timeouts)
                else:
                    heapq.heappop(self._timeouts)
            else:
                break
        for timeout in due_timeouts:
            timeout.callback()

        while not self._event_queue.empty():
            event = self._event_queue.get()
            event.handle()

        self._impl.poll(timeout=1)

    def process_event(self, event):
        event.handle()

    def _set_timeout(self, callback, delay, periodic=False):
        delay = norm_delay(delay)
        deadline = time.time() + delay
        timeout = _Timeout(
            deadline, callback, is_periodic=periodic, delay=delay
        )
        heapq.heappush(self._timeouts, timeout)

    def set_timeout(self, callback, delay):
        self._set_timeout(callback, delay, periodic=False)

    def set_interval(self, callback, interval):
        self._set_timeout(callback, interval, periodic=True)

    def add_handler(self, fd, callback, io_events):
        def_log.debug("FD: %s" % fd)
        self._fd_handlers.setdefault(fd, []).append(callback)
        def_log.debug("Events: %s" % io_events)
        self._impl.register(fd, io_events | self.ERROR)

    def remove_handler(self, fd):
        self._fd_handlers.pop(fd, None)
        try:
            self._impl.unregister(fd)
        except Exception:
            def_log.debug("Error deleting fd from IOLoop", exc_info=True)


    def run(self):
        while True:
            self.next_tick()


class EPollEventLoop(EventLoop):
    # Constants from the epoll module
    _EPOLLIN = 0x001
    _EPOLLPRI = 0x002
    _EPOLLOUT = 0x004
    _EPOLLERR = 0x008
    _EPOLLHUP = 0x010
    _EPOLLRDHUP = 0x2000
    _EPOLLONESHOT = (1 << 30)
    _EPOLLET = (1 << 31)

    # Our events map exactly to the epoll events
    NONE = 0
    READ = _EPOLLIN
    WRITE = _EPOLLOUT
    ERROR = _EPOLLERR | _EPOLLHUP

    def __init__(self, **kwargs):
        super().__init__(impl=select.epoll())

    def register(self, fd, events):
        select.epoll.register(fd, events | self.ERROR)
