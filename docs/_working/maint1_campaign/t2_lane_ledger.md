---
ttl: task_bound
owner: st-maint1-t2lane
campaign: 维护一班 T2（蒸发战争·stash drop 治本）
---

# T2 件② 施工台账 — stash drop 蒸发治本（认人 + 存证 + 留痕）

- 车道：`D:\ZephyrAlpha\.worktrees\st-maint1-t2lane`
- 分支：`ai/st-maint1-t2lane/task-maint1-evaporation-cure`（基线=当时 dev）
- 会话：st-maint1-t2lane（写码车道，集成由总包做；本车道零 git add/commit/stash/reset/checkout/入队/merge）
- 日期：2026-10-10
- 判据口径变更声明：见 §4（必读）

---

## 1. 改动文件清单（绝对路径）

| # | 文件 | 性质 |
|---|------|------|
| 1 | `D:\ZephyrAlpha\.worktrees\st-maint1-t2lane\src\zephyr\governance\audit\reconciliation_registry.py` | 改（S1 通道治本 + 新增治理面单一真源） |
| 2 | `D:\ZephyrAlpha\.worktrees\st-maint1-t2lane\scripts\git_guard.py` | 改（S2 分类纠正 + 破坏性通道闸门） |
| 3 | `D:\ZephyrAlpha\.worktrees\st-maint1-t2lane\tests\gov\governance\audit\test_stash_lifecycle.py` | 改（把 bug 立法的期望改判，见 §4） |
| 4 | `D:\ZephyrAlpha\.worktrees\st-maint1-t2lane\tests\gov\governance\audit\test_stash_drop_ownership_cure.py` | 新建（红证载体，17 用例） |

未碰：`scripts/session_worktree.py`、`scripts/commit_queue.py`、`scripts/governance/commit_queue_landing.py`、`git_commit_gateway.py`、任何注册表 yaml、任何 PG 写面、`data/` 业务目录。

---

## 2. 病灶复核（逐条核到 return/drop 行，与取证车道一致）

| 取证坐标 | 复核实况（改前行号） | 实读结论 |
|---|---|---|
| S1 TTL≈4h | `reconciliation_registry.py:9826` `_STASH_TTL_SECONDS = 4 * 3600` | 一致 |
| S1 仅 user-manual- 受保护 | `:9828` `_PROTECTED_STASH_PREFIXES = ("user-manual-",)` | 一致 |
| S1 反向匹配当 drop 判据 | `:9836-9851` `_is_ai_generated` docstring 白纸黑字："非 user-manual- 前缀的 stash **都是 AI 创建的**"；`:9853-9864` `_should_drop` 只看前缀+age | 一致：不看 sid、不看活性、不看 claim |
| S1 任何 commit 触发 | `:9875-9877` `_trigger = bool(committed_files)` | 一致 |
| S1 主仓裸 drop | `:9958-9963` `["git","stash","drop",stash_ref]`，前后无锚、无审计、无归属判定 | 一致：零存证 |
| S2 drop 当只读 | `git_guard.py:99-100` `STASH_READONLY = {"list","show","drop"}` → `:605-606` `if args[0] in STASH_READONLY: return _passthrough(git_args)` | 一致：无条件放行 |
| S2 clear 仅 warn | `git_guard.py:610-612` warn 后 `_passthrough` | 一致 |
| alias 实证 | 主仓 `git config --get-regexp alias` 七条 alias 全指 git_guard | 即 §S2 那条分类就是主仓 `git stash drop` 的实际闸门 |

---

## 3. 逐处判据行级说明（改后行号）

### 3.1 `reconciliation_registry.py` — 治理面（新增，单一真源）

区块注释 `:9770-9800` 记录病根与三前置。新增模块级符号：

