---
module_id: KE-1349-------4--------fail-close-003
status: active
title: 10.2 **与其他 4 个服务相反——fail-closed 降级**
category: module_blueprint
ttl: permanent
---

# 10.2 **与其他 4 个服务相反——fail-closed 降级**

10.2 **与其他 4 个服务相反——fail-closed 降级**

> **核心原则**：LSG 是安全闸门。其他服务挂了"宁可功能残缺不阻塞"，**LSG 挂了必须 fail-closed**，宁可全部拒绝流量。放水一秒都可能导致 prompt injection 成功。

**DEGRADE-SEC-001：规则库加载失败——fail-closed 全拒**

触发场景：
- `llm_security_patterns.yaml` 损坏 / 被删
- 规则热加载语法错误

降级动作：

```python
try:
    await self._reload_rules()
except LSGRuleLoadError as e:
    self._mode = "fail_closed"
    log_structured("lsg_degrade", code="DEGRADE-SEC-001", reason=str(e), severity="critical")
    # 后续所有 validate_input / validate_output 一律 allow=False
    # 必须人工介入恢复

async def validate_input(self, payload):
    if self._mode == "fail_closed":
        return InputVerdict(allow=False, reason="LSG_fail_closed_DEGRADE-SEC-001")
    ...
```

**上游契约**：MCP Server / Orchestrator / CE 收到 `allow=False` 且 `reason` 含 `LSG_fail_closed` 时，展示运维告警 + 阻塞请求。**严禁绕过**。

**DEGRADE-SEC-002：schema 未注册时——按严格度决定**

触发场景：`validate_output(payload, schema_id='x.unknown')`

降级动作（受 strictness 控制）：

```python
