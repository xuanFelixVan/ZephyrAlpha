---
module_id: MOD-L00-002
submodule_path: src/zephyr/data
title: "数据源操作手册 — iFind + miniQMT + 免费开源源 API调用方法与参数坑(实测验证)"
doc_type: blueprint
status: Active
version: "2.3.0"
layer: L2_domain
layer_name: data_source
functional_domain: data
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260703-datasource
valid_from: "2026-07-03"
date: "2026-07-03"
ttl: permanent
construction_progress: verified
actual_disk_path: "src/zephyr/data/"
belongs_to: "MOD-L00-001"
parent_module: "MOD-L00-001"
codification_level: L1
last_updated: "2026-07-10"
generation: 1
rule_form: reference
scope: module
stability: evolving
verifiability: empirical
references:
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_domain_data\\blueprint.md"
    section: "§4 接口契约"
    why: "数据接入层主蓝图——本操作手册是其数据源能力的详细展开"
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\business_data_architecture.md"
    section: "§5 品类全景"
    why: "业务数据库母蓝图——数据源能力需对齐品类全景"
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\sub_blueprints\\c1_market_clickhouse.md"
    section: "§0 8张表"
    why: "C1行情仓库8张表——数据源的下游消费方"
depends_on:
  - target: MOD-L00-001
    at: "§4"
    why: "数据接入层主蓝图"
  - target: MOD-ARCH-BIZDB
    at: "§5"
    why: "业务数据库母蓝图品类全景"
priority: P0
runtime_plane: hot
tags:
  - data-source
  - ifind
  - miniqmt
  - akshare
  - baostock
  - tickflow
  - yfinance
  - stooq
  - tdx
  - mootdx
  - pytdx
  - free-source
  - operation-manual
  - l00
  - ssot
summary: "数据源操作手册——iFind(70个API) + miniQMT(87个API) + 免费无Key源(Baostock/TickFlow/AKShare/财经RSS/国内新闻+公告+政策直连API) + 需Key源(NewsAPI/AlphaVantage/Finnhub/Newsdata/Tiingo) + 通达信(mootdx/pytdx)的API调用方法、参数坑与环境配置。定位为API操作手册：所有调用方法、配置细节、参数坑均已实测验证并固化，AI查询本文档=零幻觉空间，无需重新探索。可下载数据清单见数据库 data_source_assets 表（PostgreSQL depgraph）。"
responsibility_domain: 
design_maturity: design
build_status: stable
---

# 数据源操作手册

## 概述

本文件是 ZephyrAlpha 项目**数据源 API 调用的操作手册（SSoT）**，详细记录 iFind、miniQMT 以及免费开源源（Baostock/TickFlow/AKShare）的 API 调用方法、环境配置与参数坑。所有调用方法均已通过实测验证并固化于本文档。**可下载数据清单见数据库 `data_source_assets` 表**（PostgreSQL depgraph）。

**核心价值**：AI 查询本文档 = 零幻觉空间；AI 绕过本文档自行推断 = 幻觉/漂移根源。本文档存在的意义是**避免 AI 重复探索数据源接入方法**——所有方法已固化，直接复制调用即可。

### 数据获取四层逻辑（硬约束，v1.3.0 升级）

```
┌─────────────────────────────────────────────────────────────┐
│  第一层：淘宝购买历史大数据（便宜快，几块钱买全量历史）      │
│  - 5分钟K线历史(2000-2024)                                  │
│  - Tick数据历史                                             │
│  - 集合竞价历史                                             │
├─────────────────────────────────────────────────────────────┤
│  第二层：iFind 下载（淘宝买不到的 + 未来增量）               │
│  - 估值PE/PB/PS、财务数据、指数成分股、行业分类              │
│  - 日/周/月K线增量更新                                      │
│  - 资金流向(i问财)、概念板块(i问财)                         │
├─────────────────────────────────────────────────────────────┤
│  第三层：QMT 下载实时数据（3秒Tick等高频数据）               │
│  - 3秒Tick(含五档买卖盘)、1/5/15/30/60分钟K线(最近交易日)   │
│  - 期权/可转债/ETF/期货合约与K线                            │
│  - 除权除息因子、实时Tick快照                               │
├─────────────────────────────────────────────────────────────┤
│  第四层：免费开源源（覆盖 iFind 试用盲区，v1.4.0 升级）      │
│  - Baostock → A股日/周/月/分钟K线+季频财务（不受VPN影响）   │
│  - TickFlow → 美股/港股日周月季年K线（免费无Key，不受VPN影响）│
│  - AKShare → EDB宏观+国内新闻+研报（须断VPN）               │
│  - 财经RSS → 国外财经新闻8源(Yahoo/Bloomberg/CNBC等,免费无Key)│
└─────────────────────────────────────────────────────────────┘
```

**核心铁律**：iFind + QMT 能获取的数据优先用 iFind/QMT（已付费、稳定、有 SLA）；免费源作为**补充**，覆盖 iFind 试用账号盲区（A股K线历史/美股/国内外新闻/EDB宏观）。**运维铁律**：下载免费源数据时断开 VPN（Baostock/TickFlow/财经RSS 不受影响，AKShare 必须断开）。详见 §7 免费开源数据源。

---

## §1 数据源总览

### 1.1 iFind（同花顺金融数据接口）

| 属性 | 值 |
|------|-----|
| SDK来源 | `D:\同花顺Ifind金融终端api\THSDataInterface_Windows_20260227\` |
| API数量 | 70个函数，8大接口类别 |
| 数据库规模 | EDB 77,909指标 + FDB 9,875指标 + CodeTables 130万+证券 |
| 当前账号 | 试用账号（IFIND_USERNAME，有限制，见 §2.3） |
| Python版本 | 3.x（无版本限制） |

### 1.2 miniQMT（国金证券QMT xtquant）

| 属性 | 值 |
|------|-----|
| SDK来源 | `D:\国金证券QMT交易端\bin.x64\Lib\site-packages\xtquant\` |
| API数量 | 87个函数 |
| 板块覆盖 | 36个板块（A股/期货/期权/转债/ETF等） |
| 运行要求 | XtMiniQmt.exe 必须运行，is_connected=True |
| Python版本 | **必须 3.11**（pyd文件最高cp311，不支持3.12） |

### 1.3 免费开源源（v1.3.0 实测验证+VPN对比，覆盖 iFind 试用盲区）

| 数据源 | 类型 | 实测通过率 | VPN影响 | 实测日期 | 定位 | 覆盖盲区 |
|--------|------|:----------:|:-------:|:--------:|------|---------|
| **Baostock** | 服务端推送(非爬虫) | **10/10 (100%)** | 无影响 | 2026-07-03 | A股K线+财务主力 | A股日/周/月/分钟K线+季频财务+成分股+交易日历 |
| **TickFlow** | 免费API(无需Key) | **12/12 (100%)** | 无影响 | 2026-07-03 | **美股K线主力** | 美股个股/ETF日周月季年K线+港股+A股(60次/min限制) |
| **AKShare** | 爬虫聚合库 | 11/16 (69%) | ⚠️VPN有害 | 2026-07-03 | 宏观+**国内新闻**+研报+**股东信息**+申万行业 | EDB宏观+东财个股新闻+研报+**十大股东/股权质押/高管增减持/主营业务/申万行业三级**(爬国内网站,**须断开VPN**,§7.1.3) |
| **国内新闻直连API** | 6源直连API | **6/8 (75%)** | ⚠️VPN有害 | 2026-07-03 | **国内新闻+公告主力** | 东财快讯+同花顺+华尔街见闻+金十+财联社(签名修复)+巨潮(公告),免费无Key,**须断VPN** |
| **财经RSS直连** | feedparser RSS | **8/10 (80%)** | 无影响 | 2026-07-03 | **国外新闻主力** | Yahoo/SeekingAlpha/MarketWatch/Bloomberg/FT/Investing/Forbes/CNBC(免费无Key) |
| **NewsAPI.org** | 全球新闻API(需Key) | **2/2 (100%)** | 无影响 | 2026-07-03 | 全球新闻深度 | everything(16822条)+top-headlines(38条),100请求/天,§7.1.1 |
| **Alpha Vantage** | 新闻+行情(需Key) | **2/2 (100%)** | 无影响 | 2026-07-03 | 新闻+情感分析 | NEWS_SENTIMENT(50条,含情感)+日K线(100行),5次/min,§7.1.1 |
| **Finnhub** | 公司新闻+行情(需Key) | **3/3 (100%)** | 无影响 | 2026-07-03 | 公司新闻+报价 | 市场新闻(100条)+AAPL报价(308.63),§7.1.1 |
| **Newsdata.io** | 财经新闻(需Key) | **2/2 (100%)** | 无影响 | 2026-07-03 | 财经新闻补充 | business(5条)+stock(5条),200请求/天,§7.1.1 |
| **Tiingo** | 行情API(需Key) | 1/2 (50%) | 无影响 | 2026-07-03 | 日K线backup | 日K线✅(21行); News❌(需付费),§7.1.1 |
| **TDX/mootdx/pytdx** | 通达信协议直连 | ⚠️ 文档级验证(未实测) | 无影响 | 2026-07-06 | A股K线+板块分类+财务(本地+在线) | A股日/周/月/分钟K线+指数行情+**通达信板块分类**(block_gn/block_fg)+财务数据+本地.day/.lc1/.lc5文件解析;**不支持板块分笔历史+不支持历史分笔**(详见§8) |

> **实测结论（2026-07-03，含VPN对比测试）**：
> - **Baostock 最稳定**（10/10），不受VPN影响，A股K线+财务主力免费源
> - **TickFlow 美股可用**（12/12），不受VPN影响，美股K线主力免费源（2026-07-03新发现，§7.5）
> - **AKShare 宏观+新闻+研报可用**（11/16），但**VPN有害**——爬国内网站(东财/金十/商务部)，挂VPN后国内网站拒绝海外IP，**使用时必须断开VPN**
> - yfinance/Stooq 已废弃（0%通过，VPN无效），详见 §7.4
> - **财经RSS直连可用**（8/10通过，免费无Key，不受VPN影响）——国外新闻主力源，覆盖Yahoo/SeekingAlpha/MarketWatch/Bloomberg/FT/Investing/Forbes/CNBC
> - **运维建议**：下载免费源数据时**断开VPN**（Baostock/TickFlow/财经RSS不受影响，AKShare必须断开）
> - 免费源是 iFind 试用账号盲区的**补充**，不是替代。详见 §7。

---

## §2 iFind 数据源完整指南

### §2.1 环境配置

#### SDK 安装（一次性）

```powershell
# 运行安装脚本，自动创建 .pth 文件指向 x64 目录
py "D:\同花顺Ifind金融终端api\THSDataInterface_Windows_20260227\THSDataInterface_Windows\bin\x64\installiFinDPy.py"
# 安装后 iFinDPy 模块全局可用，无需 sys.path 操作
```

安装脚本会在 Python 的 site-packages 目录创建 `iFinDPy.pth` 文件，内容为：
```
D:\同花顺Ifind金融终端api\THSDataInterface_Windows_20260227\THSDataInterface_Windows\bin\x64\
```

#### 登录方法

```python
from iFinDPy import *
from zephyr.shared.security.secrets import get_secret_or_default

# 登录（0=成功, -201=已登录）；凭据从 .env 读取（IFIND_USERNAME/IFIND_PASSWORD）
r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
if not (r == 0 or r == -201):
    print(f"登录失败: errorcode={r}")
    raise Exception("iFind登录失败")
```

> **注意**：不登录直接调用 API 会返回空 DataFrame。必须先登录。

### §2.2 接口总览（70个API，8大类）

| 接口分类 | 函数名 | 简写 | 功能说明 |
|---------|--------|------|---------|
| 历史行情 | THS_HistoryQuotes | THS_HQ | 日/周/月K线（OHLCV+涨跌幅+换手率） |
| 高频序列 | THS_HighFrequenceSequence | THS_HF | 分钟K线/Tick（Interval参数控制频率） |
| 实时行情 | THS_RealtimeQuotes | THS_RQ | 实时行情快照（含盘口/资金流向） |
| 基础数据 | THS_BasicData | THS_BD | 估值PE/PB/PS + 股票基础信息 |
| 日期序列 | THS_DateSerial | THS_DS | 财务数据时间序列（ROE/净利润/资产等） |
| 数据池 | THS_DataPool | THS_DP | 指数成分股/行业板块成分股 |
| EDB经济库 | THS_EDBQuery | THS_EDB | 宏观经济指标（CPI/M2/利率等） |
| i问财 | THS_iwencai | THS_WC | 自然语言查询（最灵活的接口） |

其他接口：THS_iEvent(事件)、THS_iResearch(研报)、THS_Snapshot(快照)、THS_realTimeValuation(实时估值)、THS_DateQuery(交易日历)、THS_ReportQuery(报告查询)

> 可下载数据清单见数据库 `data_source_assets` 表（PostgreSQL depgraph）。

### §2.3 试用账号限制

#### ⚠️ 试用账号限制（3类，正式账号可解除）

| # | 数据类型 | 错误码 | 限制说明 | 正式账号预期 |
|---|---------|--------|---------|-------------|
| 11 | **5分钟/分钟K线** | -4309 | 试用账号只能获取1年历史 | ✅ 正式账号无限制 |
| 12 | **EDB宏观数据** | -4318 | ⏳ 5万条/周(每周一重置) | ✅ 正式账号同试用版(5万条/周) |
| 13 | **CFFEX期货(中金所)** | -4216 | 中金所权限被拒 | ⚠️ 需正式账号+期货权限 |

#### ❌ 试用账号不支持（4类）

| # | 数据类型 | 错误码 | 原因 |
|---|---------|--------|------|
| 14 | **事件查询(THS_iEvent)** | -5100 | "account type is not supported" |
| 15 | **研究报告(THS_iResearch)** | -5100 | "account type is not supported" |
| 16 | **美股行情** | -4210 | 代码后缀全部报错，试用账号无海外市场权限 |
| 17 | **港股行情** | -4210 | 同上 |

#### 期货数据情况

| 交易所 | 代码示例 | 测试结果 | 说明 |
|--------|---------|---------|------|
| 上期所(SHFE) | CU2607.SHF | ec=0但0行 | 代码格式正确但无数据返回 |
| 大商所(DCE) | A2609.DCE | ec=0但0行 | 同上 |
| 郑商所(CZC) | MA607.CZC | ec=0但0行 | 同上 |
| 中金所(CFFEX) | IF2607.CFE | -4216 | 明确权限拒绝 |

### §2.4 iFind API 调用方法（完整示例，直接复制可用）

#### 2.4.1 登录

```python
from iFinDPy import *
from zephyr.shared.security.secrets import get_secret_or_default
r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
# 0=成功, -201=已登录
```

#### 2.4.2 日/周/月K线（THS_HistoryQuotes）

```python
# 日K线 (Interval:D 日 / W 周 / M 月)
data = THS_HistoryQuotes(
    '600000.SH',  # 股票代码（可逗号分隔多个）
    'preClose,open,high,low,close,avgPrice,change,changeRatio,volume,turnoverRatio,amount,transactionAmount',
    'Interval:D,CPS:1,baseDate:1900-01-01,Currency:YSHB,fill:Previous',
    '2025-06-01',  # 开始日期
    '2025-07-01'   # 结束日期
)
df = THS_Trans2DataFrame(data)
# ✅ 返回 21行 DataFrame
```

**参数说明**：
- `CPS:1` = 前复权, `CPS:2` = 后复权, `CPS:0` = 不复权
- `Currency:YSHB` = 人民币报价
- `fill:Previous` = 缺失值用前值填充

#### 2.4.3 估值数据 PE/PB/PS（THS_BasicData）— ⚠️ 参数格式坑

```python
# ✅ 正确格式: 指标用分号分隔，参数格式为 "日期,类型"
# 类型 100=静态值, 101=动态值
data = THS_BasicData(
    '600000.SH',
    'ths_pe_stock;ths_pb_stock;ths_ps_stock',           # 指标用分号分隔
    '2025-06-30,100;2025-06-30,100;2025-06-30,100'     # 每个指标对应 "日期,类型"，用分号分隔
)
df = THS_Trans2DataFrame(data)
# ✅ 返回 PE=11.45, PB=0.69, PS=...
```

> **坑警告**：参数格式不是简单的日期，而是 `"日期,类型"` 用分号分隔。传错会返回 null。

#### 2.4.4 财务数据时间序列（THS_DateSerial）

```python
data = THS_DateSerial(
    '600000.SH',
    'ths_af_stock;ths_close_price_stock;ths_low_stock;ths_high_price_stock;ths_open_price_stock',
    ';100;100;100;100',  # 每个指标对应一个类型，空表示无参数
    'Days:Alldays,Fill:Previous,Interval:D',
    '2025-01-28',
    '2025-07-01'
)
df = THS_Trans2DataFrame(data)
# ✅ 返回 30行
```

#### 2.4.5 指数/行业成分股（THS_DataPool）

```python
# 指数成分股（沪深300）
data = THS_DataPool(
    'index',                                    # 类型: index=指数成分, block=板块成分
    '2025-06-30;000300.SH',                     # 日期;指数代码
    'date:Y,thscode:Y,security_name:Y'          # 输出字段
)
# ✅ 返回 300行 沪深300成分股

# 行业成分股（同花顺行业指数）
data = THS_DataPool(
    'index',
    '2025-06-30;884183.TI',  # 884183.TI = 船舶制造行业指数
    'date:Y,thscode:Y,security_name:Y'
)
# ✅ 返回 30行 行业成分股
```

#### 2.4.6 实时行情（THS_RealtimeQuotes / THS_RQ）

```python
data = THS_RealtimeQuotes(
    '600000.SH',
    'open;high;low;latest;changeRatio;amount;volume;bid1;ask1;bidSize1;askSize1;inflow;outflow'
)
df = THS_Trans2DataFrame(data)
# ✅ 返回实时行情快照（含盘口+资金流向）
```

##### THS_RQ 批量行情查询（v1.9.0 新增实测，补齐日K线/指数K线缺失数据）

> THS_RQ 支持批量查询多个代码（逗号分隔），返回最近交易日 OHLCV，可用于**批量补齐 kline_daily 和 index_kline 缺失的最新交易日数据**。非交易时段调用返回最近交易日收盘数据。

```python
from iFinDPy import *

# === 批量查询多个股票的日K线数据 ===
# codes_str: 逗号分隔的 iFind 代码（600xxx→.SH, 000/300xxx→.SZ, 8/4xxx→.BJ）
codes_str = "600519.SH,000001.SZ,300750.SZ"
df = THS_RQ(codes_str, "close;open;high;low;volume;amount", "pricetype:1", "format:dataframe")
# ✅ 返回 DataFrame，每行一个代码，含最近交易日 OHLCV
# pricetype:1 = 前复权价

