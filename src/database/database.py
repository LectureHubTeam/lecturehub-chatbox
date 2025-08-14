"""
Database operations for PostgreSQL and pgvector.
"""

from typing import Optional

import psycopg

from src.core.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, EMBEDDING_DIM
from src.utils.logger import logger


class DatabaseManager:
    """Manages PostgreSQL database connections and pgvector operations."""

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of DatabaseManager exists."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(
        self,
        connection_string: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize database manager with connection parameters.
        Only initializes once, subsequent calls return the existing instance.

        Args:
            connection_string: Full connection string (optional)
            host: Database host (optional, defaults to config)
            port: Database port (optional, defaults to config)
            database: Database name (optional, defaults to config)
            user: Database user (optional, defaults to config)
            password: Database password (optional, defaults to config)
        """
        # Only initialize once
        if self._initialized:
            return

        if connection_string:
            self.connection_string = connection_string
            self._psycopg_conn_str = self._to_psycopg_conn_str(connection_string)
        else:
            # Use individual parameters
            self.host = host or DB_HOST
            self.port = port or DB_PORT
            self.database = database or DB_NAME
            self.user = user or DB_USER
            self.password = password or DB_PASSWORD

            # Construct connection strings
            self.connection_string = (
                f"postgresql+psycopg://{self.user}:{self.password}" f"@{self.host}:{self.port}/{self.database}"
            )
            self._psycopg_conn_str = (
                f"postgresql://{self.user}:{self.password}" f"@{self.host}:{self.port}/{self.database}"
            )

        self._initialized = True
        logger.info("DatabaseManager singleton initialized")

    def _to_psycopg_conn_str(self, sqlalchemy_style_url: str) -> str:
        """
        Convert an SQLAlchemy-style URL to a psycopg-compatible URL.

        Args:
            sqlalchemy_style_url: URL in format postgresql://user:pass@host:5432/db

        Returns:
            psycopg-compatible connection string
        """
        return sqlalchemy_style_url

    def ensure_pgvector_schema(self) -> None:
        """
        Ensure pgvector extension and helper table exist.
        Creates HNSW index if supported, otherwise falls back to IVFFLAT.
        """
        try:
            with psycopg.connect(self._psycopg_conn_str) as conn:
                conn.autocommit = True
                with conn.cursor() as cur:
                    self._create_pgvector_extension(cur)
                    self._create_embeddings_table(cur)
                    self._create_vector_index(cur)
        except Exception as e:
            logger.error("PostgreSQL schema setup failed: %s", e)
            raise

    def _create_pgvector_extension(self, cursor) -> None:
        """Create pgvector extension if it doesn't exist."""
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        except Exception as e:
            logger.warning("Could not create pgvector extension: %s", e)
            # Continue without pgvector extension - other operations may still work

    def _create_embeddings_table(self, cursor) -> None:
        """Create the embeddings helper table."""
        try:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS embeddings (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding VECTOR({EMBEDDING_DIM}),
                    metadata JSONB
                );
                """
            )
        except Exception as e:
            logger.warning("Could not create embeddings table: %s", e)
            # This might fail if pgvector extension is not available
            raise

    def _create_vector_index(self, cursor) -> None:
        """Create vector index, trying HNSW first, then IVFFLAT."""
        try:
            # Try HNSW index first (pgvector >= 0.5)
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS embeddings_hnsw_idx
                ON embeddings USING hnsw (embedding vector_cosine_ops);
                """
            )
        except Exception:
            try:
                # Fall back to IVFFLAT
                cursor.execute("SET enable_seqscan = off;")
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS embeddings_ivfflat_idx
                    ON embeddings USING ivfflat (embedding vector_cosine_ops)
                    WITH (lists = 100);
                    """
                )
            except Exception as e2:
                logger.warning("Could not create HNSW/IVFFLAT index: %s", e2)

    def test_connection(self) -> bool:
        """Test if the database connection is working."""
        try:
            with psycopg.connect(self._psycopg_conn_str) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                    return True
        except Exception as e:
            logger.error("Database connection test failed: %s", e)
            return False

    def get_connection_info(self) -> dict:
        """Get database connection information."""
        return {
            "host": getattr(self, "host", "N/A"),
            "port": getattr(self, "port", "N/A"),
            "database": getattr(self, "database", "N/A"),
            "user": getattr(self, "user", "N/A"),
            "connection_string": self.connection_string,
        }


if __name__ == "__main__":
    # Test with individual parameters
    db = DatabaseManager(host="localhost", port="5432", database="embedding", user="root", password="root_password")

    print("Database connection info:", db.get_connection_info())

    if db.test_connection():
        print("✓ Database connection successful")
        try:
            db.ensure_pgvector_schema()
            print("✓ Schema setup completed")
        except Exception as e:
            print(f"✗ Schema setup failed: {e}")
    else:
        print("✗ Database connection failed")
