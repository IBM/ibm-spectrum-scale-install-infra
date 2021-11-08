Role Definition
-------------------------------
- Role name: SMB
- Definition:
  - Stands for "Server Message Block."
  - SMB is a network protocol used by Windows-based computers that allows systems within the same network to share files.
  - It allows computers connected to the same network or domain to access files from other local computers as easily as if they 
  were on the computer's local hard drive.
  
Prerequisite
----------------------------
- CES should be enabled and configured.
- Atleast 1 node should be designated as smb node.
- Native smb service should be stopped, before usinf this role.
- smbd service should be stopped.
- winbind service should be stopped
- winbindd service should be stopped
- ctdb service should be stopped
- ctdbd service should be stopped
- The rpms required for callhome installation are as follows:
  - gpfs.smb*.rpm
  
Design
---------------------------
- Directory Structure:
  - Path: /ibm-spectrum-scale-install-infra/roles/smb
  - Inside the smb role, there are four more roles to enable microservice architecture:
    - `Precheck`: This role checks that all the prerequisites are satisfied before installing the smb rpms. It checks the following things:
      - Whether smb protocol is enabled or not.
      - Whether atleast one smb node is specified or not.
      - Whether the following services are running on the nodes:
        - smb
        - smbd
        - winbind
        - winbindd
        - ctdb
        - ctdbd
    - `Node`: This role installs the rpms required for smb protocol functionality. There are 3 methods to install smb rpms:  
      - via local package, requires  scale_install_localpkg_path variable to be set in main playbook.
      - via remote package, requires scale_install_remotepkg_path variable to be set in main playbook.
      - via yum repository, requires scale_install_callhome_repository_url variable to be set in main playbook.
    - `Cluster`: This role enables the smb protocol.
    - `Postcheck`: This role checks if smb service is running or not.

Implementation
-------------------------
- `Precheck`
  - This role creates a list of smb nodes and checks if atleast one node is set as smb nodes.
  - It checks if all the above defined commands are stopped before running this role. If a service is found running, the execution of 
  this role fails.
  
- `Node`
  - Installation via local package: rpms are on local machine
    - File name: install_local_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/smb/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list 
    ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install smb.
  - Installation via remote package: rpms are on remote machine
    - File name: install_remote_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/smb/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install smb.
  - Installation via repository: rpms are in yum repo
    - File name: install_repository.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/smb/node/tasks
    - This playbook configures the yum repo using the URL mentioned in variable scale_install_smb_repository_url and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install smb.
  - The installation method is selected in the playbook ‘install.yml’ . Installation method depends on the variables defined.
    - If  ‘scale_install_smb_repository_url’ is defined, then the installation method is repository.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is defined, then the installation method is remote.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is undefined and ‘scale_install_localpkg_path’ is defined, then the installation method is local.
  - Depending on the installation method, appropriate playbook is called for collecting the rpms and rpms are installed on all the nodes on which smb is enabled. 
  
- `Cluster`
  - To enable smb protocol, we run command `mmces service enable smb` on all the nodes where smb is enabled.
  
- `Postcheck`
  - This role uses command `mmces service list` to check if smb service is up and running.
