-- PostgreSQL Database Creation Script
-- Run this script in PostgreSQL command line or pgAdmin

-- Create database
CREATE DATABASE borc_db;

-- Connect to the database (in psql: \c borc_db)

-- Create user (if not exists)
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'postgres'
   ) THEN
      CREATE USER postgres WITH PASSWORD 'postgres';
   END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE borc_db TO postgres;

-- Additional grants for the schema
\c borc_db
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;

