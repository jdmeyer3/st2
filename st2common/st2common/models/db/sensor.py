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

from st2common.models.db import MongoDBAccess
from st2common.models.db import stormbase
from st2common.constants.types import ResourceType

__all__ = [
    'SensorTypeDB'
]


class SensorTypeDB(stormbase.StormBaseDB, stormbase.ContentPackResourceMixin,
                   stormbase.UIDFieldMixin):
    """
    Description of a specific type of a sensor (think of it as a sensor
    template).

    Attribute:
        pack - Name of the content pack this sensor belongs to.
        artifact_uri - URI to the artifact file.
        entry_point - Full path to the sensor entry point (e.g. module.foo.ClassSensor).
        trigger_type - A list of references to the TriggerTypeDB objects exposed by this sensor.
        poll_interval - Poll interval for this sensor.
    """

    RESOURCE_TYPE = ResourceType.SENSOR_TYPE
    UID_FIELDS = ['pack', 'name']

    name = me.CharField(required=True)
    ref = me.CharField(required=True)
    pack = me.CharField(required=True)
    artifact_uri = me.CharField()
    entry_point = me.CharField()
    trigger_types = me.ListField(field=me.CharField())
    poll_interval = me.IntegerField()
    enabled = me.BooleanField(default=True,
                              verbose_name=u'Flag indicating whether the sensor is enabled.')

    class Meta:
        indexes = [
            pymongo.IndexModel([('pack', pymongo.OFF), ('name', pymongo.OFF)], unique=True),
            pymongo.IndexModel([('name', pymongo.OFF)]),
            pymongo.IndexModel([('enabled', pymongo.OFF)]),
            pymongo.IndexModel([('trigger_types', pymongo.OFF)]),
        ] + (stormbase.ContentPackResourceMixin.get_indexes() +
             stormbase.UIDFieldMixin.get_indexes())

    def __init__(self, *args, **values):
        super(SensorTypeDB, self).__init__(*args, **values)
        self.ref = self.get_reference().ref
        self.uid = self.get_uid()


sensor_type_access = MongoDBAccess(SensorTypeDB)

MODELS = [SensorTypeDB]
