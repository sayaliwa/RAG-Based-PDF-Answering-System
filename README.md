📚 AI StudyMate – RAG-Based PDF Answering System



Your personal multi-document learning assistant.
Upload PDFs, text, or Markdown files and ask questions — get accurate, context-aware answers powered by Retrieval-Augmented Generation (RAG).

🚀 Live Demo

Try AI StudyMate now →



✨ Features





Multi-document support – Upload PDF, .txt, and .md files



Semantic search – Finds the most relevant passages using vector embeddings



Conversational memory – Understands follow-up questions



Source attribution – Shows which documents and chunks were used



Student-friendly answers – Clear explanations powered by Gemini 2.5 Flash



Interactive dashboard – Track documents uploaded, questions asked, and knowledge base stats



Chat history download – Export your conversation



🧠 How It Works

Document Upload
      ↓
Text Extraction & Cleaning
      ↓
Intelligent Chunking (sentence-aware)
      ↓
Embeddings (all-MiniLM-L6-v2)
      ↓
ChromaDB Vector Store
      ↓
User Question
      ↓
Semantic Retrieval (Top-K relevant chunks)
      ↓
Gemini 2.5 Flash + Context + Chat History
      ↓
Accurate, Source-Grounded Answer

The system retrieves relevant document content using semantic search and passes it (along with conversation history) to the Gemini API to generate a grounded response.



🛠️ Tech Stack







Component



Technology





Frontend



Streamlit





LLM



Google Gemini 2.5 Flash





Vector Database



ChromaDB





Embeddings



Sentence Transformers (all-MiniLM-L6-v2)





PDF Processing



PyPDF2





Language



Python



📁 Project Structure

RAG-Based-PDF-Answering-System/
├── streamlit_app.py          # Main Streamlit application
├── rag_agent.py              # RAG orchestration logic
├── gemini_wrapper.py         # Gemini API wrapper
├── knowledge_base.py         # ChromaDB + embedding management
├── chunking_utility.py       # Text chunking strategies
├── semantic_similarity.py    # Similarity helpers
├── faq_finder.py             # FAQ-related utilities
├── text_cleaner.py           # Text preprocessing
├── requirements.txt
├── README.md
└── .gitignore



☁️ Deployment

This project is deployed on Streamlit Community Cloud.





Live App: https://rag-based-pdf-answering-system-nr3sxkwikdzpcefryztenu.streamlit.app/



Repository: https://github.com/sayaliwa/RAG-Based-PDF-Answering-System



Main file: streamlit_app.py

The Gemini API key is securely managed via Streamlit Secrets