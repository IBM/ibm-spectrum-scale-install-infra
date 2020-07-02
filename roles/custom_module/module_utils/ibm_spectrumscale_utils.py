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
import time
import subprocess
import threading
import logging
import signal
import urllib.request, urllib.parse, urllib.error
import types
from collections import OrderedDict

GPFS_CMD_PATH = "/usr/lpp/mmfs/bin"
RC_SUCCESS    = 0
CMD_TIMEDOUT  = "CMD_TIMEDOUT"

class SpectrumScaleException(Exception):
    _expmsg=""
    _mmcmd=""
    _cmdargs=""
    _rc=0
    _stdout=""
    _stderr=""

    def __init__(self, msg, mmcmd, cmdargs, rc, stdout, stderr):
        self._expmsg  = msg
        self._mmcmd   = mmcmd
        self._cmdargs = nsd_names = " ".join(cmdargs)
        self._rc      = rc
        self._stdout  = stdout
        self._stderr  = stderr

    def get_message(self):
        return self._expmsg

    def __str__(self):
        error_str = ("{0}. "
                     "Command: \"{1}\". "
                     "Arguments: \"{2}\". "
                     "Error Code: {3}. "
                     "Error Message: \"{4}\". ").format(self._expmsg, 
                                                        self._mmcmd,
                                                        self._cmdargs,
                                                        self._rc,
                                                        self._stderr)

        return error_str


######################################
##                                  ##
##        Logger Functions          ##
##                                  ##
######################################
class SpectrumScaleLogger:
    logger = None

    @staticmethod
    def get_logger():
        if SpectrumScaleLogger.logger == None:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

            log_file_handler = logging.FileHandler('/var/log/ibm_specscale_ansible.log')
            log_file_handler.setLevel(logging.DEBUG)
            log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            log_file_handler.setFormatter(log_formatter)
            logger.addHandler(log_file_handler)

            # TODO: Enable once the "Shared Connection eror is rectified"
            # console_handler = logging.StreamHandler()
            # console_handler.setLevel(logging.INFO)
            # console_formatter = logging.Formatter('[%(levelname)s] %(message)s')
            # console_handler.setFormatter(console_formatter)
            # logger.addHandler(console_handler)

            SpectrumScaleLogger.logger = logger

        return SpectrumScaleLogger.logger

    @staticmethod
    def shutdown():
        if SpectrumScaleLogger.logger:
            logging.shutdown()


######################################
##                                  ##
##       Utility Functions          ##
##                                  ##
######################################
def decode(input_string):
    return urllib.parse.unquote(input_string)


def _stop_process(proc, logger, log_cmd, timeout):
    try:
        if proc.poll() is None:
            logger.info("Command %s timed out after %s sec. Sending SIGTERM", log_cmd, timeout)
            print("Command %s timed out after %s sec. Sending SIGTERM", log_cmd, timeout)
            os.kill(proc.pid, signal.SIGTERM)  # SIGKILL or SIGTERM

            time.sleep(0.5)
            if proc.poll() is None:
                logger.info("Command %s timed out after %s sec. Sending SIGKILL", log_cmd, timeout)
                print("Command %s timed out after %s sec. Sending SIGKILL", log_cmd, timeout)
                os.kill(proc.pid, signal.SIGKILL)
    except Exception as e:
        logger.warning(str(e))
        print(str(e))


