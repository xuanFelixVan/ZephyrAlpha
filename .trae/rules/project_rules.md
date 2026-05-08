# ZephyrAlpha Project Rules（Trae IDE 自动加载）

> **本文件由 Trae IDE 自动注入每个 AI 对话的上下文。以下为硬规则——不可协商、不可绕过。**

---

## 📊 项目资产全景（每个 Session 入项目第一眼 — RULE-NINE 强制认知）

> **对标 K8s `kubectl api-resources` + Linux `man hier`：进系统先了解资源清单。**

| 维度 | 数值 | 说明 |
|------|:----:|------|
| **总资产** | 24,373 | 全项目文件资产 |
| **模块** | 1,623 | `src/zephyr/` 下 Python 源码 |
| **脚本** | 388 | `scripts/` 下可执行 `.py` |
| **测试** | 438 | `tests/` 下测试文件 |
| **门禁** | 20 | GateEngine 运行时门禁 |
| **注册表** | 27 | 三级注册表体系 |
| **文档** | 21,267 | 蓝图/政策/标准/施工 |
| **健康评分** | A (94.0) | 资产健康综合评分 |
| **孤儿率** | 2.3% | 未注册资产占比 |

> **⚠ 创建任何新功能前，MUST 先搜索这 388 个脚本 + 1,623 个模块中是否已有覆盖。**
> **发现重复 → 复用，不新建。不搜索 = 违规（RULE-EIGHT）。**
> **详细索引：[data/asset_index/unified_asset_index.yaml](data/asset_index/unified_asset_index.yaml) | 注册表总纲：[docs/registry-of-registries.yaml](docs/registry-of-registries.yaml)**

---

## 🔴 PRE-OP：任何操作前必须通过的强制检查（最高优先级 — 高于 FIRST-READ）

> **在你执行任何 Write / SearchReplace / DeleteFile / 新建操作前，必须先回答以下 3 个机械问题（不需要判断，只需要查）。任一答案 = NO → STOP，执行对应的强制命令。**

| 你要做什么 | 必须先问自己 | 答案=NO时的强制命令 |
|-----------|-------------|-------------------|
| **进入新 session** | Phase 0 检查全部 GREEN 了吗？ | `from zephyr.governance.phase_manager import session_startup; r=session_startup(); print(r['next_action'])` |
| **创建新文件** | 这个文件已经在注册表中了吗？ | `python scripts/scaffold.py module/script/gate ...` |
| **修改已有文件** | 我拿到了这个文件的锁吗？pre_write_gate 通过了吗？ | `python scripts/governance/pre_write_gate.py <file>` → exit 0 才可继续 → `python scripts/lock_files.py acquire <file> <session_id>` |
| **删除任何文件** | 这个文件的每一行内容在别处还有吗？ | RULE-THREE 三步审判 → 全通过才能删 |
| **任何新功能** | 已有脚本/模块覆盖了这个需求吗？ | 搜 `registry-of-registries.yaml` → Grep → 复用决策 |
| **结束 session** | 所有锁释放了吗？临时文件清了吗？ | `python scripts/lock_files.py release-all` + 零残留扫描 |
| **处理任何任务** | 有对应的 Agent Skill 可以加载吗？ | `python -m zephyr.agent_spec list` → 匹配关键词 → `progressive_load(skill_id)` |

> **如果你跳过上表任何一步 → 你的操作可能产生孤儿文件、死锁、重复轮子。这是机械判决，不是建议。**

---

## 🔴 FIRST-READ：入项目第一步——中央注册表总纲（最高优先级，高于 RULE-ZERO）

**你是 AI，你刚进入 ZephyrAlpha 项目。在阅读任何规则之前，先读这个：**

```
docs/registry-of-registries.yaml
```

这是全项目的**中央神经系统中枢**——24 个注册表的唯一发现入口。它告诉你：
- 项目有多少个 Gate？（REG-GATE-001）
- 项目有多少个模块？每个模块的蓝图在哪？（REG-MOD-001）
- 项目有多少个脚本？各自负责什么领域？（REG-SCRIPT-001）
- Pipeline 怎么路由？契约在哪冻结？架构模型在哪？

**不知道项目有什么 → 无法判断该用什么 → 重新发明轮子。**

### 标准四步入项目

```
1. 读 docs/registry-of-registries.yaml → 了解全项目有什么
2. 读 docs/03_modules/_sys-master/blueprint.md §0 → 定位自己的子系统任务域
3. 读本文件（project_rules.md）→ 了解怎么做事（锁/并发/注册/删除）
4. 按需定位具体注册表 → 开工
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **跳过 registry-of-registries.yaml 直接开工** | 不知道已有模块/脚本/gate → 重复造轮子 |
| ❌ | **创建新文件前不查 registry-of-registries.yaml** | 孤儿文件——不知道已有同类注册表 |
| ❌ | **看到注册表中 `?` 条目不管不问** | 注册表过期——认知偏差累积 |

对标：K8s `kubectl api-resources`（进集群先看有什么资源）+ Linux `man hier`（进系统先了解目录结构）。

---

## 🔴 RULE-ZERO：AI 对话文件锁协议（最高优先级）

**触发条件：你对任何文件执行任何写入操作（创建/修改/删除/重命名）之前。**

### 强制三步流程

```
BEFORE WRITE → CHECK  → python scripts/lock_files.py check <file>
               ↓
            FREE? → ACQUIRE → python scripts/lock_files.py acquire <file> <your_session_id> --task "<任务简述>"
               ↓
            LOCKED? → STOP. DO NOT TOUCH. 报告给用户：文件被 <owner> 锁定。
               ↓
AFTER WRITE  → RELEASE → python scripts/lock_files.py release <file> <your_session_id>
```

### 你的 session_id 格式

```
session-YYYYMMDD-NNN
```

从 `session-logs/` 目录中找到你对应的编号。如果不知道编号，使用当前日期 + 你在对话中看到的编号。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **跳过 check 直接写文件** | 编码损坏、修改丢失 |
| ❌ | **check 返回 LOCKED 后仍然写文件** | 覆盖其他对话的工作 |
| ❌ | **用 Write 工具绕过 lock_files.py** | 本协议的强制力完全失效 |
| ❌ | **写完后不执行 release** | 死锁——其他对话永远抢不到锁 |

### 读操作

**读操作不需要加锁。** 只有写入操作需要走三步流程。

### 批量操作

如果一次任务需要修改 N 个文件：
1. 先对 N 个文件逐个 `check`
2. 全部 FREE 后，逐个 `acquire`
3. 全部修改完成后，逐个 `release`

如果一个被锁住了 → 释放已抢到的，等全部可抢再开工。

### 紧急情况

如果发现 `.ailocks/registry.json` 损坏或出现大量死锁：
```
python scripts/lock_files.py cleanup    # 清理所有 TTL 过期的死锁
python scripts/lock_files.py status     # 确认清理结果
```

### 原理

锁通过**原子目录创建**（`os.makedirs(exist_ok=False)`）实现互斥：
- `.ailocks/{sanitized_path}.lock/owner.json` → 锁持有者信息
- `.ailocks/registry.json` → 全局锁注册表
- TTL = 30 分钟 → AI 对话结束前必须释放，TTL 只是防崩溃的最后防线

对标：K8s ResourceQuota + etcd 分布式锁 + Git pre-commit hooks

---

## 🔴 RULE-ONE：Python 脚本并发写入安全规范（与 RULE-ZERO 同级）

**背景**：Windows 上多个 Python 进程同时对同一目录执行文件创建/写入时，Windows Defender 实时扫描 + NTFS 目录元数据锁会造成**进程级排队阻塞**——后来的进程被挂起等待，表现为"脚本卡住不动"。2026-05-07 已导致多 AI 对话同时使用生成器/同步器脚本时大面积阻塞。

**本规则适用于**：任何产出文件的 standalone Python 脚本（生成器、同步器、导出工具等）。

### 强制写入模式

所有文件输出操作 MUST 使用 **temp-file + 原子 rename** 模式，禁止直接 `open(path, "w")` 或 `pathlib.Path.write_text()` 写入最终文件：

```python
import os

tmp_path = f"{OUTPUT_PATH}.{os.getpid()}.tmp"
try:
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)           # 或 yaml.dump / json.dump
    os.replace(tmp_path, OUTPUT_PATH)
