#!/bin/bash

password="$(cat .shadow)"

lab=$1
host=$2
remote="${lab}-${host}.cse.iitb.ac.in"


sshpass -p ${password} ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=13 sysad@${remote} "echo ${password} | sudo -S /home/sysad/Videos/en.sh"


