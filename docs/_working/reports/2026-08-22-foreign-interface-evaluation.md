---
ttl: task_bound
---

# 外盘接口评估报告（92号清单 §6.4 / 44号裁定五前置验证）

- 日期：2026-08-22（周六；外盘报价为周五收盘冻结值，属预期，文中已逐项注明）
- 工单：92号清单 §6.4 外盘接口评估批（44号裁定五前置验证）
- 范围纪律：纯验证+登记；未改 src/、未改配置、未改 tasks.yaml、未执行 git、未写注册表；测试脚本置 `.runtime/` 用完即删
- 环境：Windows / Python 3.12.8 / akshare 1.18.75 / Asia/Shanghai
- 方法：每接口最小调用；requests 全局 12s 超时 + future 20s 防御（ES/NQ 3 连调用 70s）；失败最多重试 2 次；记录列名/行数/首尾时间戳/耗时/异常类型与消息

## 一、接口可用性矩阵

| # | 目标 | 接口/通道 | 可拉性 | 关键字段 | 延时口径 | 历史深度 | 耗时 |
|---|------|-----------|:------:|----------|----------|----------|-----:|
| 1a | A50 实时 | 新浪 `hq.sinajs.cn/?list=hf_CHA50CFD`（裸调） | ✅ | 最新价/买/卖/高/低/行情时间(秒)/昨结/开/日期/名称/持仓/成交 | 免费准实时通道，需 Referer 头；周六冻结于 05:05:26，盘中延时未能实证 | — | ~0.3s |
| 1b | A50 日频历史 | `ak.futures_foreign_hist("CHA50CFD")` | ✅ | date/OHLC/volume/position（近端量仓有效） | 日频 | 2016-08-22 → 2026-08-21，2594 行（10 年） | 0.52s |
| 1c | A50 兜底快照 | `ak.futures_global_spot_em()` → `CN00Y` A50期指当月连续 | ✅ | 最新价/涨跌额/涨跌幅/今开/高/低/昨结/量/买卖盘/持仓；**无时间戳字段** | 不明（无时间戳可比对） | — | 12.3~12.5s（全市场 620 行分页拉取） |
| 1d | A50 结算价 | `ak.futures_settlement_price_sgx(date)` | ❌ | — | 日级 ZIP | — | `ConnectionError: RemoteDisconnected`（其日历计算依赖 push2his，本机不可达，见 §六） |
| 2a | 中概实时（KWEB） | 新浪 `hq.sinajs.cn/?list=gb_kweb`（裸调） | ✅ | 名称/最新价/涨跌幅/时间戳/52周高低/成交量/市值等 | akshare docstring 明示**美股延时 15 分钟**；周六取证时间戳 05:18:42(北京)/Aug 21 05:14PM EDT | — | 0.32s |
| 2b | 中概日频（KWEB） | `ak.stock_us_daily(symbol="KWEB")` | ✅ | date/OHLC/volume | 日频；最新行 2026-08-20（滞后 1 个交易日，周五未入库） | 2205 行（约 9 年量级） | 0.64~0.74s |
| 2c | 金龙指数 | 新浪 `gb_hxc` 探测 | ⚠️ 不可用 | 返回 25.0098 全日静止的同名美股 ticker（价格量级与波动均非金龙指数），**同名陷阱** | — | — | 0.32s |
| 3a | 商品实时×6 | `ak.futures_foreign_commodity_realtime(["CL","OIL","GC","XAU","HG","CAD"])` | ✅ | 名称/最新价/人民币报价/涨跌额/涨跌幅/开/高/低/昨结/持仓/买/卖/行情时间(秒)/日期（14 列） | 同上 hf 通道；周六冻结 04:59:59 | — | 1.05~1.07s（一批 6 品种） |
| 3b | 商品日频历史 | `ak.futures_foreign_hist("CL")` | ✅ | date/OHLC（volume/position/settlement 近端恒 0，勿用） | 日频 | 1996-08-22 → 2026-08-21，7690 行（30 年） | 0.55s |
| 4a | ES/NQ 实时 | 新浪 `hf_ES`/`hf_NQ`（裸调，3 连调间隔 10s） | ✅ | 同 1a 字段结构，含秒级行情时间 | 秒级时间戳；3 次载荷完全一致、冻结 04:59:59 2026-08-22（周六预期）；无 403/限频迹象 | — | 单次 ~0.3s |
| 4a' | ES/NQ 经 akshare wrapper | `ak.futures_foreign_commodity_realtime("ES")` | ❌ | `KeyError: 'ES'`（wrapper 硬编码品种表 30 个，无 ES/NQ/CHA50CFD） | — | — | 0.35s |
| 4b | ES/NQ 日频历史 | `ak.futures_foreign_hist("ES"/"NQ")` | ✅ | date/OHLC（量仓恒 0） | 日频 | ES：2016-08-22→2026-08-21，2593 行（10 年）；NQ：2018-04-24→2026-08-21，2159 行（8.3 年） | ~0.5s |
| 4c | ES/NQ 兜底快照 | `ak.futures_global_spot_em()` → `ES00Y`/`NQ00Y` | ✅（快照级） | 同 1c，**无时间戳**；周六量仓=0 | 不明 | — | 含于 12.3s 全市场调用 |
| 4d | ES/NQ 历史兜底 | `ak.futures_global_hist_em("ES00Y"/"NQ00Y"/...)` | ❌ | 6 个品种全部 `ConnectionError: RemoteDisconnected`（push2his 本机不可达） | — | — | 0.33~0.37s 即断 |
| 5a | 日经225/KOSPI 实时 | `ak.index_global_spot_em()` | ❌ as-is | 默认 UA 被 push2 断连；**同请求加浏览器 UA+Referer 实测 200**（N225 f2=6601636 正常返回） | — | — | 失败 0.4s / 带头 0.41s |
| 5b | 日经225/KOSPI 历史（东财） | `ak.index_global_hist_em("日经225"/"韩国KOSPI")` | ❌ | push2his 主机级不可达（默认 UA/浏览器头/http scheme 三态均 RemoteDisconnected） | — | — | 0.35~0.4s 即断 |
| 5c | 日经225/KOSPI 历史（新浪） | `ak.index_global_hist_sina("日经225指数"/"首尔综合指数")` | ✅ | date/OHLC/volume | 日频 | **封顶 1000 行≈4 年**（日经 2022-08-09→、首尔 2022-07-27→，均至 2026-08-21）；**末日行 close=0 脏数据**（两指数同现） | ~0.5s |

