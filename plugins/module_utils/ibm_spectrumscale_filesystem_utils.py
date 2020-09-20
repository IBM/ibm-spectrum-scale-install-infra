#!/usr/bin/python
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

import os
import json
from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_utils import runCmd, parse_simple_cmd_output, GPFS_CMD_PATH, \
                         RC_SUCCESS, SpectrumScaleException

class SpectrumScaleFS:

    def __init__(self, device_name, filesystem_properties):
        self.device_name = device_name
        self.properties_list = filesystem_properties

    def __get_property_as_str(self, prop_name):
        str_prop_value = ""
        for fs_property in self.properties_list:
            if prop_name in fs_property["fieldName"]:
                str_prop_value = fs_property["data"]
        return str_prop_value

    def __get_property_as_int(self, prop_name):
        int_prop_value = 0
        for fs_property in self.properties_list:
            if prop_name in fs_property["fieldName"]:
                int_prop_value = int(fs_property["data"])
        return int_prop_value

    def __get_property_as_bool(self, prop_name):
        bool_prop_value = False
        for fs_property in self.properties_list:
            if prop_name in fs_property["fieldName"]:
                if ("Yes" in fs_property["data"] or
                    "yes" in fs_property["data"]):
                    bool_prop_value = True
        return bool_prop_value

    def get_device_name(self):
        return self.device_name

    def get_syspool_min_fragment_size(self):
        syspool_min_fragment_size = 0
        for fs_property in self.properties_list:
            if ("minFragmentSize" in fs_property["fieldName"] and
                "system pool" in fs_property["remarks"]):
                syspool_min_fragment_size = int(fs_property["data"])
        return syspool_min_fragment_size

    def get_other_pool_min_fragment_size(self):
        other_pool_min_fragment_size = 0
        for fs_property in self.properties_list:
            if ("minFragmentSize" in fs_property["fieldName"] and
                "other pools" in fs_property["remarks"]):
                other_pool_min_fragment_size = int(fs_property["data"])
        return other_pool_min_fragment_size

    def get_inode_size(self):
        return self.__get_property_as_int("inodeSize")

    def get_indirect_block_size(self):
        return self.__get_property_as_int("indirectBlockSize")

    def get_default_metadata_replicas(self):
        return self.__get_property_as_int("defaultMetadataReplicas")

    def get_max_metadata_replicas(self):
        return self.__get_property_as_int("maxMetadataReplicas")

    def get_default_data_replicas(self):
        return self.__get_property_as_int("defaultDataReplicas")

    def get_max_data_replicas(self):
        return self.__get_property_as_int("maxDataReplicas")

    def get_block_allocation_type(self):
        return self.__get_property_as_str("blockAllocationType")

    def get_file_locking_semantics(self):
        return self.__get_property_as_str("fileLockingSemantics")

    def get_acl_semantics(self):
        return self.__get_property_as_str("ACLSemantics")

    def get_num_nodes(self):
        return self.__get_property_as_int("numNodes")

    def get_syspool_block_size(self):
        syspool_block_size = 0
        for fs_property in self.properties_list:
            if ("blockSize" in fs_property["fieldName"] and
                "system pool" in fs_property["remarks"]):
                syspool_block_size = int(fs_property["data"])
        return syspool_block_size

    def get_other_pool_block_size(self):
        other_pool_block_size = 0
        for fs_property in self.properties_list:
            if ("blockSize" in fs_property["fieldName"] and
                "other pools" in fs_property["remarks"]):
                other_pool_block_size = int(fs_property["data"])
        return other_pool_block_size

    def get_quotas_accounting_enabled(self):
        return self.__get_property_as_str("quotasAccountingEnabled")

    def get_quotas_enforced(self):
        return self.__get_property_as_str("quotasEnforced")

    def get_default_quotas_enabled(self):
        return self.__get_property_as_str("defaultQuotasEnabled")

    def get_per_fileset_quotas(self):
        return self.__get_property_as_bool("perfilesetQuotas")

    def is_fileset_df_enabled(self):
        return self.__get_property_as_bool("filesetdfEnabled")

    def get_filesystem_version(self):
        return self.__get_property_as_str("filesystemVersion")

    def get_filesystem_version_local(self):
        return self.__get_property_as_str("filesystemVersionLocal")

    def get_filesystem_version_manager(self):
        return self.__get_property_as_str("filesystemVersionManager")

    def get_filesystem_version_original(self):
        return self.__get_property_as_str("filesystemVersionOriginal")

    def get_filesystem_highest_supported(self):
        return self.__get_property_as_str("filesystemHighestSupported")

    def get_create_time(self):
        return self.__get_property_as_str("create-time")

    def is_dmapi_enabled(self):
        return self.__get_property_as_bool("DMAPIEnabled")

    def get_logfile_size(self):
        return self.__get_property_as_int("logfileSize")

    def is_exact_m_time(self):
        return self.__get_property_as_bool("exactMtime")

    def get_suppress_atime(self):
        return self.__get_property_as_str("suppressAtime")

    def get_strict_replication(self):
        return self.__get_property_as_str("strictReplication")

    def is_fast_ea_enabled(self):
        return self.__get_property_as_bool("fastEAenabled")

    def is_encrypted(self):
        return self.__get_property_as_bool("encryption")

    def get_max_number_of_inodes(self):
        return self.__get_property_as_int("maxNumberOfInodes")

    def get_max_snapshot_id(self):
        return self.__get_property_as_int("maxSnapshotId")

    def get_uid(self):
        return self.__get_property_as_str("UID")

    def get_log_replicas(self):
        return self.__get_property_as_int("logReplicas")

    def is_4k_aligned(self):
        return self.__get_property_as_bool("is4KAligned")

    def is_rapid_repair_enabled(self):
        return self.__get_property_as_bool("rapidRepairEnabled")

    def get_write_cache_threshold(self):
        return self.__get_property_as_int("write-cache-threshold")

    def get_subblocks_per_full_block(self):
        return self.__get_property_as_int("subblocksPerFullBlock")

    def get_storage_pools(self):
        storage_pool_list = []
        storage_pool_str = self.__get_property_as_str("storagePools")
        if storage_pool_str:
            storage_pool_list = storage_pool_str.split(";")
        return storage_pool_list

    def is_file_audit_log_enabled(self):
        return self.__get_property_as_bool("file-audit-log")

    def is_maintenance_mode(self):
        return self.__get_property_as_bool("maintenance-mode")

    def get_disks(self):
        disk_list = []
        disk_str = self.__get_property_as_str("disks")
        if disk_str:
            disk_list = disk_str.split(";")
        return disk_list

    def is_automatic_mount_option_enabled(self):
        return self.__get_property_as_bool("automaticMountOption")

    def get_additional_mount_options(self):
        return self.__get_property_as_str("additionalMountOptions")

    def get_default_mount_point(self):
        return self.__get_property_as_str("defaultMountPoint")

    def get_mount_priority(self):
        return self.__get_property_as_int("mountPriority")

    def get_properties_list(self):
        return self.properties_list

    def to_json(self):
        # TODO: Include Filesystem Device Name
        return json.dumps(self.properties_list)

    def print_filesystem(self):
        print("Device Name                       : {0}".format(self.get_device_name()))
        print("Syspool Min Fragment Size         : {0}".format(self.get_syspool_min_fragment_size()))
        print("Other Pool Min Fragment Size      : {0}".format(self.get_other_pool_min_fragment_size()))
        print("Inode Size                        : {0}".format(self.get_inode_size()))
        print("Indirect Block Size               : {0}".format(self.get_indirect_block_size()))
        print("Default Metadata Replicas         : {0}".format(self.get_default_metadata_replicas()))
        print("Max Metadata Replicas             : {0}".format(self.get_max_metadata_replicas()))
        print("Default Data Replicas             : {0}".format(self.get_default_data_replicas()))
        print("Max Data Replicas                 : {0}".format(self.get_max_data_replicas()))
        print("Block Allocation Type             : {0}".format(self.get_block_allocation_type()))
        print("File Locking Semantics            : {0}".format(self.get_file_locking_semantics()))
        print("ACL Semantics                     : {0}".format(self.get_acl_semantics()))
        print("Num Nodes                         : {0}".format(self.get_num_nodes()))
        print("Syspool Block Size                : {0}".format(self.get_syspool_block_size()))
        print("Other Pool Block Size             : {0}".format(self.get_other_pool_block_size()))
        print("Quotas Accounting Enabled         : {0}".format(self.get_quotas_accounting_enabled()))
        print("Quotas Enforced                   : {0}".format(self.get_quotas_enforced()))
        print("Default Quotas Enabled            : {0}".format(self.get_default_quotas_enabled()))
        print("Per Fileset Quotas                : {0}".format(self.get_per_fileset_quotas()))
        print("Fileset df Enabled                : {0}".format(self.is_fileset_df_enabled()))
        print("Filesystem Version                : {0}".format(self.get_filesystem_version()))
        print("Filesystem Version Local          : {0}".format(self.get_filesystem_version_local()))
        print("Filesystem Version Manager        : {0}".format(self.get_filesystem_version_manager()))
        print("Filesystem Version Original       : {0}".format(self.get_filesystem_version_original()))
        print("Filesystem Highest Supported      : {0}".format(self.get_filesystem_highest_supported()))
        print("Create Time                       : {0}".format(self.get_create_time()))
        print("DMAPI Enabled                     : {0}".format(self.is_dmapi_enabled()))
        print("Logfile Size                      : {0}".format(self.get_logfile_size()))
        print("Is Exact m Time                   : {0}".format(self.is_exact_m_time()))
        print("Suppress atime                    : {0}".format(self.get_suppress_atime()))
        print("Strict Replication                : {0}".format(self.get_strict_replication()))
        print("Is Fast EA Enabled                : {0}".format(self.is_fast_ea_enabled()))
        print("Is Encrypted                      : {0}".format(self.is_encrypted()))
        print("Max Number Of Inodes              : {0}".format(self.get_max_number_of_inodes()))
        print("Max Snapshot Id                   : {0}".format(self.get_max_snapshot_id()))
        print("UID                               : {0}".format(self.get_uid()))
        print("Log Replicas                      : {0}".format(self.get_log_replicas()))
        print("Is 4K Aligned                     : {0}".format(self.is_4k_aligned()))
        print("Is Rapid Repair Enabled           : {0}".format(self.is_rapid_repair_enabled()))
        print("Write Cache Threshold             : {0}".format(self.get_write_cache_threshold()))
        print("Subblocks Per Full Block          : {0}".format(self.get_subblocks_per_full_block()))
        print("Storage Pools                     : {0}".format(self.get_storage_pools()))
        print("Is File Audit Log Enabled         : {0}".format(self.is_file_audit_log_enabled()))
        print("Is Maintenance Mode               : {0}".format(self.is_maintenance_mode()))
        print("Disks                             : {0}".format(self.get_disks()))
        print("Is Automatic Mount Option Enabled : {0}".format(self.is_automatic_mount_option_enabled()))
        print("Additional Mount Options          : {0}".format(self.get_additional_mount_options()))
        print("Default Mount Point               : {0}".format(self.get_default_mount_point()))
        print("Mount Priority                    : {0}".format(self.get_mount_priority()))


    @staticmethod
    def get_filesystems():
        filesystem_info_list = []

        stdout, stderr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmlsfs"),
                                                  "all", "-Y"],
                                                  sh=False)

        if rc != RC_SUCCESS:
            if 'mmlsfs: No file systems were found.' in stdout or \
                    'mmlsfs: No file systems were found.' in stderr:
                return filesystem_info_list

            raise SpectrumScaleException("Retrieving filesystem information failed",
                                     "mmlsfs",
                                     ["all", "-Y"],
                                     rc, stdout, stderr)

        filesystem_dict = parse_simple_cmd_output(stdout, "deviceName", 
                                              "properties", "filesystems")
        filesystem_list = filesystem_dict["filesystems"]

        for filesystem in filesystem_list:
            device_name   = filesystem["deviceName"]
            fs_properties = filesystem["properties"]
            filesystem_instance = SpectrumScaleFS(device_name, 
                                                                fs_properties)
            filesystem_info_list.append(filesystem_instance)

        return filesystem_info_list


    @staticmethod
    def unmount_filesystems(node_name, wait=True):
        cmd = [os.path.join(GPFS_CMD_PATH, "mmumount"), "all", "-N", node_name] 
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)

        if rc != RC_SUCCESS:
            if 'mmumount: No file systems were found' in stdout or \
                    'mmumount: No file systems were found' in stderr:
                # We can claim success on umount if there are no filesystems
                return RC_SUCCESS

            raise SpectrumScaleException("Unmounting filesystems on node failed",
                                         cmd[0], cmd[1:], rc, stdout, stderr)
        return rc, stdout 


    @staticmethod
    def create_filesystem(name, stanza_path, block_size, 
                          default_metadata_replicas,
                          default_data_replicas, num_nodes,
                          automatic_mount_option, 
                          default_mount_point):
        cmd = [os.path.join(GPFS_CMD_PATH, "mmcrfs"), name,
                                     "-F", stanza_path,
                                     "-B", block_size,
                                     "-m", default_metadata_replicas,
                                     "-r", default_data_replicas,
                                     "-n", num_nodes,
                                     "-A", automatic_mount_option,
                                     "-T", default_mount_point]
        # TODO: Make this idempotent
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)

        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Create filesystems on node failed",
                                         cmd[0], cmd[1:], rc, stdout, stderr)


        return rc, stdout


    @staticmethod
    def delete_filesystem(name):
        # TODO: Implement
        rc = RC_SUCCESS
        msg = ""
        return rc, msg


def main():
    filesystem_list = get_filesystems()
    for filesystem in filesystem_list:
        filesystem.print_filesystem()
        print("\n")


if __name__ == "__main__":
    main()
