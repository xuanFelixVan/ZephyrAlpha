# [BLUEPRINT] MOD-DATA_GOV-008 | docs/03_modules/_domain_data_governance/record_lineage_tracker/blueprint.md
# [MODULE] zephyr.data_governance.core.record_lineage_tracker
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 必填字段空 Fail-Closed; 同 batch_id 同内容重放幂等; 同 batch_id 异内容 Fail-Closed(防溯源漂移); sidecar 原子写(tmp+os.replace); 坏行 Fail-Closed; 不重复存因子值(offline_store 职责)
# [MODIFY-GUARD] tests/data_governance/test_record_lineage_tracker.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RecordLineageError(未登记错误码-申请中)
# [TESTS] tests/data_governance/test_record_lineage_tracker.py
# [A_module] module_id=MOD-DATA_GOV-008 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
M8-NEW-09 Metaxy Record-Level Tracker（MOD-DATA_GOV-008）。

真源：construction_backlog_dig.tsv B13-04278（A3 数据架构 §17.2，裁定=做 P1）
+ CAND-DATGOV-005。

定位：列级血缘（B13-04276 / MOD-DATA_GOV-007）覆盖 SQL 变换，特征值**记录级**
（source_file + transform + code_version + computed_at）血缘未建，因子审计追溯
断链（TSV 现状）。本模块为每特征批次登记溯源元数据写 **sidecar 元数据表**
（JSONL），支持单条因子值反查原始行情行。

与 B13-04144 离线仓 7 列 Schema 联动（MOD-L02-001 offline_store）：batch_id 对齐
其内容寻址批文件名（batch_<sha256[:16]>，去 .parquet），**只引用约定不重算摘要、
不重复存因子值**；批次 Parquet 写归 OfflineStore，本模块只管 sidecar 元数据
原子写（tmp+os.replace，对齐其原子写哲学）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: sidecar_path 参数
#   fields: 参数 sidecar_path（无注解）
#   code: record_lineage_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① RecordLineageTracker
#   name_en: RecordLineageTracker
#   intro: 记录级血缘台账——批次溯源登记/反查 + sidecar JSONL 持久化。
#   desc: 记录级血缘台账——批次溯源登记/反查 + sidecar JSONL 持久化。 幂等哲学对齐 MOD-DATA_GOV-002（同键重放幂等）；同键异内容 Fail-Closed…；公共方法（定义序）: registe…
#   inputs: sidecar_path
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: RecordLineageTracker
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Final

__all__: Final = [
    "FeatureBatchProvenance",
    "RecordLineageError",
    "RecordLineageTracker",
]

_log = logging.getLogger(__name__)


class RecordLineageError(ValueError):
    """记录级血缘台账输入/持久化非法（Fail-Closed；未登记错误码-申请中）。"""


@dataclass(frozen=True)
class FeatureBatchProvenance:
    """特征批次溯源记录（不可变）。

    Attributes:
        batch_id: 批次标识（对齐离线仓内容寻址批文件名 batch_<sha256[:16]>）
        factor_name: 因子名
        source_files: 原始行情来源文件（反查原始行情行的落点）
        transform: 变换描述（计算逻辑标识）
        code_version: 代码版本（git 提交/发布号）
        computed_at: 计算时间（ISO 字符串）
        trade_dates: 覆盖交易日（反查索引维度）
        row_count: 批次行数
    """

    batch_id: str
    factor_name: str
    source_files: tuple[str, ...]
    transform: str
    code_version: str
    computed_at: str
    trade_dates: tuple[str, ...] = ()
    row_count: int = 0


