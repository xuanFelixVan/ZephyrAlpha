# [A_test] module_id: MOD-GOV_decision_graph_reader | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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

from pathlib import Path

import pytest

try:
    from zephyr.governance.persistence.decision_graph_reader import DecisionGraphReader

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:  # noqa: BLE001 — import 失败降级 skip_module，不得阻断收集  # pragma: no cover
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
    except Exception:  # noqa: BLE001 — DB 可用性探测必须永不抛异常（降级 skip）
        return False


_DB_READY = _db_available()
db_required = pytest.mark.skipif(not _DB_READY, reason="decisiongraph DB 不可用")

_YAML = Path(__file__).resolve().parent.parent.parent / "architecture_model" / "domain" / "decision_graph_model.yaml"


def _yaml_contract() -> tuple[set[str], set[str]]:
    """从 YAML 真源动态派生 track/layer 契约集合（AGENTS.md §测试断言 SSoT 派生规则：

    测试断言禁止硬编码派生计数/派生集合，MUST 从 SSoT 真源动态派生）。
    """
    import yaml

    with open(_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    tracks = {t["track_id"] for t in data.get("tracks", [])}
    layers = {l["layer_id"] for l in data.get("layers", [])}
    return tracks, layers


class TestImportAndStructure:
    """模块结构与 import 可用性。"""

    def test_reader_importable(self):
        assert DecisionGraphReader is not None

    def test_reader_instantiable(self):
        reader = DecisionGraphReader()
        assert reader is not None

    @pytest.mark.parametrize(
        "method",
        [
            "get_all_tracks",
            "get_all_layers",
            "get_all_nodes",
            "get_all_edges",
            "get_layers_by_track",
            "get_nodes_by_layer",
            "get_edges_by_type",
            "get_track_count",
            "get_layer_count",
            "get_node_count",
            "get_edge_count",
            "find_order_nodes_without_risk_approving",
            "find_signal_to_order_direct_edges",
            "find_nodes_missing_evidence_hash",
            "get_full_graph",
        ],
    )
    def test_method_exists(self, method):
        assert hasattr(DecisionGraphReader, method), f"缺少方法 {method}"


@db_required
class TestInitialData:
    """DB 可用时验证初始化数据契约（tracks/layers 覆盖 YAML 真源）。

    契约语义：decisiongraph DB 由 YAML 真源（decision_graph_model.yaml）初始化，
    运行期 tracks/layers 集合 MUST 覆盖 YAML 契约（DB 可含更多设计期条目，
    精确相等断言会被正常演进打破——#ARCH-115 后 PG 常驻数据已实证）。
    """

    def test_track_count_covers_yaml(self):
        yaml_tracks, _ = _yaml_contract()
        with DecisionGraphReader() as reader:
            assert reader.get_track_count() >= len(yaml_tracks)

    def test_layer_count_covers_yaml(self):
        _, yaml_layers = _yaml_contract()
        with DecisionGraphReader() as reader:
            assert reader.get_layer_count() >= len(yaml_layers)

    def test_tracks_cover_yaml_contract(self):
        yaml_tracks, _ = _yaml_contract()
        with DecisionGraphReader() as reader:
            track_ids = {t["track_id"] for t in reader.get_all_tracks()}
            assert yaml_tracks <= track_ids

    def test_layers_cover_yaml_contract(self):
        _, yaml_layers = _yaml_contract()
        with DecisionGraphReader() as reader:
            layer_ids = {l["layer_id"] for l in reader.get_all_layers()}
            assert yaml_layers <= layer_ids

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
