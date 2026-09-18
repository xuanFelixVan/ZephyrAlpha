---
ttl: task_bound
completes_when: 规则与审计一条龙战役波1-波5 全部收口，且本册 §3 待裁清单每一条都被 Max/Owner 判掉或明确判不办并留痕
---

# 规则与审计一条龙 · 施工台账（总包代持 · `st-fullflow-20260918`）

> **本册是什么**：`docs/_working/2026-09-18-rule-audit-master-construction-plan.md`（Max 已封口的裁定与施工卡）
> 的**施工侧事实台账**。方案与 gate-identity 详案是裁定真源，本册**不改它们一个字**，只记三件事：
> ① 施工中发现"方案事实前提不成立"的**修正表**（§4）；② 因此触发的**停手与待裁**（§3）；③ 各车道 §5 回执全文（§2）。
> 编号用 `R-A*`，与全流通战役的 `R-0*` 不混。

## 1. 总包裁定（施工侧，不含价值判断）

- **R-A1｜WP1 站点二的普查断言被现场实测推翻 ⇒ 原处方作废冻结**。
  方案 §1.3/§7 把"`gate_persistence.py:215` INSERT 列名与实表不符、每次调用必失败"标为 `[亲验]`。实测：
  该写入端的目标库**根本不是 `governance.db`**，而是 `data/drift_audit/drift_events.db`
  （`gate_persistence.py:54` 自定路径），该库 `gate_decisions` 真实列 = `(id, module_id, gate, decision, detail, decided_at)`，
  **与 INSERT 逐列吻合**；车道用真实公共 API 在临时 project_root 上**写入成功并读回 1 行**。
  而 `governance.db` 里另一张同名异构表 `gate_decisions` 列 = `(decision_id, gate_id, decision, reason, decided_at, decided_by)`
  ⇒ 普查把**两个不同 DB 里的同名表**当成一张。**照处方改列名的唯一后果是把一条能用的写通路改成必炸**
  （实测 `OperationalError: table gate_decisions has no column named gate_id`）。
  ⇒ 总包处置：`wp1` 处方冻结，站点二判"不修"，交 Max 按 C-2 选方向。
  [车道亲验 + 总包独立只读复核两库 DDL 与列名，均一致]

- **R-A2｜★ 新发现一项方案未记的破坏性地雷（C-0），优先级高于本 WP 原目标**。
  `RollbackVerifier.heal_db_consistency` 的 **tasks 支路**：
  ① 默认目标库就是生产 `data/databases/governance.db`（`rollback_verifier.py:165`）；
  ② 代码里 `valid_statuses` 只认 5 个值（:183），而真源词表 `_DDL_TASKS` 声明 **10 个**合法态
  （`sqlite_schema.py:87-91`）⇒ `READY/BLOCKED/WAITING/RETRY/VERIFIED` 全被判为脏；
  ③ 生产 `tasks` 表**实际没有继承 status 的 CHECK** ⇒ 误改不会被库拦下；
  ④ 现值分布实测 `BLOCKED=152 / READY=78` ⇒ **230 行任务状态会被静默改成 FAILED**。
  **当前唯一保护 = 全仓零生产调用方**（`git grep` + 未跟踪文件 fs grep 双尺，仅 2 个定义文件 + 3 个测试文件命中）。
  ⇒ 总包独立复核结论：生产库 `tasks` DDL 里 9 处 CHECK 全在 `namespace/seq/actual_hours/is_deleted/approval_required/
  requires_rb_check/idempotent/evolution_policy/estimate_hours` 上，**status 一栏确实无 CHECK** ⇒ C-0 成立且严重。
  ⇒ **施工侧即时措施（不等 Max）**：本战役**波2/波3 任何车道不得调用或扩接 `heal_db_consistency`**，
  WP2/WP3 若要写 gates/gate_decisions 台账，须先证明不共用该 verifier；`scripts/rollback.py` 不得新增 `heal/verify` 子命令。
  真正处置（改派生 or 退役）待 Max 判（C-0）。

- **R-A3｜WP12 证明 D-12 处方是对外零效应的空改动 ⇒ 连带作废波2/波3 的验收观测面**。
  `GATE-RULE-CATALOG` 子 spec 被 `_compose_reconcilers("GATE-RULE-AUDIT", …)` 合成，落库 `gate_id` 永远是父名；
  且 `_trigger_catalog` 的扩展名集 ⊂ 同复合体 `_trigger_arch_refs` 的 `REFERENCE_TEXT_EXTS` ⇒ 父 trigger 恒等。
  实测三组：真 790 笔提交 A/B **子判定变 248 笔 / 父判定变 0 笔**；
  `reconcile_execution_log` 里 `gate_id='GATE-RULE-CATALOG'` **= 0 行**（总包独立复核：库总行 77512、该 gate_id 0 行、
  父 `GATE-RULE-AUDIT` 1870 行、distinct gate_id 63）；生产库实证"只改 `docs/01_policies_and_standards/` 非 rules 文件的提交"
  早已触发 catalog 重生并 auto-commit ⇒ **D-12 的"永不触发"依据被证伪**。
  ⇒ 总包处置：`wp12.patch` 冻结不应用；**波2（WP2/WP3）与波3（WP4）开工前必须先换验收面**——
  凡以"某子门 gate_id 在 `reconcile_execution_log` 出行"写的判据都不可判，改判"父 gate_id 的 detail 串 + 生成物 hash"。

- **R-A4｜站点一是"幻影 fixture 共谋"的实例，值得当判据复用**。
  `tests/rollback/test_rollback_verifier_root.py:124/140/155` 与 `_unit.py:56` **自建 `gates(gate_id, result)` 幻影表**
  （生产库无 `result` 列），再断言 `gates_fixed == 1` ⇒ 该写入端在生产结构上 100% 抛 `IndexError` 并被内层 `except` 吞掉，
  而 CI 52 例全绿。车道另证：**按处方改成 `passed` 后**，`gates` 的 `CHECK(passed IN (0,1))` 使非法值物理上不可入库
  ⇒ 得到的是一台**构造上永不为真的门**（"恒真返回比缺功能更坏"的又一实例），且 root:148/unit:178 两例当场转红。
  ⇒ 与 `sqlite_schema.py:949` "SSoT 铁律：测试是真源"正面冲突 ⇒ 谁让步交 Max 判（C-1）。

- **R-A5｜本册不修 Max 原文，改立 §4 事实修正表**。
  方案 §7 的 `[亲验]` 分级里有两条经现场实测为假/不可实现（站点二、D-12 依据句）。改 Max 文档越权，
  但**后续车道若照原引用施工会造出新破坏** ⇒ 修正只在本册 §4 落地，并在**每本新车道任务书里带上 §4 对应行**。

- **R-A6｜§6.2⊥WP15.4 的矛盾由**门禁本体**裁出结果，不是解释题**。
  WP15 实测：`check_protected_paths.py:74` 把 `docs/01_policies_and_standards/rules/` 写进 `PROTECTED_PATTERNS`
  （注释"重大修改须 Owner 审批"），由 `PROTECTED-PATHS`（priority=28）import 复用硬阻断；
  逃生仅两条：`[ARCH-APPROVAL:ARCH-*]` 且 id **须在 `architecture_issue_registry.yaml` 在册**，或 env 紧急绕过。
  而 9 条陈旧指向的靶文件 **9/9 全在 `rules/` 下**（7 个 `trae_*.yaml`）。
  ⇒ 车道取"§6.2 + 门禁更硬"解释，**9/9 只出案卷、零改动**，未自造 approval id、未用 env 绕。总包认同该解释。
  请 Max 三选一（任一即可盲执行，替换文本已备好）：① 登记 1 个 `ARCH-*` issue 供 9 条共用、仍一条一提交；
  ② 判 Max 直改；③ 拆口径——机器列表值豁免保护、散文/changelog 保留人工（顺带裁 `archived` 两条）。
- **R-A7｜方案与任务书给的案卷路径是错的（我的派工错误之二）**。
  `rules_enforcement_census.json` 不在 `st-ruledisp-20260918/staging/`，真身在 **`st-auditdoc-v4-20260918/staging/`**；
  坐实方式不是猜——生成器 `_rule_enforcement_census.py` **末行硬编码**该输出路径。件未被 TTL 清，已 tmp+冷库双备份（三份 sha256 全等）。
  ⇒ 后续任何引用 `.runtime` 案卷的任务书，**先实测路径再生成**；且 `st-auditdoc-v4` 工棚（WP15.1 拆除靶）拆时**勿连带清 staging**。
- **R-A8｜"词表违规 1 条"实测是 9 处 / 4 族 / 9 文件，且这台词表无牙**。
  非法值 `standard×4 / checklist×2 / report×2 / reference×1`（声明总数 224，合法 215）；
  方案只列了 `defect_pattern_checklist.md`，**漏了 `alignment_checklist.md`**（同值第二处）；
  全仓**没有任何在册门按词表校验文档的 `rule_form`**（`check_frontmatter_metadata.py` 零命中 `rule_form`；
  `validate_rule_frontmatter.py` 只扫 `rules/trae_*.yaml` 扫不到 `sop/**.md`；`frontmatter_schema.json` 无消费者）。
  ⇒ 若 Max 采处方甲只改 1 个文件，**违规数不清零**（M-3）。
- **R-A9｜"一条 census 条目 ≠ 一行 diff"——按 sed 全串替换会伪造历史**。
  9 条陈旧指向实际含 **21 处文本位**：机器列表值 17 处（可机械改）+ 条文散文 3 处 + **历史 changelog 1 处（`trae_036:893` 禁改）**。
  另有 `trae_036:315` 的 `command:` 含盘符绝对路径，改法需裁（M-6）。
- **R-A10｜WP7 已落地（本役波1 第一笔真改动）**：commit `f8c1fc044a`，唯一文件 `reconciliation_registry.py`（+79 −1），
  两轴派生可判分母 **0 → 86**（=H40+M32+L14，0 未知值；门位 owner-required 64 / ai-self-decide 22），
  `action` 仍 `warn`、未加字段、未动 WP12 的 trigger 段——**并发隔离三条全守住**。
  另证一条纪律有效：**CloneGuard 首提交判死两个孪生函数 structural 相似度 100%，车道按手册 §7 合并成单一 `_derive_axis`
  （轴差异降级为 mapping 数据）后落地**——这正是手册那行"只有消除第二个函数体才能消克隆"的第一次实战复用。
  ⚠️ **跨车道接口待接**：D-7 要求"案卷生成器**与**对账门"都读两轴派生；对账门侧已导出公共函数
  `derive_rule_risk` / `derive_two_axis_risk_for_rules`，**案卷侧在 WP8 的 `_tools/dossier_core.py`（WP7 按禁改令未动）**。
  ⇒ 若 WP8 收工时该列仍为 0，波2 补一刀接线（列入 C-11）。
- **R-A11｜幻觉引用第二例，且这次在**代码注释**里**。
  `reconciliation_registry.py:5419` 注释引用 commit `170cba56e0`——`git cat-file -t` 报 `Not a valid object name`，
  `--all` 亦无；★ **同处真实迁移 commit 是 `6933dbcff3`**（本总包起初写成 `feac5f7b28`，经 WP1-取证车道纠正并由我独立复跑证实：`feac5f7b28` 只是该文件的**出生提交**（`git show --stat feac5f7b28` = 单文件 524 insertions），R100 改名件在 `6933dbcff3`（2026-07-02，message 里的『批次4b』与注释逐字对应）。⇒ **这是我本役第 5 处自记错误，也是『引用了他物但指错号』的第二例**）。与我在 §7.10 记的"裁定号 343（该号从未登记）经任务书二级传播"同族，
  **但代码注释面此前未查过** ⇒ 建议把"引用 commit/裁定号/路径前先验存在"从车道纪律升成**门禁**（列 C-10）。

## 2. 波1 车道回执全文（§5 六项格式，逐条嵌入，未做删改）
### WP1 · 两坏写入端（`st-ramp-wp1-20260919`）

# WP1 回执 · 车道 st-ramp-wp1-20260919

**结论先行：按 §6.4 + §6.6 + D-13 停手。两写入端零代码改动、零提交。方案 §7 对第二写入端的 `[亲验]` 断言经现场实测被推翻；另发现一项方案未记的破坏性地雷（见 §2.1c / C-0），建议优先于本 WP 处置。**

冷启动：`python --version` → `Python 3.12.8`（EXIT=0）；`python -m zephyr.trading.process_reaper --status` →
`last_run=2026-09-18 19:10:55`（计划任务存活，写操作前提满足）。未跑 `lock_files.py cleanup`
（主区 111 件他会话 staged、`st-bizmine-20260919` 持热册 claim，避免代动他人登记；本车道全程未 acquire/release 任何锁）。

---

### 1. 改动文件清单 + commit hash

**无。本车道未修改任何 tracked 文件，未产生提交。**

```
$ git status --porcelain -- src/zephyr/infrastructure/rollback/rollback_verifier.py \
    src/zephyr/gov_drift/gate_persistence.py tests/rollback tests/gate
（空输出，EXIT=0）

$ git diff --cached --name-only -- src/zephyr/infrastructure/rollback src/zephyr/gov_drift
（空输出 —— 本车道未 stage 任何文件）

$ git log -1 --name-only
commit 95cea99a47... chore(integrity): post-flush re-register rules_integrity_db ...
（HEAD 非本车道产出；`git log -1 --name-only` 无本人文件 = 归属核实通过，未吸收他人内容，也未被他内容吸收）

$ git diff --cached --name-only | wc -l
111          # 主区他会话 staged 现值（任务书给的 107 是发单时刻，已漂移，按 §0.6 以实测为准）
```

产物全部在 `.runtime/tmp/st-ramp-wp1-20260919/`（未入库，由总包代持）：
`_schema_probe.py`（真库列名实测）、`_redblue_probe.py`（红蓝证探针）、`_prescribed_patch_probe.py`（处方反证）、
`_destructive_probe.py`（破坏性实测）、`RECEIPT.md`（本文件）。

---

### 2. 红证

### 2.1 站点一 `rollback_verifier.py:195` —— 红证成立，但**方案处方不可实现**

注入物：临时库 `wp1_*/real_schema.db`，**gates 表 DDL 逐字从生产库 `data/databases/governance.db`
的 sqlite_master 读出后照抄**（非手写），插 2 行 `passed=0 / passed=1`。
（**未对生产库做任何 DML**——heal_db_consistency 含 `UPDATE`，在生产库上跑会真改数据，故只在 tmp 复现结构。）

```
[P0] 真库 governance.db :: gates DDL
CREATE TABLE "gates" (
    gate_run_id TEXT PRIMARY KEY,
    gate_id TEXT NOT NULL,
    passed INTEGER NOT NULL CHECK(passed IN (0,1)),
    details TEXT NOT NULL DEFAULT '{}',
    artifact_path TEXT, session_id TEXT,
    task_id TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
    created_at TEXT NOT NULL )

[P1] rollback_verifier.heal_db_consistency on REAL gates schema
gates_fixed=0 tasks_fixed=0 healed=False details=[]
swallowed_warnings=2                     ← 2 行 gates 全部被内层 except 吞掉
gate rows after heal: [('gr-1', 0), ('gr-2', 1)]     ← 一字未动
[P1] 直接 gate['result'] 抛 IndexError: No item with that key
[P1] 复跑仍被吞的告警条数=2
[P1] 写入非法 passed 值被真表拦下 IntegrityError: CHECK constraint failed: passed IN (0,1)
     ⇒ 该表不存在可被 heal 的非法 result
探针退出码 PROBE_EXIT=0
```

**红**：门禁面校验在真实结构上 100% 抛 IndexError 并被静默吞（方案 §1.3 该条 `[亲验]` 复现成立）。
**但处方失效**：方案 WP1 要求"按实表列名重写（`passed` 而非 `result`）"——`passed` 受
`CHECK(passed IN (0,1)) NOT NULL` 约束，非法值**物理上无法入库**（上列 IntegrityError 实证）。
把校验改写成 `passed not in (0,1)` 得到的是一台**由构造保证永不为真的门**——正是宪法/纪律点名的
"恒真返回比缺功能更坏"。故**改前的红拿到了（空转+吞异常），改后的红拿不到**（新代码在真表上永不触发），
红→绿闭环不可成立，**验收判据不可二值化**（§6.6；处方反证见 §2.1b）。

撤样：`shutil.rmtree(TMP)`，生产库复核无漂移（见 §3.3）。

### 2.1b 把处方实现一份再实测（证明"改后必红 + 改后必恒绿"）

命令：`python .runtime/tmp/st-ramp-wp1-20260919/_prescribed_patch_probe.py`（PROBE2_EXIT=0）
做法：读 `src/zephyr/infrastructure/rollback/rollback_verifier.py` 原文，按 WP1 处方做三处替换
（`gate["result"]`→`gate["passed"]`、合法集→`{0,1}`、`UPDATE gates SET result='FAIL' WHERE gate_id=?`→
`SET passed=0 WHERE gate_run_id=?`），落到 tmp 副本后用 importlib 真加载执行（**非 mock**），
分别在"测试 fixture 的幻影库"与"生产库 DDL 照抄的真结构库"上跑：

```
prescribed-copy 加载成功；改动三处已断言存在
[a] 处方代码 × 测试 fixture 幻影库: gates_fixed=0 healed=False swallowed=1
[a] ⇒ root:148 与 unit:178 的 `assert gates_fixed == 1` 改后必红（红证）
[b] 处方代码 × 真库 schema: gates_fixed=0 healed=False details=[] swallowed=0
[b] ⇒ 真表上 CHECK(passed IN (0,1)) 使非法值不可入库：处方实现出来的门**永不为真**（恒真/恒绿，非修复）
```

即：**照 WP1 处方改 = 现有 2 个用例转红 + 得到一台构造上永不为真的门**，两条都不满足"改后见绿且能红"。

### 2.1c 意外发现（方案未覆盖，风险高于本 WP 原目标）：同一方法的 tasks 支路在生产库上是**破坏性地雷**

命令：`python .runtime/tmp/st-ramp-wp1-20260919/_destructive_probe.py`（PROBE3_EXIT=0）
生产库仅只读取分布，UPDATE 演示全在 tmp 库。

```
[真库] tasks.status 列定义 = ["status TEXT DEFAULT 'PENDING',"]      ← 无 CHECK 约束，FAILED 可写入
[真库] tasks status 分布 = {'BLOCKED':152,'CANCELLED':214,'COMPLETED':1981,'IN_PROGRESS':76,'READY':78}
[真库] 落在代码 valid_statuses 之外的状态 = {'BLOCKED':152,'READY':78} 合计 230 行会被 UPDATE 成 FAILED
[tmp 演示] healed=True tasks_fixed=2 details=['task t0: status READY -> FAILED', 'task t1: status BLOCKED -> FAILED']
[tmp 演示] 改后 status = [('t0','FAILED'), ('t1','FAILED'), ('t2','COMPLETED')]
```

要害：`heal_db_consistency` 的**默认目标就是 `project_root/data/databases/governance.db`**
（`rollback_verifier.py:165`），而代码里的 `valid_statuses` 五值集**与真源词表不符**——
`sqlite_schema.py:87-91` 的 `_DDL_TASKS` 声明合法态是 **10 值**
（PENDING/IN_PROGRESS/COMPLETED/VERIFIED/FAILED/BLOCKED/WAITING/READY/RETRY/CANCELLED），
方法只认其中 5 值 ⇒ READY/BLOCKED/WAITING/RETRY/VERIFIED 全被判为脏。
更糟：生产 `tasks` 表实际**没有继承该 CHECK**（列定义只剩 `status TEXT DEFAULT 'PENDING'`，
CHECK 缺失的成因见 `sqlite_schema.py:826-836` 记录的 writable_schema hack 历史），
所以这次误改**不会被数据库拦下**。当前唯一保护=**没人调用它**。任何人给 `scripts/rollback.py`
补一个 `heal`/`verify` 子命令、或从仓根 cwd 触发一次，就会把 230 行任务状态静默改成 FAILED。
本车道**未在生产库上执行过该方法**（已核实前后行数与 status 分布未变）。

### 2.2 站点二 `gate_persistence.py:215` —— 普查断言被推翻，"红"根本不存在

注入物：临时 `project_root` 走真实公共 API（非 mock）。

```
[P2] GatePersistence.persist_gate_decision 实测（临时 project_root）
目标库 = C:\Users\fanzi\AppData\Local\Temp\wp1_*/proj\data\drift_audit\drift_events.db
[P2] 写入成功，读回 1 行: [('MOD-A','GATE-1','PASS','redblue probe','2026-09-18T18:31:39.697830+00:00')]
[P2] 结论：普查 'INSERT 列名与实表不符 → 每次调用必失败' 不成立

[P0] drift_audit/drift_events.db :: gate_decisions DDL
CREATE TABLE gate_decisions (id INTEGER PRIMARY KEY AUTOINCREMENT, module_id TEXT,
                             gate TEXT, decision TEXT, detail TEXT, decided_at TEXT)
```

反证（**执行方案处方才会产生的红**）：

```
[P3] 若按普查处方把 INSERT 改成 gate_id/reason/decided_by
[P3] 红：OperationalError: table gate_decisions has no column named gate_id

[P4] governance.db 的 gate_decisions 能否接受现 INSERT 列名
[P4] 红：OperationalError: table gate_decisions has no column named module_id ⇒ 确系两个同名异构表（不同 DB）
```

**定性**：该写入端**目标库根本不是 governance.db**，而是 `data/drift_audit/drift_events.db`；
其自建表列与 INSERT 逐列吻合。普查把"同名异构的两张表（不同 DB 文件）"当成一张，
方案 §1.3/§7 的 `[亲验]` 标记错误——**这正是 §6.4「普查出现与裁定矛盾的证据」= 停手情形**。
若照处方"就地改列名"，唯一后果是**把一条能用的写通路改成必炸**（P3 实证）。

撤样：tmp 目录整体删除；生产 `drift_events.db` 复核 mtime/行数未变（§3.3）。

---

### 3. 验收命令与本次实测输出

### 3.1 真表列名（全部走在册真源，未裸 connect 写）
命令：`python .runtime/tmp/st-ramp-wp1-20260919/_schema_probe.py`（EXIT=0）
governance.db 经 `DatabaseService.get_governance_conn(read_only=True)`（在册唯一真源）；
drift_events.db 经 `zephyr.governance.persistence.sqlite_schema.get_db_connection`（该文件自身使用的连接工厂）。
语句只有 `PRAGMA table_info` / `SELECT COUNT/MIN/MAX`，**零 DML**。

```
gates          : [gate_run_id, gate_id, passed, details, artifact_path, session_id, task_id, created_at]  rows=1791  max created_at=2026-06-29T18:20:27.908171+00:00
gate_runs      : 同列集                                                                                    rows=6445  max created_at=2026-09-15T12:18:49.115825+00:00
gate_decisions : [decision_id, gate_id, decision, reason, decided_at, decided_by]                          rows=35    max decided_at=2026-07-27T14:35:47.593160
drift_events.db.gate_decisions : [id, module_id, gate, decision, detail, decided_at]                       rows=0
drift_events.db.scan_results   : [scan_id, detectors_run, total_drift_events, storm_mode_triggered, committed_at, sha256]  rows=0
```

要点：**`gates`/`gate_runs` 列集完全相同**（migration 34 兼容表，DDL 见 `sqlite_schema.py:952`），
`gates` 无 `result` 列 → 站点一诊断成立。

### 3.2 调用方存在性实测（把方案的 `[推断]` 变成 `[亲验]`）