| 行 | 符号 | 判据 |
|---|---|---|
| `:9802` | `_STASH_EXPLICIT_OWNER_RE` | 显式署名优先：`session_worktree_pre_merge: <sid>` / `session_worktree_abort: <sid>` |
| `:9805` | `_STASH_SID_TOKEN_RE` | `(?<![A-Za-z0-9])(?:st\|sess)-…` 兜底抽 sid。**假阳性只会落到"未注册=ghost=豁免"侧，永不造成误删** |
| `:9809` | `STASH_DROP_AUDIT_RELPATH` | `.runtime/gate_audit/stash_drop_governance.jsonl`（循既有 gate_audit 约定，对标 `git_guard.py:377`；`.jsonl` 是 sweep 保护后缀 `:7744`） |
| `:9835` | `stash_owner_candidates()` | 返回去重候选；**多候选=归属不可判**，调用侧必须豁免 |
| `:9890` | `anchor_stash_ref()` | 前置②：`git update-ref refs/quarantine/stash-<sid>-<ts>-<sha8>` 后**必须** `git show-ref --verify` 复核；写不进/看不境 = 返回 `("","")` → 调用侧不 drop |
| `:9934` | `list_stash_refs()` | 供 `stash clear` 枚举（clear 默认阻断时需要知道要毁几条） |
| `:9949` | `govern_stash_drop()` | 三前置判定（不 drop）：前置0 sha 可解析 → 前置1a sid 唯一可判 → 前置1b **活性** → 前置1c **claim** → 前置2 存证锚 |
| `:10062` | `drop_governed_stash()` | 前置通过才动手；drop 前再 `rev-parse` 复核索引未漂移（漂了当归属不明放弃）；无论动手/豁免都落审计（含 `did_drop`）；`:10086` 是全模块唯一 `git stash drop` 出口 |

活性与 claim 的判据真源（复用在册原语，未自造）：

- `:9999`/`:10001` `zephyr.security.access_control.session_concurrency.liveness_verdict(sid)` — 定义在 `session_concurrency.py:1637`（裁定#480 C-2 单一活性裁决表），本判据只接受 `state == "dead"`（`:9810 _LIVENESS_DEAD_STATE`）。`alive`/`degraded`/`ghost`（含"注册表无片+无心跳"=未注册）一律豁免。
- `:10029`/`:10031` `zephyr.infrastructure.runtime.concurrency_guard.check_rollback_conflict(files, owner_sid, root)` — 定义在 `concurrency_guard.py:150`。stash 触及文件被其他在场会话 claim → 豁免（HELD-OVERLAP 不硬闯）。
- 两个原语任一不可用（import 败/异常）= **判活不明/冲突不明** → 豁免（fail-closed 关在动手侧，不关扫描侧）。

清扫通道改造（原 `:9900-9992` 的 drop 循环 → 现 `:10300-10380` 区间）：

- 前缀/TTL/aggressive 降级为**候选筛选**（`_is_ai_generated`/`_should_drop` docstring 已改写：`:10185`/`:10201`）；
- 每条候选一律走 `drop_governed_stash(project_root, stash_ref, actor=f"reconciler:{session_id}")`（`:10328`）；
- 结果面新增 `exempt=N` 与豁免样例；`action` 口径：有 errors=warn、有豁免=warn（不静默）、有 drop 无错=clean、全未入库=skip（`:10354-10368`）；
- `_trigger` 保持 `bool(committed_files)`，注释说明触发不是病灶、动手面已 fail-closed（`:10218-10222`）。
  - 判据分叉记录：曾考虑把触发收窄（如仅 stash 数超阈才扫），按"更保守=宁可不 drop"方向不动触发面——触发只影响扫描成本，drop 侧三前置才是蒸发面；改触发会掩盖堆积信号，留下一轮专项。

### 3.2 `git_guard.py` — 分类纠正 + 破坏性闸门

