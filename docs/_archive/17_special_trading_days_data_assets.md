---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=A股"特殊交易日"数据资产全景与治理（含 hk_trade_calendar 语义错配修复 #ARCH-DATA-001/002） · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.1 · date=2026-08-15 · topic=special_trading_days_data_assets · scope=07_trading_decision_architecture · related_issues=- "#ARCH-DATA-001（hk_trade_calendar 语义错配即时止血）" - "#ARCH-DATA-002（capability-API 语义对齐治本）"

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-13 第一批（会话 AI-STD-001）定稿：草案→active v1.0.0。§5 治本方案 5 项裁定齐全（符号一致性双向校验 + 语义字段 + semantic_registry + AST 门禁采纳，运行时抽样推迟），§6 六项讨论全部拍板；hk_trade_calendar 语义错配修复（#ARCH-DATA-001）+ 治本方案（#ARCH-DATA-002）落地。
>
> **最终成果**：A 股特殊交易日数据资产全景与治理定稿；合并后补检全过（无 BOM/换行统一 LF/相对链接零断链）。
>
> **未做事项及原因**：运行时抽样校验未做——裁定推迟，MVP 范围外。
>
> **复核补记（AI-NIGHT-001 复核 2026-08-19）**：代码实证以下定稿后施工项仍未落地，补登备查——① §6.6-1 akshare hk_trade_calendar 声明残留**仍存在**（akshare_provider.py 实证：capability frozenset L275 与 CapabilityContract("hk_trade_calendar") L511 未删，方法体已无，仍为"声明无实现"态）；② §6.6-2 calendar_event_refresh 任务未登记（tasks.yaml 实证仅 hk_trade_calendar_refresh 一条 internal 任务，calendar_event 表仍无数据填充通道）；③ §6.6-4 六条品类注册未补登（business_data_categories.yaml 实证仅 market_hk_trade_calendar + market_northbound_hold_snapshot 相关段）；④ §5.8 MVP 最小集（施工项 4 符号一致性双向 gate + 施工项 1 expected_market/expected_variety 字段）未施工（grep 实证 expected_market 零命中，现有 check_route_meta_consistency 仅覆盖路由↔meta 声明、不校验 _fetch_xxx 方法真实定义）；⑤ §6.3 FOMC 等 3 个 manual event_type CSV 未填充（与 ② 同批条件未达成）；⑥ §6.6-3 三条 akshare 采集链按 v1.0.0 定稿暂缓未施工（属既定裁定，待下个数据资产窗口）。scheduler.py create_provider 亦无 source=="internal" 分支（实证），internal 任务目前无调度路由——与 16 号调度闭环同根缺口。

> ## 结案报告回填（2026-08-28 代码实证复核）
> 原复核补记缺口①②④已闭环：①akshare_provider.py 的 hk_trade_calendar 声明残留已删（2026-08-20，注释实证）；②calendar_event_refresh 已登记（tasks.yaml L1862，dependencies 含 trade_calendar/hk_trade_calendar）；④expected_market 已落码（provider_base.py 字段+akshare/okx/internal_compute 三 provider+capability_semantic_gate.py 语义门禁）；⑤data/manual/calendar_event_manual.csv（FOMC 等）已填充。
> **仍真实未完工**：运行时抽样校验（裁定推迟）；§6.6-3 三条 akshare 采集链（既定暂缓）。

# A股"特殊交易日"数据资产全景与治理

> 本文档承接原 `.trae/documents/special_trading_days_data_ingestion.md`（工作规划，不入 git）的规划职责，
> 转为正式 design_memo。v0.1.0 称 `business_data_categories.yaml` 与 `tasks.yaml` 中对该旧路径的引用为悬空引用，
> v0.2.0 全项目 Grep 核实该引用已不存在（见 §6.4，任务关闭）。

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

- 不做新治理裁定（裁定落在 `architecture_issue_registry.yaml` 的 #ARCH-DATA-001/002）
- 治本方案设计定稿落在本文档 §5（v1.0.0 AI-STD-001 定稿，逐项结论见 §5.8），§6 讨论项已定夺并记录裁定
- 后续施工追踪由 §6.6 台账承载（不单独补登立项条目，见 §6.6-5 定稿裁定）

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

> ⚠️ "✅ 已派生"=派生函数已实现；但 `calendar_event_refresh` 任务未注册（§3.3），表当前无数据填充通道，见 §3.5 注记。

### 2.2 日历表类（交易日历本身）

| 日历 | 落地表 | 数据源 | 覆盖状态 |
|---|---|---|---|
| A股交易日历 | trade_calendar | baostock / exchange_calendars XSHG | ✅ 已有 |
| 港股交易日历 | hk_trade_calendar | exchange_calendars XHKG | ✅ 本次修复（#ARCH-DATA-001，原 akshare 用 A股日历冒充） |

### 2.3 个股事件类（有 symbol）

