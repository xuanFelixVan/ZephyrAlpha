---
module_id: KE-module_blu-2_5_r4-r8-000
title: 2.5 R4-R8 缓解
category: module_blueprint
---

# 2.5 R4-R8 缓解

2.5 R4-R8 缓解

在 `risk_mitigation.py` 中实现对应的 MitigationHandler：
- R4: `SchemaVersionGuard`: 双向版本校验
- R5: `TokenCalibration`: 滚动窗口校准
- R6: `KillSwitchSafeguard`: 脉冲过滤 + 多条件非AND
- R7: `SandboxHardener`: 资源硬边界
- R8: `ProvenanceIntegrityChecker`: hash 链定期校验
