#!/usr/bin/python
# -*- coding: utf-8 -*-

# author: IBM Corporation
# description: Highly-customizable Ansible module 
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
module: ibm_ss_cluster
short_description: IBM Spectrum Scale Cluster Management
version_added: "0.0"

description:
    - This module can be used to create or delete an IBM Spectrum Scale
      Cluster or retrieve information about the cluster.

options:
    op:
        description:
            - An operation to execute on the IBM Spectrum Scale Cluster.
              Mutually exclusive with the state operand.
        required: false
    state:
        description:
            - The desired state of the cluster.
        required: false
        default: "present"
        choices: [ "present", "absent" ]
    stanza:
        description:
            - Cluster blueprint that defines membership and node attributes
        required: false
    name:
        description:
            - The name of the cluster to be created, deleted or whose 
              information is to be retrieved
        required: false

'''

EXAMPLES = '''
# Retrive information about an existing IBM Spectrum Scale cluster
- name: Retrieve IBM Spectrum Scale Cluster information
  ibm_ss_cluster:
    op: list

# Create a new IBM Spectrum Scale Cluster
- name: Create an IBM Spectrum Scale Cluster
  ibm_ss_cluster:
    state: present
    stanza: "/tmp/stanza"
    name: "host-01"

# Delete an existing IBM Spectrum Scale Cluster
- name: Delete an IBM Spectrum Scale Cluster
  ibm_ss_cluster:
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
import json
import sys
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_ss_utils import runCmd, parse_aggregate_cmd_output, RC_SUCCESS

MMLSCLUSTER_SUMMARY_FIELDS=['clusterSummary','cnfsSummary', 'cesSummary']


def get_cluster_info():
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


def create_cluster(name, stanza_path):
    # TODO: Make This idempotent
    stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmcrcluster",
                                 "-N", stanza_path,
                                 "-C", name],
                                sh=False)

    if rc == RC_SUCCESS:
        msg = stdout
    else:
        msg = stderr

    return rc, msg


def delete_cluster(name):
    # TODO: Implement
    rc = RC_SUCCESS
    msg = ""
    return rc, msg


def main():
    # Setup the module argument specifications
    scale_arg_spec = dict(
                           op     = dict(
                                          type='str', 
                                          choices=['get'], 
                                          required=False
                                        ),
                           state  = dict(
                                          type='str', 
                                          choices=['present', 'absent'], 
                                          required=False
                                        ),
                           stanza = dict(
                                          type='str', 
                                          required=False
                                        ),
                           name   = dict(
                                          type='str', 
                                          required=False
                                        )
                         )


    scale_req_if_args = [
                          [ "state", "present", [ "stanza", "name" ] ],
                          [ "state", "absent", [ "name" ] ]
                        ]

    scale_req_one_of_args = [
                              [ "op", "state" ]
                            ]

    # Instantiate the Ansible module with the given argument specifications
    module = AnsibleModule(
                            argument_spec=scale_arg_spec,
                            required_one_of=scale_req_one_of_args,
                            required_if=scale_req_if_args 
                          )

    rc = RC_SUCCESS
    msg = result_json = ""
    state_changed = False
    if module.params['op'] and "get" in module.params['op']:
        # Retrieve the IBM Spectrum Scale cluster information
        rc, msg, result_json = get_cluster_info()
    elif module.params['state']:
        if "present" in module.params['state']:
            # Create a new IBM Spectrum Scale cluster
            rc, msg = create_cluster(
                                       module.params['name'],
                                       module.params['stanza']
                                    )
        else:
            # Delete the existing IBM Spectrum Scale cluster
            rc, msg = delete_cluster(module.params['name'])

        if rc == RC_SUCCESS:
            state_changed = True

    # Module is done. Return back the result
    module.exit_json(changed=state_changed, msg=msg, rc=rc, result=result_json)


if __name__ == '__main__':
    main() 
