

import streamlit as st
import sys
import os
from pathlib import Path
from PyPDF2 import PdfReader


# Add project root to sys.path so package imports like DAY_2.knowledge_base work
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try standard package imports first; fallback to direct module import if needed
try:
    from rag_agent import RAGAgent
    from knowledge_base import KnowledgeBase
except ModuleNotFoundError:
    # Fallback for environments running the file directly where packages aren't resolved
    sys.path.insert(0, os.path.join(project_root, 'DAY_2'))
    sys.path.insert(0, os.path.join(project_root, 'DAY_3'))
    from rag_agent import RAGAgent
    from knowledge_base import KnowledgeBase


def init_session_state():
    
    if 'agent'not in st.session_state:
        st.session_state.agent = None
    
    
    if 'messages' not in st.session_state:
        st.session_state.messages =[]
    
   
    if 'kb' not in st.session_state:
        st.session_state.kb = None
    
    if 'auto_initialized' not in st.session_state:
        st.session_state.auto_initialized = False

    if 'question_count' not in st.session_state:
        st.session_state.question_count = 0

    if 'documents_uploaded' not in st.session_state:
        st.session_state.documents_uploaded = 0    


def main():
    """
    Main application function.
    
    This is where we build our beautiful web interface!
    """
    
    st.set_page_config(
        
        page_title="📚 AI StudyMate",
        layout="wide",  
        initial_sidebar_state="expanded"
    )
   
    init_session_state()
    
    
    env_api_key = os.getenv('GEMINI_API_KEY')
    if env_api_key and not st.session_state.auto_initialized and st.session_state.agent is None:
        try:
            
            st.session_state.kb = KnowledgeBase("studymate_knowledge")
            
            st.session_state.agent = RAGAgent(
                gemini_api_key=env_api_key,
                knowledge_base=st.session_state.kb,
            )
            
            st.session_state.auto_initialized = True
            
        except Exception as e:
            pass
        
    
    # =================================================================
    # HEADER
    # =================================================================

    st.title("📚 AI StudyMate")
    st.markdown("### Your Personal Multi-Document Learning Assistant")
    st.caption("Powered by Gemini 2.5 Flash • ChromaDB • Semantic Search")
    
    st.markdown("---")
    
    # =================================================================
    # SIDEBAR - Configuration & Setup
    # =================================================================
    
    with st.sidebar:
        # Check for API key in environment
        env_api_key = os.getenv('GEMINI_API_KEY')
        
        # Only show Configuration section if NO environment API key
        if not env_api_key:
            st.header("⚙️ Configuration")
            
            
            api_key = st.text_input(
                "Gemini API Key",
                type="password",
                help="Get your free key from https://aistudio.google.com/app/apikey",
                placeholder="Enter your API key here..."
            )
            
            with st.expander("💡 API Key Tips"):
                st.markdown("""
                **Getting an API Key:**
                1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
                2. Sign in with your Google account
                3. Click "Get API Key" or "Create API Key"
                4. Copy the key and paste it above
                
                **Free Tier Limits:**
                - 15 requests per minute
                - 1,500 requests per day
                - If you hit limits, wait 60 seconds or use a new key
                
                **If You Change Keys:**
                - Click "🔄 Reset Knowledge Base" below
                - Re-initialize the agent with the new key
                """)
            
            
            if st.button("🚀 Initialize Agent", type="primary", use_container_width=True):
                if not api_key:
                    st.error("⚠️ Please provide your Gemini API key or set GEMINI_API_KEY environment variable!")
                else:
                    with st.spinner("Initializing RAG Agent... This may take a moment..."):
                        try:
                           
                            st.session_state.kb = KnowledgeBase("studymate_knowledge")
                            
                            st.session_state.agent = RAGAgent(
                                gemini_api_key=api_key,
                                knowledge_base=st.session_state.kb,
                            )
                            
                            st.success("✅ Agent initialized successfully with Study Materials!")
                            st.balloons()  # Celebration! 🎉
                            
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            st.markdown("---")
        
        # Document upload section
        st.header("📄 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Upload documents to expand knowledge base",
            accept_multiple_files=True,
            
            type=['txt', 'md', 'pdf'],
            help="Upload .txt or .md or .pdf files containing information you want the agent to learn"
        )
        
        if uploaded_files and st.button("Process Documents", use_container_width=True):
            if st.session_state.kb is None:
                st.error("⚠️ Please initialize the agent first!")
            else:
                with st.spinner(f"Processing {len(uploaded_files)} files..."):
                    try:
                        progress_bar = st.progress(0)
                        status = st.empty()

                        total_files = len(uploaded_files)

                        for index, file in enumerate(uploaded_files):
                            status.info(f"📄 Reading {file.name}...")

                            progress_bar.progress(
                                int((index / total_files) * 100))
                            
                            file_ext = Path(file.name).suffix.lower()
                            
                           
                            file_ext = Path(file.name).suffix.lower()

                            if file_ext == ".pdf":
                                reader = PdfReader(file)
                                text = ""

                                for page in reader.pages:
                                    page_text = page.extract_text()
                                    if page_text:
                                        text += page_text

                            else:
                                text = file.read().decode("utf-8")
                            status.info("✂️ Splitting document into chunks...")

                            progress_bar.progress(
                                int(((index + 0.4) / total_files) * 100))
                            status.info("🧠 Generating embeddings...")
                            # Add to knowledge base
                            st.session_state.kb.add_document(
                                text,
                                metadata={'source': file.name, 'type': 'user-uploaded', 'file_type': file_ext}
                            )
                            progress_bar.progress(
                            int(((index + 1) / total_files) * 100))
                        
                        st.success(f"✅ Processed {len(uploaded_files)} documents successfully!")
                        status.success("✅ Knowledge Base Ready!")
                        progress_bar.empty()
                        st.session_state.documents_uploaded += len(uploaded_files)
                        
                    except Exception as e:
                        st.error(f"❌ Error processing files: {str(e)}")
        
        st.markdown("---")
        
       
        
        st.markdown("---")
        
        # Statistics section
        if st.session_state.kb:
            st.header("📈 Dashboard")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("📄 Documents",
                           st.session_state.documents_uploaded)

            with col2:
                st.metric("❓ Questions",
                          st.session_state.question_count)

            if st.session_state.agent:
                st.success("🟢 Agent Active")
            else:
                st.warning("🔴 Agent Offline")    
            st.header("📊 Knowledge Base Stats")
           
            stats = st.session_state.kb.get_stats()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Chunks", stats['total_chunks'])
            
            with col2:
                st.metric("Embedding Dim", stats['embedding_dimension'])
            
            st.caption(f"Model: {stats['embedding_model']}")
            
            
            if st.button("🔄 Reset Knowledge Base", use_container_width=True, type="secondary"):
                st.session_state.agent = None
                st.session_state.kb = None
                st.session_state.messages = []
                st.session_state.auto_initialized = False
                env_api_key = os.getenv('GEMINI_API_KEY')
                if env_api_key:
                    st.success("✅ Knowledge base reset! Refresh the page to reinitialize.")
                else:
                    st.success("✅ Knowledge base reset! Click 'Initialize Agent' to start fresh.")
                st.rerun()
        
        st.markdown("---")
        
        # Help section
        with st.expander("How to Use"):
            env_api_key = os.getenv('GEMINI_API_KEY')
            
            if env_api_key:
                
                st.markdown("""
             ### 🚀 Getting Started
             ✅ AI StudyMate is ready! Upload your learning materials and start asking questions.

            ### 📚 Supported Documents

            - 📄 PDF files (.pdf)
            - 📝 Text files (.txt)
            - 📋 Markdown files (.md)

            ### ✨ Features

            - Multi-document question answering
            - Conversational memory
            - Semantic search using vector embeddings
            - Source-aware responses with similarity scores
            - Context retrieval for transparent answers
            - Chat history download

            ### 💡 Tips

            - Upload high-quality study material for better answers.
            - Ask specific questions for more accurate responses.
            - Use follow-up questions naturally (e.g., "Explain this further").
            - Review retrieved sources to verify the answer.

            ### ❓ Example Questions

            - Summarize Chapter 3.
            - Explain Normalization with an example.
            - What are the advantages of CNN over ANN?
            - Compare Logistic Regression and Decision Trees.
            - Generate revision notes from this document.
            - What are the important interview questions from this topic?
        
            """)
            else:
                # Full help with setup instructions
                st.markdown("""
                ### 🚀 Getting Started

                1. Enter your Gemini API key.
                2. Click **Initialize Agent**.
                3. Upload your study documents.
                4. Start asking questions.

                ### 📚 Supported Documents

                - 📄 PDF files (.pdf)
                - 📝 Text files (.txt)
                - 📋 Markdown files (.md)

                ### ✨ What AI StudyMate Can Do

                - Answer questions from your uploaded documents.
                - Explain difficult concepts in simple language.
                - Summarize chapters and notes.
                - Maintain conversation context.
                - Show retrieved document sources.
                - Download chat history.

                ### 💡 Tips

                - Upload relevant study materials first.
                - Ask one topic at a time.
                - Use follow-up questions for deeper explanations.
                - Verify answers using the retrieved context section.
                """)
    
    # =================================================================
    # MAIN AREA - Chat Interface
    # =================================================================
    
    if st.session_state.agent is None:
        
        env_api_key = os.getenv('GEMINI_API_KEY')
        
        if env_api_key:
            
            st.info("🔄 Initializing agent... Please wait or refresh the page.")
        else:
            
            st.info("👈 Please configure and initialize the agent in the sidebar to begin")
            st.markdown("## Ask Questions about your knowledge base once the agent is ready!")
        
    else:
        
        st.header("💬 Ask Me Anything!")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources for assistant messages
                if message["role"] == "assistant" and "sources" in message:
                    if message["sources"]:
                        with st.expander(f"📚 View {len(message['sources'])} Sources"):
                            for i, source in enumerate(message['sources'], 1):
                                similarity = source.get('similarity', 0) * 100
                                
                                st.markdown(f"**Source {i}:** {source['metadata'].get('source', 'Unknown')}")
                                st.caption(f"Relevance: {similarity:.1f}%")
                                st.text(source['text'][:200] + "...")
                                st.markdown("---")
        
        # Chat input
        if prompt := st.chat_input("Ask about your pdf's and document, or anything in the knowledge base..."):
            
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            st.session_state.question_count += 1
            
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
          
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        
                        result = st.session_state.agent.answer(prompt,
                                                               chat_history=st.session_state.messages,
                                                               verbose=False)
                        
                        
                        st.markdown(result['answer'])
                        
                      
                        if result['sources']:
                            with st.expander("🔍 Retrieved Context"):
                                for source in result['sources']:
                                    similarity = source.get('similarity', 0) * 100
                                    
                                    source_name = source['metadata'].get( 'source','Unknown')
                                    st.markdown(f"### 📄 {source_name}")
                                    st.caption(f"Similarity Score : {similarity:.1f}%")
                                    st.code(source['text'][:350] + "...",language=None)
                                    st.markdown("---")
                        else:
                            st.caption("No sources found in knowledge base")
                        
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result['answer'],
                            "sources": result['sources']
                        })
                        
                    except Exception as e:
                        error_message = str(e)
                        
                        # Check if it's a quota error
                        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message or "quota" in error_message.lower():
                            st.error("""
                            ⚠️ **API Quota Exceeded**
                            
                            You've hit the Gemini API free tier limit (15-20 requests per minute).
                            
                            **Solutions:**
                            1. **Wait 60 seconds** and try again
                            2. **Use a different API key** (get one at https://aistudio.google.com/app/apikey)
                            3. **Upgrade your API plan** for higher quotas
                            4. **Restart the app** after changing API key
                            
                            To restart with a new key:
                            - Click "🔄 Reset Knowledge Base" in the sidebar
                            - Enter your new API key
                            - Click "Initialize Agent"
                            """)
                        else:
                            st.error(f"❌ Error: {error_message}")
                        
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "Sorry, I encountered an error. Please try again or check the error message above.",
                            "sources": []
                        })
        
        if st.session_state.messages:
            chat_text = ""

            for msg in st.session_state.messages:
                role = msg["role"]
                content = msg["content"]

                chat_text += (
                      f"{role.upper()}:\n"
                      f"{content}\n\n"
             )

            st.download_button(
                "⬇ Download Chat",
                chat_text,
                file_name="chat_history.txt",
                mime="text/plain"
            )
           
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()


# =================================================================
# RUN THE APP
# =================================================================

if __name__ == "__main__":
    main()