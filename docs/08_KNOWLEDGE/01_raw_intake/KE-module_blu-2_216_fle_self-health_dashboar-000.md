---
module_id: KE-module_blu-2_216_fle_self-health_dashboar-000
title: 2.216 FLE Self-Health Dashboard - fle_health_dashboard.py (🆕 v0.20.0 - 盲点266 — O
category: module_blueprint
---

# 2.216 FLE Self-Health Dashboard - fle_health_dashboard.py (🆕 v0.20.0 - 盲点266 — O

2.216 FLE Self-Health Dashboard - fle_health_dashboard.py (🆕 v0.20.0 - 盲点266 — Owner对FLE元健康的一屏感知)

**致命问题**：FLE现在有260+风险、37+安全门、228+文件——但Owner如何在一秒钟内知道"FLE今天健康吗"？没有单一的health composite。Owner必须在僵尸评分、MTTI、信任度、Context Rot、降级等级、配置复杂度、技能萎缩率等十几个指标之间横跳，无法快速做triage。这违反了1人维护场景下的认知效率第一原则。
**对标**：Datadog Service Health Score + Dynatrace Davis Health Score + Google SRE Service Health Dashboard

```python
@dataclass
class FLEHealthComposite:
    overall_health: float          # 0-100, 加权复合分
    health_tier: str               # "GREEN"|"YELLOW"|"ORANGE"|"RED"|"PURPLE"
    component_scores: dict[str, float]  # 各子维度的分数
    top_3_risks: list[str]         # 当前最大的3个风险
    trend_arrow: str               # "↑" improving, "→" stable, "↓" deteriorating
    owner_recommended_action: str  # "NO_ACTION"|"REVIEW"|"INTERVENE"|"ESCALATE"

class FLEHealthDashboard:
    COMPONENT_WEIGHTS: dict[str, float] = {
        "trust_decay": 0.20,
        "zombie_score": 0.15,
        "context_rot": 0.10,
        "graceful_degradation": 0.15,
        "mtti": 0.10,
        "config_complexity": 0.08,
        "skill_atrophy": 0.07,
        "regulatory_compliance": 0.10,
        "repair_effectiveness": 0.05,
    }

    async def generate_health_snapshot(self) -> FLEHealthComposite:
        scores = {}
        scores["trust_decay"] = self.trust_decay_monitor.trust * 100
        scores["zombie_score"] = (1 - self.zombie_fle_detector.detect_zombie().zombie_score) * 100
        scores["context_rot"] = (1 - self.context_rot_monitor.detect_rot().rot_score) * 100
        scores["graceful_degradation"] = self._degradation_to_score(
            self.graceful_degradation_manager.current_level)
        scores["mtti"] = self._mtti_to_score(
            self.mtti_tracker.compute_mtti().get("mtti_sec", 0))
        scores["config_complexity"] = (1 - self.config_complexity_budget.audit().items_ratio) * 100
        scores["skill_atrophy"] = (1 - self._get_skill_atrophy_rate()) * 100
        scores["regulatory_compliance"] = self._compute_regulatory_compliance_score()
        scores["repair_effectiveness"] = self._get_repair_effectiveness_rate() * 100
        overall = sum(scores[k] * self.COMPONENT_WEIGHTS[k] for k in scores)
        # Tier
        tier = ("GREEN" if overall >= 85 else "YELLOW" if overall >= 70
                else "ORANGE" if overall >= 50 else "RED" if overall >= 25 else "PURPLE")
        action = ("NO_ACTION" if tier in ("GREEN", "YELLOW")
                  else "REVIEW" if tier == "ORANGE"
                  else "INTERVENE" if tier == "RED" else "ESCALATE")
        # 健康度发生重大变化→主动推送
        prev = await self._load_previous_snapshot()
        delta = overall - (prev.overall_health if prev else overall)
        if delta < -15:  # 骤降15分+
            self.FLE.notify_owner("FLE_HEALTH_DECLINED",
                f"FLE health dropped {abs(delta):.0f} points to {overall:.0f}/100 ({tier}). "
                f"Top risks: {'; '.join(self._top_risks(scores, 3))}. "
                f"Recommended: {act