def runCmd(cmd, timeout=300, sh=False, env=None, retry=0):
    """
    Execute an external command, read the output and return it.
    @param cmd (str|list of str): command to be executed
    @param timeout (int): timeout in sec, after which the command is forcefully terminated
    @param sh (bool): True if the command is to be run in a shell and False if directly
    @param env (dict): environment variables for the new process (instead of inheriting from the current process)
    @param retry (int): number of retries on command timeout
    @return: (stdout, stderr, rc) (str, str, int): the output of the command
    """

    logger = SpectrumScaleLogger.get_logger()

    if isinstance(cmd, str):
        log_cmd = cmd
    else:
        log_cmd = ' '.join(cmd)

    t_start = time.time()
    try:
        if env is not None:
            fullenv = dict(os.environ)
            fullenv.update(env)
            env = fullenv
        # create the subprocess, ensuring a new process group is spawned
        # so we can later kill the process and all its child processes
        proc = subprocess.Popen(cmd, shell=sh,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                close_fds=False, env=env)

        timer = threading.Timer(timeout, _stop_process, [proc, logger, log_cmd, timeout])
        timer.start()

        (sout, serr) = proc.communicate()
        timer.cancel()  # stop the timer when we got data from process

        ret = proc.poll()
    except OSError as e:
        logger.debug(str(e))
        sout = ""
        serr = str(e)
        ret = 127 if "No such file" in serr else 255
    finally:
        try:
            proc.stdout.close()
            proc.stderr.close()
        except:  #pylint: disable=bare-except
            pass

    t_run = time.time() - t_start
    logger.debug("runCmd: Command executed: {0} Start time: {1} End time: {2} "
                 "Total time: {3}".format(log_cmd, t_start, 
                                          time.time(), t_run))

    cmd_timeout = ret in (-signal.SIGTERM, -signal.SIGKILL)  # 143,137
    if ret == -6 and retry >= 0 :  # special handling for sigAbrt
        logger.warning("runCmd: retry abrt %s with subprocess %s", cmd, s32)
        (sout, serr, ret) = runCmd(cmd, timeout, sh, env, -1)

    if cmd_timeout and retry > 0:
        retry -= 1
        logger.warning("runCmd: Retry command %s counter: %s", cmd, retry)
        (sout, serr, ret) = runCmd(cmd, timeout, sh, env, retry)
    elif cmd_timeout:
        serr = CMD_TIMEDOUT
        logger.warning("runCmd: %s Timeout:%d ret:%s", cmd, timeout, ret)
    else:
        logger.debug("runCmd: %s :(%d) ret:%s \n%s \n%s", cmd, timeout, ret, serr, sout)

    return (sout, serr, ret)


######################################
##                                  ##
##        Parse Functions           ##
##                                  ##
######################################

# NOTE: The machine parsable "mm" list (-Y) commands fall into three categories
# in terms of how the information is organized and therefore should be parsed.
# Each of these different formats are listed below along with the appropriate 
# parsing functions

