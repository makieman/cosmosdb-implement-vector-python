"""
Vector search functions for storing and retrieving documents with embeddings from Cosmos DB.
These functions serve as the interface between the Flask app and Cosmos DB vector search.
"""
import os
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential


def get_container():
    """Get a reference to the Cosmos DB container using Entra ID authentication."""
    endpoint = os.environ.get("COSMOS_ENDPOINT")
    database_name = os.environ.get("COSMOS_DATABASE")
    container_name = os.environ.get("COSMOS_CONTAINER")

    if not endpoint or not database_name or not container_name:
        raise ValueError(
            "COSMOS_ENDPOINT, COSMOS_DATABASE, and COSMOS_CONTAINER "
            "environment variables must be set"
        )

    credential = DefaultAzureCredential()
    client = CosmosClient(endpoint, credential=credential)
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    return container


# BEGIN STORE VECTOR DOCUMENT FUNCTION

def store_vector_document(
    document_id: str,
    chunk_id: str,
    content: str,
    embedding: list,
    metadata: dict = None
) -> dict:
    """Store a document chunk with its vector embedding."""
    container = get_container()

    chunk = {
        "id": chunk_id,
        "documentId": document_id,
        "content": content,
        "metadata": metadata or {},
        "embedding": embedding,
        "createdAt": datetime.utcnow().isoformat(),
        "chunkIndex": metadata.get("chunkIndex", 0) if metadata else 0
    }

    response = container.upsert_item(body=chunk)
    ru_charge = response.get_response_headers()["x-ms-request-charge"]

    return {
        "chunk_id": chunk_id,
        "document_id": document_id,
        "ru_charge": float(ru_charge)
    }

# END STORE VECTOR DOCUMENT FUNCTION


# BEGIN VECTOR SIMILARITY SEARCH FUNCTION

def vector_similarity_search(embedding: list, top_n: int = 5) -> list:
    """Find the most similar chunks by vector distance."""
    container = get_container()

    query = """
        SELECT TOP @topN
            c.id,
            c.documentId,
            c.content,
            c.metadata,
            c.chunkIndex,
            c.createdAt,
            VectorDistance(c.embedding, @embedding) AS similarityScore
        FROM c
        ORDER BY VectorDistance(c.embedding, @embedding)
    """

    items = container.query_items(
        query=query,
        parameters=[
            {"name": "@topN", "value": top_n},
            {"name": "@embedding", "value": embedding}
        ],
        enable_cross_partition_query=True
    )

    return [
        {
            "chunk_id": item["id"],
            "document_id": item["documentId"],
            "content": item["content"],
            "metadata": item["metadata"],
            "chunk_index": item["chunkIndex"],
            "created_at": item["createdAt"],
            "score": item["similarityScore"]
        }
        for item in items
    ]

# END VECTOR SIMILARITY SEARCH FUNCTION


# BEGIN FILTERED VECTOR SEARCH FUNCTION

def filtered_vector_search(
    embedding: list,
    category: str = None,
    top_n: int = 5
) -> list:
    """Find similar chunks, optionally filtered by category."""
    container = get_container()

    if category:
        query = """
            SELECT TOP @topN
                c.id,
                c.documentId,
                c.content,
                c.metadata,
                c.chunkIndex,
                c.createdAt,
                VectorDistance(c.embedding, @embedding) AS similarityScore
            FROM c
            WHERE c.metadata.category = @category
            ORDER BY VectorDistance(c.embedding, @embedding)
        """
        parameters = [
            {"name": "@topN", "value": top_n},
            {"name": "@embedding", "value": embedding},
            {"name": "@category", "value": category}
        ]
    else:
        query = """
            SELECT TOP @topN
                c.id,
                c.documentId,
                c.content,
                c.metadata,
                c.chunkIndex,
                c.createdAt,
                VectorDistance(c.embedding, @embedding) AS similarityScore
            FROM c
            ORDER BY VectorDistance(c.embedding, @embedding)
        """
        parameters = [
            {"name": "@topN", "value": top_n},
            {"name": "@embedding", "value": embedding}
        ]

    items = container.query_items(
        query=query,
        parameters=parameters,
        enable_cross_partition_query=True
    )

    return [
        {
            "chunk_id": item["id"],
            "document_id": item["documentId"],
            "content": item["content"],
            "metadata": item["metadata"],
            "chunk_index": item["chunkIndex"],
            "created_at": item["createdAt"],
            "score": item["similarityScore"]
        }
        for item in items
    ]

# END FILTERED VECTOR SEARCH FUNCTION


def get_all_categories() -> list:
    """Get a list of unique categories from the container."""
    try:
        container = get_container()
        query = "SELECT DISTINCT c.metadata.category FROM c WHERE IS_DEFINED(c.metadata.category)"
        items = container.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        return sorted([item["category"] for item in items if item.get("category")])
    except Exception:
        return []


def get_all_document_ids() -> list:
    """Get a list of unique document IDs from the container."""
    try:
        container = get_container()
        query = "SELECT DISTINCT c.documentId FROM c"
        items = container.query_items(
            query=query,
            enable_cross_partition_query=True
        )
        return sorted([item["documentId"] for item in items])
    except Exception:
        return []
