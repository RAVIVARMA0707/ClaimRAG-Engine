import os
from langchain.agents import create_agent
from dotenv import load_dotenv
from src.api.v1.schemas.query_schema import QueryRequest
from src.api.v1.services.query_services import QueryServices
from src.api.v1.tools.vector_search_tool import vector_search
from src.api.v1.tools.fts_search_tool import fts_search
from src.api.v1.tools.hybrid_search_tool import hybrid_search

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")

def run_rag_agent(request: QueryRequest)->str:
    agent = create_agent(
        model = GOOGLE_LLM_MODEL,
        system_prompt= """
            You are a helpful assistant.

            You MUST follow these rules:
            1. ALWAYS call the tool retrieve_context before answering
            2. Decide the best tool based on the query intent:
                - fts_search → IDs, codes, keywords, error numbers
                - hybrid_search → short or mixed queries
                - vector_search → natural language or long questions
            3. You MUST use exactly ONE retrieval tool before answering.
            4. NEVER answer without using the tool
            5. Use ONLY the retrieved context
            6. If answer is not found, say: "Answer not found in documents"

            Be precise and concise.
            """,
        tools=[vector_search,fts_search,hybrid_search]
    )
    response = agent.invoke(
        {
            "messages":[{
                "role":"user","content":request.query
            }]
        }
    )

    
    answer = response["messages"][-1].content
    return QueryServices.format_results(request.query, answer)


