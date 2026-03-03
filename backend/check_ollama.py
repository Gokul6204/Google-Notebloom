from langchain_ollama import OllamaEmbeddings
import inspect
print(inspect.signature(OllamaEmbeddings.__init__))
try:
    OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
    print("Init successful without timeout")
except Exception as e:
    print(f"Init failed without timeout: {e}")

try:
    OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434", timeout=30.0)
    print("Init successful with 'timeout'")
except Exception as e:
    print(f"Init with 'timeout' failed: {e}")