import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Manages document chunking, ChromaDB vector indexing, and semantic context retrieval for RAG evaluation."""

    def __init__(self, persist_dir: str = settings.CHROMA_PERSIST_DIRECTORY):
        self.persist_dir = persist_dir
        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
            )
            logger.info(f"Initialized ChromaDB persistent client at {self.persist_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            self.client = None

    def _get_collection_name(self, assignment_id: int) -> str:
        return f"assignment_{assignment_id}_knowledge"

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks using paragraph, sentence and word boundaries."""
        if not text:
            return []
        
        # Split by double newlines (paragraphs) first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            
            if len(current_chunk) + len(p) + 2 <= chunk_size:
                current_chunk = f"{current_chunk}\n\n{p}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # If paragraph itself is longer than chunk_size, split by words
                if len(p) > chunk_size:
                    words = p.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= chunk_size:
                            temp_chunk = f"{temp_chunk} {word}".strip()
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = word
                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = p

        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def index_assignment_documents(
        self,
        assignment_id: int,
        assignment_title: str,
        instructions: str,
        reference_docs: List[Dict[str, str]],
        rubric_guidelines: Optional[str] = None
    ) -> int:
        """Indexes assignment instructions, reference documents, and rubric into ChromaDB."""
        if not self.client:
            logger.warning("ChromaDB client unavailable, skipping indexing.")
            return 0

        collection_name = self._get_collection_name(assignment_id)
        
        try:
            # Recreate collection for fresh indexing
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass

            collection = self.client.create_collection(
                name=collection_name,
                metadata={"assignment_id": assignment_id, "title": assignment_title}
            )

            documents = []
            metadatas = []
            ids = []
            doc_idx = 0

            # 1. Index Instructions
            if instructions:
                inst_chunks = self.chunk_text(instructions)
                for chunk in inst_chunks:
                    doc_idx += 1
                    documents.append(chunk)
                    metadatas.append({"source": "instructions", "title": assignment_title, "doc_idx": doc_idx})
                    ids.append(f"inst_{assignment_id}_{doc_idx}")

            # 2. Index Rubric Guidelines
            if rubric_guidelines:
                rubric_chunks = self.chunk_text(rubric_guidelines)
                for chunk in rubric_chunks:
                    doc_idx += 1
                    documents.append(chunk)
                    metadatas.append({"source": "rubric", "title": "Rubric Standards", "doc_idx": doc_idx})
                    ids.append(f"rubric_{assignment_id}_{doc_idx}")

            # 3. Index Reference Documents
            for ref in reference_docs:
                title = ref.get("title", "Reference Doc")
                content = ref.get("content", "")
                if content:
                    ref_chunks = self.chunk_text(content)
                    for chunk in ref_chunks:
                        doc_idx += 1
                        documents.append(chunk)
                        metadatas.append({"source": "reference_doc", "title": title, "doc_idx": doc_idx})
                        ids.append(f"ref_{assignment_id}_{doc_idx}")

            if documents:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Indexed {len(documents)} chunks for assignment #{assignment_id}")

            return len(documents)

        except Exception as e:
            logger.error(f"Error indexing assignment documents in ChromaDB: {e}")
            return 0

    def query_context(self, assignment_id: int, query: str, n_results: int = 4) -> List[Dict[str, Any]]:
        """Query ChromaDB for relevant knowledge context snippets."""
        if not self.client or not query:
            return []

        collection_name = self._get_collection_name(assignment_id)
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            if count == 0:
                return []

            actual_n = min(n_results, count)
            results = collection.query(
                query_texts=[query],
                n_results=actual_n
            )

            context_items = []
            if results and "documents" in results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                for doc, meta in zip(docs, metas):
                    context_items.append({
                        "content": doc,
                        "source": meta.get("source", "knowledge_base"),
                        "title": meta.get("title", "Document"),
                    })

            return context_items
        except Exception as e:
            logger.warning(f"RAG query failed for assignment #{assignment_id}: {e}")
            return []


rag_service = RAGService()
