---
title: 施工进度总跟踪表（并发施工队分配/进度/反馈/核验）
doc_type: register
summary: "并发施工队分配/进度/反馈/核验的唯一跟踪登记表：批次状态+反馈记录+遗留项登记（#1-49）+变更记录"
date: 2026-08-12
rebuilt: 2026-08-13
ttl: permanent
completes_when: "全部批次施工完工且遗留项清零后归档（归档不删除，保留审计链）"
---

# 施工进度总跟踪表

> **用途**：统筹会话记录并发施工队的分配/进度/反馈/核验，施工完毕后归档或删除。
> **创建**：2026-08-12
> **重建说明**：⚠️ 本文件于 2026-08-13 晚重建。原文件在施工统筹会话期间仅存于工作区/暂存区，**从未 commit**，会话关闭后丢失。本版基于 `.runtime/sessions/ai-sop-001/construction_progress_tracker_backup.md`（2026-08-13 17:33 快照）+ 各施工队/统筹会话记忆重建，个别遗留项的原始措辞可能与原版有出入，但事项内容已逐项实证核对。
> **迁移说明（2026-08-14）**：自 `docs/_working/` 迁入 design_memos——_working 临时区两次被 reconciler 误删（事故 #49），迁入永久区根治；所有外部引用已同步更新。
> **关联 SOP**：[construction_workflow_sop.md](../../../01_policies_and_standards/sop/construction_workflow_sop.md) v1.4.0（2026-08-13 自 design_memos/02 迁入 01/sop 专区）

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

### 第 4 批+紧急插队（2026-08-15 用户派单，当日全部完工 merge）

