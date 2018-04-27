import enum
from queue import Queue
from functools import partial
from .log import def_log

__all__ = ['Promise']


class _PromiseState(enum.IntEnum):
    Pending = 0
    Resolved = 1
    Rejected = 2


class PromiseError(Exception):
    pass


class InvalidPromiseStateError(PromiseError):
    pass


class Promise:
    def __init__(self, *, event_loop):
        self._event_loop = event_loop
        self._status = _PromiseState.Pending
        self._thens = Queue()
        self._value = None
        self._reason = None

    def _on_resolved(self, result=None):
        if self._status != _PromiseState.Pending:
            raise InvalidPromiseStateError
        self._status = _PromiseState.Resolved
        self._value = result
        while not self._thens.empty():
            then = self._thens.get()

            def _make_resolver():
                return partial(then.resolve, result=result)

            self._event_loop.set_immediate(_make_resolver())

    def _on_rejected(self, reason=None):
        if self.status != _PromiseState.Pending:
            raise InvalidPromiseStateError
        self._status = _PromiseState.Rejected
        self._reason = reason
        while not self._thens.empty():
            then = self._thens.get()

            def _rejector():
                return partial(then.reject, reason=reason)

            self._event_loop.set_immediate(_rejector)

    def then(self, on_resolved=None, on_rejected=None):
        then_ = Then(on_resolved, on_rejected)
        self._thens.put(then_)
        return then_


class InstantPromise(Promise):
    def __init__(self, task, *, event_loop):
        self._task = task
        self._event_loop.set_immediate(self._wrap_task(task))
        super().__init__(event_loop=event_loop)

    def _wrap_task(self, task):
        return partial(task, self._on_resolved, self._on_rejected)

    def then(self, on_resolved=None, on_rejected=None):
        then_ = Then(on_resolved, on_rejected)
        self._thens.put(then_)
        return then_


class Then(Promise):
    def __init__(self, on_resolved, on_rejected):
        self._on_resolved = on_resolved
        self._on_rejected = on_rejected

    def resolve(self, result=None):
        if callable(self._on_resolved):
            self._on_resolved(result=result)

    def reject(self, reason=None):
        if callable(self._on_rejected):
            self._on_rejected(reason=reason)
