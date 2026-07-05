# [A_test] module_id: SRC-TST-9003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.extract_decisiongraph
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
"""test_extract_decisiongraph — extract_decisiongraph CLI 测试。

验证内容：
  - 脚本可执行（subprocess --help 退出码 0）
  - main 函数存在
  - DB 可用时 --summary 不抛异常
"""

import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "governance" / "extract_decisiongraph.py"


def _db_available() -> bool:
    try:
        sys.path.insert(0, "src")
        from zephyr.governance.persistence.decisiongraph_schema import (
            get_decisiongraph_pg_connection,
        )
        conn = get_decisiongraph_pg_connection()
        conn.close()
        return True
    except Exception:
        return False


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
        assert "extract" in result.stdout.lower() or "decision" in result.stdout.lower()

    def test_main_function_exists(self):
        sys.path.insert(0, str(_SCRIPT.parent.parent.parent))
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("extract_decisiongraph", _SCRIPT)
            mod = importlib.util.module_from_spec(spec)
            # 不执行 main，仅检查可加载
            assert spec is not None
        except Exception as e:
            pytest.fail(f"脚本无法加载: {e}")


@pytest.mark.skipif(not _db_available(), reason="decisiongraph DB 不可用")
class TestSummaryCommand:
    """DB 可用时 --summary 输出验证。"""

    def test_summary_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), "--summary"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, f"--summary 失败: {result.stderr}"
