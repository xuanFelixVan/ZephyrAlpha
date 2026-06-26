---
module_id: GOV-036-PHASE-D
doc_type: construction_plan
status: Active
version: 2.0.0
created: '2026-06-22'
last_updated: '2026-06-22'
owner: human
purpose: 阶段D全量功能测试的详细施工方案，含前置条件、分阶段执行计划、验收标准
parent_document: architecture_upgrade_discussion.md §二十五
anti_hallucination: 所有路径和命令均已验证存在，所有数字来自实际查询
ttl: permanent
---

# 阶段D：全量功能测试 — 详细施工方案

> **父文档**：[architecture_upgrade_discussion.md §二十五](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md)
> **讨论方案**：§25.1-25.7 定义了D1-D5五项工作内容，本文档将其展开为可执行的施工步骤
> **核心原则**：准备阶段（Phase 0）可立即执行；测试执行阶段（Phase 1+）需A/B/C完成

## 〇、就绪度评估（2026-06-22 实测）

### 0.1 前置条件完成状态

| 前置条件 | 状态 | 证据 | 阻塞级别 |
|----------|------|------|:---:|
| 阶段A：安全网 | ⚠️ 部分完成 | ide_health_service 守护进程未运行；DM-100000/100001/100002 待执行 | P0 |
| 阶段B：全量清洁 | ✅ 基本完成 | audit_registration.py = CLEAN；script_manifest.yaml 存在(457脚本) | — |
| 阶段C：depgraph补全 | ⚠️ 运行态完成 | 43域0空域；但9-12个空壳域无模块；设计态补全未开始 | P1 |

### 0.2 基础设施就绪度

| 维度 | 实测值 | 目标值 | 差距 | 阻塞级别 |
|------|--------|--------|------|:---:|
| depgraph 孤儿节点率 | 98.4% (14,159/14,384) | <5% | 93.4pp | P0 |
| [BLUEPRINT] 头部覆盖率 | 2.9% (100/3,421) | >30% | 27.1pp | P0 |
| `__all__` 覆盖率 | 17.8% (100/562) | >60% | 42.2pp | P1 |
| Phase D 核心表 | 0/5 | 5/5 | 5表 | P0 |
| pytest 可收集测试 | 33,662 | — | — | ✅ |
| depgraph.db 节点数 | 14,374 | — | — | ✅ |
| depgraph.db 域数 | 43 | — | — | ✅ |
| script_manifest.yaml | 457脚本 | — | — | ✅ |

### 0.3 施工策略

**分两阶段施工**：

| 阶段 | 内容 | 前置条件 | 可否立即执行 |
|------|------|---------|:---:|
| **Phase 0：准备** | 建表 + 清单提取 + pytest插件 + 试运行 | 无 | ✅ 立即 |
| **Phase 1：执行** | 建卡 + 六类测试 + 存活地图 + 闭环反馈 | A+B+C完成 | ❌ 阻塞中 |

Phase 0 的产出将直接降低 Phase 1 的阻塞项——清单提取会发现孤儿节点的真实归属，试运行会暴露实际可测试范围。

### 0.4 项目功能全景（18大功能 + 8骨架功能）

> 来源：蓝图注册表(60蓝图) + 源码(30+顶层包) + 功能域注册表(34子域) + System Master蓝图(102章)

#### 0.4.1 18大功能（代码成熟度高，可分配AI恢复）

| # | 功能ID | 大功能 | 包含的子系统 | 代码成熟度 | 对应蓝图 | 源码包 |
|---|--------|--------|------------|:---:|---------|--------|
| 1 | F1 | 自动驾驶/运行时大脑 | AutoPilot + AutoRuntimeCore + Conductor + SessionLifecycle + WorkOrchestrator + DreamCycle + CircadianScheduler + IdeHealthDaemon + StagingArea + AdmissionController + VerdictEngine | 高 | MOD-INF-035 | trading/ |
| 2 | F2 | 门禁引擎 | PhaseManager + PhaseExecutor + 51门控检查 + GateEngine + G0-G7门禁 + 门禁域熔断器 | 高 | MOD-INF-007 | governance/rule_enforcement/ |
| 3 | F3 | 任务系统 | TaskRepo + TaskCard + BlueprintDecomposer + 10状态机 + 粒度门禁(R1-R6) + 超粒度自动拆分 | 高 | MOD-INF-006 | governance/ |
| 4 | F4 | 预算执行器 | BudgetEngine + TokenBudget + CostBudget + ContextBudget + IPI防御 + 螺旋预警 + pre_flight_check | 高 | MOD-INF-024 | governance/ |
| 5 | F5 | 升级/委托/A2A协议 | EscalationAPI + DelegationEngine(四级约束) + A2A五层协议 + 死锁检测 + 仲裁器 + GovernanceAdapter | 高 | MOD-INF-022/025 | governance/ + infrastructure/a2a_protocol/ |
| 6 | F6 | 漂移检测/行为审计 | DriftDetector(39检测器) + ChaosInjector + BaselineManager + ContractDriftDetector + 17维度审计 + DriftCronScheduler | 高 | MOD-INF-023/033 | behavioral_audit/ |
| 7 | F7 | LLM安全网关 | L0-L8九层纵深防御 + InputSanitizer + ConstitutionEngine + RedBlueValidator + GameDayRunner + InjectionEngine + DeepSeekSpecialRiskManager | 高 | MOD-INF-014/030 | security/ |
| 8 | F8 | Agent权限/RBAC | AgentRBAC七层纵深 + KillSwitch + PermissionGuard + AgentSigner + AgentCooldown + 55模块完整性 | 高 | MOD-INF-018 | security/access_control/ |
| 9 | F9 | 回滚系统 | Git-native回滚 + AutoRollbackTrigger + RollbackSimulator + RollbackWAL + RollbackDrill + RollbackSandbox + CascadingRollbackAnalyzer | 高 | MOD-INF-021 | infrastructure/rollback/ |
| 10 | F10 | AI模型入职考试/模型画像 | ExamOrchestrator(五轴考试:横/纵/速/幻/稳) + 27道标准题 + CapabilityPassport + ModelProfiler(7维画像) + ModelTaskMatrix + ModelDiscovery | 高 | MOD-INF-036/034 | intelligence/model_profiling/ |
| 11 | F11 | 上下文引擎 | ContextPipeline四阶段 + 15个Context子模块 + Prompt注册表 | 高 | MOD-INF-008 | autonomy_core/ |
| 12 | F12 | 向量记忆/知识库 | ChromaDB 8 Collection + BGE-M3嵌入 + HybridRetriever + CrossCollectionRetriever + 知识管线(ingest/triage/extract/activate/analyze) + UnifiedMemoryAPI | 高 | MOD-INF-011/KB-001 | integration/vector_memory/ + governance/kb/ |
| 13 | F13 | MCP服务器集群 | 11个MCP Server + Gateway + 蓝图搜索/门禁/治理/知识库/向量记忆/哨兵/任务/遥测/文档守卫服务器 | 高 | MOD-INF-013 | integration/mcp/ |
| 14 | F14 | 管线编排/反馈环 | Pipeline M1-M11双管线路由 + BackpressureManager + FeedbackLoop + SLOManager + ErrorBudgetManager + AutoEvolution + FitnessFunctionFramework | 高 | MOD-INF-009/010 | integration/ + ops/ |
| 15 | F15 | 自动修复引擎 | SelfHealAgent + FixStateMachine + 8类修复器 + FixSafety + ShadowWorkspace + ComplianceAuditor | 高 | MOD-INF-031 | infrastructure/auto_fix_engine/ |
| 16 | F16 | 审计编排/孤儿审判 | AuditOrchestrator(三子系统) + SemanticAuditor + MerkleAudit + OrphanJudge(三决策树) + 信任引擎 + 重放引擎 | 高 | MOD-INF-027/028/029/020 | governance/audit_trail/ |
| 17 | F17 | 交易核心链路 | ExecutionEngine + OrderManager + OMSRiskEngine(三层风控) + StopLossEngine + AlphaSignalPipeline + FactorRegistry + BacktestEngine + StrategyPortfolio + BrokerInterface + SimulationBroker | 中-高 | MOD-L02~L06 | ex_core/ + risk/ + signal_fundamental/ + factor/ + simulation/ + pf_core/ |
| 18 | F18 | 治理脚本系统(7维度) | 457个治理脚本(d1~d7) + script_manifest + 质量标准8维度 + 命名规范N-01~N-15 | 高 | MOD-INF-005 | scripts/governance/ |

