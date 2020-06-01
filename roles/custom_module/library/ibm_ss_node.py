#!/usr/bin/python
# -*- coding: utf-8 -*-

# author: IBM Corporation
# description: Highly-customizable Ansible module
# for installing and configuring IBM Spectrum Scale (GPFS)
# company: IBM
# license: Apache-2.0

ANSIBLE_METADATA = {
                       'status': ['preview'],
                       'supported_by': 'IBM',
                       'metadata_version': '1.0'
                   }


DOCUMENTATION = '''
---
module: ibm_ss_node
short_description: IBM Spectrum Scale Node Management
version_added: "0.1"

description:
    - This module can be used to add, remove or retrieve information 
      about an IBM Spectrum Scale Node(s) from the Cluster.

options:
    op:
        description:
            - An operation to execute on the IBM Spectrum Scale Node.
              Mutually exclusive with the state operand.
        required: false
    state:
        description:
            - The desired state of the Node in relation to the cluster.
        required: false
        default: "present"
        choices: [ "present", "absent" ]
    nodefile:
        description:
            - Blueprint that defines all node attributes
        required: false
    name:
        description:
            - The name of the Node to be added, removed or whose 
              information is to be retrieved
        required: false

'''

EXAMPLES = '''
# Retrive information about an existing IBM Spectrum Scale Node(s)
- name: Retrieve IBM Spectrum Scale Node information
  ibm_ss_node:
    op: list

# Adds a Node to the IBM Spectrum Scale Cluster
- name: Add node to IBM Spectrum Scale Cluster
  ibm_ss_node:
    state: present
    nodefile: "/tmp/nodefile"
    name: "node1.gpfs.ibm.com"

# Delete an existing IBM Spectrum Node from the Cluster
- name: Delete an IBM Spectrum Scale Node from Cluster
  ibm_ss_node:
    state: absent
    name: "node1.gpfs.ibm.com"
'''

RETURN = '''
changed:
    description: A boolean indicating if the module has made changes
    type: boolean
    returned: always

msg:
    description: The output from the cluster create/delete operations
    type: str
    returned: when supported

rc:
    description: The return code from the IBM Spectrum Scale mm command
    type: int
    returned: always

results:
    description: The JSON document containing the cluster information
    type: str
    returned: when supported
'''

import os
import re
import sys
import json
import time
import logging
import traceback
from ansible.module_utils.basic import AnsibleModule

try:
    from ansible.module_utils.ibm_ss_utils import runCmd, RC_SUCCESS, \
                                                  parse_aggregate_cmd_output, \
                                                  SpectrumScaleLogger, \
                                                  SpectrumScaleException
except:
    from ibm_ss_utils import runCmd, RC_SUCCESS, parse_aggregate_cmd_output, \
                             SpectrumScaleLogger, SpectrumScaleException

try:
    from ansible.module_utils.ibm_ss_disk_utils import SpectrumScaleDisk
except:
    from ibm_ss_disk_utils import SpectrumScaleDisk

try:
    from ansible.module_utils.ibm_ss_df_utils import SpectrumScaleDf
except:
    from ibm_ss_df_utils import SpectrumScaleDf

try:
    from ansible.module_utils.ibm_ss_nsd_utils import SpectrumScaleNSD
except:
    from ibm_ss_nsd_utils import SpectrumScaleNSD

try:
    from ansible.module_utils.ibm_ss_filesystem_utils import SpectrumScaleFS
except:
    from ibm_ss_filesystem_utils import SpectrumScaleFS

try:
    from ansible.module_utils.ibm_ss_cluster_utils import SpectrumScaleCluster, \
                                                          SpectrumScaleNode
except:
    from ibm_ss_cluster_utils import SpectrumScaleCluster, SpectrumScaleNode

try:
    from ansible.module_utils.ibm_ss_zimon_utils import get_zimon_collectors
except:
    from ibm_ss_zimon_utils import get_zimon_collectors

###############################################################################
##                                                                           ##
##                           Helper Functions                                ##
##                                                                           ##
###############################################################################

def get_all_nsds_of_node(instance):
    """
        This function performs "mmlsnsd -X -Y".
        Args:
            instance (str): instance for which disks are use by filesystem.
            region (str): Region of operation
        Returns:
           all_disk_names (list): Disk names in list format.
                                  Ex: [nsd_1a_1_0, nsd_1c_1_0, nsd_1c_d_1]
    """
    logger.debug("Function Entry: get_all_nsds_of_node. "
                 "Args: instance={0}".format(instance))
    nsd_list = []
    nsd_list = SpectrumScaleNSD.get_all_nsd_info()

    all_nsd_names = []
    for nsd in nsd_list:
        if nsd.get_remarks() == 'server node' and instance in nsd.get_server_list():
            all_nsd_names.append(nsd.get_name())

    logger.debug("Function Exit: get_all_nsds_of_node(). "
                 "Return Params: all_nsd_names={0} ".format(all_nsd_names))

    return all_nsd_names


