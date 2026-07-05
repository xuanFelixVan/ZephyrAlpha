# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.pre_apply_integrity_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/rule_enforcement/test_pre_apply_integrity_gate.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/governance/code_dedup/test_pre_apply_integrity_gate.py
# [A_module] module_id=MOD-UNK_pre_apply_integrity_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Pre-Apply 完整性门 — SHA256重新验证."""

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
