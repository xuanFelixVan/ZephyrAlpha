# [A_test] module_id: MOD-SCRIPT-start_paper_session | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SCRIPT-start_paper_session | scripts/start_paper_session.py | §
# [MODULE] tests.ex_core.test_fill_jsonl_single_writer
# [DOMAIN] D_EX_CORE
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_fill_jsonl_single_writer.py — M7-BF-5「Fill 事实单一写者」验收钉（F57 恒空的总根）。

病根（2026-09-26 实测，非推测）：成交只进 `tracker.apply_fill`，而
`FillHandler.process_fill` 的 JSONL 落盘腿**全仓无生产调用方** → `data/fills/`
自 08-27 起零文件 → F57 盘后结算对账/EOD 的"系统侧输入"结构性恒空，
拿空表仍判 PASS=假绿。

本件钉四件事（全部 tmp 目录，禁写生产 data/fills——宪法 §9.6）：
  1. 生产装配点跑通后 fills_dir **真出现文件**，且 F57 读取口径
     （`FillHandler.query_fills_by_date`）能原样读回（写读闭环）。
  2. **单一写者**：AST 静态扫描 src/ + scripts/，同时"构造 FillHandler(fills_dir=…)"
     且"调用 process_fill"的文件必须恰好一个＝`scripts/start_paper_session.py`；
     第二处出现即红（不得两处写同一路径）。
  3. 写者不得二次污染在管订单：OrderManager._on_fill 已在回调链**之前**就地累加
     filled_quantity/avg_fill_price/status，写者若直接吃活订单=同一笔计两次。
  4. fill_id 重放（同派发器/跨重启持久去重集）全历史只落一行，
     券商单号口径（fill.order_id=broker_order_id）的成交也必须落盘。
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from zephyr.ex_core.fill_handler import FillHandler
from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.state_store import AppendOnlyDedupSet

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "start_paper_session",
    _ROOT / "scripts" / "start_paper_session.py",
)
sps = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("start_paper_session", sps)  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(sps)

#: 唯一合法生产写点（相对仓库根，POSIX 分隔符）
_SINGLE_WRITER_SITE = "scripts/start_paper_session.py"


def _fill(order_id: str, *, fill_id: str = "f1", symbol: str = "600000.SH", qty: str = "100") -> Fill:
    return Fill(
        fill_id=fill_id,
        fill_price=Decimal("10"),
        fill_timestamp=datetime(2026, 8, 21, 2, 0, tzinfo=UTC),
        filled_quantity=Decimal(qty),
        idempotency_key=f"ik-{fill_id}",
        order_id=order_id,
        strategy_id="paper-keepalive",
        symbol=symbol,
    )


def _order(om: OrderManager, symbol: str = "600000.SH", qty: str = "100"):
    order = om.create_order(
        symbol=symbol,
        strategy_id="paper-keepalive",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal(qty),
    )
    order.broker_order_id = f"brk-{order.order_id[:6]}"
    return order


def _wire(tmp_path: Path, om: OrderManager, *, dedup_path: Path | None = None):
    """生产装配点直调（fills_dir/去重文件全部注入 tmp，禁写 data/）。"""
    tracker = PositionTracker(initial_cash=Decimal("1000000"), portfolio_id="paper-book-test")
    return sps._wire_position_book_feed(
        om,
        tracker,
        strategy_id="paper-keepalive",
        fills_dir=tmp_path / "fills",
        fill_jsonl_dedup_path=dedup_path if dedup_path is not None else tmp_path / "state" / "paper_fill_jsonl_written",
    )


def _jsonl_files(tmp_path: Path) -> list[Path]:
    return sorted((tmp_path / "fills").glob("*.jsonl"))


def _read_lines(tmp_path: Path) -> list[dict]:
    rows: list[dict] = []
    for path in _jsonl_files(tmp_path):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


class TestFillJsonlProducer:
    def test_dispatched_fills_land_a_real_file(self, tmp_path):
        """跑通装配链后 fills_dir 真出现文件——F57 系统侧输入自此非结构性恒空。"""
        om = OrderManager()
        dispatcher = _wire(tmp_path, om)
        order = _order(om, qty="300")
        om._on_fill(_fill(order.order_id, fill_id="f0", qty="100"))
        om._on_fill(_fill(order.order_id, fill_id="f1", qty="100"))
        om._on_fill(_fill(order.order_id, fill_id="f2", symbol="000001.SZ", qty="100"))
        assert dispatcher.stop(timeout=5.0) is True

        files = _jsonl_files(tmp_path)
        assert len(files) == 1, "成交按交易日归档，一日一文件"
        rows = _read_lines(tmp_path)
        assert sorted(r["fill"]["fill_id"] for r in rows) == ["f0", "f1", "f2"]
        assert rows[0]["trade_date"] == "20260821"

    def test_f57_reader_roundtrips_what_the_writer_wrote(self, tmp_path):
        """写读闭环：F57 用 query_fills_by_date 读到的笔数/字段必须与写入一致。"""
        om = OrderManager()
        dispatcher = _wire(tmp_path, om)
        order = _order(om, qty="200")
        om._on_fill(_fill(order.order_id, fill_id="f0", qty="100"))
        om._on_fill(_fill(order.order_id, fill_id="f1", qty="100"))
        assert dispatcher.stop(timeout=5.0) is True

        reader = FillHandler(fills_dir=tmp_path / "fills")
        fills = reader.query_fills_by_date("2026-08-21")
        assert [f.fill_id for f in fills] == ["f0", "f1"]
        assert fills[0].fill_price == Decimal("10")
        assert fills[0].filled_quantity == Decimal("100")
        assert fills[0].symbol == "600000.SH"

    def test_broker_order_id_keyed_fill_is_not_silently_dropped(self, tmp_path):
        """券商单号口径（fill.order_id=broker_order_id）也必须落盘。

        写者的 order_id 一致性校验若按本地 UUID 走，这笔必抛 OrderNotFoundError，
        被派发线程计入 errors 吞掉=又一条静默丢失的 Fill 事实。
        """
        om = OrderManager()
        dispatcher = _wire(tmp_path, om)
        order = _order(om)
        om._on_fill(_fill(order.broker_order_id, fill_id="fb"))
        assert dispatcher.stop(timeout=5.0) is True
        assert dispatcher.stats.errors == 0
        assert [r["fill"]["fill_id"] for r in _read_lines(tmp_path)] == ["fb"]


