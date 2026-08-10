---
ttl: permanent
doc_type: architecture_view
title: A股"特殊交易日"数据资产全景与治理（含 hk_trade_calendar 语义错配修复 #ARCH-DATA-001/002）
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.1.0"
date: 2026-08-10
topic: special_trading_days_data_assets
scope: 07_trading_decision_architecture / 03_modules_database
related_issues:
  - "#ARCH-SPECIAL-DAYS（特殊日子数据资产立项）"
  - "#ARCH-DATA-001（hk_trade_calendar 语义错配即时止血）"
  - "#ARCH-DATA-002（capability-API 语义对齐治本）"
---

# A股"特殊交易日"数据资产全景与治理

> 本文档承接原 `.trae/documents/special_trading_days_data_ingestion.md`（工作规划，不入 git）的规划职责，
> 转为正式 design_memo。`business_data_categories.yaml` 与 `tasks.yaml` 中对该旧路径的引用为悬空引用，
> 待统一指向本文档（见 §6.4）。

## 1. 文档定位

### 1.1 为什么有这份文档

用户识别到 A 股存在大量会引发"资金避险 / 资金流出 / 价格异常"的"特殊日子"——除权日、除夕、
股指期货交割日、月末季末、LPR 公布日、MSCI 调整、新股申购、ETF 赎回等。这些日子是回测与实盘
信号的重要前向特征，需作为数据资产纳入 ClickHouse，让回测和信号系统能直接 JOIN。

施工过程中附带发现一个已有 bug：`akshare_provider._fetch_hk_trade_calendar` 用 A 股日历
（`ak.tool_trade_date_hist_sina`）冒充港股日历，会污染 `c1_market.hk_trade_calendar`。该 bug
暴露出项目在"capability 名 ↔ 数据源 API 语义对齐"维度存在系统性治理盲区，需治本方案。

本文档同时承载三件事：
1. **特殊交易日完整清单**（用户最初要求的全集盘点）
2. **已施工数据资产盘点**（schema / 表 / 任务 / 派生，反映真实状态）
3. **待施工治本方案**（#ARCH-DATA-002，讨论清楚后再施工）

### 1.2 本文档不做裁定

- 不做新裁定（裁定落在 `architecture_issue_registry.yaml` 的 #ARCH-DATA-001/002）
- 只做"现状盘点 + 待施工讨论"，供后续 AI/人认领施工
- 治本方案的最终设计细节在 §5 讨论，定稿后回填本文档并转 active

## 2. 特殊交易日完整清单

按"会引发资金避险/流出/价格异常"的作用机理分四大类。**覆盖状态**列对齐 §3 实际施工盘点。

### 2.1 日历结构类（全市场事件，无 symbol）

| 事件 | 机理 | 落地表 | event_type | 覆盖状态 |
|---|---|---|---|---|
| 月末（最后交易日） | 季末粉饰+基金排名调仓 | calendar_event | month_end | ✅ 已派生 |
| 季末 | 季度粉饰+公募排名 | calendar_event | quarter_end | ✅ 已派生 |
| 半年末 | 中期排名+半年报窗口 | calendar_event | half_year_end | ✅ 已派生 |
| 年末 | 年度排名+年终调仓 | calendar_event | year_end | ✅ 已派生 |
| 股指期货交割日（每月第3个周五） | 交割日效应+期现收敛 | calendar_event | futures_delivery | ✅ 已派生 |
| 股指期权到期日 | 到期日效应 | calendar_event | index_option_expiry | ✅ 已派生 |
| ETF期权到期日（每月第4个周三） | 到期日效应 | calendar_event | etf_option_expiry | ✅ 已派生 |
| LPR公布日（每月20日，遇周末顺延） | 利率预期+地产链反应 | calendar_event | lpr_announcement | ✅ 已派生 |
| 港股通休市日（A股开盘但港股休市） | 北向资金停摆 | calendar_event | hk_connect_closed | ✅ 已派生（依赖 hk_trade_calendar，本次修复） |
| FOMC议息日 | 外围风险偏好传导 | calendar_event | fomc_meeting | ⏸ 表结构预留，manual 未填充 |
| 重要会议（两会/中央经济工作会议） | 政策预期+维稳 | calendar_event | major_meeting | ⏸ 表结构预留 |
| 印花税调整日 | 交易成本突变 | calendar_event | stamp_duty_change | ⏸ 表结构预留 |

