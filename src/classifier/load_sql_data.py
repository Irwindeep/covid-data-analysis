import pandas as pd
import mysql.connector
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

db_config = {
    'host': 'localhost',
    'user': str(os.getenv("MYSQL_USERNAME")),
    'password': str(os.getenv("MYSQL_PASSWORD")),
    'database': str(os.getenv("MYSQL_DB")),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci'
}

query = """
SELECT 
    p.person_id,
    p.name,
    p.age,
    p.gender,
    p.email,
    p.phone_no,
    ts1.session_date AS session1_date,
    ts1.room_temperature AS session1_room_temp,
    ts1.view AS session1_view,
    ti1.image_path AS session1_image_path,
    ti1.min_temperature AS session1_min_temp,
    ti1.max_temperature AS session1_max_temp,
    ti1.region_of_interest AS session1_roi,
    ts2.session_date AS session2_date,
    ts2.room_temperature AS session2_room_temp,
    ts2.view AS session2_view,
    ti2.image_path AS session2_image_path,
    ti2.min_temperature AS session2_min_temp,
    ti2.max_temperature AS session2_max_temp,
    ti2.region_of_interest AS session2_roi,
    vs.heart_rate,
    vs.oxygen_saturation,
    vs.systolic_pressure,
    vs.diastolic_pressure,
    hs.covid_symptoms,
    hs.forehead_temp,
    hs.status AS health_status
FROM 
    persons p
LEFT JOIN 
    thermal_sessions ts1 ON p.person_id = ts1.person_id AND ts1.session_id = (
        SELECT MIN(session_id) 
        FROM thermal_sessions 
        WHERE person_id = p.person_id
    )
LEFT JOIN 
    thermal_images ti1 ON ts1.session_id = ti1.session_id
LEFT JOIN 
    thermal_sessions ts2 ON p.person_id = ts2.person_id AND ts2.session_id = (
        SELECT MAX(session_id) 
        FROM thermal_sessions 
        WHERE person_id = p.person_id
    )
LEFT JOIN 
    thermal_images ti2 ON ts2.session_id = ti2.session_id
LEFT JOIN 
    vital_signs vs ON p.person_id = vs.person_id
LEFT JOIN 
    health_status hs ON p.person_id = hs.person_id
WHERE 
    hs.status IS NOT NULL;
"""

try:
    connection = mysql.connector.connect(**db_config)
    df = pd.read_sql(query, connection)

    output_csv = './dataset/full.csv'
    df.to_csv(output_csv, index=False)
    print(f"Data successfully saved to {output_csv}")
except mysql.connector.Error as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        connection.close()
