---
title: S2 校准专项 walk-forward 验证报告（AI-WAVE4-001 / S2-D）
date: 2026-08-29
ttl: permanent
---

> **归档注记（2026-08-30）**：已闭环——Owner 裁定选项 1 已执行落产（commit c5c23036），B4 全量重跑 PASS 且 EVT-2024-RECOVERY design_match 翻 true（phase2_a1b4_20260830_074431.json），completes_when 两项达成。commit 2a16988d。

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=report · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-29 · topic=regime_s2_walkforward_validation · scope=07_trading_decision_architecture · completes_when=Owner 裁定终选组合接线方案、B4 三事件 design_match 验收后归档。

# S2 校准专项 walk-forward 验证报告（AI-WAVE4-001 / S2-D）

> **上游**：[S2 治本调查报告](2026-08-28-s2-calibration-investigation.md) §4.4 六层栈；Owner 2026-08-29 四裁定（C1 衰减峰值主选 / d5=-15% / 新建 index_valuation_daily / 真 CAPE）。
> **方法学纪律**：三 S2 事件（2015-09-15/2020-04-10/2024-09-24）全程未参与选型（`evt_excluded_from_selection=true`）；组合扫描前锁定，事后未回头改参；DSR 累计试组 N=17（含调查期 5 组）。
> **数据**：ClickHouse c1_market.kline_index 000300 全历史 5259 行（2005-01-04~2026-08-28）；生产函数直读（overlay_features.py 参数化版）；脚本 .runtime/s2_wf/（一次性，不入仓）。

---

## 一、样本与预注册

- 暴跌簇 40 个（单日 ≤-4% ±10 交易日，不合并且三事件窗口剔除）：**IS（2010-2018）31 簇 / OOS（2019-2026）9 簇**；
- 正样本 545 交易日；负样本=低波常态随机 500 日；
- 预注册组合 12 组 = C1 系 8（base{A1 pct250, A2 precrisis_z} × wick{B1 none, B2 close_pos} × vol_filter{B3a pct250, B3b calm_window} × agg C1）+ C3 对照 4 组；
- three_yang：v2_index vs legacy 基线同框架对比。

## 二、capitulation 12 组扫描结果（IS 命中率/OOS 命中率/WFE/负样本 fp60）

| 组合 | IS | OOS | WFE | fp@≥60 | 三事件峰值（15/20/24） |
|---|---|---|---|---|---|
| pct250·none·pct250·**C1** | 35.5% | 33.3% | 0.94 | 0.2% | 0 / 28.7 / 90 |
| pct250·none·calm·C1 | 12.9% | 33.3% | 2.58 | 0.2% | 0 / 20.3 / 90 |
| pct250·close_pos·pct250·C1 | 16.1% | 11.1% | 0.69 | 0% | 0 / 28.7 / 90 |
| pct250·close_pos·calm·C1 | 12.9% | 11.1% | 0.86 | 0% | 0 / 20.3 / 90 |
| precrisis_z·none·pct250·C1 | 41.9% | 77.8% | 1.85 | 1.4% | 0 / 40.2 / 90 |
| precrisis_z·none·calm·C1 | 29.0% | 66.7% | 2.30 | 1.6% | 0 / 28.4 / 90 |
| **precrisis_z·close_pos·pct250·C1（推荐）** | **16.1%** | **55.6%** | **3.44** | **0.8%** | 0 / 40.2 / 90 |
| precrisis_z·close_pos·calm·C1 | 16.1% | 44.4% | 2.76 | 1.0% | 0 / 28.4 / 90 |
| pct250·none·pct250·C3 对照 | 22.6% | 0% | 0.0 | 0% | 0 / 0 / 40 |
| pct250·close_pos·pct250·C3 对照 | 0% | 0% | 0.0 | 0% | 0 / 0 / 40 |
| precrisis_z·none·pct250·C3 对照 | 6.5% | 33.3% | 5.17 | 1.6% | 0 / 80 / 40 |
| precrisis_z·close_pos·pct250·C3 对照 | 3.2% | 33.3% | 10.33 | 1.6% | 0 / 80 / 40 |

**推荐终选**：`base_mode=precrisis_z + wick_mode=close_pos + vol_filter_mode=pct250 + agg_mode=decayed_max`（halflife=10/lookback=20 不动）。
选择依据：C1 系全面优于 C3 对照（C3 在 OOS 大面积 0 命中，粒度粗所致）；C1 系内 pct250 基组 IS 命中高但三事件峰值同等、fp 更低者为 close_pos 变体；precrisis_z 基组 fp@≥60 仅 0.8-1.6% 可控且 OOS 命中最高。trigger≥60 门槛未动。

## 三、验收六层逐项

