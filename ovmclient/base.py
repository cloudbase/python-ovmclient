# Copyright (c) 2017 Cloudbase Solutions Srl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ovmclient import exception


class BaseManager(object):
    def __init__(self, conn, rel_url):
        self._conn = conn
        self._rel_url = rel_url

    @staticmethod
    def _get_id_value(obj):
        if isinstance(obj, dict):
            return obj["value"]
        return obj

    def get_all(self):
        return self._conn.get(self._rel_url)

    def get_all_ids(self):
        return self._conn.get('%s/id' % self._rel_url)

    def get_id_by_name(self, name):
        ids = [id for id in self.get_all_ids() if id.get('name') == name]
        if not ids:
            raise exception.ObjectNotFoundException(
                "No object found with name: %s" % name)
        if len(ids) > 1:
            raise exception.TooManyObjectsException(
                "More than one object exists with name: %s" % name)
        return ids[0]

    def _get_id_url(self, id):
        return '%s/%s' % (self._rel_url, self._get_id_value(id))

    def get_by_id(self, id):
        return self._conn.get(self._get_id_url(id))

    def get_by_name(self, name):
        id = self.get_id_by_name(name)
        return self.get_by_id(id['value'])

    def create(self, data, **kwargs):
        return self._conn.post(self._rel_url, data, kwargs)

    def update(self, id, data=None):
        return self._conn.put(self._get_id_url(id), data)

    def delete(self, id):
        return self._conn.delete(self._get_id_url(id))

    def _action(self, id, action_name, data=None, params={}):
        rel_url = "%s/%s" % (self._get_id_url(id), action_name)
        return self._conn.put(rel_url, data, params)

    def _add_child_object(self, id, child_type, child_id):
        return self._action(
            self.self._get_id_value(id), "add%s" % child_type, child_id)

    def _remove_child_object(self, id, child_type, child_id):
        return self._action(
            self._get_id_value(id), "remove%s" % child_type, child_id)
