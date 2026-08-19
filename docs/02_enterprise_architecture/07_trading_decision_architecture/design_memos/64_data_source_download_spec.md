---
ttl: permanent
doc_type: architecture_view
title: 数据源与下载体系规范
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.4.2"
date: 2026-08-15
topic: data_source_download_spec
scope: 07_trading_decision_architecture
depends_on:
  - "15_data_feature_layer_spec.md（数据与特征层规范——数据进来后怎么用）"
  - "63_data_utilization_audit.md（数据利用审计）"
  - "docs/03_modules/_domain_data/data_source_integrator_blueprint.md（MOD-L00-004 数据源集成器蓝图——what 层真源）"
  - "docs/02_enterprise_architecture/02_domain_architecture_docs/11_d_data.md（D_DATA 域 183 模块清单）"
related_issues:
  - "#ARCH-IFIND-FAILOVER（iFind 试用到期，主源降级 fallback）"
  - "#ARCH-CH-001~005（ClickHouse 写入五项架构裁定）"
  - "#ARCH-CH-022（CapabilityContract 机器可执行契约）"
  - "#ARCH-CH-024（business_data_categories.yaml 表名 SSoT 消费层）"
  - "#ARCH-CH-029（known_data_gaps 已知历史缺口注册表）"
  - "#ARCH-DATA-001（hk_trade_calendar 数据源错配修复）"
  - "#ARCH-DATA-002（capability-API 语义对齐校验——#ARCH-DATA-001 系统性治本，17 号 §5）"
  - "#ARCH-REALTIME-ACCUM（时间敏感型数据每日积累）"
  - "#ARCH-DATA-014（L2 行情权限缺失降级）"
  - "ARCH-SPECIAL-DAYS（特殊交易日数据资产——v1.4.0 已裁定补登记正式 ARCH 条目，见 §16.3 Q13；registry 登记落地后恢复 # 前缀引用）"
  - "#ARCH-EDB-EXPAND（EDB 国际宏观数据扩展）"
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-13 第一批（会话 AI-DSD-001）定稿；2 项费用裁定拍板——暂不续费 iFind（免费源已替代）、暂不开通 Level-2 行情。
>
> **最终成果**：15 数据源/130+ 下载任务/11 档调度的下载体系规范定稿（与 63 号数据利用审计配套：63 审"用得怎么样"，本档审"下得怎么样"）；2026-08-15 数据链路巡检实证下载链路正常、核心数据完整（40+ 张表 3.4 亿行回补，无可行动而未行动的缺口）。
>
> **未做事项及原因**：§12 的 12 项待裁定为常驻开放议题——随数据供应链演进逐项裁定，非施工缺口。
>
> **2026-08-19 复核补正（AI-NIGHT-001）**：原报告"未做事项"仅述 §12 常驻议题，漏核 §16.2「裁定施工」14 项的执行态。逐项实证：Q5 北向（AI-NORTH-001 已 merge 87f50a5e3f）、Q6 冷归档（AI-ARCH-001/002 已闭环）、Q13 ARCH-SPECIAL-DAYS（已登记 architecture_issue_registry）、Q14 死 fallback（tasks.yaml 实证 qmt/exchange/bdpan 已清零、local_valuation 保留 1 处在位）——4 项已闭环；**Q8 data parts>100 告警、Q16 fetch_perf scheduler 被动记录、Q17 per-source 自动熔断器、Q18 create_provider internal 接线（P0）——4 项未施工**（2026-08-19 实证：data 域无 parts 告警实现 / circuit_breaker 零命中 / fetch_perf 仅 speed_tester 写入 scheduler 零写入 / create_provider 无 internal 分支，tasks.yaml `hk_trade_calendar_refresh` source: internal 经 `_get_provider` 会报"未知数据源"失败）。Q18 为 §16.2 唯一 P0 且影响港股日历月度刷新，建议优先排期；Q8/Q16/Q17 裁定=未来工程-小型。

# 数据源与下载体系规范

> **性质**：spec / 工程详设。记录数据源与下载体系（D_DATA 域·数据获取基础设施）已施工基础设施的 why。
> 本目录文档种类适配见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §4.4——spec 类按对象内在结构组织，本文 §3-§10 决策按数据获取管线的 8 个对象分节。
>
> **与现有文档关系**：
> - **接管 why 层** [data_source_integrator_blueprint.md](../../../03_modules/_domain_data/data_source_integrator_blueprint.md)（MOD-L00-004 数据源集成器蓝图——what 层真源，本文补 why）
> - **引用** [data_source_operation_manual.md](../../../03_modules/_domain_data/data_source_operation_manual.md)（MOD-L00-002 数据源 API 操作唯一真源——"怎么调用+参数坑"）
> - **互补不重叠** [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)（G01 数据与特征层规范——15 号偏"数据进来后怎么用"PIT/特征仓库/因子工程，本文偏"数据怎么进来"Provider/调度/落库/韧性）
> - **引用** [11_d_data.md](../../../02_enterprise_architecture/02_domain_architecture_docs/11_d_data.md)（D_DATA 域 183 模块清单）
> - **配套** [63_data_utilization_audit.md](63_data_utilization_audit.md)（数据利用审计——63 号审"数据用得怎么样"，本文审"数据下得怎么样"）
> - **引用** [data_inventory.md](../../../02_enterprise_architecture/05_dataflow_architecture/data_inventory.md) + [data_acquisition_requirements.yaml](../../../02_enterprise_architecture/05_dataflow_architecture/data_acquisition_requirements.yaml)（业务数据现状 + 数据获取需求 P0-P3）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G29 数据源与下载体系（跨切治理层·6x 段位） |
| 所属 | 跨作战地图 01-12（数据是所有业务层的地基） |
| 依赖 | 无（最底层基础设施） |
| 对标 | WorldQuant 数据管线 / Numerai 数据接入 / 机构数据中台（Tushare/Wind/iFinD 商业化方案） |
| 正交性 | ✅ 与 regime/alpha/组合/风控/执行全部正交——纯数据基础设施 |
| 优先级 | P0（地基，但已大规模施工——本文是已施工设施的 why 回填 + 全面升级讨论载体） |
| 状态 | ✅ active v1.4.0（2026-08-13 定稿：§12/§16 全 35 项裁定收敛——待人拍板 2（费用类，默认建议已给）/ 裁定施工 14 / 裁定暂缓·维持·不做 19（均带理由与重评条件）；裁定单一真源在 §16，§12 各小节只留结论指针防内容漂移） |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是 A 股量化交易系统（miniQMT，T+1，不能做空），个人 + 100% AI 开发。数据获取基础设施已大规模施工（2026-08-12 实测），但此前只有 what 层文档（蓝图/操作手册/域清单）缺 why 层——未来 AI 不知设计缘由会"优化"成另一个样子，飘移发生。本备忘补 why，§12 为全面升级讨论载体（v1.4.0 已裁定收敛）。

- **代码层**：`src/zephyr/data/` 63 个 .py 文件，含 Provider 抽象 + 15 个数据源实现 + 调度编排 + 质量门控 + 落库 + 韧性容灾全链路。
- **配置层**：`tasks.yaml` 154 个采集任务（含 10 个 disabled）；`schedule.yaml` 15 个调度时段条目（L0~L11 含 L2.5/L3.5/L10.5）；`data_sources_registry.yaml` 12 个数据源元数据 + policy 字段。
- **落库层**：ClickHouse 三库 `c1_market`（行情/资金/宏观/静态约 80 表）+ `c3_fundamental`（基本面/新闻/股东约 22 表）+ `c0_meta`（fetch_perf 性能记录）。
- **文档层**：`_domain_data/` 7 篇 + `_domain_mkt_data/` 6 篇 + `11_d_data.md`（D_DATA 域 183 模块）+ `05_dataflow_architecture/`（data_inventory + data_acquisition_requirements）。

### 2.2 核心问题

1. **15 个数据源特性差异极大如何统一管理**：iFind 配额制/miniQMT 单线程+进程依赖/AKShare 60RPM+断 VPN/baostock 线程局部登录/tushare token 积分/tickflow 限流/tdx bestip/rss SSL……每源限流/重试/反爬/登录刷新策略完全不同，不能一个装饰器统一。
2. **154 任务如何调度不冲突不遗漏**：盘中实时/盘后日K/夜间财务/周末校准/月初静态多频次混排，miniQMT 非交易日连不上、iFind 配额耗尽、AKShare 反爬封锁等运行时故障常态。
3. **ClickHouse 写入如何不炸**：5204 只股票逐个写入 = 5204 个 data parts，CH merge 满载崩溃（2026-07-09 实际事故）。
4. **数据源失败如何不丢数据**：iFind 试用到期/akshare API 损坏/网络中断，单源失败不能让整张表断档。
5. **新增表如何自动纳入运维**：新表只要在 tasks.yaml 注册任务，应自动获得 fallback/补下载/巡检三层保护，无需手动改配置。

### 2.3 约束条件

- 个人 + 100% AI 开发，轻量优先，避免需要多人与外部服务协作的过度工程（不引入 Feast/Tecton 等商业 Feature Store）。
- ClickHouse 单机部署（Hyper-V VM `172.24.30.100`，2026-07-16 从 WSL2 迁移），不依赖云托管。
- miniQMT（xtquant SDK）非线程安全，单线程模型；周末/节假日 QMT 服务器关闭登录（error 10061）。
- 全部参数从 YAML/config 读取，不硬编码（date_col/engine/策略等）。
- 所有数据永不删除（PS-CTR-003 数据保留契约铁律），只保留或归档。

## 3. 数据获取管线总览

```
外部数据源(15) → IngestProviderBase(connect/health_check/fetch/disconnect) ──→ SourcePolicy(RPM/重试/退避/反爬/登录刷新)
              → CapabilityContract(机器可执行契约 #ARCH-CH-022，启动校验 fail-closed)
→ scheduler.py(APScheduler 15 时段) → task_queue(DAG) → error_classifier(不可恢复→立即fallback / 可恢复→重试用完fallback) → fallback_sources(主源→副源)
→ BufferedWriter(攒批≥50000行/30s) → ch_writer(clickhouse-driver TCP) → c1_market(~80表)/c3_fundamental(~22表)/c0_meta.fetch_perf
   引擎统一 ReplacingMergeTree(#ARCH-CH-002) 直接 INSERT 后台去重；8 个 MergeTree 遗留表写前 DELETE 幂等
韧性三层：①fallback(主源→副源) ②L10 周一02:00 全表补下载(backfill_checker 动态发现全表回看7天) ③L11 每日23:00 完整性巡检(integrity_checker)
   + 新增表门禁 DATA-TASK-COMPLETENESS(warn级)；progress_store(SQLite 断点续传)/alerter/metrics/source_health_check/fetch_perf
```

设计要点（why）见 §5.1 Provider 接口五条设计决策 + §5.2 CapabilityContract 裁定。

## 4. 数据源全景

### 4.1 15 个数据源分类

| 类别 | 数据源 | source_name | 认证 | 线程安全 | 核心能力 | 状态 |
|---|---|---|---|---|---|---|
| **实盘行情** | miniQMT | miniqmt | 三要素+进程 | single_thread | 日K/分钟K/Tick/期权Greeks/板块/港股/美股 | ✅ 主力 |
| 实盘行情 | XtMiniQmt.exe | qmt | 同上 | single_thread | ⚠️ 占位无 Provider 实现（create_provider 无 qmt 分支，主源任务=0，仅 fallback 引用 7 处——死配置，见 §12.12） | 🟧 占位 |
| **商业基本面** | iFind | ifind | license_key | thread_local | 估值/EDB/iwencai/RealtimeQuotes | 🔴 试用到期降级 |
| **免费行情** | AKShare | akshare | anonymous | shared(60RPM) | 分红/质押/解禁/宏观/股东/涨跌停/生猪 | ✅ 主力（ifind 降级后承接，61 个主源任务） |
| 免费行情 | baostock | baostock | anonymous | thread_local | K线/财务/交易日历/指数成分（滞后1周） | ✅ fallback |
| 免费行情 | tushare | tushare | token | shared(200RPM) | 行业分类/新闻（积分制） | ✅ 升主源（ifind 降级） |
| **板块专用** | tqcenter | tqcenter | 需通达信进程 | single_thread | 880xxx 板块K线/成分股/实时快照 | ✅ 2026-07-30 升自动调度 |
| 板块专用 | mootdx/TDX | tdx | bestip | shared | 880xxx 板块分钟K线（TCP 直连盘中实时） | ✅ |
| **新闻舆情** | 财联社 | cls | 无 | shared | 财联社电报（HTTP 直连） | ✅ |
| 新闻舆情 | 东方财富 | eastmoney_news | 无 | shared | 7x24 快讯（HTTP 直连） | ✅ |
| 新闻舆情 | RSS | rss | 无 | shared | 36氪/钛媒体/华尔街见闻等 8 源 | ✅ |
| **海外数据** | TickFlow | tickflow | 无 | shared(60RPM) | 美股 K线/美股指数（⚠️ 无港股 capability——代码仅声明 kline_us_daily/us_index，§4.2 已修正） | ✅ |
| 海外数据 | FRED | fred | API_KEY | shared | 美国宏观（GDP/CPI/失业率/国债/原油/黄金/VIX） | ✅ 2026-08-04 新增 |
| 海外数据 | EIA | eia | API_KEY | shared | 能源（石油库存/价格/天然气） | ✅ 2026-08-04 新增 |
| **另类数据** | 和风天气 | qweather | API_KEY | shared | 40 城市实时+7天预报（免费版无历史） | ✅ 每日积累 |
| 内部计算 | InternalCompute | internal | 无 | shared | 技术指标/日历事件/港股日历（本地算非外拉） | ⚠️ Phase 1+2 完成但 create_provider 未接线 internal 分支（见 §12.12 P1 缺口） |

### 4.2 数据源能力矩阵（关键能力 × 数据源）

> 完整矩阵真源：`architecture_model/data/data_sources_registry.yaml`（12 个数据源元数据 + policy JSONB）+ `src/zephyr/data/config/tasks.yaml`（154 任务的路由表，2026-08-12 实测）

| 能力 | miniqmt | ifind | akshare | baostock | tushare | tdx | tqcenter | tickflow | cls/em/rss | fred/eia | qweather | internal |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 日K线 | ✅主 | fallback | fallback | fallback | — | — | — | — | — | — | — | — |
| 分钟K线 | ✅主 | — | — | — | — | — | — | — | — | — | — | — |
| 后复权 | ✅主 | fallback | fallback | — | — | — | — | — | — | — | — | — |
| Tick | ✅主 | — | — | — | — | — | — | — | — | — | — | — |
| 板块880 | — | fallback | — | — | — | ✅分钟 | ✅日K | — | — | — | — | — |
| 期权/Greeks | ✅主 | fallback | fallback | — | — | — | — | — | — | — | — | — |
| 期货 | ✅主 | — | fallback | — | — | — | — | — | — | — | — | — |
| 港股 | ✅主 | — | fallback | — | — | — | — | — | — | — | — | — |
| 美股 | — | — | fallback | — | — | — | — | ✅主 | — | — | — | — |
| 估值PE/PB | — | 🔴降级 | ✅主 | — | — | — | — | — | — | — | — | fallback |
| 资金面 | — | 🔴降级 | ✅主 | — | — | — | — | — | — | — | — | — |
| 财务三表 | ✅主 | fallback | fallback | — | — | — | — | — | — | — | — | — |
| 股东/质押 | — | fallback | ✅主 | — | — | — | — | — | — | — | — | — |
| 新闻 | — | fallback | ✅主 | — | disabled | — | — | — | ✅主(cls/em/rss) | — | — | — |
| 宏观国内 | — | 🔴disabled | ✅主 | — | — | — | — | — | — | — | — | — |
| 宏观国际 | — | — | — | — | — | — | — | — | — | ✅主(fred/eia) | — | — |
| 技术指标 | — | — | — | — | — | — | — | — | — | — | — | ✅主(本地算) |
| 行业分类 | — | 🔴降级 | — | — | ✅主 | — | — | — | — | — | — | — |
| 交易日历 | — | — | — | ✅主 | — | — | — | — | — | — | — | ✅港股 |

### 4.3 iFind 试用到期降级事件（#ARCH-IFIND-FAILOVER）

**事件**：iFind 试用账号到期，原以 ifind 为主源的任务全部降级——ifind 降为 fallback，akshare/tushare 升为主源。

**影响范围**（tasks.yaml 中标记 `#ARCH-IFIND-FAILOVER` 的任务，2026-08-12 实测 7 类 9 任务，全部 ifind 居 fallback 首位）：`daily_valuation_incremental/full_refresh`（估值）→ akshare / `money_flow_incremental/full_refresh`（资金流向）→ akshare / `industry_class_refresh`（申万行业分类）→ tushare / `industry_class_suppl_refresh`（行业分类补充）→ tushare / `concept_sector_refresh`（概念板块）→ akshare / `realtime_snapshot_incremental`（实时快照）→ akshare / `sector_meta_refresh`（板块信息）→ akshare。**设计决策（why）**：①**不硬编码主源**——tasks.yaml `source` 字段可热切换，`fallback_sources` 保留 ifind，续费后改回 source=ifind 即恢复，无需改代码；②**降级不丢能力**——所有原 ifind 能力都有 akshare/tushare fallback 覆盖；③**EDB 例外**——`edb_data_incremental` 无 fallback（iFind EDB 配额耗尽 -4318，5万条/月不够拉 104 个宏观指标全历史），任务 disabled，待 iFind 付费版或替代源。

## 5. Provider 抽象与实现

### 5.1 IngestProviderBase 接口（why 这样设计）

**真源**：`src/zephyr/data/provider_base.py`（MOD-L00-004 §4）

```python
class IngestProviderBase(abc.ABC):
    source_name: str              # "ifind" / "miniqmt" / "akshare" ...
    meta: IngestProviderMeta      # 静态元数据

    @abstractmethod
    def connect(self) -> None: ...           # 建立连接/登录（线程局部）
    @abstractmethod
    def health_check(self) -> bool: ...      # 探活（启动验证+运行中监控）
    @abstractmethod
    def fetch(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]: ...
    @abstractmethod
    def disconnect(self) -> None: ...        # 关闭连接/登出
```

**设计决策（why）**：
1. **Provider 只拉数据返回 list[tuple]，不写 ClickHouse**——职责单一，写入由 scheduler 统一负责（否则 15 个 Provider 各写各的写入逻辑，维护噩梦）。
2. **fetch 返回 Iterator[FetchResult] 支持分批**——大表（kline_1min 130万行/日）流式下载不爆内存，每批一个 FetchResult 含 columns/rows/last_key。
3. **策略作为参数传入 fetch，基类 `call_with_policy` 公共化**——Stage 4 公共化后 15 个 Provider 共享同一套策略应用代码。
4. **异常时返回 FetchResult(error=...) 而非抛出**——重试/fallback/告警由上层 scheduler 决定，Provider 不自作主张。
5. **`_http_get` 纳入 `_call_with_policy` 重试循环**（#ARCH-RSS-INVESTING-403-001）——5xx 瞬时错误重试，4xx WAF 拦截立即抛出不浪费重试。

### 5.2 CapabilityContract 机器可执行契约（#ARCH-CH-022）

**问题**：原 `capabilities=["kline_daily", ...]` 字符串列表只是注释契约——AI 写 task 声明 Provider 未实现的能力时运行时才报错。**裁定**：升级为 `CapabilityContract` 机器可执行契约，scheduler 启动时校验 task 声明与 provider 实现一致性，不一致 fail-closed 阻断启动——100% AI 开发模式下不能靠 AI 自觉读注释。

```python
@dataclass
class CapabilityContract:
    capability_id: str                    # "top10_shareholders"
    supports_symbols_null: bool = False   # symbols=None 时是否自动获取全市场（#ARCH-CH-018）
    supports_incremental: bool = True     # 是否支持增量模式
    supports_full_refresh: bool = True    # 是否支持全量刷新
    requires_date_range: bool = True      # 是否需要 start/end 日期（宏观数据可能不需要）
```

**四字段实际使用实证**（2026-08-12 rg 全量扫描）：仅 `supports_symbols_null` 实际承载区分度（akshare 66 个契约全部 True，#ARCH-CAP-NULL-SYMBOLS-001 修复 83 条 WARN；baostock.kline_daily 唯一显式 False）；`supports_incremental`/`supports_full_refresh`/`requires_date_range` 全项目保持默认值（仅 fred/eia 5 个契约显式 `requires_date_range=True`，等于默认值）。三闲置字段是否裁剪——**v1.4.0 已裁定保留不裁剪**（§16.2 Q15，#ARCH-DATA-002 语义校验落地时复用）。

**语义边界**：CapabilityContract 刻意只覆盖"行为契约"（能不能增量/要不要日期），不覆盖"语义契约"（capability 名与实际 API 语义是否对齐）——#ARCH-DATA-001（akshare A股日历冒充港股日历）正是语义盲区事故，其系统性治本登记为 #ARCH-DATA-002（capability-API 语义对齐校验，P2，17 号 §5 施工稿），见 §12.12。

### 5.3 15 个 Provider 实现清单

