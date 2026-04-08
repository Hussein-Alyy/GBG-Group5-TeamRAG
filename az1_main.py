import os
import uuid
import tempfile
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from azure.core.credentials import AzureKeyCredential
from pypdf import PdfReader

# =========================
# Load ENV
# =========================
load_dotenv()

def get_env(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing ENV: {name}")
    return value

# ENV
BLOB_CONNECTION_STRING = get_env("BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = get_env("BLOB_CONTAINER_NAME")

SEARCH_ENDPOINT = get_env("SEARCH_ENDPOINT")
SEARCH_KEY = get_env("SEARCH_KEY")
INDEX_NAME = get_env("INDEX_NAME")

AZURE_OPENAI_ENDPOINT = get_env("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = get_env("AZURE_OPENAI_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = get_env("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = get_env("AZURE_OPENAI_API_VERSION")

# =========================
# Clients
# =========================
blob_service = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

openai_client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)

# =========================
# Embedding
# =========================
def get_embeddings(texts):
    response = openai_client.embeddings.create(
        input=texts,
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return [r.embedding for r in response.data]

# =========================
# Read PDF
# =========================
def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# =========================
# Chunking
# =========================
def chunk_text(text, size=800, overlap=100):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return chunks

# =========================
# Create Index
# =========================
def create_index():
    client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
        profiles=[VectorSearchProfile(name="profile", algorithm_configuration_name="hnsw")]
    )

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="chunk", type=SearchFieldDataType.String),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SimpleField(name="url", type=SearchFieldDataType.String),  

        SearchField(
            name="vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,
            vector_search_profile_name="profile"
        )
    ]

    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)

    try:
        client.delete_index(INDEX_NAME)
    except:
        pass

    client.create_index(index)
    print("Index created")

# =========================
# Load PDFs from Blob
# =========================
def load_pdfs_from_blob():
    container = blob_service.get_container_client(BLOB_CONTAINER_NAME)
    blobs = container.list_blobs()

    all_docs = []

    for blob in blobs:
        if blob.name.endswith(".pdf"):
            print(f"Downloading {blob.name}")

            blob_client = container.get_blob_client(blob)
            blob_url = blob_client.url  

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                temp.write(blob_client.download_blob().readall())
                temp_path = temp.name

            text = read_pdf(temp_path)
            chunks = chunk_text(text)
            vectors = get_embeddings(chunks)

            for i, chunk in enumerate(chunks):
                all_docs.append({
                    "id": str(uuid.uuid4()),
                    "chunk": chunk,
                    "title": blob.name,
                    "url": blob_url,  
                    "vector": vectors[i]
                })

    return all_docs

# =========================
# Upload
# =========================
def upload_docs(docs):
    client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    client.upload_documents(docs)
    print(f"Uploaded {len(docs)} docs")

# =========================
# Search
# =========================
def search(query):
    client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    vector = get_embeddings([query])[0]

    vq = VectorizedQuery(
        vector=vector,
        k_nearest_neighbors=5,
        fields="vector"
    )

    results = client.search(
        search_text=query,
        vector_queries=[vq],
        top=5
    )

    for r in results:
        print("\n---")
        print("File:", r["title"])
        print("URL:", r["url"])  # ✅ PRINT URL
        print("Text:", r["chunk"][:200])

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    create_index()

    docs = load_pdfs_from_blob()
    upload_docs(docs)

    while True:
        q = input("\nAsk: ")
        if q == "exit":
            break
        search(q)
