import pandas as pd
import subprocess

file_location=input()

df = pd.read_excel(file_location)

for index, row in df.iterrows():
    student_id = row['StudentID']
    lab = row['Lab']

    if row['Lab'] == "sl1":
            student_ip = "10.130.153." + str(row['SeatNo'])
    elif row['Lab'] == "sl2":
        student_ip = "10.130.154." + str(row['SeatNo'])
    elif row['Lab'] == "sl3":
        student_ip = "10.130.155." + str(row['SeatNo'])
    else:
        app.logger.error(f"Invalid Lab for StudentID: {row['StudentID']}")

    result = subprocess.run(['sshpass' , '-f' , '/home/umang/dank/cs699/Course_project_git/password.txt' ,'ssh' , '-o' , 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'ConnectTimeout=3' , f'sysad@{student_ip}' , 'mkdir' , '-p' , f'/home/sysad/Desktop/submission_{row['StudentID']}/sample_data'])
    # print(f"Created directory for StudentID: {student_id} at /home/sysad/Desktop/submission_{student_id}/sample_data")
    print(result)