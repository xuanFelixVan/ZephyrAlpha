# 四图孤儿治理与同步闭环 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 消除 3 个孤儿模块 + 1 个状态漂移，增加 sync prune 逻辑和 gate 触发扩展，达成四图零问题

**Architecture:** A1-A3 数据修复 + B1 prune 逻辑 + B2 gate 扩展 + B3 onboarding 文档

**Tech Stack:** Python, PostgreSQL, YAML, Markdown frontmatter

**Spec:** `docs/_working/2026-07-15-panorama_orphan_governance_spec.md`

**重要约束:**
- 所有文件路径用绝对路径（d:\ZephyrAlpha\...）
- 不要用 git commit，由 main agent 负责通过 session_worktree_commit 提交
- PYTHONPATH 需设置：`$env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"`
- 先 Read 文件确认实际代码，不要凭行号修改
- depgraph 修改必须用 apply_depgraph.py，禁止直接改数据库
- 改 depgraph 前必须 git commit 备份（由 main agent 在 Task 1 前完成）

---

### Task 1: 数据修复 — MOD-004 + MOD-GOV_SCRIPTS-001

**Files:**
- Modify: `d:\ZephyrAlpha\docs\03_modules\_cross_layer\_b_track_interfaces\feedback_loop_engine_interface.md`
- Modify: `d:\ZephyrAlpha\scripts\governance\d7_code\scan_complexity.py`
- DB: depgraph node 更新（MOD-GOV_SCRIPTS-001 → MOD-GOV-SCRIPTS）

- [ ] **Step 1: Read MOD-004 blueprint 文件确认 frontmatter**

Read `d:\ZephyrAlpha\docs\03_modules\_cross_layer\_b_track_interfaces\feedback_loop_engine_interface.md` 前 30 行，确认：
- `module_id: MOD-004` 的确切位置和格式
- 是否已有 `design_maturity` / `build_status` / `responsibility_domain` 字段
- 同目录兄弟文件 `d:\ZephyrAlpha\docs\03_modules\_cross_layer\_b_track_interfaces\context_engine_interface.md` 前 15 行，确认字段格式参考

- [ ] **Step 2: 修改 MOD-004 frontmatter**

将 `module_id: MOD-004` 改为 `module_id: MOD-FEEDBACK_LOOP`。

补齐缺失字段（参考兄弟文件格式）。在 frontmatter 中添加：
```yaml
design_maturity: design
build_status: planned
responsibility_domain: D_FEEDBACK_LOOP
```

注意：先 Read 确认实际内容，用 Edit 精确替换。如果字段已存在则不重复添加。

- [ ] **Step 3: 验证 MOD-004 修改**

Run: `Select-String -Path "docs\03_modules\_cross_layer\_b_track_interfaces\feedback_loop_engine_interface.md" -Pattern "module_id|design_maturity|responsibility_domain"`

Expected: `module_id: MOD-FEEDBACK_LOOP`, `design_maturity: design`, `responsibility_domain: D_FEEDBACK_LOOP`

- [ ] **Step 4: Read scan_complexity.py 确认头部**

Read `d:\ZephyrAlpha\scripts\governance\d7_code\scan_complexity.py` 前 20 行，确认 `[BLUEPRINT] MOD-GOV_SCRIPTS-001` 的确切格式。

同时 Read 同目录 `d:\ZephyrAlpha\scripts\governance\d7_code\check_pure_shim.py` 前 5 行，确认 `MOD-GOV-SCRIPTS` 的格式参考。

- [ ] **Step 5: 修改 scan_complexity.py 头部 module_id**

将文件头部 `[BLUEPRINT] MOD-GOV_SCRIPTS-001` 改为 `[BLUEPRINT] MOD-GOV-SCRIPTS`。

注意：文件头可能有多个地方引用 module_id（如 `[BLUEPRINT]` 行、注释中的 `module_id=` 等），需要全部替换。用 `replace_all=true` 如果模式唯一。

- [ ] **Step 6: 更新 depgraph 节点**

先查询旧节点 ID：
```python
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
with get_depgraph_pg_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT node_id, path, blueprint_id FROM nodes WHERE blueprint_id = 'MOD-GOV_SCRIPTS-001'")
        print(cur.fetchall())
```

然后用 apply_depgraph.py 删除旧节点并添加新节点（或运行 generate_project_depgraph.py 增量更新）：