```
$ git grep -n "heal_db_consistency" -- ':!.worktrees' ':!.aidrafts'
  src/.../rollback_verifier.py:164（定义）
  tests/rollback/test_rollback_verifier_root.py :115 :130 :146 :161
  tests/rollback/test_rollback_verifier_unit.py :148 :162 :176 :191
  docs/03_modules/_domain_infrastructure/algo_flow/rollback/rollback_verifier.yaml:20
⇒ 生产调用方 0 个。scripts/rollback.py 仅 `status` 子命令调 verifier，且只调 `g0_verify()`（:140）；
  rollback_boot_integration.py 仅构造实例（:105），不调 heal。

$ git grep -n "persist_gate_decision\|persist_scan_result" -- src scripts
  仅 src/zephyr/gov_drift/gate_persistence.py:210 定义；src/scripts 命中 0（persist_scan_result 亦 0）
$ git grep -n "GatePersistence" -- src
  gov_drift/_infrastructure.py:85,143（re-export）; gov_drift/__init__.py:153,459（re-export）;
  compliance/behavioral_auditor/__init__.py:250,424（re-export）⇒ 无实例化点
$ grep -rln --include=*.py --exclude-dir={.runtime,.worktrees,.aidrafts,.git} -e heal_db_consistency \
      -e persist_gate_decision -e "GatePersistence(" .
  仅 2 个定义文件 + 3 个测试文件 ⇒ 未跟踪文件里也无生产调用方
$ git grep -n "gate_decisions" -- src scripts
  写：仅 gate_persistence.py:215（写 drift_events.db）
  governance.db 的 gate_decisions 列名只出现在 sqlite_schema.py:850（DDL）与 tests/governance/shared/test_governance_db.py:389
  ⇒ **governance.db.gate_decisions 在当前树里根本没有写方**
$ git grep -n "gate_persistence|rollback_verifier" -- gate_registry.yaml in_process_gate_registry.yaml
  空 ⇒ 两模块均无门禁注册；cross_module_dependency_registry.yaml 仅 DEP-025d 一条声明性描述（转报，非调用点）
```

**判定：两写入端皆无活调用方（tests-only）。**

### 3.3 撤样后现状复核

```
$ ls -la data/drift_audit/drift_events.db      → 20480  Aug 21 11:20（探针未触，临时 project_root）
$ sqlite3(readonly) gate_decisions rows = 0 ；scan_results rows = 0
$ sqlite3(readonly) governance.db：gates=1791 / gate_runs=6445 / gate_decisions=35 / tasks=2501
  gates max created_at=2026-06-29T18:20:27.908171+00:00 ；gate_decisions max decided_at=2026-07-27T14:35:47.593160
  （与探针运行前逐项一致 ⇒ 生产库零漂移）
```

### 3.4 测试基线（现状绿，且这绿是幻影 schema 共谋出来的）

```
$ python -m pytest tests/rollback/test_rollback_verifier_unit.py \
    tests/rollback/test_rollback_verifier_root.py tests/gate/test_gate_persistence.py \
    -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning" \
    --basetemp=.runtime/tmp/st-ramp-wp1-20260919/bt
collected 52 items … 52 passed in 2.26s      PYTEST_EXIT=0

$ python -m pytest "tests/rollback/test_rollback_verifier_root.py::TestHealDbConsistency::test_db_with_invalid_gate_result" \
    "tests/rollback/test_rollback_verifier_unit.py::TestHealDBConsistency::test_fixes_invalid_gate_result" \
    -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning" \
    --basetemp=.runtime/tmp/st-ramp-wp1-20260919/bt2
collected 2 items … 2 passed in 0.41s        EXIT=0
```

关键：`tests/rollback/test_rollback_verifier_root.py:124 / :140 / :155` 与
`tests/rollback/test_rollback_verifier_unit.py:56`（共享 helper `_create_test_db`）
**自建 `CREATE TABLE gates (gate_id TEXT PRIMARY KEY, result TEXT)`**（生产库不存在的结构），
再断言 `gates_fixed == 1`（root:148、unit:178）。⇒ 测试与代码共谋一套幻影 schema，站点一的空转在 CI 里
永远看不见；§2.1b 已实测：把代码对齐实表后，这 2 个用例当场转红。
（改测试 fixture = 动"测试是真源"的裁定域，`sqlite_schema.py:949` 明写"SSoT 铁律：测试是真源"，
与本发现正面冲突 → 须 Max 裁。）

---

### 4. 命中的门位项与待裁清单

命中停手条款：
- **§6.4** 普查出现与裁定矛盾的证据（站点二 `[亲验]` 被现场推翻）。
- **§6.6** 验收判据无法二值化（站点一改写后为 CHECK 恒成立的永不为真门）。
- **D-13** 站点一"改 passed 校验"的目标语义、站点二 `decided_by` 取值来源，均无唯一现场来源，需语义判断。
- 门位：WP1 属 high 档（门禁/治理自身），但按 §2 未做四类动作，本可施工；**停手原因不是门位，是事实与处方不成立**。

待裁清单（交 Max）：
| # | 待裁事项 | 处方 A（修） | 处方 B（退役） |
|---|---|---|---|
| **C-0** | **`heal_db_consistency` 的 tasks 支路 = 破坏性地雷**（默认写生产 governance.db；词表只认 10 值中的 5 值；生产表缺 CHECK 故拦不住；实测 READY/BLOCKED 会被改成 FAILED，涉及 230 行现值）——**方案 §1.3/§7 完全未记此项，风险高于本 WP 原目标** | 让词表从 `_DDL_TASKS` 单一真源派生（读 CHECK 值集，不硬编码），并在写前加 dry-run + 行数上限护栏 | 整方法退役（与 C-1 一并处置）。**任一处方都涉及语义判断 → 未自裁** |
| C-1 | `RollbackVerifier.heal_db_consistency` 的 gates 支路（0 生产调用方 + 恒真不可实现） | 把目标改到 `gate_runs`/`gates` 的**真实可非法面**（`details` JSON 可解析性、`passed` 与 `gate_id` 完整性链），同步重写 fixture（root:124/140/155、unit:56 的 `gates(gate_id,result)`）与 2 处 `gates_fixed == 1` 断言（root:148、unit:178，§2.1b 实测改后当场转红），并把内层 except 改登记（`fail_open_register` 口径需先跑生成器，禁手改册） | 删除 gates 支路（其 tasks 支路见 C-0）：涉及删代码/改公共 API → §6.1 停手 |
| C-2 | `gate_persistence.persist_gate_decision` 写的是 **shadow DB** 的 **同名异构表**（真表 0 行、无人调用） | 目标库改指 governance.db 并按 `sqlite_schema.py:850` 列名写（`gate_id/decision/reason/decided_at/decided_by`）——**必须先定 `decided_by` 取值来源**（会话 sid？固定字面量？）= 需推断，D-13 不许自填 | 认定该持久化面为历史空壳（drift_events.db 早被 #62 裁定"空壳 schema B 已废止"，同表是否属同类须 Max 按 #62 原文判） |
| C-3 | 站点一普查断言为真但**方案 §1.3 "每次调用必失败"与 §7 `[亲验]` 分级需更正**（防 WP2/WP3 沿用错误列名口径） | 修 `2026-09-18-gate-identity-root-fix-plan.md` §1.3/§7 文本（文档改由总包代持） | — |
| C-4 | D-3 第②③步（声明表退役 / 清行）依赖本回执新事实：`gates`(1791 行, 止 06-29) 是 `gate_runs`(6445 行, 止 09-15) 的**同构兼容表**；`governance.db.gate_decisions` 35 行**树内无写方**；`drift_events.db.gate_decisions` 0 行 | — | 本 WP 未做任何 DB 删除（按任务书第 5 条），仅递交"死表/活表"判据 |

---

### 5. 证据等级（逐项）

- `[亲验]` 站点一：`gates` 真列名无 `result`、`gate["result"]` 抛 IndexError、内层 except 吞 2 条、`gates_fixed=0`、`passed` 受 CHECK 约束故非法值不可入库。
- `[亲验]` 站点一（处方反证）：处方代码副本在幻影 fixture 库上 `gates_fixed=0`（⇒ root:148 / unit:178 由绿转红）、在真结构库上 `gates_fixed=0 且 swallowed=0`（⇒ 改后为构造性恒绿，非修复）。
- `[亲验]` 站点二：`persist_gate_decision` 在真实目标库 `drift_events.db` 上**写入成功并读回 1 行**；该表真列名与 INSERT 逐列吻合；按普查处方改写必 `OperationalError`；两库同名表互不兼容（P3/P4 双向实证）。
- `[亲验]` 调用方：两写入端 src/scripts 生产调用方 0，仅 re-export + tests（git grep 全仓 + 未跟踪 fs grep 双尺，排除 .worktrees/.aidrafts）。
- `[亲验]` 现状：52 个相关测试全绿；绿是幻影 schema 共谋（fixture 自建 `gates(gate_id, result)`）。
- `[亲验]` 未污染生产：governance.db 四表行数与 max 时间戳探针前后逐项相等；drift_events.db mtime/行数未变。
- `[转报]` 主区 111 件他会话 staged、热册由 `st-bizmine-20260919` 持有 claim：未复跑他人 claim 登记，仅按 `git diff --cached --name-only | wc -l` 实测件数与任务书 107 的差异登记。
- `[推断]` `governance.db.gate_decisions` 的 35 行历史写方已消失（只查了当前树的符号命中，未做全历史 `git log -S` 归因）；`tests/governance/shared/test_governance_db.py:389` 是唯一按真列名写的地方，属测试专用。
- `[推断]` `cross_module_dependency_registry.yaml:DEP-025d` 声称"gate_persistence 漂移预算门禁"为硬运行时依赖，与"src 内零调用点"不符——未判谁真谁假。

---

### 6. 未做完的部分与原因

1. **未改代码**（两站点）：非"没做"，是**做了前置实测后判定处方不成立**——站点二前提为假，站点一改后必恒真。按 D-13/§6.4/§6.6 停手，处方与证据在 §2、§4 交回 Max。
2. **未做 D-3 第②③步**（声明表退役、清行）：任务书明令禁止本 WP 执行，亦未做任何 DB 删除。
3. **未提交**：无任何 tracked 改动，按纪律禁空提交（"If there are no changes to commit, do not create an empty commit"），故未走 `git_commit.py`；因此 §1 的 commit hash 记为 N/A，`git log -1 --name-only` 只用于证明 HEAD 非本车道产出。
4. **未跑真库端到端写读**（站点一在 `governance.db` 实物上、站点二在生产 `drift_events.db` 实物上）：`heal_db_consistency` 含 `UPDATE gates/tasks`，在生产库上执行会真改数据（185MB、2501 tasks），违反 RULE-DATA-OPS 三步验证；已用"生产库 DDL 逐字照抄到 tmp"替代，等价性=结构真、数据假，**此项标 `[推断]` 不冒充 `[亲验]`**。
5. **未登记 fail_open_register / capability / creation_token**：无新文件、无行为变更落地，登记前提不存在。

### WP12 · 登记册生成器 trigger 扩前缀（`st-ramp-wp12-20260919`）

# WP12 回执 · 会话 st-ramp-wp12-20260919（裁定 D-12 / 登记册生成器 trigger 扩前缀）

日期：2026-09-19 · 环境：Python 3.12.8 [亲验] · 分支 dev · 主区 cwd `D:/ZephyrAlpha`

### 0. 一句话结论

**主改停在案卷，未落地**：`GATE-RULE-CATALOG` 的 trigger 前缀扩写在现行架构下是**对外零效应的空改动**，
且方案给定的验收观测面（`reconcile_execution_log` 出现 `GATE-RULE-CATALOG` 新行）**在本仓从未存在过**
（全库 77511 行中 0 行）。按 §6.4（出现与裁定矛盾的证据）+ §6.5/§6.6（验收判据无法二值化）停手回流。
**附带项已完成并证实**（生成器两次跑幂等、滞后已消除），但滞后是由 reconciler 自己落的（HEAD `6fe0804830`），
故本车道 **零提交、零 tracked 改动**。处方补丁 = `.runtime/tmp/st-ramp-wp12-20260919/wp12.patch`（`git apply --check` PASS）。

---

### ① 改动清单 + hash

**本车道未产生任何 commit**（无 tracked 改动可归属）。三项交付物全在非 tracked 介质：

| 件 | 路径 | 状态 |
|---|---|---|
| 主改补丁（未应用） | `D:\ZephyrAlpha\.runtime\tmp\st-ramp-wp12-20260919\wp12.patch` | `git apply --check --ignore-whitespace` = PASS |
| 冷备副本（防 TTL） | `G:\zephyr_cold\wp12_lane\`（补丁+两份探针脚本+本回执） | 已复制 |
| 只读探针 | 同目录 `probe_trigger.py` / `ab_measure.py` / `qlog.py` | 只读，不落 tracked |

补丁正文（一行，锚点全仓唯一命中，脚本 assert 过）：

```diff
--- a/src/zephyr/governance/audit/reconciliation_registry.py
+++ b/src/zephyr/governance/audit/reconciliation_registry.py
@@ -6106,7 +6106,7 @@ def make_rule_audit_reconciler(gateway: object) -> ReconcilerSpec:
-    _RULES_PREFIX = "docs/01_policies_and_standards/rules/"
+    _RULES_PREFIX = "docs/01_policies_and_standards/"
```

`git log -1 --name-only` 原文（HEAD 现属他车道，非本车道；列此以证本车道未吸收他人内容）：

```
95cea99a47 | lane | Sat Sep 19 02:33:15 2026 +0800 | chore(integrity): post-flush re-register rules_integrity_db (capture final HEAD, 时序竞态治本 2026-08-02)

scripts/governance/meta/rules_integrity_db.json
```

开工定位（不照方案行号盲改，实测 `git grep`）：

```
$ git grep -n '01_policies_and_standards/rules/' -- src/zephyr/governance/audit/reconciliation_registry.py
:3856   ← GATE-YAML-SYNC 的 trigger（另一台门，非本包对象，未动）
:6029   ← _RULES_PREFIX 常量（GATE-RULE-CATALOG 唯一使用点）
:7398   ← trae_071 文档串引用（非判定）
$ git grep -n '_RULES_PREFIX' -- …
:6029 定义；:6040 唯一消费点（_trigger_catalog 内）
```
方案说"约 :6029 与 :6036-6043"，开工实测吻合；施工中途工作区被 WP7 在途改动插入约 80 行（:460+ 新增块 + :119 改一行），
补丁 hunk 落点因此显示为 :6106（该工作区副本里常量在 :6109）。

---

### ② 红证（照方案原法做不到，附证伪证据；未做处如实标注，不用 mock 冒充）

### 2.1 阴性/阳性对照在本仓不可执行——两条独立理由，各自实测

**理由 A：观测面对象不存在（`gate_id='GATE-RULE-CATALOG'` 全库 0 行）**

```
$ python .runtime/tmp/st-ramp-wp12-20260919/qlog.py GATE-RULE-CATALOG 5
db_total_rows=77473 gate=GATE-RULE-CATALOG gate_rows=0 shown=0
（施工末复测）db_total_rows=77511 gate=GATE-RULE-CATALOG gate_rows=0
$ python -c "… SELECT action, COUNT(*) FROM reconcile_execution_log WHERE gate_id='GATE-RULE-AUDIT' GROUP BY action"
('auto_committed', 1355) ('critical_warn', 53) ('warn', 462)
```

机理（读码 [亲验]）：`spec_catalog(gate_id="GATE-RULE-CATALOG")` 在 `make_rule_audit_reconciler` 末尾
被 `_compose_reconcilers("GATE-RULE-AUDIT", spec_catalog, spec_rule_file_audit, spec_arch_refs)` 合成
（开工 HEAD 面 :6347，施工末工作区现号 :6429，行号随并发提交漂移），
`reconcile_for` 只在**父 spec** 上落归属（:799-800 `result.gate_id = spec.gate_id`），
`_log_reconcile_results` 记的永远是 `GATE-RULE-AUDIT`；子判定只以 `[<action>] <detail>` 混进 detail 串。
全仓 `register()` 清单（`git_commit_gateway.py:1368-1470`）中无 GATE-RULE-CATALOG 独立注册项。

**理由 B：改了前缀也不换行为（集合包含 + 真历史 A/B 实测）**

- `_trigger_catalog` 只放行扩展名 `(".yaml", ".yml", ".md")`（开工 HEAD 面 :6040）；
  同复合体里的 `_trigger_arch_refs` 放行 `REFERENCE_TEXT_EXTS = (".py", ".yaml", ".yml", ".md", ".json", ".txt")`
  （`src/zephyr/gov_enforcement/commit_gates/_reference_helpers.py:64`）。
  ⇒ `catalog_old ⊆ catalog_new ⊆ arch_refs ⊆ parent(OR)` ⇒ **父 trigger 恒等**（扩前缀不可能新增任何触发）。
- 且 `_compose_reconcilers._reconcile`（:5127）`results = [r(committed_files, session_id) for r in reconciles]`
  **无条件串跑全部子 body**，`reconcile_for` 的子 trigger 门控在合成后已消失（:707 `if not spec.trigger(...)` 只看父）。

真 790 笔提交（`git log -800 --name-only`）逐笔跑真常量（`_RULE_FILE_PATHS` / `REFERENCE_TEXT_EXTS` / `_rel_path`）：

```
$ python .runtime/tmp/st-ramp-wp12-20260919/ab_measure.py
commits_analyzed=790
parent_trigger_true_OLD=786  parent_trigger_true_NEW=786
子判定 _trigger_catalog 取值改变的提交数 = 248
父门 GATE-RULE-AUDIT trigger 取值改变的提交数 = 0   <-- 改动对外零效应
样例 (sha, 命中新前缀的文件, catalog_old, catalog_new, parent_old, parent_new):
   ('6fe0804830', 'docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml', False, True, True, True)
   ('6fa8fd2cc7', 'docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml', False, True, True, True)
   …
```

生产谓词本体（与 `git_commit_gateway.py:1396` 同一构造表达式，真 `GitCommitGateway`，非 mock）：

```
$ python .runtime/tmp/st-ramp-wp12-20260919/probe_trigger.py
spec.gate_id = GATE-RULE-AUDIT
trigger(docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md) = True   ← 改前即 True
trigger(docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml)         = True
trigger(docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml)               = True
trigger(src/zephyr/shared/io/file_utils.py)                                                   = True
```

### 2.2 "注入一个 sop 文档提交"这一步：本车道未做，原因如实记

方案原法要求改前/改后各做一次注入提交、比 DB 新行。未做，两条实因：
1. 由 2.1 已证 **不存在任何可区分的输入**（父 trigger 恒等），注入两笔提交得到两笔同样的行，
   既不能出红也不能出绿，只会在拥堵通道上多压两笔含他人 staged 面的提交；
2. **§6.6 文件撞车已实发**：施工中途 `reconciliation_registry.py` 出现 WP7 车道的在途未提交改动
   （`git diff HEAD --numstat` = `83 1`，hunk 在 :119 与 :460+，与本包 :6106 不重叠但同文件同批），
   按任务书硬约束"发现不是自己改的 hunk → 不合并提交别人内容 → 出 patch + 停手"执行。

⇒ 本包红证状态：**未证（判据不可执行）**，不写"通过"。若 Max 重定观测面（见 ④ 待裁 2），
注入对照可在 1 个提交内补做。

---

### ③ 验收命令与本次实测输出（数字全是本次跑的）

### 3.1 附带项：重跑 `generate_rule_catalog.py` 消除滞后 + 幂等实测（两次跑）

```
$ C=docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml
$ echo "HEAD_hash=$(git rev-parse HEAD:$C)"; stat -c 'pre_mtime=%y size=%s' $C
HEAD_hash=0388f4e263a920f6370302cb7b30b2a73a50d81a
pre_mtime=2026-09-19 02:31:11.886441500 +0800 size=104358

$ python scripts/governance/d3_metadata/generate_rule_catalog.py ; echo "rc1=$?"
Scanning: D:\ZephyrAlpha\docs\01_policies_and_standards
Found 261 files with frontmatter
Catalog unchanged (261 entries), skip rewrite (idempotent)
rc1=0
post_run1_hash=0388f4e263a920f6370302cb7b30b2a73a50d81a

$ python scripts/governance/d3_metadata/generate_rule_catalog.py ; echo "rc2=$?"
Catalog unchanged (261 entries), skip rewrite (idempotent)
rc2=0
post_run2_hash=0388f4e263a920f6370302cb7b30b2a73a50d81a   ← 与 run1、pre 三点同值
mtime=2026-09-19 02:31:11.886441500 +0800 size=104358        ← 两次跑 hash 与 mtime 全不动
```

幂等性加证（冷写两笔 + 与入库件逐字比，只比 `generated_at` 之外）：

```
$ python …generate_rule_catalog.py --output $T/cat_scratch1.yaml   # 全新写，无旧时间戳
Generated catalog with 261 entries -> …/cat_scratch1.yaml
$ python …generate_rule_catalog.py --output $T/cat_scratch2.yaml
Generated catalog with 261 entries -> …/cat_scratch2.yaml
$ diff <(sed 's/^generated_at:.*/generated_at: X/' cat_scratch1.yaml) <(… cat_scratch2.yaml) → 空
SCRATCH1==SCRATCH2 (除 generated_at 外逐字节相同)
$ diff <(sed …cat_scratch1.yaml) <(sed …rule_catalog_registry.yaml) → 空
SCRATCH==TRACKED (HEAD 内容 = 生成器定点)
```

滞后消除核对（本车道开工时 worktree 比 HEAD 新，施工中被 reconciler 自己入库）：

```
（开工时）git diff HEAD --numstat --ignore-cr-at-eol -- $C  →  50 5      ← 258→261 条、3 处字段刷新
（现  在）git diff HEAD --numstat --ignore-cr-at-eol -- $C  →  空（identical）
$ git log --oneline -3 -- $C
6fe0804830 chore(reconciler): batched auto-commit (3 reconcilers) by GitCommitGateway post-commit
```
补进去的条目含 `…/sop/review_sop/rule_disposition_policy.md`、`…/_registry/catalogs/domain_responsibility_layer_mapping.yaml`、
`…/_registry/catalogs/fail_open_register.yaml`，字段刷新含 `audit_prompts_20_ai.md` 的 title、数据源 SOP 的 version 1.0.0→1.1.0。
（方案说"2 条未登记 + 3 条字段陈旧"，本次实测为"3 条新增 + 2 条字段刷新"，计数以命令为准。）

**这条 auto-commit 本身就是 D-12 病因证伪的最新样本**：触发它的那笔提交 `2cab47d016` 只改了一个文件
`docs/_working/fullflow_campaign/delivery/FINAL_DELIVERY_REPORT.md`（既不在 `rules/`，也不在 `01_policies_and_standards/`），
对应库行：

```
('2026-09-18 18:33:17.922492+00:00', 'GATE-RULE-AUDIT', 'st-fullflow-20260918', 'auto_committed',
 '[auto_committed] rule_catalog_registry drift detected and auto-reconciled | …')
