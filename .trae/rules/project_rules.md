# ZephyrAlpha 首关 — AI 入群唯一入口

> v0.20.0 | Python >=3.11 | Pydantic V2 | ~24K 资产 | 健康 A(94.0)
> 本文件由 IDE 自动注入每个 AI 对话。全读完再开工。

---

## 资产全景

| 资产 | 数量 | 发现入口 |
|------|:---:|------|
| 模块 | 4,639 | `python scripts/governance/extract_depgraph.py --summary` |
| 脚本 | 483 | `scripts/script_manifest.yaml` |
| 门禁 | 43 | `src/zephyr/governance/rule_enforcement/_registry.yaml` |
| 蓝图 | 60 | `docs/03_modules/blueprint_registry.yaml` |
| 模板 | 13 | `docs/03_modules/template_registry.yaml` |
| Agent Skill | 22 | `data/capability_cards/` (skill_*.yaml) |

### ⚠️ 真源文件（SSoT）— 任何 AI 进项目 MUST 先知道

| 真源 | 绝对路径 | 说明 |
|------|---------|------|
| **架构全景图+依赖全景图（唯一真源）** | `D:/ZephyrAlpha/data/databases/depgraph.db` | SQLite 数据库，设计态+运行态合一。由上至下：域→模块→依赖设计→path_design命名规则；由下至上：文件→域+模块+蓝图。包含 path_design 段（路径设计权威）+ capacity声明(1500模块)。**不存在其他依赖图文件，任何其他 depgraph 文件都是旧版或归档**。**⚠️ 禁止直接 Read！AI 必须用 `python scripts/governance/extract_depgraph.py --summary/--domains/--top` 提取子集。详见 RULE-SIXTEEN** |
| **治理数据库** | `D:/ZephyrAlpha/data/databases/governance.db` | SQLite，治理元数据+任务卡+成本+审计日志（26表）。任务系统SSoT。访问：`python -c "from zephyr.governance.task_repo import TaskRepository; r=TaskRepository(); print(len(r.list_all()))"` |
| **业务时序数据库** | `D:/ZephyrAlpha/data/databases/market.duckdb` | DuckDB，业务时序数据（Tick/K线/因子/订单/持仓/风控，7表+1视图）。访问：`python -c "import duckdb; con=duckdb.connect(r'D:/ZephyrAlpha/data/databases/market.duckdb', read_only=True); print(con.execute('SHOW TABLES').fetchall())"` |
| **迁移登记表** | `D:/ZephyrAlpha/docs/02_enterprise_architecture/migration_registry.yaml` | 每个需要迁移的文件的旧路径→新路径映射。搬家任务卡的唯一真源 |

**绝对禁止**：
- ❌ 引用 `project-entity-depgraph-v3-domain-draft.yaml`（已合并入真源，保留为副本）
- ❌ 引用 `target-path-tree.yaml`（不存在，path_design 在 depgraph 内）
- ❌ 引用 `archive/` 下的任何旧版 depgraph 文件作为真源
- ❌ 把 `project-path-tree.yaml` 当作独立真源修改（已合并至架构全景图）
- ❌ 把 `functional_domain_registry.yaml` 当作域定义唯一真源（域定义已合并至架构全景图，registry 保留为兼容副本）

> 创建任何新功能前，MUST 先搜索 483 脚本 + 4,639 模块中是否已有覆盖。不搜索 = 违规。

---

## PRE-OP：任何操作前必须通过的强制检查

| 你要做什么 | 必须先问自己 | 答案=NO时的强制命令 |
|-----------|-------------|-------------------|
| **进入新 session** | Phase 0 检查全部 GREEN？守护进程在跑？FLE 在跑？ | `from zephyr.governance.phase_manager import session_startup; r=session_startup(); print(r['next_action'])` + `python scripts/ide_health_service.py --status` → running=false→`python scripts/ide_health_service.py --start` |
| **创建新文件** | 文件已在注册表中？ | `python scripts/scaffold.py module/script/gate ...` |
| **修改已有文件** | 拿到锁了？pre_write_gate 通过？ | `python scripts/governance/pre_write_gate.py <file>` → exit 0 → `python scripts/lock_files.py acquire <file> <session_id>` |
| **删除任何文件** | 文件每一行内容在别处还有？ | RULE-THREE 三步审判 → 全通过才能删 |
| **任何新功能** | 已有脚本/模块覆盖？ | 搜 registry_of_registries.yaml → Grep → 复用决策 |
| **新建/改造自动化系统** | 已通过两轨分类？ 🕐/⚡/🕐+⚡？ | RULE-FIFTEEN 施工三步 → 对照分类表 → 实现 → 验证 |
| **结束 session** | 锁释放？临时文件清？ | `python scripts/lock_files.py release-all` + 零残留扫描 |
| **处理任何任务** | 有对应 Agent Skill？ | 查看 `data/capability_cards/` 目录（skill_*.yaml）→ 匹配 → Read 对应 yaml |
| **读取/修改 depgraph** | 用 extract_depgraph.py 提取？不是直接 Read/Write？ | `python scripts/governance/extract_depgraph.py --summary` 提取子集；修改用 `apply_depgraph.py --batch`。直接 Read 157MB → OOM 崩溃 |

跳过任何一步 → 可能产生孤儿文件、死锁、重复轮子。

---

## FIRST-READ：入项目第一步

```
1. 读 docs/registry_of_registries.yaml → 了解全项目有什么
2. 提取 depgraph 摘要：`python scripts/governance/extract_depgraph.py --summary`（架构全景图+依赖图唯一真源 D:/ZephyrAlpha/data/databases/depgraph.db，禁止直接 Read。→ 项目域架构+目录结构+依赖关系+capacity声明。详见 RULE-SIXTEEN）
2.1 确认三库就绪：depgraph.db（依赖图）+ governance.db（治理/任务）+ market.duckdb（业务时序）。路径均在 `data/databases/`。depgraph 用 extract_depgraph.py；governance 用 TaskRepository；market 用 duckdb.connect(read_only=True)
3. 读 docs/03_modules/_sys_master/blueprint.md §0 → 定位子系统任务域
4. 读本文件（project_rules.md）→ 了解怎么做事
5. 按需定位具体注册表 → 开工
```

| # | 绝对禁止 | 后果 |
|---|---------|------|
| ❌ | 跳过 registry_of_registries.yaml 直接开工 | 不知道已有模块/脚本 → 重复造轮子 |
| ❌ | 创建新文件前不查 registry_of_registries.yaml | 孤儿文件 |
| ❌ | 看到注册表中 `?` 条目不管不问 | 注册表过期——认知偏差累积 |

---

## RULE-ZERO：文件锁协议
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**触发**：对任何文件执行写入操作前。

### 强制三步

```
BEFORE WRITE → CHECK  → python scripts/lock_files.py check <file>
               ↓
            FREE? → ACQUIRE → python scripts/lock_files.py acquire <file> <session_id> --task "<简述>"
               ↓
            LOCKED? → STOP. 报告用户：文件被 <owner> 锁定。
               ↓
AFTER WRITE  → RELEASE → python scripts/lock_files.py release <file> <session_id>
```

### 自动门禁（v2.0 — DM-409）

**问题**：上述三步依赖AI自觉执行，DM-291事件证明AI可能跳过。

**方案**：`lock_files.py` v2.0 新增 `pre_write_guard()` + `LockGuard` + `guard-write` 子命令。

| 方式 | 用法 | 场景 |
|------|------|------|
| Python API | `pre_write_guard(file, session_id, task)` | AI工具调用链集成 |
| Context Manager | `with LockGuard(file, session_id, task):` | Python脚本内自动acquire/release |
| CLI | `python scripts/lock_files.py guard-write <file> <session> --task <desc>` | 命令行写前检查 |

`pre_write_guard()` 在文件被锁时抛出 `FileLockedError`（而非静默通过）。`LockGuard` 在 `with` 块退出时自动释放锁。

### session_id 格式

`session-YYYYMMDD-NNN`，从 `session_logs/` 目录找编号。

### 批量操作

1. 先对 N 个文件逐个 `check`
2. 全部 FREE 后，逐个 `acquire`
3. 全部改完后，逐个 `release`

一个被锁 → 释放已抢到的，等全部可抢再开工。

### 紧急情况

```
python scripts/lock_files.py cleanup    # 清理 TTL 过期的死锁
python scripts/lock_files.py status     # 确认清理结果
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 跳过 check 直接写文件 | 编码损坏、修改丢失 |
| ❌ | check 返回 LOCKED 后仍然写文件 | 覆盖其他对话的工作 |
| ❌ | 用 Write 工具绕过 lock_files.py | 锁协议完全失效 |
| ❌ | 写完后不执行 release | 死锁——其他对话永远抢不到锁 |

---

## RULE-ONE：Python 脚本并发写入安全
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**适用**：任何产出文件的 standalone Python 脚本。

### 强制写入模式

```python
import os
tmp_path = f"{OUTPUT_PATH}.{os.getpid()}.tmp"
try:
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp_path, OUTPUT_PATH)
except PermissionError:
    try: os.remove(tmp_path)
    except OSError: pass
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 脚本中 `open(fixed_path, "w")` 直接写最终文件 | 多实例运行时阻塞/崩溃 |
| ❌ | `Path.write_text(fixed_path)` | 同上 |
| ❌ | 新写脚本跳过此模式 | 被其他 AI 并发调用时卡住 |

