import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import uuid
import sys
sys.path.append('.')


from chunking_utility import TextChunker


class KnowledgeBase:
   
    
    def __init__(self, collection_name: str = "studymate_knowledge"):
        
        print("[INFO] Initializing Vector Store")
        
        
        self.client = chromadb.Client()
        
        
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        print("   Loading embedding model: all-MiniLM-L6-v2")
        print("   (This creates 384-dimensional vectors)")
        
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "AI StudyMate Vector Store"}
        )
        
        self.chunker = TextChunker(chunk_size=500, overlap=50)
        
        current_count = self.collection.count()
        
        print(f"✅ Knowledge Base '{collection_name}' ready!")
        print(f"   Current documents: {current_count} chunks")
        print()
    
    def add_document(self, text: str, metadata: Dict = None) -> List[str]:
        
        if metadata is None:
            metadata = {}
        
        print("[INFO] Processing document")
        
        
        chunks = self.chunker.chunk_text(text, method='sentences')
        print(f"   ✂️  Created {len(chunks)} chunks")
        
        
        ids = []
        texts = []
        metadatas = []
        
        for chunk in chunks:
           
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            
            
            texts.append(chunk['text'])
            
           
            chunk_metadata = {
                **metadata,  # User-provided metadata
                'chunk_id': chunk['chunk_id'],
                'word_count': chunk['word_count'],
                'method': chunk.get('method', 'unknown')
            }
            metadatas.append(chunk_metadata)
        
        
        print("[INFO] Generating embeddings")
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks to knowledge base")
        print(f"   Total chunks in KB: {self.collection.count()}\n")
        
        return ids
    
    def query(self, query_text: str, top_k: int = 3) -> List[Dict]:
       
        print(f"🔍 Searching for: '{query_text}'")
        print(f"   Looking for top {top_k} results...")
        
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        
        
        formatted_results = []
        
        for i in range(len(results['ids'][0])):
           
            distance = results['distances'][0][i] if 'distances' in results else None
            similarity = (1 - distance) if distance is not None else None
            
            
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': distance,
                'similarity': similarity
            })
        
        print(f"✅ Found {len(formatted_results)} relevant chunks\n")
        
        return formatted_results
    
    def get_stats(self) -> Dict:
        
        return {
            'collection_name': self.collection.name,
            'total_chunks': self.collection.count(),
            'embedding_dimension': 384,  # for all-MiniLM-L6-v2
            'embedding_model': 'all-MiniLM-L6-v2'
        }
    
    def clear(self):
        
        
        print("⚠️  Clearing knowledge base...")
        self.client.delete_collection(self.collection.name)
        
       
        self.collection = self.client.create_collection(
            name=self.collection.name,
            embedding_function=self.embedding_function
        )
        
        print("✅ Knowledge base cleared (all documents removed)\n")



