IBM Spectrum Scale (GPFS) Remote Cluster and Mount Role
======================================

Role Definition
-------------------------------
- Role name: **remotemount_configure**
- Definition:
  - This role adds support for consumers of the playbook to remote mount a IBM Spectrum Scale filesystem from a Storage cluster. 
    The roles leverage the Spectrum Scale REST API , meaning 5.0.5.2 or later versions of Scale contains the endpoints.

    - **Accessing/Client Cluster** - Is the cluster that remote mounts the FileSystem
    - **Owner/Storage Cluster** - Is the cluster that Owns the FileSystem.


Features
-----------------------------

- Remote Mounts FS with API calls to Clusters Storage and Client
- Remote Mounts FS with API calls to Storage Clusters and CLI to Client/Accessing Cluster
- Cleanup Remote Mount from Client and Storage Servers
- Remote Mount several filesystems in same ansible play.
- Check's and add Remote Filesystems if not already there. 
- Check if remote cluster is already defined. 


Limitation
-----------------------------
- Can't remove singel filesystems without removing the remote cluster connection
- Can't update filesystems Variables. like mountpoint, mount_attributes.

Prerequisite
----------------------------
- Spectrum Scale GUI should be enabled and configured on Storage Cluster.
- Spectrum Scale GUI user with Administrator Role. (**Scale User with Administrator or ContainerOperator role/rights**)
-   Only users with role 'Administrator' or 'CNSS Operator' have permission to for this REST endpoint. 
    - Read also the documentation of CLI command 'mmremotecluster delete'.
    - ``/usr/lpp/mmfs/gui/cli/mkuser remotemount -g ContainerOperator -p password01``
- Spectrum Scale Version 5.0.5.2 or later
- Firewall opening between all Storage Cluster and Client Cluster. (Se list below)   
- HTTPS/443 Network access from where you run the Ansible playbook.
  - If you run with "no_gui" on Client Cluster, Then you need right/privilege to run Spectrum Scale Commands. (Root have this)


Variables
----------------------------

The following variables would need to be defined by the user, either as vars to calling the role in collections, or in group_vars/all. The **precheck.yml** will fail the role if minimal attributes are not defined.

- ``scale_remotemount_client_gui_username: admin`` **Scale User with Administrator or ContainerOperator role/rights**
- ``scale_remotemount_client_gui_password: passw0rd``
- ``scale_remotemount_client_gui_hostname:`` **IP or Hostname to Client GUI Node**
- ``scale_remotemount_storage_gui_username: admin`` **Scale User with Administrator or ContainerOperator role/rights**
- ``scale_remotemount_storage_gui_password: "passw0rd``
- ``scale_remotemount_storage_gui_hostname:`` **IP or Hostname to Client GUI Node**

**Filesystems** variables need to be a list, see example below 
- ``scale_remotemount_client_filesystem_name: fs1``
- ``scale_remotemount_client_remotemount_path: "/gpfs/fs1"``
- ``scale_remotemount_storage_filesystem_name: gpfs01``  **Storage Cluster filesystem you want to mount**
- ``scale_remotemount_access_mount_attributes: "rw"``  **Default RW** **Filesystem can be mounted in different access mount: RW or RO**
- ``scale_remotemount_client_mount_fs: yes`` (Default to yes) ** Indicates when the file system is to be mounted:** options are yes, no, automount (When the file system is first accessed.) 
- ``scale_remotemount_client_mount_priority: 0`` (Default to 0 ) **File systems with higher Priority numbers are mounted after file systems with lower numbers. File systems that do not have mount priorities are mounted last. A value of zero indicates no priority.**


