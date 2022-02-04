#!/bin/bash

action=$1
ssh_cfg=.ssh/config


if [[ $action == 'rm' ]];then
   > $ssh_cfg
   exit 0
fi


cp ${ssh_cfg}.default $ssh_cfg

