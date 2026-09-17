---
ttl: task_bound
title: T1-β 节点挖矿：注册表与提交门禁自欺骗检测（默认关 / 无输入 / 作用域口径）
session: st-qoder-mining-20260917
date: 2026-09-17
parent: S11_assembled_backtest
lane: J
---

# 节点挖矿：门禁自欺骗（父环节 S11_assembled_backtest）

> 范围：`gate_registry.yaml` 宣称的 169 条门禁里，**哪些实际不会触发**（默认关 / 触发面为空 /
> 脚本无入口 / 输入件缺席），以及"own-diff 作用域"与"宣称全仓扫描"的口径落差。
> 方法：AST 级普查（不用 substring 判接线）+ 在 HEAD(451e0fc8ea) 逐条实跑记 findings 数。
> 探测件（只读）：`.runtime/tmp/mining_gates_20260918/{probe_gates,probe_scope,probe_exec,probe_run}.py`
> → `gate_flags.json` / `gate_noinput.json` / `commit_gate_scope.json` / `gate_executability.json` / `gate_head_run.json`。
> 方法论前提（本仓史）：派生件 `blueprint_registry.yaml` 已退库且**盘上也不存在**，
> 吃它的检测维度永远 0 输入——本文把这一族逐个查清。

## 1 现状盘点（宣称 → 验真/验伪）

### 1.1 注册表自身账面

