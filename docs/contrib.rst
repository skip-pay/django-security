Extra
=====

Django-security-logger provides extra features to improve your logged data.

security.contrib.debug_toolbar_log
----------------------------------

If you are using ``django-debug-toolbar`` you can log toolbar results with logged request. You only add extension to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'security.contrib.debug_toolbar_log',
        ...
    )

And add  ``security.contrib.debug_toolbar_log.middleware.DebugToolbarLogMiddleware`` on the first place::

    MIDDLEWARE = (
        'security.contrib.debug_toolbar_log.middleware.DebugToolbarLogMiddleware',
        ...
    )

Finally you can start log debug toolbar settings with your logged requests by turning on settings::

    SECURITY_DEBUG_TOOLBAR = True

Do not forget turn on django DEBUG.

To show results in ``django-is-core`` you must set setting::

    SECURITY_SHOW_DEBUG_TOOLBAR = True


django-is-core
--------------

Backends ``elasticsearch`` and ``sql`` provide prepared django-is-core administration. If you are using django-is-core library you can find admin core classes in:
* elasticsearch - ``security.elasticsearch.is_core.cores``
    * ``InputRequestLogCore``
    * ``OutputRequestLogCore``
    * ``CommandLogCore``
    * ``CeleryTaskRunLogCore``
    * ``CeleryTaskInvocationLogCore``
* sql - ``security.sql.is_core.cores``
    * ``InputRequestLogCore``
    * ``OutputRequestLogCore``
    * ``CommandLogCore``
    * ``CeleryTaskRunLogCore``
    * ``CeleryTaskInvocationLogCore``
