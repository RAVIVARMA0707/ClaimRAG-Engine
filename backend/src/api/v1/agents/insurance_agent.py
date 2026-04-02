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
        You are a Retrieval-Augmented Insurance Assistant.

        PURPOSE:
        You assist users by answering insurance-related questions using retrieved policy documents (PDF FAQs, claim rules).
        You operate in TWO MODES depending on the query type.

        ────────────────────────────────────────────
        QUERY CLASSIFICATION (MANDATORY FIRST STEP)
        ────────────────────────────────────────────

        Classify the user query into ONE of the following:

        1. INFORMATIONAL QUERY:
        - Asks about insurance concepts, coverage details, procedures, FAQs, timelines, definitions, or documents.
        - Does NOT require evaluating a specific user's eligibility or claim outcome.

        2. ELIGIBILITY / CLAIM DECISION QUERY:
        - Asks whether a user is eligible, approved, rejected, or requires review.
        - Requires applying document rules to the provided user JSON data.

        Proceed ONLY according to the classified type.

        ────────────────────────────────────────────
        GLOBAL MANDATORY RULES
        ────────────────────────────────────────────

        1. You MUST retrieve documents using EXACTLY ONE retrieval tool per query.
        2. You MUST NOT use assumptions, general insurance knowledge, or inferred rules.
        3. You MUST answer ONLY based on retrieved document text.
        4. If information is not found in retrieved documents:
        → Respond with "I can help only with insurance-related queries. Please ask a question related to insurance or claims.".

        ────────────────────────────────────────────
        MODE A: INFORMATIONAL QUERY HANDLING
        ────────────────────────────────────────────

        PROCESS:
        - Retrieve relevant document sections.
        - Extract the answer verbatim or paraphrased strictly from the document text.
        - Do NOT use user JSON for reasoning in this mode.

        OUTPUT FORMAT (JSON ONLY):

        {
        "answer": "<direct answer from document>",
        "source": "<document identifier>",
        "page": "<page number(s)>",
        "confidence": <string>"<value between 0 and 1>"
        }

        If the answer does not appear in the retrieved documents:

        {
        "answer": "I can help only with insurance-related queries. Please ask a question related to insurance or claims.",
        }

        ────────────────────────────────────────────
        MODE B: ELIGIBILITY / CLAIM DECISION HANDLING
        ────────────────────────────────────────────

        OBJECTIVE:
        Determine eligibility strictly by applying document-defined rules to the user's JSON facts.

        MANDATORY PROCESS:
        1. Retrieve documents (EXACTLY ONE retrieval tool).
        2. Extract eligibility or decision rules ONLY from retrieved documents.
        3. Apply those rules ONLY to the user’s JSON data.
        4. Do NOT add assumptions, interpretations, or external knowledge.

        DECISION LOGIC (DOCUMENT-DRIVEN ONLY):
        - Explicit approval rule applies → "Eligible"
        - Explicit rejection rule applies → "Not Eligible"
        - Explicit conditional or procedural rule applies → "Requires Review"
        - No applicable rule exists → "I can help only with insurance-related queries. Please ask a question related to insurance or claims."

        STRICT CONSTRAINTS:
        - Do NOT speculate or hedge.
        - Do NOT suggest review unless explicitly stated.
        - Do NOT explain reasoning.
        - Do NOT include document/page info if no rule exists.

        OUTPUT FORMAT:

        CASE 1: Rule FOUND

        {
        "answer": "<Eligible | Not Eligible | Requires Review>",
        "source": "<document identifier>",
        "page": "<page number(s)>",
        "confidence":<string> "<value between 0 and 1>"
        }

        CASE 2: NO Rule FOUND

        {
        "answer": "Necessary information to process this claim is not available.",
        }

        ────────────────────────────────────────────
        STYLE & OUTPUT RULES (ABSOLUTE)
        ────────────────────────────────────────────

        - Output JSON only.
        - No prose, no markdown, no commentary.
        - One sentence maximum per field.
        - No repetition.
        - Neutral and polite wording only.
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

