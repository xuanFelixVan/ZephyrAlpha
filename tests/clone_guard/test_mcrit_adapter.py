# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_mcrit_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_mcrit_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""McritAdapter 单元测试——验证废弃占位降级行为。

mcrit 已废弃（领域错位——二进制/恶意软件逆向工具，非源码克隆检测），见
clone-guard-engine-verification-ruling.md §2.1。本测试验证占位恒返回降级，
且不发起任何 subprocess 调用。
"""

from pathlib import Path
from unittest.mock import patch

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.mcrit_adapter import McritAdapter


class TestMcritHealthCheck:
    """health_check 恒返回 False（工具不可用）。"""

    def test_always_returns_false(self, tmp_path: Path):
        """无论 CLI/索引状态如何，health_check 恒返回 False。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        assert adapter.health_check() is False

    def test_returns_false_even_with_cli_present(self, tmp_path: Path):
        """即使 mock CLI 存在，仍返回 False（已废弃，不再探测 CLI）。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        with patch("shutil.which", return_value="/fake/mcrit"):
            assert adapter.health_check() is False


class TestMcritDetect:
    """detect 恒返回 ([], True)——工具不可用·降级。"""

    def test_empty_files_returns_degraded(self, tmp_path: Path):
        """空文件列表也返回降级（占位不短路）。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is True

    def test_with_files_returns_degraded(self, tmp_path: Path):
        """有文件也返回空 + 降级。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        findings, degraded = adapter.detect(["src/foo.py", "src/bar.py"])
        assert findings == []
        assert degraded is True

    def test_enabled_in_config_still_degraded(self, tmp_path: Path):
        """即使 mcrit_enabled=True，仍返回降级（废弃不受配置开关影响）。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        findings, degraded = adapter.detect(["src/foo.py"])
        assert findings == []
        assert degraded is True

    def test_no_subprocess_call_made(self, tmp_path: Path):
        """废弃占位不发起任何 subprocess 调用。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("subprocess.run") as mock_run:
            findings, degraded = adapter.detect(["src/foo.py"])
        assert mock_run.call_count == 0
        assert findings == []
        assert degraded is True


class TestMcritSearch:
    """search 恒返回 []——L0 搜索不可用。"""

    def test_returns_empty(self, tmp_path: Path):
        adapter = McritAdapter(tmp_path, CloneGuardConfig())
        assert adapter.search("def foo():") == []

    def test_returns_empty_even_when_enabled(self, tmp_path: Path):
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("shutil.which", return_value="/fake/mcrit"):
            assert adapter.search("def foo():", top_k=5) == []

    def test_no_subprocess_call_made(self, tmp_path: Path):
        """废弃占位 search 不发起 subprocess 调用。"""
        adapter = McritAdapter(tmp_path, CloneGuardConfig(mcrit_enabled=True))
        with patch("subprocess.run") as mock_run:
            result = adapter.search("def foo():")
        assert mock_run.call_count == 0
        assert result == []
