Role Definition
-------------------------------
- Role name: sed
- Definition:
  - The self-encrypting drives (SED) support protects data at rest on IBM Storage Scale System drives.
  - TPM is a specialized hardware security chip that provides secure cryptographic functions.
  - mmvdisk tpm , esstpm and esstpm key provides options to setup the tpm ,generate keys, enroll drives with the generated keys in the IBM Storage Scale cluster.
  - These operations are performed on the I/O nodes and the keys generated are also backed up on the utility node.  


Prerequisite
----------------------------
- Red Hat Enterprise Linux 9.x is supported.
- OpenSSL version 3+ is supported. 
- TPM version 2.0 is required to use this support
- A password file with appropriate permissions (600) must exist for taking TPM ownership.

Design
---------------------------
- Directory Structure:
  - Path: /ibm-spectrum-scale-install-infra/roles/sed_configure
  - Inside the sed role, there are sub-tasks to setup the TPM stepwise
    - `check_prereq`: This task checks that all the prerequisites are satisfied before proceeding with the TPM setup. It checks the following things:
      - RHEL 9.x is present.
      - OpenSSL 3+ version present.
      - Check whether TPM is enabled from BIOS. 
      - Check tpm2-tools rpms. If not installed already, install it. 
    - `tpm_ownership`: This task sets up the TPM to be used.   
      - check if tpm ownership already taken, if yes skip the entire process after validating the ownership
      - if not taken, we proceed to take the ownership
      - if 'change_pasword' flag is set, we skip the setup and jump to the password change
    - `create_nv_slots`: This task create NV slots which will be used for key generation.
    - `generate_tpm_key`: This task generated a tpm key in the mentioned nv slot. 
    - `enroll_sed`: This task enrolls an sed using the tpm key
    - `manage_key`: This task handles the backup and restore of the tpm key.
