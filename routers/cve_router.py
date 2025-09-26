from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from google.cloud import bigquery
import numpy as np
from typing import Optional
from routers.config import client,dataset_id


router = APIRouter()

table = "CVEs"
full_table_id = f"{client.project}.{dataset_id}.{table}"

def query_bigquery(query: str):
    try:
        df = client.query(query).to_dataframe()
        df = df.replace({np.nan: None})
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def build_filter(field: str, value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    val = value.strip().lower()
    if val == "null":
        return f"{field} IS NULL"
    elif val == "":
        return f"{field} = ''"
    elif val == "true":
        return f"{field} = TRUE"
    elif val == "false":
        return f"{field} = FALSE"
    else:
        return f"{field} = '{value}'"

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
def get_cve_by_id(cve_id: str):
    query = f"SELECT * FROM `{full_table_id}` WHERE cve_id = '{cve_id}' LIMIT 1"
    df = query_bigquery(query)
    if df.empty:
        raise HTTPException(status_code=404, detail="CVE not found")
    return JSONResponse(content=jsonable_encoder(df.to_dict(orient="records")[0]))

@router.get("/filter-date")
def filter_cve(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format")
):
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

@router.get("/severity/{severity}")
def get_cves_by_severity(severity: str, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    query = f"""
    SELECT * FROM `{full_table_id}`
    WHERE UPPER(severity) = '{severity.upper()}'
    ORDER BY published_date DESC
    LIMIT {page_size + 1} OFFSET {offset}
    """
    df = query_bigquery(query)
    has_more = len(df) > page_size
    df = df.head(page_size)
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
        "records": jsonable_encoder(df.to_dict(orient="records"))
    })

@router.get("/status/{status}")
def get_cves_by_status(status: str, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    query = f"""
    SELECT * FROM `{full_table_id}`
    WHERE vulnerability_status = '{status}'
    ORDER BY published_date DESC
    LIMIT {page_size + 1} OFFSET {offset}
    """
    df = query_bigquery(query)
    has_more = len(df) > page_size
    df = df.head(page_size)
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
        "records": jsonable_encoder(df.to_dict(orient="records"))
    })

@router.get("/published")
def get_cves_by_date(
    published_after: str = Query(..., description="YYYY-MM-DD"),
    published_before: str = Query(..., description="YYYY-MM-DD"),
    page: int = 1,
    page_size: int = 10
):
    offset = (page - 1) * page_size
    query = f"""
    SELECT * FROM `{full_table_id}`
    WHERE published_date >= '{published_after}' AND published_date <= '{published_before}'
    ORDER BY published_date DESC
    LIMIT {page_size + 1} OFFSET {offset}
    """
    df = query_bigquery(query)
    has_more = len(df) > page_size
    df = df.head(page_size)
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
        "records": jsonable_encoder(df.to_dict(orient="records"))
    })

@router.get("/search")
def search_cves(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    complexity: Optional[str] = None,
    authentication: Optional[str] = None,
    confidentiality_impact: Optional[str] = None,
    integraty_impact: Optional[str] = None,
    availability_impact: Optional[str] = None,
):
    offset = (page - 1) * page_size
    filters = []
    for field, val in {
        "complexity": complexity,
        "authentication": authentication,
        "confidentiality_impact": confidentiality_impact,
        "integraty_impact": integraty_impact,
        "availability_impact": availability_impact
    }.items():
        f = build_filter(field, val)
        if f:
            filters.append(f)
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = f"""
    SELECT * FROM `{full_table_id}`
    {where_clause}
    ORDER BY published_date DESC
    LIMIT {page_size + 1} OFFSET {offset}
    """
    df = query_bigquery(query)
    has_more = len(df) > page_size
    df = df.head(page_size)
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
        "records": jsonable_encoder(df.to_dict(orient="records"))
    })

@router.get("/assigner")
def filter_by_assigner(
    assigner: str = Query(..., description="Filter CVEs by assigner"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
):
    offset = (page - 1) * page_size
    if assigner.lower() == "null":
        condition = "assigner IS NULL"
    elif assigner == "":
        condition = "assigner = ''"
    else:
        condition = f"assigner = '{assigner}'"
    query = f"""
    SELECT * FROM `{full_table_id}`
    WHERE {condition}
    ORDER BY published_date DESC
    LIMIT {page_size + 1} OFFSET {offset}
    """
    df = query_bigquery(query)
    has_more = len(df) > page_size
    df = df.head(page_size)
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
        "records": jsonable_encoder(df.to_dict(orient="records"))
    })

@router.get("/attack_vector")
def filter_by_vector(
    attack_vector: str = Query(..., description="Filter CVEs by attack_vector"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
):
    offset = (page - 1) * page_size
    if attack_vector.lower() == "null":
        condition = "attack_vector IS NULL"
    elif attack_vector == "":
        condition = "attack_vector = ''"
    else:
        condition = f"attack_vector = '{attack_vector}'"
    query = f"""
    SELECT * FROM `{full_table_id}`
    WHERE {condition}
    ORDER BY published_date DESC
    LIMIT {page_size + 1} OFFSET {offset}
    """
    df = query_bigquery(query)
    has_more = len(df) > page_size
    df = df.head(page_size)
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
        "records": jsonable_encoder(df.to_dict(orient="records"))
    })

@router.get("/type")
def get_cves_by_type(type: str, page: int = 1, page_size: int = 10):
    offset = (page - 1) * page_size
    query = f"""
    SELECT * FROM `{full_table_id}`
    WHERE type = '{type}'
    ORDER BY published_date DESC
    LIMIT {page_size + 1} OFFSET {offset}
    """
    df = query_bigquery(query)
    has_more = len(df) > page_size
    df = df.head(page_size)
    return JSONResponse(content={
        "page": page,
        "page_size": page_size,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
        "records": jsonable_encoder(df.to_dict(orient="records"))
    })