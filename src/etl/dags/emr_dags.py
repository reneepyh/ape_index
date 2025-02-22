from datetime import timedelta, datetime
import time
from airflow import DAG
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator, EmrTerminateJobFlowOperator, EmrAddStepsOperator
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from airflow.operators.python import PythonOperator

SPARK_STEPS = [
    {
        "Name": "Ape_Index_Redshift",
        "ActionOnFailure": "TERMINATE_CLUSTER",
        "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
                "spark-submit",
                "--deploy-mode", "cluster",
                "s3://[REDACTED]/spark_etl.py",
                "--user", "[REDACTED]",
                "--password", "[REDACTED]",
            ],
        }
    }
]

JOB_FLOW_OVERRIDES = {
    "Name": "Ape_Index",
    "ReleaseLabel": "emr-7.7.0",
    "Applications": [{"Name": "Spark"}],
    "Instances": {
        "Ec2KeyName": "emr",
        "InstanceGroups": [
              {
                  "Name": "Primary node",
                  "Market": "ON_DEMAND",
                  "InstanceRole": "MASTER",
                  "InstanceType": "m5.xlarge",
                  "InstanceCount": 1,
              },
         ],
         "KeepJobFlowAliveWhenNoSteps": True,
         "TerminationProtected": False,
    },
    "LogUri": "s3://[REDACTED]/logs",
    "JobFlowRole": "AmazonEMR-InstanceProfile-[REDACTED]",
    "ServiceRole": "service-role/AmazonEMR-ServiceRole-[REDACTED]",
    "VisibleToAllUsers": True,
}

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def sleep_one_minute():
    time.sleep(60)

with DAG(
    "ape_index_etl",
    default_args=DEFAULT_ARGS,
    description="Run Ape Index ETL on EMR and terminate after a delay",
    schedule_interval="0 2 * * *",
    start_date=datetime(2025, 2, 17),
    catchup=False,
) as dag:
    
    # 1. Create the EMR cluster (job flow)
    create_emr_cluster = EmrCreateJobFlowOperator(
        task_id="create_emr_cluster",
        job_flow_overrides=JOB_FLOW_OVERRIDES,
        aws_conn_id="aws_default",
        wait_policy="wait_for_completion",
    )

    # 2. Add the Spark ETL step to the cluster.
    add_steps = EmrAddStepsOperator(
        task_id="add_steps",
        job_flow_name="Ape_Index",
        cluster_states=["WAITING", "RUNNING"],
        steps=SPARK_STEPS,
        aws_conn_id="aws_default",
    )

    # 3. Wait for the Spark step to complete.
    wait_for_step = EmrStepSensor(
        task_id="wait_for_step",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='add_steps', key='return_value')[0] }}",
        aws_conn_id="aws_default",
        poke_interval=30,
    )

    # 4. Wait an additional 1 minutes after the step completes.
    delay_before_terminate = PythonOperator(
        task_id="delay_before_terminate",
        python_callable=sleep_one_minute,
    )

    # 5. Terminate the EMR cluster.
    terminate_emr_cluster = EmrTerminateJobFlowOperator(
        task_id="terminate_emr_cluster",
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id="aws_default",
    )

    # workflow
    create_emr_cluster >> add_steps >> wait_for_step >> delay_before_terminate >> terminate_emr_cluster
