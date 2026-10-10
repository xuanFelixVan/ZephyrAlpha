---
case_id: st-p17-storage
title: storage-decision dossier for four file-authorities
owner_rule: this decision is not agent-approvable beyond analysis
ttl: task_bound
completes_when: CASE.md carries four fully specified options plus external practice mapping plus flip-evidence table plus safe-first-step sequencing plus the Option0-or-1 case
turn_budget: 150
turns_used_at_completion: 45
verified: F1 through F12 including 22 path bindings and 14 gate path sites and guard mechanisms read directly
assumed: tasks row count and the 17 percent under-record figure and the three-bag retirement narrative
input_set_disjoint_with: docs/_working/total_command_closeout
evidence_ref:
  cmd: grep -n _CANONICAL_KEYS scripts/governance/d3_metadata/add_module_translation.py
  cmd2: grep -n LOCK_ROOT scripts/lock_files.py
  cmd3: sed -n 98,108p src/zephyr/governance/registry_projection/state.py
  files:
    - scripts/governance/d3_metadata/add_module_translation.py
    - scripts/lock_files.py
    - src/zephyr/shared/io/paths.py
    - src/zephyr/security/access_control/session_concurrency.py
    - src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py
    - src/zephyr/governance/registry_projection/state.py
    - src/zephyr/library/library_regen_reconciler.py
status: complete
scope_note: the two master books under total_command_closeout are held by another live lane and are OFF LIMITS; this campaign lands only under three_piece_infra and is marked pending merge-back
---

# Storage decision dossier (RESEARCH + DESIGN ONLY)

Status: IN PROGRESS. Section order is fixed so later edits are append/replace only.

## 0. Standing rules recorded up front

- Owner standing rule: this storage decision is NOT the executing agent's and NOT the
  reviewer's to self-approve. Authority here is analysis only. Any cutover needs the
  Owner's gate (AGENTS.md section 5 high tier - registry net deletion and production
  flow are Owner gates).
- Off-limits: `docs/_working/total_command_closeout/**` is currently held by another live
  lane. Nothing in any option below proposes editing those master books.
- This dossier lands in `docs/_working/three_piece_infra/storage_decision/` with a written
  pending-merge-back note. No commit, no add, no enqueue, no DB write, no migration, no
  process kill performed or proposed as a side effect of this study.

## 1. Subject: the four file-authorities

| # | authority | today | stated scale |
|---|-----------|-------|--------------|
| A1 | capability_canonical_file_registry.yaml | YAML file | rows about 11.5k tokens |
| A2 | module_translation_registry.yaml | YAML file | about 7.8k entries |
| A3 | .ailocks/registry.json + .runtime/session_registry.json | two JSON files | live lock and session state |
| A4 | trial ledger | file | under-recorded about 17 percent |

## 2. Observed pains (to be verified against code)

1. Whole-file snapshot in a commit bag -> concurrent writer collision; queue retires the
   staler bag (`cascade_stale`); three such bags retired back-to-back one night.
2. Per-worktree lock files -> lanes cannot see each other's claims; a coordinator was
   judged dead by its own heartbeat while working; live cause of a duplicate
   general-contractor appointment.
3. Trial ledger under-records about 17 percent because the recording function is not called.

## 3. Findings (all verified by reading code in the main workspace)

### F1 The two "files" are not single-key-space files — they are multi-tenant containers

Measured on disk (main workspace, 2026-09-27):

| file | bytes | top-level data sections (line of section key) |
|------|-------|------------------------------------------------|
| `capability_canonical_file_registry.yaml` | 2,953,814 | `capabilities:` L13, `creation_tokens:` L5145, `di_seam_exemptions:` L53419 |
| `module_translation_registry.yaml` | 3,623,035 | `entries:` L33, `battle_map_steps:` L61303, `battle_map_cross_cutting:` L65730, `algo_submodules:` L66589 |

Consequences that the brief did not state and that change every option:

- The **hottest writer** in the capability file is not the capability index at all. It is
  `creation_tokens`, written by the CREATE-GUARD toolchain for *every new file*
  (`scripts/governance/d3_metadata/batch_creation_tokens.py`). It shares one 2.95 MB blob with
  a cold capability index. So **splitting by section is available today and is nearly free**,
  while "split by top-level source directory" is not even well defined for these files.
- `module_translation_registry.yaml` is keyed by **three different key spaces**:
  `module_path` (entries), `step_id` (battle_map_steps, e.g. `BM-BUY-04`),
  `category` (battle_map_cross_cutting, e.g. `funnel`). Verified in
  `scripts/governance/_shared/module_translation_loader.py:139` (module_path),
  `:577-588` (step_id), `:757-764` (category). Any directory-based shard must not disturb
  the latter three sections — they are not per-directory at all.
- Both files are declared hot in `src/zephyr/shared/io/file_utils.py:412-418`
  (`DEFAULT_HOT_FILES` includes both, lines 415 and 417) — so both already go through
  `safe_write_text` CAS.

### F2 The `add_module_translation` clobber is real, and its exact mechanism is narrower than "overwrite"

- Required fields are only four: `module_path, domain_id, name_zh, plain_zh`
  (`add_module_translation.py:499`).
- Canonical field list has seven: `module_path, domain_id, name_zh, name_en, desc_zh, desc_en, plain_zh`
  (`add_module_translation.py:224-232`).
- `_upsert_entry` merges old values into the new entry **only for keys that are NOT canonical
  and NOT derived** (`add_module_translation.py:410-416`, the skip is `if k in _CANONICAL_KEYS or k in _DERIVED_KEYS: continue`).
- `_format_entry_block` then emits **every** canonical key unconditionally with
  `entry.get(k, "")` (`add_module_translation.py:294-300`).
- Therefore: an upsert that omits `name_en` / `desc_zh` / `desc_en` writes those three as empty
  and **silently destroys previously registered text**. Extension (non-canonical) keys were
  already fixed against exactly this by ruling 335
  (`add_module_translation.py:289-292`, "旧版固定 7 行输出即字段吞噬器"). The canonical seven
  were left unprotected — the fix was applied to the wrong field set.
- The correct merge semantics **already exist in the same file** but only on the `--dedupe`
  path: `_merge_duplicate_blocks` (`add_module_translation.py:575-587`) keeps the highest-info
  entry and fills empty fields from the losers.
- Read side masks the damage: `module_translation_loader.py:146-152` arbitrates duplicates by
  info score, so a lossy write is not visible in queries even though the file has lost data.

### F3 The brief's item "make the token tool refuse to re-register an existing path" is ALREADY DONE

- `batch_creation_tokens.py:96-107` `scan_unregistered()` = tracked ∪ untracked **minus** already
  registered; `:109-113` `load_registered()` returns the set of `file` values from `creation_tokens`;
  `:503-508` refuses with "无待登记文件（全部已登记或前缀为空）".
- Additionally a wide-prefix foolproof exists at `:521-535` (W4, after the emomine 481-entry
  mis-scan on 2026-09-22).
- Residual gap is **not** the CLI: it is direct YAML edits of `creation_tokens` that bypass the tool.
  Do not sell this as a win in Option 0; it is already banked.

### F4 Claim visibility across worktrees — one of the two registries is already fixed, the other is not

- `src/zephyr/shared/io/paths.py:84-97`: `REPO_ROOT` is deliberately **worktree-aware**
  (env `ZEPHYR_WORKTREE_ROOT` wins).
- `paths.py:100-116` `strip_session_worktree()` and `:121` `MAIN_REPO_ROOT` = always main repo.
- `paths.py:206-214` documents the precedent verbatim: `DB_PATH` was re-anchored to
  `MAIN_REPO_ROOT` because "worktree 进程与主仓进程读写同一份" — the identical bug class.
