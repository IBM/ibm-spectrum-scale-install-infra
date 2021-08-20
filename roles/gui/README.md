IBM Spectrum Scale (GPFS) GUI Ansible Role
======================================

Highly-customizable Ansible role for installing and configuring IBM Spectrum Scale (GPFS) GUI nodes. 

Features
--------

- **Install GUI and zimon packages**
- **Configure Performance Monitoring and collectors**
- **Install and configure Call Home**
- **Dual/HA GUI Nodes**
- **Create Local Users for GUI**
- **Change Password Policy for GUI Users**
- **Configure Active Directory and Map roles to LDAP Groups**
- **Configure E-Mail Notifications**
- **Configure E-Mail Receptions**
- **Configure SNMP Notification**
- **Request HTTPs Certifcate from Hasicorp Vault**
- **Create local Admin User with password from Hasicorp Vault**


The following installation methods are available:
- **Install from (existing) YUM repository**
- **Install from local installation package (accessible on Ansible control machine)**


Future plans:
- **Upgrade, Change and Disable services.**
- **Adding nodes to Performance sensors**

Installation
------
Installation

```
$ ansible-playbook -i hosts playbook.yml

or ./ansible.sh
```



Requirements
-------------

As there's no public repository available, you'll need to download Spectrum Scale (GPFS) packages from the IBM website. Visit https://www.ibm.com/support/fixcentral and search for 'IBM Spectrum Scale (Software defined storage)'.

Local Spectrum Scale Repo
-------
To created a local repo on a web server:

```
cd /your/webserver/folder
# Download the Spectrum Scale install files. get directlink or copy it into your server 
wget ------Spectrum Scale Binary -----
sh ./Spectrum_Scale_Data_Management-5.0.X.X-x86_64-Linux-install --dir ./SpectrumScaleRpms/5.0.X.X/ --silent
yum install -y createrepo
cd SpectrumScaleRpms/5.0.X.X/
createrepo .
```


Role Variables
--------------

Default variables are defined in defaults/main.yml in every rolse. You'll also find detailed documentation in that file. Define your own host variables in your inventory to override the defaults.

Defining the variable scale_version is mandatory. 
- Furthermore, you'll need to configure an installation method by defining one of the following variables:
    - `scale_install_repository_url:` this needs to pointed to `zimon_rpms` folder, as orginal library from download cant find the correct packages.
 
Role Dependencies
----

core role needs to be executed first. but we can also execute only gui role if core  cluster is already exists.

Example Playbook
----------------

The simplest possible playbook to install Spectrum Scale on a node with GUI:

```
---
- hosts: scale01.example.com
  vars:
    - scale_version: 5.0.4.0
    - scale_install_localpkg_path: /path/to/Spectrum_Scale_Standard-5.0.4.0-x86_64-Linux-install
  roles:
    - core/precheck
    - core/node
    - core/cluster
    - gui/precheck
    - gui/node
    - gui/cluster
```

This will install all required packages and create a single-node Spectrum Scale cluster with GUI.

In reality you'll most probably want to install Spectrum Scale on a number of nodes, and you'll also want to consider the node roles in order to achieve high-availability. The cluster will be configured with all hosts in the current play:

```
# host_vars/scale01:
---
scale_storage:
  - filesystem: gpfs01
    blockSize: 4M
    defaultMetadataReplicas: 2
    defaultDataReplicas: 2
    numNodes: 16
    automaticMountOption: true
    defaultMountPoint: /mnt/gpfs01
    disks:
      - device: /dev/sdb
        nsd: nsd_1
        servers: scale01
        failureGroup: 10
        usage: metadataOnly
        pool: system
      - device: /dev/sdc
        nsd: nsd_2
        servers: scale01
        failureGroup: 10
        usage: dataOnly
        pool: data
    
    scale_nodeclass:
      - class1
    scale_config:
      - nodeclass: class1
        params:
          - pagepool: 2G
          - autoload: yes
          - ignorePrefetchLunCount: yes
scale_cluster_gui: true
```
```
# host_vars/scale02:
---
scale_storage:
  - filesystem: gpfs01
    disks:
      - device: /dev/sdb
        nsd: nsd_3
        servers: scale02
        failureGroup: 20
        usage: metadataOnly
        pool: system
      - device: /dev/sdc
        nsd: nsd_4
        servers: scale02
        failureGroup: 20
        usage: dataOnly
        pool: data
scale_cluster_gui: true  ##Dual/HA GUI
```


- For more information check out man pages and https://www.ibm.com/support/knowledgecenter/en/STXKQY/ibmspectrumscale_welcome.html



All the variable below can be added to **host_vars/host:**  on the node you want to be GUI node. 
For the Second GUI node, you only needs to have `scale_cluster_gui: true`

