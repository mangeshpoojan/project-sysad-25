import subprocess
import time
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

labs = ["sl1", "sl2", "sl3", "cs101"]
# labs = ["sl3"]

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

table_query = '''CREATE TABLE IF NOT EXISTS machine_uptimes_log (
     id INT AUTO_INCREMENT PRIMARY KEY,
     lab VARCHAR(10) NOT NULL,
     machine_number INT NOT NULL,
     weeks INT NOT NULL,
     days INT NOT NULL,
     hours INT NOT NULL,
     record_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

     INDEX (lab),
     INDEX (machine_number),
     INDEX (record_time)
 );'''



cursor.execute(table_query)
connection.commit()

for lab in labs:
    failed_systems[lab] = []


def parser(s: str) -> dict:

    id_part, time_part = s.split(" ", 1)
    id_part = id_part.split("-")
    
    
    segments = [seg.strip() for seg in time_part.split(",") if seg.strip()]

    weeks = 0
    days = 0
    hours = 0

    for seg in segments:
        parts = seg.split()         
        value = int(parts[0])
        unit = parts[1].lower() 

        if "week" in unit:
            weeks = value
        elif "day" in unit:
            days = value
        elif "hour" in unit:
            hours = value

    return {
        "lab": id_part[0],
        "machine_num": id_part[1],
        "weeks": weeks,
        "days": days,
        "hours": hours,
    }


def check(out):
    if(out[-1] == ',' or out[-1] == 's'):
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
            ["bash", "uptimes.sh", lab, sys_num], capture_output=True, text=True
        )
        
        if(not check(str(result.stdout.strip()))):
            failed_systems[lab].append(sys_num)
        else:
            val = str(result.stdout.strip())
            to_store.append(val)
        
        time.sleep(0.5)
        
        # print(result)
        print(str(result.stdout.strip()))
        print(type(str(result.stdout.strip())))



for entry in to_store:
    print(entry)
    entry = parser(entry)
    lab = entry["lab"]
    machine_num = entry["machine_num"]
    weeks = entry["weeks"]
    days = entry["days"]
    hours = entry["hours"]
    query = f"INSERT INTO `machine_uptimes_log` (`id`, `lab`, `machine_number`, `weeks`, `days`, `hours`) VALUES (NULL, '{lab}', {machine_num}, {weeks}, {days}, {hours});"
    cursor.execute(query)
    connection.commit()
    # print(query)

for lab in failed_systems:
    for systems in failed_systems[lab]:
        print(lab, systems)


