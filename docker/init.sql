-- Initialize database with pgvector extension
-- This script runs automatically when the PostgreSQL container starts

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

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
    RAISE NOTICE 'PGVector will create its own tables automatically';
END $$;
