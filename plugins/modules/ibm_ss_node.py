#!/usr/bin/python
# -*- coding: utf-8 -*-

# author: IBM Corporation
# description: Highly-customizable Ansible role module
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
version_added: "0.0"

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
    name: "host-01"

# Delete an existing IBM Spectrum Node from the Cluster
- name: Delete an IBM Spectrum Scale Node from Cluster
  ibm_ss_node:
    state: absent
    name: "host-01"
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
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_ss_utils import runCmd, parse_aggregate_cmd_output, RC_SUCCESS, get_logger

###############################################################################
##                                                                           ##
##                           Helper Functions                                ##
##                                                                           ##
###############################################################################

#
# This function retrieves the Role for each node in the Spectrum Scale Cluster
#
# Returns:
#     role_details = {
#                       "Daemon Name", "IP", "Admin Name": "Role"
#                    }
#     Where Role is "ces", quorum", "gateway" etc
#
def get_gpfs_node_roles():
    logger.debug("Function Entry: get_gpfs_node_roles(). ")

    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmlscluster", "-Y"])
    except Exception as exp_msg:
        logger.error("While obtaining nodes vs. role map. Execution halted!\n"
                     "Message: %s", exp_msg)
        exit(1)

    if rc:
        logger.error("Operation (mmlscluster -Y) failed.")
        logger.error("stdout: %s\nstderr: %s", stdout, stderr)
        exit(1)
    else:
        output = stdout.splitlines()

        daemon_node_token = output[1].split(':').index('daemonNodeName')
        ipaddress_token   = output[1].split(':').index('ipAddress')
        admin_node_token  = output[1].split(':').index('adminNodeName')
        designation_token = output[1].split(':').index('designation')
        other_role_token  = output[1].split(':').index('otherNodeRoles')
        alias_role_token  = output[1].split(':').index('otherNodeRolesAlias')

        role_details, final_value = {}, ''
        for cmd_line in output:
            if re.match(r"mmlscluster:clusterNode:\d+", cmd_line):
                daemon_value = cmd_line.split(':')[daemon_node_token]
                ip_value = cmd_line.split(':')[ipaddress_token]
                admin_value = cmd_line.split(':')[admin_node_token]
                other_role_value = cmd_line.split(':')[other_role_token]
                alias_role_value = cmd_line.split(':')[alias_role_token]
                designation_value = cmd_line.split(':')[designation_token]

                key = '{},{},{}'.format(daemon_value, ip_value, admin_value)

                if not designation_value and not alias_role_value and not \
                        other_role_value:
                    final_value = ''
                elif designation_value and not alias_role_value and not \
                        other_role_value:
                    final_value = designation_value
                elif not designation_value and alias_role_value and not \
                        other_role_value:
                    final_value = alias_role_value
                elif not designation_value and not alias_role_value and \
                        other_role_value:
                    final_value = other_role_value
                elif designation_value and alias_role_value and not \
                        other_role_value:
                    final_value = '{},{}'.format(designation_value,
                                                 alias_role_value)
                elif not designation_value and alias_role_value and \
                        other_role_value:
                    final_value = '{},{}'.format(alias_role_value,
                                                 other_role_value)
                elif designation_value and not alias_role_value and \
                        other_role_value:
                    final_value = '{},{}'.format(designation_value,
                                                 other_role_value)
                elif designation_value and alias_role_value and \
                        other_role_value:
                    final_value = '{},{},{}'.format(designation_value,
                                                    alias_role_value,
                                                    other_role_value)

                role_details[key] = final_value

    logger.debug("Function Exit: get_gpfs_node_roles(). Return Params: "
                 "role_details={0}".format(role_details))

    return role_details