方案 A（推荐）：运行 generate_project_depgraph.py 重新扫描源码（不加 --force）：
```
cd d:\ZephyrAlpha; $env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python scripts/governance/generate_project_depgraph.py
```

方案 B（备选）：用 apply_depgraph.py 手动操作：
```
# 查询 apply_depgraph.py 是否有 --delete-nodes 或类似命令
python scripts/governance/apply_depgraph.py --help
```

验证旧节点已删除、新节点已创建：
```python
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
with get_depgraph_pg_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT node_id, path, blueprint_id FROM nodes WHERE blueprint_id = 'MOD-GOV_SCRIPTS-001'")
        print("旧节点:", cur.fetchall())
        cur.execute("SELECT node_id, path, blueprint_id FROM nodes WHERE blueprint_id = 'MOD-GOV-SCRIPTS' AND path LIKE '%scan_complexity%'")
        print("新节点:", cur.fetchall())
```

Expected: 旧节点 0 rows，新节点 1 row

- [ ] **Step 7: 更新 path_ownership_map.yaml**

搜索 `path_ownership_map.yaml` 中 `MOD-GOV_SCRIPTS-001` 的引用并替换为 `MOD-GOV-SCRIPTS`：
```
Select-String -Path "scripts\governance\generators\generate_path_ownership_map.py" -Pattern "MOD-GOV_SCRIPTS-001"
```

注意：path_ownership_map.yaml 可能是自动生成的，如果是则只需修改源文件后重新生成。先检查是否是自动生成文件。

- [ ] **Step 8: 报告完成**

不要 commit。报告修改了哪些文件，depgraph 更新结果。

---

### Task 2: sync_prune 逻辑 + MOD-BIZ-002 清理

**Files:**
- Modify: `d:\ZephyrAlpha\scripts\governance\sync_panorama_module.py`
- Test: `d:\ZephyrAlpha\tests\test_sync_panorama_module.py`（如存在）或 `d:\ZephyrAlpha\tests\governance\test_sync_panorama_module.py`

- [ ] **Step 1: Read sync_panorama_module.py 确认结构**

Read `d:\ZephyrAlpha\scripts\governance\sync_panorama_module.py`，确认：
- CLI 参数解析部分（argparse）
- `sync_module_panorama` 主函数
- decision_layers UPSERT SQL 语句
- 现有测试文件位置（用 Glob 搜索 `test_sync_panorama`）

- [ ] **Step 2: 写失败测试 — prune_orphans**

在测试文件中追加测试：

```python
def test_prune_orphans_removes_orphan_placeholder_layers():
    """prune_orphans 删除 decision_layers 中 track='placeholder' 且 layer_id 不在 depgraph.nodes.blueprint_id 中的记录。"""
    # 需要 mock 或真实 DB 连接
    # 调用 prune_orphans() 函数
    # 验证返回 deleted_count >= 0
    # 验证 MOD-BIZ-002 已被删除（如果在测试 DB 中）
    pass  # 根据实际测试框架调整
```

注意：先 Read 确认测试文件是否存在及其测试风格（是否用真实 DB、mock、fixture 等），然后编写匹配风格的测试。

- [ ] **Step 3: 运行测试确认失败**

Run: `cd d:\ZephyrAlpha; $env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python -m pytest tests/test_sync_panorama_module.py -v -k prune`
Expected: FAIL（prune_orphans 函数不存在）

- [ ] **Step 4: 实现 prune_orphans 函数**

在 `sync_panorama_module.py` 中添加 `prune_orphans` 函数：

```python
def prune_orphans(conn_depgraph, conn_decision) -> dict:
    """删除 decision_layers 中的孤儿占位层。

    孤儿定义：track='placeholder' 且 layer_id 不在 depgraph.nodes.blueprint_id 中。
    """
    # 1. 查询 depgraph 中所有 blueprint_id
    with conn_depgraph.cursor() as cur:
        cur.execute("SELECT DISTINCT blueprint_id FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id <> ''")
        valid_ids = {row[0] if not isinstance(row, dict) else row["blueprint_id"] for row in cur.fetchall()}

    # 2. 查询 decision_layers 中的占位层
    with conn_decision.cursor() as cur:
        cur.execute("SELECT layer_id FROM decision_layers WHERE track = 'placeholder'")
        placeholders = [row[0] if not isinstance(row, dict) else row["layer_id"] for row in cur.fetchall()]

    # 3. 找出孤儿
    orphans = [lid for lid in placeholders if lid not in valid_ids]

    # 4. 删除孤儿
    deleted = 0
    if orphans:
        with conn_decision.cursor() as cur:
            for lid in orphans:
                cur.execute("DELETE FROM decision_layers WHERE layer_id = %s AND track = 'placeholder'", (lid,))
                deleted += cur.rowcount
        conn_decision.commit()

    return {"deleted": deleted, "orphans": orphans}
```

