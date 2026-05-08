---
task_id: "TASK-SYS-0036"
source_blueprint: "SYS-MASTER-001"
source_section: "§77 订单执行质量监控与异常检测 + §81 What-If仿真与灵敏度分析引擎 + §84 混沌工程与自动故障演练 + §86 AI决策可解释性与监管审计深度 + §90 A/B实验框架与统计严谨性"

title: "执行质量四维异常(成交率异常/价格恶化/延迟尖峰/拒绝率爆增)+经纪商评分五维(成交率/价格改善/延迟/拒绝率/费用效益×0.25/0.25/0.20/0.15/0.15)+结算监控 + What-If三引擎(参数灵敏度扫描±20%/MonteCarlo 10000路径Cholesky/VaR+CVaR+MaxDD分布+破产概率/反事实分析) + 混沌工程五类故障注入(网络/数据源/经纪商API/计算资源CPU+磁盘/数据损坏)+自动演练日历+失败升级 + AI决策解释链(步骤化)+模型卡+审计就绪四要求 + A/B实验模板(定义/假设/归因/记录)+显著性检验(ε-threshold)+结果自动记录 五合一实验与韧性框架"
description: |
  将 §77 执行质量 + §81 What-If + §84 混沌工程 + §86 可解释性 + §90 A/B实验五合一落地为实验验证与韧性保障框架。
  §77 定义：
  （1）四维异常检测——成交率异常（正常≥90%/日 突然<80%→即时告警）· 价格恶化（slippage vs arrival price>预期>3σσ→推断价格影响EL量）· 延迟尖峰（订单往返>200ms→>500ms异常→降级策略）· 拒绝率爆增（reg|rej>5%/天→审查+临时降级经纪人）。
  （2）经纪商质量评分——5维 Weighted（成交率 0.25 + 价格改善 0.25 + 延迟 0.20 + 拒绝率 0.15 + 费用效益 0.15）→ 每日 broker_quality.csv →滚动3月 healthy min 0.70。
  （3）结算监控——经纪商报告vs 内部日志>偏差→ ①T+1匹配 ②持仓验证 ∀broker→异常→强制 6s 结算会议。
  §81 定义：
  （1）三引擎——Parameter Sweep（关键参数 ±20% 每次 5×5 额/N→ 响应面结果）· MonteCarlo（10000路径+Cholesky分解 →生成 VaR/CVaR/MaxDD 分布+破产概率 Prob(Equity<0)）· CounterFactual（"如果处理/去[因子3×]"或用量/P历史分100@env→时延 42条+mini J）。
  §84 定义：
  （1）五类故障注入——网络故障（延迟300→500ms+包丢 1%）· 数据源故障（行情延迟/暂停2h +异常数据-O大/小空值）· 经纪商API故障（返回HTTP 5xx→503→远端降级）· 计算资源故障（CPU占满→磁盘 IOPS 限制至20%）· 数据损坏（行情/仓位 DB→随机 1行 乱/报纸）。
  （2）自动演练日历——Weekly Drill：Wed 15:00 ET· Monthly Full Chaos：Last Fri· Quarterly BCP Full：末末→自动主持人简报+Slack通道。
  （3）失败升级——演练→ A发现 Exec Quality 等 3/ Mat→ SEMI-O：根因+ 修复→im- D2 层1-12事后 →Incident 级触发Level §20 table。
  §86 定义：
  （1）交易决策解释链——Step1 宏观环境 → Step2 信号产生 → Step3 组合权重优化 → Step4 执行算法 →→all 回路回 writable audit trail。
  （2）模型卡= Model ID/版本/训练数据日期/最后验证/偏差度量（Sharpe比率/IC/最大DD）/公平性指标/已知限制/审核频率（月）→每新模型提交 Owners。
  （3）审计就绪 4 项：全保留—解释链≥ 5年/PII 匿名/人类可读/基元 → 验收：合规审查通过（0 取证）。
  §90 定义：
  （1）实验模板——Template（ID/A/B desc/假设/has+− duration/数据win gates）· 显著性=ε-sigmathreshold→0和非正确分 Prob>0.95 调整大小。
  （2）结果自动记录——New Pos Recorded+logged (always)→ (Best→publish MOD-MASTER-001, Rollback if Fail/sl mor)。结论路径 归档 后 Owner rev 决策-gate。
  本卡搭建 execution_quality.py + what_if_engine.py + chaos_engineering.py + explainability_audit.py + ab_experiment.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\execution_quality.py"
    description: "§77 4维异常(成交率/价格恶化/延迟/拒绝率)+5维经纪商评分(0.25×5)+结算监控 T+1"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\what_if_engine.py"
    description: "§81 参数扫描±20% + MonteCarlo 10000路径Cholesky(VaR+CVaR+MaxDD+破产概率) + 反事实分析"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\chaos_engineering.py"
    description: "§84 5类故障注入(网络/数据/API/CPU/数据损坏)+演练日历(周三/月终/季终)+失败升级"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\explainability_audit.py"
    description: "§86 决策解释链+模型卡(ID/版本/训练日期/偏差/公平性/限制/审计频率)+审计就绪4项"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ab_experiment.py"
    description: "§90 实验模板+显著性ε-threshold+结果自动记录(publish/rollback)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\execution_quality.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\what_if_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\chaos_engineering.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\explainability_audit.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ab_experiment.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§77 4异常+5评分+结算 + §81 参数MC反事实 + §84 5故障+日历+升级 + §86 解释链+模型卡+审计4项 + §90 实验+显著性+记录"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 80

