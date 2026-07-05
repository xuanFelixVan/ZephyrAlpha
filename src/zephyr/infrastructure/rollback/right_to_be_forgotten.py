# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.right_to_be_forgotten
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_right_to_be_forgotten | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Right to be Forgotten — GDPR 遗忘权合规检查器。

依据：
    蓝图 MOD-INF-021 §6.13 B78 + 决策 D-021-17 + §9 exit code 19
    任务卡 TASK-INF-0252

功能：
    - right_to_be_forgotten_registry: 被遗忘权用户哈希集维护
    - 回滚恢复含被遗忘用户数据 → 自动净化
    - 无法自动净化 → exit 19 GDPR_BLOCKED → DEFER_TO_HUMAN
    - 对标 EU GDPR Article 17 "Right to be forgotten"
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXIT_GDPR_BLOCKED = 19

SENSITIVE_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"),
]


@dataclass
class ForgottenUser:
    user_hash: str
    registered_at: str
    request_id: str
    reason: str = "GDPR Article 17"


@dataclass
class PurgeResult:
    purged: bool
    files_purged: list[str]
    files_blocked: list[str]
    gdpr_blocked: bool = False
    exit_code: int = 0


@dataclass
class SensitiveMatch:
    pattern: str
    matched_content: str
    file_path: str
    line_number: int = 0


class RightToBeForgotten:
    def __init__(self, registry_dir: Path | None = None) -> None:
        self._registry_dir = registry_dir or Path("data/rollback/gdpr")
        self._registry_path = self._registry_dir / "right_to_be_forgotten_registry.json"
        self._forgotten_hashes: set[str] = set()
        self._load_registry()

    def register_forgotten_user(
        self,
        identifier: str,
        request_id: str = "",
        reason: str = "GDPR Article 17",
    ) -> ForgottenUser:
        user_hash = self._hash_identifier(identifier)
        forgotten = ForgottenUser(
            user_hash=user_hash,
            registered_at=datetime.now(UTC).isoformat(),
            request_id=request_id or f"GDPR-REQ-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            reason=reason,
        )
        self._forgotten_hashes.add(user_hash)
        self._save_registry(forgotten)
        return forgotten

    def is_forgotten(self, identifier: str) -> bool:
        return self._hash_identifier(identifier) in self._forgotten_hashes

    def scan_files_for_forgotten_data(
        self,
        files: list[str],
        project_root: Path | None = None,
    ) -> list[SensitiveMatch]:
        root = project_root or Path.cwd()
        matches: list[SensitiveMatch] = []

        email_hashes: set[str] = set()
        ssn_hashes: set[str] = set()

        for file_path in files:
            full_path = root / file_path
            if not full_path.exists():
                continue

            try:
                content = full_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue

            emails = SENSITIVE_PATTERNS[0].findall(content)
            for email in emails:
                email_hash = self._hash_identifier(email)
                if email_hash in self._forgotten_hashes:
                    email_hashes.add(email_hash)
                    matches.append(
                        SensitiveMatch(
                            pattern="email",
                            matched_content=self._mask_identifier(email),
                            file_path=file_path,
                        )
                    )

            ssns = SENSITIVE_PATTERNS[3].findall(content)
            for ssn in ssns:
                ssn_hash = self._hash_identifier(ssn)
                if ssn_hash in self._forgotten_hashes:
                    ssn_hashes.add(ssn_hash)
                    matches.append(
                        SensitiveMatch(
                            pattern="ssn",
                            matched_content=self._mask_identifier(ssn),
                            file_path=file_path,
                        )
                    )

        return matches

    def purge_sensitive_data(
        self,
        files: list[str],
        project_root: Path | None = None,
    ) -> PurgeResult:
        root = project_root or Path.cwd()
        matches = self.scan_files_for_forgotten_data(files, root)

        if not matches:
            return PurgeResult(
                purged=True,
                files_purged=[],
                files_blocked=[],
            )

        files_purged: list[str] = []
        files_blocked: list[str] = []

        for file_path in files:
            full_path = root / file_path
            if not full_path.exists():
                continue

            file_matches = [m for m in matches if m.file_path == file_path]

            if not file_matches:
                continue

            try:
                content = full_path.read_text(encoding="utf-8")

                for m in file_matches:
                    content = self._mask_content(content, m)

                full_path.write_text(content, encoding="utf-8")
                files_purged.append(file_path)
            except Exception:
                files_blocked.append(file_path)

        gdpr_blocked = len(files_blocked) > 0
        return PurgeResult(
            purged=not gdpr_blocked,
            files_purged=files_purged,
            files_blocked=files_blocked,
            gdpr_blocked=gdpr_blocked,
            exit_code=EXIT_GDPR_BLOCKED if gdpr_blocked else 0,
        )

    def check_restore_safety(
        self,
        files_to_restore: list[str],
        snapshot_data: str,
    ) -> PurgeResult:
        matches: list[SensitiveMatch] = []
        for identifier_hash in self._forgotten_hashes:
            if identifier_hash in snapshot_data:
                matches.append(
                    SensitiveMatch(
                        pattern="gdpr_registry_hash",
                        matched_content=identifier_hash,
                        file_path="snapshot",
                    )
                )

        if matches:
            return PurgeResult(
                purged=False,
                files_purged=[],
                files_blocked=files_to_restore,
                gdpr_blocked=True,
                exit_code=EXIT_GDPR_BLOCKED,
            )

        return self.purge_sensitive_data(files_to_restore)

    def _hash_identifier(self, identifier: str) -> str:
        normalized = identifier.strip().lower()
        return hashlib.sha256(f"gdpr:forgotten:{normalized}:salt-v1".encode()).hexdigest()

    def _mask_identifier(self, identifier: str) -> str:
        if len(identifier) <= 4:
            return "****"
        return identifier[:2] + "*" * (len(identifier) - 4) + identifier[-2:]

    def _mask_content(self, content: str, match: SensitiveMatch) -> str:
        if match.pattern == "email":
            return SENSITIVE_PATTERNS[0].sub("[REDACTED-EMAIL]", content)
        if match.pattern == "ssn":
            return SENSITIVE_PATTERNS[3].sub("[REDACTED-SSN]", content)
        return content.replace(match.matched_content, "[REDACTED]")

    def _load_registry(self) -> None:
        if not self._registry_path.exists():
            return
        try:
            data = json.loads(self._registry_path.read_text(encoding="utf-8"))
            for entry in data.get("forgotten_users", []):
                self._forgotten_hashes.add(entry["user_hash"])
        except (json.JSONDecodeError, KeyError):
            pass

    def _save_registry(self, forgotten: ForgottenUser) -> None:
        self._registry_dir.mkdir(parents=True, exist_ok=True)

        existing: list[dict[str, Any]] = []
        if self._registry_path.exists():
            try:
                data = json.loads(self._registry_path.read_text(encoding="utf-8"))
                existing = data.get("forgotten_users", [])
            except (json.JSONDecodeError, KeyError):
                pass

        existing.append(
            {
                "user_hash": forgotten.user_hash,
                "registered_at": forgotten.registered_at,
                "request_id": forgotten.request_id,
                "reason": forgotten.reason,
            }
        )

        self._registry_path.write_text(
            json.dumps(
                {
                    "version": "1.0.0",
                    "compliance": "GDPR Article 17",
                    "last_updated": datetime.now(UTC).isoformat(),
                    "forgotten_users": existing,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
