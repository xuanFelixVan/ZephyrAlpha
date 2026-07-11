# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.thematic_clusterer
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/compliance/test_thematic_clusterer.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_thematic_clusterer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""主题聚类器 — 噪声信号比·告警疲劳缓解."""

from collections import defaultdict


class ThematicClusterer:
    """重复组主题聚类——将50组重复归约到3-5个主题."""

    def cluster(self, duplicate_groups: list[dict], max_clusters: int = 5) -> dict:
        """元组->主题"""
        themes: dict[str, list[dict]] = defaultdict(list)
        for group in duplicate_groups:
            members = group.get("members", [])
            paths = [m[0] for m in members]
            theme = self._classify(paths)
            themes[theme].append(group)

        top_themes = sorted(themes.items(), key=lambda x: len(x[1]), reverse=True)[:max_clusters]
        total = sum(len(g) for _, g in top_themes)
        noise_ratio = (len(duplicate_groups) - total) / max(len(duplicate_groups), 1)

        return {
            "themes": {t: len(g) for t, g in top_themes},
            "total_clustered": total,
            "noise_ratio": round(noise_ratio, 3),
            "recommendation": f"Top {len(top_themes)} themes cover {total}/{len(duplicate_groups)} groups",
        }

    @staticmethod
    def _classify(paths: list[str]) -> str:
        combined = "/".join(paths).lower()
        if "test" in combined:
            return "Test Patterns"
        if "shared" in combined:
            return "Shared Library"
        if any(kw in combined for kw in ("infrastructure", "l01_")):
            return "Infrastructure"
        if any(kw in combined for kw in ("pipeline", "workflow")):
            return "Pipeline"
        return "General"
