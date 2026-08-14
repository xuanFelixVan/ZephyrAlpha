---
title: 施工进度总跟踪表（并发施工队分配/进度/反馈/核验）
doc_type: construction_tracker
date: 2026-08-12
rebuilt: 2026-08-13
ttl: task_bound
completes_when: "全部批次施工完工且遗留项清零后归档或删除"
---

# 施工进度总跟踪表

> **用途**：统筹会话记录并发施工队的分配/进度/反馈/核验，施工完毕后归档或删除。
> **创建**：2026-08-12
> **重建说明**：⚠️ 本文件于 2026-08-13 晚重建。原文件在施工统筹会话期间仅存于工作区/暂存区，**从未 commit**，会话关闭后丢失。本版基于 `.runtime/sessions/ai-sop-001/construction_progress_tracker_backup.md`（2026-08-13 17:33 快照）+ 各施工队/统筹会话记忆重建，个别遗留项的原始措辞可能与原版有出入，但事项内容已逐项实证核对。
> **关联 SOP**：[construction_workflow_sop.md](../01_policies_and_standards/sop/construction_workflow_sop.md) v1.4.0（2026-08-13 自 design_memos/02 迁入 01/sop 专区）

## 一、施工队总览

### 第一批（8 个，2026-08-13 18:43 全部完工 PASS，已全部 merge 回 dev）

| # | session_id | 任务 | 类型 | commit | 状态 |
|---|---|---|---|---|---|
| 1 | AI-DRWD-001 | 35 号回撤 Protocol（Kill Switch 链路 + detect_ghost_positions） | 业务施工 | — | ✅ 已 merge（81 测试 passed） |
| 2 | AI-POS-001 | 31 号仓位算法（MOD-POS-001/020/021 + §2.8 漂移再平衡） | 业务施工 | 3 笔单域拆分 | ✅ 已 merge（25 新测试 2 轮全绿） |
| 3 | AI-EXEC-001 | 40 号执行 broker（10 项 P0 gap + IS 4 桶 + 盘前检查链） | 业务施工 | — | ✅ 已 merge |
| 4 | AI-REG-COMP-001 | factor(111)/strategy(59)/risk_limit(42) 补 Step4-8 | 建库 | ac75684951 | ✅ 已 merge（E1-E20 errors=0） |
| 5 | AI-REG-IND-001 | technical_indicator_registry 新建（40 条目/58 输出列） | 建库 | eea122f432 + fd76ba4acb | ✅ 已 merge |
| 6 | AI-REG-EXE-001 | execution_algo(6) + data_asset(166) 新建 | 建库 | c7701fcde6 | ✅ 已 merge |
| 7 | AI-STD-001 | 17 号特殊交易日定稿（draft→active v1.0.0） | 定稿 | f81ea001 | ✅ 已 merge |
| 8 | AI-DSD-001 | 64 号数据源下载定稿 | 定稿 | — | ✅ 已 merge |

### 第二批（7 个，2026-08-13 20:46 全部完工 PASS，已全部 merge 回 dev）

| # | session_id | 任务 | 类型 | commit | 状态 |
|---|---|---|---|---|---|
| 9 | AI-VAR-001 | 36 号 VaR/ES 监控 | 业务施工 | 2 个 commit | ✅ 已 merge（零遗留） |
| 10 | AI-FRA-001 | 32 号 FirmRiskAggregator（修复 P0 字段名漂移） | 业务施工 | 8e4d60d5 | ✅ 已 merge（60 测试全绿） |
| 11 | AI-BUY-001 | 41 号买入流（修复 detect_breakout_failure 算法顺序缺陷） | 业务施工 | — | ✅ 已 merge（83 测试 2 轮全绿） |
| 12 | AI-REG-PAT-001 | chart_pattern_registry 新建（15 条目，8 大类形态） | 建库 | 206f4858 | ✅ 已 merge |
| 13 | AI-REG-FLD-001 | field_dictionary 新建（16 域 257 条目） | 建库 | — | ✅ 已 merge（6314 行，0 错/0 警） |
| 14 | AI-REG-EXP-001 | experiment_registry 新建（5 条可溯源实验记录） | 建库 | 4b92a41a | ✅ 已 merge（57 项检查 0 FAIL） |
| 15 | AI-REG-K4-001 | risk_limit 补登 var/es/kill_switch 三类（20 条） | 建库 | — | ✅ 已 merge（闭环第一批遗留#6） |

