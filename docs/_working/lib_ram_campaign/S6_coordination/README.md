---
ttl: task_bound
title: S6 与 st-p1b 在途 reconciler 的协调面 · 图书馆内存常驻缓存战役（谁在改什么 / 重叠区 / 刷新挂点 / untracked-phantom 取证）
created: 2026-09-29
sid: st-libram-s4s7-20260929
status: 挖矿中（盘面态与 diff 全部亲验；对方意图为读档推断，见 §7）
---

# S6 协调面（只读取证，零改动）

**本簿使命**：本战役要改的读侧件与 st-p1b 在途的刷新管线**同处 `src/zephyr/library/` 一个目录**。
不取证清楚就动工 = 连坐冲突 + COMMIT_SCOPE 误判 + 对方 staged 差异被我吸收。
本簿给出：三方现状 → 三列重叠表 → R2 刷新挂点（零新增计划任务）→ untracked-phantom 硬证据。

## ① 真源（协调事实的唯一来源=盘面 git 态，不是任何人的记忆）

判 tracked 铁律：本仓有 76+ 大文件从未入 git 的先例，`is_clean` 对其返回空=假干净，
**必须用 `git ls-files --error-unmatch <path>`**——判据出处
`docs/_working/fms_overhaul/S8_conflict_surface/README.md:55`（§⑤14 untracked-phantom 区）。
本簿 §⑤b 全部按此法实测。

## ② 写者（谁在写这些件，盘面实证）

`git status --porcelain` [亲验 2026-09-29，分支 `dev`，`git rev-parse --abbrev-ref HEAD`=dev]：

```
D  scripts/governance/generators/check_library_tri_consistency.py      ← 暂存区被删（HEAD 版 368 行）
?? scripts/governance/generators/check_library_tri_consistency.py      ← 同名文件又以 untracked 存在盘上
?? scripts/governance/generators/check_library_tri_consistency.py.tmp.22232.a10f663735ee  ← CAS 残渣
MM scripts/governance/generators/generate_front_door.py
MM scripts/governance/generators/generate_library_index.py
M  scripts/governance/generators/regen_clean_check.py
MM src/zephyr/library/ledger_schema.py
MM src/zephyr/library/librarian.py
MM src/zephyr/library/library_regen_reconciler.py
```

`MM` = 既有 staged 又有 unstaged 改动。**本战役读侧改型的三个目标件里两个正在被改**
（`librarian.py` / `ledger_schema.py`），唯一干净的是 `src/zephyr/library/lookup.py`（未出现在 status 中）[亲验]。

对方在改什么（`git diff -U0` 逐 hunk 读，非猜）[亲验]：

| 件 | diff 量 | 内容（对方意图，读档自注释） |
|----|--------|------------------------------|
| `src/zephyr/library/library_regen_reconciler.py` | +84/-约2（untracked+staged 两侧） | 新增 `LibraryIngestShrinkError`(:50)、`_count_nonempty_consumers`(:53-60)、**`ingest_with_shrink_guard`(:62-98)**（全量入账前后对 `potential_consumers` 非空计数做快照对比，缩水→先落 audit 事件再 raise）；`__all__` 扩(:36-40)；INVARIANTS 追加"全量入账必经缩水闸"(:8) |
| `src/zephyr/library/librarian.py` | +12/-4 | `act()` delete 分支透传 `successor_of`(:195-197 附近)；upsert 冲突分支**裸参数重传第 15 占位**(:189-191, :239-240)——修"引用 EXCLUDED 的守卫形同虚设"根因 |
| `src/zephyr/library/ledger_schema.py` | +26/-8 | `lib_assets` 增 `successor_of text`(:80)；`_SQL_UPSERT_ASSET` 冲突分支改 `COALESCE(%s::text[], ...)(:130)`；新增 `_SQL_COUNT_NONEMPTY_CONSUMERS`(:135-138)；`_SQL_MARK_DECEASED` 增列(:151)；**`_SQL_LOOKUP` 投影列增 `disposition_authority, successor_of`(:161)** |
| `scripts/governance/generators/generate_library_index.py` | +19/-? | 馆页生成随 `successor_of` 展示联动（墓碑去向渲染） |

