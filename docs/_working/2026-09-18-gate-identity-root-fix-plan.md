---
ttl: task_bound
title: 门禁身份与触发台账治本施工方案（闸0 · B′ 方案 · 交施工队执行）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-18
topic: gate_identity_root_fix
scope: global
session: st-ruledisp-20260918
---

# 门禁身份与触发台账治本施工方案（B′）

> **交给谁**：主施工队（大规模施工会话）。本方案由 `st-ruledisp-20260918` 会话完成只读普查后产出，**未动任何代码**。
> **法条**：判决流程一律按 `docs/01_policies_and_standards/sop/review_sop/rule_disposition_policy.md`（六道闸 × 六类归宿）。本方案是该程序法"闸 0 身份闸"的施工落地。
> **执行前提**：主区当前有他会话在途 staged 内容，**禁止从主区提交**；一律隔离 worktree + GitCommitGateway（并发窗口走 `--enqueue` 队列正门）。

## 0. 裁定结论（Owner 已批：一律取治本）

### 0.1 方案 A 不治本，方案 B 需升级为 B′

**A（统一命名）为什么不是治本**——反证：假设今晚就把 169 台提交门禁、91 条引擎门禁、63 个 reconciler 改成一套命名，明天照样发生：

| 现存缺陷 | 改名能否治好 |
|---|---|
| `rollback_verifier.py` 读不存在的列 → 门禁面校验空转 | 不能 |
| `gate_persistence.py` INSERT 列名不符 → 决策永不落库 | 不能 |
| 962 条条文声明的强制体全仓零命中（悬空强制） | 不能 |
| 册内 entry 命令与 `.pre-commit-config.yaml` 实参不一致（21 条） | 不能 |
| `risk_tier_registry` 对规则面失明（1401/1404 案卷 domain 未登记） | 不能 |

改名只让查询方便一点，而"查不方便"是症状不是病。**A 还会制造假的 1:1**——提交门禁 / 规则条款 / reconciler 是三类不同对象（一个门禁可强制多条规则，一条规则可有多个强制体），塞进同一命名空间等于把语义抹掉。

**B（映射视图）方向对但不够**：视图自己也会漂。活证据 = `src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml`，它曾是与引擎同步的册子，`last_updated` 停在 2026-06-22、`summary.total: 93` 而实际 91 条。

**B′ = 把"声明面 ↔ 执行面 ↔ 运行面"的三面一致性做成提交时门禁，而不是事后视图。**
一句话：**让不一致无法被提交进来**。核心构件就是你已批准新增的那台"规则↔门禁对账门"——它不是附加品，是 B′ 的心脏。

### 0.2 第 2–5 项的治本选择

| # | 事项 | 治本选择（本方案采用） | 治标做法（明确不采用） |
|---|---|---|---|
| 2 | 改门禁执行链写入端 | **改**。含修好两个坏写入端；提交门禁每次执行落库（**放行也记**）；条款级记录带 `rule_id + section_key` | 只建视图、不修写入端 |
| 3 | DB 死数据 | **顺序＝先修/停写入端 → 再声明表退役 → 最后才清理行**。写入端不停，删完还会长回来 | 直接 DELETE 行 |
| 4 | 第四册异常 | **接生成器**：计数派生、`status` 走受控词表、`last_updated` 由生成器写 | 把 93 手改成 91 |
| 5 | `gate_id='-'` 未归因 | **写入端强制归因**：拿不到 gate_id 即拒写并告警 | 事后批量补标 |

## 1. 普查实测（分母，全部现场可复跑）

### 1.1 五个身份面

