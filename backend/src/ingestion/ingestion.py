from unittest import loader
from dotenv import load_dotenv
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader 
from src.core.db import get_vector_store
load_dotenv()
PG_CONNECTION = os.getenv("PG_CONNECTION_STRING")
def ingest_pdf(file_path):
    """Ingest a PDF file and save it in vector database"""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    print("Pages: "+str(len(docs)))

    for doc in docs:
        doc.metadata.update({
            "source":file_path,
            "document_extension":"pdf",
            "page":doc.metadata.get("page",None),
            "category":"hr_support_desk",
            "last_updated":os.path.getmtime(file_path)
        })

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100, 
        separators=[
            "\n\n",
            "\n",
            ".",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(docs)
    print("Chunks: "+str(len(chunks)))

    vector_store = get_vector_store(collection_name="insurance_claim_collection")

    vector_store.add_documents(chunks)
    print("Ingestion completed successfully!")

if __name__ == "__main__":
    ingest_pdf(r"data\Insurance_claim.pdf")

