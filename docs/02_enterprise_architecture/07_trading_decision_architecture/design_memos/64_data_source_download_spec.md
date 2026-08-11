---
ttl: permanent
doc_type: architecture_view
title: 数据源与下载体系规范
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "1.2.1"
date: 2026-08-10
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
  - "#ARCH-REALTIME-ACCUM（时间敏感型数据每日积累）"
  - "#ARCH-DATA-014（L2 行情权限缺失降级）"
  - "#ARCH-SPECIAL-DAYS（特殊交易日数据资产）"
  - "#ARCH-EDB-EXPAND（EDB 国际宏观数据扩展）"
---

# 数据源与下载体系规范

> **性质**：spec / 工程详设。记录数据源与下载体系（D_DATA 域·数据获取基础设施）已施工基础设施的 why。
> 本目录文档种类适配见 [01_design_memo_management_spec](01_design_memo_management_spec.md) §4.4——spec 类按对象内在结构组织，本文 §3-§10 决策按数据获取管线的 8 个对象分节。
>
> **与现有文档关系**：
> - **接管 why 层** [data_source_integrator_blueprint.md](../../03_modules/_domain_data/data_source_integrator_blueprint.md)（MOD-L00-004 数据源集成器蓝图——what 层真源，本文补 why）
> - **引用** [data_source_operation_manual.md](../../03_modules/_domain_data/data_source_operation_manual.md)（MOD-L00-002 数据源 API 操作唯一真源——"怎么调用+参数坑"）
> - **互补不重叠** [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)（G01 数据与特征层规范——15 号偏"数据进来后怎么用"PIT/特征仓库/因子工程，本文偏"数据怎么进来"Provider/调度/落库/韧性）
> - **引用** [11_d_data.md](../../02_enterprise_architecture/02_domain_architecture_docs/11_d_data.md)（D_DATA 域 183 模块清单）
> - **配套** [63_data_utilization_audit.md](63_data_utilization_audit.md)（数据利用审计——63 号审"数据用得怎么样"，本文审"数据下得怎么样"）
> - **引用** [data_inventory.md](../../02_enterprise_architecture/05_dataflow_architecture/data_inventory.md) + [data_acquisition_requirements.yaml](../../02_enterprise_architecture/05_dataflow_architecture/data_acquisition_requirements.yaml)（业务数据现状 + 数据获取需求 P0-P3）

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G29 数据源与下载体系（跨切治理层·6x 段位） |
| 所属 | 跨作战地图 01-12（数据是所有业务层的地基） |
| 依赖 | 无（最底层基础设施） |
| 对标 | WorldQuant 数据管线 / Numerai 数据接入 / 机构数据中台（Tushare/Wind/iFinD 商业化方案） |
| 正交性 | ✅ 与 regime/alpha/组合/风控/执行全部正交——纯数据基础设施 |
| 优先级 | P0（地基，但已大规模施工——本文是已施工设施的 why 回填 + 全面升级讨论载体） |
| 状态 | 🟧 draft v1.2.1（v1.2 全配套模块补全 + v1.2.1 核对补全遗漏：§10.14 commit_gates 防回退门禁 9 项 + §11.4 数据消费者层 + §11.5 验证层测试清单 48 项 + §11.2 路径修正；经 rg 实际扫描核对 src/zephyr/data/ 63 文件 + commit_gates 9 门禁 + tests 48 测试 + 消费者层全覆盖；§12 缺口与升级方向待人讨论定夺） |

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是 A 股量化交易系统（miniQMT，T+1，不能做空），个人 + 100% AI 开发。数据获取基础设施已大规模施工：

- **代码层**：`src/zephyr/data/` 约 48 个文件，含 Provider 抽象 + 15 个数据源实现 + 调度编排 + 质量门控 + 落库 + 韧性容灾全链路。
- **配置层**：`tasks.yaml` 约 130+ 采集任务（远超早期 61 个，已扩展到期权/可转债/港股/美股/生猪/天气/特殊交易日/技术指标等）；`schedule.yaml` 11 档调度时段；`data_sources_registry.yaml` 12 个数据源元数据 + policy 字段。
- **落库层**：ClickHouse 三库 `c1_market`（行情/资金/宏观/静态约 80 表）+ `c3_fundamental`（基本面/新闻/股东约 22 表）+ `c0_meta`（fetch_perf 性能记录）。
- **文档层**：`_domain_data/` 7 篇 + `_domain_mkt_data/` 6 篇 + `11_d_data.md`（D_DATA 域 183 模块）+ `05_dataflow_architecture/`（data_inventory + data_acquisition_requirements）。

但此前只有 what 层文档（蓝图、操作手册、域清单），缺少 why 层——未来 AI 看到当前 Provider 抽象/调度编排/落库引擎/韧性机制设计，不知道为什么是这样，"优化"成另一个样子，飘移发生。本备忘补这个 why，并以 §12 缺口与升级方向作为全面升级的讨论载体。

### 2.2 核心问题