```

### 3.2 DB 读数走 DatabaseService（未用裸 duckdb/裸 connect）

`.runtime/tmp/st-ramp-wp12-20260919/qlog.py` 用 `zephyr.infrastructure.database_service.get_db_service().get_governance_conn(read_only=True)`。

---

### ④ 命中的门位项与待裁清单

**本车道未触发任何门位**（零提交、零 tracked 改动，未过 GitCommitGateway）。注册会话 `st-ramp-wp12-20260919`（pid=0），
未 claim 任何文件，`.ailocks/registry.json` 内 9 把锁无一落在我两个目标件上（施工前后各查一次）。
禁碰件 `capability_canonical_file_registry.yaml` **未作任何修改、未 stage、未入清单**（它只在我一次全仓
`git grep 'GATE-RULE-CATALOG'` 的只读检索输出里被打印过两行）。

待裁（回流 Max）：

1. **D-12 处方是否作废**：扩前缀无可观测效果。真问题若判为"catalog 重生应当只对扫描目录内变更触发"，
   则处方是反向的——现在它**对任何一笔提交都无条件重生**（含只改 `docs/_working` 的提交），
   12min 级周期刷写靠生成器的 idempotent-skip 兜住（`generate_rule_catalog.py` L285-311 注释自述该兜法）。
   候选处方（择一，需 Max 定，均涉门禁判定逻辑=§6.3）：
   (a) 把 `spec_catalog` 从 `_compose_reconcilers` 摘出独立注册；
   (b) 改 `_compose_reconcilers` 让子 body 受子 trigger 门控（影响**全部**复合 reconciler，风险面大）；
   (c) 维持现状、只把方案 §1 D-12 的"影响"句改成事实描述（文档面，零代码）。
2. **红证观测面重定**：`reconcile_execution_log.gate_id` 由 composition 抹平为父名，
   凡以"子门 gate_id 出行"写验收的卡都不可判（本卡即其一）。受影响 reconciler 家数本次未穷举 → 需 WP2/WP4 面统一裁。
3. **附带发现（只报不改）**：`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`
   中 `GATE-RULE-CATALOG` / `GATE-RULE-AUDIT` **零条目**（`grep -ci 'rule.audit\|rule.catalog'` = 0），
   而代码侧确有两台判定 → 属 WP4（规则↔门禁对账门）/WP1（身份台账）面，不在本包权限内。
4. **§6.6 两 WP 改同一处（实发）**：`reconciliation_registry.py` 工作区含 WP7 在途 `83 1` 未提交改动；
   本车道以 patch 交付，未合并提交他人内容。两包改动行不重叠（WP7 :119/:460+，本包 :6106），
   若 Max 仍要 D-12 原样落地，建议 `git apply wp12.patch` 并入 WP7 那一批（同文件族一次过）。

---

### ⑤ 证据等级（逐项）

| 结论 | 等级 |
|---|---|
| `gate_id='GATE-RULE-CATALOG'` 全库 0 行（77473 / 77511 两次读数） | [亲验] 本次 SQL |
| `_RULES_PREFIX` 唯一消费点是 `_trigger_catalog`（:6029/:6040） | [亲验] git grep |
| `spec_catalog` 被合成进 `GATE-RULE-AUDIT`、DB 永不记子名 | [亲验] 读码 + 探针 `spec.gate_id=GATE-RULE-AUDIT` + 真历史行 detail 串 |
| 扩前缀后父 trigger 取值零变化（248 子判定变 / 0 父判定变 / 790 笔真提交） | [亲验] 生产常量 + 真历史文件清单 |
| sop-only 提交早已触发 catalog 重生并 auto-commit（37abea57d3 → 17:54:52Z 行） | [亲验] 库行 + `git show --name-only` 配对 |
| 生成器两次跑幂等（hash/mtime 不动）+ 冷写逐字同 + HEAD=生成器定点 | [亲验] 本次命令输出 |
| 滞后由 `6fe0804830`（reconciler auto-commit）自行入库 | [亲验] git log + 库行 |
| "改前不触发"前提为假 | [亲验]（上述四组一致） |
| 无外部输入能区分改前改后 | [亲验] 集合包含 + 790 笔实测；**未做注入提交** = 该项缺一手样本，标 [推断]（依赖 2.1 两条实测，非猜测） |
| 方案"2 条未登记 + 3 条字段陈旧"计数 | [转报]（本次实测为 3 新增 + 2 刷新，以命令为准） |
| gate_registry 无这两台门的条目 | [亲验] grep（原因未查 = [推断]） |

---

### ⑥ 未完成部分与原因

1. **主改（扩前缀）未落地** —— §6.4 + §6.5/§6.6：裁定依据句被实测证伪、验收判据不可二值化；处方补丁已备好待裁（④.1/④.2）。
2. **注入式红证未做** —— 无可区分输入（②2.1），且目标文件被 WP7 在途改动占据，注入提交会吸收他人 83 行未落地内容；已按任务书改出 patch。
3. **附带项无提交动作** —— 重跑确认滞后已为零（HEAD == 生成器定点），`git diff HEAD --numstat -- <catalog>` 为空，无内容可提交；未新建 tracked 文件（遵"总包代持入库"）。
4. **`rule_ai_perception_index.yaml` 未动** —— 不在本包范围（其生成器由 `_reconcile_catalog` 另一支串联，本次 worktree vs HEAD 无漂移）。
5. **本回执由总包代持入库**，本车道未在 tracked 区新建任何文件。


## 3. 待裁清单（交 Max，全案卷已在 §2）

| # | 事项 | 处方甲 | 处方乙 | 总包意见 |
|---|---|---|---|---|
| **C-0** | `heal_db_consistency` tasks 支路 = 230 行破坏性地雷（R-A2） | status 合法值从 `_DDL_TASKS` 单一真源派生 + 写前 dry-run/行数上限护栏 | 整方法退役（与 C-1 并案） | **甲**（退役会连带 C-1，且该方法仍可能被治理面需要） |
| **C-1** | 站点一 gates 支路：0 生产调用方 + 处方恒真化（R-A4） | 把校验目标改到真实可非法面（`details` JSON 可解析性、`passed`×`gate_id` 完整性链）+ 同步重写幻影 fixture 与 2 处断言 + except 走 `fail_open_register` 生成器口径 | 删 gates 支路（涉删代码=§6.1 停手） | 甲，但**必须先定"测试是真源 vs 实表是真源"谁让步** |
| **C-2** | 站点二：写的是 shadow DB 的同名异构表、真表 0 行、无人调用（R-A1） | 目标库改指 `governance.db` 并按 `sqlite_schema.py:850` 列名写——**`decided_by` 取值来源未定 ⇒ D-13 不许自填** **→ Max 已判（改法作废）**：INSERT 不改（自有库列匹配）；真问题=零调用者，salvage 取证在飞 `st-ramp-wp1c`，结论交 Max。 | 认定历史空壳（`drift_events.db` 已被 #62 裁"空壳 schema 废止"，同表是否同类须按 #62 原文判） | 乙的可能性更大（0 行 + 0 调用方），但要 Max 按 #62 原文判 |
| **C-3** | 方案 §1.3/§7 两处事实需更正（防后续车道沿用错口径） | 由 Max 在方案原文改注 | 本册 §4 已代持事实修正 | 乙已做，甲待 Max 顺手 |
| **C-4** | D-3 第②③步（表退役/清行）依赖新事实 | `gates`(1791 行，止 2026-06-29) 是 `gate_runs`(6445 行，止 2026-09-15) 的**同构兼容表**；`governance.db.gate_decisions` 35 行**树内无写方**；`drift_events.db.gate_decisions` 0 行 | — | 判死表前须补 `git log -S` 全历史归因（车道此项标 `[推断]`） **→ 03:1x 更新**：D-17 已判此条口径部分修正（活库无 CHECK 与源码 DDL 有 CHECK 同时成立），雷仍真；另开 **WP16** 治漂移根因。`st-ramp-wp16` 在飞。 |
| **C-5** | D-12 处方是否作废（R-A3） | (a) 把 `spec_catalog` 从 `_compose_reconcilers` 摘出独立注册 | (b) 改合成器让子 body 受子 trigger 门控（**影响全部复合 reconciler，风险面大**） | 先 (c)：只把 §1 D-12 的"影响"句改成事实描述（零代码），(a)/(b) 待 WP4 上线时一并判 |
| **C-6** | 波2/波3 验收观测面需统一重定（R-A3 连带） | 判"父 gate_id + detail 串 + 生成物 hash" | 给复合体补子归因（改落库面，涉门禁行为=§6.3） | 甲（乙属门禁语义变更，风险大于收益） |
| **C-7** | 9 条陈旧指向的落地通道（R-A6，方案 §6.2⊥WP15.4） | 登记 1 个 `ARCH-*` issue 供 9 条共用，一条一提交（净改动 17 行列表值） | 判 Max 直改 / 或拆口径（列表值豁免、散文与 changelog 保留人工） | 倾向"拆口径 + 一条一提交"；A 类 17 行已备可盲执行替换文本 **→ Max 已裁 D-14**：`rules/` 全域冻结至 WP9，只出案卷+可粘贴替换文本，**不落地**（判决对象不得漂移）。 |
| **C-8** | WP15.2 词表违规（M-2/M-3/M-4） | 处方甲：改 `procedural`（词表定义原文含"检查清单"，语义等价） | 处方乙：走词表新增流程（必触发 GATE-VOCAB，**放开面 35 份 `doc_type: policy` 文档**） | 甲，但**必须连带 `alignment_checklist.md`** 否则不清零；version/date bump 属 D-13 禁自定 |
| **C-9** | 两条 `archived`（TRAE-032/TRAE-055）归 B 搬家还是 D3 退役（M-5） | — | — | 需先补"谁替代 `assign_module_id`/`audit_domain_nodes`"的 salvage（车道标 `[推断]`，未穷尽） |
| **C-10** | `reconciliation_registry.py:5419` 引不存在的 commit（R-A11） | 逐件修正引用 | **升成门禁**：引用 commit/裁定号/路径前先验存在（本役已三次：#343 / 本条 / 方案 §7 自陈需复跑） | 乙（本役反复出现的缺陷类，纪律拦不住） |
| **C-11** | D-7 的案卷生成器侧未接线（R-A10） | WP8 若在跑就导入 `derive_rule_risk` | 波2 单开一刀接线（改 `_tools/dossier_core.py` 的 `risk_tier_for` 判据） | 先等 WP8 回执，未接则走乙 |
| **C-12** | `rule_form` 取值三处独立承载（M-7：词表 + `doc_type_vocabulary` + 派生 `frontmatter_schema.json`）+ `trae_043:427` 与词表自相矛盾（M-8） | — | — | 属 WP8 收窄后闸3 的 D1 合并特征，归 Max 案卷面一并判 |
| **C-13 ✅已由 Max 裁（D-9 修订）** | 两份宪法正文已分叉（R-A12）：谁是真源、另一份改指针还是删；** RULE-WORKTREE 该以哪份为准** | — | — | 施工侧临时措施：后续任务书引用宪法条款一律**写明份别**；本役我自己引的是 AGENTS 版 |
| **C-14** | `adversarial_validation` 护栏假绿（R-A13）+ `:213` 用 `datetime.now(UTC)` 与 RULE-SCHEMA-TZ 口径待核 | 补 `description` 传参 + 宽 except 改登记（`fail_open_register` 生成器口径） | 顺带把"兜底记账混入分子"的同类面（WP2/D-2 的 gate_id 归因）一起治 | 甲先做（否则 D-8 的 A/B 批没有可用护栏）；另建议 WP14/WP13 的验收脚本一律带"**自证能红**"注入 |
| **C-15** | A/B 双盲是否现在跑（波5）+ **B 组砍法未选**（128/134/89 行三案，影响面已实测）+ 卷子 §3–§9（72 行、占全文 51%）**零题面覆盖** | — | — | 若瘦身目标是"砍后半段"，**现有卷必报"零损失"**——先补题再跑批，否则测出的是噪声 |

| **C-16** | 队列 `--enqueue` 落地后主区 index 仍压改前 blob（R-A23，两次独立复现） | serializer 落地后对受影响路径刷新主区 index | 落地回执强制输出三态 sha，不一致由网关拦 | 两者都要；短期靠 D-15③ 施工侧自核，但这是**纪律补不是机制补** |
| **C-17** | `data/rule_optimization/key_facts.yaml`：`must_not_appear_as.pattern` 与推荐写法自相矛盾（F-2）+ 三条 `must_appear_in` 永假（F-3）+ 唯一消费者在 `_archive` | 逐条重判该册存活性：活→修 pattern 与 must_appear_in；死→按 D3/D4 退役 | — | 先判存活再修，**别在僵尸台账上做精细修正**（浪费且可能永不被消费） |
| **C-18** | 断链类判据不可二值化：模板占位符与存量断链使 `--ci` 恒红（F-4）；处方验收命令 `:!`×2 并用在本机 fatal（exit 128，须改 `:(exclude)`） | 观测面改"特定串断链条数"+排除式收窄到具体行/锚（F-5 那条活链接要能露出来） | — | 甲；同时把 F-5/F-6 四处同类文本位并进来一次性判 |
## 4. 事实修正表（后续车道任务书必带对应行）

| 方案原文 | 现场实测（2026-09-19，本战役复跑） | 影响 |
|---|---|---|
| "`gate_persistence.py:215` INSERT 列名与实表不符，每次调用必失败"（§1.3/§7 `[亲验]`） | **假**：目标库是 `drift_events.db`，列逐列吻合，实测写入+读回成功 | WP1 处方作废（C-2） |
| "`gates` 表读不存在的 `result` 列且异常被吞"（§7 `[亲验]`） | **真**：真列集无 `result`，实测抛 `IndexError` 且 2 行全被吞 | 但处方不可实现（C-1） |
| D-12 "现前缀导致改 `sop/`、`_registry/` 下文档**永不触发**重生" | **假**：父 trigger 恒等且早已触发；sop-only 提交 `37abea57d3` 已促成 auto-commit | WP12 主改作废（C-5） |
| WP12/WP2/WP3/WP4 的验收面 `reconcile_execution_log` 出现**子门** gate_id | **该面不存在**：库 77512 行里 `GATE-RULE-CATALOG` 0 行（复合体只落父名） | 波2/波3 判据换（C-6） |
| WP1 行号 :191 / :215 | 现漂至 :195 / :215（WP7 又在同文件插入约 80 行） | 一律 `git grep` 自定位 |
| 方案"2 条未登记 + 3 条字段陈旧" catalog 滞后 | 实测 3 条新增 + 2 条字段刷新，且已由 reconciler auto-commit `6fe0804830` 自行入库 | 计数以命令为准 |
| `tasks.status` 受词表约束 | **生产表该列无 CHECK**（9 处 CHECK 均在别的列） | C-0 能被静默改 |
| 任务书/方案给 `…/st-ruledisp-20260918/staging/rules_enforcement_census.json` | **不存在**；真身 `…/st-auditdoc-v4-20260918/staging/`（生成器末行硬编码坐实） | R-A7 |
| WP15.2"词表违规 1 条（`defect_pattern_checklist.md`）" | 实测 **9 处 / 4 族 / 9 文件**，且无任何门按词表校验文档 `rule_form` | R-A8 |
| WP15.4"路径陈旧 **9 条**→ 逐条改指向" | 9 条 = **21 处文本位**（17 列表值 + 3 散文 + **1 历史 changelog 禁改**） | R-A9 |
| 波1 各车道报"主区 staged 现值" | 111（WP1）→ 112→117（WP15）——**任务书里我写的 107 是发单时刻**，一律以现场 `git diff --cached --name-only | wc -l` 为准 | §0.6 计数现场实测 |
| WP7 改前"退化方向可判分母" | 0（现行 domain→risk_tier_registry→default low 链，86 份全"未规定"）；改后 86 | R-A10 |
| WP11 处方靶 `architecture_model/data/rule_optimization/key_facts.yaml` | **不存在**；真身 `data/rule_optimization/key_facts.yaml`（行号逐字吻合） | R-A24 / C-17 |
| WP11 验收命令 `git grep … -- ':!*_archive*' ':!<path>'` | 本环境两条 `:!` 并用即 `fatal: outside repository`（exit 128）⇒ 改 `':(exclude)…'`，排除集等价 | R-A24 / C-18 |
| `gates` 活库结构（D-17 口径，总包复跑） | 8 列；`gate_run_id` 为 PK、`gate_id` **非唯一**（1791 行/1008 distinct）；`passed` **有** CHECK、`details` **无** CHECK；`gates`≡`gate_runs` 列集；**无任何活库有 `result` 列** | R-A22 |
| 处方"§7 说 `170cba56e0` 的真实件是 `feac5f7b28`"（我原写） | 更正：`6933dbcff3` 才是 R100 迁移件，`feac5f7b28` 是出生件 | R-A11 更正 |
| D-9"`AGENTS.md`↔`agent_constitution_l0.md` 正文≈100% 镜像，仅差 frontmatter+3 行头部" | 实测 **88.18%**（97/110 行），剥 frontmatter 后**无全等点**，残余 29 行、段落级 76.0%，**5 处正文分叉**（含 §0.3 RULE-WORKTREE 两份给不同指令） | R-A12 / C-13 |
| D-8"`adversarial_validation run` 作门禁面回归护栏" | 该护栏当前**区分度 0**（52/52 全走缺 `description` 的 fail-closed 兜底） | R-A13 / C-14 |
| D-9 否决项"project_rules↔AGENTS 重叠≈0" | **复测成立**（共享 1 条=表格分隔符、`trae_*` 锚点 1、`RULE-*` 键 1、0.265%）⇒ 不动它这条判据保留 | — |

- **R-A12｜★ D-9 的"≈100% 全文镜像"被实测推翻，而且真相更坏：两份宪法已经**内容分叉**。**
  实测（WP13 的 `overlap_probe.py`，378 行只读；仪器自证：同文件自比=100%、注入一行语义翻转即被点名）：
  共享非空行 **97** 条 = l0 正文的 **88.18%**（不是"≈100%"）；剥 frontmatter 后**不存在任何 N** 使 `AGENTS[N:]` 与 l0 逐字节全等，
  残余差异 **29 行**、段落级重叠 **76.0%**；AGENTS 独有 16 条 / l0 独有 13 条。
  **5 处正文分叉**里最要命的是 **§0.3 RULE-WORKTREE 两份给的是不同指令**：
  AGENTS 已改成"降级直改主区=**显式申请制**（登记原因，GW 标记自动计数+周审计）"，
  l0 仍是旧文"（或按既定裁定降级走 `scripts/git_commit.py` 正门）"。
  ⇒ 这不是"瘦身目标选错了"，而是**唯一必读宪法有两份互不一致的正文**——每个车道读到的那份不同，行为就不同
  （本役我自己两条纪律（worktree 降级、§8 对齐范围"全图全库"vs"八图"）正落在这 5 处分叉上）。
  ⇒ 触发 §6④（案卷与裁定矛盾）：停手，收敛方向交 Max（C-13）。**波1 已发出的任务书不必撤回**，
  但**后续任务书凡引用宪法条款，必须写明引的是哪一份**。
- **R-A13｜D-8 指定的"护栏命令"本身是假绿，且是教科书级的"恒真返回"**。
  `python -m zephyr.security.adversarial_validation run` 报 `{total:52, blocked:52, blocked_rate:1.0}`，
  真因是 `defense_runner.py:200-215` 构造 `Task(...)` **未传必填字段 `description`** ⇒ pydantic 每次抛 `ValidationError`
  ⇒ 被 `:219` 的宽 `except` 吞掉后按 fail-closed 记成 BLOCKED。stderr 实测 `real_gate_failed 52 / fail_closed 52 / Traceback 52`。
  ⇒ **`blocked=total` 与门禁真实能力无关，区分度=0**（改宪法前后都必然报 1.0）。
  这正是我在全流通战役记下的"假处置一族"里的**恒真返回 + 投递前置闩**混合体：**它看起来在工作，而且报的是满分**。
  ⇒ D-8 说这条只作护栏不替代行为测试；实测后进一步降级：**修好 `description` 之前它连护栏都不是**。列 C-14。

## 1b. Max 更正批的采纳与自我口径修正（`d622d4d180` + `47a7426b7f`，03:0x 复核）

- **R-A14｜本战役报给 Max 的两条"方案内矛盾"均已被裁掉，且 Max 另修了 D-9**：
  - **D-14（矛盾①）**：`docs/01_policies_and_standards/rules/` **全域冻结至 WP9 判案完成**；施工队只出案卷 + **可直接粘贴的替换文本**（逐条给行号），
    落地由 Max 判案后一次性做（须 `[ARCH-APPROVAL:ISSUE_ID]`）。理由里比"受保护路径"更强的一层＝**rules/ 正是 WP9 的判决对象**，
    一边判一边改会造成判决对象漂移、案卷号失去意义。⇒ 我此前给 WP15 定的"只出案卷"处置由裁定升级为明文，WP15.4 的 9 条**确定不落地**。
  - **D-15（矛盾②）**：**主区具名 + `--enqueue` 是合规正门，不算降级、不需登记降级原因**；禁的是"主区直连提交"。
    并追加三条硬前置：① `--files` 只列自己文件；② 热文件须逐字证"对 dev 纯 insert 零 delete"；
    ③ **落地后三态核实**（`git show HEAD:<f>` / `git ls-files -s` 的 blob / 工作区字节三者 sha 一致）——
    队列落地只写工作区不动 index，会留"index 压旧 blob"的回退隐患，实测出现过**新文件 index 位是空 blob**。
  - **D-9 修订（采纳 R-A12）**：两份宪法**不是镜像而是已分叉的双真源**；Max 亲自 `diff --strip-trailing-cr` 复核得 **42 行真实差异**
    （★ 并自陈教训：**不剥行尾符会得到"整文件全差异"的假象，他此前因此误判为镜像**——与我 §4 修正表第 6 行同源）；
    **真源＝`AGENTS.md`**（被 CLI 自动注入且条文更全），`agent_constitution_l0.md` 属过期镜像却自称真源 ⇒ 出口 D1 合并；
    改宪法族一律回流 Max/Owner。另实测 `AGENTS.md` 工作副本是 **CRLF 而 `.gitattributes` 要求 LF**（新记一条隐患，未处置）。
  - **D-16（案卷 TTL）**：小件（`dossiers_summary.json`/`dossiers_index.json`，判决依据）**promote 入 git**；
    逐份案卷正文（14MB 级）留 `.runtime` 双镜像**不入 git**（程序法第 7 节：案卷是派生物）。⇒ 我此前"全部由总包代持"的做法按此拆开。
- **R-A15｜D-17 对我自己 R-A2/C-0 的部分更正**（这条对我最重要，写下来防我再犯）：
  同一个坑 Max 与我各踩一半——他拿 `governance.db` 的 `gate_decisions` 列判 `drift_events.db` 的写入端（误判"必失败"），
  我拿 `sqlite_schema.py` 的 **DDL 源码**判**活库** `tasks.status`（我说"无 CHECK"对活库成立，他说"有 CHECK"对源码成立）。
  ⇒ 判据改硬：**任何表结构断言必须写库文件名 + 从活库读**（`pragma table_info` / `sqlite_master`）。
  ⇒ 真问题升格为独立 WP：**WP16 逐库逐表 DDL↔活库漂移清单**（只出证据，补约束属 DB 结构变更=门位）。已派车道 `st-ramp-wp16-20260919`。
- **R-A16｜D-15 ③ 三态核实已对本战役全部已落件复跑，全 OK**：
  `rule_audit_campaign/CONSTRUCTION_LEDGER.md`（队列件 `-0021`）/ `kimi_audit/lane_reports/C2.md` 与
  `ai_layer_vision/OBJ_S_perimeter/DESIGN.md`（L2 队列件 `dd8badd2c3`，该车道落地后**自己发现并修好了 index 压旧 blob**）/
  `fullflow_campaign/COORDINATION_LEDGER.md` 四件均 `HEAD==index==disk`。命令：
  `git rev-parse HEAD:<f>` × `git ls-files -s <f>` × `git hash-object <f>`。
- **R-A17｜同一次自检抓到"陈旧快照压 index"机制**第三次复发**（非我件，只登记不代修）**：
  `git diff --cached --numstat --ignore-cr-at-eol | awk '$1==0 && $2>0'` 实测：
  ① `docs/_working/bizmine_night/bizmine_campaign_ledger.md` staged 比 HEAD **少 4 行**——少的是已交付台账行
  （`05:5x 币圈 st-bizmine-cry 两卡实测全落（T0-PRERG-01 VWAP RED / T0-PRERG-02 funding carry RED…）`、
  `05:0x 总包 Owner 睡前终令`、`05:0x IND-A/B/C 三切片发车`、`05:0x ALT-B 发车`）；
  ② `tests/frontend/*.py` **11 件各少 3 行治理头**（`[STABILITY]` / `[SAFETY]` / `[AI_AUTONOMY]`）；
  ③ 两类件 worktree 均与 index 不一致（`MM`）⇒ **任何人一次 `commit -a`/全量 add 就把已交付内容清空**。
  与 R-063（写侧 token 蒸发）/R-073（热册 `+0 -4`）/R-074（13 件回退快照，含两件被 index 判删的牙齿测试）**同机制、第四例**。
  ⇒ 结论：`提交侧净删即拦`（B23/B22 配对）不能再等"下一役"，它是本仓**当前复发率最高**的一类缺陷；已按 §3.4 不代修他人 staged 面。
- **R-A18｜C-14 我按 Flash 边界停手（复现完成，不自签落地）**：
  最小复现：`Task.model_fields` 必填集含 `description`，而 `defense_runner.py:200-215` 构造时未传 ⇒
  `ValidationError: description Field required` 被 `:219` 宽 `except` 吞掉、按 fail-closed 记 BLOCKED ⇒
  `blocked=total=52 / blocked_rate=1.0` **零区分度**。可粘贴处方三条：
  ① 补 `description`（值取场景自身字段的组合，**属语义选择 ⇒ 待 Max 定口径**）；
  ② 把 `source`（`real_gate` / `fail_closed` / `simulate`）单列计数进 report，`blocked_rate` 只在 `real_gate` 分母上成立
  （与 D-2"拿不到身份即拒记"同判据）；③ `:213/:214` 的 `datetime.now(UTC)` 换成在册 `zephyr.shared.utils.time_utils.now_utc`
  （我实测 `now_utc()` 可用；`DATETIME-NOW-FORBIDDEN` 会在改这两行的 diff 上命中）。

- **R-A19｜源码树野库的根因不是"某次传参错"，而是 `project_root = dirname×N(__file__)` 与文件深度耦合**（WP1-取证）。
  时间线（四笔 commit 全部亲验）：2026-06-21 `a5c1a81787` 把 `gate_persistence.py` 迁到深度 4 的
  `src/zephyr/governance/drift_detection/` ⇒ 同一份代码 root 落到 `<仓根>/src`；2026-07-12 `78e46622ef`
  把 `_db_path` 从 `str(DB_PATH)` 改成 `os.path.join(_audit_dir, "drift_events.db")` ⇒ **野库当场被建出**；
  次日 `cb1ef2e9ae`(R099) 迁回深度 3 ⇒ 野库被遗弃在树里。
- **R-A20｜★ 该缺陷在 HEAD 仍是活体，且"只删库不改 root"必复发**：实测 import 求值
  `drift_detector.py:59 _PROJECT_ROOT = D:\ZephyrAlpha\src`，并被显式传给 `HotfixBypass`/`AutoFixer`；
  `integration_test_runner.py:172` 同形；两者 `__init__` 都 `makedirs(<src>/data/drift_audit)`。
  ⇒ 同类面普查：全仓"自证为仓库根"的 `__file__` 锚定派生式 **137 处，其中落点异常 23 处**
  （含 `financial_derived_compute.py:53` 与 `pf_alloc` 四件）。
  ⇒ **处方顺序判据（交 Max 定）**：F-2 与 F-1 必须同批判序——**先修 root（唯一真源 `REPO_ROOT`）、再删野库**；
    野库本身是空壳残骸（三表 0 行、`sqlite_sequence` 空、比真库多一张 #62 已废止的 12 列 `drift_events` schema B、
    sha256 与真库不同 ⇒ **非副本**）、**零读方**、且 `.gitignore:100 *.db` 命中 ⇒ 删除不产生任何 git 变更。
    **本战役任何车道不得自行删**（门位第②类）。
- **R-A21｜"假声明"族再添三例，且其中一例是在册热册**（WP1-取证案卷二，全部 `[亲验]`）：
  ① `persist_gate_decision` **从来没有过调用方**（逐 rev 树检 7 次全 0，不是"被摘"）；
    它的"应然调用者"只活在登记面——`cross_module_dependency_registry.yaml:359-368` 的 **DEP-025d 声称 `runtime`/`hard` 依赖**、
    `capability_canonical_file_registry.yaml:1997-2002` 声称消费者为 `drift_engine;detector_dispatcher;alert_router`
    **三者对 `GatePersistence` 的实测引用全 = 0**（而三文件 import 行数 17/11/3，证明 grep 有效、文件非空）。
  ② **`ruling_registry.yaml`（166 条）里查无"裁定号 62"**，而 `gate_persistence.py:24` 与归档裁定书都自称"#62 治本"
    ⇒ 违 RULE-RULING（裁定须先登记且同 commit 原子）；且 #62 原文对这两张表写的是"**是否在用另案核查**"
    ⇒ **不能拿 #62 当"已判空壳"**（这条纠我此前 C-2 表述里的一处 looseness）。
  ③ `governance.db.gate_decisions` 那 **35 行全是测试残留**（`gate_id='GATE-TEST-001'`/`decided_by='test_agent'`
    逐字吻合 `tests/governance/shared/test_governance_db.py:28/389-390`），末条时间戳与 07-27 那次"测试解耦"
    （`9371a46e17`）**同日** ⇒ 属宪法 §9.6"测试禁写生产路径"的历史违规实据；另有 `audit_entries` 中 `actor='test_agent'` 45 行。
    ⇒ **DB 净删行属门位第②类**，只取证未删一行（F-6）。
  ④ 附带一颗未引爆的雷（只报）：`gate_persistence.py:241` 在 **str** 上调 `.get("sha256")`
    （`sha_key` 来自 `data.pop("sha256")`，是 hex 字符串）⇒ **该方法一旦被调用即 `AttributeError`**，
    而外层只捕 `JSONDecodeError/OSError`。调用面未取证（F-9）。

## 5. 波1 追加回执与案卷（WP7 / WP15·2·4）

### WP7 · 闸4 风险档两轴派生（`st-ramp-wp7-20260919`）— 已落地 `f8c1fc044a`

# WP7 回执 — 修"闸4 风险档失明"（裁定 D-7：两轴派生）

会话：`st-ramp-wp7-20260919`　分支：`dev`　日期：2026-09-19

---

### ① 改动清单 + commit hash（归属核实）

**commit `f8c1fc044a`** — `fix(gov/audit): WP7 修闸4风险档失明——对账门直读两轴派生(裁定 D-7)`

`git show --numstat --format= f8c1fc044a`：
```
79	1	src/zephyr/governance/audit/reconciliation_registry.py
```
唯一文件、纯自家内容，未吸收任何他会话 staged 内容（`git log -1 --name-only` 核实）。
改动三点（全部在同一 .py 内）：
1. `from typing import Callable` → `Callable, Final`（1 行替换，即那 1 个删除行）。
2. 模块级新增两轴派生（line ~460-530）：映射常量 `SAFETY_LEVEL_TO_DEGRADATION` /
   `AI_AUTONOMY_TO_GATE_POSITION`（`Final`），函数 `_derive_axis` /
   `derive_rule_risk` / `derive_two_axis_risk_for_rules`。
3. `GATE-RULE-FILE-AUDIT._reconcile_rule_file_audit` 的 report dict 增一行
   `derived_two_axis_risk`（只记录字段，`action` 仍为 `warn`）。

未新增字段到任何规则 YAML；未新增/退役门禁；未触碰派生册。

---

### ② 红证（零基线证明 + 改后非零，输出原文）

**改后代码已落 HEAD，为出"改前 = 0"的对照，harness 的"现行派生链"分支照抄轨A详案
`generate_dossiers.py` 的旧语义（`risk_tier_for(domain/scope)→risk_tier_registry→default low
→expected_fail`），与 WP8 案卷生成器判据同源。只读脚本 `.runtime/tmp/st-ramp-wp7-20260919/wp7_harness.py`。**

```
[分母] trae_*.yaml 文件数 = 86

[safety_level 分布] {'H': 40, 'M': 32, 'L': 14}
[ai_autonomy 分布] {'immutable_core': 34, 'human_gated': 30, 'ai_modifiable': 22}
[缺字段] 0 项
[未知值(不在合法词表)] 0 项

===== 现行派生链（domain→risk_tier_registry）应然退化方向可判分母 =====
expected_fail 分布: {'未规定': 86}
>>> 改前 应然退化方向可判分母 = 0            ← 红/零基线（"没有尺子"）

===== 改后：两轴派生（safety_level/ai_autonomy）应然退化方向可判分母 =====
应然退化方向分布: {'fail-closed': 40, 'fail-closed-own-scope': 32, 'fail-open-with-trace': 14}
人机门位分布: {'owner-required': 64, 'ai-self-decide': 22}
>>> 改后 应然退化方向可判分母 = 86            ← 从 0 变非零（修好）
[对账] safety_level 合法值 H+M+L = 86；可判分母 = 86；相等=True
[未知/不可判退化方向] 0 项
```

**对账结论**：改后"应然退化方向可判分母 = 86 = H(40)+M(32)+L(14)"，与 `safety_level` 分布严格相等，
0 未知值。门位派生：owner-required = immutable_core(34)+human_gated(30) = 64；ai-self-decide =
ai_modifiable(22)，和 = 86。

**红证插曲（CloneGuard 拦截并治本，非绕过）**：首次入队 `q-...-0001` 判死，
`dead_reason = CAPABILITY-OVERLAP：derive_degradation_direction 与 derive_gate_position
extract 级 structural 相似度 100%`——正是 CONSTRUCTION_DISCIPLINE §7 所述"两函数仅剩字面量差别
永不消克隆"的实弹。按 §7 唯一解合并为单一 `_derive_axis`（轴差异降级为 mapping 数据），
CloneGuard 复跑 `passed=True` 后 `requeue` 生成 `q-...-0002` 落地成功。
历史死信 `q-...-0001` 留在 `dead/` 由维护班收敛（我的最终内容已随 `-0002` 落地，非未落地）。

---

### ③ 验收命令与本次实测输出

- `python --version` → `Python 3.12.8`　`[亲验]`
- `python .runtime/tmp/st-ramp-wp7-20260919/wp7_harness.py` → 见 ② 全量输出。　`[亲验]`
- `python -m py_compile src/zephyr/governance/audit/reconciliation_registry.py` → `PY_COMPILE_OK`。　`[亲验]`
- 导入 + 派生自测（含错误路径，证明不臆测填值）：　`[亲验]`
```
derive_rule_risk({'safety_level':'H','ai_autonomy':'immutable_core'})
  → {degradation_direction:'fail-closed', gate_position:'owner-required', judgeable:True/True}
derive_rule_risk({'safety_level':'Z','ai_autonomy':'weird'})
  → {degradation_direction:None, gate_position:None, judgeable:False/False}   # 未知→不可判，不编造
derive_two_axis_risk_for_rules('.', ['__nope__.yaml'])
  → [{error:'load-failed: FileNotFoundError', judgeable:False/False}]        # 载入失败如实上报
```
- 工厂构造 `make_rule_audit_reconciler` → `gate_id=GATE-RULE-AUDIT` 正常返回。　`[亲验]`
- 既有套件：`pytest tests/governance/audit/test_validate_rules_integrity_fold.py` → `4 passed`。　`[亲验]`
- CloneGuard：`CloneGuardOrchestrator(Path('.')).check([file]).passed` → `True`。　`[亲验]`

---

### ④ 门位项与待裁

- **本 WP 门位：否（D-7 明示）**。改动为纯可观测派生字段，未改任何门禁判定逻辑/阈值/flag 出厂默认
  （GATE-RULE-FILE-AUDIT 仍 `action=warn`），不触发 §6.3 停手条件。
- 未新增/退役门禁 → 无 D-5 净零增长对价义务；未提交任何注册表/派生册 → 无 R-074 净删风险
  （我的唯一提交面是一个 .py）。
- **待裁/回流（非阻塞，交 WP8/总包知悉）**：D-7 要求"案卷生成器**与**对账门"都读两轴派生。
  对账门侧（本车道）已落地为 `reconciliation_registry` 的可导入公共函数
  `derive_rule_risk` / `derive_two_axis_risk_for_rules`。**案卷生成器侧在 WP8 的 `_tools/dossier_core.py`
  （本车道禁改）**，需 WP8 在判据收窄重跑时把 `risk_tier_for` 的"应然退化方向"判定改调本公共派生函数，
  才能真正让重跑案卷的"退化方向可判分母"从 0 变非零。此为跨车道接口，非我职权，特此留痕。

---

### ⑤ 证据等级（逐项）

- 86 份规则两字段现场复测（H40/M32/L14；immutable_core34/human_gated30/ai_modifiable22；86/86 齐备）：`[亲验]`
- 改前可判分母 = 0（现行链语义复现）：`[亲验]`（复现逻辑照抄轨A详案 generate_dossiers.py，属 `[亲验]` 复跑）
- 改后可判分母 = 86 且与 safety_level 对账相等、0 未知：`[亲验]`
- 两轴映射值（H/M/L、三 autonomy → 档位）：`[亲验]` 照抄裁定 D-7 原文（判决书原文照抄类，D-13 允许）
- `domain: TRAE` 未登记于 risk_tier_registry → 旧链恒落 default low：`[亲验]`（读 risk_tier_registry.yaml）
- GATE-RULE-FILE-AUDIT 端到端产出 derived_two_axis_risk 字段：`[推断]`——工厂/复合 reconcile 需完整 gateway
  (run_git 等)，我的 stub 不足以跑通全复合链，但该字段是对已单测函数 `derive_two_axis_risk_for_rules`
  的一行纯数据嵌入，函数本身已 `[亲验]`；未做整链 e2e，故此项保守标 `[推断]`（不谎报为 `[亲验]`）。
- WP8 案卷重跑后分母转非零：`[未跑]`（属 WP8 职权，本车道禁改其采集器，未越权代跑）。

---

### ⑥ 未完成部分与原因

1. **案卷生成器侧接线未完成**：WP8 拥有 `_tools/dossier_core.py`，本车道按并发隔离硬约束禁改，
   故只提供公共派生函数供其导入，未代改判据。**不是"没跑成通过"，是越权边界，已回流留痕（④）**。
2. **端到端整链 reconcile 未跑**：缺一个能过 `run_git`/catalog 子流程的完整 gateway stub；
   既有测试套件无 rule-file-audit 专项整链用例。核心函数与 report 字段已分别 `[亲验]`/`[推断]` 覆盖，
   如实标注，未粉饰。
3. 历史死信 `q-...-0001` 未由我删除（死信归维护班处置；我的内容已随 `-0002` 落地，无遗漏）。

**边界自查（全部守住）**：未碰 WP12 的 `GATE-RULE-CATALOG` trigger 前缀（HEAD 内该处仍为
`startswith("docs/01_policies_and_standards/rules/")`）；未碰 WP8 `_tools/`；未碰被
`st-bizmine-20260919` 持 claim 的 `capability_canonical_file_registry.yaml`；未给规则新增字段；
未改判定阈值/flag；派生对每个文件先查 `git status --porcelain` 确认非他会话在途脏后才改。

### WP15(2/4) · 词表违规与路径陈旧（`st-ramp-wp15-20260919`）— 零改动，全部转案卷（另有 `WP15-2_dossier.md`/`WP15-4_dossier.md`/`item4_occurrence_map.txt` 逐字位清单在同目录与冷库）

# 回执 — WP15 第 2 件 + 第 4 件 ｜ 车道 `st-ramp-wp15-20260919`

战役：规则与审计一条龙 ｜ 日期 2026-09-19 ｜ 执行档 Flash
**本车道两件的主要产出＝案卷与处方；对仓内跟踪文件零改动、零提交。**

---

### ① 改动清单 + hash

**零改动。** 未新建任何 tracked 文件（按令："总包代持入库"）。

| 项 | 值 |
|---|---|
| 跟踪文件改动 | 0 |
| 提交 | 0（无改动可提交） |
| `git log --all --oneline --grep="st-ramp-wp15-20260919"` | 空输出（本车道无 commit） |
| HEAD 归属核实 `git log -1 --name-only` | `7e97dca312` ｜ `docs(bizmine): 台账——并发扩容至7车道…` ｜ `[GW:st-bizmine-20260919:q-20260919-st-bizmine-20260919-0003]` ｜ 文件 `docs/_working/bizmine_night/bizmine_campaign_ledger.md` ⇒ **HEAD 是他会话（st-bizmine）的落地，非本车道，无连坐** |
| 10 件靶文件改后复核 `git status --porcelain -- <路径清单>`（7 件 `rules/trae_*.yaml` ＋ 2 件 sop md ＋ 1 件词表 yaml） | **空输出＝全部 clean**（开工时逐一复核 7 件规则文件亦 clean） |
| 主区他会话在途面（开工→收工） | staged `112 → 117`；工作区脏 tracked `107`（均非本车道产生） |

交付物（全部在未跟踪的 `.runtime/tmp/st-ramp-wp15-20260919/`，`.runtime` 已 gitignore）：

| 文件 | 用途 |
|---|---|
| `WP15-2_dossier.md` | 第 2 件案卷：词表真源实测 + 处方甲/乙影响面 |
| `WP15-4_dossier.md` | 第 4 件案卷：9 条逐条处方 + 权限边界判定 |
| `item4_occurrence_map.txt` | 21 处文本位原文（行号 + 行内容） |
| `wp15_4_ruler.py` | 红/绿尺子（可复跑，退出码即结论） |
| `_census_rerun.py` + `census_rerun/` | census 独立复现副本（输出改指本车道，不写他会话 staging） |
| `census_backup/rules_enforcement_census.json` | 抢救副本 |

冷库：`G:/zephyr_cold/30_corpus/rule_audit_v1_20260919/`（目录现 7 件，本车道新增 1 件）。

---

### ② 红证

### (a) 开工第 0 动作 — census 时效抢救（**含一处必须报告的路径更正**）

- 任务书/方案给的路径 `.runtime/sessions/**st-ruledisp-20260918**/staging/rules_enforcement_census.json`
  → **不存在**（`ls` 退出码 2）。
- 全 `.runtime` 检索唯一真身：`.runtime/sessions/**st-auditdoc-v4-20260918**/staging/rules_enforcement_census.json`
  （41065 B，`stale` 段 9 条，与方案"9 条"吻合）。
- **出处坐实用生成器自身，不靠猜**：`_rule_enforcement_census.py` 末行硬编码输出
  `'.runtime/sessions/st-auditdoc-v4-20260918/staging/rules_enforcement_census.json'`。
- ⇒ 判"源件未被 TTL 清除、只是归属会话写错"，**不触发停手**；已双备份。
  备份核对：源件 + tmp 副本 + 冷库副本 **sha256 三份全等**
  `facea6618118bff1ccec25e32433518b6073bfb4021e667c32daa9bdef78d06b`（件数：tmp 1、冷库目录 7）。
- 残留风险（提醒总包）：**源件仍在 24h TTL 区内**，`st-auditdoc-v4-20260918` 工棚（WP15.1 靶）拆除时勿连带清 staging。

### (b) 第 4 件 — 红＝旧指向不存在（9/9 成立），绿＝处方新指向成立

```
$ python .runtime/tmp/st-ramp-wp15-20260919/wp15_4_ruler.py ; echo EXIT=$?
rule      RED old-absent GREEN new-exists tracked  uniq  verdict
TRAE-013  True           True             True     True  OK
TRAE-016  True           True             True     True  OK
TRAE-017  True           True             True     True  OK
TRAE-032  True           True             True     True  OK
TRAE-033  True           True             True     True  OK
TRAE-036  True           True             True     True  OK
TRAE-036  True           True             True     True  OK
TRAE-036  True           True             True     True  OK
TRAE-055  True           True             True     True  OK

