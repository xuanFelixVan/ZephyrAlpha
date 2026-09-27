# [BLUEPRINT] MOD-SCRIPT-start_paper_session | scripts/start_paper_session.py | §
# [MODULE] scripts.start_paper_session
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib；zephyr.compliance.compliance_report_registry+manipulation_realtime_monitor（F62 C-002 三门装配批：先报告后交易 + 盘中操纵冻结）；zephyr.ex_core.cancel_rate_guard（日申报计数器，OrderManager 与 TradingSession 同实例双注入）；zephyr.ex_core.trading_session（TradingSession/TradingSessionConfig 真源）；zephyr.ex_core.live_strategy_adapter（--service 常驻服务模式：LiveStrategyAdapter/StrategySlot）；zephyr.ex_core.adapters.miniqmt_broker（延迟 import）；zephyr.ex_core.order_manager；zephyr.ex_core.signal_providers；zephyr.ex_core.risk_layer_orchestrator+position_reconciler+position_tracker.tracker（H5-P0 风控接线批）；zephyr.ex_core.async_fill_dispatcher（成交入账离回调线程，stop 排空）；zephyr.governance.adapters.risk_validation_bridge；zephyr.risk.implementations.default_risk_validator；zephyr.risk.core.drawdown_tracker/var_calculator/tail_risk_monitor；zephyr.position.core.drawdown_controller；zephyr.shared.state_store（JsonStateStore+AppendOnlyDedupSet Crash-only 外部化）；zephyr.governance.strategies.strategy_base；zephyr.pf_core.topn_momentum_strategy（--strategy 可选）；zephyr.shared.infra.process_pool（run_subprocess_hidden SSoT）；zephyr.ex_core.pre_execution_checker（MOD-EX-024 执行前四级闸门，经 TradingSession.attach_pre_execution_gate 挂载）；zephyr.compliance.discipline_prohibition_checker（C-004 纪律闸补仓腿 + KillSwitchLite 策略级熔断，F62 诚实起点批）；zephyr.compliance.compliance_log（合规证据日志注入点，测试用 tmp_path）；zephyr.shared.contracts.position（补仓腿现价派生读 PositionSnapshot）
# [CONSUMERS] 57 号文 §2 盘中模拟盘——交易日 09:25 前人工拉起；--service=LiveStrategyAdapter 常驻服务模式（GAP-2 残余① CLI 接线已落）；挂计划任务/调度=Owner 窗口
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 仅连 QMT 模拟账户（config/.env.qmt 只读 QMT_SIM_* 两键，实盘前缀键永不触碰——键名真源见 SECRETS.md；NL-2 判据②故此处不落其实盘键名字样）；默认纯会话保活不自动 rebalance（--strategy 缺省=安全默认）；--dry-run 只连不打任何单；有界保活循环 15:05 自动 stop；KeyboardInterrupt 优雅 stop（stop 自动撤未成交单语义保留）；--service 模式 assemble_session 包 StrategySlot 交 LiveStrategyAdapter 监督（异常隔离+退避重启熔断+biz 心跳 tmp/live_strategy_biz.heartbeat），adapter.run(close_at) 有界收场；**风控层必装配**——DrawdownTracker 基线只取券商实时净值（读不到/非正=拒绝装配会话 exit 1，禁兜底常量猜基线）；Kill Switch 状态经 JsonStateStore 外部化（重启存活熔断，#ARCH-QUANT-002 生产零注入治本）；成交经 OrderManager 回调**只入队** AsyncFillDispatcher（回调线程零耗时，落账在派发线程），会话 stop() MUST 排空派发队列（含 --service 退避重启路径，排不掉=CRITICAL 出声）供盘中对账冻结；**执行前四级闸门必装配**（H5-P0 决策门零接线清偿）——探针真源=DefaultRiskValidator.kill_switch_active，禁静默退化为"熔断级不判定"
# [MODIFY-GUARD] 57_daily_cycle_sop.md §2/§7 GAP-2；#ARCH-DAILY-CYCLE-GAP23-001
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=正常收场（含 dry-run 成功/收盘自动停/Ctrl+C 优雅停）；exit 1=连接/装配/运行异常；exit 2=参数非法
# [TESTS] tests/scripts/test_start_paper_session.py
# [A_module] module_id=MOD-SCRIPT-start_paper_session | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 57 号文 §2 交易日 09:25 前人工拉起的盘中会话保活 CLI（过渡形态，非常驻 daemon），与 commit_queue.py 同类
# noqa: m10-time-trigger  M10豁免: 保活循环为"有界 while now<收盘时点 + time.sleep 轮询"（PERM-TRIGGER 门禁批准的过渡形态结构），非 while True 永久轮询
# @高风险动作: 连接 QMT 模拟盘并可由 TradingSession 下单（模拟账户）；--dry-run 显式只连不下单；stop() 撤全部未成交单
"""start_paper_session.py — 模拟盘交易日启动脚本 MVP（57 号文 GAP-2，Owner 2026-08-21 批准施工）

真源
----
- 57 号文 §2（盘中模拟盘运行：当前形态=手动拉起 TradingSession 进程并保活；
  常驻服务=GAP-2——本脚本即该缺口的过渡形态施工件，**非 daemon 不挂调度**）。
- 57 号文 §1（开盘前检查三命令口径：QMT 进程/调度器状态/数据源健康——
  本脚本启动前打印检查项，C1 QMT 进程实探，C3 miniqmt connect_ok 由
  broker.connect() 探活覆盖）。

功能
----
``python scripts/start_paper_session.py [--strategy NAME] [--dry-run] [--universe ...] [--service]``：

1. 读 config/.env.qmt 模拟账户（QMT_SIM_PATH/QMT_SIM_ACCOUNT）→ 构造 MiniQmtBroker。
2. 装配 TradingSession（OrderManager 注册 broker + RiskValidationBridge 风控桥 +
   RiskLayerOrchestrator 组合级风控层（回撤/VaR/尾部→仓位上限、EMERGENCY→熔断清算、
   盘中对账→冻结标的、启动恢复→Fail-Closed；回撤基线=券商实时净值，读不到即装配失败）+
   策略/信号/价格提供器）→ session.start()（连接+成交回调注册+风控层启动）。
3. 保活循环（**有界**：``while 现在 < 收盘时点(默认15:05)``，非 while True——
   PERM-TRIGGER 门禁合规）：到点自动 session.stop()；KeyboardInterrupt 优雅
   stop——stop 自动撤未成交单语义保留（trading_session.py L305/L942）。
4. 启动前检查项打印（57 号文 §1 三命令口径，关键两项：C1 QMT 进程实探 +
   C3 miniqmt 连接探活）。
5. ``--service`` 常驻服务模式（GAP-2 残余① CLI 接线）：assemble_session 包
   StrategySlot 交 LiveStrategyAdapter 监督运行——异常隔离+退避重启熔断+
   biz 心跳 tmp/live_strategy_biz.heartbeat，``adapter.run(close_at=收盘时点)``
   有界收场（到点/KeyboardInterrupt 优雅停，语义与保活循环一致）；
   挂计划任务/调度=Owner 窗口（本脚本不挂任何调度）。

参数
----
- ``--strategy NAME``：默认空=纯会话保活不自动 rebalance（安全默认——
  真信号源（construction_backlog B4）未施工，57 号文 GAP-2 原文登记）。
  可选 ``topn-momentum``（需配 --universe）：mock 信号+小额约束的彩排口径，
  仅模拟盘用途，启动时大字告警。
- ``--dry-run``：只连不打任何单（connect → get_positions 探活 → disconnect），
  冒烟用（--service 同给时 dry-run 优先）。
- ``--service``：常驻服务模式——LiveStrategyAdapter 监督 slot（异常隔离/退避重启
  熔断/biz 心跳）；--poll 在本模式不适用（监督节奏=adapter 心跳 15s）。
- ``--universe a.SH,b.SZ``：--strategy 模式的标的池（逗号分隔）。
- ``--interval N``：已删除（B4 治本 2026-09-05：threading.Timer 周期调仓违反
  trae_060 §3 禁时间触发；调仓触发源=ex_core.rebalance.requested 事件）。
- ``--close-time HH:MM``：保活截止时点（默认 15:05，收盘后 5 分钟收尾缓冲）。
- ``--poll N``：保活轮询秒（默认 30，仅过渡形态保活循环）。
- ``--max-single X``：--strategy 模式单标的权重上限（默认 0.01=1%，冒烟口径）。

生产调用示例（写进 tracker 用）::

    python scripts/start_paper_session.py --dry-run          # 冒烟：只连不下单
    python scripts/start_paper_session.py                    # 交易日 09:25 前拉起，纯保活至 15:05
    python scripts/start_paper_session.py --service          # 常驻服务模式（LiveStrategyAdapter 监督至 15:05）
    python scripts/start_paper_session.py --strategy topn-momentum --universe 600000.SH,000001.SZ
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
import time
import uuid
from collections.abc import Callable
from datetime import datetime
from datetime import time as dtime
from decimal import Decimal
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

_REPO_ROOT = Path(__file__).resolve().parents[1]
# 脚本直跑（python scripts/xxx.py）时保证 src 布局可导入（冒烟脚本同口径）
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.compliance.compliance_log import ComplianceLogger  # noqa: E402
from zephyr.compliance.compliance_report_registry import ReportGate  # noqa: E402
from zephyr.compliance.discipline_prohibition_checker import (  # noqa: E402
    DisciplineContext,
    DisciplineGuard,
    KillSwitchLite,
)
from zephyr.compliance.manipulation_realtime_monitor import (  # noqa: E402
    ManipulationRealtimeMonitor,
)
from zephyr.ex_core.async_fill_dispatcher import AsyncFillDispatcher  # noqa: E402
from zephyr.ex_core.cancel_rate_guard import CancelRateGuard  # noqa: E402
from zephyr.ex_core.live_strategy_adapter import LiveStrategyAdapter, StrategySlot  # noqa: E402
from zephyr.ex_core.order_manager import OrderManager  # noqa: E402
from zephyr.ex_core.position_reconciler import PositionReconciler  # noqa: E402
from zephyr.ex_core.position_tracker.tracker import PositionTracker  # noqa: E402
from zephyr.ex_core.risk_layer_orchestrator import RiskLayerConfig, RiskLayerOrchestrator  # noqa: E402
from zephyr.ex_core.signal_providers import make_mock_price_provider, make_mock_signal_provider  # noqa: E402
from zephyr.ex_core.trading_session import DisciplineCtxProvider, TradingSession, TradingSessionConfig  # noqa: E402
from zephyr.governance.adapters.risk_validation_bridge import RiskValidationBridge  # noqa: E402
from zephyr.governance.strategies.strategy_base import StrategyBase  # noqa: E402
from zephyr.position.core.drawdown_controller import DrawdownController  # noqa: E402
from zephyr.risk.core.drawdown_tracker import DrawdownTracker  # noqa: E402
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor  # noqa: E402
from zephyr.risk.core.var_calculator import VaRCalculator  # noqa: E402
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator  # noqa: E402
from zephyr.shared.contracts.fill import Fill  # noqa: E402
from zephyr.shared.contracts.order import Order  # noqa: E402
from zephyr.shared.contracts.position import PositionSnapshot  # noqa: E402
from zephyr.shared.contracts.risk_limits import RiskLimits  # noqa: E402
from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402
from zephyr.shared.state_store import AppendOnlyDedupSet, JsonStateStore  # noqa: E402

_logger = logging.getLogger(__name__)

#: QMT 模拟盘配置文件（只读 QMT_SIM_* 两键；实盘前缀键本脚本永不读取，键名真源见 SECRETS.md
#: ——NL-2 判据② 禁 AI 侧文件出现实盘密钥键名字样）
_ENV_QMT_PATH = _REPO_ROOT / "config" / ".env.qmt"
#: A 股交易时刻口径=北京时区（与 trading_session._SHANGHAI_TZ 同口径）
_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
#: OrderManager 内注册 broker 的标识（与 TradingSessionConfig.broker_id 对齐）
_BROKER_ID = "miniqmt"
#: --strategy 可选策略注册表键（MVP 仅 topn-momentum，与冒烟脚本同件）
_STRATEGY_TOPN_MOMENTUM = "topn-momentum"
#: Crash-only 风控状态外部化根目录（#ARCH-QUANT-002）：kill_switch/var_model_status/
#: rollback_state 三命名空间 + 本地持仓账 fill_id 去重集同根，人工核查即 ls 此目录。
#: 测试 MUST 经 state_dir 注入 tmp_path（宪法 §9.6 禁写生产 data/）。
_RISK_STATE_DIR = _REPO_ROOT / "data" / "runtime" / "state"
#: fill_id 去重集文件名前缀（每次装配一份唯一 token——券商 fill 回调链是 append，
#: --service 崩溃重启会重造会话而旧会话的死回调仍在链上先跑；若共用同一文件，
#: 死回调会替新账本"抢先登记"fill_id，令新 tracker 漏入账→对账假漂移→误冻结）。
#: 新账本启动即经 recover_from_broker 把当日成交号登记入自己的去重集，语义不丢。
_FILL_DEDUP_PREFIX = "paper_fill_ids"
#: 会话停机时等待成交派发线程排空的秒数：在途成交未落本地账就重启，新会话拿到的
#: 账本必然落后于券商 → 首轮对账误冻结。超时不阻断停机（停机优先），但大声出声。
_FILL_DISPATCH_DRAIN_TIMEOUT_S = 5.0


# ── 纯保活占位策略（默认安全态）──────────────────────────────────────────────


class _KeepAliveStrategy(StrategyBase):
    """纯保活占位策略——永远返回空目标权重（57 号文 GAP-2 安全默认）。

    默认模式 rebalance_interval_seconds=0 且 universe=[]，自动调仓从不会被
    触发；本策略是 TradingSession 构造契约（strategy 必填）的最小满足件。
    注意：空目标权重 + 非空持仓在 _compute_order_deltas 语义下=清仓卖出，
    故保活模式 MUST 保持 interval=0 无人手动调 rebalance——本脚本保证。
    """

    def generate_target_weights(
        self,
        universe: list[str],
        signals: dict[str, float],
        constraints: dict[str, Any],
    ) -> dict[str, float]:
        return {}


# ── CLI 参数 ─────────────────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 参数解析。"""
    parser = argparse.ArgumentParser(
        prog="start_paper_session.py",
        description="模拟盘交易日启动脚本（57 号文 GAP-2：默认纯保活过渡形态不下单；--service=LiveStrategyAdapter 常驻服务模式）",
    )
    parser.add_argument(
        "--strategy",
        default="",
        help=f"策略名（默认空=纯会话保活不自动 rebalance，安全默认）；可选 {_STRATEGY_TOPN_MOMENTUM}",
    )
    parser.add_argument("--dry-run", action="store_true", help="只连不打任何单（connect→探活→disconnect），冒烟用")
    parser.add_argument(
        "--service",
        action="store_true",
        help="常驻服务模式：assemble_session 包 StrategySlot 交 LiveStrategyAdapter 监督"
        "（异常隔离+退避重启熔断+biz 心跳 tmp/live_strategy_biz.heartbeat），run(close_at) 有界收场",
    )
    parser.add_argument(
        "--universe", default="", help="标的池，逗号分隔（如 600000.SH,000001.SZ）；--strategy 模式必填"
    )
    # --interval 已删除（B4 治本 2026-09-05：Timer 周期调仓违反禁时间触发；
    # 调仓触发源=ex_core.rebalance.requested 事件）
    parser.add_argument("--close-time", default="15:05", help="保活截止时点 HH:MM（默认 15:05 北京时区）")
    parser.add_argument("--poll", type=int, default=30, help="保活轮询秒（默认 30）")
    parser.add_argument("--max-single", type=float, default=0.01, help="--strategy 模式单标的权重上限（默认 0.01）")
    return parser.parse_args(argv)