def gpfs_del_nsd(all_node_disks):
    """
        This function performs "mmdelnsd".
        Args:
            all_node_disks (list): List of disks corresponding to an instance.
    """
    disk_name = ";".join(all_node_disks)
    logger.info("** disk_name = {0}".format(disk_name))
    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmdelnsd", disk_name])
    except Exception as exp_msg:
        logger.error("While deleting NSD. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if rc:
        logger.error("Operation (mmdelnsd %s) failed.", disk_name)
        logger.error("stdout: %s\nstderr: %s", stdout, stderr)
        exit(1)
    else:
        logger.info("Operation (mmdelnsd %s) completed successfully.",
                    disk_name)


def gpfs_del_disk(instance, fs_name, disk_names):
    """
        This function performs "mmdeldisk".
        Args:
            instance (str): instance for which disk needs to be deleted.
            fs_name (str): Filesystem name associated with the disks.
            disk_names (list): Disk name to be deleted.
                              Ex: ['gpfs1nsd', 'gpfs2nsd', 'gpfs3nsd']
    """
    disk_name = ";".join(disk_names)
    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmdeldisk", fs_name,
                                    disk_name, '-N', instance])
    except Exception as exp_msg:
        logger.error("While deleting disk. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if rc:
        logger.error("Operation (mmdeldisk %s %s -N %s) failed.", fs_name,
                     disk_name, instance)
        logger.error("stdout: %s\nstderr: %s", stdout, stderr)
        exit(1)
        # TODO: This is most obvious situation, we need to enhance message
    else:
        logger.info("Operation (mmdeldisk %s %s -N %s) completed "
                    "successfully.", fs_name, disk_name, instance)


def get_all_disks_of_node(instance, region):
    """
        This function performs "mmlsnsd -X -Y".
        Args:
            instance (str): instance for which disks are use by filesystem.
            region (str): Region of operation
        Returns:
           all_disk_names (list): Disk names in list format.
                                  Ex: [nsd_1a_1_0, nsd_1c_1_0, nsd_1c_d_1]
    """
    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmlsnsd", '-X', '-Y'])
    except Exception as exp_msg:
        logger.error("While obtaining disk to filesystem details. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if "No disks were found" in stderr:
        return []

    output = stdout.splitlines()

    disk_token = output[0].split(':').index('diskName')
    server_token = output[0].split(':').index('serverList')
    remark = output[0].split(':').index('remarks')
    all_disk_names = []
    for cmd_line in output:
        if re.match(r"mmlsnsd:nsd:\d+", cmd_line):
            disk_host = cmd_line.split(':')[server_token]
            if cmd_line.split(':')[remark] == 'server node' and disk_host == instance:
                all_disk_names.append(cmd_line.split(':')[disk_token])

    return all_disk_names


def get_zimon_collectors():
    """
        This function returns zimon collector node ip's.
    """
    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmperfmon", "config",
                                     "show"])
    except Exception as exp_msg:
        logger.error("While obtaining zimon configuration details. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if rc:
        if "There is no performance monitoring configuration data" in stderr:
            return []
        logger.error("Operation (mmperfmon config show) failed.")
        logger.error("stdout: %s\nstderr: %s", stdout, stderr)
        exit(1)
    else:
        logger.info("Operation (mmperfmon config show) completed "
                    "successfully.")
        output = stdout.splitlines()
        col_regex = re.compile(r'colCandidates\s=\s(?P<collectors>.*)')
        for cmd_line in output:
            if col_regex.match(cmd_line):
                collectors = col_regex.match(cmd_line).group('collectors')

        collectors = collectors.replace("\"", '').replace(" ", '')
        collectors = collectors.split(',')
        logger.info("Identified collectors: %s ", collectors)

    return collectors


def get_allfsnames():
    """
        This function executes mmlsfs and returns all filesystem names in
        list form.
        Returns:
            fs_names (list): All filesystem names in the cluster.
                Ex: fs_names = ['gpfs0', 'gpfs1']
    """
    output = []
    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmlsfs", "all", "-Y"])
    except Exception as exp_msg:
        logger.error("While obtaining list of filesystems. Execution halted!\n"
                     "Message: %s", exp_msg)

    fs_names = []
    if rc:
        if 'mmlsfs: No file systems were found.' in stdout or \
                'mmlsfs: No file systems were found.' in stderr:
            logger.debug("No filesystems were found in the cluster.")
            return list(fs_names)

        logger.error("Operation (mmlsfs all -Y) failed:")
        logger.error("stdout: %s\nstderr: %s", stdout, stderr)
        exit(1)

    output = stdout.splitlines()
    device_index = output[0].split(':').index('deviceName')
    for cmd_line in output[1:]:
        device_name = cmd_line.split(':')[device_index]
        fs_names.append(device_name)
    fs_names = set(fs_names)

    return list(fs_names)


def get_all_fs_to_disk_map(fs_list):
    """
        This function performs "mmlsdisk <fs> -L -Y".
        Args:
            fs_list (list): List of all filesystems in the cluster.
        Returns:
            fs_disk_map (dict): Dict of fs names vs. disk names.
                Ex: {'fs1': ['gpfs1nsd', 'gpfs2nsd'],
                     'fs2': ['gpfs3nsd', 'gpfs4nsd']}
    """
    fs_disk_map = {}
    for each_fs in fs_list:
        print(each_fs)
        disk_name = []
        try:
            stdout, stderr, rc = runCmd(['/usr/lpp/mmfs/bin/mmlsdisk', each_fs,
                                        '-L', '-Y'])
        except Exception as exp_msg:
            logger.error("While obtaining filesystem to disk map. "
                         "Execution halted! Message: %s",
                         exp_msg)

            exit(1)

        if rc:
            logger.error("Operation (mmlsdisk %s -L -Y) failed.", each_fs)
            logger.error("stdout: %s\nstderr: %s", stdout, stderr)
            exit(1)
        else:
            output = stdout.splitlines()
            disk_token = output[0].split(':').index('nsdName')
            for cmd_line in output:
                if re.match(r"mmlsdisk::\d+", cmd_line):
                    disk_name.append(cmd_line.split(':')[disk_token])
                    fs_disk_map[each_fs] = disk_name

    return fs_disk_map


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
    try:
        # TODO
        # The original code executed the command "/usr/lpp/mmfs/bin/mmdf <fs_name> -d -Y"
        # but this did not work if there were multiple Pools with a separate System Pool.
        # Therefore the "-d" flag has been removed. Check to see why the "-d" flag was 
        # was used in the first place
        stdout, stderr, rc = runCmd(['/usr/lpp/mmfs/bin/mmdf', fs_name,
                                    '-Y'])
    except Exception as exp_msg:
        logger.error("While obtaining filesystem capacity. Execution halted!\n"
                     "Code:, Message: ")
        exit(1)

    if rc:
        logger.error("Operation (mmdf %s -d -Y) failed.", fs_name)
        logger.error("stdout: %s\nstderr: %s", stdout, stderr)
        exit(1)
    else:
        output = stdout.splitlines()
        disk_token = output[0].split(':').index('nsdName')
        percent_token = output[0].split(':').index('freeBlocksPct')
        free_token = output[0].split(':').index('freeBlocks')
        size_token = output[0].split(':').index('diskSize')
        disk_size_map = {}
        for cmd_line in output:
            if re.match(r"mmdf:nsd:\d+", cmd_line):
                total = cmd_line.split(':')[size_token]
                free = cmd_line.split(':')[free_token]
                used = int(total) - int(free)
                disk = cmd_line.split(':')[disk_token]
                disk_size_map[disk] = \
                    {'free_size': int(free), 'used_size': used,
                     'percent': cmd_line.split(':')[percent_token]}

    return disk_size_map


def gpfs_remove_nodes(existing_instances, skip=False):
    """
        This function performs "mmshutdown" and "mmdelnode".
        Args:
            exist_instances (list): List of instances to remove from cluster.
    """
    if not skip:
        try:
            # TODO: Should we first unmount to ensure proper shutdown?
            #stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmumount", "-a", 
            #                             "-N", existing_instances])

            stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmshutdown", "-N",
                                         existing_instances])

        except Exception as exp_msg:
            logger.error("While shutting down gpfs. Execution halted!\n"
                         "Code:, Message: ")
            exit(1)

        if rc:
            logger.error("Operation (mmshutdown -N %s) failed.",
                         existing_instances)
            logger.error("stdout: %s\nstderr: %s", stdout, stderr)
            exit(1)
        else:
            logger.info("Operation (mmshutdown -N %s) completed successfully.",
                        existing_instances)

    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmdelnode", "-N",
                                    existing_instances])

    except Exception as exp_msg:
        logger.error("While deleting node(s) from gpfs cluster. "
                     "Execution halted!\nCode:, Message:")
        exit(1)

    if rc:
        logger.error("Operation (mmdelnode -N %s) failed.", existing_instances)
        logger.error("stdout: %s\nstderr: %s", stdout, stderr)
        exit(1)
    else:
        logger.info("Operation (mmdelnode -N %s) completed successfully.",
                    existing_instances)