### 第三批（3 个会话，2026-08-13 20:46 由第二统筹会话分配，等用户裁定开工）

| # | 任务方向 | 状态 |
|---|---|---|
| 16 | 33 号 BudgetChange（AI-BGT-001，含 33 号文档重建核实+行号漂移修正 v1.1.0+MOD-POS-022 四瑕疵修复） | ✅ 已 merge（7ccc296d1e，2026-08-14 sess-batch-cleanup-0814；3 commits：1e78d0d20e/1b8a774ad5/15b1e40f8a，33 测试 2 轮全绿；wipe 事故后统筹重建 worktree 复跑 33 passed 确认） |
| 17 | 37 号流动性危机 Protocol（AI-LIQ-001，MOD-RK-21 六算法+54 测试+37号 v1.1.0） | ✅ 已 merge（885cddc3af，2026-08-14 sess-batch-cleanup-0814；4 commits：d53693a13e/16a089c812/db695f9d1c/3e39367c37，统筹独立复跑 54 passed；Step1/Step6 双 PASS，3 处文档缺陷修复落地 v1.1.0） |
| 18 | 42 号卖出流（AI-SELL-001，MVP 4 模块 MOD-SELL-000/004/005/019） | ✅ 完工已 merge（分支 87764ffb29 经 a337e0f54c 回 dev；depgraph 重建后 4 节点 stable+production 实证；sell_decision 227 测试全绿；42 号 v1.7.1） |

## 二、统筹会话与 merge 记录

| 项 | 内容 |
|---|---|
| 第一统筹会话 | AI-SOP-001（SOP 总统筹）：产出 construction_workflow_sop.md v1.0.0→v1.3.0（2026-08-13 迁 01/sop，现 v1.4.0），commits 6c99667d / 9e0c5141 等 |
| 第二统筹会话 | 2026-08-13 19:16 接手（经交接包恢复上下文），核验第二批 7/7 PASS，登记遗留项 19→28，分配第三批 |
| merge 会话 | 2026-08-13 21:05 完成全部 17 个 worktree merge 回 dev；3 处冲突（strategy_book.py / capability_canonical_file_registry.yaml / registry_master_index.yaml / AGENTS.md+ROOR）按"双方有价值则合并"原则解决 |
| SOP 当前版本 | v1.4.0 已在 dev（2026-08-13 迁至 docs/01_policies_and_standards/sop/construction_workflow_sop.md） |

## 三、并发环境状态（2026-08-13 晚重建时实测）

