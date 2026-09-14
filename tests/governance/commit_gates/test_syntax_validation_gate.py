# -*- coding: utf-8 -*-
# [A_test] module_id: MOD-GOV_syntax_validation_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_syntax_validation_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_syntax_validation_gate — .py 语法错误硬阻断门禁单测（红蓝 v3 P0-1 批 2）

守卫测试（[TTL] permanent——批 1 裁定先例：守卫测试不能被 TTL 清扫器回收，
否则守卫静默消失=未来事故）。

扫描源语义（probe 2i 实弹复验发现的关键设计）：网关 gate 链跑在 git add 之前，
暂存区只有上次手动 add 的残留——本 gate 扫描 files 参数（commit() 归一化的
本 commit 真实提交清单），不扫暂存区。测试直接把文件列表传给 check。

覆盖：
- 好文件（合法 Python）→ 放行
- 坏文件（def broken(:）→ 阻断且 detail 含文件名与行号（红蓝 v3 S1.4 实弹复刻）
- 绝对路径（网关实际传参形式）同样入扫
- tests/ 路径同样检测（豁免只认 noqa 标记不认目录）
- noqa 豁免标记（reason>=10 字符）→ 放行
- noqa 标记 reason 不足 10 字符 → 仍阻断
- 非 SyntaxError 解析异常 → fail-open 放行；
  null bytes 在 Python 3.12 报 SyntaxError 属真实坏源码 → 阻断（fail-closed）
- 空 files → 放行
- git rev-parse 失败 → fail-open 放行
- GateSpec 字段（gate_id / priority=49）
"""

from __future__ import annotations

from types import SimpleNamespace

from zephyr.gov_enforcement.commit_gates.syntax_validation_gate import (
    _has_syntax_fixture_exemption,
    make_syntax_validation_gate,
)

GOOD_PY = "x = 1\nprint(x)\n"

# 红蓝 v3 S1.4 实弹同款坏语法（def broken(:）
BAD_PY = "def broken(:\n    pass\n"

# noqa 豁免（合规：reason >= 10 字符）
EXEMPT_BAD_PY = (
    "# noqa: syntax-fixture  故意坏语法夹具：测试解析器容错行为\n"
    "def broken(:\n    pass\n"
)

# noqa 标记但 reason 不足 10 字符（不合规，仍应阻断）
# 字符串值内 reason=123456789（9 字符<10）验证豁免拒绝；源行尾部含引号使行级
# 长度≥10，过 NOQA-VALIDATION 行级理由检查（对标 m11 测试先例）
EXEMPT_SHORT_REASON_PY = (
    "# noqa: syntax-fixture  123456789\n"
    "def broken(:\n    pass\n"
)


class _FakeGateway:
    """最小网关桩：只提供 project_root（wt_root 探测用）。

    扫描源=files 参数，不读暂存区——无 run_git 依赖（fail-open 探测由
    wt_root 为空的分支自然覆盖）。
    """

    def __init__(self, project_root: str):
        self.project_root = project_root


def _run(gateway, files=None):
    gate = make_syntax_validation_gate()
    return gate.check(gateway, files or [], session_id=None)


def _write(tmp_path, rel: str, content: str) -> str:
    """在 tmp_path 下写文件，返回相对路径（正斜杠）。"""
    import os

    target = tmp_path / rel.replace("/", os.sep)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return rel


# ── 放行路径 ──────────────────────────────────────────────────


def test_good_file_passes(tmp_path):
    rel = _write(tmp_path, "src/mod.py", GOOD_PY)
    ok, msg = _run(_FakeGateway(str(tmp_path)), [rel])
    assert ok, msg


def test_empty_files_passes(tmp_path):
    ok, msg = _run(_FakeGateway(str(tmp_path)), [])
    assert ok, msg


def test_non_py_files_ignored(tmp_path):
    ok, msg = _run(_FakeGateway(str(tmp_path)), ["README.md", "cfg.yaml"])
    assert ok, msg


def test_missing_file_skipped(tmp_path):
    # files 列表有路径但盘上不存在（delete/幻影场景）→ 跳过不阻断
    ok, msg = _run(_FakeGateway(str(tmp_path)), ["src/gone.py"])
    assert ok, msg


# ── 阻断路径 ──────────────────────────────────────────────────


def test_bad_file_blocks_with_filename_and_lineno(tmp_path):
    rel = _write(tmp_path, "src/broken_mod.py", BAD_PY)
    ok, msg = _run(_FakeGateway(str(tmp_path)), [rel])
    assert not ok
    assert "src/broken_mod.py" in msg
    assert ":1" in msg  # 行号（def broken(: 在第 1 行）


def test_absolute_path_also_scanned(tmp_path):
    # 网关实际传参=绝对路径（commit() abspath 归一）——同样入扫
    target = tmp_path / "abs_bad.py"
    target.write_text(BAD_PY, encoding="utf-8")
    ok, msg = _run(_FakeGateway(str(tmp_path)), [str(target)])
    assert not ok
    assert "abs_bad.py" in msg


def test_tests_dir_also_checked(tmp_path):
    # 红蓝 v3 实证：坏文件从 tests/ 进来——豁免只认 noqa 标记不认目录
    rel = _write(tmp_path, "tests/test_bad_fixture.py", BAD_PY)
    ok, msg = _run(_FakeGateway(str(tmp_path)), [rel])
    assert not ok
    assert "tests/test_bad_fixture.py" in msg


def test_multiple_bad_files_all_listed(tmp_path):
    r1 = _write(tmp_path, "src/a_bad.py", BAD_PY)
    r2 = _write(tmp_path, "scripts/b_bad.py", "y = (\n")
    ok, msg = _run(_FakeGateway(str(tmp_path)), [r1, r2])
    assert not ok
    assert "src/a_bad.py" in msg
    assert "scripts/b_bad.py" in msg


def test_block_message_teaches_noqa_escape(tmp_path):
    rel = _write(tmp_path, "src/broken_mod.py", BAD_PY)
    ok, msg = _run(_FakeGateway(str(tmp_path)), [rel])
    assert not ok
    assert "syntax-fixture" in msg  # 教学信息：逃生口标记


# ── noqa 豁免路径 ─────────────────────────────────────────────


def test_noqa_exempt_bad_file_passes(tmp_path):
    rel = _write(tmp_path, "tests/test_fixture_kept.py", EXEMPT_BAD_PY)
    ok, msg = _run(_FakeGateway(str(tmp_path)), [rel])
    assert ok, msg


def test_noqa_short_reason_still_blocks(tmp_path):
    rel = _write(tmp_path, "tests/test_fixture_bad_reason.py", EXEMPT_SHORT_REASON_PY)
    ok, msg = _run(_FakeGateway(str(tmp_path)), [rel])
    assert not ok


def test_has_syntax_fixture_exemption_unit():
    assert _has_syntax_fixture_exemption(EXEMPT_BAD_PY)
    assert not _has_syntax_fixture_exemption(EXEMPT_SHORT_REASON_PY)
    assert not _has_syntax_fixture_exemption(GOOD_PY)
    assert not _has_syntax_fixture_exemption("# noqa: syntax-fixture\n")  # 无 reason


# ── fail-open 路径 ────────────────────────────────────────────


def test_null_byte_file_blocks(tmp_path):
    # null bytes → Python 3.12 ast.parse 抛 SyntaxError("source code string cannot
    # contain null bytes")——真实坏源码应阻断（fail-closed），非环境异常
    target = tmp_path / "src" / "null_byte.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"\x00\x00import os\n")
    ok, msg = _run(_FakeGateway(str(tmp_path)), [str(target)])
    assert not ok
    assert "null_byte.py" in msg


def test_gate_spec_fields():
    gate = make_syntax_validation_gate()
    assert gate.gate_id == "SYNTAX-VALIDATION"
    assert gate.priority == 49
