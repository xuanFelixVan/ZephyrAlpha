---
ttl: task_bound
---

# 四大件施工蓝图（MOD-BT-201/202/203/204）——下一班按图索骥即刻开工

> 2026-09-15 st-facbe-20260914 起草。depgraph 设计态已登记（201/202/203/204），
> 号段 201-204 已占用（脚本 grep 确认）。本文=可直接执行的施工图，非概念稿。

## MOD-BT-201 · E7 前哨对账器（scripts/backtest/forward_post.py）

**触发**：E4 及格者 80 条（`oos_tested`），门控已完全触发。

**核心逻辑**（三步）：
1. `fetch_e4_passers()` — 查 strategy_screen `verdict='oos_tested'` 的
   DISTINCT strategy_id + 最近 is_sharpe；
2. `fetch_sim_daily(strategy_id)` — 查 sim_paper_ledger 该策略模拟盘日账
   （sim_trade_log 或 sim_wallet 表）；无模拟盘记录→提示走 C1 自动开户（已有）；
3. `reconcile(pred_file, sim_daily)` — 逐日对账：预测方向 vs 实际涨跌→
   命中/偏差/缺失三类→`forward_post_report.csv`（含累计命中率/信息比/最大连续偏差）。

**依赖**：MOD-BT-084 考尺（已有）；sim_paper_ledger（已有）；strategy_screen（已有）。
**测试**：合成模拟盘数据验证对账三分类；零网络。
**验收**：恐慌反弹 CAND-e3da6fa71af1（已在 sim）能出完整对账报告。

## MOD-BT-202 · MCTS 第三轨（scripts/backtest/mcts_expression_search.py）

**核心逻辑**（四步）：
1. `MCTSNode` — state=部分表达式（算子栈），children=可扩展操作（push 算子/push 特征/eval）；
2. `ucb_select(node, c=1.4)` — UCB1 选择：exploitation(node.value) + exploration(√(2lnN)/n)；
3. `expand + simulate` — 沿树扩展一步→DSL 求值（复用 `build_eval_ops`+`evaluate_expr`）
   →`residualize`→`rank_ic` 作 reward；
4. `backprop` — reward 回传路径→下轮选择偏好高分分支。

**依赖**：MOD-BT-155 的 `build_eval_ops`/`evaluate_expr`/`residualize`/`rank_ic`（全已有）；
  MOD-BT-194 考尺（评分）；白名单 YAML（已 active）。
**测试**：合成面板验证 UCB 选择/树生长/reward 回传；零网络。
**验收**：合成数据上 MCTS 能找到增量 IC>0 的表达式（vs 随机搜索基线）。
**输出**：`lane_c3_candidates.csv`（出生证 birth_channel='C3'）。

## MOD-BT-203 · 图谱增补入图（scripts/backtest/graph_enrich_ingest.py）

**核心逻辑**（三步，**入图必须 Owner 审批 flag**）：
1. `read_staging(csv_path)` — 读 graph_enrich_staging.csv（已产）status='staged' 行；
2. `validate_relation(row, ig_fact_conn)` — ①supplier/customer 都在 symbol 宇宙或
   ig_node 节点表 ②evidence 原文在 news_data 可查 ③非重复（同 supplier+customer+product
   在 ig_fact 无同relation）；
3. `write_to_ig_fact(conn, validated_rows, dry_run=True)` — `INSERT INTO ig_fact
   (subject, relation, object, value, evidence_chunk_id, confidence, as_of, source,
   market, created_at)`，`source='graph_enrich_staging'`，`confidence=staging 值×0.8`
   （降级因子），`dry_run=True` 时只打印 INSERT 语句不执行。
   **`--approve` flag 必须显式传入才真正写入**（Owner 审批门，缺省=dry-run）。

**依赖**：graph_enrich_staging.py（MOD-BT-193，已建）；ig_fact 表（PG）。
**测试**：合成 staging 行验证三道校验门；mock ig_fact 连接验证 dry-run/write 双路径。
**验收**：staging CSV 中合法行能写入 ig_fact 且 source 标记正确。

## MOD-BT-204 · Kronos 微调数据管线（scripts/backtest/kronos_finetune_prep.py）

**核心逻辑**（三步）：
1. `build_finetune_dataset(symbols, start, end)` — 从 CH 拉 K 线→
   按 Kronos finetune_csv 格式输出（date,open,high,low,close,volume,amount）→
   切分 train/val（80/20 时间序）→写 `data/kronos_finetune/` 下 CSV；
2. `generate_finetune_script()` — 生成调用 Kronos 官方 finetune 模块的 wrapper
   （`.runtime/tmp/kronos_repo/finetune/` 下有现成脚本）→输出 `.runtime/tmp/kronos_finetune_run.py`；
3. `launch_finetune(gpu=True)` — 子进程启动 GPU 微调（nohup 后台），日志落
   `.runtime/logs/kronos_finetune.log`；微调完成后权重自动替换 `vendor/kronos_weights/kronos_small`。

**依赖**：Kronos 官方仓（vendor/Kronos，已有）；CH kline_daily_hfq（已有）；GPU（RTX 3090 24GB）。
**测试**：数据格式校验+切分比例；微调脚本生成内容检查。
**验收**：微调 10 epoch 后 val loss 下降；新权重在 kronos_adapter 中 load 不报错。
**注意**：微调耗时约 1-4h（GPU），需夜窗/周六窗执行；微调期间不得跑其他 GPU 任务。

---

## 执行顺序建议

| 优先 | 模块 | 理由 | 预估班次 |
|---|---|---|---|
| **1** | MOD-BT-201 E7 前哨 | 80 及格者等验证；sim 基建现成 | 1 班 |
| **2** | MOD-BT-203 图谱入图 | staging 已产；打通 E1D 全链 | 1 班 |
| **3** | MOD-BT-202 MCTS | 车道 C 三轨；DSL 基建全现成 | 1-2 班 |
| **4** | MOD-BT-204 Kronos 微调 | GPU 密集；需夜窗/周六窗 | 1 班+训练时间 |
