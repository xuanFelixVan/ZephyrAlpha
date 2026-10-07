# [MODULE] tests.gov.governance.scripts_governance.test_check_tick_duplication
# [DOMAIN] D_GOV_CODE_QUALITY
# [TTL] permanent

"""test_check_tick_duplication.py — tick 判重判据件配对红样测试（DSC-06 / IN1-28 自红，2026-10-07）。

病根（IN1-28）：uniqExact(14 平铺列) 撞 CH「Nullable 聚合参数 ≤8」上限（Code 42 恒抛），
被 ch_reader.query 空串契约吞成 0 行 0 重复 = 半假绿；且 exit 码只看 dup 腿。

本文件锁四件事（2026-10-07 DSC-06 批修复面）：
- ①tuple 单参包装：_SQL_TOTAL_ROW 必含 uniqExact(tuple(...))；真 CH 只读探针
  （WHERE 0=1 零数据移动，仅触发聚合参数个数分析）证明 tuple 形式不抛 Code 42（CH 不可达 skip）
- ②fail-visible：任一腿查询失败 exit 2 且 stderr 印明哪条腿；三腿真空 0 行 exit 0——
  严格通道 query_rows（失败 raise / 真空 []）把两态结构分开，禁吞成空表假绿
- ③src 路径推算：_SRC_DIR 由 __file__ 推算（worktree 内跑加载被审仓自己的 src），禁硬编码仓根
- exit 语义：真重复 exit 1（dup 腿）

隔离铁律：ch_reader 全程 monkeypatch 替身（脚本模块命名空间打桩），零生产数据触碰；
唯一例外=CH 探针测试（只读 WHERE 0=1，不可达即 skip）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "governance" / "data_quality" / "check_tick_duplication.py"


def _load_script_module() -> ModuleType:
    """按文件路径装载被测脚本（scripts/ 不在包路径内，importlib 直载）。"""
    spec = importlib.util.spec_from_file_location("_check_tick_duplication_under_test", _SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def mod() -> ModuleType:
    return _load_script_module()


def _run_main(mod: ModuleType, monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    monkeypatch.setattr(sys, "argv", ["check_tick_duplication.py", *argv])
    with pytest.raises(SystemExit) as ei:
        mod.main()
    return int(ei.value.code or 0)


# ── ①tuple 单参包装 ──────────────────────────────────────────────────────
class TestTupleWrapSql:
    def test_total_row_sql_wraps_tuple(self, mod: ModuleType) -> None:
        # 14 平铺列直塞 uniqExact 撞 CH Nullable 聚合参数 ≤8 上限；必须 tuple(...) 单参包装
        assert "uniqExact(tuple(" in mod._SQL_TOTAL_ROW

    def test_built_sql_keeps_all_14_columns_inside_tuple(self, mod: ModuleType) -> None:
        sql = mod._build_total_row_query("202609", None)
        assert "uniqExact(tuple(trade_date, timestamp" in sql
        for col in mod._TICK_COLUMNS:
            assert col in sql

    def test_nullable_tuple_uniqexact_does_not_raise_on_real_ch(self, mod: ModuleType) -> None:
        # 真 CH 只读探针：WHERE 0=1 零数据移动，仅触发聚合参数个数分析——
        # 旧平铺写法在此恒抛 Code 42（参数 ≤8 上限是分析期检查），tuple 包装后必须通过。
        sql = (
            "SELECT uniqExact(tuple(trade_date, timestamp, symbol, market_type, price, volume, "
            "amount, direction, data_source, bid_price, ask_price, bid_volume, ask_volume, quality_flag)) "
            "FROM tick_data WHERE 0=1"
        )
        try:
            rows = mod.ch_reader.query_rows(sql)
        except Exception as e:  # noqa: BLE001 — CH 不可达/表缺席环境跳过（CI/无网）
            pytest.skip(f"CH 不可达，跳过真库探针: {e}")
        assert len(rows) == 1  # 聚合恒返 1 行


# ── ②fail-visible：查询失败 exit 2 印腿名 / 真空 0 行 exit 0 ─────────────
def _install_query_rows(mod: ModuleType, monkeypatch: pytest.MonkeyPatch, behavior) -> None:
    monkeypatch.setattr(mod.ch_reader, "query_rows", behavior)


class TestFailVisible:
    @pytest.mark.parametrize(
        "leg_marker,leg_label",
        [
            ("uniqExact", "total_row（该月总行数/全字段唯一行数）"),
            (
                "dup_group_cnt",
                "summary（重复组汇总）",
            ),  # summary SQL 以 SELECT count() AS dup_group_cnt 开头（子查询含 HAVING，禁作 marker）
            ("ORDER BY", "detail（重复组详情）"),  # ORDER BY dup_cnt DESC 为 detail 腿独有
        ],
    )
    def test_leg_failure_exits_2_and_names_leg(self, mod, monkeypatch, capsys, leg_marker, leg_label):
        from zephyr.data.ch_reader import ClickHouseQueryError

        def boom(sql, *a, **kw):
            if leg_marker in sql:
                raise ClickHouseQueryError(sql, [("code", "42: too many arguments")])
            return []

        _install_query_rows(mod, monkeypatch, boom)
        code = _run_main(mod, monkeypatch, "--month", "202609")
        assert code == 2
        err = capsys.readouterr().err
        assert "判重查询腿失败" in err
        assert leg_label.split("（")[0] in err  # 腿名印明（total_row/summary/detail）

    def test_genuine_zero_rows_exits_0_not_2(self, mod, monkeypatch, capsys):
        # ''（查询失败）与『0 行』必须可分：三腿真空 → exit 0（非 2）
        def fake(sql, *a, **kw):
            if "uniqExact" in sql:
                return [("0", "0")]  # 聚合腿恒返 1 行（全月 0 行的合法读数）
            return []  # summary/detail 真空 = 0 重复

        _install_query_rows(mod, monkeypatch, fake)
        code = _run_main(mod, monkeypatch, "--month", "202609")
        assert code == 0
        assert "未发现真重复行" in capsys.readouterr().out

    def test_true_duplicate_exits_1(self, mod, monkeypatch, capsys):
        row = tuple(str(i) for i in range(14)) + ("2",)  # 14 字段值 + dup_cnt

        def fake(sql, *a, **kw):
            if "uniqExact" in sql:
                return [("100", "99")]
            if "dup_group_cnt" in sql:
                return [("1", "2")]
            return [row]

        _install_query_rows(mod, monkeypatch, fake)
        code = _run_main(mod, monkeypatch, "--month", "202609")
        assert code == 1
        assert "发现 1 组真重复行" in capsys.readouterr().out

    def test_invalid_month_exits_2(self, mod, monkeypatch):
        assert _run_main(mod, monkeypatch, "--month", "2026-09") == 2


# ── ③src 路径推算（禁硬编码仓根） ─────────────────────────────────────────
class TestSrcPathDerivation:
    def test_src_dir_derived_from_file_location(self, mod: ModuleType) -> None:
        assert Path(mod._SRC_DIR).resolve() == (_SCRIPT_PATH.resolve().parents[3] / "src").resolve()

    def test_no_hardcoded_repo_root_in_source(self) -> None:
        text = _SCRIPT_PATH.read_text(encoding="utf-8")
        # 回归红样：硬编码仓根赋值禁再入（注释里引用病史字面量不算）
        assert '_SRC_DIR = r"d:' not in text
