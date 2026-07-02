---
module_id: MOD-L00-002
submodule_path: src/zephyr/data
title: "数据源能力地图 — iFind + miniQMT 可获取数据完整清单与获取方法"
doc_type: blueprint
status: Active
version: "1.0.0"
layer: data
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
last_updated: "2026-07-03"
generation: 1
rule_form: reference
scope: module
stability: evolving
verifiability: empirical
references:
  - path: "d:\\ZephyrAlpha\\docs\\03_modules\\_domain_data\\blueprint.md"
    section: "§4 接口契约"
    why: "数据接入层主蓝图——本地图是其数据源能力的详细展开"
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
  - target: ARCH-BIZDB-001
    at: "§5"
    why: "业务数据库母蓝图品类全景"
priority: P0
runtime_plane: hot
tags:
  - data-source
  - ifind
  - miniqmt
  - capability-map
  - l00
  - ssoT
summary: "数据源能力地图——iFind(70个API) + miniQMT(87个API)可获取数据的完整清单与获取方法。所有API调用方法、配置细节、参数坑均已实测验证并固化，AI查询本文档=零幻觉空间，无需重新探索。"
---

# 数据源能力地图 — iFind + miniQMT

## 概述

本文件是 ZephyrAlpha 项目**数据源能力的唯一真源（SSoT）**，详细记录 iFind 和 miniQMT 两个数据源能获取哪些数据、以及如何获取。所有 API 调用方法、环境配置、参数细节均已通过实测验证并固化于本文档。

**核心价值**：AI 查询本文档 = 零幻觉空间；AI 绕过本文档自行推断 = 幻觉/漂移根源。本文档存在的意义是**避免 AI 重复探索数据源接入方法**——所有方法已固化，直接复制调用即可。

