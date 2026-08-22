# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md
# [MODULE] zephyr.intelligence.reflexion.batch_runner
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.reflexion.reflection_schema; zephyr.intelligence.reflexion.roles; zephyr.intelligence.reflexion.l1_reflector
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 盘中零调用(09:30-15:00 工作日拒执行, fail-closed); 仅盘后离线窗口批量跑; 轨迹目录逐文件 json 读入, 坏文件跳过不阻断
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] IntradayReflectionForbidden(RuntimeError) — 盘中调用即抛
# [TESTS] tests/intelligence/test_reflexion_phase0.py
# [A_module] module_id=MOD-REFLEXION_AGENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""盘后批量反思入口 —— 12号文 §4.2 P0-4(手动+计划任务挂点)。

定位: 读当日任务轨迹目录(*.json, 每文件一条 Trajectory)→ 逐条 Evaluator 评估
→ L1 反思 → 反思记录批量落盘 data/brain/reflections/(jsonl)。

盘中零调用守卫(INVARIANTS, 12号文 §2.3 频率约束: 反思全部发生在盘后离线窗口,
不进盘中、不进下单热路径; §5-5 不做盘中实时反思): 工作日 09:30-15:00
(Asia/Shanghai) 调用 run_batch 即抛 IntradayReflectionForbidden。

轨迹文件格式(与 Trajectory 数据载体对称): {"task_id", "steps": [{"action",
"observation"}], "final_output", "succeeded", "error"}。

不做什么: 不做定时自触发(挂点由人/计划任务调用, 本件不含调度器); 不做盘中
实时反思; 不做反思触发裁决(归 Phase 1 ReflCtrl)。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

from zephyr.intelligence.reflexion.l1_reflector import L1Reflector
from zephyr.intelligence.reflexion.reflection_schema import (
    ReflectionRecord,
    ReflectionStore,
)
from zephyr.intelligence.reflexion.roles import (
    EvaluationReport,
    EvaluatorProtocol,
    RubricEvaluator,
    Trajectory,
    TrajectoryStep,
)

logger = logging.getLogger(__name__)

# A股盘中窗口(Asia/Shanghai, 固定 UTC+8 无夏令时; 不引 tzdata 依赖)
CN_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")
TRADING_START: time = time(9, 30)
TRADING_END: time = time(15, 0)


class IntradayReflectionForbidden(RuntimeError):
    """盘中调用反思批量入口(09:30-15:00 工作日)——fail-closed 拒执行。"""


def is_intraday(now: datetime | None = None) -> bool:
    """判定盘中窗口: 工作日(周一至五) 且 09:30 <= 当地时间 < 15:00。"""
    now = now or datetime.now(CN_TZ)
    local = now.astimezone(CN_TZ)
    if local.weekday() >= 5:  # 周末非盘中
        return False
    return TRADING_START <= local.time() < TRADING_END


def load_trajectory(path: Path) -> Trajectory:
    """读单个轨迹文件(json)为 Trajectory; 格式非法 → ValueError。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"轨迹文件非 dict: {path}")
    steps = [
        TrajectoryStep(
            step_index=idx,
            action=str(s.get("action", "")),
            observation=str(s.get("observation", "")),
        )
        for idx, s in enumerate(data.get("steps", []) or [])
    ]
    return Trajectory(
        task_id=str(data["task_id"]),
        steps=steps,
        final_output=str(data.get("final_output", "")),
        succeeded=bool(data.get("succeeded", False)),
        error=str(data.get("error", "") or ""),
    )


class BatchReflectionRunner:
    """盘后批量反思器: 轨迹目录 → 批量反思记录落盘。

    盘中零调用: 本类一切批量执行入口先过 _guard_off_hours(09:30-15:00 拒执行);
    任何盘中反思需求一律拒绝, 无例外开关(12号文 §2.3/§5-5)。
    """

    def __init__(
        self,
        store: ReflectionStore | None = None,
        evaluator: EvaluatorProtocol | None = None,
        reflector: L1Reflector | None = None,
    ) -> None:
        self._store = store or ReflectionStore()
        self._evaluator = evaluator or RubricEvaluator()
        self._reflector = reflector or L1Reflector()

    @staticmethod
    def _guard_off_hours(now: datetime | None) -> None:
        # 盘中零调用守卫(12号文 §2.3 频率约束+§5-5): 盘后离线窗口才允许反思
        if is_intraday(now):
            raise IntradayReflectionForbidden(
                "盘中零调用(INVARIANTS): 09:30-15:00 工作日禁止批量反思, "
                "请在盘后离线窗口执行(12号文 §2.3/§5-5)"
            )

    def run_batch(
        self,
        trajectory_dir: Path | str,
        now: datetime | None = None,
    ) -> list[ReflectionRecord]:
        """批量跑一个轨迹目录, 产出反思记录并落盘; 返回本次产出的记录。"""
        self._guard_off_hours(now)
        trajectory_dir = Path(trajectory_dir)
        records: list[ReflectionRecord] = []
        for path in sorted(trajectory_dir.glob("*.json")):
            try:
                trajectory = load_trajectory(path)
            except (ValueError, KeyError, json.JSONDecodeError) as exc:
                # 坏轨迹文件跳过不阻断批量(留痕日志, 不写反思记录——无有效轨迹不复盘)
                logger.warning("轨迹文件非法跳过: %s (%s)", path, exc)
                continue
            report: EvaluationReport = self._evaluator.evaluate(trajectory)
            record = self._reflector.reflect(
                trajectory, report, trajectory_ref=str(path)
            )
            self._store.append(record)
            records.append(record)
        return records
