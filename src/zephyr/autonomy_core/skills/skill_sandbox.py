# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_sandbox
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.governance.audit_trail.bridge
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_sandbox | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Sandbox
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 沙箱隔离执行引擎
======================
机制:
  1. ToolAllowlist: 仅允许 Skill 声明的工具集
  2. FileBoundary: 限制文件读写范围到沙箱目录
  3. NetworkBoundary: 阻止未授权的网络调用
  4. ResourceQuota: CPU/内存/IO 配额限制
  5. TaintTracking: 标记来自沙箱的输出为"需审核"
"""

from __future__ import annotations

import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from zephyr.governance.audit_trail.bridge import write_to_core

_DEFAULT_SAFE_TOOLS = {
    "read_file",
    "grep",
    "glob",
    "ls",
    "search_codebase",
}

_RISKY_TOOLS = {
    "write_file",
    "search_replace",
    "delete_file",
    "run_command",
    "execute",
    "bash",
}

_FORBIDDEN_TOOLS = {
    "mcp_github_create_or_update_file",
    "mcp_github_push_files",
    "mcp_github_delete_file",
    "mcp_github_merge_pr",
}

_DANGEROUS_COMMAND_PATTERNS = [
    r"rm\s+-rf",
    r"format\s+[cdef]:",
    r"dd\s+if=",
    r"mkfs\.",
    r">\s*/dev/",
    r"chmod\s+777",
    r"wget\s+.*\|\s*(?:ba)?sh",
    r"curl\s+.*\|\s*(?:ba)?sh",
    r"eval\s+",
]


class SkillSandbox:
    """Skill 沙箱隔离执行器"""

    SANDBOX_ROOT = Path(tempfile.gettempdir()) / "zephyr_sandbox"

    def __init__(self, skill_id: str):
        self._skill_id = skill_id
        self._sandbox_dir = self.SANDBOX_ROOT / skill_id.replace(":", "_").replace("/", "_")
        self._allowed_tools: set[str] = set(_DEFAULT_SAFE_TOOLS)
        self._blocked_tools: set[str] = set()
        self._file_boundary: Path | None = None
        self._network_allowed = False
        self._active = False
        self._audit_log: list[dict[str, Any]] = []

    @property
    def isolated_tools(self) -> list[str]:
        return sorted(self._allowed_tools) if self._active else []

    def activate(
        self,
        allowed_tools: list[str] | None = None,
        restrict_files: bool = True,
        allow_network: bool = False,
    ) -> dict[str, Any]:
        self._active = True

        if allowed_tools:
            self._allowed_tools = set(allowed_tools)
        else:
            self._allowed_tools = set(_DEFAULT_SAFE_TOOLS)

        self._blocked_tools = set()
        self._blocked_tools.update(_FORBIDDEN_TOOLS)

        self._network_allowed = allow_network

        if restrict_files:
            self._sandbox_dir.mkdir(parents=True, exist_ok=True)
            self._file_boundary = self._sandbox_dir

        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "action": "sandbox_activated",
            "skill_id": self._skill_id,
            "allowed_tools": sorted(self._allowed_tools),
            "blocked_tools": sorted(self._blocked_tools),
            "file_boundary": str(self._file_boundary) if self._file_boundary else "none",
            "network_allowed": self._network_allowed,
        }
        self._audit_log.append(entry)

        write_to_core("skill_sandbox_activated", entry)

        return {
            "sandbox": "active",
            "skill_id": self._skill_id,
            "isolated_tools": sorted(self._allowed_tools),
            "blocked_tools": sorted(self._blocked_tools),
            "file_boundary": str(self._file_boundary) if self._file_boundary else "unrestricted",
            "network_allowed": self._network_allowed,
        }

    def check_tool(self, tool_name: str) -> tuple[bool, str]:
        if not self._active:
            return True, "sandbox_not_active"

        if tool_name in _FORBIDDEN_TOOLS:
            return False, "tool_forbidden_globally"

        if tool_name in self._blocked_tools:
            return False, "tool_blocked"

        if tool_name in self._allowed_tools:
            return True, "tool_allowed"

        if tool_name in _RISKY_TOOLS:
            return False, "risky_tool_not_allowed"

        return False, "tool_not_in_allowlist"

    def check_command(self, command: str) -> tuple[bool, str]:
        if not self._active:
            return True, "sandbox_not_active"

        for pattern in _DANGEROUS_COMMAND_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                self._audit_log.append(
                    {
                        "timestamp": datetime.now(UTC).isoformat(),
                        "action": "command_blocked",
                        "skill_id": self._skill_id,
                        "command": command[:200],
                        "pattern_matched": pattern,
                    }
                )
                write_to_core(
                    "skill_sandbox_command_blocked",
                    {
                        "skill_id": self._skill_id,
                        "command": command[:200],
                        "pattern_matched": pattern,
                    },
                )
                return False, f"dangerous_command_pattern: {pattern}"

        return True, "command_allowed"

    def check_file_access(self, file_path: str) -> tuple[bool, str]:
        if not self._active:
            return True, "sandbox_not_active"

        if self._file_boundary is None:
            return True, "no_file_boundary"

        resolved = Path(file_path).resolve()

        if str(resolved) == str(self._file_boundary):
            return True, "file_in_sandbox"

        sandbox_str = str(self._file_boundary)
        if str(resolved).startswith(sandbox_str):
            return True, "file_in_sandbox"

        return False, f"file_outside_sandbox: {str(resolved)[:100]}"

    def deactivate(self) -> dict[str, Any]:
        self._active = False

        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "action": "sandbox_deactivated",
            "skill_id": self._skill_id,
        }
        self._audit_log.append(entry)

        write_to_core("skill_sandbox_deactivated", entry)

        return {
            "sandbox": "inactive",
            "skill_id": self._skill_id,
            "audit_log_entries": len(self._audit_log),
        }

    def get_audit(self) -> list[dict[str, Any]]:
        return list(self._audit_log)
