# ZephyrAlpha 首关 — AI 入群唯一入口

> v0.20.0 | Python >=3.11 | Pydantic V2 | ~24K 资产 | 健康 A(94.0)
> 本文件由 IDE 自动注入每个 AI 对话。全读完再开工。

---

## 第一原则：AI消费优先（TRAE-057）

> **所有产出物 MUST 以 AI可发现、可解析、可执行 为第一优先级。**
> 格式分工铁律：规则/元数据=YAML，叙事/蓝图=Markdown，代码=十五字段头部。
> 真源：[trae_057_ai_consumer_first.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_057_ai_consumer_first.yaml)

---

## 第二原则：向内收铁律（TRAE-060）

> **100% AI 开发场景下的顶层收敛约束。动手前 MUST 直读真源，禁止同步复制。**
> 真源：[trae_060_inward_consolidation.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_060_inward_consolidation.yaml)（frozen, safety_level: H, ai_autonomy: immutable_core）

| 原则 | 一句话 | 违反后果 |
|------|--------|---------|
| ① 能现成不创造 | 动手前先 Grep / 搜注册表 / 查 CapabilityLookup；能扩展不新建；禁止同步复制 | 造第二真源→漂移 |
| ② 创造必全自动 | 永久脚本事件驱动 + 自动运行 + 自动维护 + 自动关闭；禁止手工触发，禁止时间触发（cron/Timer/CircadianScheduler） | 必然被遗忘→漂移 |
| ③ 第一性原理治本 | 先问元问题该不该存在 / 能否删除或合并；治本不治标（MTH-006） | 症状反复 |

**判定流程、禁止清单、GATE-VOCAB 门禁、例外清单** → 全部见真源 §1-§6。本节仅入口指向，不复制内容（复制=同步=违反原则①）。

> 元约束：本原则同样约束规则自身的传播——规则的消费方（含本文件）必须直读 trae_060 真源，禁止摘抄片段充当第二真源。

---

## 资产全景

| 资产 | 数量 | 发现入口 |
|------|:---:|------|
| 模块 | 4,639 | `python scripts/governance/extract_depgraph.py --summary` |
| 脚本 | 483 | `scripts/script_manifest.yaml` |
| 门禁 | 43 | `src/zephyr/governance/rule_enforcement/_registry.yaml` |
| 蓝图 / 模板 | 60 / 13 | `docs/03_modules/blueprint_registry.yaml` / `template_registry.yaml` |
| Agent Skill | 22 | `data/capability_cards/` (skill_*.yaml) |

### ⚠️ 真源文件（SSoT）— 任何 AI 进项目 MUST 先知道

| 真源 | 绝对路径 | 说明 |
|------|---------|------|
| **路径全景图+依赖全景图（唯一真源）** | PostgreSQL `depgraph`（localhost:5432） | PostgreSQL 16，设计态+运行态合一。**⚠️ 禁止裸连！** MUST 用 `extract_depgraph.py --summary/--domains/--top` 提取子集，或通过 `get_depgraph_pg_connection()` 有限查询。详见 RULE-SIXTEEN |
| **数据库清单（4库唯一真源）** | `docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml` | INFRA-DB-001~004（governance.db/ChromaDB/depgraph/DuckDB OLAP）。**禁止在其它文档同步数据库清单**。market.duckdb 已于2026-07-01废弃。详见 AGENTS.md §11.0 |
| **真源分类铁律（TRAE-062）** | `docs/01_policies_and_standards/rules/trae_062_ssot_classification.yaml` | 两类真源：①规则数据→YAML 真源（DB 只读缓存）②架构数据→PostgreSQL DB 真源。**禁止凭记忆推断**，写入数据前 MUST 查此规则。详见 AGENTS.md §11.0.2 |

**绝对禁止**：引用 `project-entity-depgraph-v3-domain-draft.yaml`/`target_path_tree.yaml`/`archive/` 下归档文件/`project-path-tree.yaml`/`functional_domain_registry.yaml` 作为真源（均已被合并或为派生物）。

> 创建任何新功能前，MUST 先搜索 483 脚本 + 4,639 模块中是否已有覆盖。不搜索 = 违规。

---

## PRE-OP：任何操作前必须通过的强制检查

| 你要做什么 | 必须先问自己 | 答案=NO时的强制命令 |
|-----------|-------------|-------------------|
| **进入新 session** | Phase 0 检查全部 GREEN？守护进程在跑？ | `session_startup()` + `python scripts/ide_health_service.py --status` → running=false→`--start` |
| **创建新文件** | 文件已在注册表中？ | `python scripts/scaffold.py module/script/gate ...` |
| **修改已有文件** | 拿到锁了？pre_write_gate 通过？ | `python scripts/governance/d5_architecture/pre_write_gate.py <file>` → exit 0 → `python scripts/lock_files.py acquire <file> <session_id>` |
| **删除任何文件** | 文件每一行内容在别处还有？ | RULE-THREE 三步审判 → 全通过才能删 |
| **任何新功能 / 自动化系统** | 已有脚本覆盖？自动化已过两轨分类？ | 搜 registry_of_registries.yaml → 复用决策；自动化走 RULE-FIFTEEN |
| **结束 session** | 锁释放？临时文件清？ | `python scripts/lock_files.py release-all` + 零残留扫描 |
| **处理任何任务** | 有对应 Agent Skill？ | 查看 `data/capability_cards/` 目录（skill_*.yaml）→ 匹配 → Read |
| **读取/修改 depgraph** | 用 extract_depgraph.py 提取？不是直接裸连？ | `extract_depgraph.py --summary`（读取）/ `apply_depgraph.py --batch`（修改）。连接用 `get_depgraph_pg_connection()` |

