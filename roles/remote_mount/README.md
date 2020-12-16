IBM Spectrum Scale (GPFS) Remote Cluster and Mount Role
======================================

Role Definition
-------------------------------
- Role name: **remote_mount**
- Definition:
  - This role adds support for consumers of the playbook to remote mount a IBM Spectrum Scale filesystem from a Storage cluster. 
    The roles leverage the Spectrum Scale REST API , meaning 5.0.5.2 or later versions of Scale contains the endpoints.

    - **Accessing/Client Cluster** - Is the cluster that remote mounts the FileSystem
    - **Owner/Storage Cluster** - Is the cluster that Owns the FileSystem.


Features
-----------------------------

- Remote Mounts FS with API calls to Clusters Storage and Client
- Remote Mounts FS with API calls to Storage Clusters and CLI to Client/Accessing Cluster
- Cleanup Remote Mount from Client and Storage Server



Prerequisite
----------------------------
- Spectrum Scale GUI should be enabled and configured on Storage Cluster.
- Spectrum Scale GUI user with Administrator Role.
- Spectrum Scale Version 5.0.5.2 or later
- HTTPS/443 Network access from where you run the Ansible playbook.
- If you run with "no_gui" on Client Cluster, then you need right/privilege to run Spectrum Scale Commands. (Root have this)


Variables
----------------------------

The following variables would need to be defined by the user, either as vars to calling the role in collections, or in group_vars/all. The **precheck.yml** will fail the role if minimal attributes are not defined.



- ``scale_remotemount_debug: false`` - (Default to False) **Outputs information after tasks**
- ``scale_remotemount_forceRun: false`` (Default to False) **If scale_remotemount_forceRun is passed in, then the playbook is attempting to run remote_mount role regardless of whether the filesystem is configured** 
- ``scale_remotemount_access_mount_attributes: "rw"``  **Default RW** **Filesystem can be mounted in different access mount: RW or RO**
- ``scale_remotemount_client_gui_username: admin`` **Scale User with Administrator or ContainerOperator role/rights**
- ``scale_remotemount_client_gui_password: passw0rd``
- ``scale_remotemount_client_gui_hostname:`` **IP or Hostname to Client GUI Node**
- ``scale_remotemount_client_filesystem_name: fs1``
- ``scale_remotemount_client_remotemount_path: "/mnt/{{ scale_remotemount_client_filesystem_name }}"``
- ``scale_remotemount_storage_gui_username: "{{ scale_remotemount_client_gui_username }}"``
- ``scale_remotemount_storage_gui_password: "{{ scale_remotemount_client_gui_password }}"``
- ``scale_remotemount_storage_gui_hostname:`` **IP or Hostname to Client GUI Node**
- ``scale_remotemount_storage_filesystem_name: gpfs01``  **Storage Cluster filesystem you want to mount**
- ``scale_remotemount_client_no_gui: False``(Default to False) - **If Accessing/Client Cluster don`t have GUI, it will use CLI against Client Cluster**
- ``scale_remotemount_storage_pub_key_location:`` (Defaults to :"/tmp/storage_cluster_public_key.pub") - **Client Cluster (Access) is downloading the pubkey from Owning cluster and importing it**
- ``scale_remotemount_cleanup_remote_mount: false``  (Default to False) **Unmounts, remove the filesystem, and the connection between Accessing/Client cluster and Owner/Storage Cluster. This only works if both Clusters have GUI/RESTAPI interface**



Example Playbooks
-------------------------------

There is also example playbooks in samples folder. 


**Playbook: Storage Cluster and Client Cluster have GUI**

Normally you will use Localhost, then all RestAPI call will occur over https to Storage and Client Cluster from where you run the playbook 

    - hosts: localhost
      vars:
        - scale_remotemount_client_gui_username: admin
        - scale_remotemount_client_gui_password: Admin@GUI
        - scale_remotemount_client_gui_hostname: 10.10.10.10
        - scale_remotemount_client_filesystem_name: fs1
        - scale_remotemount_client_remotemount_path: "/mnt/{{ scale_remotemount_client_filesystem_name }}"
        - scale_remotemount_storage_gui_username: "{{ scale_remotemount_client_gui_username }}"
        - scale_remotemount_storage_gui_password: "{{ scale_remotemount_client_gui_password }}"
        - scale_remotemount_storage_gui_hostname: 10.10.10.20
        - scale_remotemount_storage_filesystem_name: gpfs01
      roles:
        - remote_mount
    




**Playbook: GUI only on Storage Cluster**

Following example will connect up to the first node on the Client Cluster and run the playbook and do API Call to Storage Cluster. 
So the Client Cluster Node needs access on https/443 to Storage Cluster GUI Node.

    - hosts: scale-client-cluster-node-1
      gather_facts: false
      vars:
        scale_remotemount_client_gui_username: admin
        scale_remotemount_client_gui_password: Admin@GUI
        scale_remotemount_client_filesystem_name: fs1
        scale_remotemount_client_remotemount_path: "/mnt/{{ scale_remotemount_client_filesystem_name }}"
        client_cluster_filesystem_automount: automount
        scale_remotemount_storage_gui_username: "{{ scale_remotemount_client_gui_username }}"
        scale_remotemount_storage_gui_password: "{{ scale_remotemount_client_gui_password }}"
        scale_remotemount_storage_gui_hostname: 10.10.10.20
        scale_remotemount_storage_filesystem_name: gpfs01
        scale_remotemount_client_no_gui: true
       roles:
         - remote_mount