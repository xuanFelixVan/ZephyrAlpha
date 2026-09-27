---
ttl: task_bound
completes_when: TEST-SOURCE-CONSISTENCY resolves source and test from the same incoming tree with red proofs landed under tests/gov_enforcement
lane: st-gate-fix
task: gate-tree-read-fix
status: done_pending_landing
turn_budget: 150
verified: asymmetry pinned by 7 sandbox git tests plus before and after runs of the tonight scenario
assumed: landing side runs this same in-process gate module and the serializer worktree index holds the bag bytes
input_set_disjoint_with: docs/01_policies_and_standards/_registry single writer coordinator
evidence_ref.cmd: python /tmp/gateproof/proof.py prefix then fixed plus pytest of four named test files
---

# CASE — TEST-SOURCE-CONSISTENCY resolved source from disk while resolving test from index

## 1. The defect as reported

Two bags died at LANDING although both the test file and the module it imported were inside the bag:

- `tests/backtest/test_chart_condition_package.py:26` —
  `from zephyr.backtest.regime_validation import chart_condition_package` reported as 符号不存在
- `src/zephyr/gov_enforcement/commit_gates/create_guard.py` + its replay test — symbols
  `_chunk_class_names` / `_attribute_class_grep_lines` reported as 不存在. Confirmed same gate:
  `create_guard.py` lives under `src/zephyr/gov_enforcement/commit_gates/`, i.e. it is a
  `zephyr.*` module, so the 符号不存在 text can only come from TEST-SOURCE-CONSISTENCY.

## 2. Fact: which face each side of the comparison was read from (pre-fix, HEAD blob)

Pre-fix file = `git show HEAD:src/zephyr/gov_enforcement/commit_gates/test_source_consistency_gate.py`.

TEST side — the incoming tree:
- line 334 `_get_staged_py_files(gateway, ...)` → `git diff --cached --name-only`
- line 368 `content = _read_staged_file(gateway, test_file)` →
  `_diff_helpers.py:262` → `gateway.run_git(["git","show",":"+path])` → **index bytes**
- line 372 `_get_added_lines` → `git diff --cached --unified=0` → **index diff**
- `run_git` default cwd = `self.project_root` (docstring `git_commit_gateway.py:4402-4403`)
  and at landing `project_root = <serializer worktree>` (
  `scripts/governance/commit_queue_landing.py:2149-2151`,
  `GitCommitGateway(project_root=self.worktree_path, registry=..., roster_root=self.repo_root)`)

SOURCE side — the process import disk:
- line 79 `_SRC_ROOT = REPO_ROOT / "src"` (REPO_ROOT frozen at import time;
  `src/zephyr/shared/io/paths.py:73-97`, `ZEPHYR_WORKTREE_ROOT` env else walk from `paths.__file__`)
- line 251 `source_file = _module_to_path(module_path)`
- lines 136-141 `py_file.exists()` / `init_file.exists()` → **disk**
- line 187 `content = file_path.read_text(encoding="utf-8")` → **disk**
- lines 280-283 submodule hatch `(pkg_dir / f"{name}.py").is_file()` → **disk**

Landing daemon imports `zephyr.*` from the main region (`roster_root=self.repo_root`, whose own
docstring at `git_commit_gateway.py:1006-1012` already records exactly this split:
「落地器场景 project_root=worktree，而 importlib 经进程 sys.path 解析到主区盘」).
Therefore at landing: test bytes = serializer worktree index (bag, new), source bytes = main region
disk (bag absent) → the gate compares **two different worlds** and calls the difference drift.

Direction of the error is always the same: any module first introduced by the bag is invisible to the
source face, so "land code and test together" — the behaviour the repo explicitly wants (§2.4 gate+own
test in one bag is legal) — is precisely the shape that dies. Recorded precedent:
`docs/_working/total_command_closeout/11_rescue_playbook.md` R-6.1 (content gates read index bytes,
not the disk) and `HANDOFF_collision_chief3.md` §五.13 (lane must be reset onto dev or
existence/symbol gates read stale bytes and report false red).

## 3. Fix (same face for both sides)

`src/zephyr/gov_enforcement/commit_gates/test_source_consistency_gate.py`:

