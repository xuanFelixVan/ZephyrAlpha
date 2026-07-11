# D_GOVERNANCE 域拆分实施计划（Phase 1）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 D_GOVERNANCE 域 506 production 节点降至 ~306，通过完成空壳域节点迁移+同步所有引用

**Architecture:** depgraph SQL UPDATE 迁移节点 domain_id + 批量替换代码/脚本/测试表头 + 注册表/词表新增域定义 + 循环验证至0遗漏

**Tech Stack:** PostgreSQL (depgraph), Python (psycopg2), PowerShell, session_worktree

---

## 全局上下文（所有 Task 共享）

### 环境变量
- `PYTHONPATH` = `d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance`
- 工作目录 = `d:\ZephyrAlpha`

### depgraph 连接方式
```python
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\src")
sys.path.insert(0, r"d:\ZephyrAlpha\scripts\governance")
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
```

### 关键表结构
- `nodes` 表：`domain_id`、`subdomain_id`、`design_maturity`（值 production/prototype/design）、`build_status`（值 generated/stable/planned/testing/deprecated）
- `domains` 表：`domain_id`（PK）、`domain_name`、`domain_group`、`ssot_path`、`lifecycle`、`build_status`、`layer_id`、`production_nodes`（缓存列）
- 所有表在 `public` schema 下

### D_GOVERNANCE 迁移映射
| subdomain_id | 目标域 | 代码目录 | 表头新值 |
|---|---|---|---|
| D_GOVERNANCE-AUDIT_TRAIL | D_GOV_AUDIT | audit_trail/, audit/, semantic_audit/ | `# [DOMAIN] D_GOV_AUDIT` |
| D_GOVERNANCE-DRIFT_DETECTION | D_GOV_DRIFT | drift_detector_core/ | `# [DOMAIN] D_GOV_DRIFT` |
| D_GOVERNANCE-RULE_ENFORCEMENT | D_GOV_ENFORCEMENT | commit_gates/, rule_enforcement/, rule_bridge/, behavioral_admission/ | `# [DOMAIN] D_GOV_ENFORCEMENT` |
| D_GOVERNANCE-KB | D_GOV_KB（新建） | kb/ | `# [DOMAIN] D_GOV_KB` |
| D_GOVERNANCE-SCRIPT_GOVERNANCE | D_GOV_SCRIPTS | scripts/ | `# [DOMAIN] D_GOV_SCRIPTS` |

### session_worktree 工作流
```
session_worktree_start(sid) → 编辑文件 → session_worktree_commit(sid, files, msg) → session_worktree_merge(sid)
```

---

## Task 1: OPS-2026071201 — D_GOVERNANCE 域拆分总卡（depgraph映射阶段）

**Files:**
- Create: `docs/_working/phase1_baseline.md`
- Backup: `tmp/depgraph_backup_phase1.dump`

- [ ] **Step 1: 启动 session_worktree**

Run（PowerShell，工作目录 `d:\ZephyrAlpha`）:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.rule_bridge.session_worktree import session_worktree_start, generate_session_id
sid = generate_session_id()
r = session_worktree_start(sid, breaking_change=True)
print('SESSION_ID=' + r['session_id'])
print('WORKTREE_PATH=' + r['worktree_path'])
print('BRANCH=' + r['branch'])
print('CREATED=' + str(r['created']))
"
```

Expected output:
```
SESSION_ID=sess-XXXXX-YYYYMMDDHHMMSS
WORKTREE_PATH=d:\ZephyrAlpha\.aidrafts\sess-XXXXX-YYYYMMDDHHMMSS
BRANCH=session/sess-XXXXX-YYYYMMDDHHMMSS
CREATED=True
```

记录 `SESSION_ID` 和 `WORKTREE_PATH` 供后续所有 Task 使用。后续命令中用 `$SID` 和 `$WT` 替代：
```powershell
$SID = "sess-XXXXX-YYYYMMDDHHMMSS"  # 替换为实际值
$WT = "d:\ZephyrAlpha\.aidrafts\$SID"
```

- [ ] **Step 2: 备份 depgraph DB（pg_dump）**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.depgraph_schema import backup_before_migration
from pathlib import Path
p = backup_before_migration(Path(r'd:\ZephyrAlpha\tmp\depgraph_backup_phase1.dump'))
print('BACKUP_OK=' + str(p))
"
```

Expected output:
```
BACKUP_OK=d:\ZephyrAlpha\tmp\depgraph_backup_phase1.dump
```

