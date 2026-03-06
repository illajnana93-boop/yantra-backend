from services.rag_service import rag_service
import asyncio

async def test_hindi_rag():
    q = "श्याम यंत्र के लाभ"
    print(f"❓ Question: {q}")
    res = rag_service.get_relevant_context(q)
    print(f"📚 Context found: {len(res)} chars")
    if res:
        print(f"📝 Excerpt: {res[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_hindi_rag())
