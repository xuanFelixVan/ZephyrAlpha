# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §8.3 + §16 Phase 2b
# [MODULE] zephyr.security.adversarial_validation.game_day_scheduler
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.adversarial_validation.game_day_runner; zephyr.shared.io.paths
# [CONSUMERS] cli.py; CI/CD workflow
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事件主触发(git push webhook->per_commit)+CI定时兜底(cron_daily/weekly/monthly由外部CI调用trigger); MUST NOT schedule overlapping game days; 状态文件锚定REPO_ROOT
# [MODIFY-GUARD] Adding triggers MUST update _TRIGGER_MAP; scheduler state persisted to data/red_blue/scheduler-state.yaml
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ScheduleConflictError on overlapping schedules; SchedulerNotInitializedError if state file missing
# [TESTS] tests/red_blue/test_game_day_scheduler.py
# [A_module] module_id=MOD-INF-030 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: state_path 参数
#   fields: 参数 state_path（无注解）
#   code: game_day_scheduler.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① GameDayScheduler
#   name_en: GameDayScheduler
#   intro: 游戏日调度状态机（事件主触发 + CI 定时兜底）。
#   desc: 游戏日调度状态机（事件主触发 + CI 定时兜底）。 触发模型（原则②创造必全自动）： - 主触发=事件：git push webhook → handle_webhook("p…；公共方法（定义序）: state,…
#   inputs: state_path
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: GameDayScheduler
#   downstream: cli.py; CI/CD workflow
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

from zephyr.security.adversarial_validation.game_day_runner import GameDayFrequency, GameDayRunner
from zephyr.shared.io.paths import REPO_ROOT

logger = logging.getLogger(__name__)

__all__: list[str] = ["GameDayScheduler", "ScheduleConflictError"]

# 锚定 REPO_ROOT（对齐同包 commit_trigger.py 范式；原 CWD 相对路径会在非仓根
# 工作目录下派生第二状态文件——状态真源分裂）。
_STATE_PATH: Path = REPO_ROOT / "data" / "red_blue" / "scheduler-state.yaml"
# 5.79.2 修复：原模块级 os.makedirs 在 import 时执行，在只读文件系统/受限沙箱中 import 直接抛 PermissionError。
# 延迟到 GameDayScheduler.__init__ 中创建。

_TRIGGER_MAP: dict[str, list[GameDayFrequency]] = {
    "git_push": [GameDayFrequency.PER_COMMIT],
    "cron_daily": [GameDayFrequency.DAILY],
    "cron_weekly": [GameDayFrequency.WEEKLY],
    "cron_monthly": [GameDayFrequency.MONTHLY],
    "full_cycle": [
        GameDayFrequency.PER_COMMIT,
        GameDayFrequency.DAILY,
        GameDayFrequency.WEEKLY,
        GameDayFrequency.MONTHLY,
    ],
}
# Stage 4 公共化：公共别名（primary），_TRIGGER_MAP 保留为向后兼容别名。
TRIGGER_MAP: dict[str, list[GameDayFrequency]] = _TRIGGER_MAP


