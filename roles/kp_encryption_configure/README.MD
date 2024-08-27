# Enabling Encryption with IBM® Key Protect on IBM Storage Scale

IBM® Key Protect is a powerful service on IBM Cloud that simplifies the provisioning and storage of encrypted keys for applications across IBM Cloud services. By using IBM Key Protect, you can centralize the management of data encryption and efficiently oversee the entire key lifecycle, providing a robust foundation for securing your data on an IBM Storage Scale cluster.

## Setting Up IBM Key Protect

The first step in enabling encryption for your Storage Scale cluster file system is to create a Key Protect service. Once the service is set up, you will generate an encryption key and apply an encryption policy to your desired file system within the cluster. For a detailed guide on setting up and managing your Key Protect service, refer to the [IBM Key Protect documentation](https://cloud.ibm.com/docs/key-protect?topic=key-protect-about).

## Configuring Cluster Nodes

To ensure that every node in the cluster can access the encrypted file system, it's essential to have specific configuration files on each node. These include:

- `/var/mmfs/etc/RKM.conf`
- `/var/mmfs/etc/prefix.p12`

These files are critical for enabling secure access to the encrypted file system across the entire cluster. Without them, nodes will not be able to interact with the encrypted data.

## Understanding Secure Storage and Data Protection

Secure storage relies on encryption to render data unreadable to unauthorized users. Data is encrypted while at rest (on disk) and decrypted only when accessed by authorized users. It's important to note that encryption protects only the data itself, not the associated metadata.

IBM GPFS encryption safeguards against various threats, including disk theft or improper disposal, and unprivileged user attacks in a multi-tenant cluster. However, it does not protect against malicious actions by a cluster administrator.

In addition to securing data, GPFS encryption facilitates secure data deletion. By leveraging encryption and key management, it ensures that once the master encryption keys are deleted from the key server, the data becomes irretrievable. For more details, refer to [Encryption keys](https://www.ibm.com/docs/en/STXKQY_5.1.8/com.ibm.spectrum.scale.v5r10.doc/bl1adv_encryptionkeys.html#encryptionkeys).

## Configuring Key Protect

The `kp_encryption_configure` Ansible role automates the distribution of essential files to streamline the encryption process:

- Distributing the `.p12` and `RKM.conf` files to all servers to enable encryption.


For more in-depth information about encryption in IBM Spectrum Scale, including various encryption use cases, see the [Encryption documentation](https://www.ibm.com/docs/en/storage-scale/5.1.8?topic=administering-encryption).