# [BLUEPRINT] MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §ARCH-WORKTREE-LIFECYCLE-001
# [MODULE] zephyr.gov_enforcement.rule_bridge.worktree_lifecycle
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.session_worktree; zephyr.governance.audit.git_performance_monitor_reconciler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 状态记录持久化到 .runtime/worktree_lifecycle/；转换必须合法；幂等
# [MODIFY-GUARD] 状态语义变更需同步 worktree_state_machine.yaml + 测试
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] session_not_found->WorktreeLifecycleError; invalid_transition->WorktreeTransitionError(->WorktreeLifecycleError)
# [TESTS] tests/governance/rule_bridge/test_worktree_lifecycle.py
# [A_module] module_id=MOD-GOV_ENFORCEMENT_WORKTREE_LIFECYCLE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

WorktreeLifecycle — worktree 生命周期状态机（5态 + 8转换）

#ARCH-WORKTREE-LIFECYCLE-001 治本（2026-07-21）：
原 SessionManager（MOD-INF-039，5态：idle/active/paused/completed/archived）是死代码
（生产引用=0，仅测试覆盖）。本模块继承其状态机基础设施，但状态语义重新设计为
worktree 实际生命周期：

    created → active → idle → quarantined → swept
                    ↘ active (resume)

状态语义：
  - created: session_worktree_start 完成，worktree 已创建（待施工）
  - active: AI 正在施工（Edit/Write/commit 进行中）
  - idle: 施工暂停（等待用户反馈/外部依赖）
  - quarantined: sweep 发现 stale + 未合并提交，分支 tip 保存到 refs/quarantine/<sid>
  - swept: worktree 已物理清理（资源释放完成，记录归档）

与 session_worktree.py 的关系：
  本模块是"状态记录层"，session_worktree.py 是"操作执行层"。
  session_worktree_start/commit/merge/abort/sweep 可选调用本模块记录状态历史，
  本模块不强制 session_worktree.py 必须调用——但 reconciler/监控 SHOULD 通过本模块查询状态。

持久化：
  JSON 文件，存于 .runtime/worktree_lifecycle/<session_id>.json。
  不依赖 DB，保持轻量；reconciler 通过扫描该目录发现异常状态。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: session_id 与目标状态
