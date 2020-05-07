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
module: ibm_ss_filesystem
short_description: IBM Spectrum Scale Filesystem Management
version_added: "0.0"

description:
    - This module can be used to create or delete an IBM Spectrum Scale
      filesystem or retrieve information about the filesystem.

options:
    op:
        description:
            - An operation to execute on the IBM Spectrum Scale filesystem.
              Mutually exclusive with the state operand.
        required: false
    state:
        description:
            - The desired state of the filesystem.
        required: false
        default: "present"
        choices: [ "present", "absent" ]
    stanza:
        description:
            - Filesystem blueprint that defines membership and NSD attributes
        required: false
    name:
        description:
            - The name of the filesystem to be created, deleted or whose 
              information is to be retrieved
        required: false
    block_size:
        description:
            - The filesystem blocksize
        required: false
    default_metadata_replicas:
        description:
            - The filesystem defaultMetadataReplicas
        required: false
    default_data_replicas:
        description:
            - The filesystem defaultDataReplicas
        required: false
    num_nodes:
        description:
            - The filesystem numNodes
        required: false
    automatic_mount_option:
        description:
            - The filesystem automaticMountOption 
        required: false
    default_mount_point:
        description:
            - The filesystem defaultMountPoint
        required: false

'''

EXAMPLES = '''
# Retrive information about an existing IBM Spectrum Scale filesystem
- name: Retrieve IBM Spectrum Scale filesystem information
  ibm_ss_filesystem:
    op: get

# Create a new IBM Spectrum Scale Filesystem
- name: Create an IBM Spectrum Scale filesystem
  ibm_ss_filesystem:
    state: present
    stanza: "/tmp/filesystem-stanza"
    name: "FS1"

# Delete an existing IBM Spectrum Scale Filesystem
- name: Delete an IBM Spectrum Scale filesystem
  ibm_ss_filesystem:
    state: absent
    name: "FS1"
'''

RETURN = '''
changed:
    description: A boolean indicating if the module has made changes
    type: boolean
    returned: always

msg:
    description: The output from the filesystem create/delete operations
    type: str
    returned: when supported

rc:
    description: The return code from the IBM Spectrum Scale mm command
    type: int
    returned: always

results:
    description: The JSON document containing the filesystem information
    type: str
    returned: when supported
'''

import json
import sys
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.ibm_spectrum_scale.install_infra.plugins.module_utils.ibm_ss_utils import runCmd, parse_simple_cmd_output, RC_SUCCESS

MMLSFS_DATATYPE="filesystems"
MMLSFS_KEY="deviceName"
MMLSFS_PROPERTY_NAME="properties"

def get_filesystem_info():
    msg = result_json = ""
    stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmlsfs","all","-Y"], sh=False)

    if rc == RC_SUCCESS:
        result_dict = parse_simple_cmd_output(
                                               stdout, 
                                               MMLSFS_KEY, 
                                               MMLSFS_PROPERTY_NAME,
                                               MMLSFS_DATATYPE
                                             )
        result_json = json.dumps(result_dict)
        msg = "The command \"mmlsfs\" executed successfully"
    else:
        msg = stderr

    return rc, msg, result_json


def create_filesystem(name, stanza_path):
    # TODO: Make This idempotent
    stdout, stderr, rc = runCmd(["/usr/lpp/mmfs/bin/mmcrfs",
                                 name,
                                 "-F", stanza_path,
                                 "-B", block_size,
                                 "-m", default_metadata_replicas,
                                 "-r", default_data_replicas,
                                 "-n", num_nodes,
                                 "-A", automatic_mount_option,
                                 "-T", default_mount_point],
                                sh=False)

    if rc == RC_SUCCESS:
        msg = stdout
    else:
        msg = stderr

    return rc, msg


def delete_filesystem(name):
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
                                        ),
                           block_size = dict(
                                          type='str', 
                                          required=False
                                        ),
                           num_nodes  = dict(
                                          type='str', 
                                          required=False
                                        ),
                           default_metadata_replicas = dict(
                                                             type='str', 
                                                             required=False
                                                           ),
                           default_data_replicas     = dict(
                                                             type='str', 
                                                             required=False
                                                           ),
                           automatic_mount_option    = dict(
                                                             type='str', 
                                                             required=False
                                                           ),
                           default_mount_point       = dict(
                                                             type='str', 
                                                             required=False
                                                           )
                         )


    scale_req_if_args = [
                          [ "state", "present", [ "stanza", 
                                                  "name", 
                                                  "block_size", 
                                                  "num_nodes", 
                                                  "default_metadata_replicas", 
                                                  "default_data_replicas", 
                                                  "automatic_mount_option", 
                                                  "default_mount_point" ] 
                          ],
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
        # Retrieve the IBM Spectrum Scae filesystem information
        rc, msg, result_json = get_filesystem_info()
    elif module.params['state']:
        if "present" in module.params['state']:
            # Create a new IBM Spectrum Scale cluster
            rc, msg = create_filesystem(
                                         module.params['stanza'],
                                         module.params['name'],
                                         module.params["block_size"], 
                                         module.params["num_nodes"], 
                                         module.params["default_metadata_replicas"], 
                                         module.params["default_data_replicas"], 
                                         module.params["automatic_mount_option"], 
                                         module.params["default_mount_point"] 
                                       )
        else:
            # Delete the existing IBM Spectrum Scale cluster
            rc, msg = delete_filesystem(module.params['name'])

        if rc == RC_SUCCESS:
            state_changed = True

    # Module is done. Return back the result
    module.exit_json(changed=state_changed, msg=msg, rc=rc, result=result_json)


if __name__ == '__main__':
    main() 
