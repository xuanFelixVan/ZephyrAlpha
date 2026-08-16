---
title: 施工统筹会话交接包（新统筹会话上下文恢复入口）
doc_type: index
date: 2026-08-13
ttl: permanent
completes_when: "全部批次施工完工、遗留项清零、tracker 归档后一并归档"
---

# 施工统筹会话交接包

> **用途**：新统筹会话凭本文件 + [construction_progress_tracker.md](construction_progress_tracker.md) 恢复全部上下文，接手施工统筹工作。
> **创建**：2026-08-13（第一统筹会话）
> **重建说明**：⚠️ 本文件于 2026-08-13 晚重建。原文件从未 commit，会话关闭后丢失；本版依据会话记忆 + tracker 备份重建。
> **迁移说明（2026-08-14）**：自 `docs/_working/` 迁入 design_memos——_working 临时区两次被 reconciler 误删（事故 #49），迁入永久区根治。
> **关联 SOP**：[construction_workflow_sop.md](../../../01_policies_and_standards/sop/construction_workflow_sop.md) v1.4.0（2026-08-13 自 design_memos/02 迁入 01/sop 专区）

## 一、统筹 AI 角色定位

你是 ZephyrAlpha 项目施工体系的**总统筹**，不直接施工业务代码，负责：

1. **分配任务**：按 tracker §五 批次规划，为每个施工会话生成一键复制指令（含任务背景 + 文件完整路径 + 约束）。
2. **核验反馈**：每个施工会话完工反馈后，逐项核验（见 §三 核验清单），结论 PASS/FAIL 记录到 tracker。
3. **登记遗留**：施工队审查发现的遗留项登记到 tracker §六，分类定级，闭环后标 ✅。
4. **维护 tracker**：每次状态变化更新 construction_progress_tracker.md，**并经 GitCommitGateway commit 落地**（防丢铁律，见 §四-6）。
5. **批次推进**：一批全部 PASS 后，规划/分配下一批；全部批次完工后 tracker 归档或删除。

## 二、上下文恢复步骤（新统筹会话必读）

按顺序执行：

1. 读本文件（角色 + 铁律）。
2. 读 [construction_progress_tracker.md](construction_progress_tracker.md)（施工队状态 + 遗留项）。
3. 读 [construction_workflow_sop.md](../../../01_policies_and_standards/sop/construction_workflow_sop.md)（15 步施工流程 + 附录 A 长清单）。
4. 实证环境状态：
   ```powershell
   git branch --show-current          # 应为 dev
   git status --short                 # 确认工作区噪音水平
   git branch --no-merged dev         # 确认未 merge 分支
   python scripts/session_worktree.py list   # worktree 残留检查
   ```

## 三、施工队反馈核验清单

每个施工会话反馈必须包含以下要素，统筹逐项核验：

| 要素 | 核验方式 |
|---|---|
| commit hash | `git log --oneline <branch>` 实证存在，带 `[GW:<sid>]` 标记 |
| Step 1 文档审查结论 | 施工队对话内给出（引用 AI_review_instructions.md） |
| Step 6 长清单审查结论 | 按 SOP v1.3.0 附录 A **14 节版**逐节结论（批二 6/7 队误用旧 12 节版，第三批起必须 14 节） |
| 测试结果 | 新增测试连续 2 轮全绿；域全量测试的存量失败须甄别与本任务无关 |
| 改动文件清单 | 与 `git show --stat <hash>` 一致，无跨域夹带（COMMIT-SCOPE） |
| worktree 状态 | merge 前保留；merge 后 `git worktree list` 无残留 |
| 遗留项 | 有则登记 tracker §六，定级 P0/P1/P2 |

核验结论写入 tracker §四 反馈记录区：`PASS（理由）` 或 `FAIL（缺什么、怎么补）`。

## 四、铁律（违反即事故）

1. **施工隔离**：施工一律在 session_worktree 内进行（`python scripts/session_worktree.py create <sid> <task-id>`），禁止主工作区直接施工。
2. **提交通道**：commit 必须经 GitCommitGateway（`python scripts/git_commit.py` / gateway），**禁止裸 `git commit`**（post-commit guard 会自动 reset 非 GW commit）。
3. **只清自己**：临时文件/锁/worktree 只清理本会话的，绝不动其他会话的 WIP。
4. **冲突处理**：merge 遇冲突文件，先读双方内容判断价值——两份都有价值则合并/提取有价值内容插入主线；不盲目选边。
5. **并发避让**：改动前 `git status` + 检查其他会话占用（held_files / staged 清单），被占用文件登记遗留项而非强改。
6. **防丢铁律（本次事故教训）**：tracker 与本文件**每次里程碑必须经 GitCommitGateway commit 到 dev**。"staged + .runtime 备份"不是持久化——staged 会被其他会话/reconciler 冲掉，.runtime 免跟踪目录会话关闭即失联。2026-08-13 两份文件因此丢失，靠备份+记忆重建。
7. **新建文件即 `git add`**：project_memory #ARCH-GIT-CLEAN-GUARD-FIX 教训——`git clean -fd` 物理删除 untracked 文件不进回收站。

