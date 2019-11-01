# Copyright 2019 Extreme Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import pymodm as me
import pymongo

from st2common.constants import types
from st2common import fields as db_field_types
from st2common import log as logging
from st2common.models.db import stormbase
from st2common.util import date as date_utils


__all__ = [
    'WorkflowExecutionDB',
    'TaskExecutionDB'
]


LOG = logging.getLogger(__name__)


class WorkflowExecutionDB(stormbase.StormFoundationDB, stormbase.ChangeRevisionFieldMixin):
    RESOURCE_TYPE = types.ResourceType.EXECUTION

    action_execution = me.CharField(required=True)
    spec = stormbase.EscapedDictField()
    graph = stormbase.EscapedDictField()
    input = stormbase.EscapedDictField()
    notify = stormbase.EscapedDictField()
    context = stormbase.EscapedDictField()
    state = stormbase.EscapedDictField()
    status = me.CharField(required=True)
    output = stormbase.EscapedDictField()
    errors = stormbase.EscapedDynamicField()
    start_timestamp = db_field_types.ComplexDateTimeField(default=date_utils.get_datetime_utc_now)
    end_timestamp = db_field_types.ComplexDateTimeField()

    class Meta:
        indexes = [
            pymongo.IndexModel([('action_execution', pymongo.OFF)])
        ]


class TaskExecutionDB(stormbase.StormFoundationDB, stormbase.ChangeRevisionFieldMixin):
    RESOURCE_TYPE = types.ResourceType.EXECUTION

    workflow_execution = me.CharField(required=True)
    task_name = me.CharField(required=True)
    task_id = me.CharField(required=True)
    task_route = me.IntegerField(required=True, min_value=0)
    task_spec = stormbase.EscapedDictField()
    delay = me.IntegerField(min_value=0)
    itemized = me.BooleanField(default=False)
    items_count = me.IntegerField(min_value=0)
    items_concurrency = me.IntegerField(min_value=1)
    context = stormbase.EscapedDictField()
    status = me.CharField(required=True)
    result = stormbase.EscapedDictField()
    start_timestamp = db_field_types.ComplexDateTimeField(default=date_utils.get_datetime_utc_now)
    end_timestamp = db_field_types.ComplexDateTimeField()

    class Meta:
        indexes = [
            pymongo.IndexModel([('workflow_executions', pymongo.OFF)]),
            pymongo.IndexModel([('task_id', pymongo.OFF)]),
            pymongo.IndexModel([('task_id', pymongo.OFF), ('task_route', pymongo.OFF)]),
            pymongo.IndexModel([('workflow_execution', pymongo.OFF), ('task_id', pymongo.OFF)]),
            pymongo.IndexModel([('workflow_execution', pymongo.OFF), ('task_id', pymongo.OFF), ('task_route', pymongo.OFF)]),
        ]


MODELS = [
    WorkflowExecutionDB,
    TaskExecutionDB
]
