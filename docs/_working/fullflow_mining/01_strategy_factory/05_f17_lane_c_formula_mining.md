---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F17 车道C·公式挖掘机（gplearn/智能体/MCTS 三轨）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-155+158+202
map_node: FAC-E1C
---

# F17 · 车道C-公式挖掘机（三轨）

## 一、环节定义与边界
一句话：受控搜索空间（config/factor_mining_whitelist.yaml 白名单算子，status=active，Owner 2026-09-14 审定）内的公式因子量产——gplearn 遗传规划轨（155）+LLM 智能体 DSL 轨（158）+MCTS 树搜索轨（202），统一增量 IC（对 REG-IND-001 基座残差 rank IC）作描述性验收，判定权留 E2/E4。
上游供料=kline_daily_hfq+technical_indicator 面板（CH）、E2 过审假说（158 种子反哺）、白名单 YAML；下游消费=lane_c_candidates.csv/lane_c2_candidates.csv/lane_c3_candidates.csv→E2→auto_construct（C/C2 公式轨直通 E3）。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | 面板 fetch_panel（lane_c_formula_miner.py:328-，universe=窗内成交额 topN、特征 ≤T、y=前向 5 日收益、基座=TI 日频）；白名单 load_whitelist fail-closed（:98-108）；158 种子=CH precheck_passed（lane_c2_agentic_miner.py:62-65） |
| 下游消费 | lane_c_candidates.csv 16 行（4 批：09-14×8、09-15×2、**09-22 A101×2+HF×4**）/lane_c2_candidates.csv 8 行（09-15 两批）/lane_c3_candidates.csv **不存在**；E2 台账消费 C 渠道 10 条+C2 渠道 8 条；auto_construct 消费 C/C2 过审 |
| 自动化触发 | 无常驻（manual CLI）；重算力 E0 问闸 heavy 档接线实证（run_mine :401-405，闸拒拒跑、--smoke 工程烟测豁免留痕） |
| 真源与注册表 | MOD-BT-155:16026/MOD-BT-158:16033/MOD-BT-202:16075 三件全在册；tests 三套在盘（test_lane_c_formula_miner/test_lane_c2_agentic_miner/test_mcts_expression_search）；Owner 2026-09-14 四项裁定（双轨分期/REG-IND-001 基座/种群1000×50/白名单审定制）落地在码；设计稿=2026-09-14-fac-e1c-formula-mining-design.md |
| 门禁与质量尺 | 白名单∩引擎算子 fail-closed 交集；增量 IC 验收线 0.01（S02-N2 收紧，158:60）；AST 原创性门 Jaccard<0.8（158:59）；AST 节点上限 14；搜索（gplearn 内置 spearman）与验收（自算增量 IC）分离；随机种子固定可复算；出生证含白名单 md5 指纹（:289-299）；--smoke 豁免仅限小规模留痕 |
| 当前运行状态 | **黄（gplearn/智能体两轨真实出货，MCTS 零出货）**。gplearn 最近出货=2026-09-22（A101/HF 两批 6 条——注意批号带非时间戳后缀，为特殊批标记）；C2 最近=09-15；C3=零。E2 漏斗：C 渠道 8 reject/1 pass+2 defer；C2 渠道 6 reject+2 defer——**过审率极低（27 候选 1 pass）** |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| gplearn 轨 run_mine（问闸→白名单→面板→GP→增量 IC→卸货） | scripts/backtest/lane_c_formula_miner.py:400- | built（16 条出货实证） |
| 自定义面板算子 make_panel_operators（groupby 分组语义/参差面板） | 同上:116- | built（v2.1） |
| 假说文本 v2（算子释义+机制自述要求，治 reject_tautology 误杀） | 同上:246-261 | built |
| 面板/特征工程 compute_features（挖矿与考卷件共用唯一实现） | 同上:302-326 | built |
| 智能体轨 lane_c2（种子→DSL→AST 校验→增量 IC+原创性→卸货） | scripts/backtest/lane_c2_agentic_miner.py（477 行） | built（8 条出货实证） |
| 两段式机制门 build_mechanism_prompt（图9 记为已入 C2） | 同上:103- | built |
| MCTS 轨 mcts_expression_search | scripts/backtest/mcts_expression_search.py:68-170 | **半成品**：run_search 主体是"随机扩展+评估"，UCB 选择/回传未接主循环（:145 自注 Simplified MCTS）；零出货；未挂 _LANE_SPECS |
| AlphaGen 轨 | — | missing（图9 与 155 头注一致：立项另批，双轨分期裁定内） |
| LLM 辅助生成省算力替代 | — | missing（图9 提及，无件） |

## 四、堵点与病灶
1. **C 渠道 E2 过审率 1/27**：现象=gplearn+C2 共 27 条候选仅 1 条 pass（E2-20260914-070402）；根因=公式因子假说天然难过"机制六问"（reject_no_mechanism/tautology 为主）——这恰是 E2 防噪音总闸在工作（非病灶），但 09-15 后 C 渠道 2 条+I 渠道 10 条全部 defer_llm_unreachable（LLM 不可达期）且滞留（同 F21 断点③）；修法=deferred 重审通道修复后自然解。
2. **C3 MCTS 名实差距**：图9/头注宣传"UCB1 选择→扩展→评估→回传"，主循环实为随机搜索；且 eval_fn 异常吞成 -1.0 会把语法错误候选与真负 IC 混为一池；修法=接通 UCB 主循环或诚实降格为"随机表达式采样器"；1 天；本车道可修。
3. **09-22 批号命名漂移**：E1C-20260922-A101/HF 后缀非 strftime 产物（正常批=E1C-YYYYMMDD-HHMMSS）——批号语义分裂，台账聚合/排序受影响；修法=回填生成脚本的批号规约或登记特批语义；0.5 天；待挖（需查 09-22 班会话记录确认特批含义）。
4. **GP 正式档（1000×50）从未跑过**：台账 16 条全部来自 smoke/小规模档（批号可证 09-14/15/22 均为小批）；白名单 active 但正式档算力窗（E0 heavy）+时长成本未实战校准；修法=排一次正式档夜跑并记录耗时/产出率；属运行任务非施工。

## 五、提速与合并机会
- 155/158 共享面板与算子（158 build_eval_ops 委托 155 make_panel_operators，CLONE-GUARD 决议在案）——正确形态，无需合并。
- 202（MCTS）若转正应并入 158 产线（同 E2/construct 消费面），避免第三条独立卸货路径。

## 六、自审闸三态
- **三态结论：partial**（155/158 built；202 半成品+零出货；正式档未实战；deferred 滞留牵连）。
- **差什么才算 built**：①202 接通 UCB 主循环（或图9 除名第三轨）+首次真实出货+挂 _LANE_SPECS；②deferred 重审通道修复（F21 侧）使 2 条 C defer 可重考；③（图9 口径"选型待小批量试产"已由四项裁定解决，无欠账）。

## 七、复核命令
```bash
python -c "import csv;from collections import Counter;rs=list(csv.DictReader(open('data/strategy_intake/lane_c_candidates.csv',encoding='utf-8-sig')));print(Counter(r['birth_batch'] for r in rs))"
python scripts/backtest/lane_c_formula_miner.py mine --smoke --population 30 --generations 3 --universe-n 40 --dry-run  # 烟测演练
python scripts/backtest/factory_intake_pipeline.py race    # C/C2 漏斗
python -m pytest tests/backtest/test_lane_c_formula_miner.py tests/backtest/test_lane_c2_agentic_miner.py tests/backtest/test_mcts_expression_search.py -q
```
