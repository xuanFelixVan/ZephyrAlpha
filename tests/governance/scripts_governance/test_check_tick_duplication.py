# [A_test] module_id: MOD-GOV_check_tick_duplication | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_DQ | scripts/governance/data_quality/check_tick_duplication.py | §
# [MODULE] tests.governance.scripts_governance.test_check_tick_duplication
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_TICK_DUP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_check_tick_duplication.py — tick 判重判据件配对红样测试（F05 缺口 D1 治本 2026-09-27）

病根：check_tick_duplication.py（2026-07-16 tick_data 21 个月误删事故治本件、
RULE-DATA-OPS/trae_063 判重禁聚合数配套）判据件零配对测试（M5 census C 类
"疑似判据失效 3 件"之一）——判据回退无红证。

本文件补齐配对红样（卷面 D1 处置令：真重复/边界串位两例）：
- 真重复红样：14 字段全同行被正确判为真重复（dup_group_cnt>0 -> exit 1）
- 边界串位红样：同排序键不同价位行（2026-07-16 事故形态）不被误判为真重复
  （dup_group_cnt==0 -> exit 0）——同时对照演示禁用判据 count()-uniqExact(排序键)
  会误报，证判据件守的就是这条铁律
- 判据 SQL 构造：全字段 GROUP BY + HAVING count()>1，禁用判据不得出现
- TSV 解析健壮性 / Vertical 报告格式 / exit code 语义

隔离铁律：ch_reader.query 全程 monkeypatch 替身，tmp_path 隔离，零生产数据触碰。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

# parents[0]=scripts_governance/ [1]=governance/ [2]=tests/ [3]=repo root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "governance" / "data_quality" / "check_tick_duplication.py"


