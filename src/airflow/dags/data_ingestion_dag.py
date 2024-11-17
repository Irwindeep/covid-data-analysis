import logging
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from ingestion.database import Database
from ingestion.data_processing import DataProcessor
from ingestion.elasticsearch_client import ElasticsearchClient
from dotenv import load_dotenv, find_dotenv
import os
import pandas as pd
from typing import List

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
        self.processor = DataProcessor()
        self.es_client = ElasticsearchClient()
        self.version = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.index_body = {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }

    def process_and_ingest_data(
            self,
            file_name: str,
            required_columns: List[str],
            table_name: str
    ) -> None:
        file_path = os.path.join(self.data_dir, file_name)

        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded data from {file_path}")

            df = self.processor.validate_data(df, required_columns)
            df = self.processor.clean_data(df)
            df = self.processor.transform_data(df)

            for _, row in df.iterrows():
                row["version"] = self.version,
                row["version_timestamp"] = datetime.now()
                with self.database as db:
                    db.insert_data(table_name, row.to_dict())
            
            logger.info(f"Successfully ingested data into {table_name}")

            es_data = df.to_dict(orient="records")
            for record in es_data:
                record["version"] = self.version
                record["version_timestamp"] = datetime.now()

            if not self.es_client.index_exists(table_name):
                self.es_client.create_index(index_name=table_name, body=self.index_body)

            success = self.es_client.index_data(index_name=table_name, data=es_data)
            if success:
                logger.info(f"Successfully indexed {file_name} data into Elasticsearch")

            df = df.iloc[0:0]
            df.to_csv(file_path)

        except Exception as e:
            logger.error(f"Error processing and ingesting {file_name}: {e}")

    def ingest_person_data(self) -> None:
        self.process_and_ingest_data(
            file_name="persons.csv",
            required_columns=[
                "name",
                "age",
                "gender",
                "email",
                "phone_no",
                "address"
            ],
            table_name="persons"
        )

    def ingest_thermal_session_data(self) -> None:
        self.process_and_ingest_data(
            file_name="thermal_sessions.csv",
            required_columns=[
                "person_id",
                "session_date",
                "room_temperature",
                "view"
            ],
            table_name="thermal_sessions"
        )

    def ingest_thermal_image_data(self) -> None:
        self.process_and_ingest_data(
            file_name="thermal_images.csv",
            required_columns=[
                "session_id",
                "image_path",
                "min_temperature",
                "max_temperature",
                "region_of_interest"
            ],
            table_name="thermal_images"
        )

    def ingest_vital_sign_data(self) -> None:
        self.process_and_ingest_data(
            file_name="vital_signs.csv",
            required_columns=[
                "person_id",
                "heart_rate",
                "oxygen_saturation",
                "systolic_pressure",
                "diastolic_pressure"
            ],
            table_name="vital_signs"
        )

    def ingest_health_status_data(self) -> None:
        self.process_and_ingest_data(
            file_name="health_status.csv",
            required_columns=[
                "person_id",
                "covid_symptoms",
                "forehead_temp",
                "status"
            ],
            table_name="health_status"
        )

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

            ingest_person_task >> ingest_thermal_session_task >> [ingest_thermal_image_task, ingest_vital_sign_task, ingest_health_status_task
]

load_dotenv(dotenv_path=find_dotenv(".env"))

DB_USERNAME = str(os.getenv("MYSQL_USERNAME"))
DB_PASSWORD = str(os.getenv("MYSQL_PASSWORD"))
DB_NAME = str(os.getenv("MYSQL_DB"))
DATA_DIR = str(os.getenv("DATA_DIR"))

ingestor = Ingestor(DB_USERNAME, DB_PASSWORD, DB_NAME, DATA_DIR, dag)
ingestor.create_dag()