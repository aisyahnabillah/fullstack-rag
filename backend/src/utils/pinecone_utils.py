import os
from pinecone import Pinecone
from decouple import config
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader


# --- Load ENV vars ---
PINECONE_API_KEY = config("PINECONE_API_KEY")
PINECONE_INDEX = config("PINECONE_INDEX", default="lab-rag-index")
PINECONE_NAMESPACE = config("PINECONE_NAMESPACE", default="ns1")

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# --- Init Pinecone ---
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

# --- Embedding model ---
EMBEDDING_MODEL_NAME = "thenlper/gte-small"
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)


def query_pinecone(vector, top_k=3):
    """Query Pinecone index"""
    try:
        result = index.query(
            namespace=PINECONE_NAMESPACE,
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        matches = [
            {"id": m.id, "score": m.score, "metadata": m.metadata}
            for m in result.matches
        ]
        print(f"[Pinecone] Found {len(matches)} matches")
        return {"matches": matches}
    except Exception as e:
        print(f"[Pinecone] Query error: {str(e)}")
        raise


def upload_website_to_pinecone(url: str):
    """Scrape website, split docs, embed, and upload to Pinecone"""
    print(f"[1/4] Loading website: {url}")
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()
        print(f"[2/4] Loaded {len(docs)} documents")
    except Exception as e:
        return f"❌ Failed to load {url}: {str(e)}"

    if not docs:
        return f"❌ No content found at {url}"

    # 2. Split into chunks
    print(f"[3/4] Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"[3/4] Created {len(chunks)} chunks")

    # 3. Upsert to Pinecone
    print(f"[4/4] Uploading to Pinecone...")
    try:
        PineconeVectorStore.from_documents(
            chunks,
            embeddings,
            index_name=PINECONE_INDEX,
            namespace=PINECONE_NAMESPACE,
        )
        print(f"[✓] Successfully indexed!")
        return f"✅ Indexed {len(chunks)} chunks from {url} into Pinecone (namespace: {PINECONE_NAMESPACE})"
    except Exception as e:
        print(f"[!] Upload error: {str(e)}")
        return f"❌ Failed to index: {str(e)}"