实测 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`：

| 字段 | 实测 |
|---|---|
| `total_gates` | 169 = 实际条目 169 ✅ 一致 |
| `generated_at` | `'2026-09-16T14:22:32Z'` |
| `source` | commit-gate 113 / pre-commit 55 / manual 1 |
| `status` | active 168 / deprecated 1 |
| `severity` / `enforce` | **两条字段在全部 169 条里均为 None**（注册表不携带阻断强度信息） |
| `always_run` | True ×1，False ×168 |
| `files_trigger` | **122 条为空**（113 条 in-process 门禁的 trigger 由生成器硬写空：`generate_gate_registry.py:145-146` 注释"触发逻辑在闭包内…无法从文本可靠提取"） |
| `own_scope` | True 26 / False 87 / **字段缺失 56**（缺失的正是 55 条 pre-commit + 1 条 manual） |
| `entry` 目标脚本存在性 | 53 条 script 型门禁，**缺文件 0**，存在但未跟踪 0 ✅ |

真实执行面：`.pre-commit-config.yaml` 68 个 hook（全 `repo: local`）+ `commit_gates/` 117 个模块（`*.py` 去 `__init__.py`）
（113 已注册 + 4 个非门禁 helper：`_reference_helpers.py` / `_diff_helpers.py` / `capability_lookup_bypass_policy.py` / `gate_repo.py`；113+4=117 闭合）。

### 1.2 【验伪】两条"已转硬阻断"的门禁，脚本根本没有入口——运行=空操作

`.pre-commit-config.yaml` 头部过渡计划原文（`:19,21`）：
"GATE-13 (蓝图重叠检测) → ✅ 已转硬阻断（args --ci）"、"GATE-14 (AI权限注册表) → ✅ 已转硬阻断（args --ci）"。

AST 实测（`gate_executability.json`，53 条 script 型门禁中仅 3 条无 `__main__`，其中 2 条即此二者）：

| 门禁 | 脚本 | 实测 |
|---|---|---|
| GATE-13 | `scripts/governance/d11_compliance/validate_blueprint_overlap.py`（108 行） | **无 `__main__`、无 argparse**。`return [], 0` 在 `:102`（`run_validation` 的早退分支），末句是 `:108 return overlaps, len(component_map)`——两句都在没人调用的 `run_validation()` 体内。`python … --ci` → rc=0、**0 行输出**（实测 `gate_head_run.json`） |
| GATE-14 | `scripts/governance/d5_architecture/validators/validate_authority_registry.py`（173 行） | 同上：无 `__main__`。`--ci` → rc=0、0 行输出 |

即：注册表 `status: active` + 配置头"已转硬阻断" + 实测 rc=0 三重口径下，这两条门禁
**对任何输入都不会失败**——因为 `run_validation()` 从未被调用。

### 1.3 【验伪】两条门禁的触发面与输入面同时不存在

| 门禁 | hook `files:`（决定何时触发） | 脚本实际读的输入 | 实测存在性 |
|---|---|---|---|
| GATE-14 | `^docs/01_policies_and_standards/_registry/catalogs/ai-autonomy-authority-registry\.md$` | `REGISTRY_PATH = docs/01_policies_and_standards/policies/ai_autonomy_authority_registry.md`（`:48-54`） | **两个路径都不存在**；真源实为 `…_registry/catalogs/ai_autonomy_authority_registry.yaml`（`.yaml`，异目录异扩展名） |
| GATE-13 | `^docs/19_development_workspace/drafts-and-audits/.*\.md$` | `DRAFTS_ROOT = docs/03_modules/_drafts`（`:33-35`） | **两个目录都不存在** |

后果（可复算）：仓库里永不可能出现匹配 `files:` 的提交文件 → 这两条 hook **触发次数恒 0**；
即使手动强跑，GATE-13 走 `:101-102` 返回 `([], 0)`，GATE-14 走 `:164-165` 返回
`(["注册表文件不存在: …"], 0)`——**而后者的 errors 非空却因 1.2 无入口而不被消费**。

### 1.4 派生件 `blueprint_registry.yaml`：退库后**盘上也没有**，且保护门禁已被自身退库动作作废

| 断言 | 实测 |
|---|---|
| `.gitignore:569-574` 裁定理由 | "该文件 100% 可由真源重生成…消费方读盘不读 git…本裁定仅解跟踪、**盘文件保留**" |
| 盘文件 | `ls docs/03_modules/blueprint_registry.yaml` → **No such file or directory**（`git check-ignore -v` 命中 `.gitignore:574`，`git ls-files` 不跟踪）→ "盘文件保留"**已不成立**，且因已解跟踪，这次消失**不会出现在任何 git 状态里** |
| 保护该文件的门禁 `derived_file_deletion_gate.py:94-97` | `_PROTECTED_DERIVED_FILES` 含此路径；但检测面是 `git diff --cached --diff-filter=D`（`:112`）——**对已解跟踪文件恒不产生 D 记录** → 保护被"退库"这个动作本身绕过；且 `:106-120` git diff 失败/异常 → `return None` = fail-open |
| 重生器 | `sync_registry_from_blueprints.py:8` INVARIANTS 已认账："磁盘缺失 MUST 走 BOOTSTRAP 全量重建，禁 exit 拒绝——旧硬退出=自举死锁"，`:155` 注："git clean 之后 registry 永久缺席，且 check_blueprint_code_alignment 的 registry 维度静默空转（fail-open）" |

**吃这个派生件的检测，逐个实测：**

| 消费方 | 缺文件时行为 | HEAD 实测 |
|---|---|---|
| `check_blueprint_code_alignment.py:224-228 load_blueprint_registry()` | `if not exists: return {}` | 实跑 `--json`：`blueprints_in_registry: **0**`（`depgraph_module_ids: 1571`，`code_headers_scanned: 3475`，`total_findings: 165 / HIGH 42`，rc=1）→ registry 维度 0 输入，ORPHAN 判定完全退化到 depgraph 单源 |
| 同文件 `:426-435 check_blueprint_file_list()` | **无条件 `return []`**（docstring："此检查冗余，保留函数签名以维持向后兼容"） | 该维度**永久 0 findings**，与输入无关 |
| 同文件 `:438-468 check_code_not_in_blueprint()` | 遍历 code_headers + depgraph（不吃 registry） | 61 条 `CODE_NOT_IN_DEPGRAPH`（LOW） |
| `triple_alignment.py:108-125 _load_bp_entries()`（GATE-TRIPLE-ALIGN，**pre-commit hook `gate-triple-align`**） | 认账"文件缺失不再是事故而是决策终态"，缺失则从 frontmatter 现算 | 实跑 rc=0，输出 42 条（`dep_map_orphan_module` **38** + `module_id_dep_map_missing` 3 + `code_path_missing` 1），38 条文案为 `expected=in blueprint_registry.yaml, actual=NOT FOUND`——**报告的是"我的输入不存在"，却被呈现为"38 个模块登记缺失"**；全 🟡 WARN → exit 0 |
| `scripts/construction/_e2e_check.py:29` | `open(...)` 无存在性判断 | 直跑必 FileNotFoundError（未实跑，避免副作用） |
| `tests/blueprint/test_blueprint_code_sync.py:96` | 断言期望该路径 | 测试面 |
| `validate_static_manifest_drift.py:98` | 已显式摘除 registry 检查（注释 2026-08-19"退库终态跟进"） | 真干净（主动降级为不检） |
| `auto_sync_all_registries.py:63` REGISTRIES["blueprint"] | 指向该路径，写侧 | 手工件 |

**结论**：`blueprint_registry.yaml` 一族的"0 输入"共牵动 1 条 pre-commit hook（GATE-TRIPLE-ALIGN，
输出为噪声）+ 1 条 pre-merge 阻断件（`check_blueprint_code_alignment`，经 `session_worktree.py:5858`
subprocess 调用，registry 维度空）+ 1 个手工同步器。**该族不是"门禁被绕过"，而是"门禁拿着空账本在报账本里没有"**。

### 1.5 【验真】`own_scope` 字段与代码实际一致（本项未失配）

`generate_gate_registry.py:150` 用 `own_scope = "_build_own_scope" in text`（**substring**）生成字段。
AST 复算（`commit_gate_scope.json`，116 文件逐个解析 `_build_own_scope` 调用点）：

- `own_scope=True` 且 AST 调用点=0 的：**0 条**；
- `own_scope!=True` 但 AST 有调用点的：**0 条**；
- `_build_own_scope` 定义：`commit_gates/_diff_helpers.py:475-494`，`files` 与 `session_id` 皆空 → `return scope or None`（`:494`）"退化为旧行为扫全量"，registry 读异常 → 降级 files-only（`:492` 注释"fail-open 红线"）。

即字段本身准确，但**生成方式是被禁止的 substring 判定**，一致属侥幸（任何在注释里提到
`_build_own_scope` 的 gate 都会被误标 True）。

### 1.6 作用域口径落差：26 条标 own_scope=True，其中 25 条注释自述"全量/全仓"

实测 `commit_gate_scope.json`：`claims_full_scan_n>0 且 ast_call_count>0` = **25 条**（占 26 条 own_scope=True 的 96%）。典型：

| 门禁 | 自述 | 实际实现 |
|---|---|---|
| `ASYNCIO-RUN-IN-CONTEXT:8` | "检测 `src/zephyr/` **全量**代码(.py)新增行…阻断" | staged ∩ 本 session（`:475-494`） |
| `DATETIME-NOW-FORBIDDEN:8` | "src/zephyr/ **全量**代码" | 同上 |
| `NO-BARE-SQL:113` / `BARE-SUBPROCESS:221` / `CAP-CONSISTENCY:147` / `MSG-EXPOSURE:411` / `NOQA-VALIDATION:232` / `UNSAFE-DICT-SPREAD:163` / `ZEPHYR-ENV-DIRECT-ACCESS:127` | "退化旧行为**扫全量**；**本 session 自身违规仍硬阻断**" | 外来 staged **不硬阻断**（降级审计） |
| `DECISION-MAP:8,31` | "触发式（2026-09-11 Owner 批准收窄）：本 commit 触及地图输入面才跑全量" | 不触即完全不跑 |
| `NO-HIGH-COMPLEXITY:43,47` | "**只检测新增函数**：存量高复杂度由人工排查+全量扫描脚本补充" | 存量不检 |

落差性质：不是撒谎（注释里同时写了收窄），而是**注册表不携带该信息**（`files_trigger` 空、无
`severity`/`enforce` 字段），读 `gate_registry.yaml` 的 AI 无法看出这 113 条 in-process 门禁
"扫什么"，只能靠逐文件读头注释。

## 2 六向挖矿日志表

| 向 | 事实 | 证据 |
|---|---|---|
| ①上游（谁生成注册表） | `own_scope` 由 substring 生成；`files_trigger` 对 113 条 in-process 门禁硬写空；`severity/enforce` 字段存在但全 None | §1.1 / `generate_gate_registry.py:145-150` |
| ②下游（谁消费注册表） | `validate_static_manifest_drift.py`（GATE-21，pre-commit）HEAD 实跑 **rc=1**，修复提示里点名"运行 `sync_registry_from_blueprints.py --write`"——即**修 registry 要靠那个磁盘缺失才刚被 BOOTSTRAP 救活的生成器**（自举闭环仍在） | `gate_head_run.json` GATE-21 rc=1 lines=12 |
| ③机制（默认关普查） | AST：46 个门禁脚本共 **70 个 default-off 旗标**（`--warn-only` 20 / `--ci` 16 / `--staged` 7 / `--json` 4 / `--fix` 2 / `--check` 2 / `--check-targets` 1 …）。其中真正吃掉检测维度的是 `--check-targets`（见下行）与 `--warn-only`（见下行） | `gate_flags.json` |
| ③机制（吃掉维度的旗标） | `check_blueprint_code_alignment.py:487-493` `--check-targets` 默认关，注释自认"仓内既存**数百条**历史未解析落点，清债前直接入链会把既有漂移变成全局硬阻断（裁定#262 后续批治本，2026-09-16）"。HEAD 实跑对照：不带=165 findings/42 HIGH，**带=513 findings/390 HIGH**（`BLUEPRINT_TARGET_ID_MISMATCH` 180 + `BLUEPRINT_TARGET_MISSING` 168） | `align_head.json` / `align_targets.json` |
| ③机制（warn-only 在链路里） | hook 侧 7 条：entry 含 `--warn-only` = `gate-naming-audit` / `gate-script-q` / `gateway-post-commit-ritual`；args 含 = `gate-nested-flat-prefix` / `gate-silent-degradation` / `gate-node-label-quality` / `gate-algo-quality`。实测**注册表 entry 与 hook args 不同步**：GATE-ALGO-QUALITY 注册 entry 无 `--warn-only`（直跑 rc=1 / 89 findings），hook 带 `--warn-only`（rc=0）→ 同一门禁在两个口径下结论相反 | `.pre-commit-config.yaml` + `gate_head_run.json` |
| ④后端（永不自动跑） | 68 hook 里 **8 条 `stages:[manual]`** = `gate-arch`、`gate-naming-audit`、`gate-frontmatter-audit`、`gate-bp-place`、`handoff-log-generate`、`gate-drift-light-scan`、`sync-audit-protocol-numbers`、`gate-dedup`；注册表把它们（GATE-ARCH/GATE-BP-PLACE/GATE-DEDUP/GATE-NAMING-AUDIT/GATE-FRONTMATTER-AUDIT…）标为 `source: pre-commit` + `status: active` + `files_trigger` 非空 | §1.1 + `gate_executability.json` |
| ④后端（manual 门禁的存量） | `validate_blueprint_placement.py --ci` HEAD 实跑：**176 条 P0 违规，rc=1**；注册 entry（不带 `--ci`）实跑 rc=0/188 行 → **双重失效**：注册口径不阻断 + hook 口径 manual 不触发 | 实跑 |
| ④后端（崩溃） | GATE-ARCH 实跑 **rc=1 + FileNotFoundError: YAML 文件不存在: D:\ZephyrAlpha\architecture_model**（`scripts/governance/_shared/yaml_utils.py:72` 把目录当 YAML 读）→ 若真接入 commit 链会全红；因 `stages:[manual]` 无人踩到 | `gate_head_run.json` |
| ⑤前端（面板） | 见 `data_ingestion_chain_mining.md` §2 ⑤前端：告警面板唯一生产者旗标默认关，`.runtime/ops_notifications/notifications.jsonl` 不存在 | 交叉引用 |
| ⑥数据字段（输入缺失→判康） | AST 普查 46 脚本得 **9 处**"输入不存在即返回 空/0/True"：`check_architecture_gates.py:914`（缺 `ssot-issue-tracking.yaml` → `return True`，实测该文件**不存在**，且 `:913` 把 SKIP 塞进 errors 后仍返回 True）、`validate_blueprint_overlap.py:102`、`validate_authority_registry.py:165`、`triple_alignment.py:110`、`validate_worktree_required.py:155`（缺 skip 日志 → 0）、`check_canonical_yaml_drift.py:107`、`verify_schema_truth.py:243`、`check_test_symbol_validity.py:140`、`validate_nested_flat_dirs.py:95` | `gate_noinput.json` |
| ⑥数据字段（HEAD 实跑台账） | 49 条 script 门禁 HEAD 实跑 rc 分布：**rc=0 27 条 / rc=1 18 条 / rc=2 4 条**（`gate_head_run.json` 共 52 条记录，另有 3 条 rc=None 进程崩溃无退出码：`GATE-INTEGRITY`/`GATE-VOCAB`/`GATE-SCHEMA-TRUTH`；52−3=本行 49）；其中 0 输出行数（standalone 无输入嫌疑）：`GATE-PROTECTED-PATHS`、`GATE-ALGO-FLOW`、`GATE-NAMING`、`GATE-14`、`GATE-13`、`GATE-SRC-NO-DATA`、`GATE-VMS-SSOT`、`GATE-NO-TESTS-UNIT`、`GATE-NO-COMMIT-DERIVED`、`GATE-GEN-NO-REALTIME-TIME` | `gate_head_run.json` |

## 3 业界与开源对照（四闸）

| 候选做法 | 来源可溯 | 交叉验证 | A股适配 | 可回测+数据可得 | 裁定 |
|---|---|---|---|---|---|
| 门禁必须**自带入口自证**：注册表条目附带一次 dry-run 冒烟（执行 `<entry> --help`，要求 rc==0 且有 usage 文本） | ✅ pre-commit 官方 hook 契约 | ✅ 本文 GATE-13/14 即缺此闸 | ✅ 纯本地 | ✅ | **采纳**（成本最低、直接杀 §1.2 全族） |
| 触发面可达性检查：`files:` 正则必须能匹配仓内现存或可预见路径（`rg --files | <regex>` 计数 > 0 或登记为"前瞻型"） | ✅ | ✅ §1.3 双不存在 | ✅ | ✅ | **采纳** |
| 派生件"输入存在性"作为门禁的第一条断言（输入缺 = 红，不是空集通过） | ✅ | ✅ §1.4 全族 | ✅ | ✅ | **采纳** |
| 注册表可执行化（policy-as-code，如 pre-commit 自身即真源，不再有第二份 YAML 描述它） | ✅ | ⚠️ 本仓 169 条 vs 68 hook + 116 模块 = 三份真源 | ✅ | ❌ 无历史可比 | **挂起**：先补"三份对账"门禁 |
| 门禁"触发计数"遥测（每条门禁 30 天实际执行/失败次数，0 执行即红） | ✅ | ✅ 能一次性暴露 manual/空触发面全族 | ✅ | ✅（`.runtime/gate_audit/` 已有 worktree_skip.jsonl 先例） | **采纳为终局方案**：本表 §4 的 GT-* 全是它的特例 |

## 4 堵点与欠账清单

| ID | 级别 | 病灶类 | 堵点 | 可施工验收标准 |
|---|---|---|---|---|
| GT-1 | P0 | 自欺骗-门禁 | GATE-13 / GATE-14 脚本无 `__main__`，`--ci` 恒 rc=0，配置头却记"已转硬阻断"（§1.2） | 补入口或改 hook entry 为统一 runner；新增门禁断言"每条 script 型注册门禁 `python <entry>` rc∈{0,1} 且 stdout 非空"；`.pre-commit-config.yaml:19,21` 文案与实测一致 |
| GT-2 | P0 | 自欺骗-门禁 | GATE-13/14 的 hook `files:` 路径在仓内**不存在**（§1.3）→ 触发恒 0；GATE-14 真源已改 `.yaml` 且换目录 | hook `files:` 指向真在用的真源路径；加"触发面可达性"检查（对每条 hook 正则跑仓内匹配数，0 者红或标 forward-looking） |
| GT-3 | P0 | 自欺骗-注册表 | 8 条 `stages:[manual]` hook 在注册表中仍标 `source: pre-commit` + `files_trigger` 非空；HEAD 存量：GATE-BP-PLACE `--ci` **176 条 P0**、GATE-ARCH 直接崩溃（§1.4/④后端） | 注册表新增 `trigger_stage` 字段并由生成器从 `.pre-commit-config.yaml` 实读（禁止手写）；`manual` 者 `files_trigger` 置空 + `status: manual_only`；GATE-ARCH 的 `architecture_model` 目录当 YAML 读的 bug 修复 |
| GT-4 | P1 | 派生件空账本 | `blueprint_registry.yaml` 盘上不存在，而 `derived_file_deletion_gate` 只看 `git diff --cached --diff-filter=D` → 解跟踪即绕过（§1.4） | 保护清单从"staged 删除"改为"存在性 + 新鲜度"（盘缺 = 红）；BOOTSTRAP 落地并留 `blueprints_in_registry>0` 断言；`check_blueprint_code_alignment.py:426-435` 的无条件 `return []` 要么恢复维度要么删除并在注册表标 retired |
| GT-5 | P1 | 自欺骗-告警文案 | GATE-TRIPLE-ALIGN 把"输入文件不存在"输出成 38 条"模块 NOT FOUND"WARN，rc=0（§1.4） | 输入缺失单独归因（`INPUT_MISSING`），与真漂移分桶；WARN-only 结论不得进 rc 语义 |
| GT-6 | P1 | 默认关维度 | `--check-targets` 默认关掩盖 **348 条 HIGH**（180 落点 ID 不符 + 168 落点文件不存在）（③机制） | 先清债再入链；或引入 baseline 文件（存量豁免、增量红），禁止"整维默认关" |
| GT-7 | P1 | 口径相反 | GATE-ALGO-QUALITY：注册 entry（无 `--warn-only`）rc=1/89 findings，hook args（带）rc=0；两者由同一注册表描述（③机制） | 生成器把 hook args 合入注册表 `entry`，`validate_static_manifest_drift` 增加"entry 与 hook 实参一致"断言 |
| GT-8 | P2 | 作用域不可见 | 113 条 in-process 门禁 `files_trigger` 恒空、无 `severity/enforce`；25/26 own_scope=True 门禁自述"全量"（§1.6） | 注册表补 `scan_scope`（full-staged / own-session / trigger-only）由 AST 提取调用点生成，禁用 substring |
| GT-9 | P2 | 自举闭环 | GATE-21（rc=1）的修复提示要求跑 `sync_registry_from_blueprints.py --write`，而后者正是退库死锁的当事件（②下游） | 修复提示改指 BOOTSTRAP 路径；GATE-21 在 HEAD 收敛到 rc=0 或登记为已知豁免 |
| GT-10 | P2 | 注册表↔现实三源 | 169 注册条目 vs 68 hook vs 116 门禁模块，无对账门禁（`gate-id-uniq` 只校 hook id 唯一，实测"scanned 68 hook declarations, 68 unique ids"） | 新增三向对账门禁：注册条目数==hook数+in-process数，孤儿（注册无实体/实体未注册）为红 |
| GT-11 | P1 | 判定不可复现（硬阻断门禁偶发失灵） | 实证对：`c4425e60cb`（2026-09-16 23:07，带 `[GW:]` 认证标记）把 3 行含裸 SQL 的 **added 行**放进 HEAD（`git show c4425e60cb -- src/zephyr/strategy_pipeline/screen_source.py \| grep "^+" \| grep -i select` → 3 命中，落点 `screen_source.py:166/…`），同一文件同一规则**今天实测** `_SQL_PATTERN.search(line)=True`、`_is_exempt_line=False`、`noqa: bare-sql` 标记 0 处（不在 `noqa_exempt_registry.yaml`）——门禁没拦；而同类内容在 09-17 拦掉了自家 queue item。**同规则·同内容·两次相反结论** ⇒ "硬阻断"实为偶发阻断 | 先定机制再谈修：`_get_added_lines` 的观测面是 `gateway.run_git(["git","diff","--cached",…,"--",path])`，**空输出（rc=0）与"确实无新增行"不可判别**——worktree/序列化器 index 与主区 index 分歧时该文件在此 context 未 staged 即静默判干净（`_diff_helpers._repo_state_has_file:310-319` 已把"序列化器落地 worktree 未 checkout 的 staged 新文件"列为同盲区家族，2026-09-17 清偿中）。①added 行为空时改判"不可判别"：与本 commit 文件清单交叉核对，清单内而 diff 空 → 红（禁 fail-open）；②可复现性回归：用真实提交 diff 造 fixture 断言 NO-BARE-SQL `passed=False`；③追溯复核门禁：对最近 N 条 HEAD 提交重跑内容型门禁，存量判定与重跑结论不一致者出清单（不是让它红，是让"门禁何时失灵"变成可观测面） |
| GT-12 | P1 | 恒红测试无观测面 | 实测：`tests/governance/governance_e2e/test_phase1_gate_check.py::test_eight_module_dirs_exist` 与 `::test_each_module_has_init` **已恒红 12 天**（本轮串行复现 `2 failed, 1 passed, 1 skipped`）。红因：`agent-spec / drift-detector / budget-enforcer` 三个 kebab marker 目录被 `441852d976`（2026-09-05，`audit(AI-21)`，提交自述 "no new capability created"）整目录删除，而被删文件第 6 行自述 `# Phase 1 gate marker (kebab-case dir). Implementation in zephyr.gov_drift.` ⇒ 删掉的是**指向实现的占位指针**（每目录仅 1 个 `__init__.py`，共 106 行），能力零损失，但测试"八目录同名存在"的前提自此失效。真正的洞不在测试红，在**红没有归属**：`_registry/catalogs/` 只有 `noqa_exempt`/`panorama_exempt_list`/`registry_master_index_exemptions` 三张豁免表，**没有"已知红/带期限豁免"登记通道**，`known_failures/xfail 名单` 全仓 grep 0 命中 ⇒ 恒红与真回归在观测面上不可区分，任何跑全量的人第一天看到 2 条红、第三天就脱敏 ⇒ "套件全绿"这一验收信号自 09-05 起已被污染，且它正是 GT-1/2/3 那批"门禁不跑"能长期存活的培养基 | 归治理域，本轮**不代修**（宪章 §3.4；该目录 09-16 仍在 `externalize_algo_flow` 480 文件波次中被别的车道动）。两条候选修法：①测试断言对象从"kebab 目录存在"改为"八能力→实现模块可导入"，且该映射须由注册表生成（§9 第 5 条：静态清单禁手工维护——现 `PHASE1_REQUIRED_FILES`/`EIGHT_MODULES` 两张手抄清单本身就是漂移源）；②开"已知红登记表"通道：条目带 `owner`+`到期日`+`到期未修即升 P0`，配一条门禁核对"HEAD 恒红集 ⊆ 登记表"，使长红要么被修要么被点名，禁止无声挂着 |
| GT-13 | P1 | 已知红制度化＝xfail 毯子化 | 实测：`tests/governance/integration/test_all_scripts.py` `--collect-only` **2122 items，其中 2044 条（96.3%）挂 blanket `xfail(strict=False)`**（`_XFAIL_ARCH092`:64 / `_XFAIL_JSONL`:68，未挂毯子仅 78 条），reason 自述"待专项清偿批修脚本后摘除"（`860e4c2787`，2026-08-31 落地）。`strict=False` 把三种相反状态压成同一绿色：**脚本仍崩=XFAIL 绿 / 脚本已被别人修好=XPASS 绿 / 新崩=XFAIL 绿**——本轮进度带里 XPASS（大写 X）与 xfail（小写 x）混排即证："已修未摘毯子"与"未修"同时存在且不可分。**2026-09-17 全量实测（4911s 独占跑）：`1857 xpassed / 187 xfailed / 77 passed / 1 failed`** ⇒ 2044 条毯子里 **91% 早就修好了**，毯子仍挂着；唯一真红经复测证明是确定性缺陷而非调度噪声（GT-17，已治本 `2ba9536a`）。它与 GT-12 同根（无"已知红/带期限豁免"登记通道），但比 GT-12 更隐蔽：恒红至少还在终端输出里可见，毯子把红**制度化成期望值**，并且这 2044 条正是"治理脚本健康探测"的全部覆盖面——探测器自己不可信时，GT-1/2/3 那批"门禁不跑"就永远只以 xfail 形态存在，不会以红形态逼任何人清账 | ①`strict=True` + baseline 文件（只对 baseline 内条目豁免；修好即 XPASS→硬报，逼摘毯子）；②reason 里的"待专项清偿"转成可核对债项（owner+到期日，与 GT-12 同一条登记通道）；③`xpassed` 计数进 CI 观测面（当前无通道读它），非零=存量债已清偿但毯子未摘；④**本战役已给出 1857 这个数**，摘毯子批可据此按 reason 分桶直删（187 条真 xfail 才需要 baseline 承接） |
| GT-14 | P1 | 登记工具产幻影证据面，且被下游门禁当真值消费 | `apply_depgraph.py:1102` `blueprint_path = f"docs/03_modules/{blueprint_id}/"` 是**纯字符串拼接**；同函数 `:1096-1099` 确有存在性检查，但只 `print("WARNING: ... 蓝图文件不存在", file=sys.stderr)` 后**照样 INSERT/UPDATE**。只读取证（PG `nodes` 表，探针跑完即删）：**166 条带 `blueprint_path` 的节点里 164 条指向盘上不存在的目录（98.8%）**——例：`docs/03_modules/MOD-SIG-142/`、`docs/03_modules/MOD-DAT-daban_engine_payload/`、`docs/03_modules/MOD-L08-001/`（真蓝图实为 `docs/03_modules/_domain_<X>/<module>/blueprint.md` 三级布局，id 拼一级目录结构上必然不存在）。**下游把它当事实**：`triple_alignment.py:186` `SELECT DISTINCT blueprint_id, path, blueprint_path FROM nodes WHERE blueprint_id ~ '^(MOD-\|SH-\|SYS-)'` → `_ModuleCheckContext.bp_path` ⇒ **GT-5 那 38 条"模块 NOT FOUND"WARN 的根因在此**：蓝图没丢，是登记器写了一个从未存在的路径，而门禁用它判"模块不存在" | ①存在性检查改硬失败（或存在才写、不存在写空 + 单独 pending 列），禁"warn 后照样落库"；②蓝图路径不得由 id 推导——由 `capability_canonical_file_registry.yaml`/blueprint 目录反查（真源已有，拼接是伪造）；③`triple_alignment` 对盘缺路径单独归因 `PHANTOM_PATH_FROM_REGISTRAR`（不计入"模块缺失"，与 GT-5 修法并批）；④存量 164 条一次性重推 + 出清单（生成器产出，勿手改，宪章 §9 第 5 条） |
| GT-15 | P1 | 验收断内存对象、产物却丢字段（本轮已治本） | H4-B 实证：`_collect_timeseries` 造的 `cash_curve` 只随内存 `ts` 返回，而 `sink_backtest_result` 的具名参数集只有 equity/trade/drawdown/benchmark → **端到端真数据落盘产物 `cash_curve points=0`**，同时测试 `assert ts["cash_curve"]` 自接线当日起**一直全绿**。这是本节点母题的最纯形态：验收语句写的是"产物现金腿可事后复核"，断言对象却是函数返回值。已修：`metrics["cash_curve"]` 落盘（`BacktestRunArtifact` 顶层 `[MODIFY-GUARD]` 结构冻结，不加键）+ 测试改**读盘三断**（落盘==内存逐位等、与 `equity_curve` 等长、点结构含 timestamp/cash），commit `7186ca49c5` | 通用判据（推广普查，本条**未做完**）：凡验收语义含"产物/落盘/上报/可事后复核"，断言对象 MUST 是读盘结果。可机证化：①`_collect_timeseries` 返回键集 ⊖ `sink_backtest_result` 参数集 的差集非空即红（一条结构性防漏门禁，成本极低）；②普查 `tests/` 内"只断返回值不断落盘"的产物类测试（`grep -rn "assert ts\[" tests/` 起步），逐条判定是否该升级为读盘断言 |
| GT-16 | P2 | 自家文档把门禁能力写强/写反，据此放弃正当修法 | 本车道挖矿文档 `reconciler_event_trigger_chain_mining.md` RC-14 曾以"NO-HIGH-COMPLEXITY **扫整文件**且无 noqa 通道 ⇒ 存量圈复杂度越门禁故暂不改"为两条硬理由之一。读码证伪：`high_complexity_gate.py:168-186`（裁定#214 专治此误判）只罚 `node.lineno ∈ added_lines` **且** `node.name ∉ HEAD 函数名集合` 的**真新增**函数，改存量函数（`reconcile_for`=29）根本不触发；"无 noqa"那半条为真。危害不在记错事实，在**据此把可做的修法判成不可做**（文档是后续会话的施工依据，写强门禁＝自造假约束）。同一条事实其实早已记在长期记忆里，落文档时未回核代码 | ①写门禁行为 MUST 附 `file:line` 判据（本表 GT-1~GT-10 全部如此，RC-14 是本战役唯一裸断言处，已改）；②把"门禁判据范围"从散文升成注册表字段：`gate_registry.yaml` 增 `scope: added-new-functions \| whole-file \| staged-lines`，由门禁自述+生成器同步，文档/记忆引用字段而非脑补；③已修正=RC-14 现只保留 HELD-OVERLAP 一条真理由（受害草稿数实测已从 8 增至 13） |
| GT-17 | P1 | 探测器旁路"扫描面真源"，把 96% 火力打在别人在途草稿上；预算被击穿后退化成只剩 `timeout` 一种说法 | `validate_config_integrity.py` L4 `l4_path_constants` 手写 `REPO_ROOT.rglob("*.py")` 配**本地** `EXCLUDE_DIRS: tuple[str, ...] = ()`（`:95`，自 2026-05-04 建文件起就是空元组），把共享真源 `_shared.constants.EXCLUDE_DIRS:213`（11 项，且 `iter_files` 另带"目录名以点开头不进入"规则＝宪章 §9.4 会话暂存树的契约性排除）顶掉，等于零剪枝。实测：枚举 **199267** 个 `.py`，其中 **190928** 个躺在 `.aidrafts`(106599)/`.worktrees`(65925)/`.runtime`(18200) 里（仓内 `.py` 真身 8275）；L4 吐 4018 条告警、**4003 条是别人在途草稿**、15 条真源码一致性漂移被埋；单脚本 `--warn-only` **121s**（并发挤占下 201s）> `scripts/script-manifest.yaml:3487 timeout_seconds: 60` ⇒ quick 冒烟只能报 `timeout`。**双重失效**：真信号被噪音埋掉，同时探测器因超时失去全部判定能力——而这正是 GT-1/2/3"门禁不跑"的第三种形态：**门禁在跑，但跑成噪声**。已地质修 `2ba9536a`：观测面改 git 口径（`ls-files --cached --others --exclude-standard`，与 GATE-ERRCODE `604f414846` 同先例），121s→**7.1s**，总告警 4202→198，L4 真源码 15 条前后逐字节相同（零覆盖损失） | ①通用判据：**全仓扫描型探测器的观测面必须是 git/注册表口径，不得是文件系统枚举**；②结构闸候选：普查 `scripts/governance/**` 里 `REPO_ROOT.rglob(` / `os.walk(` 且未 import `_shared.walk`、未走 git 口径的扫描器，逐条判"是否旁路真源"——`validate_script_quality.py:344` 已有同型判据但**只识别 `os.walk`，识别不了 `rglob`**，本条就是它的漏网形态，判据应从"写法"升级为"是否使用共享扫描面"；③`timeout_seconds` 在 manifest 里 1004 条全是默认 60（`generate_manifest.py` 产出，禁手改），缺"按实测校准预算"回路：建议 reconciler 记录每脚本 P50/P95 实测耗时、预算取 P95×2、越界出清单，否则预算永远是愿望值、探测器永远只会喊"超时"而说不出"变慢了多少" |

