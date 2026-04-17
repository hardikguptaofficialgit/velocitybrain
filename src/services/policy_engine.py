from typing import Any

from src.core.config import settings


class PolicyEngine:
    DESTRUCTIVE_TOOLS = {'delete_page', 'put_page', 'sync_brain'}

    def check_tool_call(self, name: str, arguments: dict[str, Any] | None = None) -> None:
        args = arguments or {}
        if name in self.DESTRUCTIVE_TOOLS:
            allow = settings.mcp_allow_destructive_tools or bool(args.get('approve'))
            if not allow:
                raise PermissionError(
                    f"Tool '{name}' is destructive and blocked by policy. "
                    "Pass approve=true and set MCP_ALLOW_DESTRUCTIVE_TOOLS=true to enable."
                )
