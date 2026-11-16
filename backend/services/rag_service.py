"""Retrieval-Augmented Generation (RAG) Service for Coal Mine Safety & Statutory Regulations."""

import os
import glob
import re
from typing import List, Dict, Any, Optional
from config import Config
from knowledge_base.retriever import HybridRetriever, SimpleBM25
from database.db import query_db, execute_db

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False


class RAGService:
    """Enterprise RAG Service with Hybrid Retrieval (Dense Vector + BM25) and Extractive Synthesis."""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.persist_dir = getattr(Config, "CHROMA_PERSIST_DIR", "chroma_db")
        os.makedirs(self.persist_dir, exist_ok=True)
        self.collection_name = "coal_mine_safety_kb"

        self.embedding_model = None
        self.chroma_client = None
        self.collection = None

        self.retriever = HybridRetriever(rrf_k=60)
        self.chunks_corpus: List[Dict[str, Any]] = []
        self.bm25_index: Optional[SimpleBM25] = None

        self._init_components()

    def _init_components(self):
        """Initialize ChromaDB and SentenceTransformer embedding model."""
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # Load standard lightweight embedding model
                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"[RAGService] Warning: Could not load SentenceTransformer: {e}")
                self.embedding_model = None

        if HAS_CHROMADB:
            try:
                self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
                self.collection = self.chroma_client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"[RAGService] Warning: Could not initialize ChromaDB: {e}")
                self.chroma_client = None
                self.collection = None

        # Auto-load documents from knowledge_base/documents if corpus is empty
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "documents")
        if os.path.exists(docs_dir):
            for fname in os.listdir(docs_dir):
                fpath = os.path.join(docs_dir, fname)
                if os.path.isfile(fpath) and fname.endswith((".txt", ".md")):
                    try:
                        self.ingest_document(fpath, {"title": fname.replace("_", " ").replace(".txt", "").title()})
                    except Exception as e:
                        print(f"[RAGService] Note loading {fname}: {e}")

    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 120) -> List[str]:
        """Split document text into semantically cohesive overlapping chunks."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_chunk = []
        current_len = 0

        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len > chunk_size and current_chunk:
                chunk_str = "\n\n".join(current_chunk)
                chunks.append(chunk_str)
                # Keep tail for overlap
                overlap_chars = 0
                new_chunk = []
                for p in reversed(current_chunk):
                    if overlap_chars + len(p) <= overlap:
                        new_chunk.insert(0, p)
                        overlap_chars += len(p)
                    else:
                        break
                current_chunk = new_chunk
                current_len = sum(len(p) for p in current_chunk)

            current_chunk.append(para)
            current_len += para_len

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    def ingest_document(self, file_path: str, metadata: Dict[str, Any] = None) -> int:
        """Extract text from file, create chunks, index in vector database & BM25."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")

        metadata = metadata or {}
        filename = os.path.basename(file_path)
        doc_type = metadata.get("document_type", filename.split(".")[-1].lower())
        title = metadata.get("title", filename.replace("_", " ").replace(".txt", "").title())

        # Extract text content
        text_content = ""
        if doc_type in ("txt", "text"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()
        elif doc_type == "pdf":
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                text_content = "\n".join([page.get_text() for page in doc])
            except Exception as e:
                print(f"Error reading PDF {file_path}: {e}")
        elif doc_type in ("docx", "doc"):
            try:
                import docx
                doc = docx.Document(file_path)
                text_content = "\n".join([p.text for p in doc.paragraphs if p.text])
            except Exception as e:
                print(f"Error reading DOCX {file_path}: {e}")

        if not text_content.strip():
            return 0

        # Chunk document
        chunks = self.chunk_text(text_content)
        if not chunks:
            return 0

        doc_chunks = []
        ids = []
        embeddings = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filename}_{i}"
            chunk_meta = {
                "source": filename,
                "title": title,
                "chunk_index": i,
                "document_type": doc_type,
            }
            ids.append(chunk_id)
            metadatas.append(chunk_meta)
            doc_chunks.append(chunk)

            # Keep in in-memory corpus
            corpus_entry = {
                "id": chunk_id,
                "text": chunk,
                "source": filename,
                "title": title,
                "metadata": chunk_meta,
            }
            self.chunks_corpus.append(corpus_entry)

        # Index in ChromaDB if available
        if self.collection is not None:
            if self.embedding_model is not None:
                embeddings = self.embedding_model.encode(doc_chunks).tolist()
                self.collection.upsert(
                    ids=ids,
                    documents=doc_chunks,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
            else:
                self.collection.upsert(
                    ids=ids,
                    documents=doc_chunks,
                    metadatas=metadatas,
                )

        # Rebuild BM25 index with all chunks in corpus
        self._rebuild_bm25()

        # Update or record in database knowledge_documents table
        try:
            doc_rec = query_db("SELECT id FROM knowledge_documents WHERE file_path = ?", (file_path,), one=True)
            if not doc_rec:
                execute_db(
                    """
                    INSERT INTO knowledge_documents (title, source, document_type, file_path, version, is_active)
                    VALUES (?, ?, ?, ?, '1.0', 1)
                    """,
                    (title, filename, doc_type, file_path),
                )
        except Exception:
            pass

        return len(chunks)

    def _rebuild_bm25(self):
        """Rebuild in-memory BM25 index from all ingested chunks."""
        if not self.chunks_corpus:
            self.bm25_index = None
            return
        corpus_texts = [c["text"] for c in self.chunks_corpus]
        self.bm25_index = SimpleBM25(corpus=corpus_texts)

    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector similarity and BM25 ranking."""
        if not self.chunks_corpus:
            return []

        # 1. BM25 Search
        bm25_results = []
        if self.bm25_index is not None:
            scores = self.bm25_index.get_scores(query)
            # Rank indices by score
            indexed_scores = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
            for idx, score in indexed_scores[:top_k * 2]:
                if score > 0.05:
                    item = dict(self.chunks_corpus[idx])
                    item["bm25_score"] = float(score)
                    bm25_results.append(item)

        # 2. Dense Vector Search
        dense_results = []
        if self.collection is not None and self.embedding_model is not None:
            try:
                query_vec = self.embedding_model.encode([query]).tolist()[0]
                res = self.collection.query(
                    query_embeddings=[query_vec],
                    n_results=min(top_k * 2, len(self.chunks_corpus))
                )
                if res and res.get("ids") and res["ids"][0]:
                    for i, cid in enumerate(res["ids"][0]):
                        doc_text = res["documents"][0][i] if res.get("documents") else ""
                        meta = res["metadatas"][0][i] if res.get("metadatas") else {}
                        dense_results.append({
                            "id": cid,
                            "text": doc_text,
                            "source": meta.get("source", ""),
                            "title": meta.get("title", ""),
                            "metadata": meta,
                        })
            except Exception as e:
                print(f"[RAGService] Vector search error: {e}")

        # If both are available, fuse with RRF; otherwise fallback to whichever is populated
        if dense_results and bm25_results:
            return self.retriever.reciprocal_rank_fusion(dense_results, bm25_results, top_k=top_k)
        elif dense_results:
            return dense_results[:top_k]
        elif bm25_results:
            return bm25_results[:top_k]

        return []

    def _handle_conversational_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Comprehensive conversational intent handler for natural human interaction.

        Handles greetings, farewells, identity, capabilities, gratitude, small-talk,
        well-being questions, humor requests, time/date queries, and more.
        Returns None only when the query is NOT a recognized conversational pattern,
        allowing the caller to proceed with RAG retrieval or off-topic refusal.
        """
        q = re.sub(r"[^\w\s]", "", query.lower()).strip()
        tokens = set(q.split())
        q_words = q.split()
        n_words = len(q_words)

        # Helper: build a response dict
        def _conv(answer: str) -> Dict[str, Any]:
            return {
                "answer": answer,
                "sources": [],
                "confidence": 0.99,
                "has_sufficient_evidence": True,
                "is_conversational": True,
            }

        # ------------------------------------------------------------------ #
        #  1. GREETINGS  (hi, hello, hey, howdy, good morning, sup, yo, etc.)
        # ------------------------------------------------------------------ #
        greeting_words = {
            "hi", "hello", "hey", "howdy", "hola", "greetings", "yo", "sup",
            "heya", "hiya", "namaste", "namaskar", "salaam", "ola",
        }
        greeting_phrases = [
            "good morning", "good afternoon", "good evening", "good day",
            "good night", "whats up", "wassup", "how do you do",
            "long time no see", "nice to meet you",
        ]
        if (tokens & greeting_words and n_words <= 6) or any(p in q for p in greeting_phrases):
            return _conv(
                "Hello! Welcome to the Coal Mine Safety & Statutory Compliance Assistant.\n\n"
                "I am here to help you with anything related to coal mine safety, DGMS regulations, "
                "hazard management, inspection protocols, and statutory compliance under CMR 2017.\n\n"
                "How can I assist you today? You can ask me about gas concentration limits, "
                "roof support standards, emergency procedures, or any other mining safety topic."
            )

        # ------------------------------------------------------------------ #
        #  2. WELL-BEING / HOW ARE YOU
        # ------------------------------------------------------------------ #
        wellbeing_phrases = [
            "how are you", "hows it going", "how are things", "how do you feel",
            "hows your day", "how have you been", "are you okay", "are you fine",
            "are you good", "are you well", "you doing okay", "you alright",
            "hows everything", "whats new", "how is life", "hows life",
            "are you there", "you okay", "feeling good",
        ]
        if any(p in q for p in wellbeing_phrases):
            return _conv(
                "Thank you for asking! I am functioning optimally and ready to assist you.\n\n"
                "As your Coal Mine Safety Assistant, I am always here to help with safety regulations, "
                "hazard assessments, compliance queries, and DGMS guidelines. What mining safety "
                "question can I help you with?"
            )

        # ------------------------------------------------------------------ #
        #  3. IDENTITY / WHO ARE YOU / WHAT IS THIS SYSTEM
        # ------------------------------------------------------------------ #
        identity_phrases = [
            "who are you", "what are you", "what is this", "your name",
            "tell me about yourself", "introduce yourself", "what is your name",
            "whats your name", "who made you", "who created you", "who built you",
            "who developed you", "what do you do", "what is your purpose",
            "what is your role", "what system is this", "about this app",
            "about this system", "about this platform", "what is this app",
            "tell me about this system", "what is your job",
            "what are you for", "why do you exist", "what is this tool",
            "describe yourself", "who is this", "what is this assistant",
        ]
        if any(p in q for p in identity_phrases):
            return _conv(
                "I am the AI-powered Safety and Statutory Governance Assistant, developed as part of "
                "the Smart Innovation Hackathon project (SIH26024) for Indian Coal Mines.\n\n"
                "My core capabilities include:\n"
                "• Answering questions grounded in Coal Mines Regulations (CMR 2017) and DGMS safety circulars\n"
                "• Real-time hazard classification and risk severity prediction using machine learning\n"
                "• Monitoring statutory compliance across inspections, ventilation, and certifications\n"
                "• Providing regulatory citations and safety procedure references\n\n"
                "I assist mine managers, safety officers, and DGMS inspectors in maintaining the highest "
                "safety standards. Note: I am a decision-support system and do not replace statutory examinations "
                "or human safety judgment."
            )

        # ------------------------------------------------------------------ #
        #  4. CAPABILITIES / HELP / GUIDE
        # ------------------------------------------------------------------ #
        help_phrases = [
            "what can you do", "help me", "how can you help", "how to use",
            "what are your features", "show me features", "capabilities",
            "what do you know", "what topics", "can you help", "guide me",
            "i need help", "assist me", "what should i ask", "what to ask",
            "give me a tour", "how does this work", "how this works",
            "what questions can i ask", "what can i ask", "show me",
            "teach me", "explain features", "list features", "your abilities",
            "what are you capable of", "help", "menu", "options",
            "what services", "how do i use this",
        ]
        if any(p in q for p in help_phrases) or (q == "help"):
            return _conv(
                "Here is how I can assist your colliery operations:\n\n"
                "1. **Statutory Regulations**: Ask about permissible gas concentrations (CH4, CO, CO2), "
                "ventilation air velocities, escape routes, or emergency action plans under CMR 2017.\n\n"
                "2. **Strata & Ground Control**: Query standards for roof bolting, convergence monitoring, "
                "hydraulic props, pillars, or opencast bench slope angles.\n\n"
                "3. **Equipment & Inspections**: Check statutory overhaul frequencies, FLP electrical equipment "
                "standards, and mandatory inspection schedules.\n\n"
                "4. **Hazard Management**: Learn about hazard classification, risk assessment methodologies, "
                "and DGMS technical circulars for specific hazard types.\n\n"
                "5. **AI Risk Assessment**: Use the AI Safety Model page to classify physical observations "
                "into hazard categories with severity predictions.\n\n"
                "6. **Compliance Monitoring**: Check compliance status of your mine against statutory rules.\n\n"
                "Try asking:\n"
                "• 'What are the methane limits in return airways?'\n"
                "• 'What is the opencast bench slope limit?'\n"
                "• 'What are the ventilation requirements for underground mines?'\n"
                "• 'Explain emergency evacuation procedures'"
            )

        # ------------------------------------------------------------------ #
        #  5. GRATITUDE / AFFIRMATION / POSITIVE FEEDBACK
        # ------------------------------------------------------------------ #
        gratitude_words = {
            "thanks", "thank", "thx", "thankyou", "thanku", "thnx", "thnks",
            "appreciate", "appreciated", "grateful", "ty",
        }
        affirm_words = {
            "awesome", "great", "perfect", "wonderful", "excellent", "fantastic",
            "amazing", "brilliant", "superb", "nice", "cool", "good", "fine",
            "neat", "lovely", "beautiful", "impressive", "outstanding", "splendid",
        }
        acknowledge_words = {
            "ok", "okay", "understood", "clear", "got", "noted", "alright",
            "right", "sure", "yep", "yup", "yeah", "yes", "correct",
            "absolutely", "indeed", "certainly", "roger", "copy",
        }
        if (tokens & gratitude_words) and n_words <= 8:
            return _conv(
                "You're welcome! Safety is the paramount objective in all colliery operations. "
                "If you have any more questions about mining regulations, hazard management, "
                "or compliance requirements, feel free to ask anytime."
            )
        if (tokens & affirm_words) and n_words <= 5:
            return _conv(
                "Glad I could help! If you need further assistance with statutory citations, "
                "hazard assessments, or any mining safety topic, I am right here."
            )
        if (tokens & acknowledge_words) and n_words <= 3:
            return _conv(
                "Understood! Let me know if you have any other questions about coal mine safety, "
                "compliance, or regulatory standards."
            )

        # ------------------------------------------------------------------ #
        #  6. FAREWELLS
        # ------------------------------------------------------------------ #
        farewell_words = {
            "bye", "goodbye", "cya", "later", "farewell", "adios", "cheerio",
            "peace", "cheers",
        }
        farewell_phrases = [
            "see you", "take care", "good night", "goodnight", "gotta go",
            "have a good day", "have a nice day", "talk later", "catch you later",
            "signing off", "logging off", "see ya", "im leaving", "i am leaving",
        ]
        if (tokens & farewell_words and n_words <= 5) or any(p in q for p in farewell_phrases):
            return _conv(
                "Goodbye! Stay safe and ensure all statutory shift handover registers are completed "
                "per CMR 2017. Remember, safety first in every mining operation. See you next time!"
            )

        # ------------------------------------------------------------------ #
        #  7. SMALL TALK / COMMON HUMAN CONVERSATION
        # ------------------------------------------------------------------ #
        # Age / Personal questions
        personal_phrases = [
            "how old are you", "your age", "when were you born", "your birthday",
            "where are you from", "where do you live", "are you human",
            "are you a robot", "are you a bot", "are you real", "are you ai",
            "are you artificial", "are you machine", "are you alive",
            "do you have feelings", "do you have emotions", "can you think",
            "can you feel", "are you intelligent", "are you smart",
            "do you sleep", "do you eat", "do you dream", "are you conscious",
        ]
        if any(p in q for p in personal_phrases):
            return _conv(
                "That is a great question! I am an AI-powered assistant, so I do not have a physical "
                "form, age, or personal experiences. I was designed specifically for coal mine safety "
                "and statutory compliance support.\n\n"
                "While I may not have feelings, I am very dedicated to helping keep mining operations "
                "safe! Is there a mining safety or compliance question I can help you with?"
            )

        # Jokes / Fun
        joke_phrases = [
            "tell me a joke", "say something funny", "make me laugh",
            "know any jokes", "got a joke", "humor me", "be funny",
            "tell a joke", "joke", "funny",
        ]
        if any(p in q for p in joke_phrases) and n_words <= 8:
            return _conv(
                "Here is a mining-themed one for you:\n\n"
                "Why did the miner bring a ladder to work? Because he wanted to reach new heights "
                "in safety compliance!\n\n"
                "But seriously, safety is no laughing matter underground. Can I help you with any "
                "mining safety regulations or hazard assessments?"
            )

        # Time / Date questions
        time_phrases = [
            "what time is it", "what is the time", "current time", "todays date",
            "what day is it", "what is the date",
        ]
        if any(p in q for p in time_phrases):
            return _conv(
                "I do not have access to a real-time clock, but you can check the time on your device. "
                "However, speaking of time — are your statutory inspection schedules up to date? "
                "I can help you verify compliance timelines and overdue inspection deadlines."
            )

        # Preferences / Favorites
        preference_phrases = [
            "whats your favorite", "what is your favorite", "do you like",
            "do you prefer", "whats your favourite", "what do you like",
            "your hobby", "your hobbies", "what do you enjoy",
        ]
        if any(p in q for p in preference_phrases):
            return _conv(
                "As an AI assistant focused on coal mine safety, my favorite thing is helping ensure "
                "that mining operations run safely and in full statutory compliance!\n\n"
                "If I had to pick a favorite regulation, it would be the ventilation standards under "
                "CMR 2017 — proper airflow saves lives underground. Would you like to know more about "
                "ventilation requirements?"
            )

        # Compliments
        compliment_phrases = [
            "you are smart", "you are good", "you are helpful", "youre great",
            "youre awesome", "good job", "well done", "nice work",
            "you are the best", "youre the best", "i like you", "love you",
            "you rock", "bravo", "kudos", "impressive work",
        ]
        if any(p in q for p in compliment_phrases):
            return _conv(
                "Thank you for the kind words! I strive to provide accurate and helpful information "
                "about coal mine safety and statutory compliance.\n\n"
                "Your safety is my priority. Is there anything else I can help you with regarding "
                "mining regulations or hazard management?"
            )

        # Apologies
        apology_phrases = [
            "sorry", "my bad", "apologies", "i apologize", "forgive me",
            "pardon", "excuse me", "oops",
        ]
        if any(p in q for p in apology_phrases) and n_words <= 6:
            return _conv(
                "No need to apologize! I am here to help. Feel free to ask any question about "
                "coal mine safety, DGMS regulations, or statutory compliance. No question is too "
                "basic or too detailed."
            )

        # Agreement to suggestions
        agree_phrases = [
            "sounds good", "that works", "go ahead", "proceed", "continue",
            "lets do it", "lets go", "do it", "carry on",
        ]
        if any(p in q for p in agree_phrases):
            return _conv(
                "Great! What specific mining safety or compliance topic would you like to explore? "
                "I can help with hazard classifications, regulatory requirements, inspection standards, "
                "or equipment safety protocols."
            )

        # Confusion / Clarification
        confusion_phrases = [
            "i dont understand", "i am confused", "im confused", "what do you mean",
            "can you explain", "explain again", "say that again", "repeat",
            "come again", "not clear", "unclear", "elaborate", "more details",
        ]
        if any(p in q for p in confusion_phrases):
            return _conv(
                "I am sorry for any confusion! Let me help clarify.\n\n"
                "I am your Coal Mine Safety Assistant. You can ask me questions like:\n"
                "• 'What are the permissible methane levels underground?'\n"
                "• 'What is the minimum ventilation airflow requirement?'\n"
                "• 'Explain the emergency evacuation procedure'\n"
                "• 'What equipment inspections are mandatory?'\n\n"
                "Please rephrase your question or try one of the examples above, and I will do my best "
                "to provide a clear, regulation-backed answer."
            )

        # Boredom / Idle chat
        boredom_phrases = [
            "im bored", "i am bored", "nothing to do", "entertain me",
            "lets chat", "lets talk", "talk to me", "chat with me",
            "can we talk", "just chatting", "random", "anything",
        ]
        if any(p in q for p in boredom_phrases):
            return _conv(
                "I am always happy to chat about coal mine safety! Here are some interesting topics "
                "we could explore:\n\n"
                "• The latest DGMS safety circular requirements\n"
                "• How AI and machine learning are improving mine safety\n"
                "• Common hazard patterns in Indian collieries\n"
                "• Best practices for underground ventilation design\n\n"
                "Pick a topic, or ask me any mining safety question!"
            )

        # Not conversational — return None so the caller can try RAG or refuse
        return None

    def _is_mining_related(self, query: str) -> bool:
        """Check if a query contains mining, safety, or compliance-related keywords."""
        q = query.lower()
        mining_keywords = [
            "mine", "mining", "coal", "colliery", "underground", "opencast",
            "shaft", "tunnel", "drift", "seam", "pillar", "strata", "roof",
            "ventilation", "methane", "gas", "dust", "explosion", "fire",
            "safety", "hazard", "risk", "danger", "accident", "incident",
            "fatality", "injury", "rescue", "emergency", "evacuation",
            "inspection", "audit", "compliance", "regulation", "statutory",
            "dgms", "cmr", "mines act", "overman", "surveyor", "foreman",
            "blasting", "detonator", "explosive", "drilling", "excavation",
            "conveyor", "winder", "hoist", "pump", "compressor", "fan",
            "electrical", "flameproof", "intrinsic", "earth", "leakage",
            "subsidence", "inundation", "flooding", "slope", "bench",
            "environment", "emission", "pollution", "reclamation",
            "worker", "training", "certification", "permit", "license",
            "first aid", "medical", "occupational", "health",
            "ppe", "helmet", "lamp", "detector", "sensor", "alarm",
            "shift", "handover", "register", "report", "log", "record",
        ]
        return any(kw in q for kw in mining_keywords)

    def generate_answer(self, query: str) -> Dict[str, Any]:
        """Generate structured response based on retrieved regulatory passages.

        Logic flow:
        1. Check conversational intents (greetings, identity, help, thanks, farewell, small-talk)
        2. Run RAG retrieval — if good sources found, return statutory answer with citations
        3. If RAG returns 0 sources or very low relevance AND query is not mining-related,
           return polite off-topic refusal
        4. If RAG returns 0 sources but query IS mining-related, return disclaimer
        """
        # Step 1: Check conversational intents first
        conv_res = self._handle_conversational_query(query)
        if conv_res:
            return conv_res

        # Step 2: Check if the query is mining-related BEFORE RAG retrieval
        is_mining = self._is_mining_related(query)

        # Step 3: If the query is NOT mining-related, return off-topic refusal immediately
        # (BM25 can return false-positive low-relevance matches for any query)
        if not is_mining:
            return {
                "answer": (
                    "I appreciate your question, but as a specialized Coal Mine Safety & Statutory "
                    "Compliance Assistant, I can only answer queries related to:\n\n"
                    "• Mining operations and procedures\n"
                    "• Safety regulations and hazard management\n"
                    "• DGMS statutory compliance and circulars\n"
                    "• Coal Mines Regulations (CMR) 2017\n"
                    "• Equipment safety and inspection standards\n"
                    "• Worker training and certification requirements\n\n"
                    "Please ask a question within these domains, or type 'help' to see what I can "
                    "assist you with."
                ),
                "sources": [],
                "confidence": 0.0,
                "has_sufficient_evidence": False,
                "is_off_topic": True,
            }

        # Step 4: Run RAG retrieval for mining-related queries
        retrieved = self.hybrid_search(query, top_k=4)

        # Step 5: If no passages retrieved for a mining-related query
        if not retrieved:
            return {
                "answer": (
                    "Your question appears to be related to mining operations, but I could not find "
                    "specific information in my current knowledge base to answer it definitively.\n\n"
                    "I recommend consulting:\n"
                    "• The Coal Mines Regulations (CMR) 2017 — full statutory text\n"
                    "• Relevant DGMS Technical Circulars and Safety Directives\n"
                    "• Your designated Mine Safety Officer or DGMS Inspector\n\n"
                    "You can also upload additional regulatory documents through the Knowledge Base "
                    "management section to expand my reference library."
                ),
                "sources": [],
                "confidence": 0.0,
                "has_sufficient_evidence": False,
            }

        # Format context and sources
        sources = []
        passages_text = []
        for r in retrieved:
            src_name = r.get("source") or r.get("title", "Safety Document")
            clean_chunk = r.get("text", "").strip()
            passages_text.append(f"--- [Source: {src_name}] ---\n{clean_chunk}")
            sources.append({
                "source": src_name,
                "title": r.get("title", src_name),
                "rrf_score": r.get("rrf_score", 0.0),
                "snippet": clean_chunk[:200] + "..." if len(clean_chunk) > 200 else clean_chunk,
            })

        # Generate structured synthesis
        # Extract direct rule references or pertinent answers
        key_matches = []
        for p in retrieved:
            txt = p.get("text", "")
            lines = [l.strip() for l in txt.split("\n") if l.strip()]
            for line in lines:
                if any(w in line.lower() for w in ["regulation", "limit", "must", "shall", "maximum", "minimum", "prohibited", "standard", "threshold"]):
                    key_matches.append(line)

        summary_points = "\n".join([f"• {m}" for m in key_matches[:5]]) if key_matches else "\n".join([f"• {r['text'][:150]}..." for r in retrieved[:3]])

        response_body = (
            f"Based on the official Directorate General of Mines Safety (DGMS) guidelines and Coal Mines Regulations 2017:\n\n"
            f"{summary_points}\n\n"
            f"Detailed Context:\n"
            f"{retrieved[0]['text'][:450]}...\n\n"
            f"Note: Adherence to statutory DGMS procedures is mandatory under Section 22 of the Mines Act 1952."
        )

        return {
            "answer": response_body,
            "sources": sources,
            "confidence": 0.88,
            "has_sufficient_evidence": True,
        }
