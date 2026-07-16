---
ttl: permanent
archived_at: 2026-07-16
archived_from: docs/_working/ghost_commit_automation_assessment.md
archive_reason: 评估完成，completes_when 满足
---

# GitCommitGateway 自动化能力评估报告

> **文档ID**: ARCH-AUTO-ASSESS-001
> **创建时间**: 2026-06-25
> **任务卡**: OPS-2026062517
> **状态**: 评估完成
> **评估对象**: GitCommitGateway 自动启动/事件启动/自动运行/自动关闭能力

---

## 1. 评估结论（一句话）

**GitCommitGateway 是"被动调用型"网关，不需要也不应该做成常驻服务——当前"任务完成自动触发 + 手动 CLI"的双入口模式已满足需求，自动关闭由 Python 作用域 + finally 保证。**

---

## 2. 当前自动化能力盘点

### 2.1 自动启动能力

| 启动方式 | 是否支持 | 说明 |
|---------|---------|------|
| 常驻进程/守护进程 | ❌ 不需要 | 网关是无状态工具，调用即启动 |
| systemd/服务注册 | ❌ 不需要 | 非 7×24 服务 |
| 定时任务（cron） | ❌ 不需要 | commit 是事件驱动，非时间驱动 |
| 手动 CLI | ✅ 已有 | `python scripts/git_commit.py` |
| 代码调用 | ✅ 已有 | `GitCommitGateway().commit()` |

### 2.2 事件启动能力

| 事件源 | 是否接入 | 说明 |
|--------|---------|------|
| TaskRepository.transition(COMPLETED) | ✅ 已接入 | `_auto_commit_on_completion` 自动触发 |
| PG LISTEN/NOTIFY | ❌ 未接入 | 当前 SQLite，无 LISTEN/NOTIFY；PG 迁移后可评估 |
| Webhook | ❌ 未接入 | 无 webhook 场景 |
| 消息队列 | ❌ 未接入 | 无 MQ 基础设施 |

### 2.3 自动运行能力

| 运行环节 | 自动化程度 | 验证状态 |
|---------|-----------|---------|
| 获取全局锁 | ✅ 自动 | 极端测试验证（TTL/损坏/超时） |
| 选择性 stash | ✅ 自动 | 端到端测试验证 |
| git add + commit | ✅ 自动 | 端到端测试验证 |
| stash pop 恢复 | ✅ 自动（finally） | 极端测试验证（冲突保留） |
| 环境变量清理 | ✅ 自动（finally） | 极端测试验证 |
| GW 标记追加 | ✅ 自动 | 端到端测试验证 |

### 2.4 自动关闭能力

| 关闭环节 | 自动化程度 | 验证状态 |
|---------|-----------|---------|
| 锁释放 | ✅ 自动（__exit__） | 极端测试验证（异常后释放） |
| stash 恢复 | ✅ 自动（finally） | 极端测试验证 |
| 环境变量清理 | ✅ 自动（finally） | 极端测试验证 |
| 临时消息文件清理 | ✅ 自动（finally） | 代码审查确认 |
| 进程退出 | ✅ 自动（Python 作用域） | 无需额外处理 |

---

## 3. 为什么不需要常驻服务

### 3.1 网关的本质是"工具"不是"服务"

GitCommitGateway 的核心逻辑是：**收到调用 → 加锁 → stash → commit → 恢复 → 返回**。这是同步操作，不需要常驻内存。

### 3.2 常驻服务的弊端

| 弊端 | 说明 |
|------|------|
| 增加故障面 | 常驻进程可能崩溃/内存泄漏，多一个 SPOF |
| 增加复杂度 | 需要心跳/重启/监控，违反"少一层抽象=少一个幻觉源"原则 |
| 无实际收益 | commit 是低频操作（任务完成时），不需要预热/缓存 |
| 与 SSoT 冲突 | 常驻服务会持有状态，违反 Single Source of Truth |

### 3.3 当前模式的优势

```
任务完成 → transition(COMPLETED) → _auto_commit_on_completion → GitCommitGateway.commit() → 返回
```