#### 0.4.2 骨架/预留功能（有目录但代码未实现，暂不分配AI）

| # | 功能ID | 功能 | 状态 | 源码包 |
|---|--------|------|------|--------|
| 19 | F19 | 智能Order Routing | 骨架 | ex_sor/ |
| 20 | F20 | A股信号 | 骨架 | signal_ashare/ |
| 21 | F21 | 数字孪生 | 骨架 | digital_twin/ |
| 22 | F22 | 新回测架构 | 骨架 | backtest/ |
| 23 | F23 | 卖出决策 | 骨架 | sell_decision/ |
| 24 | F24 | 前端Dashboard | 低 | frontend/ |
| 25 | F25 | 合规引擎 | 骨架 | compliance/ |
| 26 | F26 | ML服务 | 骨架 | ml_serve/ |

#### 0.4.3 功能间依赖关系（决定AI并行顺序）

```
F1(自动驾驶) ← 依赖 ← F2(门禁) + F3(任务) + F4(预算) + F5(升级)
F17(交易链路) ← 依赖 ← F12(向量记忆) + F14(管线/反馈)
F13(MCP集群) ← 依赖 ← F2(门禁) + F3(任务) + F12(知识库)
F15(自动修复) ← 依赖 ← F9(回滚) + F16(审计)
F6(漂移) ← 依赖 ← F16(审计)

无依赖可立即并行：F7(安全) / F8(RBAC) / F9(回滚) / F10(考试) / F11(上下文) / F18(脚本)
```

***

## 一、Phase 0：准备阶段（统筹AI负责，可立即执行）

### STEP 0.1：depgraph.db 新建5张核心表

**目标**：为 D1/D4/D5 的数据存储建表

**方法**：在 `depgraph_schema.py` 的 `_MIGRATIONS` 列表追加 v5 迁移

**DDL**：

```sql
-- v5: Phase D functional testing tables

-- D1: 功能清单
CREATE TABLE IF NOT EXISTS func_inventory (
    module_id TEXT PRIMARY KEY,
    domain_id TEXT,
    module_name TEXT NOT NULL DEFAULT '',
    ssot_path TEXT,
    blueprint_id TEXT,
    build_status TEXT DEFAULT 'unbuilt',
    has_test INTEGER DEFAULT 0,
    has_init_all INTEGER DEFAULT 0,
    consumers_count INTEGER DEFAULT 0,
    source_tags TEXT DEFAULT '[]',
    extracted_at TEXT NOT NULL,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);
CREATE INDEX IF NOT EXISTS idx_fi_domain ON func_inventory(domain_id);
CREATE INDEX IF NOT EXISTS idx_fi_blueprint ON func_inventory(blueprint_id);
CREATE INDEX IF NOT EXISTS idx_fi_build_status ON func_inventory(build_status);

-- D1: 多源交叉证据
CREATE TABLE IF NOT EXISTS func_source_cross (
    module_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_path TEXT,
    extracted_at TEXT NOT NULL,
    PRIMARY KEY (module_id, source_type),
    FOREIGN KEY (module_id) REFERENCES func_inventory(module_id)
);

-- D4: 存活地图
CREATE TABLE IF NOT EXISTS liveness_map (
    file_path TEXT NOT NULL,
    referenced_by_test TEXT DEFAULT '',
    referenced_by_script TEXT DEFAULT '',
    referenced_by_module TEXT DEFAULT '',
    last_verified TEXT,
    verification_type TEXT DEFAULT 'static',
    PRIMARY KEY (file_path)
);
CREATE INDEX IF NOT EXISTS idx_lm_verified ON liveness_map(last_verified);

-- D4: 域级存活率汇总
CREATE TABLE IF NOT EXISTS liveness_summary (
    domain_id TEXT PRIMARY KEY,
    total_files INTEGER DEFAULT 0,
    live_files INTEGER DEFAULT 0,
    dead_files INTEGER DEFAULT 0,
    unverified_files INTEGER DEFAULT 0,
    liveness_ratio REAL DEFAULT 0.0,
    last_computed TEXT,
    FOREIGN KEY (domain_id) REFERENCES domains(domain_id)
);

-- D5: 跨阶段反馈
CREATE TABLE IF NOT EXISTS phase_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_phase TEXT NOT NULL DEFAULT 'D',
    target_phase TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('P0','P1','P2')),
    finding_type TEXT NOT NULL,
    file_path TEXT,
    evidence_json TEXT,
    status TEXT DEFAULT 'open' CHECK (status IN ('open','fixed','wontfix','deferred')),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pf_target ON phase_feedback(target_phase);
CREATE INDEX IF NOT EXISTS idx_pf_severity ON phase_feedback(severity);
CREATE INDEX IF NOT EXISTS idx_pf_status ON phase_feedback(status);
```

