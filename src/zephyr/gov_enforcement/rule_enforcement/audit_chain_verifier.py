# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.audit_chain_verifier
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.gate_context; zephyr.gov_audit.writer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 链append-only持久化(gate_chain.jsonl); clear需confirm=True且留痕核心链
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 持久化失败仅告警不阻断; clear无confirm抛PermissionError
# [TESTS] tests/audit/test_audit_chain_verifier.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
审计链验证工具——独立重放门禁判定+Hash链完整性校验（beta）
同时将门禁审计事件写入核心 zephyr.gov_audit.writer.AuditWriter 不可变审计链

5.37.8：本地门禁 hash 链持久化——append-only JSONL（gate_chain.jsonl）+ 重启恢复，
与 AuditWriter 的 events.jsonl 同目录约定（data/audit_trail/）。
5.37.9：clear() 权限保护——必须显式 confirm=True，操作本身写核心审计链留痕。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: persist_path 参数
#   fields: 参数 persist_path（无注解）
#   code: audit_chain_verifier.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AuditReport
#   name_en: AuditReport
#   intro: class AuditReport 源码 L105-L116
#   desc: 公共方法（定义序）: summary；源码 L105-L116
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② AuditChainVerifier
#   name_en: AuditChainVerifier
#   intro: class AuditChainVerifier 源码 L119-L356
#   desc: 公共方法（定义序）: core_writer, last_hash, chain, compute_hash, append, verify_chain, replay, length, clear；源码 L119-L…
#   inputs: persist_path
#   outputs: 返回值
# - id: A3
#   name_zh: ③ main
#   name_en: main
#   intro: main() 源码 L362-L363
#   desc: 源码 L362-L363
#   inputs: 无参数
#   outputs: 返回值
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: AuditReport, AuditChainVerifier, main
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

import hashlib
import json
import logging
import os
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus
from zephyr.shared.io.serialization import dumps

_CORE_AUDIT_AVAILABLE = False
try:
    from zephyr.gov_audit.writer import AuditWriter as _CoreAuditWriter

    _CORE_AUDIT_AVAILABLE = True
except ImportError:
    _CoreAuditWriter = None

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    gate_id: str
    status: GateStatus
    reasons: list[str]
    previous_hash: str
    hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AuditReport:
    entries: list[AuditEntry]
    chain_valid: bool
    reproduced: bool
    verified_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def summary(self) -> str:
        return (
            f"AuditReport: {len(self.entries)} entries, "
            f"chain={'OK' if self.chain_valid else 'BROKEN'}, "
            f"reproduced={'OK' if self.reproduced else 'MISMATCH'}"
        )


