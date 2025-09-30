# Fullstack RAG

📌 **Overview**  
This project is a minimal end-to-end experiment of **Retrieval-Augmented Generation (RAG)**.  
It is built using **FastAPI (backend)** and **React.js (frontend)** to answer user questions based on a small set of medical-related documents.  

⚠️ **Disclaimer**  
This is a **beta version (0.1.0)** and currently only uses a **very limited dataset**.  
It is intended for **educational purposes only** and will be improved in the future.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python), Pinecone (vector database), HuggingFace API (Zephyr-7B model)  
- **Frontend**: React.js  
- **Embedding Model**: `thenlper/gte-small`  
- **Tools**: Poetry (dependency management), python-decouple for `.env` configs  

---

## 📂 Current Workflow

### 1️⃣ Backend
- Converts user input into embeddings using `gte-small`  
- Retrieves relevant context from Pinecone  
- Sends the question + context to HuggingFace Zephyr model  
- Returns the generated answer and retrieved context  

### 2️⃣ Frontend
- Simple React.js form to input questions  
- Displays both the generated answer and retrieved document snippets  
- Basic responsive layout  

---