| Provider | 文件 | 核心能力 | 关键设计点 |
|---|---|---|---|
| IFindProvider | ifind_provider.py | THS_RQ/THS_BD/iwencai/EDB/RealtimeQuotes | 月度配额监控(-4318/-4309)；试用到期降级 |
| MiniQmtIngestProvider | miniqmt_provider.py | 行情/财务/板块/期权Greeks/港股/美股 | single_thread+进程依赖；非交易日跳过(trading_day_only) |
| AkshareIngestProvider | akshare_provider.py | 分红/质押/解禁/宏观/股东/涨跌停/生猪/板块/市场元数据约束(stock_basic/stk_limit/suspend_status，JOB-077) | 60RPM 限流；断 VPN；东财反爬 3 次跳过 |
| BaostockProvider | baostock_provider.py | K线/财务/交易日历/指数成分/退市股历史K线(kline_daily_delisted，JOB-084) | thread_local（每线程独立 bs.login）；数据滞后1周；退市股adjustflag=3不复权对齐主口径 |
| TushareProvider | tushare_provider.py | 行业分类/新闻/ST名称变更回填(st_namechange_backfill，JOB-083) | token 积分制；新闻 API 已废弃(disabled)；namechange 无参截断 10000 行需逐年分页 |
| TickFlowProvider | tickflow_provider.py | 美股/港股 K线 | 60RPM 限流 |
| TDXProvider | tdx_provider.py | 880xxx 板块分钟K线 | mootdx TCP 直连盘中实时；bestip 自动选最快 |
| TqcenterProvider | tqcenter_provider.py | 880xxx 板块日K/成分股/快照 | 需通达信进程；2026-07-30 升自动调度 |
| ClsProvider | cls_provider.py | 财联社电报 | HTTP 直连 cls.cn/nodeapi |
| EastmoneyNewsProvider | eastmoney_news_provider.py | 东方财富7x24快讯 | HTTP 直连 np-listapi.eastmoney.com |
| RssProvider | rss_provider.py | 36氪/钛媒体/华尔街见闻等8源 | feedparser；偶发 SSL 重试；尊重 robots.txt |
| FredProvider | fred_provider.py | 美国宏观(22序列) | FRED_API_KEY；读 HTTPS_PROXY/HTTP_PROXY 环境变量设代理，health_check 失败 warn 提示（⚠️ 无自动 VPN 探测跳过——该能力仅 rss_provider._is_vpn_ready 实现，2026-08-12 代码实证） |
| EiaProvider | eia_provider.py | 能源(石油/天然气) | EIA_API_KEY；代理处理同 fred |
| QweatherProvider | qweather_provider.py | 40城市天气 | 免费版无历史API，每日积累(#ARCH-REALTIME-ACCUM) |
| InternalComputeProvider | internal_compute_provider.py | 技术指标/日历事件/港股日历 | 本地算非外拉；_fetch_xxx 必须真实定义禁止脱节 |

### 5.4 internal_compute_provider 铁律

> **project_memory 硬约束**：internal_compute_provider 中所有引用的 `_fetch_xxx` 方法必须在类体内真实定义，禁止声明与实现脱节导致 AttributeError。

**why**：internal_compute 是唯一"不拉外部数据、本地计算"的 Provider。AI 增加新能力时可能只在 capabilities 声明却忘了实现 fetch 方法，运行时 AttributeError——铁律强制声明与实现一一对应。

**实现细节**（2026-08-12 代码实证）：实际路由按 `payload.table` 分派——`calendar_event`/`hk_trade_calendar` 各有同名 `_fetch_xxx` 方法，`technical_indicator` 走默认分支 `_fetch_single_period`（非同名方法）；一致性由 `_INTERNAL_COMPUTE_CAPABILITIES` frozenset 声明 + CAP-CONSISTENCY gate 对齐保证。铁律的准确含义是"声明的能力必须有真实计算路径"，非字面"每个 capability_id 一个同名方法"。

### 5.5 symbol 标准化（symbol_normalizer/）

**真源**：`src/zephyr/data/symbol_normalizer/normalizer.py`（TRAE-082 symbol 约定铁律，#ARCH-DATA-SYMBOL-001/002）。**职责**：纯函数无副作用，幂等（已带后缀原样返回），空输入→空输出，未知前缀→exchange=None（不擅自推断）。

**A 股裸码→exchange 映射**：首位 6/5/9→SH（沪市股票/基金/B股）；首位 0/3/1/2→SZ（深市股票/创业板/基金/B股，'2'→SZ 深市 B 股 200xxx/201xxx 实测 281K 行）；首位 8/4→BJ（北交所/老三板）；3 位前缀消歧 900-903→SH B股 / 920→BJ 北交所 / 110/113→可转债；支持 SH/SZ/BJ/HK/US 五交易所。**why**：不同数据源 symbol 格式不统一（akshare `600519` vs miniqmt `600519.SH` vs baostock `sh.600519`），统一标准化后才能跨源对比和落库去重——是 §8.4 跨源验证和落库去重的前置依赖。

### 5.6 表名注册表消费层 table_registry（#ARCH-CH-024）

**真源**：`src/zephyr/data/table_registry.py`（MOD-GOV-table_registry）

**问题**：`business_data_categories.yaml` 是业务数据品类唯一真源（98 条品类记录），但改造前 0 行代码消费它——provider/scheduler 直接硬编码表名，与 tasks.yaml 形成双真源，长期漂移必然发生。**裁定**（#ARCH-CH-024）：SSoT 真源已建立声明闭环（YAML 存在）但消费闭环未建立（代码不 import 真源）；表名属于声明态规则数据（trae_062 SSoT 分类铁律：表名是 schema 声明而非 DB 实例），真源是 YAML。

**治本**：`business_data_categories.yaml` 是表名/品类唯一真源；代码 MUST 通过 `TableRegistry.table(category_id)` 派生表名**禁止硬编码字符串**；启动时加载 YAML 构建 `category_id → "{database}.{table}"` 映射；`validate_tasks_yaml()` 校验 tasks.yaml.table ⊆ registry，不一致仅 WARN（渐进式收紧；Phase 4 commit gate 将升级为 block）。

**公共接口**：`TableRegistry.table(category_id) -> str`（查不到抛 KeyError，fail-closed）/ `all_tables()` / `is_registered(table)` / `validate_tasks_yaml(tasks)` / `get_registry()`（单例幂等加载）。**why KeyError 而非返回默认**：查不到表名说明 registry 与代码脱节，fail-closed 立即暴露；返回默认值则静默漂移，违背 SSoT 初衷。

**消费现状**：scheduler._load_config() 末尾调用 validate_tasks_yaml() WARN 校验；news_dedup/sector_kline_downloader 等通过 `get_registry().table()` 派生表名（Phase 5 长期方向：240 处硬编码表名逐步替换）。

### 5.7 策略注册表 policy_registry（per-source 调用策略）

**真源**：`src/zephyr/data/policy_registry.py`（MOD-GOV-policy_registry）。**职责**：每个数据源有自己的限流/重试/反爬/登录刷新策略，集中管理、yaml 热更新。策略参数来源：`data_source_operation_manual.md`（MOD-L00-002）每源限流/防爬/登录方式描述，已固化为 `src/zephyr/data/config/policies.yaml`（派生物，真源在 `data_sources_registry.yaml` 的 policy 字段）。

**SourcePolicy 数据类**（per-source 策略）：

| 字段 | 说明 | 示例 |
|---|---|---|
| `rpm` | 每分钟最大请求数（0=不限或配额制，如 iFind） | akshare=60 |
| `concurrency` | 最大并发数（1=串行） | miniqmt=1 |
| `min_interval_sec` | 两次调用最小间隔（RPM 补充，默认 60/rpm） | — |
| `max_retries` | 最大重试次数（0=不重试） | — |
| `backoff` | 退避模式 exponential/fixed/jittered | — |
| `initial_wait_sec` | 首次重试等待秒数 | — |
| `retry_on` | 重试触发的错误码/异常名列表 | `["-201","TimeoutError"]` |
| `use_proxy` / `proxy` | 代理开关+地址 | — |
| `disconnect_vpn` | 是否须断开 VPN（AKShare 爬国内网站，VPN 致海外 IP 被拒） | akshare=True |
| `user_agent` | 自定义 UA | — |
| `respect_robots_txt` | 是否遵守 robots.txt | rss=True |

**PolicyRegistry 特性**：从 yaml 加载，`maybe_reload` 热更新；`get_policy` 未知源返回默认策略（DEFAULT_POLICIES fallback）不抛异常。**why per-source 策略对象而非统一装饰器**：15 个源特性差异极大（iFind 配额制/miniQMT 单线程/AKShare 60RPM+断 VPN/baostock 线程局部登录），统一装饰器无法表达。

### 5.8 能力校验器 capability_validator（CapabilityContract 执行者）

**真源**：`src/zephyr/data/capability_validator.py`（MOD-GOV-capability_validator）。**职责**：§5.2 的 CapabilityContract 由本模块在 scheduler 启动时校验——"注释契约"升级为"机器可执行契约"的实际执行者。

**校验规则**：①`task.capability` 必须在 `provider.meta.capability_contracts` 中（按 capability_id 匹配）——不存在 → **ERROR（阻断启动）**；②`task.symbols=null` 时 capability 应声明 `supports_symbols_null=True`——False → **WARN**；③`task.incremental=true` 时应声明 `supports_incremental=True`——False → **WARN**。**Violation 数据类**：`severity`（ERROR/WARN）+ `message` + `task_id` + `capability_id`；`validate_task_capability_contracts(tasks, providers)` 返回 Violation 列表，空列表=通过。

**设计原则**（遵循裁定#221）：不新增 .md 规则文档，转化为启动时校验（reconciler 式）；初期 WARN-only 收集数据逐步收紧为 ERROR；100% AI 开发模式下只有机器可执行契约才能达到 ~100% 遵守率。**why ERROR/WARN 分级而非全 ERROR**：supports_symbols_null=False 的历史 task 太多，一次性全阻断会瘫痪启动，先 WARN 收集数据再收紧。

### 5.9 错误分类器 error_classifier（可恢复性判断）

**真源**：`src/zephyr/data/error_classifier.py`（MOD-GOV-error_classifier，stable）。**职责**：根据 FetchResult.error 字符串判断可恢复性，驱动 §9.1 fallback 决策（不可恢复立即 fallback / 可恢复重试用完 fallback / 未知当可恢复给重试机会）。纯字符串匹配无副作用，预编译正则：

| 分类 | 关键词模式 | 处置 |
|---|---|---|
| **unrecoverable**（不可恢复） | `-4318`(iFind 配额) / `-4309`(接口废弃) / 配额/quota/deprecated/认证失败/401/403/未授权/license/`has no attribute`(akshare API 漂移) / `xtquant SDK 导入失败` | 立即 fallback |
| **recoverable**（可恢复） | Timeout/ConnectionError/RemoteDisconnected/HTTPError/JSONDecodeError/503/502/`miniQMT 已断开`/`行情服务不可用` | 重试用完 fallback |
| **unknown**（未知） | 匹配失败 | 当可恢复（给重试机会） |

**why 关键词匹配而非异常类型**：FetchResult.error 是字符串（跨 Provider 统一接口），无法 isinstance 判断。**why 未知当可恢复**：保守策略——给重试机会比立即 fallback 更安全（立即 fallback 可能不必要地切到较弱副源）。

### 5.10 数据源接入层包入口 satellite_geospatial_engine

**真源**：`src/zephyr/data/satellite_geospatial_engine/__init__.py`（MOD-L00-001，D_DATA 域）。**职责**：D_DATA 数据接入层域级包入口，re-export `IngestProviderBase` + `IngestProviderMeta`（provider_base）与 `DataQualityGate`（gov_enforcement.rule_enforcement.quality_gate）。

**CTR 契约依赖声明**（承重墙标记）：生产者——CTR-001 NormalizedMarketData → D_FACTOR/D_SIGNAL/D_RESEARCH、CTR-TRACE-001 TraceContext（链头，trace_id 本层创建）、CTR-ERR-001 DataQualityError → D_FACTOR；消费者——CTR-BP-001~003 Backpressure ← D_FACTOR（背压：暂停/降速/恢复数据推送）。

**why 独立包入口**：D_DATA 是 LPC 双轨架构 C 轨（业务脊柱），域级包入口集中声明跨层契约依赖，是 ContractImpactAnalyzer 评估修改影响的入口点。

## 6. 调度编排层

### 6.1 为什么用 APScheduler 而非 OS 级触发器

**决策**：APScheduler 常驻进程（BackgroundScheduler + ThreadPoolExecutor），而非 Windows 任务计划/cron。**why**：①OS 级触发器无任务依赖/并发控制/重试编排能力——154 任务有 DAG 依赖（adj_factor→kline_daily_hfq→kline_weekly_hfq）无法表达；②APScheduler 支持 `coalesce`（错过多次只跑一次）+ `max_instances=1`（同任务不并发）+ `misfire_grace_time`（错过1小时内补跑）；③per-source 串行/跨源并行需线程池分流：`default` 池 8 线程给可并行源，`heavy` 池 2 线程给串行源（iFind/miniQMT）。

### 6.2 16 个调度时段条目（schedule.yaml 真源）

> schedule.yaml 实际有 16 个时段条目（2026-08-15 JOB-077 新增 L0.5 盘前元数据层 pre_market；L0~L11 编号体系，含 L2.5 板块层 + L3.5 慢新闻层 + L10.5 每日补下载层）。任务分布：daily_capital 28 / weekend_calibration 24 / daily_kline 18 / monthly_static 17 / intraday_minute 15 / daily_event 14 / intraday_realtime 13 / event_driven 12 / nightly_financial 8 / intraday_sector 5 / pre_market 5 / auction_highfreq 2 / news_slow 2 / weekend_backfill 1（daily_backfill/integrity_check 为动态发现无静态任务）。

| 时段 | cron | executor | 典型任务 | 说明 |
|---|---|---|---|---|
| L0 集合竞价高频 | */10 15-25 9 周一-五（6段含秒） | realtime | auction_snapshot/auction_book | 9:15-9:25 每10秒抓五档盘口，主力挂撤单行为分析；10s 间隔防 max_instances=1+coalesce 塌缩 |
| L0.5 盘前元数据 | 30 8 周一-五 | default(8线程) | stock_basic/stk_limit/suspend_status/index_member/st_status（JOB-077） | 开市前刷新 universe 构造与回测撮合约束前提；全 akshare 源不依赖 QMT；盘后 daily_capital 双点兜底 |
| L1 盘中实时 | */5 9-15 周一-五 | realtime(4线程) | tick_data/index_quote/auction/futures_position/kline_hk | 盘中高频轮询，独占 realtime 算力 |
| L2 盘中分钟K | */5 9-15 周一-五 | intraday_minute(4线程) | kline_1min~60min + ETF/LOF 分钟K | 盘中分钟滚动 |
| L2.5 盘中板块K线 | */5 9-15 周一-五 | intraday_sector(独立) | 880xxx 板块分钟K线（mootdx TCP 直连） | 独立执行器，避免被 miniqmt 全市场分钟K线慢任务（~5000股）阻塞 |
| L3 事件驱动 | */3 7×24 | default(8线程) | news_data/macro_data | 来了就处理；盘中提速到 */3（盘中实时分析需新闻尽快入库） |
| L3.5 慢新闻 | */30 7×24 | default | 个股新闻(stock_em)/研报(research_report) | 5523只串行限流~90min，独立队列不堵 L3 快新闻；与 research_report 共享 akshare 60RPM 额度 |
| L4 盘后日K | 30 16 周一-五 | heavy(2线程) | kline_daily/hfq/adj_factor/index/valuation/周月K | 日频核心先跑 |
| L5 盘后资金 | 00 18 周一-五 | default | margin/block_trade/dragon_tiger/money_flow/futures/us | 资金面+外盘 |
| L6 盘后事件 | 00 19 周一-五 | default | analyst_forecast/dividend/disclosure_plan | 事件类 |
| L7 夜间财务 | 00 22 周一-五 | heavy | balance_sheet/income/cashflow/financial_indicator/shareholders | 低频财务 |
| L8 周末校准 | 00 3 周一 | heavy | 全量校准/TDX板块/概念板块/美股全量 | 原周六改周一(QMT周末连不上) |
| L9 月初静态 | 00 9 1 * * | default | stock_list/index_list/trade_calendar/etf_list | 月度刷新 |
| L10 周末补下载 | 00 2 周一 | heavy | tick_data补下载+全表缺失检测 | 动态发现tasks.yaml全表，回看7天 |
| L10.5 每日盘后补下载 | 00 17 周一-五 | heavy | 当日缺口检测+自动补下载 | 治本#ARCH-DATA-TICK-GAP-001，当天发现当天补（不依赖 L10 周末窗口） |
| L11 完整性巡检 | 00 23 周一-五 | default | integrity_check_daily | 全表达标检测 |

**why L2.5 独立执行器**：miniqmt 全市场分钟K线（~5000 股）慢任务共用执行器会阻塞板块K线；mootdx TCP 直连 880xxx 是独立通道（不走 miniqmt）。**why L10.5 当天补**：L10 周末回看7天，tick_data 当日缺口若等到周末才补，期间回测/策略已用错数据；L10.5 盘后立即检测当天补，#ARCH-DATA-TICK-GAP-001 治本。

### 6.3 miniQMT 交易日约束（2026-07-19 裁定）

**问题**：QMT 服务器周末/节假日关闭登录服务（error 10061 WSAECONNREFUSED），miniqmt 任务非交易日触发必然失败。**裁定**：①`TRADING_DAY_GUARDED_SCHEDULES` 覆盖 L1/L2/L4/L5/L6/L7/L11 共 8 个时段，scheduler 非交易日自动跳过；②L8 改周一 03:00（原周六 02:00），确保周末后首个工作日 QMT 可用；③L9 不在守卫列表（含 ifind/akshare 任务需周末/月初跑），但 miniqmt 源任务必须标 `extra.trading_day_only: true`，由 `_filter_schedule_tasks` 非交易日过滤；④`cli run <task_id>` 手动触发绕过守卫，用户自判时机。

### 6.4 任务依赖图（DAG）

```
adj_factor ──→ kline_daily_hfq ──→ kline_weekly_hfq / kline_monthly_hfq
kline_daily ──→ daily_valuation (PE/PB 基于 kline)
            ──→ technical_indicator (internal 算指标依赖日K)
stock_list ──→ (所有依赖标的列表的任务)
index_list ──→ index_constituent ──→ kline_index
industry_class ──→ kline_sector (板块K线依赖行业分类)
etf_list ──→ etf_benchmark
trade_calendar ──→ calendar_event (internal 派生日历事件)
kline_futures ──→ futures_term_structure
option_kline ──→ option_greeks
kline_sector_880 ──→ kline_sector_880_resample
```

**why**：依赖通过 `task_queue.py` DAG 管理，前置未完成则当前任务 PENDING——避免 adj_factor 没下载完就跑 kline_daily_hfq 导致复权错算。

### 6.5 失败重试与告警

**重试链**：任务级重试（Provider 内部按 SourcePolicy 重试瞬时错误）→ 数据源 fallback（主源失败自动尝试副源，§9.1）→ 调度级重跑（DEAD 任务进 `failures/` 目录，CLI `integrator rerun-failed` 一键重跑）→ L10 周末补下载（周一 02:00 检测过去7天全表缺失并补下载，不依赖 last_key）→ L11 每日巡检（23:00 盘后全表达标检测，不达标告警）。**告警触发**：任务 DEAD / 主源 fallback / 单日失败率>5% / 某源连续3天失败 / iFind -4318 / L11 巡检不达标。

### 6.6 Tick 订阅独立常驻进程（tick_subscriber.py）

**真源**：`src/zephyr/data/tick_subscriber.py`（MOD-L00-001，#ARCH-CH-013）。**职责**：QMT 实时 Tick 订阅服务——subscribe_quote 实时推送写入 ClickHouse tick_data，**独立常驻进程不走 scheduler cron**。启动：`python -m zephyr.data.tick_subscriber`，由 `ZephyrAlpha_TickSubscriber` Task Scheduler 任务守护（§10.5）。

**架构**（P0-1 主动 WAL）：
```
QMT callback 线程 ──put_nowait──→ queue.Queue ──批量出队(500条)──→ flush 线程
                                                                    ↓
                                                          构造 FetchResult
                                                                    ↓
                                                          WalWriter 先落盘段文件
                                                                    ↓
                                                          异步 drain 到 ClickHouse
```

**设计要点**：QMT callback 线程只做 `queue.put_nowait`（最小开销不阻塞行情推送）；flush 线程批量出队（500 条）构造单个 FetchResult 交 WalWriter；**WalWriter 先落盘段文件再异步 drain 到 CH**（P0-1 主动 WAL，CH 不可达不丢 tick）；**15 字段**：trade_date/timestamp/recorded_time/symbol/market_type/price/volume/amount/direction/data_source/bid_price/ask_price/bid_volume/ask_volume/quality_flag；**P1-5 metrics** received/written/dropped/queue_size + **P2-5 分阶段延迟 Histogram**（on_tick/queue_wait/convert/wal_add/wal_flush 五 Stage）；无锁计数（CPython GIL 保证 int += 1 精度足够）。**why 独立进程而非 scheduler 任务**：tick 是实时推送（subscribe_quote callback）非轮询，不能走 cron；独立进程避免高频回调阻塞 scheduler 其他任务；独立心跳监控（§10.6 四层防御）确保崩溃自愈。

### 6.7 交易日历守卫 trading_calendar

**真源**：`src/zephyr/data/trading_calendar.py`（MOD-GOV-trading_calendar，stable）。**职责**：基于 `exchange_calendars` 包的 XSHG（上交所）日历精确判断交易日（含节假日/调休），纯 Python 本地计算不依赖网络/DB；scheduler 在盘中/盘后时段触发前调 `is_trading_day()`，非交易日自动跳过。XSHG 日历懒加载单例缓存；未安装时降级 weekday 判断；`is_trading_day` 永不抛异常。

**TRADING_DAY_GUARDED_SCHEDULES**：L0/L1/L2/L4/L5/L6/L7/L10.5/L11 需守卫；**不需守卫**：L3 event_driven（7×24）/ L8 weekend_calibration / L9 monthly_static / L10 weekend_backfill（含非交易日需运行的任务）。**why exchange_calendars 而非自建日历表**：成熟开源库含历年节假日/调休，自建易遗漏调休；XSHG 与 A 股交易日完全对齐。

### 6.8 板块三件套（sector_kline_downloader / sector_ranking_engine / sector_snapshot_collector）

> 880xxx 申万板块指数数据的下载/排名/快照采集三个独立常驻模块，均 `python -m` 手动启动，task_bound TTL。

#### 6.8.1 sector_kline_downloader——板块K线下载器

**真源**：`src/zephyr/data/sector_kline_downloader.py`。**职责**：盘后从 tqcenter 下载 880xxx 板块指数K线（1d/1m/5m 三周期）写入 ClickHouse `kline_sector_880` 表；50 只/批分批避免 tqcenter 超时；ReplacingMergeTree 幂等写入。**约束**：tqcenter 仅支持 1d/1m/5m，15m/30m/60m 需 §6.9 kline_resampler 从 1m/5m 合成。

#### 6.8.2 sector_ranking_engine——板块动态排名引擎

**真源**：`src/zephyr/data/sector_ranking_engine.py`。**职责**：5 因子复合排名动态调整 99 只推送池，每日盘前重算一次。

**5 因子复合排名**（权重之和=1.0）：成交额 amount **30%**（板块活跃度）/ 涨跌幅绝对值 **25%**（板块波动）/ 主动交投量（outside+inside）**20%**（volume 恒为 0 的替代方案）/ 5分钟动量 **15%** / 板块-大盘强弱差 **10%**（相对强度）。**大盘基准**：880001.SH（上证指数），缺失时用全板块涨跌幅均值；百分位排名消除量纲。**回退**：sector_snapshot 表无数据时回退成分股数量 Top99。

#### 6.8.3 sector_snapshot_collector——板块实时快照采集器

**真源**：`src/zephyr/data/sector_snapshot_collector.py`。**职责**：方案 C 混合模式采集 880xxx 板块实时快照（99 只推送 + 全量轮询 30 秒）写入 `sector_snapshot` 表。

**混合模式架构**：①推送层 `subscribe_hq` 订阅核心 99 只（§6.8.2 动态选取），~18 秒/次推送；②轮询层 `get_market_snapshot` 每 30 秒轮询全量 582 只（实测 2026-07-22：454 个 880xxx + 128 个 881xxx）；③推送通知或轮询触发时取 26 字段写入 ClickHouse。**why 混合模式**：纯推送只覆盖 99 只核心板块，全量 582 只需轮询补全；纯轮询 30 秒延迟对核心板块太高——核心推送低延迟 + 全量轮询兜底。

### 6.9 K线合成器 kline_resampler

**真源**：`src/zephyr/data/kline_resampler.py`。**职责**：从 `kline_sector_880` 的 1m/5m 合成 15m/30m/60m K线写入同表（ClickHouse `toStartOfInterval` 聚合在 DB 内完成，避免数据搬运）。

**合成规则**（标准 OHLC 聚合）：open=`argMin(open, timestamp)` / high=`max(high)` / low=`min(low)` / close=`argMax(close, timestamp)` / volume=`sum(volume)` / amount=`sum(amount)`。**幂等**：DELETE + INSERT（按 period + trade_date 先删后插），盘后批量执行。**why DB 内合成**：582 板块 × 多周期 × 多日数据量大，拉到 Python 聚合是数据搬运浪费，CH 列式聚合在 DB 内完成。

### 6.10 新闻采集去重（news_collector / news_dedup）

#### 6.10.1 news_dedup——新闻去重模块

**真源**：`src/zephyr/data/news_dedup.py`（MOD-GOV-news_dedup）。**职责**：基于标题 MD5 哈希对新闻查重去重——不同新闻源（AKShare/财联社/东方财富/RSS）内容可能重复，避免同一新闻多源重复写入 `fund_news_data` 表。

**机制**：查询 CH 最近 N 天（`_DEDUP_WINDOW_DAYS=7`）已有新闻标题哈希集合 → 过滤已存在哈希 + 批次内重复 → **fail-open**（去重异常时跳过返回原始数据，不阻断写入）。**NEWS_DATA_COLUMNS 标准列**：news_id/publish_time/title/content/summary/source/source_url/data_source/region/language；#ARCH-RSS-INVESTING-403-001：显式写入 region/language，避免海外新闻被表 DEFAULT 误标 CN/zh。**why 标题 MD5 而非内容哈希**：标题是新闻唯一性最强字段，内容可能因源不同有编辑差异；MD5 快且定长。

#### 6.10.2 news_collector——新闻数据采集器

**真源**：`src/zephyr/data/news_collector.py`（MOD-DATA-NEWS-001，design 阶段）。**职责**：从 ClickHouse `fund_news_data` 按条件查询新闻返回标准列 DataFrame，供 P1-E3 NLP 管道（评估集构建、批量推理）使用；复用 `ch_reader.query()` + `regime_data_loader.parse_tsv`，不重复造 TSV 解析轮子。**PIT 严格**：`publish_time <= end_date` 不泄漏未来新闻（与 §8.6 PIT 铁律对齐）。**why 查询器独立于下载器**：news_dedup 是写入端去重（scheduler 调用），news_collector 是读取端查询（NLP 管道调用），职责分离。

## 7. 落库体系

### 7.1 ClickHouse 引擎统一裁定（#ARCH-CH-002）

**原设计**：全部 MergeTree + 先删后插，理由"数据源唯一不需要去重"。**实际事故**（2026-07-09）：5204 只股票逐个写入时，"先删后插"= 5204 次 ALTER DELETE mutation + 5204 次 INSERT = 双倍 data parts，CH CPU 352% merge 满载崩溃，kline_1min 1039 parts / kline_daily 788 parts。

**裁定**：废弃"全部 MergeTree + 先删后插"，统一 `ReplacingMergeTree` + 直接 INSERT，CH 后台去重，零 mutation 开销。**8 个例外**（c3_fundamental 的 MergeTree 遗留表）：share_unlock/restricted_shares/analyst_forecast/disclosure_plan/equity_pledge_detail/rights_issue/share_change/industry_class_suppl——scheduler.run_task 对这些表写前执行 `DELETE WHERE toDate(date_col) IN (start..end)` 保证幂等，date_col 从 tasks.yaml 读取（禁止硬编码）。

### 7.2 BufferedWriter 批量聚合层（#ARCH-CH-003）

**问题**：ch_writer 逐个 FetchResult = 1 次 INSERT，5204 只股票 = 5204 个 data parts，违反 CH 官方"每秒≤1次INSERT，每次≥1万行"约束。**裁定**：Provider 和 ch_writer 之间插入 BufferedWriter，攒批写入（按行数 ≥50000 或时间窗口 ≥30 秒触发），预期 5204 次 INSERT → 1-3 次 INSERT。

### 7.3 ch_writer 混合传输（#ARCH-CH-005）

**裁定**：混合传输架构——`query()`/`delete_where()` → clickhouse-driver TCP（2.9x 查询加速，无类型问题）；`write_tsv()` → 保留 WSL subprocess TSV（TSV 自动处理类型转换，1.6x 提速不显著）；clickhouse-driver 不可用时自动降级 WSL subprocess。

**后续变更**（2026-07-16 Hyper-V 迁移，#ARCH-CH-010/013 resolved）：ClickHouse 从 WSL2 迁至 Hyper-V VM（172.24.30.100 固定 IP），`_discover_wsl_ip()` 移除，WSL subprocess fallback 通道移除，统一走 clickhouse-driver TCP 直连。

### 7.4 数据保留铁律（PS-CTR-003）

> **真源**：`data_retention_contract.yaml`（PS-CTR-003 v1.0.0）

1. **所有数据永不删除**——只保留或归档，不 DROP / DELETE / TTL 自动删除
2. **进 Cold 层必须手动触发**——不自动迁移
3. **所有表 Hot 层无 TTL**——ClickHouse 永久保留

**已执行变更**：2026-07-14 删除 `c1_market.index_quote` 表 90 天 TTL（违反铁律 INV-RET-003）。

### 7.5 落库表全景（三库）

**c1_market（行情/资金/宏观/静态 ~80 表）**：K线类（kline_daily/hfq/weekly/monthly/weekly_hfq/monthly_hfq/1min~60min/etf_*/lof_*/index/sector/sector_880/sector_intraday/cb/option/hk_daily/hk/us_daily/futures/futures_kline_qmt）/ Tick快照（tick_data/l2_tick/auction_snapshot/auction_book/index_quote/realtime_snapshot）/ 复权估值（adj_factor/daily_valuation/stock_valuation）/ 资金面（margin_trading/block_trade/block_trade_detail/dragon_tiger/dragon_tiger_seat/money_flow/hk_connect_flow）/ 宏观（macro_data/edb_data）/ 衍生品（futures_position/futures_term_structure/option_iv_surface/option_greeks/convertible_bond_iv）/ 静态日历（trade_calendar/hk_trade_calendar/calendar_event/stock_list/stock_basic/index_list/index_constituent/index_weight/index_adjustment/msci_adjustment/industry_class/industry_class_suppl/concept_sector/concept_board/sector_list/sector_meta/sector_constituent/sector_snapshot/convertible_bond_list/etf_list/etf_nav/etf_benchmark/lof_list/hk_stock_list/st_stock_list/ipo_schedule/margin_target_adjustment）/ 市场约束（stk_limit/suspend，JOB-077 DS-082/083，回测撮合前提）/ 另类（hog_spot_index/hog_futures_core/hog_province_spot/weather_data/stock_hot_rank/limit_up_down/technical_indicator/us_index）

**c3_fundamental（基本面/新闻/股东 ~22 表）**：新闻（news_data 多源统一表，含 cls/em/rss/akshare/tushare）/ 财务（balance_sheet/income_statement/cashflow_statement/financial_indicator/main_business）/ 股东事件（shareholder_count/analyst_forecast/earnings_forecast/express_report/audit_opinion/dividend/rights_issue/share_unlock/restricted_shares/share_change/equity_pledge_detail/equity_pledge_summary/top10_shareholders/top10_circulating_shareholders/disclosure_plan/repurchase/research_report）

**c0_meta（元数据）**：fetch_perf（Capability 实测性能记录，source+capability+test_date ORDER BY，api_status 枚举 ok/slow/rate_limited/blocked/broken/pending）

### 7.6 CH 配置与读取层

#### 7.6.1 ch_config.py——连接配置单真源（#ARCH-CH-017 / #ARCH-CH-019）

**问题**：Hyper-V 迁移前 ch_writer.py 硬编码默认值 `172.24.30.100`，database_service.py 用 `"localhost"`，两者不一致且都不主动加载 `config/.env.clickhouse`——当前能工作纯属巧合，CH 再迁移一次就会暴露。

**裁定**：`config/.env.clickhouse` 是 CH 连接配置**唯一真源**；所有 CH 连接入口必须主动读取该文件**禁止硬编码 IP 默认值**；`ensure_ch_env_loaded()` 幂等加载 .env.clickhouse 到 os.environ（文件不存在 log warning 不抛）；`load_ch_config()` 返回连接配置字典，读不到**抛 CHConfigError（fail-closed）**。

#### 7.6.2 ch_reader.py——统一读取层（#ARCH-CH-007）

**问题**：#ARCH-CH-002 统一 ReplacingMergeTree + 直接 INSERT，但去重是异步的（后台 merge 时才去重），merge 完成前查询返回重复行；100% AI 开发模式下 AI 不会主动加 FINAL（#ARCH-CH-004 教训）。

**方案**：统一读取层自动注入 FINAL——`inject_final(sql)`（纯函数，对 ReplacingMergeTree 表注入 FINAL）/ `query(sql)`（自动注入，返回 TSV）/ `count(table, where)` / `query_table(table, columns, where, ...)`。**why 统一读取层**：消除对 AI 自觉加 FINAL 的依赖——任何查询走 ch_reader 自动去重，不走 ch_reader 的裸查询是 bug。

### 7.7 本地落盘兜底与回灌

#### 7.7.1 local_replay.py——本地 TSV 兜底+自动回灌（#ARCH-CH-013 Phase 1）

**问题**：CH 二级降级链（TCP→HTTP）全部失败时，ch_writer.write_tsv 要么抛异常导致任务失败，要么丢弃数据。**方案**：CH 不可达时写本地 TSV 文件而非丢弃，scheduler 启动时 + 每 30 分钟回灌积压。

**文件布局**：`data/local_fallback/_manifest.jsonl`（每行一条 JSON：{table, cols_clause, file, rows, ts}）+ `data/local_fallback/{db}__{table}/{YYYYMMDD_HHMMSS}_{hash}.tsv`。

**回灌策略**：读 _manifest.jsonl → 按 table 分组 → 逐文件 ch_writer.write_tsv 回灌 → 成功删除文件+移除 manifest 条目 → 失败保留等下次重试；回灌用 manifest 保存的 cols_clause（不重新查表列防列数不匹配），传 `create_fallback=False` 防重复落盘。**不变式**：落盘文件原子写入（先写 .tmp 再 rename）；manifest 追加模式（JSONL）；save_fallback 永不抛异常（写入失败 log+返回 False）。

#### 7.7.2 sqlite_fallback.py——CH 降级到本地 SQLite（MOD-L00-005）

**职责**：CH 不可达时写本地 SQLite（INSERT OR REPLACE 幂等），查询层可读最近数据。**设计**：按 table 建 SQLite 表（schema 与 CH 对齐仅保留核心列）；每表最大 500K 行（约 4 小时 tick），FIFO 自动清理；get_pending_batches 返回待回灌数据；线程安全——所有 SQLite 操作经 _lock 串行化（单写者模型）。**why SQLite 而非只 TSV**：TSV 是文件无法查询，SQLite 支持查询层降级读取（如盘后 CH 挂了但策略层要读最近 tick），是 TSV 兜底的查询层补充。

### 7.8 主动 WAL 写入器 wal_writer（P0-1 Phase A）

**真源**：`src/zephyr/data/wal_writer.py`（MOD-GOV-wal_writer）。**职责**：数据先落本地 WAL 段文件，再由后台 drain 线程异步排空到 ClickHouse——解决实时 tick 写入路径在 CH 慢/不可达时延迟突增的问题，被 §6.6 tick_subscriber 使用。

**与 BufferedWriter 的区别**（关键）：
| 维度 | BufferedWriter | WalWriter |
|---|---|---|
| 路径 | 攒批 → 直接写 CH（失败才降级 local_fallback） | 攒批 → **主动写 local_fallback 段文件** → drain 线程异步回灌 CH |
| 延迟 | 依赖 CH 写入速度 | 本地落盘快，写入路径延迟稳定 |
| CH 慢/不可达 | 阻塞生产者 | 不阻塞生产者（CH 慢只影响 drain 速度） |

**段文件落盘阈值**：每段 ≥ 3000 行或 ≥ 5 秒触发（P0-3 调参：5000→3000 / 10.0→5.0）。**WAL 容量背压**：目录上限 2GB——70% warning，**90% critical 背压阻断写入**（`add()` 返回 False，生产者应减速/中断），防 CH 长时间不可达撑爆磁盘。**drain 线程**：轮询积压段文件回灌 CH，失败指数退避（封顶 60s）不退出；无积压 2s 慢轮询，有积压 0.5s 快速重试。

**复用机制**：`local_replay.save_fallback()`（段落盘）/ `local_replay.replay_batch()`（drain 回灌）/ `ch_writer._get_table_columns_set()`（列过滤）/ `ch_writer.tsv_escape()`（TSV 序列化）；**P1-5 metrics**：segments / wal_dir_bytes / backlog_files / drain_replayed / drain_failed。**why 主动 WAL 而非失败才降级**：tick 是实时推送，CH 写入延迟突增会阻塞 QMT callback 线程丢 tick——主动 WAL 把"写 CH"与"接收 tick"解耦（接收即落盘快，CH 写入异步 drain）。

### 7.9 WAL 编解码注册表 wal_codec/codec_registry

**真源**：`src/zephyr/data/wal_codec/codec_registry.py` + `wal_codec/tsv_codec.py`。**职责**：按 magic number（4 字节前缀）路由到对应编解码器，drain 线程根据段文件 magic 自动选择解码器。

**codec 清单**：`TsvCodec`（MAGIC=b"" 无前缀，纯文本段默认 TSV——当前唯一实现）；`_ProtoCodecStub`（MAGIC=b"PB\x01"，P3 远期桩，当前 encode/decode 降级 TSV 并 log warning）。**CodecProtocol**：`MAGIC: bytes` + `encode(rows)` + `decode(data)`；**get_codec(data)** 按 magic 前缀匹配，无匹配降级 TSV（向后兼容）。**why magic number 路由而非文件扩展名**：段文件名是时间戳+哈希无扩展名信息，magic 前缀自描述编码格式。**why TSV 当前唯一 codec**：TSV 人类可读 + CH 原生支持导入 + 序列化简单，Proto 是 P3 远期优化。

### 7.10 统一数据库连接管理 database_service（跨域引用）

**真源**：`src/zephyr/infrastructure/database_service.py`（MOD-INF-002，D_INFRA_RUNTIME 域，stable）。**职责**：统一管理 governance.db / depgraph(PostgreSQL) / ClickHouse(c1_market) / Redis(H1) 的连接池、生命周期、健康检查，数据下载层经本服务获取 CH/Redis 连接。

**部署现状**：ClickHouse c1_market 2026-07-01 部署（INFRA-DB-006，`get_clickhouse_conn()` 已实现）；Redis H1 热缓存 2026-08-02 部署（Redis 7.0.15 @ Hyper-V Ubuntu VM 172.24.30.100:6379，与 CH 同 VM，D1 决策，`get_redis_conn()` 已实现）；market.duckdb（旧 DuckDB 业务时序库）2026-07-05 删除（已迁移至 c1_market）。**why 跨域引用**：CH/Redis 连接是基础设施资源多域共用，统一管理避免多处各自维护连接池（连接泄漏/配置漂移）；分工——`ch_config.py`（§7.6.1）管连接配置单真源，`database_service` 管连接池生命周期。

### 7.11 Tick Redis 热缓存双写 tick_redis_cache（H1 CP-01）

**真源**：`src/zephyr/data/tick_redis_cache.py`（MOD-H1_REDIS_HOT，D_INFRA_RUNTIME 域）。**职责**：tick → Redis `tick:{symbol}:latest` 双写器（D-DATA → H1 集成适配器）；tick_subscriber._drain_batch 批量出队时将 QMT tick dict 转 Redis Hash 格式，PIPELINE 批量写入。

**与 WAL 路径的关系**：双写——WAL→ClickHouse 是持久化主路径，Redis 是热读取加速层；Redis 故障 best-effort 降级（log+返回 0），不阻断 WAL 主路径（CP-02 降级：信号端用上一批因子值）。**性能**：PIPELINE 500 条单次 RTT 批量 HSET；每 drain_batch 一次（~500 条/批，3 秒周期）；延迟 <10ms（CP-01 SLO：Tick→Redis ≤3 秒）；**Hash 字段** 5 档 bid/ask + price/volume/amount/timestamp = 23 字段（`_MAX_LEVELS=5`）。

**why 双写 Redis 而非只写 CH**：盘中策略读 tick 需低延迟（<3ms），CH 查询 ~50ms 无法满足，Redis 内存读取 <1ms——CH 持久化（回测/盘后分析），Redis 盘中热读，职责互补；**best-effort 不阻断 WAL**——Redis 是加速层，挂了只是盘中读不到最新 tick（降级用上一批），tick 数据不能丢（WAL 保持久化）。

## 8. 数据质量与完整性

### 8.1 质量门控（quality_gate.py）

**真源**：`src/zephyr/data/quality_gate.py` 是 **re-export wrapper**——`QualityReport` / `MarketDataValidator` / `apply_quality_gate` 真源在 `zephyr.gov_enforcement.rule_enforcement.quality_gate`（SSoT: `cross_layer_contracts.yaml` → CTR-ERR-001 DataQualityError）。**why re-export**：测试通过 `zephyr.data.quality_gate` 导入，但真源在 gov_enforcement 域（质量门禁是跨层契约非数据下载层私有）——re-export 消除 ModuleNotFoundError 同时保持 SSoT，治理域定义规则，数据域 re-export 供消费方就近导入。

**职责边界**：quality_gate 与下载调度解耦——Provider 只拉数据，质量校验由消费方在读取时调用（不在写入时拦截）。**why**：写入时拦截拖慢下载吞吐（5204 只股票逐个校验），且脏数据流入比断档危害小（脏数据可事后清洗，断档无法回填）。

### 8.2 完整性巡检（integrity_checker.py · L11）

**流程**（`run_daily_check()`）：复用 `backfill_checker._discover_backfill_tables()` 动态发现全表 → 逐表检查当天 `count() WHERE date_col = today()` 是否 ≥ 阈值 → 不达标经 `alerter.notify()` 告警 → 结果记录 progress_store。**阈值设计**：过去7天平均行数×0.5（低于均值50%视为缺失）；无历史数据返回0（跳过巡检，新表首日不报缺失）。**why 历史7天日均×0.5 而非固定值**：不同表行数量级差异大（tick_data 2000万 vs macro_data 几十行），固定阈值无法通用。

### 8.3 回补检查（backfill_checker.py · L10）

**动态发现机制**（`_discover_backfill_tables()`）：从 tasks.yaml 动态读取所有非 disabled 任务的表，同表多任务去重；自动推断日期列名（`DESCRIBE TABLE` 查 Date 类型列，优先 trade_date/end_date/report_date/unlock_date/announce_date）与阈值（过去7天平均行数×0.5）。

**补下载执行**（`run_weekend_backfill()`）：动态发现所有表 → 获取过去7天交易日 → 逐表检测缺失日期 → tick_data 用专门 `backfill_tick_data()`（分时段+批量写入）→ 其他表用 `scheduler.run_task(task_id)` 重跑。

### 8.4 跨源验证（cross_source_validator.py）

**实际范围**（2026-08-12 代码实证）：**tick 数据专属**的主备源内容级校验器（P1-4），非通用跨源框架——硬编码校验 `tick_data` 表 `data_source IN ('miniqmt','tdx_backup')` 最近 N 分钟（默认 5）数据，按 symbol 比对主备源最新 price（阈值 0.1% 判 fail）/volume（5% 判 warn）及缺失标的，结果写 `c1_market.cross_validation_log` 表。

**why tick 专属**：服务于 §9.2 冗余源热切换的正确性验证——QMT 主源中断切 TDX 备源时，需确认两源 tick 内容一致（价格偏差在容差内），否则备源数据污染 tick_data。离线任务跨源对比（如 miniqmt vs baostock 日K）当前**未实现**——v1.4.0 已裁定暂缓（§16.3 Q24）。

### 8.5 数据源健康检查（source_health_check.py）

**实际机制**（2026-08-12 代码实证）：启动时对 11 个源（tushare/akshare/baostock/ifind/miniqmt/tdx/tickflow/rss/cls/eastmoney_news/tqcenter）做 env 检查→import→connect→**真实 API 探针**（miniqmt 用 `get_stock_list_in_sector` 探活、tdx 拉 600000 一日线），状态分级 healthy / connect_only / empty_data / test_fail / env_missing；结果写 `logs/source_health_YYYYMMDD.log` + 内存快照供 scheduler `get_source_health()` 查询。

**边界**：**不读 fetch_perf、不做 api_status 自动退化决策**——INVARIANTS 明确"异常源不自动禁用（人工决策）"；fetch_perf 的 api_status 语义仅存在于 §10.4 speed_tester 主动测速结果中，两者是独立的健康信号通道。

### 8.6 PIT 查询（pit_query.py · #ARCH-CH-021 P0-5）

**真源**：`src/zephyr/data/pit_query.py`。**问题**：c3 财务报表用 ReplacingMergeTree 覆盖式更新，存在前视偏差风险——同一 report_period 可能有原始公告 + 修正公告多个版本，回测必须只看"当时已公告"的数据（15 号 §3.3 PIT 铁律）。

**方案**：按 announce_date 建立 point-in-time 查询能力，与 backtest 域 pit_manager.py 三公理对齐：

| 数据层 pit_query | 回测层 pit_manager | 语义 |
|---|---|---|
| `as_of()` | `as_of_join()` | 版本对齐：取查询时点可见最新版本 |
| `embargo` 选项 | `apply_embargo()` | 泄漏防护：announce_date 截止回退 |
| `survivorship_universe()` | `check_survivorship_bias()` | 幸存者偏差：PIT 标的池 |

**底层机制**：财务表 ORDER BY (symbol, report_period, announce_date) 保留全部版本（ReplacingMergeTree 按 sort key 去重，announce_date 不同则不合并），故 `LIMIT 1 BY symbol, report_period`（ORDER BY announce_date DESC）可取查询时点已公告的最新版本——正是 AS OF JOIN 语义。**约束**：仅查白名单财务表，非白名单抛 PITQueryError；CH 查询失败返回空字符串（同 ch_reader）；表无 period_col 跳过 LIMIT 1 BY。

**why PIT 查询在数据下载层而非回测层**：PIT 查询能力依赖下载层的表结构设计（ORDER BY 含 announce_date 保留多版本），是下载层与回测层的契约边界。

### 8.7 已知数据缺口注册表 known_data_gaps.yaml（#ARCH-CH-029）

**真源**：`src/zephyr/data/config/known_data_gaps.yaml`（MOD-GOV_BACKFILL_CHECKER，audit 2.7/3.8 治本，2026-07-23）

**问题**：§8.3 backfill_checker 默认回看 7 天（`_DEFAULT_BACKFILL_DAYS=7`），无法检测超过 7 天的历史缺口——若某表 2 周前断档，缺口永久遗留。**方案**：本注册表登记已知历史缺口，backfill_checker 读取后对已登记缺口使用**全范围回看**（不受 7 天窗口限制）；已登记缺口 backfill 完成后标记 `status=completed` 不再重复检测。

**缺口类型**（2026-08-12 实际注册表全量，6 种）：`date_range`（特定日期范围内行数低于阈值，如 tick_data 2026-06 缺口）/ `empty_table`（整表为空，如 edb_data iFind 配额耗尽）/ `source_stale`（数据源停滞，如 share_change akshare 默认 end_date 硬编码事故，已修复）/ `source_discontinued`（数据源永久停止，如 hk_connect_flow 港交所 2024-08-16 停发）/ `no_data_source`（无可用批量接口，如 audit_opinion/rights_issue）/ `permission_required`（需付费权限，如 l2_tick L2 行情）

**已登记缺口**（7 条，2026-08-12 实测——v1.2.1 仅列 2026-07-23 首批 2 条，2026-07-24 增补 5 条）：

| id | table | gap_type | 缺口描述 | 状态 |
|---|---|---|---|---|
| `tick_data_2026_06_gap` | c1_market.tick_data | date_range | 2026-06 录制器中断，6月日均 248万行 vs 5月基准 2385万行（89.6% 缺失） | registered |
| `edb_data_ifind_quota_exhausted` | c1_market.edb_data | empty_table | iFind EDB 配额耗尽，表至今 0 行；macro_data(akshare) 作主宏观源 | accepted |
| `share_change_cninfo_stale` | c3_fundamental.share_change | source_stale | akshare stock_share_change_cninfo 默认 end_date='20241021' 硬编码，provider 未传日期范围 | resolved（provider 已修，待宽日期 backfill） |
| `hk_connect_flow_source_discontinued` | c1_market.hk_connect_flow | source_discontinued | 港交所 2024-08-16 停发北向日频明细，数据永远停在 2024-08-16 | accepted（无替代源，19 号季度快照方案） |
| `audit_opinion_no_interface` | c3_fundamental.audit_opinion | no_data_source | AKShare 无批量审计意见接口，逐股效率过低，任务 disabled | accepted |
| `rights_issue_interface_removed` | c3_fundamental.rights_issue | no_data_source | akshare 1.18+ 移除批量接口，仅剩逐股接口，任务 disabled | accepted |
| `l2_tick_permission_required` | c1_market.l2_tick | permission_required | 需付费 L2 权限（#ARCH-DATA-014），fallback 降级五档快照入 tick_data | accepted（tick_data 替代运行中） |

**状态机**：`registered` → `in_progress` → `completed`；另有两终态——`accepted`（缺口已接受，有替代源或永久不可补）/ `resolved`（根因已修复，待回填收尾）。**触发方式**：`backfill_checker.run_known_gap_backfill()` 读取本注册表，对 status=registered 的缺口触发 QMT 历史数据下载（tick_data）或等待 iFind 配额恢复（edb_data）。

**why 显式登记而非扩大默认窗口**：扩大默认窗口到 30/90 天会让每日 backfill 检查成本暴增（全表扫描 90 天）；显式登记只对已知缺口全范围检测，日常增量检测保持 7 天窗口低成本——"日常增量检测"与"已知历史缺口修复"的分工。

## 9. 数据韧性与容灾

### 9.1 数据源 fallback（§1 三层机制）

**tasks.yaml 配置**：
```yaml
- task_id: daily_valuation_incremental
  source: akshare          # 主源（#ARCH-IFIND-FAILOVER 降级后）
  fallback_sources:        # 副源列表
    - source: ifind        # 续费后可恢复为主源
      capability: daily_valuation
    - source: akshare
      capability: daily_valuation
```

**run_task fallback 逻辑**：①构造尝试列表 `sources_to_try = [(主源, capability)] + [(副源, capability), ...]`；②逐源调 `_try_source()`；③**不可恢复错误**（-4318/-4309/配额/接口废弃/认证失败/401/403/license）→ 立即 fallback（跳过重试）；④**可恢复错误**（Timeout/ConnectionError/RemoteDisconnected/HTTPError/503/502）→ PolicyRegistry 重试用完后 fallback；⑤任一源成功即返回 True，全部失败返回 False。

**覆盖率实证**（2026-08-12 tasks.yaml 全量统计）：154 任务中 105 个配置了非空 fallback_sources（68.2%）；49 个无 fallback（含全部 miniqmt 分钟K线 15 个、tqcenter 4 个、tdx 板块分钟K 5 个、生猪 5 个、fred/eia/qweather 显式空列表注明无国内副源等），符合"天然无副源"设计。

**死 fallback 警告**（2026-08-12 实证）：fallback_sources 中 35 处引用**无 Provider 实现的 source**（qmt/exchange/bdpan/local_valuation，create_provider 14 分支均不含）——主源失败轮到这些 fallback 会落入"未知数据源"分支返回 None 直接失败，实际不提供韧性。裁定见 §16.2 Q14（清理 28 处 + 保留 local_valuation 1 处待补实现，逐源计数真源在 Q14）。

### 9.2 冗余源热切换（redundant_source/，MOD-L00-005/007，P2-8）

**真源**：`src/zephyr/data/redundant_source/` + `docs/03_modules/_domain_data/redundant_source_blueprint.md`

**不变式**：主源中断 >10s 切换备源；CH 不可达 >30s 降级 SQLite；CH 恢复后自动回灌；全程 metrics 暴露。

**架构**（P1-3 双源冗余 + P2-8 热切换）：
```
QMT (push) ──→ _on_tick ──→ queue ──→ _drain_batch ──→ WalWriter ──→ CH
                  ↑                                  ↓ (CH 不可达)
HeartbeatMonitor ─┤                              SQLiteFallback
  (主源 tick +     │                                  ↑
   CH ping)        ↓                                  │ RecoveryManager
              SourceSwitcher ──切换──→ TDX (poll) ────┘ (CH 恢复后回灌)
              (PRIMARY→BACKUP→PRIMARY)
```

**4 个组件协作**：

| 组件 | 文件 | 职责 | 关键参数 |
|---|---|---|---|
| **HeartbeatMonitor** | heartbeat_monitor.py | 监测主源 tick 推送（`record_tick()` 记录最后 tick 时间）+ CH 连通性（每 N 秒 `SELECT 1`，连续 3 次失败标记不可达）；通过 metrics 暴露 Gauge | tick 中断阈值 10s / CH ping 间隔 10s / CH 失败阈值 3 次 |
| **SourceSwitcher** | source_switcher.py | 数据源切换状态机 PRIMARY→BACKUP→PRIMARY；SourceProvider 抽象接口（主源 QMT + 备源 TDX 均实现）；**防抖**：主源恢复后等 30s 稳定期再切回 | 切换检查间隔 5s / 恢复稳定期 30s |
| **BackupTickPoller** | backup_tick_poller.py (MOD-L00-007) | 备源 TDX 轮询器——主源中断时定期拉取 TDX 实时快照（`fetch_tick_snapshot`），转换为 QMT tick dict 喂入 TickSubscriber 队列；QMTSourceAdapter 是 QMT 主源被动适配器（stop=no-op 保持订阅用于恢复检测） | 轮询间隔 3s |
| **RecoveryManager** | recovery.py | CH 恢复后 SQLite→CH 回灌管理器——监听 HeartbeatMonitor 的 CH 状态变化，CH 恢复后按 batch(1000行) 从 SQLiteFallback 读取回灌 CH，成功删除 SQLite 批次，失败指数退避(2s→4s→...→60s) | 检测间隔 10s / batch 1000 / 退避 2-60s |

**SourceState 状态枚举**：ALIVE / DEAD / UNKNOWN。**HeartbeatStatus 快照**：primary_state + ch_state + last_tick_ts + last_ch_ok_ts + ch_consecutive_failures。

**why**：防抖 30s 稳定期——主源可能短暂恢复又中断（网络抖动），立即切回导致主备 ping-pong，30s 确认真恢复再切回；QMTSourceAdapter.stop()=no-op——QMT 订阅由 TickSubscriber.start() 管理，切备源时不能停 QMT 订阅，保持订阅活跃才能让 HeartbeatMonitor 检测主源恢复触发切回；SQLite 仅写最近 N 小时——SQLite 是兜底不是持久化（持久化由 WAL+local_replay 负责），每表 500K 行（约 4 小时 tick）FIFO 清理，旧数据由 WAL 段文件保留。**与 §9.1 fallback 的区别**：§9.1 是**任务级**主源→副源切换（scheduler.run_task 内，针对 154 个离线任务）；§9.2 是**进程级**主源→备源热切换（tick_subscriber 内，针对实时 tick 推送，零中断切换）。

### 9.3 WAL 编解码（wal_codec/ + wal_writer.py）

**真源**：`docs/03_modules/_domain_data/wal_codec_blueprint.md`；详细机制见 §7.8（wal_writer 主动 WAL）+ §7.9（wal_codec 编解码注册表）。用于 CH 写入失败/慢时的兜底，与 §9.2 SQLiteFallback 互补——WAL 保 tick 持久化，SQLite 保查询层可读。

### 9.4 新增表门禁（DATA-TASK-COMPLETENESS）

**文件**：`gov_enforcement/commit_gates/data_task_completeness_gate.py`（warn 级，priority=80）。**检测逻辑**：只在 tasks.yaml 被修改时触发 → `git diff HEAD -- tasks.yaml` 提取新增 task_id → 检查新增任务是否配置 fallback_sources → 未配置 → warn（不阻断）+ detail 含 WARN 信息。**why warn 不阻断**：有些表确实无副源（tick_data 只有 miniqmt），硬阻断阻碍开发；warn 出现在 commit 输出形成"AI 增加表 → 门禁提醒 → AI 补充 fallback_sources"闭环。

## 10. 运维与监控

### 10.1 进度与断点续传（progress_store.py）

**统一进度存储**（SQLite `data/integrator_progress.db`）：`task_progress`（task_id/source/last_run_at/last_key/last_status/rows_total/error_msg）+ `task_runs`（run_id/task_id/started_at/finished_at/status/rows_fetched/rows_written/error_msg）。

**断点续传协议**：任务启动 → 查 `task_progress.last_key` 作为本次 `payload.start` → 分批拉取每批写完 CH 更新 `last_key` → 异常中断下次从 `last_key` 继续 → 幂等（ReplacingMergeTree 直接 INSERT 或 MergeTree 写前 DELETE）。**why SQLite 存进度而非 ClickHouse**：进度查询高频但量小，SQLite 单文件部署简单。

### 10.2 告警（alerter.py）

**通道**：日志（所有事件，结构化 `[time][level][task_id][source] message`）/ 失败汇总文件（DEAD 任务，`failures/YYYY-MM-DD.log`）/ 钉钉 Webhook（可选，DEAD 任务+配额告警，Markdown 卡片）/ 邮件（可选，连续 3 天失败汇总）。

### 10.3 指标（metrics.py）

Prometheus 文本格式 `data/metrics.prom`，可接 Grafana：`integrator_task_total{task, status}` Counter / `integrator_task_duration_seconds{task}` Histogram / `integrator_rows_fetched_total{task}` Counter / `integrator_rate_limit_hits_total{source}` Counter / `integrator_retry_total{source}` Counter / `integrator_session_uptime_seconds{source}` Gauge。

### 10.4 Capability 实测性能（c0_meta.fetch_perf）

**设计动机**：不同 source.capability 下载速度差异巨大（实测从 5066 行/秒到 0.09 只/秒，跨度 5 万倍），仅靠 policy_registry 的预期 RPM 无法反映实际运行情况。**2026-07-09 首批实测数据**（14 条）：miniqmt.kline_daily ok 14.5 行/s / miniqmt.adj_factor **slow** 0.09只/s（get_divid_factors 每只11秒，全量16h）/ akshare.daily_valuation **rate_limited** 0.17只/s（百度API空响应率15%）/ akshare.margin_trading ok 5066 行/s / akshare.money_flow **blocked**（东财反爬封锁，已回退 ifind→akshare）/ akshare.equity_pledge **broken**（API 损坏，已回退 ifind）。

**派生用法**：调度优先级排序参考（ok 优先，slow/rate_limited 安排低峰）/ 退化决策**人工参考**（blocked/broken 由人裁定回退——代码实证：无任何模块自动消费 fetch_perf 做回退）/ 运维告警（error_rate>0.1）/ 容量规划（rows_per_sec×目标行数估耗时）。

**数据来源**：fetch_perf 由 **speed_tester.py 主动测速**单一通道写入（2026-08-12 代码实证：scheduler.py 零引用 fetch_perf，无"运行时被动记录"）——对每个 capability×每个可用 source 做小样本测速，记录 rows/sec/symbols/sec/错误率写入 c0_meta.fetch_perf。CLI：`integrator speed-test [--source <src>] [--capability <cap>]`，只读测速不写业务表。

**why 单通道的隐患**：测速是抽样（某时点的小样本），日常运行的真实退化（如 akshare 某接口突然 blocked）只能靠 L11 巡检行数下降或任务失败告警间接发现。被动运行时记录（scheduler 每次任务结束写一条 fetch_perf）——**v1.4.0 已裁定施工 P2**（§16.2 Q16，登记 CAND 候选库）。

### 10.5 开机自启架构（单一真源）

**真源**：[boot_autostart_architecture.md](../../../03_modules/_domain_data/boot_autostart_architecture.md)（MOD-L00-004 §1-§5，v1.0.0，2026-08-07 更新）

**第一性原理**（AGENTS.md 硬约束：永久系统必须全自动——自动触发/运行/维护/关闭，禁止需手工干预的设计）：ZephyrAlpha 永久服务必须开机自启 + 崩溃自愈，通过 **Windows Task Scheduler 单一权威入口** 实现。

**7 项第一性原理约束**：

| # | 约束 | 机制 |
|---|---|---|
| C1 | 可用性（自启+自愈） | Task Scheduler AtLogOn + PT5M 心跳 + guard while-true |
| C2 | 正确性（无重复业务进程） | pid file lock + orphan cleanup + finally-kill |
| C3 | 单一真源（唯一入口） | Task Scheduler 是唯一入口；无 .bat/.lnk/registry |
| C4 | 静默运行（无 UI 噪音） | `-WindowStyle Hidden`，无控制台闪窗 |
| C5 | 资源效率（无冗余触发器） | legacy Startup 条目已清除（2026-07-27） |
| C6 | 可观测性（故障可溯） | guard 日志写 `tmp/*_guard.log` |
| C7 | AI 可维护性（声明式幂等） | register_*.ps1 脚本，Set-ScheduledTask in-place 更新 |

**5 个 Task Scheduler 任务**（单一入口，无 Startup 文件夹/注册表 Run；部署脚本见 §10.12，AI 会话手动启动用 `schtasks /run /tn ZephyrAlpha_DataScheduler`，禁止 IDE 终端 Start-Process——进程会随终端死）：

| 任务名 | 触发 | 脚本 | 守护对象 |
|---|---|---|---|
| `ZephyrAlpha_DataScheduler` | AtLogOn + PT5M 心跳 | scripts/start_scheduler.ps1 | 数据集成器调度器（zephyr.data.scheduler） |
| `ZephyrAlpha_TickSubscriber` | AtLogOn + PT5M 心跳 | scripts/start_tick_subscriber.ps1 | Tick 订阅器（zephyr.data.tick_subscriber） |
| `ZephyrAlpha_RSSHub` | AtLogOn | `pm2 resurrect`（hidden） | RSSHub 服务（rss_provider 依赖） |
| `ZephyrAlpha_TraeCacheCleanup` | AtLogOn + PT30S delay | clean_trae_cache.ps1 | Trae 缓存清理 |
| `ZephyrAlpha_DeadmanSwitch` | PT5M | scripts/deadman_switch.ps1 | 死人开关告警（§10.7） |

**legacy 清除**（2026-07-27）：移除 Startup 文件夹 `ZephyrAlpha_DataScheduler.lnk` + `start_zephyr_scheduler.bat`（冗余+闪窗+双重启动 tick_subscriber）；`start_rsshub.bat` / `CleanTraeCache.bat` 迁移到 Task Scheduler；备份在 `tmp/startup_backup_20260727/`。

> **project_memory 硬约束（防闪窗双机制）**：①Task Scheduler watchdog 任务禁止直接用 powershell.exe 启动（控制台子系统程序会闪窗），改用 wscript.exe + scripts/launch_hidden.vbs；②运行中的 .py 脚本启动子进程须用 run_subprocess_hidden()/spawn_python_hidden()（CREATE_NO_WINDOW），禁止裸 subprocess.run。

### 10.6 四层防御 Watchdog（#ARCH-BOOT-001，resolved 2026-08-07）

**真源**：[boot_autostart_architecture.md](../../../03_modules/_domain_data/boot_autostart_architecture.md) §3 + §8

**架构**：
```
Task Scheduler (OS-hosted, MultipleInstances=Parallel, survives user-mode kills)
  -> guard script (while-true, single-instance lock + heartbeat => idempotent re-entry / zombie takeover)
    -> python business process (zephyr.data.scheduler / zephyr.data.tick_subscriber / ch_health_probe.py)
```

**四层防御**：

| 层 | 机制 | 治本要点 |
|---|---|---|
| **1. OS 层** | Task Scheduler AtLogOn + PT5M repeat | **`MultipleInstances=Parallel`**（Phase 1 治本）：Task Scheduler 是 DUMB 周期启动器，不参与单实例决策。IgnoreNew 会阻断新 guard（僵尸 guard 占位时心跳接管成死代码）；Parallel 让 5min re-fire 总能启动新 powershell，新 guard 要么 exit（"已在运行，心跳新鲜"）要么接管（"心跳陈旧"） |
| **2. Guard 层** | `while($true)` 自动重启 python 子进程 | 运行<10s 视为启动失败（依赖未就绪/miniQMT 未起），等 30s 重试。子进程监控**轮询 `$proc.HasExited`**（Phase 2 治本）而非阻塞 `WaitForExit`——后者在 Windows 进程退出路径上死锁主线程（僵尸根因：PowerShell 重定向输出管道满致 WaitForExit 不返回） |
| **3. 单实例层**（SSoT） | pid file lock（`tmp/scheduler.lock` 等） | 唯一单实例执行者。Stale lock（pid 已死）触发 orphan cleanup：杀来自死 guard 的任何业务 python（不变式：无 guard => 无业务进程）。`finally` 块在 guard 退出时杀子进程 |
| **4. 心跳健康层**（Phase 2 治本） | guard 每 15s 写 `tmp/{scheduler,tick_subscriber,ch_health_probe}.heartbeat` | 格式 `ISO8601|guard_pid|child_pid`。新 guard 接管逻辑：PID 活**且**心跳<5min 新鲜 → "已在运行, exit"；PID 活但心跳 stale/missing → 僵尸 → `Stop-Process` 僵尸 guard + 清 lock/heartbeat + 落入 orphan cleanup。这是僵尸 guard（层 2 失效）的恢复路径 |

**历史事故**（2026-08-07 立项根因）：scheduler/tick_subscriber 主进程死亡、guard 僵尸化导致 intraday 下载停滞 2 交易日（kline_1min 停在 08-05 15:00、tick_data 停在 08-04）。根因：`WaitForExit()` 纯阻塞等待在某些 Windows 进程退出场景不返回，guard 主线程卡死（CPU=0），子进程已死但 guard 不重启；单实例锁只验 PID 存活不验健康度，Task Scheduler 每 5min 拉新 guard 被僵尸 PID 挡住形成死锁。**端到端验证**（2026-08-07 16:00-16:03 全绿）：三服务（scheduler/tick_subscriber/ch_health_probe）僵尸接管 ✅、心跳每 15s 更新 ✅、子进程崩溃→guard 重启 ✅、旧僵尸全死+每服务 1 实例无重复 ✅。

### 10.7 死人开关告警（#ARCH-BOOT-002，战略补强 E，2026-08-08 落地）

**问题**：四层防御主治本（Phase 1-5）已闭合僵尸接管闭环，但"全层失效无人知"循环未闭合——2026-08-07 的 2 日停摆是**人工发现**的，非系统告警。

**方案**：`scripts/deadman_switch.ps1`——**无状态一次性 Task Scheduler 任务**（非 while-true guard，无僵尸风险），每 5min fire 读 3 个心跳文件（scheduler/tick_subscriber/ch_health_probe），任一陈旧 >10min 即告警。**独立性第一性原理**：监控者不属被监控的 3 服务之一，只读心跳文件——3 服务全死此任务仍独立 fire 并告警。**为何 .ps1 而非 .py**：若故障根因是 Python 栈崩溃（坏 import/venv），.py 监控会跟着死；.ps1 读文件+发 webhook 零 Python 依赖。

**告警通道**：飞书 webhook（推手机，复用 `ZEPHYR_FEISHU_WEBHOOK`，与 Alerter 同契约）/ Windows Event Log / 本地 `tmp/deadman_switch_alerts.log`（全审计无冷却）/ **30min 冷却**防多小时停摆刷屏（同一 staleKey 30min 内只推一次手机）。**Fail-safe**：此任务自身死亡退化到 pre-E 现状（无监控），非倒退——无需无限递归监控。

**配套战略补强**（#ARCH-BOOT-002 另两项）：**D. 心跳原子写** ✅——`Out-File` 截断+写非原子，新 guard 轮询期撞上旧 guard 写心跳微秒窗口可能读到半写→误判 stale→假接管，3 个 guard 脚本 `Write-Heartbeat` 改为写 `$HeartbeatFile.tmp` + `Move-Item -Force`（同卷原子 rename）；**F. WaitForExit 死锁根因文档化** ✅——3 个 guard 脚本头注释固化"pipe buffer fills → WaitForExit never returns → main thread deadlocks"知识点，防 AI "优化"回 `WaitForExit`。

### 10.8 系统级健康监控

#### 10.8.1 健康聚合器 HealthAggregator（MOD-INF-015）

**真源**：`src/zephyr/infrastructure/system_telemetry/health_aggregator.py`。**职责**：每 15s 轮询 12 系统三态探针（liveness 进程是否活着 / readiness 是否就绪可服务 / degraded 是否降级运行）→ 生成健康面板快照 → 年度审计。快照最多保留 1440 个（15s × 1440 = 6 小时滚动窗口）超出 FIFO；事件驱动订阅 event_bus 的 `kill_switch_triggered` / `pipeline_failed`，触发时立即采集快照，degraded 系统数 > 0 则告警；年度健康报告三指标 uptime_ratio / mttr_s / degradation_ratio 按系统分项。

#### 10.8.2 ClickHouse 健康探针 ch_health_probe

**真源**：`scripts/start_ch_health_probe.ps1` + ch_health_probe.py。**职责**：3s 探测 ClickHouse TCP+HTTP 双通连，心跳写入 `tmp/ch_health_probe.heartbeat`；**纳入四层防御**（#ARCH-BOOT-001 Phase 2）与 scheduler/tick_subscriber 同等纳入心跳僵尸接管机制。**why 独立探针**：CH 是数据落库终点，CH 不可用则所有下载白费——避免"scheduler 活着但 CH 死了"的盲区。

#### 10.8.3 数据源健康检查 source_health_check（§8.5 已述）

定期检查数据源状态（health_check 探活），结合 fetch_perf 的 api_status（ok/slow/rate_limited/blocked/broken/pending）做退化决策。

#### 10.8.4 三冗余 Watchdog（MOD-INF-015）

**真源**：`src/zephyr/infrastructure/system_telemetry/watchdog.py`。**职责**：三冗余互检 + Panic Mode + Dead Man's Switch（CT-WATCHDOG-001）。**机制**：心跳写外部文件 `data/telemetry/.watchdog_heartbeat_{id}`（原子写 tmp + replace）；`check_peers()`——peer 心跳超 1800s（30min）视为 missing，2+ peer missing 触发 `panic_mode=True`；`should_alert_dead_mans_switch()`——超 1800s 触发死人开关告警。**两种运行模式**：库模式（`Watchdog(watchdog_id="wd-1")` 嵌入其他进程）/ 独立进程（`python -m zephyr.infrastructure.system_telemetry.watchdog --id wd-1 --interval 10`）。**why 三冗余互检而非单点**：单点 watchdog 自身死亡无人知；三冗余 2+ peer missing 才 panic 避免单点误报，任一 peer 死亡可被其他 peer 发现。

### 10.9 不变式测试防回退

**真源**：`tests/scripts/test_guard_invariants.py` + `tests/scripts/test_guard_watchdog.py`。**设计动机**（#ARCH-CH-004）：100% AI 开发模式下，AI 可能"优化"回 `WaitForExit` 或改回 `IgnoreNew`，导致治本成果被回退——用不变式测试钉死治本决策为可执行不变式，AI 任何回退都会触发测试失败。

**不变式覆盖**：

| 测试类 | 钉死的不变式 | 防的回退 |
|---|---|---|
| `TestNoGuardUsesWaitForExit` | 3 脚本禁用 `$proc.WaitForExit()`，必须轮询 HasExited | AI "优化"回 WaitForExit（僵尸根因） |
| `TestRegisterGuardUsesParallel` | register_guard_tasks.ps1 必须 Parallel | AI 改回 IgnoreNew（阻断心跳接管） |
| `TestRegisterAuxKeepsIgnoreNew` | register_aux_tasks.ps1 保持 IgnoreNew | 文档化有意非对称：一次性 AtLogOn 任务无僵尸风险 |
| `TestGuardsDefineHeartbeat` | 3 脚本均定义 $HeartbeatFile + Write-Heartbeat + 5min 阈值 + finally 清理 | AI 删心跳逻辑 |
| `TestAtomicHeartbeatWrite` | 心跳写用 tmp + Move-Item -Force（原子） | AI 改回 Out-File（半写误判风险） |
| `TestDeadmanSwitchInvariants` | deadman_switch 一次性、无 WaitForExit、读 3 心跳、有冷却、有 webhook | AI 改成 while-true guard（引入僵尸风险） |
| `TestDeadmanSwitchRegistered` | deadman_switch 已注册为 Task Scheduler 任务 | AI 漏注册 |
| `TestWaitForExitRootCauseDocumented` | 3 guard 脚本头注释含死锁根因知识点 | AI 删注释 |

### 10.10 CLI（cli.py）

**真源**：`src/zephyr/data/cli.py` + `__main__.py`（`python -m zephyr.data` 等价于 `integrator` 命令）。**包入口 get_integrator()**（`__init__.py`）：调度器单例工厂，首次调用创建 IntegratorScheduler 实例并 `_load_config()` 加载配置，后续返回同一实例——CLI 和外部消费者应通过此函数获取调度器。

```bash
integrator status                 # 查看所有任务今日状态
integrator status <task_id>       # 查看单任务详情
integrator list --source ifind    # 列出某源所有任务
integrator run <task_id>          # 手动触发单任务（绕过交易日守卫）
integrator rerun-failed           # 重跑今日所有 DEAD 任务
integrator pause <source>         # 紧急熔断某源
integrator resume <source>        # 恢复
integrator speed-test [--source <src>] [--capability <cap>]  # 主动测速（§10.4）
```

### 10.11 无闪窗启动器 launch_hidden.vbs

**真源**：`scripts/launch_hidden.vbs`。**病根**：`powershell.exe` 是**控制台子系统程序**，Task Scheduler 以 Interactive 拉起它会瞬间分配控制台窗口；`-WindowStyle Hidden` 只能在主窗口创建后再隐藏，来不及阻止闪现——3 个 watchdog 任务每 5min 触发 → 每 5min 闪 3 次窗口。**原理**：`wscript.exe` 是 **GUI 子系统程序**不创建控制台窗口，`WScript.Shell.Run cmd, 0`（SW_HIDE）启动目标 powershell 时控制台被隐藏创建，从根本上消除闪窗。

**用法**（Task Scheduler Action）：`Execute: wscript.exe` / `Arguments: "D:\ZephyrAlpha\scripts\launch_hidden.vbs" "<ps1 full path>"`。**等待策略**：`sh.Run cmd, 0, True`（True=等待子进程退出）——guard 脚本 while-true 常驻，wscript 随之常驻；guard 崩溃 → wscript 返回退出码 → Task Scheduler 检测失败 → RestartOnFailure 触发；与原 powershell 直接常驻行为一致，且避免 wscript 立即退出导致 Task Scheduler job object 误杀孙进程 guard。**why vbs 而非 .ps1 直接启动**：project_memory 硬约束——watchdog 任务禁止直接用 powershell.exe 启动，vbs 是消除闪窗的唯一方案。

### 10.12 幂等注册脚本 register_guard_tasks.ps1 / register_aux_tasks.ps1

**真源**：`scripts/register_guard_tasks.ps1`（guard 任务）+ `scripts/register_aux_tasks.ps1`（aux 任务）。**职责**：声明式幂等注册 5 个 Task Scheduler 任务（§10.5 表格），`Set-ScheduledTask` in-place 更新已存在任务。

**关键约束**（register_guard_tasks.ps1 头注释固化）：
- **NEVER Unregister+Register an existing task**——Unregister 会 TERMINATE 运行中的 guard 实例（2026-07-22 23:30-00:48 静默 guard 死亡根因：re-registration 杀了运行中 guard 42196/55188，watchdog 虽复活但服务 needless bounced），必须用 `Set-ScheduledTask` in-place 更新。
- **MultipleInstances=Parallel**（guard 任务，fix #ARCH-BOOT-001 Phase 1）：Task Scheduler 是 DUMB 周期启动器不参与单实例决策；单实例 SSoT 是脚本级 PID lock + heartbeat check——IgnoreNew 会阻断新 guard（僵尸 guard 占位时心跳接管成死代码）。
- **register_aux_tasks.ps1 保持 IgnoreNew**：一次性 AtLogOn 任务无 while-true guard 无僵尸风险，IgnoreNew 合适——**文档化有意非对称**（不变式测试 TestRegisterGuardUsesParallel / TestRegisterAuxKeepsIgnoreNew 钉死）。

**部署**（交互用户，无需管理员）：`powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1`（scheduler + tick_subscriber + ch_health_probe + deadman_switch）+ `powershell -ExecutionPolicy Bypass -File scripts\register_aux_tasks.ps1`（RSSHub + TraeCache）。

**why 声明式幂等而非手动 schtasks**：AI 可维护性（C7 约束）——register 脚本可重复执行（in-place 更新），AI 改配置后重跑脚本即同步，无需易错的手动 schtasks。

### 10.13 Prometheus HTTP 端点 metrics_server（P1-5 可观测性）

**真源**：`src/zephyr/shared/observability/metrics_server.py`（MOD-INF-016，D_SHARED 域）。**职责**：启动 daemon 线程提供 `/metrics` 和 `/health` HTTP 端点，输出 MetricsRegistry 的 Prometheus 兼容文本，被 §6.6 tick_subscriber 调用（`start_metrics_server(port=9925)`）。`GET /metrics`（Prometheus 文本 200）/ `GET /health`（200）/ 未知路径 404；端口默认 9925，daemon 线程不阻塞主流程，静默访问日志。

**why HTTP 端点而非只写 metrics.prom 文件**：文本文件需外部 scraper 定时读取延迟高；HTTP 端点支持 Prometheus pull 实时抓取 + curl 手动验证，tick_subscriber 独立进程的指标可被直接抓取；**daemon 线程而非独立进程**——metrics_server 是附属组件，独立进程会增加守护复杂度（又多一个 watchdog），daemon 线程随主进程生死。

### 10.14 数据相关 commit_gates 防回退门禁（pre-commit 静态检测层）

**真源**：`src/zephyr/gov_enforcement/commit_gates/`（MOD-GATE_ENGINE，D_GOV_CODE_QUALITY 域，由 `GitCommitGateway` 在 pre-commit 钩子统一调度）

**与 §10.9 不变式测试的区别**：§10.9 是运行时不变式测试（pytest 钉死设计）；本节是 commit 时静态检测（git diff staged 行 AST/正则扫描，AI 改代码时即时拦截）——两者互补，§10.9 防"运行时行为回退"，本节防"源码回退"。**why 独立成节**：100% AI 开发模式下，§5-§9 的设计决策（BufferedWriter/ch_reader FINAL/version 列/TableRegistry/CapabilityContract/无裸 SQL）若无 commit 门禁强制，AI 后续开发极易"图方便"绕过——门禁是设计决策的"执法层"配套。

**9 个数据相关门禁**（block=硬阻断 / warn=提醒不阻断）：

| gate_id | 文件 | 级别 | 防回退对象 | 裁定 |
|---|---|---|---|---|
| **CH-BATCH-SIZE** | ch_batch_size_gate.py | block | 禁止 for/async for 循环内直接调 `write_result`（必须经 §7.2 BufferedWriter） | #ARCH-CH-004 |
| **CH-FINAL-GATE** | ch_final_gate.py | block | 禁止直接调 `ch_writer.query()`（必须用 §7.6.2 ch_reader.query() 自动注入 FINAL） | #ARCH-CH-007 B5 |
| **CH-VERSION-COL** | ch_version_col_gate.py | block | 禁止 `quality_flag` 作 ReplacingMergeTree version 列（值全 1 致 merge 去重失效） | #ARCH-CH-009 |
| **TABLE-NAME-REGISTRY** | table_name_registry_gate.py | block | 禁止硬编码表名字符串（必须用 §5.6 TableRegistry）+ tasks.yaml 表名校验 | #ARCH-CH-024 Phase 5 |
| **CAP-CONSISTENCY** | capability_consistency_gate.py | block | `*_provider.py` 的 fetch 路由能力集 MUST = meta.capabilities 声明集 | #ARCH-CH-022 Phase 4.4 |
| **NO-BARE-SQL** | bare_sql_gate.py | block | 禁止裸 SQL 字面量（SELECT/INSERT/UPDATE/DELETE）—— SQL 集中化原则 §5.160 | §5.160.2 |
| **CAPABILITY-LOOKUP-REQUIRED** | capability_lookup_required_gate.py | block | commit 含 src/zephyr 业务代码变更时 session MUST 调 capability_lookup | #ARCH-066 |
| **CAPABILITY-OVERLAP** | capability_overlap_gate.py | block+warn | extract 级克隆（3+副本）硬阻断 / review 级（2副本）警告 / token overlap warn | #ARCH-FORCE-MERGE-DEDUP-001 |
| **DATA-TASK-COMPLETENESS** | data_task_completeness_gate.py | warn | tasks.yaml 新增 task 提醒配 §9.1 fallback_sources（不阻断） | §4 门禁设计 |

**豁免机制**：`tests/` 全豁免；docstring/注释/import 行豁免；模块自身豁免（ch_writer.py 豁免 CH-FINAL-GATE / table_registry.py 豁免 TABLE-NAME-REGISTRY）；`SQL_*` 常量定义行豁免（ast 精确识别多行常量）。

**fail-open / fail-closed 策略**：git diff 不可达 / AST 解析失败 / YAML 解析失败 → **fail-open**（passed=True，logger.warning，不阻断——检测器失效不能瘫痪开发）；检出违例 → **fail-closed**（阻断 commit）；audit log 目录缺失（capability_lookup）→ **fail-closed**（防"删目录绕过"攻击向量）。**紧急逃生**：`[no-lookup:reason]` commit msg 白名单标记 / `ZEPHYR_BYPASS_LOOKUP=1` 环境变量（与 `ZEPHYR_COMMIT_GATEWAY=1` 同级逃生阀）。

**why DATA-TASK-COMPLETENESS warn 而非 block**：历史 154 任务中 49 个（31.8%）无 fallback_sources（2026-08-12 实测），一次性全阻断会瘫痪开发，warn 渐进式补全后再收紧；**why CAPABILITY-OVERLAP 接入 CloneGuard**：纯 token overlap 检测不出"语义克隆"（变量改名+小逻辑增减），Echo-Guard 语义嵌入检测 extract 级克隆（3+副本）硬阻断强制合并去重。

## 11. 已施工盘点

### 11.1 代码文件清单（src/zephyr/data/）

> 真源：depgraph（`extract_depgraph.py --modules MOD-L00-004`）。以下为职责描述，文件列表以 depgraph 为准。共 63 个 .py 文件（2026-08-12 rg 实测）。

**包入口**：`__init__.py`（get_integrator 单例工厂）/ `__main__.py`（python -m zephyr.data CLI 入口）
**Provider 抽象层**：provider_base.py（IngestProviderBase + FetchPayload + FetchResult + IngestProviderMeta + CapabilityContract §5.1-§5.2）/ capability_validator.py（§5.8）/ error_classifier.py（§5.9）/ policy_registry.py（§5.7）/ table_registry.py（§5.6）/ quality_gate.py（§8.1 re-export wrapper）
**Provider 实现**（15 个）：implementations/{akshare,baostock,cls,eastmoney_news,eia,fred,ifind,internal_compute,miniqmt,qweather,rss,tdx,tickflow,tqcenter,tushare}_provider.py
**symbol 标准化**：symbol_normalizer/{__init__,normalizer}.py（§5.5 TRAE-082）
**域包入口**：satellite_geospatial_engine/__init__.py（§5.10 D_DATA 域入口 + CTR 契约声明）
**调度编排**：scheduler.py / task_queue.py / progress_store.py（§10.1）/ alerter.py（§10.2）/ metrics.py（§10.3）/ cli.py（§10.10）/ trading_calendar.py（§6.7）
**落库**：ch_config.py（§7.6.1）/ ch_reader.py（§7.6.2 FINAL 注入）/ ch_writer.py（§7.3）/ buffered_writer.py（§7.2）/ wal_writer.py（§7.8）/ local_replay.py（§7.7.1）/ wal_codec/{__init__,codec_registry,tsv_codec}.py（§7.9）
**质量完整性**：integrity_checker.py（§8.2 L11）/ backfill_checker.py（§8.3 L10）/ cross_source_validator.py（§8.4）/ source_health_check.py（§8.5）/ pit_query.py（§8.6）/ speed_tester.py（§10.4）
**业务下载器**：sector_kline_downloader.py（§6.8.1）/ sector_ranking_engine.py（§6.8.2）/ sector_snapshot_collector.py（§6.8.3）/ kline_resampler.py（§6.9）/ news_collector.py（§6.10.2）/ news_dedup.py（§6.10.1）/ tick_redis_cache.py（§7.11）/ tick_subscriber.py（§6.6）
**冗余容灾**：redundant_source/{__init__,heartbeat_monitor,source_switcher,backup_tick_poller,recovery,sqlite_fallback}.py（§9.2 热切换 + SQLite 兜底）
**配置**：`src/zephyr/data/config/tasks.yaml`（§11.2）/ `src/zephyr/data/config/schedule.yaml`（§6.2 15条目）/ `src/zephyr/data/config/policies.yaml`（派生）/ `src/zephyr/data/config/known_data_gaps.yaml`（§8.7）
**守护与自启**（跨域引用，真源在 D_INFRA_RUNTIME / scripts/）：infrastructure/{database_service.py（§7.10）, system_telemetry/{watchdog,health_aggregator,health_probes}.py} + shared/observability/{metrics,metrics_server}.py（§10.13） + scripts/{start_scheduler,start_tick_subscriber,start_ch_health_probe,deadman_switch,register_guard_tasks,register_aux_tasks,clean_trae_cache}.ps1 + launch_hidden.vbs（§10.11） + tests/scripts/{test_guard_invariants,test_guard_watchdog}.py（§10.9） + gov_enforcement/commit_gates/{ch_batch_size,ch_final,ch_version_col,table_name_registry,capability_consistency,capability_lookup_required,capability_overlap,bare_sql,data_task_completeness}_gate.py（§10.14 门禁 9 项）

### 11.2 配置文件清单

| 文件 | 作用 | 条目数 |
|---|---|---|
| `src/zephyr/data/config/tasks.yaml` | 采集任务清单（表→Provider→策略→fallback） | 154 任务（含 10 disabled，2026-08-12 实测） |
| `src/zephyr/data/config/schedule.yaml` | 15 个调度时段条目（L0~L11，含 L2.5 板块 + L3.5 慢新闻 + L10.5 每日补下载） | 15 条目 |
| `src/zephyr/data/config/policies.yaml` | per-source 策略参数（派生物，真源在 registry.yaml） | 派生 |
| config/known_data_gaps.yaml | 已知历史缺口注册表（§8.7，backfill 全范围回看） | 7 条登记（1 registered + 5 accepted + 1 resolved） |
| architecture_model/data/data_sources_registry.yaml | 数据源元数据 + policy（真源） | 12 数据源 |
| docs/03_modules/_cross_layer/database/business_data_categories.yaml | 业务数据品类/表名 SSoT 真源（§5.6 TableRegistry 消费对象，98 条品类） | 98 品类 |

**tasks.yaml 任务字段结构**（每个 task 的完整字段）：

| 字段 | 说明 | 示例 |
|---|---|---|
| `task_id` | 任务唯一标识 | `adj_factor_incremental` |
| `table` | 目标表（全限定，经 TableRegistry 校验） | `c1_market.adj_factor` |
| `source` | 主源 runtime_id | `miniqmt` |
| `schedule` | 调度时段（对应 schedule.yaml 标识） | `daily_kline` |
| `incremental` | 是否增量模式 | `true` |
| `date_col` | 日期列名（从 YAML 读取，禁止硬编码） | `trade_date` |
| `dependencies` | 同批次内前置任务 task_id（DAG 依赖） | `["adj_factor_incremental"]` |
| `capability` | Provider 能力标识（经 capability_validator 校验） | `adj_factor` |
| `symbols` | 标的列表（null=全市场，CapabilityContract.supports_symbols_null） | `null` |
| `fallback_sources` | 副源列表（§9.1，未配置则 DATA-TASK-COMPLETENESS warn） | `[{source: ifind, capability: adj_factor}]` |
| `extra` | 扩展字段（description / trading_day_only 等） | `{description: "..."}` |

### 11.3 文档清单

文档清单与 §17 引用同源：`_domain_data/` 7 篇（index.md MOD-L00-001 D-DATA 域索引 / blueprint.md MOD-L00-001 v4.0.4 / data_source_integrator_blueprint.md MOD-L00-004 what 层真源 v0.4.1 / data_source_operation_manual.md MOD-L00-002 / boot_autostart_architecture.md / redundant_source_blueprint.md / wal_codec_blueprint.md）+ `_domain_mkt_data/` 6 子模块蓝图（autoload/connectors/failover/raw_data_cache/vendor_base/vendor_registry）+ `11_d_data.md`（D_DATA 域 183 模块）+ `05_dataflow_architecture/`（data_inventory + data_acquisition_requirements P0-P3）+ design_memos 5 篇（15 互补 / 17 特殊交易日 / 18 冷归档 / 19 北向快照 / 63 配套）——链接与真源路径见 §17.1-§17.3。

### 11.4 数据消费者层（上游依赖 zephyr.data 的模块）

> 数据下载层的输出被谁消费。核对方式：`rg "from zephyr\.data|import zephyr\.data" src/zephyr/`。

**直接消费者**（src/zephyr/data/ 内部互引除外）：

| 消费者 | 域 | 消费的数据下载层能力 | 用途 |
|---|---|---|---|
| `regime/regime_feature_builder.py` | D_REGIME | ch_reader.query / table_registry | regime 特征构建读取行情/板块数据 |
| `runtime/intraday_main.py` | D_RUNTIME | tick_subscriber / ch_reader / table_registry | 盘中主流程消费实时 tick + 历史数据 |
| `infrastructure/database_service.py` | D_INFRA_RUNTIME | 提供 CH/Redis 连接（提供者，非消费者） | §7.10 统一连接管理 |

**间接消费者**（通过 regime/runtime 二次传递）：D_FACTOR / D_SIGNAL / D_RESEARCH / D_BACKTEST 等域通过 CTR-001 NormalizedMarketData 契约消费数据下载层产出的标准化行情（§5.10 CTR 契约声明）。

**why 记录消费者层**：数据下载层的任何接口变更（如 ch_reader.query 签名 / table_registry.table 返回值）MUST 评估对这些消费者的影响——这是 §5.10 CTR 契约 + ContractImpactAnalyzer 的输入。

### 11.5 单元测试与不变式测试清单（验证层配套）

> 数据下载层的验证配套分两类：单元测试（验证模块行为正确）+ 不变式测试（钉死设计决策防回退）。

**A. 模块单元测试**（`tests/zephyr/data/`，25 个文件，验证 §5-§7 各模块行为）：test_provider_base / test_providers / test_providers_stage3（Provider 抽象+15 实现 §5.1/§5.3）/ test_capability_validator（§5.8）/ test_internal_compute_provider（§5.4）/ test_data_scheduler / test_data_task_queue（§6.1/§6.4）/ test_data_cli（§10.10）/ test_ch_writer（§7.3）/ test_wal_writer / test_wal_codec（§7.8/§7.9）/ test_local_replay（§7.7.1）/ test_redundant_source / redundant_source/test_heartbeat_monitor_alert（§9.2）/ test_tick_subscriber / test_tick_redis_cache（§6.6/§7.11）/ test_kline_resampler（§6.9）/ test_sector_ranking_engine / test_sector_snapshot_collector（§6.8.2/§6.8.3）/ test_integrity_checker / test_cross_source_validator（§8.2/§8.4）/ test_policy_registry / test_error_classifier（§5.7/§5.9）/ test_progress_store / test_alerter / test_metrics（§10.1/§10.2/§10.3）

**B. 数据治理测试**（`tests/data/`，13 个文件，验证数据生命周期/质量/分类）：
test_data_classification / test_data_lifecycle / test_data_pipeline_guard / test_data_quality / test_data_quality_gate / test_data_source_reliability / test_data_volume_growth_monitor / test_l00_data_source / test_market_quality_validator / test_news_collector / test_pit_query / test_source_health_check / test_symbol_normalizer

**C. commit_gates 门禁测试**（`tests/governance/commit_gates/`，验证 §10.14 门禁本身正确）：
test_ch_batch_size_gate / test_ch_final_gate / test_ch_version_col_gate / test_data_task_completeness_gate / test_table_name_registry_gate / test_capability_lookup_required_gate / test_capability_overlap_gate / test_bare_sql_gate

**D. 守护不变式测试**（`tests/scripts/`，§10.9 已述）：test_guard_invariants / test_guard_watchdog（钉死 §10.5-§10.8 守护配置防回退）

**why 记录测试层**：测试是配套的验证层——模块行为变更 MUST 同步更新单元测试，设计决策变更 MUST 同步更新不变式测试；AI 改代码时通过 `[TESTS]` 头注释定位对应测试文件。

## 12. 已知缺口与升级方向（讨论载体）

> **本节是用户要求的"对系统里已经有的数据源和数据下载进行全面升级"的讨论载体**。逐项列出已识别的缺口、待升级项及其裁定。**v1.4.0（2026-08-13）已定稿**——本节全部项裁定收敛，裁定单一真源在 §16（三表：待人拍板/裁定施工/裁定暂缓），本节各小节只留结论指针。

### 12.1 iFind 试用到期遗留影响（#ARCH-IFIND-FAILOVER）

**现状**：iFind 试用账号到期，7 类 9 任务已降级（估值/资金流/行业分类/概念板块/实时快照/板块信息/行业分类补充），akshare/tushare 升为主源。

**缺口**：
- `edb_data_incremental` **disabled**（iFind EDB 配额耗尽 -4318，5万条/月不够拉 104 个宏观指标全历史，无 fallback）——edb_data 表至今 0 行，known_data_gaps 登记 `edb_data_ifind_quota_exhausted` 状态 **accepted**（macro_data akshare 291K 行作为主宏观数据源）。
- **国际宏观已由 #ARCH-EDB-EXPAND 落地**（2026-08-04）：FRED 3 任务（macro_fred/macro_worldbank 22 序列）+ EIA 2 任务（石油/天然气）启用中——国际宏观缺口已闭合，**中国宏观 EDB 仍无完整替代**（akshare macro_data 覆盖主要指标但非 EDB 全量 104 指标）。
- iFind 续费后需手动改回 source=ifind（7 类任务），目前 tasks.yaml 已保留 ifind 为 fallback，切换成本低。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] iFind 续费 → **待人拍板（费用项），默认建议暂不续费**——akshare/tushare 已兜底 7 类 9 任务、国际宏观已由 #ARCH-EDB-EXPAND 闭合、fallback 配置保留切换成本低（§16.1 Q1）。
- [x] 中国宏观 EDB 104 指标全量化 → **不做，维持 accepted 缺口**——macro_data（akshare）兜底核心指标，多源拼凑口径漂移风险大于收益；未来按需单点补指标（§16.3 Q2）。

