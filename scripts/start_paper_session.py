# [BLUEPRINT] MOD-SCRIPT-start_paper_session | scripts/start_paper_session.py | §
# [MODULE] scripts.start_paper_session
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib；zephyr.ex_core.trading_session（TradingSession/TradingSessionConfig 真源）；zephyr.ex_core.live_strategy_adapter（--service 常驻服务模式：LiveStrategyAdapter/StrategySlot）；zephyr.ex_core.adapters.miniqmt_broker（延迟 import）；zephyr.ex_core.order_manager；zephyr.ex_core.signal_providers；zephyr.governance.adapters.risk_validation_bridge；zephyr.risk.implementations.default_risk_validator；zephyr.governance.strategies.strategy_base；zephyr.pf_core.topn_momentum_strategy（--strategy 可选）；zephyr.shared.infra.process_pool（run_subprocess_hidden SSoT）
# [CONSUMERS] 57 号文 §2 盘中模拟盘——交易日 09:25 前人工拉起；--service=LiveStrategyAdapter 常驻服务模式（GAP-2 残余① CLI 接线已落）；挂计划任务/调度=Owner 窗口
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 仅连 QMT 模拟账户（config/.env.qmt QMT_SIM_*，实盘 QMT_REAL_* 永不触碰）；默认纯会话保活不自动 rebalance（--strategy 缺省=安全默认）；--dry-run 只连不打任何单；有界保活循环 15:05 自动 stop；KeyboardInterrupt 优雅 stop（stop 自动撤未成交单语义保留）；--service 模式 assemble_session 包 StrategySlot 交 LiveStrategyAdapter 监督（异常隔离+退避重启熔断+biz 心跳 tmp/live_strategy_biz.heartbeat），adapter.run(close_at) 有界收场
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
   策略/信号/价格提供器）→ session.start()（连接+成交回调注册）。
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
- ``--interval N``：--strategy 模式自动调仓间隔秒（默认 300）。
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
import logging
import sys
import time
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

from zephyr.ex_core.live_strategy_adapter import LiveStrategyAdapter, StrategySlot  # noqa: E402
from zephyr.ex_core.order_manager import OrderManager  # noqa: E402
from zephyr.ex_core.signal_providers import make_mock_price_provider, make_mock_signal_provider  # noqa: E402
from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig  # noqa: E402
from zephyr.governance.adapters.risk_validation_bridge import RiskValidationBridge  # noqa: E402
from zephyr.governance.strategies.strategy_base import StrategyBase  # noqa: E402
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator  # noqa: E402
from zephyr.shared.contracts.risk_limits import RiskLimits  # noqa: E402
from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: E402

_logger = logging.getLogger(__name__)

#: QMT 模拟盘配置文件（只读 QMT_SIM_* 两键；QMT_REAL_* 实盘键本脚本永不触碰）
_ENV_QMT_PATH = _REPO_ROOT / "config" / ".env.qmt"
#: A 股交易时刻口径=北京时区（与 trading_session._SHANGHAI_TZ 同口径）
_SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
#: OrderManager 内注册 broker 的标识（与 TradingSessionConfig.broker_id 对齐）
_BROKER_ID = "miniqmt"
#: --strategy 可选策略注册表键（MVP 仅 topn-momentum，与冒烟脚本同件）
_STRATEGY_TOPN_MOMENTUM = "topn-momentum"


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
    parser.add_argument("--interval", type=int, default=300, help="--strategy 模式自动调仓间隔秒（默认 300）")
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


def assemble_session(args: argparse.Namespace, broker: object) -> TradingSession:
    """装配 TradingSession（57 号文 §2 过渡形态编排）。

    默认（--strategy 空）：_KeepAliveStrategy + 空 universe + interval=0
    → start() 仅连接+注册成交回调，永不自动 rebalance（纯保活安全默认）。
    --strategy topn-momentum：mock 信号 + --universe + interval 自动调仓
    （彩排口径——LiveStrategyAdapter 真信号源未施工，启动时大字告警）。
    """
    order_manager = OrderManager()
    order_manager.register_broker(_BROKER_ID, broker)
    risk_validator = RiskValidationBridge(DefaultRiskValidator())
    now = datetime.now(_SHANGHAI_TZ)

    if args.strategy == "":
        strategy: StrategyBase = _KeepAliveStrategy()
        universe: list[str] = []
        signal_provider = make_mock_signal_provider({})
        price_provider = make_mock_price_provider({})
        interval = 0  # 纯保活：永不自动调仓（安全默认）
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
        interval = args.interval
        strategy_id = args.strategy
        constraints = {"top_n": len(universe), "max_single": args.max_single}
    else:
        raise ValueError(f"未知策略: {args.strategy!r}（可选: {_STRATEGY_TOPN_MOMENTUM}）")

    config = TradingSessionConfig(
        universe=universe,
        broker_id=_BROKER_ID,
        strategy_id=strategy_id,
        rebalance_interval_seconds=interval,
        strategy_constraints=constraints,
        risk_limits=RiskLimits(
            as_of_date=now,
            idempotency_key=f"paper-{now.isoformat()}",
            max_single_position=max(args.max_single, 0.01),
        ),
    )
    return TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=risk_validator,
        signal_provider=signal_provider,
        price_provider=price_provider,
        order_manager=order_manager,
        config=config,
    )


def assemble_adapter(
    args: argparse.Namespace,
    broker: object,
    *,
    session_factory: Callable[[argparse.Namespace, object], object] | None = None,
    now_fn: Callable[[], datetime] | None = None,
    sleeper: Callable[[float], None] = time.sleep,
    **adapter_kwargs: Any,
) -> LiveStrategyAdapter:
    """常驻服务装配（57 号文 GAP-2 残余① CLI 接线）：assemble_session 包 StrategySlot 交 LiveStrategyAdapter。

    slot 工厂每次调用重造新会话实例（崩溃重启=工厂重造，不携残留订单/计数态——
    StrategySlot 契约）；adapter 监督语义=异常隔离+退避重启熔断+biz 心跳
    tmp/live_strategy_biz.heartbeat（纳入 deadman_switch 监控清单=Owner 窗口，
    tracker #273）。仅承载模拟盘会话（assemble_session 口径连 QMT 模拟账户）。

    Args:
        args: CLI 参数（strategy/universe/interval 等透传 session 装配）。
        broker: 已连接的模拟盘 broker（main 已 connect 探活）。
        session_factory: 会话装配器（测试注入 mock；None=assemble_session）。
        now_fn: 当前时间（测试注入假钟；None=adapter 默认北京时区现在）。
        sleeper: 监督轮询睡眠（测试注入假钟；默认 time.sleep）。
        adapter_kwargs: 透传 LiveStrategyAdapter（heartbeat_path 等测试注入件）。
    """
    factory = session_factory or assemble_session
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