# === 批量补齐 kline_daily（A股，分批每批50个）===
# 代码转换: 6位数字 → iFind 格式
def to_ifind_code(symbol: str) -> str:
    if symbol.startswith(('60', '68', '69')):
        return f"{symbol}.SH"
    elif symbol.startswith(('00', '30', '20')):
        return f"{symbol}.SZ"
    elif symbol.startswith(('8', '4', '9')):
        return f"{symbol}.BJ"
    return None

# 批量查询（每批50个代码，逗号分隔）
batch_codes = ",".join([to_ifind_code(s) for s in symbols[:50]])
df = THS_RQ(batch_codes, "close;open;high;low;volume;amount", "pricetype:1", "format:dataframe")
# ✅ 50行，列: thscode/close/open/high/low/volume/amount

# === 批量补齐 index_kline（指数）===
# 指数代码转换: 000xxx→.SH, 399xxx→.SZ, 880xxx→.TDX, 881xxx→.TI
def to_ifind_index_code(code: str):
    if code.startswith('000'):
        return code + ".SH", "SH"
    elif code.startswith('399'):
        return code + ".SZ", "SZ"
    elif code.startswith('880'):
        return code + ".TDX", "TDX"
    elif code.startswith('881'):
        return code + ".TI", "TI"
    return None, None
```

> THS_RQ 是批量补齐日K线/指数K线缺失数据的**最优方案**（批量+快速+前复权）

##### THS_BD 基础数据接口限制（v1.9.0 实测补充）

> THS_BD 有以下重要限制需注意：

| 限制 | 说明 | 影响 |
|------|------|------|
| **不支持分号分隔多指标** | `THS_BD(codes, "ths_pledge_ratio_stock;ths_total_shares_stock", ...)` 返回 -209 | 需分次单独查询每个指标，然后合并结果 |
| **分红相关指标全部失败** | ths_latest_dividend_plan_stock / ths_dividend_announce_date_stock / ths_dividend_cash_ps_stock 等全部 -209 | 分红明细不可用 THS_BD 获取，需用 AKShare stock_history_dividend_detail |
| **股权质押字段部分不可用** | ths_pledge_ratio_stock ✅ + ths_total_shares_stock ✅，但 pledge_count/unrestricted_pledge/restricted_pledge ❌ | 股权质押只能拿比例和总股本，其他字段留空 |
| **单位转换坑** | ths_total_shares_stock 返回单位为"股"，表字段 total_shares 单位为"万" → 需 /1e4 | 不转换会导致数量级错误 |
| **PCF指标不可用** | ths_pcf_stock_ttm 返回 -209 | PCF改用i问财(THS_iwencai)查`"{ts_code} 市现率"`补齐当天值，历史值由AKShare全量刷新补齐（见§2.4.7 i问财） |

##### THS_DS 日期序列接口限制（v1.9.0 实测补充）

> **2026-07-05 实测**：THS_DS 单代码查询返回 -209 "params invalid"，即使按文档格式传参也无法使用。补齐日K线/指数K线数据应改用 THS_RQ（批量实时行情）。

##### i问财查询限制补充（v1.9.0 实测）

> **2026-07-05 实测**：i问财（THS_WC）不适合查询**个股分红明细**。以下查询全部失败：
> - "分红公告日在2026年6月28日到2026年7月5日之间的股票" → -1201 failed
> - "近期有分红公告的股票" → -4001 no data
> - "分红方案 2026年7月" → -1201 failed
> - "600519 分红" → -1201 failed
>
> **结论**：i问财适合查询**概念板块/龙虎榜/融资融券/大宗交易/限售解禁**等聚合类数据，但不适合查询按日期范围筛选的个股分红明细。分红明细需用 **AKShare stock_history_dividend_detail**（见 §7.3.5）。

#### 2.4.7 i问财自然语言查询（THS_iwencai）— 最灵活的接口

```python
# i问财: 用中文提问获取数据
data = THS_iwencai('2025年6月30日主力资金净流入前10只股票', 'stock')
# ✅ 返回 股票代码/股票简称/主力资金流向/排名

data = THS_iwencai('同花顺概念板块列表', 'stock')
# ✅ 返回 概念板块列表

data = THS_iwencai('600000.SH 近5天主力资金流向', 'stock')
# ✅ 返回 区间资金流向
```

**i问财已验证的查询能力（2026-07-03实测，16项全部✅）**：

| 查询语句 | 返回行数 | 返回字段 |
|---------|---------|---------|
| "2025年6月30日龙虎榜个股" | 5536 | 股票代码/简称/上榜次数 |
| "2025年6月融资融券余额前10只股票" | 10 | 股票代码/简称/融资融券余额/排名 |
| "2025年6月大宗交易个股" | 1340 | 股票代码/简称/大宗交易日期 |
| "2025年7月限售解禁个股" | 254 | 股票代码/简称/解禁日期/股数/比例/金额 |
| "600000.SH 2024年审计意见" | 1 | 股票代码/简称/审计意见类别 |
| "2025年6月30日涨停股票" | 91 | 股票代码/简称/涨停 |
| "2025年6月30日跌停股票" | 5 | 股票代码/简称/跌停 |
| "ST股票列表" | 211 | 股票代码/股票简称 |
| "2025年6月新股上市" | 8 | 股票代码/简称/新股上市日期 |
| "600000.SH 股东人数" | 1 | 股票代码/简称/最新股东户数 |
| "600000.SH 每股收益" | 1 | 股票代码/简称/基本每股收益(多年) |
| "600000.SH 机构持仓" | 1 | 股票代码/简称/机构持股占流通股比例 |
| "600000.SH 业绩预告" | 1 | 股票代码/简称/预告净利润 |
| "2025年6月回购股票" | 705 | 股票代码/简称/回购公告日/截止日/数量 |
| "2025年6月高管增减持" | 378 | 股票代码/简称/高管变动股数合计 |
| "600000.SH 分红" | 1 | 股票代码/简称/分红明细 |

> ❌ **i问财不可查**：研报评级(需THS_iResearch正式账号)、北向资金(4种查询都-4001 no data)

**i问财局限**：查询"美股"/"港股"/"期货"时返回的是A股相关概念股，不是真正的海外/期货数据。试用账号通过i问财只能查询A股数据。但i问财可灵活查询A股的龙虎榜/融资融券/大宗交易/限售解禁/审计意见/涨停跌停/ST/新股/股东/机构持仓/业绩预告/回购/增减持/分红等16类数据，是iFind中最灵活的接口。

#### 2.4.8 EDB宏观数据（THS_EDBQuery）— ⏳ 5万条/周(每周一重置)

```python
# EDB = Economic Data Base，77,909个宏观/行业经济指标
# 分类: 中国宏观11,762 + 行业经济24,522 + 全球宏观12,385 + 利率1,646 + 经济景气991 + 世界经济3,573 + 区域宏观23,030
data = THS_EDBQuery(
    'M001620326;M002822183',  # 指标代码（分号分隔）
    '2025-01-01',
    '2025-06-30'
)
# ⏳ 试用账号 -4318 "exceeded this week" 周配额超限，每周一自动重置(试用版=正式版,均5万条/周)
```

#### 2.4.9 组合查询（获取行业成分股的实时行情）

```python
# 1. 获取行业成分股
thsData = THS_DataPool('index', '2025-06-30;884183.TI', 'date:Y,thscode:Y,security_name:Y')
ths_codes = ','.join(thsData['tables'][0]['table']['THSCODE'])

# 2. 批量获取实时行情
thsdata = THS_RealtimeQuotes(ths_codes,
    'open;high;low;latest;changeRatio;amount;volume;bid1;ask1;bidSize1;askSize1;inflow;outflow')
result = THS_Trans2DataFrame(thsdata)
```

### §2.5 iFind EDB 宏观数据库详解

EDB = Economic Data Base（经济数据库），iFind的宏观/行业经济指标库，共 **77,909个指标**：

| 类别 | 指标数 | 示例指标 |
|------|-------|---------|
| 中国宏观 | 11,762 | CPI、PPI、PMI、M0/M1/M2、GDP、社融、外汇储备 |
| 行业经济 | 24,522 | 钢材产量、汽车销量、发电量、水泥产量、手机出货量 |
| 全球宏观 | 12,385 | 美国非农、欧盟CPI、日本GDP、各国利率决议 |
| 利率 | 1,646 | 国债收益率曲线、Shibor、LPR、MLF利率 |
| 经济景气 | 991 | 消费者信心指数、制造业PMI分项、景气先行指数 |
| 世界经济 | 3,573 | OECD领先指标、IMF预测、世界银行数据 |
| 区域宏观 | 23,030 | 各省市GDP、地方财政、区域工业增加值 |

**策略价值**：宏观因子是策略共振的核心维度（如M2增速→流动性→板块轮动；PMI→周期股择时；国债收益率→估值贴现率）。

---

## §3 miniQMT 数据源完整指南

### §3.1 环境配置（三要素 + 参数坑，缺一不可）

> ⚠️ **这是最容易踩坑的部分。所有配置必须严格按以下顺序执行，任何一个错误都会导致"周期错误"或导入失败。**

#### 要素1：Python 版本必须 3.11

```powershell
# 必须用 py -3.11 运行，不支持 3.12
py -3.11 your_script.py
```

**原因**：xtquant 的 pyd 文件最高只到 cp311（Python 3.11），Python 3.12 会报 `ModuleNotFoundError: No module named 'xtquant.IPythonApiClient'`。

#### 要素2：sys.path.append（不能用 insert）

```python
import sys
qmt_xtquant = r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages'
sys.path.append(qmt_xtquant)   # ✅ 用 append
# sys.path.insert(0, qmt_xtquant)  # ❌ 不能用 insert！会覆盖系统 numpy
```

**原因**：`insert(0, ...)` 会把 QMT 的 site-packages 放在 sys.path 最前面，覆盖系统 numpy，导致 `Missing required dependencies ['numpy', 'pytz']`。`append` 把 QMT 路径放在末尾，不影响系统包优先级。

#### 要素3：os.chdir 到 QMT bin.x64 目录（关键！）

```python
import os
os.chdir(r'D:\国金证券QMT交易端\bin.x64')  # 关键!
```

**原因**：xtquant 的 `data_dir` 默认是相对路径 `../userdata_mini/datadir`。如果不 chdir，从 `d:\ZephyrAlpha` 运行时会解析为 `d:\userdata_mini\datadir`（不存在），导致所有 K线/Tick API 报"周期错误"。

#### 🚫 禁止：修改 xtdata.data_dir

```python
# ❌ 绝对不能这样做！
xtdata.data_dir = r'D:\国金证券QMT交易端\userdata_mini\datadir'
# 这会破坏底层 C++ 函数，导致 get_market_data_ex / get_local_data 报"周期错误"
```

**原因**：`get_local_data` 等函数的默认参数 `data_dir=data_dir` 在模块加载时就绑定了。修改 `xtdata.data_dir` 不会更新已绑定函数的默认参数，但会破坏底层 C++ 函数对路径的处理逻辑。必须用 `os.chdir` 让相对路径正确解析。

#### 完整初始化模板（直接复制）

```python
import sys, os

# 要素1: sys.path.append（不能用 insert）
qmt_xtquant = r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages'
sys.path.append(qmt_xtquant)

# 要素2: os.chdir 到 QMT bin.x64 目录
os.chdir(r'D:\国金证券QMT交易端\bin.x64')

# 要素3: 导入并验证连接
from xtquant import xtdata
client = xtdata.get_client()
assert client.is_connected(), "QMT未连接，请确保 XtMiniQmt.exe 正在运行"
```

#### QMT 客户端运行要求

- 进程名：`XtMiniQmt.exe`（miniQMT 模式，不是完整交易终端）
- 验证方法：`xtdata.get_client().is_connected()` 返回 `True`
- 数据目录：`D:\国金证券QMT交易端\userdata_mini\datadir\`（含 `SH/86400/`、`SZ/86400/`、`DividData/` 等子目录）

### §3.2 接口总览（87个API）

xtquant 包含 87 个 API 函数，核心分类：

| 分类 | 关键函数 | 说明 |
|------|---------|------|
| 行情下载 | download_history_data, download_history_data2 | 下载历史K线/Tick到本地 |
| 行情获取 | get_market_data_ex, get_market_data, get_local_data | 读取本地/服务器行情 |
| 实时行情 | get_full_tick, subscribe_quote, subscribe_whole_quote | 实时Tick快照/订阅推送 |
| Level-2 | get_l2_order, get_l2_quote, get_l2_transaction | 逐笔委托/成交/行情（需L2权限） |
| 财务数据 | download_financial_data2, get_financial_data | 11张财务报表 |
| 期权 | get_option_list, get_option_detail_data, get_option_undl_data | 期权合约/Greeks/标的 |
| 可转债 | get_cb_info, download_cb_data | 可转债详情 |
| ETF | get_etf_info | ETF详情 |
| 指数 | download_index_weight, get_index_weight | 指数权重 |
| 复权 | get_divid_factors, getDividFactors | 除权除息因子 |
| 行业 | get_industry | 行业分类 |
| 期货 | get_main_contract, download_history_contracts | 主力合约/历史合约 |
| 交易日历 | get_trading_calendar, get_trading_dates, get_holidays | 交易日/假日 |
| 板块 | get_sector_list, get_stock_list_in_sector, download_sector_data | 板块/成分股 |
| 股票详情 | get_instrument_detail, get_instrument_type, get_stock_type | 股票基础信息 |

> 可下载数据清单见数据库 `data_source_assets` 表（PostgreSQL depgraph）。

### §3.3 数据频率支持

| 频率代码 | 说明 | 对应C1表 |
|---------|------|---------|
| tick | 3秒Tick（含买卖盘） | tick_data |
| 1m | 1分钟K线 | kline_1min |
| 5m | 5分钟K线 | kline_5min |
| 15m | 15分钟K线 | kline_15min |
| 30m | 30分钟K线 | kline_30min |
| 1h | 60分钟K线 | kline_60min |
| 1d | 日K线 | daily_kline |
| 1w | 周K线 | kline_weekly |
| 1mon | 月K线 | kline_monthly |

### §3.4 miniQMT API 调用方法（完整示例，直接复制可用）

#### 3.4.1 初始化（必须）

```python
import sys, os

# 三要素配置
qmt_xtquant = r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages'
sys.path.append(qmt_xtquant)                          # 要素1: append不是insert
os.chdir(r'D:\国金证券QMT交易端\bin.x64')             # 要素2: chdir到QMT目录

from xtquant import xtdata
client = xtdata.get_client()
assert client.is_connected(), "QMT未连接"              # 要素3: 验证连接
```

#### 3.4.2 日K线（注意参数顺序坑！）

```python
# ⚠️ 参数顺序: (field_list, stock_list, period, start_time, end_time)
#                 0           1           2       3           4
# period 在第3位！不是第5位！

# ✅ 正确
data = xtdata.get_market_data_ex([], ['600000.SH'], '1d', '20250601', '20250630')
# 返回 {'600000.SH': DataFrame(20行)}

# ❌ 错误（会报"周期错误"）
# data = xtdata.get_market_data_ex([], ['600000.SH'], '20250601', '20250630', '1d')
# → period='20250601' 不在 {'1m','5m','15m','30m','1h','1d'} 中
```

#### 3.4.3 下载历史数据 + 获取（两步）

```python
# 步骤1: 下载（返回None是正常的！源码无return语句）
xtdata.download_history_data('600000.SH', '1d', '20240101', '20250630')
# 参数: (stock_code, period, start_time, end_time)
# 返回 None = 正常，数据已异步下载到本地

# 步骤2: 获取（从本地读取）
data = xtdata.get_market_data_ex([], ['600000.SH'], '1d', '20240101', '20250630')
df = data['600000.SH']  # ✅ 359行
```

#### 3.4.4 5分钟K线 / 1分钟K线 / Tick（最近交易日）

```python
# 5分钟K线（只能下载最近交易日）
xtdata.download_history_data('600000.SH', '5m', '20260702', '20260702')
data = xtdata.get_market_data_ex([], ['600000.SH'], '5m', '20260702', '20260702')
# ✅ 48行

# 1分钟K线
xtdata.download_history_data('600000.SH', '1m', '20260702', '20260702')
data = xtdata.get_market_data_ex([], ['600000.SH'], '1m', '20260702', '20260702')
# ✅ 241行

# Tick数据（3秒，含五档买卖盘）
xtdata.download_history_data('600000.SH', 'tick', '20260702', '20260702')
data = xtdata.get_market_data_ex([], ['600000.SH'], 'tick', '20260702', '20260702')
# ✅ 4998行
```

#### 3.4.5 前复权K线

```python
# dividend_type: 'none'(不复权) / 'front'(前复权) / 'back'(后复权) / 'front_ratio' / 'back_ratio'
data = xtdata.get_market_data_ex(
    [], ['600000.SH'], '1d', '20250601', '20250630',
    -1,           # count: -1=全部
    'front'       # dividend_type: 前复权
)
```

#### 3.4.6 实时Tick快照

```python
tick = xtdata.get_full_tick(['600000.SH', '000001.SZ'])
# 返回 {'600000.SH': {lastPrice, open, high, low, volume, amount,
#                     askPrice:[5档], bidPrice:[5档], askVol:[5档], bidVol:[5档], ...}}
```

#### 3.4.7 交易日历（market参数坑）

```python
# ✅ 正确: market用 'SH' 或 'SZ'
dates = xtdata.get_trading_dates('SH', '20250601', '20250701')
# ✅ 21天

# ❌ 错误: market用 'SSE' 或 'SZSE' 会返回空
# dates = xtdata.get_trading_dates('SSE', '20250601', '20250701')  # 空!

# 全量交易日历
cal = xtdata.get_trading_calendar('SH')  # ✅ 8673天，从19901219开始
```

#### 3.4.8 股票/合约列表

```python
stocks = xtdata.get_stock_list_in_sector('沪深A股')   # ✅ 5207只
opts   = xtdata.get_stock_list_in_sector('上证期权')   # ✅ 662个
cb     = xtdata.get_stock_list_in_sector('上证转债')   # ✅ 152个
etf    = xtdata.get_stock_list_in_sector('沪市ETF')    # ✅ 946个
cffex  = xtdata.get_stock_list_in_sector('中金所')     # ✅ 802个
```

#### 3.4.9 除权除息因子

```python
df = xtdata.get_divid_factors('600000.SH')
# ✅ 26条记录（2000年至今），含 interest/stockBonus/allotPrice/gugai/dr 等字段
```

#### 3.4.10 股票详情

```python
detail = xtdata.get_instrument_detail('600000.SH')
# ✅ 含 InstrumentName/UpStopPrice/DownStopPrice/FloatVolume/TotalVolume/OpenDate 等
```

#### 3.4.11 批量下载多只股票

```python
codes = ['600000.SH', '000001.SZ', '600519.SH', '000858.SZ', '601318.SH']
# 批量下载
for code in codes:
    xtdata.download_history_data(code, '1d', '20250601', '20250630')
