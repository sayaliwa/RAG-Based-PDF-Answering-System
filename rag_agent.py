
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)


from gemini_wrapper import GeminiWrapper
from knowledge_base import KnowledgeBase
from typing import List, Dict


class RAGAgent:
    
    def __init__(
        self,
        gemini_api_key: str,
        knowledge_base: KnowledgeBase = None,
        temperature: float = 0.3
    ):
        
        print("🚀 Initializing RAG Agent...\n")
        
        
        self.llm = GeminiWrapper(
            api_key=gemini_api_key,
            model_name="gemini-2.5-flash",
            temperature=temperature
        )
        
        
        self.llm.set_persona(
            """
            You are AI StudyMate.

            You have access to previous conversation history.

            Use both:
            1. Conversation history.
            2. Retrieved documents.

            If the user asks follow-up questions such as:

            - Explain more.
            - Give an example.
            - Explain the third type.
            - Why?

            Understand the previous context before answering.

            Never hallucinate.
            """)
        
        self.knowledge_base = knowledge_base
        
        print("✅ RAG Agent ready!")
        print("   Mode: Retrieval-Augmented Generation")
        print("   Source attribution: Enabled")
        print("   Hallucination protection: Active")
        print()
    
    def set_knowledge_base(self, knowledge_base: KnowledgeBase):
       
        
        self.knowledge_base = knowledge_base
        
        stats = knowledge_base.get_stats()
        print(f"✅ Knowledge base connected!")
        print(f"   Collection: {stats['collection_name']}")
        print(f"   Chunks available: {stats['total_chunks']}\n")
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict]:
        
        if not self.knowledge_base:
            print("⚠️  No knowledge base connected!")
            return []
        
        
        results = self.knowledge_base.query(query, top_k=top_k)
        return results
    
    def build_prompt_with_context(self, query: str, context_chunks: List[Dict]) -> str:
        
        
        if not context_chunks:
            return f"""The user asked: "{query}"

You don't have any relevant information in your knowledge base to answer this question.
Please respond honestly that you don't have this information available, and suggest 
that the user might need to provide relevant documents or ask a different question."""
        
        
        context_text = "=== KNOWLEDGE BASE CONTEXT ===\n\n"
        context_text += "Here are relevant excerpts from the knowledge base:\n\n"
        
        
        for i, chunk in enumerate(context_chunks, 1):
            source = chunk['metadata'].get('source', 'Unknown Source')
            source_type = chunk['metadata'].get('source_type', '')
            
            context_text += f"[Source {i}: {source}]\n"
            context_text += f"{chunk['text']}\n\n"
        
        
        prompt = f"""{context_text}
=== USER QUESTION ===


"""
        
        return prompt
    
    def answer(self,query: str,chat_history=None,top_k: int = 3,verbose: bool = True) -> Dict:
       
        if verbose:
            print(f"\n{'='*70}")
            print(f"🔍 RAG PIPELINE STARTING")
            print(f"{'='*70}\n")
            print(f"Query: '{query}'\n")

        history_context = ""

        if chat_history:
            history_context = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in chat_history[-6:]
            ]
        )    
        
      
        if verbose:
            print("Step 1/3: 🔍 Retrieving relevant context...")
        
       
        search_query = query

        if history_context:
            search_query = f"""
        Previous Conversation:
        {history_context}

        Current Question:
        {query}
        """

        context_chunks = self.retrieve_context(
        search_query,
        top_k=top_k)
        
        if context_chunks:
            if verbose:
                print(f"   ✅ Found {len(context_chunks)} relevant chunks")
                for i, chunk in enumerate(context_chunks, 1):
                    similarity = chunk.get('similarity', 0) * 100
                    source = chunk['metadata'].get('source', 'Unknown')
                    print(f"      {i}. {source} (Similarity: {similarity:.1f}%)")
        else:
            if verbose:
                print("   ⚠️  No relevant context found")
        
       
        if verbose:
            print("\nStep 2/3: 📝 Building prompt with context...")
        
        
        context_prompt = self.build_prompt_with_context(
        query,
        context_chunks)

        prompt = f"""
        You are AI StudyMate, a conversational AI learning assistant.

        Conversation History:
        {history_context}

        Retrieved Context:
        {context_prompt}

        Current Question:
        {query}

        Instructions:
        - Use the conversation history to understand follow-up questions.
        - Answer using ONLY the retrieved context whenever possible.
        - If the retrieved documents don't contain the answer, clearly say so.
        - Never invent facts.
        - If appropriate, mention the source document(s).
        - Explain concepts in a clear, student-friendly manner.

        Answer:
      """
        
        if verbose:
            print(f"   ✅ Prompt ready ({len(prompt)} characters)")
        
        
        if verbose:
            print("\nStep 3/3: 🤖 Generating answer with Gemini...")
        
        
        answer = self.llm.generate(prompt)
        
        if verbose:
            print(f"   ✅ Answer generated ({len(answer)} characters)\n")
            print(f"{'='*70}\n")
        
        result = {
            'query': query,
            'answer': answer,
            'sources': [
                {
                    'text': chunk['text'][:300] + '...' if len(chunk['text']) > 300 else chunk['text'],
                    'metadata': chunk['metadata'],
                    'similarity': chunk.get('similarity', 0)
                }
                for chunk in context_chunks
            ],
            'num_sources': len(context_chunks),
            'has_sources': len(context_chunks) > 0
        }
        
        return result
    
   