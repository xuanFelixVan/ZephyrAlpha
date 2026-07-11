# [BLUEPRINT] MOD-GOV-check_vocab_hardcode | tests/test_check_vocab_hardcode.py | §gate-vocab-detection7-tests
# [MODULE] tests.test_check_vocab_hardcode
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.check_vocab_hardcode
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 测试隔离——monkeypatch REPO_ROOT 指向 tmp_path，不扫描真实仓库；仅测检测7（commit_gates 硬编码 tests/）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] task_bound
"""test_check_vocab_hardcode.py — GATE-VOCAB 检测7 单元测试（2026-06-30 治本补全）

覆盖检测7（commit_gates 测试目录名硬编码，红攻发现2治本）的核心场景：
1. commit_gates 中硬编码 "tests/" 字面量 → 检出
2. docstring 内 "tests/" → 不检出（docstring 豁免）
3. # noqa: gate-vocab 行 → 不检出（内联豁免）
4. 非 commit_gates 目录的 "tests/" → 不检出（范围限制）
5. "tests" 无斜杠 → 不检出（子串匹配 "tests/"）
6. f-string 含 "tests/" → 检出（JoinedStr 内 Constant 节点）
7. 列表多元素含 "tests/" → 检出（每个 Constant 独立命中）

测试隔离：monkeypatch cvh.REPO_ROOT → tmp_path，_check_file 在 tmp_path 下判定
commit_gates 范围，不扫描真实仓库 3575 文件。
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_D3_META = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_D3_META) not in sys.path:
    sys.path.insert(0, str(_D3_META))

import check_vocab_hardcode as cvh  # noqa: E402

_COMMIT_GATES_REL = "src/zephyr/governance/commit_gates"


def _make_commit_gate_file(tmp_path: Path, name: str, content: str) -> Path:
    """在 tmp_path 下创建模拟 commit_gates 文件，返回绝对路径。"""
    fp = tmp_path / _COMMIT_GATES_REL / name
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    return fp


def _detection7_issues(issues: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """从 _check_file 结果中筛选检测7的 issue（含 '硬编码测试目录名'）。"""
    return [i for i in issues if "硬编码测试目录名" in i[1]]


def test_detection7_hardcoded_tests_slash(tmp_path, monkeypatch):
    """检测7: commit_gates 中硬编码 'tests/' 字面量 → 检出。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_EXEMPT = "tests/"\n')
    issues = cvh._check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 1, f"应检出1处硬编码tests/, 实际: {d7}"
    assert d7[0][0] == 1, f"应在第1行检出, 实际行号: {d7[0][0]}"


def test_detection7_docstring_exempt(tmp_path, monkeypatch):
    """检测7: docstring 内 'tests/' → 不检出（docstring 豁免）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    content = '"""模块说明\n\ntests/ 豁免设计说明。\n"""\n'
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", content)
    issues = cvh._check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"docstring 应豁免, 实际检出: {d7}"


def test_detection7_noqa_exempt(tmp_path, monkeypatch):
    """检测7: # noqa: gate-vocab 行 → 不检出（内联豁免）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    content = '_EXEMPT = "tests/"  # noqa: gate-vocab\n'
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", content)
    issues = cvh._check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"noqa 应豁免, 实际检出: {d7}"


def test_detection7_non_commit_gates_scope(tmp_path, monkeypatch):
    """检测7: 非 commit_gates 目录的 'tests/' → 不检出（范围限制）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = tmp_path / "src" / "zephyr" / "other_module.py"
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text('_EXEMPT = "tests/"\n', encoding="utf-8")
    issues = cvh._check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"非commit_gates不应检出, 实际: {d7}"


def test_detection7_tests_without_slash(tmp_path, monkeypatch):
    """检测7: 'tests' 无斜杠 → 不检出（子串匹配 'tests/'）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_X = "tests"\n')
    issues = cvh._check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"'tests'无斜杠不应检出, 实际: {d7}"


def test_detection7_fstring(tmp_path, monkeypatch):
    """检测7: f-string 含 'tests/' → 检出（JoinedStr 内 Constant 节点）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_X = f"tests/{name}"\n')
    issues = cvh._check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 1, f"f-string应检出, 实际: {d7}"


def test_detection7_list_multiple(tmp_path, monkeypatch):
    """检测7: 列表多元素含 'tests/' → 检出（每个 Constant 独立命中）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_X = ["tests/a", "tests/b"]\n')
    issues = cvh._check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 2, f"列表2元素应各检出1处(共2), 实际: {len(d7)}"