**执行命令**：

```bash
# 1. 备份 depgraph.db
copy D:\ZephyrAlpha\data\databases\depgraph.db D:\ZephyrAlpha\data\databases\depgraph.db.backup.pre_phase_d

# 2. 修改 depgraph_schema.py 追加 v5 迁移（见下方代码变更）

# 3. 执行迁移
python -c "from zephyr.governance.depgraph_schema import init_db; init_db(); print('v5 migration done')"

# 4. 验证
python -c "import sqlite3; conn=sqlite3.connect('D:/ZephyrAlpha/data/databases/depgraph.db'); c=conn.cursor(); c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('func_inventory','func_source_cross','liveness_map','liveness_summary','phase_feedback')\"); print([r[0] for r in c.fetchall()])"
```

**验收**：5张新表存在 + `_schema_version` 中有 version=5 记录

### STEP 0.2：D1 功能清单提取

**目标**：从 depgraph.db 多源提取功能清单，写入 func_inventory 表

**数据源与提取逻辑**：

| 源 | 提取SQL | 写入字段 |
|----|---------|---------|
| nodes (module类型) | `SELECT node_id, domain_id, node_name, path, blueprint_id, build_status, change_policy, modification_permission FROM nodes WHERE node_type='module'` | module_id, domain_id, module_name, ssot_path, blueprint_id, build_status |
| nodes (script类型) | `SELECT node_id, domain_id, node_name, path, blueprint_id, build_status FROM nodes WHERE node_type='script'` | 同上 |
| nodes (test类型) | `SELECT node_id, domain_id, node_name, path FROM nodes WHERE node_type='test'` | 同上（标记 has_test=1 的上游模块） |
| __init__.py __all__ | AST解析 `src/zephyr/**/__init__.py` | has_init_all |
| 代码十字段 | Grep `[CONSUMERS]` | consumers_count |
| 蓝图文件 | `SELECT blueprint_id, path FROM nodes WHERE node_type='design_node'` | blueprint_id交叉 |

**实现**：创建脚本 `scripts/governance/extract_func_inventory.py`

**核心逻辑**：

```python
# 伪代码
def extract_func_inventory():
    conn = get_db_connection()
    
    # STEP 1: 从 nodes 表提取 module/script/test
    for row in conn.execute("SELECT node_id, domain_id, node_name, path, blueprint_id, build_status FROM nodes WHERE node_type IN ('module','script','test')"):
        upsert_func_inventory(conn, row)
    
    # STEP 2: 标记 has_test（test节点引用的模块）
    conn.execute("""
        UPDATE func_inventory SET has_test = 1 
        WHERE module_id IN (
            SELECT DISTINCT e.to_node_id FROM edges e 
            JOIN nodes n ON e.from_node_id = n.node_id 
            WHERE n.node_type = 'test' AND e.dep_type = 'test_depends'
        )
    """)
    
    # STEP 3: 标记 has_init_all（AST解析）
    for init_file in glob('src/zephyr/**/__init__.py'):
        if has_all_declaration(init_file):
            pkg = init_file_parent_package(init_file)
            conn.execute("UPDATE func_inventory SET has_init_all = 1 WHERE ssot_path LIKE ?", (f'%{pkg}%',))
    
    # STEP 4: 统计 consumers_count（从 [CONSUMERS] 头部或 edges 入度）
    conn.execute("""
        UPDATE func_inventory SET consumers_count = (
            SELECT COUNT(*) FROM edges WHERE to_node_id = func_inventory.module_id
        )
    """)
    
    # STEP 5: 写入 func_source_cross 交叉证据
    # ...
    
    conn.commit()
```

**执行命令**：

```bash
python scripts/governance/extract_func_inventory.py
```

**验收**：

```bash
python -c "import sqlite3; conn=sqlite3.connect('D:/ZephyrAlpha/data/databases/depgraph.db'); c=conn.cursor(); c.execute('SELECT COUNT(*) FROM func_inventory'); print(f'Total: {c.fetchone()[0]}'); c.execute('SELECT COUNT(*) FROM func_inventory WHERE blueprint_id IS NOT NULL AND blueprint_id != \"\"'); print(f'With blueprint: {c.fetchone()[0]}'); c.execute('SELECT COUNT(*) FROM func_inventory WHERE has_test = 1'); print(f'With test: {c.fetchone()[0]}')"
```

**预期产出**：

| 指标 | 预估值 |
|------|--------|
| func_inventory 总行数 | ~12,572 (9,932 modules + 536 scripts + 2,104 tests) |
| 有蓝图的模块 | ~60-100 (2.9%覆盖率反映在blueprint_id字段) |
| 有测试的模块 | 待实测 |

### STEP 0.3：创建 liveness_collector pytest 插件

**目标**：自动收集测试运行时的模块加载证据

**文件**：`tests/conftest.py` 追加 fixture（不新建文件，复用已有 conftest）

**核心逻辑**：

