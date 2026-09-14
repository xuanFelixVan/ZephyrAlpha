---
blueprint_id: MOD-SIG-150
module_name: strategy_decay_certifier
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

# MOD-SIG-150 strategy_decay_certifier 蓝图

> 设计真源：生命周期协议 v2.0 三域落地。策略域**衰减侧**（晋升侧 E0-E9 归属域管线不动）。

## 0. 定位
读 c1_backtest.backtest_strategy_screen 每策略最新行（FINAL）→ deflated_sharpe
三态判定 → 连周计数 → retired/复活建议台账（JSON）→ 策略域会话消费。
**退役=建议制**：状态翻转归策略域管线（边界）。

## 1. 阈值（预注册）
DS≥0.5 且 oos_tested→certified｜0≤DS<0.5→probation｜DS<0→failed｜
FAILED_WINDOWS=8 周扫 failed→retired 建议｜retired 后 DS 回升≥0.5→resurrected。

## 2. 边界
不翻转 strategy_registry 状态；不做晋升侧（工厂管线所有）；
复活闸不做序贯收紧（策略样本粒度粗，M=8 已保守，收紧待数据积累后裁定）。