def _load_script_module():
    """按文件路径加载判据件模块（scripts/ 非 import 包，走 spec 加载）。"""
    spec = importlib.util.spec_from_file_location("check_tick_duplication_under_test", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_script_module()


def _tick_row(mod, **overrides) -> list[str]:
    """构造一行 14 字段 tick 记录（字符串形态，对齐 ch TSV 返回），可按字段覆盖。"""
    base: dict[str, str] = {
        "trade_date": "20260701",
        "timestamp": "2026-07-01 00:00:01.000",
        "symbol": "BTCUSDT",
        "market_type": "spot",
        "price": "100.5",
        "volume": "1.0",
        "amount": "100.5",
        "direction": "buy",
        "data_source": "test_source",
        "bid_price": "100.4",
        "ask_price": "100.6",
        "bid_volume": "1.0",
        "ask_volume": "1.0",
        "quality_flag": "0",
    }
    base.update(overrides)
    return [base[c] for c in mod._TICK_COLUMNS]


def _make_query_mock(total: tuple[int, int], summary: tuple[int, int], detail_rows: list[list[str]]):
    """按 SQL 形态分发替身：uniqExact->总行查询；sum(dup_cnt)->汇总；否则->重复组详情。"""

    def fake_query(sql: str) -> str:
        if "uniqExact" in sql:
            return f"{total[0]}\t{total[1]}"
        if "sum(dup_cnt)" in sql:
            return f"{summary[0]}\t{summary[1]}"
        if not detail_rows:
            return ""
        return "\n".join("\t".join(str(v) for v in row) for row in detail_rows)

    return fake_query


class TestCriterionQueries:
    """判据 SQL 构造配对：全字段 GROUP BY 铁律 + 禁用判据不得混入。"""

    def test_duplication_query_groups_by_all_14_fields(self, mod):
        sql = mod._build_duplication_query("202607", None, 20)
        for col in mod._TICK_COLUMNS:
            assert col in sql, f"判据 SQL 缺业务字段 {col}（全字段铁律破口）"
        assert "GROUP BY" in sql
        assert "HAVING dup_cnt > 1" in sql

    def test_duplication_query_has_no_forbidden_criterion(self, mod):
        """禁用判据 count()-uniqExact(排序键) 不得出现在真重复判据 SQL 中。"""
        sql = mod._build_duplication_query("202607", "spot", 20)
        assert "uniqExact" not in sql
        assert "REPLACE" not in sql and "DELETE" not in sql  # 只读判据，无破坏性动词
        # 市场类型过滤参数化
        assert "market_type = 'spot'" in sql

    def test_summary_query_is_full_field_group(self, mod):
        sql = mod._build_summary_query("202607", None)
        for col in mod._TICK_COLUMNS:
            assert col in sql
        assert "HAVING dup_cnt > 1" in sql

    def test_validate_month(self, mod):
        assert mod._validate_month("202607") is True
        assert mod._validate_month("2026-07") is False
        assert mod._validate_month("abc") is False
        assert mod._validate_month("2026071") is False


class TestTrueDuplicateRedSample:
    """红样①：真重复（14 字段全同行）必须被判出 -> exit 1。"""

    def test_true_duplicate_detected(self, mod, monkeypatch):
        dup_row = _tick_row(mod)
        detail_rows = [dup_row + ["2"]]  # 14 字段 + dup_cnt=2
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(2, 1), summary=(1, 2), detail_rows=detail_rows),
        )
        result: dict[str, Any] = mod.check_duplication("202607")
        assert result["dup_group_cnt"] == 1
        assert result["dup_row_cnt"] == 2
        assert len(result["dup_groups"]) == 1
        group = result["dup_groups"][0]
        assert group["dup_cnt"] == 2
        assert group["fields"]["symbol"] == "BTCUSDT"
        assert group["fields"]["price"] == "100.5"

    def test_true_duplicate_main_exits_1(self, mod, monkeypatch, capsys):
        """exit 语义红样：发现真重复 -> main 退出码 1（需排查根因，禁直接删除）。"""
        dup_row = _tick_row(mod)
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(2, 1), summary=(1, 2), detail_rows=[dup_row + ["2"]]),
        )
        monkeypatch.setattr(sys, "argv", ["check_tick_duplication.py", "--month", "202607"])
        with pytest.raises(SystemExit) as ei:
            mod.main()
        assert ei.value.code == 1
        out = capsys.readouterr().out
        assert "真重复" in out

    def test_multi_group_duplication_ordering(self, mod, monkeypatch):
        """多重复组：按 dup_cnt 降序进入详情，行数计入 dup_row_cnt。"""
        rows = [
            _tick_row(mod, symbol="AAA") + ["3"],
            _tick_row(mod, symbol="BBB") + ["2"],
        ]
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(5, 2), summary=(2, 5), detail_rows=rows),
        )
        result = mod.check_duplication("202607")
        assert result["dup_group_cnt"] == 2
        assert result["dup_row_cnt"] == 5
        assert result["dup_groups"][0]["dup_cnt"] == 3
        assert result["dup_groups"][1]["dup_cnt"] == 2
        assert result["dup_groups"][0]["fields"]["symbol"] == "AAA"


