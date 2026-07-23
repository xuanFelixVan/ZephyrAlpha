---
module_id: GOV-036-PHASE4B-CLEANUP
status: deprecated
version: 3.0.0
created: '2026-06-22'
last_updated: '2026-06-22'
owner: human
purpose: 阶段4 STEP 4b 全量清洁的详细施工方案，包含域架构裁定、堵塞解除、清洁范围、执行步骤、验证标准
parent_doc: architecture_upgrade_discussion.md §5.5
review_log: |
  v2.1.0 修复8项审查问题（3严重+3中等+2轻微），增加隐藏消费者5类模式检查
  v2.2.0 修正域计数55→44
  v3.0.0 新增域架构裁定（三维度分析→43域），修正production口径，更新全文档一致性
ttl: permanent
---

> **裁定 #ARCH-REN-001（2026-06-26）**：6 个域 ID 连字符→下划线改名：
> D-GOV-DOCS→D-GOV_DOCS, D-GOV-ENFORCEMENT→D-GOV_ENFORCEMENT, D-GOV-SCRIPTS→D-GOV_SCRIPTS,
> D-GOV_AUDIT_TESTS→D-AUDITTEST, D-INTEGRATION-GATEWAY→D-INTEGRATION_GATEWAY, D-SECURITY-LLM→D-SECURITY_LLM。
> 本文档中出现的旧域名均为历史记录，已由上述裁定更新。


# 阶段4 STEP 4b：全量清洁施工方案

> **前置条件**：§5.5.1 定义的3项堵塞必须先解除
> **核心原则**：从 depgraph.db 出发，逐域裁定保留/删除；疑似文件必须四步审判；零消费者≠无价值
> **四步审判声明**：本方案的四步审判是 RULE-THREE 三步审判的细化展开——STEP 1-2 对应 RULE-THREE STEP 1-2，STEP 3+4 对应 RULE-THREE STEP 3（功能价值+废墟影响拆分为独立步骤）。铁律优先，本方案不改变 RULE-THREE 的判定标准。

## 一、堵塞解除（施工前必须完成）

| # | 堵塞项 | 类型 | 解除命令 | 预计耗时 |
|---|--------|------|---------|:-------:|
| 1 | git tag 未创建 | 硬 | `git tag phase-4-snapshot HEAD` | 10秒 |
| 2 | ide_health_service 未运行 | 硬 | `python scripts/ide_health_service.py --start` | 30秒 |
| 3 | 阶段4a搬家对齐完成状态 | 软 | Owner 确认 | — |

> 3项全部解除后，本方案可立即施工。

## 二、域架构裁定（施工前必须完成）

### 2.1 问题背景

depgraph.db 原始记录43个域，但项目规则（project_rules.md RULE-TEN）规定当前39平铺域。差异来自3个数据质量问题 + 5个D48拆分产物。需在清洁前先裁定域架构。

### 2.2 三维度分析框架

| 维度 | 来源 | 核心约束 |
|------|------|---------|
| 项目规则 | project_rules.md + trae_055 ARCH-CAP-001~007 + architecture_upgrade_discussion.md §2.1/§17.6 | 39平铺域 / 200硬上限 / <80考虑合并 / 平行域无子域 / 下划线命名 |
| 业界实践 | DDD黄金法则 + Vibe Coding Wall + 量化机构架构（Jane Street/Citadel/Two Sigma） | 1500模块推荐30-50域 / 单域20-50模块 / AI session上下文可覆盖 |
| 技术实质 | depgraph.db production节点 + 文件路径 + import分析 | 5个拆分产物的实际功能和耦合度 |

### 2.3 关键修正：production口径

ARCH-CAP-001 明确规定：**模块 = production 节点**（`design_maturity='production'`），禁止用总节点数做容量判定。

| 域 | 总节点数（错误口径） | **production节点数（正确口径）** |
|---|:---:|:---:|
| D-GOVERNANCE | 4285 | **138** |
| D-SECURITY | 849 | **134** |
| D-GOV_RULE | 175 | 175 |
| D-GOV_AUDIT | 69 | 69 |
| D-GOV_DRIFT | 22 | 22 |
| D-BEHAVIORAL_AUDIT | 60 | 60 |
| D-INFRA_RUNTIME | 726 | **1** |
| D-INFRA_OPS | 404 | **3** |

### 2.4 5个D48拆分产物逐域裁定