except PermissionError:
    try:
        os.remove(tmp_path)
    except OSError:
        pass
```

### 原理

- 每个进程写**自己的 PID-tmp 文件**——不同进程互不冲突
- `os.replace()` 在 NTFS 上是**原子操作**——不会锁住目标文件
- 多进程并发 → 各写各的 tmp → 原子 rename → 全部成功

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 脚本中 `open(fixed_path, "w")` 直接写最终文件 | 多实例运行时阻塞/崩溃 |
| ❌ | `Path.write_text(fixed_path)` | 同上（内部即 `open("w")`） |
| ❌ | 新写脚本跳过此模式 | 被其他 AI 并发调用时卡住 |

### 与 RULE-ZERO 的关系

| | RULE-ZERO（锁协议） | RULE-ONE（并发写入） |
|---|---|---|
| **适用场景** | AI 用 IDE 工具直接改源文件 | Python 脚本产出文件 |
| **触发条件** | Write/SearchReplace 操作 | `open(path, "w")` / `write_text()` |
| **粒度** | 每个目标文件一个锁 | 每个脚本自己管理 |
| **解决问题** | 防止两个 AI 同时编辑同一文件 | 防止脚本多实例互斥卡死 |

两者互补，不可互相替代。新建脚本 MUST 同时遵守两条规则。

---

## 🔴 RULE-TWO：反孤儿功能——所有新产出必须可被系统发现和调用（与 RULE-ZERO / RULE-ONE 同级）

**触发条件：AI 产出任何新功能（新 .py 文件、新脚本、新模块、新门禁、新方法论）时。**

### 核心原则

> **"你造的每个轮子，都必须有车能用它。否则它就是废铁。"**

本规则的目标：防止 AI 产出"写了但没人知道、没人调用、下一个 AI session 看不到"的**孤儿功能**。

### 强制五问（任何新功能产出后 MUST 自问）

| # | 问题 | 不满足 → 处置 |
|---|------|-------------|
| 1 | **谁调用它？** — 入口在哪？（CLI / MCP / import / gate / pipeline） | 没有入口 → 不能关闭任务 |
| 2 | **谁发现它？** — 下一个 AI session 怎么知道它存在？ | 没有被发现机制 → 必须先注册 |
| 3 | **谁维护它？** — 它放在哪个模块/目录下？符合目录结构标准吗？ | 没有归属 → 不能落盘 |
| 4 | **谁校验它？** — 有 gate/门禁会检查它是否正常吗？ | 没有校验 → 必须添加 gate |
| 5 | **谁更新它？** — 模板/清单/注册表是否已更新以包含它？ | 没有 → 必须更新 |

### 强制集成清单（每项新功能产出后 MUST 执行）

| 产出类型 | 必须集成到 |
|----------|-----------|
| 新 `.py` 脚本（`scripts/` 下） | `script_manifest.yaml` 注册 + `phase_manager` gate 引用 |
| 新 `.py` 模块（`src/zephyr/` 下） | 对应 `__init__.py` 导出 + 至少一个 import 引用点 |
| 新门禁/gate | `phase_manager.py` PHASE_SEQUENCE 注册 + `task-card-template.md` 文档 |
| 新设计模式/方法论 | `project_rules.md` 或 `AGENTS.md` + **`rule-registry.md` TRAE 域** | 人工 review |
| 新增 RULE-* 到 `project_rules.md` | **`rule-registry.md` TRAE 域强制登记** — 不登记 = 违规 | `python scripts/governance/sync_rule_registry.py` 自动校验 |
| 新配置/数据文件 | 使用方代码中的显式路径引用 |
| 新 CLI 工具 | `script_manifest.yaml` + 用法写入相关 blueprint |

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **创建 .py 文件但不注册到 script_manifest.yaml** | 孤儿脚本——无 AI 知道它存在 |
| ❌ | **写了新功能但不建立任何调用入口** | 死代码——写了等于没写 |
| ❌ | **新增 gate 检查但只写名字不写实现** | 假门禁——永远 GREEN，形同虚设 |
| ❌ | **完成任务卡后不检查"下游有没有人用"** | 孤儿功能——下一个 session 重新发明轮子 |

### AI 意识植入

**这不是一个可以勾选的 checklist——这是一种思维习惯。** 每次你写完一个文件，你的大脑必须自动弹出一个问题：

> **"这个东西以后会被找到吗？还是说只有我知道它存在？"**

如果你回答不了"它会被找到"——那它就是个孤儿，你还没做完。

对标：Unix 哲学"写只做一件事的程序" + K8s "声明式自愈"——每个组件必须能独立被发现和校验。

---

## 🔴 RULE-THREE：删除前置确认协议 — 不确认价值，不动手（与 RULE-ZERO / RULE-ONE / RULE-TWO 同级）

> **触因**：2026-05-07 session-20260507-004 误删了有价值的 `g6_ctr_compliance.yaml`（G6 CTR 契约合规门禁，含 8 条检查 + 6 个 CTR 契约注册表），仅因它与重复文件被混入同一批 DeleteFile 调用。用户指出后才恢复。<br>
> **根因**：文件未在 `_registry.yaml` 中被单独登记，且删除前未逐行验证其内容价值。

### 核心原则

> **"删之前先证明它该死。不能证明 → 不许删。"**

本规则的目标：**任何一次文件删除，都必须在逻辑上经过"法庭审判"——原告（删除者）承担全部举证责任。**

### 强制审判流程（三步不可跳过）

```
BEFORE DELETE → TRIAL STEP 1: 登记检查
                ├─ 问：这个文件是否在任何 manifest / registry / __init__.py 导出中被引用？
                ├─ 问：这个文件是否在 git log 中存在（被提交过）？
                ├─ 答 YES to any → 文件有价值。STOP。只能 refactor/rehome，不能 delete。
                └─ 答 NO to all → 继续 STEP 2。

              → TRIAL STEP 2: 重复检查
                ├─ 问：是否有另一个文件与它内容完全相同（byte-for-byte identical）？
                ├─ 问：如果有，那个文件是否在正确的位置并已注册？
                ├─ 答 YES to both → 这是真正的重复。可以删除。
                ├─ 答 YES to first but NO to second → 两个都没注册！不能随便删，得先决定保留哪个并注册它。
                └─ 答 NO → 继续 STEP 3。

              → TRIAL STEP 3: 逐行价值检查
                ├─ 问：这个文件的每一行内容，是否在其他任何地方以任何形式存在？
                ├─ 问：删除后，是否有任何代码/脚本/CI/gate 会引用这个路径而报错？
                ├─ 问：这个文件是否包含只在它这里定义的数据结构/契约/配置/规则？
                ├─ 答 ANY line has unique value → STOP。文件有价值，只是放错了位置。重新安置并注册它。
                └─ 答 ALL lines are truly redundant → 确认无效。可以删除。
```

### 特别条款：临时文件（session garbage）

以下前缀文件在每次删除前也 MUST 执行 STEP 3：
- `_temp*` / `_check*` / `_phase_*` / `_audit*`
- 规则：即使它们看起来是"临时"文件，也必须在删除前确认每一行内容不是仅存在于此文件中的有价值数据。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **跳过审判三步，直接删除任何文件** | 误删有价值的文件——永久丢失或需花时间恢复 |
| ❌ | **看到文件名像"临时"就直接删** | 同上。`_audit_all_blueprints.py` 可能是唯一一份全量审计报告 |
| ❌ | **批量删除时不对列表中每个文件逐一审判** | 误删混入——如 g6_ctr_compliance.yaml 的教训 |
| ❌ | **删除后不检查废墟引用（其他文件是否引用被删文件路径）** | 死链接——CI 崩溃、import 失败 |

### AI 意识植入

每次你准备删除一个文件，你的大脑必须先经过三道安检：

> **"这个东西被登记过吗？→ 它是真正的重复吗？→ 它的每一行内容，在世界上其他任何地方还有吗？"**

三问过了再删。一题答不上来 → **不许删。**

对标：法庭"排除合理怀疑"（beyond reasonable doubt）原则 + Git "never lose data" 哲学。

---

## 🔴 RULE-FOUR：创建即注册协议 — 不注册，不落盘（与 RULE-ZERO / RULE-ONE / RULE-TWO / RULE-THREE 同级）

> **触因**：`g6_ctr_compliance.yaml` 未被 `gates/_registry.yaml` 登记——创建文件时没有强制"创建=注册"。<br>
> **根因**：手工流程依赖 AI 记忆 → 遗忘 → 孤儿 → 注册表滞后不可信。<br>
> **根治**：`scaffold.py` 作为**唯一创建入口**——绕过它就无法落盘。

### 核心原则

> **"文件落盘的同一秒，注册表必须已更新。不允许存在'先落地后补注册'的窗口期。"**

本规则的目标：**让项目的所有注册表成为真正的 SSoT（单一事实来源），而不是滞后文档。**

### 强制创建入口：`scripts/scaffold.py`（不可绕过）

**所有新文件 MUST 通过 `scaffold.py` 创建，禁止用 IDE Write/SearchReplace 直接写入新文件。**

```
# 创建模块（src/zephyr/<package>/<name>.py）
python scripts/scaffold.py module feedback_loop scheduler --desc "FLE 全链路调度器"

