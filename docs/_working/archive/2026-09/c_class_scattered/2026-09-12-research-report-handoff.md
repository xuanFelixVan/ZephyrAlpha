---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：未结案（仍有待办）。处置=**保留**。**
>
> **✅ 已完成（2 条，摘录）**
> - L23: ## 2. 已完成并入库（全部可审计）
> - L61: - `scripts/ch/backfill_research_report_full.py`（研报历史回补，已完成使命，留档）
>
> **⚠️ 未完成（3 条，逐条摘录）**
> - L9: > 一句话现状：**数据侧+派生层+因子函数库全部落地并入库；下一步是 C2 因子评估（按纪律排队 P0 主线之后）**。
> - L16: - 本批主题：把"券商研报"从三处未接线雏形做成**全链路就绪**的数据资产——
> - L69: **因子层（C2 待评估的料）**
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 23 个，其中判废弃 0、路径漂移 0）+ commit 提及 3 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# 交接包：研报/一致预期消费端（2026-09-12 全天工作 → 新会话）

> 交接人：研报/expectation 会话（WorkBuddy，commit 14b7bb18ce 落批）。
> 接收人：新对话（讨论/继续研报消费端）。
> 一句话现状：**数据侧+派生层+因子函数库全部落地并入库；下一步是 C2 因子评估（按纪律排队 P0 主线之后）**。

---

## 1. 项目背景 30 秒版

- ZephyrAlpha = A 股量化系统，100% AI 开发。宪法=`AGENTS.md`（L0，唯一必读）。
- 本批主题：把"券商研报"从三处未接线雏形做成**全链路就绪**的数据资产——
  研报明细（事件流）→ 一致预期派生层（每股每日矩阵）→ 预期因子族（纯函数库）。
- 核心价值：不用付费数据商，自建 PIT 正确的一致预期（对标朝阳永续原理），
  支撑华泰金工系列公开公式（预期修正/超预期/分歧度/异常覆盖/评级动量）。
- 纪律要点：PIT 铁律（只认 publish_date）、禁"游结论"（因子结论必走 SOP-B 台账+run 档案）、
  回测通道排队（C2 评估排在 P0 主线之后）。

## 2. 已完成并入库（全部可审计）

| 项 | 产物 | 实况 |
|----|------|------|
| 研报明细表 | `c3_fundamental.research_report`（DS-228/JOB-090） | 146,633 行 / 4,695 只 / 2017-01-02~2026-09-11 / EPS 非空率 92.7% / 茅台抽查与东财一致 |
| 日度增量 | capability `research_report_detail` + 任务 `research_report_detail_incremental` | 每交易日 20:30（research_nightly 时段）自动跑 |
| C1 派生层 | `c3_fundamental.consensus_daily`（DS-229/JOB-091） | 6,775,964 行，(symbol, trade_date, forecast_year)，PIT 铁律内嵌 |
| C2 预备 | 预期因子纯函数库 EXP-01~06 + 14 单测全绿 | 未做 SOP-B 评估（排队中） |
| PIT 扩表 | pit_query 白名单 +research_report（锚列参数化） | 已由 PIT 哨兵会话随批落地（271dd14576） |
| 提交 | `14b7bb18ce`（12 文件）+ 前批 5 文件被三会话正常捎带 | git log 可查，零回退 |

## 3. 排队项（有意分期，非烂尾）——新会话按此推进

| 期 | 内容 | 前置/依赖 |
|----|------|----------|
| C1.5 | consensus 重建挂夜间调度（research_nightly 后串跑） | 无，可随时做 |
| **C2** | 预期因子评估：factor_registry 登记 expectations 族 → backtest_backlog 预注册 → SOP-B ④⑤⑥ 逐因子出证（multifactor_pit_backtest / layered_backtest 现成引擎） | **排队 P0 主线后**；factor_registry.yaml 当前有他会话在途，登记前查占用 |
| C3 | 超预期事件填坑（event_factor_matrix 的 EarningsFactorData 契约已预留 consensus_before/after 字段） | C1 已就绪 |
| C4 | PDF 文本 LLM 管线（body_status/body_ref 列已预留；DeepSeek 六类结构化情感） | 建议等 P0 收口 |
| C5 | 信号融合（signal_fundamental 预期下修否决 + FundamentalInputBundle 扩字段） | SOP-C C5 解冻后 |

