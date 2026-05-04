## 6. 核心调用流程

```
外部Agent (Trae/Cursor/Claude Code)
    |
    +-- stdio connect --> MCP Server (Python进程)
            |
            +-- tool/discover --> 返回 tool_contracts.yaml 工具清单
            |
            +-- tool/call {name:"decompose_blueprint", args:{...}}
            |       +-- task_manager_server.decompose_blueprint()
            |       +-- blueprint_decomposer --> TaskCard YAML
            |       +-- 返回 TaskCard列表
            |
            +-- tool/call {name:"query_ke", args:{keyword:"..."}}
            |       +-- knowledge_base_server.query_ke()
            |       +-- 返回 KE条目列表
            |
            +-- tool/call {name:"gate_check", args:{task_id:"..."}}
            |       +-- gate_engine_server.check()
            |       +-- 返回 Gate判定结果
            |
            +-- [disconnect] --> 进程退出, stdio 关闭
```

**同步模型**：请求->等待->响应（非流式）。每个 tool/call 是原子操作。

**错误处理**：Tool not found -> `{-32000}`; Args invalid -> `{-32602}`; Internal error -> `{-32603}`.

## 7. 集成依赖关系

| 上游依赖 | 依赖对象 | 契约 |
|---------|---------|------|
| task_manager MCP -> TaskCard | MOD-INF-006 task-system | decompose_blueprint(tool_contracts.yaml) |
| knowledge_base MCP -> KE查询 | MOD-KB-001 knowledge-base | query_ke / create_ke |
| gate_engine MCP -> Gate判定 | MOD-INF-007 gate-engine | gate_check / gate_status |

| 下游消费方 | 消费接口 | 说明 |
|-----------|---------|------|
| Trae IDE | stdio tool/call | 开发时实时调用 |
| Claude Code | stdio tool/call | CI环境Gate判定 |
| Cursor | stdio tool/call | 知识库查询 |

## 11. 施工指引

### 11.1 knowledge_base MCP 实现

```
Step 1: 读 knowledge_base_server.py 现有 stub 代码
Step 2: 实现 query_ke(keyword: str) -> list[dict]
        +-- 连接 MOD-KB-001 的 KE 索引
        +-- 返回匹配的 KE 条目摘要
Step 3: 实现 create_ke(title, body, source) -> ke_id
        +-- 走 KMS 三层漏斗：draft -> audit -> formal
        +-- 返回新 KE 的 ID
Step 4: 在 tool_contracts.yaml 注册新 tool 定义
Step 5: 测试: pytest tests/integration/test_mcp_e2e.py::test_kb_query
```

### 11.2 gate_engine MCP 实现

```
Step 1: 读 gate_engine_server.py 现有 stub 代码
Step 2: 实现 gate_check(task_id) -> GateResult
        +-- 调用 Gate Engine G0-G7 逐门禁检查
        +-- 返回: {gate, passed, reason}
Step 3: 实现 gate_status() -> 各Gate当前状态(open/circuit_broken)
Step 4: 测试: pytest test_gate_check / test_gate_status
```

### 11.3 测试清单

```
[ ] task_manager decompose_blueprint 正常输入 -> TaskCard列表
[ ] task_manager 非法蓝图路径 -> 错误码
[ ] knowledge_base query_ke 空结果 -> 空列表
[ ] gate_engine gate_check 已通过 -> passed=true
[ ] gate_engine gate_check 阻塞 -> passed=false+reason
[ ] MCP进程崩溃 -> Agent重连恢复
```
