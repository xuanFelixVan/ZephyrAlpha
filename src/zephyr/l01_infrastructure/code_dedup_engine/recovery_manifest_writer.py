# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.recovery_manifest_writer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Recovery Manifest Writer — R2纯文本base64 Manifest."""

from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timezone
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
        manifest += f"\n=== GENERATED_AT: {datetime.now(timezone.utc).isoformat()} ==="

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(manifest, encoding="utf-8")

        return {
            "file_count": len(affected_files),
            "manifest_sha256": total_sha.hexdigest(),
            "output": str(path),
        }
