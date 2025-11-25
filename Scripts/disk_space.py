import subprocess
import time
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# labs = ["sl3"]
labs = ["sl1", "sl2", "sl3", "cs101"]
failed_systems = {}
to_store = []

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT"))
)

cursor = connection.cursor() 

table_query = '''CREATE TABLE IF NOT EXISTS machine_storage_log (
     id INT AUTO_INCREMENT PRIMARY KEY,
     lab VARCHAR(10) NOT NULL,
     machine_number INT NOT NULL,
     disk_size VARCHAR(10) NOT NULL,
     disk_used VARCHAR(10) NOT NULL,
     available VARCHAR(10) NOT NULL,
     use_percent VARCHAR(10) NOT NULL,
     available_int VARCHAR(10) NOT NULL,
     record_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

     INDEX (lab),
     INDEX (machine_number),
     INDEX (record_time)
 );'''



cursor.execute(table_query)
connection.commit()

for lab in labs:
    failed_systems[lab] = []

def check(out):
    if(out[-1] == '%'):
        return True
    return False

def status_check(lab_name):

    subprocess.run(["bash", "status.sh", lab_name])


for lab in labs:

    status_check(lab)

    with open("alive_hosts", "r") as f:
        lines = f.readlines()
    
    for line in lines:
        # print(line)
        sys_num = line.split("-")[1].split(".")[0]
        result = subprocess.run(
            ["bash", "disk_space.sh", lab, sys_num], capture_output=True, text=True
        )
        
        if(not check(str(result.stdout.strip()))):
            failed_systems[lab].append(sys_num)
        else:
            val = str(result.stdout.strip()).replace("-"," ")
            to_store.append(val)
        
        time.sleep(0.5)
        
        # print(result)
        print(str(result.stdout.strip()))
        print(type(str(result.stdout.strip())))



for entry in to_store:
    print(entry)
    entry = entry.split(" ")
    lab = entry[0]
    machine_num = entry[1]
    size = entry[2]
    used = entry[3]
    ava = entry[4]
    use = entry[5] 
    ava_int = ava[:-1]  #this will be used to decide the colour of row in frontend
    query = f"INSERT INTO `machine_storage_log` (`id`, `lab`, `machine_number`, `disk_size`, `disk_used`, `available`, `use_percent`, `available_int`) VALUES (NULL, '{lab}', {machine_num}, '{size}', '{used}', '{ava}', '{use}', '{ava_int}');"
    cursor.execute(query)
    connection.commit()
    # print(query)

for lab in failed_systems:
    for systems in failed_systems[lab]:
        print(lab, systems)


