# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.4
# [MODULE] zephyr.gov_audit.writer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models; zephyr.shared.session.session_audit
# [CONSUMERS] audit-orchestrator.pipeline_runner; cli
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 报告写入必须原子操作(temp-file+os.replace)
# [MODIFY-GUARD] 报告格式变更必须同步 cli.py + query.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 写入失败抛IOError
# [TESTS] tests/audit-orchestrator/test_writer.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import hashlib
import hmac
import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final

from zephyr.gov_audit.contracts import AuditWriter as AuditWriterABC  # 5.104.15 修复: 继承ABC契约
from zephyr.gov_audit.models import AuditEventType, AuditIssue, GlobalAuditReport
from zephyr.shared.io.paths import AUDIT_DATA_DIR, REPO_ROOT  # 路径真源（SSoT）
from zephyr.shared.io.serialization import dumps
from zephyr.shared.security.secrets import get_secret_or_default
from zephyr.shared.session.session_audit import (
    register_audit_writer_provider as _register_audit_writer_provider,
)
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["AuditReportWriter", "AuditWriter", "get_audit_writer"]

# 治本（AI-AUDIT12 路径SSoT收敛）：默认目录锚定 zephyr.shared.io.paths 真源。
# 原 DEFAULT_AUDIT_DIR=Path.cwd()/"data"/"audit_trail"（下划线+相对 cwd）与验证方
# AUDIT_DATA_DIR（data/audit-trail 连字符绝对路径）双真源不一致——默认写入的
# events.jsonl 永远落在验证器/小时 Merkle 聚合器读不到的目录，审计链默认即断链。
DEFAULT_REPORT_DIR: Final[Any] = REPO_ROOT / "data" / "audit_history"
DEFAULT_AUDIT_DIR: Final[Any] = AUDIT_DATA_DIR
_GENESIS_HASH = "0" * 64

# 治本（I9 核心模型强制消费）：已知事件类型白名单——AuditEventType 值（lowercase）
# + 运行时桥接/执行器使用但未登记到 AuditEventType 的事件类型。
# 不在白名单中的 event_type 会被规范化为 "unknown"，防止数据注入和日志污染。
_KNOWN_EVENT_TYPES: frozenset[str] = frozenset(
    getattr(AuditEventType, name).value.lower()
    for name in dir(AuditEventType)
    if name.isupper() and not name.startswith("_")
) | frozenset({
    # 运行时事件类型（来自 bridges/executors，尚未登记到 AuditEventType）
    "rbac_decision", "rollback_discard", "rollback_nexus", "rollback_operation",
    "drift_hotfix_bypass", "mcp_tool_call", "gate_audit", "skill_loaded",
    "budget_enforcement", "delegation_create", "chain_cleared", "session_record",
    "lifecycle_state_change", "feedback_loop_evolution",
    "generic", "unknown", "file_detail",
})

# 5.17.1 修复：模块级单例（供 contracts.py 委托桥接使用）
_GLOBAL_WRITER: "AuditWriter | None" = None
_GLOBAL_WRITER_LOCK = threading.Lock()


