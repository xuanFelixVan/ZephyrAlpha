---
ttl: task_bound
doc_type: report
title: 深度审查报告——机构Regime评分器（D03）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：机构Regime评分器（D03）

- 状态: **已审**
- 级别: P1｜类型: 算法（CAPE/IV/两融三维合成）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/institutional_regime_scorer.py:134(score:169)`（583 行全文通读，NaN 行为已实机复现）
- 生产调用方: **查无**——全仓 grep `InstitutionalRegimeScorer` 仅命中模块自身与 `src/zephyr/regime/__init__.py` 再导出；[CONSUMERS] 栏"运行时装配批"无实际接线（checklist#8 孤儿候选，MATURITY=design 自洽）
- 测试文件: `tests/regime/test_institutional_regime_scorer.py`（权重/三维度分档/越界/缺失覆盖较全）

## 1 对象快照

- 审查范围：三维评分器全文件（权重归一/CAPE/IV/两融子映射/合成/态映射）。排除项：三源数据管道（index_valuation_daily/option_iv_surface_incremental/margin_trading_incremental，归 P2 数据域）；10 号 spec §4.7.6/§4.8.5/§4.11.10 原文未回读（材料包缺项）。
- 材料包缺项声明：三源数据画像未取；阈值（CAPE 95/80 分位、两融 2.5%/2.0%、VIX 35/40）的 A 股历史实证未复算——本报告审实现与自洽性，不裁定阈值优劣。
- 测试覆盖概况：分档/边界/缺失/越界/权重归一覆盖良好；**NaN 输入零覆盖**（有 test_iv_negative_vix 无 NaN 用例）。
- 变更热力：3 次，低返工。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **NaN 合成 VIX 静默判"平静"（已实机复现）**：`iv_synthetic_vix=NaN` 时 None 检查不拦，`nan<0` False 不拦，绝对值映射各级比较全 False 落 else → **score=20.0, available=True**——NaN 被当低 IV 计入合成且无 degraded 标记；同函数 percentile/margin 路有 [0,1] 域检查会拦 NaN（判 available=False），唯独 IV 绝对值路无域检查。已跑：NaN VIX + cape 0.85 + margin 0.022 → composite 54.25 neutral confidence=1.0，IV 维度假可用 | institutional_regime_scorer.py:360-318（_score_iv_absolute :300-318） | P1 | `InstitutionalRegimeScorer().score(iv_synthetic_vix=float('nan'))` → dimensions['iv'].score==20.0 且 available==True |
| A | F-A2 **margin_high 标志语义合流**：杠杆高（balance≥2.0%→70/90）、去杠杆极端（drop≥15%→65/85）、融资冰点（buy≤7%→65/85）三种相反现象都把维度分推高 → flags["margin_high"] 同名承载"泡沫杠杆"与"恐慌去杠杆"；泡沫/恐慌判别实际全押在 iv_high/cape_low 上。当前三子分取均值有阻尼，但 score≥70 边界上可由"balance 高+drop 大"组合触达 | :407-452,535,542-557 | P3 | 造 balance=0.021+drop=0.16+buy=0.06 → margin=(70+65+65)/3≈66.7<70 不触；balance=0.026+drop=0.26 → (90+85)/2=87.5 触发 margin_high——观察态映射结果是否合预期 |
| A | F-A3 合成分语义自洽性：score 高=极端（泡沫/恐慌同向），composit 混两相后由态映射二次判别——docstring 已明示"非方向性"，设计自洽；但单看 regime_score 数值无法区分泡沫与恐慌，下游只吃 regime_score 不吃 regime_state 会失义 | :31-33,564-571 | P3 | 读输出契约（state+score 双出）与消费方约定（当前无消费方，见 F-C1） |
| A | F-A4 权重负值/零和 fail-closed（ConfigError）+构造期归一——防御到位；confidence=0.2+0.8×n/3 全缺时特判 0.0——公式边界正确 | :152-163,220-222,203-212 | 已查无 | tests:69-91 |
| A | F-A5 CAPE 绝对值辅助修正是 max() 单向上抬（≥40→90、≥30→70），与分位分不冲突；value 无域检查但 NaN/负值经 max 比较为 False 自然忽略——行为安全 | :281-287 | 已查无 | cape_value=NaN 跑分不抛不抬 |
| B | F-B1 输入为纯数值注入（不直连库），断供语义=None→维度 degraded→权重归一继续合成——**fail-open 已声明且有 degraded/degraded_dimensions 字段**，比同域其他模块的静默降级规范；但"单维缺失即可翻转态"未设门槛：IV 缺失时 high-cape+high-margin 日以 confidence 0.73 判 extreme_bubble | :139-143,201-215 | P2 | score(cape 0.96, margin 0.026)（IV 缺）→ extreme_bubble, confidence 0.73, degraded=True |
| C | F-C1 **孤儿模块（checklist#8）**：全仓无生产调用方，仅 __init__ 再导出；空转期间任何阈值/行为缺陷都不会被发现——与 wyckoff 引擎结构性死亡案例同族。爆炸半径=0（未接线），接线日=风险激活日 | 模块头 [CONSUMERS] vs grep 结果 | P2 | `grep -rn "InstitutionalRegimeScorer" src/ scripts/ --include="*.py"` 仅 2 文件 |
| D | F-D1 IV 阈值口径与 D08 合成 VIX 的量纲衔接未在本模块核（35/40 假定输入即合成 VIX 指数点位）；S2 trigger 的 vix 维度（D01 :324）是 0-100 评分非 VIX 点位，两处"vix"键语义不同——跨模块同名异义再次出现（同 rpt_d02 F-D1 族） | :96-99 ↔ regime_detector.py:320-324 | P3 | 对照 D08 输出量纲（rpt_d08 跟进） |
| E | F-E1 静默失败面：F-A1（NaN→20 分）是唯一非 None 的静默错值通道；其余越界/缺失均有 degraded 留痕。无日志 except、无时间戳（纯函数无副作用）——重放幂等成立 | :300-318 | 见 F-A1 | — |
| E | F-E2 假阳性：全缺失→NEUTRAL+confidence 0（:203-212）合规；部分缺失降 confidence 但态照判（F-B1）——下游若只看 state 不看 confidence/degraded 即带病传播 | :226-232 | P2 | 同 F-B1 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | CAPE 分位作长期估值锚 | **对等已有**——CAPE 分位/前瞻收益关系为学界业界标准用法；文献同时警告"CAPE 是差的市场择时工具"，本项目将其压到 0.35 权重并只作极端分档（非择时）与文献口径一致 | [IFA: CAPE Fear — Valuation Ratios and Market Timing](https://www.ifa.com/articles/cape_fear_valuation_ratios_market_timing)（IFA，1926-2024 实证）；[Shiller 官方数据集](http://www.econ.yale.edu/~shiller/data.htm)（Yale） |
| 2 | 两融/margin debt 作杠杆情绪指标 | **对等已有**——美股 FINRA margin debt 文献共识"水平随市值水涨船高，变化率（降幅/骤降）才是信号"，本项目三子分含 drop_from_peak/buy_ratio 变化率维度，口径符合 | [FINRA Margin Statistics](https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics)（FINRA）；[Advisor Perspectives: Margin Debt 更新](https://www.advisorperspectives.com/dshort/updates/2026/08/20/margin-debt-finra-july-2026)（2026） |
| 3 | 多指标合成情绪/极端指数（VIX+估值+杠杆） | **对等已有**——CNN Fear & Greed 等合成指数同构（VIX/动量/广度 0-100 分档合成）；"用于风险管理/仓位而非精确择时"的定位与本项目 regime 分档一致 | [CNN Fear & Greed Index](https://edition.cnn.com/markets/fear-and-greed)（CNN/Money，持续更新） |

## 4 缺陷清单（按严重级）

- **F-A1（P1）NaN 合成 VIX 判 20 分假可用**：现状=IV 绝对值路无域检查，NaN 落最低档且 available=True → 证据=实机复现（本报告 §2 F-A1）→ 影响=IV 管道出 NaN 的恐慌日被计"平静"，经 0.35 权重拉低合成分、态映射可能由 panic 翻 neutral；爆炸半径=未来接线后的机构分/态消费方 → 建议修法=_score_iv 入口对 synthetic_vix 加 isfinite 检查（NaN→available=False 走 degraded），补 NaN 单测 → 验证法=本报告 §2 F-A1 一行复现命令。
- **F-C1（P2）孤儿模块**：建议接线前冻结或在注册表登记"design 未接线"状态，防止误以为在产（对齐 checklist#8 处置）→ 验证法=grep 复核。
- **F-B1/E2（P2）降级降置信不降判决**：建议消费契约强制 state+confidence+degraded 三元组同读（接线时落 capability 卡）→ 验证法=IV 缺失用例。
- **F-A2/D1/A3（P3）**：标志合流、跨模块 vix 同名异义、score 单标量失义——常规队列。

## 5 挂起疑问

1. 阈值的 A 股历史实证（两融 2.5% 阈在 2015 峰值约 4.7% 流通市值口径下是否过松/口径是占比流通市值还是自由流通市值）需数据画像裁定——材料包缺项，本审查未判。
2. "运行时装配批"接线计划在哪个批次——决定 F-C1 从孤儿转产的时点与回归测试义务。

## 6 完备性自评

- 六轴全查：A（三子映射逐档+NaN/越界/权重边界；NaN 实机复现）、B（纯注入无直连库，断供=degraded 声明式）、C（消费方查无=孤儿发现）、D（跨模块 vix 同名异义+与 D08 量纲衔接挂 D08）、E（静默失败 F-A1、假阳性 E2、幂等查无、时序不适用-纯函数）、F（3 条带来源）。
- 长尾清单：①10 号 spec 三节原文未回读，阈值的 spec↔代码一致性未逐条核；②三源管道数据质量归 P2 域；③RegimeState 词表与 D01/D02 词表的三方关系未做全词表对账（建议收口时并案）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 NaN VIX 静默判平静: 确认→治本（域检查+degraded 留痕+中性 50 分）。复检 78/78。孤儿+MATURITY 虚标: 挂起。
- 修复提交: q-0021（D03/D04 NaN 防御）。
