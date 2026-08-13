---
title: 施工进度总跟踪表（并发施工队分配/进度/反馈/核验）
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
| 16 | 33 号 BudgetChangeHandler 施工（含文档重建核实） | ✅ 完工（AI-BGT-001，2026-08-14，commits 1e78d0d2/1b8a774a + tracker 同步，worktree 待 merge） |
| 17 | 待分配 | ⏳ 等裁定 |
| 18 | 待分配 | ⏳ 等裁定 |

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

## 五、施工批次规划（当前）

| 批次 | 内容 | 状态 |
|---|---|---|
| 第 1 批·业务+建库+定稿 | 8 个施工队 | ✅ 全部完工 merge |
| 第 2 批·业务+建库 | 7 个施工队 | ✅ 全部完工 merge |
| 第 3 批 | 3 个会话已分配（33 BudgetChange 等） | ⏳ 等用户裁定开工；须用 SOP v1.3.0 的 14 节长清单 |
| 后续批次 | 37 流动性 / 34 RegimeMeta / 60 跨切 / 43 合规 / 53 模拟实盘 / 54 对账 / 55 监控 | ⏳ 未分配 |

## 六、遗留项登记表（重建版，按优先级分类）

> 原表经 15（第一批末）→19（交接时）→28（第二批末）三轮演变，原文件丢失。
> 本版从各会话记忆重建 + 逐项实证核对当前状态（2026-08-13 晚）。✅=已闭环 / 🔥=阻塞已解除现在即可处理 / ⏳=待处理 / 🧊=远期。

### P0 · 阻塞已解除，现在即可闭环（原 bm-fill/runner 占用类）

| # | 遗留项 | 来源 | 实证状态（2026-08-13 晚） | 状态 |
|---|---|---|---|---|
| 1 | #ARCH-DATA-002 fix_phase 回填"设计已定稿，见 17 号 v1.0.0 §5.8" | AI-STD-001 | 已实证 fix_phase 仍为"待规划（设计阶段）…"旧文本，未回填 | 🔥 可处理 |
| 2 | 00_index §0 目录 17 号仍标 draft v0.1.0（L42/L645），实际已 active v1.0.0 | AI-STD-001 | 已实证 L42/L645 滞后 | 🔥 可处理 |
| 3 | #ARCH-BREG-001 fix_phase 更新：factor/strategy/risk_limit Step4-8、indicator、chart_pattern、field_dictionary、experiment 均已完成，文本仍写"待施工/待做" | AI-REG-COMP/FLD | 已实证 fix_phase 文本滞后（last_updated 2026-08-13 但内容未含批一/批二完工态） | 🔥 可处理 |
| 4 | 17 号文档路径引用/BOM/换行符补检（merge 后由统筹执行） | AI-STD-001 | merge 已完成，可执行补检 | 🔥 可处理 |
| 5 | AGENTS.md 业务资产速查更新（17 号定稿 + 12 注册表建成后） | AI-STD-001 | ✅ 已闭环（2026-08-13，commit f15de056，Owner 批准 [ARCH-APPROVAL] 落地，12 注册表速查全量更新） | ✅ |

### P1 · 治理登记缺口/一致性问题

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 6 | depgraph build_status 滞后：MOD-POS-020 节点状态异常 | AI-POS-001 | 模块已 production 落码，depgraph 未同步 | ⏳ |
| 7 | depgraph MOD-POS-021 状态仍 design 滞后 | AI-FRA-001 | 同上 | ⏳ |
| 8 | capability_canonical_file_registry 未登记 MOD-POS-021（违反硬约束） | AI-FRA-001 | 需补登记 | ⏳ |
| 9 | AGENTS.md 显化修改被 PROTECTED-PATHS 门禁阻断，需 Owner 审批 | AI-REG-FLD-001 / EXP-001 | 两队同遇；走 Owner 审批流程。**2026-08-13 进展**：12 注册表速查改动已获 Owner 批准落地（f15de056）；后续新增显化修改仍需逐个审批 | 🔄 部分闭环 |
| 10 | dangling FK：UNI-BASKET-001（regime 验证 10 大盘股篮子未登记 universe_registry） | AI-REG-EXP-001 | 需补登 universe_registry 或修正引用 | ⏳ |
| 11 | 16 号文档 8 大类指标 vs 代码实际 5 大类（trend/momentum/volatility/volume/reversal）不一致 | AI-REG-IND-001 | 文档需对齐代码现实 | ⏳ |
| 12 | data_asset 注册表 13 个 E5 告警（旧 dataflow 注册表锚点漂移） | AI-REG-EXE-001 | 锚点漂移治理 | ⏳ |
| 13 | field_dictionary source_system 3 个值 pending（当时 data_asset_registry 未就绪；现已建成） | AI-REG-FLD-001 | 重跑 E4 FK 检查复核 | 🔥 可复核 |
| 14 | 52 号 §7 DSR 双实现未统编（阈值 0.5 vs 0.95），影响 dsr_value 字段语义 | AI-REG-EXP-001 | 需裁定统一阈值 | ⏳ 等裁定 |
| 15 | BUY 队 5 个新文件 token 与既有 capability 名称重叠 | AI-BUY-001 | 命名冲突需消解 | ⏳ |
| 16 | MOD-PLAN-001/002/003 域不一致 | AI-BUY-001 | depgraph 域归属修正 | ⏳ |
| 17 | 33 号文档骨架化，直接影响第三批 33 BudgetChange 施工 | AI-FRA-001 | 第三批开工前需先充实 33 号文档 | ✅ 已闭环（AI-BGT-001：文档核实已重建+行号漂移修正+代码 3 瑕疵修复+33 条测试补齐，commit 1e78d0d2/1b8a774a） |

