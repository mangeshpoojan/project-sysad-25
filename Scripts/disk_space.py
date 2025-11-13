import subprocess
import time

lab = "sl1"
subprocess.run(["bash", "status.sh", lab])

with open("alive_hosts", "r") as f:
    lines = f.readlines()

output = []

for line in lines:
    # print(line)
    sys_num = line.split("-")[1].split(".")[0]
    result = subprocess.run(
        ["bash", "disk_usage.sh", lab, sys_num], capture_output=True, text=True
    )
    time.sleep(0.5)
    output.append(str(result.stdout.strip()))
