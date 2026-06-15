from fastembed import TextEmbedding


class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.model = TextEmbedding(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [emb.tolist() for emb in self.model.embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        emb_list = list(self.model.embed([text]))
        result: list[float] = emb_list[0].tolist()
        return result
