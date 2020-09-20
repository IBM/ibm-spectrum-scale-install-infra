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
import time
from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_spectrumscale_utils import runCmd, parse_aggregate_cmd_output, \
                         parse_unique_records, GPFS_CMD_PATH, \
                         RC_SUCCESS, SpectrumScaleException

class SpectrumScaleNode:

    def __init__(self, node_dict):
        self.node = node_dict
        self.node_number = int(self.node["nodeNumber"])
        self.daemon_name = self.node["daemonNodeName"]
        self.admin_name = self.node["adminNodeName"]
        self.ip = self.node["ipAddress"]
        self.admin_login = self.node["adminLoginName"]
        self.designation = self.node["designation"]
        self.other_roles = self.node["otherNodeRoles"]
        self.role_alias = self.node["otherNodeRolesAlias"]

    def get_node_number(self):
        return self.node_number

    def get_daemon_node_name(self):
        return self.daemon_name

    def get_admin_node_name(self):
        return self.admin_name

    def get_ip_address(self):
        return self.ip

    def get_admin_login_name(self):
        return self.admin_login

    def get_designation(self):
        # The "designation" field can have the following values:
        #       "quorumManager"
        #       "quorum"
        #       "manager"
        #       ""
        return self.designation

    def get_other_node_roles(self):
        # The "otherNodeRoles" field can have a comma seperated list of 
        # one of the following alphabets
        #     "M"   - cloudNodeMarker
        #     "G"   - gatewayNode
        #     "C"   - cnfsNode
        #     "X"   - cesNode
        #     "C"   - ctdbNode
        #     "I"   - ioNode
        #     "s"   - snmpAgent
        #     "t"   - tealAgent
        #     "Z"   - perfmonNode
        #     "E"   - cnfsEnabled
        #     "D"   - cnfsDisabled
        #     "new" - NEW_NODE
        #     ""    - OLD_NODE
        #     "Q"   - quorumNode
        #     "N"   - nonQuorumNode
        return self.other_roles

    def get_other_node_roles_alias(self):
        # The "otherNodeRolesAlias" field can have a comma seperated list of
        # one of the following 
        #     "gateway"
        #     "ctdb"
        #     "ionode"
        #     "snmp_collector"
        #     "teal_collector"
        #     "perfmon"
        #     "ces"
        #     "cnfs"
        return self.role_alias

    def is_quorum_node(self):
        if "quorum" in self.designation:
            return True
        return False

    def is_manager_node(self):
        if "manager" in (self.designation).lower():
            return True
        return False

    def is_tct_node(self):
        if "M" in self.other_roles:
            return True
        return False

    def is_gateway_node(self):
        if ("G" in self.other_roles or
            "gateway" in self.role_alias):
            return True
        return False

    def is_ctdb_node(self):
        if "ctdb" in self.role_alias:
            return True
        return False

    def is_io_node(self):
        if ("I" in self.other_roles or
            "ionode" in self.role_alias):
            return True
        return False

    def is_snmp_node(self):
        if ("s" in self.other_roles or
            "snmp_collector" in self.role_alias):
            return True
        return False

    def is_teal_node(self):
        if ("t" in self.other_roles or
            "teal_collector" in self.role_alias):
            return True
        return False

    def is_perfmon_node(self):
        if ("Z" in self.other_roles or
            "perfmon" in self.role_alias):
            return True
        return False

    def is_ces_node(self):
        if ("X" in self.other_roles or
            "ces" in self.role_alias):
            return True
        return False

    def is_cnfs_node(self):
        if ("E" in self.other_roles or
            "D" in self.other_roles or
            "cnfs" in self.role_alias):
            return True
        return False

    def to_json(self):
        return json.dumps(self.node)

    def get_node_dict(self):
        return self.node

    def print_node(self):
        print("Node Number            : {0}".format(self.get_node_number()))
        print("Daemon Node Name       : {0}".format(self.get_daemon_node_name()))
        print("IP Address             : {0}".format(self.get_ip_address()))
        print("Admin Node Name        : {0}".format(self.get_admin_node_name()))
        print("Designation            : {0}".format(self.get_designation()))
        print("Other Node Roles       : {0}".format(self.get_other_node_roles()))
        print("Admin Login Name       : {0}".format(self.get_admin_login_name()))
        print("Other Node Roles Alias : {0}".format(self.get_other_node_roles_alias()))
        print("Is Quorum Node         : {0}".format(self.is_quorum_node()))
        print("Is Manager Node        : {0}".format(self.is_manager_node()))
        print("Is TCT Node            : {0}".format(self.is_tct_node()))
        print("Is Gateway Node        : {0}".format(self.is_gateway_node()))
        print("Is CTDB Node           : {0}".format(self.is_ctdb_node()))
        print("Is IO Node             : {0}".format(self.is_io_node()))
        print("Is SNMP Node           : {0}".format(self.is_snmp_node()))
        print("Is Teal Node           : {0}".format(self.is_teal_node()))
        print("Is Perfmon Node        : {0}".format(self.is_perfmon_node()))
        print("Is CES Node            : {0}".format(self.is_ces_node()))
        print("Is CNFS Node           : {0}".format(self.is_cnfs_node()))


    def __str__(self):
        return str("Node Number            : {0}\n"
                   "Daemon Node Name       : {1}\n"
                   "IP Address             : {2}\n"
                   "Admin Node Name        : {3}\n"
                   "Designation            : {4}\n"
                   "Other Node Roles       : {5}\n"
                   "Admin Login Name       : {6}\n"
                   "Other Node Roles Alias : {7}\n"
                   "Is Quorum Node         : {8}\n"
                   "Is Manager Node        : {9}\n"
                   "Is TCT Node            : {10}\n"
                   "Is Gateway Node        : {11}\n"
                   "Is CTDB Node           : {12}\n"
                   "Is IO Node             : {13}\n"
                   "Is SNMP Node           : {14}\n"
                   "Is Teal Node           : {15}\n"
                   "Is Perfmon Node        : {16}\n"
                   "Is CES Node            : {17}\n"
                   "Is CNFS Node           : {18}".format(
                   self.get_node_number(), 
                   self.get_daemon_node_name(), 
                   self.get_ip_address(), 
                   self.get_admin_node_name(), 
                   self.get_designation(), 
                   self.get_other_node_roles(), 
                   self.get_admin_login_name(), 
                   self.get_other_node_roles_alias(), 
                   self.is_quorum_node(), 
                   self.is_manager_node(), 
                   self.is_tct_node(), 
                   self.is_gateway_node(), 
                   self.is_ctdb_node(), 
                   self.is_io_node(), 
                   self.is_snmp_node(), 
                   self.is_teal_node(), 
                   self.is_perfmon_node(), 
                   self.is_ces_node(), 
                   self.is_cnfs_node()))


    @staticmethod
    def get_state(node_names=[]):
        stdout = stderr = ""
        rc = RC_SUCCESS

        cmd = [os.path.join(GPFS_CMD_PATH, "mmgetstate")]

        if len(node_names) == 0:
            cmd.append("-a")
        else:
            # If a set of node names have ben provided, use that instead
            node_name_str = ' '.join(node_names)
            cmd.append("-N")
            cmd.append(node_name_str)
           
        cmd.append("-Y")

        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)

        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Retrieving the node state failed",
                                         cmd[0], cmd[1:],
                                         rc, stdout, stderr)

        node_state_dict = parse_unique_records(stdout)
        node_state_list = node_state_dict["mmgetstate"]

        node_state = {}
        for node in node_state_list:
            node_state[node["nodeName"]] = node["state"]
    
        return node_state


    @staticmethod
    def shutdown_node(node_name, wait=True):
        stdout = stderr = ""
        rc = RC_SUCCESS

        if isinstance(node_name, basestring):
            node_name_str = node_name
            node_name_list = [node_name]
        else:
            node_name_str = ' '.join(node_name)
            node_name_list = node_name
 
        cmd = [os.path.join(GPFS_CMD_PATH, "mmshutdown"), "-N", node_name_str]
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)

        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Shutting down node failed",
                                         cmd[0], cmd[1:],
                                         rc, stdout, stderr)

        if wait:
            # Wait for a maximum of 36 * 5 = 180 seconds (3 minutes)
            MAX_RETRY = 36
            retry = 0
            done = False
            while(not done and retry < MAX_RETRY):
                time.sleep(5)
                node_state = SpectrumScaleNode.get_state(node_name_list)
                done = all("down" in state for state in node_state.values())
                retry = retry + 1

            if not done:
                raise SpectrumScaleException("Shutting down node(s) timed out",
                                             cmd[0], cmd[1:], -1, "",
                                             "Node state is not \"down\" after retries")
        return rc, stdout


    @staticmethod
    def start_node(node_name, wait=True):
        stdout = stderr = ""
        rc = RC_SUCCESS

        if isinstance(node_name, basestring):
            node_name_str = node_name
            node_name_list = [node_name]
        else:
            node_name_str = ' '.join(node_name)
            node_name_list = node_name
 
        cmd = [os.path.join(GPFS_CMD_PATH, "mmstartup"), "-N", node_name_str]
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:], 
                                         -1, stdout, stderr)

        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Starting node failed", cmd[0], 
                                         cmd[1:], rc, stdout, stderr)

        if wait:
            # Wait for a maximum of 36 * 5 = 180 seconds (3 minutes)
            MAX_RETRY = 36
            retry = 0
            done = False
            while(not done and retry < MAX_RETRY):
                time.sleep(5)
                node_state = SpectrumScaleNode.get_state(node_name_list)
                done = all("active" in state for state in node_state.values())
                retry = retry + 1

            if not done:
                raise SpectrumScaleException("Starting node(s) timed out",
                                             cmd[0], cmd[1:], -1, ""
                                             "Node state is not \"active\" after retries")
        return rc, stdout