## 二、关键实证摘录（原始载荷）

**ES/NQ 三连调（seq1@05:21:37 / seq2@05:21:48 / seq3@05:21:58，三次完全一致）**：
```
var hq_str_hf_ES="7689.850,,7687.500,7688.000,7714.000,7661.250,04:59:59,7662.500,7669.000,0,37,33,2026-08-22,标普500指数期货,0";
var hq_str_hf_NQ="29361.680,,29373.000,29374.000,29539.000,29220.000,04:59:59,29300.500,29327.000,0,1,1,2026-08-22,纳斯达克指数期货,0";
```

**A50（hf_CHA50CFD @05:20:11）**：`"14824.560,,14818.000,14826.000,14849.000,14808.000,05:05:26,14843.000,14843.000,800082,7,1,2026-08-22,富时中国A50期货,55250"`；`hf_CHA50` 返回空串。

**KWEB（gb_kweb @05:21:59）**：`"中概网络股ETF,26.6600,-0.11,2026-08-22 05:18:42,-0.0300,26.9200,26.9500,26.5800,41.2690,23.2300,18193797,...,Aug 21 05:14PM EDT,..."`。

**东财 spot 关键代码全在位**（`futures_global_spot_em`，620 行）：`CN00Y` A50期指当月连续 14826.0（量 55250/持仓 800082，与新浪口径一致）、`ES00Y` 7690.86、`NQ00Y` 29358.83、`CL00Y` 86.64、`GC00Y` 4661.6、`HG00Y` 6.58、`SI00Y` 69.01。与新浪交叉比对：ES 7690.86 vs 7689.85、NQ 29358.83 vs 29361.68、A50 14826.0 vs 14824.56——同一冻结时刻的微小价差，量级互验通过。

