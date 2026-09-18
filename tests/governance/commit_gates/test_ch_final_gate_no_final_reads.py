# [A_test] module_id: MOD-GOV_ch_final_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | §0.1
# [MODULE] tests.governance.commit_gates.test_ch_final_gate_no_final_reads
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_ch_final_gate_no_final_reads.py — CH-FINAL-GATE 判据②（无 FINAL 直连读）单测

权威依据：ch_final_gate.py（_scan_missing_final_reads / _check_missing_final）

立测背景（红队车道 st-ff-pit2-20260918，2026-09-18 实证）：
  原 CH-FINAL-GATE 只匹配 `ch_writer.query(`，而经
  `DatabaseService.get_clickhouse_conn().execute()` 直连的 SQL 完全不过门禁 ⇒
  生产读路径可在 ReplacingMergeTree 后台 merge 完成前读到未去重行
  （实测 2026-09-17 当日 kline_daily 无 FINAL 6,471 行 / 带 FINAL 5,568 行）。
  本 gate 此前**零测试覆盖**（全仓 grep `ch_final_gate` 在 tests/ 下 0 命中），
  故"门禁无牙"长期不可见——本文件是把判据钉住的第一批测试。

测试组：
- TestEngineResolution: 真接 CH 解析引擎（不 mock 防线自身；CH 不可达则整组 skip 并出声）
- TestNoFinalDetection: 无 FINAL 直连读 → 红；带 FINAL / 走 ch_reader / inject_final → 白
- TestOwnDiffScope: 存量行不参与判定，新增行参与（防 70 处存量连坐）
- TestExemptions: docstring 示例 / system 库 / noqa 逃生 / 非 Replacing 表
- TestDegradationOutLoud: 引擎不可解析时不静默放行，必须记 WARNING（防"被兜底吞掉的加固"）
- TestGateSpecWiring: GateSpec 字段 + 经 check 闭包的端到端红

