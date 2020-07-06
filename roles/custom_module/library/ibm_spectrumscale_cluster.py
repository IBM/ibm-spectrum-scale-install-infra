#!/usr/bin/python
# -*- coding: utf-8 -*-
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

ANSIBLE_METADATA = {
                       'status': ['preview'],
                       'supported_by': 'IBM',
                       'metadata_version': '1.0'
                   }


DOCUMENTATION = '''
---
module: ibm_spectrumscale_cluster
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
  ibm_spectrumscale_cluster:
    op: list

# Create a new IBM Spectrum Scale Cluster
- name: Create an IBM Spectrum Scale Cluster
  ibm_spectrumscale_cluster:
    state: present
    stanza: "/tmp/stanza"
    name: "node1.domain.com"

# Delete an existing IBM Spectrum Scale Cluster
- name: Delete an IBM Spectrum Scale Cluster
  ibm_spectrumscale_cluster:
    state: absent
    name: "node1.domain.com"
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
import traceback
from ansible.module_utils.basic import AnsibleModule

try: 
    from ansible.module_utils.ibm_spectrumscale_utils import RC_SUCCESS, SpectrumScaleLogger
except:
    from ibm_spectrumscale_utils import RC_SUCCESS, SpectrumScaleLogger

try: 
    from ansible.module_utils.ibm_spectrumscale_cluster_utils import SpectrumScaleCluster
except:
    from ibm_spectrumscale_cluster_utils import SpectrumScaleCluster


def main():
    logger = SpectrumScaleLogger.get_logger()

    logger.debug("------------------------------------")
    logger.debug("Function Entry: ibm_spectrumscale_cluster.main()")
    logger.debug("------------------------------------")

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
        try:
            scale_cluster = SpectrumScaleCluster()
            cluster_info_dict = {}
            cluster_info_dict["cluster_info"] = scale_cluster.get_cluster_dict()
            result_json = json.dumps(cluster_info_dict)
            msg = "Retrieve Cluster information successfully executed"
        except Exception as e:
            st = traceback.format_exc()
            e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
            module.fail_json(msg=e_msg)
    elif module.params['state']:
        if "present" in module.params['state']:
            # Create a new IBM Spectrum Scale cluster
            try:
                cmd_rc, stdout = SpectrumScaleCluster.create_cluster(
                                                          module.params['name'],
                                                          module.params['stanza']
                                                    )
                rc = cmd_rc
                msg = "Create Cluster successfully executed"
                result_json = stdout
            except Exception as e:
                st = traceback.format_exc()
                e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
                module.fail_json(msg=e_msg)
        else:
            # Delete the existing IBM Spectrum Scale cluster
            try:
                cmd_rc, stdout = SpectrumScaleCluster.delete_cluster(
                                                           module.params['name']
                                                       )
                rc = cmd_rc
                msg = "Delete Cluster successfully executed"
                result_json = stdout
            except Exception as e:
                st = traceback.format_exc()
                e_msg = ("Exception: {0}  StackTrace: {1}".format(str(e), st))
                module.fail_json(msg=e_msg)


        if rc == RC_SUCCESS:
            state_changed = True

    logger.debug("------------------------------------")
    logger.debug("Function Exit: ibm_spectrumscale_cluster.main()")
    logger.debug("------------------------------------")

    SpectrumScaleLogger.shutdown()

    # Module is done. Return back the result
    module.exit_json(changed=state_changed, msg=msg, rc=rc, result=result_json)


if __name__ == '__main__':
    main() 
