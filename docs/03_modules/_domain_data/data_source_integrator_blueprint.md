---
module_id: MOD-L00-004
title: 数据源集成器蓝图
doc_type: blueprint
status: Draft
layer: L2_domain
date: "2026-07-06"
version: "0.4.0"
ttl: permanent
supersedes:
  - "MOD-L00-001 §3.1 Provider 抽象部分（接管）"
depends_on:
  - "MOD-L00-002 数据源操作手册（策略参数来源）"
  - "MOD-L00-003 数据获取需求清单（任务清单来源）"
construction_progress: stage3_done
language: zh
description: 统一管理多个数据源的自动下载——Provider 抽象 + per-source 策略注册表 + APScheduler 调度编排 + 进度/告警统一管理
responsibility_domain: 
build_status: generated
design_maturity: prototype
---

# 数据源集成器蓝图（MOD-L00-004）

> **本蓝图目标**：把当前 61 项"手动触发"数据全部纳入自动调度，按数据源特性差异化处理限流/重试/反爬/登录刷新，实现盘后自动批量下载 + 失败告警 + 断点续传。
>
> **与现有文档关系**：
> - **接管** [blueprint.md](blueprint.md) §3.1 的 Provider 抽象部分（原蓝图声称"已实现"但 `src/zephyr/data/` 实际为空，本次一并重建）
> - **消费** [data_source_operation_manual.md](data_source_operation_manual.md) 中每个数据源的限流/防爬/登录方式（抽取为 per-source 策略参数）
> - **消费** [data_acquisition_plan.md](data_acquisition_plan.md) 的需求清单（转化为调度任务）
> - **解决** [data_acquisition_plan.md](data_acquisition_plan.md) 暴露的"61 项手动触发、0 项自动更新"短板（matrix 由 `tmp/generate_acquisition_matrix.py` 派生）

---

## §0 文档对齐

### §0.1 与 MOD-L00-001 blueprint.md 的边界划分

| 职责 | 归属 | 说明 |
|------|------|------|
| Provider 抽象（DataSourceBase / DataSourceMeta） | **本蓝图接管** | 原蓝图 §3.1/§4/§16.6 声称已实现但磁盘不存在，移交本蓝图重建 |
| 数据质量门禁（DataQualityGate） | 保留原蓝图 | 与下载调度解耦，由消费方在读取时调用 |
| CTR-001/002/003 输出契约 | 保留原蓝图 | 数据格式规范不变 |
| 调度编排 / 策略注册表 / 进度统一 / 告警 | **本蓝图新增** | 原蓝图未设计 |
| `src/zephyr/data/` 目录 | **本蓝图主管** | 实际写入代码 |

### §0.2 代码文件清单（目标态）

```
src/zephyr/data/
├── __init__.py
├── provider_base.py              # DataSourceBase 抽象 + DataSourceMeta
├── policy_registry.py            # SourcePolicy + per-source 策略注册表
├── scheduler.py                  # APScheduler 调度器封装
├── task_queue.py                 # 任务依赖图 + 优先级队列
├── progress_store.py             # 统一进度存储（SQLite）
├── alerter.py                    # 告警（日志 + 文件 + 可选钉钉/邮件）
├── metrics.py                    # 指标采集（Prometheus 文本格式）
├── cli.py                        # 命令行：手动触发/查看状态/重跑失败
├── config/
│   ├── schedule.yaml             # 调度计划（4档时段）
│   ├── policies.yaml             # per-source 策略参数（#183 起为派生物，真源见 data_sources_registry.yaml）
│   └── tasks.yaml                # 任务清单（表→Provider→策略）
└── implementations/
    ├── ifind_provider.py         # iFind（THS_RQ/THS_BD/iwencai/EDB）
    ├── miniqmt_provider.py       # miniQMT（xtdata 行情/财务/板块）
    ├── akshare_provider.py       # AKShare（分红/质押/解禁/宏观等）
    ├── baostock_provider.py      # baostock（线程局部登录）
    ├── tushare_provider.py       # tushare（新闻）
    ├── tickflow_provider.py      # TickFlow（美股/港股）
    ├── tdx_provider.py           # mootdx/pytdx（板块指数）
    └── rss_provider.py           # 财经RSS（新闻爬虫）
```

### §0.3 当前态/目标态差距

| 维度 | 当前态 | 目标态 |
|------|--------|--------|
| 自动更新项数 | 0 / 78 | ≥ 61 / 78（剩余 14 项空表 + 3 项无法获取） |
| 调度机制 | 人工运行 `python tmp/_fetch_*.py` | APScheduler 常驻进程自动触发 |
| 限流处理 | 每个脚本各写 `time.sleep` | per-source 策略注册表，统一 RPM/并发 |
| 重试策略 | 每个脚本各写 `for i in range(3)` | 策略化退避（指数/抖动），可热更新 |
| 断点续传 | 13 个 per-script JSON 文件 | 统一 SQLite 进度存储 |
| 失败告警 | 无（靠人看日志） | 日志 + 失败汇总文件 + 可选钉钉/邮件 |
| 数据源连接 | 脚本内直接 `import` SDK | Provider 封装，统一生命周期管理 |
| Provider 抽象 | 不存在 | DataSourceBase + 8 个实现 |
| 代码位置 | `tmp/_fetch_*.py`（TTL=task_bound） | `src/zephyr/data/`（长期资产） |