判据自证非空转：每条"白"都配一条只差关键字的"红"，避免扫描器静默失效造成假绿。
"""

from __future__ import annotations

import ast
import logging
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.ch_final_gate import (  # noqa: E402
    _build_containers,
    _check_missing_final,
    _reader_covered,
    _resolve_engine,
    _scan_missing_final_reads,
    _scan_violations,
    make_ch_final_gate,
)

REPLACING_TABLE = "c1_market.kline_daily"
NO_FINAL_SQL_FILE = '''
"""行情读取。"""


def fetch_close(day: str) -> list:
    sql = "SELECT symbol, close FROM c1_market.kline_daily WHERE trade_date = %(d)s"
    conn = get_conn()
    return conn.execute(sql, {"d": day})
'''
WITH_FINAL_SQL_FILE = NO_FINAL_SQL_FILE.replace("kline_daily WHERE", "kline_daily FINAL WHERE")
VIA_CH_READER_FILE = '''
"""行情读取（走统一读取层）。"""
from zephyr.data import ch_reader


def fetch_close(day: str) -> str:
    sql = "SELECT symbol, close FROM c1_market.kline_daily WHERE trade_date = '%s'" % day
    return ch_reader.query(sql)
'''
VIA_INJECT_FINAL_FILE = '''
"""行情读取（自行注入）。"""
from zephyr.data.ch_reader import inject_final


def build(day: str) -> str:
    sql = "SELECT symbol FROM c1_market.kline_daily WHERE trade_date = '%s'" % day
    return inject_final(sql)
'''

_ENGINES = {REPLACING_TABLE: "ReplacingMergeTree", "c1_market.plain_mt": "MergeTree"}


@pytest.fixture
def fake_engine(monkeypatch):
    """把引擎解析换成在册字典——函数判定面不得依赖 CH 在线（确定性要求）。"""
    monkeypatch.setattr(
        "zephyr.gov_enforcement.commit_gates.ch_final_gate._resolve_engine",
        lambda full: _ENGINES.get(full, ""),
    )
    return _ENGINES


def _scan(src: str, added_lines: set[int] | None = None, noqa_lines: set[int] | None = None):
    """判据②扫描入口 + **测试源合法性自检**（结构性防空转）。

    判据②对 SyntaxError 是 fail-open（返回 `[], []`），所以**不合法的测试源会让该用例的
    所有断言恒真**。本次复测实录：前手 3 个用例把多行隐式拼接写成无括号形式（非法 Python），
    `test_python_import_prose_is_not_mistaken_for_sql` 长期假绿、我新加的 2 个截断钉桩用例
    第一版同样中招（变异 m2b 复原截断缺陷时它们**不转红**才暴露）。
    故在入口统一断言源可解析——需要测 SyntaxError 分支的用例请直连 `_scan_missing_final_reads`。
    """
    assert _parses(src), "测试源不是合法 Python——判据②会 fail-open，用例将恒真（假绿）"
    return _scan_missing_final_reads(src, "demo/x.py", added_lines, noqa_lines or set())


def _parses(src: str) -> bool:
    """测试源自检：判据②对 SyntaxError 是 fail-open（返回空），因此**不合法的测试源
    会让任何断言恒真**。多行隐式拼接必须带括号，否则用例是假绿（本次复测实录 3 例）。"""
    try:
        ast.parse(src)
    except SyntaxError:
        return False
    return True


class TestEngineResolution:
    """不 mock 防线自身：真接 CH 验证"哪些表需要 FINAL"这条判据的输入面是活的。"""

    def test_replacing_table_engine_resolves(self):
        try:
            engine = _resolve_engine(REPLACING_TABLE)
        except Exception as exc:  # noqa: BLE001 — pragma: no cover - CH 不可达（任何驱动层异常都按不可达处理）
            pytest.skip(f"CH 不可达，引擎面无法真验：{exc}")
        if not engine:
            pytest.skip("CH 不可达（get_table_engine 返回空串），引擎面无法真验")
        assert "Replacing" in engine

    def test_nonexistent_table_resolves_to_empty_not_raise(self):
        # 不存在的表 ⇒ 空串（判据据此出声降级，而非抛异常打死 gateway）
        assert _resolve_engine("c1_market.__no_such_table_zz__") == ""

    def test_system_db_engine_is_not_replacing(self):
        engine = _resolve_engine("system.tables")
        assert "Replacing" not in engine


class TestNoFinalDetection:
    def test_direct_execute_without_final_is_red(self, fake_engine):
        violations, unresolved = _scan(NO_FINAL_SQL_FILE)
        assert violations == [f"demo/x.py:L6 (FROM {REPLACING_TABLE} 无 FINAL 且未走 ch_reader)"]
        assert unresolved == []

    def test_with_final_is_white(self, fake_engine):
        assert _scan(WITH_FINAL_SQL_FILE)[0] == []

    def test_via_ch_reader_is_white(self, fake_engine):
        assert _scan(VIA_CH_READER_FILE)[0] == []

    def test_via_inject_final_is_white(self, fake_engine):
        assert _scan(VIA_INJECT_FINAL_FILE)[0] == []

    def test_non_replacing_table_is_white(self, fake_engine):
        src = NO_FINAL_SQL_FILE.replace(REPLACING_TABLE, "c1_market.plain_mt")
        assert _scan(src)[0] == []

    def test_every_white_case_has_a_red_twin(self, fake_engine):
        """防空转：白判据逐个去掉 FINAL/去掉注入载体后必须转红。"""
        assert _scan(WITH_FINAL_SQL_FILE)[0] == []
        assert _scan(NO_FINAL_SQL_FILE)[0] != []
        assert _scan(VIA_CH_READER_FILE)[0] == []
        bare = VIA_CH_READER_FILE.replace("ch_reader.query(sql)", "conn.execute(sql)")
        assert _scan(bare)[0] != []


class TestOwnDiffScope:
    def test_legacy_line_not_judged_when_not_added(self, fake_engine):
        """存量行（未进本次 added 集）不判——防 70 处存量连坐无辜提交人。"""
        violations, _ = _scan(NO_FINAL_SQL_FILE, added_lines={2, 3})
        assert violations == []

    def test_added_line_is_judged(self, fake_engine):
        violations, _ = _scan(NO_FINAL_SQL_FILE, added_lines={6})
        assert len(violations) == 1

    def test_multi_line_implicit_concat_is_judged_as_one_unit(self, fake_engine):
        """隐式拼接的多行 SQL 在 AST 里是**一个** Constant（lineno=首行）——
        整体判 FINAL，不按片段拆判（否则"FINAL 写在下一片段"的正当写法会被假红）。"""
        src = (
            "SQL_X = (\n"
            '    "SELECT a "\n'
            f'    "FROM {REPLACING_TABLE} "\n'
            '    "WHERE b = 1"\n'
            ")\n"
        )
        assert _scan(src, added_lines={4})[0] != []  # 触及常量跨度即判
        assert _scan(src, added_lines={2})[0] != []  # 常量起点=第 2 行，同属该跨度
        assert _scan(src, added_lines={30})[0] == []  # 与本次新增无关 ⇒ 不判
        with_final = src.replace(REPLACING_TABLE, f"{REPLACING_TABLE} FINAL")
        assert _scan(with_final, added_lines={2, 3, 4})[0] == []

    def test_empty_added_set_disables_the_criterion(self, fake_engine):
        assert _scan(NO_FINAL_SQL_FILE, added_lines=set())[0] == []


class TestExemptions:
    def test_docstring_example_is_not_a_violation(self, fake_engine):
        src = f'"""示例：SELECT * FROM {REPLACING_TABLE} WHERE ..."""' "\n"
        assert _scan(src)[0] == []

    def test_system_database_is_skipped(self, fake_engine):
        src = 'def f():\n    return "SELECT name FROM system.settings WHERE 1"\n'
        violations, unresolved = _scan(src)
        assert violations == [] and unresolved == []

    def test_noqa_escape_hatch_works_per_line(self, fake_engine):
        assert _scan(NO_FINAL_SQL_FILE)[0] != []
        assert _scan(NO_FINAL_SQL_FILE, noqa_lines={6})[0] == []

    def test_noqa_on_other_line_does_not_exempt(self, fake_engine):
        assert _scan(NO_FINAL_SQL_FILE, noqa_lines={3})[0] != []

    def test_syntax_error_fails_open_without_raising(self, fake_engine):
        """直连 `_scan_missing_final_reads`——`_scan` 入口已禁止不合法测试源（防空转）。"""
        assert _scan_missing_final_reads("def broken(:\n    pass\n", "demo/x.py", None, set()) == ([], [])


class TestDegradationOutLoud:
    """引擎不可解析（CH 不可达）⇒ 判据降级，但必须出声——不能静默等效于放行。"""

    def test_unresolved_engine_is_reported_and_warned(self, monkeypatch, caplog, tmp_path):
        monkeypatch.setattr(
            "zephyr.gov_enforcement.commit_gates.ch_final_gate._resolve_engine", lambda _t: ""
        )
        victim = tmp_path / "bad.py"
        victim.write_text(NO_FINAL_SQL_FILE, encoding="utf-8")
        violations, unresolved = _scan(NO_FINAL_SQL_FILE)
        assert violations == []
        assert unresolved == [REPLACING_TABLE]
        with caplog.at_level(logging.WARNING):
            assert _check_missing_final(MagicMock(), "demo/bad.py", str(victim), None) == []
        assert "判据②降级" in caplog.text
        assert REPLACING_TABLE in caplog.text

    def test_resolved_engine_produces_no_degradation_warning(self, fake_engine, caplog, tmp_path):
        clean = tmp_path / "ok.py"
        clean.write_text(WITH_FINAL_SQL_FILE, encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            found = _check_missing_final(MagicMock(), "demo/ok.py", str(clean), None)
        assert found == []
        assert "判据②降级" not in caplog.text

    def test_python_import_prose_is_not_mistaken_for_sql(self, fake_engine):
        """`from zephyr.data.ch_reader import x` 里的小写 from + 点号路径不得被判成表引用
        （实测第一版判据就在此假红，_SQL_SHAPE 与 db.tbl 后不接点号两道闸即为此设）。

        ★ 前手把本用例写成无括号多行拼接（非法 Python）⇒ 一直走的是 SyntaxError
        fail-open 分支、断言恒真。补括号后被验的才是真对象（`_SQL_SHAPE` 那道闸）。
        """
        src = (
            "TEMPLATE = (\n"
            "    'generated body:\\n'\n"
            "    'from zephyr.data.ch_reader import inject_final\\n'\n"
            "    'from zephyr.data import ch_reader\\n'\n"
            ")\n"
        )
        violations, unresolved = _scan(src)
        assert violations == [] and unresolved == []

    def test_sql_shaped_constant_with_dotted_python_path_is_not_truncated(self):
        r"""★ 截断缺陷钉桩（st-ff-gov2 复测，2026-09-18 实测 WARNING 的根因）。

        与上条的分工：本常量**确实含 SELECT** ⇒ 过 `_SQL_SHAPE` 闸、真进
        `_DB_QUALIFIED_FROM`。旧先行 `(?!\s*\.)` 会被 `\w+` **回溯**绕过——
        `zephyr.data.ch_reader` 截断成假表名 `zephyr.dat`（后接 `a`，非点号 ⇒ 先行通过），
        再被送去查引擎 ⇒ 提交期真出过
        `CH-FINAL-GATE 判据②降级：…['zephyr.dat','zephyr.data']`。
        "不可判定"被当成"这轮不判"，与 R-055b/F-2"缺位维默认稳定"同病（#273）。
        断言 unresolved==[] ——旧写法下必红（截断名经真 `_resolve_engine` 得空串）。
        本用例不 mock 防线自身（走真 CH 面，口径见 TestEngineResolution）。
        """
        src = (
            'TPL = (\n'
            '    "SELECT a "\n'
            '    "FROM zephyr.data.ch_reader "\n'
            '    "WHERE b = 1\\n"\n'
            ')\n'
        )
        violations, unresolved = _scan(src)
        assert violations == []
        assert unresolved == [], f"点号路径被截断成假表名: {unresolved}"

    def test_python_import_clause_after_from_is_not_a_table(self, fake_engine):
        """两段点号名与 db.tbl 形状同构，正则层面不可分，靠 `import` 子句辨伪
        （真源：scripts/ch/apply_market_tables_ddl.py:1190 的模板常量被当成表 `zephyr.data`，
        与 `zephyr.dat` 一起构成那条实测降级 WARNING 的 2 个不可解析名）。"""
        src = (
            'TPL = (\n'
            '    "import x\\n"\n'
            '    "from zephyr.data import ch_reader, ch_writer\\n"\n'
            '    "SELECT 1\\n"\n'
            ')\n'
        )
        violations, unresolved = _scan(src)
        assert violations == [] and unresolved == []

    def test_trailing_period_does_not_split_a_real_table_name(self, fake_engine):
        """散文句末点号同样触发回溯截断（`c1_market.kline_daily.`→`c1_market.kline_dai`）。"""
        src = f'STMT = "SELECT a FROM {REPLACING_TABLE}."\n'
        violations, unresolved = _scan(src)
        assert violations == [] and unresolved == []

    def test_positive_control_real_missing_final_still_red_after_lookahead_fix(self, fake_engine):
        """防"过度收紧把判据改成永不匹配"：表名后接换行/空白的真违规必须仍红。"""
        src = f'STMT = "SELECT a FROM {REPLACING_TABLE}\\n"\n'
        violations, unresolved = _scan(src)
        assert len(violations) == 1 and unresolved == []

    def test_unresolvable_table_is_out_loud_without_mocks(self, caplog, tmp_path):
        """不 mock 防线自身：真取一个不存在的表名，门必须出声且与"已豁免"可区分。"""
        src = 'STMT = "SELECT a FROM c1_market.__no_such_table_zz__ WHERE 1"\n'
        with caplog.at_level(logging.WARNING):
            violations, unresolved = _scan(src)
        assert violations == [], "不可解析不应被当成违规（那是 fail-closed 打死通道）"
        assert unresolved == ["c1_market.__no_such_table_zz__"]
        victim = tmp_path / "unresolved.py"
        victim.write_text(src, encoding="utf-8")
        with caplog.at_level(logging.WARNING):
            assert _check_missing_final(MagicMock(), "demo/u.py", str(victim), None) == []
        assert "判据②降级" in caplog.text


class TestContainerHelpers:
    def test_innermost_container_decides_reader_coverage(self):
        tree = ast.parse(VIA_CH_READER_FILE)
        containers = _build_containers(tree)
        # 函数体内有 ch_reader.query → 该行被覆盖；模块级第 1 行不在任何函数里
        assert _reader_covered(containers, 8) is True
        assert _reader_covered(containers, 1) is False

    def test_uncovered_container_returns_false(self):
        containers = _build_containers(ast.parse(NO_FINAL_SQL_FILE))
        assert _reader_covered(containers, 6) is False


class TestGateSpecWiring:
    def test_gate_spec_fields(self):
        spec = make_ch_final_gate()
        assert spec.gate_id == "CH-FINAL-GATE"
        assert spec.priority == 37

    def test_end_to_end_red_on_staged_direct_read(self, fake_engine, tmp_path):
        """经 _scan_violations 全链路：新增文件里的无 FINAL 直连读必须进违规清单。"""
        victim = tmp_path / "bad_reader.py"
        victim.write_text(NO_FINAL_SQL_FILE, encoding="utf-8")
        gateway = MagicMock()
        gateway.run_git.return_value = SimpleNamespace(returncode=0, stdout="")
        found = _scan_violations(gateway, [str(victim)], {str(victim)}, str(tmp_path))
        assert len(found) == 1 and "无 FINAL" in found[0]

    def test_end_to_end_white_on_staged_final_read(self, fake_engine, tmp_path):
        ok = tmp_path / "good_reader.py"
        ok.write_text(WITH_FINAL_SQL_FILE, encoding="utf-8")
        gateway = MagicMock()
        gateway.run_git.return_value = SimpleNamespace(returncode=0, stdout="")
        assert _scan_violations(gateway, [str(ok)], {str(ok)}, str(tmp_path)) == []
