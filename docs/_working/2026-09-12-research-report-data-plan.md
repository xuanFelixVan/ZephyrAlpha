---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（1 条，摘录）**
> - L8: > 已完成：数据源验证（全网）+ 现有链路代码级摸底 + **三个零冲突新文件已落盘**。
>
> **⚠️ 未完成（2 条，逐条摘录）**
> - L9: > 待办：本方案 §3 的共享文件改动（需持 claim 施工）→ 验收 → 全市场回补。
> - L21: | 本方案 | 新建独立明细表 `c3_fundamental.research_report` + 回补器（**已落盘**）；共享文件接线（**待施工**）；现有链路并行不动，二期退役 |
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 2 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 研报+分析师预测数据侧施工方案（定稿 2026-09-12）

> Owner 拍板：先搞定数据（数据源→建表→集成→下载），模块/分析后置。
> 已完成：数据源验证（全网）+ 现有链路代码级摸底 + **三个零冲突新文件已落盘**。
> 待办：本方案 §3 的共享文件改动（需持 claim 施工）→ 验收 → 全市场回补。

---

## 0. 结论速览

| 项 | 结论 |
|----|------|
| 数据源 | 东财研报中心（AKShare `stock_research_report_em`，免费）。按个股深回溯（茅台实证 2017-08 起 771 条；接口参数 beginTime=2000-01-01）。每份研报自带：机构/东财评级/行业/日期/**预测期 0/1/2 的 EPS 与 PE 数值**/PDF 直链 |
| 一致预期历史 | 不买数据商：用研报明细按 publish_date 自聚合 = PIT 正确一致预期（朝阳永续原理）。**P1-C 就此解决** |
| analyst_forecast 表 | 维持现状（快照累积设计正确；`stock_profit_forecast_em` 只给当前快照=接口限制已裁定，官方一致预期对照价值保留） |
| 现有链路问题 | research_report_incremental（tasks.yaml:1242）每天在拉，但把 EPS/PE 数值、个股代码、评级变动全丢了，"机构：X\|评级：Y"拼串塞 news_data 共表 |
| 本方案 | 新建独立明细表 `c3_fundamental.research_report` + 回补器（**已落盘**）；共享文件接线（**待施工**）；现有链路并行不动，二期退役 |

## 1. 已落盘的三个新文件（零冲突，直接可用）

| 文件 | 作用 | 状态 |
|------|------|------|
| `schemas/categories/fundamental/fundamental_research_report.py` | DDL-as-Code 真源（22 业务列+审计列+TRAE-082 MATERIALIZED 派生，ReplacingMergeTree(ingest_ts)，ORDER BY (symbol,publish_date,report_id)） | ✅ 已写 |
| `scripts/ch/apply_research_report_ddl.py` | 建表+验证（base 账号执行 DDL，#ARCH-CH-027；`--verify` 仅验证；exit code 诚实） | ✅ 已写 |
| `scripts/ch/backfill_research_report_full.py` | 全市场回补器：断点续作/控频 0.4s/单股失败跳过/report_id 去重预检/EPS 动态年份列展开/`--check` 验收模式（exit 0=有数据） | ✅ 已写 |

建表与试跑命令（exit code 可观测）：

```powershell
python scripts/ch/apply_research_report_ddl.py          # 0=建表+验证成功
python scripts/ch/backfill_research_report_full.py --limit 5   # 试跑 5 只（茅台/平安等头部在列首附近）
python scripts/ch/backfill_research_report_full.py             # 全市场约 1-2 小时（断点续作可中断重跑）
python scripts/ch/backfill_research_report_full.py --check     # 验收：rows/date_range/symbols/eps非空率（exit 0=有数据）
```

## 2. 表结构要点（c3_fundamental.research_report）

