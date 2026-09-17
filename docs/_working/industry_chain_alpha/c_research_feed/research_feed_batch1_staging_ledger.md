---
module_id: c_research_feed.research_feed_batch1_staging_ledger
ttl: task_bound
---

# 线C 首批 50 篇研报暂存抽取台账（batch1）

> Owner 待批的首批 50 篇试点（C 簿 §5）执行件。**候选≠事实：本台账全部为暂存候选关系，绝不写 ig_fact 正图**（入图需 Owner 审核另批，MOD-BT-193 不变量）。

## 1. 批次信息

| 项 | 值 |
|----|-----|
| 会话 | st-igalpha2-20260918（2026-09-18 夜班） |
| 工具 | `scripts/backtest/graph_enrich_staging.py extract --sample 50 --source research` |
| 模型 | qwen3:8b（本地 OllamaChat，内置 LSG 网关，零外部 LLM 调用） |
| 源表 | c3_fundamental.research_report（146,669 行，2017-01-02~2026-09-13） |
| 全文源 | data/c4_pdf_cache/{2017..2021}/{report_id}.pdf（F 盘 junction，勿回迁） |
| 暂存 CSV | `.runtime/tmp/igalpha2_20260918/research_staging_batch1.csv`（9 列 schema，50 行） |
| 抽取时点 | 2026-09-18T05:10:42+08:00（单批原子） |

## 2. 结果统计

| 指标 | 值 |
|------|-----|
| 抽样 | 50/50 全部 PDF 全文级（rr:pdf: 前缀，零 rr:meta: 摘要级降级） |
| accepted（staged） | **50/50**（confidence 0.9~0.95，evidence 零空值=逐字原文摘录全过防幻觉门） |
| rejected / llm_error | 0 / 0 |

## 3. 暂存候选样例（前 10，全量见 CSV）

| report_id | supplier | product | customer | conf |
|-----------|----------|---------|----------|------|
| AP202112311537638006 | 山西煤层气有限责任公司 | 煤层气 | 蓝焰控股 | 0.95 |
| AP202112311537680049 | 斯达半导 | IGBT模块和分立器件 | 国内主流光伏逆变器客户 | 0.95 |
| AP202112311537711498 | 高瓴投资 | 战略投资 | Qumei Runto | 0.95 |
| AP202112311537732599 | 恒润股份 | 风塔法兰 | 维斯塔斯、金风科技 | 0.95 |
| AP202112311537700210 | 宁德时代 | 动力电池 | 浙江远景 | 0.95 |
| AP202112311537680668 | 当升科技 | 固态锂电材料 | 卫蓝新能源 | 0.95 |
| AP202112311537643140 | 万顺新材 | 高精度电子铝箔 | 卓越新材料 | 0.95 |
| AP202112311537638008 | 科力尔 | 伺服系统 | 华为 | 0.95 |
| AP202112311537658157 | 南通拓邦尤能科技有限公司 | 锂电池项目 | 南通市 | 0.95 |
| AP202112311537711799 | 南玻A | 光伏玻璃 | 光伏电站 | 0.95 |

## 4. 抽取口径（防幻觉三闸，与新闻源同一契约）

1. evidence 必须正文逐字摘录，无原文支撑=丢弃；2. supplier≠customer；3. confidence<0.7 丢弃。
prompt=`build_research_extract_prompt`（研报标题+机构/行业/评级元数据头+全文前 1500 字）。

## 5. 已知边界与后续

- 抽样级联=2017-2021 窗口倒序优先 PDF 全文可定位行；2022+ 全文反爬断档（C 簿 §6），本轮未涉。
- 候选主体名未对齐实体身份证库（线D），"公司/下游企业"类泛称入图前须消解。
- 入图批准流走 graph_enrich_ingest --approve 先例（C-5 已挖），本批仅为 Owner 送审材料。
