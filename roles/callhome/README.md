Role Definition
-------------------------------
- Role name: callhome
- Definition:
  - The call home feature collects files, logs, traces, and details of certain system events from different nodes and services.
  - The mmcallhome command provides options to configure, enable, run, schedule, and monitor call home related tasks in the IBM Spectrum Scale cluster.
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
    - `precheck`: This role checks that all the prerequisites are satisfied before installing the callhome rpms. It checks the following things:
      - Whether callhome is enabled or not.
      - If callhome is enabled, it checks whether proper customer information is provided or not. This is necessary for proper configuration of callhome. Without this information callhome installation will fail.
      - Check whether proxy is enabled. If yes, check if all the information required for setting up proxy is defined.
      - Check if connection can be established to URL https://esupport.ibm.com.
    - `node`: This role installs the rpms required for callhome functionality. There are 3 methods to install callhome rpms:  
      - via local package, requires  scale_install_localpkg_path variable to be set in main playbook.
      - via remote package, requires scale_install_remotepkg_path variable to be set in main playbook.
      - via yum repository, requires scale_install_callhome_repository_url variable to be set in main playbook.
    - `cluster`: This role configures the callhome functionality. All the parameters required for configuration needs to be defined in `group_vars` or in the JSON inventory. If callhome is already configured, this step is skipped. Following configurations are made:
      - Check if callhome is enabled. If yes, skip this step.
      - Setup the call home proxy configuration if enabled.
      -	Setup the call home customer configuration.
      -	Enable callhome.
      -	Check if callhome group is already created. If yes, skip next step.
      -	Create callhome group.
      -	Setup the call home schedule configuration.
    - `postcheck`: This role performs the connection test and returns the status.
