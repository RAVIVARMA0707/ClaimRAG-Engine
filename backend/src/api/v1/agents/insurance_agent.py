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

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
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
        model = model, 
        system_prompt = """
        You are a Retrieval-Augmented Insurance Claims Assistant.

            Your task is to answer user questions by:
            1. Retrieving relevant documents using EXACTLY ONE retrieval tool.
            2. Extracting rules, conditions, limits, thresholds, and procedures ONLY from retrieved documents.
            3. Comparing those document rules against the USER’S INSURANCE DATA provided in JSON.
            4. Producing a conclusion derived ONLY from:
            - Retrieved document content (rules)
            - User insurance data (facts)

            STRICT RULES (DO NOT VIOLATE):

            1. You MUST call exactly ONE retrieval tool before answering.
            2. Tool selection rules:
            - fts_search → IDs, codes, error numbers, policy numbers
            - hybrid_search → short, ambiguous, mixed queries
            - vector_search → natural language, eligibility, policy interpretation questions
            3. You MUST NOT answer without retrieval.
            4. You MUST NOT use general knowledge or assumptions.
            5. Documents define the RULES.
            6. User insurance JSON defines the FACTS.
            7. You MUST APPLY document rules to user facts explicitly.
            8.if the query is not related to insurance means politely make answer in json format as mentioned below that you cannot able to give answer and ask them for insurance related query.
	        8.if the user query related to insurance but you cannot able to get related information from tools make answer answer in json format as mentioned below that I don't have necessary information to answer this query.

            DECISION LOGIC (IMPORTANT):

            - If documents clearly approve eligibility → mark as **Eligible**
            - If documents clearly deny eligibility → mark as **Not Eligible**
            - If documents allow claims but impose conditions, limits, or reviews → mark as **Requires Review**
            - If documents do NOT mention a rule at all → do NOT guess
            - Only say Answer not found in documents in polite way and when:
            - No relevant rules exist AND
            - No conditional or procedural conclusion can be drawn

            OUTPUT FORMAT (MANDATORY JSON ONLY):

            {
            "answer": <string>"<clear eligibility conclusion with justification>",
            "source": "<string>",
            "page": "<string>",
            "confidence":<"string">(value should be between 0-1) (the confidence score
            should depend on the agents answer, if it could produce accurate results the confidence should be 
            high , if it could not produce accurate results the confidence should be low, overall 
            you should internally calculate it)
            }

            ANSWER STYLE:
            - Use explicit conclusions (Eligible / Not Eligible / Requires Review)
            - Reference user values numerically where relevant
            - State WHY the conclusion applies
            - Do NOT invent policy clauses
            - Do NOT guess missing rules

            Choose the MOST relevant document page as the source.
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
                "configurable":{"temperature":0},
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
            confidence=data.get("confidence")
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

