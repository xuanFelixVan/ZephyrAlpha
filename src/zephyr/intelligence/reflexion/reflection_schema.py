# [BLUEPRINT] MOD-REFLEXION_AGENT | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/12_reflexion_multi_agent.md
# [MODULE] zephyr.intelligence.reflexion.reflection_schema
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.io.paths(MAIN_REPO_ROOT); zephyr.shared.utils.time_utils(now_utc_str)
# [CONSUMERS] zephyr.intelligence.reflexion.roles; zephyr.intelligence.reflexion.l1_reflector; zephyr.intelligence.reflexion.batch_runner
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] L1 只规则化归因(本件为 schema 层不做归因); 缺必填字段拒收(严格校验, 未知字段同拒); outcome=failure 必须带非空归因类别+非空改进建议; 落盘仅 data/brain/reflections/ jsonl 追加
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ReflectionSchemaError(ValueError) — 校验失败即抛, fail-closed
# [TESTS] tests/intelligence/test_reflexion_phase0.py
# [A_module] module_id=MOD-REFLEXION_AGENT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
反思记录 Schema —— 12号文 §4.2 P0-1 结构化反思记录契约。

定位: 自反Agent 三角色/L1~L3 反思共用的结构化记录载体(可计算机读对象,
非自由文本感想, 12号文 §3.1 Why 结构化记录)。三级共用同一套 schema。

字段(工单冻结): reflection_id / task_id / trajectory_ref / outcome(success|failure)
/ failure_category / improvement_suggestions[] / created_at / schema_version。
improvement_suggestions 元素为 ImprovementSuggestion(category/suggestion/evidence_ref),
每条建议锚定归因类别且以 evidence_ref 追溯轨迹片段(12号文 §4.2 P0-3 验收口径)。

严格校验(fail-closed): 缺必填字段/未知字段/非法 outcome/failure 缺归因或建议
→ ReflectionSchemaError。

落盘: ReflectionStore 追加写 data/brain/reflections/reflections.jsonl(每行一条),
可读回(from_dict 对称往返)。

不做什么: 不做 LLM 自由文本反思(Phase 1 才评估); 不做 L2/L3(N=5 累积/远期);
不做证据链挂接(P2-4)。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: root 参数
#   fields: 参数 root（无注解）
#   code: reflection_schema.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ImprovementSuggestion
#   name_en: ImprovementSuggestion
#   intro: 单条改进建议: 锚定归因类别 + 可追溯轨迹片段(evidence_ref 如 step[2])。
#   desc: 单条改进建议: 锚定归因类别 + 可追溯轨迹片段(evidence_ref 如 step[2])。；公共方法（定义序）: to_dict, from_dict；源码 L103-L139
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② ReflectionRecord
#   name_en: ReflectionRecord
#   intro: 结构化反思记录(三级反思共用 schema, 12号文 §3.1/§4.2 P0-1)。
#   desc: 结构化反思记录(三级反思共用 schema, 12号文 §3.1/§4.2 P0-1)。；公共方法（定义序）: to_dict, from_dict；源码 L143-L235
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ ReflectionStore
#   name_en: ReflectionStore
#   intro: 反思记录落盘器: data/brain/reflections/reflections.jsonl 追加写, 可读回。
#   desc: 反思记录落盘器: data/brain/reflections/reflections.jsonl 追加写, 可读回。；公共方法（定义序）: path, append, read_all；源码 L238-L271
#   inputs: root
#   outputs: 返回值
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: ImprovementSuggestion, ReflectionRecord, ReflectionStore
#   downstream: zephyr.intelligence.reflexion.roles; zephyr.intelligence.reflexion.l1_reflector…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Final, Literal

from zephyr.shared.io.paths import MAIN_REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc_str

SCHEMA_VERSION: Final[str] = "1.0"

Outcome = Literal["success", "failure"]
VALID_OUTCOMES: Final[frozenset[str]] = frozenset({"success", "failure"})


class ReflectionSchemaError(ValueError):
    """反思记录校验失败(缺必填字段/未知字段/非法取值)——fail-closed。"""


@dataclass(frozen=True)
class ImprovementSuggestion:
    """单条改进建议: 锚定归因类别 + 可追溯轨迹片段(evidence_ref 如 step[2])。"""

    category: str  # 锚定的归因类别(须等于所属记录的 failure_category 词表值)
    suggestion: str  # 建议内容(非空)
    evidence_ref: str  # 轨迹片段引用(非空, 如 "step[2]")

    REQUIRED_FIELDS: ClassVar[frozenset[str]] = frozenset({"category", "suggestion", "evidence_ref"})

    def __post_init__(self) -> None:
        for name in self.REQUIRED_FIELDS:
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ReflectionSchemaError(f"ImprovementSuggestion.{name} 缺失或为空(严格校验拒收): {value!r}")

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "suggestion": self.suggestion,
            "evidence_ref": self.evidence_ref,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImprovementSuggestion:
        if not isinstance(data, dict):
            raise ReflectionSchemaError(f"ImprovementSuggestion 非 dict: {type(data)!r}")
        unknown = set(data) - cls.REQUIRED_FIELDS
        if unknown:
            raise ReflectionSchemaError(f"ImprovementSuggestion 未知字段拒收: {sorted(unknown)}")
        missing = cls.REQUIRED_FIELDS - set(data)
        if missing:
            raise ReflectionSchemaError(f"ImprovementSuggestion 缺必填字段拒收: {sorted(missing)}")
        return cls(
            category=data["category"],
            suggestion=data["suggestion"],
            evidence_ref=data["evidence_ref"],
        )


