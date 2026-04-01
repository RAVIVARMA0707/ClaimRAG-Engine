from dotenv import load_dotenv  #uv add python-dotenv
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from langchain_postgres import PGVector   # uv add langchain-postgres
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

PG_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING")
PG_CONNECTION = os.getenv("PG_CONNECTION")

#Used to craete a embeddings for a Chunks
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDINGS_MODEL"),
        api_key=os.getenv("GOOGLE_API_KEY"),
        output_dimensionality=1536
    )

#Used to store the embedding into the vector database
def get_vector_store(collection_name: str = "insurance_claim_collection"):
    return PGVector(
        collection_name=collection_name,
        connection=PG_CONNECTION_STRING,
        embeddings=get_embeddings(),
        use_jsonb=True
    )  


def setup_fts_index():
    conn = psycopg2.connect(PG_CONNECTION)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS langchain_pg_embedding_fts_idx
        ON langchain_pg_embedding
        USING GIN (to_tsvector('english', document));
    """)

    cursor.close()
    conn.close()  