| 面 | 载体 | distinct | 时间窗 | 判定 |
|---|---|---|---|---|
| 提交门禁册 | `_registry/catalogs/gate_registry.yaml` | 169（`source`: pre-commit 55 / commit-gate 113 / manual 1） | 机生 `generated_at` 2026-09-16 | 活 |
| 进程内门禁册 | `_registry/catalogs/in_process_gate_registry.yaml` | 113 | — | 活，**是上者真子集**（overlap=113） |
| 规则引擎册 | `src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml` | 91（`summary.total` 写 93） | `last_updated` 2026-06-22 | **疑停更 + 计数漂移** |
| 条款级运行记录 | `governance.db`：`gates` / `gate_runs` | 1008 / 645 | `gates` 2026-06-21→06-29；`gate_runs` 07-03→09-15 | 一死一停更 |
| reconciler 台账 | `governance.db`：`reconcile_execution_log` | 63（77,018 行） | 2026-08-11→今 | **唯一健康活台账** |

第六面（普查中补获）：`governance.db` `rule_enforcement_log` — 36 行、**1 个 distinct rule_id**、结果全 `PASS`、窗口 2026-06-13→07-27 → 退化残留，写入端 `src/zephyr/shared/database/database_crud_mixin.py:123`。

两两交集：YAML∩gates=0 · YAML∩gate_runs=0 · YAML∩reconcile=3 · reconciler规格(49)∩reconcile台账(63)=31 · gate_runs∩reconcile=0。

### 1.2 触发记录载体（决定退役审计能否跑）

| 对象 | 唯一载体 | 窗口 | 致命限制 |
|---|---|---|---|
| 提交门禁 169 台 | `.runtime/audit/commit_block_events.jsonl`（1375 行、68 distinct、234 条 `gate_id='-'`） | 仅 2026-09-13→今 | gitignore = 易失；**只记拦截不记放行**（无分母）；未归因 234 条 |
| 规则条款 | `db.gate_runs` | 07-03→09-15 | 已停更；条款 id（`G0:CP-9007`/`G_TRAE_003:DM-100001`）**全仓代码与规则零命中** = 运行时合成，无法回指规则小节 |
| reconciler | `db.reconcile_execution_log` | 08-11→今 | 健康 |
| 聚合统计 | `.runtime/audit/gate_execution_stats.jsonl` | 09-15→今 | **无 gate_id 字段**，给不出按台触发率 |

**结论**：90 天零触发退役判定，当前对 169 台提交门禁**完全不可算**。

### 1.3 已定位的坏写入端（治本的起点）

| 位置 | 症状 | 证据 |
|---|---|---|
| `src/zephyr/infrastructure/rollback/rollback_verifier.py:191-198` | 读 `gate["result"]`，而 `gates` 实表列为 `gate_run_id/gate_id/passed/details/artifact_path/session_id/task_id/created_at`——**无 result 列**；异常被内层 try 吞掉 → 门禁面校验**空转** | 实表列取自 `governance.db` information_schema；DDL 见 `src/zephyr/governance/persistence/sqlite_schema.py:952` |
| `src/zephyr/gov_drift/gate_persistence.py:210-219` | `INSERT INTO gate_decisions(module_id, gate, decision, detail, decided_at)`，实表列为 `decision_id/gate_id/decision/reason/decided_at/decided_by` → **每次调用必失败**，故该表停在 2026-07-27（35 行、1 个身份） | DDL 见 `sqlite_schema.py:850` |

其余写入端（活）：`src/zephyr/gov_enforcement/commit_gates/gate_repo.py:93`（INSERT INTO gate_runs）、`scripts/governance/meta/gate_engine_selfcheck.py:176`、`scripts/governance/meta/validate_gate_engine_external.py:197`、`scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py:598`（INSERT INTO gates）。

### 1.4 一个必须澄清的假警报（否则会误删）

Flash 案卷面报"133 条册内门禁在 `.pre-commit-config.yaml` 无同名 hook"。**按 `source` 字段分档后真实漂移只有 2 条**：

| source | 条目 | 在 pre-commit 找不到同名 hook | 解释 |
|---|---|---|---|
| `pre-commit` | 55 | **2** | 真漂移，须修 |
| `commit-gate` | 113 | 108 | **正常**——进程内门禁本来就没有 pre-commit hook |
| `manual` | 1 | 1 | 待核 |

