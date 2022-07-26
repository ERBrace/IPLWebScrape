"""DAG definition for extract and transform pipeline.
"""
# pylint: disable=pointless-statement
import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


import os, sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from src.extract import extract
from src.transform import transform
from src.load import load


dag = DAG(
   dag_id="ipl_extract_and_transform",
   start_date=airflow.utils.dates.days_ago(1),
   schedule_interval=None,
)


def _extract_data():
   """Extracts the batter data and saves it to a csv.
   """
   data = extract()
   data.to_csv("./data/extracted_data.csv", index=False)


def _transform_data():
   """Loads, cleans, transforms and saves the batter data.
   """
   import pandas as pd
   data = pd.read_csv("./data/extracted_data.csv")
   transformed_data = transform(data)
   transformed_data.to_csv("./data/transformed_data.csv")


def _load_data():
   """Loads the batter data into a local sqlite db.
   """
   data = "./data/transformed_data.csv"
   load(data)


extract_data = PythonOperator(
   task_id="extract_data",
   python_callable=_extract_data,
   dag=dag,
)


transform_data = PythonOperator(
   task_id="transform_data",
   python_callable=_transform_data,
   dag=dag,
)


load_data = PythonOperator(
   task_id="load_data",
   python_callable=_load_data,
   dag=dag,
)


notify = BashOperator(
   task_id="notify",
   bash_command='echo "The Indian Premier League data has been extracted and transformed."',
   dag=dag,
)

extract_data >> transform_data >> load_data >> notify
