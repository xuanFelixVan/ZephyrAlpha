---
module_id: KE-579
status: active
title: D-DEPS：依赖与接口一致性
category: documentation
ttl: permanent
---

# D-DEPS：依赖与接口一致性

D-DEPS：依赖与接口一致性

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| 各层 YAML 接口声明与跨层契约一致 | ✅ | CTR-001~CTR-006 在 layers/*.yaml 和 cross_layer_contracts.yaml 中一致 |
| 模块依赖方向符合分层架构 | ✅ | 依赖图无环（2026-05-06 确认，101 节点扫描） |
| 依赖置信度分级 | ✅ | _schema.yaml v2.1 已提取 L1/L2/L3 分级 |

**验证详情**：
- `cross_layer_contracts.yaml` 中 CTR-001~CTR-006 与 `layers/l00_data_source.yaml`、`layers/l02_alpha_factor.yaml`、`layers/l06_trade_execution.yaml` 中的接口声明一致。
- `architecture_endgame_locked.md` §一 已确认：`detect_depends_on_cycles.py` exit 0，depends_on 有向图无环。
- 分层架构方向：L00 → L02 → L03 → L04 → L05 → L06 → L07，无逆向依赖。

---
