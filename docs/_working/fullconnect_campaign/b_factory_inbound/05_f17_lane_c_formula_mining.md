---
ttl: task_bound
title: F17 车道C·公式挖掘机（gplearn/智能体/MCTS 三轨）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F17 · 车道C-公式挖掘机（三轨）

> 挖矿基册=01_strategy_factory/05_f17_lane_c_formula_mining.md（SF-A）。本卷=独立复核+09-26/27 增量。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | kline_daily_hfq+technical_indicator 面板（CH，fetch_panel lane_c_formula_miner.py:328-）；config/factor_mining_whitelist.yaml（active，fail-closed :98-108）；158 种子=CH precheck_passed（lane_c2_agentic_miner.py:62-65） |
| 下游 | lane_c_candidates.csv **16 行**（4 批 09-14×8/09-15×2/09-22 A101×2+HF×4，09-27 复测）｜lane_c2_candidates.csv 8 行｜lane_c3_candidates.csv **仍不存在**→E2→auto_construct（C/C2） |
| 自动触发 | 无常驻；run_mine :401-405 E0 heavy 档问闸接线实证；--smoke 豁免留痕 |
| 真源注册表 | MOD-BT-155=:16026／158=:16033／202=:16075（grep 实证）；图 9 FAC-E1C partial；tests 三套在盘（formula_miner/agentic_miner/mcts）；Owner 09-14 四项裁定落地在码；设计稿=2026-09-14-fac-e1c-formula-mining-design.md |
| 门禁质量尺 | 白名单∩引擎算子 fail-closed；增量 IC 线 0.01；AST 原创性 Jaccard<0.8；节点上限 14；搜索/验收分离；白名单 md5 指纹出生证 |
| 运行状态 | **黄（Ollama 断供放大滞留）**。gplearn 最近出货 09-22；C2 最近 09-15；C3 零出货维持。09-26 E2 班审 C 渠道新批 5 条**全 defer_llm_unreachable**（E2-20260926-102842，09-27 CH 实证）——C 渠道漏斗更新为 1 pass/15 审+7 defer（含 09-15 两条件） |

## 二、子模块三级枚举
1. **代码面**：lane_c_formula_miner.py（run_mine :400-、make_panel_operators :116-、假说文本 v2 :246-261、compute_features :302-326——挖矿/考卷件共用唯一实现）｜lane_c2_agentic_miner.py 477 行（build_mechanism_prompt :103-、三道验收）｜mcts_expression_search.py:68-170（**半成品维持**：随机扩展主循环、UCB 未接 :145 自注 Simplified）。
2. **注册表/文档面**：path_ownership_map 三锚点；FAC-E1C（**store_refs 为空数组**——三轨出货台账未登记进图 9 store_refs，登记欠账）；factor_mining_whitelist.yaml；design_refs=AlphaGen/AlphaForge/DolphinDB。
3. **数据/任务面**：台账 16+8+0；零计划任务；E2 消费面 C 渠道 15 条已审（09-27 CH 批分布实证）。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**（155/158 built+202 半成品）。
- **骨架勘误/增量**：①SF-A 记"C 渠道 2 条 defer 滞留"——09-26 增至 **7 条 C defer**（+5 新审全 defer），滞留面扩大；根因双因=幂等 SQL 缺陷（deferred 被跳过）+Ollama 断供期新审直接 defer。②基册记 09-22 批号 A101/HF 命名漂移待查——维持待挖（需 09-22 班会话记录）。③FAC-E1C store_refs 空数组为基册未点名的登记欠账（三轨台账路径应入 store_refs）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | C 渠道 7 条 defer 滞留（LLM 断供期产物） | CH 批 E2-20260915-120800×2+E2-20260926-102842×5 全 defer_llm_unreachable | 施工（F21 侧）：幂等 SQL 排除 deferred+Ollama 恢复后重审 | P1 |
| 2 | C3 MCTS 名实差距+零出货+未挂编排 | :145 自注；csv 不存在；_LANE_SPECS 无 C3 | 施工 1 天接 UCB 或诚实降格/图 9 除名；出货后挂载 | P2 |
| 3 | 09-22 批号非 strftime 语义 | E1C-20260922-A101/HF 后缀 | 待挖：查 09-22 班记录；0.5 天批号规约回填 | P2 |
| 4 | GP 正式档（1000×50）从未实战 | 16 条全 smoke/小批档 | 运行任务：排正式档夜跑+E0 heavy 窗实战校准 | P2 |
| 5 | E2 过审率 1/27（C+C2） | CH 批分布（1 pass） | 非病灶（E2 防噪在工作）；假说文本 v2 已迭代防误杀 | P2（观察） |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核有增量：defer 滞留 2→7 条（新证据）；新增 store_refs 登记欠账；其余四条病灶维持。

## 六、复跑命令
```bash
python -c "import csv;from collections import Counter;rs=list(csv.DictReader(open('data/strategy_intake/lane_c_candidates.csv',encoding='utf-8-sig')));print(Counter(r['birth_batch'] for r in rs))"
ls data/strategy_intake/lane_c3_candidates.csv 2>&1     # 不存在=C3 零出货
python scripts/backtest/lane_c_formula_miner.py mine --smoke --population 30 --generations 3 --universe-n 40 --dry-run
python scripts/backtest/factory_intake_pipeline.py race
python -m pytest tests/backtest/test_lane_c_formula_miner.py tests/backtest/test_lane_c2_agentic_miner.py tests/backtest/test_mcts_expression_search.py -q
```
