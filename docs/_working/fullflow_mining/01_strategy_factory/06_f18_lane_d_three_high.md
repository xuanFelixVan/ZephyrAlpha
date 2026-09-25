---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F18 车道D·产业链三高（BOM 拆解四支柱）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-090
map_node: FAC-E1D
---

# F18 · 车道D-产业链三高

## 一、环节定义与边界
一句话：ig_fact 图谱 BOM 拆解——环节（belongs_to_sector 板块）×四支柱（高增长/高利润/高壁垒/咽喉度）winsorized z 分加权合成→topN 环节生成确定性假说→出生证卸 three_high_candidates.csv，交 E2。
上游供料=PG ig_fact 三关系（belongs_to_sector/produces/supplies_to）+ig_company_metric（客户集中度）+CH c3_fundamental.financial_indicator（announce_date PIT）；下游消费=E2 预审（D 渠道）→E3 假说轨翻译（MOD-BT-190 取 D/B 过审）。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | SQL_MEMBER/SQL_BARRIER/SQL_CHOKEPOINT 三常量（three_high_screen.py:62-82）；财务表名走 TableRegistry（_fin_sql :90-93，#ARCH-CH-024）；config/chainmap_cluster_names.yaml（图9 data_refs） |
| 下游消费 | three_high_candidates.csv 实测 40 行=2 批（E1D-20260914-043752×20+055847×20，唯一 candidate_id 22——同环节 id 稳定跨批重叠）；E2 台账 D 渠道 15 条（8 pass/2 reject/5 defer）；E3 translated_manifest 4 条 D 渠道（09-15 班） |
| 自动化触发 | 无常驻（manual；factory_intake_pipeline run 首步调用 run_screen） |
| 真源与注册表 | MOD-BT-090 在 path_ownership_map.yaml:1550,16285；tests/backtest/test_three_high_screen.py 在盘；图9 FAC-E1D build_status=partial（LLM 增补管线未建=v5.1 升级路线）；Capponi 图谱多跳验证为方法论 design_refs |
| 门禁与质量尺 | 出生证机器写入（:151-157）；零 LLM 依赖（本车道）；candidate_id 对环节名 md5 稳定可重跑；财务列只取 announce_date 最新行（PIT :160-163）；winsorize 5/95 防极值绑架（:96-104）；聚合过滤 min_members=5+fin_coverage≥0.6；本车道不评分不及格线 |
| 当前运行状态 | **绿（本体）/停（产出）**。最近真实出货=2026-09-14 05:58（E1D-20260914-055847）；文件 mtime 09-24 07:27 与 birth_batch 不符——09-23/09-24 批量合并事件污染 mtime（多文件共享 09-23 14:21 mtime 族），**以 birth_batch 为准**；09-14 后零新增班次 |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| 三库聚合 fetch_pg_sector_stats/fetch_ch_financial_stats/fetch_pg_chokepoint_stats | scripts/backtest/three_high_screen.py:166-203 | built（PG 只读连接+CH writer 通道读） |
| 四支柱评分 score_three_high（纯函数） | 同上:107-126 | built（growth 0.30/margin 0.25/barrier 0.25/chokepoint 0.20） |
| 确定性假说文本 build_hypothesis | 同上:135-148 | built（同输入同句） |
| 环节聚合 aggregate_sector_stats（中位数+覆盖过滤） | 同上:206-240 | built |
| 卸货 run_screen（dry-run 诚实回看） | 同上:243-274 | built |
| LLM 增补管线（年报/公告→关系抽取→staging） | — | **另轨已建**：graph_enrich_staging.py（MOD-BT-193，图9 FAC-E3 algo_note_extra 声明"绝不写 ig_fact 正图，入图需 Owner 审核"）——归 E3/图谱线，本车道仅消费其产物（未接线） |
| 增补→ig_fact 入图通道 | — | missing（Owner 门位，裁定另批） |

## 四、堵点与病灶
1. **产出停滞（09-14 后零班次）**：同 F14 触发缺位根因；修法=事件触发器落地后 D 为 run 首步自动随跑；无独立施工。
2. **重叠批堆积**：top20 环节两批重叠 18 个→csv 40 行唯一 id 22；幂等由 E2 侧 id 去重兜底（CH 实证无重复判定行），但 csv 侧堆积+head(limit) 组合挤占 E2 名额（F21 堵点③同根）；修法=D 车道卸货前按已存在 candidate_id 去重（学 B 车道 load_existing_ids 模式）或 E2 侧过滤后 tail；0.5 天；本车道可修。
3. **咽喉支柱数据稀疏**：downstream_breadth/supply_pressure 依赖 produces+supplies_to 边密度，缺失时 fillna(0)+supply_pressure=downstream_breadth 兜底（:238-239）——兜底语义会让"无证据环节"得中性分而非低分，倾斜排序；修法=咽喉证据缺失单列 flag 并降权；1 天；本车道可修。
4. **LLM 增补线跨轨割裂**：graph_enrich_staging（193）已建但 D 车道未消费其 staging 产物，图9 把 193 记在 E3 名下——增补→进货的价值链未闭合；修法=接线消费或图9 把依赖边画清；待裁（跨 SF-B/E3 边界）。

## 五、提速与合并机会
- 零 LLM 设计使 D 是全厂最便宜的进货道（编排默认首步）；若 E2 幂等+去重修复，D 可高频重跑（成本≈三次 SQL 聚合）。
- 与 KS 组 chain_registry/ig_fact 审计面共享真源（F12 产业链图谱=873 条数据面），无需重复建数。

## 六、自审闸三态
- **三态结论：partial**（筛选器+卸货 built；LLM 增补消费线未闭合+重叠堆积小病灶）。
- **差什么才算 built**：①candidate_id 去重前置（或 E2 侧修后书面确认 csv 堆积无害）；②193 staging→D 的消费边接通（或裁定入图 Owner 批后由 ig_fact 直供，则 D 无需改）；③进入常态班次（随触发器解决）。

## 七、复核命令
```bash
python -c "import csv;from collections import Counter;rs=list(csv.DictReader(open('data/strategy_intake/three_high_candidates.csv',encoding='utf-8-sig')));print(len(rs),len({r['candidate_id'] for r in rs}),Counter(r['birth_batch'] for r in rs))"
python scripts/backtest/three_high_screen.py screen --top 20 --dry-run   # 只看不写演练
python -m pytest tests/backtest/test_three_high_screen.py -q
```