| 行 | 改动 | 判据 |
|---|---|---|
| `:105-109` | `STASH_READONLY = {"list","show"}`（**drop 移出**），注释点名旧 L99-100/L605-606 与 alias 实证 | drop 不是只读：它让未落地在飞面失去取回面 |
| `:112-113` | 新增 `STASH_DESTRUCTIVE = {"drop","clear"}` | 破坏性家族集中判定，clear 一并升档 |
| `:115-127` | 新增 `STASH_DESTRUCTIVE_ESCAPE_ENV="ZEPHYR_STASH_DROP_ESCAPE"` + `_STASH_DESTRUCTIVE_ESCAPE_KEYWORDS`（3 项白名单） | 逃生标记形态循既有白名单惯例（`[no-lookup:<白名单 reason>]` / `[allow-mass-deletion:<reason>]`）；**匹配语义复用真源 `capability_lookup_bypass_policy.is_exempt_reason`**，禁自造 |
| `:400` | `_audit_self_harm(..., extra=None)` 新增可选字段 | 判定面/存证面入既有审计通道（`git_guard_self_harm.jsonl`），不开新目录、不改旧记录形状 |
| `:634` | `_stash_destructive_governance()` | 治理面取用；import 败 → 返回 None → 调用侧无逃生即阻断 |
| `:652` | `_stash_escape_reason()` | env 值必须命中白名单关键词，否则打印"逃生不生效"并按无逃生处理 |
| `:672-790` | `_handle_stash_destructive()` | ① 逐条 `govern_stash_drop`（同一真源，防双判据）② 全过才 `_passthrough` ③ 任一不过 → 打印阻断+解决方案+`_audit_self_harm` → `return 1` ④ 白名单逃生只豁免归属判定，**仍逐条尝试落锚**并 `forced=True` 记审计 ⑤ clear 需先枚举，枚举不出=阻断 |
| `:798-806` | `_handle_stash` 路由：READONLY→透传；DESTRUCTIVE→治理通道；OVERWRITE(pop/apply/branch)→原冲突检查不变；push→原自伤逻辑不变 | 旧 `:610-612` clear 仅 warn 分支已删除 |
| `:9`/`:37-45` | 头部 `[INVARIANTS]` + 使用说明补"drop/clear 非只读，放行前先落字节锚" | 文档与实现同批 |

---

## 4. 判据口径变更（(c) 强制项）

### 旧判据（原文坐标）

- `reconciliation_registry.py`（改前）`:9836-9851` `_is_ai_generated`：docstring 断言"非 user-manual- 前缀的 stash **都是 AI 创建的**"；
- `:9853-9864` `_should_drop`：`not protected && (aggressive || ai_generated) && age>=4h` → **直接进 drop 队列**；
- `:9958-9963`：无锚、无审计、无归属 `git stash drop`。
- 被立法的期望（`tests/gov/governance/audit/test_stash_lifecycle.py` 改前 `:283-303`）：
  `test_aggressive_drops_unknown_ai_prefixes` 断言 `"dropped=2" in result.detail` 且 `len(remaining)==1`，其中一条正是 **`other-session-wip-module-id-naming-fix`** ——即"别人在飞的 WIP 该被 drop"被写成了期望。同文件 `:317`（`dropped=1`，属主 `session_worktree_pre_merge: sess-xxx` 未注册）、`:365-369`（`dropped=8`，全部无 sid 可判）、`:396-400`（`dropped=8`，含 `sess-001/sess-002` 未注册）同病。

### 新判据

前缀/TTL 只产生**候选**；动手需三前置全过（认人=唯一 sid + 活性裁决 `dead` + 未被在场会话 claim；存证=refs/quarantine 锚写入且复核可见；留痕=jsonl 审计）。任一不过 → 不 drop，只 warn+记账。

### 为什么这不是放松门禁

1. 判据只增不减：旧条件（非 user-manual- + TTL/aggressive）仍是**必要条件**，新增三条前置是**合取**项——被 drop 的集合是旧集合的子集。
2. 识别力没缩：8 个原 AI 前缀 + 7+ 种未知前缀仍全部进候选（`test_real_world_unknown_prefixes_recognized`/`test_session_worktree_prefix_still_recognized` 现在断言 `exempt=8`，即 8 条都被识别到并逐条判定，不再形同虚设）；旧"识别不出→零清理"的病不复发，因为豁免也留痕（审计可见、warn 可见）。
3. git_guard 侧是**升档不是降档**：`drop` 从"无条件 passthrough"变成默认阻断；`clear` 从"warn 后 passthrough"变成默认阻断；逃生需要白名单 reason，且逃生路径仍先尝试落字节锚。
4. 期望改判方向单一：所有改判用例都从"应该少"改成"应该不动手"（更保守），无一条把阻断改成了放行。

改判说明已写进测试本体（每个改判用例的 docstring 第一句都点名 2026-10-10 st-maint1-20261010 + 理由），文件级声明在 `test_stash_lifecycle.py:33-40`。

---

## 5. 红证（顺序：先红后绿）