- 主键序 `(symbol, publish_date, report_id)`，report_id=PDF 链接 infoCode 提取（兜底 MD5），ReplacingMergeTree(ingest_ts) 双保险去重。
- 预测期列 `fy0/fy1/fy2_year + eps_fyN + pe_fyN`：akshare 动态年份列（"{YYYY}-盈利预测-收益/市盈率"）在解析侧按年份升序映射并**落年份值**——年份滚动不漂移。
- `body_status/body_ref` 为 PDF 全文二期预留列（本阶段只存 `source_url` 链接，不做批量下载——合规与体量后议）。
- 一致预期派生（二期消费端阶段）：`SELECT symbol, toDate(publish_date) as d, avg(eps_fyN) ... GROUP BY symbol, d` 按 as-of 滚动，天然 PIT，无前视。

## 3. 共享文件改动（paste-ready，持 claim 施工会话执行）

### 3.1 akshare_provider.py 新增 capability（日度增量用）

参考既有 `_fetch_research_report`（akshare_provider.py:2902）与注册点 L733/L753/L367-369。新增 `_fetch_research_report_detail`：复用 `ak.stock_research_report_em(symbol)`，解析逻辑与 `backfill_research_report_full.parse_rows` **同源**（建议把 parse_rows 提为共享函数防两处漂移），返回 FetchResult(table=c3_fundamental.research_report, columns=INSERT_COLUMNS, ...)。CapabilityContract 注册 capability 名建议 `fetch_research_report_detail`。

### 3.2 tasks.yaml 新增任务（照 analyst_forecast_incremental 条目式样，tasks.yaml:567-577）

```yaml
- task_id: research_report_detail_incremental
  table: c3_fundamental.research_report
  source: akshare
  capability: fetch_research_report_detail
  schedule: daily_event          # 或新增 research_nightly 时段（见 3.3）
  incremental: true
  date_col: publish_date
  fallback_sources: []           # DATA-TASK-COMPLETENESS gate 会 warn，登记理由"东财研报无第二免费源"
```

### 3.3 schedule.yaml：挂 `daily_event`（19:00 工作日）即可；如嫌与财报事件任务抢窗口，加 `research_nightly`（20:30 周一~五）。

### 3.4 business_data_categories.yaml：加品类 `research_report_detail`（真源 #ARCH-CH-024，download-status 面板可见的前提）。

### 3.5 data_asset_registry.yaml 登记（照 DS-199 块格式；CH 实况回填在回补完成后）：

- `DS-228 c3_fundamental.research_report`（physical_type=clickhouse_table，domain_id=D_FACTOR，pit_policy=strict——publish_date 即公告时点，survivorship_free=true 退市股研报仍在接口历史里，produced_by_source=SRC-AKSHARE-001）
- `JOB-089 ingest.akshare_research_report_detail`（daily_event）；回补器记一次性 JOB-090 或仅在 format_summary 注记。

## 4. 施工顺序（Owner 视角的四步）

1. **建表+试跑**（可今天做，新文件已就位）：apply DDL → `--limit 5` 试跑 → 人工抽查 2-3 只 vs 东财网页（评级/预测值对得上）。
2. **全市场回补**：`--limit 0` 全量，断点续作，预计 1-2 小时；完成后 `--check` 验收 + 回填 registry CH 实况。
3. **正式集成（§3 五处改动）**——✅ **2026-09-12 19:24~19:50 完成**：akshare_provider 新增 capability `research_report_detail`（_AKSHARE_CAPABILITIES+CapabilityContract+表常量+_parse/_fetch 方法）；tasks.yaml 新增 research_report_detail_incremental（schedule=research_nightly 20:30 工作日独立时段，不与 daily_event 抢池）；schedule.yaml 新增 research_nightly 槽位；business_data_categories.yaml 登记品类 fund_research_report；数据资产登记表 +DS-228 +JOB-090（v1.7.0，entry_counts 227/89）。**验证探针 ALL_OK（19 项）**：四 YAML 解析/任务条目/时段/品类→表解析/DS-JOB 登记/能力双侧注册/实拉解析 22 元组/端到端 fetch 冒烟（rows=0=窗口内已全在库，写侧去重符合预期）。10 文件已 git add，提交待 CREATE-GUARD token/翻译登记（建议 TRAE 管道执行，gate 输出可视）。
4. **二期（消费端阶段再说）**：一致预期派生层+预期修正/超预期/分歧度因子族；PDF 批量下载解析（body 列已预留）；research_report_collector（DORMANT）裁定复活或退役——新表已覆盖其数据价值，评级变动事件可从表 diff 派生；research_rating.py 从字符串解析切到结构化表；旧 research_report_incremental 从 news_data 退役（省 30min 全市场轮询）。

