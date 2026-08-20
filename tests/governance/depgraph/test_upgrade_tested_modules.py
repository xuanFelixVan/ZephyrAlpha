"""单测 upgrade_tested_modules —— ARCH-MM-002 两档化。

ARCH-MM-002 (2026-07-23): design_maturity 从 3 态（design/prototype/production）
简化为 2 态（design/production）。职责单一原则：
- design_maturity = 物理存在性（文件存在=production，仅设计=design）
- build_status = 测试覆盖度（planned/stable/generated）

upgrade_tested_modules 只升级 build_status（production+test → stable），
不再升级 design_maturity（CODE_TYPES 节点物理存在即 production）。

测试覆盖：
- 有测试覆盖的 CODE_TYPES 模块：build_status generated → stable
- 边升级: import_depends → test_depends
- 无测试覆盖的模块：build_status 保持 generated
- 非代码类型/非 import_depends/非 test 源：不升级
- 2 态 smoke test：derive_design_maturity / derive_build_status 不再产出 prototype

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

from generate_project_depgraph import (  # noqa: E402
    CODE_TYPES,
    derive_build_status,
    derive_design_maturity,
    upgrade_tested_modules,
)


def _make_node(node_id, node_type, design_maturity="production", build_status="generated"):
    """构造测试用 node dict。

    ARCH-MM-002: 默认 design_maturity='production'（物理存在=production）。
    """
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
    """upgrade_tested_modules 核心逻辑测试（ARCH-MM-002 两档化）。"""

    def test_tested_module_build_status_upgraded_to_stable(self):
        """有测试覆盖的 CODE_TYPES 模块 build_status 应升级为 stable。

        ARCH-MM-002: design_maturity 保持 production（物理存在不变），
        仅 build_status generated → stable。
        """
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "mod1")]

        tested = upgrade_tested_modules(nodes, edges)

        assert "mod1" in tested
        # design_maturity 不再被 upgrade_tested_modules 修改（职责单一）
        assert nodes["mod1"]["design_maturity"] == "production"
        # build_status 升级为 stable
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

    def test_untested_module_stays_production_generated(self):
        """无测试覆盖的模块应保持 production/generated 不变。

        ARCH-MM-002: 无 prototype 态。未测模块 design_maturity=production，
        build_status=generated（AI 已生成未验证）。
        """
        nodes = {
            "mod1": _make_node("mod1", "module"),
            "mod2": _make_node("mod2", "module"),
            "test1": _make_node("test1", "test"),
        }
        edges = [_make_edge("test1", "mod1")]  # 只测 mod1，不测 mod2

        upgrade_tested_modules(nodes, edges)

        assert nodes["mod2"]["design_maturity"] == "production"
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
        assert nodes["cfg1"]["design_maturity"] == "production"  # 未变
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
        assert nodes["mod1"]["design_maturity"] == "production"
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
        assert nodes["mod1"]["design_maturity"] == "production"

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


class TestTwoStateMaturitySmoke:
    """ARCH-MM-002 两档化 smoke test。

    验证 design_maturity 只产出 design/production（无 prototype），
    build_status 不再有 prototype 分支。
    """

    def test_derive_design_maturity_always_production(self):
        """derive_design_maturity 对所有 CODE_TYPES 返回 production。

        ARCH-MM-002: 物理存在=production，generator 扫描到的文件恒为 production。
        has_test 参数保留但不再影响结果。
        """
        for nt in CODE_TYPES:
            assert derive_design_maturity(nt, has_test=False) == "production"
            assert derive_design_maturity(nt, has_test=True) == "production"

    def test_derive_design_maturity_no_prototype(self):
        """derive_design_maturity 永不返回 prototype（已删除）。"""
        for nt in CODE_TYPES:
            assert derive_design_maturity(nt) != "prototype"
            assert derive_design_maturity(nt, has_test=True) != "prototype"

    def test_derive_build_status_two_state(self):
        """derive_build_status 在 2 态下的推导规则。

        - design → planned
        - production + test → stable
        - production 无 test → generated
        """
        assert derive_build_status("design") == "planned"
        assert derive_build_status("design", has_test=True) == "planned"
        assert derive_build_status("production", has_test=True) == "stable"
        assert derive_build_status("production", has_test=False) == "generated"

    def test_derive_build_status_no_prototype_branch(self):
        """derive_build_status 不再有 prototype 分支（输入 prototype 走默认 generated）。"""
        # prototype 不再是合法 design_maturity，传入应走默认分支（非 design → generated/stable）
        # 确保不返回特殊 prototype 相关值
        result = derive_build_status("prototype", has_test=False)
        assert result in ("generated", "planned")  # 走默认路径，无 crash
        result = derive_build_status("prototype", has_test=True)
        assert result in ("stable", "generated", "planned")

    def test_maturity_rank_only_two_states(self):
        """panorama_common.MATURITY_RANK 只包含 design/production（无 prototype）。"""
        # 延迟导入避免循环依赖
        _PANORAMA_COMMON = _GOV_SCRIPTS / "d5_architecture" / "panorama_common.py"
        if _PANORAMA_COMMON.exists():
            import importlib.util

            spec = importlib.util.spec_from_file_location("panorama_common", _PANORAMA_COMMON)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            assert mod.MATURITY_RANK == {"design": 0, "production": 1}
            assert "prototype" not in mod.MATURITY_RANK
            # min_maturity 在 2 态下取最小
            assert mod.min_maturity(["production", "design"]) == "design"
            assert mod.min_maturity(["production", "production"]) == "production"
            assert mod.min_maturity([]) == ""
