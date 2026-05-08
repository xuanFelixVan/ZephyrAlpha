"""MOD-INF-026 §28 — 紧急旁路协议。

BypassManager: inventory_override.yaml → 强制 GREEN + 自动过期 24h。
对标 K8s Admission Webhook 的 emergency bypass + CI/CD 的 deployment freeze override。
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class BypassState(BaseModel):
    enabled: bool = False
    reason: str = ""
    expires_at: Optional[datetime] = None
    is_expired: bool = False


class BypassManager:
    OVERRIDE_FILENAME = "inventory_override.yaml"
    MAX_BYPASS_HOURS = 24
    _DEFAULT_OVERRIDE_PATH = Path("config/capacity") / OVERRIDE_FILENAME

    def __init__(self, project_root: Optional[Path] = None) -> None:
        if project_root:
            self._override_path = project_root / "config" / "capacity" / self.OVERRIDE_FILENAME
        else:
            self._override_path = self._DEFAULT_OVERRIDE_PATH

    def get_bypass_state(self) -> BypassState:
        if not self._override_path.exists():
            return BypassState()

        import yaml
        try:
            data = yaml.safe_load(self._override_path.read_text(encoding="utf-8"))
        except Exception:
            return BypassState()

        if data is None or not isinstance(data, dict):
            return BypassState()

        activated_str = data.get("activated_at")
        expires_str = data.get("expires_at")

        activated_at: Optional[datetime] = None
        expires_at_cfg: Optional[datetime] = None

        if activated_str:
            try:
                activated_at = datetime.fromisoformat(str(activated_str))
            except ValueError:
                pass

        if expires_str:
            try:
                expires_at_cfg = datetime.fromisoformat(str(expires_str))
            except ValueError:
                pass

        now = datetime.now(timezone.utc)

        if expires_at_cfg and now > expires_at_cfg:
            return BypassState(is_expired=True)

        if activated_at and (now - activated_at).total_seconds() > self.MAX_BYPASS_HOURS * 3600:
            return BypassState(is_expired=True)

        enabled = data.get("enabled", True)
        reason = data.get("reason", "")

        return BypassState(
            enabled=bool(enabled),
            reason=reason,
            expires_at=expires_at_cfg or (activated_at.replace(tzinfo=timezone.utc) if activated_at and activated_at.tzinfo else None),
        )

    def is_bypass_active(self) -> bool:
        state = self.get_bypass_state()
        return state.enabled and not state.is_expired

    def write_override(self, reason: str, activated_by: str, hours: int = 24) -> Path:
        import yaml
        now = datetime.now(timezone.utc)
        override = {
            "enabled": True,
            "reason": reason,
            "activated_by": activated_by,
            "activated_at": now.isoformat(),
            "expires_at": (now + timedelta(hours=hours)).isoformat(),
            "notification_channel": "dashboard",
        }

        self._override_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = f"{self._override_path}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.dump(override, f, allow_unicode=True)
        os.replace(tmp, str(self._override_path))

        return self._override_path

    def remove_override(self) -> bool:
        if self._override_path.exists():
            self._override_path.unlink()
            return True
        return False