Spetrum Scale Local GUI Users
-------

##### Spectrum Scale GUI Admin.
- This is to be able to access the Spectrum Scale GUI. Change the role for the user do the Permission that is sufficient. (See list of roles below)
    - Default password policy is length of 6 Character. 
    - For Secure environment, Store you password in Ansible Vault or HasiCorp Vault. Se option for HasiCorp below
    - FYI: All of the Parameters here is mandatory.

```
scale_gui_admin_user: "admin"
scale_gui_admin_password: "Admin@GUI"
scale_gui_admin_role: "SecurityAdmin,SystemAdmin"
```

##### Spectrum Scale GUI user. 
- Extra Users can be created.
    - Change the Role for the user to the Permission that is sufficient. 
    - All of the Parameters is mandatory.
```
scale_gui_user_username: 'SEC'
scale_gui_user_password: 'Storage@Scale1'
scale_gui_user_role: 'SystemAdmin'
```

##### HasiCorp Integration - Create Admin user with password from Vault.
- HasiCorp - Create local Admin user with password from vault
    - The Secret is writen to vault `secret/private/{{ computed.name | default(AdminGUI) }}/gui"`
```
scale_gui_admin_hc_vault: false
scale_gui_admin_hc_vault_user: "admin"
scale_gui_admin_hc_vault_role: "SecurityAdmin,SystemAdmin"
```

##### Specifies a role name for the group. Role name is not case-sensitive. Available system-defined roles are:
- **Administrator** - Manages all functions on the system except those deals with managing users, user groups, and authentication.
- **SecurityAdmin** - Manages all functions on the system, including managing users, user groups, and user authentication.
- **SystemAdmin** - Manages clusters, nodes, alert logs, and authentication.
- **StorageAdmin**  - Manages disks, file systems, pools, filesets, and ILM policies.
- **SnapAdmin** - Manages snapshots for file systems and filesets.
- **DataAccess** - Controls access to data. For example, managing access control lists.
- **Monitor** - Monitors objects and system configuration but cannot configure, modify, or manage the system or its resources.
- **ProtocolAdmin** - Manages object storage and data export definitions of SMB and NFS protocols.
- **UserAdmin** - Manages access for GUI users. Users who are part of this group have edit permissions only in the Access pages of the GUI. 


----------------------------------------------------------------------------------------------

GUI Users Password Policy Parameters
-------
Add and Change what you need in your inventory files and rest wil use default
If you only want to change max age of password. 
Add  



```
scale_gui_password_policy_change: true
scale_gui_password_policy:
  maxAge: '90'
```


For all functions:

   ```
    scale_gui_password_policy_change: ## To enable Change of Password Policy
    scale_gui_password_policy:
      minLength: '6' ## Minimum password length
      maxAge: '90'   ## Maximum password age
      minAge: '0'    ## Minimum password age
      remember: '3'  ## Remember old passwords
      minUpperChars: '0'   ## Minimum upper case characters
      minLowerChars: '0'   ## Minimum lower case characters
      minSpecialChars: '0' ## Minimum special case characters
      minDigits: '0'   ## Minimum digits
      maxRepeat: '0'   ## Maximum number of repeat characters
      minDiff: '1'     ## Minimum different characters with respect to old password
      rejectOrAllowUserName: '--rejectUserName'  ## either  '--rejectUserName' or '--allowUserName'
   ```
----------------------------------------------------------------------------------------------

LDAP information for Managing GUI users in an external AD or LDAP server
-----
Enable Active Directory Integration og GUI
you'll likely want to define in your inventory

```
scale_gui_ldap_integration: true
scale_gui_ldap:
  name: 'myad' ##Alias for your LDAP/AD server
  host: 'myad.mydomain.local'
  bindDn: 'CN=servicebind,CN=Users,DC=mydomain,DC=local'
  bindPassword: 'password'
  baseDn: 'CN=Users,DC=mydomain,DC=local'
  port: '389' #Default 389
  type: 'ad' #Default Microsoft Active Directory
  #securekeystore: /tmp/ad.jks #Local on GUI Node
  #secureport: '636' #Default 636
```

Managing GUI users in an external AD or LDAP  Parameters

Parameter                Description
- **name:**               Alias for your LDAP/AD server
- **host:**               The IP address or host name of the LDAP server.
- **baseDn:**             BasedDn string for the repository.
- **bindDn:**             BindDn string for the authentication user.
- **bindPassword:**       Password of the authentication user.
- **port:**               Port number of the LDAP. Default is 389
- **type:**               Repository type (ad, ids, domino, secureway, iplanet, netscape, edirectory or custom). Default is ad.
- **securekeystore:**     Location with file name of the keystore file (.jks, .p12 or .pfx).
- **secureport:**         Port number of the LDAP.  636 over SSL.


