---
skill_id: SKILL-DOM-{{MODULE_ABBR}}-{{NUMBER}}
name: "容量保障体系蓝图（B3 · 2）"
description: ""
allowed-tools: [Read, Grep, Glob, Edit, Write, Bash]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-06
version: "0.1.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
---

# Domain Skill: 容量保障体系蓝图（B3 · 2）

## CRITICAL Rules

### Core Operations
# dependency_capacity_guard.py（v2.5.0 新增，挂载到 pip 操作的 wrapper）
class DependencyCapacityGuard:
    """拦截 pip 变更——在变更前/后做容量快照，异常自动回滚"""

    def guard_pip_operation(
        self, operation: str, packages: list[str]
    ) -> "PipCapacityResult":
        """在 pip install/upgrade 前后做容量对比"""
        before = self._capacity_snapshot()
        before_hash = self._pip_freeze_hash()

        # 执行 pip 操作（在 sandbox 中先跑，不在真实环境）
        with Sandbox.create() as sb:
            try:
                pip_result = sb.pip(operation, packages, timeout=120)
            except Exception as e:
                return PipCapacityResult(
                    allowed=False,
                    reason=f"pip {operation} {packages} 在 sandbox 中失败: {e}"
                )

        after = self._capacity_snapshot(after_pip=True)
        diff = CapacityDiff(before=before, after=after)

        # 判定：变更超过了"合理范围"吗？
        if diff.memory_increase_mb > 100:
            return PipCapacityResult(
                allowed=False,
                reason=f"pip {operation} {packages} 导致内存增加 {diff.memory_increase_mb}MB "
                       f"（从 {before.memory_mb}MB → {after.memory_mb}MB），超出 100MB 安全阈值",
                rollback_command=f"pip install --force-reinstall {' '.join(packages)}=={before.versions}",
            )

        if diff.import_time_increase_ms > 500:
            return PipCapacityResult(
                allowed=False,
                reason=f"pip {operation} {packages} 导致模块导入时间增加 "
                       f"{diff.import_time_increase_ms}ms——可能引入了重型依赖",
            )

        # 通过——记录到容量审计日志
        self.db.log_dependency_change(
            operation=operation, packages=packages,
            before_hash=before_hash, after_hash=self._pip_freeze_hash(),
            capacity_diff=diff,
        )
        return PipCapacityResult(allowed=True, capacity_diff=diff)
```

**集成方式**：所有 AI Agent 对 `pip` 的调用都必须经过 `DependencyCapacityGuard`——AI 不能直接调用 `subprocess.run(['pip', 'install'...])`。

---

### Unique Constraints
## 2. 设计约束（回顾大盘 + 用户原意）

**Owner 指示**（形成设计约束）：
- 未来不止 1000 模块，可能 1500+，所有设计按极限容量考虑
- 现在把能改的改了，不给未来埋雷
- 为系统保留"多进程 / 分布式事件总线 / 数据库分片"的口子
- 零依赖优先：能用 Python stdlib + SQLite 完成的不引入新依赖
- 免费优先：能用 Trae CN 免费模型完成的不调付费 API

**当前规模**：97 模块设计 + 144 实现文件 | **极限容量**：500 模块（单进程），超过则启用多进程/分布式扩展

---

### Common Error Patterns
待填写

## Checklist

- [ ] Verify blueprint before implementation
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