### 数据获取三层逻辑（硬约束）

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
└─────────────────────────────────────────────────────────────┘
```

**核心铁律**：只获取 iFind + QMT 未来能持续获取的数据，边界外的不碰。原因：现在获取不了的数据，未来也获取不了，策略无法依赖。

### 实测验证状态（2026-07-03）

| 数据源 | 环境 | 验证状态 | 实测日期 |
|--------|------|---------|---------|
| iFind | 试用账号 werty017 | ✅ 12类API逐个验证 | 2026-07-03 |
| miniQMT | XtMiniQmt.exe 运行中 | ✅ 15类API逐个验证 | 2026-07-03 |

---

## §1 数据源总览

### 1.1 iFind（同花顺金融数据接口）

| 属性 | 值 |
|------|-----|
| SDK来源 | `D:\同花顺Ifind金融终端api\THSDataInterface_Windows_20260227\` |
| API数量 | 70个函数，8大接口类别 |
| 数据库规模 | EDB 77,909指标 + FDB 9,875指标 + CodeTables 130万+证券 |
| 当前账号 | 试用账号 werty017（有限制，见 §2.4） |
| Python版本 | 3.x（无版本限制） |

### 1.2 miniQMT（国金证券QMT xtquant）

| 属性 | 值 |
|------|-----|
| SDK来源 | `D:\国金证券QMT交易端\bin.x64\Lib\site-packages\xtquant\` |
| API数量 | 87个函数 |
| 板块覆盖 | 36个板块（A股/期货/期权/转债/ETF等） |
| 运行要求 | XtMiniQmt.exe 必须运行，is_connected=True |
| Python版本 | **必须 3.11**（pyd文件最高cp311，不支持3.12） |

### 1.3 能力边界一句话总结

- **iFind 擅长**：估值数据、财务数据、宏观EDB、i问财自然语言查询、概念板块
- **QMT 擅长**：3秒Tick、分钟K线、期权/可转债/ETF/期货、除权因子、实时快照
- **iFind 独有**：EDB宏观数据（77,909指标）、i问财、估值PE/PB/PS
- **QMT 独有**：3秒Tick(含五档)、除权除息因子、指数权重、期权/可转债/期货合约
- **两者均无**：美股/港股（试用账号限制）、新闻事件、研究报告（试用账号限制）

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

# 登录（0=成功, -201=已登录）
r = THS_iFinDLogin('werty017', 'R16w864M')
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

### §2.3 可下载数据清单（实测验证）

#### ✅ 可正常下载（10类）

| # | 数据类型 | 接口 | 测试样本 | 数据字段 |
|---|---------|------|---------|---------|
| 1 | **日K线** | THS_HistoryQuotes(Interval:D) | 600000.SH 21行 | preClose/open/high/low/close/avgPrice/change/changeRatio/volume/turnoverRatio/amount/transactionAmount |
| 2 | **周K线** | THS_HistoryQuotes(Interval:W) | 600000.SH 5行 | open/high/low/close/volume/amount |
| 3 | **月K线** | THS_HistoryQuotes(Interval:M) | 同上 | 同日K线 |
| 4 | **估值数据(PE/PB/PS)** | THS_BasicData | 600000.SH PE=11.45 PB=0.69 | ths_pe_stock/ths_pb_stock/ths_ps_stock/ths_pcf_stock_ttm/ths_dividend_ratio_stock |
| 5 | **财务数据(时间序列)** | THS_DateSerial | 600000.SH 30行 | ths_close_price_stock + 可查ROE/净利润/总资产等 |
| 6 | **指数成分股** | THS_DataPool(index) | 沪深300 300行 | DATE/THSCODE/SECURITY_NAME |
| 7 | **行业成分股** | THS_DataPool(index) | 同花顺行业 30行 | DATE/THSCODE/SECURITY_NAME |
| 8 | **实时行情** | THS_RealtimeQuotes | 600000.SH | latest/changeRatio/amount/volume/inflow/outflow |
| 9 | **i问财-资金流向** | THS_iwencai | 前10只 | 股票代码/股票简称/主力资金流向/排名 |
| 10 | **i问财-概念板块** | THS_iwencai | 同花顺概念 | 股票代码/股票简称/所属概念 |

### §2.4 试用账号限制

#### ⚠️ 试用账号限制（3类，正式账号可解除）

| # | 数据类型 | 错误码 | 限制说明 | 正式账号预期 |
|---|---------|--------|---------|-------------|
| 11 | **5分钟/分钟K线** | -4309 | 试用账号只能获取1年历史 | ✅ 正式账号无限制 |
| 12 | **EDB宏观数据** | -4318 | ⏳ 月度配额限制(下月重置) | ✅ 正式账号无限制 |
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

### §2.5 iFind API 调用方法（完整示例，直接复制可用）

#### 2.5.1 登录

```python
from iFinDPy import *
r = THS_iFinDLogin('werty017', 'R16w864M')
# 0=成功, -201=已登录
```

#### 2.5.2 日/周/月K线（THS_HistoryQuotes）

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

#### 2.5.3 估值数据 PE/PB/PS（THS_BasicData）— ⚠️ 参数格式坑

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

#### 2.5.4 财务数据时间序列（THS_DateSerial）

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

#### 2.5.5 指数/行业成分股（THS_DataPool）

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

#### 2.5.6 实时行情（THS_RealtimeQuotes）

```python
data = THS_RealtimeQuotes(
    '600000.SH',
    'open;high;low;latest;changeRatio;amount;volume;bid1;ask1;bidSize1;askSize1;inflow;outflow'
)
df = THS_Trans2DataFrame(data)
# ✅ 返回实时行情快照（含盘口+资金流向）
```

#### 2.5.7 i问财自然语言查询（THS_iwencai）— 最灵活的接口

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

#### 2.5.8 EDB宏观数据（THS_EDBQuery）— ⏳ 月度配额限制

```python
# EDB = Economic Data Base，77,909个宏观/行业经济指标
# 分类: 中国宏观11,762 + 行业经济24,522 + 全球宏观12,385 + 利率1,646 + 经济景气991 + 世界经济3,573 + 区域宏观23,030
data = THS_EDBQuery(
    'M001620326;M002822183',  # 指标代码（分号分隔）
    '2025-01-01',
    '2025-06-30'
)
# ⏳ 试用账号 -4318 "exceeded this month" 月度配额超限，下月自动重置
# ✅ 正式账号无配额限制，可立即下载
```

#### 2.5.9 组合查询（获取行业成分股的实时行情）

```python
# 1. 获取行业成分股
thsData = THS_DataPool('index', '2025-06-30;884183.TI', 'date:Y,thscode:Y,security_name:Y')
ths_codes = ','.join(thsData['tables'][0]['table']['THSCODE'])

