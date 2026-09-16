---
ttl: task_bound
title: T1-β 节点挖矿：滑点与冲击成本模型（阈值来源/A股流动性分层/成本常数拍脑袋猎捕）
session: st-qoder-t1b-h-20260916
date: 2026-09-16
parent: S11_assembled_backtest
lane: H
---

# 节点挖矿：滑点与冲击成本模型（父环节 S11_assembled_backtest）

> 范围：撮合层成本三件套——**滑点（slippage_bps）**、**冲击成本（Almgren-Chriss）**、
> **成交量参与率上限（max_participation_rate）**，以及扫其他"拍脑袋"成本常数。佣金万0.854
> 已 Owner #233 裁定为实盘真值（本文**不重挖佣金费率本身**，只挖它与最低佣金地板的交互经济影响）。
> 结论全部实证：代码 file:line + 现网产物 `bt-fw-823d7fd7.json` 真数 + CH 只读 + 探针
> `.runtime/tmp/h_probe_costs.py`/`h_probe_costs2.py`/`h_probe_cap.py`。

## 1 现状盘点（成本常数的"校准来源"逐一验真/验伪）

### 1.1 费率单一真源位点（matching_logic.py:62-68）

| 常数 | 值 | 声明来源 | 验真结论 |
|------|----|---------|----------|
| COMMISSION_RATE | 0.0000854（万0.854，双向） | Owner #233 实盘协议价 | **已校准**✓（现网大额单边际费率实测=9.54e-5 含过户，:62） |
| STAMP_TAX_RATE | 0.0005（万5，卖出单边） | 2023-08 法定 | **法定**✓ |
| TRANSFER_FEE_RATE | 0.00001（万0.1，双向） | 沪深法定 | **法定**✓ |
| MIN_COMMISSION | 5 元（不免五） | Owner 2026-08-22 | **已校准**✓ 但见 §1.4 经济扭曲 |
| **SLIPPAGE_BPS** | **1 bp（固定）** | 注释："日频低换手口径，冲击成本另层覆盖" | **未校准（拍脑袋）**✗ + 前提被证伪 |
| lot_size | 100 | A股整手 | 法定✓ |
| price_limit_pct | 0.10 | 主板涨跌停兜底 | 法定✓（未知前缀最后防线） |

### 1.2 滑点 1bp：无来源 + 前置假设"低换手"被现网证伪

- 真源 `matching_logic.py:63 SLIPPAGE_BPS=1`；应用 `matching_logic.py:491-495
  _apply_slippage`（买 ×(1+1bp)、卖 ×(1-1bp)），**与订单规模/流动性无关的常数**。
- **实证（h_probe_costs.py）**：现网全部 14,311 笔 fill 的 `price/decision_price-1` =
  **+1.000bp（买）/ -1.000bp（卖），方差恒为 0** → 滑点是纯常数，且**冲击成本没有渗进成交价**
  （见 §1.3）。
- docstring 立论"日频低换手" **被证伪**：现网年化单边换手 **≈52×**（h_probe_costs2.py，
  总成交名义/avg NAV=99× over 242 日）。"低换手"假设不成立 → "1bp 足矣、冲击另层覆盖"的
  双重自我安慰同时破产（另层根本不覆盖，见 §1.3）。

### 1.3 冲击成本（Almgren-Chriss）：默认参数未估 + 单位错致实际为 0/静默旁路

- 模型 `execution_simulation/almgren_chriss_impact_model.py`：`temp=η·p^β·σ`、
  `perm=γ·p^0.5·σ`；`DEFAULT_PARAMS`（:176）= `ImpactParams(eta=0.1, beta=1.0, gamma=0.05,
  sigma=0.02)`，其注释自述 **"生产经 estimate_params 估出后注入"**。
- **零生产者校准（grep src）**：`estimate_params`（:333）在 src 内**无任何调用方** →
  引擎 `matching_engine.py:699-700 if self._impact_model is None:
  self._impact_model = AlmgrenChrissImpactModel()` → **永远吃 DEFAULT_PARAMS**，docstring
  承诺的"估出后注入"从未接线（**阈值未校准** P1）。
- **参与率算错（承 §H1-A）**：`matching_engine.py:711 model.quote(order_qty_股, vol_手)` →
  p=股/手=100×真实；`_validate_participation`（:184-185）p>1 抛错 → 被 `:712-714`
  except 吞掉"该标的按无冲击成交"（**静默降级**）。真实参与率>1% 即冲击归零。
