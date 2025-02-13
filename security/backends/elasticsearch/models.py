import json
from datetime import datetime
from elasticsearch import NotFoundError

from django.db import router
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.core.serializers.json import DjangoJSONEncoder

from elasticsearch_dsl import Q
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, Object, Boolean, Float, CustomField

from security.backends.common.mixins import (
    CeleryTaskInvocationLogStrMixin, CeleryTaskRunLogStrMixin, CommandLogStrMixin, InputRequestLogStrMixin,
    LogShortIdMixin, OutputRequestLogStrMixin
)
from security.config import settings
from security.enums import (
    RequestLogState, CeleryTaskInvocationLogState, CeleryTaskRunLogState, CommandState, LoggerName
)

from .connection import set_connection

WILDCARD = '*'


def get_index_name(logger_name, partitioned=True):
    index_name = '{}-{}-log'.format(
        settings.ELASTICSEARCH_DATABASE.get('prefix', 'security'),
        logger_name.value,
    )
    if partitioned:
        index_name += WILDCARD

    return index_name


class JSONTextField(CustomField):

    name = 'jsontext'
    builtin_type = Text()

    def serialize(self, data):
        if data is None:
            return None
        elif isinstance(data, str):
            return data
        else:
            return json.dumps(data, cls=DjangoJSONEncoder)


class EnumField(CustomField):

    name = 'enum'
    builtin_type = Keyword()

    def __init__(self, enum):
        self._enum = enum

    def _serialize(self, data):
        return data.name

    def _deserialize(self, data):
        if isinstance(data, self._enum):
            return data
        else:
            return self._enum[data]


class Log(LogShortIdMixin, Document):

    id = Keyword()
    extra_data = Object()
    slug = Keyword()
    related_objects = Keyword()
    parent_log = Keyword()
    start = Date()
    stop = Date()
    time = Float()
    release = Keyword()

    def __str__(self):
        return self.meta.id

    @classmethod
    def _get_using(cls, using=None):
        set_connection()
        return super()._get_using(using)

    @property
    def pk(self):
        return self.meta.id

    def update(
        self,
        using=None,
        index=None,
        detect_noop=True,
        doc_as_upsert=False,
        refresh=False,
        retry_on_conflict=None,
        script=None,
        script_id=None,
        scripted_upsert=False,
        upsert=None,
        return_doc_meta=False,
        update_only_changed_fields=False,
        **fields
    ):
        if update_only_changed_fields:
            fields = {k: v for k, v in fields.items() if getattr(self, k) != v}
        if fields:
            super().update(
                using, index, detect_noop, doc_as_upsert, refresh, retry_on_conflict, script, script_id,
                scripted_upsert, upsert, return_doc_meta, **fields
            )

    @classmethod
    def is_partitioned(cls):
        return '*' in cls._index._name


class PartitionedLog(Log):

    DAY_FORMAT = "%Y-%m-%d"
    INSTANT_REFRESH = False  # WARNING: OVERRIDE THIS ONLY FOR TESTS

    def save(self, **kwargs):
        # assign now if no timestamp given
        if not self.start:
            self.start = datetime.now()

        # override the index to go to the proper timeslot
        kwargs['index'] = self._format_index_name(self.start)

        # convenience for tests, to get rid of refresh latency
        if self.INSTANT_REFRESH:
            kwargs['refresh'] = self.INSTANT_REFRESH

        return super().save(**kwargs)

    @classmethod
    def get(cls, id, *_, **__):
        search = cls.search().query("term", _id=id)
        response = search.execute()
        return response.hits[0] if response.hits else None

    @classmethod
    def _format_index_name(cls, dt):
        return dt.strftime(f'{cls._index._name.replace("*", "")}-%Y-%m-%d')

    @classmethod
    def get_template(cls):
        index_name = cls._index._name.split("*")[0]
        return cls._index.as_template(index_name, order=0)

    @classmethod
    def init(cls, *_, **__):
        """
        Create the index and populate the mappings in elasticsearch.
        """
        template = cls.get_template()
        template.save()


class RequestLog(PartitionedLog):

    host = Keyword()
    method = Keyword()
    path = Keyword()
    queries = JSONTextField()
    is_secure = Boolean()

    # Request information
    request_headers = JSONTextField()
    request_body = Text()

    # Response information
    response_code = Keyword()
    response_headers = JSONTextField()
    response_body = Text()

    state = EnumField(enum=RequestLogState)
    error_message = Text()


