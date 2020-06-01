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
import traceback
from ansible.module_utils.basic import AnsibleModule

try: 
    from ansible.module_utils.ibm_ss_utils import RC_SUCCESS
except:
    from ibm_ss_utils import RC_SUCCESS

try:
    from ansible.module_utils.ibm_ss_filesystem_utils import SpectrumScaleFS
except:
    from ibm_ss_filesystem_utils import SpectrumScaleFS


def main():
    logger.debug("---------------------------------------")
    logger.debug("Function Entry: ibm_ss_filesystem.main()")
    logger.debug("---------------------------------------")

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
        # Retrieve the IBM Spectrum Scale filesystem information
        try:
            result_dict = {}
            filesystem_list = []

            filesystems = SpectrumScaleFS.get_filesystems()
            for fs in filesystems:
                filesystem_info = {}
                filesystem_info["deviceName"] = fs.get_device_name()
                filesystem_info["properties"] = fs.get_properties_list()
                filesystem_list.append(filesystem_info)
            
            result_dict["filesystems"] = filesystem_list
            result_json = json.dumps(result_dict)            

            msg = "Successfully retrieved filesystem information"
        except Exception as e:
            st = traceback.format_exc()
            e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
            module.fail_json(msg=e_msg)
    elif module.params['state']:
        if "present" in module.params['state']:
            # Create a new IBM Spectrum Scale cluster
            try:
                rc, result_json = SpectrumScaleFS.create_filesystem(
                                             module.params['stanza'],
                                             module.params['name'],
                                             module.params["block_size"], 
                                             module.params["num_nodes"], 
                                             module.params["default_metadata_replicas"], 
                                             module.params["default_data_replicas"], 
                                             module.params["automatic_mount_option"], 
                                             module.params["default_mount_point"] 
                                           )
                msg = "Successfully created filesystem"
            except Exception as e:
                st = traceback.format_exc()
                e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
                module.fail_json(msg=e_msg)
        else:
            # Delete the existing IBM Spectrum Scale cluster
            try:
                rc, result_json = SpectrumScaleFS.delete_filesystem(
                                             module.params['name']
                                          )
                msg = "Successfully deleted filesystem"
            except Exception as e:
                st = traceback.format_exc()
                e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
                module.fail_json(msg=e_msg)

        if rc == RC_SUCCESS:
            state_changed = True

    logger.debug("---------------------------------------")
    logger.debug("Function Exit: ibm_ss_filesystem.main()")
    logger.debug("---------------------------------------")

    # Module is done. Return back the result
    module.exit_json(changed=state_changed, msg=msg, rc=rc, result=result_json)


if __name__ == '__main__':
    main() 