### 2.2 日历表类（交易日历本身）

| 日历 | 落地表 | 数据源 | 覆盖状态 |
|---|---|---|---|
| A股交易日历 | trade_calendar | baostock / exchange_calendars XSHG | ✅ 已有 |
| 港股交易日历 | hk_trade_calendar | exchange_calendars XHKG | ✅ 本次修复（#ARCH-DATA-001，原 akshare 用 A股日历冒充） |

### 2.3 个股事件类（有 symbol）

| 事件 | 机理 | 落地表 | 数据源 | 覆盖状态 |
|---|---|---|---|---|
| 指数成分股调整（沪深300/中证500/中证1000） | 被动基金强制调仓 | index_adjustment | akshare | ✅ 已施工 |
| 新股申购+上市 | 打新冻结资金吸筹/上市资金分流 | ipo_schedule | akshare | ✅ 已施工 |
| 两融标的调整 | 杠杆资金被迫加减仓 | margin_target_adjustment | akshare | ✅ 已施工 |
| 红利税节点（除息日前1月/前1年） | 税动机交易（持股期限跨档） | dividend_tax_node（VIEW） | internal（rights_issue 派生） | ✅ 已施工 |
| 除权除息日 | 除权缺口+税节点触发源 | rights_issue（c3_fundamental） | akshare/ifind | ✅ 已有（非本次新增） |
| MSCI/富时调整 | 外资被动调仓 | msci_adjustment | manual（待接入） | ⏸ 表结构预留，disabled |
| 解禁日 | 解禁抛压预期 | share_unlock（c3_fundamental） | akshare/ifind | ✅ 已有 |
| 股权质押 | 平仓线风险 | equity_pledge（c3_fundamental） | akshare | ✅ 已有 |
| 回购 | 回购支撑 | repurchase（c3_fundamental） | akshare | ✅ 已有 |

### 2.4 待评估项（用户提及但尚未建表）

| 事件 | 评估 | 建议 |
|---|---|---|
| ETF 赎回日（大额申赎） | ETF 大额申赎引发成分股买卖，可能扰动流动性。但 A 股 ETF 申赎为 T+0 实物申赎，无固定"赎回日"；ETF 净赎回数据可从 `etf_nav` 衍生 | 暂不单独建表，需要时在查询层从 etf_nav 衍生净赎回指标 |
| 除夕（春节前最后交易日） | 已被 trade_calendar（is_open=0）+ year_end/month_end 覆盖，资金避险效应可由月末/年末事件捕获 | 不单独建表 |
| 分红股权登记日 | rights_issue 表已含 ex_date，登记日=ex_date-1，可查询层计算 | 不单独建表 |

## 3. 已施工数据资产盘点

> 反映 2026-08-10 真实状态。schema 文件均为 DDL-as-Code，由 `apply_market_tables_ddl.py` 自动发现建表。

### 3.1 schema 层（7 个文件，均在 `schemas/categories/`）

| schema 文件 | 表 | 引擎 | ORDER BY | 数据源 |
|---|---|---|---|---|
| market_calendar_event.py | c1_market.calendar_event | ReplacingMergeTree | (event_date, event_type) | internal |
| market_index_adjustment.py | c1_market.index_adjustment | ReplacingMergeTree | (index_code, effective_date, symbol) | akshare |
| market_ipo_schedule.py | c1_market.ipo_schedule | ReplacingMergeTree | (ipo_date, symbol) | akshare |
| market_margin_target_adjustment.py | c1_market.margin_target_adjustment | ReplacingMergeTree | (effective_date, symbol) | akshare |
| market_dividend_tax_node.py | c1_market.dividend_tax_node | **VIEW**（非 TABLE） | N/A | internal（rights_issue 派生） |
| market_msci_adjustment.py | c1_market.msci_adjustment | ReplacingMergeTree | (index_provider, effective_date, symbol) | manual（disabled） |
| market_hk_trade_calendar 相关 | c1_market.hk_trade_calendar | — | (cal_date) | internal（本次修复） |

设计要点：
- 个股事件表（index_adjustment / ipo_schedule / margin_target_adjustment / msci_adjustment）均带
  MATERIALIZED `exchange` + `symbol_canonical`（TRAE-082 universal 身份键，跨表 JOIN 用）
