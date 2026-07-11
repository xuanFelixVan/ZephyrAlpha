# D_TRADING 域拆分实施计划（Phase 2）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 D_TRADING 域 280 production 节点降至 ~43，通过拆出 feedback_loop 和 orchestrator 到独立域

**Architecture:** 新建2个域 + depgraph SQL UPDATE by path prefix + 批量替换175个代码表头 + 蓝图/文档/注册表同步 + 循环验证至0遗漏

**Tech Stack:** PostgreSQL (depgraph), Python (psycopg2), PowerShell, session_worktree

---

## 前置上下文

### 依赖关系
- **Phase 1（D_GOVERNANCE 拆分）必须完成**：OPS-2026071201~009 全部 closed
- 方案文档：`docs/_working/domain_split_proposal_d_governance_d_trading.md`

### 数据库连接
所有 Python 脚本连接 depgraph (PostgreSQL) 的标准方式：
```python
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\src")
sys.path.insert(0, r"d:\ZephyrAlpha\scripts\governance")
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2

conn = psycopg2.connect(**_build_pg_dsn())
conn.autocommit = False  # 事务模式，需显式 commit
```

### 关键表结构
- `nodes` 表：`domain_id`（FK→domains）、`path`（代码路径）、`design_maturity`（值 production/prototype/design）、`build_status`（值 generated/stable/planned/testing/deprecated）
- `domains` 表：`domain_id`（PK，CHECK `^D_[A-Z][A-Z0-9_]*$`）、`domain_name`、`domain_group`（NOT NULL）、`ssot_path`、`lifecycle`（CHECK operational/design_only/prototype/deprecated）、`build_status`（CHECK planned/generated/testing/stable/deprecated）、`layer_id`（CHECK L0_infrastructure/L1_foundation/L2_domain/L3_application/NULL）、`production_nodes`（缓存列）
- 表均在 `public` schema 下

### 迁移映射
| 迁移条件 | 目标域 | 代码目录 | 文件数 | 当前表头 |
|---|---|---|---|---|
| path LIKE 'src/zephyr/trading/feedback_loop/%' | D_FEEDBACK_LOOP | feedback_loop/ | 100 | D_OPS / D_INFRA_RUNTIME |
| path LIKE 'src/zephyr/trading/orchestrator/%' | D_ORCHESTRATOR | orchestrator/ | 75 | D_INFRA_RUNTIME |

### 新域定义参数
| domain_id | domain_name | ssot_path | blueprint_id | layer_id | lifecycle | build_status |
|---|---|---|---|---|---|---|
| D_FEEDBACK_LOOP | feedback_loop_engine | src/zephyr/trading/feedback_loop/ | MOD-FEEDBACK_LOOP | L1_foundation | operational | stable |
| D_ORCHESTRATOR | agent_orchestrator | src/zephyr/trading/orchestrator/ | MOD-INF-039 | L1_foundation | operational | stable |

> **注意**：任务卡中 D_ORCHESTRATOR 的 layer_id 标注为 `cross_layer`（概念层），但 DB CHECK 约束仅允许 `L0_infrastructure/L1_foundation/L2_domain/L3_application`。蓝图文件 `layer: L1_foundation`，故 DB 层使用 `L1_foundation`。

---

## Task 1: OPS-2026071202 — D_TRADING 域拆分总卡（depgraph 映射阶段）

**依赖**：OPS-2026071201（Phase 1 D_GOVERNANCE 总卡）必须已 closed
**目标**：创建 Phase 2 工作环境，验证前置条件

- [ ] **Step 1: 验证 Phase 1 已完成**

运行以下命令检查 Phase 1 任务卡状态：

```powershell
cd d:\ZephyrAlpha
python -c "import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance'); from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2; conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor(); cur.execute(\"SELECT domain_id, production_nodes FROM domains WHERE domain_id IN ('D_GOVERNANCE','D_GOV_AUDIT','D_GOV_DRIFT','D_GOV_ENFORCEMENT','D_GOV_KB','D_GOV_SCRIPTS') ORDER BY domain_id\"); [print(f'{r[0]}: {r[1]} production nodes') for r in cur.fetchall()]; conn.close()"
```

预期输出（Phase 1 完成后 D_GOVERNANCE 应已降至 ~306）：
```
D_GOVERNANCE: ~306 production nodes
D_GOV_AUDIT: 58 production nodes
D_GOV_DRIFT: 57 production nodes
D_GOV_ENFORCEMENT: ~144 production nodes
D_GOV_KB: 22 production nodes
D_GOV_SCRIPTS: 440 production nodes
```

- [ ] **Step 2: 查询 D_TRADING 当前状态（拆分前基线）**

```powershell
cd d:\ZephyrAlpha
python -c "import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance'); from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2; conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor(); cur.execute(\"SELECT domain_id, production_nodes FROM domains WHERE domain_id = 'D_TRADING'\"); r = cur.fetchone(); print(f'D_TRADING: {r[1]} production nodes (pre-split)'); cur.execute(\"SELECT COUNT(*) FROM nodes WHERE domain_id = 'D_TRADING' AND path LIKE 'src/zephyr/trading/feedback_loop/%'\"); print(f'  feedback_loop 路径下: {cur.fetchone()[0]} 节点'); cur.execute(\"SELECT COUNT(*) FROM nodes WHERE domain_id = 'D_TRADING' AND path LIKE 'src/zephyr/trading/orchestrator/%'\"); print(f'  orchestrator 路径下: {cur.fetchone()[0]} 节点'); conn.close()"
```

预期输出：
```
D_TRADING: 280 production nodes (pre-split)
  feedback_loop 路径下: ~336 节点（含 production + design + prototype）
  orchestrator 路径下: ~74 节点（含 production + design + prototype）
```

- [ ] **Step 3: 创建 session_worktree**

```powershell
cd d:\ZephyrAlpha
python scripts\governance\session_worktree.py start --session phase2-d-trading-split
```

预期输出：
```
[OK] session_worktree 创建成功: d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
```

> 后续所有 Task 在此 worktree 中操作：`cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split`

