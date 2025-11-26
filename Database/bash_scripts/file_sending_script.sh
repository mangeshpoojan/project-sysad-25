#!/bin/bash
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" scp -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o UserKnownHostsFile=/dev/null /home/umang/dank/cs699/Course_project_git/project-sysad-25/Database/bash_scripts/sending_submit.sh sysad@10.130.155.44:/home/sysad/Desktop
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=3 sysad@10.130.155.44 'chmod +x /home/sysad/Desktop/sending_submit.sh'
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=3 -o UserKnownHostsFile=/dev/null sysad@10.130.155.44 '/home/sysad/Desktop/sending_submit.sh'
