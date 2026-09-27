---
ttl: task_bound
completes_when: coordinator applies the four registration blocks below and the lane is released
lane: st-gate-fix
task: gate-tree-read-fix
status: awaiting_coordinator
verified: registry files untouched by this lane
assumed: single writer owns docs/01_policies_and_standards/_registry
input_set_disjoint_with: docs/01_policies_and_standards/_registry/**
evidence_ref.cmd: git status --porcelain -uall in .worktrees/st-gate-fix shows only three files
---

# register_manifest — st-gate-fix / gate-tree-read-fix

This lane wrote nothing under `docs/01_policies_and_standards/_registry/**`.
Everything below is a copy-ready registration request for the single-writer coordinator.

## 1. module_translation_registry.yaml — one new entry (required by TRANSLATION-COVERAGE)

Anchor: insert next to the sibling test entry at `module_path: tests/governance/commit_gates/test_test_source_consistency_gate.py`

```yaml
- module_path: tests/gov_enforcement/test_gate_tree_view_source_resolution.py
  domain_id: D_GOV_ENFORCEMENT
  name_zh: 门禁树视图同源观测面单测
  name_en: Test Gate Tree View Source Resolution
  desc_zh: ''
  desc_en: ''
  plain_zh: 检查那道防测试漂移的门禁，是不是把测试和源码放在同一份待提交内容里比对，防止新代码被误杀。
  responsibility_layer: governance
```

Command shape used by the tooling: `python scripts/governance/d3_metadata/add_module_translation.py`
(fallback: hand-insert the block above in the same catalogue bag as the gate fix).

## 2. depgraph — register before merge (RULE-DEPGRAPH)

```
python scripts/governance/apply_depgraph.py --add-file-node \
  --path tests/gov_enforcement/test_gate_tree_view_source_resolution.py
python scripts/governance/apply_depgraph.py --add-edge \
  --from tests/gov_enforcement/test_gate_tree_view_source_resolution.py \
  --to src/zephyr/gov_enforcement/commit_gates/test_source_consistency_gate.py
```

No rename happened in this lane, so `generate_project_depgraph.py --force` is not required by
RENAME-DEPGRAPH-SYNC; regenerate only if the coordinator prefers a full rebuild in the same window.

## 3. gate_registry.yaml — no field change expected

`TEST-SOURCE-CONSISTENCY` keeps `gate_id`, `priority=102`, `own_scope` marking. The fix changed the
**observation face inside the gate body**, recorded in the module header `[INVARIANTS]`
(新增 两侧同源铁律). If the registry mirrors that invariant string, regenerate with the registry
generator rather than editing the row.

## 4. Scoped follow-ups to file (survey results, NOT fixed here)

| id to file | gate | one-line ask |
|---|---|---|
| FU-GATE-FACE-1 | SCRIPTS-IMPORT-INTEGRITY | symbol universe is imported from main-disk `_shared.constants` via `sys.path` mutation and cached in `sys.modules`; replace with AST parse of the tree bytes. Direction = false green, so priority = 静默漏检 rather than 阻断 |
| FU-GATE-FACE-2 | ALGO-FLOW-LINK | anchor-target and source_of_truth existence probed on disk (`:350`, `:417`) while content is staged-first; migrate to `_repo_state_has_file`. Warn-only today, so do not upgrade to blocking in the same bag |
| FU-GATE-FACE-3 | RESOURCE-SCHEDULE | helper/registry loaded from `REPO_ROOT` disk with `return None` on miss (`:710-716`); make it tree-first so a landing worktree does not silently skip scheduling |

Already-declared exemption, no action: `CONSUMERS-ACCURACY` keeps the disk face on purpose
(warn-only, documented in-source under the 裁定#279 blind-spot family).

## 5. Bag composition note for whoever lands this

The bag must contain, together: the gate fix, this test file, the translation entry (§1), the
depgraph node (§2), and `CASE.md` + this manifest. Per the recorded cross-bag trap, a registry-first
bag without the code, or code without its test, re-creates exactly the failure this fix removes.
