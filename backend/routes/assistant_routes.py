"""AI Regulatory Assistant routes for DGMS compliance Q&A and knowledge base management."""

import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from database.db import query_db, execute_db
from services.rag_service import RAGService
from services.auth_service import role_required, jwt_required, get_jwt_identity
from services.audit_service import log_action

assistant_bp = Blueprint("assistant", __name__, url_prefix="/api/assistant")


@assistant_bp.route("/ask", methods=["POST"])
@jwt_required()
def ask_assistant():
    """Answer regulatory questions using hybrid search over DGMS circulars and CMR 2017."""
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or data.get("question") or "").strip()

    if not query:
        return jsonify({"success": False, "data": None, "message": "Query parameter cannot be empty"}), 400

    rag = RAGService.get_instance()
    result = rag.generate_answer(query)

    user_id = int(get_jwt_identity())
    log_action(
        user_id=user_id,
        action="ASSISTANT_QUERY",
        entity_type="rag_query",
        new_values={"query": query, "sources_count": len(result.get("sources", []))},
    )

    res_data = dict(result)
    res_data["content"] = result.get("answer")
    return jsonify({"success": True, "data": res_data, "message": "Response generated successfully"}), 200


@assistant_bp.route("/documents", methods=["GET"])
@jwt_required()
def list_documents():
    """List all regulatory reference documents in the knowledge base."""
    docs = query_db(
        """
        SELECT id, title, source, document_type, file_path, revision_date, version, is_active, ingested_at
        FROM knowledge_documents
        ORDER BY ingested_at DESC
        """
    )
    return jsonify({"success": True, "data": docs, "message": "Knowledge documents retrieved"}), 200


@assistant_bp.route("/ingest", methods=["POST"])
@jwt_required()
@role_required(["admin", "safety_officer"])
def ingest_document_route():
    """Upload or trigger ingestion of regulatory documents into the RAG vector store."""
    rag = RAGService.get_instance()
    user_id = int(get_jwt_identity())

    # Check if a file was uploaded
    if "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "data": None, "message": "No file selected"}), 400

        filename = secure_filename(file.filename)
        upload_dir = getattr(Config, "UPLOAD_DIR", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        saved_path = os.path.join(upload_dir, filename)
        file.save(saved_path)

        chunks = rag.ingest_document(
            file_path=saved_path,
            metadata={"title": filename.rsplit(".", 1)[0].replace("_", " ").title(), "source": filename}
        )
        log_action(user_id=user_id, action="INGEST_FILE", entity_type="knowledge_document", new_values={"filename": filename, "chunks": chunks})

        return jsonify({"success": True, "data": {"filename": filename, "chunks": chunks}, "message": f"Document ingested ({chunks} chunks)"}), 201

    # Otherwise re-scan default documents directory
    docs_dir = getattr(Config, "KNOWLEDGE_BASE_DIR", "knowledge_base/documents")
    if not os.path.exists(docs_dir):
        return jsonify({"success": False, "data": None, "message": "Knowledge base directory not found"}), 404

    total_chunks = 0
    for fname in os.listdir(docs_dir):
        if fname.lower().endswith((".txt", ".pdf", ".docx")):
            fpath = os.path.join(docs_dir, fname)
            chunks = rag.ingest_document(fpath, metadata={"title": fname.replace("_", " ").title(), "source": fname})
            total_chunks += chunks

    log_action(user_id=user_id, action="REINDEX_ALL", entity_type="knowledge_base", new_values={"total_chunks": total_chunks})

    return jsonify({"success": True, "data": {"total_chunks": total_chunks}, "message": f"Knowledge base indexed ({total_chunks} chunks)"}), 200
