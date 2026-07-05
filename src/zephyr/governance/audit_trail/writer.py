# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §4.4
# [MODULE] zephyr.governance.audit_trail.writer
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.models
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
# [A_module] module_id=MOD-GOV_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
from typing import Any

from zephyr.governance.audit_trail.contracts import AuditWriter as AuditWriterABC  # 5.104.15 修复: 继承ABC契约
from zephyr.governance.audit_trail.models import AuditIssue, GlobalAuditReport

logger = logging.getLogger(__name__)

__all__ = ["AuditReportWriter", "AuditWriter", "get_audit_writer"]

DEFAULT_REPORT_DIR = Path.cwd() / "data" / "audit_history"
DEFAULT_AUDIT_DIR = Path.cwd() / "data" / "audit_trail"
_GENESIS_HASH = "0" * 64

# 5.17.1 修复：模块级单例（供 contracts.py 委托桥接使用）
_GLOBAL_WRITER: "AuditWriter | None" = None
_GLOBAL_WRITER_LOCK = threading.Lock()


class AuditReportWriter(AuditWriterABC):  # 5.104.15 修复: 继承ABC契约
    def __init__(self, report_dir: Path | None = None) -> None:
        self._report_dir = Path(report_dir or DEFAULT_REPORT_DIR)
        self._report_dir.mkdir(parents=True, exist_ok=True)

    def write_report(self, report: GlobalAuditReport, path: Path | None = None) -> Path:
        output_path = path or self._report_dir / f"{report.audit_id}.json"
        report.finished_at = report.finished_at or datetime.now()
        content = report.model_dump_json(indent=2, default=str)

        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            # 5.74.4 修复：os.replace 前刷盘，确保审计内容落盘，防止崩溃后
            # 目标文件存在但内容为空/不完整，破坏审计完整性。
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(str(tmp_path), str(output_path))
        except Exception:
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

        content = issue.model_dump_json(indent=2, default=str)
        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            # 5.74.4 修复：os.replace 前刷盘，确保审计内容落盘，防止崩溃后
            # 目标文件存在但内容为空/不完整，破坏审计完整性。
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(str(tmp_path), str(output_path))
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        return output_path

    def write_json(self, data: dict[str, Any], filename: str) -> Path:
        output_path = self._report_dir / filename
        content = json.dumps(data, indent=2, ensure_ascii=False, default=str)

        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            # 5.74.4 修复：os.replace 前刷盘，确保审计内容落盘，防止崩溃后
            # 目标文件存在但内容为空/不完整，破坏审计完整性。
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.replace(str(tmp_path), str(output_path))
        except Exception:
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
        except Exception:
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
        prefix = "AUD-F" if event_type == "file_detail" else "AUD-T"

        with self._lock:
            self._lamport_counter += 1
            entry_id = _generate_entry_id(prefix=prefix, seq=self._lamport_counter)

            entry: dict[str, Any] = dict(event)
            entry["entry_id"] = entry_id
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()
            entry["prev_hash"] = self._last_hash
            entry["lamport_time"] = self.lamport_time + 1
            entry["lamport_clock_counter"] = self._lamport_counter
            entry["lamport_clock_ide"] = self.ide_source

            # entry_hash = SHA-256(canonical JSON of entry，不含 entry_hash/hmac_signature)
            canonical = json.dumps(entry, sort_keys=True, ensure_ascii=False, default=str)
            entry_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            entry["entry_hash"] = entry_hash

            # HMAC-SHA256 签名（覆盖 entry_hash）
            if self._hmac_key:
                entry["hmac_signature"] = hmac.new(
                    self._hmac_key, entry_hash.encode("utf-8"), hashlib.sha256
                ).hexdigest()

            try:
                with open(self._event_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
            except Exception:
                self._write_failures += 1
                if self._write_failures >= self._max_write_failures:
                    self._readonly = True
                raise

            self._last_hash = entry_hash
            self.event_count += 1
            self.lamport_time += 1

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
            from zephyr.governance.audit_trail.integrity import MerkleAggregator
            root = MerkleAggregator.aggregate(self._batch_event_hashes)
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
    key = os.environ.get("ZEPHYR_AUDIT_HMAC_SECRET", "")
    if key:
        return key.encode("utf-8")
    # 兜底默认（测试兼容 + 开发环境可用，生产应设置 env var）
    logger.warning(
        "ZEPHYR_AUDIT_HMAC_SECRET 未设置，使用公开默认密钥（不提供任何安全保证，仅限开发/测试）"
    )
    return b"zephyr-audit-hmac-default-key"