### 与 RULE-ZERO 的关系

| | RULE-ZERO（锁协议） | RULE-ONE（并发写入） |
|---|---|---|
| 适用场景 | AI 用 IDE 工具改源文件 | Python 脚本产出文件 |
| 触发条件 | Write/SearchReplace | `open(path, "w")` / `write_text()` |
| 解决问题 | 防止两个 AI 同时编辑同一文件 | 防止脚本多实例互斥卡死 |

两者互补，不可互相替代。新建脚本 MUST 同时遵守两条规则。

---

## RULE-TWO：反孤儿功能
**YAML真源**: → 参见 rules/trae_002_anti_orphan_search_first.yaml

**触发**：AI 产出任何新功能时。

### 强制五问

| # | 问题 | 不满足 → 处置 |
|---|------|-------------|
| 1 | 谁调用它？入口在哪？ | 没有入口 → 不能关闭任务 |
| 2 | 谁发现它？下一个 AI session 怎么知道？ | 没有发现机制 → 必须先注册 |
| 3 | 谁维护它？放在哪个模块/目录下？ | 没有归属 → 不能落盘 |
| 4 | 谁校验它？有 gate 检查吗？ | 没有校验 → 必须添加 gate |
| 5 | 谁更新它？模板/清单/注册表已更新？ | 没有 → 必须更新 |

### 注册判定原则

**注册管理单元，不注册文件。** 需要注册 = 满足以下任一条件：

| 条件 | 含义 |
|------|------|
| 独立生命周期 | 可被独立创建/修改/删除，不依附于其他东西 |
| 跨域消费者 | 被不在同一目录/模块/子系统下的东西消费 |
| 需要治理决策 | 谁能改、何时改、改了影响谁——需要显式回答 |
| 无法自然发现 | 没有命名约定/import链/目录结构等自然机制 |

**豁免**：已有可靠自然发现机制的管理单元，不需要额外注册表。

| 文件类型 | 需要注册？ | 发现机制 |
|----------|:---:|------|
| `scripts/*.py` | ✅ | 无自然发现路径，必须靠注册表 |
| `src/zephyr/<pkg>/*.py` | ✅ | import 链 + `__all__` |
| `gates/*.yaml` | ✅ | GateEngine 运行时从注册表加载 |
| 蓝图（blueprint.md） | ✅ | 定义代码应该长什么样，治理级 |
| 策略/标准 | ✅ | 全项目引用，治理级 |
| `tests/*.py` | ❌ | pytest 命名约定自动发现 |
| 普通文档（非蓝图非策略） | ❌ | 目录结构 + frontmatter |
| `config/*.yaml` | ❌ | 代码中显式路径引用 |
| `data/*.yaml`/`*.json` | ❌ | 代码中显式路径引用 |

### 强制集成清单

| 产出类型 | 必须集成到 |
|----------|-----------|
| 新 `.py` 脚本（`scripts/` 下） | `script_manifest.yaml` 注册 + `phase_manager` gate 引用 |
| 新 `.py` 模块（`src/zephyr/` 下） | 对应 `__init__.py` 导出 + 至少一个 import 引用点 |
| 新门禁/gate | `phase_manager.py` PHASE_SEQUENCE 注册 + `_registry.yaml` |
| 新设计模式/方法论 | `project_rules.md` 或 `AGENTS.md` + `rule-registry.md` TRAE 域 |
| 新增 RULE-* | `rule-registry.md` TRAE 域强制登记 → `python scripts/governance/sync_rule_registry.py` |
| 新配置/数据文件 | 使用方代码中的显式路径引用 |
| 新 CLI 工具 | `script_manifest.yaml` + 用法写入相关 blueprint |
| 新测试文件（`tests/` 下） | 治理锚定表头（A_test 6字段简化版）+ pytest 命名约定。豁免注册表登记 |

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 创建 .py 文件但不注册到 script_manifest.yaml | 孤儿脚本 |
| ❌ | 写了新功能但不建立任何调用入口 | 死代码 |
| ❌ | 新增 gate 只写名字不写实现 | 假门禁 |
| ❌ | 完成任务卡后不检查"下游有没有人用" | 孤儿功能 |

---

## RULE-THREE：删除前置确认
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**核心**：删之前先证明它该死。不能证明 → 不许删。

### 三步审判

```
STEP 1 登记检查：在 manifest/registry/__init__.py 中被引用？git log 中存在？
  YES → 有价值，不能删。只能 refactor/rehome。

STEP 2 重复检查：有另一个文件与它内容完全相同？那个文件在正确位置且已注册？
  双 YES → 真正重复，可删。
  YES+NO → 两个都没注册！先决定保留哪个并注册。

STEP 3 逐行价值检查：每行内容在其他地方存在？删除后有无代码引用此路径报错？
  ANY 有价值 → 保留并注册。
  ALL 无价值 → 可以删。
```

**临时文件也须过 STEP 3**：`_temp*` / `_check*` / `_phase_*` / `_audit*` 删除前必须确认内容价值。

**零消费者≠无价值**——判断删除看功能价值，不看消费者数量。零消费者可能因自动化管线未接通（客观原因），非代码无意义。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 跳过审判三步，直接删除 | 误删有价值文件 |
| ❌ | 看到文件名像"临时"就直接删 | 可能是唯一一份全量审计报告 |
| ❌ | 批量删除时不对每个文件逐一审判 | 误删混入 |
| ❌ | 删除后不检查废墟引用 | 死链接——CI 崩溃、import 失败 |

---

## RULE-FOUR：创建即注册
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**核心**：scaffold.py 是唯一创建入口。绕过它创建的文件 = 孤儿。

### scaffold.py 用法

```
python scripts/scaffold.py module <包名> <模块名>    # 创建模块
python scripts/scaffold.py script <路径>              # 创建脚本
python scripts/scaffold.py gate <ID>                  # 创建门禁
```

### 注册表映射

| 文件类型 | 创建命令 | 自动注册到 |
|----------|---------|-----------|
| `src/zephyr/<pkg>/<name>.py` | `scaffold.py module <pkg> <name>` | `<pkg>/__init__.py` `__all__` |
| `scripts/<path>/<name>.py` | `scaffold.py script <path>` | `scripts/script_manifest.yaml` |
| `src/zephyr/gates/<id>.yaml` | `scaffold.py gate <id>` | `src/zephyr/governance/rule_enforcement/_registry.yaml` |

**scaffold 自动完成**：查重 → 创建（temp-file + atomic rename）→ 注册 → 返回路径+导入命令。

**修改已有文件不走 scaffold**——走 RULE-ZERO 锁协议。

**决策分叉**：新建文件 → scaffold；不新建文件（修改已有）→ RULE-ZERO 锁协议。

### 孤儿检测

```
python scripts/governance/audit_registration.py           # 报告孤儿
python scripts/governance/audit_registration.py --json    # JSON 输出
python scripts/governance/audit_registration.py --fix     # 交互式修复
```

返回码 `0` = CLEAN，`1` = 有孤儿。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 用 Write/SearchReplace 直接创建新文件 | 孤儿文件——无注册 |
| ❌ | 绕过 scaffold 创建后"事后补注册" | 窗口期 → 可能没补 → 依然是孤儿 |
| ❌ | 创建后不验证 scaffold 输出的导入命令 | 注册可能有语法错误 |
| ❌ | 跳过 SSoT 冲突检查直接创建 | 功能重复 → 命名混乱 |
| ❌ | 对已有自然发现机制的文件类型强制要求注册表登记 | 注册表膨胀，维护成本 > 治理收益 |

---

## RULE-FIVE：临时文件零残留
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**触发**：AI session 创建了以下前缀文件时：`_temp*` / `_check*` / `_fix*` / `_phase_*` / `_deep*` / `_construction*` / `_rebuild*` / `_audit*`

### 强制二选一处置（session 结束前 MUST 完成）

| 路径 | 条件 | 操作 |
|------|------|------|
| **归档** | 文件有持续使用价值 | 移动到标准目录 + 注册到对应注册表 |
| **删除** | 一次性检查/临时验证/实验脚本 | 物理删除，不留残骸 |

### 每日安检

```
python scripts/lock_files.py check-session <session_id>
```

发现任何匹配 → 必须先处置再施工。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 在根目录创建临时 .py/.yaml/.json 脚本 | 孤儿文件 |
| ❌ | session 关闭时根目录仍有 `_temp*` 等文件 | 磁盘垃圾累积 |
| ❌ | "这个脚本可能以后有用，先留着" | 永远不会有人回来用它 |
| ❌ | 跳过每日安检直接开工 | 在垃圾堆上盖楼 |

---

## RULE-SIX + RULE-ZERO-TASK：任务粒度边界
**YAML真源**: → 参见 rules/trae_003_task_granularity_threshold.yaml

### 八指标机械门