## 五、当前状态快照（2026-08-17 凌晨，第六统筹接手三连收口+三批并发派单）

- **全部历史批次（第 1-5 批+治理批+数据批+重建类）**：✅ 11 路施工会话实质内容全在 dev——SENT e53bc3b70c / RCAN 057a9a2384 / SIM eafc17941c / FIX a539c1fcb6 / MON 0d5f8f0777 / ASM 8b932ced42 / TDEBT 16c3dcf2c9 / NORTH 87f50a5e3f / JOB077 bdf37ab8d5+1e9f14fc82 / JOB083 846a1019a6 / JOB084 3f7f7b603b；ARCH-001 抢救入库 2cdbbc80a7；ARCH-002 冷分层 f556515519。
- **🔴 P0 风控接线批**：✅ 双路 merge 闭环——RRESIL 原语层 dbc5d40e2b → RWIRE 消费层 2b3b68b5d2（module_translation 冲突手工并集）；风控三件套+KillSwitch+对账器生产接线，红队实证全链（回撤 25%→EMERGENCY→真实置位→MARKET SELL 清算/熔断重启存活/并发单轮发单/重放不重复/重建期禁单 Fail-Closed）；**风控层从"纸面熔断"转生产接线态**。
- **233 测试债下批**：✅ **6/6 全部 merge 闭环**（10775 项 2 轮全绿，六 worktree 全四证清理）——UTIL bdda340270 / TRD a3321a0e1c+8e7e0420b5 补链 / AUTO 7877748977+9222d8bd7b / DATA 62e550dcd3 / SEC 3041dc7745 / GOV da552aa74c→5e486bebed；merge 撞号重编：TRD→#ARCH-103/104/105、SEC→#ARCH-106/107/108、DATA→#ARCH-109~113、GOV→#ARCH-114/115/116（6b96c2fa81，全仓引用同步 12 文件 24 处，registry 545 条零 dup）；#ARCH-099 gov_db fixture 治本 resolved；统筹收口 commit 1053b74b03/2caf454963/20bd8de887。
- **结案报告独立复核批（用户直派，dev 直改未走 worktree）**：✅ 已完工入库——28 篇已结案 memo 补结案报告三段式+外部审查员口径实证（52 引用 commit 逐个 git log 实证/关键套件复跑/43 号装配逐行实证）；当场修正 53/54 号漂移+16/55 号计数滞后；新登记 tracker 遗留 #101-#103（**tracker 内部编号，非 registry #ARCH**——#101 53 号五态降级机裁定-代码出入待落码 / #102 regime_detector 文件头 MATURITY 与蓝图不一致 / #103 git 超时测试环境敏感）。
- **🔄 在途四路并发**：①**AI-RFIX-001 算法修复批**（施工中，HEAD 已推进 e30ed31e67，13 文件 WIP 期曾实证）——范围=F1 ES 插值/F2+F4 NaN+Inf 过滤/Qwen P1 群/F5 死代码/FHS 裁定，指令=docs/_working/dispatch/2026-08-16-rfix001-algo-fix-order.md，施工面锁定 risk/core/var_calculator+tail_risk_monitor、position/core/drawdown_controller、ex_core/order_manager、pf_alloc/core/regime_meta_allocator+4 测试+memo 31/36+CAND registry+var_calculator blueprint；②**AI-GOVA-001 治理批 A 包**（Z1-Z3 退役存证/分类器/daemon 失锚自退+#ARCH-114 脚本命名/EXIT 常量+tracker #102 顺手修+#115/116 xfail 清除+watchdog RestartOnFailure 退避+fail-open 出方案）指令=docs/_working/dispatch/2026-08-17-gova001-governance-batch-a-order.md；③**AI-LVL3-001 37 号 LEVEL_3 接线**（LEVEL_3 检测→逃生指令→Kill Switch 生产链路）指令=docs/_working/dispatch/2026-08-17-lvl3001-liquidity-level3-wiring-order.md；④**AI-REDIS-001 state_store Redis 后端**（JsonStateStore/AppendOnlyDedupSet 同接口 Redis 实现，消费方零改动）指令=docs/_working/dispatch/2026-08-17-redis001-state-store-redis-backend-order.md。四路文件级零交集两两实证。
- **第六统筹已闭环（2026-08-17 凌晨）**：①#ARCH-115/116 复跑终证 OBE 转正（关联 4 文件 36 项=29 passed+7 xpassed 零失败，tracker #104 行已更新）；②**validation_cases 移动事件调查+治本**（Owner 调查令）——23:18 移动实证（task:SRC-081 嫌疑未坐实+RFIX 排除+9df037441c 已回退未复现），第一性原理裁定=historical_events.yaml 迁 src/zephyr/regime/validation/phase2/ 消费代码同包，AI-VCFIX-001 自施自 merge 闭环（65045348e8→aaa570ea70，#ARCH-117 resolved，test_b4 16/16×2+phase2 106/106+dev 复跑全绿）；③tracker 三处登记落袋 6f0436d9。
- **待推进（RFIX merge 后解锁，交集已实证）**：①#87 阈值统读（drawdown_controller.py 仓位上限数值表=RFIX Qwen P1-a 同代码段强交集）；②#ARCH-ERRCODE-001 错误码改号（登记时自定"择无并发窗口"）；③depgraph 刷新（防 var_calculator/blueprint.md 与 RFIX 三方冲突，merge 后顺做）；④全量测试复跑终证（#115/116 已 OBE，全量背书可待）；⑤QUANT-002 registry 流转收口（统筹动作）；⑥tracker #101（53 号五态降级机落码）排期等 Owner；⑦#61-64 专项裁定挂起；⑧#96 观察项。
- **环境**：PG 5432 Running；#99 单实例锁治本已落地；depgraph 23:37 已刷（9df037441c）；主仓当前仅剩 timestamp 派生噪声。
- **明日待办**：2026-08-17 开盘 tick 实盘验证（订阅序列/biz 心跳/断流重订阅三项清单）。
- **SOP**：v1.4.0 在 dev（01/sop 专区）；merge 冲突处理 SOP=01/sop/merge_conflict_resolution_sop.md；worktree 清理 SOP=01/sop/worktree_cleanup_sop.md。
- **教训登记（2026-08-17 第六统筹增补）**：①CAPABILITY-LOOKUP 门禁首次实证——CapabilityLookup().find() 需显式传 session_id 或设 ZEPHYR_SESSION_ID，否则静默跳过审计写盘（向后兼容无 session 场景），门禁按 MAIN_REPO_ROOT/.runtime/lookup_audit/<sid>.jsonl 二值判定；②CRLF 幻影 stash 复活实证——幻影 stash push 后 checkout 恢复又按 CRLF 写回工作区，幻影原地复活，正确处置=人工确认零内容差异（git diff 等行互换+EOL 警告）+--force-skip-checks 清理落审计；③merge --yes 幂等（已 merge 检测后直走自动清理）。
- **教训登记（2026-08-16）**：①派发类文件一律落 tracked 区（docs/_working/dispatch/），.runtime 免跟踪区违防丢铁律 #6；②网关正确姿势=--adopt-prior-work 必须挂在 **commit 主命令**上（tracker 遗留 #92 专项复现坐实）；③merge 配号前必全文件 grep 最大号——本日三起撞号（TRD/SEC/GOV）均因施工队各自取号；④IDE 脏缓冲区陷阱——Edit 报成功≠落盘，重要写盘后须进程外工具回读校验（GOV registry 条目回滚事故两度命中）；⑤merge 事故两起已留痕（误取基点漏链/theirs 覆盖，见 0bd6a2b55d/02dd2cc70f 自纠 commit）。

## 六、新批次开工指令要点（供生成一键复制指令时引用）

- 每个施工会话开头必须：`python scripts/session_worktree.py create <sid> <task-id>`（自动备环境三件套；提交前在 worktree 内 `. .\activate_env.ps1`）
- 长清单审查用 **SOP 附录 A 14 节版**
- 反馈必须含：commit hash + Step 1 结论 + Step 6 结论 + 测试结果 + worktree 状态 + 遗留项
- commit 走网关；FOREIGN-CHANGE 对子代理/代编辑误报走 --allow-overlap 并留痕
- 涉及 AGENTS.md 显化修改：走 Owner 审批（PROTECTED-PATHS 门禁，遗留项 #9/#41）
- merge 冲突处理唯一真源：01/sop/merge_conflict_resolution_sop.md（三分法：叠加合并/迭代取新/互斥升级用户）
- worktree 清理必须走 01/sop/worktree_cleanup_sop.md 四证（死亡证明/无未合并工作/统筹批准/可恢复快照）
