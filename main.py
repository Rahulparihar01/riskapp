from fastapi import FastAPI, Query, HTTPException
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI()

# Service account key file path
key_path = "loyal-weaver-427600-s9-77fc8a9ce15a.json"

# Set up BigQuery credentials and client
credentials = service_account.Credentials.from_service_account_file(key_path)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)
dataset_id = "CyberSecurity"

# @app.get("/get-data")
# def get_data():
#     table="FinalNews3"
#     full_table_id = f"{client.project}.{dataset_id}.{table}"

#     try:
#         query = f"SELECT * FROM `{full_table_id}`"
#         df = client.query(query).to_dataframe()

#         return JSONResponse(content=df.to_dict(orient="records"))

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

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





# @app.get("/get-CWEs-data")
# def get_data(
#     # table: str = Query(..., description="Table name inside the CyberSecurity dataset"),
#     page: int = Query(1, ge=1),
#     page_size: int = Query(10, ge=1)
# ):
#     table= "CWEs"
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