acceptance_criteria:
  - "execution_quality.py 实现 Anomaly4Dim——fill_rate(norm≥90% daily suddenly<80%→alert)· price_deterioration(slippage vs arrival >3σ→estimate EL)· latency_spike(roundtrip>200ms→>500ms anomalous→degrade)· reject_surge(reg|rej>5%/day→review+temp demote broker)· BrokerScoring5(count(成交 0.25+价格改善 0.25+延迟 0.20+拒绝率 0.15+费用效益 0.15)→ daily broker_quality.csv rolling3m healthy min 0.70)· Settlement(report vs internal→T+1 match+position verify→anomaly? enforce 6s settlement call)"
  - "what_if_engine.py 实现 ParamSweep——key params ±20% 5×5 grid→response surface output· MonteCarlo(10000 paths Cholesky decomp→generate VaR/CVaR/MaxDD distribution+Prob(Equity<0)· CounterFactual(if remove factor3× / if different start date historical re-sim →output comparison)"
  - "chaos_engineering.py 实现 FaultInjection——5 types(Network delay 300→500ms+pkt loss1%· Data source delay+2h suspend+anomaly· Broker API 5xx→503 degrade· Compute CPU max+disk IOPS 20%· Data corruption prices+positions 1 random row)· DrillCalendar(Weekly Wed 15:00 ET/Monthly FullChaos Last Fri/Quarterly BCP Full last→auto host brief+Slack)· Escalation(exec quality 3/Mat→semi-o→root cause+fix→post-mortem 1-12→Incident §20 level)"
  - "explainability_audit.py 实现 ExplanationChain——Step1 macro→Step2 signal→Step3 portfolio weight→Step4 execution algo→ all writable audit trail· ModelCard(ID/version/training_date/last_validation/bias(Sharpe/IC/MaxDD)/fairness/known_limits/audit_freq monthly)→new model submit Owner· AuditReady(保留解释链≥5yr/PII anonymized/human-readable/radical→compliance 0 forensics pass)"
  - "ab_experiment.py 实现 ExperimentTemplate——ID/A/B desc/hypothesis+duration/data_win_gates· Significance=ε-sigma threshold non-zero correct Prob>0.95· AutoRecord——new pos logged→best publish MOD-MASTER-001 / rollback if fail → archive → Owner decision-gate"
  - "script_manifest.yaml 注册全部 5 个 .py"

rollback_instructions: |
  1. 删除 execution_quality.py / what_if_engine.py / chaos_engineering.py / explainability_audit.py / ab_experiment.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0028"
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
---
