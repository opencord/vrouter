# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-02-21 01:31
from __future__ import unicode_literals

import core.models.xosbase_header
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0002_initial_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='VRouterService',
            fields=[
                ('service_decl_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Service_decl')),
            ],
            options={
                'verbose_name': 'vRouter Service',
            },
            bases=('core.service',),
        ),
        migrations.CreateModel(
            name='VRouterServiceInstance',
            fields=[
                ('serviceinstance_decl_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ServiceInstance_decl')),
            ],
            options={
                'verbose_name': 'vRouter Service Instance',
            },
            bases=('core.serviceinstance',),
        ),
        migrations.CreateModel(
            name='VRouterStaticRoute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text=b'Time this model was created')),
                ('updated', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Time this model was changed by a non-synchronizer')),
                ('enacted', models.DateTimeField(blank=True, default=None, help_text=b'When synced, set to the timestamp of the data that was synced', null=True)),
                ('policed', models.DateTimeField(blank=True, default=None, help_text=b'When policed, set to the timestamp of the data that was policed', null=True)),
                ('backend_register', models.CharField(blank=True, default=b'{}', max_length=1024, null=True)),
                ('backend_need_delete', models.BooleanField(default=False)),
                ('backend_need_reap', models.BooleanField(default=False)),
                ('backend_status', models.CharField(default=b'Provisioning in progress', max_length=1024, null=True)),
                ('backend_code', models.IntegerField(default=0)),
                ('deleted', models.BooleanField(default=False)),
                ('write_protect', models.BooleanField(default=False)),
                ('lazy_blocked', models.BooleanField(default=False)),
                ('no_sync', models.BooleanField(default=False)),
                ('no_policy', models.BooleanField(default=False)),
                ('policy_status', models.CharField(blank=True, default=b'Policy in process', max_length=1024, null=True)),
                ('policy_code', models.IntegerField(blank=True, default=0, null=True)),
                ('leaf_model_name', models.CharField(help_text=b'The most specialized model in this chain of inheritance, often defined by a service developer', max_length=1024)),
                ('backend_need_delete_policy', models.BooleanField(default=False, help_text=b'True if delete model_policy must be run before object can be reaped')),
                ('xos_managed', models.BooleanField(default=True, help_text=b'True if xos is responsible for creating/deleting this object')),
                ('backend_handle', models.CharField(blank=True, help_text=b'Handle used by the backend to track this object', max_length=1024, null=True)),
                ('changed_by_step', models.DateTimeField(blank=True, default=None, help_text=b'Time this model was changed by a sync step', null=True)),
                ('changed_by_policy', models.DateTimeField(blank=True, default=None, help_text=b'Time this model was changed by a model policy', null=True)),
                ('prefix', models.CharField(help_text=b'The destination prefix and netmask (IP/NM)', max_length=52, unique=True)),
                ('next_hop', models.CharField(help_text=b'The next-hop for the route', max_length=52)),
                ('vrouter', models.ForeignKey(db_index=False, help_text=b'The static route to be configured in ONOS', on_delete=django.db.models.deletion.CASCADE, related_name='static_routes', to='vrouter.VRouterServiceInstance')),
            ],
            options={
                'verbose_name': 'vRouter static route',
            },
            bases=(models.Model, core.models.xosbase_header.PlModelMixIn),
        ),
    ]