> **与本战役的第一号硬重叠**：`_SQL_LOOKUP` 的**投影列集正在被改**（+2 列）。
> 世代快照的 schema（S3 §4.2 提"lib_assets 全 21 列"）与缓存行对象（S2）必须**以改后列集为准**，
> 任何在 `ledger_schema.py` HEAD 版上写死的列清单都会在合并瞬间错位。施工批开工前必须先
> `git diff src/zephyr/library/ledger_schema.py` 复核列集（写进 §⑥ 净零条款 4）。

## ③ 消费者（刷新事件链现状，逐跳 file:line）

```
commit 落地
  └─ GitCommitGateway.run_post_commit_reconcile
       src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:1086（P2-3 异步化：默认 spawn detached worker，
       env ZEPHYR_RECONCILE_SYNC=1 强制同步；异步口 :1057-1083，同步口 :1097-1105,1114）
  └─ 规格发现：reconciliation_registry._EXTERNAL_SPEC_MODULES 显式列名 + importlib 惰性 import
       src/zephyr/governance/audit/reconciliation_registry.py:650（"zephyr.library.library_regen_reconciler" 在册）
       src/zephyr/governance/audit/reconciliation_registry.py:663（import ...  # noqa: F401）
       钩子入口签名 src/zephyr/library/library_regen_reconciler.py:190-194（make_external_reconciler_spec）
  └─ LIBRARY-REGEN ReconcilerSpec（gate_id="LIBRARY-REGEN", priority=200, file_ops={read,write}）
       library_regen_reconciler.py:180-188
       trigger=_TRIGGER_PREFIXES = ("src/","scripts/","data/","docs/01_policies_and_standards/_registry/")  :43
       reconcile 四步：① collect_all() + ② ingest_with_shrink_guard（:127-138）
                     → ③ 子进程跑 generate_library_index.py（:141-155, timeout=300）
                     → ④ 子进程跑 check_library_coverage.py（:157-172）
```

另两条链**不在** post-commit 事件链上（`[STARTUP] manual`）：
- `check_library_tri_consistency.py:6,9`（[TTL] permanent、manual、exit 0/1/2 语义 `:13`）——
  其 [CONSUMERS] `:5` 自述"S1 FMS-HYGIENE 门（设计消费方）；reconciliation_registry 挂接（**待 st-p1b 落地后经其通道追加**）"，
  [MODIFY-GUARD] `:8` 明写"registry 挂接避让 st-p1b，落地后追加"→ **它当前无自动触发者，是人工/后续挂接的尺**；
- `regen_clean_check.py:17,30-32`（FMS-REGEN-CLEAN 数据源，`--staged` 门模式），其消费者见
  `scripts/generate_manifest.py:5`；该件盘面态 `M `（staged 已改）[亲验]，**也是他队在途件**。

**各件职责一句话**（读档自述，交叉验过盘面）：

| 件 | 现在做什么 | 谁触发 |
|----|-----------|--------|
| `library_regen_reconciler.py` | **刷新管线**（写）：增量采集→入账（带缩水闸）→馆页重生成→coverage 对账；全程 fail-soft，只出 clean/warn/skip | post-commit 事件（`:8` INVARIANTS 明写禁 cron/Timer/sleep-loop） |
| `reconciliation_registry.py` | reconciler 注册与调度总表 + 结果落盘 `.runtime/reconcile_reports/` | 被 gateway 调用 |
| `library_new_module_reconciler.py` | **不存在**（见 §⑤b 幻影取证） | — |
| `check_library_tri_consistency.py` | 三层断言尺（账↔视图↔盘，含 regen-clean 子步），**纯只读不修不写账**（`:7`） | manual（挂接待 st-p1b） |
| `generate_library_index.py` | 七馆页+INDEX 生成器，产出=生成视图非真源（`:8`），并经 `Librarian.act` 自登记 | 被 reconciler ③ 步子进程调 + manual |

## ④ 漂移史（这条协调面以前怎么翻的车）

