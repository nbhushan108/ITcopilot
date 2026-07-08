-- ITcopilot PostgreSQL Initialization Script
-- Creates extensions and default schema for production deployments.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges to application user
GRANT ALL PRIVILEGES ON DATABASE itcopilot TO itcopilot;