| 活动 | 状态 | 说明 |
|---|---|---|
| ALGO_FLOW runner（PID 20796） | ✅ 已完工 | 58/58 批全部经 GitCommitGateway 落地 dev，20 个临时文件已清理 |
| bm-fill 会话 | ✅ 已结束 | dev 上仅剩 `ai/bm-fill/task-battlemap-coverage` 分支未 merge（17 个 ai/* 分支中唯一） |
| 主工作区 dev | ✅ 干净 | 仅剩运行时噪音（feature_flags.jsonl 等审计日志） |
| 17 个已 merge ai/* 分支 | ⚠️ 待清理 | merge 已完成，分支未删除 |

## 四、反馈记录区（摘要）

- [AI-STD-001] 2026-08-13：§5 治本方案 5 项裁定齐全（项4 符号一致性双向校验+项1 语义字段+项2 semantic_registry+项3 AST gate 采纳，项5 运行时抽样推迟），MVP=项4+项1；§6 讨论项 6.1→选项B / 6.2→MSCI空置 / 6.3→CSV+IMPORT / 6.5→ETF赎回日关闭 / 6.6-3→暂缓 / 6.6-5→本文档承载。核验 PASS。
- [AI-POS-001] 2026-08-13 17:45：任务目标全部落码，25 新测试 2 轮全绿，长清单 PASS。3 项遗留（见 §7）。
- [AI-DRWD-001] 2026-08-13 17:33：81 测试 passed/0 failed，长清单 PASS，无遗留。
- [AI-REG-COMP-001] 2026-08-13 17:47：三表审计 errors=0/warnings=0，code_path 空 212 条为 candidate 合法态。2 项遗留（见 §7）。
- [AI-REG-IND-001] 2026-08-13 17:38：40 条目 58 输出列。2 项遗留（见 §7）。
- [AI-REG-EXE-001] 2026-08-13 17:45：EXA-{DOMAIN}-{NNN} 6 条 + DATA-{DOMAIN}-{NNN} 166 条。1 项遗留（见 §7）。
- [AI-DSD-001] 2026-08-13 17:39：2 项费用裁定（暂不续费 iFind / 暂不开通 L2）已拍板。
- [AI-FRA-001] 2026-08-13 19:35：commit 8e4d60d5 实证存在，双审查 PASS，60 测试全绿。4 项遗留（见 §7）。
- [AI-REG-FLD-001] 2026-08-13 20:02：0 错/0 警/3 pending。2 项遗留（见 §7）。
- [AI-VAR-001]：零遗留（FHS/QbSD/Vol-Targeting 为远期项本期不落码）。
- [AI-REG-K4-001]：补登 20 条（var 5 / es 3 / kill_switch 12），E1-E20 0 ERROR，闭环第一批遗留#6。
- [AI-REG-EXP-001]：反馈正文截断未给 hash，统筹经 git log 实证 4b92a41a。4 项遗留（见 §7）。
- [AI-BUY-001] 2026-08-13 20:34：83 测试 2 轮全绿，12 节全 PASS。2 项遗留（见 §7）。
- [AI-BGT-001] 2026-08-14：第三批 1/3。3 commits（1e78d0d20e/1b8a774ad5/15b1e40f8a）统筹已核验。关键修正：33 号文档非骨架（2026-08-12 已由 6a4f539214 重建 active v1.0.0），阶段 A 实为重建质量核实——ALGO_FLOW 标记 commit e5a6632c71 致文档行号引用系统性漂移 +68，已逐处修正（v1.1.0）。33号 §7 新发现 4 项闭环（re-target 窗口硬编码/fail-closed 声明/错误码撞号/补 33 测试）。Step 1 PASS + Step 6 十四节 PASS（A.13 ⚠️ 存量阻断：9 幽灵锚点经实证为存量）。33 测试 2 轮全绿。worktree 保留待 merge。⚠️ merge 注意：①BGT worktree 内 tracker 副本有编辑，与 dev 重建版必冲突——以 dev 版为准（其 #34-37 已并入 dev 版 §六）；②worktree 内 2 份他域 blueprint frontmatter sync 派生物未提交，merge 时甄别。4 项遗留（见 §六 #34-37）。 |

## 五、施工批次规划（当前）

| 批次 | 内容 | 状态 |
|---|---|---|
| 第 1 批·业务+建库+定稿 | 8 个施工队 | ✅ 全部完工 merge |
| 第 2 批·业务+建库 | 7 个施工队 | ✅ 全部完工 merge |
| 第 3 批 | 33 BudgetChange / 37 流动性 / 42 卖出流 | ✅ 3/3 全部完工 merge |
| **治理插队批（2026-08-14 用户裁定）** | **AI-GIT-001：git/并发协作基础设施专项（65/66/67 号 + 裁定书 S1-S6：ops_guard 删除收敛/清理四证 SOP/网关锚定/观测层/task_board 重建）** | ✅ 已完工，worktree 保留待 merge（14 commits，详见 §六 #38-40/43/25 与完工反馈） |
| 第 4 批 | 34 RegimeMeta / 60 跨切（骨架需重建）/ 43 合规 | ⏳ 等治理批完工 |
| 第 5 批 | 53 模拟实盘 / 54 对账 / 55 监控 | ⏳ 等第 4 批 |
| 重建类 | 28 号情绪周期（可从 a3750b90d1 恢复 v1.2.0）/ 60 号骨架 | ⏳ 随批排期 |

## 六、遗留项登记表（重建版，按优先级分类）

> 原表经 15（第一批末）→19（交接时）→28（第二批末）三轮演变，原文件丢失。
> 本版从各会话记忆重建 + 逐项实证核对当前状态（2026-08-13 晚）。✅=已闭环 / 🔥=阻塞已解除现在即可处理 / ⏳=待处理 / 🧊=远期。

### P0 · 阻塞已解除，现在即可闭环（原 bm-fill/runner 占用类）

| # | 遗留项 | 来源 | 实证状态（2026-08-13 晚） | 状态 |
|---|---|---|---|---|
| 1 | #ARCH-DATA-002 fix_phase 回填"设计已定稿，见 17 号 v1.0.0 §5.8" | AI-STD-001 | ✅ 已闭环（fix_phase 已更新为"设计已定稿（17号 §5 治本方案裁定）"，last_updated 2026-08-13；重建 tracker 时误标滞后，本次复核实证已更新） | ✅ |
| 2 | 00_index §0 目录 17 号仍标 draft v0.1.0（L42/L645），实际已 active v1.0.0 | AI-STD-001 | ✅ 已闭环（L42 与 L645 均已实标 active v1.0.0；重建 tracker 时误标滞后，本次复核实证正确） | ✅ |
| 3 | #ARCH-BREG-001 fix_phase 更新：factor/strategy/risk_limit Step4-8、indicator、chart_pattern、field_dictionary、experiment 均已完成，文本仍写"待施工/待做" | AI-REG-COMP/FLD | ✅ 已闭环（fix_phase 已详述批一/批二全部 12 注册表完工态；重建 tracker 时误标滞后，本次复核实证已更新） | ✅ |
| 4 | 17 号文档路径引用/BOM/换行符补检（merge 后由统筹执行） | AI-STD-001 | ✅ 已闭环（补检全部 PASS：BOM 无/换行符统一 LF/frontmatter 完整/相对链接 0 断链） | ✅ |
| 5 | AGENTS.md 业务资产速查更新（17 号定稿 + 12 注册表建成后） | AI-STD-001 | ✅ 已闭环（2026-08-13，commit f15de056，Owner 批准 [ARCH-APPROVAL] 落地，12 注册表速查全量更新） | ✅ |

### P1 · 治理登记缺口/一致性问题

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 6 | depgraph build_status 滞后：MOD-POS-020 节点状态异常 | AI-POS-001 | 模块已 production 落码，depgraph 未同步 | ✅ 已闭环（2026-08-14 AI-SELL-001 实证：merge 后 #ARCH-70 同身份 UPDATE 通道自动转换，当前 stable+production） |
| 7 | depgraph MOD-POS-021 状态仍 design 滞后 | AI-FRA-001 | 同上 | ✅ 已闭环（2026-08-14 同 #6，stable+production 实证） |
| 8 | capability_canonical_file_registry 未登记 MOD-POS-021（违反硬约束） | AI-FRA-001 | 需补登记 | ⏳ |
| 9 | AGENTS.md 显化修改被 PROTECTED-PATHS 门禁阻断，需 Owner 审批 | AI-REG-FLD-001 / EXP-001 | 两队同遇；走 Owner 审批流程。**2026-08-13 进展**：12 注册表速查改动已获 Owner 批准落地（f15de056）；后续新增显化修改仍需逐个审批 | 🔄 部分闭环 |
| 10 | dangling FK：UNI-BASKET-001（regime 验证 10 大盘股篮子未登记 universe_registry） | AI-REG-EXP-001 | 需补登 universe_registry 或修正引用 | ⏳ |
| 11 | 16 号文档 8 大类指标 vs 代码实际 5 大类（trend/momentum/volatility/volume/reversal）不一致 | AI-REG-IND-001 | 文档需对齐代码现实 | ⏳ |
| 12 | data_asset 注册表 13 个 E5 告警（旧 dataflow 注册表锚点漂移） | AI-REG-EXE-001 | 锚点漂移治理 | ⏳ |
| 13 | field_dictionary source_system 3 个值 pending（当时 data_asset_registry 未就绪；现已建成） | AI-REG-FLD-001 | 重跑 E4 FK 检查复核 | ✅ 已闭环（2026-08-14 统筹复核：SRC-QMT-001/AKSHARE-001/INTERNAL-001 在 data_asset_registry L114/136/422 实证存在，pending 标注清零，commit f0ebfdd5） |
| 14 | 52 号 §7 DSR 双实现未统编（阈值 0.5 vs 0.95），影响 dsr_value 字段语义 | AI-REG-EXP-001 | 需裁定统一阈值 | ⏳ 等裁定 |
| 15 | BUY 队 5 个新文件 token 与既有 capability 名称重叠 | AI-BUY-001 | 命名冲突需消解 | ⏳ |
| 16 | MOD-PLAN-001/002/003 域不一致 | AI-BUY-001 | depgraph 域归属修正 | ⏳ |
| 17 | 33 号文档骨架化，直接影响第三批 33 BudgetChange 施工 | AI-FRA-001 | 第三批开工前需先充实 33 号文档 | ✅ 已闭环（实际 2026-08-12 批二回填 6a4f539214 已重建为 active v1.0.0；AI-BGT-001 核实重建质量并修行号漂移→v1.1.0） |

### P1-补 · 第二统筹会话补登（2026-08-13）

> 重建版漏登 5 项，由第二统筹会话对照原反馈记录补登。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 29 | AI-BUY-001 新建 6 模块（MOD-PA-006/TRIG-001/PLAN-001~003）未创建 blueprint.md | AI-BUY-001 | SOP Step 4 要点 1 必做项（新建模块按 blueprint_construction_template.md 建蓝图），施工时遗漏；用户 2026-08-13 裁定"登记遗留项 merge 后统一补"。merge 已完成，条件解除 | ✅ 已闭环（2026-08-14 统筹补建 5 蓝图 448-496 行，合规 72/72 全 PASS；blueprint_registry 153→158；creation_token 5 条已登记；commit f0ebfdd5） |
| 30 | T+1 可卖持仓口径（current_holdings 应为 T+1 口径可卖权重） | AI-FRA-001 | 供数方需按 T+1 口径供数，供数口径对齐后关闭 | ⏳ |
| 31 | 62 号 E1 文案瑕疵（写"14 字段"实为 15 字段含 name_zh） | AI-REG-FLD-001 | 文档文案滞后，62 号负责会话顺手修正 | ⏳ |
| 32 | chart_pattern used_by_factors 回填 | AI-REG-PAT-001 | factor_registry 尚未施工形态因子，形态因子施工后回填 | ⏳ |
| 33 | 62 号 §12 P2-9 状态同步未做 | AI-REG-EXP-001 | 避免热文档冲突，留 62 号负责会话同步 | ⏳ |

### P1-补2 · 第三批 AI-BGT-001 登记（2026-08-14）

> 来源：AI-BGT-001 反馈 §7。原登记在 BGT worktree tracker 副本（merge 时以 dev 版为准），由统筹并入本表。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 34 | 幽灵锚点 9 个存量硬阻断（BM-INV-002） | AI-BGT-001 | 经主工作区 2026-08-13 16:04 报告实证为存量，非施工引入；统筹走 battle_map 治理，非施工队范围 | ⏳ 统筹治理项 |
| 35 | 37 份蓝图 §11 代码索引漂移（含 MOD-POS-022 仍标"❌ 未实现"） | AI-BGT-001 | 统筹统一跑 sync_blueprint_code_index.py（单队跑会搭便车 36 份他域文件） | ⏳ 统筹统一执行 |
| 36 | 30 号表述漂移（"47 单测全绿"/"481 行"/不存在方法名） | AI-BGT-001 | 越界项，留 30 号负责会话 | ⏳ 30 号会话 |
| 37 | 00_index 对 33 号版本登记滞后（现已 v1.1.0） | AI-BGT-001 | 登记时 bm-fill 占用 00_index；现已释放，统筹可直接同步 | ✅ 已闭环（2026-08-14 统筹同步 00_index L57/L657 至 v1.1.0；v1.1.0 内容在 BGT worktree commit 1b8a774ad5，随第三批统一 merge 生效） |

### P0-事故 · 2026-08-14 worktree wipe 事故（AI-LIQ-001 裁定书）

> 裁定书全文已归档：docs/_working/audit/architecture-reviews/2026-08-14_ai-liq-001_worktree_wipe_incident_review.md
> 事故：01:42-01:47 三 worktree（BGT/LIQ/SELL）tracked 文件被物理清空；后发现 .worktrees 目录整体二次删除。分支 ref 完好，committed 工作零损失。四层根因：R1 删除原语零拦截 / R2 worktree 隔离是君子协定 / R3 删除无审计 / R4 清理无 SOP。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 38 | S1 删除能力收敛（ops_guard 全原语删除拦截+审计）+ S2 worktree 清理四证 SOP | AI-LIQ-001 裁定书 | R1/R2/R4 治本，P0 治理施工，建议独立会话承接 | ✅ 已闭环（2026-08-14 AI-GIT-001：S1 ops_guard 3e2bb5ed70——四类删除原语拦截+保护区 fail-closed+白名单+审计 jsonl，42 红队向量 100% 拦截；S2 四证 SOP 新建 + session_worktree merge/abort 接入 69558c6479，逃生通道 --force-skip-checks 落审计） |
| 39 | S4 网关 worktree 锚定缺陷（git_commit.py bootstrap 未插 src/ 致 REPO_ROOT 恒=主工作区） | AI-LIQ-001 裁定书 | P1；已修复 bug 在网关入口复发；过渡期 workaround=PYTHONPATH=<worktree>\src | ✅ 已闭环（2026-08-14 AI-GIT-001：67abc2ea bootstrap 改 cwd git rev-parse 解析+插 src/，a6453e58 paths.py ZEPHYR_WORKTREE_ROOT 感知+activate_env 注入；无 PYTHONPATH 复测 4/4 通过） |
| 40 | S3 观测层补齐（reconcile worker stdio 落盘日志 + commit 后 worktree 快照审计） | AI-LIQ-001 裁定书 | P1；本次 4 个 worker 死因不可考直接原因=零日志 | ✅ 已闭环（2026-08-14 AI-GIT-001：7383bcd1 worker stdio 落盘 .runtime/logs/reconcile_worker_<sha>.log，95f94195 spawn_python_hidden stdout/stderr_path（WMI 降级走 cmd 壳层重定向），b36507d8 网关 commit 后 status 快照 worktree_status_snapshots.jsonl；端到端实证日志+快照各 5 条） |
| 41 | AGENTS.md "179 条已声明能力"硬编码计数漂移（实际 341 条） | AI-LIQ-001 | 裁定：改动态表述（以 capability registry 实时查询为准），挂 #9 Owner 审批通道 | ⏳ 等 Owner 审批 |
| 42 | 37 号蓝图 §5 两项跨会话排期：①编排层接入 35 号 §3.13 调用方 ②IPO 数据源接入（数据层） | AI-LIQ-001 | 非 37 号施工范围，分配给 35 号调用方会话/数据层会话 | ⏳ 待分配 |
| 43 | SOP 文本章节号漂移（遗留项登记目标 §七 vs tracker 现状 §六） | AI-LIQ-001 裁定书 S6 | SOP 文本修正，下轮 SOP 维护时顺手 | ✅ 已闭环（2026-08-14 AI-GIT-001，71281b93：construction_workflow_sop.md L400/L415 §七→§六） |
| 44 | 00_index 37 号版本同步（v1.0.18→v1.1.0）+ MOD-RK-21 production 状态 | AI-LIQ-001 | 照 #37 先例：统筹同步 00_index，随 LIQ merge 生效 | ✅ 已闭环（2026-08-14 LIQ 已 merge，00_index L61/L636 同步 v1.1.0；顺手同步第一二批全部滞后版本：31→1.25.0/32→1.0.22/35→1.39.0/36→1.10.2/41→1.7.0/42→1.7.1） |
| 45 | AI-SELL-001 depgraph 流转遗留（4 节点 design 待 merge 后转换） | AI-SELL-001 | 42 号卖出流 4 模块已 merge（a337e0f54c 含 87764ffb29）；重建后 MOD-SELL-000/004/005/019 全部 stable+production、边升级 active 不断链（#ARCH-70 通道实证）；SOP Step 8 已改写"只登记不流转+merge 后自动转换"分流口径 | ✅ 已闭环（2026-08-14 实证） |
| 46 | MOD-SELL-014/017 不施工（MVP 决策）+ TradeLevelCircuitBreaker Phase 2 | AI-SELL-001 | 014/017 维持 spec 裁定；42 v1.7.1 补阶段 5b+触发条件勘正；CircuitBreaker 孤儿决策补登 CAND-SELL-001（trigger=G04 参数校准+连续小亏实盘证据）；battle_map_07 BM-SELL-04-C 文案分裂——派生文件不入 git，depgraph 014=planned 为真源，随下一次 battle_map 重生成自动订正 | ✅ 已闭环（2026-08-14，42 v1.7.1 + CAND-SELL-001） |
| 47 | worktree 环境断层（PYTHONPATH/.env.postgres/lookup_audit 三件套） | AI-SELL-001 | #ARCH-WORKTREE-ENV-001 落地：session_worktree create 自动备环境 + strip_session_worktree/audit 锚定/双机制检测治本（a2163c1b）；.gitignore 显式登记（5e61c9b7） | ✅ 已闭环（2026-08-14）；关联 #39 已全闭环（67abc2ea bootstrap 插 src + activate_env 注入 ZEPHYR_WORKTREE_ROOT） |
| 48 | G04 参数校准动作无负责方/无跟踪（42 号 §6/§7 三项触发条件共同依赖） | AI-SELL-001 审查发现 | 已挂 00_index G04 行跟踪（P1-6 同批）；校准本身依赖首批策略回测/实盘，非施工队范围 | ⏳ 统筹跟踪项 |
| 49 | 【新事故机制】GATE-ROOT-TEMP-SWEEP reconciler 扫走 worktree `.git` 指针文件 | AI-GIT-001 实证（2026-08-14 13:19-13:28） | S4 修复后 worker 首次正确锚定 worktree，root-sweep 动态白名单（=tracked 文件）不覆盖 worktree 的 `.git` 指针 FILE 与 `activate_env.ps1`，shutil.move 至 .runtime/tmp 致 worktree 瞬间 prunable、git 命令向上穿透锚定主仓。与 wipe 事故同族（R2 君子协定层）。**已修复**：65a2e8a6 sweeper 护栏（.git/activate_env.ps1 永不触碰），worktree 已 git worktree repair，activate_env.ps1 已恢复 | ✅ 已闭环（机制修复+实证验收）；wipe 事故凶手候选机制登记备查 |
| 50 | reconcile live-timeout 测试隔离缺陷 + 测试污染生产审计日志 | AI-GIT-001 实证 | test_reconcile_async.py 两测试（test_live_timeout_*）告警计数跨测试/跨运行泄漏（期望 1 实测 2-3 且逐次递增）；且 pytest 运行向生产 reconcile_execution_log 写入测试 SHA（live_heal_sha/live_timeout_sha）触发 RECONCILER-HEALTH 误报横幅。存量问题，非本次引入 | ⏳ 治理排期 |
| 51 | script_manifest.yaml `demos/demo_e2e_pipeline.py` 幽灵条目 | AI-GIT-001 发现 | 该文件在 dev 树未被 git 跟踪（仅主仓工作区 gitignored 残留），manifest regen 在 worktree 内扫描会反复移除该条目——已在 AI-GIT-001 提交中还原保持现状；归属 pipeline 域，由统筹裁定清理或补跟踪 | ⏳ 统筹裁定 |
| 52 | 存量幽灵锚点精确画像（#34 补充） | AI-GIT-001 实证 | #34 登记 9 个，实测 10 个：655-663 九个数字 node_id 形态（BM-EXE-02/04/05/06）+ 524 一个 blueprint 形态（MOD-DAT-fred_ingest，BM-RES-11-A）。S5 级联提示已落地（7a08eb74）防新增；存量清理仍走统筹 apply_battle_map.py --remove-anchor | ⏳ 统筹治理项（同 #34） |

### P2 · 测试/代码健康（存量问题，非施工引入）

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 18 | test_position_state_machine.py 2 个既有时间炸弹失败 | AI-POS-001 | 存量测试债，与 31 号施工无关 | ⏳ |
| 19 | var_calculator.py annualization_factor 配置未消费 + docstring 转义畸变 | AI-VAR-001 | 代码健康项 | ⏳ |

### 流程/环境类

| # | 遗留项 | 说明 | 状态 |
|---|---|---|---|
| 20 | 6/7 批二反馈仍用旧版 12 节长清单 | 第三批起统一用 SOP v1.3.0 的 14 节版 | ⏳ 第三批执行 |
| 21 | `ai/bm-fill/task-battlemap-coverage` 分支未 merge | 17 个 ai/* 分支中唯一未合入；需确认内容是否还需 | ✅ 已闭环（2026-08-14 sess-batch-cleanup-0814 仪式性 merge 273a229499：23 冲突 hunk 逐读全 B类迭代型，dev 已吸收全量且迭代至 v2.10.1，净零差异实证；分支已删） |
| 22 | 17 个已 merge 的 ai/* 分支待删除 | git branch -d 清理 | ✅ 已闭环（2026-08-14 统筹执行，16 个施工分支全部 git branch -d 安全删除；ai/bm-fill 分支按用户裁定留另一 AI 处理，见 #21） |
| 23 | scripts/session_worktree.py 此前从未被 git 跟踪（merge 清理中丢失的根因） | 已从 stash@{1} 恢复（sha256 与 asset index 一致 BBCACD36…），本次随交接文件一并 commit 落地 | 🔥 本次处理 |
| 24 | 交接文件防丢机制失效：原 tracker/handoff 仅靠 staged+.runtime 备份，未 commit | 本重建版直接 commit 到 dev；后续统筹会话每个里程碑必须经 GitCommitGateway 落地 tracker | 🔥 本次处理 |
| 25 | scripts/task_board.py 丢失（66 号队列 MVP 前置条件，曾 untracked WIP） | wipe/并发期间从磁盘消失且从未入 git，不可恢复；66 号施工时按 66 memo §2.4 #9 schema（.runtime/task_board.db SQLite WAL+CAS）重建 | ✅ 已闭环（2026-08-14 AI-GIT-001 按 66 memo §2.4 #9 schema 重建，0e5ed3b9：三态机/60min TTL/exit 2 DENIED/死信 metadata 承载/板根锚主仓跨 worktree 单板；17 测试全过含 8 线程 CAS 恰一胜；三登记齐） |
| 26 | ai/AI-BGT-001 + ai/AI-LIQ-001 分支已 merge（7ccc296d1e/885cddc3af）待删 | ✅ 已闭环（2026-08-14 sess-batch-cleanup-0814：重建者会话已死（session registry 无注册），worktree 内容实证为 CRLF 幻影+审计日志，worktree 已 remove、分支已 git branch -d） |
| 27 | integrity 基线漂移 4 文件 + merge 落盘路径 gap | ✅ ①②已修复落地（#ARCH-MERGE-PATH-GAP-001：guard parents 判定 + 网关 merge finalize）；③自愈 3/4，残 1 为 SELL 活跃 WIP 待其提交收敛 |

### ✅ 已闭环（备查）

| # | 遗留项 | 闭环方式 |
|---|---|---|
| 25 | 第一批#6：risk_limit 的 var/es/kill_switch 三类 0 条目 | AI-REG-K4-001 补登 20 条（var 5/es 3/kill_switch 12），E1-E20 0 ERROR |
| 26 | 31 号文档"70 测试"声明失实 | AI-POS-001 施工期内已修正 |
| 27 | 64 号 2 项费用裁定（iFind 续费 / L2 开通） | 已拍板：暂不续费 iFind（免费源已替代）、暂不开通 L2 |
| 28 | REG-IND 80 个 pending（inputs→field_dictionary forward-ref） | field_dictionary 已建成（257 条目），大部分应可解析；残余并入 #13 复核 |

## 七、变更记录

| 日期 | 变更 | 理由 |
|---|---|---|
| 2026-08-12 | 初建 | 6 个施工队并发，需跟踪表防止搞混 |
| 2026-08-13 | 新增 §七 遗留项登记表 | AI-STD-001 审查发现 4 项遗留 |
| 2026-08-13 18:43 | 第一批 8 队完工，遗留项 15 项 | 第一统筹会话 |
| 2026-08-13 20:46 | 第二批 7 队完工，遗留项 19→28，#6 闭环 | 第二统筹会话 |
| 2026-08-13 21:05 | 全部 17 个 worktree merge 回 dev | merge 会话 |
| 2026-08-13 晚 | **文件重建**（原文件未 commit 丢失）+ 遗留项按 P0/P1/P2 重分类 + 状态逐项实证 | 本会话 |
| 2026-08-13 晚 | SOP 迁家（02/67→01/sop 专区）+ 遗留 #5 闭环（AGENTS.md 速查，Owner 批准 f15de056）+ #9 部分闭环 | 本会话（sess-recovery-0813） |
| 2026-08-13 晚 | 补登 5 项遗漏遗留（#29-33），其中 #29 蓝图补建因 merge 完成转 🔥 可处理 | 第二统筹会话（用户裁定蓝图遗留登记） |
| 2026-08-14 | P0 八项统筹闭环（#1-5/#13/#22/#29，commit f0ebfdd5 等）；AI-BGT-001 核验 PASS（33 测试统筹独立复跑确认）；#17/#37 闭环；#34-37 并入 §六 | 第三统筹会话 |
| 2026-08-14 | AI-LIQ-001 核验 PASS（54 测试独立复跑）；wipe 事故处置：.worktrees 整体二次消失但三分支 ref 完好零损失，BGT/LIQ worktree 已从分支重建；裁定书归档 audit/architecture-reviews；#38-44 登记（S1/S2/S3/S4 治本待立项） | 第三统筹会话 |
| 2026-08-14 | 第三批 3/3 全部 merge（sess-batch-cleanup-0814 执行）；00_index 全量版本同步（31/32/35/36/37/41/42）；**用户裁定治理插队**：AI-GIT-001 git 基础设施专项优先于第 4/5 批，00_index §5 + 本表批次区已更新 | 第三统筹会话 |
| 2026-08-14 | 文档压缩批完工：18 篇 33.6k→23.2k 行，一文档一子代理×3 波自审全 PASS，62 号 19 段研究散文表格化修复 PURE-ASSERTION；⚠️ **reconciler 批 auto-commit accd0cbe36 误删本表+handoff**（疑 ttl:task_bound 触发 TTL 类 reconciler 自动清理，已字节级恢复重写并登记为事故 #49）；裁定书文件同步恢复 | 第三统筹会话 |
