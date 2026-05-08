"""死共享模块检测器 — shared/子模块无人使用 → DEAD."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone


class DeadModuleDetector:
    """死模块检测."""

    _DEAD_THRESHOLD_DAYS: int = 60

    def detect(self, shared_dir: str | Path, last_access: dict[str, str]) -> list[dict]:
        """检测30天+无人使用的shared模块."""
        sdir = Path(shared_dir)
        dead: list[dict] = []
        now = datetime.now(timezone.utc)

        for py_file in sdir.rglob("*.py"):
            key = str(py_file)
            last = last_access.get(key, "")
            if not last:
                dead.append({"module": key, "reason": "从未被引用"})
                continue
            try:
                dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
                if (now - dt.replace(tzinfo=timezone.utc)).days >= self._DEAD_THRESHOLD_DAYS:
                    dead.append({"module": key, "reason": f"超过{self._DEAD_THRESHOLD_DAYS}天未引用"})
            except ValueError:
                pass

        return dead
