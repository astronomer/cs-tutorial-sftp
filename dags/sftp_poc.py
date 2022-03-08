from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.sftp.hooks.sftp import SFTPHook
from airflow.providers.sftp.operators.sftp import SFTPOperator
from airflow.providers.sftp.sensors.sftp import SFTPSensor
from airflow.utils.task_group import TaskGroup
from datetime import datetime

def delete_sftp_file(file_path):
    # https://github.com/apache/airflow/blob/main/airflow/providers/sftp/hooks/sftp.py
    hook = SFTPHook(ssh_conn_id='sftp_default')
    try:
        hook.delete_file(file_path)
    except OSError:
        print("File doesn't exist...continuing")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False
}

with DAG(
        dag_id='sftp_poc',
        start_date=datetime(2022, 3, 1),
        max_active_runs=3,
        schedule_interval=None,
        default_args=default_args,
        catchup=False
) as dag:

    start, finish = [DummyOperator(task_id=task_id) for task_id in ['start', 'finish']]

    add_to_known_hosts = BashOperator(
        task_id='add_to_known_hosts',
        bash_command='ssh-keyscan {{ conn.sftp_default.host }} > /home/astro/.ssh/known_hosts'
    )

    with TaskGroup('sftp') as tg1:
        sftp_hook_example = PythonOperator(
            task_id='delete_sftp_file',
            python_callable=delete_sftp_file,
            op_kwargs={
                "file_path": "/tmp/single-file/test-file.txt"
            }
        )

        sftp_sensor_example = SFTPSensor(
            task_id='check_for_sftp_file',
            path='/tmp/single-file/test-file.txt',
            sftp_conn_id='sftp_default',
            mode="poke",
            poke_interval=5,
            timeout=60*5
        )

        sftp_operator_example = SFTPOperator(
            task_id='upload_sftp_file',
            ssh_conn_id='sftp_default', #if not provided, then you need the ssh_hook
            local_filepath='/tmp/single-file/test-file.txt',
            remote_filepath='/tmp/single-file/test-file.txt',
            operation='put',
            create_intermediate_dirs=True
        )

        sftp_hook_example >> [sftp_sensor_example, sftp_operator_example]

    start >> add_to_known_hosts >> tg1 >> finish