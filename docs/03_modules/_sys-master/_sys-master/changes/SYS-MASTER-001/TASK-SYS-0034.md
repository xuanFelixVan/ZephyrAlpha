---

task_id: "TASK-SYS-0034"
source_blueprint: "SYS-MASTER-001"
source_section: "§54 AI代码审查深度模型 + §67 AI自诊断-自修复与知识自动化 + §71 Prompt工程全生命周期管理 + §72 AI上下文窗口策略与幻觉防御 + §73 多模型共识与智能体辩论协议 + §74 AI代码生成标准与项目脚手架"

title: "AI代码审查六级(L0 ruff→L1安全审计→L2逻辑+边界→L3架构对齐→L4策略对齐→L5双AI辩论)+三审查规则(全AI产出必经L3/模块冒烟实验/VibeCoding审查)+ 自诊断三修复层(L1 AutoFix/L2 Suggest→AutoApply/L3 Report)+AUTO-KB + Prompt版本控制+回归测试+契约+PES + 上下文五级预算(500/2K/5K/18K/40K)+渐进加载+裁剪规则+幻觉三级检测+自动修复 + 多模型三种共识协议(多数/加权/全票)+辩论三轮(R1→R2→R3)+能力图谱+异议升级 + AI代码六约定(文件/脚手架/代码头/注释禁止/import/类型提示) 六合一AI品质闭环"
description: |
  将 §54 AI代码审查 + §67 自诊断 + §71 Prompt工程 + §72 上下文窗口 + §73 多模型共识 + §74 AI代码标准六合一落地为AI施工品质全闭环。
  §54 定义：
  （1）审查深度 6 级——L0 语法-格式（ruff,延期<1min）· L1 安全审计（secret scan+依赖漏洞扫描 §80→阻断）· L2 逻辑与边界（边界检查+空值处理→<5min）· L3 架构对齐（blueprint契约+allowed/forbidden touch §45→模块冒烟集合）· L4 策略对齐（信号→回测§三维→熵+性能 允许Override?）· L5 双AI辩论（A审查B反审查→Owner终裁仅L5）。
  （2）三条审查规则——所有AI产出MUST通过L3· 模块部署前L3+L4完整审查· 氛围编程黄金路径：AI自L2→→AI同伴查至L3→OwnerL4 标志→终。
  §67 定义：
  （1）三层自修复——L1 AutoFix（已知模式：修复→TDD runner→回测5年→blacks/ruff auto accept 无需Owner）· L2 Suggest→AutoApply（新模式：建议→无Owner在线？+建设>风险→自动应用+注日志+下次Owner禁止）· L3 Report Only（需深层方案建议）。
  （2）AUTO-KB 知识自动化——发现→记录→解决→防御→文档化 5步无缝+知识库本地 SQL 每次入。
  §71 定义：
  （1）Prompt生命周期——版本号（P-ID + SemanticVersion 增量=DEPLOY 后+1）· 回归测试（改变→test_old_vs_new→只允许下降<5%性能阈值）· 契约层（Functions Protocol P-QoS ）→PES（结构化提示缓存）。
  §72 定义：
  （1）上下文窗口策略——5 级预算 Tier0-500 / T1-2K / T2-5K / T3-18K / T4-40K token（根据 task复杂度动态 route）· 上下文容量（按需逐步扩展加载子蓝图 parts）· 裁剪规则（过近上下文 →删除重复误差>30%· 错误优先+last 30day+全引用文档 retain）。
  （2）幻觉三级检测——L1 事实一致性 Reject（deactivate+retry template）· L2 蓝图冲突（在输出中标记差值→对比→差异>%threshold DEACT）· L3 自指悖论（输出中产生否决自己=new→检测）→ 自动修复（deactive模块+REST_API→旧版模型→default）。
  §73 定义：
  （1）三种多模型共识协议——多数投票（50%+相同结果）· 加权投票（static Q分数 (A/B/C)+ rate）· 全票共识（核心决策 P0-1 门槛）。
  （2）结构化辩论格式——Round1 模型A单一解答（背景+推理+证据）→ Round2 模型B挑战（可替代+矛盾点）→ Round3 模型A最终反驳+改变结论？→ 诉辩目录 YAML 结果最终保留。
  （3）模型能力图谱——task×model map（生成/分析/数学/语义/代码/创意）×置信度。
  （4）异议升级——三模型都不同意/识别 self-长等待?→ Owner通知强制干预。
  §74 定义：
  （1）6 项代码约定——文件组织（按"约定"YAML abord）· Scaffold template（python setup+page=模板,自动生成）· 代码头（Python:shebang+path）· 注释（no justification/no redundant → code self-document → 需要的话 majors only）· import 顺序（future→stdlib→3rd→local）+自动 isort → 类型提示（全部 public 函数 must）。
  （2）AI 禁止模式——禁止生成注释 in demo/example· 生成测试必须 Fail 吗？(TDD mode,必须 fail——pass=bad) → Vibe模式。
  本卡搭建 code_review_ai.py + ai_self_diagnosis.py + prompt_lifecycle.py + context_manager.py + multi_model_consensus.py + ai_code_standards.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\code_review_ai.py"
    description: "§54 L0-L5六级审查 + 3审查规则(必经L3/冒烟L3+L4/黄金路径L2-L3-L4)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ai_self_diagnosis.py"
    description: "§67 3层自修复(L1Auto/L2Suggest/L3Report)+AUTO-KB 5步知识自动化"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\prompt_lifecycle.py"
    description: "§71 Prompt版本+回归测试(<5%退化)+契约+PES缓存"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\context_manager.py"
    description: "§72 5级Token预算(500/2K/5K/18K/40K)+渐进加载+裁剪+幻觉3级检测+修复"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\multi_model_consensus.py"
    description: "§73 3协议(多数/加权/全票)+辩论3轮(R1→R3)+能力图谱+异议升级Owner"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ai_code_standards.py"
    description: "§74 6约定(文件/脚手架/代码头/注释禁止/import顺序/类型提示)+禁止模式"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\code_review_ai.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ai_self_diagnosis.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\prompt_lifecycle.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\context_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\multi_model_consensus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ai_code_standards.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§54 L0-L5审查+3规则 + §67 3修复层+AUTO-KB + §71 Prompt版本/回归/契约/PES + §72 5Token预算/幻觉 + §73 3共识/辩论/能力/异议 + §74 6约定/禁止模式"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 35000
