# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_loop_detector
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF-021 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackLoopDetector — 回滚循环检测器。

依据: 蓝图 MOD-INF-021 §7 Phase 2.2 + §6.2 B6 + D-021-10

同一 (task_id, gate_id) 组合触发回滚 >3次/h -> 暂停 agent 自动回滚权限 + DEFER_TO_HUMAN。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: rollback_loop_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RollbackLoopDetector
#   name_en: RollbackLoopDetector
#   intro: class RollbackLoopDetector 源码 L77-L182
#   desc: 公共方法（定义序）: log_path, project_root, record, check, is_blocked, get_blocked_combinations；源码 L77-L182
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: RollbackLoopDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path


@dataclass
class LoopAlert:
    task_id: str
    gate_id: str
    count_in_hour: int
    blocked_until: str
    escalated: bool


@dataclass
class LoopDetectorResult:
    loop_detected: bool
    alerts: list[LoopAlert]


class RollbackLoopDetector:
    MAX_ROLLBACKS_PER_HOUR: int = 3
    MAX_ROLLBACKS_PER_DAY: int = 10
    BLOCK_DURATION_MINUTES: int = 60
    LOG_FILE: str = ".zephyr/rollback_loop_log.jsonl"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._log_path = self._project_root / self.LOG_FILE

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def log_path(self):
        """只读：log_path（Stage 4 公共化）。"""
        return self._log_path

    @log_path.setter
    def log_path(self, value):
        """写入：log_path（Stage 4 公共化）。"""
        self._log_path = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def record(self, task_id: str, gate_id: str, success: bool = False) -> None:
        entry = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "task_id": task_id,
            "gate_id": gate_id,
            "success": success,
        }
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def check(self) -> LoopDetectorResult:
        alerts: list[LoopAlert] = []
        now = datetime.now(UTC)

        counts_1h: dict[tuple[str, str], int] = defaultdict(int)
        counts_24h: dict[tuple[str, str], int] = defaultdict(int)

        if not self._log_path.exists():
            return LoopDetectorResult(loop_detected=False, alerts=[])

        try:
            with open(self._log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        ts = datetime.fromisoformat(entry["timestamp_utc"])
                        tid = entry["task_id"]
                        gid = entry["gate_id"]
                        key = (tid, gid)

                        if now - ts <= timedelta(hours=1):
                            counts_1h[key] += 1
                        if now - ts <= timedelta(hours=24):
                            counts_24h[key] += 1
                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue
        except FileNotFoundError:
            pass

        for (tid, gid), count in counts_1h.items():
            if count > self.MAX_ROLLBACKS_PER_HOUR:
                block_until = now + timedelta(minutes=self.BLOCK_DURATION_MINUTES)
                alerts.append(
                    LoopAlert(
                        task_id=tid,
                        gate_id=gid,
                        count_in_hour=count,
                        blocked_until=block_until.isoformat(),
                        escalated=count > self.MAX_ROLLBACKS_PER_DAY,
                    )
                )

        loop_detected = len(alerts) > 0
        return LoopDetectorResult(
            loop_detected=loop_detected,
            alerts=alerts,
        )

    def is_blocked(self, task_id: str, gate_id: str) -> bool:
        result = self.check()
        for alert in result.alerts:
            if alert.task_id == task_id and alert.gate_id == gate_id:
                return True
        return False

    def get_blocked_combinations(self) -> dict[str, list[str]]:
        result = self.check()
        blocked: dict[str, list[str]] = defaultdict(list)
        for alert in result.alerts:
            blocked[alert.task_id].append(alert.gate_id)
        return dict(blocked)