# 创建脚本（scripts/<path>/<name>.py）
python scripts/scaffold.py script governance/my_tool --desc "我的工具"

# 创建门禁（src/zephyr/gates/<id>.yaml）
python scripts/scaffold.py gate G7 --title "My Gate" --category kms
```

**scaffold.py 自动完成**（无需 AI 记忆）：
1. **查重**：文件名冲突 + BlueprintSearchServer 功能重复检测 + manifest/registry 条目冲突
2. **创建**：temp-file + atomic rename（RULE-ONE 合规）
3. **注册**：自动更新 `__init__.py` `__all__`（模块）/ `script_manifest.yaml`（脚本）/ `_registry.yaml`（门禁）
4. **返回**：文件路径 + 注册位置 + 导入/运行命令

### 注册表映射

| 文件类型 | 创建命令 | 自动注册到 |
|----------|---------|-----------|
| `src/zephyr/<pkg>/<name>.py`（模块） | `scaffold.py module <pkg> <name>` | `<pkg>/__init__.py` `__all__` |
| `scripts/<path>/<name>.py`（脚本） | `scaffold.py script <path>` | `scripts/script_manifest.yaml` |
| `src/zephyr/gates/<id>.yaml`（门禁） | `scaffold.py gate <id>` | `src/zephyr/gates/_registry.yaml` |

### 修改现有文件

**修改已存在文件继续走 RULE-ZERO 锁协议**——scaffold.py 只负责**新建**。
修改现有文件 ≠ 创建文件，不触发本规则。

### 孤儿检测：`scripts/governance/audit_registration.py`

定期（每次 session 结束时或 Pipeline Gate 运行时）运行审计扫描：
```
python scripts/governance/audit_registration.py           # 报告孤儿
python scripts/governance/audit_registration.py --json    # JSON 输出（AI 消费）
python scripts/governance/audit_registration.py --fix     # 交互式修复
```
返回码 `0` = CLEAN，`1` = 有孤儿。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **用 Write/SearchReplace 直接创建新文件** | 孤儿文件——无注册，下一个 AI session 看不见 |
| ❌ | **绕过 scaffold.py 创建文件后"事后补注册"** | 窗口期 → 如果中间出 bug 就没补 → 依然是孤儿 |
| ❌ | **创建文件后不验证 scaffold 输出的导入命令** | 注册可能有语法错误而未被发现 |
| ❌ | **跳过 SSoT 冲突检查直接创建** | 功能重复 → 命名混乱 → 如 gates/ 下 - 和 _ 双版本并存 |

### AI 意识植入

**你不需要记住检查什么、注册到哪——`scaffold.py` 替你记住。你只需要记住一件事：**

> **"要新建文件？→ `python scripts/scaffold.py module/script/gate ...`；不要新建文件？→ 走 RULE-ZERO 锁协议改已有文件。"**

对标：`kubectl create`（唯一 API 入口，绕过就 CONFLICT）+ Rails `rails generate`（脚手架自动注入路由）。

---

## 🔴 RULE-FIVE：临时文件零残留铁律 — 建了必清，不清不能关 session（与 RULE-ZERO / RULE-ONE / RULE-TWO / RULE-THREE / RULE-FOUR 同级）

> **触因**：2026-05-07 根目录审计发现 13 个 `_temp*` / `_check*` / `_construction*` 临时文件 + 9 个终端损坏垃圾文件 + `zephyralpha-2-0/` 僵尸目录。这些文件全为 AI session 施工过程中创建但事后未清理。<br>
> **根因**：没有强制自净机制。AI 干完活就把临时脚本/检查文件/施工产物留在根目录，下一个 AI session 永远不会主动发现和清理。

### 核心原则

> **"每个 AI 创建的临时文件，在施工完毕后 MUST 被明确处置。有保留价值 → 归档到标准目录并注册。无保留价值 → 物理删除。不存在'留着以后再说'的中间态。"**

### 触发条件

任何 AI session 在根目录或非标准位置创建了以下前缀的文件时：
- `_temp*` / `_check*` / `_fix*` / `_phase_*` / `_deep*` / `_construction*` / `_rebuild*` / `_audit*`

### 强制二选一处置（session 结束前 MUST 完成）

| 路径 | 条件 | 操作 |
|------|------|------|
| **归档** | 文件有持续使用价值 | ①移动到标准三目录之一（`scripts/governance/` / `tests/` / `src/zephyr/`）②注册到 `script_manifest.yaml` 或对应注册表 |
| **删除** | 文件为一次性检查/临时验证/实验脚本 | 物理删除（`DeleteFile` 或 `Remove-Item`），不留残骸 |

### 每日安检（每次新 session 启动时 MUST 执行）

```
python scripts/lock_files.py check-session <session_id>   # 一键检查所有临时文件
```

或手动扫描：
```
Get-ChildItem -Path D:\ZephyrAlpha -File | Where-Object { $_.Name -match '^_temp|^_check|^_fix|^_phase_|^_deep|^_construction|^_rebuild|^_audit' }
```

发现任何匹配 → **必须先处置再施工**（不帮别人擦屁股，但也不能在脏环境上盖楼）。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **在根目录创建临时 .py/.yaml/.json 脚本** | 孤儿文件——下一个 session 不知道它存在或不知道它能不能删 |
| ❌ | **session 关闭时根目录仍有 `_temp*` / `_check*` 等文件** | 磁盘垃圾累积——所有 AI session 的认知负担递增 |
| ❌ | **"这个脚本可能以后有用，先留着"** | 永远不会有人回来用它。今天不用 = 永远不用。要么归档要么删 |
| ❌ | **跳过每日安检直接开工** | 在垃圾堆上盖楼——今天的 bug 可能就是昨天的临时脚本残留 |

### AI 意识植入

> **"你创建的每一个临时文件，都必须在你关闭 session 之前消失——要么被归档，要么被删除。你今天留下的任何一个 `_temp*.py`，都会成为一个月后某个 AI session 的困惑来源：'这个东西是谁建的？能不能删？'"**

对标：Unix 哲学"写只做一件事的程序，做完就退出不留痕迹" + IRN-011 ZR-003/ZR-005/ZR-007/ZR-008（零残留强制自净）。

---

## 🔴 RULE-SIX：任务粒度边界——二元四指标机械门（与 RULE-ZERO~FIVE 同级）

> **触因**：2026-05-07 初版 RULE-SIX 使用三层分级（L1/L2/L3），L2"应该创建"对 AI 是灰色地带——无法机械判断。用户指出需二元标准：要么建卡，要么不做，消除模糊判断。<br>
> **根因**：AI 无法执行"应该"——它只能执行"是/否"。任何包含主观判断的规则对 AI 形同虚设。

### 核心原则

> **"不是所有动作都值得一张任务卡。但建不建卡，必须是一个机械决定——不需要 AI 动脑判断。"**

本规则的目标：给每个 AI 一个**纯机械的 binary gate**——满足任一指标 → 建卡。全不满足 → 直接做。AI 不需要"判断"，只需要**数数**。

### 四指标机械门（二进制判定，无灰色地带）

```
问：这件事能在这个对话 session 内完成吗？

