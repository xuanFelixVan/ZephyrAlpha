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

真实执行面：`.pre-commit-config.yaml` 68 个 hook（全 `repo: local`）+ `commit_gates/` 116 个模块
（113 已注册，`_reference_helpers.py` / `capability_lookup_bypass_policy.py` / `gate_repo.py` 3 个非门禁）。

### 1.2 【验伪】两条"已转硬阻断"的门禁，脚本根本没有入口——运行=空操作

`.pre-commit-config.yaml` 头部过渡计划原文（`:19,21`）：
"GATE-13 (蓝图重叠检测) → ✅ 已转硬阻断（args --ci）"、"GATE-14 (AI权限注册表) → ✅ 已转硬阻断（args --ci）"。

AST 实测（`gate_executability.json`，53 条 script 型门禁中仅 3 条无 `__main__`，其中 2 条即此二者）：

| 门禁 | 脚本 | 实测 |
|---|---|---|
| GATE-13 | `scripts/governance/d11_compliance/validate_blueprint_overlap.py`（108 行） | **无 `__main__`、无 argparse**。文件最后一句是 `:102 return [], 0`。`python … --ci` → rc=0、**0 行输出**（实测 `gate_head_run.json`） |
| GATE-14 | `scripts/governance/d5_architecture/validators/validate_authority_registry.py`（173 行） | 同上：无 `__main__`。`--ci` → rc=0、0 行输出 |

即：注册表 `status: active` + 配置头"已转硬阻断" + 实测 rc=0 三重口径下，这两条门禁
**对任何输入都不会失败**——因为 `run_validation()` 从未被调用。

### 1.3 【验伪】两条门禁的触发面与输入面同时不存在

| 门禁 | hook `files:`（决定何时触发） | 脚本实际读的输入 | 实测存在性 |
|---|---|---|---|
| GATE-14 | `^docs/01_policies_and_standards/_registry/catalogs/ai-autonomy-authority-registry\.md$` | `REGISTRY_PATH = docs/01_policies_and_standards/policies/ai_autonomy_authority_registry.md`（`:24-30`） | **两个路径都不存在**；真源实为 `…_registry/catalogs/ai_autonomy_authority_registry.yaml`（`.yaml`，异目录异扩展名） |
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
- `_build_own_scope` 定义：`commit_gates/_diff_helpers.py:438-460`，`files` 与 `session_id` 皆空 → `return None`（`:455`）"退化为旧行为扫全量"，registry 读异常 → 降级 files-only（`:462` 注释"fail-open 红线"）。

即字段本身准确，但**生成方式是被禁止的 substring 判定**，一致属侥幸（任何在注释里提到
`_build_own_scope` 的 gate 都会被误标 True）。

### 1.6 作用域口径落差：26 条标 own_scope=True，其中 25 条注释自述"全量/全仓"

实测 `commit_gate_scope.json`：`claims_full_scan_n>0 且 ast_call_count>0` = **25 条**（占 26 条 own_scope=True 的 96%）。典型：

| 门禁 | 自述 | 实际实现 |
|---|---|---|
| `ASYNCIO-RUN-IN-CONTEXT:8` | "检测 `src/zephyr/` **全量**代码(.py)新增行…阻断" | staged ∩ 本 session（`:438-460`） |
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
| ⑥数据字段（HEAD 实跑台账） | 49 条 script 门禁 HEAD 实跑 rc 分布：**rc=0 24 条 / rc=1 20 条 / rc=2 5 条**；其中 0 输出行数（standalone 无输入嫌疑）：`GATE-PROTECTED-PATHS`、`GATE-ALGO-FLOW`、`GATE-NAMING`、`GATE-14`、`GATE-13`、`GATE-SRC-NO-DATA`、`GATE-VMS-SSOT`、`GATE-NO-TESTS-UNIT`、`GATE-NO-COMMIT-DERIVED`、`GATE-GEN-NO-REALTIME-TIME` | `gate_head_run.json` |

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

## 5 子节点清单（还能挖的）

1. 49 条实跑中 10 条 0 输出（standalone 无输入嫌疑），需带 `--staged`+伪造 index 复测才能区分"真干净/没输入"。
2. 55 条 pre-commit 门禁的 `own_scope` 字段缺失 = 该维度对读注册表者不可见（本文只核了 in-process 侧）。
3. `.pre-commit-config.yaml:1-45` 的 warn-only→硬阻断"过渡时间表"是**手写**的，与 hook args 无机器绑定；GATE-22 记"仍 warn-only 骨架（当前 SKIP）"，需实跑核实 SKIP 语义。
4. `scripts/governance/run_gate_chain.py`（GATE-VOCAB 用它串两条子检查、逗号传参）——串链内任一子件失败是否被聚合掩盖。
5. 3 条 rc=2（用法错误类：`GATE-TEST`/`GATE-RETURN-CONTRACT`/`GATE-WORKTREE-OPS-TELEMETRY`/`GATE-ENCODING`）：注册 entry 与脚本 argparse 不匹配，值得逐条查是否等价"从未真正跑过"。
6. `.runtime/gate_audit/worktree_skip.jsonl`（实测存在，3756 字节，末次 09-08）——worktree 侧 skip 计数的真实触发史。

## 6 封矿判定

**部分封矿（本节点主脉已枯，留 3 条活脉）**：

- 枯：注册表账面/字段一致性（§1.1、§1.5 已穷举，own_scope 侥幸准确）；派生件 registry 消费族（§1.4 已逐个定性，含 1 条 `return []`、1 条 BOOTSTRAP 认账）；"脚本无入口"族（AST 全量 53 条，命中 2 条，无更多）。
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
| 4 | GT-5/GT-7 | 结论失真/口径相反，属"能看到但看错" | 2 文件 | 低-中 |
| 5 | GT-4/GT-6 | 需 Owner 裁定（派生件是否回库、348 HIGH 清偿策略） | 跨派生件治理战役 | 高，勿单批做 |
| 6 | GT-8/GT-9/GT-10 | 结构性可观测性，随门禁遥测一并做 | 分散 | 低 |
