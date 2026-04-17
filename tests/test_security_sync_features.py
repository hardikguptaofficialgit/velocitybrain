from pathlib import Path

from src.core.config import settings
from src.services.org_ingest import OrgIngestService
from src.services.policy_engine import PolicyEngine
from src.services.sync_service import SyncService


def test_policy_engine_blocks_destructive_tools_by_default():
    engine = PolicyEngine()
    try:
        engine.check_tool_call('delete_page', {})
        assert False, 'expected PermissionError'
    except PermissionError:
        assert True


def test_org_parse_sections():
    content = """* Heading A\nBody A\n** Heading B\nBody B"""
    sections = OrgIngestService().parse_sections(content)
    assert len(sections) >= 2
    assert sections[0]['title'] == 'Heading A'


def test_sync_dry_run_does_not_write_registry(tmp_path: Path, monkeypatch):
    repo = tmp_path / 'repo'
    repo.mkdir()
    (repo / 'notes.org').write_text('* Note\nHello', encoding='utf-8')

    monkeypatch.setattr(settings, 'workspace_root', str(tmp_path))
    monkeypatch.setattr(settings, 'local_storage_path', str(tmp_path / 'data'))
    monkeypatch.setattr(settings, 'allow_unsafe_file_reads', False)

    service = SyncService()
    result = service.full_sync(repos=[str(repo)], dry_run=True)
    assert result['dry_run'] is True
    assert result['status'] == 'planned'
    assert not service.registry_path.exists()