timeout_minutes: 90

acceptance_criteria:
  - "code_review_ai.py 实现 ReviewLevel（L0到L5）——L0(ruff <1min commit)· L1(secret+dep scan→block)· L2(boundary+null check <5min)· L3(blueprint allowed/forbidden+smoke test)· L4(signal counterpart check override? §3)· L5(dual AI debate A review B counter→Owner final only at L5)· 3 Rules(all AI MUST L3· module pre-deploy L3+L4· vibe path L2→peer check L3→OwnerL4 final)"
  - "ai_self_diagnosis.py 实现 RepairLayer(L1_AUTOFIX/L2_SUGGEST_AUTOAPPLY/L3_REPORT)——L1(known patterns fix→TDD→backtest 5yr→blacks ruff auto accept)· L2(new pattern→>Owner online? suggest→ apply+log+future veto)· L3(report deep fix suggestions)· AutoKB(Discover→Record→Solve→Defend→Document 5step seamless→SQL local)"
  - "prompt_lifecycle.py 实现 PromptVersioner——P-ID+SemanticVer increment on deploy +1· RegressionTest(change→test_old_vs_new→allow <5% degradation)· ContractLayer(Fn_Protocol P-QoS)· PES(structured prompt cache)"
  - "context_manager.py 实现 TokenBudget——5 tiers(T0 500/T1 2K/T2 5K/T3 18K/T4 40K)→dynamic route by task complexity· ProgressiveLoad(sub-blueprint parts on demand)· ClipRule(near duplicate>30%→drop· errors first+last 30days+all ref docs retain)· HallucinationDetect(L1 fact check reject deactivate+retry· L2 blueprint conflict mark diff→>threshold deact· L3 self-refute output negates self→detect)· AutoFix(deactivate module+REST old model default)"
  - "multi_model_consensus.py 实现 ConsensusProtocol（MAJORITY/WEIGHTED/UNANIMOUS）——MAJORITY 50%+same· WEIGHTED static Q+A/B/C+rate· UNANIMOUS P0-1 gate· Debate(R1 modelA answer→R2 modelB challenge alt+contradiction→R3 modelA final rebut+change?→ YAML result saved)· CapabilityMap(task×model map gen/analysis/math/semantic/code/creative ×confidence)· Escalation(all3disagree OR self-long-wait→Owner manual override)"
  - "ai_code_standards.py 实现 CodeConvention——6 items YAML· ScaffoldGenerator(template auto-gen python setup)· HeaderEnum python shebang+path· CommentEnum(no justification+no redundant→self-doc· isort(import order)→type hints(all public→must)· VerboseForbidEnum(no demo/example comments· tests MUST fail on first TDD→pass=bad vibe)"
  - "script_manifest.yaml 注册全部 6 个 .py"

rollback_instructions: |
  1. 删除 code_review_ai.py / ai_self_diagnosis.py / prompt_lifecycle.py / context_manager.py / multi_model_consensus.py / ai_code_standards.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0033"
blocked_by: []
status: "done"
tags_fn:
  - "ai"
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
