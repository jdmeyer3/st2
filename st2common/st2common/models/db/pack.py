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

from st2common import fields as db_field_types
from st2common.models.db import MongoDBAccess
from st2common.models.db import stormbase
from st2common.constants.types import ResourceType
from st2common.constants.pack import PACK_VERSION_REGEX
from st2common.constants.pack import ST2_VERSION_REGEX
from st2common.util.secrets import get_secret_parameters
from st2common.util.secrets import mask_secret_parameters

__all__ = [
    'PackDB',
    'ConfigSchemaDB',
    'ConfigDB'
]


class PackDB(stormbase.StormFoundationDB, stormbase.UIDFieldMixin,
             me.MongoModel):
    """
    System entity which represents a pack.
    """

    RESOURCE_TYPE = ResourceType.PACK
    UID_FIELDS = ['ref']

    ref = me.CharField(required=True)
    name = me.CharField(required=True)
    description = me.CharField(required=True)
    keywords = me.ListField(field=me.CharField())
    version = db_field_types.RegexStringField(regex=PACK_VERSION_REGEX, required=True)
    stackstorm_version = db_field_types.RegexStringField(regex=ST2_VERSION_REGEX)
    python_versions = me.ListField(field=me.CharField())
    author = me.CharField(required=True)
    email = me.EmailField()
    contributors = me.ListField(field=me.CharField())
    files = me.ListField(field=me.CharField())
    path = me.CharField(required=False)
    dependencies = me.ListField(field=me.CharField())
    system = me.DictField()

    class Meta:
        indexes = [
            pymongo.IndexModel([('ref', pymongo.OFF)], unique=True),
            pymongo.IndexModel([('name', pymongo.OFF)], unique=True),
        ] + stormbase.UIDFieldMixin.get_indexes()

    def __init__(self, *args, **values):
        super(PackDB, self).__init__(*args, **values)
        self.uid = self.get_uid()


class ConfigSchemaDB(stormbase.StormFoundationDB):
    """
    System entity representing a config schema for a particular pack.
    """

    pack = me.CharField(
        required=True,
        verbose_name='Name of the content pack this schema belongs to.')
    attributes = stormbase.EscapedDynamicField(
        verbose_name='The specification for config schema attributes.')

    class Meta:
        indexes = [
            pymongo.IndexModel([('pack', pymongo.OFF)], unique=True)
        ]
        

class ConfigDB(stormbase.StormFoundationDB):
    """
    System entity representing pack config.
    """
    pack = me.CharField(
        required=True,
        verbose_name='Name of the content pack this config belongs to.')
    values = stormbase.EscapedDynamicField(
        verbose_name='Config values.',
        default={})
    
    class Meta:
        indexes = [
            pymongo.IndexModel([('pack', pymongo.OFF)], unique=True)
        ]

    def mask_secrets(self, value):
        """
        Process the model dictionary and mask secret values.

        :type value: ``dict``
        :param value: Document dictionary.

        :rtype: ``dict``
        """
        result = copy.deepcopy(value)

        config_schema = config_schema_access.get_by_pack(result['pack'])

        secret_parameters = get_secret_parameters(parameters=config_schema.attributes)
        result['values'] = mask_secret_parameters(parameters=result['values'],
                                                  secret_parameters=secret_parameters)

        return result


# specialized access objects
pack_access = MongoDBAccess(PackDB)
config_schema_access = MongoDBAccess(ConfigSchemaDB)
config_access = MongoDBAccess(ConfigDB)

MODELS = [PackDB, ConfigSchemaDB, ConfigDB]
