# [BLUEPRINT] MOD-CMP-013 | docs/03_modules/_domain_compliance/evidence_chain_generator/blueprint.md
# [MODULE] zephyr.compliance.evidence_chain_generator
# [DOMAIN] D_COMPLIANCE
# [DEPENDENCIES] 无（协议核心纯内存；clock/落盘root 全注入；仅 stdlib）
# [CONSUMERS] 运行时装配批（采集器注册表统一注入点装配 / 检索导出供合规审计）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] append-only（只增不改不删）; prev_hash 哈希链（首记录 prev_hash=GENESIS）; 同输入必同输出（确定性）; 采集器按名称排序确定性执行; 落盘仅在注入 root 时发生（JSONL 单行一条合法 JSON）
# [MODIFY-GUARD] docs/03_modules/_domain_compliance/evidence_chain_generator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EvidenceChainError(占位 ZA-CMP-UNREGISTERED-EVIDENCE-CHAIN)——空snapshot_id/非法载荷/重复采集器/链校验失败时抛
# [TESTS] tests/compliance/test_evidence_chain_generator.py
# [A_module] module_id=MOD-CMP-013 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""EvidenceChainGenerator — 合规证据链生成器（MOD-CMP-013）。

B1-00312（AUD-DRAFT-001-DIGEST P2 波 P2-W10，CAND-CMP-003，C2）：委托/成交/
决策快照**自动采集**（采集器注册表注入）→ **哈希链式落盘**（append-only +
prev_hash 链，复用 compliance_log 的 WORM 语义）+ **检索导出**（按时间/类型/
标的查询 + 导出 JSONL）。

设计要点：
- **WORM 思想**：链上记录一经写入不可改不可删；`verify_chain()` 可重放
  校验 prev_hash 链完整性，任何篡改必检出（Fail-Closed 抛专用 Error）。
- **纯内存/DI**：时钟注入；落盘根目录注入（None 时纯内存不落盘），测试
  写 tmp_path，不触网不开子进程。
- **确定性**：采集器按注册名排序执行；record_hash 由 (seq, prev_hash,
  规范化快照, recorded_at) 的 sha256 唯一决定，同输入必同输出。

查重分工：compliance_log=通用合规日志 JSONL 载体（无哈希链/无采集注册表）；
audit_trail=审计轨迹族（无 prev_hash 链校验语义）。本件=证据链生成与校验层。
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChainRecord",
    "EvidenceChainError",
    "EvidenceChainGenerator",
    "EvidenceSnapshot",
]

#: 首记录 prev_hash 哨兵（链起点，确定性常量）
GENESIS_HASH: Final[str] = "0" * 64


class EvidenceChainError(Exception):
    """证据链输入/链完整性非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-CMP-UNREGISTERED-EVIDENCE-CHAIN。
    """


@dataclass(frozen=True)
class EvidenceSnapshot:
    """合规证据快照（委托/成交/决策载体，frozen）。"""

    snapshot_id: str
    evidence_type: str  # 证据类型（如 order/trade/decision，词表由调用方治理）
    symbol: str  # 标的代码（跨标的证据可为空串以外的全局标识，如 "PORTFOLIO"）
    payload: Mapping  # 证据载荷（须可被 JSON 序列化）
    taken_at: datetime.datetime


@dataclass(frozen=True)
class ChainRecord:
    """链上记录（append-only，prev_hash 哈希链节点）。"""

    seq: int  # 链序号（从 1 起，严格递增）
    snapshot: EvidenceSnapshot
    prev_hash: str
    record_hash: str
    recorded_at: datetime.datetime


def _canonical(obj: object) -> str:
    """规范化 JSON 序列化（键排序、紧凑分隔符，确定性哈希基元）。

    不使用 default 兜底：payload 必须为 JSON 原生类型，否则抛 TypeError
    （由 _validate_snapshot 转 EvidenceChainError，Fail-Closed）。
    """
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _snapshot_canonical(snapshot: EvidenceSnapshot) -> str:
    return _canonical({
        "snapshot_id": snapshot.snapshot_id,
        "evidence_type": snapshot.evidence_type,
        "symbol": snapshot.symbol,
        "payload": snapshot.payload,
        "taken_at": snapshot.taken_at.isoformat(),
    })


