# Dockerfile

FROM apache/airflow:2.10.3-python3.12

ENV AIRFLOW_HOME=/opt/airflow

COPY airflow.cfg ${AIRFLOW_HOME}/airflow.cfg
COPY webserver_config.py ${AIRFLOW_HOME}/webserver_config.py

COPY dags/ ${AIRFLOW_HOME}/dags/
COPY logs/ ${AIRFLOW_HOME}/logs/

EXPOSE 8080