from src.cli import build_parser
from src.mcp_stdio import VelocityBrainMCPServer


def test_cli_has_expected_commands():
    parser = build_parser()

    args = parser.parse_args(['init'])
    assert args.command == 'init'

    args = parser.parse_args(['query', 'what do I know about Jane Doe?'])
    assert args.command == 'query'
    assert args.question.startswith('what do I know')

    args = parser.parse_args(['status'])
    assert args.command == 'status'

    args = parser.parse_args(['status'])
    assert args.command == 'status'


def test_mcp_tool_list_contains_core_tools():
    tools = VelocityBrainMCPServer()._tool_list()['tools']
    names = {tool['name'] for tool in tools}

    assert 'ingest_text' in names
    assert 'query' in names
    assert 'run_agent' in names
    assert 'list_skills' in names
    assert 'healthz' in names

def test_mcp_policy_blocks_destructive_calls():
    server = VelocityBrainMCPServer()
    try:
        server._tool_call('delete_page', {})
        assert False, 'expected PermissionError'
    except PermissionError:
        assert True