- `paths.py:178` `anchor_main_root()` is the canonical utility (gitdir-pointer based; covers
  `.worktrees`, `.aidrafts`, `commit_queue` landing worktree, nested sandboxes).
- **Session registry is already main-anchored**:
  `src/zephyr/security/access_control/session_concurrency.py:290-315` —
  `SessionRegistry.__init__` calls `anchor_main_root(root)`, and the comment records that
  missing this caused `SESSION-REQUIRED` false reds (#ARCH-324).
- **File claims are not**: `scripts/lock_files.py:97` `LOCK_ROOT = REPO_ROOT / ".ailocks"` →
  `.ailocks/registry.json` (LOCK_ROOT L97, REGISTRY_PATH L101) is per-worktree.
- So the two claim registers disagree, and `lock_files.py:873` itself says both must be released
  ("两处都要放"). This is the concrete, verified mechanism behind "lanes cannot see each other's claims".
- Windows concurrency note: `lock_files.py:104-106` — 26 concurrent read-modify-write of
  `registry.json` lose locks, hence a global named Mutex. Any shared claim store inherits that
  requirement; it is already solved there.

### F5 Liveness is heartbeat-derived and decoupled from work — the duplicate-general-contractor mechanism

- `session_concurrency.py:152` `_HEARTBEAT_TIMEOUT_SECONDS = 90`; `:169`
  `_ACTIVITY_IDLE_TIMEOUT_SECONDS = 1800`.
- `session_concurrency.py:8` and `:227` / `:290-298`: `last_activity` is refreshed **only** by real
  governance operations (`register` / `claim_file` / `register_dependency`); **heartbeat does not
  refresh it**. The daemon auto-exits after 1800 s idle, and 90 s later the registry entry is
  judged dead and `held_files` are released automatically.
- Net effect: a lane that is *working* (computing, verifying, writing docs) but not *claiming*
  for 30 minutes is declared dead by its own liveness design, and its claims are released under
  it while it keeps running. Another lane can then claim the same file and the appointment
  decision can be made twice. There is no token that invalidates the ex-lease holder's later
  write — this is precisely a missing **fencing token**.
- `is_alive` logic: `session_concurrency.py:274-291` (pid>0 uses PID liveness + TTL 3600 s;
  pid=0 logical session uses heartbeat freshness only).

### F6 Why bags collide, and why the queue retires instead of rebuilding

- `scripts/commit_queue.py:1368-1389` `_mark_cascade_stale`: after item X lands, every pending
  item whose `meta.depends_on` contains X, **or whose `base_head` equals X's `base_head`**, is
  marked stale by a shadow file. On dequeue, `_revalidate_stale_base` re-checks; if the base is
  no longer valid the item is demoted to dead-letter with `dead_reason=cascade_stale`
  (`:1704-1717`, catalogue entry `:2372`).
- Bags are **append-only and never rewritten**: `:1378-1379` "袋 JSON 零改写（append-only 不变量）".
  So there is no rebase-and-rebuild path — which is exactly what a merge queue does and what this
  repo does not. Three same-base bags carrying snapshots of one registry will therefore retire
  two of three.
- Base re-validation is done against git blobs:
  `scripts/governance/commit_queue_landing.py:1672-1673` and `:1698-1701`
  (`git cat-file -e <base>:<rel>`, `_read_blob_text_opt`).

### F7 The three guards named in the brief all diff git blobs — verified

- `REGISTRY-MASS-DELETION` (`src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py`):
  `git diff --cached --name-only --diff-filter=AM` (`:214`), `git show HEAD:<rel>` (`:248`),
  `_read_staged_file` = `git show :path` (`:62` import of `_diff_helpers`),
  `difflib.SequenceMatcher` over HEAD lines vs staged lines (`:112-125`), plus a third signal
  that is a **set difference of entry identities HEAD-side minus staged-side** (`:32`, `:154-165`).
  Registered `own_scope: true`, priority 140
  (`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml:1589-1599`).
  Its raison d'être is recorded in its own INVARIANTS: a 2026-09-09 near-evaporation of 4703 lines.
- `HOT-FILE-BASE-FRESHNESS` (`hot_file_base_freshness_gate.py:20-58`): compares the HEAD anchored
  at claim time (`claim_head`) with current HEAD via
  `git diff --name-only claim_head..HEAD -- <file>` (`:47`). It exists *because* `safe_write_text`
  CAS cannot see the case where disk bytes never changed but HEAD moved under you (`:31-36`).
- Own-scope diffing (`_diff_helpers.py:26-32, 262-312`): `_read_staged_file` = `git show :path`,
  `_get_staged_py_files` = `git diff --cached --name-only`, plus an immutable-tree view proxy (`:31`).
- `_capability_registry_io.py:57-101`: six gate processes reading the same 2.95 MB file converge
  to one `yaml.safe_load` (single 3.6-4.2 s parse; measured 2.16 s to 0.2 ms on cache hit), keyed
  by `(normcase path, mtime_ns, size)`. Important for Option 1: **parse cost is already solved**,
  so sharding buys merge hygiene, not speed.

### F8 PostgreSQL precedent — real, but the brief's specifics are partly wrong

- PG is genuinely used, and **the repo already uses PG advisory locks for registry-ish writes**:
  `scripts/governance/apply_depgraph.py:93` (`import psycopg2`), `:211-212`
  (`SELECT pg_advisory_lock(424242)` / `pg_advisory_unlock`), `:547-551`, `:2638`.
  Library is PG-backed: `src/zephyr/library/librarian.py:62` (`PgConnection` duck-type protocol),
  `:108` (psycopg2 connection). Config exists: `config/.env.postgres`
  (`POSTGRES_HOST/PORT/DB/USER/PASSWORD` plus separate `POSTGRES_READER_*`).
- **Premise correction**: the `tasks` table is **SQLite**, not PostgreSQL —
  `src/zephyr/governance/persistence/task_repo.py:78` (`import sqlite3`), `:92`
  (`sqlite_schema.get_db_connection/init_db`), `:166` (`sqlite_master`), `:1055-1056`
  (`sqlite3.Row` to TaskCard, "含全部 62 字段"). The brief's "73 columns / PG" is not what the code says.
- **Premise confirmed**: the state machine is exactly 14 states and COMPLETED vs VERIFIED are
  distinct, with VERIFIED terminal:
  `src/zephyr/gov_enforcement/rule_enforcement/task_types.py:63-84`
  (PENDING, CREATED, LOCKED, ASSIGNED, READY, IN_PROGRESS, REVIEWING, COMPLETED, VERIFIED, FAILED,
  BLOCKED, WAITING, RETRY, CANCELLED); transitions
  `task_repo.py:43-44` (`COMPLETED -> VERIFIED, IN_PROGRESS`; `VERIFIED -> terminal, no out-edges`);
  `COMPLETED` requires 2 consecutive zero-error acceptance rounds
  (`task_repo.py:8` `CIRCULAR_ACCEPTANCE_ROUNDS=2`). Row count 2546 not verified (no DB query run —
  study-only, memory pressure); treat as assumed.

### F9 The half-finished-migration precedent is worse than described: 7 zero-byte DBs

Measured `find data -maxdepth 2 -name "*.db" -size 0`:
`data/zalpha_metadata.db`, `data/databases/depgraph.db`, `data/databases/integrator_progress.db`,
`data/databases/progress.db`, `data/databases/scheduler_progress.db`, `data/depgraph.db`,
`data/runtime/progress.db` — **7**, all zero bytes.

Live pointers into the dead one:
- `scripts/governance/d5_architecture/validators/validate_cross_references.py:225`
  `db_path = REPO_ROOT / "data" / "zalpha_metadata.db"` — a validator whose subject is a 0-byte file.
- `src/zephyr/infrastructure/rollback/sqlite_dumper.py:532` — `SELECT schema_version FROM zalpha_metadata`.
- `src/zephyr/infrastructure/asset_inventory/registry_adapter.py:37` — "SqliteAdapter reads governance.db (zalpha_metadata.db)".
- `src/zephyr/shared/api/shared_quickref.yaml:149` — documented as `data/zalpha_metadata.db`.
- `src/zephyr/governance/persistence/database_manager.py:569-623, :790` — still mints backups named
  `zalpha_metadata_*.db`, and `:790` records that this naming is the source of 85% of 118 leftover .db files.

### F10 Option 3 is not hypothetical — the repo already built it, for exactly this file

`src/zephyr/governance/registry_projection/` (`__init__.py`, `model.py`, `pg_source.py`,
`projection_generator.py`, `renderer.py`, `state.py`) plus
`scripts/governance/registry_projection/registry_projection_generator.py`, created 2026-09-23
(W-M1 lane B). Its own INVARIANTS (`__init__.py:8-10`):

- "YAML := render(PG 账本快照) 单向投影：生成器是投影册唯一合法写者，读端零改动
  （11 读端继续读本地 YAML，永不触 PG——丙号文支柱③）"
- Enforcement hooks: `REGISTRY-YAML-PARSE` gate extension (own-scope) + belt daemon `registry_drift`.
- `projection_generator.py:72-80`: management register is `REG-CAPCAN-001` — the capability
  registry — and its physical path is resolved through ROOR, with the invariant
  "禁 .py 硬编码 SSoT 路径".
- `state.py:98-108` `classify(disk_sha, state_sha, render_sha)` → four quadrants:
  CLEAN / PRIVATE_EDIT (state==render but disk differs) / STALE (disk==state but render differs) /
  CONFLICT; and it degrades to D-vs-S only when PG is down, so hand edits still surface.

That is a textbook implementation of "single writer + regeneration + drift guard". **The decision is
therefore not "invent Option 3" but "does the existing W-M1 projection actually land, and does it cover
the other three authorities".**

### F11 The projection's known defect is structural, and it is documented in the library case

`src/zephyr/library/library_regen_reconciler.py:8` INVARIANTS, verbatim:
"馆页/对账报告为生成视图（**gitignore 面**），提交仍走人工批".
The library reconciler is event-triggered on post-commit (`:17-22`, `:38` trigger = library input
surface `src/scripts/data/catalogs`), regenerates pages, and is fail-soft
(`:8` "全程 fail-soft（单步失败降级 warn 不抛）"; `:13` "reconcile 永不抛异常").

So: generation is automatic, **landing is deliberately manual**, failure is deliberately silent.
A projection under that contract can regenerate perfectly forever and never appear in the repo —
which is exactly the 4-day-stale symptom. This is the defect Option 3 must fix, not an argument
against Option 3.

### F12 One more git-only protection the brief did not list

`RULING-COMMIT-VERIFIED` (`src/zephyr/gov_enforcement/commit_gates/ruling_commit_verified_gate.py:22, :193, :265`,
priority 109) hard-verifies that a document's claim "已完成（commit XXX）" references a commit hash
that actually exists. Any authority that leaves git loses the ability to make such a claim at all.

## 4. Option 0 - keep files, fix the writer

### 4.1 What changes (four items, one of them already banked)

1. **`add_module_translation` upsert becomes a merge, not a replace.**
   In `_upsert_entry` (`add_module_translation.py:402-417`), seed the seven canonical fields from
   the existing matched block before formatting, i.e. drop the `_CANONICAL_KEYS` exclusion at
   `:413` for the *fill-empty* direction only, reusing `_merge_duplicate_blocks`
   (`:575-587`) semantics that already exist. Add a stricter rule: a canonical field that is
   non-empty on disk and empty in the incoming entry must be either preserved or refused loudly —
   never silently blanked. Cost: ~15 lines in one function + one test in
   `tests/governance/d3_metadata/test_add_module_translation.py`. **This is the highest value /
   lowest cost item in the whole dossier.**
2. **Token re-registration refusal — already implemented; do not re-sell it.** Verified at
   `batch_creation_tokens.py:96-108, 503-508`. If the pain is still being observed, the cause is
   writes that bypass the CLI, i.e. direct YAML edits. The correct closing move is to make
   `REGISTRY-YAML-PARSE` / `CREATE-GUARD` reject a `creation_tokens` entry whose `file` already
   exists — a check on the *diff*, not a new tool.
3. **Claims visible across worktrees without a database.** One-line-class change with precedent:
   `scripts/lock_files.py:97` `LOCK_ROOT = REPO_ROOT / ".ailocks"` → anchor to the main repo, using
   the existing `anchor_main_root()` (`paths.py:178`) or `MAIN_REPO_ROOT` (`:121`), exactly as
   `DB_PATH` (`paths.py:206-214`) and `SessionRegistry` (`session_concurrency.py:290-315`) already do.
   The session registry is already shared; only `.ailocks` is not, so this closes the F4 split.
   Keep the existing Windows named Mutex (`lock_files.py:104-106`) — it becomes more load-bearing,
   not less.
4. **Liveness stops being an inference.** Two sub-parts, no DB:
   (a) refresh `last_activity` on evidence of real work, not only on claim operations — the current
   asymmetry is `session_concurrency.py:227` and is what kills a working lane;
   (b) add a **fence token**: a monotonically increasing `lease_epoch` per session in
   `session_registry.json`, bumped whenever a claim set is reassigned, and written into every commit
   bag + every hot-file claim. A writer whose `lease_epoch` is below the recorded maximum is refused
   at the gateway instead of silently merged. That converts "judged dead while alive" from a data-loss
   event into a retryable denial, and it is the specific fix for the duplicate general-contractor
   appointment (F5).
5. **Trial ledger: call the recorder at the boundary that cannot be skipped.**
   `TrialLedger.record_run` (`src/zephyr/backtest/core/n_trial_ledger.py:332`) has **exactly one**
   non-test caller, `scripts/backtest/reexam_cpcv_harness.py:327`. The main grid path,
   `scripts/backtest/factory_grid_executor.py`, only calls `set_effective_trials` (`:863`);
   `sync_screen_counts` is called from `scripts/backtest/c4_batch_screen.py:417`. So under-recording
   is a **call-graph fact, not a storage fact**. Fix = record inside the executor(s) that produce
   trials, and/or a gate that fails when a landed grid run has no ledger entry. Changing storage
   changes nothing here.

### 4.2 Blast radius

- Item 1: one function, one test file. Consumers unaffected (read side already tolerates both).
- Item 3: `lock_files.py` (1659 lines) plus every reader of `.ailocks/registry.json`. Grep the
  literal: `scripts/lock_files.py:97,101,306,308,317,324`; `lock_files.py:855, 873, 919, 930, 996-998,
  1037, 1130, 1171` treat `.ailocks` and SessionRegistry as two registers. Highest-risk item: it
  changes the concurrency *model* (see 4.4).
- Item 4b: `session_registry.json` schema + `git_commit_gateway` / `commit_queue` bag metadata +
  `--adopt-prior-work` semantics (AGENTS §2.3). Needs a ruling number (RULE-RULING).
- Item 5: backtest executors; no governance coupling.

### 4.3 Protections kept / lost

All eleven protections in F7/F12/F10 are kept untouched. Nothing is lost. This is the only option
with a zero-protection-loss profile.

### 4.4 What this fixes, and what it plainly does NOT fix

- **Fixes**: silent text destruction in the translation registry (F2, real and reproducible by reading);
  cross-lane claim blindness (F4); liveness killing a working lane and allowing a double appointment
  (F5, with a fence token); trial under-recording (F12/4.1.5 — orthogonal to storage anyway).
- **Does NOT fix**: **whole-file bag collision.** Two lanes that each snapshot the whole 2.95 MB or
  3.62 MB file still produce two bags with the same `base_head`, so `_mark_cascade_stale`
  (`commit_queue.py:1368-1389`) still marks and `cascade_stale` still retires. CAS makes the loss
  *impossible*; it makes the *collision* *certain*. Under Option 0 the nightly retirements continue
  and the cost is re-registration labour, not corruption. State this to the Owner plainly.
- **New risk introduced by item 3**: shared claims means two lanes that would have worked in parallel
  on the same registry file now deny each other *before* editing. That is arguably better (fail early
  instead of retire late) but it is a throughput/serialisation decision with a merge-model
  consequence — it is an Owner gate, not an engineer call.

### 4.5 Migration and rollback

No data migration. Land behind a flag; rollback = revert commit. For item 3, rollback must also
re-release claims that moved to the shared store (use `gateway.release_files('<sid>', files)`,
AGENTS §2.7).

### 4.6 Cost (engineer-hours, honest)

| item | hours |
|------|-------|
| 1 merge-on-upsert + test | 3-5 |
| 2 diff-level duplicate-token check | 3-4 |
| 3 shared claim store | 8-12 (incl. concurrency tests on Windows Mutex) |
| 4a activity refresh | 2-3 |
| 4b fence token end-to-end | 14-20 |
| 5 ledger call at executor boundary + guard | 6-10 |
| **total** | **36-54** |

## 5. Option 1 - shard the files

### 5.1 What changes

Two distinct shardings, and the cheap one is not the one the brief described:

- **1a. Split by section (recommended if any sharding is done).**
  `creation_tokens` out of the capability file (its own register), and
  `battle_map_steps` / `battle_map_cross_cutting` / `algo_submodules` out of the translation file.
  These are already separate key spaces with separate loaders
  (`module_translation_loader.py:556-591`, `:734-766`), so a bag touching `creation_tokens` and a bag
  touching `capabilities` stop colliding. This alone removes the hottest write from the 2.95 MB blob.
- **1b. Split `entries` / `capabilities` by top-level source dir family**
  (e.g. `catalogs/capability_registry/src__zephyr__trading.yaml`). Only meaningful for the two
  big *append-mostly* sections.

### 5.2 Enumerated hardcoded paths (the count the brief asked for)

True path-construction sites in Python (comments, docstrings, and gate *message strings* excluded):

- capability registry — **14 sites**:
  `src/zephyr/governance/capability_lookup.py:103`;
  `src/zephyr/gov_enforcement/commit_gates/create_guard.py:569`;
  `src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py:90` (watch-list dict key);
  `src/zephyr/gov_enforcement/commit_gates/secret_hardcode_gate.py:104` (exemption list);
  `src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py:170` (`_CAPABILITY_REGISTRY_REL`);
  `src/zephyr/shared/io/file_utils.py:415` (`DEFAULT_HOT_FILES`);
  `scripts/governance/architecture_health_dashboard.py:127`;
  `scripts/governance/d3_metadata/batch_creation_tokens.py:74`;
  `scripts/governance/d6_security/detect_git_dangerous.py:84`;
  `scripts/governance/d8_doc_sync/metric_count_drift_reconciler.py:86` and `:260`;
  `scripts/governance/generate_project_depgraph.py:3075`;
  `scripts/governance/meta/validate_rules_integrity.py:124`;
  `scripts/scaffold.py:103`.
- module_translation registry — **8 sites**:
  `scripts/governance/d3_metadata/add_module_translation.py:113`;
  `scripts/governance/d5_architecture/generators/generate_domain_doc.py:1918`;
  `scripts/governance/d8_doc_sync/algo_flow_translation_reconciler.py:93` and `:360`;
  `scripts/governance/oneoff/fix_module_translation_zh.py:44`;
  `scripts/governance/oneoff/_fix_remaining_en.py:33`;
  `scripts/governance/_shared/algo_flow_translation_sync.py:47`;
  `scripts/governance/_shared/module_translation_loader.py:78`.
- Total **22 live path bindings**, plus broad textual references (52 Python files mention the
  capability name, 38 mention the translation name — most are prose/messages that keep working,
  but 3 gates carry the filename in the *user-facing violation message*, e.g.
  `ssot_redefinition_gate.py:218`, `create_guard.py:706,722`, which become wrong advice).
- Non-Python: no machine-readable binding found outside the two files themselves; the many
  `architecture_issue_registry.yaml` hits are historical prose, not paths.
- The repo already has the right indirection and says so: `projection_generator.py:73-79` resolves
  the path from **ROOR** with the invariant "禁 .py 硬编码 SSoT 路径". Sharding should therefore go
  through ROOR rather than editing 22 constants — but ROOR itself becomes a hot file (see 5.4).

### 5.3 Failure modes (stated as asked)

1. **Cross-shard uniqueness becomes a join.** `capability_id` and `module_id` uniqueness is today
   checkable inside one file. Sharded, a duplicate can hide across two shards and *every* current
   checker is per-file: `module_translation_loader.py:146-152` dedups inside one `entries` list;
   `_merge_duplicate_blocks` (`add_module_translation.py:575-587`) is likewise per-file;
   `add_translation` post-write verification counts hits in one file (`:545-556`). A new
   cross-shard uniqueness pass is mandatory, and it must run in a gate, which means it must be
   cheap — the opposite of what `_capability_registry_io.py` was built to avoid (six gates, one
   2.95 MB parse).
2. **The deletion-count guard loses its denominator.** `REGISTRY-MASS-DELETION` computes
   `deleted > added` per file and compares YAML entry counts HEAD vs staged
   (`registry_mass_deletion_gate.py:258-262`) plus an entry-identity set difference (`:32`).
   Sharded, a whole shard deleted looks like *one file* of net deletion, and a legitimate shard
   rebalance looks like mass deletion in that shard only. It needs either (a) a registered total
   denominator across shards, or (b) per-shard thresholds that are *derived*, not hand-set — and
   hand-set denominators violate the repo's own rule against statically maintained lists
   (AGENTS §9.5). Note also `create_guard.py`'s wide-prefix W4 foolproof is prefix-based
   (`batch_creation_tokens.py:521-535`) and would silently widen under sharding.
3. **Hot-file list, exemption lists and watch lists must all grow per shard**: `file_utils.py:415,417`
   (DEFAULT_HOT_FILES), `secret_hardcode_gate.py:104`, `registry_yaml_parse_gate.py:51,90`
   (`_WATCH_FILES`), `commit_preflight.py:170`, `lock_files.py` reclaim surface.
4. **ROOR + registry_of_registries becomes the new single point of contention** — a 23rd hot file
   that every shard registration must touch, i.e. the collision returns in a smaller body.
5. **Docs and provenance rot**: `docs/03_modules/**/blueprint.md`, `docs/library/rule.md`, AGENTS §6.2
   and the `capability_canonical_file_registry.yaml` name embedded in violation messages all
   teach a path that no longer exists.
6. **Reader fan-out**: the 11 readers named by `registry_projection/__init__.py:9` become 11 readers
   x N shards; `preload()` (`module_translation_loader.py:345-350`) and the shared parse cache
   (`_capability_registry_io.py:57-101`, a **single-entry** cache, `_PARSE_CACHE = {"key": None, "data": None}`)
   degrade badly — a single-entry cache with N shards thrashes on every shard switch. That is a real
   regression, because the cache is explicitly one-slot.

### 5.4 Migration steps

1. Add a shard-manifest register (generated, never hand-maintained — AGENTS §9.5).
2. Land a *reader* that unions shards, keep the old path as an alias; verify byte-identical
   union vs the pre-split file (`canonicalize` in `registry_projection/model.py` already does
   comparable normalisation).
3. Cut writers over to shard-addressed writes; one shard per writer call.
4. Delete the monolith only after the cross-shard uniqueness gate is green for a full cycle.
5. Rebuild depgraph (`generate_project_depgraph.py --force`, RULE-DEPGRAPH / AGENTS §9.10) and re-run
   `alignment_checklist` / `align_all.py` because module paths changed.

### 5.5 Rollback

Keep the monolith in git; a `merge-shards -> monolith` generator plus a recorded sha of the last
good monolith. Rollback = restore monolith + flip readers back. Clean only because nothing else
changes; must be tested *before* cutover, not after.

### 5.6 Cost

- 1a (section split): **24-40 h** — 22 path bindings minus those that don't apply, the union
  reader, the watch/hot/exemption lists, plus cross-shard uniqueness.
- 1b (directory shards): **70-110 h** — and it must also fix failure mode 1 (join), 2 (denominator)
  and the single-entry cache regression in 5.3.6. 1b is the expensive one and is *not* the one that
  removes the hottest writer.

## 6. Option 2 - move to PostgreSQL

### 6.1 What changes

Rows replace lines: `INSERT/UPDATE/DELETE` per entry; the YAML authority is deleted; readers query PG.
Concurrency control is genuinely available and the repo already does it:
`apply_depgraph.py:211-212, 547-551` (`pg_advisory_lock(424242)`). Row-level writes do end the
whole-file snapshot collision, and would end `_mark_cascade_stale`
(`commit_queue.py:1368-1389`) firing on registry bags, because a registry bag stops existing.

### 6.2 What is LOST — the file-only protections, item by item

1. **Git-pinned auditability.** `REGISTRY-MASS-DELETION` reads `git show HEAD:<rel>`
   (`registry_mass_deletion_gate.py:248`) and `git show :path` for staged
   (`:62` via `_diff_helpers.py:262-270`). Its entry-identity signal is literally
   "HEAD-side identity set minus staged-side set" (`:32`). With rows there is **no HEAD-side set**;
   the guard degenerates to a trigger that logs deletes. The 4703-line evaporation it was written
   for (INVARIANTS, `:8`) is exactly the accident a logged delete does not stop, because a delete
   that is legal today is legal tomorrow too.
2. **Base freshness / stale-snapshot detection.** `HOT-FILE-BASE-FRESHNESS` compares
   `claim_head..HEAD` per file (`hot_file_base_freshness_gate.py:47`) and exists precisely because
   CAS cannot see "disk bytes unchanged, HEAD moved" (`:31-36`). A DB has no HEAD. Row-level
   optimistic versioning protects a *single row write* but has no equivalent for
   "my derived decision was computed against a snapshot that is now two commits old".
3. **Own-scope diffing / guilt-by-not-my-diff.** `_diff_helpers._build_own_scope`,
   `_get_staged_py_files` = `git diff --cached --name-only` (`:280-312`), `_read_staged_file`,
   `_is_cosmetic_only_change`. AGENTS §3.1-3.3 makes own-scope the *default* for content-scanning
   gates; `gate_registry.yaml` carries `own_scope: true` per gate (e.g. `:1598`). A DB write has no
   diff, so the whole "foreign staged violation = warn, not block" innocence mechanism
   (`_audit_foreign_staged`) loses its basis. This is the single biggest systemic loss — it is not
   one gate, it is the *scoping doctrine* of the entire gate system.
4. **Revert-to-rollback.** AGENTS §0/§切换记录: the constitution's own stated rollback is
   `git revert`. Registry history is currently `git log -- <file>`. With rows, rollback needs
   backups, and F9 shows the repo's backup hygiene track record (7 zero-byte DBs, 118 leftover
   `zalpha_metadata_*.db`, `database_manager.py:790`).