## 5 子节点清单（还能挖的）

1. 49 条实跑中 10 条 0 输出（standalone 无输入嫌疑），需带 `--staged`+伪造 index 复测才能区分"真干净/没输入"。
2. 55 条 pre-commit 门禁的 `own_scope` 字段缺失 = 该维度对读注册表者不可见（本文只核了 in-process 侧）。
3. `.pre-commit-config.yaml:1-45` 的 warn-only→硬阻断"过渡时间表"是**手写**的，与 hook args 无机器绑定；GATE-22 记"仍 warn-only 骨架（当前 SKIP）"，需实跑核实 SKIP 语义。
4. `scripts/governance/run_gate_chain.py`（GATE-VOCAB 用它串两条子检查、逗号传参）——串链内任一子件失败是否被聚合掩盖。
5. 4 条 rc=2（用法错误类：`GATE-TEST`/`GATE-RETURN-CONTRACT`/`GATE-WORKTREE-OPS-TELEMETRY`/`GATE-ENCODING`）：注册 entry 与脚本 argparse 不匹配，值得逐条查是否等价"从未真正跑过"。
6. `.runtime/gate_audit/worktree_skip.jsonl`（实测存在，3756 字节，末次 09-08）——worktree 侧 skip 计数的真实触发史。

## 6 封矿判定

