# [TTL] permanent
# [MODULE] tests.data.data.data.test_regind001_audit_status_alignment
# [DOMAIN] D_DATA
"""REG-IND-001 覆盖审计尺与 T1 停算立法的对齐钉（统筹裁定④，2026-10-12 夜）。

零 CH：ch_reader.query 全程替换为假取数器，只验判据分派本身。
三条钉（缺一即本次修法不成立）：
  1) 停算列全 NULL 而 在产列全有值 ⇒ rc=0，且 12 个停算列出现在"披露面"而非"全 0 列"；
  2) 摘掉 status 读径（helper 返回空集＝旧形"全列判罚"）⇒ 同一份数据必红 rc=2
     ——证明第 1 条的绿是豁免生效，不是尺失灵（反向对照，禁只跑正向）；
  3) 在产列里真有整列空 ⇒ 仍 rc=2（豁免不得吞掉真缺口）。
"""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]  # tests/data/data/data/<file> → 仓根
SCRIPT = REPO / "scripts" / "data" / "audit_technical_indicator_coverage.py"
# 实测形状：ch_reader 的 TCP 通道把 CH NULL 渲染成字面 "None"（pandas 默认 NA 表含它）；
# 假取数器必须同形，否则测的是"\\N 不被识别"这种尺自己的病，不是被测判据。
NULL_CELL = "None"


def _load_audit(monkeypatch):
    """按文件路径载入审计件（scripts 不在包内，import 名不可用）。"""
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "src"))
    spec = importlib.util.spec_from_file_location("audit_ti_coverage_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fake_query_factory(state: dict, monkeypatch, *, null_retired: bool = True, null_one_active: str | None = None):
    """假取数器：按 SQL 里的列清单造 total 行 TSV；停算列置 NULL，可选把某个在产列也置 NULL。"""
    from zephyr.data import ch_reader

    def fake_query(sql: str, timeout: int = 600) -> str:
        cols = sql.split("SELECT", 1)[1].split("FROM", 1)[0].strip().split(", ")
        state["batches"] = state.get("batches", 0) + 1
        state["cols_seen"] = state.get("cols_seen", []) + cols
        lines = []
        for _ in range(state["total"]):
            cells = []
            for c in cols:
                is_null = (null_retired and c in state["retired"]) or (
                    null_one_active is not None and c == null_one_active
                )
                cells.append(NULL_CELL if is_null else "1.0")
            lines.append("\t".join(cells))
        return "\n".join(lines) + "\n"

    monkeypatch.setattr(ch_reader, "query", fake_query)
    return fake_query


def _prepare(monkeypatch) -> dict:
    mod = _load_audit(monkeypatch)
    from zephyr.factor.technical_indicators import autodiscover_technical_indicators
    from zephyr.factor.technical_indicators.indicator_base import TechnicalIndicatorRegistry

    autodiscover_technical_indicators()
    all_cols = sorted(TechnicalIndicatorRegistry.list_output_columns())
    retired = set(mod._load_retired_indicator_outputs())
    state = {"total": 21, "retired": retired, "all_cols": all_cols}
    # 停算面必须非空且含本次事故列，否则这份数据造不出"豁免生效"的场景
    assert retired, "REG-IND-001 册停算面为空，测试前提不成立"
    assert {"squeeze_on", "wad", "chop_14"} <= retired
    return mod, state


def test_retired_columns_are_disclosed_not_judged(monkeypatch):
    mod, state = _prepare(monkeypatch)
    _fake_query_factory(state, monkeypatch)
    monkeypatch.setattr(
        sys, "argv", ["x", "--symbol", "600519", "--period", "daily", "--start", "2026-08-01", "--end", "2026-08-31"]
    )
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    rc = mod.main()
    out = buf.getvalue()
    assert rc == 0, out
    assert "AUDIT PASS" in out
    assert "停算面披露" in out and "squeeze_on" in out
    assert "全 0 列（0）" in out  # 停算列没被判成缺陷
    assert state["batches"] > 0  # 假取数器真被调用（不是零命中空过）


def test_removing_status_readpath_makes_the_same_data_red(monkeypatch):
    """反向对照：把 status 读径摘掉（helper 返空集）＝旧形"全列判罚"，同数据必红。"""
    mod, state = _prepare(monkeypatch)
    _fake_query_factory(state, monkeypatch)
    monkeypatch.setattr(mod, "_load_retired_indicator_outputs", lambda: frozenset())
    monkeypatch.setattr(
        sys, "argv", ["x", "--symbol", "600519", "--period", "daily", "--start", "2026-08-01", "--end", "2026-08-31"]
    )
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    rc = mod.main()
    out = buf.getvalue()
    assert rc == 2, out
    assert "AUDIT FAIL" in out and "squeeze_on" in out


def test_active_column_still_all_null_still_fails(monkeypatch):
    """豁免不得吞掉真缺口：在产列整列空仍判 rc=2。"""
    mod, state = _prepare(monkeypatch)
    judged = [c for c in state["all_cols"] if c not in state["retired"]]
    hole = judged[0]
    _fake_query_factory(state, monkeypatch, null_one_active=hole)
    monkeypatch.setattr(
        sys, "argv", ["x", "--symbol", "600519", "--period", "daily", "--start", "2026-08-01", "--end", "2026-08-31"]
    )
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    rc = mod.main()
    out = buf.getvalue()
    assert rc == 2, out
    assert hole in out


def test_unreadable_registry_yaml_is_not_false_green(monkeypatch):
    """册读不到＝尺不可信，必须非零退出，既不得全列判罚也不得全列豁免。"""
    mod, state = _prepare(monkeypatch)
    _fake_query_factory(state, monkeypatch)
    monkeypatch.setattr(mod, "_TI_REGISTRY_YAML", Path("/nonexistent/technical_indicator_registry.yaml"))
    monkeypatch.setattr(
        sys, "argv", ["x", "--symbol", "600519", "--period", "daily", "--start", "2026-08-01", "--end", "2026-08-31"]
    )
    buf = io.StringIO()
    monkeypatch.setattr(sys, "stdout", buf)
    rc = mod.main()
    assert rc == 3
    assert "审计不可信" in buf.getvalue()