- [ ] **Step 3: 查询基线 — D_GOVERNANCE 当前 production_nodes**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"SELECT domain_id, domain_name, production_nodes FROM domains WHERE domain_id = 'D_GOVERNANCE'\"\"\")
print('DOMAIN:', cur.fetchone())
cur.execute(\"\"\"SELECT COUNT(*) FROM nodes WHERE domain_id = 'D_GOVERNANCE' AND design_maturity = 'production'\"\"\")
print('ACTUAL_PRODUCTION_NODES:', cur.fetchone()[0])
cur.execute(\"\"\"SELECT subdomain_id, COUNT(*) FROM nodes WHERE domain_id = 'D_GOVERNANCE' AND design_maturity = 'production' GROUP BY subdomain_id ORDER BY 2 DESC\"\"\")
for row in cur.fetchall():
    print('  SUBDOMAIN:', row)
conn.close()
"
```

Expected output（节点的 production_nodes 缓存列可能滞后，以 ACTUAL_PRODUCTION_NODES 为准）:
```
DOMAIN: ('D_GOVERNANCE', 'registry_management', 506)
ACTUAL_PRODUCTION_NODES: 506
  SUBDOMAIN: ('D_GOVERNANCE-RULE_ENFORCEMENT', 62)
  SUBDOMAIN: ('D_GOVERNANCE-AUDIT_TRAIL', 56)
  SUBDOMAIN: ('D_GOVERNANCE-DRIFT_DETECTION', 56)
  SUBDOMAIN: ('D_GOVERNANCE-KB', 22)
  SUBDOMAIN: ('D_GOVERNANCE-SCRIPT_GOVERNANCE', 4)
  ...（其余 subdomain_id 为 NULL 或其他值）
```

- [ ] **Step 4: 创建基线记录文件**

File: `docs/_working/phase1_baseline.md`

Content:
```markdown
# Phase 1 D_GOVERNANCE 域拆分基线

**记录时间**: 2026-07-12
**Session ID**: <填入 Step 1 实际值>
**DB 备份**: tmp/depgraph_backup_phase1.dump

## 基线数据（来自 Step 3）
- D_GOVERNANCE production_nodes 缓存列: 506
- D_GOVERNANCE 实际 production 节点: 506
- 各 subdomain 节点分布: 见 Step 3 输出

## 预期迁移后
- D_GOVERNANCE: 506 - 200 = ~306 production 节点
- D_GOV_AUDIT: +56
- D_GOV_DRIFT: +56
- D_GOV_ENFORCEMENT: +62
- D_GOV_KB: +22（新建）
- D_GOV_SCRIPTS: +4
```

将 `<填入 Step 1 实际值>` 替换为 Step 1 输出的 `SESSION_ID`。

---

## Task 2: OPS-2026071203 — 新建 D_GOV_KB 域定义（5处）

**Depends on:** Task 1

**Files:**
- Modify: depgraph DB `domains` 表（INSERT）
- Modify: `architecture_model/index.yaml`
- Modify: `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`
- Modify: `scripts/governance/d5_architecture/generators/domain_name_mapping.py`
- Modify: `docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml`

- [ ] **Step 1: depgraph DB domains 表 INSERT D_GOV_KB**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
INSERT INTO domains (
    domain_id, domain_name, domain_group, description,
    ssot_path, current_modules, max_modules, lifecycle,
    created_at, updated_at, build_status, modification_permission,
    layer_id, target_modules, production_nodes
) VALUES (
    'D_GOV_KB',
    'knowledge_base_governance',
    'governance',
    '知识库治理域——KB 管线/知识引擎/向量记忆后端（MOD-KB-001 拆分自 D_GOVERNANCE）',
    'src/zephyr/governance/kb/',
    0, 150, 'operational',
    '2026-07-12', '2026-07-12', 'stable', 'ai_modifiable',
    'L2_domain', 60, 0
)
ON CONFLICT (domain_id) DO NOTHING
\"\"\")
conn.commit()
cur.execute(\"SELECT domain_id, domain_name, layer_id, lifecycle FROM domains WHERE domain_id = 'D_GOV_KB'\")
print('INSERTED:', cur.fetchone())
conn.close()
"
```

Expected output:
```
INSERTED: ('D_GOV_KB', 'knowledge_base_governance', 'L2_domain', 'operational')
```

- [ ] **Step 2: architecture_model/index.yaml 新增 D_GOV_KB 条目**

File: `d:\ZephyrAlpha\architecture_model\index.yaml`

定位 L201-203（D_GOV_ENFORCEMENT 条目之后，D_GOV_REPAIR 条目之前）:
```yaml
- id: D_GOV_ENFORCEMENT
  name: rule_enforcement
  layer_id: L2_domain
- id: D_GOV_REPAIR
  name: rollback
  layer_id: L2_domain
```

用 Edit 工具将 `old_string`:
```
- id: D_GOV_ENFORCEMENT
  name: rule_enforcement
  layer_id: L2_domain
- id: D_GOV_REPAIR
```
替换为 `new_string`:
```
- id: D_GOV_ENFORCEMENT
  name: rule_enforcement
  layer_id: L2_domain
- id: D_GOV_KB
  name: knowledge_base_governance
  layer_id: L2_domain
- id: D_GOV_REPAIR
```

验证（Grep）:
```
pattern: "^- id: D_GOV_KB$"
path: d:\ZephyrAlpha\architecture_model\index.yaml
```
Expected: 1 match.

- [ ] **Step 3: functional_domain_registry.yaml 新增 D_GOV_KB 条目**

File: `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml`

定位 D_GOV_DRIFT 条目末尾（约 L118，`ai_autonomy: human_gated` 之后），在 `D_GOVERNANCE` 条目（约 L119）之前插入。

用 Edit 工具将 `old_string`（D_GOV_DRIFT 条目末尾 + 空行 + D_GOVERNANCE 条目开头）:
```yaml
  stability: stable
  ai_autonomy: human_gated
- domain: D_GOVERNANCE
  subdomain: registry_management
```
替换为 `new_string`:
```yaml
  stability: stable
  ai_autonomy: human_gated
- domain: D_GOV_KB
  subdomain: knowledge_base_governance
  ssot_module: MOD-KB-001
  ssot_path: src/zephyr/governance/kb/
  covers:
  - 知识管线(ingest/triage/extract/activate/analyze)
  - 知识仓库(kb_repo)
  - 统一记忆API(unified_memory_api)
  - 知识完整性(integrity)
  - 重排序(reranker)
  - 安全制动(safety_brake)
  - VMS记忆后端(vms_memory_backend)
  - 知识引擎(knowledge_engine)
  - 知识蒸馏(knowledge_distiller)
  - 嵌入版本锁(embedding_version_lock)
  aliases:
  - knowledge base governance
  - 知识库治理
  - KB governance
  stability: stable
  ai_autonomy: ai_modifiable
- domain: D_GOVERNANCE
  subdomain: registry_management
```

注意：上述 `old_string` 必须唯一匹配。D_GOV_DRIFT 条目末尾的 `ai_autonomy: human_gated` 在文件中出现多次，但 `ai_autonomy: human_gated\n- domain: D_GOVERNANCE\n  subdomain: registry_management` 组合是唯一的。

验证（Grep）:
```
pattern: "^- domain: D_GOV_KB$"
path: d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml
```
Expected: 1 match.

- [ ] **Step 4: domain_name_mapping.py 新增 D_GOV_KB 映射**

File: `d:\ZephyrAlpha\scripts\governance\d5_architecture\generators\domain_name_mapping.py`

需在 3 个字典中新增 D_GOV_KB 条目：`DOMAIN_NAME_ZH`、`DOMAIN_NAME_EN`、`DOMAIN_DESC_ZH`。

Edit 1 — `DOMAIN_NAME_ZH`（在 D_GOV_ENFORCEMENT 之后插入）:
- `old_string`:
```python
    "D_GOV_ENFORCEMENT": "规则执行",
    "D_GOV_RULE": "规则治理",
```
- `new_string`:
```python
    "D_GOV_ENFORCEMENT": "规则执行",
    "D_GOV_KB": "知识库治理",
    "D_GOV_RULE": "规则治理",
```

Edit 2 — `DOMAIN_NAME_EN`（在 D_GOV_ENFORCEMENT 之后插入）:
- `old_string`:
```python
    "D_GOV_ENFORCEMENT": "Rule Enforcement",
    "D_GOV_RULE": "Rule Governance",
```
- `new_string`:
```python
    "D_GOV_ENFORCEMENT": "Rule Enforcement",
    "D_GOV_KB": "Knowledge Base Governance",
    "D_GOV_RULE": "Rule Governance",
```

Edit 3 — `DOMAIN_DESC_ZH`（在 D_GOV_ENFORCEMENT 之后插入）:
- `old_string`:
```python
    "D_GOV_ENFORCEMENT": "规则执行，负责治理规则执行和门禁拦截",
    "D_GOV_RULE": "规则治理，负责规则注册、规则版本和规则依赖管理",
```
- `new_string`:
```python
    "D_GOV_ENFORCEMENT": "规则执行，负责治理规则执行和门禁拦截",
    "D_GOV_KB": "知识库治理，负责知识管线、知识引擎和向量记忆后端管理",
    "D_GOV_RULE": "规则治理，负责规则注册、规则版本和规则依赖管理",
```

验证:
```powershell
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from domain_name_mapping import get_domain_name_zh, get_domain_name_en, get_domain_desc_zh
print('ZH:', get_domain_name_zh('D_GOV_KB'))
print('EN:', get_domain_name_en('D_GOV_KB'))
print('DESC:', get_domain_desc_zh('D_GOV_KB'))
"
```
Expected output:
```
ZH: 知识库治理
EN: Knowledge Base Governance
DESC: 知识库治理，负责知识管线、知识引擎和向量记忆后端管理
```

- [ ] **Step 5: target_layer_vocabulary.yaml 新增 D_GOV_KB 条目**

File: `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\target_layer_vocabulary.yaml`

定位 L149-152（D_GOV_RULE 条目之后，`# === 基础设施域` 注释之前）:
```yaml
  - value: D_GOV_RULE
    definition: "治理规则域——规则引擎/规则桥接"
    is_foundation: false
    ai_keywords: ["规则", "rule"]

  # === 基础设施域（来源：functional_domain_registry.yaml）===
```

Edit — `old_string`:
```yaml
  - value: D_GOV_RULE
    definition: "治理规则域——规则引擎/规则桥接"
    is_foundation: false
    ai_keywords: ["规则", "rule"]

  # === 基础设施域（来源：functional_domain_registry.yaml）===
```
`new_string`:
```yaml
  - value: D_GOV_RULE
    definition: "治理规则域——规则引擎/规则桥接"
    is_foundation: false
    ai_keywords: ["规则", "rule"]
  - value: D_GOV_KB
    definition: "治理知识库域——知识管线/知识引擎/向量记忆后端"
    is_foundation: false
    ai_keywords: ["知识库", "kb", "knowledge base"]

  # === 基础设施域（来源：functional_domain_registry.yaml）===
```

同时更新 `total_values` 从 `38` 改为 `39`:
- `old_string`: `total_values: 38`
- `new_string`: `total_values: 39`

验证（Grep）:
```
pattern: "^  - value: D_GOV_KB$"
path: d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\target_layer_vocabulary.yaml
```
Expected: 1 match.

- [ ] **Step 6: 验证 5 处定义一致性**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
sys.path.insert(0, r'd:\ZephyrAlpha\scripts\governance')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2

# 1. depgraph DB
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"SELECT domain_id, domain_name FROM domains WHERE domain_id = 'D_GOV_KB'\")
print('1. DB:', cur.fetchone())

# 2. index.yaml
import yaml
with open(r'd:\ZephyrAlpha\architecture_model\index.yaml', encoding='utf-8') as f:
    idx = yaml.safe_load(f)
kb = [d for d in idx['domains'] if d['id'] == 'D_GOV_KB']
print('2. index.yaml:', kb)

# 3. functional_domain_registry.yaml
with open(r'd:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml', encoding='utf-8') as f:
    reg = yaml.safe_load(f)
kb_entries = [e for e in reg['entries'] if e['domain'] == 'D_GOV_KB']
print('3. registry entries:', len(kb_entries))

# 4. domain_name_mapping.py
from domain_name_mapping import get_domain_name_zh
print('4. mapping ZH:', get_domain_name_zh('D_GOV_KB'))

# 5. target_layer_vocabulary.yaml
with open(r'd:\ZephyrAlpha\docs\01_policies_and_standards\_registry\vocabularies\target_layer_vocabulary.yaml', encoding='utf-8') as f:
    voc = yaml.safe_load(f)
kb_val = [v for v in voc['values'] if v['value'] == 'D_GOV_KB']
print('5. vocabulary:', kb_val)
conn.close()
"
```

Expected output:
```
1. DB: ('D_GOV_KB', 'knowledge_base_governance')
2. index.yaml: [{'id': 'D_GOV_KB', 'name': 'knowledge_base_governance', 'layer_id': 'L2_domain'}]
3. registry entries: 1
4. mapping ZH: 知识库治理
5. vocabulary: [{'value': 'D_GOV_KB', 'definition': '治理知识库域——知识管线/知识引擎/向量记忆后端', 'is_foundation': False, 'ai_keywords': ['知识库', 'kb', 'knowledge base']}]
```

---

## Task 3: OPS-2026071204 — 迁移 D_GOV depgraph 节点（5批SQL UPDATE）

**Depends on:** Task 2

**Files:**
- Modify: depgraph DB `nodes` 表（5 批 UPDATE）
- Modify: depgraph DB `domains` 表（production_nodes 缓存列更新）

- [ ] **Step 1: 查询基线 — 5 个 subdomain 的待迁移节点数**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
for sub in ['D_GOVERNANCE-AUDIT_TRAIL', 'D_GOVERNANCE-DRIFT_DETECTION',
            'D_GOVERNANCE-RULE_ENFORCEMENT', 'D_GOVERNANCE-KB',
            'D_GOVERNANCE-SCRIPT_GOVERNANCE']:
    cur.execute(\"\"\"SELECT COUNT(*) FROM nodes
        WHERE domain_id = 'D_GOVERNANCE' AND subdomain_id = %s\"\"\", (sub,))
    total = cur.fetchone()[0]
    cur.execute(\"\"\"SELECT COUNT(*) FROM nodes
        WHERE domain_id = 'D_GOVERNANCE' AND subdomain_id = %s
        AND design_maturity = 'production'\"\"\", (sub,))
    prod = cur.fetchone()[0]
    print(f'{sub}: total={total}, production={prod}')
conn.close()
"
```

Expected output:
```
D_GOVERNANCE-AUDIT_TRAIL: total=56, production=56
D_GOVERNANCE-DRIFT_DETECTION: total=56, production=56
D_GOVERNANCE-RULE_ENFORCEMENT: total=62, production=62
D_GOVERNANCE-KB: total=22, production=22
D_GOVERNANCE-SCRIPT_GOVERNANCE: total=4, production=4
```

- [ ] **Step 2: SQL UPDATE Batch 1 — AUDIT_TRAIL → D_GOV_AUDIT**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
UPDATE nodes SET domain_id = 'D_GOV_AUDIT'
WHERE domain_id = 'D_GOVERNANCE'
  AND subdomain_id = 'D_GOVERNANCE-AUDIT_TRAIL'
\"\"\")
print('Rows updated:', cur.rowcount)
conn.commit()
conn.close()
"
```

Expected output:
```
Rows updated: 56
```

- [ ] **Step 3: SQL UPDATE Batch 2 — DRIFT_DETECTION → D_GOV_DRIFT**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
UPDATE nodes SET domain_id = 'D_GOV_DRIFT'
WHERE domain_id = 'D_GOVERNANCE'
  AND subdomain_id = 'D_GOVERNANCE-DRIFT_DETECTION'
\"\"\")
print('Rows updated:', cur.rowcount)
conn.commit()
conn.close()
"
```

Expected output:
```
Rows updated: 56
```

- [ ] **Step 4: SQL UPDATE Batch 3 — RULE_ENFORCEMENT → D_GOV_ENFORCEMENT**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
UPDATE nodes SET domain_id = 'D_GOV_ENFORCEMENT'
WHERE domain_id = 'D_GOVERNANCE'
  AND subdomain_id = 'D_GOVERNANCE-RULE_ENFORCEMENT'
\"\"\")
print('Rows updated:', cur.rowcount)
conn.commit()
conn.close()
"
```

Expected output:
```
Rows updated: 62
```

- [ ] **Step 5: SQL UPDATE Batch 4 — KB → D_GOV_KB**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
UPDATE nodes SET domain_id = 'D_GOV_KB'
WHERE domain_id = 'D_GOVERNANCE'
  AND subdomain_id = 'D_GOVERNANCE-KB'
\"\"\")
print('Rows updated:', cur.rowcount)
conn.commit()
conn.close()
"
```

Expected output:
```
Rows updated: 22
```

- [ ] **Step 6: SQL UPDATE Batch 5 — SCRIPT_GOVERNANCE → D_GOV_SCRIPTS**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
UPDATE nodes SET domain_id = 'D_GOV_SCRIPTS'
WHERE domain_id = 'D_GOVERNANCE'
  AND subdomain_id = 'D_GOVERNANCE-SCRIPT_GOVERNANCE'
\"\"\")
print('Rows updated:', cur.rowcount)
conn.commit()
conn.close()
"
```

Expected output:
```
Rows updated: 4
```

- [ ] **Step 7: 更新 production_nodes 缓存列**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
UPDATE domains d SET production_nodes = (
    SELECT COUNT(*) FROM nodes n
    WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production'
)
WHERE d.domain_id IN (
    'D_GOVERNANCE', 'D_GOV_AUDIT', 'D_GOV_DRIFT',
    'D_GOV_ENFORCEMENT', 'D_GOV_KB', 'D_GOV_SCRIPTS'
)
\"\"\")
print('Domains updated:', cur.rowcount)
conn.commit()
cur.execute(\"\"\"
SELECT domain_id, production_nodes FROM domains
WHERE domain_id IN (
    'D_GOVERNANCE', 'D_GOV_AUDIT', 'D_GOV_DRIFT',
    'D_GOV_ENFORCEMENT', 'D_GOV_KB', 'D_GOV_SCRIPTS'
) ORDER BY domain_id
\"\"\")
for row in cur.fetchall():
    print(' ', row)
conn.close()
"
```

Expected output:
```
Domains updated: 6
  ('D_GOV_AUDIT', 58)
  ('D_GOV_DRIFT', 57)
  ('D_GOV_ENFORCEMENT', 144)
  ('D_GOV_KB', 22)
  ('D_GOV_SCRIPTS', 444)
  ('D_GOVERNANCE', 306)
```

（具体数值取决于迁移前各域已有节点数；D_GOVERNANCE 应 ≈306）

- [ ] **Step 8: 验证迁移结果**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
# 验证：5 个 subdomain 的节点 domain_id 已全部更新
cur.execute(\"\"\"
SELECT subdomain_id, domain_id, COUNT(*)
FROM nodes
WHERE subdomain_id IN (
    'D_GOVERNANCE-AUDIT_TRAIL', 'D_GOVERNANCE-DRIFT_DETECTION',
    'D_GOVERNANCE-RULE_ENFORCEMENT', 'D_GOVERNANCE-KB',
    'D_GOVERNANCE-SCRIPT_GOVERNANCE'
)
GROUP BY subdomain_id, domain_id
ORDER BY subdomain_id
\"\"\")
for row in cur.fetchall():
    print(' ', row)
# 验证：D_GOVERNANCE 不再包含这 5 个 subdomain 的节点
cur.execute(\"\"\"
SELECT COUNT(*) FROM nodes
WHERE domain_id = 'D_GOVERNANCE'
  AND subdomain_id IN (
    'D_GOVERNANCE-AUDIT_TRAIL', 'D_GOVERNANCE-DRIFT_DETECTION',
    'D_GOVERNANCE-RULE_ENFORCEMENT', 'D_GOVERNANCE-KB',
    'D_GOVERNANCE-SCRIPT_GOVERNANCE'
  )
\"\"\")
print('D_GOVERNANCE 残留待迁 subdomain 节点:', cur.fetchone()[0])
conn.close()
"
```

Expected output:
```
  ('D_GOVERNANCE-AUDIT_TRAIL', 'D_GOV_AUDIT', 56)
  ('D_GOVERNANCE-DRIFT_DETECTION', 'D_GOV_DRIFT', 56)
  ('D_GOVERNANCE-KB', 'D_GOV_KB', 22)
  ('D_GOVERNANCE-RULE_ENFORCEMENT', 'D_GOV_ENFORCEMENT', 62)
  ('D_GOVERNANCE-SCRIPT_GOVERNANCE', 'D_GOV_SCRIPTS', 4)
D_GOVERNANCE 残留待迁 subdomain 节点: 0
```

---

## Task 4: OPS-2026071205 — 同步 D_GOV 代码表头（src/ 文件）

**Depends on:** Task 3

**Files:**
- Modify: `src/zephyr/governance/audit_trail/*.py`、`src/zephyr/governance/audit/*.py`、`src/zephyr/governance/semantic_audit/*.py` → D_GOV_AUDIT
- Modify: `src/zephyr/governance/drift_detector_core/**/*.py` → D_GOV_DRIFT
- Modify: `src/zephyr/governance/commit_gates/*.py` → D_GOV_ENFORCEMENT
- Modify: `src/zephyr/governance/rule_enforcement/**/*.py` → D_GOV_ENFORCEMENT
- Modify: `src/zephyr/governance/rule_bridge/*.py` → D_GOV_ENFORCEMENT
- Modify: `src/zephyr/governance/behavioral_admission/*.py` → D_GOV_ENFORCEMENT
- Modify: `src/zephyr/governance/kb/**/*.py` → D_GOV_KB

- [ ] **Step 1: 列出所有需迁移的 src/ 文件（基线）**

Run:
```powershell
cd d:\ZephyrAlpha
# 统计每个目录下带 D_GOVERNANCE 表头的文件数
$dirs = @(
    'src/zephyr/governance/audit_trail',
    'src/zephyr/governance/audit',
    'src/zephyr/governance/semantic_audit',
    'src/zephyr/governance/drift_detector_core',
    'src/zephyr/governance/commit_gates',
    'src/zephyr/governance/rule_enforcement',
    'src/zephyr/governance/rule_bridge',
    'src/zephyr/governance/behavioral_admission',
    'src/zephyr/governance/kb'
)
foreach ($d in $dirs) {
    $count = (Get-ChildItem -Path $d -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Measure-Object).Count
    Write-Host "$d : $count files"
}
```

Expected output（数值为实际统计值，用作迁移基线）:
```
src/zephyr/governance/audit_trail : N files
src/zephyr/governance/audit : N files
src/zephyr/governance/semantic_audit : N files
src/zephyr/governance/drift_detector_core : N files
src/zephyr/governance/commit_gates : 41 files
src/zephyr/governance/rule_enforcement : N files
src/zephyr/governance/rule_bridge : N files
src/zephyr/governance/behavioral_admission : N files
src/zephyr/governance/kb : 31 files
```

记录总数 `TOTAL_SRC` 供 Step 9 验证。

- [ ] **Step 2: 批量替换 audit_trail/ + audit/ + semantic_audit/ → D_GOV_AUDIT**

Run:
```powershell
cd d:\ZephyrAlpha
$dirs = @(
    'src/zephyr/governance/audit_trail',
    'src/zephyr/governance/audit',
    'src/zephyr/governance/semantic_audit'
)
foreach ($d in $dirs) {
    Get-ChildItem -Path $d -Recurse -Filter *.py | ForEach-Object {
        $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
        if ($content -match '^# \[DOMAIN\] D_GOVERNANCE$' -m) {
            $newContent = $content -replace '^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_AUDIT'
            Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
            Write-Host "Updated: $($_.FullName)"
        }
    }
}
```

Expected output: 列出所有更新的文件路径，每行一个。

- [ ] **Step 3: 批量替换 drift_detector_core/ → D_GOV_DRIFT**

Run:
```powershell
cd d:\ZephyrAlpha
Get-ChildItem -Path 'src/zephyr/governance/drift_detector_core' -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        $newContent = $content -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_DRIFT'
        Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Host "Updated: $($_.FullName)"
    }
}
```

Expected output: 列出 drift_detector_core 下所有更新的文件（含 `bridges/drift_bridge.py`、`performance_baseline.py` 等）。

- [ ] **Step 4: 批量替换 commit_gates/ → D_GOV_ENFORCEMENT**

Run:
```powershell
cd d:\ZephyrAlpha
Get-ChildItem -Path 'src/zephyr/governance/commit_gates' -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        $newContent = $content -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_ENFORCEMENT'
        Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Host "Updated: $($_.FullName)"
    }
}
```

Expected output: 列出 commit_gates 下 41 个更新的文件。

- [ ] **Step 5: 批量替换 rule_enforcement/ → D_GOV_ENFORCEMENT**

Run:
```powershell
cd d:\ZephyrAlpha
Get-ChildItem -Path 'src/zephyr/governance/rule_enforcement' -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        $newContent = $content -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_ENFORCEMENT'
        Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Host "Updated: $($_.FullName)"
    }
}
```

Expected output: 列出 rule_enforcement 下所有更新的文件。

- [ ] **Step 6: 批量替换 rule_bridge/ → D_GOV_ENFORCEMENT**

Run:
```powershell
cd d:\ZephyrAlpha
Get-ChildItem -Path 'src/zephyr/governance/rule_bridge' -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        $newContent = $content -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_ENFORCEMENT'
        Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Host "Updated: $($_.FullName)"
    }
}
```

Expected output: 列出 rule_bridge 下更新的文件（含 `session_worktree.py`、`git_commit_gateway.py` 等）。

- [ ] **Step 7: 批量替换 behavioral_admission/ → D_GOV_ENFORCEMENT**

Run:
```powershell
cd d:\ZephyrAlpha
Get-ChildItem -Path 'src/zephyr/governance/behavioral_admission' -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        $newContent = $content -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_ENFORCEMENT'
        Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Host "Updated: $($_.FullName)"
    }
}
```

Expected output: 列出 behavioral_admission 下更新的文件。

- [ ] **Step 8: 批量替换 kb/ → D_GOV_KB**

Run:
```powershell
cd d:\ZephyrAlpha
Get-ChildItem -Path 'src/zephyr/governance/kb' -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        $newContent = $content -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_KB'
        Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
        Write-Host "Updated: $($_.FullName)"
    }
}
```

Expected output: 列出 kb 下 31 个更新的文件（含 `pipeline/*.py`、`storage/*.py`、`kb_engine/*.py` 等）。

- [ ] **Step 9: 验证替换结果 — 9 个目录下应无 D_GOVERNANCE 表头残留**

Run:
```powershell
cd d:\ZephyrAlpha
$dirs = @(
    'src/zephyr/governance/audit_trail',
    'src/zephyr/governance/audit',
    'src/zephyr/governance/semantic_audit',
    'src/zephyr/governance/drift_detector_core',
    'src/zephyr/governance/commit_gates',
    'src/zephyr/governance/rule_enforcement',
    'src/zephyr/governance/rule_bridge',
    'src/zephyr/governance/behavioral_admission',
    'src/zephyr/governance/kb'
)
$totalResidual = 0
foreach ($d in $dirs) {
    $count = (Get-ChildItem -Path $d -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Measure-Object).Count
    if ($count -gt 0) { Write-Host "RESIDUAL in $d : $count files" }
    $totalResidual += $count
}
Write-Host "TOTAL_RESIDUAL=$totalResidual"
```

Expected output:
```
TOTAL_RESIDUAL=0
```

若 `TOTAL_RESIDUAL > 0`，回到对应 Step 重新替换。

---

## Task 5: OPS-2026071206 — 同步 D_GOV 脚本表头（scripts/ 文件）

**Depends on:** Task 3

**Files:**
- Modify: `scripts/governance/**/*.py` 中所有 `# [DOMAIN] D_GOVERNANCE` 表头 → `# [DOMAIN] D_GOV_SCRIPTS`