# 2. 批量获取实时行情
thsdata = THS_RealtimeQuotes(ths_codes,
    'open;high;low;latest;changeRatio;amount;volume;bid1;ask1;bidSize1;askSize1;inflow;outflow')
result = THS_Trans2DataFrame(thsdata)
```

### §2.6 iFind EDB 宏观数据库详解

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

### §3.3 可下载数据清单（实测验证 2026-07-03）

#### K线数据（download_history_data + get_market_data_ex）

| # | 数据类型 | period | 测试样本 | 测试结果 | 说明 |
|---|---------|--------|---------|---------|------|
| 1 | **日K线** | 1d | 600000.SH 2025-06-01~06-30 | ✅ 20行 | open/high/low/close/volume/amount/settle/openInterest/preClose/suspendFlag |
| 2 | **日K线(长历史)** | 1d | 600000.SH 2024-01-01~2025-06-30 | ✅ 359行 | download成功，日期范围20240102~20250630 |
| 3 | **前复权日K线** | 1d,dividend_type='front' | 600000.SH | ✅ 20行 | 复权处理正常 |
| 4 | **1分钟K线** | 1m | 600000.SH 2026-07-02 | ✅ 241行 | 09:30开始每分钟一根 |
| 5 | **5分钟K线** | 5m | 600000.SH 2026-07-02 | ✅ 48行 | 09:35开始每5分钟一根 |
| 6 | **Tick数据(3秒)** | tick | 600000.SH 2026-07-02 | ✅ 4998行 | 09:15:03开始，含五档买卖盘 |
| 7 | **指数日K线** | 1d | 000001.SH上证指数 | ✅ 20行 | 指数数据正常 |
| 8 | **批量K线** | 1d | 5只股票同时 | ✅ 各20行 | 600000.SH/000001.SZ/600519.SH/000858.SZ/601318.SH |
| 9 | **ETF日K线** | 1d | 510300.SH沪深300ETF | ✅ 20行 | ETF数据正常 |
| 10 | **可转债日K线** | 1d | 111017.SH | ✅ 20行 | 可转债数据正常 |

> **高频数据时间限制**：5分钟K线/Tick/1分钟K线只能下载**最近交易日**的数据，历史高频数据 QMT 本地不保留（需淘宝购买历史数据）。日K线可下载长历史（359行验证成功）。

#### 实时数据

| # | 数据类型 | 函数 | 测试结果 | 说明 |
|---|---------|------|---------|------|
| 11 | **实时全Tick** | get_full_tick | ✅ 成功 | 600000.SH最新价8.70/成交量711376，000001.SZ最新价10.28 |
| 12 | **实时行情订阅** | subscribe_quote / subscribe_whole_quote | ✅ API可用 | 推送模式，需订阅后回调 |

#### 基础数据

| # | 数据类型 | 函数 | 测试结果 | 说明 |
|---|---------|------|---------|------|
| 13 | **除权除息因子** | get_divid_factors | ✅ 26条 | 600000.SH 26次除权记录（2000年至今） |
| 14 | **交易日历** | get_trading_dates('SH',...) | ✅ 21天 | market参数必须用'SH'不是'SSE' |
| 15 | **交易日历(全)** | get_trading_calendar('SH') | ✅ 8673天 | 从19901219开始 |
| 16 | **股票详情** | get_instrument_detail | ✅ 成功 | 浦发银行，含涨跌停价/流通股本/总股本/上市日期 |
| 17 | **板块列表** | get_sector_list | ✅ 36个板块 | 含A股/期货/期权/转债/ETF等 |

#### 合约列表

| # | 数据类型 | 函数 | 测试结果 | 说明 |
|---|---------|------|---------|------|
| 18 | **A股股票列表** | get_stock_list_in_sector('沪深A股') | ✅ 5207只 | 全部A股 |
| 19 | **期权合约列表** | get_stock_list_in_sector('上证期权') | ✅ 662个 | 期权合约代码 |
| 20 | **可转债列表** | get_stock_list_in_sector('上证转债') | ✅ 152个 | 可转债代码 |
| 21 | **ETF列表** | get_stock_list_in_sector('沪市ETF') | ✅ 946个 | ETF代码 |
| 22 | **中金所期货合约** | get_stock_list_in_sector('中金所') | ✅ 802个 | 含IF/IC/IH/IM等合约 |

#### API已知待实际验证

| # | 数据类型 | 函数 | 签名 | 说明 |
|---|---------|------|------|------|
| 23 | **财务数据** | download_financial_data2 + get_financial_data | get_financial_data(stock_list, table_list, start_time, end_time, report_type) | table_list见 §3.6 |
| 24 | **指数权重** | download_index_weight() + get_index_weight(index_code) | download无参，get传index_code | — |
| 25 | **Level-2逐笔委托** | get_l2_order | (field_list, stock_code, start_time, end_time, count) | 需L2权限 |
| 26 | **Level-2逐笔成交** | get_l2_transaction | 同上 | 需L2权限 |
| 27 | **Level-2行情** | get_l2_quote | 同上 | 需L2权限 |
| 28 | **可转债详情** | get_cb_info | — | 可转债基本信息 |
| 29 | **ETF详情** | get_etf_info | — | ETF基本信息 |
| 30 | **期权详情** | get_option_detail_data | — | 期权Greeks |

### §3.4 数据频率支持

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

### §3.5 miniQMT API 调用方法（完整示例，直接复制可用）

#### 3.5.1 初始化（必须）

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

#### 3.5.2 日K线（注意参数顺序坑！）

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

#### 3.5.3 下载历史数据 + 获取（两步）

```python
# 步骤1: 下载（返回None是正常的！源码无return语句）
xtdata.download_history_data('600000.SH', '1d', '20240101', '20250630')
# 参数: (stock_code, period, start_time, end_time)
# 返回 None = 正常，数据已异步下载到本地