class SpectrumScaleCluster:

    def __retrieve_cluster_info(self):
        stdout = stderr = ""
        rc = RC_SUCCESS
        cmd = [os.path.join(GPFS_CMD_PATH, "mmlscluster"), "-Y"]
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)
        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Retrieving the cluster information failed",
                                         cmd[0], cmd[1:], rc, stdout, stderr)

        return  parse_aggregate_cmd_output(stdout, 
                                           ["clusterSummary",
                                            "cnfsSummary",
                                            "cesSummary"])

    def __init__(self):
        self.cluster_dict = self.__retrieve_cluster_info()
        self.name = self.cluster_dict["clusterSummary"]["clusterName"]
        self.c_id = self.cluster_dict["clusterSummary"]["clusterId"]
        self.uid_domain = self.cluster_dict["clusterSummary"]["uidDomain"]
        self.rsh_path = self.cluster_dict["clusterSummary"]["rshPath"]
        self.rsh_sudo_wrapper = self.cluster_dict["clusterSummary"]["rshSudoWrapper"]
        self.rcp_path = self.cluster_dict["clusterSummary"]["rcpPath"]
        self.rcp_sudo_wrapper = self.cluster_dict["clusterSummary"]["rcpSudoWrapper"]
        self.repository_type = self.cluster_dict["clusterSummary"]["repositoryType"]
        self.primary_server = self.cluster_dict["clusterSummary"]["primaryServer"]
        self.secondary_server = self.cluster_dict["clusterSummary"]["secondaryServer"]
        

    def get_name(self):
        return self.name

    def get_id(self):
        return self.c_id

    def get_uid_domain(self):
        return self.uid_domain

    def get_rsh_path(self):
        return self.rsh_path

    def get_rsh_sudo_wrapper(self):
        return self.rsh_sudo_wrapper

    def get_rcp_path(self):
        return self.rcp_path

    def get_rcp_sudo_wrapper(self):
        return self.rcp_sudo_wrapper

    def get_repository_type(self):
        return self.repository_type

    def get_primary_server(self):
        return self.primary_server

    def get_secondary_server(self):
        return self.secondary_server

    def __str__(self):
        return str("Cluster Name    : {0}\n"
                   "Cluster ID      : {1}\n"
                   "UID Domain      : {2}\n"
                   "rsh Path        : {3}\n"
                   "rsh Sudo Wrapper: {4}\n"
                   "rcp Path        : {5}\n"
                   "rcp Sudo Wrapper: {6}\n"
                   "Repository Type : {7}\n"
                   "Primary Server  : {8}\n"
                   "Secondary Server: {9}".format(
                   self.get_name(), 
                   self.get_id(),
                   self.get_uid_domain(),
                   self.get_rsh_path(),
                   self.get_rsh_sudo_wrapper(),
                   self.get_rcp_path(),
                   self.get_rcp_sudo_wrapper(),
                   self.get_repository_type(),
                   self.get_primary_server(),
                   self.get_secondary_server()))

    def to_json(self):
        return json.dumps(self.cluster_dict)

    def get_cluster_dict(self):
        return self.cluster_dict

    def get_nodes(self):
        node_list = []
        for node in self.cluster_dict["clusterNode"]:
            node_instance = SpectrumScaleNode(node)
            node_list.append(node_instance)

        return node_list

    @staticmethod
    def delete_node(node_name):
        stdout = stderr = ""
        rc = RC_SUCCESS

        if isinstance(node_name, basestring):
            node_name_str = node_name
        else:
            node_name_str = ' '.join(node_name)
 
        cmd = [os.path.join(GPFS_CMD_PATH, "mmdelnode"), "-N", node_name_str]
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)


        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Deleting node from cluster failed",
                                         cmd[0], cmd[1:], rc, stdout, stderr)

        return rc, stdout


    @staticmethod
    def add_node(node_name, stanza_path):
        stdout = stderr = ""
        rc = RC_SUCCESS

        if isinstance(node_name, basestring):
            node_name_str = node_name
        else:
            node_name_str = ' '.join(node_name)

        cmd = [os.path.join(GPFS_CMD_PATH, "mmaddnode"),
               "-N", stanza_path, "--accept"]

        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:], 
                                         -1, stdout, stderr)

        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Adding node to cluster failed",
                                         cmd[0], cmd[1:],
                                         rc, stdout, stderr)

        return rc, stdout, stderr


    @staticmethod
    def apply_license(node_name, license):
        stdout = stderr = ""
        rc = RC_SUCCESS

        if isinstance(node_name, basestring):
            node_name_str = node_name
        else:
            node_name_str = ' '.join(node_name)

        cmd = [os.path.join(GPFS_CMD_PATH, "mmchlicense"), license, 
               "--accept", "-N", node_name_str]

        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:], 
                                         -1, stdout, stderr)


        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Changing license on  node failed",
                                         cmd[0], cmd[1:], 
                                         rc, stdout, stderr)

        return rc, stdout


    @staticmethod
    def create_cluster(name, stanza_path):
        stdout = stderr = ""
        rc = RC_SUCCESS

        cmd = [os.path.join(GPFS_CMD_PATH, "mmcrcluster"), "-N", stanza_path, 
               "-C", name]
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)


        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Creating cluster failed",
                                         cmd[0], cmd[1:],
                                         rc, stdout, stderr)

        return rc, stdout


    @staticmethod
    def delete_cluster(name):
        stdout = stderr = ""
        rc = RC_SUCCESS

        cmd = [os.path.join(GPFS_CMD_PATH, "mmdelnode"), "-a"]
        try:
            stdout, stderr, rc = runCmd(cmd, sh=False)
        except Exception as e:
            raise SpectrumScaleException(str(e), cmd[0], cmd[1:],
                                         -1, stdout, stderr)


        if rc != RC_SUCCESS:
            raise SpectrumScaleException("Deleting cluster failed",
                                         cmd[0], cmd[1:], 
                                         rc, stdout, stderr)
        return rc, stdout


def main():
    cluster = SpectrumScaleCluster()
    print(cluster.to_json())
    print("\n")

    for node in cluster.get_nodes():
        print(node)
        print("\n")


if __name__ == "__main__":
    main()

