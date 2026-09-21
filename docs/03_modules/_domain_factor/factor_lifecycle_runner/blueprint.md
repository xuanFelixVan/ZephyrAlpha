---
blueprint_id: MOD-L02-LIFECYCLE
module_name: factor_lifecycle_runner
domain: D_FACTOR
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

# MOD-L02-LIFECYCLE factor_lifecycle_runner 蓝图

> 设计真源：生命周期协议 v2.0 三域落地（docs/_working/archive/2026-09/pattern_line/
> lifecycle-rollout-three-domains.md）。补齐 factor_decay_monitor_weekly 任务块的
> runner 缺口（该块 disabled 原因自述施工后启用）。

## 0. 定位
遍历 factor_registry→judge_factor 三级判定（域内预注册）∧BHY 族校正→
联合认证（certified/probation/failed）→连周计数→retired/复活（149 台账语义）
→decay_state 行级回写（零格式漂移）。单写手：retired/resurrected 覆盖当日三态。

## 1. 阈值（预注册：90 号 §2 + 本蓝图）
BHY q=0.10（任意依赖稳健）｜淘汰连 RETIRED_AFTER_WEEKLY=20 周扫→retired｜
复活=ic 回合格以上且族拒绝｜无 lookback 因子封顶 probation（Fail-Closed）。

## 2. 边界
不做 IC 回测管线（ic/lookback 由域内既有评估供给，缺口另批）；
不接油门（因子权重消费归因子域裁定）。