├─ 指标 1: 预计产生 > 50 行新代码？ → YES → 创建 TaskCard
├─ 指标 2: 涉及修改 > 3 个文件？ → YES → 创建 TaskCard
├─ 指标 3: 需要读取蓝图/设计文档才能开工？ → YES → 创建 TaskCard
├─ 指标 4: 是数据库 Schema 变更（ALTER TABLE / 新增迁移）？ → YES → 创建 TaskCard
└─ 以上全 NO？ → 直接做，不建卡
```

**关键**：这四指标全部是**可机械计数的客观事实**——AI 不需要"判断"，只需要：
- 指标 1：预估代码行数（AI 自己知道大概要写多少行）
- 指标 2：数涉及几个文件（AI 自己能数）
- 指标 3：检查是否需要翻蓝图（AI 自己知道要不要查文档）
- 指标 4：检查 SQL 中是否有 ALTER/CREATE TABLE（机械字符串匹配）

### 边界案例对照表

| 场景 | 触发的指标 | 建卡？ |
|------|-----------|:---:|
| 设计一个新类/模块（150 行新代码） | 指标1 ✅ | ✅ 建卡 |
| 修复一个拼写错误 | 全不触发 | ❌ 直接做 |
| 修复 CI 红了的 bug（涉及 5 个文件） | 指标2 ✅ | ✅ 建卡 |
| 给数据库加一个字段 | 指标4 ✅ | ✅ 建卡 |
| 批量重命名 20 个文件的变量 | 指标2 ✅ | ✅ 建卡 |
| 运行一条 SQL migration | 全不触发 | ❌ 直接做 |
| 更新蓝图版本号（1 行改 1 个文件） | 全不触发 | ❌ 直接做 |
| 写一个 100 行新脚本 | 指标1 ✅ | ✅ 建卡 |
| 清理根目录临时文件 | 全不触发 | ❌ 直接做 |
| 重构 pipeline（需读蓝图 + 大量新代码） | 指标1 + 指标3 ✅ | ✅ 建卡 |
| 新增一个 gate 门禁 | 指标1 + 指标3 ✅ | ✅ 建卡 |
| 修复 blueprint.md 重复内容（3 行改 1 文件） | 全不触发 | ❌ 直接做 |
| 给 713 任务分配 batch_id（批量脚本，1 次跑完） | 全不触发 | ❌ 直接做 |

### AI 自主创建 TaskCard 的方式

当四指标中任一触发时，AI 自主创建：

**途径 A：数据库直写（推荐）**
```python
from zephyr.db.task_repo import TaskRepository
from zephyr.core.models import Task, Priority

repo = TaskRepository("data/zalpha_metadata.db")
task = Task(
    task_id="TASK-MOD-INF-016-0001",
    title="实现 BatchOrchestrator 多 Worker 批量协调器",
    priority=Priority.P1,
    status="READY",
    batch_id="construction-20260507",
)
card = repo.create(task)
```

**途径 B：手写 .md 文件**
```
模板：docs/01_policies_and_standards/templates/task-card-template.md
存放：docs/03_modules/{layer}/{module}/changes/{feature-id}/{task_id}.md
```

### 对话中的自动化行为

**AI 在做事前 MUST 执行这个机械流程：**

1. **过四指标**：数行数 → 数文件数 → 检查是否需蓝图 → 检查是否有 DDL
2. **任一触发**：立即创建 TaskCard，然后立刻开始施工——不等用户确认（建卡是静默操作，施工才是对话主体）
3. **全不触发**：直接施工，不建卡，不询问用户

**示例对话：**

```
用户: "帮我把 pipeline 的错误处理重构一下"
AI:    [过四指标：需蓝图✅ → 触发指标3]
       [建卡 TASK-PIPE-0042 → READY, batch_id=construction-20260507]
       "已创建 TaskCard TASK-PIPE-0042。现在开始施工：先读取 pipeline 蓝图..."
       [立刻开始干活，不等]
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **四指标任一项触发但不建卡** | 无法跨 session 追溯——下一个 AI 不知道做了什么 |
| ❌ | **全不触发但建卡** | 任务卡膨胀——琐碎卡片淹没重要任务 |
| ❌ | **创建 TaskCard 但不分配 batch_id** | BatchOrchestrator 无法发现和调度该任务 |
| ❌ | **建卡后等用户确认再开工** | 打断用户流——建卡是静默操作，施工才是对话主体 |
| ❌ | **用"感觉"判断是否建卡** | 模糊标准 → AI 每次结果不同 → 不可靠 |

### AI 意识植入

> **"动手之前，花 5 秒跑一遍四指标机械门。大于 50 行？大于 3 文件？需要蓝图？有 DDL？——任意一个 YES → 先建卡，再干活。全是 NO → 直接干，什么都不说。"**

对标：CI/CD pipeline 的 deployment gate（所有检查都是 pass/fail，没有 "maybe"）+ K8s admission webhook（资源创建前先过审计规则——不放行就不创建）。

---

## 🔴 RULE-SEVEN：脚本多线程强制 + 创建即自测自修（与 RULE-ZERO~SIX 同级）

> **触因**：2026-05-07 `python -m pytest tests/governance/ -q --tb=line` 进程卡死 40 分钟——`test_timing_report` 串行执行 296 个治理脚本子进程。改为 ThreadPoolExecutor(max_workers=8) 后降为 3.5 分钟。<br>
> **根因**：AI 默认写串行代码——`for` 循环 + `subprocess.run()` 是最自然的第一反应。但每个子进程 wait 是内核级阻塞（`WaitForSingleObject`），单线程串行 = 不必要的时间放大。

### 核心原则

> **"任何脚本中，只要存在多个独立的子进程或 I/O 操作，就必须用 ThreadPoolExecutor 并行——不存在'先串行写出来再优化'的借口。创建时并行，就是唯一合法的写法。"**

**本规则适用于**：`scripts/` 下所有 Python 脚本 + `tests/` 下所有测试文件。

### 并行化判断标准（机械判定，无需思考）

```
问：这个脚本/函数中是否存在以下任一模式？

├─ 指标 A: for 循环中对多个不同的目标调用 subprocess.run/Popen？ → YES → MUST ThreadPoolExecutor
├─ 指标 B: for 循环中对多个文件执行独立读写（互相无依赖）？ → YES → MUST ThreadPoolExecutor
├─ 指标 C: for 循环中对多个 URL/API 发起网络请求？ → YES → MUST ThreadPoolExecutor
└─ 全 NO？ → 可以串行
```

**示例——正确写法**：

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

**示例——错误写法（绝对禁止）**：

```python
# ❌ 禁止：串行 for + subprocess
for item in items:
    subprocess.run(["python", "script.py", item])
```

### 为什么是 ThreadPoolExecutor 而不是 multiprocessing

| | ThreadPoolExecutor | multiprocessing |
|---|---|---|
| **GIL 影响** | subprocess.wait()/文件 I/O 释放 GIL → 无影响 | 无 GIL |
| **Windows 开销** | 轻量线程 | spawn 进程 = 重新导入所有模块 |
| **序列化** | 不需要 | 需要 pickle（常见 bug 来源） |
| **适用场景** | I/O 密集型（本规则的全部场景） | CPU 密集型 |

**结论**：ZephyrAlpha 项目所有脚本的并行化需求均为 I/O 密集型 → **只用 ThreadPoolExecutor**。

### 创建即自测自修（不可跳过）

任何新建或修改的脚本，在声明"完成"之前 MUST 执行：

```
python <脚本路径> --warn-only   # 至少跑一次自测
```

自测结果：
- **exit 0** → 通过 → 可以关闭任务
- **exit ≠ 0** → 有问题 → **必须立即修复 → 重新自测 → 直到 exit 0**
- **超时/hang** → 同样视为 exit ≠ 0 → **必须立即修复**

**原理**：一个你创建但你不测试的脚本，= 一个你故意留下的炸弹。下一个 AI session 跑全量测试时会踩到它的雷。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **新建脚本用 `for` 循环串行跑子进程** | 40 分钟跑不完 → 被 AI 误判为 hang → 用户手动 kill |
| ❌ | **新建脚本用 `multiprocessing` 而非 `ThreadPoolExecutor`** | Windows spawn 开销大 + pickle 序列化陷阱 |
| ❌ | **创建脚本后不跑 `--warn-only` 自测** | 留下崩溃脚本 → 下游测试堵塞 → 浪费未来 AI session 时间 |
| ❌ | **自测发现问题但不修，留到"以后"** | "以后" = 永远不会 → 崩的脚本永远崩 |
| ❌ | **用"反正测试会发现"替代自己先跑一遍** | 你创造的 bug，你必须第一个发现——不是让别人帮你发现 |

