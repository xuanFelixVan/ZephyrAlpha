# [BLUEPRINT] MOD-ML-003 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.training_dataset_manager.manager
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] 无（标准库 hashlib/json）
# [CONSUMERS] MOD-ML-001 training_pipeline（load 段数据集版本锚定）；MOD-ML-009 learning_effect_feedback（效果回喂血缘）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 版本单调递增（同 dataset 重注册 version+1）；content_hash=sha256（canonical JSON）；parent_version 必须已存在；内存态默认（DB 持久化注入位预留）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DatasetLineageError(ZA-MLT-0006)——未知数据集/版本/parent 悬空时抛；空 rows→ValueError
# [TESTS] tests/ml_train/test_training_dataset_manager.py
# [A_module] module_id=MOD-ML-003 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
D_ML_TRAIN — MOD-ML-003 训练数据集管理器。

数据集版本化 / 快照 / 血缘登记三能力：

- ``register_dataset``：登记新快照（版本单调递增，sha256 内容指纹）。
- ``lineage``：沿 ``parent_version`` 回溯血缘链（新→旧）。
- ``get_snapshot`` / ``load_rows``：版本快照检索。

默认内存态存储（测试/合成小数据场景）；DB 持久化经构造器 ``store`` 注入位预留，
本类自身不触 DB/网络。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: store 参数
#   fields: 参数 store（无注解）
#   code: manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TrainingDatasetManager
#   name_en: TrainingDatasetManager
#   intro: 训练数据集管理器（MOD-ML-003）。
#   desc: 训练数据集管理器（MOD-ML-003）。 Parameters ---------- store : 持久化存储注入位（None=内存态）。需实现 ``save(dataset…；公共方法（定义序）: registe…
#   inputs: store
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: TrainingDatasetManager
#   downstream: MOD-ML-001 training_pipeline（load 段数据集版本锚定）；MOD-ML-009 learning_effect_feedback…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_log = logging.getLogger(__name__)


class DatasetLineageError(Exception):
    """ZA-MLT-0006: 数据集血缘/版本检索失败。"""

    error_code = "ZA-MLT-0006"


@dataclass(frozen=True)
class DatasetSnapshot:
    """数据集版本快照。"""

    dataset_id: str
    version: int
    row_count: int
    content_hash: str  # sha256 hex（canonical JSON）
    description: str
    parent_version: int | None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def _content_hash(rows: list[dict[str, Any]]) -> str:
    """canonical JSON → sha256（键排序+紧凑分隔，同内容同指纹）。"""
    blob = json.dumps(rows, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class TrainingDatasetManager:
    """训练数据集管理器（MOD-ML-003）。

    Parameters
    ----------
    store : 持久化存储注入位（None=内存态）。需实现
        ``save(dataset_id, version, rows, snapshot)`` /
        ``load(dataset_id, version)`` 两方法（duck-typing）。
    """

    def __init__(self, store: Any = None) -> None:
        self._store = store
        self._snapshots: dict[str, dict[int, DatasetSnapshot]] = {}
        self._rows: dict[tuple[str, int], list[dict[str, Any]]] = {}

    # ── 版本化登记 ───────────────────────────────────────────────────

    def register_dataset(
        self,
        dataset_id: str,
        rows: list[dict[str, Any]],
        description: str = "",
        parent_version: int | None = None,
    ) -> DatasetSnapshot:
        """登记数据集新快照（版本单调递增）。

        Raises
        ------
        ValueError
            rows 为空。
        DatasetLineageError
            parent_version 悬空（不存在的历史版本）。
        """
        if not rows:
            raise ValueError("rows 为空——数据集至少一行")
        versions = self._snapshots.setdefault(dataset_id, {})
        if parent_version is not None and parent_version not in versions:
            raise DatasetLineageError(
                f"parent_version={parent_version} 在数据集 {dataset_id!r} 历史中不存在（血缘悬空）"
            )
        version = max(versions, default=0) + 1
        snap = DatasetSnapshot(
            dataset_id=dataset_id,
            version=version,
            row_count=len(rows),
            content_hash=_content_hash(rows),
            description=description,
            parent_version=parent_version,
        )
        versions[version] = snap
        self._rows[(dataset_id, version)] = list(rows)
        if self._store is not None:
            self._store.save(dataset_id, version, rows, snap)
        _log.info("数据集登记: %s v%d rows=%d", dataset_id, version, len(rows))
        return snap

    # ── 血缘 ─────────────────────────────────────────────────────────

    def lineage(self, dataset_id: str, version: int) -> list[DatasetSnapshot]:
        """血缘链回溯（自 version 沿 parent_version 向旧，含自身）。"""
        versions = self._versions_or_raise(dataset_id)
        if version not in versions:
            raise DatasetLineageError(f"数据集 {dataset_id!r} 无 version={version}")
        chain: list[DatasetSnapshot] = []
        cur: int | None = version
        while cur is not None:
            snap = versions[cur]
            chain.append(snap)
            cur = snap.parent_version
        return chain

    def list_versions(self, dataset_id: str) -> list[DatasetSnapshot]:
        """列出版本史（升序）。"""
        versions = self._versions_or_raise(dataset_id)
        return [versions[v] for v in sorted(versions)]

    # ── 快照检索 ─────────────────────────────────────────────────────

    def get_snapshot(self, dataset_id: str, version: int) -> DatasetSnapshot:
        versions = self._versions_or_raise(dataset_id)
        if version not in versions:
            raise DatasetLineageError(f"数据集 {dataset_id!r} 无 version={version}")
        return versions[version]

    def load_rows(self, dataset_id: str, version: int) -> list[dict[str, Any]]:
        """取回快照行数据（内存态直取；注入 store 时优先 store.load）。"""
        self.get_snapshot(dataset_id, version)  # 校验存在性
        if self._store is not None:
            rows = self._store.load(dataset_id, version)
            if rows is not None:
                return rows  # type: ignore[no-any-return]
        return list(self._rows[(dataset_id, version)])

    # ── 内部 ─────────────────────────────────────────────────────────

    def _versions_or_raise(self, dataset_id: str) -> dict[int, DatasetSnapshot]:
        versions = self._snapshots.get(dataset_id)
        if not versions:
            raise DatasetLineageError(f"未知数据集: {dataset_id!r}")
        return versions


__all__ = [
    "DatasetLineageError",
    "DatasetSnapshot",
    "TrainingDatasetManager",
]
