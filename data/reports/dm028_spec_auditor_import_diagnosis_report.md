# DM-028 诊断报告：spec_auditor.py 导入不存在的 zephyr.autonomy_core.agent_lifecycle.registry

**任务卡**: DM-028
**诊断日期**: 2026-06-15
**诊断模型**: deepseek
**状态**: COMPLETED

---

## 问题描述

`spec_auditor.py` 文件（多个副本）第37行导入不存在的模块：
```python
from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability
```

错误原因：`zephyr.autonomy_core.agent_lifecycle` 子包不存在，`AgentCapability` 类实际定义在 `zephyr.orchestration.agent_lifecycle.registry` 模块中。

---

## 诊断发现

### 1. 错误导入路径

**文件**: `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\spec_auditor.py`
**第37行**:
```python
from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability
```

**问题**: `zephyr.autonomy_core.agent_lifecycle` 路径不存在。

### 2. 正确替代路径

**文件**: `d:\ZephyrAlpha\src\zephyr\orchestration\agent_lifecycle\registry.py`
**第46行**:
```python
class AgentCapability(BaseModel):
    agent_id: str
    capabilities: list[str] = []
    version: str = "1.0.0"
    spec_hash: str = ""
```

**正确导入路径**:
```python
from zephyr.orchestration.agent_lifecycle.registry import AgentCapability
```

### 3. AgentCapability 兼容性分析

**定义位置**: `zephyr.orchestration.agent_lifecycle.registry`
**类结构**:
- `agent_id: str`
- `capabilities: list[str] = []`
- `version: str = "1.0.0"`
- `spec_hash: str = ""`

**使用方式**（spec_auditor.py 第46-73行）:
```python
def record_agent_spec(capability: AgentCapability) -> dict[str, Any]:
    caps = getattr(capability, "capabilities", getattr(capability, "claimed_capabilities", []))
    return {
        "event_type": "AGENT_SPEC_REGISTERED",
        "agent_id": capability.agent_id,
        "claimed_capabilities": caps,
        "model_provider": getattr(capability, "model_provider", "unknown"),
        "version": getattr(capability, "version", "0.0.0"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

**兼容性判定**: **完全兼容**。`AgentCapability` 类包含 `agent_id`、`capabilities`、`version` 字段，与 `spec_auditor.py` 的使用方式完全匹配。`model_provider` 通过 `getattr(..., "unknown")` 防御，即使缺失也不报错。

### 4. 其他6个 spec_auditor.py 副本检查

| 文件路径 | 第37行导入语句 | 问题 |
|---------|--------------|------|
| `src/zephyr/governance/semantic_auditor/spec_auditor.py` | `from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability` | **相同错误** |
| `src/zephyr/governance/semantic_audit/spec_auditor.py` | `from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability` | **相同错误** |
| `src/zephyr/governance/bridges/spec_auditor.py` | `from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability` | **相同错误** |
| `src/zephyr/governance/spec_auditor.py` | `from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability` | **相同错误** |
| `src/zephyr/governance/audit_trail/bridges/spec_auditor.py` | `from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability` | **相同错误** |

**结论**: 共6个 `spec_auditor.py` 副本存在相同错误导入，全部需要修复为：
```python
from zephyr.orchestration.agent_lifecycle.registry import AgentCapability
```

---

## 修复方案

### 统一修复模式

将所有 `spec_auditor.py` 副本的第37行从：
```python
from zephyr.autonomy_core.agent_lifecycle.registry import AgentCapability
```

改为：
```python
from zephyr.orchestration.agent_lifecycle.registry import AgentCapability
```

### 受影响文件清单（6个）

1. `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\spec_auditor.py`
2. `d:\ZephyrAlpha\src\zephyr\governance\semantic_auditor\spec_auditor.py`
3. `d:\ZephyrAlpha\src\zephyr\governance\semantic_audit\spec_auditor.py`
4. `d:\ZephyrAlpha\src\zephyr\governance\bridges\spec_auditor.py`
5. `d:\ZephyrAlpha\src\zephyr\governance\spec_auditor.py`
6. `d:\ZephyrAlpha\src\zephyr\governance\audit_trail\bridges\spec_auditor.py`

---

## 验收标准达成检查

- [x] 诊断报告包含错误导入路径
- [x] 提供正确替代路径
- [x] AgentCapability 兼容性分析（完全兼容）
- [x] 其他6个 spec_auditor.py 副本检查（全部存在相同错误）

---

## 后续任务

- **DM-029**: 按本诊断报告执行修复（6个文件）
- **DM-030**: 修复后复查验证
