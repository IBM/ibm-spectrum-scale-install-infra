**Auth Configuration**

This Ansible playbook is designed to automate the process of checking and setting up authentication (Auth) for a service. The playbook performs the following tasks:

For more information, see https://www.ibm.com/docs/en/storage-scale/5.1.8?topic=reference-mmuserauth-command

**Check Service Existence:**
Verifies if the service already exists by inspecting the output of the command: /usr/lpp/mmfs/bin/mmuserauth service check | grep -q 'File configuration is *'.

**Setup Auth with USERDEFINED:**
If the service does not exist and to use userdefined auth mechanism, it sets up authentication using the command: /usr/lpp/mmfs/bin/mmuserauth service create --data-access-method file --type userdefined.

**Setup Auth with LDAP:**
If the service does not exist and to LDAP auth mechanism, it sets up authentication using the command: /usr/lpp/mmfs/bin/mmuserauth service create --data-access-method file --type ldap
