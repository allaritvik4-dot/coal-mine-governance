"""Database utility module for SQLite with helper functions."""

import sqlite3
import os
from flask import g, current_app, has_app_context
from config import Config

_standalone_db = None


def get_db():
    """Get or create database connection for the current Flask request context or standalone session."""
    if has_app_context():
        if "db" not in g:
            db_path = getattr(Config, "DATABASE_PATH", "database/coal_mine.db")
            if current_app and current_app.config.get("DATABASE_PATH"):
                db_path = current_app.config["DATABASE_PATH"]

            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON;")
        return g.db
    else:
        global _standalone_db
        if _standalone_db is None:
            db_path = getattr(Config, "DATABASE_PATH", "database/coal_mine.db")
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
            _standalone_db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            _standalone_db.row_factory = sqlite3.Row
            _standalone_db.execute("PRAGMA foreign_keys = ON;")
        return _standalone_db


def close_db(e=None):
    """Close the database connection if open."""
    if has_app_context():
        db = g.pop("db", None)
        if db is not None:
            db.close()
    else:
        global _standalone_db
        if _standalone_db is not None:
            _standalone_db.close()
            _standalone_db = None


def query_db(query, args=(), one=False):
    """Execute a SELECT query and return rows as list of dicts (or single dict if one=True)."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if not rv:
        return None if one else []
    results = [dict(row) for row in rv]
    return results[0] if one else results


def execute_db(query, args=()):
    """Execute an INSERT, UPDATE, or DELETE query and commit transaction.
    
    Returns the lastrowid on INSERT, or rowcount on other operations.
    """
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    last_id = cur.lastrowid
    row_count = cur.rowcount
    cur.close()
    return last_id if last_id else row_count


def init_db(app=None):
    """Initialize database tables and seed initial data if database is empty."""
    db_path = getattr(Config, "DATABASE_PATH", "database/coal_mine.db")
    if app and app.config.get("DATABASE_PATH"):
        db_path = app.config["DATABASE_PATH"]

    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

    # Check if users table is populated; if empty, run seed data
    cur = conn.execute("SELECT COUNT(*) AS count FROM users;")
    row = cur.fetchone()
    if row and row["count"] == 0:
        seed_path = os.path.join(os.path.dirname(__file__), "seed_data.sql")
        if os.path.exists(seed_path):
            with open(seed_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            conn.commit()

    conn.close()