**禁止**按 133 这个数去"补齐 hook"或删条目，那会破坏 108 台进程内门禁的登记。

### 1.5 可机械推导的映射（好消息）

- `trae_nnn` ↔ 引擎册 `G_TRAE_nnn`：49 条 `G_TRAE_*` 身份，**49/49 全部对上 `rules/trae_nnn_*.yaml`**。
- 规则 → 提交门禁：`rules/trae_*.yaml` 的 `enforcement.paired_gate_id`，**56/86 可解析到两册**（29 条未声明、1 条悬空 = `TRAE-079` 声称 `COMMIT-CRITICAL-SECTION-LOCK`，两册零命中且执行体不存在）。
- 引擎册 `file` 字段：81/81 实存（相对注册表目录解析）。
- **推导不出的一段**：条款级 id 后缀（`DM-*`/`CP-*`/`SRC-*`/`STD-*`）↔ 规则小节键（如 `gov_eng_002`）。全仓零命中 → 必须由写入端在记录时同时落 section key（WP3）。

## 2. 工作包（WP1–WP7）

> 每个 WP 都必须满足：① 隔离 worktree 施工；② 有红证（改前先证明检查器会红，改后证明变绿）；③ 热文件走 `safe_write_text` CAS；④ 命中门位四类的动作先登记待裁不自裁。

### WP1 · 修好两个坏写入端（最高优先，其他 WP 的证据源）
- **改**：`rollback_verifier.py:191-198` 按实表列名重写（`passed` 而非 `result`；`UPDATE` 用 `gate_run_id` 而非 `gate_id`，后者非唯一）；内层 `except` 不得静默吞——按 `fail_open_register` 五轴口径登记或改为抛出。
- **改**：`gate_persistence.py:210-219` 的 INSERT 列名对齐实表（`gate_id/decision/reason/decided_at/decided_by`），并补 `decided_by` 来源。
- **验收**：各写一个负向用例（故意给错列名/坏值）证明**改前会失败、改后会拦**；再跑一次真实调用，`db.gate_decisions` 行数增加且 `decided_at` 为当前时间。
- **门位**：改的是门禁/治理自身 → high 档。**不涉及**四类动作（非净删、非 flag 翻转、非 production 流转、非资金），可施工，但 commit message 须声明行为变更。

### WP2 · 提交门禁持久触发台账（治本核心）
- **新建**：`governance.db` 一张 `gate_trigger_log`（或复用 `gate_runs` 并统一身份口径），列至少含 `gate_id`（**必须是册内身份**）、`passed`（**放行也记**）、`session_id`、`ts`、`trigger_source`。保留期 ≥ 90 天，超期由既有清理机制按 TTL 收敛（禁新建常驻守护；OS 托管 one-shot）。
- **改**：提交门禁执行链在每次判定后落一条记录；`.runtime/audit/commit_block_events.jsonl` 保留为易失快查面，但**不再是唯一载体**。
- **强制归因**：拿不到 `gate_id` 时拒写并告警（治本项 5），杜绝 `'-'`。
- **验收**：连续两次提交后，`select gate_id,passed,count(*) from <表> where ts>now()-interval 1 hour group by 1,2` 能同时看到 `passed=true` 与 `false` 的行；故意注入一个违规提交，能查到对应 `gate_id` 的 `passed=false`（红证）。
- **门位**：改门禁执行链写入端 = **门禁自身**，high 档。Owner 已批（裁定项 2）。

### WP3 · 条款级运行记录带上规则身份
- **改**：规则引擎写 `gate_runs`（`gate_repo.py:93` 及两个 selfcheck/validate 脚本）时，除条款级 id 外**必须同时落 `rule_id` 与 `section_key`**。
- **理由**：现在条款 id 是运行时合成、全仓零命中，导致"哪条规则的哪一小节被触发过"永久不可查（§1.5 最后一条）。
- **验收**：跑一次引擎评估，新行的 `rule_id` 能在 `rules/trae_*.yaml` 里查到、`section_key` 能在该文件 `sections` 键里查到（100% 命中，否则红）。

