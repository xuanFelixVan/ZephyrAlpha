# [BLUEPRINT] MOD-EVIDENCE_CHAIN | 待统筹登记（18号清单 §6 波4-11 / 11号文 §4.2 Phase 0 / apply_depgraph 设计态登记建议见 .runtime/p3_fragments/w4_11.md）
# [MODULE] zephyr.research.evidence.evidence_chain
# [DOMAIN] D_KNOWLEDGE  # 2026-08-22 统筹裁定：D_RESEARCH 不在 depgraph domains 表，归属 D_KNOWLEDGE（知识管理——假设/证据=知识资产）
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.io.paths; zephyr.research.evidence.hypothesis_registry
# [CONSUMERS] zephyr.research.evidence.batch_entry; tests/research/test_evidence_phase0.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 证据 append-only 只增不改不删（持续生长语义，11号文 §3.1）；polarity ∈ {support, contradict, neutral} 三态词表，词表外取值拒绝；hypothesis_id 外键必须已存在于假设注册表（拒挂孤儿证据）；每条 content_hash=SHA-256(规范化 JSON) 落盘固化，verify_integrity 重算不一致即 EvidenceIntegrityError；jsonl 任一行不可解析 fail-fast（篡改/损坏不静默跳过）
# [MODIFY-GUARD] tests/research/test_evidence_phase0.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EvidenceChainError(ZA-RE-0010)——基础错误（落盘损坏 fail-fast）；UnknownHypothesisError(ZA-RE-0011)——外键约束；InvalidPolarityError(ZA-RE-0012)——三态词表外；EvidenceIntegrityError(ZA-RE-0013)——hash 重算不一致（篡改检出）
# [TESTS] tests/research/test_evidence_phase0.py
# [A_module] module_id=MOD-EVIDENCE_CHAIN | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""证据链（Evidence Chain）——研究证据关联组件 P0-2（11号文 §4.2）。

职责：证据条目的三态挂链（支持/反驳/中性）+ 来源 + 日期 + 假设外键 + 完整性
hash 固化防篡改，append-only jsonl 落盘。

证据条目：
    evidence_id（EV-%04d 单调递增）/ hypothesis_id（外键 → 假设注册表）/
    polarity（support | contradict | neutral 三态）/ source（来源）/
    content（内容）/ created_at（ISO 8601 CST）/ content_hash（SHA-256 固化）

防篡改设计（11号文 §3.1"借鉴但不复用 governance EvidencePack"）：
    借鉴审计证据包的 hash 完整性模式——每条证据落盘时以 SHA-256 固化
    （覆盖 evidence_id/hypothesis_id/polarity/source/content/created_at 六字段
    的规范化 JSON）；verify_integrity() 全量重算，任一不一致即
    EvidenceIntegrityError。语义差异：审计包是"打包封存"，本链是"持续生长"
    （append-only），域不同不复用其类（11号文 §2.1 划界）。

落盘格式：data/research/evidence/evidence_chain.jsonl（一行一条目，UTF-8）。
    落点选择理由见 hypothesis_registry.py docstring"落点选择"段。

频率约束（11号文 §2.3/§5-3）：日频/周频批量写入，不做盘中实时更新。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 证据挂链请求
#   fields: hypothesis_id（外键）/polarity（三态）/source/content/at
#   code: EvidenceChain.append 入口
# - id: I2
#   name: 落盘 evidence_chain.jsonl（构造时加载）
#   fields: 每行一条 EvidenceEntry.to_dict（含 content_hash）
#   code: EvidenceChain._load（任一行不可解析 fail-fast ZA-RE-0010）
# 层: 算法
# - id: A1
#   name_zh: ① 外键+三态词表校验
#   name_en: append 前置判定
#   desc: registry.get 外键存在性（缺失即 ZA-RE-0011）→ EvidencePolarity 词表校验（越表即 ZA-RE-0012）
#   inputs: I1
#   outputs: 合法挂链请求
# - id: A2
#   name_zh: ② hash 固化+append-only 落盘
#   name_en: compute_entry_hash + _append_line
#   desc: 六字段规范化 JSON 的 SHA-256 固化进 content_hash → jsonl 单行追加（flush+fsync）
#   inputs: A1
#   outputs: EvidenceEntry（落盘固化）
# - id: A3
#   name_zh: ③ 完整性重算校验
#   name_en: verify_integrity
#   desc: 全量条目重算 hash 与落盘值比对，任一不一致即 ZA-RE-0013（篡改检出）
#   inputs: I2 加载结果
#   outputs: 通过/raise
# 层: 输出
# - id: O1
#   name_zh: 证据条目/聚合视图
#   name_en: list_for / summary_for（EvidenceSummary）/ iter_all
#   downstream: zephyr.research.evidence.iteration_guide（EvidenceSummary 消费）；zephyr.research.evidence.batch_entry；tests/research/test_evidence_phase0.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A3
# A2 --> O1
# A3 --> O1