def gpfs_df_disk(fs_name):
    """
        This function performs "mmdf" to obtain disk capacities.
        Args:
            fs_name (str): Filesystem name associated with the disks.
        Returns:
            disk_size_map (dict): Disk name vs. free block size vs. percent
                                  free blocks.
                                  Ex: {
                                        'nsd_1a_1_0': {'free_size': 10485760,
                                                       'used_size': 480256,
                                                       'percent': 95},
                                        'nsd_1c_1_0': {'free_size': 10485760,
                                                       'used_size': 480256,
                                                       'percent': 95}
                                      }
    """
    logger.debug("Function Entry: gpfs_df_disk(). "
                 "Args: fs_name={0}".format(fs_name))

    nsd_df_list = SpectrumScaleDf.get_df_info(fs_name)
    disk_size_map = {}
    for nsd_df in nsd_df_list:
        total = nsd_df.get_disk_size()
        free  = nsd_df.get_free_blocks()
        used  = total - free
        free_block_pct = nsd_df.get_free_blocks_pct()
        disk  = nsd_df.get_nsd_name()
        disk_size_map[disk] = {
                                  'free_size': free, 
                                  'used_size': used,
                                  'percent': free_block_pct
                              }

    logger.debug("Function Exit: gpfs_df_disk(). "
                 "Return Params: disk_size_map={0} ".format(disk_size_map))

    return disk_size_map


def get_node_nsd_info():
    logger.debug("Function Entry: get_node_nsd_info().")

    nsd_list = SpectrumScaleNSD.get_all_nsd_info()

    node_nsd_map = {}
    nsd_node_map = {}

    for nsd in nsd_list:
        if  nsd.get_remarks() == 'server node':
            # Populate the node_nsd_map data structure
            nsd_list = []
            for node_name in nsd.get_server_list():
                if node_name in node_nsd_map.keys():
                    nsd_list = node_nsd_map[node_name]
                nsd_list.append(nsd.get_name())
                node_nsd_map[node_name] = nsd_list
            
            # Populate the nsd_node_map data structure
            host_list = []
            if nsd.get_name() in nsd_node_map.keys():
                host_list = nsd_node_map[nsd.get_name()]
            for server in nsd.get_server_list():
                host_list.append(server)
            nsd_node_map[nsd.get_name()] = host_list 

    logger.debug("Function Exit: get_node_nsd_info(). "
                 "Return Params: node_nsd_map={0} "
                 "nsd_node_map={1}".format(node_nsd_map, nsd_node_map))

    return node_nsd_map, nsd_node_map


###############################################################################
##                                                                           ##
##               Functions to remove node(s) from cluster                    ##
##                                                                           ##
###############################################################################

#
# Retrieve the mapping of Filesystems to NSDs
#
# Returns:
#     fs_to_nsd_map (dict): Dict of fs names vs. disk names
#                   Ex: {'fs1': ['gpfs1nsd', 'gpfs2nsd'],
#                        'fs2': ['gpfs3nsd', 'gpfs4nsd']}
#
def get_filesystem_to_nsd_mapping():
    logger.debug("Function Entry: get_filesystem_to_nsd_mapping().")

    fs_to_nsd_map = {}

    # Retrieve all filesystems on this cluster
    fs_instance_list = SpectrumScaleFS.get_filesystems()

    # For each filesystem, determine the Filesystem to NSD mapping
    for fs in fs_instance_list:

        # Get all NSDs for this Filesystem
        nsds_for_fs = SpectrumScaleDisk.get_all_disk_info(fs.get_device_name())

        for nsd in nsds_for_fs:
            nsd_list = []

            # If an entry already exists for the File system, then
            # simply add the new NSD to the list
            if fs.get_device_name() in fs_to_nsd_map.keys():
                nsd_list = fs_to_nsd_map[fs.get_device_name()]

            nsd_list.append(nsd.get_nsd_name())
            fs_to_nsd_map[fs.get_device_name()] = nsd_list

    logger.debug("Function Exit: get_filesystem_to_nsd_mapping(). "
                 "Return Params: fs_to_nsd_map={0} ".format(fs_to_nsd_map))

    return fs_to_nsd_map


