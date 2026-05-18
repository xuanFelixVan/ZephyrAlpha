---

task_id: "TASK-SYS-0029"
source_blueprint: "SYS-MASTER-001"
source_section: "§43 运维成熟度 + §46 1人运营保障 + §55 组合级风险管理与压力测试 + §56 波动率目标与动态杠杆"

title: "运维成熟度(MTTD<5min/MTTR<30min/告警疲劳防护/Runbook自文档化/SLO月度评审) + 1人运营保障(每日负荷上限/决策简约/Burnout预警/强制休息) + 组合风险管理(VaR+CVaR+Component VaR+5大压力场景+危机相关) + 波动率目标(Vol Target 15%/杠杆约束/Warm-up Ramp 4阶段)四合一落地"
description: |
  将 §43 运维成熟度 + §46 1人运营保障 + §55 组合风险管理 + §56 波动率目标四合一落地为单人全栈量化运维韧性框架。
  §43 定义：
  （1）MTTD < 5min（Telemetry）· MTTR < 30min（自修复 L1+L2）· Alert-to-action 延迟 < 1min（Owner在线）。
  （2）告警疲劳防护——单告警 < 5次/天，合并同类型、去重、分级（INFO→WARN→CRIT→EMERGE，Owner只看3个）。
  （3）Runbook 自文档化——每次事故 AI 自动生成 runbook· Owner离线>24h，AI自用runbook响应。
  （4）SLO 月度评审——每月1次SLO是否需要调整（§20 calm review）。
  §46 定义：
  （1）每日负荷上限——Session ≤ 4/天· AI产出评审 ≤ 12 commits/天· 施工+交易同天🛑禁止（分时段）· 重大部署后观察期 48h不部署。
  （2）决策简约化——每Session最多3个关键决策，剩下由AI自主做。
  （3）Burnout早期预警——连续2天Session完成率<50%→Burnout Warning→建议休息。
  （4）强制休息节奏——每日12h离线· 每周1天无码/无交易· 每月2天完全离线。
  §55 定义：
  （1）组合风险度量——VaR（95%/99%，Historical 500天）· CVaR（99%，E(loss|loss>VaR_99)）· Component VaR（每个位置 marginal VaR贡献）。
  （2）五大压力场景——GFC 2008（-50%全球急跌）· COVID Crash 2020-03（-35%/月+vol×5）· Flash Crash 2010-05-06（-10%/日内+恢复）· Rate Shock 2022（Fed加息-30% Bond）· Volmageddon 2018-02（VIX spike+-90% Inverse VIX）。
  （3）危机相关性管理——ρ_crisis = min(2×ρ_normal, 0.95)· 对策（提前减仓/分散化资产类型/动态风险映射≥周回顾）。
  §56 定义：
  （1）Vol Target 框架——σ_target = 15%年化· Leverage = σ_target/σ_realized(60天)· Max Leverage 2.0×· Min Leverage 0.0（全现金）。
  （2）杠杆约束——单一资产Max 25% AUM/Notional· Sector上限 40% AUM· Cash reserve ≥ 5% AUM。
  （3）Warm-up Ramp 4阶段——P1 0.25×（前30天学习）→ P2 0.50×（30-60天验证）→ P3 0.75×（60-90天信任建立）→ P4 1.00×（90+天完全信任）。
  本卡搭建 ops_maturity.py + one_person_ops.py + portfolio_risk.py + vol_target.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ops_maturity.py"
    description: "§43 MTTD<5min/MTTR<30min + 告警疲劳防护4级 + Runbook自动生成 + SLO月度评审"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\one_person_ops.py"
    description: "§46 每日负荷上限(Session≤4/commits≤12) + 决策简约(≤3/Session) + Burnout预警 + 强制休息节奏"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\portfolio_risk.py"
    description: "§55 VaR 95/99% Historical 500d + CVaR 99% + Component VaR + 5大压力场景 + 危机相关ρ_crisis"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\vol_target.py"
    description: "§56 Vol Target 15%年化 + Leverage=σ_target/σ_realized(60d) max2×min0 + 杠杆约束(25%/40%/5%) + Warm-up Ramp 4阶段"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ops_maturity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\one_person_ops.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\portfolio_risk.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\vol_target.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§43 MTTD/MTTR/告警/Runbook/SLO + §46 负荷/决策/Burnout/休息 + §55 VaR/CVaR/5场景/危机相关 + §56 Vol Target/Warm-up Ramp"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 80

acceptance_criteria:
  - "ops_maturity.py 实现 OpsMetrics——MTTD<5min（telemetry detect to alert）· MTTR<30min（L1 auto+L2 suggest）· alert_to_action<1min· 告警合并去重分级INFO/WARN/CRIT/EMERGE→daily_alert_count≤5· RunbookGenerator（每次事故→AI自动生成runbook.yaml）· SLOReview（每月自动SLO达标率+调整建议）"
  - "one_person_ops.py 实现 DailyLoadGuard——sessions_today（≤4）· commits_to_review（≤12）· trade+build同日（🛑block）· major_deploy_cooldown（48h内 follow-up部署禁止）· DecisionBudget（≤3关键决策/Session, marks D1/D2/D3/D4）· BurnoutDetector（连续2天completion<50%→WARNING→suggest_rest）· RestSchedule（每日12h/每周1天/每月2天离线check）"
  - "portfolio_risk.py 实现 RiskMetrics——VaR_95/VaR_99（Historical 500天）· CVaR_99（E(loss|loss>VaR_99)）· ComponentVaR（per position marginal contribution）→ daily_batch_compute"
  - "portfolio_risk.py 实现 StressTester——5场景（GFC-50%/COVID-35%+vol5×/FlashCrash-10%/RateShock-30%Bond/Volmageddon VIXspike-90%InverseVIX）· CrisisCorrelation（ρ_crisis=min(2×ρ_normal,0.95）→对策建议（减仓/分散化/≥周回顾）"
  - "vol_target.py 实现 VolTargetEngine——σ_realized_60d（EMA annualized）→ leverage=σ_target(15%) / σ_realized→ clamp(0, 2.0)· ConstraintCheck（单一资产≤25%AUM / Sector≤40%AUM / Cash≥5%AUM）· WarmupRamp（P1 0.25×(30d)→P2 0.50×(30-60d)→P3 0.75×(60-90d)→P4 1.00×(90+d)→auto progress on time）"

rollback_instructions: |
  1. 删除 ops_maturity.py / one_person_ops.py / portfolio_risk.py / vol_target.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0024"
blocked_by: []
status: "created"
tags_fn:
  - "trading"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
blueprint_id: DOM-GOV-001
---
