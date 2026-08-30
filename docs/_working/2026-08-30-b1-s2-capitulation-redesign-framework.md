---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=design_memo_working · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-30 · topic=regime_s2_capitulation_redesign_framework · scope=07_trading_decision_architecture · completes_when=S2 残余四件（2015/2020 事件标注裁定、fund 跨工程项、ERP 管道、dump 阈值同源化）闭环后归档。

# B1：S2 算法重设计框架——capitulation 三过滤器校准（启动阶段产出）

> **上游真源**：[14_regime_s2_diagnosis](../02_enterprise_architecture/07_trading_decision_architecture/design_memos/14_regime_s2_diagnosis.md)（v0.5.3，诊断+治本详设单一真源）、[S2 校准专项收尾报告](reports/2026-08-30-s2-closure-report.md)（2026-08-30）、S2 walk-forward 验证报告（2026-08-29，已归档）。
> **本文定位**：B 类任务的启动阶段框架产出——缺陷分析 + 三过滤器校准目标与候选方法 + 数据需求 + 分阶段路径。**重要前提说明**：截至本报告日（2026-08-30），capitulation 三过滤器校准已由 S2 校准专项**完成落产**（Owner 2026-08-29 裁定选项 1，commit c5c23036），本文按"框架 + 已落地基线 + 残余路径"三层结构如实记录，不重复已闭环工作。

---

## 1. 背景与当前基线（2026-08-30 实证）

### 1.1 缺陷缘起（14 号文诊断结论）

S2（CRISIS→RECOVERY）评分算法时点错配：capitulation 被实现为"当日正在暴跌"的瞬时信号（`z>1 ∧ pct<-1.5%` 两维分档），而设计意图（10 号文 §4.12.1）是"近期**曾**出现投降抛售"的过程信号——复苏事件日是企稳时点，当日不会暴跌，导致三历史事件 ±10 窗口内 trigger 永不触发（B4 S2 0/3）。叠加三过滤器联玩过严（A 股暴跌日光脚大阴线致下影线比≈0）与衰减权重过薄（wavg 下单日 90 分仅贡献 ~8 分）。

### 1.2 已落地基线（校准专项终态）

| 层 | 终选 | 实证位置 |
|---|---|---|
| 基础分 base_mode | `precrisis_z`（危机前基准 z：`volume.shift(20).rolling(40)` 均值/方差，抗危机簇内滚窗失真） | overlay_features.py:387-393 |
| 过滤器①量能 vol_filter_mode | `pct250`（250 日滚动量能分位 >0.8） | overlay_features.py:400-401 |
| 过滤器②实体 | 不变：`|close-open| > 0.4×ATR(14)`（真实体，实证唯一健康维度） | overlay_features.py:406-408 |
| 过滤器③形态 wick_mode | `close_pos`（A 股本土化：`(close-low)/(high-low)<0.15` 收盘贴底光脚阴线，替代与 A 股暴跌形态根本冲突的下影线>0.5） | overlay_features.py:415-417 |
| 聚合 agg_mode | `decayed_max`（衰减峰值 `max(daily_i × e^(-age·0.693/halflife))`，非归一化） | overlay_features.py:305-308 |
| 参数 | halflife=10 / lookback=20 / trigger≥60 未动 | overlay_signals_builder.py:337-341 接线 |

**验收六层**（walk-forward 12 组预注册组合扫描，IS 2010-2018 / OOS 2019-2026，三事件全程未参与选型）：WFE=3.44 ✅ / 负样本 fp@≥60=0.8% ✅ / 参数平移 ±10% 命中率零变化 ✅ / **MC 置换 p=0.87 ❌（诚实标注，DSR N=17 备案）** / MinTRL 低置信标注 ✅ / 预注册纪律 ✅。B4 重跑全 PASS（S1 3/3 + S2 1/1：EVT-2024 confirm Δ=+3d），EVT-2024 design_match 翻 true；EVT-2015/2020 维持 false（事件日滞后超 halflife=10 衰减物理极限 + fund=0 跨工程项，非算法缺陷）。

### 1.3 残余缺口（重设计未闭合项）