def check_nodes_exist(nodes_to_be_deleted):
    logger.debug("Function Entry: check_nodes_exist(). "
                 "Args: nodes_to_be_deleted={0}".format(nodes_to_be_deleted))

    filtered_nodes_to_be_deleted = []
    existing_node_list = SpectrumScaleCluster().get_nodes()
    for node_to_del in nodes_to_be_deleted:
        for existing_node in existing_node_list:
            if (node_to_del in existing_node.get_daemon_node_name() or
                node_to_del in existing_node.get_admin_node_name()  or
                node_to_del in existing_node.get_ip_address()):
                filtered_nodes_to_be_deleted.append(existing_node)

    logger.debug("Function Exit: check_nodes_exist(). "
                 "Return Params: filtered_nodes_to_be_deleted="
                 "{0} ".format(filtered_nodes_to_be_deleted))

    return filtered_nodes_to_be_deleted
        

def check_roles_before_delete(existing_node_list_to_del):
    logger.debug("Function Entry: check_roles_before_delete(). "
                 "Args: existing_node_list_to_del="
                 "{0}".format(existing_node_list_to_del))

    for node_to_del in existing_node_list_to_del:
        # Do not delete nodes that are designated as "quorum", "manager",
        # "gateway", "ces", "TCT", "SNMP"
        if (node_to_del.is_quorum_node()  or
            node_to_del.is_manager_node() or
            node_to_del.is_gateway_node() or
            node_to_del.is_ces_node()     or
            node_to_del.is_tct_node()     or
            node_to_del.is_snmp_node()):
            exp_msg = ("Cannot remove node {0} since it is designated "
                       "as either a quorum, gateway, CES, TCT or SNMP "
                       "node. Re-run the current command without "
                       "{1}".format(node_to_del.get_admin_node_name(),
                                    node_to_del.get_admin_node_name()))
            raise SpectrumScaleException(exp_msg, "", [], -1, "", "")

    # TODO: Should we also check the Zimon Collector Nodes
    # zimon_col_nodes = get_zimon_collectors()

    logger.debug("Function Exit: check_roles_before_delete().")


def remove_multi_attach_nsd(nodes_to_be_deleted):
    logger.debug("Function Entry: remove_multi_attach_nsd(). "
                 "Args nodes_to_be_deleted={0}".format(nodes_to_be_deleted))

    # Iterate through each server to be deleted 
    node_map, nsd_map = get_node_nsd_info()
    for node_to_delete in nodes_to_be_deleted:
        logger.debug("Processing all NSDs on node={0} for "
                     "removal".format(node_to_delete.get_admin_node_name()))
        #node_map, nsd_map = get_node_nsd_info()

        # Check if the node to be deleted has access to any NSDs
        #if node_to_delete in node_map.keys():
        if node_to_delete.get_admin_node_name() in node_map.keys():
            nsds_to_delete_list = node_map[node_to_delete.get_admin_node_name()]

            # For each Node, check all the NSDS it has access to. If the 
            # Node has access to an NSD that can also be accessed from other
            # NSD servers, then we can simply modify the server access list 
            # through the mmchnsd command
            for nsd_to_delete in nsds_to_delete_list: 
                # Clone list to avoid modifying original content
                nsd_attached_to_nodes = (nsd_map[nsd_to_delete])[:]
                nsd_attached_to_nodes.remove(node_to_delete.get_admin_node_name())
                if len(nsd_attached_to_nodes) >= 1:
                    # This node has access to an NSD, that can also be 
                    # accessed by other NSD servers. Therefore modify the 
                    # server access list
                    SpectrumScaleNSD.remove_server_access_to_nsd(nsd_to_delete, 
                                                node_to_delete.get_admin_node_name(),
                                                nsd_attached_to_nodes)
   
    # All "mmchnsd" calls are asynchronous. Therefore wait here till all 
    # modifications are committed before proceeding further. For now just
    # sleep but we need to enhance this to ensure the async op has completed
    time.sleep(30)

    logger.debug("Function Exit: remove_multi_attach_nsd(). ")


