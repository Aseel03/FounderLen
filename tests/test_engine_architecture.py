from __future__ import annotations

import ast
from pathlib import Path

FORBIDDEN_IMPORTS = (
    "founderlens.agent",
    "founderlens.mcp_servers",
    "langgraph",
    "fastapi",
    "mcp",
    "groq",
)
ENGINE_DIR = Path(__file__).parents[1] / "src" / "founderlens" / "engine"


def test_engine_does_not_import_agent_or_transport_packages() -> None:
    violations: list[str] = []
    for source in ENGINE_DIR.rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules = [node.module]
            else:
                continue
            for module in modules:
                if any(
                    module == prefix or module.startswith(prefix + ".")
                    for prefix in FORBIDDEN_IMPORTS
                ):
                    violations.append(f"{source.relative_to(ENGINE_DIR)} imports {module}")
    assert not violations, "Forbidden engine imports:\n" + "\n".join(violations)
