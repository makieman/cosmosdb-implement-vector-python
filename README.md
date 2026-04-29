# Azure Cosmos DB Vector Search Demo (Python)

![Azure](https://img.shields.io/badge/Azure-Cosmos%20DB-blue)
![Python](https://img.shields.io/badge/Python-3.x-yellow)
![Flask](https://img.shields.io/badge/Flask-App-lightgrey)
![Status](https://img.shields.io/badge/Status-Completed-success)

## Overview
This project demonstrates vector search in Azure Cosmos DB for NoSQL using a simple Flask app. It stores documents with embeddings, runs similarity search, and supports filtered queries by metadata.

## Architecture

```mermaid
flowchart TD
    A[Source data (sample_vectors.json)] --> B[Load into Cosmos DB]
    B --> C[Vector embeddings stored]
    C --> D[Vector similarity search]
    D --> E[Filtered search by metadata]
    E --> F[Flask UI results]
```

## Tech Stack
- Database: Azure Cosmos DB for NoSQL (vector search)
- Backend: Python + Flask
- Auth: Azure Entra ID (DefaultAzureCredential)
- Deployment: Azure CLI / Portal

## Data Model
```json
{
  "id": "chunk-id",
  "documentId": "doc-1",
  "content": "text chunk...",
  "embedding": [0.123, -0.456, ...],
  "metadata": {
    "source": "support-portal",
    "category": "billing",
    "tags": ["refund", "subscription"],
    "chunkIndex": 0
  },
  "createdAt": "2026-04-29T12:34:56.789Z"
}
```

## Project Structure
```
/azdeploy.ps1
/azdeploy.sh
/client
  app.py
  requirements.txt
  sample_vectors.json
  setup_container.py
  vector_functions.py
  /static
  /templates
/rag-backend
  rag_functions.py
```

## Key Components
- `client/vector_functions.py`: vector storage and search helpers.
- `client/setup_container.py`: creates the vector container and policies.
- `client/app.py`: Flask UI to load data and run searches.
- `rag-backend/rag_functions.py`: document chunk storage/retrieval helpers.

## Setup and Run

### 1) Deploy Azure resources
Run the deployment script and follow the menu:

```powershell
powershell -ExecutionPolicy Bypass -File ./azdeploy.ps1
```

Menu flow:
1. Create Cosmos DB account
2. Configure Entra ID access
3. Check deployment status
4. Retrieve connection info (writes .env.ps1)

### 2) Load environment variables (PowerShell)
```powershell
. .\.env.ps1
```

### 3) Run the Flask app
```powershell
cd client
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask run
```

Open: http://127.0.0.1:5000

## Example Usage
- Load sample data from the UI.
- Run a vector similarity search.
- Run a filtered vector search by category.

## Performance Notes
- Chunk-based storage improves retrieval accuracy.
- Idempotent upserts avoid duplicate writes.
- Partition key uses `documentId` for efficient reads.

## License
MIT License

---

## Interview / CV Summary

### Short version
Built a vector-search demo using Azure Cosmos DB for NoSQL and a Flask UI, enabling semantic search over embedded documents with metadata filtering.

### Medium version
Designed and implemented a Python Flask app that stores embedded document chunks in Azure Cosmos DB (vector search), performs similarity search, and supports filtered queries by metadata. Used Entra ID authentication and an idempotent upsert model to keep data consistent.

### Interview-ready version
I built a production-style demo where documents are chunked and stored with embeddings in Azure Cosmos DB for NoSQL. At query time, the app performs vector similarity search to retrieve the most relevant chunks, and it can narrow results with metadata filters. I focused on schema design, partitioning by `documentId`, and idempotent writes so the data model scales cleanly and is easy to maintain.