- [ ] **Step 4: 验证 PYTHONPATH 和 DB 连接**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2; conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor(); cur.execute('SELECT version()'); print(cur.fetchone()[0]); conn.close()"
```

预期输出：
```
PostgreSQL 16.x on x86_64-pc-linux-gnu, ...
```

---

## Task 2: OPS-2026071210 — 新建 D_FEEDBACK_LOOP + D_ORCHESTRATOR 域定义

**依赖**：OPS-2026071202（Task 1）
**目标**：在 5 处真源中创建 2 个新域定义

### 5 处真源清单（每域）
1. depgraph DB `domains` 表 INSERT
2. `architecture_model/index.yaml`（由 reconciler 从 DB 自动生成）
3. `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`
4. `scripts/governance/d5_architecture/generators/domain_name_mapping.py`
5. `docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml`

- [ ] **Step 1: 在 depgraph DB domains 表 INSERT D_FEEDBACK_LOOP**

创建脚本 `d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\scripts\governance\_phase2_insert_domains.py`：

```python
"""Phase 2: 在 domains 表中新建 D_FEEDBACK_LOOP 和 D_ORCHESTRATOR 域"""
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\src")
sys.path.insert(0, r"d:\ZephyrAlpha\scripts\governance")
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
from datetime import datetime, UTC

now_iso = datetime.now(UTC).isoformat()

INSERT_SQL = """
INSERT INTO domains (
    domain_id, domain_name, domain_group, description, ssot_path,
    current_modules, max_modules, lifecycle, created_at, updated_at,
    build_status, modification_permission, layer_id, target_modules,
    production_nodes
) VALUES (
    %s, %s, %s, %s, %s,
    0, 150, 'operational', %s, %s,
    'stable', 'ai_modifiable', 'L1_foundation', 150,
    0
)
ON CONFLICT (domain_id) DO NOTHING
"""

domains = [
    (
        "D_FEEDBACK_LOOP",
        "feedback_loop_engine",
        "foundation",
        "反馈循环引擎——自我改进闭环引擎，regime→detect→diagnose→act→verify→self-heal 全链路自治",
        "src/zephyr/trading/feedback_loop/",
        now_iso,
        now_iso,
    ),
    (
        "D_ORCHESTRATOR",
        "agent_orchestrator",
        "foundation",
        "代理编排器——Agent全生命周期编排引擎，任务队列/调度/沙箱执行/幻觉检测/滚动升级",
        "src/zephyr/trading/orchestrator/",
        now_iso,
        now_iso,
    ),
]

conn = psycopg2.connect(**_build_pg_dsn())
conn.autocommit = False
try:
    with conn.cursor() as cur:
        for d in domains:
            cur.execute(INSERT_SQL, d)
            print(f"  INSERT domain: {d[0]} ({d[1]})")
    conn.commit()
    print(f"[OK] 成功插入 {len(domains)} 个域")
except Exception as e:
    conn.rollback()
    print(f"[ERROR] 插入失败: {e}")
    raise
finally:
    conn.close()
```

运行：
```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\_phase2_insert_domains.py
```

预期输出：
```
  INSERT domain: D_FEEDBACK_LOOP (feedback_loop_engine)
  INSERT domain: D_ORCHESTRATOR (agent_orchestrator)
[OK] 成功插入 2 个域
```

- [ ] **Step 2: 验证 DB INSERT 成功**

```powershell
python -c "import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance'); from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2; conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor(); cur.execute(\"SELECT domain_id, domain_name, ssot_path, layer_id, lifecycle, build_status FROM domains WHERE domain_id IN ('D_FEEDBACK_LOOP','D_ORCHESTRATOR') ORDER BY domain_id\"); [print(r) for r in cur.fetchall()]; conn.close()"
```

预期输出：
```
('D_FEEDBACK_LOOP', 'feedback_loop_engine', 'src/zephyr/trading/feedback_loop/', 'L1_foundation', 'operational', 'stable')
('D_ORCHESTRATOR', 'agent_orchestrator', 'src/zephyr/trading/orchestrator/', 'L1_foundation', 'operational', 'stable')
```

- [ ] **Step 3: 在 functional_domain_registry.yaml 中添加 2 个域条目**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml`

在文件末尾（最后一个 entry `- domain: D_GOV_RULE` 之后）追加：

```yaml
- domain: D_FEEDBACK_LOOP
  subdomain: feedback_loop_engine
  ssot_module: MOD-FEEDBACK_LOOP
  ssot_path: src/zephyr/trading/feedback_loop/
  covers:
  - 反馈收集器(collectors)
  - 反馈检测器(detectors)
  - 反馈诊断器(diagnosers)
  - 反馈执行器(actors)
  - SLO管理(slo_manager)
  - 错误预算(error_budget)
  - 评估线束(eval_harness)
  - 自动进化(auto_evolution)
  - 自适应学习循环(adaptive_learning)
  - 规则自优化(rule_optimizer)
  - 策略进化(policy_evolution)
  - 知识沉淀(knowledge_crystallizer)
  aliases:
  - feedback loop
  - 反馈环
  - feedback
  - 反馈
  - SLO
  - error budget
  - self evolution
  - 自进化
  - auto evolution
  - 自适应
  - adaptive learning
  - policy evolution
  - FLE
  stability: evolving
  ai_autonomy: ai_modifiable
- domain: D_ORCHESTRATOR
  subdomain: agent_orchestrator
  ssot_module: MOD-INF-039
  ssot_path: src/zephyr/trading/orchestrator/
  covers:
  - Agent全生命周期编排
  - 任务队列(task_queue)
  - Agent调度(agent_orchestrator)
  - 沙箱执行(script_runner)
  - 幻觉检测(hallucination_detector)
  - 滚动升级(rolling_upgrade)
  - 状态同步(state_synchronizer)
  - 故障恢复(rollback_manager)
  - 会话管理(session_manager)
  aliases:
  - orchestrator
  - 编排器
  - agent orchestrator
  - task queue
  - 任务队列
  - hallucination detection
  - 幻觉检测
  stability: evolving
  ai_autonomy: ai_modifiable
```

- [ ] **Step 4: 在 domain_name_mapping.py 中添加 3 个字典条目**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\scripts\governance\d5_architecture\generators\domain_name_mapping.py`

**4a. 在 `DOMAIN_NAME_ZH` 字典中（L1 基础平台层区块，`"D_OPS": "反馈循环",` 之后）添加：**

```python
    "D_FEEDBACK_LOOP": "反馈循环引擎",
    "D_ORCHESTRATOR": "代理编排器",
```

具体操作：在 `DOMAIN_NAME_ZH` 字典中找到 `"D_OPS": "反馈循环",` 行，在其后插入上述 2 行。

**4b. 在 `DOMAIN_NAME_EN` 字典中（`"D_OPS": "Feedback Loop",` 之后）添加：**

```python
    "D_FEEDBACK_LOOP": "Feedback Loop Engine",
    "D_ORCHESTRATOR": "Agent Orchestrator",
