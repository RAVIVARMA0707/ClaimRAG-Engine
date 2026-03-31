from fastapi import APIRouter,UploadFile,File
from src.api.v1.schemas.query_schema import QueryRequest,QueryResponse
from src.api.v1.services.query_services import QueryServices

router = APIRouter()

@router.post("/query")
def query_endpoint(request: QueryRequest)->dict:
    return QueryServices.run_rag_agent(request)

@router.post("/upload-pdf")
def upload_file(file: UploadFile = File(...)):
    return QueryServices.upload_file(file=file)

@router.post("/ingest")
def do_ingestion():
    return QueryServices.ingestion()
