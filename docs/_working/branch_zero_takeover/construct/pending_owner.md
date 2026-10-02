---
ttl: task_bound
session: st-construct-20261002
date: 2026-10-02
title: 留待 Owner 裁定项清单
completes_when: 全部条目获 Owner 表态后销册
---

# pending_owner.md — st-construct-20261002 移交 Owner 项

## A. 唯二终留项（承接前总包，本包无变化）

1. **TRD-A10 实盘腿**：保持关闭（裁定二），解锁条件=模拟盘 60 交易日+Sharpe>1 证据+Owner 签字。
2. **origin/master 删除**：`git push origin --delete master`（删前确认无外部消费）——命令在 Owner 手里。

## B. 本包新增移交项

3. **TradingWatchdog 任务动作修复**：系统登记的 principal SID 断裂（"帐户名与安全标识间无任何映射"），任务 Disabled（92 D3 Owner 门位设计）。动作仍指老路径 `scripts\start_trading.ps1`（已迁 scripts\installers\）。**处方：Owner 开启窗时先 Unregister 旧任务→跑 scripts\tasks\register\register_guard_tasks.ps1 重建（create-if-absent 分支将以新路径注册）**。
4. **C4Exam_OneShot0915 / FactoryLaneC_OneShot0915 拒绝访问**：两个一次性实验任务（豁免登记在案，禁用/删除/转正=Owner 门位）XML 补丁被 ACL 拒——动作仍指老路径。任务若仍 Disabled 则无运行时影响；处置（删/修）=Owner 门位。
5. **migration_registry 13 条 pending**：机械核验=从未执行的模块拆分**计划**（gate_engine/rule_engine 两个 subdir 的 13 件，老文件全在、新路径全无）。冻结册守卫只许 pending→done 流转——两条路 Owner 选：①立项执行拆分（大重构）；②修订册守卫允许"plan-retired"状态（收编进 schema_migrations 台账批）。现状=13 条假 pending 长期挂账。
6. **GATE-SELFDOC 宪法条款无实现**：AGENTS.md §1 规定行级/frontmatter 豁免标记，但 detect_git_dangerous 等检测器全仓无对应读取逻辑（legacy_v1 宪法归档的 GIT-DANGEROUS 豁免实测无效）。P2 债：实现门侧豁免读取（≤10 行限制照宪法），或修宪删除该条款。
7. **requeue 快照通道缺陷**：requeue 重快照会把主区全部脏面卷入落地临时索引（本次 q-0007~0011 连环死实证；同清单全新 enqueue 即过）。已登记的"prestage own-scope 化"议题（台账域二 #10）应升 P1——requeue 在多会话并发环境下结构性不可用。
8. **估值 v2 DROP 窗口**：index_valuation_daily_v2_quar_20261002 隔离第 1/7 天，**2026-10-09 期满**。到期无人认领即走 DROP（净零 §4）。建腿若立项=v1/v2 口径归属+akshare 候选源 Owner 裁。
9. **index_valuation_daily_quar_20260920**：v1 的旧隔离副本（8125 行）已超 7 天隔离窗——同通道可 DROP（本包未动，避免与 v2 混批；Owner 点头即执行）。

## C. 前总包遗留复核（本包验证后维持原判）

10. **PROTECTED-PATHS 预检读数分歧**（裁定八）：不紧急，维护班溯源；本包 ruling 册一行路径修复留手待载体 issue。
11. **metaq .rda 契约**：留盘+登记结案（CR-7），无新证据。