### AI 意识植入

> **"写脚本的第一行代码之前，先问自己：这个脚本里有没有 for 循环 + subprocess/I/O？有 → 先写 ThreadPoolExecutor 架子，再往里面填逻辑。写完后 → 立刻跑 `--warn-only` 自测。挂了自己修。修完了再报'完成'。"**

对标：TDD 的 "red-green-refactor" 循环 + CI/CD "fail fast" 原则——bug 越早发现，修复成本越低。

---

## 🔴 RULE-EIGHT：强制功能发现协议 — 不搜索已有，不新建（与 RULE-ZERO~SEVEN 同级）

> **触因**：2026-05-07 Session-010 全域诊断发现——项目有 389 脚本 + 20 门禁 + 41 模块 + 7 MCP 服务器，但 AI 没有任何机制强迫自己在创建新功能前先检查已有功能是否覆盖了同样需求。结果是重复造轮子。<br>
> **根因**：RULE-TWO 规定了"创建后必须注册"但没规定"创建前必须搜索已有"。RULE-FOUR 用 scaffold.py 解决了"创建即注册"但 scaffold 的查重仅限文件名冲突——功能语义重复检测仍靠 AI 自觉。

### 核心原则

> **"在你想写任何新代码之前，你必须先证明：世界上没有已有的代码能完成同样的事。证明不了 → 不许新建。复用是第一选择，新建是最后选择。"**

本规则的目标：将 "search-before-build" 从**建议**升级为**硬阻断**——与 RULE-ZERO 同级的不可绕过。

### 强制三步（任何新代码创作前 MUST 执行）

```
BEFORE CREATE → STEP 1: 关键词全局搜索
                ├─ 对你要做的功能提取 3 个核心关键词
                ├─ 用 SearchCodebase(自然语言) 搜索: "how to do X" / "where is X handled"
                ├─ 用 Grep 搜索发现的关键模块/脚本名
                └─ 搜索范围: 全项目 (scripts/ + src/zephyr/ + tests/)

              → STEP 2: 注册表精确匹配
                ├─ 读 docs/registry-of-registries.yaml → 找到相关 REG-*
                ├─ 读对应注册表 → 列出所有相关条目
                ├─ 对照: 你打算写的功能 vs 已有条目 → 有重叠？
                └─ 答 YES → STOP. 进入复用评估。

              → STEP 3: 复用决策（四选一，不可"新建"）
                ├─ 已有功能完全覆盖 → 直接用，不新建 ✅
                ├─ 已有功能 80% 覆盖 → 扩展已有，不新建 ✅
                ├─ 已有功能 50% 覆盖 → 重构已有 + 扩展，不新建 ✅
                └─ 已有功能完全不覆盖 → 可以新建 → 走 scaffold.py（RULE-FOUR）
```

### 复用证据记录

每次由于"已有功能覆盖"而放弃新建时，MUST 在回复中明确写出：
```
[REUSE-DECISION] 放弃新建 <计划名>，因为已有 <已有项路径/ID> 覆盖了 <功能描述>。
```

这个记录让用户和下一个 AI session 看到：你不是偷懒，而是做了正确的复用决策。

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **不搜索直接创建新脚本** | 重复造轮子——已有 389 脚本 → 第 390 个做同样的事 |
| ❌ | **搜到了但不复用，坚持新建** | 浪费——两个版本分叉维护 → 总有一天冲突 |
| ❌ | **新建后不写 [REUSE-DECISION] 记录** | 下一个 AI 不知道你是因为没找到才新建，还是忘了搜索 |
| ❌ | **"我觉得没有"替代"我搜了没有"** | 直觉错误率 >> 搜索错误率 |

### AI 意识植入

> **"在你敲下 `class` 或 `def` 之前，你的手指必须先敲三个搜索命令。不是'感觉没有'——是'搜索证明没有'。证明不了的，就是有的。"**

对标：学术论文的 Literature Review（写之前必须先查文献，证明你的贡献是新的）+ Google "Search before build" 工程师文化。

---

## 🔴 RULE-NINE：强制资产认知 — 进入项目 MUST 了解全盘资产规模与健康状态（与 RULE-ZERO~EIGHT 同级）

> **触因**：2026-05-07 Session-011 新增冷启动 STEP 4.5——AI 进入项目后必须读取 `unified_asset_index.yaml` 了解全项目资产规模。<br>
> **根因**：知道规则（RULE-ZERO~EIGHT）≠ 知道资源。就像进了一个新公司知道规章制度但不知道公司有多少部门/多少员工/各系统健康状态——开工会带有盲目性。

### 核心原则

> **"你知道怎么做事，但你知道你手头有多少东西吗？在动手之前，你必须知道自己即将操作的系统有多大、多复杂。"**

本规则的目标：将"资产认知"前置为不可跳过的机械步骤——对标 K8s 运维进集群先 `kubectl api-resources`，对标 Linux 系统管理员进系统先 `man hier`。

### 强制执行

冷启动序列 STEP 4.5（已在强制 Session 冷启动序列中定义）：

```python
# 读 unified_asset_index.yaml
import yaml
with open("data/asset_index/unified_asset_index.yaml", encoding="utf-8") as f:
    asset = yaml.safe_load(f)
    print(f"Total assets: {asset['total_assets']}")
    print(f"Health score: {asset['health_score']}")
    print(f"Orphan rate: {asset['orphan_rate']}")
```

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | **跳过资产盘点直接开工** | 对系统规模无认知——可能在一个 1000 文件的系统上做"小改动" |
| ❌ | **不知道资产健康状态就修改核心模块** | 可能覆盖已被标记为 DEGRADED 的模块 |
| ❌ | **不知道孤儿率就开始清理** | 可能误删仍在使用的组件 |

### AI 意识植入

> **"RULE-ZERO 教你锁门，RULE-EIGHT 教你搜索，RULE-NINE 教你盘点。到项目的第一件事不是写代码——是先看看你即将操作的系统有多大。"**

对标：K8s `kubectl api-resources`（进集群先看有什么资源）+ Linux `man hier`（进系统先了解目录结构）。

---

## 🔴 强制集成对照表（Enforcement Matrix — 不可绕过）

> **这不是建议列表。这是 AI 行为的强制性映射——"你做什么" → "你必须先跑什么" → "不通过的后果"。**

