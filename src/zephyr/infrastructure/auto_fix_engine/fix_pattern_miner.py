# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_pattern_miner
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-FEEDBACK_LOOP(feedback-loop)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只从成功修复学习;模式MUST持久化;频率MUST递增
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PatternMiningError
# [TESTS] tests/auto-fix-engine/test_fix_pattern_miner.py
# [A_module] module_id=MOD-INF_fix_pattern_miner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import json
import logging
import os
import sqlite3
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import FixAction, FixStatus
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)


class FixPatternMiner:
    def __init__(self, db_path: str = str(DB_PATH)) -> None:
        self._db_path = db_path
        self._pattern_cache: dict[str, dict[str, Any]] = {}
        self._ensure_db()

    def _ensure_db(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS fix_patterns "
                "(pattern_id TEXT PRIMARY KEY, action_type TEXT NOT NULL, dimension TEXT NOT NULL, "
                "frequency INTEGER NOT NULL DEFAULT 1, success_rate REAL NOT NULL DEFAULT 0.0, "
                "last_seen TEXT NOT NULL, pattern_data TEXT DEFAULT '{}')"
            )
            conn.commit()
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            conn.close()

    def mine(self, actions: list[FixAction]) -> list[dict[str, Any]]:
        new_patterns: list[dict[str, Any]] = []
        by_type: dict[str, list[FixAction]] = defaultdict(list)
        for action in actions:
            by_type[action.action_type].append(action)
        for action_type, type_actions in by_type.items():
            succeeded = [a for a in type_actions if a.status == FixStatus.COMPLETED]
            failed = [a for a in type_actions if a.status == FixStatus.FAILED]
            total = len(type_actions)
            success_rate = len(succeeded) / total if total > 0 else 0.0
            pattern_id = f"pattern_{action_type}"
            pattern = {
                "pattern_id": pattern_id,
                "action_type": action_type,
                "dimension": succeeded[0].metadata.get("dimension", "") if succeeded else "",
                "frequency": total,
                "success_rate": success_rate,
                "last_seen": datetime.now(UTC).isoformat(),
                "pattern_data": {
                    "total": total,
                    "succeeded": len(succeeded),
                    "failed": len(failed),
                    "common_targets": [a.target for a in succeeded[:5]],
                },
            }
            self._upsert_pattern(pattern)
            new_patterns.append(pattern)
        return new_patterns

    def get_patterns(self, dimension: str = "", min_frequency: int = 1) -> list[dict[str, Any]]:
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            if dimension:
                rows = conn.execute(
                    "SELECT pattern_id, action_type, dimension, frequency, success_rate, last_seen, pattern_data "
                    "FROM fix_patterns WHERE dimension=? AND frequency>=? ORDER BY frequency DESC",
                    (dimension, min_frequency),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT pattern_id, action_type, dimension, frequency, success_rate, last_seen, pattern_data "
                    "FROM fix_patterns WHERE frequency>=? ORDER BY frequency DESC",
                    (min_frequency,),
                ).fetchall()
            patterns = []
            for row in rows:
                patterns.append(
                    {
                        "pattern_id": row[0],
                        "action_type": row[1],
                        "dimension": row[2],
                        "frequency": row[3],
                        "success_rate": row[4],
                        "last_seen": row[5],
                        "pattern_data": json.loads(row[6]) if row[6] else {},
                    }
                )
            return patterns
        except Exception:
            return []
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()

    def predict_fix_type(self, target: str, dimension: str = "") -> str | None:
        patterns = self.get_patterns(dimension=dimension, min_frequency=2)
        best: dict[str, Any] | None = None
        for p in patterns:
            if best is None or p["success_rate"] > best["success_rate"]:
                best = p
        if best and best["success_rate"] > 0.5:
            return best["action_type"]
        return None

    def _upsert_pattern(self, pattern: dict[str, Any]) -> None:
        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            existing = conn.execute(
                "SELECT frequency, success_rate FROM fix_patterns WHERE pattern_id=?",
                (pattern["pattern_id"],),
            ).fetchone()
            if existing:
                new_freq = existing[0] + pattern["frequency"]
                new_rate = (existing[1] * existing[0] + pattern["success_rate"] * pattern["frequency"]) / new_freq
                conn.execute(
                    "UPDATE fix_patterns SET frequency=?, success_rate=?, last_seen=?, pattern_data=? WHERE pattern_id=?",
                    (
                        new_freq,
                        new_rate,
                        pattern["last_seen"],
                        json.dumps(pattern["pattern_data"], ensure_ascii=False),
                        pattern["pattern_id"],
                    ),
                )
            else:
                conn.execute(
                    "INSERT INTO fix_patterns (pattern_id, action_type, dimension, frequency, success_rate, last_seen, pattern_data) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        pattern["pattern_id"],
                        pattern["action_type"],
                        pattern["dimension"],
                        pattern["frequency"],
                        pattern["success_rate"],
                        pattern["last_seen"],
                        json.dumps(pattern["pattern_data"], ensure_ascii=False),
                    ),
                )
            conn.commit()
        except Exception as exc:
            logger.error("Failed to upsert pattern: %s", exc)
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()
