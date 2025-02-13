from django.conf import settings as django_settings


DEFAULTS = {
    'DEFAULT_THROTTLING_VALIDATORS_PATH': 'security.throttling.default_validators',
    'THROTTLING_FAILURE_VIEW': 'security.throttling.views.throttling_failure_view',
    'LOG_REQUEST_IGNORE_IP': (),
    'LOG_REQUEST_IGNORE_URL_PATHS': (),
    'LOG_REQUEST_BODY_LENGTH': 10000,
    'LOG_RESPONSE_BODY_LENGTH': 10000,
    'LOG_RESPONSE_BODY_CONTENT_TYPES': (
        'application/json', 'application/xml', 'text/xml', 'text/csv',
    ),
    'LOG_JSON_STRING_LENGTH': 250,
    'COMMAND_LOG_EXCLUDED_COMMANDS': (
        'runserver', 'makemigrations', 'migrate', 'sqlmigrate', 'showmigrations', 'shell', 'shell_plus', 'test',
        'help', 'reset_db', 'compilemessages', 'makemessages', 'dumpdata', 'loaddata', 'init_elasticsearch_log'
    ),
    'HIDE_SENSITIVE_DATA': True,
    'HIDE_SENSITIVE_DATA_PATTERNS': {
        'BODY': (
            r'"password"\s*:\s*"((?:\\"|[^"])*)',
            r'<password>([^<]*)',
            r'password=([^&]*)',
            r'csrfmiddlewaretoken=([^&]*)',
            r'(?i)content-disposition: form-data; name="password"\r\n\r\n.*',
            r'"access_key": "([^"]*)',
        ),
        'HEADERS': (
            r'Authorization',
            r'X_Authorization',
            r'Cookie',
            r'.*token.*',
        ),
        'QUERIES': (
            r'.*token.*',
        ),
    },
    'SENSITIVE_DATA_REPLACEMENT': '[Filtered]',
    'APPEND_SLASH': True,
    'BACKUP_STORAGE_CLASS': 'security.storages.BackupFileSystemStorage',
    'BACKUP_STORAGE_PATH': None,
    'DEBUG_TOOLBAR': False,
    'DEBUG_TOOLBAR_IGNORE_URL_REGEX_PATHS': (),
    'SHOW_DEBUG_TOOLBAR': False,
    'LOG_OUTPUT_REQUESTS': True,
    'AUTO_GENERATE_TASKS_FOR_DJANGO_COMMANDS': {},
    'CELERY_HEALTH_CHECK_DEFAULT_QUEUE': getattr(django_settings, 'CELERY_DEFAULT_QUEUE', 'default'),
    'LOG_DB_NAME': None,
    'CLEAN_LOGS_BACKUP_FILE_BATCH_SIZE': 10000,
    'TASK_LOGGER_NAME': 'security.task',
    'TASK_USE_PRE_COMMIT': False,
    'ELASTICSEARCH_DATABASE': None,
    'ELASTICSEARCH_LOGSTASH_WRITER': False,
    'ELASTICSEARCH_VECTOR_WRITER': False,
    'ELASTICSEARCH_AUTO_REFRESH': False,
    'ELASTICSEARCH_CLEAN_LOGS_READ_BATCH_SIZE': 1000,
    'ELASTICSEARCH_CLEAN_LOGS_DELETE_BATCH_SIZE': 1000,
    'ELASTICSEARCH_CLEAN_LOGS_DELETE_REQUEST_TIMEOUT': 30,
    'ELASTICSEARCH_CLEAN_LOGS_DELETE_ATTEMPTS': 10,
    'ELASTICSEARCH_CLEAN_LOGS_DELETE_ATTEMPT_SLEEP': 5,
    'ELASTICSEARCH_MAX_NUMBER_OF_TERMS': 65536,
    'ELASTICSEARCH_TIMEOUT': 10,
    'SQL_CLEAN_LOGS_DELETE_BATCH_SIZE': 1000,
    'BACKEND_WRITERS': None,
    'BACKEND_READER': None,
    'LOG_STRING_IO_FLUSH_TIMEOUT': 5,
    'SET_STALE_CELERY_INVOCATIONS_LIMIT_PER_RUN': 1000,
    'SET_STALE_CELERY_AGE_DAYS_LIMIT_PER_RUN': 30,
    'RELEASE': None,
    'RAISE_WRITER_EXCEPTIONS': False,
    'THROTTLING_ENABLED': True,
    'LOG_STRING_OUTPUT_TRUNCATE_LENGTH': 10000,
    'LOG_STRING_OUTPUT_TRUNCATE_OFFSET': 1000,
}


class Settings:

    def __getattr__(self, attr):
        if attr not in DEFAULTS:
            raise AttributeError('Invalid Security setting: "{}"'.format(attr))

        return getattr(django_settings, 'SECURITY_{}'.format(attr), DEFAULTS[attr])


settings = Settings()
