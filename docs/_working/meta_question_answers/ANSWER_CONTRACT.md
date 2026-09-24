---
ttl: task_bound
completes_when: 283 问全部有 outcome 且总账交付后随包归档
title: st-metaq-20260923 答题纪律契约（分包子代理必读）
owner: ZephyrAlpha-Owner
session: st-metaq-20260923
date: 2026-09-23
---

# 答题纪律契约（每问答题前必须重读一遍）

## 0. 身份与边界
- 你是 st-metaq-20260923 的分包答题代理。总包已认领全部 283 问，你只管答题产证据。
- **禁令**：禁写 PG（含 meta_question 任何表；回写由总包单写者 ingest 完成）；禁 git 操作；禁写生产路径（data/ 业务目录、注册表、宪法）；禁跑 pytest 全量套件；禁动他问的结论。
- 探针脚本只准落 `.runtime/tmp/st-metaq-20260923/probes/`，证据 JSON 只准落 `docs/_working/meta_question_answers/results/`。

## 1. 环境 API（每条命令前先修 PATH）
```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
```
```python
# CH 只读（clickhouse_driver.Client，无 cursor，用 execute）
from zephyr.infrastructure.database_service import DatabaseService
svc = DatabaseService()
conn = svc.get_clickhouse_conn(role="reader")
rows = conn.execute("SELECT ... FROM c1_market.kline_daily WHERE trade_date <= '2025-09-09' ...")
# PG 只读（默认 read_only=True，禁传 read_only=False）
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
pg = get_depgraph_pg_connection()
cur = pg.cursor(); cur.execute("SELECT ..."); ...
```
- 库名前缀：行情=c1_market、财务=c3_fundamental、回测=c1_backtest、图谱/概念=PG public、问题表=PG meta_question schema。
- 每条取数 SQL **必须**带 `<= '2025-09-09'`（PIT 闭卷切点）。涉及时戳/公告日的口径题同样受切点约束。

## 2. 小挖矿三查（每问动探针前，结论写进 result JSON 的 three_check 字段）
1. **数据在库吗**：表存在+行数够样本窗（骨架台账 01_skeleton_ledger.json 的 need_tables 已给初判，你要用真实查询复核）。
2. **字段口径清楚吗**：因子/事件定义能从题面+exam_plan 无歧义落地吗？字段名要 DESCRIBE 实证，禁凭直觉猜列名。
3. **判据能机械跑吗**：threshold 里的数字比较能用代码复现吗？
- 三缺一 → outcome=insufficient，precondition_gap 写清"缺哪个数据源/哪段管线/什么口径"，禁硬答。

## 3. outcome 判定树
- **pass**：三查全过+真实跑数+结果过 threshold。结论必须含数字（IC 值/t 值/样本数/窗口）。
- **fail**：三查全过+真实跑数+结果不过 threshold。两种 fail 必须区分写进 conclusion：
  - `fail_type=no_alpha`：因子/信号在闭卷窗内真实数据上无预测力（如实报数字）。**只登记，禁任何"修出预测力"的施工**（改参数重跑出好看数字=换卷作弊）。
  - `fail_type=infra`：数据缺失/管线断/机制未建导致的失败。转总包走 fail 大挖矿作业簿。
- **insufficient**：三查不全（数据没落库/窗口在切点后为零样本/口径无法机械落地/审计对象不存在）。写明缺什么、复考前置条件。
- 对"未建管线的登记审计问"（外围线 U4/U5 等）：审计对象不存在 → insufficient（注明"待管线建成后复考"），禁硬判 fail——但 U1/U2/U3 这类与源线谱册/DS 册文本比对的登记一致性问**现在就能考**，如实判 pass/fail。
- 结论禁含切点后数据：窗口 `[start, 2025-09-09]`；切点后仅可作"现状观察"且不得进入任何校正/阈值比较。

## 4. result JSON 契约（一问一文件：results/<q_id>.json，UTF-8）
```json
{
  "q_id": "PQ-NNNN",
  "exam_ref": "st-metaq-20260923/probe/<batch>_<q_id>",
  "outcome": "pass|fail|insufficient",
  "fail_type": "no_alpha|infra|null(insufficient或pass时)",
  "confidence": 0.0,
  "conclusion": "一段话结论，含关键数字与口径（fail 时写明 no_alpha/infra 区分）",
  "data_window": {"start": "YYYY-MM-DD", "end": "2025-09-09"},
  "pit_assertion": "本题取数与校正只用了切点前数据；具体断言一句",
  "three_check": {"data": "OK|NO+说明", "caliber": "OK|NO+说明", "mechanical": "OK|NO+说明"},
  "evidence": [{"probe": "脚本相对路径", "query": "SQL/检查逻辑原文（截断≤500字）", "result": {"关键数字...": 0}}],
  "threshold": "从 exam_plan 抄录",
  "notes": "复考前置/缺口/备注"
}
```
- confidence 口径：1.0=全窗口机检数字齐；0.7=机检+部分口径判断；0.4=主要靠登记册文本比对；0.2=仅现状观察。
- 禁改他问文件；禁重写已存在的 results/<q_id>.json（发现已存在=读一下，若完整就跳过该问）。
- 字段名实证前科登记：macro_data 指标名=FRED_* 英文命名（中文名匹配漏检）；kline_index 锚=symbol 非 symbol_canonical；tick_data.timestamp=北京时间−8h；PE/PB 在 stock_indicator 非 stock_daily_basic。

## 5. 比对基准（登记核验类）
- 源线谱册：`docs/_working/chain_piling_campaign/02_source_line_registry.md`（29 线三档 + 每线 U1-U6 现答）。
- 数据源册：`architecture_model/data/data_sources_registry.yaml`（DS-* 元数据：status/coverage/成本）。
- U1 核验=题面宣称的问题域 vs 该线 U1 信号词集能否覆盖（语义判断，逐词列对照表进 evidence）。
- U2 核验=该线登记渠道/成本 vs DS 册 status/coverage 字段（逐字段对照进 evidence）。

## 6. 完工汇报格式（你的最后一条消息）
`BATCH <name> DONE: N问 pass=X fail=Y(no_alpha=a infra=b) insufficient=Z | 未答清单+案由（若有）`