5. **RULING-COMMIT-VERIFIED** (`ruling_commit_verified_gate.py:22,193`): a claim "done (commit XXX)"
   becomes unformalisable for DB-resident state; there is nothing to point at.
6. **Review-as-concurrency-control.** A YAML diff is reviewable line by line; a row set is not.
   See §8 registry-as-code.
7. **A DB row can be exactly as false as a YAML line.** Nothing in Option 2 improves *truth*.
   It improves *concurrency of writing falsehoods*. The real truth defects found in this study —
   F2 (silent field loss), F5 (liveness inference), F12/4.1.5 (recorder with no caller) — are
   **call-graph and semantics bugs** that survive any storage choice. Note the repo's own census
   finding in the same class: guards that exist but are never called are decoration.

### 6.3 The rule that prevents repeating the dead-pointer precedent

State it as a law, because `data/zalpha_metadata.db` (0 bytes, still pointed at by
`validate_cross_references.py:225`, `sqlite_dumper.py:532`, `registry_adapter.py:37`,
`shared_quickref.yaml:149`) is the counter-example:

> **No-pointer-orphan rule.** A path or DSN may be referenced by code only while the referent is
> provably live *and* the reference is resolvable through a register (ROOR). The migration unit is
> not "new store exists", it is **writer cut over + all readers cut over + old pointer deleted + a
> gate that fails when a referenced store path is 0 bytes or absent** — landed in the *same* commit
> bag. Until that bag lands, the old file stays authoritative. A migration may not be "half done"
> in the trunk; a half-done migration is a regression, not progress.
> Mechanically: extend `validate_cross_references.py` into a gate (it is already a validator with a
> 0-byte target — the fix is to make it *enforce*, not merely to exist), asserting every registered
> store path exists, is non-zero, and matches its declared engine.

