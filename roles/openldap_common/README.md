Role Definition
-------------------------------
- Role name: OpenLDAP
- Definition:
  - Stand-alone LDAP Load Balancer Daemon (server or slapd module).

Requirements
------------

- Ubuntu 22.04

Role Variables
--------------

- The parameters required to configure are as follows:

```
  ldap_domain: "example.com"
  ldap_organization: "Example Organization"
  ldap_admin_password: "Passw0rd"
  ldap_basedn: "dc=example,dc=com"
  ldap_admin_dn: "cn=admin,{{ ldap_basedn }}"
  default_usergroup: "sample_group"
  default_user: "john"
  default_user_password: "Passw0rd"
```

  `default_usergroup`, `default_user`, `default_user_password` are optional.

Example Playbook
----------------

```
  - hosts: servers
    roles:
      - openldap-common
```
