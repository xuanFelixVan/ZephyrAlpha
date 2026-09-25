---
ttl: task_bound
title: 决策地图战役施工文档包（2026-09-24 深夜建）
doc_type: readme
---

# 决策地图战役施工文档包（2026-09-24 深夜建）

> 本目录=2026-09-24 总指挥对话轮（Owner × st-cmd-20260924）全部讨论、裁定、施工计划的**结构化真源**。
> 目的：对话会关，文档不会忘。任何继任会话从本 README 进入即可接手全部上下文。
> 纪律：本目录文件变更走 safe_write CAS；整包随批落 HEAD（防蒸发，交付=落 HEAD）。

## 终局目标（一句话）

**交易决策地图全链"原材料备好"**：大盘状态→板块→个股→策略库，每层通道在线、深史无断供、状态真值全史可查、概率表可算；GPU 搜索（本周窗）产出"什么条件下什么策略赚钱"的成绩单；剩下=组合。

## 状态仪表盘（2026-09-24 22:00 快照）

| 战线 | 状态 | 下一步 |
|---|---|---|
| GPU 搜索 T1（3700 格全档门） | 🟢 **跑批中**（grid_20260924-213246，21:32 发车） | 预计周六 08:00-14:00 完 → T2 900 格自动接棒 |
| 裁定 #413 | ✅ 已注册+落队（q-0014） | 方案①列下窗口升级案 |
| 方法论总册十件 | ✅ 已落队（q-0013） | 按册消费进施工 |
| P1 三张条件概率表 | ⚪ 待开工（数据面已验） | GPU 跑批期间并行，详见 04 |
| AI 层 245 件落地 | ⏸ 等"队列畅通"广播 | 判据=E2E 完成+pending<5，本班守望 |
| 蒸发案 | ✅ 已破案+治本已批（EV-01~06 开工，EV-01 黑匣子先行） | 10 号文取证+15 号文治本方案 |
| 退役策略重考 | 📋 纪律已立+开工令已批（09-26） | 排 GPU 第一轮条件骨架之后；CPCV 框架 |

## 文件导航

| 文件 | 内容 |
|---|---|
| [01_goal_and_architecture.md](01_goal_and_architecture.md) | Owner 愿景复述（已验收）+四层架构映射+数据面实测+机构对照结论 |
| [02_rulings_and_calibers.md](02_rulings_and_calibers.md) | 全部已裁事项与口径（#413 四项/六段定论/800 对账/重考三纪律/冷水六条）——**防重裁** |
| [03_gpu_campaign.md](03_gpu_campaign.md) | GPU 战役：现行运行信息+守望要点+方案①升级案施工清单 |
| [04_p1_conditional_tables.md](04_p1_conditional_tables.md) | **主施工文档**：三张条件概率表的数据源/口径/schema/验收 |
| [05_t0_and_strategy_library.md](05_t0_and_strategy_library.md) | 做T线（分钟/tick 分工+材料线）+策略库（退役重考全套） |
| [06_methodology_index.md](06_methodology_index.md) | 方法论十册索引+冷水六条的消费路径映射 |
| [07_pending_work_master_list.md](07_pending_work_master_list.md) | **全量待办总清单**（Owner 23 条原单+今日新增，四类分栏） |
| [08_watch_and_risks.md](08_watch_and_risks.md) | 看守时点表+风险登记+巡检操作规程 |
| [09_link_skeletons.md](09_link_skeletons.md) | **九环节骨架总表**（挖矿班产出：每环节通道/原料/状态轴/概率表覆盖/四判据打钩/缺口/下游） |
| [10_evaporation_forensics.md](10_evaporation_forensics.md) | 蒸发案取证报告（头号嫌疑人=landing _sync_worktree 打穿主仓 65%，治本处方三件） |
| [11_integrated_backtest_audit.md](11_integrated_backtest_audit.md) | 整装回测八环节审计（宇宙完整性/正确性/自动化+施工项 IBT 编号） |
| [12_data_universe_census.md](12_data_universe_census.md) | 数据面宇宙总普查（每表五问：新鲜度/宇宙完整性/登记/更新机制/缺口卡 DU 编号） |
| [13_trading_chain_audit.md](13_trading_chain_audit.md) | 交易链八环节审计（排班/盘前/执行/风控/模拟盘/日循环+施工项 TRD 编号） |
| [14_consumption_census.md](14_consumption_census.md) | 九族数据消费面普查（谁在用什么/上架无客/考死退役/该接未接+CNS 施工项） |
| [15_evaporation_cure_plan.md](15_evaporation_cure_plan.md) | 蒸发治本施工方案（EV-01~06，**已批开工 09-26**） |

## 会话与责任

- 本包作者/现任总指挥：st-cmd-20260924（2026-09-24 12:01 自 st-cmd-20260923 交接书接管）
- 指挥台账：docs/_working/cmd_ledger/overnight_decisions_20260924.md（R39-R43）
- Owner 对话批准记录：见 02 号文各条"依据"栏
