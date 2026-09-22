# [BLUEPRINT] MOD-SCRIPT-run_post_settlement | scripts/run_post_settlement.py | §
# [MODULE] scripts.run_post_settlement
# [DOMAIN] D_TRADING
# [DEPENDENCIES] stdlib；zephyr.trading.post_settlement_pipeline（流水线真源）；zephyr.trading.settlement_reconciliation（SettlementReconciler）；zephyr.trading.broker_settlement_adapter（fetch_broker_settlement_records 券商侧适配）；zephyr.ex_core.fill_handler（query_fills_by_date 读取口径）；zephyr.risk.core.daily_auditor（DailyAuditor.audit + run_var_backtest_from_store）；zephyr.risk.core.backtest_store（VarBacktestStore 门面，VaR 定级归档）；zephyr.shared.state_store（JsonStateStore 风控状态根）；zephyr.data.trading_calendar（is_trading_day 交易日回推）；zephyr.ex_core.adapters.miniqmt_broker（QMT 模拟盘连接，延迟 import 可降级）
# [CONSUMERS] 57 号文 §3 收盘结算管线触发入口（人工 CLI 保留；挂调度已获 Owner 2026-09-15 全自动指令批准——计划任务 ZephyrAlpha_PostSettlement 工作日 15:30 经 scripts/register_post_settlement_task.ps1 注册，幂等只读不变）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读对账+审计不写业务 DB（reconciliation_differences 落库由 recon_runner 负责，本脚本不重复写）；VaR 回测定级为本脚本新增状态写副作用且只写既有风控状态根(data/runtime/state)的 var_backtest_report_* 归档——状态根/盘前基线缺失即整步跳过且绝不 mkdir 造目录，本步异常与结论永不改退出码，定级动作不在本脚本执行（§3.10 唯一执行者=编排层 apply_var_backtest_action）；QMT 不在线降级为仅系统侧+显式标注（不伪造"券商侧为空"的假比对）；对账不一致必打印 C 类异常清单+exit 3（不静默）；步骤异常 exit 1；幂等（同 trade_date 重跑无副作用）
# [MODIFY-GUARD] 57_daily_cycle_sop.md §3/§7 GAP-3；54_reconciliation_attribution.md §2.4/§3.3；#ARCH-DAILY-CYCLE-GAP23-001
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=OK 或 SKIPPED；exit 3=DRIFT（结算对账不一致）；exit 1=ERROR（步骤异常/参数非法/交易日解析失败）
# [TESTS] tests/scripts/test_run_post_settlement.py
# [A_module] module_id=MOD-SCRIPT-run_post_settlement | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 本文件是 57 号文 §3 盘后结算 CLI（无常驻进程无自轮询循环；工作日 15:30 计划任务经外部 Task Scheduler 单发触发本幂等 CLI，2026-09-15 Owner 全自动指令批准），与 commit_queue.py 同类
# @高风险动作: 只读对账+审计，不写业务 DB（写副作用两处=① FillHandler 初始化时 mkdir data/fills 目录兜底；② VaR 回测定级归档写既有 data/runtime/state 的 var_backtest_report_*（根/盘前基线不存在则整步跳过，不 mkdir 不建根）；券商侧仅 query 查询不下单，定级动作不在本脚本执行）
"""run_post_settlement.py — 盘后结算对账+日终审计 CLI（57 号文 GAP-3，Owner 2026-08-21 批准施工）

真源
----
- 57 号文 §3（收盘结算 15:30 后手动触发形态）+ §7 GAP-3（post_settlement_pipeline
  无 CLI/注入脚本——本脚本即该缺口的施工件，**挂调度不在本件**）。
- 54 号文 §2.4 缺口 #2 / §3.3（盘后 15:30 硬时点，A 股 T+1 结算）。
- 56 号文 §3（对账归因三分类：A 滑点/B 部分成交/C 拒单缺失）——C 类=MISSING_IN_*

功能
----
``python scripts/run_post_settlement.py [trade_date]``（YYYY-MM-DD；缺省=最近交易日，
用 zephyr.data.trading_calendar.is_trading_day 从今天回推，含今天——盘后语义，
上午跑请显式传前一交易日）：

1. 系统侧：FillHandler(fills_dir=data/fills).query_fills_by_date(trade_date) 回放
   当日 Fill JSONL（56 号文 G3 落盘口径，进程退出不丢当日 Fill）。
2. 券商侧：config/.env.qmt 模拟账户构造 MiniQmtBroker → connect →
   broker_settlement_adapter.fetch_broker_settlement_records（业务配对键口径真源）。
   **QMT 不在线/xtquant 不可用 → 降级：reconcile_fn=None（流水线标 SKIPPED）+
   显式打印降级标注与系统侧 Fill 笔数**——绝不拿空券商侧硬对（否则系统侧全部
   成交会被误判 MISSING_IN_BROKER 假 DRIFT）。
3. 审计：DailyAuditor().audit 包装（MOD-RK-20 五件套）。持仓/净值/限额真源
   未接线（57 号文 GAP 族后续批），当前以空快照最小输入跑通链路并显式标注。
4. VaR 回测定级归档：``DailyAuditor.run_var_backtest_from_store`` 以风控状态根
   （``data/runtime/state``，编排层同款）的盘前基线归档为预测腿、``var_pnl_dual_*``
   clean P&L 为实现腿配对定级，归档 ``var_backtest_report_YYYY-MM-DD`` 供**下一会话
   编排层唯一执行者** ``apply_var_backtest_action`` 落地（本脚本不改任何风控态）。
   状态根/盘前基线不存在 → 整步跳过并标注（不 mkdir、不伪造定级）；本步异常/结论
   **永不改退出码**。
5. 打印 PostSettlementRunResult 全字段 + C 类异常清单（若有）。

exit code 矩阵（57 号文 §3 验收口径）
-------------------------------------
- 0 = reconcile/audit 全 OK，或任一步 SKIPPED（含 QMT 降级）
- 3 = DRIFT（结算对账不一致——C 类清单已打印，当日 tracker 登记闭环，56 号文 C10）
- 1 = ERROR（对账/审计步骤异常，或 trade_date 参数非法）

生产调用示例（写进 tracker 用）::

    python scripts/run_post_settlement.py 2026-08-21
    python scripts/run_post_settlement.py            # 缺省=最近交易日（盘后语义）
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
# 脚本直跑（python scripts/xxx.py）时保证 src 布局可导入（冒烟脚本同口径）
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.data.trading_calendar import is_trading_day  # noqa: E402
from zephyr.ex_core.fill_handler import FillHandler  # noqa: E402
from zephyr.risk.core.backtest_store import VarBacktestStore  # noqa: E402
from zephyr.risk.core.daily_auditor import AuditRequest, DailyAuditor  # noqa: E402
from zephyr.shared.state_store import JsonStateStore  # noqa: E402
from zephyr.trading.broker_settlement_adapter import fetch_broker_settlement_records  # noqa: E402
from zephyr.trading.post_settlement_pipeline import (  # noqa: E402
    PostSettlementRunResult,
    run_post_settlement_pipeline,
)
from zephyr.trading.settlement_reconciliation import (  # noqa: E402
    DriftType,
    ReconciliationResult,
    SettlementReconciler,
)

_logger = logging.getLogger(__name__)

#: 默认系统侧 Fill JSONL 落盘目录（56 号文 G3 口径：{fills_dir}/YYYYMMDD.jsonl）
_DEFAULT_FILLS_DIR = _REPO_ROOT / "data" / "fills"
#: QMT 模拟盘配置文件（QMT_SIM_PATH / QMT_SIM_ACCOUNT；实盘 QMT_REAL_* 本脚本永不触碰）
_ENV_QMT_PATH = _REPO_ROOT / "config" / ".env.qmt"
#: 风控层状态根（36号 §3.18 持久化门面根目录）——盘后 VaR 回测定级的**跨进程交付面**：
#: 编排层（start_paper_session 装配）读同一根，本脚本写 var_backtest_report_* 归档。
#: 字面真源在 scripts/start_paper_session.py `_RISK_STATE_DIR`（两脚本各持一份是
#: SSOT 债，收敛点待主会话裁决——本件不擅自改禁改清单内文件）
_RISK_STATE_DIR = _REPO_ROOT / "data" / "runtime" / "state"
#: 交易日回推上限（防御性有界——exchange_calendars 异常 + 全周末也不可能超 31 天）
_MAX_LOOKBACK_DAYS = 31
#: 模拟盘组合标识（审计报告 portfolio_id 标签；与券商侧 portfolio 语义无关）
_PAPER_PORTFOLIO_ID = "miniqmt-sim"
#: C 类异常（56 号文 §3：拒单/缺失）——对账 drifts 中属 C 类的差异类型
_C_CLASS_DRIFT_TYPES = frozenset({DriftType.MISSING_IN_SYSTEM, DriftType.MISSING_IN_BROKER})
#: 严格 YYYY-MM-DD 格式（四-二-二位，连字符分隔）
_TRADE_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


# ── 注入依赖容器（生产装配 vs 测试 mock 同一入口）─────────────────────────────


@dataclass
class PipelineDeps:
    """run_post_settlement_pipeline 三注入件 + 输出标注。

    Attributes:
        reconcile_fn: 结算对账可调用；None=该步 SKIPPED（QMT 降级语义）。
        audit_fn: 日终审计可调用；None=SKIPPED。
        alert_sink: 告警出口 callable(trade_date, message)。
        notes: 运行标注（降级原因/接线缺口等），main 末尾原样打印。
        reconcile_results: 内部 holder——reconcile 闭包把每次结果追加进来，
            供 main 打印 C 类异常清单（流水线结果只带状态不带 drifts 明细）。
        system_fills_reader: 降级路径专用——系统侧 Fill 读取 callable
            （trade_date → list[Fill]），供 main 打印"仅系统侧"笔数标注。
        var_backtest_fn: 盘后 VaR 回测定级装配 callable（trade_date →
            VarBacktestReport|None，36号 §3.9/§3.10/§3.18 产端）；
            None=状态根不可用（该步不跑，永不影响退出码）。
    """

    reconcile_fn: Callable[[str], object] | None
    audit_fn: Callable[[str], object] | None
    alert_sink: Callable[[str, str], None] | None
    notes: list[str] = field(default_factory=list)
    reconcile_results: list[ReconciliationResult] = field(default_factory=list)
    system_fills_reader: Callable[[str], list] | None = None
    var_backtest_fn: Callable[[str], object] | None = None


# ── CLI 参数与交易日解析 ─────────────────────────────────────────────────────


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """CLI 参数解析（trade_date 可选位置参数，YYYY-MM-DD）。"""
    parser = argparse.ArgumentParser(
        prog="run_post_settlement.py",
        description="盘后结算对账+日终审计 CLI（57 号文 GAP-3；只读不写业务 DB）",
    )
    parser.add_argument(
        "trade_date",
        nargs="?",
        default=None,
        help="结算日 YYYY-MM-DD；缺省=最近交易日（is_trading_day 从今天回推，含今天——盘后语义）",
    )
    parser.add_argument(
        "--if-trading-day",
        action="store_true",
        help="仅当日是交易日才执行，否则静默 exit 0（挂调度专用守卫：非交易日空转零打扰）",
    )
    return parser.parse_args(argv)


def resolve_trade_date(arg: str | None, *, today: date | None = None) -> str:
    """解析结算日：显式入参做严格 YYYY-MM-DD 校验；缺省回推最近交易日。

    Args:
        arg: CLI 位置参数（None=缺省）。
        today: 回推基准日（测试注入用；None=今天）。

    Returns:
        "YYYY-MM-DD" 结算日。

    Raises:
        ValueError: 入参格式非法 / 31 天回推窗口内无交易日（防御性兜底）。
    """
    if arg is not None:
        # 严格 YYYY-MM-DD：正则卡四位年/两位月日（strptime 对零填充宽容会放行
        # "2026-8-1"，date.fromisoformat 3.11+ 会放行紧凑 "20260821"，口径均不收）
        if not _TRADE_DATE_RE.fullmatch(arg):
            raise ValueError(f"trade_date 格式非法（期望 YYYY-MM-DD）: {arg!r}")
        try:
            datetime.strptime(arg, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"trade_date 不是合法日历日（YYYY-MM-DD）: {arg!r}") from exc
        return arg
    day = today or date.today()
    for _ in range(_MAX_LOOKBACK_DAYS):
        if is_trading_day(day):
            return day.isoformat()
        day -= timedelta(days=1)
    raise ValueError(f"最近 {_MAX_LOOKBACK_DAYS} 天内无交易日（回推基准={day}）——交易日历异常")


# ── 生产件装配（真实注入：系统侧 Fill / 券商侧结算单 / 审计包装）──────────────


def load_qmt_sim_config(env_path: Path = _ENV_QMT_PATH) -> tuple[str, str]:
    """从 config/.env.qmt 读模拟盘配置（冒烟脚本同口径；只读 QMT_SIM_* 两键）。

    Returns:
        (QMT_SIM_PATH, QMT_SIM_ACCOUNT)。

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


