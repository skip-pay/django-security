import copy

from contextvars import ContextVar

from uuid import uuid4

from contextlib import ContextDecorator

from security.config import settings
from security.utils import get_object_triple


undefined = object()

# Stack of currently open loggers, used to link a logger to its parent.
#
# A ContextVar isolates the stack per thread and per asyncio task. The value is an
# immutable tuple so that the default is never mutated in place and contexts cannot
# share a list by reference.
_loggers_stack = ContextVar('security_loggers', default=())


class _LoggersStack:
    """
    Read-only access to the current logger stack via ``SecurityLogger.loggers``,
    kept for backward compatibility. Returns a tuple, not a mutable list.
    """

    def __get__(self, obj, objtype=None):
        return _loggers_stack.get()


class SecurityLogger(ContextDecorator):

    loggers = _LoggersStack()
    logger_name = None
    store = True

    def __init__(self, id=None, parent_log=undefined, related_objects=None, slug=None, extra_data=None,
                 start=None, stop=None, error_message=None, time=None, release=None):
        self.id = id or (uuid4() if self.logger_name else None)
        loggers = _loggers_stack.get()
        self.parent = loggers[-1] if loggers else None

        self.related_objects = set()
        if related_objects:
            self.add_related_objects(*related_objects)

        self.start = start
        self.stop = stop
        self.error_message = error_message
        self.release = release or settings.RELEASE

        self.slug = slug
        if self.parent:
            self.related_objects |= self.parent.related_objects
            if not self.slug:
                self.slug = self.parent.slug
        parent_with_id = self._get_parent_with_id()
        self.parent_log = (
            '{}|{}'.format(parent_with_id.logger_name.value, parent_with_id.id) if parent_with_id else None
        ) if parent_log is undefined else parent_log

        self._extra_data = extra_data
        if self._extra_data is None:
            self._extra_data = self.parent.extra_data if self.parent else {}

        if self.store:
            _loggers_stack.set(_loggers_stack.get() + (self,))

        self.backend_logs = {}
        self.stream = None

    def _get_parent_with_id(self):
        parent = self.parent
        while parent and not parent.id:
            parent = parent.parent
        return parent

    @property
    def time(self):
        return (self.stop - self.start).total_seconds() if self.start and self.stop else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.store:
            self.close()

    def set_slug(self, slug):
        self.slug = slug

    def add_related_objects(self, *related_objects):
        self.related_objects |= set(get_object_triple(obj) for obj in related_objects)

    @property
    def extra_data(self):
        return copy.deepcopy(self._extra_data)

    def update_extra_data(self, data):
        self._extra_data.update(data)

    def close(self):
        loggers = _loggers_stack.get()
        if not loggers or loggers[-1] != self:
            raise RuntimeError('Log already finished')

        _loggers_stack.set(loggers[:-1])

    def to_dict(self):
        return dict(
            extra_data=self.extra_data,
            time=self.time,
            **{k: v for k, v in self.__dict__.items() if k not in {
                'backend_logs', 'stream', 'store', 'logger_name', 'loggers', 'parent'
            } and not k.startswith('_')}
        )


def get_last_logger(name):
    for logger in reversed(_loggers_stack.get()):
        if logger.logger_name == name:
            return logger
    return None
