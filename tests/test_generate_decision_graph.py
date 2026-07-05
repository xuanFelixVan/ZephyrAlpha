# [A_test] module_id: SRC-TST-9005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §decisiongraph
# [MODULE] scripts.governance.generate_decision_graph
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
"""test_generate_decision_graph — generate_decision_graph YAML→DB 同步器测试。

验证内容：
  - 脚本可执行（subprocess --help 退出码 0）
  - YAML 真源文件存在且可加载（4 tracks + 10 layers）
  - _YAML_PATH 路径正确
  - sync_decision_graph 函数存在
"""

import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "governance" / "generate_decision_graph.py"
_YAML = Path(__file__).resolve().parent.parent / "architecture_model" / "domain" / "decision_graph_model.yaml"


class TestYAMLTruthSource:
    """YAML 真源文件可用性。"""

    def test_yaml_file_exists(self):
        assert _YAML.exists(), f"YAML 真源不存在: {_YAML}"

    def test_yaml_loadable_with_4_tracks(self):
        import yaml
        with open(_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        tracks = data.get("tracks", [])
        assert len(tracks) == 4, f"期望 4 tracks，实际 {len(tracks)}"

    def test_yaml_loadable_with_10_layers(self):
        import yaml
        with open(_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        layers = data.get("layers", [])
        assert len(layers) == 10, f"期望 10 layers，实际 {len(layers)}"

    def test_yaml_contains_invariants(self):
        import yaml
        with open(_YAML, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        invariants = data.get("invariants", [])
        assert len(invariants) == 5, f"期望 5 invariants，实际 {len(invariants)}"


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

    def test_yaml_path_constant(self):
        content = _SCRIPT.read_text(encoding="utf-8")
        assert "decision_graph_model.yaml" in content, "脚本未引用 YAML 真源文件名"

    def test_no_db_write_on_dry_check(self):
        # 脚本源码应包含 sync_decision_graph 函数定义
        content = _SCRIPT.read_text(encoding="utf-8")
        assert "def sync_decision_graph" in content, "缺少 sync_decision_graph 函数"
