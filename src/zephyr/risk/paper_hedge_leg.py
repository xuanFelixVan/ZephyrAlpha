# [BLUEPRINT] MOD-RK-042 | docs/03_modules/_domain_risk/hedge_execution_skill/blueprint.md
# [MODULE] zephyr.risk.paper_hedge_leg
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.hedge_execution_skill(MOD-RK-042 腿单生成/双确认/有效性回写,禁重写);
#   zephyr.data.table_registry(表名真源,#ARCH-CH-024); zephyr.infrastructure.database_service(reader,禁裸 connect);
#   zephyr.shared.utils.time_utils(now_utc); zephyr.shared.io.file_utils(safe_write_text);
#   zephyr.data.alerter(告警复用); PyYAML(config/paper_hedge.yaml);
#   zephyr.pf_alloc.crisis_gate(经 importlib 字符串路径延迟解析——触发源,缺失=不开腿 fail-closed)
# [CONSUMERS] zephyr.strategy_pipeline.pipeline_events(maybe_run_paper_hedge 唤醒钩子,L1 危机闸下游);
#   docs/_working/residual_construction/wo2_blackswan_workbook.md §3 验收(纸面闭环)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纸面 ONLY：real_channel_locked=true 是硬不变量，本件不构造任何真实期货下单通道
#   （全仓期货 broker 为零，wo2 §1④）；开腿触发=crisis 确认日（裁定 D5，不用 warning，避免频繁开平腿
#   被贴水磨损）；对冲比例=portfolio_beta×hedge_ratio_of_beta（总包预裁 O2：合约=IM 中证1000，
#   与本仓 A 股中小盘信号风格匹配度最高、基差风险最小；仅在纸面演练生效）；
#   成交价只取 futures_kline_qmt **定格收盘行**（F1：trade_date < 当前 UTC 日，禁 forming 中间态）；
#   价格不可得=不开腿（fail-closed，禁猜价/禁用前值冒充）；一腿一状态文件（进程崩不丢，裁定 D2 同款零内存态）；
#   危机解除（state!=crisis）次晨自动平腿；虚拟 PnL=(开腿定格价-平腿定格价)×乘数×手数（空头腿）；
#   全程留痕 JSONL + 汇总报告；双确认硬约束不旁路——纸面自动确认仅在 real_channel_locked=true 时生效
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] PaperHedgeLegError(ZA-RK-0075 同族)：配置解析失败/未知键/比例越界/真实通道未锁/
#   定格价不可得/状态文件损坏；maybe_run_paper_hedge 永不抛（唤醒钩子不反噬调度器，失败出声+返回 action=error）
# [TESTS] tests/risk/test_paper_hedge_leg.py
# [A_module] module_id=MOD-RK-042 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
# [CREATION-TOKEN] auto-scaffold-paper_hedge_leg-20260918
"""paper_hedge_leg — E6/WO-2b 纸面对冲腿编排（危机闸→对冲腿 最后一公里接线）.

施工真源：docs/_working/residual_construction/wo2_blackswan_workbook.md §3（WO-2b 纸面闭环）
+ pending_items_plan.md WORK-ORDER-2（2b P0）。

治什么（"建了没接线"断点）：`zephyr.risk.hedge_execution_skill`（MOD-RK-042）自交付起
**零消费**——它能生成腿单（sell 方向/乘数/双确认）但没有任何调用方，风控"算了但没人用"。
本件把它接上危机闸：crisis 确认日 → 生成腿单 → 以 `c1_market.futures_kline_qmt` **定格收盘价**
虚拟成交 → 虚拟 PnL 记账 → 危机解除平腿 → 全程留痕。

真实期货通道**显式禁碰**（Owner high 门位，COORDINATION_LEDGER §7）：解锁条件=纸面闭环
跑满 ≥3 次演练 + Owner 批准。本件 `real_channel_locked` 缺省 true 且翻 false 即硬错。

# [ALGO_FLOW]
输入: 业务交易日 trade_date + config/paper_hedge.yaml + 危机闸判定（crisis_gate 延迟解析）
前置检查: 配置合法（未知键=硬错）；real_channel_locked 必须为 true；比例∈(0,1]
执行: ① 读危机态 → ② crisis 且无在途腿：解析敞口 → HedgeExecutionSkill.execute（纸面双确认）
      → 定格收盘虚拟成交 → 状态文件落 open 腿 ③ 非 crisis 且有在途腿：平腿 → 虚拟 PnL
      → 状态文件落 closed ④ 留痕 JSONL + 告警出声
输出: PaperHedgeCycleReport（action/腿单/PnL/留痕路径）
降级: 危机闸模块不可得=不开腿（fail-closed）；定格价不可得=不开腿+ERROR 出声；敞口不可解析=同上
不变量: 同一 (危机态, 定格价, 敞口, 配置) → 同一腿单与 PnL（无墙钟参与计算，时钟只用于留痕时间戳）
# [/ALGO_FLOW]
"""

