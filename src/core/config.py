import os
from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = os.getenv('APP_NAME', 'Velocity Brain')
    env: str = os.getenv('ENV', 'dev')
    port: int = int(os.getenv('PORT', '8080'))

    # Database/runtime
    database_url: str = os.getenv('DATABASE_URL', 'postgresql://velocity:velocity@localhost:5432/velocitybrain')
    db_connect_timeout_seconds: int = int(os.getenv('DB_CONNECT_TIMEOUT_SECONDS', '5'))
    db_lock_timeout_ms: int = int(os.getenv('DB_LOCK_TIMEOUT_MS', '5000'))
    db_statement_timeout_ms: int = int(os.getenv('DB_STATEMENT_TIMEOUT_MS', '15000'))

    # Embeddings/models
    embed_dim: int = int(os.getenv('EMBED_DIM', '1536'))
    embedding_provider: str = os.getenv('EMBEDDING_PROVIDER', 'openai-compatible')
    embedding_model: str = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
    model_router: str = os.getenv('MODEL_ROUTER', 'native')

    # Paths and policy
    skills_path: str = os.getenv('SKILLS_PATH', 'skills')
    local_storage_path: str = os.getenv('LOCAL_STORAGE_PATH', './data')
    workspace_root: str = os.getenv('WORKSPACE_ROOT', str(Path.cwd()))
    identity_spec_path: str = os.getenv('IDENTITY_SPEC_PATH', 'identity.spec.json')
    default_access_level: str = os.getenv('DEFAULT_ACCESS_LEVEL', 'private')
    allow_unsafe_file_reads: bool = os.getenv('ALLOW_UNSAFE_FILE_READS', 'false').lower() == 'true'
    mcp_allow_destructive_tools: bool = os.getenv('MCP_ALLOW_DESTRUCTIVE_TOOLS', 'false').lower() == 'true'


settings = Settings()
