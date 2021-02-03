Role Definition
-------------------------------
- Role name: OBJECT
- Definition:
  - Object storage combines the benefits of IBM Spectrum Scale with the most widely used open source object store, OpenStack Swift. 
  - GPFS file systems may be exported using the Object protocol from one or more nodes.
  - After export, normal access to the file system can proceed from GPFS cluster nodes or OBJECT client nodes.


Prerequisite
----------------------------
- CES should be enabled and configured.
- At least 1 node should be designated as object node.
- Access to a external repository server to install the dependency Openstack and Swift packages.
  The installation of the dependency packages for object will be done via an external repository server (e.g. ftp3). 
  This external repository server needs to be subscript to all object defined nodes.

- The parameters required to configure are as follows:

  scale_ces_obj:
   pwd_file: obj_passwd.j2
   dynamic_url: True/False
   enable_s3: True/False
   local_keystone: True/False
   enable_file_access: True/False
   endpoint_hostname: [name_of_first_obj_node]
   object_fileset: Object_Fileset
   admin_user: [username]
   admin_pwd: [password]
   database_pwd: [password]


Design
---------------------------
- Directory Structure:
  - Path: /ibm-spectrum-scale-install-infra/roles/scale_object
  - Inside the object role, there are four more roles to enable microservice architecture:
    - `Precheck`: This role checks that all the prerequisites are satisfied before installing the object rpms. It checks the following things:
      - Whether all object definitions are correct.
      - Whether at least one object node is specified or not.
    - `Node`: This role installs the rpms required for object protocol functionality. There are 3 methods to install object rpms:
      - via local package, requires  scale_install_localpkg_path variable to be set in main playbook.
      - via remote package, requires scale_install_remotepkg_path variable to be set in main playbook.
      - via yum repository, requires scale_install_repository_url variable to be set in main playbook.
    - `Cluster`: This role enables the object protocol.
	  - Configuration of pmswift for performance monitor.
    - `Postcheck`: This role checks if object service is running or not.


Implementation
-------------------------
- `Precheck`
  - This role creates a list of object nodes and checks if atleast one node is set as object nodes.
  - Checks if all object definitons set in group_var/all.yml are correct.
  
- `Node`
  - Installation via local package: rpms are on local machine
    - File name: install_local_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/scale_object/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install object.
  - Installation via remote package: rpms are on remote machine
    - File name: install_remote_pkg.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/scale_object/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install object.
  - Installation via repository: rpms are in yum repo
    - File name: install_repository.yml
    - Path: /root/ibm-spectrum-scale-install-infra/roles/nfs/node/tasks
    - This playbook configures the yum repo using the URL mentioned in variable scale_install_nfs_repository_url and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install object.
  - The installation method is selected in the playbook ‘install.yml’ . Installation method depends on the variables defined.
    - If  ‘scale_install_repository_url’ is defined, then the installation method is repository.
    -   If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is defined, then the installation method is remote.
    -   If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is undefined and ‘scale_install_localpkg_path’ is defined, then the installation method is local.
  - Depending on the installation method, appropriate playbook is called for collecting the rpms and rpms are installed on all the nodes on which object is enabled.

- `Cluster`
  - To enable object protocol, we run command `mmces service enable obj` on all the nodes where object is enabled.

- `Postcheck`
  - This role uses command `mmces service list` to check if object service is up and running.


Mit freundlichen Grüßen / Kind regards

Christoph Keil

IBM Systems
Spectrum Scale Development
				
				

Phone:	+49-162-4159479	 Am Weiher 24		

Email:	chkeil@de.ibm.com	 65451 Kelsterbach		 

		 Germany		 
				
IBM Data Privacy Statement 				
IBM Deutschland Research & Development GmbH / Vorsitzender des Aufsichtsrats: Gregor Pillen
Geschäftsführung: Dirk Wittkopp
Sitz der Gesellschaft: Böblingen / Registergericht: Amtsgericht Stuttgart, HRB 243294 				