### 5.1 RED-A 行为红证（主区未修码）

探针 `-p redpin` 先把 `zephyr.*` 从 `D:\ZephyrAlpha\src`（未修码）钉进 sys.modules，再用车道新测试打它
（探针件 `.runtime\tmp\maint1_t2_red\redpin.py`，临时件不入仓）。

```
cd D:\ZephyrAlpha\.worktrees\st-maint1-t2lane
PYTHONNOUSERSITE=1 PYTHONPATH=/d/ZephyrAlpha/.runtime/tmp/maint1_t2_red \
  python -m pytest -c py.ini tests/gov/governance/audit/test_stash_drop_ownership_cure.py \
  -p no:cacheprovider -p redpin -k "live_owner"
```

原文输出（关键段）：

```
[RED-PIN] reconciliation_registry = D:\ZephyrAlpha\src\zephyr\governance\audit\reconciliation_registry.py
[RED-PIN] has govern_stash_drop = False
__________ TestOwnershipGate.test_live_owner_stash_is_never_dropped ___________
        result = _run_reconciler(tmp_path, monkeypatch)
>       assert "dropped=0" in result.detail, result.detail
E       AssertionError: stash lifecycle: dropped=1 (>4h AI stash, aggressive=False), kept=0, protected=0, errors=0
1 failed, 16 deselected in 1.10s
```

即：未修码把**属主为在场活会话（pid=当前进程、注册表心跳新鲜）**的 stash 直接 drop 掉。

全集红（行为用例段）：

```
PYTHONNOUSERSITE=1 PYTHONPATH=.../maint1_t2_red python -m pytest -c py.ini \
  tests/gov/governance/audit/test_stash_drop_ownership_cure.py -p no:cacheprovider -p redpin \
  -k "Ownership or DeadOwner or AuditTrail"
→ 9 failed, 8 passed
   FAILED …::test_live_owner_stash_is_never_dropped                  (dropped=1 期望 0)
   FAILED …::test_unregistered_owner_exempt                           (被 drop)
   FAILED …::test_message_without_sid_exempt                          (被 drop)
   FAILED …::test_ambiguous_owner_sid_exempt                          (被 drop)
   FAILED …::test_dead_owner_dropped_and_bytes_recoverable_from_anchor (无锚可取回)
   FAILED …::test_audit_written_for_blocked_and_dropped                AssertionError: [] assert 0 == 2
   （另 3 条为治理面新 API 的 ImportError：govern_stash_drop / drop_governed_stash / stash_owner_candidates 主区不存在）
```

### 5.2 RED-B 闸门红证（主区 git_guard 对 stash drop 无条件放行）

```
cd D:\ZephyrAlpha\.runtime\tmp\maint1_t2_red\repo   （临时 git 仓，一条 stash）
env -u ZEPHYR_FORCE_STASH -u ZEPHYR_COMMIT_GATEWAY -u ZEPHYR_GIT_GUARD_FAST_PATH \
    -u ZEPHYR_STASH_DROP_ESCAPE PYTHONNOUSERSITE=1 \
    python "D:/ZephyrAlpha/scripts/git_guard.py" stash drop "stash@{0}"
```

原文输出：

```
--- stash before ---
stash@{0}: On master: 谁也没认领的在飞面
=== 主区未修码 git_guard 对 stash drop 的判定 ===
Dropped stash@{0} (1cb1b9ebf1b6d5162cc34c33347fc42bdef9c5e0)
RC=0
--- stash after ---
(空=已被放行删除)
--- 存证锚 ---
(空=零存证)
```

### 5.3 GREEN 车道绿灯

```
cd D:\ZephyrAlpha\.worktrees\st-maint1-t2lane
PYTHONNOUSERSITE=1 python -m pytest -c py.ini \
  tests/gov/governance/audit/test_stash_drop_ownership_cure.py -p no:cacheprovider
→ 17 passed in 12.19s

PYTHONNOUSERSITE=1 python -m pytest -c py.ini \
  tests/gov/governance/audit/test_stash_lifecycle.py -p no:cacheprovider
→ 38 passed in 10.33s

两文件同跑 → 55 passed in 21.56s
```

采集面点名（防 glob 假绿）：

