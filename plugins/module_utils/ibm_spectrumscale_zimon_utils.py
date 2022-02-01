#!/usr/bin/python3
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
import re
import json
import time

try:
    from ansible.module_utils.ibm_spectrumscale_utils import runCmd, \
            GPFS_CMD_PATH, RC_SUCCESS, SpectrumScaleException
except:
    from ibm_spectrumscale_utils import runCmd, GPFS_CMD_PATH, \
            RC_SUCCESS, SpectrumScaleException


def get_zimon_collectors():
    """
        This function returns zimon collector node ip's.
    """
    stdout = stderr = ""
    rc = RC_SUCCESS

    cmd = []
    mmcmd_idx = 1
    if admin_ip:
        cmd.extend(["ssh", admin_ip])
        mmcmd_idx = len(cmd) + 1

    cmd.extend([os.path.join(GPFS_CMD_PATH, "mmperfmon"), "config", "show"])

    try:
        stdout, stderr, rc = runCmd(cmd, sh=False)
    except Exception as e:
        raise SpectrumScaleException(str(e), cmd[0:mmcmd_idx], cmd[mmcmd_idx:],
                                     -1, stdout, stderr)

    if rc != RC_SUCCESS:
        raise SpectrumScaleException("Retrieving Zimon information failed",
                                     cmd[0:mmcmd_idx], cmd[mmcmd_idx:], rc,
                                     stdout, stderr)

    output = stdout.splitlines()
    col_regex = re.compile(r'colCandidates\s=\s(?P<collectors>.*)')
    for cmd_line in output:
        if col_regex.match(cmd_line):
            collectors = col_regex.match(cmd_line).group('collectors')

    collectors = collectors.replace("\"", '').replace(" ", '')
    collectors = collectors.split(',')

    return collectors


def main():
    zimon_collectors_list = get_zimon_collectors()
    for collector in zimon_collectors_list:
        print(collector)


if __name__ == "__main__":
    main()

