# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] scripts.construction.qmt_bridge_regression_smoke
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.adapters.qmt_file_bridge_integration; zephyr.ex_core.order_manager; zephyr.ex_core.execution_report_producer; zephyr.data.ch_reader; zephyr.shared.utils.time_utils
# [CONSUMERS] 人工/CI 回归调用（全流通战役 L2 断点 E4 回归冒烟）
# [STARTUP] manual
# [MATURITY] draft
# [INVARIANTS] 模拟盘 ONLY(env=real 硬拒, 账户 8886156677 双重断言); ack 检测按通道分流(HTTP→柜台 sysid, 文件→ack 行); 已撤单不进 Order 导出=预期语义非失败; execution_report 断点 E4 回归钉(T6b 必须 +1 行)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 退出码 0=全 PASS; 1=有 FAIL; 2=参数/环境非法(如实盘路径或桥不可达)
# [TESTS] tests/ex_core/test_execution_report_producer.py（单元面）; 本脚本=链路面回归冒烟
# [A_module] module_id=MOD-L06-001-QMTFB | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 一次性回归冒烟 CLI（人工/验收批触发，非常驻系统；由 sim 战役验收批与演练清单调用）
# noqa: m10-time-trigger  M10豁免: ack/终态等待为单次有界轮询（20-30s 上界，非周期调度器）
"""QMT 文件桥回归冒烟（参数化，全流通战役 L2 / 断点 E4 回归钉）。

来历：2026-09-18 E2E 段二（docs/_working/clean_exam_e2e/env3_e2e_bridge/
seg2_execution_log.md）跑通 100 股模拟单全生命周期，但暴露两个**检测法缺陷**
（非链路故障），本脚本把修正后的检测法固化为可重复回归：

  缺陷① T2 的 ack 检测对 HTTP 快路径**结构性失明**——本单走 HTTP POST 直投沙箱
     EXEC（18901），orders_sim.csv 从未落行、ack_sim.csv 也不新增，只看 ack 文件
     必然 10s 超时误判 FAIL。修正=**按通道分流**：HTTP 路径查柜台 sysid 回填
     （broker_order_id），文件路径才查 ack 行。
  缺陷② T6a 把"Order.csv 不含本单"判为 FAIL——但 QMT 官方导出**不含已撤单**，
     与终态 CANCELLED 自洽。修正=接受该语义，改以 orders_sim.csv 指令行
     （order + cancel 双行）为柜台镜像铁证。

新增 T6b 断点 E4 回归钉：终态后 `c1_market.execution_report` 必须为本单落
**恰好一行**聚合（order_id 命中、actual_quantity 与成交量一致）。接线前恒 0 行。

安全边界（宪法 §12 场景事实 + R3 E2E 安全裁定）：
  - **模拟盘 ONLY**：`--env real` 直接 exit 2；实盘账户 8887871993 全程不触碰。
  - **账户双重断言**：broker ENV_CONFIG["sim"]["account"] 与柜台 Account.csv
    两处都必须等于 8886156677，任一不符立即中止。
  - 默认委托价 = 昨收×0.90 跌停价（必不成交 + 价格笼子豁免），成交面零扰动。

用法::

    python scripts/construction/qmt_bridge_regression_smoke.py            # 全默认
    python scripts/construction/qmt_bridge_regression_smoke.py --symbol 510300.SH \
        --qty 100 --no-cancel --json-out .runtime/tmp/smoke.json
"""

from __future__ import annotations

import argparse
import json
import logging
import socket
import sys
import threading
import time
from decimal import Decimal
from pathlib import Path
from typing import Final

from zephyr.data import ch_reader
from zephyr.ex_core.adapters.qmt_file_bridge_integration import QmtFileBridgeAssembly
from zephyr.ex_core.execution_report_producer import EXECUTION_REPORT_TABLE
from zephyr.ex_core.order_manager import OrderManager
from zephyr.governance.adapters.risk_validation_bridge import RiskValidationBridge
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.shared.contracts.order import OrderSide, OrderType
from zephyr.shared.utils.time_utils import now_utc

_WAIT_EVT = threading.Event()  # 有界可中断等待器（单次冒烟的 ack/终态确认，非调度器）

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
_log = logging.getLogger("qmt_bridge_regression_smoke")


