IBM Spectrum Scale (GPFS) Deployment using Ansible Roles
========================================================

Ansible project with multiple roles for installing and configuring IBM Spectrum Scale (GPFS).

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

#### Core Spectrum Scale Cluster features
- [x] Install core Spectrum Scale packages on Linux nodes
- [x] Install Spectrum Scale license packages on Linux nodes
- [x] Compile or install pre-compiled Linux kernel extension (mmbuildgpl)
- [x] Configure client and server license
- [x] Assign default quorum (maximum 7 quorum nodes) if user has not defined in the inventory
- [x] Assign default manager nodes(all nodes will act as manager node) if user has not defined in the inventory
- [x] Create new cluster (mmcrcluster -N /var/mmfs/tmp/NodeFile -C {{ scale_cluster_clustername }})
- [x] Create cluster with profiles
- [x] Create Cluster with daemon and admin network
- [x] Add new node into existing cluster
- [x] Configure node classes
- [x] Define configuration parameters based on node classes
- [x] Configure NSDs and file system
- [ ] Configure NSDs without file system
- [x] Extend NSDs and file system
- [x] Add disks to existing file systems

#### Spectrum Scale Management GUI features
- [x] Install Spectrum Scale management GUI packages on GUI designated nodes
- [x] maximum 3 management GUI nodes to be configured
- [x] Install performance monitoring sensor packages on all Linux nodes
- [x] Install performance monitoring packages on all GUI designated nodes
- [x] Configure performance monitoring and collectors
- [ ] Configure HA federated mode collectors

#### Spectrum Scale Callhome features
- [x] Install Spectrum Scale callhome packages on all cluster nodes
- [x] Configure callhome

#### Spectrum Scale CES (SMB and NFS) Protocol supported features (5.0.5.2)
- [x] Install Spectrum Scale SMB or NFS on selected cluster nodes
- [x] Install Spectrum Scale OBJECT on selected cluster nodes (5.1.1.0)
- [x] CES IPV4 or IPV6 support
- [x] CES interface mode support


Minimal tested Versions
-----------------------

The following Ansible versions are tested:

- 2.9 and above

The following IBM Spectrum Scale versions are tested:

- 5.0.4.0
- 5.0.4.1
- 5.0.4.2
- 5.0.5.X
- 5.0.5.2 For CES (SMB and NFS)  
- 5.1.0.0
- 5.1.1.0 with Object

Specific OS requirements:

- For CES (SMB/NFS) on SLES15, Python 3 is required.
- For CES (OBJECT) RhedHat 8.x is required. 


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

- **Download Spectrum Scale packages**

  - A Developer Edition Free Trial is available at this site: https://www.ibm.com/account/reg/us-en/signup?formid=urx-41728

  - Customers who have previously purchased Spectrum Scale can obtain entitled versions from IBM Fix Central. Visit https://www.ibm.com/support/fixcentral and search for 'IBM Spectrum Scale (Software defined storage)'.

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