| 域 | production模块 | 合并后父域模块数 | 超200? | <80? | 物理迁移完成? | **裁定** | 裁定理由 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|------|
| D-GOV_RULE | 175 | 175+138=313 | ❌超限 | — | ❌未完成 | **保留** | 合并后313>200违反硬上限；规则执行引擎+门禁管线是独立业务能力 |
| D-GOV_AUDIT | 69 | 69+138=207 | ❌超限 | — | ❌未完成 | **保留** | 合并后207>200违反硬上限；审计追踪链+合规验证是独立业务能力 |
| D-GOV_DRIFT | 22 | 22+138=160 | ✅在150-200 | ❌22<80 | ❌未完成 | **合并回D-GOVERNANCE** | 22<80域过小（ARCH-CAP-002）；合并后160在150-200高度耦合区间；文件散落无独立ssot_path |
| D-BEHAVIORAL_AUDIT | 60 | 60+134=194 | ✅不超限 | ❌60<80 | ✅已完成 | **保留** | 拆分已物理完成（76个.py文件已迁移）；60模块构成完整独立域；回退成本高 |
| D-INFRA_RUNTIME | 1 | — | — | — | — | **重命名为D-INFRA_RUNTIME** | 设计域是D-INFRA_RUNTIME但DB缺失下划线版；D-INFRA_RUNTIME功能=应用运行时服务，与D-INFRA_RUNTIME语义一致 |

### 2.5 业界实践对标

| 业界指标 | 推荐值 | ZephyrAlpha裁定后 | 对标结果 |
|---------|--------|------------------|---------|
| 1500模块推荐域数 | 30-50 | 43 | ✅ 在区间内 |
| 单域模块数 | 20-50 | 平均36 | ✅ 在区间内 |
| Vibe Coding Wall | 50文件后AI退化 | 最大175(D-GOV_RULE) | ⚠️ D-GOV_RULE偏大，但合并会超200硬上限 |
| AI session可覆盖 | 单域≤50模块 | 3个域超50 | ⚠️ 需关注，未来D-GOV_RULE达200时再次拆分 |

### 2.6 最终域数裁定

```
39设计域（§17.6）
+ D-GOV_RULE（保留，第40域）
+ D-GOV_AUDIT（保留，第41域）
+ D-BEHAVIORAL_AUDIT（保留，第42域）
+ D-TEST（D77决策执行，第43域）
- D-GOV_DRIFT（合并回D-GOVERNANCE，22个节点domain_id改回）
= 43域
```

> D-GOVERNANCE合并后：138+22=160 production模块（150-200高度耦合区间，满足ARCH-CAP-003四标准）。

### 2.7 depgraph.db 域数据质量问题修复（11项操作）

| # | 操作 | 类型 | 影响范围 |
|---|------|------|---------|
| 1 | 删除6个连字符重复域 | DB清理 | D-AUTONOMY-CORE/PERM, D-GOV_AUDIT/DRIFT, D-INFRA-OPS, D-ML-TRAIN（0模块空壳） |
| 2 | 删除5个新空壳连字符域 | DB清理 | D-GOV-ENFORCEMENT/REPAIR/SCRIPTS, D-INTEGRATION-GATEWAY, D-SECURITY-LLM（0模块，不在39设计中） |
| 3 | D-INFRA_RUNTIME + D-INFRA_RUNTIME → D-INFRA_RUNTIME | 域重命名 | 2个域合并为1个下划线版 |
| 4 | D-GOV_DRIFT合并回D-GOVERNANCE | 域合并 | 22个节点domain_id改回D-GOVERNANCE |
| 5 | 创建D-TEST域 | D77执行 | 1个INSERT |
| 6 | 清理functional_domain_registry.yaml连字符条目 | YAML清理 | 12个条目 |
| 7 | 更新§17.6纳入D-GOV_RULE/D-GOV_AUDIT/D-BEHAVIORAL_AUDIT/D-TEST | 文档更新 | architecture_upgrade_discussion.md |
| 8 | 更新project_rules.md RULE-TEN域数39→43 | 规则更新 | project_rules.md第610行 |
| 9 | 修复D-BEHAVIORAL_AUDIT depgraph路径过时 | DB修复 | 60个节点file_path更新（文件已迁至behavioral_audit/但DB记录旧路径） |
| 10 | 修复D-INFRA_RUNTIME production节点分类 | DB修复 | 726个节点design_maturity重分类（大量实际存在的文件被误标为design/prototype） |
| 11 | 更新D-GOVERNANCE production节点数 | DB修复 | 138→160（合并D-GOV_DRIFT后） |

