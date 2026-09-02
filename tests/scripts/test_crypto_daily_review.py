# [A_test] module_id: MOD-SCRIPT-crypto_daily_review | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-SCRIPT-crypto_daily_review | scripts/crypto_daily_review.py | §
# [MODULE] tests.scripts.test_crypto_daily_review
# [DOMAIN] D_TRADING
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""test_crypto_daily_review.py — UTC 日切复盘脚本单测（tmp 隔离，不碰生产 data/docs）。

覆盖：
  1. CLI 参数解析（--date/--shift 缺省与显式）
  2. resolve_date（显式校验 / 非法格式 / 缺省今日 UTC）
  3. shift_window（三班窗口半开区间，shift=16 跨日界）
  4. load_category_records + filter_window（当日+次日文件 / 坏行跳过 / 半开过滤 / 时区归一）
  5. 五节聚合 summarize_*（持仓符号约定 / 成交合计 / 资金费率 / 信号命中率 / 系统最差状态）
  6. render_markdown（五节齐全 / 降级"无数据（未接线）" / 标注节）
  7. main 端到端（tmp 数据根+报告目录：报告写盘 / exit 码 / 幂等覆盖 / 降级标注打印）
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "crypto_daily_review",
    _ROOT / "scripts" / "crypto_daily_review.py",
)
cdr = importlib.util.module_from_spec(_spec)
sys.modules["crypto_daily_review"] = cdr  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(cdr)

_DATE = "2026-08-28"  # 复盘日（周五）
_TZ = timezone.utc


def _write_jsonl(data_root: Path, category: str, day: str, records: list[dict]) -> None:
    """按落盘口径写 {data_root}/{category}/{YYYYMMDD}.jsonl。"""
    dir_path = data_root / category
    dir_path.mkdir(parents=True, exist_ok=True)
    path = dir_path / f"{day}.jsonl"
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _fill(
    ts: str, symbol: str = "BTC-USDT", side: str = "buy", price: str = "30000", qty: str = "0.1", fee: str = "0.6"
) -> dict:
    return {"ts": ts, "symbol": symbol, "side": side, "price": price, "qty": qty, "fee": fee, "trade_id": f"t-{ts}"}


# ── 1. CLI 参数解析 ──


class TestParseArgs:
    def test_defaults(self):
        args = cdr.parse_args([])
        assert args.date is None
        assert args.shift == 0

    def test_explicit(self):
        args = cdr.parse_args(["--date", _DATE, "--shift", "16"])
        assert args.date == _DATE
        assert args.shift == 16

    def test_shift_choices_reject_invalid(self):
        with pytest.raises(SystemExit):
            cdr.parse_args(["--shift", "4"])


# ── 2. resolve_date ──


class TestResolveDate:
    def test_explicit_valid(self):
        assert cdr.resolve_date(_DATE) == _DATE

    def test_default_today_utc(self):
        assert cdr.resolve_date(None, today=date(2026, 8, 28)) == _DATE

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="格式非法"):
            cdr.resolve_date("2026/08/28")

    def test_compact_digits_rejected(self):
        with pytest.raises(ValueError, match="格式非法"):
            cdr.resolve_date("20260828")

    def test_non_padded_rejected(self):
        with pytest.raises(ValueError, match="格式非法"):
            cdr.resolve_date("2026-8-1")

    def test_non_calendar_day_rejected(self):
        with pytest.raises(ValueError, match="合法日历日"):
            cdr.resolve_date("2026-02-30")


# ── 3. shift_window ──


class TestShiftWindow:
    def test_shift_0(self):
        start, end = cdr.shift_window(_DATE, 0)
        assert start == datetime(2026, 8, 28, 0, tzinfo=_TZ)
        assert end == datetime(2026, 8, 28, 8, tzinfo=_TZ)

    def test_shift_8(self):
        start, end = cdr.shift_window(_DATE, 8)
        assert start == datetime(2026, 8, 28, 8, tzinfo=_TZ)
        assert end == datetime(2026, 8, 28, 16, tzinfo=_TZ)

    def test_shift_16_crosses_day_boundary(self):
        start, end = cdr.shift_window(_DATE, 16)
        assert start == datetime(2026, 8, 28, 16, tzinfo=_TZ)
        assert end == datetime(2026, 8, 29, 0, tzinfo=_TZ)

    def test_invalid_shift(self):
        with pytest.raises(ValueError, match="取值非法"):
            cdr.shift_window(_DATE, 4)


# ── 4. 数据读取与窗口过滤 ──


