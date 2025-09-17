from services.vector_service import build_embeddings, collection

if __name__ == "__main__":
    build_embeddings()
    print("Embeddings berhasil dibuat dan disimpan ke Chroma")

    print("Total film di vector store:", collection.count())