| 事件 | 机理 | 落地表 | 数据源 | 覆盖状态 |
|---|---|---|---|---|
| 指数成分股调整（沪深300/中证500/中证1000） | 被动基金强制调仓 | index_adjustment | akshare | 🟨 schema 已建；采集链（provider 方法/任务/品类注册）未施工（v0.2.0 核实） |
| 新股申购+上市 | 打新冻结资金吸筹/上市资金分流 | ipo_schedule | akshare | 🟨 schema 已建；采集链未施工（v0.2.0 核实） |
| 两融标的调整 | 杠杆资金被迫加减仓 | margin_target_adjustment | akshare | 🟨 schema 已建；采集链未施工（v0.2.0 核实） |
| 红利税节点（除息日前1月/前1年） | 税动机交易（持股期限跨档） | dividend_tax_node（VIEW） | internal（rights_issue 派生） | ✅ VIEW DDL 已建（DDL-as-Code 自动建表）；品类注册未登记（v0.2.0 核实） |
| 除权除息日 | 除权缺口+税节点触发源 | rights_issue（c3_fundamental） | akshare/ifind | ✅ 已有（非本次新增） |
| MSCI/富时调整 | 外资被动调仓 | msci_adjustment | manual（待接入） | ⏸ schema 预留（无注册/无任务，等效 disabled） |
| 解禁日 | 解禁抛压预期 | share_unlock（c3_fundamental） | akshare/ifind | ✅ 已有 |
| 股权质押 | 平仓线风险 | equity_pledge（c3_fundamental） | akshare | ✅ 已有 |
| 回购 | 回购支撑 | repurchase（c3_fundamental） | akshare | ✅ 已有 |

### 2.4 待评估项（用户提及但尚未建表）

| 事件 | 评估 | 建议 |
|---|---|---|
| ETF 赎回日（大额申赎） | ETF 大额申赎引发成分股买卖，可能扰动流动性。但 A 股 ETF 申赎为 T+0 实物申赎，无固定"赎回日"；ETF 净赎回数据可从 `etf_nav` 衍生 | 暂不单独建表，需要时在查询层从 etf_nav 衍生净赎回指标 |
| 除夕（春节前最后交易日） | 已被 trade_calendar（is_open=0）+ year_end/month_end 覆盖，资金避险效应可由月末/年末事件捕获 | 不单独建表 |
| 分红股权登记日 | rights_issue 表已含 ex_date，登记日=ex_date-1，可查询层计算 | 不单独建表 |
| 国债期货交割日（交割月第2个周五，T/TF/TS） | 与股指期货交割日（第3个周五）**不同日**。国债期货交割影响资金面（交割占用保证金+现券联动），但对 A 股个股价格的直接效应弱于股指期货（参与者主要是机构利率交易员，资金分流为间接传导） | 登记待评估：若固收+跨资产研究启动（cross_asset 域），可加 `bond_futures_delivery` event_type；MVP 股票系统优先级低 |
| MLF 操作日（每月15日，遇周末顺延） | 中期借贷便利利率是 LPR 的前瞻信号（MLF→LPR 传导链），2019 年 LPR 改革后是重要政策利率窗口；与已覆盖的 lpr_announcement（每月20日）互补 | 登记待评估：派生规则简单（每月15日顺延下一工作日），可加 `mlf_operation` event_type，成本同 LPR 派生 |
| 财报强制披露截止窗口（季报/年报：4/30、8/31、10/31 截止） | 截止日前后是业绩暴雷/超预期集中披露期，事件驱动策略的重要避险/机会窗口；express_report/disclosure_plan 表已有个股披露计划，但"全市场披露截止窗口"作为日历事件未覆盖 | 登记待评估：可加 `earnings_deadline` event_type（每年 4/30、8/31、10/31 三个固定截止日，遇非交易日取前一交易日）；与事件驱动 sleeve（G10）联动价值高 |
| 央行 OMO 每日操作 / CPI/PMI/社融发布日 | OMO 每日进行无固定效应日；经济数据发布日（CPI 每月9-13日/PMI 月末月初/社融 10-15日）日期不固定，需外部数据源（宏观表已收数据本身，发布日效应可从宏观数据时间戳间接推导） | 不单独建表；宏观数据表（macro_data/edb_data）已覆盖数据本身，发布日效应属事件研究层自行关联 |
| 富时A50期货交割日（每月倒数第2个工作日，新交所） | v0.2.0 第4轮搜索新发现（东财 2026-07《交割日对A股市场的影响》）：A50 是离岸衍生品，覆盖 A 股盘前/夜间超长交易时段，海外资管+北向对冲资金集中使用——交割日前隔夜外资集中调仓直接形成次日 A 股跳空高开/低开，北向重仓金融/消费龙头是主要受冲击标的。常规月份形成"股指期货交割（第3周五）→ETF期权交割（第4周三）→月末A50交割"固定链条 | 登记待评估：派生规则确定（每月倒数第2个工作日），可加 `a50_futures_delivery` event_type；与 hk_connect_closed（北向停摆）协同刻画北向资金节奏，优先级高于国债期货交割日 |