跳过任何一步 → 可能产生孤儿文件、死锁、重复轮子。

---

## FIRST-READ：入项目第一步

```
1. 读 docs/registry_of_registries.yaml → 了解全项目有什么
2. 提取 depgraph 摘要：python scripts/governance/extract_depgraph.py --summary（PostgreSQL 数据库 depgraph，禁止裸连。详见 RULE-SIXTEEN）
2.1 确认数据库就绪：4 库清单（INFRA-DB-001~004）见 infrastructure_registry.yaml（真源，详见 AGENTS.md §11.0）
3. 读 docs/03_modules/_system_master/blueprint.md §0 → 定位子系统任务域
4. 读本文件（project_rules.md）→ 了解怎么做事
5. 按需定位具体注册表 → 开工
6. 创建任何代码/脚本/模块前 → MUST 读 trae_056_module_creation_workflow.yaml（11阶段完整工作流程）
7. 查 CapabilityLookup 确认能力是否已存在（防重复造轮子）→ CapabilityLookup().find("关键词")
```

| ❌ 绝对禁止 | 后果 |
|---------|------|
| 跳过 registry_of_registries.yaml 直接开工 | 不知道已有模块/脚本 → 重复造轮子 |
| 创建新文件前不查 registry_of_registries.yaml | 孤儿文件 |
| 看到注册表中 `?` 条目不管不问 | 注册表过期——认知偏差累积 |

---

## RULE-ZERO：文件锁协议
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**触发**：对任何文件执行写入操作前。

### 强制三步

```
BEFORE WRITE → CHECK  → python scripts/lock_files.py check <file>
            FREE? → ACQUIRE → python scripts/lock_files.py acquire <file> <session_id> --task "<简述>"
            LOCKED? → STOP. 报告用户：文件被 <owner> 锁定。
AFTER WRITE  → RELEASE → python scripts/lock_files.py release <file> <session_id>
```

### 自动门禁（v2.0 — DM-409）

`pre_write_guard(file, session_id, task)` 锁定抛 `FileLockedError`；`with LockGuard(...)` 自动释放；CLI: `lock_files.py guard-write <file> <session> --task <desc>`。

### claim 前移协议（Edit 阶段覆盖治本，2026-06-30）

**触发**：AI session 处理任何文件前（Edit/Write 之前）。强制流程：①CLAIM `git_commit.py --session <id> --files <f1,f2> --claim-only` ②CHECK `python scripts/governance/d5_architecture/pre_write_gate.py <file> --session <id>`（overlap 检测）③EDIT ④COMMIT `git_commit.py --session <id> --files <f> --message ...`。

| 场景 | 模式 |
|------|------|
| 单 AI 对话 | 模式 A：直接锁 + claim（lock_files.py + git_commit.py --claim-only） |
| ≥2 AI 并发同文件 | 模式 A'：claim 前移 + overlap 检测 MUST |
| ≥2 AI 并发高风险 | 模式 B：StagingArea 草稿 MUST（write_draft/commit） |

claim 前移是常态软约束防线，StagingArea 是高风险兜底（物理隔离 Edit 产物），两者分层不冲突。session_id：`session-YYYYMMDD-NNN`。批量：逐个 check → 全 FREE 后逐个 acquire → 全改完后逐个 release。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 跳过 check 直接写文件 | 编码损坏、修改丢失 |
| ❌ | check 返回 LOCKED 后仍然写文件 | 覆盖其他对话的工作 |
| ❌ | Edit 前不 --claim-only 声明 | overlap 检测无数据，防线失效 |
| ❌ | 写完后不执行 release | 死锁——其他对话永远抢不到锁 |
| ❌ | 多 AI 并发时直接 git commit 绕过 StagingArea | 文件被覆盖、pre-commit 卡死 |
| ❌ | 使用 git commit --no-verify 绕过 pre-commit | 违反 trae_029 |

---

## 执行环境与文件卫生（RULE-ONE + RULE-FIVE + RULE-SEVENTEEN）
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml（RULE-ONE/RULE-FIVE）；RULE-SEVENTEEN 无独立 YAML。

**RULE-ONE：Python 脚本并发写入安全** — 任何产出文件的 standalone Python 脚本 MUST 原子写入（tmp+replace）：
```python
tmp_path = f"{OUTPUT_PATH}.{os.getpid()}.tmp"
try: open(tmp_path, "w", encoding="utf-8").write(content); os.replace(tmp_path, OUTPUT_PATH)
except PermissionError: try: os.remove(tmp_path) except OSError: pass
```
禁止 `open(fixed_path,"w")` / `Path.write_text()` 直接写最终文件——多实例运行时阻塞/崩溃。与 RULE-ZERO 互补：RULE-ZERO 防 AI 同时编辑同文件，RULE-ONE 防脚本多实例互斥卡死。