在 CLI argparse 中添加 `--prune-orphans` 选项，调用 `prune_orphans` 函数。

- [ ] **Step 5: 运行测试确认通过**

Run: `cd d:\ZephyrAlpha; $env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python -m pytest tests/test_sync_panorama_module.py -v -k prune`
Expected: PASS

- [ ] **Step 6: 执行 prune 清理 MOD-BIZ-002**

Run: `cd d:\ZephyrAlpha; $env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python scripts/governance/sync_panorama_module.py --prune-orphans`

Expected: 输出 deleted=1（MOD-BIZ-002），或更多如果存在其他孤儿

验证：
```python
from zephyr.governance.persistence.decisiongraph_schema import get_decisiongraph_pg_connection
with get_decisiongraph_pg_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT layer_id FROM decision_layers WHERE layer_id = 'MOD-BIZ-002'")
        print("MOD-BIZ-002:", cur.fetchall())
```
Expected: 0 rows

- [ ] **Step 7: 报告完成**

不要 commit。报告 prune 逻辑实现 + MOD-BIZ-002 清理结果。

---

### Task 3: Gate 触发扩展 + AGENTS.md onboarding + 验证

**Files:**
- Modify: `d:\ZephyrAlpha\src\zephyr\gov_enforcement\commit_gates\panorama_alignment_gate.py`
- Modify: `d:\ZephyrAlpha\AGENTS.md`

- [ ] **Step 1: 扩展 gate 触发模式**

Read `d:\ZephyrAlpha\src\zephyr\gov_enforcement\commit_gates\panorama_alignment_gate.py` line 58-69（`_TRIGGER_PATTERNS`）。

在 `_TRIGGER_PATTERNS` 元组中追加：
```python
    "docs/03_modules/",
```

这样任何 `docs/03_modules/` 下的文件变更都会触发对齐检测。

- [ ] **Step 2: 更新 AGENTS.md §9 onboarding 流程**

Read `d:\ZephyrAlpha\AGENTS.md` 搜索 §9 或 "新模块接入" 或 "onboarding" 相关章节。

在 onboarding 步骤中增加"四图注册步骤"：

```markdown
### 四图注册（ARCH-057 裁定）

新模块 MUST 按以下顺序注册四图：

1. **depgraph 登记（真源）**：`python scripts/governance/apply_depgraph.py --add-design-node --path <源码路径> --blueprint-id <MOD-XXX> --domain-id <D_XXX>`
2. **四图同步**：`python scripts/governance/sync_panorama_module.py <MOD-XXX>`（自动派生到 dataflow/decision/blueprint）
3. **对齐验证**：`python scripts/governance/d5_architecture/generators/align_panoramas.py`（问题总数应为 0）
4. **孤儿清理**（定期）：`python scripts/governance/sync_panorama_module.py --prune-orphans`（清理 decision_layers 中的孤儿占位层）

禁止跳过步骤 1-2 直接创建蓝图文件（会导致 blueprint 图孤儿）。
```

- [ ] **Step 3: 重跑对齐检测**

Run: `cd d:\ZephyrAlpha; $env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python scripts/governance/d5_architecture/generators/align_panoramas.py`

Expected: 问题总数 = 0（孤儿=0, 状态漂移=0, 域不一致=0, 设计态孤立=0）

如果有剩余问题，报告具体是哪些。

- [ ] **Step 4: 运行全部相关测试**

Run: `cd d:\ZephyrAlpha; $env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python -m pytest tests/test_align_panoramas.py tests/test_sync_panorama_module.py -v --tb=short -q`

Expected: 全部 passed

- [ ] **Step 5: 报告完成**

不要 commit。报告：
- gate 触发模式修改
- AGENTS.md 修改
- 对齐检测结果
- 测试结果
