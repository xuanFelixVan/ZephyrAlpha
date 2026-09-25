---
ttl: task_bound
session: st-ailayer-fullflow-frxc
date: 2026-09-25
---

# M8 补裁证据 · F122 管线路由 M4/M5 边界（双方证据并排，只列证据与选项，不裁）

> 挖矿会话 st-ailayer-fullflow-frxc ｜ 2026-09-25 ｜ 只读挖矿+本目录零 commit。
> 待裁命题：F122"管线路由 M1-M11"（config/blueprint_routing.yaml 30 路由 + src/zephyr/integration/pipeline_orchestrator.py 三层编排）归 M4（AI 层/Agent 编排）还是 M5（调度常驻）——M0 待裁项 24 原文"待裁：M4（Agent 编排）或 M5（调度）边界"；总筹初步口径"M4M5 互引"（orchestration §四 M0 行）；S0 总册 F122 行维持 partial/待裁。
> **先决发现（命名冲突警示）**：pipeline_orchestrator 的"M1-M11"是 **AI 编码管线段**（A区 M1-M5 生产/B区 M6-M11 审计，pipeline_orchestrator.py:51-52 双管线架构），与本次挖矿战役的 M1-M8 车道**同名异义**——"M4/M5 边界"之争本身可能源于该冲突的误读（M0 X7 行把两套 M 编号并置）。

## 一、两件物盘点（实为正交两物，代码头注已自声明）
| 件 | 身份 | 域/蓝图 | 语义 |
|---|---|---|---|
| config/blueprint_routing.yaml | 蓝图触发路由表 SSoT（30 条 route，R001-R030，priority 1-100） | **D_INFRA_RUNTIME / MOD-INF-002**；Human-Gated（"路由映射变更=关键架构变更"，头注 :15） | 关键词/路径模式→**蓝图文献与人类检索**（含 blueprint_search MCP）——给"AI Agent 决定读哪份蓝图"用 |
| src/zephyr/integration/pipeline_orchestrator.py | M1-M11 编码管线协调器（production，TaskCard dispatch+TaskRepository 修桥 v0.3.2+三层模型策略 DeepSeek/GLM/Claude） | **D_INTEGRATION / MOD-INF-009** | **CT-PIPE 编排**：真源=TaskCard+ct_pipe_routing.resolve_ct_pipe_orc001，头注 AUDIT-08 明文"**不以 blueprint_routing.yaml 解析 Mx 节点**""blueprint_routing 属 MOD-INF-009 路由表，与 CT-PIPE 编排**正交**"（:19-24） |
| 唯一生产消费方 | src/zephyr/trading/auto_runtime_core.py:65,:1103——PipelineOrchestrator 挂入 TaskQueue dispatch handler（300s 轮询派发）；:1119 BlueprintWatcher 另挂 | 消费方=F71 AutoRuntime Core（M2 车道"系统大脑"，built） | **运行宿主既非 M4 也非 M5** |
| capability 卡 | data/capability_cards/pipeline_orchestrator.yaml（MOD-INF-035，capability_id=pipeline-orchestrator，category=orchestration，tags=[pipeline,orchestration,M1-M11]，requires_human=true） | 卡片域=orchestration | 能力册挂在 F91 能力反查族（M4 资产）名下 |

## 二、M4 方证据（归 AI 层/Agent 编排）
1. M0 总册 F90 行已把"M1-M11 管线编排"登记进 **F90 Agent 编排与 A2A**（"orchestrator+skills 60+/A2A/M1-M11 管线编排｜src/zephyr/orchestrator/、autonomy_core/、integration/mcp/"）——登记面先例在 M4 语汇。
2. pipeline_orchestrator DEPENDENCIES 深度 AI 栈：LSGSecurityGateway（宪法 §9.2 全 LLM 必经）、autonomy_core、a2a layer3_coordination、local_model_scheduler、embedding_router、reranker、LLMGateway 三层模型路由（:3-4）——全部是 M4 三册（03_lsg_defense 等）的看守资产。
3. 管线段本体是"AI 编码工序"（代码生成/校验/审查/合规），执行体=LLM Agent——语义上是 M4"AI 管 AI"域（F94/F95 设计面的施工态远亲）。
4. capability 卡（F91 族，M4 车道资产）已收 capability_id=pipeline-orchestrator——能力反查入口现成。

