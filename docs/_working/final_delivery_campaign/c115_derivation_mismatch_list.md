---
ttl: task_bound
title: "C115 派生错配八条清单（functional_domain_registry ssot_path↔covers B 类须裁项）"
session: st-finaldel-lists-20260930
completes_when: "Owner 逐条勾选处置方向后，另批施工；本清单只读不改册"
---

# C115 · 八条派生错配清单（ Owner 裁定用）

> **工卡**：`docs/_working/final_delivery_campaign/workorders_governance.md` L54（C115，OWNER_GATE，M+Owner；卡面明示"8 条错配列 Owner 裁定"）。
> **依据（HEAD）**：`docs/_working/total_command_closeout/wave5/registry_derivation_report.md` §1.2（L107-133 实测表）+ §5.4（L392-428 待裁表）；`docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`（entries=94，本清单零改动）。
> **范围口径**：报告 §1.2 实测错配共 10 条，其中 A 类 2 条（#7 D_AUTONOMY_CORE/agent_communication、#10 D_DATA/data_source_integrator）报告已给确定 diff、属"按 report 改册"机械面，**不在本清单**；余 B 类 **8 条**（§5.4 明示"逐条须裁定，本包不给臆测路径"）即本清单。SKIP-6 治本项（`total_gates` 派生计数，af7e492276 total_* 自动发现器）已闭合，不在 8 条内。
> **HEAD 复核（2026-09-30 本会话实测，8/8 仍错配）**：`test -d` 三路径全 MISSING、`grep -rlw` 三符号按声称面零命中/他域命中；CR-008 尺**未落 HEAD**（`check_registry_consistency.py` 现无 verify_domain_ssot，报告 §2 三件属 AI 余量另线），故下表证据以报告行锚+本会话手工复测双列。
> **每条复算命令（HEAD 可跑）**：
> ```bash
> test -d src/zephyr/autonomy_perm && echo EXISTS || echo MISSING          # 条1/2
> test -d src/zephyr/data/persistence && echo EXISTS || echo MISSING       # 条3（同名唯一=governance/persistence）
> test -d src/zephyr/shared/shared_services && echo EXISTS || echo MISSING # 条4
> grep -rlw "CanaryController\|CascadeDetector" src/zephyr scripts         # 条6（预期空）
> grep -rlw "HITL" src/zephyr                                              # 条8（命中在他域）
> grep -rlw "KnowledgeBaseServer" src/zephyr scripts                       # 条9（预期空）
> ```

## 八条逐条（涉册全部=functional_domain_registry.yaml；行锚=registry_derivation_report.md 行号）

### 条 1 · D_AUTONOMY_PERM/budget_enforcement —— PATH_MISSING
- **错配描述**：ssot_path 指向 `src/zephyr/autonomy_perm/`，全仓无此包（`autonomy_perm` 仅作为域名字符串出现于 `governance/agent_spec/rbac_bridge.py` 等，无实体目录）。
- **涉册**：functional_domain_registry.yaml（D_AUTONOMY_PERM 域 2 条中第 1 条）。
- **证据**：report L121（§1.2 表）、L420（§5.4 待裁表行"1–2"）；本会话复测 `test -d` = MISSING。
- **建议处置**：**改册+Owner 裁**——该域整块无实体：判"真未落地"则两条目标 backlog/退役（净删=high 门位）；判"路径写错"则 RBAC 实现在 `src/zephyr/security/access_control/` 是否指此须裁定。
- Owner 勾选：☐同意建议 ☐其他（注明）

### 条 2 · D_AUTONOMY_PERM/escalation —— PATH_MISSING
- **错配描述**：同条 1 病灶（同域第 2 条，同指不存在的 `src/zephyr/autonomy_perm/`；covers 声称 EscalationEngine/DelegationEngine 等随域悬空）。
- **涉册**：functional_domain_registry.yaml（D_AUTONOMY_PERM 第 2 条）。
- **证据**：report L122、L420（与条 1 同表行）；本会话复测 `test -d` = MISSING。
- **建议处置**：**改册+Owner 裁**——与条 1 同批同向裁定（退役/backlog/改指 security/access_control），禁止两条分叉处置。
- Owner 勾选：☐同意建议 ☐其他（注明）

### 条 3 · D_INFRA_RUNTIME/persistence —— PATH_MISSING
- **错配描述**：ssot_path 指向 `src/zephyr/data/persistence/`，不存在；全仓同名唯一目录=`src/zephyr/governance/persistence/`（跨域）。
- **涉册**：functional_domain_registry.yaml（D_INFRA_RUNTIME/persistence 条）。
- **证据**：report L123、L421；本会话复测：data/persistence=MISSING、governance/persistence=EXISTS。
- **建议处置**：**改册+Owner 裁**——治理域目录能否作 D_INFRA_RUNTIME 子域真源：改指会破"域=目录"口径（跨域指向），维持现值则条目恒红；须裁定口径归属后改 ssot_path 或改域归属。
- Owner 勾选：☐同意建议 ☐其他（注明）

