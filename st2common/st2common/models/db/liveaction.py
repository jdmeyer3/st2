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
import copy

import pymodm as me
import pymongo

from st2common import log as logging
from st2common.models.db import MongoDBAccess
from st2common.models.db import stormbase
from st2common.models.db.notification import NotificationSchema
from st2common.fields import ComplexDateTimeField
from st2common.util import date as date_utils
from st2common.util.secrets import get_secret_parameters
from st2common.util.secrets import mask_secret_parameters

__all__ = [
    'LiveActionDB',
]

LOG = logging.getLogger(__name__)

PACK_SEPARATOR = '.'


class LiveActionDB(stormbase.StormFoundationDB):
    workflow_execution = me.CharField()
    task_execution = me.CharField()
    # TODO: Can status be an enum at the Mongo layer?
    status = me.CharField(
        required=True,
        verbose_name='The current status of the liveaction.')
    start_timestamp = ComplexDateTimeField(
        default=date_utils.get_datetime_utc_now,
        verbose_name='The timestamp when the liveaction was created.')
    end_timestamp = ComplexDateTimeField(
        verbose_name='The timestamp when the liveaction has finished.')
    action = me.CharField(
        required=True,
        verbose_name='Reference to the action that has to be executed.')
    action_is_workflow = me.BooleanField(
        default=False,
        verbose_name='A flag indicating whether the referenced action is a workflow.')
    parameters = stormbase.EscapedDynamicField(
        default={},
        verbose_name='The key-value pairs passed as to the action runner & execution.')
    result = stormbase.EscapedDynamicField(
        default={},
        verbose_name='Action defined result.')
    context = me.DictField(
        default={},
        verbose_name='Contextual information on the action execution.')
    callback = me.DictField(
        default={},
        verbose_name='Callback information for the on completion of action execution.')
    runner_info = me.DictField(
        default={},
        verbose_name='Information about the runner which executed this live action (hostname, pid).')
    notify = me.EmbeddedDocumentField(NotificationSchema)
    delay = me.IntegerField(
        min_value=0,
        verbose_name='How long (in milliseconds) to delay the execution before scheduling.'
    )

    class Meta:
        indexes = [
            pymongo.IndexModel([('-start_timestamp', pymongo.OFF), ('action', pymongo.OFF)]),
            pymongo.IndexModel([('start_timestamp', pymongo.OFF)]),
            pymongo.IndexModel([('end_timestamp', pymongo.OFF)]),
            pymongo.IndexModel([('action', pymongo.OFF)]),
            pymongo.IndexModel([('status', pymongo.OFF)]),
            pymongo.IndexModel([('context.trigger_instance.id', pymongo.OFF)]),
            pymongo.IndexModel([('workflow_execution', pymongo.OFF)]),
            pymongo.IndexModel([('task_execution', pymongo.OFF)]),
        ]

    def mask_secrets(self, value):
        from st2common.util import action_db

        result = copy.deepcopy(value)
        execution_parameters = value['parameters']

        # TODO: This results into two DB looks, we should cache action and runner type object
        # for each liveaction...
        #
        #       ,-'"-.
        # .    f .--. \
        # .\._,\._',' j_
        #  7______""-'__`,
        parameters = action_db.get_action_parameters_specs(action_ref=self.action)

        secret_parameters = get_secret_parameters(parameters=parameters)
        result['parameters'] = mask_secret_parameters(parameters=execution_parameters,
                                                      secret_parameters=secret_parameters)
        return result

    def get_masked_parameters(self):
        """
        Retrieve parameters with the secrets masked.

        :rtype: ``dict``
        """
        serializable_dict = self.to_serializable_dict(mask_secrets=True)
        return serializable_dict['parameters']


# specialized access objects
liveaction_access = MongoDBAccess(LiveActionDB)

MODELS = [LiveActionDB]
