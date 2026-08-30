# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.trackers.import_surface_tracker
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/security/test_import_surface_tracker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Import表面积负债追踪 — SBS 0-100 + shared burden score.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: import_surface_tracker.py
# 层: 算法
# - id: A1
#   name_zh: ① ImportSurfaceTracker
#   name_en: ImportSurfaceTracker
#   intro: Import表面积 (SBS) 负债追踪.
#   desc: Import表面积 (SBS) 负债追踪.；公共方法（定义序）: compute_sbs, analyze_file；源码 L51-L71
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ImportSurfaceTracker
#   downstream: tests/governance/security/test_import_surface_tracker.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
