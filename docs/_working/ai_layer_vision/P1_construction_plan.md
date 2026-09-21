---
ttl: task_bound
title: AI 层 P1 施工方案（收尾批版，裁定#392（D-12） 追认基线）
owner: ZephyrAlpha-Owner
session: st-taskcards-exec-20260921
date: 2026-09-21
status: plan_v2_d12_closeout
completes_when: 各批次全部落地并验收销账后随 ai_layer 车道归档转 archived
---

# AI 层 P1 施工方案 v2（收尾批）

> **与 v1 的关系**：v1 方案零产出（无实体），本版即首版。原任务书的"首催=L2"立论已失效——L2 被全流通车道抢建 8/9 项（84007a1d6a），裁定#392（D-12） 追认既成事实并授权"方案改收尾批+补 4 测试件"；本版按该授权重构，**L2 段降格为收尾批**，其余面按依赖序照编。
> 复审依据=同目录 P1_construction_review.md v2（问题分级 P0/P1/P2 与裁定清单以它为准）。

## 一、六要素

### 1.1 分批（按依赖序，五字段制见 §二）

| 批次 | 主题 | 状态 |
|------|------|------|
| 批次 0 | L2 收尾批（4 验收测试件+注册表卫生+生产核验） | **本班已交付**（见 §二批次 0 表后注） |
| 批次 1 | L2 登记补全批（capability card+depgraph 节点+canonical 幽灵条目+P1 小修） | 待开单 |
| 批次 2 | OBJ_M 模型线 C1-C8（Owner 点名第二催） | 待开单（C6 前置 Owner 批 OBJ_M-#1） |
| 批次 3 | OBJ_R 收尾 S3/S4/S5 | 待开单（S3 治理立案前置；S4 依赖统计窗；S5 依赖 Owner-4） |
| 批次 4 | 七段主线 L1→L4→L6→L3→L5→L7（README §4 依赖序） | 待各段开单，本文只挂锚不定细节 |
| 批次 5 | OBJ_T / OBJ_S 对象线 | 同上 |

### 1.2 车道

- 本方案施工归 **ai_layer 车道**（tc_07/tc_10 派生单）；批次 3 的 OBJ_R S3 涉治理层资产，路由改派 **gov 车道**联办（见路由）。
- 多会话窗口纪律照 parallel_session_coordination_policy.md：worktree 隔离默认、改前 claim、网关提交、`git log -1 --name-only` 核归属。

### 1.3 路由

- 施工批：Flash（复杂度低）/GLM（中）；红蓝对抗与 Owner 门位项按宪法 §5 走裁定登记。
- S3 阈值外置化：触及 gate 源码=治理层资产（OBJ_R-#5 治理立案在案）——**提案由 ai_layer 车道起草，施工归 gov 车道，批文归 Owner**。
- 每批开工前查 SessionRegistry 避让在飞车道（裁定#392 执行路由同款），tasks.yaml 互斥件错峰。

### 1.4 资源

- 每批一个执行班（单会话+按需子代理 2-3 并发，批间串行）；批次 2 体量最大（8 项含两新模块+三表+前端页），建议独占一个完整工作日窗。
- PG（depgraph 实例）只读+test_schema 临时面；生产 ai_intake schema 写操作仅限登记器幂等部署。

### 1.5 红线（逐条，违反即硬阻断）

**三禁碰（他车道在飞区+治理真源）**：
1. 禁碰 `docs/03_modules/**`（模块蓝图真源，MODIFY-GUARD 语义归治理层）。
2. 禁碰 TDM（trading decision map）与 `AGENTS.md`（宪法 L0；宪法修改另有门位）。
3. 禁碰他车道在飞域：甲线写域 `src/zephyr/data/**`、`src/zephyr/factor/technical_indicators/**`；st-refscan 的 15 个 staged index.md 在途件不得吸收（提交后必核归属）。

**五条永不触碰**：
1. 实盘凭证（API key/账户/下单通道）——只读凭据亦不得复制出 secrets.py 通道。
2. 付费动作（订阅/充值/升级/调用计费接口产生费用）。
3. 宪法权限语义（门位豁免/权限边界/OWNER 门位代签）。
4. 审计链（审计记录不可改写/删除/回填）。
5. 验收判据自改（DESIGN 验收标准是MODIFY-GUARD 真源，改判据先改设计稿再施工；测试断言不得为绿而改）。

**批次内红线**：governance/ 根禁新增 .py（ARCH-031，一律进子包）；事件层零定时器（禁 cron/Timer/sleep-loop，宪法 §9.3）；测试禁写生产路径（tmp_path/test_schema）；生熟分离——产线代码禁读 ai_intake.*；注册表热文件必 safe_write_text CAS+写后 YAML 解析验证。

### 1.6 回滚

