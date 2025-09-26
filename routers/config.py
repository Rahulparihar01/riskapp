from google.cloud import bigquery
from google.oauth2 import service_account

# Service account key file path
key_path = "loyal-weaver-427600-s9-77fc8a9ce15a.json"

# Set up BigQuery credentials and client
credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)
dataset_id = "CyberSecurity"