"""单测 upgrade_tested_modules —— ARCH-FRONTMATTER-STATE-001 Phase 1。

验证有测试覆盖的模块的 design_maturity 和 build_status 升级逻辑：
- design_maturity: prototype → production（原有逻辑，回归保护）
- build_status: generated → stable（ARCH-FRONTMATTER-STATE-001 新增，修复死代码）
- 边升级: import_depends → test_depends（原有逻辑，回归保护）

测试隔离：使用内存 dict/list 构造假 nodes/edges，不触碰生产 depgraph。
"""
import sys
from pathlib import Path

import pytest

# 将 scripts/governance 加入 sys.path 以导入 generate_project_depgraph 模块
_REPO_ROOT = Path(__file__).resolve().parents[3]
_GOV_SCRIPTS = _REPO_ROOT / "scripts" / "governance"
if str(_GOV_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_GOV_SCRIPTS))

from generate_project_depgraph import upgrade_tested_modules, CODE_TYPES  # noqa: E402


def _make_node(node_id, node_type, design_maturity="prototype", build_status="generated"):
    """构造测试用 node dict。"""
    return {
        "id": node_id,
        "type": node_type,
        "design_maturity": design_maturity,
        "build_status": build_status,
    }


def _make_edge(src, dst, dep_type="import_depends"):
    """构造测试用 edge dict。"""
    return {
        "from": src,
        "to": dst,
        "dep_type": dep_type,
        "coupling_strength": "critical",
    }


class TestUpgradeTestedModules:
    """upgrade_tested_modules 核心逻辑测试。"""

    def test_tested_module_upgraded_to_production_stable(self):
        """有测试覆盖的 CODE_TYPES 模块应升级为 production/stable。"""
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "mod1")]

        tested = upgrade_tested_modules(nodes, edges)

        assert "mod1" in tested
        assert nodes["mod1"]["design_maturity"] == "production"
        assert nodes["mod1"]["build_status"] == "stable"

    def test_edge_upgraded_to_test_depends(self):
        """test→module 的 import_depends 边应升级为 test_depends。"""
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "mod1")]

        upgrade_tested_modules(nodes, edges)

        assert edges[0]["dep_type"] == "test_depends"
        assert edges[0]["coupling_strength"] == "optional"

    def test_untested_module_stays_prototype_generated(self):
        """无测试覆盖的模块应保持 prototype/generated 不变。"""
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "mod2": _make_node("mod2", "module"),
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "mod1")]  # 只测 mod1，不测 mod2

        upgrade_tested_modules(nodes, edges)

        assert nodes["mod2"]["design_maturity"] == "prototype"
        assert nodes["mod2"]["build_status"] == "generated"

    def test_non_code_type_target_not_upgraded(self):
        """目标为非 CODE_TYPES（如 config）时不应升级。"""
        nodes = {
            "cfg1": _make_node("cfg1", "config"),
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "cfg1")]

        tested = upgrade_tested_modules(nodes, edges)

        assert "cfg1" not in tested
        assert nodes["cfg1"]["design_maturity"] == "prototype"  # 未变
        assert nodes["cfg1"]["build_status"] == "generated"  # 未变

    def test_non_import_depends_edge_ignored(self):
        """非 import_depends 边（如 references）不应触发升级。"""
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "mod1", dep_type="references")]

        tested = upgrade_tested_modules(nodes, edges)

        assert tested == set()
        assert nodes["mod1"]["design_maturity"] == "prototype"
        assert nodes["mod1"]["build_status"] == "generated"

    def test_non_test_source_not_upgraded(self):
        """源节点非 test 类型时不应触发升级。"""
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "mod2": _make_node("mod2", "module"),
        }
        edges = [_make_edge("mod2", "mod1")]  # module→module，非 test→module

        tested = upgrade_tested_modules(nodes, edges)

        assert tested == set()
        assert nodes["mod1"]["design_maturity"] == "prototype"

    def test_multiple_test_edges_all_upgraded(self):
        """多个 test→module 边应全部升级。"""
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "mod2": _make_node("mod2", "script"),
            "test1": _make_node("test1", "test"),
            "test2": _make_node("test2", "test"),
        }
        edges = [
            _make_edge("test1", "mod1"),
            _make_edge("test2", "mod2"),
        ]

        tested = upgrade_tested_modules(nodes, edges)

        assert tested == {"mod1", "mod2"}
        assert nodes["mod1"]["build_status"] == "stable"
        assert nodes["mod2"]["build_status"] == "stable"
        assert all(e["dep_type"] == "test_depends" for e in edges)

    def test_code_types_contains_module_and_script(self):
        """回归保护：CODE_TYPES 应包含 module 和 script（depgraph 主要代码类型）。"""
        assert "module" in CODE_TYPES
        assert "script" in CODE_TYPES

    def test_empty_inputs(self):
        """空 nodes/edges 应安全返回空集。"""
        tested = upgrade_tested_modules({}, [])
        assert tested == set()

    def test_target_node_missing_from_nodes(self):
        """边的目标节点不在 nodes dict 中时应安全跳过（无法判定 type 不升级）。"""
        nodes = {
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "ghost")]  # ghost 不在 nodes

        tested = upgrade_tested_modules(nodes, edges)

        # 目标节点不存在 → to_type 为空 → 不在 CODE_TYPES → 不加入 tested_modules
        # 这是正确行为：无法判定类型时不升级，避免误升级非代码节点
        assert tested == set()
        # 不 crash 即通过
