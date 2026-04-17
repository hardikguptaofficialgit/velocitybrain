from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.api.routes import router
from src.background.scheduler import start_scheduler
from src.core.config import settings

app = FastAPI(title=settings.app_name, version='1.0.0')
app.include_router(router)

DOCS_ROOT = Path('docs').resolve()
WEB_ROOT = Path('web').resolve()
DOC_PAGES: list[tuple[str, str, str, Path]] = [
    ('overview', 'Overview', 'Getting Started', Path('README.md').resolve()),
    ('client-integrations', 'Client Integrations', 'Getting Started', (DOCS_ROOT / 'CLIENT_INTEGRATIONS.md').resolve()),
    ('architecture', 'Architecture', 'Core Concepts', (DOCS_ROOT / 'ARCHITECTURE.md').resolve()),
    ('db-schema', 'DB Schema', 'Core Concepts', (DOCS_ROOT / 'DB_SCHEMA.md').resolve()),
    ('skill-system', 'Skill System', 'Core Concepts', (DOCS_ROOT / 'SKILL_SYSTEM.md').resolve()),
    ('agent-loop', 'Agent Loop', 'Workflows', (DOCS_ROOT / 'AGENT_LOOP.md').resolve()),
    ('workflows', 'Workflows', 'Workflows', (DOCS_ROOT / 'WORKFLOWS.md').resolve()),
    ('api-design', 'API Design', 'Interfaces', (DOCS_ROOT / 'API_DESIGN.md').resolve()),
    ('folder-structure', 'Folder Structure', 'Interfaces', (DOCS_ROOT / 'FOLDER_STRUCTURE.md').resolve()),
]
DOC_PAGE_MAP: dict[str, tuple[str, str, Path]] = {
    slug: (title, category, path) for slug, title, category, path in DOC_PAGES
}


if WEB_ROOT.exists():
    app.mount('/guide/static', StaticFiles(directory=str(WEB_ROOT)), name='guide-static')


@app.on_event('startup')
def _startup():
    start_scheduler()


@app.get('/')
def root():
    return {
        'app': settings.app_name,
        'mode': 'api-and-cli',
        'docs': '/docs',
        'guide': '/guide',
        'health': '/v1/healthz',
    }


@app.get('/guide', response_class=HTMLResponse)
def guide_home():
    index_file = WEB_ROOT / 'index.html'
    if not index_file.exists():
        raise HTTPException(status_code=404, detail='Guide app not found')
    return index_file.read_text(encoding='utf-8')


@app.get('/v1/docs/pages')
def docs_pages():
    pages = [
        {'slug': slug, 'title': title, 'category': category}
        for slug, title, category, file_path in DOC_PAGES
        if path_exists(file_path)
    ]
    return {'count': len(pages), 'pages': pages}


def path_exists(path: Path) -> bool:
    try:
        return path.exists() and path.is_file()
    except OSError:
        return False


@app.get('/v1/docs/page/{slug}')
def docs_page(slug: str):
    page = DOC_PAGE_MAP.get(slug)
    if not page:
        raise HTTPException(status_code=404, detail='Unknown docs page')
    title, category, file_path = page
    if not path_exists(file_path):
        raise HTTPException(status_code=404, detail='Docs page missing')
    try:
        display_path = str(file_path.relative_to(Path.cwd()))
    except ValueError:
        display_path = str(file_path)

    return {
        'slug': slug,
        'title': title,
        'category': category,
        'path': display_path,
        'markdown': file_path.read_text(encoding='utf-8'),
    }
