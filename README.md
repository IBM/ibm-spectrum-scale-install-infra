**Important**: You are viewing the `main` branch of this repository. If you've previously used the `master` branch in your own playbooks then you will need to make some changes in order to switch to the `main` branch. See [MIGRATING.md](MIGRATING.md) for details.

---

IBM Storage Scale (GPFS) Deployment using Ansible Roles
=======================================================

Ansible project with multiple roles for installing and configuring IBM Storage Scale (GPFS) software defined storage.

**Table of Contents**

- [Features](#features)
- [Versions](#minimal-tested-versions)
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

#### Infrastructure minimal tested configuration

- [x] Pre-built infrastructure (using a static inventory file)
- [ ] Dynamic inventory file

#### OS support

- [x] Support for RHEL 7 on x86_64, PPC64 and PPC64LE
- [x] Support for RHEL 8 on x86_64 and PPC64LE
- [x] Support for RHEL 9 on x86_64 and PPC64LE
- [x] Support for UBUNTU 20 on x86_64 and PPC64LE
- [x] Support for UBUNTU 22 on x86_64 and PPC64LE
- [x] Support for SLES 15 on x86_64 and PPC64LE

#### Common prerequisites

- [x] Disable SELinux (`scale_prepare_disable_selinux: true`), by default false
- [x] Disable firewall (`scale_prepare_disable_firewall: true`), by default false.
- [ ] Install and start NTP
- [ ] Create /etc/hosts mappings
- [ ] Open firewall ports
- [x] Generate SSH keys
- [x] User must set up base OS repositories

#### Core IBM Storage Scale prerequisites

- [x] Install yum-utils package
- [x] Install gcc-c++, kernel-devel, make
- [x] Install elfutils,elfutils-devel (RHEL8 specific)

#### Core IBM Storage Scale Cluster features

- [x] Install core IBM Storage Scale packages on Linux nodes
- [x] Install IBM Storage Scale license package on Linux nodes
- [x] Compile or install pre-compiled Linux kernel extension (mmbuildgpl)
- [x] Configure client and server license
- [x] Assign default quorum (maximum 7 quorum nodes) if user has not defined in the inventory
- [x] Assign default manager nodes (all nodes will act as manager nodes) if user has not defined in the inventory
- [x] Create new cluster (mmcrcluster -N /var/mmfs/tmp/NodeFile -C {{ scale_cluster_clustername }})
- [x] Create cluster with profiles
- [x] Create cluster with daemon and admin network
- [x] Add new node into existing cluster
- [x] Configure node classes
- [x] Define configuration parameters based on node classes
- [x] Configure NSDs and file system
- [ ] Configure NSDs without file system
- [x] Add NSDs
- [x] Add disks to existing file system

#### IBM Storage Scale Management GUI features

- [x] Install IBM Storage Scale management GUI packages on designated GUI nodes
- [x] Maximum 3 GUI nodes to be configured
- [x] Install performance monitoring sensor packages on all Linux nodes
- [x] Install performance monitoring collector on all designated GUI nodes
- [x] Configure performance monitoring and collectors
- [ ] Configure HA federated mode collectors

#### IBM Storage Scale Call Home features

- [x] Install IBM Storage Scale Call Home packages on all cluster nodes
- [x] Configure Call Home

#### IBM Storage Scale CES (SMB and NFS) Protocol supported features

- [x] Install IBM Storage Scale SMB or NFS on selected cluster nodes (5.0.5.2 and above)
- [x] Install IBM Storage Scale Object on selected cluster nodes (5.1.1.0 and above)
- [x] Install IBM Storage Scale S3 on selected cluster nodes (5.2.0.0 and above)
- [x] CES IPV4 or IPV6 support
- [x] CES interface mode support

Minimal tested Versions
-----------------------

The following Ansible versions are tested:

- 2.9 and above
- **Refer to the [Release Notes](https://github.com/IBM/ibm-spectrum-scale-install-infra/releases) for details**

The following IBM Storage Scale versions are tested:

- 5.0.4.0 and above
- 5.0.5.2 and above for CES (SMB and NFS)
- 5.1.1.0 and above for CES (Object)
- 5.2.0.0 and above for CES (S3)
- **Refer to the [Release Notes](https://github.com/IBM/ibm-spectrum-scale-install-infra/releases) for details**

Specific OS requirements:

- For CES (SMB/NFS) on SLES15: Python 3 is required.
- For CES (Object): RhedHat 8.x is required.
- For CES (S3): RhedHat 8.x or RhedHat 9.x is required.

Prerequisites
-------------

Users need to have a basic understanding of the [Ansible concepts](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html) for being able to follow these instructions. Refer to the [Ansible User Guide](https://docs.ansible.com/ansible/latest/user_guide/index.html) if this is new to you.

- **Install Ansible on any machine** ([control node](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#control-node))

  ```shell
  $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  $ python get-pip.py
  $ pip3 install ansible==2.9
  ```

  Refer to the [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/index.html) for detailed installation instructions.

  Note that [Python 3](https://docs.ansible.com/ansible/latest/reference_appendices/python_3_support.html) is required for certain functionality of this project to work. Ansible should automatically detect and use Python 3 on managed machines, refer to the [Ansible documentation](https://docs.ansible.com/ansible/latest/reference_appendices/python_3_support.html#using-python-3-on-the-managed-machines-with-commands-and-playbooks) for details and workarounds.

- **Download IBM Storage Scale packages**

  - A Developer Edition Free Trial is available at this site: https://www.ibm.com/account/reg/us-en/signup?formid=urx-41728

  - Customers who have previously purchased IBM Storage Scale can obtain entitled versions from IBM Fix Central. Visit https://www.ibm.com/support/fixcentral and search for 'IBM Storage Scale (Software defined storage)'.

- **Create password-less SSH keys between all nodes in the cluster**

  A pre-requisite for installing IBM Storage Scale is that password-less SSH must be configured among all nodes in the cluster. Password-less SSH must be configured and verified with [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name), hostname, and IP of every node to every node.

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

- **Create project directory on [Ansible control node](https://docs.ansible.com/ansible/latest/user_guide/basic_concepts.html#control-node)**

  The preferred way of accessing the roles provided by this project is by placing them inside the `collections/ansible_collections/ibm/spectrum_scale` directory of your project, adjacent to your [Ansible playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html). Simply clone the repository to the correct path:

  ```shell
  $ mkdir my_project
  $ cd my_project
  $ git clone -b main https://github.com/IBM/ibm-spectrum-scale-install-infra.git collections/ansible_collections/ibm/spectrum_scale
  ```

  Be sure to clone the project under the correct subdirectory:

  ```shell
  my_project/
  ├── collections/
  │   └── ansible_collections/
  │       └── ibm/
  │           └── spectrum_scale/
  │               └── ...
  ├── hosts
  └── playbook.yml
  ```

- **Create Ansible inventory**

  Define IBM Storage Scale nodes in the [Ansible inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) (e.g. `hosts`) in the following format:

  ```yaml
  # hosts:
  [cluster01]
  scale01  scale_cluster_quorum=true   scale_cluster_manager=true
  scale02  scale_cluster_quorum=true   scale_cluster_manager=true
  scale03  scale_cluster_quorum=true   scale_cluster_manager=false
  scale04  scale_cluster_quorum=false  scale_cluster_manager=false
  scale05  scale_cluster_quorum=false  scale_cluster_manager=false
  ```

  The above is just a minimal example. It defines [Ansible variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) directly in the [inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html). There are other ways to define variables, such as [host variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#host-variables) and [group variables](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#group-variables).

  Numerous variables are available which can be defined in either way to customize the behavior of the roles. Refer to [VARIABLES.md](VARIABLES.md) for a full list of all supported configuration options.

- **Create Ansible playbook**

  The basic [Ansible playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html) (e.g. `playbook.yml`) looks as follows:

  ```yaml
  # playbook.yml:
  ---
  - hosts: cluster01
    collections:
      - ibm.spectrum_scale
    vars:
      - scale_install_localpkg_path: /path/to/Spectrum_Scale_Standard-5.0.4.0-x86_64-Linux-install
    roles:
      - core_prepare
      - core_install
      - core_configure
      - core_verify
  ```

  Again, this is just a minimal example. There are different installation methods available, each offering a specific set of options:

  - Installation from (existing) YUM repository (see [samples/playbook_repository.yml](samples/playbook_repository.yml))
  - Installation from remote installation package (see [samples/playbook_remotepkg.yml](samples/playbook_remotepkg.yml))
  - Installation from local installation package (see [samples/playbook_localpkg.yml](samples/playbook_localpkg.yml))
  - Installation from single directory package path (see [samples/playbook_directory.yml](samples/playbook_directory.yml))

  Refer to [VARIABLES.md](VARIABLES.md) for a full list of all supported configuration options.

- **Run the playbook to install and configure the IBM Storage Scale cluster**

  - Using the `ansible-playbook` command:

    ```shell
    $ ansible-playbook -i hosts playbook.yml
    ```

  - Using the automation script:

    ```shell
    $ cd samples/
    $ ./ansible.sh
    ```

    > **Note:**
    > An advantage of using the automation script is that it will generate log files based on the date and the time in the `/tmp` directory.

- **Playbook execution screen**

  Playbook execution starts here:

  ```shell
  $ ./ansible.sh
  Running #### ansible-playbook -i hosts playbook.yml

  PLAY #### [cluster01]
  **********************************************************************************************************

  TASK #### [Gathering Facts]
  **********************************************************************************************************
  ok: [scale01]
  ok: [scale02]
  ok: [scale03]
  ok: [scale04]
  ok: [scale05]

  TASK [common : check | Check Spectrum Scale version]
  *********************************************************************************************************
  ok: [scale01]
  ok: [scale02]
  ok: [scale03]
  ok: [scale04]
  ok: [scale05]

  ...
  ```

  Playbook recap:

  ```shell
  #### PLAY RECAP
  ***************************************************************************************************************
  scale01                 : ok=0   changed=65    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  scale02                 : ok=0   changed=59    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  scale03                 : ok=0   changed=59    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  scale04                 : ok=0   changed=59    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  scale05                 : ok=0   changed=59    unreachable=0    failed=0    skipped=0   rescued=0    ignored=0
  ```

Optional Role Variables
-----------------------

Users can define [variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html) to override default values and customize behavior of the roles. Refer to [VARIABLES.md](VARIABLES.md) for a full list of all supported configuration options.

Additional functionality can be enabled by defining further variables. Browse the examples in the [samples/](samples/) directory to learn how to:

- Configure storage and file systems (see [samples/playbook_storage.yml](samples/playbook_storage.yml))
- Configure node classes and configuration attributes (see [samples/playbook_nodeclass.yml](samples/playbook_nodeclass.yml))
- Deploy IBM Storage Scale using JSON inventory (see [samples/playbook_json_ces.yml](samples/playbook_json_ces.yml))

Available Roles
---------------

The following [roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) are available for you to reuse when assembling your own [playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html):

- Core GPFS (`roles/core_*`)\*
- GUI (`roles/gui_*`)
- SMB (`roles/smb_*`)
- NFS (`roles/nfs_*`)
- Object (`roles/obj_*`)
- HDFS (`roles/hdfs_*`)
- Call Home (`roles/callhome_*`)
- File Audit Logging (`roles/fal_*`)
- S3 (`roles/s3_*`)
- ...

Note that [Core GPFS](roles/core) is the only mandatory role, all other roles are optional. Each of the optional roles requires additional configuration variables. Browse the examples in the [samples/](samples/) directory to learn how to:

- Configure Graphical User Interface (GUI) (see [samples/playbook_gui.yml](samples/playbook_gui.yml))
- Configure Protocol Services (SMB & NFS) (see [samples/playbook_ces.yml](samples/playbook_ces.yml))
- Configure Protocol Services (HDFS) (see [samples/playbook_ces_hdfs.yml](samples/playbook_ces_hdfs.yml))
- Configure Protocol Services (Object) (see [samples/playbook_ces_object.yml](samples/playbook_ces_object.yml))
- Configure Call Home (see [samples/playbook_callhome.yml](samples/playbook_callhome.yml))
- Configure File Audit Logging (see [samples/playbook_fileauditlogging.yml](samples/playbook_fileauditlogging.yml))
- Configure cluster with daemon and admin network (see [samples/daemon_admin_network](samples/daemon_admin_network))
- Configure remotely mounted filesystems (see [samples/playbook_remote_mount.yml](samples/playbook_remote_mount.yml))

Cluster Membership
------------------

All hosts in the play are configured as nodes in the same IBM Storage Scale cluster. If you want to add hosts to an existing cluster then add at least one node from that existing cluster to the play.

You can create multiple clusters by running multiple plays. Note that you will need to [reload the inventory](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/meta_module.html) to clear dynamic groups added by the IBM Storage Scale roles:

```yaml
- name: Create one cluster
  hosts: cluster01
  roles: ...

- name: Refresh inventory to clear dynamic groups
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - meta: refresh_inventory

- name: Create another cluster
  hosts: cluster02
  roles: ...
```

Limitations
-----------

The roles in this project can (currently) be used to create new clusters or extend existing clusters. Similarly, new file systems can be created or extended. But this project does _not_ remove existing nodes, disks, file systems or node classes. This is done on purpose — and this is also the reason why it can not be used, for example, to change the file system pool of a disk. Changing the pool requires you to remove and then re-add the disk from a file system, which is not currently in the scope of this project.

Furthermore, upgrades are not currently in scope of this role. IBM Storage Scale supports rolling online upgrades (by taking down one node at a time), but this requires careful planning and monitoring and might require manual intervention in case of unforeseen problems.

Troubleshooting
---------------

The roles in this project store configuration files in `/var/mmfs/tmp` on the first host in the play. These configuration files are kept to determine if definitions have changed since the previous run, and to decide if it's necessary to run certain IBM Storage Scale commands (again). When experiencing problems one can simply delete these configuration files from `/var/mmfs/tmp` in order to clear the cache — doing so forces re-application of all definitions upon the next run. As a downside, the next run may take longer than expected as it might re-run unnecessary IBM Storage Scale commands. This will automatically re-generate the cache.

Reporting Issues and Feedback
-----------------------------

Please use the [issue tracker](https://github.com/IBM/ibm-spectrum-scale-install-infra/issues) to ask questions, report bugs and request features.

Contributing Code
-----------------

We welcome contributions to this project, see [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

Disclaimer
----------

Please note: all roles / playbooks / modules / resources in this repository are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. We are not responsible for any damage or charges or data loss incurred with their use. You are responsible for reviewing and testing any scripts you run thoroughly before use in any production environment. This content is subject to change without notice.

Copyright and License
---------------------

Copyright IBM Corporation, released under the terms of the [Apache License 2.0](LICENSE).
