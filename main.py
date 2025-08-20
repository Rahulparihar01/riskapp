from fastapi import FastAPI, Query, HTTPException
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from fastapi.responses import JSONResponse
import numpy as np
import datetime
import os 
import json
# Initialize FastAPI app
app = FastAPI()

# Service account key file path
#key_path = "loyal-weaver-427600-s9-77fc8a9ce15a.json"
service_account_json = os.getenv("GCP_CREDENTIALS_JSON")
if not service_account_json:
    raise RuntimeError("GCP_CREDENTIALS_JSON environment variable not set")
# Set up BigQuery credentials and client
credentials_dict = json.loads(service_account_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)
dataset_id = "CyberSecurity"
@app.get("/")
def health_check():
    return {"status": "ok"}



@app.get("/get-finalnew3-data")
def get_data(
    # table: str = Query(..., description="Table name inside the CyberSecurity dataset"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    table= "FinalNews3"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
        df = client.query(query).to_dataframe()

        # Check if there are more rows
        has_more = len(df) > page_size
        df = df.head(page_size)  # Trim to page_size if we fetched extra

        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": df.to_dict(orient="records")
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get-cves-data")
def get_data(
    # table: str = Query(..., description="Table name inside the CyberSecurity dataset"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    table= "CVEs"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
        df = client.query(query).to_dataframe()

        # Check if there are more rows
        has_more = len(df) > page_size
        df = df.head(page_size)  # Trim to page_size if we fetched extra

        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": df.to_dict(orient="records")
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import json 


@app.get("/newsarticle")
def get_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    table = "newsarticle"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
        df = client.query(query).to_dataframe()

        has_more = len(df) > page_size
        df = df.head(page_size)

        # 🔥 Convert datetime columns to ISO format strings
        datetime_cols = ["createdAt", "datePublished", "dateUpdated"]
        for col in datetime_cols:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)

        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": json.loads(df.to_json(orient="records"))
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/get-cves-data")
def get_data(
    # table: str = Query(..., description="Table name inside the CyberSecurity dataset"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    table= "CVEs"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
        df = client.query(query).to_dataframe()

        # Check if there are more rows
        has_more = len(df) > page_size
        df = df.head(page_size)  # Trim to page_size if we fetched extra

        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": df.to_dict(orient="records")
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



from fastapi.encoders import jsonable_encoder


@app.get("/get-CWEs-data")
def get_data(
    # table: str = Query(..., description="Table name inside the CyberSecurity dataset"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    table= "CWEs_test"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
        df = client.query(query).to_dataframe()
        print('dhdhffj')
        # Check if there are more rows
        has_more = len(df) > page_size
        df = df.head(page_size)  # Trim to page_size if we fetched extra
        print(df)
        records = jsonable_encoder(df.to_dict(orient="records"))

        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": records
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# @app.get("/get-cpes-data")
# def get_data(
#     # table: str = Query(..., description="Table name inside the CyberSecurity dataset"),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1)
# ):
#     table= "cpes"
#     full_table_id = f"{client.project}.{dataset_id}.{table}"

#     try:
#         offset = (page - 1) * page_size
#         query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
#         df = client.query(query).to_dataframe()

#         # Check if there are more rows
#         has_more = len(df) > page_size
#         df = df.head(page_size)  # Trim to page_size if we fetched extra

#         return JSONResponse(content={
#             "page": page,
#             "page_size": page_size,
#             "next_page": page + 1 if has_more else None,
#             "has_more": has_more,
#             "records": df.to_dict(orient="records")
#         })

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




@app.get("/get-cpes-data")
def get_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    table = "cpes"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
        df = client.query(query).to_dataframe()

        # Convert NumPy/ndarray types → Python native types
        df = df.applymap(
            lambda x: x.tolist() if isinstance(x, np.ndarray) 
            else (x.item() if isinstance(x, (np.int64, np.float64)) else x)
        )

        # Check if there are more rows
        has_more = len(df) > page_size
        df = df.head(page_size)

        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": df.to_dict(orient="records")
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/filter-date-cve")
def filter_cve(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    table = "CVEs"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        offset = (page - 1) * page_size
        query = f"""
            SELECT *
            FROM `{full_table_id}`
            WHERE SAFE_CAST(SAFE_CAST(published_date AS TIMESTAMP) AS DATE) 
                  BETWEEN @start_date AND @end_date
            ORDER BY SAFE_CAST(SAFE_CAST(published_date AS TIMESTAMP) AS DATE) DESC
            LIMIT {page_size + 1}
            OFFSET {offset}
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date)
            ]
        )

        df = client.query(query, job_config=job_config).to_dataframe()

        has_more = len(df) > page_size
        df = df.head(page_size)

        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": df.to_dict(orient="records")
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get-cve_id")
def get_cve(
    cve_id: str = Query(..., description="CVE ID to search, e.g., CVE-2025-23118")
):
    table = "CVEs"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        query = f"""
            SELECT *
            FROM `{full_table_id}`
            WHERE cve_id = @cve_id
            LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("cve_id", "STRING", cve_id)
            ]
        )

        df = client.query(query, job_config=job_config).to_dataframe()

        if df.empty:
            return JSONResponse(content={"message": f"No record found for {cve_id}"}, status_code=404)

        return JSONResponse(content=df.to_dict(orient="records")[0])  # return first match

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/get-cpe-id")
def get_cpe(
    cve_id: str = Query(..., description="CVE ID to search, e.g., CVE-2025-23118")
):
    table = "cpes"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        query = f"""
            SELECT *
            FROM `{full_table_id}`
            WHERE cve_id = @cve_id
            LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("cve_id", "STRING", cve_id)
            ]
        )

        df = client.query(query, job_config=job_config).to_dataframe()

        if df.empty:
            return JSONResponse(
                content={"message": f"No record found for {cve_id}"}, 
                status_code=404
            )

        # Convert NumPy types to Python native types
        record = df.to_dict(orient="records")[0]
        clean_record = {
            k: (v.tolist() if isinstance(v, np.ndarray) else v.item() if hasattr(v, "item") else v)
            for k, v in record.items()
        }

        return JSONResponse(content=clean_record)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-cwes-id")
def get_cwe_id(
    cve_id: str = Query(..., description="CVE ID to search, e.g., CVE-2025-23118")
):
    table = "CWEs_test"
    full_table_id = f"{client.project}.{dataset_id}.{table}"

    try:
        query = f"""
            SELECT *
            FROM `{full_table_id}`
            WHERE cve_id = @cve_id
            LIMIT 1
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("cve_id", "STRING", cve_id)
            ]
        )

        df = client.query(query, job_config=job_config).to_dataframe()

        if df.empty:
            return JSONResponse(
                content={"message": f"No record found for {cve_id}"},
                status_code=404
            )

        record = df.to_dict(orient="records")[0]

        # Convert NumPy, datetime, and date types
        clean_record = {}
        for k, v in record.items():
            if isinstance(v, np.ndarray):
                clean_record[k] = v.tolist()
            elif hasattr(v, "item"):  # numpy scalar
                clean_record[k] = v.item()
            elif isinstance(v, (datetime.datetime, datetime.date)):
                clean_record[k] = v.isoformat()  # "YYYY-MM-DD" or "YYYY-MM-DDTHH:MM:SS"
            else:
                clean_record[k] = v

        return JSONResponse(content=clean_record)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