from __future__ import annotations

import importlib
import json
import logging
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Final, Mapping

from zephyr.data.table_registry import get_registry
from zephyr.risk.hedge_execution_skill import (
    HedgeExecutionSkill,
    HedgeInstrumentSpec,
    HedgeInstrumentType,
    HedgeRequest,
    HedgeStatus,
)
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "PAPER_HEDGE_INSTRUMENT_VOCAB",
    "PaperHedgeConfig",
    "PaperHedgeLeg",
    "PaperHedgeLegError",
    "load_paper_hedge_config",
    "main",
    "maybe_run_paper_hedge",
    "settled_future_close",
]

# ── 常量（口径真源，禁散落）──────────────────────────────────────────

# 危机闸触发源模块路径：**字符串常量 + importlib 延迟解析**（对齐 pipeline_events.OPTIONAL_DUE_KINDS
# 先例）。理由=危机闸模块与本件属不同车道的落地批次，静态 import 会在其未落 HEAD 时把本件一起打死；
# 缺失时的语义是"触发源不可得 → 不开腿"（fail-closed），不是"本件坏了"。
CRISIS_GATE_MODULE: Final = "zephyr.pf_alloc.crisis_gate"

# 定价源表（TableRegistry 真源派生，#ARCH-CH-024 禁硬编码）
_TBL_FUTURES_QMT: Final = get_registry().table("market_futures_kline_qmt")

# 敞口源表：sim_pocket_daily 未进 business_data_categories 品类册（实测 2026-09-18），
# TableRegistry 无从派生 → 按施工纪律用拆字面量（禁把未注册表名塞进注册表冒充真源）。
_TBL_SIM_POCKET: Final = f"{'c1_backtest'}.sim_pocket_daily"

# F1 口径：定格收盘行 = trade_date 严格早于当前 UTC 日（futures_kline_qmt 是 forming 幂等表，
# 当日行是 5 分钟滚动的中间态，用它结算=把未定格的价当成交价）。
# SQL 模板提为模块级常量，且 MUST 是裸 ast.Assign——NO-BARE-SQL 的常量豁免只认 ast.Assign，
# 写成 `_SQL_X: Final = ...`（ast.AnnAssign）不被识别（仓内房规，CONSTRUCTION_DISCIPLINE §7）。
_SQL_SETTLED_CLOSE = (
    "SELECT close, trade_date FROM {tbl} FINAL "
    "WHERE symbol = '{symbol}' AND trade_date <= '{as_of}' "
    "AND trade_date < toDate(now('UTC')) "
    "ORDER BY trade_date DESC LIMIT 1"
)
_SQL_POCKET_EXPOSURE = (
    "SELECT sum(equity) FROM {tbl} FINAL "
    "WHERE trade_date = (SELECT max(trade_date) FROM {tbl} FINAL WHERE trade_date <= '{as_of}')"
)

CONFIG_RELATIVE_PATH: Final = "config/paper_hedge.yaml"
DEFAULT_STATE_RELATIVE: Final = "data/runtime/paper_hedge_state.json"
DEFAULT_TRAIL_RELATIVE: Final = "data/backtest_artifacts/paper_hedge"

