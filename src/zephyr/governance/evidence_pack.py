# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §8
# [MODULE] zephyr.governance.evidence_pack
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.integrity; replay_engine
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 证据包不可变性; 签名后禁止修改
# [MODIFY-GUARD] 证据格式变更必须同步 integrity.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 打包失败返回None
# [TESTS] tests/audit-orchestrator/test_evidence_pack.py
# [A_module] module_id=MOD-GOV_evidence_pack | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from zephyr.shared.io.serialization import dumps
import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["EvidencePack"]


class EvidencePack:
    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = Path(output_dir or Path("data/audit_evidence"))
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def pack(
        self, audit_id: str, findings: list[dict[str, Any]], metadata: dict[str, Any] | None = None
    ) -> dict[str, Any] | None:
        try:
            serialized = dumps(findings, sort_keys=True, ensure_ascii=False)
            evidence_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

            pack_data = {
                "audit_id": audit_id,
                "evidence_hash": evidence_hash,
                "created_at": datetime.now(UTC).isoformat(),
                "finding_count": len(findings),
                "findings": findings,
                "metadata": metadata or {},
            }

            output_path = self._output_dir / f"{audit_id}_evidence.json"
            import os

            tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
            try:
                tmp_path.write_text(
                    dumps(pack_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                os.replace(str(tmp_path), str(output_path))
            except Exception:
                try:
                    tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass
                raise

            return {
                "evidence_id": evidence_hash[:16],
                "path": str(output_path),
                "finding_count": len(findings),
                "hash": evidence_hash,
            }
        except Exception as exc:
            logger.error("EvidencePack.pack failed: %s", exc, exc_info=True)
            return None

    def verify(self, evidence_id: str) -> bool:
        for path in self._output_dir.glob("*_evidence.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                findings = data.get("findings", [])
                serialized = dumps(findings, sort_keys=True, ensure_ascii=False)
                current_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
                if current_hash[:16] == evidence_id:
                    return current_hash == data.get("evidence_hash", "")
            except Exception:
                continue
        return False

    def list_packs(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for path in sorted(self._output_dir.glob("*_evidence.json"), key=lambda p: p.stat().st_mtime, reverse=True):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                results.append(
                    {
                        "audit_id": data.get("audit_id", ""),
                        "evidence_hash": data.get("evidence_hash", "")[:16],
                        "finding_count": data.get("finding_count", 0),
                        "created_at": data.get("created_at", ""),
                    }
                )
            except Exception:
                continue
        return results