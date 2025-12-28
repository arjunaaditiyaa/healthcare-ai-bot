from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

def ingest_pdf(path):
    docs = PyPDFLoader(path).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)

    db = Chroma(
        persist_directory="medical_vectors",
        embedding_function=OllamaEmbeddings(
            model="nomic-embed-text"
        )
    )
    db.add_documents(chunks)
    db.persist()
