"""BM25 retriever for keyword-based full-text search."""

import logging
import math
from collections import Counter
from typing import Any, Optional

from llama_index.core import Document
from llama_index.core.schema import NodeWithScore, QueryBundle, TextNode
from llama_index.core.retrievers import BaseRetriever

logger = logging.getLogger(__name__)


class BM25Retriever(BaseRetriever):
    """BM25 retriever for keyword-based search.

    BM25 (Best Matching 25) is a probabilistic ranking function used for
    full-text search. It's particularly effective for keyword matching.
    """

    def __init__(
        self,
        nodes: list[TextNode],
        k1: float = 1.5,
        b: float = 0.75,
        similarity_top_k: int = 5,
    ):
        """Initialize BM25 retriever.

        Args:
            nodes: List of TextNode objects to search
            k1: Term frequency saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
            similarity_top_k: Number of results to return
        """
        self.nodes = nodes
        self.k1 = k1
        self.b = b
        self._similarity_top_k = similarity_top_k

        # Build index
        self._build_index()

        super().__init__()

    def _build_index(self) -> None:
        """Build BM25 index from nodes."""
        self.doc_freqs: dict[str, int] = {}
        self.doc_lengths: list[int] = []
        self.doc_term_freqs: list[dict[str, int]] = []

        # Calculate document frequencies and term frequencies
        for node in self.nodes:
            text = node.get_content().lower()
            terms = self._tokenize(text)

            # Document length
            self.doc_lengths.append(len(terms))

            # Term frequencies in this document
            term_freq = Counter(terms)
            self.doc_term_freqs.append(term_freq)

            # Document frequencies (how many docs contain each term)
            for term in set(terms):
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        # Calculate average document length
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0
        self.num_docs = len(self.nodes)

        logger.info(f"Built BM25 index with {self.num_docs} documents, avg length: {self.avg_doc_length:.1f}")

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into terms.

        Args:
            text: Input text

        Returns:
            List of terms
        """
        # Simple tokenization (can be improved with proper tokenizer)
        import re

        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        terms = text.split()

        # Remove stop words (basic English stop words)
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with'
        }
        terms = [t for t in terms if t not in stop_words and len(t) > 1]

        return terms

    def _calculate_bm25_score(
        self,
        query_terms: list[str],
        doc_idx: int,
    ) -> float:
        """Calculate BM25 score for a document.

        Args:
            query_terms: Query terms
            doc_idx: Document index

        Returns:
            BM25 score
        """
        score = 0.0
        doc_length = self.doc_lengths[doc_idx]
        term_freqs = self.doc_term_freqs[doc_idx]

        for term in query_terms:
            if term not in term_freqs:
                continue

            # Term frequency in document
            tf = term_freqs[term]

            # Document frequency
            df = self.doc_freqs.get(term, 0)

            # IDF (Inverse Document Frequency)
            idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1.0)

            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)

            score += idf * (numerator / denominator)

        return score

    def _retrieve(self, query_bundle: QueryBundle) -> list[NodeWithScore]:
        """Retrieve nodes using BM25.

        Args:
            query_bundle: Query bundle

        Returns:
            List of nodes with scores
        """
        query_text = query_bundle.query_str.lower()
        query_terms = self._tokenize(query_text)

        if not query_terms:
            logger.warning("No valid query terms after tokenization")
            return []

        # Calculate scores for all documents
        scores = []
        for idx in range(len(self.nodes)):
            score = self._calculate_bm25_score(query_terms, idx)
            if score > 0:
                scores.append((idx, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Get top-k results
        top_k = scores[:self._similarity_top_k]

        # Create NodeWithScore objects
        results = []
        for idx, score in top_k:
            node = self.nodes[idx]
            results.append(NodeWithScore(node=node, score=score))

        logger.info(f"BM25 retrieved {len(results)} results for query: {query_text[:50]}...")

        return results

    def update_nodes(self, nodes: list[TextNode]) -> None:
        """Update the index with new nodes.

        Args:
            nodes: New list of nodes
        """
        self.nodes = nodes
        self._build_index()


def create_bm25_retriever(
    documents: list[Document],
    k1: float = 1.5,
    b: float = 0.75,
    similarity_top_k: int = 5,
) -> BM25Retriever:
    """Create BM25 retriever from documents.

    Args:
        documents: List of LlamaIndex Documents
        k1: BM25 k1 parameter
        b: BM25 b parameter
        similarity_top_k: Number of results to return

    Returns:
        BM25Retriever instance
    """
    # Convert documents to nodes
    nodes = []
    for doc in documents:
        node = TextNode(
            text=doc.text,
            metadata=doc.metadata,
            id_=doc.doc_id,
        )
        nodes.append(node)

    return BM25Retriever(
        nodes=nodes,
        k1=k1,
        b=b,
        similarity_top_k=similarity_top_k,
    )