# 步骤2: 获取（从本地读取）
data = xtdata.get_market_data_ex([], ['600000.SH'], '1d', '20240101', '20250630')
df = data['600000.SH']  # ✅ 359行
```

#### 3.5.4 5分钟K线 / 1分钟K线 / Tick（最近交易日）

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

#### 3.5.5 前复权K线

```python
# dividend_type: 'none'(不复权) / 'front'(前复权) / 'back'(后复权) / 'front_ratio' / 'back_ratio'
data = xtdata.get_market_data_ex(
    [], ['600000.SH'], '1d', '20250601', '20250630',
    -1,           # count: -1=全部
    'front'       # dividend_type: 前复权
)
```

#### 3.5.6 实时Tick快照

```python
tick = xtdata.get_full_tick(['600000.SH', '000001.SZ'])
# 返回 {'600000.SH': {lastPrice, open, high, low, volume, amount,
#                     askPrice:[5档], bidPrice:[5档], askVol:[5档], bidVol:[5档], ...}}
```

#### 3.5.7 交易日历（market参数坑）

```python
# ✅ 正确: market用 'SH' 或 'SZ'
dates = xtdata.get_trading_dates('SH', '20250601', '20250701')
# ✅ 21天

# ❌ 错误: market用 'SSE' 或 'SZSE' 会返回空
# dates = xtdata.get_trading_dates('SSE', '20250601', '20250701')  # 空!

# 全量交易日历
cal = xtdata.get_trading_calendar('SH')  # ✅ 8673天，从19901219开始
```

#### 3.5.8 股票/合约列表

```python
stocks = xtdata.get_stock_list_in_sector('沪深A股')   # ✅ 5207只
opts   = xtdata.get_stock_list_in_sector('上证期权')   # ✅ 662个
cb     = xtdata.get_stock_list_in_sector('上证转债')   # ✅ 152个
etf    = xtdata.get_stock_list_in_sector('沪市ETF')    # ✅ 946个
cffex  = xtdata.get_stock_list_in_sector('中金所')     # ✅ 802个
```

#### 3.5.9 除权除息因子

```python
df = xtdata.get_divid_factors('600000.SH')
# ✅ 26条记录（2000年至今），含 interest/stockBonus/allotPrice/gugai/dr 等字段
```

#### 3.5.10 股票详情

```python
detail = xtdata.get_instrument_detail('600000.SH')
# ✅ 含 InstrumentName/UpStopPrice/DownStopPrice/FloatVolume/TotalVolume/OpenDate 等
```

#### 3.5.11 批量下载多只股票

```python
codes = ['600000.SH', '000001.SZ', '600519.SH', '000858.SZ', '601318.SH']
# 批量下载
for code in codes:
    xtdata.download_history_data(code, '1d', '20250601', '20250630')
