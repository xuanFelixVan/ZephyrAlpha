# ZephyrAlpha 首关 — AI 入群唯一入口

> v0.20.0 | Python 3.12+ | Pydantic V2 | ~24K 资产 | 健康 A(94.0)
> 本文件由 IDE 自动注入每个 AI 对话。全读完再开工。

---

## 资产全景

| 资产 | 数量 | 发现入口 |
|------|:---:|------|
| 模块 | 1,623 | [registry-of-registries.yaml](file:///d:/ZephyrAlpha/docs/registry-of-registries.yaml) |
| 脚本 | 388 | `scripts/script_manifest.yaml` |
| 门禁 | 20 | `src/zephyr/gates/_registry.yaml` |
| 蓝图 | 41 | `docs/03_modules/blueprint-registry.yaml` |
| 模板 | 13 | `docs/03_modules/template-registry.yaml` |
| Agent Skill | 21 | `python -m zephyr.agent_spec list` |

> 创建任何新功能前，MUST 先搜索 388 脚本 + 1,623 模块中是否已有覆盖。不搜索 = 违规。

---

## PRE-OP：任何操作前必须通过的强制检查

| 你要做什么 | 必须先问自己 | 答案=NO时的强制命令 |
|-----------|-------------|-------------------|
| **进入新 session** | Phase 0 检查全部 GREEN？ | `from zephyr.governance.phase_manager import session_startup; r=session_startup(); print(r['next_action'])` |
| **创建新文件** | 文件已在注册表中？ | `python scripts/scaffold.py module/script/gate ...` |
| **修改已有文件** | 拿到锁了？pre_write_gate 通过？ | `python scripts/governance/pre_write_gate.py <file>` → exit 0 → `python scripts/lock_files.py acquire <file> <session_id>` |
| **删除任何文件** | 文件每一行内容在别处还有？ | RULE-THREE 三步审判 → 全通过才能删 |
| **任何新功能** | 已有脚本/模块覆盖？ | 搜 registry-of-registries.yaml → Grep → 复用决策 |
| **结束 session** | 锁释放？临时文件清？ | `python scripts/lock_files.py release-all` + 零残留扫描 |
| **处理任何任务** | 有对应 Agent Skill？ | `python -m zephyr.agent_spec list` → 匹配 → `progressive_load(skill_id)` |

跳过任何一步 → 可能产生孤儿文件、死锁、重复轮子。

---

## FIRST-READ：入项目第一步

```
1. 读 docs/registry-of-registries.yaml → 了解全项目有什么
2. 读 docs/01_policies_and_standards/_registry/catalogs/project-path-tree.yaml → 项目现在长什么样
3. 读 docs/03_modules/_sys-master/blueprint.md §0 → 定位子系统任务域
4. 读本文件（project_rules.md）→ 了解怎么做事
5. 按需定位具体注册表 → 开工
```

| # | 绝对禁止 | 后果 |
|---|---------|------|
| ❌ | 跳过 registry-of-registries.yaml 直接开工 | 不知道已有模块/脚本 → 重复造轮子 |
| ❌ | 创建新文件前不查 registry-of-registries.yaml | 孤儿文件 |
| ❌ | 看到注册表中 `?` 条目不管不问 | 注册表过期——认知偏差累积 |

---

## RULE-ZERO：文件锁协议

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

### session_id 格式

`session-YYYYMMDD-NNN`，从 `session-logs/` 目录找编号。

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

**触发**：AI 产出任何新功能时。

### 强制五问

| # | 问题 | 不满足 → 处置 |
|---|------|-------------|
| 1 | 谁调用它？入口在哪？ | 没有入口 → 不能关闭任务 |
| 2 | 谁发现它？下一个 AI session 怎么知道？ | 没有发现机制 → 必须先注册 |
| 3 | 谁维护它？放在哪个模块/目录下？ | 没有归属 → 不能落盘 |
| 4 | 谁校验它？有 gate 检查吗？ | 没有校验 → 必须添加 gate |
| 5 | 谁更新它？模板/清单/注册表已更新？ | 没有 → 必须更新 |

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

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 创建 .py 文件但不注册到 script_manifest.yaml | 孤儿脚本 |
| ❌ | 写了新功能但不建立任何调用入口 | 死代码 |
| ❌ | 新增 gate 只写名字不写实现 | 假门禁 |
| ❌ | 完成任务卡后不检查"下游有没有人用" | 孤儿功能 |

---

## RULE-THREE：删除前置确认

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
| `src/zephyr/gates/<id>.yaml` | `scaffold.py gate <id>` | `src/zephyr/gates/_registry.yaml` |

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

---

## RULE-FIVE：临时文件零残留

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

### 四指标机械门

```
├─ 指标 1: 预计产生 > 50 行新代码？ → YES → 走任务系统
├─ 指标 2: 涉及修改 > 3 个文件？ → YES → 走任务系统
├─ 指标 3: 需要读取蓝图/设计文档？ → YES → 走任务系统
├─ 指标 4: 是数据库 Schema 变更？ → YES → 走任务系统
└─ 全 NO → 直接做，不走任务系统
建卡后立刻施工——不等用户确认
```

**RULE-ZERO-TASK**：建卡唯一合法路径 = `BlueprintDecomposer.decompose(blueprint_path)` → TaskCard → SQLite。禁止手写 `.md` 建卡，禁止直接 `TaskRepository.create()` 建卡。

**任务系统二元路由**：

| 判定 | 路由 | 入口 |
| 任一指标 YES | MUST 走任务系统 | `BlueprintDecomposer.decompose(blueprint_path)` → TaskCard → SQLite |
| 全 NO | 直接做，不走任务系统 | 直接施工 |

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

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 四指标任一触发但不建卡 | 无法跨 session 追溯 |
| ❌ | 全不触发但建卡 | 任务卡膨胀 |
| ❌ | 建卡后等用户确认再开工 | 打断用户流——建卡是静默操作 |
| ❌ | 用"感觉"判断是否建卡 | 模糊标准 → 每次结果不同 |

---

## RULE-SEVEN：脚本并行化 + 创建即自测

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

### 强制三步（任何新代码创作前 MUST 执行）

```
STEP 1: 关键词全局搜索
  → SearchCodebase(自然语言) + Grep（scripts/ + src/zephyr/ + tests/）

STEP 2: 注册表精确匹配
  → 读 registry-of-registries.yaml → 找相关 REG-* → 对照已有条目

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

> 详见 [onboarding_detail.md §15](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)

### 绝对禁止

| # | 行为 | 后果 |
|---|------|------|
| ❌ | 不推演直接移动模块 | 引入新循环依赖，系统堵塞 |
| ❌ | 按数量从大到小治理 | 前面的决定可能让后面的问题消失，白做 |
| ❌ | 用"零消费者"判定删除 | 误删有价值的安全/治理组件 |
| ❌ | 先补测试再重构 | 重构改代码，测试白写 |

---

## RULE-ELEVEN：跨蓝图变更通知

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

## 防幻觉十八条（Vibe Coding 铁律）

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

**格式标准**: [code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)

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
| 5 | **防幻觉头部**——新建/修改代码文件 MUST 包含 `[BLUEPRINT]`/`[MODULE]`/`[INVARIANTS]`/`[MODIFY-GUARD]`/`[CONSUMERS]`/`[STABILITY]`/`[SAFETY]`/`[AI_AUTONOMY]`/`[ERROR_CONTRACT]`/`[TESTS]` 十字段头部。缺失 = 孤儿文件 |
| 6 | **根因追踪（MTH-006）**——遇到 bug/失败/漂移/异常 → MUST 追问到底：连问为什么直到找到最根部原因，**不是固定5个——是问到底**。追问路上发现的每个中间问题 MUST 一并解决，不留尾巴。治根判定：修复后同类问题不再产生 + 作用于设计层面 + 可泛化为原则。禁止只修症状不治根 |
| 7 | **搜索先行复用决策**——新建功能前 MUST 搜索已有覆盖。搜索三步：①关键词全局搜索 ②注册表精确匹配 ③复用决策。复用四选一：完全覆盖→直接用 / 80%→扩展已有 / 50%→重构+扩展 / 0%→scaffold 新建。放弃新建时 MUST 写 `[REUSE-DECISION]` |
| 8 | **编码安全**——Python `open(path, 'w')` 禁止省略 `encoding='utf-8'`；PowerShell 写文件用 `[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)`；禁止 Trae+Cursor 同时打开同一文件；扫描器大量报错 → 先检查扫描器逻辑 |
| 9 | **修改原则**——发现事实错误 → 直接修正，禁止添加"之前为什么是错的"解释段；文档中所有数字/版本号/计数必须是当前唯一真实值；单个 real number 原则：一个事实在所有蓝图中只能有一个数字，不一致 = bug |
| 10 | **审计前置**——任何涉及文件变更的任务完成后 MUST 执行审计清单。不审不清，不清不继续 |
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
| 任何文件变更后 | `python scripts/governance/audit_registration.py` | 有孤儿 → 禁止关闭任务 |
| 修改蓝图§5.5自动化触发机制 / 修改代码实现 | `python scripts/governance/d5_architecture/checkers/check_blueprint_automation_sync.py --blueprint <蓝图路径>` | §5.5状态列与代码不一致 → 禁止关闭任务 |
| **蓝图-代码双向对齐** | 蓝图 §4 文件清单 ↔ 代码 `[BLUEPRINT]` 字段互相验证 | 不对齐 → 漂移，禁止关闭任务 |
| **蓝图-代码-路径树三方对齐** | 结构变更后 MUST 同步刷新：`generate_project_depgraph.py` + `generate_project_path_tree.py --write` + 蓝图 §4 | 任一方过时 → AI 看到幻影/漏掉真实文件 → 禁止关闭任务 |
| **创建/删除/移动文件后** | `python scripts/governance/generate_project_path_tree.py --write` | 路径树过时 → 下个 session 冷启动看到错误结构 → 禁止关闭任务 |
| 安全敏感变更 | `python scripts/governance/d6_security/scan_secret_leak.py` | 泄漏 → 硬阻断 CI |
| 回滚/撤销 | `python scripts/rollback.py preflight` → CLEAN → `rollback.py <cmd>` | preflight FAIL → 禁止回滚 |
| Agent间协作/多Agent/冲突 | `from zephyr.a2a import GovernanceAdapter; adapter.verify_pair(a, b)` + Skill 路由 a2a → SKILL-DOM-A2A-001 | 静默失败 + 死锁无防护 |
| 高风险操作（批量/安全） | `from zephyr.escalation import EscalationEngine; EscalationEngine().evaluate(RuleCategory, desc)` | 可能执行本应变 blocked 的操作 |
| 多Agent/MCP 委托 | `from zephyr.escalation import DelegationEngine; engine.delegate(event, strategy)` | 死锁/循环委托/深度溢出 |
| LLM API 调用前 | `from zephyr.budget_enforcer import BudgetEngine; engine.pre_flight_check(operation_id, tokens, cost)` | 超预算 → 降级或拒绝 |
| 任何写入/执行/修改前 | `guard.check(identity, operation, target_path)` — PermissionGuard | BLOCKED → 禁止执行 |
| 施工前：检查已有知识 | `kb.search("<关键词>")` | 重复造轮子 / 违反已有决策 |
| 施工后：写入知识 | `kb.write(topic="...", content="...", provenance=build_provenance(...))` | 知识丢失 → 下个 session 不知道 |

---

## Session 冷启动序列

进入项目后 MUST 按以下顺序执行（不可跳过、不可重排）：

```
STEP 1   — 读 docs/registry-of-registries.yaml → 了解全项目注册表
STEP 1.1 — 读 docs/03_modules/template-registry.yaml → 了解可用模板
STEP 1.2 — 读 project-path-tree.yaml → 项目现在长什么样
STEP 1.5 — 读 docs/03_modules/_sys-master/blueprint.md §0 → 定位子系统任务域
STEP 2   — 读本文件（project_rules.md）→ 了解硬规则
STEP 3   — Session Continuity 恢复: 上一个 session 做了啥 / 未完成任务 / 锁状态
STEP 4   — Phase Manager: 当前施工阶段（46 个门控检查）
STEP 4.5 — 资产盘点: unified_asset_index.yaml（总资产/健康评分/孤儿率）
STEP 4.6 — Skill 发现: python -m zephyr.agent_spec list（19 个已注册 Skill）
STEP 4.7 — KB 自检: bootstrap 扫描文档 → 填充知识库 → 施工前查已有 KE
STEP 4.8 — Escalation Protocol 激活: 升级/委托安全网
STEP 4.9 — Drift Detector 初始化: 39 个检测器 + 漂移预算检查
STEP 4.10 — Agent RBAC 激活: 身份注册 + PermissionGuard + 55 模块完整性
STEP 4.11 — Rollback System 激活: preflight + AutoTrigger + Kill Switch
STEP 4.12 — Budget Enforcer 激活: Token/Cost/Time 三维预算
STEP 4.13 — Audit Trail: 审计链完整性 + 最近 50 条事件注入
STEP 4.14 — A2A Protocol: 发现→通信→调度→防护 四段检查
STEP 5   — 按需定位具体注册表 → 开工
```

不完成 STEP 1-4.14 = 不可开工。

---

## Session 开关门

**进门**: 读 [registry-of-registries.yaml](file:///d:/ZephyrAlpha/docs/registry-of-registries.yaml) → 读 `docs/03_modules/_sys-master/blueprint.md` §0 → `python -m zephyr.agent_spec list`

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
7. 零残留扫描: _temp* / _check* / _fix* / _phase_* 前缀文件 → 全部删除
8. 确认本次 session 产生的所有 .py 文件在合法三目录中
9. 废墟引用检查: 删过文件/目录 → 确认无其他文件引用已删路径
10. 写 Session Log（session-logs/YYYY/MM/session-YYYYMMDD-NNN.yaml）
```

---

## 触发关键词 → Agent Skill 路由

| 关键词 | Skill |
|--------|-------|
| database / sql / migration | SKILL-DOM-DBS-001 |
| mcp / server / tool | SKILL-DOM-MCP-001 |
| context / pipeline | SKILL-DOM-CTX-001 |
| feedback / loop / 根因 / 5 Whys / 治根 / 追问到底 / 诊断反转 | SKILL-DOM-FBL-001 |
| gate / rule / policy | SKILL-DOM-GAT-001 |
| permission / rbac | SKILL-DOM-AGT-001 |
| blueprint / architecture | SKILL-DOM-BLU-001 |
| audit / drift / governance | SKILL-DOM-DRF-001 |
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

加载: `python -m zephyr.agent_spec load <skill_id>`
Python API: `from zephyr.agent_spec.integration.pipeline_bridge import PipelineSkillBridge; PipelineSkillBridge.inject_for_task("任务描述")`

---

## 不确定时的默认路径

```
1. 撞门禁 → 读门禁输出 → 按输出说的做
2. 不知道有什么 → 搜 registry-of-registries.yaml
3. 不知道怎么做 → python -m zephyr.agent_spec list → 匹配关键词 → 加载 Skill
4. 不知道能不能改 → 搜 docs/01_policies_and_standards/
```

---

## 关键标准速查

| 领域 | 标准 | module_id |
|------|------|-----------|
| 治理决策 | [governance-methodology-standard.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/meta/governance-methodology-standard.md) | PS-STD-011 |
| 代码构建 | [code-construction-standards.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md) | GOV-ENG-001 |
| 脚本质量 | [quality-standard.md](file:///d:/ZephyrAlpha/scripts/governance/quality-standard.md) | SCRIPT-QUALITY-001 |
| AI 压缩工作流标准 | [compression-workflow-standard.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/document/compression-workflow-standard.md) | GOV-DOC-011 |
| Session 状态机 | [session-state-runbook.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-session-state-runbook.md) | OPS-VC-002 |
| 会话门禁 | [gate-checklist.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/vibe-coding-gate-checklist.md) | OPS-VC-005 |
| 事故响应 | [incident-playbook.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/ai-incident-and-emergency-playbook.md) | OPS-VC-004 |
| Vibe Coding 入口 | [vibe_coding/index.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/operational/vibe_coding/index.md) | OPS-VC-001 |
| 模板 | [template-registry.yaml](file:///d:/ZephyrAlpha/docs/03_modules/template-registry.yaml) | REG-TEMPLATE-001 |

> 详细规则、施工指导、方法论参考 → 见 [`.trae/rules/onboarding_detail.md`](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md)
