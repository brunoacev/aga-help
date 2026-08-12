"""Fixtures compartilhadas para testes."""

from __future__ import annotations

import sqlite3

import pytest

from core.db import schema


@pytest.fixture(autouse=True)
def in_memory_db(tmp_path, monkeypatch):
    """Usa banco SQLite em memória para cada teste."""
    db_file = tmp_path / "test.db"

    def _get_connection():
        conn = sqlite3.connect(db_file)
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    monkeypatch.setattr("core.db.connection.DB_PATH", db_file)
    monkeypatch.setattr("core.db.connection.get_connection", _get_connection)
    schema.init_db()
    yield
