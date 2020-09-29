IBM Spectrum Scale (GPFS) Deployment using Ansible Roles
========================================================

Ansible project with multiple roles for installing and configuring IBM Spectrum Scale (GPFS).

**Table of Contents**

- [Features](#features)
- [Supported Versions](#supported-versions)
- [Prerequisites](#prerequisites)
- [Installation Instructions](#installation-instructions)
- [Optional Role Variables](#optional-role-variables)
- [Available Roles](#available-roles)
- [Cluster Membership](#cluster-membership)
- [Limitations](#limitations)
- [Troubleshooting](#troubleshooting)
- [Reporting Issues and Feedback](#reporting-issues-and-feedback)
- [Contributing Code](#contributing-code)
- [Disclaimer](#disclaimer)
- [Copyright and License](#copyright-and-license)


Features
--------

#### Infrastructure support
- [x] Pre-built infrastructure (using a static inventory file)
- [ ] Dynamic inventory file

#### OS support
- [x] Support for RHEL 7 on x86_64, PPC64 and PPC64LE
- [x] Support for RHEL 8 on x86_64 and PPC64LE
- [x] Support for UBUNTU 20 on x86_64 and PPC64LE
- [x] Support for SLES 15 on x86_64 and PPC64LE

#### Common prerequisites
- [x] Disable SELinux (`scale_prepare_disable_selinux: true`), by default false
- [x] Disable firewall (`scale_prepare_disable_firewall: true`), by default true.
- [ ] Disable firewall ports
- [ ] Install and start NTP
- [ ] Create /etc/hosts mappings
- [ ] Open firewall ports
- [x] Generate SSH key
- [x] User must set up base OS repositories

#### Core Spectrum Scale prerequisites
- [x] Install yum-utils package
- [x] Install gcc-c++, kernel-devel, make
- [x] Install elfutils,elfutils-devel (RHEL8 specific)

#### Core Spectrum Scale Cluster supported features
- [x] Install core Spectrum Scale packages on Linux nodes
- [x] Install Spectrum Scale license packages on Linux nodes
- [x] Compile or install pre-compiled Linux kernel extension (mmbuildgpl)
- [x] Configure client and server license
- [x] Assign default quorum (maximum 7 quorum nodes) if user has not defined in the inventory
- [x] Assign default manager nodes(all nodes will act as manager node) if user has not defined in the inventory
- [x] Create new cluster (mmcrcluster -N /var/tmp/NodeFile -C {{ scale_cluster_clustername }})
- [x] Create cluster with profiles
- [x] Add new node into existing cluster
- [x] Configure node classes
- [x] Define configuration parameters based on node classes
- [x] Configure NSDs and file system
- [ ]  Configure NSDs without file system
- [x] Extend NSDs and file system
- [x] Add disks to existing file systems

#### Spectrum Scale GUI Cluster supported features
- [x] Install Spectrum Scale GUI packages on GUI designated nodes
- [x] maximum 3 GUI nodes to be configured
- [x] Install performance monitoring sensor packages on all Linux nodes
- [x] Install performance monitoring packages on all GUI designated nodes
- [x] Configure performance monitoring and collectors
- [ ] Configure HA federated mode collectors

#### Spectrum Scale Callhome Cluster supported features
- [x] Install Spectrum Scale callhome packages on all cluster nodes
- [x] Configure callhome

#### Spectrum Scale CES (SMB and NFS) Protocol supported features (5.0.5.2)
- [x] Install Spectrum Scale SMB or NFS on selected cluster nodes
- [x] CES IPV4 or IPV6 support
- [x] CES interface mode support 
- 

Supported Versions
------------------

The following Ansible versions are supported:

- 2.7 and above

The following IBM Spectrum Scale versions are supported:

- 5.0.4.0
- 5.0.4.1
- 5.0.4.2
- 5.0.5.X
- 5.0.5.2 For CES (SMB and NFS)  

Specific OS Requirements.

- For CES (SMB/NFS) on SLES15, Python3 is required.

Prerequisites
-------------

Users need to have a basic understanding of the [Ansible concepts](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html) for being able to follow these instructions. Refer to the [Ansible User Guide](https://docs.ansible.com/ansible/latest/user_guide/index.html) if this is new to you.

- **Install Ansible on any machine** ([control node](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#control-node))

  ```shell
  $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  $ python get-pip.py --user
  $ pip install --user ansible
  ```

  Refer to the [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/index.html) for detailled installation instructions.

- **Download Spectrum Scale packages**

  1. A Developer Edition Free Trial is available at this site: https://www.ibm.com/account/reg/us-en/signup?formid=urx-41728

  2. Customers who have previously purchased Spectrum Scale can obtain entitled versions from IBM Fix Central. Visit https://www.ibm.com/support/fixcentral and search for 'IBM Spectrum Scale (Software defined storage)'.

- **Create password-less SSH keys between all Spectrum Scale nodes in the cluster**

  A pre-requisite for installing Spectrum Scale is that password-less SSH must be configured among all nodes in the cluster. Password-less SSH must be configured and verified with [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name), hostname, and IP of every node to every node.

  Example:

  ```shell
  $ ssh-keygen
  $ ssh-copy-id -oStrictHostKeyChecking=no node1.gpfs.net
  $ ssh-copy-id -oStrictHostKeyChecking=no node1
  $ ssh-copy-id -oStrictHostKeyChecking=no
  ```

  Repeat this process for all nodes to themselves and to all other nodes.


Installation Instructions
-------------------------

- **Clone `ibm-spectrum-scale-install-infra` repository to your [Ansible control node](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#control-node)**

  ```shell
  $ git clone https://github.com/IBM/ibm-spectrum-scale-install-infra.git
  ```

- **Change working directory to `ibm-spectrum-scale-install-infra/`**

  ```shell
  $ cd ibm-spectrum-scale-install-infra/
  ```

- **Create Ansible inventory**

  1. Define Spectrum Scale nodes in the [Ansible inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) (e.g. `./hosts`) in the following format

     ```yaml
     # hosts:
     [cluster01]
     scale01  scale_cluster_quorum=true   scale_cluster_manager=true   scale_cluster_gui=false
     scale02  scale_cluster_quorum=true   scale_cluster_manager=true   scale_cluster_gui=false
     scale03  scale_cluster_quorum=true   scale_cluster_manager=false  scale_cluster_gui=false
     scale04  scale_cluster_quorum=false  scale_cluster_manager=false  scale_cluster_gui=false
     scale05  scale_cluster_quorum=false  scale_cluster_manager=false  scale_cluster_gui=false
     ```

     The following [Ansible variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) are defined in the above [inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html):

     - `[cluster01]`: User defined host groups for Spectrum Scale cluster nodes on which
       Spectrum Scale installation will take place.

     - `scale_cluster_quorum`: User defined node designation for Spectrum Scale quorum. It
       can be either true or false.

     - `scale_cluster_manager`: User defined node designation for Spectrum Scale manager. It
       can be either true or false.

     - `scale_cluster_gui`: User defined node designation for Spectrum Scale GUI. It
       can be either true or false.
       
     - `is_protocol_node`: User defined node designation for Spectrum Scale Protocol. It
        can be either true or false.true `scale_protocols:` variable also needs to set in group_vars.

     > **Note:**
     Defining node roles such as `scale_cluster_quorum` and `scale_cluster_manager` is optional. If you do not specify any quorum nodes then the first seven hosts in your inventory are automatically assigned the quorum role.

  2. To create NSDs, file systems and node classes in the cluster you'll need to provide additional information. It is recommended to use [Ansible group variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#assigning-a-variable-to-many-machines-group-variables) (e.g. `group_vars/*`) as follows:

     ```yaml
     # group_vars/all:
     ---
     scale_storage:
       - filesystem: gpfs01
         blockSize: 4M
         defaultMetadataReplicas: 2
         defaultDataReplicas: 2
         numNodes: 16
         automaticMountOption: true
         defaultMountPoint: /mnt/gpfs01
         disks:
           - device: /dev/sdb
             nsd: nsd_1
             servers: scale01
             failureGroup: 10
             usage: metadataOnly
             pool: system
           - device: /dev/sdc
             nsd: nsd_2
             servers: scale01
             failureGroup: 10
             usage: dataOnly
             pool: data
     ```

     Refer to `man mmchfs` and `man mmchnsd` man pages for a description of these storage parameters.

     The `filesystem` parameter is mandatory, `servers`, and the `device` parameter is mandatory for each of the file system's `disks`. All other file system and disk parameters are optional. Hence, a minimal file system configuration would look like this:

     ```yaml
     # group_vars/all:
     ---
     scale_storage:
       - filesystem: gpfs01
         disks:
           - device: /dev/sdb
             servers: scale01
           - device: /dev/sdc
             servers: scale01,scale02
     ```

     > **Important:**
     `scale_storage` *must* be define using [group variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#assigning-a-variable-to-many-machines-group-variables). Do *not* define disk parameters using [host variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#assigning-a-variable-to-one-machine-host-variables) or [inline variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#defining-variables-in-a-playbook) in your playbook. Doing so would apply them to all hosts in the group/play, thus defining the same disk multiple times...

     Furthermore, Spectrum Scale node classes can be defined on a per-node basis by defining the `scale_nodeclass` variable:

     ```yaml
     # host_vars/scale01:
     ---
     scale_nodeclass:
       - classA
       - classB
     ```

     ```yaml
     # host_vars/scale02:
     ---
     scale_nodeclass:
       - classA
       - classC
     ```

     These node classes can optionally be used to define Spectrum Scale configuration parameters. It is suggested to use [group variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#assigning-a-variable-to-many-machines-group-variables) for that purpose:

     ```yaml
     # group_vars/all:
     ---
     scale_config:
       - nodeclass: classA
         params:
           - pagepool: 16G
           - autoload: no
           - ignorePrefetchLUNCount: yes
     ```

     Refer to the `man mmchconfig` man page for a list of available configuration parameters.

     Note that configuration parameters can be defined as variables for *any* host in the play &mdash; the host for which you define the configuration parameters is irrelevant.

  3. To install and configure callhome in the cluster you'll need to provide additional information. It is recommended to use [group variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#assigning-a-variable-to-many-machines-group-variables) as follows:

     ```yaml
     # group_vars/all.yml:
     ---
     scale_callhome_params:
       is_enabled: true
       customer_name: abc
       customer_email: abc@abc.com
       customer_id: 12345
       customer_country: IN
       proxy_ip:
       proxy_port:
       proxy_user:
       proxy_password:
       proxy_location:
       callhome_server: host-vm1
       callhome_group1: [host-vm1,host-vm2,host-vm3,host-vm4]
       callhome_schedule: [daily,weekly]
     ```
     
  4. To Install and configure Protocol Service (SMB and NFS) in the cluster you'll need to provide additional information. It is recommended to use [group variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#assigning-a-variable-to-many-machines-group-variables) as follows:
       
       **IPv4 CES inventory:**
       ```yaml
       # group_vars/all.yml:
       ---
       scale_protocols:
           smb: false
           nfs: false
           export_ip_pool: [192.168.100.100,192.168.100.101]
           filesystem: cesSharedRoot
           mountpoint: /gpfs/cesSharedRoot
       ```
     
       ```yaml
       smb: set True for required protocol
       nfs: set True for required protocol
       export_ip_pool: Comma separated list of ipv6 CES IP
       filesystem: Any file system that is going to act as cesSharedRoot filesystem
       mountpoint: CES shared root file system mount point.
       ```
     
       **IPv6 CES inventory:**
       ```yaml
       # group_vars/all.yml:
       ---
       scale_protocols:
            smb: false
            nfs: false,
            interface: [eth0]
            export_ip_pool: [2002:90b:e006:84:250:56ff:feb9:7787]
            filesystem: cesSharedRoot
            mountpoint: /gpfs/cesSharedRoot
       ```
     
      User have to set `true` for required protocol **smb** and or **nfs**
      
       ```yaml
       interface: Comma separated list of ipv6 interface eg, eth0,eth1
       export_ip_pool: Comma separated list of ipv6 CES IP
       filesystem: Any file system that is going to act as cesSharedRoot filesystem
       mountpoint: CES shared root file system mount point.
       ```       
       
       Minimum Playbook roles to install SMB and NFS.
       
       ```yaml
       roles:         
          - core/precheck  
          - core/node        
          - core/cluster         `
          - nfs/precheck         
          - nfs/node         
          - nfs/cluster
          - smb/precheck 
          - smb/node     
          - smb/cluster
       ````
     
- **Create Ansible playbook**

  The basic [Ansible playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html) (e.g. `./playbook.yml`) looks as follows:

  ```yaml
  # playbook.yml:
  ---
  - hosts: cluster01
    vars:
      - scale_version: 5.0.4.0
      - scale_install_localpkg_path: /path/to/Spectrum_Scale_Standard-5.0.4.0-x86_64-Linux-install
    roles:
      - core/precheck
      - core/node
      - core/cluster
      - gui/precheck
      - gui/node
      - gui/cluster
      - zimon/precheck
      - zimon/node
      - zimon/cluster
      - callhome/precheck
      - callhome/node
      - callhome/cluster
      - callhome/postcheck
  ```   

  The following installation methods are available:

  - Installation from (existing) YUM repository (`scale_install_repository_url`)
  - Installation from remote installation package (`scale_install_remotepkg_path`)
  - Installation from local installation package (`scale_install_localpkg_path`)
  - Installation from single directory package path (`scale_install_directory_pkg_path`)

  > **Note:**
  Defining the variable `scale_version` is optional for `scale_install_localpkg_path` and `scale_install_directory_pkg_path` installation methods. It is mandatory for `scale_install_repository_url` and `scale_install_remotepkg_path` installation methods. Furthermore, you'll need to configure an installation method
  by defining *one* of the following variables:
  - `scale_install_repository_url` (eg: http://infraserv/scale/) - root of the Scale package folders and remember the last slash `/` in the url.
  - `scale_install_remotepkg_path` (accessible on Ansible managed node)
  - `scale_install_localpkg_path` (accessible on Ansible control machine)
  - `scale_install_directory_pkg_path` (eg: /opt/IBM/spectrum_scale_packages)

  > **Important:**
  If you are using the single directory installation method (`scale_install_directory_pkg_path`), you need to keep all required Spectrum Scale RPMs in a single user-provided directory.

  - When using the `scale_install_repository_url` the other Ansible Roles will use the main path. example GUI will add /gpfs_rpms/` to the path and create seperate repo.
  
  
- **Run the playbook to install and configure the Spectrum Scale cluster**

  - Using the `ansible-playbook` command:

    ```shell
    $ ansible-playbook -i hosts playbook.yml
    ```

  - Using the automation script:

    ```shell
    $ ./ansible.sh
    ```   

    > **Note:**
    An advantage of using the automation script is that it will generate log files based on the date and the time in the `/tmp` directory.

- **Playbook execution screen**

  Playbook execution starts here:

  ```shell
  $ ./ansible.sh
  Running #### ansible-playbook -i hosts playbook.yml

  PLAY #### [cluster01]
  **********************************************************************************************************

  TASK #### [Gathering Facts]
  **********************************************************************************************************
  ok: [GPFS-vm1]
  ok: [GPFS-vm2]
  ok: [GPFS-vm3]

  TASK [common : check | Check Spectrum Scale version]               
  *********************************************************************************************************
  ok: [GPFS-vm1] => {
      "changed": false,
      "msg": "All assertions passed"
  }
  ok: [GPFS-vm2] => {
      "changed": false,
      "msg": "All assertions passed"
  }
  ok: [GPFS-vm3] => {
      "changed": false,
      "msg": "All assertions passed"
  }
  ```

  Playbook recap:

  ```shell
  #### PLAY RECAP
  ***************************************************************************************************************
  GPFS-vm1                 : ok=0   changed=65    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  GPFS-vm2                 : ok=0   changed=59    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  GPFS-vm3                 : ok=0   changed=59    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  ```


JSON inventory method
----------------------

 There is also created Ansible playbook sample for deploying IBM Spectrum Scale (GPFS) cluster using json inventory.
 
 **playbook_json.ces.yml** --> **set_json_variables.yml** --> **vars/scale_clusterdefinition.json**
 
- **Ansible Playbook:** 
    - **playbook_json.ces.yml**
         -  Roles Include: Core, zimon, GUI, Protocol (NFS, SMB), callhome and scale_fileauditlogging. 
 
 
- **set_json_variables.yml**

    - The Playbook set variables from `set_json_variables.yml` that is read from `vars/scale_clusterdefinition.json`

- **vars/scale_clusterdefinition.json**
 
   - This file can be adjusted to your environment or created.
   - Example `scale_clusterdefinition.json` is separated into:
   
       - `scale_cluster`: 
       - `node_details`: Variables that set's variables to each node (* like host_vars*)
       - `scale_storage`:
       - `scale_callhome_params`:
       - `scale_protocols`:
       
- Example **scale_clusterdefinition.json**

  ```json
    {
      "scale_cluster": {
            "scale_cluster_name": "gpfs1.local",
            "scale_cluster_profile_name": "gpfsprotocoldefaults"
      },
      "node_details": [
        {
          "fqdn" : host-vm1,
          "is_protocol_node" :false,
          "is_nsd_server" : false,
          "is_quorum_node" : false,
          "is_manager_node" : false,
          "is_gui_server" : false,
          "is_callhome_node" : false,
          "scale_zimon_collector" : false
        },
        {
          "fqdn" : host-vm2,
          "is_protocol_node" : false,
          "is_nsd_server" : false,
          "is_quorum_node" : false,
          "is_manager_node" : false,
          "is_gui_server" : false,
          "is_callhome_node" : false,
          "scale_zimon_collector" : false
        },
        {
          "fqdn" : host-vm3,
          "is_protocol_node" : false,
          "is_nsd_server" : false,
          "is_quorum_node" : false,
          "is_manager_node" : false,
          "is_gui_server" : false,
          "is_callhome_node" : false,
          "scale_zimon_collector" : false
        }
      ],
      "scale_storage":[
        {
          "filesystem": "cesSharedRoot",
          "blockSize": 4M,
          "defaultMetadataReplicas": 1,
          "defaultDataReplicas": 1,
          "automaticMountOption": true,
          "defaultMountPoint": /gpfs/cesSharedRoot,
          "disks": [
           {
            "device": "/dev/sdb",
            "nsd": "nsd1",
            "servers": "host-vm1",
            "usage": dataAndMetadata,
            "pool": system
           }
          ]
        }
      ],
      "scale_callhome_params":{
          "is_enabled": false,
          "customer_name": abc,
          "customer_email": abc@abc.com,
          "customer_id": 12345,
          "customer_country": IN,
          "proxy_ip":,
          "proxy_port":,
          "proxy_user":,
          "proxy_password":,
          "proxy_location":,
          "callhome_server": host-vm1,
          "callhome_group1": [host-vm1,host-vm2,host-vm3],
          "callhome_schedule": [daily,weekly]
      },
      "scale_protocols":{
          "smb": false,
          "nfs": false,
          "export_ip_pool": [192.168.100.100,192.168.100.101],
          "filesystem": cesSharedRoot,
          "mountpoint": /gpfs/cesSharedRoot
      }
    }
  ```
---
- **Scale Protocols**
  - If CES Groups is desired `scale_protocols` example below can be used.
     - For more information about [CES Groups](https://www.ibm.com/support/knowledgecenter/STXKQY_5.0.5/com.ibm.spectrum.scale.v5r05.doc/bl1adm_configcesprotocolservipadd.htm)
  
    ```json
    },
    "scale_protocols":{
          "smb": false,
          "nfs": false,
          "interface": [],
          "scale_ces_groups":[
           {
             "group_name": "group1",
             "node_list": [host-vm1,host-vm2],
             "export_ip_pool": [192.168.100.100,192.168.100.101]
           },
           {
             "group_name": "group2",
             "node_list": [host-vm3],
             "export_ip_pool": [192.168.100.102,192.168.100.103]
          }
          ],
          "filesystem": cesSharedRoot,
          "mountpoint": /gpfs/cesSharedRoot
    }
    ```

Optional Role Variables
-----------------------

User can also define some of the following [variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) to override default values and customize the behavior:

- `scale_cluster_clustername`: User defined Spectrum Scale cluster name.
- `scale_prepare_disable_selinux`: SELinux can be disabled. It can be either true or false (default).
- `scale_prepare_disable_firewall`: Firewall can be disabled. It can be either true or false (default).


Available Roles
---------------

If you are assembling your own [playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html), the following [roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) are available for you to reuse:

- [Core GPFS](./roles/core)
- [GPFS GUI](./roles/gui)
- [GPFS Callhome](./roles/callhome)
- [GPFS SMB](./roles/smb)
- [GPFS NFS](./roles/nfs)
- [GPFS SCALE_FILEAUDITLOGGING](./roles/scale_fileauditlogging)


Cluster Membership
------------------

All hosts in the play are configured as nodes in the same cluster. If you want to add hosts to an existing cluster then add at least one node from that existing cluster to the play.

You can create multiple clusters by running multiple plays.


Limitations
-----------

The roles in this project can (currently) be used to create new clusters or extend existing clusters. Similarly, new file systems can be created or extended. But this role does *not* remove existing nodes, disks, file systems or node classes. This is done on purpose. This is also the reason why it can not be used, for example, to change the file system pool of a disk. Changing the pool requires you to remove and then re-add the disk from a file system, which is not currently in the scope of this role.

Furthermore, upgrades are not currently in scope of this role. Spectrum Scale supports rolling online upgrades (by taking down one node at a time), but this requires careful planning and monitoring and might require manual intervention in case of unforeseen problems.


Troubleshooting
---------------

The roles in this project store configuration files in `/var/tmp` on the first host in the play. These configuration files are kept to determine if definitions have changed since the previous run, and to decide if it's necessary to run certain Spectrum Scale commands (again). When experiencing problems one can simply delete these configuration files from `/var/tmp` in order to clear the cache &mdash; doing so forces re-application of all definitions upon the next run. As a downside, the next run may take longer than expected as it might re-run unnecessary Spectrum Scale commands. This will automatically re-generate the cache.


Reporting Issues and Feedback
-----------------------------

Please use the [issue tracker](https://github.com/IBM/ibm-spectrum-scale-install-infra/issues) to ask questions, report bugs and request features.


Contributing Code
-----------------

We welcome contributions to this project, see [Contributing](CONTRIBUTING.md) for more details.


Disclaimer
----------

Please note: all playbooks / modules / resources in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. We are not responsible for any damage or charges or data loss incurred with their use. You are responsible for reviewing and testing any scripts you run thoroughly before use in any production environment. This content is subject to change without notice.


Copyright and License
---------------------

Copyright IBM Corporation 2020, released under the terms of the [Apache License 2.0](LICENSE).
