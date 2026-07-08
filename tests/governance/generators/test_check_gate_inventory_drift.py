# [MODULE] tests.governance.generators.test_check_gate_inventory_drift
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.generators.check_gate_inventory_drift
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试 check_gate_inventory_drift.py 核心函数（scan_actual_gates/scan_blueprint_listed/detect_drift/main）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV-test_check_gate_inventory_drift | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-055]
"""test_check_gate_inventory_drift.py — commit_gates 模块清单漂移检测脚本单元测试（ARCH-055）

覆盖：
- scan_actual_gates: 扫描 commit_gates 目录实际 .py 文件
- scan_blueprint_listed: 解析 blueprint.md §0.1 表格
- detect_drift: 漂移检测（missing/extra）
- main: exit code 契约（0=一致 / 1=漂移 / 2=错误）
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


@pytest.fixture
def drift_module(monkeypatch, tmp_path):
    """用 tmp_path 替换 GATES_DIR 和 BLUEPRINT_PATH，隔离测试。"""
    fake_gates_dir = tmp_path / "src" / "zephyr" / "governance" / "commit_gates"
    fake_gates_dir.mkdir(parents=True)
    fake_blueprint = tmp_path / "docs" / "gate_engine" / "blueprint.md"
    fake_blueprint.parent.mkdir(parents=True)

    # 清除可能已导入的模块缓存
    mod_name = "scripts.governance.generators.check_gate_inventory_drift"
    if mod_name in sys.modules:
        monkeypatch.delitem(sys.modules, mod_name)

    mod = importlib.import_module("scripts.governance.generators.check_gate_inventory_drift")
    monkeypatch.setattr(mod, "GATES_DIR", fake_gates_dir)
    monkeypatch.setattr(mod, "BLUEPRINT_PATH", fake_blueprint)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    return mod, fake_gates_dir, fake_blueprint


class TestScanActualGates:
    """scan_actual_gates: 扫描 commit_gates 目录实际 .py 文件。"""

    def test_returns_py_files_excluding_init(self, drift_module):
        mod, gates_dir, _ = drift_module
        (gates_dir / "__init__.py").write_text("", encoding="utf-8")
        (gates_dir / "ttl_gate.py").write_text("", encoding="utf-8")
        (gates_dir / "create_guard.py").write_text("", encoding="utf-8")

        result = mod.scan_actual_gates()

        assert result == {"ttl_gate.py", "create_guard.py"}

    def test_empty_dir_returns_empty_set(self, drift_module):
        mod, _, _ = drift_module
        assert mod.scan_actual_gates() == set()

    def test_dir_not_exist_returns_empty(self, drift_module):
        mod, gates_dir, _ = drift_module
        # 删除目录模拟不存在
        import shutil
        shutil.rmtree(gates_dir)
        assert mod.scan_actual_gates() == set()


class TestScanBlueprintListed:
    """scan_blueprint_listed: 解析 blueprint.md §0.1 表格。"""

    def test_extracts_commit_gates_entries(self, drift_module):
        mod, _, blueprint = drift_module
        blueprint.write_text(
            "| `commit_gates/ttl_gate.py` | §0.1 | TTL门禁 | 已实现 | | 本模块 |\n"
            "| `commit_gates/create_guard.py` | §0.1 | 新建守卫 | 已实现 | | 本模块 |\n"
            "| `commit_gates/gate_repo.py` | §0.1 | gate仓库 | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        result = mod.scan_blueprint_listed()

        assert result == {"ttl_gate.py", "create_guard.py", "gate_repo.py"}

    def test_empty_blueprint_returns_empty(self, drift_module):
        mod, _, _ = drift_module
        assert mod.scan_blueprint_listed() == set()

    def test_file_not_exist_returns_empty(self, drift_module):
        mod, _, blueprint = drift_module
        blueprint.unlink(missing_ok=True)
        assert mod.scan_blueprint_listed() == set()

    def test_non_gate_lines_ignored(self, drift_module):
        mod, _, blueprint = drift_module
        blueprint.write_text(
            "Some other text\n"
            "| `other_module/foo.py` | §0.1 | 其他 | 已实现 | | 本模块 |\n"
            "| `commit_gates/ttl_gate.py` | §0.1 | TTL门禁 | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        result = mod.scan_blueprint_listed()

        assert result == {"ttl_gate.py"}


class TestDetectDrift:
    """detect_drift: 漂移检测。"""

    def test_in_sync_no_drift(self, drift_module):
        mod, gates_dir, blueprint = drift_module
        (gates_dir / "ttl_gate.py").write_text("", encoding="utf-8")
        (gates_dir / "create_guard.py").write_text("", encoding="utf-8")
        blueprint.write_text(
            "| `commit_gates/ttl_gate.py` | §0.1 | TTL | 已实现 | | 本模块 |\n"
            "| `commit_gates/create_guard.py` | §0.1 | 守卫 | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        missing, extra = mod.detect_drift()

        assert missing == []
        assert extra == []

    def test_missing_in_blueprint(self, drift_module):
        mod, gates_dir, blueprint = drift_module
        (gates_dir / "ttl_gate.py").write_text("", encoding="utf-8")
        (gates_dir / "new_gate.py").write_text("", encoding="utf-8")
        blueprint.write_text(
            "| `commit_gates/ttl_gate.py` | §0.1 | TTL | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        missing, extra = mod.detect_drift()

        assert missing == ["new_gate.py"]
        assert extra == []

    def test_extra_in_blueprint(self, drift_module):
        mod, gates_dir, blueprint = drift_module
        (gates_dir / "ttl_gate.py").write_text("", encoding="utf-8")
        blueprint.write_text(
            "| `commit_gates/ttl_gate.py` | §0.1 | TTL | 已实现 | | 本模块 |\n"
            "| `commit_gates/deleted_gate.py` | §0.1 | 已删 | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        missing, extra = mod.detect_drift()

        assert missing == []
        assert extra == ["deleted_gate.py"]

    def test_both_missing_and_extra(self, drift_module):
        mod, gates_dir, blueprint = drift_module
        (gates_dir / "new_gate.py").write_text("", encoding="utf-8")
        blueprint.write_text(
            "| `commit_gates/deleted_gate.py` | §0.1 | 已删 | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        missing, extra = mod.detect_drift()

        assert missing == ["new_gate.py"]
        assert extra == ["deleted_gate.py"]


class TestMain:
    """main: exit code 契约。"""

    def test_exit_0_when_in_sync(self, drift_module, capsys):
        mod, gates_dir, blueprint = drift_module
        (gates_dir / "ttl_gate.py").write_text("", encoding="utf-8")
        blueprint.write_text(
            "| `commit_gates/ttl_gate.py` | §0.1 | TTL | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        exit_code = mod.main()

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "OK" in captured.out
        assert "1 gates" in captured.out

    def test_exit_1_when_drift(self, drift_module, capsys):
        mod, gates_dir, blueprint = drift_module
        (gates_dir / "ttl_gate.py").write_text("", encoding="utf-8")
        (gates_dir / "missing_gate.py").write_text("", encoding="utf-8")
        blueprint.write_text(
            "| `commit_gates/ttl_gate.py` | §0.1 | TTL | 已实现 | | 本模块 |\n",
            encoding="utf-8",
        )

        exit_code = mod.main()

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "DRIFT" in captured.out
        assert "missing_gate.py" in captured.out
