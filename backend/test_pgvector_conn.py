
import os
import logging
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"Testing PGVector with: {db_url}")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)

try:
    vector_db = PGVector(
        connection=db_url,
        collection_name="test_collection",
        embeddings=embeddings,
        use_jsonb=True
    )
    print("PGVector initialized!")
    
    # Try a simple query
    print("Trying a simple query...")
    vector_db.similarity_search("test", k=1)
    print("Query successful!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
