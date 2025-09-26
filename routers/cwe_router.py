from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from google.cloud import bigquery
import numpy as np
import datetime
from routers.config import client,dataset_id

router = APIRouter()

table = "CWEs_test"
full_table_id = f"{client.project}.{dataset_id}.{table}"

@router.get("/data")
def get_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    try:
        offset = (page - 1) * page_size
        query = f"SELECT * FROM `{full_table_id}` LIMIT {page_size + 1} OFFSET {offset}"
        df = client.query(query).to_dataframe()
        has_more = len(df) > page_size
        df = df.head(page_size)
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

@router.get("/filter_cve_id/")
def get_cwe_id(
    cve_id: str = Query(..., description="CVE ID to search, e.g., CVE-2025-23118")
):
    try:
        query = f"""
            SELECT *
            FROM `{full_table_id}`
            WHERE cve_id = @cve_id

        """
        print(query)
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("cve_id", "STRING", cve_id)
            ]
        )
        df = client.query(query, job_config=job_config).to_dataframe()
        # print(df)
        if df.empty:
            return JSONResponse(
                content={"message": f"No records found for {cve_id}"},
                status_code=404
            )
        
        # Convert dataframe to list of dicts with clean formatting
        records = []
        for record in df.to_dict(orient="records"):
            clean_record = {}
            for k, v in record.items():
                if isinstance(v, np.ndarray):
                    clean_record[k] = v.tolist()
                elif hasattr(v, "item"):
                    clean_record[k] = v.item()
                elif isinstance(v, (datetime.datetime, datetime.date)):
                    clean_record[k] = v.isoformat()
                else:
                    clean_record[k] = v
            records.append(clean_record)

        return JSONResponse(content={"results": records})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/cwe_id/")
def get_cwe_id(
    cwe_id: str = Query(..., description="CWE ID to search, e.g., CWE-119")
):
    try:
        query = f"""
            SELECT *
            FROM `{full_table_id}`
            WHERE cwe = @cwe
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("cwe", "STRING", cwe_id)
            ]
        )
        df = client.query(query, job_config=job_config).to_dataframe()
        
        if df.empty:
            return JSONResponse(
                content={"message": f"No records found for {cwe_id}"},
                status_code=404
            )
        
        # Convert dataframe to list of dicts with clean formatting
        records = []
        for record in df.to_dict(orient="records"):
            clean_record = {}
            for k, v in record.items():
                if isinstance(v, np.ndarray):
                    clean_record[k] = v.tolist()
                elif hasattr(v, "item"):
                    clean_record[k] = v.item()
                elif isinstance(v, (datetime.datetime, datetime.date)):
                    clean_record[k] = v.isoformat()
                else:
                    clean_record[k] = v
            records.append(clean_record)

        return JSONResponse(content={"results": records})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