**说明**: `scripts/governance/` 下所有带 `D_GOVERNANCE` 表头的脚本统一迁移到 `D_GOV_SCRIPTS`。已知 `scripts/governance/` 下有 100 个文件带此表头。

- [ ] **Step 1: 列出所有带 D_GOVERNANCE 表头的 scripts/ 文件（基线）**

Run:
```powershell
cd d:\ZephyrAlpha
$count = (Get-ChildItem -Path 'scripts/governance' -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Measure-Object).Count
Write-Host "TOTAL_SCRIPTS=$count"
# 列出前 10 个样本路径
Get-ChildItem -Path 'scripts/governance' -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Select-Object -First 10 | ForEach-Object { Write-Host $_.Path }
```

Expected output:
```
TOTAL_SCRIPTS=100
d:\ZephyrAlpha\scripts\governance\architecture_health_dashboard.py
d:\ZephyrAlpha\scripts\governance\apply_depgraph.py
d:\ZephyrAlpha\scripts\governance\apply_dataflowgraph.py
...
```

- [ ] **Step 2: 批量替换 scripts/governance/ → D_GOV_SCRIPTS**

Run:
```powershell
cd d:\ZephyrAlpha
$updated = 0
Get-ChildItem -Path 'scripts/governance' -Recurse -Filter *.py | ForEach-Object {
    $content = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($content -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        $newContent = $content -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS'
        Set-Content -Path $_.FullName -Value $newContent -NoNewline -Encoding UTF8
        $updated++
    }
}
Write-Host "UPDATED=$updated"
```

