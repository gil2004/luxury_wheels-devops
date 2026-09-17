import sys
import os
import sqlite3
import tempfile
import pytest

os.environ.setdefault("SECRET_KEY", "test-secret")

_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ.setdefault("DATABASE_PATH", _db_path)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))


@pytest.fixture(scope="session", autouse=True)
def base_de_dados():
    pasta = os.path.join(os.path.dirname(__file__), "..")
    conn = sqlite3.connect(_db_path)
    for ficheiro in ("schema.sql", "seed.sql"):
        with open(os.path.join(pasta, ficheiro),) as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()
    yield
    os.close(_db_fd)
    os.unlink(_db_path)