1. **供数轴被清零事故（裁-07）**：09-24~27 三轮全量 ingest 把人工回填的 68 资产 `potential_consumers` 冲空，
   根因=upsert 冲突分支引用被 VALUES COALESCE 预空的 `EXCLUDED`（`ledger_schema.py` 注释 `:105-112` diff 实证；
   守卫实现 `library_regen_reconciler.py:62-98`）。
   → **对缓存战役的直接含义**：这类"入账前后计数对账"就是**写侧校验读真源**的活例——
   它若读世代缓存，缩水事故将永久隐身。S4 §⑤ 的"不可缓存"由此从原则升级为**点名条款**。
2. **CAS 残渣**：`check_library_tri_consistency.py.tmp.22232.a10f663735ee` 在盘（热文件写中断遗体，
   根宪法 §1.13 的 `safe_write_text` 面）；S1 簿已记 59 条 .tmp 被当真源引用的前科（转引 S3 §3.4 `:60`）。
3. **避让清单与真实盘面不符**（本簿最重要漂移发现）：任务书/避让六件里的
   `library_new_module_reconciler.py` **盘面无此件**，而**真正在改的** `generate_library_index.py` /
   `regen_clean_check.py` / `check_library_tri_consistency.py` **不在避让清单上**。
   → 照清单避让 = 让开一个不存在的文件，同时踩进三个在途件。**返工风险源**。
4. **视图层无世代锚事故**：S5 簿（fms 侧图书馆接线簿）§2.2 三快照漂移，转引自 S3 §3.5 `:58` [读档]。

## ⑤ 冲突面

### a) 三列表：本战役改哪个 / 对方(st-p1b)改哪个 / 重叠区

| 资产 | 本战役要改（施工面） | 对方在途改动（盘面实证 §②） | 重叠区与处置 |
|------|---------------------|------------------------------|--------------|
| `src/zephyr/library/ledger_schema.py` | **不改**（世代戳/S1 案 B 用 `max(event_id)`，零 DDL；S1 §避让） | ✅ 正改：`successor_of` 列 + `_SQL_LOOKUP` 投影 + `_SQL_COUNT_NONEMPTY_CONSUMERS` | **高重叠（同文件不同 hunk）**：本战役只**读**它的 SQL 常量做快照 SELECT；开工前必须 rebase 到对方落地后，或按"列集动态取"写（禁硬编码列清单） |
| `src/zephyr/library/librarian.py` | S2 世代缓存层若挂在 `Librarian` 读方法上 → **要改**（`lookup()` 旁路） | ✅ 正改：`act()` delete/upsert 冲突分支 | **最高危**：对方 [CONSUMERS] 面含 reconciler，改同文件必连坐。处置=缓存层**新件 `src/zephyr/library/generation_cache.py`（拟建）不碰 librarian.py**，只 wrap `Librarian.lookup` 调用方（即改 `lookup.py`，它当前干净） |
| `src/zephyr/library/lookup.py` | ✅ 要改（`lookup_assets` 读世代 + A4 词表随代 + close→release） | ❌ 未在途（不在 status） | **本战役主战场，窗口干净**——但 `fms_overhaul/00_orchestration.md:56` 声明 FMS B3 已把 successor_of 落在 `ledger_schema.py`+`lookup.py`（"其未触碰"）→ 该声明与当前 `librarian.py`/`ledger_schema.py` 在途态**部分失效**，`lookup.py` 是唯一还成立的免碰区。**开工优先级：先 lookup.py** |
| `src/zephyr/library/library_regen_reconciler.py` | ❌ **不改**（避让件） | ✅ 正改（+84 行缩水闸） | 零交集：世代刷新**不在此挂 invalidate**（S2 §91 同判、S3 §63 同判，三簿一致） |
| `src/zephyr/governance/audit/reconciliation_registry.py` | ❌ **不改**（避让件） | 未见于 status（但 `:650,663` 是其注册位，对方新增 reconciler 必改此） | **挂点否决**：新增外部规格必须改这个列名清单（`:650`）→ 任何"新 reconciler 刷缓存"的方案都撞避让件，故 §⑥ 判据选"读时版本比对" |
| `scripts/governance/generators/generate_library_index.py` | ❌ 不改（S3 案 B 曾提议挂尾步刷快照） | ✅ 正改（+19 行） | **S3 案 B 当前不可用**（撞在途件）→ 刷快照只走 S3 案 A（`scripts/backup/library_ledger_backup.py` 尾步，该件未在途且不在避让清单） |
| `scripts/governance/generators/check_library_tri_consistency.py` | ❌ 不改 | ⚠️ 被 staged 删除 + 盘上 untracked 重建（§⑤b） | 本战役蓝侧验收尺之一；**尺子本身状态不稳** → 见 §⑦ 缺口 3 |
| `data/library_snapshots/`（拟建） | ✅ 新建（S3 判家） | 无 | 需 `.gitignore` 循 `data/drift_baselines/*` 先例（S3 §2.1 判家证据链） |