class _CountingRiskBridge(RiskValidationBridge):
    """pre-trade 校验触发计数器（裁定 #338⑤ 接线验收：sim 单全链断言须含
    pre-trade 校验触发证据——本冒烟以 calls≥1 为 TR 步判据，st-sim-launch-20260923）。
    """

    def __init__(self, risk_validator) -> None:
        super().__init__(risk_validator)
        self.calls = 0

    def validate_order(self, *args, **kwargs):  # noqa: ANN002, ANN003 — 透传端口签名
        self.calls += 1
        return super().validate_order(*args, **kwargs)


#: 模拟账户（宪法 §12 场景事实）——双重断言用，实盘 8887871993 禁触
SIM_ACCOUNT: Final[str] = "8886156677"
REAL_ACCOUNT: Final[str] = "8887871993"
HTTP_BRIDGE_PORT: Final[int] = 18901

# NO-BARE-SQL：SQL 一律模块级常量
SQL_REPORT_COUNT: Final[str] = (
    "SELECT count() FROM " + EXECUTION_REPORT_TABLE + " FINAL WHERE order_id = '{order_id}'"  # noqa: bare-sql  首提存量行：NO-BARE-SQL 集中化常量形态（st-sim-launch-20260923 收编遗留）
)
SQL_REPORT_ROW: Final[str] = (
    "SELECT order_id, symbol, direction, intended_quantity, actual_quantity, "
    "intended_price, vwap_price, commission, broker_id, algo_type, idempotency_key, "
    "execution_start, execution_end FROM " + EXECUTION_REPORT_TABLE + " FINAL "
    "WHERE order_id = '{order_id}'"
)


def _fail_fast(message: str) -> None:
    """安全/环境前置不满足 → 立即 exit 2（禁继续下单）。"""
    _log.error("前置中止: %s", message)
    raise SystemExit(2)


def _assert_sim_env(broker) -> None:
    """账户双重断言①：broker 配置面必须是模拟账户。"""
    cfg_account = broker.ENV_CONFIG["sim"]["account"]
    if cfg_account != SIM_ACCOUNT:
        _fail_fast(f"broker sim 账户配置={cfg_account}，期望 {SIM_ACCOUNT}")
    if REAL_ACCOUNT in (broker.ENV_CONFIG["sim"].get("bridge_dir", ""),):
        _fail_fast("sim 桥目录含实盘账户串")
    _log.info("账户断言① PASS: broker.env=sim account=%s", cfg_account)


def _assert_sim_counter(broker) -> None:
    """账户双重断言②：柜台 Account.csv 资金面可读且非实盘实例。"""
    if broker._env != "sim":
        _fail_fast(f"broker 实例 env={broker._env}，本冒烟禁实盘")
    # 镜像预热轮询（st-commitchain-20260922 竞态修复）：CounterStateMirror 首轮同步
    # 未完成时 get_account() 为空——connect 后立即读必撞；轮询至多 12s 等镜像就绪。
    account: dict = {}
    for _ in range(6):
        account = broker.get_counter_account()
        if account:
            break
        _WAIT_EVT.wait(2)
    if not account:
        _fail_fast("柜台 Account.csv 不可读（QMT 模拟端未导出？）")
    _log.info(
        "账户断言② PASS: env=%s available=%s total=%s", broker._env, account.get("available"), account.get("total")
    )


def _detect_channel(port: int = HTTP_BRIDGE_PORT, timeout: float = 2.0) -> str:
    """通道探测：HTTP 快路径可达=http，否则=file（T2 检测分流依据）。"""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=timeout):
            return "http"
    except OSError:
        return "file"


