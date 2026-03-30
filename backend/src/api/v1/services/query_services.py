from src.api.v1.schemas.query_schema import QueryRequest,QueryResponse
from src.core.db import get_vector_store

class QueryServices():

    def user_query(request: str) ->QueryResponse:
        vector_store = get_vector_store()
        print("searching")
        docs = vector_store.similarity_search(query=request,k=5)
        print("Search completed")

        return {
            "query":request,
            "results": "\n".join([ doc.page_content for doc in docs])
        }