**RULE-FIVE：临时文件零残留** — session 创建 `_temp*`/`_check*`/`_fix*`/`_phase_*`/`_deep*`/`_construction*`/`_rebuild*`/`_audit*` 前缀文件时，结束前 MUST 二选一处置：有持续价值→归档+注册；一次性→物理删除。每日安检：`python scripts/lock_files.py status`。

**RULE-SEVENTEEN：禁止 PowerShell 语法** — RunCommand 仅允许裸命令（`python <脚本>.py`/`python scripts/git_commit.py ...`/`python -m pytest`/`python -m zephyr.<mod>`）。禁止：管道`|`、引号嵌套、`$`变量、cmdlet、`>`重定向、`;`串联、裸`git`命令（用 `git_guard.py <子命令>`，但 `commit` 子命令是裸透传会被阻断，commit 用 `git_commit.py`）。文件操作映射：读→Read、写→Write/Edit、搜索文件→Glob、搜索内容→Grep、删除→DeleteFile。复杂逻辑写 `.py` 脚本。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 脚本中 `open(fixed_path,"w")` 直接写最终文件 | 多实例运行时阻塞/崩溃 |
| ❌ | 在根目录创建临时 .py/.yaml/.json 脚本 | 孤儿文件 |
| ❌ | session 关闭时根目录仍有 `_temp*` 等文件 | 磁盘垃圾累积 |
| ❌ | RunCommand 使用 PowerShell 管道/引号嵌套/重定向 | 引号出错 + 中文乱码 + 文件损坏 |
| ❌ | 裸 `git` 命令 | Trae 硬编码审查弹窗 |

---

## 创建/搜索/注册铁律（RULE-TWO + RULE-FOUR + RULE-EIGHT）
**YAML真源**: → 参见 rules/trae_002_anti_orphan_search_first.yaml（RULE-TWO/RULE-EIGHT）、rules/trae_001_file_operation_security.yaml（RULE-FOUR）

**RULE-EIGHT：搜索先行** — 任何新代码创作前 MUST 三步：①关键词全局搜索（SearchCodebase+Grep）②注册表精确匹配（registry_of_registries.yaml）③复用决策（完全覆盖→直接用 / 80%→扩展 / 50%→重构+扩展 / 0%→scaffold新建）。放弃新建时 MUST 写 `[REUSE-DECISION] 放弃新建 <X>，因为已有 <Y> 覆盖了 <Z>`。

**RULE-FOUR：创建即注册** — scaffold.py 是唯一创建入口。绕过它 = 孤儿。
```
python scripts/scaffold.py module <包名> <模块名>    # 创建模块 → 注册 __init__.py __all__
python scripts/scaffold.py script <路径>              # 创建脚本 → 注册 script_manifest.yaml
python scripts/scaffold.py gate <ID>                  # 创建门禁 → 注册 _registry.yaml
python scripts/scaffold.py rule <主题_描述>           # 创建规则文件（ARCH-037，命名 trae_NNN_<主题>_<描述>.yaml）
```
修改已有文件不走 scaffold——走 RULE-ZERO 锁协议。**完整创建工作流程（11阶段）** 见 [TRAE-056](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml)。包名约束：`scripts/` 下禁止使用与 `src/zephyr/` 同名的顶层包名（防 import 命名空间冲突）。

**RULE-TWO：反孤儿功能** — 产出新功能时 MUST 自问五问：谁调用？谁发现？谁维护？谁校验？谁更新？注册判定原则：注册管理单元（不注册文件），满足任一条件即需注册——独立生命周期/跨域消费者/需要治理决策/无法自然发现。已有可靠自然发现机制的豁免（tests/pytest自动发现、config/代码路径引用、普通文档/目录结构）。

### 强制集成清单

| 产出类型 | 必须集成到 |
|----------|-----------|
| 新 `.py` 脚本（`scripts/` 下） | `script_manifest.yaml` 注册 + `phase_manager` gate 引用 |
| 新 `.py` 模块（`src/zephyr/` 下） | 对应 `__init__.py` 导出 + 至少一个 import 引用点 |
| 新门禁/gate | `phase_manager.py` PHASE_SEQUENCE 注册 + `_registry.yaml` |
| 新增 RULE-* | `rule-registry.md` TRAE 域强制登记 → `python scripts/governance/sync_rule_registry.py` |
| 新 `.md` 文档 | frontmatter MUST 含 `ttl` 字段；过程性文档默认落 `docs/_working/`（ttl=task_bound） |

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 用 Write/SearchReplace 直接创建新文件 | 孤儿文件——无注册 |
| ❌ | 不搜索直接创建新脚本 | 重复造轮子 |
| ❌ | 搜到了但不复用，坚持新建 | 两个版本分叉维护 |
| ❌ | 创建 .py 文件但不注册到 script_manifest.yaml | 孤儿脚本 |
| ❌ | 创建 `.md` 文档但 frontmatter 不含 `ttl` 字段 | 文档无保留期，无法识别过期/清理 |

---

