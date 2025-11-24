#!/bin/bash
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" scp /home/umang/dank/cs699/Course_project_git/project-sysad-25/Database/bash_scripts/sending_submit.sh sysad@10.130.153.2:/home/sysad/Desktop
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" ssh sysad@10.130.153.2 'chmod +x /home/sysad/Desktop/sending_submit.sh'
sshpass -f "/home/umang/dank/cs699/Course_project_git/password.txt" ssh sysad@10.130.153.2 '/home/sysad/Desktop/sending_submit.sh'