#############################################
#                                           #
#              TYPE 1                       #
#                                           #
#############################################
#
# "mm" command output type #1
#
#  mmlscluster:clusterSummary:HEADER:version:reserved:reserved:clusterName:clusterId:uidDomain:rshPath:rshSudoWrapper:rcpPath:rcpSudoWrapper:repositoryType:primaryServer:secondaryServer:
#  mmlscluster:clusterNode:HEADER:version:reserved:reserved:nodeNumber:daemonNodeName:ipAddress:adminNodeName:designation:otherNodeRoles:adminLoginName:otherNodeRolesAlias:
#  mmlscluster:cnfsSummary:HEADER:version:reserved:reserved:cnfsSharedRoot:cnfsMoundPort:cnfsNFSDprocs:cnfsReboot:cnfsMonitorEnabled:cnfsGanesha:
#  mmlscluster:cnfsNode:HEADER:version:reserved:reserved:nodeNumber:daemonNodeName:ipAddress:cnfsState:cnfsGroupId:cnfsIplist:
#  mmlscluster:cesSummary:HEADER:version:reserved:reserved:cesSharedRoot:EnabledServices:logLevel:addressPolicy:
#  mmlscluster:cesNode:HEADER:version:reserved:reserved:nodeNumber:daemonNodeName:ipAddress:cesGroup:cesState:cesIpList:
#  mmlscluster:cloudGatewayNode:HEADER:version:reserved:reserved:nodeNumber:daemonNodeName:
#  mmlscluster:clusterSummary:0:1:::cluster.domain.com:2936932203756487754:cluster.domain.com:/usr/bin/ssh:no:/usr/bin/scp:no:CCR:server-1.domain.com::
#  mmlscluster:clusterNode:0:1:::1:server-1.domain.com:10.0.0.1:server-1.domain.com:quorum:Z::perfmon:
#  mmlscluster:clusterNode:0:1:::2:server-3.domain.com:10.0.0.4:server-3.domain.com:quorumManager:Z::perfmon:
#  mmlscluster:clusterNode:0:1:::3:server-4.domain.com:10.0.0.4:server-4.domain.com:quorumManager:Z::perfmon:
#  mmlscluster:clusterNode:0:1:::4:server-2.domain.com:10.0.0.2:server-2.domain.com::Z::perfmon:
#
#
# The above output is parsed and represented in JSON as follows:
#
# {
#  "clusterSummary": {
#    "version": "1",
#    "clusterName": "cluster.domain.com",
#    "clusterId": "2936932203756844651",
#    "uidDomain": "cluster.domain.com",
#    "rshPath": "/usr/bin/ssh",
#    "rshSudoWrapper": "no",
#    "rcpPath": "/usr/bin/scp",
#    "rcpSudoWrapper": "no",
#    "repositoryType": "CCR",
#    "primaryServer": "server-1.domain.com",
#    "secondaryServer": ""
#  },
#  "clusterNode": [
#    {
#      "version": "1",
#      "nodeNumber": "1",
#      "daemonNodeName": "server-1.domain.com",
#      "ipAddress": "10.0.0.1",
#      "adminNodeName": "server-1.domain.com",
#      "designation": "quorum",
#      "otherNodeRoles": "Z,X",
#      "adminLoginName": "",
#      "otherNodeRolesAlias": "perfmon,ces"
#    },
#    {
#      "version": "1",
#      "nodeNumber": "2",
#      "daemonNodeName": "server-3.domain.com",
#      "ipAddress": "10.0.0.4",
#      "adminNodeName": "server-3.domain.com",
#      "designation": "quorumManager",
#      "otherNodeRoles": "Z",
#      "adminLoginName": "",
#      "otherNodeRolesAlias": "perfmon"
#    },
#    {
#      "version": "1",
#      "nodeNumber": "3",
#      "daemonNodeName": "server-4.domain.com",
#      "ipAddress": "10.0.0.4",
#      "adminNodeName": "server-4.domain.com",
#      "designation": "quorumManager",
#      "otherNodeRoles": "Z",
#      "adminLoginName": "",
#      "otherNodeRolesAlias": "perfmon"
#    },
#    {
#      "version": "1",
#      "nodeNumber": "4",
#      "daemonNodeName": "server-2.domain.com",
#      "ipAddress": "10.0.0.2",
#      "adminNodeName": "server-2.domain.com",
#      "designation": "",
#      "otherNodeRoles": "Z,X",
#      "adminLoginName": "",
#      "otherNodeRolesAlias": "perfmon,ces"
#    }
#  ],
#  "cesSummary": {
#    "version": "1",
#    "cesSharedRoot": "/ibm/cesSharedRoot",
#    "EnabledServices": "SMB,NFS",
#    "logLevel": "0",
#    "addressPolicy": "even-coverage"
#  },
#  "cesNode": [
#    {
#      "version": "1",
#      "nodeNumber": "1",
#      "daemonNodeName": "server-1.domain.com",
#      "ipAddress": "10.0.0.1",
#      "cesGroup": "",
#      "cesState": "e",
#      "cesIpList": "10.0.0.5,10.0.0.6"
#    },
#    {
#      "version": "1",
#      "nodeNumber": "4",
#      "daemonNodeName": "server-2.domain.com",
#      "ipAddress": "10.0.0.2",
#      "cesGroup": "",
#      "cesState": "e",
#      "cesIpList": "10.0.0.7,10.0.0.8"
#    }
#  ]
#}
#
# TODO: Change function name to something more appropriate
def parse_aggregate_cmd_output(cmd_raw_out, summary_records, header_index=2):
    data_out = OrderedDict()
    headers = OrderedDict()

    if isinstance(cmd_raw_out, str):
        lines = cmd_raw_out.splitlines()
    else:
        # for python3, this will be sent back in bytes, so decode first 
        lines = cmd_raw_out.decode("utf-8").splitlines() 

    for line in lines:
        values = line.split(":")
        if len(values) < 3:
            continue

        command = values[0]
        datatype = values[1] or values[0]
        if datatype == "":
            continue

        if values[header_index] == 'HEADER':
            headers[datatype] = values
            continue

        columnNames = headers[datatype]

        json_object = OrderedDict()
        for key, value in zip(columnNames[header_index+1:], 
                              values[header_index+1:]):
            json_object[key] =  decode(value)

        if "" in json_object:
            del json_object[""]
        if 'reserved' in json_object:
            del json_object['reserved']

        # Summary records should only exist once
        if datatype in summary_records:
            json_d_type = "object"
            data_out[datatype] = json_object
        else:
            json_d_type = "array"
            json_array = []
            if datatype in data_out.keys():
                # An element in the array already exists
                json_array = data_out[datatype]
            json_array.append(json_object)
            data_out[datatype] = json_array

    return data_out


