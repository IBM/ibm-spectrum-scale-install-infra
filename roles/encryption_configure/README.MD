# Enabling encryption by using GKLM

The Spectrum Scale cluster file system can be encrypted by using the IBM Security® Guardium® Key Lifecycle Manager (GKLM). You can enable encryption features during deployment. The encryption provides highly available key servers for cryptographic operations on the GPFS file system.

GPFS provides support for file encryption that ensures both secure storage and secure deletion of data. GPFS manages encryption through the use of encryption keys and encryption policies.

**Note:**  File encryption is available with IBM Storage Scale Advanced Edition, IBM Storage Scale Data Management Edition, or IBM Storage Scale Developer Edition or IBM Storage Scale Erasure Code Edition. The file system must be at GPFS 4.1 or later. Encryption is supported in the following environments:

- Multicluster environments (provided that the remote nodes have their own /var/mmfs/etc/RKM.conf files and access to the remote key management servers. For more information, see [Encryption keys](https://www.ibm.com/docs/en/STXKQY_5.1.8/com.ibm.spectrum.scale.v5r10.doc/bl1adv_encryptionkeys.html#encryptionkeys).)
- FPO environments

Secure storage uses encryption to make data unreadable to anyone who does not possess the necessary encryption keys. The data is encrypted while "at rest" (on disk) and is decrypted on the way to the reader. Only data, not metadata, is encrypted.

GPFS encryption can protect against attacks targeting the disks (for example, theft or acquisition of improperly discarded disks) as well as attacks performed by unprivileged users of a GPFS node in a multi-tenant cluster (that is, a cluster that stores data belonging to multiple administrative entities called tenants). However, it cannot protect against deliberate malicious acts by a cluster administrator.

Secure data deletion leverages encryption and key management to guarantee erasure of files beyond the physical and logical limitations of normal deletion operations. If data is encrypted, and the master key (or keys) required to decrypt it have been deleted from the key server, that data is effectively no longer retrievable. See [Encryption keys](https://www.ibm.com/docs/en/STXKQY_5.1.8/com.ibm.spectrum.scale.v5r10.doc/bl1adv_encryptionkeys.html#encryptionkeys).

# Integration of GKLM with Scale Cluster:

The Ansible role for the encryption configure will do the below automation process,

- The key servers are added to each cluster (storage and compute).
- Tenants and clients are created on each cluster.
- The master key is created for encrypting the file system.
- An encryption policy is created and applied to the file system.

The storage and compute clusters have access to the encrypted file system, and any files that are created on the file system are encrypted.

**Verifying encryption on the file system**

1. Log in to any of the clusters (storage or compute nodes) by running the following SSH command: 

    ```ssh
    ssh -J root@BASTION_SERVER vpcuser@STORAGE_NODE
    ```

2. List the key server that was added to the cluster by running the following command:

    ```text
    mmkeyserver server show
    ```

3. List the key components, for example tenant or client, by running the following commands:

    ```text
    mmkeyserver tenant show
    ```

    ```text
    mmmkeyserver client show
    ```

4. Validate the policy that was applied to the cluster by running the following command:

    ```text
    mmlspolicy FILESYSTEM_NAME -L
    ```

5. Check the encrypted file by running the following command:

    ```text
    mmlsattr -n gpfs.Encryption FILE_NAME
    ```

To learn more about encryption for Spectrum Scale or different encryption use cases, see [Encryption](https://www.ibm.com/docs/en/storage-scale/5.1.8?topic=administering-encryption)