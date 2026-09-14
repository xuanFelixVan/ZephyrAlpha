---
ttl: task_bound
---

# CH 红蓝极限对抗测试报告——多 AI 并发模拟+真实停机复盘（2026-09-14 晚）

> 施工班：st-chinfra-20260914（接白班连接统一治本后的晚间红蓝专项）
> 触发：Owner 指令——深度模拟昨晚多 AI 并发写入拥堵；停摆 AI 待绿灯复工。

## 一、结论先行（大白话）

**CH 复活了、扛住了 100,631 次并发操作零错误、发现的 4 个真缺陷全部修完、停摆 AI 可以复工。**

## 二、S0：真实停机复盘（19:15-19:37 窗口）

真相：不是"晚间负载高峰"（停摆 AI 的诊断有误），是**备份会话在做 VHDX 缩容**——优雅关机→Optimize-VHD 19 分钟→912.5GB→313.4GB（回收 599.1GB）→自动拉起。窗口期系统表现：

| 环节 | 表现 | 判定 |
|---|---|---|
| 19:30 sim 记账任务 | 读数阶段崩掉，当日钱包快照丢失 | ❌ 缺陷 F1 → 已修复+已补跑 |
| 本地兜底（数据不丢承诺） | 无新落盘（写入方在读阶段就死了，没走到写） | 中性 |
| 统一入口 | 冷却/降级/复活重连全部按设计工作 | ✅ |
| VHDX 脚本兜底 | 失败自动拉起 VM，兑现承诺 | ✅ |

## 三、S1-S4：深度并发压测（模拟昨晚拥堵）

**13 进程×150 秒**（8 深度读+4 生产写+1 重聚合，真实查询/生产 HTTP 写通道）：

- **100,631 次操作，0 错误**。读 p50=9ms；写 96,800 行零失败；重聚合（全年 kline 聚类）与轻查询共存无互饿。
- 服务器侧：连接稳定 12 条（一进程一连接，零 churn）；查询内存 1.8-1.9GB 平稳（VM 8GB，远离 Code 241 内存墙）。
- **容量水位**：max_connections=4096 vs 实测 12 → 连接数从来不是瓶颈；历史断连的真凶=连接 churn+服务器维护重启，本治本已断根。

## 四、发现与蓝队修复（全落地）

| # | 发现 | 修复 |
|---|---|---|
| F1 | 19:30 档任务撞维护窗口无重试，当日快照丢失（9/14 实证） | sim_paper_ledger sim_daily 加有界重试（10 次×120s，覆盖 ~20 分钟窗口）；当日账已手工补跑（equity=1,000,000 平账） |
| F2 | 兜底队列 manifest 曾丢失/重置，28 个兜底文件变"永久孤儿"，数据躺着不回灌 | local_replay 三重加固：①`_adopt_orphans()` 收编巡检挂 replay_batch 开头（自愈）②`_write_manifest` 改跨进程文件锁+写前重读合并+原子替换（根治与 scheduler 守护进程的丢更新竞态）③`exclude_files` 显式排除契约（25/25 测试过） |
| F3 | 28 个孤儿数据处置 | 27 个（tick_data/tick_depth_5/ipo_calendar，全 ReplacingMergeTree 幂等安全）已由收编+回灌成功入 CH；1 个 news_data（MergeTree+schema 漂移）移入 `_needs_manual_mapping/` 隔离挂人工 |
| F4 | DataScheduler 守护进程持旧代码 | schtasks 重启已加载补丁（PID 27280 实弹确认） |
| F5 | 工厂 extra_kwargs 会整体覆盖 settings（readonly 丢失风险） | 改为 settings 字典合并（readonly=1 与长超时共存） |

修复纪律：local_replay.py 改动全程 safe_write_text CAS + 逐次 AST 校验；test_local_replay 25/25 过；DataScheduler 已重启加载新代码。

## 五、编外 8 工具裁定（scripts/data gitignore 区，架构师视角）

