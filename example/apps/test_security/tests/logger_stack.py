import threading

from germanium.test_cases.default import GermaniumTestCase
from germanium.tools import assert_equal, assert_is_none, assert_raises

from security.logging.common import SecurityLogger, get_last_logger

from security.enums import LoggerName


class NamedLogger(SecurityLogger):

    logger_name = LoggerName.INPUT_REQUEST


class LoggerStackTestCase(GermaniumTestCase):
    """
    The stack of open loggers must be isolated per thread.

    It used to be a plain class attribute, which is shared by the whole process even
    though SecurityLogger inherited from threading.local (only instance attributes are
    thread-local). Concurrent threads therefore pushed onto one shared stack, which
    linked a logger to a parent from another thread and made close() raise
    "Log already finished" for a logger that was still valid.
    """

    def test_logger_stack_should_be_empty_by_default(self):
        assert_equal(SecurityLogger.loggers, ())

    def test_nested_loggers_should_be_linked_to_parent_and_pop_in_order(self):
        with SecurityLogger() as outer:
            assert_is_none(outer.parent)
            assert_equal(SecurityLogger.loggers, (outer,))

            with SecurityLogger() as inner:
                assert_equal(inner.parent, outer)
                assert_equal(SecurityLogger.loggers, (outer, inner))

            assert_equal(SecurityLogger.loggers, (outer,))

        assert_equal(SecurityLogger.loggers, ())

    def test_logger_closed_out_of_order_should_raise(self):
        with SecurityLogger() as outer:
            inner = SecurityLogger()
            assert_raises(RuntimeError, outer.close)
            inner.close()

    def test_logger_with_store_disabled_should_not_enter_stack(self):
        class NotStoredLogger(SecurityLogger):
            store = False

        with SecurityLogger() as outer:
            not_stored = NotStoredLogger()
            assert_equal(SecurityLogger.loggers, (outer,))

            with SecurityLogger() as inner:
                assert_equal(inner.parent, outer)

            assert_equal(not_stored.parent, outer)

    def test_get_last_logger_should_find_logger_by_name(self):
        assert_is_none(get_last_logger(LoggerName.INPUT_REQUEST))

        with NamedLogger() as named:
            with SecurityLogger():
                assert_equal(get_last_logger(LoggerName.INPUT_REQUEST), named)

        assert_is_none(get_last_logger(LoggerName.INPUT_REQUEST))

    def test_concurrent_threads_should_not_share_the_logger_stack(self):
        thread_count = 2
        # Force both threads to keep their logger open at the same time, so that a
        # shared stack is guaranteed to interleave instead of relying on timing.
        both_opened = threading.Barrier(thread_count)
        errors = []
        parents = []

        def open_close_logger():
            try:
                with SecurityLogger() as logger:
                    parents.append(logger.parent)
                    assert_equal(SecurityLogger.loggers, (logger,))
                    both_opened.wait(timeout=5)
            except Exception as ex:
                errors.append(ex)

        threads = [threading.Thread(target=open_close_logger) for _ in range(thread_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        assert_equal(errors, [])
        assert_equal(parents, [None] * thread_count)
        assert_equal(SecurityLogger.loggers, ())

    def test_logger_opened_in_thread_should_not_leak_to_other_threads(self):
        seen_in_thread = []

        with SecurityLogger() as outer:
            def read_stack():
                seen_in_thread.append(SecurityLogger.loggers)

            thread = threading.Thread(target=read_stack)
            thread.start()
            thread.join(timeout=10)

            assert_equal(SecurityLogger.loggers, (outer,))

        assert_equal(seen_in_thread, [()])
