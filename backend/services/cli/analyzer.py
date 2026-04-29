"""Main Jira analysis orchestrator"""

from pathlib import Path
from typing import Dict, List
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.llms import LLM
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.readers.jira import JiraReader
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.retrievers import QueryFusionRetriever
from tqdm import tqdm
import chromadb

from backend.services.cli.config import load_config
from backend.services.cli.data_loader import DataLoader
from backend.services.cli.index_tracker import IndexTracker
from backend.services.cli.output_formatter import OutputFormatter

class JiraAnalyzer:
    def __init__(self, config_path: Path, use_mock_jira: bool = False):
        self.config = load_config(config_path)
        self.use_mock_jira = use_mock_jira
        self._setup_llm()
        self._setup_storage()
        self.tracker = IndexTracker(Path(self.config.storage.index_cache))
        self.loader = DataLoader(self.config, self.tracker, use_mock_jira=use_mock_jira)
        self.formatter = OutputFormatter(Path(self.config.storage.output))
        self.index = self._load_or_create_index()

        if use_mock_jira:
            from backend.services.cli.mock_jira import MockJiraLoader
            self.mock_jira = MockJiraLoader()

    def _setup_llm(self):
        Settings.llm = OpenAILike(
            api_base=self.config.llm.base_url,
            api_key="dummy",
            model=self.config.llm.model,
            is_chat_model=True,
            timeout=300.0,  # 5 minutes timeout
            request_timeout=300.0
        )

        # Use LM Studio for embeddings too (faster, no download needed)
        try:
            from llama_index.embeddings.openai import OpenAIEmbedding
            Settings.embed_model = OpenAIEmbedding(
                api_base=self.config.llm.base_url,
                api_key="dummy",
                model_name="nomic-embed-text-v1.5",  # LM Studio embedding model
                timeout=60.0
            )
        except Exception as e:
            print(f"Warning: Using HuggingFace embeddings (slower): {e}")
            from llama_index.embeddings.huggingface import HuggingFaceEmbedding
            Settings.embed_model = HuggingFaceEmbedding(
                model_name=self.config.llm.embedding_model
            )

    def _setup_storage(self):
        store_path = Path(self.config.storage.vector_store)
        store_path.mkdir(parents=True, exist_ok=True)

        db = chromadb.PersistentClient(path=str(store_path))
        collection = db.get_or_create_collection("cli_analysis")
        self.vector_store = ChromaVectorStore(chroma_collection=collection)

        # Persist docstore for BM25
        self.docstore_path = store_path / "docstore.json"

    def _load_or_create_index(self) -> VectorStoreIndex:
        from llama_index.core.storage.docstore import SimpleDocumentStore
        from llama_index.core.schema import TextNode

        # Load or create docstore
        if self.docstore_path.exists():
            docstore = SimpleDocumentStore.from_persist_path(str(self.docstore_path))
        else:
            docstore = SimpleDocumentStore()

        # If docstore is empty but vector store has data, rebuild docstore from vector store
        if len(docstore.docs) == 0 and self.vector_store._collection.count() > 0:
            print(f"Rebuilding docstore from {self.vector_store._collection.count()} vectors...")

            # Get all nodes from vector store
            all_data = self.vector_store._collection.get(include=['documents', 'metadatas'])

            # Reconstruct nodes and add to docstore
            for doc_text, metadata in zip(all_data['documents'], all_data['metadatas']):
                node = TextNode(
                    text=doc_text,
                    id_=metadata.get('doc_id', metadata.get('document_id')),
                    metadata={k: v for k, v in metadata.items()
                             if not k.startswith('_node')}
                )
                docstore.add_documents([node])

            # Persist the rebuilt docstore
            docstore.persist(str(self.docstore_path))
            print(f"Docstore rebuilt with {len(docstore.docs)} documents")

        # Create storage context with populated docstore
        storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store,
            docstore=docstore
        )

        # Create index directly (not from_vector_store) to preserve docstore
        # from_vector_store() ignores the passed storage_context and creates a new empty one
        index = VectorStoreIndex(
            nodes=[],
            storage_context=storage_context,
            show_progress=False
        )

        return index

    def _get_retriever(self, top_k: int = None):
        """Get retriever based on config mode"""
        top_k = top_k or self.config.retrieval.similarity_top_k
        mode = self.config.retrieval.mode

        # Check if we have enough documents for BM25
        doc_count = len(self.index.docstore.docs)

        if mode == "vector":
            return VectorIndexRetriever(index=self.index, similarity_top_k=top_k)

        elif mode == "bm25":
            if doc_count < 2:
                print(f"Warning: Only {doc_count} documents in index, falling back to vector retrieval")
                return VectorIndexRetriever(index=self.index, similarity_top_k=top_k)

            return BM25Retriever.from_defaults(
                docstore=self.index.docstore,
                similarity_top_k=top_k
            )

        elif mode == "hybrid":
            if doc_count < 2:
                print(f"Warning: Only {doc_count} documents in index, falling back to vector retrieval")
                return VectorIndexRetriever(index=self.index, similarity_top_k=top_k)

            # Vector retriever
            vector_retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=top_k
            )

            # BM25 retriever
            bm25_retriever = BM25Retriever.from_defaults(
                docstore=self.index.docstore,
                similarity_top_k=top_k
            )

            # Fusion with custom weights
            return QueryFusionRetriever(
                retrievers=[vector_retriever, bm25_retriever],
                similarity_top_k=top_k,
                num_queries=1,
                mode="reciprocal_rerank",
            )

        else:
            raise ValueError(f"Unknown retrieval mode: {mode}")

    def refresh_all(self):
        """Force refresh all data sources"""
        with tqdm(total=4, desc="Refreshing data sources") as pbar:
            pbar.set_description("Loading Jira issues")
            jira_docs = self.loader.load_jira_issues(force_refresh=True)
            pbar.update(1)

            pbar.set_description("Loading Confluence pages")
            conf_docs = self.loader.load_confluence_pages(force_refresh=True)
            pbar.update(1)

            pbar.set_description("Loading local documents")
            local_docs = self.loader.load_documents(force_refresh=True)
            pbar.update(1)

            all_docs = jira_docs + conf_docs + local_docs
            if all_docs:
                pbar.set_description(f"Indexing {len(all_docs)} documents")
                for doc in tqdm(all_docs, desc="Building index", leave=False):
                    self.index.insert(doc)
                # Persist docstore
                self.index.storage_context.docstore.persist(str(self.docstore_path))
            pbar.update(1)

        print(f"Refresh complete: {len(all_docs)} documents indexed")

    def _fetch_jira_detail(self, jira_key: str) -> Dict:
        """Fetch full Jira issue with comments and attachments"""
        if self.use_mock_jira:
            return self.mock_jira.get_issue(jira_key)

        from llama_index.readers.jira import JiraReader
        reader = JiraReader(
            server_url=self.config.jira.server_url,
            email=self.config.jira.email,
            api_token=self.config.jira.token
        )

        docs = reader.load_data(query=f"key = {jira_key}")
        if not docs:
            raise ValueError(f"Issue {jira_key} not found")

        return {
            "key": jira_key,
            "content": docs[0].text,
            "metadata": docs[0].metadata
        }

    def _retrieve_similar_issues(self, issue_text: str, top_k: int = 5) -> List[Dict]:
        """Retrieve similar Jira issues"""
        retriever = self._get_retriever(top_k=top_k)
        nodes = retriever.retrieve(issue_text)

        return [
            {
                "text": node.text,
                "score": node.score,
                "metadata": node.metadata
            }
            for node in nodes
            if node.metadata.get("source", "").startswith("jira") or
               "key" in node.metadata
        ][:top_k]

    def _retrieve_relevant_docs(self, query: str, top_k: int = 10) -> List[Dict]:
        """Retrieve relevant wiki/spec/case documents"""
        retriever = self._get_retriever(top_k=top_k)
        nodes = retriever.retrieve(query)

        return [
            {
                "text": node.text,
                "score": node.score,
                "metadata": node.metadata
            }
            for node in nodes
        ][:top_k]

    def _generate_rca(self, issue: Dict, similar: List[Dict], docs: List[Dict]) -> str:
        """Generate RCA using LLM"""
        context = f"""# Issue: {issue['key']}

## Issue Content
{issue['content']}

## Similar Issues
{self._format_similar(similar)}

## Relevant Documentation
{self._format_docs(docs)}

Based on the above information, provide:
1. Root Cause Analysis
2. Action Items
3. Verification Steps
"""

        response = Settings.llm.complete(context)
        return response.text

    def _format_similar(self, similar: List[Dict]) -> str:
        lines = []
        for i, item in enumerate(similar[:3], 1):
            lines.append(f"### {i}. {item['metadata'].get('key', 'Unknown')}")
            lines.append(item['text'][:500] + "...")
        return "\n\n".join(lines)

    def _format_docs(self, docs: List[Dict]) -> str:
        lines = []
        for i, doc in enumerate(docs[:5], 1):
            source = doc['metadata'].get('source', 'Unknown')
            title = doc['metadata'].get('title', 'Untitled')
            lines.append(f"### {i}. [{source}] {title}")
            lines.append(doc['text'][:500] + "...")
        return "\n\n".join(lines)

    def analyze(self, jira_key: str, output_dir: str = None) -> Dict:
        """Run full analysis pipeline"""
        print(f"\n{'='*60}")
        print(f"Analyzing {jira_key}")
        print(f"Retrieval mode: {self.config.retrieval.mode}")
        if self.config.retrieval.mode == "hybrid":
            print(f"  BM25 weight: {self.config.retrieval.bm25_weight}")
            print(f"  Vector weight: {self.config.retrieval.vector_weight}")
        print(f"{'='*60}\n")

        # Ensure index is up to date
        with tqdm(total=7, desc="Analysis pipeline") as pbar:
            pbar.set_description("Loading new data")
            jira_docs = self.loader.load_jira_issues()
            conf_docs = self.loader.load_confluence_pages()
            local_docs = self.loader.load_documents()

            new_docs = jira_docs + conf_docs + local_docs
            if new_docs:
                for doc in tqdm(new_docs, desc="Indexing new docs", leave=False):
                    self.index.insert(doc)
                # Persist docstore after adding new docs
                self.index.storage_context.docstore.persist(str(self.docstore_path))
            pbar.update(1)

            # Analysis pipeline
            pbar.set_description(f"Fetching {jira_key}")
            issue = self._fetch_jira_detail(jira_key)
            pbar.update(1)

            pbar.set_description("Retrieving similar issues")
            similar = self._retrieve_similar_issues(issue['content'])
            pbar.update(1)

            pbar.set_description("Retrieving relevant docs")
            docs = self._retrieve_relevant_docs(issue['content'])
            pbar.update(1)

            pbar.set_description("Generating RCA")
            rca = self._generate_rca(issue, similar, docs)
            pbar.update(1)

            # Output
            pbar.set_description("Saving results")
            output_path = Path(output_dir) if output_dir else self.formatter.output_dir
            result = self.formatter.save(jira_key, issue, similar, docs, rca, output_path)
            pbar.update(1)

            pbar.set_description("Complete")
            pbar.update(1)

        print(f"\n{'='*60}")
        print(f"Analysis complete")
        print(f"  Similar issues found: {len(similar)}")
        print(f"  Relevant docs found: {len(docs)}")
        print(f"  Markdown: {result['markdown_path']}")
        print(f"  HTML: {result['html_path']}")
        print(f"{'='*60}\n")

        return result
