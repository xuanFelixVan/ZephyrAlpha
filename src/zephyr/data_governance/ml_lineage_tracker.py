# [BLUEPRINT] MOD-DATA_GOV-013 | docs/03_modules/_domain_data_governance/ml_lineage_tracker/blueprint.md
# [MODULE] zephyr.data_governance.ml_lineage_tracker
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES] 无（纯内存；experiment_tracking 事件经注入适配器落边；clock 注入）
# [CONSUMERS] 运行时装配批（experiment_tracking 适配器绑定 / 模型评审全链反查 / 预测溯源查询）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 节点类型词表闭合(dataset|feature|model|prediction); 边类型词表闭合(dataset_to_feature|feature_to_model|model_to_prediction|dataset_to_model)且方向匹配; 节点/边幂等登记; 有向无环(加边成环拒绝); 反查结果按ID排序去重; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_governance/ml_lineage_tracker/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MlLineageError(占位 ZA-DATA-UNREGISTERED-ML-LINEAGE)——词表外类型/未知节点/方向不符/成环/适配器缺失或异常时抛
# [TESTS] tests/data_governance/test_ml_lineage_tracker.py
# [A_module] module_id=MOD-DATA_GOV-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""



ml_lineage_tracker — AI-ML 管线血缘追踪器（MOD-DATA_GOV-013）。

B10-02324（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DATGOV-010，A1 M8-NEW-05）：
ML 血缘——串接 **训练数据集版本 -> 特征版本 -> 模型版本 -> 线上预测** 四类血
缘边（边类型词表闭合）+ 登记接口（从 experiment_tracking 事件落边，注入适
配器）+ **模型到数据全链反查** + **预测到训练样本溯源**查询。

查重分工（蓝图 §0）：core/lineage_tracker=通用表级血缘（本件=ML 域四类节点
/边词表闭合的专用链，不改其存储）；ml_train/training_dataset_manager=数据
集版本本体（本件只登记版本 ID 血缘，不管数据集内容）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: ml_lineage_tracker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: event_adapter 参数
#   fields: 参数 event_adapter（无注解）
#   code: ml_lineage_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MlLineageTracker
#   name_en: MlLineageTracker
#   intro: ML 管线血缘追踪器（词表闭合登记 + 全链反查 + 预测溯源）。
#   desc: ML 管线血缘追踪器（词表闭合登记 + 全链反查 + 预测溯源）。；公共方法（定义序）: register_node, register_edge, register_event, node_kind, edges,…
#   inputs: clock event_adapter
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: MlLineageTracker
#   downstream: 运行时装配批（experiment_tracking 适配器绑定 / 模型评审全链反查 / 预测溯源查询）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "MlEdgeKind",
    "MlLineageEdge",
    "MlLineageError",
    "MlLineageTracker",
    "MlNodeKind",
    "PredictionLineage",
]


class MlLineageError(Exception):
    """ML 血缘登记/查询输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATA-UNREGISTERED-ML-LINEAGE。
    """


class MlNodeKind(str, Enum):
    """ML 血缘节点类型词表（闭合）。"""

    DATASET = "dataset"
    FEATURE = "feature"
    MODEL = "model"
    PREDICTION = "prediction"


class MlEdgeKind(str, Enum):
    """ML 血缘边类型词表（闭合，四类）。"""

    DATASET_TO_FEATURE = "dataset_to_feature"
    FEATURE_TO_MODEL = "feature_to_model"
    MODEL_TO_PREDICTION = "model_to_prediction"
    DATASET_TO_MODEL = "dataset_to_model"