**部分封矿（本节点主脉已枯，留 3 条活脉）**：

- 枯：注册表账面/字段一致性（§1.1、§1.5 已穷举，own_scope 侥幸准确）；派生件 registry 消费族（§1.4 已逐个定性，含 1 条 `return []`、1 条 BOOTSTRAP 认账）；"脚本无入口"族（AST 全量 53 条，命中 3 条：`GATE-13`/`GATE-14` 无入口 + `GATE-ERRCODE`（其 entry 指向 `tests/governance/test_error_code_consistency.py`，本身不是可执行门禁脚本），无更多）。
- 活脉 A：GT-3 的 manual 门禁存量（GATE-BP-PLACE 176 P0 这类"永远不跑的红"）逐个量化——本文只跑了 4 条 manual。
- 活脉 B：10 条 0 输出门禁的"没输入 vs 真干净"需伪造 staged index 才能判，本轮受只读约束未做。
- 活脉 C：门禁触发计数遥测（§3 末行）一旦落地，本文全部 GT-* 可由一条门禁自证；那是下一节点的矿脉，不是本节点的。

退出路径裁定建议：**先施工 GT-1/GT-2/GT-3**（三条都是"门禁实际不跑"的根因类，改动局限于
门禁配置与注册表生成器，零策略风险），GT-4/GT-6 需 Owner 裁定（涉及恢复一个被裁退库的派生件、
以及 348 条 HIGH 的清偿排期）。

