# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.shadow_trust_validator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""影子信任验证器 — ImportError 防护回路."""

from __future__ import annotations

from pathlib import Path


class ShadowTrustValidator:
    """影子清单信任链验证."""

    def validate_imports(self, manifest_functions: list[str], codebase_root: str | Path) -> dict:
        """验证影子清单中的导入在codebase中确实存在."""
        root = Path(codebase_root)
        missing = []
        verified = 0

        for fname in manifest_functions:
            found = False
            for py_file in root.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8")
                    if fname in content:
                        found = True
                        verified += 1
                        break
                except (OSError, UnicodeDecodeError):
                    pass
            if not found:
                missing.append(fname)

        return {
            "verified": verified,
            "missing": len(missing),
            "missing_functions": missing[:10],
        }
