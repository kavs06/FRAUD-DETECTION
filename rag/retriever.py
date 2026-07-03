class Retriever:
    def __init__(self, vector_store, top_k: int = 5):
        self.retriever = vector_store.as_retriever(search_kwargs={"k": top_k})

    def retrieve(self, query: str) -> str:
        print(f"Retrieving top documents for query: '{query}'")
        docs = self.retriever.invoke(query)
        
        context = ""
        for i, doc in enumerate(docs):
            context += f"--- Document {i+1} ---\n"
            context += doc.page_content + "\n\n"
            
        return context
