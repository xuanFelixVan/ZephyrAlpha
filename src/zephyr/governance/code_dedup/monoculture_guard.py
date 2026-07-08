# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.monoculture_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/code_quality/test_code_dedup_engine.py; tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/governance/security/test_monoculture_guard.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_monoculture_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Monoculture 免疫 — BRS 0-100 + 去重悖论检测.

职责：
  - BRS (Blast Radius Score) = min(100, caller_score + cross_layer_score + critical_path_score + test_gap_score)
  - 4级判定：SAFE(0-25) / CAUTION(26-50) / RISKY(51-75) / DANGEROUS(76-100)
  - BRS≥76 -> 停止去重 + 生成"不建议修复"报告
  - --force-monoculture CLI 覆盖逻辑
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml


@dataclass
class BlastRadiusScore:
    caller_count: int = 0
    cross_layer_count: int = 0
    on_critical_path: bool = False
    has_independent_unit_test: bool = False
    blast_radius_score: int = 0
    level: str = "SAFE"
    recommendation: str = ""
    mitigating_action: str = ""


class MonocultureGuard:
    """BRS 计算 + 去重悖论检测."""

    _MAX_THRESHOLD: int = 20
    _MAX_CROSS_LAYER: int = 5

    def compute_brs(
        self,
        caller_count: int = 0,
        cross_layer_count: int = 0,
        on_critical_path: bool = False,
        has_independent_unit_test: bool = False,
    ) -> BlastRadiusScore:
        """BRS = min(100, caller*40/threshold + cross*30/max_cross + critical*20 + test_gap*10)."""
        caller_score = min(caller_count / self._MAX_THRESHOLD, 1.0) * 40
        cross_layer_score = min(cross_layer_count / self._MAX_CROSS_LAYER, 1.0) * 30
        critical_score = 20 if on_critical_path else 0
        test_gap_score = 10 if not has_independent_unit_test else 0

        total = min(100, int(round(caller_score + cross_layer_score + critical_score + test_gap_score)))
        level, rec, action = self._classify(total, caller_count, on_critical_path)

        return BlastRadiusScore(
            caller_count=caller_count,
            cross_layer_count=cross_layer_count,
            on_critical_path=on_critical_path,
            has_independent_unit_test=has_independent_unit_test,
            blast_radius_score=total,
            level=level,
            recommendation=rec,
            mitigating_action=action,
        )

    def should_block_dedup(self, brs: BlastRadiusScore) -> bool:
        """BRS≥76 -> 停止去重."""
        return brs.level == "DANGEROUS"

    def generate_report(self, func_name: str, brs: BlastRadiusScore) -> str:
        """生成"为什么不修复"报告."""
        if brs.level != "DANGEROUS":
            return ""

        return (
            f"Monoculture 免疫：不修复 {func_name}\n"
            f"   BRS = {brs.blast_radius_score}/100 ({brs.level})\n"
            f"   调用方: {brs.caller_count} | 跨层: {brs.cross_layer_count}\n"
            f"   关键路径: {'是' if brs.on_critical_path else '否'} | 独立测试: {'有' if brs.has_independent_unit_test else '无'}\n"
            f"   建议: {brs.recommendation}\n"
            f"   缓解措施: {brs.mitigating_action}\n"
            f"   Owner 可用 --force-monoculture 覆盖此决策"
        )

    def save_risk_report(
        self,
        entries: list[tuple[str, BlastRadiusScore]],
        output_path: str | Path | None = None,
    ) -> None:
        """保存 monoculture-risk.yaml."""
        if output_path is None:
            output_path = Path("data/cache/monoculture-risk.yaml")
        path = Path(output_path)

        risks = []
        for func_name, brs in entries:
            risks.append(
                {
                    "function": func_name,
                    "blast_radius_score": brs.blast_radius_score,
                    "level": brs.level,
                    "caller_count": brs.caller_count,
                    "cross_layer_count": brs.cross_layer_count,
                    "on_critical_path": brs.on_critical_path,
                    "has_independent_unit_test": brs.has_independent_unit_test,
                    "recommendation": brs.recommendation,
                    "mitigating_action": brs.mitigating_action,
                }
            )

        data = {
            "version": "1.0.0",
            "generated_at": datetime.now(UTC).isoformat(),
            "risks": risks,
        }

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.dump(data, allow_unicode=True, default_flow_style=False),
            encoding="utf-8",
        )

    @staticmethod
    def _classify(total: int, callers: int, critical: bool) -> tuple[str, str, str]:
        if total <= 25:
            return "SAFE", "正常去重——BRS在安全范围内", "无"
        if total <= 50:
            return "CAUTION", "去重但标记blast_radius:CAUTION——强烈建议补充独立测试", "补充@pytest.mark.parametrize测试"
        if total <= 75:
            return "RISKY", "去重但Session Log高亮+建议故障注入测试", "生成TaskCard BRS-AUDIT——故障注入测试"
        action = "强烈建议补充独立测试" if callers > 10 else "Owner确认后--force-monoculture覆盖"
        return (
            "DANGEROUS",
            "停止去重——BRS≥76爆炸半径不可接受。分散重复=天然blast radius隔离",
            action,
        )
