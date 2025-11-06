import os
import shutil
import uuid
import time # Optional: Add for debugging, if needed

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from chromadb import Client

# Assuming config.py is correctly set up
from config import GROQ_API_KEY, CHROMA_DIR, COLLECTION_NAME

# --- CRITICAL FIX: REMOVE GLOBAL INITIALIZATION OF EXTERNAL SERVICES ---
# The CohereEmbeddings object must NOT be initialized globally as it can hang startup.
# embedding_function = CohereEmbeddings(model="embed-english-light-v3.0") # REMOVED

client = Client() # Keep the Chroma client here, as it's safe.


def process_pdfs(files):
    # 1. Initialize Embeddings LOCALLY (inside the function)
    embedding_function = CohereEmbeddings(model="embed-english-light-v3.0")

    try:
        # Client interaction is now safe
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    
    # We must explicitly pass the embedding function during creation, as we rely on it now.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function.embed_query 
    )

    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    total_chunks = 0

    for file in files:
        # Save the file temporarily
        path = os.path.join(temp_dir, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Loader for pypdf
        loader = PyPDFLoader(path) 
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        total_chunks += len(chunks)

        for doc in chunks:
            collection.add(
                documents=[doc.page_content],
                metadatas=[doc.metadata],
                ids=[str(uuid.uuid4())],
            )
    
    # Clean up the temporary directory after processing
    shutil.rmtree(temp_dir, ignore_errors=True) 
    return total_chunks


def ask_question(query: str):
    # 1. Instantiate the remote Cohere model LOCALLY
    embeddings = CohereEmbeddings(
        model="embed-english-light-v3.0" 
    )

    vectorstore = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings, # Pass the locally defined embedding function
        # persist_directory=CHROMA_DIR # REMOVED for in-memory client
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    llm = ChatGroq(
        temperature=0.5,
        # API key is read automatically from the GROQ_API_KEY environment variable
        model_name="llama-3.3-70b-versatile"
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa_chain({"query": query}) # Use the updated dictionary format for chain calls

    sources = []
    for doc in result["source_documents"]:
        meta = doc.metadata
        file_name = meta.get("source") or meta.get("file_name") or "Unknown"
        sources.append(file_name)

    return {
        "answer": result["result"],
        "sources": list(set(sources))
    }
