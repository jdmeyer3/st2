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


__all__ = [
    'RoleDB',
    'UserRoleAssignmentDB',
    'PermissionGrantDB',
    'GroupToRoleMappingDB',

    'role_access',
    'user_role_assignment_access',
    'permission_grant_access'
]


class RoleDB(stormbase.StormFoundationDB):
    """
    An entity representing a role which can be assigned to the user.

    Attribute:
        name: Role name. Also servers as a primary key.
        description: Role description (optional).
        system: Flag indicating if this is system role which can't be manipulated.
        permission_grants: A list of IDs to the permission grant which apply to this
        role.
    """
    name = me.CharField(required=True)
    description = me.CharField()
    system = me.BooleanField(default=False)
    permission_grants = me.ListField(field=me.CharField())

    class Meta:
        indexes = [
            pymongo.IndexModel([('name', pymongo.OFF)], unique=True),
            pymongo.IndexModel([('system', pymongo.OFF)])
        ]


class UserRoleAssignmentDB(stormbase.StormFoundationDB):
    """
    An entity which represents a user role assingnment.

    Attribute:
        user: A reference to the user name to which the role is assigned.
        role: A reference to the role name which is assigned to the user.
        source: Source where this assignment comes from. Path to a file for local assignments
                and "API" for API assignments.
        description: Optional assigment description.
    """
    user = me.CharField(required=True)
    role = me.CharField(required=True)
    source = me.CharField(required=True)
    description = me.CharField()
    # True if this is assigned created on authentication based on the remote groups provided by
    # the auth backends.
    # Remote assignments are special in a way that they are not manipulated with when running
    # st2-apply-rbac-auth-definitions tool.
    is_remote = me.BooleanField(default=False)

    class Meta:
        indexes = [
            pymongo.IndexModel([('user', pymongo.OFF)]),
            pymongo.IndexModel([('role', pymongo.OFF)]),
            pymongo.IndexModel([('source', pymongo.OFF)]),
            pymongo.IndexModel([('is_remote', pymongo.OFF)]),
            pymongo.IndexModel([('user', pymongo.OFF), ('role', pymongo.OFF)], unique=True),
            pymongo.IndexModel([('user', pymongo.OFF), ('source', pymongo.OFF)], unique=True),
        ]


class PermissionGrantDB(stormbase.StormFoundationDB):
    """
    An entity which represents permission assignment.

    Attribute:
        resource_uid: UID of a target resource to which this permission applies to.
        resource_type: Type of a resource this permission applies to. This attribute is here for
        convenience and to allow for more efficient queries.
        permission_types: A list of permission type granted to that resources.
    """
    resource_uid = me.CharField(required=False)
    resource_type = me.CharField(required=False)
    permission_types = me.ListField(field=me.CharField())

    class Meta:
        indexes = [
            pymongo.IndexModel([('resource_uid', pymongo.OFF)])
        ]


class GroupToRoleMappingDB(stormbase.StormFoundationDB):
    """
    An entity which represents mapping from a remote auth backend group to StackStorm roles.

    Attribute:
        group: Name of the remote auth backend group.
        roles: A reference to the local RBAC role names.
        source: Source where this assignment comes from. Path to a file for local assignments
                and "API" for API assignments.
        description: Optional description for this mapping.
    """
    group = me.CharField(required=True)
    roles = me.ListField(field=me.CharField())
    source = me.CharField()
    description = me.CharField()
    enabled = me.BooleanField(required=True, default=True,
                              verbose_name='A flag indicating whether the mapping is enabled.')

    class Meta:
        indexes = [
            pymongo.IndexModel([('group', pymongo.OFF)], unique=True)
        ]

# Specialized access objects
role_access = MongoDBAccess(RoleDB)
user_role_assignment_access = MongoDBAccess(UserRoleAssignmentDB)
permission_grant_access = MongoDBAccess(PermissionGrantDB)
group_to_role_mapping_access = MongoDBAccess(GroupToRoleMappingDB)

MODELS = [RoleDB, UserRoleAssignmentDB, PermissionGrantDB, GroupToRoleMappingDB]