class AuditReportWriter(AuditWriterABC):  # 5.104.15 修复: 继承ABC契约
    def __init__(self, report_dir: Path | None = None) -> None:
        self._report_dir = Path(report_dir or DEFAULT_REPORT_DIR)
        self._report_dir.mkdir(parents=True, exist_ok=True)

    def write_report(self, report: GlobalAuditReport, path: Path | None = None) -> Path:
        output_path = path or self._report_dir / f"{report.audit_id}.json"
        report.finished_at = report.finished_at or now_utc()
        content = report.model_dump_json(indent=2)

        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            # 5.74.4 修复：os.replace 前刷盘，确保审计内容落盘，防止崩溃后
            # 目标文件存在但内容为空/不完整，破坏审计完整性。
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(str(tmp_path), str(output_path))
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        logger.info("Audit report written: %s", output_path)
        return output_path

    def write_issue(self, issue: AuditIssue, report_dir: Path) -> Path:
        dir_path = Path(report_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        output_path = dir_path / f"{issue.issue_id}.json"

        content = issue.model_dump_json(indent=2)
        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            # 5.74.4 修复：os.replace 前刷盘，确保审计内容落盘，防止崩溃后
            # 目标文件存在但内容为空/不完整，破坏审计完整性。
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(str(tmp_path), str(output_path))
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        return output_path

    def write_json(self, data: dict[str, Any], filename: str) -> Path:
        output_path = self._report_dir / filename
        content = dumps(data, indent=2, ensure_ascii=False)

        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            # 5.74.4 修复：os.replace 前刷盘，确保审计内容落盘，防止崩溃后
            # 目标文件存在但内容为空/不完整，破坏审计完整性。
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(str(tmp_path), str(output_path))
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        return output_path

    def list_reports(self, limit: int = 50) -> list[Path]:
        files = sorted(self._report_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        return files[:limit]


class AuditWriter:
    """不可变审计写入器——JSONL 追加 + SHA-256 哈希链 + HMAC-SHA256 签名 + Lamport 时钟。

    5.17.1 修复：从 no-op 桩升级为真正落盘的 append-only JSONL 哈希链写入器。
    旧代码 write()/flush() 均为 pass，审计事件静默丢弃，安全机制名实分离。
    """

    def __init__(
        self,
        data_dir: Path | str | None = None,
        enable_merkle: bool = True,
        hmac_key: str | None = None,
        ide_source: str | None = None,
        backend=None,
    ) -> None:
        self.data_dir = Path(data_dir) if data_dir else DEFAULT_AUDIT_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._event_log_path = self.data_dir / "events.jsonl"
        self.enable_merkle = enable_merkle
        self.ide_source = ide_source or "unknown"
        self._hmac_key = _resolve_hmac_key(hmac_key if hmac_key is not None else "")
        self._last_hash = _GENESIS_HASH
        self._batch_event_hashes: list[str] = []
        self.event_count = 0
        self.lamport_time = 0
        self._lamport_counter = 0
        self._write_failures = 0
        self._max_write_failures = 5
        self._readonly = False
        self._lock = threading.Lock()
        self._load_state()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def max_write_failures(self):
        """只读：max_write_failures（Stage 4 公共化）。"""
        return self._max_write_failures

    @max_write_failures.setter
    def max_write_failures(self, value):
        """写入：max_write_failures（Stage 4 公共化）。"""
        self._max_write_failures = value

    @property
    def readonly(self):
        """只读：readonly（Stage 4 公共化）。"""
        return self._readonly

    @readonly.setter
    def readonly(self, value):
        """写入：readonly（Stage 4 公共化）。"""
        self._readonly = value


    @property
    def write_failures(self):
        """只读：write_failures（Stage 4 公共化）。"""
        return self._write_failures

    @write_failures.setter
    def write_failures(self, value):
        """写入：write_failures（Stage 4 公共化）。"""
        self._write_failures = value


    # ── Stage 4 公共化（2026-07-28）：只读 property ──
    # 消除 tests/audit/test_audit_adversarial.py 中 15 处私有成员访问。

    @property
    def event_log_path(self) -> Path:
        """只读：event_log_path（Stage 4 公共化）。"""
        return self._event_log_path

    @event_log_path.setter
    def event_log_path(self, value):
        """写入：event_log_path（Stage 4 公共化）。"""
        self._event_log_path = value

    def _load_state(self) -> None:
        """从已有 events.jsonl 恢复 _last_hash 和 event_count（重启后链连续）。"""
        if not self._event_log_path.exists():
            return
        count = 0
        last_hash = _GENESIS_HASH
        try:
            with open(self._event_log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    count += 1
                    try:
                        entry = json.loads(line)
                        eh = entry.get("entry_hash")
                        if eh:
                            last_hash = eh
                    except json.JSONDecodeError:
                        pass
            self.event_count = count
            self._last_hash = last_hash
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("AuditWriter._load_state failed", exc_info=True)

    def write(self, event: dict[str, Any]) -> str:
        """追加一条审计事件到 JSONL，返回 entry_hash（即 chain_hash，64 字符）。

        每条 entry 包含：entry_id, timestamp, prev_hash, entry_hash, hmac_signature,
        lamport_time, lamport_clock_counter, lamport_clock_ide。
        """
        if self._readonly:
            raise RuntimeError(
                "AuditWriter is in readonly mode (too many write failures)"
            )

        event_type = event.get("event_type", "generic")
        # 治本（I9 核心模型强制消费）：event_type 白名单规范化——不在 _KNOWN_EVENT_TYPES 中的
        # event_type 会被规范化为 "unknown"，防止数据注入和日志污染。
        if event_type not in _KNOWN_EVENT_TYPES:
            event_type = "unknown"
            event["event_type"] = "unknown"
        # provenance 默认 "direct_agent"（直接写入，非委托/桥接）
        event.setdefault("provenance", "direct_agent")
        prefix = "AUD-F" if event_type == "file_detail" else "AUD-T"

        with self._lock:
            self._lamport_counter += 1
            entry_id = _generate_entry_id(prefix=prefix, seq=self._lamport_counter)

            entry: dict[str, Any] = dict(event)
            # 治本（AI-AUDIT12 保留字段净化）：剔除生产方注入的保留字段——实证主仓
            # 2026-07-04 起 5343 条 gate_audit 事件（audit_chain_verifier 预注入自有
            # entry_hash）canonical 绑定了不可恢复的外来哈希值，整段链永久不可验证；
            # 且 writer 无 HMAC 密钥时外来 hmac_signature 会原样落盘（伪造签名幻象）。
            # entry_hash/hmac_signature 只能由本 writer 计算赋值，禁止生产方预注入。
            entry.pop("entry_hash", None)
            entry.pop("hmac_signature", None)
            entry["entry_id"] = entry_id
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()
            entry["prev_hash"] = self._last_hash
            entry["lamport_time"] = self.lamport_time + 1
            entry["lamport_clock_counter"] = self._lamport_counter
            entry["lamport_clock_ide"] = self.ide_source

            # entry_hash = SHA-256(canonical JSON of entry，不含 entry_hash/hmac_signature)
            canonical = dumps(entry, sort_keys=True, ensure_ascii=False)
            entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            entry["entry_hash"] = entry_hash

            # HMAC-SHA256 签名（覆盖 entry_hash）
            if self._hmac_key:
                entry["hmac_signature"] = hmac.new(
                    self._hmac_key, entry_hash.encode("utf-8"), hashlib.sha256
                ).hexdigest()

            try:
                with open(self._event_log_path, "a", encoding="utf-8") as f:
                    f.write(dumps(entry, ensure_ascii=False) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                self._write_failures += 1
                if self._write_failures >= self._max_write_failures:
                    self._readonly = True
                raise

            self._last_hash = entry_hash
            self.event_count += 1
            self.lamport_time += 1
            # 治本（AI-AUDIT12 Merkle 批聚合断链）：写入成功后把 entry_hash 累积进当前
            # 批次——此前 _batch_event_hashes 无任何追加点，finalize_current_batch()
            # 恒返回 None、get_merkle_batches() 恒为空，Merkle 批聚合路径整体死代码。
            if self.enable_merkle:
                self._batch_event_hashes.append(entry_hash)

        return entry_hash

    def write_with_cot(self, event: dict[str, Any], reasoning_trace: str = "") -> dict[str, str]:
        """写入带 CoT 推理链的审计事件。reasoning_trace 截断至 500 字符。"""
        truncated = reasoning_trace[:500] if reasoning_trace else ""
        cot_hash = (
            hashlib.sha256(truncated.encode("utf-8")).hexdigest() if truncated else ""
        )

        enriched = dict(event)
        enriched["reasoning_trace"] = truncated
        enriched["cot_hash"] = cot_hash

        chain_hash = self.write(enriched)
        return {"chain_hash": chain_hash, "cot_hash": cot_hash}

    def merge_lamport(self, other_time: int) -> int:
        """Lamport 时钟合并：max(local, other) + 1。"""
        self.lamport_time = max(self.lamport_time, other_time) + 1
        return self.lamport_time

    def flush(self) -> None:
        """同步刷盘——write() 已即时落盘+fsync，此方法为 no-op 兼容接口。"""
        pass

    def finalize_current_batch(self) -> str | None:
        """finalize 当前批次，返回 merkle root。"""
        if not self._batch_event_hashes:
            return None
        if self.enable_merkle:
            from zephyr.gov_audit.integrity import MerkleAggregator

            # 治本（AI-AUDIT12）：MerkleAggregator 仅有 build/verify 静态方法，
            # 原调用不存在的 aggregate() 必抛 AttributeError。
            root = MerkleAggregator.build(self._batch_event_hashes)
        else:
            root = self._last_hash
        self._batch_event_hashes.clear()
        return root

    def get_merkle_batches(self) -> list[str]:
        """返回当前未 finalized 的事件哈希列表（供外部聚合）。"""
        return list(self._batch_event_hashes)


def get_audit_writer(
    data_dir: Path | str | None = None,
    enable_merkle: bool = True,
    hmac_key: str | None = None,
    ide_source: str | None = None,
    backend=None,
) -> AuditWriter:
    """双重检查锁定单例工厂。"""
    global _GLOBAL_WRITER
    if _GLOBAL_WRITER is None:
        with _GLOBAL_WRITER_LOCK:
            if _GLOBAL_WRITER is None:
                _GLOBAL_WRITER = AuditWriter(
                    data_dir=data_dir,
                    enable_merkle=enable_merkle,
                    hmac_key=hmac_key,
                    ide_source=ide_source,
                    backend=backend,
                )
    return _GLOBAL_WRITER


def _generate_entry_id(prefix: str = "AUD-T", seq: int | None = None) -> str:
    """生成审计条目 ID：{prefix}-{timestamp}-{uuid8}[-{seq:04d}]。"""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    seq_str = f"-{seq:04d}" if seq is not None else ""
    return f"{prefix}-{ts}-{short_uuid}{seq_str}"


def _resolve_hmac_key(config=None) -> bytes:
    """解析 HMAC 密钥：config 参数 > ZEPHYR_AUDIT_HMAC_SECRET 环境变量 > 兜底默认。

    5.17.2 修复：旧代码无视 config 和 env 直接返回硬编码 b"default-key"。
    现在优先读取显式传入的 config 字符串，其次读取环境变量，最后兜底默认。
    """
    if config and isinstance(config, str) and config.strip():
        return config.strip().encode("utf-8")
    key = get_secret_or_default("ZEPHYR_AUDIT_HMAC_SECRET", "")
    if key:
        return key.encode("utf-8")
    # 兜底默认（测试兼容 + 开发环境可用，生产应设置 env var）
    logger.warning(
        "ZEPHYR_AUDIT_HMAC_SECRET 未设置，使用公开默认密钥（不提供任何安全保证，仅限开发/测试）"
    )
    return b"zephyr-audit-hmac-default-key"


def resolve_audit_hmac_secret() -> str:
    """解析审计 HMAC 密钥为字符串（供 IntegrityVerifier 等消费方使用）。

    委托至 _resolve_hmac_key() 并解码为 str。测试 SSoT：
    IntegrityVerifier(hmac_key="") 时调用此函数获取密钥。
    """
    return _resolve_hmac_key().decode("utf-8")


# 5.174-M6 治本：模块 import 时向 L0 shared 层 session_audit 注册审计写入器工厂——
# 依赖注入消除 session_audit.append_record 原 L0→L2 延迟 import（shared 禁止向上
# import governance；依赖方向 governance(L2)→shared(L0)，符合向下依赖原则）。
_register_audit_writer_provider(get_audit_writer)
