import subprocess
import time
import mysql.connector
import os


# labs = ["sl1", "sl2", "sl3", "cs101"]
labs = ["sl2"]
failed_systems = {}
to_store = []

def status_check(lab_name):

    subprocess.run(["bash", "status.sh", lab_name])


for lab in labs:

    status_check(lab)

    with open("alive_hosts", "r") as f:
        lines = f.readlines()

    for line in lines:
        print(line)
        sys_num = line.split("-")[1].split(".")[0]
        print(lab,sys_num)
        subprocess.run(["bash", "internet_disable.sh", lab, sys_num])

        print("")