---

## §1 设计背景与目标

### §1.1 背景

[data_acquisition_plan.md](data_acquisition_plan.md) 暴露的核心问题：

- **61 项数据已有但需手动触发**——这是最大的自动化短板
- **0 项自动更新**——没有任何定时任务
- **每个数据源特性差异大**：
  - iFind：月度配额（-4318/-4309），需 THS_iFinDLogin
  - miniQMT：需三要素 + XtMiniQmt.exe 进程在跑
  - AKShare：60 次/分钟，须断开 VPN（国内反海外 IP）
  - baostock：每线程独立 `bs.login()`，数据滞后约 1 周
  - TickFlow：60 次/分钟
  - Stooq：JS 浏览器验证
  - 东方财富：反爬严重，3 次重试全失败案例
  - 财经 RSS：偶发 SSL 错误需重试
- **12 个 `_fetch_*.py` 脚本各写各的**——无共享调度/重试/限流基础设施
- **`tmp/` 是 TTL=task_bound 临时目录**——脚本退役后能力丢失，无法形成长期资产

### §1.2 目标

| 目标 | 度量 |
|------|------|
| G1 自动化 | 61 项手动触发数据 → 自动每日/周更新，无需人工介入 |
| G2 差异化策略 | 每个数据源有独立限流/重试/反爬/登录刷新策略 |
| G3 可靠性 | 单日下载成功率 ≥ 99%，最迟 18:30 完成 |
| G4 可观测 | 失败任务 5 分钟内告警，可查进度/重跑 |
| G5 长期资产 | 代码进 `src/zephyr/data/`，不再依赖 `tmp/` |
| G6 平滑迁移 | 12 个 `_fetch_*.py` 分批迁移，迁移期间旧脚本可用 |

### §1.3 范围

**In scope**：
- Provider 抽象层（DataSourceBase + 8 个实现）
- per-source 策略注册表（限流/重试/反爬/登录）
- APScheduler 调度编排（4 档时段）
- 进度统一存储（SQLite，取代 per-script JSON）
- 告警（日志 + 失败汇总文件 + 可选钉钉/邮件）
- CLI（手动触发/查看状态/重跑失败）

**Out of scope**：
- 数据质量门禁（保留在 MOD-L00-001）
- 实时订阅（QMT subscribe 行情）——另起模块
- 数据导出/查询 API——另起模块
- Web 监控 UI——后续 Spiral

---

## §2 模块边界

### §2.1 职责边界

| 做什么 | 不做什么 |
|--------|---------|
| 什么时候下哪个表（调度） | 数据怎么用（策略层职责） |
| 用哪个 Provider 下（路由） | 数据质量校验（DataQualityGate 职责） |
| 限流/重试/反爬（per-source 策略） | 数据存储格式（CTR-001 契约职责） |
| 写入 ClickHouse（TSV） | 数据建模（领域层职责） |
| 进度/断点续传 | 数据清洗（Provider 内部职责） |
| 失败告警 | 业务告警（运维层职责） |

### §2.2 与 _fetch_*.py 的关系

**迁移策略**：分批迁移，迁移期间旧脚本保留可用。

| 阶段 | 迁移内容 | 旧脚本处置 |
|------|---------|-----------|
| 阶段1 | 3 个核心源（iFind/QMT/AKShare）的 Provider 实现 | 保留 |
| 阶段2 | 策略注册表 + 调度器，接入首批 10 个任务 | 保留 |
| 阶段3 | 剩余 5 个 Provider（baostock/tushare/tickflow/tdx/rss） | 保留 |
| 阶段4 | 全部 61 项任务接入调度 | 旧脚本退役删除（TTL=task_bound） |

迁移判据：新 Provider 产出与旧脚本产出**行数一致 + 抽样 100 行字段一致**，方可切换。

---

## §3 架构设计

### §3.1 组件架构

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI (cli.py)                             │
│   integrator run <task> | status | rerun-failed | list      │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Scheduler (scheduler.py)                       │
│   APScheduler 常驻进程                                      │
│   ├─ 16:30 daily  ─ kline_daily/index_kline/valuation       │
│   ├─ 17:00 daily  ─ margin/block_trade/dragon_tiger/money   │
│   ├─ 18:00 daily  ─ rights_issue/dividend/restricted        │
│   └─ 周六 10:00   ─ balance_sheet/income/cashflow/holders   │
└────────┬───────────────────────────────────┬────────────────┘
         │                                   │
┌────────▼──────────┐              ┌────────▼─────────────────┐
│  TaskQueue        │              │  Alerter (alerter.py)     │
│  (task_queue.py)  │              │  ├─ 日志 (logs/)          │
│  ├─ 依赖图 DAG    │              │  ├─ 失败汇总 (failures/)  │
│  ├─ 优先级        │              │  └─ 钉钉/邮件 (可选)       │
│  └─ 并发控制      │              └───────────────────────────┘
└────────┬──────────┘
         │