# 批量获取
data = xtdata.get_market_data_ex([], codes, '1d', '20250601', '20250630')
# ✅ 各20行
```

### §3.5 财务数据 API（11张报表）

`get_financial_data(stock_list, table_list, start_time, end_time, report_type)` 的 `table_list` 可选值：

| table_list值 | 报表名 | 说明 |
|-------------|--------|------|
| Balance | ASHAREBALANCESHEET | 资产负债表 |
| Income | ASHAREINCOME | 利润表 |
| CashFlow | ASHARECASHFLOW | 现金流量表 |
| Capital | CAPITALSTRUCTURE | 资本结构 |
| HolderNum | SHAREHOLDER | 股东人数 |
| Top10Holder | TOP10HOLDER | 前十大股东 |
| Top10FlowHolder | TOP10FLOWHOLDER | 前十大流通股东 |
| PensionHolder | — | 养老金持股 |
| Top10NSHolder | — | 前十大非流通股东 |
| Top10NSFlowHolder | — | 前十大非流通流通股东 |
| Performance | — | 业绩快报 |
| ProfitForecast | — | 盈利预测 |

```python
# 下载财务数据
xtdata.download_financial_data2(['600000.SH'], '', '20240101', '20250630')
# 获取（table_list为空=全部）
fd = xtdata.get_financial_data(['600000.SH'], [], '20240101', '20250630', 'report_time')
# report_type: 'announce_time'(公告日) / 'report_time'(报告期)
```

### §3.6 miniQMT 36个板块列表

| # | 板块名称 | 说明 |
|---|---------|------|
| 1 | 上期所 | 上海期货交易所合约 |
| 2 | 上证A股 | 上海证券交易所A股 |
| 3 | 上证B股 | 上海证券交易所B股 |
| 4 | 上证期权 | 上海证券交易所期权 |
| 5 | 上证转债 | 上海证券交易所可转债 |
| 6 | 中金所 | 中国金融期货交易所 |
| 7 | 京市A股 | 北京证券交易所A股 |
| 8 | 创业板 | 深圳创业板 |
| 9 | 大商所 | 大连商品交易所 |
| 10 | 沪市ETF | 上海ETF |
| ... | (共36个板块) | 含沪深A股/港股通/期货/期权/转债等 |

---

## §4 iFind vs miniQMT vs TDX 对比矩阵

### §4.1 能力对比总表

| # | 数据类型 | iFind 试用账号 | miniQMT | TDX/mootdx | 推荐来源 | 说明 |
|---|---------|:--------------:|:-------:|:----------:|---------|------|
| 1 | 日K线 | ✅ 21行 | ✅ 已验证(359行) | ✅ frequency=9 | 两者均可 | QMT 可下载长历史，iFind 增量更新 |
| 2 | 周K线 | ✅ 5行 | ✅(1w周期) | ✅ frequency=5 | iFind | iFind 字段更全（含换手率） |
| 3 | 月K线 | ✅ | ✅(1mon周期) | ✅ frequency=6 | iFind | 同上 |
| 4 | 1分钟K线 | ❌ 试用限制(-4309) | ✅ 已验证(241行) | ✅ frequency=7/8 | **QMT** | QMT 可下载最近交易日 |
| 5 | 5分钟K线 | ❌ 试用限制(-4309) | ✅ 已验证(48行) | ✅ frequency=0 | **QMT** | 历史需淘宝购买 |
| 6 | 15/30/60分钟K线 | ❌ 试用限制 | ✅(15m/30m/1h) | ✅ frequency=1/2/3 | **QMT** | 同上 |
| 7 | 3秒Tick | ❌ | ✅ 已验证(4998行) | ⚠️ 仅最近交易日分笔 | **QMT 独有** | QMT含五档买卖盘；TDX仅个股分笔(无五档) |
| 8 | 集合竞价 | ❌ | ✅ API可用 | ❌ | **QMT 独有** | subscribe_quote |
| 9 | 实时Tick快照 | ✅ | ✅ 已验证 | ✅ client.quote() | QMT | QMT 的 get_full_tick 字段更全 |
| 10 | 估值 PE/PB/PS | ✅ | ❌ | ❌ | **iFind 独有** | iFind THS_BasicData |
| 11 | 财务数据 | ✅ 时间序列 | ✅ API可用(11张表) | ✅ Affair.fetch(gpcw*.zip) | 两者均可 | QMT 报表结构化，iFind 灵活查询；TDX财务数据需下载zip解压 |
| 12 | 资金流向 | ✅ i问财 | ❌ | ❌ | **iFind 独有** | i问财可自然语言查询 |
| 13 | 指数成分股 | ✅ 300行 | ✅ API可用 | ⚠️ 板块成分(block_*.dat) | iFind | iFind 已验证；TDX仅板块成分非指数成分 |
| 14 | 行业分类 | ✅ 30行 | ⚠️ 返回空 | ✅ **通达信板块分类** | iFind+TDX | iFind同花顺行业；TDX 880xxx体系(详见§8) |
| 15 | 概念板块 | ✅ i问财 | ❌ | ✅ **block_gn.dat** | iFind+TDX | iFind i问财；TDX通达信概念板块 |
| 16 | EDB 宏观数据 | ⏳ 5万条/周(-4318,每周一重置) | ❌ | ❌ | iFind(试用=正式) | 仅 iFind 有，77,909指标 |
| 17 | 期货数据 | ❌ 无权限 | ✅ 802个合约 | ⚠️ ExtQuotes | **QMT 独有** | QMT 有中金所/上期所/大商所；TDX扩展行情支持期货 |
| 18 | 期权数据 | ❌ | ✅ 662个合约 | ❌ | **QMT 独有** | QMT 有上证期权 |
| 19 | 可转债数据 | ❌ | ✅ 152个+K线 | ❌ | **QMT 独有** | QMT 有上证转债 |
| 20 | ETF数据 | ❌ | ✅ 946个+K线 | ⚠️ K线 | **QMT** | QMT 有沪市ETF |
| 21 | 美股/港股 | ❌ 无权限(-4210) | ✅ 港股通已验证(957只+K线20行) | ⚠️ ExtQuotes港股 | QMT(港股通) | 美股试用受限，港股QMT可获取；TDX扩展行情支持港股(market=47) |
| 22 | 新闻/事件 | ❌ 不支持(-5100) | ❌ | ❌ | 无 | 试用账号不支持 |
| 23 | 研究报告 | ❌ 不支持(-5100) | ❌ | ❌ | 无 | 试用账号不支持 |
| 24 | Level-2数据 | ❌ | ⚠️ 需L2权限 | ❌ | QMT | 需开通L2权限 |
| 25 | 除权除息因子 | ❌ | ✅ 已验证(26条) | ❌ | **QMT 独有** | — |
| 26 | 指数权重 | ❌ | ✅ API可用 | ❌ | **QMT 独有** | — |
| 27 | 交易日历 | ✅ THS_DateQuery | ✅ 8673天 | ⚠️ 间接(从K线推断) | 两者均可 | QMT 已验证 |
| 28 | **板块分笔历史** | ❌ | ❌ | ❌ | **无API**(淘宝购买) | 用户已购sector/mkt_index板块分笔(2011-11~2026-07)，**无API可持续更新**，需手工导出(详见§8.6) |
| 29 | **本地通达信数据文件** | ❌ | ❌ | ✅ **Reader.factory** | **TDX 独有** | .day/.lc1/.lc5文件解析(需安装通达信客户端) |
| 30 | **个股分笔(最近交易日)** | ❌ | ✅ Tick | ✅ client.transaction() | QMT | TDX仅取最近交易日分笔，历史分笔需淘宝购买 |

### §4.2 数据源选择决策树

```
需要获取数据？
├── 是高频数据（Tick/分钟K线）？
│   ├── 最近交易日 → QMT（download_history_data + get_market_data_ex）
│   └── 历史高频 → 淘宝购买（QMT本地不保留历史高频）
├── 是估值数据（PE/PB/PS）？ → iFind THS_BasicData
├── 是宏观数据（CPI/M2/利率）？ → iFind EDB（需正式账号）
├── 是资金流向/概念板块？ → iFind i问财（THS_iwencai）
├── 是期权/可转债/ETF/期货？ → QMT（合约列表+K线）
├── 是除权因子/指数权重？ → QMT 独有
├── 是日/周/月K线？
│   ├── 需要长历史 → QMT download_history_data（359行验证）
│   └── 需要增量+换手率 → iFind THS_HistoryQuotes
├── 是财务数据？
│   ├── 需要结构化报表 → QMT get_financial_data（11张表）
│   └── 需要灵活查询 → iFind THS_DateSerial
└── 是新闻/研报？ → 无（试用账号不支持，需正式账号）
```

### §4.3 能力边界一句话总结

| 数据源 | 独有能力 | 受限能力 |
|--------|---------|---------|
| **iFind** | EDB宏观数据(77,909)、i问财、估值PE/PB/PS、概念板块 | 高频K线(试用-4309)、美股港股(-4210)、事件研报(-5100) |
| **miniQMT** | 3秒Tick(含五档)、除权因子、指数权重、期权/可转债/期货合约 | 历史高频(仅最近交易日)、行业分类(返回空)、L2数据(需权限) |
| **TDX/mootdx** | 通达信板块分类(880xxx体系)、本地通达信数据文件读取(.day/.lc1/.lc5) | 无板块分笔历史、无历史分笔(仅最近交易日)、无复权、无估值/EDB/新闻/研报 |
| **三者均无** | — | 美股/港股(试用)、新闻事件、研究报告(试用)、**板块分笔历史**(淘宝购买/手工导出) |

### §4.4 七源互补全景矩阵

> 7 个数据源 × 22 个数据品类的覆盖全景。✅=实测通过 ⏳=配额限制 ❌=不可用 ⚠️=部分覆盖 —=不适用

| 数据品类 | iFind试用 | QMT | Baostock | TickFlow | AKShare | 财经RSS | TDX/mootdx | 补充说明 |
|---------|:---------:|:---:|:--------:|:--------:|:-------:|:-------:|:----------:|---------|
| A股日/周/月K线 | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | |
| A股分钟K线 | ⚠️ | ✅ | ✅ | ❌ | — | — | ✅ | Baostock/TDX补历史 |
| A股估值PE/PB | ✅ | — | ⚠️ | — | — | — | — | |
| A股财务报表 | ✅ | ✅ | ✅ | — | — | — | ✅ | Baostock季频/TDX gpcw zip |
| A股资金流向 | ✅ | — | — | — | — | — | — | |
| 龙虎榜/大宗/融资 | ✅ | — | — | — | — | — | — | |
| EDB宏观(CPI/PMI) | ⏳ | — | — | — | ✅ | — | — | AKShare补盲区(须断VPN) |
| 3秒Tick | — | ✅ | — | — | — | — | — | QMT独有(含五档) |
| 个股分笔(最近日) | — | ✅ | — | — | — | — | ✅ | TDX client.transaction() |
| 个股分笔(历史) | — | — | — | — | — | — | — | 淘宝购买/手工导出 |
| 期权/可转债/期货 | — | ✅ | — | — | — | — | — | |
| 除权因子 | — | ✅ | — | — | — | — | — | |
| 指数成分股 | ✅ | — | ✅ | — | — | — | — | Baostock 50/300/500 |
| 交易日历 | — | ✅ | ✅ | — | — | — | — | Baostock |
| 美股日/周/月/季/年 | ❌ | — | — | ✅ | ❌ | ❌ | — | TickFlow 12/12通过 |
| 美股ETF | ❌ | — | — | ✅ | — | ❌ | — | TickFlow SPY/DIA/QQQ |
| 美股真实指数 | ❌ | — | — | ❌ | — | ❌ | — | 用ETF替代(SPY/DIA/QQQ) |
| 港股日K线 | ❌ | ✅ | — | ✅ | — | ❌ | — | TickFlow 00700.HK✅ |
| 财经新闻(国内) | ❌ | — | — | — | ✅ | — | — | AKShare东财个股新闻(须断VPN) |
| 财经新闻(国外) | ❌ | — | — | — | — | ✅ | — | RSS直连8源(Yahoo/Bloomberg/CNBC等) |
| 研报/一致预期 | ❌ | — | — | — | ✅ | — | — | AKShare补盲区(须断VPN) |
| **通达信板块分类** | — | — | — | — | — | — | ✅ | TDX独有(880xxx体系) |
| **板块分笔历史** | — | — | — | — | — | — | — | 无API(淘宝购买/手工导出,§8.6) |
| **本地TDX文件** | — | — | — | — | — | — | ✅ | TDX独有(.day/.lc1/.lc5,需装客户端) |

> **实测结论（2026-07-06，含 VPN 对比 + 新闻源扩展 + TDX板块分类）**：
> - iFind 试用账号 ❌ 盲区中，**EDB宏观 + 新闻 + 研报** 被 AKShare 覆盖（须断 VPN）
> - **A股K线+财务** 被 Baostock 覆盖（实测 10/10，最稳定，不受 VPN 影响）
> - **美股K线 + ETF** 被 TickFlow 覆盖（实测 12/12，不受 VPN 影响）—— 美股不再需要淘宝购买
> - **国外财经新闻** 被 RSS 直连覆盖（8/10通过，免费无Key，不受VPN影响）
> - **A股+美股+国内外新闻全品类数据 100% 可获取**（六源互补）
> - **TDX/mootdx** 补充通达信板块分类、本地文件读取、个股最近交易日分笔；**关键限制——无板块分笔历史**(无API,只能手工导出)
> - **运维建议**：下载免费源数据时**断开 VPN**（Baostock/TickFlow/财经RSS/TDX 不受影响，AKShare 必须断开）

---

## §5 数据获取策略（四步执行）

### §5.1 执行顺序总览

```
第一步：iFind 立即下载（试用账号能获取的）
   ↓
第二步：QMT 立即下载（客户端运行时能获取的）
   ↓
第三步：淘宝购买历史数据（QMT无法下载的长历史高频）
   ↓
第四步：iFind 正式账号（升级后解锁EDB/美股/研报）
```

### §5.2 第一步：iFind 试用账号立即下载

| 优先级 | 数据项 | 对应C1表/品类 | 操作 | API |
|--------|--------|--------------|------|-----|
| P0 | 估值数据补充（1800只缺失股票） | daily_valuation | 批量下载PE/PB/PS | THS_BasicData |
| P0 | 资金流向（i问财批量查询） | money_flow | 按日查询主力资金流向 | THS_iwencai |
| P0 | 日/周/月K线增量更新 | daily_kline 等 | 增量下载 | THS_HistoryQuotes |
| P1 | 指数成分股 | 新建表 | 下载沪深300/中证500等 | THS_DataPool |
| P1 | 行业分类 | 新建表 | 下载同花顺行业成分 | THS_DataPool + i问财 |

**执行模板**：
```python
from iFinDPy import *
from zephyr.shared.security.secrets import get_secret_or_default
THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))

# 批量估值数据（注意参数格式坑，见 §2.4.3）
stocks = ['600000.SH', '000001.SZ', ...]  # 1800只
for stock in stocks:
    data = THS_BasicData(stock, 'ths_pe_stock;ths_pb_stock;ths_ps_stock',
                         '2025-06-30,100;2025-06-30,100;2025-06-30,100')
    df = THS_Trans2DataFrame(data)
    # 写入 daily_valuation 表