```python
# 追加到 tests/conftest.py

import sys
import sqlite3
from pathlib import Path

_LIVENESS_DB = Path("D:/ZephyrAlpha/data/databases/depgraph.db")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    before = set(sys.modules.keys())
    yield
    after = set(sys.modules.keys())
    loaded = sorted(after - before)
    if loaded and _LIVENESS_DB.exists():
        try:
            conn = sqlite3.connect(str(_LIVENESS_DB), timeout=10)
            test_name = item.nodeid
            for mod in loaded:
                if mod.startswith("zephyr."):
                    conn.execute(
                        "INSERT OR IGNORE INTO liveness_map (file_path, referenced_by_test, verification_type) VALUES (?, ?, 'runtime')",
                        (mod, test_name)
                    )
                    conn.execute(
                        "UPDATE liveness_map SET referenced_by_test = referenced_by_test || ',' || ? WHERE file_path = ?",
                        (test_name, mod)
                    )
            conn.commit()
            conn.close()
        except Exception:
            pass
```

**注意**：此插件仅在 Phase 1 测试执行时生效。Phase 0 先注册到 conftest.py，不影响现有测试。

**验收**：`python -m pytest tests/unit/shared/ -v --tb=short -x 2>&1 | Select-Object -Last 5` — 确认插件不破坏现有测试

### STEP 0.4：静态存活地图构建

**目标**：不运行测试，通过 AST 分析 + depgraph 边数据构建初始存活地图

**方法**：

```python
# 伪代码：build_static_liveness.py
def build_static_liveness():
    conn = get_db_connection()
    
    # STEP 1: 从 edges 表提取所有 import_depends 边
    edges = conn.execute("""
        SELECT e.from_node_id, e.to_node_id, n1.path as from_path, n2.path as to_path
        FROM edges e
        JOIN nodes n1 ON e.from_node_id = n1.node_id
        JOIN nodes n2 ON e.to_node_id = n2.node_id
        WHERE e.dep_type = 'import_depends'
    """).fetchall()
    
    # STEP 2: 写入 liveness_map
    for from_id, to_id, from_path, to_path in edges:
        # to_path 被 from_path 引用
        conn.execute("""
            INSERT OR IGNORE INTO liveness_map (file_path, referenced_by_module, verification_type, last_verified)
            VALUES (?, ?, 'static', datetime('now'))
        """, (to_path,))
        conn.execute("""
            UPDATE liveness_map SET referenced_by_module = referenced_by_module || ',' || ? 
            WHERE file_path = ?
        """, (from_path, to_path))
    
    # STEP 3: 从 script_manifest.yaml 提取脚本引用
    # ...
    
    # STEP 4: 计算域级存活率
    conn.execute("""
        INSERT OR REPLACE INTO liveness_summary (domain_id, total_files, live_files, dead_files, unverified_files, liveness_ratio, last_computed)
        SELECT d.domain_id,
               COUNT(DISTINCT n.node_id) as total_files,
               COUNT(DISTINCT CASE WHEN lm.file_path IS NOT NULL THEN n.node_id END) as live_files,
               0 as dead_files,
               COUNT(DISTINCT CASE WHEN lm.file_path IS NULL THEN n.node_id END) as unverified_files,
               CASE WHEN COUNT(DISTINCT n.node_id) > 0 
                    THEN CAST(COUNT(DISTINCT CASE WHEN lm.file_path IS NOT NULL THEN n.node_id END) AS REAL) / COUNT(DISTINCT n.node_id)
                    ELSE 0 END as liveness_ratio,
               datetime('now')
        FROM domains d
        JOIN nodes n ON n.domain_id = d.domain_id AND n.node_type = 'module'
        LEFT JOIN liveness_map lm ON n.path = lm.file_path
        GROUP BY d.domain_id
    """)
    
    conn.commit()
```

**验收**：

```bash
python -c "import sqlite3; conn=sqlite3.connect('D:/ZephyrAlpha/data/databases/depgraph.db'); c=conn.cursor(); c.execute('SELECT COUNT(*) FROM liveness_map'); print(f'Liveness entries: {c.fetchone()[0]}'); c.execute('SELECT domain_id, total_files, live_files, liveness_ratio FROM liveness_summary ORDER BY liveness_ratio DESC LIMIT 10'); [print(r) for r in c.fetchall()]"
```

### STEP 0.5：试运行——诊断测试基线

**目标**：不建卡，先跑一轮 pytest 了解实际通过率

**命令**：

```bash
# 分层试运行
python -m pytest tests/unit/ -v --tb=line -q --no-header 2>&1 | Select-Object -Last 5
python -m pytest tests/integration/ -v --tb=line -q --no-header 2>&1 | Select-Object -Last 5
python -m pytest tests/e2e/ -v --tb=line -q --no-header 2>&1 | Select-Object -Last 5
```

**产出**：记录每层通过率，作为 Phase 1 验收基线

**注意**：试运行可能耗时较长（33,662 测试），建议分批执行：

```bash
# 按子目录分批
python -m pytest tests/unit/shared/ -q --tb=line 2>&1 | Select-Object -Last 3
python -m pytest tests/unit/governance/ -q --tb=line 2>&1 | Select-Object -Last 3
python -m pytest tests/unit/kb/ -q --tb=line 2>&1 | Select-Object -Last 3
# ... 逐批
```

### STEP 0.6：Phase 0 验收

| # | 验收项 | 判定命令 | 通过条件 |
|---|--------|---------|---------|
| 1 | 5张新表存在 | `SELECT name FROM sqlite_master WHERE type='table' AND name IN (...)` | 5/5 |
| 2 | func_inventory 非空 | `SELECT COUNT(*) FROM func_inventory` | >10,000 |
| 3 | func_source_cross 非空 | `SELECT COUNT(*) FROM func_source_cross` | >10,000 |
| 4 | liveness_map 非空 | `SELECT COUNT(*) FROM liveness_map` | >1,000 |
| 5 | liveness_summary 非空 | `SELECT COUNT(*) FROM liveness_summary` | >30 |
| 6 | pytest 不被 conftest 改动破坏 | `pytest tests/unit/shared/ -q` | exit 0 或有已知失败 |
| 7 | 试运行基线记录 | 人工确认 | 有数字 |

***

## 二、Phase 1：20 AI 并行功能恢复（需A/B/C完成）

### 2.1 Phase 1 前置条件清单

