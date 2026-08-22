# [BLUEPRINT] MOD-EVIDENCE_CHAIN | 待统筹登记（18号清单 §6 波4-11 / 11号文 §4.2 Phase 0 / apply_depgraph 设计态登记建议见 .runtime/p3_fragments/w4_11.md）
# [MODULE] zephyr.research.evidence.hypothesis_registry
# [DOMAIN] D_KNOWLEDGE  # 2026-08-22 统筹裁定：D_RESEARCH 不在 depgraph domains 表，归属 D_KNOWLEDGE（知识管理——假设/证据=知识资产）
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.io.file_utils; zephyr.shared.io.paths
# [CONSUMERS] zephyr.research.evidence.evidence_chain; zephyr.research.evidence.batch_entry; tests/research/test_evidence_phase0.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 状态机仅允许 proposed→testing→supported/refuted→archived（另含 proposed/testing→archived 中止边）；archived 为终态不可迁移不可变更；proposed→supported/refuted 直飞被拒（须过 testing）；hypothesis_id=HYP-%04d 单调递增不重号；每次迁移留痕 status_history（from/to/at/reason）；落盘原子写（tmp+os.replace），读损坏 fail-fast 不静默兜底
# [MODIFY-GUARD] tests/research/test_evidence_phase0.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] HypothesisRegistryError(ZA-RE-0001)——契约违反（空陈述/篡改归档/落盘损坏）；HypothesisNotFoundError(ZA-RE-0002)；InvalidTransitionError(ZA-RE-0003)——非法状态迁移
# [TESTS] tests/research/test_evidence_phase0.py
# [A_module] module_id=MOD-EVIDENCE_CHAIN | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""假设注册表（Hypothesis Registry）——研究证据关联组件 P0-1（11号文 §4.2）。

职责：研究假设的结构化 CRUD + 生命周期状态机 + JSON 落盘持久化。

状态机（设计真源 11号文 §3.1/P0-1）：
    proposed → testing → supported / refuted → archived
    附加中止边：proposed / testing → archived（未验证/验证中放弃归档）
    archived 为终态：不可迁出、不可变更（归档即审计封存；Phase 0 不开翻案重开边）。

Why 结构化存储而非纯文档（11号文 §3.1）：研究迭代最大的浪费是"重复验证已否定的
假设"和"忘记为什么放弃某条线"——假设必须可机读，状态机驱动后续迭代引导规则化
处理；纯文档无法规则化。

落点选择（data/research/evidence/，理由）：参照既有研究侧资产落点
data/brain/passports/（模型画像研究产物 JSON 落盘 data/brain/）；假设/证据是
**永久研究资产**（TTL permanent），.runtime 有 TTL 7d 清理 reconciler 属易失区，
严禁落永久资产；data/research/evidence/ 与 data/brain/（模型画像域）分域并列。

落盘格式：data/research/evidence/hypotheses.json
    {"schema_version": "1.0.0", "hypotheses": [Hypothesis.to_dict(), ...]}
    写入原子（zephyr.shared.io.file_utils.atomic_write：tmp + os.replace）。

频率约束（11号文 §2.3/§5-3）：本组件按日频/周频批量消费，不做盘中实时更新；
批量入口见 batch_entry.py（盘中 09:30-15:00 拒绝执行守卫）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 假设 CRUD/状态迁移请求
#   fields: create(statement/tags/notes/at)；update(hypothesis_id/statement/tags/notes/at)；transition(hypothesis_id/to_status/reason/at)
#   code: HypothesisRegistry.create / update / transition 入口
# - id: I2
#   name: 落盘快照 hypotheses.json（构造时加载）
#   fields: schema_version + hypotheses[]（Hypothesis.to_dict 行）
#   code: HypothesisRegistry._load（损坏 fail-fast ZA-RE-0001）
# 层: 算法
# - id: A1
#   name_zh: ① 状态机迁移判定+留痕
#   name_en: transition
#   desc: 目标状态词表校验 → ALLOWED_TRANSITIONS 出边判定（非法即 ZA-RE-0003）→ replace 新实例 + status_history 追加（from/to/at/reason）
#   inputs: I1
#   outputs: 迁移后 Hypothesis 新实例
# - id: A2
#   name_zh: ② 原子快照落盘
#   name_en: _save
#   desc: 全量快照 JSON 经 atomic_write（tmp+os.replace）写 hypotheses.json；create/update/transition 每步变更即落盘
#   inputs: A1 及 CRUD 变更结果
#   outputs: hypotheses.json 落盘文件
# 层: 输出
# - id: O1
#   name_zh: Hypothesis 值对象与查询视图
#   name_en: create/get/list_all/update/transition 返回值
#   downstream: zephyr.research.evidence.evidence_chain（外键真源）；zephyr.research.evidence.batch_entry；tests/research/test_evidence_phase0.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1（加载重建内存表后服务迁移判定）
# A1 --> A2
# A2 --> O1