#############################################
#                                           #
#              TYPE 2                       #
#                                           #
#############################################
#
# "mm" command output type #2
#
#  mmlsfs::HEADER:version:reserved:reserved:deviceName:fieldName:data:remarks:
#  mmlsfs::0:1:::FS1:minFragmentSize:8192::
#  mmlsfs::0:1:::FS1:inodeSize:4096::
#  mmlsfs::0:1:::FS1:indirectBlockSize:32768::
#  mmlsfs::0:1:::FS1:defaultMetadataReplicas:2::
#  mmlsfs::0:1:::FS1:maxMetadataReplicas:2::
#  mmlsfs::0:1:::FS1:defaultDataReplicas:1::
#  mmlsfs::0:1:::FS1:maxDataReplicas:2::
#  mmlsfs::0:1:::FS1:blockAllocationType:scatter::
#  mmlsfs::0:1:::FS1:fileLockingSemantics:nfs4::
#  mmlsfs::0:1:::FS1:ACLSemantics:nfs4::
#  mmlsfs::0:1:::FS1:numNodes:100::
#  mmlsfs::0:1:::FS1:blockSize:4194304::
#  mmlsfs::0:1:::FS1:quotasAccountingEnabled:none::
#  mmlsfs::0:1:::FS1:quotasEnforced:none::
#  mmlsfs::0:1:::FS1:defaultQuotasEnabled:none::
#  mmlsfs::0:1:::FS1:perfilesetQuotas:No::
#  mmlsfs::0:1:::FS1:filesetdfEnabled:No::
#  mmlsfs::0:1:::FS1:filesystemVersion:22.00 (5.0.4.0)::
#  mmlsfs::0:1:::FS1:filesystemVersionLocal:22.00 (5.0.4.0)::
#  mmlsfs::0:1:::FS1:filesystemVersionManager:22.00 (5.0.4.0)::
#  mmlsfs::0:1:::FS1:filesystemVersionOriginal:22.00 (5.0.4.0)::
#  mmlsfs::0:1:::FS1:filesystemHighestSupported:22.00 (5.0.4.0)::
#  mmlsfs::0:1:::FS1:create-time:Fri Feb 21 01%3A36%3A21 2020::
#  mmlsfs::0:1:::FS1:DMAPIEnabled:No::
#  mmlsfs::0:1:::FS1:logfileSize:33554432::
#  mmlsfs::0:1:::FS1:exactMtime:Yes::
#  mmlsfs::0:1:::FS1:suppressAtime:relatime::
#  mmlsfs::0:1:::FS1:strictReplication:whenpossible::
#  mmlsfs::0:1:::FS1:fastEAenabled:Yes::
#  mmlsfs::0:1:::FS1:encryption:No::
#  mmlsfs::0:1:::FS1:maxNumberOfInodes:513024::
#  mmlsfs::0:1:::FS1:maxSnapshotId:0::
#  mmlsfs::0:1:::FS1:UID:090B5475%3A5E4F9685::
#  mmlsfs::0:1:::FS1:logReplicas:0::
#  mmlsfs::0:1:::FS1:is4KAligned:Yes::
#  mmlsfs::0:1:::FS1:rapidRepairEnabled:Yes::
#  mmlsfs::0:1:::FS1:write-cache-threshold:0::
#  mmlsfs::0:1:::FS1:subblocksPerFullBlock:512::
#  mmlsfs::0:1:::FS1:storagePools:system::
#  mmlsfs::0:1:::FS1:file-audit-log:No::
#  mmlsfs::0:1:::FS1:maintenance-mode:No::
#  mmlsfs::0:1:::FS1:disks:nsd1;nsd2::
#  mmlsfs::0:1:::FS1:automaticMountOption:yes::
#  mmlsfs::0:1:::FS1:additionalMountOptions:none::
#  mmlsfs::0:1:::FS1:defaultMountPoint:%2Fibm%2FFS1::
#
# The above output is parsed and represented in JSON as follows:
#
#{
#   filesystems : [
#                    {
#                        deviceName      : FS1
#                        properties      : [
#                                             {
#                                                fieldName: minFragmentSize 
#                                                data     : 8192
#                                                remarks  : ""
#                                             },
#                                             {
#                                                fieldName: inodeSize
#                                                data     : 4096
#                                                remarks  : ""
#                                             }
#                                          ]
#                        
#                    },
#                    {
#                        deviceName      : FS2
#                        properties      : [
#                                             {
#                                                fieldName: minFragmentSize 
#                                                data     : 8192
#                                                remarks  : ""
#                                             },
#                                             {
#                                                fieldName: inodeSize
#                                                data     : 4096
#                                                remarks  : ""
#                                             }
#                                          ]
#                        
#                    }
#                 ]
#}
#
# TODO: Change function name to something more appropriate
def parse_simple_cmd_output(cmd_raw_out, cmd_key, cmd_prop_name, 
                            datatype="", header_index=2):
    data_out = OrderedDict()
    headers = OrderedDict()

    if isinstance(cmd_raw_out, str):
        lines = cmd_raw_out.splitlines()
    else:
        lines = cmd_raw_out

    for line in lines:
        values = line.split(":")
        if len(values) < 3:
            continue

        command = values[0]

        if not datatype:
            datatype = values[1] or values[0]
        if datatype == "":
            continue

        if values[header_index] == 'HEADER':
            headers[datatype] = values
            continue

        columnNames = headers[datatype]

        json_object = OrderedDict()
        instance_key = ""
        for key, value in zip(columnNames[header_index+1:], 
                              values[header_index+1:]):
            if cmd_key in key:
                instance_key = value
            else:
                json_object[key] =  decode(value)

        if "" in json_object:
            del json_object[""]
        if 'reserved' in json_object:
            del json_object['reserved']

        json_array = []
        obj_found = False
        if datatype in data_out.keys():
            # List of OrederDict
            json_array = data_out[datatype]
            prop_list = []
            # Each obj is an OrderDict
            for obj in json_array:
                key_val = obj[cmd_key]
                if instance_key in key_val:
                    # We found the obj to which this record should be added
                    prop_list = obj[cmd_prop_name]
                    prop_list.append(json_object)
                    obj[cmd_prop_name] = prop_list
                    obj_found = True
                    break

        if not obj_found:
            prop_list = []
            prop_list.append(json_object)
            device_dict = OrderedDict()
            device_dict[cmd_key] = instance_key
            device_dict[cmd_prop_name] = prop_list
            json_array.append(device_dict)
            
        data_out[datatype] = json_array

    return data_out