依据: 11号文 §3.1/§4.2 P0-2 + 18号清单 §6 波4-11
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Final, Iterator

from zephyr.research.evidence.hypothesis_registry import (
    CST,
    DEFAULT_STORE_DIR,
    HypothesisNotFoundError,
    HypothesisRegistry,
)
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT  # noqa: F401  # 供 DEFAULT_STORE_DIR 同源复用

__all__: Final = [
    "EvidenceChain",
    "EvidenceChainError",
    "EvidenceEntry",
    "EvidenceIntegrityError",
    "EvidencePolarity",
    "EvidenceSummary",
    "InvalidPolarityError",
    "UnknownHypothesisError",
    "compute_entry_hash",
]

log = logging.getLogger(__name__)

# ============================================================================
# 1. 错误契约（ZA-RE-0010~0013）
# ============================================================================


class EvidenceChainError(ZephyrBaseError):
    """ZA-RE-0010: 证据链基础错误（落盘损坏 fail-fast）。"""

    error_code = "ZA-RE-0010"


class UnknownHypothesisError(EvidenceChainError):
    """ZA-RE-0011: 证据挂接的 hypothesis_id 不存在（外键约束违反）。"""

    error_code = "ZA-RE-0011"


class InvalidPolarityError(EvidenceChainError):
    """ZA-RE-0012: 证据极性取值越出三态词表（support/contradict/neutral）。"""

    error_code = "ZA-RE-0012"


class EvidenceIntegrityError(EvidenceChainError):
    """ZA-RE-0013: 完整性校验失败——条目内容 hash 重算不一致（篡改检出）。"""

    error_code = "ZA-RE-0013"


# ============================================================================
# 2. 常量与三态词表
# ============================================================================

CHAIN_FILENAME: Final = "evidence_chain.jsonl"
EVIDENCE_ID_PREFIX: Final = "EV-"

#: hash 固化覆盖字段（规范化 JSON sort_keys 后 SHA-256）
HASH_FIELDS: Final = (
    "evidence_id",
    "hypothesis_id",
    "polarity",
    "source",
    "content",
    "created_at",
)


class EvidencePolarity(str, Enum):
    """证据极性三态（11号文 §3.1：支持/反驳/中性）。"""

    SUPPORT = "support"
    CONTRADICT = "contradict"
    NEUTRAL = "neutral"


# ============================================================================
# 3. 证据条目与聚合
# ============================================================================


@dataclass(frozen=True)
class EvidenceEntry:
    """证据条目（不可变——append 落盘后不改不删）。"""

    evidence_id: str
    hypothesis_id: str
    polarity: str  # EvidencePolarity.value
    source: str
    content: str
    created_at: str  # ISO 8601（CST）
    content_hash: str  # SHA-256 hex（64 字符）

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "hypothesis_id": self.hypothesis_id,
            "polarity": self.polarity,
            "source": self.source,
            "content": self.content,
            "created_at": self.created_at,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceEntry:
        return cls(
            evidence_id=str(data["evidence_id"]),
            hypothesis_id=str(data["hypothesis_id"]),
            polarity=str(data["polarity"]),
            source=str(data["source"]),
            content=str(data["content"]),
            created_at=str(data["created_at"]),
            content_hash=str(data["content_hash"]),
        )


@dataclass(frozen=True)
class EvidenceSummary:
    """单假设的证据聚合视图——迭代引导器（iteration_guide）的输入契约。"""

    hypothesis_id: str
    support_count: int
    contradict_count: int
    neutral_count: int
    total_count: int
    latest_support_at: str | None  # ISO 8601；无支持证据→None
    latest_at: str | None  # ISO 8601；无任何证据→None

    def counts_dict(self) -> dict[str, int]:
        return {
            "support": self.support_count,
            "contradict": self.contradict_count,
            "neutral": self.neutral_count,
            "total": self.total_count,
        }