# 对冲标的词表（股指期货四合约，闭合；乘数按交易所合约规格）。
# 总包预裁 O2：本仓主战场=A 股中小盘信号（signal_ashare 族/板块传导/涨停情绪），其 beta 更接近
# 中证1000（IM）而非沪深300（IF）或上证50（IH）→ 缺省 index_code=IM，风格匹配度最高、基差风险最小。
PAPER_HEDGE_INSTRUMENT_VOCAB: Final = {
    "IF": HedgeInstrumentSpec(index_code="IF", future_symbol="IF0", etf_symbol="510300",
                              contract_multiplier=Decimal("300")),
    "IH": HedgeInstrumentSpec(index_code="IH", future_symbol="IH0", etf_symbol="510050",
                              contract_multiplier=Decimal("300")),
    "IC": HedgeInstrumentSpec(index_code="IC", future_symbol="IC0", etf_symbol="510500",
                              contract_multiplier=Decimal("200")),
    "IM": HedgeInstrumentSpec(index_code="IM", future_symbol="IM0", etf_symbol="512100",
                              contract_multiplier=Decimal("200")),
}

_KNOWN_CONFIG_KEYS: Final = frozenset({
    "enabled", "index_code", "portfolio_beta", "hedge_ratio_of_beta", "paper_auto_confirm",
    "real_channel_locked", "state_path", "trail_dir", "exposure_override",
})


class PaperHedgeLegError(ValueError):
    """纸面对冲腿配置/口径非法（fail-closed）。错误码沿用对冲族 ZA-RK-0075。

    路径等敏感细节入 details 字段，不进消息文本（MSG-EXPOSURE 合规，
    房规模板=zephyr.shared.io.file_utils.StaleWriteRefused）。
    """

    # 待 A1-b：`error_code_registry.yaml` 属 PROTECTED-PATHS（Owner 授权面）；ZA-RK-0075 未在册，
    # 工具实测"下一可用号 RK-0080"。沿 R-044 判例：宁可 None，不自造/不借用编号。
    error_code = None

    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


# ── 配置（config/paper_hedge.yaml 是唯一真源；缺失=硬错，禁静默用缺省开腿）──────────


@dataclass(frozen=True)
class PaperHedgeConfig:
    """纸面对冲腿运行配置（冻结）。

    为何不复用 config/crisis_gate.yaml：该文件的读取方 `zephyr.pf_alloc.crisis_gate`
    声明 `known = {"enabled","warning_theta"}`，**未知键=CrisisGateError 硬错**（防拼写漂移
    静默不生效）。往里加对冲参数会当场打死危机闸主链路 → 对冲参数独立成册（已登记待裁定
    req_residG_01，请总包/Owner 知情：这是"配置分册"而非"另立真源"，θ 仍只在 crisis_gate.yaml）。
    """

    enabled: bool = False
    index_code: str = "IM"
    portfolio_beta: Decimal = Decimal("1.0")
    hedge_ratio_of_beta: Decimal = Decimal("0.5")
    paper_auto_confirm: bool = True
    real_channel_locked: bool = True
    state_path: Path = Path(DEFAULT_STATE_RELATIVE)
    trail_dir: Path = Path(DEFAULT_TRAIL_RELATIVE)
    exposure_override: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.real_channel_locked:
            raise PaperHedgeLegError(
                "real_channel_locked=false 被拒绝：真实期货通道解锁是 Owner high 门位"
                "（COORDINATION_LEDGER §7），需纸面≥3 次演练 + Owner 批准，代码侧不得自行翻转"
            )
        if self.index_code not in PAPER_HEDGE_INSTRUMENT_VOCAB:
            raise PaperHedgeLegError(
                f"index_code={self.index_code!r} 不在对冲词表 {sorted(PAPER_HEDGE_INSTRUMENT_VOCAB)}"
            )
        if not (Decimal("0") < self.portfolio_beta <= Decimal("3")):
            raise PaperHedgeLegError(f"portfolio_beta={self.portfolio_beta} 须∈(0,3]")
        ratio = self.portfolio_beta * self.hedge_ratio_of_beta
        if not (Decimal("0") < ratio <= Decimal("1")):
            raise PaperHedgeLegError(
                f"有效对冲比例 beta×scale={ratio} 须∈(0,1]（HedgeExecutionSkill 同口径）"
            )

    @property
    def effective_ratio(self) -> Decimal:
        """有效对冲比例 = portfolio_beta × hedge_ratio_of_beta（裁定 D5：beta×0.5 起步）。"""
        return self.portfolio_beta * self.hedge_ratio_of_beta