条目=9 全绿=True 失败条数=0
EXIT=0
```
**诚实标注**：因本车道零改动，**不存在"改后绿"**。上面的 GREEN 是"候选新值在盘实存 + 在册 + 唯一"，
属处方可用性验证；真正的"改后绿"（census 陈旧数 9→0）须待 §④ M-1 门位放行后由施工方复跑同尺子取得。
起点数字已双证：census 原样 9 条 + **今日独立复跑仍 9 条、集合逐条相同**（`stale identical: True`，
`counts` 全等），排除"历史快照噪声"。

### (c) 第 2 件 — 红＝值确不在词表；且测出"这条词表无牙"

```
$ git grep -n "^rule_form:" | grep -vE ":(declarative|procedural|data|structural)[[:space:]]*(#.*)?$"
… 命中 9 处非法（standard×4 / checklist×2 / reference×1 / report×2）；总声明 224 处
$ python -c "<读 rule_form_vocabulary.yaml>"
MEASURED legal rule_form values: ['declarative','procedural','data','structural'] total_values=4 len=4
'checklist' in legal?  False
$ git grep -c "rule_form" -- scripts/governance/d3_metadata/check_frontmatter_metadata.py
EXIT=1        ← 零命中：阻断型 GATE-FRONTMATTER 根本不查 rule_form
$ python scripts/governance/d3_metadata/validate_rule_frontmatter.py ; EXIT=1
  …FAIL: trae_086…: 缺少必填字段 'provenance' / 字段顺序错误
  RESULT: FAIL (2 个问题)     ← 全仓扫的是 rules/trae_*.yaml，**扫不到 sop/**.md**；且 2 项 FAIL 与本件无关（存量，见 ⑥）
```
⇒ 争点坐实为"违规"，同时坐实**没有任何在册门禁按词表校验文档 rule_form**（案卷 F-1）。

---

### ③ 验收命令与本次实测输出（数字全部现跑）

| 验收问题 | 命令 | 本次实测 |
|---|---|---|
| census 是否仍成立 | `python .runtime/tmp/st-ramp-wp15-20260919/_census_rerun.py` + 与备份逐字段比 | `backup stale len: 9 \| rerun stale len: 9`、`stale identical: True`、`counts` 两份相同、差集两侧皆 `set()` |
| 陈旧口径拆细 | 读 `counts` 字段 | `{short_module:16, missing:48, external:22, **stale_path:7**, ok:67, **archived:2**, process:25}` ⇒ 9 = 7+2（方案未区分） |
| 9 条靶文件真实路径 | `git grep -n -F <旧串> -- docs/.../rules/` | **9/9 全落 `docs/01_policies_and_standards/rules/trae_{013,016,017,032,033,036,055}*.yaml`**（7 个文件） |
| 一处=census 条目 ≠ 一行 diff | 逐行定位（`item4_occurrence_map.txt`） | 文本位共 **21 处**：机器列表值 **17** ＋ 条文散文 **3** ＋ 历史 changelog **1**（`trae_036:893`，禁改） |
| 新指向是否有歧义 | `git ls-files "*/<basename>"` ×6 | 每个 basename 全仓**唯一 1 命中** ⇒ 零条落入"两候选都合理" |
| 受保护路径是否真拦 | `git grep -n -A30 "^PROTECTED_PATTERNS" -- scripts/governance/d6_security/check_protected_paths.py` | `:74 ("docs/01_policies_and_standards/rules/", "重大修改须 Owner 审批（rules/ 下所有 .yaml）")`，被 `PROTECTED-PATHS`(priority=28) import 复用硬阻断 |
| 词表合法值全集 | 读 `…/vocabularies/rule_form_vocabulary.yaml` | `declarative / procedural / data / structural`（4）；`deprecated_values: []` ⇒ 方案该处表述成立 |
| 争点值真实路径+行 | `git grep -n "rule_form: checklist"` | `sop/review_sop/defect_pattern_checklist.md:4`（方案争点）＋ **`sop/governance_sop/alignment_checklist.md:4`（方案漏计）** ＋ 派生册 `rule_catalog_registry.yaml` 2 处 |
| 全仓非法 rule_form | `git grep -n "^rule_form:"` 分类 | 声明 224；合法 215；**非法 9 处 / 4 族 / 9 文件**（`standard`4、`checklist`2、`report`2、`reference`1） |
| `procedural` 是否装得下 checklist | 读词表 `procedural.definition` | 原文含"步骤、**检查清单**、回滚方案" ⇒ 语义等价成立 |
| 处方乙要过哪些门 | 读 `gate_registry.yaml` GATE-VOCAB | `files_trigger: ^(src/zephyr/.*\.py\|scripts/.*\.py\|docs/01_policies_and_standards/_registry/vocabularies/.*\.yaml)$` ⇒ 改词表必触发；`--check` 下未同步重生 schema 即红 |
| 处方乙放开面 | 数 `doc_type: policy` 带 frontmatter 文档 | **35 份**（`docs/01_policies_and_standards` 32 ＋ `scripts/governance` 3） |
| 判决书是否被牵动 | `ruling_registry.yaml` grep `rule_form\|defect_pattern`；`dossiers_index.json` 计数 | 前者**零命中**；`defect_pattern_checklist` **0 命中**、`alignment_checklist` 6 命中（均为条目内容非 frontmatter）⇒ 不动判决实质，只动派生册 2 取值 |
| 陈旧串仓外余量 | `git grep -c -F <6 旧串>` 分组 | `rules/` 内 31 处；**`rules/` 外 23 处 / 17 文件**（不在 9 条之列，未改） |

