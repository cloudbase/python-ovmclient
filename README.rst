Python Oracle VM Client
=======================

* Author:         Cloudbase Solutions
* Contact:        info@cloudbasesolutions.com
* Home page:      https://cloudbase.it
* Source:         https://github.com/cloudbase/python-ovmclient
* License:        Apache 2.0

Usage
-----

VM lifecycle
~~~~~~~~~~~~

How to create, modify, start, stop and delete a VM::

    import ovmclient
    from ovmclient import constants

    client = ovmclient.Client(
        'https://host:7002/ovm/core/wsapi/rest', 'admin', 'yadayada')

    # Make sure the manager is running
    client.managers.wait_for_manager_state()

    repo_id = client.repositories.get_id_by_name('repo1')
    pool_id = client.server_pools.get_id_by_name('pool1')
    network_id = client.networks.get_id_by_name('management')

    # Create a virtual disk
    disk_data = {
        'diskType': constants.DISK_TYPE_VIRTUAL_DISK,
        'size': 1024 * 1024 * 1024,
        'shareable': False,
        'name': 'dummy.img',
    }

    job = client.jobs.wait_for_job(
        client.repository_virtual_disks(repo_id).create(disk_data, sparse='true'))
    disk_id = job['resultId']

    # Create a VM
    vm_data = {
        'name': 'vm1',
        'description': 'Blah',
        'vmDomainType': constants.VM_DOMAIN_TYPE_XEN_HVM_PV_DRIVERS,
        'repositoryId': repo_id,
        'serverPoolId': pool_id,
        'cpuCount': 4,
        'cpuCountLimit': 4,
        'hugePagesEnabled': False,
        'memory': 1024,
        'memoryLimit': 1024,
        'osType': 'Oracle Linux 7',
    }

    job = client.jobs.wait_for_job(client.vms.create(vm_data))
    vm_id = job['resultId']

    # Map the virtual disk
    vm_disk_mapping_data = {
        'virtualDiskId': disk_id,
        'diskWriteMode': constants.DISK_WRITE_MODE_READ_WRITE,
        'emulatedBlockDevice': False,
        'storageElementId': None,
        'diskTarget': 0,
    }

    job = client.jobs.wait_for_job(
        client.vm_disk_mappings(vm_id).create(vm_disk_mapping_data))

    # Add a vnic
    vnic_data = {
        'networkId': network_id,
    }

    client.jobs.wait_for_job(client.vm_virtual_nics(vm_id).create(vnic_data))

    # Retrieve the VM
    vm = client.vms.get_by_id(vm_id)

    # Update the VM, e.g. setting a new name
    vm['name'] = 'vm2'
    client.jobs.wait_for_job(client.vms.update(vm_id, vm))

    # Start the VM
    client.jobs.wait_for_job(client.vms.start(vm_id))

    # Kill the VM
    client.jobs.wait_for_job(client.vms.kill(vm_id))

    # Delete the VM
    client.jobs.wait_for_job(client.vms.delete(vm_id))

    # Delete the virtual disk
    client.jobs.wait_for_job(
        client.repository_virtual_disks(repo_id).delete(disk_id))


Cloning a VM
~~~~~~~~~~~~

How to clone a VM or a VM template::

    import ovmclient

    client = ovmclient.Client(
        'https://host:7002/ovm/core/wsapi/rest', 'admin', 'yadayada')

    # Make sure the manager is running
    client.managers.wait_for_manager_state()

    pool_id = client.server_pools.get_id_by_name('pool1')

    # Get an existing VM or a VM template
    vm_id = client.vms.get_id_by_name('vm1')

    # Set to True to create a VM template, False for a regular VM
    create_template = True

    # Clone the VM
    job = client.jobs.wait_for_job(
        client.vms.clone(vm_id, pool_id, create_template=create_template))
    new_vm_id = job['resultId']

    # Rename the VM template
    data = client.vms.get_by_id(new_vm_id)
    data["name"] = 'new_name'
    client.jobs.wait_for_job(client.vms.update(new_vm_id, data))

    # Delete the VM template
    client.jobs.wait_for_job(client.vms.delete(new_vm_id))


Discovering servers
~~~~~~~~~~~~~~~~~~~

How to discover and take ownership of an unowned Oracle VM host::

    import ovmclient

    client = ovmclient.Client(
        'https://host:7002/ovm/core/wsapi/rest', 'admin', 'yadayada')

    # Make sure the manager is running
    client.managers.wait_for_manager_state()

    # Discover a new host and take ownership
    client.servers.discover('newovmhost')