## 修复优先级裁定建议

| 序 | ID | 为什么先它 | 预计改动面 | 风险 |
|---|---|---|---|---|
| 1 | GT-1 | 2 条硬阻断门禁当前对任何输入都不可能失败，是最纯粹的门禁虚设 | 2 个脚本补 `__main__`，或 1 处 hook entry 改指 runner | 低 |
| 2 | GT-2 | 与 GT-1 同批：即使补了入口，触发面仍为 0 | `.pre-commit-config.yaml` 2 个 `files:` + 新可达性断言 | 低 |
| 3 | GT-3 | 8 条 manual + 176 条 P0 存量 + 1 条崩溃，注册表口径与执行口径系统性背离 | `generate_gate_registry.py` 实读 stages | 中（注册表全量重生成，需 GATE-21 复验） |
| 4 | GT-11 | 它使"门禁已阻断"这件事本身不可信：GT-1/2/3 是"门禁不跑"，GT-11 是"门禁跑了也可能判错"——后者污染所有前者的验收证据 | 1 条真实 diff fixture 先定机制，再改 `_get_added_lines` 空输出语义 | 低（判据收紧可能使原本静默放行的提交转红，需与序列化器同盲区家族并批） |
| 5 | GT-12 | 恒红测试是"全绿"信号失效的培养基——GT-1/2/3 能长存正因没人看套件整体状态；且它的修法是一条登记通道，不是改代码 | 新增豁免表 + 对账门禁；测试侧改断言源归治理域 | 低（但需与治理域并批，勿单点动 `tests/governance/governance_e2e/`） |
| 6 | GT-5/GT-7 | 结论失真/口径相反，属"能看到但看错" | 2 文件 | 低-中 |
| 7 | GT-4/GT-6 | 需 Owner 裁定（派生件是否回库、348 HIGH 清偿策略） | 跨派生件治理战役 | 高，勿单批做 |
| 8 | GT-8/GT-9/GT-10 | 结构性可观测性，随门禁遥测一并做 | 分散 | 低 |
| 9 | GT-14 | 它是**别的门禁的假证据源**：GT-5 的 38 条"模块 NOT FOUND"WARN 根因就在这条（164/166 失配＝登记即污染，非偶发）；先断源，再谈 GT-5 的归因分桶 | `apply_depgraph.py` 存在性检查转硬失败 + id→真蓝图路径改反查 + 存量 164 条重推出清单 | 中（改 depgraph 行需与再生/对账并批） |
| 10 | GT-15 | 本批已治本（`7186ca49c5`）；剩一条**廉价结构闸**：`_collect_timeseries` 返回键集 ⊖ `sink_backtest_result` 参数集 差集非空即红，能一次性挡住全仓同形态漏盘 | 1 处差集断言 + 测试侧普查 | 低 |
| 11 | GT-13 | 与 GT-12 共用同一条"已知红/baseline"登记通道，**勿单点把 strict=False 改 True**：2044 条毯子瞬时转 strict 会爆出大面积红，反而把真债掩在噪声里 | baseline 文件 + 通道登记 + XPASS 计数进观测面 | 高（顺序错即制造新一轮恒红） |
| 12 | GT-16 | 文档卫生，本批已就地修正（RC-14 只留 HELD-OVERLAP 一条真理由）；结构修法=门禁判据范围进 `gate_registry.yaml` 字段 | 已改文档；`scope` 字段随门禁遥测批次 | 低 |
| 13 | GT-17 | 本批已地质修（`2ba9536a`，观测面→git 口径，121s→7.1s）；剩两条结构修法：①`rglob` 旁路扫描面普查（现判据只认 `os.walk`）②`timeout_seconds` 按实测 P95×2 校准回路（现 1004 条全默认 60） | ①1 处判据扩展 ②1 个 reconciler（事件触发，宪章 §9 第 3 条） | 中（①会让既有手写扫描器集中出清单，需按域分桶而非一次性红） |