## 三、M5 方证据（归调度常驻）
1. blueprint_routing.yaml 域册=D_INFRA_RUNTIME+MOD-INF-002（基建运行时域）——**两件物中"路由表"那件的域册归属是基建而非 AI**。
2. 运行形态常驻：TaskQueue 300s 轮询+BlueprintWatcher 60s 轮询挂 AutoRuntimeCore——"常驻族登记/健康表/水位"是 M5 五册的治理词汇；M10 豁免注记（periodic_profile while+sleep）也是 M5 09 运维红线的豁免语义。
3. M5 车已收 X4 双引擎自动化总计划（Qoder 白班×GLM 夜班，F119）——"AI 会话编排调度"语义相邻；管线三层模型策略（哪家模型跑哪段）与夜班排班同构。

## 四、反方/第三方证据（对 M4、M5 双向削弱）
1. **两册均零认领**：m4_ai_layer/ 四册与 m5_scheduling/ 五册 grep "管线路由|pipeline_orchestrator|blueprint_routing" **零命中**——双方在挖矿波从未实际主张过该环节；"边界之争"是 M0 骨架期的纸面问题。
2. **AUDIT-08 真源边界已裁决过一次**（代码级）：blueprint_routing.yaml（文献路由）≠CT-PIPE 编排，正交——"一件事拆两半分给两车道"的前提不成立，它本来就是两件事。
3. **运行宿主是 F71**：唯一生产消费点在 auto_runtime_core（M2 收编的 built 环节）——按"谁消费谁认领"口径应归 F71 执行臂；按"谁供料谁认领"则两件物向 LLS 网关/蓝图文献各找各源。
4. 命名冲突未消解前，任何"M4/M5"字面归属都会持续制造误读（本证据册 §一 先决发现；总册 F122 行下游写"Agent 编排"亦是被 M1-M11 字面牵引的例子）。

## 五、裁定选项（并排陈列，本组不裁）
- **选项 A·归 M4（F90/F91 双挂）**：pipeline_orchestrator→F90 Agent 编排（管线段=AI 工序）；blueprint_routing.yaml→F91 能力反查族（蓝图文献路由与 capability_lookup/blueprint_search 同族）。M5 不挂；M2 以"消费方"记互引。
- **选项 B·归 F71 执行臂（M2 引用）**：管线编排器是 AutoRuntimeCore 的子件（dispatch handler 实证），按运行宿主归属 M2 车道登记、M4 记依赖（LSG/三层模型）；blueprint_routing.yaml 单独归 F91。最贴运行事实，但 M2 已收卷需补册。
- **选项 C·维持互引（总筹初步口径）+补登记**：维持"M4M5 互引"，但把 AUDIT-08 正交边界写进 F122 行与 M4/M5 册各一行（消"边界"伪命题），另登记命名消歧：文档层统一把编码管线段称"CT-Pipe M1-M11"，禁与挖矿车道 M1-M8 裸并置（修 M0 总册 F122/X7 行措辞即可，零代码改动）。
- 无论何选项：30 路由的 Human-Gated 属性（路由变更=架构变更）建议随裁登记 risk_tier（现为 high 域语义、无 tier 行）。

## 六、复核命令（10 分钟）
```bash
# 1. 路由 30 条复现（应 routes: 30）
python -c "import yaml;d=yaml.safe_load(open('config/blueprint_routing.yaml',encoding='utf-8'));print('routes:',len(d['routes']),'| module:',d['module_id'])"
# 2. AUDIT-08 正交自声明复现（应见'正交'与'不以 blueprint_routing.yaml'）
sed -n '19,24p' src/zephyr/integration/pipeline_orchestrator.py
# 3. 唯一生产消费方复现（应 auto_runtime_core 两处）
grep -rn "PipelineOrchestrator" src/zephyr/trading/auto_runtime_core.py | head -3
grep -rln "pipeline_orchestrator" src --include="*.py" | grep -v "integration/pipeline_orchestrator"
# 4. M4/M5 两册零认领复现（应无输出）
grep -rn "管线路由\|pipeline_orchestrator\|blueprint_routing" docs/_working/fullflow_mining/m4_ai_layer/ docs/_working/fullflow_mining/m5_scheduling/
# 5. 双域身份复现（应 D_INFRA_RUNTIME 与 D_INTEGRATION 各一）
grep -n "DOMAIN" config/blueprint_routing.yaml | head -1
grep -n "\[DOMAIN\]" src/zephyr/integration/pipeline_orchestrator.py | head -1
# 6. capability 卡复现（应 pipeline-orchestrator/ACTIVE/requires_human true）
grep -n "capability_id\|requires_human\|category" data/capability_cards/pipeline_orchestrator.yaml | head -4
```
