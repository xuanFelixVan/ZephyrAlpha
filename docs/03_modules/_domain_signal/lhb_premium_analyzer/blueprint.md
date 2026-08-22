---
blueprint_id: MOD-SIG-057
module_name: lhb_premium_analyzer
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-SIG-057 lhb_premium_analyzer 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘录 §9.7（yueniuzq 2026-07 口径），M3-⑤ 次日预判。
> 代码：`src/zephyr/signal_ashare/lhb_premium_analyzer.py`

## 0. 定位

龙虎榜盘后溢价分析器——管"明天会怎样"：消费前一交易日龙虎榜（dragon_tiger_seat 608k 行 2022 起 + dragon_tiger 汇总，62 号注册表数据已在库未消费），输出次日开盘预判三名单+个股级溢价系数。与 MOD-SIG-056（seat_pattern_analyzer 管"谁在买"，单票单日席位形态）正交：本模块管"次日溢价"（全市场当日榜单批量扫描）。

## 1. 接口

```python
def compute_lhb_premium(
    trade_date: str | date | datetime,
    ch_client: Any | None = None,            # clickhouse-driver 鸭子类型；None=延迟取 ch_writer.get_client
    config: LhbPremiumConfig | None = None,  # None=44号 §9.7 默认口径
) -> LhbPremiumResult
```

席位身份口径复用 `seat_registry.yaml`：机构=seat_type institution；一线/知名游资=registry 命中且 seat_style ∈ {龙头连板, 首板}（对齐 MOD-SIG-056 白名单）；一日游=registry 静态标签 + 近 20 交易日隔日卖出率>70% 动态复核。

## 2. 输出契约

`LhbPremiumResult`（frozen dataclass slots，asdict JSON 可序列化，prediction_log 预留）：

- `high_open_candidates`：净买率>5% 且买方机构+一线游资≥2 席
- `low_open_risks`：机构席位净卖出占比>5%
- `fanhe_watchlist`：跌停股买一为知名游资（联动 28 号反核阶段纪律）
- `premiums: dict[str, LhbSymbolPremium]`——各信号标的 premium_factor（1.0 基准 / 0.3 降权）+ tags + reasons 理由链
- 降权规则：独食型（单一席位买入占比>60%）/ 一日游型 → 高开候选溢价系数 ×0.3
- `degraded` / `notes`：降级留痕
- 「当日成交额」口径=龙虎榜上榜成交额（buy+sell，缺汇总行回退席位行合计），非全市场个股日成交额（该列龙虎榜表未携带）

## 3. 不变量（头注 INVARIANTS 原文）

- premium_factor ∈ {1.0, 0.3}
- 无数据/查询异常/客户端不可用 MUST 返回 degraded=True 空结果不炸
- T 日龙虎榜盘后 17:00 公布，本模块输出仅供 T+1 盘前消费（PIT）

## 4. 降级行为

- ERROR_CONTRACT：查询异常/客户端不可用→degraded=True 不抛；trade_date 格式非法→ValueError（调用方契约违例，fail-closed）
- 隔日卖出率动态复核样本<3 不定性（噪声护栏）
- 历史查询窗口 45 自然日覆盖 20 交易日

## 5. 边界（不做）

- MVP 阶段无消费方（候选：M3-③ 情景方案标的不例外清单、prediction_log 落库）
- 不做单票席位形态跟随信号（MOD-SIG-056 职责）

## 6. 测试

tests/signal_ashare/test_lhb_premium_analyzer.py
