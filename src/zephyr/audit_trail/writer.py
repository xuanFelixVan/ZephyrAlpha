"""audit_trail.writer — MOD-INF-020 · 不可变写入器
==================================================
蓝图 §3 · Append-only 审计日志写入

约束
----
  - Write-Once: 每条记录写入后不可修改/删除
  - Chain Hash: SHA-256 哈希链——每条记录引用前一条的哈希
  - HMAC-SHA256: 系统级签名——蓝图 D-020-04，密钥从 ZEPHYR_AUDIT_HMAC_SECRET 环境变量读取
  - Lamport Clock: 逻辑时钟 (ide_source, counter) 解决多 IDE 时序一致性——蓝图 D-020-09
  - Merkle Aggregation: 按批次构建 Merkle 树——蓝图 §2.2
  - Thread-Safe: threading.RLock 保护读写竞态
  - Atomic Write: 真正 append（open("a") + flush）——蓝图 D-020-02
  - Entry ID: AUD-T/AUD-F-{UUID7}-{SEQ} 格式——蓝图 §2.1
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

_logger = logging.getLogger(__name__)

DEFAULT_AUDIT_DATA_DIR: Path = Path("data/audit_trail")
_HMAC_ENV_VAR: str = "ZEPHYR_AUDIT_HMAC_SECRET"
_FALLBACK_HMAC_KEY: str = "zephyr-audit-hmac-default-key"


def _resolve_hmac_key(explicit_key: str = "") -> bytes:
    if explicit_key:
        return explicit_key.encode("utf-8")
    env_val = os.environ.get(_HMAC_ENV_VAR, "")
    if env_val:
        return env_val.encode("utf-8")
    _logger.warning(
        "AuditWriter: %s not set, using fallback HMAC key — NOT production-safe",
        _HMAC_ENV_VAR,
    )
    return _FALLBACK_HMAC_KEY.encode("utf-8")


def _generate_entry_id(prefix: str = "AUD-T", seq: int = 0) -> str:
    uuid7_like = uuid4().hex[:20]
    return f"{prefix}-{uuid7_like}-{seq:04d}"


class AuditWriter:
    def __init__(
        self,
        data_dir: Path | str = DEFAULT_AUDIT_DATA_DIR,
        hmac_key: str = "",
        enable_merkle: bool = True,
        merkle_batch_size: int = 100,
        ide_source: str = "unknown",
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._event_log_path = self._data_dir / "events.jsonl"
        self._chain_state_path = self._data_dir / "chain_state.json"
        self._merkle_state_path = self._data_dir / "merkle_state.json"
        self._hmac_key = _resolve_hmac_key(hmac_key)
        self._enable_merkle = enable_merkle
        self._merkle_batch_size = merkle_batch_size
        self._lock = threading.RLock()
        self._ide_source = ide_source
        self._lamport_counter: int = self._load_lamport_counter()
        self._current_batch_hashes: list[str] = self._load_pending_batch()
        self._readonly = False
        self._write_failures = 0
        self._max_write_failures = 3
        self._entry_seq: int = self._load_entry_seq()

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    @property
    def event_count(self) -> int:
        if not self._event_log_path.exists():
            return 0
        with open(self._event_log_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

    @property
    def lamport_time(self) -> int:
        return self._lamport_counter

    @property
    def ide_source(self) -> str:
        return self._ide_source

    def write(self, event: dict[str, Any]) -> str:
        if self._readonly:
            raise RuntimeError("AuditWriter is in readonly mode due to repeated write failures")
        validated = self._validate_event(event)
        with self._lock:
            try:
                result = self._write_locked(validated)
                self._write_failures = 0
                return result
            except Exception:
                self._write_failures += 1
                if self._write_failures >= self._max_write_failures:
                    self._readonly = True
                    _logger.critical(
                        "AuditWriter: entering readonly mode after %d consecutive write failures",
                        self._write_failures,
                    )
                raise

    @staticmethod
    def _validate_event(event: dict[str, Any]) -> dict[str, Any]:
        try:
            from zephyr.audit_trail.models import AuditEntryV1, AuditEventType
            etype_str = event.get("event_type", "unknown")
            try:
                etype = AuditEventType(etype_str)
            except ValueError:
                etype = AuditEventType.UNKNOWN
            entry = AuditEntryV1(
                event_type=etype,
                agent_id=event.get("agent_id", ""),
                session_id=event.get("session_id", ""),
                target_path=event.get("target_path", ""),
                operation=event.get("operation", ""),
                status=event.get("status", ""),
                provenance=event.get("provenance", "direct_agent"),
            )
            validated = dict(event)
            validated["event_type"] = etype.value
            validated["provenance"] = entry.provenance.value
            return validated
        except ImportError:
            return event

    def write_with_cot(
        self,
        event: dict[str, Any],
        reasoning_trace: str = "",
    ) -> dict[str, Any]:
        if reasoning_trace:
            if len(reasoning_trace) > 500:
                reasoning_trace = reasoning_trace[:500]
            event["reasoning_trace"] = reasoning_trace
            event["cot_hash"] = hashlib.sha256(reasoning_trace.encode("utf-8")).hexdigest()
        chain_hash = self.write(event)
        return {"chain_hash": chain_hash, "cot_hash": event.get("cot_hash", "")}

    def _write_locked(self, event: dict[str, Any]) -> str:
        prev_chain_hash = self._read_chain_state()
        self._lamport_counter += 1
        self._entry_seq += 1

        event_data = dict(event)
        event_data["prev_hash"] = prev_chain_hash
        event_data["timestamp"] = event_data.get("timestamp") or datetime.now(UTC).isoformat()
        event_data["lamport_time"] = self._lamport_counter
        event_data["lamport_clock_ide"] = self._ide_source
        event_data["lamport_clock_counter"] = self._lamport_counter
        event_data["ide_source"] = self._ide_source

        if "entry_id" not in event_data or not event_data["entry_id"]:
            prefix = "AUD-F" if event_data.get("event_type") in ("file_detail", "file_read", "file_write", "file_delete") else "AUD-T"
            event_data["entry_id"] = _generate_entry_id(prefix, self._entry_seq)

        event_json = json.dumps(event_data, ensure_ascii=False, sort_keys=True, default=str)
        chain_hash = hashlib.sha256(event_json.encode("utf-8")).hexdigest()
        event_data["entry_hash"] = chain_hash

        if self._hmac_key:
            hmac_sig = hmac.new(
                self._hmac_key,
                event_json.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            event_data["hmac_signature"] = hmac_sig

        final_json = json.dumps(event_data, ensure_ascii=False, sort_keys=True, default=str)

        self._append_atomic(final_json)
        self._write_chain_state(chain_hash)
        self._save_lamport_counter()

        if self._enable_merkle:
            self._current_batch_hashes.append(chain_hash)
            if len(self._current_batch_hashes) >= self._merkle_batch_size:
                self._finalize_merkle_batch()

        _logger.info("AuditWriter: wrote event #%d, chain_hash=%s, lamport=%d", self.event_count, chain_hash[:16], self._lamport_counter)
        return chain_hash

    def finalize_current_batch(self) -> str | None:
        with self._lock:
            if not self._current_batch_hashes:
                return None
            return self._finalize_merkle_batch()

    def _finalize_merkle_batch(self) -> str | None:
        if not self._current_batch_hashes:
            return None
        from zephyr.audit_trail.integrity import MerkleAggregator
        merkle_root = MerkleAggregator.build(self._current_batch_hashes)
        batch_id = f"batch-{self._lamport_counter}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        batch_record = {
            "batch_id": batch_id,
            "merkle_root": merkle_root,
            "entry_count": len(self._current_batch_hashes),
            "first_hash": self._current_batch_hashes[0],
            "last_hash": self._current_batch_hashes[-1],
            "finalized_at": datetime.now(UTC).isoformat(),
            "lamport_range": [self._lamport_counter - len(self._current_batch_hashes) + 1, self._lamport_counter],
        }
        self._save_merkle_batch(batch_record)
        self._current_batch_hashes = []
        self._save_pending_batch()
        _logger.info("Merkle batch finalized: %s, root=%s, entries=%d", batch_id, merkle_root[:16], batch_record["entry_count"])
        return merkle_root

    def _append_atomic(self, event_json: str) -> None:
        try:
            self._data_dir.mkdir(parents=True, exist_ok=True)
            with open(self._event_log_path, "a", encoding="utf-8") as f:
                f.write(event_json + "\n")
                f.flush()
                os.fsync(f.fileno())
        except (PermissionError, OSError):
            raise

    def _read_chain_state(self) -> str:
        if self._chain_state_path.exists():
            data = json.loads(self._chain_state_path.read_text(encoding="utf-8"))
            return data.get("chain_hash", "")
        return ""

    def _write_chain_state(self, chain_hash: str) -> None:
        tmp_path = self._chain_state_path.with_name(
            f"{self._chain_state_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
        )
        content = json.dumps(
            {"chain_hash": chain_hash, "updated_at": datetime.now(UTC).isoformat(), "lamport_time": self._lamport_counter, "entry_seq": self._entry_seq}, indent=2
        )
        try:
            tmp_path.write_text(content, encoding="utf-8")
            os.replace(tmp_path, self._chain_state_path)
        except (PermissionError, OSError):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

    def _load_lamport_counter(self) -> int:
        if self._chain_state_path.exists():
            try:
                data = json.loads(self._chain_state_path.read_text(encoding="utf-8"))
                return data.get("lamport_time", 0)
            except (json.JSONDecodeError, OSError):
                return 0
        return 0

    def _load_entry_seq(self) -> int:
        if self._chain_state_path.exists():
            try:
                data = json.loads(self._chain_state_path.read_text(encoding="utf-8"))
                return data.get("entry_seq", 0)
            except (json.JSONDecodeError, OSError):
                return 0
        return 0

    def _save_lamport_counter(self) -> None:
        pass

    def _load_pending_batch(self) -> list[str]:
        if self._merkle_state_path.exists():
            try:
                data = json.loads(self._merkle_state_path.read_text(encoding="utf-8"))
                return data.get("pending_hashes", [])
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def _save_pending_batch(self) -> None:
        tmp_path = self._merkle_state_path.with_name(
            f"{self._merkle_state_path.name}.{os.getpid()}.{threading.get_ident()}.tmp"
        )
        content = json.dumps({"pending_hashes": self._current_batch_hashes}, indent=2)
        try:
            tmp_path.write_text(content, encoding="utf-8")
            os.replace(tmp_path, self._merkle_state_path)
        except (PermissionError, OSError):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def _save_merkle_batch(self, batch_record: dict[str, Any]) -> None:
        batch_dir = self._data_dir / "merkle_batches"
        batch_dir.mkdir(parents=True, exist_ok=True)
        batch_file = batch_dir / f"{batch_record['batch_id']}.json"
        tmp_path = batch_file.with_name(f"{batch_file.name}.{os.getpid()}.tmp")
        try:
            tmp_path.write_text(json.dumps(batch_record, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp_path, batch_file)
        except (PermissionError, OSError):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    def get_merkle_batches(self) -> list[dict[str, Any]]:
        batch_dir = self._data_dir / "merkle_batches"
        if not batch_dir.exists():
            return []
        batches: list[dict[str, Any]] = []
        for f in sorted(batch_dir.glob("batch-*.json")):
            try:
                batches.append(json.loads(f.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue
        return batches

    def merge_lamport(self, remote_lamport: int) -> int:
        self._lamport_counter = max(self._lamport_counter, remote_lamport) + 1
        return self._lamport_counter
