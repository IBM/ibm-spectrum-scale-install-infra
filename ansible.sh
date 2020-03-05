#!/bin/bash

export ANSIBLE_LOG_PATH=/tmp/ansible_$(date "+%Y%m%d%H%M%S").log

IFS=$','

echo 'Running ansible-playbook -i hosts playbook.yml'
ansible-playbook -i hosts playbook.yml
