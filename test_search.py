from services.rag_service import rag_service

query = "श्याम यंत्र को कहाँ रखना चाहिए"

results = rag_service.search(query)

print("\nUser Question:")
print(query)

print("\nSearch Results:")
print(results)