# [A_test] module_id: MOD-GOV_factor_dag | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] tests.factor.test_factor_dag
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_factor_dag.py
# [A_module] module_id=MOD-L02-001 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""D_FACTOR core factor_dag 测试——dag.py。

覆盖：
- FactorNode / FactorEdge / FactorDAG 数据结构
- add_node / add_edge（重复处理）
- validate（重复节点 / 悬空边 / 环检测）
- topological_layers（Kahn 分层 / 环抛 ValueError / 外部依赖过滤）
- build_dag_from_registry（从 FactorRegistry 构建 / 过滤外部依赖 / 未注册抛 KeyError）
"""

from __future__ import annotations

import pytest

dag_mod = pytest.importorskip("zephyr.factor.core.factor_dag.dag")
factor_base = pytest.importorskip("zephyr.factor.factor_base")

FactorDAG = dag_mod.FactorDAG
FactorNode = dag_mod.FactorNode
FactorEdge = dag_mod.FactorEdge
build_dag_from_registry = dag_mod.build_dag_from_registry

FactorBase = factor_base.FactorBase
FactorMeta = factor_base.FactorMeta
FactorRegistry = factor_base.FactorRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


def _make_node(fid: str, deps: list[str] | None = None) -> FactorNode:
    return FactorNode(factor_id=fid, dependencies=deps or [])


class TestFactorNode:
    def test_default_values(self) -> None:
        n = FactorNode(factor_id="m1")
        assert n.factor_id == "m1"
        assert n.domain == ""
        assert n.dependencies == []
        assert n.metadata == {}


class TestFactorDAGAddOperations:
    def test_add_node(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a"))
        assert len(dag.nodes) == 1

    def test_add_node_overwrites_duplicate(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a", ["b"]))
        dag.add_node(_make_node("a", ["c"]))  # 覆盖
        assert len(dag.nodes) == 1
        assert dag.nodes[0].dependencies == ["c"]

    def test_add_edge(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_edge(FactorEdge(from_factor="a", to_factor="b"))
        assert len(dag.edges) == 1

    def test_add_edge_skips_duplicate(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_edge(FactorEdge(from_factor="a", to_factor="b"))
        dag.add_edge(FactorEdge(from_factor="a", to_factor="b"))
        assert len(dag.edges) == 1


class TestValidate:
    def test_clean_dag_no_errors(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a"))
        dag.add_node(_make_node("b", ["a"]))
        assert dag.validate() == []

    def test_duplicate_node_detected(self) -> None:
        """add_node 已去重，但若手动构造重复节点应能检测。"""
        dag = FactorDAG(
            dag_id="t",
            nodes=[_make_node("a"), _make_node("a")],
        )
        errors = dag.validate()
        assert any("重复节点" in e for e in errors)

    def test_dangling_edge_detected(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a"))
        dag.add_edge(FactorEdge(from_factor="a", to_factor="nonexistent"))
        errors = dag.validate()
        assert any("悬空边" in e for e in errors)

    def test_cycle_detected(self) -> None:
        """a -> b -> c -> a 形成环。"""
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a", ["c"]))  # a 依赖 c
        dag.add_node(_make_node("b", ["a"]))  # b 依赖 a
        dag.add_node(_make_node("c", ["b"]))  # c 依赖 b
        errors = dag.validate()
        assert any("检测到环" in e for e in errors)


class TestTopologicalLayers:
    def test_empty_dag(self) -> None:
        assert FactorDAG(dag_id="t").topological_layers() == []

    def test_single_node(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a"))
        assert dag.topological_layers() == [["a"]]

    def test_linear_chain(self) -> None:
        """a <- b <- c（c 依赖 b，b 依赖 a）→ 分层 [a], [b], [c]。"""
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a"))
        dag.add_node(_make_node("b", ["a"]))
        dag.add_node(_make_node("c", ["b"]))
        layers = dag.topological_layers()
        assert layers == [["a"], ["b"], ["c"]]

    def test_parallel_layer(self) -> None:
        """a, b 无依赖；c 依赖 a 和 b → 分层 [a, b], [c]。"""
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a"))
        dag.add_node(_make_node("b"))
        dag.add_node(_make_node("c", ["a", "b"]))
        layers = dag.topological_layers()
        assert len(layers) == 2
        assert set(layers[0]) == {"a", "b"}
        assert layers[1] == ["c"]

    def test_external_dependency_filtered(self) -> None:
        """dependencies 中不在 nodes 集合内的项视为外部输入（不计入入度）。"""
        dag = FactorDAG(dag_id="t")
        # a 依赖 "market_data"（外部，不在 DAG 内）和 "b"
        dag.add_node(_make_node("a", ["market_data", "b"]))
        dag.add_node(_make_node("b"))
        layers = dag.topological_layers()
        # b 无内部依赖 → 第 0 层；a 依赖 b → 第 1 层
        assert layers == [["b"], ["a"]]

    def test_cycle_raises_value_error(self) -> None:
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a", ["b"]))
        dag.add_node(_make_node("b", ["a"]))
        with pytest.raises(ValueError, match="检测到环"):
            dag.topological_layers()

    def test_diamond_shape(self) -> None:
        """菱形：a -> b, a -> c, b -> d, c -> d → 分层 [a], [b, c], [d]。"""
        dag = FactorDAG(dag_id="t")
        dag.add_node(_make_node("a"))
        dag.add_node(_make_node("b", ["a"]))
        dag.add_node(_make_node("c", ["a"]))
        dag.add_node(_make_node("d", ["b", "c"]))
        layers = dag.topological_layers()
        assert len(layers) == 3
        assert layers[0] == ["a"]
        assert set(layers[1]) == {"b", "c"}
        assert layers[2] == ["d"]


class TestBuildDagFromRegistry:
    def test_builds_simple_dag(self) -> None:
        """注册 2 个因子（b 依赖 a），构建 DAG 应含 2 节点 1 边。"""

        @FactorRegistry.register
        class FactorA(FactorBase):
            meta = FactorMeta(factor_id="a", name="A", domain="test")

            def compute(self, data, **kwargs):
                return data["close"]

        @FactorRegistry.register
        class FactorB(FactorBase):
            meta = FactorMeta(factor_id="b", name="B", domain="test", dependencies=["a"])

            def compute(self, data, **kwargs):
                return data["close"]

        dag = build_dag_from_registry(["a", "b"], dag_id="test_dag")
        assert dag.dag_id == "test_dag"
        assert len(dag.nodes) == 2
        assert len(dag.edges) == 1
        assert dag.edges[0].from_factor == "a"
        assert dag.edges[0].to_factor == "b"

    def test_filters_external_dependency(self) -> None:
        """dependencies 中不在 factor_ids 集合内的项被过滤（不生成边）。"""

        @FactorRegistry.register
        class FactorA(FactorBase):
            meta = FactorMeta(
                factor_id="a",
                name="A",
                domain="test",
                dependencies=["market_data"],  # 外部输入
            )

            def compute(self, data, **kwargs):
                return data["close"]

        dag = build_dag_from_registry(["a"])
        assert len(dag.nodes) == 1
        assert dag.nodes[0].dependencies == []  # 外部依赖被过滤
        assert len(dag.edges) == 0

    def test_unregistered_factor_raises_keyerror(self) -> None:
        with pytest.raises(KeyError):
            build_dag_from_registry(["nonexistent_factor"])

    def test_partial_internal_deps(self) -> None:
        """a 依赖 b（内部）和 market_data（外部），只 b 在 factor_ids。"""

        @FactorRegistry.register
        class FactorB(FactorBase):
            meta = FactorMeta(factor_id="b", name="B", domain="test")

            def compute(self, data, **kwargs):
                return data["close"]

        @FactorRegistry.register
        class FactorA(FactorBase):
            meta = FactorMeta(
                factor_id="a",
                name="A",
                domain="test",
                dependencies=["b", "market_data"],
            )

            def compute(self, data, **kwargs):
                return data["close"]

        dag = build_dag_from_registry(["a", "b"])
        a_node = next(n for n in dag.nodes if n.factor_id == "a")
        assert a_node.dependencies == ["b"]  # market_data 被过滤
        # 拓扑分层应正确
        layers = dag.topological_layers()
        assert layers == [["b"], ["a"]]