- calendar_event 无 symbol（全市场事件），不带 MATERIALIZED 派生列
- dividend_tax_node 为 VIEW，由 `c3_fundamental.rights_issue` 实时派生（除息日前1月=1月节点/前1年=1年节点），
  无独立存储、无调度任务，遵循"由现有数据派生不新建表"原则

### 3.2 business_data_categories.yaml 注册（6 条 + hk_trade_calendar）

注册于 `docs/03_modules/_cross_layer/database/business_data_categories.yaml` L1921-2019（"A股特殊日子数据资产"段）。
注意 L1923 引用 `special_trading_days_data_ingestion.md` 为悬空引用（见 §6.4）。

| category_id | table | enabled | data_source | sla |
|---|---|---|---|---|
| market_calendar_event | calendar_event | true | [internal] | L2 |
| market_index_adjustment | index_adjustment | true | [akshare] | L2 |
| market_ipo_schedule | ipo_schedule | true | [akshare] | L2 |
| market_margin_target_adjustment | margin_target_adjustment | true | [akshare] | L2 |
| market_dividend_tax_node | dividend_tax_node | true | [internal] | L3 |
| market_msci_adjustment | msci_adjustment | **false** | [manual] | L3 |
| market_hk_trade_calendar | hk_trade_calendar | true | [internal]（本次修复，原 [exchange]） | L2 |

### 3.3 tasks.yaml 采集任务（5 个 + hk_trade_calendar_refresh）

注册于 `src/zephyr/data/config/tasks.yaml` L2369-2433。注意 L2371 引用同上悬空。

| task_id | table | source | schedule | incremental | 状态 |
|---|---|---|---|---|---|
| calendar_event_refresh | calendar_event | internal | monthly_static | false（全量重算幂等） | ✅ 依赖 trade_calendar_refresh |
| index_adjustment_refresh | index_adjustment | akshare | monthly_static | false（diff 快照） | ✅ |
| ipo_schedule_incremental | ipo_schedule | akshare | daily_event | true | ✅ |
| margin_target_adjustment_refresh | margin_target_adjustment | akshare | monthly_static | false（diff 快照） | ✅ |
| msci_adjustment_refresh | msci_adjustment | akshare | monthly_static | false | ⏸ disabled=true（无数据源） |
| hk_trade_calendar_refresh | hk_trade_calendar | internal（本次修复，原 akshare） | monthly_static | false | ✅ fallback 已清空 |

### 3.4 Provider capability

| Provider | capability | 实现方法 | 底层 API |
|---|---|---|---|
| InternalComputeProvider | calendar_event | _fetch_calendar_event | 读 trade_calendar 规则派生 |
| InternalComputeProvider | hk_trade_calendar | _fetch_hk_trade_calendar（本次实现） | exchange_calendars XHKG |
| AkshareIngestProvider | index_adjustment | _fetch_index_adjustment | ak.index_stock_cons_weight_csindex 等 |
| AkshareIngestProvider | ipo_schedule | _fetch_ipo_schedule | ak.stock_zh_a_new_em |
| AkshareIngestProvider | margin_target_adjustment | _fetch_margin_target_adjustment | ak.stock_margin_underlying_info_szse/sse |
| ~~AkshareIngestProvider~~ | ~~hk_trade_calendar~~ | ~~_fetch_hk_trade_calendar~~ | ~~ak.tool_trade_date_hist_sina（A股日历，本次移除）~~ |

### 3.5 calendar_event event_type 完整枚举与派生状态

`market_calendar_event.py` DDL 注释列出 12 个 event_type。InternalComputeProvider._fetch_calendar_event
实际派生情况：

| event_type | 派生状态 | 派生逻辑 |
|---|---|---|
| month_end | ✅ 已派生 | 按 (year,month) 分组取最大交易日 |
| quarter_end | ✅ 已派生 | month∈{3,6,9,12} 的 month_end |
| half_year_end | ✅ 已派生 | month==6 的 month_end |
| year_end | ✅ 已派生 | month==12 的 month_end |
| futures_delivery | ✅ 已派生 | 每月第3个周五，非交易日顺延下一交易日 |
| index_option_expiry | ✅ 已派生 | 同 futures_delivery（每月第3个周五） |
| etf_option_expiry | ✅ 已派生 | 每月第4个周三，非交易日顺延 |
| lpr_announcement | ✅ 已派生 | 每月20日，遇周末顺延下一工作日 |
| hk_connect_closed | ✅ 已派生 | A股交易日 − 港股交易日（依赖 hk_trade_calendar，本次修复后正确） |
| fomc_meeting | ⏸ 未派生 | 表结构预留，data_source=manual，待手工录入 |
| major_meeting | ⏸ 未派生 | 表结构预留，待手工录入 |
| stamp_duty_change | ⏸ 未派生 | 表结构预留，待手工录入 |

