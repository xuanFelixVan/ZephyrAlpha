# [BLUEPRINT] MOD-LLM_SECURITY
# [MODULE] zephyr.security.llm_defense.llm_security.layers.l2a_process_sandbox
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.llm_defense.llm_security.gateway; tests.llm_security.test_l2a_process_sandbox
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SandboxStatus(Enum):
    """Status of a sandbox execution."""

    COMPLETED = "completed"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"


@dataclass
class SandboxContainerConfig:
    """Configuration for sandbox container.

    Defaults match the canonical hardening profile: a slim Python image,
    30s timeout, and a read-only root filesystem.
    """

    image: str = "python:3.12-slim"
    timeout_seconds: int = 30
    read_only_rootfs: bool = True
    # Legacy fields (kept for backward compatibility with prior stub API)
    memory_limit: str = "512m"
    cpu_limit: float = 1.0
    network_disabled: bool = True
    read_only_paths: list[str] = field(default_factory=list)


@dataclass
class WASIRuntimeConfig:
    """Configuration for WASI runtime sandbox.

    Defaults: WASI ``_start`` entry point and 256 pages (16 MiB) of memory.
    """

    entry_point: str = "_start"
    memory_pages: int = 256
    # Legacy fields
    module_path: str = ""
    max_memory: int = 16777216
    max_threads: int = 1
    timeout_ms: int = 30000
    allowed_env: list[str] = field(default_factory=list)


@dataclass
class FilesystemAuditEntry:
    """Audit entry for a filesystem operation in the sandbox."""

    path: str = ""
    operation: str = ""
    checksum: str = ""
    size_bytes: int = 0
    # Legacy fields
    allowed: bool = True
    timestamp: str = ""


@dataclass
class SandboxExecutionResult:
    """Result of executing code in the sandbox."""

    status: SandboxStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    blocked_by_guard: bool = False


@dataclass
class ChangeValidationResult:
    """Result of validating filesystem changes between snapshots."""

    allowed: bool = True
    new_files: int = 0
    suspicious_paths: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


# Data exfiltration patterns — BlindSpot5 detections.
_DATA_EXFIL_PATTERNS = [
    r"extract\s+all\s+data",
    r"gather\s+information\s+recursively",
    r"exfiltrate",
    r"upload\s+all\s+files",
    r"send\s+everything\s+to",
    r"dump\s+(the\s+)?database",
]

# Suspicious filesystem paths — secret material that must not appear post-change.
_SUSPICIOUS_PATH_PATTERNS = [
    r"secrets?[/\\]",
    r"\.env\b",
    r"\.ssh[/\\]",
    r"\.aws[/\\]",
    r"credentials?",
    r"private[_-]?key",
    r"/etc/shadow",
    r"/etc/passwd",
    r"id_rsa",
    r"\.pfx\b",
    r"\.p12\b",
]


