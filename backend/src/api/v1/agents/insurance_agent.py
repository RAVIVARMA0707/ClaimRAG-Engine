import os
from langchain.agents import create_agent
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from dotenv import load_dotenv
from src.api.v1.schemas.query_schema import QueryRequest,QueryResponse
from src.api.v1.tools.vector_search_tool import vector_search
from src.api.v1.tools.fts_search_tool import fts_search
from src.api.v1.tools.hybrid_search_tool import hybrid_search

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")

def run_rag_agent(request: QueryRequest)->QueryResponse:
    agent = create_agent(
        model = GOOGLE_LLM_MODEL, 
        system_prompt = """
            You are a retrieval-augmented assistant.

            You MUST follow these rules:
            1. You MUST call exactly ONE retrieval tool before answering.
            2. Decide the best tool based on the query intent:
                - fts_search → IDs, codes, keywords, error numbers
                - hybrid_search → short, ambiguous, or mixed queries
                - vector_search → natural language or long questions
            3. NEVER answer without calling a retrieval tool.
            4. Use ONLY the content returned by the tool.
            5. Do NOT use prior knowledge.
            6. If the answer is not found in the retrieved context, say exactly:
               "Answer not found in documents"

            Be precise and concise.
        """,
        tools=[vector_search,fts_search,hybrid_search]
    )
    try:
        response = agent.invoke(
            {
                "messages":[{
                    "role":"user","content":request.query
                }]
            },
            config={
                "tags" : ["insurance_agent"],
                "metadata":{
                    "user_id":"user_001",
                    "feature":"insurance_claim_lookup",
                    "env":"dev"
                },
                "run_name":"insurance_agent_run"
            }       
        )    
        answer=QueryResponse
        answer.result = response["messages"][-1].text 

        #todo
        # answer.doc_name
        # answer.page
        # answer.confidence

        return answer

    
    except ChatGoogleGenerativeAIError as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                return {
                    "response": (
                        "Currently I am experiencing high demand"
                        " get back after sometime."
                    )
                }

            # Other Google model errors
            return {"response": f"Google model error: {str(e)}"}



    # return QueryServices.format_results(request.query, answer)