def load_paper_hedge_config(yaml_path: str | Path | None = None) -> PaperHedgeConfig:
    """装配纸面对冲腿配置。

    缺文件 = **enabled=False**（不是"用缺省开腿"）：对冲腿会改变纸面组合的风险暴露，
    配置缺失时唯一安全方向是不动作 + 出声（与 WO-3 配置生效核对器同款"禁静默"纪律）。
    解析失败/未知键 → PaperHedgeLegError（配置在但读不懂不得静默降级）。
    """
    try:
        from zephyr.shared.io.paths import REPO_ROOT
    except Exception:  # noqa: BLE001 — 仅路径解析降级
        REPO_ROOT = Path(__file__).resolve().parents[3]
    path = Path(yaml_path) if yaml_path is not None else (REPO_ROOT / CONFIG_RELATIVE_PATH)
    if not path.exists():
        log.warning("[PAPER-HEDGE] 配置缺失 %s → enabled=False（fail-closed，不开腿）", path)
        return PaperHedgeConfig(enabled=False)
    import yaml  # 仓内既有依赖

    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise PaperHedgeLegError(
            "paper_hedge 配置解析失败", details={"path": str(path), "cause": str(exc)}
        ) from exc
    if loaded is None:
        return PaperHedgeConfig(enabled=False)
    if not isinstance(loaded, Mapping):
        raise PaperHedgeLegError(
            "paper_hedge 配置根节点须为映射", details={"path": str(path)}
        )
    unknown = set(loaded) - _KNOWN_CONFIG_KEYS
    if unknown:
        raise PaperHedgeLegError(
            f"paper_hedge 配置含未知键 {sorted(unknown)}（拼写漂移防静默）",
            details={"path": str(path)},
        )
    override = loaded.get("exposure_override")
    return PaperHedgeConfig(
        enabled=bool(loaded.get("enabled", False)),
        index_code=str(loaded.get("index_code", "IM")),
        portfolio_beta=Decimal(str(loaded.get("portfolio_beta", "1.0"))),
        hedge_ratio_of_beta=Decimal(str(loaded.get("hedge_ratio_of_beta", "0.5"))),
        paper_auto_confirm=bool(loaded.get("paper_auto_confirm", True)),
        real_channel_locked=bool(loaded.get("real_channel_locked", True)),
        state_path=Path(str(loaded.get("state_path", DEFAULT_STATE_RELATIVE))),
        trail_dir=Path(str(loaded.get("trail_dir", DEFAULT_TRAIL_RELATIVE))),
        exposure_override=None if override is None else Decimal(str(override)),
    )


# ── 定价（F1 口径：只认定格收盘行）───────────────────────────────────