### WP4 · 规则↔门禁对账门（新增门禁，B′ 的心脏）
- **新建**：一台 own-scope 提交门禁，判据（全部二值）：
  1. 规则 YAML 的 `enforcement.paired_gate_id` 若非空 → 必须在两册之一可解析；
  2. `enforcement.executors` 每项必须落入四类之一：仓内实存文件/模块、登记过的外部工具、登记过的人工流程、MCP 服务名；**四类之外即阻断**；
  3. 规则小节若声明"由门禁强制" → 该 gate_id 必须在册且 `status: active`；
  4. `gate_registry` 中 `source: pre-commit` 的条目 → 必须在 `.pre-commit-config.yaml` 有同名 hook，且 entry 命令实参与 hook 实参一致（当前 2 条漂移 + 21 条旗标不一致由此收敛）；
  5. 第四册 `summary.total` 必须等于 `gates` 条目数（当前 93≠91）。
- **作用域**：own-scope（只判本次改动涉及的规则/册条目），避免存量 962 条悬空强制一次性堵死所有提交。**存量清理走 WP6，不靠这台门硬扛。**
- **fail 方向**：fail-closed（门禁自身，high 档）。
- **净零增长对价（宪法 §4.1）**：新增 1 台，须合并同族门腾名额。候选：`GATE-NAMING`/`GATE-NAMING-AUDIT`、`GATE-FRONTMATTER`/`GATE-FRONTMATTER-AUDIT`、`GATE-ERRCODE`/`GATE-ERRCODE-CONSISTENCY` 三对"增量版+审计版"，各合并为单门双模式（`--mode incremental|audit`），可释放 3 个名额。**合并前须核实二者职责确为同族两模式**，若扫描面语义不同则不得合并，改用退役零触发门抵账。

### WP5 · 第四册接生成器
- **改**：`src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml` 由生成器产出（从 `g1..g6` stage YAML + `rules/` 反推），`summary.total` 与 `by_category` 派生计算，`last_updated` 由生成器写；`status` 取值走受控词表（当前混用 `active` 86 / `implemented` 4 / `draft` 1 —— `implemented` 与 `active` 是否同义须先裁词表）。
- **验收**：连跑两次生成器字节一致（幂等）；手改 `summary.total` 后重跑即被覆盖（证明是派生面）。
- **门位**：生成器新增 = B/C 类，须登记 capability + creation_token + ARCH 条目（三连带）。

### WP6 · 存量悬空强制清理（962 条）
- **依据**：案卷面 `_runtime/.../staging/dossiers_index.json`（1404 份案卷）+ 取证二分 `_tools/forensics.json`。
- **已取证**：27 个执行体名**实现面历史零命中**（从来没有过），含 `session_worktree_*` 一族 9 个、`capability_lookup_*` 一族 3 个、`commit_gate_*` 一族 3 个、`static_scan_*` 2 个等；2 个**曾经有过**（`validate_phase_transition.py`、`score_architecture.py`）；`COMMIT-CRITICAL-SECTION-LOCK` 全历史命中 1 次。
- **处置**：按程序法闸 1 二分——"曾经有过"→ 出口 B（改指向）；"从来没有过"→ 出口 D4（判无效 + salvage 取证 + **上报登记流程缺陷**）。
- **批量纪律**：一次一个规则文件族，改完即 `git add`；**禁止**一批 962 条全仓扫改（会与他人施工连坐，且无法复核）。
- **门位**：涉及注册表净删行者逐条登记待裁。