### b) untracked-phantom 硬取证 [亲验，逐件 `git ls-files --error-unmatch`]

| 路径 | 盘上 | tracked | 判读 |
|------|:---:|:---:|------|
| `src/zephyr/governance/audit/library_new_module_reconciler.py` | **NO** | **NO** | **幻影避让件**：盘面无、index 无。它被以下在册引用：`docs/_working/fms_overhaul/00_orchestration.md:56`、`S8_conflict_surface/README.md:16`、`capability_canonical_file_registry.yaml:53299`、`fms_deadref_baseline.yaml:9616`、`wave13_chief3/inbox/byte_ledger/01_byte_ledger.md:251`（18470 字节 p1b 版 vs 其余三道 17647） |
| `scripts/governance/generators/check_library_tri_consistency.py` | YES | **NO**（index 里已删） | **假干净高危**：HEAD 有 368 行版、暂存区标 `D`、盘上是新 untracked 内容 → 任何 `is_clean` 判据对它返回空；本战役若在其上跑验收，结果不可信 |
| `src/zephyr/library/library_regen_reconciler.py` | YES | YES | 正常在途（MM） |
| `src/zephyr/governance/audit/reconciliation_registry.py` | YES | YES | 正常 |
| `scripts/governance/generators/generate_library_index.py` | YES | YES | 正常在途（MM） |

**幻影判定的两种可能（未裁定，交总筹）**：
(a) 该件在 st-p1b 的 **session worktree** 里尚未 merge 回主区（根宪法 §0.3 默认 worktree 施工）→
则"避让"是对的，只是主区看不见；(b) 它是**计划新建件**（byte_ledger 记 4 道会话同 sha 不同字节，说明曾被实体化过）。
→ **无论哪种，本战役都不得把协调假设建立在"读得到的文件"之外**：判据=每次开工前重跑
`git ls-files --error-unmatch` + `git status --porcelain <六件>` 双验，并把结果写进施工批晨报（§⑥ 条款 4）。

## ⑥ 净零方案 + R2 刷新挂点（禁新增计划任务的落法）

**挂点判定（本簿结论）**：世代**失效**不需要事件，世代**落盘**才需要事件。

| 层 | 触发 | 是否新增计划任务 | 证据/理由 |
|----|------|:---:|----------|
| **R2 世代失效与重建**（内存） | **读时版本号比对 + single-flight**（Owner §2）——每次读比对 `max(event_id)` 水位（S1 案 B），跳变即单飞重建 | **零** | 版本水位查询即 `ledger_schema.py:135-138` 同款单查（S3 §4.3 步骤 1 实测 3.4ms），**且这条查询必须走 PG 现读**（读缓存判版本=循环自证，S4 §⑤）；无需任何写者通知，天然零改动避让 reconciler |
| **R3 快照落盘**（磁盘） | 搭 S3 案 A：`scripts/backup/library_ledger_backup.py` 成功尾步（既有 schtasks `ZephyrAlpha_LibraryLedgerBackup` 链，`library_ledger_backup.py:21` 自述"调度走 schtasks（系统级调度，reaper keep 登记放行）"） | **零**（复用既有） | S3 案 B（`generate_library_index.py` 尾步）**当前否决**——该件在途 MM（§②） |
| 写侧即时 invalidate | **否决**：不在 `Librarian.act` 加钩子，不在 reconciler 加钩子 | — | 与 S2 §91、S3 §63 三簿一致；且改 `librarian.py`/`library_regen_reconciler.py` 必撞在途 diff（§⑤a 高危行） |
| 新增 reconciler 规格 | **否决**：`_EXTERNAL_SPEC_MODULES` 是列名清单（`reconciliation_registry.py:650`），加名=改避让件 | — | 根宪法 §9.3 事件触发虽满足，但冲突成本 > 收益；读时比对已覆盖正确性 |