def _try_connect_sim_broker() -> tuple[object | None, str]:
    """探测性连接 QMT 模拟盘（永不抛异常——降级是正常路径非故障）。

    Returns:
        (broker, 标注)：连接成功返回已连接 broker；任何一步失败返回
        (None, 降级原因标注)。broker 类型为 MiniQmtBroker（鸭子类型满足
        broker_settlement_adapter.BrokerTradeSource 协议）。
    """
    try:
        qmt_path, qmt_account = load_qmt_sim_config()
    except Exception as exc:  # noqa: BLE001 — 配置缺失=降级路径，原因入标注
        return None, f"QMT 配置读取失败（{type(exc).__name__}: {exc}）"
    try:
        # 延迟 import：xtquant 仅券商在线路径需要，离线降级环境不拖垮本脚本
        from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker

        broker = MiniQmtBroker(
            path=qmt_path,
            session_id="post_settlement_probe",
            account_id=qmt_account,
        )
        if not broker.connect():
            return None, "MiniQmtBroker.connect() 返回 False（XtMiniQmt 终端未在线？）"
        return broker, f"QMT 模拟盘已连接（account={qmt_account}）"
    except Exception as exc:  # noqa: BLE001 — xtquant 缺失/终端离线/超时均为降级路径
        return None, f"QMT 连接异常（{type(exc).__name__}: {exc}）"


