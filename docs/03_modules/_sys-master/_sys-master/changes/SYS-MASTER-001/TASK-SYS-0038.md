---
task_id: "TASK-SYS-0038"
source_blueprint: "SYS-MASTER-001"
source_section: "§101 基准与评估完整性保障 + §102 跨环境一致性与Windows 11本地化 + §一百〇三 变更记录与维护审计"

title: "基准完整性四维(行情覆盖/因子一致性/回测稳定性/HFT保真度)+Point-in-Time(≤15min延迟/←→+T)+健康检查月/季度 + 跨环境四维一致性(Python版本/依赖版本/数据结构/data seed/模型输出浮点ε<1e-9)+Win11风险矩阵(权限/路径PS/CRLF编码/内存/进程)+幂等脚本(npm-PS) + 变更记录(版本/日期/影响/描述/Author)三合一最终保障"
description: |
  将 §101 基准完整性 + §102 跨环境一致性 + §一百〇三 变更记录三合一落地为系统最终质量保障防线。
  §101 定义：
  （1）四维基准完整性——行情覆盖（所有活跃symbol有≥1年数据+∅缺测/周<0.1%→验证年/季度）· 因子一致性（信号activation相同+summary stat中逐月→IC/Sharpe stable<10% relative→验证月）· 回测稳定（反复 5次 full backtest→逐月 pnl std< 基pct1%→验证周）· HFT保真度（tick-to-trade模型准确>99%→验证周）。
  （2）Point-in-Time（PIT）——行情mat ≤15min delay· Previous Close→标记 T-1 vs T errors→验证：POINTS Retrieve以 EXACT时间点。
  （3）健康检查——月度(Dim 1-4 above· 自动run  grid) 季度(Full历史 2016-2024 re-run与 九月 bl match→输出偏差报告) →不一致→Owner通知。
  §102 定义：
  （1）四维跨环境一致性——Python版本（exact 3.11.9→≤month drift chk）· 依赖版本（freeze.md5 hash exact≤month diff→drift alert）· 数据结构（parquet/pickle→schema 一致+ NULL空 !=None→ digital backbone detect）· Model Output（回测PnL 浮点 toler<1e-9→ 运行5y backtest全环境比→diff report XML）。
  （2）Win11风险矩阵——权限（lm / admin escalation blocked / UAC→firewall自动like disable b causal）· 路径反斜杠（X:→所有参考一致 [WSL+X:/?] →antipattern if source_diff）· CRLF编码（gitattributes→`*.bat/proj/csproj text eol=crlf`^ ）· 内存（Win专属>=16GB→ constant ready→≤内存Load avg】<75%）· 进程（环境排黑(bg)只有一个python脚本: system_module required =1。）。
  （3）幂等脚本——可重复执行——新系统配置 ——所有脚本-PS,Bash,task 仅→生成。
  §一百〇三 定义：
  变更记录格式——日期 (YYYY-MM-DD) / 版本 / 影响(破坏性/增强/修复) / 节影响 / 描述 / Author。
  示例："2026-02-15 / v1.0.0 / 新增 / §1-50 全局 / 初始蓝图创建 / AI 辅助 Owner 终裁"。
  本卡搭建 benchmark_integrity.py + cross_env_consistency.py + changelog_manager.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\benchmark_integrity.py"
    description: "§101 4维(行情覆盖/因子一致性/回测稳定性/HFT保真度)+PIT+健康检查月/季度"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\cross_env_consistency.py"
    description: "§102 4维(Python3.11.9/依赖hash/数据结构schema/Model输出ε<1e-9)+Win11风险矩阵(权限/路径/CRLF/内存<75%/进程)+幂等脚本"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\changelog_manager.py"
    description: "§103 变更记录(日期/版本/影响/节/描述/Author)→自动追加+格式校验"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\benchmark_integrity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\cross_env_consistency.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\changelog_manager.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§101 4维基准+PIT+健康检查 + §102 4维一致性+Win11风险+幂等 + §103 变更记录格式"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 22000
timeout_minutes: 60

acceptance_criteria:
  - "benchmark_integrity.py 实现 IntegrityDim 枚举（MARKET_COVERAGE/FACTOR_CONSISTENCY/BACKTEST_STABILITY/HFT_FIDELITY）——COVERAGE(all active symbols ≥1yr data+∅missing/wk<0.1%→verify year/quarter)· FACTOR(signal activation identical+summary monthly IC/Sharpe stable<10% relative→verify monthly)· BACKTEST(5×full backtest→monthly pnl std<base_pct1%→verify weekly)· HFT(tick-to-trade accuracy>99%→verify weekly)· PIT(mkt data ≤15min delay+PrevClose→T-1 vs T error marked)· HealthCheck(monthly above dims+grid run/quarterly full 2016-2024 re-run vs Sept→bias report→inconsist→Owner notify)"
  - "cross_env_consistency.py 实现 ConsistencyDim（PYTHON/DEPENDENCIES/DATA_STRUCTURE/MODEL_OUTPUT）——PYTHON(exact 3.11.9 ≤month drift check)· DEPS(freeze.md5 hash exact ≤month→drift alert)· DATA(parquet/pickle schema consist+NULL!=None detected)· MODEL(backtest pnl float toler<1e-9→run 5y backtest all envs→diff report XML)· Win11Matrix(权限 escal blocked UAC auto firewall· 路径反斜杠 X:→ all refs consistent WSL+/ antipattern if source diff· CRLF gitattr *.bat/proj eol=crlf· 内存 Win≥16GB load avg<75%· 进程 single python system_module=1)· IdempotentScripts(PS+Bash+task re-exec generate same output always)"
  - "changelog_manager.py 实现 Changelog——format(日期 YYYY-MM-DD / 版本 / 影响(破坏/增强/修复) / 节影响 / 描述 / Author)——auto append to _sys-master/changelog.md· validate format on commit· warn on duplicate version→ block commit"
  - "script_manifest.yaml 注册全部 3 个 .py"

rollback_instructions: |
  1. 删除 benchmark_integrity.py / cross_env_consistency.py / changelog_manager.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0037"
blocked_by: []
status: "done"
tags_fn:
  - "qa"
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
