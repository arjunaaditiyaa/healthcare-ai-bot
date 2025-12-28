from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

def retrieve_medical_context(query):
    db = Chroma(
        persist_directory="medical_vectors",
        embedding_function=OllamaEmbeddings(
            model="nomic-embed-text"
        )
    )
    docs = db.similarity_search(query, k=4)
    return "\n".join(d.page_content for d in docs)
