---
module_id: KE-585
status: active
title: D-TEST：架构守卫与测试适配度
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# D-TEST：架构守卫与测试适配度

D-TEST：架构守卫与测试适配度

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| 架构模型是否有对应 fitness function | ✅ | 16/16 不变量有对应 FF |
| 所有不变量是否有对应检查 | ✅ | 全部已注册 manifest.yaml |
| fitness function 实现完整度 | ⚠️ | FF 已标记 maturity + phase_required（INV-001=t1, INV-004=l02, INV-016=beta） |

**P0-003（已降级）**：FF-001（INV-001 Kill Switch 延迟）当前为"声明级"检查（CAP-009），`ZEPHYR_T1_KILL_SWITCH_PROBE=1` 实测钩子预留但未实现实际探针。**根因**：T1 真实资金接入前 Kill Switch 无实际运行时环境。**状态**：✅ 已修复——`manifest.yaml` 已标记 `maturity: L1-declarative` + `phase_required: t1`，明确 T1 前升级为 L3-runtime 实测探针。

**P0-004（已降级）**：FF-004（INV-004 PIT 铁律）当前为"静态扫描 L02 look-ahead 模式"，但 `check_pit_compliance.py` 未实际扫描源码中的 look-ahead 用法（如 `.shift(-1)` / `.future()` 等模式）。**根因**：PIT 合规检查需要因子计算代码实际存在后才能有效扫描，当前 L02 为 planned 状态。**状态**：✅ 已修复——`manifest.yaml` 已标记 `maturity: L1-declarative` + `phase_required: l02_implementation`，明确 L02 实现后激活实际扫描逻辑。

**P1-004**：FF-016（INV-016 审计日志不可篡改）当前仅检查 `policy_decision_ledger.jsonl` 存在性，未实现哈希链校验。**状态**：✅ 已修复——`manifest.yaml` 已标记 `maturity: L1-declarative` + `phase_required: beta`，明确 beta 阶段升级为 L2-static-scan 哈希链校验。

**P2-002**：`check_schema_consistency.py` 仅检查 `physical_path` 文件存在性，未检查文件内容是否与 YAML 声明的接口签名一致。**状态**：✅ 已修复——`manifest.yaml` 已标记 `maturity: L2-static-scan` + `phase_required: phase2`，明确 Phase 2 配合 OCP 冻结机制升级。

---