### 12.2 disabled 任务清单及原因

> 2026-08-12 实测 tasks.yaml 共 **10 个** disabled 任务（下表前 10 行）；`msci_adjustment_refresh` 从未在 tasks.yaml 登记（v1.2.1 误列入本表），实际是"待接入未配置"缺口，保留在 §12.6。

| task_id | disabled 原因 | 修复路径 |
|---|---|---|
| edb_data_incremental | iFind EDB 配额耗尽（-4318)，无 fallback | iFind 付费版 / 维持 accepted（macro_data 兜底） |
| audit_opinion_incremental | AKShare 无专用批量审计意见接口，逐股获取效率过低 | 待 iFind 等数据源补齐 |
| rights_issue_incremental | akshare 1.18+ 移除 stock_rights_issue_detail_sina，逐股接口效率过低 | 待数据源补齐 |
| news_tushare_incremental | API 已废弃（数据截止2024-08，pro.news 返回"请指定正确的接口名"） | 由 RSS/cls/eastmoney 覆盖 |
| kline_us_daily_qmt_incremental | QMT 无美股板块，需单独开通美股行情权限 | 已由 tickflow+akshare 双源覆盖 |
| l2_tick_snapshot | 需付费 L2 行情权限（#ARCH-DATA-014） | 用户开通 L2 后启用，fallback 降级到 tick_data |
| margin_trading_qmt_placeholder | QMT 无接口，已由 AKShare 覆盖 | 占位 disabled |
| dragon_tiger_qmt_placeholder | QMT 无接口，已由 AKShare 覆盖 | 占位 disabled |
| block_trade_qmt_placeholder | QMT 无接口，已由 AKShare 覆盖 | 占位 disabled |
| kline_5min_history_backfill | 百度云已下载2000-2024，任务已退役 | — |

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] audit_opinion / rights_issue 替代源 → **暂缓，维持 disabled**——低频事件无当下消费方，26 号事件驱动施工到需要时再启（§16.3 Q3）。
- [x] MSCI/富时调整爬虫 → **暂缓**——走 #ARCH-SPECIAL-DAYS 补登记后由 17 号特殊日子治理承载，不单开爬虫（§16.3 Q3/Q13）。
- [x] L2 行情开通 → **待人拍板（费用项），默认建议暂不开通**——24 号打板策略未到需 L2 微观结构的施工阶段，tick_data 降级兜底中（§16.1 Q4）。

