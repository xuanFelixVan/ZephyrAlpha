# [BLUEPRINT] MOD-ML-019 | docs/03_modules/_domain_machine_learning_train/research_data_manager/blueprint.md
# [MODULE] zephyr.ml_train.research_data_manager
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（纯内存/DI；lineage_sink/quality_scorer/hasher/clock 全注入；hash 缺省 hashlib/json stdlib；语义旁挂 training_dataset_manager）
# [CONSUMERS] 运行时装配批（lineage 回调绑定 / 质量门控评分器绑定 / 保留策略 TTL 声明装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 版本链单向追加(parent 指向前驱)写后不可改; content_hash 缺省 sha256(sort_keys) 确定性; 质量评分∈[0,1]且低于 min_quality 门禁拒绝入链; 血缘事件仅经注入回调且回调异常不阻断; 保留策略未声明 Fail-Closed; 链头恒保留; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/research_data_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ResearchDataError(占位 ZA-MLT-UNREGISTERED-RESEARCH-DATA)——空 dataset_id/空 manifest/评分越界或低于门禁/未知数据集或版本/保留策略未声明时抛
# [TESTS] tests/ml_train/test_research_data_manager.py
# [A_module] module_id=MOD-ML-019 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ResearchDataManager — 研究数据管理器（MOD-ML-019）。

B13-04336（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-027，A3 D-RESEARCH-01）：
**数据集快照**（manifest + hash，Git-like 单向版本链）+ **血缘挂 lineage 回调**
（注入 sink，事件留痕）+ **质量评分**（复用质量门控注入，可选 min_quality
门禁）+ **元数据检索**（manifest 键值匹配，确定性排序）+ **保留策略**
（TTL 裁决，链头恒保留）。DVC/LakeFS 思想单机内存版。

分工：training_dataset_manager=训练数据集内容管理；本件=研究数据快照版本链
与血缘/质量/保留协议面，不碰真实存储（root/ sink 全注入）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: research_data_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: lineage_sink 参数
#   fields: 参数 lineage_sink（无注解）
#   code: research_data_manager.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: quality_scorer 参数
#   fields: 参数 quality_scorer（无注解）
#   code: research_data_manager.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: min_quality 参数
#   fields: 参数 min_quality（无注解）
#   code: research_data_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ResearchDataManager
#   name_en: ResearchDataManager
#   intro: 研究数据管理器（快照版本链 + 血缘 + 质量 + 检索 + 保留）。
#   desc: 研究数据管理器（快照版本链 + 血缘 + 质量 + 检索 + 保留）。；公共方法（定义序）: commit_snapshot, head, history, get_version, list_datasets, se…
#   inputs: clock lineage_sink quality_scorer min_quality retention_ttl hasher
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: ResearchDataManager
#   downstream: 运行时装配批（lineage 回调绑定 / 质量门控评分器绑定 / 保留策略 TTL 声明装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "DatasetSnapshot",
    "ResearchDataError",
    "ResearchDataManager",
    "RetentionDecision",
]


class ResearchDataError(Exception):
    """研究数据管理输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-RESEARCH-DATA。
    """


@dataclass(frozen=True)
class DatasetSnapshot:
    """数据集快照版本节点（frozen；Git-like 单向链）。"""

    dataset_id: str
    version_id: str
    parent_version: str | None
    manifest: dict
    content_hash: str
    quality_score: float | None
    message: str
    created_at: datetime.datetime


@dataclass(frozen=True)
class RetentionDecision:
    """保留策略 TTL 裁决（frozen）。"""

    dataset_id: str
    version_id: str
    keep: bool
    reason: str


