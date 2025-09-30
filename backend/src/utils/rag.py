import asyncio
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_huggingface import HuggingFaceEmbeddings
from decouple import config
from huggingface_hub import InferenceClient
from .pinecone_utils import query_pinecone

# --- Embeddings ---
EMBEDDING_MODEL_NAME = "thenlper/gte-small"
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    multi_process=False,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# --- LLM (Zephyr via Hugging Face API) ---
HUGGINGFACE_API_KEY = config("HUGGINGFACE_API_KEY")
MODEL_NAME = "HuggingFaceH4/zephyr-7b-beta"

print("Connecting to Zephyr via Hugging Face API...")
client = InferenceClient(model=MODEL_NAME, token=HUGGINGFACE_API_KEY)

def generate_with_zephyr(prompt: str):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        temperature=0.3,
    )
    return response.choices[0].message["content"]


print("Model connected!")

# --- Prompt ---
PROMPT_TEMPLATE = """Context:
{context}

Question: {question}

Answer clearly and concisely:
"""

# --- RAG Functions ---
def get_answer_and_docs(question: str):
    print(f"[1/4] Processing question: {question}")
    
    vectorized_input = embedding_model.embed_query(question)
    
    print("[2/4] Querying Pinecone...")
    context = query_pinecone(vectorized_input, top_k=3)
    
    if not context.get("matches") or len(context["matches"]) == 0:
        return {
            "answer": "I don't have any information to answer this question. Please index some documents first.",
            "context": []
        }
    
    retrieved_texts = [match["metadata"]["text"] for match in context["matches"]]
    combined_context = "\n\n".join(retrieved_texts)
    
    print(f"[3/4] Generating answer with Zephyr API...")
    prompt = PROMPT_TEMPLATE.format(context=combined_context, question=question)
    
    try:
        answer = generate_with_zephyr(prompt)
        print("[✓] Answer generated!")
        
        return {
            "answer": answer,
            "context": context["matches"],
        }
    except Exception as e:
        print(f"[!] Error: {str(e)}")
        return {
            "answer": f"Error generating answer: {str(e)}",
            "context": context["matches"],
        }


async def async_get_answer_and_docs(question: str):
    """Async generator"""
    yield {"event_type": "start", "data": "Processing..."}
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, get_answer_and_docs, question)
    
    yield {"event_type": "answer", "data": result["answer"]}
    yield {"event_type": "context", "data": [m["metadata"] for m in result["context"]]}
    yield {"event_type": "done", "data": "Completed"}
