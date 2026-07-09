# 四图对齐剩余 7 问题治本方案 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修正 ARCH-056 分层真源规则，消除剩余 7 个四图对齐问题（状态漂移 4 + 域不一致 3）

**Architecture:** domain_id 真源从 depgraph（路径投票）改为 blueprint（逻辑声明）；design_maturity 不再强制四图一致（各图维度不同）；补齐 3 个蓝图缺失字段；修正 1 个蓝图域声明；ARCH-056 裁定记录更新

**Tech Stack:** Python, PostgreSQL, YAML, Markdown frontmatter

**Spec:** `docs/_working/2026-07-10-panorama_remaining_7_issues_remediation.md`

**重要约束:**
- 所有文件路径用绝对路径（d:\ZephyrAlpha\...）
- 不要用 git commit，由 main agent 负责通过 session_worktree_commit 提交
- PYTHONPATH 需设置：`$env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"`
- 先 Read 文件确认实际代码，不要凭行号修改（行号可能已变化）

---

### Task 1: 修改 align_panoramas.py 检测逻辑

**Files:**
- Modify: `d:\ZephyrAlpha\scripts\governance\d5_architecture\generators\align_panoramas.py`
- Test: `d:\ZephyrAlpha\tests\test_align_panoramas.py`

**核心改动:**
1. `_detect_state_drifts`：不再比较四图 design_maturity 一致性，改为检测 blueprint 缺 design_maturity 字段
2. `_detect_domain_mismatches`：depgraph 与 blueprint 域不一致时以 blueprint 为准，降级不报告
3. `to_markdown`：更新报告标题和处置建议

- [ ] **Step 1: Read align_panoramas.py 确认当前代码**

Read `d:\ZephyrAlpha\scripts\governance\d5_architecture\generators\align_panoramas.py` 的以下区域：
- line 560-586：`_detect_state_drifts` 函数
- line 596-618：`_detect_domain_mismatches` 函数
- line 126-206：`to_markdown` 方法

- [ ] **Step 2: 写失败测试 — 状态漂移新逻辑**

在 `d:\ZephyrAlpha\tests\test_align_panoramas.py` 的 `TestDetectStateDrifts` 类中，修改 `test_drift_when_maturity_differs` 测试，并在类末尾追加新测试：

**修改** `test_drift_when_maturity_differs`（原测试期望四图不一致报漂移，新逻辑不应报）：

```python
    def test_no_drift_when_maturity_differs_across_graphs(self):
        """四图 design_maturity 不一致 → 不再报漂移（各图维度不同是正常的）。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="design"),
            _make_node("MOD-X", "dataflow", design_maturity="production"),
            _make_node("MOD-X", "decision", design_maturity="prototype"),
            _make_node("MOD-X", "blueprint", design_maturity="design"),
        ]
        assert _detect_state_drifts(nodes) == []
```

**追加** blueprint 字段缺失检测测试：

```python
    def test_drift_when_blueprint_missing_design_maturity(self):
        """blueprint 缺 design_maturity 字段 → 报字段缺失。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="prototype"),
            _make_node("MOD-X", "blueprint", design_maturity=None),
        ]
        drifts = _detect_state_drifts(nodes)
        assert len(drifts) == 1
        assert drifts[0]["module_id"] == "MOD-X"
        assert "missing" in drifts[0].get("issue", "").lower() or drifts[0]["blueprint"] == "-"

    def test_no_drift_when_blueprint_has_maturity(self):
        """blueprint 有 design_maturity 字段 → 不报。"""
        nodes = [
            _make_node("MOD-X", "depgraph", design_maturity="prototype"),
            _make_node("MOD-X", "blueprint", design_maturity="prototype"),
        ]
        assert _detect_state_drifts(nodes) == []
```

- [ ] **Step 3: 运行测试确认失败**

Run: `$env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python -m pytest tests/test_align_panoramas.py::TestDetectStateDrifts -v`
Expected: FAIL — `_detect_state_drifts` 仍用旧逻辑（四图不一致报漂移）

- [ ] **Step 4: 修改 _detect_state_drifts 函数**

将 `d:\ZephyrAlpha\scripts\governance\d5_architecture\generators\align_panoramas.py` 中 `_detect_state_drifts` 函数（约 line 560-586）替换为：

```python
def _detect_state_drifts(all_nodes: list[PanoramaNode]) -> list[dict]:
    """状态漂移：blueprint 缺 design_maturity 字段（ARCH-056 修正后新语义）。

    四图 design_maturity 维度差异不再报告（各图评估维度不同是正常的）。
    仅检测 blueprint 图中 design_maturity 字段缺失的情况。
    """
    grouped = _group_by_module_id(all_nodes)
    drifts: list[dict] = []
    for mid, nodes in grouped.items():
        graphs = {n.graph for n in nodes}
        if "blueprint" not in graphs:
            continue  # 无 blueprint 节点，不检测
        bp_nodes = [n for n in nodes if n.graph == "blueprint"]
        for n in bp_nodes:
            if not n.design_maturity:
                drifts.append({
                    "module_id": mid,
                    "depgraph": next((x.design_maturity or "-" for x in nodes if x.graph == "depgraph"), "-"),
                    "dataflow": next((x.design_maturity or "-" for x in nodes if x.graph == "dataflow"), "-"),
                    "decision": next((x.design_maturity or "-" for x in nodes if x.graph == "decision"), "-"),
                    "blueprint": "-",
                    "issue": "missing_design_maturity",
                })
                break  # 一个 blueprint 节点缺字段就够了
    drifts.sort(key=lambda x: x["module_id"])
    return drifts
```