class TestLoadAndFilter:
    def test_missing_file_returns_not_found(self, tmp_path):
        records, found = cdr.load_category_records(tmp_path, "fills", _DATE)
        assert records == []
        assert found is False

    def test_reads_current_and_next_day_files(self, tmp_path):
        _write_jsonl(tmp_path, "fills", "20260828", [_fill("2026-08-28T17:00:00+00:00")])
        _write_jsonl(tmp_path, "fills", "20260829", [_fill("2026-08-29T00:30:00+00:00")])
        records, found = cdr.load_category_records(tmp_path, "fills", _DATE)
        assert found is True
        assert len(records) == 2

    def test_bad_lines_skipped(self, tmp_path):
        dir_path = tmp_path / "fills"
        dir_path.mkdir(parents=True)
        (dir_path / "20260828.jsonl").write_text(
            '{"ts": "2026-08-28T01:00:00+00:00", "symbol": "BTC-USDT"}\nnot-a-json\n{"symbol": "no-ts"}\n\n',
            encoding="utf-8",
        )
        records, found = cdr.load_category_records(tmp_path, "fills", _DATE)
        assert found is True
        assert len(records) == 1

    def test_naive_ts_treated_as_utc_and_z_suffix(self, tmp_path):
        _write_jsonl(
            tmp_path,
            "fills",
            "20260828",
            [_fill("2026-08-28T01:00:00"), _fill("2026-08-28T02:00:00Z")],
        )
        records, _ = cdr.load_category_records(tmp_path, "fills", _DATE)
        assert records[0]["_ts"] == datetime(2026, 8, 28, 1, tzinfo=_TZ)
        assert records[1]["_ts"] == datetime(2026, 8, 28, 2, tzinfo=_TZ)

    def test_filter_window_half_open(self):
        start, end = cdr.shift_window(_DATE, 0)

        def _rec(hour: int, minute: int = 0) -> dict:
            return {"_ts": datetime(2026, 8, 28, hour, minute, tzinfo=_TZ)}

        records = [_rec(0), _rec(7, 59), _rec(8), _rec(0, 30)]
        got = cdr.filter_window(records, start, end)
        # 起点含、终点斥；结果按 ts 升序
        assert [r["_ts"].hour * 60 + r["_ts"].minute for r in got] == [0, 30, 7 * 60 + 59]

    def test_shift_16_includes_late_night_excludes_next_midnight(self, tmp_path):
        _write_jsonl(
            tmp_path,
            "fills",
            "20260828",
            [_fill("2026-08-28T23:30:00+00:00"), _fill("2026-08-28T15:59:59+00:00")],
        )
        _write_jsonl(tmp_path, "fills", "20260829", [_fill("2026-08-29T00:00:00+00:00")])
        records, _ = cdr.load_category_records(tmp_path, "fills", _DATE)
        start, end = cdr.shift_window(_DATE, 16)
        got = cdr.filter_window(records, start, end)
        assert len(got) == 1
        assert got[0]["_ts"] == datetime(2026, 8, 28, 23, 30, tzinfo=_TZ)


# ── 5. 五节聚合 ──


def _rec(ts_hour: int, **kw) -> dict:
    """构造已过 _parse_ts 口径的窗口内记录（shift 0 窗口 00:00-08:00）。"""
    return {"ts": f"2026-08-28T0{ts_hour}:00:00+00:00", "_ts": datetime(2026, 8, 28, ts_hour, tzinfo=_TZ), **kw}


class TestSummarizePositions:
    def test_net_direction_sign_convention(self):
        records = [
            _rec(1, symbol="BTC-USDT", side="long", qty="0.5", action="open"),
            _rec(2, symbol="BTC-USDT", side="long", qty="0.2", action="decrease"),
            _rec(3, symbol="ETH-USDT", side="short", qty="2", action="open"),
            _rec(4, symbol="ETH-USDT", side="short", qty="1", action="close"),
        ]
        s = cdr.summarize_positions(records)
        assert s["total_events"] == 4
        btc = s["per_symbol"]["BTC-USDT"]
        assert btc["events"] == 2
        assert btc["opened"] == Decimal("0.5")
        assert btc["closed"] == Decimal("0.2")
        assert btc["net"] == Decimal("0.3")  # 多仓净增
        eth = s["per_symbol"]["ETH-USDT"]
        # 空仓：open=-2、close=+1 → 净 -1
        assert eth["net"] == Decimal("-1")

    def test_empty(self):
        s = cdr.summarize_positions([])
        assert s["total_events"] == 0
        assert s["per_symbol"] == {}


