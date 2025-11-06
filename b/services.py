import os, shutil, uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_groq import ChatGroq
from chromadb import PersistentClient
from config import GROQ_API_KEY, CHROMA_DIR, COLLECTION_NAME

embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
client = PersistentClient(path=CHROMA_DIR)

def process_pdfs(files):
    try:
        client.delete_collection(COLLECTION_NAME)
    except:
        pass
    collection = client.get_or_create_collection(COLLECTION_NAME)

    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    total_chunks = 0

    for file in files:
        path = os.path.join(temp_dir, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

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

    return total_chunks


def ask_question(query: str):
    vectorstore = Chroma(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_function,
        persist_directory=CHROMA_DIR
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatGroq(
        temperature=0.5,
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    result = qa_chain(query)

    # Extract file names or metadata info
    sources = []
    for doc in result["source_documents"]:
        meta = doc.metadata
        file_name = meta.get("source") or meta.get("file_name") or "Unknown"
        sources.append(file_name)

    return {
        "answer": result["result"],
        "sources": list(set(sources))  # remove duplicates
    }