#: 边类型 -> (源节点类型, 目标节点类型) 方向闭合表
_ALLOWED_DIRECTION: Final[dict[MlEdgeKind, tuple[MlNodeKind, MlNodeKind]]] = {
    MlEdgeKind.DATASET_TO_FEATURE: (MlNodeKind.DATASET, MlNodeKind.FEATURE),
    MlEdgeKind.FEATURE_TO_MODEL: (MlNodeKind.FEATURE, MlNodeKind.MODEL),
    MlEdgeKind.MODEL_TO_PREDICTION: (MlNodeKind.MODEL, MlNodeKind.PREDICTION),
    MlEdgeKind.DATASET_TO_MODEL: (MlNodeKind.DATASET, MlNodeKind.MODEL),
}

#: 适配器返回的边规格 (kind, source_id, target_id)
EdgeSpec = tuple[MlEdgeKind, str, str]


@dataclass(frozen=True)
class MlLineageEdge:
    """ML 血缘边（kind + 两端版本 ID，frozen）。"""

    kind: MlEdgeKind
    source: str
    target: str


@dataclass(frozen=True)
class PredictionLineage:
    """预测溯源视图（模型/特征/数据集版本全链，frozen，各自排序）。"""

    prediction_id: str
    model_versions: tuple[str, ...]
    feature_versions: tuple[str, ...]
    dataset_versions: tuple[str, ...]