class EvidenceChainGenerator:
    """证据链生成器（采集注册表 + append-only 哈希链 + 检索导出）。

    Args:
        clock: 时钟注入（记录时戳确定性来源）。
        root: 落盘根目录注入；None 时纯内存不落盘。注入后每条记录追加
            ``root/"evidence_chain.jsonl"`` 单行 JSON。
    """

    _LOG_NAME: Final[str] = "evidence_chain.jsonl"

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        root: Path | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._root = Path(root) if root is not None else None
        self._collectors: dict[str, Callable[[], Iterable[EvidenceSnapshot]]] = {}
        self._chain: list[ChainRecord] = []

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _validate_snapshot(self, snapshot: EvidenceSnapshot) -> None:
        if not isinstance(snapshot, EvidenceSnapshot):
            raise EvidenceChainError(f"非法快照类型: {type(snapshot).__name__!r}")
        if not snapshot.snapshot_id:
            raise EvidenceChainError("snapshot_id 为空")
        if not snapshot.evidence_type:
            raise EvidenceChainError(f"evidence_type 为空: {snapshot.snapshot_id!r}")
        if not snapshot.symbol:
            raise EvidenceChainError(f"symbol 为空: {snapshot.snapshot_id!r}")
        if not isinstance(snapshot.taken_at, datetime.datetime):
            raise EvidenceChainError(f"taken_at 非法: {snapshot.snapshot_id!r}")
        try:
            _snapshot_canonical(snapshot)
        except (TypeError, ValueError) as exc:
            raise EvidenceChainError(
                f"payload 不可序列化: {snapshot.snapshot_id!r} ({exc})"
            ) from exc

    def _record_hash(self, seq: int, prev_hash: str, snapshot: EvidenceSnapshot,
                     recorded_at: datetime.datetime) -> str:
        material = "|".join([
            str(seq),
            prev_hash,
            _snapshot_canonical(snapshot),
            recorded_at.isoformat(),
        ])
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def _append(self, snapshot: EvidenceSnapshot) -> ChainRecord:
        self._validate_snapshot(snapshot)
        seq = len(self._chain) + 1
        prev_hash = self._chain[-1].record_hash if self._chain else GENESIS_HASH
        recorded_at = self._clock()
        record = ChainRecord(
            seq=seq,
            snapshot=snapshot,
            prev_hash=prev_hash,
            record_hash=self._record_hash(seq, prev_hash, snapshot, recorded_at),
            recorded_at=recorded_at,
        )
        self._chain.append(record)  # append-only：只增不改不删
        if self._root is not None:
            self._persist(record)
        _log.info("证据链记录: seq=%d id=%s hash=%s", seq, snapshot.snapshot_id, record.record_hash[:12])
        return record

    def _persist(self, record: ChainRecord) -> None:
        """落盘（注入 root 时）：JSONL 单行一条合法 JSON，追加写。"""
        line = _canonical({
            "seq": record.seq,
            "prev_hash": record.prev_hash,
            "record_hash": record.record_hash,
            "recorded_at": record.recorded_at.isoformat(),
            "snapshot": json.loads(_snapshot_canonical(record.snapshot)),
        })
        try:
            self._root.mkdir(parents=True, exist_ok=True)
            with (self._root / self._LOG_NAME).open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            # 落盘失败不阻断采集（链在内存仍可校验），留痕即可
            _log.exception("证据链落盘失败: seq=%d", record.seq)

    # ── 采集器注册表 ──────────────────────────────────────────────────────

    def register_collector(
        self, name: str, collector: Callable[[], Iterable[EvidenceSnapshot]]
    ) -> None:
        """登记快照采集器（名称唯一；重复登记 Fail-Closed）。"""
        if not name:
            raise EvidenceChainError("采集器名称为空")
        if not callable(collector):
            raise EvidenceChainError(f"采集器不可调用: {name!r}")
        if name in self._collectors:
            raise EvidenceChainError(f"采集器重复登记: {name!r}")
        self._collectors[name] = collector

    # ── 采集（自动 → 哈希链式上链）─────────────────────────────────────────

    def collect(self) -> list[ChainRecord]:
        """执行全部采集器（按名称排序确定性），快照逐条 append-only 上链。"""
        out: list[ChainRecord] = []
        for name in sorted(self._collectors):
            snapshots = self._collectors[name]()
            for snapshot in snapshots:
                out.append(self._append(snapshot))
        return out

    # ── 链校验 ────────────────────────────────────────────────────────────

    def verify_chain(self) -> bool:
        """重放校验 prev_hash 链完整性；任何篡改 → Fail-Closed 抛 Error。"""
        prev_hash = GENESIS_HASH
        for expect_seq, record in enumerate(self._chain, start=1):
            if record.seq != expect_seq:
                raise EvidenceChainError(
                    f"链序号断裂: 期望 {expect_seq} 实际 {record.seq}"
                )
            if record.prev_hash != prev_hash:
                raise EvidenceChainError(
                    f"prev_hash 链断裂: seq={record.seq} id={record.snapshot.snapshot_id!r}"
                )
            recomputed = self._record_hash(
                record.seq, record.prev_hash, record.snapshot, record.recorded_at
            )
            if recomputed != record.record_hash:
                raise EvidenceChainError(
                    f"record_hash 校验失败（疑似篡改）: seq={record.seq}"
                )
            prev_hash = record.record_hash
        return True

    # ── 检索导出 ──────────────────────────────────────────────────────────

    def query(
        self,
        *,
        start: datetime.datetime | None = None,
        end: datetime.datetime | None = None,
        evidence_type: str | None = None,
        symbol: str | None = None,
    ) -> list[ChainRecord]:
        """按时间区间/证据类型/标的检索（确定性按 seq 排序）。"""
        if start is not None and end is not None and start > end:
            raise EvidenceChainError(f"时间区间非法: start={start!r} > end={end!r}")
        out: list[ChainRecord] = []
        for record in self._chain:
            ts = record.snapshot.taken_at
            if start is not None and ts < start:
                continue
            if end is not None and ts > end:
                continue
            if evidence_type is not None and record.snapshot.evidence_type != evidence_type:
                continue
            if symbol is not None and record.snapshot.symbol != symbol:
                continue
            out.append(record)
        return out

    def export_jsonl(
        self,
        records: Iterable[ChainRecord] | None = None,
    ) -> str:
        """导出 JSONL（默认导出全链；单行一条合法 JSON）。"""
        items = list(records) if records is not None else list(self._chain)
        lines = [
            _canonical({
                "seq": r.seq,
                "prev_hash": r.prev_hash,
                "record_hash": r.record_hash,
                "recorded_at": r.recorded_at.isoformat(),
                "snapshot": json.loads(_snapshot_canonical(r.snapshot)),
            })
            for r in items
        ]
        return "\n".join(lines) + ("\n" if lines else "")

    # ── 查询 ─────────────────────────────────────────────────────────────

    def records(self) -> list[ChainRecord]:
        """全链只读视图（确定性按 seq 排序）。"""
        return list(self._chain)