## 7 pass A 22 红归因台账（2026-09-17 复跑，逐条判归属）

**为什么记在这里**：GT-12/GT-13 的母题是"红没有归属通道 ⇒ 全绿信号失真"。一次跨 6 域
全量跑（15 878 passed / 22 failed / 1 852 xpassed）出来的 22 条红，若不逐条归因，
下一轮就会有人拿"套件红 22 条"当"本战役引入 22 条"来读——这正是本节点批判的读法。
判据一律给到 `file:line` 或"起点复现"这类可核事实，禁按印象分类。

| 归因 | 条数 | 测试与机证 | 处置 |
|---|---|---|---|
| **本车道自伤，已修** | 1 | `tests/governance/test_validate_yaml_summaries.py::test_consumer_registry_passes_when_consistent`：`domain_events.yaml summary.by_audit_level.medium=8，实际=9`（本车道 `895ce2c91f` 加 medium 事件时只同步了 `total_events`/`by_frequency`，漏 `by_audit_level`） | 已按条目机械重算（`6c461bb6ba`）；派生计数块由条目推导，属 §9 第 5 条"静态清单禁手工维护"的又一个实例 |
| **陈旧契约测试（早于本战役），已修** | 5 | `tests/governance/trading/{test_e2e_pipeline,test_phase_e_main_flow}.py`：`isinstance('600519', Order)`=False、`'str' object has no attribute 'quantity'`——`generate_target_weights` 自 `8c1564b272`（2026-09-02）返回 `dict[str,float]`，迭代得裸代码串；`test_l09_backtest_basic` 传 flat+无 `symbol` 列面板→引擎取不到价→0 成交被 `engine_base.py:227` 合理性护栏 fail-closed。**五处在 `b1334ae3ff^`（本战役起点前一提交）全量复现** ⇒ 证伪"本车道引入" | 测试改调同件既有 `generate_orders()`、数据改 `MultiIndex(symbol,date)`（引擎 docstring 契约），46 passed |
| **探针基线未随真源，已修** | 3 | `test_check_vocab_hardcode.py` 三断言硬编码 82 vs 真源 94（`config/governance/noqa_exempt_registry.yaml` 于 `4efe2ba568` 2026-09-13 净增 12 条） | 基线按真源对齐 + 日期注记（条目内容未改） |
| **环境/套件污染（隔离复跑即绿）** | 4 | `test_doc_lifecycle.py::TestRecycleBin::test_prune_after_30_days`（WinError 5 recycle_bin 改名被锁）；`test_resource_schedule_gate.py::test_pool_concurrency_absent_field_is_bit_for_bit_legacy_behaviour`；`test_phase1_gate_check.py::test_each_module_has_init`；`test_reconcile_generators.py::test_stale_scans_all_generators`（`reconcile_stale: 跳过——已有重生成在跑（held by pid=20168）`→扫 0 个） | 不改代码：三条同文件隔离复跑 `71 passed`。**"并发跑就红、隔离跑就绿"本身是 GT-12 的一个观测面**（红因是共享 `.runtime`/进程锁，不是被测件） |
| **上一行判错的一例（复测推翻，已治本）** | 1 | `test_all_scripts.py::test_warn_quick[governance/d1_structure/validate_config_integrity.py]`：pass A 时按"脚本执行 status=`timeout`，非断言失败"记成环境项。本轮**独占复跑仍红**（61.15s 撞 60s 预算），直跑脚本实测 **121s**（并发挤占下 201s）⇒ 与调度无关，是确定性缺陷。根因见 GT-17 | 已修 `2ba9536a`：观测面收敛到 git 口径后 7.1s，L4 真源码 15 条告警逐字节不变。这条错判不删——它正是本节点母题的自证：**"timeout" 这一种措辞会把确定性性能塌方伪装成调度噪声**，没有基线复跑就会永久误归 |
| **他会话归属，按宪章 §3.4 不代修** | 8 | `test_phase1_gate_check.py::test_eight_module_dirs_exist`＝GT-12 已登记的 12 天恒红；`test_check_vocab_hardcode.py::test_main_exits_zero_warn_only`（余 5 处 `[STARTUP] lazy`＋2 处复制词表加载＋2 条 UNREGISTERED noqa，全属 altdata/research 车道）；`test_security_scripts.py::test_exit_code_gate_passes`/`::test_naming_gate_passes`（他会话治理脚本裸 `return 0/1/2` 与命名）；`test_battle_map_research_incubation.py` 三条（步数 33→34，`BM-RES-01-E` 属在途作战地图波次）；`test_error_code_consistency.py::test_all_code_definitions_registered`（`ZA-INF-RT-ADM` 定义于 `src/zephyr/infra_runtime/runtime_admission.py:89`，`429b68783b` 2026-09-17 07:36 由 st-govmap 落地，错误码注册表 0 条 `ZA-INF-RT`） | 逐条已在收口报告点名 owner+落点；代修=改别人语义（错误码含义/是否可重试只有 owner 知），且热注册表并写会撞号 |

