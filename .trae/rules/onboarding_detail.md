# ZephyrAlpha AI 入职细则 — L1 施工指导与原理

> 本文件是 `project_rules.md`（L0）的详细补充。
> AI 不需要通读本文件——撞到 L0 铁律引用的命令时，命令的输出会指向此处。
> 也可以通过 Grep/SearchCodebase 按关键词检索对应章节。

---

## 一、四条铁律详解

### 1. 写入文件锁协议（RULE-ZERO）

**原理**: 多个 AI session 可能同时修改同一文件。锁通过原子目录创建实现互斥——同一时刻，一个文件只能被一个 session 写入。就像手术室一次只能进一个主刀医生。

**模式 A：直接锁（单 AI 对话默认）**:
```
BEFORE WRITE → CHECK  → python scripts/lock_files.py check <file>
               ↓
            FREE? → ACQUIRE → python scripts/lock_files.py acquire <file> <session_id> --task "简述"
               ↓
            LOCKED? → STOP. 报告用户：文件被 <owner> 锁定。
               ↓
AFTER WRITE  → RELEASE → python scripts/lock_files.py release <file> <session_id>
```

**模式 B：草稿模式（多 AI 并发推荐）**:
```
1. DRAFT  → from zephyr.trading.staging_area import StagingArea
            sa = StagingArea()
            sa.write_draft("<session_id>", "<file_path>", "<content>")
            # 写草稿到 .aidrafts/{session_id}/{file}（不获取排他锁）
2. EDIT   → 修改草稿内容（在 .aidrafts/ 下操作，不影响原文件）
3. COMMIT → result = sa.commit("<session_id>", "<file_path>")
            # 提交时获取锁+冲突检测+原子搬入+释放锁
            # result = OK / CONFLICT / CONFLICT_NEEDS_OWNER
4. 冲突?  → sa.try_auto_merge("<session_id>", "<file_path>")
            # 自动 rebase（简单冲突）或 CONFLICT_NEEDS_OWNER（复杂冲突）
```

**模式 B 实现**: `src/zephyr/trading/staging_area.py` — StagingArea 类。
- `write_draft(session_id, file_path, content)` — 写草稿到 `.aidrafts/`
- `commit(session_id, file_path)` — 提交草稿（冲突检测+原子写入）
- `try_auto_merge(session_id, file_path)` — 自动合并（简单冲突 rebase）
- `list_drafts(session_id)` — 列出会话草稿
- `discard(session_id, file_path)` — 丢弃草稿
- `get_conflict(session_id, file_path)` — 获取冲突详情

**模式 B 冲突检测机制**: 写草稿时记录原文件 mtime+hash 作为基线。提交时对比当前文件 mtime+hash 与基线——不一致则判定为 CONFLICT。

**session_id 格式**: `session-YYYYMMDD-NNN`。从 `session_logs/` 目录找到对应编号。

**批量操作**: 先对 N 个文件逐个 check → 全部 FREE 后逐个 acquire → 全部改完后逐个 release。一个被锁 = 释放已抢到的，等全部可抢再开工。

**读操作不需要加锁**。

**紧急清理**: `python scripts/lock_files.py cleanup`（清理 TTL 过期的死锁）+ `python scripts/lock_files.py status`（确认）

**底层实现**: 锁通过 `os.makedirs(exist_ok=False)` 原子目录创建实现互斥。`.ailocks/{sanitized_path}.lock/owner.json` = 锁持有者信息，`.ailocks/registry.json` = 全局锁注册表。TTL = 30 分钟——对话结束前必须释放，TTL 只是防崩溃的最后防线。

