---
task_id: "TASK-MST-0032"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §三十七 Round 5 深度交叉审计盲点——B-MOD-319~335(D.运维自动化第3~5号/E.氛围编程特有/F.金融业务/G.蓝图自身) + §37.9 汇总 + §37.10 1人+AI生存三法则"

title: "实现 Round 5 新盲点关闭——B-MOD-319~335（运维自动化后半/氛围编程特有/金融业务/蓝图自身）+ 1人+AI生存三法则"
description: |
  实现蓝图 §三十七（v0.9.0 Round 5 深度交叉审计）35 个新盲点中的后 17 个（B-MOD-319 ~ B-MOD-335），覆盖 4 个维度 + §37.10 生存三法则。

  **D. 运维自动化（B-MOD-319~321，后3盲点）**：
  B-MOD-319(RPN=48🔴)：无"Owner认知恢复协议"——出差/休假2周回来大脑已忘记系统全貌，需AI自动生成"你离开期间发生了什么"摘要；
  B-MOD-320(RPN=12🟡)：无磁盘空间监控与自动清理联动——CT-DISK-GUARD仅检测但不触发CT-LEAN清理；
  B-MOD-321(RPN=12🟡)：无数据库真空操作自动化调度——SQLite高频写入后需VACUUM/ANALYZE/PRAGMA integrity_check自动调度。

  **E. 氛围编程特有（B-MOD-322~328，7盲点）**——专业机构不靠vibe coding，这是ZephyrAlpha特化盲区：
  B-MOD-322(RPN=60🔴)：无AI"施工节奏"强制执行——M1模块应每天≤3文件变更，M3可>10，无运行时强制→AI以M4速度施工M1模块一次改20个文件全搞砸；
  B-MOD-323(RPN=36🔴)：无"AI疲劳检测"——同一session内AI产出质量随Token消耗下降，拐点在哪？30分钟？100K tokens？需量化并在拐点前提醒Owner新建session；
  B-MOD-324(RPN=18🟡)：无"上下文切换成本"度量——AI在多个模块间跳跃施工vs专注一个模块的质量差异，需数据支撑"串行vs并行"策略决策；
  B-MOD-325(RPN=18🟡)：无"AI建议采纳率"追踪——AI建议Owner接受了多少/拒绝了多少/修改后接受多少，反映AI决策质量和协作成熟度；
  B-MOD-326(RPN=64🔴)：无"跨Session设计一致性"校验——周一AI和周三AI可能做出矛盾设计决策，需在Session启动时注入"上一次施工的决策记录"；
  B-MOD-327(RPN=18🟡)：无"蓝图Token预算vs实际消耗"反馈回路——蓝图声明8000 token预算但每次实际注入多少？命中率多少？需闭环反馈驱动预算优化；
  B-MOD-328(RPN=64🔴)：无"AI暗知识传递"漏洞——某个session的AI发现架构问题但没强制写入蓝图/Handoff，下个AI永远不知道。

  **F. 金融业务（B-MOD-329~332，4盲点）**——模型风险治理/实盘硬断路器完全缺失：
  B-MOD-329(RPN=45🔴)：无交易策略渐进式上线路径——因子/策略从创建→回测→paper trading→小仓位→全仓位的生命周期管理，AI可能直接从回测跳到实盘；
  B-MOD-330(RPN=20🟠)：无实时风险敞口硬限制——不依赖AI/风控模块判断的运行时硬断路器"无论发生什么都不可越过position limit/leverage cap/cash reserve floor"；
  B-MOD-331(RPN=20🟠)：无市场异常自动熔断——闪崩/流动性枯竭/波动率突然爆发→自动减仓或停止交易，需独立于主风控模块的旁路监控；
  B-MOD-332(RPN=36🔴)：无回测过拟合检测——AI优化因子时天然容易过拟合历史数据，需Deflated Sharpe Ratio/Probabilistic Sharpe Ratio/CSCV等检验。

  **G. 蓝图自身体系（B-MOD-333~335，3盲点）**——蓝图定义了一切怎么健康，但蓝图本身也需要健康管控：
  B-MOD-333(RPN=32🟠)：蓝图自身膨胀无管控——SYS-MASTER从0.1.0→0.5.0增长4倍，MOD-MASTER从0.1.0→0.9.0持续膨胀，CT-KISS控制了代码膨胀但无人控制蓝图膨胀；
  B-MOD-334(RPN=27🟠)：无蓝图"影响力分析"——修改一条CT-*契约影响哪些模块？哪些AI行为会改变？没有依赖追踪和影响传播范围评估；
  B-MOD-335(RPN=16🟡)：无蓝图与外部标准的合规映射矩阵——ISO 27001/ISO 42001/MiFID II/NIST AI RMF各控制项对应蓝图的哪个§/哪条CT-*？

  **§37.9 35盲点汇总与优先级**：P0=16个(B301/303/307/308/311/313/314/315/317/318/319/322/323/326/328/332)，P1=12个，P2=7个。建议14个P0在本轮立即施工，其中11个可通过扩展现有模块实现。

  **§37.10 1人+AI的生存三法则（施工指引，非盲点）**：
  法则1「Owner能量预算管理」——Owner每天有有限的"决策能量"。AI不应每天抛出10个"你选A还是B？"的问题。定义AI自主决策比例的渐进提升路径：beta阶段30%自主/70% ASK→stable阶段70%自主/30% ASK→production阶段90%自主/10% ASK（仅P0事务）。监控"每日ASK次数"指标→超过阈值→AI需改进自主决策能力。
  法则2「系统自我解释能力」——蓝图~3,800行+子蓝图9,000+行=Owner不可能全记住。AI每次被问"系统当前状态"时必须在30秒~2分钟内输出摘要（对标AWS Well-Architected Tool）：(1)总体健康分+趋势箭头 (2)TOP3风险+建议动作 (3)最近变更摘要 (4)需Owner关注事项≤3项。
  法则3「系统降级运行三模式」——FULL(生产):全部54CT-*在线(策略实盘/实盘风控)；CORE(日常开发):核心15CT-*在线(Orc/CE/Gate/Script/DB/FLE)；MINIMAL(紧急):仅5CT-*在线(Health/Gate/DB/Backup/Watchdog)——Owner出差/系统故障时的生存底线。切换条件：手动触发OR CT-AUTONOMY-001 l3(72h)自动触发。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\gate_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\blindspot_r5_19_35.py"
    description: "Round 5 盲点19~35门禁实现——B-MOD-319~335，含Owner认知恢复/施工节奏/AI疲劳/跨Session一致性/暗知识传递/策略上线路径/实盘硬断路器/回测过拟合/蓝图膨胀/影响力分析/合规映射等check方法"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\owner_recovery.py"
    description: "Owner认知恢复协议——B-MOD-319——自动生成'你离开期间发生了什么'摘要（变更清单+新盲点+待确认事项）"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\vibe_guard.py"
    description: "氛围编程防护器——B-MOD-322/323/326/328——施工节奏强制执行+AI疲劳检测+跨Session一致性校验+暗知识强制写入"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\trading\\strategy_lifecycle.py"
    description: "策略生命周期管理器——B-MOD-329——创建→回测→paper trading→小仓位→全仓位5阶段门禁"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\trading\\hard_circuit_breaker.py"
    description: "实盘硬断路器——B-MOD-330/331——position limit/leverage cap/cash reserve floor硬限制+市场异常自动熔断"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\trading\\overfit_detector.py"
    description: "回测过拟合检测器——B-MOD-332——Deflated Sharpe/Probabilistic Sharpe/CSCV检验"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\blueprint_bloat_guard.py"
    description: "蓝图膨胀防护——B-MOD-333/334——蓝图行数预算+契约影响力分析"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\compliance_matrix.py"
    description: "合规映射矩阵——B-MOD-335——ISO 27001/ISO 42001/MiFID II/NIST AI RMF→蓝图§/CT-*映射"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\survival_rules.py"
    description: "生存三法则执行器——§37.10——能量预算监控+自我解释摘要+降级模式切换"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_blindspot_r5_19_35.py"
    description: "Round 5 盲点19~35单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_owner_recovery.py"
    description: "Owner认知恢复单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_vibe_guard.py"
    description: "氛围编程防护单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\blindspot_r5_19_35.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\owner_recovery.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\vibe_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\trading\\strategy_lifecycle.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\trading\\hard_circuit_breaker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\trading\\overfit_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\blueprint_bloat_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\compliance_matrix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\survival_rules.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_blindspot_r5_19_35.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_owner_recovery.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_vibe_guard.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\gate_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§三十七——Round 5 深度交叉审计 B-MOD-319~335 完整定义（D.运维自动化后3盲点 + E.氛围编程特有7盲点 + F.金融业务4盲点 + G.蓝图自身3盲点）+ §37.9 汇总 + §37.10 生存三法则"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 90