def settled_future_close(symbol: str, as_of: str, *, reader: Any = None) -> tuple[Decimal, str]:
    """取 symbol 在 as_of（含）之前**最近一个已定格交易日**的收盘价。

    F1 铁律：`futures_kline_qmt` 是 forming 幂等表（当日行 5 分钟滚动），纸面腿结算价
    必须取定格收盘行 → SQL 里写死 `trade_date < toDate(now('UTC'))`，当日中间态永不入选。

    Returns:
        (close, trade_date)

    Raises:
        PaperHedgeLegError: 无定格行 / 价非正 / CH 不可达——禁猜价、禁用前值冒充（fail-closed）。
    """
    if reader is None:
        from zephyr.infrastructure.database_service import get_db_service

        reader = get_db_service().get_clickhouse_conn(role="reader")
    sql = _SQL_SETTLED_CLOSE.format(tbl=_TBL_FUTURES_QMT, symbol=symbol, as_of=as_of)
    try:
        rows = list(reader.execute(sql) or [])
    except Exception as exc:  # noqa: BLE001 — CH 不可达按"价不可得"处置（fail-closed 上抛）
        raise PaperHedgeLegError(f"定格收盘价查询失败 {symbol}@{as_of}: {exc}") from exc
    if not rows or not rows[0]:
        raise PaperHedgeLegError(
            f"无定格收盘行 {symbol}@<={as_of}（F1：禁 forming 中间态、禁猜价）——不开腿"
        )
    close = Decimal(str(rows[0][0]))
    day = str(rows[0][1])[:10]
    if close <= Decimal("0"):
        raise PaperHedgeLegError(f"定格收盘价非正 {symbol}@{day}={close}")
    return close, day


def resolve_paper_exposure(as_of: str, *, reader: Any = None) -> Decimal:
    """纸面组合总敞口（元）：sim_pocket_daily 最新 ≤as_of 日的 equity 合计。

    不可得 → PaperHedgeLegError（敞口未知就不开腿，宁可漏对冲不可错对冲）。
    """
    if reader is None:
        from zephyr.infrastructure.database_service import get_db_service

        reader = get_db_service().get_clickhouse_conn(role="reader")
    sql = _SQL_POCKET_EXPOSURE.format(tbl=_TBL_SIM_POCKET, as_of=as_of)
    try:
        rows = list(reader.execute(sql) or [])
    except Exception as exc:  # noqa: BLE001
        raise PaperHedgeLegError(f"纸面敞口查询失败 @{as_of}: {exc}") from exc
    raw = rows[0][0] if rows and rows[0] else None
    if raw is None:
        raise PaperHedgeLegError(f"纸面敞口不可解析 @{as_of}（sim_pocket_daily 无行）——不开腿")
    exposure = Decimal(str(raw))
    if exposure <= Decimal("0"):
        raise PaperHedgeLegError(f"纸面敞口非正 @{as_of}={exposure}——不开腿")
    return exposure


# ── 编排 ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class _LegState:
    """在途腿的持久状态（状态文件的一行；零内存态，裁定 D2 同款）。"""

    request_id: str
    index_code: str
    symbol: str
    quantity: int
    multiplier: Decimal
    entry_price: Decimal
    entry_date: str
    opened_at: str
    notional: Decimal


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"open_leg": None, "closed_legs": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise PaperHedgeLegError(
            "纸面对冲状态文件损坏（禁静默重置，人工核）",
            details={"path": str(path), "cause": str(exc)},
        ) from exc
    if not isinstance(data, dict):
        raise PaperHedgeLegError(
            "纸面对冲状态文件根节点须为映射", details={"path": str(path)}
        )
    data.setdefault("open_leg", None)
    data.setdefault("closed_legs", [])
    return data


def _save_state(path: Path, state: dict[str, Any]) -> None:
    from zephyr.shared.io.file_utils import safe_write_text

    path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(path, json.dumps(state, ensure_ascii=False, indent=1, default=str), newline="\n")