### 6.4 Migration steps

1. Schema + row-level version column; keep advisory-lock single-writer discipline
   (`apply_depgraph.py:211-212` precedent).
2. Dual-read from day one (PG primary, YAML mirror regenerated).
3. Re-implement the four guards of 6.2 as *ledger-history* guards over a PG history table with
   snapshots pinned to commit shas — i.e. rebuild git's properties, at which point see §7:
   you are one step from Option 3 and you should stop and prefer Option 3.
4. Cut writers, then readers, then delete the monolith and every one of the 22 path bindings (§5.2).
5. ROOR + `alignment_checklist` + depgraph rebuild.

### 6.5 Rollback

Reverse dual-read: YAML becomes authoritative again, PG becomes the mirror. Only safe if the YAML
mirror was regenerated continuously *and landed*. If it was not (F11), rollback is data loss —
this is the honest reason Option 2's rollback story is worse than Option 3's.

### 6.6 Cost

**160-240 h** for the four authorities, dominated by re-implementing 6.2 items 1-5 and re-testing
the gate doctrine. Plus an operational dependency the repo must then survive: PG down. Today PG
outage degrades the library/depgraph; making registries PG-primary moves *commit gating* into
PG's availability envelope. `registry_projection/state.py:100-101` already chooses degradation
over coupling for the projection ("render_sha=None（PG 宕机）时降级只比 D vs S") — a deliberate
design that Option 2 would have to reverse.