class InputRequestLog(InputRequestLogStrMixin, RequestLog):

    user_id = Keyword()
    ip = Keyword()
    view_slug = Keyword()

    class Index:
        name = get_index_name(LoggerName.INPUT_REQUEST)

    @cached_property
    def user(self):
        return get_user_model().objects.filter(pk=self.user_id).first()


class OutputRequestLog(OutputRequestLogStrMixin, RequestLog):

    class Index:
        name = get_index_name(LoggerName.OUTPUT_REQUEST)


class CommandLog(CommandLogStrMixin, PartitionedLog):

    name = Keyword()
    input = Text()
    is_executed_from_command_line = Boolean()
    output = Text()
    is_successful = Boolean()
    state = EnumField(enum=CommandState)
    error_message = Text()

    class Index:
        name = get_index_name(LoggerName.COMMAND)


class CeleryTaskInvocationLog(CeleryTaskInvocationLogStrMixin, PartitionedLog):

    celery_task_id = Keyword()
    name = Keyword()
    queue_name = Keyword()
    applied_at = Date()
    triggered_at = Date()
    is_unique = Boolean()
    is_async = Boolean()
    is_on_commit = Boolean()
    input = Text()
    task_args = JSONTextField()
    task_kwargs = JSONTextField()
    estimated_time_of_first_arrival = Date()
    expires_at = Date()
    stale_at = Date()
    state = EnumField(enum=CeleryTaskInvocationLogState)

    @property
    def last_run(self):
        runs = CeleryTaskRunLog.search().filter(
            Q('term', celery_task_id=self.celery_task_id)
            & Q('range', start={"gt": self.start or now()})  # Task run follows after invocation
        ).sort('-start').execute()
        return runs[0] if runs else None

    class Index:
        name = get_index_name(LoggerName.CELERY_TASK_INVOCATION)


class CeleryTaskRunLog(CeleryTaskRunLogStrMixin, PartitionedLog):

    celery_task_id = Keyword()
    state = EnumField(enum=CeleryTaskRunLogState)
    name = Keyword()
    input = Text()
    task_args = JSONTextField()
    task_kwargs = JSONTextField()
    result = JSONTextField()
    error_message = Text()
    output = Text()
    retries = Integer()
    estimated_time_of_next_retry = Date()
    queue_name = Keyword()
    waiting_time = Float()

    class Index:
        name = get_index_name(LoggerName.CELERY_TASK_RUN)


def _get_content_type(model, using=None):
    return ContentType.objects.db_manager(using).get_for_model(model)


def get_key_from_content_type_object_id_and_model_db(content_type_pk, object_pk, model_db):
    return '|'.join((model_db, str(content_type_pk), str(object_pk)))


def get_key_from_object(obj, model_db=None):
    content_type = _get_content_type(obj)
    model_db = model_db or router.db_for_write(content_type.model_class())
    return get_key_from_content_type_object_id_and_model_db(content_type.pk, obj.pk, model_db)


def get_object_from_key(key):
    model_db, content_type_id, object_pk = key.split('|')
    return ContentType.objects.get(
        pk=content_type_id
    ).model_class().objects.using(model_db).filter(pk=object_pk).first()


def get_object_triple_from_key(key):
    return key.split('|')


def get_response_state(status_code):
    if status_code >= 500:
        return RequestLogState.ERROR
    elif status_code >= 400:
        return RequestLogState.WARNING
    else:
        return RequestLogState.INFO


logger_name_to_log_model = {
    LoggerName.INPUT_REQUEST: InputRequestLog,
    LoggerName.OUTPUT_REQUEST: OutputRequestLog,
    LoggerName.COMMAND: CommandLog,
    LoggerName.CELERY_TASK_INVOCATION: CeleryTaskInvocationLog,
    LoggerName.CELERY_TASK_RUN: CeleryTaskRunLog,
}


def get_log_model_from_logger_name(logger_name):
    return logger_name_to_log_model[logger_name]


def get_log_from_key(key):
    try:
        logger_name, id = key.split('|')
        return get_log_model_from_logger_name(logger_name).get(id=id)
    except NotFoundError:
        return None


def get_log_key(log):
    logger_name = {v: k for k, v in logger_name_to_log_model.items()}[log.__class__]
    return '{}|{}'.format(logger_name.value, log.meta.id)


def refresh_model(model):
    set_connection()
    model._index.refresh()
