from fastapi import FastAPI
from google.cloud import bigquery
from google.oauth2 import service_account
import os
from routers import cve_router, cwe_router, cpe_router, finalnews_router

# Initialize FastAPI app
app = FastAPI()

# Service account key file path
key_path = "loyal-weaver-427600-s9-77fc8a9ce15a.json"


# Include routers
app.include_router(cve_router.router, prefix="/cve", tags=["CVE"])
app.include_router(cwe_router.router, prefix="/cwe", tags=["CWE"])
app.include_router(cpe_router.router, prefix="/cpe", tags=["CPE"])
app.include_router(finalnews_router.router, prefix="/finalnews", tags=["FinalNews"])

@app.get("/")
async def root():
    return {"message": "Welcome to the CyberSecurity API"}