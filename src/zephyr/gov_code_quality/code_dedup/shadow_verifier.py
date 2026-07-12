# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.shadow_verifier
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/adversarial/test_shadow_verifier.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_shadow_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""影子清单验证器 — size sanity check + semantic验证 + 覆盖度报告."""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ShadowVerifyResult:
    manifest_size: int = 0
    original_size: int = 0
    size_ok: bool = False
    semantic_ok: bool = False
    coverage_ratio: float = 0.0
    issues: list[str] = field(default_factory=list)


class ShadowVerifier:
    """影子清单验证器."""

    _MAX_RATIO: float = 1.2
    _MIN_COVERAGE: float = 0.80

    def verify_size(self, manifest_path: str | Path, original_dir: str | Path) -> tuple[bool, int, int]:
        """Manifest size ≤ 120% original."""
        m_size = self._dir_size(Path(manifest_path))
        o_size = self._dir_size(Path(original_dir))

        if o_size == 0:
            return True, m_size, o_size

        ok = (m_size / o_size) <= self._MAX_RATIO
        return ok, m_size, o_size

    def verify_semantic(self, manifest_functions: set[str], original_functions: set[str]) -> tuple[bool, float]:
        """语义验证——覆盖率 ≥ 80%."""
        if not original_functions:
            return True, 1.0

        coverage = len(manifest_functions & original_functions) / len(original_functions)
        return coverage >= self._MIN_COVERAGE, coverage

    def generate_dashboard_card(
        self,
        manifest_path: str | Path,
        original_dir: str | Path,
        manifest_funcs: set[str],
        original_funcs: set[str],
    ) -> ShadowVerifyResult:
        """生成影子清单验证仪表盘 card."""
        size_ok, m_size, o_size = self.verify_size(manifest_path, original_dir)
        semantic_ok, coverage = self.verify_semantic(manifest_funcs, original_funcs)

        issues: list[str] = []
        if not size_ok:
            issues.append(f"影子清单大小超标: {m_size}/{o_size} = {m_size / o_size:.1%}")
        if not semantic_ok:
            issues.append(f"函数覆盖率不足: {coverage:.1%} < {self._MIN_COVERAGE:.0%}")

        return ShadowVerifyResult(
            manifest_size=m_size,
            original_size=o_size,
            size_ok=size_ok,
            semantic_ok=semantic_ok,
            coverage_ratio=round(coverage, 3),
            issues=issues,
        )

    @staticmethod
    def _dir_size(path: Path) -> int:
        if not path.exists():
            return 0
        if path.is_file():
            return path.stat().st_size
        total = 0
        for root, _, files in os.walk(str(path)):
            for f in files:
                fp = Path(root) / f
                try:
                    total += fp.stat().st_size
                except OSError:
                    pass
        return total