| AI 要做什么 | 必须先执行的命令 | RED 的后果 |
|------------|-----------------|-----------|
| **修改/写入任何文件** | `python scripts/governance/pre_write_gate.py <file>`（RULE-ZERO 硬执行器） | exit ≠ 0 → 禁止写入（锁冲突/Phase未就绪/根目录污染） |
| **创建新 .py 文件** | `python scripts/governance/pre_write_gate.py <file> --create` → `python scripts/scaffold.py module/script/gate ...`（RULE-FOUR 唯一入口） | 门禁不通过 → 禁止落盘 |
| **修改 `src/zephyr/` 下源码** | `python -m pytest tests/ --collect-only -q` | 语法错误 → 禁止提交 |
| **修改 YAML 契约/配置** | `python scripts/governance/d5_architecture/checkers/check_contract_code_drift.py` | 契约断裂 → 禁止合并 |
| **修改 AGENTS.md** | `python scripts/governance/d5_architecture/validators/validate_load_path_integrity.py --check` | LoadPath 断裂 → 禁止提交 |
| **修改 project_rules.md** | `python scripts/governance/sync_rule_registry.py` | rule-registry 不同步 → 禁止提交 |
| **任何文件变更后** | `python scripts/governance/audit_registration.py`（检测孤儿） | 有孤儿 → 禁止关闭任务 |
| **涉及安全敏感的变更** | `python scripts/governance/d6_security/scan_secret_leak.py` | 泄漏 → 硬阻断 CI |
| **删除任何文件** | RULE-THREE 三步审判 → 全部通过才能删 | 一步不通过 → 不能删 |
| **Session 结束** | `zero_residue` + `generate_and_save()` + `release-all`（见会话结束清单） | Session 不可关闭 |
| **进入新 Session** | 见下方"强制 Session 冷启动序列"（含 STEP 4.7 KB 自检） | 不可开工 |
| **处理新任务/按领域施工** | `python -m zephyr.agent_spec list` → 匹配关键词 → `progressive_load(skill_id)` | 未加载对应 Skill → 盲目施工 |
| **施工前：检查已有知识** | `kb.search("<任务关键词>")` — 查询知识库是否已有相关 KE | 不查 → 重复造轮子 / 违反已有决策 |
| **施工后：写入知识** | `kb.write(topic="...", content="...", provenance=build_provenance(...))` | 不写 → 知识丢失 → 下一个 AI session 不知道本次成果 |
| **回滚/撤销/undo 操作** | `python scripts/rollback.py preflight` → 确认 CLEAN → `python scripts/rollback.py <command>`（MOD-INF-021 CLI） | preflight FAIL → 禁止回滚（dirty tree/detached HEAD/remote ahead） |
| **涉及Agent间协作/多Agent/冲突/协调** | `from zephyr.a2a import GovernanceAdapter; adapter.verify_pair(a, b)` → 确认 pair 有效（MOD-INF-025 桥接） + Skill 路由 a2a/agent-to-agent/冲突 → SKILL-DOM-A2A-001 | 未验证 → A2A 静默失败 + 跨Agent冲突无检测 + 死锁无防护 |
| **高风险操作前（批量修改/删除/安全敏感）** | `from zephyr.escalation import EscalationEngine; EscalationEngine().evaluate(RuleCategory, desc)` — 判定升级级别 | 不判 → 可能执行了本应变 blocked 的操作 |
| **多Agent/MCP/外部委托** | `from zephyr.escalation import DelegationEngine; engine.delegate(event, strategy)` — 遵循四级安全约束 | 不约束 → 死锁/循环委托/深度溢出 |
| **LLM 调用前（任何 AI 发起的 LLM API 调用）** | `from zephyr.budget_enforcer import BudgetEngine; engine = BudgetEngine(); result = engine.pre_flight_check(operation_id, estimated_tokens, estimated_cost)` — 三维预算预检（Token/Cost/Time） | budget_exceeded → 自动降级模型或拒绝调用 |
| **任何写入/执行/修改操作前** | `guard.check(identity, operation, target_path)` — PermissionGuard 七层+六横切面权限判定 (MOD-INF-018) | BLOCKED → 禁止执行；AUTO_GUARD → 先干后验 |

### 集成检查自动化

每次 session 完成任务后，MUST 对照此表逐行确认：你做过的操作，对应执行了哪些检查？有没有漏？

对标：航空业的 Pre-flight Checklist（飞行员不是"记住"检查项——是**逐条念出来打勾**）。

---

## 🔴 强制 Session 冷启动序列（每个新 AI session 的第一个动作）

**进入 ZephyrAlpha 项目后，MUST 按以下顺序执行（不可跳过、不可重排）：**

