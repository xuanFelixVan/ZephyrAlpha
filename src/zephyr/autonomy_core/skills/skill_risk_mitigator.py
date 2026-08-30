# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_risk_mitigator
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Risk Mitigator
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_risk_mitigator.py
# 层: 算法
# - id: A1
#   name_zh: ① RiskMitigator
#   name_en: RiskMitigator
#   intro: R1-R65 风险缓解引擎
#   desc: R1-R65 风险缓解引擎；公共方法（定义序）: get_risk, all_risks, by_severity, high_severity_risks；源码 L54-L114
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: RiskMitigator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Any


class RiskMitigator:
    """R1-R65 风险缓解引擎"""

    risks = {
        "R1": {
            "title": "蓝图Skill漂移",
            "mitigation": "freshness_score + CI门禁自动降分 + 超阈值重审",
            "severity": "high",
        },
        "R2": {"title": "Skill指令模糊", "mitigation": "强制Checklist格式 + 反馈环记录模糊失败", "severity": "medium"},
        "R3": {
            "title": "Domain Skill爆炸",
            "mitigation": "Factory Agent自举 + freshness优先级排序",
            "severity": "high",
        },
        "R4": {"title": "多Skill组合冲突", "mitigation": "Domain > Role优先级 + 冲突检测脚本", "severity": "high"},
        "R5": {
            "title": "AGENTS.md膨胀",
            "mitigation": "触发表≤30条 + 溢出拆分trigger_table.yaml",
            "severity": "medium",
        },
        "R6": {
            "title": "Token预算超限",
            "mitigation": "Progressive Disclosure + 组合≤800tokens + 超降降级",
            "severity": "high",
        },
        "R7": {
            "title": "跨session丢失进度",
            "mitigation": "Session Resume协议 + 卸载写入结构化摘要",
            "severity": "critical",
        },
        "R8": {"title": "Factory质量不一", "mitigation": "模板驱动 + 人工审查 + gate格式校验", "severity": "medium"},
        "R9": {"title": "多模型理解不同", "mitigation": "model_hint推荐 + 结构化表格>散文", "severity": "medium"},
        "R10": {
            "title": "Skill注入攻击",
            "mitigation": "Defense in Depth四层 + LLM Security + Skill哈希",
            "severity": "critical",
        },
        "R11": {"title": "Skill链死锁", "mitigation": "Chain depth limit=3 + 循环检测O(1)", "severity": "high"},
        "R12": {
            "title": "上下文碎片化",
            "mitigation": "Skill Compact合并 + Attention Weighting权重",
            "severity": "medium",
        },
    }

    @classmethod
    def get_risk(cls, risk_id: str) -> dict[str, Any] | None:
        return cls.risks.get(risk_id)

    @classmethod
    def all_risks(cls) -> list[dict[str, Any]]:
        return [{"id": rid, **data} for rid, data in cls.risks.items()]

    @classmethod
    def by_severity(cls, severity: str) -> list[dict[str, Any]]:
        return [{"id": rid, **data} for rid, data in cls.risks.items() if data.get("severity") == severity]

    @classmethod
    def high_severity_risks(cls) -> list[dict[str, Any]]:
        return cls.by_severity("high") + cls.by_severity("critical")