def _validate_text(value: str, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RecordLineageError(f"必填字段为空: {field_name}={value!r}")
    return value.strip()


def _validate_provenance(prov: FeatureBatchProvenance) -> FeatureBatchProvenance:
    """必填字段校验（Fail-Closed）。"""
    if not isinstance(prov, FeatureBatchProvenance):
        raise RecordLineageError(f"provenance 类型非法: {type(prov).__name__}")
    _validate_text(prov.batch_id, field_name="batch_id")
    _validate_text(prov.factor_name, field_name="factor_name")
    _validate_text(prov.transform, field_name="transform")
    _validate_text(prov.code_version, field_name="code_version")
    _validate_text(prov.computed_at, field_name="computed_at")
    if not prov.source_files:
        raise RecordLineageError("source_files 为空（无法反查原始行情行）")
    for src in prov.source_files:
        _validate_text(src, field_name="source_files[]")
    for td in prov.trade_dates:
        _validate_text(td, field_name="trade_dates[]")
    if not isinstance(prov.row_count, int) or prov.row_count < 0:
        raise RecordLineageError(f"row_count 必须为非负整数: {prov.row_count!r}")
    return prov


class RecordLineageTracker:
    """记录级血缘台账——批次溯源登记/反查 + sidecar JSONL 持久化。

    幂等哲学对齐 MOD-DATA_GOV-002（同键重放幂等）；同键异内容 Fail-Closed
    （溯源漂移不容静默覆盖）。
    """

    def __init__(self, sidecar_path: str | Path | None = None) -> None:
        self._sidecar_path = Path(sidecar_path) if sidecar_path is not None else None
        self._by_batch: dict[str, FeatureBatchProvenance] = {}
        self._by_factor_date: dict[tuple[str, str], list[str]] = {}

    def register(self, provenance: FeatureBatchProvenance) -> bool:
        """登记批次溯源（True=新登记；False=同内容重放幂等；同键异内容 Fail-Closed）。"""
        prov = _validate_provenance(provenance)
        existing = self._by_batch.get(prov.batch_id)
        if existing is not None:
            if existing == prov:
                return False
            raise RecordLineageError(f"batch_id {prov.batch_id!r} 已登记且内容不一致（溯源漂移 Fail-Closed）")
        self._by_batch[prov.batch_id] = prov
        for trade_date in prov.trade_dates:
            self._by_factor_date.setdefault((prov.factor_name, trade_date), []).append(prov.batch_id)
        return True

    def get(self, batch_id: str) -> FeatureBatchProvenance | None:
        """按批次标识查溯源记录（未知返回 None）。"""
        _validate_text(batch_id, field_name="batch_id")
        return self._by_batch.get(batch_id.strip())

    def backtrack(self, factor_name: str, trade_date: str) -> list[FeatureBatchProvenance]:
        """单条因子值反查：(factor_name, trade_date) → 批次溯源列表（source_files 落点）。"""
        factor = _validate_text(factor_name, field_name="factor_name")
        date = _validate_text(trade_date, field_name="trade_date")
        return [self._by_batch[bid] for bid in self._by_factor_date.get((factor, date), [])]

    def flush(self) -> int:
        """sidecar JSONL 原子写（tmp+os.replace；无 sidecar 路径 Fail-Closed）。"""
        if self._sidecar_path is None:
            raise RecordLineageError("未配置 sidecar_path（纯内存台账不支持 flush）")
        records = sorted(self._by_batch.values(), key=lambda p: p.batch_id)
        payload = "".join(json.dumps(asdict(prov), ensure_ascii=False, sort_keys=True) + "\n" for prov in records)
        self._sidecar_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self._sidecar_path.with_suffix(self._sidecar_path.suffix + ".tmp")
        tmp_path.write_text(payload, encoding="utf-8")
        os.replace(tmp_path, self._sidecar_path)
        return len(records)

    @classmethod
    def load(cls, sidecar_path: str | Path) -> RecordLineageTracker:
        """sidecar JSONL 读回重建台账（坏行/缺文件 Fail-Closed）。"""
        path = Path(sidecar_path)
        if not path.exists():
            raise RecordLineageError(f"sidecar 文件不存在: {path}")
        tracker = cls(path)
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                prov = FeatureBatchProvenance(
                    batch_id=raw["batch_id"],
                    factor_name=raw["factor_name"],
                    source_files=tuple(raw["source_files"]),
                    transform=raw["transform"],
                    code_version=raw["code_version"],
                    computed_at=raw["computed_at"],
                    trade_dates=tuple(raw.get("trade_dates", ())),
                    row_count=raw.get("row_count", 0),
                )
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                raise RecordLineageError(f"sidecar 坏行 @{lineno}（Fail-Closed 不静默错读）: {exc}") from exc
            tracker.register(prov)
        return tracker

    def provenances(self) -> Sequence[FeatureBatchProvenance]:
        """全部溯源记录（batch_id 序，只读快照）。"""
        return tuple(self._by_batch[bid] for bid in sorted(self._by_batch))
