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

import hashlib
import json

import pymodm as me
import pymongo

from st2common.constants.types import ResourceType
from st2common.models.db import MongoDBAccess
from st2common.models.db import stormbase

__all__ = [
    'TriggerTypeDB',
    'TriggerDB',
    'TriggerInstanceDB',
]


class TriggerTypeDB(stormbase.StormBaseDB,
                    stormbase.ContentPackResourceMixin,
                    stormbase.UIDFieldMixin,
                    stormbase.TagsMixin):
    """Description of a specific kind/type of a trigger. The
       (pack, name) tuple is expected uniquely identify a trigger in
       the namespace of all triggers provided by a specific trigger_source.
    Attribute:
        name - Trigger type name.
        pack - Name of the content pack this trigger belongs to.
        trigger_source: Source that owns this trigger type.
        payload_info: Meta information of the expected payload.
    """

    RESOURCE_TYPE = ResourceType.TRIGGER_TYPE
    UID_FIELDS = ['pack', 'name']

    ref = me.CharField(required=False)
    name = me.CharField(required=True)
    pack = me.CharField(required=True)
    payload_schema = me.DictField()
    parameters_schema = me.DictField(default={})

    class Meta:
        indexes = [
            pymongo.IndexModel([('pack', pymongo.OFF), ('name', pymongo.OFF)], unique=True)
                  ] + (stormbase.ContentPackResourceMixin.get_indexes() +
                        stormbase.TagsMixin.get_indexes() +
                        stormbase.UIDFieldMixin.get_indexes())

    def __init__(self, *args, **values):
        super(TriggerTypeDB, self).__init__(*args, **values)
        self.ref = self.get_reference().ref
        # pylint: disable=no-member
        self.uid = self.get_uid()


class TriggerDB(stormbase.StormBaseDB, stormbase.ContentPackResourceMixin,
                stormbase.UIDFieldMixin):
    """
    Attribute:
        name - Trigger name.
        pack - Name of the content pack this trigger belongs to.
        type - Reference to the TriggerType object.
        parameters - Trigger parameters.
    """

    RESOURCE_TYPE = ResourceType.TRIGGER
    UID_FIELDS = ['pack', 'name']

    ref = me.CharField(required=False)
    name = me.CharField(required=True)
    pack = me.CharField(required=True)
    type = me.CharField()
    parameters = me.DictField()
    ref_count = me.IntegerField(default=0)

    class Meta:
        indexes = [
            pymongo.IndexModel([('pack', pymongo.OFF), ('name', pymongo.OFF)], unique=True),
            pymongo.IndexModel([('name', pymongo.OFF)]),
            pymongo.IndexModel([('type', pymongo.OFF)]),
            pymongo.IndexModel([('parameters', pymongo.OFF)]),
        ] + stormbase.UIDFieldMixin.get_indexes()

    def __init__(self, *args, **values):
        super(TriggerDB, self).__init__(*args, **values)
        self.ref = self.get_reference().ref
        self.uid = self.get_uid()

    def get_uid(self):
        # Note: Trigger is uniquely identified using name + pack + parameters attributes
        # pylint: disable=no-member
        uid = super(TriggerDB, self).get_uid()

        # Note: We sort the resulting JSON object so that the same dictionary always results
        # in the same hash
        parameters = getattr(self, 'parameters', {})
        parameters = json.dumps(parameters, sort_keys=True)
        parameters = hashlib.md5(parameters.encode()).hexdigest()

        uid = uid + self.UID_SEPARATOR + parameters
        return uid

    def has_valid_uid(self):
        parts = self.get_uid_parts()
        # Note: We add 1 for parameters field which is not part of self.UID_FIELDS
        return len(parts) == len(self.UID_FIELDS) + 1 + 1


class TriggerInstanceDB(stormbase.StormFoundationDB):
    """An instance or occurrence of a type of Trigger.
    Attribute:
        trigger: Reference to the Trigger object.
        payload (dict): payload specific to the occurrence.
        occurrence_time (datetime): time of occurrence of the trigger.
    """
    trigger = me.CharField()
    payload = stormbase.EscapedDictField()
    occurrence_time = me.DateTimeField()
    status = me.CharField(
        required=True,
        verbose_name='Processing status of TriggerInstance.')

    class Meta:
        indexes = [
            pymongo.IndexModel([('occurrence_time', pymongo.OFF)]),
            pymongo.IndexModel([('trigger', pymongo.OFF)]),
            pymongo.IndexModel([('-occurrence_time', pymongo.OFF), ('trigger', pymongo.OFF)]),
            pymongo.IndexModel([('status', pymongo.OFF)]),
        ]


# specialized access objects
triggertype_access = MongoDBAccess(TriggerTypeDB)
trigger_access = MongoDBAccess(TriggerDB)
triggerinstance_access = MongoDBAccess(TriggerInstanceDB)

MODELS = [TriggerTypeDB, TriggerDB, TriggerInstanceDB]