### 12.3 blocked/broken API（akshare 数据源退化）

**现状**（fetch_perf 实测）：`akshare.money_flow` **blocked**（东财反爬封锁 RemoteDisconnected，#ARCH-IFIND-FAILOVER 后 akshare 主源但也 blocked，实际靠 fallback 链兜底）/ `akshare.equity_pledge` **broken**（API 损坏 data_json[result]为 None，已回退 ifind）/ `akshare.equity_pledge_summary` **broken**（同上）/ `akshare.daily_valuation` **rate_limited**（百度API空响应率15%，0.17只/s）。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] akshare money_flow blocked 替代源 → **先验证 fallback 链实效 + 评估 tushare moneyflow 积分，专用爬虫暂缓**（§16.2 Q10 / §16.3 Q19）。
- [x] equity_pledge broken 替代源 → **评估 tushare pledge（积分成本），积分不经济则登记 accepted 缺口**——低频数据影响面有限（§16.3 Q19）。
- [x] daily_valuation rate_limited 优化 → **暂缓**——维持 1s/股限流，全量走周末窗口；终极解是 local_valuation 本地估值（§16.3 Q14/Q20）。

### 12.4 slow capability（性能瓶颈）

**现状**：`miniqmt.adj_factor` **slow** 0.09只/s（get_divid_factors 每只11秒，全量16h）——增量模式下每日只拉近期可接受，全量回算需周末窗口。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] adj_factor 全量回算优化 → **暂缓**——增量模式每日可接受，全量回算走周末 16h 窗口；复权因子是交易核心数据，换源反推有口径一致性风险，宁慢勿错（§16.3 Q21）。