#   fields: session_id 字符串 + target_state（created/active/idle/quarantined/swept）+ detail 备注
#   code: transition(session_id, target_state) L203
# - id: I2
#   name: 状态机配置 YAML
#   fields: transitions 合法转换表 + timeout_rules 超时规则
#   code: config/worktree_state_machine.yaml L70
# - id: I3
#   name: 生命周期记录 JSON
#   fields: state / created_at / last_transition_at / history 转换历史
#   code: .runtime/worktree_lifecycle/{session_id}.json L71
# 层: 算法
# - id: A1
#   name_zh: ① 加载状态机配置
#   name_en: load_state_machine_config / _load_config
#   intro: 从 YAML 读合法转换表和超时规则，文件缺失就用内置默认转换表兜底
#   desc: yaml.safe_load 读取；FileNotFoundError 时告警并留空，后续 _is_valid_transition 回退 _DEFAULT_TRANSITIONS
#   inputs: I2
#   outputs: transitions + timeout_rules
# - id: A2
#   name_zh: ② 注册新 session
#   name_en: WorktreeLifecycle.register
#   intro: 给新 session 建初始状态 created 的记录，已存在就直接返回当前状态
#   desc: 幂等：读到已有记录则返回其 state；否则写 {state:created, created_at, history:[None→created]} JSON
#   inputs: I1 I3
#   outputs: WorktreeState.CREATED
# - id: A3
#   name_zh: ③ 合法转换校验
#   name_en: _is_valid_transition
#   intro: 对照转换表检查 from→to 是否合法，swept 是终态不许再转
#   desc: 优先查 config transitions 逐条匹配 from/to；config 缺失时查内置 _DEFAULT_TRANSITIONS frozenset 表（L331）
#   inputs: A1
#   outputs: True/False
#   invariant: swept 为终态（出边为空集）
# - id: A4
#   name_zh: ④ 执行状态转换
#   name_en: WorktreeLifecycle.transition
#   intro: 校验通过后改写状态、盖时间戳、追加历史，非法就抛 WorktreeTransitionError
#   desc: RLock 保护；未注册抛 WorktreeLifecycleError；非法转换抛 WorktreeTransitionError(ZA-TR-0018)；写回 JSON 记录
#   inputs: I1 I3 A3
#   outputs: 目标 WorktreeState
#   invariant: 转换必须合法；记录持久化到 .runtime/worktree_lifecycle/
# - id: A5
#   name_zh: ⑤ 隔离到期检查
#   name_en: check_quarantine_expiry
#   intro: 扫 quarantined 状态的 session，超过 72 小时没动就列入清理名单
#   desc: elapsed_h=(now-last_transition_at)/3600 ≥ QUARANTINE_TTL_HOURS(72) → 加入 expired 列表
#   inputs: I3
#   outputs: 过期 session_id 列表
# - id: A6
#   name_zh: ⑥ swept 记录归档清理
#   name_en: cleanup_swept
#   intro: 把已 swept 终态的记录物理删除，最多一次清 100 条
#   desc: list_by_state(SWEPT) 取前 max_count 条，逐条 _delete_record 删 JSON 文件
#   inputs: I3
#   outputs: 清理条数
# 层: 输出
# - id: O1
#   name_zh: 当前状态与转换历史
#   name_en: WorktreeState / history list
#   intro: get_state/get_history/list_by_state 返回状态与轨迹，供 reconciler 发现异常 worktree
#   downstream: session_worktree；git_performance_monitor_reconciler（# [CONSUMERS] 头）
# - id: O2
#   name_zh: 隔离到期名单
#   name_en: expired session list
#   intro: 超 72h 的 quarantined session 列表，供 sweep 流程物理清理
#   downstream: session_worktree sweep 流程（内部使用）
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# I3 --> A2
# A1 --> A3
# I1 --> A4
# I3 --> A4
# A3 --> A4
# I3 --> A5
# I3 --> A6
# A2 --> A4
# A4 --> O1
# A5 --> O2
# A6 --> O1
"""

from __future__ import annotations

import json
import logging
import time
from enum import Enum, unique
from pathlib import Path
from threading import RLock
from typing import Any

import yaml

from zephyr.shared.foundation.errors import SessionError
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

__all__ = [
    "WorktreeLifecycle",
    "WorktreeLifecycleError",
    "WorktreeState",
    "WorktreeTransitionError",
    "load_state_machine_config",
]

_logger = logging.getLogger(__name__)

DEFAULT_STATE_MACHINE_PATH: Path = REPO_ROOT / "config" / "worktree_state_machine.yaml"
DEFAULT_RECORDS_DIR: Path = REPO_ROOT / ".runtime" / "worktree_lifecycle"
QUARANTINE_TTL_HOURS: int = 72


class WorktreeLifecycleError(SessionError):
    """worktree lifecycle 通用错误。"""


class WorktreeTransitionError(WorktreeLifecycleError):
    """非法状态转换。"""

    error_code = "ZA-TR-0018"


@unique
class WorktreeState(str, Enum):
    """worktree 5态状态机。"""

    CREATED = "created"
    ACTIVE = "active"
    IDLE = "idle"
    QUARANTINED = "quarantined"
    SWEPT = "swept"


def load_state_machine_config(path: Path | None = None) -> dict[str, Any]:
    """从 worktree_state_machine.yaml 加载状态机定义。"""
    resolved = path or DEFAULT_STATE_MACHINE_PATH
    if not resolved.exists():
        raise FileNotFoundError(f"worktree_state_machine.yaml not found: {resolved}")
    with resolved.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


class WorktreeLifecycle:
    """worktree 生命周期管理器。

    从 config/worktree_state_machine.yaml 加载状态定义和转换规则，
    在运行时强制执行合法转换，记录每个 session 的状态历史。

    Usage::

        wl = WorktreeLifecycle()
        wl.register("sess-abc")
        wl.transition("sess-abc", "active")
        wl.transition("sess-abc", "swept")
    """

    def __init__(
        self,
        config_path: Path | None = None,
        records_dir: Path | None = None,
    ) -> None:
        self._config_path = config_path or DEFAULT_STATE_MACHINE_PATH
        self._records_dir = records_dir or DEFAULT_RECORDS_DIR
        self._lock = RLock()
        self._transitions: list[dict[str, Any]] = []
        self._timeout_rules: list[dict[str, Any]] = []
        self._load_config()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def config_path(self):
        """只读：config_path（Stage 4 公共化）。"""
        return self._config_path

    @config_path.setter
    def config_path(self, value):
        """写入：config_path（Stage 4 公共化）。"""
        self._config_path = value

    def _load_config(self) -> None:
        try:
            config = load_state_machine_config(self._config_path)
        except FileNotFoundError:
            _logger.warning("worktree_state_machine.yaml not found, using defaults")
            return
        self._transitions = config.get("transitions", [])
        self._timeout_rules = config.get("timeout_rules", [])

    # ------------------------------------------------------------------
    # 持久化辅助
    # ------------------------------------------------------------------

    def _record_path(self, session_id: str) -> Path:
        return self._records_dir / f"{session_id}.json"

    def _read_record(self, session_id: str) -> dict[str, Any] | None:
        path = self._record_path(session_id)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            _logger.warning("failed to read record %s: %s", path, e)
            return None

    def _write_record(self, session_id: str, record: dict[str, Any]) -> None:
        self._records_dir.mkdir(parents=True, exist_ok=True)
        path = self._record_path(session_id)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    def _delete_record(self, session_id: str) -> None:
        path = self._record_path(session_id)
        if path.exists():
            try:
                path.unlink()
            except OSError as e:
                _logger.warning("failed to delete record %s: %s", path, e)

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------

    def register(self, session_id: str) -> WorktreeState:
        """注册新 session，初始状态 = CREATED。幂等：已存在则返回当前状态。"""
        with self._lock:
            existing = self._read_record(session_id)
            if existing is not None:
                return WorktreeState(existing.get("state", WorktreeState.CREATED.value))
            record = {
                "session_id": session_id,
                "state": WorktreeState.CREATED.value,
                "created_at": now_utc().timestamp(),
                "last_transition_at": now_utc().timestamp(),
                "history": [{"from": None, "to": WorktreeState.CREATED.value, "at": now_utc().timestamp()}],
            }
            self._write_record(session_id, record)
        _logger.info("WorktreeLifecycle: registered %s", session_id)
        return WorktreeState.CREATED

    def transition(
        self,
        session_id: str,
        target_state: str,
        detail: str | None = None,
    ) -> WorktreeState:
        """执行状态转换。失败抛 WorktreeTransitionError。"""
        with self._lock:
            record = self._read_record(session_id)
            if record is None:
                raise WorktreeLifecycleError(
                    "session not registered",
                    details={"session_id": session_id},
                )
            current = WorktreeState(record["state"])
            target = WorktreeState(target_state)
            if not self._is_valid_transition(current, target):
                raise WorktreeTransitionError(
                    f"Transition {current.value} -> {target.value} not allowed",
                    details={
                        "session_id": session_id,
                        "from": current.value,
                        "to": target.value,
                    },
                )
            record["state"] = target.value
            record["last_transition_at"] = now_utc().timestamp()
            record["history"].append(
                {
                    "from": current.value,
                    "to": target.value,
                    "at": now_utc().timestamp(),
                    "detail": detail,
                }
            )
            self._write_record(session_id, record)
        _logger.info("WorktreeLifecycle: %s %s -> %s", session_id, current.value, target.value)
        return target

    def get_state(self, session_id: str) -> WorktreeState:
        """查询当前状态。session 不存在抛 WorktreeLifecycleError。"""
        with self._lock:
            record = self._read_record(session_id)
            if record is None:
                raise WorktreeLifecycleError(
                    "session not registered",
                    details={"session_id": session_id},
                )
            return WorktreeState(record["state"])

    def get_history(self, session_id: str) -> list[dict[str, Any]]:
        """查询转换历史。"""
        with self._lock:
            record = self._read_record(session_id)
            if record is None:
                raise WorktreeLifecycleError(
                    "session not registered",
                    details={"session_id": session_id},
                )
            return list(record.get("history", []))

    def list_by_state(self, state: WorktreeState | str) -> list[str]:
        """按状态列出所有 session_id。"""
        if isinstance(state, WorktreeState):
            target = state.value
        else:
            target = state
        result: list[str] = []
        if not self._records_dir.exists():
            return result
        with self._lock:
            for path in self._records_dir.glob("*.json"):
                try:
                    record = json.loads(path.read_text(encoding="utf-8"))
                    if record.get("state") == target:
                        result.append(record.get("session_id", path.stem))
                except (json.JSONDecodeError, OSError):
                    continue
        return result

    def check_quarantine_expiry(self) -> list[str]:
        """检查 quarantine 是否超过 72h，返回需清理的 session_id 列表。"""
        now = now_utc().timestamp()
        expired: list[str] = []
        for sid in self.list_by_state(WorktreeState.QUARANTINED):
            record = self._read_record(sid)
            if record is None:
                continue
            last_transition = record.get("last_transition_at", 0)
            elapsed_h = (now - last_transition) / 3600
            if elapsed_h >= QUARANTINE_TTL_HOURS:
                expired.append(sid)
        return expired

    def cleanup_swept(self, max_count: int = 100) -> int:
        """清理 SWEPT 状态的记录（归档完成），返回清理数量。"""
        cleaned = 0
        sids = self.list_by_state(WorktreeState.SWEPT)
        for sid in sids[:max_count]:
            with self._lock:
                self._delete_record(sid)
            cleaned += 1
        return cleaned

    def _is_valid_transition(self, current: WorktreeState, target: WorktreeState) -> bool:
        """校验转换是否合法（按 config 的 transitions 表）。"""
        if not self._transitions:
            # config 缺失时使用内置默认转换表
            return _DEFAULT_TRANSITIONS.get(current, set()).__contains__(target)
        for t in self._transitions:
            if t.get("from") == current.value and t.get("to") == target.value:
                return True
        return False

    @property
    def active_sessions(self) -> list[str]:
        """返回当前 ACTIVE 状态的 session 列表。"""
        return self.list_by_state(WorktreeState.ACTIVE)


# 内置默认转换表（config 缺失时的 fallback）
_DEFAULT_TRANSITIONS: dict[WorktreeState, frozenset[WorktreeState]] = {
    WorktreeState.CREATED: frozenset({WorktreeState.ACTIVE, WorktreeState.SWEPT}),
    WorktreeState.ACTIVE: frozenset(
        {
            WorktreeState.IDLE,
            WorktreeState.SWEPT,
            WorktreeState.QUARANTINED,
        }
    ),
    WorktreeState.IDLE: frozenset(
        {
            WorktreeState.ACTIVE,
            WorktreeState.QUARANTINED,
            WorktreeState.SWEPT,
        }
    ),
    WorktreeState.QUARANTINED: frozenset(
        {
            WorktreeState.ACTIVE,
            WorktreeState.SWEPT,
        }
    ),
    WorktreeState.SWEPT: frozenset(),  # 终态
}