def _build_reconcile_fn(
    broker: object,
    deps: PipelineDeps,
    *,
    fills_dir: Path | None = None,
) -> Callable[[str], ReconciliationResult]:
    """构造结算对账闭包：系统侧 Fill + 券商侧结算单 → SettlementReconciler。

    系统侧读取口径复用 fill_handler.query_fills_by_date（56 号文 G3）；
    券商侧经 broker_settlement_adapter 业务配对键口径适配（56 号文 §2 G4）。
    结果追加进 deps.reconcile_results 供 C 类清单打印。
    fills_dir 缺省=data/fills（测试注入 tmp 目录隔离）。
    """
    handler = FillHandler(fills_dir=fills_dir or _DEFAULT_FILLS_DIR)
    reconciler = SettlementReconciler()

    def _reconcile(trade_date: str) -> ReconciliationResult:
        system_fills = handler.query_fills_by_date(trade_date)
        broker_records = fetch_broker_settlement_records(broker, trade_date)
        result = reconciler.reconcile(system_fills, broker_records, trade_date)
        deps.reconcile_results.append(result)
        return result

    return _reconcile


def _build_audit_fn() -> Callable[[str], object]:
    """DailyAuditor().audit 包装（MOD-RK-20 L971 五件套）。

    持仓/净值/限额真源未接线（57 号文 GAP 族后续批）——以空快照最小输入
    跑通 对账→归因→合规→清单→问题追溯 全链路；输入缺口由 main 显式标注，
    不伪装成完整审计。
    """
    auditor = DailyAuditor()

    def _audit(trade_date: str) -> object:
        request = AuditRequest(
            trading_date=date.fromisoformat(trade_date),
            portfolio_id=_PAPER_PORTFOLIO_ID,
            positions_prev=[],
            positions_now=[],
            fills=[],
            nav=0.0,
            consumptions=[],
        )
        return auditor.audit(request)

    return _audit