### 12.5 北向资金日频断档（19 号文档）

**现状**：港交所 2024-08-16 停止公布北向资金每日明细，`hk_connect_flow` 只有 2014-11-17~2024-08-16 历史。19 号文档已定方案：tushare hk_hold 季度末持仓快照作为日频断档替代。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] 19 号方案落地施工 → **施工，P1**——项目层面已有裁定（日频断档→tushare hk_hold 季度快照，akshare fallback），19 号 draft v0.1.0 转施工队列（§16.2 Q5）。

### 12.6 数据源覆盖缺口

| 缺口 | 影响 | 候选方案 |
|---|---|---|
| MSCI/富时指数调整 | 外资流入预期（ARCH-SPECIAL-DAYS 未登记编号） | 爬虫 MSCI 官网 / Wind / 第三方 |
| L2 逐笔行情 | 打板策略微观结构（24 号） | 付费开通 miniQMT L2 权限 |
| edb_data 中国宏观 EDB | 宏观因子（104 指标） | iFind 付费版 / akshare+东方财富+统计局拼凑 |
| 龙虎榜机构席位明细 | 机构资金动向 | akshare 已覆盖（dragon_tiger_seat） |
| 期货分笔数据 | 期货微观结构 | 待评估需求 |
| 港股 Level2 | 港股微观结构 | 待评估需求 |

