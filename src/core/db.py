from contextlib import contextmanager
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

from src.core.config import settings


@contextmanager
def get_conn():
    try:
        options = f"-c lock_timeout={settings.db_lock_timeout_ms} -c statement_timeout={settings.db_statement_timeout_ms}"
        with psycopg.connect(
            settings.database_url,
            row_factory=dict_row,
            connect_timeout=max(1, settings.db_connect_timeout_seconds),
            options=options,
        ) as conn:
            yield conn
    except psycopg.OperationalError as exc:
        raise RuntimeError(
            'Database connection failed. Check DATABASE_URL and ensure the DB/schema exist. '
            f'url={settings.database_url} error={exc}'
        ) from exc


def bootstrap_schema(embed_dim: int | None = None) -> dict:
    dim = int(embed_dim or settings.embed_dim)
    schema_path = Path('migrations/schema.sql')
    if not schema_path.exists():
        return {'ok': False, 'error': f'schema file missing: {schema_path}'}

    sql = schema_path.read_text(encoding='utf-8')
    sql = sql.replace('vector(1536)', f'vector({dim})')

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

    return {'ok': True, 'embed_dim': dim, 'schema': str(schema_path)}


def serialize_vector(values: list[float], dim: int | None = None) -> str:
    target = int(dim or settings.embed_dim)
    if len(values) != target:
        raise ValueError(f'vector dimension mismatch: expected {target}, got {len(values)}')
    return '[' + ','.join(f'{float(v):.8f}' for v in values) + ']'
