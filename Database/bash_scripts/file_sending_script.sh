#!/bin/bash
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 /home/umang/dank/cs699/Course_project_git/project-sysad-25/Database/bash_scripts/sending_submit.sh sysad@10.130.155.3:/home/sysad/Desktop
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ConnectTimeout=10 sysad@10.130.155.3 'chmod +x /home/sysad/Desktop/sending_submit.sh'
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ConnectTimeout=10 sysad@10.130.155.3 '/home/sysad/Desktop/sending_submit.sh'