- [ ] **Step 5: 写失败测试 — 域不一致新逻辑**

在 `d:\ZephyrAlpha\tests\test_align_panoramas.py` 的 `TestDetectDomainMismatches` 类中追加测试：

```python
    def test_depgraph_blueprint_mismatch_not_reported(self):
        """depgraph 与 blueprint 域不一致 → 不报告（blueprint 是逻辑真源）。"""
        nodes = [
            _make_node("MOD-X", "depgraph", domain_id="D_TRADING"),
            _make_node("MOD-X", "blueprint", domain_id="D_INFRA_RUNTIME"),
        ]
        assert _detect_domain_mismatches(nodes) == []

    def test_dataflow_blueprint_mismatch_reported(self):
        """dataflow 与 blueprint 域不一致 → 报告（dataflow 应向 blueprint 对齐）。"""
        nodes = [
            _make_node("MOD-X", "dataflow", domain_id="D_TRADING"),
            _make_node("MOD-X", "blueprint", domain_id="D_INFRA_RUNTIME"),
        ]
        mismatches = _detect_domain_mismatches(nodes)
        assert len(mismatches) == 1
        assert mismatches[0]["module_id"] == "MOD-X"
        assert mismatches[0]["dataflow"] == "D_TRADING"
        assert mismatches[0]["blueprint"] == "D_INFRA_RUNTIME"
```

- [ ] **Step 6: 运行测试确认失败**

Run: `$env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python -m pytest tests/test_align_panoramas.py::TestDetectDomainMismatches -v`
Expected: FAIL — `_detect_domain_mismatches` 仍用旧逻辑

- [ ] **Step 7: 修改 _detect_domain_mismatches 函数**

将 `_detect_domain_mismatches` 函数（约 line 596-618）替换为：

```python
def _detect_domain_mismatches(all_nodes: list[PanoramaNode]) -> list[dict]:
    """域不一致：dataflow/decision 与 blueprint 域不一致（ARCH-056 修正后新语义）。

    depgraph 与 blueprint 域不一致不报告（depgraph 是路径投票值，blueprint 是逻辑真源）。
    仅检测 dataflow/decision 与 blueprint 不一致的情况。
    """
    grouped = _group_by_module_id(all_nodes)
    mismatches: list[dict] = []
    for mid, nodes in grouped.items():
        graphs = {n.graph for n in nodes}
        if "blueprint" not in graphs:
            continue  # 无 blueprint 节点，无法比较
        bp_domain = next((n.domain_id for n in nodes if n.graph == "blueprint" and n.domain_id), None)
        if not bp_domain:
            continue  # blueprint 无 domain_id，无法比较
        per_graph: dict[str, str] = {}
        for n in nodes:
            if n.graph in ("dataflow", "decision") and n.domain_id:
                per_graph[n.graph] = n.domain_id
        mismatched = {g: d for g, d in per_graph.items() if d != bp_domain}
        if mismatched:
            mismatches.append({
                "module_id": mid,
                "depgraph": "-",
                "dataflow": mismatched.get("dataflow", "-"),
                "decision": mismatched.get("decision", "-"),
                "blueprint": bp_domain,
            })
    mismatches.sort(key=lambda x: x["module_id"])
    return mismatches
```

- [ ] **Step 8: 更新 to_markdown 报告标题和处置建议**

在 `to_markdown` 方法中（约 line 126-206），修改以下行：

将 line 138 的 `"  - 状态漂移（design_maturity 不一致）"` 改为：
```python
        lines.append("  - 状态漂移（blueprint 缺 design_maturity）: {}".format(len(self.state_drifts)))
```

将 line 158 的 `"## 2. 状态漂移（design_maturity 不一致）"` 改为：
```python
        lines.append("## 2. 状态漂移（blueprint 缺 design_maturity 字段）")
```

将 line 201 的处置建议改为：
```python
        lines.append("- 状态漂移：blueprint frontmatter 补齐 design_maturity 字段（四图维度差异不再报告）")
```

将 line 202 的处置建议改为：
```python
        lines.append("- 域不一致：dataflow/decision 向 blueprint 对齐（depgraph 路径投票值不覆盖逻辑声明）")
```

- [ ] **Step 9: 运行全部测试确认通过**

Run: `$env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python -m pytest tests/test_align_panoramas.py -v`
Expected: 全部 passed（原有测试可能需要适配新逻辑，修改 `test_drift_when_maturity_differs` 为 `test_no_drift_when_maturity_differs_across_graphs`）