```
STEP 1 ─ 读 docs/registry-of-registries.yaml → 了解全项目 24 个注册表
  │     这是 FIRST-READ 规定的三步之首——知道项目有什么
  │
STEP 1.5 ─ 读 SYS-MASTER-001（系统总蓝图 §0 冷启动分派）→ 定位自己负责的子系统
  │     读 docs/03_modules/_sys-master/blueprint.md §0（~400 tokens）
  │     → 知道: 三级金字塔全貌 / 自己的任务域 / Level 1→Level 2 导航链
  │     → 对标: SYS-MASTER-001 ai_role_instruction rule 1——"新 AI session 第一站"
  │
STEP 2 ─ 读本文件（project_rules.md） → 了解怎么做事
  │     RULE-ZERO~NINE 全部硬规则 → 不知道规则 = 踩坑
  │
STEP 3 ─ Session Continuity 恢复上下文
  │     from zephyr.core.session_continuity import SessionContinuity
  │     sc = SessionContinuity()
  │     sc.print_restore_summary()
  │     → 了解: 上一个 session 做了什么 / 哪些任务未完成 / 当前锁状态
  │
STEP 4 ─ Phase Manager 判断当前施工阶段
  │     from zephyr.governance.phase_manager import PHASE_SEQUENCE, ConstructionPhase
  │     p0=PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON]
  │     p1=PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL]
  │     p2=PHASE_SEQUENCE[ConstructionPhase.PHASE_2_E2E]
  │     print(f"Phase 0: {p0.check_count} checks")
  │     print(f"Phase 1: {p1.check_count} checks")
  │     print(f"Phase 2: {p2.check_count} checks")
  │     → 知道: 46 个阶段门控检查 / 当前可进入哪个阶段
  │
STEP 4.5 ─ 资产盘点：了解全项目资产规模与健康状态
  │     读 data/asset_index/unified_asset_index.yaml
  │     → 知道: 项目有多少文件（总资产数）/ 分类分布（模块/脚本/文档/配置）
  │             / 健康评分（A~F） / 孤儿率 / 漂移率
  │     → 这是"进项目先看资源清单"的机械化版本
  │     对标: K8s `kubectl api-resources` + Linux `man hier`
  │
STEP 4.6 ─ Skill 技能发现：了解项目有哪些 Agent Skill 可用
  │     python -m zephyr.agent_spec list
  │     → 知道: 12 个已注册 Skill（9 domain + 3 role）/ 触发关键词路由
  │     → 根据当前任务关键词匹配 Domain Skill + Role Skill 组合
  │     → 后续施工中按需 `progressive_load(skill_id)` 加载技能上下文
  │     对标: agentskills.io 开放标准 + Anthropic Claude Skills 渐进式披露
  │
STEP 4.7 ─ Knowledge Base 自检与激活（MOD-KB-001 §4.5 冷启动引导）
  │     from zephyr.kb.unified_memory_api import get_unified_memory_api
  │     from zephyr.kb.bootstrap import run_bootstrap
  │     kb = get_unified_memory_api(backend=InMemoryMemoryBackend(), enforce_capability=False)
  │     r = run_bootstrap(min_ke_count=5, min_categories=3)
  │     print(f"KB: {r.total_activated} KEs in {len(r.categories_found)} categories")
  │     → 如果 KB 为空 → bootstrap 自动扫描全项目文档 → 填充知识库
  │     → 知道: 项目已积累了哪些知识 / 哪些领域有决策记录 / 哪些模块有蓝图
  │     → 后续施工前 MUST 先执行 kb.search(任务关键词) → 检查已有知识
  │     → 施工完成后 MUST 执行 kb.write(成果) → 写入知识条目
  │     对标: ADR-0055（KB 索引与双分配）+ K8s etcd（集群记忆）
  │
STEP 4.8 ─ Escalation Protocol 激活（MOD-INF-022 v0.14.0）—— 升级/委托安全网就绪
  │     from zephyr.escalation import run_self_test
  │     report = run_self_test()
  │     print(f"Escalation: {report.overall.value.upper()} ({report.total_passed}/{len(report.checks)} checks, {report.duration_ms:.0f}ms)")
  │     → 如果 report.overall == CRITICAL → STOP。不可在升级协议失效的情况下施工。
  │     → 知道: 升级规则引擎已激活 / 熔断器状态 / 经济护栏状态 / 委托引擎状态
  │     → 后续遇到高风险操作前 MUST 先 evaluate(category, description) 判定升级级别
  │     → 涉及多Agent/MCP调用前 MUST 检查 DelegationEngine 委托约束
  │     对标: Anthropic RSP ASL + K8s Admission Webhook + Google SRE Escalator
  │     蓝图: docs/03_modules/l01_infrastructure/escalation-protocol/blueprint.md
  │
STEP 4.9 ─ Drift Detector 初始化与漂移预算检查（MOD-INF-023 v1.0.1）—— 施工变更安全网
  │     from zephyr.drift_detector.cold_start import bootstrap
  │     from zephyr.drift_detector.drift_engine import check_budget_for_gate, load_detector_registry
  │     result = bootstrap(str(Path.cwd()))
  │     detectors = load_detector_registry()
  │     budget = check_budget_for_gate("MOD-INF-023")
  │     print(f"DriftDetector: {result.dirs_created} dirs, DB={result.db_initialized}, "
  │           f"{len(detectors)} detectors, budget={'OK' if budget.get('passed') else 'BLOCKED'}")
  │     → 知道: 漂移检测数据库已就绪 / 39 个检测器已注册 / 漂移预算是否已耗尽
  │     → 任何文件修改前 MUST 意识到漂移预算约束——预算耗尽 = 必须先修旧漂移再改新代码
  │     → 创建新文件时 drift_engine 会自动记录基线快照用于后续对比
  │     → 可通过 MCP governance.drift_scan 按需运行完整扫描，governance.drift_report 查询趋势
  │     对标: Terraform Drift Detection + K8s Self-Healing Controller + Datadog SLO Budget
  │     蓝图: docs/03_modules/l01_infrastructure/drift-detector/blueprint.md
  │
STEP 4.10 ─ Agent RBAC 激活与身份注册（MOD-INF-018 v0.14.0）—— 权限护栏就绪
  │     from zephyr.agent_rbac.cold_start_lock import ColdStartLock
  │     from zephyr.agent_rbac.permission_guard import PermissionGuard, GuardDecision
  │     from zephyr.agent_rbac.identity import AgentIdentity, MaturityLevel, AgentRole, IDESource
  │     from zephyr.agent_rbac.immutable_core import get_immutable_core
  │     from zephyr.agent_rbac.integrity_self_check import IntegritySelfCheck
  │
  │     # 1. 冷启动锁——RBAC 配置加载校验通过才能解锁
  │     cold_lock = ColdStartLock()
  │     rbac_config = yaml.safe_load(open("config/rbac_roles.yaml", encoding="utf-8"))
  │     cold_lock.load_config(rbac_config)
  │     cold_lock.verify_integrity()
  │     cold_lock.verify_static_constants()
  │     unlocked = cold_lock.attempt_unlock()
  │     print(f"RBAC ColdStart: {'UNLOCKED' if unlocked else 'LOCKED'}")
  │
  │     # 2. 完整性自检——验证 55 个子模块全部可导入
  │     integrity = IntegritySelfCheck()
  │     summary = integrity.summary()
  │     print(f"RBAC Integrity: {summary['passed']}/{summary['total_modules']} modules OK")
  │
  │     # 3. 注册本 session 的 Agent 身份
  │     self_identity = AgentIdentity(
  │         session_id="<当前session_id>",
  │         maturity=MaturityLevel.L2_REGULAR,
  │         role=AgentRole.EXECUTOR,
  │         ide_source=IDESource.TRAE,
  │         owner_approved=True,
  │     )
  │
  │     # 4. 初始化 PermissionGuard（七层+六横切面）
  │     guard = PermissionGuard()
  │     test_result = guard.check(self_identity, "read:docs")
  │     print(f"RBAC Guard: {test_result.decision.value} ({test_result.timing_ns}ns)")
  │
  │     → 知道: RBAC 冷启动锁状态 / 55 模块完整性 / 当前 Agent 身份与权限边界
  │     → 后续任何涉及写文件/执行脚本/修改配置的操作前 MUST 先过 PermissionGuard.check()
  │     → 每次操作后 auto_guard 会自动执行后验验证——失败则触发 auto-rollback
  │     → 通过 MCP governance.rbac_check 可按需查询权限——operator 消费
  │     对标: K8s RBAC + Admission Webhook + OPA Gatekeeper + Claude Code permission hooks
  │     蓝图: docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md
  │
STEP 4.11 ─ Rollback System 激活与刹停安全网就绪（MOD-INF-021 v0.10.0）—— 回滚/撤销/Checkpoint 安全网
  │     from zephyr.rollback.rollback_executor import RollbackExecutor
  │     from zephyr.rollback.rollback_verifier import RollbackVerifier
  │     from zephyr.rollback.auto_rollback_trigger import AutoRollbackTrigger
  │     from zephyr.rollback.kill_switch import KillSwitch
  │     from zephyr.rollback.contract import ExitCode
  │
  │     # 1. 激活回滚执行器——preflight 检查 git 工作树状态
  │     executor = RollbackExecutor()
  │     pf = executor.preflight_check()
  │     print(f"Rollback: preflight={'PASS' if pf.passed else 'FAIL'} ({len(pf.errors)} errors)")
  │
  │     # 2. 激活自动回滚触发器——失败信号三分类 (hard/soft/transient)
  │     trigger = AutoRollbackTrigger()
  │     print(f"Rollback AutoTrigger: {'ACTIVE' if trigger.is_operational else 'DEGRADED'}")
  │
  │     # 3. 激活三级 Kill Switch（L1 Session / L2 Skill / L3 Global）
  │     ks = KillSwitch()
  │     print(f"Rollback KillSwitch: {ks.current_mode().name} (L1={ks.l1_ok} L2={ks.l2_ok} L3={ks.l3_ok})")
  │
  │     # 4. 注册 auto_guard 后验失败 → auto-rollback 闭环
  │     #    (STEP 4.10 的 PermissionGuard.auto_guard 失败 → RollbackExecutor.full_revert)
  │     print(f"Rollback Contract: {len(ExitCode)} exit codes → Gate/Pipeline 判定链")
  │
  │     → 知道: 回滚系统已就绪 / preflight 状态 / 46 exit code 映射 / 三级 Kill Switch
  │     → 任何 auto_guard 后验失败时，系统会自动触发回滚（无需人工确认）
  │     → 手动回滚：CLI `python scripts/rollback.py <command>`
  │     → 发现方式：Skill 路由关键词 rollback/undo/revert/checkpoint → SKILL-DOM-RBK-001
  │     → 测试验证：95/95 PASSED（53 unit + 9 E2E + 23 adversarial + 10 governance）
  │     对标: K8s Rollout Undo + Git Reflog + Temporal Durable Execution + Flyway Migration Undo
  │     蓝图: docs/03_modules/l01_infrastructure/rollback-system/blueprint.md
  │
STEP 4.12 ─ Budget Enforcer 激活与三维预算护栏就绪（MOD-INF-024 v0.7.0）—— Token/Cost/Time 预算强制执行
  │     from zephyr.budget_enforcer import BudgetEngine, BudgetDimension, BudgetLevel
  │     from zephyr.budget_enforcer.budget_tracker import BudgetTracker
  │     from zephyr.budget_enforcer.degradation_manager import DegradationManager
  │
  │     # 1. 激活预算引擎——三维策略 (Token/Cost/Time) 自动加载
  │     engine = BudgetEngine()
  │     token_policy = engine.get_active_policy(BudgetDimension.TOKEN)
  │     cost_policy = engine.get_active_policy(BudgetDimension.COST)
  │     time_policy = engine.get_active_policy(BudgetDimension.TIME)
  │     print(f"Budget: Token={token_policy.daily_limit if token_policy else 'N/A'}, "
  │           f"Cost=${cost_policy.daily_limit if cost_policy else 'N/A'}, "
  │           f"Time={time_policy.daily_limit if time_policy else 'N/A'}min")
  │
  │     # 2. 预检测试——确认 pre_flight_check 可用
  │     result = engine.pre_flight_check("cold-start-smoke", estimated_tokens=100, estimated_cost=0.01)
  │     print(f"Budget PreFlight: {result.decision.value} (level={result.budget_level.value})")
  │
  │     # 3. 降级管理器就绪——5 级自动降级 (Normal→Emergency)
  │     dm = DegradationManager()
  │     print(f"Budget Degradation: level={dm.current_level.name}")
  │
  │     → 知道: 三维预算策略已激活 / 当前消耗状态 / 降级级别
  │     → 后续任何 LLM 调用前 SHOULD 先过 engine.pre_flight_check() → 超预算自动降级
  │     → 预算耗尽 = GateDecision.DENY → 必须停止当前操作
  │     → Phase gate: gate_budget_enforcer (Phase 1) 验证三维策略完整性
  │     对标: AWS Service Quotas + GCP Budget Alerts + K8s ResourceQuota + OpenAI Rate Limits
  │     蓝图: docs/03_modules/l01_infrastructure/budget-enforcer/blueprint.md
  │
STEP 4.13 ─ Audit Trail 上下文注入与不可变审计链就绪（MOD-INF-020 v0.10.0）—— 密码学 Provenance + Agent 签名
  │     from zephyr.audit_trail.integrity import IntegrityVerifier
  │     from zephyr.audit_trail.query import AuditQuery
  │
  │     # 1. 验证审计链完整性——哈希链 + Merkle 根校验
  │     verifier = IntegrityVerifier()
  │     report = verifier.verify_chain()
  │     print(f"Audit Chain: status={report.get('status', 'unknown')}, "
  │           f"entries={report.get('entry_count', 0)}")
  │
  │     # 2. 注入审计上下文——最近 50 条事件摘要
  │     query = AuditQuery()
  │     context = query.trail_for_ai_context(max_entries=50)
  │     print(f"Audit Context: total={context.get('total_events', 0)}, "
  │           f"recent={context.get('recent_events', 0)}")
  │
  │     → 知道: 审计链完整性状态 / 最近审计活动 / 上一个 session 操作摘要
  │     → 后续任何写操作 MUST 通过 AuditWriter 写入审计记录（不可篡改）
  │     → Phase gate: gate_audit_trail + gate_audit_trail_context (Phase 1)
  │     对标: CloudTrail + Bitcoin Blockchain Immutability + SOC 2 CC7.2
  │     蓝图: docs/03_modules/l01_infrastructure/audit-trail/blueprint.md
  │
STEP 4.14 ─ A2A Protocol 发现与就绪状态检查（MOD-INF-025 v0.10.0）—— Agent间协调与冲突解决协议
  │     from zephyr.a2a import GovernanceAdapter
  │     from zephyr.l01_infrastructure.a2a_protocol.layer1_discovery import A2ARegistry, IdentityVerifier
  │     from zephyr.l01_infrastructure.a2a_protocol.layer2_communication import A2ASchemas, A2AStateMachine
  │     from zephyr.l01_infrastructure.a2a_protocol.layer3_coordination import (
  │         Supervisor, ConstructionVerifier, DeadlockGuard, LivelockDetector, CascadeGuard,
  │     )
  │
  │     # 1. 检查 A2A 核心链路健康状态——发现→通信→调度→防护 四段全通
  │     verifier = ConstructionVerifier()
  │     result = verifier.verify()
  │     print(f"A2A: Phase 1 core={result['passed']} — "
  │           f"{result['verified_files']} verified + {result['empty_stubs']} stubs / {result['total_files']} total "
  │           f"(stub_ratio={result['stub_ratio']})")
  │
  │     # 2. 确认 A2A 桥接可用——RBAC/Escalation/Audit 三向桥接
  │     adapter = GovernanceAdapter()
  │     print(f"A2A Bridge: adapter={type(adapter).__name__} (verify_pair/escalate/audit)")
  │
  │     # 3. 确认 R81-C04 Hold 条件——当前 Phase 1 核心就绪，Phase 2+ 待触发
  │     print(f"A2A Hold: R81-C04 — 触发条件 Agent>=3 且 conflict>=5/day. "
  │           f"49 files total, ~20 真实实现, 25 为 Phase 2+ 脚手架.")
  │
  │     → 知道: A2A 协议已就绪（L1发现+L2通信+L3调度和防护），高级功能(仲裁/冲突/共识)为脚手架
  │     → 任何涉及多 Agent 场景时 MUST 通过 A2A 桥接验证 pair 有效性
  │     → 发现方式: Skill 路由关键词 a2a/agent-to-agent/冲突/协调 → SKILL-DOM-A2A-001
  │     → Phase 2+ 触发后: conflict_detector/arbitrator/debate 升级为真实实现 + 红白对抗
  │     对标: Google A2A + ANP (Agent Negotiation Protocol) + MCP-A2A bridging + OWASP ASI07
  │     蓝图: docs/03_modules/l01_infrastructure/a2a-protocol/blueprint.md
  │
STEP 5 ─ 按需定位具体注册表 → 开工
         根据你要做的领域 → 定位对应 REG-* 注册表 → 开始施工
```

