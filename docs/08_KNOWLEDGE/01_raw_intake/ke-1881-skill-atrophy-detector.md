---
module_id: KE-1790---002
status: active
title: 2.215 Skill Atrophy Detector - skill_atrophy_detector.py (🆕 v0.20.0 - 盲点265 — FL
category: module_blueprint
---

# 2.215 Skill Atrophy Detector - skill_atrophy_detector.py (🆕 v0.20.0 - 盲点265 — FL

2.215 Skill Atrophy Detector - skill_atrophy_detector.py (🆕 v0.20.0 - 盲点265 — FLE技能的自然退化检测与淘汰)

**致命问题**：FLE通过16代累积了250+个"技能"（诊断模式、修复策略、异常分类器）。但FLE的运营环境在变化——某些异常模式可能再也不会出现了（因为底层代码已被改写）、某些REPAIR策略已过时。这些atrophied skills占据KB空间、消耗检测资源、产生噪音。FLE需要像生物体一样，有"用进废退"的技能生命周期管理。
**对标**：Google Catastrophic Forgetting Research (EWC) + Anki Spaced Repetition Algorithm + LangChain Skill Deprecation

```python
@dataclass
class SkillHealth:
    skill_id: str       # "anomaly_signature_0x3FA" 或 "repair_pattern_CFG_RELOAD"
    skill_type: str     # "DETECTION"|"DIAGNOSIS"|"REPAIR"|"VERIFICATION"
    last_activated: datetime  # 最近一次被触发
    activation_count_30d: int
    activation_count_90d: int
    accuracy_30d: float  # 触发后正确的比例
    atrophy_score: float  # 0=常用, 1=已死亡
    status: str  # "ACTIVE"|"ATROPHYING"|"RETIRED"

class SkillAtrophyDetector:
    ATROPHY_WARNING_DAYS: int = 45   # 45天未激活→警告
    ATROPHY_RETIRE_DAYS: int = 120    # 120天未激活→退休
    ACCURACY_RETIRE_THRESHOLD: float = 0.3  # accuracy<30%→强制退休

    async def audit_skill_health(self) -> SkillHealthReport:
        now = datetime.now()
        skills = await self._load_all_skills()
        report = SkillHealthReport()
        for skill in skills:
            days_since_activation = (now - skill.last_activated).days
            if skill.accuracy_30d < self.ACCURACY_RETIRE_THRESHOLD and skill.activation_count_30d >= 3:
                await self._retire_skill(skill, reason=f"accuracy={skill.accuracy_30d:.0%}<30%")
                report.retired_accuracy.append(skill)
            elif days_since_activation > self.ATROPHY_RETIRE_DAYS:
                await self._retire_skill(skill, reason=f"dormant={days_since_activation}d>120d")
                report.retired_dormant.append(skill)
            elif days_since_activation > self.ATROPHY_WARNING_DAYS:
                skill.atrophy_score = min(1.0, (days_since_activation - self.ATROPHY_WARNING_DAYS)
                                          / (self.ATROPHY_RETIRE_DAYS - self.ATROPHY_WARNING_DAYS))
                report.atrophying.append(skill)
        if len(report.atrophying) > 10 or len(report.retired_dormant) > 3:
            self.FLE.notify_owner("SKILL_ATROPHY_REPORT",
                f"{len(report.atrophying)} skills atrophying, "
                f"{len(report.retired_dormant)} retired (dormant), "
                f"{len(report.retired_accuracy)} retired (inaccurate). "
                f"KB size reduced by {len(report.retired_dormant)+len(report.retired_accuracy)} skills. "
                f"Recommend: review retired skills—if environment changes, some may need re-activation.")
        return report
```