净零四条（施工批须守）：
1. 世代失效语义**不建新真源、不建新注册表**：版本水位唯一口径=`lib_events.max(event_id)`（S1 案 B）。
2. 不新增 reconciler / 不改 registry / 不改 `library_regen_reconciler.py`（§⑥ 表已给否决理由，防后来者"顺手加个刷新的钩子"）。
3. 新建件至多一个：S2 已定名 **`src/zephyr/library/ledger_cache.py`**（对齐 `S2_librarian_cache/README.md` §4.2 实现位 `:120`
   与常量位 `:145`，本战役其他簿不得另起 `generation_cache.py` 之类型名——两名并存=第二真源）。
   须过三件套：creation_token + 头部 14 字段 + `add_module_translation.py` 大白话简介
   （脚本真身 [亲验 tracked] = `scripts/governance/d3_metadata/add_module_translation.py`，非根宪法裸名所指位置）；
   并声明替代了什么（净零 §4.1）——建议声明"内收 `lookup.py:51-78` 每查询全量 YAML 解析"为其替代收益。
4. **开工前双验仪式**（本簿立法，写进施工批 checklist）：
   `git status --porcelain src/zephyr/library scripts/governance/generators` +
   对避让六件逐个 `git ls-files --error-unmatch`；两项输出贴进晨报，
   与 §⑤b 表不一致即**停手上报**（防在幻影上排产 / 防在途件被吸收）。

## ⑦ 自审闸三态

**状态：`未干`（盘面事实已挖干；"对方意图"一侧仍是读档推断，不能当批文用）**

挖干（可直接指导施工序）：
- 五件现状、职责、触发链逐跳 file:line（§③），post-commit 异步 worker 语义（`git_commit_gateway.py:1086` + `ZEPHYR_RECONCILE_SYNC`）；
- 在途 diff 内容**逐 hunk 读过**（§②），并据此点名 `_SQL_LOOKUP` 投影变更为本战役第一号硬重叠；
- untracked-phantom 三行硬判据 [亲验]，含 `library_new_module_reconciler.py` 盘面无件的反例（§⑤b）；
- 避让清单与真实在途面不符（§④3）+ 由此否决 S3 案 B（§⑤a）；
- R2 挂点结论：**读时版本比对（零事件）+ 落盘走备份链（零新计划任务）**，与 S2/S3 两簿同判不冲突。

缺口：
1. **[未取证] st-p1b 的会话状态**：`python -m zephyr.trading.process_reaper --status` 与
   `lock_files.py` 现状**本会话未跑**（只读战役，且 §0.2 属写操作前置检查，非本簿取证义务）→
   无法判断 `MM` 是"活跃施工中"还是"已弃的遗留脏"。**这条必须总筹裁**，因为两种情况下的排产序完全相反。
2. **[未取证] `library_new_module_reconciler.py` 是否在 st-p1b 的 worktree 里**：
   未枚举 `.runtime/sessions/*/worktree*`（越界读他队工作区）。§⑤b 的 (a)/(b) 二选一因此悬置。
3. **[状态不稳] 蓝侧尺的可信度**：`check_library_tri_consistency.py` 处于"index 已删 + 盘上 untracked"态，
   其盘上版与 HEAD 版差异未 diff（只确认行数不同：HEAD 368 行 vs 盘上 253+ 行）。
   → S7 蓝侧"两套既有尺仍绿"这一条**目前无法定基线**（已在 S7 §蓝侧标注为阻塞项）。
4. **[未读] `reconciliation_registry.py` 的 reconcile_for 调度细节**（priority 排序、异步 worker payload 目录、
   `is_exempt_reason` 与 capability_lookup_bypass_policy 的共用面 `capability_lookup_bypass_policy.py:14` 已见，未回读）。

受阻：无（全部只读取证成功；仅一次 `find . -iname` 全仓遍历超时，已改用定向 `[ -e ]` + `git ls-files` 复现同一判据）。