**push2his 三态诊断**：默认 UA / 浏览器 UA+Referer / http scheme → 全部 0.1~0.4s 内 `ConnectionError: RemoteDisconnected`；对照 push2 加浏览器头 200 正常。判定：**push2his.eastmoney.com 主机级不可达（疑本机防火墙/运营商策略）**，非 UA 问题。

## 三、主源/兜底裁定建议（44号 §9.8 通道3 实证核对）

44号预设：主源=新浪 hf，兜底=东财。实证结论：

1. **主源=新浪 hf：实证支持，维持**。字段全（含秒级行情时间+日期）、单次 0.3~1s、免费通道仅需 `Referer: https://finance.sina.com.cn/` 头、无明文限频口径（10s 间隔连调无 403）；覆盖 ES/NQ/CHA50CFD/CL/OIL/GC/XAU/HG/CAD 全部目标品种。**唯一缺口**：akshare wrapper 品种表硬编码 30 个商品代码，ES/NQ/CHA50CFD 直接调 wrapper 报 `KeyError`——波 4 接线须裸调 `hq.sinajs.cn` 或自封装薄层。
2. **兜底=东财：修正**。东财三族端点本机表现分裂——
   - `futsseapi`（futures_global_spot_em）：可用，但 12s+ 全市场分页、**无时间戳字段**，只能当"最新价快照级兜底"，无法判新鲜度；
   - `push2`（index_global_spot_em 等）：默认 UA 被断连，需自带浏览器 UA+Referer 才通，akshare as-is 不可用；
   - `push2his`（全部 hist 族 + SGX 结算价日历依赖）：**主机级不可达**，历史兜底能力为零。
   - 裁定建议：东财兜底**降级保留为快照级**（futsseapi 族，可接受），历史兜底从 push2his 族移出；若统筹侧他机验证 push2his 可通，则为单机环境问题，可再议恢复。
3. **新增实证红利**：新浪 `futures_foreign_hist` 实测不仅覆盖商品（CL 30 年），还覆盖 `CHA50CFD`（10 年）、`ES`（10 年）、`NQ`（8.3 年）——**主源通道自带日频历史回填能力，兜底历史需求可整体缓解**。

## 四、A50 / 中概 / 商品 / 日韩接入建议

| 品种 | 裁定 | 接线要点 |
|------|------|----------|
| A50 期指 | **接入** | 实时主源=新浪裸调 `hf_CHA50CFD`；快照兜底=东财 `CN00Y`；历史=新浪 `futures_foreign_hist("CHA50CFD")`（10 年，量仓近端有效）。SGX 结算价接口**砍**（日级 + 本机不可达 + 对异动监控无增量价值） |
| 中概 | **接入 KWEB** | 实时=新浪 `gb_kweb`（口径：延时 15 分钟，盘前异动判断需按 15min 滞后解读）；日频=`stock_us_daily("KWEB")`（**symbol 必须大写**，小写触发 qfq 因子页解析 `SyntaxError`；最新行滞后 1 个交易日）。金龙指数**砍**（无干净代理，`gb_hxc` 系同名美股陷阱） |
| 商品（WTI/布伦特/金/铜） | **接入** | 实时=wrapper 一批 6 品种 1 次调用（1s）；历史=`futures_foreign_hist`（CL 30 年）。三个口径坑：①**人民币报价字段批量调用时错位**（实证 CL 批量 582.28 vs 单拉 4250.65，price_mul 对齐 bug），弃用该字段只存美元价；②周六持仓量=0、hist 量仓近端恒 0，量仓字段暂不入库；③COMEX 铜新浪单位美分/磅（668.34）vs 东财美元/磅（6.58），跨源比对前必须统一单位 |
| 日韩（日经225/KOSPI） | **砍**（44号裁定三授权：权重最低，接口不顺即砍） | 实时无 as-is 可用接口（东财 push2 需自实现带头才通）；历史仅新浪 1000 行≈4 年且末日 close=0 脏数据。若未来复活：仅考虑 `index_global_hist_sina` 日频 + 末行 `close=0` 清洗规则 |

