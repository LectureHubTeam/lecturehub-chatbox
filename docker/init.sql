-- Initialize database with pgvector extension
-- This script runs automatically when the PostgreSQL container starts

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(384),
    metadata JSONB
);

-- Create HNSW index for vector similarity search
CREATE INDEX IF NOT EXISTS embeddings_hnsw_idx 
ON embeddings USING hnsw (embedding vector_cosine_ops);

-- Create additional indexes for better performance
CREATE INDEX IF NOT EXISTS embeddings_metadata_idx 
ON embeddings USING GIN (metadata);

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE embedding TO root;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO root;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO root;

-- Create a function to check if pgvector is working
CREATE OR REPLACE FUNCTION test_pgvector() RETURNS TEXT AS $$
BEGIN
    RETURN 'pgvector extension is working correctly';
END;
$$ LANGUAGE plpgsql;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully';
    RAISE NOTICE 'pgvector extension enabled';
    RAISE NOTICE 'embeddings table created with HNSW index';
END $$;
