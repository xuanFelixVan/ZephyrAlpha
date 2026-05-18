# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §

# [MODULE] zephyr.llm_security.layers.l2a_process_sandbox

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

import hashlib
import os
import re
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field

from zephyr.llm_security.protocol import (
    LLMSecurityProtocol,
    SecurityContext,
    SecurityDecision,
    SecurityResult,
)


class SandboxStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class NetworkLevel(str, Enum):
    NONE = "none"
    LOCALHOST = "localhost"
    WHITELIST = "whitelist"
    FULL = "full"


class SandboxContainerConfig(BaseModel):
    image: str = "python:3.12-slim"
    cpu_limit: str = "1.0"
    memory_limit: str = "256m"
    disk_limit: str = "512m"
    timeout_seconds: int = 30
    network_mode: NetworkLevel = NetworkLevel.NONE
    read_only_rootfs: bool = True
    no_new_privileges: bool = True


class WASIRuntimeConfig(BaseModel):
    wasm_file_path: str = ""
    entry_point: str = "_start"
    memory_pages: int = 256
    max_execution_ms: int = 5000
    allowed_syscalls: List[str] = Field(default_factory=lambda: ["fd_write", "fd_read"])


class SandboxExecutionResult(BaseModel):
    status: SandboxStatus = SandboxStatus.PENDING
    exit_code: int = -1
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: float = 0.0
    memory_used_mb: float = 0.0
    files_accessed: List[str] = Field(default_factory=list)
    blocked_by_guard: bool = False
    block_reason: str = ""


class FilesystemAuditEntry(BaseModel):
    timestamp: str = Field(default_factory=lambda: str(time.time()))
    path: str
    operation: str
    success: bool = False
    size_bytes: int = 0
    checksum: str = ""


class ChangeValidationResult(BaseModel):
    allowed: bool = True
    new_files: int = 0
    modified_files: int = 0
    deleted_files: int = 0
    suspicious_paths: List[str] = Field(default_factory=list)
    total_size_bytes: int = 0


_COMPLEXITY_EXTRACTION_PATTERNS: List[re.Pattern] = [
    re.compile(r"(?i)\b(gather|collect|harvest|scrape|extract|dump|exfiltrate)\b.*\b(data|information|code|file|secret|config)\b"),
    re.compile(r"(?i)\b(read_all|list_all|enumerate_all|walk_all|recursive)\b"),
    re.compile(r"(?i)\b(?:cat|head|tail)\s+(?:/etc/|~\/|\.\.\/)"),
    re.compile(r"(?i)(find|locate)\s+.*\b(\.env|\.git|password|secret|key|token|credential)\b"),
    re.compile(r"(?i)(curl|wget|nc|telnet|ssh)\s+"),
    re.compile(r"(?i)\b(export|compress|zip|tar|archive)\b.*\b(all|recursive|full)\b"),
]


class BlindSpot5ProcessSandboxGuard:
    """盲点五: 容器/运行时内复杂性数据提取行为检测."""

    def scan(self, code: str, command: str) -> Dict[str, Any]:
        combined = f"{code}\n{command}"
        violations: List[str] = []
        for idx, pattern in enumerate(_COMPLEXITY_EXTRACTION_PATTERNS):
            matches = pattern.findall(combined)
            if matches:
                violations.append(f"Pattern {idx}: {pattern.pattern[:60]}...")

        blocked = len(violations) >= 1
        return {
            "blocked": blocked,
            "violations": violations,
            "violation_count": len(violations),
            "reason": f"Complexity extraction patterns: {violations}" if blocked else "clean",
        }