### P1-补 · 第二统筹会话补登（2026-08-13）

> 重建版漏登 5 项，由第二统筹会话对照原反馈记录补登。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 29 | AI-BUY-001 新建 6 模块（MOD-PA-006/TRIG-001/PLAN-001~003）未创建 blueprint.md | AI-BUY-001 | SOP Step 4 要点 1 必做项（新建模块按 blueprint_construction_template.md 建蓝图），施工时遗漏；用户 2026-08-13 裁定"登记遗留项 merge 后统一补"。merge 已完成，条件解除 | 🔥 可处理（建议与 #15 token 重叠消解 + #16 域不一致统一同批处理） |
| 30 | T+1 可卖持仓口径（current_holdings 应为 T+1 口径可卖权重） | AI-FRA-001 | 供数方需按 T+1 口径供数，供数口径对齐后关闭 | ⏳ |
| 31 | 62 号 E1 文案瑕疵（写"14 字段"实为 15 字段含 name_zh） | AI-REG-FLD-001 | 文档文案滞后，62 号负责会话顺手修正 | ⏳ |
| 32 | chart_pattern used_by_factors 回填 | AI-REG-PAT-001 | factor_registry 尚未施工形态因子，形态因子施工后回填 | ⏳ |
| 33 | 62 号 §12 P2-9 状态同步未做 | AI-REG-EXP-001 | 避免热文档冲突，留 62 号负责会话同步 | ⏳ |
| 34 | 幽灵锚点 9 个存量硬阻断（BM-INV-002） | AI-BGT-001 | align_all 硬阻断；2026-08-13 16:04 主工作区报告已存在同样 9 个，非本批引入；涉及 battle_map 治理，超本队范围 | ⏳ 待统筹处理 |
| 35 | 37 份蓝图 §11 代码索引漂移（sync_blueprint_code_index --check 实测） | AI-BGT-001 | 含 MOD-POS-022 §11.1 仍标"❌ 未实现"（depgraph 已流转 generated/production）；生成器为全局运行，单队修会搭便车其余 36 份，建议统筹统一跑 | ⏳ 待统筹处理 |
| 36 | 30 号文档表述漂移（"47 单测全绿"/"481 行"/不存在方法名 _check_tier2_convergence_or_escalate） | AI-BGT-001 | 33 号 §7-6 越界登记；33 号测试已补 33 条，30 号表述需其负责会话修正 | ⏳ 越界待处理 |
| 37 | 00_index §0/§7.3 对 33 号等重建文档版本登记滞后 | AI-BGT-001 | 33 号已 v1.1.0；00_index 为 bm-fill 占用文件，本队不碰 | ⏳ 越界待处理 |

### P2 · 测试/代码健康（存量问题，非施工引入）

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 18 | test_position_state_machine.py 2 个既有时间炸弹失败 | AI-POS-001 | 存量测试债，与 31 号施工无关 | ⏳ |
| 19 | var_calculator.py annualization_factor 配置未消费 + docstring 转义畸变 | AI-VAR-001 | 代码健康项 | ⏳ |

### 流程/环境类

| # | 遗留项 | 说明 | 状态 |
|---|---|---|---|
| 20 | 6/7 批二反馈仍用旧版 12 节长清单 | 第三批起统一用 SOP v1.3.0 的 14 节版 | ⏳ 第三批执行 |
| 21 | `ai/bm-fill/task-battlemap-coverage` 分支未 merge | 17 个 ai/* 分支中唯一未合入；需确认内容是否还需 | ⏳ 等裁定 |
| 22 | 17 个已 merge 的 ai/* 分支待删除 | git branch -d 清理 | 🔥 可处理 |
| 23 | scripts/session_worktree.py 此前从未被 git 跟踪（merge 清理中丢失的根因） | 已从 stash@{1} 恢复（sha256 与 asset index 一致 BBCACD36…），本次随交接文件一并 commit 落地 | 🔥 本次处理 |
| 24 | 交接文件防丢机制失效：原 tracker/handoff 仅靠 staged+.runtime 备份，未 commit | 本重建版直接 commit 到 dev；后续统筹会话每个里程碑必须经 GitCommitGateway 落地 tracker | 🔥 本次处理 |

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
| 2026-08-14 | 第三批 #16（33 号 BudgetChangeHandler）完工：#17 闭环；补登 #34-37（幽灵锚点存量/37 蓝图索引漂移/30 号表述/00_index 同步）；depgraph MOD-POS-022 流转 generated+production | AI-BGT-001 |
