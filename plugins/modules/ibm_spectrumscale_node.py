#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2020 IBM Corporation
# and other contributors as indicated by the @author tags.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

ANSIBLE_METADATA = {
                       'status': ['preview'],
                       'supported_by': 'IBM',
                       'metadata_version': '1.0'
                   }


DOCUMENTATION = '''
---
module: ibm_spectrumscale_node
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
  ibm_spectrumscale_node:
    op: list

# Adds a Node to the IBM Spectrum Scale Cluster
- name: Add node to IBM Spectrum Scale Cluster
  ibm_spectrumscale_node:
    state: present
    nodefile: "/tmp/nodefile"
    name: "node1.domain.com"

# Delete an existing IBM Spectrum Node from the Cluster
- name: Delete an IBM Spectrum Scale Node from Cluster
  ibm_spectrumscale_node:
    state: absent
    name: "node1.domain.com"
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

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_utils import runCmd, RC_SUCCESS, \
                                                  parse_aggregate_cmd_output, \
                                                  SpectrumScaleLogger, \
                                                  SpectrumScaleException

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_disk_utils import SpectrumScaleDisk

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_df_utils import SpectrumScaleDf

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_nsd_utils import SpectrumScaleNSD

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_filesystem_utils import SpectrumScaleFS

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_cluster_utils import SpectrumScaleCluster, \
                                                          SpectrumScaleNode

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_zimon_utils import get_zimon_collectors

###############################################################################
##                                                                           ##
##                           Helper Functions                                ##
##                                                                           ##
###############################################################################

def get_all_nsds_of_node(logger, instance):
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


def gpfs_df_disk(logger, fs_name):
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


def get_node_nsd_info(logger):
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
#     fs_to_nsd_map (dict): Dict of fs names and SpectrumScaleDisk objects
#
def get_filesystem_to_nsd_mapping(logger):
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

            nsd_list.append(nsd)
            fs_to_nsd_map[fs.get_device_name()] = nsd_list

    logger.debug("Function Exit: get_filesystem_to_nsd_mapping(). "
                 "Return Params: fs_to_nsd_map={0} ".format(fs_to_nsd_map))

    return fs_to_nsd_map


def check_cluster_health(logger):
    logger.debug("Function Entry: check_cluster_health(). ")

    unhealthy_nodes = []
    all_nodes_state = SpectrumScaleNode.get_state()
   
    for node_name, state in all_nodes_state.iteritems():
        if ("down" in state or
            "arbitrating" in state or
            "unknown" in state):
            unhealthy_nodes.append(node_name)

    if unhealthy_nodes:
        unhealthy_nodes_str = ' '.join(map(str, unhealthy_nodes))
        error_msg = ("The following node(s) \"{0}\" is(are) currently not up. "
                     "Ensure all nodes in the cluster are fully operational "
                     "before retrying the operation.".format(unhealthy_nodes_str))
        logger.error(error_msg)
        raise SpectrumScaleException(error_msg, "", [], -1, "", "")

    logger.debug("Function Exit: check_cluster_health(). ")


def check_nodes_exist(logger, nodes_to_be_deleted):
    logger.debug("Function Entry: check_nodes_exist(). "
                 "Args: nodes_to_be_deleted={0}".format(nodes_to_be_deleted))

    logger.info("Checking if node(s) marked for removal exist in the cluster")
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
        

def check_roles_before_delete(logger, existing_node_list_to_del):
    logger.debug("Function Entry: check_roles_before_delete(). "
                 "Args: existing_node_list_to_del="
                 "{0}".format(existing_node_list_to_del))

    logger.info("Checking the designations for all nodes marked for removal")

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
            logger.error(exp_msg)
            raise SpectrumScaleException(exp_msg, "", [], -1, "", "")

    # TODO: Should we also check the Zimon Collector Nodes
    # zimon_col_nodes = get_zimon_collectors()

    logger.debug("Function Exit: check_roles_before_delete().")


def check_disk_health(logger, fs_nsd_map):
    logger.debug("Function Entry: check_disk_health(). "
                 "Args fs_nsd_map={0}".format(fs_nsd_map))

    unhealthy_disks = []
    for fs_name, disk_list in fs_nsd_map.iteritems():
        for disk in disk_list:
            if "down" in disk.get_availability():
                unhealthy_disks.append(disk.get_nsd_name())

    if unhealthy_disks:
        unhealthy_disks_str = ' '.join(map(str, unhealthy_disks))
        error_msg = ("The following disks \"{0}\" are currently not healthy. "
                     "Ensure all disks in the cluster are healthy before "
                     "retrying the operation.".format(unhealthy_disks_str))
        logger.error(error_msg)
        raise SpectrumScaleException(error_msg, "", [], -1, "", "")

    logger.debug("Function Exit: check_disk_health(). ")


def remove_multi_attach_nsd(logger, nodes_to_be_deleted):
    logger.debug("Function Entry: remove_multi_attach_nsd(). "
                 "Args nodes_to_be_deleted={0}".format(nodes_to_be_deleted))

    logger.info("Checking node(s) for multi-node attached NSD(s)")

    # Iterate through each server to be deleted 
    node_map, nsd_map = get_node_nsd_info(logger)
    for node_to_delete in nodes_to_be_deleted:
        logger.debug("Processing all NSDs on node={0} for "
                     "removal".format(node_to_delete.get_admin_node_name()))
        #node_map, nsd_map = get_node_nsd_info(logger)

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
                    logger.info("Removing server access to NSD {0} from node "
                                "{1}".format(nsd_to_delete, 
                                             node_to_delete.get_admin_node_name()))
                    SpectrumScaleNSD.remove_server_access_to_nsd(nsd_to_delete, 
                                                node_to_delete.get_admin_node_name(),
                                                nsd_attached_to_nodes)
   
    # All "mmchnsd" calls are asynchronous. Therefore wait here till all 
    # modifications are committed before proceeding further. For now just
    # sleep but we need to enhance this to ensure the async op has completed
    time.sleep(10)

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
def remove_nodes(logger, node_names_to_delete):
    logger.debug("Function Entry: remove_nodes(). "
                 "Args: node_list={0}".format(node_names_to_delete))

    rc = RC_SUCCESS
    msg = result_json = ""
    removed_node_list = []

    logger.info("Attempting to remove node(s) {0} from the "
                "cluster".format(' '.join(map(str, node_names_to_delete))))

    # Ensure all nodes in the cluster are healthy
    check_cluster_health(logger)

    # Check that the list of nodes to delete already exist. If not, 
    # simply ignore
    nodes_to_delete = check_nodes_exist(logger, node_names_to_delete)

    if len(nodes_to_delete) == 0:
        msg = str("All node(s) marked for removal ({0}) are already not part "
                  "of the cluster".format(' '.join(map(str, 
                                                   node_names_to_delete))))
        logger.info(msg)
        return rc, msg, result_json

    # Precheck nodes to make sure they do not have any roles that should
    # not be deleted
    check_roles_before_delete(logger, nodes_to_delete)

    # For each Filesystem, Get the Filesystem to NSD (disk) mapping
    fs_nsd_map = get_filesystem_to_nsd_mapping(logger)

    check_disk_health(logger, fs_nsd_map)

    # An NSD node can have access to a multi attach NSD (shared NSD) or
    # dedicated access to the NSD (FPO model) or a combination of both.

    # First modify the Shared NSDs and remove access to all NSD Nodes 
    # that are to be deleted. Note: As long as these are Shared NSD's
    # another NSD server will continue to have access to the NSD (and 
    # therefore Data)
    remove_multi_attach_nsd(logger, nodes_to_delete)

    # Finally delete any dedicated NSDs (this will force the data to be
    # copied to another NSD in the same Filesystem). Finally delete the
    # node from the cluster

    logger.debug("Identified all filesystem to disk mapping: "
                 "{0}".format(fs_nsd_map))
    
    for node_to_del_obj in nodes_to_delete:
        node_to_del = node_to_del_obj.get_admin_node_name()
        logger.debug("Operating on server: {0}".format(node_to_del))
        
        # For each node to be deleted, retrieve the NSDs (disks) on the node
        all_node_disks = get_all_nsds_of_node(logger, node_to_del)
        logger.debug("Identified disks for server ({0}): "
                     "{1}".format(node_to_del, all_node_disks))

        # The Node does not have any disks on it (compute node). Delete the
        # node without any more processing
        if len(all_node_disks) == 0:
            logger.info("Unmounting filesystem(s) on {0}".format(node_to_del))
            SpectrumScaleFS.unmount_filesystems(node_to_del, wait=True)

            logger.info("Shutting down node {0}".format(node_to_del))
            SpectrumScaleNode.shutdown_node(node_to_del, wait=True)

            logger.info("Deleting compute node {0}".format(node_to_del))
            SpectrumScaleCluster.delete_node(node_to_del)

            removed_node_list.append(node_to_del)
            continue
   
        # Generate a list of NSD (disks) on the host to be deleted for
        # each filesystem
        #
        # fs_disk_map{} contains the following:
        #    Filesystem Name -> NSDs on the host to be deleted
        fs_disk_map = {}
        for fs_name, disks in fs_nsd_map.iteritems():
            node_specific_disks = []
            for disk_instance in disks:
                if disk_instance.get_nsd_name() in all_node_disks:
                    node_specific_disks.append(disk_instance.get_nsd_name())
            fs_disk_map[fs_name] = node_specific_disks

        logger.debug("Identified filesystem to disk map for server "
                     "({0}): {1}".format(node_to_del, fs_disk_map))

        for fs in fs_disk_map:
            disk_cap = gpfs_df_disk(logger, fs)
            logger.debug("Identified disk capacity for filesystem "
                         "({0}): {1}".format(fs, disk_cap))

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
                         "filesystem ({0}): {1}".format(fs, size_to_be_del))

            other_disks = []
            for disk_name in disk_cap:
                if disk_name not in fs_disk_map[fs]:
                    other_disks.append(disk_name)
            logger.debug("Identified other disks of the filesystem "
                         "({0}): {1}".format(fs, other_disks))

            if not other_disks:
                msg = str("No free disks available to restripe data "
                          "for the filesystem {0}".format(fs))
                logger.error(msg)
                raise SpectrumScaleException(msg=msg, mmcmd="", cmdargs=[], 
                                             rc=-1, stdout="", stderr="")

            size_avail_after_migration, total_free = 0, 0
            for disk in other_disks:
                # Accumulate free size on all disks.
                total_free += disk_cap[disk]['free_size']
                logger.debug("Identified free size in other disks of the "
                             "filesystem ({0}): {1}".format(fs, total_free))

            size_avail_after_migration = total_free - size_to_be_del
            logger.debug("Expected size after restriping of the filesystem "
                         "({0}): {1}".format(fs, size_avail_after_migration))

            percent = int(size_avail_after_migration*100/total_free)
            logger.debug("Expected percentage of size left after restriping "
                         "of the filesystem ({0}): {1}".format(fs, percent))

            if percent < 20:
                msg = ("Not enough space left for restriping data for "
                       "filesystem {0}".format(fs))
                logger.error(msg)
                raise SpectrumScaleException(msg=msg, mmcmd="", cmdargs=[], 
                                             rc=-1, stdout="", stderr="")

            if fs_disk_map[fs]:
                # mmdeldisk will not be hit if there are no disks to delete.
                logger.info("Deleting disk(s) {0} from node "
                            "{1}".format(' '.join(map(str, fs_disk_map[fs])), 
                                         node_to_del))
                SpectrumScaleDisk.delete_disk(node_to_del, fs, fs_disk_map[fs])

        if all_node_disks:
            # mmdelnsd will not be hot if there are no disks to delete.
            logger.info("Deleting all NSD(s) {0} attached to node "
                        "{1}".format(' '.join(map(str, all_node_disks)), 
                                     node_to_del))
            SpectrumScaleNSD.delete_nsd(all_node_disks)

        logger.info("Unmounting filesystem(s) on {0}".format(node_to_del))
        SpectrumScaleFS.unmount_filesystems(node_to_del, wait=True)

        logger.info("Shutting down node {0}".format(node_to_del))
        SpectrumScaleNode.shutdown_node(node_to_del, wait=True)

        logger.info("Deleting storage node {0}".format(node_to_del))
        SpectrumScaleCluster.delete_node(node_to_del)

        removed_node_list.append(node_to_del)
        
    msg = str("Successfully removed node(s) {0} from the "
              "cluster".format(' '.join(map(str, removed_node_list))))

    logger.info(msg)
    logger.debug("Function Exit: remove_nodes(). "
                 "Return Params: rc={0} msg={1}".format(rc, msg))

    return rc, msg, result_json


###############################################################################
##                                                                           ##
##               Functions to retrieve Node information                      ##
##                                                                           ##
###############################################################################

def get_node_info_as_json(logger, node_names=[]):
    logger.debug("Function Entry: get_node_info_as_json(). "
                 "Args: node_names={0}".format(node_names))

    rc = 0
    msg = result_json = ""
    node_info_dict = {}
    node_info_list = []

    cluster = SpectrumScaleCluster()
    node_instance_list = cluster.get_nodes()

    for node_instance in node_instance_list:
        if len(node_names) == 0:
            node_info_list.append(node_instance.get_node_dict())
        else:
            if (node_instance.get_ip_address() in node_names or
                node_instance.get_admin_node_name() in node_names or
                node_instance.get_daemon_node_name() in node_names):
                node_info_list.append(node_instance.get_node_dict())

    node_info_dict["clusterNodes"] = node_info_list
    result_json = json.dumps(node_info_dict)
    msg = "List cluster successfully executed"

    logger.debug("Function Exit: get_node_info_as_json(). "
                 "Return Params: rc={0} msg={1} "
                 "result_json={2}".format(rc, msg, result_json))

    return rc, msg, result_json


def get_node_status_as_json(logger, node_names=[]):
    logger.debug("Function Entry: get_node_status_as_json(). "
                 "Args: node_names={0}".format(node_names))

    rc = 0
    msg = result_json = ""
    node_status = {}

    node_state = SpectrumScaleNode.get_state(node_names)
    result_json = json.dumps(node_state)
    msg = "Cluster status successfully executed"

    logger.debug("Function Exit: get_node_status_as_json(). "
                 "Return Params: rc={0} msg={1} "
                 "result_json={2}".format(rc, msg, result_json))

    return rc, msg, result_json


###############################################################################
##                                                                           ##
##           Functions to Stop/Start Node(s) in the Cluster                  ##
##                                                                           ##
###############################################################################

def start_nodes(logger, node_names):
    logger.debug("Function Entry: start_nodes(). "
                 "Args: node_names={0}".format(node_names))

    rc = RC_SUCCESS
    msg = stdout = result_json = ""

    for node in node_names:
        logger.info("Attempting to start node {0}".format(node))
        rc, stdout = SpectrumScaleNode.start_node(node, wait=True)

    msg = str("Successfully started node(s) "
              "{0}".format(' '.join(map(str, node_names))))

    logger.info(msg)

    logger.debug("Function Exit: start_nodes(). "
                 "Return Params: rc={0} msg={1} "
                 "result_json={2}".format(rc, msg, result_json))

    return rc, msg, result_json


def stop_nodes(logger, node_names):
    logger.debug("Function Entry: stop_nodes(). "
                 "Args: node_names={0}".format(node_names))

    rc = RC_SUCCESS
    msg = stdout = result_json = ""

    for node in node_names:
        logger.info("Attempting to stop node {0}".format(node))
        rc, stdout = SpectrumScaleNode.shutdown_node(node, wait=True)

    msg = str("Successfully stopped node(s) "
              "{0}".format(' '.join(map(str, node_names))))

    logger.info(msg)

    logger.debug("Function Exit: stop_nodes(). "
                 "Return Params: rc={0} msg={1} "
                 "result_json={2}".format(rc, msg, result_json))

    return rc, msg, result_json


###############################################################################
##                                                                           ##
##               Functions to add Node(s) to the Cluster                     ##
##                                                                           ##
###############################################################################

def add_nodes(logger, node_names, stanza, license):
    logger.debug("Function Entry: add_nodes(). "
                 "Args: node_names={0}".format(node_names))

    rc = RC_SUCCESS
    msg = stdout = result_json = ""

    logger.info("Attempting to add node(s) {0} to the "
                "cluster".format(' '.join(map(str, node_names))))

    rc, stdout, stderr = SpectrumScaleCluster.add_node(node_names, stanza)

    logger.info("Attempting to apply licenses to newly added "
                "node(s)".format(' '.join(map(str, node_names))))

    rc, stdout = SpectrumScaleCluster.apply_license(node_names, license)

    for node in node_names:
        logger.info("Attempting to start node {0}".format(node))
        rc, stdout = SpectrumScaleNode.start_node(node, wait=True)

    msg = str("Successfully added node(s) {0} to the "
              "cluster".format(' '.join(map(str, node_names))))

    logger.info(msg)

    logger.debug("Function Exit: add_nodes(). "
                 "Return Params: rc={0} msg={1} "
                 "result_json={2}".format(rc, msg, result_json))

    return rc, msg, result_json


###############################################################################
##                                                                           ##
##                              Main Function                                ##
##                                                                           ##
###############################################################################

def main():
    logger = SpectrumScaleLogger.get_logger()

    logger.debug("----------------------------------")
    logger.debug("Function Entry: ibm_spectrumscale_node.main()")
    logger.debug("----------------------------------")

    # Setup the module argument specifications
    scale_arg_spec = dict(
                           op       = dict(
                                            type='str', 
                                            choices=['get', 'status', 'start', 'stop'], 
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
                                          ),
                           license  = dict(
                                            type='str', 
                                            choices=['server', 'client', 'fpo'], 
                                            required=False
                                          ),
                         )


    scale_req_args        = [
                              [ "state", "present", [ "nodefile", "name", "license" ] ],
                              [ "state", "absent", [ "name" ] ]
                            ]


    scale_req_one_of_args = [
                              [ "op", "state" ]
                            ]

    scale_mutual_ex_args  = [
                              [ "get", "status", "start", "stop" ]
                            ]

    # Instantiate the Ansible module with the given argument specifications
    module = AnsibleModule(
                            argument_spec=scale_arg_spec,
                            required_one_of=scale_req_one_of_args,
                            required_if=scale_req_args,
                            mutually_exclusive=scale_mutual_ex_args
                          )

    rc = -1
    msg = result_json = ""
    state_changed = False

    try:
        if module.params['op']:
            node_names = []
            if module.params['name']:
                node_names = module.params['name'].split(',')

            if "get" in module.params['op']:
                # Retrieve the IBM Spectrum Scale node information
                rc, msg, result_json = get_node_info_as_json(logger, 
                                                             node_names)
            elif "status" in module.params['op']:
                # Retrieve the IBM Spectrum Scale Node state
                rc, msg, result_json = get_node_status_as_json(logger, 
                                                               node_names)
            elif "start" in module.params['op']:
                # Start the IBM Spectrum Scale Server(s)
                rc, msg, result_json = start_nodes(logger, node_names)
            elif "stop" in module.params['op']:
                # Stop the IBM Spectrum Scale Server(s)
                rc, msg, result_json = stop_nodes(logger, node_names)

        elif module.params['state']:
            listofserver = module.params['name']
            if "present" in module.params['state']:
                # Create a new IBM Spectrum Scale cluster
                rc, msg, result_json = add_nodes(logger,
                                                 listofserver.split(','),
                                                 module.params['nodefile'],
                                                 module.params['license'])
            else:
                # Delete the existing IBM Spectrum Scale cluster
                rc, msg, result_json = remove_nodes(logger, 
                                                    listofserver.split(','))

            if rc == RC_SUCCESS:
                state_changed = True
                
    except SpectrumScaleException as sse:
        st = traceback.format_exc()
        e_msg = ("Exception: {0}  StackTrace: {1}".format(str(sse), st))
        logger.debug(e_msg)
        failure_msg = "FAILED: " + sse.get_message()
        module.fail_json(msg=failure_msg, changed=False, rc=-1, 
                         result=result_json, stderr=str(st))
    except Exception as e:
        st = traceback.format_exc()
        e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
        logger.debug(e_msg)
        failure_msg = "FAILED: " + e.get_message()
        module.fail_json(msg=failure_msg, changed=False, rc=-1, 
                         result=result_json, stderr=str(st))

    logger.debug("---------------------------------")
    logger.debug("Function Exit: ibm_spectrumscale_node.main()")
    logger.debug("---------------------------------")

    SpectrumScaleLogger.shutdown()

    # Module is done. Return back the result
    if rc == RC_SUCCESS:
        module.exit_json(msg=msg, changed=state_changed, rc=rc, result=result_json)
    else:
        failure_msg = "FAILED: " + msg
        module.fail_json(msg=failure_msg, changed=state_changed, rc=rc, 
                         result=result_json)


if __name__ == '__main__':
    main() 