- 代码批：每批一 merge 单元，回滚=revert 该批 commit（worktree 隔离，主区零驻留）。
- DDL 批：ai_intake schema 全部 IF NOT EXISTS 幂等件，回滚=DROP SCHEMA CASCADE（生产 schema 回滚须 Owner 门位——涉注册表净删级）。
- 注册表批：safe_write_text 的 CAS 写前留 hash，回滚=按 hash 还原字节；登记器插入条目回滚=摘除该条目（锚定纯插入的可逆面）。
- 测试批：tests/ 独立无生产耦合，回滚=删文件零副作用。

## 二、分批明细（每批五字段：施工项/涉及文件/依赖/验收标准/预估规模）

### 批次 0：L2 收尾批 —— 本班已交付（2026-09-21）

| 施工项 | 涉及文件 | 依赖 | 验收标准（DESIGN §四 项 9 原文："全绿；零生产路径写入；进回归批"） | 规模 |
|--------|---------|------|----------------------------------------------------------------|------|
| 补 4 验收测试件 | tests/ai_layer/intake/test_gate.py / test_card_store.py / test_events.py / test_kpi.py（新建，tests/ 豁免 CREATE-GUARD） | 84007a1d6a 成品 | test_gate 16 / test_card_store 12 / test_events 14 / test_kpi 12，目录合跑 66 passed；PG 不可达=skip 而非假绿；写面=test_schema+tmp_path 零生产路径 | 4 件约 1100 行 |
| 注册表卫生（D-7+幽灵条目） | capability_canonical_file_registry.yaml（L33174 加 merge_evaluation 注记+两份交付 .md token 登记）；module_translation_registry.yaml（L55581 幽灵行 CAS 摘除留注记） | 裁定#392（D-7）/D-12 | 账实一致（路径全存在）；safe_write_text CAS+写后 `yaml.safe_load` 验证零错 | 2 热文件两处点名修改 |
| 生产核验 | scripts/ai_layer/apply_ai_intake_ddl.py --verify | — | `VERIFY ai_intake: OK`（已实测） | 零代码 |

批次 0 复审结论与证据：P1_construction_review.md §三（L2 8.5/9 逐项核验表）。**批次 0 无剩余施工**，登记半项缺口移交批次 1。

### 批次 1：L2 登记补全批（Small，纯登记+微修）

| 施工项 | 涉及文件 | 依赖 | 验收标准 | 规模 |
|--------|---------|------|---------|------|
| capability card 补登 | data/capability_cards/（intake 族卡，渐进披露 L0-L3） | 批次 0 | 复审 P1-b 销账；capability_lookup.find 可反查命中 | 1 卡 |
| depgraph 设计节点补登记 | apply_depgraph.py --add-design-node（DB） | 批次 0 | 复审 P1-c 销账；generate_project_depgraph 全图无 orphan 节点 | 登记操作 |
| canonical 册幽灵条目处置 | capability_canonical_file_registry.yaml L35828（intake/events.py） | 批次 0 同款 CAS 通道 | 复审 P1-d 销账；路径账实一致 | 1 行摘除留注记 |
| README 标题计数刷新 | docs/_working/ai_layer_vision/README.md §3.5 标题（"6 项"→"5 项"） | — | 复审 P2-a 销账；正文与标题一致 | 1 行 |
| （可选）handle_alert schema 注入口 | src/zephyr/ai_layer/intake/kpi.py | Owner 对复审裁定清单#7 点头 | P2-e 销账；测试补 demote 动作路断言（test_schema 注入） | ~5 行+测试 |

### 批次 2：OBJ_M 模型线 C1-C8（Owner 点名第二催；Large）

依赖链（OBJ_M DESIGN §施工项表原文）："C1→C2→C3→C4（M1/M2 前后件）；C5/C6 依赖 C3；C7 依赖 C3；C8 可与 C2 并行"。

| 施工项 | 涉及文件 | 依赖 | 验收标准（引 DESIGN 原文） | 规模 |
|--------|---------|------|--------------------------|------|
| C1 M1 源注册表 | config/model_intel_sources.yaml（新增，带治理锚定头） | 无 | "12 源全登记（URL/频率/配额/四闸字段）；智谱价页补核完成；试跑 3 源产出真情报卡 ≥10 张" | S |
| C2 M1 扫描器 | src/zephyr/intelligence/model_intel/（scanner.py+intel_card.py，新增模块） | C1 | "事件触发+周历窗口（无 cron/Timer）；simhash 查重；情报卡 100% 过四闸字段校验；新模块登记 add_module_translation+creation_token" | M |
| C3 M2 模型库三表 | DatabaseService 迁移：model_registry / model_price_history / model_promo_history | C2 | "全部经 DatabaseService（禁裸 duckdb）；时间字段显式时区；生熟分离（未过闸情报不入 registry）" | M |
| C4 M2 打分口径 | config/model_scoring_policy.yaml（新增，常数预注册） | C3 | "常数齐（P 权重/αβ/档界）；Owner 确认一次；重算幂等（同输入同分）" | S |
| C5 M3 双跑执行器 | src/zephyr/intelligence/model_profiling/dual_run.py + config/dual_run_criteria.yaml（新增） | C3 | "五层×20 件抽样可复现（固定 seed）；判据冻结校验（改判据=拒绝+强制新 experiment_id）；产出 L4 格式证据包" | M |
| C6 M4 路由表增轨 | config/model_routing_policy.yaml（修改：AI 层轨 8 条+free_window_pref 字段） | C3；**前置=OBJ_M-#1 Owner 终批（README §3.5 真待 Owner 表）** | "既有 12 轨零改动；新轨逐条带 evidence_ref；router 加载不报错+既有测试全绿" | S |
| C7 M5 预算分析器 | src/zephyr/intelligence/budget_analyzer.py + /api/budget-advisories + web/pages/budget.html + features/budget/budget.js（新增） | C3 | "日报告=usage_records 口径；burn-rate 两窗（7d/30d）有测试；四档阈值告警有测试；免费节省单列；页面无支付按钮（验收硬查）" | M-L |
| C8 排班登记 | resource_profile_registry 生成器三源增补后 --force 再生 | 可与 C2 并行 | "三实体入库；生成器幂等；考试窗口与 mine_vs_exam 冲突闸绿；零手工改表" | S |