## 4. 必读文件（新会话按序读）

1. `AGENTS.md` — 宪法 L0（冷启动序列+硬规则）
2. `docs/_working/2026-09-12-expectation-consumption-design.md` — **消费端设计 v1.0**（本批总纲：§1 第一性原理/§2 调研/§3 五模块/§4 咬合点/§5 分期/§6 决策点）
3. `docs/_working/2026-09-12-research-report-data-plan.md` — 数据侧施工方案+验收单
4. `docs/01_policies_and_standards/sop/backtest_system_sop/` — SOP-B 七步循环（因子评估的流程真源）+ SOP-D 档案规范
5. `docs/_working/2026-09-12-data-layer-gap-analysis.md` — 数据分层体检（本次工作的起点全景）

## 5. 相关工作文件（全部路径）

**数据表 DDL 真源**
- `schemas/categories/fundamental/fundamental_research_report.py`
- `schemas/categories/fundamental/consensus_daily.py`

**脚本（构建/回补/部署）**
- `scripts/ch/build_consensus_daily.py`（consensus 重建 CLI：--start/--window/--symbols/--check PIT 交叉验证）
- `scripts/ch/apply_consensus_daily_ddl.py` / `scripts/ch/apply_research_report_ddl.py`
- `scripts/ch/backfill_research_report_full.py`（研报历史回补，已完成使命，留档）

**集成层（能力/任务/调度/PIT）**
- `src/zephyr/data/implementations/akshare_provider.py`（研报明细能力在 L2965 起：_research_forecast_map/_research_report_id/_fetch_research_report_detail 等 5 helper）
- `src/zephyr/data/config/tasks.yaml`（L579 research_report_detail_incremental）
- `src/zephyr/data/config/schedule.yaml`（L92 research_nightly）
- `src/zephyr/data/pit_query.py`（L211 白名单 + L216 锚列覆盖）

**因子层（C2 待评估的料）**
- `src/zephyr/factor/expectations.py`（EXP-01~06 纯函数）
- `tests/factor/test_expectations.py` / `tests/scripts/test_build_consensus_daily.py`

**登记表（C2 要动的）**
- `docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml`（10 类 10 族，预期条目为零；growth 族 L194 注记=种子）
- `docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml`（SOP-B 预注册；无注册不归档）
- `docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（factor_eval schema 已支持，EXP-FACTOR-EVAL-001 起无先例）
- `docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（DS-228/229、JOB-090/091 已在）

**评估引擎（现成，勿新建）**
- `src/zephyr/factor/analysis/multifactor_pit_backtest.py`（注入式回调+5 层 PIT 断言）
- `src/zephyr/factor/analysis/layered_backtest.py`（layered_returns/compute_layer_spread）

**C3/C5 咬合点**
- `src/zephyr/intelligence/event_factor_matrix.py`（EarningsFactorData L288-312、expectation_gap_with_revision_momentum L393-410）
- `src/zephyr/signal_fundamental/negative_veto.py`（frozen facts+纯函数裁决模式）
- `src/zephyr/intelligence/llm_fundamental_analysis.py`（FundamentalInputBundle L72-81）

## 6. 新会话第一步建议

1. 读必读文件 1-2（15 分钟）；
2. 与 Owner 确认 C2 评估是否放行（排队纪律：P0 主线跑完没有？）；
3. 放行则按序：factor_registry 族登记（D1：荐新建 expectations 族）→ backlog 预注册 → EXP-02 修正动量先跑（D2 首选，文献最强+我们数据最独特）。