- **实证净效应**：现网 p（引擎所见）中位 0.0013 → temp≈0.1×0.0013×0.02=2.6e-6≈**0.03bp**，
  远低于噪声；叠加 §1.2 fill 方差为 0 → **冲击成本对本 run 实际贡献≈0**，`impact_cost_enabled
  =True`（vectorized_engine.py:118）是**装饰性开关**。

### 1.4 其他"拍脑袋"成本常数猎捕结果

- `max_participation_rate=0.10`（vectorized_engine.py:117）：**无任何校准来源**，
  docs 命中仅为设计备忘录意图（`90_methodology_open_questions.md` 等），ruling_registry 无
  条目（grep governance=空）→ **阈值未校准**，且因单位错实为 **0.1%**（§H1-A）。
- `min_listing_age_days=120`（vectorized_engine.py:122）、`DEFAULT_RISK_FREE_RATE`、
  `DSR_OVERFITTING_FLOOR=0.5`/`DSR_SIGNIFICANCE_THRESHOLD=0.95`（metrics/decision_gate）
  —— 120 与 0.95 有业界惯例背书（次新/显著性通行阈值），风险冻结；0.10 与 1bp 无背书。
- `initial_capital=1,000,000`（vectorized_engine.py:107）——是**换手/佣金地板失真的放大器**：
  1M ÷ 满仓 3290 标的 → 单笔中位 ¥2280（§1.5）。资金规模未随成员数缩放，是"容量假设"缺失。

### 1.5 最低佣金地板支配真实成本（佣金"费率"名存实亡）

- 现网（h_probe_costs.py/costs2.py）：单笔中位名义 **¥2280**，98.9% 买单低于 5 元地板阈值
  （~¥52.4k）→ **1382 笔顶地板**。
- 实际综合费率：中位 **万21.5**、p90 **万72.6**、max **万350**，是名义万0.854 的 **25–410×**。
- **全 run 佣金 ¥95,529 = 总亏损 ¥184,653 的 51.7%**。→ 本 backtest 的"亏损"过半来自
  微额高频交易的地板佣金，而非 alpha 衰减或市场。

## 2 六向挖矿日志表

| 方向 | 矿点 | 锚点 | 实证 | 结论 |
|------|------|------|------|------|
| ①上游 | 滑点常数来源 | matching_logic.py:63 | fill 方差=0，恒 1bp | 未校准（P1） |
| ①上游 | 冲击参数估计器 | impact:176 注释 vs :333 estimate_params | src 零调用 | 默认参数入生产（P1） |
| ②下游 | 冲击进不进成交价 | matching_engine.py:711-721 | 成交 slip 无 p 依赖 | 冲击≈0/旁路（P1） |
| ③机制 | 参与率单位 | matching_engine.py:655 | 真实 p max=0.001 | 100× 钳位（P0，见 H1-A） |
| ④后端 | A股流动性分层 | max_participation=0.10 无量纲 | 无来源 | 阈值拍脑袋（P1） |
| ⑥数据 | 换手 vs 低换手假设 | fw run turnover 52× | 现网 99×/242d | 假设证伪（P1） |
| ③机制 | 地板佣金经济 | MIN_COMMISSION=5 :66 | 1382 顶地板，占亏 51.7% | 微额交易支配成本（P0 经济） |

## 3 业界与开源对照（四闸）

- **滑点非固定**：Zipline `SlippageModel`（VolumeSlippage：与 ADV 及订单占比相关）、
  qlib 支持交易成本随量。业界不用常数 1bp 配高换手。四闸：来源可溯（Zipline/qlib docs）✓
  ≥2✓A股适配✓可得✓ → **1bp 常数不满足"可回测保真"**。
- **Almgren-Chriss 参数须标定**：原作（Almgren & Chriss 1999；风险市场实践）η/γ 由分笔/分钟
  数据回归。本项目 `estimate_params` 已实现但无消费者（§1.3）。四闸：来源✓≥2✓A股可得✓
  （分钟表在库）→ **接线即得校准**。
- **参与率上限惯例**：合规/回测常设 ADV 的 5–15%（**以股计**）。本项目 0.10 意图合理，但
  单位错致 0.1%（§H1-A）。四闸全过 → 修单位即可对齐。
