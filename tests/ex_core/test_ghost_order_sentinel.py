# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint_qmt_file_bridge.md
# [MODULE] tests.ex_core.test_ghost_order_sentinel
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.ghost_order_sentinel; scripts.run_post_settlement; pytest
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 红绿合成数据：有幽灵单→报告 N>0(ran_with_findings)、干净→0(ran_and_clean)、柜台导出停摆→禁判(ghost_count=None 不假绿)；全程 tmp_path 假文件+注入时钟，零 socket 零交易通道零生产 data/ 写入；测试隔离铁律——托管腿经 report_dir 注入 tmp，不落生产 data/reports
# [MODIFY-GUARD] TRD-A10 桥客户端两缺陷案卷
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L06-004-GOS | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""幽灵单日哨兵红绿测试（TRD-A10 观察窗对账尺）。

盖行格式与内核 _merge_transitions 同款（`mark + 空格 + body`）；柜台 Order.csv
列语义与 CounterStateMirror 同源（col9=remark，GBK）。指令行格式与 broker
_append_instruction 同款：`order_id,action,symbol,side,qty,pricetype,price`。
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from zephyr.ex_core.ghost_order_sentinel import run_ghost_order_check

_CST = ZoneInfo("Asia/Shanghai")
_TRADE_DATE = "2026-09-29"
_NOW = datetime(2026, 9, 29, 8, 0, 0, tzinfo=timezone.utc)  # = CST 16:00 当日盘后

_HEADER = "order_id,action,symbol,side,qty,pricetype,price"

_ORDERS_DIRTY = "\n".join(
    [
        _HEADER,
        "R1,order,600000.SH,buy,100,fix,10.0",  # 盖章 #DONE 且柜台可见=正常
        "#DONE R1,order,600000.SH,buy,100,fix,10.0",
        "#DONE R2,order,000001.SZ,sell,200,fix,20.0",  # 幽灵：柜台全天零收录
        "#SENDING R3,order,600036.SH,buy,300,fix,30.0",  # 柜台可见但日终未闭合
        "#FAIL R4,order,600050.SH,buy,400,fix,4.0",  # 拒单化=非幽灵
        "R5,cancel,R1",  # 撤单行不走可见性判据
        "R6,order,601398.SH,buy,500,fix,5.0",  # 裸行=从未下发
        "#DONE R7,order,601988.SH,buy,600,fix,6.0",  # 幽灵
        "#DONE R2,order,000001.SZ,sell,200,fix,20.0",  # 同 remark 重复合同
        "",
    ]
)

_ORDERS_CLEAN = "\n".join(
    [
        _HEADER,
        "#DONE R1,order,600000.SH,buy,100,fix,10.0",
        "#SENDING R2,order,000001.SZ,sell,200,fix,20.0",
        "",
    ]
)


def _make_counter_csv(stock_dir: Path, visible: set[str]) -> Path:
    """合成柜台官方导出（26 列，col9=remark，含表头行，GBK）。"""
    stock_dir.mkdir(parents=True, exist_ok=True)
    out = stock_dir / "Order.csv"
    rows: list[list[str]] = []
    header = [f"col{i}" for i in range(26)]
    header[9] = "投资备注"
    rows.append(header)
    for i, remark in enumerate(sorted(visible)):
        row = [f"c{j}" for j in range(26)]
        row[9] = remark
        row[15] = f"sysid{i}"
        row[16] = "已报" if i % 2 == 0 else "全部成交"  # 活跃+终态混合——日终全量可见
        rows.append(row)
    out.write_text("\n".join(",".join(r) for r in rows) + "\n", encoding="gbk")
    return out


def _touch_today(path: Path) -> None:
    """把文件 mtime 钉在注入时钟对应交易日内（CST 判日口径）。"""
    stamp = _NOW.timestamp()
    os.utime(path, (stamp, stamp))


def _now() -> datetime:
    return _NOW


def _run(tmp_path: Path, orders_text: str, visible: set[str] | None, stock_dir: Path | None = None):
    bridge = tmp_path / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    orders = bridge / "orders_sim.csv"
    orders.write_text(orders_text, encoding="ascii")
    stock = stock_dir if stock_dir is not None else tmp_path / "stock"
    if visible is not None:
        _touch_today(_make_counter_csv(stock, visible))
    report = run_ghost_order_check(
        trade_date=_TRADE_DATE,
        env="sim",
        orders_file=orders,
        stock_dir=stock,
        report_dir=tmp_path / "reports",
        now=_now,
    )
    return report, tmp_path / "reports" / f"ghost_order_sentinel_{_TRADE_DATE}_sim.json"


class TestGhostCountRedGreen:
    """红：有幽灵单→N>0；绿：干净→0。"""

    def test_red_ghost_found_when_counter_silent(self, tmp_path: Path) -> None:
        report, report_file = _run(tmp_path, _ORDERS_DIRTY, visible={"R1", "R3"})
        assert report.status == "ran_with_findings"
        assert report.ghost_count == 2
        assert set(report.ghost_remarks) == {"R2", "R7"}
        assert report.mirror_fresh is True

    def test_green_clean_day_zero_ghost(self, tmp_path: Path) -> None:
        report, _ = _run(tmp_path, _ORDERS_CLEAN, visible={"R1", "R2"})
        assert report.status == "ran_and_clean"
        assert report.ghost_count == 0
        assert report.ghost_remarks == ()

    def test_filled_order_remark_stays_visible_at_day_end(self, tmp_path: Path) -> None:
        """已成单 remark 仍在柜台导出全量行里=不算幽灵（与运行时活跃镜像不同口径）。"""
        report, _ = _run(tmp_path, _ORDERS_CLEAN, visible={"R1", "R2"})
        assert report.counter_visible_remarks == 2