def compute_entry_hash(payload: dict[str, Any]) -> str:
    """计算条目完整性 hash：规范化 JSON（sort_keys，UTF-8）的 SHA-256 hex。"""
    canonical = json.dumps({k: payload[k] for k in HASH_FIELDS}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ============================================================================
# 4. 证据链
# ============================================================================


class EvidenceChain:
    """证据链——append-only 挂链 + 外键约束 + 完整性校验。

    Args:
        store_dir: 落盘目录；None → DEFAULT_STORE_DIR（与假设注册表同根）。
        registry: 假设注册表（外键真源）——append 时校验 hypothesis_id 存在。
    """

    def __init__(
        self,
        store_dir: Path | str | None = None,
        *,
        registry: HypothesisRegistry,
    ) -> None:
        self._store_dir = Path(store_dir) if store_dir is not None else DEFAULT_STORE_DIR
        self._path = self._store_dir / CHAIN_FILENAME
        self._registry = registry
        self._entries: list[EvidenceEntry] = []
        self._load()

    # ── 持久化 ────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not self._path.exists():
            return  # fresh boot：空链
        with self._path.open("r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    self._entries.append(EvidenceEntry.from_dict(json.loads(line)))
                except Exception as exc:  # JSONDecodeError/KeyError/TypeError
                    raise EvidenceChainError(
                        f"证据链落盘损坏（第 {lineno} 行不可解析），fail-fast（篡改/损坏不静默跳过）: {self._path}",
                        details={"path": str(self._path), "lineno": lineno, "cause": repr(exc)},
                    ) from exc

    def _append_line(self, entry: EvidenceEntry) -> None:
        self._store_dir.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def _next_id(self) -> str:
        seq = 0
        for e in self._entries:
            if e.evidence_id.startswith(EVIDENCE_ID_PREFIX):
                try:
                    seq = max(seq, int(e.evidence_id[len(EVIDENCE_ID_PREFIX) :]))
                except ValueError:
                    continue
        return f"{EVIDENCE_ID_PREFIX}{seq + 1:04d}"

    # ── 挂链 ──────────────────────────────────────────────────────────────

    def append(
        self,
        hypothesis_id: str,
        polarity: str | EvidencePolarity,
        source: str,
        content: str,
        *,
        at: datetime | None = None,
    ) -> EvidenceEntry:
        """追加证据条目（外键校验 → 三态词表校验 → hash 固化 → 落盘）。

        Raises:
            UnknownHypothesisError: hypothesis_id 在注册表不存在（外键约束）。
            InvalidPolarityError: polarity 越出三态词表。
        """
        try:
            self._registry.get(hypothesis_id)
        except HypothesisNotFoundError:
            raise UnknownHypothesisError(
                f"证据拒挂——假设不存在: {hypothesis_id}（外键约束）",
                details={"hypothesis_id": hypothesis_id},
            ) from None
        try:
            pol = EvidencePolarity(polarity)
        except ValueError:
            raise InvalidPolarityError(
                f"证据极性越出三态词表: {polarity!r}（词表：support/contradict/neutral）",
                details={"polarity": str(polarity), "hypothesis_id": hypothesis_id},
            ) from None
        created_at = (at if at is not None else datetime.now(CST)).isoformat()
        draft = {
            "evidence_id": self._next_id(),
            "hypothesis_id": hypothesis_id,
            "polarity": pol.value,
            "source": source,
            "content": content,
            "created_at": created_at,
        }
        entry = EvidenceEntry(content_hash=compute_entry_hash(draft), **draft)
        self._append_line(entry)
        self._entries.append(entry)
        log.info("证据挂链 %s → %s（%s）", entry.evidence_id, hypothesis_id, pol.value)
        return entry

    # ── 查询与聚合 ────────────────────────────────────────────────────────

    def list_for(self, hypothesis_id: str) -> list[EvidenceEntry]:
        """按假设列出证据（追加序）。"""
        return [e for e in self._entries if e.hypothesis_id == hypothesis_id]

    def iter_all(self) -> Iterator[EvidenceEntry]:
        return iter(self._entries)

    def summary_for(self, hypothesis_id: str) -> EvidenceSummary:
        """聚合单假设证据计数/最新时间——迭代引导器输入。"""
        entries = self.list_for(hypothesis_id)
        support = [e for e in entries if e.polarity == EvidencePolarity.SUPPORT.value]
        contradict = [e for e in entries if e.polarity == EvidencePolarity.CONTRADICT.value]
        neutral = [e for e in entries if e.polarity == EvidencePolarity.NEUTRAL.value]
        return EvidenceSummary(
            hypothesis_id=hypothesis_id,
            support_count=len(support),
            contradict_count=len(contradict),
            neutral_count=len(neutral),
            total_count=len(entries),
            latest_support_at=support[-1].created_at if support else None,
            latest_at=entries[-1].created_at if entries else None,
        )

    # ── 完整性 ────────────────────────────────────────────────────────────

    def verify_integrity(self) -> None:
        """全量重算条目 hash 与落盘值比对——任一不一致即篡改检出，fail-fast。"""
        bad = [e.evidence_id for e in self._entries if compute_entry_hash(e.to_dict()) != e.content_hash]
        if bad:
            raise EvidenceIntegrityError(
                f"证据完整性校验失败——{len(bad)} 条目 hash 重算不一致（篡改检出）: {bad}",
                details={"evidence_ids": bad, "path": str(self._path)},
            )
