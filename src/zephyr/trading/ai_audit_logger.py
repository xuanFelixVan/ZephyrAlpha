# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.ai_audit_logger
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_ai_audit_logger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AiAuditLogger — AI 行为审计日志
================================
蓝图: ARC-0001 §6.1
所有 AI 行为写入结构化 JSONL，不可变、追加式。

5.17.3 修复：添加 SHA-256 哈希链 + 篡改检测，实现真正的不可变性。
"""

import hashlib
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG

_GENESIS_HASH = "0" * 64


class _LogEntry(BaseModel):
    model_config = BASE_CONFIG
    log_type: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    session_id: str = ""
    detail: dict[str, Any] = {}
    prev_hash: str = ""
    entry_hash: str = ""


class AiAuditLogger:
    """AI 行为审计日志——所有 AI 决策/执行的不可变记录。

    5.17.3 修复：每条日志通过 SHA-256 哈希链关联前一条日志，重启后链恢复连续。
    提供 verify_integrity() 方法用于检测篡改。

    借鉴:
      - Claude Code: Markdown 文件作为持久记忆
      - K8s Audit Log: 所有 API 调用记录
    """

    def __init__(self, log_dir: Path, session_id: str = "") -> None:
        self._log_dir = Path(log_dir)
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._session_id = session_id
        self._lock = threading.Lock()
        self._pending_count = 0
        self._last_hash = _GENESIS_HASH
        self._load_last_hash()

    def _load_last_hash(self) -> None:
        """从今日日志最后一行恢复 _last_hash（重启后链连续）。"""
        try:
            f = self._date_file()
            if not f.exists():
                return
            last_hash = _GENESIS_HASH
            with f.open(encoding="utf-8") as fp:
                for line in fp:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        eh = entry.get("entry_hash")
                        if eh:
                            last_hash = eh
                    except json.JSONDecodeError:
                        continue
            self._last_hash = last_hash
        except Exception:
            pass

    def _date_file(self) -> Path:
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self._log_dir / f"ai_audit_{date_str}.jsonl"

    def _compute_hash(self, entry_dict: dict[str, Any]) -> str:
        """对 entry 计算 SHA-256（排除 entry_hash 字段本身）。"""
        payload = {k: v for k, v in entry_dict.items() if k != "entry_hash"}
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _write(self, entry: _LogEntry) -> None:
        with self._lock:
            entry.prev_hash = self._last_hash
            entry_dict = entry.model_dump()
            entry_hash = self._compute_hash(entry_dict)
            entry.entry_hash = entry_hash
            line = entry.model_dump_json() + "\n"
            with self._date_file().open("a", encoding="utf-8") as f:
                f.write(line)
            self._last_hash = entry_hash
            self._pending_count += 1

    def verify_integrity(self, date_str: str | None = None) -> bool:
        """验证日志文件 hash 链完整性。

        Args:
            date_str: 指定日期（YYYY-MM-DD），默认验证今日日志。

        Returns:
            True=链完整，False=发现篡改或断裂。
        """
        if date_str:
            f = self._log_dir / f"ai_audit_{date_str}.jsonl"
        else:
            f = self._date_file()
        if not f.exists():
            return True
        prev = _GENESIS_HASH
        try:
            with f.open(encoding="utf-8") as fp:
                for line_no, line in enumerate(fp, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        return False
                    stored_prev = entry.get("prev_hash", "")
                    stored_hash = entry.get("entry_hash", "")
                    if stored_prev != prev:
                        return False
                    recomputed = self._compute_hash(entry)
                    if recomputed != stored_hash:
                        return False
                    prev = stored_hash
            return True
        except Exception:
            return False

    def log_inference(
        self,
        model: str,
        work_type: str,
        input_snippet: str = "",
        output_snippet: str = "",
        latency_ms: float = 0.0,
        layer: str = "local",
    ) -> None:
        self._write(
            _LogEntry(
                log_type="inference",
                session_id=self._session_id,
                detail={
                    "model": model,
                    "work_type": work_type,
                    "input_text_snippet": input_snippet[:200],
                    "output_snippet": output_snippet[:200],
                    "latency_ms": latency_ms,
                    "layer": layer,
                },
            )
        )

    def log_embedding(
        self,
        model: str,
        text_length: int,
        dim: int,
        latency_ms: float = 0.0,
        layer: str = "local",
    ) -> None:
        self._write(
            _LogEntry(
                log_type="embedding",
                session_id=self._session_id,
                detail={
                    "model": model,
                    "text_length": text_length,
                    "dim": dim,
                    "latency_ms": latency_ms,
                    "layer": layer,
                },
            )
        )

    def log_routing(
        self,
        task_id: str,
        from_layer: str,
        to_layer: str,
        reason: str = "",
    ) -> None:
        self._write(
            _LogEntry(
                log_type="routing",
                session_id=self._session_id,
                detail={
                    "task_id": task_id,
                    "from_layer": from_layer,
                    "to_layer": to_layer,
                    "reason": reason,
                },
            )
        )

    def log_ambiguity(
        self,
        entry_id: str,
        task_id: str,
        context: str,
        options: list[dict[str, str]] | None = None,
    ) -> None:
        self._write(
            _LogEntry(
                log_type="ambiguity",
                session_id=self._session_id,
                detail={
                    "entry_id": entry_id,
                    "task_id": task_id,
                    "context": context,
                    "options": options or [],
                },
            )
        )

    def log_health(
        self,
        capability_id: str,
        status: str,
        latency_ms: float = 0.0,
        error: str = "",
    ) -> None:
        self._write(
            _LogEntry(
                log_type="health",
                session_id=self._session_id,
                detail={
                    "capability_id": capability_id,
                    "status": status,
                    "latency_ms": latency_ms,
                    "error": error,
                },
            )
        )

    def log_registration(
        self,
        capability_id: str,
        event: str,
    ) -> None:
        self._write(
            _LogEntry(
                log_type="registration",
                session_id=self._session_id,
                detail={
                    "capability_id": capability_id,
                    "event": event,
                },
            )
        )

    def has_pending_flush(self) -> bool:
        return self._pending_count > 0

    def flush(self) -> None:
        with self._lock:
            self._pending_count = 0

    def query(self, filters: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for f in sorted(self._log_dir.glob("ai_audit_*.jsonl")):
            # 5.169 修复：用 context manager 防止文件句柄泄漏
            with f.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    match = True
                    for k, v in filters.items():
                        if entry.get(k) != v:
                            detail = entry.get("detail", {})
                            if detail.get(k) != v:
                                match = False
                                break
                    if match:
                        results.append(entry)
        return results