class TestSideCounts:
    """同报告里的另列计数面（stuck/fail/bare/cancel/duplicate）。"""

    def test_side_counts_on_dirty_day(self, tmp_path: Path) -> None:
        report, _ = _run(tmp_path, _ORDERS_DIRTY, visible={"R1", "R3"})
        assert report.stuck_sending_remarks == ("R3",)
        assert report.fail_order_rows == 1
        assert report.bare_order_rows == 2  # R1 的裸行 + R6（R1 先裸写后被盖章=两行并存）
        assert report.cancel_rows == 1
        assert report.duplicate_remark_violations == {"R1": 2, "R2": 2}  # 内核口径:同 remark 行数(裸行+盖章行)
        assert report.instruction_rows_total == 9

    def test_report_json_written(self, tmp_path: Path) -> None:
        _, report_file = _run(tmp_path, _ORDERS_DIRTY, visible={"R1"})
        assert report_file.exists()
        payload = json.loads(report_file.read_text(encoding="utf-8"))
        assert payload["trade_date"] == _TRADE_DATE
        assert payload["ghost_count"] == 3  # R2/R7 #DONE 不可见 + R3 #SENDING 不可见
        assert payload["status"] == "ran_with_findings"


class TestHonestSuspension:
    """柜台导出停摆=禁判，绝不假绿（ghost_count=None）。"""

    def test_missing_counter_export_suspends_judgement(self, tmp_path: Path) -> None:
        report, _ = _run(tmp_path, _ORDERS_DIRTY, visible=None)
        assert report.status == "judgement_suspended"
        assert report.ghost_count is None
        assert report.mirror_fresh is False

    def test_stale_export_from_other_day_suspends_judgement(self, tmp_path: Path) -> None:
        """导出存在但修改日期非 trade_date=看不见当日柜台，禁判。"""
        stock = tmp_path / "stale_stock"
        _make_counter_csv(stock, {"R1", "R3"})
        stamp = datetime(2026, 9, 26, 8, 0, 0, tzinfo=timezone.utc).timestamp()
        os.utime(stock / "Order.csv", (stamp, stamp))
        report, _ = _run(tmp_path, _ORDERS_DIRTY, visible=None, stock_dir=stock)
        assert report.status == "judgement_suspended"
        assert report.ghost_count is None
        assert report.counter_export_age_s is not None and report.counter_export_age_s > 0

    def test_bridge_missing_degrades_without_raise(self, tmp_path: Path) -> None:
        report = run_ghost_order_check(
            trade_date=_TRADE_DATE,
            orders_file=tmp_path / "nope.csv",
            stock_dir=tmp_path / "no_stock",
            report_dir=tmp_path / "reports",
            now=_now,
        )
        assert report.status == "bridge_missing"
        assert report.instruction_rows_total == 0


class TestHostedLeg:
    """run_post_settlement 托管腿：出声不阻断、report_dir 可注入（测试隔离）。"""

    def test_step_writes_report_to_injected_dir(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from scripts.run_post_settlement import _run_ghost_order_sentinel_step
        from zephyr.ex_core.adapters.qmt_file_bridge_broker import QmtFileBridgeBroker

        bridge = tmp_path / "bridge"
        bridge.mkdir()
        (bridge / "orders_sim.csv").write_text(_ORDERS_CLEAN, encoding="ascii")
        stock = tmp_path / "stock"
        _touch_today(_make_counter_csv(stock, {"R1", "R2"}))
        monkeypatch.setitem(
            QmtFileBridgeBroker.ENV_CONFIG,
            "sim",
            {"orders_file": str(bridge / "orders_sim.csv"), "stock_dir": str(stock)},
        )
        reports = tmp_path / "reports"
        _run_ghost_order_sentinel_step(_TRADE_DATE, report_dir=reports)  # 不抛=托管腿纪律
        payload = json.loads((reports / f"ghost_order_sentinel_{_TRADE_DATE}_sim.json").read_text(encoding="utf-8"))
        assert payload["status"] == "ran_and_clean"

    def test_step_swallows_missing_bridge(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from scripts.run_post_settlement import _run_ghost_order_sentinel_step
        from zephyr.ex_core.adapters.qmt_file_bridge_broker import QmtFileBridgeBroker

        monkeypatch.setitem(
            QmtFileBridgeBroker.ENV_CONFIG,
            "sim",
            {"orders_file": str(tmp_path / "absent.csv"), "stock_dir": str(tmp_path / "no_stock")},
        )
        reports = tmp_path / "reports"
        _run_ghost_order_sentinel_step(_TRADE_DATE, report_dir=reports)  # 桥缺失也不抛
        assert (reports / f"ghost_order_sentinel_{_TRADE_DATE}_sim.json").exists()
