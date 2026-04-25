"""Hybrid retriever combining BM25 and vector search."""

import logging
from typing import Optional

from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore, QueryBundle

from .bm25_retriever import BM25Retriever

logger = logging.getLogger(__name__)


class HybridRetriever(BaseRetriever):
    """Hybrid retriever combining BM25 (keyword) and vector (semantic) search.

    This retriever combines the strengths of both approaches:
    - BM25: Good for exact keyword matching
    - Vector: Good for semantic similarity

    Results are combined using weighted scores.
    """

    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_retriever: BaseRetriever,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
        similarity_top_k: int = 5,
    ):
        """Initialize hybrid retriever.

        Args:
            bm25_retriever: BM25 retriever instance
            vector_retriever: Vector retriever instance
            bm25_weight: Weight for BM25 scores (default: 0.5)
            vector_weight: Weight for vector scores (default: 0.5)
            similarity_top_k: Number of results to return
        """
        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self._similarity_top_k = similarity_top_k

        # Normalize weights
        total_weight = bm25_weight + vector_weight
        self.bm25_weight = bm25_weight / total_weight
        self.vector_weight = vector_weight / total_weight

        logger.info(
            f"Initialized HybridRetriever with BM25 weight: {self.bm25_weight:.2f}, "
            f"Vector weight: {self.vector_weight:.2f}"
        )

        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        """Retrieve nodes using hybrid search.

        Args:
            query_bundle: Query bundle

        Returns:
            List of nodes with combined scores
        """
        # Get results from both retrievers
        bm25_results = self.bm25_retriever.retrieve(query_bundle)
        vector_results = self.vector_retriever.retrieve(query_bundle)

        logger.info(
            f"BM25 returned {len(bm25_results)} results, "
            f"Vector returned {len(vector_results)} results"
        )

        # Normalize scores to [0, 1] range
        bm25_scores = self._normalize_scores(bm25_results)
        vector_scores = self._normalize_scores(vector_results)

        # Combine scores
        combined_scores: dict[str, tuple[NodeWithScore, float]] = {}

        # Add BM25 results
        for node_with_score, norm_score in zip(bm25_results, bm25_scores):
            node_id = node_with_score.node.node_id
            weighted_score = norm_score * self.bm25_weight
            combined_scores[node_id] = (node_with_score, weighted_score)

        # Add vector results
        for node_with_score, norm_score in zip(vector_results, vector_scores):
            node_id = node_with_score.node.node_id
            weighted_score = norm_score * self.vector_weight

            if node_id in combined_scores:
                # Node appears in both results, add scores
                existing_node, existing_score = combined_scores[node_id]
                combined_scores[node_id] = (existing_node, existing_score + weighted_score)
            else:
                combined_scores[node_id] = (node_with_score, weighted_score)

        # Sort by combined score
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Create final results with combined scores
        final_results = []
        for node_with_score, combined_score in sorted_results[:self._similarity_top_k]:
            final_results.append(
                NodeWithScore(
                    node=node_with_score.node,
                    score=combined_score,
                )
            )

        logger.info(f"Hybrid retrieval returned {len(final_results)} results")

        return final_results

    def _normalize_scores(self, results: list[NodeWithScore]) -> list[float]:
        """Normalize scores to [0, 1] range using min-max normalization.

        Args:
            results: List of NodeWithScore

        Returns:
            List of normalized scores
        """
        if not results:
            return []

        scores = [r.score for r in results if r.score is not None]

        if not scores:
            return [0.0] * len(results)

        min_score = min(scores)
        max_score = max(scores)

        if max_score == min_score:
            # All scores are the same
            return [1.0] * len(results)

        # Min-max normalization
        normalized = [
            (score - min_score) / (max_score - min_score)
            if score is not None else 0.0
            for score in [r.score for r in results]
        ]

        return normalized


def create_hybrid_retriever(
    bm25_retriever: BM25Retriever,
    vector_retriever: BaseRetriever,
    bm25_weight: float = 0.5,
    vector_weight: float = 0.5,
    similarity_top_k: int = 5,
) -> HybridRetriever:
    """Create hybrid retriever.

    Args:
        bm25_retriever: BM25 retriever
        vector_retriever: Vector retriever
        bm25_weight: Weight for BM25 scores
        vector_weight: Weight for vector scores
        similarity_top_k: Number of results

    Returns:
        HybridRetriever instance
    """
    return HybridRetriever(
        bm25_retriever=bm25_retriever,
        vector_retriever=vector_retriever,
        bm25_weight=bm25_weight,
        vector_weight=vector_weight,
        similarity_top_k=similarity_top_k,
    )