- **Change working directory**

  There are different methods for accessing the roles provided by this project. You can either change your working directory to the cloned repository and create your own files inside this directory (optionally copying examples from the [samples/](samples/) subdirectory):

  ```shell
  $ cd ibm-spectrum-scale-install-infra/
  ```

  Alternatively, you can define an [Ansible environment variable](https://docs.ansible.com/ansible/latest/reference_appendices/config.html#envvar-ANSIBLE_ROLES_PATH) to make the roles accessible in any external project directory:

  ```shell
  $ export ANSIBLE_ROLES_PATH=$(pwd)/ibm-spectrum-scale-install-infra/roles/
  ```

- **Create Ansible inventory**

  Define Spectrum Scale nodes in the [Ansible inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) (e.g. `./hosts`) in the following format:

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

  The basic [Ansible playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html) (e.g. `./playbook.yml`) looks as follows:

  ```yaml
  # playbook.yml:
  ---
  - hosts: cluster01
    vars:
      - scale_install_localpkg_path: /path/to/Spectrum_Scale_Standard-5.0.4.0-x86_64-Linux-install
    roles:
      - core/precheck
      - core/node
      - core/cluster
      - core/postcheck
  ```   

  Again, this is just a minimal example. There are different installation methods available, each offering a specific set of options:

  - Installation from (existing) YUM repository (see [samples/playbook_repository.yml](samples/playbook_repository.yml))
  - Installation from remote installation package (see [samples/playbook_remotepkg.yml](samples/playbook_remotepkg.yml))
  - Installation from local installation package (see [samples/playbook_localpkg.yml](samples/playbook_localpkg.yml))
  - Installation from single directory package path (see [samples/playbook_directory.yml](samples/playbook_directory.yml))

  Refer to [VARIABLES.md](VARIABLES.md) for a full list of all supported configuration options.

- **Run the playbook to install and configure the Spectrum Scale cluster**

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
- Configure node classes and Spectrum Scale configuration attributes (see [samples/playbook_nodeclass.yml](samples/playbook_nodeclass.yml))
- Deploy Spectrum Scale using JSON inventory (see [samples/playbook_json_ces.yml](samples/playbook_json_ces.yml))


Available Roles
---------------

The following [roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html) are available for you to reuse when assembling your own [playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html):

- [Core GPFS](roles/core)*
- [GPFS GUI](roles/gui)
- [GPFS SMB](roles/smb)
- [GPFS NFS](roles/nfs)
- [GPFS OBJECT](roles/scale_object)
- [GPFS HDFS](roles/scale_hdfs)
- [GPFS Call Home](roles/callhome)
- [GPFS File Audit Logging](roles/scale_fileauditlogging)

Note that [Core GPFS](roles/core) is the only mandatory role, all other roles are optional. Each of the optional roles requires additional configuration variables. Browse the examples in the [samples/](samples/) directory to learn how to:

- Configure Graphical User Interface (GUI) (see [samples/playbook_gui.yml](samples/playbook_gui.yml))
- Configure Protocol Services (SMB & NFS) (see [samples/playbook_ces.yml](samples/playbook_ces.yml))
- Configure Protocol Services (HDFS) (see [samples/playbook_ces_hdfs.yml](samples/playbook_ces_hdfs.yml))
- Configure Protocol Services (OBJECT) (see [samples/playbook_ces_object.yml](samples/playbook_ces_object.yml))
- Configure Call Home (see [samples/playbook_callhome.yml](samples/playbook_callhome.yml))
- Configure File Audit Logging (see [samples/playbook_fileauditlogging.yml](samples/playbook_fileauditlogging.yml))
- Configure cluster with daemon and admin network (see samples/daemon_admin_network)

Cluster Membership
------------------

All hosts in the play are configured as nodes in the same Spectrum Scale cluster. If you want to add hosts to an existing cluster then add at least one node from that existing cluster to the play.

You can create multiple clusters by running multiple plays.


Limitations
-----------

The roles in this project can (currently) be used to create new clusters or extend existing clusters. Similarly, new file systems can be created or extended. But this role does *not* remove existing nodes, disks, file systems or node classes. This is done on purpose &mdash; and this is also the reason why it can not be used, for example, to change the file system pool of a disk. Changing the pool requires you to remove and then re-add the disk from a file system, which is not currently in the scope of this role.

Furthermore, upgrades are not currently in scope of this role. Spectrum Scale supports rolling online upgrades (by taking down one node at a time), but this requires careful planning and monitoring and might require manual intervention in case of unforeseen problems.


Troubleshooting
---------------

The roles in this project store configuration files in `/var/mmfs/tmp` on the first host in the play. These configuration files are kept to determine if definitions have changed since the previous run, and to decide if it's necessary to run certain Spectrum Scale commands (again). When experiencing problems one can simply delete these configuration files from `/var/mmfs/tmp` in order to clear the cache &mdash; doing so forces re-application of all definitions upon the next run. As a downside, the next run may take longer than expected as it might re-run unnecessary Spectrum Scale commands. This will automatically re-generate the cache.


Reporting Issues and Feedback
-----------------------------

Please use the [issue tracker](https://github.com/IBM/ibm-spectrum-scale-install-infra/issues) to ask questions, report bugs and request features.


Contributing Code
-----------------

We welcome contributions to this project, see [CONTRIBUTING.md](CONTRIBUTING.md) for more details.


Disclaimer
----------

Please note: all playbooks / modules / resources in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. We are not responsible for any damage or charges or data loss incurred with their use. You are responsible for reviewing and testing any scripts you run thoroughly before use in any production environment. This content is subject to change without notice.


Copyright and License
---------------------

Copyright IBM Corporation 2020, released under the terms of the [Apache License 2.0](LICENSE).
