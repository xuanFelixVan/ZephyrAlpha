# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.pre_apply_integrity_gate

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Pre-Apply 完整性门 — SHA256重新验证."""

from __future__ import annotations

import hashlib
from pathlib import Path


class PreApplyIntegrityGate:
    """修复前完整性门."""

    def verify(self, file_path: str | Path, expected_sha256: str) -> tuple[bool, str]:
        """对即将修改的文件做SHA256验证——不匹配→ABORT."""
        path = Path(file_path)
        if not path.exists():
            return False, "FILE_NOT_FOUND"

        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected_sha256:
            return False, f"SHA_MISMATCH: expected={expected_sha256[:16]}... actual={actual[:16]}..."
        return True, "SHA256_OK"
