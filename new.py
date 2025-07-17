
from fastapi import FastAPI, Query, HTTPException
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from fastapi.responses import JSONResponse
import os
from typing import Optional
from datetime import date, datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="CyberSecurity API", description="API for querying BigQuery tables in the CyberSecurity dataset")

# List of allowed tables
ALLOWED_TABLES = {
    "CPEs", "CVEs", "CVEs2", "CVEsEpssScores", "CVEsGithubRepos", "CVEsGithubRepos2",
    "CVEs_temp", "CWEs", "FinalCVEs", "FinalCVEsGithubRepos", "FinalCVEs_temp",
    "FinalEpssTable", "FinalNews", "FinalNews2", "FinalNews3", "ImportantCVEs",
    "News", "NewsClassification1", "NewsClassification2", "NewsData", "NewsEntities",
    "NewsEntities2", "NewsEntities3", "NewsEntitiesData", "NewsLetterData", "PdfNews",
    "ProcessedNews", "ProcessedNews2", "ProcessedNews3", "ProcessedNews4", "QA_Dataset",
    "RSSLinks", "RSSNews", "RiskGPTDataset", "WebsiteDetails", "WebsiteLinks",
    "Websites", "test_cves_table"
}

# Load BigQuery credentials
key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "loyal-weaver-427600-s9-77fc8a9ce15a.json")
try:
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
except Exception as e:
    logger.error(f"Failed to initialize BigQuery client: {str(e)}")
    raise Exception(f"Failed to initialize BigQuery client: {str(e)}")

dataset_id = "CyberSecurity"

def serialize_dates(obj):
    """Convert date, datetime, or other non-serializable objects to JSON-compatible formats."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='ignore')
    elif pd.isna(obj):
        return None  # Convert NaN/None to JSON null
    return obj

def fetch_paginated_data(table: str, page: int, page_size: int) -> dict:
    """Helper function to fetch paginated data from a BigQuery table."""
    if table not in ALLOWED_TABLES:
        logger.error(f"Invalid table name: {table}")
        raise HTTPException(status_code=400, detail="Invalid table name")

    full_table_id = f"{client.project}.{dataset_id}.{table}"
    offset = (page - 1) * page_size

    try:
        # Using SELECT * for simplicity; consider specifying columns for performance
        query = f"""
            SELECT * FROM `{full_table_id}`
            LIMIT {page_size + 1} OFFSET {offset}
        """
        df = client.query(query).to_dataframe()

        # Log column types for debugging
        logger.info(f"Table {table} columns: {dict(df.dtypes)}")

        # Convert all columns to ensure JSON serialization
        for col in df.columns:
            df[col] = df[col].apply(serialize_dates)

        # Check if there are more rows
        has_more = len(df) > page_size
        df = df.head(page_size)  # Trim to page_size

        return {
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": df.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Query failed for table {table}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Generate separate endpoints for each table
def create_endpoint(table_name: str):
    @app.get(f"/get-{table_name.lower().replace('_', '-')}-data")
    async def get_data(
        page: int = Query(1, ge=1, description="Page number (1-based)"),
        page_size: int = Query(10, ge=1, le=100, description="Number of records per page")
    ):
        return JSONResponse(content=fetch_paginated_data(table_name, page, page_size))

# Create endpoints for all tables
for table in ALLOWED_TABLES:
    create_endpoint(table)