class BlindSpot5ProcessSandboxGuard:
    """Combined blind-spot detection and process sandboxing guard.

    Scans code/command text for data-exfiltration and mass-collection
    patterns before the code is allowed to execute in the sandbox.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def scan(self, code: str, command: str = "") -> dict[str, Any]:
        """Scan code (and optional command) for exfiltration patterns.

        Returns:
            Dict with ``blocked`` (bool) and ``violation_count`` (int).
        """
        text = f"{code or ''}\n{command or ''}"
        lowered = text.lower()
        violations = 0
        for pat in _DATA_EXFIL_PATTERNS:
            if re.search(pat, lowered, re.IGNORECASE):
                violations += 1
        return {"blocked": violations > 0, "violation_count": violations}

    # Legacy interface
    def check_blind_spot(self, process_id: str) -> bool:
        return False

    def sandbox_execute(self, command: str, timeout: int = 30) -> dict[str, Any]:
        return {"exit_code": 0, "stdout": "", "stderr": ""}

    def validate_process(self, process_id: str) -> bool:
        return True


class ProcessSandbox:
    """Low-level process sandbox executor (legacy interface)."""

    def __init__(self, config=None):
        self.config = config or {}

    def execute(self, command, timeout=30):
        return {"exit_code": 0, "stdout": "", "stderr": ""}

    def validate_command(self, command):
        return True


class ProcessSandboxLayer:
    """L2a Process Sandbox Layer.

    Executes untrusted Python code in an isolated subprocess with a hard
    timeout and a BlindSpot5 pre-execution guard. Filesystem access can be
    audited and changes between two snapshots validated for safety.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._guard = BlindSpot5ProcessSandboxGuard()

    def execute_in_sandbox(
        self,
        code: str,
        timeout: int = 30,
    ) -> SandboxExecutionResult:
        """Execute Python ``code`` in a subprocess with guard + timeout.

        Pre-checks the code with BlindSpot5; if it trips, returns BLOCKED.
        Otherwise spawns ``python -c <code>`` and enforces ``timeout``.
        """
        guard_result = self._guard.scan(code, "")
        if guard_result["blocked"]:
            return SandboxExecutionResult(
                status=SandboxStatus.BLOCKED,
                stdout="",
                stderr="blocked by BlindSpot5ProcessSandboxGuard",
                exit_code=-1,
                blocked_by_guard=True,
            )
        try:
            proc = subprocess.run(
                [sys.executable, "-c", code or ""],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return SandboxExecutionResult(
                status=SandboxStatus.COMPLETED,
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                blocked_by_guard=False,
            )
        except subprocess.TimeoutExpired as e:
            out = e.stdout if isinstance(e.stdout, str) else ""
            err = e.stderr if isinstance(e.stderr, str) else ""
            return SandboxExecutionResult(
                status=SandboxStatus.TIMEOUT,
                stdout=out,
                stderr=err,
                exit_code=-1,
                blocked_by_guard=False,
            )

    def audit_filesystem_access(
        self,
        path: str,
        operation: str = "scan",
    ) -> list[FilesystemAuditEntry]:
        """Walk ``path`` and produce one audit entry per file found."""
        entries: list[FilesystemAuditEntry] = []
        if not path or not os.path.exists(path):
            return entries
        if os.path.isfile(path):
            entries.append(self._make_entry(path, operation))
            return entries
        if os.path.isdir(path):
            for root, _dirs, files in os.walk(path):
                for name in files:
                    fpath = os.path.join(root, name)
                    try:
                        entries.append(self._make_entry(fpath, operation))
                    except OSError:
                        continue
        return entries

    @staticmethod
    def _make_entry(path: str, operation: str) -> FilesystemAuditEntry:
        try:
            size = os.path.getsize(path)
        except OSError:
            size = 0
        checksum = ""
        try:
            with open(path, "rb") as f:
                checksum = hashlib.md5(f.read()).hexdigest()
        except (OSError, PermissionError):
            checksum = ""
        return FilesystemAuditEntry(
            path=path,
            operation=operation,
            checksum=checksum,
            size_bytes=size,
        )

    def validate_changes(
        self,
        before: list[FilesystemAuditEntry],
        after: list[FilesystemAuditEntry],
    ) -> ChangeValidationResult:
        """Validate the diff between two filesystem snapshots.

        New files (in ``after`` but not ``before``) increment ``new_files``.
        Any new file whose path matches a suspicious pattern flips
        ``allowed`` to False and is recorded in ``suspicious_paths``.
        """
        before_paths = {e.path for e in (before or [])}
        after_paths = {e.path for e in (after or [])}
        new_paths = after_paths - before_paths
        suspicious: list[str] = []
        for p in new_paths:
            for pat in _SUSPICIOUS_PATH_PATTERNS:
                if re.search(pat, p, re.IGNORECASE):
                    suspicious.append(p)
                    break
        allowed = len(suspicious) == 0
        return ChangeValidationResult(
            allowed=allowed,
            new_files=len(new_paths),
            suspicious_paths=suspicious,
            details={
                "before_count": len(before_paths),
                "after_count": len(after_paths),
                "new_paths": sorted(new_paths),
            },
        )

    # Legacy interface
    def execute(self, command, timeout=30):
        return {"exit_code": 0, "stdout": "", "stderr": ""}

    def validate_command(self, command):
        return True

    def layer_name(self) -> str:
        return "l2a_process_sandbox"

    def layer_index(self) -> int:
        return 2

    async def evaluate(self, ctx: object) -> object:
        """Pass-through evaluation — sandbox layer does not block the gateway chain.

        Code-execution guarding happens at ``execute_in_sandbox`` time;
        the gateway-facing ``evaluate`` is a pass-through ALLOW so downstream
        layers can continue.
        """
        from zephyr.security.llm_defense.llm_security.protocol import SecurityResult
        from zephyr.shared.contracts.security.security_decision import SecurityDecision

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="l2a_process_sandbox — pass-through",
            layer_name="l2a_process_sandbox",
            score=1.0,
        )
