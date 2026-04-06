<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=30&duration=3000&pause=1000&color=FF6B35&center=true&vCenter=true&width=700&lines=GBG+TeamRAG+%F0%9F%A7%A0;Chat+with+Your+Documents;PDF+%E2%86%92+Intelligent+Answers;Azure+Powered+RAG+Pipeline" alt="Typing SVG" />

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Azure Blob](https://img.shields.io/badge/Azure_Blob_Storage-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Azure Search](https://img.shields.io/badge/Azure_AI_Search-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![HNSW](https://img.shields.io/badge/HNSW-Vector__Index-FF6B35?style=for-the-badge)

<br/>

> Ask questions about your PDF documents in plain language — no manual search required.  
> GBG TeamRAG ingests PDFs from Azure Blob Storage, indexes them with vector search,  
> and retrieves the most relevant chunks to answer any question intelligently.

<br/>

[![MIT License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active_Development-blue?style=flat-square)]()
[![Pipeline](https://img.shields.io/badge/Pipeline-Ingest_%E2%86%92_Embed_%E2%86%92_Search-success?style=flat-square)]()

</div>

---

## 📋 Table of Contents

- [✨ Overview](#-overview)
- [🚀 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [⚙️ Installation](#️-installation)
- [🔧 Configuration](#-configuration)
- [📁 Project Structure](#-project-structure)
- [🛡️ Security](#️-security)
- [👥 Team](#-team)

---

## ✨ Overview

**GBG TeamRAG** is a fully cloud-native **Retrieval-Augmented Generation (RAG)** pipeline that turns your PDF document library into a conversational knowledge base. Powered by **Azure OpenAI Embeddings**, **Azure AI Search (HNSW vector index)**, and **Azure Blob Storage**, it lets users find answers buried inside documents — instantly and intelligently.

We built GBG TeamRAG as part of our **GBG Academy AI training program**, combining enterprise-grade cloud infrastructure with state-of-the-art vector search to deliver a production-ready RAG solution.

---

## 🚀 Features

### 📄 Automated PDF Ingestion
- Connects directly to **Azure Blob Storage** and downloads all PDFs automatically
- Extracts full text using **PyPDF** with multi-page support
- Processes entire document libraries in a single run

### ✂️ Intelligent Chunking
- Splits documents into **800-character chunks** with **100-character overlap**
- Overlap ensures no context is lost at chunk boundaries
- Each chunk is tagged with its source document title for full traceability

### 🔢 Azure OpenAI Embeddings
- Embeds every chunk using **text-embedding-3-small** (1536 dimensions)
- Batch embedding calls for efficient API usage
- Embeddings stored directly in Azure AI Search for zero-latency retrieval

### 🔍 Hybrid Vector Search
- **Azure AI Search** index with **HNSW algorithm** for fast approximate nearest neighbor search
- Combines **keyword search** + **vector search** in a single query (hybrid retrieval)
- Returns the **top 5 most relevant chunks** per query for maximum coverage

### 🏗️ Auto Index Management
- Automatically **creates and recreates** the search index on every pipeline run
- Full schema definition including vector dimensions and search profiles
- Zero manual portal configuration required

### 💬 Interactive Query Loop
- After ingestion, drops into an **interactive terminal loop**
- Ask any question and get the top matching document chunks instantly
- Type `exit` to quit cleanly

---

## 🏗️ Architecture

```
📁 Azure Blob Storage
        │
        │  Download PDFs
        ▼
┌───────────────────────────────────────────────────────┐
│                   GBG TeamRAG Pipeline                │
│                                                       │
│  ┌─────────────────┐     ┌──────────────────────────┐ │
│  │   PDF Reader     │────▶│   Text Chunker           │ │
│  │   (PyPDF)        │     │   800 chars / 100 overlap│ │
│  └─────────────────┘     └──────────────┬───────────┘ │
│                                         │             │
│                          ┌──────────────▼───────────┐ │
│                          │  Azure OpenAI Embeddings  │ │
│                          │  text-embedding-3-small   │ │
│                          │  (1536 dimensions)        │ │
│                          └──────────────┬───────────┘ │
│                                         │             │
│                          ┌──────────────▼───────────┐ │
│                          │  Azure AI Search Index    │ │
│                          │  HNSW Vector Index        │ │
│                          │  + Keyword Search         │ │
│                          └──────────────┬───────────┘ │
└─────────────────────────────────────────│─────────────┘
                                          │
                    ┌─────────────────────┼──────────────────────┐
                    │                     │                      │
                    ▼                     ▼                      ▼
           🔢 Embed Query        🔍 Hybrid Search         📄 Return Top 5
           (same model)          (vector + keyword)        Chunks + Titles
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.10+
- Azure Blob Storage container with PDF files
- Azure AI Search resource
- Azure OpenAI resource with `text-embedding-3-small` deployment

### 1. Clone the repository

```bash
git clone https://github.com/GBG-Group5-DataCopilot/gbg-teamrag.git
cd gbg-teamrag
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

### 4. Run the pipeline

```bash
python az1_main.py
```

The pipeline will:
1. ✅ Create the Azure AI Search index
2. ✅ Download and process all PDFs from Blob Storage
3. ✅ Embed and upload all chunks
4. ✅ Start the interactive query loop

---

## 🔧 Configuration

Create a `.env` file in the project root:

```env
# Azure Blob Storage
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
BLOB_CONTAINER_NAME=your-container-name

# Azure AI Search
SEARCH_ENDPOINT=https://your-resource.search.windows.net
SEARCH_KEY=your-search-key
INDEX_NAME=your-index-name

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

> ⚠️ **Never commit your `.env` file to version control.** Add it to `.gitignore` immediately.

---

## 📁 Project Structure

```
gbg-teamrag/
├── az1_main.py             # Main pipeline: ingest → embed → index → search
├── .env                    # Environment variables (not committed)
├── .env.example            # Template for environment variables
├── requirements.txt        # Python dependencies
└── README.md               # You are here
```

---

## 🛡️ Security

| Layer | Mechanism | Protection |
|-------|-----------|------------|
| **Credential Management** | All secrets loaded from `.env` via `python-dotenv` | No hardcoded credentials |
| **Environment Validation** | `get_env()` raises on missing variables at startup | Fails fast before any API call |
| **Read-Only Search** | Pipeline only reads from Blob, writes only to Search index | No data modification risk |
| **Temp File Cleanup** | PDFs downloaded to `tempfile` — OS-managed cleanup | No sensitive files left on disk |

---

## 👥 Team

**GBG-Group5-TeamRAG** — Built with 🤝 collaboration

| Name |
|------|
| **Hussein Aly Abd El-Bari** |
| **Mina Samy** |
| **Amr Baheeg** |
| **Nada Emad** |
| **Dana Ahmed** |

---

<div align="center">

**Built during the GBG Academy AI Program — Egypt 🇪🇬**

*"We don't just search documents — we understand them."*

<br/>

⭐ If you find this project useful, please give it a star!

</div>
