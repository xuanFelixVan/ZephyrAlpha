# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.trust_anchor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.asset_inventory.__init__
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
# [A_module] module_id=MOD-INF_trust_anchor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""MOD-INF-026 §26 — 三重信任锚验证门 R20。

TripleTrustAnchorGate: Git clean + pytest green + audit continuity -> trust level。
对标 TUF 信任根模型 + Bitcoin "不信任，验证" 原则。
"""

import subprocess
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from zephyr.shared.io.paths import REPO_ROOT


class TrustLevel(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    BROKEN = "BROKEN"


class TrustAnchorResult(BaseModel):
    git_ok: bool = False
    test_ok: bool = False
    audit_ok: bool = False
    trust_level: TrustLevel = TrustLevel.BROKEN
    recommendation: str = ""
    checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TripleTrustAnchorGate:
    SELF_SRC_SEARCH = "src/zephyr/asset-inventory/"
    MAX_AUDIT_GAP_HOURS = 24
    MAX_CACHE_AGE_MINUTES = 5

    def __init__(self, project_root: Path) -> None:
        self._root = project_root
        self._cache: TrustAnchorResult | None = None

    def verify(self, force: bool = False) -> TrustAnchorResult:
        if not force and self._cache and self._cache_age_minutes() < self.MAX_CACHE_AGE_MINUTES:
            return self._cache

        git_ok = self._check_git_clean()
        test_ok = self._run_pytest()
        audit_ok = self._check_audit_continuity()

        trust_level = self._calculate_trust({
            "git_ok": git_ok,
            "test_ok": test_ok,
            "audit_ok": audit_ok,
        })

        self._cache = TrustAnchorResult(
            git_ok=git_ok,
            test_ok=test_ok,
            audit_ok=audit_ok,
            trust_level=trust_level,
            recommendation=self._recommend(trust_level),
        )
        return self._cache

    def _check_git_clean(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "--", self.SELF_SRC_SEARCH],
                capture_output=True,
                text=True,
                cwd=str(self._root),
                timeout=10,
            )
            return result.stdout.strip() == ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _run_pytest(self) -> bool:
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/asset-inventory/", "-q", "--tb=line", "-x"],
                capture_output=True,
                text=True,
                cwd=str(self._root),
                timeout=180,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_audit_continuity(self) -> bool:
        log_path = self._root / "data" / "reports" / "security_access_log.jsonl"
        if not log_path.exists():
            return True

        try:
            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            if not lines or all(l.strip() == "" for l in lines):
                return True

            if len(lines) < 2:
                return True

            import json

            timestamps: list[datetime] = []
            for line in lines:
                try:
                    obj = json.loads(line)
                    ts = obj.get("ts")
                    if ts:
                        timestamps.append(datetime.fromisoformat(ts))
                except (json.JSONDecodeError, ValueError):
                    continue

            if len(timestamps) < 2:
                return False

            timestamps.sort()
            max_gap_h = max(
                (timestamps[i + 1] - timestamps[i]).total_seconds() / 3600 for i in range(len(timestamps) - 1)
            )
            return max_gap_h < self.MAX_AUDIT_GAP_HOURS
        except (OSError, PermissionError):
            return False

    @staticmethod
    def _calculate_trust(checks: dict[str, bool]) -> TrustLevel:
        # 5.96.3 修复：原 (git_ok, test_ok, audit_ok) 三布尔参数蔓延，改为 dict 提升调用点可读性
        green_count = sum(checks.values())
        if green_count == 3:
            return TrustLevel.FULL
        if green_count == 2:
            return TrustLevel.PARTIAL
        return TrustLevel.BROKEN

    @staticmethod
    def _recommend(trust_level: TrustLevel) -> str:
        if trust_level is TrustLevel.FULL:
            return "盘点器完全可信——正常运行：索引更新、对账、自愈全部开启"
        if trust_level is TrustLevel.PARTIAL:
            return "盘点器部分可信——正常运行，Dashboard 标记 trust_level=partial"
        return "盘点器不可信——停止自愈，仅作只读扫描+报告"

    def _cache_age_minutes(self) -> float:
        if not self._cache:
            return float("inf")
        return (datetime.now(timezone.utc) - self._cache.checked_at).total_seconds() / 60


# ============================================================================
# SRC-0040: 从 emergency_bypass.py 合并 — BypassManager + BypassState
# ============================================================================

import os as _os
from datetime import UTC
from datetime import timedelta as _timedelta


class BypassState(BaseModel):
    """旁路状态——对标 K8s Admission Webhook 的 emergency bypass。"""

    enabled: bool = False
    reason: str = ""
    expires_at: datetime | None = None
    is_expired: bool = False


def _load_override_yaml(override_path: Path) -> dict | None:
    if not override_path.exists():
        return None
    import yaml
    try:
        data = yaml.safe_load(override_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if data is None or not isinstance(data, dict):
        return None
    return data


def _parse_override_datetime(value) -> datetime | None:
    if value:
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            pass
    return None


def _is_bypass_expired(
    activated_at: datetime | None,
    expires_at_cfg: datetime | None,
    max_hours: int,
) -> bool:
    now = datetime.now(UTC)
    if expires_at_cfg and now > expires_at_cfg:
        return True
    if activated_at and (now - activated_at).total_seconds() > max_hours * 3600:
        return True
    return False


class BypassManager:
    """紧急旁路协议——inventory_override.yaml -> 强制 GREEN + 自动过期 24h。"""

    OVERRIDE_FILENAME = "inventory_override.yaml"
    MAX_BYPASS_HOURS = 24
    _DEFAULT_OVERRIDE_PATH = (REPO_ROOT / "config" / "capacity") / OVERRIDE_FILENAME

    def __init__(self, project_root: Path | None = None) -> None:
        if project_root:
            self._override_path = project_root / "config" / "capacity" / self.OVERRIDE_FILENAME
        else:
            self._override_path = self._DEFAULT_OVERRIDE_PATH

    def get_bypass_state(self) -> BypassState:
        data = _load_override_yaml(self._override_path)
        if data is None:
            return BypassState()

        activated_at = _parse_override_datetime(data.get("activated_at"))
        expires_at_cfg = _parse_override_datetime(data.get("expires_at"))

        if _is_bypass_expired(activated_at, expires_at_cfg, self.MAX_BYPASS_HOURS):
            return BypassState(is_expired=True)

        enabled = data.get("enabled", True)
        reason = data.get("reason", "")

        return BypassState(
            enabled=bool(enabled),
            reason=reason,
            expires_at=expires_at_cfg
            or (activated_at.replace(tzinfo=UTC) if activated_at and activated_at.tzinfo else None),
        )

    def is_bypass_active(self) -> bool:
        state = self.get_bypass_state()
        return state.enabled and not state.is_expired

    def write_override(self, reason: str, activated_by: str, hours: int = 24) -> Path:
        import yaml

        now = datetime.now(UTC)
        override = {
            "enabled": True,
            "reason": reason,
            "activated_by": activated_by,
            "activated_at": now.isoformat(),
            "expires_at": (now + _timedelta(hours=hours)).isoformat(),
            "notification_channel": "dashboard",
        }

        self._override_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = f"{self._override_path}.{_os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(override, f, allow_unicode=True)
        _os.replace(tmp, str(self._override_path))

        return self._override_path

    def remove_override(self) -> bool:
        if self._override_path.exists():
            self._override_path.unlink()
            return True
        return False
