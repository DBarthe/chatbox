# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_pseudo', models.CharField(max_length=64, verbose_name="author's pseudo")),
                ('author_ip', models.GenericIPAddressField(null=True, verbose_name="author's ip address")),
                ('content', models.TextField(verbose_name='message content')),
                ('datetime', models.DateTimeField(help_text='the datetime of the message creation', verbose_name='date and time', auto_now_add=True)),
            ],
        ),
    ]
