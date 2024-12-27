from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from jira import JIRA
import boto3
from botocore.exceptions import ProfileNotFound, ClientError
import os
import json

app = FastAPI()

# Load environment variables
JIRA_SERVER = os.getenv("JIRA_SERVER")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

jira = JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

def get_aws_credentials_from_secret(secret_name, region_name):
    secrets_manager_client = boto3.client('secretsmanager', region_name)
    try:
        get_secret_value_response = secrets_manager_client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response['SecretString']
        credentials = json.loads(secret)
        return credentials
    except ClientError as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        raise e

def get_s3_client(secret_name):
    region_name = "us-east-1"
    credentials = get_aws_credentials_from_secret(secret_name, region_name)
    session = boto3.Session(
        aws_access_key_id=credentials['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=credentials['AWS_SECRET_ACCESS_KEY'],
        region_name=region_name
    )
    return session.client('s3')

def create_s3_bucket(s3_client, bucket_name, region_name):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
        return False 
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            try:
                # For us-east-1, don't specify LocationConstraint
                if region_name == "us-east-1":
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region_name}
                    )
                print(f"Bucket '{bucket_name}' created successfully in region '{region_name}'.")
                return True
            except ClientError as create_error:
                print(f"Error creating bucket '{bucket_name}': {create_error}")
                return False  
        else:
            print(f"Unexpected error: {e}")
            return False

def process_jira_tickets():
    query_info = 'status = "Work in progress" AND labels = "automated"'
    issues = jira.search_issues(query_info)

    for issue in issues:
        fields = issue.fields
        table_data = fields.description
        parsed_table = parse_jira_table(table_data)
        project_name = parsed_table.get("project_name")
        environment = parsed_table.get("environment")
        bucket_prefix = parsed_table.get("bucket_prefix")
        region_name = parsed_table.get("region_name")
        profile_name = f"{project_name.lower()}_{environment.lower()}"
        s3_client = get_s3_client(profile_name)

        if not s3_client:
            error_message = f"Invalid AWS profile '{profile_name}'."
            jira.add_comment(issue, error_message)
            continue

        bucket_name = f"{bucket_prefix}-{project_name.lower()}-{environment.lower()}"
        if create_s3_bucket(s3_client, bucket_name, region_name):
            comment = f"Bucket '{bucket_name}' created successfully."
            jira.add_comment(issue, comment)
            transition_issue_to_done(issue)
        else:
            comment = f"Bucket '{bucket_name}' already exists or there was an error."
            jira.add_comment(issue, comment)
            transition_issue_to_pending(issue)
            
def transition_issue_to_done(issue):
    transitions = jira.transitions(issue) 
    for transition in transitions:
        if transition['name'] == 'Mark as done': 
            jira.transition_issue(issue, transition['id'])
            print(f"Issue {issue.key} transitioned to Done.")
            return

def transition_issue_to_pending(issue):
    transitions = jira.transitions(issue) 
    print(transitions)
    for transition in transitions:
        if transition['name'] == 'Pending': 
            jira.transition_issue(issue, transition['id'])
            print(f"Issue {issue.key} transitioned to Pending.")
            return
            
def parse_jira_table(table_data):
    rows = table_data.strip().split("\n")
    parsed_data = {}
    for row in rows:
        if row.startswith("|") and not row.startswith("||"):  
            columns = [col.strip() for col in row.strip("|").split("|")]
            if len(columns) >= 2:
                key, value = columns[0], columns[1]
                parsed_data[key] = value
    return parsed_data

# APScheduler configuration
scheduler = BackgroundScheduler()

# Add a job to check JIRA tickets every minute
scheduler.add_job(process_jira_tickets, "interval", minutes=1)

@app.on_event("startup")
def start_scheduler():
    scheduler.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()

@app.get("/health")
def health():
    return {"message": "FastAPI is running, and the scheduler is processing every minute!"}
