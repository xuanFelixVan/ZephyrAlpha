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
# [A_module] module_id=MOD-INF-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: db_path 参数
#   fields: 参数 db_path（无注解）
#   code: fix_health_check.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① FixHealthCheck
#   name_en: FixHealthCheck
#   intro: class FixHealthCheck 源码 L62-L143
#   desc: 公共方法（定义序）: check_config, db_path, check_db, check；源码 L62-L143
#   inputs: db_path
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FixHealthCheck
#   downstream: engine.py;__main__.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixHealthReport
from zephyr.shared.io.paths import DB_PATH
from zephyr.shared.io.sqlite_factory import get_db_connection

logger = logging.getLogger(__name__)


class FixHealthCheck:
    def __init__(self, db_path: str | Path = DB_PATH) -> None:
        self._db_path = db_path

    def check_config(self) -> bool:
        """公共接口：check_config（Stage 4 公共化）。"""
        return self._check_config()

    @property
    def db_path(self):
        """只读：db_path（Stage 4 公共化）。"""
        return self._db_path

    @db_path.setter
    def db_path(self, value):
        """写入：db_path（Stage 4 公共化）。"""
        self._db_path = value

    def check_db(self) -> bool:
        """公共接口：check_db（Stage 4 公共化）。"""
        return self._check_db()

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
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            conn = get_db_connection(self._db_path)
            conn.execute("SELECT 1")
            conn.close()
            return True
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return False