```

**4c. 在 `DOMAIN_DESC_ZH` 字典中（`"D_OPS": "反馈循环，负责系统运行反馈、性能监控和自动调优闭环",` 之后）添加：**

```python
    "D_FEEDBACK_LOOP": "反馈循环引擎，负责系统自我改进闭环：异常检测、根因诊断、自动修复和自我进化",
    "D_ORCHESTRATOR": "代理编排器，负责 Agent 任务全生命周期：任务入队、调度、沙箱执行、幻觉检测和收尾归档",
```

- [ ] **Step 5: 在 target_layer_vocabulary.yaml 中添加 2 个词表值**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\docs\01_policies_and_standards\_registry\vocabularies\target_layer_vocabulary.yaml`

**5a. 将 `total_values: 38` 改为 `total_values: 40`**

```yaml
total_values: 40
```

**5b. 在 `values:` 列表中（`- value: D_OPS` 条目之后）添加 2 个新值：**

```yaml
  - value: D_FEEDBACK_LOOP
    definition: "反馈循环引擎域——自我改进闭环/异常检测/根因诊断/自动进化"
    is_foundation: false
    ai_keywords: ["反馈循环", "feedback loop", "fle", "self-improvement"]
  - value: D_ORCHESTRATOR
    definition: "代理编排器域——Agent全生命周期编排/任务队列/沙箱执行/幻觉检测"
    is_foundation: false
    ai_keywords: ["编排器", "orchestrator", "agent orchestrator", "task queue"]
```

- [ ] **Step 6: 运行 sync_yaml_to_depgraph.py 将注册表同步到 DB**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d8_doc_sync\sync_yaml_to_depgraph.py
```

预期输出（关键行）：
```
同步 #156: 功能域注册表 → domains + arch_path_mappings...
  同步 ... 个功能域（含 modification_permission 字段映射），跳过 0 个非规范域ID，去重 ... 个重复域
同步 #157: 词汇表 → field_vocabularies...
  同步 ... 个词汇值
[PASS] 28 项 YAML→DB 同步完成
```

- [ ] **Step 7: 验证 architecture_model/index.yaml 已由 reconciler 自动更新**

```powershell
python -c "import yaml; data = yaml.safe_load(open(r'd:\ZephyrAlpha\.worktrees\phase2-d-trading-split\architecture_model\index.yaml', encoding='utf-8')); domains = [d for d in data['domains'] if d['id'] in ('D_FEEDBACK_LOOP','D_ORCHESTRATOR')]; [print(d) for d in domains]; print(f'共找到 {len(domains)} 个新域')"
```

预期输出：
```
{'id': 'D_FEEDBACK_LOOP', 'name': 'feedback_loop_engine', 'layer_id': 'L1_foundation'}
{'id': 'D_ORCHESTRATOR', 'name': 'agent_orchestrator', 'layer_id': 'L1_foundation'}
共找到 2 个新域
```

> 若 index.yaml 未自动更新，手动在 `domains:` 列表中（按字母序，D_FEEDBACK_LOOP 在 D_FUNDAMENTAL_SIGNAL 之后、D_GOVERNANCE 之前；D_ORCHESTRATOR 在 D_MKT_DATA 之后、D_OPS 之前）添加：
> ```yaml
> - id: D_FEEDBACK_LOOP
>   name: feedback_loop_engine
>   layer_id: L1_foundation
> - id: D_ORCHESTRATOR
>   name: agent_orchestrator
>   layer_id: L1_foundation
> ```

- [ ] **Step 8: session_worktree 提交**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python scripts\governance\session_worktree.py commit --session phase2-d-trading-split --message "OPS-2026071210: 新建 D_FEEDBACK_LOOP + D_ORCHESTRATOR 域定义（5处真源）"
```

预期输出：
```
[OK] session_worktree 提交成功
```

---

## Task 3: OPS-2026071211 — 迁移 D_TRADING depgraph 节点（2批 SQL UPDATE by path prefix）

**依赖**：OPS-2026071210（Task 2 完成）
**目标**：将 D_TRADING 中 feedback_loop 和 orchestrator 路径下的节点迁移到新域