def get_node_nsd_info():

    try:
        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmlsnsd", '-X', '-Y'])
    except Exception as exp_msg:
        logger.error("While obtaining disk to filesystem details. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    output = stdout.splitlines()

    if "No disks were found" in stderr:
        return {}, {} 

    nsd_token_idx     = output[0].split(':').index('diskName')
    server_token_idx  = output[0].split(':').index('serverList')
    remarks_token_idx = output[0].split(':').index('remarks')

    node_nsd_map = {}
    nsd_node_map = {}

    for line in output:
        if re.match(r"mmlsnsd:nsd:\d+", line):
            nsd_name    = line.split(':')[nsd_token_idx]
            host_name   = line.split(':')[server_token_idx]
            host_status = line.split(':')[remarks_token_idx]

            if  host_status == 'server node':
                # Populate the node_nsd_map data structure
                nsd_list = []
                if host_name in node_nsd_map.keys():
                    nsd_list = node_nsd_map[host_name]
                nsd_list.append(nsd_name)
                node_nsd_map[host_name] = nsd_list
                
                # Populate the nsd_node_map data structure
                host_list = []
                if nsd_name in nsd_node_map.keys():
                    host_list = nsd_node_map[nsd_name]
                host_list.append(host_name)
                nsd_node_map[nsd_name] = host_list 

    return node_nsd_map, nsd_node_map


###############################################################################
##                                                                           ##
##               Functions to add a node to the cluster                      ##
##                                                                           ##
###############################################################################

def add_node(name, stanza_path):
    # TODO: Make This idempotent
    stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmaddnode",
                                 "-N", nodefile_path,
                                 "--accept"],
                                sh=False)

    if rc == RC_SUCCESS:
        msg = stdout
    else:
        msg = stderr

    return rc, msg