class AuditChainVerifier:
    def __init__(self, persist_path: Path | str | None = None) -> None:
        self._chain: list[AuditEntry] = []
        self._last_hash = "0" * 64
        # 5.37.8：门禁审计链持久化路径（append-only JSONL + hash chain）。
        # 优先级：显式参数 > ZEPHYR_GATE_CHAIN_PATH 环境变量（测试隔离用）
        # > 默认 data/audit_trail/gate_chain.jsonl（与 AuditWriter 同目录约定）。
        env_path = os.environ.get("ZEPHYR_GATE_CHAIN_PATH", "")
        if persist_path is not None:
            self._persist_path = Path(persist_path)
        elif env_path:
            self._persist_path = Path(env_path)
        else:
            self._persist_path = Path.cwd() / "data" / "audit_trail" / "gate_chain.jsonl"
        self._persist_lock = threading.Lock()
        self._load_persisted_chain()
        self._core_writer: _CoreAuditWriter | None = None
        if _CORE_AUDIT_AVAILABLE:
            try:
                self._core_writer = _CoreAuditWriter()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in audit_chain_verifier", exc_info=True)

    @property
    def core_writer(self) -> _CoreAuditWriter | None:
        """只读：core_writer（Stage 4 公共化）。"""
        return self._core_writer

    @core_writer.setter
    def core_writer(self, value):
        """写入：core_writer（Stage 4 公共化）。"""
        self._core_writer = value

    @property
    def last_hash(self):
        """只读：last_hash（Stage 4 公共化）。"""
        return self._last_hash

    @last_hash.setter
    def last_hash(self, value):
        """写入：last_hash（Stage 4 公共化）。"""
        self._last_hash = value

    @property
    def chain(self) -> list[AuditEntry]:
        """只读：chain（Stage 4 公共化）。"""
        return self._chain

    @chain.setter
    def chain(self, value):
        """写入：chain（Stage 4 公共化）。"""
        self._chain = value

    @staticmethod
    def compute_hash(payload: dict) -> str:
        payload_str = dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    def _load_persisted_chain(self) -> None:
        """从 gate_chain.jsonl 恢复链与尾哈希（5.37.8：重启后链连续，可跨进程校验）。"""
        if not self._persist_path.exists():
            return
        try:
            with open(self._persist_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                        entry = AuditEntry(
                            gate_id=raw["gate_id"],
                            status=GateStatus[raw["status"]],
                            reasons=list(raw.get("reasons") or []),
                            previous_hash=raw["previous_hash"],
                            hash=raw["hash"],
                            timestamp=datetime.fromisoformat(raw["timestamp"]),
                        )
                    except (KeyError, ValueError, TypeError):
                        logger.warning("skip malformed persisted gate audit line", exc_info=True)
                        continue
                    self._chain.append(entry)
            if self._chain:
                self._last_hash = self._chain[-1].hash
        except OSError:
            logger.warning("load persisted gate chain failed: %s", self._persist_path, exc_info=True)

    def _persist_entry(self, entry: AuditEntry, ts: datetime) -> None:
        """追加一条门禁审计条目到 JSONL（5.37.8：落盘失败仅告警，不阻断门禁主流程）。

        ts 必须是 entry.hash 计算时覆盖的时间戳（即 GateResult.timestamp）——
        持久化 entry.timestamp（append 时刻）会导致重载后 verify_chain 重算不一致。
        """
        try:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            line = dumps(
                {
                    "gate_id": entry.gate_id,
                    "status": entry.status.name,
                    "reasons": entry.reasons,
                    "previous_hash": entry.previous_hash,
                    "hash": entry.hash,
                    "timestamp": ts.isoformat(),
                },
                ensure_ascii=False,
            )
            with self._persist_lock, open(self._persist_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
                f.flush()
                os.fsync(f.fileno())
        except OSError:
            logger.warning("persist gate audit entry failed: %s", self._persist_path, exc_info=True)

    def append(self, gate_id: str, result: GateResult) -> AuditEntry:
        payload = {
            "gate_id": gate_id,
            "status": result.status.name,
            "reasons": result.reasons,
            "timestamp": result.timestamp.isoformat(),
            "previous_hash": self._last_hash,
        }
        entry_hash = self._compute_hash(payload)
        entry = AuditEntry(
            gate_id=gate_id,
            status=result.status,
            reasons=list(result.reasons),
            previous_hash=self._last_hash,
            hash=entry_hash,
        )
        self._chain.append(entry)
        self._last_hash = entry_hash
        logger.debug("audit entry #%d: %s -> %s", len(self._chain), gate_id, entry_hash[:16])
        # 持久化时间戳与 hash 载荷一致（result.timestamp，见 _persist_entry docstring）
        self._persist_entry(entry, result.timestamp)

        if self._core_writer is not None:
            try:
                core_event = {
                    "event_type": "gate_audit",
                    "agent_id": "gate_engine",
                    "session_id": gate_id,
                    "target_path": gate_id,
                    "operation": "gate_check",
                    "status": result.status.name,
                    "reasons": list(result.reasons),
                    "entry_hash": entry_hash,
                }
                self._core_writer.write(core_event)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in audit_chain_verifier", exc_info=True)

        return entry

    def verify_chain(self) -> AuditReport:
        prev = "0" * 64
        valid = True
        for entry in self._chain:
            if entry.previous_hash != prev:
                logger.error(
                    "chain break at %s: expected=%s got=%s", entry.gate_id, prev[:16], entry.previous_hash[:16]
                )
                valid = False
                break
            payload = {
                "gate_id": entry.gate_id,
                "status": entry.status.name,
                "reasons": entry.reasons,
                "timestamp": entry.timestamp.isoformat(),
                "previous_hash": prev,
            }
            computed = self._compute_hash(payload)
            if computed != entry.hash:
                logger.error("hash mismatch at %s", entry.gate_id)
                valid = False
                break
            prev = entry.hash
        return AuditReport(entries=list(self._chain), chain_valid=valid, reproduced=valid)

    def replay(self, ctx: GateContext, checkers: dict[str, callable]) -> AuditReport:
        results: list[GateResult] = []
        for gate_id, checker in checkers.items():
            results.append(checker(ctx))

        reproduced = True
        for result in results:
            matching = [e for e in self._chain if e.gate_id == result.gate_id]
            if not matching or matching[-1].status != result.status:
                reproduced = False
                break

        return AuditReport(
            entries=list(self._chain), chain_valid=self.verify_chain().chain_valid, reproduced=reproduced
        )

    @staticmethod
    def _compute_hash(payload: dict) -> str:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return AuditChainVerifier.compute_hash(payload)

    @property
    def length(self) -> int:
        return len(self._chain)

    def clear(self, reason: str = "", *, confirm: bool = False, cleared_by: str = "") -> None:
        """清空审计链——5.37.9 权限保护：高危操作，必须显式 confirm=True。

        - confirm=False（默认）→ 抛 PermissionError，拒绝执行（防误调/未授权抹除链）。
        - confirm=True → 先把 clear 操作本身写入核心审计链留痕（含 reason/cleared_by/
          链长/尾哈希），再清空内存链与持久化文件（文件残留会导致重启后链复活，
          与 clear 语义矛盾，故一并删除）。
        """
        if not confirm:
            raise PermissionError(
                "AuditChainVerifier.clear() refused: 抹除审计链必须显式 confirm=True "
                "(5.37.9 permission guard); pass reason=/cleared_by= for accountability"
            )
        # 5.17.4 修复：clear() 前写入审计事件，留痕可追溯（防止无审计抹除链）
        if self._core_writer is not None:
            try:
                self._core_writer.write(
                    {
                        "event_type": "chain_cleared",
                        "agent_id": cleared_by or "audit_chain_verifier",
                        "reason": reason or "unspecified",
                        "cleared_by": cleared_by,
                        "chain_length": len(self._chain),
                        "last_hash": self._last_hash,
                    }
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in audit_chain_verifier", exc_info=True)
        self._chain.clear()
        self._last_hash = "0" * 64
        try:
            if self._persist_path.exists():
                self._persist_path.unlink()
        except OSError:
            logger.warning("remove persisted gate chain failed: %s", self._persist_path, exc_info=True)


__all__ = ["AuditChainVerifier", "AuditEntry", "AuditReport"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
