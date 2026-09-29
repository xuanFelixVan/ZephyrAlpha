# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] zephyr.ex_core.ghost_order_sentinel
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib: dataclasses, json, pathlib, typing, zoneinfo; 内核只读解析副本已内联(bridge_instruction_kernel 已葬 78982c4c81/裁定 #420 同期, 见下方"内核只读解析副本"段); zephyr.shared.io.file_utils(safe_write_text); zephyr.shared.utils.time_utils(now_utc); zephyr.ex_core.adapters.qmt_file_bridge_broker(ENV_CONFIG 路径真源, 懒加载)
# [CONSUMERS] scripts.run_post_settlement._run_ghost_order_sentinel_step(日终托管腿, TRD-A10 观察窗 2026-09-29 挂入, 28d596cf96 hosted-leg 同款); 独立 CLI(python -m zephyr.ex_core.ghost_order_sentinel)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读统计不执法——本件是日终读侧对账尺, 禁写指令文件/禁判单/禁复单(运行时执法腿=qmt_file_bridge_broker._reconcile_unconfirmed_claims, 本件只数不动单); 判定复用内核同一把尺(parse_instruction/duplicate_remark_violations=本件内联只读副本, 原内核已葬, 禁第二套解析); 幽灵口径=已盖章(#SENDING/#DONE)下单行且 remark 不在柜台 Order.csv 全量行(含终态行——日终可见性以文件全量为准, 与运行时镜像只留活跃单不同); 柜台导出缺失或非当日=禁判(mirror_fresh=False 时 ghost_count=None, 绝不把回读平面故障反推成"柜台零收录"); 撤单行不走 remark 可见性判据只计数(内核 is_counter_confirmed 同口径); 报告落盘必经 safe_write_text; 时钟注入 now callable, 禁裸 datetime.now(RULE-SCHEMA-TZ); 生产路径不硬编码——由宿主注入 QmtFileBridgeBroker.ENV_CONFIG; 实盘 env=real 仅读侧观察, 实盘四禁不因本件放松
# [MODIFY-GUARD] TRD-A10 桥两缺陷案卷 docs/_working/decision_map_campaign_20260924/links/L07_exec/trd_a10_bridge_client_defects.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 不抛异常——桥文件缺失/解析异常一律降级出报告(status=bridge_missing/judgement_suspended, fail-soft 出声), 托管腿异常由宿主吞并出声不改退出码; CLI exit 0=ran_and_clean / 3=ran_with_findings / 2=judgement_suspended 或 bridge_missing(对齐 run_post_settlement DRIFT=3 出声语义)
# [TESTS] tests/ex_core/test_ghost_order_sentinel.py
# [A_module] module_id=MOD-L06-004-GOS | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""幽灵单日哨兵——TRD-A10 观察窗的日终读侧对账尺。

大白话：TRD-A10 换版后要连看 30 个交易日"零静默丢弃"。运行时腿
（qmt_file_bridge_broker._reconcile_unconfirmed_claims）负责当场把幽灵单
拒单化；本件是**日终读侧的尺子**——收盘后把当日指令文件和柜台官方导出
（Stock/Order.csv）摆在一起，数一数"执行器声称已发、柜台全天零收录"的
单有几张，落一份 JSON 报告给观察窗台账抄数。只数，不动单。

口径（源自已葬内核 bridge_instruction_kernel 的同一把尺——本件内联只读副本，禁第二套解析）：
  幽灵单   = 下单行已被盖章(#SENDING/#DONE=执行器声称下发) 且该 remark 在
             柜台 Order.csv **全量行**(含已成/已撤/废单)里找不到。
  禁判     = Order.csv 缺失或修改日期不是 trade_date（柜台导出停摆≠柜台
             零收录，此时 ghost_count=None，宁缺勿假绿）。
  另列计数 = stuck_sending(#SENDING 日终未闭合)、#FAIL 拒单化行、裸行
             (从未下发)、撤单行(不走 remark 可见性判据)、同 remark 重复
             合同(缺陷②显形面，duplicate_remark_violations 内联副本)。

挂接：run_post_settlement 日终链托管腿（无 cron/Timer，四要素之"自动触发"
= 既有 15:30 结算宿主槽位），先例=28d596cf96 hosted cleaning gate。

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/ghost_order_sentinel.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Final
from zoneinfo import ZoneInfo

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.utils.time_utils import now_utc

# ============================ 内核只读解析副本（自包含化） ============================
# 源自 bridge_instruction_kernel（已葬 78982c4c81 判定/葬法裁定 #420 同期），
# 此处为只读解析副本，唯一消费方=本哨兵。禁回改内核语义——两把尺必须逐字同源。

#: 盖章标记（执行器对指令行的状态戳，与柜台文件面字符串逐字同源）
MARK_SENDING: Final = "#SENDING"
MARK_DONE: Final = "#DONE"
MARK_FAIL: Final = "#FAIL"
_ALL_MARKS: Final = (MARK_SENDING, MARK_DONE, MARK_FAIL)
_HEADER_PREFIX: Final = "order_id"

#: 指令行动作列取值（与 QmtFileBridgeBroker.FileBridgeInstruction 同口径）
ACTION_ORDER: Final = "order"
ACTION_CANCEL: Final = "cancel"


@dataclass(frozen=True)
class InstructionRow:
    """一条指令行的解析视图（源自已葬内核，只读副本）。"""

    order_id: str
    action: str
    body: str
    mark: str = ""
    raw: str = ""
    target: str = ""
    """撤单行的目标 remark（action=cancel 时=柜台配对键），下单行为空。"""

    @property
    def is_claimed(self) -> bool:
        """已被执行器盖章（#SENDING/#DONE/#FAIL）=非裸行。"""
        return bool(self.mark)

    @property
    def is_terminal_mark(self) -> bool:
        return self.mark in (MARK_DONE, MARK_FAIL)


def parse_instruction(raw: str) -> InstructionRow | None:
    """解析一行指令文本（表头/空行/不可解析返回 None）。

    源自 bridge_instruction_kernel（已葬 78982c4c81 判定/葬法裁定 #420 同期），
    此处为只读解析副本，唯一消费方=本哨兵。
    """
    line = raw.strip()
    if not line or line.startswith(_HEADER_PREFIX):
        return None
    mark = ""
    for candidate in _ALL_MARKS:
        if line.startswith(candidate):
            mark = candidate
            line = line[len(candidate) :].strip()
            break
    fields = [f.strip() for f in line.split(",")]
    if len(fields) < 2 or not fields[0]:
        return None
    return InstructionRow(
        order_id=fields[0],
        action=fields[1],
        body=line,
        mark=mark,
        raw=raw,
        target=fields[2] if fields[1] == ACTION_CANCEL and len(fields) > 2 else "",
    )


def duplicate_remark_violations(remark_counts: Mapping[str, int], *, max_allowed: int = 1) -> dict[str, int]:
    """同 remark 合同数>上限=重复申报（缺陷②的柜台侧显形），供告警消费。

    源自 bridge_instruction_kernel（已葬 78982c4c81 判定/葬法裁定 #420 同期），
    此处为只读解析副本，唯一消费方=本哨兵。
    """
    return {remark: n for remark, n in remark_counts.items() if n > max_allowed}


# ========================== 内核只读解析副本段结束 ==========================

_CST: Final = ZoneInfo("Asia/Shanghai")

#: 柜台 Order.csv 的 remark 列号（与 qmt_file_bridge_broker.CounterStateMirror 同列语义）
_REMARK_COL: Final = 9
_REMARK_HEADER: Final = "投资备注"

STATUS_RAN_AND_CLEAN: Final = "ran_and_clean"
STATUS_RAN_WITH_FINDINGS: Final = "ran_with_findings"
STATUS_JUDGEMENT_SUSPENDED: Final = "judgement_suspended"
STATUS_BRIDGE_MISSING: Final = "bridge_missing"

_DEFAULT_REPORT_DIR: Final = Path("data/reports")


@dataclass(frozen=True)
class GhostSentinelReport:
    """日终幽灵单对账报告（观察窗台账的抄数源）。"""

    trade_date: str
    env: str
    orders_file: str
    counter_export: str
    instruction_rows_total: int
    claimed_order_remarks: tuple[str, ...] = ()
    counter_visible_remarks: int = 0
    ghost_remarks: tuple[str, ...] = ()
    ghost_count: int | None = None
    stuck_sending_remarks: tuple[str, ...] = ()
    fail_order_rows: int = 0
    bare_order_rows: int = 0
    cancel_rows: int = 0
    duplicate_remark_violations: dict[str, int] = field(default_factory=dict)
    mirror_fresh: bool = False
    counter_export_age_s: float | None = None
    status: str = STATUS_JUDGEMENT_SUSPENDED
    generated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _read_lines(path: Path) -> list[str]:
    """容错读指令文件（ASCII 写入口径；他人写端可能占用，读失败=空）。"""
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def _load_counter_remarks(stock_dir: Path) -> set[str]:
    """柜台 Order.csv 全量行 remark（含终态——日终可见性以文件全量为准）。

    GBK 读取复用 broker 的共享读实现（QMT 写端可能占用），禁第二套解析器。
    """
    from zephyr.ex_core.adapters.qmt_file_bridge_broker import _read_gbk_csv

    export = stock_dir / "Order.csv"
    if not export.exists():
        return set()
    remarks: set[str] = set()
    for row in _read_gbk_csv(export):
        if len(row) <= _REMARK_COL:
            continue
        remark = row[_REMARK_COL].strip()
        if remark and remark != _REMARK_HEADER:
            remarks.add(remark)
    return remarks


def _export_fresh(stock_dir: Path, trade_date: str, now: Callable[[], datetime]) -> tuple[bool, float | None]:
    """日终新鲜度：Order.csv 存在且修改日期（CST）==trade_date 才可判。

    与运行时 60s 超龄判据不同尺：日终只问"导出是不是当天的"——隔日旧导出
    看不见当日委托，照样是回读平面故障，禁判。
    """
    export = stock_dir / "Order.csv"
    if not export.exists():
        return False, None
    try:
        mtime = datetime.fromtimestamp(export.stat().st_mtime, tz=ZoneInfo("UTC"))
    except OSError:
        return False, None
    age_s = (now() - mtime).total_seconds()
    return mtime.astimezone(_CST).date().isoformat() == trade_date, age_s


def _resolve_bridge_paths(
    env: str,
    orders_file: Path | None,
    stock_dir: Path | None,
) -> tuple[Path, Path]:
    """解析桥文件与柜台导出目录（显式注入优先，缺省回读 QmtFileBridgeBroker.ENV_CONFIG——懒加载）。"""
    if orders_file is not None and stock_dir is not None:
        return orders_file, stock_dir
    from zephyr.ex_core.adapters.qmt_file_bridge_broker import QmtFileBridgeBroker

    cfg = QmtFileBridgeBroker.ENV_CONFIG[env]
    return (
        Path(cfg["orders_file"]) if orders_file is None else orders_file,
        Path(cfg["stock_dir"]) if stock_dir is None else stock_dir,
    )


def run_ghost_order_check(
    *,
    trade_date: str,
    env: str = "sim",
    orders_file: Path | None = None,
    stock_dir: Path | None = None,
    report_dir: Path | None = None,
    now: Callable[[], datetime] | None = None,
) -> GhostSentinelReport:
    """日终对账入口：只读统计当日幽灵单并落报告（不判单不复单不写桥文件）。

    Args:
        trade_date: 对账交易日（YYYY-MM-DD）。
        env: "sim"（默认）/ "real"——real 仅读侧观察。
        orders_file: 指令文件路径；缺省取 QmtFileBridgeBroker.ENV_CONFIG。
        stock_dir: 柜台导出目录；缺省同上。
        report_dir: 报告目录；缺省 data/reports。
        now: 注入时钟（缺省 now_utc，RULE-SCHEMA-TZ）。
    """
    now = now or now_utc
    orders_file, stock_dir = _resolve_bridge_paths(env, orders_file, stock_dir)

    lines = _read_lines(orders_file)
    if not lines:
        report = GhostSentinelReport(
            trade_date=trade_date,
            env=env,
            orders_file=str(orders_file),
            counter_export=str(stock_dir / "Order.csv"),
            instruction_rows_total=0,
            mirror_fresh=False,
            status=STATUS_BRIDGE_MISSING,
            generated_at=now().isoformat(),
        )
        _write_report(report, report_dir)
        return report

    rows = [r for r in (parse_instruction(ln) for ln in lines) if r is not None]
    order_rows = [r for r in rows if r.action == ACTION_ORDER]
    claimed = [r for r in order_rows if r.mark in (MARK_SENDING, MARK_DONE)]
    claimed_remarks = tuple(sorted({r.order_id for r in claimed}))
    stuck_sending = tuple(sorted({r.order_id for r in order_rows if r.mark == MARK_SENDING}))
    dup = duplicate_remark_violations(Counter(r.order_id for r in order_rows))
    mirror_fresh, age_s = _export_fresh(stock_dir, trade_date, now)

    ghost_remarks: tuple[str, ...] = ()
    ghost_count: int | None = None
    if mirror_fresh:
        counter_remarks = _load_counter_remarks(stock_dir)
        ghost_remarks = tuple(sorted(set(claimed_remarks) - counter_remarks))
        ghost_count = len(ghost_remarks)
        status = STATUS_RAN_WITH_FINDINGS if ghost_count > 0 else STATUS_RAN_AND_CLEAN
    else:
        counter_remarks: set[str] = set()
        status = STATUS_JUDGEMENT_SUSPENDED

    report = GhostSentinelReport(
        trade_date=trade_date,
        env=env,
        orders_file=str(orders_file),
        counter_export=str(stock_dir / "Order.csv"),
        instruction_rows_total=len(rows),
        claimed_order_remarks=claimed_remarks,
        counter_visible_remarks=len(counter_remarks),
        ghost_remarks=ghost_remarks,
        ghost_count=ghost_count,
        stuck_sending_remarks=stuck_sending,
        fail_order_rows=sum(1 for r in order_rows if r.mark == MARK_FAIL),
        bare_order_rows=sum(1 for r in order_rows if not r.mark),
        cancel_rows=sum(1 for r in rows if r.action == ACTION_CANCEL),
        duplicate_remark_violations=dict(dup),
        mirror_fresh=mirror_fresh,
        counter_export_age_s=age_s,
        status=status,
        generated_at=now().isoformat(),
    )
    _write_report(report, report_dir)
    return report


def _write_report(report: GhostSentinelReport, report_dir: Path | None) -> Path:
    target_dir = Path(report_dir) if report_dir is not None else _DEFAULT_REPORT_DIR
    out = target_dir / f"ghost_order_sentinel_{report.trade_date}_{report.env}.json"
    safe_write_text(out, json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n")
    return out


def main(argv: list[str] | None = None) -> int:
    """独立 CLI：python -m zephyr.ex_core.ghost_order_sentinel --trade-date YYYY-MM-DD"""
    parser = argparse.ArgumentParser(description="TRD-A10 幽灵单日哨兵（日终读侧对账尺，只读）")
    parser.add_argument("--trade-date", required=True, help="对账交易日 YYYY-MM-DD")
    parser.add_argument("--env", default="sim", choices=["sim", "real"], help="桥环境（real 仅读侧观察）")
    parser.add_argument("--report-dir", default=None, help="报告目录（缺省 data/reports）")
    args = parser.parse_args(argv)
    report = run_ghost_order_check(
        trade_date=args.trade_date,
        env=args.env,
        report_dir=Path(args.report_dir) if args.report_dir else None,
    )
    print(
        f"[ghost-order-sentinel] date={report.trade_date} env={report.env} status={report.status} "
        f"ghost={report.ghost_count} stuck_sending={len(report.stuck_sending_remarks)} "
        f"duplicate={len(report.duplicate_remark_violations)}"
    )
    if report.status == STATUS_RAN_WITH_FINDINGS:
        print(f"[ghost-order-sentinel] 幽灵单 remark: {', '.join(report.ghost_remarks)}")
    return {"ran_and_clean": 0, "ran_with_findings": 3}.get(report.status, 2)


if __name__ == "__main__":
    sys.exit(main())
