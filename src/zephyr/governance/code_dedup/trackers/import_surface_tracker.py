# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.trackers.import_surface_tracker
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/security/test_import_surface_tracker.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_import_surface_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Import表面积负债追踪 — SBS 0-100 + shared burden score."""

from pathlib import Path


class ImportSurfaceTracker:
    """Import表面积 (SBS) 负债追踪."""

    def compute_sbs(self, imports_count: int, max_healthy: int = 100) -> int:
        """SBS = min(100, imports * 100 / max_healthy)."""
        return min(100, int(imports_count / max_healthy * 100))

    def analyze_file(self, file_path: str | Path) -> dict:
        """分析单个文件的import表面积."""
        path = Path(file_path)
        if not path.exists():
            return {"file": str(file_path), "import_count": 0, "sbs": 0}

        source = path.read_text(encoding="utf-8")
        import_count = source.count("\nimport ") + source.count("\nfrom ")

        return {
            "file": str(file_path),
            "import_count": import_count,
            "sbs": self.compute_sbs(import_count),
        }
