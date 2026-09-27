---
ttl: task_bound
completes_when: 战役收官时本件条目清零（或全部转为 Owner 已裁）则使命完成
title: 六图战役·待裁项登记（Owner 睡眠期跳过继续）
owner: st-mapbuild-20260924（总包）
---

# 99 待裁项（一句话 + 两选项 + 总包推荐）

> 登记规则：自裁模板（第一性原理+对标机构实践+查既有裁定）仍无法定的才进本件；进本件后**跳过继续下一任务**，不停工等待。
> 例外：**破坏性/资金类**条目即便总包能判，也必须经 Owner 门位（宪法 §5 第 2 条 high 域），本类条目**不执行只上报**。

## P0（有死线，优先看）

| # | 图 | 一句话 | 选项A | 选项B | 推荐 | 状态 |
|---|----|--------|-------|-------|------|------|
| P0-1 | 图12 | 备份镜像 `g_mirror` 的 `ch_vm_backup` 目标：e3cff4e6fc 已摘除（防 robocopy /MIR 回删），但被 6b7749d4a8 反向复活，dev HEAD 至今仍含该目标，主区只有一条未提交的 M；F 侧已瘦身为配置级 ⇒ **下一次 /MIR 会删掉 G 侧唯一 `data.vhdx`（实测 591.57 GiB），且 robocopy 退出码仍记 ok、无红字**。图12 W-F 车道实测判读，Owner 早执轮 7c06425bee 记的"摘除"事实成立但落地态被回退 | 立即再摘一次并同批补防回退锚（在 depgraph/契约面钉住"该目标不得回加"，让回加即触门禁） | 只恢复主区那条未提交 M 后走正门落地（快但同样无防回退锚，下次仍可被反向复活） | **A**——本件已发生一次"修好被反向复活"，只修不防=第三次踩同一坑；防回退锚属注册表/契约面净增，Owner 门位放行后再动 | **待 Owner（死线 2026-09-25 06:00，即下一次 DailyBackup 触发前）**；本战役全程未碰 backup 配置与盘侧 |

## 一般待裁（挖矿期累计）

| # | 图 | 一句话 | 选项A | 选项B | 推荐 | 状态 |
|---|----|--------|-------|-------|------|------|
| （暂无） | | 其余裁定项已按自裁模板自行判定并执行，登记在 `01_lane_workplan.md`（自裁 A 粒度律 / 自裁 B 封矿单元律）与后续施工卷 | | | | |

## 已知会 Owner 但不需决策的实测红条目（供晨读，不占门位）

1. **图12 终点不可证**：`recon_runner.run_daily_reconciliation`（日终三账）**未接线**——15:40 槽无分派 + 零调用方 + `reconciliation_differences` 0 行。图12 的域终点"对账 PASS"因此今天无法机械证明。（`reconcile_execution_log` 8.7 万行属图11 自愈环，误当对账证据=假绿）
2. **缺口回补器 `auto_backfiller` 建好未接线**：仅 `__init__` re-export + 测试；`wiring_registry.yaml:549-555` 以 `pure_library/exempt` 合法绕过接线门，而 SOP:138 写"常态在岗"。后果=因子/公式升级/源修复三类历史回填无人补。
3. **OPTIMIZE 周维护"开工了但没登记"**：计划任务 LastRun 09-20 03:30 / Result=0 / 日志 659 分区，但 `resource_samples` 零 `ops_*` 样本（册上 `planned/samples:0` 是测量缺失而非未跑）。且"失败 0"**不可信**：ch_reader 失败返空串不抛，`optimize_merge.py:145-148` 记为成功（同帧实测有 500 错误）。
4. **判重器不可用**：`check_tick_duplication` 的 `_SQL_TOTAL_ROW` 平铺 14 列在 `tick_data` 恒抛 Code 42，被静默吞成 0；真重复实测 2 组 4 行。RULE-DATA-OPS 点名的判重工具本身现在是坏的。
5. **图11 precommit 通道的回滚旗失效**：flag 名 `gate_precommit_run_enabled` 未在 flags 册注册且 default=True ⇒ 册上写的"回滚=flag OFF"恒不可达。
6. **图11 死分支**：`git_commit.py` 退出码实 11 种（0-10），码 4（STASH_CONFLICT 支）无生产者=死分支，码 8 双义。
7. **多表断供/滞后实测**（图12）：`l2_tick` 0 行（L2 权限+降级腿已删）、`suspend` 0 行（停复牌子源断链）、`hk_kline`/`futures_kline_qmt` 停 09-16、`kline_sector_intraday` 停 2 交易日、周/月线停 9 日、`consensus_daily` 停 10 日（上游 `research_report` 停 6 日）、`sector_state` 两 stage trade_date 倒挂、`sector_preference` 全表仅 1 行。
8. **CLI `pause <source>` 名义化**：`policies.yaml` 无 `enabled` 键、热重载即复位、不跨进程——停源动作今天不真生效。
9. **图14 政策与实码背离 9 处**：`construction_workflow_policy` 声称的件里 `scripts/ide_health_service.py`（5 份文档共引、全仓不存在）、`session_worktree.py` 四子命令、`apply_depgraph --query-production` flag 等**不存在**；且裁定#384（2026-09-20）把该政策上游 49 件 design_memos 整体归档，造成政策内 12 处链接全断、行号锚 7/7 全偏。
10. **L-INTEG 收口撞号重编（知会，非决策件）**：任务书预设收口裁=裁定#412，实扫发现主区已落地 #411（翻译册 dedupe）/#412（akshare 克隆退役）/#413（GPU 点火三件套），且本战役未落地首波三图准入裁原编 #411 与已落地 #411 撞号。处置=战役侧让号重编 #411→#414、收口总裁取 #415（取号器在册面+手工核对 pending 袋，在途无新声明）；已落地条目零改动，册面删除集=∅。选项A=维持 414/415（推荐，键唯一已实证）；选项B=若 Owner 认为战役条目应回到 411 位则需对已落地条目做历史改写（不推荐，违"已落地不回改"）。