- `_read_source_view(gateway, rel)` (line 94) — source bytes come from `_read_staged_file`
  (= index, or `git show <head_rev>:path` under the S1 immutable tree view), then HEAD.
- `_resolve_source_rel` (121) — module → tree path probed through the same face;
  `_SRC_ROOT` disk kept **only** as last-resort fallback when both git faces are empty
  (git unreachable / legacy direct unit-test calls), which is the pre-fix world, not the normal one.
- `_source_content` (140) / `_submodule_exists` (154) — content and package-submodule hatch both
  ask the tree first, disk second.
- `_symbols_from_content` (251) — symbol table extracted from **tree bytes**;
  `_extract_source_symbols(path)` kept (unchanged semantics) as the disk fallback and unit-test face.
- `_check_import_node(node, test_file, gateway=None)` + `_check_test_file(..., gateway=...)`
  take the gateway; the check closure passes it (was already available as first arg).

Discriminating power untouched: no exemption list, no symbol-matching loosening, no skip marker,
no threshold change. Index still outranks HEAD, so a rename that the test does not follow is still red.

## 4. Red proofs (repo law R-5)

Harness `proof.py` (throwaway temp dir; never touches production paths or the real queue) stages a
new module `src/zephyr/backtest/regime_validation/chart_condition_package.py` plus the test that
imports it, and points the gate's disk face at a second directory holding only the base tree
(= main region at landing).

BEFORE (pre-fix code loaded from the HEAD blob) — `python /tmp/gateproof/proof.py prefix`, exit 1:

```
TEST-SOURCE-CONSISTENCY (§5.178)：检测到测试-源码符号漂移
  测试文件 import 的符号在源码中不存在（名称漂移）。
  tests/backtest/test_chart_condition_package.py:1: from zephyr.backtest.regime_validation import chart_condition_package -> 符号不存在（源码 __init__.py 中未定义）
[prefix] gate verdict: passed=False
```

AFTER (same scenario, same disk split, fixed code) — `python /tmp/gateproof/proof.py fixed`, exit 0:

```
[fixed] gate verdict: passed=True
```

Landed as `tests/gov_enforcement/test_gate_tree_view_source_resolution.py` (7 cases, all tmp_path):

| case | expectation |
|---|---|
| `test_new_module_and_its_test_in_same_bag_passes` | tonight case ⇒ PASS after fix |
| `test_prefix_observation_face_fails_this_scenario` | pre-fix face re-computed in-sandbox ⇒ still sees 不存在 (red proof kept without pinning HEAD) |
| `test_genuine_symbol_rename_still_blocks` | test imports `foo_new`, source defines `foo_old` ⇒ FAIL |
| `test_test_in_bag_without_source_in_bag_blocks` | test in bag, source nowhere ⇒ FAIL 模块不存在 (no new escape hatch) |
| `test_index_wins_over_stale_head` | symbol exists only in stale HEAD ⇒ FAIL (HEAD is not a fallback hole) |
| `test_index_rename_matches_test_passes` | bag renames and test follows ⇒ PASS |
| `test_disk_face_is_last_resort_only` | git-face empty + disk has it ⇒ PASS (old fail-open preserved) |

## 5. Sibling survey — one side from disk, the other from index/HEAD