## 7. Option 3 - hybrid, minimal-cutover

### 7.1 It already exists — scope the decision correctly

`src/zephyr/governance/registry_projection/` implements exactly "state in PG, file is a generated
projection, single legal writer, drift guard", targeted at `REG-CAPCAN-001`
(`projection_generator.py:72-80`) with `11 读端继续读本地 YAML，永不触 PG`
(`__init__.py:9-10`). So Option 3 for A1 is a **completion** question, not a design question.
The four requirements, each already having a repo answer:

1. **Single writer** — enforced by construction: "生成器是投影册唯一合法写者"
   (`__init__.py:9`) + advisory lock precedent (`apply_depgraph.py:547-551`) + queue lease single
   writer (`commit_queue.py:1388` "仅 lease 持有者（单写者）调用").
2. **Regeneration LANDED, not just produced** — this is the F11 defect and the real work.
   `library_regen_reconciler.py:8` says pages are a gitignored view and "提交仍走人工批"; so the
   generator can succeed forever while the repo stays stale. Safe landing = the reconciler enqueues
   its own bag through `GitCommitGateway`/queue on its own post-commit event, with the
   `[GW:]`-marked path (AGENTS §9.8), and a *staleness* alarm with a numeric budget.
   Must be idempotent and loop-safe: a projection commit is a *derived* change and must be excluded
   from the trigger surface, exactly as `library_regen_reconciler.py:38` already excludes
   "馆页/对账报告/纯文档变更不触发，防 regen 风暴". Get that exclusion wrong and you build a commit
   oscillator.