### 条 4 · D_SHARED/shared_services —— PATH_MISSING
- **错配描述**：ssot_path 指向 `src/zephyr/shared/shared_services/`，不存在；`src/zephyr/shared/` 存在但无该子包（covers 声称的 event_bus/lazy_loader/file_utils 实体散在 shared/ 各处）。
- **涉册**：functional_domain_registry.yaml（D_SHARED/shared_services 条）。
- **证据**：report L124、L422；本会话复测 `test -d` = MISSING。
- **建议处置**：**改册+Owner 裁**——三选一：①条目退役（注册表净删=high 门位）②补实体目录③ssot_path 改指 `src/zephyr/shared/` 上层并收窄 covers 文案。
- Owner 勾选：☐同意建议 ☐其他（注明）

### 条 5 · D_TEST/test_domain_placeholder —— PATH_UNDECLARED
- **错配描述**：ssot_path 写成括注 `(depgraph domains.ssot_path 为空)`，非路径（自述占位域，depgraph 实测 0 节点）。
- **涉册**：functional_domain_registry.yaml（D_TEST/test_domain_placeholder 条）。
- **证据**：report L125、L423；本会话册面现读确认括注原文仍在（covers 自述"空壳域…净删属 Owner 门位"）。
- **建议处置**：**改册+Owner 裁**——保留则须显式豁免登记（占位条目进豁免白名单，CR-008 落地后不哭狼），不允许静默绿；否则净删（high 门位）。
- Owner 勾选：☐同意建议 ☐其他（注明）

### 条 6 · D_GOV_DRIFT/drift_detection —— COVERS_UNFOUND
- **错配描述**：ssot_path `src/zephyr/gov_drift/` 存在，但 covers 声称的 `CanaryController`/`CascadeDetector` 两符号全仓 0 命中（词边界 grep）——承诺未建能力。
- **涉册**：functional_domain_registry.yaml（D_GOV_DRIFT/drift_detection 条）。
- **证据**：report L126、L424（§5.4 表"#6"行）；本会话复测 `grep -rlw` = 0 命中。
- **建议处置**：**改册+Owner 裁**——删 covers 未建声称（收敛承诺面）或转列 backlog 显式标记"规划中"；报告红证逼出的词边界尺（防 CanaryControllerV2 子串假阳性）随 CR-008 落地同批。
- Owner 勾选：☐同意建议 ☐其他（注明）

### 条 7 · D_SECURITY_LLM/llm_defense —— COVERS_UNFOUND（跨域命中）
- **错配描述**：ssot_path `src/zephyr/security/llm_defense/` 本体存在，但 covers 声称的 `HITL` 命中面在 `src/zephyr/integration/pipeline_orchestrator.py`、`src/zephyr/intelligence/*`，非 llm_defense——跨域声称或文案误挂。
- **涉册**：functional_domain_registry.yaml（D_SECURITY_LLM/llm_defense 条）。
- **证据**：report L128、L425；本会话复测 `grep -rlw HITL src/zephyr` = 命中 integration+intelligence，llm_defense 面零命中。
- **建议处置**：**改册+Owner 裁**——判"跨域声称"（HITL 语义属 llm_defense 但实现在他域→covers 注记实现位置）或"文案误挂"（直接删该声称项）。
- Owner 勾选：☐同意建议 ☐其他（注明）

### 条 8 · D_INTEGRATION_GATEWAY/mcp_servers —— COVERS_UNFOUND
- **错配描述**：ssot_path `src/zephyr/integration/mcp/` 存在，但 covers 声称的 `KnowledgeBaseServer` 全仓 0 命中——该 server 疑退役/更名/未建。
- **涉册**：functional_domain_registry.yaml（D_INTEGRATION_GATEWAY/mcp_servers 条）。
- **证据**：report L129、L426；本会话复测 `grep -rlw` = 0 命中。
- **建议处置**：**改册+Owner 裁**——核实该 server 是否退役/更名：退役则删声称、更名则改 covers 符号名、未建则转 backlog。
- Owner 勾选：☐同意建议 ☐其他（注明）

## 汇总

- **建议分布**：改册 8/8（其中含"退役=注册表净删 high 门位"子选项 3 条：条 1/2/4/5 视裁定方向）；**改生成器 0 条**（report §2 三件改器=AI 余量另线，工卡已注明"涉 ROOR 族走总筹"）；**判可接受漂移 0 条**（8 条均为"说它管、它不在"级账实脱钩，无漂移容忍空间）。
- **先决依赖**：CR-008/CR-007c 尺未落 HEAD——8 条的现状机检依赖 `check_registry_consistency.py` 扩件落地（report §2，AI 余量线）；落地前以上手工复算命令为准。
- **边界声明**：本清单只读域册与报告，零册面改动；A 类 2 条（#7/#10）不列入；收编施工=Owner 逐条勾选后另批。