### 2.5 日历→仓位约束规则（BM-POS-08 日历仓位约束，v0.2.2 作战地图全覆盖补丁补登）

> **定位**：BM-POS-08（L3.5，MOD-POS-017，source_ref：D-POSITION §1.5 POS-17 + §7.4 A股风险日历→仓位约束 v8.0）是日历资产的**消费侧裁决层**——本文 §2/§3 盘点的 calendar_event 等资产管"日子是什么"，本环节管"日子到了仓位怎么办"。触发=当前日期命中风险日历事件；数据基座=本文既有 calendar_event 资产（§3.5 event_type 枚举）+ 个股事件表。
>
> **裁定（采纳作战地图登记规则，补 why 层）**：周期性日历风险（交割日/年报截止/预告截止/财报窗口/信息空窗）是 A 股可预期的结构性风险源，用**临时仓位上限**而非信号层调权来响应——仓位上限是硬约束（不可被信号强度覆盖），匹配"日历风险=确定日期+不确定幅度"的性质。**理由**：① 日历事件日期确定、效应方向历史可验，适合规则化硬约束而非模型软调权；② 与 regime 节流（市场级、连续）正交——日历约束是事件级、离散的临时收紧，两者乘性叠加不冲突；③ 个人系统无人工日历盯防，规则化才能 100% 执行。**重评条件**：calendar_event 表回填（§3.3 最优先缺口）且各规则实盘运行 6 个月后，按误伤率（约束触发但无风险事件）校准收紧幅度。
>
> **日历事件 → 临时仓位上限裁决表**（参数以作战地图 BM-POS-08 indicators 登记为准，现行代码值列对齐）：

| # | 日历事件 | 约束动作 | 现行代码值 | 数据基座（本文资产） |
|---|---|---|---|---|
| 1 | 期权交割日 | **否决新开仓位**（仅允许减仓） | 期权交割日否决新开仓 | calendar_event `index_option_expiry`/`etf_option_expiry`（§3.5 已派生） |
| 2 | 4 月下旬（年报截止日）ST 清零 | **ST 股仓位强制清零** | 年报截止日 ST 清零 | ST 标记（D-FACTOR）+ year_end/quarter_end 日历序列 |
| 3 | 业绩预告截止日前 5 日 | **否决未出预告个股新买入** | 预告截止日前 5 日否决新买入 | 预告截止日历 + disclosure 数据（§2.4 财报截止窗口待评估项联动） |
| 4 | 微盘股信息空窗期（股东信息空窗） | **<50 亿市值标的仓位上限收紧 50%** | 股东信息空窗期微盘股收紧 50% | 市值分类（D-FACTOR）+ 股东信息数据空窗判定 |
| 5 | 交割日前后 | **仓位上限临时下调 5-10%** | 交割日前后下调 5-10% | calendar_event `futures_delivery`（每月第 3 个周五，§3.5 已派生） |
| 6 | 财报前 3 天（个股） | **标的仓位上限下调 + 禁止新建** | 财报前 3 天降仓位+禁新建 | 个股披露计划（express_report/disclosure_plan，§2.4） |

> **契约/数据流**：输入=风险日历+当前日期 → 日历事件匹配+临时仓位上限调整 → 输出 **CalendarPositionAlert + 临时仓位上限** → 下游 **BM-POS-01 仓位裁决上限 / BM-POS-04 跨策略硬限制**消费（日历上限与 regime Shrinkage、回撤 Protocol position_cap 乘性叠加取最紧）。consumes：A股风险日历（D-DATA，本文资产）/ 当前持仓（D-EX-CORE）/ ST 标记 + 市值分类（D-FACTOR）。
>
> **降级**：日历数据缺失 → 跳过日历约束（仅依赖市场状态仓位上限，可能漏防周期性风险）——这也是 §3.3 calendar_event_refresh 任务补登记列为最优先缺口的原因：**数据基座空表时本环节整体处于降级态**。
>
> **过度工程审查**：6 条规则全部复用本文既有日历资产与 D-FACTOR 既有标记，不新建数据表、不新建状态机；裁决逻辑是查表匹配（<50 行），✅ 通过。

## 3. 已施工数据资产盘点

> 反映 2026-08-12 真实状态（v0.2.0 Grep 全量核实）。schema 文件均为 DDL-as-Code，由 `apply_market_tables_ddl.py` 自动发现建表。

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

### 3.2 business_data_categories.yaml 注册（v0.2.0 核实：仅 1 条已注册，6 条待施工）

文件：`docs/03_modules/_cross_layer/database/business_data_categories.yaml`。

