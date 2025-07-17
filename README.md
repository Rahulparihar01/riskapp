# Cybersecurity Data API

This project is a FastAPI application designed to fetch paginated data from Google BigQuery tables within the `CyberSecurity` dataset. It uses a service account for authentication and provides endpoints to query the `FinalNews3`, `CVEs`, and `CWEs_test` tables.

## Features
- **Endpoints**:
  - `/get-finalnew3-data`: Retrieves paginated records from the `FinalNews3` table.
  - `/get-cves-data`: Retrieves paginated records from the `CVEs` table.
  - `/get-CWEs-data`: Retrieves paginated records from the `CWEs_test` table.
- **Pagination**: Supports `page` and `page_size` query parameters for controlled data retrieval.
- **Error Handling**: Returns HTTP exceptions for query failures.
- **Data Encoding**: Uses `jsonable_encoder` for proper JSON serialization in the `CWEs_test` endpoint.


## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Rahulparihar01/riskapp.git
   cd riskapp
   ```

2. **Install Dependencies**:
   Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud Credentials**:
   - Place the service account key file (`loyal-weaver-427600-s9-77fc8a9ce15a.json`) in the project root.
   - Ensure the service account has access to the BigQuery project and `CyberSecurity` dataset.

4. **Run the Application**:
   Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be accessible at `http://127.0.0.1:8000`.

## Usage
- Use tools like `curl`, Postman, or a browser to access the API.
- Example request:
  ```bash
  curl "http://127.0.0.1:8000/get-finalnew3-data?page=1&page_size=10"
  ```
- Response format:
  ```json
  {
    "page": 1,
    "page_size": 10,
    "next_page": 2,
    "has_more": true,
    "records": [...]
  }
  ```

## Endpoints
- **GET /get-finalnew3-data**: Fetches paginated data from `FinalNews3`.
- **GET /get-cves-data**: Fetches paginated data from `CVEs`.
- **GET /get-CWEs-data**: Fetches paginated data from `CWEs_test`.

Each endpoint accepts:
- `page`: Page number (default: 1).
- `page_size`: Records per page (default: 10).

## Notes
- The `CWEs` endpoint is commented out; the active endpoint uses `CWEs_test`.
- Verify that `FinalNews3`, `CVEs`, and `CWEs_test` tables exist in the `CyberSecurity` dataset.
- The `CWEs_test` endpoint uses `jsonable_encoder` to handle complex data types.

## Troubleshooting
- **Authentication Issues**: Ensure the service account key file is valid and has correct permissions.
- **Table Not Found**: Confirm the tables exist in the `CyberSecurity` dataset.
- **Connection Errors**: Check internet connectivity and Google Cloud project settings.