**规则真源**: [trae_001_file_operation_security.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) RULE-ZERO | 门禁: G0 | 实现: [lock_files.py](file:///d:/ZephyrAlpha/scripts/lock_files.py) + [staging_area.py](file:///d:/ZephyrAlpha/src/zephyr/trading/staging_area.py)

---

### 2. 创建文件协议（RULE-FOUR）

**核心**: `scripts/scaffold.py` 是唯一创建入口。绕过它创建的文件 = 孤儿——无注册，下一个 AI session 看不见。

**scaffold.py 自动完成**: 查重（文件名冲突 + 功能重复检测）→ 创建（temp-file + 原子 rename）→ 注册（__init__.py / script-manifest.yaml / _registry.yaml）→ 返回路径+导入命令。

**注册表映射**:
| 文件类型 | 创建命令 | 自动注册到 |
|----------|---------|-----------|
| `src/zephyr/<pkg>/<name>.py` | `scaffold.py module <pkg> <name>` | `<pkg>/__init__.py` `__all__` |
| `scripts/<path>/<name>.py` | `scaffold.py script <path>` | `scripts/script-manifest.yaml` |
| `src/zephyr/gates/<id>.yaml` | `scaffold.py gate <id>` | `src/zephyr/governance/rule_enforcement/_registry.yaml` |

**修改已有文件不走 scaffold**——走 RULE-ZERO 锁协议。

**孤儿检测**: `python scripts/governance/audit_registration.py`（每次 session 结束或 Pipeline Gate 运行时扫描）。exit 0 = CLEAN，exit 1 = 有孤儿。

**SSoT 创建门禁（三层防线）**: scaffold 查重维度3（module_path 冲突）是硬阻断。三层防线：L1 scaffold 主防线 → L2 GitCommitGateway 兜底 → L3 pre-commit hook 双保险。绕过 scaffold 直接 Write 新 .py 后 commit 会被 L2/L3 拦截。已知边界：`git commit --no-verify` 能绕过 L3，依赖 GATE-COMMIT-GW 规则约束。检测逻辑唯一真源：`capability_lookup.check_ssot_conflicts()`。详见 [check_ssot_gate.py](file:///d:/ZephyrAlpha/scripts/governance/check_ssot_gate.py)。

**规则真源**: [trae_001_file_operation_security.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) RULE-FOUR + [trae_015_arch_path_registration.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_015_arch_path_registration.yaml) | 实现: [scaffold.py](file:///d:/ZephyrAlpha/scripts/scaffold.py) | 验证: `python scripts/governance/audit_registration.py`

---

### 3. 删除文件协议（RULE-THREE）

**核心**: 删之前先证明它该死。不能证明 → 不许删。

**三步审判**:
```
STEP 1: 登记检查 — 文件是否在 manifest/registry/__init__.py 中被引用？在 git log 中存在？
  YES → 文件有价值。只能 refactor/rehome，不能 delete。

STEP 2: 重复检查 — 有另一个文件与它内容完全相同吗？那个文件在正确位置且已注册？
  YES to both → 真正重复，可以删。
  YES to first but NO to second → 两个都没注册！先决定保留哪个并注册。

STEP 3: 功能价值检查 — 零消费者≠无价值。判断标准：
  3a: 代码是否有独立功能价值？（即使当前无消费者，功能本身是否有意义）
  3b: 零消费者是否因客观原因？（自动化管线未接通、新模块尚未集成等）
  3c: 删除后是否需要重新实现？（如果将来需要类似功能，重建成本多高）
  ANY → 有功能价值 → 保留并接通（注册+集成），不删除。
  ALL → 无功能价值且无客观原因 → 可以删。
```

**临时文件也须过 STEP 3**: `_temp*` / `_check*` / `_phase_*` / `_audit*` 前缀文件删除前必须确认内容价值。

**规则真源**: [trae_001_file_operation_security.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) RULE-THREE + [trae_052_cross_blueprint_change_cleanup.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_052_cross_blueprint_change_cleanup.yaml)（价值判定）

---

### 4. 搜索先行协议（RULE-EIGHT）

**核心**: 在敲 `class` 或 `def` 之前，先敲三个搜索命令。不是"感觉没有"——是"搜索证明没有"。

**强制三步**:
```
STEP 1: 关键词全局搜索 → SearchCodebase + Grep（scripts/ + src/zephyr/ + tests/）
STEP 2: 注册表精确匹配 → registry_of_registries.yaml → 对应 REG-* → 对照
STEP 3: 复用决策（四选一）:
  - 完全覆盖 → 直接用
  - 80% 覆盖 → 扩展已有
  - 50% 覆盖 → 重构已有 + 扩展
  - 完全不覆盖 → 走 scaffold.py 新建
```

**复用证据**: 因"已有覆盖"放弃新建时，写 `[REUSE-DECISION] 放弃新建 <X>，因为已有 <Y> 覆盖了 <Z>`。

**后果量化**: 项目已有 483 脚本 + 43 门禁 + 4,639 模块 + 10 MCP 服务器。不搜索就新建 = 在 483 个脚本里造第 484 个重复。

---

## 二、并发写入安全（RULE-ONE + RULE-SEVEN）

### RULE-ONE: 原子写入

**背景**: Windows 上多进程同时写入同一目录时，Defender 实时扫描 + NTFS 目录元数据锁会造成进程级排队阻塞。

**强制模板**:
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

**原理**: 每个进程写自己的 PID-tmp 文件（互不冲突）+ `os.replace()` 在 NTFS 上是原子操作。

### RULE-SEVEN: 强制 ThreadPoolExecutor

**背景**: 2026-05-07 `for + subprocess.run()` 串行跑 296 个治理脚本 → 进程卡死 40 分钟。改为 `ThreadPoolExecutor(max_workers=8)` → 3.5 分钟。

**判定标准（机械判定）**:
- 指标 A: `for` 循环中调用 `subprocess.run/Popen`？→ MUST ThreadPoolExecutor
- 指标 B: `for` 循环中对多个文件独立读写？→ MUST ThreadPoolExecutor
- 指标 C: `for` 循环中对多个 URL/API 发起网络请求？→ MUST ThreadPoolExecutor

**为什么 ThreadPoolExecutor 而不是 multiprocessing**: subprocess.wait()/文件 I/O 释放 GIL（GIL 无影响）→ 轻量线程优于 spawn 进程。ZephyrAlpha 所有并行需求均为 I/O 密集型 → 只用 ThreadPoolExecutor。

**创建即自测**: 新建/修改脚本 → `python <脚本> --warn-only` → exit≠0 → 必须立即修复 → 重新自测 → exit 0 才能声明完成。

**操作序列**（写脚本时的完整工作流）: (1)写前判断：脚本里有没有 for+subprocess/I/O？有 → 先写 ThreadPoolExecutor 架子 (2)写后自测：立刻跑 `--warn-only` (3)修完才报完成：挂了自己修，修完再报"完成"

**后果量化**: 串行 296 个脚本 → 卡死 40 分钟。并行 → 3.5 分钟。串行不是"慢一点"，是"卡死"。

---

## 三、反孤儿与零残留（RULE-TWO + RULE-FIVE）

### RULE-TWO: 反孤儿功能

**核心**: 每个轮子都必须有车能用它。

**触发时机**: 写完文件的那一刻，MUST 自问——"这东西以后会被找到吗？还是说只有我知道它存在？"回答不了"会被找到" → 孤儿，还没做完。

**强制五问（新功能产出后自问）**:
| # | 问题 | 不满足 → 处置 |
|---|------|-------------|
| 1 | 谁调用它？入口在哪？ | 没有入口 → 不能关闭任务 |
| 2 | 谁发现它？下一个 AI session 怎么知道？ | 没有发现机制 → 必须先注册 |
| 3 | 谁维护它？放在哪个模块/目录下？ | 没有归属 → 不能落盘 |
| 4 | 谁校验它？有 gate 检查吗？ | 没有校验 → 必须添加 gate |
| 5 | 谁更新它？模板/清单/注册表已更新？ | 没有 → 必须更新 |

**注册判定原则**: 注册管理单元，不注册文件。需要注册 = 满足任一：独立生命周期 / 跨域消费者 / 需要治理决策 / 无法自然发现。已有可靠自然发现机制的豁免。详见 `project_rules.md` RULE-TWO 注册判定原则表。

**强制集成清单（每项新功能产出后 MUST 执行）**:

| 产出类型 | 必须集成到 |
|----------|-----------|
| 新 `.py` 脚本（`scripts/` 下） | `script-manifest.yaml` 注册 + `phase_manager` gate 引用 |
| 新 `.py` 模块（`src/zephyr/` 下） | 对应 `__init__.py` 导出 + 至少一个 import 引用点 |
| 新门禁/gate | `phase_manager.py` PHASE_SEQUENCE 注册 + `_registry.yaml` |
| 新设计模式/方法论 | `project_rules.md` 或 `AGENTS.md` + `rule-registry.md` TRAE 域 |
| 新增 RULE-* 到 `project_rules.md` | `rule-registry.md` TRAE 域强制登记 → `python scripts/governance/sync_rule_registry.py` 自动校验 |
| 新配置/数据文件 | 使用方代码中的显式路径引用 |
| 新 CLI 工具 | `script-manifest.yaml` + 用法写入相关 blueprint |
| 新测试文件（`tests/` 下） | 治理锚定表头（A_test 6字段简化版）+ pytest 命名约定。豁免注册表登记 |

### RULE-FIVE: 零残留

**核心**: 每个临时文件必须在 session 关闭前消失——要么归档，要么删除。不存在"留着以后再说"。

**后果预演**: 今天留的任何一个 `_temp*.py`，都会成为下个月某个 AI session 的困惑来源——"这个东西是谁建的？能不能删？"

**临时文件前缀**: `_temp*` / `_check*` / `_fix*` / `_phase_*` / `_deep*` / `_construction*` / `_rebuild*` / `_audit*`

**每日安检**: `python scripts/lock_files.py check-session <session_id>`

**规则真源**: [zero_residue.yaml](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_enforcement/zero_residue.yaml)（gate_id: ZERO-RESIDUE, ZR-001~009）

---

## 四、任务粒度边界（RULE-SIX）

**核心**: 不是所有动作都值得一张任务卡。但建不建卡是机械决定——不需要 AI 判断，只需要数数。

**八指标机械门**:
```
├─ 指标 1: 预计产生 > 50 行新代码？ → YES → 建 TaskCard
├─ 指标 2: 涉及修改 > 3 个文件？ → YES → 建 TaskCard
├─ 指标 3: 需要读取蓝图/设计文档？ → YES → 建 TaskCard
├─ 指标 4: 是数据库 Schema 变更？ → YES → 建 TaskCard
├─ 指标 5: depgraph 数据库操作(INSERT/UPDATE/DELETE)？ → YES → 建 TaskCard
├─ 指标 6: 消费者影响 > 50 个文件？ → YES → 建 TaskCard
├─ 指标 7: 跨域操作？ → YES → 建 TaskCard
├─ 指标 8: 多步骤施工 > 3 个步骤？ → YES → 建 TaskCard
└─ 全 NO → 直接做，不建卡
```

**建卡双触发机制**（RULE-ZERO-TASK）: 任务卡 MUST 通过 `TaskRepository.create()` 写入 SQLite，禁止手写 `.md` 建卡。建卡触发 = 用户主动 OR 八指标阈值触发。蓝图拆解是建卡来源之一，非唯一路径。

| 触发方式 | 适用场景 | 入口 |
|----------|---------|------|
| 用户主动触发 | 用户明确要求建卡 | `TaskRepository.create(task, allow_direct_create=True)` → TaskCard → SQLite |
| 阈值自动触发 | 八指标任一YES（AI按MTH-009先裁定后确认→建议建卡→Owner确认） | `TaskRepository.create(task, allow_direct_create=True)` → TaskCard → SQLite |

**建卡来源**（不再限于蓝图）:

| 来源 | 适用场景 | 入口 |
|------|---------|------|
| 蓝图拆解 | 有蓝图原文 | `BlueprintDecomposer.decompose(blueprint_path)` → TaskCard → SQLite |
| Bug修复/架构债务/代码扫描/重构任务 | 无蓝图原文 | `TaskRepository.create(task, allow_direct_create=True)` → TaskCard → SQLite |

`.md` 仅伴读副本，禁止作为创建入口。规则来源：trae_003_task_granularity_threshold.yaml RULE-ZERO-TASK。

**模板校验门禁**: `create()` 时自动校验18项必填字段（description/files_in_scope/deliverables/applicable_rules/allowed_touch/rollback_instructions/post_sync_standard/acceptance 等），缺字段直接拒绝建卡。

**粒度门禁（RULE-THIRTEEN）**: `create()` 时自动校验 R1-R6 六条规则（deliverables≤1 / files_in_scope≤3 / acceptance≤1 / construction_targets≤1 / description结构词 / description≥100字），超限直接拒绝建卡。

**超粒度自动拆分**: 建卡被粒度门禁拦截时，调用 `TaskRepository.auto_split_task(task)` 或 MCP `task_manager.auto_split(task_id)` 可按违规维度自动拆分为多张合规子卡。详见 `trae_034_task_card_standard.yaml §6.5`。

**完成门槛门禁**: `transition(task_id, COMPLETED)` 时自动执行 `post_sync_standard` 中的验证命令，任一命令 exit≠0 则拒绝完成（`SyncVerificationError`）。AI 不需要"记得"验证——系统强制执行。

**建卡后立刻施工**——不等用户确认。建卡是静默操作，施工才是对话主体。

**边界案例对照表**:

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
| depgraph 数据库 INSERT 新域 | 指标5 ✅ | ✅ |
| 大规模 import 更新（>50 文件） | 指标6 ✅ | ✅ |
| 跨域模块迁移 | 指标7 ✅ | ✅ |

---

## 五、强制 Session 冷启动序列

> 以下为 L0 "进门"步骤的完整展开。日常使用 L0 版本即可。新 AI 首次进入或深度任务时完整执行。

```
STEP 0  — 🛡️ RULE-GUARDIAN 守护进程启动 + 过期锁清理（非协商，任何平台进入必做第一步）:
           python scripts/lock_files.py cleanup
           python scripts/ide_health_service.py --status
           running=false → python scripts/ide_health_service.py --start-background
           running=true  → 继续
           ⚠️ 守护进程未运行 = 禁止执行任何后续步骤（含 STEP 1 及写操作）
STEP 0.5 — 🧠 大脑系统启动（单次 boot 模式，Trae AI 进入项目时必做）:
           检查: 查看当前 terminal 列表 → 是否有 start_brain.py 在运行？
           未运行 → RunCommand(blocking=false): python scripts/construction/start_brain.py --once
           已运行 → 跳过（避免重复启动）
           验证: 等待15秒 → 检查输出包含 "[OK] Boot" → 确认boot步骤成功
           ⚠️ CircadianScheduler 不常驻运行。
           所有审计/治理任务通过 pre-commit GATE（commit事件）和 boot_hooks（状态变更事件）自动触发。
           start_brain.py 现在以 --once 模式运行：执行 boot 后立即退出。
STEP 1  — 读 docs/registry_of_registries.yaml → 了解全项目 48 个注册表
STEP 1.1 — 读 docs/03_modules/template_registry.yaml → 了解可用模板（蓝图/任务卡/依赖图/策略/标准等）
STEP 1.2 — 提取 depgraph 摘要：`python scripts/governance/extract_depgraph.py --summary`（架构全景图+依赖图唯一真源，PostgreSQL 数据库 `depgraph` localhost:5432，禁止裸连）→ 项目域架构+模块归属+路径设计规则+capacity声明。连接用 `from zephyr.governance.depgraph_schema import get_depgraph_pg_connection`
STEP 1.2.1 — 提取文件级依赖：`python scripts/governance/extract_depgraph.py --paths`（文件级依赖关系，含设计态和运营态，真源 depgraph PostgreSQL）→ 文件依赖+迁移状态
STEP 1.2.2 — 路径树工具链（全景图维护，文件变更后必跑）:
           - 运营态目录树刷新: `python scripts/governance/generate_project_path_tree.py --write`（扫描磁盘→写入 depgraph 数据库 arch_directory_tree表。文件创建/删除/移动后MUST执行）
           - 运营态目录树检查: `python scripts/governance/generate_project_path_tree.py --check`（CI漂移检测，Session关门前必跑，G6_PT门禁）
           - 目标路径推导与对齐验证: 通过 `get_depgraph_pg_connection()` 查询 `SELECT path, blueprint_id FROM nodes WHERE design_maturity='production'`（派生产物已删除，depgraph 数据库是唯一查询入口，禁止重新创建 YAML 副本）
           - 架构文档路径树: `python scripts/governance/d5_architecture/generators/generate_path_tree.py`（读 depgraph 数据库→生成md文档，供人类查看）
STEP 1.5 — 读 docs/03_modules/_sys_master/blueprint.md §0 → 定位子系统任务域
STEP 2  — 读 project_rules.md（即 L0 首关页面）→ 了解硬规则
STEP 3  — Session Continuity 恢复: 上一个 session 做了啥 / 未完成任务 / 锁状态
STEP 4  — Phase Manager: 当前施工阶段（46 个门控检查）
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
STEP 4.15 — DepMap 依赖图: ⚠️ 禁止运行 generate_project_depgraph.py --output-db（裁定#207 R2 C2：破坏性DB重建需--force，DELETE运营态节点后从磁盘扫描重建，手工维护数据丢失）。depgraph 数据库是唯一查询入口，通过 `get_depgraph_pg_connection()` 或 `apply_depgraph.py --query` 查询。概览用 `python scripts/governance/extract_depgraph.py --summary`
STEP 5  — 按需定位具体注册表 → 开工
STEP 6  — **AutoPilot 自动驾驶**: 初始化 AutoPilot → status_report() → claim_next → 执行 → transition(COMPLETED) → 循环
           `from zephyr.trading.autopilot import AutoPilot; ap = AutoPilot(<session_id>); print(ap.status_report()); tasks = ap.run_cycle(max_tasks=3)`
           返回 tasks 列表 → AI session 逐任务执行 → 完成后 transition(COMPLETED) → 继续 run_cycle 直到无 READY 任务
```

---

---

## 六、强制集成对照表

> 这不是建议。这是 AI 行为的强制性映射——"你做什么" → "你必须先跑什么"。

| AI 要做什么 | 必须先执行的命令 | 不通过的后果 |
|------------|-----------------|-----------|
| **写入任何文件** | 见 L0 铁律 #1 | 禁止写入 |
| **创建新文件** | 见 L0 铁律 #2 | 禁止落盘 |
| **删除文件** | 见 L0 铁律 #3 | 禁止删除 |
| **新建功能** | 见 L0 铁律 #4 | 重复造轮子 |
| **遇到任何决策**（方案选择/范围裁定/触发条件判定/多选项权衡） | 读 trae_025 MTH-009 → 按"分析过程+裁定结果+确认请求"三段格式输出 → 引用 MTH-007 四问（埋雷/容量/对标/建议） | 裁定格式不全或只给选项不给推荐 → 禁止提交方案 |
| **修改 depgraph 数据库**（通过 apply_depgraph.py） | 见 trae_054 STEP0：① pg_dump 备份 `pg_dump -U zephyr -d depgraph > data/databases/backups/depgraph_backup_XXX.sql` ② 事务回滚：apply_depgraph.py 在事务内执行，失败自动 ROLLBACK（PG MVCC 保证） | 未备份 → 禁止执行 apply_depgraph.py |
| 修改 `src/zephyr/` 下源码 | `python -m pytest tests/ --collect-only -q` | 语法错误 → 禁止提交 |
| 修改 YAML 契约/配置 | `python scripts/governance/d5_architecture/checkers/check_contract_code_drift.py` | 契约断裂 → 禁止合并 |
| 修改 AGENTS.md | `python scripts/governance/d5_architecture/validators/validate_load_path_integrity.py --check` | LoadPath 断裂 → 禁止提交 |
| 修改 project_rules.md | `python scripts/governance/sync_rule_registry.py` | rule-registry 不同步 → 禁止提交 |
| 任何文件变更后 | `python scripts/governance/audit_registration.py` | 有孤儿 → 禁止关闭任务 |
| 写入文件后 | `python scripts/git_guard.py add <具体文件>` + `python scripts/git_commit.py --session <id> --files <f> --message <msg>`（RULE-TWENTY） | 未提交 = 代码丢失 → 禁止关闭任务 |
| 涉及安全敏感的变更 | `python scripts/governance/d6_security/scan_secret_leak.py` | 泄漏 → 硬阻断 CI |
| 创建依赖图 | 先读 `TPL-DEPGRAPH-001` 模板 → 按模板格式创建 → 验证蓝图双向链接 | 不符合模板 → 禁止提交 |
| Session 结束 | 见 L0 "Session 开关门 → 关门" | 不可关闭 |
| 进入新 Session | 见 L0 "Session 开关门 → 进门" + 本文件 §五 | 不可开工 |
| 按领域施工 | 查看 `data/capability_cards/` 目录（skill_*.yaml）→ 匹配 → Read 对应 yaml | 未加载 Skill → 盲目施工 |
| 施工前：检查已有知识 | `kb.search("<关键词>")` | 重复造轮子 / 违反已有决策 |
| 施工后：写入知识 | `kb.write(topic="...", content="...", provenance=build_provenance(...))` | 知识丢失 → 下个 session 不知道 |
| 回滚/撤销/undo | `python scripts/rollback.py preflight` → CLEAN → `rollback.py <cmd>` | preflight FAIL → 禁止回滚 |
| Agent 间协作/多 Agent | `GovernanceAdapter.verify_pair(a, b)` + Skill 路由 `a2a` | 静默失败 + 死锁无防护 |
| 高风险操作（批量/安全） | `EscalationEngine().evaluate(RuleCategory, desc)` | 可能执行应被 blocked 的操作 |
| 多 Agent/MCP 委托 | `DelegationEngine.delegate(event, strategy)` 遵循四级约束 | 死锁/循环委托/深度溢出 |
| LLM API 调用前 | `BudgetEngine().pre_flight_check(operation_id, tokens, cost)` | 超预算 → 降级或拒绝 |
| 任何写入/执行/修改前 | `PermissionGuard.check(identity, operation, target_path)` | BLOCKED → 禁止；AUTO_GUARD → 先干后验 |
| **新建/修改代码文件** | 添加防幻觉头部：`[BLUEPRINT]`/`[MODULE]`/`[DOMAIN]`/`[INVARIANTS]`/`[MODIFY-GUARD]`/`[CONSUMERS]`/`[STABILITY]`/`[SAFETY]`/`[AI_AUTONOMY]`/`[ERROR_CONTRACT]`/`[TESTS]` 十一字段 | 缺失 = 孤儿文件 → 禁止关闭任务 |
| **规格化蓝图** | 先 Layer 1（蓝图+施工图模板 v4.0 合规）→ 后 Layer 2（规格化砍削） | Layer 1 不通过 → 禁止砍削 |
| **规格化代码文件** | STEP 5.5：检查文件头部十一字段完整性 | 缺失 → 必须补充（规格化的"加"方向） |
| **蓝图-代码双向对齐** | 蓝图 frontmatter.file_manifest + dependency_graph ↔ 代码 `[BLUEPRINT]` 字段互相验证 | 不对齐 → 漂移，禁止关闭任务 |
| **三方对齐（全景图+蓝图+代码头部）** | 结构变更后 MUST 执行三方对齐：①全景图对齐: `diagnose_depgraph.py`（depgraph↔磁盘文件）②蓝图对齐: 蓝图frontmatter.file_manifest+dependency_graph↔实际代码 ③代码头部对齐: [BLUEPRINT]/[CONSUMERS]/[MODULE]↔实际引用。⚠️ 架构升级期间（阶段0-4）禁止运行 generate_project_depgraph.py（会覆盖 depgraph 数据库全景图）。仅 depgraph 数据库为真源。正常期: `python scripts/governance/generate_project_depgraph.py --max-workers 8` + `python scripts/governance/generate_project_path_tree.py --write` + 蓝图 frontmatter | 任一方过时 → AI 看到幻影/漏掉真实文件 → 禁止关闭任务 |
| **创建/删除/移动文件后** | `python D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write` | 路径树过时 → 下个 session 冷启动看到错误结构 → 禁止关闭任务 |
| **写代码时** | 禁止占位符：无 `TODO`/`...`/`pass`/`NotImplementedError` | 半成品 = 未完成 → 禁止关闭任务 |
| **修改文件** | 编辑优先 + 最小变更：surgical edit，禁止删+建，禁止顺手重构 | 丢失 history / 引入无关 bug → 禁止关闭任务 |
| **使用 import/API** | 导入验证：Grep/Read 确认存在后才使用 | 引用不存在的模块 → 语法错误 |
| **交付代码** | 自审闭环 + 新代码必测 + 安全最低通过 | 输出不匹配 / bug / 安全漏洞 → 禁止交付 |
| **不确定时** | 假设显式化：标记 `[ASSUMPTION]` 等待确认 | 静默假设 = 幻觉 → 禁止继续 |
| **大范围修改** | 计划先行 + 跨文件影响检查 | 失控 / 集成断裂 → 禁止执行 |
| **长对话** | 上下文新鲜度：>30 轮或矛盾 → 开新会话 | 上下文退化 → 幻觉温床 |
| **每步完成后** | 步骤验证门：验证当前步成功后才进下一步 | 错误累积 → 回溯成本指数增长 |
| **修改 PS-REG-012** | MUST 同步检查 PS-STD-001 对应章节 | 数据漂移 → 禁止关闭任务 |
| **修改 PS-STD-001** | MUST 同步检查 PS-REG-012 对应字段 | 规则漂移 → 禁止关闭任务 |
| **修改任何 trae_XXX 规则文件** | Read trae_030 全文（规则元文档，含 GOV-DOC-016 纯陈述原则 + GOV-DOC-017 规则抽象性原则） | 不读元规则 → 可能违反纯陈述/抽象性原则 → 禁止改规则 |

规则真源: [trae_001_file_operation_security.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_001_file_operation_security.yaml) + [gate_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml)（门禁注册表）

---

## 七、编码安全

| # | 规则 |
|---|------|
| 1 | Python `open(path, 'w')` 禁止省略 `encoding='utf-8'` |
| 2 | **禁止 PowerShell 语法**（RULE-SEVENTEEN）——RunCommand 只允许裸命令（python/git/pytest）。禁止管道\|、引号嵌套、$变量、cmdlet、>重定向、;串联。文件操作用 Read/Write/Edit/Glob/Grep/DeleteFile。复杂逻辑写 .py 脚本 |
| 3 | `files.autoGuessEncoding` = `false`, `files.encoding` = `utf8` |
| 4 | 禁止 Trae + Cursor 同时打开同一文件 |
| 5 | 扫描器大量报错 → 先检查扫描器本身的逻辑 |
| 6 | `.db` 文件存在性判断禁止用 LS/Glob（工具过滤 `.db` 扩展名会漏显示）。MUST 用 `python -c "import os; print(os.path.isfile(r'绝对路径'))"` 确认 |
| 7 | **git commit 免确认技巧**——RunCommand 直接调用 `git commit` 会触发 Trae 确认弹窗 + 被 GATE-COMMIT-GW 门禁阻断。正确方式：用 `python scripts/git_commit.py --session <id> --files <f> --message <msg>`（封装 GitCommitGateway，内部用 subprocess 调 git，绕过 Trae 弹窗 + 经串行锁+stash 隔离+GW 标记）。**禁止**写临时 .py 脚本裸调 `subprocess.run(["git", "commit", "--no-verify"])`——这绕过 GitCommitGateway，会被 post-commit 审计 reconciler 标记为违规 |

---

## 八、施工纪律

- 原子事务：关联修改同一批完成
- 脚本入库：新建 .py 立即注册到 script-manifest.yaml
- AI 受众优先：输出格式优先让 AI 零歧义消费
- 立即暂存（RULE-STAGE）：文件修改后 MUST 立即 `git add <具体文件>`。pre-commit 框架运行时会 stash 未暂存修改，hook 改文件后 stash pop 冲突 → 修改丢失。已暂存的修改不在 stash 范围内，不受影响。**改完不 add = 修改可能丢**

### 根源分析（MTH-006 触发）

**触发条件**：修改既有产物(代码/数据/规则/文档结构)即触发——pre_condition 强制；新增类操作可豁免深挖，但仍须诊断反转验证(step 6)

**核心机制——追问到底**：不是固定问5个为什么，而是**一直问，问到底**，直到找到最根部的原因。追问路上发现的每个中间问题 MUST 一并解决，不留尾巴。发现并发问题时 MUST 同时解决，不留给"以后"。

**判定标准**：

| | 治根 | 治标 |
|---|------|------|
| 修复后同类问题 | 不再产生 | 可能重现 |
| 修复作用层面 | 系统设计层面 | 当前实例 |
| 可否泛化 | 可描述为一条原则 | 无法泛化 |

**追问到底的操作序列**：
```
发现问题 → 问为什么 → 找到中间原因 → 这是根吗？
  ├─ NO → 继续问为什么 → 找到更深层原因 → 这是根吗？
  │   ├─ NO → 继续...
  │   └─ YES → 修复根因 + 修复路上发现的所有中间问题
  └─ YES → 修复根因
修复后验证：同类问题是否还会产生？YES → 没追到底，继续问
深挖后未发现系统性问题？→ 检查写法/表述是否制造了误解（MTH-006 规则7）
```

**常见症状→根因映射**：

| 症状 | 常见根因 | 治根方向 |
|------|---------|---------|
| 多处路径引用失效 | 系统按路径而非属性判定行为 | 改为属性推导引用 |
| 多文件字段冲突 | 概念在多处定义（非 SSoT） | 合并真源，其余改为引用 |
| 编号跳跃/不连续 | 编号规则未被显式定义 | 编号分配铁律（见 PS-STD-001 §5.4） |
| 相似规则在多个文件重复 | 文件边界未按责任单一原则划分 | 按唯一职责重新划分文件边界 |
| 修完文件后发现目录缺文件 | 诊断时跳过结构盘点直接修字段 | 先结构前置检查→补全→再修字段 |

**根因结论（从 RULE-ZERO~NINE 压缩时保留）**：

| RULE | 根因判定 |
|------|---------|
| RULE-THREE | 文件未在 `_registry.yaml` 中被单独登记，删除前未逐行验证内容价值 |
| RULE-FOUR | 手工流程依赖 AI 记忆 → 遗忘 → 孤儿 → 注册表滞后不可信 |
| RULE-FIVE | 没有强制自净机制——AI 干完活留临时文件，下一个 session 永远不会主动清理 |
| RULE-SIX | AI 无法执行"应该"——它只能执行"是/否"，含主观判断的规则形同虚设 |
| RULE-SEVEN | AI 默认写串行代码——`for`+`subprocess.run()` 是最自然的第一反应 |
| RULE-EIGHT | RULE-TWO 规定了"创建后必须注册"但没规定"创建前必须搜索已有" |

**详见**：[trae_024_methodology_diagnosis.yaml MTH-006](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml)

### 慢/卡死脚本诊断 SOP（PERF-001 触发）

> 脚本跑着跑着卡了/超时/无响应 → 直接改代码 = 治标不治本。先诊断。

**触发条件（机械判定）**：

| 脚本类型 | 触发条件 |
|---------|---------|
| 短脚本（预期 ≤30s） | 超预期 2x 或 2 分钟无输出 |
| 长脚本（预期 >30s） | 超预期 1.5x 或 3 分钟无输出 |

**十项检查流程**：

```
遇到慢/卡死 → ① 基线对比 → 确认异常？
  ├─ NO → 记录基线，关闭
  └─ YES → ② 分阶段计时 → 找瓶颈阶段
       → ③ 输入规模 → ④ 功能必要性 → ⑧ 输出规模（数据层）
       → ⑤ 资源消耗 → ⑥ 死循环 → ⑦ 静默挂起（运行层）
       → ⑨ 增量缓存 → ⑩ 超时熔断（防护层）
       → 修复 → 重新计时 → 确认达标
```

| # | 检查项 | 方法 | 不通过→处置 |
|---|--------|------|-----------|
| ① | 基线对比 | 历史运行时间 / 同类脚本对比 | 进入②-⑩ |
| ② | 分阶段计时 | `time.perf_counter()` 找耗时 > 50% 的阶段 | 针对性优化 |
| ③ | 输入规模 | 统计输入量、排除不该扫的文件 | 缩小范围或加排除规则 |
| ④ | 功能必要性 | 每个输出字段/步骤是否有消费者 | 删冗余输出 |
| ⑤ | 资源消耗 | CPU/内存/磁盘 IO | CPU<5% → 等IO/锁；内存>80% → swap |
| ⑥ | 死循环/无限等待 | `while True` / `queue.get(timeout=None)` | 加超时 |
| ⑦ | 静默挂起 | `except: pass` 吞异常 | 改为 `except Exception as e: print(e)` |
| ⑧ | 输出规模 | 冗余数据占比 > 30% → 瘦身 | 删冗余字段或增量输出 |
| ⑨ | 增量/缓存 | 全量重算 + 变化 < 5% → 应增量 | 加文件 mtime 检测 / 哈希缓存 |
| ⑩ | 超时熔断 | 无 `--timeout` → 必须加 | 加 `argparse --timeout` + `signal.SIGALRM` |

**建卡判定**：
- < 5 分钟修复（加超时/加日志/删冗余）→ 直接修，不建卡
- 5-30 分钟修复（优化算法/加缓存）→ **建卡**
- > 30 分钟修复（重构/增量机制）→ **建卡，拆分多步**

**SSoT**：[trae_034_task_card_standard.yaml §9 PERF-001](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml)

---

## 九、修改原则（第一性原理）

| # | 规则 |
|---|------|
| 1 | 发现事实错误 → 直接修正数字/名称/路径/状态。禁止添加解释性段落说明"之前为什么是错的" |
| 2 | 文档中所有数字、字段数、版本号、计数必须是当前唯一真实值。不留"X到Y变更描述"的过渡文本 |
| 3 | 历史版本差异通过变更日志追踪，不在正文中保留已过时数据 |
| 4 | 单个 real number 原则：一个事实在所有蓝图中只能有一个数字。N 处出现 = 同一数字，不一致就是 bug，直接修 |

---

## 十、极简产出标准

> 规则真源: [trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（文档编号与元数据 + 产出物规格化）

### 10.1 核心原则

**为 AI 消费优化，不是为人类阅读优化。** Token = 成本 = 注意力预算。每个字必须有信息增量。

> 本节是 [TRAE-057 AI消费优先原则](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_057_ai_consumer_first.yaml) §1 的施工展开。TRAE-057 是顶层原则，本节是其具体施工指导。

### 10.2 格式优先级

```
表格 > 命令 > 一句话 > 段落 > 散文
```

能用表格的不用段落。能写命令的不写描述。不写"为什么"和"对标"——那不是当前 token 预算该花的。

### 10.3 各产出类型 Token 预算

| 产出类型 | Token 上限 | 格式要求 | 示例 |
|---------|:---:|------|------|
| IDE 规则文件 (L0) | ≤500 | 表格+命令。零散文 | project_rules.md |
| 蓝图 §0 分派表 | ≤400 | 表格。一页内 | blueprint.md §0 |
| 蓝图正文 | ≤3000/章 | 模板强约束 | blueprint_construction_template.md（蓝图+施工图模板） |
| 施工指导 | ≤2000 | 步骤式。禁止"为什么"段落 | onboarding_detail.md |
| TaskCard | 不限 | 一卡一任务。拆卡四条机械规则：R1 deliverables>1 / R2 files_in_scope>3 / R3 acceptance独立验收点>1 / R4 施工步骤跨>1个施工目标 | GOV-TASK-001 §6 |
| AI 对话输出 | ≤500/条 | 结论先行。背景后置 | — |
| 代码注释 | 0（禁止） | blueprint 是 SSoT | — |

### 10.4 删掉清单（AI 产出中禁止出现的段落类型）

| 禁止出现 | 原因 | 举例 |
|---------|------|------|
| "为什么"解释段 | L2 背景知识，不应占当前 context | "这个设计的原理是..." |
| "对标"段 | AI 不需要文化类比来执行规则 | "对标 K8s ResourceQuota..." |
| "历史/触因"段 | git log 里，不在正文里 | "2026-05-07 触发了这个规则..." |
| "AI 意识植入"散文 | 人类散文，AI 不需要 | "你创建的每一个临时文件..." |
| 过渡/桥梁句 | 多一个字都是浪费 | "接下来让我们看看..." |
| ASCII/mermaid 图 | 条件判定：图中信息在表格/步骤中已表达 → 冗余 | 状态机的 ASCII 框图和状态转换表说同一件事 |

### 10.5 判定标准

写完后问自己两问：

> **1. 删掉这一句，AI 还会做错吗？** — 不会 → 删。
> **2. 这一句在 Token 预算表里属于 L0/L1/L2？** — 当前不在对应层 → 移到对应层或删。

### 10.6 产出物规格化安全协议

> **完整方法论** → [GOV-DOC-011 trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)（触发条件 / 优化前三步 / 分类型策略 / 安全原则 / 优化后步骤）。
> 以下是速查版——安全清单 + 全项目优化批序。每次优化前必读。

**可以删的 5 类（只此 5 类）**:

> ⚠️ **豁免**: 施工规格（协议定义、函数签名、触发逻辑、验收标准、跨系统影响分析）不在此列——施工规格永不压缩。压缩施工规格 = AI 不知道怎么做 = 产生幻觉或错误。

| 可删类型 | 示例 |
|---------|------|
| "大白话解释"/"大白话总结"段落 | AI 不需要人类翻译 |
| "对标 K8s/ITIL/Unix/..."长篇对比段落 | 专业框架映射表保留 |
| "AI 意识植入"散文 | "你创建的每一个临时文件都是对未来的承诺..." |
| "修订记录/变更历史"段落 | git log 已有 |
| ASCII/mermaid 流程图 | AI 不需要视觉化（**条件**：图中的信息已在表格或步骤中完整表达 → 可删。表和图中信息不一致 → 保留图） |

**绝对不可删的 15 类**:

| 不可删 | 举例 |
|--------|------|
| frontmatter 字段 | module_id, title, version, layer, depends_on, tags, **ttl（必填，2 值：permanent/task_bound）**。过程文档默认落 [`docs/_working/`](file:///d:/ZephyrAlpha/docs/_working/)（task_bound）；判定见 [`ttl_vocabulary.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 `decision_tree` |
| 路径 | 绝对路径 `d:/ZephyrAlpha/...` 和相对路径 |
| module_id 引用 | MOD-INF-XXX, PS-STD-XXX |
| 命令和代码模板 | `python scripts/...`、代码块 |
| 表格 | 状态表、映射表、对照表、约束表 |
| "禁止/必须/SHOULD/MUST"约束 | 所有约束语句 |
| 漂移防护语句 | "修改此文件必须同步更新 X/Y/Z" |
| 异常处理表格和流程 | 所有异常处理 |
| 状态不变量约束 | 所有状态不变量 |
| depends_on 依赖声明 | 所有依赖声明 |
| 触发条件/适用场景 | "何时应执行此规则"的判定逻辑 |
| 完成标准/通过条件 | "此流程完成"的 exit criteria |
| 多步流程中的步骤 | 不可部分删除——删一步则全流程断裂 |
| 可解析引用 | 项目术语 KB 决策记录/KB/TaskCard/Gate 后必须有路径 |
| 导航路径/冷启动序列 | "新 AI 如何找到这个文件、如何开始使用"——命令链或 3-5 步路径 |
| **施工规格** | **协议定义（字段级）、函数签名（参数+返回类型）、触发逻辑（scheduler 注册参数）、验收标准（机械可判定 exit code+预期输出）、跨系统影响（上游调用点+下游消费者）** |

**优化顺序（逐文件执行，每次只改一个）**:

| 批次 | 文件 | 操作 |
|:---:|------|------|
| 1 | `.trae/rules/project_rules.md` | 压缩到 ~80 行 L0，砍掉"原理""对标""AI 意识植入""触因/根因" |
| 1 | `.trae/rules/onboarding_detail.md` | L1 文件，保留所有表格/命令/约束 |
| 1 | `AGENTS.md` | 去重，交叉引用 L0 |
| 1 | `CLAUDE.md` | 去重，交叉引用 L0 |
| 2 | `README.md` | 版本号/路径修正，加 AI 规则入口 |
| 2 | 根目录临时文件 | 移到 `C:\Users\fanzi\AppData\Local\Temp\临时工作区\` |
| 3 | `agent_spec/AGENTS.md` | 已迁移到 `data/capability_cards/`，本项跳过 |
| 3 | `trae_024_methodology_diagnosis.yaml` | 保留 frontmatter+总则+决策链+13 原则+框架映射表 |
| 4 | `trae_010_code_naming_organization.yaml` | 保留 frontmatter+命名表+文件组织+类型层级+导入+SSoT 守卫(命名规则真源见trae_028_doc_structure_naming.yaml) |
| 4 | `quality_standard.md` | 保留 frontmatter+8 维度+6 点验收+3 模板+禁止清单+41 条提纲 |
| 5 | `vibe_coding/` (4 个文件) | 逐文件处理，session-state-runbook 完整保留 |
| 6 | `data/capability_cards/skill_dom_*.yaml` (19 个) | 保留 CRITICAL Rules+Core Ops+Constraints+Error Patterns+Checklist+Constants+References |
| 7 | `data/capability_cards/skill_rol_*.yaml` (3 个) | 保留 CRITICAL Rules+Workflow+References |

### 10.7 对话输出反幻觉验证

**适用范围**：AI 对话输出的所有内容（报告、方案、构思、分析、清单），不限于落盘文件。

**核心原则**：对话输出中的事实性数据 MUST 来自实际命令输出，禁止凭模式生成。

**强制自审两次**：

```
对话输出前 → 自审第1次 → 发现问题 → 修正 → 自审第2次 → 零问题 → 输出
                                  ↓ 有问题
                          修正 → 自审第2次 → ... → 连续两次零问题 → 输出
```

**机械可判定检查清单**：

| # | 检查项 | 判定标准 | 不通过→处置 |
|---|--------|---------|------------|
| 1 | 数据来源 | 报告中的域名/数字/路径是否都有对应命令输出？ | 重新查询数据 |
| 2 | 模式生成 | 是否存在凭命名模式（如D-XXX-YYY）编造的数据？ | 删除编造数据，重新查询 |
| 3 | 数量核对 | 报告中的总数是否与命令输出一致？ | 重新运行命令核对 |
| 4 | 行级对应 | 报告表格每一行是否能在命令输出中找到对应？ | 逐行核对修正 |
| 5 | 重新验证 | 报告生成后是否重新运行验证命令核对？ | 补跑验证命令 |

**不通过处置**：任一项不通过 → 重新查询数据 → 修正报告 → 重新自审 → 连续两次零问题才能输出。

**典型幻觉场景**：

| 场景 | 幻觉表现 | 正确做法 |
|------|---------|---------|
| 域名清单 | 凭D-XXX-YYY模式编造不存在的域名 | 查询depgraph数据库获取实际域名 |
| 模块清单 | 凭路径模式编造不存在的模块 | Grep/Read获取实际模块 |
| 数字统计 | 凭印象填写数量 | 运行统计命令获取实际数字 |
| 依赖关系 | 凭逻辑推断编造依赖边 | 查询domain_dependencies表 |

---

## 十一、L2 知识库索引

> 以下内容不在本文件中，按需检索：

| 内容 | 位置 | Token |
|------|------|:---:|
| 治理方法论 13 原则 (MTH-001~013) | [`trae_024_methodology_diagnosis.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_024_methodology_diagnosis.yaml) | ~3500 |
| 代码构建标准（命名/文件组织/类型注解） | [`trae_010_code_naming_organization.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_010_code_naming_organization.yaml) | ~1500 |
| 编码约定（L3 implementer 专属） | `src/zephyr/agent-spec/references/coding_conventions.md`（待创建） | ~350 |
| 审计脚本质量标准（8 维度） | [`quality_standard.md`](file:///d:/ZephyrAlpha/scripts/governance/quality_standard.md) | ~3500 |
| Vibe Coding 施工方法论 | `docs/03_modules/_sys_master/blueprint.md` §十五 | ~2000 |
| Session 状态机（5状态/7转换） | [`session-state-runbook.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-session-state-runbook.md)（待创建） | ~800 |
| 会话门禁检查清单（12项） | [`gate-runbook.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-gate-runbook.md)（待创建） | ~600 |
| AI 事故响应手册（P0/P1/P2） | [`incident-runbook.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/ai-incident-and-emergency-runbook.md)（待创建） | ~1500 |
| Vibe Coding 操作入口 | [`vibe_coding/index.md`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/index.md) | ~300 |
| 术语表 | `docs/01_policies_and_standards/_registry/vocabularies/glossary.yaml`（待创建） | ~1000 |
| 规则体系总索引 | `docs/01_policies_and_standards/index.md` | ~500 |
| **AI 压缩工作流标准** | [`trae_030_doc_numbering_metadata.yaml`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml) | ~800 |

---

## 十二、防幻觉十八条详解

> L0 已列出十八条铁律。本节展开每条的操作定义和判定标准。

### 12.1 结构追溯层（#1-#6）

已在 L0 + trae_010_code_naming_organization.yaml §7 完整定义。此处补充十一字段总览：

| # | 字段 | 必填 | 枚举值/格式 | 对齐 PS-REG-012 |
|---|------|:---:|-----------|:---:|
| 1 | `[BLUEPRINT]` | ✅ | `{module_id} | {path} | §{N}` | — |
| 2 | `[MODULE]` | ✅ | `{full.module.path}` | — |
| 3 | `[INVARIANTS]` | ✅ | 分号分隔 | — |
| 4 | `[MODIFY-GUARD]` | ✅ | 分号分隔 | — |
| 5 | `[CONSUMERS]` | ⚠️ | 分号分隔 | — |
| 6 | `[STABILITY]` | ✅ | `frozen/stable/evolving/volatile` | ✅ 复用 stability |
| 7 | `[SAFETY]` | ✅ | `H/M/L` | ✅ 复用 safety_level |
| 8 | `[AI_AUTONOMY]` | ✅ | `immutable_core/human_gated/ai_modifiable` | ✅ 复用 ai_autonomy |
| 9 | `[ERROR_CONTRACT]` | ⚠️ | 分号分隔 | — |
| 10 | `[TESTS]` | ⚠️ | 分号分隔 | — |
| 11 | `[DOMAIN]` | ⚠️ | `D-XXX`（覆盖路径派生，仅跨域模块需填） | — |

**`[AI_AUTONOMY]` 与修改行为的关系**：

| `[AI_AUTONOMY]` 值 | AI 能做什么 | 违反后果 |
|:---:|------|---------|
| `immutable_core` | AI 只读。禁止 AI 自主修改；Owner 批准后可通过任务卡通道修改（依据 ABS-01/META-001："AI 禁止**自主**修改"） | 未批准就改 = 越权 |
| `human_gated` | 可提议修改，需 Owner 批准 | 未批准就改 = 越权 |
| `ai_modifiable` | 可直接修改 | — |

**`immutable_core` 例外通道（Owner 批准后修改流程）**：

| 步骤 | 操作 | 依据 |
|------|------|------|
| 1 | Owner 审批任务卡（含修改范围+回滚方案） | ABS-01/META-001 |
| 2 | AI 加锁目标文件（RULE-ZERO） | L0 铁律 #1 |
| 3 | AI 执行修改（仅限任务卡批准范围） | 最小变更原则 |
| 4 | 验收命令通过后释放锁 | 步骤验证门 #11 |
| 5 | 更新任务卡状态为 COMPLETED | 完成门槛门禁 |

**`[STABILITY]` 与修改策略的关系**：

| `[STABILITY]` 值 | 修改策略 | 违反后果 |
|:---:|---------|---------|
| `frozen` | 禁止修改 | 修改 = 破坏不变量 |
| `stable` | 需变更门控 | 跳过门控 = 漂移 |
| `evolving` | 可频繁修改 | — |
| `volatile` | AI 可自主调整 | — |

### 12.2 行为约束层（#7-#10）

**#7 禁止占位符**

| 判定 | 示例 | 处置 |
|------|------|------|
| `TODO` / `FIXME` / `HACK` | `# TODO: implement error handling` | 禁止。必须实现 |
| `...`（Ellipsis）作为函数体 | `def process(): ...` | 禁止。必须写完整实现 |
| `pass` 作为唯一函数体 | `def validate(): pass` | 禁止。必须写完整实现 |
| `NotImplementedError` | `raise NotImplementedError` | 禁止。必须实现或拆分任务 |
| `# implement later` / `# will add` | `# will add validation later` | 禁止。现在就实现 |

**豁免**: 抽象基类的 `@abstractmethod` + `raise NotImplementedError` 是合法的——它声明了接口契约，不是偷懒。

**#8 编辑优先**

| 判定 | 禁止 | 正确做法 |
|------|------|---------|
| 修改文件内容 | 删除文件 → 重新创建 | SearchReplace 精确替换 |
| 修改函数 | 删掉整个函数重写 | 只替换变更的行 |
| 修改类 | 删掉整个类重写 | 只替换变更的方法/属性 |

**判定标准**: `git diff` 中出现 `-` 整文件删除 + `+` 整文件新增 → 违反 #8。正常 diff 应只有少量 `-`/`+` 行。

**#9 最小变更**

| 允许 | 禁止 |
|------|------|
| 修复指定 bug 的最小改动 | "顺便"重命名变量 |
| 添加指定功能的最小代码 | "顺手"优化相邻函数 |
| 按需求修改的精确行 | "顺便"调整代码风格 |

**判定标准**: diff 中任何与需求无关的变更 → 违反 #9。用户说"修 X"→ diff 只能有修 X 的行。

**#10 假设显式化**

| 场景 | 标记方式 | 处置 |
|------|---------|------|
| 不确定 API 返回格式 | `[ASSUMPTION] API 返回 JSON {status: str}` | 标记后继续，等用户确认 |
| 不确定配置值 | `[ASSUMPTION] MAX_RETRIES = 3` | 标记后继续，等用户确认 |
| 不确定文件路径 | `[ASSUMPTION] 配置文件在 data/config.yaml` | **禁止假设路径**——必须 Grep 确认 |
| 不确定函数签名 | `[ASSUMPTION] process() 接受 str 参数` | **禁止假设签名**——必须 Read 确认 |

**路径和签名假设 = 禁止**。这两类假设是幻觉最高发区域，必须验证。

### 12.3 输出验证层（#11-#14）

**#11 步骤验证门**

```
每步完成后强制自检：
STEP N 完成 → 运行验证命令 → exit 0? → 进 STEP N+1
                        → exit ≠ 0? → 修复 → 重新验证 → exit 0 → 进 STEP N+1
禁止：STEP 1 → STEP 2 → STEP 3 → 回头发现 STEP 1 就错了
```

**#12 导入验证**

| 操作 | 验证方式 |
|------|---------|
| `from zephyr.xxx import Yyy` | Grep `class Yyy` 或 Read 目标文件确认存在 |
| `import some_library` | Grep `requirements.txt` / `pyproject.toml` 确认已安装 |
| 调用 `obj.method()` | Read `obj` 的类定义确认 `method` 存在 |
| 使用 `config.KEY` | Read 配置文件确认 `KEY` 存在 |

**#13 自审闭环**

产出代码后 MUST 逐项检查：

| 检查项 | 判定标准 |
|--------|---------|
| 功能完整 | 需求的每个点都有对应实现 |
| 边界处理 | 空输入 / 零值 / None / 超长输入 有处理 |
| 错误路径 | try/except 覆盖所有可能失败点 |
| 类型一致 | 函数签名类型与实际使用一致 |
| 导入完整 | 所有使用的类型/函数都已导入 |

**#14 新代码必测**

| 场景 | 要求 |
|------|------|
| 新建模块 | MUST 创建 `test_{module}.py` |
| 修改函数 | MUST 更新或添加对应测试用例 |
| 修改 Bug | MUST 添加回归测试 |
| 豁免 | `__init__.py` / 纯配置 YAML 不需要测试 |

### 12.4 安全防护层（#15-#18）

**#15 安全最低通过**

交付前 MUST 三项检查：

| 检查 | 内容 | 不通过 → 处置 |
|------|------|-------------|
| 认证检查 | 敏感操作是否有权限控制 | 缺失 → 必须添加 |
| 注入检查 | SQL/命令/路径 是否有参数化 | 拼接 → 必须参数化 |
| 数据暴露 | 日志/错误信息 是否泄露敏感数据 | 泄露 → 必须脱敏 |

**#16 计划先行**

触发条件（任一满足即触发）：
- 修改 > 3 个文件
- 新增 > 50 行代码
- 涉及 > 2 个模块的接口变更
- 数据库 Schema 变更

执行流程：
```
1. 输出计划（改哪些文件、改什么、为什么）
2. 等待用户确认
3. 按计划执行
4. 执行后验证
```

**#17 跨文件影响检查**

修改文件前强制三步：
```
STEP 1: 读取文件头部 [CONSUMERS] 字段 → 列出所有消费者
STEP 2: Grep 项目中所有 import/引用该文件的位置
STEP 3: 评估修改对每个消费者的影响 → 无影响 → 继续 / 有影响 → 同步修改
```

**#18 上下文新鲜度**

| 信号 | 判定 | 处置 |
|------|------|------|
| 对话轮数 > 30 | 上下文退化风险 | 建议开新会话 |
| AI 输出与之前矛盾 | 上下文已污染 | 必须开新会话 |
| AI 重复相同输出 | 陷入循环 | 必须开新会话 |
| AI 忘记之前确认的决策 | 上下文溢出 | 必须开新会话 |

---

## 十三、治理施工流程（RULE-TEN）

> **触发条件**：对项目结构做任何非平凡变更——移动模块、拆分包、重构依赖、批量修改标签。
> **核心原则**：先推演再动手。推演不过 = 禁止执行。

### 13.1 14步统一流程（RULE-TEN）

**触发**：对项目做任何非平凡变更——恢复功能、新建功能、移动模块、拆分包、重构依赖、批量修改标签。

| 阶段 | STEP | 名称 | 做什么 |
|------|:---:|------|--------|
| 分析设计 | 1 | 读蓝图 | 读取功能对应蓝图，理解设计意图 |
| 分析设计 | 2 | 全量定位 | 全项目搜索所有相关文件（本包+孤儿+重复+跨蓝图） |
| 分析设计 | 3 | 归属裁定 | 孤儿纳入/重复去重/跨蓝图归属裁定 |
| 分析设计 | 4 | 蓝图设计 | 在蓝图里设计依赖关系+启动方式+自动运行+自动结束 |
| 施工 | 5 | 位置校验 | 按蓝图设计调整文件位置/命名/注册 |
| 施工 | 6 | 修复断链 | 按蓝图设计的依赖关系修复import断链 |
| 施工 | 7 | 补全头部 | 补全文件头部十字段 |
| 施工 | 8 | 运行测试 | pytest运行功能测试 |
| 施工 | 9 | 修复失败 | 修复失败测试直到通过 |
| 安全验证 | 10 | 红蓝对抗 | 罗列极限测试清单+执行+修复漏洞 |
| 收尾对齐 | 11 | 更新蓝图 | 将实际状态写回蓝图frontmatter |
| 收尾对齐 | 12 | 三方对齐 | 全景图+蓝图+代码头部三方一致验证 |
| 收尾对齐 | 13 | 更新索引 | 更新所有相关INDEX/注册表/manifest |
| 收尾对齐 | 14 | 报告 | 向统筹AI报告状态 |

**核心原则**：先分析再动手，先设计再施工。跳过任何步骤 = 违规。

**轻量模式**：当变更仅涉及文件移动/重命名/依赖调整，不涉及功能恢复/新建时，可使用5步轻量模式：依赖图推演→蓝图归属→导入路径映射→执行操作→验证。

**详细规格**：→ 参见 `docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md §2.3`

### 13.2 推演方法（STEP 1 详解）

对每个拟执行的变更（移动模块/拆包/改标签），MUST 回答以下问题：

| # | 问题 | 判定标准 |
|---|------|---------|
| 1 | 变更后是否产生新的循环依赖？ | 任何新循环 → **BLOCKED**，必须先解决循环。**同层循环也禁止**（同层单向允许，禁止形成环） |
| 2 | 变更后跨包违规是增还是减？ | 减少或不变 → **SAFE**；增加但都是向下依赖 → **CAUTION**；增加且是向上依赖 → **BLOCKED**（DIP例外见下） |
| 3 | 目标包是否有蓝图？ | 有蓝图 → OK；无蓝图 → **NEEDS NEW BLUEPRINT**，先建蓝图再移动 |
| 4 | 受影响的 import 有多少？ | 列出完整清单，逐一更新，不能遗漏 |
| 5 | 是否涉及编排器依赖？ | 编排器(F1)→下层contract/event依赖 = **DIP例外**，不计入逆向依赖（依赖抽象接口/事件总线，非具体实现） |

**判定结果**：
- **SAFE**：减少违规，无新循环 → 可立即执行
- **CAUTION**：增加少量向下依赖（专用包→shared基础层），无新循环 → 可执行，但需记录新增的跨包边
- **BLOCKED**：产生新循环（跨层或同层）或向上runtime依赖 → 禁止执行，必须先解决阻塞
- **DIP例外**：编排器→下层contract(抽象接口)/event(事件总线)依赖不视为逆向依赖——对标K8s CRI/CSI、Netflix Conductor Worker API

> 详见 [core_function_dependency_design.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/core_function_dependency_design.md)（37个功能依赖设计真源，含四种依赖类型定义）

### 13.3 治理顺序的因果链

治理项之间有**因果关系**——前面的决定会影响后面的问题是否还需要做。**必须按因果链从根到叶执行，不能按数量从大到小。**

```
第1层：架构决定（定义"应该是什么样"）
  ↓ 决定了包间依赖规则
第2层：结构重构（让代码匹配架构）
  ↓ 重构后，God模块、孤儿、深链自动减少
第3层：元数据对齐（标签和注册）
  ↓ 标签对了，稳定性/自治违规自动消失
第4层：质量补全（测试覆盖）
  ↓ 前面都稳定了，测试才有意义
```

**具体执行顺序**：

| 顺序 | 治理项 | 为什么先做 | 做完后什么会减轻 |
|:---:|--------|-----------|----------------|
| 1 | 跨包违规（架构重构） | **根因**：shared/ 被所有包导入，职责不清 | God模块↓、深链↓、孤儿↓ |
| 2 | God模块分解 | 依赖#1：包边界清晰后才知道该拆什么 | fan_out/fan_in↓ |
| 3 | 孤儿模块消理 | 依赖#1+#2：重构后很多"孤儿"自然获得消费者 | 孤儿↓ |
| 4 | 空 blueprint_id | 依赖#1：重构后模块归属可能变化 | — |
| 5 | 稳定性/自治违规 | 依赖#1+#4：架构和标签都稳定后才能准确判断 | 可能全部消失 |
| 6 | 测试覆盖 | **最后做**：前面重构会改代码，先重构再写测试 | — |

**禁止**：看到"测试缺口最多"就先补测试——重构会改代码，测试白写。

### 13.4 价值判定原则（RULE-THREE 补充）

**零消费者≠无价值。** 判断模块是否该删除/移动，看功能价值，不看消费者数量。

| 判定维度 | 问题 | 答案=YES → |
|---------|------|-----------|
| 3a 独立功能价值 | 代码是否有独立功能？ | 保留并接通，不删除 |
| 3b 客观原因 | 零消费者是否因管线未接通？ | 保留并接通，不删除 |
| 3c 重建成本 | 删除后是否需要重新实现？ | 保留，不删除 |

**ANY → 有功能价值 → 保留并接通，不删除。**

典型例子：
- `kill_switch.py` 零消费者 ≠ 能删。安全紧急制动，必须有。
- `capacity_calibrator.py` 零消费者 ≠ 能删。容量治理核心，只是未接通。
- `alert_manager.py` 零消费者 ≠ 能删。告警系统组件，管线未完成。

### 13.5 验证命令（STEP 5 详解）

每次结构变更后 MUST 依次执行：

```bash
# 1. 重新生成依赖图（⚠️ 架构升级期间禁止运行——会覆盖 depgraph 数据库全景图）
# python scripts/governance/generate_project_depgraph.py --max-workers 8  # 正常期才运行

# 2. 诊断依赖图
python scripts/governance/diagnose_depgraph.py

# 3. 重新生成物理路径树
python D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write

# 4. 注册审计
python scripts/governance/audit_registration.py

# 5. 关键模块导入测试
python scripts/governance/verify_key_imports.py
```

**任何一步失败 = 回滚变更。**

### 13.6 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 不推演直接移动模块 | 引入新循环依赖，系统堵塞 |
| ❌ | 不检查蓝图归属就移动 | 模块变成蓝图孤儿 |
| ❌ | 移动后不更新所有 import | 运行时 ImportError |
| ❌ | 移动后不验证 depgraph | 循环依赖回退 |
| ❌ | 按数量从大到小治理 | 前面的决定可能让后面的问题消失，白做 |
| ❌ | 用"零消费者"判定删除 | 误删有价值的安全/治理组件 |
| ❌ | 先补测试再重构 | 重构改代码，测试白写 |
| ❌ | **编排器直接依赖下层具体实现(runtime)** | 违反DIP，控制平面耦合数据平面（应改为contract依赖抽象接口） |
| ❌ | **同层循环依赖** | 同层单向允许，但禁止形成环（如 F2→F4→F2） |
