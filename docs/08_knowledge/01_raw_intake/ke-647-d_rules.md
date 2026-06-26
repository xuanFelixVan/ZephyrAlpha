---
module_id: KE-582
status: active
title: D-RULES：架构原则与不变量可验证性
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# D-RULES：架构原则与不变量可验证性

D-RULES：架构原则与不变量可验证性

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| 架构原则可验证 | ✅ | 4 条安全红线每条都有 gate_ref 映射到具体 CI/工件 |
| 不变量可由 arch_guard 检查 | ✅ | 16/16 不变量都有对应 fitness function |

**验证详情**：

| 不变量 | fitness function | 状态 | 说明 |
|--------|-----------------|:----:|------|
| INV-001 Kill Switch 延迟 | FF-001 check_kill_switch_latency.py | active | 声明级检查（CAP-009），实测钩子预留 |
| INV-002 单一持仓限制 | FF-002 check_position_limit.py | active | 读取 config/risk_params.yaml |
| INV-003 日损失限额 | FF-003 check_daily_loss_limit.py | active | 读取 config/risk_params.yaml |
| INV-004 PIT 铁律 | FF-004 check_pit_compliance.py | active | 静态扫描 L02 look-ahead |
| INV-005 Broker ACL 边界 | FF-005 check_acl_boundary.py | active | 源码级扫描，实现完整 |
| INV-006 前端 ACL 边界 | FF-006 check_fe_acl_boundary.py | active | 源码级扫描，实现完整 |
| INV-007 幂等 Key | FF-007 check_idempotency_key.py | active | P0/P1 契约检查 |
| INV-008 层依赖方向 | FF-008 layer_boundary_check.py | active | import-linter 检查 |
| INV-009 OCP 签名冻结 | FF-009 check_ocp_signatures.py | active | SHA256 校验 |
| INV-010 Schema 一致性 | FF-010 check_schema_consistency.py | active | physical_path 存在性检查 |
| INV-011 跨平面通信 | FF-011 check_cross_plane_communication.py | active | 拓扑 + import 嗅探，实现完整 |
| INV-012 Hot Path 纯度 | FF-012 check_hot_path_purity.py | active | asyncio 禁用检查，实现完整 |
| INV-013 风控参数一致性 | FF-013 check_risk-params_consistency.py | active | config 真源对齐 |
| INV-014 Survivorship Bias | FF-014 check_survivorship_bias.py | active | 声明开关检查 |
| INV-015 AISG 拦截 | FF-015 check_aisg_gateway.py | active | 文件存在性 + sandbox 测试 |
| INV-016 审计日志不可篡改 | FF-016 check_audit_log_immutability.py | active | policy_decision_ledger 存在性 |

**结论**：16/16 不变量全部有 fitness function 对应，manifest.yaml 注册完整，run_all.py 编排器可执行。

---