| category_id | table | 注册状态（v0.2.0 Grep 核实） |
|---|---|---|
| market_hk_trade_calendar | hk_trade_calendar | ✅ 已注册（L781，data_source=[internal]，含 #ARCH-DATA-001 注释） |
| market_calendar_event | calendar_event | ❌ 未注册（待施工） |
| market_index_adjustment | index_adjustment | ❌ 未注册（待施工） |
| market_ipo_schedule | ipo_schedule | ❌ 未注册（待施工） |
| market_margin_target_adjustment | margin_target_adjustment | ❌ 未注册（待施工） |
| market_dividend_tax_node | dividend_tax_node | ❌ 未注册（待施工；VIEW 派生，注册仅作台账） |
| market_msci_adjustment | msci_adjustment | ❌ 未注册（预留，等效 disabled） |

> v0.2.0 修正：v0.1.0 声称"7 条注册于 L1921-2019（A股特殊日子数据资产段）"经 Grep
> 核实该段落与 6 条 category_id 均不存在——schema DDL 落盘 ≠ 品类注册落盘，两者是独立动作。本表已改为真实状态。

### 3.3 tasks.yaml 采集任务（v0.2.0 核实：仅 1 个已注册，5 个待施工）

文件：`src/zephyr/data/config/tasks.yaml`。

| task_id | table | source | 注册状态（v0.2.0 Grep 核实） |
|---|---|---|---|
| hk_trade_calendar_refresh | hk_trade_calendar | internal | ✅ 已注册（L1833-1842，source akshare→internal，无 fallback_sources） |
| calendar_event_refresh | calendar_event | internal | ❌ 未注册（待施工；internal 派生函数已实现，仅缺任务登记） |
| index_adjustment_refresh | index_adjustment | akshare | ❌ 未注册（待施工；provider 方法亦缺失，见 §3.4） |
| ipo_schedule_incremental | ipo_schedule | akshare | ❌ 未注册（待施工；provider 方法亦缺失） |
| margin_target_adjustment_refresh | margin_target_adjustment | akshare | ❌ 未注册（待施工；provider 方法亦缺失） |
| msci_adjustment_refresh | msci_adjustment | — | ❌ 未注册（预留，无数据源） |

> v0.2.0 修正：v0.1.0 声称"6 个任务注册于 L2369-2433"经 Grep 核实仅
> hk_trade_calendar_refresh 存在。calendar_event 的 internal 派生函数（§3.5）已实现但无调度
> 任务——**calendar_event 表当前无数据填充通道（DDL 建表后空表），这是最优先补齐的缺口**。

### 3.4 Provider capability（v0.2.0 核实）

| Provider | capability | 实现方法 | 状态（v0.2.0 Grep 核实） |
|---|---|---|---|
| InternalComputeProvider | calendar_event | `_fetch_calendar_event`（L505）+ `_derive_*` 系列 | ✅ 已实现 |
| InternalComputeProvider | hk_trade_calendar | `_fetch_hk_trade_calendar`（L625，exchange_calendars XHKG） | ✅ 已实现（本次修复） |
| AkshareIngestProvider | index_adjustment | — | ❌ 方法不存在（待施工） |
| AkshareIngestProvider | ipo_schedule | — | ❌ 方法不存在（待施工） |
| AkshareIngestProvider | margin_target_adjustment | — | ❌ 方法不存在（待施工） |
| ~~AkshareIngestProvider~~ | ~~hk_trade_calendar~~ | ~~`_fetch_hk_trade_calendar`~~ | 方法体已删（留注释）；⚠️ 声明残留见 §4.2 |

> v0.2.0 修正：v0.1.0 将三个 akshare 采集方法标为已实现（含底层 API
> `ak.index_stock_cons_weight_csindex` 等），经 Grep 核实 akshare_provider.py 中无任何
> index_adjust/ipo_sched/margin_target 相关方法——§2.3 三个"🟨"状态与此一致。

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

> ⚠️ v0.2.0 注记：上表"✅ 已派生"指 **派生函数已实现**（`_derive_month_ends` /
> `_derive_futures_delivery` / `_derive_lpr_announcement` / `_derive_hk_connect_closed`，Grep 核实存在）。
> 但因 §3.3 `calendar_event_refresh` 任务未注册，**派生函数无调度通道，calendar_event 表大概率为空表**——"代码就绪、数据未灌"。回填数据只需补登记该任务并跑一次。

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
| 1 | 实现 `_fetch_hk_trade_calendar`（XHKG 日历，sessions_in_range 主路径 + is_session 逐日回退） | internal_compute_provider.py L625 起 |
| 2 | 移除 akshare 的 hk_trade_calendar：`_fetch_hk_trade_calendar` 方法体 + 死常量 `_TBL_HK_TRADE_CALENDAR` 已删（L4445-4447 留 #ARCH-DATA-001 注释）。⚠️ **v0.2.0 核实发现 2 处声明残留**：capability frozenset（akshare_provider.py L169）与 `CapabilityContract("hk_trade_calendar", ...)`（L363）未删——provider 声明了 capability 却无实现方法，若误配 source=akshare 跑该 capability 会 AttributeError。此残留正是 §5.5 施工项 4（声明-实现符号一致性 gate）的活靶，列入紧随清理任务（见 §6.6） | akshare_provider.py |
| 3 | hk_trade_calendar_refresh: source akshare→internal，fallback_sources 清空 | tasks.yaml L1833-1842 |
| 4 | market_hk_trade_calendar: data_source [exchange]→[internal] | business_data_categories.yaml L794 |
| 5 | 登记 #ARCH-DATA-001（止血裁定）+ #ARCH-DATA-002（治本立项） | architecture_issue_registry.yaml L13682+ |