---

### ④ 门位项与待裁

### M-1【必记 · 方案内矛盾，本车道未自行拍板】§6.2 ⊥ §3 WP15.4（并波及 §2 表与 WP10）

| 侧 | 原文与位置 |
|---|---|
| 要改 | §3 WP15.4"路径陈旧 9 条 → **逐条改指向，一条一提交**"；§3 WP10"Flash 只做 B 类里值可现场确定的部分：**把陈旧指向改成实存路径**"；§2 总表 WP15 门位列 **"否"** |
| 要停 | §6 第 2 项"需要改 `AGENTS.md`、`architecture_model/`、**`rules/`** 下任何内容（受保护路径）⇒ **立刻停手回流**" |
| 冲突点 | 9 条靶文件 **100% 落在 `docs/01_policies_and_standards/rules/`** ⇒ 同一动作既被 WP15.4 要求又被 §6.2 禁止 |
| 代码仲裁 | `check_protected_paths.py:74` 把该前缀列进 `PROTECTED_PATTERNS`，`PROTECTED-PATHS`(priority=28) 硬阻断；逃生仅两条：`[ARCH-APPROVAL:ARCH-*]`（id 须在 `architecture_issue_registry.yaml` 在册）**或** `ZEPHYR_PROTECTED_PATHS_BYPASS=1`（注释自陈"紧急逃生"） |
| 本车道处置 | 取"§6.2 + 门禁更硬"解释 ⇒ **9/9 只出案卷，零改动**；未自造 approval id、未用 env 绕过 |

**请裁三选一**（任一给出即可盲执行）：
1. 在 `architecture_issue_registry.yaml` 登记 1 个 `ARCH-*` issue 供 9 条共用，仍一条一提交（净改动＝A 类 17 行）；
2. 判为 Max 直改（本件案卷即终态）；
3. 拆口径：A 类列表值豁免保护、B/C 类（散文/changelog/含盘符绝对路径）保留人工——顺带裁 §4.2 两条 `archived`。

### 其它门位/待裁项

| # | 项 | 为何停手 |
|---|---|---|
| M-2 | **WP15.2 甲/乙二选一** | 方案 §3 明文"二选一由 Max 定，施工队先只出证据" ⇒ 已交，未选 |
| M-3 | 处方甲若采纳：是否**连带** `alignment_checklist.md` | 方案只列 1 文件；不连带则违规不清零（实测同值 2 处） |
| M-4 | 处方甲是否同批 bump 两文件 `version`/`date` | frontmatter 语义值，无唯一现场来源 ⇒ D-13 禁自定 |
| M-5 | 2 条 `archived`（TRAE-032 / TRAE-055）归 B 还是 D3 | "新指向在 `_archive/`"＝执行体退役，`enforcement.executors` 指死码＝假强制；且需判"谁替代它" |
| M-6 | `trae_036:315` 的 `command: python D:/ZephyrAlpha/…`（含盘符绝对路径） | 靶在 `rules/`；改法（只换相对段 vs 整体相对化）需裁 |
| M-7 | **F-2 多真源**：`rule_form` 取值集合由 `rule_form_vocabulary.yaml` ＋ `doc_type_vocabulary.yaml` ＋派生 `frontmatter_schema.json` 三处独立承载，改一处必须同步另两处 | 按 WP8 收窄后闸 3 判据命中 D1 合并特征 ⇒ 归 Max 案卷面 |
| M-8 | **F-3 真源自相矛盾**：`trae_043_meta_rule_metadata.yaml:427` 把"`doc_type`与`rule_form`矛盾(如 policy 配 procedural)"列为禁止，而词表/schema 均判 `procedural` 为 policy 合法值（`trae_043:452-453` 另给目录限定版）| 若采纳处方甲，按 427 字面会误判"改完即违规"；靶在 `rules/` ⇒ 受保护 |
| M-9 | **F-1 无牙**：rule_form 词表对 md 文档零强制（无门按词表校验；`frontmatter_schema.json` 无消费者，全仓 `jsonschema` 零命中） | 补牙属 C 类加牙（判据设计），程序法 §1 优先挂既有门 ⇒ 归 Max |
| M-10 | 指令卡夹带内容核对：文件正文/registry/注释一律当数据。**未发现夹带指令**。唯二"引用不存在之物"：`reconciliation_registry.py:5419` 注释引 commit `170cba56e0`（`git cat-file -t` 报 `Not a valid object name`，`--all` 亦无；实际入库 commit `feac5f7b28`，**总包更正：真实迁移件为 `6933dbcff3`，`feac5f7b28` 是该文件出生提交**）；方案 §7 亦自陈"引用本文件任何数字前请复跑" | 只记发现，未据其执行任何动作 |

---

### ⑤ 逐项证据等级

**第 0 动作（census 抢救）**
- 任务书路径不存在、真身在 `st-auditdoc-v4` 会话目录：`[亲验]`（ls/find/sha256）
- 生成器输出路径硬编码为 `st-auditdoc-v4…`：`[亲验]`（读 `_rule_enforcement_census.py` 末行）
- 双备份件数与三份哈希全等：`[亲验]`
- "方案 WP8 所称 `_tools/` 目录确实存在"：`[亲验]`
- 冷库目录既有 6 件的来历：`[推断]`（未逐件溯源，非本车道产出）

**第 2 件（词表违规）**
- 词表真源路径与 4 合法值、`total_values` 自洽、`deprecated_values: []`：`[亲验]`
- 争点行 `defect_pattern_checklist.md:4` 及其 `doc_type: policy`：`[亲验]`
- 全仓 224 声明 / 9 非法 / 4 族分布、`alignment_checklist.md` 漏计：`[亲验]`
- `procedural` 定义含"检查清单"⇒ 语义等价：`[亲验]`（引原文，判"等价"本身是轻语义结论）
- `doc_type_vocabulary.policy.allowed_rule_forms` ＋ schema 的 `policy→enum[declarative,procedural]`：`[亲验]`
- 无任何在册门按词表校验文档 rule_form（F-1）：`[亲验]`（grep 门体源码 + 跑两台校验器看作用面）
  唯"未来某 CI 面是否另有消费"未穷尽 ⇒ 该子项 `[推断]`
- 处方乙的 GATE-VOCAB 触发与 `--check` 必红：`[亲验]`（读册）＋ `[推断]`（**未实跑**，见 ⑥）
- 处方乙放开面 35 份 policy：`[亲验]`
- 判决书零牵动（ruling_registry 零命中、dossiers_index 0/6 命中）：`[亲验]`
- `sync_yaml_to_depgraph.py:878` 硬编码 `'declarative'` 为第 7 承载回声：`[亲验]`

**第 4 件（陈旧 9 条）**
- 9 条内容与 `stale` 段原文、`counts` 7+2=9 口径：`[亲验]`
- 今日复跑仍 9 条且集合相同：`[亲验]`
- 9/9 靶文件在 `rules/`：`[亲验]`
- 旧路径 9/9 不存在、新路径实存+在册+唯一：`[亲验]`（尺子 exit 0）
- 21 文本位与 A/B/C 三类分位：`[亲验]`（逐行定位，见 `item4_occurrence_map.txt`）
- `PROTECTED_PATTERNS` 含 `rules/` 且被 priority=28 门 import：`[亲验]`
- "approval issue_id 需在 architecture_issue_registry 在册"：`[转报]`（源＝ `protected_paths_gate.py:41,58` 注释，未跑 reconciler 验证）
- 2 条 `archived` 属退役而非搬家：`[亲验]`（retirement_log:17 / script-manifest 6512,7629 在册）
- "谁替代 assign_module_id / audit_domain_nodes"：`[推断]`（仅给近邻候选，未做调用方 salvage）⇒ 故列 M-5 待裁
- `170cba56e0` 不存在、实际 add commit 为 `feac5f7b28`：`[亲验]`
  **→ 总包更正（04:0x）**：`feac5f7b28` 是**出生**提交；**迁移（R100）**件为 `6933dbcff3`。本行原文保留以存取证过程，结论以更正为准。
- 仓外 23 处/17 文件余量：`[亲验]`
- **未做**："改后绿"（9→0）：因零改动而不成立，未谎报

**环境与边界**
- 开工/收工两次核实 10 件靶文件 clean、主区 staged 112→117、tracked 脏 107：`[亲验]`
- HEAD 归属为 `st-bizmine-20260919`、本车道零 commit：`[亲验]`

---

### ⑥ 未完成部分与原因（含"没跑"清单）

1. **第 2 件按设计不改** — 方案 §3 明文"施工队先只出证据，二选一由 Max 定"。已交甲/乙影响面各一份，未择一，**非欠账**。
2. **第 4 件 9 条全部未落地** — §6.2 与 PROTECTED-PATHS 门拦（M-1）。已备可盲执行的逐字替换文本（A 类 17 行）；缺的是 approval issue 或 Max 直改授权。
3. **未实跑 `generate_derived_files.py --check` / 未实跑 GATE-VOCAB 全链** — 处方乙"改词表即红"是**读门体+trigger 推出的**，未做注入实验。若 Max 倾向乙，开工第一步应先补这条红证（造临时词表改动→看红→撤样），本车道未做 ⇒ 记为 **未证绿**。
4. **未跑 `scripts/governance/d11_compliance/validate_vocabulary_coverage.py`** — 已读源码判定其只查"有无对应词表文件"、不查文档取值 ⇒ 与本件无关，为省轮次未跑（不是"跑了通过"）。
5. **两条 `archived` 的 salvage（谁还在消费）未做穷尽** — 只给了 grep 近邻，未剔 re-export/测试/文档；M-5 需此数据才能定 B 还是 D3。
6. **`validate_rule_frontmatter.py` 现测 2 项 FAIL（`trae_086_frontend_module_construction.yaml` 缺 `provenance` ＋ 字段顺序）** — 与本件两靶无关的存量，**未代修**（宪法 §3.4 owner 责任制），仅登记。
7. **census 源件仍在 24h TTL 覆盖下** — 已 tmp+冷库双备份；源件本体未 promote（不属本车道权限，且 WP15.1 拆工棚可能连带）。建议总包把该案卷需要的 4 件产物 promote 到 `docs/_working/`。
8. **未碰** `capability_canonical_file_registry.yaml`（`st-bizmine-20260919` 持 claim + R-073 风险）— 全程零接触，已核。
9. 派生册 `rule_catalog_registry.yaml` 本车道工作区显示为 `MM`（他会话 staged＋工作区脏），**本车道只读不写**（读取仅为证明它抄录了 2 处 `checklist`），未做任何修改，也未 claim。归属自证：本车道全部写操作的目标路径均在 `.runtime/tmp/st-ramp-wp15-20260919/` 下（6 件，见 ① 表）；该册收工实测 mtime `2026-09-19 02:31:11`、未 staged 差异 `+50/-5`，与"生成器重生"形态一致 ⇒ 判为他会话（bizmine 侧）在该时刻重写，非本车道，亦无连坐（本车道零 commit）。

### WP13 · 记忆/宪法文档收敛（Flash 侧三件）（`st-ramp-wp13-20260919`）— 宪法一字未动

# WP13 回执（Flash 车道 · 只做 D-8/D-9 里 Flash 可做的三条）

会话：`st-ramp-wp13-20260919`　日期：2026-09-19　铁律执行：**宪法文档零改动**
（`git status --porcelain -- AGENTS.md docs/.../agent_constitution_l0.md .trae/rules/project_rules.md` 输出为空；
三份文件 sha256(16) 开工与收工同为 `22e1c246d8db93d2` / `1aa67ab326d0e159` / `683f94e2f54a1152`）

---

### ① 产物清单与路径（**tracked 改动＝0，因此无 commit hash**）

全部产物在 `.runtime/` 下（`.gitignore:262` 的 `/*` 规则覆盖 ⇒ 不入库），并已冷备到非 TTL 介质
`G:\zephyr_cold\wp13_st-ramp-wp13-20260919_20260919\`（24 个文件 / 250KB）。

| 对应任务 | 产物 | 说明 |
|---|---|---|
| ① 重叠率机证 | `.runtime/tmp/st-ramp-wp13-20260919/overlap_probe.py`（378 行，只读） | 输入只有三份 md 文件，不改任何文件 |
| | `.../overlap_report.md` + `overlap_report.json` | 三组数字 + project_rules 复测 + 仪表自证 |
| ② A/B/C 材料 | `.../make_ab_pack.py`（337 行） | 出包器（含 C 组可区分性探针、B 砍法影响面探针、题面覆盖探针） |
| | `.../ab_pack/A.md`（**raw bytes 与 AGENTS.md 全等**：12058B，sha256(16) `22e1c246d8db93d2`，CRLF 未转译） | A 组＝只持现行文档 |
| | `.../ab_pack/C.md`（124 行） | C 组＝阳性对照（砍掉 §0 冷启动序列，原第 11-27 行） |
| | `.../ab_pack/B.md` | **只有处方**（D-13）：三种砍法实测行数/影响面 + 待 Max 选定 |
| | `.../ab_pack/b_variant_probe.md` / `b_variant_counts.json` | 三砍法实测：128/134/89 行，丢失与被削弱锚点逐条 |
| | `.../ab_pack/scenarios.md`（139 行） | 10 个实战场景题面 + L72-75 判定口径原文与映射 + 判分表模板 |
| | `.../ab_pack/c_discrimination.md` / `c_discrimination.json` | 红证本体（见 ②） |
| | `.../ab_pack/paper_coverage.json` | 卷子对各章节的覆盖度（实测出盲区） |
| | `.../ab_pack/HOWTO_double_blind.md` | 怎么跑双盲（角色/隔离/计分/达标判据/解封） |
| | `.../ab_pack/blind/pack_1.md`、`pack_2.md`、`mapping.json` | 标签洗牌（seed=20260919）；当前只有 A/C 两包 |
| ③ 门禁面护栏 | `.../adversarial_run.json`（CLI stdout 原样）+ `adversarial_run.stderr.txt`（834 行全文） | |
| | `.../adversarial_run_summary.md` | 结论计数 + "为什么 1.0 不是绿灯" |

禁碰清单执行：`capability_canonical_file_registry.yaml` 未读写；`reconciliation_registry.py` /
`rollback_verifier.py` / `gate_persistence.py` / `st-ruledisp-20260918/staging/_tools/` 全程未触碰（本车道连只读都不需要）。
未新建任何 tracked 文件 ⇒ 无 CREATE-GUARD / 翻译登记欠账；未提交 ⇒ 无归属核实项（`git log -1 --name-only` 不适用，见 ⑥）。

### ② 红证＝C 组可区分性（本车道具体化）

D-8 要求"C 必须显著差于 A，否则废卷重出题"。**行为面**（真派子代理答题）本车道按指令未跑，
所以我出的是**材料面的可区分性机证**：把每题"正确答案必须含的字面锚点"拿出来，验它在 A 在不在、在 C 还差不差。

命令：`python .runtime/tmp/st-ramp-wp13-20260919/make_ab_pack.py`（重跑即得下表）

| 场景 | 答案锚点 | 设计期望 | 在 A | 在 C | 符合设计 |
|---|---|---|---|---|---|
| S1 | `$env:LOCALAPPDATA\Programs\Python\Python312` | must flip | 是 | **否** | ✅ |
| S2 | `python -m zephyr.trading.process_reaper --status` | must flip | 是 | **否** | ✅ |
| S3 | `lock_files.py acquire <file> <sid>` | must flip | 是 | **否** | ✅ |
| S4 | `capability_lookup.find(<kw>, session_id=<sid>)` | must flip | 是 | **否** | ✅ |
| S5 | `apply_depgraph.py --add-design-node` | must flip | 是 | **否** | ✅ |
| S6–S10 | `scripts/git_commit.py` / `safe_write_text` / `check_tick_duplication.py` / `docs/registry_of_registries.yaml` / `trae_062_ssot_classification.yaml` | must survive | 是 | 是 | ✅ ×5 |

- 冷启动敏感题翻转 **5/5**，对照题存活 **5/5** ⇒ 判定 **PASS**（`ab_pack/c_discrimination.md`）。
- C.md 与 A.md 的行差 **17 行 = 恰好 §0 一节**（原第 11-27 行），未误伤别处 ⇒ 阳性对照是"单变量"的。
- **仪器本身的红/绿对照**（`overlap_report.md` §3）：同一文件自比 ⇒ 行共享 113/113、段落 27/27（100%）、字节全等点在 drop=0（绿）；
  在 l0 第 38 行注入一条硬规则语义翻转（`RULE-GUARDIAN` 的"存活是写操作前提"→"与写操作无关"，**纯内存，不落盘**）
  ⇒ 行共享由 97 降到 96，且**仪器点名该行进入"l0 独有"清单**（`injected_line_reported_as_unique=True`）（红）。
  ⇒ 报"不是镜像"这件事不是我的判断，是仪器在能报全等的前提下报出了不等。
- **诚实边界**：以上证明的是"C 组拿不到这些答案要素"，"因此被试答案会变差"这一步是 `[推断]`
  （推断依据＝这 5 题的必含判分点就是这些字面命令，文档里没有第二处可推）。真正达标与否要等 HOWTO 跑批。

### ③ 验收命令与本次实测输出

### (a) 重叠率三组数字

命令：`python .runtime/tmp/st-ramp-wp13-20260919/overlap_probe.py --md .runtime/tmp/st-ramp-wp13-20260919/overlap_report.md --json`
（JSON 落 `overlap_report.json`；两文件均已在 `G:\zephyr_cold\...` 冷备）

- **数字 A｜共享非空行**：整文件原样字面行 **97** 条；剥 l0 frontmatter 后归一化比对同为 **97** 条；
  占 l0 正文非空行（110 行）**88.18%**；其中章节标题行 11 条；`trae_*` 锚点共享 5 个、`RULE-*` 键共享 14 个。
- **数字 B｜各自独有**：AGENTS 独有 **16** 条、l0 独有 **13** 条（换行不敏感的段落级：AGENTS 8/27 块独有、l0 6/25 块独有）。
- **数字 C｜差异是否只在 frontmatter + 头部 N 行**：**否**。
  l0 frontmatter = 11 行、AGENTS 无 frontmatter；剥掉 frontmatter 后**不存在任何 N** 使 AGENTS[N:] 与 l0 逐字节全等
  （最小头部丢弃点 `None`，全等头部点 `无`），残余差异 **29 行**；段落级重叠 **76.0%**。
  分叉点位（实测原文摘录）：§0.3 RULE-WORKTREE（AGENTS 已是"为默认；降级直改主区=显式申请制（登记原因，GW 标记自动计数+周审计）"，
  l0 仍是旧文"（或按既定裁定降级走 `scripts/git_commit.py` 正门）"）、§0.4 能力反查（AGENTS 多"施工/新模块另必读 construction_workflow_policy.md"）、
  §1 表第 3 行、§6.2 检索序（AGENTS 多"方法论真源地图=sop/README.md 九族索引"）、§8（AGENTS"全图全库对齐"vs l0"八图对齐"）、
  末节（l0="## 切换程序（本文件转正流程）"4 步，AGENTS="## 切换记录"3 行）。

### (b) project_rules.md ↔ AGENTS.md（D-9 用它否决第二瘦身目标）——**复测成立**

- 共享非空行：去重 **1** 条 / 多重集 **1** 条（就是表格分隔符 `|------|------|`），占 project_rules 非空行（377）**0.265%**；
- 共享 `trae_*` 锚点 **1** 个（`trae_062_ssot_classification`）、共享 `RULE-*` 键 **1** 个（`RULE-GIT-SAFE`）。
- ⇒ 与 D-9 括号里的三个数（1 条/1 个/1 个）**逐项吻合**，"正交"声明成立，**未动 `.trae/rules/project_rules.md`**。

### (c) 门禁面护栏

命令：`python -m zephyr.security.adversarial_validation run`（exit=0，耗时 duration_ms=411.6）

```json
{ "session_id": "RB-dffa42c13243", "total": 52, "blocked": 52, "bypassed": 0, "blocked_rate": 1.0 }
```

stderr 计数（实测）：`real_gate_failed` **52**、`fail_closed … BLOCKED` **52**（distinct scenario 52）、`Traceback` **52**、
`lock_time_check_failed` **2**（file=models.py rc=2）；`status` 另测得注册场景 **53**（T1:18/T2:22/T3:5/T6:8）。

**判读（重要，别当绿灯）**：52/52 全部没走到真门禁——`src/zephyr/security/adversarial_validation/defense_runner.py:200-215`
构造 `Task(...)` 未传必填字段 `description`，pydantic 每次抛 `ValidationError`，被 `:219` 的宽 `except` 吞掉后按 **fail-closed → BLOCKED** 记账。
⇒ `blocked=total` 与门禁真实能力**无关**，这条护栏当前**区分度为 0**（改宪法前后都必然报 1.0）。
按 D-8 原限定＋本实测：**本条 JSON 不构成、也不能被写成"A/B 已通过"**（回执通篇未这样用）。

### ④ 门位项与待裁清单

| # | 事项 | 性质 | 交给谁 |
|---|---|---|---|
| 1 | **D-9 的断言与实测矛盾**：AGENTS↔l0 正文重叠 88.18%（非"≈100% 镜像"），差异远不止"frontmatter + 3 行头部"（29 行残余 / 5 处正文分叉）。触发总方案 §6 情形④（"案卷或普查出现与本文件裁定矛盾的证据"）⇒ 我已停手（本就无权改），只交案卷 | §6④ 回流 | Max |
| 2 | **镜像收敛方向**（保谁为真源、另一份改指针还是删）＋**"现行宪法"到底是哪一份**：mtime 显示 AGENTS(09-16) 比 l0(09-12) 新，但 l0 frontmatter 自称"现行宪法真源"；两份在 RULE-WORKTREE 上给不同指令＝**A 组材料选哪份会直接改变分数**。本车道按 D-9 字面取 AGENTS.md 作 A | 宪法=high 档＋受保护路径，须 `[ARCH-APPROVAL:…]` | Max（Owner 门位） |
| 3 | **B 组砍法未选**（128/134/89 行三案，实测影响面见 `b_variant_probe.md`；B2 会真丢 S10 锚点、B1/B3 当前卷子测不出） | 语义判断，D-13 只出处方 | Max |
| 4 | **补题裁可**：`paper_coverage.json` 实测 §3–§9＋切换记录（72 行，占全文 51%）零题面覆盖 ⇒ 若瘦身目标是"砍后半段"，现有卷必报"零损失"。建议加 5 题（连坐作用域/退役审计/门位 tier/上下文预算/裸 duckdb 禁令） | 出题需判断"什么值得考" | Max 批准后我再补（我可机械生成） |
| 5 | **`defense_runner.py:200` 缺 `description`** ⇒ 护栏假绿；同类病＝WP2/D-2"拿不到 gate_id 即拒写并告警"（分子混入兜底）。另 `:213` 用 `datetime.now(UTC)`，与 RULE-SCHEMA-TZ"生成器禁 datetime.now()"的口径需对齐核查 | 非本车道范围（属 WP2/WP4 门禁执行链） | 回流 Max / WP2、WP4 owner |
| 6 | 是否要把本案卷（重叠率＋A/B 材料）promote 到 `docs/_working/`（`.runtime/tmp/` 有 24h TTL，现已冷备 G: 一份） | 新建 tracked 治理文档＝三连门风险（FILE-PLACEMENT-TTL / N-11 / creation_token），且需与他会话 107 件 staged 抢队 | 待总包裁；本车道未提交 |

### ⑤ 证据等级（逐项）

- `[亲验]`（本车道自己跑出来的）：
  1. AGENTS↔l0 三组数字（97 条 / 16 & 13 条 / 无全等点、残余 29 行、段落级 76.0%）与 6 处分叉点位（5 处正文＋1 处末节）的原文摘录；
  2. project_rules↔AGENTS 复测（1 条 / 1 锚点 / 1 键 / 0.265%）；
  3. C 组可区分性 5/5 翻转 + 5/5 存活、C 与 A 行差恰为 §0 的 17 行；
  4. 仪器自证（绿＝100% 自比、红＝注入行被点名且共享数下降）；
  5. 护栏 JSON（52/52/1.0）与 stderr 三类计数（52/52/52/2）、注册场景 53；
  6. `defense_runner.py:200-215` 缺 `description` 与 `:219` 宽 except（我直接读码核实，非日志转述）；
  7. 宪法三文件开工/收工 sha256 相同、`git status --porcelain` 对它们为空；
  8. B 三砍法行数（128/134/89）与锚点丢失/削弱清单、`paper_coverage.json` 盲区；
  9. 出包器的越界写保护实弹：`--out docs/_working/wp13_probe_should_refuse` 被拒且未创建目录；
  10. `A.md` 与 `AGENTS.md` 的 raw bytes 全等（同一 sha256(16)、同 12058B、同 CRLF）——第一次跑批时 A.md 是文本再编码产物，
     被这项复核抓出后已改为字节复制（**自我更正一次，留痕**）。
- `[转报]`：`#ARCH-310 R3` 的 A/B 原法与先例（commit `c964c376c0`/`f2e92de716`，32 场景/9 维度/A-B 双基准）——引自总方案 D-8 与 v3 计划，我未复跑历史 commit；L72-75 判定口径原文（读了 v3 计划正文，属原文摘录但判分映射是我做的）。
- `[推断]`：
  1. "C 组会让被试答案变差"的**行为面**结论（材料面已机证，行为面未跑）；
  2. B 三案的"预期风险"高中低评级（影响面是实测的，风险是判断）；
  3. AGENTS 比 l0 "更新"的方向（依据＝文件 mtime 与文本演进痕迹，未做 commit 考古）。