**执行顺序**：

```
STEP D1: 备份 depgraph.db
STEP D2: 删除11个连字符域（操作1-2）
STEP D3: D-INFRA_RUNTIME + D-INFRA_RUNTIME → D-INFRA_RUNTIME（操作3）
STEP D4: D-GOV_DRIFT合并回D-GOVERNANCE（操作4）
STEP D5: 创建D-TEST（操作5）
STEP D6: 清理YAML（操作6）
STEP D7: 更新文档和规则（操作7-8）
STEP D8: 修复depgraph路径和分类（操作9-11）
STEP D9: 验证（见§六 验证命令）
```

**验证命令**：

```bash
# 1. 域数验证（应为43）
python -c "import sqlite3; conn=sqlite3.connect('data/databases/depgraph.db'); print(f'Domains: {conn.execute(\"SELECT COUNT(*) FROM domains\").fetchone()[0]}')"

# 2. 连字符域清零验证（应为0）
python -c "import sqlite3; conn=sqlite3.connect('data/databases/depgraph.db'); print(f'Hyphen domains: {conn.execute(\"SELECT COUNT(*) FROM domains WHERE domain_id LIKE \\\"%-%\\\"\").fetchone()[0]}')"

# 3. D-GOV_DRIFT合并验证（应为0）
python -c "import sqlite3; conn=sqlite3.connect('data/databases/depgraph.db'); print(f'D-GOV_DRIFT nodes: {conn.execute(\"SELECT COUNT(*) FROM nodes WHERE domain_id=?\", (\"D-GOV_DRIFT\",)).fetchone()[0]}')"

# 4. D-TEST存在验证（应为1）
python -c "import sqlite3; conn=sqlite3.connect('data/databases/depgraph.db'); print(f'D-TEST exists: {conn.execute(\"SELECT COUNT(*) FROM domains WHERE domain_id=?\", (\"D-TEST\",)).fetchone()[0]}')"

# 5. production节点分布
python -c "
import sqlite3
conn=sqlite3.connect('data/databases/depgraph.db')
rows=conn.execute('SELECT d.domain_id, COUNT(n.node_id) FROM domains d LEFT JOIN nodes n ON d.domain_id=n.domain_id AND n.design_maturity=\"production\" GROUP BY d.domain_id HAVING COUNT(n.node_id)>0 ORDER BY COUNT(n.node_id) DESC').fetchall()
for r in rows: print(f'{r[0]:30s} {r[1]:5d}')
"
```

### 2.8 裁定后的43域清单

| # | 域ID | production模块 | 来源 |
|---|------|:---:|------|
| 1-38 | D-MKT_DATA...D-SHARED | 各异 | §17.6设计域（38个，D-INFRA_RUNTIME由D-INFRA_RUNTIME+D-INFRA_RUNTIME重命名而来） |
| 39 | D-INFRA_RUNTIME | 1→需重分类 | D-INFRA_RUNTIME重命名 |
| 40 | D-GOV_RULE | 175 | D48拆分保留 |
| 41 | D-GOV_AUDIT | 69 | D48拆分保留 |
| 42 | D-BEHAVIORAL_AUDIT | 60 | D-SECURITY拆分保留 |
| 43 | D-TEST | 待统计 | D77执行 |

> D-GOV_DRIFT（22模块）合并回D-GOVERNANCE，D-GOVERNANCE从138→160。

## 三、清洁范围（调查数据，2026-06-22）

### 3.1 总览

| 类别 | 数量 | 严重度 | 清洁策略 |
|------|:----:|:------:|---------|
| depgraph 零入度节点 | 3,024 | 🔴 | 按域逐个四步审判（**必须检查5类隐藏消费者**） |
| 其中幽灵节点（无文件路径） | 304 | 🔴 | 清理 depgraph.db 陈旧记录 |
| 迁移注册表旧路径仍存在 | 63 | 🔴 | 确认新路径有效后删除旧文件 |
| 迁移注册表新路径不存在 | 2,216 | 🔴 | 重新同步 depgraph.db + migration_registry |
| 空/仅注释 `__init__.py` | 221 | ⚠️ | 保留（包结构占位），标记脚手架 |
| 根目录临时文件 | 2 | ⚠️ | 直接删除 |
| `_fix` 前缀文件 | 1 | ⚠️ | **不删除**（见§四 STEP 2） |
| 注册表孤儿 | 0 | ✅ | 无需操作 |

