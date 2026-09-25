# [A_test] module_id: zephyr.ai_layer.redline.drop_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_drop_gate
# [MODULE] tests.ai_layer.redline.test_drop_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; zephyr.ai_layer.redline.drop_gate
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/ai_layer/redline/test_drop_gate.py
# [MATURITY] testing
# [INVARIANTS] 验收标准（DESIGN 红蓝 R1-F4）：对禁删清单样例路径的 DROP 语句被阻断；
#              审计经 project_root=tmp_path 隔离；纯函数核 _scan 优先直测
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_drop_gate.py — S3 DROP-GATE 单测（禁删样例路径 DROP 阻断/逃生标记/fail-open）。"""

from __future__ import annotations

import json
from pathlib import Path

from zephyr.ai_layer.redline.drop_gate import (
    ALLOW_MARKER_RE,
    make_drop_gate,
    scan_drop_lines,
)

FORBIDDEN_TABLE = "c1_backtest.sim_trade_log"  # DESIGN §2 档 A 禁删点名件（事件溯源源）
DROP_SQL = f"DROP TABLE {FORBIDDEN_TABLE};"


def test_drop_on_no_delete_sample_path_blocked(tmp_path: Path, fake_gateway_factory):
    """验收主样例：对禁删清单样例路径的 DROP 语句被阻断。"""
    gateway = fake_gateway_factory(
        staged={"scripts/migration/nuke.py": f'SQL = "{DROP_SQL}"\n'}
    )
    passed, detail = make_drop_gate().check(
        gateway, ["scripts/migration/nuke.py"], session_id="s1"
    )
    assert passed is False
    assert "DROP TABLE" in detail and FORBIDDEN_TABLE in detail
    audit = tmp_path / ".runtime/gate_audit/obj_s_drop_gate.jsonl"
    record = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert record["action"] == "block" and record["rule_id"] == "NL-6"


def test_variants_truncate_drop_column_drop_database_case_insensitive():
    assert len(scan_drop_lines("TRUNCATE TABLE t1")) == 1
    assert len(scan_drop_lines("truncate t1")) == 1
    assert len(scan_drop_lines("ALTER TABLE t DROP COLUMN c;")) == 1
    assert len(scan_drop_lines("drop database c1_backtest")) == 1
    assert len(scan_drop_lines("DROP\tTABLE  t2")) == 1
    assert scan_drop_lines("SELECT dropped_col, 'DROP TABLE' AS hint FROM t") == [
        "SELECT dropped_col, 'DROP TABLE' AS hint FROM t"
    ], "词边界判据按行匹配：字符串字面量含 DROP TABLE 同样命中（静态扫描保守面）"


def test_benign_sql_allowed(fake_gateway_factory):
    gateway = fake_gateway_factory(
        staged={
            "scripts/etl/load.py": "INSERT INTO t SELECT 1;\nDELETE FROM tmp WHERE day < today - 7;\n"
        }
    )
    passed, detail = make_drop_gate().check(gateway, ["scripts/etl/load.py"], session_id="s1")
    assert passed is True and detail == ""


def test_owner_gate_marker_allows_with_audit(tmp_path: Path, fake_gateway_factory):
    """Owner 门逃生：[allow-drop-gate:reason≥10字] 放行+审计。"""
    gateway = fake_gateway_factory(
        staged={"scripts/migration/nuke.py": f'SQL = "{DROP_SQL}"\n'}
    )
    passed, note = make_drop_gate().check(
        gateway,
        ["scripts/migration/nuke.py"],
        session_id="s1",
        commit_message="schema migration [allow-drop-gate:Owner 批复的归档表迁移-2026]",
    )
    assert passed is True
    assert "Owner 批复的归档表迁移-2026" in note, "放行注记携带 reason（随审计留痕）"
    audit = tmp_path / ".runtime/gate_audit/obj_s_drop_gate.jsonl"
    record = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert record["action"] == "allowed_by_marker"


def test_short_marker_reason_is_ineffective(fake_gateway_factory):
    """reason<10 字的标记无效（防标记漂洗）→ 仍阻断。"""
    gateway = fake_gateway_factory(
        staged={"scripts/migration/nuke.py": f'SQL = "{DROP_SQL}"\n'}
    )
    passed, _ = make_drop_gate().check(
        gateway,
        ["scripts/migration/nuke.py"],
        session_id="s1",
        commit_message="[allow-drop-gate:trust me]",
    )
    assert passed is False
    assert ALLOW_MARKER_RE.search("[allow-drop-gate:trust me]") is None


def test_staged_read_failure_fail_open(fake_gateway_factory):
    """staged 读失败（二进制/悬空）→ 跳过该文件不误报。"""
    gateway = fake_gateway_factory(staged={"blob.bin": "ignored"})  # FakeGateway 无该 key 内容
    gateway._staged = {"blob.bin": None}  # type: ignore[assignment] — 模拟 :path 缺内容
    passed, detail = make_drop_gate().check(gateway, ["blob.bin"], session_id="s1")
    assert passed is True and detail == ""
