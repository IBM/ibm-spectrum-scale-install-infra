Role Definition
-------------------------------
- Role name: HDFS
- Definition:
  - HDFS is a network protocol used by Windows-based computers that allows systems within the same network to share files.
  - It allows computers connected to the same network or domain to access files from other local computers as easily as if they 
  were on the computer's local hard drive.

OS/Arch Support:
---------------------------
- Arch : 
   -1: x86
   -2: PowerLe
- OS   :
   -1: RHEL7
   -2: RHEL8

Prerequisite
----------------------------
- CES should be enabled and configured.
- Atleast 1 node should be designated as hdfs node.
- Native hdfs service should be stopped, before usinf this role.
- Atleast one dedicated cesip required for hdfs role.
- Make sure, JAVA 1.8.0 version(java-<1.8.0>-openjdk-devel) should be installed on all the hdfs host nodes and JAVA_HOME exported.
  -1:
     # yum installjava-1.8.0-openjdk-devel
  -2:
     # vi ~/.bashrc
     # export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
     # export PATH=$PATH:$JAVA_HOME/bin

Design
---------------------------
- Directory Structure:
  - Path: /ibm-spectrum-scale-install-infra/roles/scale_hdfs
  - Inside the scale_hdfs role, there are four more roles to enable microservice architecture:
    - `Precheck`: This role checks that all the prerequisites are satisfied before installing the hdfs rpms. It checks the following things:
      - Whether hdfs protocol is enabled or not.
      - Whether atleast one hdfs node is specified or not.
      - Whether supporting JAVA installed on all the hdfs nodes.
    - `Node`: This role installs the rpms required for hdfs protocol functionality. There are 3 methods to install hdfs rpms:  
      - via local package, requires  scale_install_localpkg_path variable to be set in main playbook.
      - via remote package, requires scale_install_remotepkg_path variable to be set in main playbook.
      - via yum repository, requires scale_install_callhome_repository_url variable to be set in main playbook.
    - `Cluster`: This role configure and enables the hdfs protocol.
    - `Postcheck`: This role checks if hdfs service is running or not.

Implementation
-------------------------
- `Precheck`
  - This role creates a list of hdfs nodes and checks if atleast one node is set as hdfs nodes.
  - It checks if all prerequisites are satisfied like supported JAVA installed and JAVA_HOME set(currently java-1.8.0-openjdk supported)
  
- `Node`
  - Installation via local package: rpms are on local machine
    - File name: install_local_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/scale_hdfs/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list 
    ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install hdfs.
  - Installation via remote package: rpms are on remote machine
    - File name: install_remote_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/scale_hdfs/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install hdfs.
  - Installation via repository: rpms are in yum repo
    - File name: install_repository.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/scale_hdfs/node/tasks
    - This playbook configures the yum repo using the URL mentioned in variable scale_install_hdfs_repository_url and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install hdfs.
  - The installation method is selected in the playbook ‘install.yml’ . Installation method depends on the variables defined.
    - If  ‘scale_install_hdfs_repository_url’ is defined, then the installation method is repository.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is defined, then the installation method is remote.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is undefined and ‘scale_install_localpkg_path’ is defined, then the installation method is local.
  - Depending on the installation method, appropriate playbook is called for collecting the rpms and rpms are installed on all the nodes on which hdfs is enabled. 

- `Cluster`
  - This role setup all hdfs required configurations.
  - To enable hdfs protocol, we run command `mmces service enable hdfs` on all the nodes where hdfs is enabled.

- `Postcheck`
  - This role verify namenodes and datanodes status.
  - This role uses command `mmces service list` to check if hdfs service is up and running.