## 5. 裁定与风险

| 项 | 裁定 |
|----|------|
| 现有 news_data 链路 | **并行不动**（新表日度增量挂夜间时段，双拉成本可接受；避免动 sentiment/tagging 现有消费方）。二期消费切换后退役旧任务 |
| news_data 无 DDL-as-Code 真源 | 治理欠账，单独立项（rebuild_news_data.py 仅为重建脚本非真源） |
| 接口风险 | 控频 0.4s/股+断点续作+单股失败跳过；EM 无第二免费源（fallback_sources 登记理由） |
| 深度预期 | 实际回溯≈2017 年起（接口 2000 参数是上限，覆盖以返回为准）——8 年+历史足够因子回测 |
| 合规 | 只存元数据+预测数值+链接；PDF 全文下载延后至二期专项（体量与合规再评估） |
| 施工纪律 | 提交走 git_commit.py；新建 .py 需 CREATE-GUARD creation_token + add_module_translation 登记；claim 后再改共享文件（tasks.yaml/akshare_provider/registry 今日有他会话 staged 历史） |

## 6. 验收清单

- [x] `apply_research_report_ddl.py --verify` exit 0（2026-09-12 17:00 通过）
- [x] 试跑 5 只：463 行/9.5 年，EPS 值抽查相符（茅台 69.83/18.59 与接口原值一致）
- [x] 全市场回补完成（2026-09-12 16:48~18:35，exit 0）：**146,633 行 / 覆盖 4,695 只（5555 只中 860 只无研报覆盖属正常）/ 日期 2017-01-02~2026-09-11**
- [x] eps_fy0 非空率 **92.7%**（135,921/146,633），eps_fy1 88.7%——远超 60% 验收线
- [x] 抽查茅台：2026-08-21 西南证券"买入" fy2026 EPS 69.83 / PE 18.59，与东财源值一致；report_id=AP202608211828244348（infoCode 提取正确）
- [x] 评级分布实录：买入 101,041（68.9%）/ 增持 33,044（22.5%）/ 空 11,361 / 持有 610 / 中性 544 / 卖出 30 / 回避 2 / 减持 1——**卖方评级"买入+增持"占 91% 的系统性乐观偏置**，后续评级因子化时必须数值化+去偏（历史已知问题，与朝阳永续一致预期口径对照可校准）
- [ ] registry DS-228/JOB-089 登记 + CH 实况回填（本节实况即材料：146,633 行，valid_since=2017-01-02）——待持 claim 施工会话随 §3 五处接线一并落地
- [ ] 日度增量任务上线后 download-status 面板可见 research_report_detail 品类

## 7. 回补完成实录（2026-09-12）

| 项 | 值 |
|----|----|
| 运行 | scripts/ch/backfill_research_report_full.py，16:48~18:35（约 1h47m），exit 0，单股零致命失败 |
| 行数 | 146,633（FINAL 去重后） |
| 覆盖 | 4,695 / 5,555 只 A 股 |
| 历史深度 | 2017-01-02 ~ 2026-09-11（9.7 年） |
| EPS 预测覆盖 | fy0 92.7% / fy1 88.7% |
| 结论 | **P1-C（一致预期历史回补）数据侧完成**——一致预期可按 publish_date 自聚合（PIT 正确），免付费数据商 |