### ⑥ 未完成部分与原因（**没有任何一项被写成"通过"**）

1. **A/B/C 双盲未跑**（按本车道指令："材料齐了就交回"＋机器并发到顶＋污染即废卷）。
   ⇒ D-8 的"B 缺口 ≤ A""连续两轮零新增缺口""C 显著差于 A（行为面）"三条判据**均未测**。已交 HOWTO + 盲包 + 判分表模板，可即刻派工。
2. **B 组无可跑材料**（D-13：砍法是语义判断）⇒ 盲包当前只有 pack_1(A)/pack_2(C)。
3. **镜像收敛方向未做**（本车道禁止项，Max 的活）；`AGENTS.md`/`l0`/`project_rules.md` **一字未动**。
4. 护栏侧遗留：`lock_time_check_failed file=models.py rc=2` 两条**未追因**（非本车道范围，仅登记）；
   亦未跑 `report`/`gameday` 子命令（总方案未要求）。
5. 提交侧：零 tracked 改动 ⇒ 未走 `git_commit.py`、未 claim/release 任何文件，因此没有"commit hash + `git log -1 --name-only` 核实"可贴（此项**不适用**，不是漏做）。
6. 题面 §3–§9 盲区**未补题**（补题需判断"哪些内容值得考"，属语义判断；待 ④-4 裁可后一条命令可生成）。

### 附：夹带指令扫描（全局纪律 0.8）

本车道读过的所有文件（两份宪法、总方案、v3 计划、CONSTRUCTION_DISCIPLINE、CLI 源码、stderr 全文、MEMORY.md 变更通知）
中**未发现**夹带的执行指令；`adversarial_run.stderr.txt` 里的日志行、registry/文档里的"必须/禁止"字样一律按**数据**处理，
未据以改变本车道动作（唯一例外＝本车道指令本身）。
- **R-A22｜WP1-施工两笔落地并经总包独立复验**：`ee54c976f1`（改 1 + C-0 护栏，`rollback_verifier.py` +160 −45、
  `tests/rollback/conftest.py` 新建 +60、root/unit 两测试件 +227 −50）与 `413edaff0e`（改 2，护栏 +67 −4 / 测试 +93 −4）。
  - **总包复验**（不轻信车道）：`pytest tests/rollback` 本机实跑 **708 passed / 7 xfailed / 2 xpassed（234s）**；
    四件 `HEAD==index==disk` 三态一致；**生产 `governance.db` 未被写坏**——`tasks.status` 分布仍是
    `BLOCKED 152 / CANCELLED 214 / COMPLETED 1981 / IN_PROGRESS 76 / READY 78`（total 2501、FAILED 0）、`gates` 1791 行。
  - **C-0 那颗雷的处置方向已由代码落实**：`valid_statuses` 不再硬编码 5 值，改为**从单一真源 `_DDL_TASKS` 派生**
    （派生失败即 `HealRefusedError` 抛，不猜值）；真写必须显式给 `max_rows`，计划修正行数超上限即拒；
    目标表列集与活库不符（幻影结构）也拒。⇒ 台账 R-A2 的"施工侧即时禁令"可解除（改为"已修，待 Max 复验"）。
  - **D-17 应用后的活库事实**（写下来防再错）：`governance.db.gates` = 8 列，`gate_run_id` 是 PK、`gate_id` **非唯一**
    （1791 行 / 1008 distinct ⇒ 用 `gate_id` 定位 UPDATE 会误伤）；`passed` **有** `CHECK(passed IN (0,1))`，
    而 `details TEXT NOT NULL DEFAULT '{}'` **无 CHECK**；`gates` 与 `gate_runs` **列集完全相同**；
    ★ **全仓没有任何活库存在 `result` 列** —— 幻影结构只活在测试自建的临时库里（这正是"52 例全绿却查不出空转"的根因）。
  - ⚠️ 遗留两件小账：① 那 **2 个 xpassed**（xfail 标记因本次修复而失效，应摘帽，属测试卫生）；
    ② 改 1 的"合法面重定向"里，可非法面已挪到 `details` JSON 可解析性与 `passed`×`gate_run_id` 完整性链，
    但**"这台校验现在到底能拦什么"应进 WP4 对账门的一次实测复核**（不凭本次自述结案）。
- **R-A23｜★ 队列落地不刷主区 index——同一隐患第二次独立复现，升为系统性缺陷（C-16）**。
  L2 车道先发现（它自己具名 `git add` 抹平），WP11 再撞上：`--enqueue` 落地后
  `HEAD=<新 blob>` / `index=<改前旧 blob>` / `worktree=<新内容>` 三态不一致（`git status` 显 `MM`）。
  ⇒ **后果**：任何人此后一次 `commit -a`/全量 add，就把该文件**静默回退到改前版本**——
  与 R-063（写侧 token 蒸发）、R-073/R-074（陈旧快照压 index）**同族第四、五例**，但这次的成因不是坏写入端，
  而是**队列落地语义本身**。⇒ 治本方向交 Max：serializer 落地后应对受影响路径做一次主区 index 刷新
  （或落地回执里强制输出三态 sha 并由网关拦不一致）；施工侧对策已生效=**D-15③ 每次队列落地后必做三态核实**。
- **R-A24｜WP11 堆一落地 + 六条新缺陷（F-1..F-6），其中一条会让校验器惩罚正确写法**。
  - 落地：`7f68805b98`（`_registry/catalogs/index.md` 删"外部登记表"僵尸行 + 模板第 666 行改为
    `frontmatter → 生成器` 链）。断链尺子（在册 `audit_broken_links.py`）实测 `blueprint_registry` 断链 **2 → 0**、
    全量断链 5 → 3，并做了**注入-撤样双向阴性对照**；`git grep` 基线 383 行/119 件 → 381/118，变化的**恰是那两行**。
  - **处方第 5 条被车道按 §6.6 拒绝执行**（三条理由：前置未成立 / 该括号目前为真 / 该文件在 WP9 判决对象面上）
    ⇒ 总包认同，这比"照单全做"更对。
  - **F-1 方案路径又错**：`architecture_model/data/rule_optimization/key_facts.yaml` **不存在**，
    真身 `data/rule_optimization/key_facts.yaml`（行号 113-114/323-332/545-554/581 与真身逐字吻合）。
    ⇒ 与 R-A7（census 路径错）同族第二例：**处方里的路径必须逐条实测后再派工**。
  - **F-2 ★ 命名事实自相矛盾**：`key_facts.yaml` 里 `fact` 与 `must_not_appear_as.pattern` **是同一个串**
    （`blueprint_registry.yaml`），`reason` 还写着"连字符写法错误，实际文件名用下划线 blueprint_registry.yaml"
    ——即**被判"错误"的 pattern 就是它推荐的正确写法**；成因疑似历次"把连字符全量 sed 成下划线"时把 pattern 一起改了。
    ⇒ **任何按此册跑的校验都会把正确写法判成违规**。修法需语义判断 ⇒ 未自拟，列 C-17。
  - **F-3 派生退库留下不可满足断言**：同册三条 `must_appear_in` 指向 ROOR / `registry_of_registries.yaml` /
    `project_rules.md`，实测 **ROOR 命中 0、project_rules 命中 0** ⇒ "必须出现"永假；
    且该册在册消费者只找到一个，还在 `scripts/governance/_archive/`（归档 one-off）⇒ 疑似僵尸台账（同 C-17 并案）。
  - **F-5 验收排除式屏蔽了一条活体链接**：处方按"历史 changelog"意图写 `':!docs/03_modules/_cross_layer/*/blueprint.md'`，
    却连带屏蔽 `context_engine/blueprint.md:125` 的**真 file:/// 链接**（非 changelog 行）⇒ 判据自身有洞。
  - **F-6 同类缺陷另有 4 处未列**（含可写路径上的 `scripts/governance/d7_code/fix_n13_snake_case.py:22` 自指矛盾：
    "删除 1 个遗留存根 blueprint_registry.yaml（真源为 blueprint_registry.yaml）"）。
  - **F-4 判据不可二值化**：`audit_broken_links --ci` 对模板件改前改后**都是 exit 1**（占位符 `tests/xxx.py` 等常驻红）
    ⇒ 若有门以它硬阻断模板文件，信号只能取"特定串断链条数"，不能用文件级退出码（列 C-18）。

## 6. WP1-取证车道案卷（改 3 + salvage，全程只读，零改动）

- 产物 13 件双镜像：`.runtime/tmp/st-ramp-wp1c-20260919/` 与冷库 `G:/zephyr_cold/30_corpus/rule_audit_v1_20260919/wp1c/`
  （`sha256sum -c MANIFEST_sha256.txt` ⇒ 13/13 OK）。含 `DOSSIER-1_stray_db.md`、
  `DOSSIER-2_persist_gate_decision_salvage.md`、四支探针与**九组"仪器能红"双向对照**（`controls_a/b.txt`）。
- 只读纪律自证：三库主文件 size+mtime 探针前后**逐位不变**；`mode=ro` 下三次写试探全部 `attempt to write a readonly database`。
  ★ 车道诚实披露一处非数据写痕：以 `mode=ro` 打开 WAL 库会刷新同目录 `-shm`（32KB 索引映射，非数据）。
- 门位/待裁登记：F-1 删野库（第②类，未执行）· F-2 root 与删库的先后序（同批判序）· F-3 "裁定号 62" 未登记 ·
  F-4 热册 CONSUMERS 虚假声明 · F-5 蓝图指向不存在路径 + DEP-025d 声称 runtime/hard 而代码零实现 ·
  F-6 生产库 35+45 行测试残留（净删门位）· F-7 注释 commit 号错指 · F-8 词表 5/10/14 三源不一（闸3 多真源）·
  F-9 `:241` str.get 潜在 AttributeError（未取证调用面）。

## 7. 波1/加料批次回执（WP1-施工 / WP11）

### WP1-施工（改 1 + 改 2，`st-ramp-wp1b-20260919`）— 已落地 `ee54c976f1` / `413edaff0e`

# WP1-施工（改 1 + 改 2）回执 · 车道 `st-ramp-wp1b-20260919`

日期：2026-09-19　分支：`dev`　范围：`docs/_working/2026-09-18-gate-identity-root-fix-plan.md` §WP1 的**改 1、改 2**两条（逐字照办，未自扩）
冷启动：`python --version` = **Python 3.12.8**；`python -m zephyr.trading.process_reaper --status` → `last_run=2026-09-18 19:10:55`（计划任务存活，写操作前提满足）。
本车道改前逐件 `git status --porcelain -- <f>` 全为 FREE/干净 + `lock_files.py acquire` 成功（4 件：源文件、两个测试文件、`tests/rollback/conftest.py`）。
`CapabilityLookup().find(...)` 已按 RULE-CAPABILITY-LOOKUP 以本会话 id 留审计（三次查询全部 0 命中，见④.6）。

---

### ① 改动清单 + 各批 hash（归属核实）

两批，各自带用例，同一文件族，每批完成立即落地（无攒批）。

### 批 1（改 1 + C-0 护栏）= commit `ee54c976f11e4e8600a7bd6a3f231cdd741ec172`

```
$ git log -1 --name-only --format='%H %s' ee54c976f1
ee54c976f11e4e8600a7bd6a3f231cdd741ec172 fix(rollback/gov): WP1改1 heal_db_consistency 按活库实列重写 + 拆 C-0 破坏性地雷

src/zephyr/infrastructure/rollback/rollback_verifier.py
tests/rollback/conftest.py
tests/rollback/test_rollback_verifier_root.py
tests/rollback/test_rollback_verifier_unit.py
```
numstat（`git diff --cached --numstat` 于提交前）：源 `160/45`、conftest `60/0`、root 测试 `125/27`、unit 测试 `102/23`。

### 批 2（改 2）= commit `413edaff0e7d43309fca0c49f5458b7d030aeaca`

```
$ git log -1 --name-only --format='%H %s' 413edaff0e
413edaff0e7d43309fca0c49f5458b7d030aeaca fix(rollback/gov): WP1改2 clean_pycache 加三重护栏——拆 shutil.rmtree 破坏性地雷

src/zephyr/infrastructure/rollback/rollback_verifier.py
tests/rollback/test_rollback_verifier_root.py
tests/rollback/test_rollback_verifier_unit.py
```

### D-15③ 队列落地后三态核实（HEAD blob / index blob / 工作区字节）

```
批 1：rollback_verifier.py            HEAD=bd3f0714… IDX=bd3f0714… WT=bd3f0714… TRIPLE_MATCH
      tests/rollback/conftest.py      HEAD=96558196… IDX=96558196… WT=96558196… TRIPLE_MATCH
      test_rollback_verifier_root.py  HEAD=d85dfe62… IDX=d85dfe62… WT=d85dfe62… TRIPLE_MATCH
      test_rollback_verifier_unit.py  HEAD=bdb93c7a… IDX=bdb93c7a… WT=bdb93c7a… TRIPLE_MATCH
批 2：rollback_verifier.py / root / unit 三件全 TRIPLE_MATCH（`git status --porcelain` 对 4 件均为空）
```
两笔 commit 的文件清单**恰为本车道具名清单**，未吸收任何他会话 staged 内容（主区 staged 现量在发单时为 203 件，实测见⑤）。

### 逐条对处方

| 处方条目 | 落点 | 状态 |
|---|---|---|
| 改 1：按活库实列重写（用 `passed` 不用 `result`） | `_SQL_GATES_SCAN` + `_gate_row_fixes()` | 完成 |
| 改 1：UPDATE 定位用 `gate_run_id` | `_SQL_GATE_MARK_NOT_PASSED` / `_SQL_GATE_RESET_DETAILS` | 完成 |
| 改 1：内层 `except Exception` 不得静默吞 | 三处宽 except 全删；改抛 `HealRefusedError`（口径不匹配 ⇒ 取抛出，见④.1） | 完成（选"抛出"分支） |
| 改 1 附：负向用例 | root/unit 各 1 条幻影结构用例 + `details` 非 JSON 真非法面用例 + 上限护栏用例 | 完成 |
| 改 1 附：同批修幻影 fixture（root:124/140/155、unit:56）+ 同步 root:148/unit:178 断言 | `conftest.py: live_gates_ddl`（活库 DDL 逐字照抄）；两处 `gates_fixed == 1` 断言改挂到真实可非法面 | 完成 |
| 改 2：三重护栏 ①`is_relative_to` ②仓根可验证 ③命中拒删并报错、先验后删 | `clean_pycache()` + `_require_verifiable_repo_root()` + `_escaped_pycache_targets()` | 完成 |
| 改 2：外层 `except Exception` 只 `logger.warning` 的旧行为改掉、但不炸穿调用方 | 读调用方后取抛出（生产调用方 0，见④.5） | 完成 |
| C-0 (a) 词表单一真源派生 | `_derive_task_status_vocabulary()` 读 `sqlite_schema._DDL_TASKS` 的 `CHECK(status IN (...))`，派生不出即抛 | 完成 |
| C-0 (b) 真写前 dry-run + 行数上限护栏 | 默认 `dry_run=True`；真写必须显式 `max_rows`；超限抛 `HealRefusedError` | 完成（上限值不自拍，见④.2） |
| 不做：`gate_persistence.persist_gate_decision()` INSERT | 未触碰该文件 | 遵守 |
| 不碰：`src/data/drift_audit/drift_events.db` / 任何库文件删除 | 全程只 `mode=ro` URI 读；未删任何文件 | 遵守 |

---

### ② 红证

### 2.1 改 2（处方指定：`_project_root` 指向临时目录树，确认护栏拒删并报错）

仪器：`.runtime/tmp/st-ramp-wp1b-20260919/_pycache_guard_probe.py`（同树同输入分别喂 HEAD 版与新版模块）。
**全程只在 `tempfile.mkdtemp()` 造的树上跑，未在真仓根执行过任何删除。**
仪器自证：HEAD 副本与 `git show ee54c976f1^:src/.../rollback_verifier.py` 逐字节相同
（sha256 前缀均为 `608450b8b004f8d1`，脚本比对输出 `identical: True`）。

```
$ python .runtime/tmp/st-ramp-wp1b-20260919/_pycache_guard_probe.py
--- 改前（HEAD 原始实现） ---
project_root = C:\Users\fanzi\AppData\Local\Temp\wp1b_pycache_cutg6470\old\misresolved_root
仓根标记检查: .git exists=False  AGENTS.md exists=False
删除前目录清单（8 项）: ['KEEP_ME.txt', 'deep', 'deep\\nested', 'deep\\nested\\__pycache__',
  'deep\\nested\\__pycache__\\b.pyc', 'src', 'src\\__pycache__', 'src\\__pycache__\\a.pyc']
结果: clean_pycache() 返回 removed=2
删除后目录清单（4 项）: ['KEEP_ME.txt', 'deep', 'deep\\nested', 'src']
清单差异: 消失的项 = ['deep\\nested\\__pycache__', 'deep\\nested\\__pycache__\\b.pyc',
                     'src\\__pycache__', 'src\\__pycache__\\a.pyc']
EXIT(用例退出码)=0

--- 改后（三重护栏） ---
project_root = C:\Users\fanzi\AppData\Local\Temp\wp1b_pycache_cutg6470\new\misresolved_root
仓根标记检查: .git exists=False  AGENTS.md exists=False
删除前目录清单（8 项）: [同上 8 项]
结果: 抛出 PycacheGuardError: 拒删 __pycache__：project_root=...\new\misresolved_root
      缺 ['.git', 'AGENTS.md'] 任一标记 ⇒ 不可验证为仓根（fail-safe：宁可不删）
删除后目录清单（8 项）: [与删除前逐项相同]
清单差异: 消失的项 = []
EXIT(用例退出码)=42

PASS  改前：临时树里的 __pycache__ 被真删（这就是破坏性地雷的实物面）
PASS  改后：护栏②命中 → 拒删并抛出 PycacheGuardError
PASS  改后：整棵树零删除（清单与删除前逐项相同，fail-safe 只退化为不删）
PROBE_EXIT=0
```

护栏①（越界靶子）与"不吞异常"的通路级红绿对照在 pytest 内（`_pycache_guard_probe.py` 只覆盖②）：
- `test_guard_rejects_targets_resolving_outside_root`：monkeypatch `Path.glob` 产出树外靶子
  ⇒ `PycacheGuardError: ... 之外 ...`，并断言**树内树外一个都没删**（护栏③"先验后删"的可观测面）。
  Windows 端到端 symlink 版需 `SeCreateSymbolicLink` 权限 ⇒ 不写成会 SKIP 的判据，改用 glob 输出等价形态 + 谓词直测。
- `test_rmtree_failure_is_reported_not_swallowed`：注入 `PermissionError` ⇒ 必须抛出（旧行为：`logger.warning` 咽掉后照常返回计数）。

### 2.2 改 1（负向用例：改前空转 / 改后能拦能修对）

仪器：`.runtime/tmp/st-ramp-wp1b-20260919/_redblue_probe.py`——**建库 DDL 逐字照抄活库 `sqlite_master`**，
三种场景各喂 HEAD 版 + 新版（默认 dry_run）+ 新版（显式真写）。

```
$ python .runtime/tmp/st-ramp-wp1b-20260919/_redblue_probe.py    （PROBE_EXIT=0）

S1 活库结构 + details 非 JSON（活库真能非法的面）
  [改前(HEAD)]                tasks_fixed=0 gates_fixed=0 healed=False dry_run=n/a(旧版无此栏) 吞异常=1
                             库内值 前=('COMPLETED','{not json') 后=('COMPLETED','{not json')     ← 空转
  [改后 默认 dry_run=True]    tasks_fixed=0 gates_fixed=1 healed=True  dry_run=True 吞异常=0
                             details=["gate R-1: details 非 JSON -> 列默认值（原值前 120 字符='{not json'）"]
                             库内值 前=后=('COMPLETED','{not json')                                ← 计划不落库
  [改后 dry_run=False,max_rows=10] gates_fixed=1 dry_run=False
                             库内值 前=('COMPLETED','{not json') 后=('COMPLETED','{}')              ← 修对

S2 活库结构 + tasks.status=READY（C-0 地雷现值）
  [改前(HEAD)]  tasks_fixed=1  details=['task T-1: status READY -> FAILED']  库内值 前=('READY',…) 后=('FAILED',…)
                ^^^ C-0 地雷实锤：READY 被静默改成 FAILED
  [改后 两种模式] tasks_fixed=0 gates_fixed=0 healed=False  库内值 前=后=('READY','{}')

S3 旧幻影 fixture 结构 gates(gate_id,result)
  [改前(HEAD)]  gates_fixed=1 details=['gate G-1: result BROKEN -> FAIL'] 库内 BROKEN→FAIL
                ← "假绿"：只在生产不存在的表上"能修"（旧 root:135-148 用例正是这一档）
  [改后 两种模式] 抛出 HealRefusedError: gates 列集与活库实列不符 ⇒ 拒绝自愈（不读幻影列）:
                  no such column: gate_run_id      库内值 前后不变
```

**用例文件级"改前红"的诚实标注**：把 HEAD 版源文件临时放回工作区跑新用例，得到的是
**收集期 `ImportError: cannot import name 'HealRefusedError'`（两文件均 ERROR，2 errors in 1.53s）**——
新符号在旧版不存在，因此"用例改前红"在 pytest 层只能以 ImportError 形式呈现（红但不是断言级红）；
**断言级的改前红/改后绿由上面两支探针承担**（同输入、同库结构、HEAD 副本与工作区版本对拍）。
窗口处置：swap 期间只动工作区不动索引，跑完立即 `git show :<f> > <f>` 还原，
还原后工作区 sha256 == 索引 blob sha256（`07f3bb7ee3cb5bf9…`，逐件核对通过）。

### 2.3 测试实测

```
$ PYTHONPATH=src python -m pytest tests/rollback/test_rollback_verifier_root.py tests/rollback/test_rollback_verifier_unit.py -q
42 passed in 3.06s            （批 1 后 38 → 批 2 后 42）

$ PYTHONPATH=src python -m pytest tests/rollback/ -q
批 1 后：704 passed, 7 xfailed, 2 xpassed in 134.09s
批 2 后：708 passed, 7 xfailed, 2 xpassed in 220.62s
```
（坑记录：`-o cache_dir=…` 与 `-p no:cacheprovider` 都会让本仓 pytest 直接 INTERNALERROR
——前者是未知配置项、后者关掉 `cache_dir` 的注册方，`filterwarnings=error` 升级为异常；
CONSTRUCTION_DISCIPLINE §6 已记前半条，本车道补后半条。）

---