class TestSummarizeFills:
    def test_totals_and_per_symbol(self):
        records = [
            _rec(1, symbol="BTC-USDT", side="buy", price="30000", qty="0.1", fee="0.6"),
            _rec(2, symbol="BTC-USDT", side="sell", price="31000", qty="0.1", fee="0.62"),
            _rec(3, symbol="ETH-USDT", side="buy", price="2000", qty="1", fee="0.4"),
        ]
        s = cdr.summarize_fills(records)
        assert s["total"] == 3
        assert s["buy_count"] == 2
        assert s["sell_count"] == 1
        assert s["total_notional"] == Decimal("3000") + Decimal("3100") + Decimal("2000")
        assert s["total_fees"] == Decimal("1.62")
        btc = s["per_symbol"]["BTC-USDT"]
        assert btc["count"] == 2
        assert btc["buy_qty"] == Decimal("0.1")
        assert btc["sell_qty"] == Decimal("0.1")


class TestSummarizeFunding:
    def test_per_symbol_stats(self):
        records = [
            _rec(1, symbol="BTC-USDT", rate="0.0001", payment="0.3"),
            _rec(2, symbol="BTC-USDT", rate="0.0003", payment="0.9"),
            _rec(3, symbol="ETH-USDT", rate="-0.0002", payment="-0.1"),
        ]
        s = cdr.summarize_funding(records)
        assert s["total_events"] == 3
        btc = s["per_symbol"]["BTC-USDT"]
        assert btc["count"] == 2
        assert btc["avg_rate"] == Decimal("0.0002")
        assert btc["min"] == Decimal("0.0001")
        assert btc["max"] == Decimal("0.0003")
        assert btc["payment_sum"] == Decimal("1.2")
        # 最新费率=窗口内 ts 最大者
        assert btc["latest_rate"] == Decimal("0.0003")
        assert s["per_symbol"]["ETH-USDT"]["payment_sum"] == Decimal("-0.1")


class TestSummarizeSignals:
    def test_hit_rate_resolved_only(self):
        records = [
            _rec(1, symbol="BTC-USDT", signal="long", outcome="hit"),
            _rec(2, symbol="ETH-USDT", signal="short", outcome="miss"),
            _rec(3, symbol="BTC-USDT", signal="long", outcome="hit"),
            _rec(4, symbol="SOL-USDT", signal="flat", outcome="pending"),
        ]
        s = cdr.summarize_signals(records)
        assert s["total"] == 4
        assert s["hits"] == 2 and s["misses"] == 1 and s["pending"] == 1
        assert s["hit_rate"] == Decimal(2) / Decimal(3)

    def test_hit_rate_none_when_no_resolved(self):
        s = cdr.summarize_signals([_rec(1, outcome="pending")])
        assert s["hit_rate"] is None


class TestSummarizeSystem:
    def test_overall_worst_status(self):
        records = [
            _rec(1, component="gateway", status="ok", message="up"),
            _rec(2, component="feed", status="warn", message="lag"),
            _rec(3, component="feed", status="error", message="down"),
        ]
        s = cdr.summarize_system(records)
        assert s["overall"] == "error"
        assert s["counts"] == {"ok": 1, "warn": 1, "error": 1, "unknown": 0}
        assert len(s["latest"]) == 3

    def test_overall_warn_without_error(self):
        s = cdr.summarize_system([_rec(1, component="feed", status="warn", message="lag")])
        assert s["overall"] == "warn"

    def test_empty_unknown(self):
        assert cdr.summarize_system([])["overall"] == "unknown"


# ── 6. render_markdown ──


