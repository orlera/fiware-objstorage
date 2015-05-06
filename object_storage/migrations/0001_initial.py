# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('attachment', models.FileField(upload_to=b'storage')),
                ('upload_date', models.DateTimeField(verbose_name=b'uploaded on')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
