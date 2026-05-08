---
task_id: "TASK-MST-0031"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §三十七 Round 5 深度交叉审计盲点——B-MOD-301~318(A.测试与质量/B.可观测性/C.安全纵深/D.运维自动化第1~2号)"

title: "实现 Round 5 新盲点关闭——B-MOD-301~318（测试与质量/可观测性/安全纵深/运维自动化前半）"
description: |
  实现蓝图 §三十七（v0.9.0 Round 5 深度交叉审计）注入的 35 个新盲点中的前 18 个（B-MOD-301 ~ B-MOD-318），覆盖 4 个维度。

  **§37.1 审计结果全景矩阵**：蓝图设计完备性 ~92/100（世界级），但可执行性仅 ~15/100（53/54 条 CT-* 为 DO_NOT_CALL）。蓝图的高质量本身制造了"虚假完整感"——这是最深层的元盲点。

  **A. 测试与质量（B-MOD-301~306，6盲点）**——AI施工后无自动化质量关卡（当前最高风险盲区）：
  B-MOD-301(RPN=48🔴)：无AI施工"冒烟测试"关卡——每次AI变更后自动运行最小可运行验证；
  B-MOD-302(RPN=27🟠)：无Property-Based Testing——AI生成代码需fuzz边界值(None/空列表/极大值)；
  B-MOD-303(RPN=40🔴)：无Golden File Test(金标准)——因子/风控计算需ground truth对照集；
  B-MOD-304(RPN=18🟡)：无Chaos Engineering故障注入清单——(4故障点×12系统)具体矩阵；
  B-MOD-305(RPN=18🟡)：无Regression Test Selection(智能选测)——依赖图分析只跑受影响测试子集；
  B-MOD-306(RPN=24🟠)：无Flaky Test Detection——间歇性失败测试毒化CI信任。

  **B. 可观测性（B-MOD-307~311，5盲点）**——Telemetry零采集，"花了多少钱买了什么"黑盒：
  B-MOD-307(RPN=48🔴)：无AI Token"单位产出"度量——每¥1产出有效代码行/功能点/修复Bug数的ROI；
  B-MOD-308(RPN=36🔴)：无Session有效性度量——"真正干活"vs"绕圈子/卡住/幻觉纠正"的Token分布；
  B-MOD-309(RPN=12🟡)：无Blueprint↔Code漂移可视化面板——48%差距的缩小/扩大趋势；
  B-MOD-310(RPN=18🟡)：无AI行为质量时间序列档案——M1→M2→M3→M4阶段质量趋势基线；
  B-MOD-311(RPN=64🔴)：无"系统熵增"度量——重复代码/死代码/蓝图代码不一致/循环依赖的量化趋势（氛围编程结构风险最大项）。

  **C. 安全纵深（B-MOD-312~316，5盲点）**——Supply Chain安全与AI副作用验证完全空白：
  B-MOD-312(RPN=27🟠)：无AI Agent"最小权限"动态评估——session实际需要vs被授予权限的diff审计；
  B-MOD-313(RPN=36🔴)：无Dependency Supply Chain安全扫描——Safety/Snyk/Dependabot集成检测已知漏洞；
  B-MOD-314(RPN=32🔴)：无AI Prompt注入自动化Fuzzing测试——用另一个AI专门攻击自己的prompt找注入漏洞；
  B-MOD-315(RPN=60🔴)：无LLM输出→系统状态实际副作用验证——AI调用FileWrite后验证是否与AI声称一致；
  B-MOD-316(RPN=24🟠)：无Secrets生命周期管理——轮换策略/泄露检测/使用审计/过期提醒/零化确认。

  **D. 运维自动化（B-MOD-317~318，前2盲点）**——Bus factor=1场景下Owner认知恢复无协议：
  B-MOD-317(RPN=45🔴)：无G6 REJECT后的Session自动恢复链——下个session需知道"为什么被拒/修了什么/可否继续"；
  B-MOD-318(RPN=45🔴)：无系统"一键健康检查"命令——Owner每天早上打开IDE跑一个命令看到🟢🟡🔴12系统健康面板+建议动作TOP3。

  **施工策略**：B-MOD-303/307/308/311/315/317/318（7个高优先级）可通过扩展现有模块实现（Telemetry采集+Script System审计+Gate Engine门禁），而非新建模块。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\gate_engine.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\blindspot_r5_1_18.py"
    description: "Round 5 盲点1~18门禁实现——B-MOD-301~318，含冒烟测试/Property-Based/Golden File/Flaky/Token ROI/Session效率/熵增/供应链扫描/Prompt Fuzzing/副作用验证/一键健康等check方法"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\quality_metrics.py"
    description: "质量可观测性采集器——B-MOD-307/308/310/311——Token ROI + Session效率 + AI质量趋势 + 系统熵增"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\security\\supply_chain_scanner.py"
    description: "供应链安全扫描器——B-MOD-313——Safety/Snyk集成+依赖漏洞检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\security\\prompt_fuzzer.py"
    description: "Prompt注入Fuzzing引擎——B-MOD-314——对抗性AI攻击自身prompt"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\security\\side_effect_validator.py"
    description: "AI副作用验证器——B-MOD-315——FileWrite/ShellExecute前后状态diff"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\one_click_health.py"
    description: "一键健康检查命令——B-MOD-318——12系统面板+TOP3建议+最近变更摘要"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_blindspot_r5_1_18.py"
    description: "Round 5 盲点1~18单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_quality_metrics.py"
    description: "质量可观测性单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_supply_chain_scanner.py"
    description: "供应链扫描单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_prompt_fuzzer.py"
    description: "Prompt Fuzzing单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\blindspot_r5_1_18.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\telemetry\\quality_metrics.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\security\\supply_chain_scanner.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\security\\prompt_fuzzer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\security\\side_effect_validator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\one_click_health.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_blindspot_r5_1_18.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_quality_metrics.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_supply_chain_scanner.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_prompt_fuzzer.py"

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
    reason: "§三十七——Round 5 深度交叉审计 B-MOD-301~318 完整定义（A.测试与质量6盲点 + B.可观测性5盲点 + C.安全纵深5盲点 + D.运维自动化前2盲点）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 14000
