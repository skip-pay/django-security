# Generated by Django 3.1.4 on 2020-12-21 18:49

from django.db import migrations, models
import django.core.serializers.json


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0001_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytasklog',
            name='task_args',
            field=models.JSONField(blank=True, editable=False, encoder=django.core.serializers.json.DjangoJSONEncoder,
                                   null=True, verbose_name='task args'),
        ),
        migrations.AlterField(
            model_name='celerytasklog',
            name='task_kwargs',
            field=models.JSONField(blank=True, editable=False, encoder=django.core.serializers.json.DjangoJSONEncoder,
                                   null=True, verbose_name='task kwargs'),
        ),
        migrations.AlterField(
            model_name='celerytaskrunlog',
            name='result',
            field=models.JSONField(blank=True, editable=False, encoder=django.core.serializers.json.DjangoJSONEncoder,
                                   null=True, verbose_name='result'),
        ),
        migrations.AlterField(
            model_name='celerytaskrunlog',
            name='task_args',
            field=models.JSONField(blank=True, editable=False, encoder=django.core.serializers.json.DjangoJSONEncoder,
                                   null=True, verbose_name='task args'),
        ),
        migrations.AlterField(
            model_name='celerytaskrunlog',
            name='task_kwargs',
            field=models.JSONField(blank=True, editable=False, encoder=django.core.serializers.json.DjangoJSONEncoder,
                                   null=True, verbose_name='task kwargs'),
        ),
        migrations.AlterField(
            model_name='inputloggedrequest',
            name='queries',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True,
                                   verbose_name='queries'),
        ),
        migrations.AlterField(
            model_name='inputloggedrequest',
            name='request_headers',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True,
                                   verbose_name='request headers'),
        ),
        migrations.AlterField(
            model_name='inputloggedrequest',
            name='response_headers',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True,
                                   verbose_name='response headers'),
        ),
        migrations.AlterField(
            model_name='outputloggedrequest',
            name='queries',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True,
                                   verbose_name='queries'),
        ),
        migrations.AlterField(
            model_name='outputloggedrequest',
            name='request_headers',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True,
                                   verbose_name='request headers'),
        ),
        migrations.AlterField(
            model_name='outputloggedrequest',
            name='response_headers',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True,
                                   verbose_name='response headers'),
        ),
    ]