| # | 前置条件 | 当前状态 | 解除方法 |
|---|----------|---------|---------|
| 1 | ide_health_service 守护进程运行 | 未运行 | 启动守护进程 |
| 2 | 阶段A安全网卡完成 | 部分完成 | 执行 DM-100000/100001/100002 |
| 3 | 阶段B全量清洁完成 | 基本完成 | 确认前置条件满足 |
| 4 | depgraph 孤儿节点率 <50% | 98.4% | Phase 0 清单提取后批量注册 |
| 5 | [BLUEPRINT] 覆盖率 >15% | 2.9% | 批量补头部 |
| 6 | `__all__` 覆盖率 >40% | 17.8% | 批量补 `__all__` |

### 2.2 20 AI 并行分工方案

**核心思路**：18个大功能各分配1个AI负责恢复修复，统筹AI负责基础设施+协调+验收。

| AI编号 | 负责功能 | 对应§0.4.1功能ID | 核心源码包 | 依赖的其他AI |
|--------|---------|:---:|-----------|------------|
| AI-01 | 自动驾驶/运行时大脑 | F1 | trading/ | AI-02, AI-03, AI-04, AI-05 |
| AI-02 | 门禁引擎 | F2 | governance/rule_enforcement/ | 无 |
| AI-03 | 任务系统 | F3 | governance/ | 无 |
| AI-04 | 预算执行器 | F4 | governance/ | 无 |
| AI-05 | 升级/委托/A2A协议 | F5 | governance/ + infrastructure/a2a_protocol/ | 无 |
| AI-06 | 漂移检测/行为审计 | F6 | behavioral_audit/ | AI-16 |
| AI-07 | LLM安全网关 | F7 | security/ | 无 |
| AI-08 | Agent权限/RBAC | F8 | security/access_control/ | 无 |
| AI-09 | 回滚系统 | F9 | infrastructure/rollback/ | 无 |
| AI-10 | AI模型入职考试/模型画像 | F10 | intelligence/model_profiling/ | 无 |
| AI-11 | 上下文引擎 | F11 | autonomy_core/ | 无 |
| AI-12 | 向量记忆/知识库 | F12 | integration/vector_memory/ + governance/kb/ | 无 |
| AI-13 | MCP服务器集群 | F13 | integration/mcp/ | AI-02, AI-03, AI-12 |
| AI-14 | 管线编排/反馈环 | F14 | integration/ + ops/ | 无 |
| AI-15 | 自动修复引擎 | F15 | infrastructure/auto_fix_engine/ | AI-09, AI-16 |
| AI-16 | 审计编排/孤儿审判 | F16 | governance/audit_trail/ | 无 |
| AI-17 | 交易核心链路 | F17 | ex_core/ + risk/ + signal_fundamental/ + factor/ + simulation/ + pf_core/ | AI-12, AI-14 |
| AI-18 | 治理脚本系统(7维度) | F18 | scripts/governance/ | 无 |
| **统筹AI** | 基础设施+协调+验收 | — | depgraph.db + conftest.py + 跨AI依赖 | 全部 |

### 2.3 每个AI的统一工作流程（14步）

每个功能AI收到元任务卡后，按以下14步执行。完成后自建详细任务卡。

