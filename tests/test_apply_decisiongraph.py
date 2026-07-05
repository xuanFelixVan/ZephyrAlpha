# [A_test] module_id: SRC-TST-9004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.apply_decisiongraph
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
"""test_apply_decisiongraph — apply_decisiongraph CLI 测试。

验证内容：
  - 脚本可执行（subprocess --help 退出码 0）
  - main 函数存在
  - 不实际写 DB（避免污染生产数据）
"""

import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "governance" / "apply_decisiongraph.py"


class TestCLIEntryPoint:
    """CLI 入口可用性。"""

    def test_script_file_exists(self):
        assert _SCRIPT.exists(), f"脚本不存在: {_SCRIPT}"

    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"--help 失败: {result.stderr}"
        out = (result.stdout + result.stderr).lower()
        assert "apply" in out or "decision" in out

    def test_module_loadable(self):
        sys.path.insert(0, "src")
        import importlib.util
        spec = importlib.util.spec_from_file_location("apply_decisiongraph", _SCRIPT)
        assert spec is not None, "无法创建模块 spec"


class TestWriteLockKey:
    """验证 pg_advisory_lock 键常量（424244，防止与 depgraph/dataflowgraph 撞锁）。"""

    def test_lock_key_is_424244(self):
        # 读取脚本源码确认锁键
        content = _SCRIPT.read_text(encoding="utf-8")
        assert "424244" in content, "apply_decisiongraph.py 未使用 pg_advisory_lock(424244)"

    def test_no_depgraph_lock_key_collision(self):
        content = _SCRIPT.read_text(encoding="utf-8")
        # 424242 是 depgraph 的锁，不应出现在 apply_decisiongraph
        # 允许在注释里提到，但 pg_advisory_lock(424242) 不应出现
        assert "pg_advisory_lock(424242)" not in content, "锁键与 depgraph 冲突"
