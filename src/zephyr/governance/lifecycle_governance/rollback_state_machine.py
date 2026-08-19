# [BLUEPRINT] MOD-GOV-045 | docs/03_modules/_domain_governance/rollback_state_machine/blueprint.md | §
# [MODULE] zephyr.governance.lifecycle_governance.rollback_state_machine
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.state_store
# [CONSUMERS] zephyr.governance.lifecycle_governance.paper_live_transition
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 自动迁移只能单向更保守(to_idx>from_idx);无自动恢复(恢复须人工+双人复核+RCA);fail-closed读取失败/无持久化默认SOFT_HALT;Hysteresis trip!=recover;自动降级须累计>=30笔交易(P0事件绕过)
# [MODIFY-GUARD] tests/governance/trading/test_degradation_rollback_fsm.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PermissionError(恢复缺RCA已写+双人复核);ValueError(恢复目标非更宽松态/UNWINDING仓位未平)
# [TESTS] tests/governance/trading/test_degradation_rollback_fsm.py
# [A_module] module_id=MOD-GOV-045 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: governance
# category: lifecycle_governance
# status: active
# created: "2026-08-17"
# ---

"""D_GOVERNANCE — 53 号 §3.8 降级/回退 5 态状态机（#ARCH-QUANT-003 代码落地）。

定位（方案 C 按维度各一真源，2026-08-15 Owner 裁定）：
  降级维度（快变量/每 tick 评估/自动触发/单向更保守）唯一真源 = 本模块五态
  （NORMAL/THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING）；
  阶段维度（慢变量/晋级仪式/人工审批）唯一真源 = 同包 paper_live_transition.py
  三阶段。两机唯一耦合点 = 阶段晋级前置"当前降级姿态=NORMAL"。

  注意：src/zephyr/infrastructure/rollback/rollback_state_machine.py 为回滚步骤
  编排机（RollbackStep/StepStatus），与本模块语义完全不同，仅同名巧合
  （#ARCH-QUANT-003 裁定原文）。

核心约束（53 号 §3.8 伪代码逐行落地）：
  ① 状态只能单向"更保守"迁移（无自动恢复）——自动化的方向只能是更保守，
    绝不能自动恢复并继续下单（quant67 2026-05-01 熔断状态机）。
  ② 恢复须人工 + 双人复核 + RCA 已写（缺一 PermissionError）。
  ③ fail-closed：状态读取失败/无持久化默认 SOFT_HALT——kill switch 停错代价
    < 不停代价（与 circuit breaker fail-open 职责区分，53 号 L567 裁定）。
  ④ Hysteresis 防抖动：trip 与 recover 阈值不同（recover 仅作人工恢复参考，
    不参与自动迁移）。
  ⑤ 最小样本地板：自动降级须累计 ≥30 笔交易（对齐 AlphaFactory G2.2 统计地板），
    P0 事件绕过样本地板。

A 股 T+1 适配：SOFT_HALT = REDUCING 态（仅减仓不新建，只卖不买，符合交收规则）；
UNWINDING 仅对 T-1 及之前持仓生效（当日买入无法卖出），故 UNWINDING→NORMAL
须 position_flat=True。

状态持久化：复用 zephyr.shared.state_store.JsonStateStore（#ARCH-QUANT-002
Crash-only 状态外部化承载层，同包先例 default_risk_validator KillSwitch 状态）——
进程 crash/重启后熔断姿态存活。本模块只消费 JsonStateStore 公开接口
（save/load 三分语义），不碰实现内部。

SSoT: #ARCH-QUANT-003 (architecture_issue_registry.yaml) +
docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/53_simulation_live_path.md §3.8

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 每 tick 风险指标
#   fields: intraday_dd/daily_loss/reject_rate/circuit_breaker/p0_event/reject_rate_duration_s
#   code: evaluate_rollback(metrics)
# - id: I2
#   name: 当前姿态与累计样本量
#   fields: current: RollbackState + trade_count: int
#   code: evaluate_rollback(current, trade_count)
# - id: I3
#   name: 人工恢复三要素
#   fields: rca_written/dual_approval/position_flat（bool 三件套）
#   code: recover(rca_written, dual_approval, position_flat)
# - id: I4
#   name: 持久化姿态记录
#   fields: state/reason/trade_count/updated_at（JsonStateStore 命名空间 rollback_state）
#   code: load_persisted_state(store) / safe_read_state(persisted)
# 层: 算法
# - id: A1
#   name_zh: ① 样本地板闸门
#   name_en: sample floor gate
#   intro: 累计 <30 笔且无 P0 事件 → 不触发自动降级（AlphaFactory G2.2 统计地板，防小样本噪声误触发）
#   desc: trade_count < _MIN_SAMPLE_TRADES and not p0_event → return current
#   inputs: I1, I2
#   outputs: 放行/拦截判定
#   invariant: P0 事件绕过地板
# - id: A2
#   name_zh: ② 单向更保守梯子评估
#   name_en: evaluate_rollback one-way ladder
#   intro: 每 tick 单步：NORMAL→THROTTLED（soft 超限）→SOFT_HALT（hard 超限/daily_loss>2.5%/持续 60s）→HARD_HALT（daily_loss≥3%/熔断/P0）
#   desc: _breach 按 _HYSTERESIS[key].trip×mult 严格大于判定；HARD_HALT→UNWINDING 不自动
#   inputs: I1, I2
#   outputs: 新状态（等于 current 或更保守态）
#   invariant: to_idx > from_idx；无自动恢复路径
# - id: A3
#   name_zh: ③ 人工恢复三件套裁决
#   name_en: recover manual adjudication
#   intro: 权限（RCA+双人复核缺一 PermissionError）→ 方向（非更宽松 ValueError）→ 仓位（UNWINDING 未平 ValueError）
#   desc: 检查序固定：权限先于方向先于仓位；UNWINDING→NORMAL 须 position_flat（T+1 仅 T-1 持仓可平）
#   inputs: I3
#   outputs: 目标状态
#   invariant: 恢复只能向更宽松态
# - id: A4
#   name_zh: ④ fail-closed 姿态读取
#   name_en: safe_read_state fail-closed
#   intro: 读取失败/无持久化/畸形/损坏一律 SOFT_HALT（停错代价 < 不停代价）
#   desc: StateCorruptError/None/KeyError/ValueError 全收敛 SOFT_HALT；与 circuit breaker fail-open 职责相反
#   inputs: I4
#   outputs: RollbackState（永不为 None）
#   invariant: 任何异常路径不抛给调用方，默认停
# 层: 输出
# - id: O1
#   name_zh: 降级姿态（RollbackState）
#   name_en: degradation posture
#   intro: 供执行层按姿态撤单/阻断/减仓/平仓；供 paper_live_transition 晋级前置校验
#   downstream: zephyr.governance.lifecycle_governance.paper_live_transition.check_promotion_allowed
# - id: O2
#   name_zh: 持久化姿态载荷
#   name_en: persisted posture payload
#   intro: persist_state 原子写 JsonStateStore（pid-tmp+os.replace），重启存活
#   downstream: JsonStateStore（#ARCH-QUANT-002 承载层）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I3 --> A3
# I4 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O1
# A2 --> O2
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Final

from zephyr.shared.state_store import JsonStateStore, StateCorruptError

__all__: Final = [
    "RollbackState",
    "STATE_NAMESPACE",
    "evaluate_rollback",
    "load_persisted_state",
    "persist_state",
    "recover",
    "safe_read_state",
]


class RollbackState(str, Enum):
    """降级/回退五态（53 号 §3.8 五态表，枚举序=保守程度序）。"""

    NORMAL = "NORMAL"  # 正常运行
    THROTTLED = "THROTTLED"  # 1 级：节流（TWAP/VWAP 加宽 + 降订单速率）
    SOFT_HALT = "SOFT_HALT"  # 2-3 级：撤单+阻断 = REDUCING 态（仅减仓不新建）
    HARD_HALT = "HARD_HALT"  # 3 级：完全静默，持仓保留等待人工评估
    UNWINDING = "UNWINDING"  # 4 级：Flatten（T+1 仅对 T-1 持仓生效）


# 单向迁移矩阵：只能 to_idx > from_idx（更保守）；恢复走专用 recover() 须人工
_AUTO_TRANSITIONS: Final = {
    # (from, to): 触发判定函数名
    (RollbackState.NORMAL, RollbackState.THROTTLED): "soft_breach",
    (RollbackState.THROTTLED, RollbackState.SOFT_HALT): "hard_breach",
    (RollbackState.SOFT_HALT, RollbackState.HARD_HALT): "p0_or_circuit_breaker",
    # HARD_HALT → UNWINDING 须人工 + 双人复核，不在自动迁移中
}

# Hysteresis 阈值（trip / recover）——防抖动
_HYSTERESIS: Final = {
    "intraday_dd": {"trip": 0.01, "recover": 0.003},  # 1% trip / 0.3% recover
    "daily_loss": {"trip": 0.03, "recover": 0.00},  # 3% trip / 0% recover
    "reject_rate": {"trip": 0.01, "recover": 0.005},  # 1% trip / 0.5% recover
}
_MIN_SAMPLE_TRADES: Final = 30  # AlphaFactory G2.2 统计地板，避免小样本噪声误触发

# JsonStateStore 命名空间（单条状态记录，"最新一条即真源"）
STATE_NAMESPACE: Final = "rollback_state"


def evaluate_rollback(metrics: dict, current: RollbackState,
                      trade_count: int) -> RollbackState:
    """每 tick 调用：根据 metrics 决定是否单向降级。不做自动恢复。

    Args:
        metrics: {"intraday_dd", "daily_loss", "reject_rate",
                  "circuit_breaker": bool, "p0_event": bool, ...}
        current: 当前状态
        trade_count: 累计交易笔数（< _MIN_SAMPLE_TRADES 不触发，避免噪声）
    Returns:
        新状态（等于 current 或更保守态）
    """
    # 最小样本保护：交易笔数不足不触发自动降级（除非 P0 事件）
    if trade_count < _MIN_SAMPLE_TRADES and not metrics.get("p0_event"):
        return current

    if current == RollbackState.NORMAL:
        if _breach(metrics, "intraday_dd") or _breach(metrics, "reject_rate"):
            return RollbackState.THROTTLED

    if current == RollbackState.THROTTLED:
        if (_breach(metrics, "intraday_dd", mult=2.0)          # DD > 2%
                or _breach(metrics, "reject_rate", mult=5.0)    # reject > 5%
                or _breach(metrics, "daily_loss", mult=5.0 / 6.0)  # daily_loss > 2.5%（"接近 3%"，AI-R5 补齐 53 号迁移矩阵明文触发）
                or _persistent(metrics, "reject_rate", 60)):    # 持续 60s
            return RollbackState.SOFT_HALT  # = REDUCING 态（仅减仓不新建）

    if current == RollbackState.SOFT_HALT:
        if (_breach(metrics, "daily_loss")
                or metrics.get("circuit_breaker")
                or metrics.get("p0_event")):
            return RollbackState.HARD_HALT

    # HARD_HALT → UNWINDING 不自动，须人工 + 双人复核（见 recover()）
    return current


def recover(current: RollbackState, target: RollbackState,
            rca_written: bool, dual_approval: bool,
            position_flat: bool) -> RollbackState:
    """恢复（向更宽松态迁移）须人工 + 双人复核 + RCA 已写。

    Args:
        current: 当前状态（更保守）
        target: 目标状态（更宽松）
        rca_written: RCA 报告是否已写
        dual_approval: 是否双人复核通过
        position_flat: 仓位是否为 0（UNWINDING→NORMAL 必须）
    Returns:
        目标状态
    Raises:
        PermissionError: 未满足 RCA + 双人复核
        ValueError: 仓位未平 / 目标非更宽松态
    """
    if not (rca_written and dual_approval):
        raise PermissionError("恢复须 RCA 已写 + 双人复核（quant67 2026-05）")
    if _state_idx(target) >= _state_idx(current):
        raise ValueError("恢复只能向更宽松态迁移（单向保守原则）")
    if current == RollbackState.UNWINDING and not position_flat:
        raise ValueError("UNWINDING->NORMAL 须仓位=0（T+1：T-1 持仓已平）")
    return target


def safe_read_state(persisted: dict | None) -> RollbackState:
    """fail-closed：状态读取失败默认 SOFT_HALT（默认停，非默认允许）。

    kill switch 须 fail-closed（停错代价 < 不停代价）；
    circuit breaker 须 fail-open（停错代价 > 不停代价，误杀正常策略）。
    """
    try:
        if persisted is None:
            raise OSError("无持久化状态")
        return RollbackState(persisted["state"])
    except Exception:  # noqa: BLE001 — fail-closed 语义要求全捕获：任何读取异常一律默认 SOFT_HALT（53 号 §3.8 裁定）
        return RollbackState.SOFT_HALT  # fail-closed，默认进 REDUCING 态


# --- 状态持久化（JsonStateStore 公开接口消费，#ARCH-QUANT-002 承载层） ---
def persist_state(store: JsonStateStore, state: RollbackState, *,
                  reason: str = "", trade_count: int = 0) -> Path:
    """原子落盘当前降级姿态（含触发原因/样本量/时间戳，供 RCA 追溯）。"""
    payload = {
        "state": state.value,
        "reason": reason,
        "trade_count": trade_count,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    return store.save(STATE_NAMESPACE, payload)


def load_persisted_state(store: JsonStateStore) -> RollbackState:
    """启动加载降级姿态——fail-closed：损坏/缺失/畸形一律 SOFT_HALT。

    JsonStateStore.load 三分语义：None=无记录 / dict=记录 / StateCorruptError=损坏；
    本层按 kill switch 职责统一收敛为 fail-closed（53 号 §3.8 裁定）。
    """
    try:
        persisted = store.load(STATE_NAMESPACE)
    except StateCorruptError:
        return RollbackState.SOFT_HALT
    return safe_read_state(persisted)


# --- 辅助函数 ---
def _breach(metrics: dict, key: str, mult: float = 1.0) -> bool:
    return metrics.get(key, 0.0) > _HYSTERESIS[key]["trip"] * mult


def _persistent(metrics: dict, key: str, seconds: int) -> bool:
    return metrics.get(f"{key}_duration_s", 0) >= seconds


def _state_idx(s: RollbackState) -> int:
    return list(RollbackState).index(s)
