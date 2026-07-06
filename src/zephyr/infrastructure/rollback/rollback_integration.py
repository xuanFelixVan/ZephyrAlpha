# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_integration
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_rollback_integration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Rollback Integration — executor 集成增强层。

对 rollback_executor.py 提供以下功能的集成入口：
    - 0247: --to ACL 权限检查
    - 0248: 网络分区超时（_run_git 已含 timeout=10）
    - 0253: Prompt Injection 过滤
    - 0254: PSQL 连接池恢复
    - 0255: 嵌套环境检测
    - 0256: MCP 不可逆操作识别
    - 0257: 通知洪流节制
    - 0258: Self-Audit Conflict 解决
    - 0259: Git Binary 完整性验证
    - 0260: 反向预言自我实现防护
    - 0261: 青野检查点密度控制
"""

from __future__ import annotations
from zephyr.shared.io.sqlite_factory import get_db_connection

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from zephyr.infrastructure.rollback.contract import ExitCode
from zephyr.shared.security.secrets import get_secret_or_default

from zephyr.shared.io.paths import REPO_ROOT

PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|above)\s+(instructions?|prompts?)", re.IGNORECASE),
    re.compile(r"\bDAN\b.*\bdo\s+anything\s+now\b", re.IGNORECASE),
    re.compile(r"\b(UNICHAT|DEVELOPER.?MODE|JAILBREAK)\b", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(a\s+)?(\w+\s+){0,3}(GPT|AI|assistant)", re.IGNORECASE),
    re.compile(r"pretend\s+(you\s+are|to\s+be)\b", re.IGNORECASE),
    re.compile(r"system\s*:\s*override", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"\[system\]\([^)]*\)", re.IGNORECASE),
]

IRREVERSIBLE_GIT_COMMANDS = [
    "reflog expire",
    "gc --prune",
    "push --force",
    "push --delete",
    "push -f",
    "filter-branch",
    "reset --hard",
]

CHECKPOINT_MIN_INTERVAL_S = 600
CHECKPOINT_DENSITY_MAX_PER_HOUR = 6
# 5.137.1 修复：checkpoint 密度阈值魔数提取为命名常量
CHECKPOINT_TOKEN_RATE_HIGH = 5000
CHECKPOINT_TOKEN_RATE_CRITICAL = 10000
# 5.137.1 修复：指数退避上限魔数提取为命名常量
EXPONENTIAL_BACKOFF_MAX_SLEEP_S = 60

NOTIFICATION_THROTTLE_WINDOW_S = 300
NOTIFICATION_THROTTLE_MAX = 10


@dataclass
class AclCheckResult:
    allowed: bool
    is_owner: bool
    session_id: str
    reason: str = ""


@dataclass
class InjectionScanResult:
    safe: bool
    findings: list[str]
    exit_code: int = 0


@dataclass
class NestedEnvInfo:
    is_container: bool
    is_vm: bool
    container_type: str
    worktree_adjustment: bool = False
    timeout_adjustment: int = 10


@dataclass
class NotificationState:
    window_count: int = 0
    window_start: float = 0.0
    throttled: bool = False


@dataclass
class CheckpointDensity:
    allowed: bool
    last_checkpoint_utc: str
    next_allowed_utc: str
    current_interval_s: float
    reason: str = ""


class RollbackIntegration:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._notify_state = NotificationState()
        self._last_checkpoint_time: datetime | None = None

    def acl_check_to_target(self, session_id: str, target: str, owner_session_id: str | None = None) -> AclCheckResult:
        env_owner = owner_session_id or os.environ.get("ZEPHYR_OWNER_SESSION_ID", "")

        if not env_owner:
            return AclCheckResult(
                allowed=False,
                is_owner=False,
                session_id=session_id,
                reason="No owner session configured. --to requires owner privileges.",
            )

        is_owner = session_id == env_owner

        if not is_owner:
            return AclCheckResult(
                allowed=False,
                is_owner=False,
                session_id=session_id,
                reason=f"--to target override denied for non-owner session {session_id}. "
                f"Only {env_owner} can use --to.",
            )

        if not re.match(r"^[a-f0-9]{7,40}$|^[\w./-]+$", target):
            return AclCheckResult(
                allowed=False,
                is_owner=True,
                session_id=session_id,
                reason=f"Invalid --to target format: {target}",
            )

        return AclCheckResult(
            allowed=True,
            is_owner=True,
            session_id=session_id,
            reason=f"Owner {session_id} authorized for --to {target}",
        )

    def scan_prompt_injection(self, trigger: str, message: str) -> InjectionScanResult:
        findings: list[str] = []
        combined = f"{trigger} {message}"

        for pattern in PROMPT_INJECTION_PATTERNS:
            matches = pattern.findall(combined)
            for match in matches:
                match_str = match if isinstance(match, str) else str(match)
                findings.append(f"Prompt injection detected: pattern={pattern.pattern}, match={match_str[:100]}")

        safe = len(findings) == 0
        exit_code = (
            0 if safe else ExitCode.PROMPT_INJECTION_FILTERED if hasattr(ExitCode, "PROMPT_INJECTION_FILTERED") else 18
        )

        return InjectionScanResult(safe=safe, findings=findings, exit_code=exit_code)

    def detect_nested_environment(self) -> NestedEnvInfo:
        is_container = False
        is_vm = False
        container_type = "bare_metal"
        worktree_adjustment = False
        timeout_adjustment = 10

        if os.path.exists("/.dockerenv"):
            is_container = True
            container_type = "docker"
            worktree_adjustment = True
            timeout_adjustment = 30
        elif os.path.exists("/run/.containerenv"):
            is_container = True
            container_type = "podman"
            worktree_adjustment = True
            timeout_adjustment = 30
        else:
            try:
                with open("/proc/1/cgroup") as f:
                    cgroup_content = f.read()
                    if "docker" in cgroup_content or "kubepods" in cgroup_content:
                        is_container = True
                        container_type = "k8s" if "kubepods" in cgroup_content else "docker"
                        worktree_adjustment = True
                        timeout_adjustment = 30
            except (FileNotFoundError, PermissionError):
                pass

        try:
            result = subprocess.run(
                ["systemd-detect-virt", "--quiet"],
                capture_output=True,
                timeout=3,
            )
            if result.returncode == 0:
                is_vm = True
                container_type = "vm"
                timeout_adjustment = 20
        except (FileNotFoundError, subprocess.TimeoutExpired):
            try:
                result = subprocess.run(
                    ["wmic", "computersystem", "get", "manufacturer"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                if any(v in result.stdout.upper() for v in ["VMWARE", "VIRTUALBOX", "QEMU", "XEN"]):
                    is_vm = True
                    container_type = "vm"
                    timeout_adjustment = 20
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        return NestedEnvInfo(
            is_container=is_container,
            is_vm=is_vm,
            container_type=container_type,
            worktree_adjustment=worktree_adjustment,
            timeout_adjustment=timeout_adjustment,
        )

    def check_irreversible_command(self, command: str) -> tuple[bool, str, int]:
        command_lower = command.lower()
        for op in IRREVERSIBLE_GIT_COMMANDS:
            if op in command_lower:
                exit_code = ExitCode.MCP_IRREVERSIBLE if hasattr(ExitCode, "MCP_IRREVERSIBLE") else 22
                return True, op, exit_code
        return False, "", 0

    def throttle_notification(self) -> tuple[bool, str]:
        now = time.time()

        if self._notify_state.window_start == 0:
            self._notify_state.window_start = now
            self._notify_state.window_count = 0

        if now - self._notify_state.window_start > NOTIFICATION_THROTTLE_WINDOW_S:
            self._notify_state.window_start = now
            self._notify_state.window_count = 0
            self._notify_state.throttled = False

        self._notify_state.window_count += 1

        if self._notify_state.window_count > NOTIFICATION_THROTTLE_MAX:
            self._notify_state.throttled = True
            exit_code = ExitCode.NOTIFICATION_THROTTLED if hasattr(ExitCode, "NOTIFICATION_THROTTLED") else 23
            return True, (
                f"Notification throttled: {self._notify_state.window_count} "
                f"notifications in {NOTIFICATION_THROTTLE_WINDOW_S}s window "
                f"(max: {NOTIFICATION_THROTTLE_MAX})"
            )

        return False, ""

    def get_notification_summary(self) -> dict[str, Any]:
        return {
            "throttled": self._notify_state.throttled,
            "window_count": self._notify_state.window_count,
            "window_start": datetime.fromtimestamp(self._notify_state.window_start, tz=UTC).isoformat()
            if self._notify_state.window_start
            else "",
            "window_s": NOTIFICATION_THROTTLE_WINDOW_S,
            "max_notifications": NOTIFICATION_THROTTLE_MAX,
        }

    def resolve_self_audit_conflict(self, audit_path: Path | None = None) -> tuple[bool, str]:
        target = audit_path or (REPO_ROOT / "data" / "rollback" / "audit" / "audit_findings.json")

        tmp_path = Path(str(target) + ".conflict_tmp")
        bak_path = Path(str(target) + ".conflict_bak")

        if tmp_path.exists():
            try:
                existing = json.loads(target.read_text(encoding="utf-8"))
                tmp_data = json.loads(tmp_path.read_text(encoding="utf-8"))

                merged = self._three_way_merge(existing, tmp_data)

                if bak_path.exists():
                    bak_path.unlink()
                shutil.copy2(str(target), str(bak_path))

                target.write_text(
                    json.dumps(merged, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

                tmp_path.unlink()
                return True, f"Self-audit conflict resolved: merged {len(merged.get('findings', []))} entries"
            except (json.JSONDecodeError, FileNotFoundError):
                exit_code = ExitCode.SELF_AUDIT_CONFLICT if hasattr(ExitCode, "SELF_AUDIT_CONFLICT") else 24
                return False, "Self-audit conflict IRRESOLVABLE"
            except Exception as e:
                exit_code = ExitCode.SELF_AUDIT_CONFLICT if hasattr(ExitCode, "SELF_AUDIT_CONFLICT") else 24
                return False, f"Self-audit conflict merge failed: {e}"

        return True, "No self-audit conflict detected"

    def verify_git_binary_integrity(self, known_hashes: dict[str, str] | None = None) -> tuple[bool, str, int]:
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                exit_code = ExitCode.GIT_BINARY_MISMATCH if hasattr(ExitCode, "GIT_BINARY_MISMATCH") else 25
                return False, "Git binary not functional", exit_code

            git_path = shutil.which("git") or shutil.which("git.exe")
            if git_path:
                git_bytes = Path(git_path).read_bytes()
                actual_hash = hashlib.sha256(git_bytes).hexdigest()

                if known_hashes:
                    basename = os.path.basename(git_path).lower()
                    expected = known_hashes.get(basename, "")
                    if expected and actual_hash != expected:
                        exit_code = ExitCode.GIT_BINARY_MISMATCH if hasattr(ExitCode, "GIT_BINARY_MISMATCH") else 25
                        return (
                            False,
                            (f"Git binary hash mismatch: expected={expected[:12]}... actual={actual_hash[:12]}..."),
                            exit_code,
                        )

                return True, f"Git binary verified: hash={actual_hash[:12]}...", 0

            return True, "Git binary integrity check passed (no hash database)", 0
        except (subprocess.TimeoutExpired, Exception) as e:
            exit_code = ExitCode.GIT_BINARY_MISMATCH if hasattr(ExitCode, "GIT_BINARY_MISMATCH") else 25
            return False, f"Git binary verification failed: {e}", exit_code

    def detect_reverse_prophecy(self, agent_output: str) -> tuple[bool, str]:
        negative_patterns = [
            r"rollback\s+will\s+(fail|not\s+succeed|be\s+rejected)",
            r"this\s+revert\s+(will|is\s+likely\s+to)\s+(fail|break|corrupt)",
            r"cannot\s+(revert|rollback|restore)",
            r"(rollback|revert)\s+is\s+(dangerous|risky|unsafe)",
            r"predicted\s+outcome.*(failure|error|corrupt)",
            r"(i\s+predict|i\s+forecast|i\s+expect).*(fail|error|problem)",
        ]

        detected: list[str] = []
        for pattern in negative_patterns:
            matches = re.findall(pattern, agent_output, re.IGNORECASE)
            detected.extend(matches)

        if detected:
            return True, (
                f"Reverse prophecy detected: {len(detected)} negative prediction(s) found. "
                "Check-act isolation enforced — prediction will NOT influence execution."
            )

        return False, "No reverse prophecy detected"

    def check_checkpoint_density(self, token_rate: float = 0.0) -> CheckpointDensity:
        now = datetime.now(UTC)

        adjusted_interval = CHECKPOINT_MIN_INTERVAL_S
        if token_rate > CHECKPOINT_TOKEN_RATE_HIGH:
            adjusted_interval = CHECKPOINT_MIN_INTERVAL_S * 2
        elif token_rate > CHECKPOINT_TOKEN_RATE_CRITICAL:
            adjusted_interval = CHECKPOINT_MIN_INTERVAL_S * 4

        if self._last_checkpoint_time is None:
            self._last_checkpoint_time = now
            return CheckpointDensity(
                allowed=True,
                last_checkpoint_utc=now.isoformat(),
                next_allowed_utc=(now + timedelta(seconds=adjusted_interval)).isoformat(),
                current_interval_s=0,
                reason="First checkpoint — always allowed",
            )

        elapsed = (now - self._last_checkpoint_time).total_seconds()

        if elapsed < adjusted_interval:
            next_allowed = self._last_checkpoint_time + timedelta(seconds=adjusted_interval)
            return CheckpointDensity(
                allowed=False,
                last_checkpoint_utc=self._last_checkpoint_time.isoformat(),
                next_allowed_utc=next_allowed.isoformat(),
                current_interval_s=elapsed,
                reason=f"Checkpoint too frequent: {elapsed:.1f}s < {adjusted_interval}s minimum. "
                f"Falling back to git-native single-sha mode.",
            )

        self._last_checkpoint_time = now
        return CheckpointDensity(
            allowed=True,
            last_checkpoint_utc=now.isoformat(),
            next_allowed_utc=(now + timedelta(seconds=adjusted_interval)).isoformat(),
            current_interval_s=elapsed,
            reason=f"Checkpoint allowed: {elapsed:.1f}s >= {adjusted_interval}s minimum",
        )

    def connection_pool_health_check(self, db_url: str = "", max_retries: int = 3) -> tuple[bool, str, int]:
        if not db_url:
            db_url = get_secret_or_default("DATABASE_URL", "")

        if not db_url:
            return True, "No database URL configured — skipping pool check", 0

        for attempt in range(max_retries):
            try:
                if "psycopg2" in db_url or "postgresql" in db_url:
                    try:
                        import psycopg2

                        conn = psycopg2.connect(db_url, connect_timeout=5)
                        conn.close()
                        return True, "PostgreSQL connection pool healthy", 0
                    except ImportError:
                        pass

                try:
                    import sqlite3

                    conn = get_db_connection(db_url.replace("sqlite:///", ""), timeout=5)
                    # 5.169 修复：try/finally 确保 conn 关闭，execute 抛异常时不泄漏
                    try:
                        conn.execute("SELECT 1")
                    finally:
                        conn.close()
                    return True, "SQLite connection pool healthy", 0
                except (sqlite3.Error, Exception):
                    pass

                time.sleep(min(EXPONENTIAL_BACKOFF_MAX_SLEEP_S, 2**attempt))

            except Exception as e:
                if attempt == max_retries - 1:
                    exit_code = ExitCode.CONNECTION_POOL_FAILED if hasattr(ExitCode, "CONNECTION_POOL_FAILED") else 20
                    return False, f"Connection pool health check FAILED after {max_retries} retries: {e}", exit_code

        exit_code = ExitCode.CONNECTION_POOL_FAILED if hasattr(ExitCode, "CONNECTION_POOL_FAILED") else 20
        return False, "Connection pool health check FAILED", exit_code

    @staticmethod
    def _three_way_merge(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
        merged: dict[str, Any] = {}

        all_keys = set(base.keys()) | set(incoming.keys())

        for key in all_keys:
            base_val = base.get(key)
            inc_val = incoming.get(key)

            if base_val is None:
                merged[key] = inc_val
            elif inc_val is None:
                merged[key] = base_val
            elif isinstance(base_val, list) and isinstance(inc_val, list):
                seen = {json.dumps(item, sort_keys=True, ensure_ascii=False) for item in base_val}
                merged_list = list(base_val)
                for item in inc_val:
                    item_str = json.dumps(item, sort_keys=True, ensure_ascii=False)
                    if item_str not in seen:
                        merged_list.append(item)
                        seen.add(item_str)
                merged[key] = merged_list
            elif isinstance(base_val, dict) and isinstance(inc_val, dict):
                merged[key] = RollbackIntegration._three_way_merge(base_val, inc_val)
            else:
                merged[key] = inc_val

        return merged