```
├─ 指标 1: 预计产生 > 50 行新代码？ → YES → 走任务系统
├─ 指标 2: 涉及修改 > 3 个文件？ → YES → 走任务系统
├─ 指标 3: 需要读取蓝图/设计文档？ → YES → 走任务系统
├─ 指标 4: 是数据库 Schema 变更？ → YES → 走任务系统
├─ 指标 5: depgraph.db 操作(INSERT/UPDATE/DELETE)？ → YES → 走任务系统
├─ 指标 6: 消费者影响 > 50 个文件？ → YES → 走任务系统
├─ 指标 7: 跨域操作？ → YES → 走任务系统
├─ 指标 8: 多步骤施工 > 3 个步骤？ → YES → 走任务系统
└─ 全 NO → 直接做，不走任务系统
建卡后立刻施工——不等用户确认
```

**RULE-ZERO-TASK**：任务卡 MUST 通过 `TaskRepository.create()` 写入 SQLite，禁止手写 `.md` 建卡。建卡触发 = 用户主动 OR 八指标阈值触发。蓝图拆解是建卡来源之一，非唯一路径。

**任务系统双触发机制**：

| 触发方式 | 说明 | 入口 |
|----------|------|------|
| 用户主动触发 | 用户明确要求建卡 | `TaskRepository.create(allow_direct_create=True)` → TaskCard → SQLite |
| 阈值自动触发 | 八指标任一YES | AI按MTH-009先裁定后确认→建议建卡→Owner确认→`TaskRepository.create(allow_direct_create=True)` |

**建卡来源**（不再限于蓝图）：

| 来源 | 入口 |
|------|------|
| 蓝图拆解 | `BlueprintDecomposer.decompose(blueprint_path)` → TaskCard → SQLite |
| Bug修复/架构债务/代码扫描/重构任务 | `TaskRepository.create(allow_direct_create=True)` → TaskCard → SQLite |

### 边界案例对照表

| 场景 | 触发指标 | 建卡？ |
|------|---------|:---:|
| 设计新类/模块（150 行新代码） | 指标1 ✅ | ✅ |
| 修复拼写错误 | 全不触发 | ❌ |
| 修 CI 红了的 bug（涉及 5 个文件） | 指标2 ✅ | ✅ |
| 给数据库加字段 | 指标4 ✅ | ✅ |
| 批量重命名 20 个文件的变量 | 指标2 ✅ | ✅ |
| 运行一条 SQL migration | 全不触发 | ❌ |
| 更新蓝图版本号（1 行 1 文件） | 全不触发 | ❌ |
| 写 100 行新脚本 | 指标1 ✅ | ✅ |
| 清理根目录临时文件 | 全不触发 | ❌ |
| 重构 pipeline（需读蓝图+大量新代码） | 指标1+3 ✅ | ✅ |
| 新增 gate 门禁 | 指标1+3 ✅ | ✅ |
| depgraph.db INSERT 新域 | 指标5 ✅ | ✅ |
| 大规模 import 更新（>50 文件） | 指标6 ✅ | ✅ |
| 跨域模块迁移 | 指标7 ✅ | ✅ |

### 粒度标准（一卡一任务）

| 字段 | 上限 | 超限处置 |
|------|:---:|------|
| `deliverables` | ≤ 1 | MUST 拆分为多张卡 |
| `files_in_scope` | ≤ 3 | MUST 拆分为多张卡 |
| `acceptance` 独立验收点 | ≤ 1 | 人工判定拆分 |
| 跨 Phase | 禁止 | MUST 拆分为多张卡 |

**任务卡 = 施工图+审计记录**：施工细节写在任务卡 description 里（不限字数），不写在蓝图里。蓝图只写设计（是什么/为什么），任务卡写施工（怎么做/改哪里/改成什么）。**任务卡永久保留，禁止删除**——COMPLETED/CANCELLED 的卡是审计链、依赖链、知识沉淀的唯一真源。删除已完成卡 = 删除 git log。实现：数据库触发器 `prevent_hard_delete` 阻止任何 DELETE 操作；只能软删除（is_deleted=1，仅限 Owner 审批）。

**深挖病根**: `transition(COMPLETED)` 时如有 error/failure，MUST 有 MTH-006 `root_cause_analysis` 记录。无记录 → 拒绝完成。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 八指标任一触发但不建卡 | 无法跨 session 追溯 |
| ❌ | 全不触发但建卡 | 任务卡膨胀 |
| ❌ | 建卡后等用户确认再开工 | 打断用户流——建卡是静默操作 |
| ❌ | 用"感觉"判断是否建卡 | 模糊标准 → 每次结果不同 |
| ❌ | 手写 .md 建卡（.md 仅伴读副本） | 绕过 SQLite 真源 |

---

## RULE-SEVEN：脚本并行化 + 创建即自测
**YAML真源**: → 参见 rules/trae_004_parallel_atomic_transaction.yaml

### 并行化判断标准（机械判定）

```
├─ 指标 A: for 循环中对多个目标调用 subprocess.run/Popen？ → YES → MUST ThreadPoolExecutor
├─ 指标 B: for 循环中对多个文件执行独立读写？ → YES → MUST ThreadPoolExecutor
├─ 指标 C: for 循环中对多个 URL/API 发起网络请求？ → YES → MUST ThreadPoolExecutor
└─ 全 NO？ → 可以串行
```

### 正确写法

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

_MAX_WORKERS = 8

def run_all_tasks(items: list[Item]) -> list[Result]:
    results: list[Result] = []
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(_run_one, item): item for item in items}
        for future in as_completed(futures):
            results.append(future.result())
    return results
```

### 错误写法（绝对禁止）

```python
for item in items:
    subprocess.run(["python", "script.py", item])  # ❌ 串行 = 卡死
```

**只用 ThreadPoolExecutor**，不用 multiprocessing（I/O 密集型，GIL 无影响，线程优于进程）。

### 创建即自测

```
python <脚本路径> --warn-only   # 至少跑一次
exit 0 → 通过 → 可关闭任务
exit ≠ 0 → 必须立即修复 → 重新自测 → 直到 exit 0
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 新建脚本用 `for` 循环串行跑子进程 | 40 分钟跑不完 → 卡死 |
| ❌ | 用 `multiprocessing` 而非 `ThreadPoolExecutor` | Windows spawn 开销大 + pickle 陷阱 |
| ❌ | 创建脚本后不跑 `--warn-only` 自测 | 留下崩溃脚本 |
| ❌ | 自测发现问题但不修 | 崩的脚本永远崩 |

---

## RULE-EIGHT：搜索先行
**YAML真源**: → 参见 rules/trae_002_anti_orphan_search_first.yaml

### 强制三步（任何新代码创作前 MUST 执行）

```
STEP 1: 关键词全局搜索
  → SearchCodebase(自然语言) + Grep（scripts/ + src/zephyr/ + tests/）

STEP 2: 注册表精确匹配
  → 读 registry_of_registries.yaml → 找相关 REG-* → 对照已有条目

STEP 3: 复用决策（四选一）
  → 完全覆盖 → 直接用
  → 80% 覆盖 → 扩展已有
  → 50% 覆盖 → 重构已有 + 扩展
  → 完全不覆盖 → 走 scaffold.py 新建
```

### 复用证据记录

放弃新建时 MUST 写：`[REUSE-DECISION] 放弃新建 <X>，因为已有 <Y> 覆盖了 <Z>`

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 不搜索直接创建新脚本 | 重复造轮子 |
| ❌ | 搜到了但不复用，坚持新建 | 两个版本分叉维护 |
| ❌ | 新建后不写 [REUSE-DECISION] | 下一个 AI 不知道你为什么新建 |
| ❌ | "我觉得没有"替代"我搜了没有" | 直觉错误率 >> 搜索错误率 |

---

## RULE-NINE：强制资产认知
**YAML真源**: → 参见 rules/trae_005_modification_governance.yaml

进项目 MUST 先了解全盘资产规模与健康状态。