def _wait_sysid(broker, order_id: str, timeout: float) -> str:
    """HTTP 通道 ack 判据：柜台 sysid 回填（broker_order_id 非空）。"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        order = broker.query_order(order_id)
        # 判据必须是柜台回填的真实 sysid：经 OrderManager 提交后 broker_order_id
        # 会先被预填为本地 order_id，相等=尚未回填（不得作为柜台 ack 证据）
        if order is not None and order.broker_order_id and order.broker_order_id != order_id:
            return order.broker_order_id
        _WAIT_EVT.wait(1.0)
    return ""


def _wait_ack_line(ack_file: Path, key: str, timeout: float) -> str:
    """文件通道 ack 判据：ack_sim.csv 出现本单 key 的行。"""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if ack_file.exists():
            for line in ack_file.read_text(encoding="ascii", errors="replace").splitlines():
                if line.startswith(key + ","):
                    return line.strip()
        _WAIT_EVT.wait(1.0)
    return ""


def _wait_terminal(broker, order_id: str, timeout: float) -> str:
    """轮询至终态（FILLED/CANCELLED/REJECTED），返回状态名或空串。"""
    terminal = {"FILLED", "CANCELLED", "REJECTED"}
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        order = broker.query_order(order_id)
        status = order.status.value if order is not None else ""
        if status in terminal:
            return status
        _WAIT_EVT.wait(1.0)
    return ""


def _instruction_lines(orders_file: Path, key: str) -> list[str]:
    """orders_sim.csv 中本单指令行（order/cancel 双行=柜台镜像铁证，T6a 修正判据）。"""
    if not orders_file.exists():
        return []
    return [
        line.strip()
        for line in orders_file.read_text(encoding="ascii", errors="replace").splitlines()
        if line.strip().startswith(key + ",") or line.strip().startswith(f"C{key},")
    ]


def _report_rows(order_id: str) -> list[str]:
    """execution_report 本单聚合行（ReplacingMergeTree 必带 FINAL）。"""
    raw = ch_reader.query(SQL_REPORT_ROW.format(order_id=order_id))
    return [line for line in raw.splitlines() if line.strip()]


def _record(results: list[dict], step: str, ok: bool, evidence: str) -> None:
    results.append({"step": step, "result": "PASS" if ok else "FAIL", "evidence": evidence})
    _log.info("[%s] %s — %s", "PASS" if ok else "FAIL", step, evidence)


def _verify_terminal(results: list[dict], om: OrderManager, broker, order_id: str, args: argparse.Namespace) -> str:
    """T4/T5 终态验证（撤单/挂单分流），返回终态串。"""
    if args.cancel:
        cancelled = om.cancel_order(order_id)
        status = _wait_terminal(broker, order_id, args.terminal_timeout)
        _record(results, "T5 撤单终态", status == "CANCELLED", f"cancel_order={cancelled} status={status}")
        return status
    status = _wait_terminal(broker, order_id, args.terminal_timeout)
    _record(results, "T4 状态可辨", bool(status), f"status={status or '未达终态(未撤单, 挂单中=预期)'}")
    return status


def _run_smoke(args: argparse.Namespace) -> int:
    """执行 T1-T6b 全链，返回退出码。"""
    results: list[dict] = []
    if args.env != "sim":
        _fail_fast("本冒烟模拟盘 ONLY，--env real 禁用（实盘启用=Owner 门位）")

    om = OrderManager()
    # R-H5E-1 显式注入（裁定 #338⑤）：冒烟下的是真 sim 单，进桥前必须过
    # pre-trade 前置校验闸；内存态校验器（冒烟进程生命周期内有效）。
    counting_bridge = _CountingRiskBridge(DefaultRiskValidator(state_store=None))
    assembly = QmtFileBridgeAssembly(
        om,
        enable_real=False,
        enable_sim=True,
        sync_interval=args.sync_interval,
        risk_validator=counting_bridge,
    )
    assembly.assemble()
    connected = assembly.connect_all()
    broker = assembly.get_broker("qmt_sim")
    if not connected.get("qmt_sim") or broker is None:
        _fail_fast(f"sim broker 连接失败: {connected}")

    _assert_sim_env(broker)
    _assert_sim_counter(broker)
    channel = args.ack_channel if args.ack_channel != "auto" else _detect_channel()
    _record(results, "T1 前置/双账户断言/通道探测", True, f"channel={channel} cash={broker.get_available_cash()}")

    baseline = int(ch_reader.query(SQL_REPORT_COUNT.format(order_id="__baseline__")).strip() or "0")
    _record(results, "T1b execution_report 基线", True, f"baseline_rows(order_id=__baseline__)={baseline}")

    idem_batch = f"smoke-{int(now_utc().timestamp())}"
    order = _submit(om, broker, args, idem_batch)
    order_id = order.order_id if order is not None else ""
    idem = order.idempotency_key if order is not None else ""
    _record(results, "T2 提交", bool(order_id), f"order_id={order_id} idem={idem} batch={idem_batch}")
    if not order_id:
        assembly.disconnect_all()
        return _finish(results, args, 1)

    ack_ok, ack_evidence = _check_ack(broker, channel, order_id, idem, args.ack_timeout)
    _record(results, f"T3 ack 检测（通道={channel}）", ack_ok, ack_evidence)

    _record(
        results,
        "TR pre-trade 校验触发证据（R-H5E-1 裁定 #338⑤ 接线验收）",
        counting_bridge.calls >= 1,
        f"validate_order calls={counting_bridge.calls} (期望>=1：sim 单进桥前校验已触发)",
    )

    _verify_terminal(results, om, broker, order_id, args)

    lines = _instruction_lines(broker._orders_file, idem)
    expect_lines = 2 if args.cancel else 1
    _record(
        results,
        "T6a 柜台镜像（指令行口径，已撤单不进 Order 导出=预期语义）",
        len(lines) >= expect_lines,
        f"orders_sim.csv 命中 {len(lines)} 行(期望>={expect_lines}): {lines}",
    )

    rows = _report_rows(order_id)
    expected_actual = "0" if args.cancel else None
    ok = len(rows) == 1
    if ok and expected_actual is not None:
        ok = rows[0].split("\t")[4] == expected_actual
    _record(
        results,
        "T6b 断点 E4 回归钉（execution_report 本单聚合行）",
        ok,
        f"rows={len(rows)} (期望 1) detail={rows}",
    )

    assembly.disconnect_all()
    return _finish(results, args, 0 if all(r["result"] == "PASS" for r in results) else 1)


def _submit(om: OrderManager, broker, args: argparse.Namespace, batch_id: str):
    """建单 + 提交（跌停价=必不成交），返回 Order（失败 None）。

    幂等键由 OrderManager 确定性派生（strategy|symbol|trade_date|signal_batch|side），
    故每次回归用唯一 signal_batch_id 开批，避免与历史批次撞键。
    """
    om.begin_signal_batch(batch_id)
    order = om.create_order(
        symbol=args.symbol,
        strategy_id=args.strategy_id,
        side=OrderSide.BUY if args.side == "buy" else OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal(str(args.qty)),
        limit_price=Decimal(str(args.price)),
        broker_id="qmt_sim",
    )
    try:
        om.submit_order(order.order_id, broker_id="qmt_sim")
    except Exception as exc:  # noqa: BLE001 — 冒烟需把提交异常转成 FAIL 而非崩栈
        _log.error("提交失败: %r", exc)
        return None
    return order


def _check_ack(broker, channel: str, order_id: str, idem: str, timeout: float) -> tuple[bool, str]:
    """T3 ack 检测按通道分流（缺陷①修正）。返回 (是否观测到 ack, 证据文本)。"""
    if channel == "http":
        sysid = _wait_sysid(broker, order_id, timeout)
        if sysid:
            return True, f"HTTP 通道判据=柜台 sysid 回填: broker_order_id={sysid}"
        return False, f"HTTP 通道 {timeout}s 未见柜台 sysid 回填"
    ack_line = _wait_ack_line(broker._ack_file, idem, timeout)
    if ack_line:
        return True, f"文件通道判据=ack 行: {ack_line}"
    return False, f"文件通道 {timeout}s 未见 ack 行"


def _finish(results: list[dict], args: argparse.Namespace, code: int) -> int:
    """汇总输出（可选 JSON 落盘）。"""
    passed = sum(1 for r in results if r["result"] == "PASS")
    summary = {
        "ts": now_utc().isoformat(),
        "env": args.env,
        "account": SIM_ACCOUNT,
        "channel": args.ack_channel,
        "passed": passed,
        "total": len(results),
        "exit_code": code,
        "steps": results,
    }
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        _log.info("结果 JSON 落盘: %s", out)
    _log.info("=" * 50)
    _log.info("回归冒烟汇总: %d/%d PASS, exit=%d", passed, len(results), code)
    return code


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="QMT 文件桥回归冒烟（模拟盘 ONLY）")
    p.add_argument("--env", default="sim", choices=["sim"], help="环境（仅 sim；实盘=Owner 门位）")
    p.add_argument("--symbol", default="510300.SH", help="标的（默认 510300.SH）")
    p.add_argument("--side", default="buy", choices=["buy", "sell"])
    p.add_argument("--qty", type=int, default=100, help="委托数量（最小整手 100）")
    p.add_argument("--price", type=float, default=4.07, help="委托价（默认跌停价=必不成交）")
    p.add_argument("--strategy-id", default="smoke_bridge_regression")
    p.add_argument("--cancel", dest="cancel", action="store_true", default=True, help="撤单收敛终态（默认）")
    p.add_argument("--no-cancel", dest="cancel", action="store_false", help="不撤单（观察挂单态）")
    p.add_argument("--ack-channel", default="auto", choices=["auto", "http", "file"], help="T3 ack 检测通道")
    p.add_argument("--ack-timeout", type=float, default=20.0)
    p.add_argument("--terminal-timeout", type=float, default=30.0)
    p.add_argument("--sync-interval", type=float, default=1.0)
    p.add_argument("--json-out", default="", help="结果 JSON 落盘路径")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return _run_smoke(args)


if __name__ == "__main__":
    sys.exit(main())
