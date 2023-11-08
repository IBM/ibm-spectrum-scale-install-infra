**Setting up LDAP Environment.**

This Ansible playbook is designed to automate the process of setting up the environment for LDAP. The playbook performs the following tasks:

**Create LDAP Base OU:**
Verifies if the base OU exist on the LDAP directory. If the OU is not present, a new OU will be created.

**Check and create LDAP Group:**
Checks if the provided LDAP group already present in the LDAP server. If not a new group will be created based on the requirement.

**Check and create LDAP User:**
Checks if the provided LDAP user already present in the LDAP server. If not the user will be created based on the requirement.
