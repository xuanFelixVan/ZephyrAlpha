# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.security_governance.tamper_evident_log
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.gov_audit.writer
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] pending_review
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_tamper_evident_log | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
import logging

logger = logging.getLogger(__name__)

import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path


def _resolve_hmac_key() -> bytes:
    """5.17.5 修复：解析 HMAC 密钥（env > 兜底默认）。

    生产环境 MUST 设置 ZEPHYR_TAMPER_HMAC_SECRET 环境变量。
    缺失时回退到派生密钥（仅 dev/test 用，启动时 WARN）。
    """
    key = os.environ.get("ZEPHYR_TAMPER_HMAC_SECRET", "")
    if key:
        return key.encode("utf-8")
    # 兜底：仅用于 dev/test，启动告警（禁止用于生产）
    logger.warning(
        "TamperEvidentLog: ZEPHYR_TAMPER_HMAC_SECRET 未设置，使用兜底派生密钥"
        "（仅 dev/test，生产环境 MUST 配置 env var）"
    )
    # 派生而非硬编码字符串，避免相同密钥跨项目复用
    import getpass
    import socket
    _material = f"zephyr:{getpass.getuser()}:{socket.gethostname()}".encode("utf-8")
    return hashlib.sha256(_material).digest()


@dataclass
class LogEntry:
    entry_id: str
    action: str
    data: str
    prev_hash: str
    timestamp: float = field(default_factory=time.time)
    hash: str = ""
    hmac_signature: str = ""


class TamperEvidentLog:
    def __init__(self, log_path: str | None = None):
        """初始化 TamperEvidentLog。

        Args:
            log_path: 日志文件绝对路径。None 时使用项目根的
                logs/tamper_evident.jsonl 绝对路径（铁律：禁相对路径）。
        """
        if log_path is None:
            _project_root = Path(__file__).resolve().parents[4]
            self._log_path = _project_root / "logs" / "tamper_evident.jsonl"
        else:
            self._log_path = Path(log_path)
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_secure_perms()
        self._hmac_key: bytes = _resolve_hmac_key()
        self._chain: list[LogEntry] = []
        self._last_hash: str = "0" * 64
        self._counter: int = 0
        self._load_chain()

    def _ensure_secure_perms(self) -> None:
        if os.name == "nt":
            return
        try:
            if self._log_path.exists():
                os.chmod(str(self._log_path), 0o600)
        except OSError:
            pass

    def _compute_hmac(self, hash_value: str) -> str:
        return hmac.new(self._hmac_key, hash_value.encode("utf-8"), hashlib.sha256).hexdigest()

    def _load_chain(self) -> None:
        if not self._log_path.exists():
            return
        with open(self._log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = LogEntry(
                        entry_id=data.get("entry_id", ""),
                        action=data.get("action", ""),
                        data=data.get("data", ""),
                        prev_hash=data.get("prev_hash", ""),
                        timestamp=data.get("timestamp", 0.0),
                        hash=data.get("hash", ""),
                        hmac_signature=data.get("hmac_signature", ""),
                    )
                    self._chain.append(entry)
                    self._last_hash = entry.hash
                    self._counter += 1
                except (json.JSONDecodeError, KeyError):
                    continue

    def append(self, action: str, data: str) -> LogEntry:
        self._counter += 1
        now = time.time()
        raw = f"{self._counter}:{action}:{data}:{now}:{self._last_hash}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        sig = self._compute_hmac(h)

        entry = LogEntry(
            entry_id=f"tel-{self._counter:06d}",
            action=action,
            data=data,
            prev_hash=self._last_hash,
            timestamp=now,
            hash=h,
            hmac_signature=sig,
        )
        self._chain.append(entry)
        self._last_hash = h

        new_file_created = not self._log_path.exists()
        with open(self._log_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "entry_id": entry.entry_id,
                        "action": entry.action,
                        "data": entry.data,
                        "prev_hash": entry.prev_hash,
                        "timestamp": entry.timestamp,
                        "hash": entry.hash,
                        "hmac_signature": entry.hmac_signature,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        if new_file_created:
            os.chmod(str(self._log_path), 0o600)

        try:
            from zephyr.gov_audit.writer import get_audit_writer

            get_audit_writer().write(
                {
                    "event_type": "budget_enforcement",
                    "action_type": action,
                    "agent_id": "budget-enforcer",
                    "target_path": str(self._log_path),
                    "operation": action,
                }
            )
        except Exception as e:
            logger.warning("suppressed error in tamper_evident_log", exc_info=True)

        return entry

    def verify(self) -> tuple[bool, int]:
        prev = "0" * 64
        for i, entry in enumerate(self._chain):
            raw = f"{i + 1}:{entry.action}:{entry.data}:{entry.timestamp}:{prev}"
            expected = hashlib.sha256(raw.encode()).hexdigest()
            if expected != entry.hash:
                return False, i
            # 5.17.5 修复：HMAC 校验（旧条目无签名则跳过，向后兼容）
            if entry.hmac_signature:
                expected_sig = self._compute_hmac(entry.hash)
                if expected_sig != entry.hmac_signature:
                    return False, i
            prev = entry.hash
        return True, len(self._chain)

    def recent(self, n: int = 20) -> list[LogEntry]:
        return self._chain[-n:]

    def chain_length(self) -> int:
        return len(self._chain)

    def tail_hash(self) -> str:
        return self._last_hash