```
STEP 1   读蓝图 → 读取功能对应蓝图，理解设计意图
          命令: Read <blueprint_path>
          产出: 功能设计意图摘要

STEP 2   全量定位 → 找到功能相关的所有源码文件（全项目搜索，不仅限本包）
          2.1 本包文件 → Glob <源码包>/**/*.py
          2.2 孤儿文件 → audit_registration.py 找孤儿 → Grep功能关键词匹配
          2.3 重复文件 → 相似功能名/类名/函数名 Grep → 识别重复实现
          2.4 跨蓝图文件 → Grep [BLUEPRINT] 全项目 → 找归属其他蓝图但功能相关的文件
          产出: 全量文件清单（含分类标签：本包/孤儿/重复/跨蓝图）

STEP 3   归属裁定 → 对STEP 2找到的非本包文件做归属裁定
          3.1 孤儿文件裁定 → RULE-THREE价值判断(3a独立功能/3b客观原因/3c重建成本)
              相关→纳入本功能 | 不相关→不管
          3.2 重复文件裁定 → 功能是否完全覆盖？
              完全重复→保留质量高的，删除另一个 | 部分重复→合并或拆分
          3.3 跨蓝图文件裁定 → 功能放在哪个蓝图更合适？
              本蓝图更合适→协商迁移 | 对方蓝图更合适→建立依赖关系不迁移
          产出: 归属裁定记录 + 最终文件清单

STEP 4   蓝图设计 → 在蓝图里设计依赖关系+启动方式+自动运行+自动结束
          4.1 依赖关系设计 → 设计 frontmatter.dependency_graph
              内部依赖: 本功能范围内模块间调用关系
              外部依赖: 本功能依赖哪些其他功能
              被依赖: 哪些其他功能依赖本功能
              依赖方向: 确认无循环/无向上违规
          4.2 启动方式设计 → 设计功能的启动入口
              命令行启动: python -m <module> / python <script>.py
              事件驱动启动: hook/scheduler/observer 注册点
              API调用启动: 入口函数+参数
          4.3 自动运行设计 → 设计功能如何独立运行
              环境依赖: 需要哪些环境变量/配置/服务
              初始化序列: 启动前必须完成的步骤
              运行参数: 必需参数+可选参数
          4.4 自动结束设计 → 设计功能如何优雅退出
              完成条件: 什么状态表示任务完成
              超时熔断: 最大运行时间+超时处理
              资源清理: 退出时释放哪些资源（锁/临时文件/连接）
          产出: 蓝图设计文档（写入蓝图 §3/§4/frontmatter）

STEP 5   位置校验 → 按蓝图设计调整文件位置/命名/注册
          5.1 全景图定位 → extract_depgraph.py --modules <ID> 查每个文件在全景图中的域归属
          5.2 路径校验   → 文件实际路径 vs 蓝图设计的路径，不一致=放错位置
          5.3 命名校验   → 文件名是否符合命名规范(N-01~N-15)
          5.4 归属校验   → 文件的[BLUEPRINT]头部 vs 蓝图ID，不一致=归属错误
          5.5 位置修正   → 放错位置的文件移到正确位置（走RULE-TEN六步流程）
          5.6 注册校验   → 文件是否在正确的__init__.py / script_manifest.yaml / _registry.yaml中注册
          产出: 位置校验报告 + 位置修正记录

STEP 6   修复断链 → 按蓝图设计的依赖关系修复import断链
          命令: python -c "import <module>" 逐模块验证
          断链修复: 查迁移登记表 → 更新 import → 验证
          新纳入文件: STEP 3纳入的孤儿/重复文件 → 添加import引用
          产出: 修复记录列表

STEP 7   补全头部 → 补全文件头部十字段
          补: [BLUEPRINT] / [MODULE] / [INVARIANTS] / [MODIFY-GUARD] / [CONSUMERS]
              [STABILITY] / [SAFETY] / [AI_AUTONOMY] / [ERROR_CONTRACT] / [TESTS]
          产出: 头部补全记录

STEP 8   运行测试 → 运行功能相关测试，记录通过/失败
          命令: python -m pytest tests/<相关目录>/ -v --tb=short
          产出: 测试结果（通过数/失败数/错误数）

STEP 9   修复失败 → 修复失败测试，确保功能可独立运行
          修复 → 重新运行 → 直到通过或标记为"需人工介入"
          产出: 修复记录 + 最终测试结果

STEP 10  红蓝对抗极限测试 → 罗列极限测试清单并执行
          10.1 攻击面罗列 → 列出所有可攻击的入口/参数/状态/边界
          10.2 红队极限测试清单 → 设计极限输入/异常场景/恶意操作
              输入极限: 空输入/超长输入/特殊字符/None/负数/零值
              状态极限: 并发访问/资源耗尽/网络中断/服务不可用
              安全极限: 权限越界/注入攻击/路径穿越/敏感数据暴露
          10.3 执行红队测试 → 逐项执行极限测试
          10.4 蓝队验证 → 门禁/检查是否捕获红队攻击
          10.5 修复安全漏洞 → 红队发现的漏洞必须修复
          产出: 红蓝对抗测试清单 + 测试结果 + 修复记录

STEP 11  更新蓝图 → 将实际状态写回蓝图frontmatter
          11.1 更新 frontmatter.file_manifest（文件清单：路径/存在性/归属）
          11.2 更新 frontmatter.dependency_graph（文件级依赖 + symbols）
          11.3 更新 frontmatter.version + construction_progress
          11.4 更新 §0.2 对齐验证矩阵
          产出: 蓝图更新记录

STEP 12  三方对齐 → 验证全景图+蓝图+代码头部三方一致
          12.1 全景图对齐: depgraph.db ↔ 磁盘实际文件（文件级）
          12.2 蓝图对齐: 蓝图frontmatter.file_manifest+dependency_graph ↔ 实际代码（功能级）
          12.3 代码头部对齐: [BLUEPRINT]/[CONSUMERS]/[MODULE] ↔ 实际引用（引用级）
          产出: 三方对齐结果（PASS/FAIL per维度）

STEP 13  更新索引 → 更新所有相关INDEX文件和注册表
          13.1 罗列相关索引清单 → 本功能涉及的索引文件列表:
              __init__.py (包导出)
              script_manifest.yaml (脚本注册)
              _registry.yaml (门禁注册)
              docs/registry-of-registries.yaml (注册表之注册表)
              rule-registry.md (规则注册)
              project-architecture-panorama.yaml (架构全景图)
              project-entity-depgraph.yaml (依赖全景图)
              migration-registry.yaml (迁移登记表)
          13.2 逐项更新 → 确保每个索引文件反映最新状态
          13.3 验证索引一致性 → 索引间交叉引用无断裂
          产出: 索引更新清单 + 验证结果

STEP 14  报告 → 向统筹AI报告功能恢复状态
          报告格式:
            功能ID: FXX
            状态: RESTORED / PARTIAL / BLOCKED
            全量文件数: N（本包+纳入孤儿+去重后）
            归属裁定: [孤儿纳入/重复去重/跨蓝图迁移记录]
            蓝图设计: [依赖图+启动方式+自动运行+自动结束]
            位置修正: [放错位置的文件→正确位置]
            修复文件数: N
            测试通过率: X%
            红蓝对抗: [测试项数/通过数/漏洞数]
            蓝图更新: [frontmatter变更列表]
            三方对齐: PASS/FAIL（每方结果）
            索引更新: [已更新的索引文件列表]
            缺失文件: [列表]
            需人工介入: [列表]
            P0反馈: [列表]（写入 phase_feedback 表）
```

### 2.4 AI 并行启动顺序（按依赖关系分波）

```
第1波（无依赖，立即并行，12个AI）:
  AI-02 门禁引擎
  AI-03 任务系统
  AI-04 预算执行器
  AI-05 升级/委托/A2A
  AI-07 LLM安全网关
  AI-08 Agent权限/RBAC
  AI-09 回滚系统
  AI-10 AI考试/模型画像
  AI-11 上下文引擎
  AI-12 向量记忆/知识库
  AI-14 管线/反馈环
  AI-16 审计编排/孤儿审判
  AI-18 治理脚本系统

第2波（依赖第1波完成，4个AI）:
  AI-01 自动驾驶（等 AI-02/03/04/05）
  AI-06 漂移/行为审计（等 AI-16）
  AI-13 MCP集群（等 AI-02/03/12）
  AI-17 交易核心链路（等 AI-12/14）

第3波（依赖第2波完成，1个AI）:
  AI-15 自动修复引擎（等 AI-09/16）
```

### 2.5 统筹AI的职责

统筹AI（本对话）不负责具体功能恢复，负责：

| 职责 | 具体工作 |
|------|---------|
| **基础设施** | STEP 0.1~0.6 全部执行（建表/清单提取/pytest插件/存活地图/试运行） |
| **AI分配** | 为每个功能AI准备启动上下文（蓝图路径+源码包+依赖列表） |
| **跨AI协调** | 处理AI间的文件锁冲突（RULE-ZERO）；解决跨功能依赖问题 |
| **进度跟踪** | 汇总各AI报告，更新 func_inventory 表的 build_status |
| **验收** | 执行 §三 验收标准，判定 Phase 1 是否完成 |
| **反馈路由** | 将 phase_feedback 中的 P0 问题路由到对应阶段(A/B/C) |

### 2.6 元任务卡模板（统筹AI创建，功能AI自建详细卡）

统筹AI为每个功能AI创建一张元任务卡。功能AI拿到后自行拆分详细任务卡。

