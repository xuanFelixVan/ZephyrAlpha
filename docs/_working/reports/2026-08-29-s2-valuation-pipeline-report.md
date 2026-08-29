---
ttl: task_bound
---

# S2 估值"路A"指数级估值管道施工报告

> **任务**：建设 S2 估值"路A"指数级估值管道（c1_market.index_valuation_daily）
> **裁定**：Owner 已裁定③新建独立表（不复用个股 daily_valuation）+ ④直接做真 CAPE（拒绝 PE 中位平滑近似）
> **日期**：2026-08-29
> **施工人**：sub-agent

---

## 一、Step 0 勘探结果（四项）

### ① akshare stock_zh_index_value_csindex 实测

| 项目 | 结果 |
|---|---|
| 接口 | `ak.stock_zh_index_value_csindex(symbol='000300')` |
| 返回列 | 日期/指数代码/指数中文全称/指数中文简称/指数英文全称/指数英文简称/市盈率1/市盈率2/股息率1/股息率2 |
| 历史深度 | **仅最近 20 条**（约 1 个月），无 start/end 参数 |
| 速度 | 0.65s |
| 结论 | **不可用于历史回填**，仅适合增量采集当日快照 |

### ② akshare stock_index_pe_lg 实测（乐咕 fallback）

| 项目 | 结果 |
|---|---|
| 接口 | `ak.stock_index_pe_lg(symbol='沪深300')` |
| 返回列 | 日期/指数/等权静态市盈率/静态市盈率/静态市盈率中位数/等权滚动市盈率/滚动市盈率/滚动市盈率中位数 |
| 历史深度 | **2005-04-29 ~ 2026-08-28**，257 条**月度**数据 |
| 速度 | 3.72s |
| 结论 | 历史深度足够（21 年），但**月度频率**不满足日频 CAPE 计算需求，仅作交叉验证 fallback |

### ③ ClickHouse macro_data 盘点

| 指标 | 状态 | 覆盖范围 | 结论 |
|---|---|---|---|
| **CPI 月度** | ❌ 缺失 | macro_data 中仅有 `FRED_CPI_CN`（2021-08~2025-04，45 条）和 `WB_CPI_INFLATION/CHN`（年度 2016~2025，10 条） | **无中国月度 CPI 长历史**，需补采 akshare `macro_china_cpi_monthly`（1996-02~2025-09，357 条） |
| **10Y 国债** | ⚠️ 在位但浅 | `国债_10年`/`中国国债收益率10年` 覆盖仅 **2026-07-10 ~ 2026-08-28**（36 条） | 历史深度不足，需补采 akshare `bond_china_yield`（2010-2026 全历史，4163 条） |

### ④ 真 CAPE 口径可行性确认

| 项目 | 结果 |
|---|---|
| **日频 PE_TTM 源** | ✅ `ak.stock_zh_index_hist_csindex`（中证官网历史K线）含 `滚动市盈率` 列，2010-01-01 ~ 2026-08-28 共 4046 条日频记录，PE_TTM 非空 3621 条（2010 年初 NaN，2010-01-04 起有值） |
| **历史深度** | ✅ 4046 条 > 5 年 + 1250 交易日窗口（1250 交易日 ≈ 5 年） |
| **速度** | 36.56s（全历史 2010-2026） |
| **CPI 通胀调整** | ⚠️ macro_data 无中国月度 CPI，需补采 akshare `macro_china_cpi_monthly` |
| **10Y 国债（ERP）** | ⚠️ macro_data 覆盖仅 2026-07-10 起，需补采 akshare `bond_china_yield` 分年拉取 |

**关键发现**：`stock_zh_index_hist_csindex` 是真正的主源——支持 start_date/end_date 参数拉取全历史，返回 16 列含 `滚动市盈率`（PE_TTM）和 `股息率1`，日频。`stock_zh_index_value_csindex` 仅返回最近 20 条，不可用于历史回填。

---

## 二、改动/新增文件清单

### 新增文件（4 个）