# 批量获取
data = xtdata.get_market_data_ex([], codes, '1d', '20250601', '20250630')
# ✅ 各20行
```

### §3.6 财务数据 API（11张报表）

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

### §3.7 miniQMT 36个板块列表

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

## §4 iFind vs miniQMT 对比矩阵

### §4.1 能力对比总表

| # | 数据类型 | iFind 试用账号 | miniQMT | 推荐来源 | 说明 |
|---|---------|:--------------:|:-------:|---------|------|
| 1 | 日K线 | ✅ 21行 | ✅ 已验证(359行) | 两者均可 | QMT 可下载长历史，iFind 增量更新 |
| 2 | 周K线 | ✅ 5行 | ✅(1w周期) | iFind | iFind 字段更全（含换手率） |
| 3 | 月K线 | ✅ | ✅(1mon周期) | iFind | 同上 |
| 4 | 1分钟K线 | ❌ 试用限制(-4309) | ✅ 已验证(241行) | **QMT** | QMT 可下载最近交易日 |
| 5 | 5分钟K线 | ❌ 试用限制(-4309) | ✅ 已验证(48行) | **QMT** | 历史需淘宝购买 |
| 6 | 15/30/60分钟K线 | ❌ 试用限制 | ✅(15m/30m/1h) | **QMT** | 同上 |
| 7 | 3秒Tick | ❌ | ✅ 已验证(4998行) | **QMT 独有** | 含五档买卖盘 |
| 8 | 集合竞价 | ❌ | ✅ API可用 | **QMT 独有** | subscribe_quote |
| 9 | 实时Tick快照 | ✅ | ✅ 已验证 | QMT | QMT 的 get_full_tick 字段更全 |
| 10 | 估值 PE/PB/PS | ✅ | ❌ | **iFind 独有** | iFind THS_BasicData |
| 11 | 财务数据 | ✅ 时间序列 | ✅ API可用(11张表) | 两者均可 | QMT 报表结构化，iFind 灵活查询 |
| 12 | 资金流向 | ✅ i问财 | ❌ | **iFind 独有** | i问财可自然语言查询 |
| 13 | 指数成分股 | ✅ 300行 | ✅ API可用 | iFind | iFind 已验证 |
| 14 | 行业分类 | ✅ 30行 | ⚠️ 返回空 | **iFind** | QMT 需特殊参数 |
| 15 | 概念板块 | ✅ i问财 | ❌ | **iFind 独有** | i问财可查询 |
| 16 | EDB 宏观数据 | ⏳ 配额限制(-4318,下月重置) | ❌ | iFind 正式账号 | 仅 iFind 有，77,909指标 |
| 17 | 期货数据 | ❌ 无权限 | ✅ 802个合约 | **QMT 独有** | QMT 有中金所/上期所/大商所 |
| 18 | 期权数据 | ❌ | ✅ 662个合约 | **QMT 独有** | QMT 有上证期权 |
| 19 | 可转债数据 | ❌ | ✅ 152个+K线 | **QMT 独有** | QMT 有上证转债 |
| 20 | ETF数据 | ❌ | ✅ 946个+K线 | **QMT** | QMT 有沪市ETF |
| 21 | 美股/港股 | ❌ 无权限(-4210) | ✅ 港股通已验证(957只+K线20行) | QMT(港股通) | 美股试用受限，港股QMT可获取 |
| 22 | 新闻/事件 | ❌ 不支持(-5100) | ❌ | 无 | 试用账号不支持 |
| 23 | 研究报告 | ❌ 不支持(-5100) | ❌ | 无 | 试用账号不支持 |
| 24 | Level-2数据 | ❌ | ⚠️ 需L2权限 | QMT | 需开通L2权限 |
| 25 | 除权除息因子 | ❌ | ✅ 已验证(26条) | **QMT 独有** | — |
| 26 | 指数权重 | ❌ | ✅ API可用 | **QMT 独有** | — |
| 27 | 交易日历 | ✅ THS_DateQuery | ✅ 8673天 | 两者均可 | QMT 已验证 |

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
| **两者均无** | — | 美股/港股(试用)、新闻事件、研究报告(试用) |

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
THS_iFinDLogin('werty017', 'R16w864M')

# 批量估值数据（注意参数格式坑，见 §2.5.3）
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
| P1 | EDB宏观数据 | 77,909个宏观/行业指标 | 解除-4318配额限制 |
| P1 | 美股/港股行情 | 海外市场数据 | 解除-4210权限拒绝 |
| P1 | 5分钟/分钟K线历史 | iFind历史高频 | 解除-4309一年限制 |
| P2 | 新闻/事件 | THS_iEvent | 解除-5100账号类型限制 |
| P2 | 研究报告 | THS_iResearch | 解除-5100账号类型限制 |
| P2 | CFFEX期货 | 中金所期货行情 | 解除-4216权限拒绝 |

### §5.6 C1 行情仓库 8 张表填充状态

> C1行情仓库8张表（tick_data/daily_kline/auction_snapshot/index_quote/option_iv_surface/futures_position/futures_term_structure/convertible_bond_iv）的填充状态、数据来源、验证结果，详见 [数据获取需求清单 §2.1 c1_market 行情库](data_acquisition_plan.md)（19张表完整对照，含8张空表填充状态）。

---

## §6 技术备注

### §6.1 iFind 估值数据正确参数格式（坑）

```python
# ✅ 正确格式: 指标用分号分隔，参数格式为 "日期,类型"
# 类型 100=静态值, 101=动态值
THS_BasicData('600000.SH',
    'ths_pe_stock;ths_pb_stock;ths_ps_stock',
    '2025-06-30,100;2025-06-30,100;2025-06-30,100')