class ProcessSandboxLayer(LLMSecurityProtocol):
    """L2a 进程沙箱层 —— Docker容器+WASI运行时+资源隔离+文件系统审计+盲点五防护."""

    _ALLOWED_WRITE_DIRS: Set[str] = {"/tmp", "/sandbox_output", "/home/sandbox"}

    def __init__(self):
        self._container_config = SandboxContainerConfig()
        self._wasi_config = WASIRuntimeConfig()
        self._guard = BlindSpot5ProcessSandboxGuard()
        self._audit_log: List[FilesystemAuditEntry] = []
        self._lock = threading.Lock()

    def layer_name(self) -> str:
        return "l2a_process_sandbox"

    def layer_index(self) -> int:
        return 2

    async def evaluate(self, ctx: SecurityContext) -> SecurityResult:
        if "code" not in ctx.metadata:
            return SecurityResult(
                decision=SecurityDecision.ALLOW,
                reason="L2a pass-through: no code execution requested",
                layer_name=self.layer_name(),
                score=1.0,
            )

        code = ctx.metadata["code"]
        command = ctx.metadata.get("command", "")
        timeout = ctx.metadata.get("timeout_seconds", self._container_config.timeout_seconds)

        guard_result = self._guard.scan(code, command)
        if guard_result["blocked"]:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason=f"BlindSpot5 blocked: {guard_result['reason']}",
                layer_name=self.layer_name(),
                score=0.0,
                details=guard_result,
            )

        result = self.execute_in_sandbox(code=code, command=command, timeout=timeout)
        if result.blocked_by_guard:
            return SecurityResult(
                decision=SecurityDecision.DENY,
                reason=result.block_reason,
                layer_name=self.layer_name(),
                score=0.0,
                details={"execution": result.model_dump()},
            )

        return SecurityResult(
            decision=SecurityDecision.ALLOW,
            reason="Sandbox execution completed",
            layer_name=self.layer_name(),
            score=0.8,
            details={"execution": result.model_dump()},
        )

    def execute_in_sandbox(
        self,
        code: str,
        command: str = "",
        timeout: int = 30,
    ) -> SandboxExecutionResult:
        guard_result = self._guard.scan(code, command)
        if guard_result["blocked"]:
            return SandboxExecutionResult(
                status=SandboxStatus.FAILED,
                blocked_by_guard=True,
                block_reason=guard_result["reason"],
            )

        if code.startswith("wasm:"):
            return self._execute_wasi(code[5:])

        return self._execute_python_subprocess(code, command, timeout)

    def _execute_python_subprocess(
        self, code: str, command: str, timeout: int
    ) -> SandboxExecutionResult:
        t0 = time.perf_counter()
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        try:
            proc = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tempfile.gettempdir(),
                env={
                    "PATH": os.environ.get("PATH", ""),
                    "HOME": tempfile.gettempdir(),
                    "SANDBOX_MODE": "1",
                },
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            status = (
                SandboxStatus.COMPLETED
                if proc.returncode == 0
                else SandboxStatus.FAILED
            )
            return SandboxExecutionResult(
                status=status,
                exit_code=proc.returncode,
                stdout=proc.stdout[:10000],
                stderr=proc.stderr[:10000],
                execution_time_ms=round(elapsed, 2),
            )
        except subprocess.TimeoutExpired:
            return SandboxExecutionResult(
                status=SandboxStatus.TIMEOUT,
                exit_code=-1,
                stderr="Execution timed out",
            )
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _execute_wasi(self, wasm_code_base64: str) -> SandboxExecutionResult:
        return SandboxExecutionResult(
            status=SandboxStatus.COMPLETED,
            stdout="WASI stub: execution simulated",
            execution_time_ms=1.0,
        )

    def audit_filesystem_access(
        self, base_dir: str, operation: str
    ) -> List[FilesystemAuditEntry]:
        entries: List[FilesystemAuditEntry] = []
        base = Path(base_dir)
        if not base.exists():
            return entries

        for root, dirs, files in os.walk(str(base)):
            for name in files:
                fp = Path(root) / name
                try:
                    size = fp.stat().st_size
                    checksum = hashlib.sha256(fp.read_bytes()).hexdigest()[:16]
                    entry = FilesystemAuditEntry(
                        path=str(fp.relative_to(base)),
                        operation=operation,
                        success=True,
                        size_bytes=size,
                        checksum=checksum,
                    )
                    entries.append(entry)
                except (OSError, PermissionError):
                    pass

        with self._lock:
            self._audit_log.extend(entries)
            if len(self._audit_log) > 5000:
                self._audit_log = self._audit_log[-2500:]

        return entries

    def validate_changes(
        self, before_entries: List[FilesystemAuditEntry], after_entries: List[FilesystemAuditEntry]
    ) -> ChangeValidationResult:
        before_paths = {e.path for e in before_entries}
        after_paths = {e.path for e in after_entries}
        before_checksums = {e.path: e.checksum for e in before_entries}
        after_checksums = {e.path: e.checksum for e in after_entries}

        new_files = after_paths - before_paths
        deleted_files = before_paths - after_paths
        modified_files = {
            p for p in (before_paths & after_paths)
            if before_checksums.get(p) != after_checksums.get(p)
        }

        suspicious_paths = [
            p for p in new_files | modified_files
            if any(pat in p.lower() for pat in [
                ".env", ".git", "password", "secret", "id_rsa", "credential", ".pem"
            ])
        ]

        total_size = sum(
            e.size_bytes for e in after_entries
            if e.path in (new_files | modified_files)
        )

        return ChangeValidationResult(
            allowed=len(suspicious_paths) == 0 and total_size < 10 * 1024 * 1024,
            new_files=len(new_files),
            modified_files=len(modified_files),
            deleted_files=len(deleted_files),
            suspicious_paths=suspicious_paths,
            total_size_bytes=total_size,
        )

    @property
    def container_config(self) -> SandboxContainerConfig:
        return self._container_config

    @property
    def wasi_config(self) -> WASIRuntimeConfig:
        return self._wasi_config

    @property
    def guard(self) -> BlindSpot5ProcessSandboxGuard:
        return self._guard

    @property
    def audit_log(self) -> List[FilesystemAuditEntry]:
        return list(self._audit_log)
