from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str =  Field(...,description="User query")
    category: Optional[str] = Field(
        default=None,
        description="Optional metadata filter"
    )



class QueryResponse(BaseModel):
    result: str 
    page:Optional[str]
    doc_name:Optional[str]
    confidence:Optional[str]
