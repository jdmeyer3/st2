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

from st2common import log as logging
from st2common.models.db import MongoDBAccess
from st2common.models.db import stormbase

__all__ = [
    'ActionExecutionStateDB',
]


LOG = logging.getLogger(__name__)

PACK_SEPARATOR = '.'


class ActionExecutionStateDB(stormbase.StormFoundationDB):
    """
        Database entity that represents the state of Action execution.
    """
    execution_id = me.ObjectIdField(
        required=True,
        verbose_name='liveaction ID.')
    query_module = me.CharField(
        required=True,
        verbose_name='Reference to the runner model.')
    query_context = me.DictField(
        required=True,
        verbose_name='Context about the action execution that is needed for results query.')

    class Meta:
        indexes = [
            pymongo.IndexModel([('execution_id', pymongo.TEXT)], unique=True),
            pymongo.IndexModel([('query_module', pymongo.OFF)])
        ]


# specialized access objects
actionexecstate_access = MongoDBAccess(ActionExecutionStateDB)

MODELS = [ActionExecutionStateDB]