class MlLineageTracker:
    """ML 管线血缘追踪器（词表闭合登记 + 全链反查 + 预测溯源）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        event_adapter: Callable[[Mapping], Iterable[EdgeSpec]] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._adapter = event_adapter
        self._kinds: dict[str, MlNodeKind] = {}
        self._edges: set[MlLineageEdge] = set()
        self._downstream: dict[str, set[str]] = {}
        self._upstream: dict[str, set[str]] = {}

    # ── 登记 ─────────────────────────────────────────────────────────────

    def register_node(self, node_id: str, kind: MlNodeKind) -> None:
        """登记节点：ID 非空；kind 词表闭合；同 ID 同 kind 幂等，异 kind 拒绝。"""
        if not node_id:
            raise MlLineageError("node_id 为空")
        if not isinstance(kind, MlNodeKind):
            raise MlLineageError(f"词表外节点类型: {kind!r}")
        existing = self._kinds.get(node_id)
        if existing is not None and existing is not kind:
            raise MlLineageError(f"节点类型冲突: {node_id!r} 已登记 {existing.value}，实收 {kind.value}")
        self._kinds[node_id] = kind

    def register_edge(self, kind: MlEdgeKind, source_id: str, target_id: str) -> MlLineageEdge:
        """登记边：kind 词表闭合、两端已登记、方向匹配闭合表、成环拒绝、幂等。"""
        if not isinstance(kind, MlEdgeKind):
            raise MlLineageError(f"词表外边类型: {kind!r}")
        want_src, want_dst = _ALLOWED_DIRECTION[kind]
        src_kind = self._kinds.get(source_id)
        dst_kind = self._kinds.get(target_id)
        if src_kind is None:
            raise MlLineageError(f"未知源节点: {source_id!r}")
        if dst_kind is None:
            raise MlLineageError(f"未知目标节点: {target_id!r}")
        if src_kind is not want_src or dst_kind is not want_dst:
            raise MlLineageError(
                f"边方向不符: {kind.value} 须 {want_src.value}->{want_dst.value}，"
                f"实收 {src_kind.value}->{dst_kind.value}"
            )
        edge = MlLineageEdge(kind=kind, source=source_id, target=target_id)
        if edge in self._edges:
            return edge  # 幂等
        if self._reachable(target_id, source_id):
            raise MlLineageError(f"加边成环拒绝: {source_id!r} -> {target_id!r}")
        self._edges.add(edge)
        self._downstream.setdefault(source_id, set()).add(target_id)
        self._upstream.setdefault(target_id, set()).add(source_id)
        _log.debug("ML血缘边登记: %s %s -> %s", kind.value, source_id, target_id)
        return edge

    def register_event(self, event: Mapping) -> tuple[MlLineageEdge, ...]:
        """从 experiment_tracking 事件落边（适配器注入；异常 Fail-Closed 包装）。"""
        if self._adapter is None:
            raise MlLineageError("event_adapter 未注入（Fail-Closed 不旁路）")
        try:
            specs = list(self._adapter(event))
        except MlLineageError:
            raise
        except Exception as exc:  # noqa: BLE001 — 适配器异常包装
            raise MlLineageError(f"event_adapter 适配失败: {exc}") from exc
        edges: list[MlLineageEdge] = []
        for spec in specs:
            if len(spec) != 3:
                raise MlLineageError(f"非法边规格(须三元组): {spec!r}")
            edges.append(self.register_edge(spec[0], spec[1], spec[2]))
        _log.info("experiment 事件落边: %d 条", len(edges))
        return tuple(edges)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def node_kind(self, node_id: str) -> MlNodeKind:
        """节点类型查询（未知 → Fail-Closed）。"""
        kind = self._kinds.get(node_id)
        if kind is None:
            raise MlLineageError(f"未知节点: {node_id!r}")
        return kind

    def edges(self) -> tuple[MlLineageEdge, ...]:
        """全部边（按 (kind,source,target) 确定性排序）。"""
        return tuple(sorted(self._edges, key=lambda e: (e.kind.value, e.source, e.target)))

    def datasets_of_model(self, model_id: str) -> tuple[str, ...]:
        """模型到数据全链反查：可达的全部数据集版本 ID（排序去重）。"""
        self._require_kind(model_id, MlNodeKind.MODEL)
        return tuple(sorted(n for n in self._upstream_closure(model_id) if self._kinds[n] is MlNodeKind.DATASET))

    def features_of_model(self, model_id: str) -> tuple[str, ...]:
        """模型上游全部特征版本 ID（排序去重）。"""
        self._require_kind(model_id, MlNodeKind.MODEL)
        return tuple(sorted(n for n in self._upstream_closure(model_id) if self._kinds[n] is MlNodeKind.FEATURE))

    def model_of_prediction(self, prediction_id: str) -> str:
        """预测所属模型版本（恰一个，否则 Fail-Closed）。"""
        self._require_kind(prediction_id, MlNodeKind.PREDICTION)
        models = sorted(n for n in self._upstream_closure(prediction_id) if self._kinds[n] is MlNodeKind.MODEL)
        if len(models) != 1:
            raise MlLineageError(f"预测 {prediction_id!r} 上游模型数={len(models)}（须恰为 1）")
        return models[0]

    def trace_prediction(self, prediction_id: str) -> PredictionLineage:
        """预测到训练样本溯源：模型/特征/数据集版本全链反查。"""
        self._require_kind(prediction_id, MlNodeKind.PREDICTION)
        closure = self._upstream_closure(prediction_id)
        return PredictionLineage(
            prediction_id=prediction_id,
            model_versions=tuple(sorted(n for n in closure if self._kinds[n] is MlNodeKind.MODEL)),
            feature_versions=tuple(sorted(n for n in closure if self._kinds[n] is MlNodeKind.FEATURE)),
            dataset_versions=tuple(sorted(n for n in closure if self._kinds[n] is MlNodeKind.DATASET)),
        )

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _require_kind(self, node_id: str, want: MlNodeKind) -> None:
        kind = self.node_kind(node_id)
        if kind is not want:
            raise MlLineageError(f"节点类型不符: {node_id!r} 为 {kind.value}，须 {want.value}")

    def _reachable(self, start: str, goal: str) -> bool:
        visited: set[str] = set()
        stack: list[str] = [start]
        while stack:
            node = stack.pop()
            if node == goal:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(self._downstream.get(node, ()))
        return False

    def _upstream_closure(self, seed: str) -> set[str]:
        visited: set[str] = set()
        stack: list[str] = list(self._upstream.get(seed, ()))
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            stack.extend(self._upstream.get(node, ()))
        return visited