```
读 data/asset_index/unified_asset_index.yaml
→ 知道总资产/健康评分/孤儿率
→ 不知道系统有多大 = 盲目施工
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 跳过资产盘点直接开工 | 对系统规模无认知 |
| ❌ | 不知道资产健康状态就修改核心模块 | 可能覆盖 DEGRADED 模块 |
| ❌ | 不知道孤儿率就开始清理 | 可能误删仍在使用的组件 |

---

## RULE-TEN：治理施工流程
**YAML真源**: → 参见 rules/trae_005_modification_governance.yaml

**触发**：对项目结构做任何非平凡变更——移动模块、拆分包、重构依赖、批量修改标签。

### 五步强制流程

```
STEP 1  依赖图推演 → 模拟变更后的依赖链，确认不会产生新循环/堵塞
STEP 2  蓝图归属   → 确认目标包有蓝图，模块的 [BLUEPRINT] 指向正确
STEP 3  导入路径映射 → 列出所有受影响的 import 语句（Grep 全项目）
STEP 4  执行操作   → 按推演验证过的计划操作
STEP 5  验证       → 重新生成 depgraph + path-tree + diagnose，确认无回退
```

### 治理因果链（从根到叶，不按数量从大到小）

```
第1层 架构决定 → 第2层 结构重构 → 第3层 元数据对齐 → 第4层 质量补全
```

| 顺序 | 治理项 | 为什么先做 |
|:---:|--------|-----------|
| 1 | 跨包违规（架构重构） | **根因**：shared/ 职责不清 |
| 2 | God模块分解 | 依赖#1：包边界清晰后才知道该拆什么 |
| 3 | 孤儿模块消理 | 依赖#1+#2：重构后很多孤儿自然获得消费者 |
| 4 | 空 blueprint_id | 依赖#1：重构后归属可能变化 |
| 5 | 稳定性/自治违规 | 依赖#1+#4：架构和标签都稳定后才能准确判断 |
| 6 | 测试覆盖 | **最后做**：先重构再写测试 |

### 价值判定（RULE-THREE 补充）

**零消费者≠无价值。** 判断删除/移动看功能价值，不看消费者数量。`kill_switch.py` 零消费者≠能删。

### 域归属铁律

**模块归入已有域（当前 39 域，见 `extract_depgraph.py --summary`），不新建域。** 新建功能域/子域 MUST 经 Owner 书面审批。AI 遇到模块无域归属时，优先根据 `[BLUEPRINT]` 字段归入已有域；只有穷尽所有已有域仍无法合理归属时，才可提议新建域并等待 Owner 审批。

> 详见 [onboarding_detail.md §15](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 不推演直接移动模块 | 引入新循环依赖，系统堵塞 |
| ❌ | 按数量从大到小治理 | 前面的决定可能让后面的问题消失，白做 |
| ❌ | 用"零消费者"判定删除 | 误删有价值的安全/治理组件 |
| ❌ | 先补测试再重构 | 重构改代码，测试白写 |
| ❌ | **新建功能域/子域未经 Owner 审批** | 域膨胀失控——模块应归入已有域（当前 39 域），新建域必须 Owner 书面同意 |

---

## RULE-ELEVEN：跨蓝图变更通知
**YAML真源**: → 参见 rules/trae_052_cross_blueprint_change_cleanup.yaml

**触发**：修改任何蓝图的接口契约（Collection 名、API 签名、数据格式、依赖方向）时。

### 强制三步

```
STEP 1  识别消费方 → Grep 全项目引用该接口的所有蓝图/代码
STEP 2  同步更新   → 所有消费方蓝图 §4 + 代码常量/调用 同步修改
STEP 3  验证       → 端到端测试确认消费方仍能正常调用
```

### 判定标准

| 变更类型 | 是否触发 | 示例 |
|---------|:-------:|------|
| Collection 名变更 | ✅ | `ke_entries` → `knowledge` |
| API 签名变更 | ✅ | `search(query)` → `search(query, collections)` |
| 数据格式变更 | ✅ | ScoredHit 新增字段 |
| 依赖方向变更 | ✅ | 可选→必须 |
| 新增 Collection | ❌ | 向后兼容 |
| 新增可选参数 | ❌ | 向后兼容 |

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 只改提供方，不改消费方 | 消费方静默降级/断路 |
| ❌ | 改了接口但不 Grep 消费方 | 遗漏消费方→生产故障 |
| ❌ | 消费方蓝图不更新 §4 契约 | 下个 AI session 看到旧契约→幻觉 |

---
---

## RULE-TWELVE：项目瘦身与自动清理
**YAML真源**: → 参见 rules/trae_052_cross_blueprint_change_cleanup.yaml

**核心**：发现候选清理物 → 先判定价值 → 有价值则接通系统，无价值才删除。禁止仅凭"零消费者"或"版本旧"判定。

### 价值判定标准

```
发现候选清理物
├─ 有价值？
│   ├─ YES → 接入系统
│   │        ├─ 归属到蓝图（更新 blueprint §4）
│   │        ├─ 对齐依赖图（⚠️ 架构升级期间禁用 generate_project_depgraph.py，用 extract_depgraph.py）
│   │        ├─ 对齐路径树（path-tree --write）
│   │        └─ 对齐代码表头（[BLUEPRINT]/[MODULE] 十一字段）
│   └─ NO  → 走 RULE-THREE 三步审判 → 确认无价值 → 删除
│
├─ 过时蓝图版本？→ 新版本缺失旧版本独有内容？→ 保留/合并，不删
│               └─ 新版本完全覆盖？→ 归档
│
└─ 零消费者？→ 判功能价值（不看消费者数）
              └─ 有价值 → 接入；无价值 → 删除
```

### 清理触发链

| 触发条件 | 清理动作 | 验证 |
|---------|---------|------|
| Phase COMPLETED | 该 Phase 所有 TaskCard → 归档到 `data/archive/taskcards/`（按需创建） | `audit_registration.py` |
| TaskCard COMPLETED | 中间 checkpoint → 删除，保留最终 | — |
| Session CLOSED | `_temp*` / `_check*` 等前缀文件 → 删除 | RULE-FIVE |
| Session CLOSED | `data/cache/` → 清空 | — |
| 新蓝图发布 + 旧版全覆盖 | 旧蓝图版本 → 归档 | 内容对比 |
| 审计发现零价值孤儿 | 删除 + 刷新注册表 | `audit_registration.py` |
| 审计发现僵尸引用 | 清理注册表残留 | `audit_registration.py` |
| brain 重建后 | 合并旧 embeddings | — |

### 清理后验证三步

```
1. python scripts/governance/audit_registration.py → exit 0
2. python scripts/governance/generate_project_path_tree.py --write
3. ⚠️ 架构升级期间禁止运行——会覆盖 depgraph.db。用 extract_depgraph.py --summary 替代
# python scripts/governance/generate_project_depgraph.py --max-workers 8  # 正常期才运行
```

任一失败 → 回滚清理。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 仅凭"零消费者"判定删除 | 误删有价值的安全/治理组件 |
| ❌ | 仅凭"时间旧"删除蓝图版本 | 丢失新版本未覆盖的内容 |
| ❌ | 清理后不跑验证三步 | 注册表/路径树/依赖图漂移 |
| ❌ | 只做一次性清理，不建常驻机制 | 垃圾持续累积 |

---

## RULE-THIRTEEN：任务卡粒度铁律
**YAML真源**: → 参见 rules/trae_003_task_granularity_threshold.yaml

**核心**：一卡一任务，独立可验证。任务卡 = 施工图——施工细节写在 description 里（不限字数），蓝图只写设计。

### 粒度门禁（create() 时自动校验）

| 字段 | 上限 | 超限处置 |
|------|:---:|------|
| `deliverables` 数量 | ≤ 1 | 拒绝建卡，提示拆卡 |
| `files_in_scope` 数量 | ≤ 3 | 拒绝建卡，提示拆卡 |
| `acceptance` 独立验收点 | ≤ 1 | 人工判定 |
| 跨 Phase | 禁止 | 拒绝建卡，提示拆卡 |

### 拆卡四条机械规则（任一触发即拆）

| # | 规则 | 判定 |
|---|------|------|
| R1 | deliverables > 1 | 数列表长度 |
| R2 | files_in_scope > 3 | 数列表长度 |
| R3 | acceptance 有 > 1 个独立验收点 | 验收点能否独立通过/失败 |
| R4 | 施工步骤跨 > 1 个施工目标 | 施工目标 = 对一个文件/模块的一次原子修改 |
| R5 | description 缺"根因/治根/施工步骤/验收标准" | 结构词缺失 = 描述不完整 |
| R6 | description < 100字 | 信息不足 = 幻觉温床 |

### 超粒度自动拆分

建卡被 R1-R6 拦截时，调用 `TaskRepository.auto_split_task(task)` 或 MCP `task_manager.auto_split(task_id)` 可按违规维度自动拆分为多张合规子卡。详见 `trae_034_task_card_standard.yaml §6.5`。

### 状态转换与认领

| 转换 | 说明 |
|------|------|
| PENDING → READY | 建卡后手动/自动转就绪 |
| READY → IN_PROGRESS | `repo.claim_next(batch_id, worker_id)` 原子认领，自动转 IN_PROGRESS |
| IN_PROGRESS → COMPLETED | 施工完成，触发 `_auto_phase_cleanup_hook` 硬删除 |
| COMPLETED → VERIFIED | 验证通过（终态） |
| 任意 → CANCELLED | 取消，同样触发硬删除 |

`claim_next(batch_id, worker_id)` — 按 batch 轮转原子认领，返回 TaskCard 或 None。

### 深挖病根强制

```
transition(task_id, COMPLETED) 时自动校验：
├─ 任务中有 error/failure？→ MUST 有 root_cause_analysis 记录
│   └─ 无记录 → 拒绝完成（SyncVerificationError）
└─ root_cause_analysis = MTH-006 根源分析（追问到底，非固定5次）
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | deliverables > 3 或 files_in_scope > 5 仍建卡 | 任务边界模糊，验收困难 |
| ❌ | 遇到 error 不写 root_cause_analysis 直接完成 | 症状修复，根因残留 |
| ❌ | 用"修了"替代 MTH-006 根源分析 | 同类问题必然重现 |

---
## RULE-FOURTEEN：根目录清爽铁律
**YAML真源**: → 参见 rules/trae_001_file_operation_security.yaml

**核心**：根目录是项目门面——只允许白名单目录/文件存在。任何不在白名单中的 = 垃圾。

### 根目录白名单（物理存在于根目录的文件/目录）