## 删除/跨蓝图/瘦身收敛（RULE-THREE + RULE-ELEVEN + RULE-TWELVE）
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml（RULE-THREE）、rules/trae_052_cross_blueprint_change_cleanup.yaml（RULE-ELEVEN/RULE-TWELVE）

**RULE-THREE：删除前置确认** — 删之前先证明它该死。不能证明 → 不许删。三步审判：①登记检查（manifest/registry/__init__.py 引用？git log 存在？）YES→有价值，只能 refactor/rehome ②重复检查（有完全相同文件且已注册？）双 YES→可删 ③逐行价值检查（每行内容在别处存在？删除后有无引用报错？）ALL 无价值→可删。临时文件也须过 STEP 3。**零消费者≠无价值**——看功能价值，不看消费者数量。

**RULE-ELEVEN：跨蓝图变更通知** — 修改任何蓝图接口契约（Collection 名、API 签名、数据格式、依赖方向）时 MUST 三步：①Grep 全项目识别消费方 ②同步更新所有消费方蓝图 §4 + 代码常量/调用 ③端到端测试。向后兼容变更（新增 Collection/新增可选参数）不触发。

**RULE-TWELVE：项目瘦身与自动清理** — 发现候选清理物 → 先判定价值 → 有价值则接通系统（归属蓝图+对齐依赖图+对齐路径树+对齐代码表头），无价值才走 RULE-THREE 删除。禁止仅凭"零消费者"或"版本旧"判定。清理触发链：Phase COMPLETED→归档任务卡；Session CLOSED→删 `_temp*`/清 cache；新蓝图全覆盖旧版→归档旧版。清理后验证三步：`audit_registration.py`→exit 0、`generate_project_path_tree.py --write`、（架构升级期间禁止 `generate_project_depgraph.py`，用 `extract_depgraph.py --summary` 替代）。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 跳过审判三步，直接删除 | 误删有价值文件 |
| ❌ | 看到文件名像"临时"就直接删 | 可能是唯一一份全量审计报告 |
| ❌ | 只改提供方，不改消费方 | 消费方静默降级/断路 |
| ❌ | 仅凭"零消费者"判定删除 | 误删有价值的安全/治理组件 |
| ❌ | 清理后不跑验证三步 | 注册表/路径树/依赖图漂移 |

---

## 任务粒度与并行化（RULE-SIX + RULE-SEVEN）
**YAML真源**: → 参见 rules/trae_003_task_granularity_threshold.yaml（RULE-SIX）、rules/trae_004_parallel_atomic_transaction.yaml（RULE-SEVEN）

**RULE-SIX：任务粒度边界** — 八指标机械门（任一 YES → 走任务系统）：①>50 行新代码 ②修改>3 文件 ③需读蓝图/设计文档 ④数据库 Schema 变更 ⑤depgraph 操作 ⑥消费者影响>50 文件 ⑦跨域操作 ⑧多步骤施工>3 步。全 NO → 直接做。**RULE-ZERO-TASK**：任务卡 MUST 通过 `TaskRepository.create(allow_direct_create=True)` 写入 SQLite，禁止手写 `.md` 建卡。建卡双触发：用户主动 OR 阈值自动。建卡来源：蓝图拆解（`BlueprintDecomposer.decompose`）/ Bug修复/架构债务/重构任务。建卡后立刻施工——不等用户确认。

**粒度标准（一卡一任务）**：`deliverables`≤1、`files_in_scope`≤3、`acceptance` 独立验收点≤1、跨 Phase 禁止。任务卡=施工图+审计记录，**永久保留禁止删除**（数据库触发器 `prevent_hard_delete` 阻止 DELETE；只能软删除且限 Owner 审批）。`transition(COMPLETED)` 时如有 error/failure，MUST 有 MTH-006 `root_cause_analysis` 记录，无记录→拒绝完成。

**RULE-SEVEN：脚本并行化 + 创建即自测** — 机械判定（任一 YES → MUST ThreadPoolExecutor）：A.`for`+subprocess.run/Popen B.`for`+多文件独立读写 C.`for`+多URL/API请求。**只用 ThreadPoolExecutor**（I/O 密集型，GIL 无影响），不用 multiprocessing。`max_workers=8`。创建即自测：`python <脚本> --warn-only` → exit 0 才能声明完成，exit≠0 必须立即修复。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 八指标任一触发但不建卡 | 无法跨 session 追溯 |
| ❌ | 手写 .md 建卡（.md 仅伴读副本） | 绕过 SQLite 真源 |
| ❌ | 新建脚本用 `for` 循环串行跑子进程 | 40 分钟跑不完 → 卡死 |
| ❌ | 用 `multiprocessing` 而非 `ThreadPoolExecutor` | Windows spawn 开销大 + pickle 陷阱 |
| ❌ | 创建脚本后不跑 `--warn-only` 自测 | 留下崩溃脚本 |

---

## RULE-NINE：强制资产认知
**YAML真源**: → 参见 rules/trae_005_modification_governance.yaml

进项目 MUST 先了解全盘资产规模与健康状态。读 `data/asset_index/unified_asset_index.yaml` → 知道总资产/健康评分/孤儿率。不知道系统有多大 = 盲目施工。