###############################################################################
##                                                                           ##
##               Functions to remove node(s) from cluster                    ##
##                                                                           ##
###############################################################################

def remove_multi_attach_nsd(nodes_to_be_deleted):
    logger.debug("Function Entry: remove_multi_attach_nsd(). "
                 "Args nodes_to_be_deleted={0}".format(nodes_to_be_deleted))

    # Iterate through each server to be deleted 
    for node_to_delete in nodes_to_be_deleted:
        logger.debug("Processing all NSDs on node={0} for "
                     "removal".format(node_to_delete))
        node_map, nsd_map = get_node_nsd_info()

        # Check if the node to be deleted has access to any NSDs
        if node_to_delete in node_map.keys():
            nsds_to_delete_list = node_map[node_to_delete]

            # For each Node, check all the NSDS it has access to. If the 
            # Node has access to an NSD that can also be accessed from other
            # NSD servers, then we can simply modify the server access list 
            # through the mmchnsd command
            for nsd_to_delete in nsds_to_delete_list: 
                # Clone list to avoid modifying original content
                nsd_attached_to_nodes = (nsd_map[nsd_to_delete])[:]
                nsd_attached_to_nodes.remove(node_to_delete)
                if len(nsd_attached_to_nodes) >= 1:
                    # This node has access to an NSD, that can also be 
                    # accessed by other NSD servers. Therefore modify the 
                    # server access list
                    #
                    # mmchnsd "nsd1:host-nsd-01"
                    server_access_list = ','.join(map(str, nsd_attached_to_nodes))
                    server_access_list = nsd_to_delete+":"+server_access_list

                    try:
                        stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmchnsd", 
                                                     server_access_list], 
                                                    sh=False)
                    except Exception as exp_msg:
                        logger.error("Exception encountered during execution "
                                     "of modifying NSD server access list "
                                     "for NSD={0} on Node={1}. Exception "
                                     "Message={2)".format(nsd_to_delete,
                                                          node_to_delete,
                                                          exp_msg))
                        exit(1)

                    if rc != RC_SUCCESS:
                        logger.error("Failed to modify NSD server access list "
                                     "for NSD={0} on Node={1}. Output={2} "
                                     "Error={3}".format(nsd_to_delete,
                                                        node_to_delete,
                                                        stdout,
                                                        stderr))
                        exit(1)
                    else:
                        logger.info("Successfully modify NSD server access "
                                    "list for NSD={0} on Node={1}".format(
                                        nsd_to_delete, node_to_delete))
   
    # All "mmchnsd" calls are asynchronous. Therefore wait here till all 
    # modifications are committed before proceeding further. For now just
    # sleep but we need to enhance this to ensure the async op has completed
    time.sleep(60)

    logger.debug("Function Exit: remove_multi_attach_nsd(). ")


