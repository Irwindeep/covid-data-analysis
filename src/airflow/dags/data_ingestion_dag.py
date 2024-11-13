from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from ingestion.database import Database
from dotenv import load_dotenv
import os

class Ingestor:
    def __init__(
            self,
            username: str,
            password: str,
            database_name: str,
            data_dir: str
    ) -> None:
        self.database = Database(username, password, database_name)
        self.default_args = {
            'owner': 'airflow',
            'depends_on_past': False,
            'retries': 1,
            'relay_delay': timedelta(minutes=5),
            'start_date': datetime(2024, 14, 11)
        }
        self.data_dir = data_dir

        self.dag = DAG(
            'data_ingestion_dag',
            default_args=self.default_args,
            description="Automate data ingestion using Airflow",
            schedule_interval=timedelta(days=1)
        )

    def ingest_person_data(self) -> None:
        pass

    def ingest_thermal_session_data(self) -> None:
        pass


load_dotenv("../../../.env")

DB_USERNAME = os.getenv("MYSQL_USERNAME")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DB")