def _parse_universe(raw: str) -> list[str]:
    """逗号分隔标的池解析（去空白去空段）。"""
    return [s.strip() for s in raw.split(",") if s.strip()]


def _parse_close_time(raw: str) -> dtime:
    """HH:MM 解析（非法→ValueError 由 main 转 exit 2）。"""
    return datetime.strptime(raw, "%H:%M").time()


# ── config/.env.qmt 读取（冒烟脚本同口径，只读 QMT_SIM_*）─────────────────────


def load_qmt_sim_config(env_path: Path = _ENV_QMT_PATH) -> tuple[str, str]:
    """从 config/.env.qmt 读模拟盘配置（只读 QMT_SIM_PATH/QMT_SIM_ACCOUNT）。

    Raises:
        FileNotFoundError: 配置文件缺失。
        ValueError: 两键任一缺失。
    """
    if not env_path.is_file():
        raise FileNotFoundError(f"QMT 配置文件不存在: {env_path}")
    qmt_path = ""
    qmt_account = ""
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip()
        if key == "QMT_SIM_PATH":
            qmt_path = val
        elif key == "QMT_SIM_ACCOUNT":
            qmt_account = val
    if not qmt_path or not qmt_account:
        raise ValueError(f"{env_path.name} 缺少 QMT_SIM_PATH 或 QMT_SIM_ACCOUNT")
    return qmt_path, qmt_account


