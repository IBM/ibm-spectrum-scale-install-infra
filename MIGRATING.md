# Migrating from master to main

This Git repository has two branches: `master`, which is now stable, and `main`, which is where new functionality will be implemented. Your playbooks need to be adjusted when switching from one branch to the other — and these adjustments are outlined in this document.

## What's changing?

A long-term goal of this project is to publish the code through [Ansible Galaxy](https://galaxy.ansible.com/). It became clear that changes to the project's directory structure would be inevitable to follow the conventions imposed by Galaxy (i.e. [Collections format](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)) — and this was taken as an opportunity to also rename all existing roles and some variables for consistency. See [#570](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/570), [#572](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/572), and [#590](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/590) for details.

All playbooks using the Ansible roles provided by this project need to adapt this new naming scheme, in order to use the latest updates implemented in the `main` branch.

**Important**: The `master` branch (previous default) will stay with the current naming scheme. It is considered stable, which means that only critical bug fixes will be added. New functionality will solely be implemented in the `main` (new default) branch.

## What do I need to do?

The following steps need to be taken in order to consume the `main` branch in your own projects:

- Repository contents need to be placed in a `collections/ansible_collections/ibm/spectrum_scale` directory, adjacent to your playbooks. The easiest way to do this is to clone the correct branch into the appropriate path:

  ```shell
  $ git clone -b main https://github.com/IBM/ibm-spectrum-scale-install-infra.git collections/ansible_collections/ibm/spectrum_scale
  ```

  The resulting directory structure should look similar to this:

  ```shell
  my_project/
  ├── collections/
  │   └── ansible_collections/
  │       └── ibm/
  │           └── spectrum_scale/
  │               └── ...
  ├── hosts
  └── playbook.yml
  ```

- Once the repository contents are available in the appropriate path, roles can be referenced by using their Fully Qualified Collection Name (FQCN). A minimal playbook should look similar to this:

  ```yaml
  # playbook.yml:
  ---
  - hosts: cluster01
    roles:
      - ibm.spectrum_scale.core_prepare
      - ibm.spectrum_scale.core_install
      - ibm.spectrum_scale.core_configure
      - ibm.spectrum_scale.core_verify
  ```

  Refer to the [Ansible User Guide](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html#using-collections-in-a-playbook) for details on using collections, including alternate syntax with the `collections` keyword.

  Note that all role names have changed:

  - Old naming: `[component]/[precheck|node|cluster|postcheck]`
  - New naming: `[component]_[prepare|install|configure|verify]`

  Refer to the [name mapping table](#role-name-mapping-table) for a list of new role names.

- Some variables have been renamed for consistency as well, but it's expected that these changes only affect very few users. See [#590](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/590) for details, and refer to [VARIABLES.md](VARIABLES.md) for a complete listing of all available variables.

## Role Name Mapping Table

| `master` branch                  | `main` branch                            |
| -------------------------------- | ---------------------------------------- |
| callhome/cluster                 | ibm.spectrum_scale.callhome_configure    |
| callhome/node                    | ibm.spectrum_scale.callhome_install      |
| callhome/postcheck               | ibm.spectrum_scale.callhome_verify       |
| callhome/precheck                | ibm.spectrum_scale.callhome_prepare      |
| core/cluster                     | ibm.spectrum_scale.core_configure        |
| core/common                      | ibm.spectrum_scale.core_common           |
| core/node                        | ibm.spectrum_scale.core_install          |
| core/postcheck                   | ibm.spectrum_scale.core_verify           |
| core/precheck                    | ibm.spectrum_scale.core_prepare          |
| core/upgrade                     | ibm.spectrum_scale.core_upgrade          |
| gui/cluster                      | ibm.spectrum_scale.gui_configure         |
| gui/node                         | ibm.spectrum_scale.gui_install           |
| gui/postcheck                    | ibm.spectrum_scale.gui_verify            |
| gui/precheck                     | ibm.spectrum_scale.gui_prepare           |
| gui/upgrade                      | ibm.spectrum_scale.gui_upgrade           |
| nfs/cluster                      | ibm.spectrum_scale.nfs_configure         |
| nfs/common                       | ibm.spectrum_scale.ces_common            |
| nfs/node                         | ibm.spectrum_scale.nfs_install           |
| nfs/postcheck                    | ibm.spectrum_scale.nfs_verify            |
| nfs/precheck                     | ibm.spectrum_scale.nfs_prepare           |
| nfs/upgrade                      | ibm.spectrum_scale.nfs_upgrade           |
| remote_mount/                    | ibm.spectrum_scale.remotemount_configure |
| scale_auth/upgrade               | ibm.spectrum_scale.auth_upgrade          |
| scale_ece/cluster                | ibm.spectrum_scale.ece_configure         |
| scale_ece/node                   | ibm.spectrum_scale.ece_install           |
| scale_ece/precheck               | ibm.spectrum_scale.ece_prepare           |
| scale_ece/upgrade                | ibm.spectrum_scale.ece_upgrade           |
| scale_fileauditlogging/cluster   | ibm.spectrum_scale.fal_configure         |
| scale_fileauditlogging/node      | ibm.spectrum_scale.fal_install           |
| scale_fileauditlogging/postcheck | ibm.spectrum_scale.fal_verify            |
| scale_fileauditlogging/precheck  | ibm.spectrum_scale.fal_prepare           |
| scale_fileauditlogging/upgrade   | ibm.spectrum_scale.fal_upgrade           |
| scale_hdfs/cluster               | ibm.spectrum_scale.hdfs_configure        |
| scale_hdfs/node                  | ibm.spectrum_scale.hdfs_install          |
| scale_hdfs/postcheck             | ibm.spectrum_scale.hdfs_verify           |
| scale_hdfs/precheck              | ibm.spectrum_scale.hdfs_prepare          |
| scale_hdfs/upgrade               | ibm.spectrum_scale.hdfs_upgrade          |
| scale_hpt/node                   | ibm.spectrum_scale.afm_cos_install       |
| scale_hpt/postcheck              | ibm.spectrum_scale.afm_cos_verify        |
| scale_hpt/precheck               | ibm.spectrum_scale.afm_cos_prepare       |
| scale_hpt/upgrade                | ibm.spectrum_scale.afm_cos_upgrade       |
| scale_object/cluster             | ibm.spectrum_scale.obj_configure         |
| scale_object/node                | ibm.spectrum_scale.obj_install           |
| scale_object/postcheck           | ibm.spectrum_scale.obj_verify            |
| scale_object/precheck            | ibm.spectrum_scale.obj_prepare           |
| scale_object/upgrade             | ibm.spectrum_scale.obj_upgrade           |
| smb/cluster                      | ibm.spectrum_scale.smb_configure         |
| smb/node                         | ibm.spectrum_scale.smb_install           |
| smb/postcheck                    | ibm.spectrum_scale.smb_verify            |
| smb/precheck                     | ibm.spectrum_scale.smb_prepare           |
| smb/upgrade                      | ibm.spectrum_scale.smb_upgrade           |
| zimon/cluster                    | ibm.spectrum_scale.perfmon_configure     |
| zimon/node                       | ibm.spectrum_scale.perfmon_install       |
| zimon/postcheck                  | ibm.spectrum_scale.perfmon_verify        |
| zimon/precheck                   | ibm.spectrum_scale.perfmon_prepare       |
| zimon/upgrade                    | ibm.spectrum_scale.perfmon_upgrade       |

## Migration script

If you have existing playbooks which reference roles provided by this project, and you wish to migrate to the new format, then there is a [migration script](migrate.sh) available to replace all occurrences of role names in a given file. You can use the migration script like so:

```shell
$ ./migrate.sh playbook.yml
```

Note that the script will create a backup of the file prior to making any changes. Further note that the script does not perform any kind of syntax checking, so you will need to manually verify that the resulting code is syntactically correct.

## What if I need help?

Create a [new issue](https://github.com/IBM/ibm-spectrum-scale-install-infra/issues/new) and provide (the relevant parts of) your playbook, along with the exact error message.