**本车道自伤的第二类（不是红但已改）**：本车道 3 个文件头写了词表外的 `[STARTUP]` 值
（`on_demand`×2、`event`×1）——`startup_vocabulary.yaml` 只有 5 个合法值，门禁对越词表只 WARN
故长期无人看。已归位为 `manual`/`imported`/`event_driven`，仓内 vocab WARN 8→5。
它与 §2 ⑥"输入缺失→判康"同族：**warn 级门禁在 100% AI 场景 = 没有门禁**（GT-1/2/3 的根因句式）。

## 8 strict 模式残差（GT-17 副产，都不是测试红但都是"规则不可满足"）

`validate_config_integrity.py` 严格模式（不带 `--warn-only`）在 HEAD 仍 `exit 1`。要点不在
"有 3 条 error"，在**mandatory 规则的自证条件长期不可能满足、且没有任何观测面看得见它**：
`trae_016_arch_drift_detection.yaml:117` 把"配置一致"判据写成 `exit 0`、`:121` 把"漂移则修复
后才能继续"列为强制步骤，而冒烟层一律 `--warn-only` ⇒ 这条规则从未被真正核对过（§2 同族）。

| 残留 | 机证 | 归属与处置 |
|---|---|---|
| **R-GT17-a**：`[L10] pyproject.toml 未注册 marker ['smoke','timeout']` = 探测器**两条假阳性** | ①`timeout` 由 pytest-timeout 插件注册：`python -m pytest --markers` 实测输出 `@pytest.mark.timeout(timeout, method=None, func_only=False, …)`，而 L10 只读 `pyproject.toml` 显式 `markers` 列表（`:172-181` 9 项，无 timeout）；②`smoke` 的 6 处命中全在测试文件 **docstring 散文**里（`tests/governance/audit/test_p3_integration_smoke.py:39`、`tests/governance/test_apply_depgraph_smoke.py:44` 等"4. @pytest.mark.smoke：快速运行"式自述），L10 用全文正则不分代码/散文。反证：默认配置带 `--strict-markers` 跑 6456 条测试全绿 ⇒ 若真未注册，收集期即炸 | 修法=L10 观测面改 AST 装饰器提取 + markers 取 pytest 自述注册表（含插件项），勿硬编码插件 marker 名单（RULE-SSOT）。本轮未做：改 detector 判定口径会同时改它对全仓的 error 集，须与 GT-17② 旁路普查并批 |
| **R-GT17-b**：`[L1] config/chainmap_cluster_names.yaml` 解析为 None | 13 行全注释、零数据条目；声明消费方 `industry_chain_map_gate.py`、`dashboard/api_server.py`（"空契约文件"＝GT-14 幻影证据面同族） | 归 chainmap 车道（`47df41167f`，2026-09-10）：要么填要么删，不代修（宪章 §3.4） |
| **R-GT17-c**：`[L5] trae_028_doc_structure_naming.yaml 缺少 config/ 目录结构定义` | 规则 YAML 自身缺 `config/` 目录条目，而该规则正是"目录结构命名"真源 | 归规则域（`e2fede99f4`，2026-08-18） |
| ~~`[L1] config/asset_inventory.yaml` YAML 语法错误~~ **本轮已消** | `:151` notes 双引号标量里 `F:\offrepo_backup\data_download` 单反斜杠 → `found unknown escape character 'o'` → **整文件 `yaml.safe_load` 失败**，消费者 `scan_offrepo_assets.py` 等一读即抛 | `2ba9536a` 反斜杠双写；解析后 notes 文本与原意逐字相同（`offrepo_assets` 15 条完整可读） |