批次红线加则：C6 触碰既有路由表=产线路由面，Owner 终批前零改动（只出 diff 提案）；C7 页面无支付按钮=五永不触碰第 2 条（付费动作）的验收落点。

### 批次 3：OBJ_R 收尾 S3/S4/S5（Medium，跨车道）

| 施工项 | 涉及文件 | 依赖 | 验收标准（引 OBJ_R DESIGN §S 表原文） | 规模 | 路由 |
|--------|---------|------|--------------------------------------|------|------|
| S3 阈值外置化提案 | 提案文档+gate 硬编码常量→注册表条目清单（对标 AI-THD-001 统读） | 治理立案（OBJ_R-#5 在案）；触及 gate 源码=治理层资产 | "commit gate 硬编码常量→注册表条目清单"；"改 gate 源码=治理层资产，非本卡权限" | S（提案）/M（施工归 gov） | ai_layer 起草→gov 施工→Owner 批 |
| S4 月度体检任务 | 触发率/误拦率统计器+standards_proposal 生成器，挂 L1 内监慢周期 | **gate_execution_stats 积累 ≥1 窗**（DESIGN 原文前置） | 统计器+提案生成器有测试；顺带补 gen_intake_ref_snapshots 幂等重跑断言（复审 P2-d） | M | 待前置窗满，先出设计单 |
| S5 案例库起步 | casebook.md+首案补登确认 | **Owner-4**（OBJ_R-#4 首案已补登在案，残余=升格 catalogs 时机=OBJ_R-#6 治理立案） | 首案 CASE-2026-0917-001 在档即起步件，升格时机走攒案门槛 | S | 治理立案窗 |

### 批次 4/5：七段主线与对象线（本文只挂锚）

- 依赖序真源=README §4："L1 感知→L4 对比→L6 切换→L3 清洗→L5 排产→L7 传承"，各段 DESIGN.md=工程真源；每段开工另走 construction_workflow 15 步闭环开单（README §4 原文），本方案不预写细节（防与开单时 DESIGN 漂移打架）。
- 挂账提醒：L4-#3（intake_exam_due 契约对齐，跨稿契约=Owner 门位）与 L5-#3（任务书 schema provenance 增补）是 README §3.5 真待 Owner 表既有项，开单前催批。
- TC-10 互认：组合层立项（eng_quantcombine）与 L4/OBJ_M 重叠面，两边立项互认同源防双份考尺（tc_07 卡 §5 在案）——批次 2 C4/C5 开单时与 TC-10 立项方交换考尺锚点。

## 三、催批与 Owner 动作项汇总

1. 批次 2 开工批文（C1-C3/C8 可先行，C4 含"Owner 确认一次"，C6 前置 OBJ_M-#1 终批）。
2. 复审裁定清单#4/#7 两个执行级事项点头（canonical 幽灵条目处置已含在批次 1；#7 可选项默认不做）。
3. README §3.5 真待 Owner 5 项既有催批节奏不变（其中 OBJ_M-#1 与批次 2 直接相关）。
4. 密钥轮换（裁定#392 尾款）维持 Owner 动作项，AI 只核对不代生成。

## 四、本方案与既有真源的关系

- 净零申报：本方案替代"原任务书 P1 方案段"（v1 零产出无实体可废）；不新增规则/gate；两份交付物（本文件+P1_construction_review.md）创建 token 走 batch_creation_tokens 登记器（--merge-evaluation 一句话内收评估）。
- L2 段验收判据真源仍= L2_intake_library/DESIGN.md §四（MODIFY-GUARD 保护）；本方案只编排不定义判据。
- 交付物归档：批次 0-1 销账后本文件转 status: executing；全部批次清零后随 ai_layer 车道归档（completes_when）。

## 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-09-21 | v2 | 裁定#392（D-12） 授权重写：L2 段降格收尾批（批次 0 本班已交付）、OBJ_M 提为批次 2、OBJ_R S3-S5 批次 3、七段/对象线挂锚批次 4/5；六要素+红线三禁碰五永不触碰全齐 |