1. **15 个数据源特性差异极大如何统一管理**：iFind 配额制/miniQMT 单线程+进程依赖/AKShare 60RPM+断 VPN/baostock 线程局部登录/tushare token 积分/tickflow 限流/tdx bestip/rss SSL……每个源限流/重试/反爬/登录刷新策略完全不同，不能一个装饰器统一。
2. **130+ 任务如何调度不冲突不遗漏**：盘中实时/盘后日K/夜间财务/周末校准/月初静态等多频次混排，miniQMT 非交易日连不上、iFind 配额耗尽、AKShare 反爬封锁等运行时故障常态。
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
外部数据源（15 个）                Provider 抽象层                策略注册表
miniQMT/iFind/AKShare ──→  IngestProviderBase      ──→  SourcePolicy
baostock/tushare/tickflow     (connect/health_check/      (RPM/重试/退避/
tdx/tqcenter/cls               fetch/disconnect)           反爬/登录刷新)
eastmoney_news/rss/eia                                      ↓
fred/qweather/internal_compute                    CapabilityContract
                                                  (机器可执行契约 #ARCH-CH-022)
                                                          ↓
                          ↓
调度编排层（APScheduler 11 档时段）         落库层（ClickHouse）
scheduler.py ──→ task_queue(DAG) ──→  BufferedWriter(攒批≥50000行/30s)
              ↓                          ↓
         error_classifier               ch_writer(混合传输: driver TCP + WSL)
         (不可恢复→立即fallback          ├─ c1_market（行情/资金/宏观/静态 ~80表）
          可恢复→重试用完fallback)       ├─ c3_fundamental（基本面/新闻/股东 ~22表）
              ↓                          └─ c0_meta.fetch_perf（性能记录）
         fallback_sources                ↑
         (主源→副源列表)                 ReplacingMergeTree(统一引擎 #ARCH-CH-002)
                                          ↑
                          ↓              幂等: 直接INSERT+CH后台去重
数据韧性三层机制                   ←──── 8 个 MergeTree 表写前 DELETE
§1 fallback（主源→副源）                  ↑
§2 全表补下载（L10 周一02:00）      integrity_checker(L11 每日23:00巡检)
§3 完整性巡检（L11 每日23:00）      backfill_checker(L10 动态发现全表)
§4 新增表门禁（DATA-TASK-COMPLETENESS warn级）
                          ↓
                    进度/告警/监控
                    progress_store(SQLite 断点续传)
                    alerter(日志+failures/+钉钉/邮件)
                    metrics(Prometheus 文本格式)
                    source_health_check / fetch_perf
```

**设计要点（why）**：
- **Provider 只拉数据不写库**：职责单一，写入由上层 scheduler 统一负责（避免 15 个 Provider 各写各的写入逻辑）。
- **策略作为参数传入 fetch**：限流/重试由基类 `call_with_policy` 公共化，子类不重复实现（Stage 4 公共化，避免 15 份重复代码）。
- **fetch 返回 Iterator[FetchResult]**：支持分批，每批一个 FetchResult，大表可流式下载不爆内存。
- **CapabilityContract 机器可执行契约**：把"注释契约"升级为 scheduler 启动时校验的机器契约（#ARCH-CH-022），不一致 fail-closed 阻断启动——100% AI 开发模式下不能靠 AI 自觉读注释。

## 4. 数据源全景

### 4.1 15 个数据源分类

| 类别 | 数据源 | source_name | 认证 | 线程安全 | 核心能力 | 状态 |
|---|---|---|---|---|---|---|
| **实盘行情** | miniQMT | miniqmt | 三要素+进程 | single_thread | 日K/分钟K/Tick/期权Greeks/板块/港股/美股 | ✅ 主力 |
| 实盘行情 | XtMiniQmt.exe | qmt | 同上 | single_thread | QMT 占位任务（多数 disabled） | 🟧 占位 |
| **商业基本面** | iFind | ifind | license_key | thread_local | 估值/EDB/iwencai/RealtimeQuotes | 🔴 试用到期降级 |
| **免费行情** | AKShare | akshare | anonymous | shared(60RPM) | 分红/质押/解禁/宏观/股东/涨跌停/生猪 | ✅ 主力（ifind 降级后承接） |
| 免费行情 | baostock | baostock | anonymous | thread_local | K线/财务/交易日历/指数成分（滞后1周） | ✅ fallback |
| 免费行情 | tushare | tushare | token | shared(200RPM) | 行业分类/新闻（积分制） | ✅ 升主源（ifind 降级） |
| **板块专用** | tqcenter | tqcenter | 需通达信进程 | single_thread | 880xxx 板块K线/成分股/实时快照 | ✅ 2026-07-30 升自动调度 |
| 板块专用 | mootdx/TDX | tdx | bestip | shared | 880xxx 板块分钟K线（TCP 直连盘中实时） | ✅ |
| **新闻舆情** | 财联社 | cls | 无 | shared | 财联社电报（HTTP 直连） | ✅ |
| 新闻舆情 | 东方财富 | eastmoney_news | 无 | shared | 7x24 快讯（HTTP 直连） | ✅ |
| 新闻舆情 | RSS | rss | 无 | shared | 36氪/钛媒体/华尔街见闻等 8 源 | ✅ |
| **海外数据** | TickFlow | tickflow | 无 | shared(60RPM) | 美股/港股 K线 | ✅ |
| 海外数据 | FRED | fred | API_KEY | shared | 美国宏观（GDP/CPI/失业率/国债/原油/黄金/VIX） | ✅ 2026-08-04 新增 |
| 海外数据 | EIA | eia | API_KEY | shared | 能源（石油库存/价格/天然气） | ✅ 2026-08-04 新增 |
| **另类数据** | 和风天气 | qweather | API_KEY | shared | 40 城市实时+7天预报（免费版无历史） | ✅ 每日积累 |
| 内部计算 | InternalCompute | internal | 无 | shared | 技术指标/日历事件/港股日历（本地算非外拉） | ✅ Phase 1+2 完成 |

### 4.2 数据源能力矩阵（关键能力 × 数据源）

> 完整矩阵真源：`architecture_model/data/data_sources_registry.yaml`（12 个数据源元数据 + policy JSONB）+ `src/zephyr/data/config/tasks.yaml`（130+ 任务的路由表）

| 能力 | miniqmt | ifind | akshare | baostock | tushare | tdx | tqcenter | tickflow | cls/em/rss | fred/eia | qweather | internal |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 日K线 | ✅主 | fallback | fallback | fallback | — | — | — | — | — | — | — | — |
| 分钟K线 | ✅主 | — | — | — | — | — | — | — | — | — | — | — |
| 后复权 | ✅主 | fallback | fallback | — | — | — | — | — | — | — | — | — |
| Tick | ✅主 | — | — | — | — | — | — | — | — | — | — | — |
| 板块880 | — | fallback | — | — | — | ✅分钟 | ✅日K | — | — | — | — | — |
| 期权/Greeks | ✅主 | fallback | fallback | — | — | — | — | — | — | — | — | — |
| 期货 | ✅主 | — | fallback | — | — | — | — | — | — | — | — | — |
| 港股 | ✅主 | — | fallback | — | — | — | — | ✅主 | — | — | — | — |
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

**影响范围**（tasks.yaml 中标记 `#ARCH-IFIND-FAILOVER` 的任务）：
- `daily_valuation_incremental/full`（估值 PE/PB/PS/PCF）→ akshare 主源
- `money_flow_incremental/full`（资金流向）→ akshare 主源
- `industry_class_refresh`（申万行业分类）→ tushare 主源
- `industry_class_suppl_refresh`（申万/中证行业分类补充）→ tushare 主源
- `concept_sector_refresh`（概念板块列表）→ akshare 主源
- `realtime_snapshot_incremental`（实时行情快照）→ akshare 主源
- `sector_meta_refresh`（板块信息）→ akshare 主源

**设计决策（why）**：
- **不硬编码主源**：tasks.yaml 的 `source` 字段可热切换，`fallback_sources` 列表保留 ifind——续费后改回 source=ifind 即可恢复，无需改代码。
- **降级不丢能力**：所有原 ifind 能力都有 akshare/tushare fallback 覆盖，数据连续性不受影响。
- **EDB 例外**：`edb_data_incremental` 无 fallback（iFind EDB 配额耗尽 -4318，5万条/月不够拉 104 个宏观指标全历史），该任务 disabled，待 iFind 付费版或替代源。

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
1. **Provider 只拉数据返回 list[tuple]，不写 ClickHouse**——职责单一，写入由上层 scheduler 统一负责。若 Provider 内部写库，15 个 Provider 各写各的写入逻辑，维护噩梦。
2. **fetch 返回 Iterator[FetchResult] 支持分批**——大表（如 kline_1min 130万行/日）可流式下载不爆内存，每批一个 FetchResult 含 columns/rows/last_key。
3. **策略作为参数传入 fetch，由基类 `call_with_policy` 公共化**——限流/重试逻辑不每个子类重写，Stage 4 公共化后 15 个 Provider 共享同一套策略应用代码。
4. **异常时返回 FetchResult(error=...) 而非抛出**——让上层 scheduler 决定重试/fallback/告警，Provider 不自作主张。
5. **`_http_get` 纳入 `_call_with_policy` 重试循环**（#ARCH-RSS-INVESTING-403-001）——5xx 瞬时错误重试，4xx WAF 拦截立即抛出不浪费重试。

### 5.2 CapabilityContract 机器可执行契约（#ARCH-CH-022）

**问题**：原 `capabilities=["kline_daily", ...]` 是字符串列表，只是注释契约——AI 写 task 声明 `capability: kline_daily` 但 Provider 实际没实现该能力时，运行时才报错。

**裁定**：升级为 `CapabilityContract` 机器可执行契约，scheduler 启动时校验 task 声明与 provider 实现一致性，不一致 fail-closed 阻断启动。

```python
@dataclass
class CapabilityContract:
    capability_id: str                    # "top10_shareholders"
    supports_symbols_null: bool = False   # symbols=None 时是否自动获取全市场（#ARCH-CH-018）
    supports_incremental: bool = True     # 是否支持增量模式
    supports_full_refresh: bool = True    # 是否支持全量刷新
    requires_date_range: bool = True      # 是否需要 start/end 日期（宏观数据可能不需要）
```

**why**：100% AI 开发模式下不能靠 AI 自觉读注释——AI 写 task 时可能声明 Provider 没有的能力，机器契约启动时拦截，防止运行时才发现的错配。

### 5.3 15 个 Provider 实现清单

| Provider | 文件 | 核心能力 | 关键设计点 |
|---|---|---|---|
| IFindProvider | ifind_provider.py | THS_RQ/THS_BD/iwencai/EDB/RealtimeQuotes | 月度配额监控(-4318/-4309)；试用到期降级 |
| MiniQmtIngestProvider | miniqmt_provider.py | 行情/财务/板块/期权Greeks/港股/美股 | single_thread+进程依赖；非交易日跳过(trading_day_only) |
| AkshareIngestProvider | akshare_provider.py | 分红/质押/解禁/宏观/股东/涨跌停/生猪/板块 | 60RPM 限流；断 VPN；东财反爬 3 次跳过 |
| BaostockProvider | baostock_provider.py | K线/财务/交易日历/指数成分 | thread_local（每线程独立 bs.login）；数据滞后1周 |
| TushareProvider | tushare_provider.py | 行业分类/新闻 | token 积分制；新闻 API 已废弃(disabled) |
| TickFlowProvider | tickflow_provider.py | 美股/港股 K线 | 60RPM 限流 |
| TDXProvider | tdx_provider.py | 880xxx 板块分钟K线 | mootdx TCP 直连盘中实时；bestip 自动选最快 |
| TqcenterProvider | tqcenter_provider.py | 880xxx 板块日K/成分股/快照 | 需通达信进程；2026-07-30 升自动调度 |
| ClsProvider | cls_provider.py | 财联社电报 | HTTP 直连 cls.cn/nodeapi |
| EastmoneyNewsProvider | eastmoney_news_provider.py | 东方财富7x24快讯 | HTTP 直连 np-listapi.eastmoney.com |
| RssProvider | rss_provider.py | 36氪/钛媒体/华尔街见闻等8源 | feedparser；偶发 SSL 重试；尊重 robots.txt |
| FredProvider | fred_provider.py | 美国宏观(22序列) | FRED_API_KEY；VPN 探测关闭时跳过 |
| EiaProvider | eia_provider.py | 能源(石油/天然气) | EIA_API_KEY |
| QweatherProvider | qweather_provider.py | 40城市天气 | 免费版无历史API，每日积累(#ARCH-REALTIME-ACCUM) |
| InternalComputeProvider | internal_compute_provider.py | 技术指标/日历事件/港股日历 | 本地算非外拉；_fetch_xxx 必须真实定义禁止脱节 |

### 5.4 internal_compute_provider 铁律

> **project_memory 硬约束**：internal_compute_provider 中所有引用的 `_fetch_xxx` 方法必须在类体内真实定义，禁止声明与实现脱节导致 AttributeError。

**why**：internal_compute 是唯一"不拉外部数据、本地计算"的 Provider（技术指标/日历事件/港股日历），其 `_fetch_xxx` 方法是计算入口。AI 增加新能力时可能只在 capabilities 声明却忘了实现 fetch 方法，运行时 AttributeError。该铁律强制声明与实现一一对应。

### 5.5 symbol 标准化（symbol_normalizer/）

**真源**：`src/zephyr/data/symbol_normalizer/normalizer.py`（TRAE-082 symbol 约定铁律，#ARCH-DATA-SYMBOL-001/002）

**职责**：纯函数无副作用，幂等（已带后缀原样返回），空输入→空输出，未知前缀→exchange=None（不擅自推断）。

**A 股裸码→exchange 映射**：
- 首位 6/5/9→SH（沪市股票/基金/B股）
- 首位 0/3/1/2→SZ（深市股票/创业板/基金/B股，1.1.0 补 '2'→SZ 深市 B 股 200xxx/201xxx 实测 281K 行）
- 首位 8/4→BJ（北交所/老三板）
- 3 位前缀消歧：900-903→SH B股 / 920→BJ 北交所 / 110/113→可转债
- 支持 SH/SZ/BJ/HK/US 五交易所

**why**：不同数据源 symbol 格式不统一（akshare `600519` vs miniqmt `600519.SH` vs baostock `sh.600519`），统一标准化后才能跨源对比和落库去重。这是跨源验证（§8.4）和数据落库去重的前置依赖。

### 5.6 表名注册表消费层 table_registry（#ARCH-CH-024）

**真源**：`src/zephyr/data/table_registry.py`（MOD-GOV-table_registry）

**问题**：`business_data_categories.yaml` 是业务数据品类唯一真源（声明态规则数据，含 98 条品类记录），但改造前 0 行代码消费它——所有 provider/scheduler 直接硬编码表名字符串，与 tasks.yaml 形成双真源。长期漂移必然发生（改名只改一处，另一处遗忘）。

**裁定**（#ARCH-CH-024 第一性原理根因）：SSoT 真源已建立声明闭环（YAML 存在），但消费闭环未建立（代码不 import 真源）。表名属于声明态规则数据（trae_062 SSoT 分类铁律：表名是 schema 声明而非 DB 实例），真源是 YAML。

**治本**：
- `business_data_categories.yaml` 是表名/品类唯一真源
- 代码 MUST 通过 `TableRegistry.table(category_id)` 派生表名，**禁止硬编码字符串**
- 启动时加载 YAML，构建 `category_id → "{database}.{table}"` 映射
- `validate_tasks_yaml()` 校验 tasks.yaml.table ⊆ registry，不一致仅 WARN（渐进式收紧；Phase 4 commit gate 将升级为 block）

**公共接口**：
- `TableRegistry.table(category_id) -> str`：返回全限定表名（查不到抛 KeyError，fail-closed 禁止凭记忆编表名）
- `TableRegistry.all_tables() -> list[str]`：所有已注册全限定表名
- `TableRegistry.is_registered(table) -> bool`
- `TableRegistry.validate_tasks_yaml(tasks) -> list[str]`
- `get_registry() -> TableRegistry`：单例（幂等加载）

**why KeyError 而非返回默认**：查不到表名说明 registry 与代码脱节，fail-closed 立即暴露；若返回默认值则静默漂移，违背 SSoT 初衷。

**消费现状**：scheduler._load_config() 末尾调用 validate_tasks_yaml() WARN 校验；news_dedup/sector_kline_downloader 等通过 `get_registry().table()` 派生表名（Phase 5 长期方向：240 处硬编码表名逐步替换为 TableRegistry.table() 常量引用）。

### 5.7 策略注册表 policy_registry（per-source 调用策略）

**真源**：`src/zephyr/data/policy_registry.py`（MOD-GOV-policy_registry）

**职责**：每个数据源有自己的限流/重试/反爬/登录刷新策略，集中管理、yaml 热更新。策略参数来源：`data_source_operation_manual.md`（MOD-L00-002）中每个数据源的限流/防爬/登录方式描述，已固化为 `config/policies.yaml`（派生物，真源在 `data_sources_registry.yaml` 的 policy 字段）。

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

**PolicyRegistry 特性**：从 yaml 加载，支持 `maybe_reload` 热更新（运行时改 policies.yaml 无需重启）；`get_policy` 未知源返回默认策略（DEFAULT_POLICIES fallback），不抛异常。

**why per-source 策略对象而非统一装饰器**：15 个源特性差异极大（iFind 配额制/miniQMT 单线程/AKShare 60RPM+断 VPN/baostock 线程局部登录），统一装饰器无法表达这些差异，必须 per-source 策略对象。

### 5.8 能力校验器 capability_validator（CapabilityContract 执行者）

**真源**：`src/zephyr/data/capability_validator.py`（MOD-GOV-capability_validator）

**职责**：§5.2 定义的 CapabilityContract 契约由本模块在 scheduler 启动时校验——把"注释契约"升级为"机器可执行契约"的实际执行者。

**校验规则**：
1. `task.capability` 必须在 `provider.meta.capability_contracts` 中（按 capability_id 匹配）——不存在 → **ERROR（阻断启动）**
2. `task.symbols=null` 时，对应 capability 应声明 `supports_symbols_null=True`——`False` → **WARN**（不阻断，渐进式收紧；向后兼容字符串声明）
3. `task.incremental=true` 时，对应 capability 应声明 `supports_incremental=True`——`False` → **WARN**

**Violation 数据类**：`severity`（ERROR/WARN）+ `message` + `task_id` + `capability_id`。`validate_task_capability_contracts(tasks, providers)` 返回 Violation 列表，空列表=通过。

**设计原则**（遵循裁定#221）：
- 不新增 .md 规则文档，转化为启动时校验（reconciler 式）
- 初期 WARN-only 收集数据，逐步收紧为 ERROR（渐进式治理）
- 100% AI 开发模式下，只有机器可执行契约才能达到 ~100% 遵守率

**why ERROR/WARN 分级而非全 ERROR**：supports_symbols_null=False 的历史 task 太多，一次性全阻断会瘫痪启动；先 WARN 收集数据，逐步补声明后再收紧为 ERROR。

### 5.9 错误分类器 error_classifier（可恢复性判断）

**真源**：`src/zephyr/data/error_classifier.py`（MOD-GOV-error_classifier，stable）

**职责**：根据 FetchResult.error 字符串判断可恢复性，驱动 §9.1 fallback 决策（不可恢复立即 fallback / 可恢复重试用完 fallback / 未知当可恢复给重试机会）。

**纯字符串匹配无副作用**，预编译正则，覆盖 iFind/akshare/QMT 常见错误：

| 分类 | 关键词模式 | 处置 |
|---|---|---|
| **unrecoverable**（不可恢复） | `-4318`(iFind 配额) / `-4309`(接口废弃) / 配额/quota/deprecated/认证失败/401/403/未授权/license/`has no attribute`(akshare API 漂移) / `xtquant SDK 导入失败` | 立即 fallback |
| **recoverable**（可恢复） | Timeout/ConnectionError/RemoteDisconnected/HTTPError/JSONDecodeError/503/502/`miniQMT 已断开`/`行情服务不可用` | 重试用完 fallback |
| **unknown**（未知） | 匹配失败 | 当可恢复（给重试机会） |

**why 关键词匹配而非异常类型**：FetchResult.error 是字符串（跨 Provider 统一接口），无法用 isinstance 判断异常类型（§13 已述）。

**why 未知当可恢复**：保守策略——给重试机会比立即 fallback 更安全（立即 fallback 可能不必要地切换到较弱的副源）。

### 5.10 数据源接入层包入口 satellite_geospatial_engine

**真源**：`src/zephyr/data/satellite_geospatial_engine/__init__.py`（MOD-L00-001，D_DATA 域）

**职责**：D_DATA 数据接入层的域级包入口，re-export `IngestProviderBase` + `IngestProviderMeta`（provider_base）与 `DataQualityGate`（gov_enforcement.rule_enforcement.quality_gate）。

**CTR 契约依赖声明**（承重墙标记）：
- 作为生产者：CTR-001 NormalizedMarketData → D_FACTOR/D_SIGNAL/D_RESEARCH；CTR-TRACE-001 TraceContext（链头，trace_id 由本层创建）；CTR-ERR-001 DataQualityError → D_FACTOR
- 作为消费者：CTR-BP-001~003 Backpressure ← D_FACTOR（背压信号：暂停/降速/恢复数据推送）

**why 独立包入口**：D_DATA 是 LPC 双轨架构 C 轨（业务脊柱），域级包入口集中声明跨层契约依赖，ContractImpactAnalyzer 评估修改影响时的入口点。

## 6. 调度编排层

### 6.1 为什么用 APScheduler 而非 OS 级触发器

**决策**：采用 APScheduler 常驻进程（BackgroundScheduler + ThreadPoolExecutor），而非 Windows 任务计划/cron。

**why**：
- OS 级触发器无任务依赖/并发控制/重试编排能力——130+ 任务有 DAG 依赖（adj_factor→kline_daily_hfq→kline_weekly_hfq），OS 触发器无法表达。
- APScheduler 支持 `coalesce`（错过多次只跑一次）+ `max_instances=1`（同任务不并发）+ `misfire_grace_time`（错过1小时内补跑）。
- per-source 串行/跨源并行需要线程池分流：`default` 池 8 线程给可并行源，`heavy` 池 2 线程给串行源（iFind/miniQMT）。

### 6.2 13 档调度时段（schedule.yaml 真源）

> schedule.yaml 真实档位为 13 档（含 L2.5 板块层 + L10.5 每日补下载层），非早期 9/11 档。

| 时段 | cron | executor | 典型任务 | 说明 |
|---|---|---|---|---|
| L1 盘中实时 | */5 9-15 周一-五 | realtime(4线程) | tick_data/index_quote/auction/futures_position/kline_hk | 盘中高频轮询，独占 realtime 算力 |
| L2 盘中分钟K | */5 9-15 周一-五 | intraday_minute(4线程) | kline_1min~60min + ETF/LOF 分钟K | 盘中分钟滚动 |
| L2.5 盘中板块K线 | */5 9-15 周一-五 | intraday_sector(独立) | 880xxx 板块分钟K线（mootdx TCP 直连） | 独立执行器，避免被 miniqmt 全市场分钟K线慢任务（~5000股）阻塞 |
| L3 事件驱动 | */3 7×24 | default(8线程) | news_data/macro_data | 来了就处理；盘中提速到 */3（盘中实时分析需新闻尽快入库） |
| L4 盘后日K | 30 16 周一-五 | heavy(2线程) | kline_daily/hfq/adj_factor/index/valuation/周月K | 日频核心先跑 |
| L5 盘后资金 | 00 18 周一-五 | default | margin/block_trade/dragon_tiger/money_flow/futures/us | 资金面+外盘 |
| L6 盘后事件 | 00 19 周一-五 | default | analyst_forecast/dividend/disclosure_plan | 事件类 |
| L7 夜间财务 | 00 22 周一-五 | heavy | balance_sheet/income/cashflow/financial_indicator/shareholders | 低频财务 |
| L8 周末校准 | 00 3 周一 | heavy | 全量校准/TDX板块/概念板块/美股全量 | 原周六改周一(QMT周末连不上) |
| L9 月初静态 | 00 9 1 * * | default | stock_list/index_list/trade_calendar/etf_list | 月度刷新 |
| L10 周末补下载 | 00 2 周一 | heavy | tick_data补下载+全表缺失检测 | 动态发现tasks.yaml全表，回看7天 |
| L10.5 每日盘后补下载 | 盘后 | default | 当日缺口检测+自动补下载 | 治本#ARCH-DATA-TICK-GAP-001，当天发现当天补（不依赖 L10 周末窗口） |
| L11 完整性巡检 | 00 23 周一-五 | default | integrity_check_daily | 全表达标检测 |

**why L2.5 独立执行器**：miniqmt 全市场分钟K线（~5000 股）是慢任务，若与板块K线共用 intraday_minute 执行器，板块K线会被阻塞。mootdx TCP 直连获取 880xxx 板块分钟K线是独立通道（不走 miniqmt），独立执行器避免互相阻塞。

**why L10.5 当天补**：L10 周末补下载回看7天，但 tick_data 当日缺口若等到周末才补，期间回测/策略已用错数据。L10.5 盘后立即检测当日缺口当天补，#ARCH-DATA-TICK-GAP-001 治本。

### 6.3 miniQMT 交易日约束（2026-07-19 裁定）

**问题**：QMT 服务器周末/节假日关闭登录服务（error 10061 WSAECONNREFUSED），miniqmt 任务非交易日触发必然失败。

**裁定**：
1. `TRADING_DAY_GUARDED_SCHEDULES` 覆盖 L1/L2/L4/L5/L6/L7/L11 共 8 个时段，scheduler 非交易日自动跳过。
2. L8 改周一 03:00（原周六 02:00），确保周末后首个工作日 QMT 可用。
3. L9 不在守卫列表（含 ifind/akshare 任务需周末/月初跑），但 miniqmt 源任务必须标 `extra.trading_day_only: true`，由 `_filter_schedule_tasks` 非交易日过滤。
4. `cli run <task_id>` 手动触发绕过守卫，用户自判时机。

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

**why**：依赖通过 `task_queue.py` DAG 管理，前置未完成则当前任务 PENDING。避免 adj_factor 没下载完就跑 kline_daily_hfq 导致复权错算。

### 6.5 失败重试与告警

- **任务级重试**：Provider 内部按 SourcePolicy 重试（瞬时错误）。
- **数据源 fallback**：主源失败后自动尝试副源（§9.1）。
- **调度级重跑**：DEAD 任务进 `failures/` 目录，CLI `integrator rerun-failed` 一键重跑。
- **L10 周末补下载**：周一 02:00 自动检测过去7天全表缺失并补下载（不依赖 last_key）。
- **L11 每日巡检**：每天 23:00 盘后全表达标检测，不达标告警。
- **告警触发**：任务 DEAD/主源 fallback/单日失败率>5%/某源连续3天失败/iFind -4318/L11 巡检不达标。

### 6.6 Tick 订阅独立常驻进程（tick_subscriber.py）

**真源**：`src/zephyr/data/tick_subscriber.py`（MOD-L00-001，#ARCH-CH-013）

**职责**：QMT 实时 Tick 订阅服务——subscribe_quote 实时推送，写入 ClickHouse tick_data。**独立常驻进程，不走 scheduler cron**。

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

**设计要点**：
- **QMT callback 线程只做 queue.put_nowait**（最小开销，不阻塞 QMT 行情推送）
- **flush 线程批量出队**（500 条）构造单个 FetchResult 交 WalWriter
- **WalWriter 先落盘段文件再异步 drain 到 CH**（P0-1 主动 WAL，CH 不可达时不丢 tick）
- **15 字段**：trade_date/timestamp/recorded_time/symbol/market_type/price/volume/amount/direction/data_source/bid_price/ask_price/bid_volume/ask_volume/quality_flag
- **P1-5 metrics 埋点**：received/written/dropped/queue_size
- **P2-5 分阶段延迟 Histogram**：Stage1 on_tick / Stage2 queue_wait / Stage3 convert / Stage4 wal_add / Stage5 wal_flush
- **无锁计数**：CPython GIL 保证 int += 1 统计精度足够

**启动**：`python -m zephyr.data.tick_subscriber`，由 `ZephyrAlpha_TickSubscriber` Task Scheduler 任务守护（§10.5）。

**why 独立进程而非 scheduler 任务**：tick 数据是实时推送（subscribe_quote callback）非轮询，不能走 scheduler cron；独立进程避免 tick 高频回调阻塞 scheduler 其他任务；独立心跳监控（§10.6 四层防御）确保 tick_subscriber 崩溃自愈。

### 6.7 交易日历守卫 trading_calendar

**真源**：`src/zephyr/data/trading_calendar.py`（MOD-GOV-trading_calendar，stable）

**职责**：基于 `exchange_calendars` 包的 XSHG（上交所）日历精确判断每个交易日（含节假日/调休），纯 Python 本地计算不依赖网络/DB。scheduler 在盘中/盘后时段触发前调用 `is_trading_day()`，非交易日自动跳过。

**XSHG 日历单例缓存**：exchange_calendars 加载较慢，`_get_xshg_calendar()` 懒加载 + 单例缓存避免重复初始化。

**回退策略**：exchange_calendars 未安装时降级为 weekday 判断（周一~周五），保证 scheduler 不因依赖缺失而崩溃。`is_trading_day` 永不抛异常。

**TRADING_DAY_GUARDED_SCHEDULES**（需交易日历守卫的时段）：
- L1 intraday_realtime / L2 intraday_minute / L4 daily_kline / L5 daily_capital / L6 daily_event / L7 nightly_financial / L10.5 daily_backfill / L11 integrity_check / L0 auction_highfreq
- **不需守卫**：L3 event_driven（7×24）/ L8 weekend_calibration / L9 monthly_static / L10 weekend_backfill（这些时段含非交易日需运行的任务）

**why exchange_calendars 而非自建日历表**：exchange_calendars 是成熟开源库，含历年节假日/调休数据，自建易遗漏调休（如 2024 年春节调休）。XSHG 即上交所日历，与 A 股交易日完全对齐。

### 6.8 板块三件套（sector_kline_downloader / sector_ranking_engine / sector_snapshot_collector）

> 880xxx 申万板块指数数据的下载/排名/快照采集三个独立常驻模块，均 `python -m` 手动启动，task_bound TTL。

#### 6.8.1 sector_kline_downloader——板块K线下载器

**真源**：`src/zephyr/data/sector_kline_downloader.py`

**职责**：盘后从 tqcenter 下载 880xxx 板块指数K线（1d/1m/5m 三周期）写入 ClickHouse `kline_sector_880` 表。50 只/批分批下载避免 tqcenter 超时。ReplacingMergeTree 幂等写入。

**约束**：tqcenter 仅支持 1d/1m/5m，15m/30m/60m 不被直接支持，需 §6.9 kline_resampler 从 1m/5m 合成。

#### 6.8.2 sector_ranking_engine——板块动态排名引擎

**真源**：`src/zephyr/data/sector_ranking_engine.py`

**职责**：5 因子复合排名动态调整 99 只推送池，每日盘前重算一次。

**5 因子复合排名**（权重之和=1.0）：
1. 成交额 amount **30%**——板块活跃度
2. 涨跌幅绝对值 **25%**——板块波动
3. 主动交投量（outside+inside）**20%**——交投活跃度（volume 恒为 0 的替代方案）
4. 5分钟动量 **15%**——短期动量
5. 板块-大盘强弱差 **10%**——相对强度

**大盘基准**：880001.SH（上证指数），缺失时用全板块涨跌幅均值。百分位排名消除量纲差异。

**回退**：sector_snapshot 表无数据时回退到成分股数量 Top99。

#### 6.8.3 sector_snapshot_collector——板块实时快照采集器

**真源**：`src/zephyr/data/sector_snapshot_collector.py`

**职责**：方案 C 混合模式采集 880xxx 板块实时快照（99 只推送 + 全量轮询 30 秒）写入 `sector_snapshot` 表。

**混合模式架构**：
1. **推送层**：`subscribe_hq` 订阅核心 99 只（由 §6.8.2 ranking_engine 动态选取），~18 秒/次推送通知
2. **轮询层**：`get_market_snapshot` 每 30 秒轮询全量 582 只（实测 2026-07-22：582 只 = 454 个 880xxx + 128 个 881xxx，非设计时估算的 584）
3. 收到推送通知或轮询触发时，调 `get_market_snapshot` 取 26 字段写入 ClickHouse

**why 混合模式而非纯推送/纯轮询**：纯推送只覆盖 99 只核心板块，全量 582 只需轮询补全；纯轮询 30 秒延迟对核心板块太高。混合模式核心板块推送低延迟 + 全量板块轮询兜底。

### 6.9 K线合成器 kline_resampler

**真源**：`src/zephyr/data/kline_resampler.py`

**职责**：从 `kline_sector_880` 表的 1m/5m 数据合成 15m/30m/60m K线写入同表（ClickHouse `toStartOfInterval` 聚合在 DB 内完成，避免数据搬运）。

**合成规则**（标准 OHLC 聚合）：
- open = `argMin(open, timestamp)`——窗口内第一条K线开盘价
- high = `max(high)` / low = `min(low)`
- close = `argMax(close, timestamp)`——窗口内最后一条K线收盘价
- volume = `sum(volume)` / amount = `sum(amount)`

**幂等**：DELETE + INSERT（按 period + trade_date 范围先删后插），盘后批量执行。

**why DB 内合成而非拉到 Python 聚合**：板块K线数据量大（582 板块 × 多周期 × 多日），拉到 Python 聚合是数据搬运浪费；ClickHouse `toStartOfInterval` + `argMin/argMax` 在 DB 内完成，利用 CH 列式聚合优势。

### 6.10 新闻采集去重（news_collector / news_dedup）

#### 6.10.1 news_dedup——新闻去重模块

**真源**：`src/zephyr/data/news_dedup.py`（MOD-GOV-news_dedup）

**职责**：基于标题 MD5 哈希对新闻数据查重去重。不同新闻源（AKShare/财联社/东方财富/RSS）获取的内容可能重复，需基于标题去重避免同一条新闻被多源重复写入 `fund_news_data` 表。

**机制**：
- 查询 ClickHouse 中最近 N 天（`_DEDUP_WINDOW_DAYS=7`）已有新闻的标题哈希集合
- 过滤掉已存在的标题哈希 + 同一批次内重复标题
- **fail-open**：去重异常时跳过去重返回原始数据（不阻断写入）

**NEWS_DATA_COLUMNS 标准列**：news_id/publish_time/title/content/summary/source/source_url/data_source/region/language。#ARCH-RSS-INVESTING-403-001：显式写入 region/language，避免海外新闻被表 DEFAULT 误标 CN/zh。

**why 标题 MD5 而非内容哈希**：标题是新闻唯一性最强的字段，内容可能因源不同有编辑差异；MD5 计算快且定长。

#### 6.10.2 news_collector——新闻数据采集器

**真源**：`src/zephyr/data/news_collector.py`（MOD-DATA-NEWS-001，design 阶段）

**职责**：从 ClickHouse `fund_news_data` 表按条件查询新闻返回标准列 DataFrame，供 P1-E3 NLP 管道（评估集构建、批量推理）使用。复用 `ch_reader.query()` + `regime_data_loader.parse_tsv`，不重复造 TSV 解析轮子。

**PIT 严格**：`publish_time <= end_date`，不泄漏未来新闻（与 §8.6 pit_query 的 PIT 铁律对齐）。

**why 查询器独立于下载器**：news_dedup 是写入端去重（scheduler 调用），news_collector 是读取端查询（NLP 管道调用），职责分离——下载层只管下，消费层按需查。

## 7. 落库体系

### 7.1 ClickHouse 引擎统一裁定（#ARCH-CH-002）

**原设计**：全部 MergeTree + 先删后插，理由"数据源唯一不需要去重"。

**实际事故**（2026-07-09）：5204 只股票逐个写入时，"先删后插"= 5204 次 ALTER DELETE mutation + 5204 次 INSERT = 双倍 data parts，CH CPU 352% merge 满载崩溃，kline_1min 1039 parts / kline_daily 788 parts。

**裁定**：废弃"全部 MergeTree + 先删后插"，统一 `ReplacingMergeTree` + 直接 INSERT，CH 后台去重，零 mutation 开销。

**8 个例外**（c3_fundamental 的 MergeTree 遗留表）：share_unlock/restricted_shares/analyst_forecast/disclosure_plan/equity_pledge_detail/rights_issue/share_change/industry_class_suppl——scheduler.run_task 对这些表写前执行 `DELETE WHERE toDate(date_col) IN (start..end)` 保证幂等，date_col 从 tasks.yaml 读取（禁止硬编码）。

### 7.2 BufferedWriter 批量聚合层（#ARCH-CH-003）

**问题**：ch_writer 逐个 FetchResult = 1 次 INSERT，5204 只股票 = 5204 个 data parts，违反 CH 官方"每秒≤1次INSERT，每次≥1万行"约束。

**裁定**：Provider 和 ch_writer 之间插入 BufferedWriter，攒批写入（按行数 ≥50000 或时间窗口 ≥30 秒触发）。预期 5204 次 INSERT → 1-3 次 INSERT。

### 7.3 ch_writer 混合传输（#ARCH-CH-005）

**裁定**：采用混合传输架构
- `query()` / `delete_where()` → clickhouse-driver TCP（2.9x 查询加速，无类型问题）
- `write_tsv()` → 保留 WSL subprocess TSV（TSV 自动处理类型转换，1.6x 提速不显著）
- clickhouse-driver 不可用时自动降级到 WSL subprocess

**后续变更**（2026-07-16 Hyper-V 迁移，#ARCH-CH-010/013 resolved）：ClickHouse 从 WSL2 迁至 Hyper-V VM（172.24.30.100 固定 IP），`_discover_wsl_ip()` 移除，WSL subprocess fallback 通道移除，统一走 clickhouse-driver TCP 直连。

### 7.4 数据保留铁律（PS-CTR-003）

> **真源**：`data_retention_contract.yaml`（PS-CTR-003 v1.0.0）

1. **所有数据永不删除**——只保留或归档，不 DROP / DELETE / TTL 自动删除
2. **进 Cold 层必须手动触发**——不自动迁移
3. **所有表 Hot 层无 TTL**——ClickHouse 永久保留

**已执行变更**：2026-07-14 删除 `c1_market.index_quote` 表 90 天 TTL（违反铁律 INV-RET-003）。

### 7.5 落库表全景（三库）

**c1_market（行情/资金/宏观/静态 ~80 表）**：
- K线类：kline_daily/kline_daily_hfq/kline_weekly/kline_monthly/kline_weekly_hfq/kline_monthly_hfq/kline_1min~60min/kline_etf_*/kline_lof_*/kline_index/kline_sector/kline_sector_880/kline_sector_intraday/kline_cb/kline_option/kline_hk_daily/kline_hk/kline_us_daily/kline_futures/futures_kline_qmt
- Tick/快照：tick_data/l2_tick/auction_snapshot/auction_book/index_quote/realtime_snapshot
- 复权/估值：adj_factor/daily_valuation/stock_valuation
- 资金面：margin_trading/block_trade/block_trade_detail/dragon_tiger/dragon_tiger_seat/money_flow/hk_connect_flow
- 宏观：macro_data/edb_data
- 衍生品：futures_position/futures_term_structure/option_iv_surface/option_greeks/convertible_bond_iv
- 静态/日历：trade_calendar/hk_trade_calendar/calendar_event/stock_list/index_list/index_constituent/index_weight/index_adjustment/msci_adjustment/industry_class/industry_class_suppl/concept_sector/concept_board/sector_list/sector_meta/sector_constituent/sector_snapshot/convertible_bond_list/etf_list/etf_nav/etf_benchmark/lof_list/hk_stock_list/st_stock_list/ipo_schedule/margin_target_adjustment
- 另类：hog_spot_index/hog_futures_core/hog_province_spot/weather_data/stock_hot_rank/limit_up_down/technical_indicator/us_index

**c3_fundamental（基本面/新闻/股东 ~22 表）**：
- 新闻：news_data（多源统一表，含 cls/em/rss/akshare/tushare）
- 财务：balance_sheet/income_statement/cashflow_statement/financial_indicator/main_business
- 股东/事件：shareholder_count/analyst_forecast/earnings_forecast/express_report/audit_opinion/dividend/rights_issue/share_unlock/restricted_shares/share_change/equity_pledge_detail/equity_pledge_summary/top10_shareholders/top10_circulating_shareholders/disclosure_plan/repurchase/research_report

**c0_meta（元数据）**：fetch_perf（Capability 实测性能记录，source+capability+test_date ORDER BY，api_status 枚举 ok/slow/rate_limited/blocked/broken/pending）

### 7.6 CH 配置与读取层

#### 7.6.1 ch_config.py——连接配置单真源（#ARCH-CH-017 / #ARCH-CH-019）

**问题**：Hyper-V 迁移前，ch_writer.py 用 `os.environ.get("CLICKHOUSE_HOST", "172.24.30.100")` 硬编码默认值，database_service.py 用 `"localhost"` 默认值，两者不一致且都不主动加载 `config/.env.clickhouse`。当前能工作纯属硬编码默认值巧合等于 .env.clickhouse 的值，CH 再迁移一次就会暴露。

**裁定**：
- `config/.env.clickhouse` 是 CH 连接配置**唯一真源**
- 所有 CH 连接入口必须主动读取该文件，**禁止硬编码 IP 默认值**
- `ensure_ch_env_loaded()`：幂等加载 .env.clickhouse 到 os.environ（文件不存在 log warning 不抛）
- `load_ch_config()`：返回连接配置字典，读不到**抛 CHConfigError（fail-closed）**

#### 7.6.2 ch_reader.py——统一读取层（#ARCH-CH-007）

**问题**：#ARCH-CH-002 统一 ReplacingMergeTree + 直接 INSERT，但去重是异步的（后台 merge 时才去重），merge 完成前查询返回重复行。100% AI 开发模式下 AI 不会主动在查询中加 FINAL（#ARCH-CH-004 教训）。

**方案**：统一读取层自动注入 FINAL 关键字：
- `inject_final(sql)`：纯函数，对 SQL 中的 ReplacingMergeTree 表自动注入 FINAL
- `query(sql)`：执行查询（自动注入 FINAL），返回 TSV 字符串
- `count(table, where)`：计数查询（自动注入 FINAL），返回 int
- `query_table(table, columns, where, ...)`：便捷表查询

**why 统一读取层**：消除对 AI 自觉加 FINAL 的依赖——任何查询走 ch_reader 自动去重，不走 ch_reader 的裸查询是 bug。

### 7.7 本地落盘兜底与回灌

#### 7.7.1 local_replay.py——本地 TSV 兜底+自动回灌（#ARCH-CH-013 Phase 1）

**问题**：CH 二级降级链（TCP→HTTP）全部失败时（VM/CH 不可达），ch_writer.write_tsv 要么抛异常导致任务失败，要么丢弃数据。

**方案**：CH 不可达时写本地 TSV 文件而非丢弃，scheduler 启动时 + 每 30 分钟回灌积压。

**文件布局**：
```
data/local_fallback/
    _manifest.jsonl              # 每行一条 JSON：{table, cols_clause, file, rows, ts}
    c1_market__kline_daily/
        20260715_103723_abc123.tsv
    c3_fundamental__news_data/
        20260715_103723_def456.tsv
```

**回灌策略**：读 _manifest.jsonl → 按 table 分组 → 逐文件 ch_writer.write_tsv 回灌 → 成功删除文件+移除 manifest 条目 → 失败保留等下次重试。回灌用 manifest 保存的 cols_clause（不重新查表列防列数不匹配），传 `create_fallback=False` 防重复落盘。

**不变式**：本地落盘文件原子写入（先写 .tmp 再 rename）；manifest 追加模式（JSONL）；save_fallback 永不抛异常（写入失败 log+返回 False）。

#### 7.7.2 sqlite_fallback.py——CH 降级到本地 SQLite（MOD-L00-005）

**职责**：CH 不可达时写本地 SQLite（INSERT OR REPLACE 幂等），查询层可读最近数据。

**设计**：按 table 创建 SQLite 表（schema 与 CH 对齐，仅保留核心列）；每表最大 500K 行（约 4 小时 tick 数据），FIFO 自动清理；get_pending_batches 返回待回灌数据。线程安全：所有 SQLite 操作通过 _lock 串行化（SQLite 单写者模型）。

**why SQLite 而非只 TSV**：TSV 是文件无法查询，SQLite 支持查询层降级读取（如盘后 CH 挂了但策略层要读最近 tick），是 TSV 兜底的查询层补充。

### 7.8 主动 WAL 写入器 wal_writer（P0-1 Phase A）

**真源**：`src/zephyr/data/wal_writer.py`（MOD-GOV-wal_writer）

**职责**：数据先落本地 WAL 段文件，再由后台 drain 线程异步排空到 ClickHouse。解决实时 tick 写入路径在 CH 慢/不可达时延迟突增的问题。被 §6.6 tick_subscriber 使用。

**与 BufferedWriter 的区别**（关键）：
| 维度 | BufferedWriter | WalWriter |
|---|---|---|
| 路径 | 攒批 → 直接写 CH（失败才降级 local_fallback） | 攒批 → **主动写 local_fallback 段文件** → drain 线程异步回灌 CH |
| 延迟 | 依赖 CH 写入速度 | 本地落盘快，写入路径延迟稳定 |
| CH 慢/不可达 | 阻塞生产者 | 不阻塞生产者（CH 慢只影响 drain 速度） |

**段文件落盘阈值**：每段 ≥ 3000 行或 ≥ 5 秒触发（P0-3 调参：5000→3000 / 10.0→5.0）。

**WAL 容量背压**：WAL 目录上限 2GB——70% warning，**90% critical 背压阻断写入**（`add()` 返回 False，生产者应减速/中断）。防止 CH 长时间不可达时 WAL 段文件无限增长撑爆磁盘。

**drain 线程**：轮询积压段文件回灌 CH，失败指数退避（封顶 60s）不退出；无积压 2s 慢轮询，有积压 0.5s 快速重试。

**复用机制**：
- `local_replay.save_fallback()`：段落盘（原子写 + manifest 追加）
- `local_replay.replay_batch()`：drain 回灌
- `ch_writer._get_table_columns_set()`：列过滤
- `ch_writer.tsv_escape()`：TSV 序列化

**P1-5 metrics 埋点**：segments / wal_dir_bytes / backlog_files / drain_replayed / drain_failed。

**why 主动 WAL 而非 BufferedWriter 失败才降级**：tick 数据是实时推送，CH 写入延迟突增会阻塞 QMT callback 线程导致丢 tick。主动 WAL 把"写 CH"与"接收 tick"解耦——接收即落盘（快），CH 写入异步 drain（不影响接收）。

### 7.9 WAL 编解码注册表 wal_codec/codec_registry

**真源**：`src/zephyr/data/wal_codec/codec_registry.py` + `wal_codec/tsv_codec.py`

**职责**：按 magic number（4 字节前缀）路由到对应编解码器。drain 线程根据段文件 magic 自动选择解码器。

**codec 清单**：
- `TsvCodec`：MAGIC=b""（无前缀），纯文本段文件默认按 TSV 解码——当前唯一实现的 codec
- `_ProtoCodecStub`：MAGIC=b"PB\x01"，Proto 段 P3 远期实现桩，当前 encode/decode 降级到 TSV 并 log warning

**CodecProtocol 协议**：`MAGIC: bytes` + `encode(rows) -> bytes` + `decode(data) -> list[tuple]`。

**get_codec(data)**：遍历 codec 列表，data 以 magic 开头则返回对应 codec；无匹配降级到 TSV（向后兼容）。decode 时 Proto 段需跳过 magic 前缀。

**why magic number 路由而非文件扩展名**：段文件名是时间戳+哈希无扩展名信息；magic 前缀自描述编码格式，drain 线程无需知道段文件用什么 codec 写的。

**why TSV 当前唯一 codec**：TSV 人类可读 + CH 原生支持 TSV 导入 + 序列化简单。Proto codec 是 P3 远期优化（更紧凑+更快解码），当前 TSV 够用。

### 7.10 统一数据库连接管理 database_service（跨域引用）

**真源**：`src/zephyr/infrastructure/database_service.py`（MOD-INF-002，D_INFRA_RUNTIME 域，stable）

**职责**：统一管理 governance.db / depgraph(PostgreSQL) / ClickHouse(c1_market) / Redis(H1) 的连接池、生命周期、健康检查。数据下载层通过本服务获取 CH/Redis 连接。

**部署现状**：
- ClickHouse c1_market 行情仓库 2026-07-01 部署（INFRA-DB-006），`get_clickhouse_conn()` 已实现
- Redis H1 热缓存 2026-08-02 部署——Redis 7.0.15 @ Hyper-V Ubuntu VM（172.24.30.100:6379，与 ClickHouse 同 VM，D1 决策），`get_redis_conn()` 已实现
- market.duckdb（旧 DuckDB 业务时序库）2026-07-05 删除（业务行情数据已迁移至 ClickHouse c1_market）

**why 跨域引用而非数据下载层自管连接**：CH/Redis 连接是基础设施资源，governance/depgraph/数据下载层共用，统一管理避免多处各自维护连接池（连接泄漏/配置漂移）。数据下载层的 `ch_config.py`（§7.6.1）负责 CH 连接配置单真源，`database_service` 负责连接池生命周期，两者分工。

### 7.11 Tick Redis 热缓存双写 tick_redis_cache（H1 CP-01）

**真源**：`src/zephyr/data/tick_redis_cache.py`（MOD-H1_REDIS_HOT，D_INFRA_RUNTIME 域）

**职责**：tick → Redis `tick:{symbol}:latest` 双写器（D-DATA → H1 集成适配器）。tick_subscriber._drain_batch 批量出队时，将 QMT tick dict 转换为 Redis Hash 格式，PIPELINE 批量写入。

**与 WAL 路径的关系**：双写——WAL→ClickHouse 是持久化主路径，Redis 是热读取加速层。Redis 故障时 best-effort 降级——log+返回 0，不阻断 WAL 主路径（CP-02 降级：信号端用上一批因子值）。

**性能**：
- PIPELINE 模式：500 条 tick 单次 RTT 批量 HSET
- 写入频率：每 drain_batch 一次（~500 条/批，tick_subscriber 3 秒周期）
- 延迟：<10ms（CP-01 SLO：Tick→Redis ≤3 秒）

**Hash 字段**：5 档 bid/ask + price/volume/amount/timestamp = 23 字段（`_MAX_LEVELS=5`）。

**why 双写 Redis 而非只写 CH**：盘中策略读 tick 需要低延迟（<3ms），CH 查询延迟（~50ms）无法满足；Redis 内存读取 <1ms。CH 是持久化（回测/盘后分析），Redis 是盘中热读（策略实时决策），两者职责互补。

**why best-effort 不阻断 WAL**：Redis 是加速层，挂了只是盘中策略读不到最新 tick（降级用上一批），但 tick 数据不能丢（WAL 保证持久化）。Redis 故障不应导致 tick 采集中断。

## 8. 数据质量与完整性

### 8.1 质量门控（quality_gate.py）

**真源**：`src/zephyr/data/quality_gate.py` 是 **re-export wrapper**——`QualityReport` / `MarketDataValidator` / `apply_quality_gate` 真源在 `zephyr.gov_enforcement.rule_enforcement.quality_gate`（SSoT: `cross_layer_contracts.yaml` → CTR-ERR-001 DataQualityError）。

**why re-export**：测试通过 `zephyr.data.quality_gate` 导入，但真源在 gov_enforcement 域（质量门禁是跨层契约，非数据下载层私有）。re-export 消除 ModuleNotFoundError 的同时保持 SSoT 单真源——治理域定义质量规则，数据域 re-export 供消费方按域就近导入。

**职责边界**：quality_gate 与下载调度解耦——Provider 只拉数据，质量校验由消费方在读取时调用（不在写入时拦截）。

**why**：写入时拦截会拖慢下载吞吐（5204 只股票逐个校验），且脏数据流入比数据断档危害小（脏数据可事后清洗，断档无法回填）。质量门控放在读取端，按需校验。

### 8.2 完整性巡检（integrity_checker.py · L11）

**流程**（`run_daily_check()`）：
1. 复用 `backfill_checker._discover_backfill_tables()` 动态发现全表
2. 逐表检查当天 `count() WHERE date_col = today()` 是否 ≥ 阈值
3. 不达标的表通过 `alerter.notify()` 告警
4. 结果记录到 progress_store

**阈值设计**：过去7天平均行数×0.5（低于均值50%视为缺失）；无历史数据返回0（跳过巡检，新表首日不报缺失）。

**why 阈值用历史7天日均×0.5 而非固定值**：不同表行数量级差异大（tick_data 2000万 vs macro_data 几十行），固定阈值无法通用。

### 8.3 回补检查（backfill_checker.py · L10）

**动态发现机制**（`_discover_backfill_tables()`）：从 tasks.yaml 动态读取所有非 disabled 任务的表，同表多任务去重。自动推断：
- **日期列名**：`DESCRIBE TABLE` 查 Date 类型列，优先选 trade_date/end_date/report_date/unlock_date/announce_date
- **阈值**：过去7天平均行数×0.5

**补下载执行**（`run_weekend_backfill()`）：
1. 动态发现所有表 → 获取过去7天交易日
2. 逐表检测缺失日期
3. tick_data 用专门 `backfill_tick_data()`（分时段+批量写入）
4. 其他表用 `scheduler.run_task(task_id)` 重跑

### 8.4 跨源验证（cross_source_validator.py）

交叉验证不同数据源数据的一致性（如 miniqmt vs baostock 的日K线对比），用于发现单源数据错误。

### 8.5 数据源健康检查（source_health_check.py）

定期检查数据源状态（health_check 探活），结合 fetch_perf 的 api_status（ok/slow/rate_limited/blocked/broken/pending）做退化决策。

### 8.6 PIT 查询（pit_query.py · #ARCH-CH-021 P0-5）

**真源**：`src/zephyr/data/pit_query.py`

**问题**：c3 财务报表使用 ReplacingMergeTree 覆盖式更新，存在前视偏差风险——同一 report_period 可能有原始公告 + 修正公告多个版本。回测必须只看"当时已公告"的数据（15 号 §3.3 PIT 铁律）。

**方案**：按 announce_date 建立 point-in-time 查询能力，与 backtest 域 pit_manager.py 三公理对齐：

| 数据层 pit_query | 回测层 pit_manager | 语义 |
|---|---|---|
| `as_of()` | `as_of_join()` | 版本对齐：取查询时点可见最新版本 |
| `embargo` 选项 | `apply_embargo()` | 泄漏防护：announce_date 截止回退 |
| `survivorship_universe()` | `check_survivorship_bias()` | 幸存者偏差：PIT 标的池 |

**底层机制**：财务表 ORDER BY (symbol, report_period, announce_date) 保留全部版本（ReplacingMergeTree 按 sort key 去重，announce_date 不同则不合并），故 `LIMIT 1 BY symbol, report_period`（ORDER BY announce_date DESC）可取查询时点已公告的最新版本——这正是 AS OF JOIN 语义。

**约束**：仅查白名单财务表，非白名单抛 PITQueryError；CH 查询失败返回空字符串（同 ch_reader）；表无 period_col 跳过 LIMIT 1 BY。

**why PIT 查询在数据下载层而非回测层**：下载层不仅要把数据下下来，还要保证回测能 PIT 查询——PIT 查询能力依赖下载层的表结构设计（ORDER BY 含 announce_date 保留多版本），是下载层与回测层的契约边界。

### 8.7 已知数据缺口注册表 known_data_gaps.yaml（#ARCH-CH-029）

**真源**：`src/zephyr/data/config/known_data_gaps.yaml`（MOD-GOV_BACKFILL_CHECKER，audit 2.7/3.8 治本，2026-07-23）

**问题**：§8.3 backfill_checker 默认回看 7 天（`_DEFAULT_BACKFILL_DAYS=7`），无法检测超过 7 天的历史缺口。若某表 2 周前断档，backfill_checker 7 天窗口看不到，缺口永久遗留。

**方案**：本注册表登记已知历史缺口，backfill_checker 读取后对已登记缺口使用**全范围回看**（不受 7 天窗口限制）。已登记缺口 backfill 完成后标记 `status=completed`，不再重复检测。

**缺口类型**：
- `date_range`——特定日期范围内行数低于阈值（如 tick_data 2026-06 缺口）
- `empty_table`——整表为空（如 edb_data iFind 配额耗尽）

**已登记缺口**（2026-07-23）：

| id | table | gap_type | 缺口描述 | 状态 |
|---|---|---|---|---|
| `tick_data_2026_06_gap` | c1_market.tick_data | date_range | 2026-06 录制器中断，6月日均 248万行 vs 5月基准 2385万行（89.6% 缺失） | registered |
| `edb_data_ifind_quota_exhausted` | c1_market.edb_data | empty_table | iFind EDB 配额耗尽，表至今 0 行（end_date=null 持续中） | registered |

**状态机**：`registered` → `in_progress` → `completed`。

**触发方式**：`backfill_checker.run_known_gap_backfill()` 读取本注册表，对 status=registered 的缺口触发 QMT 历史数据下载（tick_data）或等待 iFind 配额恢复（edb_data）。

**why 显式登记而非扩大默认窗口**：扩大默认窗口到 30/90 天会让每日 backfill 检查成本暴增（全表扫描 90 天）；显式登记只对已知缺口全范围检测，日常增量检测保持 7 天窗口低成本。这是"日常增量检测"与"已知历史缺口修复"的分工。

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

**run_task fallback 逻辑**：
1. 构造数据源尝试列表：`sources_to_try = [(主源, capability)] + [(副源, capability), ...]`
2. 逐源调用 `_try_source()`
3. **不可恢复错误**（-4318/-4309/配额/接口废弃/认证失败/401/403/license）→ 立即 fallback（跳过重试）
4. **可恢复错误**（Timeout/ConnectionError/RemoteDisconnected/HTTPError/503/502）→ PolicyRegistry 重试用完后 fallback
5. 任一源成功即返回 True，全部失败返回 False

**why 错误分类器用关键词匹配而非异常类型**：FetchResult.error 是字符串（跨 Provider 统一接口），无法用 isinstance 判断异常类型。

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

**SourceState 状态枚举**：ALIVE / DEAD / UNKNOWN。

**HeartbeatStatus 快照**：primary_state + ch_state + last_tick_ts + last_ch_ok_ts + ch_consecutive_failures。

**why 防抖 30s 稳定期**：主源可能短暂恢复又中断（网络抖动），立即切回会导致主备频繁切换（ping-pong）。30s 稳定期确认主源真正恢复后再切回。

**why QMTSourceAdapter.stop()=no-op**：QMT 订阅由 TickSubscriber.start() 管理，切换到备源时不能停 QMT 订阅——保持订阅活跃才能让 HeartbeatMonitor 检测主源恢复触发切回。

**why SQLite 仅写最近 N 小时**：SQLite 是兜底不是持久化（持久化由 WAL+local_replay 负责），SQLite 无限增长会撑爆磁盘。每表 500K 行（约 4 小时 tick）FIFO 自动清理，超过的旧数据由 WAL 段文件保留。

**与 §9.1 fallback 的区别**：§9.1 fallback 是**任务级**主源→副源切换（scheduler.run_task 内，针对 130+ 离线任务）；§9.2 是**进程级**主源→备源热切换（tick_subscriber 内，针对实时 tick 推送，零中断切换）。

### 9.3 WAL 编解码（wal_codec/ + wal_writer.py）

**真源**：`docs/03_modules/_domain_data/wal_codec_blueprint.md`

> 详细机制见 §7.8（wal_writer 主动 WAL 写入器）+ §7.9（wal_codec 编解码注册表）。

`wal_writer.py` 主动 WAL 写入器：数据先落本地段文件再异步 drain 到 CH（P0-1，被 tick_subscriber 使用）；`wal_codec/` 按 magic number 路由编解码器（TsvCodec 当前唯一实现，Proto codec P3 远期桩）。用于 CH 写入失败/慢时的兜底，与 §9.2 SQLiteFallback 互补——WAL 保 tick 持久化，SQLite 保查询层可读。

### 9.4 新增表门禁（DATA-TASK-COMPLETENESS）

**文件**：`gov_enforcement/commit_gates/data_task_completeness_gate.py`（warn 级，priority=80）

**检测逻辑**：
1. 只在 tasks.yaml 被修改时触发
2. `git diff HEAD -- tasks.yaml` 提取新增的 task_id
3. 解析 tasks.yaml 检查新增任务是否配置了 fallback_sources
4. 未配置 → warn（不阻断）+ detail 含 WARN 信息

**why warn 不阻断**：有些表确实无副源（tick_data 只有 miniqmt），硬阻断阻碍开发。warn 出现在 commit 输出形成"AI 增加表 → 门禁提醒 → AI 补充 fallback_sources"闭环。

## 10. 运维与监控

### 10.1 进度与断点续传（progress_store.py）

**统一进度存储**（SQLite `data/integrator_progress.db`）：
- `task_progress`：task_id/source/last_run_at/last_key/last_status/rows_total/error_msg
- `task_runs`：run_id/task_id/started_at/finished_at/status/rows_fetched/rows_written/error_msg

**断点续传协议**：
1. 任务启动 → 查 `task_progress.last_key` → 作为本次 `payload.start`
2. 分批拉取 → 每批写完 CH → 更新 `last_key`
3. 异常中断 → 下次启动从 `last_key` 继续
4. 幂等：CH 写入用 ReplacingMergeTree 直接 INSERT 或 MergeTree 写前 DELETE

**why SQLite 存进度而非 ClickHouse**：进度查询高频但量小，SQLite 单文件部署简单。

### 10.2 告警（alerter.py）

| 通道 | 触发 | 格式 |
|---|---|---|
| 日志 | 所有事件 | 结构化日志 `[time][level][task_id][source] message` |
| 失败汇总文件 | DEAD 任务 | `failures/YYYY-MM-DD.log` |
| 钉钉 Webhook（可选） | DEAD 任务 + 配额告警 | Markdown 卡片 |
| 邮件（可选） | 连续 3 天失败 | 汇总邮件 |

### 10.3 指标（metrics.py）

Prometheus 文本格式 `data/metrics.prom`，可接 Grafana：
- `integrator_task_total{task, status}` Counter
- `integrator_task_duration_seconds{task}` Histogram
- `integrator_rows_fetched_total{task}` Counter
- `integrator_rate_limit_hits_total{source}` Counter
- `integrator_retry_total{source}` Counter
- `integrator_session_uptime_seconds{source}` Gauge

### 10.4 Capability 实测性能（c0_meta.fetch_perf）

**设计动机**：不同 source.capability 下载速度差异巨大（实测从 5066 行/秒到 0.09 只/秒，跨度 5 万倍），仅靠 policy_registry 的预期 RPM 无法反映实际运行情况。

**2026-07-09 首批实测数据**（14 条）：
- miniqmt.kline_daily ok 14.5 行/s
- miniqmt.adj_factor **slow** 0.09只/s（get_divid_factors 每只11秒，全量16h）
- akshare.daily_valuation **rate_limited** 0.17只/s（百度API空响应率15%）
- akshare.margin_trading ok 5066 行/s
- akshare.money_flow **blocked**（东财反爬封锁，已回退 ifind→akshare）
- akshare.equity_pledge **broken**（API 损坏，已回退 ifind）

**派生用法**：调度优先级排序（ok 优先，slow/rate_limited 安排低峰）/ 退化决策（blocked/broken 自动回退）/ 运维告警（error_rate>0.1）/ 容量规划（rows_per_sec×目标行数估耗时）。

**数据来源**：fetch_perf 的数据由两部分组成——
1. **speed_tester.py 主动测速**（MOD-L00-004 §8.5）：对每个 capability×每个可用 source 做小样本测速，记录 rows/sec/symbols/sec/错误率，结果写入 c0_meta.fetch_perf。CLI：`integrator speed-test [--source <src>] [--capability <cap>]`。只读测速不写业务表，小样本测试。
2. **运行时被动记录**：scheduler 执行任务时自动记录实际性能。

**why 主动测速 + 被动记录双通道**：被动记录依赖任务实际运行（某些任务可能周/月频次，被动记录更新慢）；主动测速可按需触发，用于主用/备用源选型和数据源健康监控的及时决策。

### 10.5 开机自启架构（单一真源）

**真源**：[boot_autostart_architecture.md](../../03_modules/_domain_data/boot_autostart_architecture.md)（MOD-L00-004 §1-§5，v1.0.0，2026-08-07 更新）

**第一性原理**（AGENTS.md 硬约束：永久系统必须全自动——自动触发/运行/维护/关闭，禁止需手工干预的设计）：ZephyrAlpha 永久服务必须开机自启 + 崩溃自愈。通过 **Windows Task Scheduler 单一权威入口** 实现。

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

**5 个 Task Scheduler 任务**（单一入口，无 Startup 文件夹/注册表 Run）：

| 任务名 | 触发 | 脚本 | 守护对象 |
|---|---|---|---|
| `ZephyrAlpha_DataScheduler` | AtLogOn + PT5M 心跳 | scripts/start_scheduler.ps1 | 数据集成器调度器（zephyr.data.scheduler） |
| `ZephyrAlpha_TickSubscriber` | AtLogOn + PT5M 心跳 | scripts/start_tick_subscriber.ps1 | Tick 订阅器（zephyr.data.tick_subscriber） |
| `ZephyrAlpha_RSSHub` | AtLogOn | `pm2 resurrect`（hidden） | RSSHub 服务（rss_provider 依赖） |
| `ZephyrAlpha_TraeCacheCleanup` | AtLogOn + PT30S delay | clean_trae_cache.ps1 | Trae 缓存清理 |
| `ZephyrAlpha_DeadmanSwitch` | PT5M | scripts/deadman_switch.ps1 | 死人开关告警（§10.7） |

**部署**（一次性，无需管理员，交互用户）：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1   # scheduler + tick_subscriber + deadman_switch
powershell -ExecutionPolicy Bypass -File scripts\register_aux_tasks.ps1      # RSSHub + TraeCache
# AI 会话手动启动（禁止 IDE 终端 Start-Process，进程会随终端死）：
schtasks /run /tn ZephyrAlpha_DataScheduler
```

**legacy 清除**（2026-07-27）：移除 Startup 文件夹 `ZephyrAlpha_DataScheduler.lnk` + `start_zephyr_scheduler.bat`（冗余+闪窗+双重启动 tick_subscriber）；`start_rsshub.bat` / `CleanTraeCache.bat` 迁移到 Task Scheduler。备份在 `tmp/startup_backup_20260727/`。

> **project_memory 硬约束（防闪窗双机制）**：
> - Task Scheduler watchdog 任务禁止直接用 powershell.exe 启动（控制台子系统程序会闪窗），改用 wscript.exe + scripts/launch_hidden.vbs
> - 运行中的 .py 脚本启动子进程须用 run_subprocess_hidden()/spawn_python_hidden()（CREATE_NO_WINDOW），禁止裸 subprocess.run

### 10.6 四层防御 Watchdog（#ARCH-BOOT-001，resolved 2026-08-07）

**真源**：[boot_autostart_architecture.md](../../03_modules/_domain_data/boot_autostart_architecture.md) §3 + §8

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

**历史事故**（2026-08-07 立项根因）：scheduler/tick_subscriber 主进程死亡、guard 僵尸化导致 intraday 下载停滞 2 交易日（kline_1min 停在 08-05 15:00、tick_data 停在 08-04）。根因：`WaitForExit()` 纯阻塞等待在某些 Windows 进程退出场景不返回，guard 主线程卡死（CPU=0），子进程已死但 guard 不 log "exited"、不重启；单实例锁只验 PID 存活不验健康度，Task Scheduler 每 5min 拉新 guard 被僵尸 PID 挡住 "Guard already running, exit" 形成死锁。

**端到端验证**（2026-08-07 16:00-16:03 全绿）：

| 验证项 | scheduler | tick_subscriber | ch_health_probe |
|---|---|---|---|
| 僵尸接管（旧guard→新guard） | 24040→640 ✅ | 26940→19480 ✅ | 9132→23384 ✅ |
| 心跳每 15s 更新 | 640\|23232 ✅ | 19480\|7432 ✅ | 23384\|2364 ✅ |
| 子进程崩溃→guard 重启 | 杀29640→attempt2(23232) ✅ | — | — |
| 旧僵尸全死+无重复实例 | 24040/26940/9132 全死，每服务1实例 ✅ |

### 10.7 死人开关告警（#ARCH-BOOT-002，战略补强 E，2026-08-08 落地）

**问题**：四层防御主治本（Phase 1-5）已闭合僵尸接管闭环，但"全层失效无人知"循环未闭合——2026-08-07 的 2 日停摆是**人工发现**的，非系统告警。

**方案**：`scripts/deadman_switch.ps1`——**无状态一次性 Task Scheduler 任务**（非 while-true guard，无僵尸风险），每 5min fire 读 3 个心跳文件（scheduler/tick_subscriber/ch_health_probe），任一陈旧 >10min 即告警。

**独立性第一性原理**：监控者不属被监控的 3 服务之一，只读心跳文件；若 3 服务全死，此任务仍独立 fire 并告警。

**为何 .ps1 而非 .py**：若故障根因是 Python 栈崩溃（坏 import/venv），.py 监控会跟着死；.ps1 读文件+发 webhook 零 Python 依赖。

**告警通道**：
- 飞书 webhook（推手机，复用 `ZEPHYR_FEISHU_WEBHOOK`，与 Alerter 同契约）
- Windows Event Log
- 本地 `tmp/deadman_switch_alerts.log`（全审计无冷却）
- **30min 冷却**防多小时停摆刷屏（同一 staleKey 30min 内只推一次手机）

**Fail-safe**：此任务自身死亡退化到 pre-E 现状（无监控），非倒退——无需无限递归监控。

**配套战略补强**（#ARCH-BOOT-002 另两项）：
- **D. 心跳原子写** ✅：`Out-File` 截断+写非原子，新 guard 轮询期撞上旧 guard 写心跳微秒窗口可能读到半写→误判 stale→假接管（杀健康 guard）。3 个 guard 脚本 `Write-Heartbeat` 改为写 `$HeartbeatFile.tmp` + `Move-Item -Force`（同卷原子 rename）
- **F. WaitForExit 死锁根因文档化** ✅：3 个 guard 脚本头注释固化"pipe buffer fills → WaitForExit never returns → main thread deadlocks"知识点，防 AI "优化"回 `WaitForExit`

### 10.8 系统级健康监控

#### 10.8.1 健康聚合器 HealthAggregator（MOD-INF-015）

**真源**：`src/zephyr/infrastructure/system_telemetry/health_aggregator.py`

**职责**：每 15s 轮询 12 系统三态探针（liveness/readiness/healthz）→ 生成健康面板快照 → 年度审计。

**三态模型**：
- `liveness`：进程是否活着（alive/dead）
- `readiness`：是否就绪可服务（ready/not_ready）
- `degraded`：是否降级运行（healthz=degraded）

**快照管理**：最多保留 1440 个快照（15s × 1440 = 6 小时滚动窗口），超出 FIFO 淘汰。

**事件驱动订阅**（永久系统四要素：自动触发）：订阅 event_bus 的 `kill_switch_triggered` / `pipeline_failed` 事件，触发时立即采集健康快照，degraded 系统数 > 0 则告警。

**年度健康报告**：uptime_ratio / mttr_s / degradation_ratio 三指标按系统分项。

#### 10.8.2 ClickHouse 健康探针 ch_health_probe

**真源**：`scripts/start_ch_health_probe.ps1` + ch_health_probe.py

**职责**：3s 探测 ClickHouse TCP+HTTP 双通连，心跳写入 `tmp/ch_health_probe.heartbeat`。

**纳入四层防御**（#ARCH-BOOT-001 Phase 2）：ch_health_probe 与 scheduler/tick_subscriber 同等纳入心跳僵尸接管机制（缺陷 2 修复：初版方案未覆盖 ch_health_probe）。

**why 独立探针**：ClickHouse 是数据落库终点，CH 不可用则所有下载白费。独立探针避免"scheduler 活着但 CH 死了"的盲区。

#### 10.8.3 数据源健康检查 source_health_check（§8.5 已述）

定期检查数据源状态（health_check 探活），结合 fetch_perf 的 api_status（ok/slow/rate_limited/blocked/broken/pending）做退化决策。

#### 10.8.4 三冗余 Watchdog（MOD-INF-015）

**真源**：`src/zephyr/infrastructure/system_telemetry/watchdog.py`

**职责**：三冗余互检 + Panic Mode + Dead Man's Switch（CT-WATCHDOG-001）。

**机制**：
- 心跳写入外部文件 `data/telemetry/.watchdog_heartbeat_{id}`（原子写：tmp + replace）
- `check_peers(peers, peer_heartbeats)`：peer 心跳超 1800s（30min）视为 missing，2+ peer missing 触发 `panic_mode=True`
- `should_alert_dead_mans_switch(last_heartbeat_s)`：超 1800s 触发死人开关告警

**两种运行模式**：
1. 库模式：`Watchdog(watchdog_id="wd-1")` 嵌入其他进程
2. 独立进程：`python -m zephyr.infrastructure.system_telemetry.watchdog --id wd-1 --interval 10`

**why 三冗余互检而非单点**：单点 watchdog 自身死亡无人知；三冗余互检，2+ peer missing 才 panic，避免单点误报，且任一 peer 死亡可被其他 peer 发现。

### 10.9 不变式测试防回退

**真源**：`tests/scripts/test_guard_invariants.py` + `tests/scripts/test_guard_watchdog.py`

**设计动机**（#ARCH-CH-004）：100% AI 开发模式下，AI 可能"优化"回 `WaitForExit`（看似更简洁）或改回 `IgnoreNew`（看似更安全），导致治本成果被回退。用不变式测试钉死治本决策为可执行不变式，AI 任何回退都会触发测试失败。

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

**真源**：`src/zephyr/data/cli.py` + `__main__.py`（`python -m zephyr.data` 等价于 `integrator` 命令）

**包入口 get_integrator()**（`__init__.py`）：调度器单例工厂，首次调用创建 IntegratorScheduler 实例并 `_load_config()` 加载配置，后续调用返回同一实例。CLI 和外部消费者应通过此函数获取调度器。

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

**真源**：`scripts/launch_hidden.vbs`

**病根**：`powershell.exe` 是**控制台子系统程序**。Task Scheduler 以 Interactive 方式拉起它会瞬间分配一个控制台窗口；`-WindowStyle Hidden` 只能在 PowerShell 主窗口创建之后再隐藏，来不及阻止那一瞬间的闪现。3 个 watchdog 任务每 5min 重复触发 → 每 5min 闪 3 次窗口。

**原理**：`wscript.exe` 是 **GUI 子系统程序**，不创建控制台窗口；`WScript.Shell.Run cmd, 0`（SW_HIDE）启动目标 powershell 时，控制台窗口被隐藏创建，从根本上消除闪窗。

**用法**（Task Scheduler Action）：
```
Execute:    wscript.exe
Arguments:  "D:\ZephyrAlpha\scripts\launch_hidden.vbs" "<ps1 full path>"
```

**等待策略**：`sh.Run cmd, 0, True`（True=等待子进程退出）。guard 脚本是 while-true 常驻，wscript 随之常驻；guard 崩溃 → wscript 返回其退出码 → Task Scheduler 检测失败 → RestartOnFailure 触发。与原 powershell 直接常驻行为一致，且避免 wscript 立即退出导致 Task Scheduler job object 误杀孙进程 guard。

**why vbs 而非 .ps1 直接启动**：project_memory 硬约束——Task Scheduler watchdog 任务禁止直接用 powershell.exe 启动（控制台子系统程序会闪窗）。vbs 是 GUI 子系统，是消除闪窗的唯一方案（`-WindowStyle Hidden` 治标不治本）。

### 10.12 幂等注册脚本 register_guard_tasks.ps1 / register_aux_tasks.ps1

**真源**：`scripts/register_guard_tasks.ps1`（guard 任务）+ `scripts/register_aux_tasks.ps1`（aux 任务）

**职责**：声明式幂等注册 5 个 Task Scheduler 任务（§10.5 表格），`Set-ScheduledTask` in-place 更新已存在任务。

**关键约束**（register_guard_tasks.ps1 头注释固化）：
- **NEVER Unregister+Register an existing task**——Unregister 会 TERMINATE 运行中的 guard 实例（2026-07-22 23:30-00:48 静默 guard 死亡根因：re-registration 杀了运行中 guard 42196/55188，watchdog 虽复活但服务 needless bounced）。必须用 `Set-ScheduledTask` in-place 更新。
- **MultipleInstances=Parallel**（guard 任务，fix #ARCH-BOOT-001 Phase 1）：Task Scheduler 是 DUMB 周期启动器，不参与单实例决策；单实例 SSoT 是脚本级 PID lock + heartbeat check。IgnoreNew 会阻断新 guard（僵尸 guard 占位时心跳接管成死代码）。
- **register_aux_tasks.ps1 保持 IgnoreNew**：一次性 AtLogOn 任务无 while-true guard，无僵尸风险，IgnoreNew 合适。**文档化有意非对称**（不变式测试 TestRegisterGuardUsesParallel / TestRegisterAuxKeepsIgnoreNew 钉死）。

**部署**（交互用户，无需管理员）：
```powershell
powershell -ExecutionPolicy Bypass -File scripts\register_guard_tasks.ps1   # scheduler + tick_subscriber + ch_health_probe + deadman_switch
powershell -ExecutionPolicy Bypass -File scripts\register_aux_tasks.ps1      # RSSHub + TraeCache
```

**why 声明式幂等而非手动 schtasks**：AI 可维护性（C7 约束）——register 脚本可重复执行（in-place 更新），AI 改配置后重跑脚本即可同步到 Task Scheduler，无需手动 schtasks 命令易出错。

### 10.13 Prometheus HTTP 端点 metrics_server（P1-5 可观测性）

**真源**：`src/zephyr/shared/observability/metrics_server.py`（MOD-INF-016，D_SHARED 域）

**职责**：启动 daemon 线程提供 `/metrics` 和 `/health` HTTP 端点，输出 MetricsRegistry 的 Prometheus 兼容文本。被 §6.6 tick_subscriber 调用（`start_metrics_server(port=9925)`）。

**端点**：
- `GET /metrics`——输出 Prometheus 文本格式指标（200）
- `GET /health`——健康检查（200）
- 未知路径——404

**配置**：端口默认 9925；独立 daemon 线程不阻塞主流程；静默访问日志（不刷屏）。

**验证**：
```bash
curl http://localhost:9925/metrics
curl http://localhost:9925/health
```

**why HTTP 端点而非只写 metrics.prom 文件**：§10.3 的 metrics.prom 文本文件需外部 scraper（Prometheus node_exporter textfile collector）定时读取，延迟高；HTTP 端点支持 Prometheus pull 模式实时抓取，且支持 curl 手动验证。tick_subscriber 作为独立进程，HTTP 端点让它的指标可被 Prometheus 直接抓取。

**why daemon 线程而非独立进程**：metrics_server 是 tick_subscriber 的附属可观测性组件，独立进程会增加守护复杂度（又多一个 watchdog）。daemon 线程随主进程生死，简单且够用。

### 10.14 数据相关 commit_gates 防回退门禁（pre-commit 静态检测层）

**真源**：`src/zephyr/gov_enforcement/commit_gates/`（MOD-GATE_ENGINE，D_GOV_CODE_QUALITY 域，由 `GitCommitGateway` 在 pre-commit 钩子统一调度）

**与 §10.9 不变式测试的区别**：§10.9 是运行时不变式测试（pytest 跑测试钉死设计）；本节是 commit 时静态检测（git diff staged 行 AST/正则扫描，AI 改代码时即时拦截）。两者互补——§10.9 防"运行时行为回退"，本节防"源码回退"。

**why 独立成节**：100% AI 开发模式下，§5-§9 的设计决策（BufferedWriter/ch_reader FINAL/version 列/TableRegistry/CapabilityContract/无裸 SQL）若无 commit 门禁强制，AI 后续开发极易"图方便"绕过（直接调 write_result / ch_writer.query / 硬编码表名）。门禁是设计决策的"执法层"配套。

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

**fail-open / fail-closed 策略**：
- git diff 不可达 / AST 解析失败 / YAML 解析失败 → **fail-open**（passed=True，logger.warning，不阻断——检测器失效不能瘫痪开发）
- 检出违例 → **fail-closed**（passed=False，阻断 commit）
- audit log 目录缺失（capability_lookup）→ **fail-closed**（防"删目录绕过"攻击向量）

**紧急逃生**：`[no-lookup:reason]` commit msg 白名单标记 / `ZEPHYR_BYPASS_LOOKUP=1` 环境变量（与 `ZEPHYR_COMMIT_GATEWAY=1` 同级逃生阀）。

**why DATA-TASK-COMPLETENESS warn 而非 block**：历史 130+ 任务多数无 fallback_sources，一次性全阻断会瘫痪开发；warn 提醒渐进式补全，新任务养成配 fallback 习惯后再收紧。

**why CAPABILITY-OVERLAP 接入 CloneGuard**：纯 token overlap 检测不出"语义克隆"（变量改名+小逻辑增减）；Echo-Guard 语义嵌入检测 extract 级克隆（3+副本）硬阻断，强制合并去重。

## 11. 已施工盘点

### 11.1 代码文件清单（src/zephyr/data/）

> 真源：depgraph（`extract_depgraph.py --modules MOD-L00-004`）。以下为职责描述，文件列表以 depgraph 为准。共 50+ 文件。

**包入口**：`__init__.py`（get_integrator 单例工厂）/ `__main__.py`（python -m zephyr.data CLI 入口）
**Provider 抽象层**：provider_base.py（IngestProviderBase + FetchPayload + FetchResult + IngestProviderMeta + CapabilityContract §5.1-§5.2）/ capability_validator.py（§5.8 启动时契约校验）/ error_classifier.py（§5.9 错误分类器）/ policy_registry.py（§5.7 per-source 策略注册表）/ table_registry.py（§5.6 表名 SSoT 消费层）/ quality_gate.py（§8.1 re-export wrapper）
**Provider 实现**（15 个）：implementations/{akshare,baostock,cls,eastmoney_news,eia,fred,ifind,internal_compute,miniqmt,qweather,rss,tdx,tickflow,tqcenter,tushare}_provider.py
**symbol 标准化**：symbol_normalizer/{__init__,normalizer}.py（§5.5 TRAE-082）
**域包入口**：satellite_geospatial_engine/__init__.py（§5.10 D_DATA 域入口 + CTR 契约声明）
**调度编排**：scheduler.py / task_queue.py / progress_store.py（§10.1）/ alerter.py（§10.2）/ metrics.py（§10.3）/ cli.py（§10.10）/ trading_calendar.py（§6.7 交易日历守卫）
**落库**：ch_config.py（§7.6.1 连接配置单真源）/ ch_reader.py（§7.6.2 统一读取层 FINAL 注入）/ ch_writer.py（§7.3 混合传输）/ buffered_writer.py（§7.2 攒批）/ wal_writer.py（§7.8 主动 WAL）/ local_replay.py（§7.7.1 TSV 兜底+回灌）/ wal_codec/{__init__,codec_registry,tsv_codec}.py（§7.9 编解码注册表）
**质量完整性**：integrity_checker.py（§8.2 L11 巡检）/ backfill_checker.py（§8.3 L10 补下载）/ cross_source_validator.py（§8.4 跨源验证）/ source_health_check.py（§8.5 数据源健康）/ pit_query.py（§8.6 PIT 查询）/ speed_tester.py（§10.4 主动测速）
**业务下载器**：sector_kline_downloader.py（§6.8.1 板块K线）/ sector_ranking_engine.py（§6.8.2 板块排名）/ sector_snapshot_collector.py（§6.8.3 板块快照）/ kline_resampler.py（§6.9 K线合成）/ news_collector.py（§6.10.2 新闻查询）/ news_dedup.py（§6.10.1 新闻去重）/ tick_redis_cache.py（§7.11 Redis 热缓存双写）/ tick_subscriber.py（§6.6 Tick 订阅独立进程）
**冗余容灾**：redundant_source/{__init__,heartbeat_monitor,source_switcher,backup_tick_poller,recovery,sqlite_fallback}.py（§9.2 热切换 + SQLite 兜底）
**配置**：config/tasks.yaml（§11.2）/ config/schedule.yaml（§6.2 13档）/ config/policies.yaml（派生）/ config/known_data_gaps.yaml（§8.7 历史缺口注册表）
**守护与自启**（跨域引用，真源在 D_INFRA_RUNTIME / scripts/）：infrastructure/{database_service.py（§7.10 连接管理）, system_telemetry/{watchdog,health_aggregator,health_probes}.py} + shared/observability/{metrics,metrics_server}.py（§10.13） + scripts/{start_scheduler,start_tick_subscriber,start_ch_health_probe,deadman_switch,register_guard_tasks,register_aux_tasks,clean_trae_cache}.ps1 + launch_hidden.vbs（§10.11） + tests/scripts/{test_guard_invariants,test_guard_watchdog}.py（§10.9 不变式测试） + gov_enforcement/commit_gates/{ch_batch_size,ch_final,ch_version_col,table_name_registry,capability_consistency,capability_lookup_required,capability_overlap,bare_sql,data_task_completeness}_gate.py（§10.14 防回退门禁 9 项）

### 11.2 配置文件清单

| 文件 | 作用 | 条目数 |
|---|---|---|
| config/tasks.yaml | 采集任务清单（表→Provider→策略→fallback） | ~130+ 任务 |
| config/schedule.yaml | 13 档调度时段（含 L2.5 板块 + L10.5 每日补下载） | 13 档 |
| config/policies.yaml | per-source 策略参数（派生物，真源在 registry.yaml） | 派生 |
| config/known_data_gaps.yaml | 已知历史缺口注册表（§8.7，backfill 全范围回看） | 2 条登记 |
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

| 文档 | module_id | 作用 |
|---|---|---|
| _domain_data/index.md | MOD-L00-001 | D-DATA 域索引 |
| _domain_data/blueprint.md | MOD-L00-001 | Datasource Core 蓝图（v4.0.4，Provider 部分已移交 004） |
| _domain_data/data_source_integrator_blueprint.md | MOD-L00-004 | 数据源集成器蓝图（what 层真源，v0.4.1） |
| _domain_data/data_source_operation_manual.md | MOD-L00-002 | 数据源 API 操作唯一真源（iFind+miniQMT 实测验证） |
| _domain_data/boot_autostart_architecture.md | — | 开机自启架构 |
| _domain_data/redundant_source_blueprint.md | — | 冗余数据源蓝图 |
| _domain_data/wal_codec_blueprint.md | — | WAL 编解码蓝图 |
| _domain_mkt_data/{autoload,connectors,failover,raw_data_cache,vendor_base,vendor_registry}/blueprint.md | — | 行情数据域 6 子模块蓝图 |
| 02_domain_architecture_docs/11_d_data.md | D_DATA | D_DATA 域 183 模块清单 |
| 05_dataflow_architecture/data_inventory.md | — | 业务数据现状（ClickHouse 实时扫描） |
| 05_dataflow_architecture/data_acquisition_requirements.yaml | — | 数据获取需求 P0-P3 |
| design_memos/15_data_feature_layer_spec.md | G01 | 数据与特征层规范（互补） |
| design_memos/17_special_trading_days_data_assets.md | — | 特殊交易日数据资产 |
| design_memos/18_cold_archive_build_plan.md | — | 冷归档施工计划 |
| design_memos/19_northbound_hold_snapshot.md | — | 北向季度快照 fetcher |
| design_memos/63_data_utilization_audit.md | — | 数据利用审计（配套） |

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

**A. 模块单元测试**（`tests/zephyr/data/`，25 个文件，验证 §5-§7 各模块行为）：

| 测试文件 | 验证对象 | 对应章节 |
|---|---|---|
| test_provider_base.py / test_providers.py / test_providers_stage3.py | IngestProviderBase + 15 Provider 实现 | §5.1/§5.3 |
| test_capability_validator.py | CapabilityContract 启动校验 | §5.8 |
| test_internal_compute_provider.py | internal_compute 铁律 | §5.4 |
| test_data_scheduler.py / test_data_task_queue.py | 调度编排 + 任务队列 | §6.1/§6.4 |
| test_data_cli.py | CLI 命令 | §10.10 |
| test_ch_writer.py | CH 混合传输写入 | §7.3 |
| test_wal_writer.py / test_wal_codec.py | 主动 WAL + 编解码 | §7.8/§7.9 |
| test_local_replay.py | TSV 兜底+回灌 | §7.7.1 |
| test_redundant_source.py / redundant_source/test_heartbeat_monitor_alert.py | 冗余源热切换 + 心跳告警 | §9.2 |
| test_tick_subscriber.py / test_tick_redis_cache.py | Tick 订阅 + Redis 双写 | §6.6/§7.11 |
| test_kline_resampler.py | K线合成 | §6.9 |
| test_sector_ranking_engine.py / test_sector_snapshot_collector.py | 板块排名 + 快照 | §6.8.2/§6.8.3 |
| test_integrity_checker.py / test_cross_source_validator.py | 完整性巡检 + 跨源验证 | §8.2/§8.4 |
| test_policy_registry.py / test_error_classifier.py | 策略注册 + 错误分类 | §5.7/§5.9 |
| test_progress_store.py / test_alerter.py / test_metrics.py | 进度/告警/指标 | §10.1/§10.2/§10.3 |

**B. 数据治理测试**（`tests/data/`，13 个文件，验证数据生命周期/质量/分类）：
test_data_classification / test_data_lifecycle / test_data_pipeline_guard / test_data_quality / test_data_quality_gate / test_data_source_reliability / test_data_volume_growth_monitor / test_l00_data_source / test_market_quality_validator / test_news_collector / test_pit_query / test_source_health_check / test_symbol_normalizer

**C. commit_gates 门禁测试**（`tests/governance/commit_gates/`，验证 §10.14 门禁本身正确）：
test_ch_batch_size_gate / test_ch_final_gate / test_ch_version_col_gate / test_data_task_completeness_gate / test_table_name_registry_gate / test_capability_lookup_required_gate / test_capability_overlap_gate / test_bare_sql_gate

**D. 守护不变式测试**（`tests/scripts/`，§10.9 已述）：test_guard_invariants / test_guard_watchdog（钉死 §10.5-§10.8 守护配置防回退）

**why 记录测试层**：测试是配套的验证层——模块行为变更 MUST 同步更新单元测试，设计决策变更 MUST 同步更新不变式测试。AI 改代码时通过 `[TESTS]` 头注释定位对应测试文件（如 §5.9 error_classifier 头注释 `[TESTS] tests/zephyr/data/test_error_classifier.py`）。

## 12. 已知缺口与升级方向（讨论载体）

> **本节是用户要求的"对系统里已经有的数据源和数据下载进行全面升级"的讨论载体**。逐项列出已识别的缺口、待升级项、待裁定方向，待人讨论定夺后升 version。

### 12.1 iFind 试用到期遗留影响（#ARCH-IFIND-FAILOVER）

**现状**：iFind 试用账号到期，7 类任务已降级（估值/资金流/行业分类/概念板块/实时快照/板块信息/行业分类补充），akshare/tushare 升为主源。

**缺口**：
- `edb_data_incremental` **disabled**（iFind EDB 配额耗尽 -4318，5万条/月不够拉 104 个宏观指标全历史，无 fallback）——edb_data 表至今 0 行。
- iFind 续费后需手动改回 source=ifind（7 类任务），目前 tasks.yaml 已保留 ifind 为 fallback，切换成本低。

**待裁定**：
- [ ] iFind 是否续费？续费则恢复主源，不续费则 edb_data 永久 disabled 需找替代源（FRED/世界银行部分覆盖，但中国宏观 EDB 无完整替代）。
- [ ] edb_data 替代方案：是否用 akshare 宏观接口 + 东方财富宏观 + 国家统计局爬虫拼凑？

### 12.2 disabled 任务清单及原因

| task_id | disabled 原因 | 修复路径 |
|---|---|---|
| edb_data_incremental | iFind EDB 配额耗尽(-4318)，无 fallback | iFind 付费版 / 替代源 |
| audit_opinion_incremental | AKShare 无专用批量审计意见接口，逐股获取效率过低 | 待 iFind 等数据源补齐 |
| rights_issue_incremental | akshare 1.18+ 移除 stock_rights_issue_detail_sina，逐股接口效率过低 | 待数据源补齐 |
| news_tushare_incremental | API 已废弃（数据截止2024-08，pro.news 返回"请指定正确的接口名"） | 由 RSS/cls/eastmoney 覆盖 |
| kline_us_daily_qmt_incremental | QMT 无美股板块，需单独开通美股行情权限 | 已由 tickflow+akshare 双源覆盖 |
| l2_tick_snapshot | 需付费 L2 行情权限（#ARCH-DATA-014） | 用户开通 L2 后启用，fallback 降级到 tick_data |
| msci_adjustment_refresh | akshare/tushare 均无 MSCI/富时调整直接接口（#ARCH-SPECIAL-DAYS） | 待爬虫 MSCI 官网/第三方/Wind |
| margin_trading_qmt_placeholder | QMT 无接口，已由 AKShare 覆盖 | 占位 disabled |
| dragon_tiger_qmt_placeholder | QMT 无接口，已由 AKShare 覆盖 | 占位 disabled |
| block_trade_qmt_placeholder | QMT 无接口，已由 AKShare 覆盖 | 占位 disabled |
| kline_5min_history_backfill | 百度云已下载2000-2024，任务已退役 | — |

**待裁定**：
- [ ] audit_opinion / rights_issue 是否值得找替代源？（低频事件，可能不值得）
- [ ] MSCI/富时调整是否值得爬虫？（#ARCH-SPECIAL-DAYS 相关，影响外资流入预期）
- [ ] L2 行情是否开通？（影响打板策略微观结构分析，24 号打板策略相关）

### 12.3 blocked/broken API（akshare 数据源退化）

**现状**（fetch_perf 实测）：
- `akshare.money_flow` **blocked**（东财反爬封锁 RemoteDisconnected）——已回退 ifind→akshare（#ARCH-IFIND-FAILOVER 后 akshare 主源，但 akshare 也 blocked，实际靠 fallback 链兜底）
- `akshare.equity_pledge` **broken**（API 损坏 data_json[result]为 None）——已回退 ifind
- `akshare.equity_pledge_summary` **broken**（同上）
- `akshare.daily_valuation` **rate_limited**（百度API空响应率15%，0.17只/s）

**待裁定**：
- [ ] akshare money_flow blocked 是否找替代源？（tushare 有 moneyflow 但需积分）
- [ ] equity_pledge broken 是否找替代源？（tushare 有 pledge 但需积分）
- [ ] daily_valuation rate_limited 是否优化？（已 Event.wait(1s)/股 限流）

### 12.4 slow capability（性能瓶颈）

**现状**：
- `miniqmt.adj_factor` **slow** 0.09只/s（get_divid_factors 每只11秒，全量16h）——增量模式下每日只拉近期可接受，全量回算需周末窗口

**待裁定**：
- [ ] adj_factor 全量回算是否优化？（如改用 akshare/tushare 复权数据反推复权因子）

### 12.5 北向资金日频断档（19 号文档）

**现状**：港交所 2024-08-16 停止公布北向资金每日明细，`hk_connect_flow` 只有 2014-11-17~2024-08-16 历史。19 号文档已定方案：tushare hk_hold 季度末持仓快照作为日频断档替代。

**待裁定**：
- [ ] 19 号方案是否落地施工？（draft v0.1.0，fetcher+落表+外资行为方法论）

### 12.6 数据源覆盖缺口

| 缺口 | 影响 | 候选方案 |
|---|---|---|
| MSCI/富时指数调整 | 外资流入预期（#ARCH-SPECIAL-DAYS） | 爬虫 MSCI 官网 / Wind / 第三方 |
| L2 逐笔行情 | 打板策略微观结构（24 号） | 付费开通 miniQMT L2 权限 |
| edb_data 中国宏观 EDB | 宏观因子（104 指标） | iFind 付费版 / akshare+东方财富+统计局拼凑 |
| 龙虎榜机构席位明细 | 机构资金动向 | akshare 已覆盖（dragon_tiger_seat） |
| 期货分笔数据 | 期货微观结构 | 待评估需求 |
| 港股 Level2 | 港股微观结构 | 待评估需求 |

### 12.7 调度编排升级方向

**现状**：APScheduler 常驻进程 + 11 档时段 + DAG 依赖 + fallback 三层韧性。

**待裁定升级方向**：
- [ ] **调度优先级动态化**：当前时段内任务按 tasks.yaml 顺序执行，是否根据 fetch_perf 的 api_status 动态排序（ok 优先，slow/rate_limited 安排低峰）？
- [ ] **任务级 SLA 监控**：当前只有成功率告警，是否加任务级 SLA（如 kline_daily 必须在 17:00 前完成，否则告警）？
- [ ] **跨源并发优化**：当前 default 池 8 线程/heavy 池 2 线程，是否按 source 细化并发控制（如 akshare 4 并发、baostock 8 并发）？
- [ ] **调度器高可用**：当前单进程，进程崩溃靠 Task Scheduler watchdog 重启 + misfire_grace_time 补跑，是否够用？

### 12.8 落库体系升级方向

**现状**：ReplacingMergeTree 统一 + BufferedWriter 攒批 + ch_writer 混合传输 + 8 表 MergeTree 遗留。

**待裁定升级方向**：
- [ ] **8 个 MergeTree 遗留表是否迁移 ReplacingMergeTree**？（share_unlock/restricted_shares/analyst_forecast/disclosure_plan/equity_pledge_detail/rights_issue/share_change/industry_class_suppl）——迁移后可去掉写前 DELETE 逻辑，但需验证去重键正确性
- [ ] **data parts 监控**：当前靠事故后人工发现 parts 爆炸，是否加 system.parts 监控告警（parts>100 告警）？
- [ ] **冷归档落地**：18 号文档 draft v0.1.0，数据保留铁律要求 Cold 层手动触发，冷归档施工计划待落地
- [ ] **WAL 兜底常态化**：CH 写入失败时数据落本地 TSV 待补，当前是否所有任务都走 WAL 兜底？

### 12.9 质量与完整性升级方向

**现状**：quality_gate 读取端校验 + integrity_checker L11 每日巡检 + backfill_checker L10 周补 + cross_source_validator 跨源验证。

**待裁定升级方向**：
- [ ] **质量门控前移**：当前 quality_gate 在读取端，是否对关键表（kline_daily/财务三表）在写入时加轻量校验？
- [ ] **跨源验证覆盖面**：cross_source_validator 当前覆盖哪些表？是否全量覆盖有 fallback 的表？
- [ ] **数据血缘追踪**：当前 fetch_perf 记录 source+capability，是否加数据血缘（哪条数据来自哪个源哪个时间拉的）？
- [ ] **PIT 一致性巡检**：15 号 §3.3 PIT 铁律，数据下载层是否加 PIT 一致性巡检（如财报 announce_date ≤ report_date）？

### 12.10 数据源扩展方向

**待裁定新增数据源**：
- [ ] **东方财富爬虫专用 provider**：当前 akshare 包装东财接口，但东财反爬严重（money_flow blocked），是否做专用爬虫 provider 绕过反爬？
- [ ] **同花顺 iwencai 爬虫**：ifind 到期后，iwencai 问财接口是否可独立爬虫（概念板块/行业分类已用 akshare 包装，但 iwencai 原生能力更强）？
- [ ] **国家统计局爬虫**：edb_data 替代方案，CPI/PPI/GDP 等官方数据
- [ ] **券商场内数据**：如打板策略需要的逐笔委托（24 号相关），miniQMT L2 或第三方

### 12.11 守护与自启升级方向

**现状**：四层防御 Watchdog（#ARCH-BOOT-001 resolved）+ 死人开关告警（#ARCH-BOOT-002 落地）+ 不变式测试防回退（8 项）+ HealthAggregator 12 系统三态探针 + ch_health_probe 独立探针 + 三冗余 Watchdog（MOD-INF-015）。2026-08-07 intraday 停摆 2 日事故已治本。

**待裁定升级方向**：
- [ ] **死人开关告警通道冗余**：当前 deadman_switch 走飞书 webhook，若飞书 API 故障则告警丢失。是否加短信/邮件备用通道？（Fail-safe 要求"此任务自身死亡退化到无监控"，但告警通道失效是另一类风险）
- [ ] **HealthAggregator 12 系统探针是否含数据集成器**：当前 12 系统三态探针（SYSTEMS 列表在 health_probes.py），是否已纳入 scheduler/tick_subscriber/CH 三个数据集成器关键服务？还是只覆盖交易/风控层？
- [ ] **心跳阈值调参**：当前 guard 心跳 15s 写、5min 判 stale；deadman_switch 10min 判 stale。是否根据实际运行数据调优（如盘中高频期缩短阈值、盘后低频期放宽）？
- [ ] **ch_health_probe 探测频率**：当前 3s 探测 CH TCP+HTTP，是否过于频繁（CH 负担）？或盘中/盘后差异化频率？
- [ ] **三冗余 Watchdog 是否启用**：watchdog.py 支持库模式和独立进程模式，当前是否已部署运行？还是仅代码就绪未启用？
- [ ] **年度健康报告落地**：HealthAggregator.annual_report() 接口已就绪，uptime_ratio/mttr/degradation_ratio 是否有实际数据产出和定期 review？
- [ ] **跨服务依赖故障传播**：RSSHub 服务挂了导致 rss_provider 失效，是否在 deadman_switch 监控范围？（当前只监控 scheduler/tick/CH 三个心跳）

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
| 调度时段 | 11 档（当前） | 按数据频率分层，新增频率需求可加档 |
| 单表行数 | ClickHouse 单机限制（~千亿行/表） | 受 Hyper-V VM 磁盘容量约束 |
| 并发 | default 8 线程 + heavy 2 线程 | APScheduler ThreadPoolExecutor 配置 |
| 数据保留 | 永久（Hot 层无 TTL） | PS-CTR-003 铁律 |

### 14.2 演进路径

1. **短期**（本文讨论定夺后）：落地 §12 待裁定项中标记 P0 的升级（iFind 续费决策 / disabled 任务处置 / 8 表迁移 ReplacingMergeTree / data parts 监控）
2. **中期**：19 号北向快照落地 / 18 号冷归档落地 / 质量门控前移 / 跨源验证全量覆盖
3. **长期**：数据源扩展（东方财富爬虫/iwencai 爬虫/统计局爬虫） / 调度优先级动态化 / 数据血缘追踪

## 15. 待裁定

> 以下为暂缓项，非永久禁止，随项目演进重新裁定。

| 项 | 暂缓理由 | 重评条件 |
|---|---|---|
| 8 个 MergeTree 遗留表迁移 ReplacingMergeTree | 需验证去重键正确性，迁移有数据风险 | 写前 DELETE 逻辑维护成本累积到痛点时 |
| 质量门控前移（写入时校验） | 拖慢下载吞吐，脏数据可事后清洗 | 关键表出现脏数据污染下游时 |
| 调度优先级动态化 | 当前静态排序够用 | slow/rate_limited 任务影响盘后窗口完成时间时 |
| 数据血缘追踪 | fetch_perf 已记录 source+capability | 出现数据溯源需求时 |
| 东方财富专用爬虫 provider | akshare 包装够用 | akshare.money_flow blocked 长期无解时 |

## 16. 待定问题（开放问题）

> 以下需人决策，AI 不擅自发挥。

1. **iFind 是否续费**？续费则恢复 7 类任务主源 + edb_data 可用；不续费则 edb_data 永久 disabled 需找替代源。
2. **edb_data 替代方案**：iFind 不续费时，是否用 akshare 宏观 + 东方财富宏观 + 国家统计局爬虫拼凑 104 个宏观指标？
3. **audit_opinion / rights_issue / MSCI 调整**：低频事件数据，是否值得找替代源？（ROI 评估）
4. **L2 行情是否开通**？影响打板策略微观结构分析（24 号相关），需付费。
5. **19 号北向快照是否落地施工**？draft v0.1.0，tushare hk_hold 季度替代方案。
6. **18 号冷归档是否落地施工**？draft v0.1.0，数据保留铁律要求 Cold 层手动触发。
7. **8 个 MergeTree 遗留表是否迁移 ReplacingMergeTree**？需验证去重键正确性。
8. **data parts 监控告警是否加**？system.parts > 100 告警，防止 parts 爆炸重演。
9. **质量门控是否前移**？关键表（kline_daily/财务三表）写入时加轻量校验？
10. **东方财富专用爬虫 provider 是否做**？akshare.money_flow blocked 长期无解时。
11. **调度优先级是否动态化**？根据 fetch_perf api_status 排序。
12. **调度器高可用是否够用**？单进程 + Task Scheduler watchdog + misfire_grace_time，还是要双活？

## 17. 引用

### 17.1 本目录设计备忘

- [00_index_trading_decision.md](00_index_trading_decision.md)——总索引与路线图
- [01_design_memo_management_spec.md](01_design_memo_management_spec.md)——设计备忘管理规范（§4.4 spec 类结构原则）
- [15_data_feature_layer_spec.md](15_data_feature_layer_spec.md)——G01 数据与特征层规范（互补：15 号偏"数据进来后怎么用"，本文偏"数据怎么进来"）
- [17_special_trading_days_data_assets.md](17_special_trading_days_data_assets.md)——特殊交易日数据资产（#ARCH-SPECIAL-DAYS）
- [18_cold_archive_build_plan.md](18_cold_archive_build_plan.md)——冷归档施工计划（数据保留 Cold 层）
- [19_northbound_hold_snapshot.md](19_northbound_hold_snapshot.md)——北向季度快照 fetcher（日频断档替代）
- [63_data_utilization_audit.md](63_data_utilization_audit.md)——数据利用审计（配套：63 号审"用得怎么样"，本文审"下得怎么样"）

### 17.2 模块蓝图（what 层真源）

- [data_source_integrator_blueprint.md](../../03_modules/_domain_data/data_source_integrator_blueprint.md)——MOD-L00-004 数据源集成器蓝图（what 层真源，本文补 why）
- [blueprint.md](../../03_modules/_domain_data/blueprint.md)——MOD-L00-001 Datasource Core 蓝图（v4.0.4，Provider 部分已移交 004）
- [data_source_operation_manual.md](../../03_modules/_domain_data/data_source_operation_manual.md)——MOD-L00-002 数据源 API 操作唯一真源
- [boot_autostart_architecture.md](../../03_modules/_domain_data/boot_autostart_architecture.md)——开机自启架构
- [redundant_source_blueprint.md](../../03_modules/_domain_data/redundant_source_blueprint.md)——冗余数据源蓝图
- [wal_codec_blueprint.md](../../03_modules/_domain_data/wal_codec_blueprint.md)——WAL 编解码蓝图
- [_domain_mkt_data/](../../03_modules/_domain_mkt_data/)——行情数据域 6 子模块蓝图（autoload/connectors/failover/raw_data_cache/vendor_base/vendor_registry）

### 17.3 域架构与数据流

- [11_d_data.md](../../02_enterprise_architecture/02_domain_architecture_docs/11_d_data.md)——D_DATA 域 183 模块清单
- [data_inventory.md](../../02_enterprise_architecture/05_dataflow_architecture/data_inventory.md)——业务数据现状（ClickHouse 实时扫描）
- [data_acquisition_requirements.yaml](../../02_enterprise_architecture/05_dataflow_architecture/data_acquisition_requirements.yaml)——数据获取需求 P0-P3

### 17.4 代码真源（depgraph path）

- `src/zephyr/data/provider_base.py`——IngestProviderBase + FetchPayload + FetchResult + IngestProviderMeta + CapabilityContract
- `src/zephyr/data/implementations/*_provider.py`——15 个 Provider 实现
- `src/zephyr/data/scheduler.py`——APScheduler 调度编排
- `src/zephyr/data/config/tasks.yaml`——130+ 采集任务清单（真源）
- `src/zephyr/data/config/schedule.yaml`——13 档调度时段（真源，含 L2.5 板块 + L10.5 每日补下载）
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
- #ARCH-BOOT-001——四层防御 Watchdog（OS层/Guard层/单实例层/心跳健康层，2026-08-07 resolved，§10.6）
- #ARCH-BOOT-002——战略补强（D.心跳原子写 / E.死人开关告警 / F.WaitForExit 根因文档化，2026-08-08 落地，§10.7）
- #ARCH-BOOT-001——四层防御 Watchdog（含 launch_hidden.vbs 无闪窗启动器，§10.11）
- #ARCH-DATA-001——hk_trade_calendar 数据源错配修复（§4 / project_memory）
- #ARCH-DATA-SYMBOL-001/002——symbol 标准化 TRAE-082（§5.5）
- #ARCH-DATA-TICK-GAP-001——L10.5 每日盘后补下载当天补（§6.2）
- #ARCH-DATA-014——L2 行情权限缺失降级（§12.2）
- #ARCH-REALTIME-ACCUM——时间敏感型数据每日积累（§4.1 qweather）
- #ARCH-SPECIAL-DAYS——特殊交易日数据资产（§12.2 / §12.6）
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