验证：9 检查点 ALL PASS——圣诞节/节礼日/耶稣受难日/复活节翌日/佛诞/香港特区成立纪念日均不在港股
交易日（A股这些日子是交易日），证明产出确为港股日历。1478 个交易日（today-5y~today+2y，合理）。

## 5. 待施工：系统性治本方案（#ARCH-DATA-002）

> 本节已定稿（v1.0.0，AI-STD-001 定稿会话，2026-08-13）。施工顺序沿用用户裁定：施工项 4 先做，
> 然后 1+2+3 同批，施工项 5 可选推迟；逐项定稿结论见 §5.8。

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

维护责任（v1.0.0 已定稿，见 §6.1 裁定）：MVP 阶段执行选项 B——新增 capability 时 reconciler
warn 不拦，存量易混淆 capability 随本施工项人工补登；满足升级触发条件后升级为选项 A
（新增强制登记、reconciler 拦截）。

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

新增轻量 AST gate（v1.0.0 定稿：**双向校验**）：
- 解析 provider `fetch()` 里的路由调用（`self._fetch_xxx(payload)`）
- 校验每个被引用的 `_fetch_xxx` 在类体内**真实定义**
- 反向校验：capability frozenset 与 `CapabilityContract(...)` 声明的每个 capability 必须有
  对应 `_fetch_<cap>` 方法定义（防 §4.2 akshare L169/L363 式"声明残留"）
- 同一 AST 扫描一次完成双向校验，违例 → 拒提交

本次 bug 的 internal 侧（AttributeError 状态）与 akshare 侧（声明残留状态）均能被此 gate 直接拦住。

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

> **过度工程审查（v0.2.0 补）**：5 项总成本 ~4.5 天，对照 charter 约束二（单机单人）不算过重——
> 其中施工项 5 已标可选/推迟。**MVP 最小集 = 施工项 4 + 1（合计 1 天）**：符号一致性 gate 防
> "半截工程"（§4.2 发现的 akshare L169/L363 声明残留正是活例）+ CapabilityContract 字段扩展
> 提供语义锚载体；施工项 2+3（注册表 + AST gate，2.5 天）随下个治理窗口同批启动，不挤占
> MVP 实盘生存级施工（40_execution_broker / 53_simulation_live_path 优先）。

### 5.8 定稿结论（v1.0.0，AI-STD-001 定稿会话，2026-08-13）

| 施工项 | 定稿结论 | 关键参数/边界 |
|---|---|---|
| 项 4 声明-实现符号一致性 gate | ✅ 采纳，**最优先施工** | 双向校验（§5.5 已回填）：路由引用方法必须真实定义 + capability 声明必须有对应 `_fetch_<cap>` 实现；同一 AST 扫描一次完成，违例拒提交 |
| 项 1 CapabilityContract 语义字段 | ✅ 采纳，随项 4 紧随施工 | 字段定为 `expected_market` / `expected_variety`，可选、未填不校验、向后兼容零迁移 |
| 项 2 capability_semantic_registry.yaml | ✅ 采纳，与项 3 同批（下个治理窗口） | 只对"跨市场/跨品种易混淆"capability 强制登记（hk_\*/us_\*/industry_\*/calendar 类）；初始登记 3 条：hk_trade_calendar / trade_calendar / industry_class；维护责任按 §6.1 裁定（MVP=选项 B warn 不拦） |
| 项 3 capability_validator AST gate | ✅ 采纳，与项 2 同批 | 验收用例=须检出 #ARCH-DATA-001 与 #ARCH-CH-INDUSTRY-CLASS-MIGRATE 两个历史 bug；未登记 capability 不校验（过度工程防线保留）；违例 → reconciler fix-in-place 提示登记或换 API |
| 项 5 运行时抽样校验 | ⏸ 推迟 | 启动条件（任一满足）：① 项 3 上线后发现漏检案例；② 日历类数据运行时语义漂移实证出现。届时扩展 cross_source_validator 抽样比对表内 is_open ↔ exchange_calendars is_session |

施工路径定稿：**MVP 最小集 = 项 4 + 项 1（约 1 天）**；项 2 + 项 3（约 2.5 天）随下个治理窗口
同批启动，不挤占实盘生存级施工（40_execution_broker / 53_simulation_live_path 优先）；项 5 推迟。
本定稿不改变 #ARCH-DATA-002 在注册表的 decided 状态；注册表 fix_phase 回填（"设计已定稿，
见 17 号 v1.0.0 §5.8"）待 bm-fill 会话释放 architecture_issue_registry.yaml 后执行（见 §6.6-5 定稿裁定）。