acceptance_criteria:
  - "B-MOD-319: Owner出差/休假2周回来→AI自动生成'你离开期间发生了什么'摘要（变更清单+新盲点+待确认事项+建议动作TOP3）"
  - "B-MOD-322: M1模块施工→ci_enforce_file_limit检查→单session≤3文件变更→超标→REJECT"
  - "B-MOD-323: AI疲劳检测→监控session内quality_score趋势→拐点检测→提醒Owner新建session"
  - "B-MOD-326: Session启动时注入上一次施工的decision_record→设计一致性校验→矛盾→WARN Owner"
  - "B-MOD-328: AI发现架构问题→强制写入handoff manifest或蓝图→下一个session可见→未写入→GATE REJECT"
  - "B-MOD-329: 策略5阶段门禁——创建→回测→paper→小仓→全仓——每阶段独立gate check→越级→CI FAIL"
  - "B-MOD-330: 实盘硬断路器——position/leverage/cash独立进程监控→超限→直接熔断（不经过AI决策）"
  - "B-MOD-332: 回测过拟合检测——Deflated Sharpe Ratio < 0.05 → 标记OVERFIT_WARNING → 阻止直接上线"
  - "B-MOD-333: 蓝图膨胀管控——蓝图行数超过budget→CI WARN + 要求Owner审批扩写"
  - "§37.10 法则1: 每日ASK次数指标→连续3天超阈值→推送Owner报告 + AI自主决策能力改进建议"
  - "§37.10 法则2: 一键摘要命令输出格式——健康分+TOP3风险+最近变更+关注事项 ≤ 4项内容"
  - "§37.10 法则3: 降级模式自动切换——MINIMAL模式仅运行Health/Gate/DB/Backup/Watchdog 5条CT-*"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\gates\blindspot_r5_19_35.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\owner_recovery.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\gates\vibe_guard.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\trading\strategy_lifecycle.py
  5. 删除 D:\ZephyrAlpha\src\zephyr\trading\hard_circuit_breaker.py
  6. 删除 D:\ZephyrAlpha\src\zephyr\trading\overfit_detector.py
  7. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\blueprint_bloat_guard.py
  8. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\compliance_matrix.py
  9. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\survival_rules.py
  10. 删除新增的测试文件

depends_on: ["TASK-MST-0031"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