| 文件 | 说明 |
|---|---|
| `schemas/categories/market_index_valuation_daily.py` | index_valuation_daily 表 DDL-as-Code（唯一真源） |
| `src/zephyr/data/implementations/index_valuation_compute.py` | 指数估值内部计算 Provider（CAPE/分位/ERP） |
| `tests/zephyr/data/test_index_valuation_compute.py` | 内部计算 Provider 单测（7 用例） |
| `tests/zephyr/data/test_akshare_index_valuation.py` | akshare 采集 Provider 单测（5 用例） |
| `tests/regime/test_overlay_signals_builder_valuation.py` | 路A 接线单测（4 用例） |

### 修改文件（5 个）

| 文件 | 改动 |
|---|---|
| `docs/03_modules/_cross_layer/database/business_data_categories.yaml` | 新增 `market_index_valuation_daily` 品类登记（calc_mode=preload，日频，SLA L2） |
| `src/zephyr/data/implementations/akshare_provider.py` | 新增 `_fetch_index_valuation_daily` 方法 + `_AKSHARE_CAPABILITIES`/`CapabilityContract` 注册 |
| `src/zephyr/data/implementations/internal_compute_provider.py` | `_INTERNAL_COMPUTE_CAPABILITIES` + `meta.capabilities` 注册 `index_valuation_daily`；`fetch()` 新增 `c1_market.index_valuation_daily` 路由分支委托 `IndexValuationComputeProvider` |
| `src/zephyr/data/config/tasks.yaml` | 新增 `index_valuation_daily_incremental`（依赖 kline_index_incremental）+ `index_valuation_daily_backfill`（2010-01-01 起全量回填） |
| `src/zephyr/regime/regime_feature_builder.py` | 新增 `get_index_valuation()` 透传方法（仿 get_money_flow/get_news_sentiment 模式） |
| `src/zephyr/regime/features/regime_data_loader.py` | 新增 `load_index_valuation()` 公共接口 + `_load_index_valuation()` 实际加载逻辑 |
| `src/zephyr/regime/overlay_signals_builder.py` | L349-350 改造：优先调 `s2_valuation_score_fundamental`（路A），数据缺失时降级回跑路B `s2_valuation_score(close)` 并 logger.warning |
| `tests/regime/test_overlay_signals_builder.py` | `_MockFeatureBuilder` 新增 `index_valuation` 参数 + `get_index_valuation()` 方法 |

---

## 三、表 DDL（c1_market.index_valuation_daily）

```sql
CREATE TABLE IF NOT EXISTS c1_market.index_valuation_daily
(
    trade_date       Date                     COMMENT '交易日期',
    symbol           String                   COMMENT '指数代码(000300/000905/399006)',
    pe_ttm           Decimal(18, 4)           COMMENT '市盈率TTM(中证官网滚动市盈率)',
    pb_mrq           Nullable(Decimal(18, 4)) COMMENT '市净率MRQ(一期暂缺,二期升级)',
    dividend_yield   Nullable(Decimal(18, 4)) COMMENT '股息率(中证官网股息率1,%)',
    cape_5y          Nullable(Decimal(18, 4)) COMMENT '5年真CAPE(P_t/mean_5y(real_E))',
    cape_5y_pct      Nullable(Decimal(18, 4)) COMMENT 'CAPE_5Y全历史分位(0~1)',
    pe_pct           Nullable(Decimal(18, 4)) COMMENT 'PE_TTM全历史分位(0~1)',
    pb_pct           Nullable(Decimal(18, 4)) COMMENT 'PB全历史分位(0~1,一期暂缺)',
    erp              Nullable(Decimal(18, 4)) COMMENT '股权风险溢价(1/PE-10Y国债,%)',
    erp_pct          Nullable(Decimal(18, 4)) COMMENT 'ERP全历史分位(0~1)',
    broken_net_ratio Nullable(Decimal(18, 4)) COMMENT '全市场破净率(二期预留)',
    buffett_ratio    Nullable(Decimal(18, 4)) COMMENT '总市值/GDP(二期预留)',
    data_source      LowCardinality(String)   DEFAULT 'akshare_csindex' COMMENT '数据来源',
    ingest_ts        DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
```

