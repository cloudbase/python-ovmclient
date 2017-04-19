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

import time

from ovmclient import base
from ovmclient import connection
from ovmclient import constants
from ovmclient import exception


class Client(object):
    def __init__(self, base_uri, username, password, verify_cert=False):
        self._conn = connection.Connection(
            base_uri, username, password, verify_cert)

    @property
    def vms(self):
        return VmManager(self._conn)

    @property
    def disk_mappings(self):
        return VmDiskMappingManager(self._conn)

    @property
    def jobs(self):
        return JobManager(self._conn)

    @property
    def managers(self):
        return ManagerManager(self._conn)

    @property
    def networks(self):
        return NetworkManager(self._conn)

    @property
    def repositories(self):
        return RepositoryManager(self._conn)

    def repository_virtual_disks(self, repository_id):
        return VirtualDiskManager(self._conn, repository_id)

    @property
    def servers(self):
        return ServerManager(self._conn)

    def server_networks(self, server_id):
        return NetworkManager(self._conn, server_id)

    @property
    def server_pools(self):
        return ServerPoolManager(self._conn)

    @property
    def virtual_disks(self):
        return VirtualDiskManager(self._conn)

    def vm_virtual_nics(self, vm_id):
        return VirtualNicManager(self._conn, vm_id)

    def vm_disk_mappings(self, vm_id):
        return VmDiskMappingManager(self._conn, vm_id)


class JobManager(base.BaseManager):
    def __init__(self, conn):
        super(JobManager, self).__init__(conn, 'Job')

    def get_transcript(self, id):
        return self._get_resource(id, "transcript")

    def abort(self, id):
        return self._action(id, "abort")

    def wait_for_job(self, job, sleep_seconds=.5):
        while not job.get('summaryDone'):
            time.sleep(sleep_seconds)
            job = self.get_by_id(job['id'])

        if job['jobRunState'].upper() == constants.JOB_RUN_STATE_FAILURE:
            raise exception.JobFailureException(job)
        return job


class ManagerManager(base.BaseManager):
    def __init__(self, conn):
        super(ManagerManager, self).__init__(conn, 'Manager')

    def wait_for_manager_state(self,
                               state=constants.MANAGER_RUN_STATE_RUNNING,
                               sleep_seconds=.5):
        managers = self.get_all()
        if not managers:
            raise exception.ObjectNotFoundException('No OVM Manager found')
        manager = managers[0]
        while manager.get(
                'managerRunState') != constants.MANAGER_RUN_STATE_RUNNING:
            time.sleep(sleep_seconds)
            manager = self.get_by_id(['id'])


class NetworkManager(base.BaseManager):
    def __init__(self, conn, server_id=None):
        if server_id:
            rel_path = "Server/%s/Network" % self._get_id_value(server_id)
        else:
            rel_path = 'Network'
        super(NetworkManager, self).__init__(conn, rel_path)


class RepositoryManager(base.BaseManager):
    def __init__(self, conn):
        super(RepositoryManager, self).__init__(conn, 'Repository')


class ServerManager(base.BaseManager):
    def __init__(self, conn):
        super(ServerManager, self).__init__(conn, 'Server')

    def discover(self, server_name, take_ownership_if_unowned=True):
        params = {
            "serverName": server_name,
            "takeOwnershipIfUnowned": take_ownership_if_unowned,
        }
        return self._conn.post("%s/discover" % self._rel_url, None, params)


class ServerPoolManager(base.BaseManager):
    def __init__(self, conn):
        super(ServerPoolManager, self).__init__(conn, 'ServerPool')


class VirtualDiskManager(base.BaseManager):
    def __init__(self, conn, repository_id=None):
        if repository_id:
            rel_path = "Repository/%s/VirtualDisk" % self._get_id_value(
                repository_id)
        else:
            rel_path = 'VirtualDisk'
        super(VirtualDiskManager, self).__init__(conn, rel_path)

    def clone(self, id, clone_target_id,
              clone_type=constants.CLONE_TYPE_NON_SPARSE_COPY):
        params = {
            "cloneType": clone_type,
        }
        return self._action(id, "clone", clone_target_id, params)

    def resize(self, id, size, sparse):
        params = {
            "size": size,
            "sparse": sparse,
        }
        return self._action(id, "resize", params=params)

    def get_empty_cdrom(self):
        return self._conn.get("VirtualDisk/virtualDiskGetEmptyCdrom")


class VirtualNicManager(base.BaseManager):
    def __init__(self, conn, vm_id):
        super(VirtualNicManager, self).__init__(
            conn, "Vm/%s/VirtualNic" % self._get_id_value(vm_id))


class VmManager(base.BaseManager):
    def __init__(self, conn):
        super(VmManager, self).__init__(conn, 'Vm')

    def get_supported_os_types(self):
        return self._conn.get('Vm/SupportedOsTypes')['strings']

    def start(self, id):
        return self._action(id, "start")

    def stop(self, id):
        return self._action(id, "stop")

    def restart(self, id):
        return self._action(id, "restart")

    def kill(self, id):
        return self._action(id, "kill")

    def suspend(self, id):
        return self._action(id, "suspend")

    def resume(self, id):
        return self._action(id, "resume")

    def get_console_url(self, id):
        return self._get_resource(id, "vmConsoleUrl")

    def get_serial_console_url(self, id):
        return self._get_resource(id, "vmSerialConsoleUrl")

    def clone(self, id, server_pool_id,
              repository_id=None, vm_clone_definition_id=None,
              create_template=False):
        params = {
            "serverPoolId": self._get_id_value(server_pool_id),
            "createTemplate": create_template,
        }

        if repository_id:
            params["repositoryId"] = self._get_id_value(repository_id)
        if vm_clone_definition_id:
            params["vmCloneDefinitionId"] = self._get_id_value(
                vm_clone_definition_id)

        return self._action(id, "clone", params=params)


class VmDiskMappingManager(base.BaseManager):
    def __init__(self, conn, vm_id=None):
        if vm_id:
            rel_path = 'Vm/%s/VmDiskMapping' % self._get_id_value(vm_id)
        else:
            rel_path = 'VmDiskMapping'

        super(VmDiskMappingManager, self).__init__(conn, rel_path)
