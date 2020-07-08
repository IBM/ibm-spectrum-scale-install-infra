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
from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_utils import runCmd, parse_unique_records, GPFS_CMD_PATH, \
                         RC_SUCCESS, SpectrumScaleException

class SpectrumScaleNSD:
    nsd = {}

    def __init__(self, nsd_dict):
        self.nsd = nsd_dict

    def get_name(self):
        name = self.nsd["diskName"]
        return name

    def get_volume_id(self):
        volumeId = self.nsd["volumeId"]
        return volumeId

    def get_server_list(self):
        server_list = []
        server_list_str = self.nsd["serverList"]
        if server_list_str:
            server_list = server_list_str.split(",")
        return server_list

    def get_device_type(self):
        device_type = self.nsd["deviceType"]
        return device_type

    def get_disk_name(self):
        disk_name = self.nsd["localDiskName"]
        return disk_name

    def get_remarks(self):
        remarks = self.nsd["remarks"]
        return remarks

    def to_json(self):
        return json.dumps(self.nsd)

    def print_nsd(self):
        print("NSD Name   : {0}".format(self.get_name()))
        print("Volume ID  : {0}".format(self.get_volume_id()))
        print("Server List: {0}".format(self.get_server_list()))
        print("Device Type: {0}".format(self.get_device_type()))
        print("Disk Name  : {0}".format(self.get_disk_name()))
        print("Remarks    : {0}".format(self.get_remarks()))

    
    @staticmethod
    def get_all_nsd_info():
        nsd_info_list = []

        stdout, stderr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmlsnsd"),
                                                  "-a", "-X", "-Y"],
                                                  sh=False)

        if rc == RC_SUCCESS:
            if "No disks were found" in stderr:
                return nsd_info_list
        else:
            raise SpectrumScaleException("Retrieving NSD information Failed",
                                     "mmlsnsd",
                                     ["-a", "-X", "-Y"],
                                     rc, stdout, stderr)

        nsd_dict = parse_unique_records(stdout)
        nsd_list = nsd_dict["nsd"]

        for nsd in nsd_list:
            nsd_instance = SpectrumScaleNSD(nsd)
            nsd_info_list.append(nsd_instance)

        return nsd_info_list


    @staticmethod
    def delete_nsd(nsd_list):
        nsd_names = ";".join(nsd_list)
        stdout, stderr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmdelnsd"), 
                                                  nsd_names])
   
        if rc != RC_SUCCESS: 
            raise SpectrumScaleException("Deleting NSD(s) Failed",
                                     "mmdelnsd",
                                     nsd_list,
                                     rc, stdout, stderr)


    @staticmethod
    def remove_server_access_to_nsd(nsd_to_delete, node_to_delete,
                                    nsd_attached_to_nodes):
        stdout = stderr = ""
        rc = -1

        # mmchnsd "nsd1:node1.domain.com"
        server_access_list = ','.join(map(str, nsd_attached_to_nodes))
        server_access_list = nsd_to_delete+":"+server_access_list

        try:
            stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmchnsd",
                                         server_access_list],
                                        sh=False)
        except Exception as e:
            e_msg = ("Exception encountered during execution of modifying NSD "
                     "server access list for NSD={0} on Node={1}. Exception "
                     "Message={2)".format(nsd_to_delete, node_to_delete, e))
            raise SpectrumScaleException(e_msg, "mmchnsd", [server_access_list],
                                     stdout, str(e))

        if rc != RC_SUCCESS:
            e_msg = ("Failed to modify NSD server access list for NSD={0} on "
                     "Node={1}".format(nsd_to_delete, node_to_delete))
            raise SpectrumScaleException(e_msg, "mmchnsd", [server_access_list],
                                         stdout, stderr)


def main():
    try:
        nsd_list = get_all_nsd_info()
        for nsd in nsd_list:
            nsd.print_nsd()
            print("\n")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