Expected output:
```
UPDATED=100
```

- [ ] **Step 3: 验证替换结果 — scripts/governance/ 下应无 D_GOVERNANCE 表头残留**

Run:
```powershell
cd d:\ZephyrAlpha
$count = (Get-ChildItem -Path 'scripts/governance' -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Measure-Object).Count
Write-Host "RESIDUAL=$count"
```

Expected output:
```
RESIDUAL=0
```

若 `RESIDUAL > 0`，回到 Step 2 重新替换遗漏文件。

- [ ] **Step 4: 抽样验证 3 个文件表头已正确更新**

Read 文件前 5 行验证:
- `d:\ZephyrAlpha\scripts\governance\generate_project_depgraph.py`
- `d:\ZephyrAlpha\scripts\governance\d11_compliance\verify_schema_health.py`
- `d:\ZephyrAlpha\scripts\governance\d5_architecture\checkers\check_blueprint_code_alignment.py`

每个文件第 3-4 行应为 `# [DOMAIN] D_GOV_SCRIPTS`。

Expected: 3 个文件均显示 `# [DOMAIN] D_GOV_SCRIPTS`。

---

## Task 6: OPS-2026071207 — 同步 D_GOV 测试+文档+注册表（25个文件）

**Depends on:** Task 3

**Files:**
- Modify: `tests/**/*.py` 中带 `# [DOMAIN] D_GOVERNANCE` 表头的文件 → 对应新域
- Modify: 3 个含逻辑断言的测试文件
- Modify: `AGENTS.md` L132
- Modify: `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml`（#ARCH-052 状态更新）

