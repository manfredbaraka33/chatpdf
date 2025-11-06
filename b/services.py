import os, shutil, uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings # ADDED: For free, remote embeddings
from langchain_community.document_loaders import PyMuPDFLoader 
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
# --- CHANGE 2: REMOVE PERSISTENCE ---
from chromadb import Client # CHANGED from PersistentClient

from config import GROQ_API_KEY, CHROMA_DIR, COLLECTION_NAME


# --- REMOVED: embedding_function = HuggingFaceEmbeddings(...) ---
# --- ADDED: Cohere embedding function is defined later, or we can define it globally:
embedding_function = CohereEmbeddings(model="embed-english-light-v3.0") # Reads COHERE_API_KEY env var

# --- CHANGED CLIENT INITIALIZATION ---
client = Client() # CHANGED from PersistentClient(path=CHROMA_DIR)


def process_pdfs(files):
    try:
        # Client interaction is now safe
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    
    # We must explicitly pass the embedding function during creation, as we rely on it now.
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function.embed_query # Use the embedding function here too
    )

    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    total_chunks = 0

    for file in files:
        # ... (File saving logic remains the same) ...
        path = os.path.join(temp_dir, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Loader is unchanged for PyMuPDF
        loader = PyMuPDFLoader(path) 
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
    vectorstore = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        # --- CHANGE 3: REMOVE PERSISTENCE AND USE COHERE EMBEDDINGS ---
        embedding_function=embedding_function, # Pass the Cohere embedding function
        # persist_directory=CHROMA_DIR # REMOVED
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatGroq(
        temperature=0.5,
        # groq_api_key=GROQ_API_KEY, # OPTIONAL: You can remove this line if GROQ_API_KEY is set in environment
        model_name="llama-3.3-70b-versatile"
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa_chain(query)

    sources = []
    for doc in result["source_documents"]:
        meta = doc.metadata
        file_name = meta.get("source") or meta.get("file_name") or "Unknown"
        sources.append(file_name)

    return {
        "answer": result["result"],
        "sources": list(set(sources))
    }