## 6. 讨论项与定稿结论

> v1.0.0（AI-STD-001，2026-08-13）：本节原"开放讨论项"均已定夺，定稿裁定逐条附于原讨论之后。
> §6.4 已于 v0.2.0 关闭（全项目 Grep 核实悬空引用不存在）。

### 6.1 API 白名单维护责任

`capability_semantic_registry.yaml` 的 `allowed_apis` 谁来维护？选项 A：新增 capability 时强制登记
（reconciler 拦截未登记）——治理强，但流程重；选项 B：先人工补登存量易混淆 capability，新增时
warn 不拦——治理弱，但不阻塞。
**定稿裁定（v1.0.0，AI-STD-001）**：MVP 阶段执行**选项 B**（新增时 warn 不拦 + 存量易混淆 capability 随施工项 2 人工补登）。升级为**选项 A**（新增强制登记、reconciler 拦截）的触发条件（任一满足即升级）：① 易混淆 capability 登记覆盖稳定运行一个完整治理窗口；② capability-API 语义错配同类 bug 再发生一次（不等治理窗口，立即升级）

### 6.2 msci_adjustment 数据源接入路径

akshare/tushare 均无 MSCI/富时调整直接接口。候选路径：
① 爬虫 MSCI 官网 quarterly review 公告（维护成本高，反爬风险）；② 接入第三方数据源（Wind/iFind MSCI 调整专题，需付费）；③ 手工录入历次调整事件（准确但滞后）。

**定稿裁定（v1.0.0，AI-STD-001）**：MVP 阶段**不需要** MSCI 调整数据，表结构维持空置（等效 disabled）。
未来事件驱动/外资流向研究启动时再审，届时路径优先级：**路径 ② 优先**（第三方数据源——iFind 已在
体系内，边际成本最低），路径 ①（爬虫）仅作 fallback，路径 ③（手工录入）用于补历史关键调整事件。

### 6.3 fomc_meeting / major_meeting / stamp_duty_change 手工填充策略

calendar_event 表结构已预留这 3 个 manual event_type，但无填充机制。候选：
① 建 CSV 录入 + 一次性 IMPORT（简单）；② 建轻量 admin 接口（过度工程）；③ 直接 INSERT SQL 脚本（最轻）。

**定稿裁定（v1.0.0，AI-STD-001）**：采纳**方案 ①（CSV 录入 + 一次性 IMPORT）**为标准填充路径——
FOMC 每年 8 次、两会每年 1 次，属低频重复录入，CSV 作手工源数据台账可复查、可增量追加；
方案 ② 排除（过度工程）；方案 ③ 仅作一次性应急补丁。
填充时机：随 §6.6-2 `calendar_event_refresh` 任务补登记同批执行（同表同批，一次回填）。

### 6.4 悬空引用修正（v0.2.0 核实：任务关闭）

v0.1.0 称 `business_data_categories.yaml` 与 `tasks.yaml` 引用
`docs/03_modules/_cross_layer/database/special_trading_days_data_ingestion.md` 为悬空引用。
**v0.2.0 全项目 Grep 核实：该引用已不存在于任何文件**（唯一提及处是本文档自述）——
推测随 v0.1.0 声称的注册/任务段从未落盘而自然不存在。本任务关闭，无需施工。

### 6.5 ETF 赎回日是否单独建表

评估结论（§2.4）：A 股 ETF 为 T+0 实物申赎，无固定"赎回日"；净赎回数据可从 `etf_nav` 衍生。
**定稿裁定（v1.0.0，AI-STD-001）**：**不单独建表**，需要时在查询层从
`etf_nav` 衍生净赎回指标。本项关闭。

### 6.6 紧随清理任务（v0.2.0 新增）

1. **akshare hk_trade_calendar 声明残留清理**（§4.2 第 2 行）：删 akshare_provider.py L169
   frozenset 中 `"hk_trade_calendar"` + L363 `CapabilityContract("hk_trade_calendar", ...)`。
   删前确认无任务以 source=akshare 调度该 capability（tasks.yaml 唯一任务 source=internal，安全）。
2. **calendar_event_refresh 任务补登记**（§3.3 最优先缺口）：派生函数已就绪，登记任务
   （monthly_static / 全量幂等 / 依赖 trade_calendar_refresh）并跑一次回填 7 年历史。
   下游等待方：[15_data_feature_layer_spec](15_data_feature_layer_spec.md) §待定项"Embargo BDay 近似
   换真交易日历（接 calendar_event）"依赖本表有数据；63 号 v2.1.0 已将本表列入"代码零引用但规划已登记"
   类别交叉佐证。
