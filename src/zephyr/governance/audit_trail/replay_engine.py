# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §9
# [MODULE] zephyr.governance.audit_trail.replay_engine
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.shared.io.streaming_reader
# [CONSUMERS] audit-orchestrator.pipeline_runner; integrity
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 重放不修改任何审计数据; 只读+比对
# [MODIFY-GUARD] 重放格式变更必须同步 evidence_pack.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 重放失败返回mismatch
# [TESTS] tests/audit-orchestrator/test_replay_engine.py
# [A_module] module_id=MOD-GOV_replay_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from zephyr.shared.io.streaming_reader import stream_jsonl, tail_jsonl

logger = logging.getLogger(__name__)

__all__ = ["ReplayEngine"]


class ReplayEngine:
    def __init__(self, evidence_dir: Path | None = None) -> None:
        self._evidence_dir = Path(evidence_dir or Path("data/audit_evidence"))

    def replay(self, evidence_id: str) -> dict[str, Any]:
        evidence_path = self._find_evidence(evidence_id)
        if evidence_path is None:
            return {"status": "not_found", "evidence_id": evidence_id, "match": False}

        try:
            data = json.loads(evidence_path.read_text(encoding="utf-8"))
            findings = data.get("findings", [])

            recomputed = self._recompute_findings(findings)

            match = recomputed["hash"] == data.get("evidence_hash", "")
            return {
                "status": "replayed",
                "evidence_id": evidence_id,
                "audit_id": data.get("audit_id", ""),
                "finding_count": len(findings),
                "match": match,
                "original_hash": data.get("evidence_hash", ""),
                "recomputed_hash": recomputed["hash"],
                "replayed_at": datetime.now().isoformat(),
            }
        except Exception as exc:
            logger.error("ReplayEngine.replay failed: %s", exc)
            return {"status": "error", "evidence_id": evidence_id, "match": False, "error": str(exc)}

    def replay_all(self) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for path in sorted(self._evidence_dir.glob("*_evidence.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                findings = data.get("findings", [])
                recomputed = self._recompute_findings(findings)
                match = recomputed["hash"] == data.get("evidence_hash", "")
                results.append(
                    {
                        "audit_id": data.get("audit_id", ""),
                        "evidence_id": data.get("evidence_hash", "")[:16],
                        "match": match,
                    }
                )
            except Exception:
                continue

        total = len(results)
        matched = sum(1 for r in results if r["match"])
        return {
            "total": total,
            "matched": matched,
            "mismatched": total - matched,
            "all_ok": total > 0 and matched == total,
            "results": results,
        }

    def _find_evidence(self, evidence_id: str) -> Path | None:
        for path in self._evidence_dir.glob("*_evidence.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if data.get("evidence_hash", "")[:16] == evidence_id:
                    return path
            except Exception:
                continue
        return None

    def _recompute_findings(self, findings: list[dict[str, Any]]) -> dict[str, str]:
        serialized = json.dumps(findings, sort_keys=True, ensure_ascii=False, default=str)
        return {"hash": hashlib.sha256(serialized.encode("utf-8")).hexdigest()}

    def replay_jsonl(self, jsonl_path: Path | str, last_n: int = 100) -> dict[str, Any]:
        recent = tail_jsonl(jsonl_path, n=last_n)
        results: list[dict[str, Any]] = []
        for record in recent:
            evidence_id = record.get("evidence_hash", "")[:16]
            if not evidence_id:
                continue
            findings = record.get("findings", [])
            recomputed = self._recompute_findings(findings)
            match = recomputed["hash"] == record.get("evidence_hash", "")
            results.append({"evidence_id": evidence_id, "match": match})

        total = len(results)
        matched = sum(1 for r in results if r["match"])
        return {
            "total": total,
            "matched": matched,
            "mismatched": total - matched,
            "all_ok": total > 0 and matched == total,
        }

    def stream_replay_jsonl(self, jsonl_path: Path | str) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for record in stream_jsonl(jsonl_path):
            evidence_id = record.get("evidence_hash", "")[:16]
            if not evidence_id:
                continue
            findings = record.get("findings", [])
            recomputed = self._recompute_findings(findings)
            match = recomputed["hash"] == record.get("evidence_hash", "")
            results.append({"evidence_id": evidence_id, "match": match})

        total = len(results)
        matched = sum(1 for r in results if r["match"])
        return {
            "total": total,
            "matched": matched,
            "mismatched": total - matched,
            "all_ok": total > 0 and matched == total,
        }


class ReplayResult:
    def __init__(self, replay_id="", success=True, entries_replayed=0, errors=None):
        self.replay_id = replay_id
        self.success = success
        self.entries_replayed = entries_replayed
        self.errors = errors or []


class ReplaySnapshot:
    def __init__(self, snapshot_id="", timestamp=None, entries=None, hash_value=""):
        self.snapshot_id = snapshot_id
        self.timestamp = timestamp
        self.entries = entries or []
        self.hash_value = hash_value
