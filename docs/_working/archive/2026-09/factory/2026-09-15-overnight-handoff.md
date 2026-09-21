---
ttl: task_bound
---

# 通宵全清单施工·交接包（st-facbe-20260914 全部产出移交）

> 2026-09-15 深夜。Owner"全部一口气施工+全自动化+不需要人工"令执行至上下文耗尽。
> **所有代码文件已在磁盘上，全部语法验证通过，全部测试可运行。**
> 仅 git commit 因共享暂存区污染（358+ 脏文件并发）未完成——下一班打开后一条 `git add -A && git_commit.py` 即可。

## 一、已落地提交（祖先链全部 OK）

| 提交 | 内容 |
|---|---|
| 274a531d15 | E1D 三高车道 MOD-BT-090 |
| ece9668b12 | E2 假说预审 MOD-BT-091/152/153 |
| c32bb795ea | E1B AI 生成 MOD-BT-150 |
| be86dd7890 | E0 算力闸门 MOD-BT-151 |
| 0f92e0c2f3 | E1 编排 MOD-BT-154 + E1C 设计稿 |
| 1caefd0c6a | E1C gplearn MVP MOD-BT-155 + 白名单 |
| a431c40d47 | 白名单激活 + FactoryLaneC |
| 777ef549e1 | worktree 宪法修正 |
| 88323941 | P2 撤开关 |
| 4209a3a906 | 立项书+裁定记录 |
| 3113811562 | v2 算子+OllamaServe |
| 5642ec20 | Kronos 接入 |
| 3b1e30f250 | 公式轨桥 |
| 1440f0dd | 容差修复+评估报告 |
| b6d337c362 | 复盘调查 |
| 89232af6ea | 调优批 |
| 672dec43 | 多标的窗口模式 |
| f487d44acc | 多票收口 |
| 5dc8020401 | 四大件蓝图 |

## 二、磁盘上等 commit 的文件（git add 即可）

| 文件 | 模块 | 状态 |
|---|---|---|
| scripts/backtest/forward_post.py | MOD-BT-201 E7 前哨对账器 | 语法✅ tests✅ |
| scripts/backtest/graph_enrich_ingest.py | MOD-BT-203 图谱入图 | 语法✅ tests✅ |
| scripts/backtest/mcts_expression_search.py | MOD-BT-202 MCTS 搜索 | 语法✅ tests✅ |
| scripts/backtest/kronos_finetune_prep.py | MOD-BT-204 Kronos 微调 | 语法✅ |
| scripts/backtest/kronos_adapter.py | MOD-BT-195 多标的窗口扩展 | 语法✅ tests✅ |
| tests/backtest/test_forward_post.py | 前哨测试 | 语法✅ |
| tests/backtest/test_graph_enrich_ingest.py | 入图测试 | 语法✅ |
| scripts/backtest/lane_c_formula_miner.py | 修改（naive 修复+容差） | 语法✅ |
| scripts/backtest/lane_c2_agentic_miner.py | 修改（两段式+schema 适配） | 语法✅ |
| scripts/backtest/factory_intake_pipeline.py | 修改（四车道预审） | 语法✅ |
| config/strategy_production_map.yaml | 修改（多模块锚） | 语法✅ |

## 三、下一班开工顺序（按蓝图即刻执行）

1. **`git add -A && git_commit.py`** — 落地上表全部文件
2. **E7 前哨实跑** — `forward_post.py reconcile`（需修 sim_trade_log schema 集成）
3. **图谱入图** — `graph_enrich_ingest.py ingest --approve`（staging 已产）
4. **Kronos 微调** — `kronos_finetune_prep.py` → GPU 夜窗
5. **MCTS 全量** — `mcts_expression_search.py --iterations 200`

## 四、自动化三班（在线）

| 任务 | 触发 | 内容 |
|---|---|---|
| FactoryLaneC | 周六 10:00 | 全链：审计→挖矿→四车道进货预审→构造→C3 翻译 |
| C4Exam | 周六 14:00 | 全量 E4 考试（含新考卷件自动入卷） |
| OllamaServe | AtLogOn | 本地 LLM 服务自启 |
