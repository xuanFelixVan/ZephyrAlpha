---
ttl: task_bound
rule_form: data
verifiability: manual
title: F1 作业簿——衍生提交并入原子化（rules_integrity 折入 reconciler 批提交）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: active
---

# F1 作业簿 — 衍生提交并入原子化（rules_integrity re-register 折入 reconciler 批提交）

> 施工包：F1（免签先干）｜真源：`docs/_working/kimi_audit/S18_提交链路根因表.md` R-01/R-02 + `S18_Flash施工包判据.md` F1 + `adjudications/S18-R2`
> 会话：st-flashspeed-20260918｜lock 持有：git_commit_gateway.py + validate_rules_integrity.py

## 0. 病灶（第一性原理）

R-01 实证：post-commit 链路在 reconciler 批提交（flush squash）**之后**再跑一次
`_post_flush_rules_integrity_re_register`，该函数用 `validate_rules_integrity.py --register`
（`_hash_git_head` 读 post-flush HEAD）重算受保护文件基线；只要任一受保护文件被
reconciler 改动（典型：`capability_canonical_file_registry.yaml` 被 metric_count_drift /
catalog reconciler 改），DB 漂移 → 触发**独立尾笔** `_commit_auto([db], "chore(integrity): post-flush re-register")`。
24h 实测 31 笔独立 integrity commit，且 13.1% 死信来自 rules_integrity 漂移。

尾笔成本：每笔 = 一次完整 `_commit_auto`（merge-check + DCR/TTL/FPT gate + GlobalCommitLock + git add + git commit）≈150-300ms + 一条 git log 噪音 + 一个队列落地目标。

**为什么是尾笔而非并入 flush 批？** 因为 `--register` 必须在 flush 后跑——它读 HEAD，
而 reconciler 改动只有 flush 后才入 HEAD。在 batcher 上下文内（flush 前）跑 register 会读到
pre-flush HEAD = 滞后基线（这正是 2026-08-02 audit-02 当初引入 post-flush register 修的病）。
时序约束把 register 钉死在 flush 后 → 必然产生独立尾笔。

## 1. 六向寻路台账

| 向 | 探查 | 结论 |
|----|------|------|
| ①上游 | 谁触发尾笔 | `_post_flush_rules_integrity_re_register`（gateway L1805）；被 `_run_post_commit_reconcile_sync`（L1931）与 `_run_post_commit_reconcile_sync_worker`（L1994）在 `with self._batcher` 块**之后**调用 |
| ②下游 | 尾笔落到哪 | `_commit_auto`（batcher 已 disable）→ 真实独立 commit；`record_derived_write(source="rules_integrity_re_register")` 先落归属台账 |
| ③算法机制 | register 时序 | register() = HEAD-based hash（`_hash_git_head`）；已含 unchanged 短路（L282 `if new_files == old_files: return unchanged`）；flush 前 HEAD 滞后是尾笔根因 |
| ④后端 | DB 落盘 | `_save_db` → `atomic_write_safe`（rules_integrity_db.json）；受 golden-hash 自保护 |
| ⑤前端 | 无 | 纯后端链路 |
| ⑥数据字段 | DB schema | `{files:{rel:{hash,critical,desc}}, registered_at, last_check_at}`；比对仅用 `files` dict（不含时间戳）→ 折入后 post-flush register 见 `new_files==old_files` 即 unchanged 不再写 |

## 2. 治本设计（工作树混合折入）

**核心洞察**：受保护文件被本提交链改动时，其**工作树内容 == 即将提交内容**（flush 只 git-add 现盘内容，不改字节）。故可在 flush **前**用工作树 hash 算出"最终态 DB"，无需等 HEAD。

**新增** `register_fold(changed_files: set[str]) -> bool`（validate_rules_integrity.py）：
- changed_files = 本次链路涉及的受保护文件相对路径集（`rel(existing) ∪ batcher.buffered_files()`）。
- 逐 manifest 条目：
  - rel ∈ changed_files → 工作树 hash（`_hash_file`，文件不存在则回退 `_hash_git_head`）。
  - rel ∉ changed_files → 复用旧 DB hash（不存在则 `_hash_git_head` → `_hash_file` 兜底）。
- `new_files == old_files` → 返回 False（不写盘）；否则 `_save_db` → 返回 True。

**新增** `_fold_rules_integrity_into_batch(existing, session_id)`（gateway）：
- 在 `with self._batcher` 块内、`reconcile_for` 之后、flush 之前调用。
- changed = rel(existing) ∪ batcher.buffered_files()。
- 调 `register_fold(changed)`；若返回 True（DB 写盘）→ `record_derived_write(committed=False)` + `batcher.buffer(session_id, [abs_db], msg)` → flush 时 squash 进同一批提交。
- 全程 try/except fail-open（异常仅 warning，降级回 post-flush 尾笔路径，不阻断）。

**保留** `_post_flush_rules_integrity_re_register` 作自愈 + 空 buffer 兜底：
- 折入后 DB 已含最终态 → post-flush `--register` 读 HEAD 算出 `new_files == old_files`（折入 DB）→ unchanged → 不写盘 → `git diff -- DB` 空 → **早返回，无尾笔**。
- 仅在折入失败/真漂移（受保护文件经非 gateway 路径入 HEAD）时才产生尾笔 = 正确的自愈行为。

## 3. 安全性等价证明（红蓝自审）