依据: 11号文 §3.1/§4.2 P0-1 + 18号清单 §6 波4-11
Version: 0.1.0
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.file_utils import atomic_write
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "ALLOWED_TRANSITIONS",
    "DEFAULT_STORE_DIR",
    "Hypothesis",
    "HypothesisNotFoundError",
    "HypothesisRegistry",
    "HypothesisRegistryError",
    "HypothesisStatus",
    "InvalidTransitionError",
]

log = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约（ZA-RE-0001~0003）
# ============================================================================


class HypothesisRegistryError(ZephyrBaseError):
    """ZA-RE-0001: 假设注册表基础错误（契约违反/落盘损坏）。"""

    error_code = "ZA-RE-0001"


class HypothesisNotFoundError(HypothesisRegistryError):
    """ZA-RE-0002: 指定 hypothesis_id 不存在。"""

    error_code = "ZA-RE-0002"


class InvalidTransitionError(HypothesisRegistryError):
    """ZA-RE-0003: 非法状态迁移（违反状态机允许边）。"""

    error_code = "ZA-RE-0003"


# ============================================================================
# 2. 常量与状态机
# ============================================================================

#: 中国标准时间（无夏令时）——落盘时间戳统一口径
CST: Final = timezone(timedelta(hours=8))

#: 默认落盘根（选择理由见模块 docstring"落点选择"段）
DEFAULT_STORE_DIR: Final[Path] = REPO_ROOT / "data" / "research" / "evidence"
HYPOTHESES_FILENAME: Final = "hypotheses.json"
SCHEMA_VERSION: Final = "1.0.0"
HYPOTHESIS_ID_PREFIX: Final = "HYP-"


class HypothesisStatus(str, Enum):
    """假设生命周期五态（11号文 §3.1）。"""

    PROPOSED = "proposed"
    TESTING = "testing"
    SUPPORTED = "supported"
    REFUTED = "refuted"
    ARCHIVED = "archived"


#: 状态机允许迁移边（终态 archived 无出边；proposed→supported/refuted 直飞须过 testing）
ALLOWED_TRANSITIONS: Final[dict[HypothesisStatus, frozenset[HypothesisStatus]]] = {
    HypothesisStatus.PROPOSED: frozenset({HypothesisStatus.TESTING, HypothesisStatus.ARCHIVED}),
    HypothesisStatus.TESTING: frozenset(
        {HypothesisStatus.SUPPORTED, HypothesisStatus.REFUTED, HypothesisStatus.ARCHIVED}
    ),
    HypothesisStatus.SUPPORTED: frozenset({HypothesisStatus.ARCHIVED}),
    HypothesisStatus.REFUTED: frozenset({HypothesisStatus.ARCHIVED}),
    HypothesisStatus.ARCHIVED: frozenset(),
}


def _now() -> datetime:
    return datetime.now(CST)


# ============================================================================
# 3. 假设条目
# ============================================================================


@dataclass(frozen=True)
class Hypothesis:
    """研究假设条目（不可变值对象——变更经 replace 产出新实例）。"""

    hypothesis_id: str
    statement: str
    status: HypothesisStatus
    proposed_at: str  # ISO 8601（CST）
    updated_at: str  # ISO 8601（CST）
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    status_history: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "statement": self.statement,
            "status": self.status.value,
            "proposed_at": self.proposed_at,
            "updated_at": self.updated_at,
            "tags": list(self.tags),
            "notes": self.notes,
            "status_history": [dict(e) for e in self.status_history],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hypothesis:
        return cls(
            hypothesis_id=str(data["hypothesis_id"]),
            statement=str(data["statement"]),
            status=HypothesisStatus(data["status"]),
            proposed_at=str(data["proposed_at"]),
            updated_at=str(data["updated_at"]),
            tags=[str(t) for t in data.get("tags", [])],
            notes=str(data.get("notes", "")),
            status_history=[dict(e) for e in data.get("status_history", [])],
        )


# ============================================================================
# 4. 注册表
# ============================================================================