# ── 启动前检查（57 号文 §1 三命令口径）───────────────────────────────────────


def check_qmt_process() -> bool | None:
    """C1 QMT 进程实探（tasklist 子串扫描 XtMiniQmt，SSoT=run_subprocess_hidden）。

    Returns:
        True=进程在；False=不在；None=非 Windows/探测失败（SKIP 不阻断，
        由 broker.connect() 探活兜底判死）。
    """
    if sys.platform != "win32":
        return None
    try:
        result = run_subprocess_hidden(["tasklist"], timeout=15)
    except Exception:  # noqa: BLE001 — 探测失败=SKIP，不阻断启动（connect 探活兜底）
        _logger.warning("tasklist 探测异常（降级 SKIP）", exc_info=True)
        return None
    return "xtminiqmt" in result.stdout.lower()


def print_prestart_checks(qmt_alive: bool | None) -> None:
    """打印启动前检查项（57 号文 §1 三命令口径；关键两项=C1+C3）。"""
    c1 = {
        True: "PASS（XtMiniQmt 进程在）",
        False: "FAIL（未检出——57 号文口径：当日模拟盘应 SKIP 并 tracker 登记 C 类）",
        None: "SKIP（非 Windows 或探测失败，由 connect 探活兜底）",
    }[qmt_alive]
    print("=== 启动前检查项（57 号文 §1 三命令口径）===")
    print(f"[C1] QMT 进程: {c1}")
    print(
        "[C2] 调度器状态（人工确认）: python -m zephyr.data status —— kline_daily_incremental/stk_limit_premarket 最近运行 SUCCESS"
    )
    print("[C3] 数据源健康（人工确认）: 十源检查 miniqmt 必须 connect_ok——本脚本 broker.connect() 即该项探活")


# ── 装配（broker / 会话）─────────────────────────────────────────────────────


def build_sim_broker() -> object:
    """读 config/.env.qmt 模拟账户 → 构造 MiniQmtBroker（延迟 import xtquant 依赖）。"""
    qmt_path, qmt_account = load_qmt_sim_config()
    # 延迟 import：--dry-run 冒烟外的环境允许 xtquant 缺席时装配错误清晰抛出
    from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker

    return MiniQmtBroker(path=qmt_path, session_id="paper_session", account_id=qmt_account)


def _make_xtdata_price_provider() -> Callable[[list[str]], dict[str, Decimal]]:
    """xtdata 最新收盘价价格提供器（--strategy 模式用；冒烟脚本同口径）。"""

    def _provider(universe: list[str]) -> dict[str, Decimal]:
        try:
            from xtquant import xtdata
        except ImportError:
            _logger.warning("xtquant 不可用，价格提供器返回空（本轮回合零 delta）")
            return {}
        prices: dict[str, Decimal] = {}
        for symbol in universe:
            try:
                data = xtdata.get_market_data_ex([], [symbol], period="1d", count=1)
                df = data.get(symbol) if data else None
                if df is not None and len(df) > 0:
                    close = float(df["close"].iloc[-1])
                    if close > 0:
                        prices[symbol] = Decimal(str(close))
            except Exception:  # noqa: BLE001 — 单标的取价失败跳过，不阻断整批
                _logger.warning("获取 %s 价格失败（跳过）", symbol, exc_info=True)
        return prices

    return _provider


