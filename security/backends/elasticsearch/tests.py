from uuid import uuid4

from django.test.utils import override_settings

from .models import CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog, InputRequestLog, OutputRequestLog
from .models import PartitionedLog


class store_elasticsearch_log(override_settings):

    def __init__(self, **kwargs):
        super().__init__(
            SECURITY_BACKEND_WRITERS=('elasticsearch',), SECURITY_ELASTICSEARCH_AUTO_REFRESH=True, **kwargs
        )

    def enable(self):
        from .connection import set_connection

        super().enable()
        uuid = uuid4()
        set_connection()
        for document_class in (CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog,
                               InputRequestLog, OutputRequestLog):
            document_class._index._name = f'{uuid}.{document_class._index._name}'
            if issubclass(document_class, PartitionedLog):
                template = document_class.get_template()
                template.save()
            else:
                document_class.init()

    def disable(self):
        for document_class in (CommandLog, CeleryTaskRunLog, CeleryTaskInvocationLog,
                               InputRequestLog, OutputRequestLog):
            document_class._index.delete()
            document_class._index._name = document_class._index._name.split('.', 1)[1]
        super().disable()
