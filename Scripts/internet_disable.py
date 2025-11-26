import subprocess
import time
import mysql.connector
import os
import sys


lab = sys.argv[1]
system_number = sys.argv[2]
flag = 0

if(lab == 'sl1'):
    flag = 1
elif(lab == 'sl2'):
    flag = 1
elif(lab == 'sl3'):
    flag = 1


# labs = ["sl1", "sl2", "sl3", "cs101"]
# labs = ["sl3"]
failed_systems = {}
to_store = []


def status_check(lab_name):

    subprocess.run(["bash", "status.sh", lab_name])

if(flag == 1):
    
    if(system_number == '-1'):

        status_check(lab)

        with open("alive_hosts", "r") as f:
            lines = f.readlines()

        for line in lines:
            print(line)
            sys_num = line.split("-")[1].split(".")[0]
            print(lab,sys_num)
            subprocess.run(["bash", "internet_disable.sh", lab, sys_num])
            print("")

    else:
         subprocess.run(["bash", "internet_disable.sh", lab, system_number])