### 12.7 调度编排升级方向

**现状**：APScheduler 常驻进程 + 15 个时段条目 + DAG 依赖 + fallback 三层韧性。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] 调度优先级动态化 → **暂缓**——静态排序够用，日终窗口总耗时翻倍时重评（§16.3 Q11）。
- [x] 任务级 SLA 监控 → **暂缓**——L11 巡检 + 任务失败告警已兜底，分钟级 SLA 个人项目过度工程（§16.3 Q23）。
- [x] 跨源并发优化 → **暂缓**——default 8 / heavy 2 线程当前无瓶颈，再细化收益有限（§16.3 Q23）。
- [x] 调度器高可用 → **够用**——Task Scheduler watchdog + misfire_grace_time 已治本（2026-08-07 事故验证），双活过度工程（§16.2 Q12）。

### 12.8 落库体系升级方向

**现状**：ReplacingMergeTree 统一 + BufferedWriter 攒批 + ch_writer 混合传输 + 8 表 MergeTree 遗留。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] 8 个 MergeTree 遗留表迁移 RMT → **暂缓**——写前 DELETE 逻辑稳定运行，merge 压力未再现；RMT 去重键验证成本>收益时迁移（§16.2 Q7）。
- [x] data parts 监控告警 → **施工，P1**——防 CH 事故重演，parts>100 告警阈值 + Grafana 面板（§16.2 Q8）。
- [x] 冷归档落地 → **施工，P2**——18 号 draft v0.1.0 转施工队列（§16.2 Q6）。
- [x] WAL 兜底常态化 → **已常态化**——BufferedWriter 写 CH 失败即落本地 TSV，integrity_checker 补录机制验证通过（无需再裁定）。

### 12.9 质量与完整性升级方向

**现状**：quality_gate 读取端校验 + integrity_checker L11 每日巡检 + backfill_checker L10 周补 + cross_source_validator 跨源验证。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] 质量门控前移 → **暂缓**——当前写入后零脏数据事故，quality_gate 读取端已兜底；增加吞吐损失无收益（§16.2 Q9）。
- [x] 跨源验证扩展 → **暂缓**——tick 场景 QMT vs TDX 已覆盖；离线 per-field 对账（2%/3% 容差）维护成本与收益不成正比（§16.3 Q24）。
- [x] 数据血缘追踪 → **暂缓**——无溯源需求场景，fetch_perf 已记 source+capability；数据质量问题出现且 fetch_perf 无法定位时重评（§16.3 Q24）。
- [x] PIT 一致性巡检 → **暂缓**——PIT 铁律由 15 号数据特征层承载，数据下载层不重复建设（§16.3 Q24）。

### 12.10 数据源扩展方向

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] 东方财富爬虫专用 provider → **暂缓**——先验证 fallback 链实效 + 评估 tushare moneyflow 积分，专用爬虫 ROI 不足时再说（§16.2 Q10）。
- [x] 同花顺 iwencai 爬虫 → **暂缓**——akshare 已包装够用；若 iFind 续费则恢复（§16.3 Q22）。
- [x] 国家统计局爬虫 → **暂缓**——macro_data（akshare）已覆盖核心指标（§16.3 Q22）。
- [x] 券商场内数据/L2 逐笔 → **待人拍板（费用项），默认建议暂不开**——24 号打板策略未到需 L2 微观结构的施工阶段（§16.1 Q4）。

### 12.11 守护与自启升级方向

**现状**：四层防御 Watchdog（#ARCH-BOOT-001 resolved）+ 死人开关告警（#ARCH-BOOT-002 落地）+ 不变式测试防回退（8 项）+ HealthAggregator 12 系统三态探针 + ch_health_probe 独立探针 + 三冗余 Watchdog（MOD-INF-015）。2026-08-07 intraday 停摆 2 日事故已治本。

**裁定（v1.4.0 定稿，理由与重评条件见 §16）**：
- [x] 死人开关告警通道冗余 → **暂缓**——飞书 webhook 3 个月零故障；通道失效概率低于本任务自身死亡退化概率，叠加收益有限（§16.3 Q25）。
- [x] HealthAggregator 12 系统探针含数据集成器 → **已纳入**——scheduler/tick_subscriber/ch_health_probe 已补入 SYSTEMS 列表（2026-08-12 实证确认，§16.3 Q25）。
- [x] 心跳阈值调参 → **暂缓**——当前 guard 15s/5min + deadman_switch 10min 零误报；盘中/盘后差异化无显著收益（§16.3 Q25）。
- [x] ch_health_probe 探测频率 → **维持 3s**——盘中毫秒级无此需求，CH 单机 VM 3s ping 负载可忽略（§16.3 Q25）。
- [x] 三冗余 Watchdog 启用 → **暂缓**——当前四层防御已治本（2026-08-07 事故验证），三冗余为锦上添花，不阻塞 active（§16.3 Q25）。
- [x] 年度健康报告落地 → **暂缓**——HealthAggregator 接口就绪但无 review 机制； uptime_ratio/mttr/degradation_ratio 待 review 机制建立后启用（§16.3 Q25）。
- [x] 跨服务依赖故障传播 → **已覆盖**——RSSHub 已纳入 SYSTEMS 列表（health_probes.py），rss_provider 失效由 HA 探针发现（§16.3 Q25）。

### 12.12 2026-08-12 架构审查新发现（v1.3.0）

> 本轮审查（rg 全量扫描代码/配置实证）发现的运行时缺口与漂移，**均为代码/配置层问题**——按约束本文档只记录不定决策，修复责任与 ARCH 登记已裁定（§16.2 Q13-Q18，v1.4.0）。

#### 12.12.1 【P1】internal Provider 未接线 create_provider——#ARCH-DATA-001 止血修复运行时断裂

**实证**：`scheduler.create_provider()`（scheduler.py L987-1049）共 14 个分支（ifind/miniqmt/akshare/baostock/tushare/tickflow/tdx/rss/cls/eastmoney_news/tqcenter/fred/eia/qweather），**无 `internal` 分支**——`source: internal` 落入 else 返回 None（"未知数据源" warning）。

**影响**：`hk_trade_calendar_refresh`（monthly_static，source=internal，#ARCH-DATA-001 止血从 akshare 切到 internal）每月 1 日触发时**主源必然失败**；另 stock_indicator 任务 fallback 到 internal（2 处）同样断裂。internal_compute_provider.py L32 docstring 自称"接入调度器：create_provider() 的 source=="internal" 分支返回本类实例"——**docstring 虚标**，与实现脱节（#ARCH-CH-004 蓝图-实现鸿沟同类）。**技术细节**：technical_indicator/calendar_event 两个 capability 无 tasks.yaml 任务（技术指标实际由 `src/zephyr/factor/technical_indicators/` D_FACTOR 域独立计算链路承载），故断线仅影响 hk_trade_calendar 一月度任务 + stock_indicator fallback。

**裁定（v1.4.0 定稿）**：见 §16.2 Q18——create_provider 补 `internal` 分支（一行 elif）+ 修 docstring 虚标 + 评估 hk_trade_calendar 缺口 + 登记新 ARCH 条目；代码修复越界未做，施工转 P0 缺口登记候选库。

#### 12.12.2 【P2】死 fallback 35 处——"心理安慰型"韧性配置

fallback_sources 中 35 处引用无 Provider 实现的 source（§9.1 死 fallback 警告；逐源计数与处置真源在 §16.2 Q14）。主源失败时这些 fallback 触发即落入"未知数据源"失败，**不提供实际韧性**且掩盖真实风险敞口。

**裁定（v1.4.0 定稿）**：见 §16.2 Q14——清理 qmt/exchange/bdpan 死配置 28 处（保留 local_valuation 1 处——daily_valuation_full_refresh 末级 fallback 有真实需求，补 internal compute provider 实现后启用）。

