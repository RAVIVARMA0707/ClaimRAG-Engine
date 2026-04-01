import os
import json
import re
from langchain.agents import create_agent
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from dotenv import load_dotenv
from src.api.v1.schemas.query_schema import QueryRequest,QueryResponse
from src.api.v1.tools.vector_search_tool import vector_search
from src.api.v1.tools.fts_search_tool import fts_search
from src.api.v1.tools.hybrid_search_tool import hybrid_search
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_LLM_MODEL = os.getenv("GOOGLE_LLM_MODEL")

def parse_agent_json(raw_output: str) -> dict:
    if not raw_output or not raw_output.strip():
        raise ValueError("Empty agent output")

    cleaned = raw_output.strip()

    # Remove markdown code fences if present
    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        cleaned,
        flags=re.IGNORECASE
    ).strip()

    return json.loads(cleaned)
def run_rag_agent(request: QueryRequest)->QueryResponse:
    agent = create_agent(
        model = GOOGLE_LLM_MODEL, 
        system_prompt = """
            You are a Retrieval-Augmented Insurance Claims Assistant.

            Your task:
            1. Retrieve documents using EXACTLY ONE tool.
            2. Extract rules, conditions, limits, thresholds, and procedures ONLY from retrieved documents.
            3. Apply those document rules to the USER’S INSURANCE DATA provided in JSON.
            4. Produce a conclusion derived ONLY from:
            - Document rules
            - User facts

            STRICT RULES:
            - You MUST call exactly one retrieval tool.
            - You MUST NOT answer without retrieval.
            - You MUST NOT use general knowledge or assumptions.
            - Documents define RULES. User JSON defines FACTS.

            Tool selection:
            - fts_search → IDs, codes, error numbers, policy numbers
            - hybrid_search → short or ambiguous queries
            - vector_search → natural language or eligibility questions

            Decision logic:
            - Explicit approval rules → Eligible
            - Explicit denial rules → Not Eligible
            - Conditional, procedural, or review-related rules → Requires Review
            - If no applicable rule exists at all → "Answer not found in documents"

            OUTPUT FORMAT (JSON only):
            {
            "answer": "<string>",
            "source": "<string>",
            "page": "<string>",
            "confidence score":" <string> (value should be between 0-1) (the confidence score
            should depend on the agents answer, if it could produce accurate results the confidence should be 
            high , if it could not produce accurate results the confidence should be low, overall 
            you should internally calculate it)
            }

            Style:
            - Use explicit decisions (Eligible / Not Eligible / Requires Review)
            - Reference user values numerically
            - State WHY the conclusion applies
            - Do NOT invent policy clauses or missing rules


        """,
        tools=[vector_search,fts_search,hybrid_search]
    )
    try:
        response = agent.invoke(
            {
                "messages":[
                     {
                        "role": "system",
                        "content": f"""
                        User Insurance Profile (JSON):
                        {json.dumps(request.insurance_data, indent=2)}

                        IMPORTANT:
                        - This data belongs to the user
                        - Use it ONLY for reasoning and comparison
                        - Do NOT invent missing fields
                        """
                     },
                     {
                           "role":"user","content":request.query
                     }
                ]

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
        
        raw_output = response["messages"][-1].text
        print("RAW OUTPUT FROM AGENT ↓↓↓")
        print(repr(raw_output))
        data = parse_agent_json(raw_output)

        return QueryResponse(
            response=data["answer"],
            doc_name=data.get("source"),
            page=data.get("page"),
            confidence=data.get("confidence score")
        )
    
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

