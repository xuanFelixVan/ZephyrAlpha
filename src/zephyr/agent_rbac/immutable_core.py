# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.immutable_core

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
L0 Immutable Core — 硬编码不可变保护区

MOD-INF-018 §2.1  D-018-04

L0 是最底层的兜底防线——硬编码在代码中，不可被任何 YAML/配置文件覆盖。
即使权限系统其他层全部失效，L0 也要保证核心护栏不垮。

设计原则:
  - 保护路径列表 (protected_paths) —— 硬编码，不可通过配置修改
  - 永远禁止操作 (always_blocked) —— 即使 rbac_roles.yaml 说 allow 也不行
  - OS ACL 双重兜底 —— 文件系统级保护作为物理防线
  - 完整性自检 —— verify_immutable_core_integrity() 检测代码自身是否被篡改
  - 最先执行、不可覆盖、不可绕过
"""

import fnmatch
import hashlib
import os
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[3]


PROTECTED_PATHS: list[str] = [
    ".git/**",
    "src/zephyr/agent_rbac/**",
    "docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md",
    "AGENTS.md",
    "docs/01_policies_and_standards/governance/**",
    "src/zephyr/gates/_registry.yaml",
    ".pre-commit-config.yaml",
    "src/zephyr/llm_security/process_sandbox.py",
    "data/telemetry/audit/**",
    "**/.env*",
    ".env*",
    "pyproject.toml",
    ".github/workflows/**",
    "docker-compose*.yml",
    "config/nav_table_mapping.yaml",
    "scripts/governance/_shared/**",
    "docs/01_policies_and_standards/ai/GOV-AI-001.md",
    "config/rbac_roles.yaml",
    ".trae/rules/**",
    ".cursorrules",
    "session-logs/**",
    "scripts/lock_files.py",
    ".vscode/tasks.json",
    ".trae/tasks.json",
    "launch.json",
]

ALWAYS_BLOCKED_OPERATIONS: list[str] = [
    "modify_immutable_core",
    "delete_audit_logs",
    "modify_self_permissions",
    "disable_kill_switch",
    "shell_true_execution",
    "circumvent_gate_engine",
    "write_to_protected_paths",
    "spawn_new_agent_unsanctioned",
    "forge_agent_identity",
    "modify_environment_variables",
    "os_acl_bypass",
    "synthesize_restricted_data",
    "cascade_failure_trigger",
    "circumvent_micro_verification",
    "self_disable_sandbox",
    "false_completion",
    "memory_poisoning",
    "permanent_file_deletion",
]


@dataclass
class IntegrityResult:
    intact: bool
    checksum: str = ""
    tampered_items: list[str] = field(default_factory=list)
    detail: str = ""


class ImmutableCore:
    """L0 不可变核心——硬编码保护路径和禁止操作的守卫"""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self._project_root = project_root or PROJECT_ROOT
        self._protected_paths = list(PROTECTED_PATHS)
        self._always_blocked = list(ALWAYS_BLOCKED_OPERATIONS)
        self._source_hash = self._compute_source_hash()

    @property
    def protected_paths(self) -> list[str]:
        return list(self._protected_paths)

    @property
    def always_blocked(self) -> list[str]:
        return list(self._always_blocked)

    def is_protected_path(self, path: str | Path) -> bool:
        target = str(path).replace("\\", "/")
        target_rel = target
        try:
            target_rel = os.path.relpath(str(path), str(self._project_root)).replace("\\", "/")
        except ValueError:
            pass

        for pattern in self._protected_paths:
            if fnmatch.fnmatch(target_rel, pattern):
                return True
            if fnmatch.fnmatch(target, pattern):
                return True
        return False

    def is_always_blocked(self, operation: str) -> bool:
        op = operation.strip().lower().replace(" ", "_").replace("-", "_")
        return op in self._always_blocked

    def verify_immutable_core_integrity(self) -> IntegrityResult:
        current_hash = self._compute_source_hash()
        if current_hash != self._source_hash:
            return IntegrityResult(
                intact=False,
                checksum=current_hash,
                tampered_items=["immutable_core.py source"],
                detail=f"Source hash mismatch: expected {self._source_hash[:16]}..., got {current_hash[:16]}...",
            )
        return IntegrityResult(intact=True, checksum=current_hash)

    def verify_protected_paths_exist(self) -> list[str]:
        missing: list[str] = []
        resolved: set[str] = set()
        for pattern in self._protected_paths:
            if pattern.startswith("**/"):
                resolved_path = self._project_root / pattern[3:]
            else:
                resolved_path = self._project_root / pattern

            search_base = resolved_path
            if "*" in pattern:
                try:
                    import glob as glob_mod
                    matches = glob_mod.glob(str(resolved_path), recursive=True)
                    if matches:
                        continue
                except Exception:
                    pass

            if not os.path.exists(str(search_base)):
                if str(search_base) not in resolved:
                    missing.append(pattern)
                    resolved.add(str(search_base))

        return missing

    def verify_os_acl(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        critical_dirs = [
            ".git/",
            "src/zephyr/agent_rbac/",
            "data/telemetry/audit/",
        ]
        for d in critical_dirs:
            target = self._project_root / d
            if not target.exists():
                results[d] = False
                continue
            if platform.system() == "Windows":
                results[d] = self._check_windows_acl(target)
            else:
                results[d] = self._check_unix_immutable(target)
        return results

    def _check_windows_acl(self, path: Path) -> bool:
        try:
            test_path = path / "_immutable_write_test.tmp"
            test_path.write_text("immutable_core_acl_test", encoding="utf-8")
            test_path.unlink()
            return True
        except (OSError, PermissionError):
            return False

    def _check_unix_immutable(self, path: Path) -> bool:
        try:
            result = os.stat(path).st_flags
            return False
        except AttributeError:
            try:
                import subprocess
                proc = subprocess.run(
                    ["lsattr", "-d", str(path)],
                    capture_output=True, text=True, timeout=5,
                )
                return "i" in proc.stdout
            except Exception:
                return False

    def _compute_source_hash(self) -> str:
        source_file = Path(__file__)
        try:
            content = source_file.read_text(encoding="utf-8")
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
        except Exception:
            return hashlib.sha256(b"").hexdigest()

    def verify_static_constants_integrity(self) -> IntegrityResult:
        if len(self._protected_paths) < 22:
            return IntegrityResult(
                intact=False,
                tampered_items=[f"protected_paths count: {len(self._protected_paths)} < 22"],
                detail="Protected paths list has been reduced below minimum threshold",
            )
        if len(self._always_blocked) < 14:
            return IntegrityResult(
                intact=False,
                tampered_items=[f"always_blocked count: {len(self._always_blocked)} < 14"],
                detail="Always blocked operations list has been reduced below minimum threshold",
            )
        return IntegrityResult(intact=True)

    def should_cold_start_lock(self) -> bool:
        rbac_roles_paths = [
            self._project_root / "config" / "rbac_roles.yaml",
            self._project_root / "rbac_roles.yaml",
        ]
        for p in rbac_roles_paths:
            if p.exists():
                return False
        return True


_immutable_core_instance: Optional[ImmutableCore] = None


def get_immutable_core() -> ImmutableCore:
    global _immutable_core_instance
    if _immutable_core_instance is None:
        _immutable_core_instance = ImmutableCore()
    return _immutable_core_instance


RbacConfig = ImmutableCore
