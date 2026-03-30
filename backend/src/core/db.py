from dotenv import load_dotenv  #uv add python-dotenv
import os
from langchain_postgres import PGVector   # uv add langchain-postgres
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

PG_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING")

#Used to craete a embeddings for a Chunks
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDINGS_MODEL"),
        api_key=os.getenv("GOOGLE_API_KEY")
    )

#Used to store the embedding into the vector database
def get_vector_store(collection_name: str = "insurance_claim_collection"):
    return PGVector(
        collection_name=collection_name,
        connection=PG_CONNECTION_STRING,
        embeddings=get_embeddings()
    )    