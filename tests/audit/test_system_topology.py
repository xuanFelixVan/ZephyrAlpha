# [A_test] module_id: SRC-TST-1716 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_system_topology
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_system_topology.py
# [TTL] task_bound


from zephyr.behavioral_audit.system_topology import (
    BTRACK_LABELS,
    BTRACK_SYSTEM_COUNT,
    CTRACK_LABELS,
    CTRACK_LAYER_COUNT,
    LAYER_GRAPH,
    PLANE_LABELS,
    RUNTIME_PLANE_COUNT,
    BTrackSystem,
    CTrackLayer,
    LayerTopology,
    RuntimePlane,
    btrack_systems_for_layer,
    get_downstream_chain,
    get_layer,
    get_layer_by_index,
    get_upstream_chain,
    layers_by_plane,
)


class TestCTrackLayer:
    def test_all_members_present(self):
        expected = [f"L{i:02d}" for i in range(14)]
        for prefix in expected:
            assert hasattr(CTrackLayer, prefix) or any(m.name.startswith(prefix) for m in CTrackLayer)

    def test_member_count(self):
        assert len(CTrackLayer) == CTRACK_LAYER_COUNT


class TestBTrackSystem:
    def test_member_count(self):
        assert len(BTrackSystem) == BTRACK_SYSTEM_COUNT

    def test_str_enum(self):
        assert BTrackSystem.SCRIPT_SYSTEM.value == "SCRIPT_SYSTEM"


class TestRuntimePlane:
    def test_member_count(self):
        assert len(RuntimePlane) == RUNTIME_PLANE_COUNT

    def test_all_planes_in_labels(self):
        for plane in RuntimePlane:
            assert plane in PLANE_LABELS


class TestLabelDicts:
    def test_ctrack_labels_complete(self):
        for layer in CTrackLayer:
            assert layer in CTRACK_LABELS

    def test_btrack_labels_complete(self):
        for system in BTrackSystem:
            assert system in BTRACK_LABELS


class TestLayerTopology:
    def test_instantiation(self):
        lt = LayerTopology(
            layer=CTrackLayer.L00_MARKET_DATA,
            label="test",
            index=0,
        )
        assert lt.layer == CTrackLayer.L00_MARKET_DATA
        assert lt.label == "test"
        assert lt.index == 0
        assert lt.upstream_layers == []
        assert lt.downstream_layers == []

    def test_is_source(self):
        lt = LayerTopology(
            layer=CTrackLayer.L00_MARKET_DATA,
            label="source",
            index=0,
            upstream_layers=[],
        )
        assert lt.is_source is True

    def test_is_not_source(self):
        lt = LayerTopology(
            layer=CTrackLayer.L01_FACTOR_FACTORY,
            label="not_source",
            index=1,
            upstream_layers=[CTrackLayer.L00_MARKET_DATA],
        )
        assert lt.is_source is False

    def test_is_sink(self):
        lt = LayerTopology(
            layer=CTrackLayer.L09_MONITORING,
            label="sink",
            index=9,
            downstream_layers=[],
        )
        assert lt.is_sink is True

    def test_is_not_sink(self):
        lt = LayerTopology(
            layer=CTrackLayer.L00_MARKET_DATA,
            label="not_sink",
            index=0,
            downstream_layers=[CTrackLayer.L01_FACTOR_FACTORY],
        )
        assert lt.is_sink is False


class TestLayerGraph:
    def test_all_layers_present(self):
        for layer in CTrackLayer:
            assert layer in LAYER_GRAPH

    def test_graph_size(self):
        assert len(LAYER_GRAPH) == CTRACK_LAYER_COUNT


class TestGetLayer:
    def test_existing_layer(self):
        lt = get_layer(CTrackLayer.L00_MARKET_DATA)
        assert lt is not None
        assert lt.index == 0

    def test_returns_correct_label(self):
        lt = get_layer(CTrackLayer.L04_RISK_CONTROL)
        assert lt is not None
        assert lt.label == "风险控制"


class TestGetLayerByIndex:
    def test_valid_index(self):
        lt = get_layer_by_index(0)
        assert lt is not None
        assert lt.layer == CTrackLayer.L00_MARKET_DATA

    def test_invalid_index(self):
        lt = get_layer_by_index(999)
        assert lt is None

    def test_all_indices_accessible(self):
        for i in range(CTRACK_LAYER_COUNT):
            lt = get_layer_by_index(i)
            assert lt is not None
            assert lt.index == i


class TestGetUpstreamChain:
    def test_source_layer_has_no_upstream(self):
        chain = get_upstream_chain(CTrackLayer.L00_MARKET_DATA)
        assert chain == []

    def test_mid_layer_has_upstream(self):
        chain = get_upstream_chain(CTrackLayer.L02_ALPHA_FACTORS)
        assert CTrackLayer.L01_FACTOR_FACTORY in chain
        assert CTrackLayer.L00_MARKET_DATA in chain

    def test_nonexistent_layer_returns_empty(self):
        chain = get_upstream_chain(CTrackLayer.L00_MARKET_DATA)
        assert isinstance(chain, list)


class TestGetDownstreamChain:
    def test_sink_layer_has_no_downstream(self):
        chain = get_downstream_chain(CTrackLayer.L09_MONITORING)
        assert chain == []

    def test_source_has_downstream(self):
        chain = get_downstream_chain(CTrackLayer.L00_MARKET_DATA)
        assert CTrackLayer.L01_FACTOR_FACTORY in chain


class TestLayersByPlane:
    def test_task_exec_plane(self):
        layers = layers_by_plane(RuntimePlane.TASK_EXEC)
        assert len(layers) > 0
        assert CTrackLayer.L02_ALPHA_FACTORS in layers

    def test_data_plane(self):
        layers = layers_by_plane(RuntimePlane.DATA)
        assert CTrackLayer.L00_MARKET_DATA in layers

    def test_empty_result_for_valid_plane(self):
        layers = layers_by_plane(RuntimePlane.SECURITY)
        assert isinstance(layers, list)


class TestBtrackSystemsForLayer:
    def test_layer_with_deps(self):
        deps = btrack_systems_for_layer(CTrackLayer.L00_MARKET_DATA)
        assert BTrackSystem.SCRIPT_SYSTEM in deps

    def test_nonexistent_layer(self):
        deps = btrack_systems_for_layer(CTrackLayer.L00_MARKET_DATA)
        assert isinstance(deps, list)
