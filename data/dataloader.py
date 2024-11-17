import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv("../.env")
DATA_DIR = os.getenv("DATA_DIR")[:-3] + '/images/termal_avi_data/'

df = pd.read_csv("./images/subject_description.csv")

db = {
    "./db/persons.csv": "name,age,gender,email,phone_no,address",
    "./db/thermal_sessions.csv": "person_id,session_date,room_temperature,view",
    "./db/thermal_images.csv": "session_id,image_path,min_temperature,max_temperature,region_of_interest",
    "./db/vital_signs.csv": "person_id,heart_rate,oxygen_saturation,systolic_pressure,diastolic_pressure",
    "./db/health_status.csv": "person_id,covid_symptoms,forehead_temp,status"
}

for file, cols in db.items():
    with open(file, 'w') as f:
        f.write(f"{cols}\n")

s1, s2 = 1, 2
for idx, row in df.iterrows():
    with open("./db/persons.csv", 'a') as f:
        f.write(f"{row["ID"]},{row["AGE"]},{"Male" if row["SEX"] == 'M' else "Female"},,,\n")

    with open("./db/thermal_sessions.csv", 'a') as f:
        room_temp = float(row["Room Temperature"]) if not pd.isna(row["Room Temperature"]) else ''

        f.write(f"{int(idx)+1},,{room_temp},Chest\n")
        f.write(f"{int(idx)+1},,{room_temp},Back\n")

    with open("./db/thermal_images.csv", 'a') as f:
        img_path = DATA_DIR + row["ID"]
        img_path_s1, img_path_s2 = img_path + "/Front/ClearFront.avi", img_path + "/Back/ClearBack.avi"

        body_temp = float(row["Body Temperature (°C)"]) if not pd.isna(row["Body Temperature (°C)"]) else ''

        f.write(f"{s1},{img_path_s1},{body_temp},{body_temp},Chest\n")
        f.write(f"{s2},{img_path_s2},{body_temp},{body_temp},Back\n")

    with open("./db/vital_signs.csv", 'a') as f:
        heart_rate = float(row["Cardiac Frequency"]) if not pd.isna(row["Cardiac Frequency"]) else ''
        oxy_sat = float(row["SpO2"][:-1]) if not pd.isna(row["SpO2"]) else ''
        sys_press = float(row["Blood Pressure"].split('/')[0]) if not pd.isna(row["Blood Pressure"]) else ''
        dias_press = float(row["Blood Pressure"].split('/')[1]) if not pd.isna(row["Blood Pressure"]) else ''

        f.write(f"{int(idx)+1},{heart_rate},{oxy_sat},{sys_press},{dias_press}\n")

    with open("./db/health_status.csv", 'a') as f:
        room_temp = row["Room Temperature"] if not pd.isna(row["Room Temperature"]) else ''
        status = "Healthy" if row["PCR Result"] == "Negative" else "Unhealthy"

        f.write(f"{int(idx)+1},,{room_temp},{status}\n")

    s1, s2 = s1+2, s2+2