#
# This function performs removal / termination of nodes from the IBM Spectrum
# Scale cluster. If the node is a server node that has access to NSD(s), then
# we attempt to remove access to this NSD (if the NSD is a shared NSD) or 
# delete access to it (if its a dedicated NSD).
#
# Args: 
#   node_names_to_delete: Nodes to be deleted from the cluster
#
# Return:
#   rc: Return code
#   msg: Output message
def remove_nodes(node_names_to_delete):
    logger.debug("Function Entry: remove_nodes(). "
                 "Args: node_list={0}".format(node_names_to_delete))

    rc = RC_SUCCESS
    msg = ""
    removed_node_list = []

    # Check that the list of nodes to delete already exist. If not, 
    # simply ignore
    nodes_to_delete = check_nodes_exist(node_names_to_delete)

    if len(nodes_to_delete) == 0:
        msg = str("Nodes specified for deletion: {0} do not exist "
                  "in the cluster".format(node_names_to_delete))
        return rc, msg

    # Precheck nodes to make sure they do not have any roles that should
    # not be deleted
    check_roles_before_delete(nodes_to_delete)

    # An NSD node can have access to a multi attach NSD (shared NSD) or
    # dedicated access to the NSD (FPO model) or a combination of both.

    # First modify the Shared NSDs and remove access to all NSD Nodes 
    # that are to be deleted. Note: As long as these are Shared NSD's
    # another NSD server will continue to have access to the NSD (and 
    # therefore Data)
    remove_multi_attach_nsd(nodes_to_delete)

    # Finally delete any dedicated NSDs (this will force the data to be
    # copied to another NSD in the same Filesystem). Finally delete the
    # node from the cluster

    # For each Filesystem, Get the Filesystem to NSD (disk) mapping
    fs_nsd_map = get_filesystem_to_nsd_mapping()

    logger.debug("Identified all filesystem to disk mapping: %s",
                 fs_nsd_map)
    
    for node_to_del_obj in nodes_to_delete:
        node_to_del = node_to_del_obj.get_admin_node_name()
        logger.debug("Operating on server: %s", node_to_del)
        
        # For each node to be deleted, retrieve the NSDs (disks) on the node
        all_node_disks = get_all_nsds_of_node(node_to_del)
        logger.debug("Identified disks for server (%s): %s", node_to_del,
                     all_node_disks)

        # The Node does not have any disks on it (compute node). Delete the
        # node without any more processing
        if len(all_node_disks) == 0:
            SpectrumScaleFS.unmount_filesystems(node_to_del, wait=True)
            SpectrumScaleNode.shutdown_node(node_to_del, wait=True)
            SpectrumScaleCluster.delete_node(node_to_del)
            continue
   
        # Generate a list of NSD (disks) on the host to be deleted for
        # each filesystem
        #
        # fs_disk_map{} contains the following:
        #    Filesystem Name -> NSDs on the host to be deleted
        fs_disk_map = {}
        for fs_name, disks in fs_nsd_map.iteritems():
            node_specific_disks = []
            for disk in disks:
                if disk in all_node_disks:
                    node_specific_disks.append(disk)
            fs_disk_map[fs_name] = node_specific_disks

        logger.debug("Identified filesystem to disk map for server (%s): %s",
                     node_to_del, fs_disk_map)

        for fs in fs_disk_map:
            disk_cap = gpfs_df_disk(fs)
            logger.debug("Identified disk capacity for filesystem (%s): %s",
                         fs, disk_cap)
            # Algorithm used for checking at-least 20% free space during
            # mmdeldisk in progress;
            # - Identify the size of data stored in disks going to be
            #   deleted.
            # - Identify the free size of the filesystem
            #   (excluding the disk going to be deleted)
            # - Allow for disk deletion, if total_free size is 20% greater
            #   even after moving used data stored in disk going to be deleted.
            size_to_be_del = 0
            for disk in fs_disk_map[fs]:
                size_to_be_del += disk_cap[disk]['used_size']
            logger.debug("Identified data size going to be deleted from "
                         "filesystem (%s): %s", fs, size_to_be_del)

            other_disks = []
            for disk_name in disk_cap:
                if disk_name not in fs_disk_map[fs]:
                    other_disks.append(disk_name)
            logger.debug("Identified other disks of the filesystem (%s): %s",
                         fs, other_disks)

            size_avail_after_migration, total_free = 0, 0
            for disk in other_disks:
                # Accumulate free size on all disks.
                total_free += disk_cap[disk]['free_size']
                logger.debug("Identified free size in other disks of the "
                             "filesystem (%s): %s", fs, total_free)

            size_avail_after_migration = total_free - size_to_be_del
            logger.debug("Expected size after restriping of the filesystem "
                         "(%s): %s", fs, size_avail_after_migration)

            percent = int(size_avail_after_migration*100/total_free)
            logger.debug("Expected percentage of size left after restriping "
                         "of the filesystem (%s): %s", fs, percent)

            if percent < 20:
                logger.error("No enough space left for restriping data for "
                             "filesystem (%s). Execution halted!", fs)
                msg = ("No enough space left for restriping data for "
                       "filesystem {0}".format(fs))
                raise SpectrumScaleException(msg, "", -1, "", "")

            if fs_disk_map[fs]:
                # mmdeldisk will not be hit if there are no disks to delete.
                SpectrumScaleDisk.delete_disk(node_to_del, fs, fs_disk_map[fs])

        if all_node_disks:
            # mmdelnsd will not be hot if there are no disks to delete.
            SpectrumScaleNSD.delete_nsd(all_node_disks)

        SpectrumScaleFS.unmount_filesystems(node_to_del, wait=True)
        SpectrumScaleNode.shutdown_node(node_to_del, wait=True)
        SpectrumScaleCluster.delete_node(node_to_del)
        removed_node_list.append(node_to_del)
        
    msg = str("Successfully removed node(s) {0} from the "
              "cluster".format(removed_node_list))

    logger.debug("Function Exit: remove_nodes(). "
                 "Return Params: rc={0} msg={1}".format(rc, msg))

    return rc, msg


