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
from ibm_ss_utils import runCmd, parse_aggregate_cmd_output, \
                         parse_unique_records, GPFS_CMD_PATH, \
                         RC_SUCCESS, SpectrumScaleException

class SpectrumScaleDf:
    nsd_df = {}

    def __init__(self, nsd_df_dict):
        self.node = nsd_df_dict

    def get_nsd_name(self):
        nsd_name = self.node["nsdName"]
        return nsd_name

    def get_storage_pool(self):
        pool = self.node["storagePool"]
        return pool

    def get_disk_size(self):
        disk_size = self.node["diskSize"]
        if disk_size:
            return int(disk_size)
        return 0

    def get_failure_group(self):
        fg = self.node["failureGroup"]
        return fg

    def stores_meta_data(self):
        meta = self.node["metadata"]
        return meta

    def stores_data(self):
        data = self.node["data"]
        return data

    def get_free_blocks(self):
        free_blocks = self.node["freeBlocks"]
        if free_blocks:
            return int(free_blocks)
        return 0

    def get_free_blocks_pct(self):
        free_blocks_pct = self.node["freeBlocksPct"]
        if free_blocks_pct:
            return int(free_blocks_pct)
        return 0

    def get_free_fragments(self):
        free_fragments = self.node["freeFragments"]
        if free_fragments:
            return int(free_fragments)
        return 0

    def get_free_fragments_pct(self):
        free_fragments_pct = self.node["freeFragmentsPct"]
        if free_fragments_pct:
            return int(free_fragments_pct)
        return 0

    def get_disk_available_for_alloc(self):
        disk_available_for_alloc  = self.node["diskAvailableForAlloc"]
        return disk_available_for_alloc

    def to_json(self):
        return json.dumps(self.nsd_df_dict)

    def get_nsd_df_dict(self):
        return self.nsd_df_dict

    def print_nsd_df(self):
        print("NSD Name                : {0}".format(self.get_nsd_name()))
        print("Storage Pool            : {0}".format(self.get_storage_pool()))
        print("Disk Size               : {0}".format(self.get_disk_size()))
        print("Failure Group           : {0}".format(self.get_failure_group()))
        print("Stores Metadata         : {0}".format(self.stores_meta_data()))
        print("Stores Data             : {0}".format(self.stores_data()))
        print("Free Blocks             : {0}".format(self.get_free_blocks()))
        print("Free Blocks %           : {0}".format(self.get_free_blocks_pct()))
        print("Free Fragments          : {0}".format(self.get_free_fragments()))
        print("Free Fragments %        : {0}".format(self.get_free_fragments_pct()))
        print("Disk Available For Alloc: {0}".format(self.get_disk_available_for_alloc()))


    @staticmethod
    def get_df_info(filesystem_name):
        nsd_df_info_list = []

        # TODO
        # The original code executed the command "/usr/lpp/mmfs/bin/mmdf <fs_name> -d -Y"
        # but this did not work if there were multiple Pools with a separate System Pool.
        # Therefore the "-d" flag has been removed. Check to see why the "-d" flag was
        # was used in the first place
        stdout, stderr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmdf"),
                                                  filesystem_name, "-Y"], 
                                    sh=False)

        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Retrieving filesystem disk space usage failed",
                                     "mmdf",
                                     [filesystem_name, "-Y"],
                                     rc, stdout, stderr)

        df_dict = parse_aggregate_cmd_output(stdout, ["poolTotal", "data", 
                                                      "metadata", "fsTotal", 
                                                      "inode"])

        nsd_df_list = df_dict["nsd"]

        for nsd_df in nsd_df_list:
            nsd_df_instance = SpectrumScaleDf(nsd_df)
            nsd_df_info_list.append(nsd_df_instance)

        return nsd_df_info_list


def main():
    # TODO: Dynamically fetch the Filesystem Names
    nsd_df_list = get_nsd_df_info("FS1")
    for nsd_df in nsd_df_list:
        nsd_df.print_nsd_df()
        print("\n")


if __name__ == "__main__":
    main()

