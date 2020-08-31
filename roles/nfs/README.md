Role Definition
-------------------------------
- Role name: NFS
- Definition:
  - Network File System (NFS) is a distributed file system protocol allowing a user on a client computer to access files over a computer network much like local storage is accessed. 
  - GPFS file systems may be exported using the Network File System (NFS) protocol from one or more nodes. 
  - After export, normal access to the file system can proceed from GPFS cluster nodes or NFS client nodes.
  
  
 
Prerequisite
----------------------------
- CES should be enabled and configured.
- Atleast 1 node should be designated as nfs node.
- Native nfs service should be stopped, before usinf this role.
- nfs-kernel-server service should be stopped.
- knfs-server service should be stopped
- The rpms required for callhome installation are as follows:
  - gpfs.nfs-ganesha*.rpm
  - gpfs.nfs-ganesha-utils*.rpm
  - gpfs.nfs-ganesha-gpfs*.rpm
  
Design
---------------------------
- Directory Structure:
  - Path: /ibm-spectrum-scale-install-infra/roles/nfs
  - Inside the nfs role, there are four more roles to enable microservice architecture:
    - `Precheck`: This role checks that all the prerequisites are satisfied before installing the nfs rpms. It checks the following things:
      - Whether nfs protocol is enabled or not.
      - Whether atleast one nfs node is specified or not.
      - Whether the following services are running on the nodes:
        - nfs
        - nfs-kernel-server
        - knfs-server
    - `Node`: This role installs the rpms required for nfs protocol functionality. There are 3 methods to install nfs rpms:  
      - via local package, requires  scale_install_localpkg_path variable to be set in main playbook.
      - via remote package, requires scale_install_remotepkg_path variable to be set in main playbook.
      - via yum repository, requires scale_install_callhome_repository_url variable to be set in main playbook.
    - `Cluster`: This role enables the nfs protocol.
    - `Postcheck`: This role checks if nfs service is running or not.

Implementation
-------------------------
- `Precheck`
  - This role creates a list of nfs nodes and checks if atleast one node is set as nfs nodes.
  - It checks if all the above defined commands are stopped before running this role. If a service is found running, the execution of this role fails.
  
- `Node`
  - Installation via local package: rpms are on local machine
    - File name: install_local_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/nfs/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install nfs.
  - Installation via remote package: rpms are on remote machine
    - File name: install_remote_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/nfs/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install nfs.
  - Installation via repository: rpms are in yum repo
    - File name: install_repository.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/nfs/node/tasks
    - This playbook configures the yum repo using the URL mentioned in variable scale_install_nfs_repository_url and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install nfs.
  - The installation method is selected in the playbook ‘install.yml’ . Installation method depends on the variables defined.
    - If  ‘scale_install_callhome_repository_url’ is defined, then the installation method is repository.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is defined, then the installation method is remote.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is undefined and ‘scale_install_localpkg_path’ is defined, then the installation method is local.
  - Depending on the installation method, appropriate playbook is called for collecting the rpms and rpms are installed on all the nodes on which nfs is enabled. 
  
- `Cluster`
  - To enable nfs protocol, we run command `mmces service enable nfs` on all the nodes where nfs is enabled.
  
- `Postcheck`
  - This role uses command `mmces service list` to check if nfs service is up and running.