#
# This function performs removal / termination of nodes from the IBM Spectrum
# Scale cluster. If the node is a server node that has access to NSD(s), then
# we attempt to remove access to this NSD (if the NSD is a shared NSD) or 
# delete access to it (if its a dedicated NSD).
#
# Args: 
#   nodes_to_delete: Nodes to be deleted from the cluster
#
# Return:
#   rc: Return code
#   msg: Output message
def remove_nodes(nodes_to_delete):
    logger.debug("Function Entry: remove_nodes(). "
                 "Args: node_list={0}".format(nodes_to_delete))

    # Precheck nodes to make sure they do not have any roles that should
    # not be deleted
    gpfs_node_roles = get_gpfs_node_roles()
    ROLES_NOT_TO_DELETE = ['quorum', 'quorumManager', 'ces', 'gateway',
                           'tct', 'snmp_collector']

    for each_ip in nodes_to_delete:
        for node_details in gpfs_node_roles:
            # The node_details consists of "daemon name,ip address,admin name"
            # Check if the node (reffered to as any of the "daemon name", 
            # "ip address" or "admin name") 
            if each_ip in node_details.split(','):
                for role in ROLES_NOT_TO_DELETE:
                    if role in gpfs_node_roles:
                        logger.info("Cannot remove node (%s), as it was "
                                    "holding (%s) role.", each_ip, role)
                        logger.error("Please re-run the current command "
                                     "without ip(s) (%s). Execution halted!",
                                     each_ip)
                        exit(1)

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
    node_map, nsd_map = get_node_nsd_info()

    all_fs_list     = get_allfsnames()
    node_disk_map   = get_all_fs_to_disk_map(all_fs_list)
    zimon_col_nodes = get_zimon_collectors()

    logger.debug("Identified all filesystem to disk mapping: %s",
                 node_disk_map)

    for each_ip in nodes_to_delete:
        logger.debug("Operating on server: %s", each_ip)
        #all_node_disks = get_all_disks_of_node(each_ip, REGION)
        all_node_disks = get_all_disks_of_node(each_ip, "")
        logger.debug("Identified disks for server (%s): %s", each_ip,
                     all_node_disks)

        if len(all_node_disks) == 0:
            gpfs_remove_nodes(each_ip)
            continue
    
        fs_disk_map = {}
        for fs_name, disks in node_disk_map.iteritems():
            node_specific_disks = []
            for each_disk in disks:
                if each_disk in all_node_disks:
                    node_specific_disks.append(each_disk)
            fs_disk_map[fs_name] = node_specific_disks
        logger.debug("Identified filesystem to disk map for server (%s): %s",
                     each_ip, fs_disk_map)

        for each_fs in fs_disk_map:
            disk_cap = gpfs_df_disk(each_fs)
            logger.debug("Identified disk capacity for filesystem (%s): %s",
                         each_fs, disk_cap)
            # Algorithm used for checking at-least 20% free space during
            # mmdeldisk in progress;
            # - Identify the size of data stored in disks going to be
            #   deleted.
            # - Identify the free size of the filesystem
            #   (excluding the disk going to be deleted)
            # - Allow for disk deletion, if total_free size is 20% greater
            #   even after moving used data stored in disk going to be deleted.
            size_to_be_del = 0
            for each_disk in fs_disk_map[each_fs]:
                size_to_be_del += disk_cap[each_disk]['used_size']
            logger.debug("Identified data size going to be deleted from "
                         "filesystem (%s): %s", each_fs, size_to_be_del)

            other_disks = []
            for disk_name in disk_cap:
                if disk_name not in fs_disk_map[each_fs]:
                    other_disks.append(disk_name)
            logger.debug("Identified other disks of the filesystem (%s): %s",
                         each_fs, other_disks)

            size_avail_after_migration, total_free = 0, 0
            for each_disk in other_disks:
                # Accumulate free size on all disks.
                total_free += disk_cap[each_disk]['free_size']
                logger.debug("Identified free size in other disks of the "
                             "filesystem (%s): %s", each_fs, total_free)

            size_avail_after_migration = total_free - size_to_be_del
            logger.debug("Expected size after restriping of the filesystem "
                         "(%s): %s", each_fs, size_avail_after_migration)
            print(size_avail_after_migration)
            #percent = 30
            percent = int(size_avail_after_migration*100/total_free)
            logger.debug("Expected percentage of size left after restriping "
                         "of the filesystem (%s): %s", each_fs, percent)

            if percent < 20:
                logger.error("No enough space left for restriping data for "
                             "filesystem (%s). Execution halted!", each_fs)
                exit(1)

            if fs_disk_map[each_fs]:
                # mmdeldisk will not be hit if there are no disks to delete.
                gpfs_del_disk(each_ip, each_fs, fs_disk_map[each_fs])

        if all_node_disks:
            # mmdelnsd will not be hot if there are no disks to delete.
            gpfs_del_nsd(all_node_disks)
        gpfs_remove_nodes(each_ip)

    logger.debug("Function Exit: remove_nodes().")
    return 0, ""