timeout_minutes: 90

acceptance_criteria:
  - "B-MOD-301: 每次AI变更后自动运行smoke_test——最小可运行验证 → FAIL→block merge"
  - "B-MOD-303: 因子/风控计算的Golden File Test——known ground truth对照集 → output diff→CI FAIL"
  - "B-MOD-307: Token ROI度量——每¥1产出的有效代码行/功能点/修复Bug数 → FLE飞书日报"
  - "B-MOD-308: Session有效性度量——'干活token' vs '绕圈子token' 的比例 → 拐点检测"
  - "B-MOD-311: 系统熵增趋势量化——重复代码率+死代码率+蓝图代码不一致率+循环依赖数 → 每周趋势报告"
  - "B-MOD-313: Dependency Supply Chain扫描——Safety check pyproject.toml依赖 → 有已知漏洞→CI FAIL"
  - "B-MOD-314: Prompt注入Fuzzing——对抗性AI生成100+ malicious input → 检测AI是否被注入"
  - "B-MOD-315: 副作用验证——AI执行FileWrite/ShellExecute → 验证实际文件变化与声明一致 → 不一致→ALERT"
  - "B-MOD-317: G6 REJECT恢复链——下一session自动读取reject_reason + fixed_items + can_continue → 不重复犯错"
  - "B-MOD-318: 一键健康检查——python scripts/health_check.py → 🟢🟡🔴12系统面板 + 建议动作TOP3 → <2min"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\gates\blindspot_r5_1_18.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\telemetry\quality_metrics.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\security\supply_chain_scanner.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\security\prompt_fuzzer.py
  5. 删除 D:\ZephyrAlpha\src\zephyr\security\side_effect_validator.py
  6. 删除 D:\ZephyrAlpha\src\zephyr\orchestrator\one_click_health.py
  7. 删除新增的测试文件

depends_on: []
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