def _build_var_backtest_fn(
    auditor: DailyAuditor | None = None,
    *,
    state_dir: Path | None = None,
) -> Callable[[str], object] | None:
    """构造盘后 VaR 回测定级装配闭包（36号 §3.9 装配 + §3.10 定级 + §3.18 归档）。

    状态根门禁：`data/runtime/state`（编排层同款根）不存在，或尚无盘前基线
    归档 `var_premarket_baseline.json`（编排层未跑过=预测腿零来源）→ 返回
    None 让该步整体不跑。**本脚本绝不为此 mkdir 状态根**：一只往不存在的
    空归档里写数据的"产端"是假接线，且会把只读脚本变成写脚本。

    Args:
        auditor: DailyAuditor 实例（缺省新建，与 audit_fn 同型）
        state_dir: 状态根覆盖（测试注入 tmp_path 隔离）

    Returns:
        callable(trade_date) → VarBacktestReport|None；None=条件不具备，跳过
    """
    root = state_dir or _RISK_STATE_DIR
    if not root.is_dir() or not (root / "var_premarket_baseline.json").is_file():
        return None
    bt_auditor = auditor or DailyAuditor()
    store = VarBacktestStore(JsonStateStore(root))

    def _grade(trade_date: str) -> object:
        return bt_auditor.run_var_backtest_from_store(store, date.fromisoformat(trade_date))

    return _grade


