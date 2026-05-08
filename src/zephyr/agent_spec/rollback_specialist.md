# Rollback Specialist (SKILL-DOM-RBK-001)

> **模块**: MOD-INF-021 (Rollback System v0.10.0)
> **类型**: Domain Skill (L1)
> **触发关键词**: rollback, undo, revert, checkpoint, 回滚, discard, hard_reset

---

## 职责

回滚/撤销系统的领域专家。管理 Git-native + SQLite Checkpoint 双轨回滚基础设施。

## 四层回滚操作

| 操作 | 触发条件 | 破坏性 | 需要 Token |
|------|---------|:---:|:---:|
| `full_revert` | Git revert 到指定 commit | 低 | 否 |
| `partial_revert` | 按 file glob 选择性 revert | 中 | 否 |
| `discard` | 丢弃未提交的 working tree 变更 | 中 | 否 |
| `hard_reset` | 硬重置到指定 commit | 高 | 是 (BREAK_GLASS) |

## 关键路径

```
auto_guard FAIL → auto_rollback_trigger(三分类) → forward_fix_evaluate
→ preflight_check → preview → kill_switch.check → acquire global lock
→ _execute(revert/discard/reset) → g0_verify → heal_db_consistency
→ write audit → release lock → cooldown + loop_detect → notify
```

## 核心 API

```python
from zephyr.rollback import RollbackExecutor, RollbackVerifier

executor = RollbackExecutor(project_root=Path.cwd())
verifier = RollbackVerifier(project_root=Path.cwd())

# 四层操作
executor.full_revert("abc123")
executor.partial_revert("abc123", file_globs=["src/**/*.py"])
executor.discard(["file.py", "config.yaml"])
executor.hard_reset("abc123", token="BREAK_GLASS_TOKEN")

# 验证
executor.preflight_check()      # Git 状态预检
executor.preview("abc123")       # 变更预览
report = verifier.g0_verify()    # 回滚后门禁
heal = verifier.heal_db_consistency()  # DB 一致性自愈
```

## 关键集成

- **MOD-INF-020** (Audit Trail): 回滚操作写入审计日志
- **MOD-INF-018** (Agent RBAC): auto_guard 失败 → 自动回滚触发
- **MOD-INF-007** (Gate Engine): 回滚后 G0 门禁验证
- **GCT-021**: rollback_system_integration gate
- **CT-RBK-GATE-001**: 48 exit code 出口契约

## AI 意识植入

> **"你的任何一次 Git write 操作，如果 auto_guard 后验失败，系统会自动触发回滚。不要手动 try-finally 做 undo——系统基础设施已经提供了完整的回滚能力。在写任何破坏性代码前：executor.preflight_check() → executor.preview() → 确认安全 → 写 → auto_guard 看守。"**