def _account_nav(broker: object) -> tuple[Decimal, float]:
    """读券商实时快照取 (cash, nav)——回撤基线唯一真源，禁兜底常量。

    为什么要 fail-fast 而不是给个默认 100 万：基线偏高=回撤永不觉醒（假安全），
    偏低=开盘即误熔断（假停机），两种错法都比不上"起不来"这个可运维的结论。

    Raises:
        ValueError: 快照不可读或净值非正/非有限。
    """
    try:
        snapshot = broker.get_positions()  # type: ignore[attr-defined]
    except Exception as exc:  # noqa: BLE001 — 基线不可得=拒装风控层（上层 exit 1）
        raise ValueError(f"账户快照不可读，风控基线不可得（{type(exc).__name__}: {exc}）") from exc
    cash = Decimal(str(snapshot.cash)) if snapshot.cash is not None else Decimal("0")
    mv = snapshot.total_market_value
    market_value = Decimal(str(mv)) if mv is not None else Decimal("0")
    nav = float(cash + market_value)
    if not math.isfinite(nav) or nav <= 0:
        raise ValueError(f"账户净值非法（cash={cash} market_value={market_value} nav={nav}）——无法建立回撤基线")
    return cash, nav


def _wire_position_book_feed(
    order_manager: OrderManager,
    tracker: PositionTracker,
    *,
    strategy_id: str,
) -> AsyncFillDispatcher:
    """券商成交 → 入队 → 派发线程落本地持仓账（盘中对账链的前置件）。

    为什么必须异步（AsyncFillDispatcher 的立身理由，40_execution_broker §决策①
    工程约束1）：券商成交回报在 miniQMT 底层 C++ 线程内回调，回调里任何耗时操作
    都会拖慢后续回报（该模块记录的实盘案例=3 秒延迟），而 ``tracker.apply_fill``
    要 append fill_id 去重文件=同步磁盘 I/O。故回调线程只做 O(1) 入队，落账
    在消费线程。

    fill.order_id 双口径（miniqmt_broker.query_trades_today：券商推送带 broker
    订单号，而 OrderManager 以本地 UUID 为键）故两路都查。查不到只告警不入账：
    漏入账会在下一轮对账暴露为 drift 并冻结该标的（停错方向，不静默放行）。
    """

    def _lookup_order(fill: Fill) -> Order | None:
        order = order_manager.get_order(fill.order_id)
        if order is None:
            order = next((o for o in order_manager.orders.values() if o.broker_order_id == fill.order_id), None)
        if order is None:
            _logger.warning(
                "成交无法配对本地订单，跳过入账（将经对账暴露为 drift）: order_id=%s symbol=%s",
                fill.order_id,
                fill.symbol,
            )
        return order

    dispatcher = AsyncFillDispatcher(
        consumer=lambda fill, order: tracker.apply_fill(fill, order.side),
        lookup_order_fn=_lookup_order,
        consumer_name=f"paper-fill-dispatch-{strategy_id}",
    )
    # 先起消费线程再挂回调：未 start 时 enqueue 仍会成功但永不消费（Queue 静默积压），
    # 顺序反了就把"成交不见了"变成一种可能。
    dispatcher.start()
    order_manager.register_fill_callback(dispatcher.enqueue)
    return dispatcher


def _attach_dispatcher_teardown(
    session: TradingSession,
    dispatcher: AsyncFillDispatcher,
) -> None:
    """把派发器排空挂进会话停机路径（成交入账线程不得靠 daemon 身份"自然死"）。

    TradingSession.stop() 是全仓唯一拆除口（CLI 收盘/Ctrl+C 与
    LiveStrategyAdapter._stop_slot 退避重启都经此处），故在此包一层而不是改
    [SAFETY] M 的会话契约。在途成交未落账就重启=新会话账本落后于券商，
    首轮对账会把正常仓位误判为漂移并冻结标的——排空失败必须大声。
    """
    original_stop = session.stop

    def _stop() -> None:
        try:
            original_stop()
        finally:
            drained = dispatcher.stop(timeout=_FILL_DISPATCH_DRAIN_TIMEOUT_S)
            if not drained:
                stats = dispatcher.stats
                _logger.critical(
                    "成交派发器未能在 %ss 内排空（queue_size=%d enqueued=%d dispatched=%d errors=%d）"
                    "——本地持仓账落后于券商，下一轮对账将冻结相关标的，须人工核对成交",
                    _FILL_DISPATCH_DRAIN_TIMEOUT_S,
                    stats.queue_size,
                    stats.enqueued,
                    stats.dispatched,
                    stats.errors,
                )

    session.stop = _stop  # type: ignore[method-assign]
    # 留把手：运维/测试经 session.fill_dispatcher.stats 看积压与去重数
    session.fill_dispatcher = dispatcher  # type: ignore[attr-defined]


def _log_position_drift(result: object) -> None:
    """持仓对账漂移大声出声（冻结已生效，此处只负责让人看见）。"""
    _logger.critical(
        "持仓对账漂移: 冻结标的=%s 差异=%s",
        sorted(result.frozen_symbols),  # type: ignore[attr-defined]
        [(d.symbol, f"系统{d.system_qty}/券商{d.broker_qty}") for d in result.drifts],  # type: ignore[attr-defined]
    )


def assemble_risk_layer(
    broker: object,
    order_manager: OrderManager,
    *,
    strategy_id: str,
    kill_switch_owner: DefaultRiskValidator,
    state_store: JsonStateStore,
    initial_cash: Decimal,
    nav_baseline: float,
) -> tuple[RiskLayerOrchestrator, AsyncFillDispatcher]:
    """装配组合级风控层（H5-P0 治本：编排器全仓零生产装配=四链全盲）。

    四条链在此点亮（前 3 条由 TradingSession.start/rebalance 消费）：
      1. 回撤/VaR/尾部 → position_cap 缩放目标权重、allow_new_position 禁新开仓
      2. 回撤/尾部 EMERGENCY → 单一仲裁点熔断清算（状态层=同一 DefaultRiskValidator，
         与订单级校验共享同一熔断闩，避免"风控桥放行/编排层熔断"双头）
      3. 券商持仓 vs 本地账 盘中对账 → is_symbol_frozen 下单前硬拦
      4. 启动恢复 recover_from_broker → 重建完成前 Fail-Closed 禁单

    today_fills_probe 显式改指 ``query_trades_today``：RiskLayerConfig 出厂默认
    ``get_today_fills`` 全仓无任何 broker 实现（探针名是幻影，链 4 的成交重放
    恒降级为空列表）——本处是唯一生产装配点，按真名注入，不改 Safety-H 默认值。

    链 3 的进料（成交→本地账）走异步派发线程：返回 (编排器, 派发器)，调用方 MUST
    经 _attach_dispatcher_teardown 把派发器挂进会话停机路径，否则在途成交随进程退出。

    未接线（缺市场级进料口生产者，登记 tracker）：systemic_input_provider（需
    盘口 sell_pressure/spread，sentiment_index 全仓无产源）、rollback_metrics_provider
    （需 daily_loss/reject_rate，且注入即令启动姿态 fail-closed 落 SOFT_HALT、
    解除须人工 RCA 双人复核——属 Owner 运维门位，不由模拟盘装配脚本代开）。
    """
    tracker = PositionTracker(
        initial_cash=initial_cash,
        portfolio_id=f"paper-book-{strategy_id}",
        dedup_store=AppendOnlyDedupSet(
            state_store.root_dir / f"{_FILL_DEDUP_PREFIX}-{strategy_id}-{uuid.uuid4().hex[:8]}.txt"
        ),
    )
    dispatcher = _wire_position_book_feed(order_manager, tracker, strategy_id=strategy_id)

    def _open_orders_provider() -> dict[str, dict]:
        return {o.broker_order_id: {} for o in order_manager.get_open_orders() if o.broker_order_id}

    def _order_stats_provider() -> tuple[int, int]:
        """R1-02 撤单率预检进料（drawdown_liquidation_guard §6.14①，zc-lane-k-20260927）。

        数据源=OrderManager.declaration_guard（CancelRateGuard 滚动窗口
        total_cancels/total_resolved）；未注入 guard=(0,0) → guard 判
        "当日无委托，无撤单率约束"，不阻断清算腿（fail-open）。
        """
        guard = order_manager.declaration_guard
        if guard is None:
            return (0, 0)
        return (guard.total_cancels, guard.total_resolved)

    return RiskLayerOrchestrator(
        drawdown_controller=DrawdownController(),
        drawdown_tracker=DrawdownTracker(initial_net_value=nav_baseline),
        var_calculator=VaRCalculator(),
        tail_risk_monitor=TailRiskMonitor(),
        broker=broker,  # type: ignore[arg-type]
        position_tracker=tracker,
        kill_switch_owner=kill_switch_owner,
        reconciler=PositionReconciler(
            system_source=tracker,
            broker_source=broker,  # type: ignore[arg-type]
            on_drift=_log_position_drift,
        ),
        open_orders_provider=_open_orders_provider,
        order_stats_provider=_order_stats_provider,
        config=RiskLayerConfig(today_fills_probe="query_trades_today"),
        state_store=state_store,
    ), dispatcher


