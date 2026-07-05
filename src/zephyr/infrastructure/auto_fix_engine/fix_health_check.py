# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_health_check
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;__main__.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] MUST检测所有关键组件;unhealthy MUST阻止新修复
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HealthCheckError
# [TESTS] tests/auto-fix-engine/test_fix_health_check.py
# [A_module] module_id=MOD-INF_fix_health_check | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixHealthReport
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)


class FixHealthCheck:
    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self._db_path = db_path

    def check(
        self,
        fixers: dict[str, Any] | None = None,
        budget_ok: bool = True,
        cascade_active: bool = False,
        dead_letter_count: int = 0,
        approval_queue_size: int = 0,
    ) -> FixHealthReport:
        fixer_status: dict[str, str] = {}
        if fixers:
            for name, fixer in fixers.items():
                try:
                    if hasattr(fixer, "scan"):
                        fixer_status[name] = "healthy"
                    else:
                        fixer_status[name] = "degraded"
                except Exception:
                    fixer_status[name] = "unhealthy"
        db_accessible = self._check_db()
        config_loaded = self._check_config()
        healthy = (
            budget_ok
            and not cascade_active
            and dead_letter_count < 100
            and db_accessible
            and config_loaded
            and all(v == "healthy" for v in fixer_status.values())
        )
        return FixHealthReport(
            healthy=healthy,
            fixers=fixer_status,
            budget_ok=budget_ok,
            cascade_active=cascade_active,
            dead_letter_count=dead_letter_count,
            approval_queue_size=approval_queue_size,
            db_accessible=db_accessible,
            config_loaded=config_loaded,
        )

    def _check_db(self) -> bool:
        try:
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self._db_path)
            conn.execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False

    def _check_config(self) -> bool:
        try:
            config_path = Path(__file__).parent / "auto_fix_config.yaml"
            if not config_path.exists():
                return False
            content = config_path.read_text(encoding="utf-8")
            if not content.strip():
                return False
            return True
        except Exception:
            return False
