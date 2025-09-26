from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from routers.config import client,dataset_id

router = APIRouter()

table = "FinalNews3"
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
        return JSONResponse(content={
            "page": page,
            "page_size": page_size,
            "next_page": page + 1 if has_more else None,
            "has_more": has_more,
            "records": df.to_dict(orient="records")
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))