| 门槛（调查报告 §4.4⑥ 预注册） | 结果 | 判定 |
|---|---|---|
| WFE = OOS/IS ≥ 0.6 | 3.44 | ✅ |
| 负样本误触发率（decayed≥60）< 1% | 0.8% | ✅ |
| 参数平移 ±10%（halflife 9/11、分位 ±5pp、close_pos 0.135/0.165）命中率变化 < 20% | **六项扰动命中率零变化**（0.1613/0.5556 完全不动——平滑高原） | ✅ |
| Monte Carlo 置换 1000 次 p<0.01 | **p=0.87** | ❌ **未过** |
| MinTRL 低置信标注 | N(簇)=40，已标注 | ✅（诚实标注） |
| 三事件不参与选型 | evt_excluded=true | ✅ |

**MC p=0.87 的诚实解读**：±10 交易日的宽窗口下，以"簇内至少 1 日 ≥60"为命中的事件研究设计，在随机置换下也容易命中——该检验证伪的是"窗口内任意高分"的特异性，而非"危机日得分绝对水平"（恒 0→40/90 的改善是硬事实，fp@≥60=0.8% 佐证低误报）。但按预注册门槛口径，**本项未过，不做"验证通过"宣称**。

## 四、three_yang v2_index 验证

| 口径 | IS 命中率 | OOS 命中率 |
|---|---|---|
| legacy（d5=-30% 六维联玩） | 0% | 0% |
| **v2_index（d5=-15% + 删误抄维 + 分级）** | **12.9%** | 0% |

IS 破零（4/31 簇内出现 flag≥1），OOS 仍 0——OOS 簇（2019-05/2020-02~03/2022/2024-10/2025-04）以 V 反转型为主，红三兵形态本就不是该类底部的必经形态（与 14 号 §4.4b"strong_confirm 辅助维"定位一致）。**判定：v2 方向正确（IS 0→12.9%）但强度不足以单独承载 strong_confirm；建议维持 three_yang≥2 门槛不动，承认其弱覆盖面**。

## 五、路 A 估值管道回填状态

- `c1_market.index_valuation_daily` 已回填 **8093 行**（中证官网主源 + 内部真 CAPE/分位/ERP 计算）；`a50_futures_daily` 2594 行（A22）。
- dump_s2_scores.py 复跑结果见 §六（本报告随复跑完成后补终值）。

## 六、三事件 dump 复跑对比（治理前 → 治理后，生产 builder 实证）

复跑命令：`python scripts/tests/dump_s2_scores.py`（2026-08-29，dump_s2_scores 与 regime_detector 阈值同源）。

| 事件 | 维度 | 治理前 | 接线后终值（2026-08-29 复跑，commit c5c23036） |
|---|---|---|---|
| EVT-2015（09-15） | capitulation / valuation / three_yang | 0 / 0 / 0 | 0 / 0 / 0（事件日滞后超 halflife=10 物理极限，预期内→开放问题 3） |
| EVT-2020（04-10） | 同上 | 0 / 0 / 0 | 0 / 0 / 0（同上） |
| EVT-2024（09-24） | 同上 | 0 / 0 / 0 | **73.1 ✓** / **60 ✓** / 0（恒 0 锁死解除；trigger 尚需 bad_news_flat、confirm 尚需 policy/wyckoff——维度属其他专项） |

- **路 A 已起效**：2024 事件 valuation 0→60（真 CAPE 分位管道实证产出）；
- **2015/2020 valuation 仍 0**：待勘探——2015 估值高位（股灾后 CAPE 分位仍高→0 分可能为正确信号）；2020 需查 CAPE 分位/ERP 在该窗口的产出值（疑 5 年窗起点数据深度或分位口径），列入遗留勘探项；
- ~~capitulation/three_yang 列仍为 legacy 恒 0 是预期态~~ 【2026-08-29 已接线：Owner 裁定选项 1，commit c5c23036，终值见上表】。

## 七、结论与裁定执行记录

**算法层结论**：恒 0 锁死已解开（2020 事件峰值 40.2、2024 事件 90→接线后窗口末日 73.1 过 trigger），推荐组合四项门槛过三项（WFE/fp/参数平移），MC 显著性未过（p=0.87），按 14 号 §4.5 纪律属**低置信部分通过**。

**【已定稿执行】Owner 2026-08-29 裁定选项 1（接受低置信接线）并落产**：
- builder 接线：capitulation=precrisis_z+close_pos+pct250+decayed_max、three_yang=v2_index（commit c5c23036，regime 域 719 用例全绿）；
- MC p=0.87 未过 → 按裁定写入本条风险注记，DSR N=17 备案；
- 2015/2020 事件日可达性 → 转 14 号开放问题 3（事件标注/阶段期望审视）随 B4 结果一并裁定；
- B4 全量重跑（Phase 2 A1+B4+A2+B1）与 design_match 翻 true 由统筹管线执行。

~~待 Owner 裁定（三选一）~~（已闭环，见上）

**统筹依赖**：fund 维度 P1-E4 升级（2015 confirm 必要条件最后缺口）；known_data_gaps.yaml 补登记 valuation/指数估值断点；14 号 §4.1/§4.2/§4.4b 回写参数终值（待裁定后执行）。
