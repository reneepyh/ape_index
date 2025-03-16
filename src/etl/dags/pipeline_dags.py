from datetime import timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.utils.dates import days_ago

DEFAULT_ARGS = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='trigger_ecs_task',
    default_args=DEFAULT_ARGS,
    description='DAG to trigger ECS Tasks for ETL pipeline',
    schedule_interval='0 1 * * *',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    trigger_etl_task = EcsRunTaskOperator(
        task_id='trigger_etl_task',
        cluster='ape-index',
        task_definition='ape-index-pipeline',
        launch_type='FARGATE',
        overrides={
            'containerOverrides': [
                {
                    'name': 'ape-index-pipeline',
                },
            ],
        },
        network_configuration={
            'awsvpcConfiguration': {
                'subnets': ['subnet-016250600ef270ada', 'subnet-04b1202cff9333a33', 'subnet-00583d3593f035e5c'],
                'securityGroups': ['sg-0dad08ba8db7995e8'],
                'assignPublicIp': 'ENABLED',
            },
        },
        aws_conn_id='aws_default',
        region='ap-southeast-2',
    )

    trigger_etl_task