```

### §5.3 第二步：QMT 立即下载

| 优先级 | 数据项 | 对应C1表 | 操作 | 验证状态 |
|--------|--------|---------|------|---------|
| P0 | 日K线增量（5207只A股） | daily_kline | download_history_data('1d') + get_market_data_ex | ✅ 已验证359行 |
| P0 | 1/5/15/30/60分钟K线（最近交易日） | kline_5min 等 | download_history_data('5m') 等 | ✅ 已验证48/241行 |
| P0 | Tick数据（最近交易日） | tick_data | download_history_data('tick') | ✅ 已验证4998行 |
| P0 | 除权除息因子（全市场） | divid_factors | get_divid_factors | ✅ 已验证26条 |
| P0 | 实时Tick快照 | tick_data | get_full_tick | ✅ 已验证 |
| P1 | ETF日K线（946个） | etf_kline | download_history_data | ✅ 已验证20行 |
| P1 | 可转债日K线（152个） | cb_kline | download_history_data | ✅ 已验证20行 |
| P1 | 期权合约+K线（662个） | option表 | download_history_data | ✅ 合约列表已验证 |
| P1 | 期货合约（中金所802个） | futures表 | download_history_data | ✅ 合约列表已验证 |
| P1 | 财务数据（11张报表） | financial表 | download_financial_data2 + get_financial_data | API已确认 |
| P2 | 指数权重 | index_weight | download_index_weight() + get_index_weight | API已确认 |
| P2 | Level-2数据 | l2表 | get_l2_order/quote/transaction | 需L2权限 |

**批量下载执行模板**：
```python
import sys, os
sys.path.append(r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages')
os.chdir(r'D:\国金证券QMT交易端\bin.x64')
from xtquant import xtdata

# 批量下载5207只A股日K线
stocks = xtdata.get_stock_list_in_sector('沪深A股')
for code in stocks:
    xtdata.download_history_data(code, '1d', '20240101', '20250630')
    # 返回None是正常的，数据已异步下载
# 批量获取
data = xtdata.get_market_data_ex([], stocks, '1d', '20240101', '20250630')
```

### §5.4 第三步：淘宝购买历史数据

> **原因**：QMT 只能下载最近交易日的高频数据，历史高频数据 QMT 本地不保留。

| 优先级 | 数据项 | 时间范围 | 说明 |
|--------|--------|---------|------|
| P0 | 5分钟K线历史 | 2000-2024 | QMT 只能下载最近交易日，历史走淘宝 |
| P0 | Tick数据历史 | 2000-2024 | 同上 |
| P1 | 集合竞价历史 | 2000-2024 | 同上 |

**购买后导入流程**：
1. 淘宝购买数据（CSV/HDF5格式）
2. 编写导入脚本，标准化字段对齐 C1 表 Schema
3. 通过 C1MarketWriter.upsert_* 批量写入 ClickHouse
4. 质量校验：DataQualityGate.check

### §5.5 第四步：iFind 升级正式账号

| 优先级 | 数据项 | 说明 | 解锁后能力 |
|--------|--------|------|-----------|
| P1 | EDB宏观数据 | 77,909个宏观/行业指标 | 5万条/周(试用=正式,每周一重置) |
| P1 | 美股/港股行情 | 海外市场数据 | 解除-4210权限拒绝 |
| P1 | 5分钟/分钟K线历史 | iFind历史高频 | 解除-4309一年限制 |
| P2 | 新闻/事件 | THS_iEvent | 解除-5100账号类型限制 |
| P2 | 研究报告 | THS_iResearch | 解除-5100账号类型限制 |
| P2 | CFFEX期货 | 中金所期货行情 | 解除-4216权限拒绝 |

> C1 行情仓库填充状态见 ClickHouse 实时扫描。

---

## §7 免费开源数据源（v1.1.0 新增）

### §7.1 概述与定位

本章节记录 iFind 试用账号盲区的**免费开源替代源**（免费无Key）+ **需免费注册API Key的源**。iFind 试用账号（IFIND_USERNAME）有 4 类数据不可用：美股(-4210)、港股(-4210)、新闻事件(-5100)、研究报告(-5100)，另有 EDB 宏观(-4318)5万条/周配额限制(每周一重置,试用版=正式版)。本章节的源完全覆盖这些盲区。

**核心定位**：
- 免费源是**补充**，不是替代。iFind/QMT 能获取的数据优先用 iFind/QMT（已付费、稳定、有 SLA）。
- 免费源覆盖 iFind 试用账号的 ❌ 盲区（A股K线历史/美股/国内外新闻/EDB宏观），使策略所需数据 100% 可获取。
- 优先免费无Key源（Baostock/TickFlow/AKShare/财经RSS），需Key源作为深度补充（历史新闻归档/情感分析/实时报价）。

> **免费源实测总览**：11源完整对比表+实测结论见 [§1.3 数据源总览](#13-免费开源源v130-实测验证vpn对比覆盖-ifind-试用盲区)。主力源：Baostock(A股) + TickFlow(美股) + 财经RSS(国外新闻) + AKShare(国内新闻/宏观)；需Key源：NewsAPI/AlphaVantage/Finnhub/Newsdata 新闻全部✅，Tiingo 日K线✅(News❌需付费)；yfinance/Stooq 已废弃（§7.4）。

#### §7.1.1 API Key 清单（需免费注册源，用户已注册，2026-07-03）

> **安全说明**：所有 API key/账号密码通过环境变量读取（见 `.env.example`），禁止在文档中记录明文。QMT/Baostock/TickFlow/AKShare/财经RSS 不需要账号密码。

| 数据源 | 环境变量 | 免费额度 | 实测状态 | 实测日期 |
|--------|---------|---------|:--------:|:--------:|
| **NewsAPI.org** | `NEWSAPI_KEY` | 100请求/天 | ✅ 2/2通过 | 2026-07-03 |
| **Tiingo** | `TIINGO_API_KEY` | 免费tier(日K线✅/News❌需付费) | ⚠️ 1/2通过 | 2026-07-03 |
| **Finnhub** | `FINNHUB_API_KEY` | 免费tier | ✅ 3/3通过 | 2026-07-03 |
| **Newsdata.io** | `NEWSDATA_API_KEY` | 200请求/天 | ✅ 2/2通过 | 2026-07-03 |
| **Alpha Vantage** | `ALPHAVANTAGE_API_KEY` | 5次/min | ✅ 2/2通过 | 2026-07-03 |
| iFind(试用) | `IFIND_USERNAME` / `IFIND_PASSWORD` | 试用账号(有限制) | ✅ 已验证 | 2026-07-03 |

> **Tiingo认证方式**：用Header `Authorization: Token <key>`，不是URL `apiKey=`参数。News API返回403"You do not have permission"（免费tier不含），日K线API `tiingo/daily/<symbol>/prices` 可用。
> **Alpha Vantage限流**：5次/min，请求间隔需≥12秒。
> **AskNews**：网站已挂售，跳过。

#### §7.1.2 国内财经新闻+公告+政策直连API清单（免费无Key，实测6/8通过，2026-07-03）

> **API 清单已结构化**：6 个国内直连 API（东财快讯/同花顺快讯/华尔街见闻/金十数据/财联社电报/巨潮公告）记录在 `depgraph.data_source_apis` 表（DS-NEWSAPI-API-003~008），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留分类摘要、参数坑与签名算法。
>
> 从 [china-finance-rss](https://github.com/yuxuan-made/china-finance-rss) 项目源码提取的正确 API URL。**须断开 VPN**（国内网站）。与 AKShare(§7.3) 互补——AKShare 覆盖个股新闻+研报，直连 API 覆盖 7x24 实时快讯+公告+政策。

**A. 财经新闻快讯（4/4 通过）** — 东财/同花顺/华尔街见闻/金十，均 `GET` 返回 JSON（东财为 jsonP 需正则提取），免费无 Key。

**B. 财联社电报（签名修复，✅可用）** — `GET https://www.cls.cn/v1/roll/get_roll_list`，签名修复后 10 条/次，字段最丰富（50+ 字段）。

> **财联社签名算法**（从 china-finance-rss 源码提取）：
> 1. 参数序列化：`key=value` 格式，按 key 大写排序拼接，嵌套用 `key[index]`/`key[subkey]`
> 2. 签名：`SHA1(serialized) → MD5(sha1_digest) → sign`
> 3. 参数：`{refresh_type:1, rn:50, last_time:0, os:web, sv:8.7.9, app:CailianpressWeb, sign:<签名>}`
> 4. Header：`Referer: https://www.cls.cn/telegraph`
>
> **财联社字段价值**（50+ 字段，最有价值的国内新闻源）：
> - `stock_list` — 关联股票代码（直接可用，不用 NLP 提取）
> - `subjects` — 主题分类
> - `tags` — 标签
> - `level` — 重要级别（C/B/A 级）
> - `reading_num` — 阅读数（热度指标）
> - `shareurl` — 分享链接

**C. 上市公司公告（巨潮资讯网，✅可用）** — `POST http://www.cninfo.com.cn/new/hisAnnouncement/query`，证监会指定信息披露平台。

> **巨潮资讯网**是证监会指定信息披露平台，有完整的上市公司公告历史（年报/季报/临时公告/董事会决议等）。
> - 参数: `stock=代码,orgId` / `column=sse(上交所)或szse(深交所)` / `pageSize` / `seDate=开始~结束`
> - 返回字段: secCode/secName/announcementTitle/announcementTime/adjunctUrl(PDF)/announcementType
> - **坑**：orgId 必须正确（如 `gssz0000001` 深交所/`gsshz0000001` 上交所），错则 NoneType 错误

**D. 中国政策/监管数据源（HTML 爬虫，未结构化入 DB）**

> 以下 4 源为 HTML 页面爬虫源（非结构化 API），保留为待开发清单。`ak.news_cctv` 已结构化入 `depgraph.data_source_apis`（DS-AKSHARE-API-017）。

| 数据源 | URL | 可访问 | 方式 | 可获取内容 |
|--------|-----|:------:|------|-----------|
| **证监会** | `http://www.csrc.gov.cn/csrc/c100028/index.shtml` | ✅ | HTML 爬虫(BeautifulSoup) | 要闻/政策解读/行政处罚/监管措施/行政复议/市场禁入/新闻发布会 |
| **中国政府网** | `https://www.gov.cn/zhengce/` | ✅ | HTML 爬虫 | 国务院政策文件/法规/规章 |
| **中国人民银行** | `http://www.pbc.gov.cn/zhengcehuobisi/125207/index.html` | ✅ | HTML 爬虫 | 货币政策/公开市场操作/利率公告 |
| **AKShare news_cctv** | `ak.news_cctv(date="20260702")` | ✅ 10 条 | AKShare | 央视新闻联播文字稿(政策风向标)，列=date/title/content |

> **政策数据获取方案**：
> - **实时政策快讯**：财联社电报(含 stock_list 关联股票) + AKShare `news_cctv`(央视新闻联播)
> - **政策原文归档**：证监会/中国政府网/央行 HTML 爬虫（页面已验证可访问，需开发 BeautifulSoup 解析器，**后续建表时做**）
> - **证监会可获取内容**：要闻/行政处罚决定书/监管措施(警示函等)/行政复议/市场禁入/新闻发布会文字稿

> **国内新闻+公告+政策主力方案**：东方财富快讯(50条) + 华尔街见闻(20条) + 同花顺快讯(20条) + 金十数据(21条) + **财联社电报(10条,字段最丰富)** + **巨潮资讯网(上市公司公告)** + AKShare 个股新闻/研报/央视新闻联播(§7.3) = **8 源覆盖国内财经快讯+上市公司公告+政策监管**。
> **金十数据特殊处理**：需先 `GET https://www.jin10.com/` 提取 JS bundle URL → `GET` bundle 提取 `x-app-id` → 用 `x-app-id` Header 调用 flash API。详见 §7.7.8。
> **华尔街见闻**：channel=global-channel 覆盖全球新闻(中英文)，是国外新闻的中文版补充源。
> **巨潮资讯网 orgId 坑**：必须用正确的 orgId（深交所 `gssz` 前缀/上交所 `gsshz` 前缀），错则 NoneType 错误。

#### §7.1.3 股权穿透 + 产业链地图数据源清单（实测，2026-07-03）

> 用户提问：①公司股权穿透/股东信息（董事长/股东股份/控股架构）能否获取？②产业链地图（每只股票在产业链中的位置/上下游关系/产业链涵盖公司清单）能否获取？本节为搜索+实测结论。

**A. 股权穿透/股东信息 — AKShare 免费接口实测（断VPN，2026-07-03）**

> **API 清单已结构化**：9 个 AKShare 股权穿透 API 记录在 `depgraph.data_source_apis` 表（DS-AKSHARE-API-018~026，含 2 个 deprecated 反爬失败），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留实测明细（字段规模属价值增量，不入 DB）。

| # | 接口 | 实测结果 | 数据规模 | 字段 |
|---|------|:--------:|---------|------|
| 1 | `ak.stock_gdfx_top_10_em(symbol="SH600000", date="20240930")` | ✅ | 10行/股 | 序号/股东名称/股东性质/持股数量/持股比例/股份状态/变动情况/质押股份 |
| 2 | `ak.stock_gdfx_free_top_10_em(symbol="SH600000", date="20240930")` | ✅ | 10行/股 | 十大流通股东（同上+股东类型+增减+变动比例） |
| 3 | `ak.stock_zh_a_gdhs_detail_em(symbol="600000")` | ✅ | 60行/股 | 股东户数本次/上次/增减/户均持股（历史明细） |
| 4 | `ak.stock_zh_a_gdhs()` | ✅ | 429358行 | 全市场股东户数（含区间涨跌幅） |
| 5 | `ak.stock_gpzy_pledge_ratio_em()` | ✅ | 2294行 | 质押机构/质押比例/质押股数/质押市值/警戒线/平仓线 |
| 6 | `ak.stock_ggcg_em(symbol="全部")` | ✅ | 145213行 | 高管增减持（全市场，含增持/减持/变动比例/变动后持股/变动开始日/变动截止日/公告日） |
| 7 | `ak.stock_zygc_em(symbol="SH600000")` | ✅ | 200行/股 | 主营构成/主营收入/收入比例/主营成本/成本比例/主营利润/利润比例/毛利率（按报告期+分类类型） |
| 8 | `ak.stock_individual_info_em(symbol="600000")` | ❌ | - | ConnectionError（东方财富反爬严重，3次重试全失败）— 原本可拿董事长/总经理/注册资本/上市日期 |
| 9 | `ak.stock_hold_control_cninfo(symbol="600000")` | ❌ | - | KeyError（接口存在但功能不稳定，3只股票全失败） |
| 10 | `ak.stock_gdfx_holding_change_em(date="20240930")` | ❌ | - | AKShare 内部 bug（Length mismatch: Expected 21 elements, got 20） |
| 11 | `ak.stock_zygk_em` | ❌ | - | 该函数不存在（被废弃/重命名，akshare 1.18.64 中无此 API） |

> **AKShare 股权穿透能拿到的（免费）**：十大股东 + 十大流通股东 + 股东户数（单股明细/全市场） + 股权质押（全市场） + 高管增减持（全市场） + 主营业务构成（按报告期+分类类型）
>
> **AKShare 拿不到的**：①董事长/总经理/法人代表/注册资本/上市日期（`stock_individual_info_em` 反爬，需 iFind 正式账号或巨潮公告 PDF 解析）；②实际控制人链（`stock_zygk_em` 不存在，需天眼查/iFind）；③控股关系穿透链（`stock_hold_control_cninfo` 失败，需天眼查/iFind/巨潮公告 PDF）；④多层股权穿透（子公司→母公司→实控人，AKShare 完全无此能力）。

**B. 股权穿透 — 其他数据源搜索结论**

| 数据源 | 能力 | 是否可用 | 说明 |
|--------|------|:--------:|------|
| **天眼查** | 完整股权穿透 API（get_shareholder_info / get_actual_controller / get_beneficial_owners / get_equity_tree / get_subsidiary_info） | ❌ 商业付费 | 需会员套餐，按调用次数/包年计费 |
| **同花顺 iFind** | 有完整产业图谱+股东信息+实控人 | ⚠️ 需正式账号 | 试用账号（IFIND_USERNAME）受限，需购买正式账号 |
| **Tushare** | stock_top10_holders / stock_hold_control | ⚠️ 需积分 | 免费2000积分不够，需5000分以上（充值或贡献获取） |
| **巨潮资讯网** | 上市公司公告 PDF（含实控人/控股关系/股东大会决议） | ✅ 已验证可用 | 需 BeautifulSoup + PDF 解析（PDF URL 在 adjunctUrl 字段） |
| **GitHub 开源** | 中文"股权穿透 股东 python" + 英文"company ownership equity python" | ❌ 0 结果 | 全球开源社区无股权穿透项目 |

> **股权穿透方案建议**：
> - **可立即落地**（免费）：AKShare 拿"十大股东+股权质押+高管增减持+主营业务构成+股东户数" → 入库 `c3_fundamental`
> - **需 PDF 解析**（免费但工作量大）：巨潮公告 PDF 中包含实控人/控股关系链 → 后续做 PDF 抽取（BeautifulSoup 解析 HTML + pdfplumber/PyPDF2 解析 PDF）
> - **需付费**：天眼查 API 或 iFind 正式账号才能拿到完整股权穿透图谱（多层穿透+实控人链）

**C. 产业链地图 — AKShare 实测（断VPN，2026-07-03）**

> **API 清单已结构化**：7 个 AKShare 产业链 API 记录在 `depgraph.data_source_apis` 表（DS-AKSHARE-API-028~034，含 4 个 deprecated 反爬/内部 bug），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留实测明细（字段规模属价值增量，不入 DB）。

| # | 接口 | 实测结果 | 数据规模 | 字段 |
|---|------|:--------:|---------|------|
| 1 | `ak.sw_index_first_info()` | ✅ | 31个 | 行业代码/行业名称/成份个数/静态市盈率/TTM市盈率/市净率/静态股息率（如：农林牧渔/基础化工/钢铁/银行/非银金融/有色金属） |
| 2 | `ak.sw_index_second_info()` | ✅ | 131个 | 同上 + **上级行业**字段（如：种植业→农林牧渔，渔业→农林牧渔，国有大行→银行） |
| 3 | `ak.sw_index_third_info()` | ✅ | 336个 | 同上 + 上级行业（如：种子→种植业→农林牧渔，粮食种植→种植业→农林牧渔） |
| 4 | `ak.sw_index_third_cons()` | ❌ | - | AKShare 内部 bug（Length mismatch: Expected 18 elements, got 17）— 三级行业成分股 |
| 5 | `ak.stock_board_industry_name_em()` | ❌ | - | ConnectionError（东方财富反爬严重） |
| 6 | `ak.stock_board_industry_cons_em(symbol="银行")` | ❌ | - | ConnectionError（东方财富反爬严重） |
| 7 | `ak.stock_board_concept_name_em()` | ❌ | - | ConnectionError（东方财富反爬严重） |
| 8 | `ak.stock_zygc_em(symbol="SH600000")` | ✅ | 200行/股 | 主营业务构成（按 报告日期/分类类型/主营构成 拆分）— 可作为产业链归类依据 |

> **产业链地图关键说明**：
> - **申万行业三级分类**（31一级 + 131二级 + 336三级）**只是行业归类**，不是产业链——它告诉你"浦发银行属于银行-国有大行-国有大型银行Ⅱ"，但不告诉你"浦发银行的上下游是谁、和哪些公司构成同一个产业链"。
> - **真正的产业链地图**需要节点（公司/产品）+ 边（上下游关系），如"光伏产业链"包含：硅料（通威/大全）→ 硅片（隆基/中环）→ 电池片（通威/爱旭）→ 组件（晶科/天合）→ 电站（林洋/太阳能）；这种关系数据**AKShare 完全无此能力**。
> - **AKShare 的 `stock_zygc_em` 主营业务构成**可以辅助产业链归类——根据主营业务文本（如"硅片制造"、"光伏组件"）将公司映射到产业链节点，但需要人工/NLP 维护产业链节点表+上下游关系表。

**D. 产业链地图 — 其他数据源搜索结论**

| 数据源 | 能力 | 是否可用 | 说明 |
|--------|------|:--------:|------|
| **同花顺 iFind 产业图谱** | 3D 动态产业链图，覆盖 200+ 产业链，节点+上下游关系 | ⚠️ 需正式账号 | 试用账号无权限，正式账号可调用 THS_iwencai 查询产业链 |
| **东方财富 Choice 产业链** | 大模型生成+研究所复核的产业链图谱，含节点+上下游+公司映射 | ❌ 商业产品 | 需付费订阅 Choice 终端 |
| **Wind 产业链图谱** | 类似 Choice，节点+上下游+公司映射 | ❌ 商业产品 | 需付费订阅 Wind 终端 |
| **中商产业研究院产业链图谱** | PDF/图片格式的产业链图谱 | ❌ 付费报告 | 单份报告几百元，无 API |
| **深交所产业链图谱课题标准** | 申万行业分类 + 8 种关联关系（上下游/同级/竞争/互补/派生/支撑/依托/协同） | ❌ 数据未公开 | 课题标准已发布但底层数据未对外 |
| **GitHub 开源** | 中文"产业链地图 python" + 英文"industry chain map python" | ❌ 0 结果 | 全球开源社区无产业链地图项目，仅找到不相关的市场报告 |

> **产业链地图核心结论**：**GitHub 和开源社区无产业链地图数据库**。目前业界产业链图谱都是**商业付费产品**（iFind/Choice/Wind/中商产业研究院）。

**E. 产业链地图自建方案（按可行性排序）**

| 方案 | 思路 | 工作量 | 数据来源 | 落地建议 |
|------|------|:------:|---------|---------|
| **方案A：申万三级骨架 + 主营业务填充** | 用申万 31→131→336 三级行业分类作为产业链骨架，每只股票按主营业务文本归类到三级行业节点 | 小 | AKShare（已验证可用） | ✅ 优先落地：申万行业入库 + stock_zygc_em 主营业务入库 |
| **方案B：主营业务关键词 + 上下游规则** | 解析每只股票主营业务构成（stock_zygc_em 200行/股）→ 提取业务关键词 → 按"原料→生产→销售"逻辑手工维护产业链上下游关系表 | 中 | AKShare + 人工梳理产业链节点 | ⏳ 第二阶段：先梳理 10-20 条核心产业链（光伏/新能源车/半导体/白酒/医药/CXO/猪肉/钢铁/煤炭/银行） |
| **方案C：购买商业数据** | 直接买 iFind 正式账号或 Choice 产业链图谱，导出产业链节点+上下游关系 | 最小 | 商业付费 | ⏳ 备选：如果方案B 工作量过大，再考虑付费 |
| **方案D：基于公开资料自建完整产业链** | 招股说明书+年报"经营情况"+券商研报"行业分析"中抽取产业链关系，需要 NLP 抽取 | 大 | 公开 PDF + NLP | ⏳ 长期：方案B 之上做 NLP 自动抽取 |

> **产业链地图建议**：先落地方案A（申万三级骨架入库 + stock_zygc_em 主营业务入库），形成"行业分类+主营业务"的基础数据。再按方案B手工梳理核心产业链（10-20条），形成产业链节点表+上下游关系表。如工作量过大，再考虑方案C购买商业数据。

### §7.2 Baostock 完整指南（实测 10/10 通过，最稳定）

#### 基本信息

| 属性 | 值 |
|------|-----|
| 官网 | `https://baostock.com` |
| 类型 | 免费开源证券数据平台（服务端推送，非爬虫） |
| 实测通过率 | **10/10 (100%)** — 2026-07-03 |
| 安装 | `pip install baostock` |
| 鉴权 | 无需注册、无需 API Key（匿名登录 `bs.login()`） |
| 返回格式 | pandas DataFrame |
| Python版本 | 3.6/3.9+ |
| 数据更新时间 | 日K 17:30 / 复权因子 18:00 / 分钟K 20:00 |

#### §7.2.1 数据覆盖范围

> **API 清单已结构化**：16 个 Baostock API（K线/季频财务/成分股/证券列表/行业分类/基本信息/分红等）记录在 `depgraph.data_source_apis` 表（DS-BAOSTOCK-API-001~016），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留分类摘要，调用示例见 §7.2.2。

**核心分类**：
- **K线** — `query_history_k_data_plus(frequency="d/w/m/5/15/30/60")`，日 K 从 1990-12-19 起，分钟 K 近 5 年（2020-01-03 起）
- **季频财务** — `query_profit_data()` 盈利能力 / `query_balance_data()` 资产负债 / `query_cash_flow_data()` 现金流 / `query_growth_data()` 成长能力 / `query_operation_data()` 营运能力 / `query_dupont_data()` 杜邦分析，均从 2007 年起
- **成分股** — `query_hs300_stocks()` 沪深300 / `query_sz50_stocks()` 上证50 / `query_zz500_stocks()` 中证500
- **基础数据** — `query_trade_dates()` 交易日历 / `query_all_stock()` 证券列表 / `query_stock_basic()` 股票基本信息 / `query_stock_industry()` 行业分类 / `query_dividend_data()` 分红（**滞后约1周+，见 §7.2.5，分红明细改用 AKShare**）

> ⚠️ **分红数据滞后**：`query_dividend_data(yearType="report")` 严重滞后，详见 §7.2.5；分红明细改用 AKShare `stock_history_dividend_detail`（§7.3.5）。

#### §7.2.2 API 调用示例（直接复制可用）

```python
import baostock as bs
import pandas as pd

# 1. 登录（匿名，无需注册）
lg = bs.login()
if lg.error_code != '0':
    raise Exception(f"登录失败: {lg.error_msg}")

# 2. 日K线（前复权）
rs = bs.query_history_k_data_plus(
    "sh.600000",  # 代码格式: sh.XXXXXX / sz.XXXXXX
    "date,code,open,high,low,close,volume,amount,pctChg,turn",
    start_date="2024-06-01", end_date="2025-01-01",
    frequency="d",     # d=日 w=周 m=月 5/15/30/60=分钟
    adjustflag="2"     # 1=后复权 2=前复权 3=不复权
)
# 3. ResultData 转 DataFrame
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)
# ✅ 返回 144行

# 4. 季频财务（盈利能力）
rs = bs.query_profit_data(code="sh.600000", year=2024, quarter=3)
df = rs.get_data()  # 也可用 get_data() 替代手动循环
# ✅ 返回 roeAvg/npMargin/gpMargin

# 5. 沪深300成分股
rs = bs.query_hs300_stocks()
df = rs.get_data()
# ✅ 返回 300行

# 6. 登出
bs.logout()
```

**代码格式坑**：Baostock 用 `sh.600000`/`sz.000001`（小写点号），不是 `600000.SH`。需做转换：`code = "sh." + stock_code[:6] if stock_code.endswith("SH") else "sz." + stock_code[:6]`

#### §7.2.3 Baostock 优势

- **服务端推送（非爬虫）**：比 AKShare 稳定，不受上游网站改版影响
- **数据规范**：字段命名统一，单位明确
- **K线含估值字段**：可返回 peTTM/pbMRQ/psTTM/isST（需在 fields 中指定）
- **完全免费**：零注册、零 API Key、零请求限制

#### §7.2.4 Baostock 限制

| 限制 | 说明 |
|------|------|
| 仅A股 | 不覆盖美股/港股/期货/期权 |
| 仅历史 | 无实时行情（日K 17:30后才更新当日数据） |
| 分钟线仅近5年 | 5/15/30/60分钟K线从2020-01-03起 |
| 代码格式特殊 | sh.XXXXXX/sz.XXXXXX（需转换） |
| 需login/logout | 每次使用需登录，用完登出 |
| **分红数据滞后** | `query_dividend_data(yearType="report")` 查 3000 symbol 全 0 新数据，落后 AKShare 约1周+ | 分红明细改用 AKShare `stock_history_dividend_detail`（见 §7.3.5） |

#### §7.2.5 分红数据滞后实测（v1.9.0，2026-07-05）

> baostock `query_dividend_data(year, yearType="report")` **数据严重滞后**——批量查询近期分红数据时大量返回 0 条新数据，且脚本会卡住。同期 AKShare `stock_history_dividend_detail` 能拿到最新分红公告。

| 数据源 | 接口 | 结论 |
|--------|------|------|
| baostock | `query_dividend_data(yearType="report")` | ❌ 滞后约1周+，且 query 返回空 |
| AKShare | `stock_history_dividend_detail(indicator="分红")` | ✅ 实时 |

> **结论**：分红明细数据**不要使用 baostock**，改用 [AKShare stock_history_dividend_detail](#735-stock_history_dividend_detail-最可靠的分红数据源v190-新增实测)（见 §7.3.5）。baostock 的 K线/季频财务/成分股接口依然稳定可用，仅分红接口存在滞后。

### §7.3 AKShare 完整指南

#### 基本信息

| 属性 | 值 |
|------|-----|
| GitHub | `akfamily/akshare` |
| Stars | 19,750+（2026-07-03） |
| 活跃度 | 2026-07-02 最近更新（持续维护） |
| 许可证 | MIT |
| 安装 | `pip install akshare --upgrade` |
| 数据源 | 国家统计局/央行/东方财富/新浪/同花顺/巨潮/雪球/天天基金等公开渠道 |
| 返回格式 | pandas DataFrame |
| 鉴权 | 无需注册、无需 API Key |
| Python版本 | 3.8+ |

> ⚠️ **VPN影响警告（2026-07-03 VPN对比实测）**：AKShare是爬虫库，底层爬的是**国内网站**（东方财富/金十数据/商务部/国家统计局等）。挂VPN后IP变为海外，**国内网站拒绝海外IP连接**，导致：
> - 不挂VPN：宏观9/10通过 ✅
> - 挂VPN：宏观仅2/10通过 ❌（GDP/CPI✅，PPI/PMI/M2/LPR/社融/US_CPI/US_UNEMP全部 `ConnectionResetError`/`Max retries exceeded`）
> - **结论：使用AKShare时必须断开VPN**。VPN对AKShare有害无益。

#### §7.3.1 宏观经济数据（替代 iFind EDB，实测 9/10 通过）

**iFind EDB 盲区**：试用账号 -4318 "exceeded this week"（周配额超限，每周一重置,试用版=正式版均5万条/周），且 EDB 的 77,909 指标中策略常用的核心宏观指标在 AKShare 中都有对应。

> **API 清单已结构化**：10 个 AKShare 宏观 API（7 中国宏观 + 3 美国宏观）记录在 `depgraph.data_source_apis` 表（DS-AKSHARE-API-001~010），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留 iFind EDB 覆盖对照矩阵（覆盖度分析属价值增量，不入 DB）。

**核心 API 分类**：
- **中国宏观** — `macro_china_gdp`(GDP) / `macro_china_cpi`(CPI) / `macro_china_ppi_yearly`(PPI) / `macro_china_pmi`(PMI) / `macro_china_money_supply`(M0/M1/M2) / `macro_china_lpr`(LPR) / `macro_china_shrzgm`(社融增量)
- **美国宏观** — `macro_usa_cpi_monthly`(CPI) / `macro_usa_unemployment_rate`(失业率) / `macro_usa_fed_interest_rate`(联邦基金利率)
- **其他宏观模块** — `macro_euro_*` 欧洲宏观 / `macro_japan_*` 日本宏观（完整列表见 [AKShare 官方文档](https://akshare.akfamily.xyz/data/economy/economy.html)）

> 所有宏观 API 调用约定：无参数 → 返回 pandas DataFrame → 直接 `to_csv` 或写入 ClickHouse。**必须断开 VPN**（见上方 VPN 警告）。调用示例见 §7.7.2。

**覆盖范围对照**：

| iFind EDB 类别 | 指标数 | AKShare 对应 | 覆盖度 |
|---------------|:------:|-------------|:------:|
| 中国宏观 | 11,762 | `macro_china_*` 系列 | ✅ 核心指标全覆盖(GDP/CPI/PPI/PMI/M2/LPR/社融) |
| 全球宏观 | 12,385 | `macro_usa_*`/`macro_euro_*`/`macro_japan_*` | ✅ 主要经济体核心指标 |
| 利率 | 1,646 | `macro_china_lpr` + `rate_interbank` | ✅ LPR/Shibor/银行间 |
| 经济景气 | 991 | `macro_china_pmi` 分项 | ✅ PMI分项 |
| 行业经济 | 24,522 | `ak.macro_china_*` 行业分项 | ⚠️ 部分覆盖(钢材/汽车/发电量等) |
| 世界经济 | 3,573 | 部分通过 `macro_global_*` | ⚠️ 部分覆盖 |
| 区域宏观 | 23,030 | 各省市统计局接口 | ⚠️ 部分覆盖 |

> **结论**：策略所需的核心宏观因子（CPI/PPI/PMI/M0/M1/M2/GDP/社融/LPR/利率/汇率）在 AKShare 中**全部覆盖**，可完全替代 iFind EDB 的策略常用部分。iFind EDB 的优势在于细分行業/区域指标（77,909 全量），但策略层面用不到这么细。

#### §7.3.2 财经新闻与研报（替代 iFind iEvent/iResearch，实测 3/5 通过）

**iFind 盲区**：试用账号 -5100 "account type is not supported"（事件/研报不支持）。

> **API 清单已结构化**：6 个 AKShare 新闻/研报 API 记录在 `depgraph.data_source_apis` 表（DS-AKSHARE-API-011~016），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留 iFind 覆盖对照矩阵（替代关系分析属价值增量，不入 DB）。

**核心 API 分类**：
- **个股新闻** — `stock_news_em(symbol="600000")`（东方财富个股新闻）
- **财经快讯** — `stock_info_global_cls()`（财联社全球快讯，实时滚动）/ `stock_info_global_em()`（东方财富全球资讯）
- **研报** — `stock_research_report_em(symbol="600000")`（东方财富个股研报）/ `stock_profit_forecast_ths(symbol="600000")`（同花顺一致预期 EPS，替代 iFind 分析师预期）
- **事件日历** — `news_eco_calendar()`（财经事件日历：经济数据发布/央行决议等）
- **三大报表（备用）** — `stock_financial_report_sina(stock="600000", symbol="资产负债表")`，iFind/QMT 已能获取，仅作备用

> 所有 API 返回 pandas DataFrame。调用示例见 §7.7.2。

**覆盖对照**：

| iFind 接口 | 试用状态 | AKShare 替代 | 覆盖度 |
|-----------|:--------:|-------------|:------:|
| THS_iEvent（事件） | ❌ -5100 | `stock_news_em` + `stock_info_global_cls` | ✅ 个股新闻+财联社快讯 |
| THS_iResearch（研报） | ❌ -5100 | `stock_research_report_em` + `stock_profit_forecast_ths` | ✅ 研报+一致预期EPS |

#### §7.3.3 美股数据（❌ 实测失败，Connection aborted）

```python
import akshare as ak
# 美股历史K线（备用，TickFlow为主力）
df = ak.stock_us_hist(symbol="AAPL", period="daily", start_date="20200101", end_date="20251231")
```

#### §7.3.4 AKShare 限制与坑

| 限制 | 说明 | 缓解 |
|------|------|------|
| 爬虫聚合 | 上游网站改版会断接口 | 日K线/宏观等核心接口稳定（来自官方统计局/央行），小众接口可能断 |
| 无 PIT 保证 | 历史数据可能被上游追溯调整（财报修正） | 严肃回测需自己存档快照，不能依赖实时拉取 |
| 复权偶发错位 | 边角 case 复权 bug | 与 iFind/QMT 交叉验证 |
| 上游限速 | 东方财富/新浪对高频访问会临时封 IP | 控制请求频率（<1次/秒），加 sleep |
| 字段名不统一 | 同一字段在不同接口有不同命名 | 查阅 AKShare 文档确认字段名 |
| **东财实时快照反爬** | `stock_zh_a_spot_em()` 被 RemoteDisconnected 阻断（东财反爬升级） | 实时行情改用 QMT（见 §3）或 iFind THS_RQ（见 §2.4.6） |

#### §7.3.5 stock_history_dividend_detail — 最可靠的分红数据源（v1.9.0 新增实测）

> **API 清单已结构化**：`stock_history_dividend_detail` 已记录在 `depgraph.data_source_apis` 表（DS-AKSHARE-API-027），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留参数坑（列名前导空格）、字段映射表和批量补齐脚本（实测过程属价值增量，不入 DB）。

> AKShare `stock_history_dividend_detail` 是分红明细数据的**最优数据源**——比 baostock（滞后约1周+，见 §7.2.5）、iFind THS_BD 分红指标（-209 全部失败，见 §2.4.6）、iFind 问财（不适合个股明细查询，见 §2.4.6）都可靠。

**API 调用方法**：

```python
import akshare as ak

# 查询单个 symbol 的分红明细
df = ak.stock_history_dividend_detail(symbol="600036", indicator="分红")
# ✅ 返回 DataFrame，字段：公告日期/送股/转增/派息/进度/除权除息日/股权登记日/红股上市日
# 注意：列名有前导空格，需 df.columns = [c.strip() for c in df.columns]
```

**字段映射**（→ c3_fundamental.rights_issue 表）：

| AKShare 字段 | 表字段 | 说明 |
|------------|--------|------|
| 公告日期 | announce_date | YYYY-MM-DD |
| 送股 | bonus_shares | 每股送股数 |
| 转增 | capitalized_shares | 每股转增股本 |
| 派息 | dividend_pre_tax | 每股税前派息(元) |
| 进度 | status | 实施/预案/批准 |
| 除权除息日 | ex_date | YYYY-MM-DD |
| 股权登记日 | record_date | YYYY-MM-DD |
| 红股上市日 | listing_date | YYYY-MM-DD |

**多线程批量补齐示例**：

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_dividend_for_symbol(symbol: str, last_date: str) -> list:
    import akshare as ak
    result = []
    try:
        df = ak.stock_history_dividend_detail(symbol=symbol, indicator="分红")
        if df is None or df.empty:
            return []
        df.columns = [c.strip() for c in df.columns]  # 列名有前导空格
        for _, row in df.iterrows():
            announce_date = str(row.get('公告日期', '')).strip()[:10]
            if not announce_date or announce_date <= last_date:
                continue
            if announce_date in ('NaT', 'None', 'nan', ''):
                continue
            result.append({
                'symbol': symbol,
                'announce_date': announce_date,
                'bonus_shares': float(row.get('送股', 0) or 0) or None,
                'capitalized_shares': float(row.get('转增', 0) or 0) or None,
                'dividend_pre_tax': float(row.get('派息', 0) or 0) or None,
                'status': str(row.get('进度', '')).strip(),
                'ex_date': str(row.get('除权除息日', '')).strip()[:10] or None,
                'record_date': str(row.get('股权登记日', '')).strip()[:10] or None,
                'listing_date': str(row.get('红股上市日', '')).strip()[:10] or None,
            })
    except Exception as e:
        pass  # 个别 symbol 失败不影响整体
    return result

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(fetch_dividend_for_symbol, sym, LAST_DATE): sym
               for sym in symbols}
    for future in as_completed(futures):
        result = future.result()
        # ... 构建 TSV 写入 ClickHouse (data_source='akshare')
```

> - data_source 字段值：`akshare`

> **分红明细数据源优先级**：
> 1. ✅ **AKShare `stock_history_dividend_detail`**（最可靠，实时）
> 2. ❌ baostock `query_dividend_data`（滞后约1周+，见 §7.2.5）
> 3. ❌ iFind THS_BD 分红指标（-209 全部失败，见 §2.4.6）
> 4. ❌ iFind 问财 THS_WC（不适合个股明细查询，见 §2.4.6）

### §7.4 已废弃数据源（yfinance + Stooq，实测0%通过，VPN无效）

| 源 | 废弃原因 | 替代方案 |
|----|---------|---------|
| yfinance | Yahoo对yfinance库级全局限流(非IP限流),VPN无效 | TickFlow(美股K线/ETF) |
| Stooq | JS浏览器验证阻断,pandas_datareader已移除 | TickFlow(美股K线/ETF) |

### §7.5 TickFlow 完整指南（✅ 实测 12/12 通过——美股K线主力免费源，2026-07-03新发现）

#### 基本信息

| 属性 | 值 |
|------|-----|
| 官网 | `https://tickflow.org` |
| 文档 | `https://docs.tickflow.org` |
| 类型 | 免费API服务（服务端推送，非爬虫） |
| 实测通过率 | **12/12 (100%)** |
| VPN影响 | 无影响（服务端API，不受IP限制） |
| 安装 | `pip install "tickflow[all]" --upgrade`（v0.1.24） |
| 鉴权 | **免费服务无需注册、无需API Key**（`TickFlow.free()`） |
| Python版本 | 3.9+ |
| 频率限制 | **60次/分钟**（免费服务速率限制，超限提示等待重试） |
| 数据更新 | 日K线为历史数据，盘中不实时更新 |

#### §7.5.1 数据覆盖范围（实测验证）

> **API 清单已结构化**：TickFlow 核心 API（`tf.klines.get`）记录在 `depgraph.data_source_apis` 表（DS-TICKFLOW-API-001），详见 [asset_catalog.md](../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。本节保留实测覆盖矩阵（symbol/period 支持情况属价值增量，不入 DB）。

| # | 数据类型 | 代码格式 | 实测样本 | 实测结果 |
|---|---------|---------|---------|---------|
| 1 | A股日K线 | `600000.SH`/`000001.SZ` | 600000.SH 5行 | ✅ 通过 |
| 2 | 美股日K线 | `AAPL.US` | AAPL.US 5行 | ✅ 通过 |
| 3 | 美股多只 | `XXXX.US` | AAPL/MSFT/TSLA/NVDA/GOOG/AMZN/META/NFLX 8只 | ✅ 全部通过 |
| 4 | 美股ETF | `SPY.US`/`DIA.US` | SPY.US/DIA.US | ✅ 通过 |
| 5 | 港股日K线 | `00700.HK` | 00700.HK 5行 | ✅ 通过 |
| 6 | 周K线 | period=`1w` | AAPL.US 5行 | ✅ 通过 |
| 7 | 月K线 | period=`1M` | AAPL.US 5行 | ✅ 通过 |
| 8 | 季K线 | period=`1Q` | AAPL.US 5行 | ✅ 通过 |
| 9 | 年K线 | period=`1Y` | AAPL.US 5行 | ✅ 通过 |
| 10 | 历史深度 | count=100 | AAPL.US 100行 | ✅ 5个月历史 |
| 11 | 标的信息 | `tf.instruments.batch` | 600000.SH | ✅ 含上市日期/总股本/涨跌停价 |
| 12 | A股代码格式 | `XXXXXX.SH/SZ` | 600000.SH/000001.SZ | ✅ 正确格式（sh.600000不可用） |

> ❌ **TickFlow免费服务不提供**：实时行情、分钟级K线（1m/5m/15m/30m/60m）、美股真实指数（DJI/IXIC/GSPC，可用ETF替代：SPY/DIA/QQQ）
> ⚠️ **频率限制**：60次/分钟，批量下载需 `time.sleep(1)` 控制频率

#### §7.5.2 API调用示例（直接复制可用）

```python
from tickflow import TickFlow
import time

# === 初始化免费服务（无需注册无需Key）===
tf = TickFlow.free()

# === A股日K线 ===
df = tf.klines.get("600000.SH", period="1d", count=100, as_dataframe=True)
# ✅ 返回100行，列=['symbol','name','timestamp','trade_date','trade_time','open','high','low','close','volume','amount']

# === 美股日K线（代码格式: XXXX.US）===
df = tf.klines.get("AAPL.US", period="1d", count=100, as_dataframe=True)
# ✅ 返回100行

# === 美股多只批量下载（注意60次/min限制）===
us_stocks = ["AAPL.US", "MSFT.US", "TSLA.US", "NVDA.US", "GOOG.US", "AMZN.US", "META.US", "NFLX.US"]
for code in us_stocks:
    df = tf.klines.get(code, period="1d", count=500, as_dataframe=True)
    print(f"{code}: {len(df)}行")
    time.sleep(1)  # 避免60次/min限流

# === 周/月/季/年K线 ===
df_week  = tf.klines.get("AAPL.US", period="1w", count=52,  as_dataframe=True)  # 周K线
df_month = tf.klines.get("AAPL.US", period="1M", count=12,  as_dataframe=True)  # 月K线
df_quart = tf.klines.get("AAPL.US", period="1Q", count=4,   as_dataframe=True)  # 季K线
df_year  = tf.klines.get("AAPL.US", period="1Y", count=10,  as_dataframe=True)  # 年K线

# === 港股日K线（代码格式: 00XXXX.HK）===
df = tf.klines.get("00700.HK", period="1d", count=100, as_dataframe=True)
# ✅ 腾讯控股

# === 美股ETF（替代指数）===
df = tf.klines.get("SPY.US", period="1d", count=100, as_dataframe=True)  # 标普500ETF
df = tf.klines.get("DIA.US", period="1d", count=100, as_dataframe=True)  # 道琼斯ETF
df = tf.klines.get("QQQ.US", period="1d", count=100, as_dataframe=True)  # 纳斯达克100ETF

# === 标的信息查询 ===
info = tf.instruments.batch(symbols=["600000.SH", "AAPL.US"])
# 返回: [{'symbol','exchange','code','name','region','type','ext':{上市日期/总股本/涨跌停价...}}]
```

#### §7.5.3 TickFlow 优势

1. **完全免费无需注册**——`TickFlow.free()` 直接使用，无API Key
2. **美股日K线可用**——填补yfinance/Stooq/AKShare美股全部失败的空白
3. **统一API**——A股/美股/港股用同一套API，代码格式统一（`XXXXXX.SH`/`XXXX.US`/`00XXXX.HK`）
4. **多周期K线**——日/周/月/季/年K线全部支持
5. **不受VPN影响**——服务端API，挂不挂VPN都能用
6. **标的信息查询**——含上市日期/总股本/涨跌停价

#### §7.5.4 TickFlow 限制

| 限制 | 说明 | 缓解 |
|------|------|------|
| 60次/min限流 | 免费服务速率限制，超限提示等待 | `time.sleep(1)` 控制频率，批量下载分批 |
| 无实时行情 | 免费服务不提供盘中实时数据 | 实盘用QMT；TickFlow仅用于历史数据下载 |
| 无分钟K线 | 1m/5m/15m/30m/60m不可用 | 分钟K线用Baostock(A股)/QMT(美股) |
| 无真实指数 | DJI/IXIC/GSPC不可用 | 用ETF替代：SPY.US/DIA.US/QQQ.US |
| 历史深度未知 | count=100成功，count=500被限流(非深度限制) | 分批下载，等限流后重试 |
| 无复权数据 | 免费服务仅提供原始价格 | 与Baostock/QMT交叉验证复权 |

### §7.6 风险与限制（必读）

#### §7.6.1 免费源共性风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **无 SLA** | 免费源无服务保证，可能随时失效 | 多源备份：TickFlow(美股主力)↔Baostock(A股)↔AKShare(宏观) |
| **无 PIT 保证**(AKShare) | 历史数据可能被上游追溯调整 | 下载后立即存档快照（写入 ClickHouse 后不再更新历史） |
| **爬虫失效**(AKShare) | 上游网站改版会断接口 | 核心接口（宏观/日K线）来自官方统计局/央行，稳定；小众接口可能断 |
| **请求限流** | 高频访问会被封/限速 | Baostock/AKShare 控制频率<1次/秒；TickFlow 60次/min |
| **数据质量** | 复权/分红调整偶发错误 | 与 iFind/QMT 交叉验证关键数据 |
| **VPN有害**(AKShare) | 爬国内网站挂VPN后国内拒绝海外IP | **下载免费源数据时断开VPN**（Baostock/TickFlow不受影响） |

#### §7.6.2 免费源 vs 付费源决策矩阵

| 数据需求 | iFind/QMT(付费) | 免费源 | 推荐选择 |
|---------|:---------------:|:------:|---------|
| A股日K线 | ✅ 已付费 | ✅ Baostock | **iFind/QMT**（已付费，稳定） |
| A股估值PE/PB | ✅ 已付费 | ⚠️ AKShare(部分) | **iFind**（精确到个股） |
| A股财务报表 | ✅ 已付费 | ✅ Baostock | **iFind/QMT**（已付费） |
| EDB宏观CPI/PMI/M2 | ⏳ 5万条/周 | ✅ AKShare | **AKShare**（免费无限制） |
| 美股日K线 | ❌ 试用不支持 | ✅ TickFlow | **TickFlow**（免费无Key，12/12通过） |
| 美股指数 | ❌ 试用不支持 | ✅ TickFlow(ETF替代) | **TickFlow**（SPY/DIA/QQQ 替代真实指数） |
| 财经新闻 | ❌ 试用不支持 | ✅ AKShare | **AKShare**（免费，须断开VPN） |
| 研报/一致预期 | ❌ 试用不支持 | ✅ AKShare | **AKShare**（免费，须断开VPN） |
| 3秒Tick/期权/可转债 | ✅ QMT独有 | ❌ 无免费源 | **QMT**（独有） |

> **决策原则**：iFind/QMT 能获取的优先用 iFind/QMT（已付费、稳定、有 SLA）；免费源仅用于 iFind 试用账号的 ❌ 盲区。

### §7.7 免费源 API 调用完整示例

> 七源互补关系见 [§1.3 数据源总览](#13-免费开源源v130-实测验证vpn对比覆盖-ifind-试用盲区) + [§4.1 能力对比总表](#41-能力对比总表)。

#### §7.7.1 环境配置

```powershell
# 一次性安装所有免费源库（须用 Python 3.11）
pip install akshare --upgrade
pip install baostock --upgrade
pip install "tickflow[all]" --upgrade
```

#### §7.7.2 EDB 宏观数据下载（替代 iFind THS_EDBQuery，须断开VPN）

```python
import akshare as ak
import pandas as pd
from datetime import datetime

# 下载中国核心宏观指标
indicators = {
    'GDP':   ak.macro_china_gdp(),
    'CPI':   ak.macro_china_cpi(),
    'PPI':   ak.macro_china_ppi_yearly(),
    'PMI':   ak.macro_china_pmi(),
    'M2':    ak.macro_china_money_supply(),
    'LPR':   ak.macro_china_lpr(),
    '社融':  ak.macro_china_shrzgm(),
}

# 下载美国核心宏观指标
us_indicators = {
    'US_CPI':    ak.macro_usa_cpi_monthly(),
    'US_UNEMP':  ak.macro_usa_unemployment_rate(),
    'US_FED':    ak.macro_usa_fed_interest_rate(),
}

# 合并并写入 ClickHouse（示例）
for name, df in {**indicators, **us_indicators}.items():
    df['indicator'] = name
    df['fetch_time'] = datetime.now()
    print(f"✅ {name}: {len(df)}行")
    # df.to_clickhouse(...)  # 实际写入时用 DatabaseService
```

#### §7.7.3 国外财经新闻下载（RSS直连，免费无Key，不受VPN影响）

> 美股下载示例见 [§7.5.2 TickFlow API调用示例](#752-api调用示例直接复制可用)；国内财经新闻+研报见 [§7.3.2 财经新闻与研报](#732-财经新闻与研报替代-ifind-ieventiresearch实测-35-通过)。

```python
# 国外财经新闻主力源 = RSS直连（feedparser，免费无Key，实测8/10通过）
# 国内财经新闻 = AKShare stock_news_em（见 §7.3.2，须断开VPN）
import feedparser
import pandas as pd
import time

# 实测可用的8个国外财经RSS源（2026-07-03验证）
rss_sources = {
    "Yahoo Finance":  "https://finance.yahoo.com/news/rssindex",
    "SeekingAlpha":   "https://seekingalpha.com/market_currents.xml",
    "MarketWatch":    "https://feeds.content.dowjones.io/public/rss/mw_topstories",
    "Bloomberg":      "https://feeds.bloomberg.com/markets/news.rss",
    "FT":             "https://www.ft.com/rss/home",
    "Investing.com":  "https://www.investing.com/rss/news_1.rss",
    "Forbes":         "https://www.forbes.com/business/feed/",
    "CNBC TopNews":   "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "CNBC World":     "https://www.cnbc.com/id/100727362/device/rss/rss.html",
}

all_news = []
for source, url in rss_sources.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        all_news.append({
            "source": source,
            "title": entry.get("title", ""),
            "summary": entry.get("summary", "")[:200],
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    print(f"✅ {source}: {len(feed.entries)}条")
    time.sleep(0.5)

df = pd.DataFrame(all_news)
df.to_csv("D:/A股数据/rss/global_financial_news.csv", index=False)
print(f"\n总计: {len(df)}条新闻 from {len(rss_sources)}个源")
```

> **RSS直连优势**：免费无Key、不受VPN影响、覆盖8个权威财经媒体、实时更新。
> **RSS直连限制**：仅最新新闻（无历史归档）、无情感分析（需自行NLP处理）、部分源偶发SSL错误需重试。
> **备用方案**：需历史新闻归档时用 NewsAPI.org（16822条）或 Alpha Vantage NEWS_SENTIMENT（含情感分析），需免费Key，见 §7.1.1。

#### §7.7.4 需Key新闻/行情源API调用（用户已注册，实测验证）

```python
# 需Key源API调用示例（Key从环境变量读取，见 §7.1.1）
import requests
import time
from zephyr.shared.security.secrets import get_secret_or_default

# 1. NewsAPI.org — 全球新闻(16822条), 100请求/天
NEWSAPI_KEY = get_secret_or_default("NEWSAPI_KEY")
url = f"https://newsapi.org/v2/everything?q=stock market&apiKey={NEWSAPI_KEY}&pageSize=100&language=en"
r = requests.get(url, timeout=15)
articles = r.json().get("articles", [])
print(f"NewsAPI: {len(articles)}条 | 样本={articles[0]['title'][:80]}")

time.sleep(1)

# 2. Alpha Vantage — 新闻+情感分析(50条)+日K线, 5次/min
ALPHAVANT_KEY = get_secret_or_default("ALPHAVANTAGE_API_KEY")
url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey={ALPHAVANT_KEY}&limit=50"
r = requests.get(url, timeout=15)
feed = r.json().get("feed", [])
# feed中每条含: title/url/source/overall_sentiment_score/overall_sentiment_label
print(f"AlphaVantage News: {len(feed)}条 | 情感={feed[0].get('overall_sentiment_label')}")

time.sleep(13)  # 5次/min = 12秒间隔

# 3. Finnhub — 市场新闻(100条)+实时报价, 免费tier
FINNHUB_KEY = get_secret_or_default("FINNHUB_API_KEY")
url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
r = requests.get(url, timeout=15)
news = r.json()
print(f"Finnhub News: {len(news)}条 | 样本={news[0].get('headline','')[:80]}")

time.sleep(1)

# 4. Finnhub — AAPL实时报价
url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={FINNHUB_KEY}"
r = requests.get(url, timeout=15)
quote = r.json()
print(f"AAPL报价: current={quote.get('c')} high={quote.get('h')} low={quote.get('l')}")

time.sleep(1)

# 5. Newsdata.io — 财经新闻, 200请求/天
NEWSDATA_KEY = get_secret_or_default("NEWSDATA_API_KEY")
url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&category=business&language=en&size=50"
r = requests.get(url, timeout=15)
articles = r.json().get("results", [])
print(f"Newsdata: {len(articles)}条")

time.sleep(1)

# 6. Tiingo — 日K线(TickFlow backup), Header认证
TIINGO_KEY = get_secret_or_default("TIINGO_API_KEY")
url = "https://api.tiingo.com/tiingo/daily/AAPL/prices?startDate=2025-06-01&endDate=2025-07-01"
headers = {"Authorization": f"Token {TIINGO_KEY}"}
r = requests.get(url, headers=headers, timeout=15)
data = r.json()
# 每行含: date/open/high/low/close/volume/adjClose/adjHigh/adjLow/adjOpen/adjVolume
print(f"Tiingo AAPL日K线: {len(data)}行 | close={data[-1].get('close')}")
# 注意: Tiingo News API返回403(免费tier不含), 仅日K线可用
```

> **需Key源定位**：
> - **NewsAPI.org**：全球新闻覆盖最广（16822条），适合宏观舆情监控
> - **Alpha Vantage**：唯一含**情感分析**的源（overall_sentiment_score/label），适合量化情绪因子
> - **Finnhub**：公司级新闻+实时报价，适合个股事件驱动
> - **Newsdata.io**：财经新闻补充（200请求/天额度较高）
> - **Tiingo**：日K线作为TickFlow backup（News API需付费不可用）

#### §7.7.5 国内财经新闻下载（直连API，免费无Key，须断开VPN）

> 国内新闻直连API清单（东财/同花顺/华尔街见闻/金十/财联社/巨潮）详见 [§7.1.2](#712-国内财经新闻公告政策直连api清单免费无key实测68通过2026-07-03)。本节提供完整调用示例。

```python
# 国内财经新闻主力 = 直连API(7x24快讯) + AKShare(个股新闻/研报, 见 §7.3.2)
# 直连API 4源: 东方财富/同花顺/华尔街见闻/金十数据
import requests
import re
import json
import time

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json, */*",
           "Accept-Language": "zh-CN,zh;q=0.9", "Referer": ""}

# 1. 东方财富快讯 (50条, jsonP格式)
url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html"
r = requests.get(url, headers={**HEADERS, "Referer": "https://kuaixun.eastmoney.com/"}, timeout=10)
match = re.search(r'var\s+ajaxResult\s*=\s*(\{.*\})', r.text, re.DOTALL)
em_news = json.loads(match.group(1)) if match else {}
print(f"东财快讯: {len(em_news.get('LivesList', []))}条")

time.sleep(1)

# 2. 同花顺快讯 (20条, JSON)
url = "https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=&track=website&pagesize=50"
r = requests.get(url, headers={**HEADERS, "Referer": "https://news.10jqka.com.cn/"}, timeout=10)
ths_news = r.json().get("data", {}).get("list", [])
print(f"同花顺快讯: {len(ths_news)}条 | 样本={ths_news[0].get('title','')[:60]}")

time.sleep(1)

# 3. 华尔街见闻 (20条, JSON, 全球新闻中英文)
url = "https://api-one-wscn.awtmt.com/apiv1/content/lives?channel=global-channel&client=pc&limit=50"
r = requests.get(url, headers={**HEADERS, "Referer": "https://wallstreetcn.com/live"}, timeout=10)
wscn_news = r.json().get("data", {}).get("items", [])
print(f"华尔街见闻: {len(wscn_news)}条 | 样本={wscn_news[0].get('title','')[:60]}")

time.sleep(1)

# 4. 金十数据 (21条, 需提取x-app-id)
r = requests.get("https://www.jin10.com/", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
script_match = re.search(r'(?:https:)?//www\.jin10\.com/new/js/index\.[^"\'\ ]+\.js', r.text)
script_url = script_match.group(0)
if script_url.startswith("//"): script_url = "https:" + script_url
r2 = requests.get(script_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
app_id = re.search(r'"x-app-id":"([^"]+)"', r2.text).group(1)
url = "https://flash-api.jin10.com/get_flash_list?channel=-8200&limit=50"
r3 = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "x-app-id": app_id,
                                "x-version": "1.0.0", "Referer": "https://www.jin10.com/"}, timeout=10)
jin10_news = r3.json().get("data", [])
print(f"金十数据: {len(jin10_news)}条 | 样本={jin10_news[0].get('data',{}).get('content','')[:60]}")
```

> **国内新闻直连API优势**：免费无Key、7x24实时快讯、覆盖国内+全球财经。
> **限制**：仅最新快讯（无历史归档）、API可能随网站更新而变更、须断开VPN。
> **与AKShare互补**：直连API覆盖7x24实时快讯，AKShare覆盖个股关联新闻(stock_news_em)+研报(stock_research_report_em)。

### §7.8 免费源验证脚本

```python
"""免费源连接验证脚本——运行此脚本确认主力免费源可用
主力源 = Baostock(A股) + TickFlow(美股) + AKShare(宏观/国内新闻/研报) + 财经RSS(国外新闻)
废弃源 = yfinance(Yahoo库级限流) + Stooq(JS浏览器验证)
注意: 须用 py -3.11 运行；AKShare 测试前须断开 VPN；RSS/TickFlow/Baostock 不受VPN影响
"""
import sys

def test_baostock():
    try:
        import baostock as bs
        bs.login()
        rs = bs.query_history_k_data_plus("sh.600000", "date,code,open,high,low,close,volume",
                                          start_date="2025-06-01", frequency="d")
        rows = []
        while (rs.error_code == '0') and rs.next():
            rows.append(rs.get_row_data())
        bs.logout()
        assert len(rows) > 0, "Baostock返回空"
        print(f"✅ Baostock OK: 600000 日K线 {len(rows)}行")
        return True
    except Exception as e:
        print(f"❌ Baostock 失败: {e}")
        return False

def test_tickflow():
    try:
        from tickflow import TickFlow
        tf = TickFlow.free()
        df = tf.klines.get("AAPL.US", period="1d", count=5, as_dataframe=True)
        assert not df.empty, "TickFlow AAPL.US返回空"
        print(f"✅ TickFlow OK: AAPL.US {len(df)}行 close={df['close'].iloc[-1]}")
        return True
    except Exception as e:
        print(f"❌ TickFlow 失败: {e}")
        return False

def test_akshare():
    try:
        import akshare as ak
        df = ak.macro_china_cpi()
        assert not df.empty, "AKShare CPI返回空"
        print(f"✅ AKShare OK: CPI {len(df)}行")
        return True
    except Exception as e:
        print(f"❌ AKShare 失败: {e}（若挂VPN请断开后重试）")
        return False

def test_rss():
    try:
        import feedparser
        feed = feedparser.parse("https://www.cnbc.com/id/100003114/device/rss/rss.html")
        n = len(feed.entries)
        assert n > 0, "CNBC RSS返回空"
        print(f"✅ 财经RSS OK: CNBC {n}条")
        return True
    except Exception as e:
        print(f"❌ 财经RSS 失败: {e}")
        return False

if __name__ == "__main__":
    results = [test_baostock(), test_tickflow(), test_akshare(), test_rss()]
    print(f"\n总结: {sum(results)}/4 主力免费源可用")
    if not all(results):
        sys.exit(1)
```

---

## §8 通达信 TDX/mootdx/pytdx 数据源完整指南（v1.9.0 新增）

### §8.1 概述与定位

| 属性 | 值 |
|------|-----|
| 项目主页 | https://github.com/mootdx/mootdx （主仓） / https://gitee.com/ibopo/mootdx （Gitee镜像） |
| PyPI 包名 | `mootdx` |
| 协议 | MIT（开源免费，无API Key） |
| Python 版本 | 3.8+（推荐3.10+） |
| 当前稳定版 | 0.11.x（截至2026-07） |
| 上游依赖 | `pytdx`（通达信协议底层实现） |
| 数据来源 | 通达信行情服务器（TCP协议直连） + 通达信本地数据文件解析 |
| 实测状态 | ⚠️ **文档级验证**（基于官方文档+GitHub README+WebSearch综合整理，2026-07-06），尚未在本机实测调用；首次使用前须运行 §8.7 验证脚本 |

**定位**：TDX/mootdx 是 Baostock/AKShare 之外的第三个 A 股免费数据源，其**独有价值**是：
1. **通达信板块分类（880xxx.TDX体系）**——iFind/AKShare/Baostock 均无此分类（同花顺/申万/东财分类与通达信不兼容）
2. **本地通达信数据文件读取**——直接解析 .day/.lc1/.lc5 二进制文件，零网络延迟
3. **个股最近交易日分笔数据**——`client.transaction()` 可获取最近交易日个股分笔（非3秒Tick，无五档）
4. **全周期K线（frequency=0~9）**——5分/15分/30分/60分/日/周/月/1分 全覆盖

**重要限制**：
- ❌ **不支持板块指数分笔历史**——用户淘宝购买的 sector/mkt_index 板块分笔数据（2011-11~2026-07）**无 API 可持续更新**，只能从通达信客户端手工导出（详见 §8.6）
- ❌ **不支持历史个股分笔**——`client.transaction()` 仅取最近交易日，历史个股分笔需淘宝购买
- ❌ **不支持复权数据**——仅原始价格，前复权/后复权需自行计算
- ❌ **不支持估值/EDB/新闻/研报**——这些能力用 iFind/AKShare
- ❌ **不支持美股**——TDX协议仅覆盖A股+港股(扩展)+期货(扩展)
- ⚠️ **服务器稳定性**——TDX服务器由各券商提供（非官方SLA），偶尔断线需 `bestip=True` 自动切换

### §8.2 环境配置

#### §8.2.1 安装

```powershell
# 完整功能安装（推荐）
pip install -U 'mootdx[all]'

# 仅核心功能
pip install 'mootdx'

# 包含命令行工具
pip install 'mootdx[cli]'

# 验证安装
python -c "import mootdx; print(mootdx.__version__)"
# 预期输出: 0.11.x
```

#### §8.2.2 服务器优选（首次使用前必跑）

```powershell
# 自动测试并选择响应速度最快的TDX服务器节点（一次性）
python -m mootdx bestip --verbose
# 输出会写入 ~/.mootdx/config.json，后续 Quotes.factory(bestip=True) 自动读取
```

### §8.3 可获取数据完整清单

#### §8.3.1 在线行情（quotes 模块，需网络）

> **API 清单已结构化**：TDX 在线行情 API 记录在 `depgraph.data_source_apis` 表（DS-TDX-API-001~005），详见 [asset_catalog.md](../../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。

- `client.bars(symbol, frequency, offset)` — A股K线全周期（frequency=0~9 对应 5分/15分/30分/60分/日/周/月/1分）
- `client.index(symbol, frequency)` — 指数K线（symbol='000001'上证）
- `client.quote(symbol)` — 实时报价（code/name/price/rise/percent）
- `client.minute(symbol)` — 分时数据（datetime/price/avg_price/volume）
- `client.transaction(symbol)` — 个股分笔（仅最近交易日；buyorsell:0=买/1=卖/2=中性）

#### §8.3.2 本地数据文件读取（reader 模块，需安装通达信客户端）

> **API 清单已结构化**：TDX 本地文件 API 记录在 `depgraph.data_source_apis` 表（DS-TDX-API-006~009），详见 [asset_catalog.md](../../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。

- `reader.daily(symbol)` — 日线（.day，解析 `vipdoc/sh/lday/shXXXXXX.day`）
- `reader.minute(symbol, suffix=1)` — 分钟线（.lc1）
- `reader.fzline(symbol)` — 5分钟线（.lc5）
- `reader.block(symbol, group=True)` — 板块分类（.dat：block_gn=概念 / block_fg=行业，880xxx.TDX体系）

> **路径约定**：通达信默认数据目录 `C:/new_tdx/vipdoc/`，沪市在 `sh/`，深市在 `sz/`，港股在 `hk/`。

#### §8.3.3 财务数据（affair 模块）

> **API 清单已结构化**：TDX 财务数据 API 记录在 `depgraph.data_source_apis` 表（DS-TDX-API-010~011），详见 [asset_catalog.md](../../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。

- `Affair.files()` — 可下载财务文件列表（返回 `gpcwYYYYMMDD.zip` 列表）
- `Affair.fetch(downdir, filename)` — 下载财务数据包（单个或全量）

> **财务数据格式**：gpcw YYYYMMDD.zip 解压后为 `.dat` 二进制文件，需配套 `财务数据对照表.xls` 解读字段含义（通达信官方提供）。

#### §8.3.4 扩展行情（ExtQuotes 模块）

> **API 清单已结构化**：TDX 扩展行情 API 记录在 `depgraph.data_source_apis` 表（DS-TDX-API-012），详见 [asset_catalog.md](../../../02_enterprise_architecture/01_global_architecture_diagram/asset_catalog.md) §数据源 API 清单。

- `ExtQuotes().bars(market, symbol, frequency)` — 港股/期货K线（market=47=港股；不同品种 market 值不同）

### §8.4 API 调用完整示例（直接复制可用）

#### §8.4.1 在线行情——A股K线（全周期）

```python
from mootdx.quotes import Quotes

# 初始化客户端（bestip=True 自动选择最优服务器）
client = Quotes.factory(market='std', multithread=True, heartbeat=True, bestip=True)

# 日K线（frequency=9）
daily = client.bars(symbol='600036', frequency=9, offset=100)
# 返回 DataFrame: ['datetime','open','high','low','close','volume','amount']

# 周/月/分钟K线（仅 frequency 不同）
weekly  = client.bars(symbol='600036', frequency=5, offset=52)   # 周线
monthly = client.bars(symbol='600036', frequency=6, offset=12)   # 月线
min5    = client.bars(symbol='600036', frequency=0, offset=100)  # 5分钟
min15   = client.bars(symbol='600036', frequency=1, offset=100)  # 15分钟
min30   = client.bars(symbol='600036', frequency=2, offset=100)  # 30分钟
min60   = client.bars(symbol='600036', frequency=3, offset=100)  # 60分钟
min1    = client.bars(symbol='600036', frequency=7, offset=240)  # 1分钟

# 指数K线（symbol='000001' 上证指数 / '399001' 深证成指 / '399006' 创业板指）
index_daily = client.index(symbol='000001', frequency=9)
```

#### §8.4.2 在线行情——实时报价与分时

```python
# 实时报价
quote = client.quote(symbol='600036')  # 招商银行
# 返回 dict: {'code','name','price','rise','percent', ...}

# 分时数据
minute = client.minute(symbol='000001')  # 平安银行分时
# 返回 DataFrame: ['datetime','price','avg_price','volume']
```

#### §8.4.3 在线行情——个股分笔（最近交易日）

```python
# ⚠️ 仅获取最近交易日的个股分笔数据，历史分笔需淘宝购买
transactions = client.transaction(symbol='600036')
# 返回 DataFrame: ['time','price','vol','num','buyorsell']
# buyorsell: 0=买盘/1=卖盘/2=中性盘
```

#### §8.4.4 本地通达信数据文件读取

```python
from mootdx.reader import Reader

# 初始化本地读取器（指定通达信安装目录）
reader = Reader.factory(market='std', tdxdir='C:/new_tdx')
# 路径必须指向通达信安装根目录（含 vipdoc/ 子目录）

# 日线数据（解析 vipdoc/sh/lday/sh600036.day）
daily = reader.daily(symbol='600036')

# 分钟线（解析 vipdoc/sh/fzline/sh600036.lc1）
minute = reader.minute(symbol='600036', suffix=1)

# 5分钟线（解析 vipdoc/sh/fzline/sh600036.lc5）
min5 = reader.fzline(symbol='600036')
```

#### §8.4.5 通达信板块分类（TDX独有，880xxx体系）

```python
from mootdx.reader import Reader

reader = Reader.factory(market='std', tdxdir='C:/new_tdx')

# 概念板块（解析 T0002/block_gn.dat）
concept_blocks = reader.block(symbol='block_gn.dat', group=True)
# 返回 DataFrame: ['blockname','code','stock_count', ...]
# blockname=概念板块名称 / code=板块下股票代码 / stock_count=板块股票数

# 行业板块（解析 T0002/block_fg.dat）
industry_blocks = reader.block(symbol='block_fg.dat')

# ⚠️ 通达信板块分类体系（880xxx.TDX）与同花顺/申万/东财分类不兼容
# 这是 TDX 独有的分类视角，可作为策略研究的补充维度
```

#### §8.4.6 财务数据下载与解析

```python
from mootdx.affair import Affair

# 1. 查询可下载的财务文件列表（全量历史）
files = Affair.files()
# 返回 list: ['gpcw19960630.zip','gpcw19961231.zip',...,'gpcw20231231.zip']

# 2. 下载单个财务文件
Affair.fetch(downdir='./financial_data', filename='gpcw20231231.zip')

# 3. 全量下载（首次使用时，会比较慢）
Affair.fetch(downdir='./financial_data')

# 4. 解析下载的 .dat 文件（需配合通达信官方"财务数据对照表.xls"解读字段）
# 通常 .dat 文件位于 downdir/ 下，按日期命名
```

#### §8.4.7 扩展行情——港股/期货

```python
from mootdx.quotes import ExtQuotes

# 港股K线（market=47）
hk_client = ExtQuotes()
hk_daily = hk_client.bars(market=47, symbol='00700', frequency=9, offset=100)
# 腾讯控股日K线

# 期货K线（market值因品种而异，需查通达信文档）
# futures = hk_client.bars(market=..., symbol='...', frequency=9)
```

#### §8.4.8 智能缓存（高频查询优化）

```python
from mootdx.utils.pandas_cache import pandas_cache

# 装饰器模式，1小时缓存
@pandas_cache(expire=3600)
def fetch_minute(symbol):
    client = Quotes.factory(market='std')
    return client.minute(symbol=symbol)

# 首次调用从接口获取（~500ms）
data1 = fetch_minute('600036')
# 后续调用直接读缓存（~10ms）
data2 = fetch_minute('600036')
```

### §8.5 TDX 与其他数据源对比

| 维度 | TDX/mootdx | Baostock | AKShare | iFind | QMT |
|------|-----------|----------|---------|-------|-----|
| 协议类型 | 通达信TCP协议直连 | 服务端推送 | 爬虫聚合 | iFind专有协议 | QMT专有协议 |
| 服务器成本 | 免费（券商TDX服务器） | 免费（官方） | 免费（爬国内网站） | 试用账号/正式付费 | 需QMT账号 |
| VPN 影响 | 无影响 | 无影响 | ⚠️ 有害（须断开） | 无影响 | 无影响 |
| A股K线 | ✅ 全周期(0~9) | ✅ 日/周/月/分钟 | ⚠️ 部分 | ✅ 全周期 | ✅ 全周期 |
| 板块分类 | ✅ **880xxx体系独有** | ❌ | ⚠️ 申万行业 | ⚠️ 同花顺行业 | ❌ |
| 财务数据 | ✅ gpcw zip | ✅ 季频6项 | ⚠️ 部分 | ✅ 时间序列 | ✅ 11张表 |
| 个股分笔 | ⚠️ **仅最近交易日** | ❌ | ❌ | ❌ | ✅ 3秒Tick |
| 复权数据 | ❌ 仅原始价格 | ✅ 前复权 | ⚠️ 部分 | ✅ 前复权 | ✅ 除权因子 |
| 估值PE/PB | ❌ | ⚠️ 部分 | ❌ | ✅ 精确个股 | ❌ |
| 宏观EDB | ❌ | ❌ | ✅ CPI/PMI/M2 | ⏳ 5万条/周 | ❌ |
| 美股 | ❌ | ❌ | ❌ | ❌ 试用不支持 | ❌ |
| 新闻/研报 | ❌ | ❌ | ✅ 东财个股 | ❌ 试用不支持 | ❌ |

### §8.6 分笔数据可持续获取方案（9个市场分类，重要）

**用户痛点**：用户通过淘宝购买+百度云下载已获取9个市场的历史分笔成交数据（stock/stock_bj/index/hk/etf/lof/cb/sector/mkt_index）。**核心问题：未来增量如何持续获取？如果无法持续获取，历史数据将沦为"死数据"**。

**结论速览**：9个市场的可持续获取能力差异巨大——6个可持续（个股类），3个不可持续（指数/板块类）。

#### §8.6.1 9个市场分笔数据可持续获取能力总览

| 分类 | 市场 | 已购历史范围 | 可持续获取？ | 推荐方案 | 粒度匹配 |
|------|------|------------|:----------:|---------|:-------:|
| **A股个股类** | stock | 2000-06 ~ 2026-07 | ✅ 可持续 | miniQMT每日增量（3秒快照）或L2逐笔 | ⚠️/✅ |
| **A股个股类** | stock_bj | 2020-07 ~ 2026-07 | ✅ 可持续 | 同上 | ⚠️/✅ |
| **基金类** | etf | 2005-02 ~ 2026-07 | ✅ 可持续 | miniQMT支持ETF Tick | ⚠️/✅ |
| **基金类** | lof | 2008-06 ~ 2026-07 | ✅ 可持续 | 同上 | ⚠️/✅ |
| **基金类** | cb | 2018-09 ~ 2026-07 | ✅ 可持续 | miniQMT支持可转债Tick | ⚠️/✅ |
| **港股** | hk | 2025-01 ~ 2026-07 | ⚠️ 部分可持续 | miniQMT港股通（957只，非全市场） | ⚠️ |
| **指数分笔** | index | 2000-07 ~ 2026-07 | ❌ 不可持续 | 无API，用K线替代 | ❌ |
| **板块分笔** | sector | 2011-11 ~ 2026-07 | ❌ 不可持续 | 手工导出/自建聚合/静态参考 | ❌ |
| **板块分笔** | mkt_index | 2011-11 ~ 2026-07 | ❌ 不可持续 | 同上 | ❌ |

> **粒度说明**：用户淘宝购买的是**真实逐笔成交**（每一笔成交一条记录）；miniQMT Tick 是 **3秒快照**（含五档买卖盘，非真实逐笔）；L2 逐笔成交才是真实逐笔。⚠️ 表示粒度不一致，✅ 表示粒度匹配。

#### §8.6.2 个股类分笔可持续获取方案（stock/stock_bj/etf/lof/cb）

##### 方案A：miniQMT 每日增量下载（推荐，已具备能力，免费）

```python
from xtquant import xtdata
# 每日收盘后自动跑，5000只10分钟完成
xtdata.download_history_data(stock_code, period='tick', 
                             start_time='YYYYMMDD', incrementally=True)

# 批量下载（多线程，500只一组）
xtdata.download_history_data2(stock_list, period='tick', 
                              start_time='YYYYMMDD', end_time='YYYYMMDD')

# 实时订阅（盘中推送）
xtdata.subscribe_quote(stock_code, period='tick', callback=on_tick)
xtdata.subscribe_whole_quote(code_list=['SH','SZ'], callback=on_tick)
```

**优势**：
- ✅ 免费（已有QMT账号）
- ✅ 全A股+ETF+可转债覆盖
- ✅ 支持批量多线程，5000只10分钟完成
- ✅ `incrementally=True` 自动只下载缺失部分
- ✅ 含五档买卖盘（10档行情）

**关键限制**：
- ⚠️ **Tick 是 3 秒快照**（不是真实逐笔成交），粒度比淘宝购买的真实逐笔粗
- ⚠️ miniQMT 仅最近交易日 Tick，完整版 QMT 才能下载历史 Tick
- ⚠️ 历史数据（真实逐笔）与未来增量（3秒快照）粒度不一致，需在策略层处理

##### 方案B：QMT Level-2 逐笔成交（需开通L2权限，粒度匹配）

```python
from xtquant import xtdata
# 真实逐笔成交，粒度匹配用户淘宝买的数据
xtdata.download_history_data(stock_code, period='l2transaction', 
                             start_time='YYYYMMDD', incrementally=True)
xtdata.download_history_data(stock_code, period='l2order',  # 逐笔委托
                             start_time='YYYYMMDD', incrementally=True)

# 读取
l2_trans = xtdata.get_l2_transaction(stock_code, start_time, end_time)
l2_order = xtdata.get_l2_order(stock_code, start_time, end_time)
```

**优势**：
- ✅ **真实逐笔成交**（每一笔成交一条记录），粒度与淘宝购买数据完全匹配
- ✅ 含逐笔委托（l2order），比逐笔成交更细
- ✅ 可每日增量下载，持续获取

**要求**：
- ⚠️ 需在券商开通 **L2 行情权限**（通常资金门槛50万+，或部分券商免费提供）
- ⚠️ 部分券商 miniQMT 不支持 L2，需完整版 QMT

##### 方案C：mootdx client.transaction()（免费，仅最近交易日）

```python
from mootdx.quotes import Quotes
client = Quotes.factory(market='std', bestip=True)
# 仅获取最近交易日的个股分笔（真实逐笔）
transactions = client.transaction(symbol='600036')
# 返回 DataFrame: ['time','price','vol','num','buyorsell']
# buyorsell: 0=买盘/1=卖盘/2=中性盘
```

**优势**：
- ✅ 免费，无需任何账号
- ✅ **真实逐笔成交**，粒度匹配淘宝购买数据
- ✅ 不受 VPN 影响

**限制**：
- ❌ **仅最近交易日**，无法补历史
- ❌ 不支持 ETF/可转债/港股分笔（仅 A股个股）
- ⚠️ 可每日自动跑做增量，但若某日失败则该日数据永久丢失

##### 方案D：付费第三方 API（如 gugudata）

- gugudata：当日分笔实时数据，499元/月 或 1999元/年
- 其他付费源：Wind/Choice/iFind正式版（均有分笔数据，但费用高昂）

#### §8.6.3 港股分笔可持续获取方案（hk）

| 方案 | 操作 | 覆盖范围 | 限制 |
|------|------|---------|------|
| miniQMT 港股通 | `xtdata.download_history_data('00700.HK', period='tick')` | 957只港股通标的 | 非全市场港股；3秒快照非逐笔 |
| mootdx ExtQuotes | `ExtQuotes().bars(market=47, symbol='00700')` | 港股K线 | ❌ 仅K线，非分笔 |
| 手工导出 | 通达信客户端→港股→导出分笔 | 全市场 | 半自动，每月1次 |

**推荐**：miniQMT 港股通覆盖核心标的（957只），3秒快照粒度；非港股通标的只能手工导出或接受为静态参考表。

#### §8.6.4 指数分笔可持续获取方案（index）

**关键结论：指数分笔无 API 可持续获取**

| 数据源 | 指数分笔能力 | 说明 |
|--------|------------|------|
| miniQMT | ❌ 仅指数K线 | `xtdata.download_history_data('000001.SH', period='1d')` 仅K线 |
| mootdx | ❌ 仅指数K线 | `client.index()` 仅K线，非分笔 |
| iFind | ❌ 仅指数K线 | THS_HistoryQuotes 仅OHLCV |
| Baostock | ❌ 仅指数K线 | query_history_k_data_plus 仅K线 |
| 通达信客户端 | ⚠️ 手工导出 | 可导出指数分笔，但需手工操作 |

**可行方案**：

| 方案 | 操作 | 频率 | 自动化 |
|------|------|------|--------|
| A. 接受为静态参考表 | 不持续更新，仅作为 2000-07~2026-07 历史快照 | 一次性 | 无 |
| B. 用指数K线替代 | 放弃分笔粒度，用1分钟/日K线替代 | 每日自动 | 高 |
| C. 通达信客户端手工导出 | 每月从通达信导出指数分笔 | 每月1次 | 半自动 |
| D. 用ETF分笔替代指数分笔 | 沪深300ETF(510300)分笔替代沪深300指数分笔 | 每日自动 | 高 |

**推荐方案 A+B 组合**：
- **历史已购数据（2000-07~2026-07）**：作为静态参考表保留（方案A）
- **未来增量**：用 miniQMT 指数K线（1分钟/日）替代（方案B），接受粒度变粗
- **若必须分笔粒度**：用对应ETF分笔替代（方案D），如 510300 替代沪深300指数

#### §8.6.5 板块分笔可持续获取方案（sector/mkt_index）

**关键结论：板块分笔无 API 可持续获取**

**原因**：
- mootdx/pytdx 通过 TCP 协议直连通达信行情服务器，仅支持**个股分笔最近交易日**（`client.transaction()`），**不支持板块指数分笔历史下载**
- 通达信官方量化插件 TDXQuant 明确"暂时不支持获取分笔数据"
- QMT/miniQMT 不支持板块分笔
- 同花顺 iFind 有板块指数但也是 K 线级别，不是分笔
- TDX 板块指数复盘系统（业界方案）也仅获取板块指数"开高低收量价"，非分笔

**用户已购数据**：sector/mkt_index 板块分笔成交历史数据（2011-11 ~ 2026-07，存于百度云 `量化交易数据/通达信板块_分笔成交/` 与 `量化交易数据/通达信板块_分笔成交/通达信_市场统计指数_分笔成交_按月归档/`）

**可行方案**（按优先级）：

| 方案 | 操作 | 频率 | 难度 | 自动化程度 |
|------|------|------|------|----------|
| A. 通达信客户端手工导出 | 打开通达信客户端→选择板块指数→导出分笔数据→导入 ClickHouse | 每月1次 | 中 | 半自动（客户端导出后脚本自动入库） |
| B. 接受为静态参考表 | 不持续更新，仅作为 2011-11~2026-07 的历史快照参考 | 一次性 | 低 | 无 |
| C. 用同花顺板块替代 | 同花顺iFind有881二级行业板块（已通过 THS_WC 问财接口更新 tdx_sector_info 表），分笔数据用同花顺板块指数K线替代 | 每日自动 | 低 | 高（已实现） |
| D. 自建板块分笔聚合 | 用个股分笔数据（mootdx client.transaction 或 miniQMT L2 每日下载）按通达信板块成分股（block_gn.dat/block_fg.dat）聚合为板块分笔 | 每日 | 高 | 高（需自建聚合逻辑） |

**推荐方案 C+D 组合**：
- **历史已购数据（2011-11~2026-07）**：作为静态参考表保留，不再更新（方案B）
- **未来增量**：采用方案D——每日通过 mootdx `client.transaction()` 或 miniQMT L2 下载个股分笔，按通达信板块成分股（block_gn.dat/block_fg.dat）聚合为板块分笔成交
- **同花顺交叉验证**：用同花顺881二级行业板块（已实现 tdx_sector_info 表更新）作为另一维度板块分类（方案C）

#### §8.6.6 推荐决策矩阵（9个市场未来增量获取策略）

```
┌──────────────────────────────────────────────────────────────────────────┐
│  9个市场分笔数据未来增量获取策略（v1.9.0，2026-07-06）                       │
├──────────────────────────────────────────────────────────────────────────┤
│  市场         │ 历史已购范围       │ 未来增量方案              │ 自动化  │
├──────────────────────────────────────────────────────────────────────────┤
│  stock        │ 2000-06~2026-07    │ miniQMT tick每日增量      │ ✅ 高   │
│  stock_bj     │ 2020-07~2026-07    │ miniQMT tick每日增量      │ ✅ 高   │
│  etf          │ 2005-02~2026-07    │ miniQMT tick每日增量      │ ✅ 高   │
│  lof          │ 2008-06~2026-07    │ miniQMT tick每日增量      │ ✅ 高   │
│  cb           │ 2018-09~2026-07    │ miniQMT tick每日增量      │ ✅ 高   │
│  hk           │ 2025-01~2026-07    │ miniQMT港股通tick(957只)  │ ⚠️ 中  │
│  index        │ 2000-07~2026-07    │ ❌ 无API，用K线替代        │ ⚠️ 中  │
│  sector       │ 2011-11~2026-07    │ ❌ 无API，方案C+D组合      │ ⚠️ 中  │
│  mkt_index    │ 2011-11~2026-07    │ ❌ 无API，方案C+D组合      │ ⚠️ 中  │
└──────────────────────────────────────────────────────────────────────────┘
```

#### §8.6.7 关键限制与注意事项

1. **粒度不一致问题（重要）**：
   - 用户淘宝购买的历史数据 = **真实逐笔成交**（每一笔成交一条记录）
   - miniQMT Tick = **3秒快照**（含五档买卖盘，非真实逐笔）
   - QMT L2 逐笔成交 = **真实逐笔**（粒度匹配）
   - **若策略依赖真实逐笔粒度**：必须开通 L2 权限用 `get_l2_transaction()`，否则历史与未来粒度不一致
   - **若策略可接受3秒快照**：miniQMT 免费即可，但需在策略层处理粒度差异

2. **miniQMT vs 完整版 QMT**：
   - miniQMT：仅最近交易日 Tick，免费
   - 完整版 QMT：可下载历史 Tick（3秒快照），需完整版权限
   - L2 逐笔：需开通 L2 行情权限（资金门槛50万+ 或部分券商免费）

3. **mootdx client.transaction() 的增量风险**：
   - 仅最近交易日，若某日下载失败则该日数据**永久丢失**（无法补历史）
   - 建议作为 backup，主力用 miniQMT

4. **板块/指数分笔的"断代"问题**：
   - 2011-11~2026-07 有淘宝购买的历史分笔数据
   - 2026-07 之后无 API 可持续获取
   - **断代点 = 2026-07**，之后只能用 K 线替代或自建聚合

5. **自建板块分笔聚合（方案D）的开发量**：
   - 需每日下载全市场个股分笔（5000只 × 10分钟）
   - 需维护通达信板块成分股映射（block_gn.dat/block_fg.dat 每月刷新）
   - 需实现聚合逻辑（按板块成分股加权/简单求和/成交量加权等）
   - 预计开发周期 1-2 周

6. **数据归档策略**：
   - 历史已购数据（淘宝）作为"金标准"快照保留，不再更新
   - 未来增量数据标注 `data_source` 字段区分来源（bdpan/miniqmt/mootdx/l2）
   - 定期交叉验证不同来源数据的一致性

#### §8.6.8 分笔数据可持续获取实施路线图

| 阶段 | 任务 | 优先级 | 依赖 |
|------|------|:------:|------|
| Phase 1 | miniQMT 每日增量下载个股类分笔（stock/stock_bj/etf/lof/cb） | P0 | 已有QMT账号 |
| Phase 2 | 评估是否开通 L2 权限（粒度匹配需求） | P1 | 策略层粒度需求评估 |
| Phase 3 | miniQMT 港股通分笔每日增量（hk，957只） | P1 | 已有QMT账号 |
| Phase 4 | index 指数分笔 → 用指数K线替代方案实施 | P2 | 策略层接受K线粒度 |
| Phase 5 | sector/mkt_index 板块分笔 → 方案D自建聚合开发 | P2 | Phase 1 完成 |
| Phase 6 | 历史已购数据作为静态参考表归档（index/sector/mkt_index） | P3 | 无 |

### §8.7 TDX 数据源验证脚本

```python
"""TDX/mootdx 数据源连接与功能验证脚本
首次使用 TDX 前必跑，验证通过后再接入业务流程。
注意：须先 pip install 'mootdx[all]' && python -m mootdx bestip --verbose
"""
import sys

def test_mootdx_install():
    try:
        import mootdx
        print(f"✅ mootdx 安装OK: 版本={mootdx.__version__}")
        return True
    except ImportError:
        print("❌ mootdx 未安装，请运行: pip install 'mootdx[all]'")
        return False

def test_kline_daily():
    try:
        from mootdx.quotes import Quotes
        client = Quotes.factory(market='std', bestip=True)
        df = client.bars(symbol='600036', frequency=9, offset=5)
        assert df is not None and len(df) > 0, "日K线返回空"
        print(f"✅ 日K线OK: 600036 返回 {len(df)} 行, 最新close={df['close'].iloc[-1]}")
        return True
    except Exception as e:
        print(f"❌ 日K线失败: {e}")
        return False

def test_realtime_quote():
    try:
        from mootdx.quotes import Quotes
        client = Quotes.factory(market='std', bestip=True)
        q = client.quote(symbol='600036')
        assert q and 'price' in q, "实时报价返回异常"
        print(f"✅ 实时报价OK: 600036 price={q.get('price')} name={q.get('name')}")
        return True
    except Exception as e:
        print(f"❌ 实时报价失败: {e}")
        return False

def test_index_kline():
    try:
        from mootdx.quotes import Quotes
        client = Quotes.factory(market='std', bestip=True)
        df = client.index(symbol='000001', frequency=9)
        assert df is not None and len(df) > 0, "指数K线返回空"
        print(f"✅ 指数K线OK: 上证指数 返回 {len(df)} 行")
        return True
    except Exception as e:
        print(f"❌ 指数K线失败: {e}")
        return False

def test_local_reader():
    """本地数据读取测试（需安装通达信客户端）"""
    try:
        from mootdx.reader import Reader
        # ⚠️ 修改为你的通达信安装路径
        reader = Reader.factory(market='std', tdxdir='C:/new_tdx')
        df = reader.daily(symbol='600036')
        if df is not None and len(df) > 0:
            print(f"✅ 本地读取OK: 600036 日线 {len(df)} 行")
            return True
        else:
            print("⚠️ 本地读取返回空（未安装通达信客户端或路径错误）")
            return False
    except Exception as e:
        print(f"⚠️ 本地读取跳过: {e}")
        return False

def test_block_data():
    """通达信板块分类测试（TDX独有能力）"""
    try:
        from mootdx.reader import Reader
        reader = Reader.factory(market='std', tdxdir='C:/new_tdx')
        # 概念板块
        concept = reader.block(symbol='block_gn.dat', group=True)
        if concept is not None and len(concept) > 0:
            print(f"✅ 通达信板块分类OK: 概念板块 {len(concept)} 行")
            return True
        else:
            print("⚠️ 板块分类返回空（需通达信客户端已下载板块数据）")
            return False
    except Exception as e:
        print(f"⚠️ 板块分类跳过: {e}")
        return False

if __name__ == "__main__":
    print("=== TDX/mootdx 数据源验证 ===\n")
    results = [
        test_mootdx_install(),
        test_kline_daily(),
        test_realtime_quote(),
        test_index_kline(),
        test_local_reader(),  # 可选（需通达信客户端）
        test_block_data(),    # 可选（需通达信客户端）
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n总结: {passed}/{total} 项通过")
    # 在线行情3项必过，本地读取2项可选
    if results[0] and results[1] and results[2] and results[3]:
        print("✅ 核心在线行情可用，可接入业务流程")
        sys.exit(0)
    else:
        print("❌ 核心在线行情不可用，请检查网络或运行 python -m mootdx bestip --verbose")
        sys.exit(1)
```

### §8.8 TDX 数据源运维规则

1. **首次使用前**：必须运行 `pip install 'mootdx[all]'` + `python -m mootdx bestip --verbose` + §8.7 验证脚本
2. **服务器稳定性**：TDX服务器偶尔断线，`Quotes.factory(bestip=True)` 会自动切换最优服务器；若持续失败，重跑 `python -m mootdx bestip`
3. **板块分笔历史**：**无 API 可持续更新**（§8.6），用户已购 sector/mkt_index 数据作为静态参考表保留，未来增量按方案 C+D 组合实施
4. **本地数据读取**：必须安装通达信客户端并下载完整数据，路径 `tdxdir='C:/new_tdx'` 需指向实际安装目录
5. **频率限制**：TDX服务器无明确频率限制，但建议控制 < 5次/秒避免被服务器临时封禁
6. **VPN 影响**：TDX 协议直连不受 VPN 影响（与 Baostock/TickFlow 一致），可挂 VPN 使用
7. **与 iFind/QMT 交叉验证**：首次使用 TDX K线数据时，应与 iFind THS_HistoryQuotes 交叉验证 close/volume 一致性
8. **数据归档**：TDX 在线获取的数据写入 ClickHouse 后不再更新历史（与 Baostock/AKShare 一致，避免上游追溯调整）
9. **板块分类更新**：通达信板块成分股（block_gn.dat/block_fg.dat）随股票上市/退市变化，建议每月用 `reader.block()` 重新读取并刷新 `tdx_sector_info` 相关表

### §8.9 TDX 与项目现有架构的关系

| 项目现有数据源 | TDX 替代关系 | 说明 |
|--------------|-------------|------|
| iFind THS_HistoryQuotes | ⚠️ 部分替代 | TDX可替代日/周/月/分钟K线，但无换手率/涨跌幅字段 |
| iFind THS_BasicData (PE/PB) | ❌ 不可替代 | TDX无估值数据 |
| iFind THS_DateSerial (财务) | ⚠️ 部分替代 | TDX gpcw zip 可下载财务，但需手动解析 |
| iFind THS_iwencai (i问财) | ❌ 不可替代 | TDX无自然语言查询能力 |
| QMT download_history_data | ⚠️ 部分替代 | TDX可替代K线，但无3秒Tick/除权因子/期权/可转债 |
| Baostock query_history_k_data_plus | ✅ 互补 | 两者均为A股K线免费源，可交叉验证 |
| AKShare stock_news_em | ❌ 不可替代 | TDX无新闻数据 |
| 淘宝购买的板块分笔历史 | ❌ **不可持续替代** | TDX无板块分笔历史API（§8.6） |

### §8.10 文档维护规则

1. **本文件是数据源 API 调用的操作手册（SSoT）**：AI 查询本文档 = 零幻觉空间；AI 绕过本文档自行推断 = 幻觉/漂移根源。可下载数据清单见数据库 `data_source_assets` 表。
2. **新增数据源时**：必须在 §1 总览 + §2/§3/§7/§8 详细指南 + §4 对比矩阵 + §5 获取策略 中同步更新。
3. **API 验证后**：必须将调用方法固化到 §2.4 / §3.4 / §7.7 / §8.4 的完整示例中，避免重复探索。
4. **遇到新坑时**：必须记录到对应数据源章节的技术备注，包含症状、根因、修复方法。
5. **免费源接口失效时**：必须记录到 §7.6 风险与限制，并提供替代方案（多源备份）。
6. **TickFlow 失效应急**：TickFlow 限流或失效时，立即切换到需API Key的 Alpha Vantage/Tiingo/Finnhub（见 §7.5 限制说明），并跟踪 TickFlow 官网修复进度。
7. **交叉验证**：免费源与 iFind/QMT 关键数据（如宏观CPI）应交叉验证一致性；TDX 首次使用 K线/财务数据时与其他源交叉验证。
8. **VPN 使用规则**：下载免费源数据前**必须断开 VPN**（Baostock/TickFlow/TDX/财经RSS 不受影响，AKShare 爬国内网站挂 VPN 会失败）；VPN 对 yfinance/Stooq 无效（已废弃）。
9. **TDX 接口失效时**：必须记录到 §8.5 对比表 + §8.8 运维规则，并提供替代方案。
10. **TDX bestip 失效应急**：可手动指定服务器 IP:PORT（如 `Quotes.factory(market='std', server=('115.238.90.226', 7709))`），或切换到 Baostock 作为 A股 K线 backup。
11. **C1 表填充状态变化时**：填充状态见 ClickHouse 实时扫描。

---

--- 文档结束 ---