- **最低佣金建模**：聚宽/qlib 国产框架均 `max(5, notional×rate)`，本项目实现正确；业界通例是
  **在容量/资金规模报告中显式披露地板占比**，本项目未披露 → 报告欠账。

## 4 堵点与欠账清单（文件/函数/验收标准）

| ID | 级别 | 病灶类 | 堵点 | 可施工验收标准 |
|----|------|--------|------|----------------|
| H2-A | **P1** | 阈值未校准/零消费者 | `estimate_params`（impact:333）无生产者，引擎永远吃 DEFAULT_PARAMS | 在 framework 装载阶段按分钟/日频成交回归 η/γ/σ 注入 `AlmgrenChrissImpactModel(params=...)`；验收：产物披露实际 η/β/γ/σ + 与 0.1/1.0/0.05/0.02 默认有显著偏离记录 |
| H2-B | **P1** | 未校准/量纲前提伪 | `SLIPPAGE_BPS=1`（matching_logic.py:63）常数 + "低换手"假设被 52× 换手证伪 | 改为与参与率相关的滑点（或直接依赖修好的冲击层）；验收：滑点随订单 ADV 占比单调，且不再声称"冲击另层覆盖"（另层当前≈0） |
| H2-C | **P0** | 静默降级/单位 | `matching_engine.py:711` 冲击 p 用股/手，>1% 真量即 except 旁路 | 承 H1-A 单位修正后，报价入 [0,1]；旁路计数进 metrics 并 WARNING；验收：无"该标的按无冲击成交"静默路径（除真无 volume） |
| H2-D | **P0(经济)** | 报告欠账 | 地板佣金占亏 51.7% 未披露 | 产物新增 `cost_attribution`（佣金/滑点/冲击/印花税/过户 + 地板触发笔数与占比）；验收：现网重跑能一眼看出"过半亏损=地板佣金" |
| H2-E | **P1** | 容量假设缺 | initial_capital 不随成员数缩放 → 中位 ¥2280 碎股 | 设最小下单名义/合并碎股或资金按标的数下限；验收：中位单笔名义>可参与阈值，换手回落至合理区间 |
| H2-F | **P2** | 阈值未校准 | `max_participation_rate=0.10` 无来源登记 | 补 calibration 记录（数据源+样本+分位）入 governance 或改可配置；验收：有可追溯出处或标 TODO 阻断放行 |

## 5 子节点清单

- H2.a `estimate_params` 生产接线（分钟数据可得性核查，与数据车道共挖）。
- H2.b 滑点模型升级：常数→规模/流动性相关（与 H2-C 单位修正联动）。
- H2.c 成本归因产物 `cost_attribution`（与 §H4 现金、§H1 产物 schema 共挖）。
- H2.d 容量/资金规模-成员数缩放策略（换手治理入口，联动 §H3）。
- H2.e 参与率阈值登记或参数化（H2-F）。

## 6 封矿判定

**部分封矿**。成本常数已逐项验真/验伪（佣金法定✓、印花税/过户法定✓、最低佣金校准✓但经济扭曲、
滑点/参与率/冲击参数三项未校准✗），冲击成本"实际为 0 + 单位错致旁路"已现网实证（fill slip 方差=0、
真实 p≤0.001）。**未封子脉**：estimate_params 接线的分钟数据质量、滑点动态化的经验曲线、资金
规模-碎股合并策略。P0（单位/地板经济披露）与 P1（三项未校准）建议移交施工班；本节点与 §H1-A
同根（手/股），修一处两治。

## 修复优先级裁定建议

| 编号 | 一句话 | 级别 | 建议归属 |
|------|--------|------|----------|
| H2-C/H1-A | 冲击/参与率手-股单位错，>1% 真量静默旁路 | **P0** | 撮合层单点（与本表 H2-A 同修） |
| H2-D | 地板佣金占亏 51.7% 未进产物 | **P0(经济披露)** | 施工班（产物扩展） |
| H2-A | 冲击默认参数未估（estimate_params 零消费者） | **P1** | 施工班 |
| H2-B | 滑点 1bp 无来源 + 低换手假设证伪 | **P1** | 施工班 |
| H2-E | 1M/3290 碎股致成本失真（容量假设缺） | **P1** | 施工班 |
| H2-F | 参与率 0.10 无出处 | **P2** | 排期 |
