from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

loader=PyPDFLoader("data/Policy_Handbook.pdf")

docs=loader.load()

splitter=RecursiveCharacterTextSplitter(chunk_size=600,chunk_overlap=100)
chunks=splitter.split_documents(docs)
embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore=FAISS.from_documents(chunks,embedding)

@tool
def document_search(query: str) -> str:
    """..."""
    results = vectorstore.similarity_search_with_score(query, k=5)
    
    THRESHOLD = 1.5  
    
    relevant = [doc for doc, score in results if score < THRESHOLD]
    
    if not relevant:
        return "No relevant information found in the document."
    
    return "\n\n".join([doc.page_content for doc in relevant])