- [ ] **Step 1: 列出 tests/ 中带 D_GOVERNANCE 表头的文件**

Run:
```powershell
cd d:\ZephyrAlpha
Get-ChildItem -Path 'tests' -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Group-Object Path | ForEach-Object { Write-Host $_.Name }
```

Expected output（14 个文件，每个文件 1 个表头）:
```
d:\ZephyrAlpha\tests\git\test_git_commit_gateway.py
d:\ZephyrAlpha\tests\test_align_panoramas.py
d:\ZephyrAlpha\tests\governance\test_ast_import_rewriter.py
d:\ZephyrAlpha\tests\test_generate_decision_diagram.py
d:\ZephyrAlpha\tests\test_generate_dataflow_diagram.py
d:\ZephyrAlpha\tests\governance\generators\test_check_gate_inventory_drift.py
d:\ZephyrAlpha\tests\governance\commit_gates\test_tests_coverage_gate.py
d:\ZephyrAlpha\tests\governance\commit_gates\test_r5_digit_suffix_gate.py
d:\ZephyrAlpha\tests\governance\commit_gates\test_create_guard.py
d:\ZephyrAlpha\tests\governance\scripts_governance\test_check_vocab_hardcode.py
d:\ZephyrAlpha\tests\governance\scripts_governance\test_pre_write_gate.py
d:\ZephyrAlpha\tests\io\test_depgraph_schema.py
d:\ZephyrAlpha\tests\io\test_verify_schema_health.py
d:\ZephyrAlpha\tests\rollback\test_concurrency_guard_red_blue.py
```

- [ ] **Step 2: 批量替换 tests/ 表头（按子目录归属）**

Run:
```powershell
cd d:\ZephyrAlpha

# tests/governance/commit_gates/ → D_GOV_ENFORCEMENT
Get-ChildItem -Path 'tests/governance/commit_gates' -Recurse -Filter *.py | ForEach-Object {
    $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        Set-Content -Path $_.FullName -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_ENFORCEMENT') -NoNewline -Encoding UTF8
        Write-Host "Updated (ENFORCEMENT): $($_.FullName)"
    }
}

# tests/governance/scripts_governance/ → D_GOV_SCRIPTS
Get-ChildItem -Path 'tests/governance/scripts_governance' -Recurse -Filter *.py | ForEach-Object {
    $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        Set-Content -Path $_.FullName -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
        Write-Host "Updated (SCRIPTS): $($_.FullName)"
    }
}

# tests/governance/depgraph/ → D_GOV_SCRIPTS（depgraph 生成器脚本属脚本治理）
Get-ChildItem -Path 'tests/governance/depgraph' -Recurse -Filter *.py | ForEach-Object {
    $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        Set-Content -Path $_.FullName -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
        Write-Host "Updated (SCRIPTS): $($_.FullName)"
    }
}

# tests/governance/generators/ → D_GOV_SCRIPTS
Get-ChildItem -Path 'tests/governance/generators' -Recurse -Filter *.py | ForEach-Object {
    $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        Set-Content -Path $_.FullName -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
        Write-Host "Updated (SCRIPTS): $($_.FullName)"
    }
}

# tests/io/ → D_GOV_SCRIPTS（depgraph_schema/verify_schema_health 属脚本治理范畴）
Get-ChildItem -Path 'tests/io' -Recurse -Filter *.py | ForEach-Object {
    $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        Set-Content -Path $_.FullName -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
        Write-Host "Updated (SCRIPTS): $($_.FullName)"
    }
}

# tests/git/ → D_GOV_ENFORCEMENT（git_commit_gateway 属 rule_enforcement 范畴）
Get-ChildItem -Path 'tests/git' -Recurse -Filter *.py | ForEach-Object {
    $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        Set-Content -Path $_.FullName -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_ENFORCEMENT') -NoNewline -Encoding UTF8
        Write-Host "Updated (ENFORCEMENT): $($_.FullName)"
    }
}

# tests/rollback/ → D_GOV_ENFORCEMENT（concurrency_guard 属 rule_enforcement）
Get-ChildItem -Path 'tests/rollback' -Recurse -Filter *.py | ForEach-Object {
    $c = Get-Content -Path $_.FullName -Raw -Encoding UTF8
    if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
        Set-Content -Path $_.FullName -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_ENFORCEMENT') -NoNewline -Encoding UTF8
        Write-Host "Updated (ENFORCEMENT): $($_.FullName)"
    }
}

# tests/governance/test_ast_import_rewriter.py → D_GOV_SCRIPTS
$f = 'tests/governance/test_ast_import_rewriter.py'
$c = Get-Content -Path $f -Raw -Encoding UTF8
if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
    Set-Content -Path $f -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
    Write-Host "Updated (SCRIPTS): $f"
}

# tests/test_generate_decision_diagram.py → D_GOV_SCRIPTS
$f = 'tests/test_generate_decision_diagram.py'
$c = Get-Content -Path $f -Raw -Encoding UTF8
if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
    Set-Content -Path $f -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
    Write-Host "Updated (SCRIPTS): $f"
}

# tests/test_generate_dataflow_diagram.py → D_GOV_SCRIPTS
$f = 'tests/test_generate_dataflow_diagram.py'
$c = Get-Content -Path $f -Raw -Encoding UTF8
if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
    Set-Content -Path $f -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
    Write-Host "Updated (SCRIPTS): $f"
}

# tests/test_align_panoramas.py → D_GOV_SCRIPTS
$f = 'tests/test_align_panoramas.py'
$c = Get-Content -Path $f -Raw -Encoding UTF8
if ($c -match '(?m)^# \[DOMAIN\] D_GOVERNANCE$') {
    Set-Content -Path $f -Value ($c -replace '(?m)^# \[DOMAIN\] D_GOVERNANCE$', '# [DOMAIN] D_GOV_SCRIPTS') -NoNewline -Encoding UTF8
    Write-Host "Updated (SCRIPTS): $f"
}
```