| 类型 | 允许项 | 说明 |
|------|--------|------|
| IDE 配置 | `.editorconfig`, `.traeignore`, `.vscode/` | 编辑器通用 |
| AI 规则 | `.trae/`, `AGENTS.md` | AI session 注入 |
| 版本控制 | `.gitignore`, `.gitattributes` | Git |
| CI/CD | `.pre-commit-config.yaml`, `.github/` | 门禁 |
| 架构约束 | `.importlinter` | 层契约 |
| Python | `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `requirements-demo.txt`, `py.ini` | 构建+依赖 |
| 运行时配置 | `.env.example`, `config/` | 环境变量模板 |
| Docker | `Dockerfile`, `docker-compose.yml` | 容器 |
| 项目文档 | `README.md`, `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md` | GitHub 页面 |
| 源码目录 | `src/`, `scripts/`, `tests/`, `tools/` | 代码 |
| 文档 | `docs/`, `architecture_model/`, `specs/` | 蓝图+规格 |
| 数据 | `data/`, `models/`, `infra/`, `demos/`, `session_logs/` | 数据+模型+基础设施 |
| 运行时（自动生成） | `.ailocks/`, `.aidrafts/`, `.audit_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.runtime/`, `.zephyr/`, `.zephyr_secure/`, `logs/`, `reports/`, `_journals/` | 系统生成，自动重建 |

### AI 可以做和不可以做的事

| # | 行为 | 判定 | 后果 |
|---|------|:---:|------|
| ✅ | 在根目录创建临时 `.py` 脚本，运行完后立即删除 | **允许** | — |
| ✅ | 在根目录创建临时 `.md` / `.txt` 输出文件（测试结果/验证报告），用完后立即删除 | **允许** | — |
| ❌ | 在根目录下创建任何**永久性** `.py` / `.md` / `.yaml` / `.json` / `.txt` 文件 | 直接判定为垃圾 | 应该放到 `scripts/` / `docs/` / `tests/` 等标准目录 |
| ❌ | 在根目录下创建任何**子目录**（`_temp*` / `_check*` / 新名字） | 目录蔓延 | 垃圾 |
| ❌ | Session 结束时根目录仍有临时文件残留 | 垃圾留给下一个 session | 违反零残留铁律 |

### 系统绝对不能做的事（代码级禁令）

| # | 行为 | 修复方向 |
|---|------|---------|
| ❌ | 创建空目录而不填充（`meta/`, `tasks/`, `results/`, `cache/` 等） | 禁止 mkdir-only 操作——创建目录时 MUST 同时写入内容 |
| ❌ | 每次检查生成一个独立报告文件（如 `truth_source_cascade` 轰炸 300+ 个） | O(1) 文件：覆盖写入、追加单日志、或写数据库 |
| ❌ | Skill 查找失败后持久化 `NONEXISTENT-SKILL_*.json` | 失败 = 不落盘 |
| ❌ | 自动保存 AI 会话提示词到 `_prompts/` | 禁用或设 max 保留数 + TTL 自动清理 |

### Session 关门时必须做

```
7.1 根目录审计: ls 根目录 → 逐项对照白名单 → 不在白名单中的 → 直接删除或归档
```

### 根源

本次清理发现的 40+ 个垃圾文件/空目录，根因只有一个：**没有根目录白名单门禁——任何人/AI/系统都可以往根目录写东西，永远没人清理。**

AIR-001: 每次 session 关门时强制根目录审计。
AIR-002: 任何系统生成根目录文件必须配套 TTL/上限/轮转策略。

---

## RULE-FIFTEEN：自动化双轨判定
**YAML真源**: → 参见 rules/trae_053_automation_dual_track.yaml

**核心**：任何新建/改造自动化系统，MUST 通过两轨分类 + 实现验证。单轨实现 = 未完成。

### 两轨分类表

| 任务特征 | 适合轨 | 原因 |
|---------|:---:|------|
| 全项目扫描（去重、孤儿、临时文件、审计保留） | 🕐 定时 | 事件驱动太贵：每次文件变更就扫全项目 |
| 重操作（深度漂移扫描、模型画像、语义审计） | 🕐 定时 | 凌晨跑，不影响白天业务 |
| 外部同步（定价、模型列表、上游数据） | 🕐 定时 | 没有事件源，只能定时拉 |
| 缓存/日志维护（轮转、失效、清理） | 🕐 定时 | 日常运维，不需要实时 |
| 状态变更响应（BLOCKED→升级、IN_PROGRESS→超时计时器） | ⚡ 事件 | 有明确 TransitionEvent 触发点 |
| 即时校验（蓝图变更→三方对齐、LLM调用→预算检查） | ⚡ 事件 | 实时反馈，等到明天太晚 |
| 关键校验（预算健康、三方对齐、升级路径） | 🕐+⚡ 双轨 | 事件做增量，定时做全量兜底 |

### 施工强制三步

```
STEP 1: 判定归属 → 对照分类表确定 🕐 / ⚡ / 🕐+⚡
STEP 2: 实现
  ├─ 🕐 定时 → 在 boot_cron_jobs.py 中注册（circadian_scheduler.register_task）
  │             守护进程已挂载 circadian_scheduler，无需额外启动
  ├─ ⚡ 事件 → 在 boot_hooks.py 中注册 hook_registry.register 或 event_bus.subscribe
  │             守护进程已加载 boot_hooks，无需额外启动
  └─ 🕐+⚡ 双轨 → 两条都要
STEP 3: 验证 → python scripts/ide_health_service.py --status
  ├─ circadian.running=true + tasks_registered 正确计数 → 🕐 通过
  └─ 触发事件后 check 对应 hooks 执行 → ⚡ 通过
```

### 守护进程承载

| 轨 | 载体 | 位置 |
|---|------|------|
| 🕐 定时 | `CircadianScheduler`（守护进程中，每小时整点执行） | [ide_health_service.py](file:///d:/ZephyrAlpha/scripts/ide_health_service.py) |
| ⚡ 事件 | `HookRegistry`（TransitionEvent 触发）+ `EventBusBackpressure`（topic 触发） | [boot_hooks.py](file:///d:/ZephyrAlpha/src/zephyr/trading/boot_hooks.py) |

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 新建自动化系统不判定两轨归属 | 盲目挂在单一轨＝要么遗漏要么浪费 |
| ❌ | 全项目重扫描挂在事件驱动上 | 每次文件变更扫全项目＝拖死 |
| ❌ | 实时校验只靠定时（等到凌晨才跑） | 反馈延迟十几小时 |
| ❌ | 关键校验只有一轨无兜底 | 事件丢了没补偿＝漏报 |
| ❌ | 实现定时轨但不注册到 circadian_scheduler | 代码写好了但没人跑 |
| ❌ | 实现事件轨但不注册到 hook_registry | 触发条件满足了但钩子不响 |

---
## RULE-SIXTEEN：depgraph 程序化访问协议
**YAML真源**: → 参见 rules/trae_054_depgraph_access_protocol.yaml

**核心**：depgraph 存储在 SQLite 数据库 `D:/ZephyrAlpha/data/databases/depgraph.db`（v4.0.0, 16张表）——禁止 AI 直接 Read/Write。必须通过提取/应用脚本操作。

### 触发条件

任何需要读取或修改 depgraph 的操作——包括查看模块定义、修改 physical_files、更新 blueprint_status、查看域结构等。

### 强制操作序列

```
读取 depgraph 数据:
  STEP 1: 确定需要什么数据（域摘要？指定域？指定模块？顶级元数据？路径列表？）
  STEP 2: 运行对应提取命令
          python scripts/governance/extract_depgraph.py --summary     # 39域+模块数
          python scripts/governance/extract_depgraph.py --domains D-FACTOR,D-RISK
          python scripts/governance/extract_depgraph.py --modules D-FACTOR-01
          python scripts/governance/extract_depgraph.py --top          # 顶级元数据
          python scripts/governance/extract_depgraph.py --paths        # 所有physical_files
          python scripts/governance/extract_depgraph.py --stats        # 文件大小统计
  STEP 3: AI 只读提取结果（JSON，几KB到几百KB，安全）

修改 depgraph:
  STEP 0: 前置备份（MUST，每次 apply_depgraph.py 执行前）
          git add data/databases/depgraph.db
          git commit -m "backup: depgraph before <操作描述>"
          git log -1 --oneline data/databases/depgraph.db   # 验证备份存在
          # 回滚: git checkout HEAD~1 -- data/databases/depgraph.db
  STEP 1: AI 生成变更 JSON 文件
  STEP 2: python scripts/governance/apply_depgraph.py --batch changes.json --dry-run  # 验证
  STEP 3: python scripts/governance/apply_depgraph.py --batch changes.json             # 执行
  STEP 4: python scripts/governance/extract_depgraph.py --summary     # 验证变更