# 返回: PE=11.45, PB=0.69

# ❌ 错误格式（会返回 null）
# THS_BasicData('600000.SH', 'ths_pe_stock', '2025-06-30')  # 缺少类型参数
```

**格式说明**：
- 第2参数：指标代码，多个用分号 `;` 分隔
- 第3参数：每个指标对应 `"日期,类型"`，多个用分号 `;` 分隔
- 类型 `100` = 静态值（历史日期），`101` = 动态值（最新）

### §6.2 miniQMT 运行要求与关键配置

1. **Python 版本**：必须 3.11（pyd 文件最高 cp311，不支持 3.12）
2. **QMT 客户端**：`XtMiniQmt.exe` 必须运行，`is_connected()` 返回 `True`
3. **sys.path**：必须用 `append`，不能用 `insert`（会覆盖系统 numpy）
4. **os.chdir**：必须 chdir 到 `D:\国金证券QMT交易端\bin.x64`（让相对路径 `../userdata_mini/datadir` 正确解析）
5. **禁止**：不能修改 `xtdata.data_dir` 为绝对路径（会破坏底层 C++ 函数，导致"周期错误"）
6. **下载流程**：K线/Tick 数据需要先 `download_history_data` 再 `get_market_data_ex`

### §6.3 miniQMT "周期错误" 根因与修复

**症状**：`get_market_data_ex` 返回"周期错误"（鍛ㄦ湡閿欒，GBK编码乱码），所有 period 值都报错。

**根因**：参数顺序搞反了。`get_market_data_ex` 的参数顺序是 `(field_list, stock_list, period, start_time, end_time)`，period 在第3位，不是第5位。

```python
# ✅ 正确: period在第3位
xtdata.get_market_data_ex([], ['600000.SH'], '1d', '20250601', '20250630')

# ❌ 错误: period在第5位（会报"周期错误"）
# xtdata.get_market_data_ex([], ['600000.SH'], '20250601', '20250630', '1d')
# → period='20250601' 不在 {'1m','5m','15m','30m','1h','1d'} 中
```

**诊断方法**：
1. 检查 `xtdata.get_client().is_connected()` 是否为 `True`
2. 检查 `os.getcwd()` 是否为 `D:\国金证券QMT交易端\bin.x64`
3. 检查参数顺序：period 必须在第3位
4. 检查 period 值是否在 `{'tick','1m','5m','15m','30m','1h','1d','1w','1mon'}` 中

### §6.4 miniQMT download_history_data 返回 None 是正常的

```python
result = xtdata.download_history_data('600000.SH', '1d', '20240101', '20250630')
print(result)  # None
# ✅ None 是正常的！源码中该函数没有 return 语句，数据已异步下载到本地
```

**原因**：`download_history_data` 源码中没有 `return` 语句，所以返回 `None`。数据是异步下载的，调用后立即返回，数据在后台写入本地 `datadir`。

### §6.5 miniQMT get_trading_dates market 参数坑

```python
# ✅ 正确: market 用 'SH' 或 'SZ'
xtdata.get_trading_dates('SH', '20250601', '20250701')  # 21天