### 3.2 零入度节点域分布（Top 10）

| 域 | 零入度数 | 占总量% | 备注 |
|----|:--------:|:------:|------|
| D-GOVERNANCE | 1,204 | 39.8% | 治理脚本天然零入边（被调度器调用，不被import） |
| D-OPS | 264 | 8.7% | 运维脚本 |
| D-INFRA_RUNTIME（原D-INFRA_RUNTIME） | 242 | 8.0% | 基础设施（含 rollback 47个零导入但被 `__init__.py` 重导出） |
| D-AUTONOMY_CORE | 190 | 6.3% | 含大量 `_` 前缀内部模块 |
| D-COMPLIANCE | 167 | 5.5% | 合规脚本 |
| D-TRADING | 133 | 4.4% | 交易运营 |
| D-INTEGRATION | 113 | 3.7% | 集成模块 |
| D-SECURITY | 87 | 2.9% | 安全模块（零入边≠可删；37个零导入被 `__init__.py` 动态导入） |
| D-SHARED | 85 | 2.8% | 共享服务 |
| D-RISK | 72 | 2.4% | 风控模块 |

> **关键判断**：D-GOVERNANCE 的 1,204 个零入度节点中，绝大多数是治理脚本——它们被 `phase_manager.py` 调度执行，不被其他模块 import。这不是"可删"信号，是"治理脚本天然属性"。

### 3.3 迁移残留旧文件（63个，按域分组）

| 旧路径目录 | 文件数 | 新路径目标 | 实际状态 |
|-----------|:------:|-----------|---------|
| `src/zephyr/alt_data/` | ~8 | `src/zephyr/data/vector_storage/` | 新旧并存（重复文件） |
| `src/zephyr/compliance/` | ~9 | `src/zephyr/compliance/`（保留，域已存在） | 旧文件即正确位置 |
| `src/zephyr/ex_core/adapters/` | ~5 | `src/zephyr/ex_core/` | 新旧并存 |
| `src/zephyr/ops/` | ~3 | `src/zephyr/observability/` | 新旧并存 |
| 其他散落 | ~38 | 需逐个确认 | — |

> **修正**：调查发现 pending 条目中**新旧路径同时存在** = 重复文件问题，不是"迁移未开始"。清理策略应调整为"删除旧路径重复文件 + 更新 status 为 done"。

### 3.4 幽灵节点（304个，无文件路径）

这些是 depgraph.db 中的陈旧记录——节点在数据库中存在但磁盘上无对应文件。需清理数据库记录。

## 四、施工步骤

### STEP 0：堵塞解除 + 基线采集

```
0a. 解除3项堵塞（见§一）
0b. 执行域架构裁定（见§二 STEP D1-D9）
0c. 备份关键文件：
    cp data/databases/depgraph.db data/databases/depgraph.db.backup.pre-cleanup
    cp data/databases/governance.db data/databases/governance.db.backup.pre-cleanup
0d. 运行全量基线扫描，产出基线报告：
    python scripts/governance/audit_registration.py --json > data/cleanup_log/baseline_audit.json
    python scripts/governance/d1_structure/detect_temp_files.py --scan-dir D:/ZephyrAlpha --warn-only > data/cleanup_log/baseline_temp.txt
0e. 创建 data/cleanup_log/ 目录
0f. 从 depgraph.db 导出零入度节点清单（用 python 替代 sqlite3 CLI，Windows 兼容）：
    python -c "
import sqlite3, csv
conn=sqlite3.connect('data/databases/depgraph.db')
rows=conn.execute('SELECT n.node_id, n.node_type, n.file_path, n.domain_id FROM nodes n WHERE n.node_id NOT IN (SELECT to_node_id FROM edges) AND n.node_type IN (\"module\",\"script\",\"gate\")').fetchall()
with open('data/cleanup_log/zero_inbound_nodes.csv','w',newline='') as f:
    csv.writer(f).writerows([('node_id','node_type','file_path','domain_id')]+rows)
print(f'Exported {len(rows)} zero-inbound nodes')
"
0g. 获取 RULE-ZERO 锁协议说明（后续 STEP 涉及文件写入时必须遵守）：
    写入前 → python scripts/lock_files.py check <file>
    写入 → python scripts/lock_files.py acquire <file> <session_id> --task "描述"
    写完 → python scripts/lock_files.py release <file> <session_id>
```