3. **三条 akshare 采集链施工评估**（§3.4）：index_adjustment / ipo_schedule /
   margin_target_adjustment 的 provider 方法 + 任务 + 品类注册整套补建；施工前先确认 MVP
   是否真需要这三类数据（与 §6.2 一并评估优先级）。63 号 v2.1.0 亦将此 3 表列入
   "代码零引用但规划已登记"类别（交叉佐证）。
   **定稿评估结论（v1.0.0，AI-STD-001）**：**暂缓施工**——MVP 阶段聚焦实盘生存级，三类数据
   服务事件驱动/打新等 alpha 侧增强而非生存级，优先级让位 §6.6-2（calendar_event 回填为风险侧
   BM-POS-08 日历仓位约束的数据基座，风险优先）；与 §6.2 MSCI 同批于下个数据资产窗口再审。
   若届时确定启动，属未来功能：先登记 candidate_module_registry（CAND）再施工。
4. **6 条品类注册补登**（§3.2）：随对应采集链施工一并补登；calendar_event/dividend_tax_node
   两条 internal 类可先行。注册表体系施工规范与 data_asset_registry 登记要求见
   [62_business_registry_construction](62_business_registry_construction.md)（G62 总案）。
5. **特殊日子数据资产立项条目补登评估**（v0.2.0 新增）：v0.1.0 frontmatter related_issues 曾引用一个
   "特殊日子数据资产立项"的 ARCH 编号，但 architecture_issue_registry.yaml 中并无对应条目。
   v0.2.0 已从 frontmatter 移除该悬空引用；若需立项追踪后续施工（§6.6-2/3/4），
   应先在注册表补登条目、再在本文档恢复引用——待用户裁定是否需要。

   **定稿裁定（v1.0.0，AI-STD-001）**：**不单独补登立项条目**——后续施工（§6.6-1~4）由本文档
   active 状态承载追踪（§6.6 即任务台账，修复/清理类问题已由 #ARCH-DATA-001/002 覆盖，功能类
   按 §6.6-3 结论未来启动时登 CAND）。另：#ARCH-DATA-001/002 注册表条目的 fix_phase 回填
   （"§5.8 设计定稿完成"）待 bm-fill 会话释放 architecture_issue_registry.yaml 后由后续会话
   执行——本会话遵守多会话并发防护铁律，不触碰该文件。

## 7. 关键文件清单

| 文件 | 角色 |
|---|---|
| schemas/categories/market_calendar_event.py | calendar_event DDL 真源 |
| schemas/categories/market_index_adjustment.py | index_adjustment DDL 真源 |
| schemas/categories/market_ipo_schedule.py | ipo_schedule DDL 真源 |
| schemas/categories/market_margin_target_adjustment.py | margin_target_adjustment DDL 真源 |
| schemas/categories/market_dividend_tax_node.py | dividend_tax_node VIEW DDL 真源 |
| schemas/categories/market_msci_adjustment.py | msci_adjustment DDL 真源（预留） |
| src/zephyr/data/implementations/internal_compute_provider.py | calendar_event（L505）+ hk_trade_calendar（L625）派生 |
| src/zephyr/data/implementations/akshare_provider.py | ⚠️ hk_trade_calendar 声明残留 2 处（L169/L363，§6.6-1 待清理）；三个事件采集方法未施工 |
| src/zephyr/data/config/tasks.yaml | 1 个已注册任务（hk_trade_calendar_refresh L1833）+ 5 个待注册（§3.3） |
| docs/03_modules/_cross_layer/database/business_data_categories.yaml | 1 条已注册（market_hk_trade_calendar L781）+ 6 条待注册（§3.2） |
| docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml | #ARCH-DATA-001/002 裁定 |
| docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/17_special_trading_days_data_assets.md | 本文档 |