- ``scale_remotemount_client_no_gui: False``(Default to False) - **If Accessing/Client Cluster don`t have GUI, it will use CLI against Client Cluster**
- ``scale_remotemount_storage_pub_key_location:`` (Defaults to :"/tmp/storage_cluster_public_key.pub") - **Client Cluster (Access) is downloading the pubkey from Owning cluster and importing it**
- ``scale_remotemount_cleanup_remote_mount: false``  (Default to False) **Unmounts, remove the filesystem, and the connection between Accessing/Client cluster and Owner/Storage Cluster. This now works on clusters that not have GUI/RESTAPI interface on Client Cluster**
- ``scale_remotemount_debug: false`` - (Default to False) **Outputs information after tasks**
- ``scale_remotemount_forceRun: false`` (Default to False) **If scale_remotemount_forceRun is passed in, then the playbook is attempting to run remote_mount role regardless of whether the filesystem is configured**

- ``scale_remotemount_storage_pub_key_location:`` (Defaults to :"/tmp/storage_cluster_public_key.pub") - **Client Cluster (Access) pubkey that is changed from json to right format and then used when creating connection**
- ``scale_remotemount_storage_pub_key_location_json:`` (Defaults to : "/tmp/storage_cluster_public_key_json.pub") **Client Cluster (Access) is downloading the pubkey as JSON from Owning cluster**
- ``scale_remotemount_storage_pub_key_delete:`` (Default to: true) **delete both temporary pubkey after the connection have been established**

-  ``scale_remotemount_storage_adminnodename: true `` (Default to: false) **Spectrum Scale uses the Deamon node name and the IP Attach to connect and run cluster traffic on. In most cases the admin network and deamon network is the same. In case you have different AdminNode address and DeamonNode address and for some reason you want to use admin network, then you can set the variable to true**


- ``scale_remotemount_gpfsdemon_check: true ``(Default to: true) **Checks that GPFS deamon is started on GUI node, it will check the first server in NodeClass GUI_MGMT_SERVERS, this is the same flag to check when trying to mount up filesystems on all nodes. Check can be disabled with changing the flag to false.**

- ``scale_remotemount_client_mount_on_nodes: all``(Default to: all) **Default it will try to mount the filesystem on all client cluster (accessing) nodes, here you can replace this with a comma separated list of servers. example: scale1-test,scale2-test**


- ``scale_remotemount_storage_contactnodes_filter: '?fields=roles.gatewayNode%2Cnetwork.daemonNodeName&filter=roles.gatewayNode%3Dfalse' `` 
  - When adding the storage Cluster as a remotecluster in client cluster we need to specify what nodes should be used as contact node, and in normal cases **all** nodes would be fine. In case we have AFM Gateway nodes, or Cloud nodes TFCT, we want to use the RESTAPI filter to remove those nodes, so they are not used.

  - **Example**: 
     - Default is only list all servers that have (AFM) gatewayNode=false. ``scale_remotemount_storage_contactnodes_filter: '?fields=roles.gatewayNode%2Cnetwork.daemonNodeName&filter=roles.gatewayNode%3Dfalse'``
     - No AFM and CloudGateway: ``?fields=roles.gatewayNode%2Cnetwork.daemonNodeName%2Croles.cloudGatewayNode&filter=roles.gatewayNode%3Dfalse%2Croles.cloudGatewayNode%3Dfalse``
     - To create your own filter, go to the API Explorer on Spectrum Scale GUI. https://IP-TO-GUI-NODE/ibm/api/explorer/#!/Spectrum_Scale_REST_API_v2/nodesGetv2
      
    Roles in version 5.1.1.3
        
    ```json
      "roles": {
         "cesNode": false,
         "cloudGatewayNode": false,
         "cnfsNode": false,
         "designation": "quorum",
         "gatewayNode": false,
         "managerNode": false,
         "otherNodeRoles": "perfmonNode",
         "quorumNode": true,
         "snmpNode": false
    ```

Example Playbook's
-------------------------------

There is also example playbook's in samples folder. 

### Playbook: Storage Cluster and Client Cluster have GUI

You can use localhost, then all RestAPI call will occur over https to Storage and Client Cluster locally from where you run the Ansible playbook 
```yaml
    - hosts: localhost
      vars:
         scale_remotemount_client_gui_username: admin
         scale_remotemount_client_gui_password: Admin@GUI
         scale_remotemount_client_gui_hostname: 10.10.10.10
         scale_remotemount_storage_gui_username: admin
         scale_remotemount_storage_gui_password: Admin@GUI
         scale_remotemount_storage_gui_hostname: 10.10.10.20
         scale_remotemount_filesystem_name:
          - { scale_remotemount_client_filesystem_name: "fs2", scale_remotemount_client_remotemount_path: "/gpfs/fs2", scale_remotemount_storage_filesystem_name: "gpfs01", } # Minimum variables
          - { scale_remotemount_client_filesystem_name: "fs3", scale_remotemount_client_remotemount_path: "/gpfs/fs3", scale_remotemount_storage_filesystem_name: "gpfs02", scale_remotemount_client_mount_priority: '2', scale_remotemount_access_mount_attributes: "rw", scale_remotemount_client_mount_fs: "yes"  }
      roles:
        - remote_mount
```

``ansible-playbook -i hosts remotmount.yml``

-----------

### Playbook: GUI only on Storage Cluster

Following example will connect up to the first host in your ansible host file, and then run the playbook and do API Call to Storage Cluster. 
So in this case the Client Cluster node needs access on https/443 to Storage Cluster GUI Node.
```yaml
    - hosts: scale-client-cluster-node-1
      gather_facts: false
      vars:
        scale_remotemount_storage_gui_username: admin
        scale_remotemount_storage_gui_password: Admin@GUI
        scale_remotemount_storage_gui_hostname: 10.10.10.20
        scale_remotemount_client_no_gui: true
        scale_remotemount_filesystem_name:
          - { scale_remotemount_client_filesystem_name: "fs2", scale_remotemount_client_remotemount_path: "/gpfs/fs2", scale_remotemount_storage_filesystem_name: "gpfs01", } # Minimum variables
          - { scale_remotemount_client_filesystem_name: "fs3", scale_remotemount_client_remotemount_path: "/gpfs/fs3", scale_remotemount_storage_filesystem_name: "gpfs02", scale_remotemount_client_mount_priority: '2', scale_remotemount_access_mount_attributes: "rw", scale_remotemount_client_mount_fs: "yes"  }
       roles:
         - remote_mount
```
Firewall recommendations for communication among cluster's
--------

```
Source : Remote Cluster (Access)
destination:  Storage cluster (Owner)
ports: 1191, 443, ephemeral port range, (SSH is god to have, but should not be needed)
```
```
Source: Storage cluster (Owner)
Destination: Remote Cluster (Access)
ports: 443 , 1191, ephemeral port range
```

If the installation toolkit is used, the ephemeral port range is automatically set to 60000-61000. Firewall ports must be opened according to the defined ephemeral port range. 
If commands such as mmlsmgr and mmcrfs hang, it indicates that the ephemeral port range is improperly configured.


to set the tscCmdPortRange configuration variable:
``mmchconfig tscCmdPortRange=LowNumber-HighNumber ``



Troubleshooting
------------------------

- If you get **401 - Unauthorized** -  Check that your user is working with a Curl, and that is have the correct Role. 

  ``-k`` will use insecure.
  
  ``curl -k -u admin:password -X GET --header 'accept:application/json' 'https://10.33.3.xx:443/scalemgmt/v2/nodes/all/health/states?fields=entityName,state&filter=component=NODE'``


-  Check that the user on GUI Nodes are active
  
   ```console
    [root@scale-dev-01 ~]# /usr/lpp/mmfs/gui/cli/lsuser
    Name                  Long name Password status Group names                 Failed login attempts Target Feedback Date
    admin                           active          Administrator,SecurityAdmin 0                     15.01.2021 17:32:05.000   
    remotemount                     active          ContainerOperator           0                     
   ```


- Problems Mounting filesystems, first start with checking the mmfs.log 

  ```console 
  tail  /var/adm/ras/mmfs.log.latest
  2021-06-08_14:42:50.085+0200: Failed to open fs1.
  2021-06-08_14:42:50.085+0200: Incompatible file system format.
  2021-06-08_14:42:50.085+0200: [E] Failed to open fs1.
  2021-06-08_14:42:50.085+0200: [W] Command: err 236: mount fs1
  2021-06-08_14:42:50.086+0200: [N] The file system format version of fs1 is not supported on this node. The most recent supported version is 23.00 (5.0.5.0).
  ```
  
  - Then check the Scale Version on both Clusters. 
  
  ```console
  [root@scale-test1 ~]# mmdiag --version
  
  === mmdiag: version ===
  Current GPFS build: "5.0.5.2 ".
  Built on Aug 17 2020 at 16:45:12
  Running 4 hours 54 minutes 18 secs, pid 2941
  ```
  
  - If the Version is supported, then check the mmfs.log.latest on  Storage Cluster, and in this case the SSH key has been changed, mmauth genkey
  - The Cleanup or force to try to mount up again the filesystem with new key, this will most likely cause downtime if not allready having issues. 

   ```console
  tail  /var/adm/ras/mmfs.log.latest
  2021-06-10_07:48:14.371+0000: [E] The key used by the contact node named 10.33.3.146 scale-test2 <c0n5> has changed.  Contact the administrator to obtain the new key and register it using "mmauth update".
  2021-06-10_07:48:14.372+0000: [E] Killing connection from 10.33.3.146, err 726
  2021-06-10_07:48:14.372+0000: Operation not permitted
  ```