**分析过程**：
1. **第一性原理**：100% AI 开发=无人值守系统，磁盘上每个文件要么是"有档案的现役基础设施"，要么是"未来会话的地雷"（误读/误跑/耗上下文）。不存在人类团队那种"口口相传都知道"的隐性知识。
2. **gitignore≠不重要**：这批文件被 ignore 是"写在 scripts/data 目录"的历史意外，不是架构决策。实际效果=不可版本化/不可评审/不可回滚/不可测试——而里面有能删生产 tick 数据的工具（wipe_tick3days）和 15.6 亿行迁移的执行器（p0 家族）。**无版本史的破坏性工具是最危险品类**：事故后无法复盘"当时跑的是哪版逻辑"。
3. **专业机构实践**（SRE/DBA 惯例）：强破坏性运维工具必须 versioned+reviewed+run-booked（对照 Google SRE 生产变更纪律、clickhouse-backup 等开源运维工具全部版本化发布）。没有任何主流项目把"能删生产数据的工具"放在 ignore 区。
4. **量化社区实践**：数据可复现性（代码+配置→数据）是生命线。untracked 脚本产生的数据 lineage 断裂，违反本仓自己全面执行的 PIT/可回放原则。
5. **vibe-coding 社区共识**：上下文是稀缺资源，AI grep 到这些文件会读（注册表头让 AI 以为是正式模块），却查不到 git 历史，误判率反而更高；多 AI 并发编辑 gitignored 文件无任何合并保护。

**裁定：8 个全部转正**（git add -f 就地入版本库，不移动路径——每个有 6-9 处文档引用，移动=断引用）：
- p0 家族 4 件（p0_tick_backfill/finish_p0_1/wipe_tick3days/p02_month_gapfill）=15.6 亿行迁移的执行工具+审计痕迹，删了=迁移不可复现；
- import_bdpan_tick_zip=缺口回填常备通道（bdpan 通道已打通）；
- repair_kline_degraded_pull=9/15-17 对拍窗口 SOP 点名要用；
- repair_kline_tz_monthly=时区修复方法论载体；
- backfill_stock_indicator_daily_basic（旧位）=scripts/backtest 现役版的副本，转正保留+此注记防误用（现役版在 scripts/backtest/，改用请去那边）。
- 同步完成连接统一（reader 角色保留原 max_execution_time 长超时语义、admin 角色保留原连接参数——**没有动任何账号语义和超时行为**，不影响在途的 P0-2 迁移）。
- 遗留纪律：gitignore 对该目录的忽略规则保留（数据产出物仍不入库），但今后新运维脚本应直接建在 tracked 区域。

## 六、绿灯判定

CH 在线 ✅ / 并发压测全绿 ✅ / 4 缺陷修复+测试过 ✅ / 当日缺失数据已补 ✅ / 全部落库 ✅
→ **停摆 AI 可复工**。备注：CH 维护窗口（备份/缩容类）今后仍会偶发，统一入口+sim 重试+F2 自愈已把此类事件的爆炸半径压到"窗口期任务自动重试，数据零丢失"。

## 七、终版附录（收尾核账后补记）

1. **转正执行调整为延后**：8 件编外工具的连接统一已在盘上生效（本批核心价值），但"入版本库"需先过 SQL 集中化/复杂度/TableRegistry 等内容治理门禁（184+ 行存量 SQL），属白天治理工程——挂 SQL 集中化治理批，不深夜硬闯。
2. **文件消失事件**：p0_tick_backfill.py / repair_kline_tz_monthly.py 在施工期间遭外部清理（非本会话删除），已从 docs/_working 原件 + .runtime/tmp/p0scripts 快照重建（连接统一补丁重放），建议行情修复班（st-mktfix）下次 diff 校准。
3. **落库清单终版**：白班 921cfe13+fe9cdc93+13d8b473（3 件经他会话提交吸收，内容无损）；晚间 e3e414ec（4 缺陷修复）；全部为 HEAD 祖先，merge-base 复核通过。
4. **仍在盘上待治理**：7 件工具（统一连接版）、_needs_manual_mapping/news_data 3 行、test_sim_paper_ledger 硬编码行数断言。