## 8. 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1.0 | 2026-08-10 | 初稿。承接 .trae 工作文档规划职责；记录完整清单 + 已施工盘点 + #ARCH-DATA-001 止血 + #ARCH-DATA-002 治本讨论稿 |
| v0.2.0 | 2026-08-12 | **已施工盘点真实化修正**（架构审查第 1-3 轮 Grep 全量核实）：① §3.2 品类注册从"7 条已注册"修正为"仅 market_hk_trade_calendar 1 条已注册，6 条待施工"（v0.1.0 声称的 L1921-2019 注册段不存在）；② §3.3 采集任务从"6 个已注册"修正为"仅 hk_trade_calendar_refresh 1 个已注册，5 个待施工"（v0.1.0 声称的 L2369-2433 任务段不存在），并点名 calendar_event 表"代码就绪、数据未灌"为最优先缺口；③ §3.4 三个 akshare 采集方法（index_adjustment/ipo_schedule/margin_target_adjustment）从"已实现"修正为"方法不存在"；④ §2.3 三个个股事件覆盖状态从"✅ 已施工"修正为"🟨 schema 已建、采集链未施工"；⑤ §4.2 止血动作第 2 行从"4 处全删"修正为"方法体+死常量已删，capability frozenset（L169）+ CapabilityContract（L363）两处声明残留"；⑥ §6.4 悬空引用修正任务关闭（全项目 Grep 核实该引用已不存在）；⑦ 新增 §6.6 紧随清理任务 5 项（残留清理/任务补登记/采集链评估/注册补登/立项条目补登评估）；⑧ §2.4 待评估项新增 5 行（国债期货交割日/MLF 操作日/财报强制披露截止窗口/央行 OMO 与经济数据发布日/富时A50期货交割日——A50 为第4轮搜索新发现，每月倒数第2个工作日，离岸衍生品隔夜调仓直接影响 A 股次日跳空，优先级高于国债期货交割日）；⑨ §5.7 补过度工程审查（MVP 最小集=施工项 4+1）；⑩ frontmatter 修正：related_issues 移除注册表中不存在的立项条目引用，scope 双值改单值（01 号规范 §4.2 单值范式）。教训：schema DDL 落盘 ≠ 采集链施工完成，盘点类文档须以 Grep 实证为准。另注：本版修正曾遭并发会话回滚三次，此为重放写入并立即 git add 保护 |
| v0.2.1 | 2026-08-12 | 第6轮一致性审查·交叉引用补全：§6.6-2 补 15 号下游依赖注记（15 号 PIT Embargo"BDay 近似换真交易日历"待决策项依赖 calendar_event 表有数据）+ 63 号 v2.1.0 交叉佐证（63 号已将 calendar_event 等 6 表列入"代码零引用但规划已登记"类别，与本版 §3.2/§3.3 核实结论互验）；§6.6-4 补 62 号引用（品类注册补登施工规范见 G62 总案） |
| v0.2.2 | 2026-08-12 | 作战地图全覆盖补丁——BM-POS-08。新增 §2.5 日历→仓位约束规则：日历事件→临时仓位上限裁决表 6 条（期权交割日否决新开仓/4 月下旬年报截止 ST 清零/预告截止前 5 日否决新买入/微盘股信息空窗收紧 50%/交割日前后下调 5-10%/财报前 3 天降仓位+禁新建，参数以作战地图 indicators 为准核对），数据基座=本文既有 calendar_event 资产（§3.5 event_type 枚举）；输出 CalendarPositionAlert+临时仓位上限 → BM-POS-01/BM-POS-04 消费，与 regime Shrinkage/回撤 Protocol 乘性叠加取最紧；降级=日历数据缺失跳过约束（§3.3 空表即整体降级态）。补定位→裁定（理由+重评条件）→契约→降级四层 |
| v1.0.0 | 2026-08-13 | **定稿转 active**（AI-STD-001 定稿会话）：① §5 治本方案逐项定稿，新增 §5.8 定稿结论表——项4 符号一致性 gate 采纳且最优先（定稿明确为**双向校验**：路由引用方法须真实定义 + capability 声明须有对应 `_fetch_<cap>` 实现，§5.5 已回填）；项1 CapabilityContract 语义字段（expected_market/expected_variety，可选零迁移）采纳紧随；项2 semantic_registry 采纳与项3同批（初始登记 hk_trade_calendar/trade_calendar/industry_class 3 条，仅易混淆类强制）；项3 AST gate 采纳（验收用例=检出 #ARCH-DATA-001 + #ARCH-CH-INDUSTRY-CLASS-MIGRATE）；项5 运行时抽样推迟并明确启动条件。MVP 最小集=项4+项1 维持不变；② §5.3 维护责任待拍板点落定（MVP=选项B warn不拦）；③ §6 讨论项定夺——§6.1 选项B+升级A触发条件（稳定运行一个治理窗口，或同类bug再现立即升级）；§6.2 MSCI 裁定MVP空置、未来优先iFind路径；§6.3 裁定CSV录入+一次性IMPORT为标准路径、随§6.6-2同批执行；§6.5 ETF赎回日不建表关闭；§6.6-3 三条akshare采集链暂缓施工（MVP聚焦实盘生存级，风险优先让位calendar_event回填；未来启动先登CAND）；§6.6-5 裁定不单独立项、本文档承载追踪；④ §1.2 阻塞表述解除（设计定稿落本文档§5.8，治理裁定仍在注册表）；⑤ frontmatter status draft→active、version 0.2.2→1.0.0、date→2026-08-13。注：#ARCH-DATA-001/002 注册表 fix_phase 回填因 bm-fill 会话占用 architecture_issue_registry.yaml 未同步，待释放后由后续会话执行（多会话并发防护铁律） |
| v1.0.1 | 2026-08-15 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08）——① §3.2/§3.3/§3.4 v0.2.0 修正说明各压为一段（"DDL 落盘≠注册落盘/任务落盘/方法落地"教训保留）；② §3.5 注记去行号留函数名稳定标识；③ §6.1/§6.2/§6.3/§6.4/§6.5 已定稿讨论项去除过程性"待讨论/倾向"残留，定稿裁定逐字保留；§2 清单/§3 盘点/§4 止血/§5 治本/§5.8 定稿/§6.6 台账/§7 文件清单零改动 |