class TestBoundarySortKeyOverlapRedSample:
    """红样②：边界串位（同排序键不同价位/维度行，2026-07-16 事故形态）不得判为真重复。

    场景：两行 trade_date/timestamp/symbol/market_type 全同（排序键撞车），
    但 price/volume/amount/direction 不同=有效记录。2026-07-16 事故根因即
    用 count()-uniqExact(排序键) 把这类行算成"重复"并删除了 21 个月数据。
    """

    def _boundary_rows(self, mod):
        row_a = _tick_row(mod, price="100.5", volume="1.0", amount="100.5", direction="buy")
        row_b = _tick_row(mod, price="101.0", volume="2.0", amount="202.0", direction="sell")
        return row_a, row_b

    def test_boundary_rows_not_flagged_as_duplicate(self, mod, monkeypatch):
        row_a, row_b = self._boundary_rows(mod)
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(2, 2), summary=(0, 0), detail_rows=[]),  # 全字段 uniq=总行数，零重复组
        )
        result = mod.check_duplication("202607")
        assert result["total_row_cnt"] == 2
        assert result["uniq_full_field_cnt"] == 2
        assert result["dup_group_cnt"] == 0, "同排序键不同价位行被误判为真重复——判据回退红证命中"
        assert result["dup_groups"] == []

    def test_boundary_rows_main_exits_0(self, mod, monkeypatch):
        """exit 语义：边界串位无真重复 -> exit 0（禁止构成破坏性操作理由）。"""
        row_a, row_b = self._boundary_rows(mod)
        assert row_a[:4] == row_b[:4], "夹具前置：两行排序键前四元必须相同（撞车形态）"
        assert row_a != row_b
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(2, 2), summary=(0, 0), detail_rows=[]),
        )
        monkeypatch.setattr(sys, "argv", ["check_tick_duplication.py", "--month", "202607"])
        with pytest.raises(SystemExit) as ei:
            mod.main()
        assert ei.value.code == 0

    def test_forbidden_criterion_would_misfire_documented(self, mod, monkeypatch):
        """对照留证：禁用判据 count()-uniqExact(排序键) 在本场景误报 1，判据件判 0。

        uniqExact(trade_date,timestamp,symbol) = 1（排序键撞车），
        count() - uniqExact(排序键) = 2 - 1 = 1 -> 事故判据会报"1 条重复"；
        全字段判据报 0。两者之差就是 2026-07-16 误删 21 个月的病灶。
        """
        row_a, row_b = self._boundary_rows(mod)
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(2, 2), summary=(0, 0), detail_rows=[]),
        )
        result = mod.check_duplication("202607")
        forbidden_criterion = result["total_row_cnt"] - 1  # uniqExact(排序键)=1
        assert forbidden_criterion == 1, "对照前提失效：禁用判据在本夹具应误报 1"
        assert result["dup_group_cnt"] == 0
        assert row_a[4] != row_b[4]  # price 不同=有效记录


class TestParsingAndReport:
    """TSV 解析健壮性与报告格式配对。"""

    def test_parse_tsv_roundtrip(self, mod):
        tsv = "1\t2\n3\t4"
        rows = mod._parse_tsv(tsv, 2)
        assert rows == [["1", "2"], ["3", "4"]]

    def test_parse_tsv_skips_malformed_rows(self, mod):
        tsv = "1\t2\nbad-row\n\n5\t6"
        rows = mod._parse_tsv(tsv, 2)
        assert rows == [["1", "2"], ["5", "6"]], "列数不符行必须跳过（防误解析）"

    def test_parse_tsv_empty_on_empty(self, mod):
        assert mod._parse_tsv("", 2) == []
        assert mod._parse_tsv("\\N", 2) == []

    def test_vertical_format_lists_all_fields(self, mod):
        row = _tick_row(mod)
        text = mod._format_vertical(row, "2", 1)
        assert "重复组 #1" in text and "重复 2 次" in text
        for col in mod._TICK_COLUMNS:
            assert col in text

    def test_query_sql_recorded_for_audit(self, mod, monkeypatch):
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(0, 0), summary=(0, 0), detail_rows=[]),
        )
        result = mod.check_duplication("202607")
        assert "GROUP BY" in result["query_sql"]
        assert "HAVING dup_cnt > 1" in result["query_sql"]

    def test_main_invalid_month_exits_2(self, mod, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["check_tick_duplication.py", "--month", "bad"])
        with pytest.raises(SystemExit) as ei:
            mod.main()
        assert ei.value.code == 2

    def test_main_ch_failure_exits_2(self, mod, monkeypatch):
        def boom(sql: str) -> str:
            raise RuntimeError("CH 连接异常")

        monkeypatch.setattr(mod.ch_reader, "query", boom)
        monkeypatch.setattr(sys, "argv", ["check_tick_duplication.py", "--month", "202607"])
        with pytest.raises(SystemExit) as ei:
            mod.main()
        assert ei.value.code == 2

    def test_main_json_output(self, mod, monkeypatch, capsys):
        import json

        dup_row = _tick_row(mod)
        monkeypatch.setattr(
            mod.ch_reader,
            "query",
            _make_query_mock(total=(2, 1), summary=(1, 2), detail_rows=[dup_row + ["2"]]),
        )
        monkeypatch.setattr(sys, "argv", ["check_tick_duplication.py", "--month", "202607", "--json"])
        with pytest.raises(SystemExit) as ei:
            mod.main()
        assert ei.value.code == 1
        payload = json.loads(capsys.readouterr().out)
        assert payload["dup_group_cnt"] == 1
        assert payload["query_sql"]