# ── C-004 合规闸：诚实起点两把（纪律闸补仓腿 + 策略级熔断）───────────────────
# 判据口径（43 号 §4.3，MOD-CMP-002）：四条严禁腿里**只有真源可派生的那条**才装；
# 未装的腿必须在装配现场可见地宣告，不许用静默默认值伪装成已防。

#: 盘上无源的 20 日双基线哨兵值。**故意不用 0**：
#: ``DisciplineGuard._check_revenge`` 的判据带 ``freq/size_baseline_20d > 0`` 前置
#: （discipline_prohibition_checker.py:268/:270 实测），0 与"无数据"行为一致，
#: 却会被下游读成"基线确实测得为 0"——那是静默假闸的伪装面。负值不可能充当基线，
#: 只表达"无源"，且报复腿的未激活态由装配横幅 + DISCIPLINE_LEG_ARMING 显式宣告。
#: 真源侧实测：对口历史表 c1_market.execution_report 仅 1 行，20 日窗从未被积累。
_NO_SOURCE_BASELINE: float = -1.0

#: 四条严禁腿在本正门的真实激活态（值口径 armed / not_armed_*）。
#: 本表是装配横幅与测试断言的**同一真源**，禁另抄一份散文清单。
DISCIPLINE_LEG_ARMING: dict[str, str] = {
    "ADDING_TO_LOSER": "armed",  # 被套补仓：position_pnl_pct 可由 tracker 均价 + 现价派生
    "CHASING": "not_armed_no_signal_anchor",  # 踏空追高：无信号参考价/30min 拉升源
    "REVENGE_TRADING": "not_armed_no_20d_baseline",  # 亏损报复：20 日双基线盘上无源
    "OVERCONFIDENCE": "not_armed_no_win_streak",  # 盈利骄傲：连盈笔数盘上无源（仅 Warning 级）
}

#: 人话注解（启动横幅逐腿打印，与 DISCIPLINE_LEG_ARMING 同键）。
_LEG_ARMING_NOTES: dict[str, str] = {
    "ADDING_TO_LOSER": "真装：浮亏=现价/均价-1，均价源=PositionTracker.avg_costs（CTR-006 无成本字段，"
    "故必须走 tracker 侧），现价源=券商快照派生价，退化=本单申报价",
    "CHASING": "追高腿未激活：signal_ref_price/surge_30min_pct 传 None=MOD-CMP-002 官方"
    '"无锚不可判"跳过口（设计内语义，不是降级凑数）',
    "REVENGE_TRADING": "报复腿未激活：freq_baseline_20d/size_baseline_20d 盘上无源（哨兵 -1，"
    "禁 0 占位）+daily_pnl_pct/projected_daily_freq 亦无源→该腿本会话恒不判",
    "OVERCONFIDENCE": "骄傲腿未激活：win_streak 盘上无源恒 0（该腿仅 Warning 不阻断）",
}


def _discipline_leg_arming_status(tracker: PositionTracker | None) -> dict[str, str]:
    """按装配现场实际可用的供数面产出腿状态表（tracker 取不到时补仓腿也明示未装）。"""
    status = dict(DISCIPLINE_LEG_ARMING)
    if tracker is None:
        status["ADDING_TO_LOSER"] = "not_armed_no_position_cost_source"
    return status


def _position_current_price(order: Order, positions: PositionSnapshot) -> float | None:
    """现价：优先券商持仓快照派生价（市值/数量），退化用本单申报价。

    两路都是本会话已有的供数面，不新增行情依赖。快照缺市值/数量时用申报价——
    限价单申报价即委托人认可的现价，口径写在这里供审阅，不静默猜数。
    """
    qty = positions.holdings.get(order.symbol)
    market_value = positions.market_values.get(order.symbol)
    if qty is not None and market_value is not None and qty > 0 and market_value > 0:
        return float(market_value / qty)
    if order.limit_price is not None and order.limit_price > 0:
        return float(order.limit_price)
    return None


def _position_pnl_pct(
    tracker: PositionTracker | None,
    order: Order,
    positions: PositionSnapshot,
) -> float | None:
    """该标的持仓浮盈（小数）；任一环节无源返回 None（补仓腿不判，由调用处出声）。"""
    if tracker is None:
        return None
    try:
        avg_cost = tracker.avg_costs.get(order.symbol)
        if avg_cost is None or avg_cost <= 0:
            return None
        current = _position_current_price(order, positions)
        if current is None:
            return None
        return float(current) / float(avg_cost) - 1.0
    except Exception:  # noqa: BLE001 — 失效类型不可枚举，降级为"不可判"而非上抛
        _logger.warning("[DISCIPLINE] 浮亏取数失效（本单不判补仓）: symbol=%s", order.symbol, exc_info=True)
        return None


