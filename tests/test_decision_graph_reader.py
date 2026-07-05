# [A_test] module_id: SRC-TST-9002 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SH-DB-002 | docs/03_modules/_cross_layer/database/blueprint.md | §decisiongraph
# [MODULE] zephyr.governance.persistence.decision_graph_reader
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
"""test_decision_graph_reader — DecisionGraphReader 单元/集成测试。

验证内容：
  - import 成功（模块可加载）
  - 关键查询方法存在（get_all_tracks/get_all_layers/find_*）
  - DB 可用时：4 tracks + 10 layers 初始化数据验证
  - 不变量检测方法可调用（DEC-INV-001/002/005）
"""

import sys

import pytest

sys.path.insert(0, "src")

try:
    from zephyr.governance.persistence.decision_graph_reader import DecisionGraphReader

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:  # pragma: no cover
    _IMPORT_OK = False
    _IMPORT_REASON = repr(e)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


def _db_available() -> bool:
    try:
        from zephyr.governance.persistence.decisiongraph_schema import (
            get_decisiongraph_pg_connection,
        )
        conn = get_decisiongraph_pg_connection()
        conn.close()
        return True
    except Exception:
        return False


_DB_READY = _db_available()
db_required = pytest.mark.skipif(not _DB_READY, reason="decisiongraph DB 不可用")


class TestImportAndStructure:
    """模块结构与 import 可用性。"""

    def test_reader_importable(self):
        assert DecisionGraphReader is not None

    def test_reader_instantiable(self):
        reader = DecisionGraphReader()
        assert reader is not None

    @pytest.mark.parametrize("method", [
        "get_all_tracks", "get_all_layers", "get_all_nodes", "get_all_edges",
        "get_layers_by_track", "get_nodes_by_layer", "get_edges_by_type",
        "get_track_count", "get_layer_count", "get_node_count", "get_edge_count",
        "find_order_nodes_without_risk_approving",
        "find_signal_to_order_direct_edges",
        "find_nodes_missing_evidence_hash",
        "get_full_graph",
    ])
    def test_method_exists(self, method):
        assert hasattr(DecisionGraphReader, method), f"缺少方法 {method}"


@db_required
class TestInitialData:
    """DB 可用时验证初始化数据（4 tracks + 10 layers）。"""

    def test_track_count_is_4(self):
        with DecisionGraphReader() as reader:
            assert reader.get_track_count() == 4

    def test_layer_count_is_10(self):
        with DecisionGraphReader() as reader:
            assert reader.get_layer_count() == 10

    def test_tracks_contain_model_driven(self):
        with DecisionGraphReader() as reader:
            tracks = reader.get_all_tracks()
            track_ids = {t["track_id"] for t in tracks}
            assert "model_driven" in track_ids

    def test_layers_contain_L0_and_L6(self):
        with DecisionGraphReader() as reader:
            layers = reader.get_all_layers()
            layer_ids = {l["layer_id"] for l in layers}
            assert "L0" in layer_ids
            assert "L6" in layer_ids

    def test_nodes_empty_initially(self):
        with DecisionGraphReader() as reader:
            assert reader.get_node_count() == 0

    def test_edges_empty_initially(self):
        with DecisionGraphReader() as reader:
            assert reader.get_edge_count() == 0


@db_required
class TestInvariantChecks:
    """不变量检测方法可调用且返回 list。"""

    def test_find_order_nodes_without_risk_approving(self):
        with DecisionGraphReader() as reader:
            result = reader.find_order_nodes_without_risk_approving()
            assert isinstance(result, list)

    def test_find_signal_to_order_direct_edges(self):
        with DecisionGraphReader() as reader:
            result = reader.find_signal_to_order_direct_edges()
            assert isinstance(result, list)

    def test_find_nodes_missing_evidence_hash(self):
        with DecisionGraphReader() as reader:
            result = reader.find_nodes_missing_evidence_hash()
            assert isinstance(result, list)
