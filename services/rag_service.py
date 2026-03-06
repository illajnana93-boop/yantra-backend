import os
from typing import List, Dict
import re

class RAGService:
    def __init__(self):
        print("Initializing Production RAG Service (Lightweight Search Mode)...")
        self.documents = []
        self.kb_loaded = False
        
        # Comprehensive English/Hinglish -> Hindi keyword mapping
        self.translation_map = {
            # Core subjects
            "shyam": "श्याम", "yantra": "यंत्र", "baba": "बाबा",
            "khatu": "खाटू", "guruji": "गुरुजी", "guru": "गुरु",
            
            # Benefits & effects
            "benefit": "लाभ", "benefits": "लाभ", "laabh": "लाभ",
            "advantage": "लाभ", "effect": "प्रभाव", "effects": "प्रभाव",
            "result": "फल", "power": "शक्ति", "importance": "महत्व",
            "significance": "महत्व", "why": "क्यों", "what": "क्या",
            
            # Placement & location
            "placement": "स्थान", "place": "स्थान", "direction": "दिशा",
            "where": "कहाँ", "kahan": "कहाँ", "rakhe": "रखें",
            "keep": "रखें", "install": "स्थापित", "home": "घर",
            "house": "घर", "office": "कार्यालय", "business": "व्यापार",
            "shop": "दुकान", "north": "उत्तर", "east": "पूर्व",
            
            # Worship & ritual
            "worship": "पूजा", "pooja": "पूजा", "puja": "पूजा",
            "ritual": "विधि", "vidhi": "विधि", "how": "कैसे",
            "method": "विधि", "process": "विधि", "perform": "करें",
            "activate": "जागृत", "jagrit": "जागृत", "energize": "जागृत",
            "incense": "अगरबत्ती", "attar": "इत्र", "perfume": "इत्र",
            "flower": "फूल", "lamp": "दीपक", "light": "दीपक",
            "days": "दिन", "45": "४५", "daily": "प्रतिदिन",
            
            # Stories & history
            "story": "कहानी", "katha": "कथा", "history": "इतिहास",
            "origin": "उत्पत्ति", "name": "नाम", "real": "असली",
            "original": "असली", "who": "कौन", "when": "कब",
            
            # Spiritual concepts
            "blessing": "आशीर्वाद", "ashirwad": "आशीर्वाद",
            "grace": "कृपा", "protection": "रक्षा", "raksha": "रक्षा",
            "energy": "ऊर्जा", "spiritual": "आध्यात्मिक", "divine": "दिव्य",
            "faith": "श्रद्धा", "devotion": "भक्ति", "bhakti": "भक्ति",
            "prayer": "प्रार्थना", "mantra": "मंत्र", "gotra": "गोत्र",
            
            # Life topics
            "wealth": "धन", "money": "धन", "dhan": "धन",
            "health": "स्वास्थ्य", "disease": "रोग", "cure": "ठीक",
            "marriage": "विवाह", "love": "प्रेम", "family": "परिवार",
            "children": "संतान", "job": "नौकरी", "career": "व्यापार",
            "success": "सफलता", "peace": "शांति", "happiness": "सुख",
            "problem": "समस्या", "solution": "समाधान", "wish": "इच्छा",
            
            # Temple & delivery
            "temple": "मंदिर", "mandir": "मंदिर", "price": "मूल्य",
            "cost": "मूल्य", "delivery": "वितरण", "get": "प्राप्त",
            "receive": "प्राप्त", "wall": "दीवार", "name": "नाम",
            "vision": "दृष्टि", "mission": "मिशन", "100": "सौ",
        }
        print("✓ Production RAG Service Ready (Full English Support Active)")

    def load_local_knowledge(self) -> bool:
        """Reads all .txt files from the knowledge_base folder."""
        kb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'knowledge_base'))
        if not os.path.exists(kb_path):
            print(f"✗ Knowledge base path not found: {kb_path}")
            return False
            
        print(f"Reading spiritual texts from: {kb_path}")
        docs_to_index = []
        try:
            for filename in os.listdir(kb_path):
                if filename.endswith(".txt"):
                    file_path = os.path.join(kb_path, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():
                                # Chunking logic to avoid "too many points" (returning huge files)
                                # We split by paragraphs or double newlines first
                                paragraphs = content.split('\n\n')
                                for para in paragraphs:
                                    para = para.strip()
                                    if not para:
                                        continue
                                    
                                    # If a paragraph is too long, split it further by lines or fixed size
                                    if len(para) > 800:
                                        lines = para.split('\n')
                                        current_chunk = []
                                        current_length = 0
                                        for line in lines:
                                            if current_length + len(line) > 800 and current_chunk:
                                                docs_to_index.append({
                                                    'content': '\n'.join(current_chunk),
                                                    'metadata': {'source': filename}
                                                })
                                                current_chunk = []
                                                current_length = 0
                                            current_chunk.append(line)
                                            current_length += len(line)
                                        if current_chunk:
                                            docs_to_index.append({
                                                'content': '\n'.join(current_chunk),
                                                'metadata': {'source': filename}
                                            })
                                    else:
                                        docs_to_index.append({
                                            'content': para,
                                            'metadata': {'source': filename}
                                        })
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
            
            if docs_to_index:
                return self.load_knowledge_base(docs_to_index)
            print("✗ No valid text found in knowledge_base.")
            return False
        except Exception as e:
            print(f"Error accessing knowledge folder: {e}")
            return False

    def load_knowledge_base(self, documents: List[Dict]) -> bool:
        """Processes documents for the search engine."""
        try:
            print(f"Indexing {len(documents)} spiritual entries for search...")
            self.documents = documents
            self.kb_loaded = True
            print(f"✓ Search Index Ready: {len(self.documents)} entries indexed.")
            return True
        except Exception as e:
            print(f"✗ Indexing Error: {e}")
            return False
    
    def search(self, query: str, k: int = 3) -> List[Dict]:
        """Performs fast keyword-based matching (No ML dependency)."""
        if not self.kb_loaded:
            if not self.load_local_knowledge():
                return []
            
        try:
            # 1. Expand query for Hinglish support
            query_clean = query.lower()
            search_terms = set(re.findall(r"(?u)\b[\w']+\b", query_clean))
            
            # Map Hinglish/English to Hindi for better matching
            words_to_add = set()
            for word in search_terms:
                if word in self.translation_map:
                    words_to_add.add(self.translation_map[word])
            search_terms.update(words_to_add)
            
            # 2. Score documents based on hit count
            scored_docs = []
            for doc in self.documents:
                content = doc['content'].lower()
                score = 0
                for term in search_terms:
                    # Simple count-based scoring
                    if term in content:
                        score += 1
                
                if score > 0:
                    scored_docs.append((score, doc))
            
            # 3. Sort by score and return top K
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            
            results = []
            for score, doc in scored_docs[:k]:
                results.append({
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'score': score
                })
            
            return results
        except Exception as e:
            print(f"✗ Search failed: {e}")
            return []
            
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """Helper for AI LLM to get context easily."""
        results = self.search(query, k=k)
        if not results:
            return ""
        return "\n\n".join([r['content'] for r in results])

# Export singleton
rag_service = RAGService()