def _make_discipline_ctx_provider(
    tracker: PositionTracker | None,
    *,
    normal_exposure: float,
) -> DisciplineCtxProvider:
    """C-004 纪律闸上下文提供器（就地闭包；OrderRequest 由会话侧 _make_order_request 代做）。

    诚实起点=本批只装补仓腿，其余三腿明示未装（键值见 DISCIPLINE_LEG_ARMING）：
      - 追高腿 signal_ref_price/surge_30min_pct=None（官方无锚跳过口）；
      - 报复腿双基线=_NO_SOURCE_BASELINE 哨兵、daily_pnl/projected_freq 无源；
      - 骄傲腿 win_streak=0（无源，且该腿仅 Warning）。
    每个字段自带失效降级（返回 None/哨兵），绝不因取数失败上抛——会话侧对
    provider 异常是**逐单 Fail-Closed 全拒**，那是失效面而非判据面（有测钉住）。
    """
    blind_announced: set[str] = set()

    def _provide(order: Order, positions: PositionSnapshot) -> DisciplineContext:
        pnl = _position_pnl_pct(tracker, order, positions)
        if (
            pnl is None
            and tracker is not None
            and positions.holdings.get(order.symbol, Decimal("0")) > 0
            and order.symbol not in blind_announced
        ):
            blind_announced.add(order.symbol)
            _logger.warning(
                "[DISCIPLINE] 补仓腿盲区: symbol=%s 有持仓但均价底档缺失（隔夜仓未经本会话成交派生）"
                "——该标的本会话不判补仓，这是明示盲区不是放行判据",
                order.symbol,
            )
        return DisciplineContext(
            signal_ref_price=None,
            surge_30min_pct=None,
            position_pnl_pct=pnl,
            win_streak=0,
            normal_exposure=normal_exposure,
            daily_pnl_pct=0.0,
            projected_daily_freq=0.0,
            freq_baseline_20d=_NO_SOURCE_BASELINE,
            size_baseline_20d=_NO_SOURCE_BASELINE,
        )

    return _provide


def _print_discipline_declaration(leg_status: dict[str, str]) -> None:
    """装配现场大声宣告"装了什么/没装什么"（横幅与 DISCIPLINE_LEG_ARMING 同源）。

    未激活的腿必须在此可见——判据的一部分，不是免责声明。
    """
    print("[DISCIPLINE] 纪律闸（MOD-CMP-002）已装配，逐腿激活态如下：")
    for behavior, state in leg_status.items():
        print(f"[DISCIPLINE]   {behavior}: {state} —— {_LEG_ARMING_NOTES[behavior]}")
    print(f"[DISCIPLINE][STATUS] {json.dumps(leg_status, ensure_ascii=False, sort_keys=True)}")
    print(
        "[DISCIPLINE] 策略级熔断 KillSwitchLite 已装配：state_path=默认主仓锚定"
        "（data/compliance_log/kill_switch_lite_state.json，恒锚主仓故 worktree 无路径歧义）"
        " 语义=文件不存在→is_blocked 放行；文件存在但 JSON 读不出→全拒（Fail-Closed）；"
        "熔断状态由报复腿触发（本批报复腿未激活，故本会话不会自行触发）"
    )
    _logger.warning(
        "[DISCIPLINE] 明示未装（本批口径=诚实起点只装两把，其余腿缺真源不凑数）："
        "追高腿/报复腿/骄傲腿未激活，只装补仓腿 + 策略级熔断锁"
    )