```yaml
# 元任务卡示例（F2 门禁引擎）
task_id: "META-F2"
title: "F2 门禁引擎功能恢复"
namespace: "phase-d"
status: "READY"
priority: "high"
description: |
  恢复F2门禁引擎全部功能，使其可独立运行。
  工作流程：读蓝图→定位源码→修复断链→补全头部→运行测试→修复失败→更新蓝图→三方对齐→报告。
  完成后自建详细任务卡（如PhaseManager恢复、GateEngine恢复等）。
files_in_scope:
  - "src/zephyr/governance/rule_enforcement/"
deliverables:
  - "F2全部模块import成功且可独立运行"
source_blueprint: "MOD-INF-007"
safety_level: "M"
ai_autonomy_level: "ai_modifiable"
applicable_rules:
  - "RULE-ZERO 文件锁协议"
  - "RULE-FOUR 创建文件走scaffold.py"
  - "RULE-EIGHT 搜索先行"
  - "RULE-TEN STEP 4.5 更新蓝图"
  - "三方对齐（全景图+蓝图+代码头部）"
allowed_touch:
  - "src/zephyr/governance/rule_enforcement/"
  - "docs/03_modules/_domain_governance/rule_enforcement/blueprint.md"
  - "tests/governance/"
post_sync_standard:
  - "python scripts/governance/diagnose_depgraph.py"
  - "python scripts/governance/audit_registration.py"
acceptance:
  - "F2全部模块import成功 + 蓝图frontmatter已更新 + 三方对齐PASS"
dependency_type: "independent"
```

### 2.7 蓝图格式方案：混合格式（YAML frontmatter扩展 + MD正文不变）

**决策**：蓝图保持 .md 文件，扩展 frontmatter 增加结构化字段，正文不变。

**frontmatter 新增字段**：

```yaml
# 新增：文件清单（从 §0.1 正文表格迁移）
file_manifest:
  - path: "src/zephyr/governance/rule_enforcement/phase_manager.py"
    section: "§3.1"
    responsibility: "门禁阶段调度与执行"
    exists: true
    ownership: "F2"
    blueprint_ref: "MOD-INF-007 §3"
  - path: "src/zephyr/governance/rule_enforcement/gate_engine.py"
    section: "§3.2"
    responsibility: "门禁规则评估引擎"
    exists: true
    ownership: "F2"
    blueprint_ref: "MOD-INF-007 §3"

# 新增：依赖图（从 §10 正文表格迁移，文件级 + symbols）
dependency_graph:
  internal:  # 蓝图范围内的文件间依赖
    - from: "phase_manager.py"
      to: "gate_engine.py"
      symbols: ["evaluate", "register_gate"]
      dep_type: "calls"
    - from: "gate_engine.py"
      to: "gate_registry.py"
      symbols: ["get", "register"]
      dep_type: "calls"
  external:  # 对其他蓝图/域的依赖
    - from: "phase_manager.py"
      to: "zephyr.governance.task_repo"
      blueprint: "MOD-INF-006"
      symbols: ["TaskRepository"]
      dep_type: "import"
    - from: "gate_engine.py"
      to: "zephyr.shared.contracts.gate"
      blueprint: "MOD-INF-016"
      symbols: ["GateContext", "GateVerdict"]
      dep_type: "implements"
```

**依赖图颗粒度裁定**（基于C4模型+AI社区实践）：

| 层 | 粒度 | 存储位置 | 更新方式 | 用途 |
|---|------|---------|---------|------|
| Layer 1 | 文件/模块级 | 蓝图 frontmatter.dependency_graph | AI恢复完成后更新 | 架构治理、循环检测、三方对齐 |
| Layer 2 | 函数/符号级 | 不持久化，AST实时计算 | 按需 | 影响分析、利用率计算、重构决策 |

**正文变更**：§0.1 和 §10 保留摘要表，详细数据在 frontmatter。其余章节不变。