###############################################################################
##                                                                           ##
##               Functions to retrieve Node information                      ##
##                                                                           ##
###############################################################################

def get_node_info_as_json(node_names):
    logger.debug("Function Entry: get_node_info_as_json(). "
                 "Args: node_names={0}".format(node_names))

    rc = 0
    msg = result_json = ""
    node_info_list = []

    cluster = SpectrumScaleCluster()
    node_instance_list = cluster.get_nodes()

    for node_instance in node_instance_list:
        node_info_list.append(node_instance.get_node_dict())

    result_json = json.dumps(node_info_list)
    msg = "List cluster successfully executed"

    logger.debug("Function Exit: get_node_info_as_json(). "
                 "Return Params: rc={0} msg={1} "
                 "result_json={2}".format(rc, msg, result_json))

    return rc, msg, result_json


###############################################################################
##                                                                           ##
##                              Main Function                                ##
##                                                                           ##
###############################################################################

def main():
    logger.debug("----------------------------------")
    logger.debug("Function Entry: ibm_ss_node.main()")
    logger.debug("----------------------------------")

    # Setup the module argument specifications
    scale_arg_spec = dict(
                           op       = dict(
                                            type='str', 
                                            choices=['get'], 
                                            required=False
                                          ),
                           state    = dict(
                                            type='str', 
                                            choices=['present', 'absent'], 
                                            required=False
                                          ),
                           nodefile = dict(
                                            type='str', 
                                            required=False
                                          ),
                           name     = dict(
                                            type='str', 
                                            required=False
                                          )
                         )


    scale_req_args        = [
                              [ "state", "present", [ "stanza", "name" ] ],
                              [ "state", "absent", [ "name" ] ],
                              [ "op", "get", [ "name" ] ]
                            ]


    scale_req_one_of_args = [
                              [ "op", "state" ]
                            ]

    # Instantiate the Ansible module with the given argument specifications
    module = AnsibleModule(
                            argument_spec=scale_arg_spec,
                            required_one_of=scale_req_one_of_args,
                            required_if=scale_req_args,
                          )

    rc = RC_SUCCESS
    msg = result_json = ""
    state_changed = False

    if module.params['op'] and "get" in module.params['op']:
        # Retrieve the IBM Spectrum Scale node information
        node_name_str = module.params['name']
        rc, msg, result_json = get_node_info_as_json(node_name_str.split(','))
    elif module.params['state']:
        if "present" in module.params['state']:
            # Create a new IBM Spectrum Scale cluster
            rc, msg = SpectrumScaleCluster.add_node(
                                         module.params['name'],
                                         module.params['stanza']
                                     )
        else:
            listofserver = module.params['name']

            # Delete the existing IBM Spectrum Scale cluster
            try:
                rc, msg = remove_nodes(listofserver.split(','))
            except Exception as e:
                st = traceback.format_exc()
                e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
                module.fail_json(msg=e_msg)

        if rc == RC_SUCCESS:
            state_changed = True

    logger.debug("---------------------------------")
    logger.debug("Function Exit: ibm_ss_node.main()")
    logger.debug("---------------------------------")

    # Module is done. Return back the result
    module.exit_json(changed=state_changed, msg=msg, rc=rc, result=result_json)


if __name__ == '__main__':
    logger = SpectrumScaleLogger.get_logger()
    main() 