1. **EVT-2015/2020 design_match=false 残余**：根因已从"算法错配"收窄为"事件标注时点 vs 信号物理可达性"（capitulation 主峰早于事件日 12-14+ 交易日，超 halflife=10 衰减极限）→ 14 号文开放问题 3，需 Owner/专项裁定 expected_stage/事件日标注。
2. **fund=0**（2015 confirm 必要条件最后缺口）→ P1-E4 跨工程项（融资余额+超大单升级）。
3. **MC p=0.87 低置信**：终选组合置换检验未过预注册门槛，低置信接线已注记。
4. **three_yang v2_index OOS 0%**（IS 12.9%）：维持 strong_confirm 辅助维定位。
5. **S2 trigger 阶段三事件均未触发**（2024 走 confirm 路径命中）。
6. **dump_s2_scores.py 阈值陈旧**（vix 40/无析取/three_yang≥1）与 regime_detector 现行配置（vix 30/keys_or_gte/≥2）不同源。
7. **可选第 5/6 维未启用**：期权 put/call>1.4 + 新低占比>90%（Step 0 ④ 勘探无数据管道，默认关）。

---

## 2. 当前算法缺陷分析（框架层归纳）

| # | 缺陷 | 根因 | 处置状态 |
|---|---|---|---|
| D1 | 瞬时信号 vs 过程语义 | 当日值无 rolling/衰减 | ✅ 已治本（decayed_max 过程化） |
| D2 | 基础分 z 基准簇内失真 | 20 日滚窗均量在危机簇内被抬高，z 结构性压低 | ✅ 已治本（precrisis_z 危机前基准） |
| D3 | 量能过滤器用 20 日均量×2.0 | 同上簇内失真 | ✅ 已治本（pct250 长期分位） |
| D4 | 下影线>0.5 与 A 股暴跌形态冲突 | 暴跌日 close≈low，wick_ratio≈0，交集过严恒 0 | ✅ 已治本（close_pos 收盘贴底替代） |
| D5 | wavg 归一化衰减贡献过薄 | 单日 90 分仅 ~8 分，trigger≥60 需多日簇集，实操不可达 | ✅ 已治本（decayed_max 单日即 90） |
| D6 | 状态粘滞风险（rolling max 方案） | 单日高分持续 lookback 日 | ✅ 已规避（衰减峰值自然消退） |
| D7 | 残余：信号物理可达性 vs 事件标注时点 | halflife=10 衰减 12-14 天后仅剩 ~30%，早于事件日 3 周的簇不可达 | ⚠️ 开放（开放问题 3，标注裁定而非调参） |
| D8 | 残余：可选 5/6 维数据缺席 | 期权 put/call、创新低占比无管道 | ⚠️ 开放（默认关，非阻断） |

**方法论纪律（不可妥协）**：禁止"调参直到 3/3 命中"的循环验证；超参扫描须在独立于三事件的样本（walk-forward 全历史）上做；参数变更须预注册 + DSR 试验次数备案（当前 N=17）。

## 3. 三过滤器校准目标与候选方法（专业机构实践维度）

### 3.1 过滤器①：量能放大（成交量维度）

- **校准目标**：区分"真投降式放量"与"普通下跌放量"，且在危机簇内不失准。
- **候选族**（专业机构实践）：①固定倍数法（量 > 2.0×20 日均量——ChartMath/JournalPlus/Pomegra 2026 共识区间 2-3×，取研究下限留 selective 余地）；②长期分位法（250 日量能分位 >0.8，与 synthetic_vix_pct 同族抗簇内失真）；③平静窗基准法（危机前 shift(20).rolling(40) 均量×1.5）。
- **终选与理由**：`pct250`——簇内危机期固定倍数法基准被持续高量抬高（2015 股灾 max z=1.79 结构性不可达），长期分位对"相对自身历史的异常"最稳健。
- **敏感性**：实体/量能阈值建议配套 ATR 倍数敏感性扫描（0.5×/1.0×/1.5×/2.0×）——phuazz 2026-08 实证 ATR 倍数过紧具破坏性。

### 3.2 过滤器②：实体力度（波动率维度）

- **校准目标**：确认"恐慌级价格宣泄"而非阴跌——单日真实体相对近期波动率显著放大。
- **候选**：`|close-open| > k×ATR(14)`，k=0.4（真实体口径，项目 K 线有 open 字段，弃 close-to-close 近似）。
- **状态**：实证唯一健康维度，校准中保持不变（对照锚）。
- **注意**：ATR 为模块级自实现（`_atr`，Wilder 平滑，overlay_features.py:197-215），项目无现成。

