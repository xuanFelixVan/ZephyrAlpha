---
ttl: task_bound
title: 08 看守时点表+风险登记+巡检规程
---

# 08 · 看守时点表 + 风险登记 + 巡检规程

## 一、时点表

| 时点 | 事项 |
|---|---|
| 09-24 22:00 | GPU T1 已发车（grid_20260924-213246） |
| 09-25 白天 | P1 三张概率表交付；蒸发追凶报告 |
| 09-25 全天 | 队列消化（本班 9 件+他班在队）；pending<5 且 E2E 完成 → AI 层广播 |
| 周六 08:00-14:00 | T1 预计完赛 → 验收（manifest=3700/negatives/net_returns/dead=0）→ T2 900 格发车 |
| 周六 14:00/18:00 | c4_exam/model_exam 例行跑（与 GPU 完赛天然错开；若 GPU 拖过 14:00，按 #413③ 改签周一 08:00） |
| 周日 09:00 | 59h 窗收 → GPU 战役总成绩单（cost_adjusted_sharpe+negatives 台账+DSR） |
| 下周 | 方案①升级案/T2 后主效应分析/退役重考预注册/72h 双轨切主评估 |

## 二、风险登记（在册在办）

| 风险 | 状态 | 对策 |
|---|---|---|
| **主区蒸发连环（四例）**：untracked+index reset--hard+clean-fd 特征，机制未定位 | 🔴 追凶在办（09-25 报告） | 对策已制度化：交付即落 HEAD（本包/台账全走队列）；t0 班另见 index 9 条暂存删除待查执行源 |
| 队列瓶颈：pending 30+，吞吐 12-14/h | 🟡 常态 | k=4 池化在跑；AI 层广播以 pending<5 为判据即为此设 |
| f18d34c8（18:00 收班巡检自动化）状态矛盾（completed/runCount=31 但 nextRunAt 指向当日） | 🟡 | 不重建防双发；本班兜底亲跑 |
| t0 5 封死信（TABLE-NAME-REGISTRY+NO-BARE-SQL 内容可修型） | 🟢 包活自修（§3.4 不代修） | 观察 |
| 跨班收官互清（图书馆班两度被清理） | 🟡 文化性 | 停手公共面不对抗；交付即落 HEAD |
| 共享 index 战场（620 件 staged，含外来 BLUEPRINT 违规件） | 🟡 | 直连提交会被连坐——**一律走队列**（快照语义免疫） |
| GPU 单卡互斥（exclusive_group=gpu_default vs 本地 LLM 21.6GB 硬顶） | 🟡 | 跑批期间禁起本地大模型 |

## 三、巡检操作规程（每轮 10 分钟）

1. `python scripts/commit_queue.py status`（pending/processing/done/dead 四数+心跳）；
2. `tail .runtime/logs/grid_t1_20260924.log`（进度/异常）+ `tasklist | grep python`（进程存活）；
3. `nvidia-smi`（显存≤18GB 配额/温度）；
4. 产物目录增长抽查（data/strategy_intake/grid_*/）；
5. 死信箱（.runtime/commit_queue/dead/）新增验尸；
6. 本包状态仪表盘（README）核对更新——变更走 CAS。

## 四、继任指引

继任会话：读本 README → 02 号文（防重裁）→ 07 号文（待办全量）→ 本文件（看守）。指挥台账=cmd_ledger/overnight_decisions_20260924.md（R39 起）。