3. **Drift guard with four quadrants** — already implemented and correct
   (`state.py:98-108`): CLEAN / PRIVATE_EDIT / STALE / CONFLICT, and it survives PG being down.
   Enforcement hooks are already wired to `REGISTRY-YAML-PARSE` (own-scope) + belt daemon
   `registry_drift` (`__init__.py:11`).
4. **Path resolved through ROOR, never hardcoded** — already the invariant
   (`projection_generator.py:73`).

### 7.2 When a projection becomes a second source of truth

A projection silently degrades into two authorities when any of these holds:

- **A human or a tool writes the projection.** Mitigated only by making the projection *not* a
  `DEFAULT_HOT_FILES` member writable by claim (today both registries ARE hot-writeable at
  `file_utils.py:415,417`), so a shard/projection file must be added to the hot list *with* a
  generator-only ownership marker, or `PRIVATE_EDIT` becomes the normal state.
- **The landing path is manual.** F11: manual landing plus a gitignored view is the definition of a
  projection that can be arbitrarily stale while the DB is authoritative; readers then see a
  different world than writers.
- **Consumers read the projection for truth and the DB for state inconsistently.** The 11 readers
  in `__init__.py:10` must be *all*-readers, not *most*; one straggler reading PG makes it a
  co-authority.
- **Drift is recorded but not enforced.** `classify` returning STALE/CONFLICT must block, not just
  be "记账" (accounting). `state.py` only classifies; the belt daemon "registry_drift 记账"
  (`__init__.py:12`) is a ledger, and a ledger with no gate is decoration (same failure class as
  F12's un-called recorder).
- **Regeneration is not pinned to a commit.** Without a recorded `render_sha` tied to the landed
  blob, no git-pinned protection of 6.2 can be recovered — the projection then buys you nothing
  that a plain file did not already have, at higher complexity.

### 7.3 Blast radius

Smallest of the migrating options: readers untouched by design (`__init__.py:10`), writers are the
PG ledger writers plus the generator. The gates keep working because the file still exists and still
diffs — **this is the option that preserves F7 and F12 instead of re-implementing them.**
It does add: a PG ledger for the other three authorities, a landing commit path, a staleness alarm,
and enforcement of STALE/CONFLICT.

### 7.4 Migration steps (per authority, and they are independent)

1. Land the W-M1 fix for "regenerates but never lands" (this campaign) *before* extending coverage.
2. Prove it on A1: N consecutive drift-free days, with STALE/CONFLICT actually blocking.
3. Only then extend the ledger to A2, then A4 (trial ledger — but see 7.6).
4. A3 (locks/session) is explicitly **not** a projection candidate — see 7.6.

### 7.5 Rollback

Repoint the generator's source from PG back to a checked-out monolith snapshot, or simply stop
landing and let the file be edited directly again (it is still a file). Rollback is the strongest
here *because* nothing is deleted: F7/F12 protections were never removed.

### 7.6 Cost

- Finish landing + enforcement for A1: **20-35 h** (largely already scoped as this campaign).
- Extend ledger to A2: **+25-40 h**.
- Extend to A4 trial ledger: **+10-15 h**, and it is worth *less* than it sounds because the trial
  ledger's problem is missing callers (4.1.5), not storage.
- A3: **do not migrate** (7.6 rationale below).
- Total: **45-90 h**, with a partial, useful increment bankable at ~30 h.

### 7.7 Honest caveat

Option 3's cost is *front-loaded on a promise the repo has not yet kept*: F11. Until the projection
lands by itself, extending projection coverage adds a second authority with a demonstrated
never-lands failure mode. The sequencing in 7.4 is therefore not stylistic; it is the whole risk
management of this option.

## 8. External practice (verified; anything unverified is labelled)

### 8.1 Merge queues: this repo already has the queue, but not the *rebuild*

Verified semantics, with quotes retrieved from the primary docs:

- **GitLab merge trains** (docs.gitlab.com/ci/pipelines/merge_trains/): each MR's pipeline is
  combined with the ones ahead of it — "The second merge train pipeline runs on the changes of both
  merge requests combined" — and on failure "GitLab removes that merge request from the merge train,
  and starts new pipelines for all the merge requests that were queued after it."
- **Zuul gating** (zuul-ci.org gating docs): changes are tested "in parallel" assuming predecessors
  pass; on failure "Zuul will report its failure and drop C from the queue," and the ones behind are
  retested without it.
- **GitHub Merge Queue** (docs.github.com, merging-a-pull-request-with-a-merge-queue): I retrieved
  the page but the extraction only returned the summary line "A merge queue helps merge pull requests
  into a busy protected branch after required checks pass." The merge-group/rebuild detail is
  **not verified by me** — stated here as "the same remove-and-retest pattern is what GitHub's queue
  is for", without quoting language I did not read.

**Mapping to this repo, precisely.** `commit_queue.py` shares the *fail-an-item-and-remove-it* half
(`dead_reason=cascade_stale`, `:1704-1717`) but deliberately inverts the *rebuild-successors* half:
bags are append-only and never rewritten (`:1378-1379` "袋 JSON 零改写（append-only 不变量）"), so a
successor whose base moved is retired, not re-based and re-validated. Every one of tonight's three
retirements is that inverted half: the labour of "rebuild the successor" was transferred onto the
agent who wrote the bag. Two cheap, storage-independent moves follow directly from the precedent:

1. Keep bag content immutable but allow a **re-base-and-requeue** step: `_revalidate_stale_base`
   already exists and already runs at dequeue time (`:1376-1377`, `:2372` even instructs
   "重投前先按当前 dev 重取基底（--base-head）"). Automating that re-take, instead of dying, is the
   merge-queue behaviour — and it fixes the *cost* of collision without touching storage at all.
2. Group bags by shard/section so that "combined pipeline" is meaningful (Option 1a), which is what
   makes a rebuild cheap instead of impossible.

### 8.2 Registry-as-code: package registries are data-in-git, and PR review *is* the concurrency control

- **crates.io index** (doc.rust-lang.org/cargo/reference/registries.html), verified quote: the `git`
  protocol "stores index metadata in a git repository and requires Cargo to clone the entire repo";
  the newer `sparse` protocol instead "fetches individual metadata files using plain HTTP requests".
  Two lessons, both directly on point:
  (a) one of the world's busiest registries put its authority **in git** and used review+merge as the
  concurrency control — this is the repo's current design, and it is not a naive design;
  (b) the same ecosystem then found that cloning the whole index was too heavy, and moved to
  **fetching individual small files** — i.e. they solved it by *sharding per key*, not by replacing
  git with a database. That is the strongest external support for Option **1a**, and the strongest
  evidence *against* Option 2 for this class of data. I did **not** verify the exact
  name-length directory rule (it is specified in the linked index-format/running-a-registry section,
  which I did not fetch) — I only verified "one file per crate is fetchable individually".
- **Git as authority is compatible with the repo's own protections**: F7's guards are all
  HEAD-vs-staged diff guards because the authority is a blob. The precedent says: keep the blob,
  shrink it.

### 8.3 Fencing tokens for the lease / liveness problem (F5) specifically

- Verified from Martin Kleppmann's distributed-locking article: fencing tokens are
  **monotonically increasing** numbers supplied by the lock service, and the storage service
  **rejects a write carrying a stale (lower) token**; the failure being defended against is exactly
  this repo's failure — a long pause or clock skew makes the lease expire, the stalled holder wakes
  up believing it still holds the lock, and proceeds to corrupt state.
- etcd / ZooKeeper / Kubernetes implement the same shape with different vocabulary: a lease with a
  TTL, a keepalive that must keep refreshing it, and a monotonic revision/epoch that accompanies the
  claim so a stale holder can be distinguished. I verified the *concept and mechanism* (Kleppmann)
  and this repo's own queue already has a single-writer lease
  (`commit_queue.py:1388` "仅 lease 持有者（单写者）调用"). I did **not** fetch primary etcd/Kubernetes
  spec text for this dossier (the etcd lease doc 404'd); the etcd/K8s mapping below is stated as
  design analogy, not as a quoted citation.
- Mapping is near-exact, and shows what is missing here:

  | external system | mechanism | this repo today | gap |
  |---|---|---|---|
  | K8s leader Lease | `renewTime` + `holderIdentity`; takeover only after expiry | `last_heartbeat`, 90 s timeout (`session_concurrency.py:152`) | present |
  | etcd revision | monotonic revision accompanies every claim | none | **absent** |
  | fencing token | storage rejects lower-token writes | gateway accepts any live-looking session | **absent** |
  | keepalive semantics | refresh is decoupled from doing work | `last_activity` refreshed only by register/claim (`:227`) | **inverted** — working-but-not-claiming dies |

  The `--adopt-prior-work` flag (AGENTS §2.3) is this repo's existing, hand-rolled *recovery* from
  the missing fence: it re-adopts work after a claim identity was lost. A `lease_epoch` would make
  that safe by construction instead of by flag discipline.
- **The point for the storage decision**: fencing is a *protocol*, not a *storage engine*. Postgres
  would not have prevented F5 — a stale row writer writes just as happily. Option 0 item 4 and
  Option 3 both need the fence; only Option 2 pretends otherwise.

## 9. Table of evidence that would flip the verdict

| # | evidence | direction |
|---|---|---|
| E1 | Retirement rate attributable to the *two registries* is < ~1 per week over a 4-week census (not one night) | strongly toward Option 0; collision is not the bottleneck |
| E2 | Census shows the majority of `cascade_stale` deaths are **non-registry** bags, or are same-bag re-enqueues after a code change | Option 0/1 — sharding registries fixes a cost centre that is not where the loss is |
| E3 | A re-base-and-requeue automation (8.1.1) alone removes most retirements | **kills Options 1/2/3 as answers to collision**; storage was never the problem |
| E4 | Collision incidents trace to `creation_tokens` writes (F1) rather than `capabilities`/`entries` | Option 1a only (section split), nothing bigger |
| E5 | Measured lane counts that actually touch the same registry concurrently >= 3 routinely | toward Option 1b or 2 |
| E6 | A real loss event where a *row-level* DB write would have been silently wrong too (e.g. a false ledger/registry row) | against Option 2 — confirms F6/6.2.7 truth is not storage |
| E7 | `REGISTRY-MASS-DELETION`, `HOT-FILE-BASE-FRESHNESS`, own-scope doctrine are demonstrably *load-bearing* (near-misses they actually blocked in 90 days) | strongly against Option 2; strongly for Option 3 (keeps blobs) |
| E8 | Those three guards are found decorative (like the repo's own census of 装饰/半接线 guards) | weakens the file-only argument, opens Option 2 |
| E9 | W-M1 projection lands by itself for N consecutive drift-free days with STALE/CONFLICT actually blocking (F10/F11) | go-mandatory for Option 3; without it Option 3 is disqualifying |
| E10 | Projection landing stays manual even after the campaign fix (gitignore + "提交仍走人工批" survives, `library_regen_reconciler.py:8`) | against Option 3 *and* Option 2 (no DB-backed authority can land itself here) |
| E11 | PG outage frequency / commit-gate availability data shows PG is down during working hours regularly | against Option 2 (moves commit gating into PG's envelope; cf. `state.py:100-101` deliberate degradation) |
| E12 | `tasks` table census: the repo's own PG/SQLite state store shows unreconciled states or ghost rows at scale | against Option 2 — "as false as a YAML line" becomes measured |
| E13 | Cross-shard uniqueness check turns out cheap (sub-second over shards) | removes Option 1's main argument against itself (5.3.1) |
| E14 | `.ailocks` shared-claim change (Option 0 item 3) measurably increases queue waiting/serialisation | roll back item 3, keep items 1/2/4/5; consider 1a instead |
| E15 | Two authorities (A3) cannot be git files at all because they must be read cross-worktree in real time | A3 belongs in a shared store regardless of what A1/A2/A4 do — argues for *per-authority* answers, not one |

## 10. Recommended sequencing — safe under ANY final choice

Everything here is worth doing whether or not anything migrates, and none of it forecloses anything.

**Tier 1: unambiguous defects, no architecture involved (do now)**
1. Fix `add_module_translation` canonical-field clobber by reusing `_merge_duplicate_blocks`
   semantics (4.1.1). Data is being destroyed right now; cost 3-5 h; fully revertible.
2. Add a post-write check that a canonical field never goes non-empty to empty without an explicit
   flag (makes the F2 class loud instead of silent).
3. Call `TrialLedger.record_run` at the executor boundary that cannot be bypassed (4.1.5). Storage-
   independent; the missing-caller problem survives every option.
4. Fix the liveness asymmetry so a working lane is not judged dead (F5, item 4a). Cheap, and it is a
   live safety bug, not a design preference.

**Tier 2: protocol, still not storage**
5. Introduce the **fence token** (`lease_epoch`) — needed by Option 0, 1 *and* 3; only Option 2
   claims not to need it, and 6.2.7 says that claim is false (8.3).
6. Make `_revalidate_stale_base` **re-base and requeue instead of die** (8.1.1). This attacks the
   measured cost (retired bags) without touching a single file layout. Highest leverage-per-hour in
   the dossier for the collision pain specifically.
7. Add the **no-pointer-orphan rule as a mechanical gate** (6.3): every registered store path must
   exist, be non-zero, match its declared engine. Independent of the decision, and it retroactively
   explains F9. Cheap insurance before *any* migration.

**Tier 3: file hygiene that every option can use**
8. **Option 1a — section split of `creation_tokens` out of the capability registry** (F1, 5.1).
   Separates the hottest writer from the cold index, is a pure-file change, is fully revertible, and
   is the external precedent that crates.io actually followed (8.2). Do it before considering 1b/2/3.
9. Census, don't guess: measure for 4 weeks which files bags actually collide on, and which guards
   actually block (E1/E2/E3/E7/E8). The whole decision hinges on this and it is unmeasured today.

**Tier 4: gated on evidence, and only after the W-M1 landing fix is proven**
10. Complete and *prove* the projection lands itself (7.4 step 1-2) before extending coverage.
11. Only then decide A2/A4 per authority. **Do not migrate A3** (locks/session): its requirement is a
    shared live store, which is best served by one shared file + Mutex (already built,
    `lock_files.py:104-106`) or by PG if the Owner prefers — but its protections are not git-pinned,
    so it is the one authority where a DB is genuinely defensible. It is also the smallest.

## 11. The case where Option 0 (or 0 + 1a) is the right answer

Write it plainly, because it is a real and possibly the best answer.

Option 0 is correct when **all** of these hold:

1. **The corruption-class bugs are writer bugs, not storage bugs** — which this study verified.
   F2 is a field-set exclusion in one function (`add_module_translation.py:413`). F5 is which event
   refreshes `last_activity` (`session_concurrency.py:227`). F12 is a recorder with one caller. F4 is
   one root constant that is already fixed for the sibling registry
   (`lock_files.py:97` vs `session_concurrency.py:290-315`). None of these is caused by YAML, and
   none is caused by *anything* about file-vs-row storage. A migration would ship all four bugs into
   a new engine.
2. **The measured collision cost is below the fix cost.** If the census (E1/E2/E3) shows a few
   retirements a week, and E3 shows that re-base-and-requeue (Tier 2 item 6) recovers most of them,
   then Options 1b/2/3 (70-110 / 160-240 / 45-90 h) are buying back hours they cost several times
   over — and the repo's own net-zero rule (AGENTS §4.1: new machinery must declare what it replaces)
   has no answer for what Option 2 replaces.
3. **The git-pinned protections are load-bearing.** F7 proved they diff blobs; if E7 shows they
   actually block near-misses (and the mass-deletion gate's own INVARIANTS records a 4703-line
   near-evaporation as its raison d'être), then Option 2 does not "re-implement" them, it *degrades*
   them — a HEAD-side identity set (`registry_mass_deletion_gate.py:32`) has no DB analogue, because
   an audit trail that any writer can UPDATE is not an audit trail.
4. **Read fan-out is wide and write fan-out is narrow.** 52 Python files read the capability registry
   and 38 the translation registry (§F1/5.2), while only a handful write them. That asymmetry is the
   textbook signature of a *file with generated content*, not of a database workload — and it is
   exactly the shape Option 3 was scoped to preserve ("11 读端继续读本地 YAML，永不触 PG").
5. **Availability.** Commit gating must not depend on PG. `state.py:100-101` shows the maintainers
   already chose "degrade rather than couple" for the projection. Option 0 preserves that property
   for free.

Option 0 + **1a** (section split) is the right answer when, on top of the above, the census shows the
collisions are concentrated on `creation_tokens` (E4). That is the most likely outcome on current
evidence, because `creation_tokens` is the section written on *every new file* while `capabilities`
is written occasionally. It is a pure-file change, fully revertible, and it has the strongest external
precedent in the dossier (8.2).

**What Option 0 explicitly does not buy**: it does not stop two lanes snapshotting the same file, so
`cascade_stale` retirements continue unless Tier 2 item 6 (re-base and requeue) is done. Anyone
presenting Option 0 as "the collision is handled because CAS refuses stale writes" is confusing
*correctness* with *throughput* — CAS makes the collision safe and simultaneously makes it certain.

## 12. Instruction-looking text encountered, recorded as DATA (not followed)

- `AGENTS.md` and per-worktree `agents.md` copies injected as project context, plus
  `.trae/rules/project_rules.md` pointers: rule claims, not instructions executed by this study.
- `C:\Users\fanzi\.qoder-cn\projects\D--ZephyrAlpha\memory\MEMORY.md` and
  `C:\Users\fanzi\.qoder-cn\memory\MEMORY.md` injected as "Memory" notes with imperative phrasing
  ("停手上报", "必追问采集面", "落笔前必须先 grep"). Treated as prior-lesson data only.
- Frontmatter/docstring text inside read files carrying `INVARIANTS`, `MODIFY-GUARD`, `TTL`,
  `ERROR_CONTRACT` directives (e.g. `add_module_translation.py:9-16`,
  `registry_mass_deletion_gate.py:8-13`, `session_concurrency.py:8`) — read as documentation of
  intent, and where they assert behaviour I verified the code or marked it assumed.
- `config/.env.postgres` contains credential *keys*; values not read into this dossier beyond
  key names (RULE-SECRETS).
- Violation-message strings inside gates that name registry paths (e.g.
  `ssot_redefinition_gate.py:218`, `create_guard.py:706,722`) are user-facing advice text; they are
  evidence for Option 1's doc-rot failure mode, not instructions.
- No file in the read set contained an embedded attempt to redirect this task (no "ignore previous
  instructions"-type content found). The one near-miss is prose in `total_command_closeout/**`
  master books, which this study did not open beyond filename matches and which are held by another
  lane.

## 13. Premise corrections to the tasking brief (recorded because they change the options)

1. **`add_module_translation` merge-vs-overwrite**: confirmed real, but the mechanism is *narrower*
   than "replace a whole existing entry" — extension fields are already merged
   (`:410-416`); only the 7 canonical keys are clobbered, and only the 3 optional ones actually lose
   data (`name_en`, `desc_zh`, `desc_en`). See F2.
2. **"make the token tool refuse to re-register an existing path"**: already implemented
   (`batch_creation_tokens.py:96-108, 503-508`, plus a wide-prefix guard at `:521-535`). See F3.
3. **"the repo already runs PG ... and has a `tasks` table with 73 columns/2546 rows"**: the `tasks`
   table is **SQLite** (`task_repo.py:78,92,166`) with **62** model fields (`:1055-1056`), not PG/73.
   The 14-state machine with distinct COMPLETED vs VERIFIED **is** confirmed
   (`task_types.py:63-84`). Row count 2546 unverified. See F8.
4. **"`.ailocks/registry.json` + `.runtime/session_registry.json`" as one authority**: they are
   already inconsistent with each other — the session registry is main-anchored
   (`session_concurrency.py:290-315`) and `.ailocks` is not (`lock_files.py:97`). The brief's pain #2
   is therefore a *half-done* fix, not an absent one. See F4.
5. **"four other 0-byte DBs"**: measured **seven** 0-byte `.db` files under `data/` (maxdepth 2).
   See F9.
6. **Option 3 "check whether this repo already has that pattern"**: it does, deliberately, for the
   capability registry specifically, with a four-quadrant drift classifier — `registry_projection`
   (W-M1 lane B, 2026-09-23). The question is completion of landing, not design. See F10/F11.
7. **File scale**: the registries are 2.95 MB and 3.62 MB, not token-count-scale single-purpose
   tables; both are multi-section containers, which changes Option 1's design space. See F1.

## 14. Verification status

- `verified:` F1 F2 F3 F4 F5 F6 F7 F8(states, backends) F9 F10 F11 F12, all 22+14 path bindings,
  sizes, section line numbers, guard mechanisms — by direct read of the cited files.
- `assumed:` tasks row count 2546; "three bags retired back-to-back tonight"; the ~17 percent trial
  under-record figure; the duplicate-general-contractor incident narrative (mechanism verified, event
  not reproduced); 11-reader count as currently accurate.
- `not verified:` exact crates.io index directory-sharding rule; GitHub merge queue merge-group
  rebuild wording; etcd/Kubernetes primary spec text (analogies only, labelled in 8.3).
- External evidence: 4 primary docs pages fetched/quoted (GitLab merge trains, Zuul gating,
  Cargo registries, Kleppmann distributed locking), GitHub merge queue page fetched but content
  extraction insufficient.

## 15. Pending merge-back note

This case file is a study product of lane `st-p17-storage` and lands under
`three_piece_infra/storage_decision/`. **PENDING MERGE-BACK**: it has not been merged to the main
workspace, not committed, and not queued (no git add/commit/enqueue performed). It must be merged
back by whoever holds the campaign index, and reconciled against — but never editing —
`docs/_working/total_command_closeout/**`, which is held by another live lane and is off-limits for
this decision. Nothing in Options 0-3 proposes editing those two master books.