### STEP 1：根目录临时文件清理（2个文件，低风险）

| 文件 | 内容 | 审判结果 | 操作 |
|------|------|---------|------|
| `_error_details.txt` | 41个pytest错误列表 | STEP 1-4 全过：无注册、无重复、无独立功能、无废墟引用 | 删除 |
| `_pytest_output.txt` | pytest完整输出（1134KB） | STEP 1-4 全过：无注册、无重复、无独立功能、无废墟引用 | 删除 |

> 这2个文件是调试输出，不属于任何注册表，无代码引用，可直接删除。

### STEP 2：`_fix_and_lifecycle.py` 处置（1个文件，**不删除**）

| 文件 | 实际状态 | 操作 |
|------|---------|------|
| `src/zephyr/governance/_fix_and_lifecycle.py` | **有消费者**（`zephyr.testing.code_dedup.__init__`）、**有蓝图**（MOD-INF-017）、**STABILITY=frozen**、**AI_AUTONOMY=immutable_core** | **保留+迁移** |

> 该文件有消费者+蓝图+frozen/immutable_core 声明，禁止 AI 自主删除。应迁移到正确位置（`src/zephyr/testing/code_dedup/_fix_and_lifecycle.py`），而非删除。迁移属于 STEP 4a 搬家对齐范畴。

### STEP 3：迁移残留旧文件处理（63个）

```
3a. 逐文件确认（遵守 RULE-ZERO 锁协议）：
    - 新旧路径同时存在且内容相同？→ 删除旧文件 + 更新 migration_registry status=done
    - 新路径存在但旧文件内容更新？→ 以旧文件为准，覆盖新路径，删除旧文件
    - 新路径不存在？→ 标记为"迁移未完成"，不删除旧文件
3b. 对"迁移未完成"的文件：
    - 确认旧文件是否在正确位置（有些目录如 compliance/ 本身就是正确位置）
    - 如果旧文件在正确位置 → 更新 migration_registry 标记为 no_move_needed
    - 如果旧文件不在正确位置 → 标记为"需搬家"，留给 STEP 4a
3c. 更新 migration_registry.yaml（注意：文件名是下划线不是连字符）：
    标记已删文件 status=removed
3d. 每删一个文件后立即 Grep 废墟检查
```

### STEP 4：depgraph.db 幽灵节点清理（304个）

```
4a. 查询所有无文件路径的节点：
    python -c "
import sqlite3
conn=sqlite3.connect('data/databases/depgraph.db')
rows=conn.execute('SELECT node_id, node_type, domain_id, design_maturity FROM nodes WHERE (file_path IS NULL OR file_path = \"\") AND node_type IN (\"module\",\"script\",\"gate\")').fetchall()
print(f'Total ghost nodes: {len(rows)}')
for r in rows[:20]: print(r)
"
4b. 逐个确认：
    - 设计态节点？→ 保留（设计态文件尚未创建是正常的）
    - 运营态节点？→ 磁盘上确实不存在 → 删除节点 + 删除关联边
4c. 批量清理 SQL（先备份 depgraph.db）：
    DELETE FROM edges WHERE from_node_id IN (SELECT node_id FROM nodes WHERE (file_path IS NULL OR file_path = '') AND design_maturity='production')
    DELETE FROM nodes WHERE (file_path IS NULL OR file_path = '') AND design_maturity='production'
```

### STEP 5：零入度节点逐域审判（3,024个，按域分批）

**🔴 必须先检查5类隐藏消费者**（仅凭 Python import 链分析会遗漏约290个文件的真实消费者）：

| # | 隐藏消费者模式 | 受影响文件数 | 检测方法 |
|---|--------------|:----------:|---------|
| 1 | `__init__.py` 重导出（`from . import xxx`） | ~120+ | 读 `__init__.py` 的 `from . import` 块 |
| 2 | `__getattr__` 动态导入（`importlib.import_module()`） | ~82 | 读 `__init__.py` 的 `__getattr__` + `_SUBMODULES` |
| 3 | 函数内延迟导入 | ~47 | 读 `phase_check_registry.py` 函数体 |
| 4 | subprocess 调用（`subprocess.run([sys.executable, script])`） | ~11 | 读 `phase_check_registry.py` 的 subprocess 调用 |
| 5 | YAML/蓝图引用（配置文件中的路径字符串） | ~30+ | Grep YAML/MD 文件中的 `.py` 引用 |