### ③ 验收命令与本次实测输出（含活库 DDL 原文 · D-17）

### 3.1 从**活库**读的 `gates` / `gate_runs` DDL 与 `pragma table_info`（`mode=ro`）

```
$ python .runtime/tmp/st-ramp-wp1b-20260919/_d17_schema_probe.py .      （EXIT=0）

### DB=governance.db  path=data\databases\governance.db  exists=True

--- table 'gates' ---
DDL_SQL_BEGIN
CREATE TABLE "gates" (
                gate_run_id TEXT PRIMARY KEY,
                gate_id TEXT NOT NULL,
                passed INTEGER NOT NULL CHECK(passed IN (0,1)),
                details TEXT NOT NULL DEFAULT '{}',
                artifact_path TEXT,
                session_id TEXT,
                task_id TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
                created_at TEXT NOT NULL
            )
DDL_SQL_END
PRAGMA_TABLE_INFO:
   (0, 'gate_run_id', 'TEXT', 0, None, 1)
   (1, 'gate_id', 'TEXT', 1, None, 0)
   (2, 'passed', 'INTEGER', 1, None, 0)
   (3, 'details', 'TEXT', 1, "'{}'", 0)
   (4, 'artifact_path', 'TEXT', 0, None, 0)
   (5, 'session_id', 'TEXT', 0, None, 0)
   (6, 'task_id', 'TEXT', 0, None, 0)
   (7, 'created_at', 'TEXT', 1, None, 0)
ROWCOUNT=1791

--- table 'gate_runs' ---
CREATE TABLE gate_runs (
    gate_run_id  TEXT PRIMARY KEY,
    gate_id      TEXT NOT NULL,
    passed       INTEGER NOT NULL CHECK(passed IN (0,1)),
    details      TEXT NOT NULL DEFAULT '{}',
    artifact_path TEXT,
    session_id   TEXT,
    task_id      TEXT REFERENCES tasks(task_id) ON DELETE SET NULL,
    created_at   TEXT NOT NULL
)
PRAGMA_TABLE_INFO: 与 gates 逐项相同（8 列同序）    ROWCOUNT=6445
```
⇒ **明确断言（处方要求写清"哪个库的哪张表"）**：本车道改的是
**`data/databases/governance.db` 的 `gates` 表**（不是同名同构的 `gate_runs`，
也不是别的库的同名表：实测 `.runtime/task_board.db` 只有 `tasks`（status 词表是
`pending/claimed/completed` 另一套）、`data/drift_audit/drift_events.db` 只有
`gate_decisions/scan_results`、`.zephyr/rollback_quarantine.db` 只有 `cooldown`——
四库里 `gates`/`gate_runs` 只在 governance.db 存在）。
⇒ **`result` 列的出处经全仓 SQLite 扫描被否证**（`.zephyr/.runtime/data/databases/logs/runtime`
下 2018 个 .db 逐库读 `pragma table_info(gates)`）：唯一带 `gates(gate_id, result)` 结构的库
**全是 tests 的 tmp 产物**（如 `.runtime/tmp/st-ramp-wp1-20260919/bt/test_db_with_invalid_gate_resu0/data/databases/governance.db`），
无任何活库有该列 ⇒ 旧代码的"幻影列"真身就是 R-A4 说的**幻影 fixture 自我印证**，
不是"曾经存在过的另一张活表"（唯一未穷尽面=PostgreSQL depgraph 的 11 列 `gates`，
`auto_runner.py:296,324` 读的是它，含 `event_driven/auto_start/status` 列，与本方法无关）。
⇒ 处方"UPDATE 定位用 `gate_run_id`（`gate_id` 非唯一）"经活库实测成立：
`gates` 1791 行只有 **1008 个 distinct `gate_id`**，而 `gate_run_id` 是 PRIMARY KEY。

### 3.2 活库 `tasks` 关键列（C-0 前提）

```
--- table 'tasks' (governance.db) ---
CREATE TABLE tasks (
        task_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'PENDING',          ← 无 NOT NULL、无 CHECK（源码 _DDL_TASKS 有 10 值 CHECK）
        priority TEXT DEFAULT 'MEDIUM',
        ... (76 列，其余含 namespace/seq/is_deleted 等 9 处 CHECK，均在别的列)
ROWCOUNT=2501
status distribution: COMPLETED=1981  CANCELLED=214  BLOCKED=152  READY=78  IN_PROGRESS=76
tasks 行 status 为空/NULL 计数 = 0
```
对照组（D-17 的多库同名表陷阱，同一次探针）：`.runtime/task_board.db` 的 `tasks.status`
= `TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','claimed','completed'))`——
与 governance.db 完全不同词表，绝不可混用。

### 3.3 生产库上的"改前会计划改多少 / 改后多少"（只读 URI，物理不可写）

```
$ PYTHONPATH=src python -c "…用新代码的 _plan_task_fixes/_plan_gate_fixes 直接吃 mode=ro 连接…"
派生词表(单一真源 _DDL_TASKS): ['BLOCKED','CANCELLED','COMPLETED','FAILED','IN_PROGRESS',
                               'PENDING','READY','RETRY','VERIFIED','WAITING'] n=10
改后计划: tasks=0  gates=0
改前计划(旧 5 值词表): tasks=230   ← 这些行会被静默改成 FAILED
改前误伤明细: Counter({'BLOCKED': 152, 'READY': 78})
```
落地后复核生产分布未变（与 3.2 逐项相等）：`tasks` 五档 1981/214/152/78/76、
`gates` 1791 行 / `sum(passed)=1557` / `json_valid(details)=0` 计数为 0。

### 3.4 门禁自检（写前读判据体，写后复跑尺子）

```
NO-HIGH-COMPLEXITY：新函数 cc 最大 heal_db_consistency=10、_derive_task_status_vocabulary=6，
                    clean_pycache=4，其余 ≤4（用 gate 自己的 _cyclomatic_complexity 实测）  阈值 15 → 通过
CloneGuard（手册给的尺子）：
  CloneGuardOrchestrator(Path('.').resolve()).check(
      ['src/zephyr/infrastructure/rollback/rollback_verifier.py']) → passed=True findings=[]   （两批各跑一次）
NO-BARE-SQL：4 条 SQL 提为模块级 `ast.Assign` 且命名匹配 `^_?SQL_\w+$`（不带 Final，避 §7 互斥坑）
TABLE-NAME-REGISTRY：`gates`/`tasks`/`gate_runs`/`events` 经 TableRegistry.is_registered 实测全 False
                    （注册面 210 个名字皆为 `c*_*.xxx` 式）⇒ 不命中
GATE-ERRCODE-CONSISTENCY：本批未新增任何 error_code（新异常只带消息）⇒ 不涉册
MUTABLE-CONST-WITHOUT-FINAL：新增模块常量全是字符串/整数/tuple/编译正则，无可变容器字面量 ⇒ 不命中
DATETIME-NOW-FORBIDDEN：未引入 datetime.now()/time.time()；用例里的时间戳是字面量
commit 实跑：两批的锁内门禁链均无阻断项（preflight 首跑拦下 3 项：SESSION-REQUIRED、
COMMIT-SCOPE(2 域→按处方加 --allow-multi-domain 留痕)、CAPABILITY-LOOKUP-REQUIRED，逐项治本后通过）
```

---

### ④ 门位项与待裁清单

命中门位：**high 档（改的是门禁/治理自身）**，两批 commit message 首段均为【行为变更声明】。
四类动作（production 流转 / 注册表净删 / flag 出厂翻转 / 资金破坏性操作）**一件未做**；
未改任何门禁判定阈值/flag 出厂默认（`fail_open_register.yaml` 等派生册未手改）；
未删任何文件；未对任何 DB 做 DDL/DML（生产库全程 `mode=ro`）。

| # | 待裁事项 | 我停在哪 / 选了什么 | 交谁 |
|---|---|---|---|
| ④.1 **`fail_open_register` 口径与本需求不匹配** | 生成器只按 `fail[_\-]?open` 词元对 src/scripts 做**静态点名分档**（五轴=file:line/stage/money/trace/hard_permit），没有"该吞点已被改为抛出/已修好"的表达面；若要"登记"就必须往代码里写 `fail_open=True`/`FAIL_OPEN`，而那恰好落进最差档 `hardcoded_default_permit`（= 把修好的东西重新标成硬编码放行）⇒ **按处方取"改为抛出"（fail-closed）**，派生册未手改、也未重跑生成器（本批未新增该词元，重跑只会引入他会话在途漂移）。 | 未自裁口径问题 | Max |
| ④.2 **`max_rows` 上限取多少** | 全仓 grep 无同类"单次自愈行数上限"的现成值（`fix_result_prioritizer.max_affected` 是打分归一，不是护栏）⇒ 无唯一现场来源，**不拍数**：真写（`dry_run=False`）**必须显式传 max_rows**，不传即抛 `HealRefusedError`。如 Max 要一个出厂默认，请给值的来源（裁定/规则册/现成常量），我给不出。 | 停在"由调用方决定" | Max |
| ④.3 **`passed NOT IN (0,1)` 分支在活库 `gates` 上不可达** | 活库实测 `CHECK(passed IN (0,1))` 存在且 1791 行 `typeof(passed)` 全为 `integer` ⇒ 该分支**在真约束下不可达**（处方允许的两种处置里我选第一种的另一半：不伪造非法值，用例的非法面改到活库**真能非法**的 `details`（该列 `TEXT NOT NULL DEFAULT '{}'`、无 CHECK）+ 幻影结构；同时**保留** `passed` 校验作为"活库丢 CHECK 的同类表"的防线——同类漂移本仓已实测发生：`tasks.status` 源码有 CHECK 而活库无）。"该分支退役 / 等 WP16 补约束后再定"属语义判断，未自裁。 | 已按"不伪造非法值"施工，分支去留待裁 | Max（与 WP16 并案） |
| ④.4 **C-0 我做到哪一步** | 只做处方允许的两件：(a) 词表从单一真源 `_DDL_TASKS` 派生（实测 10 值，替换硬编码 5 值）；(b) 真写前 dry-run + 行数上限护栏（默认 `dry_run=True`，超限拒写并抛）。**未**整方法退役（§6.1 涉删代码/改公共 API），**未**给 `heal_db_consistency` 新增任何调用方（R-A2 波2/波3 禁令：本车道也没有让它被链路调起），**未**改 tasks 支路的"脏值→FAILED"修复语义（处方禁止），**未**在生产库上跑过一次真写（RULE-DATA-OPS 三步验证未做 → 见⑥.3）。`dry_run` 默认值取 True 是我按"fail-safe=只退化为不写"选的；若 Max 判"heal 应当默认落库"，翻一个参数默认即可。 | 停在退役与阈值之外的一切 | Max |
| ④.5 **clean_pycache 报错形态：抛出 vs 返回可见对象** | 调用方普查（`git grep clean_pycache` + 逐文件读）：`scripts/rollback.py:138-141` 只调 `g0_verify`；`rollback_boot_integration.py:101-106` 只构造 `RollbackVerifier` 不调方法；`venv_sync.py/warm_standby.py/cross_platform_shell.py` 只在注释/deprecated 文案里提到本类；其余命中全在 `tests/rollback` 两文件 ⇒ **生产调用方 0**，故取抛 `PycacheGuardError`（fail-closed）而不炸穿任何生产路径；root 测试头 `[ERROR_CONTRACT]` 原句"All public methods return dataclass results even on error"已按事实改写（该行本就与 `clean_pycache->int` 不符）。 | 已按实测调用方决定 | — |
| ④.6 **能力反查 0 命中** | 三次 `CapabilityLookup().find(q, session_id='st-ramp-wp1b-20260919')`（rollback_verifier 自愈 / pycache 删除护栏 / 活库 DDL 列名校验）全部 `0 hits`——即"活库列名校验 + 删除护栏"这一能力在能力卡面无条目可复用，属**新建能力面**；是否补 capability 登记（连同 WP2 的触发台账）未自裁。 | 留了审计，未造轮子外的登记 | 总包/Max |
| ④.7 **护栏②的残留面** | 处方逐字用 `.git` 或 `AGENTS.md` 验仓根。残留风险：若 `project_root` 误解析到**另一个含这两个标记的目录**（别的仓 checkout、或仓根父目录恰好放了 AGENTS.md），护栏②会放行、随后只靠①的相对性判定拦（同仓内的 sibling `__pycache__` 会被合法删）。第四护栏"与 `zephyr.shared.io.paths.REPO_ROOT` 真源比对"要不要加属语义判断 ⇒ **未自加**，报裁。旁证（同方案改 3 的取证车道 R-A19/R-A20，本次读到）：`project_root = dirname×N(__file__)` 这类误解析在 HEAD 仍是活体（`drift_detector.py:59` 实测 `_PROJECT_ROOT=D:\ZephyrAlpha\src`），全仓同类派生 137 处/落点异常 23 处 ⇒ 建议与本护栏并案判。 | 未自加第四护栏 | Max |
| ④.8 **台账 R-A4 的一行需补更正** | 台账原句"按处方改成 `passed` 后 `CHECK` 使非法值不可入库 ⇒ 得到一台构造上永不为真的门"：对 `passed` 成立（活库确有 CHECK），但**不成立于 `details`**（活库无 CHECK，真可非法）⇒ 处方不是"只能退役"。建议总包在 §4 事实修正表补一行（我不改 §1 原句）。 | 已在③.1/③.3 给实测原文 | 总包 |

---

### ⑤ 证据等级

`[亲验]`（本车道自己跑的命令与输出）
- 活库 `gates`/`gate_runs`/`tasks` 的 `select sql from sqlite_master` 与 `pragma table_info` 原文（③.1/③.2），含"gates 与 gate_runs 同构（8 列同序）"、`gates` 1791 行 / distinct `gate_id`=1008、`typeof(passed)` 全 integer、`json_valid(details)=0` 的行数=0、`tasks.status` 无 CHECK 且 2501 行分布 1981/214/152/78/76、`.runtime/task_board.db` 与 `.zephyr/rollback_quarantine.db`/`data/drift_audit/drift_events.db` 的同名表列集差异。
- 全仓 SQLite 扫描（2018 个 .db，逐库 `pragma table_info(gates)`）：无任何活库存在 `result` 列，命中 `gates(gate_id,result)` 的库全部是 tests 的 tmp 产物——把"幻影列出处"从猜测变成否证。
- 改 2 红证：HEAD 版真删 2 个 `__pycache__`（返回 removed=2、清单 8→4、EXIT=0）vs 新版拒删并抛 `PycacheGuardError`（清单 8→8、EXIT=42）。
- 改 1 红证：S1 改前 `gates_fixed=0`+吞异常 1 vs 改后 `gates_fixed=1`（dry-run 不落库 / 真写落库为 `{}`）；S2 改前 READY→FAILED 真写 vs 改后 0 改写；S3 改前在幻影表上报 `gates_fixed=1` vs 改后抛 `no such column: gate_run_id`。
- 生产库只读计划普查：改前 230（BLOCKED 152 + READY 78）/ 改后 0；以及落地后分布未变。
- 测试实测：两批 42 例（root 25 + unit 17）与 `tests/rollback/` 708 passed / 7 xfailed / 2 xpassed。
- 门禁尺子：CloneGuard `passed=True findings=[]`、新函数 cc 值、TableRegistry 注册判定、两批的三态 hash 核实、HEAD 副本与工作区版本逐字节相同。
- 调用方普查：`clean_pycache`/`heal_db_consistency` 生产调用方 0（逐文件读 `scripts/rollback.py`、`rollback_boot_integration.py` 等）。
- preflight 被拦三项及其处置（含 `--allow-multi-domain` 为处方 §2.4 明示的"gate+自家测试同批留痕"用法）。

`[转报]`（他人产物，我未复跑）
- 施工台账 R-A19/R-A20 的 `project_root` 误解析普查（137 处 / 23 处异常）与 `drift_detector.py:59` 现值——只读取证车道的结论，我只用于④.7 的旁证，未独立复跑。
- 主区并发/staged 现量与"活跃外部会话 `st-bizmine-*` 高频提交"（我发单时实测 203 件 staged，只数过件数，未核归属）。
- `CONSTRUCTION_DISCIPLINE.md` §7 各门判据口径（我读了判据体，但"仓内既有 295 处同款房规"等计数未复跑）。

`[推断]`
- 新用例的"改前红"在 pytest 层表现为收集期 ImportError（新符号不存在）；断言级红/绿由探针复现，探针里 HEAD 副本与工作区版本对拍逐字节相同 ⇒ 从探针外推到用例层这一跳是推断。
- "生产库结构 = 用例结构"的等价性：结构为真（活库 DDL 逐字照抄），数据为假（tmp 库自建行）；未在真 governance.db 上做过端到端写读（见⑥.3）。
- `_derive_task_status_vocabulary()` 的正则真只读 `_DDL_TASKS` 的 `CHECK(status IN (…))`，实测唯一命中 1 处、10 值全解析；若真源换写法（例如改成引用 YAML）该函数会抛 `HealRefusedError` 而非猜值——这一"未来失效形态"是推断。

---

### ⑥ 未完成的部分与原因（没跑的写成没跑）

1. **改 3（`src/data/drift_audit/drift_events.db`）未做**：任务书明令另一车道在做；我只在 `clean_pycache` 的护栏②docstring 里把它当**成因旁证**引用，未取证、未移除、未删文件。
2. **`fail_open_register` 生成器未重跑**（④.1）：口径不匹配已按处方改走"抛出"；不重跑的原因是派生册是热文件（§0.5 禁手改、重跑会把他人未落地的漂移一起吸进我的批次）。**不是"已核验通过"**。
3. **`heal_db_consistency` 端到端真库写读未做**：在生产 `governance.db` 上执行 `UPDATE` 需 RULE-DATA-OPS 三步验证 + 备份，属另一门位；我只做到"只读连接上算出计划行数(0)"+"tmp 库真写"。等价性标 `[推断]`。
4. **未给 `heal_db_consistency` 接任何调用方，也未退役它**：R-A2 波2/波3 禁令 + §6.1（退役涉删代码）。⇒ 站点一修好的是"一旦有人调它就不再空转"，不是"它已在治理链上跑起来"。
5. **未跑全仓测试**：只跑 `tests/rollback/`（708 例）+ 与两方法调用方的普查；未跑 `python -m zephyr.security.adversarial_validation run`（台账 R-A13 实测其区分度=0，跑了也不构成证据，故不以它冒充护栏）。
6. **`gates.passed` 不可达分支的去留、`max_rows` 出厂默认、护栏②是否加 `REPO_ROOT` 真源比对**：均出案卷未落地（④.2/④.3/④.7）。
7. **`root` 测试里 `TestDifferentialCheck` 自带的 `gates(id,name)` 简化表未改**：`differential_check` 只做 `COUNT(*)`，不涉及列名语义，且处方点名的幻影位是 root:124/140/155 与 unit:56（全部已改到活库真实列）。范围外，未顺手改。
8. **本回执未 promote 到 `docs/_working/`**：新建 tracked .md 需 creation_token（热册正被高频写），任务书要求"能不建就不建"；本文即 `.runtime/tmp/st-ramp-wp1b-20260919/RECEIPT.md`，请总包代持入库。探针/HEAD 副本/两批 commit message 备份同目录：
   `_d17_schema_probe.py`、`d17_schema_output.txt`、`_redblue_probe.py`、`_pycache_guard_probe.py`、`rollback_verifier_HEAD.py`、`msg_batch1_backup.md`、`msg_batch2_backup.md`。
9. **收尾状态**：两批均 `ENQUEUED → done → landed`（`ee54c976f1`、`413edaff0e`），三态核实通过；本车道 4 件 claim 已释放。

### WP11 · `blueprint_registry` 悬空引用处置（`st-ramp-wp11-20260919`）— 堆一落地 `7f68805b98`，堆二 19 处只报

# WP11 回执 · `blueprint_registry.yaml` 悬空引用处置（堆一落地 + 堆二只出案卷）

会话：`st-ramp-wp11-20260919`　分支：`dev`　日期：2026-09-19
处方真源：`docs/_working/2026-09-18-rule-audit-master-construction-plan.md` WP11 施工卡 + 裁定 D-11 / D-14 / D-15 / §0 全局纪律（第 9 条 D-17 附带）
裁定基线复核（本车道独立只读取证，全部实存）：
- commit `03df6215e8` 存在，`git log -1` = "chore(governance): 遗留裁定②blueprint_registry.yaml 派生退库…"，日期 2026-08-18　`[亲验]`
- `#ARCH-BP-REGISTRY-DELETION-001` 在册：`architecture_issue_registry.yaml:10824`，`status: resolved`　`[亲验]`
- 生成器实存：`scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py`（16962 字节）　`[亲验]`
- ROOR 实测：`grep -c "blueprint_registry" docs/registry_of_registries.yaml` = **0** ⇒ 该注册表已无 ROOR 条目　`[亲验]`
- 本批未恢复该文件、未改 `.gitignore`、未改 `rules/**` / `architecture_model/**` / `docs/03_modules/**` / `AGENTS.md`

---

### ① 改动清单 + hash

**落地（堆一，2 件 1 提交）**

| 文件 | 处方条 | 改动 |
|---|---|---|
| `docs/01_policies_and_standards/_registry/catalogs/index.md` | 逐点处方 2 | 删"外部登记表"里的蓝图注册表整行（原 L49） |
| `docs/01_policies_and_standards/templates/blueprint_construction_template.md` | 逐点处方 3（该条列举的 templates 靶） | "需更新的文件"表第 2 行由"手工同步该 YAML"改为 frontmatter → 生成器 链（原 L666） |

**提交归属核实**（`git log -1 --name-only`，`[亲验]`）：

```
7f68805b98ab934f4d92de16c7f156f9e9a5dac6
lane
Sat Sep 19 04:34:16 2026 +0800
docs(wp11): 蓝图注册表悬空引用处置·堆一可写面两件（派生退库后不再被当真源）

docs/01_policies_and_standards/_registry/catalogs/index.md
docs/01_policies_and_standards/templates/blueprint_construction_template.md
```

⇒ 本 commit **只含自家 2 件，零外来内容**。队列凭据：`q-20260919-st-ramp-wp11-20260919-0001`，
`commit_queue.py status --session` 实测 `state=done landed_id=7f68805b98ab934f4d92de16c7f156f9e9a5dac6`，`done=1 dead=0`。

**D-15③ 落地后三态核实**　`[亲验]`

首次核实（**发现隐患并已抹平**）——队列落地只写工作区，index 仍压着改前旧 blob：

| 文件 | `git rev-parse HEAD:<f>` | `git ls-files -s <f>` | `git hash-object <f>` | 判定 |
|---|---|---|---|---|
| catalogs/index.md | `00cf8416be546196f3b4e92209fc5c4de68cd716` | `6bf1b5389a2a51924b6a1640fce27d0372932ae1` ← **改前旧 blob** | `00cf8416be546196f3b4e92209fc5c4de68cd716` | ❌ 不一致 |
| blueprint_construction_template.md | `896cd0f21c634935ec8b206f24ca893747d52f78` | `39aa4a319af68611ac841fe73256f57c8b777413` ← **改前旧 blob** | `896cd0f21c634935ec8b206f24ca893747d52f78` | ❌ 不一致 |

`git status --porcelain` 当时两件均为 `MM` ⇒ 正是本役 R-A17 记的"陈旧快照压 index"第四例的同机制复发（**不是**我造成的写侧蒸发，是队列落地语义）。
按 D-15③ 指示具名 `git add` 抹平后复验　`[亲验]`：

| 文件 | HEAD | INDEX | DISK | 判定 |
|---|---|---|---|---|
| catalogs/index.md | `00cf8416be…` | `00cf8416be…` | `00cf8416be…` | ✅ 三态一致 |
| blueprint_construction_template.md | `896cd0f21c…` | `896cd0f21c…` | `896cd0f21c…` | ✅ 三态一致 |

`git status --porcelain -- <两件>` 终态 = 空（clean）。

**D-15② 热文件"对 dev 纯 insert 零 delete"——本批是处方明令的删除，字面无法成立，改用等价证明**　`[亲验]`

