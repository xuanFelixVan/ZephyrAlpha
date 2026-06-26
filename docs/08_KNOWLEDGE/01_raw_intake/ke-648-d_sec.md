---
module_id: KE-648
status: active
title: D-SEC：安全架构与运行时隔离
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# D-SEC：安全架构与运行时隔离

D-SEC：安全架构与运行时隔离

| 检查项 | 结果 | 说明 |
|--------|:----:|------|
| 安全架构与治理安全策略一致 | ✅ | 06-SEC 中 4 条安全红线与 architecture_principles.md §1 完全一致 |
| 运行时平面隔离清晰 | ✅ | Hot/Warm/Cold 三平面定义清晰，跨面通信协议完整 |
| 域间信任流 | ✅ | 7 个安全域（D-EXT/D-AI/D-AGT/D-INT/D-STORE/D-SECRET/D-MGMT）定义完整 |

**验证详情**：
- 06-SEC §2.1 安全域与 `architecture_principles.md` §1 安全红线一一对应：R1→D-SECRET、R2→D-MGMT、R3→D-AI/D-AGT、R4→D-STORE。
- 运行时平面隔离：`runtime_planes.md` §4.2 明确禁止 Cold→Hot 直接通信、Hot 同步调用 Warm Python、跨平面共享可变全局状态。
- LSG 四层防御（L1-L4）与 `vibe_coding_infrastructure_tech_stack.yaml` TECH-15/16/17 技术选型一致。

**P1-005**：06-SEC §10.1 Phase 门禁中 `scaffold → experimental` 出口门禁有 4 项 checkbox，但当前仅完成 1/4（本视图 status: active）。**修复**：按优先级推进剩余 3 项（git-secrets 部署、trufflehog 扫描、audit.db 测试事件）。

**P2-003**：06-SEC §4.4 LSG 误报/漏拦率 SLO 当前为"未测"状态。**修复**：experimental 末必须执行红队评估，填充基线数据。

---
