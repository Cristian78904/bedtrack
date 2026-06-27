# BedTrack - Servicio de RAG (Python)

import openai
from pinecone import Pinecone
import asyncio
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Configuración
openai.api_key = "sk-..."
pinecone.init(api_key="pc-...", environment="us-west1-gcp")

# 1. Embedding de texto
def embed_text(text: str) -> list:
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response['data'][0]['embedding']

# 2. Ingesta de documentos
def ingest_document(text: str, metadata: dict):
    # Dividir en chunks
    chunks = split_text(text, chunk_size=500)
    
    # Generar embeddings
    for chunk in chunks:
        embedding = embed_text(chunk)
        # Guardar en Vector DB
        index = pinecone.Index("bedtrack-docs")
        index.upsert([(f"doc_{metadata['id']}_{i}", embedding, metadata)])

# 3. Búsqueda en Vector DB
def search_documents(query: str, top_k: int = 5):
    query_embedding = embed_text(query)
    index = pinecone.Index("bedtrack-docs")
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    return results

# 4. Generación de respuesta
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_response(prompt: str, context: str, timeout: int = 30):
    full_prompt = f"""
    Contexto médico:
    {context}
    
    Pregunta:
    {prompt}
    
    Basándote en el contexto, responde:
    """
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai.api_key}"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                return await response.json()
        except asyncio.TimeoutError:
            return {"error": "Timeout - respuesta manual requerida"}

# 5. Flujo completo RAG
async def ask_medical_question(query: str):
    # Embedding de la pregunta
    query_embedding = embed_text(query)
    
    # Búsqueda en Vector DB
    similar_docs = search_documents(query_embedding)
    
    # Construir contexto
    context = "\n".join([doc['metadata']['text'] for doc in similar_docs])
    
    # Generar respuesta
    response = await generate_response(query, context)
    
    # Cachear respuesta frecuente
    # redis.setex(f"q:{query}", 3600, response)
    
    return response
