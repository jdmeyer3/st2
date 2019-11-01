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
import mongoengine

from st2common.constants.keyvalue import FULL_SYSTEM_SCOPE
from st2common.constants.types import ResourceType
from st2common.models.db import MongoDBAccess
from st2common.models.db import stormbase

__all__ = [
    'KeyValuePairDB'
]


class KeyValuePairDB(stormbase.StormBaseDB, stormbase.UIDFieldMixin):
    """
    Attribute:
        name: Name of the key.
        value: Arbitrary value to be stored.
    """

    RESOURCE_TYPE = ResourceType.KEY_VALUE_PAIR
    UID_FIELDS = ['scope', 'name']

    scope = me.CharField(default=FULL_SYSTEM_SCOPE)
    name = me.CharField(required=True)
    value = me.CharField()
    secret = me.BooleanField(default=False)
    expire_timestamp = me.DateTimeField()

    class Meta:
        indexes = [
            pymongo.IndexModel([('scope', pymongo.OFF), ('name', pymongo.OFF)], unique=True),
            pymongo.IndexModel([('scope', pymongo.OFF)], unique=True),
            pymongo.IndexModel([('name', pymongo.OFF)]),
            pymongo.IndexModel([('expire_timestamp', pymongo.OFF)], expireAfterSeconds=0)
        ]

    def __init__(self, *args, **values):
        super(KeyValuePairDB, self).__init__(*args, **values)
        self.uid = self.get_uid()


# specialized access objects
keyvaluepair_access = MongoDBAccess(KeyValuePairDB)

MODELS = [KeyValuePairDB]
