---
blueprint_id: MOD-SIG-148
module_name: pattern_evidence_certifier
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-09-15
last_updated: 2026-09-15
owner: ZephyrAlpha-Owner
---

# MOD-SIG-148 pattern_evidence_certifier 蓝图

> 设计真源：反过拟合自动认证方案 v1.0（docs/_working/archive/2026-09/pattern_line/
> 2026-09-15-pattern-certification-plan.md，c0c478a2a6）。Owner 令"读表人全自动"。

## 0. 文件清单

| 文件 | 说明 |
|------|------|
| src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py | 四闸统计核+认定状态机+CH 读写+CLI |
| tests/signal_ashare/strategy_signal/test_pattern_evidence_certifier.py | 教科书向量单测 |

## 0.1 定位

四闸机器化（把读表人从回路里删掉）：闸A BH-FDR（q<0.05）/闸B n_eff=n/fwd_window
（≥30）/闸C 分 regime 对照基线（加权 edge>0 且正 edge 单切片占比≤0.9）/
闸D 贝叶斯收缩 shrunk_rate（k=100）。状态机 certified/probation/failed
（retired=消费侧连续窗计数，不在本模块）。

## 1. 阈值（预注册，改动=裁定留痕）

q=0.05 ｜ n_eff_min=30 ｜ k=100 ｜ conc_max=0.9 ｜ z=1.96（Wilson 单源复用
provider._wilson_lower_bound）。

## 2. 契约

- `certify_family(pooled_rows, regime_rows_by_pattern, baseline_pooled,
  baseline_by_regime, *, fwd_window, timeframe, direction, **thresholds)`
  → list[CertificationRecord]（Fail-Closed：无基线/无数据/low_sample 不进认定）
- `run_certify(client=None, *, timeframe, direction, fwd_window)` → 摘要 dict
  （读家族行→四闸→写 c1_market.market_pattern_certification）
- CLI：`python -m ...pattern_evidence_certifier --certify --timeframe day
  --direction 向上 --fwd-window 10`（任务块经 pattern_event_job 子进程调用）

## 3. 不变式

1. 纯函数统计核同输入必同输出；2. 认定只读统计表（运动员不兼任裁判）；
3. 阈值预注册禁静默调；4. Fail-Closed（判不了=failed 不猜）；5. 认证表只追加
（ReplacingMergeTree 幂等重放）。

## 4. 边界（不做）

不做权重接油门裁定；不做 PBO/CSCV/Storey π0（二期可选）；不做向下切片扩向（另批）；
不做 retired 状态（消费侧 131/adjuster 计数连续窗，本模块只产三态）。
