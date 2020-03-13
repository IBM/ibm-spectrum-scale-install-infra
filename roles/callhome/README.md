Role Definition
-------------------------------
- Role name: Callhome
- Definition:
  - The call home feature collects files, logs, traces, and details of certain system events from different nodes and services.
  - The mmcallhome command provides options to configure, enable, run, schedule, and monitor call home related tasks in the IBM Spectrum       Scale cluster.
  - Information from each node within a call home group is collected and securely uploaded to the IBM® ECuRep server.
  
 
Prerequisite
----------------------------
- Red Hat Enterprise Linux 7.x, Red Hat Enterprise Linux 8.x nodes are supported.
- Intel x86_64, Power LE/BE are supported.
- GPFS CCR (Clustered Configuration Repository) must be enabled.
- The call home node must be able to access the following IP addresses and ports. In the configurations with a proxy, these IP addresses and ports should be accessible over the proxy connection.
  - Host name: esupport.ibm.com
  - IP address: 129.42.56.189, 129.42.60.189, 129.42.54.189
  - Port number: 443
- The parameters required to configure callhome are as follows:
  - Customer information such as customer_name, customer_email, customer_id, customer_country.
  - If proxy is enabled, the proxy information such as proxy_ip, proxy_port, proxy_user, proxy_password.
  
Design
---------------------------
- Directory Structure:
  - Path: /ibm-spectrum-scale-install-infra/roles/callhome
  - Inside the callhome role, there are four more roles to enable microservice architecture:
    - `Precheck`: This role checks that all the prerequisites are satisfied before installing the callhome rpms. It checks the following things:
      - Whether callhome is enabled or not.
      - If callhome is enabled, it checks whether proper customer information is provided or not. This is necessary for proper configuration of callhome. Without this information callhome installation will fail.
      - Check whether proxy is enabled. If yes, check if all the information required for setting up proxy is defined.
      - Check if connection can be established to URL https://esupport.ibm.com.
    - `Node`: This role installs the rpms required for callhome functionality. There are 3 methods to install callhome rpms:  
      - via local package, requires  scale_install_localpkg_path variable to be set in main playbook.
      - via remote package, requires scale_install_remotepkg_path variable to be set in main playbook.
      - via yum repository, requires scale_install_callhome_repository_url variable to be set in main playbook.
    - `Cluster`: This role configures the callhome functionality. All the parameters required for configuration can be found in `/group_vars`. If callhome is already configured, this step is skipped. Following configurations are made:
      - Check if callhome is enabled. If yes, skip this step.
      - Setup the call home proxy configuration if enabled.
      -	Setup the call home customer configuration.
      -	Enable callhome.
      -	Check if callhome group is already created. If yes, skip next step.
      -	Create callhome group.
      -	Setup the call home schedule configuration.
    - `Postcheck`: This role performs the connection test and returns the status.

Implementation
-------------------------
- `Precheck`
  - All the parameters required for setting up callhome is defined in `/ibm-spectrum-scale-install-infra/group_vars/all.yml`. We need to extract these parameters and set them as ansible facts. This is done by the play defined in `/ibm-spectrum-scale-install-infra/roles/callhome/precheck/tasks/storage.yml`. These parameters are extracted in the ansible fact ‘callhome_params’. ‘set_fact’ ansible module is used for this purpose.
  - All the parameters are then checked if they are defined and not empty. These parameters only need to be checked on callhome server node.
  
- `Node`
  - Installation via local package: rpms are on local machine
    - File name: install_local_pkg.yml
    - Path: /ibm-spectrum-scale-install-infra/roles/callhome/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install callhome.
  - Installation via remote package: rpms are on remote machine
    - File name: install_remote_pkg.yml
    - Path: /ibm-spectrum-scale-install-infra/roles/callhome/node/tasks
    - This playbook checks whether the package exists, checks for valid checksum, extracts all the rpms and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install callhome.
  - Installation via repository: rpms are in yum repo
    - File name: install_repository.yml
    - Path: /ibm-spectrum-scale-install-infra/roles/callhome/node/tasks
    - This playbook configures the yum repo using the URL mentioned in variable scale_install_callhome_repository_url and creates a list ‘scale_install_all_rpms’ that contains all the rpms and dependencies required to install callhome.
  - The installation method is selected in the playbook ‘install.yml’ . Installation method depends on the variables defined.
    - If  ‘scale_install_callhome_repository_url’ is defined, then the installation method is repository.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is defined, then the installation method is remote.
    -	If  ‘scale_install_repository_url’ is undefined and ‘scale_install_remotepkg_path’ is undefined and ‘scale_install_localpkg_path’ is defined, then the installation method is local.
  - Depending on the installation method, appropriate playbook is called for collecting the rpms and rpms are installed. 
  
- `Cluster`
  - To check if callhome is enabled or not, the command used is `mmcallhome capability list -Y`
  -	For making proxy configuration, the command used is `mmcallhome proxy change  --proxy-location {proxy_location } --proxy-port { proxy_ip } --proxy-username {proxy_user } --proxy-password { proxy_password }`
  -	For making customer configuration, the command used is `mmcallhome info change --customer-name { customer_name } --customer-id { customer_id } --email {customer_email} --country-code {customer_country }`
  - For enabling callhome, the command used is `mmcallhome capability enable`
  -	To check if callhome group is already present or not, the command used is `mmcallhome group list`
  -	To create a callhome group with a given callhome server, the command used is `mmcallhome group auto --server {callhome_server }`
  -	To setup callhome schedule, the command used is `mmcallhome schedule add –task [daily/weekly]`
  
- `Postcheck`
  - The command used to test callhome connection is mmcallhome test connection.