def _default_hash(manifest: Mapping) -> str:
    """缺省 content_hash：JSON sort_keys 序列化后 sha256（确定性）。"""
    blob = json.dumps(manifest, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class ResearchDataManager:
    """研究数据管理器（快照版本链 + 血缘 + 质量 + 检索 + 保留）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        lineage_sink: Callable[[Mapping], None] | None = None,
        quality_scorer: Callable[[Mapping], float] | None = None,
        min_quality: float | None = None,
        retention_ttl: datetime.timedelta | None = None,
        hasher: Callable[[Mapping], str] | None = None,
    ) -> None:
        if min_quality is not None and not 0.0 <= min_quality <= 1.0:
            raise ResearchDataError(f"min_quality 越界: {min_quality!r}（需 ∈[0,1]）")
        if retention_ttl is not None and retention_ttl <= datetime.timedelta(0):
            raise ResearchDataError(f"retention_ttl 须为正: {retention_ttl!r}")
        self._clock = clock or datetime.datetime.now
        self._lineage_sink = lineage_sink
        self._quality_scorer = quality_scorer
        self._min_quality = min_quality
        self._retention_ttl = retention_ttl
        self._hasher = hasher or _default_hash
        self._datasets: dict[str, list[DatasetSnapshot]] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _emit_lineage(self, event: Mapping) -> None:
        if self._lineage_sink is None:
            return
        try:
            self._lineage_sink(event)
        except Exception:  # noqa: BLE001 — 血缘回调异常不阻断主流程
            _log.exception("lineage_sink 回调失败")

    def _chain_or_raise(self, dataset_id: str) -> list[DatasetSnapshot]:
        chain = self._datasets.get(dataset_id)
        if chain is None:
            raise ResearchDataError(f"未知数据集: {dataset_id!r}")
        return chain

    # ── 快照提交（Git-like 版本链） ─────────────────────────────────────────

    def commit_snapshot(self, dataset_id: str, manifest: Mapping, message: str = "") -> DatasetSnapshot:
        """提交数据集快照：hash + 质量门禁 + 链尾追加 + 血缘事件。"""
        if not dataset_id:
            raise ResearchDataError("dataset_id 为空")
        if not isinstance(manifest, Mapping) or not manifest:
            raise ResearchDataError("manifest 为空或非映射")
        content_hash = self._hasher(manifest)
        if not isinstance(content_hash, str) or not content_hash:
            raise ResearchDataError("hasher 返回非法 content_hash")
        quality: float | None = None
        if self._quality_scorer is not None:
            quality = float(self._quality_scorer(manifest))
            if not 0.0 <= quality <= 1.0:
                raise ResearchDataError(f"质量评分越界: {quality!r}（需 ∈[0,1]）")
            if self._min_quality is not None and quality < self._min_quality:
                raise ResearchDataError(f"质量评分 {quality:.4f} 低于门禁 {self._min_quality:.4f}（拒绝入链）")
        chain = self._datasets.setdefault(dataset_id, [])
        parent = chain[-1].version_id if chain else None
        snap = DatasetSnapshot(
            dataset_id=dataset_id,
            version_id=f"{dataset_id}@v{len(chain) + 1:04d}",
            parent_version=parent,
            manifest=dict(manifest),
            content_hash=content_hash,
            quality_score=quality,
            message=message,
            created_at=self._clock(),
        )
        chain.append(snap)
        self._emit_lineage(
            {
                "event": "commit",
                "dataset_id": dataset_id,
                "version_id": snap.version_id,
                "parent_version": parent,
                "content_hash": content_hash,
                "at": snap.created_at.isoformat(),
            }
        )
        _log.info("数据集快照: %s (parent=%s)", snap.version_id, parent)
        return snap

    # ── 查询 / 元数据检索 ──────────────────────────────────────────────────

    def head(self, dataset_id: str) -> DatasetSnapshot:
        """版本链头（未知数据集 Fail-Closed）。"""
        return self._chain_or_raise(dataset_id)[-1]

    def history(self, dataset_id: str) -> tuple[DatasetSnapshot, ...]:
        """版本链历史（新→旧，Git log 序）。"""
        return tuple(reversed(self._chain_or_raise(dataset_id)))

    def get_version(self, dataset_id: str, version_id: str) -> DatasetSnapshot:
        """指定版本节点（未知 Fail-Closed）。"""
        for snap in self._chain_or_raise(dataset_id):
            if snap.version_id == version_id:
                return snap
        raise ResearchDataError(f"未知版本: {version_id!r}（数据集 {dataset_id!r}）")

    def list_datasets(self) -> tuple[str, ...]:
        """数据集清单（字典序确定性）。"""
        return tuple(sorted(self._datasets))

    def search(self, criteria: Mapping) -> tuple[DatasetSnapshot, ...]:
        """元数据检索：manifest 全键值匹配，按 (created_at, version_id) 排序。"""
        if not isinstance(criteria, Mapping) or not criteria:
            raise ResearchDataError("检索条件为空")
        out = [
            snap
            for chain in self._datasets.values()
            for snap in chain
            if all(snap.manifest.get(k) == v for k, v in criteria.items())
        ]
        out.sort(key=lambda s: (s.created_at, s.version_id))
        return tuple(out)

    # ── 保留策略（TTL 裁决） ────────────────────────────────────────────────

    def apply_retention(self) -> tuple[RetentionDecision, ...]:
        """TTL 裁决：链头恒保留；非链头超期 keep=False（未声明 TTL Fail-Closed）。"""
        if self._retention_ttl is None:
            raise ResearchDataError("retention_ttl 未声明（保留策略须显式配置）")
        now = self._clock()
        decisions: list[RetentionDecision] = []
        for dataset_id in sorted(self._datasets):
            chain = self._datasets[dataset_id]
            head_id = chain[-1].version_id
            for snap in chain:
                if snap.version_id == head_id:
                    decisions.append(
                        RetentionDecision(
                            dataset_id=dataset_id,
                            version_id=snap.version_id,
                            keep=True,
                            reason="版本链头恒保留",
                        )
                    )
                elif now - snap.created_at > self._retention_ttl:
                    decisions.append(
                        RetentionDecision(
                            dataset_id=dataset_id,
                            version_id=snap.version_id,
                            keep=False,
                            reason=f"超过保留期 {self._retention_ttl}",
                        )
                    )
                else:
                    decisions.append(
                        RetentionDecision(
                            dataset_id=dataset_id,
                            version_id=snap.version_id,
                            keep=True,
                            reason="保留期内",
                        )
                    )
        return tuple(decisions)