----------------------------------------------------------------------------------------------

Managing GUI users in an external AD or LDAP - LDAP/AD Mappings to Roles
--------

- The LDAP/AD Groups needs to be create in the LDAP. (don't need created before deployment.)

You'll likely want to define this in your host inventory

Add the mappings that you want and replace the scale-* with your ldap groups. 

   ```
    scale_gui_groups:
      administrator: 'scale-admin'
      securityadmin: 'scale-securityadmin'
      storageadmin: 'scale-storage-administrator'
      snapadmin: 'scale-snapshot-administrator'
      data_access: 'scale-data-access'
      monitor: 'scale-monitor'
      protocoladmin: 'scale-protocoladmin'
      useradmin: 'scale-useradmin'
   ```

The following are the default user groups:

- **Administrator** - Manages all functions on the system except those deals with managing users, user groups, and authentication.
- **SecurityAdmin** - Manages all functions on the system, including managing users, user groups, and user authentication.
- **SystemAdmin** - Manages clusters, nodes, alert logs, and authentication.
- **StorageAdmin**  - Manages disks, file systems, pools, filesets, and ILM policies.
- **SnapAdmin** - Manages snapshots for file systems and filesets.
- **DataAccess** - Controls access to data. For example, managing access control lists.
- **Monitor** - Monitors objects and system configuration but cannot configure, modify, or manage the system or its resources.
- **ProtocolAdmin** - Manages object storage and data export definitions of SMB and NFS protocols.
- **UserAdmin** - Manages access for GUI users. Users who are part of this group have edit permissions only in the Access pages of the GUI. 

----------------------------------------------------------------------------------------------

E-Mail notifications Parameters.
-------
- The email feature transmits operational and error-related data in the form of an event notification email.
    - Email notifications can be customized by setting a custom header and footer for the emails and customizing the subject by selecting and combining from the following variables: &message, &messageId, &severity, &dateAndTime, &cluster and &component.


- **name**  - Specifies a name for the e-mail server.
- **address** - Specifies the address of the e-mail server. Enter the SMTP server IP address or host name. For example, 10.45.45.12 or smtp.example.com.
- **portNumber** - Specifies the port number of the e-mail server. Optional.
- **reply_email_address/sender_address** - Specifies the sender's email address.
- **contact_name/sender_name** - Specifies the sender's name.
- **subject** Notifications can be customized by setting a custom header and footer  or with variable like "&cluster&message"   ## Variables:  &message &messageId &severity &dateAndTime &cluster&component
- **sender_login_id** - Login needed to authenticate sender with email server in case the login is different from the sender address (--reply). Optional.
- **password** - Password used to authenticate sender address (--reply) or login id (--login) with the email sever.
 

- Change parameter for your environments, the Mandatory fields are marked.
     ```
    ## Parameters for configure E-Mail notification
    ## Enable E-mail notifications in Spectrum Scale GUI
    scale_gui_email_notification: true
    scale_gui_email:
      name: 'SMTP_1'                ## Mandatory Default is SMTP_1
      ipaddress: 'emailserverhost'  ## Mandatory
      ipport: '25'                  ## Mandatory
      replay_email_address: "scale-server-test@acme.com" ## Mandatory
      contact_name: 'scale-contact-person'               ## Mandatory
      subject: "&cluster&message"   ## Variables:  &message &messageId &severity &dateAndTime &cluster&component
      sender_login_id:
      password:
      headertext:
      footertext:
     ```


----------------------------------------------------------------------------------------------

E-Mail Recipients Parameters
--------
- To add E-mail Recipients the scale_gui_email_notification need to be configured.
  Add all of the parameters change them to your environment. See example below.


**Options:**  
- **NAME**: Name of the email Recipients

- **Address:** userAddress Specifies the address of the e-mail user

- **Components_security_level**
   - The value `scale_gui_email_recipients_components_security_level: ` Need to contain the **Component** and the **Warning/Security Level**
        - Chose component like **SCALEMGMT** and the security_level of WARNING wil be **SCALEMGMT=ERROR**
        - Security level: Chose the lowest severity of an event for which you want to receive and email.  Example, selectin Tip includes events with severity Tip, Warning, and Error in the email.
        - The Severity level is as follows: : **INFO**, **TIP**, **WARNING**, **ERROR**

    List of all security levels:
    ```
    AFM=WARNING,AUTH=WARNING,BLOCK=WARNING,CESNETWORK=WARNING,CLOUDGATEWAY=WARNING,CLUSTERSTATE=WARNING,DISK=WARNING,FILEAUDITLOG=WARNING,FILESYSTEM=WARNING,GPFS=WARNING,GUI=WARNING,HADOOPCONNECTOR=WARNING,KEYSTONE=WARNING,MSGQUEUE=WARNING,NETWORK=WARNING,NFS=WARNING,OBJECT=WARNING,PERFMON=WARNING,SCALEMGMT=WARNING,SMB=WARNING,CUSTOM=WARNING,AUTH_OBJ=WARNING,CES=WARNING,CESIP=WARNING,NODE=WARNING,THRESHOLD=WARNING,WATCHFOLDER=WARNING,NVME=WARNING,POWERHW=WARNING
    ```

- **Reports**  listOfComponents 
    - Specifies the components to be reported. The tasks generating reports are scheduled by default to send a report once per day. Optional.

    ```
     AFM,AUTH,BLOCK,CESNETWORK,CLOUDGATEWAY,CLUSTERSTATE,DISK,FILEAUDITLOG,FILESYSTEM,GPFS,GUI,HADOOPCONNECTOR,KEYSTONE,MSGQUEUE,NETWORK,NFS,OBJECT,PERFMON,SCALEMGMT,SMB,CUSTOM,AUTH_OBJ,CES,CESIP,NODE,THRESHOLD,WATCHFOLDER,NVME,POWERHW 
    ```

- **quotaNotification**
   Enables quota notifications which are sent out if the specified threshold is violated. (See --quotathreshold)

- **quotathreshold**  valueInPercent
    - Sets  the  threshold(percent  of the hard limit)for including quota violations in the quota digest report.  
    - The default value is 100. The values -3, -2, -1, and zero have special meaning. 
    - Specify the value -2 to include all results, even entries where the hard quota not set. 
    - Specify the value -1 to include all entries where hard quota is set and current usage is greater than or equal to the soft quota.
    - Specify the value -3 to include all entries where hard quota is not set and current usage is greater than or equal to the soft quota only. 
    - Specify the value 0 to include all entries where the hard quota is set.

 Using unlisted options can lead to an error.  

**Example:** scale_gui_email_recipients
```
scale_gui_email_recipients:
  name: 'name_email_recipient_name'
  address: 'email_recipient_address@email.com'
  components_security_level: 'SCALEMGMT=WARNING,CESNETWORK=WARNING'
  reports: 'DISK,GPFS,AUTH'
  quotaNotification: '--quotaNotification' ##if defined it enabled quota Notification
  quotathreshold: '70.0'
```
- Example: Issue the following  command to add an e-mail recipient named "name_email_recipient_name" who is registered to receive reports on quota violations over 70% of the hard limit as well as an email for every 
WARNING event of the components SCALEMGMT and a report for all events of the components GPFS and DISK

----------------------------------------------------------------------------------------------
    
   
SNMP Notifications Parameters
--------
- To Configure SNMP Notification. 
 - Change the Value: 
   - **scale_gui_snmp_notification:** true
   - **ip_adress** to your SNMP server/host
   - **ip_port** to your SNMP port
   - **community** to your SNMP community 
```
scale_gui_snmp_notification: true
scale_gui_snmp_server:
  ip_adress: 'snmp_server_host'
  ip_port: '162'
  community: 'Public'
```


HasiCorp Integration - HTTPs Certificate from Vault.
------
- Generate https Certificate from HasiCorp Vault and import it to Scale GUI. 
- The Scale host need to be included in Hasi Vault and the Ansible playbook need to have the **computed.name** variables, normaly the playbook is then run from Terraform to get values. 

Change the values to true to enable the https certificate import.
 ```
 scale_gui_cert_hc_vault: true
 ```
 


Limitations
-----------

This role can (currently) have some limitation so that running it on existing environment it maybe fail.  


Troubleshooting
---------------

To get output from Ansible task in stdout and stderr for some tasks. add  `scale_gui_ansible_task_output: true` in your host var.

This role stores configuration files in `/var/mmfs/tmp` on the first host in the play. These configuration files are kept to determine if definitions have changed since the previous run, and to decide if it's necessary to run certain Spectrum Scale commands (again). When experiencing problems one can simply delete these configuration files from `/var/mmfs/tmp` in order to clear the cache &mdash; this will force re-application of all definitions upon the next run. As a downside, the next run may take longer than expected as it might re-run unnecessary Spectrum Scale commands. Doing so will automatically re-generate the cache.

If you experience  "msg": "Unable to start service gpfsgui: Job for gpfsgui.service failed because a timeout was exceeded. See \"systemctl status gpfsgui.service\" and \"journalctl -xe\" for details.\n"}`
this is mostly cause by Performance issue in your environments like overcommitment on your hypervisors, if the Service takes to long time to start the systemd times out, try to rerun the playbook.

Please use the [issue tracker](https://github.com/IBM/ibm-spectrum-scale-install-infra/issues) to ask questions, report bugs and request features.

