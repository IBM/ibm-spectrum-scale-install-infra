# Migrating from master to main

This Git repository has two branches: `master`, which is now stable, and `main`, which is where new functionality will be implemented. Your playbooks need to be adjusted when switching from one branch to the other, and these adjustments are outlined in this document.

## What's changing?

A long term goal of this project is to make the code available through [Ansible Galaxy](https://galaxy.ansible.com/). It became clear that changes to the project's directory structure would be inevitable to follow the conventions imposed by Galaxy (i.e. [Collections format](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html)) — and this was taken as an opportunity to also rename all existing roles and some variables for consistency. See [#570](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/570), [#572](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/572), and [#590](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/590) for details.

All playbooks using the Ansible roles provided by this project need to adapt this new naming scheme, in order to use the latest updates implemented in the `main` branch.

**Important**: The `master` branch (previous default) will stay with the current naming scheme. It is considered stable, which means that only critical bug fixes will be added. New functionality will solely be implemented in the `main` (new default) branch.

## What do I need to do?

The following steps need to be taken in order to consume the `main` branch in your own projects:

-   Repository contents need to be placed in a `collections/ansible_collections/ibm/spectrum_scale` directory, adjacent to your playbooks. The easiest way to do this is to clone the correct branch into the appropriate path:

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

-   Once the repository contents are available in the appropriate path, roles can be referenced by using their Fully Qualified Collection Name (FQCN). A minimal playbook should look similar to this:

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

    -   Old naming: `[component]/[precheck|node|cluster|postcheck]`
    -   New naming: `[component]_[prepare|install|configure|verify]`

    Refer to the examples in the [samples/](samples/) directory for a list of new role names.

-   Some variables have been renamed for consistency as well, but it's expected that these changes only affect very few users. See [#590](https://github.com/IBM/ibm-spectrum-scale-install-infra/pull/590) for details, and refer to [VARIABLESNEW.md](VARIABLESNEW.md) for a complete listing of all available variables.

## Migration script

If you have existing playbooks which reference roles provided by this project, and you wish to migrate to the new format, then there is a [migration script](migrate.sh) available to replace all occurrences of role names in a given file. You can use the migration script like so:

```shell
$ ./migrate.sh playbook.yml
```

Note that the script will create a backup of the file prior to making any changes. Further note that the script does not perform any kind of syntax checking — so you will need to manually verify that the resulting code is syntactically correct.

## What if I need help?

Create a [new issue](https://github.com/IBM/ibm-spectrum-scale-install-infra/issues/new) and provide (the relevant parts of) your playbook, along with the exact error message.