**四步审判修正版**（STEP 1 增加隐藏消费者检查）：

```
STEP 1 登记检查（增强版）→ 文件是否在任何注册表/manifest/__init__.py 中？
  YES → 有登记价值。标记为"保留+对齐"，不进入删除流程
  NO  → 检查5类隐藏消费者：
    - 读同目录 __init__.py 的 from . import 块 → 有重导出？→ 标记"保留+对齐"
    - 读 __init__.py 的 __getattr__ / _SUBMODULES → 有动态导入？→ 标记"保留+对齐"
    - Grep phase_check_registry.py 中的文件名 → 有 subprocess 调用？→ 标记"保留+对齐"
    - Grep YAML/MD 文件中的文件名 → 有引用？→ 标记"保留+对齐"
    - 全无 → 进入 STEP 2
```

**高危文件保护清单**（零导入但有隐藏消费者，**禁止删除**）：

| # | 文件/目录 | 零导入数 | 隐藏消费者 | 删除后果 |
|---|----------|:--------:|----------|---------|
| 1 | `infrastructure/rollback/` 下47个 | 47 | `__init__.py` 第30-77行重导出 | 整个回滚包无法导入 |
| 2 | `security/access_control/` 下37个 | 37 | `__init__.py` `__getattr__` 动态导入 | RBAC/权限系统崩溃 |
| 3 | `security/llm_defense/llm_security_01/` 下21个 | 21 | `__init__.py` 重导出 | LLM 安全层不可用 |
| 4 | `ops/resilience/` 下9个 | 9 | `__init__.py` 重导出 | 弹性系统不可用 |
| 5 | `autonomy_core/kill_switch.py` | 1 | 模块体系隐式依赖 | 安全制动失效 |
| 6 | `infrastructure/rollback/trading_kill_switch.py` | 1 | `__init__.py` 第73行重导出 | 交易回滚崩溃 |
| 7 | 11个治理脚本（detect_orphan_py.py等） | 11 | `phase_check_registry.py` subprocess | Phase 门禁失败 |
| 8 | `adversarial_validation/__main__.py` | 1 | `python -m` CLI 入口 | 对抗验证 CLI 不可用 |

**分批策略**（按零入度数量从大到小，覆盖43域）：

| 批次 | 域 | 零入度数 | 预判 | 任务卡数 |
|:---:|----|:--------:|------|:-------:|
| 1 | D-GOVERNANCE | 1,204 | 治理脚本天然零入边，大部分保留 | 3 |
| 2 | D-OPS | 264 | 运维脚本，类似治理 | 1 |
| 3 | D-INFRA_RUNTIME（原D-INFRA_RUNTIME） | 242 | 含 rollback 47个零导入（**全部被 `__init__.py` 重导出，保留**） | 1 |
| 4 | D-AUTONOMY_CORE | 190 | 含 `_` 前缀内部模块 | 1 |
| 5 | D-COMPLIANCE | 167 | 合规脚本 | 1 |
| 6 | D-TRADING | 133 | 交易运营 | 1 |
| 7 | D-INTEGRATION | 113 | 集成模块 | 1 |
| 8 | D-SECURITY | 87 | 安全模块（**37个零导入被动态导入，全部保留**） | 1 |
| 9 | D-SHARED | 85 | 共享服务 | 1 |
| 10 | D-RISK | 72 | 风控模块 | 1 |
| 11 | D-GOV_RULE | 175 | 规则执行引擎，需逐个审查 | 1 |
| 12 | D-GOV_AUDIT | 69 | 审计追踪，需逐个审查 | 1 |
| 13 | D-BEHAVIORAL_AUDIT | 60 | 行为审计，需逐个审查 | 1 |
| 14 | 其余30域 | ~265 | 按域建卡 | 3-5 |
| **合计** | **43域** | **3,024** | — | **17-20** |

**D-GOVERNANCE 特殊处理**（占总量 40%）：

```
5a. 先过滤：排除 node_type='script' 的治理脚本（天然零入边，保留）
5b. 剩余非脚本零入度节点 → 四步审判（增强版）
5c. 预计 80%+ 为治理脚本，实际需审判的约 200-300 个
```

**D-SECURITY 特殊处理**（安全模块零入边≠可删）：