def _run_sim_journal_step(trade_date: str) -> None:
    """模拟盘平台日刊收盘档（④ 排程语义修复 2026-09-22 st-sim-launch）。

    事件链早间档的日刊（daily_kline SUCCESS 唤醒）拿的是盘前快照，当日收盘后的
    真实钱包/事件数由本步在 15:30 收盘结算链末尾幂等覆盖（ReplacingMergeTree
    同键新版本）——日刊语义从"早间预览"补全为"收盘定稿"。子进程隔离（日刊内部
    自带三健康检+告警），失败只大声留痕，永不改盘后对账/审计的退出码矩阵。
    """
    try:
        from zephyr.shared.infra.process_pool import run_subprocess_hidden  # noqa: PLC0415

        proc = run_subprocess_hidden(
            [
                sys.executable,
                str(Path(__file__).resolve().parent / "backtest" / "sim_platform_journal.py"),
                "--date",
                trade_date,
            ],
            capture_output=True,
            text=True,
            timeout=600,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            _logger.error("模拟盘日刊收盘档失败 rc=%s: %s", proc.returncode, (proc.stderr or "")[-300:])
            deps_note = "模拟盘日刊：收盘档失败（详见日志）"
        else:
            deps_note = "模拟盘日刊：收盘档已写（幂等覆盖早间档）"
        print(f"[INFO] {deps_note}")
    except Exception:  # noqa: BLE001 — 本步永不改既有退出码矩阵（异常大声留痕）
        _logger.exception("模拟盘日刊收盘档异常（已吞没，不影响盘后对账/审计结论）")
        print("[INFO] 模拟盘日刊：收盘档异常（详见日志）")


def _run_var_backtest_step(deps: PipelineDeps, trade_date: str) -> None:
    """执行 VaR 定级装配并记结论标注（永不抛异常、永不改退出码）。

    定级动作不在本脚本执行——归档 `var_backtest_report_YYYY-MM-DD` 后由
    下一会话编排层唯一执行者 `apply_var_backtest_action` 落地（36号 §3.10
    单一执行者；在此直接改风控态=另立第二个头）。
    """
    if deps.var_backtest_fn is None:
        deps.notes.append(
            f"VaR 回测定级：跳过（状态根 {_RISK_STATE_DIR} 无盘前基线归档——"
            "编排层未在此根跑过，预测腿零来源，绝不拿空归档伪造定级）"
        )
        return
    try:
        report = deps.var_backtest_fn(trade_date)
    except Exception:  # noqa: BLE001 — 新增步骤永不改既有退出码矩阵（异常大声留痕）
        _logger.exception("VaR 回测定级装配异常（已吞没，不影响盘后对账/审计结论）")
        deps.notes.append("VaR 回测定级：异常（详见日志），本步未归档")
        return
    if report is None:
        deps.notes.append("VaR 回测定级：两腿零配对未定级未归档（clean P&L 双轨真源未接线，57号文 GAP 族后续批）")
        return
    deps.notes.append(
        f"VaR 回测定级已归档: action={getattr(report, 'action', '?')} "
        f"n_obs={getattr(report, 'n_obs', '?')} flags={getattr(report, 'flags', ())} "
        "→ 下一会话编排层 apply_var_backtest_action 单一执行者落地"
    )


def _stdout_alert_sink(trade_date: str, message: str) -> None:
    """告警出口：stdout 大字打印（57 号文 §6——异常当日 tracker 登记闭环，本脚本不静默）。"""
    print(f"[ALERT] {trade_date} {message}")


def build_production_deps() -> tuple[PipelineDeps, object | None]:
    """生产装配：探测 QMT → 有券商侧则全量对账，否则降级仅系统侧+标注。

    Returns:
        (deps, broker)：broker 非 None 时调用方负责用后 disconnect。
    """
    deps = PipelineDeps(
        reconcile_fn=None,
        audit_fn=_build_audit_fn(),
        alert_sink=_stdout_alert_sink,
        var_backtest_fn=_build_var_backtest_fn(),
    )
    broker, note = _try_connect_sim_broker()
    if broker is None:
        # 降级：仅系统侧+标注——reconcile_fn=None 使流水线该步 SKIPPED，
        # 系统侧 Fill 笔数仍由 system_fills_reader 读出打印（"仅系统侧"的如实口径）
        deps.notes.append(f"QMT 模拟盘不可用——降级为仅系统侧+标注（{note}）")
        deps.notes.append("券商侧结算单未参与比对：本日不构成有效对账（56 号文 R2：只登记不判定）")
        deps.notes.append(f"系统侧 Fill 读取目录: {_DEFAULT_FILLS_DIR}")
        deps.system_fills_reader = FillHandler(fills_dir=_DEFAULT_FILLS_DIR).query_fills_by_date
    else:
        deps.notes.append(note)
        deps.reconcile_fn = _build_reconcile_fn(broker, deps)
    deps.notes.append("日终审计输入=空快照最小输入（持仓/净值/限额真源未接线，57 号文 GAP 族后续批）")
    return deps, broker


# ── 输出与 exit code ─────────────────────────────────────────────────────────


def _exit_code_of(result: PostSettlementRunResult) -> int:
    """exit code 矩阵：任一步 ERROR→1；对账 DRIFT→3；OK/SKIPPED→0。"""
    if result.reconcile_status == "ERROR" or result.audit_status == "ERROR":
        return 1
    if result.reconcile_status == "DRIFT":
        return 3
    return 0


def _print_c_class_drifts(deps: PipelineDeps) -> None:
    """打印 C 类异常清单（56 号文 §3：MISSING_IN_SYSTEM/MISSING_IN_BROKER=拒单/缺失）。"""
    for result in deps.reconcile_results:
        c_drifts = [d for d in result.drifts if d.drift_type in _C_CLASS_DRIFT_TYPES]
        if not c_drifts:
            continue
        print(f"[C 类异常清单] 共 {len(c_drifts)} 笔（拒单/缺失，当日 tracker 登记闭环——56 号文 C10）:")
        for d in c_drifts:
            print(
                f"  - {d.drift_type.value}: trade_id={d.trade_id} symbol={d.symbol} "
                f"system={d.system_value} broker={d.broker_value}"
            )


def _print_result(result: PostSettlementRunResult, deps: PipelineDeps) -> None:
    """打印 PostSettlementRunResult 全字段 + 标注 + C 类清单。"""
    print("=== PostSettlementRunResult ===")
    print(f"trade_date:       {result.trade_date}")
    print(f"reconcile_status: {result.reconcile_status}")
    print(f"audit_status:     {result.audit_status}")
    print(f"errors:           {list(result.errors) if result.errors else '(无)'}")
    for note in deps.notes:
        print(f"[标注] {note}")
    _print_c_class_drifts(deps)


# ── 主入口 ───────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None, *, deps: PipelineDeps | None = None) -> int:
    """CLI 主入口。

    Args:
        argv: 命令行参数（None=sys.argv）。
        deps: 注入件（None=生产装配；测试注入 mock reconcile/audit 验证注入点
            与 exit 码矩阵，tmp 目录隔离系统侧 Fill）。

    Returns:
        exit code（0=OK/SKIPPED，3=DRIFT，1=ERROR）。
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    # 挂调度守卫（2026-08-22 Owner 批准挂 15:30 日调度）：非交易日静默退出，
    # 防止周末/节假日空跑重复结算最近交易日
    if getattr(args, "if_trading_day", False) and not is_trading_day(date.today()):
        print(f"[INFO] 今日 {date.today().isoformat()} 非交易日，跳过（--if-trading-day 守卫）")
        return 0
    try:
        trade_date = resolve_trade_date(args.trade_date)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1
    print(f"[INFO] 结算日: {trade_date}（57 号文 §3 盘后结算管线，手动触发未挂调度）")

    broker = None
    if deps is None:
        deps, broker = build_production_deps()
    # 降级路径：系统侧 Fill 笔数如实打印（"仅系统侧"的读数标注）
    if deps.system_fills_reader is not None:
        try:
            print(f"[INFO] 系统侧当日 Fill: {len(deps.system_fills_reader(trade_date))} 笔（券商侧未比对——降级标注）")
        except Exception:  # noqa: BLE001 — 读数失败不阻断主流水线
            _logger.exception("系统侧 Fill 读数失败（已吞没，仅影响标注行）")

    try:
        result = run_post_settlement_pipeline(
            trade_date,
            reconcile_fn=deps.reconcile_fn,
            audit_fn=deps.audit_fn,
            alert_sink=deps.alert_sink,
        )
    finally:
        if broker is not None:
            try:
                broker.disconnect()
            except Exception:  # noqa: BLE001 — 断开失败不影响本次结果
                _logger.exception("broker.disconnect() 异常（已吞没）")

    _run_var_backtest_step(deps, trade_date)
    _run_sim_journal_step(trade_date)
    _print_result(result, deps)
    code = _exit_code_of(result)
    print(f"[INFO] exit_code={code}（0=OK/SKIPPED, 3=DRIFT, 1=ERROR）")
    return code


if __name__ == "__main__":
    sys.exit(main())
