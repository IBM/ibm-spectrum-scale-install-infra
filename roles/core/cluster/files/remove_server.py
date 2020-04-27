#!/usr/bin/env python

# Licensed Materials - Property of IBM
#
# (C) COPYRIGHT International Business Machines Corp 1994, 2018.
# All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.

"""Script to add/remove spectrum scale compute/nsd node to existing cluster."""

import os
import re
import sys
import time
import logging
import socket
import subprocess

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS


def local_execute_cmd(cmd):
    """
        This function uses "subprocess" to execute command locally.

        Args:
            cmd (str): Command to execute locally.
        Returns (dict):
                        {
                            'stdout': <value>,
                            'stderr': <value>,
                            'returncode': <value>
                        }
    """
    obj = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, stderr = obj.communicate()
    return {'stdout': result.strip(), 'returncode': obj.returncode,
            'stderr': stderr}

def gpfs_del_nsd(all_node_disks):
    """
        This function performs "mmdelnsd".

        Args:
            all_node_disks (list): List of disks corresponding to an instance.
    """
    disk_name = ";".join(all_node_disks)
    try:
        output = local_execute_cmd(['/usr/lpp/mmfs/bin/mmdelnsd',
                                    disk_name])
    except Exception as exp_msg:
        logger.error("While deleting NSD. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if output['returncode']:
        logger.error("Operation (mmdelnsd %s) failed.", disk_name)
        logger.error("stdout: %s\nstderr: %s", output['stdout'],
                     output['stderr'])
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
        output = local_execute_cmd(['/usr/lpp/mmfs/bin/mmdeldisk', fs_name,
                                    disk_name, '-N', instance])
    except Exception as exp_msg:
        logger.error("While deleting disk. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if output['returncode']:
        logger.error("Operation (mmdeldisk %s %s -N %s) failed.", fs_name,
                     disk_name, instance)
        logger.error("stdout: %s\nstderr: %s", output['stdout'],
                     output['stderr'])
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
        output = local_execute_cmd(['ssh', '-o', 'ConnectTimeout=60',
                                    instance, 'hostname'])
    except Exception as exp_msg:
        logger.error("While obtaining hostname. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if region == 'us-east-1':
        # In VPC, if "NVirginiaRegionCondition" is met then DNS is set to
        # "ec2.internal"
        instance_hostname = output['stdout'].split('.')[0] + '.ec2.internal'
    else:
        instance_hostname = output['stdout']

    try:
        output = local_execute_cmd(['/usr/lpp/mmfs/bin/mmlsnsd', '-X', '-Y'])
    except Exception as exp_msg:
        logger.error("While obtaining disk to filesystem details. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    output = output['stdout'].splitlines()

    disk_token = output[0].split(':').index('diskName')
    server_token = output[0].split(':').index('serverList')
    remark = output[0].split(':').index('remarks')
    all_disk_names = []
    for cmd_line in output:
        if re.match(r"mmlsnsd:nsd:\d+", cmd_line):
            if cmd_line.split(':')[remark] == 'server node' and cmd_line.split(':')[server_token] == instance_hostname:
                all_disk_names.append(cmd_line.split(':')[disk_token])

    return all_disk_names

def get_zimon_collectors():
    """
        This function returns zimon collector node ip's.

    """
    try:
        output = local_execute_cmd(["/usr/lpp/mmfs/bin/mmperfmon", "config",
                                    "show"])
    except Exception as exp_msg:
        logger.error("While obtaining zimon configuration details. "
                     "Execution halted!\nMessage: %s", exp_msg)
        exit(1)

    if output['returncode']:
        logger.error("Operation (mmperfmon config show) failed.")
        logger.error("stdout: %s\nstderr: %s", output['stdout'],
                     output['stderr'])
        exit(1)
    else:
        logger.info("Operation (mmperfmon config show) completed "
                    "successfully.")
        output = output['stdout'].splitlines()
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
        output = local_execute_cmd(['/usr/lpp/mmfs/bin/mmlsfs', 'all', '-Y'])
    except Exception as exp_msg:
        logger.error("While obtaining list of filesystems. Execution halted!\n"
                     "Message: %s", exp_msg)

    fs_names = []
    if output['returncode']:
        if 'mmlsfs: No file systems were found.' in output['stdout'] or \
                'mmlsfs: No file systems were found.' in output['stderr']:
            logger.debug("No filesystems were found in the cluster.")
            return list(fs_names)

        logger.error("Operation (mmlsfs all -Y) failed:")
        logger.error("stdout: %s\nstderr: %s", output['stdout'],
                     output['stderr'])
        exit(1)

    output = output['stdout'].splitlines()
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
            output = local_execute_cmd(['/usr/lpp/mmfs/bin/mmlsdisk', each_fs,
                                        '-L', '-Y'])
            print(output)
        except Exception as exp_msg:
            logger.error("While obtaining filesystem to disk map. "
                         "Execution halted!\nCode: , Message: ")

            exit(1)

        if output['returncode']:
            logger.error("Operation (mmlsdisk %s -L -Y) failed.", each_fs)
            logger.error("stdout: %s\nstderr: %s", output['stdout'],
                         output['stderr'])
            exit(1)
        else:
            output = output['stdout'].splitlines()
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
        output = local_execute_cmd(['/usr/lpp/mmfs/bin/mmdf', fs_name, '-d',
                                    '-Y'])
    except Exception as exp_msg:
        logger.error("While obtaining filesystem capacity. Execution halted!\n"
                     "Code:, Message: ")
        exit(1)

    if output['returncode']:
        logger.error("Operation (mmdf %s -d -Y) failed.", fs_name)
        logger.error("stdout: %s\nstderr: %s", output['stdout'],
                     output['stderr'])
        exit(1)
    else:
        output = output['stdout'].splitlines()
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
                disk_size_map[cmd_line.split(':')[disk_token]] = \
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
            output = local_execute_cmd(["/usr/lpp/mmfs/bin/mmshutdown", "-N",
                                        existing_instances])
        except Exception as exp_msg:
            logger.error("While shutting down gpfs. Execution halted!\n"
                         "Code:, Message: ")
            exit(1)

        if output['returncode']:
            logger.error("Operation (mmshutdown -N %s) failed.",
                         existing_instances)
            logger.error("stdout: %s\nstderr: %s", output['stdout'],
                         output['stderr'])
            exit(1)
        else:
            logger.info("Operation (mmshutdown -N %s) completed successfully.",
                        existing_instances)

    try:
        output = local_execute_cmd(["/usr/lpp/mmfs/bin/mmdelnode", "-N",
                                    existing_instances])
    except Exception as exp_msg:
        logger.error("While deleting node(s) from gpfs cluster. "
                     "Execution halted!\nCode:, Message:")
        exit(1)

    if output['returncode']:
        logger.error("Operation (mmdelnode -N %s) failed.", existing_instances)
        logger.error("stdout: %s\nstderr: %s", output['stdout'],
                     output['stderr'])
        exit(1)
    else:
        logger.info("Operation (mmdelnode -N %s) completed successfully.",
                    existing_instances)

def remove_server_nodes(server_asg_group):
    """
        This function performs removal / termination of server nodes.

        Args:
            server_asg_group (str): Server Autoscaling group name.

        Return:
            server_nodes (int): Number of server nodes actually terminated.
    """
    all_fs_list = get_allfsnames()
    node_disk_map = get_all_fs_to_disk_map(all_fs_list)
    zimon_col_nodes = get_zimon_collectors()
    logger.debug("Identified all filesystem to disk mapping: %s",
                 node_disk_map)

    REGION = ''
    SERVER_DETAILS = server_asg_group
    for each_ip in server_asg_group:
        logger.debug("Operating on server: %s", each_ip)
        all_node_disks = get_all_disks_of_node(each_ip, REGION)
        logger.debug("Identified disks for server (%s): %s", each_ip,
                     all_node_disks)

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
                print("delere")
                # mmdeldisk will not be hit if there are no disks to delete.
                gpfs_del_disk(each_ip, each_fs, fs_disk_map[each_fs])

        if all_node_disks:
            # mmdelnsd will not be hot if there are no disks to delete.
            gpfs_del_nsd(all_node_disks)
        gpfs_remove_nodes(each_ip)



if __name__ == "__main__":
    # create logger
    logger = logging.getLogger("removeservernode")
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)

    logger.info("A. Performing prerequisite check")
    listofserver = sys.argv[1]
    print(listofserver)
    remove_server_nodes(listofserver.split(','))