```
5d. 安全模块零入边节点 → 全部标记为"保留+接通"
5e. 不进入删除流程，只记录"需接通管线"
5f. 特别保护：access_control/ 下37个零导入文件被 __getattr__ 动态导入，禁止删除
5g. 特别保护：llm_security_01/ 下21个零导入文件被 __init__.py 重导出，禁止删除
```

**D-INFRA_RUNTIME 特殊处理**（含 rollback 包）：

```
5h. rollback/ 下47个零导入文件被 __init__.py 重导出，全部保留
5i. 特别保护：trading_kill_switch.py 零导入但被 __init__.py 第73行重导出
```

### STEP 6：迁移注册表同步（2,216个新路径缺失）

```
6a. 从 depgraph.db 查询当前实际存在的文件路径
6b. 对比 migration_registry.yaml（注意：下划线不是连字符）中的 new_path
6c. 更新策略：
    - new_path 对应的文件已通过搬家到达新位置 → 更新 migration_registry
    - new_path 对应的文件不存在 → 标记为 pending，等待搬家
    - new_path 对应的文件在另一路径 → 更新 new_path 为实际路径
    - status=migrated 但旧路径仍存在 → 更新为 status=done + 删除旧文件
6d. ⚠️ 架构升级期间禁止运行 generate_project_depgraph.py（会覆盖 depgraph.db）
    改用只读验证：python scripts/governance/extract_depgraph.py --summary
```

### STEP 7：空 `__init__.py` 标记（221个，不删除）

```
7a. 扫描所有空/仅注释的 __init__.py
7b. 在 depgraph.db nodes 表标记 design_maturity='scaffold_placeholder'
7c. 不删除——包结构占位文件是合法的
```

### STEP 8：全量验证 + 产出

```
8a. 运行验证命令（全部 exit 0 = 清洁完成）：
    # 1. 注册审计
    python scripts/governance/audit_registration.py --json
    # 2. 依赖图诊断
    python scripts/governance/diagnose_depgraph.py
    # 3. 路径树更新
    python scripts/governance/generate_project_path_tree.py --write
    # 4. 临时文件扫描
    python scripts/governance/d1_structure/detect_temp_files.py --scan-dir D:/ZephyrAlpha --warn-only
    # 5. 架构契约一致性
    python scripts/governance/d5_architecture/checkers/check_contract_code_drift.py
    # 6. 关键模块导入测试
    python -c "import zephyr.shared; import zephyr.governance; print('OK')"
8b. ⚠️ 架构升级期间禁止运行 generate_project_depgraph.py
    改用只读验证：python scripts/governance/extract_depgraph.py --summary
8c. 产出 cleanup_summary.yaml（见下方格式）
8d. 健康度9指标全部达标
```

**cleanup_summary.yaml 格式**：

```yaml
meta:
  generated_at: '2026-06-xxT...'
  phase: 4b
  rounds_completed: 2

statistics:
  before:
    total_files: N
    orphan_modules: N
    orphan_scripts: N
    temp_files: N
    zombie_references: N
    zero_inbound_nodes: 3024
    ghost_nodes: 304
    domain_count_raw: 55
    domain_count_effective: 43
  after:
    total_files: N
    orphan_modules: 0
    orphan_scripts: 0
    temp_files: 0
    zombie_references: 0
    zero_inbound_nodes_remaining: N
    ghost_nodes: 0
    domain_count: 43

actions:
  registered: N
  deleted_duplicate: N
  deleted_no_value: N
  connected: N
  human_pending: N
  domains_merged: 1  # D-GOV_DRIFT → D-GOVERNANCE
  domains_renamed: 2  # D-INFRA_RUNTIME + D-INFRA_RUNTIME → D-INFRA_RUNTIME
  domains_created: 1  # D-TEST
  domains_deleted: 11  # 6连字符重复 + 5空壳连字符

domain_coverage:  # 43域覆盖矩阵
  D-MKT_DATA: done
  D-GOVERNANCE: done
  D-GOV_RULE: done
  D-GOV_AUDIT: done
  D-BEHAVIORAL_AUDIT: done
  D-TEST: done
  ...
```

**健康度达标判定**（全部达标 = 清洁成功）：

| 指标 | 目标 |
|------|------|
| 孤儿模块数 | 0 |
| 孤儿脚本数 | 0 |
| 临时文件数 | 0 |
| 僵尸引用数 | 0 |
| `__all__` 缺失包数 | 0 |
| depgraph 断裂数 | 0 |
| 关键模块导入成功率 | 100% |
| 注册表与磁盘一致率 | 100% |
| depgraph.db 模块计数与实际偏差 | 0 |
| 域数 | 43 |
| 连字符域数 | 0 |