### 3.3 过滤器③：形态确认（价格形态/趋势维度）

- **校准目标**：捕获"卖盘被吸收"或"恐慌尾盘无承接"的底部形态证据。
- **候选族**：①下影线占比 >0.5（Wyckoff/JournalPlus 经典，但与 A 股暴跌光脚大阴线根本冲突——实证恒 0）；②删除形态维（见底确认语义移交 spring/flush 域）；③**收盘位置 <0.15（A 股本土化 close_pos）**——`(close-low)/(high-low)<0.15` 收盘贴底 = 恐慌尾盘实体宣泄，与 A 股 T+1/涨跌停制度下的暴跌形态一致。
- **终选与理由**：`close_pos`——D4 缺陷的直接治本，walk-forward 选型胜出。

### 3.4 聚合层（过程化语义承载）

- **校准目标**：把"窗口外/早期的 capitulation 簇"带至事件日，且不粘滞、不过薄。
- **候选族**：①wavg 归一化衰减加权（过薄，D5）；②**decayed_max 衰减峰值**（单日 90 当日即 90，逐日 ×0.933，3 周后 ~31.9——终选）；③cluster_count 簇计数（近 20 日 daily≥70 簇数映射 0/40/60/80，C3 对照组）。
- **数值边界**：halflife=10/lookback=20 为 trigger 档单档运行；confirm 档（30/40）占位未启用。

## 4. 数据需求

| 数据 | 用途 | 状态（2026-08-30 实证） |
|---|---|---|
| 指数 OHLCV（含 open）日频 | 三过滤器+基础分全部输入 | ✅ production（overlay_signals_builder 接线位） |
| vol_z / pct_change | 基础分降级链/legacy 路径 | ✅ production |
| 涨跌家数（adv/dec） | breadth_thrust 析取通路（confirm V 反转） | ✅ production（E9d 已落码） |
| CAPE 5 年分位（index_valuation_daily） | valuation 路 A（非本过滤器但同属 S2 治本） | ✅ 已接线（2010-2026 连续） |
| ERP/ERP 分位 | valuation 加分项 | ❌ 全表 NULL（known_data_gaps 已登记 accepted，二期管道） |
| 期权 put/call、52 周新低占比 | 可选第 5/6 维 | ❌ 无管道（默认关，Step 0 ④ 勘探结论） |
| 融资余额/超大单净流入 | fund 维度升级（confirm≥50 依赖） | ❌ P1-E4 跨工程项 |

## 5. 分阶段实施路径（含已完成段回执）

| 阶段 | 内容 | 状态 |
|---|---|---|
| Phase 0 勘探门禁 | daily_valuation 字段 / wyckoff Spring 接口 / 涨跌家数 / 期权 put-call 四项勘探 | ✅ 已完成（14 号文 §4.0 Step 0） |
| Phase 1 TDD + 参数化候选族 | 三过滤器+聚合四层候选落码（≤12 组合），默认值=legacy 零行为变更 | ✅ 已完成 |
| Phase 2 walk-forward 预注册选型 | 12 组扫描、六层验收、Owner 裁定选项 1 落产（commit c5c23036） | ✅ 已完成（MC p=0.87 低置信注记） |
| Phase 3 生产接线 + B4 重验 | builder 接线终选组合；B4 4/4 PASS；EVT-2024 design_match 翻 true | ✅ 已完成（2026-08-30） |
| **Phase 4 残余闭环（本框架后续重点）** | ① 2015/2020 事件标注裁定（14 号文开放问题 3，Owner 决策）；② fund 升级（P1-E4）；③ ERP 管道（二期）；④ dump_s2_scores.py 阈值同源化；⑤ confirm 档 halflife=30/lookback=40 占位参数是否启用评估 | ⚠️ 未启动——建议立项"S2 残余闭环批"，均非调参性质 |

**启动建议**：Phase 4 的 ①④ 为纯治理/工具同源化（量小），②③ 为数据管道工程（跨工程项协调），⑤ 需在独立样本上评估。建议按 ①④→⑤→②③ 顺序排期；全程遵守 §2 方法论纪律，任何阈值变动走预注册。
