---
ttl: task_bound
title: F18 车道D·产业链三高（BOM 拆解四支柱）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F18 · 车道D-产业链三高（three_high_screen）

> 挖矿基册=01_strategy_factory/06_f18_lane_d_three_high.md（SF-A）。本卷=独立复核+**09-26 新班重大增量**。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | PG ig_fact 三关系（SQL_MEMBER/SQL_BARRIER/SQL_CHOKEPOINT :62-82）+ig_company_metric；CH c3_fundamental.financial_indicator（announce_date PIT，TableRegistry _fin_sql :90-93）；config/chainmap_cluster_names.yaml |
| 下游 | three_high_candidates.csv 09-27 复测 **60 行/唯一 id 29**（三批：E1D-20260914-043752×20+055847×20+**E1D-20260926-102753×20**，09-26 10:27 新班）→E2（D 渠道）→E3 假说轨翻译（MOD-BT-190 取 D/B） |
| 自动触发 | 无常驻；编排 run 首步调用 run_screen——09-26 班即循此路径（10:27:53 进货→10:28:42 E2，时间戳互证） |
| 真源注册表 | MOD-BT-090=path_ownership_map.yaml:1550,16285（grep 实证）；图 9 FAC-E1D partial（**store_refs 空数组**——出货台账未登记，同 C 车道欠账）；tests/backtest/test_three_high_screen.py 在盘 |
| 门禁质量尺 | 出生证机器写入（:151-157）；零 LLM 依赖；candidate_id 对环节名 md5 稳定；PIT 只取 announce_date 最新行；winsorize 5/95；min_members=5+fin_coverage≥0.6 |
| 运行状态 | **绿（本体）+复跑已重启**：09-26 新班 20 行实证车道复活（推翻基册"09-14 后零新增"）；重叠堆积仍重（新批 20 行中 13 行与旧批 id 重叠，仅 7 个新环节进池） |

## 二、子模块三级枚举
1. **代码面**：three_high_screen.py——fetch_pg_sector_stats/fetch_ch_financial_stats/fetch_pg_chokepoint_stats :166-203｜score_three_high :107-126（growth .30/margin .25/barrier .25/chokepoint .20）｜build_hypothesis :135-148｜aggregate_sector_stats :206-240｜run_screen :243-274。
2. **注册表/文档面**：path_ownership_map:1550,16285；FAC-E1D（data_refs=ig_fact+chainmap_cluster_names，补真身路径注释在 yaml）；design_refs=Capponi/FinNLP 2025/ChainKnowledgeGraph；v5.1 升级路线=LLM 增补（实件 graph_enrich_staging 归 E3 名下，D 未消费）。
3. **数据面**：台账 60 行/29 唯一 id；D 渠道 E2 已审 15 条（8 pass/2 reject/5 defer，09-27 CH）；translated_manifest D 渠道 3 条 translatable=true 带考卷件（09-15 班）。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**（筛选器 built；增补消费线未闭合）。
- **骨架勘误**：①总册/SF-A"09-14 后零新增班次"**已被 09-26 新班推翻**——出货停滞的性质是"无事件触发器导致间歇手工班"，非车道死亡；mtimes 09-26 10:27 与 birth_batch 互证（非 09-23 合并事件污染族）。②基册记 40 行唯一 22——现为 60 行唯一 29（新批净增 7 环节），重叠批堆积病灶维持且继续累积。③FAC-E1D store_refs 空数组登记欠账（同 FAC-E1C）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 重叠批堆积+head(limit) 饥饿 | 60 行唯一 29；新批 20 行 13 重叠 | 施工：卸货前按 candidate_id 去重（学 lane_b load_existing_ids）或 E2 侧过滤后 tail；0.5 天 | P1 |
| 2 | D 渠道 5 条 defer 滞留 | CH 批 E2-20260915-120740 全 defer | 施工（F21 侧幂等修复+Ollama 恢复） | P1 |
| 3 | LLM 增补线跨轨割裂（193 staging→D 未消费） | graph_enrich_staging 挂 FAC-E3 名下；D 无消费边 | 待裁：跨 SF-B/E3 边界——接线消费或图 9 画清依赖边 | P2 |
| 4 | 咽喉支柱数据稀疏兜底偏置 | :238-239 fillna(0)+兜底=中性分 | 施工：证据缺失单列 flag 降权；1 天 | P2 |
| 5 | FAC-E1D store_refs 空数组 | strategy_production_map.yaml:145-166 | 文档工：下版图补登记 | P2 |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核有重大增量：车道已复跑（勘误①）；堆积病灶量化更新（60/29）；其余维持。

## 六、复跑命令
```bash
python -c "import csv;from collections import Counter;rs=list(csv.DictReader(open('data/strategy_intake/three_high_candidates.csv',encoding='utf-8-sig')));print(len(rs),len({r['candidate_id'] for r in rs}),Counter(r['birth_batch'] for r in rs))"
python scripts/backtest/three_high_screen.py screen --top 20 --dry-run
python -m pytest tests/backtest/test_three_high_screen.py -q
```