## 五、执行顺序与依赖

```
STEP 0（堵塞解除+域架构裁定+基线采集）→ 最先执行
  ↓
STEP 1（根目录临时文件）→ 无依赖
STEP 2（_fix 文件迁移）→ 无依赖（不删除，迁移到正确位置）
STEP 3（迁移残留旧文件）→ 无依赖，遵守 RULE-ZERO 锁协议
STEP 4（幽灵节点清理）→ 无依赖
  ↓
STEP 5（零入度节点逐域审判）→ 依赖 STEP 4（幽灵节点清理后零入度清单更准确）
  ↓
STEP 6（迁移注册表同步）→ 依赖 STEP 3+5（文件处置完成后才能准确同步）
  ↓
STEP 7（空 __init__.py 标记）→ 可与 STEP 5-6 并行
  ↓
STEP 8（全量验证）→ 依赖 STEP 1-7 全部完成
```

**可并行组**：

| 并行组 | 包含步骤 | 理由 |
|--------|---------|------|
| 并行组1 | STEP 1 + 2 + 3 + 4 | 互不依赖，操作不同文件集 |

## 六、风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| 误删被 `__init__.py` 重导出的零导入文件 | **高** | **极高** | 四步审判 STEP 1 增加隐藏消费者检查；rollback/47个、security/37个、llm_security_01/21个全部保护 |
| 误删安全/治理模块 | 中 | 高 | D-SECURITY 零入边节点全部标记"保留+接通"，不进删除流程 |
| 迁移注册表同步引入错误 | 中 | 中 | 同步前备份 migration_registry.yaml，同步后 diff 确认 |
| depgraph.db 清理导致数据丢失 | 低 | 高 | 清理前 `cp depgraph.db depgraph.db.backup.pre-cleanup` |
| 63个旧文件删除后引用断裂 | 低 | 中 | 每删一个文件立即 Grep 废墟检查 |
| 运行 generate_project_depgraph.py 覆盖 depgraph.db | 低 | **极高** | **架构升级期间禁止运行**，改用 extract_depgraph.py --summary |
| 域架构裁定引入新的数据不一致 | 中 | 高 | 裁定后运行5条验证命令（§2.7），全部通过才进清洁步骤 |

## 七、人力审批清单（STEP 5 执行过程中产出）

> 以下类型的裁定必须人类审批后才能执行删除：
> - STEP 3 功能价值裁定 ALL=NO 的文件
> - D-SECURITY 域的任何删除建议
> - 任何 `kill_switch` / `alert` / `capacity` / `rollback` 相关文件
> - 任何被 `__init__.py` 重导出但看似零导入的文件（如判定需删除）
> - 域架构裁定中的域合并/重命名/删除操作（§二 STEP D1-D9）

**审批流程**：AI 产出审批清单 → Owner 逐项确认 → 确认后才执行删除。

## 八、不做的事项

| # | 不做 | 理由 |
|---|------|------|
| 1 | 删除空 `__init__.py` | 包结构占位，删除会破坏 import |
| 2 | 合并功能相似文件 | 属于重构，不属于清洁 |
| 3 | 修改文件内容 | 清洁只做保留/删除/注册，不改代码 |
| 4 | 处理 D-GOVERNANCE 治理脚本零入边 | 天然属性，不是问题 |
| 5 | 处理设计态节点缺失文件 | 设计态文件尚未创建是正常的 |
| 6 | 删除 `_fix_and_lifecycle.py` | 有消费者+蓝图+frozen/immutable_core，应迁移而非删除 |
| 7 | 运行 `generate_project_depgraph.py` | 架构升级期间禁止运行（会覆盖 depgraph.db） |
| 8 | 删除被 `__init__.py` 重导出的零导入文件 | 隐藏消费者，删除会导致包导入崩溃 |
| 9 | 将 D-GOV_RULE 合并回 D-GOVERNANCE | 合并后313>200违反硬上限 |
| 10 | 将 D-GOV_AUDIT 合并回 D-GOVERNANCE | 合并后207>200违反硬上限 |
| 11 | 将 D-BEHAVIORAL_AUDIT 合并回 D-SECURITY | 拆分已物理完成，回退成本高 |
