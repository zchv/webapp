import faiss
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import config


class FAISSIndexManager:
    """
    Manages FAISS index for efficient vector similarity search.
    Uses IndexFlatIP for exact inner product search (small-scale <10K images).
    """

    def __init__(self):
        self.index = None
        self.metadata = {
            "image_paths": [],
            "image_ids": [],
            "metadata": {}
        }
        self.dimension = None

    def build_index(self, embeddings: np.ndarray, image_paths: List[str], metadata_list: List[Dict] = None):
        """
        Build FAISS index from embeddings.

        Args:
            embeddings: numpy array of shape (N, D) where N is number of images, D is embedding dimension
            image_paths: List of image file paths
            metadata_list: Optional list of metadata dicts for each image
        """
        assert len(embeddings) == len(image_paths), "Embeddings and paths must have same length"

        self.dimension = embeddings.shape[1]
        print(f"Building FAISS index with {len(embeddings)} vectors of dimension {self.dimension}")

        # Use IndexFlatIP for exact inner product search
        # Since CLIP embeddings are normalized, inner product = cosine similarity
        self.index = faiss.IndexFlatIP(self.dimension)

        # Add vectors to index
        self.index.add(embeddings.astype('float32'))

        # Store metadata
        self.metadata["image_paths"] = image_paths
        self.metadata["image_ids"] = list(range(len(image_paths)))

        if metadata_list:
            for idx, meta in enumerate(metadata_list):
                self.metadata["metadata"][str(idx)] = meta
        else:
            for idx, path in enumerate(image_paths):
                self.metadata["metadata"][str(idx)] = {
                    "filename": Path(path).name,
                    "path": str(path)
                }

        print(f"FAISS index built successfully with {self.index.ntotal} vectors")

    def add_vectors(self, embeddings: np.ndarray, image_paths: List[str], metadata_list: List[Dict] = None):
        """
        Add new vectors to existing index.

        Args:
            embeddings: numpy array of new embeddings
            image_paths: List of new image paths
            metadata_list: Optional metadata for new images
        """
        if self.index is None:
            raise ValueError("Index not initialized. Call build_index first.")

        assert len(embeddings) == len(image_paths), "Embeddings and paths must have same length"

        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))

        # Update metadata
        start_idx = len(self.metadata["image_paths"])
        self.metadata["image_paths"].extend(image_paths)
        self.metadata["image_ids"].extend(range(start_idx, start_idx + len(image_paths)))

        if metadata_list:
            for idx, meta in enumerate(metadata_list):
                self.metadata["metadata"][str(start_idx + idx)] = meta
        else:
            for idx, path in enumerate(image_paths):
                self.metadata["metadata"][str(start_idx + idx)] = {
                    "filename": Path(path).name,
                    "path": str(path)
                }

        print(f"Added {len(embeddings)} vectors. Total: {self.index.ntotal}")

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 20,
        threshold: float = 0.0
    ) -> List[Dict]:
        """
        Search for similar images.

        Args:
            query_vector: Query embedding vector (1D array)
            top_k: Number of top results to return
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of dicts with keys: image_path, score, metadata, image_id
        """
        if self.index is None:
            raise ValueError("Index not initialized. Load or build index first.")

        # Ensure query vector is 2D and float32
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        query_vector = query_vector.astype('float32')

        # Search
        scores, indices = self.index.search(query_vector, top_k)

        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            if score < threshold:
                continue

            results.append({
                "image_id": int(idx),
                "image_path": self.metadata["image_paths"][idx],
                "score": float(score),
                "metadata": self.metadata["metadata"].get(str(idx), {})
            })

        return results

    def save_index(self, index_path: Optional[Path] = None, metadata_path: Optional[Path] = None):
        """
        Save FAISS index and metadata to disk.

        Args:
            index_path: Path to save index file (default: config.FAISS_INDEX_PATH)
            metadata_path: Path to save metadata file (default: config.METADATA_PATH)
        """
        if self.index is None:
            raise ValueError("No index to save")

        index_path = index_path or config.FAISS_INDEX_PATH
        metadata_path = metadata_path or config.METADATA_PATH

        # Save FAISS index
        faiss.write_index(self.index, str(index_path))
        print(f"FAISS index saved to {index_path}")

        # Save metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        print(f"Metadata saved to {metadata_path}")

    def load_index(self, index_path: Optional[Path] = None, metadata_path: Optional[Path] = None):
        """
        Load FAISS index and metadata from disk.

        Args:
            index_path: Path to index file (default: config.FAISS_INDEX_PATH)
            metadata_path: Path to metadata file (default: config.METADATA_PATH)
        """
        index_path = index_path or config.FAISS_INDEX_PATH
        metadata_path = metadata_path or config.METADATA_PATH

        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

        # Load FAISS index
        self.index = faiss.read_index(str(index_path))
        self.dimension = self.index.d
        print(f"FAISS index loaded from {index_path} ({self.index.ntotal} vectors)")

        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        print(f"Metadata loaded from {metadata_path}")

    def get_stats(self) -> Dict:
        """Get index statistics."""
        if self.index is None:
            return {"status": "not_initialized"}

        return {
            "status": "initialized",
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "total_images": len(self.metadata["image_paths"]),
            "index_type": "IndexFlatIP (exact search)"
        }