计算范围：[today-5年, today+2年]，全量重算幂等（ReplacingMergeTree 按 event_date+event_type 去重）。

## 4. hk_trade_calendar 数据源语义错配修复（#ARCH-DATA-001）

### 4.1 病灶

`akshare_provider._fetch_hk_trade_calendar`（原 L5154-5189）调用 `ak.tool_trade_date_hist_sina`
（新浪 A 股交易日历接口）填充 `c1_market.hk_trade_calendar`（港股交易日历表）。该 API 返回沪深交易所
交易日，与港交所（XHKG）日历在圣诞/复活节/佛诞/耶稣受难日等休市日完全不同。若运行
`hk_trade_calendar_refresh` 任务会把正确港股日历覆盖成 A 股日历，下游 `calendar_event.hk_connect_closed`
派生（A股开盘且港股休市=北向资金停摆日）全部失真。

更严重的连带状态：修复前 InternalComputeProvider 已声明 `hk_trade_calendar` capability 并在 fetch
路由调用 `self._fetch_hk_trade_calendar`，**但方法体从未实现**——akshare 版语义错，internal 版一跑
就 AttributeError。两边都坏。

### 4.2 即时止血（本次已完成，已验证）

| # | 动作 | 文件 |
|---|---|---|
| 1 | 实现 `_fetch_hk_trade_calendar`（XHKG 日历，sessions_in_range 主路径 + is_session 逐日回退） | internal_compute_provider.py L482-554 |
| 2 | 移除 akshare 的 hk_trade_calendar：capability(frozenset) + CapabilityContract + _fetch 方法 + 死常量 _TBL_HK_TRADE_CALENDAR（4 处全删） | akshare_provider.py |
| 3 | hk_trade_calendar_refresh: source akshare→internal，fallback_sources 清空 | tasks.yaml L1833-1844 |
| 4 | market_hk_trade_calendar: data_source [exchange]→[internal] | business_data_categories.yaml L794 |
| 5 | 登记 #ARCH-DATA-001（止血裁定）+ #ARCH-DATA-002（治本立项） | architecture_issue_registry.yaml L13666+ |

验证：9 检查点 ALL PASS——圣诞节/节礼日/耶稣受难日/复活节翌日/佛诞/香港特区成立纪念日均不在港股
交易日（A股这些日子是交易日），证明产出确为港股日历。1478 个交易日（today-5y~today+2y，合理）。

## 5. 待施工：系统性治本方案（#ARCH-DATA-002）

> 本节为"讨论稿"，定稿后转 active。用户已认可施工顺序：施工项4 先做，然后 1+2+3，施工项5 可选。

### 5.1 病根（第一性原理）

#ARCH-DATA-001（hk_trade_calendar A股日历冒充港股）与 #ARCH-CH-INDUSTRY-CLASS-MIGRATE
（2026-08-03，tdx 板块成分股→ifind 申万行业分级）是同一类病——provider 声明的 capability 名携带
市场/品种语义（hk_/industry_），但底层调用的 API 返回数据语义不符，而全项目无任何机制校验这种对齐。

现有校验体系覆盖：字符串存在性（capability_validator）、行为标志（CapabilityContract #ARCH-CH-022）、
AST 路由-meta 一致（check_route_meta_consistency）、运行时数值偏差（cross_source_validator，仅 tick_data）、
行数阈值（integrity_checker）。**唯独"capability 名 ↔ API 数据语义"维度完全空白**。

100% AI 开发放大此盲区：AI 凭函数名直觉选 API（`tool_trade_date_hist_sina` 含 `trade_date` 即用），
不主动查文档确认市场归属；capability 前缀对 AI 只是字符串。一周内同类 bug 再现
（INDUSTRY-CLASS → hk_trade_calendar）证明点对点修复无法收敛。