- [ ] **Step 1: 迁移前统计（按路径 + design_maturity 分组）**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor()
cur.execute(\"\"\"
SELECT domain_id, design_maturity, COUNT(*) as cnt
FROM nodes
WHERE domain_id = 'D_TRADING'
  AND (path LIKE 'src/zephyr/trading/feedback_loop/%' OR path LIKE 'src/zephyr/trading/orchestrator/%')
GROUP BY domain_id, design_maturity
ORDER BY design_maturity
\"\"\")
print('=== 迁移前统计（D_TRADING 中 feedback_loop + orchestrator 路径）===')
for r in cur.fetchall(): print(f'  {r[1]}: {r[2]} 节点')
cur.execute(\"SELECT COUNT(*) FROM nodes WHERE domain_id='D_TRADING' AND path LIKE 'src/zephyr/trading/feedback_loop/%'\")
print(f'feedback_loop 路径总计: {cur.fetchone()[0]} 节点')
cur.execute(\"SELECT COUNT(*) FROM nodes WHERE domain_id='D_TRADING' AND path LIKE 'src/zephyr/trading/orchestrator/%'\")
print(f'orchestrator 路径总计: {cur.fetchone()[0]} 节点')
conn.close()
"
```

预期输出：
```
=== 迁移前统计（D_TRADING 中 feedback_loop + orchestrator 路径）===
  production: ~237 节点
  design: ~... 节点
  prototype: ~... 节点
feedback_loop 路径总计: ~336 节点
orchestrator 路径总计: ~74 节点
```

- [ ] **Step 2: 备份 depgraph DB**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import backup_before_migration
from pathlib import Path
backup_path = Path(r'd:\ZephyrAlpha\.worktrees\phase2-d-trading-split\.backups\depgraph_pre_phase2_split.dump')
backup_path.parent.mkdir(parents=True, exist_ok=True)
result = backup_before_migration(backup_path)
print(f'[OK] DB 备份完成: {result}')
"
```

预期输出：
```
[OK] DB 备份完成: d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\.backups\depgraph_pre_phase2_split.dump
```

- [ ] **Step 3: 执行 Batch 1 SQL UPDATE — feedback_loop → D_FEEDBACK_LOOP**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
conn = psycopg2.connect(**_build_pg_dsn()); conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            UPDATE nodes
            SET domain_id = 'D_FEEDBACK_LOOP'
            WHERE path LIKE 'src/zephyr/trading/feedback_loop/%'
              AND domain_id = 'D_TRADING'
        \"\"\")
        moved = cur.rowcount
    conn.commit()
    print(f'[OK] Batch 1: {moved} 节点从 D_TRADING 迁移到 D_FEEDBACK_LOOP')
except Exception as e:
    conn.rollback()
    print(f'[ERROR] Batch 1 失败: {e}'); raise
finally:
    conn.close()
"
```

预期输出：
```
[OK] Batch 1: ~336 节点从 D_TRADING 迁移到 D_FEEDBACK_LOOP
```

- [ ] **Step 4: 执行 Batch 2 SQL UPDATE — orchestrator → D_ORCHESTRATOR**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
conn = psycopg2.connect(**_build_pg_dsn()); conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            UPDATE nodes
            SET domain_id = 'D_ORCHESTRATOR'
            WHERE path LIKE 'src/zephyr/trading/orchestrator/%'
              AND domain_id = 'D_TRADING'
        \"\"\")
        moved = cur.rowcount
    conn.commit()
    print(f'[OK] Batch 2: {moved} 节点从 D_TRADING 迁移到 D_ORCHESTRATOR')
except Exception as e:
    conn.rollback()
    print(f'[ERROR] Batch 2 失败: {e}'); raise
finally:
    conn.close()
"
```

预期输出：
```
[OK] Batch 2: ~74 节点从 D_TRADING 迁移到 D_ORCHESTRATOR
```

- [ ] **Step 5: 更新 domains 表 production_nodes 缓存列**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
conn = psycopg2.connect(**_build_pg_dsn()); conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute(\"\"\"
            UPDATE domains SET production_nodes = (
                SELECT COUNT(*) FROM nodes
                WHERE domain_id = domains.domain_id
                  AND design_maturity = 'production'
            )
            WHERE domain_id IN ('D_TRADING', 'D_FEEDBACK_LOOP', 'D_ORCHESTRATOR')
        \"\"\")
        updated = cur.rowcount
    conn.commit()
    print(f'[OK] 更新 {updated} 个域的 production_nodes 缓存')
except Exception as e:
    conn.rollback()
    print(f'[ERROR] 缓存更新失败: {e}'); raise
finally:
    conn.close()
"
```

预期输出：
```
[OK] 更新 3 个域的 production_nodes 缓存
```

- [ ] **Step 6: 迁移后验证（ARCH-CAP-002 合规检查）**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor()
cur.execute(\"SELECT domain_id, production_nodes FROM domains WHERE domain_id IN ('D_TRADING','D_FEEDBACK_LOOP','D_ORCHESTRATOR') ORDER BY domain_id\")
print('=== 迁移后 production_nodes ===')
for r in cur.fetchall():
    status = '✅ PASS' if r[1] <= 150 else '❌ FAIL (ARCH-CAP-002)'
    print(f'  {r[0]}: {r[1]} production nodes {status}')
cur.execute(\"SELECT COUNT(*) FROM nodes WHERE domain_id='D_TRADING'\")
print(f'D_TRADING 总节点数（含 design/prototype）: {cur.fetchone()[0]}')
conn.close()
"
```

预期输出：
```
=== 迁移后 production_nodes ===
  D_FEEDBACK_LOOP: ~177 production nodes ❌ FAIL (ARCH-CAP-002)
  D_ORCHESTRATOR: ~60 production nodes ✅ PASS
  D_TRADING: ~43 production nodes ✅ PASS
D_TRADING 总节点数（含 design/prototype）: ~...
```

> **注意**：D_FEEDBACK_LOOP 仍超限（~177 > 150），这是已知遗留（二期二分：D_FLE_DETECT + D_FLE_CORE），本次不处理。D_TRADING 和 D_ORCHESTRATOR 均已合规。

- [ ] **Step 7: session_worktree 提交**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python scripts\governance\session_worktree.py commit --session phase2-d-trading-split --message "OPS-2026071211: 迁移 D_TRADING depgraph 节点（feedback_loop→D_FEEDBACK_LOOP, orchestrator→D_ORCHESTRATOR）"
```

---

## Task 4: OPS-2026071212 — 同步 D_TRADING 代码表头（175 个文件）

**依赖**：OPS-2026071211（Task 3 完成）
**目标**：将 feedback_loop/ 和 orchestrator/ 目录下所有 .py 文件的 `# [DOMAIN] D_*` 表头替换为新域

- [ ] **Step 1: 预扫描 feedback_loop 目录当前表头分布**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python -c "
from pathlib import Path
import re, collections
target = Path(r'src\zephyr\trading\feedback_loop')
pattern = re.compile(r'^# \[DOMAIN\] (D_[A-Z_]+)', re.MULTILINE)
counts = collections.Counter()
total = 0
for f in target.rglob('*.py'):
    content = f.read_text(encoding='utf-8')
    m = pattern.search(content)
    if m:
        counts[m.group(1)] += 1
        total += 1
print(f'=== feedback_loop 目录表头分布（共 {total} 个 .py 文件有 DOMAIN 表头）===')
for domain, cnt in counts.most_common():
    print(f'  {domain}: {cnt} 文件')
"
```

预期输出（类似）：
```
=== feedback_loop 目录表头分布（共 ~100 个 .py 文件有 DOMAIN 表头）===
  D_OPS: ~5 文件
  D_INFRA_RUNTIME: ~1 文件
  ...
```

- [ ] **Step 2: 批量替换 feedback_loop 目录表头为 D_FEEDBACK_LOOP**

创建并运行替换脚本：

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python -c "
from pathlib import Path
import re
target = Path(r'src\zephyr\trading\feedback_loop')
new_domain = 'D_FEEDBACK_LOOP'
pattern = re.compile(r'^# \[DOMAIN\] D_[A-Z_]+', re.MULTILINE)
updated = 0
for py_file in target.rglob('*.py'):
    content = py_file.read_text(encoding='utf-8')
    if pattern.search(content):
        new_content = pattern.sub(f'# [DOMAIN] {new_domain}', content)
        py_file.write_text(new_content, encoding='utf-8')
        updated += 1
print(f'[OK] feedback_loop: 已更新 {updated} 个文件的表头为 {new_domain}')
"
```

预期输出：
```
[OK] feedback_loop: 已更新 ~100 个文件的表头为 D_FEEDBACK_LOOP
```

- [ ] **Step 3: 验证 feedback_loop 目录无残留旧表头**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python -c "
from pathlib import Path
import re
target = Path(r'src\zephyr\trading\feedback_loop')
pattern = re.compile(r'^# \[DOMAIN\] (D_[A-Z_]+)', re.MULTILINE)
non_match = []
for py_file in target.rglob('*.py'):
    content = py_file.read_text(encoding='utf-8')
    m = pattern.search(content)
    if m and m.group(1) != 'D_FEEDBACK_LOOP':
        non_match.append((str(py_file), m.group(1)))
if non_match:
    print(f'[FAIL] 发现 {len(non_match)} 个文件表头不是 D_FEEDBACK_LOOP:')
    for p, d in non_match: print(f'  {p}: {d}')
else:
    print('[PASS] feedback_loop 目录所有文件表头已统一为 D_FEEDBACK_LOOP')
"
```

预期输出：
```
[PASS] feedback_loop 目录所有文件表头已统一为 D_FEEDBACK_LOOP
```

- [ ] **Step 4: 预扫描 orchestrator 目录当前表头分布**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python -c "
from pathlib import Path
import re, collections
target = Path(r'src\zephyr\trading\orchestrator')
pattern = re.compile(r'^# \[DOMAIN\] (D_[A-Z_]+)', re.MULTILINE)
counts = collections.Counter()
total = 0
for f in target.rglob('*.py'):
    content = f.read_text(encoding='utf-8')
    m = pattern.search(content)
    if m:
        counts[m.group(1)] += 1
        total += 1
print(f'=== orchestrator 目录表头分布（共 {total} 个 .py 文件有 DOMAIN 表头）===')
for domain, cnt in counts.most_common():
    print(f'  {domain}: {cnt} 文件')
"
```

预期输出（类似）：
```
=== orchestrator 目录表头分布（共 ~68 个 .py 文件有 DOMAIN 表头）===
  D_INFRA_RUNTIME: ~68 文件
```

- [ ] **Step 5: 批量替换 orchestrator 目录表头为 D_ORCHESTRATOR**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python -c "
from pathlib import Path
import re
target = Path(r'src\zephyr\trading\orchestrator')
new_domain = 'D_ORCHESTRATOR'
pattern = re.compile(r'^# \[DOMAIN\] D_[A-Z_]+', re.MULTILINE)
updated = 0
for py_file in target.rglob('*.py'):
    content = py_file.read_text(encoding='utf-8')
    if pattern.search(content):
        new_content = pattern.sub(f'# [DOMAIN] {new_domain}', content)
        py_file.write_text(new_content, encoding='utf-8')
        updated += 1
print(f'[OK] orchestrator: 已更新 {updated} 个文件的表头为 {new_domain}')
"
```

预期输出：
```
[OK] orchestrator: 已更新 ~68 个文件的表头为 D_ORCHESTRATOR
```

- [ ] **Step 6: 验证 orchestrator 目录无残留旧表头**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python -c "
from pathlib import Path
import re
target = Path(r'src\zephyr\trading\orchestrator')
pattern = re.compile(r'^# \[DOMAIN\] (D_[A-Z_]+)', re.MULTILINE)
non_match = []
for py_file in target.rglob('*.py'):
    content = py_file.read_text(encoding='utf-8')
    m = pattern.search(content)
    if m and m.group(1) != 'D_ORCHESTRATOR':
        non_match.append((str(py_file), m.group(1)))
if non_match:
    print(f'[FAIL] 发现 {len(non_match)} 个文件表头不是 D_ORCHESTRATOR:')
    for p, d in non_match: print(f'  {p}: {d}')
else:
    print('[PASS] orchestrator 目录所有文件表头已统一为 D_ORCHESTRATOR')
"
```

预期输出：
```
[PASS] orchestrator 目录所有文件表头已统一为 D_ORCHESTRATOR
```

- [ ] **Step 7: session_worktree 提交**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python scripts\governance\session_worktree.py commit --session phase2-d-trading-split --message "OPS-2026071212: 同步 D_TRADING 代码表头（feedback_loop→D_FEEDBACK_LOOP ~100文件, orchestrator→D_ORCHESTRATOR ~68文件）"
```

---

## Task 5: OPS-2026071213 — 同步 D_TRADING 蓝图+文档+注册表（~15 个文件）

**依赖**：OPS-2026071211（Task 3 完成）
**目标**：同步蓝图 frontmatter、架构文档、注册表、脚本中的域引用

- [ ] **Step 1: 更新 feedback_loop 蓝图 responsibility_domain**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\docs\03_modules\_cross_layer\feedback_loop\blueprint.md`

将第 48 行：
```yaml
responsibility_domain: 
```
改为：
```yaml
responsibility_domain: D_FEEDBACK_LOOP
```

> 精确操作：搜索 `responsibility_domain: ` （注意末尾无值，有空格），替换为 `responsibility_domain: D_FEEDBACK_LOOP`

- [ ] **Step 2: 更新 agent_orchestrator 蓝图 responsibility_domain**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\docs\03_modules\_cross_layer\agent_orchestrator\blueprint.md`

将第 34 行：
```yaml
responsibility_domain: 
```
改为：
```yaml
responsibility_domain: D_ORCHESTRATOR
```

- [ ] **Step 3: 更新 architecture_issue_registry.yaml 中 #ARCH-052 条目**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\docs\01_policies_and_standards\_registry\catalogs\architecture_issue_registry.yaml`

找到 `#ARCH-052` 条目（约第 1432 行），在 `last_updated: '2026-07-06'` 之后添加备注行：

```yaml
  last_updated: '2026-07-12'
  notes: |
    2026-07-12 更新：D_TRADING 超限通过域拆分解决（Phase 2）。
    feedback_loop → D_FEEDBACK_LOOP（~177 production，仍超限待二期二分），
    orchestrator → D_ORCHESTRATOR（~60 production，已合规），
    D_TRADING 降至 ~43 production（已合规）。
    与聚合节点模式（ARCH-052 原方案）互补，先拆分跨层基础设施子系统。
```

同时将原 `last_updated: '2026-07-06'` 更新为 `last_updated: '2026-07-12'`。

- [ ] **Step 4: 审查 sync_yaml_to_depgraph.py 中 CTR-005→D_TRADING 映射**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\scripts\governance\d8_doc_sync\sync_yaml_to_depgraph.py`

查看第 156-167 行的 `_CTR_CONSUMER_FALLBACK` 字典：

```python
_CTR_CONSUMER_FALLBACK = {
    "CTR-001": "D_FACTOR", "CTR-TRACE-001": "D_FACTOR",
    "CTR-004": "D_EX_CORE", "CTR-005": "D_TRADING", "CTR-006": "D_RISK",
    ...
}
```

**审查结论**：`CTR-005` 是交易执行层的跨层契约，其 consumer_domain 回退为 `D_TRADING`。此映射保持不变——CTR-005 关联的是真正的交易运营（订单执行/交易会话），而非 feedback_loop/orchestrator 基础设施。D_TRADING 域仍然存在（只是节点减少了），FK 约束不会违规。

**无需修改此文件**。在 Step 7 提交说明中记录审查结论。

- [ ] **Step 5: 更新 generate_capability_heatmap.py 的 CAPABILITY_DOMAINS 硬编码列表**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\scripts\governance\d5_architecture\generators\generate_capability_heatmap.py`

在 `CAPABILITY_DOMAINS` 列表（第 65 行起）中，找到 `CC3`（基础设施）能力域定义（约第 137 行）：

```python
    {
        "id": "CC3",
        "name": "基础设施",
        "name_en": "Infrastructure",
        "type": "横切",
        "domains": [
            "D_INFRA_OPS",
            "D_INFRA_RUNTIME",
            "D_INTEGRATION",
            "D_INTEGRATION_GATEWAY",
            "D_SHARED",
            "D_FRONTEND",
            "D_REPORTING",
            "D_KNOWLEDGE",
            "D_INTELLIGENCE",
            "D_AUTONOMY_CORE",
            "D_OPS",
        ],
    },
```

在 `"D_OPS",` 之后添加 2 个新域：

```python
            "D_OPS",
            "D_FEEDBACK_LOOP",
            "D_ORCHESTRATOR",
```

> **理由**：D_FEEDBACK_LOOP 和 D_ORCHESTRATOR 是从 D_TRADING 拆出的跨层基础设施子系统，归入 CC3（基础设施）能力域最合适。D_TRADING 保留在 C5（执行交易）中。

- [ ] **Step 6: 审查 test_align_panoramas.py 中的 D_TRADING 引用**

文件：`d:\ZephyrAlpha\.worktrees\phase2-d-trading-split\tests\test_align_panoramas.py`

查看第 256、264、270 行——使用 `D_TRADING` 作为测试数据：

```python
_make_node("MOD-X", "depgraph", domain_id="D_TRADING"),
_make_node("MOD-X", "blueprint", domain_id="D_INFRA_RUNTIME"),
...
assert mismatches[0]["dataflow"] == "D_TRADING"
```

**审查结论**：这些是测试 fixture 中的示例 domain_id，用于测试域不匹配检测逻辑。D_TRADING 域仍然存在于 domains 表中（只是节点数减少），FK 不会违规。测试逻辑不依赖 D_TRADING 的节点数量。

**无需修改此文件**。在 Step 7 提交说明中记录审查结论。

- [ ] **Step 7: session_worktree 提交**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python scripts\governance\session_worktree.py commit --session phase2-d-trading-split --message "OPS-2026071213: 同步蓝图+文档+注册表（2蓝图responsibility_domain + #ARCH-052更新 + heatmap CC3增2域 + CTR-005审查通过 + test_align_panoramas审查通过）"
```

---

## Task 6: OPS-2026071214 — D_TRADING 验证：重生成 depgraph + ARCH-CAP-002 检查

**依赖**：OPS-2026071212（Task 4）和 OPS-2026071213（Task 5）均完成
**目标**：重生成 depgraph 后验证 ARCH-CAP-002 合规 + reconciler 全 clean

- [ ] **Step 1: 重生成 depgraph（从代码扫描）**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\generate_project_depgraph.py
```

预期输出（末尾）：
```
[OK] depgraph 生成完成，共 ... 节点
```

> 此步骤会重新扫描代码文件（包括已更新的表头），重写 nodes 表。新域节点（D_FEEDBACK_LOOP / D_ORCHESTRATOR）的 domain_id 会被生成器按路径前缀或表头自动分配。若生成器按路径前缀分配，结果应与 Task 3 的 SQL UPDATE 一致。

- [ ] **Step 2: 验证 D_TRADING 节点数已降至 ~43 production**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor()
for did in ('D_TRADING','D_FEEDBACK_LOOP','D_ORCHESTRATOR'):
    cur.execute('SELECT production_nodes FROM domains WHERE domain_id=%s', (did,))
    pn = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM nodes WHERE domain_id=%s AND design_maturity=%s', (did,'production'))
    actual = cur.fetchone()[0]
    status = '✅ PASS' if pn <= 150 else '❌ FAIL'
    print(f'{did}: production_nodes缓存={pn}, 实际production={actual} {status}')
conn.close()
"
```

预期输出：
```
D_TRADING: production_nodes缓存=~43, 实际production=~43 ✅ PASS
D_FEEDBACK_LOOP: production_nodes缓存=~177, 实际production=~177 ❌ FAIL（已知遗留，二期二分）
D_ORCHESTRATOR: production_nodes缓存=~60, 实际production=~60 ✅ PASS
```

- [ ] **Step 3: 运行 sync_yaml_to_depgraph.py 同步注册表**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d8_doc_sync\sync_yaml_to_depgraph.py
```

预期输出（末尾）：
```
[PASS] 28 项 YAML→DB 同步完成
```

- [ ] **Step 4: 运行 check_blueprint_code_alignment.py**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d5_architecture\checkers\check_blueprint_code_alignment.py
```

预期输出：无 ERROR / 无 domain mismatch（蓝图 responsibility_domain 与代码表头一致）。

> 若出现 mismatch，检查对应蓝图的 `responsibility_domain` 是否正确填写（Task 5 Step 1-2）。

- [ ] **Step 5: 运行 verify_schema_health.py**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d11_compliance\verify_schema_health.py
```

预期输出：schema healthy，无 drift。

- [ ] **Step 6: 验证 domains 表无 FK 违规**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor()
cur.execute(\"SELECT COUNT(*) FROM nodes n WHERE n.domain_id IS NOT NULL AND n.domain_id NOT IN (SELECT domain_id FROM domains)\")
orphans = cur.fetchone()[0]
print(f'FK 孤儿节点数（domain_id 不在 domains 表中）: {orphans}')
cur.execute(\"SELECT COUNT(*) FROM arch_directory_tree a WHERE a.domain_id IS NOT NULL AND a.domain_id NOT IN (SELECT domain_id FROM domains)\")
dir_orphans = cur.fetchone()[0]
print(f'arch_directory_tree FK 孤儿: {dir_orphans}')
if orphans == 0 and dir_orphans == 0:
    print('[PASS] 无 FK 违规')
else:
    print('[FAIL] 存在 FK 违规')
conn.close()
"
```

预期输出：
```
FK 孤儿节点数（domain_id 不在 domains 表中）: 0
arch_directory_tree FK 孤儿: 0
[PASS] 无 FK 违规
```

- [ ] **Step 7: session_worktree 提交**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python scripts\governance\session_worktree.py commit --session phase2-d-trading-split --message "OPS-2026071214: D_TRADING 验证通过（depgraph重生 + ARCH-CAP-002 D_TRADING~43✅ D_ORCHESTRATOR~60✅ + reconciler全clean + 无FK违规）"
```

---

## Task 7: OPS-2026071215 — D_TRADING 循环验证：全项目扫描遗漏 + 修复至问题 = 0

**依赖**：OPS-2026071214（Task 6 完成）
**目标**：连续 2 轮全项目扫描均 0 遗漏
**通过标准**：连续 2 轮扫描均 0 遗漏。若某轮发现问题，修复后重新计数。

### 第 1 轮验证

- [ ] **Step 1: Grep 扫描 feedback_loop/orchestrator 目录下 D_TRADING 残留引用**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python -c "
from pathlib import Path
import re
issues = []
for target_dir, expected_domain in [
    (Path(r'src\zephyr\trading\feedback_loop'), 'D_FEEDBACK_LOOP'),
    (Path(r'src\zephyr\trading\orchestrator'), 'D_ORCHESTRATOR'),
]:
    for py_file in target_dir.rglob('*.py'):
        content = py_file.read_text(encoding='utf-8')
        # 检查是否有 D_TRADING 残留
        if 'D_TRADING' in content:
            for i, line in enumerate(content.splitlines(), 1):
                if 'D_TRADING' in line:
                    issues.append(f'{py_file}:{i}: {line.strip()}')
if issues:
    print(f'[FAIL] 发现 {len(issues)} 处 D_TRADING 残留:')
    for iss in issues: print(f'  {iss}')
else:
    print('[PASS] feedback_loop/orchestrator 目录无 D_TRADING 残留引用')
"
```

预期输出：
```
[PASS] feedback_loop/orchestrator 目录无 D_TRADING 残留引用
```

- [ ] **Step 2: 验证代码表头与 depgraph domain_id 一致性**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn; import psycopg2
from pathlib import Path
import re
conn = psycopg2.connect(**_build_pg_dsn()); cur = conn.cursor()
header_pattern = re.compile(r'^# \[DOMAIN\] (D_[A-Z_]+)', re.MULTILINE)
issues = []
for target_dir, expected_domain in [
    (Path(r'src\zephyr\trading\feedback_loop'), 'D_FEEDBACK_LOOP'),
    (Path(r'src\zephyr\trading\orchestrator'), 'D_ORCHESTRATOR'),
]:
    for py_file in target_dir.rglob('*.py'):
        content = py_file.read_text(encoding='utf-8')
        m = header_pattern.search(content)
        if m and m.group(1) != expected_domain:
            issues.append(f'{py_file}: 表头={m.group(1)}, 期望={expected_domain}')
        # 检查 DB 中该节点 domain_id
        rel_path = str(py_file).replace('\\\\','/').split('src/')[1]
        rel_path = 'src/' + rel_path
        cur.execute('SELECT domain_id FROM nodes WHERE path=%s', (rel_path,))
        row = cur.fetchone()
        if row and row[0] != expected_domain:
            issues.append(f'DB {rel_path}: domain_id={row[0]}, 期望={expected_domain}')
if issues:
    print(f'[FAIL] 发现 {len(issues)} 处不一致:')
    for iss in issues: print(f'  {iss}')
else:
    print('[PASS] 代码表头与 depgraph domain_id 一致')
conn.close()
"
```

预期输出：
```
[PASS] 代码表头与 depgraph domain_id 一致
```

- [ ] **Step 3: 验证蓝图 frontmatter 与 depgraph 一致性**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import yaml
checks = [
    (r'docs\03_modules\_cross_layer\feedback_loop\blueprint.md', 'MOD-FEEDBACK_LOOP', 'D_FEEDBACK_LOOP'),
    (r'docs\03_modules\_cross_layer\agent_orchestrator\blueprint.md', 'MOD-INF-039', 'D_ORCHESTRATOR'),
]
issues = []
for path, blueprint_id, expected_domain in checks:
    with open(path, encoding='utf-8') as f:
        content = f.read()
    # 提取 frontmatter
    fm = content.split('---')[1]
    data = yaml.safe_load(fm)
    rd = data.get('responsibility_domain', '')
    if rd != expected_domain:
        issues.append(f'{path}: responsibility_domain={rd!r}, 期望={expected_domain}')
    else:
        print(f'  {path}: responsibility_domain={rd} ✅')
if issues:
    print(f'[FAIL] 发现 {len(issues)} 处蓝图不一致')
    for iss in issues: print(f'  {iss}')
else:
    print('[PASS] 蓝图 frontmatter responsibility_domain 一致')
"
```

预期输出：
```
  docs\03_modules\_cross_layer\feedback_loop\blueprint.md: responsibility_domain=D_FEEDBACK_LOOP ✅
  docs\03_modules\_cross_layer\agent_orchestrator\blueprint.md: responsibility_domain=D_ORCHESTRATOR ✅
[PASS] 蓝图 frontmatter responsibility_domain 一致
```

- [ ] **Step 4: 验证注册表/词表一致性**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import yaml
# 4a. functional_domain_registry.yaml
with open(r'docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml', encoding='utf-8') as f:
    reg = yaml.safe_load(f)
reg_domains = {e['domain'] for e in reg['entries']}
for d in ('D_FEEDBACK_LOOP', 'D_ORCHESTRATOR'):
    if d in reg_domains:
        print(f'  functional_domain_registry: {d} ✅')
    else:
        print(f'  functional_domain_registry: {d} ❌ 缺失')

# 4b. target_layer_vocabulary.yaml
with open(r'docs\01_policies_and_standards\_registry\vocabularies\target_layer_vocabulary.yaml', encoding='utf-8') as f:
    vocab = yaml.safe_load(f)
vocab_values = {v['value'] for v in vocab['values']}
for d in ('D_FEEDBACK_LOOP', 'D_ORCHESTRATOR'):
    if d in vocab_values:
        print(f'  target_layer_vocabulary: {d} ✅')
    else:
        print(f'  target_layer_vocabulary: {d} ❌ 缺失')
print(f'  total_values={vocab[\"total_values\"]} (期望=40)')

# 4c. domain_name_mapping.py
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from domain_name_mapping import DOMAIN_NAME_ZH, DOMAIN_NAME_EN, DOMAIN_DESC_ZH
for d in ('D_FEEDBACK_LOOP', 'D_ORCHESTRATOR'):
    in_zh = d in DOMAIN_NAME_ZH
    in_en = d in DOMAIN_NAME_EN
    in_desc = d in DOMAIN_DESC_ZH
    print(f'  domain_name_mapping: {d} ZH={in_zh} EN={in_en} DESC={in_desc}')
"
```

预期输出：
```
  functional_domain_registry: D_FEEDBACK_LOOP ✅
  functional_domain_registry: D_ORCHESTRATOR ✅
  target_layer_vocabulary: D_FEEDBACK_LOOP ✅
  target_layer_vocabulary: D_ORCHESTRATOR ✅
  total_values=40 (期望=40)
  domain_name_mapping: D_FEEDBACK_LOOP ZH=True EN=True DESC=True
  domain_name_mapping: D_ORCHESTRATOR ZH=True EN=True DESC=True
```

- [ ] **Step 5: 运行 check_blueprint_code_alignment.py**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d5_architecture\checkers\check_blueprint_code_alignment.py
```

预期输出：无 ERROR / 无 domain mismatch。

- [ ] **Step 6: 运行 verify_schema_health.py**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d11_compliance\verify_schema_health.py
```

预期输出：schema healthy，无 drift。

- [ ] **Step 7: 第 1 轮结论判定**

检查 Step 1-6 是否全部 PASS：
- **全部 PASS** → 标记第 1 轮通过，继续 Step 8 开始第 2 轮
- **有任何 FAIL** → 修复问题后，从 Step 1 重新开始第 1 轮（计数重置）

### 第 2 轮验证

- [ ] **Step 8: 重复 Step 1（Grep 扫描 D_TRADING 残留）**

运行与 Step 1 完全相同的命令，预期 `[PASS]`。

- [ ] **Step 9: 重复 Step 2（代码表头与 depgraph 一致性）**

运行与 Step 2 完全相同的命令，预期 `[PASS]`。

- [ ] **Step 10: 重复 Step 3（蓝图 frontmatter 一致性）**

运行与 Step 3 完全相同的命令，预期 `[PASS]`。

- [ ] **Step 11: 重复 Step 4（注册表/词表一致性）**

运行与 Step 4 完全相同的命令，预期全部 ✅。

- [ ] **Step 12: 重复 Step 5（check_blueprint_code_alignment.py）**

运行与 Step 5 完全相同的命令，预期无 ERROR。

- [ ] **Step 13: 重复 Step 6（verify_schema_health.py）**

运行与 Step 6 完全相同的命令，预期 schema healthy。

- [ ] **Step 14: 第 2 轮结论判定**

- **连续 2 轮全部 PASS** → 循环验证通过，继续 Step 15 合并
- **有任何 FAIL** → 修复后从 Step 1 重新开始（两轮计数均重置）

- [ ] **Step 15: session_worktree 合并**

```powershell
cd d:\ZephyrAlpha\.worktrees\phase2-d-trading-split
python scripts\governance\session_worktree.py merge --session phase2-d-trading-split
```

预期输出：
```
[OK] session_worktree 合并成功，变更已合并到主分支
```

- [ ] **Step 16: 最终提交确认**

```powershell
cd d:\ZephyrAlpha
git log --oneline -10
```

预期输出（应看到 Phase 2 的所有 commit）：
```
<hash> OPS-2026071215: D_TRADING 循环验证通过（连续2轮0遗漏）
<hash> OPS-2026071214: D_TRADING 验证通过（depgraph重生 + ARCH-CAP-002...）
<hash> OPS-2026071213: 同步蓝图+文档+注册表（...）
<hash> OPS-2026071212: 同步 D_TRADING 代码表头（...）
<hash> OPS-2026071211: 迁移 D_TRADING depgraph 节点（...）
<hash> OPS-2026071210: 新建 D_FEEDBACK_LOOP + D_ORCHESTRATOR 域定义（...）
...
```

---

## 回滚方案

### depgraph 节点迁移回滚

```sql
-- 将 D_FEEDBACK_LOOP 和 D_ORCHESTRATOR 的节点回滚到 D_TRADING
UPDATE nodes SET domain_id = 'D_TRADING'
WHERE domain_id IN ('D_FEEDBACK_LOOP', 'D_ORCHESTRATOR');

-- 更新 production_nodes 缓存
UPDATE domains SET production_nodes = (
    SELECT COUNT(*) FROM nodes
    WHERE domain_id = domains.domain_id
    AND design_maturity = 'production'
)
WHERE domain_id IN ('D_TRADING', 'D_FEEDBACK_LOOP', 'D_ORCHESTRATOR');
```

### 新建域回滚

```sql
DELETE FROM domains WHERE domain_id IN ('D_FEEDBACK_LOOP', 'D_ORCHESTRATOR');
```

### DB 备份恢复

```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys; sys.path.insert(0, r'd:\ZephyrAlpha\src'); sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import restore_from_backup
from pathlib import Path
restore_from_backup(Path(r'd:\ZephyrAlpha\.worktrees\phase2-d-trading-split\.backups\depgraph_pre_phase2_split.dump'))
print('[OK] DB 已从备份恢复')
"
```

### 文件变更回滚

```powershell
cd d:\ZephyrAlpha
git checkout -- src/zephyr/trading/feedback_loop/ src/zephyr/trading/orchestrator/ docs/03_modules/_cross_layer/feedback_loop/ docs/03_modules/_cross_layer/agent_orchestrator/ docs/01_policies_and_standards/_registry/ scripts/governance/d5_architecture/generators/domain_name_mapping.py scripts/governance/d5_architecture/generators/generate_capability_heatmap.py architecture_model/index.yaml
```

---

## 已知遗留（二期专项）

| 遗留项 | 说明 | 预期专项 |
|---|---|---|
| D_FEEDBACK_LOOP 仍超限 | ~177 production 节点 > 150 | 内部二分：D_FLE_DETECT（~141）+ D_FLE_CORE（~195 拆分后） |
| 代码物理路径未迁移 | feedback_loop/orchestrator 仍在 trading/ 目录下 | 物理迁移 src/zephyr/trading/feedback_loop/ → src/zephyr/feedback_loop/ + import 路径修改 |
| generate_capability_heatmap.py CC3 域列表 | 新增 2 域已加入 CC3，但 D_TRADING 仍在 C5（保留正确） | 无需后续操作 |
| #ARCH-052 聚合节点模式 | D_TRADING 已通过域拆分解决，其余 4 域仍需聚合节点模式 | Phase 2-4 继续 |