@dataclass(frozen=True)
class ReflectionRecord:
    """结构化反思记录(三级反思共用 schema, 12号文 §3.1/§4.2 P0-1)。"""

    reflection_id: str  # 反思记录唯一标识
    task_id: str  # 任务标识
    trajectory_ref: str  # 执行轨迹引用(文件路径或轨迹 ID)
    outcome: Outcome  # "success" | "failure"
    failure_category: str = ""  # 归因类别(failure 必填非空; success 留空)
    improvement_suggestions: list[ImprovementSuggestion] = field(default_factory=list)
    created_at: str = ""  # ISO 时间戳, 空则构造时回填
    schema_version: str = SCHEMA_VERSION

    REQUIRED_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "reflection_id",
            "task_id",
            "trajectory_ref",
            "outcome",
            "failure_category",
            "improvement_suggestions",
            "created_at",
            "schema_version",
        }
    )

    def __post_init__(self) -> None:
        # created_at 允许构造时留空回填; 其余字符串必填字段拒空
        if not self.created_at:
            object.__setattr__(self, "created_at", now_utc_str())
        for name in ("reflection_id", "task_id", "trajectory_ref"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ReflectionSchemaError(f"ReflectionRecord.{name} 缺失或为空(严格校验拒收): {value!r}")
        if self.outcome not in VALID_OUTCOMES:
            raise ReflectionSchemaError(
                f"ReflectionRecord.outcome 非法取值拒收: {self.outcome!r}(合法={sorted(VALID_OUTCOMES)})"
            )
        if not isinstance(self.improvement_suggestions, list) or any(
            not isinstance(s, ImprovementSuggestion) for s in self.improvement_suggestions
        ):
            raise ReflectionSchemaError("ReflectionRecord.improvement_suggestions 须为 ImprovementSuggestion 列表")
        if not self.schema_version:
            raise ReflectionSchemaError("ReflectionRecord.schema_version 缺失或为空")
        if self.outcome == "failure":
            # 12号文 §4.2 P0-3 口径: 失败记录的归因分类与改进建议非空
            if not self.failure_category.strip():
                raise ReflectionSchemaError("outcome=failure 时 failure_category 必填非空(拒收)")
            if not self.improvement_suggestions:
                raise ReflectionSchemaError("outcome=failure 时 improvement_suggestions 必填非空(拒收)")
            # 每条建议锚定归因类别: category 须与记录归因类别一致
            for s in self.improvement_suggestions:
                if s.category != self.failure_category:
                    raise ReflectionSchemaError(
                        f"建议未锚定记录归因类别: suggestion.category={s.category!r}"
                        f" != failure_category={self.failure_category!r}"
                    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "reflection_id": self.reflection_id,
            "task_id": self.task_id,
            "trajectory_ref": self.trajectory_ref,
            "outcome": self.outcome,
            "failure_category": self.failure_category,
            "improvement_suggestions": [s.to_dict() for s in self.improvement_suggestions],
            "created_at": self.created_at,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReflectionRecord:
        """严格反序列化: 缺必填字段/未知字段 → ReflectionSchemaError。"""
        if not isinstance(data, dict):
            raise ReflectionSchemaError(f"ReflectionRecord 非 dict: {type(data)!r}")
        unknown = set(data) - cls.REQUIRED_FIELDS
        if unknown:
            raise ReflectionSchemaError(f"ReflectionRecord 未知字段拒收: {sorted(unknown)}")
        missing = cls.REQUIRED_FIELDS - set(data)
        if missing:
            raise ReflectionSchemaError(f"ReflectionRecord 缺必填字段拒收: {sorted(missing)}")
        raw_suggestions = data["improvement_suggestions"]
        if not isinstance(raw_suggestions, list):
            raise ReflectionSchemaError("improvement_suggestions 须为 list")
        return cls(
            reflection_id=data["reflection_id"],
            task_id=data["task_id"],
            trajectory_ref=data["trajectory_ref"],
            outcome=data["outcome"],
            failure_category=data["failure_category"],
            improvement_suggestions=[ImprovementSuggestion.from_dict(s) for s in raw_suggestions],
            created_at=data["created_at"],
            schema_version=data["schema_version"],
        )


class ReflectionStore:
    """反思记录落盘器: data/brain/reflections/reflections.jsonl 追加写, 可读回。"""

    FILE_NAME: ClassVar[str] = "reflections.jsonl"

    def __init__(self, root: Path | None = None) -> None:
        self._root = root or (MAIN_REPO_ROOT / "data" / "brain" / "reflections")
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._root / self.FILE_NAME

    def append(self, record: ReflectionRecord) -> Path:
        """追加一条记录(jsonl 一行), 返回落盘文件路径。"""
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        return self.path

    def read_all(self) -> list[ReflectionRecord]:
        """读回全部记录(严格校验, 坏行即抛)。"""
        if not self.path.exists():
            return []
        records: list[ReflectionRecord] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for line_no, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(ReflectionRecord.from_dict(json.loads(line)))
                except (json.JSONDecodeError, ReflectionSchemaError) as exc:
                    raise ReflectionSchemaError(f"{self.path} 第 {line_no} 行记录非法: {exc}") from exc
        return records