## 9 红蓝变异探针台账（2026-09-17 收尾轮，6 条变异全部转红）

**为什么记在这里**：本节点母题是"契约写在纸上、执行链不兑现"。要证伪"我自己也在写纸面声明"，
唯一办法是把每句声明**反向改坏**，看守侧测试是否变红（变异=攻，测试=守）。探针脚本用完即删
（`.runtime/tmp` 收尾清零），故台账落文档留可复核性。还原用字节级备份而非 `git checkout`——
本仓 `.gitattributes` 声明 `eol=lf` 而工作区是 CRLF，走 git 还原会整文件重写换行、把一次探针
变成一次全文件 diff。

| 变异（攻） | 目标真源 | 应接住的测试（守） | 实测 |
|---|---|---|---|
| M1 台账测量值去掉 `≈` 前缀（把"未在宿主源码落地的裸小量"伪装成已落地） | `regime/features/overlay_features.py` | `tests/regime/test_overlay_features.py` | `1 failed, 63 passed` → RED |
| M2 删掉"状态词表真源为空即抛"的 fail-closed | `pf_core/strategy_engine/framework_composer.py` | `test_states_channel_empty_source_fails_closed` | `1 failed, 38 passed` → RED |
| M3 执行链少披露一个键（`signal_age_disclosed` 改名使其不落 metrics） | 同上 | `tests/backtest/test_h3h4_cash_pit_exec_chain.py` | `1 failed, 24 passed` → RED |
| M4 清空**整装路径**落盘名册 `_PERSISTED_VIA_METRICS_TS_KEYS` | 同上 | 同上（GT-15 结构差集闸 + 读盘三断同时红） | `2 failed, 23 passed` → RED |
| M5 清空 **CLI 单策略路径**落盘名册（本轮 R-H4B-s 新增的第二生产路径） | `scripts/run_backtest.py` | 同上（`test_cli_backtest_artifact_carries_cash_leg` 三判据） | `2 failed, 23 passed` → RED |
| M6 事件账本派生计数 `summary.by_audit_level.medium` 9→8 | `architecture_model/events/domain_events.yaml` | `tests/governance/test_validate_yaml_summaries.py` | `1 failed, 4 passed` → RED |

`restore check`：4 个被变异文件的 `git status --porcelain` 输出 = `''`（字节级原样还原）。
M4/M5 各炸 2 条，说明"登记名册 → 采集器构造 → 读盘断言"三处互相咬合：任一处单独放松即红，
这正是 GT-15 要的形态（不是靠人记得同步三处）。M1 是 GT-15 的镜像用法——台账里"实测值"与
宿主源码落地状态由同一契约测试绑定，改坏措辞即失去豁免并被判红。


## 10 双次复验台账（连续两轮同范围，判据=两轮问题数 0 且失败集差为空）

**为什么记在这里**：Owner 的收口判据是"连续两次测试问题=0"。要让这句话可核而不是一句
修辞，必须锁住被测量——两轮之间若有任何一字节改动（本仓多会话并发是常态），两轮测的就
不是同一个对象，"两次全绿"退化成"两次各自绿"。故本台账的第一列不是通过率而是**树指纹**。

| 轮 | 树指纹 | 范围 | 结果 | 失败集 |
|---|---|---|---|---|
| B5 | HEAD `eb902d3f1a`；`git status --porcelain` 对 src/scripts/tests/config/architecture_model/docs/03_modules 取 sha1=`fc48f1f524cf`；本轮三件落地文件（`scripts/run_backtest.py`、`tests/backtest/test_h3h4_cash_pit_exec_chain.py`、`scripts/governance/d1_structure/validate_config_integrity.py`）合算 sha256=`3cf2ba87329a144e` | 12 目录 + 2 文件，collected 7342，实跑 345 个测试文件 | 1 failed, 7341 passed in 601.25s | `tests/governance/test_error_code_consistency.py::TestCodeToRegistry::test_all_code_definitions_registered` |
| B6 | **与 B5 同值**（跑后再取一次三指纹全等，两分钟窗口内零漂移） | 同上（同命令同范围） | 1 failed, 7341 passed in 585.85s | 与 B5 逐字一致（两文件 `FAILED` 行 `diff` 输出为空） |

**唯一一条红的归属（不是"我的红"，给到落点级）**：`ZA-INF-RT-ADM` 定义于
`src/zephyr/infra_runtime/runtime_admission.py:89`，由 `429b68783b`（2026-09-17 07:36，
st-govmap 车道）落地，而真源 `architecture_model/contracts/error_code_registry.yaml`
头声明 `ai_autonomy: human_gated` ⇒ 按宪章 §3.4「他会话在途违规不代修」+ RULE-RULING
「不自登记他人语义」双条拦着，**修法只有其 owner 或 Owner**。剔除这一条，两轮均 7341/7341。

**范围外附加面**（这两项不在上表 12 目录内，单列以免被读成"包含在内"）：
`tests/governance/integration/test_all_scripts.py -k validate_config_integrity` =
`1 passed, 4 xpassed, 0 failed in 16.00s`；`python scripts/governance/d1_structure/validate_config_integrity.py --warn-only`
直跑 `exit 0 / 8.1s`（GT-13 治本前同命令 121s，快层 xfail 的成因就是它跑不完）。

**本台账自身的盲区（写下来，免得被当成"全链路已绿"读）**：范围=回测/组合/风控/治理门禁
四条链的 12 目录，**未含** altdata/research、frontend/dashboard、data 域与实盘下单链路
（后者按 §5 high 域 Owner 门位，R-H5E-1 pre-trade 仍在册）。所以本台账支持的句子是
"这三条链在冻结树上连续两轮无我方可归因红"，不支持"全仓全绿"。
