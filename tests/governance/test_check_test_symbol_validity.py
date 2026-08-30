# [BLUEPRINT] MOD-GOV-058 | scripts/governance/check_test_symbol_validity.py | §
# [MODULE] tests.governance.test_check_test_symbol_validity
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# [A_test] module_id: MOD-GOV-058 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
"""test_check_test_symbol_validity.py — 孤儿测试符号检测门禁单测（CAND-GATEMECH-007）。

临时目录夹具构造迷你仓（src/ + tests/），验证：
- 检出：测试 import 真源不存在的符号
- 不误报：__all__ 符号 / 顶层符号 / __init__ re-export / 子模块导入 / 三方库 / 动态 __all__
- 出口码：0=PASS / 1=发现 / --warn-only 恒 0
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts" / "governance"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import check_test_symbol_validity as gate  # noqa: E402


@pytest.fixture()
def mini_repo(tmp_path: Path) -> Path:
    """构造迷你仓：src/pkg/mod.py 真源 + tests/ 测试文件。"""
    src = tmp_path / "src" / "pkg"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text(
        "from pkg.mod import real_func\n\n__all__ = ['real_func', 'ALIAS_CONST']\nALIAS_CONST = 1\n",
        encoding="utf-8",
    )
    (src / "mod.py").write_text(
        "def real_func():\n    return 1\n\n\nclass RealClass:\n    pass\n",
        encoding="utf-8",
    )
    (tmp_path / "tests").mkdir()
    return tmp_path


def _write_test(repo: Path, body: str) -> Path:
    p = repo / "tests" / "test_sample.py"
    p.write_text(body, encoding="utf-8")
    return p


class TestDetection:
    def test_ghost_symbol_detected(self, mini_repo: Path) -> None:
        test = _write_test(mini_repo, "from pkg.mod import ghost_func\n\ndef test_x():\n    assert True\n")
        findings = gate.check_test_file(test, mini_repo)
        assert len(findings) == 1
        assert findings[0].symbol == "ghost_func"
        assert findings[0].module == "pkg.mod"

    def test_existing_symbol_pass(self, mini_repo: Path) -> None:
        test = _write_test(mini_repo, "from pkg.mod import real_func, RealClass\n")
        assert gate.check_test_file(test, mini_repo) == []

    def test_init_reexport_no_false_positive(self, mini_repo: Path) -> None:
        """__init__.py re-export（import 名 + __all__）不误报。"""
        test = _write_test(mini_repo, "from pkg import real_func, ALIAS_CONST\n")
        assert gate.check_test_file(test, mini_repo) == []

    def test_submodule_import_no_false_positive(self, mini_repo: Path) -> None:
        test = _write_test(mini_repo, "from pkg import mod\n")
        assert gate.check_test_file(test, mini_repo) == []

    def test_third_party_import_skipped(self, mini_repo: Path) -> None:
        test = _write_test(mini_repo, "from os import definitely_not_a_symbol_xyz\n")
        assert gate.check_test_file(test, mini_repo) == []

    def test_star_import_skipped(self, mini_repo: Path) -> None:
        test = _write_test(mini_repo, "from pkg.mod import *\n")
        assert gate.check_test_file(test, mini_repo) == []

    def test_dynamic_all_skips_module(self, mini_repo: Path) -> None:
        (mini_repo / "src" / "pkg" / "dyn.py").write_text("__all__ = []\n__all__.append('x')\n", encoding="utf-8")
        test = _write_test(mini_repo, "from pkg.dyn import whatever\n")
        assert gate.check_test_file(test, mini_repo) == []

    def test_syntax_error_test_skipped(self, mini_repo: Path) -> None:
        test = _write_test(mini_repo, "def broken(:\n")
        assert gate.check_test_file(test, mini_repo) == []

    def test_relative_import(self, mini_repo: Path) -> None:
        (mini_repo / "tests" / "helper_mod.py").write_text("def helper():\n    pass\n", encoding="utf-8")
        test = _write_test(mini_repo, "from .helper_mod import helper, ghost\n")
        findings = gate.check_test_file(test, mini_repo)
        assert [f.symbol for f in findings] == ["ghost"]


class TestExitCodes:
    def test_main_pass(self, mini_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_test(mini_repo, "from pkg.mod import real_func\n")
        monkeypatch.setattr(sys, "argv", ["gate", str(mini_repo / "tests" / "test_sample.py")])
        monkeypatch.setattr(gate, "REPO_ROOT", mini_repo)
        assert gate.main() == 0

    def test_main_findings(self, mini_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_test(mini_repo, "from pkg.mod import ghost\n")
        monkeypatch.setattr(sys, "argv", ["gate", str(mini_repo / "tests" / "test_sample.py")])
        monkeypatch.setattr(gate, "REPO_ROOT", mini_repo)
        assert gate.main() == 1

    def test_main_warn_only_always_zero(self, mini_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_test(mini_repo, "from pkg.mod import ghost\n")
        monkeypatch.setattr(sys, "argv", ["gate", "--warn-only", str(mini_repo / "tests" / "test_sample.py")])
        monkeypatch.setattr(gate, "REPO_ROOT", mini_repo)
        assert gate.main() == 0

    def test_main_full_scan(self, mini_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """无 positional 参数 → 全量扫 REPO_ROOT/tests/。"""
        _write_test(mini_repo, "from pkg.mod import ghost2\n")
        monkeypatch.setattr(sys, "argv", ["gate"])
        monkeypatch.setattr(gate, "REPO_ROOT", mini_repo)
        assert gate.main() == 1
