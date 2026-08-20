# [A_test] module_id: MOD-GOV_test_residue_ssot_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_test_residue_ssot_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_test_residue_ssot_gate.py — TEST-RESIDUE-SSOT 门禁单测

权威依据：test_residue_ssot_gate.py（make_test_residue_ssot_gate）
检测逻辑：staged .py 中 Assign/AnnAssign 的 Tuple/List/Set 字符串集合含 ≥2 个
trae_071 §test_residue_reclaim.covered_patterns.dir_prefixes 精确匹配 → 硬阻断。

测试组：
- TestGateSpecFields: gate_id / priority / isinstance(GateSpec)
- TestDetection（真实 AST + 真实 YAML 加载）:
  - 2/3 个 dir_prefix 硬编码（Tuple/List/Set/AnnAssign）→ 阻断
  - 单 dir_prefix（≥2 阈值以下）→ 放行
  - pytest hook 名（pytest_sessionfinish，startswith 误伤防护）→ 放行
  - 非 dir_prefix 字符串 → 放行
  - 1 prefix + 1 非 prefix（仅 1 命中）→ 放行
  - mkdtemp(prefix=...) 调用（非 Tuple 赋值）→ 放行
  - 非 .py 文件 → 忽略
  - 多违规聚合 / 多文件聚合
- TestFailOpen: git diff 失败/异常 / config 不可达 / SyntaxError / 文件缺失 / 反斜杠归一化