###############################################################################
##                                                                           ##
##               Functions to retrieve Node information                      ##
##                                                                           ##
###############################################################################

def get_node_info(node_names):
    msg = result_json = ""
    stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmlscluster","-Y"], sh=False)

    if rc == RC_SUCCESS:
        result_dict = parse_aggregate_cmd_output(stdout, 
                                                 MMLSCLUSTER_SUMMARY_FIELDS)
        result_json = json.dumps(result_dict)
        msg = "mmlscluster successfully executed"
    else:
        msg = stderr

    return rc, msg, result_json


###############################################################################
##                                                                           ##
##                              Main Function                                ##
##                                                                           ##
###############################################################################

def main():
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
        # Retrieve the IBM Spectrum Scale node (cluster) information
        node_name_str = module.params['name']
        rc, msg, result_json = get_node_info(node_name_str.split(','))
    elif module.params['state']:
        if "present" in module.params['state']:
            # Create a new IBM Spectrum Scale cluster
            rc, msg = add_node(
                                 module.params['stanza'],
                                 module.params['name']
                              )
        else:
            listofserver = module.params['name']
            # Delete the existing IBM Spectrum Scale cluster
            rc, msg = remove_nodes(listofserver.split(','))

        if rc == RC_SUCCESS:
            state_changed = True

    # Module is done. Return back the result
    module.exit_json(changed=state_changed, msg=msg, rc=rc, result=result_json)


if __name__ == '__main__':
    # Set up the Logger. Print to console and file
    logger = get_logger()
    logger.addHandler(logging.StreamHandler())
    main() 