### WP7 · risk_tier 对规则面失明
- **症状**：1401/1404 案卷的 domain 未登记于 `risk_tier_registry.yaml`（规则文件 domain 一律 `TRAE` 或空，册内 18 个域键无此项）→ "应然退化方向"恒为未规定 → 程序法闸 4 第 3 问**结构性失明**（案卷面 `退化方向不符数=0` 是失明不是清白）。
- **治本**：给规则文件补 `domain` 到 `functional_domain_registry` 的 `D_*` 键（或在 `risk_tier_registry` 增设规则面档位），使闸 4 可判。
- **验收**：重跑案卷生成，`退化方向可判分母` > 0 且 `退化方向不符数` 允许非零（**从 0 变成非零才是修好了**——这是本 WP 的红证）。

## 3. 执行顺序与依赖

```
WP1（修坏写入端）──┐
                   ├─→ WP2（触发台账）──→ WP3（条款身份）──┐
WP5（第四册生成器）─┘                                        ├─→ WP4（对账门）──→ WP6（存量清理）
WP7（risk_tier 补域）───────────────────────────────────────┘
```
- WP1 必须最先：它是 WP2/WP3 的证据源，且现在每跑一次都在静默失败。
- WP4 依赖 WP2/WP3/WP5：对账门要拿台账与派生册当输入，否则会退化成又一个静态清单。
- WP6 最后：存量清理必须在对账门上线后做，否则清完还会再长出来（**先装纱窗再扫地**）。
- WP7 可与任何 WP 并行。

## 4. 禁止事项（施工队必读）

1. **禁止**按"133 条无 hook"去补齐或删除——真实漂移 2 条，其余 108 条是进程内门禁的正常形态（§1.4）。
2. **禁止**手改任何派生册（`gate_registry.yaml`、`fail_open_register.yaml`、第四册改造后）——一律重跑生成器（宪法 §9.5）。
3. **禁止**直接 DELETE 死表行——顺序必须是"停/修写入端 → 声明退役 → 才清理"（裁定项 3）。
4. **禁止**从主区提交——主区有他会话在途 staged；一律 worktree + Gateway，并发窗口走 `--enqueue`。
5. **禁止**把"检查器没报错"当通过——每个 WP 的验收都必须先出红证（程序法 0.3）。
6. **禁止**新增常驻守护进程来维护台账保留期——用 OS 托管 one-shot（程序法 §2.4A 信号②）。

## 5. 交付回执格式（施工队回给 Owner / 总控）

每个 WP 一段，含：
1. 改动文件清单 + commit hash（`git log -1 --name-only` 核实归属）；
2. **红证**：改前注入什么、看到什么红、撤样后什么绿（命令 + 退出码原文）；
3. 验收命令与实测输出；
4. 命中的门位项与待裁清单（若有）；
5. 证据等级标注（`[亲验]`/`[转报]`/`[推断]`）；
6. 未做完的部分与原因（禁止半拉子收尾）。

## 6. 本方案的误差声明

- `[亲验]`：五个身份面的 distinct/窗口/交集、两个坏写入端的列名不符、`source` 分档后的 2 条真漂移、49/49 与 56/86 映射率、81/81 file 实存、`rule_enforcement_log` 36 行全 PASS。
- `[转报]`：1404 份案卷的各闸计数（962 悬空 / 948 多真源 / 475 无红证 / 32 不可二值判定 / 15 扫描面不符）出自 Flash 档案卷面，产物在 `.runtime/sessions/st-ruledisp-20260918/staging/`，**施工前须复跑其 `_tools` 采集器确认**（该会话自报扫描面在跑动中自增：md 文件 43→44、条款 377→379，因程序法文件本身落入被审面）。
- `[推断]`：`gates`/`gate_decisions` 判"死表"依据是最后写入时间 + 写入端坏损，未穷尽所有调用路径；WP1 施工时须先确认调用方是否仍存在。
- 本方案产出会话自身在本轮产生过 1 次假阳性（第四册 81 个 `file` 指针初判"全悬空"，实为相对目录解析后全部实存），已推翻修正。
