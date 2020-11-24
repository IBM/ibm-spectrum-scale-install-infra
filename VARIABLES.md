Variables used by Spectrum Scale (GPFS) Ansible project
=======================================================

- `scale_architecture`
  - example: `x86_64`
  - default: `{{ ansible_architecture }}`

  Specify the Spectrum Scale architecture that you want to install on your nodes.

- `scale_daemon_nodename`
  - example: `scale01`
  - dafault: `{{ ansible_hostname }}`

  Spectrum Scale daemon nodename (defaults to node's hostname).

- `scale_admin_nodename`
  - example: `scale01`
  - dafault: `{{ scale_daemon_nodename }}`

  Spectrum Scale admin nodename (defaults to node's hostname).

- `scale_prepare_disable_selinux`
  - example: `true`
  - default: `false`

  Whether or not to disable SELinux.

- `scale_prepare_enable_ssh_login`
  - example: `true`
  - default: `false`

  Whether or not enable SSH root login (PermitRootLogin) and public key authentication (PubkeyAuthentication).

- `scale_prepare_restrict_ssh_address`
  - example: `true`
  - default: `false`

  Whether or not to restrict SSH access to the admin nodename (ListenAddress). Requires `scale_prepare_enable_ssh_login` to be enabled, too.

- `scale_prepare_disable_ssh_hostkeycheck`
  - example: `true`
  - default: `false`

  Whether or not to disable SSH hostkey checking (StrictHostKeyChecking).

- `scale_prepare_exchange_keys`
  - example: `true`
  - default: `false`

  Whether or not to exchange SSH keys between all nodes.

- `scale_prepare_pubkey_path`
  - example: `/root/.ssh/gpfskey.pub`
  - default: `/root/.ssh/id_rsa.pub`

  Path to public SSH key - will be generated (if it does not exist) and exchanged between nodes. Requires `scale_prepare_exchange_keys` to be enabled, too.

- `scale_prepare_disable_firewall`
  - example: `true`
  - default: `false`

  Whether or not to disable Linux firewalld - if you need to keep firewalld active then change this variable to `false` and apply your custom firewall rules prior to running this role (e.g. as pre_tasks).

- `scale_install_localpkg_path`
  - example: `/root/Spectrum_Scale_Standard-5.0.4.0-x86_64-Linux-install`
  - default: none

  Specify the path to the self-extracting Spectrum Scale installation archive on the local system (accessible on Ansible control machine) - it will be copied to your nodes.

- `scale_install_remotepkg_path`
  - example: `/root/Spectrum_Scale_Standard-5.0.4.0-x86_64-Linux-install`
  - default: none

  Specify the path to Spectrum Scale installation package on the remote system (accessible on Ansible managed node).

- `scale_install_repository_url`
  - example: `http://server/gpfs/`
  - default: none

  Specify the URL of the (existing) Spectrum Scale YUM repository (copy the contents of /usr/lpp/mmfs/{{ scale_version }}/ to a web server in order to build your repository).

  Note that if this is a URL then a new repository definition will be created. If this variable is set to `existing` then it is assumed that a repository definition already exists and thus will *not* be created.

- `scale_install_directory_pkg_path`
  - example: `/tmp/gpfs/`
  - default: none

  Specify the path to the user-provided directory, containing all Spectrum Scale packages. Note that for this installation method all packages need to be kept in a single directory.

- `scale_version`
  - example: `5.0.4.0`
  - default: none

  Specify the Spectrum Scale version that you want to install on your nodes. It is mandatory to define this variable for the following installation methods:
  - Repository installation method (`scale_install_repository_url`)
  - Local archive installation method (`scale_install_localpkg_path`)
  - Remote archive installation method (`scale_install_remotepkg_path`)

  The variable is *not* necessary for the directory installation method (`scale_install_directory`), as with this method the version is automatically detected from the installation package at the given path.