### 5.2 施工项 1：CapabilityContract 扩展语义字段（声明层）

文件：`src/zephyr/data/provider_base.py`

```python
@dataclass
class CapabilityContract:
    capability_id: str
    supports_symbols_null: bool = False
    supports_incremental: bool = True
    supports_full_refresh: bool = True
    requires_date_range: bool = True
    # #ARCH-DATA-002 新增（可选，未填则不校验）
    expected_market: str | None = None     # a_share / hk / us / futures / macro / cross
    expected_variety: str | None = None    # stock / etf / index / calendar / news / ...
```

向后兼容（字段可选），现有 capability 不填即不校验，零迁移成本。

### 5.3 施工项 2：capability_semantic_registry.yaml（语义锚 + API 白名单）

新建 `docs/01_policies_and_standards/_registry/catalogs/capability_semantic_registry.yaml`。
**过度工程防线：只对"跨市场/跨品种易混淆"capability 强制登记**，不搞全量白名单。

```yaml
- capability_id: hk_trade_calendar
  market: hk
  variety: calendar
  allowed_apis: [exchange_calendars.XHKG]
  rationale: 港股日历与A股日历在圣诞/复活节/佛诞差异显著，易错配

- capability_id: trade_calendar
  market: a_share
  variety: calendar
  allowed_apis: [exchange_calendars.XSHG, ak.tool_trade_date_hist_sina, bs.query_trade_dates]

- capability_id: industry_class
  market: a_share
  variety: classification
  allowed_apis: [THS_*, ifind 申万接口]   # mootdx client.block 不在此列 → 拒（防 INDUSTRY-CLASS 重演）
```

维护责任（待讨论）：新增 capability 时强制登记（reconciler 拦），还是先由人工补登存量？
倾向前者，但会让"新增 capability"流程变重一点。**待用户拍板**（见 §6.1）。

### 5.4 施工项 3：capability_validator AST gate（声明时拦截）

扩展 `src/zephyr/governance/.../capability_validator.py` 的 `check_route_meta_consistency`：

1. AST 解析每个 `_fetch_<cap>` 方法体，提取调用的外部 API 符号（`ak.*` / `bs.*` / `xt.*` / `THS_*` / `exchange_calendars.*`）
2. 查 capability_semantic_registry，若该 capability 已登记 `allowed_apis`，校验提取的 API ⊆ 白名单
3. **未登记的 capability 不校验**（过度工程防线）
4. 违例 → reconciler `fix-in-place` 提示登记或换 API，拒提交

验收用例：gate 上线后须能检出 #ARCH-DATA-001（`ak.tool_trade_date_hist_sina` 不在 hk_trade_calendar 白名单）和 #ARCH-CH-INDUSTRY-CLASS-MIGRATE 两个历史 bug。

### 5.5 施工项 4：声明-实现符号一致性 gate（防"半截工程"）

**优先施工**（成本最低、收益最明确）。

针对缺陷：internal_compute 那边能出现"fetch 路由调用方法、方法却不存在"的状态并停留下来，说明没有
编译期/提交期检查"路由引用的方法是否真实定义"。

新增轻量 AST gate：
- 解析 provider `fetch()` 里的路由调用（`self._fetch_xxx(payload)`）
- 校验每个被引用的 `_fetch_xxx` 在类体内**真实定义**
- 违例 → 拒提交

本次 bug 的 internal 侧（AttributeError 状态）能被此 gate 直接拦住。

### 5.6 施工项 5：运行时抽样校验（可选/推迟）

扩展 `cross_source_validator`：对日历类数据，抽样比对表内 `is_open` 与 `exchange_calendars`
（XHKG/XSHG）的 `is_session`，发现语义漂移→告警。作为声明时 gate 的运行时兜底。

声明时 gate（施工项 3）已覆盖大部分场景，本项可推迟。

### 5.7 施工顺序与优先级

| 项 | 优先级 | 理由 | 预估成本 |
|---|---|---|---|
| 施工项 4（符号一致性 gate） | **先做** | 成本最低，直接防"半截工程"重演 | 0.5 天 |
| 施工项 1（CapabilityContract 扩展） | 紧随 | 字段添加，向后兼容 | 0.5 天 |
| 施工项 2（semantic_registry） | 同批 | 新建注册表 + 登记易混淆 capability | 1 天 |
| 施工项 3（AST gate） | 同批 | 真正治本，依赖项 2 | 1.5 天 |
| 施工项 5（运行时抽样） | 可选/推迟 | 声明时 gate 已覆盖大部分 | 1 天 |