- `tests/gov/governance/audit/test_stash_drop_ownership_cure.py`（新建，17 nodeid：`TestOwnershipGate` 5 + `TestDeadOwnerDropWithAnchor` 4 + `TestAuditTrail` 1 + `TestGitGuardStashDrop` 7）
- `tests/gov/governance/audit/test_stash_lifecycle.py`（改过，38 nodeid：`TestDropSessionPreMergeStash` 5 + `TestAiStashRegex` 20 + `TestStripStashBranchPrefix` 7 + `TestStashLifecycleReconcilerReverseMatch` 6）——已按要求**单独重跑**，不拿目录级绿灯当基座绿灯。

回归面（同批跑，未改文件）：

- `tests/meta/scripts/test_git_guard_self_harm.py` → 16 passed
- `tests/gov/governance/audit/test_git_guard_bypass_reconciler.py` → 8 passed
- `tests/gov/governance/audit`（整目录，默认 pyproject 配置 `-n 4`）→ 结果见 §7 追加记录

配置双跑说明：`-p no:cacheprovider` 与 pyproject 的 `cache_dir` 组合必 INTERNALERROR（pyproject P1-4 注记实证），故红/绿一律 `-c py.ini` 精简配置；宽网回归用默认 pyproject 配置（缓存落 `.runtime/tmp/pytest_cache`，gitignored，不污染根目录）。

### 5.4 车道装载自证（假绿防线 #1）

```
cd D:\ZephyrAlpha\.worktrees\st-maint1-t2lane
PYTHONNOUSERSITE=1 python -c "import sys; sys.path.insert(0,'src'); import zephyr.governance.audit.reconciliation_registry as rr; print(rr.__file__)"
LOADED reconciliation_registry = D:\ZephyrAlpha\.worktrees\st-maint1-t2lane\src\zephyr\governance\audit\reconciliation_registry.py
LOADED git_guard = D:\ZephyrAlpha\.worktrees\st-maint1-t2lane\scripts\git_guard.py
STASH_READONLY = ['list', 'show'] | STASH_DESTRUCTIVE = ['clear', 'drop']
```

`PYTHONNOUSERSITE=1` 已在每条命令前置（usercustomize 会把 `D:\ZephyrAlpha` 钉进 sys.path）。

---

## 6. 复核命令（总包/复审可直接复算）

```bash
cd /d/ZephyrAlpha/.worktrees/st-maint1-t2lane
# 1) 装载自证
PYTHONNOUSERSITE=1 python -c "import sys;sys.path.insert(0,'src');import zephyr.governance.audit.reconciliation_registry as m;print(m.__file__)"
# 2) 双配置绿灯
PYTHONNOUSERSITE=1 python -m pytest -c py.ini tests/gov/governance/audit/test_stash_drop_ownership_cure.py tests/gov/governance/audit/test_stash_lifecycle.py -p no:cacheprovider
PYTHONNOUSERSITE=1 python -m pytest tests/gov/governance/audit/test_stash_drop_ownership_cure.py tests/gov/governance/audit/test_stash_lifecycle.py -q
# 3) lint
PYTHONNOUSERSITE=1 python -m ruff check scripts/git_guard.py src/zephyr/governance/audit/reconciliation_registry.py tests/gov/governance/audit/test_stash_drop_ownership_cure.py tests/gov/governance/audit/test_stash_lifecycle.py
# 4) 红证复算（主区未修码，只读复核；探针件见 .runtime/tmp/maint1_t2_red/）
PYTHONNOUSERSITE=1 PYTHONPATH=/d/ZephyrAlpha/.runtime/tmp/maint1_t2_red python -m pytest -c py.ini \
  tests/gov/governance/audit/test_stash_drop_ownership_cure.py -p no:cacheprovider -p redpin -k "live_owner"
```

注：§4/§5 的复核命令全部只读或只写 tmp_path/`.runtime/tmp`；无 `data/` 业务目录写面。

---

## 7. 追加记录（施工期事实）