def assemble_session(
    args: argparse.Namespace,
    broker: object,
    *,
    state_dir: Path | None = None,
    compliance_log_path: Path | None = None,
) -> TradingSession:
    """装配 TradingSession（57 号文 §2 过渡形态编排）。

    默认（--strategy 空）：_KeepAliveStrategy + 空 universe
    → start() 仅连接+注册成交回调，永不自动 rebalance（纯保活安全默认）。
    --strategy topn-momentum：mock 信号 + --universe，启动后一次初始调仓 +
    事件驱动调仓（ex_core.rebalance.requested；彩排口径——LiveStrategyAdapter
    真信号源未施工，启动时大字告警）。
    B4 治本（2026-09-05）：原 --interval（threading.Timer 周期调仓）已删除——
    违反 trae_060 §3 禁时间触发；触发源改为事件（未来真信号源 emit）。

    H5-P0 治本（2026-09-16）：本函数 MUST 装配 RiskLayerOrchestrator 并注入
    ``risk_layer=``——此前全仓无任何生产装配点，回撤/VaR/尾部信号产而不消
    （编排器测试全绿但生产零实例化=消防栓装了没接水管）。风控基线只取券商
    实时净值，读不到即抛（main 转 exit 1），绝不带着猜出来的基线开盘。

    F62 诚实起点批：C-004 合规闸只装**两把**——纪律闸补仓腿（position_pnl_pct 由
    PositionTracker 均价面 + 现价派生）与策略级熔断 KillSwitchLite；追高/报复/骄傲
    三腿盘上无真源，**明示未装**（逐腿状态打印 + 机生 JSON 行 + DISCIPLINE_LEG_ARMING
    常量三处同源，测试可断）。guard 与 ctx_provider 必须成对注入（会话装配期 fail-fast）。

    F62 装配批（2026-09-27）：本函数 MUST 注入 C-002 三道订单级合规闸
    （``report_gate``/``declaration_guard``/``manipulation_monitor``）并把同一
    ``CancelRateGuard`` 实例透传 ``cancel_rate_guard=``——三门代码与测试全绿但
    生产零注入=闸装了没通水；计数实例分裂会让日申报 1 万笔阻断线假激活
    （TradingSession 同实例防护直接 raise，43 号 §7.4/§8/§10）。

    Args:
        state_dir: 风控状态外部化根目录（None=生产路径，测试 MUST 注入 tmp_path）。
        compliance_log_path: 合规证据日志落点（None=生产 data/compliance_log；
            测试 MUST 注入 tmp_path——根宪法 §9 第 6 条禁测试写生产 data/）。
    """
    # C-002 三道订单级合规闸（F62 装配批，43 号 §7.4/§8/§7.3）：注入即生效，
    # 未注入=该闸跳过——故本正门 MUST 全三门齐装。
    # 同实例硬约束：CancelRateGuard 一个对象同时给 OrderManager（record_submit/
    # record_cancel 计数）与 TradingSession（阻断线读数），分裂双实例会让 1 万笔
    # 日申报防线计数失明（trading_session.py 同实例防护直接 raise）。
    declaration_guard = CancelRateGuard()
    report_gate = ReportGate()
    manipulation_monitor = ManipulationRealtimeMonitor()
    order_manager = OrderManager(
        report_gate=report_gate,
        declaration_guard=declaration_guard,
        manipulation_monitor=manipulation_monitor,
    )
    # 冻结集合只由报单/撤单/成交事件喂入，不 attach 就等于没接这道闸（43 号 §10 被动观察边界）
    manipulation_monitor.attach_order_manager(order_manager)
    order_manager.register_broker(_BROKER_ID, broker)
    state_store = JsonStateStore(state_dir or _RISK_STATE_DIR)
    validator = DefaultRiskValidator(state_store=state_store)
    risk_validator = RiskValidationBridge(validator)
    now = datetime.now(_SHANGHAI_TZ)

    if args.strategy == "":
        strategy: StrategyBase = _KeepAliveStrategy()
        universe: list[str] = []
        signal_provider = make_mock_signal_provider({})
        price_provider = make_mock_price_provider({})
        strategy_id = "paper-keepalive"
        constraints: dict[str, Any] = {"top_n": 0, "max_single": 0.0}
    elif args.strategy == _STRATEGY_TOPN_MOMENTUM:
        # 延迟 import：--strategy 显式开启才加载策略件
        from zephyr.pf_core.topn_momentum_strategy import TopNMomentumStrategy

        universe = _parse_universe(args.universe)
        strategy = TopNMomentumStrategy()
        # mock 信号（彩排口径：全部 1.0 等强——TopN 退化为 universe 等权；
        # 真信号源=construction_backlog B4 待施工，57 号文 GAP-2 原文登记）
        signal_provider = make_mock_signal_provider({s: 1.0 for s in universe})
        price_provider = _make_xtdata_price_provider()
        strategy_id = args.strategy
        constraints = {"top_n": len(universe), "max_single": args.max_single}
    else:
        raise ValueError(f"未知策略: {args.strategy!r}（可选: {_STRATEGY_TOPN_MOMENTUM}）")

    initial_cash, nav_baseline = _account_nav(broker)
    risk_layer, fill_dispatcher = assemble_risk_layer(
        broker,
        order_manager,
        strategy_id=strategy_id,
        kill_switch_owner=validator,
        state_store=state_store,
        initial_cash=initial_cash,
        nav_baseline=nav_baseline,
    )
    print(
        f"[RISK] 组合级风控层已装配：回撤基线={nav_baseline:.2f}（券商实时净值）"
        f" 熔断状态外部化={state_store.root_dir}"
        " 成交探针=query_trades_today"
        " 成交入账=异步派发线程（回调内只入队）"
    )
    print(
        "[RISK] 未接线（缺市场级进料口生产者，已登记 tracker）：systemic_input_provider"
        "（LEVEL_3 逃生链）、rollback_metrics_provider（五态降级机）——仓位上限/熔断/对账/启动恢复四链已生效"
    )
    if validator.kill_switch_active:
        print("[RISK][CRITICAL] 持久化恢复=启动即熔断态——本会话禁止任何新单，须人工复位 kill_switch 记录后重启")

    config = TradingSessionConfig(
        universe=universe,
        broker_id=_BROKER_ID,
        strategy_id=strategy_id,
        strategy_constraints=constraints,
        risk_limits=RiskLimits(
            as_of_date=now,
            idempotency_key=f"paper-{now.isoformat()}",
            max_single_position=max(args.max_single, 0.01),
        ),
    )
    # ── C-004 合规闸（43 号 §4.3，MOD-CMP-002）：诚实起点两把 ──────────────────
    # 均价真源＝PositionTracker 只读 avg_costs 性质（CTR-006 PositionSnapshot 无
    # 成本字段，故成本只能从 tracker 侧取；本批不改 CTR-006 契约、不给 tracker
    # 加新公共 API）。RiskLayerOrchestrator 无公开 position_tracker 访问器，此处
    # 直读它自己持有的那个实例（同仓既有先例＝tests/scripts/test_start_paper_session.py
    # 里 session._risk_layer._position_tracker 的同一条路）；读不到≠静默降级，
    # 由 _discipline_leg_arming_status 把补仓腿一并宣告为未装。
    discipline_tracker = risk_layer._position_tracker
    compliance_logger = ComplianceLogger(path=compliance_log_path)
    kill_switch_lite = KillSwitchLite(logger=compliance_logger)
    discipline_guard = DisciplineGuard(kill_switch=kill_switch_lite, logger=compliance_logger)
    discipline_ctx_provider = _make_discipline_ctx_provider(
        discipline_tracker,
        normal_exposure=float(config.risk_limits.max_single_position),
    )
    session = TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=risk_validator,
        signal_provider=signal_provider,
        price_provider=price_provider,
        order_manager=order_manager,
        config=config,
        cancel_rate_guard=declaration_guard,
        risk_layer=risk_layer,
        kill_switch=kill_switch_lite,
        discipline_guard=discipline_guard,
        discipline_ctx_provider=discipline_ctx_provider,
    )
    _print_discipline_declaration(_discipline_leg_arming_status(discipline_tracker))
    print(
        "[DISCIPLINE] 未装清单（本批明示）：清单闸 ChecklistCompletionChecker / 交易合规检测 "
        "TradingComplianceDetector / ProgrammaticTradingGuard 均未注入本正门——"
        "清单三项 INTRADAY key 全仓零生产写侧，接上即每轮整批拒单（那是另一种假闸）"
    )
    print(
        "[COMPLIANCE] C-002 三道订单级合规闸已注入：先报告后交易(ReportGate) + "
        "日申报 5000 预警/1 万阻断(同一 CancelRateGuard 实例双注入) + "
        "盘中操纵冻结(ManipulationRealtimeMonitor，已 attach_order_manager 喂事件流)"
    )
    session.attach_pre_execution_gate(kill_switch_probe=lambda: validator.kill_switch_active)
    print(
        "[RISK] 执行前四级闸门已挂载：熔断→交易时段(A股连续竞价)→统一风控快照→否决引擎"
        " 熔断探针=KillSwitch 真源（RiskValidationBridge 不代理 kill_switch_active，故显式注入）"
    )
    _attach_dispatcher_teardown(session, fill_dispatcher)
    return session


def assemble_adapter(
    args: argparse.Namespace,
    broker: object,
    *,
    session_factory: Callable[[argparse.Namespace, object], object] | None = None,
    now_fn: Callable[[], datetime] | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    state_dir: Path | None = None,
    **adapter_kwargs: Any,
) -> LiveStrategyAdapter:
    """常驻服务装配（57 号文 GAP-2 残余① CLI 接线）：assemble_session 包 StrategySlot 交 LiveStrategyAdapter。

    slot 工厂每次调用重造新会话实例（崩溃重启=工厂重造，不携残留订单/计数态——
    StrategySlot 契约）；adapter 监督语义=异常隔离+退避重启熔断+biz 心跳
    tmp/live_strategy_biz.heartbeat（纳入 deadman_switch 监控清单=Owner 窗口，
    tracker #273）。仅承载模拟盘会话（assemble_session 口径连 QMT 模拟账户）。

    Args:
        args: CLI 参数（strategy/universe 等透传 session 装配）。
        broker: 已连接的模拟盘 broker（main 已 connect 探活）。
        session_factory: 会话装配器（测试注入 mock；None=assemble_session）。
        now_fn: 当前时间（测试注入假钟；None=adapter 默认北京时区现在）。
        sleeper: 监督轮询睡眠（测试注入假钟；默认 time.sleep）。
        state_dir: 风控状态外部化根目录（仅默认装配器生效；None=生产路径，
            测试 MUST 注入 tmp_path——宪法 §9.6 禁写生产 data/）。
        adapter_kwargs: 透传 LiveStrategyAdapter（heartbeat_path 等测试注入件）。
    """
    factory = session_factory or (lambda a, b: assemble_session(a, b, state_dir=state_dir))
    slot_id = "paper-keepalive" if args.strategy == "" else f"paper-{args.strategy}"
    slot = StrategySlot(slot_id=slot_id, session_factory=lambda: factory(args, broker))
    return LiveStrategyAdapter([slot], now_fn=now_fn, sleeper=sleeper, **adapter_kwargs)