#### 12.12.3 【P2】自动熔断（circuit breaker）缺失——与 2026 行业实践差距

2026 韧性工程主流实践（SRE playbook）：**circuit breaker** 自动熔断——滑窗错误率超阈值自动熔断源→冷却→半开探针恢复，区别于重试（retry）。项目现状：有指数退避重试（policy_registry backoff）+ 错误分类 fallback（error_classifier）+ **手动熔断**（`integrator pause <source>` CLI），但**无自动熔断**——某源持续故障时每个任务都要独立经历"重试 N 次→fallback"的完整开销，且同 schedule 内多任务重复打击已死源（如 akshare 反爬封锁时 61 个 akshare 任务逐个失败）。

**裁定（v1.4.0 定稿）**：见 §16.2 Q17——scheduler 层加 per-source 自动熔断器（连续失败 N 次熔断 M 分钟，滑窗错误率超阈值自动熔断→冷却→半开探针恢复）；登记 CAND 候选库，与手动 `integrator pause` 互补不替代。

#### 12.12.4 【P3】#ARCH-DATA-002 语义契约盲区——CapabilityContract 的行为/语义边界

§5.2 已补语义边界说明。CapabilityContract 管"行为"（增量/全量/日期/全市场），不管"语义"（capability 名↔实际 API 语义对齐）。#ARCH-DATA-001（A股日历冒充港股日历）证明语义盲区真实存在；#ARCH-DATA-002（capability-API 语义对齐校验，P2，registry proposed）是系统性治本，17 号 §5 有 5 项施工稿（capability_api_whitelist gate 等）。当前 MVP 阶段靠即时止血 + 人工 review 兜底（17 号用户裁定"能做就尽快上"）。64 号补此衔接，施工节奏由 17 号/registry 主导。

**裁定（v1.4.0 定稿）**：见 §16.2 Q15——CapabilityContract 三闲置字段（supports_incremental/supports_full_refresh/requires_date_range）**保留不裁剪**——#ARCH-DATA-002 语义校验落地时复用，裁剪有破坏性变更风险。

### 12.13 研究知识源扩展方向（BM-RES-11 / BM-RES-11-A 多模态知识采集，v1.3.1 作战地图全覆盖补丁补登）

> **定位**：作战地图 BM-RES-11（多模态知识采集，L1，design 态，source_ref：学习系统架构.md §3 S0 多模态知识采集层）+ 子环节 BM-RES-11-A（采集源分类与调度，S0）覆盖**研究知识源**——研报/新闻/公告/财报/社交媒体/另类数据/论文库（外部源 → 采集 → 分类 → 调度 → BM-RES-06 LLM 研究 Agent / 论文追踪）。本文档当前 15 源全部面向**行情/基本面/宏观交易数据**；研究知识源接入时是本体系的扩展方向而非平行新体系。
>
> **裁定（扩展模式已定，建设项登记候选）**：研究知识源接入时**按 §5.7 per-source 策略对象模式扩展**——每新增知识源=新增一个 Provider 实现（IngestProviderBase）+ data_sources_registry.yaml 一条元数据 + policies.yaml 一条 SourcePolicy，**复用现有配额（rpm/concurrency/min_interval_sec）/重试（max_retries/backoff/retry_on）/fallback（§9.1 fallback_sources + error_classifier 可恢复性判断）机制**，不新建采集框架。BM-RES-11-A 的 6 类源分类（研报/新闻/公告/财报/社交/另类）按"一源一 policy"登记，调度策略（优先级+QPS 分配+重试+增量）复用 §6 调度编排层 15 时段条目模式。**理由**：① §5.7 已论证"why per-source 策略对象而非统一装饰器"——15 个源特性差异极大必须 per-source，研究知识源差异更大（RSS 遵守 robots.txt/论文库 API 配额/社交平台反爬）更需同模式；② 新闻采集链（news_collector + news_dedup，§6.10）已是研究知识源的第一个生产实例，证明本体系承载力；③ 与 C-022/C-044 iFind QPS 协同登记一致（作战地图 code_mapping 注记）。**重评条件**：研究知识源种类超过现有时段条目承载（>5 类新源）或 QPS 配额跨源挤兑时，评估独立知识采集调度面。
>
> **登记候选（v4.0 采集增强，非 MVP）**：BM-RES-11-A 的**智能去重 / 相关性预筛**两项采集增强登记为候选——智能去重可复用 §6.10.1 news_dedup 的标题 MD5 去重模式扩展到跨源（同一研报多渠道转载）；相关性预筛（采集时即按研究主题相关性打分过滤）是知识源特有需求（交易数据源全量落库，知识源量大噪声多需预筛），待 BM-RES-06 LLM 研究 Agent 上线时一并评估。降级路径对齐作战地图登记：主源失效→自动切换备用源；调度超限→降级 QPS+延后非优先源。
>
> **边界**：本环节管"研究知识怎么进来"（采集/分类/调度），下游清洗（BM-RES-08-A）与 LLM 消费（BM-RES-06）不在本文范围；研究知识源的**内容语义校验**（如研报 PDF 解析正确性）不属 #ARCH-DATA-002 capability 语义对齐范畴，由下游质量门另行评估。

**裁定（v1.4.0 定稿）**：§12.13 扩展模式已定（per-source 策略对象扩展 + 复用现有机制），无需再裁。智能去重/相关性预筛已登记候选库（非 MVP），见 §16.3 Q26。

## 13. 考虑过的替代方案

| 方案 | 拒绝理由 |
|---|---|
| 每个 _fetch_*.py 脚本各写各的（原 61 项手动触发） | 无共享调度/重试/限流基础设施；tmp/ 是 TTL=task_bound 临时目录，脚本退役后能力丢失 |
| Windows 任务计划/cron 调度 | 无任务依赖/并发控制/重试编排能力，OS 级触发器能力不足 |
| 统一重试装饰器（所有源同一套策略） | 各源差异大（配额/反爬/线程安全），需 per-source 策略对象 |
| 仅调度层（不重建 Provider） | 现有 Provider 抽象未落地（src/zephyr/data/ 原为空），割裂设计会引用空中楼阁 |
| MergeTree 先删后插（原设计） | 5204 只股票逐个写入时先删后插=双倍 data parts，CH merge 满载崩溃（#ARCH-CH-002） |
| 临时表 staging 去重 | 复杂度过高（#ARCH-CH-002 拒绝） |
| ch_writer 全走 WSL subprocess | 每次 INSERT 启动 1 个 WSL 进程，129ms/次开销大（#ARCH-CH-005 拒绝） |
| ch_writer 全走 clickhouse-driver TCP | 类型安全约束（Date 列需 datetime.date 对象），8 个 Provider 类型转换改造风险高（#ARCH-CH-005 部分拒绝） |
| fallback 门禁硬阻断（block 级） | 有些表确实无副源（tick_data 只有 miniqmt），硬阻断阻碍开发（#ARCH-CH-015 拒绝） |
| 硬编码表列表做巡检/补下载 | 新增表需手动维护表列表，违反"新表自动纳入"核心需求（动态发现方案采用） |
| 固定阈值做完整性巡检 | 不同表行数量级差异大（tick_data 2000万 vs macro_data 几十行），固定阈值无法通用 |
| 异常类型判断错误分类（isinstance） | FetchResult.error 是字符串（跨 Provider 统一接口），无法用 isinstance（关键词匹配采用） |
| 商业 Feature Store（Feast/Tecton） | $15k-40k/月、4-6 FTE，个人项目用不起也不需要（15 号 §2.2 已裁定） |

## 14. 上限定义与演进路径

### 14.1 系统上限

| 维度 | 上限 | 理由 |
|---|---|---|
| 数据源数量 | 15 个（当前已满） | 个人项目维护成本，新增需评估 ROI |
| 任务数量 | 无硬上限（动态发现） | tasks.yaml 注册即纳入调度/巡检/补下载 |
| 调度时段 | 15 个条目（当前） | 按数据频率分层，新增频率需求可加条目 |
| 单表行数 | ClickHouse 单机限制（~千亿行/表） | 受 Hyper-V VM 磁盘容量约束 |
| 并发 | default 8 线程 + heavy 2 线程 | APScheduler ThreadPoolExecutor 配置 |
| 数据保留 | 永久（Hot 层无 TTL） | PS-CTR-003 铁律 |

### 14.2 演进路径

1. **短期**（v1.4.0 定稿施工清单）：Q18 internal 接线修复（P0）/ Q8 data parts 监控（P1）/ Q17 per-source 自动熔断器（P1）/ Q14 死 fallback 清理 28 处 / Q13 SPECIAL-DAYS 补登记 ARCH 条目
2. **中期**：Q5 19 号北向快照落地（P1）/ Q6 18 号冷归档落地（P2）/ Q16 fetch_perf 被动记录通道（P2，为调度动态化/自动熔断供数）
3. **长期**：Q1/Q4 费用项用户拍板后按裁定执行 / 数据源扩展（东方财富爬虫/iwencai 爬虫/统计局爬虫，§16.3 Q22 暂缓）/ 调度优先级动态化（§16.3 Q11 暂缓，依赖 Q16 数据）/ 数据血缘追踪（§16.3 Q24 暂缓）

## 15. 待裁定

> 以下为暂缓项，非永久禁止，随项目演进重新裁定。**v1.4.0 定稿后本表与 §16.3 裁定暂缓/维持/不做项合并**——§16.3 是裁定真源（含理由+重评条件），本表保留作快速索引。

| 项 | 暂缓理由 | 重评条件 | §16 裁定 |
|---|---|---|---|
| 8 个 MergeTree 遗留表迁移 ReplacingMergeTree | 需验证去重键正确性，迁移有数据风险 | 写前 DELETE 逻辑维护成本累积到痛点时 | §16.2 Q7 |
| 质量门控前移（写入时校验） | 拖慢下载吞吐，脏数据可事后清洗 | 关键表出现脏数据污染下游时 | §16.2 Q9 |
| 调度优先级动态化 | 当前静态排序够用 | slow/rate_limited 任务影响盘后窗口完成时间时 | §16.3 Q11 |
| 数据血缘追踪 | fetch_perf 已记录 source+capability | 出现数据溯源需求时 | §16.3 Q24 |
| 东方财富专用爬虫 provider | akshare 包装够用 | akshare.money_flow blocked 长期无解时 | §16.2 Q10 |

## 16. 待定问题（开放问题）

> **v1.4.0 定稿裁定**——18 项开放问题 + §12 全部缺口/升级方向已逐项裁定收敛，分三表：
> - **§16.1 待人拍板（费用项）**：2 项——涉及费用支出，AI 给默认建议，最终决策权在用户。
> - **§16.2 裁定施工（登记候选/转施工队列）**：14 项——AI 裁定"做"，登记 CAND 候选库或转施工队列，附施工要点。
> - **§16.3 裁定暂缓/维持/不做**：19 项——AI 裁定"暂缓/维持现状/不做"，附理由与重评条件（§15 待裁定表同源）。

### 16.1 待人拍板（费用项）

| # | 问题 | 默认建议 | 理由 | 决策方 |
|---|---|---|---|---|
| Q1 | **iFind 是否续费**？续费则恢复 7 类任务主源 + edb_data 可用；不续费则 edb_data 永久 disabled 需找替代源。 | **暂不续费** | ① akshare/tushare 已兜底 7 类 9 任务（估值/资金流/行业分类/概念板块/实时快照/板块信息/行业分类补充），fallback 链完整；② 国际宏观已由 #ARCH-EDB-EXPAND 闭合（FRED+EIA 5 任务启用中）；③ tasks.yaml 保留 ifind 为 fallback，续费后改回主源成本低；④ 个人项目成本敏感，iFind 付费版 ROI 待评估 | 人 |
| Q4 | **L2 行情是否开通**？影响打板策略微观结构分析（24 号相关），需付费。 | **暂不开通** | ① 24 号打板策略当前处于设计/回测阶段，未到需 L2 逐笔委托/快照的施工阶段；② tick_data（L1）已降级兜底，打板策略 MVP 可用 L1 验证；③ 费用支出与策略验证阶段不匹配——策略未验证有效前不投数据成本；④ miniQMT L2 权限开通后随时可启用（`l2_tick_snapshot` 任务已预留） | 人 |

### 16.2 裁定施工（登记候选/转施工队列）

| # | 问题 | 裁定 | 施工要点 | 登记 |
|---|---|---|---|---|
| Q5 | **19 号北向快照是否落地施工**？draft v0.1.0，tushare hk_hold 季度替代方案。 | **施工，P1** | 项目层面已有裁定（日频断档→tushare hk_hold 季度快照，akshare fallback）；19 号 draft v0.1.0 转施工队列，fetcher+落表+外资行为方法论三步走 | CAND 候选库 |
| Q6 | **18 号冷归档是否落地施工**？draft v0.1.0，数据保留铁律要求 Cold 层手动触发。 | **施工，P2** | 18 号 draft v0.1.0 转施工队列；Cold 层手动触发机制 + 冷热分层存储（Hot ClickHouse / Cold Parquet on disk）；PS-CTR-003 铁律合规 | CAND 候选库 |
| Q7 | **8 个 MergeTree 遗留表是否迁移 ReplacingMergeTree**？需验证去重键正确性。 | **暂缓** | 写前 DELETE 逻辑稳定运行，merge 压力未再现；迁移收益（去 DELETE 逻辑）< 验证成本（去重键正确性+数据风险）；重评条件：DELETE 逻辑维护成本累积到痛点时 | §15 待裁定 |
| Q8 | **data parts 监控告警是否加**？system.parts > 100 告警，防止 parts 爆炸重演。 | **施工，P1** | 防 CH 事故重演——2026-07-09 parts 爆炸致 CH merge 满载崩溃事故教训；parts>100 告警阈值 + Grafana 面板 + alerter 通知 | CAND 候选库 |
| Q9 | **质量门控是否前移**？关键表（kline_daily/财务三表）写入时加轻量校验？ | **暂缓** | 当前写入后零脏数据事故，quality_gate 读取端已兜底；前移增加吞吐损失无收益；重评条件：关键表出现脏数据污染下游时 | §15 待裁定 |
| Q10 | **东方财富专用爬虫 provider 是否做**？akshare.money_flow blocked 长期无解时。 | **暂缓** | 先验证 fallback 链实效 + 评估 tushare moneyflow 积分（Q19），专用爬虫 ROI 不足时再说；重评条件：akshare.money_flow blocked 长期无解且 tushare 积分不经济时 | §15 待裁定 |
| Q12 | **调度器高可用是否够用**？单进程 + Task Scheduler watchdog + misfire_grace_time，还是要双活？ | **够用** | Task Scheduler watchdog + misfire_grace_time 已治本（2026-08-07 事故后零复发）；双活引入分布式锁/脑裂复杂度，个人项目过度工程 | 无需登记 |
| Q13 | **SPECIAL-DAYS 编号悬空**：补登记正式 ARCH 条目，还是全局清除该编号？ | **补登记正式 ARCH 条目** | 特殊日子治理（MSCI/富时调整/分红除权/财报披露）有真实需求——影响外资流入预期 + 事件驱动策略；#ARCH-DATA-001/002 只覆盖语义对齐，不覆盖特殊日子数据采集；登记后 17 号 frontmatter 恢复 # 前缀引用 | ARCH registry（待登记） |
| Q14 | **死 fallback 35 处如何处置**（§12.12.2）？①清理；②补实现；③保留标注。 | **清理 28 处 + 保留 1 处** | 清理 qmt（7）/exchange（26）/bdpan（1）= 34 处→实际清理 28 处（exchange 26 处中 2 处可能为未来保留）；保留 local_valuation 1 处——daily_valuation_full_refresh 末级 fallback 有真实需求（本地估值计算），补 internal compute provider 实现后启用 | CAND 候选库 |
| Q15 | **CapabilityContract 三闲置字段是否裁剪**（§5.2 实证）？ | **保留不裁剪** | supports_incremental/supports_full_refresh/requires_date_range 当前默认值未启用，但 #ARCH-DATA-002 语义校验落地时需复用（capability 行为约束是语义校验输入）；裁剪有破坏性变更风险，保留零成本 | 无需登记 |
| Q16 | **fetch_perf 是否补被动记录通道**（§10.4 实证 scheduler 零写入）？ | **施工，P2** | scheduler 每次任务结束写一条运行时 fetch_perf，让 api_status 反映真实运行而非仅测速抽样；为 Q11 调度动态化/Q17 自动熔断提供数据基础 | CAND 候选库 |
| Q17 | **是否加 per-source 自动熔断器**（§12.12.3）？ | **施工，P1** | 2026 行业实践 circuit breaker 已是标配；scheduler 层加 per-source 自动熔断器（连续失败 N 次熔断 M 分钟，滑窗错误率超阈值自动熔断→冷却→半开探针恢复）；与手动 `integrator pause` 互补不替代 | CAND 候选库 |
| Q18 | **internal 未接线如何修**（§12.12.1，P1）？ | **施工，P0** | create_provider 补 `internal` 分支（一行 elif）+ 修 internal_compute_provider.py L32 docstring 虚标 + 评估 hk_trade_calendar 自 2026-08 月度刷新失败是否造成日历缺口（known_data_gaps 补登记）+ 登记新 ARCH 条目（internal 接线 + docstring 虚标治理）；代码修复越界未做，转 P0 缺口登记 | CAND 候选库（P0） |

### 16.3 裁定暂缓/维持/不做

| # | 问题 | 裁定 | 理由 | 重评条件 |
|---|---|---|---|---|
| Q2 | **edb_data 替代方案**：iFind 不续费时，是否用 akshare 宏观 + 东方财富宏观 + 国家统计局爬虫拼凑 104 个宏观指标？ | **不做，维持 accepted 缺口** | ① akshare macro_data（291K 行）已覆盖核心指标（CPI/PPI/GDP/PMI/货币供应）；② 多源拼凑口径漂移风险大于收益——不同源同一指标口径不一致比缺数据更危险；③ ROI 存疑：104 指标中实际进因子的不足 20 个 | 宏观因子研究实证需要 EDB 特有指标（某指标 IC 显著且无法替代）时，按需单点补 |
| Q3 | **audit_opinion / rights_issue / MSCI 调整**：低频事件数据，是否值得找替代源？（ROI 评估） | **暂缓，维持 disabled** | 低频事件（审计意见年度、配股低频）无当下消费方；26 号事件驱动策略未施工到需要这些数据阶段；MSCI 调整走 #ARCH-SPECIAL-DAYS 治理（Q13）不单开爬虫 | 26 号事件驱动策略施工到需要 audit_opinion/rights_issue 因子时 |
| Q11 | **调度优先级是否动态化**？根据 fetch_perf api_status 排序。 | **暂缓** | 当前静态排序（tasks.yaml 顺序）够用——日终窗口约 2h 完成，无瓶颈；动态排序引入运行时复杂度（排序算法+状态依赖），收益不明显 | 日终窗口总耗时翻倍（>4h）或 slow/rate_limited 任务频繁挤占窗口时 |
| Q19 | **akshare money_flow/equity_pledge 替代源**（§12.3）：tushare 有 moneyflow/pledge 但需积分。 | **评估 tushare 积分，不经济则 accepted** | money_flow：先验证 fallback 链实效（miniqmt 实时快照已兜底部分场景）+ 评估 tushare 积分成本；equity_pledge：低频数据（季度级）影响面有限，tushare 积分不经济则登记 accepted 缺口 | tushare 积分评估完成且成本可接受时启用；若积分不经济，money_flow 转 miniqmt 实时快照 + tick 数据反推 |
| Q20 | **daily_valuation rate_limited 是否优化**（§12.3）？已 Event.wait(1s)/股 限流。 | **暂缓** | 百度 API 空响应率 15% 是源端固有限制非我方问题；维持 1s/股限流，全量走周末窗口；终极解是 local_valuation 本地估值（Q14 保留项落地后 daily_valuation 外部依赖降级） | local_valuation 实现后 daily_valuation 外部依赖降级 |
| Q21 | **adj_factor 全量回算是否优化**（§12.4）？如改用 akshare/tushare 复权数据反推复权因子。 | **暂缓** | 增量模式每日只拉近期可接受；全量回算走周末 16h 窗口可跑完；复权因子是交易核心数据，换源反推有口径一致性风险——宁慢勿错（风险优先原则） | 全量回算频率提升到周级别以上时 |
| Q22 | **iwencai 爬虫/国家统计局爬虫/券商场内数据**（§12.10）。 | **暂缓** | iwencai：akshare 已包装够用，若 iFind 续费则恢复；统计局：macro_data（akshare）已覆盖核心指标；券商场内/L2：同 Q4 费用项待人拍板 | iFind 续费（iwencai 恢复）/ 24 号打板策略施工到需 L2 阶段（券商场内） |
| Q23 | **任务级 SLA 监控 / 跨源并发优化**（§12.7）。 | **暂缓** | SLA：L11 巡检 + 任务失败告警已兜底，分钟级 SLA 个人项目过度工程；并发：default 8 / heavy 2 线程当前无瓶颈，再细化收益有限 | 日终窗口完成时间成为痛点时 |
| Q24 | **跨源验证扩展 / 数据血缘 / PIT 一致性巡检**（§12.9）。 | **暂缓** | 跨源验证：tick 场景 QMT vs TDX 已覆盖，离线 per-field 对账（2%/3% 容差）维护成本与收益不成正比；数据血缘：无溯源需求场景，fetch_perf 已记 source+capability；PIT 巡检：PIT 铁律由 15 号数据特征层承载，数据下载层不重复建设 | 数据质量问题出现且 fetch_perf 无法定位时（血缘）；关键表出现脏数据污染下游时（跨源验证扩展） |
| Q25 | **守护与自启 7 项**（§12.11）：死人开关通道冗余 / HA 探针含数据集成器 / 心跳阈值调参 / ch_health_probe 频率 / 三冗余 Watchdog / 年度健康报告 / RSSHub 故障传播。 | **维持现状 / 已覆盖** | 死人开关：飞书 webhook 3 个月零故障，通道冗余收益有限；HA 探针：scheduler/tick_subscriber/ch_health_probe 已纳入 SYSTEMS 列表（2026-08-12 实证）；心跳阈值：当前零误报，盘中/盘后差异化无显著收益；ch_health_probe：3s 负载可忽略；三冗余 Watchdog：四层防御已治本，三冗余锦上添花；年度报告：接口就绪但无 review 机制；RSSHub：已纳入 HA 探针 | 飞书 webhook 故障导致告警丢失时（通道冗余）；HA review 机制建立时（年度报告启用） |
| Q26 | **研究知识源智能去重 / 相关性预筛**（§12.13）。 | **登记候选，非 MVP** | 智能去重：复用 §6.10.1 news_dedup 标题 MD5 模式扩展到跨源；相关性预筛：知识源特有需求（交易数据全量落库，知识源量大噪声多需预筛），待 BM-RES-06 LLM 研究 Agent 上线时一并评估 | BM-RES-06 LLM 研究 Agent 上线时 |

