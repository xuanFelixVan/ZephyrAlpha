---
ttl: task_bound
completes_when: 模块晋升 docs/03_modules（H-01 解冻）或工单废弃
---

# MOD-AUTO-L4-001（暂编号）generate_skeleton_health 蓝图

## 定位

骨架 v1.1 §1 工段⑨：月度只读盘点→"血肉级（自动执行）/骨架级（Owner 拍板）"两分建议书。骨锁肉动制度的例行执行器。

## ALGO_FLOW

- I1: config/trading_decision_map.yaml（节点/边/.tmp 卫生）
- I2: docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md（电态摘要+漂移比对）
- I3: config/resource_profile_registry.yaml（状态直方图）
- I4: .runtime/logs/resource_samples/*.jsonl（采样覆盖）
- I5: data/runtime/strategy_decay_ledger.json（生命周期直方图+观察名单）
- A: 五面检查→两分建议生成
- O1: docs/_working/automation/campaign/health/skeleton-health-YYYYMM.md

## 不变量

全只读；单面缺失降级"缺证"；建议两分=骨锁肉动。