┌────────▼────────────────────────────────────────────────────┐
│           PolicyRegistry (policy_registry.py)               │
│   per-source 策略查表：RPM/并发/重试/退避/反爬/登录刷新       │
└────────┬────────────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────────────────────┐
│              Provider 层 (implementations/*)                │
│   IFind | MiniQMT | AKShare | Baostock | Tushare            │
│   TickFlow | TDX | RSS                                      │
│   每个实现：fetch(payload) → FetchResult                    │
└────────┬────────────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────────────────────┐
│         ProgressStore (progress_store.py)  SQLite           │
│   统一进度存储，取代 13 个 per-script JSON                  │
└────────┬────────────────────────────────────────────────────┘
         │
┌────────▼────────────────────────────────────────────────────┐
│              ClickHouse (via _ds_common.py)                 │
│   ch_insert_tsv_explicit 写入                                │
└─────────────────────────────────────────────────────────────┘
```

### §3.2 数据流

```
1. Scheduler 触发任务 → TaskQueue.acquire(task_id)
2. TaskQueue 查依赖图 → 所有前置完成？
3. PolicyRegistry.get_policy(source) → SourcePolicy
4. Provider.fetch(payload, policy) →
     ├─ 策略层：限流 sleep / 重试 / 反爬应对 / 登录刷新
     ├─ 业务层：调用 SDK 拉数据
     └─ 返回 FetchResult(rows, stats)
5. ProgressStore.save(task_id, last_key) → 断点续传
6. ch_insert_tsv_explicit(table, rows)
7. Metrics.record(success/latency/rows)
8. 失败 → Alerter.notify(task_id, error)
```

### §3.3 任务状态生命周期

```
PENDING → RUNNING → SUCCESS
              ↓
            FAILED → (重试≤N次) → RUNNING
              ↓
            DEAD (重试耗尽) → 告警 → 人工介入 → CLI rerun
```

---

## §4 Provider 抽象层

### §4.1 DataSourceBase 接口

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator
import datetime

@dataclass
class FetchPayload:
    """下载请求"""
    table: str                    # 目标 ClickHouse 表（c1_market.kline_daily）
    symbols: list[str] | None     # 标的列表，None=全市场
    start: datetime.date          # 起始日期（含）
    end: datetime.date            # 结束日期（含）
    incremental: bool = True      # 增量 vs 全量
    extra: dict = None            # 数据源专属参数

@dataclass
class FetchResult:
    """下载结果"""
    table: str
    rows_fetched: int
    rows_written: int
    last_key: str                 # 断点续传用的最后键值（如最大日期/最大ID）
    elapsed_sec: float
    skipped: int = 0              # 跳过行数（已存在/脏数据）
    error: str | None = None

class DataSourceBase(ABC):
    """数据源 Provider 抽象基类"""

    source_name: str              # "ifind" / "miniqmt" / "akshare" ...
    meta: "DataSourceMeta"

    @abstractmethod
    def connect(self) -> None:
        """建立连接/登录（线程局部）"""

    @abstractmethod
    def health_check(self) -> bool:
        """探活（用于启动时验证 + 运行中监控）"""

    @abstractmethod
    def fetch(self, payload: FetchPayload, policy: "SourcePolicy") -> Iterator[FetchResult]:
        """按策略拉取数据，返回结果迭代器（支持分批）"""

    @abstractmethod
    def disconnect(self) -> None:
        """关闭连接/登出"""
```

### §4.2 DataSourceMeta 元数据

```python
@dataclass
class DataSourceMeta:
    name: str                     # "ifind"
    display_name: str             # "同花顺 iFind"
    auth_type: str                # "license_key" / "account" / "anonymous"
    requires_process: bool        # 是否需外部进程在跑（QMT 需 XtMiniQmt.exe）
    thread_safety: str            # "thread_local" / "shared" / "single_thread"
    rate_limit_default: int       # 默认 RPM
    capabilities: list[str]       # ["kline_daily", "financial_statement", ...]
    known_issues: list[str]       # ["月度配额-4318", "试用账号不支持沪深港通"]
```

### §4.3 Per-source 实现清单

| Provider | source_name | SDK | 登录方式 | 线程安全 | 核心能力 |
|----------|-------------|-----|---------|---------|---------|
| IFindProvider | ifind | iFinDPy | THS_iFinDLogin(user,pwd) | thread_local | THS_RQ/THS_BD/iwencai/EDB |
| MiniQMTProvider | miniqmt | xtquant | 三要素 + 进程在跑 | single_thread | 行情/财务/板块/期权Greeks |
| AKShareProvider | akshare | akshare | 无需登录 | shared（但内部有限流） | 分红/质押/解禁/宏观/股东 |
| BaostockProvider | baostock | baostock | bs.login() 匿名 | **thread_local**（每线程独立登录） | K线/财务（滞后1周） |
| TushareProvider | tushare | tushare | token | shared | 新闻（历史截止2024-08） |
| TickFlowProvider | tickflow | tickflow | 无需 key | shared | 美股/港股 K线 |
| TDXProvider | tdx | mootdx/pytdx | bestip | shared | 板块指数/板块信息 |
| RSSProvider | rss | feedparser/requests | 无 | shared | 财经新闻爬虫 |

### §4.4 迁移映射表

| _fetch_*.py | 目标 Provider | 目标任务 |
|-------------|--------------|---------|
| _fetch_valuation.py | IFindProvider | daily_valuation 增量 |
| _fetch_index_constituent.py | IFindProvider | index_constituent 全量 |
| _fetch_industry_class.py | IFindProvider | industry_class 全量 |
| _fetch_hk_daily_kline.py | MiniQMTProvider | hk_daily_kline 增量 |
| _fetch_futures_kline.py | MiniQMTProvider | futures_kline 增量 |
| _fetch_margin_trading.py | IFindProvider | margin_trading 增量 |
| _fetch_block_trade.py | IFindProvider | block_trade 增量 |
| _fetch_dragon_tiger.py | IFindProvider | dragon_tiger 增量 |
| _fetch_money_flow.py | IFindProvider | money_flow 增量 |
| _fetch_macro_data.py | AKShareProvider | macro_data 增量 |
| _fetch_analyst_forecast.py | AKShareProvider | analyst_forecast 增量 |
| _fetch_us_index.py | TickFlowProvider | us_index 增量 |

---

## §5 策略注册表

### §5.1 SourcePolicy 数据结构

```python
@dataclass
class SourcePolicy:
    """per-source 调用策略"""
    # 限流
    rpm: int                      # 每分钟最大请求数（0=不限）
    concurrency: int              # 最大并发数（1=串行）
    min_interval_sec: float       # 两次调用最小间隔（秒）

    # 重试
    max_retries: int              # 最大重试次数
    backoff: str                  # "exponential" / "fixed" / "jittered"
    initial_wait_sec: float       # 首次重试等待
    retry_on: list[str]           # 重试触发的错误码/异常名

    # 反爬
    use_proxy: bool               # 是否走代理
    proxy: str | None
    disconnect_vpn: bool          # AKShare 须断 VPN
    user_agent: str | None        # 自定义 UA
    respect_robots_txt: bool

    # 登录刷新
    session_ttl_sec: int          # 登录会话有效期（0=永久）
    relogin_on_auth_error: bool   # 401/登录失效自动重登

    # 数据源专属
    extra: dict                   # 如 iFind 月度配额监控
```

### §5.2 跨源策略矩阵（从操作手册抽取）

| 数据源 | RPM | 并发 | 重试 | 退避 | 反爬 | 登录刷新 |
|--------|-----|------|------|------|------|---------|
| **iFind** | 0（配额制） | 1 | 3 | exponential 2s/4s/8s | 无 | 月度配额 -4318 时停跑；登录失效重登 |
| **miniQMT** | 0 | 1（单线程） | 3 | fixed 1s | 无 | 探测 XtMiniQmt.exe 进程；掉线重连 |
| **AKShare** | 60 | 4 | 5 | jittered 2s±0.5 | **断 VPN**；东财接口 3 次失败跳过 | 无需登录 |
| **baostock** | 60 | 8（每线程独立 login） | 3 | fixed 2s | 无 | 每线程 bs.login()；登出 bs.logout() |
| **tushare** | 200 | 2 | 3 | exponential 1s/2s/4s | 无 | token 固定；积分不足告警 |
| **TickFlow** | 60 | 2 | 3 | jittered 1s±0.3 | 无 | 无需登录 |
| **TDX** | 0 | 1 | 3 | fixed 0.5s | bestip 自动选最快服务器 | 无 |
| **RSS** | 0 | 1 | 3 | exponential 5s/10s/20s | 偶发 SSL 重试；尊重 robots.txt | 无 |

### §5.3 策略热更新机制

- 策略参数存 `config/policies.yaml`，调度器每 60 秒重载
- #183 起 policies.yaml 改为派生物：真源在 `architecture_model/data/data_sources_registry.yaml` 的 policy 字段，
  由 `scripts/governance/d5_architecture/generators/generate_policies.py` 单向派生；改真源后 reconciler 自动重生
- 修改 yaml 后无需重启调度器即可生效
- 紧急熔断：CLI `integrator pause <source>` 立即停掉某源所有任务

---

## §6 调度编排层

### §6.1 APScheduler 配置

```python
# scheduler.py 核心配置
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

scheduler = BackgroundScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(url='sqlite:///data/integrator_jobs.db'),
    },
    executors={
        'default': ThreadPoolExecutor(8),       # 通用任务
        'heavy': ThreadPoolExecutor(2),          # iFind/QMT 等串行源
    },
    job_defaults={
        'coalesce': True,                        # 错过多次只跑一次
        'max_instances': 1,                      # 同任务不并发
        'misfire_grace_time': 3600,              # 错过1小时内仍补跑
    },
)
```

### §6.2 调度计划（4 档时段）

| 时段 | cron | 任务 | 数据源 | 说明 |
|------|------|------|--------|------|
| **盘后日K** | 16:30 周一-五 | kline_daily / kline_daily_hfq / kline_daily_none / daily_kline / adj_factor / index_kline / daily_valuation / etf_kline_* / lof_kline_* | iFind + QMT | 日频核心，先跑 |
| **盘后资金** | 17:00 周一-五 | margin_trading / block_trade / dragon_tiger / money_flow / futures_kline / hk_daily_kline / us_daily_kline / us_index / macro_data | iFind + QMT + AKShare + TickFlow | 资金面 + 外盘 |
| **盘后事件** | 18:00 周一-五 | rights_issue / dividend / restricted_shares / disclosure_plan / analyst_forecast / news_data / news_news_info / news_security | AKShare + iFind + RSS + tushare | 事件驱动数据 |
| **周末财务** | 10:00 周六 | balance_sheet / income_statement / cashflow_statement / financial_indicator / main_business / earnings_forecast / express_report / audit_opinion / shareholder_count / top10_shareholders / top10_circulating_shareholders / equity_pledge_detail / equity_pledge_summary | QMT + iFind + AKShare | 低频财务数据 |
| **静态数据** | 09:00 每月1日 | stock_list / index_list / index_constituent / industry_class / trade_calendar / etf_list / lof_list / convertible_bond_list / hk_stock_list | 各源 | 月度刷新 |

### §6.3 任务依赖图

```
adj_factor ──→ kline_daily_hfq ──→ kline_daily_none
                                    ↓
                              kline_weekly / kline_monthly

kline_daily ──→ daily_valuation (PE/PB 基于 kline)
            ──→ etf_kline_* / lof_kline_*

stock_list ──→ (所有依赖标的列表的任务)

index_list ──→ index_constituent ──→ index_kline

(财务三表独立，无依赖)
```

依赖通过 `task_queue.py` 的 DAG 管理，前置未完成则当前任务 PENDING。

### §6.4 并发控制

- **per-source 串行**：iFind/miniQMT/baostock 单线程（API 限制）
- **跨源并行**：16:30 时段 iFind 和 QMT 可并行
- **APScheduler executors**：`default` 池 8 线程给可并行源，`heavy` 池 2 线程给串行源
- **任务级锁**：同一表不允许并发写入（`max_instances=1`）

### §6.5 失败重试与告警

- **任务级重试**：Provider 内部按 SourcePolicy 重试（瞬时错误）
- **调度级重跑**：DEAD 任务进入 `failures/` 目录，CLI `integrator rerun-failed` 一键重跑
- **告警触发**：
  - 任务 DEAD → 立即告警
  - 单日失败率 > 5% → 汇总告警
  - 某数据源连续 3 天失败 → 升级告警
  - iFind 月度配额 -4318 → 立即告警并暂停该源所有任务

---

## §7 进度与断点续传

### §7.1 统一进度存储

```sql
-- SQLite: data/integrator_progress.db
CREATE TABLE task_progress (
    task_id        TEXT NOT NULL,         -- "kline_daily_incremental"
    source         TEXT NOT NULL,         -- "ifind"
    last_run_at    TIMESTAMP,
    last_key       TEXT,                  -- 最大日期 "2026-07-05" 或最大 ID
    last_status    TEXT,                  -- SUCCESS / FAILED / RUNNING
    rows_total     INTEGER,
    error_msg      TEXT,
    PRIMARY KEY (task_id)
);

CREATE TABLE task_runs (
    run_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id        TEXT NOT NULL,
    started_at     TIMESTAMP NOT NULL,
    finished_at    TIMESTAMP,
    status         TEXT,
    rows_fetched   INTEGER,
    rows_written   INTEGER,
    error_msg      TEXT
);
```

取代当前 13 个 per-script JSON 文件（`tmp/_ds_progress/fill_*.json`）。

### §7.2 断点续传协议

1. 任务启动 → 查 `task_progress.last_key` → 作为本次 `payload.start`
2. 分批拉取 → 每批写完 CH → 更新 `last_key`
3. 异常中断 → 下次启动从 `last_key` 继续
4. 幂等：CH 写入用 `INSERT INTO ... ` 配合 ReplacingMergeTree 或先删后插

### §7.3 幂等性保证

| 表引擎 | 幂等策略 |
|--------|---------|
| ReplacingMergeTree | 直接 INSERT，重复键由 CH 后台合并 |
| MergeTree | 写前 `ALTER TABLE ... DELETE WHERE date = today()`（盘后数据） |
| 临时表 | 写入 staging 表，再 `INSERT SELECT DISTINCT` 合并 |

---

## §8 可观测性

### §8.1 日志规范

```
logs/integrator/
├── scheduler.log         # 调度器主日志
├── <source>.log          # per-source 日志（ifind.log / akshare.log / ...）
├── <task>.log            # per-task 日志（kline_daily.log / ...）
└── failures/
    └── YYYY-MM-DD.log    # 每日失败汇总
```

格式：`[time] [level] [task_id] [source] message`

### §8.2 指标

```python
# metrics.py 采集的指标
integrator_task_total{task, status}          # Counter
integrator_task_duration_seconds{task}       # Histogram
integrator_rows_fetched_total{task}          # Counter
integrator_rate_limit_hits_total{source}     # Counter
integrator_retry_total{source}               # Counter
integrator_session_uptime_seconds{source}    # Gauge
```

输出为 Prometheus 文本格式 `data/metrics.prom`，可接 Grafana。

### §8.3 Capability 实测性能记录表（c0_meta.fetch_perf）

> **设计动机**：不同 source.capability 的下载速度差异巨大（实测从 5066 行/秒到 0.09 只/秒，跨度 5 万倍），且存在 API 限流/反爬/损坏等运行时问题。仅靠 `policy_registry` 的策略配置（预期 RPM）无法反映实际运行情况，需持久化实测数据供调度决策和运维排查。

**表结构**（ClickHouse `c0_meta.fetch_perf`）：

| 列 | 类型 | 说明 |
|---|---|---|
| source | String | 数据源（miniqmt/akshare/ifind/...） |
| capability | String | 能力名（kline_daily/adj_factor/...） |
| target_table | String | 目标 ClickHouse 表 |
| test_date | Date | 测试日期 |
| rows_fetched | UInt64 | 实测下载行数 |
| elapsed_sec | Float64 | 实测耗时（秒） |
| rows_per_sec | Float64 | 实测速度（行/秒），0=不适用 |
| symbols_per_sec | Float64 | 标的速度（只/秒），0=不适用 |
| error_count | UInt32 | 错误数 |
| error_rate | Float64 | 错误率（0-1） |
| rate_limited | UInt8 | 是否被限流：0=否，1=是 |
| api_status | String | ok/rate_limited/blocked/broken/slow/pending |
| known_issues | String | 已知问题描述 |
| notes | String | 备注 |
| recorded_at | DateTime | 记录时间（DEFAULT now()） |

**ENGINE**: `ReplacingMergeTree(recorded_at)` ORDER BY (source, capability, test_date) —— 同一 source+capability+date 保留最新记录。

**api_status 枚举**：

| 状态 | 含义 | 示例 |
|---|---|---|
| ok | 正常可用 | miniqmt.kline_daily（14.5 行/秒） |
| slow | 可用但极慢（<1 只/秒） | miniqmt.adj_factor（0.09 只/秒，16h/全量） |
| rate_limited | 可用但被限流，需降速 | akshare.daily_valuation（百度API空响应率15%） |
| blocked | API 被反爬封锁，不可用 | akshare.money_flow（东财 RemoteDisconnected） |
| broken | API 接口损坏，不可用 | akshare.equity_pledge（data_json[result]为None） |
| pending | 尚未测试 | miniqmt.kline_weekly（待下载验证） |

**2026-07-09 首批实测数据**（14 条，覆盖 miniqmt 6 + akshare 8）：

| source | capability | api_status | rows/s | 关键问题 |
|---|---|---|---|---|
| miniqmt | kline_daily | ok | 14.5 | — |
| miniqmt | index_kline | ok | 3.6 | 595只指数逐只 |
| miniqmt | adj_factor | **slow** | 0.09只/s | get_divid_factors 每只11秒，全量16h |
| miniqmt | kline_daily_hfq | ok | 4.6 | 从日K×复权因子计算 |
| miniqmt | kline_weekly | pending | — | 待测 |
| miniqmt | kline_monthly | pending | — | 待测 |
| akshare | daily_valuation | **rate_limited** | 0.17只/s | 百度API空响应率15%，需Event.wait(1s)/股 |
| akshare | margin_trading | ok | 5066 | stock_margin_account_szse 批量 |
| akshare | block_trade | ok | 135 | — |
| akshare | dragon_tiger | ok | 176 | — |
| akshare | share_unlock | ok | — | 无解禁数据 |
| akshare | money_flow | **blocked** | — | 东财反爬封锁，已回退ifind |
| akshare | equity_pledge | **broken** | — | API损坏，已回退ifind |
| akshare | equity_pledge_summary | **broken** | — | 同上 |

**派生用法**：
- 调度器优先级排序：`ok` 状态的 capability 优先调度，`slow`/`rate_limited` 安排在低峰时段
- 退化决策：`blocked`/`broken` 自动回退到备用源（如 akshare→ifind）
- 运维告警：`error_rate > 0.1` 或 `api_status in ('blocked','broken')` 触发告警
- 容量规划：`rows_per_sec` × `目标行数` 估算下载耗时，判断是否能在盘后窗口完成

### §8.4 告警通道

| 通道 | 触发 | 格式 |
|------|------|------|
| 日志 | 所有事件 | 结构化日志 |
| 失败汇总文件 | DEAD 任务 | `failures/YYYY-MM-DD.log` |
| 钉钉 Webhook（可选） | DEAD 任务 + 配额告警 | Markdown 卡片 |
| 邮件（可选） | 连续 3 天失败 | 汇总邮件 |

### §8.5 CLI 自查

```bash
integrator status                 # 查看所有任务今日状态
integrator status <task_id>       # 查看单任务详情
integrator list --source ifind    # 列出某源所有任务
integrator run <task_id>          # 手动触发单任务
integrator rerun-failed           # 重跑今日所有 DEAD 任务
integrator pause <source>         # 紧急熔断某源
integrator resume <source>        # 恢复
```

---

## §9 接口契约

### §9.1 公共 API

```python
# src/zephyr/data/__init__.py
from .provider_base import DataSourceBase, FetchPayload, FetchResult, DataSourceMeta
from .policy_registry import SourcePolicy, PolicyRegistry
from .scheduler import IntegratorScheduler
from .progress_store import ProgressStore
from .alerter import Alerter

def get_integrator() -> IntegratorScheduler:
    """获取调度器单例"""
```

### §9.2 配置文件格式

**config/schedule.yaml**：
```yaml
jobs:
  - id: kline_daily_incremental
    cron: "30 16 * * 1-5"
    provider: ifind
    table: c1_market.kline_daily
    mode: incremental
    depends_on: []
  - id: kline_daily_hfq
    cron: "35 16 * * 1-5"
    provider: local_compute
    table: c1_market.kline_daily_hfq
    depends_on: [kline_daily_incremental, adj_factor_incremental]
```

**config/policies.yaml**（#183 起为派生物，以下示例仅展示格式；真源在 `architecture_model/data/data_sources_registry.yaml` 的 policy 字段）：
```yaml
ifind:
  rpm: 0
  concurrency: 1
  max_retries: 3
  backoff: exponential
  initial_wait_sec: 2.0
  retry_on: ["-201", "TimeoutError", "ConnectionError"]
  session_ttl_sec: 86400
  relogin_on_auth_error: true
  extra:
    monthly_quota_alert: true
akshare:
  rpm: 60
  concurrency: 4
  max_retries: 5
  backoff: jittered
  initial_wait_sec: 2.0
  disconnect_vpn: true
  retry_on: ["HTTPError", "JSONDecodeError"]
```

---

## §10 约束与 NFR

### §10.1 技术约束

- Python 3.11+（与项目一致）
- APScheduler 3.10+
- 数据源 SDK：iFinDPy / xtquant / akshare / baostock / tushare / tickflow / mootdx / feedparser
- ClickHouse 访问：复用 `tmp/_ds_common.py` 的 `ch_insert_tsv_explicit`（WSL 调用）
- 进程模型：单进程多线程（APScheduler BackgroundScheduler + ThreadPoolExecutor）

### §10.2 SLO

| 指标 | 目标 |
|------|------|
| 单日任务成功率 | ≥ 99% |
| 盘后核心数据完成时间 | ≤ 18:30 |
| 周末财务数据完成时间 | ≤ 周六 14:00 |
| 失败告警延迟 | ≤ 5 分钟 |
| 进度查询响应 | ≤ 1 秒 |

### §10.3 容量估算

| 任务 | 单次行数 | 频率 | 年行数 |
|------|---------|------|--------|
| kline_daily 增量 | ~5500 行 | 每交易日 | ~135 万 |
| kline_1min 增量 | ~130 万行 | 每交易日 | ~3.2 亿 |
| tick_history（实盘订阅） | ~5000 万行 | 每交易日 | ~125 亿 |
| balance_sheet 增量 | ~5000 行 | 季度 | ~2 万 |

总磁盘占用年增 < 500GB（按当前 ClickHouse 压缩比）。

---

## §11 错误处理与退化矩阵

| 故障 | 检测 | 退化策略 |
|------|------|---------|
| iFind 登录失效 | health_check 返回 False | 自动 relogin，3 次失败告警 |
| iFind 月度配额耗尽 (-4318) | 错误码捕获 | 暂停该源所有任务，告警 |
| QMT 进程掉线 | 探测 XtMiniQmt.exe | 告警，尝试自动重启（可选） |
| AKShare 反爬 403 | HTTPError | 切代理 / 断 VPN / 跳过该标的 |
| baostock 数据滞后 | last_key < today-7 | 告警，标记该数据 stale |
| ClickHouse 写入失败 | ch_insert 抛异常 | 重试 3 次，仍失败告警 + 数据落本地 TSV 待补 |
| 调度器进程崩溃 | systemd/任务计划重启 | misfire_grace_time 内补跑 |
| 网络中断 | 连接超时 | 指数退避重试，5 次失败告警 |

---

## §12 安全考量

- **凭证管理**：iFind license / QMT 三要素 / tushare token 存 `.env`，不进 git
- **网络代理**：AKShare 须断 VPN；iFind/QMT 走直连
- **进程权限**：调度器以普通用户跑，ClickHouse 通过 WSL 访问
- **日志脱敏**：日志中不打印 license/token 明文

---

## §13 测试策略

| 层级 | 方法 | 工具 |
|------|------|------|
| Provider 单测 | mock SDK，验证 fetch 逻辑 + 策略应用 | pytest + unittest.mock |
| 策略注册表单测 | 验证 yaml 加载 + 热更新 | pytest |
| 调度器集成测 | 用 fake scheduler 触发，验证依赖/并发 | pytest |
| 端到端 | 选 1 个任务（如 macro_data）真跑 AKShare | 手动 + CI |
| 回归 | 迁移判据：新 Provider 产出 vs 旧脚本产出 | 行数 + 抽样 100 行字段比对 |

---

## §14 依赖关系

- **依赖**：
  - MOD-L00-002 操作手册（策略参数来源）
  - MOD-L00-003 需求清单（任务清单来源）
  - `tmp/_ds_common.py`（ClickHouse 写入工具）
- **被依赖**：
  - 未来实盘订阅模块（复用 Provider 抽象）
  - 数据质量门禁（读取集成器写入的数据）
  - 回测/实盘策略层（消费数据）

---

## §15 施工指引

### §15.1 阶段1：Provider 抽象 + 3 个核心源 ✅ 已完成（2026-07-06，commit e1050fc27b）

**交付**：
- `src/zephyr/data/provider_base.py`（DataSourceBase + FetchPayload + FetchResult + DataSourceMeta）
- `src/zephyr/data/implementations/ifind_provider.py`
- `src/zephyr/data/implementations/miniqmt_provider.py`
- `src/zephyr/data/implementations/akshare_provider.py`
- 单测覆盖 3 个 Provider

**验证**：3 个 Provider 能独立 fetch 一个任务，产出与旧脚本一致。

### §15.2 阶段2：策略注册表 + 调度器 + 首批 10 任务 ✅ 已完成（2026-07-06，111/111 单测全绿）

**交付**：
- `src/zephyr/data/policy_registry.py`（SourcePolicy + PolicyRegistry + yaml 加载）
- `src/zephyr/data/scheduler.py`（APScheduler 封装）
- `src/zephyr/data/task_queue.py`（DAG + 优先级）
- `src/zephyr/data/progress_store.py`（SQLite）
- `config/schedule.yaml` + `config/policies.yaml`（#183 起 policies.yaml 为派生物，真源见 data_sources_registry.yaml）
- 接入首批 10 个任务（kline_daily / index_kline / daily_valuation / margin_trading / block_trade / dragon_tiger / money_flow / macro_data / analyst_forecast / us_index）

**验证**：调度器常驻运行 3 天，10 个任务自动触发，成功率 ≥ 99%。

### §15.3 阶段3：剩余 5 个 Provider + 全量任务 ✅ 已完成（2026-07-06，commit 7f89ce95c0，68/68 单测全绿）

**交付**：
- `implementations/baostock_provider.py` / `tushare_provider.py` / `tickflow_provider.py` / `tdx_provider.py` / `rss_provider.py`
- 接入剩余 51 个任务
- `alerter.py` + `metrics.py`

**验证**：61 项手动触发数据全部接入调度，连续 7 天成功率 ≥ 99%。

### §15.4 阶段4：旧脚本退役 + 文档更新 ✅ 已完成（2026-07-06）

**交付**：
- ✅ 12 个 `_fetch_*.py` 脚本已删除（TTL=task_bound 退役，被 Provider 替代）
- ✅ 15 个 `_ds_progress/fill_*.json` 已删除（新 ProgressStore 用 SQLite）
- ✅ `index.md` 更新（状态 Draft→Active/in_progress）
- ✅ `blueprint.md` 加注记（Provider 部分移交本蓝图，已存在）
- ✅ `tmp/generate_acquisition_matrix.py` 重建并重新生成 matrix（61 任务全部接入 tasks.yaml 调度配置）

**验证**：重新运行 `generate_acquisition_matrix.py`，61 项任务全部接入调度（44 有数据 + 15 空表 + 2 已禁用；其中 8 张表已由 `tmp/sql/_create_integrator_missing_tables.sql` 补建，从"表不存在"转为"空表"）。

---

## §16 已知风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| iFind 试用账号配额限制 | 高 | 中 | 配额监控 + 配额耗尽时切 AKShare/baostock 降级 |
| QMT 进程需要桌面会话 | 中 | 高 | 文档明确运行环境要求；未来探索 headless 方案 |
| AKShare 接口不稳定 | 高 | 低 | 5 次重试 + 失败标的跳过 + 次日补跑 |
| 迁移期间新旧脚本冲突 | 中 | 中 | 任务级互斥锁；迁移一个切一个 |
| 调度器进程崩溃 | 低 | 高 | Windows 任务计划守护 + misfire_grace_time |
| ClickHouse WSL 调用性能 | 中 | 中 | 批量写入（每批 ≥ 1 万行） |

---

## §17 决策记录

| 日期 | 决策 | 理由 |
|------|------|------|
| 2026-07-06 | 采用 APScheduler 而非 Windows 任务计划 | 需任务依赖/并发控制/重试编排，OS 级触发器能力不足 |
| 2026-07-06 | per-source 策略注册表而非统一重试装饰器 | 各源差异大（配额/反爬/线程安全），需 per-source 策略对象 |
| 2026-07-06 | 完整集成器（Provider+调度）而非仅调度层 | 现有 Provider 抽象未落地，割裂设计会引用空中楼阁 |
| 2026-07-06 | 接管 blueprint.md 的 Provider 部分 | 原蓝图声称已实现但磁盘不存在，借此次一并重建 |
| 2026-07-06 | SQLite 存进度而非 ClickHouse | 进度查询高频但量小，SQLite 单文件部署简单 |
| 2026-07-06 | 代码进 src/zephyr/data/ 而非 tmp/ | tmp/ 是 TTL=task_bound 临时目录，集成器是长期资产 |

---

## 术语表

- **Provider**：数据源封装类，实现 DataSourceBase 接口
- **SourcePolicy**：per-source 调用策略（限流/重试/反爬/登录）
- **Task**：调度任务单元，对应一个表 + 一个 Provider + 一个策略
- **DAG**：任务依赖图（有向无环图）
- **DEAD**：任务重试耗尽，需人工介入的状态
- **misfire_grace_time**：APScheduler 错过触发时间后仍允许补跑的窗口

---

## 治理信息

- **owner**: data-platform
- **reviewers**: arch / data-eng
- **变更门槛**: 任何 §4-§7 接口变更需评审
- **施工前置**: 本蓝图评审通过 + §15.1 阶段1 启动条件具备
- **验收标准**: §15.4 阶段4 完成，✅稳定获取项数 ≥ 61