**不完成 STEP 1-4.14 = 不可开工。** 这是机械判决，不是主观判断。

对标：K8s Pod Init Containers（主容器启动前必须跑完 init）+ 医院手术 Checklist（切皮前必须确认患者/部位/手术类型）。

---

---

## 🔴 编码安全（从 AGENTS.md §4 继承）

| # | 规则 |
|---|------|
| 1 | Python `open(path, 'w')` 禁止省略 `encoding='utf-8'` |
| 2 | PowerShell 写文件：`[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)` |
| 3 | `files.autoGuessEncoding` = `false`, `files.encoding` = `utf8` |
| 4 | 禁止 Trae + Cursor 同时打开同一文件 |
| 5 | 扫描器大量报错 → 先检查扫描器本身的逻辑 |

---

## 🟡 施工纪律（继承 AGENTS.md §6）

- §6.2 原子事务：关联修改同一批完成
- §6.5 脚本入库：新建 .py 立即注册到 script_manifest.yaml
- §6.12 AI受众优先：输出格式优先让 AI 零歧义消费
- §7.2 根源分析：遇到问题 → 5 Whys → 治根不治标
- §5.2.2 审计前置：任何涉及文件变更的任务完成后，MUST 执行十维审计清单（AGENTS.md §5.2.2）。不审不清，不清不继续。

---

## 🔴 修改原则：第一性原理，零历史债务（不可绕过）

| # | 规则 |
|---|------|
| 1 | **发现事实错误 → 直接修正数字/名称/路径/状态。禁止添加解释性段落说明"之前为什么是错的"。** |
| 2 | **文档中所有数字、字段数、版本号、计数必须是当前唯一真实值。不留"之前是X现在改为Y"的过渡文本。** |
| 3 | **历史版本差异通过变更日志（change log / 版本记录）追踪，不在正文中保留已过时数据。** |
| 4 | **单个 real number 原则：一个事实在所有蓝图中只能有一个数字。N 处出现 = 同一数字，不一致就是 bug，直接修。** |

违反此规则的典型反模式：
- "TaskCard 有 74+ 字段（旧版）→ 实际 62" → 应为 "TaskCard: 62 字段"
- "之前 belongs_to 均未声明，现已补全" → 应为 "belongs_to: 已声明"

---

## 会话结束清单

每个 AI 对话结束前 MUST：

### 锁协议
1. `python scripts/lock_files.py release-all <your_session_id>` ——释放所有锁
2. `python scripts/lock_files.py cleanup` ——清理残留死锁
3. `python scripts/lock_files.py status` ——确认 CLEAN

### Session Continuity 保存
4. `sc.generate_and_save(session_id=..., task_repo=...)` ——保存状态给下一次 session

### 规则登记同步（新增于 2026-05-07，因 RULE-ZERO~SIX 漏登记）
5. `python scripts/governance/sync_rule_registry.py` ——校验 `project_rules.md` 中所有 RULE-* 条目是否已在 `rule-registry.md` 的 TRAE 域登记 → 报告缺失/差异

### 全注册表自动同步（新增于 2026-05-08，因 FLE 组件漏登记）
5.1 `python scripts/governance/auto_sync_all_registries.py --all --warn-only` ——自动扫描 gate/dependency/version 变更 → 更新 gates/_registry.yaml + module-registry.yaml + blueprint-registry.yaml + cross-module-dependency-registry.yaml → 确保零孤儿

### MANDATORY-ZR 零残留强制自净（IRN-011 · ZR-008）
6. 临时文件扫描：`_temp*` / `_check*` / `_phase_*` 前缀文件 → DeleteFile（物理删除）
7. 确认本次 session 产生的所有 `.py` 文件已在合法三目录（`scripts/governance/` / `src/zephyr/` / `tests/`）中——不存在根目录孤儿
8. 如果 session 中删除过文件或目录 → 检查废墟引用残留（其他文件仍引用已删除路径）

### 记录
9. 写 Session Log（`session-logs/YYYY/MM/session-YYYYMMDD-NNN.yaml`）

### 💡 关键原则
- 你今天留下的临时文件，**永远不会被下一个 AI session 自动发现和清理**——临时文件 = 磁盘噪音 = 下一个 AI session 的认知负担
- 对标 AGENTS.md §5.3.3 + §5.3.5，IRN-011 ZR-003/ZR-005/ZR-007/ZR-008