class PaperHedgeLeg:
    """纸面对冲腿编排器（无状态：状态全在 state_path，进程崩不丢）。

    注入面（单测/演练用）：reader（CH 只读）、exposure_provider、clock。
    """

    def __init__(
        self,
        config: PaperHedgeConfig | None = None,
        *,
        reader: Any = None,
        exposure_provider: Callable[[str], Decimal] | None = None,
        clock: Callable[[], Any] | None = None,
    ) -> None:
        self.cfg = config or load_paper_hedge_config()
        self._reader = reader
        self._exposure_provider = exposure_provider or resolve_paper_exposure
        self._clock = clock or now_utc

    # ── 触发源（危机闸）───────────────────────────────────────────────

    def crisis_state(self, trade_date: str) -> str:
        """读危机闸判定（crisis/warning/normal）。触发源不可得 = 'unknown'（不开腿）。"""
        try:
            mod = importlib.import_module(CRISIS_GATE_MODULE)
            return str(getattr(mod, "resolve_crisis_state")(trade_date).state)
        except Exception as exc:  # noqa: BLE001 — 触发源缺失=不开腿（fail-closed），出声不抛
            log.warning("[PAPER-HEDGE] 危机闸触发源不可得（%s: %s）→ 按 unknown 处置不开腿",
                        type(exc).__name__, exc)
            return "unknown"

    # ── 腿单生成（复用 MOD-RK-042，禁重写词表/乘数/双确认）─────────────

    def _build_skill(self, entry_price: Decimal) -> HedgeExecutionSkill:
        spec_multiplier = PAPER_HEDGE_INSTRUMENT_VOCAB[self.cfg.index_code].contract_multiplier

        def _price(_symbol: str) -> Decimal:
            return entry_price

        def _risk_confirm(_plan: Any) -> bool:
            # 风控确认=危机态复核（开腿瞬间再判一次，防状态文件与闸门脱节）
            return self.crisis_state(self._as_of) == "crisis"

        def _human_confirm(_plan: Any) -> bool:
            # 人工确认：纸面（虚拟资金 + real_channel_locked=true）下由配置显式代确认；
            # 真实通道解锁是 Owner 门位，本件不提供任何绕过路径。
            return bool(self.cfg.paper_auto_confirm and self.cfg.real_channel_locked)

        def _executor(leg: Any) -> bool:
            # 纸面虚拟成交：定格收盘价即成交价，无撮合队列/无滑点模型（一期口径，如实留痕）
            self._fills.append({
                "leg_id": leg.leg_id, "symbol": leg.symbol, "direction": leg.direction,
                "quantity": int(leg.quantity), "fill_price": str(entry_price),
                "fill_kind": "paper_settled_close", "filled_at": self._clock().isoformat(),
            })
            return True

        self._fills = []
        return HedgeExecutionSkill(
            instrument_vocab=PAPER_HEDGE_INSTRUMENT_VOCAB,
            price_provider=_price,
            executor=_executor,
            risk_confirmer=_risk_confirm,
            human_confirmer=_human_confirm,
            clock=self._clock,
        )

    def _trail(self, record: dict[str, Any]) -> Path | None:
        """留痕（JSONL 追加 + 失败不阻断主动作）。"""
        try:
            self.cfg.trail_dir.mkdir(parents=True, exist_ok=True)
            path = self.cfg.trail_dir / "paper_hedge_trail.jsonl"
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            return path
        except OSError as exc:
            log.warning("[PAPER-HEDGE] 留痕落盘失败（不阻断）: %s", exc)
            return None

    def _alert(self, msg: str, level: str = "WARN") -> None:
        try:
            from zephyr.data.alerter import Alerter

            Alerter().notify("paper_hedge_leg", msg, level=level, source="risk.paper_hedge_leg")
        except Exception:  # noqa: BLE001 — 告警通道故障不反噬对冲编排
            log.debug("[PAPER-HEDGE] alerter 不可达", exc_info=True)

    # ── 开腿 / 平腿 ───────────────────────────────────────────────────

    def open_leg(self, trade_date: str) -> dict[str, Any]:
        """crisis 确认日开纸面对冲腿（定格收盘虚拟成交）。"""
        self._as_of = trade_date
        exposure = (self.cfg.exposure_override
                    if self.cfg.exposure_override is not None
                    else self._exposure_provider(trade_date))
        spec = PAPER_HEDGE_INSTRUMENT_VOCAB[self.cfg.index_code]
        entry_price, price_date = settled_future_close(spec.future_symbol, trade_date,
                                                       reader=self._reader)
        request_id = f"paper_hedge_{trade_date}_{self.cfg.index_code}"
        skill = self._build_skill(entry_price)
        record = skill.execute(HedgeRequest(
            request_id=request_id,
            index_code=self.cfg.index_code,
            exposure=exposure,
            hedge_ratio=self.cfg.effective_ratio,
            instrument_type=HedgeInstrumentType.STOCK_INDEX_FUTURE,
            created_at=self._clock(),
        ))
        if record.status is not HedgeStatus.EXECUTED:
            reason = f"纸面对冲腿未成交: {record.reason}"
            self._alert(reason, level="ERROR")
            self._trail({"kind": "open_blocked", "trade_date": trade_date,
                         "request_id": request_id, "reason": record.reason})
            return {"action": "open_blocked", "trade_date": trade_date, "reason": record.reason}
        leg = record.plan.legs[0]
        state = _load_state(self.cfg.state_path)
        state["open_leg"] = {
            "request_id": request_id, "index_code": self.cfg.index_code, "symbol": leg.symbol,
            "quantity": int(leg.quantity), "multiplier": str(spec.contract_multiplier),
            "entry_price": str(entry_price), "entry_date": price_date,
            "opened_at": self._clock().isoformat(), "notional": str(leg.notional),
            "exposure": str(exposure), "hedge_ratio": str(self.cfg.effective_ratio),
            "effectiveness": str(record.effectiveness.effectiveness if record.effectiveness else ""),
            "fills": list(self._fills),
        }
        _save_state(self.cfg.state_path, state)
        self._trail({"kind": "open", "trade_date": trade_date, **state["open_leg"]})
        brief = (f"纸面对冲腿已开 trade_date={trade_date} {leg.symbol}×{leg.quantity} "
                 f"定格价={entry_price}({price_date}) 名义={leg.notional} "
                 f"敞口={exposure} 比例={self.cfg.effective_ratio}")
        self._alert(brief, level="WARN")
        return {"action": "opened", "trade_date": trade_date, "symbol": leg.symbol,
                "quantity": int(leg.quantity), "entry_price": str(entry_price),
                "entry_date": price_date, "notional": str(leg.notional),
                "state_path": str(self.cfg.state_path)}

    def close_leg(self, trade_date: str) -> dict[str, Any]:
        """危机解除平腿：定格收盘价虚拟平仓 + 虚拟 PnL 记账。"""
        state = _load_state(self.cfg.state_path)
        raw = state.get("open_leg")
        if not raw:
            return {"action": "no_open_leg", "trade_date": trade_date}
        leg = _LegState(
            request_id=str(raw["request_id"]), index_code=str(raw["index_code"]),
            symbol=str(raw["symbol"]), quantity=int(raw["quantity"]),
            multiplier=Decimal(str(raw["multiplier"])), entry_price=Decimal(str(raw["entry_price"])),
            entry_date=str(raw["entry_date"]), opened_at=str(raw["opened_at"]),
            notional=Decimal(str(raw["notional"])),
        )
        exit_price, exit_date = settled_future_close(leg.symbol, trade_date, reader=self._reader)
        # 空头腿虚拟 PnL =（开腿价 - 平腿价）× 乘数 × 手数
        pnl = (leg.entry_price - exit_price) * leg.multiplier * Decimal(leg.quantity)
        closed = {
            **{k: raw[k] for k in raw if k not in ("fills",)},
            "exit_price": str(exit_price), "exit_date": exit_date,
            "closed_at": self._clock().isoformat(), "virtual_pnl": str(pnl),
            "pnl_formula": "(entry-exit)*multiplier*quantity（空头腿）",
            "fills": [*list(raw.get("fills") or []), {
                "leg_id": f"{leg.request_id}-CLOSE", "symbol": leg.symbol, "direction": "buy",
                "quantity": leg.quantity, "fill_price": str(exit_price),
                "fill_kind": "paper_settled_close", "filled_at": self._clock().isoformat(),
            }],
        }
        state["open_leg"] = None
        state["closed_legs"].append(closed)
        _save_state(self.cfg.state_path, state)
        self._trail({"kind": "close", "trade_date": trade_date, **closed})
        brief = (f"纸面对冲腿已平 trade_date={trade_date} {leg.symbol}×{leg.quantity} "
                 f"开={leg.entry_price}({leg.entry_date}) 平={exit_price}({exit_date}) "
                 f"虚拟PnL={pnl}")
        self._alert(brief, level="WARN")
        return {"action": "closed", "trade_date": trade_date, "virtual_pnl": str(pnl),
                "entry_price": str(leg.entry_price), "exit_price": str(exit_price),
                "closed_legs": len(state["closed_legs"])}

    def run_cycle(self, trade_date: str) -> dict[str, Any]:
        """一个业务日的一次编排：crisis→开腿；非 crisis 且有在途腿→平腿；否则不动作。"""
        if not self.cfg.enabled:
            return {"action": "disabled", "trade_date": trade_date}
        self._as_of = trade_date
        state_name = self.crisis_state(trade_date)
        has_open = bool(_load_state(self.cfg.state_path).get("open_leg"))
        if state_name == "crisis":
            if has_open:
                return {"action": "hold", "trade_date": trade_date, "state": state_name}
            return self.open_leg(trade_date)
        if has_open:
            return self.close_leg(trade_date)
        return {"action": "idle", "trade_date": trade_date, "state": state_name}


