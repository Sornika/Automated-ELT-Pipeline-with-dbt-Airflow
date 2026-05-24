from datetime import datetime, timedelta
from airflow import DAG
#AS WE ARE ORCHESTRATING DOCKER CONTAINER WE NEED SOME DOCKER TYPES, OPERATOR(AND WE NEED PYTHON OPERATOR AS OUR ELT SCRIPT IS PYTHON)
from docker.types import Mount
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
#from airflow.operators.python import PythonOperator
#from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess

default_args ={
  'owner': 'airflow',  # who owns this DAG
  'depends_on_past': False, # don't wait for yesterday's run to succeed
  'email_on_failure': False, # don't send email if it fails
  'email_on_retry': False, # don't send email on retry
}

def run_elt_script():
    #wwe need to point to the docker one not local one
    script_path = "/opt/airflow/elt/elt_script.py" # path to script inside airflow container
    result = subprocess.run(["python", script_path],
                             capture_output=True, text=True) #run script
    if result.returncode !=0:  # if script failed
       raise Exception(f"Script failed with error: {result.stderr}") #exception
    else:
       print(result.stdout)

dag= DAG(
   #name of the dag
   'elt_and_dbt',    # name of the DAG shown in Airflow UI
   default_args=default_args,  # apply the settings above
   description='An ELT workflow with dbt',
   start_date=datetime(2026,5,21), # when the DAG starts running
   catchup=False,  # don't run missed past schedules
)

t1 = PythonOperator(
  task_id="run_elt_script", # name shown in Airflow UI
  python_callable=run_elt_script, # the function to run
  dag=dag # which DAG this belongs to
)

t2 = DockerOperator(
   task_id="dbt_run", 
   image='ghcr.io/dbt-labs/dbt-postgres:1.4.7', # the dbt docker image to use
   command=[ # dbt run command
      "run",
      "--profiles-dir",
      "/root/.dbt",
      "--project-dir",
      "/opt/dbt"
   ],
   auto_remove=True,
   #auto_remove=True, #automatically remove container once build # delete container after it finishes
   docker_url="unix:///var/run/docker.sock", #will directly point to the socket that we open on unix # connects to Docker on your machine
   network_mode="bridge",
   mounts=[
      Mount(
         source="C:/Users/Koira/elt/custom_postgres",
         target="/opt/dbt", 
         type="bind"
      ), # maps your dbt project folder into the container
      Mount(
         source="C:/Users/Koira/.dbt",
         target="/root/.dbt", 
         type="bind"
         )  # maps your dbt profiles folder into the container
   ],
   
   dag=dag
)

t1 >> t2 #this MEANS T1 TAKES PRIORITY OVER T2

# t1 — runs your elt_script.py which:
# connects to source postgres
# copies data to destination postgres

# t2 — runs dbt which:
# takes the raw data in destination postgres
# transforms it into models like film_ratings

# default_args → sets default behaviour for all tasks so you don't repeat yourself
# run_elt_script() → wraps your python script so Airflow can call it as a task
# DAG() → defines the pipeline name, start date, and schedule
# PythonOperator → tells Airflow "run this python function as a task"
# DockerOperator → tells Airflow "spin up this docker container as a task"
# Mount → shares your local folders with the docker container so dbt can find your project files
# t1 >> t2 → tells Airflow the order — ELT must finish before dbt starts


