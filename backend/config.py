"""Application configuration for Coal Mine Smart Governance & Compliance Monitoring System."""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration class."""

    # Database
    DATABASE_PATH = os.environ.get(
        "DATABASE_PATH", os.path.join(BASE_DIR, "database", "coal_mine.db")
    )

    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY", "coal-mine-governance-secret-key-change-in-production")

    # JWT Settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.environ.get("JWT_ACCESS_TOKEN_HOURS", 8))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Knowledge Base / RAG
    KNOWLEDGE_BASE_DIR = os.path.join(BASE_DIR, "knowledge_base", "documents")
    CHROMA_PERSIST_DIR = os.environ.get(
        "CHROMA_PERSIST_DIR", os.path.join(BASE_DIR, "chroma_db")
    )

    # File Uploads
    UPLOAD_DIR = os.environ.get(
        "UPLOAD_DIR", os.path.join(BASE_DIR, "uploads")
    )
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