| gate | cite | shape | risk | action |
|---|---|---|---|---|
| TEST-SOURCE-CONSISTENCY | pre-fix 136-141/187/280-283 vs 368 | test=index, source=import-disk | hard block, false red on every new module in a bag | **FIXED here** |
| SCRIPTS-IMPORT-INTEGRITY | `scripts_import_integrity_gate.py:119` (`sys.path.insert(REPO_ROOT/scripts/governance)` + `dir(_shared.constants)`) | scanned file = staged bytes, symbol universe = imported main-disk module (and cached in `sys.modules`) | wrong direction: stale universe **under-reports** (false green), never blocks | register |
| ALGO-FLOW-LINK | `algo_flow_link_gate.py:350` `tgt.is_file()` and `:417` `(root/sot).is_file()` vs `_read` at 269 (staged first) | content=index, existence of anchor target = disk (`root`=`gateway.project_root`) | warn-only (`return True, msg` at 421) ⇒ phantom broken-anchor text when a target is index-only; no landing block | register |
| CONSUMERS-ACCURACY | `consumers_accuracy_gate.py:221-234`, `254-257` disk probe vs `455`/`498` `_read_staged_file` | consumer content = index, target existence = disk | already declared in-source (裁定#279 family, warn-only, no block power) | no action, documented exemption |
| UNDEFINED-NAME | `undefined_name_gate.py:286-293` | disk glob only inside `scan_all_for_undefined_names` = post-commit baseline (warn); the commit gate path is single-file staged content | none in the blocking path | note only |
| REGISTRY-YAML-PARSE | `registry_yaml_parse_gate.py:124-126` | reads its own mtime state cache from disk | not a compared side | note only |
| RESOURCE-SCHEDULE | `resource_schedule_gate.py:198-200`, `710-716`, `737` | helper scripts/registry loaded from `REPO_ROOT` disk, `return None` when missing | silently skips scheduling when a file is tree-only; never false-reds a bag | register (low) |
| DOC-REF-BROKEN | `doc_ref_broken_gate.py:294` uses `_repo_state_has_file`; only `:118` reads a static policy yaml | compliant already | none | reference precedent |
| RELATIVE-PATH-LITERAL | `relative_path_literal_gate.py:189` | grep false positive — the string is inside a message | none | none |

Conclusion: TEST-SOURCE-CONSISTENCY was the only **hard-blocking** gate of this class, so exactly one
gate was fixed; the rest are warn-only or fail-open in the permissive direction and are registered
rather than silently patched.

## 6. Scoped follow-up recipe (for whoever takes the registered items)

1. Per gate, replace the disk face on the *compared* side with the shared primitives already in
   `_diff_helpers`: `_read_staged_file` (content) / `_repo_state_has_file` (existence, `:369`),
   keeping disk strictly as the git-unreachable fallback.
2. For SCRIPTS-IMPORT-INTEGRITY additionally drop the `sys.path`+`dir()` universe: parse
   `scripts/governance/_shared/constants.py` with AST from the tree instead of importing it
   (`sys.modules` caching also makes the universe stale across bags in one long-lived daemon).
3. Red proof per gate, mandatory: temp repo where the file exists only in the index ⇒ gate must agree
   with the tree, not the disk; plus the inverse (index lacks it, disk has it) ⇒ behaviour pinned
   explicitly rather than by accident.
4. Do not convert warn-only gates to blocking as a side effect of the migration — that is a separate
   ruling per §5 of the constitution.

## 7. Regression runs (targeted only, no full suite)

| file | count | result |
|---|---|---|
| `tests/governance/commit_gates/test_test_source_consistency_gate.py` | 51 | 51 passed |
| `tests/gov_enforcement/test_gate_tree_view_source_resolution.py` (new) | 7 | 7 passed |
| `tests/governance/commit_gates/test_diff_helpers.py` | 58 | 58 passed |
| `tests/governance/test_commit_queue.py` | 85 | 85 passed |
| `tests/governance/test_commit_queue_landing.py` | 70 | 69 passed, 1 failed **pre-existing** |

Pre-existing red, not mine: `TestRegistryMergeCompoundIdentity::test_true_duplicate_compound_key_still_deadletters`
(`tests/governance/test_commit_queue_landing.py:1597`) fails identically after temporarily restoring the
pre-fix gate file into place (then restored the fixed file, verified by diff), so it does not come from
this change. It is a landing-side registry compound-key dead-letter expectation.

Covered surface stated explicitly (memory lesson: `glob('test_x_*.py')` misses `test_x.py`):
`grep -rl test_source_consistency tests/` returns exactly one pre-existing test module
(`tests/governance/commit_gates/test_test_source_consistency_gate.py`, note the doubled `test_test_`
prefix that a `test_source_*` glob would miss) plus the new file. Both were run by full path.
`_diff_helpers.py` was NOT modified, so its 41 importing gates are unaffected by construction;
the helper suite was run anyway. Queue behaviour is exercised by the two queue files above;
no gate-registry YAML was regenerated (none of the registry fields for this gate changed:
same gate_id, same priority=102, same own_scope marking).

## 8. Not done / needs the coordinator

`docs/01_policies_and_standards/_registry/**` untouched (single writer). See
`register_manifest.md` next to this file.