## 五、ES/NQ 采集任务接线建议（波 4 用）

**端点**：`GET https://hq.sinajs.cn/?list=hf_ES,hf_NQ`，必带 `Referer: https://finance.sina.com.cn/` 头（不带则 403）；GBK 编码；免费、未见限频（10s 间隔实证）。

**字段映射**（hf 逗号分隔序，实证 + akshare `futures_hq_sina.py:152-167` 列序交叉确认）：

| 位置 | 含义 | 落库建议名 |
|---:|------|-----------|
| 0 | 最新价 | `last_price` |
| 2 | 买价 | `bid` |
| 3 | 卖价 | `ask` |
| 4 | 最高 | `high` |
| 5 | 最低 | `low` |
| 6 | 行情时间 HH:MM:SS | `quote_time` |
| 7 | 昨日结算价 | `prev_settle` |
| 8 | 开盘价 | `open` |
| 9 | 持仓量 | `open_interest`（周六为 0，盘中待验） |
| 12 | 日期 YYYY-MM-DD | `quote_date` |
| 13 | 中文名 | `name_cn` |

涨跌幅自算：`(last_price - prev_settle) / prev_settle`（源数据不带该字段）。

**建议调度频率**（可参数化）：
- 美股交易时段（北京 21:30~次日 05:00 夏令）：60s；
- A 股盘前窗口（09:00~09:30）：30~60s（盘前异动核心场景）；
- 其余时段：5min；
- 时间戳停滞 >2×采样间隔 → 判定冻结/休市，自动降频至 15min 或挂起（周六实证冻结态载荷恒等，硬拉无增量）。

**异动规则可参数化项**：`threshold_pct_warn`（默认 0.5）/ `threshold_pct_alert`（默认 1.0）、`ref_price_basis`（`prev_settle` 或 `open`）、`stale_tolerance`（默认 2×采样间隔）、`max_identical_ticks`、`poll_interval_sec`（分时段表）、`session_calendar`（美夏令/冬令切换）。

**历史回填**：`ak.futures_foreign_hist("ES"/"NQ")`，日频 10 年/8.3 年，`volume/position/settlement` 恒 0 勿入库。

## 六、风险与口径备注

1. **周六局限**：盘中秒级延时、限频边界、持仓量字段、人民币报价盘中形态均未能在交易日实证；上述结论中"准实时/不限频"为免费通道通行口径 + 周六间接证据，建议波 4 上线后首个交易日盘中复测一次 ES/NQ 时间戳推进（预期分钟级内推进）。
2. **push2his 本机不可达**（三态诊断均 RemoteDisconnected）：影响 `futures_global_hist_em`、`index_global_hist_em`、`futures_settlement_price_sgx`（日历依赖）、`stock_us_spot_em`。登记为环境级风险；若属本机防火墙/运营商策略，其他机器可能可通。
3. **akshare wrapper 品种表缺口**：`futures_hq_subscribe_exchange_symbol()` 硬编码 30 个商品代码，ES/NQ/CHA50CFD 不在表内；新浪底层 `hq.sinajs.cn` 实际支持（已实证）。自封装时注意 `XAU` 等 14 字段特例（akshare 源码 line 149 有 temp 列补丁）。
4. **新浪全球指数 hist 末日脏数据**：日经/首尔 2026-08-21 行 `close=0`（open/high/low 有值），消费端统一加 `close>0` 过滤。
5. **东财 spot 周六量仓口径**：ES00Y/NQ00Y 量仓=0，CL/GC/SI/CN00Y 为周五残留值——跨品种新旧不一，快照兜底仅取价格字段。

## 附：测试脚本处置

`.runtime/eval_s1_sina.py` ~ `eval_s8_kweb_depth.py` 共 7 个最小验证脚本，按工单纪律用完即删，不纳入仓内资产。
