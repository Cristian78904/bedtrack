# BedTrack - Arquitectura RAG (Retrieval-Augmented Generation)

## Flujo de Datos

[Documentos Médicos] ? [Chunking] ? [Embeddings] ? [Vector DB (Pinecone)]
                                                        ¦
                                                        ?
[Usuario] ? [Query] ? [Embedding] ? [Búsqueda en Vector DB]
                                        ¦
                                        ?
                              [Contexto Relevante]
                                        ¦
                                        ?
[Prompt + Contexto] ? [LLM (GPT-4)] ? [Respuesta Generada]

## Componentes

1. Ingesta de Datos:
   - Documentos: PDF, TXT, registros médicos
   - Chunking: División en fragmentos de 500-1000 tokens
   - Embeddings: OpenAI text-embedding-ada-002

2. Almacenamiento Vectorial:
   - Base: Pinecone / Milvus
   - Índice: HNSW (Hierarchical Navigable Small World)
   - Dimensión: 1536 (OpenAI embeddings)

3. LLM (Generación):
   - Modelo: GPT-4
   - Contexto: 8K tokens
   - Temperatura: 0.3 (precisión)

4. Orquestación:
   - API: Python FastAPI
   - Cache: Redis (respuestas frecuentes)
   - Async: Timeout 30s, retries 3
