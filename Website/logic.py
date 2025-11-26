import os
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from datetime import datetime

def get_latest_machine_data(cursor):
    query = """
        SELECT m.*
        FROM machine_storage_log m
        JOIN (
            SELECT lab, machine_number, MAX(record_time) AS latest_time
            FROM machine_storage_log
            GROUP BY lab, machine_number
        ) x
        ON m.lab = x.lab
        AND m.machine_number = x.machine_number
        AND m.record_time = x.latest_time;
    """
    cursor.execute(query)
    return cursor.fetchall()

def generate_disk_space_chart(data_list, static_folder_path):
    labels = ["0-10GB", "10-20GB", "20-30GB", "30-40GB", "40-50GB", "50GB+"]
    values = [0, 0, 0, 0, 0, 0]

    for row in data_list:
        try:
            # Assuming row[7] is 'available_int' (the numeric GB value)
            gb_val = float(row[7]) 
            
            # Sort into buckets
            if gb_val < 10:
                values[0] += 1
            elif 10 <= gb_val < 20:
                values[1] += 1
            elif 20 <= gb_val < 30:
                values[2] += 1
            elif 30 <= gb_val < 40:
                values[3] += 1
            elif 40 <= gb_val < 50:
                values[4] += 1
            else:
                values[5] += 1
        except (ValueError, TypeError):
            continue

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color=['#ef4444', '#f97316', '#eab308', '#3b82f6', '#3b82f6', '#22c55e'])
    plt.title('Distribution of Available Disk Space')
    plt.xlabel('Free Space Range')
    plt.ylabel('Count of Computers')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save logic
    filename = 'free_space_graph.png'
    # Ensure the images directory exists
    images_dir = os.path.join(static_folder_path, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    image_path = os.path.join(images_dir, filename)
    plt.savefig(image_path, bbox_inches='tight')
    plt.close() # Very important to close to free up memory!
    

def generate_disk_space_percentage_chart(data_list, static_folder_path):
    labels = ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50%+"]
    values = [0, 0, 0, 0, 0, 0]

    for row in data_list:
        try:
            percent_val = float(str(row[6]).replace('%', '').strip())

            # Sort into percentage buckets
            if percent_val < 10:
                values[0] += 1
            elif 10 <= percent_val < 20:
                values[1] += 1
            elif 20 <= percent_val < 30:
                values[2] += 1
            elif 30 <= percent_val < 40:
                values[3] += 1
            elif 40 <= percent_val < 50:
                values[4] += 1
            else:
                values[5] += 1

        except (ValueError, TypeError):
            continue

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color=['#ef4444', '#f97316', '#eab308', '#3b82f6', '#3b82f6', '#22c55e'])
    plt.title('Distribution of Available Disk Space (%)')
    plt.xlabel('Free Space Percentage Range')
    plt.ylabel('Count of Computers')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Save logic
    filename = 'free_space_percentage_graph.png'
    images_dir = os.path.join(static_folder_path, 'images')
    os.makedirs(images_dir, exist_ok=True)

    image_path = os.path.join(images_dir, filename)
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()
    

def generate_uptime_histogram(rows, static_folder_path):
    uptimes_weeks = []
    for row in rows:
        try:
            weeks = float(row[2])
            uptimes_weeks.append(weeks)
        except (ValueError, TypeError, IndexError):
            continue

    if not uptimes_weeks:
        return

    labels = ["0-5 weeks", "5-10 weeks", "10-15 weeks", "15-20 weeks", "20-25 weeks", "25+ weeks"]
    values = [0, 0, 0, 0, 0, 0]

    for weeks in uptimes_weeks:
        if weeks < 5:
            values[0] += 1
        elif 5 <= weeks < 10:
            values[1] += 1
        elif 10 <= weeks < 15:
            values[2] += 1
        elif 15 <= weeks < 20:
            values[3] += 1
        elif 20 <= weeks < 25:
            values[4] += 1
        else:
            values[5] += 1

    colors = ["#22c55e", "#65a30d", "#eab308", "#f59e0b", "#f97316", "#dc2626"]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values, color=colors)
    plt.title("Uptime Distribution (Weeks)")
    plt.xlabel("Weeks of Uptime")
    plt.ylabel("Number of PCs")
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    images_dir = os.path.join(static_folder_path, 'images')
    os.makedirs(images_dir, exist_ok=True)
    image_path = os.path.join(images_dir, "uptime_hist.png")
    plt.savefig(image_path, bbox_inches="tight")
    plt.close()





def generate_disk_space_pie_chart(cursor,static_folder_path):
    query = """
    SELECT lab, SUM(available_int) as total_free_gb
    FROM machine_storage_log m1
    WHERE record_time = (
        SELECT MAX(record_time)
        FROM machine_storage_log m2
        WHERE m2.lab = m1.lab AND m2.machine_number = m1.machine_number
    )
    GROUP BY lab;
    """
    
    cursor.execute(query)
    data_list=cursor.fetchall()

    values=[]
    labs=[]
    for row in data_list:
        values.append(row[1])
        labs.append( f"{row[0]} - {int(row[1])}GB")
    
    # print("Pie Chart Data:", labels, values)
    plt.figure(figsize=(10,10))
    plt.pie(values, labels=labs, autopct='%1.1f%%', startangle=140, colors=['#3b82f6', '#22c55e', '#eab308', '#f97316'])
    plt.title('Total Free Space by Lab')
    
    # Save logic
    filename = 'lab_space_pie_chart.png'
    images_dir = os.path.join(static_folder_path, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    image_path = os.path.join(images_dir, filename)
    plt.savefig(image_path, bbox_inches='tight')
    plt.close()
    
