from tools.document_tool import vectorstore

for q in ["expenses above $500", "how are expenses handled", "What are the working hours?", "Who won the cricket world cup?"]:
    print("QUERY:", q)
    for doc, score in vectorstore.similarity_search_with_score(q, k=3):
        print(f"  {score:.4f} | {doc.page_content[:60]!r}")