import os
from langchain.agents import create_agent
from dotenv import load_dotenv
from src.api.v1.schemas.query_schema import QueryRequest,QueryResponse
from src.api.v1.services.query_services import QueryServices

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")

def retrieval_tool(query :str)->QueryResponse:
    """
        Retrieves relevant context from vector store for a given query.
    """
    query_service = QueryServices
    return query_service.user_query(query)



def run_rag_agent(request: QueryRequest)->str:
    agent = create_agent(
        model = GOOGLE_LLM_MODEL,
        system_prompt= """
            You are a helpful assistant.

            You MUST follow these rules:
            1. ALWAYS call the tool retrieve_context before answering
            2. NEVER answer without using the tool
            3. Use ONLY the retrieved context
            4. If answer is not found, say: "Answer not found in documents"

            Be precise and concise.
            """,
        tools=[retrieval_tool]
    )
    response = agent.invoke(
        {
            "messages":[{
                "role":"user","content":request.query
            }]
        }
    )

    return response["messages"][-1].content