#############################################
#                                           #
#              TYPE 3                       #
#                                           #
#############################################
#
# "mm" command output type #3
#
#  mmlsnsd:nsd:HEADER:version:reserved:reserved:fileSystem:diskName:volumeId:serverList:thinDisk:
#  mmlsnsd:nsd:0:1:::FS1:nsd1:090B54755E4F84E6:server-3.domain.com,server-4.domain.com::
#  mmlsnsd:nsd:0:1:::FS1:nsd2:090B54765E4F84E8:server-4.domain.com,server-3.domain.com::
#  mmlsnsd:nsd:0:1:::FS2:nsd3:090B54755E4F84EA:server-3.domain.com,server-4.domain.com::
#  mmlsnsd:nsd:0:1:::FS2:nsd4:090B54765E4F84EC:server-4.domain.com,server-3.domain.com::
#
# The above output is parsed and represented in JSON as follows:
#
#  {
#    mmlsnsd : [
#                 {
#                    diskName  : "nsd1"
#                    fileSystem: "FS1"
#                    volumeId  : "090B54755E4F84E6"
#                    serverList: "server-3.domain.com,server-4.domain.com"
#                    thinDisk  : ""
#                 }
#                 {
#                    diskName  : "nsd2"
#                    fileSystem: "FS1"
#                    volumeId  : "090B54765E4F84E8"
#                    serverList: "server-4.domain.com,server-3.domain.com"
#                    thinDisk  : ""
#                 }
#                 {
#                    diskName  : "nsd3"
#                    fileSystem: "FS2"
#                    volumeId  : "090B54755E4F84EA"
#                    serverList: "server-3.domain.com,server-4.domain.com"
#                    thinDisk  : ""
#                 }
#                 {
#                    diskName  : "nsd4"
#                    fileSystem: "FS2"
#                    volumeId  : "090B54765E4F84EC"
#                    serverList: "server-4.domain.com,server-3.domain.com"
#                    thinDisk  : ""
#                 }
#              ]
#  }
#
# TODO: Change function name to something more appropriate
def parse_unique_records(cmd_raw_out, datatype="", header_index=2):
    data_out = OrderedDict()
    headers = OrderedDict()

    if isinstance(cmd_raw_out, str):
        lines = cmd_raw_out.splitlines()
    else:
        lines = cmd_raw_out

    for line in lines:
        values = line.split(":")
        if len(values) < 3:
            continue

        command = values[0]

        if not datatype:
            datatype = values[1] or values[0]
        if datatype == "":
            continue

        if values[header_index] == 'HEADER':
            headers[datatype] = values
            continue

        columnNames = headers[datatype]

        json_object = OrderedDict()
        for key, value in zip(columnNames[header_index+1:], 
                              values[header_index+1:]):
            json_object[key] =  decode(value)

        if "" in json_object:
            del json_object[""]
        if 'reserved' in json_object:
            del json_object['reserved']

        json_array = []
        if datatype in data_out.keys():
            # List of OrederDict
            json_array = data_out[datatype]
        json_array.append(json_object)
            
        data_out[datatype] = json_array

    return data_out