- [ ] **Step 10: 报告完成**

不要 commit。报告修改的文件和测试结果。

---

### Task 2: 数据修复（蓝图 frontmatter）

**Files:**
- Modify: `d:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md`
- Modify: `d:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md`
- Modify: `d:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\blueprint.md`
- Modify: `d:\ZephyrAlpha\docs\03_modules\_domain_governance\panorama_alignment_engine\blueprint.md`

- [ ] **Step 1: 补齐 MOD-L02-001 蓝图的 design_maturity**

Read `d:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md` 前 35 行，找到 `stability: evolving` 行。在其后加一行 `design_maturity: prototype`。

Edit:
- old_string: `stability: evolving\nverifiability: hybrid`
- new_string: `stability: evolving\ndesign_maturity: prototype\nverifiability: hybrid`

- [ ] **Step 2: 补齐 MOD-L04-001 蓝图的 design_maturity**

Read `d:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md` 前 35 行，找到 `stability: evolving` 行。

Edit:
- old_string: `stability: evolving\nverifiability: manual`
- new_string: `stability: evolving\ndesign_maturity: prototype\nverifiability: manual`

- [ ] **Step 3: 补齐 MOD-L05-001 蓝图的 design_maturity**

Read `d:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\blueprint.md` 前 35 行，找到 `stability: evolving` 行。

Edit:
- old_string: `stability: evolving\nverifiability: manual`
- new_string: `stability: evolving\ndesign_maturity: prototype\nverifiability: manual`

**注意**: Step 2 和 Step 3 的 old_string 相同（`stability: evolving\nverifiability: manual`），但它们是不同文件，所以不会冲突。Edit 工具需要指定不同的 file_path。

- [ ] **Step 4: 改 MOD-GOV-SYNC-PANORAMA 的 responsibility_domain**

Read `d:\ZephyrAlpha\docs\03_modules\_domain_governance\panorama_alignment_engine\blueprint.md` 前 15 行，确认 `responsibility_domain: D_GOVERNANCE` 在 line 10。

Edit:
- old_string: `responsibility_domain: D_GOVERNANCE`
- new_string: `responsibility_domain: D_GOV_SCRIPTS`

- [ ] **Step 5: 验证修改**

Run: `Select-String -Path "d:\ZephyrAlpha\docs\03_modules\_domain_factor\blueprint.md","d:\ZephyrAlpha\docs\03_modules\_domain_risk\blueprint.md","d:\ZephyrAlpha\docs\03_modules\_domain_portfolio_core\blueprint.md" -Pattern "design_maturity"`

Expected: 3 个文件各匹配到 `design_maturity: prototype`

Run: `Select-String -Path "d:\ZephyrAlpha\docs\03_modules\_domain_governance\panorama_alignment_engine\blueprint.md" -Pattern "responsibility_domain"`

Expected: `responsibility_domain: D_GOV_SCRIPTS`

- [ ] **Step 6: 报告完成**

不要 commit。报告修改的文件。

---

### Task 3: 修正 ARCH-056 + exempt_list + 重跑验证

**Files:**
- Modify: `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\architecture_issue_registry.yaml`
- Modify: `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\panorama_exempt_list.yaml`

- [ ] **Step 1: 更新 ARCH-056 裁定记录**

Read `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\architecture_issue_registry.yaml` 的 line 1564-1591（ARCH-056 条目）。

找到 `adjudication:` 字段（约 line 1573），将其中的 `(a)` 条目修改：

- old_string（在 adjudication 字段内）:
```
    (a) depgraph.nodes 为架构数据真源，dataflow/decision/blueprint 核心字段单向派生
```
- new_string:
```
    (a) depgraph.nodes 为架构数据真源（模块存在性/依赖关系/文件路径/node_type）；domain_id 真源为 blueprint frontmatter（逻辑职责声明，非物理位置）；design_maturity 各图独立评估（维度不同，不强制一致）。2026-07-10 修正
```

找到 `last_updated: '2026-07-09'`（约 line 1591），改为 `last_updated: '2026-07-10'`。

- [ ] **Step 2: 更新 exempt_list 加入 MOD-MKT_DATA**

Read `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\panorama_exempt_list.yaml`。

Edit:
- old_string: `exempt_module_ids: []`
- new_string:
```yaml
exempt_module_ids:
  - MOD-MKT_DATA
```

- [ ] **Step 3: 重跑对齐检测**

Run: `$env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python scripts/governance/d5_architecture/generators/align_panoramas.py`
Expected: 问题总数 0（或接近 0）

- [ ] **Step 4: 运行全部引擎测试**

Run: `$env:PYTHONPATH="d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"; python -m pytest tests/test_align_panoramas.py tests/governance/test_panorama_common.py tests/governance/test_blueprint_frontmatter_reconciler.py tests/governance/test_sync_panorama_module.py -v --tb=no -q`
Expected: 全部 passed

- [ ] **Step 5: 报告完成**

不要 commit。报告对齐检测结果和测试结果。
