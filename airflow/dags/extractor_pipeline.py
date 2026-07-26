import sys

sys.path.insert(0, "/opt/airflow/project")

from config.config_loader import config_load
from utils.checkpoint import CheckpointManager
from datetime import datetime, UTC
from src.extractor.paginator import Paginator
from src.extractor.raw_writer import RawWriter


from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.trigger_rule import TriggerRule

config = config_load()
page_size = config['api']['page_size']
initial_load_date = config['api']['initial_load_date']
resource = "Patient"

def checkpoint_load(**context):
    ti = context["ti"]

    checkpoint_manager = CheckpointManager()
    checkpoint = checkpoint_manager.load()

    ti.xcom_push(
        key="checkpoint",
        value=checkpoint)


def check_load_type(**context):
    ti = context["ti"]

    checkpoint = ti.xcom_pull(
        task_ids="checkpoint_load",
        key="checkpoint")
    
    resource_checkpoint = checkpoint.get(resource)
    last_successful_watermark = resource_checkpoint.get("last_successful_watermark")
    
    if last_successful_watermark is None:
        return "initial_load"

    else:
        return "incremental_load"

def initial_load(**context):
    ti = context["ti"]
    checkpoint = ti.xcom_pull(
        task_ids="checkpoint_load",
        key="checkpoint")
    resource_checkpoint = checkpoint.get(resource)
    params = {"_count": page_size,
                        "_lastUpdated": f"ge{initial_load_date}"}
    ti.xcom_push(
        key="params",
        value=params)

def incremental_load(**context):
    ti = context["ti"]
    checkpoint = ti.xcom_pull(
        task_ids="checkpoint_load",
        key="checkpoint")
    resource_checkpoint = checkpoint.get(resource)
    last_successful_watermark = resource_checkpoint.get("last_successful_watermark") 
    params = {"_count": page_size,
                        "_lastUpdated": last_successful_watermark}
    ti.xcom_push(
        key="params",
        value=params)

def api_call(**context):
    ti = context["ti"]

    paginator = Paginator()
    raw_writer = RawWriter()

    param_a = ti.xcom_pull(
        task_ids="initial_load",
        key="params")
    param_b = ti.xcom_pull(
        task_ids="incremental_load",
        key="params")
    
    if param_a is not None:
        params = param_a
    elif param_b is not None:
        params = param_b
    else:
        raise ValueError("No branch result available")
    
    checkpoint = ti.xcom_pull(
        task_ids="checkpoint_load",
        key="checkpoint")
    resource_checkpoint = checkpoint.get(resource)
    last_successful_page = resource_checkpoint.get("last_successful_page",0)

    page_number = last_successful_page + 1 
    total_records = 0
    file_path = None
    extraction_start_timestamp = datetime.now(UTC).isoformat()
    try:
        for bundle in paginator.fetch_pages(resource = resource, params = params):
            file_path = raw_writer.write(resource = resource, 
                                bundle = bundle, 
                                page_number = page_number)
            records_in_page = len(bundle.get("entry",[]))
            total_records += records_in_page
            page_number+=1
        checkpoint[resource] = {"last_successful_page":page_number - 1,
                                "total_records": total_records,
                                "status":"COMPLETED",
                                "last_successful_watermark" : extraction_start_timestamp }

        ti.xcom_push(
                    key="checkpoint",
                    value=checkpoint)
    except Exception as error:
        checkpoint[resource] = {"last_successful_page":page_number - 1,
                                "total_records": total_records,
                                "status":"FAILED",
                                "last_successful_watermark" : extraction_start_timestamp }
        ti.xcom_push(
                    key="checkpoint",
                    value=checkpoint)
        raise

def checkpoint_save(**context):

    ti = context["ti"]

    checkpoint = ti.xcom_pull(
        task_ids="api_call",
        key="checkpoint")
    resource_checkpoint = checkpoint[resource]
    checkpoint_manager = CheckpointManager()
    checkpoint_manager.save(resource = resource,
                            checkpoint = checkpoint,
                            last_successful_page = resource_checkpoint['last_successful_page'],
                            total_records = resource_checkpoint['total_records'],
                            status = resource_checkpoint['status'],
                            last_successful_watermark = resource_checkpoint['last_successful_watermark'])

with DAG(
    dag_id = "extractor_pipeline",
    start_date = datetime(2026,7,11),
    schedule = "0 12 * * *",
    catchup = False,
    tags = ["Extractor", "FHIR Extractor"],
) as dag:

    start_task = EmptyOperator(task_id = "start")

    checkpoint_load_task = PythonOperator(task_id = "checkpoint_load",
                                            python_callable = checkpoint_load)
    check_load_type_task = BranchPythonOperator(task_id = "check_load_type",
                                                python_callable = check_load_type)
    initial_load_task = PythonOperator(task_id = "initial_load",
                                            python_callable = initial_load)
    incremental_load_task = PythonOperator(task_id = "incremental_load",
                                            python_callable = incremental_load)
    api_call_task = PythonOperator(task_id = "api_call",
                                            python_callable = api_call,
                                            trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS)
    checkpoint_save_task = PythonOperator(task_id = "checkpoint_save",
                                            python_callable = checkpoint_save)
    stop_task = EmptyOperator(task_id = "stop")

    start_task >> checkpoint_load_task >> check_load_type_task

    check_load_type_task >> [initial_load_task, incremental_load_task]

    [initial_load_task, incremental_load_task] >> api_call_task >> checkpoint_save_task >> stop_task

    