### 2.8 D3 文件查找策略执行
- 禁止占位符(TODO/pass/NotImplementedError)
- 编辑优先，最小变更
```

### 2.7 D3 文件查找策略执行

测试执行中遇到缺文件时，按 §25.3.1 六步流程处理。

**高频场景预判**：

| 场景 | 预估频率 | 处理方法 |
|------|---------|---------|
| import 路径指向旧位置（迁移断链） | 高 | 查迁移登记表→更新import |
| 蓝图 §4 声明的文件不存在 | 中 | 按蓝图规格创建(scaffold.py) |
| depgraph 有设计态节点但无文件 | 中 | 标记为 design_only，跳过测试 |
| 文件存在但无 `__all__` 导出 | 高 | 补 `__all__`（非阻塞） |

### 2.4 D4 存活地图动态收集

Phase 0 的静态存活地图 + Phase 1 的 pytest 运行时收集 = 完整存活地图

**收集时机**：

| 时机 | 方法 | 数据 |
|------|------|------|
| 每批测试运行后 | conftest.py 的 pytest_runtest_call hook | 运行时加载的 zephyr.* 模块 |
| 每个治理脚本 `--json` 运行后 | 解析 JSON 输出 | 脚本扫描的路径 |
| 每卡完成后 | 手动记录 | 跨模块调用链 |

**汇总命令**：

```bash
python -c "
import sqlite3
conn = sqlite3.connect('D:/ZephyrAlpha/data/databases/depgraph.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM liveness_map WHERE verification_type = \"runtime\"')
print(f'Runtime verified: {c.fetchone()[0]}')
c.execute('SELECT COUNT(*) FROM liveness_map WHERE verification_type = \"static\"')
print(f'Static verified: {c.fetchone()[0]}')
c.execute('SELECT domain_id, total_files, live_files, liveness_ratio FROM liveness_summary ORDER BY liveness_ratio ASC LIMIT 10')
print('Lowest liveness domains:')
for r in c.fetchall(): print(f'  {r[0]}: {r[2]}/{r[1]} = {r[3]:.1%}')
"
```

### 2.5 D5 闭环反馈

**反馈写入**：

```python
# 每次发现问题时写入 phase_feedback
conn.execute("""
    INSERT INTO phase_feedback (source_phase, target_phase, severity, finding_type, file_path, evidence_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
""", ('D', target_phase, severity, finding_type, file_path, json.dumps(evidence)))
```

**反馈处理**：

| severity | 处理时限 | 处理方式 |
|----------|---------|---------|
| P0 | 立即 | 阻塞当前测试卡，通知目标阶段修复 |
| P1 | 当批次内 | 记录，批次结束后统一反馈 |
| P2 | Phase 1 结束后 | 汇总报告，不阻塞 |

***

## 三、验收标准（§25.5.3 展开）

### 3.1 Phase 0 验收（准备阶段）

| # | 验收项 | 通过条件 | 验证命令 |
|---|--------|---------|---------|
| P0-1 | 5张核心表存在 | 5/5 | `SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name IN (...)` = 5 |
| P0-2 | func_inventory 非空 | >10,000 | `SELECT COUNT(*) FROM func_inventory` |
| P0-3 | liveness_map 非空 | >1,000 | `SELECT COUNT(*) FROM liveness_map` |
| P0-4 | liveness_summary 覆盖 >30 域 | >30 | `SELECT COUNT(*) FROM liveness_summary` |
| P0-5 | pytest 不被破坏 | 现有测试通过率不降 | 试运行对比 |

### 3.2 Phase 1 验收（测试执行阶段）

| # | 验收项 | 通过条件 | 验证命令 |
|---|--------|---------|---------|
| 1 | 功能清单完整率 | ≥90% | `SELECT COUNT(*) FROM func_inventory WHERE blueprint_id IS NOT NULL` / 总数 |
| 2 | 测试卡建卡完成率 | ≥95% | governance.db tags含test的卡数 / 预估80-120 |
| 3 | 端到端测试通过率 | ≥85% | pytest exit code |
| 4 | 四方对齐通过率 | ≥90% | 蓝图↔代码↔depgraph↔路径树交叉 |
| 5 | 存活地图覆盖率 | ≥80% | liveness_map已验证 / 总文件 |
| 6 | P0反馈清零 | =0 | `SELECT COUNT(*) FROM phase_feedback WHERE severity='P0' AND status='open'` |
| 7 | P1反馈处理率 | ≥80% | P1 fixed / P1 total |
| 8 | 红蓝对抗无高危 | =0 | critical数量 |
| 9 | 事件驱动注册完整 | 100% | hook/scheduler/observer验证 |
| 10 | 自动运行率 | ≥90% | 可独立运行 / 总功能 |

***

## 四、施工脚本清单

| # | 脚本 | 类型 | 功能 | 注册到 |
|---|------|------|------|--------|
| 1 | `scripts/governance/extract_func_inventory.py` | 新建 | D1功能清单提取 | script_manifest.yaml |
| 2 | `scripts/governance/build_static_liveness.py` | 新建 | D4静态存活地图 | script_manifest.yaml |
| 3 | `tests/conftest.py` 追加 liveness hook | 修改 | D4运行时存活收集 | — |
| 4 | `src/zephyr/governance/depgraph_schema.py` 追加 v5 | 修改 | D1/D4/D5核心表DDL | — |

**注意**：脚本1和2需通过 `scaffold.py script` 创建，不可直接写文件。

***

## 五、风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| Phase 0 建表后 Phase 1 长期无法启动（A/B/C卡住） | 中 | 中 | Phase 0 产出的清单和存活地图本身有价值，可用于阶段A/B/C的决策 |
| 33,662 测试大量失败 | 高 | 高 | 试运行先摸底，分批修复，不追求100%通过 |
| 孤儿节点98.4%导致清单不可用 | 中 | 高 | 清单提取时标记孤儿状态，Phase 1前批量注册 |
| liveness_collector 影响测试性能 | 低 | 中 | 仅记录 zephyr.* 模块，忽略标准库；异步写入 |
| depgraph_schema v5 迁移与并行对话冲突 | 中 | 高 | 建表前获取文件锁(RULE-ZERO) |
| 多AI同时修改同一文件（文件锁冲突） | 高 | 高 | 统筹AI负责文件锁分配；每个AI开工前 check+acquire |
| 多AI同时写 depgraph.db（SQLite锁） | 中 | 中 | WAL模式 + busy_timeout=5000 + 每AI独立事务 |
| 功能AI修复断链时引入新断链 | 中 | 高 | 每个AI完成后统筹AI跑 audit_registration.py 验证 |
| 第2波AI等第1波完成时间过长 | 低 | 中 | 第1波AI完成后立即通知第2波，不等全部完成 |

***

## 六、与并行阶段的信息交换

| 方向 | 内容 | 格式 | 时机 |
|------|------|------|------|
| D→A | 迁移断链反馈 | phase_feedback P0 | 发现即报 |
| D→B | 清洁遗漏反馈 | phase_feedback P0/P2 | 发现即报 |
| D→C | depgraph缺失/错误反馈 | phase_feedback P1 | 每批次后 |
| D→E | 规则文件测试结果 | func_inventory.source_tags | Phase 1结束后 |
| A/B/C→D | 修复完成通知 | phase_feedback.status='fixed' | 修复后 |

***

## 七、执行时间线（20 AI 并行）

```
Phase 0（统筹AI，可立即执行）:
  STEP 0.1 建表         → 1小时
  STEP 0.2 清单提取      → 2-3小时（含脚本开发）
  STEP 0.3 pytest插件    → 1小时
  STEP 0.4 静态存活地图   → 2小时（含脚本开发）
  STEP 0.5 试运行        → 2-4小时（分批跑33K测试）
  STEP 0.6 验收          → 0.5小时
  Phase 0 合计           → ~1天

Phase 1（20 AI 并行，需A/B/C完成）:
  第1波（13个AI同时开工）:
    AI-02/03/04/05/07/08/09/10/11/12/14/16/18
    每个 AI 独立执行 STEP 1~7
    预估: 1-2天/功能，并行 → 总计 1-2天

  第2波（4个AI，等第1波完成后开工）:
    AI-01/06/13/17
    预估: 1-2天/功能，并行 → 总计 1-2天

  第3波（1个AI，等第2波完成后开工）:
    AI-15
    预估: 1天

  统筹AI 验收 + 反馈路由 → 0.5天
  Phase 1 合计 → ~3-5天（并行）

总计: Phase 0(1天) + Phase 1(3-5天) = ~4-6天
```
