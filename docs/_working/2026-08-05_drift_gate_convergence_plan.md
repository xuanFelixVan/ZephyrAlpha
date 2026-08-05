---
ttl: task_bound
status: done
date: 2026-08-05
---

# drift-gate 收敛方案（体系A × 体系B 双重执行消除）

> 治本 `#ARCH-DUAL-TRIGGER`（待登记到 architecture_issue_registry.yaml）
> 真源代码：`src/zephyr/governance/audit/reconciliation_registry.py`

## 问题

项目有两套生成器自动触发体系，在特定时序下会**双重执行同一批生成器**：

| 体系 | 触发时机 | 入口 | 执行方式 |
|------|----------|------|----------|
| **体系A** | `apply_*.py` 写完 DB 后 | `reconcile_async(source)` | 后台 subprocess 并行跑 |
| **体系B** | `git commit` 之后 | post-commit reconciler | 串联 subprocess |

**双重执行场景**：用户先跑 `apply_depgraph.py`（体系A后台跑 19 个生成器），然后 commit 变更（体系B 又跑同一批生成器）。第二遍是白跑——体系A已生成相同产物，浪费 50-60 秒。

## 方案：drift-gate（预检测跳过）

在体系B的 reconciler 的 `_reconcile` 函数**开头**加一步预检测：

```
git diff --name-only -- <产物文件列表>
```

- **有未提交变更** → 体系A已跑过，产物已更新 → 跳过生成器，直接 auto-commit 现有变更
- **无变更** → 体系A没跑过或产物过时 → 跑生成器（原逻辑兜底）
- auto-commit 失败 → 落回原逻辑跑生成器（兜底，不阻断）

返回 `action="auto_committed"`（合法值，表示"检测到漂移并自动提交修复"）。

## drift-gate 安全边界（核心判定规则）

drift-gate 能否安全使用，取决于生成器的**数据源类型**：

| 生成器数据源 | commit 是否改变数据源 | drift-gate 安全？ | 原因 |
|---|---|---|---|
| **纯 DB 查询** | 否（commit 改文件，apply 改 DB，两者独立） | ✅ 安全 | 体系A跑完后 DB 不再变，文档仍有效 |
| **DB + 文件系统扫描** | **是**（commit 本身增删文件） | ❌ 不安全 | 体系A基于旧文件系统生成，commit 后文档已过时 |

**一句话**：生成器只读 DB → 可加 drift-gate；生成器扫描文件系统 → 不能加。

## 实施记录

### ✅ 阶段1：make_arch_diagram_reconciler（已提交 `9b165499`）

- **位置**：`_reconcile` 开头（L9652）
- **覆盖**：15 个生成器（~50s 串行），全部只读 DB（depgraph_nodes/edges）
- **产物**：`_OUTPUTS` 列表 16 个文件
- **drift-gate 安全**：✅ 全部生成器纯 DB 查询

### ✅ 阶段3a：_reconcile_domain_doc（已提交 `5c7a7845`）

- **位置**：`_reconcile_domain_doc` 开头（L6573）
- **覆盖**：`generate_domain_doc.py --all`（~28s）+ `generate_domain_index.py`，只读 DB
- **产物**：`_DOC_DIRS`（02_domain_architecture_docs/ + generated/domains/）
- **drift-gate 安全**：✅ 生成器纯 DB 查询
- **关键差异**：跳过生成器时也调 `_clear_depgraph_dirty_flag()`，否则下次 commit 重复 fire

### 不实施：make_path_tree_reconciler / _reconcile_arch_model / _reconcile_manifest

| reconciler | 生成器 | 在体系A？ | 数据源 | drift-gate？ | 理由 |
|---|---|---|---|---|---|
| make_path_tree_reconciler | generate_path_tree.py | ✅ | DB + **文件系统扫描** | ❌ 不加 | commit 改文件系统→体系A文档过时，跳过会丢变更 |
| _reconcile_arch_model | dm200916_write_direct.py | ❌ | DB | ❌ 不加 | 体系A不跑此生成器，drift-gate 永不触发（死代码） |
| _reconcile_manifest | generate_script_manifest.py | ❌ | 文件系统扫描 | ❌ 不加 | 同上，体系A不跑 |

**make_path_tree_reconciler 详细排查**：

1. `generate_path_tree.py` 实测耗时 ~8-9s（日志：`regenerate_depgraph_db_*.log`）
2. 该生成器读 `arch_directory_tree` 表（目录）+ **直接扫描文件系统**（文件），见 `generate_path_tree.py` L715
3. `make_path_tree_reconciler` 的 trigger 是 `.py/.yaml` commit——commit 本身可能增删了文件
4. 体系A在 commit **之前**跑，看到的是旧文件列表；commit 后文件列表变了→体系A的文档已过时
5. 加 drift-gate 跳过生成器 → 用过时文档 → 文档与实际文件不一致，直到下次 boot `reconcile_stale` 才修正
6. `generate_project_path_tree.py --write`（DB sync）始终 DELETE+INSERT，无"无变更"信号，无法安全判定 DB 是否真的变了
7. **结论**：8-9s 的节省不值得冒文档过时的正确性风险，保守方案不加

## 下一步行动

1. **登记 issue**：将 `#ARCH-DUAL-TRIGGER` 登记到 `architecture_issue_registry.yaml`（当前代码已引用但未登记，违反注册表铁律#6）
2. **验证**：在下次 `apply_depgraph.py` + commit 的真实工作流中观察日志，确认 drift-gate 触发时返回 `action="auto_committed"` 且 detail 含 "drift-gate: skipped ... generators"
3. **阶段4（可选）**：将 `rule_ai_perception_index` 生成器添加到 `generator_registry.yaml`（待确认该生成器是否已存在）