class TestRenderMarkdown:
    def _render(self, sections, notes=None):
        start, end = cdr.shift_window(_DATE, 0)
        return cdr.render_markdown(
            _DATE,
            0,
            start,
            end,
            sections,
            notes or [],
            generated_at=datetime(2026, 8, 28, 8, 5, tzinfo=_TZ),
        )

    def test_all_five_sections_present(self):
        md = self._render({c: [] for c in cdr.CATEGORIES})
        for header in (
            "## 1. 持仓变化",
            "## 2. 成交记录",
            "## 3. 资金费率",
            "## 4. 信号验证",
            "## 5. 系统状态",
            "## 标注",
        ):
            assert header in md
        assert f"# UTC 日切复盘报告 — {_DATE} 班次 00:00 UTC" in md
        assert "[2026-08-28T00:00:00+00:00, 2026-08-28T08:00:00+00:00)" in md

    def test_missing_data_renders_not_wired(self):
        md = self._render({c: None for c in cdr.CATEGORIES}, notes=["fills 数据缺失——该节未接线"])
        assert md.count("_无数据（未接线）_") == 5
        assert "- fills 数据缺失——该节未接线" in md

    def test_no_notes_renders_placeholder(self):
        md = self._render({c: [] for c in cdr.CATEGORIES})
        assert "- （无）" in md

    def test_shift_16_window_label_crosses_midnight(self):
        start, end = cdr.shift_window(_DATE, 16)
        md = cdr.render_markdown(
            _DATE,
            16,
            start,
            end,
            {c: [] for c in cdr.CATEGORIES},
            [],
            generated_at=datetime(2026, 8, 29, 0, 5, tzinfo=_TZ),
        )
        assert "班次：16:00–次日 00:00 UTC" in md

    def test_tables_rendered_with_data(self):
        sections = {
            "positions": [_rec(1, symbol="BTC-USDT", side="long", qty="0.5", action="open")],
            "fills": [_rec(2, symbol="BTC-USDT", side="buy", price="30000", qty="0.1", fee="0.6")],
            "funding": [_rec(3, symbol="BTC-USDT", rate="0.0001", payment="0.3")],
            "signals": [_rec(4, symbol="BTC-USDT", signal="long", outcome="hit")],
            "system": [_rec(5, component="gateway", status="ok", message="up")],
        }
        md = self._render(sections)
        assert "| BTC-USDT | 1 | 0.5 | 0 | 0.5 |" in md
        assert "| BTC-USDT | 1 | 0.1 | 0 | 3000 | 0.6 |" in md
        assert "命中率（已验证口径）：100%" in md
        assert "整体状态：**ok**" in md


# ── 7. main 端到端 ──


class TestMainEndToEnd:
    def test_report_written_exit_0(self, tmp_path, capsys):
        data_root = tmp_path / "crypto"
        report_dir = tmp_path / "reports"
        _write_jsonl(data_root, "fills", "20260828", [_fill("2026-08-28T03:00:00+00:00")])
        code = cdr.main(["--date", _DATE, "--shift", "0"], data_root=data_root, report_dir=report_dir)
        assert code == 0
        path = report_dir / f"{_DATE}-crypto-daily-review.md"
        assert path.is_file()
        md = path.read_text(encoding="utf-8")
        assert "本班成交：**1** 笔" in md
        # 其余四品类无数据 → 降级标注
        assert md.count("_无数据（未接线）_") == 4
        out = capsys.readouterr().out
        assert "[标注]" in out
        assert str(path) in out

    def test_default_date_uses_today_utc(self, tmp_path):
        report_dir = tmp_path / "reports"
        code = cdr.main([], data_root=tmp_path / "crypto", report_dir=report_dir, today=date(2026, 8, 28))
        assert code == 0
        assert (report_dir / f"{_DATE}-crypto-daily-review.md").is_file()

    def test_invalid_date_exit_1(self, tmp_path, capsys):
        code = cdr.main(["--date", "2026/08/28"], data_root=tmp_path, report_dir=tmp_path / "r")
        assert code == 1
        assert "格式非法" in capsys.readouterr().out

    def test_all_data_missing_still_exit_0_with_notes(self, tmp_path, capsys):
        code = cdr.main(["--date", _DATE], data_root=tmp_path / "crypto", report_dir=tmp_path / "reports")
        assert code == 0
        out = capsys.readouterr().out
        assert out.count("[标注]") == 5  # 五品类全降级

    def test_idempotent_overwrite(self, tmp_path):
        data_root = tmp_path / "crypto"
        report_dir = tmp_path / "reports"
        assert cdr.main(["--date", _DATE], data_root=data_root, report_dir=report_dir) == 0
        first = (report_dir / f"{_DATE}-crypto-daily-review.md").read_text(encoding="utf-8")
        assert cdr.main(["--date", _DATE], data_root=data_root, report_dir=report_dir) == 0
        second = (report_dir / f"{_DATE}-crypto-daily-review.md").read_text(encoding="utf-8")
        # 重跑覆盖同名报告（生成时间行可能变化，窗口与标题恒定）
        for line_first, line_second in zip(first.splitlines(), second.splitlines()):
            if line_first.startswith("- 生成时间"):
                continue
            assert line_first == line_second

    def test_shift_16_end_to_end_window(self, tmp_path):
        data_root = tmp_path / "crypto"
        _write_jsonl(
            data_root,
            "fills",
            "20260828",
            [_fill("2026-08-28T17:00:00+00:00"), _fill("2026-08-28T10:00:00+00:00")],
        )
        report_dir = tmp_path / "reports"
        assert cdr.main(["--date", _DATE, "--shift", "16"], data_root=data_root, report_dir=report_dir) == 0
        md = (report_dir / f"{_DATE}-crypto-daily-review.md").read_text(encoding="utf-8")
        # 仅 17:00 那笔落入 16 班窗口（10:00 属 8 班）
        assert "本班成交：**1** 笔" in md