class TestSingleWriterDiscipline:
    def test_live_order_is_never_second_counted_by_the_writer(self, tmp_path):
        """写者只吃快照：活订单的 filled_quantity/status 不得因落盘腿再动一次。"""
        om = OrderManager()
        dispatcher = _wire(tmp_path, om)
        order = _order(om, qty="100")
        om._on_fill(_fill(order.order_id, fill_id="f0", qty="100"))
        assert dispatcher.stop(timeout=5.0) is True
        # OrderManager._on_fill 自己已累加一次（100），写者再累加就是 200=账实不符
        assert order.filled_quantity == Decimal("100")
        assert order.avg_fill_price == Decimal("10")
        assert [r["fill"]["fill_id"] for r in _read_lines(tmp_path)] == ["f0"]

    def test_replayed_fill_id_writes_exactly_one_line(self, tmp_path):
        """同一派发器内重放同一 fill_id：JSONL 只有一行（幂等写者）。"""
        om = OrderManager()
        dispatcher = _wire(tmp_path, om)
        order = _order(om, qty="400")
        om._on_fill(_fill(order.order_id, fill_id="dup", qty="100"))
        om._on_fill(_fill(order.order_id, fill_id="dup", qty="100"))
        assert dispatcher.stop(timeout=5.0) is True
        assert [r["fill"]["fill_id"] for r in _read_lines(tmp_path)] == ["dup"]

    def test_writer_dedup_survives_process_restart(self, tmp_path):
        """跨"重启"重放（recover_from_broker 语义）也只落一行：去重集必须持久。

        写者若只用内存 set，--service 退避重启后重放当日成交会在 JSONL 造重复行，
        F57 系统侧笔数虚高=反向假绿。
        """
        fills_dir = tmp_path / "fills"
        dedup_path = tmp_path / "state" / "paper_fill_jsonl_written"
        order = _order(OrderManager(), qty="100")

        first = FillHandler(dedup_store=AppendOnlyDedupSet(dedup_path), fills_dir=fills_dir)
        assert first.process_fill(_fill(order.order_id, fill_id="r1"), order).fill_count == 1

        second = FillHandler(dedup_store=AppendOnlyDedupSet(dedup_path), fills_dir=fills_dir)
        second.process_fill(_fill(order.order_id, fill_id="r1"), order)
        assert [r["fill"]["fill_id"] for r in _read_lines(tmp_path)] == ["r1"]

    def test_exactly_one_producer_writes_the_fills_dir(self):
        """静态扫 src/+scripts/：同时"FillHandler(fills_dir=…)"＋"调用 process_fill"的文件必须唯一。

        两处即=两个写者抢同一目录（同一 fill_id 落两行，或互相覆盖当日文件），
        这正是 BF-5 的病根形态，判据=文件集合恰好等于 {_SINGLE_WRITER_SITE}。
        """
        sites: list[str] = []
        unparsed: list[str] = []
        for pkg in ("src", "scripts"):
            for path in sorted((_ROOT / pkg).rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue
                try:
                    tree = ast.parse(path.read_text(encoding="utf-8"))
                except (SyntaxError, UnicodeDecodeError):
                    # 破损件由结构门禁 own-scope 处置，本判据只认"能解析的写点"，
                    # 不替他道在途件连坐（宪法 §3.1）
                    unparsed.append(path.relative_to(_ROOT).as_posix())
                    continue
                makes_writer = False
                calls_process_fill = False
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    fn = node.func
                    fname = getattr(fn, "id", None) or getattr(fn, "attr", None) or ""
                    if fname == "FillHandler" and any(k.arg == "fills_dir" for k in node.keywords):
                        makes_writer = True
                    if fname == "process_fill":
                        calls_process_fill = True
                if makes_writer and calls_process_fill:
                    sites.append(path.relative_to(_ROOT).as_posix())
        assert sites == [_SINGLE_WRITER_SITE], (
            f"Fill JSONL 写者必须唯一，实测={sites}（另有 {len(unparsed)} 件不可解析，未计入）"
        )

    def test_facade_does_not_default_a_fills_dir(self):
        """AggregateRootManager 门面不得自带落盘目录（否则注入即成第二写者）。"""
        src = (_ROOT / "src" / "zephyr" / "ex_core" / "aggregate_root_manager.py").read_text(encoding="utf-8")
        assert "fills_dir" not in src, "门面若开始关心落盘目录，必须与单一写者判据同批复核"

    def test_production_fills_dir_constant_points_at_repo_data_fills(self):
        """生产缺省目录口径不得被测试注入顺手改掉（F57 读的是同一个根）。"""
        assert sps._DEFAULT_FILLS_DIR == (_ROOT / "data" / "fills")
        assert sps._FILL_JSONL_DEDUP_NAME == "paper_fill_jsonl_written"
