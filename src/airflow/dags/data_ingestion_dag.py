import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from ingestion.database import Database
from dotenv import load_dotenv
import os
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 11, 1)
}

dag = DAG(
    'data_ingestion_dag',
    default_args=default_args,
    description="Automate data ingestion using Airflow",
    schedule=timedelta(days=1)
)

class Ingestor:
    def __init__(
            self,
            username: str,
            password: str,
            database_name: str,
            data_dir: str,
            dag: DAG
    ) -> None:
        self.database = Database(username, password, database_name)
        self.data_dir = data_dir

        self.dag = dag

    def ingest_person_data(self) -> None:
        person_data_path = os.path.join(self.data_dir, "persons.csv")

        try:
            df = pd.read_csv(person_data_path)
            logger.info(f"Loaded person data from {person_data_path}")

            for _, row in df.iterrows():
                data = {
                    "name": row["name"],
                    "age": row["age"],
                    "gender": row["gender"],
                    "email": row["email"],
                    "phone_no": row["phone_no"],
                    "address": row["address"]
                }

                with self.database as db:
                    db.insert_data('persons', data)

        except Exception as e:
            logger.error(f"Error ingesting person data: {e}")

    def ingest_thermal_session_data(self) -> None:
        session_data_path = os.path.join(self.data_dir, "thermal_sessions.csv")

        try:
            df = pd.read_csv(session_data_path)
            logger.info(f"Loaded thermal session data from {session_data_path}")

            for _, row in df.iterrows():
                data = {
                    "person_id": row["person_id"],
                    "session_date": row["session_date"],
                    "room_temperature": row["room_temperature"],
                    "view": row["view"],
                }

                with self.database as db:
                    db.insert_data('thermal_sessions', data)

        except Exception as e:
            logger.error(f"Error ingesting thermal session data: {e}")

    def ingest_thermal_image_data(self) -> None:
        image_data_path = os.path.join(self.data_dir, "thermal_images.csv")

        try:
            df = pd.read_csv(image_data_path)
            logger.info(f"Loaded thermal image data from {image_data_path}")

            for _, row in df.iterrows():
                data = {
                    "session_id": row["session_id"],
                    "image_path": row["image_path"],
                    "min_temperature": row["min_temperature"],
                    "max_temperature": row["max_temperature"],
                    "region_of_interest": row["region_of_interest"]
                }

                with self.database as db:
                    db.insert_data('thermal_images', data)

        except Exception as e:
            logger.error(f"Error ingesting thermal image data: {e}")

    def ingest_vital_sign_data(self) -> None:
        vital_sign_data_path = os.path.join(self.data_dir, "vital_signs.csv")

        try:
            df = pd.read_csv(vital_sign_data_path)
            logger.info(f"Loaded Vital Sign data from {vital_sign_data_path}")

            for _, row in df.iterrows():
                data = {
                    "person_id": row["person_id"],
                    "heart_rate": row["heart_rate"],
                    "oxygen_saturation": row["oxygen_saturation"],
                    "systolic_pressure": row["systolic_pressure"],
                    "diastolic_pressure": row["diastolic_pressure"]
                }

                with self.database as db:
                    db.insert_data('vital_signs', data)

        except Exception as e:
            logger.error(f"Error ingesting vital signs data: {e}")

    def ingest_health_status_data(self) -> None:
        health_status_data_path = os.path.join(self.data_dir, "health_status.csv")

        try:
            df = pd.read_csv(health_status_data_path)
            logger.info(f"Loaded health status data from {health_status_data_path}")

            for _, row in df.iterrows():
                data = {
                    "person_id": row["person_id"],
                    "covid_symptoms": row["covid_symptoms"],
                    "forehead_temp": row["forehead_temp"],
                    "status": row["status"]
                }

                with self.database as db:
                    db.insert_data('thermal_images', data)

        except Exception as e:
            logger.error(f"Error ingesting health status data: {e}")

    def create_dag(self) -> None:
        with self.dag as dag:
            ingest_person_task = PythonOperator(
                task_id="ingest_person_data",
                python_callable=self.ingest_person_data,
                dag=dag
            )

            ingest_thermal_session_task = PythonOperator(
                task_id="ingest_thermal_session_data",
                python_callable=self.ingest_thermal_session_data,
                dag=dag
            )

            ingest_thermal_image_task = PythonOperator(
                task_id="ingest_thermal_image_data",
                python_callable=self.ingest_thermal_image_data,
                dag=dag
            )

            ingest_vital_sign_task = PythonOperator(
                task_id="ingest_vital_sign_data",
                python_callable=self.ingest_vital_sign_data,
                dag=dag
            )

            ingest_health_status_task = PythonOperator(
                task_id="ingest_health_status_data",
                python_callable=self.ingest_health_status_data,
                dag=dag
            )

            ingest_person_task >> ingest_thermal_session_task >> ingest_thermal_image_task >> ingest_vital_sign_task >> ingest_health_status_task


if __name__=="__main__":
    load_dotenv("../../../.env")

    DB_USERNAME = os.getenv("MYSQL_USERNAME")
    DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
    DB_NAME = os.getenv("MYSQL_DB")
    DATA_DIR = os.getenv("DATA_DIR")
    
    ingestor = Ingestor(DB_USERNAME, DB_PASSWORD, DB_NAME, DATA_DIR, dag)
    ingestor.create_dag()