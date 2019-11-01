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

from st2common.constants.rule_enforcement import RULE_ENFORCEMENT_STATUS_FAILED
from st2common.constants.rule_enforcement import RULE_ENFORCEMENT_STATUS_SUCCEEDED
from st2common.fields import ComplexDateTimeField
from st2common.models.db import MongoDBAccess
from st2common.models.db import stormbase
from st2common.util import date as date_utils

__all__ = [
    'RuleReferenceSpecDB',
    'RuleEnforcementDB'
]


class RuleReferenceSpecDB(me.EmbeddedMongoModel):
    ref = me.CharField(verbose_name='Reference to rule.',
                       required=True)
    id = me.CharField(required=False,
                      verbose_name='Rule ID.')
    uid = me.CharField(required=True,
                       verbose_name='Rule UID.')

    class Meta:
        indexes = [
            pymongo.IndexModel([('ref', pymongo.OFF)], unique=False)
        ]

    def __str__(self):
        result = []
        result.append('RuleReferenceSpecDB@')
        result.append(str(id(self)))
        result.append('(ref="%s", ' % self.ref)
        result.append('id="%s", ' % self.id)
        result.append('uid="%s")' % self.uid)

        return ''.join(result)


class RuleEnforcementDB(stormbase.StormFoundationDB, stormbase.TagsMixin):
    UID_FIELDS = ['id']

    trigger_instance_id = me.CharField(required=True)
    execution_id = me.CharField(required=False)
    failure_reason = me.CharField(required=False)
    rule = me.EmbeddedDocumentField(RuleReferenceSpecDB, required=True)
    enforced_at = ComplexDateTimeField(
        default=date_utils.get_datetime_utc_now,
        verbose_name='The timestamp when the rule enforcement happened.')
    status = me.CharField(
        required=True,
        default=RULE_ENFORCEMENT_STATUS_SUCCEEDED,
        verbose_name='Rule enforcement status.')

    class Meta:
        indexes = [
            pymongo.IndexModel([('trigger_instance_id', pymongo.OFF)]),
            pymongo.IndexModel([('execution_id', pymongo.OFF)]),
            pymongo.IndexModel([('rule.id', pymongo.OFF)]),
            pymongo.IndexModel([('rule.ref', pymongo.OFF)]),
            pymongo.IndexModel([('enforced_at', pymongo.OFF)]),
            pymongo.IndexModel([('-enforced_at', pymongo.OFF)]),
            pymongo.IndexModel([('-enforced_at', pymongo.OFF), ('rule.ref', pymongo.OFF)]),
            pymongo.IndexModel([('status', pymongo.OFF)])
        ] + stormbase.TagsMixin.get_indexes()

    def __init__(self, *args, **values):
        super(RuleEnforcementDB, self).__init__(*args, **values)

        # Set status to succeeded for old / existing RuleEnforcementDB which predate status field
        status = getattr(self, 'status', None)
        failure_reason = getattr(self, 'failure_reason', None)

        if status in [None, RULE_ENFORCEMENT_STATUS_SUCCEEDED] and failure_reason:
            self.status = RULE_ENFORCEMENT_STATUS_FAILED

    # NOTE: Note the following method is exposed so loggers in rbac resolvers can log objects
    # with a consistent get_uid interface.
    def get_uid(self):
        # TODO Construct uid from non id field:
        uid = [self.RESOURCE_TYPE, str(self.id)]
        return ':'.join(uid)


rule_enforcement_access = MongoDBAccess(RuleEnforcementDB)

MODELS = [RuleEnforcementDB]