Expected output: 列出所有 14 个更新的文件，每个文件标注目标域。

- [ ] **Step 3: 处理 test_depgraph_generator_design_protection.py L27 逻辑断言**

File: `d:\ZephyrAlpha\tests\governance\depgraph\test_depgraph_generator_design_protection.py`

L27 内容:
```python
_TEST_DOMAIN = "D_GOVERNANCE"
```

用 Edit 工具替换:
- `old_string`: `_TEST_DOMAIN = "D_GOVERNANCE"`
- `new_string`: `_TEST_DOMAIN = "D_GOV_KB"`

说明：该测试需要一个真实存在的域作为外键，D_GOV_KB 已在 Task 2 Step 1 创建并可用。

验证（Read L25-30）:
```
25→# 用真实存在的域（外键约束要求 domain_id 必须在 domains 表中存在）
26→_TEST_DOMAIN = "D_GOV_KB"
```

- [ ] **Step 4: 处理 test_align_panoramas.py L449 测试 fixture**

File: `d:\ZephyrAlpha\tests\test_align_panoramas.py`

L449 内容（在 fixture 字符串中）:
```python
            "---\nmodule_id: MOD-GATE_ENGINE\nresponsibility_domain: D_GOVERNANCE\n---\n# Gate\n",
```

用 Edit 工具替换:
- `old_string`: `"---\nmodule_id: MOD-GATE_ENGINE\nresponsibility_domain: D_GOVERNANCE\n---\n# Gate\n",`
- `new_string`: `"---\nmodule_id: MOD-GATE_ENGINE\nresponsibility_domain: D_GOV_ENFORCEMENT\n---\n# Gate\n",`

说明：MOD-GATE_ENGINE 属于 rule_enforcement 子域，已迁移到 D_GOV_ENFORCEMENT。

验证（Read L446-452）应显示 `responsibility_domain: D_GOV_ENFORCEMENT`。

- [ ] **Step 5: 处理 test_depgraph_schema.py 测试数据**

File: `d:\ZephyrAlpha\tests\io\test_depgraph_schema.py`

Run Grep 查找文件中所有 D_GOVERNANCE 引用:
```
pattern: D_GOVERNANCE
path: d:\ZephyrAlpha\tests\io\test_depgraph_schema.py
output_mode: content
-n: true
```

对该文件中所有非表头的 `D_GOVERNANCE` 引用（如 frontmatter 测试数据中的 `domain: D_GOVERNANCE`）逐一用 Edit 工具替换为 `D_GOV_KB`（或其他迁移目标域）。表头已在 Step 2 替换。

若文件中 D_GOVERNANCE 仅作为表头出现（已在 Step 2 替换），此步跳过。

验证: 再次 Grep `D_GOVERNANCE` 应 0 匹配。

- [ ] **Step 6: 更新 AGENTS.md L132 域归属描述**

File: `d:\ZephyrAlpha\AGENTS.md`

L132 内容:
```
### 基础设施层（D_INFRA_RUNTIME / D_INFRA_RECOVERY / D_GOVERNANCE）
```

用 Edit 工具替换:
- `old_string`: `### 基础设施层（D_INFRA_RUNTIME / D_INFRA_RECOVERY / D_GOVERNANCE）`
- `new_string`: `### 基础设施层（D_INFRA_RUNTIME / D_INFRA_RECOVERY / D_GOV_ENFORCEMENT）`

说明：D_GOVERNANCE 已拆分，原 L132 列出的"基础设施层"模块实际归属 rule_enforcement，对应新域 D_GOV_ENFORCEMENT。

验证（Read L132）:
```
132→### 基础设施层（D_INFRA_RUNTIME / D_INFRA_RECOVERY / D_GOV_ENFORCEMENT）
```

- [ ] **Step 7: 更新 architecture_issue_registry.yaml #ARCH-052 状态**

File: `d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\architecture_issue_registry.yaml`

定位 #ARCH-052 条目（约 L1432）。当前 `status: decided`，需更新为 `in_progress` 并追加 Phase 1 完成记录。

用 Edit 工具替换 `old_string`（约 L1436）:
```yaml
  status: decided
  description: |
    5 个超容域（D_GOV_ENFORCEMENT 200/150, D_GOV_SCRIPTS 432/150, D_GOVERNANCE 847/150,
```
`new_string`:
```yaml
  status: in_progress
  description: |
    Phase 1（2026-07-12）：D_GOVERNANCE 域 506 production 节点降至 ~306（迁移 200 节点至 5 个 D_GOV_* 子域），同步 53 src/ + 100 scripts/ + 22 tests/ 表头，新增 D_GOV_KB 域定义（5 处）。
    5 个超容域（D_GOV_ENFORCEMENT 200/150, D_GOV_SCRIPTS 432/150, D_GOVERNANCE 847/150,
```

再定位 `last_updated`（约 L1470）:
- `old_string`:
```yaml
  created: '2026-07-06'
  last_updated: '2026-07-06'
```
- `new_string`:
```yaml
  created: '2026-07-06'
  last_updated: '2026-07-12'
```

验证（Grep）:
```
pattern: "status: in_progress"
path: d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\architecture_issue_registry.yaml
-B: 5
```
Expected: 匹配 #ARCH-052 条目的 status 行。

- [ ] **Step 8: 验证 tests/ 表头替换结果**

Run:
```powershell
cd d:\ZephyrAlpha
$count = (Get-ChildItem -Path 'tests' -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Measure-Object).Count
Write-Host "RESIDUAL_HEADER=$count"
```

Expected output:
```
RESIDUAL_HEADER=0
```

若 `RESIDUAL_HEADER > 0`，回到 Step 2 重新替换遗漏文件。

- [ ] **Step 9: 提交本 Task 所有文件变更到 worktree**

Run（替换 `$SID` 为 Task 1 Step 1 的 session_id）:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.rule_bridge.session_worktree import session_worktree_commit
import subprocess
# 收集所有已修改文件
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=r'd:\ZephyrAlpha')
files = [line[3:].strip() for line in r.stdout.strip().split('\n') if line.strip()]
result = session_worktree_commit(
    '$SID',
    files,
    'OPS-2026071207: sync D_GOV test/doc/registry headers (25 files)'
)
print(result)
"
```

Expected output:
```
{'session_id': '...', 'status': 'OK', 'message': 'committed in worktree', 'commit_hash': '...'}
```

---

## Task 7: OPS-2026071208 — D_GOV 验证：重生成 depgraph + ARCH-CAP-002 检查

**Depends on:** Task 4, Task 5, Task 6

**Files:**
- Run: `scripts/governance/generate_project_depgraph.py`
- Run: `scripts/governance/d5_architecture/checkers/check_blueprint_code_alignment.py`
- Run: `scripts/governance/d11_compliance/verify_schema_health.py`

- [ ] **Step 1: 提交所有未提交变更到 worktree**

Run（替换 `$SID` 为 Task 1 Step 1 的 session_id）:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.rule_bridge.session_worktree import session_worktree_commit
import subprocess
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=r'd:\ZephyrAlpha')
files = [line[3:].strip() for line in r.stdout.strip().split('\n') if line.strip()]
if not files:
    print('NOTHING_TO_COMMIT')
else:
    result = session_worktree_commit('$SID', files, 'OPS-2026071208: pre-validation checkpoint')
    print(result)
"
```

Expected output:
```
NOTHING_TO_COMMIT
```
（或 `{'status': 'OK', ...}` 如有未提交变更）

- [ ] **Step 2: 运行 generate_project_depgraph.py 重生成 depgraph**