---

## 四、测试结果

| 测试文件 | 用例数 | 结果 |
|---|---|---|
| `tests/zephyr/data/test_index_valuation_compute.py` | 7 | ✅ 全通过 |
| `tests/zephyr/data/test_akshare_index_valuation.py` | 5 | ✅ 全通过 |
| `tests/regime/test_overlay_signals_builder_valuation.py` | 4 | ✅ 全通过 |
| **新建/改动相关合计** | **16** | **✅ 16/16 通过** |
| 既有回归测试（overlay_signals_builder + akshare_provider + internal_compute_provider） | 73 | ✅ 73/73 通过 |

---

## 五、CAPE 口径实现说明

### 真 CAPE（拒绝 PE 中位平滑近似）

```
E_i = P_i / PE_i          # 指数盈利代理（点位/PE_TTM）
real_E_i = E_i / CPI_i    # 通胀调整（CPI 月度前向填充到日频）
CAPE_t = P_t / mean_{近1250交易日}(real_E × CPI_t)
```

- **窗口**：1250 交易日（约 5 年），`min_periods=750`（3 年，防 warmup 期全 NaN）
- **CPI 缺失时**：退化为名义 CAPE（不调整通胀），logger.warning 留痕
- **分位口径**：全历史扩展窗分位（`rank(pct=True)`），非滚动窗口——与 `s2_valuation_score_fundamental` 消费端语义一致（危机期分位<25%→60 分）

### ERP 口径

```
erp = 1/PE_TTM - 10Y国债收益率    # 百分数口径（如 0.052 = 5.2%）
```

- 10Y 国债源：`c1_market.macro_data indicator_name='国债_10年'`（akshare bond_china_yield）
- 10Y 缺失时 ERP 为 NaN（降级，不阻塞 CAPE/分位计算）

---

## 六、遗留风险与后续事项

| 风险 | 说明 | 缓解 |
|---|---|---|
| **中证官网反爬** | `stock_zh_index_hist_csindex` 全历史拉取 36.56s/次，频繁调用可能触发反爬 | 增量任务每日只拉当日；历史回填一次性执行；已配置 fallback=internal（计算列仍可产出） |
| **CPI 数据缺失** | macro_data 无中国月度 CPI，真 CAPE 退化为名义 CAPE | 已登记为后续补采任务（akshare `macro_china_cpi_monthly`） |
| **10Y 国债历史浅** | macro_data 覆盖仅 2026-07-10 起，ERP 历史分位无法计算 | 已登记为后续补采任务（akshare `bond_china_yield` 分年拉取 2010-2026） |
| **PB/破净率/巴菲特** | 一期暂缺（pb_mrq/pb_pct/broken_net_ratio/buffett_ratio 恒 NULL） | 二期升级（乐咕月度 PB 频率不足，需找日频 PB 源或自算） |
| **历史回填未执行** | `index_valuation_daily_backfill` 任务已配置但未执行 | 报告回填命令（见下） |

---

## 七、历史回填命令（未执行，供后续手动触发）

```bash
# 全量回填 2010-01-01 起（周末校准时段）
python -m zephyr.data.cli run-task index_valuation_daily_backfill

# 或经 scheduler 手动触发
python -c "
from zephyr.data.scheduler import IntegratorScheduler
s = IntegratorScheduler()
s.run_task('index_valuation_daily_backfill')
"
```

**回填后 sanity check**：2015-08 / 2020-03 / 2024-09 三时点 CAPE/PB 分位应 <40%（危机期低估区间）。

---

## 八、接线验证

- `regime_feature_builder.get_index_valuation()` → `regime_data_loader.load_index_valuation()` → `c1_market.index_valuation_daily`
- `overlay_signals_builder._precompute()` S2 valuation 维度：优先 `s2_valuation_score_fundamental(cape_percentile=...)`，缺失时降级 `s2_valuation_score(close)` 并 `logger.warning`
- `s2_valuation_score_fundamental` 函数本身未改动（overlay_features.py:430 已落码）