- 2026-10-10：新建未跟踪件（本台账 + `test_stash_drop_ownership_cure.py`）每轮改动双抄至 `D:\ZephyrAlpha\.runtime\quarantine\maint1_t2_safety\`（在册第六态防线）。
- 2026-10-10：宽网回归（默认 pyproject 配置，`-n 4`）
  `PYTHONNOUSERSITE=1 python -m pytest tests/gov/governance/audit -n 4 -q`
  → **1854 passed, 1 skipped in 44.51s**（整目录，含被改的 `test_stash_lifecycle.py` 38 例与新建 17 例）。
- 2026-10-10：双配置同判复算（GATE-PYTEST-CONFIG-DRIFT 关注的"换配置就绿"防线）——
  两支目标文件 `-c py.ini` 精简配置 = 55 passed；默认 pyproject 全量配置 = 55 passed。判定一致。
- 2026-10-10：`ruff check` 四支文件全通过（`All checks passed!`）。
- 2026-10-10：红证探针工件位置（临时区，非交付物，总包集成后可清）：
  `D:\ZephyrAlpha\.runtime\tmp\maint1_t2_red\redpin.py`（sys.modules 钉主区码）与
  `D:\ZephyrAlpha\.runtime\tmp\maint1_t2_red\repo\`（RED-B 用临时 git 仓，stash 已被主区旧闸门删掉，零锚）。
  写面仅 `.runtime/tmp/` 与 tmp_path——主区 `git status` 对 §1 四支文件路径为 clean（已核）。

---

## 8. 残余风险（如实挂账，未达标不粉饰）

1. **注册表分片收割后判据退化**：`liveness_verdict` 在"注册表无片+无心跳>90s"时给 `ghost`（`session_concurrency.py:1709`）。会话物理记录被 15 分钟墓碑宽限后收割 → 其残留 stash 永久落"未注册=豁免"，stash 堆积会回来（这正是 #ARCH-STASH-ACCUMULATION-001 想治的）。方向选择：按"宁可不 drop"保守侧不动手；豁免笔笔进 `.runtime/gate_audit/stash_drop_governance.jsonl`，堆积信号可见。后续专项建议：以墓碑/归档侧证据（sessions_archive + takeover 台账 resolve 态）补"确证曾死"通道，而不是回退到前缀反推。
2. **sid 抽取依赖 message 惯例**：AI 手工 stash 若不落 sid（如 `pre-construction stash: <测试名>`），永不可 drop。同上属保守侧代价。
3. **`git_guard` 走 alias 时的双治理**：reconciler 的 `git stash drop` 在主仓会再经 alias 进 git_guard，治理面被算两遍（两遍都会各落一个 `refs/quarantine/stash-*` 锚，字节面重复但无害）。未做去重（需跨进程状态，代价>收益）。
4. **`cleanup_stash.py` 会被新闸门拦**：`scripts/governance/d1_structure/cleanup_stash.py:120` 直接 `git stash drop`，经 alias 后需白名单逃生才能落地。该文件不在本车道改权范围——挂账给总包（改法：走 `drop_governed_stash` 或带逃生 reason）。
5. **`_drop_session_pre_merge_stash` 未加锚**（`session_worktree.py:4150`）：那是"本会话 merge 成功后删自己刚创建的 pre-merge stash"的通道，属主=自己且已在 merge 后，蒸发半径不同于 S1；不在本车道改权范围。若要一致化（drop 前也落锚），属 S3 专项。
6. **claim 冲突判据依赖 `.ailocks/` 可读**：`check_rollback_conflict` 异常时按"冲突不明"豁免（保守），无锁文件的 stash 归属判不出=不 drop。
7. **时间判据用 `GIT_COMMITTER_DATE` 造旧**，未 monkeypatch `time.time()`：`_reconcile` 内 `now = time.time()`（原 `:9903`）保持不变以免扩大 diff 面；新代码一律用 `now_utc()`（RULE-SCHEMA-TZ 合规）。若要把 TTL 判据也接到 freeze_time，属下一轮小改。
8. **新建件登记面**：`test_stash_drop_ownership_cure.py` 已带 14 字段头（tests/ 对 CREATE-GUARD creation_token 豁免）；`add_module_translation.py` 的大白话简介登记与 depgraph 节点登记（RULE-DEPGRAPH）需要注册表 yaml 写面——本车道禁碰，请总包在集成批内完成，否则 TRANSLATION-COVERAGE gate 会拦。