Run:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\generate_project_depgraph.py --no-dry-run 2>&1 | Select-Object -Last 30
```

Expected output（最后几行应显示成功）:
```
[generate_project_depgraph] PostgreSQL depgraph updated: N nodes, M edges
[generate_project_depgraph] production_nodes cached
```

- [ ] **Step 3: 查询 D_GOVERNANCE production_nodes 验证迁移效果**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"SELECT domain_id, production_nodes FROM domains
    WHERE domain_id IN (
        'D_GOVERNANCE', 'D_GOV_AUDIT', 'D_GOV_DRIFT',
        'D_GOV_ENFORCEMENT', 'D_GOV_KB', 'D_GOV_SCRIPTS'
    ) ORDER BY domain_id\"\"\")
for row in cur.fetchall():
    print(row)
# ARCH-CAP-002 检查：>150 的域
cur.execute(\"\"\"SELECT domain_id, production_nodes FROM domains
    WHERE production_nodes > 150 ORDER BY production_nodes DESC\"\"\")
print('ARCH-CAP-002 violations (>150):')
for row in cur.fetchall():
    print(' ', row)
conn.close()
"
```

Expected output:
```
('D_GOV_AUDIT', 58)
('D_GOV_DRIFT', 57)
('D_GOV_ENFORCEMENT', 144)
('D_GOV_KB', 22)
('D_GOV_SCRIPTS', 444)
('D_GOVERNANCE', 306)
ARCH-CAP-002 violations (>150):
  ('D_GOV_SCRIPTS', 444)
  ('D_GOVERNANCE', 306)
```

说明：D_GOVERNANCE 从 506 降至 306（Phase 1 目标达成，但仍 >150，需二期专项）。D_GOV_SCRIPTS 仍超限（二期治理）。

- [ ] **Step 4: 运行 check_blueprint_code_alignment.py**

Run:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d5_architecture\checkers\check_blueprint_code_alignment.py 2>&1 | Select-Object -Last 20
```

Expected output（exit code 0 或仅显示非阻断警告）:
```
[check_blueprint_code_alignment] OK: N blueprints aligned
```
或若有 warning，记录到 `docs/_working/phase1_validation_issues.md` 供 Task 8 修复。

- [ ] **Step 5: 运行 verify_schema_health.py**

Run:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d11_compliance\verify_schema_health.py 2>&1 | Select-Object -Last 20
echo "EXIT_CODE=$LASTEXITCODE"
```

Expected output:
```
[verify_schema_health] Schema healthy: N tables, version=v19
EXIT_CODE=0
```

若 `EXIT_CODE != 0`，记录 drift 详情到 `docs/_working/phase1_validation_issues.md`。

- [ ] **Step 6: 触发 reconciler 自动同步**

Run:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.rule_bridge.git_commit_gateway import GitCommitGateway
gw = GitCommitGateway(project_root=r'd:\ZephyrAlpha')
# 列出 reconciler
print('Reconcilers:', [r.name for r in gw._reconciliation_registry._reconcilers])
"
```

Expected output: 列出 17 个 reconciler 名称。

若需手动触发（验证自动同步已生效）:
```powershell
python scripts\governance\d5_architecture\syncers\blueprint_frontmatter_reconciler.py 2>&1 | Select-Object -Last 10
```

Expected: 输出 reconciler 处理结果，无 error。

- [ ] **Step 7: 提交验证检查点到 worktree**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.rule_bridge.session_worktree import session_worktree_commit
import subprocess
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=r'd:\ZephyrAlpha')
files = [line[3:].strip() for line in r.stdout.strip().split('\n') if line.strip()]
if not files:
    print('NOTHING_TO_COMMIT')
else:
    result = session_worktree_commit('$SID', files, 'OPS-2026071208: validation checkpoint + reconciler auto-sync')
    print(result)
"
```

Expected output:
```
NOTHING_TO_COMMIT
```
（或 `{'status': 'OK', ...}` 如 reconciler 自动修改了文件）

---

## Task 8: OPS-2026071209 — D_GOV 循环验证：全项目扫描遗漏+修复至问题=0

**Depends on:** Task 7

**通过标准:** 连续 2 轮全项目扫描 0 遗漏。若某轮发现问题，修复后重新计数。

- [ ] **Step 1: 第 1 轮扫描 — Grep 全项目 D_GOVERNANCE 残留引用**

Run:
```powershell
cd d:\ZephyrAlpha
# 扫描 src/、scripts/、tests/、docs/ 下的 D_GOVERNANCE 残留（排除 .aidrafts/、_archive/、本计划文件）
$results = @()
$scanPaths = @('src', 'scripts', 'tests', 'docs', 'AGENTS.md', 'architecture_model')
foreach ($p in $scanPaths) {
    if (Test-Path $p) {
        $matches = Get-ChildItem -Path $p -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch '\\\.aidrafts\\' -and $_.FullName -notmatch '\\_archive\\' -and $_.Name -ne 'domain_split_implementation_plan_phase1.md' -and $_.Name -ne 'domain_split_proposal_d_governance_d_trading.md' -and $_.Name -ne 'phase1_baseline.md' -and $_.Name -ne 'phase1_validation_issues.md' } |
            Select-String -Pattern 'D_GOVERNANCE' -ErrorAction SilentlyContinue
        $results += $matches
    }
}
Write-Host "ROUND1_TOTAL=$($results.Count)"
$results | Group-Object Path | ForEach-Object { Write-Host "  $($_.Name): $($_.Count) matches" }
```

Expected output:
```
ROUND1_TOTAL=0
```

若 `ROUND1_TOTAL > 0`，对每个残留文件用 Edit 工具修复（参考 Task 4-6 的替换规则），修复后回到 Step 1 重新扫描（计为新一轮）。

- [ ] **Step 2: 第 1 轮扫描 — 代码表头与 depgraph domain_id 一致性检查**

Run:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys, os
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2

conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
# 获取每个域的节点路径
cur.execute(\"\"\"SELECT domain_id, path FROM nodes
    WHERE domain_id IN ('D_GOV_AUDIT', 'D_GOV_DRIFT', 'D_GOV_ENFORCEMENT', 'D_GOV_KB', 'D_GOV_SCRIPTS', 'D_GOVERNANCE')
    AND design_maturity = 'production'\"\"\")
domain_paths = {}
for domain_id, path in cur.fetchall():
    domain_paths.setdefault(domain_id, []).append(path)
conn.close()

# 检查每个文件表头是否与 depgraph domain_id 一致
mismatches = []
for domain_id, paths in domain_paths.items():
    for path in paths:
        full_path = os.path.join(r'd:\ZephyrAlpha', path.replace('/', os.sep))
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, encoding='utf-8') as f:
                for line in f:
                    if line.startswith('# [DOMAIN]'):
                        header_domain = line.strip().split()[-1]
                        if header_domain != domain_id:
                            mismatches.append((path, header_domain, domain_id))
                        break
        except Exception:
            pass

print(f'MISMATCHES={len(mismatches)}')
for m in mismatches[:20]:
    print(' ', m)
"
```

Expected output:
```
MISMATCHES=0
```

若 `MISMATCHES > 0`，对每个不匹配文件用 Edit 工具修复表头，修复后回到 Step 2 重新检查。

- [ ] **Step 3: 第 1 轮扫描 — 蓝图 frontmatter 一致性检查**

Run:
```powershell
cd d:\ZephyrAlpha
# 查找蓝图文件中 responsibility_domain: D_GOVERNANCE 的残留
Get-ChildItem -Path 'docs/03_modules' -Recurse -Filter *.md | Select-String -Pattern 'responsibility_domain:\s*D_GOVERNANCE' | ForEach-Object { Write-Host "$($_.Path):$($_.LineNumber): $($_.Line)" }
```

Expected output: 无输出（0 残留）。

若有输出，对每个蓝图文件用 Edit 工具将 `responsibility_domain: D_GOVERNANCE` 替换为正确的目标域（根据蓝图所属子域），修复后回到 Step 3 重新检查。

- [ ] **Step 4: 第 1 轮扫描 — 注册表/词表一致性检查**

Run:
```powershell
cd d:\ZephyrAlpha
$files = @(
    'architecture_model/index.yaml',
    'docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml',
    'docs/01_policies_and_standards/_registry/vocabularies/target_layer_vocabulary.yaml',
    'scripts/governance/d5_architecture/generators/domain_name_mapping.py'
)
foreach ($f in $files) {
    Write-Host "=== $f ==="
    Select-String -Path $f -Pattern 'D_GOV_KB' | Select-Object -First 3 | ForEach-Object { Write-Host "  L$($_.LineNumber): $($_.Line)" }
}
```

Expected output: 每个文件均显示至少 1 个 D_GOV_KB 匹配（Task 2 新增的定义）。

若某文件无 D_GOV_KB 匹配，回到 Task 2 对应 Step 补充定义。

- [ ] **Step 5: 第 1 轮扫描 — 运行 check_blueprint_code_alignment.py**

Run:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance\d5_architecture\checkers\check_blueprint_code_alignment.py 2>&1 | Select-Object -Last 10
echo "EXIT_CODE=$LASTEXITCODE"
```