| ❌ 绝对禁止 | 后果 |
|---------|------|
| 跳过资产盘点直接开工 | 对系统规模无认知 |
| 不知道资产健康状态就修改核心模块 | 可能覆盖 DEGRADED 模块 |

---

## RULE-TEN：治理施工流程（14步统一流程）
→ 详细 14 步流程、轻量模式、三方对齐、治理顺序、依赖方向铁律见 [`onboarding_detail.md §RULE-TEN`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
**YAML真源**: → 参见 rules/trae_005_modification_governance.yaml
**摘要**：非平凡变更 MUST 遵循 14 步统一流程（分析设计→施工→安全验证→收尾对齐），跳步=违规。仅结构变更可用 5 步轻量模式。三方对齐（全景图+蓝图+代码头部）是 STEP 12 强制验证。治理顺序从根到叶：跨包违规→God模块→孤儿→blueprint_id→稳定性→测试。新建功能域 MUST Owner 书面审批。

---

## RULE-THIRTEEN：任务卡粒度铁律
→ 粒度门禁、拆卡四规则、状态转换、深挖病根见 [`onboarding_detail.md §RULE-THIRTEEN`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
**YAML真源**: → 参见 rules/trae_003_task_granularity_threshold.yaml
**摘要**：一卡一任务，独立可验证。R1-R6 任一触发即拆卡（deliverables>1/files_in_scope>3/acceptance多验收点/跨施工目标/description结构词缺失/description<100字）。超粒度可 `auto_split_task` 自动拆分。`transition(COMPLETED)` 有 error MUST 有 root_cause_analysis。

---

## RULE-FOURTEEN：根目录清爽铁律
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**核心**：根目录是项目门面——只允许白名单目录/文件存在。任何不在白名单中的 = 垃圾。

**白名单**：IDE/AI=`.editorconfig`/`.traeignore`/`.vscode/`/`.trae/`/`AGENTS.md`；版本控制/CI=`.gitignore`/`.gitattributes`/`.pre-commit-config.yaml`/`.github/`/`.importlinter`；Python=`pyproject.toml`/`requirements*.txt`/`py.ini`；运行时=`.env.example`/`config/`/`Dockerfile`/`docker-compose.yml`；文档=`README.md`/`LICENSE`/`CONTRIBUTING.md`/`SECURITY.md`；源码/文档/数据=`src/`/`scripts/`/`tests/`/`tools/`/`docs/`/`architecture_model/`/`specs/`/`data/`/`models/`/`infra/`/`demos/`/`session_logs/`；运行时自动生成=`.ailocks/`/`.aidrafts/`/`.audit_cache/`/`.mypy_cache/`/`.ruff_cache/`/`.runtime/`/`.zephyr/`/`.zephyr_secure/`/`logs/`/`reports/`/`_journals/`。

**系统级禁令**：①禁止 mkdir-only（MUST 同时写入内容）②每次检查禁止生成独立报告文件（O(1)：覆盖/追加单日志/写库）③Skill 查找失败禁止持久化 `NONEXISTENT-SKILL_*.json`（失败=不落盘）④禁止自动保存 AI 会话提示词到 `_prompts/`（禁用或设 max+TTL 自动清理）。

Session 关门时 MUST 根目录审计：ls 根目录 → 逐项对照白名单 → 不在白名单 → **删**。

---

## RULE-FIFTEEN：自动化双轨判定
**YAML真源**: → 参见 rules/trae_053_automation_dual_track.yaml

> **⚠️ 架构裁定（2026-06-26）**：定时轨（🕐 CircadianScheduler）禁止使用，仅用事件驱动 + CI 批量兜底。`CircadianScheduler` 的 register_task/start/stop/save_state 均为 no-op。原"定时轨"任务应迁移至事件驱动（boot_hooks）或 CI schedule。

**核心**：任何新建/改造自动化系统，MUST 通过两轨分类 + 实现验证。单轨实现 = 未完成。

**施工三步**：①判定归属（🕐 定时=全项目扫描/重操作/外部同步/缓存维护；⚡ 事件=状态变更响应/即时校验；🕐+⚡ 双轨=关键校验）②实现（⚡ 事件→`boot_hooks.py` 中 `hook_registry.register` 或 `event_bus.subscribe`；🕐 已禁用）③验证（`python scripts/ide_health_service.py --status` → 触发事件后 check hooks 执行）。

| ❌ 绝对禁止 | 后果 |
|---------|------|
| 新建自动化系统不判定两轨归属 | 盲目挂在单一轨 |
| 全项目重扫描挂在事件驱动上 | 每次文件变更扫全项目＝拖死 |
| 实现事件轨但不注册到 hook_registry | 触发条件满足了但钩子不响 |

---

## RULE-SIXTEEN：depgraph 程序化访问协议
→ 详细 Schema 变更协议、强制操作序列、变更 JSON 格式见 [`onboarding_detail.md §RULE-SIXTEEN`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
**YAML真源**: → 参见 rules/trae_054_depgraph_access_protocol.yaml
**摘要**：depgraph 在 PostgreSQL 16（localhost:5432, db=`depgraph`, user=`zephyr`, schema v18, 25表）。连接入口 `from zephyr.governance.depgraph_schema import get_depgraph_pg_connection`。禁止裸 `psql`/`sqlite3`。读取用 `extract_depgraph.py --summary/--domains/--modules/--top/--paths/--stats`；修改用 `apply_depgraph.py --batch`（MUST 先 pg_dump 备份，事务内执行失败自动 ROLLBACK）。Schema 变更遵循 DDL-as-Code：改 `_DDL_*` 声明→加 `_MIGRATIONS`→跑 `init_db()`→过 `verify_schema_health.py`。禁止拆分 depgraph（跨域关系丢失）或全表注入 AI 上下文（55M tokens）。

---

## RULE-EIGHTEEN：连续两次审查零问题
**YAML真源**: → 参见 rules/trae_042_meta_rule_standard.yaml §std_011_dual_review_protocol

**核心**：任何文件变更声明完成前，MUST 连续两次审查零问题。防止"执行完不检查"或"只检查一次"导致的幻觉和漂移残留。

**适用范围**：任务卡 COMPLETED / 代码修改交付 / 规则文件修改 / 文档更新 / 配置变更 / Session 关门——全部触发。纯只读操作豁免。

**强制三步**：①第一次审查（按文件类型审查清单逐项）→ 问题数=0？YES→进② / NO→修复→重执① ②第二次审查（完整重执审查清单，非仅查修复点）→ 问题数=0？YES→进③ / NO→修复→从①开始 ③连续两次零问题→通过→可声明完成。

**计数规则**：连续两次中间不能有任何问题；第二次 MUST 完整执行（禁止只查第一次的问题点）；审查 MUST 覆盖全部变更；伪造审查结果=违规。

**规则文件修改额外要求**：修改 trae_XXX.yaml 后，除连续两次审查外，MUST 额外执行 **std_010_rule_review_simulation**（模拟新AI测试）：冷启动模拟+幻觉检测+漂移检测+模拟执行+连续两次模拟零问题才通过。

| ❌ 绝对禁止 | 后果 |
|---------|------|
| 声明完成但未执行连续两次审查 | 幻觉和漂移残留 |
| 第二次审查只查第一次的问题点 | 修复可能引入新问题 |
| 修改规则文件后跳过模拟新AI测试 | 规则可能产生幻觉/漂移 |

---

## RULE-NINETEEN：先裁定后确认（MTH-009 显化）
→ 详细三段输出格式、MTH-007 决策质量四问、防幻觉十八条见 [`onboarding_detail.md §RULE-NINETEEN`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
**YAML真源**: → 参见 rules/trae_025_methodology_decision.yaml §mth_009
**摘要**：AI 遇到任何决策（方案选择/范围裁定/触发条件判定/多选项权衡）MUST 先给出专业裁定+理由（三段：分析过程→裁定结果→确认请求），再请 Owner 确认。裁定前 MUST 完成 MTH-007 四问（埋雷检查/容量检查/专业对标/最终建议）。禁止直接问"你选哪个"把决策权推给 Owner。防幻觉十八条（#1-#18）：结构追溯（[BLUEPRINT]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS] 等十五字段头部）+ 行为约束（禁止占位符/编辑优先/最小变更/假设显式化）+ 输出验证（步骤验证门/导入验证/自审闭环/新代码必测）+ 安全防护（安全最低通过/计划先行/跨文件影响检查/上下文新鲜度）。

---

## RULE-TWENTY：写完即提交（防丢失铁律）

**核心**：AI 完成文件修改后 MUST 在 session 结束前 git commit。未提交的代码 = 不存在 = 会被 git reset/checkout 冲掉。

> **GATE-COMMIT-GW 门禁**：全项目禁止裸 `git commit`。pre-commit hook 会阻断所有非 `--no-verify` 的 commit。所有 commit MUST 经 GitCommitGateway（CLI 入口 `python scripts/git_commit.py`）。`git_guard.py commit` 是裸透传会被阻断——勿用。

### 强制流程

| 时机 | 动作 |
|------|------|
| 文件修改完成 | `python scripts/git_guard.py add <具体文件>`（禁止 `add -A`/`add .`） |
| commit 提交 | `python scripts/git_commit.py --session <id> --files <f1,f2> --message "type(scope): desc"`（唯一合法 commit 入口） |
| 任务卡 transition(COMPLETED) | 自动 `git_commit.py --session <id> --files <files> --message <msg>` |
| session 结束前 | 确认 `python scripts/git_guard.py status` 干净 |

`git_commit.py --message` 内部用 `git commit -F` 文件提交（绕过 PowerShell 解析）。多行/含特殊字符用 here-string 传递。

| ❌ 绝对禁止 | 后果 |
|---------|------|
| 写完代码不提交 | git 操作冲掉工作区，代码丢失 |
| `git_guard.py add -A`/`add .` 批量添加 | 混入敏感文件或无关变更 |
| 裸 `git commit` 或 `git_guard.py commit` | GATE-COMMIT-GW 阻断 exit 1 |

---

## 规则本身的规则

| # | 规则 |
|---|------|
| 1 | `.trae/rules/` 目录 AI 不可写入。规则是 IMMUTABLE——想改规则 → 报告 Owner，不要自己改 |
| 2 | 禁止凭记忆判断任何 API/库/函数/模块/路径的存在性。不确定 → 先搜。搜不到 = 不存在，搜到了 = 存在。**双向搜索** |
| 3 | 幻觉检测器在监控。引用不存在的路径/ID/命令 → 会被阻断 |

---

## 产出规则

| # | 规则 |
|---|------|
| 1 | 新建脚本中任何 `for + subprocess/I/O` → **强制 ThreadPoolExecutor(max_workers=8)** |
| 2 | Python 写文件统一用原子写入（tmp+replace）。禁止 `open(path,"w")` 直接写 |
| 3 | 写完脚本 → 立刻跑 `python <脚本> --warn-only` 自测 |
| 4 | **极简产出**：表格>命令>一句话>段落。不写"为什么"和"对标"。**优化安全协议见 onboarding_detail.md §10.6** |
| 5 | **防幻觉头部**——新建/修改代码文件 MUST 包含十五字段头部（[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]）。缺失 = 孤儿文件 |
| 6 | **根因追踪（MTH-006）**——遇到 bug/失败/漂移 → MUST 追问到底（非固定5次，问到底）。治根判定：修复后同类问题不再产生 + 作用于设计层面 + 可泛化为原则 |
| 7 | **搜索先行复用决策**——新建功能前 MUST 搜索已有覆盖。放弃新建时 MUST 写 `[REUSE-DECISION]` |
| 8 | **编码安全**——Python `open(path,'w')` 禁止省略 `encoding='utf-8'`；禁止 Trae+Cursor 同时打开同一文件 |
| 9 | **修改原则**——发现事实错误 → 直接修正，禁止添加"之前为什么是错的"解释段；单个 real number 原则 |
| 10 | **审计前置**——任何涉及文件变更的任务完成后 MUST 执行 `python scripts/governance/run_all.py --depth quick` |
| 11 | **资产认知（RULE-NINE）**——进项目 MUST 先读 `data/asset_index/unified_asset_index.yaml` |

---

## 强制集成对照表

| AI 要做什么 | 必须先跑什么 | 不跑会怎样 |
|------------|-------------|-----------|
| **写入任何文件** | `python scripts/governance/d5_architecture/pre_write_gate.py <文件>` | exit≠0 → 禁止写入 |
| **创建新文件** | `python scripts/scaffold.py module/script/gate <参数>` | 绕开 → 孤儿文件 |
| **删除任何文件** | RULE-THREE 三步审判 → 全通过才能删 | 误删有价值文件 |
| 修改 `src/zephyr/` 源码 | `python -m pytest tests/ --collect-only -q` | 语法错误 → 禁止提交 |
| 修改 YAML 契约/AGENTS.md/project_rules.md | `check_contract_code_drift.py` / `validate_load_path_integrity.py --check` / `sync_rule_registry.py` | 契约/LoadPath/rule-registry 断裂 → 禁止提交 |
| 任何文件变更后 | `python scripts/governance/run_all.py --depth quick` | 有发现 → 先修再关 |
| **新建/改造自动化系统** | RULE-FIFTEEN 两轨判定（仅事件轨+CI兜底） | 单轨实现或未注册 → 禁止关闭任务 |
| **读取/修改 depgraph** | `extract_depgraph.py --summary`（读取）/ `apply_depgraph.py --batch`（修改）→ 详见 RULE-SIXTEEN | 裸连/读 archive → 数据过时 |
| **涉及数据库连接函数** | MUST 先读 AGENTS.md §11.4。PG 用 `get_depgraph_pg_connection`（F1/F4），SQLite 用 `get_db_connection`（F2/F3） | 误用入口 → `no such table` |
| **三方对齐** | ①`diagnose_depgraph.py` ②蓝图 frontmatter↔代码 ③代码头部↔引用 | 任一方过时 → 禁止关闭任务 |
| **创建/删除/移动文件后** | `python scripts/governance/generate_project_path_tree.py --write` | 路径树过时 → 禁止关闭任务 |
| 安全敏感变更 | `python scripts/governance/d6_security/scan_secret_leak.py` | 泄漏 → 硬阻断 CI |
| 回滚/撤销 | `python scripts/rollback.py preflight` → CLEAN → `rollback.py <cmd>` | preflight FAIL → 禁止回滚 |
| 高风险操作（批量/安全） | `EscalationEngine().evaluate(RuleCategory, desc)` | 可能执行应变 blocked 的操作 |
| 多Agent/MCP 委托 | `DelegationEngine.delegate(event, strategy)` | 死锁/循环委托/深度溢出 |
| LLM API 调用前 | `BudgetEngine().pre_flight_check(operation_id, tokens, cost)` | 超预算 → 降级或拒绝 |
| 施工前/后：知识 | `kb.search("<关键词>")` / `kb.write(topic, content, provenance)` | 重复造轮子 / 知识丢失 |
| **脚本运行慢/卡死** | PERF-001 十项检查清单 → `trae_034_task_card_standard.yaml §9` | 凭直觉改 → 治标不治本 |

---

## Session 冷启动序列

进入项目后 MUST 按以下顺序执行（不可跳过、不可重排）：

```
STEP 0.5 — Drift 健康检查（信息性不阻断）: audit_registration.py --full --compact / git stash list >5 warning / git status --porcelain >50 warning
STEP 1   — 读 docs/registry_of_registries.yaml + docs/03_modules/template_registry.yaml
STEP 1.2 — 提取 depgraph 摘要：extract_depgraph.py --summary（PostgreSQL，禁止裸连）+ 确认 4 库就绪（infrastructure_registry.yaml）
STEP 1.5 — 读 docs/03_modules/_system_master/blueprint.md §0
STEP 2   — 读本文件（project_rules.md）
STEP 3   — Session Continuity 恢复
STEP 4   — Phase Manager（46 门控）+ 资产盘点 unified_asset_index.yaml + Skill 发现 data/capability_cards/
STEP 4.7~4.14 — KB自检/Escalation/Drift Detector/RBAC/Rollback/Budget/Audit Trail/A2A 激活
STEP 4.15 — DepMap: ⚠️ 禁止 generate_project_depgraph.py（丢失手工数据）。用 extract_depgraph.py --summary
STEP 4.16 — 三方对齐验证: diagnose_depgraph.py + 蓝图 frontmatter + 代码头部
STEP 5   — 按需定位具体注册表 → 开工
```

不完成 STEP 1-4.16 = 不可开工。

---

## Session 开关门

**进门**: 读 registry_of_registries.yaml → 读 `_system_master/blueprint.md` §0 → 查看 `data/capability_cards/` → 记录 session 起点 commit（`record_session_start_commit.py <session_id>`）→ **启动大脑系统**（见 onboarding_detail.md §五 STEP 0.5）

**关门**（缺一不可）:
```
0. SessionRegistry().list_active() → assert len<=1
1-3. lock_files.py release-all <session_id> → cleanup → status 确认 CLEAN
4. sc.generate_and_save(session_id, task_repo)
5. sync_rule_registry.py
6. auto_sync_all_registries.py --all --warn-only + generate_project_path_tree.py --write + generate_path_ownership_map.py --write + data/cache/ 清空
7. 零残留扫描: _temp*/_check*/_fix*/_phase_* → 全部删除
8. 根目录审计: 对照 RULE-FOURTEEN 白名单 → 不在 → 删
9-10. .py 文件合法三目录检查 + 废墟引用检查（删过文件/目录 → 确认无引用）
11. run_all.py --depth full + post_doc_review_check <session_id>（tampering_detected=true → RED 拒绝关门）
12. TaskRepository().list_by_status('IN_PROGRESS') → assert len==0
13. 写 Session Log（session_logs/YYYY/MM/session-YYYYMMDD-NNN.yaml）
```

---

## 触发关键词 → Agent Skill 路由

完整 22 个 skill 路由见 `data/capability_cards/`（skill_*.yaml）。常用入口：

| 关键词 | Skill |
|--------|-------|
| database / sql / migration | SKILL-DOM-DBS-001 |
| mcp / server / tool | SKILL-DOM-MCP-001 |
| feedback / 根因 / 慢脚本 / 卡死 / PERF-001 | SKILL-DOM-FBL-001 |
| gate / rule / policy | SKILL-DOM-GAT-001 |
| blueprint / architecture | SKILL-DOM-BLU-001 |
| audit / drift / run_all / 全量审计 | SKILL-DOM-DRF-001 / AOR-001 |
| rollback / undo / checkpoint | SKILL-DOM-RBK-001 |
| security / lsg / injection | SKILL-DOM-LSG-001 |
| task / taskcard | SKILL-DOM-TSK-001 |
| fix / self-heal / 修复 | SKILL-DOM-AFX-001 |

加载: Read `data/capability_cards/<skill_id>.yaml`（其余 telemetry/dedup/budget/behavioral/vector/knowledge/permission/context/a2a 见目录）

---

## 不确定时的默认路径

```
1. 撞门禁 → 读门禁输出 → 按输出说的做
2. 不知道有什么 → 搜 registry_of_registries.yaml
3. 不知道怎么做 → 查看 data/capability_cards/ → 匹配关键词 → Read 对应 yaml
4. 不知道能不能改 → 搜 docs/01_policies_and_standards/
```

---

## 关键标准速查

| 领域 | 标准 | module_id |
|------|------|-----------|
| 治理决策 | `rules/trae_024_methodology_diagnosis.yaml` | PS-STD-011 |
| 代码构建 | `rules/trae_010_code_naming_organization.yaml` | GOV-ENG-001 |
| 脚本质量 | `scripts/governance/quality_standard.md` | SCRIPT-QUALITY-001 |
| AI 压缩工作流 | `rules/trae_030_doc_numbering_metadata.yaml` | GOV-DOC-011 |
| Session 状态机 / 门禁 / 事故响应 / VC 入口 | `docs/.../operational/vibe_coding/`（session-state-runbook / gate-runbook / incident-runbook / index） | OPS-VC-001~005 |
| 模板 | `docs/03_modules/template_registry.yaml` | REG-TEMPLATE-001 |

> 详细规则、施工指导、方法论参考 → 见 [`.trae/rules/onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
