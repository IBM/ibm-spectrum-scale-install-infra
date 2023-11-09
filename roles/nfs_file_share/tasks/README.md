**NFS File Share**

Use the mmnfs export commands to add, change, list, load, or remove NFS export declarations for IP addresses on nodes that are configured as CES types.

For more information, see https://www.ibm.com/docs/en/storage-scale/5.1.8?topic=reference-mmnfs-command

**Create NFS export**
Name: Create NFS export
Description: If the NFS export list does not exist, this task creates the export with specified configurations.
Command: /usr/lpp/mmfs/bin/mmnfs export add {{ scale_protocols.mountpoint }}/{{ item.item.key }} --client "{{ client_subnet_cidr }}(Access_Type=RW,SQUASH=no_root_squash)"

scale_protocols.mountpoint = existing file system.
compute_subnet_cidr = client cluster subnet cider block

**Check NFS export list**
Name: Check NFS export list
Description: This task retrieves the NFS export list for validation purposes.
Command: /usr/lpp/mmfs/bin/mmnfs export list