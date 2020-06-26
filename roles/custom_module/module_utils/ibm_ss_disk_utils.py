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
import sys
import json
from ibm_ss_utils import runCmd, parse_unique_records, GPFS_CMD_PATH, \
                         RC_SUCCESS, SpectrumScaleException

class SpectrumScaleDisk:
    disk = {}
    filesystem = ""

    def __init__(self, disk_dict, fs_name):
        self.disk = disk_dict
        self.filesystem = fs_name

    def get_nsd_name(self):
        nsd_name = self.disk["nsdName"]
        return nsd_name

    def get_driver_type(self):
        driver_type = self.disk["driverType"]
        return driver_type

    def get_sector_size(self):
        sector_size = self.disk["sectorSize"]
        return sector_size

    def get_failure_group(self):
        failure_group = self.disk["failureGroup"]
        return failure_group

    def contains_metadata(self):
        metadata = self.disk["metadata"]
        if "yes" in metadata:
            return True
        return False

    def contains_data(self):
        data = self.disk["data"]
        if "yes" in data:
            return True
        return False

    def get_status(self):
        status = self.disk["status"]
        return status

    def get_availability(self):
        availability = self.disk["availability"]
        return availability

    def get_disk_id(self):
        disk_id = self.disk["diskID"]
        return disk_id

    def get_storage_pool(self):
        pool_name = self.disk["storagePool"]
        return pool_name

    def get_remarks(self):
        remarks = self.disk["remarks"]
        return remarks

    def get_num_quorum_disks(self):
        num_qd_str = self.disk["numQuorumDisks"]
        num_quorum_disks = int(num_qd_str)
        return num_quorum_disks

    def get_read_quorum_value(self):
        read_qv_str = self.disk["readQuorumValue"]
        read_quorum_value = int(read_qv_str)
        return read_quorum_value

    def get_write_quorum_value(self):
        write_qv_str = self.disk["writeQuorumValue"]
        write_quorum_value = int(write_qv_str)
        return write_quorum_value

    def get_disk_size_KB(self):
        disk_sz_str = self.disk["diskSizeKB"]
        disk_size_KB = int(disk_sz_str)
        return disk_size_KB

    def get_disk_UID(self):
        disk_uid = self.disk["diskUID"]
        return disk_uid

    def get_thin_disk_type(self):
        thin_disk_type = self.disk["thinDiskType"]
        return thin_disk_type

    def to_json(self):
        return json.dumps(self.disk)

    def print_disk(self):
        print("NSD Name           : {0}".format(self.get_nsd_name()))
        print("Driver Type        : {0}".format(self.get_driver_type()))
        print("Sector Size        : {0}".format(self.get_sector_size()))
        print("Failure Group      : {0}".format(self.get_failure_group()))
        print("Contains Metadata  : {0}".format(self.contains_metadata()))
        print("Contains Data      : {0}".format(self.contains_data()))
        print("Status             : {0}".format(self.get_status()))
        print("Availability       : {0}".format(self.get_availability()))
        print("Disk ID            : {0}".format(self.get_disk_id()))
        print("Storage Pool       : {0}".format(self.get_storage_pool()))
        print("Remarks            : {0}".format(self.get_remarks()))
        print("Num Quorum Disks   : {0}".format(self.get_num_quorum_disks()))
        print("Read Quorum Value  : {0}".format(self.get_read_quorum_value()))
        print("Write Quorum Value : {0}".format(self.get_write_quorum_value()))
        print("NSD Disk Size (KB) : {0}".format(self.get_disk_size_KB()))
        print("Disk UID           : {0}".format(self.get_disk_UID()))
        print("Thin Disk Type     : {0}".format(self.get_thin_disk_type()))

    @staticmethod
    def get_all_disk_info(fs_name):
        disk_info_list = []
        stdout, stderr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmlsdisk"),
                                                  fs_name, "-Y"],
                                                  sh=False)

        if rc == RC_SUCCESS:
            # TODO: Check the return codes and examine other possibility and verify below
            if "No disks were found" in stderr:
                return nsd_info_list
        else:
            raise SpectrumScaleException("Retrieving disk information failed",
                                     "mmlsdisk",
                                     [fs_name, "-Y"], 
                                     rc, stdout, stderr) 

        disk_dict = parse_unique_records(stdout)
        disk_list = disk_dict["mmlsdisk"]

        for disk in disk_list:
            disk_instance = SpectrumScaleDisk(disk, fs_name)
            disk_info_list.append(disk_instance)

        return disk_info_list


    @staticmethod
    def delete_disk(node_name, filesystem_name, disk_names):
        """
            This function performs "mmdeldisk".
            Args:
                node_name (str): Node for which disk needs to be deleted.
                filesystems_name (str): Filesystem name associated with the disks.
                disk_names (list): Disk name to be deleted.
                                  Ex: ['gpfs1nsd', 'gpfs2nsd', 'gpfs3nsd']
        """
        disk_name_str = ";".join(disk_names)
        stdout, stderr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmdeldisk"), 
                                     filesystem_name,
                                     disk_name_str, '-N', node_name])

        if rc != RC_SUCCESS:
            cmd_args = "{0} {1} {2}".format(node_name, filesystem_name, disk_name_str)
            raise SpectrumScaleException("Deleting disk(s) failed. ",
                                     "mmdeldisk ",
                                     cmd_args, 
                                     rc, stdout, stderr) 

                                 
def main():
    if len(sys.argv) == 2:
        fs_name = sys.argv[1]
        try:
            disk_list = get_all_disk_info(fs_name)
            for disk in disk_list:
                disk.print_disk()
                print("\n")
        except Exception as e:
            print(e)
    else:
        print("The file system name should be specified")
        rc = 1


if __name__ == "__main__":
    main()