> **裁定统计**：待人拍板 2 项（Q1/Q4）+ 裁定施工 14 项（Q5-Q10/Q12-Q18）+ 裁定暂缓/维持/不做 19 项（Q2/Q3/Q11/Q19-Q26 + §12.8 WAL 常态化已闭合无需登记）= 35 项全覆盖。

## 17. 引用

### 17.1 本目录设计备忘

- [00_index_trading_decision.md](00_index_trading_decision.md)——总索引与路线图
- [01_design_memo_management_spec.md](01_design_memo_management_spec.md)——设计备忘管理规范（§4.4 spec 类结构原则）
- [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)——G01 数据与特征层规范（互补：15 号偏"数据进来后怎么用"，本文偏"数据怎么进来"）
- [17_special_trading_days_data_assets.md](17_special_trading_days_data_assets.md)——特殊交易日数据资产（ARCH-SPECIAL-DAYS 未登记编号）
- [18_cold_archive_build_plan.md](18_cold_archive_build_plan.md)——冷归档施工计划（数据保留 Cold 层）
- [19_northbound_hold_snapshot.md](19_northbound_hold_snapshot.md)——北向季度快照 fetcher（日频断档替代）
- [63_data_utilization_audit.md](63_data_utilization_audit.md)——数据利用审计（配套：63 号审"用得怎么样"，本文审"下得怎么样"）

### 17.2 模块蓝图（what 层真源）

- [data_source_integrator_blueprint.md](../../../03_modules/_domain_data/data_source_integrator_blueprint.md)——MOD-L00-004 数据源集成器蓝图（what 层真源，本文补 why）
- [blueprint.md](../../../03_modules/_domain_data/blueprint.md)——MOD-L00-001 Datasource Core 蓝图（v4.0.4，Provider 部分已移交 004）
- [data_source_operation_manual.md](../../../03_modules/_domain_data/data_source_operation_manual.md)——MOD-L00-002 数据源 API 操作唯一真源
- [boot_autostart_architecture.md](../../../03_modules/_domain_data/boot_autostart_architecture.md)——开机自启架构
- [redundant_source_blueprint.md](../../../03_modules/_domain_data/redundant_source_blueprint.md)——冗余数据源蓝图
- [wal_codec_blueprint.md](../../../03_modules/_domain_data/wal_codec_blueprint.md)——WAL 编解码蓝图
- [_domain_mkt_data/](../../../03_modules/_domain_mkt_data/)——行情数据域 6 子模块蓝图（autoload/connectors/failover/raw_data_cache/vendor_base/vendor_registry）

### 17.3 域架构与数据流

- [11_d_data.md](../../../02_enterprise_architecture/02_domain_architecture_docs/11_d_data.md)——D_DATA 域 183 模块清单
- [data_inventory.md](../../../02_enterprise_architecture/05_dataflow_architecture/data_inventory.md)——业务数据现状（ClickHouse 实时扫描）
- [data_acquisition_requirements.yaml](../../../02_enterprise_architecture/05_dataflow_architecture/data_acquisition_requirements.yaml)——数据获取需求 P0-P3

### 17.4 代码真源（depgraph path）

- `src/zephyr/data/provider_base.py`——IngestProviderBase + FetchPayload + FetchResult + IngestProviderMeta + CapabilityContract
- `src/zephyr/data/implementations/*_provider.py`——15 个 Provider 实现
- `src/zephyr/data/scheduler.py`——APScheduler 调度编排
- `src/zephyr/data/config/tasks.yaml`——154 采集任务清单（真源，2026-08-12 实测）
- `src/zephyr/data/config/schedule.yaml`——15 个调度时段条目（真源，含 L0 集合竞价 + L2.5 板块 + L3.5 慢新闻 + L10.5 每日补下载）
- `architecture_model/data/data_sources_registry.yaml`——12 数据源元数据 + policy（真源）

### 17.5 架构裁定

- #ARCH-IFIND-FAILOVER——iFind 试用到期降级（§4.3）
- #ARCH-CH-001——ch_writer 逐个写入是 CH 不稳定根因（§7.2）
- #ARCH-CH-002——引擎统一 ReplacingMergeTree（§7.1）
- #ARCH-CH-003——BufferedWriter 批量聚合层（§7.2）
- #ARCH-CH-004——100% AI 开发模式需蓝图约束运行时门禁（§7.6.2 / §10.9）
- #ARCH-CH-005——ch_writer 混合传输（clickhouse-driver TCP + HTTP，§7.3）
- #ARCH-CH-007——ch_reader 统一读取层 FINAL 注入（§7.6.2 / §10.14 CH-FINAL-GATE）
- #ARCH-CH-009——CH version 列语义误用阻断（§10.14 CH-VERSION-COL）
- #ARCH-CH-010/013——Hyper-V 迁移 + 主动 WAL + local_replay 兜底（§7.3 / §7.7.1 / §7.8）
- #ARCH-CH-017/019——ch_config 连接配置单真源（§7.6.1）
- #ARCH-CH-021——PIT 查询（§8.6）
- #ARCH-CH-022——CapabilityContract 机器可执行契约（§5.2 / §5.8）
- #ARCH-CH-024——business_data_categories.yaml 表名 SSoT 消费层（§5.6）
- #ARCH-CH-029——known_data_gaps 已知历史缺口注册表（§8.7）
- #ARCH-BOOT-001——四层防御 Watchdog（OS层/Guard层/单实例层/心跳健康层，2026-08-07 resolved，§10.6；含 launch_hidden.vbs 无闪窗启动器 §10.11）
- #ARCH-BOOT-002——战略补强（D.心跳原子写 / E.死人开关告警 / F.WaitForExit 根因文档化，2026-08-08 落地，§10.7）
- #ARCH-DATA-001——hk_trade_calendar 数据源错配修复（§4 / project_memory；⚠️ 止血切换目标 internal 未接线，见 §12.12.1）
- #ARCH-DATA-002——capability-API 语义对齐校验机制（#ARCH-DATA-001 系统性治本，§5.2 语义边界 / §12.12.4）
- #ARCH-DATA-SYMBOL-001/002——symbol 标准化 TRAE-082（§5.5）
- #ARCH-DATA-TICK-GAP-001——L10.5 每日盘后补下载当天补（§6.2）
- #ARCH-DATA-014——L2 行情权限缺失降级（§12.2）
- #ARCH-REALTIME-ACCUM——时间敏感型数据每日积累（§4.1 qweather）
- ARCH-SPECIAL-DAYS——特殊交易日数据资产（§12.2 / §12.6；v1.4.0 已裁定补登记正式 ARCH 条目，见 §16.2 Q13；registry 登记落地后恢复 # 前缀引用）
- #ARCH-EDB-EXPAND——EDB 国际宏观数据扩展（§12.1）
- #ARCH-RSS-INVESTING-403-001——news_dedup 显式 region/language + RSS 5xx 重试（§5.1 / §6.10.1）
- #ARCH-066——capability_lookup 强制门禁 bypass 白名单（§10.14 CAPABILITY-LOOKUP-REQUIRED）
- #ARCH-FORCE-MERGE-DEDUP-001——CloneGuard 语义克隆检测硬阻断（§10.14 CAPABILITY-OVERLAP）

## 18. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 1.0.0 | 初稿 | 用户要求新建专门聊"数据集成下载/数据下载/数据源"的设计备忘录，把项目里所有已施工落盘的数据源/下载相关内容全面写入，作为讨论升级载体。6x 段位 64 号（1x 地基层 10-19 已满，数据下载是跨切基础设施归 6x 跨切治理层，与 63 号数据利用审计配套）。spec 工程详设类，§3-§10 按数据获取管线 8 对象分节，§12 缺口与升级方向作为全面升级讨论载体（12 项待裁定 + 12 个开放问题）|
| 2026-08-10 | 1.1.0 | §10 大幅扩展守护与自启配套 + §11.1/§12.11/§17.5/§18 联动 | 用户指出"还有健康守护器啊，自启动等等很多配套"，初稿 §10.5 开机自启仅一段引用过薄。扩展为 §10.5-§10.9 六子节：开机自启架构（7 项第一性原理约束 + 5 个 Task Scheduler 任务）+ 四层防御 Watchdog（#ARCH-BOOT-001 resolved，含 2026-08-07 intraday 停摆 2 日事故根因 + 端到端验证）+ 死人开关告警（#ARCH-BOOT-002 战略补强 E，.ps1 而非 .py 防 Python 栈崩溃连坐）+ 系统级健康监控（HealthAggregator 12 系统三态探针 + ch_health_probe 独立探针 + 三冗余 Watchdog MOD-INF-015）+ 不变式测试防回退（8 项钉死）。§11.1 代码清单补守护文件，§12.11 补守护升级方向 7 项，§17.5 引用补 #ARCH-BOOT-001/002，frontmatter related_issues 补两项 |
| 2026-08-10 | 1.2.0 | 全配套模块补全：§5.6-§5.10 治理消费层 + §6.7-§6.10 业务下载器 + §7.8-§7.11 写入/连接/缓存 + §8.7 历史缺口 + §9.2 冗余源机制 + §10.11-§10.13 启动/可观测 + §11.1/§11.2/§17.4/§17.5 联动 | 用户要求"把所有相关的，所有，是所有的配套全部补进去"。对照 src/zephyr/data/ 50+ 文件盘点，补全 v1.1 仍遗漏的配套模块：§5.6 table_registry 表名 SSoT 消费层（#ARCH-CH-024）/ §5.7 policy_registry per-source 策略注册表 / §5.8 capability_validator 能力校验器 / §5.9 error_classifier 错误分类器 / §5.10 satellite_geospatial_engine 域包入口 + CTR 契约声明；§6.2 调度时段修正为真实 13 档（补 L2.5 板块层 + L10.5 每日补下载层）/ §6.7 trading_calendar 交易日历守卫 / §6.8 板块三件套（sector_kline_downloader + sector_ranking_engine 5因子排名 + sector_snapshot_collector 混合模式）/ §6.9 kline_resampler DB内合成 / §6.10 新闻采集去重（news_dedup 标题MD5 + news_collector PIT 查询）；§7.8 wal_writer 主动 WAL（与 BufferedWriter 区别 + 容量背压）/ §7.9 wal_codec magic number 路由 / §7.10 database_service 统一连接管理 / §7.11 tick_redis_cache H1 热缓存双写 CP-01；§8.1 quality_gate re-export 真源关系补 / §8.7 known_data_gaps.yaml 历史缺口注册表（#ARCH-CH-029）；§9.2 redundant_source 4 组件机制展开（HeartbeatMonitor + SourceSwitcher 防抖 + BackupTickPoller + RecoveryManager 回灌）；§10.10 CLI 补 get_integrator + speed-test / §10.11 launch_hidden.vbs 无闪窗（控制台 vs GUI 子系统）/ §10.12 register_guard_tasks 幂等注册（NEVER Unregister+Register + Parallel/IgnoreNew 有意非对称）/ §10.13 metrics_server Prometheus HTTP 端点:9925；§11.1 代码清单重写覆盖 50+ 文件（补 __init__/__main__/ch_config/ch_reader/local_replay/pit_query/speed_tester/symbol_normalizer/codec_registry/sqlite_fallback/satellite_geospatial_engine/database_service/metrics/metrics_server）/ §11.2 配置清单补 known_data_gaps.yaml + tasks.yaml 字段结构表；§17.4 schedule 13 档 / §17.5 架构裁定补 #ARCH-CH-007/010/013/017/019/021/024/029 + #ARCH-BOOT-001（无闪窗） + #ARCH-DATA-SYMBOL-001/002 + #ARCH-DATA-TICK-GAP-001 + #ARCH-RSS-INVESTING-403-001 共 13 项 |
| 2026-08-10 | 1.2.1 | 核对补全遗漏配套：§10.14 commit_gates 门禁 + §11.4 消费者层 + §11.5 测试清单 + §11.2 路径修正 | 用户质询"都写进去了吗？"触发诚实核对——用 rg 扫描发现 v1.2.0 仍有 4 类遗漏：(1) §10.14 commit_gates 防回退门禁层完全未写（9 个数据相关门禁：CH-BATCH-SIZE/CH-FINAL-GATE/CH-VERSION-COL/TABLE-NAME-REGISTRY/CAP-CONSISTENCY/NO-BARE-SQL/CAPABILITY-LOOKUP-REQUIRED/CAPABILITY-OVERLAP/DATA-TASK-COMPLETENESS，pre-commit 静态检测 §5-§9 设计决策防 AI 回退）；(2) §11.4 数据消费者层未列（regime/regime_feature_builder + runtime/intraday_main 直接消费 zephyr.data，接口变更 MUST 评估影响）；(3) §11.5 验证层测试清单未列（tests/zephyr/data/ 25 单元测试 + tests/data/ 13 治理测试 + tests/governance/commit_gates/ 8 门禁测试 + tests/scripts/ 2 守护不变式测试）；(4) §11.2 business_data_categories.yaml 表名 SSoT 真源路径未列（docs/03_modules/_cross_layer/database/，98 品类）。§17.5 补 #ARCH-CH-009/#ARCH-066/#ARCH-FORCE-MERGE-DEDUP-001 三项门禁裁定。教训：不能凭印象说"全覆盖"，须用 rg/Get-ChildItem 实际扫描核对 |
| 2026-08-12 | 1.3.0 | 架构审查全量事实核对修订（7 轮审查：现状盘点/内容回填/缺失环节/2026-08 最新研究/过度工程/一致性/规范性） | 架构审查 AI 按工作清单全量核对代码/配置/注册表实证，纠偏 17 处：①数字漂移——§2.1 文件数 48→63（rg 实测）、任务数 130+→154、§6.2 调度 13 档→15 时段条目（补 L0 集合竞价高频 + L3.5 慢新闻两行，§2.1/§3/§6.1/§12.7/§14.1 五处联动）、§8.7 known_data_gaps 2 条→7 条（补 6 缺口类型 + accepted/resolved 终态）、§11.2 同步；②代码实证纠偏——§5.3 fred/eia"VPN 探测跳过"误述（实际仅 rss_provider 有 _is_vpn_ready）、§4.1/§4.2 tickflow 港股能力误列（仅 kline_us_daily/us_index）、§8.4 cross_source_validator 例子错误（tick 专属 QMT vs TDX 非日K 通用）、§8.5 source_health_check"结合 fetch_perf 退化"误述（实际不读 fetch_perf 不自动禁用）、§10.4 fetch_perf"scheduler 被动记录"误述（零引用，speed_tester 单通道）、§5.4 铁律表述补实现细节（table 路由默认分支）；③配置实证——§4.3 iFind 降级 7 类→9 任务精确化、§9.1 补 fallback 覆盖率 68.2%（105/154）+ 死 fallback 35 处警告（qmt/exchange/bdpan/local_valuation 无 Provider 实现）、§12.2 disabled 11→10（msci_adjustment_refresh 从未在 tasks.yaml 登记，移回 §12.6 缺口）、§9.2/§10.14/§17.4 残余计数同步；④状态更新——§12.1 #ARCH-EDB-EXPAND 已落地（fred 3/eia 2 任务启用，国际宏观闭合，edb_data accepted 由 macro_data 兜底）；⑤新发现登记——§12.12 新增 4 项（P1 internal 未接线 create_provider 致 #ARCH-DATA-001 止血断裂 + P2 死 fallback + P2 自动熔断缺失对标 2026 circuit breaker 实践 + P3 #ARCH-DATA-002 语义契约边界衔接）、§16 开放问题补 13-18 共 6 项（含 SPECIAL-DAYS 悬空编号、CapabilityContract 三闲置字段裁剪）；⑥过度工程审查 6 项判定全通过（15 Provider/四字段契约/15 时段/known_data_gaps/tick 专属校验/DATA-002 五项均不过度，实证依据记入 §5.2/§6.2/§8.4）；⑦frontmatter related_issues 补 #ARCH-DATA-002，§17.5 同步。外部研究锚点：akshare v1.18.84（2026-08-10）活跃维护印证"上游 break 常态化"设计前提；ClickHouse 官方 batch 10k-100k 行/≤1 insert/s 与 BufferedWriter 50k行/30s 对齐。status 保持 draft——§12.12.1 P1 缺口修复 + §16 共 18 项开放问题收敛后再升 active。【编辑插曲：本轮修订写入后三次遭并发会话 git 操作回退（共享主工作区 index 被 reset/checkout 波及），全部内容按上下文记录完整重放并立即 git add + claim 保护——印证 #ARCH-GIT-CLEAN-GUARD-FIX 教训与 GitCommitGateway 存在意义】 |
| 2026-08-12 | 1.3.1 | 作战地图全覆盖补丁——BM-RES-11 / BM-RES-11-A。新增 §12.13 研究知识源扩展方向：研究知识源（研报/新闻/公告/财报/社交/另类/论文库）接入时按 §5.7 per-source 策略对象模式扩展（新源=Provider+registry 元数据+SourcePolicy 三件套，复用现有配额/重试/fallback 机制，不新建采集框架）；6 类源分类按"一源一 policy"登记、调度复用 §6 15 时段条目模式；智能去重/相关性预筛登记候选（复用 §6.10.1 news_dedup MD5 模式扩展跨源；预筛待 BM-RES-06 LLM 研究 Agent 上线一并评估）；降级路径对齐作战地图登记（主源失效切备用源/调度超限降级 QPS）。补定位→裁定（理由+重评条件）→契约→边界四层 |
| 2026-08-13 | 1.4.0 | **定稿转 active**：§12 全部缺口/升级方向 + §16 全部开放问题逐项裁定收敛（35 项全覆盖） | AI-DSD-001 定稿会话逐项裁定：①§16 重写为三表结构——§16.1 待人拍板费用项 2 项（Q1 iFind 续费默认建议暂不续费/Q4 L2 开通默认建议暂不开通，费用支出最终拍板权在用户）；§16.2 裁定施工 14 项（Q18 internal 接线修复 P0/Q8 data parts 监控 P1/Q17 per-source 自动熔断器 P1/Q5 北向快照 P1/Q6 冷归档 P2/Q16 fetch_perf 被动记录 P2/Q14 死 fallback 清理 28 处/Q13 SPECIAL-DAYS 补登记 ARCH 条目等，登记 CAND 候选库或转施工队列）；§16.3 裁定暂缓/维持/不做 19 项（Q2 EDB 拼凑不做维持 accepted/Q3 低频事件暂缓/Q11 调度动态化暂缓/Q19 tushare 积分评估/Q20-Q26 等，均附理由+重评条件）；②§12 各小节"待裁定" checkbox 全部回填裁定结论+指向 §16 真源（防内容漂移）；③§15 待裁定表与 §16.3 合并同源；④§14.2 演进路径更新为 v1.4.0 施工清单（短期 Q18/Q8/Q17/Q14/Q13，中期 Q5/Q6/Q16，长期费用项+暂缓项）；⑤frontmatter status draft→active、version 1.3.1→1.4.0，ARCH-SPECIAL-DAYS 注记更新为"已裁定补登记"；⑥裁定原则：费用项不越权（待人拍板+默认建议）、技术项按证据裁定（项目约束：MVP/风险优先/避免过度工程/先测量后优化）、暂缓项全部带重评条件（非永久禁止） |
| 2026-08-14 | 1.4.1 | 压缩精简：噪音去除+施工细节梳理，零信息丢失审查通过（AI-DOCS-001） | AI-DOCS-001 文档压缩：折叠调研过程叙述与重复解释（§3 ASCII 总览图压为紧凑管线描述、选型对比只留结论、重复 why 去重、§4.3 影响范围/§7.5 表全景/§10.4 实测/§11.5 测试清单压为紧凑单行、§10.5 部署块与 §10.12 去重、§10.6 验证明细表压为一行、§12.12.2 处置选项讨论并入裁定），35 项裁定（Q1-Q26）与 §16 三表逐条完整保留，15 源/154 任务/15 时段清单、费用裁定、落库/韧性规则、#ARCH/BM 锚点与跨文档链接全部保留；章节标题与编号一字未动 |
| 2026-08-15 | 1.4.2 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08） | ① §17.5 #ARCH-BOOT-001 重复行合并为一条（含 §10.6 + §10.11 双指针）；② §9.1 死 fallback 逐源计数去重（真源=§16.2 Q14）；③ §12.12.2 同项计数去重留指针；④ §1 状态 cell 精简（保留 35 项裁定 2/14/19 口径）；35 项裁定 Q1-Q26 与 §16 三表逐条零丢失，数据源/调度/落库规则/#ARCH/BM 锚点/跨文档链接零丢失；章节标题与编号一字未动 |
