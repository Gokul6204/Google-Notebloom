
try:
    from langchain_ollama import OllamaEmbeddings
    print("Imported langchain_ollama")
    emb = OllamaEmbeddings(model="nomic-embed-text")
    print(" initialized OllamaEmbeddings")
    res = emb.embed_query("test")
    print(f"SUCCESS: {res[:2]}")
except Exception as e:
    print(f"ERROR_DETAIL: {e}")