- **零状态**：网关不持有任何跨调用状态
- **零依赖**：不依赖外部服务/进程
- **零运维**：无需监控/重启/扩容

---

## 4. PG 迁移后的评估

项目规划将 depgraph.db 迁移到 PostgreSQL（D50-PG 裁定）。迁移后：

### 4.1 可选增强（非必须）

| 增强项 | 收益 | 成本 | 建议 |
|--------|------|------|------|
| PG LISTEN/NOTIFY 触发 | 任务完成事件可跨进程通知 | 中 | ⏸ 延后——当前同步调用已够用 |
| 定时清理过期锁 | 自动清理 TTL 过期的锁文件 | 低 | ⏸ 延后——锁 TTL=1800s 已有清理逻辑 |
| Webhook 通知 commit 结果 | 外部系统感知 commit | 中 | ❌ 不做——无消费者 |

### 4.2 不建议的增强

| 增强项 | 理由 |
|--------|------|
| 独立 commit 守护进程 | 违反"工具非服务"原则，增加 SPOF |
| MQ 异步 commit | commit 必须同步确认结果，异步会丢失可追溯性 |
| 多实例锁竞争 | 全局串行锁是核心设计，多实例会破坏串行化 |

---

## 5. 自动化测试覆盖

### 5.1 已覆盖的自动化场景

| 场景 | 测试文件 | 结果 |
|------|---------|------|
| 任务完成→自动触发网关 | test_task_repo_gateway_e2e.py | 9/9 PASS |
| 网关异常→任务不受影响 | test_task_repo_gateway_e2e.py | ✅ |
| 各状态码处理（OK/NOTHING/STASH_CONFLICT/FAILED/TIMEOUT） | test_task_repo_gateway_e2e.py | ✅ |
| 真实网关集成（实际 commit） | test_task_repo_gateway_e2e.py | ✅ |
| 锁自动释放（异常后） | test_git_commit_extreme.py | 11/11 PASS |
| stash 自动恢复（finally） | test_git_commit_extreme.py | ✅ |
| 环境变量自动清理 | test_git_commit_extreme.py | ✅ |

### 5.2 未覆盖但可接受的场景

| 场景 | 理由 |
|------|------|
| 进程 SIGKILL 后锁残留 | TTL=1800s 兜底，其他 session 会清理 |
| 系统断电后 stash 损失 | git stash 本身持久化到 .git/refs/stash，断电不丢 |

---

## 6. 裁定

### 6.1 当前模式裁定

**维持"被动调用型"模式，不引入常驻服务。**

- 自动启动：通过 `TaskRepository.transition(COMPLETED)` 自动触发（已验证）
- 事件启动：同步方法调用链（已验证），PG 迁移后评估 LISTEN/NOTIFY
- 自动运行：网关内部全自动化（已验证）
- 自动关闭：Python 作用域 + finally 保证（已验证）

### 6.2 后续观察项

| 观察项 | 触发条件 | 行动 |
|--------|---------|------|
| commit 频率过高导致锁等待 | 日均 commit > 100 | 评估是否需要异步队列 |
| TTL=1800s 不够用 | 单次 commit > 30 分钟 | 调大 TTL |
| 锁文件频繁损坏 | 日损坏 > 1 次 | 排查磁盘/文件系统问题 |

---

## 7. 总结

| 问题 | 答案 |
|------|------|
| 能自动启动吗？ | ✅ 任务完成时自动触发（被动调用，非常驻服务） |
| 能事件启动吗？ | ✅ 同步方法调用链（非 MQ/webhook，但够用） |
| 能自动运行吗？ | ✅ 网关内部全自动化（锁/stash/commit/恢复） |
| 能自动关闭吗？ | ✅ Python 作用域 + finally 保证 |
| 自动化测试过吗？ | ✅ 11 极端 + 9 端到端，全 PASS |
| 需要常驻服务吗？ | ❌ 不需要，工具型网关不需要常驻 |

---

> **评估人**: AI 架构师
> **裁定状态**: 维持当前模式
> **下次评估**: PG 迁移完成后（D50-PG）