```

### 变更 JSON 格式

```json
[
  {"op": "update", "module_id": "D-FACTOR-01", "field": "blueprint_status", "value": "has_blueprint"},
  {"op": "add_physical_file", "module_id": "D-FACTOR-01", "path": "src/zephyr/factor/new_file.py"},
  {"op": "remove_physical_file", "module_id": "D-FACTOR-01", "path": "src/zephyr/factor/old_file.py"},
  {"op": "set_physical_files", "module_id": "D-FACTOR-01", "files": ["path1.py", "path2.py"]}
]
```

### 为什么不能拆分 depgraph

拆分 39 个域文件 → 跨域关系丢失 → AI 看到碎片化数据 → 产生大量漂移和幻觉。depgraph 保持一个文件（SSoT），通过程序化提取访问。

### 为什么不能换模型

DeepSeek V4 RPO 1M context ≈ 1M tokens。depgraph 需要 ~55M tokens。差距 55 倍。任何当前模型都无法装下。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 用 Read 工具读取 depgraph 文件 | 157MB 加载 → OOM 崩溃 → IDE 重启 |
| ❌ | 用 Write 工具直接写 depgraph 文件 | 157MB 写入 → OOM 崩溃 + 可能损坏文件 |
| ❌ | 用任何方式将 depgraph 内容注入 AI 上下文 | 55M tokens → 内存溢出 |
| ❌ | 拆分 depgraph 为 39 个域文件 | 跨域关系丢失 → 漂移和幻觉 |
| ❌ | 绕过提取脚本自己写 Python 代码直接读 depgraph | 你的 Python 代码可以读，但 AI 上下文不能 |

### 例外

| 场景 | 允许操作 |
|------|---------|
| 读取 depgraph 前 20 行（仅看文件头警告） | ✅ Read(limit=20) |
| 运行 generate_project_depgraph.py 生成/更新 depgraph（⚠️ 架构升级期间禁止） | ✅ 生成脚本内部处理 |
| 运行 diagnose_depgraph.py 诊断 | ✅ 诊断脚本内部处理 |

---

## RULE-SEVENTEEN：禁止 PowerShell 语法

**核心**：PowerShell 引号转义复杂 + 默认非 UTF-8 编码 + `>` 重定向 = 引号出错 + 中文乱码 + 文件损坏。从规则层禁止 PowerShell 语法，复杂逻辑封装为 `.py` 脚本。

### RunCommand 白名单（仅允许裸命令）

| 允许 | 示例 |
|------|------|
| `python <脚本>.py <参数>` | `python scripts/lock_files.py check <file>` |
| `git <subcommand>` | `git status` |
| `python -m pytest <path>` | `python -m pytest tests/` |
| `python -m zephyr.<mod>` | `python -m zephyr.governance.task_repo` |

### 禁止语法（黑名单）

| # | 禁止 | 替代 |
|---|------|------|
| 1 | 管道 `\|` | 写 .py 脚本串联 |
| 2 | 引号嵌套（`"...'...'..."`） | 写 .py 脚本 |
| 3 | `$` 变量 | Python 变量 |
| 4 | cmdlet（`Get-`/`Set-`/`Where-` 等） | Read/Write/Edit 工具 |
| 5 | `>` 重定向 | Write 工具 或 Python `open(encoding='utf-8')` |
| 6 | `;` 命令串联 | 分多次 RunCommand |

### 文件操作强制映射

| 操作 | 禁止 PowerShell | 必须用 |
|------|----------------|--------|
| 读 | `Get-Content`/`cat`/`type` | Read |
| 写 | `Set-Content`/`>`/`Out-File` | Write 或 Python |
| 编辑 | 字符串替换命令 | Edit |
| 搜索文件 | `Get-ChildItem`/`dir`/`find` | Glob |
| 搜索内容 | `Select-String`/`findstr`/`grep` | Grep |
| 删除 | `Remove-Item`/`del` | DeleteFile |

### 复杂逻辑

需要管道/引号嵌套/变量 → 写 `.py` 脚本 → RunCommand 跑 `python xxx.py`。

---

## RULE-EIGHTEEN：连续两次审查零问题
**YAML真源**: → 参见 rules/trae_042_meta_rule_standard.yaml §std_011_dual_review_protocol

**核心**：任何文件变更声明完成前，MUST连续两次审查零问题。防止"执行完不检查"或"只检查一次"导致的幻觉和漂移残留。

### 适用范围

| 场景 | 触发 | 豁免 |
|------|------|------|
| 任务卡 COMPLETED | ✅ | — |
| 代码修改交付 | ✅ | — |
| 规则文件修改 | ✅ | — |
| 文档更新 | ✅ | — |
| 配置变更 | ✅ | — |
| Session 关门 | ✅ | — |
| 纯只读操作（搜索/查询/审查本身） | — | ✅ |

### 强制三步

```
STEP 1  第一次审查 → 按文件类型审查清单逐项审查 → 问题数=0？
        ├─ YES → 进 STEP 2
        └─ NO  → 修复 → 重新执行 STEP 1
STEP 2  第二次审查 → 重新执行完整审查清单（非仅查修复点）→ 问题数=0？
        ├─ YES → 进 STEP 3
        └─ NO  → 修复 → 重新从 STEP 1 开始