```
$ git diff --numstat dev -- <两件>
0	1	docs/01_policies_and_standards/_registry/catalogs/index.md
1	1	docs/01_policies_and_standards/templates/blueprint_construction_template.md
```
⇒ 字面 `N 0` 对"删一行"的处方不可能成立（那是 A 项删除本身）。等价证明已做：
(a) 动手前两件 `git status --porcelain` 均为空 ⇒ 工作区＝index＝HEAD，非陈旧快照；
(b) 全量 diff 逐字复核：**每件的唯一删除行就是处方点名的那一行**（`git diff` 输出全文已核，
见 ② 与 ③ 的原文），零外来 hunk；(c) 写入走 `safe_write_text` CAS（`expected_base_sha256` 现读现传，
`written=True`），before/after sha 已打印。⇒ 该前置的**目的**（不吃掉上游行）达成，字面不达成，如实记为偏差。

---

### ② 红证

**用了真判据，不是自造 grep**：在册脚本 `scripts/governance/d2_links/audit_broken_links.py`（断链/幽灵引用检测）。

改前（基线，红）　`[亲验]`：
```
$ python scripts/governance/d2_links/audit_broken_links.py \
    docs/01_policies_and_standards/_registry/catalogs/index.md \
    docs/01_policies_and_standards/templates/blueprint_construction_template.md
❌ 发现 5 条断链:
  → 断链: docs/03_modules/blueprint_registry.yaml ← index.md                       ← 靶 A
  → 断链: docs/03_modules/blueprint_registry.yaml ← blueprint_construction_template.md  ← 靶 B
  → 断链: scripts/governance/d5_architecture/validators/validate_path_alignment.py ← blueprint_construction_template.md
  → 断链: tests/xxx.py ← blueprint_construction_template.md
  → 断链: src/zephyr/.../file-name.py ← blueprint_construction_template.md
```
改后（绿）　`[亲验]`：`5 条 → 3 条`，其中 `blueprint_registry` 断链 **2 → 0**，余 3 条为模板占位符与一条与本批无关的存量断链（见"发现 F-4"，只报未改）。

阴性对照（证明这把尺子有区分度，不是恒绿/恒红）　`[亲验]`：
```
$ python .runtime/tmp/st-ramp-wp11-20260919/red_evidence.py
[STATE-0 现状] rc=0 blueprint_registry 断链数=0
[STATE-1 注入后] rc=0 blueprint_registry 断链数=1
   原文: → 断链: docs/03_modules/blueprint_registry.yaml ← index.md
[STATE-2 撤样后] rc=0 blueprint_registry 断链数=0
[VERDICT] 尺子有区分度（红可注、绿可复）= True
```
注入手法＝把已删那行按 CAS 原样注回，跑尺子，再 CAS 撤样；全程不碰 git，跑后 `git status --porcelain` 仍为空。

**退出码面（无法二值化的部分，写实不粉饰）**　`[亲验]`：
```
audit_broken_links.py --ci docs/01_policies_and_standards/_registry/catalogs/index.md   → exit 0（✅ 无断链）
audit_broken_links.py --ci docs/01_policies_and_standards/templates/blueprint_construction_template.md → exit 1
```
⇒ 模板件改前改后**文件级 exit 均为 1**（存量 4→3 条非本批断链），故该件的信号只能取
"blueprint_registry 断链条数 1→0"，不能用文件级退出码。此判据不闭合之处已全部写实。

**可写面 `git grep` 计数对照**　`[亲验]`：处方枚举的文本位上，含 `blueprint_registry` 字面的行数
`docs/01_policies_and_standards/_registry/catalogs/index.md` 1 → **0**；
`docs/01_policies_and_standards/templates/blueprint_construction_template.md`（第 666 行该位）1 → **0**。

---

### ③ 验收命令与本次实测输出

**处方原文命令在本机/本仓不可执行**（如实报，不偷换）　`[亲验]`：
```
$ git grep -n "blueprint_registry" -- ':!*_archive*' ':!docs/03_modules/_cross_layer/*/blueprint.md'
fatal: :\!*_archive*: '\!*_archive*' is outside repository at 'D:/ZephyrAlpha'
EXIT=128
```
单条 `:!` 排除可用、两条 `:!` 并用即 fatal（换第二条内容可复现；`':!docs/03_modules/**'`+`':!*_archive*'` 反而正常）。
⇒ 改用语义等价的 `:(exclude)` 书写，**排除集完全相同**：
```
git grep -n "blueprint_registry" -- ':(exclude)*_archive*' ':(exclude)docs/03_modules/_cross_layer/*/blueprint.md'
```

| 时点 | 命中行数 | 命中件数 |
|---|---|---|
| 基线（动手前） | **383** | **119** |
| 堆一落地后（终态，commit `7f68805b98` 之后） | **381** | **118** |

`diff` 逐行核对，**变化的正是且仅是**处方点名的两行：
```
< docs/01_policies_and_standards/_registry/catalogs/index.md:49:| 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | REG-BLUEPRINT-001 |
< docs/01_policies_and_standards/templates/blueprint_construction_template.md:666:| 2 | 蓝图注册表 | `docs/03_modules/blueprint_registry.yaml` | {新增/修改什么} | {为什么} |
```

**判据的后半句（"剩余命中全部是派生件/生成器语义，无一处再声称 SSoT 或给 file:/// 链接"）本次不能全绿**　`[亲验]`：
```
$ git grep ... | grep "file:///.*blueprint_registry"
docs/03_modules/index.md:91:| [blueprint_registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml) | 蓝图注册表（全项目模块清单·SSoT） | YAML |
```
⇒ 剩余唯一 file:/// 链接命中在 `docs/03_modules/index.md:91`，属堆二禁写面（本役红线"禁写 `docs/03_modules/**`" + 处方逐点第 1 条）。
**该判据要等 Max 落堆二才能全绿；本车道未为了让命令好看而改受保护件。**
另：除 file:/// 外仍有 19 个处方枚举的受保护文本位声称"真源/SSoT"（schema 3 + key_facts 13 + 能力册 2 + 03_modules/index 1），全部在堆二，见 ④。

---

### ④ 堆二"只报未改"清单（逐条可直接粘贴；行号＝本次实测，处方给的号已复验会漂）

> 通用表述口径：**`blueprint.md` frontmatter 是真源 → `sync_registry_from_blueprints.py` 运行时重生派生件 → 派生件不入 git（退库 commit `03df6215e8`）**。
> "WP9 面"＝是否落在 WP9 判决对象（实测案卷面 `dossiers_v2_index.json` 共 1404 件，分布
> `docs/01_policies_and_standards/` 下 rules 1025 / sop 346 / policies 30 / templates 3；下面逐件按该清单判定）。

### S2-1　`docs/03_modules/index.md`　L91（处方第 1 条）｜WP9 面：**否**｜禁写理由：本役红线"禁写 `docs/03_modules/**`"
现原文（逐字）：
```
| [blueprint_registry.yaml](file:///D:/ZephyrAlpha/docs/03_modules/blueprint_registry.yaml) | 蓝图注册表（全项目模块清单·SSoT） | YAML |
```
改后文本（逐字，去 file:/// 与 SSoT 声称；本表其余行链接真存故保留链接）：
```
| `blueprint_registry.yaml`（不入 git） | 蓝图注册表＝**纯派生件**：真源=各 `blueprint.md` frontmatter，由 `scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py` 运行时重生（派生退库 commit `03df6215e8`）；全项目模块清单请读本目录实际 `blueprint.md` 集 | YAML（派生） |
```
（同件 L103 只是 snake_case 命名示例、不含 SSoT 声称，处方未列 ⇒ 不动。）

### S2-2　`architecture_model/layers/schema.yaml`　L3 / L12-15 / L55（处方第 3 条）｜WP9 面：**否**｜禁写理由：`architecture_model/**` 受保护（PROTECTED_PATTERNS 实读 L75 + §6.2）

L3 现原文：
```
# 真源：与 MOD-MASTER-001（CT-* 集成契约）及 docs/03_modules/blueprint_registry.yaml 对齐校验。
```
L3 改后：
```
# 真源：MOD-MASTER-001（CT-* 集成契约，在册实存）。蓝图侧对账对象是派生件 docs/03_modules/blueprint_registry.yaml——
# 不入 git，真源=各 blueprint.md frontmatter，由 sync_registry_from_blueprints.py 运行时重生（派生退库 commit 03df6215e8）；
# 故本行校验前 MUST 先重生派生件，禁把缺失当"真源缺失"。
```

L12-15 现原文（`>` 折叠标量，缩进 2 空格，勿破坏）：
```
id_namespace_note: >
  根树中模块条目 id（小写 slug，如 l02-*）与 docs/03_modules/blueprint_registry.yaml
  的 module_id（MOD-*）属于不同命名空间：slug 用于本层 YAML 内索引；MOD-* 用于蓝图
  跨登记对账。
```
L12-15 改后（逐字，保持折叠标量形状）：
```
id_namespace_note: >
  根树中模块条目 id（小写 slug，如 l02-*）与派生件 docs/03_modules/blueprint_registry.yaml
  （由 blueprint.md frontmatter 经 sync_registry_from_blueprints.py 运行时重生，不入 git）
  的 module_id（MOD-*）属于不同命名空间：slug 用于本层 YAML 内索引；MOD-* 用于蓝图
  跨登记对账。
```

L55 现原文：
```
      description: "可选，对应 blueprint_registry.yaml 顶层 blueprints[] 的 module_id"
```
L55 改后：
```
      description: "可选，对应蓝图派生注册表（blueprint_registry.yaml：frontmatter→生成器运行时重生，不入 git）顶层 blueprints[] 的 module_id"
```

### S2-3　★ 路径更正：`architecture_model/data/rule_optimization/key_facts.yaml` **不存在**；真身＝`data/rule_optimization/key_facts.yaml`
`find architecture_model -iname "key_facts*"` 零命中；`git ls-files | grep key_facts` 唯一命中 = `data/rule_optimization/key_facts.yaml`。
处方给的行号（113-114 / 323-332 / 545-554 / 581）**与真身逐字吻合** ⇒ 只是目录前缀错，内容定位有效。
WP9 面：**否**（案卷面只覆盖 `docs/01_policies_and_standards/`）。
禁写理由：改判后落 `data/`＝生产数据目录（宪法 §9.6 测试禁写生产路径同源红线），且本车道任务书把它列堆二 ⇒ **只报**。

L113-114 现原文：
```
    description: "蓝图数量（blueprint_registry.yaml total_blueprints: 60）"
    ssot_source: "docs/03_modules/blueprint_registry.yaml total_blueprints"
```
L113-114 改后：
```
    description: "蓝图数量（派生件 blueprint_registry.yaml 的 total_blueprints，本次实值 60；该文件不入 git）"
    ssot_source: "docs/03_modules/**/blueprint.md frontmatter -> scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py -> docs/03_modules/blueprint_registry.yaml（纯派生件，不入 git，派生退库 commit 03df6215e8）"
```

L326 现原文：`    ssot_source: "docs/03_modules/blueprint_registry.yaml"`　⇒ 改后同 L114 括号内口径（`… -> … （纯派生件，不入 git，派生退库 commit 03df6215e8）`）。
L548 现原文：与 L326 **逐字同串** ⇒ 同一替换（`git diff` 时须用更长上下文区分，两处不可合并成一次替换）。
L581 现原文：
```
    ssot_source: "docs/03_modules/blueprint_registry.yaml total_blueprints: 60"
```
L581 改后：
```
    ssot_source: "docs/03_modules/**/blueprint.md frontmatter -> sync_registry_from_blueprints.py -> docs/03_modules/blueprint_registry.yaml（派生件）total_blueprints: 60"
```

★ **该文件另有两类缺陷超出 WP11 处方，值需语义判断 ⇒ 不自拟，列待裁**（见发现 F-2/F-3）。

### S2-4　`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`　L160-161（处方第 3 条）｜WP9 面：**否**｜禁写理由：★ 热册（正被他会话高频写）＋ 该册是否生成器产出未查（§0.5 派生册禁手改的前置未排除）
现原文（逐字，L160-162 是一个折叠标量的三行，替换须保持缩进）：
```
  description: 蓝图磁盘路径查询的唯一入口。从 blueprint_registry.yaml（SSoT 派生）按 module_id 查询， 不硬编码路径。真源链：blueprint.md
    frontmatter → sync_registry_from_blueprints.py → blueprint_registry.yaml → load_blueprint_path(module_id)。
    消除连字符/下划线漂移根因。
```
改后文本（只动 L160 括注，其余两行逐字保留）：
```
  description: 蓝图磁盘路径查询的唯一入口。从 blueprint_registry.yaml（纯派生件：不入 git，真源=blueprint.md frontmatter，派生退库 commit 03df6215e8）按 module_id 查询， 不硬编码路径。真源链：blueprint.md
    frontmatter → sync_registry_from_blueprints.py → blueprint_registry.yaml → load_blueprint_path(module_id)。
    消除连字符/下划线漂移根因。
```
落地要求：CAS（`safe_write_text` + 现读 `expected_base_sha256`）**单独一批**，写后立即进程外复验。

### S2-5　处方第 5 条 · `docs/01_policies_and_standards/sop/audit_prompts_20_ai.md` L168 括号 —— **本车道未删，三条独立理由**
现原文（逐字，L168 行首 3 空格）：
```
   ⚠ **`blueprint_registry.yaml` 在本仓不存在**（`docs/03_modules/index.md` 留有一处指向它的悬空链接）。蓝图索引真源=`docs/03_modules/` 实际结构 + 生成器产出；凡见把该文件当真源的条目，一律按锚点漂移记问题清单转总控。
```
改后文本（逐字，S2-1 落地后使用＝删该括号，其余一字不动）：
```
   ⚠ **`blueprint_registry.yaml` 在本仓不存在**（纯派生件：各 blueprint.md frontmatter → sync_registry_from_blueprints.py 运行时重生，不入 git）。蓝图索引真源=`docs/03_modules/` 实际结构 + 生成器产出；凡见把该文件当真源的条目，一律按锚点漂移记问题清单转总控。
```
未删理由　`[亲验]`：
1. 处方原文的条件是 **"上述 1 落地后"**，"上述 1"＝逐点处方第 1 条 `docs/03_modules/index.md:91`，属堆二禁写面 ⇒ 前置未成立（车道任务书把该项归堆一并写"等上面那条落地后"，与处方原文的前置对象不一致 ⇒ 按 §6.6 停手，取更严的一侧）。
2. 该括号目前**为真**：本次实测剩余 file:/// 命中恰为 1 条，就在 `docs/03_modules/index.md:91`。删掉等于抹掉一条准确的在途审计指针。
3. 该文件**在 WP9 判决对象面上**（案卷 18 个小节命中） ⇒ D-14 更强那一层理由（判决对象漂移）适用。
（同件 L325 的 `（本清单不含 blueprint_registry.yaml——该文件在本仓不存在，处置见 8.2。）` 为真且处方未列 ⇒ 不动。）

### S2-6　处方第 4 条 · 历史 changelog **不动**（改＝伪造历史）；按行号重定位后的实测位｜WP9 面：均为 blueprint 文档，非案卷面对象
- `docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md`：**L656、L936、L1011、L1064**（处方只列 656/1011；936/1064 是同件同类"同步更新/派生"表述，实测新增）
- `docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md`：**L716、L909、L1045、L1223**（处方只列 716）
- `docs/03_modules/_cross_layer/context_engine/blueprint.md`：**L125 含真实 file:/// 链接**（指向已退库的该 YAML），另有 L141/L142 把它当对齐对象 ⇒ 处方未列、且被验收排除式 `'_cross_layer/*/blueprint.md'` 整体屏蔽（见发现 F-5）
⇒ 三件全部**未改**，只登记。

---

### ⑤ 逐项证据等级

| 断言 | 等级 |
|---|---|
| 两件的改前/改后文本、CAS `written=True`、before/after sha | `[亲验]` |
| commit `7f68805b98` 归属（`git log -1 --name-only` 只见自家 2 件） | `[亲验]` |
| D-15③ 三态：首轮 index 压旧 blob → 具名 `git add` 抹平 → 三态一致 | `[亲验]` |
| 红证（audit_broken_links 5→3、blueprint 断链 2→0、注入-撤样双向、`--ci` 退出码 0/1） | `[亲验]` |
| 验收 grep 基线 383/119 与终态 381/118、变化的恰为两行 | `[亲验]` |
| 处方原文命令 exit 128（两条 `:!` 并用即 fatal） | `[亲验]` |
| D-11 取证链（`03df6215e8` / `#ARCH-BP-REGISTRY-DELETION-001` status=resolved / 生成器实存 / ROOR 零命中） | `[亲验]`（D-11 结论本身＝`[转报]` Max 已封口） |
| `key_facts.yaml` 路径不存在 + 真身在 `data/` + 行号吻合 | `[亲验]` |
| key_facts 的 `must_not_appear_as` 自相矛盾、`must_appear_in` 不可满足 | `[亲验]`（读到原文与零命中实测） |
| WP9 判决对象面分布（1404 = rules1025/sop346/policies30/templates3） | `[亲验]`（读 `dossiers_v2_index.json`） |
| 处方第 5 条前置不成立（S2-1 未落地 ⇒ 括号仍为真） | `[亲验]` + 条件式为`[推断]` |
| 堆二各替换文本"落地后能过断链/悬空门" | `[推断]`——本车道未在受保护件上试落 |
| `#231` 在册性（本回执正文未引用该号，仅 D-11 原文引用） | `[转报]`——另见 `docs/03_modules/index.md:94` 字面"裁定#231"存在，未回查 ruling_registry |

---

### ⑥ 未完成部分与原因（禁把"没跑"写成"通过"）

1. **验收判据未全绿**——只完成堆一（2 件），堆二 19 个处方枚举文本位未动（受保护/热册/`data/` 生产面）。已给全量可粘贴文本（④）。**该判据需 Max 落堆二后才能全绿。**
2. **处方第 5 条（S2-5）未执行**——前置未成立，三条理由见④；已给替换文本待与 S2-1 同批落地。
3. **D-15② 字面不达成**——"纯 insert 零 delete"对处方明令的删除不可能成立，改用等价证明（①）。
4. **处方原文验收命令不可执行**——本环境 `git grep` 两条 `:!` 并用 fatal（exit 128），改用同排除集的 `:(exclude)` 写法。

### 附：本车道新发现（全部只报未改，交 Max；不含越权处置）

- **F-1｜处方路径不存在**：`architecture_model/data/rule_optimization/key_facts.yaml` 无此件，真身 `data/rule_optimization/key_facts.yaml`。⇒ 归入台账 §4 事实修正表素材（与前役"案卷路径写错"同族）。
- **F-2｜`key_facts.yaml` 两条"命名"事实自相矛盾**：L323-332 与 L545-554 的 `fact` 与 `must_not_appear_as.pattern` **是同一个串**（`blueprint_registry.yaml`），且 `reason` 写"连字符写法错误，实际文件名用下划线 blueprint_registry.yaml"——被判"错误"的 pattern 就是被推荐的正确写法。成因疑似历次把连字符变体全量 sed 成下划线时把 pattern 一起改了。⇒ 任何按此册跑的校验会把**正确写法判成违规**。修法需语义判断，未自拟。
- **F-3｜派生退库留下不可满足断言**：`key_facts.yaml` 三条 `must_appear_in` 指向 ROOR（L550）/ `docs/registry_of_registries.yaml`（L583）/ `.trae/rules/project_rules.md`（L116、L328），实测 **ROOR 命中 0、project_rules 命中 0** ⇒ 这些"必须出现"永假。另 `data/rule_optimization/key_facts.yaml` 的在册消费者**只找到一个**：`scripts/governance/_archive/one_off/check_rule_coverage.py`（归档 one-off）⇒ 该册可能是僵尸台账（交 Max 判 D3/D4）。
- **F-4｜处方与验收判据不闭合**：处方只列 7 个靶，但 `--ci` 尺子在同目录另有存量断链（`scripts/governance/d5_architecture/validators/validate_path_alignment.py` 已不存在于该路径）；模板占位符 `tests/xxx.py` / `src/zephyr/.../file-name.py` 亦常驻红。⇒ 若某门禁以 `audit_broken_links --ci` 硬阻断模板文件，本批改前改后都是红，判据无法二值化。
- **F-5｜验收排除式把一条真 file:/// 链接屏蔽掉**：`':!docs/03_modules/_cross_layer/*/blueprint.md'` 按"历史 changelog"意图写，但同时屏蔽了 `context_engine/blueprint.md:125` 的**活体 file:/// 链接**（非 changelog 行）。⇒ 建议 Max 把排除式收窄到具体行/具体锚，或把该行并入 S2-6 之外的处置项。
- **F-6｜处方未枚举但同类缺陷另 4 处**（均为"声称该 YAML 是真源"）：
  `scripts/governance/d7_code/fix_n13_snake_case.py:22`（"删除 1 个遗留存根 blueprint_registry.yaml（真源为 blueprint_registry.yaml）"——自指矛盾，且该件在可写路径）、
  `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml:942,950`（`- 真源：blueprint_registry.yaml`；10784/10815 属历史裁定文字不动）、
  `tests/gate/test_sys_master_compliance.py:69`（注释"从 blueprint_registry.yaml SSoT 查询"）、
  `docs/03_modules/_domain_factor/blueprint.md:387` 与 `_domain_signal/blueprint.md:335`（"不进入 blueprint_registry"）。
  ⇒ 未动（禁"顺手优化" + 热册 + 历史裁定文本），列此供 Max 决定是否扩方。
- **F-7｜`docs/01_policies_and_standards/_registry/catalogs/index.md` 的"外部登记表"表头未动**：删掉蓝图行后该表仅剩 2 行且仍声明"registry_id 以 ROOR 为准"，与本件历史约定（d37a8b1f61）一致 ⇒ 无需追加说明；若 Max 希望留一条"已退库"注记，可粘贴：`（原"蓝图注册表 REG-BLUEPRINT-001"行已删：ROOR 查无该 id，该 YAML 系派生退库件，见 commit 03df6215e8）`。

### 冷启动/纪律自查
- RULE-ENV：`python --version` = **Python 3.12.8**（本 shell 实测，未出现 3.10 注入）　`[亲验]`
- RULE-GUARDIAN：`Get-ScheduledTask -TaskName '*reaper*'` → `ZephyrAlpha_ProcessReaper  State=Ready`；`python -m zephyr.trading.process_reaper --status` 正常输出（scanned=10 killed=4）　`[亲验]`
- RULE-WORKTREE：主区具名 + `--enqueue`（D-15 合规正门），未直连提交；改前两件 `--porcelain` 均为空，改前 `lock_files.py acquire` 两件、提交后自动释放（实测 `release` 报 NOT FOUND＝已由网关释放）　`[亲验]`
- 未碰：`AGENTS.md` / `architecture_model/**` / `rules/**` / `docs/03_modules/**` / `.gitignore` / `capability_canonical_file_registry.yaml` / `.runtime/sessions/**/staging/**` / `reconciliation_registry.py` / `rollback_verifier.py` / `ch_reader.py` / `flowthrough_verifier.py` / `src/zephyr/pf_alloc/**` / `_registry.yaml`　`[亲验]`
- 未跑 `capability_lookup` / `rule_discovery` 留审计（本批为文档改动，处方即真源）；未跑 `apply_depgraph --add-design-node`（无新增设计节点）⇒ 记为**未做**，非"通过"。
- 本车道工作物：`.runtime/tmp/st-ramp-wp11-20260919/{apply_stack1.py, red_evidence.py, msg.md, RECEIPT.md}`（有 24h TTL ⇒ 已同步冷库）。
- 冷库镜像：`G:/zephyr_cold/30_corpus/rule_audit_v1_20260919/wp11/`（同 4 件）。首版 sha256 双份核对
  `6fd8307ad5ae3059dd76640c5a1ec7278f798d3fcbc1cccec96b622a837df3b3`（`.runtime` 与冷库逐字节相同；本文件其后又补了 RULE-ENV/GUARDIAN 两行实测值，故以最终版重刷镜像并复核一致）　`[亲验]`