###############################################################################
##                                                                           ##
##                              Main Function                                ##
##                                                                           ##
###############################################################################

def main():
    cmd = "cluster"
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if "fs" in cmd:
            cmd = "filesystem"

    sout = ""
    serr = ""
    rc = 0
    if "cluster" in cmd:
        sout, serr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmlscluster"),"-Y"], sh=False)
        out_list = parse_aggregate_cmd_output(sout, ["clusterSummary", "cnfsSummary", "cesSummary"])
    elif "filesystem" in cmd:
        sout, serr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmlsfs"),"all","-Y"], sh=False)
        out_list = parse_simple_cmd_output(sout, "deviceName", "properties", "filesystems")
    elif "mount" in cmd:
        sout, serr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmlsmount"),"all","-Y"], sh=False)
        out_list = parse_simple_cmd_output(sout, "realDevName", "mounts", "filesystem_mounts")
    elif "config" in cmd:
        sout, serr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmlsconfig"),"-Y"], sh=False)
        out_list = parse_unique_records(sout)
    elif "df" in cmd:
        sout, serr, rc = runCmd([os.path.join(GPFS_CMD_PATH, "mmdf"),"FS1", "-Y"], sh=False)
        out_list = parse_aggregate_cmd_output(sout, ["poolTotal", "data", "metadata", "fsTotal", "inode"])


    if rc:
        print("Error executing command: %s %s", sout, serr)

    json_str = json.dumps(out_list, indent=2)
    print(json_str)


if __name__ == "__main__":
    main()

