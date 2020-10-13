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

- `scale_version`
  - example: `5.0.4.0`
  - default: none

  Specify the Spectrum Scale version that you want to install on your nodes. It is mandatory to define this variable for the following installation methods:
  - Repository installation method (`scale_install_repository_url`)
  - Local archive installation method (`scale_install_localpkg_path`)
  - Remote archive installation method (`scale_install_remotepkg_path`)

  The variable is *not* necessary for the directory installation method (`scale_install_directory`), as with this method the version is automatically detected from the installation package at the given path.
