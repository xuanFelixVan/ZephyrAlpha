# [BLUEPRINT] SRC-055 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.governance.ops_governance.agent_dispatch
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_agent_dispatch | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from typing import Final

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DomainDispatch:
    domain: str
    pre_read: str
    re_read: str
    token_budget: int
    blueprint_section: str = ""


DISPATCH_TABLE: Final[dict[str, DomainDispatch]] = {
    "gate-breaker": DomainDispatch(
        domain="门禁/断路器",
        pre_read="SYS-MASTER-001 §2",
        re_read="MOD-GATE_ENGINE blueprint",
        token_budget=600,
        blueprint_section="§2",
    ),
    "context-injection": DomainDispatch(
        domain="上下文注入",
        pre_read="SYS-MASTER-001 §2",
        re_read="MOD-CONTEXT_ENGINE blueprint",
        token_budget=500,
        blueprint_section="§2",
    ),
    "task-pipeline": DomainDispatch(
        domain="任务管线",
        pre_read="SYS-MASTER-001 §2",
        re_read="MOD-INF-009 blueprint",
        token_budget=500,
        blueprint_section="§2",
    ),
    "feedback-loop": DomainDispatch(
        domain="反馈闭环",
        pre_read="SYS-MASTER-001 §2",
        re_read="MOD-FEEDBACK_LOOP blueprint",
        token_budget=500,
        blueprint_section="§2",
    ),
    "cross-system-integration": DomainDispatch(
        domain="跨系统集成",
        pre_read="SYS-MASTER-001 §1-§3",
        re_read="MOD-MASTER_BLUEPRINT CT-*",
        token_budget=2000,
        blueprint_section="§1-§3",
    ),
    "new-module": DomainDispatch(
        domain="新建模块",
        pre_read="PS-STD-005 §5",
        re_read="blueprint-template.md",
        token_budget=800,
        blueprint_section="§5",
    ),
    "architecture-review": DomainDispatch(
        domain="架构审查",
        pre_read="SYS-MASTER-001 全文",
        re_read="PS-STD-005 + blueprint_registry.yaml",
        token_budget=4000,
        blueprint_section="全文",
    ),
    "cost-management": DomainDispatch(
        domain="成本管理/预算",
        pre_read="SYS-MASTER-001 §十二",
        re_read="MOD-INF-024 + §12.3",
        token_budget=800,
        blueprint_section="§十二",
    ),
    "data-classification": DomainDispatch(
        domain="数据分级/安全",
        pre_read="SYS-MASTER-001 §十三",
        re_read="MOD-LLM_SECURITY + §13.3",
        token_budget=600,
        blueprint_section="§十三",
    ),
    "startup-ops": DomainDispatch(
        domain="启动/运维",
        pre_read="SYS-MASTER-001 §十四",
        re_read="SH-DB-001 + §14.1",
        token_budget=500,
        blueprint_section="§十四",
    ),
    "construction-methodology": DomainDispatch(
        domain="施工方法论",
        pre_read="SYS-MASTER-001 §十五",
        re_read="§15.1 + §15.2",
        token_budget=400,
        blueprint_section="§十五",
    ),
    "testing-quality": DomainDispatch(
        domain="测试/质量保障",
        pre_read="SYS-MASTER-001 §十七",
        re_read="MOD-INF-005 + §17.1",
        token_budget=800,
        blueprint_section="§十七",
    ),
    "disaster-recovery": DomainDispatch(
        domain="灾难恢复",
        pre_read="SYS-MASTER-001 §十八",
        re_read="MOD-INF-001 + §18.3",
        token_budget=600,
        blueprint_section="§十八",
    ),
    "model-risk": DomainDispatch(
        domain="模型风险管理",
        pre_read="SYS-MASTER-001 §十九",
        re_read="MOD-FEEDBACK_LOOP + SR11-7",
        token_budget=700,
        blueprint_section="§十九",
    ),
    "incident-response": DomainDispatch(
        domain="事故响应",
        pre_read="SYS-MASTER-001 §二十",
        re_read="MOD-INF-022 + §20.3",
        token_budget=600,
        blueprint_section="§二十",
    ),
    "deployment-release": DomainDispatch(
        domain="部署/发布",
        pre_read="SYS-MASTER-001 §二十一",
        re_read="MOD-INF-009 + §21.1",
        token_budget=500,
        blueprint_section="§二十一",
    ),
    "compliance-review": DomainDispatch(
        domain="合规审查",
        pre_read="SYS-MASTER-001 §二十二",
        re_read="MOD-INF-020 + §22.2",
        token_budget=700,
        blueprint_section="§二十二",
    ),
    "security-defense": DomainDispatch(
        domain="安全纵深防御",
        pre_read="SYS-MASTER-001 §二十三",
        re_read="MOD-LLM_SECURITY + §23.1",
        token_budget=600,
        blueprint_section="§二十三",
    ),
    "session-lifecycle": DomainDispatch(
        domain="Session生命周期",
        pre_read="SYS-MASTER-001 §二十四",
        re_read="session_handover.yaml",
        token_budget=400,
        blueprint_section="§二十四",
    ),
    "environment-management": DomainDispatch(
        domain="环境管理",
        pre_read="SYS-MASTER-001 §二十五",
        re_read="IDE隔离 + 快捷键",
        token_budget=300,
        blueprint_section="§二十五",
    ),
    "observability-dashboard": DomainDispatch(
        domain="可观测性/仪表板",
        pre_read="SYS-MASTER-001 §二十六",
        re_read="MOD-INF-015 + §0.0",
        token_budget=400,
        blueprint_section="§二十六",
    ),
    "performance-baseline": DomainDispatch(
        domain="性能基线",
        pre_read="SYS-MASTER-001 §二十七",
        re_read="MOD-INF-011 + §27.1",
        token_budget=400,
        blueprint_section="§二十七",
    ),
    "supply-chain": DomainDispatch(
        domain="供应链安全",
        pre_read="SYS-MASTER-001 §二十八",
        re_read="pip-lock + audit",
        token_budget=300,
        blueprint_section="§二十八",
    ),
    "data-quality": DomainDispatch(
        domain="数据质量治理",
        pre_read="SYS-MASTER-001 §二十九",
        re_read="SH-DB-001 + §13",
        token_budget=400,
        blueprint_section="§二十九",
    ),
    "knowledge-management": DomainDispatch(
        domain="知识管理",
        pre_read="SYS-MASTER-001 §三十",
        re_read="MOD-KB-001 + AUTO-KB(§67)",
        token_budget=400,
        blueprint_section="§三十",
    ),
    "migration-strategy": DomainDispatch(
        domain="迁移策略",
        pre_read="SYS-MASTER-001 §三十一",
        re_read="MOD-INF-021 + §21",
        token_budget=300,
        blueprint_section="§三十一",
    ),
    "glossary-antipatterns": DomainDispatch(
        domain="术语/反模式",
        pre_read="SYS-MASTER-001 §三十二 + §三十三",
        re_read="§15.2 + AGENTS.md",
        token_budget=300,
        blueprint_section="§三十二-§三十三",
    ),
    "owner-offline": DomainDispatch(
        domain="Owner离线自治",
        pre_read="SYS-MASTER-001 §三十四",
        re_read="§七十 分级决策",
        token_budget=400,
        blueprint_section="§三十四",
    ),
    "third-party-deps": DomainDispatch(
        domain="第三方依赖",
        pre_read="SYS-MASTER-001 §三十五",
        re_read="MOD-INF-024 + §28",
        token_budget=300,
        blueprint_section="§三十五",
    ),
    "human-ai-bandwidth": DomainDispatch(
        domain="人机带宽",
        pre_read="SYS-MASTER-001 §三十六",
        re_read="§十五 + §62 交易HCI",
        token_budget=400,
        blueprint_section="§三十六",
    ),
    "model-drift": DomainDispatch(
        domain="模型漂移监控",
        pre_read="SYS-MASTER-001 §三十七",
        re_read="§六十 SPC + §42 ML",
        token_budget=400,
        blueprint_section="§三十七",
    ),
    "spof-elimination": DomainDispatch(
        domain="SPOF消除",
        pre_read="SYS-MASTER-001 §三十八",
        re_read="§1.3 + §45.1",
        token_budget=300,
        blueprint_section="§三十八",
    ),
    "vibe-quality": DomainDispatch(
        domain="氛围编程质量",
        pre_read="SYS-MASTER-001 §三十九",
        re_read="§六十 SPC + §15",
        token_budget=400,
        blueprint_section="§三十九",
    ),
    "market-data-pipeline": DomainDispatch(
        domain="市场数据管线",
        pre_read="SYS-MASTER-001 §四十",
        re_read="SH-DB-001 + §29",
        token_budget=600,
        blueprint_section="§四十",
    ),
    "backtest-engine": DomainDispatch(
        domain="回测引擎",
        pre_read="SYS-MASTER-001 §四十",
        re_read="MOD-FEEDBACK_LOOP + §19",
        token_budget=700,
        blueprint_section="§四十",
    ),
    "order-execution": DomainDispatch(
        domain="订单执行/风控",
        pre_read="SYS-MASTER-001 §四十一",
        re_read="MOD-INF-005 + §19",
        token_budget=600,
        blueprint_section="§四十一",
    ),
    "quant-ml": DomainDispatch(
        domain="量化ML工程",
        pre_read="SYS-MASTER-001 §四十二",
        re_read="MOD-INF-011 + §27",
        token_budget=700,
        blueprint_section="§四十二",
    ),
    "ops-maturity": DomainDispatch(
        domain="运维成熟度",
        pre_read="SYS-MASTER-001 §四十三",
        re_read="MOD-INF-001 + §0.0",
        token_budget=500,
        blueprint_section="§四十三",
    ),
    "vibe-coding-deep": DomainDispatch(
        domain="氛围编程深层",
        pre_read="SYS-MASTER-001 §四十四",
        re_read="§15.5 + MOD-INF-019",
        token_budget=600,
        blueprint_section="§四十四",
    ),
    "architecture-contracts": DomainDispatch(
        domain="架构基础契约",
        pre_read="SYS-MASTER-001 §四十五",
        re_read="MOD-MASTER_BLUEPRINT + §4.1",
        token_budget=600,
        blueprint_section="§四十五",
    ),
    "one-person-ops": DomainDispatch(
        domain="1人运营保障",
        pre_read="SYS-MASTER-001 §四十六",
        re_read="§三十六 + §三十四",
        token_budget=400,
        blueprint_section="§四十六",
    ),
    "legal-compliance": DomainDispatch(
        domain="金融合规法律",
        pre_read="SYS-MASTER-001 §四十七",
        re_read="§二十二 + §十九",
        token_budget=500,
        blueprint_section="§四十七",
    ),
    "strategy-validation": DomainDispatch(
        domain="策略验证/统计",
        pre_read="SYS-MASTER-001 §四十八",
        re_read="§四十二 + §十九",
        token_budget=600,
        blueprint_section="§四十八",
    ),
    "execution-algorithms": DomainDispatch(
        domain="执行算法/微结构",
        pre_read="SYS-MASTER-001 §四十九",
        re_read="§四十一 + §四十",
        token_budget=500,
        blueprint_section="§四十九",
    ),
    "multi-strategy": DomainDispatch(
        domain="多策略/容量管理",
        pre_read="SYS-MASTER-001 §五十",
        re_read="§四十八 + §十九",
        token_budget=500,
        blueprint_section="§五十",
    ),
    "broker-resilience": DomainDispatch(
        domain="经纪商容灾",
        pre_read="SYS-MASTER-001 §五十一",
        re_read="§三十五 + §十八",
        token_budget=400,
        blueprint_section="§五十一",
    ),
    "reproducibility": DomainDispatch(
        domain="可重现性保障",
        pre_read="SYS-MASTER-001 §五十二",
        re_read="§二十八 + §四十五",
        token_budget=400,
        blueprint_section="§五十二",
    ),
    "post-deploy-validation": DomainDispatch(
        domain="实盘后验证",
        pre_read="SYS-MASTER-001 §五十三",
        re_read="§二十一 + §三十九",
        token_budget=400,
        blueprint_section="§五十三",
    ),
    "ai-code-review": DomainDispatch(
        domain="AI代码审查深度",
        pre_read="SYS-MASTER-001 §五十四",
        re_read="§十五 + §四十四",
        token_budget=500,
        blueprint_section="§五十四",
    ),
    "portfolio-risk": DomainDispatch(
        domain="组合级风险管理",
        pre_read="SYS-MASTER-001 §五十五",
        re_read="§五十 + §十九",
        token_budget=500,
        blueprint_section="§五十五",
    ),
    "vol-target": DomainDispatch(
        domain="波动率目标/杠杆",
        pre_read="SYS-MASTER-001 §五十六",
        re_read="§五十 + §四十一",
        token_budget=400,
        blueprint_section="§五十六",
    ),
    "factor-timing": DomainDispatch(
        domain="因子择时/跨资产",
        pre_read="SYS-MASTER-001 §五十七",
        re_read="§四十二 + §四十八",
        token_budget=400,
        blueprint_section="§五十七",
    ),
    "trading-calendar": DomainDispatch(
        domain="交易日历/合约",
        pre_read="SYS-MASTER-001 §五十八",
        re_read="§四十 + §五十一",
        token_budget=300,
        blueprint_section="§五十八",
    ),
    "ops-basics": DomainDispatch(
        domain="运维基础保障",
        pre_read="SYS-MASTER-001 §五十九",
        re_read="§十八 + §四十三",
        token_budget=400,
        blueprint_section="§五十九",
    ),
    "ai-quality-spc": DomainDispatch(
        domain="AI质量SPC",
        pre_read="SYS-MASTER-001 §六十",
        re_read="§三十九 + §三十七",
        token_budget=400,
        blueprint_section="§六十",
    ),
    "pnl-attribution": DomainDispatch(
        domain="PnL归因/TCA",
        pre_read="SYS-MASTER-001 §六十一",
        re_read="§五十 + D_REPORTING",
        token_budget=500,
        blueprint_section="§六十一",
    ),
    "daily-operations": DomainDispatch(
        domain="日运营节奏/交易HCI",
        pre_read="SYS-MASTER-001 §六十二",
        re_read="§五十八 + §三十四",
        token_budget=500,
        blueprint_section="§六十二",
    ),
    "fault-tolerance": DomainDispatch(
        domain="系统容错模式",
        pre_read="SYS-MASTER-001 §六十三",
        re_read="§四十五 + §二十一",
        token_budget=400,
        blueprint_section="§六十三",
    ),
    "microstructure-defense": DomainDispatch(
        domain="微结构防御/模拟保真度",
        pre_read="SYS-MASTER-001 §六十四",
        re_read="§四十九 + §四十一",
        token_budget=400,
        blueprint_section="§六十四",
    ),
    "factor-governance": DomainDispatch(
        domain="因子治理/生命周期",
        pre_read="SYS-MASTER-001 §六十五",
        re_read="§四十八 + §五十",
        token_budget=400,
        blueprint_section="§六十五",
    ),
    "feature-flags": DomainDispatch(
        domain="功能开关/部署安全网",
        pre_read="SYS-MASTER-001 §六十六",
        re_read="§二十一 + §五十三",
        token_budget=400,
        blueprint_section="§六十六",
    ),
    "ai-self-diagnosis": DomainDispatch(
        domain="AI自诊断/知识自动化",
        pre_read="SYS-MASTER-001 §六十七",
        re_read="§六十 + §三十",
        token_budget=400,
        blueprint_section="§六十七",
    ),
    "vibe-determinism": DomainDispatch(
        domain="氛围编程确定性保障",
        pre_read="SYS-MASTER-001 §六十八",
        re_read="§五十二 + §四十四",
        token_budget=400,
        blueprint_section="§六十八",
    ),
    "secrets-lifecycle": DomainDispatch(
        domain="Secrets生命周期/环境可重建",
        pre_read="SYS-MASTER-001 §六十九",
        re_read="§十三 + §十八",
        token_budget=400,
        blueprint_section="§六十九",
    ),
    "offline-budget": DomainDispatch(
        domain="离线分级应急/全生命周期预算",
        pre_read="SYS-MASTER-001 §七十",
        re_read="§三十四 + §四十八",
        token_budget=400,
        blueprint_section="§七十",
    ),
    "prompt-lifecycle": DomainDispatch(
        domain="Prompt工程/生命周期",
        pre_read="SYS-MASTER-001 §七十一",
        re_read="§十五 + §四十四 + .zeph/prompts/",
        token_budget=400,
        blueprint_section="§七十一",
    ),
    "context-hallucination": DomainDispatch(
        domain="上下文窗口/幻觉防御",
        pre_read="SYS-MASTER-001 §七十二",
        re_read="§十二 + §六十七",
        token_budget=400,
        blueprint_section="§七十二",
    ),
    "multi-model-consensus": DomainDispatch(
        domain="多模型共识/辩论协议",
        pre_read="SYS-MASTER-001 §七十三",
        re_read="§四十四 + §五十四",
        token_budget=400,
        blueprint_section="§七十三",
    ),
    "code-generation": DomainDispatch(
        domain="代码生成标准/脚手架",
        pre_read="SYS-MASTER-001 §七十四",
        re_read="§十五 + §三十三",
        token_budget=300,
        blueprint_section="§七十四",
    ),
    "kill-switch": DomainDispatch(
        domain="Kill Switch/安全保障",
        pre_read="SYS-MASTER-001 §七十五",
        re_read="§二十 + §六十六 + §四十一",
        token_budget=500,
        blueprint_section="§七十五",
    ),
    "paper-to-live": DomainDispatch(
        domain="模拟→实盘过渡",
        pre_read="SYS-MASTER-001 §七十六",
        re_read="§五十三 + §六十四 + §五十六",
        token_budget=400,
        blueprint_section="§七十六",
    ),
    "order-quality": DomainDispatch(
        domain="订单执行质量/异常检测",
        pre_read="SYS-MASTER-001 §七十七",
        re_read="§四十一 + §六十一 + §六十四",
        token_budget=400,
        blueprint_section="§七十七",
    ),
    "knowledge-continuity": DomainDispatch(
        domain="知识连续性/断供因子",
        pre_read="SYS-MASTER-001 §七十八",
        re_read="§三十 + §六十七 + §四十六",
        token_budget=400,
        blueprint_section="§七十八",
    ),
    "local-first": DomainDispatch(
        domain="本地优先/离线运行",
        pre_read="SYS-MASTER-001 §七十九",
        re_read="§二十五 + §三十四 + §七十",
        token_budget=300,
        blueprint_section="§七十九",
    ),
    "decision-fatigue": DomainDispatch(
        domain="决策疲劳/优先级分流",
        pre_read="SYS-MASTER-001 §八十",
        re_read="§三十六 + §四十六 + §六十二",
        token_budget=400,
        blueprint_section="§八十",
    ),
    "what-if-simulation": DomainDispatch(
        domain="What-If仿真/灵敏度",
        pre_read="SYS-MASTER-001 §八十一",
        re_read="§四十 + §五十五 + §四十二",
        token_budget=400,
        blueprint_section="§八十一",
    ),
    "code-archeology": DomainDispatch(
        domain="代码考古/文档自动化",
        pre_read="SYS-MASTER-001 §八十二",
        re_read="§三十 + §五十二 + §三十一",
        token_budget=300,
        blueprint_section="§八十二",
    ),
    "data-source-reliability": DomainDispatch(
        domain="数据源可靠性/智能切换",
        pre_read="SYS-MASTER-001 §八十三",
        re_read="§二十九 + §三十五 + §四十",
        token_budget=400,
        blueprint_section="§八十三",
    ),
    "chaos-engineering": DomainDispatch(
        domain="混沌工程/故障演练",
        pre_read="SYS-MASTER-001 §八十四",
        re_read="§十八 + §六十三 + §十六",
        token_budget=400,
        blueprint_section="§八十四",
    ),
    "macro-regime": DomainDispatch(
        domain="经济体制/宏观覆盖",
        pre_read="SYS-MASTER-001 §八十五",
        re_read="§四十二 + §五十七 + §五十五",
        token_budget=400,
        blueprint_section="§八十五",
    ),
    "ai-explainability": DomainDispatch(
        domain="AI可解释性/监管审计",
        pre_read="SYS-MASTER-001 §八十六",
        re_read="§四十七 + §二十二 + §十九",
        token_budget=400,
        blueprint_section="§八十六",
    ),
    "sbom-deps": DomainDispatch(
        domain="SBOM/依赖情报",
        pre_read="SYS-MASTER-001 §八十七",
        re_read="§二十八 + §三十五 + §六十九",
        token_budget=300,
        blueprint_section="§八十七",
    ),
    "state-machine": DomainDispatch(
        domain="状态机形式化/验证",
        pre_read="SYS-MASTER-001 §八十八",
        re_read="§四十一 + §四十五 + §六十六",
        token_budget=300,
        blueprint_section="§八十八",
    ),
    "dora-metrics": DomainDispatch(
        domain="DORA指标/开发速率",
        pre_read="SYS-MASTER-001 §八十九",
        re_read="§三十九 + §六十 + §四十四",
        token_budget=300,
        blueprint_section="§八十九",
    ),
    "ab-experiment": DomainDispatch(
        domain="A/B实验框架",
        pre_read="SYS-MASTER-001 §九十",
        re_read="§四十八 + 实验 + §五十三",
        token_budget=400,
        blueprint_section="§九十",
    ),
    "corporate-actions": DomainDispatch(
        domain="企业行为/参考数据",
        pre_read="SYS-MASTER-001 §九十一",
        re_read="§四十 + §六十五 + §四十二",
        token_budget=500,
        blueprint_section="§九十一",
    ),
    "hot-restart": DomainDispatch(
        domain="热重启/盘中恢复",
        pre_read="SYS-MASTER-001 §九十二",
        re_read="§十四 + §八十八 + §六十三",
        token_budget=500,
        blueprint_section="§九十二",
    ),
    "session-concurrency": DomainDispatch(
        domain="会话并发/文件完整性",
        pre_read="SYS-MASTER-001 §九十三",
        re_read="§二十五 + §二十四 + §六十八",
        token_budget=400,
        blueprint_section="§九十三",
    ),
    "hardware-resilience": DomainDispatch(
        domain="硬件容灾/基础设施",
        pre_read="SYS-MASTER-001 §九十四",
        re_read="§十六 + §六十三 + §七十",
        token_budget=400,
        blueprint_section="§九十四",
    ),
    "api-lifecycle": DomainDispatch(
        domain="API生命周期/弃用",
        pre_read="SYS-MASTER-001 §九十五",
        re_read="§四十五 + §八十七 + §三十五",
        token_budget=400,
        blueprint_section="§九十五",
    ),
    "data-lifecycle": DomainDispatch(
        domain="数据生命周期/清理",
        pre_read="SYS-MASTER-001 §九十六",
        re_read="§五十九 + §八十二 + §八十三",
        token_budget=300,
        blueprint_section="§九十六",
    ),
    "time-sync": DomainDispatch(
        domain="时间同步/时钟纪律",
        pre_read="SYS-MASTER-001 §九十七",
        re_read="§七十五 + §五十二 + §四十五",
        token_budget=300,
        blueprint_section="§九十七",
    ),
    "stream-data": DomainDispatch(
        domain="流式数据架构",
        pre_read="SYS-MASTER-001 §九十八",
        re_read="§四十 + §八十三 + §四十一",
        token_budget=400,
        blueprint_section="§九十八",
    ),
    "silent-failure": DomainDispatch(
        domain="静默故障聚合/级联风险",
        pre_read="SYS-MASTER-001 §九十九",
        re_read="§四十三 + §六十三 + §十六",
        token_budget=400,
        blueprint_section="§九十九",
    ),
    "incremental-review": DomainDispatch(
        domain="增量审查/部分接受",
        pre_read="SYS-MASTER-001 §一百",
        re_read="§三十九 + §八十 + §五十四",
        token_budget=400,
        blueprint_section="§一百",
    ),
    "benchmark-integrity": DomainDispatch(
        domain="基准完整性/生存偏差",
        pre_read="SYS-MASTER-001 §一百〇一",
        re_read="§四十八 + §九十一 + §四十二",
        token_budget=500,
        blueprint_section="§一百〇一",
    ),
    "cross-env-consistency": DomainDispatch(
        domain="跨环境一致性/Windows风险",
        pre_read="SYS-MASTER-001 §一百〇二",
        re_read="§二十五 + §六十九 + §五十二",
        token_budget=400,
        blueprint_section="§一百〇二",
    ),
}


def resolve_domain(domain_key: str) -> DomainDispatch | None:
    """根据 domain key 返回分派信息。找不到返回 None。"""
    entry = DISPATCH_TABLE.get(domain_key)
    if entry is None:
        logger.warning("Dispatch 未命中 domain_key=%s", domain_key)
    return entry


def list_all_domains() -> list[str]:
    """列出所有已注册的任务域 key。"""
    return sorted(DISPATCH_TABLE.keys())


def resolve_by_keyword(keyword: str) -> list[DomainDispatch]:
    """模糊匹配——关键词命中 domain 名或章节号的条目列表。"""
    kw = keyword.lower()
    results: list[DomainDispatch] = []
    for entry in DISPATCH_TABLE.values():
        if kw in entry.domain.lower() or kw in entry.blueprint_section.lower() or kw in entry.pre_read.lower():
            results.append(entry)
    return results


def get_dispatch_count() -> int:
    """返回已注册域数目。"""
    return len(DISPATCH_TABLE)