用户裁定：认可此顺序，"能做就尽快上"。MVP 阶段先靠 #ARCH-DATA-001 类即时止血 + 人工 review 兜底，
下个治理窗口启动语义契约扩展设计。

## 6. 开放讨论项

### 6.1 API 白名单维护责任

`capability_semantic_registry.yaml` 的 `allowed_apis` 谁来维护？
- 选项 A：新增 capability 时强制登记（reconciler 拦截未登记）——治理强，但流程重
- 选项 B：先人工补登存量易混淆 capability，新增时 warn 不拦——治理弱，但不阻塞
- **倾向 A**，但需用户拍板。建议 MVP 阶段用 B（warn），积累一定存量后升级为 A（拦）

### 6.2 msci_adjustment 数据源接入路径

akshare/tushare 均无 MSCI/富时调整直接接口。候选路径：
1. 爬虫 MSCI 官网 quarterly review 公告（维护成本高，反爬风险）
2. 接入第三方数据源（Wind/iFind MSCI 调整专题，需付费）
3. 手工录入历次调整事件（准确但滞后）

**待讨论**：MVP 阶段是否需要 MSCI 调整数据？若需要，选哪条路径？当前表结构已预留，可空置等待。

### 6.3 fomc_meeting / major_meeting / stamp_duty_change 手工填充策略

calendar_event 表结构已预留这 3 个 manual event_type，但无填充机制。候选：
1. 建 CSV 录入 + 一次性 IMPORT（简单）
2. 建轻量 admin 接口（过度工程，不推荐）
3. 直接 INSERT SQL 脚本（最轻）

**待讨论**：填充策略 + 数据源（FOMC 日程官网可爬、两会日期固定可手工、印花税历史调整可查）。

### 6.4 悬空引用修正

`business_data_categories.yaml` L1923 与 `tasks.yaml` L2371 引用
`docs/03_modules/_cross_layer/database/special_trading_days_data_ingestion.md`，该路径不存在
（实际文档在 `.trae/documents/`，不入 git）。本文档（17 号）承接其规划职责。

**待施工**：将上述两处引用改为指向本文档
`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/17_special_trading_days_data_assets.md`。
本次提交暂不改（避免混入过多改动），列为紧随小任务。

### 6.5 ETF 赎回日是否单独建表

用户最初提及"ETF 赎回日"。评估结论（§2.4）：A 股 ETF 为 T+0 实物申赎，无固定"赎回日"；
净赎回数据可从 `etf_nav` 衍生。**建议不单独建表**，需要时在查询层衍生净赎回指标。待用户确认。

## 7. 关键文件清单

| 文件 | 角色 |
|---|---|
| schemas/categories/market_calendar_event.py | calendar_event DDL 真源 |
| schemas/categories/market_index_adjustment.py | index_adjustment DDL 真源 |
| schemas/categories/market_ipo_schedule.py | ipo_schedule DDL 真源 |
| schemas/categories/market_margin_target_adjustment.py | margin_target_adjustment DDL 真源 |
| schemas/categories/market_dividend_tax_node.py | dividend_tax_node VIEW DDL 真源 |
| schemas/categories/market_msci_adjustment.py | msci_adjustment DDL 真源（预留） |
| src/zephyr/data/implementations/internal_compute_provider.py | calendar_event + hk_trade_calendar 派生 |
| src/zephyr/data/implementations/akshare_provider.py | index_adjustment/ipo_schedule/margin_target_adjustment 采集（hk_trade_calendar 已移除） |
| src/zephyr/data/config/tasks.yaml | 6 个采集任务 |
| docs/03_modules/_cross_layer/database/business_data_categories.yaml | 7 条品类注册 |
| docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | #ARCH-DATA-001/002 裁定 |
| docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/17_special_trading_days_data_assets.md | 本文档 |

## 8. 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1.0 | 2026-08-10 | 初稿。承接 .trae 工作文档规划职责；记录完整清单 + 已施工盘点 + #ARCH-DATA-001 止血 + #ARCH-DATA-002 治本讨论稿 |
