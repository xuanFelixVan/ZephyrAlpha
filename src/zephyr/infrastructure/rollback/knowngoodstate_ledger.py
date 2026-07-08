# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.knowngoodstate_ledger
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
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
# [A_module] module_id=MOD-INF_knowngoodstate_ledger | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
KnowngoodstateLedger — 已验证正确状态收据。

依据: 蓝图 MOD-INF-021 §7 Phase 10 + §6.17 B124

回滚后自动声明当前状态为 "已知好状态" (known good state):
    每个 commit_sha -> 验证轮次 -> 通过则签名 + 时间戳。
    下次回滚目标若存在 knowngoodstate 记录，优先选择。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class KnownGoodRecord:
    commit_sha: str
    verified_at: str
    verification_method: str
    file_count: int
    db_integrity_pass: bool
    signature: str


class KnowngoodstateLedger:
    LEDGER_FILE: str = ".zephyr/knowngoodstate_ledger.jsonl"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._ledger_path = self._project_root / self.LEDGER_FILE

    def declare_known_good(
        self,
        commit_sha: str,
        verification_method: str = "post_rollback_verification",
        file_count: int = 0,
        db_integrity_pass: bool = True,
    ) -> KnownGoodRecord:
        now = datetime.now(UTC).isoformat()
        raw = f"{commit_sha}|{now}|{verification_method}|{file_count}|{db_integrity_pass}"
        signature = hashlib.sha256(raw.encode()).hexdigest()

        record = KnownGoodRecord(
            commit_sha=commit_sha,
            verified_at=now,
            verification_method=verification_method,
            file_count=file_count,
            db_integrity_pass=db_integrity_pass,
            signature=signature,
        )

        entry = {
            "commit_sha": record.commit_sha,
            "verified_at": record.verified_at,
            "verification_method": record.verification_method,
            "file_count": record.file_count,
            "db_integrity_pass": record.db_integrity_pass,
            "signature": record.signature,
        }

        self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return record

    def get_latest_known_good(self, limit: int = 5) -> list[KnownGoodRecord]:
        records: list[KnownGoodRecord] = []
        if not self._ledger_path.exists():
            return records

        with open(self._ledger_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    records.append(
                        KnownGoodRecord(
                            commit_sha=entry["commit_sha"],
                            verified_at=entry["verified_at"],
                            verification_method=entry["verification_method"],
                            file_count=entry["file_count"],
                            db_integrity_pass=entry["db_integrity_pass"],
                            signature=entry["signature"],
                        )
                    )
                except (json.JSONDecodeError, KeyError):
                    continue

        return records[-limit:]

    def find_known_good(self, commit_sha: str) -> KnownGoodRecord | None:
        records = self.get_latest_known_good(limit=1000)
        for r in reversed(records):
            if r.commit_sha == commit_sha:
                return r
        return None

    def is_known_good(self, commit_sha: str) -> bool:
        return self.find_known_good(commit_sha) is not None