Expected output:
```
[check_blueprint_code_alignment] OK
EXIT_CODE=0
```

若 `EXIT_CODE != 0`，根据输出修复蓝图/代码对齐问题，修复后回到 Step 5 重新运行。

- [ ] **Step 6: 第 1 轮扫描 — 运行 verify_schema_health.py**

Run:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python scripts\governance/d11_compliance/verify_schema_health.py 2>&1 | Select-Object -Last 10
echo "EXIT_CODE=$LASTEXITCODE"
```

Expected output:
```
[verify_schema_health] Schema healthy
EXIT_CODE=0
```

若 `EXIT_CODE != 0`，根据 drift 报告修复 schema，修复后回到 Step 6 重新运行。

- [ ] **Step 7: 第 1 轮判定**

若 Step 1-6 全部通过（0 遗漏 + 2 个脚本 exit 0），进入 Step 8 开始第 2 轮确认。

若任一 Step 发现问题并修复，本轮计数作废，回到 Step 1 重新开始第 1 轮。

- [ ] **Step 8: 第 2 轮确认扫描 — 重复 Step 1-6**

重复执行 Step 1-6 的所有扫描命令。所有命令必须再次返回 0 遗漏 + 2 个脚本 exit 0。

记录第 2 轮结果:
- Step 1 ROUND2_TOTAL=0
- Step 2 MISMATCHES=0
- Step 3 无输出
- Step 4 4 个文件均有 D_GOV_KB
- Step 5 EXIT_CODE=0
- Step 6 EXIT_CODE=0

- [ ] **Step 9: 提交最终验证记录到 worktree**

File: `d:\ZephyrAlpha\docs\_working\phase1_validation_record.md`

Content:
```markdown
# Phase 1 D_GOVERNANCE 域拆分验证记录

**验证时间**: 2026-07-12
**Session ID**: <填入实际值>
**连续 0 遗漏轮数**: 2

## 第 1 轮结果
- ROUND1_TOTAL=0
- MISMATCHES=0
- 蓝图残留=0
- 注册表/词表 D_GOV_KB 定义存在=4/4
- check_blueprint_code_alignment.py EXIT_CODE=0
- verify_schema_health.py EXIT_CODE=0

## 第 2 轮结果
- ROUND2_TOTAL=0
- MISMATCHES=0
- 蓝图残留=0
- 注册表/词表 D_GOV_KB 定义存在=4/4
- check_blueprint_code_alignment.py EXIT_CODE=0
- verify_schema_health.py EXIT_CODE=0

## ARCH-CAP-002 状态
- D_GOVERNANCE: 506 → 306（仍超限，二期专项）
- D_GOV_AUDIT: 58（合规）
- D_GOV_DRIFT: 57（合规）
- D_GOV_ENFORCEMENT: 144（合规）
- D_GOV_KB: 22（合规，新建）
- D_GOV_SCRIPTS: 444（仍超限，二期治理）
```

将 `<填入实际值>` 替换为 Task 1 Step 1 的 session_id。

- [ ] **Step 10: session_worktree_commit 最终提交**

Run（替换 `$SID` 为实际值）:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.rule_bridge.session_worktree import session_worktree_commit
import subprocess
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=r'd:\ZephyrAlpha')
files = [line[3:].strip() for line in r.stdout.strip().split('\n') if line.strip()]
if not files:
    print('NOTHING_TO_COMMIT')
else:
    result = session_worktree_commit(
        '$SID',
        files,
        'OPS-2026071209: Phase 1 D_GOV domain split - 2 rounds validation passed (0 residual)'
    )
    print(result)
"
```

Expected output:
```
{'session_id': '...', 'status': 'OK', 'message': 'committed in worktree', 'commit_hash': '...'}
```

- [ ] **Step 11: session_worktree_merge 合并到主分支**

Run（替换 `$SID` 为实际值）:
```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.rule_bridge.session_worktree import session_worktree_merge
result = session_worktree_merge('$SID')
print(result)
"
```

Expected output:
```
{'session_id': '...', 'merged': True, 'message': 'merge 成功，worktree 已清理', 'cleaned': True, 'unregistered': True, 'reconcile_results': [...]}
```

若 `merged=False`，根据 `message` 字段处理冲突，解决后重新调 `session_worktree_merge`。

- [ ] **Step 12: 最终验证 — merge 后主分支健康检查**

Run:
```powershell
cd d:\ZephyrAlpha
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
# 1. git log 确认 merge commit
git log --oneline -5
# 2. 验证 D_GOVERNANCE 节点数
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"SELECT domain_id, production_nodes FROM domains WHERE domain_id = 'D_GOVERNANCE'\")
print('D_GOVERNANCE:', cur.fetchone())
conn.close()
"
# 3. 验证无残留
$residual = (Get-ChildItem -Path 'src','scripts','tests' -Recurse -Filter *.py | Select-String -Pattern '^# \[DOMAIN\] D_GOVERNANCE$' | Measure-Object).Count
Write-Host "FINAL_RESIDUAL=$residual"
```

Expected output:
```
<merge commit hash> OPS-2026071209: Phase 1 D_GOV domain split...
D_GOVERNANCE: ('D_GOVERNANCE', 306)
FINAL_RESIDUAL=0
```

---

## 附录 A: 回滚方案

若 Phase 1 实施过程中出现严重问题需回滚：

### A.1 depgraph 节点迁移回滚

```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"\"\"
UPDATE nodes SET domain_id = 'D_GOVERNANCE'
WHERE domain_id IN ('D_GOV_AUDIT', 'D_GOV_DRIFT', 'D_GOV_ENFORCEMENT', 'D_GOV_KB', 'D_GOV_SCRIPTS')
AND subdomain_id LIKE 'D_GOVERNANCE-%'
\"\"\")
print('Rows reverted:', cur.rowcount)
conn.commit()
conn.close()
"
```

### A.2 新建域回滚

```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
import sys
sys.path.insert(0, r'd:\ZephyrAlpha\src')
from zephyr.governance.depgraph_schema import _build_pg_dsn
import psycopg2
conn = psycopg2.connect(**_build_pg_dsn())
cur = conn.cursor()
cur.execute(\"DELETE FROM domains WHERE domain_id = 'D_GOV_KB'\")
print('D_GOV_KB deleted:', cur.rowcount)
conn.commit()
conn.close()
"
```

### A.3 文件变更回滚

```powershell
cd d:\ZephyrAlpha
git checkout -- src/ scripts/ tests/ docs/ AGENTS.md architecture_model/
```

### A.4 从 pg_dump 备份恢复

```powershell
$env:PYTHONPATH = "d:\ZephyrAlpha\src;d:\ZephyrAlpha\scripts\governance"
python -c "
from zephyr.governance.depgraph_schema import restore_from_backup
restore_from_backup(r'd:\ZephyrAlpha\tmp\depgraph_backup_phase1.dump')
print('RESTORED')
"
```

---

## 附录 B: 已知遗留（二期专项）

| 遗留项 | 说明 | 预期专项 |
|---|---|---|
| D_GOVERNANCE 仍超限 | 迁移后 ~306 production 节点，仍 >150 | src/zephyr/governance/ 包按八件套拆分 |
| D_GOV_SCRIPTS 仍超限 | 444 production 节点 >150 | #ARCH-052 Phase 4 聚合节点模式治理 |
| 代码物理路径未迁移 | kb/ 等仍在 governance/ 目录下 | 物理迁移 + import 路径修改 |
| D_TRADING 域拆分 | 280 production 节点超限 | Phase 2 实施（OPS-2026071210~215） |
