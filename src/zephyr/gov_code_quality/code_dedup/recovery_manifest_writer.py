# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.recovery_manifest_writer
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/resilience/test_recovery_manifest_writer.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_recovery_manifest_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Recovery Manifest Writer — R2纯文本base64 Manifest."""

import base64
import hashlib
from datetime import UTC, datetime
from pathlib import Path


class RecoveryManifestWriter:
    """R2 纯文本 Recovery Manifest."""

    def write(self, affected_files: list[str | Path], output_path: str | Path | None = None) -> dict:
        """生成base64编码的Manifest."""
        if output_path is None:
            output_path = Path("data/cache/recovery_manifest.txt")
        path = Path(output_path)

        records = []
        total_sha = hashlib.sha256()
        for fp in affected_files:
            p = Path(fp)
            if p.exists():
                content = p.read_bytes()
                encoded = base64.b64encode(content).decode("ascii")
                sha = hashlib.sha256(content).hexdigest()
                records.append(f"FILE: {fp}\nSHA256: {sha}\nDATA: {encoded}\n---")
                total_sha.update(f"{fp}:{sha}\n".encode())

        manifest = "\n".join(records)
        manifest += f"\n=== MANIFEST_SHA256: {total_sha.hexdigest()} ==="
        manifest += f"\n=== GENERATED_AT: {datetime.now(UTC).isoformat()} ==="

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(manifest, encoding="utf-8")

        return {
            "file_count": len(affected_files),
            "manifest_sha256": total_sha.hexdigest(),
            "output": str(path),
        }
