from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from google.cloud import bigquery
import pandas as pd
import numpy as np
# from main import client, dataset_id
from routers.config import client,dataset_id

router = APIRouter()

table = "cpes"
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
        df = df.applymap(
            lambda x: x.tolist() if isinstance(x, np.ndarray) 
            else (x.item() if isinstance(x, (np.int64, np.float64)) else x)
        )
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

@router.get("/search_by_cve_id/")
def get_cpe(
    cve_id: str = Query(..., description="CVE ID to search, e.g., CVE-2025-23118")
):
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
        clean_record = {
            k: (v.tolist() if isinstance(v, np.ndarray) else v.item() if hasattr(v, "item") else v)
            for k, v in record.items()
        }
        return JSONResponse(content=clean_record)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))