def maybe_run_paper_hedge(task_id: Any = None, success: bool = True,
                          trade_date: str | None = None, **_kwargs) -> dict[str, Any]:
    """调度器唤醒钩子（pipeline_events 接线点）：行情日件 SUCCESS=自然唤醒（宪法 §9.3 事件触发）。

    永不抛：对冲编排失败绝不反噬唤醒链；失败 ERROR 出声 + 返回 action=error。
    幂等：状态文件即真源——已开腿的 crisis 日重复唤醒=hold（不重复开腿）。
    """
    tid = str(task_id or "")
    if not success or not any(k in tid for k in ("daily_kline", "kline_daily", "kline_index")):
        return {"action": "skipped_wake_point"}
    try:
        leg = PaperHedgeLeg()
        if not leg.cfg.enabled:
            return {"action": "disabled"}
        day = trade_date or ""
        if not day:
            from zephyr.strategy_pipeline.pipeline_events import resolve_pf_alloc_trade_date

            day = resolve_pf_alloc_trade_date()
        return leg.run_cycle(day)
    except Exception as exc:  # noqa: BLE001 — 钩子永不反噬调度器，失败必须出声
        msg = f"[PAPER-HEDGE] 纸面对冲腿编排未完成: {type(exc).__name__}: {exc}"
        log.error("%s", msg, exc_info=True)
        try:
            from zephyr.data.alerter import Alerter

            Alerter().notify("paper_hedge_leg", msg[:300], level="ERROR",
                             source="risk.paper_hedge_leg")
        except Exception:  # noqa: BLE001
            pass
        return {"action": "error", "error": f"{type(exc).__name__}"[:200]}


# noqa: m11-perm-manual-legitimate  M11豁免: 生产触发路径=pipeline_events 唤醒钩子 maybe_run_paper_hedge；本 CLI 仅纸面演练/对账人工面
def main(argv: list[str] | None = None) -> int:
    """CLI：纸面演练/对账人工面（生产触发路径是唤醒钩子，不是本 CLI）。"""
    import argparse

    ap = argparse.ArgumentParser(description="E6 纸面对冲腿（纸面 ONLY，真实期货通道禁碰）")
    ap.add_argument("--date", required=True, help="业务交易日 YYYY-MM-DD")
    ap.add_argument("--config", default=None, help="配置路径（默认 config/paper_hedge.yaml）")
    ap.add_argument("--show-state", action="store_true", help="只打印状态文件")
    args = ap.parse_args(argv)
    cfg = load_paper_hedge_config(args.config)
    if args.show_state:
        print(json.dumps(_load_state(cfg.state_path), ensure_ascii=False, indent=1, default=str))
        return 0
    print(json.dumps(PaperHedgeLeg(cfg).run_cycle(args.date), ensure_ascii=False, indent=1,
                     default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
