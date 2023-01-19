.. _commands:

Commands
========

purge_logs
---------

Remove old request, command or celery logs that are older than defined value, parameters:

* ``expiration`` - timedelta from which logs will be removed. Units are h - hours, d - days, w - weeks, m - months, y - years
* ``noinput`` - tells Django to NOT prompt the user for input of any kind
* ``backup`` - tells Django where to backup removed logs in JSON format
* ``type`` - tells Django what type of requests should be removed (input-request/output-request/command/celery-task-invocation/celery-task-run)

Logs can be removed only for ``elasticsearch`` and ``sql`` backends.

set_celery_task_log_state
-------------------------

Set celery tasks which are in WAITING state. Tasks which were not started more than ``SECURITY_CELERY_STALE_TASK_TIME_LIMIT_MINUTES`` (by default 60 minutes) to the failed state. Task with succeeded/failed task run is set to succeeded/failed state.
