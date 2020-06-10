#!/usr/bin/python

# author: IBM Corporation
# description: Highly-customizable Ansible role module
# for installing and configuring IBM Spectrum Scale (GPFS)
# company: IBM
# license: Apache-2.0

import os
import re
import json
import time
from ibm_ss_utils import runCmd, GPFS_CMD_PATH, RC_SUCCESS, \
                         SpectrumScaleException

def get_zimon_collectors():
    """
        This function returns zimon collector node ip's.
    """
    stdout, stderr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmperfmon"),
                                 "config", "show"])

    if rc != RC_SUCCESS:
        raise SpectrumScaleException("Retrieving Zimon information failed",
                                 "mmperfmon",
                                 ["config", "show"],
                                 rc, stdout, stderr)

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

