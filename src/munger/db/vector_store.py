"""Simple file-based vector store - no ChromaDB (avoids hanging issues)."""

import json
import warnings
from pathlib import Path
from typing import Any
from uuid import UUID

import numpy as np
from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces.*")

from munger.core.config import settings
from munger.core.models import MungerWisdom, WisdomCategory


class WisdomVectorStore:
    """Simple file-based vector store using numpy for similarity search."""

    _model = None  # Class-level cache

    @classmethod
    def _get_model(cls) -> SentenceTransformer:
        """Get or create the embedding model."""
        if cls._model is None:
            cls._model = SentenceTransformer(settings.embedding_model)
        return cls._model

    def __init__(self, persist_directory: str | None = None):
        """Initialize the vector store."""
        if persist_directory is None:
            settings.ensure_data_dir()
            persist_directory = str(settings.data_dir)

        self._data_file = Path(persist_directory) / "wisdom_store.json"
        self._embeddings_file = Path(persist_directory) / "wisdom_embeddings.npy"
        
        self._data: list[dict[str, Any]] = []
        self._embeddings: np.ndarray | None = None
        self._load()

    def _load(self) -> None:
        """Load data from files."""
        if self._data_file.exists():
            with open(self._data_file, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        if self._embeddings_file.exists():
            self._embeddings = np.load(self._embeddings_file)

    def _save(self) -> None:
        """Save data to files."""
        with open(self._data_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        if self._embeddings is not None:
            np.save(self._embeddings_file, self._embeddings)

    def _embed(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for texts."""
        model = self._get_model()
        return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    def add_wisdom(self, wisdom: MungerWisdom) -> None:
        """Add a piece of wisdom to the store."""
        item = {
            "id": str(wisdom.id),
            "category": wisdom.category.value,
            "title": wisdom.title,
            "content": wisdom.content,
            "source": wisdom.source,
            "tags": wisdom.tags,
            "related_models": wisdom.related_models,
            "year": wisdom.year,
        }
        
        embedding = self._embed([wisdom.content])
        
        self._data.append(item)
        if self._embeddings is None:
            self._embeddings = embedding
        else:
            self._embeddings = np.vstack([self._embeddings, embedding])
        
        self._save()

    def add_wisdom_batch(self, wisdom_items: list[MungerWisdom]) -> None:
        """Add multiple pieces of wisdom in batch."""
        if not wisdom_items:
            return

        items = []
        contents = []
        
        for w in wisdom_items:
            items.append({
                "id": str(w.id),
                "category": w.category.value,
                "title": w.title,
                "content": w.content,
                "source": w.source,
                "tags": w.tags,
                "related_models": w.related_models,
                "year": w.year,
            })
            contents.append(w.content)

        embeddings = self._embed(contents)
        
        self._data.extend(items)
        if self._embeddings is None:
            self._embeddings = embeddings
        else:
            self._embeddings = np.vstack([self._embeddings, embeddings])
        
        self._save()

    def search(
        self,
        query: str,
        n_results: int = 5,
        category: WisdomCategory | None = None,
        tags: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Search for relevant wisdom based on semantic similarity."""
        if not self._data or self._embeddings is None:
            return []

        query_embedding = self._embed([query])[0]
        
        # Compute cosine similarities
        norms = np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(query_embedding)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        similarities = np.dot(self._embeddings, query_embedding) / norms
        
        # Get top results
        indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in indices:
            if len(results) >= n_results:
                break
                
            item = self._data[idx]
            
            if category and item["category"] != category.value:
                continue
            
            if tags and not any(t in item["tags"] for t in tags):
                continue
            
            results.append({
                "id": item["id"],
                "content": item["content"],
                "metadata": {
                    "category": item["category"],
                    "title": item["title"],
                    "source": item["source"],
                    "tags": ",".join(item["tags"]),
                    "related_models": ",".join(item["related_models"]),
                },
                "distance": float(1 - similarities[idx]),
            })
        
        return results

    def search_by_mental_model(
        self, model_name: str, n_results: int = 5
    ) -> list[dict[str, Any]]:
        """Search for wisdom related to a specific mental model."""
        results = self.search(model_name, n_results=n_results * 2)
        
        for r in results:
            related = r["metadata"].get("related_models", "").lower()
            r["model_match"] = model_name.lower() in related
        
        results.sort(key=lambda x: (not x.get("model_match", False), x["distance"]))
        return results[:n_results]

    def get_all_categories(self) -> list[str]:
        """Get all unique categories in the store."""
        return list(set(item["category"] for item in self._data))

    def get_count(self) -> int:
        """Get the total number of wisdom items."""
        return len(self._data)

    def delete(self, wisdom_id: UUID | str) -> None:
        """Delete a wisdom item by ID."""
        wisdom_id_str = str(wisdom_id)
        for i, item in enumerate(self._data):
            if item["id"] == wisdom_id_str:
                self._data.pop(i)
                if self._embeddings is not None and len(self._embeddings) > i:
                    self._embeddings = np.delete(self._embeddings, i, axis=0)
                self._save()
                return

    def clear(self) -> None:
        """Clear all wisdom from the store."""
        self._data = []
        self._embeddings = None
        if self._data_file.exists():
            self._data_file.unlink()
        if self._embeddings_file.exists():
            self._embeddings_file.unlink()

    def get_random_wisdom(self) -> dict[str, Any] | None:
        """Get a random piece of wisdom (Daily Wisdom feature)."""
        if not self._data:
            return None
        
        import random
        item = random.choice(self._data)
        
        return {
            "id": item["id"],
            "content": item["content"],
            "metadata": {
                "category": item["category"],
                "title": item["title"],
                "source": item["source"],
                "tags": ",".join(item["tags"]),
                "related_models": ",".join(item["related_models"]),
            },
        }
