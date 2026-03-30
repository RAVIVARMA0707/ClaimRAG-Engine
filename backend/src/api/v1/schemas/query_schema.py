from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str =  Field(...,description="User query")
    category: Optional[str] = Field(
        default=None,
        description="Optional metadata filter"
    )

class QueryResult(BaseModel):
    content: str
    metadata: Dict[str,Any]

class QueryResponse(BaseModel):
    query: str
    results: List[QueryResult]