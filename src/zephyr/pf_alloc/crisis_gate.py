# [BLUEPRINT] MOD-PA-CRISIS-GATE | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md（depgraph design node 14753481）
# [MODULE] zephyr.pf_alloc.crisis_gate
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.pf_alloc.allocation_inputs(load_regime_input 复用,勿重写);
#   zephyr.pf_alloc.allocation_config; zephyr.infrastructure.database_service(writer 角色,禁裸 connect);
#   zephyr.data.alerter(告警复用,不重建告警系统); PyYAML(仅 config/crisis_gate.yaml 存在时);
#   schemas.categories.crisis_gate_log(表 DDL/INSERT 模板真源)
# [CONSUMERS] pipeline_events.run_pf_alloc_daily(L1 管线级,接线归总统筹,只调 crisis_block_check);
#   zephyr.pf_alloc.allocation_orchestrator(L2 裁决级); scripts/backtest/sim_paper_ledger(L3 账本级)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 危机判定**零新建内存态**（裁定 D2）：每次判定从 CH regime_snapshot_history 现读
#   （经 allocation_inputs.load_regime_input，天然持久，进程崩不丢）；
#   口径双档（裁定 D1）：crisis = dominant==r10（硬拦截）；warning = p_r10≥θ（缩额+告警）；
#   θ 真源=config/crisis_gate.yaml（O1 待 Owner 校准，缺省 0.5）；
#   无快照=fail-closed 平坦分布→normal **不误触**（验收③）；
#   crisis_block_check skip=True 时**不落 marker**（解除后同日可重放，由调用方保证）；
#   存量持仓不强平（强平语义归 ex_core 既有回撤阶梯，本闸只拦新增，workbook §2 动作矩阵）；
#   留痕 c1_backtest.crisis_gate_log MergeTree 只增不改；留痕/告警失败不阻断安全主流程（log+False）；
#   纯进程内存探针 kill_switch 保持"行为熔断"职责不变，本闸不挪用（裁定 D2）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AllocationInputError(日期字面量非法)；CrisisGateError(配置解析失败/未知键/θ 越界)；
#   CH 不可读→resolve_crisis_state 上抛（安全闸禁静默放行，fail-closed 处置由调用方裁定）；
#   log_crisis_gate_row/alert_crisis_level 永不抛（留痕与告警失败降级为日志）
# [TESTS] tests/pf_alloc/test_crisis_gate.py
# [A_module] module_id=MOD-PA-CRISIS-GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] auto-scaffold-crisis_gate-20260918
"""crisis_gate——危机态判读件（WO-2a 三级接线 P0，2026-09-18）。

真源：docs/_working/residual_construction/wo2_blackswan_workbook.md §1②/§2
（三级落点表 + D1~D4 设计裁定）+ pending_items_plan.md WORK-ORDER-2（2a P0）。

治什么：现行 is_crisis=dominant==r10 口径偏窄（G1）——r10 概率高但非 dominant 不触发，
恐慌预兆（p_r10=0.5+）不算危机。本件提供双档状态机 normal/warning/crisis + 三级动作
判定输入 + 留痕与告警出声，把"Owner 肉眼盯盘做危机决策"的人工环节自动化。

# [ALGO_FLOW] external: docs/03_modules/_domain_pf_alloc/algo_flow/crisis_gate.yaml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Final, Mapping, Protocol, Sequence

try:
    from zephyr.shared.io.paths import REPO_ROOT as _REPO_ROOT
except Exception:  # noqa: BLE001 — 仅路径解析降级
    _REPO_ROOT = Path(__file__).resolve().parents[2]

from zephyr.pf_alloc.allocation_config import AllocationConfig
from zephyr.pf_alloc.allocation_inputs import (
    CRISIS_STATE,
    REGIME_PROB_COLUMNS,
    RegimeInput,
    load_regime_input,
    validate_date_literal,
)

logger = logging.getLogger(__name__)

# NO-BARE-SQL 治本：写入语句提为模块级常量（plain 赋值，禁 Final 注解——R-029）。
SQL_INSERT_LOG = "INSERT INTO {table} {columns} VALUES"


__all__: Final = [
    "CrisisBlock",
    "CrisisGate",
    "CrisisGateConfig",
    "CrisisGateError",
    "CrisisState",
    "DEFAULT_WARNING_THETA",
    "STATE_CRISIS",
    "STATE_NORMAL",
    "STATE_WARNING",
    "alert_crisis_level",
    "classify_crisis_state",
    "crisis_block_check",
    "load_crisis_gate_config",
    "log_crisis_gate_row",
    "resolve_crisis_state",
]

# ── 常量（口径真源，禁散落）──────────────────────────────────────────

STATE_NORMAL = "normal"
STATE_WARNING = "warning"
STATE_CRISIS = "crisis"

# θ 缺省（config/crisis_gate.yaml 缺失时的兜底；O1 待 Owner 校准，0.5 起步）
DEFAULT_WARNING_THETA = 0.5

# p_r10 在 7 维概率向量中的列位（与 REGIME_PROB_COLUMNS 同源，禁魔法数字）
_P_R10_INDEX = REGIME_PROB_COLUMNS.index("p_r10")

# config 真源路径（相对仓根）
CONFIG_RELATIVE_PATH = "config/crisis_gate.yaml"

Reader = Callable[[str], "Sequence[Mapping[str, Any]]"]  # type: ignore[valid-type]


class _WriterPort(Protocol):
    """留痕写通道最小端口（CH client 兼容；gate-any-abuse 裸 Any 治本）。"""

    def execute(self, query: str, parameters: list) -> object: ...


class _AlerterPort(Protocol):
    """告警最小端口（zephyr.data.alerter.Alerter 兼容）。"""

    def notify(self, *args: object, **kwargs: object) -> object: ...


class CrisisGateError(ValueError):
    """危机闸配置非法（解析失败/未知键/θ 越界）。继承 ValueError 便于调用方统一捕获。

    敏感面（配置文件绝对路径）走结构化 ``details``，消息文本只留人类可读摘要——
    对齐 MSG-EXPOSURE（§5.99.20 治本）与 ZephyrBaseError 的 message/details 双通道口径。
    """

    # GATE-ERRCODE-CONSISTENCY 治本（land3）：原声明 "ZA-PA-CRISIS" 既不合注册表自述格式
    # （ZA-XX-NNNN 四位序号），注册新码又要动 PROTECTED 件
    # architecture_model/contracts/error_code_registry.yaml（Owner 审批路径，无 CLI 逃生旗）
    # ⇒ 本腿撤声明置 None，待 Owner 配号后与注册表**同一 commit 原子**转正
    #   （见 docs/_working/fullflow_campaign/adjudications/req_land3_01.md ITEM-7）。
    error_code: str | None = None

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details: dict[str, Any] = dict(details or {})


# ── 配置（θ 与全部参数的唯一真源=config/crisis_gate.yaml）─────────────


@dataclass(frozen=True)
class CrisisGateConfig:
    """危机闸运行配置（冻结）。文件缺失=本缺省；解析失败/未知键/越界=硬错。"""

    enabled: bool = True  # False=全闸旁路（显式回退开关，非删码回退）
    warning_theta: float = DEFAULT_WARNING_THETA  # O1 待 Owner 校准

    def __post_init__(self) -> None:
        if not 0 < self.warning_theta <= 1:
            raise CrisisGateError(f"warning_theta={self.warning_theta} 须∈(0,1]")


def load_crisis_gate_config(yaml_path: str | Path | None = None) -> CrisisGateConfig:
    """装配危机闸配置：config/crisis_gate.yaml（可选文件，缺失=全缺省）。

    解析失败/未知键/θ 越界 → CrisisGateError（配置在但读不懂不得静默降级，
    防"以为生效实际没生效"——WO-3 同款纪律）。
    """
    path = Path(yaml_path) if yaml_path is not None else (_REPO_ROOT / CONFIG_RELATIVE_PATH)
    if not path.exists():
        return CrisisGateConfig()
    import yaml  # 仓内既有依赖（allocation_inputs 同款，不新增依赖）

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise CrisisGateError(f"crisis_gate 配置解析失败: {exc}", details={"path": str(path)}) from exc
    if loaded is None:
        return CrisisGateConfig()
    if not isinstance(loaded, Mapping):
        raise CrisisGateError("crisis_gate 配置根节点须为映射", details={"path": str(path)})
    known = {"enabled", "warning_theta"}
    unknown = set(loaded) - known
    if unknown:
        raise CrisisGateError(
            f"crisis_gate 配置含未知键 {sorted(unknown)}（拼写漂移防静默）",
            details={"path": str(path)},
        )
    return CrisisGateConfig(
        enabled=bool(loaded.get("enabled", True)),
        warning_theta=float(loaded.get("warning_theta", DEFAULT_WARNING_THETA)),
    )


# ── 判定（纯函数，零副作用）──────────────────────────────────────────


@dataclass(frozen=True)
class CrisisState:
    """一次危机判定的完整依据（字段是 wo2 workbook §2 状态机的物化）。"""

    state: str  # normal | warning | crisis
    p_r10: float  # overlay CRISIS 态概率
    dominant: str  # regime 快照 dominant 态键（无快照=unknown）
    source_date: date | None  # 快照业务日（None=无快照）
    lag_days: int  # 快照滞后天数（无快照=-1）
    warning_theta: float = DEFAULT_WARNING_THETA  # 本次判定所用 θ（留痕可复算）
    fail_closed: bool = False  # True=无快照退化平坦口径（不误触）

    @property
    def is_crisis(self) -> bool:
        return self.state == STATE_CRISIS

    @property
    def is_warning(self) -> bool:
        return self.state in (STATE_WARNING, STATE_CRISIS)  # crisis ⊃ warning（floor 语义随行）

    @property
    def floor_active(self) -> bool:
        """CRISIS_SHRINKAGE_FLOOR=0.05 是否应激活（warning/crisis 均激活，workbook §2）。"""
        return self.is_warning


def classify_crisis_state(regime: RegimeInput, *, warning_theta: float) -> CrisisState:
    """RegimeInput → 三档状态（纯函数）。

    口径（裁定 D1）：
      - crisis = dominant == r10（硬拦截）；
      - warning = p_r10 ≥ θ（缩额 + 告警）；
      - 无快照（has_snapshot=False，fail-closed 平坦分布）→ normal **不误触**（验收③）；
    crisis 优先于 warning（同为 r10 高概率时取更严档）。
    """
    p_r10 = float(regime.probabilities[_P_R10_INDEX])
    if not regime.has_snapshot:
        return CrisisState(
            state=STATE_NORMAL,
            p_r10=p_r10,
            dominant=regime.dominant,
            source_date=None,
            lag_days=regime.lag_days,
            warning_theta=float(warning_theta),
            fail_closed=True,
        )
    if regime.dominant == CRISIS_STATE:
        state = STATE_CRISIS
    elif p_r10 >= warning_theta:
        state = STATE_WARNING
    else:
        state = STATE_NORMAL
    return CrisisState(
        state=state,
        p_r10=p_r10,
        dominant=regime.dominant,
        source_date=regime.source_date,
        lag_days=regime.lag_days,
        warning_theta=float(warning_theta),
        fail_closed=False,
    )


def resolve_crisis_state(
    trade_date: str | date | None = None,
    *,
    reader: Reader | None = None,
    gate_config: CrisisGateConfig | None = None,
    allocation_config: AllocationConfig | None = None,
) -> CrisisState:
    """业务日 → CrisisState（L0 判读入口：读 CH regime 快照 + 双档判定）。

    trade_date=None → 今天（date.today()，与 sim_paper_ledger 同款先例）。
    regime 读路径**复用** allocation_inputs.load_regime_input（PIT 最近快照，禁未来函数，
    勿另写 SQL——RULE-SSOT）。CH 不可读时原样上抛（安全闸禁静默放行）。
    """
    day = validate_date_literal(trade_date if trade_date is not None else date.today())
    cfg = gate_config or load_crisis_gate_config()
    regime = load_regime_input(day, allocation_config or AllocationConfig(), reader=reader)
    return classify_crisis_state(regime, warning_theta=cfg.warning_theta)


# ── L1 管线级：纯函数拦截检查（接线归总统筹）──────────────────────────


@dataclass(frozen=True)
class CrisisBlock:
    """L1 拦截判定结果（pipeline_events.run_pf_alloc_daily 接线消费）。

    skip=True ⇒ 调用方应短路当日额度重算并 `return {"skipped": "crisis_block"}`；
    **不落 marker**——解除后同日可重放，这一保证由调用方（接线方）承担。
    """

    skip: bool
    state: str  # normal | warning | crisis | disabled
    reason: str


def crisis_block_check(
    trade_date: str | date | None = None,
    *,
    state: CrisisState | None = None,
    reader: Reader | None = None,
    gate_config: CrisisGateConfig | None = None,
) -> CrisisBlock:
    """L1 纯函数：该业务日是否管线短路（注入 state 则零 IO，否则现读现判）。

    crisis → skip=True（额度冻结，不落 marker 由调用方保证）；
    warning → 照跑（缩额在 L2 由 shrinkage floor 承担，此处不拦）；
    normal/disabled → 照跑。
    """
    cfg = gate_config or load_crisis_gate_config()
    if not cfg.enabled:
        return CrisisBlock(
            skip=False,
            state="disabled",
            reason="crisis_gate.enabled=false（显式旁路开关，回退原因须登记）",
        )
    cs = state if state is not None else resolve_crisis_state(trade_date, reader=reader, gate_config=cfg)
    if cs.state == STATE_CRISIS:
        return CrisisBlock(
            skip=True,
            state=STATE_CRISIS,
            reason=(
                f"crisis_block：dominant={cs.dominant}（source={cs.source_date}, lag={cs.lag_days}d）"
                "→ 管线短路额度冻结；本闸不落 marker，解除后同日可重放（由调用方保证）；"
                "存量持仓不强平（强平语义归 ex_core 回撤阶梯）"
            ),
        )
    if cs.state == STATE_WARNING:
        return CrisisBlock(
            skip=False,
            state=STATE_WARNING,
            reason=(
                f"warning：p_r10={cs.p_r10:.3f}≥θ={cs.warning_theta:.2f}"
                + "→ 照跑 + CRISIS_SHRINKAGE_FLOOR=0.05 激活 + 告警"
            ),
        )
    note = "无快照 fail-closed 平坦分布→不误触" if cs.fail_closed else "regime 常态"
    return CrisisBlock(
        skip=False,
        state=STATE_NORMAL,
        reason=f"normal：dominant={cs.dominant}, p_r10={cs.p_r10:.3f}（{note}）",
    )


# ── 留痕（MergeTree 只增不改；失败不阻断安全主流程）───────────────────


def log_crisis_gate_row(
    *,
    trade_date: str | date,
    crisis_state: CrisisState,
    action_l1: str = "not_wired",
    action_l2: str = "pass",
    action_l3: str = "pass",
    probe_ts: datetime | None = None,
    writer: _WriterPort | None = None,
) -> bool:
    """判定行落 c1_backtest.crisis_gate_log（裁定 D4）。

    写通道走 DatabaseService writer 角色（宪法 §9.1 禁裸 connect）；表未建/CH 不可写
    → log+False（留痕失败不阻断拦截本身——安全动作优先于审计行，审计缺口靠日志兜底）。
    列模板取 schemas.categories.crisis_gate_log 真源（禁复制列名）。
    """
    try:
        if not isinstance(trade_date, (str, date)):
            raise CrisisGateError(f"trade_date 类型非法: {type(trade_date).__name__}")
        day = date.fromisoformat(
            validate_date_literal(trade_date)
        )  # B20 治本：Date 列槽位必须入 date 对象——str 字面量会被驱动取 value.year 抛 AttributeError 且被上方 except 吞成 warning，留痕静默蒸发（fullflow B20 驱动级实证：str 抛/date OK）
        from schemas.categories.crisis_gate_log import INSERT_COLUMNS, QUALIFIED_NAME

        ts = probe_ts or datetime.now(timezone.utc)
        row = (
            ts,
            day,
            crisis_state.state,
            float(crisis_state.p_r10),
            crisis_state.dominant,
            str(action_l1),
            str(action_l2),
            str(action_l3),
        )
        if writer is None:
            from zephyr.infrastructure.database_service import get_db_service

            writer = get_db_service().get_clickhouse_conn(role="writer")
        writer.execute(SQL_INSERT_LOG.format(table=QUALIFIED_NAME, columns=INSERT_COLUMNS), [row])
        return True
    except Exception as exc:  # noqa: BLE001 — 留痕失败不阻断安全主流程（ERROR_CONTRACT）
        logger.warning("crisis_gate_log 留痕失败（表可能未注册 DDL，由总统筹 apply）: %s", exc)
        return False


# ── 告警（复用 zephyr.data.alerter，不重建告警系统；失败不抛）─────────


def alert_crisis_level(
    level: str,
    *,
    trade_date: str | date,
    crisis_state: CrisisState,
    detail: str = "",
    alerter: _AlerterPort | None = None,
) -> bool:
    """三级各自出声（裁定 D3）：task_id=crisis_gate_<level>，写 data/failures/*.json。

    crisis → CRITICAL（落 failure 文件，WO-4 外推通道的触发面）；
    warning → WARN（日志出声；持久留痕靠 crisis_gate_log 表行）；
    normal → 不出声。
    复用 alerter 冷却/文件命名既有语义，不新建告警机制。
    """
    try:
        if crisis_state.state == STATE_NORMAL:
            return True
        from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_WARN, Alerter

        lvl = LEVEL_CRITICAL if crisis_state.state == STATE_CRISIS else LEVEL_WARN
        msg = (
            f"crisis_gate[{level}] trade_date={trade_date} state={crisis_state.state} "
            f"p_r10={crisis_state.p_r10:.3f} dominant={crisis_state.dominant} {detail}"
        ).strip()
        alerter = alerter or Alerter()
        return alerter.notify(
            f"crisis_gate_{level}",
            msg,
            level=lvl,
            source="pf_alloc.crisis_gate",
            extra={
                "trade_date": str(trade_date),
                "state": crisis_state.state,
                "p_r10": round(float(crisis_state.p_r10), 6),
                "dominant": crisis_state.dominant,
                "source_date": str(crisis_state.source_date),
                "lag_days": crisis_state.lag_days,
            },
        )
    except Exception as exc:  # noqa: BLE001 — 告警失败不阻断安全主流程（ERROR_CONTRACT）
        logger.warning("crisis_gate 告警失败（不阻断）: %s", exc)
        return False


# ── 门面（__init__.py 以 CrisisGate 注册；函数式 API 的薄封装）────────


class CrisisGate:
    """危机闸门面：L1/L2/L3 接线方统一入口（无状态，全部静态委托）。"""

    @staticmethod
    def config(yaml_path: str | Path | None = None) -> CrisisGateConfig:
        return load_crisis_gate_config(yaml_path)

    @staticmethod
    def resolve(trade_date: str | date | None = None, **kwargs: Any) -> CrisisState:
        return resolve_crisis_state(trade_date, **kwargs)

    @staticmethod
    def block_check(trade_date: str | date | None = None, **kwargs: Any) -> CrisisBlock:
        return crisis_block_check(trade_date, **kwargs)

    @staticmethod
    def log_row(**kwargs: Any) -> bool:
        return log_crisis_gate_row(**kwargs)

    @staticmethod
    def alert(level: str, **kwargs: Any) -> bool:
        return alert_crisis_level(level, **kwargs)