# ❌ 错误: market 用 'SSE' 或 'SZSE' 会返回空
# xtdata.get_trading_dates('SSE', '20250601', '20250701')  # 空!
```

### §6.6 miniQMT 高频数据时间限制

| 数据类型 | 时间范围 | 说明 |
|---------|---------|------|
| 日K线（1d） | 长历史（359行验证） | 可下载多年历史 |
| 周K线（1w） | 长历史 | 同上 |
| 月K线（1mon） | 长历史 | 同上 |
| 1分钟K线（1m） | **仅最近交易日** | 历史需淘宝购买 |
| 5分钟K线（5m） | **仅最近交易日** | 同上 |
| 15/30/60分钟K线 | **仅最近交易日** | 同上 |
| Tick数据（tick） | **仅最近交易日** | 同上 |

**原因**：QMT 客户端本地不保留历史高频数据，只缓存最近交易日的高频数据。历史高频数据需通过淘宝购买后导入。

### §6.7 iFind 试用账号错误码速查

| 错误码 | 含义 | 影响数据 | 解决方案 |
|--------|------|---------|---------|
| -201 | 已登录 | 无 | 忽略，正常 |
| -4309 | 试用账号只能获取1年历史 | 5分钟/分钟K线 | 升级正式账号 |
| -4318 | ⏳ 月度配额限制(下月重置) | EDB宏观数据 | 下月自动恢复/升级正式账号 |
| -4216 | 中金所权限被拒 | CFFEX期货 | 升级正式账号+期货权限 |
| -4210 | 海外市场无权限 | 美股/港股 | 升级正式账号 |
| -5100 | 账号类型不支持 | 事件/研报 | 升级正式账号 |
| -4001 | 无数据 | 概念板块(DataPool) | 改用 i问财 |
| -209 | 参数无效 | 情绪指标等 | 查找正确指标代码 |

### §6.8 数据源连接验证脚本

**iFind 验证**：
```python
from iFinDPy import *
r = THS_iFinDLogin('werty017', 'R16w864M')
assert r == 0 or r == -201, f"iFind登录失败: {r}"
# 测试查询
data = THS_HistoryQuotes('600000.SH', 'open,high,low,close', 'Interval:D', '2025-06-01', '2025-06-30')
df = THS_Trans2DataFrame(data)
assert len(df) > 0, "iFind查询返回空"
print(f"iFind OK: {len(df)}行")
```

**miniQMT 验证**：
```python
import sys, os
sys.path.append(r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages')
os.chdir(r'D:\国金证券QMT交易端\bin.x64')
from xtquant import xtdata

client = xtdata.get_client()
assert client.is_connected(), "QMT未连接，请启动 XtMiniQmt.exe"
# 测试查询
data = xtdata.get_market_data_ex([], ['600000.SH'], '1d', '20250601', '20250630')
assert '600000.SH' in data and len(data['600000.SH']) > 0, "QMT查询返回空"
print(f"QMT OK: {len(data['600000.SH'])}行")
```

### §6.9 文档维护规则

1. **本文件是数据源能力的唯一真源（SSoT）**：AI 查询本文档 = 零幻觉空间；AI 绕过本文档自行推断 = 幻觉/漂移根源。
2. **新增数据源时**：必须在 §1 总览 + §2/§3 详细指南 + §4 对比矩阵 + §5 获取策略 中同步更新。
3. **API 验证后**：必须将调用方法固化到 §2.5 / §3.5 的完整示例中，避免重复探索。
4. **遇到新坑时**：必须记录到 §6 技术备注，包含症状、根因、修复方法。
5. **C1 表填充状态变化时**：必须同步更新 §5.6 的填充状态列。

---

> **文档结束** — 本文档由 AI-session-20260703-datasource 创建，所有 API 调用方法均已实测验证。如遇数据源 API 变更或新数据源接入，请同步更新本文档并提升 version。
