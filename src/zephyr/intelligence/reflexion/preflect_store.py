# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md | §4.3-P1-3
# [MODULE] zephyr.intelligence.reflexion.preflect_store
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.reflexion.reflection_schema(ReflectionRecord); zephyr.shared.io.paths(MAIN_REPO_ROOT); zephyr.shared.utils.time_utils(now_utc_str)
# [CONSUMERS] tests/intelligence/test_preflect_store.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 条目四要素冻结(模式/触发条件/规避建议/来源反思 ID); 严格校验 fail-closed(缺必填字段/未知字段/空模式/空建议/重复编号拒收); 仅失败反思记录可入库; 人工编辑 editor 必填留痕且 source 转 manual_edit; 被停用条目不命中检索; 注入载荷恒带来源反思 ID
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PreFlectSchemaError(ValueError) — 校验失败即抛, fail-closed; 错误消息零 session_id
# [TESTS] tests/intelligence/test_preflect_store.py
# [A_module] module_id=MOD-REFLEXION_AGENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PreFlect 失败模式库（12号文 §3.3/§4.3 P1-3）.

定位：一本「死法大全」——每条失败模式条目写清楚失败长什么样（pattern）、什么
情况下会再犯（trigger_conditions）、怎么躲开（avoidance_advice）、是哪次反思
沉淀下来的（source_reflection_ids）。新任务开工前按任务文案检索命中条目，把
「上次怎么死的」提前摆进上下文（build_injection 载荷恒带来源反思 ID 可追溯）。

入库双通道：
- ingest_reflection：消费 L2 产出的失败反思记录（ReflectionRecord outcome=failure）
  自动生成条目落盘；成功记录拒收（仅失败反思记录可入库）。
- add：人工种子集直接落条目（12号文 §6 Q6 形态——source=manual_seed 豁免来源
  反思 ID；Q6 本身仍待 Owner 裁定，本件仅作可选 source 值不代拍板启用）。

人工编辑：edit 接口 editor 必填留痕，编辑后 source 转 manual_edit、updated_at
刷新；可停用条目（enabled=False 后检索不再命中）。

检索：规则化关键词重叠打分（trigger_conditions 子串命中计数，与 L1 归因同路线，
不引嵌入模型）。落盘：root/preflect_patterns.json 原子写，可读回（严格校验）。
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, ClassVar, Final

from zephyr.intelligence.reflexion.reflection_schema import ReflectionRecord
from zephyr.shared.io.paths import MAIN_REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc_str

logger = logging.getLogger(__name__)

# ── 条目来源取值（12号文 §3.3/§6 Q6） ─────────────────────────
SOURCE_L2: Final[str] = "l2_reflection"  # L2 失败反思记录自动沉淀
SOURCE_MANUAL_SEED: Final[str] = "manual_seed"  # 人工种子集（Q6 待裁定，仅作可选值）
SOURCE_MANUAL_EDIT: Final[str] = "manual_edit"  # 人工编辑留痕

VALID_SOURCES: Final[frozenset[str]] = frozenset(
    {SOURCE_L2, SOURCE_MANUAL_SEED, SOURCE_MANUAL_EDIT}
)

_STORE_FILE: Final[str] = "preflect_patterns.json"


class PreFlectSchemaError(ValueError):
    """失败模式条目校验失败（缺必填字段/未知字段/非法取值）——fail-closed."""