STEP 3  连续两次零问题判定 → 通过 → 可声明完成
```

### 计数规则

| 规则 | 说明 |
|------|------|
| 连续两次中间不能有任何问题 | 有问题就重新计数 |
| 第二次审查必须完整执行 | 禁止只查第一次的问题点 |
| 审查必须覆盖全部变更 | 禁止只查变更部分 |
| 伪造审查结果 = 违规 | 未实际执行审查就声明零问题 |

### 审查清单映射

| 文件类型 | 审查清单 |
|---------|---------|
| 代码 | 功能完整/边界处理/错误路径/类型一致/导入完整/安全检查 |
| 规则 | std_009_audit_checklist + std_010_rule_review_simulation |
| 文档 | 路径准确/数字一致/引用完整/格式规范/无否定陈述 |
| 配置 | 字段完整/值合法/引用存在/格式正确 |
| 任务卡 | 18字段完整/R1-R6粒度/验收命令/回滚方案 |

### 规则文件修改的额外要求

修改规则文件（trae_XXX.yaml）后，除连续两次审查外，MUST额外执行 **std_010_rule_review_simulation**（模拟新AI测试）：
1. 冷启动模拟——假装新AI第一次进项目，能否无歧义理解规则
2. 幻觉检测——规则是否可能导致AI产生幻觉（路径/ID/命令是否真实存在）
3. 漂移检测——规则是否可能导致AI偏离正确行为
4. 模拟新AI执行——按规则执行一次典型任务，检查是否产生错误
5. 连续两次模拟零问题才通过

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 声明完成但未执行连续两次审查 | 幻觉和漂移残留 |
| ❌ | 仅审查一次就声明通过 | 一次审查无法发现所有问题 |
| ❌ | 第二次审查只查第一次的问题点 | 修复可能引入新问题 |
| ❌ | 审查发现问题但不修复就声明通过 | 问题累积 |
| ❌ | 修改规则文件后跳过模拟新AI测试 | 规则可能产生幻觉/漂移 |
| ❌ | 伪造审查结果 | 自欺欺人 |

---

## RULE-NINETEEN：先裁定后确认（MTH-009 显化）
**YAML真源**: → 参见 rules/trae_025_methodology_decision.yaml §mth_009

**核心**：AI 遇到任何决策（方案选择/范围裁定/触发条件判定/多选项权衡）MUST 先给出专业裁定+理由，再请 Owner 确认。禁止直接问"你选哪个"把决策权推给 Owner。

### 触发条件

任何需要 Owner 决策的问题——包括但不限于：方案多选/备份范围裁定/触发条件判定/拆分边界决策/技术路线权衡。

### 强制三段输出格式

```
1. 分析过程（基于项目文档/专业实践/量化数据给出分析）
2. 裁定结果（明确推荐其中一个，给出理由，不是选择题）
3. 确认请求（请 Owner 确认或否决，否决需给出理由后 AI 重新裁定）
```

### MTH-007 决策质量四问（裁定前 MUST 完成）

| # | 维度 | 自问 |
|---|------|------|
| 1 | 埋雷检查 | 这个选择会不会给未来埋雷？纠正需重写架构吗？ |
| 2 | 容量检查 | 会不会限制未来容量？余量多少？ |
| 3 | 专业对标 | 专业机构/社区怎么做的？MUST 引用至少一个来源 |
| 4 | 最终建议 | 带推理：A 在埋雷维度无风险/容量有余量/对标有先例 → 推荐 A |

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 遇到决策直接问 Owner "你选哪个/你想怎么做" | 把决策权推给 Owner，违反 MTH-009 |
| ❌ | 只给选项不给推荐 | Owner 无法判断，决策质量下降 |
| ❌ | 以"我不确定"为由把决策推给 Owner | MUST 基于现有信息做出最优判断 |
| ❌ | 跳过专业对标（专业机构/社区怎么做）直接给结论 | 裁定缺乏依据 |
| ❌ | 跳过 MTH-007 决策质量四问 | 方案可能埋雷或限制容量 |

---

### 结构追溯（#1-#6）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 1 | **源头追溯**——代码文件 MUST 标注 `[BLUEPRINT] {module_id} \| {蓝图路径}` | 无标注 = 孤儿文件 |
| 2 | **不变量声明**——代码文件 MUST 标注 `[INVARIANTS] {不可违反的约束}` | AI 修改时破坏关键约束 |
| 3 | **修改守卫**——代码文件 MUST 标注 `[MODIFY-GUARD] {改此文件必须同步更新的文件}` | AI 改一处忘其他，集成断裂 |
| 4 | **依赖声明**——代码文件 MUST 标注 `[CONSUMERS] {依赖此文件的模块}` | AI 不知道修改的影响范围 |
| 5 | **蓝图锚点**——蓝图 MUST 在头部标注蓝图+施工图模板+AI 压缩工作流标准链接 | AI 偏离蓝图模板，产出不一致 |
| 6 | **漂移检测**——蓝图 §4 文件清单 ↔ 代码 `[BLUEPRINT]` 字段（含 §N 章节级）MUST 双向对齐 | 蓝图与代码漂移 |

### 行为约束（#7-#10）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 7 | **禁止占位符**——代码中禁止 `TODO`/`...`/`pass`/`NotImplementedError`。必须产出可执行代码 | 半成品伪装完成 |
| 8 | **编辑优先**——禁止删除+重建来"修改"。必须 surgical edit | 丢失 history + 注册失效 |
| 9 | **最小变更**——只改必须改的。禁止"顺手重构""顺便优化" | 无关变更引入 bug |
| 10 | **假设显式化**——不确定的决策 MUST 标记 `[ASSUMPTION]` 等待确认 | AI 凭空假设 API/格式/配置 |

### 输出验证（#11-#14）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 11 | **步骤验证门**——每步完成 MUST 验证成功后才进下一步 | 错误累积，回溯成本指数增长 |
| 12 | **导入验证**——使用任何 `import`/API/函数前 MUST Grep/Read 确认存在 | 引用不存在的库/API/模块 |
| 13 | **自审闭环**——产出代码后 MUST 对照需求自审：功能完整？边界？错误路径？ | 输出与需求不匹配 |
| 14 | **新代码必测**——新建/修改代码 → MUST 写或更新测试。无测试 = 未完成 | bug 无从发现 |

### 安全防护（#15-#18）

| # | 规则 | 不遵守会怎样 |
|---|------|------------|
| 15 | **安全最低通过**——交付前 MUST 通过：认证/注入/数据暴露三项检查 | 安全漏洞交付 |
| 16 | **计划先行**——涉及 >3 文件或 >50 行 → MUST 先输出计划 → 确认 → 执行 | 无计划大范围修改，失控 |
| 17 | **跨文件影响检查**——修改前 MUST 检查 `[CONSUMERS]` + Grep 所有引用 | 改一处忘其他，集成断裂 |
| 18 | **上下文新鲜度**——对话 >30 轮或 AI 出现重复/矛盾 → 开新会话 | 上下文退化，幻觉温床 |

**格式标准**: [trae_047_engineering_file_header.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml)（GOV-ENG-002 文件头部十一字段，原 code-construction-standards.md §7 已迁移）

---

## 规则本身的规则

| # | 规则 |
|---|------|
| 1 | `.trae/rules/` 目录 AI 不可写入。规则是 IMMUTABLE——想改规则 → 报告 Owner，不要自己改 |
| 2 | 禁止凭记忆判断任何 API/库/函数/模块/路径的存在性。不确定 → 先搜。搜不到 = 不存在，搜到了 = 存在。**双向搜索**——不假设存在，也不假设不存在 |
| 3 | 幻觉检测器在监控。引用不存在的路径/ID/命令 → 会被阻断。输出的每个路径和 ID 必须能在项目中搜到 |

---

## 产出规则

| # | 规则 |
|---|------|
| 1 | 新建脚本中任何 `for + subprocess/I/O` → **强制 ThreadPoolExecutor(max_workers=8)**。判定三指标：A.`for`+subprocess B.`for`+多文件独立读写 C.`for`+多URL请求——任一 YES → MUST 并行 |
| 2 | Python 写文件统一用原子写入。禁止 `open(path, "w")` 直接写。模板：`tmp=f"{path}.{os.getpid()}.tmp"; open(tmp,"w",encoding="utf-8")→f.write→os.replace(tmp,path)` |
| 3 | 写完脚本 → 立刻跑 `python <脚本> --warn-only` 自测。挂了自己修，修完再报完成 |
| 4 | **极简产出**：能用表格不用段落，能用命令不用描述。不写"为什么"和"对标"。每句话必须有信息增量。**优化安全协议见 onboarding_detail.md §10.6** |
| 5 | **防幻觉头部**——新建/修改代码文件 MUST 包含 `[BLUEPRINT]`/`[MODULE]`/`[DOMAIN]`/`[INVARIANTS]`/`[MODIFY-GUARD]`/`[CONSUMERS]`/`[STABILITY]`/`[SAFETY]`/`[AI_AUTONOMY]`/`[ERROR_CONTRACT]`/`[TESTS]` 十一字段头部。缺失 = 孤儿文件 |
| 6 | **根因追踪（MTH-006）**——遇到 bug/失败/漂移/异常 → MUST 追问到底：连问为什么直到找到最根部原因，**不是固定5个——是问到底**。追问路上发现的每个中间问题 MUST 一并解决，不留尾巴。治根判定：修复后同类问题不再产生 + 作用于设计层面 + 可泛化为原则。禁止只修症状不治根 |
| 7 | **搜索先行复用决策**——新建功能前 MUST 搜索已有覆盖。搜索三步：①关键词全局搜索 ②注册表精确匹配 ③复用决策。复用四选一：完全覆盖→直接用 / 80%→扩展已有 / 50%→重构+扩展 / 0%→scaffold 新建。放弃新建时 MUST 写 `[REUSE-DECISION]` |
| 8 | **编码安全**——Python `open(path, 'w')` 禁止省略 `encoding='utf-8'`；PowerShell 写文件用 `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)`；禁止 Trae+Cursor 同时打开同一文件；扫描器大量报错 → 先检查扫描器逻辑 |
| 9 | **修改原则**——发现事实错误 → 直接修正，禁止添加"之前为什么是错的"解释段；文档中所有数字/版本号/计数必须是当前唯一真实值；单个 real number 原则：一个事实在所有蓝图中只能有一个数字，不一致 = bug |
| 10 | **审计前置**——任何涉及文件变更的任务完成后 MUST 执行 `python scripts/governance/run_all.py --depth quick`。不审不清，不清不继续 |
| 11 | **资产认知（RULE-NINE）**——进项目 MUST 先了解全盘资产规模与健康状态。读 `data/asset_index/unified_asset_index.yaml` → 知道总资产/健康评分/孤儿率。不知道系统有多大 = 盲目施工 |

---

## 强制集成对照表

> 逐条念出来打勾——不是扫一眼就跳过。

| AI 要做什么 | 必须先跑什么 | 不跑会怎样 |
|------------|-------------|-----------|
| **写入任何文件** | `python scripts/governance/pre_write_gate.py <文件>` | exit≠0 → 禁止写入 |
| **创建新文件** | `python scripts/scaffold.py module/script/gate <参数>` | 绕开 scaffold → 孤儿文件 |
| **删除任何文件** | RULE-THREE 三步审判 → 全通过才能删 | 一步不通过 → 不能删 |
| 修改 `src/zephyr/` 源码 | `python -m pytest tests/ --collect-only -q` | 语法错误 → 禁止提交 |
| 修改 YAML 契约/配置 | `python scripts/governance/d5_architecture/checkers/check_contract_code_drift.py` | 契约断裂 → 禁止合并 |
| 修改 AGENTS.md | `python scripts/governance/d5_architecture/validators/validate_load_path_integrity.py --check` | LoadPath 断裂 → 禁止提交 |
| 修改 project_rules.md | `python scripts/governance/sync_rule_registry.py` | rule-registry 不同步 → 禁止提交 |
| 任何文件变更后 | `python scripts/governance/run_all.py --depth quick` | 有发现 → 先修再关 |
| 修改蓝图§5.5自动化触发机制 / 修改代码实现 | `python scripts/governance/d5_architecture/checkers/check_blueprint_automation_sync.py --blueprint <蓝图路径>` | §5.5状态列与代码不一致 → 禁止关闭任务 |
| **新建/改造自动化系统** | RULE-FIFTEEN 两轨判定：对照分类表 → 🕐 定时(circadian_scheduler) / ⚡ 事件(hook_registry) / 🕐+⚡ 双轨 | 单轨实现或未注册 → 禁止关闭任务 |
| **读取/修改 depgraph** | `python scripts/governance/extract_depgraph.py --summary`（读取）/ `python scripts/governance/apply_depgraph.py --batch <变更文件>`（修改） → 详见 RULE-SIXTEEN | 直接 Read 157MB → OOM 崩溃 |
| **蓝图-代码-路径树三方对齐** | 结构变更后 MUST 同步刷新：⚠️ 架构升级期间（阶段0-4）禁止运行 generate_project_depgraph.py（会覆盖 depgraph.db）。仅 depgraph.db 为真源。正常期: `generate_project_depgraph.py --max-workers 8` + `generate_project_path_tree.py --write` + 蓝图 §4 | 任一方过时 → AI 看到幻影/漏掉真实文件 → 禁止关闭任务 |
| **创建/删除/移动文件后** | `python scripts/governance/generate_project_path_tree.py --write` | 路径树过时 → 下个 session 冷启动看到错误结构 → 禁止关闭任务 |
| 安全敏感变更 | `python scripts/governance/d6_security/scan_secret_leak.py` | 泄漏 → 硬阻断 CI |
| 回滚/撤销 | `python scripts/rollback.py preflight` → CLEAN → `rollback.py <cmd>` | preflight FAIL → 禁止回滚 |
| Agent间协作/多Agent/冲突 | `from zephyr.infra_runtime.a2a_protocol.governance.governance_adapter import GovernanceAdapter; adapter.verify_pair(a, b)` + Skill 路由 a2a → SKILL-DOM-A2A-001 | 静默失败 + 死锁无防护 |
| 高风险操作（批量/安全） | `from zephyr.governance.escalation_engine import EscalationEngine; EscalationEngine().evaluate(RuleCategory, desc)` | 可能执行本应变 blocked 的操作 |
| 多Agent/MCP 委托 | `from zephyr.governance.delegation_engine import DelegationEngine; engine.delegate(event, strategy)` | 死锁/循环委托/深度溢出 |
| LLM API 调用前 | `from zephyr.governance.budget_engine import BudgetEngine; engine.pre_flight_check(operation_id, tokens, cost)` | 超预算 → 降级或拒绝 |
| 任何写入/执行/修改前 | `guard.check(identity, operation, target_path)` — PermissionGuard | BLOCKED → 禁止执行 |
| 施工前：检查已有知识 | `kb.search("<关键词>")` | 重复造轮子 / 违反已有决策 |
| 施工后：写入知识 | `kb.write(topic="...", content="...", provenance=build_provenance(...))` | 知识丢失 → 下个 session 不知道 |
| **脚本运行慢/卡死** | 执行 PERF-001 十项检查清单 → `docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml` §9 | 凭直觉改代码 → 治标不治本 → 卡死复现 |

---

## Session 冷启动序列

进入项目后 MUST 按以下顺序执行（不可跳过、不可重排）：

```
STEP 1   — 读 docs/registry_of_registries.yaml → 了解全项目注册表
STEP 1.1 — 读 docs/03_modules/template_registry.yaml → 了解可用模板
STEP 1.2 — 提取 depgraph 摘要：`python scripts/governance/extract_depgraph.py --summary`（唯一真源，禁止直接 Read 157MB 文件。详见 RULE-SIXTEEN）
STEP 1.3 — 确认三库就绪：depgraph.db（依赖图，extract_depgraph.py）+ governance.db（治理/任务，TaskRepository）+ market.duckdb（业务时序，duckdb.connect）。路径均在 `data/databases/`
STEP 1.5 — 读 docs/03_modules/_sys_master/blueprint.md §0 → 定位子系统任务域
STEP 2   — 读本文件（project_rules.md）→ 了解硬规则
STEP 3   — Session Continuity 恢复: 上一个 session 做了啥 / 未完成任务 / 锁状态
STEP 4   — Phase Manager: 当前施工阶段（46 个门控检查）
STEP 4.5 — 资产盘点: unified_asset_index.yaml（总资产/健康评分/孤儿率）
STEP 4.6 — Skill 发现: 查看 data/capability_cards/ 目录（22 个 skill_*.yaml）
STEP 4.7 — KB 自检: bootstrap 扫描文档 → 填充知识库 → 施工前查已有 KE
STEP 4.8 — Escalation Protocol 激活: 升级/委托安全网
STEP 4.9 — Drift Detector 初始化: 全部漂移检测器 + 漂移预算检查
STEP 4.10 — Agent RBAC 激活: 身份注册 + PermissionGuard + 全部模块完整性
STEP 4.11 — Rollback System 激活: preflight + AutoTrigger + Kill Switch
STEP 4.12 — Budget Enforcer 激活: Token/Cost/Time 三维预算
STEP 4.13 — Audit Trail: 审计链完整性 + 最近 50 条事件注入
STEP 4.14 — A2A Protocol: 发现→通信→调度→防护 四段检查
STEP 4.15 — DepMap 依赖图: ⚠️ 架构升级期间（阶段0-4）禁止运行 generate_project_depgraph.py（会覆盖 depgraph.db）。用 `python scripts/governance/extract_depgraph.py --summary` 替代。正常期: `python scripts/governance/generate_project_depgraph.py --max-workers 8` → 文件级+包级依赖
STEP 4.16 — 三方对齐验证: `python scripts/governance/check_rule_four_way_alignment.py --all`（YAML↔DB↔Code↔Blueprint）。exit≠0 → 漂移，禁止开工，先修复对齐
STEP 5   — 按需定位具体注册表 → 开工
```

不完成 STEP 1-4.16 = 不可开工。

---

## Session 开关门

**进门**: 读 [registry_of_registries.yaml](file:///d:/ZephyrAlpha/docs/registry_of_registries.yaml) → 读 `docs/03_modules/_sys_master/blueprint.md` §0 → 查看 `data/capability_cards/` 目录（skill_*.yaml）

**关门**（缺一不可）:
```
1. python scripts/lock_files.py release-all <session_id>
2. python scripts/lock_files.py cleanup
3. python scripts/lock_files.py status → 确认 CLEAN
4. sc.generate_and_save(session_id=..., task_repo=...) — 保存状态给下一次 session
5. python scripts/governance/sync_rule_registry.py — 校验 RULE-* 条目登记
6. python scripts/governance/auto_sync_all_registries.py --all --warn-only — 全注册表同步
6.1. python scripts/governance/generate_project_path_tree.py --write — 刷新路径树快照
6.2. python scripts/governance/generate_path_ownership_map.py --write — 刷新路径归属声明
6.3. Session-level cleanup: code → `data/cache/` 清空 + 临时文件全删除（RULE-TWELVE）
7. 零残留扫描: _temp* / _check* / _fix* / _phase_* 前缀文件 → 全部删除
8. 根目录审计: ls 根目录 → 逐项对照 RULE-FOURTEEN 白名单 → 不在白名单 → **删**
9. 确认本次 session 产生的所有 .py 文件在合法三目录中
10. 废墟引用检查: 删过文件/目录 → 确认无其他文件引用已删路径
11. `python scripts/governance/run_all.py --depth full` — 全量审计扫描
12. IN_PROGRESS任务检查: `python -c "from zephyr.governance.task_repo import TaskRepository; r=TaskRepository(); t=r.list_by_status('IN_PROGRESS'); assert len(t)==0, f'{len(t)} IN_PROGRESS tasks remain — 关门前必须关闭或释放"`
13. 写 Session Log（session_logs/YYYY/MM/session-YYYYMMDD-NNN.yaml）
```

---

## 触发关键词 → Agent Skill 路由

| 关键词 | Skill |
|--------|-------|
| database / sql / migration | SKILL-DOM-DBS-001 |
| mcp / server / tool | SKILL-DOM-MCP-001 |
| context / pipeline | SKILL-DOM-CTX-001 |
| feedback / loop / 根因 / 追问到底 / 治根 / 诊断反转 / 慢脚本 / 卡死 / PERF-001 | SKILL-DOM-FBL-001 |
| gate / rule / policy | SKILL-DOM-GAT-001 |
| permission / rbac | SKILL-DOM-AGT-001 |
| blueprint / architecture | SKILL-DOM-BLU-001 |
| audit / drift / governance | SKILL-DOM-DRF-001 |
| audit system / 审计系统 / 扫描系统 / 检查问题 / run_all / 全量审计 | SKILL-DOM-AOR-001 |
| knowledge / KE | SKILL-DOM-KNW-001 |
| rollback / undo / checkpoint | SKILL-DOM-RBK-001 |
| security / lsg / injection / prompt_injection | SKILL-DOM-LSG-001 |
| vector / embedding / VMS / chromadb | SKILL-DOM-VMS-001 |
| task / taskcard / task-card | SKILL-DOM-TSK-001 |
| telemetry / observability / metrics | SKILL-DOM-TEL-001 |
| dedup / duplicate / monoculture | SKILL-DOM-DED-001 |
| budget / 预算 / cost limit / token limit | SKILL-DOM-BGT-001 |
| fix / repair / self-heal / 修复 / 故障 | SKILL-DOM-AFX-001 |
| a2a / agent-to-agent / 冲突 | SKILL-DOM-A2A-001 |
| behavioral / safety / 行为审计 | SKILL-DOM-BEH-001 |

加载: Read `data/capability_cards/<skill_id>.yaml`
Python API: 待阶段4搬家后激活（当前用 Read `data/capability_cards/<skill_id>.yaml`）

---

## 不确定时的默认路径

```
1. 撞门禁 → 读门禁输出 → 按输出说的做
2. 不知道有什么 → 搜 registry_of_registries.yaml
3. 不知道怎么做 → 查看 `data/capability_cards/` 目录 → 匹配关键词 → Read 对应 yaml
4. 不知道能不能改 → 搜 docs/01_policies_and_standards/
```

---

## 关键标准速查

| 领域 | 标准 | module_id |
|------|------|-----------|
| 治理决策 | [trae_024_methodology_diagnosis.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml) | PS-STD-011 |
| 代码构建 | [trae_010_code_naming_organization.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml) | GOV-ENG-001 |
| 脚本质量 | [quality_standard.md](file:///d:/ZephyrAlpha/scripts/governance/quality_standard.md) | SCRIPT-QUALITY-001 |
| AI 压缩工作流标准 | [trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml) | GOV-DOC-011 |
| Session 状态机 | [session-state-runbook.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-session-state-runbook.md)（待创建） | OPS-VC-002 |
| 会话门禁 | [gate-runbook.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-gate-runbook.md)（待创建） | OPS-VC-005 |
| 事故响应 | [incident-runbook.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/ai-incident-and-emergency-runbook.md)（待创建） | OPS-VC-004 |
| Vibe Coding 入口 | [vibe_coding/index.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/index.md) | OPS-VC-001 |
| 模板 | [template_registry.yaml](file:///d:/ZephyrAlpha/docs/03_modules/template_registry.yaml) | REG-TEMPLATE-001 |

> 详细规则、施工指导、方法论参考 → 见 [`.trae/rules/onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