测试隔离：MagicMock 模拟 gateway.run_git + tmp_path 真实 .py 文件 + 真实 ast.parse +
真实 _load_dir_prefixes（读 trae_071 YAML，不 mock 检测逻辑——集成测试价值 > 速度）。
fixture 内容通过 write_text 写入（字符串参数，非 Tuple 赋值——本测试文件自身不触发 gate）。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.test_residue_ssot_gate import (  # noqa: E402
    make_test_residue_ssot_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _two_dir_prefixes() -> list[str]:
    """从真源取 2 个 dir_prefix 构造违规 fixture（auto-adapt trae_071 YAML 变更）。

    返回排序后前 2 个，保证 fixture 内容稳定可断言。测试依赖 YAML 含 ≥2 个 dir_prefix。
    """
    # 延迟 import 避免收集阶段触发 YAML 读取
    from zephyr.gov_enforcement.commit_gates.test_residue_ssot_gate import _load_dir_prefixes

    dps = _load_dir_prefixes()
    assert dps is not None and len(dps) >= 2, (
        "测试依赖 trae_071 §test_residue_reclaim.covered_patterns.dir_prefixes（≥2 个），YAML 不可达或前缀不足。"
    )
    return sorted(dps)[:2]


def _make_gateway(staged_files=None, project_root=None, diff_fails=False, diff_raises=False):
    """构造 mock gateway：--name-only 返回 staged 文件列表；rev-parse --show-toplevel
    返回 project_root。文件内容/存在性由 tmp_path 真实文件提供。"""
    gw = MagicMock()
    gw.project_root = project_root or str(_PROJECT_ROOT)

    if diff_raises:

        def _raise(*a, **k):
            raise RuntimeError("git not found")

        gw.run_git = _raise
        return gw

    def _run_git(cmd):
        if diff_fails and "--name-only" in cmd:
            return _MockResult(1, "")
        if "--name-only" in cmd:
            return _MockResult(0, "\n".join(staged_files or []))
        if "rev-parse" in cmd:
            return _MockResult(0, str(gw.project_root))
        return _MockResult(0, "")

    gw.run_git = _run_git
    return gw


# ---------------------------------------------------------------------------
# TestGateSpecFields
# ---------------------------------------------------------------------------
class TestGateSpecFields:
    def test_is_gate_spec(self):
        assert isinstance(make_test_residue_ssot_gate(), GateSpec)

    def test_gate_id(self):
        assert make_test_residue_ssot_gate().gate_id == "TEST-RESIDUE-SSOT"

    def test_priority(self):
        # 56——DERIVED-FILE-DELETION-PROTECTION(46)/HELD-OVERLAP(50) 之后、
        # BLUEPRINT-NODE-ID-HARDCODE(57) 之前（同 hardcode 检测族）
        assert make_test_residue_ssot_gate().priority == 56


# ---------------------------------------------------------------------------
# TestDetection — 真实 AST + 真实 YAML 加载
# ---------------------------------------------------------------------------
class TestDetection:
    def test_two_prefixes_in_tuple_blocked(self, tmp_path):
        """Tuple 含 2 个 dir_prefix → 阻断。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "bad.py").write_text(f'_PREFIXES = ("{p1}", "{p2}")\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/bad.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert not passed
        assert "TEST_RESIDUE_SSOT_VIOLATION" in msg
        assert "bad.py" in msg

    def test_three_prefixes_in_list_blocked(self, tmp_path):
        """List 含 2 个 dir_prefix + 1 非 prefix（2 命中 ≥2 阈值）→ 阻断。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "bad.py").write_text(f'_DIRS = ["{p1}", "{p2}", "other"]\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/bad.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert not passed

    def test_prefixes_in_set_blocked(self, tmp_path):
        """Set 含 2 个 dir_prefix → 阻断。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "bad.py").write_text(f"_SET = {{{p1!r}, {p2!r}}}\n", encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/bad.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert not passed

    def test_annassign_typed_tuple_blocked(self, tmp_path):
        """AnnAssign（带类型注解）含 2 个 dir_prefix → 阻断。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "bad.py").write_text(f'_PREFIXES: tuple = ("{p1}", "{p2}")\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/bad.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert not passed

    def test_single_prefix_passes(self, tmp_path):
        """单 dir_prefix（<2 阈值）→ 放行（pytest_ 单独可能是合法助手）。"""
        p1, _ = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "ok.py").write_text(f'_P = ("{p1}",)\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/ok.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_pytest_hook_names_pass(self, tmp_path):
        """pytest hook 名（pytest_sessionfinish 等）精确不匹配 dir_prefix → 放行。

        防护 startswith 误伤：若用 startswith("pytest_") 会误报 hook 名。
        本 gate 用精确匹配，hook 名不等于 "pytest_" → 不命中。
        """
        pkg = tmp_path / "tests"
        pkg.mkdir()
        (pkg / "conftest.py").write_text(
            '_HOOKS = ("pytest_sessionfinish", "pytest_configure", "pytest_collection")\n',
            encoding="utf-8",
        )
        gw = _make_gateway(staged_files=["tests/conftest.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_prefix_strings_pass(self, tmp_path):
        """非 dir_prefix 字符串集合 → 放行。"""
        pkg = tmp_path / "src"
        pkg.mkdir()
        (pkg / "ok.py").write_text('_NAMES = ("alice", "bob", "charlie")\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["src/ok.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_one_prefix_plus_non_prefix_passes(self, tmp_path):
        """1 个 dir_prefix + 1 个非 prefix（仅 1 命中 <2 阈值）→ 放行。"""
        p1, _ = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "ok.py").write_text(f'_MIX = ("{p1}", "not_a_prefix")\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/ok.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_mkdtemp_call_passes(self, tmp_path):
        """tempfile.mkdtemp(prefix="git_guard_test_") 是 Call 非 Tuple 赋值 → 放行。

        回归 #ARCH-TEST-RESIDUE-CLEANUP-001：tests/rollback/test_concurrency_guard_red_blue.py
        用此模式，本 gate 不应误报。
        """
        pkg = tmp_path / "tests"
        pkg.mkdir()
        (pkg / "helper.py").write_text(
            'import tempfile\nfrom pathlib import Path\nroot = Path(tempfile.mkdtemp(prefix="git_guard_test_"))\n',
            encoding="utf-8",
        )
        gw = _make_gateway(staged_files=["tests/helper.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_non_py_file_ignored(self, tmp_path):
        """非 .py 文件含硬编码前缀 → 忽略（放行）。"""
        p1, p2 = _two_dir_prefixes()
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "note.md").write_text(f'prefixes = ("{p1}", "{p2}")\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["docs/note.md"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_multiple_violations_in_one_file_aggregated(self, tmp_path):
        """单文件多违规赋值 → 全部汇报。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "bad.py").write_text(
            f'_A = ("{p1}", "{p2}")\n_B = ["{p1}", "{p2}"]\n',
            encoding="utf-8",
        )
        gw = _make_gateway(staged_files=["scripts/bad.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert not passed
        # 两个赋值各一行汇报
        assert msg.count("bad.py") >= 2

    def test_multiple_files_aggregated(self, tmp_path):
        """多个 staged .py 都违规 → 聚合报错。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        for name in ("a.py", "b.py"):
            (pkg / name).write_text(f'_X = ("{p1}", "{p2}")\n', encoding="utf-8")
        gw = _make_gateway(
            staged_files=["scripts/a.py", "scripts/b.py"],
            project_root=str(tmp_path),
        )
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert not passed
        assert "a.py" in msg
        assert "b.py" in msg

    def test_no_staged_files_passes(self, tmp_path):
        gw = _make_gateway(staged_files=[], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""


# ---------------------------------------------------------------------------
# TestFailOpen
# ---------------------------------------------------------------------------
class TestFailOpen:
    def test_fail_open_on_git_diff_failure(self, tmp_path):
        gw = _make_gateway(diff_fails=True, project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_git_diff_exception(self, tmp_path):
        gw = _make_gateway(diff_raises=True, project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_config_unreachable(self, tmp_path, monkeypatch):
        """_load_dir_prefixes 返回 None（YAML 不可达）→ fail-open。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "bad.py").write_text(f'_PREFIXES = ("{p1}", "{p2}")\n', encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/bad.py"], project_root=str(tmp_path))
        import zephyr.gov_enforcement.commit_gates.test_residue_ssot_gate as gate_mod

        monkeypatch.setattr(gate_mod, "_load_dir_prefixes", lambda: None)
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_fail_open_on_syntax_error(self, tmp_path):
        """staged .py 语法错误 → 跳过该文件（fail-open，不阻断 commit）。"""
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "broken.py").write_text("def (:  # 语法错误\n", encoding="utf-8")
        gw = _make_gateway(staged_files=["scripts/broken.py"], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_staged_file_missing_on_disk_skipped(self, tmp_path):
        """staged 列表含 .py 但磁盘不存在 → 跳过（放行）。"""
        rel = "scripts/ghost.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert passed
        assert msg == ""

    def test_backslash_path_normalized(self, tmp_path):
        """Windows 反斜杠路径归一化后正确检测。"""
        p1, p2 = _two_dir_prefixes()
        pkg = tmp_path / "scripts"
        pkg.mkdir()
        (pkg / "bad.py").write_text(f'_PREFIXES = ("{p1}", "{p2}")\n', encoding="utf-8")
        # git diff 返回反斜杠路径
        rel = r"scripts\bad.py"
        gw = _make_gateway(staged_files=[rel], project_root=str(tmp_path))
        passed, msg = make_test_residue_ssot_gate().check(gw, [])
        assert not passed
        assert "bad.py" in msg
