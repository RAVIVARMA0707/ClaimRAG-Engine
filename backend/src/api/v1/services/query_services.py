import os
import shutil
from pathlib import Path
from fastapi import UploadFile,File
from src.ingestion.ingestion import ingest_pdf
from src.api.v1.schemas.query_schema import QueryRequest,QueryResponse
from src.api.v1.agents.insurance_agent import run_rag_agent 

class QueryServices:    

    DATA_DIR = Path("data")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / "Insurance_claim.pdf"

    @classmethod
    def upload_file(cls,file: UploadFile = File(...)):    

        with open(cls.file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ingest_pdf(str(cls.file_path))

        return {
            "message": "File uploaded and ingested successfully",
            "saved_to": str(cls.file_path)
        }
    
    @staticmethod
    def run_rag_agent(request: QueryRequest)->QueryResponse:
        return run_rag_agent(request)