class ScheduleConflictError(RuntimeError):
    error_code = "ZA-SC-0005"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class GameDayScheduler:
    """游戏日调度状态机（事件主触发 + CI 定时兜底）。

    触发模型（原则②创造必全自动）：
      - 主触发=事件：git push webhook → handle_webhook("push") → trigger("git_push")
        （事件入口真源=同包 commit_trigger.py）。
      - 兜底=CI 定时：外部 CI 定期 job 调用 trigger("cron_daily"/"cron_weekly"/
        "cron_monthly")；should_run/next_scheduled 仅做到期判定，不含任何进程内
        定时循环（2026-08-17 治本删除 auto_start sleep-loop 守护与 flag-only
        幽灵事件订阅面——前者属原则②禁止的进程内定时调度器，后者伪装已接线
        构成幻觉源；Phase 2b 事件订阅须按 tests/safety 两 skip 文件的
        EventBus 契约施工并注册 boot_hooks）。
    """

    def __init__(
        self,
        state_path: Path | None = None,
    ) -> None:
        self._state_path: Path = state_path or _STATE_PATH
        # 5.79.2 修复：延迟到 __init__ 创建目录，避免 import 时副作用。
        os.makedirs(self._state_path.parent, exist_ok=True)
        self._runner = GameDayRunner()
        self._state: dict = self._load_state()

    # ── Stage 4 公共化（2026-07-28）：properties + 公共方法 ──
    # 消除 tests/safety/test_game_day_scheduler.py 中 68 处私有成员访问。
    # 消除 tests/safety/test_phase_manager_integration.py 中 36 处私有成员访问。

    @property
    def state(self) -> dict:
        """读写：调度器持久化状态（Stage 4 公共化，返回可变 dict 引用）。"""
        return self._state

    @state.setter
    def state(self, value: dict) -> None:
        self._state = value

    @property
    def state_path(self) -> Path:
        """只读：state_path（Stage 4 公共化）。"""
        return self._state_path

    @state_path.setter
    def state_path(self, value):
        """写入：state_path（Stage 4 公共化）。"""
        self._state_path = value

    def trigger(self, trigger_name: str) -> list[dict]:
        frequencies = _TRIGGER_MAP.get(trigger_name, [])
        if not frequencies:
            logger.warning("unknown_trigger trigger=%s", trigger_name)
            return []

        if self.is_running():
            raise ScheduleConflictError(f"Cannot trigger {trigger_name}: game day already running")

        results: list[dict] = []
        self.set_running(True)

        try:
            for freq in frequencies:
                if self.should_run(freq):
                    result = self._runner.run_game_day(freq)
                    self.record_run(freq, result)
                    results.append(
                        {
                            "frequency": freq.value,
                            "total": result.total_attacks,
                            "blocked": result.passed,
                            "bypassed": result.bypasses,
                        }
                    )
        finally:
            self.set_running(False)

        return results

    def handle_webhook(self, event_type: str, payload: dict | None = None) -> list[dict]:
        if event_type == "push":
            return self.trigger("git_push")
        elif event_type == "schedule":
            return self.trigger("cron_daily")
        elif event_type == "full_cycle":
            return self.trigger("full_cycle")
        else:
            return self.trigger(event_type)

    def last_run(self, frequency: GameDayFrequency) -> datetime | None:
        last = self._state.get("last_runs", {}).get(frequency.value)
        if last:
            return datetime.fromisoformat(last)
        return None

    def next_scheduled(self, frequency: GameDayFrequency) -> datetime | None:
        last = self.last_run(frequency)
        if last is None:
            return datetime.now(UTC)

        intervals: dict[str, timedelta] = {
            "per_commit": timedelta(minutes=5),
            "daily": timedelta(days=1),
            "weekly": timedelta(days=7),
            "monthly": timedelta(days=30),
        }
        interval = intervals.get(frequency.value, timedelta(days=1))
        return last + interval

    def should_run(self, frequency: GameDayFrequency) -> bool:
        """判断指定频率是否到达下次运行时间（Stage 4 公共化，primary）。"""
        next_run = self.next_scheduled(frequency)
        if next_run is None:
            return True
        return datetime.now(UTC) >= next_run

    def _should_run(self, frequency: GameDayFrequency) -> bool:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.should_run(frequency)

    def is_running(self) -> bool:
        """查询调度器是否正在运行游戏日（Stage 4 公共化，primary）。"""
        return self._state.get("running", False)

    def _is_running(self) -> bool:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.is_running()

    def set_running(self, running: bool) -> None:
        """设置运行标志并持久化（Stage 4 公共化，primary）。"""
        self._state["running"] = running
        self._state["updated_at"] = datetime.now(UTC).isoformat()
        self.save_state()

    def _set_running(self, running: bool) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        self.set_running(running)

    def record_run(self, frequency: GameDayFrequency, result) -> None:
        """记录单次游戏日运行结果到 last_runs 与 history（Stage 4 公共化，primary）。"""
        if "last_runs" not in self._state:
            self._state["last_runs"] = {}
        self._state["last_runs"][frequency.value] = datetime.now(UTC).isoformat()

        if "history" not in self._state:
            self._state["history"] = []
        self._state["history"].append(
            {
                "frequency": frequency.value,
                "timestamp": datetime.now(UTC).isoformat(),
                "total": result.total_attacks,
                "blocked": result.passed,
                "bypassed": result.bypasses,
            }
        )
        self._state["history"] = self._state["history"][-50:]
        self.save_state()

    def _record_run(self, frequency: GameDayFrequency, result) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        self.record_run(frequency, result)

    def _load_state(self) -> dict:
        if not self._state_path.exists():
            default = {"running": False, "last_runs": {}, "history": [], "updated_at": ""}
            self._save_state_raw(default)
            return default
        with open(self._state_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_state(self) -> None:
        """持久化当前状态到 state_path（Stage 4 公共化，primary）。"""
        self._save_state_raw(self._state)

    def _save_state(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        self.save_state()

    def _save_state_raw(self, state: dict) -> None:
        tmp = self._state_path.with_suffix(f".{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            yaml.safe_dump(state, f, allow_unicode=True, default_flow_style=False)
        os.replace(tmp, self._state_path)
