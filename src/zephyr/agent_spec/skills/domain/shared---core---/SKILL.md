---

skill_id: SKILL-DOM-SHC-001
name: "Shared + Core 蓝图"
description: "跨层共享基础设施：事件总线、SSoT 守卫、合约层、生命周期管理、ProcessLifecycleGateway 进程统一入口"
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-17
version: "0.2.0"
token_budget_l1: 80
token_budget_l2: 600
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Shared + Core (MOD-INF-016)

## CRITICAL Rules

1. **进程创建必须经过 ProcessLifecycleGateway** — 禁止裸 `subprocess.Popen` / `multiprocessing.Process`
2. **所有池化进程自动注册到 DaemonRegistry** — idle_timeout_s 空闲超时自动回收
3. **Gate 防绕过** — CI 阶段 AST 扫描检测裸调用

### Core Operations

| 操作 | 方法 | 说明 |
|------|------|------|
| 启动子进程 | `ProcessLifecycleGateway().launch(name, cmd)` | 返回 PooledProcess 或 None |
| 启动后台进程 | `ProcessLifecycleGateway().launch_daemon(name, cmd)` | 自动注册到 DaemonRegistry |
| 终止全部 | `ProcessLifecycleGateway().terminate_all()` | 清理所有池中进程 |
| 检查进程池 | `ProcessLifecycleGateway().get_stats()` | 返回 ProcessPoolStats |
| 校验入口 | `python -m zephyr.gates.invariants.en_process_lifecycle_gateway` | AST 扫描裸 Popen/Process |

### Unique Constraints

- 空闲超时默认 600s（10分钟）— 超时后进程被自动回收
- ProcessPool 上限 30 进程 — 通过 DaemonRegistry 压力降级
- Gateway 本身不持有业务逻辑 — 纯路由 + 生命周期管理

### Common Error Patterns

- `subprocess.Popen` 直接调用 → CI Gate 阻断，改用 `ProcessLifecycleGateway.launch()`
- 进程泄漏 → 未走 Gateway，检查是否有裸 Popen/Process 调用
- ollama serve 无法关闭 → 使用 `ProcessLifecycleGateway.shutdown()`

## Checklist

- [ ] Verify blueprint before implementation
- [ ] 新进程创建检查：是否使用 ProcessLifecycleGateway？
- [ ] 进程清理检查：shutdown 中是否调用 terminate_all()？
- [ ] Gate 检查：CI 是否通过 en_process_lifecycle_gateway？
- [ ] Check upstream dependencies
- [ ] Validate against acceptance criteria
- [ ] Run gate engine checks (G0-G9)

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| DEFAULT_TIMEOUT | 30 | Default operation timeout (seconds) |

## References (L3, on-demand)

- module_blueprint.md
- integration_guide.md
- troubleshooting.md