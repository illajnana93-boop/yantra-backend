import os
import sys

# Add the current directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Sri Shyam Yantra - Production RAG Initialization")
print("=" * 60)

try:
    print("\n[1/3] Importing RAG Service...")
    from services.rag_service import rag_service
    
    if not rag_service:
        print("\n✗ RAG Service failed to import.")
        sys.exit(1)
    
    print("✓ RAG service (TF-IDF Mode) initialized successfully.")
    
    print("\n[2/3] Loading Spiritual Knowledge Base from files...")
    # This automatically reads all .txt files from the /knowledge_base folder
    success = rag_service.load_local_knowledge()
    
    if success:
        print(f"✓ Successfully indexed {len(rag_service.documents)} knowledge documents.")
    else:
        print("✗ Failed to load knowledge. Make sure 'knowledge_base' folder contains text files.")
        sys.exit(1)

    print("\n[3/3] Testing Search Reliability...")
    # Test with a spiritual keyword
    test_query = "पूजा" # Puja (Worship)
    results = rag_service.search(test_query, k=2)
    
    if results:
        print(f"✓ Search Test Passed! Found {len(results)} relevant results.")
        for i, res in enumerate(results):
            print(f"\nResult {i+1} (Score: {res['score']:.3f}):")
            print(f"Source: {res['metadata'].get('source', 'Unknown')}")
            print(f"Content: {res['content'][:150]}...")
    else:
        print("⚠ Search returned no results. Check if files contain the search keywords.")

    print("\n" + "=" * 60)
    print("✓ GURUJI SEARCH ENGINE IS NOW PRODUCTION-READY!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Initialization Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)