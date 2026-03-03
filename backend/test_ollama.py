import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

print("Testing Ollama embeddings...")
print("=" * 50)

try:
    from langchain_ollama import OllamaEmbeddings
    print("✓ Imported OllamaEmbeddings")
    
    emb = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434",
        request_timeout=30.0
    )
    print("✓ Created OllamaEmbeddings instance")
    
    print("\nGenerating embedding for test text...")
    result = emb.embed_query("This is a test")
    print(f"✓ Successfully generated embedding!")
    print(f"  Embedding dimension: {len(result)}")
    print(f"  First 5 values: {result[:5]}")
    
    print("\n" + "=" * 50)
    print("SUCCESS! Ollama embeddings are working correctly.")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print(f"\nFull error details:")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 50)
    print("FAILED! Please check:")
    print("1. Is Ollama running? (check with: ollama list)")
    print("2. Is nomic-embed-text model installed? (install with: ollama pull nomic-embed-text)")
    print("3. Is Ollama accessible at http://localhost:11434?")