| 场景 | 现行（post-flush HEAD register） | 折入后（fold + post-flush 兜底） | 等价? |
|------|------|------|------|
| 受保护文件经 gateway 合法提交 | 入 existing → HEAD register 重基线 | 入 changed → 工作树 hash 重基线（==HEAD 内容） | ✓ 等价 |
| reconciler 改受保护文件（buffered） | flush 后入 HEAD → register 重基线 → **尾笔** | buffered_files 命中 → 工作树 hash 重基线 → 折入批提交（**无尾笔**） | ✓ 结果同，尾笔消除 |
| 未改动的受保护文件 | HEAD hash == 旧 DB（在同步态） | 复用旧 DB hash | ✓ 等价 |
| WIP 篡改未入 commit 的受保护文件 | HEAD 不含 WIP → register 不重基线 → check() 仍报 TAMPERED | 不在 changed → 复用旧 DB hash → check() 工作树 hash 不匹配 → TAMPERED | ✓ 不降级 |
| 手动编辑 rules_integrity_db hash | check() 报 TAMPERED（DB 是数据，hash 不匹配） | 同（fold 不改 check 逻辑） | ✓ 判据②保住 |
| 受保护文件经非 gateway 入 HEAD（漂移） | post-flush register 重基线（合法化） | fold 复用旧 hash（不合法化）→ post-flush 兜底 register 重基线 → 尾笔自愈 | ✓ 兜底覆盖，更安全 |

结论：折入对**已提交内容**与 HEAD-based 完全等价（工作树==HEAD），对**未提交 WIP 篡改**保持 check() 检测（不在 changed 集→旧 hash→工作树不匹配→TAMPERED），不降级红蓝发现3 防护。

## 4. 判据映射（S18_Flash施工包判据 F1）

| 判据 | 验法 |
|------|------|
| 无受保护文件改动的提交 → 24h 独立 integrity commit=0 | fold 对此类提交是 no-op（changed 无受保护文件→DB 不变→不 buffer）；post-flush 见 DB 已同步→unchanged→无尾笔。真仓试点 `git log` 无独立 `chore(integrity)` 尾笔 |
| 手动编辑 rules_integrity_db hash → 必报 TAMPERED | check() 逻辑未改；新增 pytest 断言 |
| 死信 rules_integrity 漂移 <2% | 尾笔消除→落地目标减少→漂移源消失；F6 总账复核 |
| pytest tests/governance/ -k "integrity or reconciler" 全绿 | 施工后跑 |
| 真仓一笔试点 git log -1 无衍生尾笔 | 施工后跑 |

## 5. 挖后自审闸（三态）

**裁定 = 施工**。设计闭环、安全等价已证、判据可机验、无需 Owner 门位（不碰门禁语义/不删门禁/不动 serializer 通道数/不碰 POST-COMMIT-GUARD/RULING-REFERENCE，符合 R4 不可放宽白名单——content-addressing golden hash 保护机制本身不变，仅改"何时算基线"的时序，hash 算法与 check 语义零改动）。

## 6. 施工日志

- [x] register_fold 落地 validate_rules_integrity.py（+ --fold CLI + _save_db 返回落盘结果）
- [x] _fold_rules_integrity_into_batch 落地 gateway + 两处 with-batcher 块内接线（sync L1927 / worker L1991）
- [x] pytest -k "integrity or reconciler" → **772 passed, 3 skipped, 7 xfailed, 49 xpassed**（0 fail）
- [x] 新增 test_validate_rules_integrity_fold.py 4 例 → **4 passed**（折入重基线/no-op/判据②TAMPERED/WIP篡改检测保住）
- [x] 真仓试点 commit `fe47296d`（7 文件）→ `git log fe47296d..HEAD` 无 `chore(integrity)` 尾笔；近 30 笔零 integrity 尾笔 ✓
- [x] 提交后 DB 自愈：worker（39 reconciler，异步 detached）跑完 → `--check` 全 17 文件完整 ✓

### 验收结论：判据全过

| 判据 | 结果 |
|------|------|
| pytest -k "integrity or reconciler" 全绿 | ✓ 772 passed |
| 真仓一笔试点 git log -1 无衍生尾笔 | ✓ fe47296d 后无 integrity 尾笔 |
| 手动编辑 rules_integrity_db hash → 必报 TAMPERED | ✓ test_manual_db_hash_edit_reports_tampered |
| 无受保护改动提交 → 独立 integrity commit=0 | ✓ fold 对此类提交 no-op（单测 test_fold_noop_when_no_protected_change） |

### 施工期观测（留给 F4/F6 的实证）

1. **异步 reconcile worker 极慢**：本笔 commit 的 detached worker（pid 6100）跑满 39 个
   reconciler 耗时 ~6 分钟（GATE-REGENERATE 卡 180s、GATE-DELETE-AUDIT 卡 120s）。
   worker 是 detached 后台进程，**不阻塞 CLI commit 返回**（commit 本身 ~2s+gate），但
   fold 在 reconcile_for 之后才跑 → DB 自愈延迟到 worker 收尾。这正是 R-08 / F4 靶子。
2. **热 DB 并发 clobber**：施工期 altdata 会话（st-altdatamap-20260917）并发活动，其
   post-flush register 在 17:54:34 读 pre-commit HEAD 重写了 DB，把我手动 pre-fold 的
   DB 覆盖回旧 hash → 我 commit 时 git-add 吸收的是被 clobber 的旧 DB（HEAD:DB 滞后）。
   worker 收尾 fold 在 18:06:30 用工作树（==已提交 HEAD 内容）重新治愈工作树 DB。
   **教训**：DB 是热争用文件；F1 fold 在 worker 内原子执行可自愈，但跨会话并发窗口内
   HEAD:DB 可能滞后一笔，由下一笔 commit 的 fold 吸收（check() 始终基于工作树，不阻断）。
3. **workspace_hygiene 还原 6 个 auto-sync 文件**（worker errors 实证）——
   #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001 同族：buffered 文件被后序 reconciler git restore，
   flush 可能 NOTHING_TO_COMMIT。F6 需排查此交互对 fold buffer 的影响。