# ── 主入口 ───────────────────────────────────────────────────────────────────


def main(
    argv: list[str] | None = None,
    *,
    broker_factory: Callable[[], object] | None = None,
    session_factory: Callable[[argparse.Namespace, object], object] | None = None,
    adapter_factory: Callable[[argparse.Namespace, object], object] | None = None,
    adapter_kwargs: dict[str, Any] | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], datetime] | None = None,
    qmt_probe: Callable[[], bool | None] = check_qmt_process,
) -> int:
    """CLI 主入口。

    Args:
        argv: 命令行参数（None=sys.argv）。
        broker_factory: broker 构造器（测试注入 mock；None=生产 build_sim_broker）。
        session_factory: 会话装配器（测试注入 mock；None=assemble_session）。
        adapter_factory: 常驻服务装配器（--service 模式测试注入 mock；None=assemble_adapter）。
        adapter_kwargs: 透传 assemble_adapter/LiveStrategyAdapter（测试注入 heartbeat_path 等）。
        sleeper: 保活轮询睡眠（测试注入假钟；默认 time.sleep）。
        now_fn: 当前时间（测试注入假钟；默认北京时区现在）。
        qmt_probe: C1 QMT 进程探测（测试注入；默认 check_qmt_process）。

    Returns:
        exit code（0=正常收场，1=连接/装配/运行异常，2=参数非法）。
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    now_fn = now_fn or (lambda: datetime.now(_SHANGHAI_TZ))

    # ── 参数校验（fail-fast，exit 2）──
    try:
        close_at = _parse_close_time(args.close_time)
    except ValueError:
        print(f"[ERROR] --close-time 格式非法（期望 HH:MM）: {args.close_time!r}")
        return 2
    if args.strategy and not _parse_universe(args.universe):
        print("[ERROR] --strategy 模式必须显式给 --universe（逗号分隔标的池）")
        return 2

    # ── 启动前检查项（57 号文 §1 三命令口径）──
    print_prestart_checks(qmt_probe())
    if args.strategy:
        print(
            f"[WARN] --strategy={args.strategy} 使用 mock 信号（LiveStrategyAdapter 未施工，57 号文 GAP-2 登记）——仅模拟盘彩排用途"
        )

    # ── 构造 broker 并连接 ──
    try:
        broker = (broker_factory or build_sim_broker)()
        if not broker.connect():
            print("[ERROR] broker.connect() 返回 False（XtMiniQmt 终端未在线？）")
            return 1
    except Exception as exc:  # noqa: BLE001 — 装配/连接失败=运营事件，exit 1 + 指引
        print(f"[ERROR] broker 装配/连接失败（{type(exc).__name__}: {exc}）——检查 XtMiniQmt 是否在线")
        return 1

    # ── dry-run：只连不打任何单（冒烟）──
    if args.dry_run:
        try:
            snapshot = broker.get_positions()
            print("[DRY-RUN] 连接探活 OK（未打任何单）")
            print(
                f"[DRY-RUN] cash={snapshot.cash} total_market_value={snapshot.total_market_value} holdings={dict(snapshot.holdings) if snapshot.holdings else '(空)'}"
            )
            return 0
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] dry-run 探活失败（{type(exc).__name__}: {exc}）")
            return 1
        finally:
            broker.disconnect()

    # ── 常驻服务模式（57 号文 GAP-2 残余①）：assemble_session 包 slot 交 LiveStrategyAdapter 监督 ──
    close_ts = datetime.combine(now_fn().date(), close_at, tzinfo=_SHANGHAI_TZ)
    if args.service:
        try:
            if adapter_factory is not None:
                adapter = adapter_factory(args, broker)
            else:
                adapter = assemble_adapter(
                    args,
                    broker,
                    session_factory=session_factory,
                    now_fn=now_fn,
                    sleeper=sleeper,
                    **(adapter_kwargs or {}),
                )
        except Exception as exc:  # noqa: BLE001 — 装配失败=运营事件，exit 1 + 指引
            print(f"[ERROR] 常驻服务装配失败（{type(exc).__name__}: {exc}）")
            broker.disconnect()
            return 1
        adapter.start()  # slot 异常隔离在 adapter 内（单 slot 装配/启动失败=FAILED 心跳可见，不抛出）
        print(
            f"[INFO] 常驻服务已启动（LiveStrategyAdapter 监督：异常隔离+退避重启熔断，"
            f"biz 心跳 tmp/live_strategy_biz.heartbeat），保活至 {close_ts.isoformat()}"
            "（Ctrl+C 优雅停止，stop 自动撤未成交单）"
        )
        if now_fn() >= close_ts:
            print("[WARN] 当前已过保活截止时点——服务启动即刻收场")
        return adapter.run(close_at=close_at)  # 有界监督循环（非 while True），finally 优雅 stop

    # ── 装配会话并启动 ──
    try:
        session = (session_factory or assemble_session)(args, broker)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] 会话装配失败（{type(exc).__name__}: {exc}）")
        broker.disconnect()
        return 1

    try:
        session.start()
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] session.start() 失败（{type(exc).__name__}: {exc}）")
        broker.disconnect()
        return 1

    # ── 初始调仓（B4 治本 2026-09-05：启动事件触发一次，替代原 Timer 首轮）──
    # --strategy 模式彩排口径：启动即建仓一次；后续调仓由
    # ex_core.rebalance.requested 事件驱动（真信号源施工后 emit）。
    if args.strategy != "":
        try:
            from zephyr.shared.event_bus import bus

            bus.emit("ex_core.rebalance.requested", {"reason": "session_start", "strategy": args.strategy})
        except Exception:  # noqa: BLE001
            _logger.warning("初始调仓事件发布失败（总线不可用），跳过", exc_info=True)

    # ── 有界保活循环（PERM-TRIGGER 合规：while now<收盘时点，非 while True）──
    print(f"[INFO] 会话已启动，保活至 {close_ts.isoformat()}（Ctrl+C 优雅停止，stop 自动撤未成交单）")
    if now_fn() >= close_ts:
        print("[WARN] 当前已过保活截止时点——启动即刻收尾停止")
    interrupted = False
    try:
        while now_fn() < close_ts:
            sleeper(args.poll)
    except KeyboardInterrupt:
        interrupted = True
        print("[INFO] KeyboardInterrupt——优雅停止（stop 自动撤未成交单）")
    finally:
        try:
            session.stop()
        except Exception:  # noqa: BLE001 — 停止异常已落日志，不改变收场语义
            _logger.exception("session.stop() 异常（已吞没）")
    print(f"[INFO] 会话已停止（{'人工中断' if interrupted else '收盘自动停止'}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