class HypothesisRegistry:
    """假设注册表——CRUD + 状态机迁移 + JSON 落盘（单写者假设，见 docstring 落点段）。

    Args:
        store_dir: 落盘目录；None → DEFAULT_STORE_DIR（data/research/evidence/）。
    """

    def __init__(self, store_dir: Path | str | None = None) -> None:
        self._store_dir = Path(store_dir) if store_dir is not None else DEFAULT_STORE_DIR
        self._path = self._store_dir / HYPOTHESES_FILENAME
        self._items: dict[str, Hypothesis] = {}
        self._load()

    # ── 持久化 ────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self._path.exists():
            return  # fresh boot：空注册表
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            rows = payload["hypotheses"]
            items = [Hypothesis.from_dict(r) for r in rows]
        except HypothesisRegistryError:
            raise
        except Exception as exc:  # JSONDecodeError/KeyError/TypeError/ValueError
            raise HypothesisRegistryError(
                f"假设注册表落盘损坏，fail-fast（不静默兜底为空表）: {self._path}",
                details={"path": str(self._path), "cause": repr(exc)},
            ) from exc
        self._items = {h.hypothesis_id: h for h in items}
        if len(self._items) != len(items):
            raise HypothesisRegistryError(
                f"假设注册表存在重复 hypothesis_id: {self._path}",
                details={"path": str(self._path)},
            )

    def _save(self) -> None:
        self._store_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "hypotheses": [h.to_dict() for h in self.list_all()],
        }
        atomic_write(self._path, json.dumps(payload, ensure_ascii=False, indent=2))

    def _next_id(self) -> str:
        seq = 0
        for hid in self._items:
            if hid.startswith(HYPOTHESIS_ID_PREFIX):
                try:
                    seq = max(seq, int(hid[len(HYPOTHESIS_ID_PREFIX) :]))
                except ValueError:
                    continue
        return f"{HYPOTHESIS_ID_PREFIX}{seq + 1:04d}"

    # ── CRUD ──────────────────────────────────────────────────────────────

    def create(
        self,
        statement: str,
        *,
        tags: list[str] | None = None,
        notes: str = "",
        at: datetime | None = None,
    ) -> Hypothesis:
        """新建假设（初始状态 proposed）。"""
        if not statement or not statement.strip():
            raise HypothesisRegistryError("假设陈述为空——契约违反（statement 必填非空白）")
        now = (at or _now()).isoformat()
        h = Hypothesis(
            hypothesis_id=self._next_id(),
            statement=statement.strip(),
            status=HypothesisStatus.PROPOSED,
            proposed_at=now,
            updated_at=now,
            tags=list(tags or []),
            notes=notes,
        )
        self._items[h.hypothesis_id] = h
        self._save()
        log.info("假设立项 %s（proposed）", h.hypothesis_id)
        return h

    def get(self, hypothesis_id: str) -> Hypothesis:
        try:
            return self._items[hypothesis_id]
        except KeyError:
            raise HypothesisNotFoundError(
                f"假设不存在: {hypothesis_id}",
                details={"hypothesis_id": hypothesis_id},
            ) from None

    def list_all(self, status: HypothesisStatus | None = None) -> list[Hypothesis]:
        """全量/按状态过滤列出（按 hypothesis_id 升序=立项序）。"""
        items = sorted(self._items.values(), key=lambda h: h.hypothesis_id)
        if status is not None:
            items = [h for h in items if h.status is status]
        return items

    def update(
        self,
        hypothesis_id: str,
        *,
        statement: str | None = None,
        tags: list[str] | None = None,
        notes: str | None = None,
        at: datetime | None = None,
    ) -> Hypothesis:
        """更新元数据（statement/tags/notes）。archived 终态不可变更（保审计封存）。"""
        h = self.get(hypothesis_id)
        if h.status is HypothesisStatus.ARCHIVED:
            raise HypothesisRegistryError(
                f"archived 终态假设不可变更: {hypothesis_id}",
                details={"hypothesis_id": hypothesis_id, "status": h.status.value},
            )
        if statement is not None and not statement.strip():
            raise HypothesisRegistryError("假设陈述为空——契约违反（statement 必填非空白）")
        h = replace(
            h,
            statement=statement.strip() if statement is not None else h.statement,
            tags=list(tags) if tags is not None else h.tags,
            notes=notes if notes is not None else h.notes,
            updated_at=(at or _now()).isoformat(),
        )
        self._items[hypothesis_id] = h
        self._save()
        return h

    # ── 状态机 ────────────────────────────────────────────────────────────

    def transition(
        self,
        hypothesis_id: str,
        to_status: HypothesisStatus | str,
        *,
        reason: str = "",
        at: datetime | None = None,
    ) -> Hypothesis:
        """状态迁移——仅允许 ALLOWED_TRANSITIONS 内边；非法迁移抛 InvalidTransitionError。"""
        h = self.get(hypothesis_id)
        try:
            target = HypothesisStatus(to_status)
        except ValueError:
            raise InvalidTransitionError(
                f"未知目标状态: {to_status!r}（词表：proposed/testing/supported/refuted/archived）",
                details={"hypothesis_id": hypothesis_id, "to_status": str(to_status)},
            ) from None
        allowed = ALLOWED_TRANSITIONS[h.status]
        if target not in allowed:
            raise InvalidTransitionError(
                f"非法状态迁移: {h.status.value} → {target.value}"
                f"（允许出边：{sorted(s.value for s in allowed) or '无——终态'}）",
                details={
                    "hypothesis_id": hypothesis_id,
                    "from_status": h.status.value,
                    "to_status": target.value,
                },
            )
        now = (at or _now()).isoformat()
        h = replace(
            h,
            status=target,
            updated_at=now,
            status_history=[
                *h.status_history,
                {"from": h.status.value, "to": target.value, "at": now, "reason": reason},
            ],
        )
        self._items[hypothesis_id] = h
        self._save()
        log.info("假设 %s 状态迁移 %s → %s（%s）", hypothesis_id, h.status_history[-1]["from"], target.value, reason)
        return h