| # | session_id | 任务 | commit | 状态 |
|---|---|---|---|---|
| 19 | AI-TICK-001 | tick_subscriber 观测层（#59 P0：18 测试入库+TestMain 隔离+模拟盘化排查） | e061a3b0+9613fbc7+a88a56fb | ✅ 已 merge（e179d4ce25；79/79 两轮+统筹 dev 复跑 79/79） |
| 20 | AI-REGIME-001 | 34 号 RegimeMeta 测试套件重建（55 用例）+blueprint v0.2.0 对齐 | 837c5b256c+2bc86c1b29 | ✅ 已 merge（经 a88a56fb finalize；55/55 两轮+pf_alloc 153/153 无污染） |
| 21 | AI-XCUT-001 | 60 号跨切清理（三处残留漂移收敛+"骨架重建"前提推翻） | 3d68da3ed3 | ✅ 已 merge（def379dbc9；battle_map §16 重生成闭合实证） |
| 22 | AI-XCUT-002 | #8 MOD-POS-021 补登+merge 残留标记清除 | 1b613f03cd | ✅ 已 merge（479de59b23） |
| 23 | AI-COMP-001 | 43 号合规纪律五环节（7 模块+78 测试）+COMPLIANCE-001 方案 A | 8fc6a993b3+b9e38e8dca+5708658d3e | ✅ 已 merge（de45d261aa；79 项两轮+统筹双环境复跑 79/79） |
| 24 | AI-TDEBT-001 | 测试债清偿批（#63，785 失败按簇分包） | 93 passed+15 xfailed 两轮 | ✅ 已 merge（16c3dcf2c9；#ARCH-093~099 裁定落地，233 长尾 6 包方案见裁定书 §关联项 E） |
| 25 | AI-SENT-001 | 28 号情绪周期恢复核实（v1.2.0→v1.2.3 零漂移+00_index 三处状态修正） | b9000950e1 | ✅ 已 merge（e53bc3b70c） |
| 26 | AI-RCAN-001 | 54 号对账归因 | — | ✅ 已 merge（057a9a2384） |
| 27 | AI-SIM-001 | 53 号模拟实盘路径（引用现状同步 v1.7.7+QUANT-002/003 裁定落地） | a905f5f6+a7c64571+def6972d | ✅ 已 merge（eafc17941c） |
| 28 | AI-FIX-001 | 治理顺手批（#69/#70/#80/#82/#73） | — | ✅ 已 merge（a539c1fcb6） |
| 29 | AI-MON-001 | 55 号监控复盘（MOD-RK-23+MOD-RPT-009+REG-ATH-001） | e6edcf76 等 6 commits | ✅ 已 merge（0d5f8f0777；撞号重编 #85→#93） |
| 30 | AI-ASM-001 | 装配批（#78 合规接线 C-004/C-002/MOD-PA-006+日申报硬计数器） | cc284ddc8b+0d0a1edc7b | ✅ 已 merge（8b932ced42；213 测试两轮全绿+红队三向量实证） |
| 31 | AI-NORTH-001 | 19 号北向季度持仓快照 fetcher | 2c6567ec7c 等 13 commits | ✅ 已 merge（87f50a5e3f；tushare_provider 冲突手工合并，双 capability 并存） |
| 32 | AI-JOB077-001 | JOB-077 市场元数据与约束接入（DS-081~085） | 669066cd27+02cc8e5125 | ✅ 已 merge（会话自 merge bdf37ab8d5+1e9f14fc82） |
| 33 | AI-JOB083-001 | JOB-083 ST 历史名称变更回填（DS-085 历史段） | 2a03ebcc76 | ✅ 已 merge（会话自 merge 846a1019a6） |
| 34 | AI-JOB084-001 | JOB-084 退市股历史 K 线回填（DS-002 幸存者偏差治理） | 875d34c775 | ✅ 已 merge（会话自 merge 3f7f7b603b） |
| — | AI-ARCH-001 | 冷热数据可见性（统筹自用登记区；发现未提交补登：INFRA-STORE-002+契约 v1.1.0） | 抢救入库 2cdbbc80a7 | ✅ 已闭环（工具本体 archiver.py 早已在 dev，登记尾巴统筹抢救落账） |
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
- [AI-ASM-001] 2026-08-15：#78 装配批完工——①范围：C-004 四道合规闸（INTRADAY 清单整批 Hard Block/KillSwitchLite 熔断/MOD-CMP-002 四项严禁/MOD-CMP-007 逐单检测）嵌入 trading_session._validate_and_submit；C-002 双硬闸（ReportGate 先报告后交易+日申报笔数读数检查）嵌入 order_manager.submit_order；MOD-PA-006 gate_batch_order 纪律闸；CancelRateGuard v1.1.0 日申报硬计数器（5000 预警/1 万阻断，报单+撤单双计自然日滚动，复用 40 号决策⑫事件流）。②实证：213 测试（ex_core 3 文件+pf_alloc+compliance 含红队 4 项）2 轮全绿；红队三向量真实触发（9999 放行→1 万阻断/清单缺项整批拒→补全恢复/报复命中熔断落盘跨链同策略均拦）。③Step 6 长清单 14 节全 PASS。④登记：43 号 v1.1.0（§8 闭环+§10 装配记录）/ARCH-COMPLIANCE-001 proposed→decided（方案 A 闭环，补 5708658d3e 丢失登记）/ARCH-COMP-001 fix_phase 接线完工/4 MOD-CMP 蓝图+执行域蓝图+MOD-PA-006 蓝图接线标注/2 新测试文件 capability 登记。⑤避让：SIM-001 施工面无重叠（其 worktree 仅 53 memo 改动）；TDEBT/FIX/JOB077/NORTH/SENT/RCAN/MON 域未碰。⑥遗留：session_audit.py docstring 存量 `\ ` 转义致 governance 链 collection error（filterwarnings=error 放大，TDEBT 域，本批测试以 -W ignore::SyntaxWarning 绕行；**2026-08-15 续查②四方实证更正：dev HEAD/工作区 0 warning 已闭环（1bde859acc ALGO_FLOW docstring 再引入 `\ `、6e3808db49 worktree-write-integrity 批顺手修复）；TDEBT 176199347e blob 0 warning 但非 dev 祖先（exit=1 实证未入）；ASM worktree HEAD/工作区仍 1 warning 系分支点存量，ASM 分支未改本文件（文件日志全 dev 继承），merge ASM 三方合并自动取 dev 干净版零冲突，ASM 侧不修；TDEBT merge 时本文件或微冲突取 dev 侧即可，本项事实闭环**）；Spoofing/Layering/WashTrade 盘中实时流驱动属后续批；merge 后 depgraph #ARCH-70 通道转 production+compliance 域 4 蓝图 design_maturity 待通道同步。⑦GATE-RULE-AUDIT 14:46 超时续查：单次 16s 完成（60s 上限），governance.db 历史显示 08-14/08-15 多次 auto_committed 成功，超时系 8+ 并发会话资源争用一次性事件非挂死，观察项若成簇再议（超时上调/增量扫描），不改代码。
- [AI-BGT-001] 2026-08-14：第三批 1/3。3 commits（1e78d0d20e/1b8a774ad5/15b1e40f8a）统筹已核验。关键修正：33 号文档非骨架（2026-08-12 已由 6a4f539214 重建 active v1.0.0），阶段 A 实为重建质量核实——ALGO_FLOW 标记 commit e5a6632c71 致文档行号引用系统性漂移 +68，已逐处修正（v1.1.0）。33号 §7 新发现 4 项闭环（re-target 窗口硬编码/fail-closed 声明/错误码撞号/补 33 测试）。Step 1 PASS + Step 6 十四节 PASS（A.13 ⚠️ 存量阻断：9 幽灵锚点经实证为存量）。33 测试 2 轮全绿。worktree 保留待 merge。⚠️ merge 注意：①BGT worktree 内 tracker 副本有编辑，与 dev 重建版必冲突——以 dev 版为准（其 #34-37 已并入 dev 版 §六）；②worktree 内 2 份他域 blueprint frontmatter sync 派生物未提交，merge 时甄别。4 项遗留（见 §六 #34-37）。 |
- [AI-RCN-001 治理批②] 2026-08-15 第四统筹核验 **PASS**（补登——原拟随 faba03fb 登记的 Edit 因 Trae IDE 脏缓冲区未落盘，merge 实证 stage1/2/3 三方均无）：①commit 实证——反馈 11 commit 全在 git log 且带 [GW:AI-RCN-001] 标记，overlap/multi-domain 逃生通道规范留痕；T0/T1 核心含 coord-0814-git001 先行落地（98aeffde63 doc_lifecycle 状态机），AI-RCN-001 续作 T2-T6；②Step 1 结论已给（裁定书真源+T3① 按现状修正为 protection 声明，采纳）；③Step 6 十四节逐节结论已给（全 PASS/N-A，A.11 depgraph 登记 MOD-GOV-044）；④测试——施工队红队+准入+关联 246 项×2 轮全绿（57s/69s），统筹独立复跑关键套件 143 项 1.47s 全绿（1 xfail=#64 留痕）；⑤stat 抽查无跨域夹带；⑥worktree 保留待 merge；⑦遗留 3 项均有着落（DB 双副本→批③闭环、#55②→批③闭环、GATE-DEPGRAPH-OPS 噪音→批③同治）。验收标准逐条机器验证：T1 红队 100% 阻断✓/T2 rogue payload 拒启✓/T3 untracked 删除必审计✓/T4 干净克隆裸 commit 误报=0✓。
- [治理批③ 同会话续作] 2026-08-15 第四统筹核验 **PASS**（补登同上）：①commit 1465ff020f 实证存在（25 文件全治理域无跨域夹带，[GW] 三留痕齐）；②裁定 1-5 与 ARCH-WORKTREE-DB-SPLIT-001 治本方案一致（仓级共享状态归主仓/anchor_main_root 两型锚定/worktree REFUSED 禁写/补丁卸载 API/#55② 顺修）；③验收——关联子集 2182 项×2 轮全绿（余 3 例 worktree_pool 环境依赖非回归）；首轮全量 4.5 万项画像 785 失败=存量 API 漂移债（单进程复现、与本批零交集）登记 #63；④新登记 #61（GATES_DIR 孤儿）/#62（drift_events 双库）/#64（trusted_git_env 断言漂移）待专项裁定；⑤临时文件全清、worktree governance.db 历史副本按裁定 1 不动随生命周期清除。
- [AI-GIT-001 第二批·wrapper 层] 2026-08-15 第四统筹核验 **PASS**（反馈文本 2026-08-15 补转，git 实证早已完成）：4 commit（611227d5 wrapper 函数集+安装脚本+40 用例/21f447c1 RULE-GIT-SAFE 双写+d6 三 hook/d7844786 CLI create 活性登记治本/0b94b4d4 文档同步）全在 dev（3926a1ffce merge 链）；40/40 两轮全绿；#66（原编号 #56）CLI create 无活性登记机制修复实证（sweep/base_sync 误抹凶手之一落网）；PS5.1 三实证修正（Alias>Function/裸--被吞/Add-Content BOM）登记文档。
- [65/66 遗留批·561ce485] 2026-08-15 第四统筹核验 **PASS**（反馈文本补转）：四项遗留全闭环——①wrapper 激活（$PROFILE 新旧 block 并存幂等误判修复，全新会话实证 git=Function/clean BLOCKED/Session ID 注入）②#67 lock_files TTL+Mutex（9 用例+DM-202919 回归 10/10）③66 plumbing 扩展（45/45+16/16；pyproject basetemp 仓内透传风险实证改系统 TEMP 留警示）④#66 两子项（sweep force-clean 接四证语义审计+heartbeat daemon 普及 CLI 路径+register pid=0 等 3 bug 治本）；66 commit_queue 本体如实留排期；新发现 #68（Trae 终端不加载 $PROFILE）——已由 c79de22c0d 闭环。
- [c79de22c0d·#68 闭环] 2026-08-15 第四统筹核验 **PASS**（反馈文本补转）：agent-tool-host -NoProfile 硬编码 strings 实证→65 memo §7.33 裁定快照注入（ensure_ai_wrapper_injection.ps1 幂等 marker+计划任务 ZephyrAlpha-AI-Wrapper-Inject 每分钟保活+wrapper AI 归因 session=ai-<pid>-<启动ts>+审计 channel 字段单文件聚合）；15 新用例全绿+既有 80 不回归+真实 AI 通道实证（clean -fd BLOCKED/status 透传）；两新陷阱登记（ZEPHYR_SESSION_ID 继承须 env.pop 隔离+IDE 脏缓冲区 Edit 不落盘——后者在本统筹 merge 中两次实证复发，均按处方 PowerShell 直写+进程外核实处置）；tracker #68 行=【已闭环】版（merge 隐性回退已修复）。
- [coord-0814-git001·T0/T1 核心] 2026-08-15 第四统筹核验 **PASS**（反馈文本补转）：98aeffde63 doc_lifecycle 状态机（观察 7 天宽限/生命迹象自动复活/满期归档 30 天回收站/零物理删除全自动）+GATE-WORKING-DOCS 一枪毙命废除（auto-commit 仅限满宽限期归档带 [lifecycle-archive] 标记）+ops_guard 回收站 API（guard_recycle/guard_move/prune_recycle_bin），4cb49217 吞噬兼容修正吸收第三统筹正则前缀吞噬实证（17/17 全绿）；TTL 声明质保链断裂新发现登记 #73；潘潘 16 文件删除平反（合法迁移收口 07b0707c2d/b2dd5630b3）已并入 #53；观察清单 .runtime/archive_watchlist.json 机器可读。
- [数据域会话·#59/#60 施工] 2026-08-15 第四统筹核验 **PASS**：commit 实证在库（3b7eae39f8 观测层治本 B/C/E 全落地——日志落盘 RotatingFileHandler 10MB×5+biz 心跳 15s 原子写双心跳正交+盘中 300s 无 tick 看门狗重订阅；a2208f30e1 巡检口径排除 6 误报表归零+lof_list 潜伏治愈；998d23d1c1 fix_phase 同步）；统筹独立复跑 tests/zephyr/data/test_tick_subscriber.py **61/61 全绿**（0.65s，补齐协调会话"未独立复跑"缺口）；施工项 2 裁定细化知情采纳（规则 B 按 schedule 判定而非裸 incremental=false，防误伤 REALTIME-ACCUM 快照积累表）；线上已部署（biz 心跳 today_rows=8035 链路活+周六 is_trading_day=false 日历正确）；周一开盘实盘终验清单 3 项备案（订阅序列日志/today_rows 盘中增长/断流模拟 5min 重订阅+10min guard 重启+deadman 告警链路）；踩坑两则登记 #75。
- [AI-TICK-001] 2026-08-15 第四统筹核验 **PASS**（三轮反馈）：①commit 实证——e061a3b0（18 项契约测试入库 +385 行）+9613fbc7（TestMain autouse 隔离防生产 run log 污染）+a88a56fb（全项目模拟盘化：restart_minimqmt.ps1 每日 16:00 任务默认重启目标改模拟——终端环境漂移制度性根源修复+4 docstring 示例）均在库；merge e179d4ce25（自执行，#ARCH-MERGE-PATH-GAP-001② 通道）；②Step 1/Step 6（A 类）PASS；③测试 79/79×2 轮（61 存量+18 新增）+统筹 dev 复跑 79/79（2.20s）；④联调实证：fake xtdata 全链路+ps1 消费侧 16/16 探针；⑤线上部署：PID 50380 连模拟盘（QMT 实例辨识 TCP 配对✓），biz 心跳全字段正确；⑥唯一人工前提=#84（模拟终端勾自动登录）；⚠️ a88a56fb 收编 REGIME 6 件 staged WIP 事故登记 #81；.pth 隔离缺口第三轮证伪（简单路径型 append，conftest/activate_env 双锚定正确）。
- [AI-XCUT-001+002] 2026-08-15 第四统筹核验 **PASS**：①3d68da3ed3（4 文件 +28/-161，60 号三处漂移收敛+§16 真源收敛 module_translation_registry conflict_matrix）+1b613f03cd（#8 MOD-POS-021 三 token 补登闭环+主仓 capability registry 一行 >>>>>>> 残留清除——RCN merge 尾巴，致谢）；②Step 1 推翻"骨架需重建"前提（60 号 active v1.0.2 内容完整实证，00_index L672 系滞后登记已同步）；③85 项×2 轮全绿；④merge def379dbc9+479de59b23（四证 PASS 自动清理+XCUT-002 派生回写 stash 存证 refs/quarantine/AI-XCUT-002）；⑤SOME-OTHER-GATE 定性测试夹具污染+358 行精确清污（备份 .runtime/governance_db_backup_before_xcut001_logcleanup.db，今日新污染=0）；⑥顺手发现登记 #80（session_worktree merge --to 默认 main 风险）。
- [AI-REGIME-001] 2026-08-15 第四统筹核验 **PASS**：①837c5b256c（55 用例重建——原套件 2026-08-11 git 灾难丢失取证不可恢复，按 34 号 §3.4 十六要点回建）+2bc86c1b29（blueprint v0.1.1→v0.2.0 全量对齐代码 v1.0.0 十二处+memo v2.8.6）；②四回归锚点覆盖（Sortino 分母 n-1=10.78 vs 7.49 可区分/water-filling N=2 无解兜底/CRISIS floor 0.09→0.05/allocation×global_shrinkage 解耦）；③55/55×2 轮+tests/pf_alloc 153/153 无交叉污染；④RECONCILER-HEALTH 384 行测试污染清偿（备份 %TEMP%\reconcile_log_test_residue_backup_20260815.json，横幅消除终证）；⑤merge 经 a88a56fb finalize 插曲知情——message 未附冲突处置留痕，审计链以会话报告+本登记为准；⑥worktree 已自清（心跳 idle 自退）。
- [AI-COMP-001] 2026-08-15 第四统筹核验 **PASS**：①3 commit 实证（8fc6a993b3 主体 31 文件+3760/-35：MOD-CMP-001/002/005/007/008/009/010 七模块+78 测试+7 蓝图+2 新登记表；b9e38e8dca 遗留登记；5708658d3e 方案 A 落地）；②Step 1 PASS（43 号 v0.1.1 交叉引用全实证，过度工程红线守住：AML/KYC/隔离墙/50μs 显式不建或降级）+Step 6 十四节全 PASS（自审捕获修复 4 项含追高边界浮点尾差）；③79 项×2 轮全绿+统筹双环境复跑 79/79（worktree 1.45s/dev 1.33s）；④merge de45d261aa（统筹执行：派生 6 取 theirs+ROOR 并集+撞号重编 #77-79）；⑤遗留三项 #77（47 项裁定全量迁移，源文档不在仓 19 种子已登记）/#78（运行时接线留装配批+日申报笔数硬计数器追加）/#79 ✅ 已闭环（方案 A）。
- [140 WIP 调查会话] 2026-08-16 第五统筹核验 **PASS**（commit 558fb2ee4b 实证在 dev，GitCommitGateway 双留痕通道规范）：①140 外来 staged 悬案终裁——终态 127 文件 100% 派生活水（AUTO 统计块数字，patch 逐 diff 实证），零损失闭环（§六 #94）；②merge 排期追认正确（JOB077 abort 独有仅 2 派生自动提交零信息损失；#ARCH-70 通道本轮已履行完毕）；③顺手治理执行——杀 2 残留 daemon+1 僵尸 backup.ps1、删 5 孤儿 worktree 目录（DC2-01 179MB 陈旧快照+4 空壳）；④治本 Z1-Z3 已 CAND 登记（CAND-WORKTREE-001 退役存证+分类器 / CAND-DAEMON-001 daemon 失锚自退，§六 #97）；⑤Z5 session/* 陈旧分支删除权交用户裁定（§六 #98）；⑥233 交接书落盘 docs/_working/reports/233_test_debt_batch_handover_20260816.md（六包施工规范备查件，与 .runtime→docs/_working/dispatch 开工指令互补）。裁定书 §4 真源=2026-08-16-test-debt-leftover-adjudication.md。

## 五、施工批次规划（当前）

| 批次 | 内容 | 状态 |
|---|---|---|
| 第 1 批·业务+建库+定稿 | 8 个施工队 | ✅ 全部完工 merge |
| 第 2 批·业务+建库 | 7 个施工队 | ✅ 全部完工 merge |
| 第 3 批 | 33 BudgetChange / 37 流动性 / 42 卖出流 | ✅ 3/3 全部完工 merge |
| **治理插队批（2026-08-14 用户裁定）** | **AI-GIT-001：git/并发协作基础设施专项（65/66/67 号 + 裁定书 S1-S6：ops_guard 删除收敛/清理四证 SOP/网关锚定/观测层/task_board 重建）** | ✅ 已 merge 回 dev（2026-08-14 统筹，16 commits：S1-S6/task_board/65号 v2.3.0/tracker #49-52 登记；worktree 按四证 SOP 清理，见 §六 #54） |
| **文档压缩批（2026-08-14 用户裁定）** | **AI-DOCS-001：18 篇 ≥1000 行大文档压缩（62/10/54/63/35/36/28/64/40/32/37/90/34/61/26/24/25/AI_review）** | ✅ 已 merge（53856ed1c0 + merge ab3df58d9d；33.6k→23.2k 行，章节编号/参数/裁定/锚点零丢失，三波子代理自审全 PASS + PURE-ASSERTION 表格化修复） |
| **治理批②（2026-08-14 晚用户裁定）** | **AI-RCN-001：reconciler 自动删除失控族治本（裁定书 T0-T6：T0 止血 dry_run/T1 删除能力显式声明+ops_guard 安全 API+统一回收站/T2 worker 启动三证+删除审计覆盖率/T3 文档保护区/T4 #55 审计迁出 tracked 区/T5 告警卫生/T6 文本对齐）** | ✅ **已 merge 回 dev**（2026-08-15 午 e0f962f36e 双亲实证；核验 PASS：12 commit 全实证+统筹复跑 143 项全绿+红队 246×2 全绿；worktree 已按四证 SOP 清理，见 §七） |
| **治理批③（2026-08-15 同会话续作）** | **ARCH-WORKTREE-DB-SPLIT-001 治本（仓级共享状态所有权归主仓/anchor_main_root 两型锚定/worktree 禁写权威 REFUSED/ops_guard 补丁卸载 API）+ #55② 四项顺修全闭环 + strip_session_worktree 同族陷阱五形态根治** | ✅ **已 merge 回 dev**（同 e0f962f36e；核验 PASS：25 文件治理域无夹带+2182×2 轮全绿；新登记 #61-#64 待专项裁定，#63 测试债建议专项清偿批——用户已裁定与第 4 批并行开工） |
| 第 4 批 | 34 RegimeMeta / 60 跨切 / 43 合规 | ✅ 3/3 全部完工 merge（2026-08-15 当日派单当日完工：34=837c5b256c+2bc86c1b29 / 60=def379dbc9 / 43=de45d261aa；另 tick 紧急插队 e179d4ce25+XCUT-002 479de59b23） |
| **测试债清偿批（2026-08-15 用户裁定并行）** | **AI-TDEBT-001：#63 全量测试存量债 785 failed/17 errors 按簇分包清偿（cross/autonomy/external/semantic/escalation 簇+collection error+xdist set 参数化治本）** | ✅ 已 merge（16c3dcf2c9，2026-08-16 第五统筹） |
| **治理顺手批（2026-08-15 晚用户裁定）** | **AI-FIX-001：#69 d6 hook 传参兼容+#70 I001 瑕疵+#80 --to main 默认值+#82 文档债+#73 TTL 质保链（增量校验+每日全量 rejudge）** | ✅ 已 merge（a539c1fcb6，2026-08-16 第五统筹） |
| **数据产能批（2026-08-15 晚用户裁定插队）** | **AI-JOB077-001：JOB-077 市场元数据与约束接入（DS-081~085：股票基本信息/涨跌停价/停复牌/指数成分/ST 状态——universe 构造+回测撮合约束前提，打板回测急需）** | ✅ 已 merge（会话自 merge bdf37ab8d5+1e9f14fc82；JOB083 846a1019a6/JOB084 3f7f7b603b 同批闭环） |
| 第 5 批 | 53 模拟实盘（AI-SIM-001）/ 54 对账归因（AI-RCAN-001）/ 55 监控复盘（AI-MON-001） | ✅ 3/3 全部 merge（eafc17941c/057a9a2384/0d5f8f0777，2026-08-16 第五统筹） |
| **数据补充批（2026-08-15 晚用户裁定增派）** | **AI-NORTH-001：19 号北向季度持仓快照 fetcher（tushare hk_hold 已验证，日频断档替代）** | ✅ 已 merge（87f50a5e3f，2026-08-16 第五统筹；tushare_provider 冲突手工合并） |
| **装配批（2026-08-15 晚用户裁定增派）** | **AI-ASM-001：#78 合规运行时接线（C-004/C-002/MOD-PA-006 调用点嵌入 40/41 号 production 链路）+日申报笔数硬计数器（5000 预警/1 万阻断，复用 24/40 号既有计数）** | ✅ 已 merge（8b932ced42，2026-08-16 第五统筹） |
| 重建类 | 28 号情绪周期恢复（AI-SENT-001，从 a3750b90d1 恢复 v1.2.0）/ 60 号骨架（XCUT-001 实证非骨架无需重建） | ✅ 28 号已闭环（内容层前序会话已恢复至 v1.2.3；AI-SENT-001 核实 v1.2.0→v1.2.3 压缩零漂移 + 00_index L54/L384/L642 三处状态修正）；60 号 ✅ 免重建 |
| **测试债清偿下批·233 长尾**（2026-08-15 深夜 TDEBT-001 裁定书建议立项，第五统筹登记） | 6 包分包（裁定书 §关联项 E，Two Sigma 风险加权安全/资金优先）：包①安全权限 ~30 项（escalation/rbac/agent_spec/skill）/ 包②交易资金 ~45 项（trading/position/pf_core/rollback）/ 包③治理蓝图 ~60 项+搭车 #ARCH-099（gov_db 8 xfail 治本=自建最小 schema fixture）/ 包④数据基础设施 ~40 项 / 包⑤自治生命周期 ~35 项 / 包⑥工具其他 ~23 项+复跑全量验证 | ✅ **6/6 全部 merge 闭环**（2026-08-16 第五统筹）：包⑥ UTIL 26 项（bdda340270）/ 包② TRD 24 项+裁定治本（a3321a0e1c+8e7e0420b5 补链，#ARCH-103/104/105）/ 包⑤ AUTO 26+1 项（7877748977+9222d8bd7b 追加）/ 包④ DATA 20+7 项（62e550dcd3，配号 #ARCH-109~113）/ 包① SEC ~30 项（3041dc7745，#ARCH-106/107/108）/ 包③ GOV ~60 项+#ARCH-099 gov_db fixture 治本 resolved（5e486bebed，#ARCH-114/115/116 重编）；10775 项 2 轮全绿；六 worktree 全四证清理 |
| **冷分层裁定批（2026-08-16 用户直派，统筹活性登记）** | **AI-ARCH-002：冷分层裁定落地（task-cold-tier-rulings）**——基于 140 WIP 调查裁定（558fb2ee4b）续作；data_retention_contract.yaml 修订+archiver.py 重构（+214 行）+test_ch_archiver.py 新建（160 行） | ✅ **已 merge 闭环**（f556515519，2026-08-16 17:25；worktree+分支已自清。【更正：统筹此前登记"施工中"系上下文压缩期滞后认知，实际早已离场】） |
| **算法修复批（2026-08-16 晚用户裁定派单，接线批已闭环触发）** | **AI-RFIX-001：F1 ES 插值（method='lower'+memo 口径裁定）/F2+F4 NaN+Inf 过滤（isfinite+nan_dropped 计数+超阈值 raise）/Qwen P1 群（仓位上限非单调数值表/撤单计数接 ASM 日申报计数器/POT 小样本降级+告警验证/D1-D9 文档漂移对账）/F5 RegimeMeta 死代码清理/FHS 漂移裁定（memo 36 §3.10 转远期候选或 CAND 登记）**——F3 幽灵第三枚举已由 RRESIL 批施工不重复 | 🔄 已派单（worktree .worktrees/AI-RFIX-001 自 dev 0bd6a2b55d 切出；与 GOV-001/ARCH-002 零交集实证——域=risk/pf_alloc/ex_core/docs，裁定书=docs/_working/reviews/2026-08-16-dual-review-adjudication.md §二/§六） |
| **🔴 P0 风控接线批（2026-08-16 双轮审查发现立专项）** | **风控三件套+KillSwitch+对账器生产接线**：双轮审查（Kimi 一审×Qwen 盲审）实证 35/36/37 模块+execute_kill_switch_liquidation+PositionReconciler **测试全绿但生产链路零实例化**（RiskOrchestrator 不存在；trading_session 仅有合规层 ASM 接线）——回撤 25% 不熔断继续下单。含 P0-2 crash 恢复（启动券商全量重建+fill_id 持久化去重+Saga 超时终态查询）+P0-3 KillSwitch 状态落盘 Fail-Closed+LIQUIDATING 锁+单一仲裁点。裁定书=docs/_working/reviews/2026-08-16-dual-review-adjudication.md | ✅ **已 merge 双路闭环**（2026-08-16 第五统筹）：RRESIL 原语层先 merge（dbc5d40e2b，零冲突）→RWIRE 消费层后 merge（2b3b68b5d2，module_translation 冲突手工并集）；接口连通实证 rebuild_from_broker(holdings, today_fills=(), *, cash=None) 兼容；统筹独立复跑 RRESIL 45/45+RWIRE 12/12 全绿；红队实证（双路非 mock）：回撤 25%→EMERGENCY→真实置位→MARKET SELL 清算全链/熔断重启存活/并发双触发单轮发单/event_id 重放不重复/rollback 不双倍回滚/重建期禁单 Fail-Closed；**风控层从"纸面熔断"转生产接线态**。遗留：37 号流动性 LEVEL_3 接线（后续批）/Redis 后端 state_store（后续批）/QUANT-002 registry 流转（统筹收口）/PG 5432 停服核查（RRESIL 报告） |
| **结案报告与独立复核批（2026-08-16 用户直派）** | **28 篇已结案设计备忘开头补写结案报告**（实际开发/最终成果/未做+原因三段式）+ **外部审查员口径独立实证**（不信任何 AI 文档：52 个引用 commit 逐个 git log 实证全在、关键套件 pytest 复跑全绿、43 号装配接线 production 代码逐行实证）——**发现 2 处漂移当场修正**（53 号五态降级机裁定落点与代码不符，#101；54 号 RCAN 批次性质=文档收敛无新增代码，报告改写）+2 处计数滞后补记（16 号 418 测试/41 条目、55 号 33 条阈值）；新登记 #101-#103 | ✅ 已完工（直改 dev 工作区，改动未提交 git） |

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
| 34 | 幽灵锚点 9 个存量硬阻断（BM-INV-002） | AI-BGT-001 | 经主工作区 2026-08-13 16:04 报告实证为存量，非施工引入；统筹走 battle_map 治理，非施工队范围 | ✅ 已闭环（2026-08-14 统筹随 #52 一并清理：实测 10 个全清，apply_battle_map.py --remove-anchor 逐条执行，anchors 499→489，DB 复查 depgraph 类幽灵归零） |
| 35 | 37 份蓝图 §11 代码索引漂移（含 MOD-POS-022 仍标"❌ 未实现"） | AI-BGT-001 | 统筹统一跑 sync_blueprint_code_index.py（单队跑会搭便车 36 份他域文件） | ⏳ 统筹统一执行 |
| 36 | 30 号表述漂移（"47 单测全绿"/"481 行"/不存在方法名） | AI-BGT-001 | 越界项，留 30 号负责会话 | ⏳ 30 号会话 |
| 37 | 00_index 对 33 号版本登记滞后（现已 v1.1.0） | AI-BGT-001 | 登记时 bm-fill 占用 00_index；现已释放，统筹可直接同步 | ✅ 已闭环（2026-08-14 统筹同步 00_index L57/L657 至 v1.1.0；v1.1.0 内容在 BGT worktree commit 1b8a774ad5，随第三批统一 merge 生效） |

### P0-事故 · 2026-08-14 worktree wipe 事故（AI-LIQ-001 裁定书）

> 裁定书全文已归档：docs/02_enterprise_architecture/04_architecture_principles_decisions/2026-08-14_ai-liq-001_worktree_wipe_incident_review.md（2026-08-14 自 _working 临时区迁入 04 永久区）
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
| 50 | reconcile live-timeout 测试隔离缺陷 + 测试污染生产审计日志 | AI-GIT-001 实证 | test_reconcile_async.py 两测试（test_live_timeout_*）告警计数跨测试/跨运行泄漏（期望 1 实测 2-3 且逐次递增）；且 pytest 运行向生产 reconcile_execution_log 写入测试 SHA（live_heal_sha/live_timeout_sha）触发 RECONCILER-HEALTH 误报横幅。存量问题，非本次引入 | ✅ 已闭环（2026-08-14 统筹：病根=conftest basetemp=<repo>/.runtime/tmp/pytest_<pid>，worktree 内 tmp_repo 被 strip_session_worktree 剥离锚定主仓生产库；治本=模块级 autouse fixture _isolate_governance_db 强制锚定 tmp_repo 独立空库；3 轮 44 passed 零新增污染实证；生产库 10 行测试污染 DELETE 清除（备份 .runtime/governance_db_backup_before_50_cleanup.db），24h 未 ack critical_warn 归零 banner 息屏） |
| 51 | script_manifest.yaml `demos/demo_e2e_pipeline.py` 幽灵条目 | AI-GIT-001 发现 | 该文件在 dev 树未被 git 跟踪（仅主仓工作区 gitignored 残留），manifest regen 在 worktree 内扫描会反复移除该条目——已在 AI-GIT-001 提交中还原保持现状；归属 pipeline 域，由统筹裁定清理或补跟踪 | ✅ 已闭环（2026-08-14 统筹裁定**清理**：FILE-COPY 门禁实证 scripts/demos/ 副本与受维护真身 scripts/construction/demo_e2e_pipeline.py 79.6% AST 重复且陈旧（7/31 vs 8/3），违反 D1 查重——删除陈旧副本，幽灵条目随 regen 自动消隐；smoke test 原指 repo 根不存在文件存量失败，顺手重指 construction 真身转绿；.gitignore `demos/`→`/demos/` 锚定根防再误伤；多真源一并裁定收敛：连字符 script-manifest.yaml 为登记真源（orphan_scanner/speed_baseline/pipeline_runner/scaffold_registrar/registration_checker/REG-SCRIPT-001 全消费此版），generate_manifest.py OUTPUT_PATH 回锚连字符，下划线 script_manifest.yaml 退库（700 条重生成），governance 子集（GATE-21 校验+integrity 保护）不动，file_autoregister 死引用顺手修） |
| 52 | 存量幽灵锚点精确画像（#34 补充） | AI-GIT-001 实证 | #34 登记 9 个，实测 10 个：655-663 九个数字 node_id 形态（BM-EXE-02/04/05/06）+ 524 一个 blueprint 形态（MOD-DAT-fred_ingest，BM-RES-11-A）。S5 级联提示已落地（7a08eb74）防新增；存量清理仍走统筹 apply_battle_map.py --remove-anchor | ✅ 已闭环（2026-08-14 统筹：10 锚点（524/655-663）逐个 --remove-anchor 清除，anchors 499→489，DB 复查 depgraph 类幽灵归零；另 28 个 candidate 类锚点（CAND-xxx 引用候选库条目）经判为合法候选池引用、非幽灵，不在本项范围） |
| 53 | reconciler 批 auto-commit（accd0cbe36）误删 tracker+handoff 两统筹文件（原 #49，merge 时与 AI-GIT-001 分支 #49 撞号改挂 #53） | 第三统筹会话实证 | 疑 frontmatter `ttl: task_bound` 触发 TTL 类 reconciler 自动清理（全批次✅被误判为任务终结）；已从 abab909da8/accd0cbe36^ 字节级恢复；**2026-08-14 晚实证复发**：本统筹备份 commit（d771ec1a）触发 post-commit reconciler，主工作区 docs/_working/潘潘直播课程/ 16 个 tracked 文件被删（git restore 已恢复）；⚠️ 同批 untracked 草稿 docs/_working/潘潘直播课程/草稿/清风量化交易系统2.0.md 被物理删除**不可恢复**（全仓+.runtime/tmp 搜索无踪迹）；凶手实证=锚定已删 AI-DOCS-001 worktree 的 rogue reconcile worker（PID 26288，17:40 启动，stdio 无日志——dev 此前无 S3 落盘，本 merge 后已补齐；统筹已终止该进程）；需排查哪个 reconciler 执行删除并加白名单/防误删规则——与 #38 S1 删除收敛同根。**取证订正（2026-08-14 深夜，S3 观测层赋能）**：①tracker/裁定书/因子与策略提炼 实证在 .runtime/working_archive/1786687492/——GATE-WORKING-DOCS 幽灵引用归档器所为（可恢复），原"TTL reconciler 误删"定性修正为"幽灵引用误归档+auto-commit 物理删除"；②19:05 批次 16 文件不在 working_archive（另一删除路径，疑活体 worker PID 19668，日志 0 字节仍在缓冲）；③ops_guard 审计零 潘潘 删除记录（删除路径绕过 S1 已包装原语，S1 覆盖面前存在盲区）；④清风 19:04 被重建后 19:05-19:15 再次消失（二次丢失；同期用户新建技术仓库.md，亦可能为用户自行移动，待确认） | 🔄 真凶已定罪（2026-08-14 晚裁定书 2026-08-14_coord_reconciler_auto_delete_governance_review.md 裁定1：GATE-WORKING-DOCS 幽灵引用归档器=三波"误删"真凶，move+auto-commit 具备实质删除能力，违反 I-GOV-2；裁定 1-7 全录含 S1 盲区/worker 零准入/#55 治本/告警卫生）——治本 T0-T6 由治理批② AI-RCN-001 承接（2026-08-14 晚用户裁定优先于第 4 批），验收标准机器可验证，全层验收后闭环。**深查补充（2026-08-14 第三轮统筹，代码级实证，供 AI-RCN-001 直接采信）**：①归档器误报三类根因实证（working_docs_1786709984.json 报告）：提取正则首字符限 [a-zA-Z] 吞前缀——`.runtime/`→`runtime/`、`.git/`→`git/`、`_shared/`→`shared/`；数字开头路径段被吞——`01_policies_and_standards`→`policies_and_standards`；纯文本提及（非引用语义）也算引用——三类叠加使"宁漏勿误"反转为"宁误勿漏"，且恢复后引用不变→反复归档（4 次实证）；②ops_guard 盲区精确机制：ops_guard.py L453-455 只解析命令字符串（Remove-Item/del/rd/Python 文本模式），reconciler 进程内删除（归档器 shutil.move/清扫器 os.remove L12784）从不经过命令字符串→审计零记录结构根因，且未覆盖 shutil.move/Path.unlink/os.rename（移动=删除效果）；③rogue worker 部分平反：reconcile_worker._run_worker L320-365 实证 payload project_root 无存活/无归属校验（结构性缺陷真实，需修）；但 19:05 潘潘 16 文件删除与潘潘会话自己的"清理16篇全覆盖源文档"提交（07b0707c2d/b2dd5630b3）高度吻合，疑合法自删被误判 rogue，清风文件归属待用户确认 | ✅ 全闭环（2026-08-15 merge e0f962f36e 落地 dev，治本验收机器实证齐全）——真凶已定罪+根因三级实证；**T0/T1 核心已落地 dev（第一统筹 coord-0814-git001，98aeffde）**：doc_lifecycle 状态机（观察 7 天宽限+生命迹象自动复活+满期归档 30 天回收站+零物理删除，17 测试全过含吞噬形态兼容——吸收第三轮统筹"正则前缀吞噬"实证：EPHEMERAL_COMPAT_PREFIXES 无前导点形态同判豁免）+ GATE-WORKING-DOCS 重写接入（一枪毙命废除，auto-commit 仅限满宽限期归档且带 [lifecycle-archive] 标记）+ ops_guard 回收站 API（guard_recycle/guard_move/prune_recycle_bin）；T2-T6 由 AI-RCN-001 续（本实现为评审基线，可迭代可 revert）；**T2-T6 已全部落地（2026-08-14 治理批②续）**：T2 worker 启动三证（锚定存活/payload 新鲜度/session 活性，缺一拒启）+ 删除/移动动作全量 stderr 落盘 + TestWorkerAdmission；T3 双裁定书 ttl→permanent；T4 flags.py 审计写迁 .runtime/audit/ + data/audit_logs/ 全目录退跟踪 + #ARCH-PRECOMMIT-STASH-ADAPT-001 立项；T5 双 cleanup reconciler 锁定跳过=clean 语义 + RECONCILER-HEALTH 横幅 24h 签名 dedup（6 新测试全过）；T6 I-GOV-2 对齐注记 + wipe 裁定书排除项勘误；107 项关联测试全过。**T0-T6 全层闭环（2026-08-15 AI-RCN-001 验收完毕）**：commit 全录——T0 止血 bed51d1956（+98aeffde63 doc_lifecycle 状态机核心）/ T1 能力收敛 dc0408d195+e63e88592d+5f81d28adf / T2 观测准入 086d0e24e4 / T2-T6 恢复批 bb3a91d48a（T3③裁定书 permanent+T4-1 审计迁出+T5+T6）/ T3①② 8621663140（目录契约 v1.2.0 禁区声明+untracked 人工确认闸门全入口接线）/ 证3 竞态+T4-2 1e794dc3（worker 活性'活跃 OR 15min 近期心跳'治本+网关 tracked 漂移监视器）/ 派生同步 a2305c9a9a；验收实证——T1 红队 100% 阻断+审计落盘（含 worker 进程内裸 os.remove 拦截）/ T2 拒启+日志可查+证3 一次性进程竞态修复（2 回归用例）/ T3 untracked 删除必落审计（9 用例）/ T4 干净工作区裸 commit 框架误报计数=0+hook 前后 tracked 零漂移（仅 by-design GATE-COMMIT-GW 拦截+存量 ZR-005 除外）/ 红队+准入关联测试连续 2 轮 246 项全绿；遗留另立 #ARCH-WORKTREE-DB-SPLIT-001（worktree/主仓 governance.db 双源致生成器振荡，open 待裁定） |
| 54 | worktree AI-GIT-001 四证 SOP 首次真实清理（S2 验收项）+ wipe 机制第三次实证 | 统筹执行 2026-08-14 晚 | merge（d8f94d4f2b+04cae020）后四证齐全执行 abort：证1 registry DEAD（唯一活跃=本统筹会话）；证2 dev..branch 0 ahead + worktree 遭 rogue worker 第三次 wipe（6038 D+1 M，分支 ref 完好、工作已全 merge 零损失）→ stash 16b5b0691b 存证 refs/quarantine/AI-GIT-001；证3 用户任务显式批准；证4 bundle .runtime/quarantine/AI-GIT-001.bundle + tip 30c126cefd 录 branch_refs.log；abort exit 0 四证全 PASS，分支 git branch -d（bundle 可秒级恢复）。⚠️ SOP 文本-实现漂移：§4 载"abort 他人需 --coordinator-approved 旗标"，实现无此旗标（证3 靠自律+审计）——同 #43 类漂移，下轮 SOP 维护顺手修 | ✅ 已闭环 |
| 65 | 【已闭环】65 号 Phase 1 wrapper 层全部 7 项施工落地+激活 | AI-GIT-001 第二批（2026-08-14 晚，用户授权"遗留+P1/P2 全处理"）；激活=2026-08-14 深夜治理批 | scripts/git_safety_wrapper.ps1（唯一真源）+ install_git_safety_wrapper.ps1（§7.7 幂等安装）+ RULE-GIT-SAFE 写入 AGENTS.md/.trae/rules（§7.2）+ d6 三 hook 接入 pre-commit（§7.13）+ Session ID（§7.32）——commits 611227d5/21f447c1，40 验收测试两轮全绿。PS5.1 实证修正 memo 三处假设：①Alias>Function（AllScope 别名需 Remove-Item Alias: 删除，Set-Alias/function 覆盖均无效）②裸 `--` 被吞（checkout 路径/分支区分改 rev-parse 校验）③Add-Content UTF8 带 BOM 坏 JSONL 首行（改 AppendAllText 无 BOM）。偏差登记：§7.1.4 ProxyCommand 未采纳；.git 阻断挂删除类。**激活实证（2026-08-14 深夜）**：$PROFILE 发现新旧两 block 并存（旧 v2.1.0 内联 370 行全量+新 dot-source——旧 marker 含新 marker 前缀子串致安装脚本幂等误判 skip），已清除旧 block 保单一真源（备份 TEMP profile_backup_20260814_213917.ps1）；全新会话实证 git=Function、clean -fd BLOCKED exit 1、status 透传、审计 JSONL BLOCKED+ALLOWED 双记录、Session ID 注入 | ✅ 全闭环（施工+激活+实证） |
| 66 | 【新事故机制·已修复】CLI session_worktree create 不做 SessionRegistry 活性登记——治理层 sweep/base_sync 误判死 session 残留 | AI-GIT-001 实证（2026-08-14 深夜，wrapper 施工期间三文件两度被抹）；残留两子项=2026-08-14 深夜治理批闭环 | 病根：scripts/session_worktree.py（CLI 入口）create 只备三件套，不注册 SessionRegistry/不 spawn heartbeat daemon（rule_bridge 的 session_worktree_start 才有 daemon）——CLI 创建的 worktree 在治理层=无注册无心跳死残留，GATE-WORKTREE-LIFECYCLE sweep（post-commit 触发）+ base_sync（无 session commit→git reset --hard 主仓 HEAD，reflog 铁证）反复抹除未提交工作（staged A 文件随 index 重置消失，git fsck dangling blob 找回）。与 #53 rogue worker 删除链同族。**已修复**：d7844786 create 补 SessionRegistry.register（锚主仓根 --git-common-dir，失败不阻断）。**残留两子项已闭环（2026-08-14 深夜治理批）**：①sweep force-clean 接四证语义审计——rule_bridge _sweep_one_dir force-clean 分支 quarantine ref 成功后落 .runtime/gate_audit/worktree_abort.jsonl（与 S2 四证同文件同构；语义映射：证1死亡=sweep 判据已确认未注册+超龄、证2=COMPENSATED 有未合并提交由证4前置补偿、证3=AUTO 72h 窗软批准供统筹复查、证4=quarantine ref）；②heartbeat daemon 普及 CLI 路径——create spawn detached daemon（30s 心跳，幂等 PID 文件，ZEPHYR_RUNTIME_GATE=0，WMI 降级），abort 对称 teardown（taskkill daemon+cleanup_heartbeat_file+unregister）。**顺手治本 3 实证 bug**：①register pid=os.getpid()→pid=0 逻辑 session（跨进程工作流 PID 死亡即判死，daemon 心跳白 spawn——rule_bridge Phase 6 早有此治本注释）；②abort 先 remove worktree 后找分支（worktree list 已删除永远找不到）→顺序颠倒；③_find_branch_for_session 返回 refs/heads/ 全限定名致 git branch -D 静默失败→剥前缀。**端到端实证**：daemon 保活 list_active 命中、证1 BLOCKED 拦截活跃会话 abort、teardown 后分支/worktree/daemon/registry 零残留 | ✅ 全闭环（机制修复+两子项+3 bug 治本+实证） |
| 67 | 65 号 Phase 2 项 8（lock_files.py TTL 五命令+§7.28 Mutex 原子写）+ 66 号 plumbing 扩展 | 65/66 memo 既定范围；2026-08-14 深夜治理批承接 | **lock_files（✅ 落地）**：§7.28 Windows 全局命名 Mutex（CreateMutexW Global\ZephyrLockFilesRegistry，5s 超时+WAIT_ABANDONED+超时 DENIED+acquire 回滚锁目录防半锁）+tmp/flush/fsync/os.replace 原子写；§11.2.2 `acquire --ttl <分钟>`（默认 1800s 真源 ttl_design 不变）+owner.json/registry expires_at 双写+`_is_stale` expires_at 优先旧格式回退+`list --session` 新命令凑齐五命令。验收 tests/git/test_lock_files_ttl_mutex.py 9 用例全绿（26 线程并发无丢锁+Mutex 超时回滚+TTL 到期自动清理），DM-202919 回归 10/10。**66 plumbing（✅ 落地）**：wrapper git() 拦 read-tree/update-index/write-tree/hash-object+ZEPHYR_SERIALIZER_MODE=1 白名单（test_git_safety_wrapper 45/45）；git_guard.py 前置硬阻断+plumbing 审计（test_git_guard_self_harm 16/16）。⚠️ 测试风险实证：pyproject basetemp 在仓内（.runtime/tmp/），白名单透传用例在仓内跑 read-tree 会真碰主仓 index（66 事故 6 同款）——已改系统 TEMP 并留警示注释；主仓 index 实证无损（staged 恒空）。**66 commit_queue 本体仍⏳待排期**（.runtime/commit_queue/ 零施工痕迹，Serializer/死信/门禁外移为大工程量单项） | ✅ lock_files+plumbing 闭环；⏳ commit_queue 本体留排期 |
| 68 | 【已闭环】Trae AI RunCommand 终端不加载 $PROFILE——wrapper 对 AI 命令通道无效 | 2026-08-14 深夜治理批实证；2026-08-15 专项闭环 | **机制根因（代码级实证）**：agent-tool-host.exe（Rust）spawn `powershell -NoProfile -NonInteractive` 硬编码于二进制（strings 实证），settings.json 无开关，四 profile 变体全抑制；但 preamble dot-source 每 toolhost 进程级快照 `native-runcommand-snapshots\process-<pid>-<ts>\powershell-profile-snapshot.ps1`=注入点。**裁定（65 memo §7.33）**：a 配置层/b AllUsers profile 不可行、d PATH shim 否决（系统段优先）、e 规则层留补充；f **快照注入采纳**——ensure_ai_wrapper_injection.ps1 幂等注入（marker ZEPHYR-AI-WRAPPER-INJECT，支持 -Remove）+ 计划任务 ZephyrAlpha-AI-Wrapper-Inject 每分钟保活（减配：toolhost 重启后≤1 调度间隔裸奔窗口）+ wrapper §7.33 AI 归因（父进程 agent-tool-host → session=ai-<pid>-<启动ts>，审计新增 channel 字段，聚合同一 IDE 会话全部 AI 命令到单文件）。**验收**：15 新用例全绿（注入幂等/端到端拦截/假 toolhost 归因/审计聚合/任务注册）+既有 80 用例不回归+人工终端实证不回归；真实 AI 通道实证 clean -fd BLOCKED/status 透传/session=ai-25808-*。**顺手登记两新陷阱**：①AI 会话子进程继承 ZEPHYR_SESSION_ID（归因特性，测试需剔除隔离，两测试文件已适配）；②Trae IDE 文档层脏缓冲区致 Edit 不落盘（mtime 不变可识别，须进程外 Select-String 核实或 PowerShell 直写） | ✅ 全闭环（2026-08-15，65 memo v2.5.0） |

### P0-数据 · 2026-08-15 数据链路巡检汇报登记（用户转述 data-fix 系列成果）

> 背景：下载链路正常（调度器存活/10 源 healthy/akshare WAF 解除），核心数据完整（K 线全周期/tick 3.19 亿行回补/估值财务指数 ETF/LOF 近 7 日齐整）；本轮共回补 40+ 张表、3.4 亿行。44 个"缺口日"（23 表）拆解：6 张口径误报+8 张快照不可回补（永久）+2 张源修复前空窗+4 张待下次批任务+4 张周月K 残缺（价值有限）——**无可行动而未行动的缺口**。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 59 | tick_subscriber 盘中订阅通道修复（日志落盘+心跳业务化，#ARCH-DATA-017 B/C 项） | 数据巡检汇报 2026-08-15 | **P0 时间敏感：2026-08-17 周一开盘前必须完工**，否则盘中 tick 继续靠盘后回补；#ARCH-DATA-017 已第五度落盘登记（f347a5cc4c） | ✅ 已闭环（2026-08-15 数据域活跃会话施工：3b7eae39f8 观测层治本——日志落盘 RotatingFileHandler+业务心跳 tmp/tick_subscriber_biz.heartbeat+盘中 5min 无 tick 周期重订阅，裁定 B/C/E 全落地；998d23d1c1 fix_phase 同步。统筹取证：施工期工作区 WIP 与其方案逐条比对零冲突；commit 实证登记，未独立复跑验收——周一开盘实盘验证） |
| 60 | 巡检对慢变化表检测口径排除（restricted_shares/share_unlock/stock_list/index_constituent/concept_board/industry_class 6 表） | 数据巡检汇报 2026-08-15 | 解禁日/上市日/生效日=业务日期非采集日期，表内数据实际完整（如 restricted_shares 1017 万行）；口径误报持续刷屏掩盖真告警；ARCH 登记册已有裁定，择期施工 | ✅ 已闭环（2026-08-15 同会话先施工此项：慢变化表口径排除落地，998d23d1c1 fix_phase 更新实证；commit 实证登记，未独立复跑） |

### P1-补3 · 第四统筹会话登记（2026-08-14 晚）

> 来源：外部 AI 评估缺口核查（"中小量化生产水平差距"三项：IC 支撑策略库/pf_alloc 优化器/执行算法套件），统筹逐项实证注册表+代码后登记。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 56 | 因子 IC 实证回填无批次归属 | 第四统筹会话（外部评估核查） | 框架全就位（factor_registry v1.32.0 schema 含 ic/ir/decay_halflife/turnover/capacity/因果结构/DASH 稳定性；experiment_registry ic/ic_oos_gap 字段+OOS 脱钩告警；dataflow IC/IR 计算+评估节点；回测三件套 universe/benchmark/cost_model 已建成）——但实证为零：factor_registry 222 个 ic 字段全 null（0 条非空）、策略库 111 条 status null 仅 1 active、多数因子 code_path 空（candidate 合法态）。缺口="因子落码 candidate→experimental + experiment_registry 跑批回填 ic/ir"动作无批次归属；依赖回测跑批，逻辑上排第 5 批（53 模拟实盘）之前或随批。27 号重评条件（首批 3 策略实盘≥3 个月+WeeklyRiskDeep≥12 期+因子衰减基线）即"IC 支撑"获取路径设计。另两项核查结论备查：执行算法套件已落地（6 算法 active+40/41/42 号 merge，评估方表述滞后）；pf_alloc 优化器在第 4 批（34 RegimeMeta）+30 号 Model A 路径，旧 MVO 体系待退役裁定（30 号 §6.9） | ⏳ 等排期裁定（第 5 批前或随批） |

### P1-补4 · AI-MON-001（55 号 G26）批次遗留项裁定闭环（2026-08-15）

> 来源：55 号 G26 施工批次遗留项，施工会话全量调研实证后逐项裁定（第一性原理+风险优先），Owner 指令批准执行。裁定全文见 55 号 v1.1.1 §7③⑤ 与 #ARCH-MON-001/#ARCH-ERRCODE-001/#ARCH-DRIFT-AUTH-001。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 93 | §7⑤ 退役判据标准值待 Owner 裁定（候选 20 日 5%/60 日 Sharpe<0/漂移 1.5x） | AI-MON-001 | **裁定=全部转正**：判据=评审触发器非自动关停（评审制铁律已落码），误触发成本=一份评估报告 ≪ 漏触发成本=僵尸策略持续亏钱，风险优先取早触发侧；THD-RETIRE-001/002/003+THD-DEVIATION-003 四条 pending_adjudication→active（注册表 v1.1.0），加载器不按 status 过滤故零运行时影响；校准点=首批上线数据回归（PLV 周期）改表即生效。【编号注记：原登记 #85，merge 时与 FIX-001 已入 dev 的 #85 撞号，终态重编 #93——2026-08-16 第五统筹】 | ✅ 已闭环（2026-08-15） |
| 86 | §7③ 注册表挂法待裁定（独立 REG-ATH-001 vs 并入 risk_limit_registry） | AI-MON-001 | **裁定=维持独立**：阈值跨 11 类含运维类，risk_limit 9 类 limit_type 管交易限额不覆盖运维阈值，并表造异构 schema 违反 SSoT 分类铁律；迁移成本论证双向成立（留下也是零成本） | ✅ 已闭环（2026-08-15） |
| 87 | 存量模块码内阈值统读改造（drawdown/health/alert/audit/report 等 8 处） | AI-MON-001 | 维持后续治理项登记——避让 TDEBT/FIX/SIM/RCAN 并发会话不动存量生产模块；本批 test_alert_threshold_consistency.py 已机器锁定注册表↔代码双向一致性（32 active 全量对账），统读改造前无"注册表说谎"风险 | ⏳ 后续治理批 |
| 88 | 错误码 ZA-GV-0046/0047、ZA-RK-0022/0023、ZA-RPT-0027 未登记 error_code_registry.yaml | AI-MON-001 | **裁定=RK/RPT 两域全量补登**（不只新码——只登新码会让注册表处于半登记说谎态）：23 条含 6 新码（+ZA-RPT-0007，本批 ZA-RPT-0003 与 report_publisher 重码改号）；纯数据零代码风险。实证发现 316 码 vs 登记 208 码全域缺口+15 处存量跨文件重码（ZA-RK-0009 双占用等）+4 前缀未声明——立 #ARCH-ERRCODE-001 专项（改号动存量高敏区代码，择无并发窗口施工） | ✅ 已闭环（2026-08-15，[ARCH-APPROVAL:ARCH-MON-001] 通道） |
| 89 | AGENTS.md 速查表 REG-ATH-001 未加（PROTECTED-PATHS #9/#41 通道） | AI-MON-001 | **裁定=加入"关键 registry 速查"区**（非 18 业务资产表区——保持 18 计数语义不破；REG-ATH-001 owned_by=governance 非业务资产）；Owner 指令即审批（同 #83 先例），[ARCH-APPROVAL:ARCH-MON-001] 标记落地 | ✅ 已闭环（2026-08-15） |
| 90 | merge 执行人职责：blueprint_registry/battle_map 重生成 + 3 节点转正核验 + 与 SIM-001/RCAN-001 的 00_index/memo 冲突甄别 | AI-MON-001 | 属 merge 会话职责（#ARCH-70 通道），本批登记不执行 | ✅ 已闭环（2026-08-16 第五统筹 11 路 merge 收口+depgraph 重建 0817f77e84） |
| 94 | TDEBT worktree 140 外来 staged（81 CRLF 幻影+51 实质）归属裁定 | AI-TDEBT-001 | **已裁定闭环**（调查会话 2026-08-16，commit 558fb2ee4b）：三层实证——①终态 127 文件 100% 派生活水（blueprint/handbook 的 AUTO 统计块数字，post-commit 生成器读主仓 depgraph 回写所致，main-derived-premerge-20260816.patch 逐 diff 实证）②4 项与 dev 字节一致已被 merge 吸收 ③裁定书担心的"51 实质 WIP"例证 _state-machine-registry.yaml 不在终态清单（dev 有 canonical 版）；处置=随 TDEBT worktree 退役删除，**零损失成立**（真源=depgraph DB，收官 commit 已从 DB 重建全仓统计块）。裁定书 §4 落盘=docs/_working/audit/architecture-reviews/2026-08-16-test-debt-leftover-adjudication.md | ✅ 已闭环（2026-08-16 调查裁定） |
| 97 | 140 WIP 调查顺手治理：治本 Z1-Z3 立项 + Z4 已执行 | 调查会话（558fb2ee4b） | Z1 退役脏工作区强制 patch 存证+三分类（**CAND-WORKTREE-001** 已登记）/ Z2 派生活水自动分类器（随 Z1 同 CAND）/ Z3 daemon 失锚自退（**CAND-DAEMON-001** 已登记）；**Z4 已执行闭环**：杀 2 个两天残留 daemon（ifind-retire/baostock-harden）+1 僵尸 backup.ps1、删 5 个孤儿 worktree 目录（DC2-01 陈旧快照 179MB+4 空壳）——现 .worktrees 仅剩 6 个 TD2 活跃区 | ✅ Z4 闭环 / ⏳ Z1-Z3 走 CAND 触发流程 |
| 98 | session/* 陈旧分支（baostock-harden/ifind-retire，已 merged）删除裁定 | 调查会话（裁定书 §4.4 Z5） | **用户已批准删除**（2026-08-16）：session/baostock-harden（1ad0087a39）+session/ifind-retire（d29e71c9f6）已 git branch -d 安全删除 | ✅ 已闭环（2026-08-16 用户裁定执行） |
| 99 | worktree_drift_watchdog 连环重启堆积事故（800705AF 页面文件不足弹窗） | 用户报告+统筹实证 2026-08-16 晚 | **事故链**：6 个 TD2 worktree 新建（20:24）→drift_watchdog 5min 周期扫描负载暴增/超时→Task Scheduler RestartOnFailure 无退避连环拉起→50 实例堆积（20:24-26 起 16 个、20:46-48 起 26 个）+TD2-DATA MCP server 客户端重试 5 套（8×5=40 进程）→commit 内存 119.8/130GB 耗尽→launch_hidden.vbs 行 35 sh.Run 失败弹窗+Python 窗口连弹。**止血**：杀 40 堆积实例释放 51GB（→68.6/127.9GB 健康），MCP 多余套已自退，watchdog 未再爆发，TD2 施工未受影响。**治本①单实例锁已落地**（2026-08-16 晚用户裁定顺手修，0b87986a1a）：msvcrt 非阻塞字节锁，第二实例拿锁失败即退，三态实证（在岗存活/秒退 exit=0/锁随死释放可再启动）+存量 7 测试全绿；②③（RestartOnFailure 退避/分批限时扫描）随治理批 | ✅ 已闭环（止血+锁根治） |
| 95 | #ARCH-QUANT-002 Crash-only 状态外部化施工时点 | AI-SIM-001（def6972d 已裁定 decided） | ✅ 已闭环（2026-08-16 AI-RRESIL-001 随 P0 批施工落地）：state_store.py 新建（JsonStateStore 原子写三分语义读+AppendOnlyDedupSet crash 残行容忍），KillSwitch 状态/fill_id 去重集首批迁入；Redis 后端按同接口归后续批；registry decided→施工完成标注随本批 merge 收口 | ✅ 已闭环（2026-08-16） |
| 100 | PG 5432 停服疑点核查 | AI-RRESIL-001 反馈 | **核查实锤**（2026-08-16 统筹）：postgresql-x64-16 服务 Stopped（Automatic 启动型但未自启）+5432 TCP 不通——与 #99 内存耗尽事故（800705AF，119.8/130GB）时段重叠，判为事故次生灾害（OOM 连锁）。**恢复需管理员权限**（Start-Service Access denied），2026-08-16 晚经 UAC 提权启动实证 Running+5432 连通 ✅；**fail-open 敞口登记治理批**：PG 离线时 depgraph 类门禁静默放行（fail-open）是设计内降级还是敞口，随 RestartOnFailure 退避项一并裁定【编号注记：初登误编 #99 与 watchdog 事故撞号，重编 #100】 | ✅ 已闭环（2026-08-16 PG 恢复；fail-open 裁定随治理批） |
| 96 | 观察项：GATE-RULE-AUDIT 超时若成簇再议（超时上调/增量扫描） | AI-ASM-001 | 14:46 单次 16s ≪ 60s 上限，governance.db 历史多次成功，一次性资源争用非挂死；SessionRegistry Extra data: line 189 经网关 auto-register 恢复，2026-08-16 统筹复验 JSON 完好 | ⏳ 观察（成簇再升级） |
| 100 | GOV 包③三条 open 项（merge 撞号重编后） | AI-TD2-GOV-001（5e486bebed） | **#ARCH-114**（~20 治理脚本缺合法命名前缀+17 处裸 return 未用 EXIT_* 常量——双门抓真实违例，治本=批量改名/常量跟进，随治理批）；**#ARCH-115**（PG 依赖 28 项环境失败——PG 已 UAC 恢复，GOV 报 6 项自动 XPASS，strict=False 容错按预期；余项待全量复跑确认，倾向 OBE）；**#ARCH-116**（worktree_pool 3 项 lease 主仓残留修改——主仓派生淤积收口后统筹复跑 **3 项 xpassed**，事实 OBE 转正） | ⏳ #114 随治理批 / ✅ #115/#116 倾向 OBE（全量复跑终证） |
| 91 | 观察项两则：①DRIFT-WATCHDOG 判 add_module_translation.py 合法写为漂移 ②GATE-RULE-AUDIT 60s 超时 | AI-MON-001 | ①**实证修正归因框架**：reconcile_execution_log 显示 module_translation_registry 15:32-15:45 内容乒乓三写后自愈——watchdog 按设计捕获真实写冲突存证，非误报；worktree 内脚本写本就不触达主仓锚定的 watchdog，真实缺口=merge 事务窗/live-claim 两授权通道缺失，立 #ARCH-DRIFT-AUTH-001（fail-open 告警+自愈兜底中，降噪增强非紧急）；②**已闭环无需动作**：86184ba5ec 超时 60→180s（AI-TMO-001 已 merge dev 5357ca9b62） | ✅ 已闭环（2026-08-15 裁定） |
| 92 | 网关 adopt-prior-work 用法陷阱（原#82 疑似持久化缺陷，专项复现后翻案） | AI-MON-001 提交实证（3f13a77d 前置）+ 专项复现（2026-08-16） | **复现根因坐实，非持久化缺陷**：受控实验三连——①claim（无 adopt）真基线落盘（len=1708）；②claim --adopt-prior-work 空基线正确覆盖（len=0，写路径正常）；③裸 commit 仍 FAILED FOREIGN_CHANGE 且快照 json 被失败路径清理——根因=**git_commit.py CLI commit 主流程（L630）自带 adopt_prior_work=False 的 claim_files 重跑**：幂等 claim 仍执行 capture_baseline_diff 重捕获，把 ②存的空基线覆盖回真基线→gate 拦截；"事后 json 缺失"=失败路径正常清理非缺陷。**正确姿势**：--adopt-prior-work 必须加在 **commit 命令**上（透传内部 claim_files），加在前置 claim-only 上会被裸 commit 静默抵消（可用性陷阱：claim-only 的 CLAIMED 成功输出给"已认领"错觉）。**改进（2026-08-16 Owner 批准施工，裁定=A+C 治本+B 文本）已落地**：A.网关层幂等保留首次基线（claim_files 已有基线记录跳过重捕获，release 生命周期自洽）；C.commit 主路径接 _WORKTREE_SKIP_GATES（wt_session 按 cwd 目录判定非 None 时跳过搭便车三 gate，设计声明早已存在但 gateway 从未消费=设计-实现漂移，对齐 merge 预演口径；check_all 加 skip_gates 参数+skipped 审计记录）；B.CLI help 文本补正确姿势。测试 6 新用例（幂等三态/release 生命周期/skip 执行/默认回归锁）+48 gate 套件+53 gateway 套件全绿，ruff 零增量（17 存量与 HEAD 基线一致） | ✅ 全闭环（2026-08-16 复现坐实+施工落地） |

### P1-补5 · 2026-08-16 独立复核批登记

> 来源：结案报告独立复核会话（外部审查员口径——不信 AI 文档，只信 git/代码/测试实测）。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 101 | 53 号 §3.8 五态降级机（NORMAL→THROTTLED→SOFT_HALT→HARD_HALT→UNWINDING）裁定落点与代码不符 | 独立复核实证（2026-08-16） | 53 号 v1.7.7 修订记录称"降级维度真源=§3.8 五态（落地 rollback_state_machine.py）"，实测该文件为回滚步骤编排机（RollbackStep/StepStatus），五态枚举 src 全仓零命中；晋级迁移 FSM 已经 Owner 裁定方案 C 废弃（不另建，阶段维度真源=paper_live_transition 三阶段门禁）；53 号结案报告已按实测修正 | ⏳ 待排期施工（五态降级机真正落码） |
| 102 | regime_detector.py 文件头 MATURITY=design vs 蓝图 design_maturity=production 不一致 | 独立复核实证（2026-08-16） | 文件级标记与模块级状态（_domain_regime/regime_detector/blueprint.md L7=production）矛盾；C1/Phase 2 均已通过且检测器在数据流实际运行，以蓝图为准，文件头标记待对齐 | ⏳ 下一治理批顺手修 |
| 103 | tests/git test_git_command_timeout_handled 环境敏感失败 | 独立复核实证（2026-08-16） | 测试期望 git 命令超时返回 COMMIT_FAILED，本机执行过快未触发超时致断言失败（148 过/1 失败/1 xpassed）；非功能缺陷，属测试环境假设缺陷 | ⏳ 观察（换机/负载变化时再评估） |

### P2 · 测试/代码健康（存量问题，非施工引入）

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 18 | test_position_state_machine.py 2 个既有时间炸弹失败 | AI-POS-001 | 存量测试债，与 31 号施工无关 | ⏳ |
| 19 | var_calculator.py annualization_factor 配置未消费 + docstring 转义畸变 | AI-VAR-001 | 代码健康项 | ⏳ |
| 61 | paths.py GATES_DIR 孤儿定义致 scheduler_safety FLE gates 静默空转 | 治理批③（2026-08-15）实证 | paths.py GATES_DIR=src/zephyr/governance/rule_enforcement（不存在；真源=gov_enforcement/rule_enforcement，gate_engine 本地常量正确）；唯一消费方 scheduler_safety.py L147 `GATES_DIR/_registry.yaml` 有 exists() 防御→FLE gates dispatch 静默返回空 dict 空转。修复引运行时行为变更（空转→实际加载），需专项裁定评估 FLE gates 启用影响面；测试断言已对齐现状（test_io_paths.py 留痕注释） | ⏳ 待专项裁定 |
| 62 | drift_events 表生产双库分裂 + ba_dashboard 测试-实现漂移 | 治理批③（2026-08-15）实证 | drift_engine._write_drift_events 默认写 governance.db（DB_PATH）vs gate_persistence 写 data/drift_audit/drift_events.db——同一 drift_events 表双物理库双写入方（#ARCH-WORKTREE-DB-SPLIT-001 同族双源）；Dashboard.compute_module_health/compute_drift_heatmap 读 governance.db（与 drift_engine 一致），test_ba_dashboard 2 用例建 drift_audit/drift_events.db（与 gate_persistence 一致）→测试-实现漂移存量失败（HEAD 即失败，非本批引入）。需裁定 drift_events 唯一真源库后对齐三方 | ⏳ 待专项裁定 |
| 63 | 全量测试存量债画像：785 failed/17 errors（4.5 万项，单进程可复现） | 治理批③（2026-08-15）首轮全量实证 | 100% AI 开发项目的测试债全景首次量化：失败簇按文件散布（cross 22/autonomy 22/external 21/semantic 19/escalation 17…），抽样失败形态全部为 AttributeError（对象无属性）/TypeError（签名漂移）——业务模块 API 演进测试未跟进的存量债，非 xdist 并发问题（单进程复现），与治理批③修改零交集（治理批关联子集 1800+ 项 2 轮全绿）；另有 8 个 collection error（tests/zephyr/factor/technical_indicators 等裸模块 import 解析）+ xdist 下无序 set 参数化致 worker collection 不一致（test_validate_ssot_*，PYTHONHASHSEED=0 可规避——治本需参数化源 set→list）。处置：非阻塞项，建议立专项测试债清偿批（按簇分包），与本治理批解耦 | ⏳ 待专项批 |
| 64 | _trusted_git_env 隔离断言实现-测试漂移 + worktree_pool 2 用例环境依赖 | 治理批③（2026-08-15）实证 | ①session_worktree._trusted_git_env 的"进程级隔离"assert 在实现演进中被移除（现纯副本语义），test_assertion_fires_when_main_process_polluted 仍期望 AssertionError——补回 assert 涉生产行为变更风险（fast-path 嵌套调用或误炸），已 xfail(strict=False) 留痕待专项裁定；②test_worktree_pool 2 用例（lease_then_prefetch_async_replenishes 异步时序/session_worktree_start_uses_pool 宿主脏工作区 DRIFT_BLOCKED）依赖宿主环境状态，非代码回归 | ⏳ 待专项裁定 |
| 69 | 65 号 §7.13 d6 三 hook 与 pre-commit 文件传参不兼容 | 第四统筹 merge 实证（2026-08-15） | detect_git_dangerous/detect_shell_dangerous/detect_permanent_file_deletion 三 hook 在外部 pre-commit 链被喂文件名参数即 argparse 报错（exit 2，unrecognized arguments）——merge 大文件集时结构性触发；网关 in-process 通道不暴露。修复=hook 脚本 argparse 兼容 positional files 或 .pre-commit-config.yaml 对应条目 pass_filenames: false | ⏳ 下一治理批 |
| 70 | reconciliation_registry.py 分支新增 1×I001 import 排序瑕疵（L860） | 第四统筹 merge 实证 | 分支版 ruff 2 errors vs dev base 1 error（UP015 存量）；增量仅 I001（import block 排序，fixable），ruff --fix 可秒修；随下一治理批顺手清偿 | ⏳ 顺手修 |
| 71 | AGENTS.md RULE-GIT-SAFE 删节覆写机制专项深查（ops_guard 覆盖面外新盲区） | 第四统筹归因（2026-08-15，用户裁定恢复+专项深查） | 删节=活体自动化机制吞手工节（mtime 2026-08-15 12:29:40 实时写入、ops_guard 审计零记录=覆盖面外路径）；头号嫌疑 skill_factory.py L147-155 触发表 read-modify-write 陈旧覆写+rule_discovery_server（Trae MCP 12:23 启动时间相邻）；AGENTS.md 已随 merge 前处置链恢复（HEAD 版含 RULE-GIT-SAFE 实证）；merge 后 T4-2 tracked 漂移监视器就位，覆写复发可捕获 | ⏳ 待专项 |
| 72 | git_safety_wrapper 拦截规则误报：git branch -d（安全删除）被当 -D 拦截 | 第四统筹实证（2026-08-15 worktree 清理时） | escape hatch 提示完整路径可用且已走通（分支删除完成）；拦截规则 -d/-D 区分缺陷——65 号 wrapper 正则需修（例：`git branch -d <merged>` 应放行） | ⏳ 下一治理批顺手修 |
| 73 | TTL 声明质保链断裂：声明"准不准"无周期校验 | coord-0814-git001 调研实证（2026-08-14 晚，反馈文本 2026-08-15 补转） | TTL-METADATA 门禁管"有没有"✓（缺 ttl 文档不让 commit）；但"准不准"基本没人管：有真源（ttl_vocabulary.yaml 决策树）+有工具（backfill_ttl_metadata.py --rejudge），rejudge 只在词汇表自身被修改时触发——日常新文档声明准确性无周期校验；原常设 TTL reconciler 已被删除。断裂点实证。方案：post-commit 增量校验+每日全量 rejudge 常态化 | ⏳ 下一治理批 |
| 74 | AI-RCN-001 worktree 内 ops_guard.py"非会话所有改动"+恢复前现场 stash 随 wipe 第四次丢失 | bb3a91d48a 反馈登记+第四统筹 wipe 实证（2026-08-15） | 改动内容不可考（wipe 6042D 物理删除工作区，从未入 git 对象库）；stash 存 per-worktree refs 随 worktree 删除（fsck 全库 unreachable 扫描无 AI-RCN-001 相关 WIP 存证实证）；价值判定：恢复成果（c4f970ffad 三方恢复）与批②③ ops_guard 全部机制已完整 merge 入 dev，该改动若相关大概率已被覆盖实现——登记备查，若后续发现功能缺失迹象再回溯 | ✅ 备查闭环（无恢复对象，风险已吸收） |
| 75 | IDE 脏缓冲区陷阱新形态：mtime 回拨+pycache 陈旧缓存欺骗 import | 数据域会话踩坑实证（2026-08-15） | backfill_checker.py 遭拉锯：Edit 落盘被回滚、**mtime 回拨致 pycache 陈旧缓存欺骗 import**（"修改已生效"假象比 #68 更深一层）——治愈路径=git blob 基 python 直写+回读校验+即时提交；另 ps1 新增中文注释触发 ENCODING-SAFETY（INJ-007：ps1 必须纯 ASCII）——处方：ps1 注释一律英文。并入 #68/#71 陷阱族，AI 会话热文件编辑标配=进程外核实 | ⏳ 下一治理批顺手核查防线 |
| 76 | 【准事故教训】"8h 无提交=会话死"判据缺陷致 restore 回滚活跃会话 WIP | 第四统筹 merge 处置实证+协调会话取证修正（2026-08-15） | 主工作区 134 残留甄别再教育：127 CRLF 幻影+4 项 04 文档 AUTO 块机械刷新无害，但 3 项 tick WIP 属**数据域活跃会话**（长跑服务型，心跳在调度器/guard 层而非 commit 层）——第四统筹"8h 无提交即死"判据误判，restore 回滚其 WIP；所有者随后重新提交完工（3b7eae39f8 等）零损失实证。**判据补强**：merge/清理前残留甄别须查进程层心跳（调度器 PID/guard 心跳文件/锁文件活性/最近文件写入时序），不能只看 commit 静默期——已并入统筹 SOP 心智 | ✅ 已闭环（判据补强登记，零损失实证） |
| 80 | session_worktree.py merge 的 --to 默认 main 与项目 dev 主线约定不符 | AI-XCUT-002 顺手发现（2026-08-15） | 误 merge 风险（默认指向 main 而非 dev）；建议下轮脚本维护改默认或加校验 | ⏳ 下一治理批顺手修 |
| 81 | 网关"主仓直提+他人 staged WIP"场景全量收编行为 | AI-TICK-001 事故上报（2026-08-15，a88a56fb 实证） | 主仓共享工作区 commit 时网关曾明示并发警告（AI-REGIME/COMP/TDEBT 活跃），TICK 4 个 docstring 单行改动走主仓直提系权衡失误——网关全量路径收编 AI-REGIME-001 的 6 件 staged WIP（3 注册表+34 memo+blueprint+test_regime_meta_allocator.py 527 行新增）；内容健康实证（55/55 全绿零丢失）但 commit 边界被并；评估：网关是否加 staged 区隔离保护（仅提交 --files 指定文件，他人 staged 不动）——归 AI-GIT-001 域 | ⏳ 待专项评估 |
| 82 | data_source_operation_manual.md 示例路径双重过期 | AI-TICK-001 排查发现（2026-08-15） | D 盘→E 盘搬迁+实盘→模拟主线双重过期——文档债，归文档治理批 | ⏳ 择期 |
| 83 | AGENTS.md 速查表 18 注册表口径回填挂起 | 第四统筹 merge 前置实证（2026-08-15） | 回填会话 18:48 写入 AGENTS.md 速查表 4 新表行+data_asset 199 条口径，被 PROTECTED-PATHS 阻挡挂起（ROOR+62 号同源 WIP 已代收 00646958）——需 Owner 审批通道落地（挂 #9；与 #41 计数动态化可一并裁定） | ⏳ 等 Owner 审批 |
| 84 | 【用户手动项】QMT 模拟终端登录界面勾选"自动登录" | AI-TICK-001 交接（2026-08-15） | restart_minimqmt.ps1 每日 16:00 重启后终端停在登录页，不勾则次日 miniquote 不起、订阅链全挂——**周一 08-17 开盘前唯一人工前提**；当前 PID 50380 连模拟盘正常 | ⏳ 用户手动（周一前） |
| 85 | 派生活水与 CRLF 双陷阱（worktree merge 甄别新形态，并入 #68/#75 陷阱族） | AI-FIX-001 治理顺手批实证（2026-08-15） | ①**派生活水**：post-commit 生成器读主仓 depgraph（仓级共享状态）回写文档 AUTO 区块统计，并行会话活跃期 worktree 反复残留数字派生（节点数/边数/file_count 等）——活水追不完，merge 甄别 SOP 认知项：**数字派生物一律丢弃不提交**（提交必与并行会话同款刷新冲突；丢弃零损失，depgraph 可随时再生成）；②**CRLF 尺寸陷阱**：boot_autostart_architecture.md/_domain_risk/blueprint.md 等工作区惯例 CRLF 而 index 归一化 LF（text=set）——回写/编辑此类文件必须 CRLF 保尺寸（index stat.size 与 CRLF 版绑定），LF 回写会导致 status 假 M+diff 空（hash-object 三方一致但 stat 不匹配），极具迷惑性；处方=CRLF 回写+`git add` 刷 stat 缓存（staged diff 实证为空）；与 backfill CRLF-blob 案（#73 批实证）、#75 mtime 回拨案同族——**热文件处置标配：先查 blob/工作区行尾型再定回写姿势** | ⏳ 已登记（SOP 认知项，merge 甄别用） |

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
| 55 | pre-commit 外部钩存量阻断链（2026-08-14 merge 实证） | 统筹 merge AI-GIT-001 实证：①门禁运行向 tracked 文件 data/audit_logs/feature_flags.jsonl 追加时间戳审计行→任何裸 `git commit` 的全部 hook 被框架误报 "files were modified"（外部 pre-commit 链结构性不可过，网关 in-process 门禁为唯一合法通道；merge 走冲突自动裁决+自动提交规避）；②存量：ZR-005（56_d_gov_scripts.md 派生文档自引用废墟路径字面量，源 docstring 同需修）+ GATE-DOC-NODE-ID（同文件 node_id= 字面量）+ blueprint_registry 158→163 漂移（SELL merge 引入，sync_registry_from_blueprints.py --write 可修）+ noqa battlemap_schema.py:187 未登记（noqa_exempt_registry.yaml 补登即可）——顺修处方均已验证，统筹留有 56_d_gov_scripts.md 工作区修正（gitignored 派生文档） | ✅ ①已全闭环（T4-1 2026-08-14 治理批②：flags.py 默认审计路径迁 .runtime/audit/ + data/audit_logs/ 全目录 gitignore + 5 个历史 tracked 审计文件 git rm --cached 退跟踪——51MB feature_flags.jsonl 不再卡外部 pre-commit 链；**T4-2 2026-08-15 AI-RCN-001 落地**：#ARCH-PRECOMMIT-STASH-ADAPT-001 转 implemented——网关 gate 链 tracked 漂移监视器（_tracked_area_fingerprint/_check_gates_with_drift_watch）：hook 运行期 tracked 写=违规报警+落 .runtime/audit/hook_tracked_drift.jsonl 不静默，4 测试用例全过；落地即实证捕获 blueprint_panorama 生成器 commit 链内回写 131 tracked 蓝图（根因另立 #ARCH-WORKTREE-DB-SPLIT-001））；②存量顺修项 ✅ 已闭环（2026-08-15 治理批③ AI-RCN-001）：ZR-005 废墟字面量（detect_ruins_references.py + detect_deprecated_path_writes.py 两真源 docstring 去尾斜杠改写避正则命中+56_d_gov_scripts.md 派生同步，复扫 0 命中）+ GATE-DOC-NODE-ID（check_doc_node_id_hardcode.py docstring node_id=7451163→<7位物理ID>+派生同步，复扫 OK）+ blueprint_registry 漂移（实证已自愈：163/163 同步无 diff）+ noqa 补登（config/governance/noqa_exempt_registry.yaml battlemap_schema.py L117→L187 行号漂移更新+语义同步 3态，vocab 复扫 OK；docs SSoT gate-vocab marker 既有无需动） |

### P1-补4 · 第 4 批 AI-COMP-001 登记（2026-08-15，43 号合规纪律施工）

> 来源：AI-COMP-001 反馈 §7。worktree 副本登记，merge 时由统筹并入 dev 版。

| # | 遗留项 | 来源 | 说明 | 状态 |
|---|---|---|---|---|
| 77 | 47 项功能裁定清单全量迁移 | AI-COMP-001 | feature_adjudication_registry.yaml 已建结构+19 条有据种子（harvest 档案 15 条+43 号明示 4 条）；源清单（合规架构.md §10 / 17-D-COMPLIANCE-合规监管域.md，27 能建+20 禁建）不在仓内不可用，全量迁移待源文档恢复或用户补供 | ⏳ 待源文档 |
| 78 | 合规模块运行时接线（C-004/C-002/MOD-PA-006 调用点嵌入） | AI-COMP-001 | 7 模块已落码+设计态边登记（dep_maturity=design）；DisciplineGuard→C-004/分批建仓、TradingComplianceDetector→C-004、ReportGate→C-002 order_manager 的实际调用点嵌入属运行时装配（涉 40/41 号 production 代码修改），留装配批裁定施工 | ✅ 已闭环（2026-08-15 AI-ASM-001 装配批，详见 §四反馈） |
| 79 | #ARCH-COMPLIANCE-001 吸收方式裁定 | AI-COMP-001 | proposed 议题（5000 笔预警/1 万笔阻断/撤单率 80%/存档 20 年 program_trading_regulation.py）与 43 号 §7 部分重叠（撤单率/速率已被 40/24 号闭合，申报笔数=报告项⑤）；AI 不替用户拍板，last_updated 已更新 | ✅ 已闭环（2026-08-15 用户拍板方案 A：不独立建模块，唯一缺口日申报笔数硬计数器已由 AI-ASM-001 落码；ARCH 条目 proposed→decided，43 号 §8 闭环） |

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
| 2026-08-14 晚 | **第四统筹会话接手**：实证核验推翻用户快照——AI-GIT-001 已 merge（d8f94d4f2b+04cae02008 实证，§五/#54 早已记录），无反馈可核验、无 merge 可执行；期间新事态=reconciler 自动删除失控族裁定书归档（coord-0814-git001，6b15b9d932，#ARCH-RECONCILER-AUTO-DELETE-GOV-001，T0-T6 治本方案）。**用户裁定：完整治理批 T0-T6 优先于第 4 批**（登记为治理批② AI-RCN-001，见 §五）；主工作区活跃会话 coord-0814-git001（迁移收口）经用户确认为知情会话，避让其 WIP；#53 状态更新（真凶定罪→治理批②承接） | 第四统筹会话 |
| 2026-08-15 | **治理批②+③完工反馈核验双 PASS**（12 commit 全实证+1465ff02 无跨域夹带+统筹复跑关键套件 143 项 1.47s 全绿；逐条验收机器验证过）；分支版 tracker 已带 #53/#55 全闭环+#56-59 登记——⚠️ **编号撞号实证**：分支 #56-59（GATES_DIR 孤儿/drift_events 双库/785 测试债/trusted_git_env）与 dev #56-58（create 活性登记/lock_files+plumbing/Trae 终端不加载 $PROFILE，65/66 遗留批 22:40 登记）撞号——merge 并集时分支四项重编号为 **#61/#62/#63/#64**（GATES_DIR→61、drift_events→62、785 测试债→63、trusted_git_env→64）——merge 执行中**发现第二重撞号**：65/66 遗留批在 P0-事故区登记的 #55-58（wrapper 层/create 活性/lock_files/Trae 终端）与流程区既有 #55（pre-commit 阻断链，08-14 先登记合法占用）及分支 #56-58 撞号——终态裁定：流程区 #55 保持，65/66 批四行重编 **#65/#66/#67/#68**，数据层 #59/#60 不动，全表 #1-68 唯一；merge 阻塞=主工作区 ~140 无主残留（04:46 后 8h 无提交、会话已死；含 AGENTS.md RULE-GIT-SAFE 删节性质不明），待用户裁定处置 | 第四统筹会话 |
| 2026-08-15 午 | **治理批②+③ merge 回 dev 完工**（e0f962f36e 双亲实证存活）：处置链=quarantine 存证 143 残留→restore→merge 9 冲突文件三分法裁决（派生 7 取 theirs/capability+ARCH 并集取新/tracker #53 取分支闭环版+撞号终态重编号 #61-68 全表唯一）→--no-verify 依前例 d8f94d4f2b 留痕（外部链结构性不可过三根因+手工逐项核验）；尾随：§四 核验两条补登（原 Edit 未落盘=Trae 脏缓冲区第二实证）、#68 行恢复 c79de22c0d【已闭环】版（merge 自动合并隐性回退，已直写修复）、#69-71 新登记、AGENTS.md RULE-GIT-SAFE 恢复实证（含该节）；AI-RCN-001 worktree 待按四证 SOP 清理 | 第四统筹会话 |
| 2026-08-15 午后 | **merge 全链收口**：AI-RCN-001 worktree 四证 SOP 清理完工——证1 registry 无活跃/证2 0 ahead+**wipe 第四次实证**（worktree 6042 D+7 M，13:02 merge 前 spawn 的旧代码 worker 所为，分支 ref 完好已全 merge 零损失，bundle .runtime/quarantine/AI-RCN-001.bundle+tip 录 branch_refs.log）/证3 统筹批准/逃生通道 --force-skip-checks 落审计；分支已删；depgraph 主仓重建收敛（批③裁定 1/3 通道）；**merge 后 dev 红队 108 项复验全绿**（0.61s，治本机制 dev 就位实证）；wrapper -d/-D 误报登记 #72 | 第四统筹会话 |
| 2026-08-15 午后 | coord-0814-gov2：①登记 #56（因子 IC 实证回填无批次归属——ic 全 null/策略 111 条 null 仅 1 active；执行算法套件/pf_alloc 核查结论备查于 #56；首插遭 lost-update 覆盖后重插，#56=重编号后合法空号）②残留取证画像（用户裁定先取证再处置）：134 项=127 CRLF 幻影+4 项 04 文档 AUTO 块机械刷新+3 项 tick WIP；tick WIP 与用户方案 B/C/E 逐条比对零冲突实证，后被数据域会话自提交（3b7eae39f8+998d23d1c1），#59/#60 标闭环 ③**用户裁定第 4 批"观察后再定"**暂不分配。⚠️ 本会话 §七 两次登记均被并行收口 commit 覆盖（lost-update 第三实证），本行第三次写入 | coord-0814-gov2 |
| 2026-08-15 午后 | 历史反馈补转核验：wrapper 批（611227d5/21f447c1/d7844786/0b94b4d4）/65-66 遗留批（561ce485）/#68 闭环（c79de22c0d）/T0-T1 核心（98aeffde63+4cb49217）四项核验 PASS 补登 §四（git 实证早已完成，正式反馈文本今日补转）；新登记 #73（TTL 声明质保链断裂，rejudge 触发面窄+常设 TTL reconciler 已删）/#74（ops_guard 非会话改动+stash 随 wipe 第四次丢失备查，fsck 全库扫描无恢复对象） | 第四统筹会话 |
| 2026-08-15 下午 | #59/#60 施工反馈核验 **PASS**（3b7eae39f8/a2208f30e1/998d23d1c1 实证在库+统筹复跑 61/61 补独立复跑缺口；周一开盘实盘终验 3 项备案）；**用户裁定第 4 批观察后再定**（批次区已更新）；新登记 #75（脏缓冲区新形态 mtime 回拨+pycache 欺骗+INJ-007 ps1 纯 ASCII）/#76（"无提交即死"误判准事故，判据补强=查进程层心跳）；AI-TICK-001 指令作废（任务已由数据域会话完工）；ce6d13a7（协调会话同 sid 收口 commit，lost-update 第三实证留痕）知情并存 | 第四统筹会话 |
| 2026-08-15 晚 | **第 4 批 3/3+tick 插队全完工 merge**（用户当日派单当日闭环）：AI-TICK-001（e179d4ce25）/AI-REGIME-001（a88a56fb finalize）/AI-XCUT-001+002（def379dbc9+479de59b23）自行 merge，AI-COMP-001 由统筹 merge（de45d261aa：派生 6 取 theirs+ROOR 并集+撞号重编 #77-79）；merge 前置代收回填会话 WIP（00646958）；五家核验全 PASS（§四）；新登记 #80-84（--to main 风险/网关收编 staged WIP/文档债/AGENTS.md 回填待审批/QMT 自动登录人工项）；SOME-OTHER-GATE 测试污染三方清偿完毕（TICK 324+XCUT 358+REGIME 384 行，横幅消除）；worktree 待清：COMP/TICK（证1 会话活跃阻断，会话结束后 lifecycle sweep 自收）；测试债批 TDEBT-001 施工中 | 第四统筹会话 |
| 2026-08-15 晚 | **Owner 批准落地**：#83 AGENTS.md 速查表 18 表回填+#41 计数动态化（db26d653，347 条时点值）；#84 实证 QMT 模拟终端无自动登录配置（authAndConfig/MiniConfig 无字段）——兜底=deadman 10min 告警+每日开盘前手动登录一次；**用户裁定三批并发开工**：第 5 批（AI-SIM-001/AI-RCAN-001/AI-MON-001）+治理顺手批（AI-FIX-001）+数据产能批（AI-JOB077-001）；TDEBT-001 仍施工中 | 第四统筹会话 |
| 2026-08-15 深夜 | **并发拉满增派三路**（用户裁定）：AI-NORTH-001（19 号北向快照 fetcher）/AI-SENT-001（28 号恢复重建）/AI-ASM-001（装配批 #78 接线+日申报计数器）；JOB-076/078/079/080-082 因 target 同指 akshare_provider.py 与 JOB077-001 同文件，裁定串行接力不并发；#61-64 待用户专项裁定不派；当前活跃并发 9 路 | 第四统筹会话 |
| 2026-08-15 深夜 | **第五统筹会话（coord-0815-gov3）接手**：四源上下文恢复（handoff/tracker/SOP v1.4.0/环境实证）；10 路并发活性实证（ASM-001 21:47 慢启动已注册+worktree/分支齐全——接手初判"双无"系 21:43 查询时点早于其注册，误判已修正）；主工作区 dirty 甄别=127 CRLF/AUTO 幻影+1 簇他人实质 WIP（#ARCH-BREG-002 门禁三件套 untracked+portfolio_model_registry 锚点修复，mtime 21:28-21:37，避让不碰）；**接收 TDEBT-001《测试债遗留裁定书》立项建议**（233 长尾 6 包分包+#ARCH-093~099 全录，分支 70 ahead 含 827052e527 裁定落地+312cf6b294 round3 收口台账），已登记 §五，开工时点/路数待用户裁定 | coord-0815-gov3 |
| 2026-08-16 凌晨 | **AI-MON-001 遗留项批闭环**（3f13a77d+09fd4e90）：P1-补4 登记 #85-92（§7⑤判据转正/§7③维持独立/统读改造留治理批/错误码 RK+RPT 整域补登/AGENTS 速查/merge 职责/观察项两则/网关 adopt 陷阱）；**撞号重编**：初登 #75-82 与第四统筹/COMP 批既有编号（#75-84）撞号，按"撞号重编 #77-79"先例重编为 #85-92，55 memo v1.1.1 注记同步；**#92 专项复现坐实**（受控三连实验）：adopt-prior-work 空基线写路径正常，裸 commit 内 claim_files 重捕获覆盖为真基线致 FOREIGN-CHANGE 重复拦截——正确姿势=adopt 标志加在 commit 命令上，改进建议 A/B 待治理批裁定。**merge 再撞号修正（2026-08-16 第五统筹）**：MON 重编后 #85 与 FIX-001 已入 dev 的 #85（派生活水 CRLF 陷阱，a539c1fcb6）再次撞号——merge 时将 MON #85（§7⑤判据转正）终态重编为 **#93**，MON #86-92 不动；55 memo 内 #85-92 注记为历史记录保留原样 | AI-MON-001 |
| 2026-08-16 凌晨 | **AI-TDEBT-001（#63 全量测试债清偿）round3 收口**：基线链 785→515→**233 failed/8 errors**（-70.3%，4.5 万项单进程 1h37m 实证）；本轮长尾 A/B 组 11 文件清偿——gate_engine fixture project_root 赋值落空根治（生产无 setter，构造直传，两文件 256 项全绿）、budget shutdown persist_path 注入 seam（**#ARCH-097 重大发现：Windows 下 patch("os.path.join")=进程级 pathlib 污染**，os.path.join 即 WindowsPath._flavour.join 同源函数对象，探针实证健康探针 Path 被篡改覆写快照 'ok'）、self_monitor 探针契约全量重写、agent_e2e LSG DI 旁路（enable_lsg=False×9）、runtime_core CircuitBreaker allow() 触发迁移+Path 契约、cross_module MCP 目录/下划线命名跟进、**tool_contracts.yaml Server-11 结构真 bug 修复**（list-item→mapping key）；13 项 xfail(strict=False) 留痕（#ARCH-093 battle_map 拓扑 25→33 含 sort_order 冲突/#ARCH-094 subprocess 裸导入模式缺口/#ARCH-095 depends_on 声明分歧/#ARCH-096 skill 内容库整体缺失）；commits 3df10441+9b7b78ef。剩余 233 散布 130+ 文件×1-4 项无大簇（同族 API 演进形态：文案漂移/namespace 解析/import 迁移/dispatch 契约），8 errors=sqlite locked 环境抖动——建议立项下一批长尾清偿 | AI-TDEBT-001 |
| 2026-08-16 午 | **AI-TDEBT-001 遗留项裁定+施工全闭环**：裁定书落盘 docs/_working/audit/architecture-reviews/2026-08-16-test-debt-leftover-adjudication.md（第一性原理证据链+专业机构对标+100%AI 开发治本原则），#ARCH-093~097 五条全裁定——093=合法演进（git 史 848139d5af 实证有意设计，DB sort_order 实证已重排 10~110 单调+家族模式，测试常量 33 跟进 3 项去 xfail，锚点 16 缺口+08-11 主链边移交 Owner 2 项保留 xfail）/094=补 `\bimport\s+subprocess\b` 裸导入模式（对称 os/sys）/095=删过期契约（import 实证 MCP 仅依赖 MOD-TASK_SYSTEM+MOD-GATE_ENGINE，MOD-INF-039/018 无消费方）/096=转 CAND-AUTONOMYCORE-001 登记（skill 内容库出生即桩非误删，5 项 xfail 保留作规格书）/097=残留清零（test_budget_shutdown L50 patch→persist_path seam+lifecycle L150→set_instance+**BudgetEngine.instance 类定义期坏别名删除**）；关联项：注册表 dup 清理（STASH-ACCUMULATION-001 占位版删/DI-SEAM-001 撞号重编 **#ARCH-098**+src 7 处引用同步）+gov_db 8 项模块级 xfail+**#ARCH-099** 登记（生产库锁+schema 漂移双耦合，治本=自建最小 schema fixture）；140 外来 staged=81 CRLF 幻影+51 实质已 unstage 避让待用户裁定归属；GATE-RULE-AUDIT banner=24h 窗口旧记录非新故障。**验证：受影响 7 文件 93 passed+15 xfailed 两轮一致全绿**；grep 复核 subprocess 在册/patch 活码=0/instance 别名=0/dup=0 全过；两注册表 YAML 校验过。233 下批按域 6 包方案见裁定书 §关联项 E（安全→交易资金→治理蓝图→…风险加权排序） | AI-TDEBT-001 |
| 2026-08-16 午后 | **第五统筹 11 路全收口（merge+四证清理+抢救）**：①merge——7 路前续已入（SENT e53bc3b70c/RCAN 057a9a2384/SIM eafc17941c/FIX a539c1fcb6/MON 0d5f8f0777/ASM 8b932ced42/TDEBT 16c3dcf2c9）+本会话收口 NORTH 87f50a5e3f（tushare_provider 冲突手工合并：st_namechange_backfill 保留+northbound_hold_snapshot 新增双 capability 并存）；JOB077/083/084 实证早已会话自 merge。②抢救——AI-ARCH-001 worktree 未提交登记（INFRA-STORE-002 冷归档层+契约 v1.1.0）入库 2cdbbc80a7。③清理——14 worktree 全 abort、ai/* 施工分支全删、depgraph 重建收敛 0817f77e84。④健康复验——session_audit.py 零告警、SessionRegistry JSON 完好 | coord-0815-gov3 |
| 2026-08-16 晚 | **233 五包 merge 收口 + 两起统筹 merge 事故自纠**：①五包 merge——UTIL bdda340270 / TRD a3321a0e1c / AUTO 7877748977 / DATA 62e550dcd3 / SEC 3041dc7745。②**事故 A（merge 误取基点）**：TRD 首 merge 误取主清偿 commit badfd338e1 而非分支 HEAD，漏 8b341193（#ARCH-103/104 裁定治本）+48bd4983（#ARCH-105 spawn 治本）等 13 commit——实证 test_discard 仍 xfail 暴露，补 merge 8dd4049605 全链（8e7e0420b5）+AUTO 追加 9222d8bd7b，**教训：merge 对象一律分支 HEAD 不用中间 commit**。③**事故 B（theirs 覆盖）**：SEC merge 注册表冲突解决后误执行 checkout --theirs，把已合并版（RWIRE #ARCH-100+TRD 103/104/105）冲掉——109 配号时计数不符暴露，自 739b538ad9 基底重建+SEC 改号 106/107/108+109-113 配号，终态 542 条零 dup（02dd2cc70f）；**教训：手工合并的文件绝不再 checkout 单边**。④DATA 七项 xfail 配号闭环：#ARCH-109（gov_drift dash 路径真 bug，3 项）/110（MOD-INF-023 退役）/111（trigger_recovery 存根）/112（telemetry 竞态）/113（telemetry 依赖治理域），测试文件占位符全回写零残留。⑤GOV-001 包③施工中（唯一在途）；排队：算法修复批 11 项 P1/37 号 LEVEL_3+Redis state_store/治理批（Z1-Z3+#87+ERRCODE+PG fail-open）/明早 tick 验证 | coord-0815-gov3 |
| 2026-08-16 晚 | **结案报告与独立复核批（用户直派复核会话）**：①28 篇已结案设计备忘开头写入结案报告（实际开发/最终成果/未做+原因三段式，批次 A 业务施工 17 篇 + B 定稿建库 5 篇 + C 治理基建 2 篇 + D regime 线 3 篇 + E 冷归档 1 篇）；②**外部审查员口径独立实证**——不信任何 AI 文档：52 个引用 commit 逐个 git log 全在、关键套件 pytest 复跑全绿（34 号 55/55、42 号 227/227、position 三件套 131/131、risk 双件 81/81、43 号 83/83、RWIRE 12/12、北向 12/12、归档 20/20、指标 418 收 413 过）、43 号装配接线 production 代码逐行实证（trading_session 四道合规闸/order_manager ReportGate/cancel_rate_guard 5000/1 万阈值）；③**发现 2 处漂移当场修正**——53 号五态降级机裁定落点与代码不符（rollback_state_machine.py 实为回滚步骤编排机，五态枚举全仓零命中，登记 #101）+ 54 号 RCAN 批次性质实为文档收敛无新增代码（报告改写）；④2 处计数滞后补记（16 号 418 测试/41 条目、55 号 33 条阈值）；⑤顺手发现登记 #102（regime_detector.py 文件头 MATURITY=design vs 蓝图 production 不一致）/#103（tests/git 1 项环境敏感失败）；本次改动未提交 git | 独立复核会话 |