@dataclass(frozen=True)
class FailurePatternEntry:
    """失败模式条目（§3.3 四要素冻结：模式/触发条件/规避建议/来源反思 ID）."""

    pattern_id: str  # 条目唯一标识
    pattern: str  # 失败模式描述（非空）
    trigger_conditions: tuple[str, ...]  # 触发条件关键词组（非空，检索命中面）
    avoidance_advice: str  # 规避建议（非空）
    source_reflection_ids: tuple[str, ...]  # 来源反思 ID（L2 入库必填非空）
    source: str  # l2_reflection | manual_seed | manual_edit
    enabled: bool = True  # 停用后检索不再命中
    created_at: str = ""  # ISO 时间戳，空则构造时回填
    updated_at: str = ""  # ISO 时间戳，空则构造时回填

    REQUIRED_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "pattern_id",
            "pattern",
            "trigger_conditions",
            "avoidance_advice",
            "source_reflection_ids",
            "source",
            "enabled",
            "created_at",
            "updated_at",
        }
    )

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(self, "created_at", now_utc_str())
        if not self.updated_at:
            object.__setattr__(self, "updated_at", self.created_at)
        if not isinstance(self.pattern_id, str) or not self.pattern_id.strip():
            raise PreFlectSchemaError(
                f"FailurePatternEntry.pattern_id 缺失或为空（严格校验拒收）: {self.pattern_id!r}"
            )
        if not isinstance(self.pattern, str) or not self.pattern.strip():
            raise PreFlectSchemaError(
                f"FailurePatternEntry.pattern 缺失或为空（严格校验拒收）: {self.pattern!r}"
            )
        if not isinstance(self.avoidance_advice, str) or not self.avoidance_advice.strip():
            raise PreFlectSchemaError(
                "FailurePatternEntry.avoidance_advice 缺失或为空（严格校验拒收）: "
                f"{self.avoidance_advice!r}"
            )
        conditions = tuple(self.trigger_conditions)
        if not conditions or any(
            not isinstance(c, str) or not c.strip() for c in conditions
        ):
            raise PreFlectSchemaError(
                "FailurePatternEntry.trigger_conditions 缺失或含空项（严格校验拒收）: "
                f"{self.trigger_conditions!r}"
            )
        object.__setattr__(self, "trigger_conditions", conditions)
        reflection_ids = tuple(self.source_reflection_ids)
        object.__setattr__(self, "source_reflection_ids", reflection_ids)
        if self.source not in VALID_SOURCES:
            raise PreFlectSchemaError(
                f"FailurePatternEntry.source 非法取值拒收: {self.source!r}"
                f"（合法={sorted(VALID_SOURCES)}）"
            )
        if self.source == SOURCE_L2 and not reflection_ids:
            raise PreFlectSchemaError(
                "FailurePatternEntry.source_reflection_ids 缺失：L2 入库必须带来源反思 ID"
                "（manual_seed 方可豁免）"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern": self.pattern,
            "trigger_conditions": list(self.trigger_conditions),
            "avoidance_advice": self.avoidance_advice,
            "source_reflection_ids": list(self.source_reflection_ids),
            "source": self.source,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FailurePatternEntry:
        """严格反序列化：缺必填字段/未知字段 → PreFlectSchemaError."""
        if not isinstance(data, dict):
            raise PreFlectSchemaError(f"FailurePatternEntry 非 dict: {type(data)!r}")
        unknown = set(data) - cls.REQUIRED_FIELDS
        if unknown:
            raise PreFlectSchemaError(f"FailurePatternEntry 未知字段拒收: {sorted(unknown)}")
        missing = cls.REQUIRED_FIELDS - set(data)
        if missing:
            raise PreFlectSchemaError(f"FailurePatternEntry 缺必填字段拒收: {sorted(missing)}")
        return cls(
            pattern_id=data["pattern_id"],
            pattern=data["pattern"],
            trigger_conditions=tuple(data["trigger_conditions"]),
            avoidance_advice=data["avoidance_advice"],
            source_reflection_ids=tuple(data["source_reflection_ids"]),
            source=data["source"],
            enabled=bool(data["enabled"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )


class PreFlectStore:
    """失败模式库：落盘 root/preflect_patterns.json，可读回."""

    def __init__(self, root: str | Path | None = None) -> None:
        self._root = (
            Path(root)
            if root
            else MAIN_REPO_ROOT / "data" / "brain" / "preflect"
        )
        self._root.mkdir(parents=True, exist_ok=True)
        self._entries: dict[str, FailurePatternEntry] = {}
        self._load()

    @property
    def path(self) -> Path:
        return self._root / _STORE_FILE

    # ── 入库 ──────────────────────────────────────────────────

    def add(self, entry: FailurePatternEntry) -> FailurePatternEntry:
        """人工种子集/外部构造条目直接入库；重复 pattern_id 拒收."""
        if entry.pattern_id in self._entries:
            raise PreFlectSchemaError(
                f"FailurePatternEntry.pattern_id 重复拒收: {entry.pattern_id!r}"
            )
        self._entries[entry.pattern_id] = entry
        self._persist()
        return entry

    def ingest_reflection(self, record: ReflectionRecord) -> FailurePatternEntry:
        """消费 L2 失败反思记录自动生成条目落盘；成功记录拒收."""
        if record.outcome != "failure":
            raise PreFlectSchemaError(
                f"仅失败反思记录可入库: outcome={record.outcome!r}（拒收）"
            )
        entry = FailurePatternEntry(
            pattern_id=f"fp-{record.reflection_id}",
            pattern=record.failure_category,
            trigger_conditions=(record.failure_category,),
            avoidance_advice="；".join(
                s.suggestion for s in record.improvement_suggestions
            ),
            source_reflection_ids=(record.reflection_id,),
            source=SOURCE_L2,
        )
        return self.add(entry)

    def get(self, pattern_id: str) -> FailurePatternEntry | None:
        return self._entries.get(pattern_id)

    # ── 人工编辑 ──────────────────────────────────────────────

    def edit(
        self,
        pattern_id: str,
        *,
        editor: str,
        pattern: str | None = None,
        avoidance_advice: str | None = None,
        trigger_conditions: tuple[str, ...] | None = None,
        enabled: bool | None = None,
    ) -> FailurePatternEntry:
        """人工编辑：editor 必填留痕；编辑后 source 转 manual_edit、updated_at 刷新."""
        if not str(editor or "").strip():
            raise PreFlectSchemaError("edit 须署名：editor 不能为空（人工编辑留痕）")
        entry = self._entries.get(pattern_id)
        if entry is None:
            raise PreFlectSchemaError(f"edit 未知 pattern_id 拒收: {pattern_id!r}")
        edited = replace(
            entry,
            pattern=entry.pattern if pattern is None else pattern,
            avoidance_advice=(
                entry.avoidance_advice if avoidance_advice is None else avoidance_advice
            ),
            trigger_conditions=(
                entry.trigger_conditions
                if trigger_conditions is None
                else tuple(trigger_conditions)
            ),
            enabled=entry.enabled if enabled is None else bool(enabled),
            source=SOURCE_MANUAL_EDIT,
            updated_at=now_utc_str(),
        )
        self._entries[pattern_id] = edited
        self._persist()
        return edited

    # ── 检索与注入 ────────────────────────────────────────────

    def retrieve(self, task_text: str) -> list[FailurePatternEntry]:
        """按任务文案检索命中条目（trigger_conditions 子串重叠打分，停用条目不命中）."""
        text = str(task_text or "")
        scored: list[tuple[int, FailurePatternEntry]] = []
        for entry in self._entries.values():
            if not entry.enabled:
                continue
            score = sum(1 for cond in entry.trigger_conditions if cond and cond in text)
            if score > 0:
                scored.append((score, entry))
        scored.sort(key=lambda item: (-item[0], item[1].pattern_id))
        return [entry for _, entry in scored]

    def build_injection(self, task_text: str) -> dict[str, Any]:
        """任务启动时构建注入载荷：命中条目 + 来源反思 ID 汇总（可追溯）."""
        hits = self.retrieve(task_text)
        source_ids: set[str] = set()
        for entry in hits:
            source_ids.update(entry.source_reflection_ids)
        return {
            "entries": [entry.to_dict() for entry in hits],
            "source_reflection_ids": sorted(source_ids),
        }

    # ── 落盘 ──────────────────────────────────────────────────

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise PreFlectSchemaError(f"{self.path} 非法 JSON（fail-closed）: {exc}") from exc
        if not isinstance(raw, dict):
            raise PreFlectSchemaError(f"{self.path} 顶层须为 dict（fail-closed）: {type(raw)!r}")
        self._entries = {
            pattern_id: FailurePatternEntry.from_dict(data)
            for pattern_id, data in raw.items()
        }

    def _persist(self) -> None:
        payload = {pid: entry.to_dict() for pid, entry in sorted(self._entries.items())}
        tmp_path = self.path.with_suffix(self.path.suffix + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.replace(tmp_path, self.path)
        except OSError as exc:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise PreFlectSchemaError(f"{self.path} 落盘失败: {exc!r}") from exc


__all__ = [
    "SOURCE_L2",
    "SOURCE_MANUAL_EDIT",
    "SOURCE_MANUAL_SEED",
    "VALID_SOURCES",
    "FailurePatternEntry",
    "PreFlectSchemaError",
    "PreFlectStore",
]
