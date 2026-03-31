from fastapi import APIRouter
from src.api.v1.schemas.query_schema import QueryRequest,QueryResponse
from src.api.v1.agent.agent import run_rag_agent 

router = APIRouter()



@router.post("/query")
def query_endpoint(request: QueryRequest)->dict:
    return run_rag_agent(request)