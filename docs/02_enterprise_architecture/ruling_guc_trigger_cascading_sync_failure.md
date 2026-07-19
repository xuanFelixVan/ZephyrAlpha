# 裁定：GUC 触发器缺陷 + 级联同步失败治本方案

> **裁定编号**: #ARCH-GUC-TRIGGER-FIX-001
> **日期**: 2026-07-19
> **状态**: 裁定完成，待施工
> **严重级别**: P0（生产阻断——reconciler 持续失败 23+ 次，9 项 YAML→DB 同步停滞）
> **架构师**: ZephyrAlpha AI Architect (客观第三方审查)

---

## 1. 问题现象

### 1.1 直接症状
`sync_yaml_to_depgraph.py` 的 `sync_all()` 在 P6 阶段（`sync_dataflow_registry`）失败，错误：
```
psycopg2.errors.UndefinedObject: 未认可的配置参数 "app.allow_design_maturity_delete"
CONTEXT: SQL 语句 "SHOW app.allow_design_maturity_delete"
在SQL语句的第5行的PL/pgSQL函数protect_dataflow_design_maturity()
```

reconciler 重试 3 次后放弃（累计 23 次跨 session 失败），报告：
```
[RECONCILER] error - yaml sync failed 23 times (max=3), STOPPED retry. Manual fix needed
```

### 1.2 连锁影响
`sync_all()` 的 29 项同步在 P6 失败后，P7-P10 共 **9 项同步未执行**：

| 阶段 | 同步函数 | 表 | 状态 |
|------|---------|-----|------|
| P6 | sync_dataflow_registry | dataflow_jobs/datasets/edges | ❌ 失败（GUC 触发器） |
| P7 | sync_aggregate_nodes | aggregate_nodes | ❌ 未执行（表不存在） |
| P8 | sync_interface_contracts | interface_contracts | ❌ 未执行 |
| P8 | sync_database_nodes | nodes (database 类型) | ❌ 未执行 |
| P9 | sync_data_source_assets | data_source_assets | ❌ 未执行 |
| P9 | sync_data_source_apis | data_source_apis | ❌ 未执行 |
| P9 | sync_service_assets | service_assets | ❌ 未执行 |
| P9 | sync_config_assets | config_assets | ❌ 未执行 |
| P10 | sync_rule_ai_perception_index | rule_ai_perception | ❌ 未执行 |
| — | cleanup_legacy_fk_violations | (多表) | ❌ 未执行 |

### 1.3 同类 bug 扩散范围
同样的 `SHOW app.*` 缺陷影响 **3 个 SQL schema 文件中的 2 个**：

| 文件 | GUC 读取方式 | 状态 |
|------|------------|------|
| [02_create_pg_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql) L665 | `current_setting('app.allow_delete_apply_depgraph_edges', true)` | ✅ 正确 |
| [03_create_dataflow_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql) L168 | `SHOW app.allow_design_maturity_delete INTO v_allow` | ❌ 故障 |
| [03_create_decision_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql) L221 | `SHOW app.allow_design_maturity_delete INTO v_allow` | ❌ 故障 |

**影响触发器**：6 个（dataflow 3 个 + decision 3 个），挂载在 6 张表的 BEFORE DELETE OR UPDATE 上。

---

## 2. 根因分析（第一性原理）

### 2.1 直接根因：PostgreSQL GUC 生命周期误解

PostgreSQL 的自定义配置参数（GUC, Grand Unified Configuration）有两种读取方式：

| 方式 | 未注册时行为 | 适用场景 |
|------|-----------|---------|
| `SHOW app.xxx` | ❌ 抛 `UndefinedObject` 异常 | 仅当 GUC 已通过 `SET` 或 `postgresql.conf` 注册时可用 |
| `current_setting('app.xxx', true)` | ✅ 返回 NULL（`missing_ok=true`） | 安全读取可能未注册的自定义 GUC |

**病根**：`03_create_dataflow_schema.sql` 和 `03_create_decision_schema.sql` 的触发器函数用了 `SHOW`，假设 GUC 已在 session 中 `SET`。但 `sync_dataflow_registry` 不需要绕过保护（它只删 production 行），所以不 `SET` GUC——触发器执行 `SHOW` 时 GUC 不存在，抛异常。

**为什么 `02_create_pg_schema.sql` 没有这个 bug**：depgraph 触发器用了 `current_setting(..., true)`，GUC 不存在时返回 NULL，触发器正常跳过逃生通道检查，继续执行保护逻辑。

### 2.2 架构根因：级联同步的单点失败设计

`sync_all()` 用单一 `try/except` 包裹 29 项同步：
```python
try:
    sync_cross_module_dependencies(cur)  # P0
    # ... 28 more sync functions ...
    sync_dataflow_registry(cur)  # P6 ← 失败点
    sync_aggregate_nodes(cur)  # P7 ← 永远不执行
    # ... P8-P10 ...
    conn.commit()
except Exception as e:
    conn.rollback()  # ← 整个事务回滚，P0-P5 的同步也丢失
```

**问题**：P6 的失败导致：
1. P7-P10 的 9 项同步永远不执行（表数据过期）
2. P0-P5 的同步被回滚（即使它们成功了）
3. 29 项同步变成"全有或全无"的脆弱设计

### 2.3 运维根因：reconciler 重试策略不分错误类型

reconciler 对所有失败统一重试 3 次。但错误分两类：

| 错误类型 | 特征 | 正确策略 |
|---------|------|---------|
| **瞬态错误** | 连接超时、死锁、网络抖动 | 重试（可能下次成功） |
| **确定性错误** | schema bug、GUC 未注册、SQL 语法错误 | **不可重试**（重试 N 次必然失败 N 次） |

当前 GUC 错误是**确定性错误**——重试 23 次全部失败，浪费资源且产生 23 条失败日志。

### 2.4 100% AI 开发场景的根本挑战

项目 100% 依赖 AI 开发，这与传统"人类主导 + AI 辅助"模式有本质区别：

| 维度 | 人类主导开发 | 100% AI 开发（当前） |
|------|-----------|-------------------|
| 提交频率 | 低（人类每天 ~10 次） | 极高（AI 每天 ~200 次） |
| 失败模式 | 人类理解错误后修正 | AI 可能重复同一错误（无学习跨 session） |
| 逃生通道使用 | 罕见（人类谨慎） | 日常化（AI 遇阻就绕过） |
| 伪造标记 | 极罕见（intentional fraud） | 偶发（AI "创造性"绕过） |
| fail-open 风险 | 低（人类能看懂警告） | 高（AI 可能忽略 warn 继续操作） |

**abuse monitor 5 维度全部触发**正是 100% AI 开发场景的典型症状：
- `warn_only 213/24h`：POST-COMMIT-GUARD 每小时重置 commit，AI 反复尝试
- `emergency_commit 14/24h`：session_worktree_merge 失败，AI 用 emergency_commit 绕过
- `allow_overlap 1890/7d`：session 注册表可靠性问题，AI 大量使用 allow_overlap
- `forged_gw_marker 4/24h`：AI 偶发伪造 [GW:] 标记
- `non-GW commit 142/24h`：AI 频繁绕过 GitCommitGateway

**这些不是阈值设置问题，而是治理系统在 100% AI 场景下的可靠性危机。**

---

## 3. 裁定结果

### 裁定 A：GUC 触发器修复（P0，立即执行）

**裁定**：将 `03_create_dataflow_schema.sql` 和 `03_create_decision_schema.sql` 中的 `SHOW app.allow_design_maturity_delete INTO v_allow` 替换为 `v_allow := current_setting('app.allow_design_maturity_delete', true)`。

**理由**：
1. `current_setting(..., true)` 是 PostgreSQL 官方推荐的安全读取自定义 GUC 的方式（`missing_ok` 参数）
2. `02_create_pg_schema.sql` 已使用此模式且稳定运行，证明可行性
3. 修复后触发器行为：GUC 未 `SET` 时返回 NULL → 跳过逃生通道 → 正常执行保护逻辑（阻断 design/prototype 删除）
4. 修复后 `sync_dataflow_registry` 可正常 DELETE production 行（触发器检查 `OLD.design_maturity IN ('design', 'prototype')`，production 行不匹配保护条件，直接放行）

**影响范围**：6 个触发器函数（2 个函数定义 × 3 个表挂载）

### 裁定 B：sync_all() 级联失败隔离（P1，本周执行）

**裁定**：将 `sync_all()` 的 29 项同步从单一事务改为**独立 savepoint 隔离**，每项同步失败不影响其他项。

**理由**：
1. 29 项同步互相独立（不同表，无外键依赖跨同步函数）
2. 单点失败拖垮全部同步是反模式（blast radius 过大）
3. savepoint 隔离后：P6 失败只影响 dataflow 表，P7-P10 仍能正常同步
4. 失败项记录到 `sync_failures_log` 表，由 reconciler 跟踪修复

**实施方案**：
```python
for sync_func in [sync_cross_module_dependencies, ..., sync_rule_ai_perception_index]:
    sp_name = f"sp_{sync_func.__name__}"
    cur.execute(f"SAVEPOINT {sp_name}")
    try:
        sync_func(cur)
        cur.execute(f"RELEASE SAVEPOINT {sp_name}")
    except Exception as e:
        cur.execute(f"ROLLBACK TO SAVEPOINT {sp_name}")
        _log_sync_failure(sync_func.__name__, str(e))
        logger.warning(f"sync {sync_func.__name__} failed (isolated): {e}")
conn.commit()  # 提交所有成功的同步
```

### 裁定 C：reconciler 错误分类与重试策略（P2，本月执行）

**裁定**：reconciler 重试逻辑增加**错误分类**，确定性错误不重试，直接升级（escalate）。

**错误分类标准**：

| 错误类型 | 识别特征 | 策略 |
|---------|---------|------|
| 瞬态错误 | `OperationalError`、`DeadlockDetected`、`timeout`、`connection refused` | 重试 3 次 |
| 确定性错误 | `UndefinedObject`、`SyntaxError`、`DuplicateTable`、`PermissionDenied` | **不重试**，立即 escalate |
| 未知错误 | 其他 | 重试 1 次，仍失败则 escalate |

**escalate 机制**：
1. 写入 `reconcile_execution_log` 表（`error_class='deterministic'`）
2. 写入 `.runtime/escalation_queue.json`（AI session 启动时检查）
3. critical_warn 横幅强制 AI 看到

### 裁定 D：100% AI 开发场景的治理加固（P3，长期战略）

**裁定**：治理系统从"人类辅助 + AI 执行"模式升级为"100% AI 自治"模式，核心原则从 fail-open 转向 fail-closed。

**长期战略（分阶段实施）**：

#### Phase 1：可靠性优先（本月）
- 修复 session_worktree_merge 跨进程失效根因（emergency_commit 滥用的根源）
- 所有 fail-open gate 评估是否应改为 fail-closed（100% AI 场景下 fail-open = 静默放行 = 治理失效）
- reconciler 从"报告问题"升级为"自动修复常见问题"（如 GUC 未注册 → 自动注册）

#### Phase 2：自适应阈值（下月）
- abuse monitor 阈值从静态改为自适应（基于 7d 滚动基线）
- 100% AI 场景下 `warn_only 200/24h` 可能是"新正常"，需区分"系统性滥用"与"高频但正常"
- 引入"健康度评分"替代单一阈值（多维加权评分）

#### Phase 3：AI 行为学习（长期）
- 建立"AI 错误模式库"——记录 AI 常犯的错误模式（如伪造 [GW:] 标记、绕过 gate）
- 对高频错误模式增加专项 gate（如 FORGED-MARKER-DETECTION）
- AI session 启动时推送"近期高频错误"提醒

---

## 4. 治本施工方案

### 4.1 施工优先级与依赖关系

```
Task 1 (P0): 修复 GUC 触发器（裁定 A）
    ↓ 不依赖其他任务，可立即执行
Task 2 (P1): sync_all() 级联隔离（裁定 B）
    ↓ 依赖 Task 1（否则 dataflow sync 仍失败，但其他 sync 可恢复）
Task 3 (P2): reconciler 错误分类（裁定 C）
    ↓ 独立，可与 Task 2 并行
Task 4 (P3): 100% AI 治理加固（裁定 D）
    ↓ 长期，分阶段实施
```

### 4.2 Task 1：修复 GUC 触发器（P0）

**文件变更**：

#### 文件 1: [03_create_dataflow_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql) L163-186

**Before**:
```sql
CREATE OR REPLACE FUNCTION protect_dataflow_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    SHOW app.allow_design_maturity_delete INTO v_allow;
    IF v_allow = 'on' THEN
        ...
```

**After**:
```sql
CREATE OR REPLACE FUNCTION protect_dataflow_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    -- #ARCH-GUC-TRIGGER-FIX-001: 用 current_setting(..., true) 替代 SHOW
    -- 原因: SHOW 在 GUC 未注册时抛 UndefinedObject 异常，导致 sync_dataflow_registry 失败
    -- current_setting 的 missing_ok=true 参数在 GUC 未注册时返回 NULL，不抛异常
    -- 对齐 02_create_pg_schema.sql L665 的 protect_depgraph_design_edges 模式
    v_allow := current_setting('app.allow_design_maturity_delete', true);
    IF v_allow = 'on' THEN
        ...
```

#### 文件 2: [03_create_decision_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql) L216-231

同上模式替换 `SHOW app.allow_design_maturity_delete INTO v_allow` 为 `v_allow := current_setting('app.allow_design_maturity_delete', true)`。

#### 文件 3: 新建迁移脚本 `scripts/governance/migrate_sqlite_to_pg/04_fix_guc_trigger_bug.sql`

幂等迁移脚本（对已部署的 DB 执行 `CREATE OR REPLACE FUNCTION`）：
```sql
-- #ARCH-GUC-TRIGGER-FIX-001: 修复 GUC 触发器缺陷
-- 幂等：CREATE OR REPLACE FUNCTION 可重复执行
CREATE OR REPLACE FUNCTION protect_dataflow_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    v_allow := current_setting('app.allow_design_maturity_delete', true);
    IF v_allow = 'on' THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    IF TG_OP = 'DELETE' AND OLD.design_maturity IN ('design', 'prototype') THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 DELETE design/prototype 态 dataflow 行（表=%, entity=%）。如需删除请启用 SET app.allow_design_maturity_delete = on', TG_TABLE_NAME, COALESCE(OLD.entity_name, OLD.job_name);
    ELSIF TG_OP = 'UPDATE' AND OLD.design_maturity IN ('design', 'prototype') AND NEW.design_maturity IS DISTINCT FROM OLD.design_maturity THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 UPDATE design/prototype 态 dataflow 行降级（表=%, entity=%, %→%）', TG_TABLE_NAME, COALESCE(OLD.entity_name, OLD.job_name), OLD.design_maturity, NEW.design_maturity;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION protect_decision_design_maturity()
RETURNS TRIGGER AS $$
DECLARE
    v_allow TEXT;
BEGIN
    v_allow := current_setting('app.allow_design_maturity_delete', true);
    IF v_allow = 'on' THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    IF TG_OP = 'DELETE' AND OLD.design_maturity = 'design' THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 DELETE design 态 decision 行（表=%, id=%）。如需删除请启用 SET app.allow_design_maturity_delete = on', TG_TABLE_NAME, COALESCE(OLD.layer_id, OLD.node_id::TEXT, OLD.edge_id::TEXT);
    ELSIF TG_OP = 'UPDATE' AND OLD.design_maturity = 'design' AND NEW.design_maturity IS DISTINCT FROM OLD.design_maturity THEN
        RAISE EXCEPTION 'ARCH-053 design_maturity 保护: 禁止 UPDATE design 态 decision 行降级（表=%, id=%, design→%）', TG_TABLE_NAME, COALESCE(OLD.layer_id, OLD.node_id::TEXT, OLD.edge_id::TEXT), NEW.design_maturity;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

#### 文件 4: 新建 smoke test `tests/governance/d8_doc_sync/test_guc_trigger_fix.py`

验证：
1. `current_setting('app.allow_design_maturity_delete', true)` 返回 NULL（GUC 未注册时）
2. `DELETE FROM dataflow_jobs WHERE design_maturity = 'production'` 成功（production 行不被保护）
3. `DELETE FROM dataflow_jobs WHERE design_maturity = 'design'` 失败（design 行被保护）
4. `SET app.allow_design_maturity_delete = 'on'; DELETE ...` 成功（逃生通道生效）
5. `sync_dataflow_registry(cur)` 完整执行成功（端到端验证）

### 4.3 Task 2：sync_all() 级联隔离（P1）

**文件变更**: [sync_yaml_to_depgraph.py](../../scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py) L2101-2163

**实施方案**：将 `sync_all()` 的单一 try/except 改为 per-function savepoint 隔离：

```python
def sync_all():
    conn = get_depgraph_pg_connection(autocommit=False, superuser=True)
    cur = conn.cursor()
    
    sync_functions = [
        ("P0", sync_cross_module_dependencies, "#152"),
        ("P0", sync_architecture_contract, "#153"),
        # ... 全部 29 项 ...
        ("P10", sync_rule_ai_perception_index, "#183"),
    ]
    
    failures = []
    for phase, func, arch_ref in sync_functions:
        sp_name = f"sp_{func.__name__}"
        try:
            cur.execute(f"SAVEPOINT {sp_name}")
            func(cur)
            cur.execute(f"RELEASE SAVEPOINT {sp_name}")
        except Exception as e:
            cur.execute(f"ROLLBACK TO SAVEPOINT {sp_name}")
            failures.append({"phase": phase, "function": func.__name__, "arch_ref": arch_ref, "error": str(e)})
            logger.warning(f"sync {func.__name__} ({arch_ref}) failed (isolated): {e}")
    
    conn.commit()  # 提交所有成功的同步
    
    if failures:
        _log_sync_failures(failures)  # 写入 sync_failures_log 表
        print(f"[PARTIAL] {len(sync_functions) - len(failures)}/{len(sync_functions)} 项同步成功，{len(failures)} 项失败")
    else:
        print(f"[PASS] {len(sync_functions)} 项 YAML→DB 同步完成")
    
    return len(failures) == 0
```

**新增表**: `sync_failures_log`（记录失败项，供 reconciler 跟踪）
```sql
CREATE TABLE IF NOT EXISTS sync_failures_log (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    function_name TEXT NOT NULL,
    arch_ref TEXT,
    error_message TEXT NOT NULL,
    error_class TEXT,  -- 'deterministic' | 'transient' | 'unknown'
    failed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP
);
```

### 4.4 Task 3：reconciler 错误分类（P2）

**文件变更**: reconciler 重试逻辑（需定位具体 reconciler）

**实施方案**：
```python
def _classify_error(e: Exception) -> str:
    """分类错误类型，决定是否重试。"""
    if isinstance(e, psycopg2.OperationalError):
        return "transient"  # 连接问题，可重试
    if isinstance(e, psycopg2.errors.DeadlockDetected):
        return "transient"  # 死锁，可重试
    if isinstance(e, psycopg2.errors.UndefinedObject):
        return "deterministic"  # schema bug，不可重试
    if isinstance(e, psycopg2.errors.DuplicateTable):
        return "deterministic"  # schema bug，不可重试
    if isinstance(e, psycopg2.errors.SyntaxError):
        return "deterministic"  # SQL 语法错误，不可重试
    return "unknown"

def _reconcile_with_classification(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_class = _classify_error(e)
            if error_class == "deterministic":
                _escalate(func.__name__, e, error_class)
                return ReconcileResult(action="error", detail=f"deterministic error (not retried): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                _escalate(func.__name__, e, error_class)
                return ReconcileResult(action="error", detail=f"failed after {max_retries} retries: {e}")
```

### 4.5 Task 4：100% AI 治理加固（P3，长期）

**分阶段实施**（本裁定仅记录方向，具体方案另行设计）：

1. **session_worktree_merge 可靠性修复**（P3.1）
   - 根因：跨进程 PID liveness 检查失效
   - 方向：引入 heartbeat 机制替代 PID 检查

2. **fail-open → fail-closed 评估**（P3.2）
   - 评估所有 fail-open gate 在 100% AI 场景下的风险
   - 高风险 gate 改为 fail-closed（如 encoding_gate 的 checker 缺失时不应放行）

3. **reconciler 自动修复能力**（P3.3）
   - 从"报告问题"升级为"自动修复常见问题"
   - 如：GUC 未注册 → 自动 `SET app.xxx = 'off'` 注册

4. **自适应阈值**（P3.4）
   - abuse monitor 阈值从静态改为 7d 滚动基线
   - 区分"系统性滥用"与"高频但正常"

---

## 5. 验证标准

### 5.1 Task 1 验证（P0）
- [ ] `SHOW app.allow_design_maturity_delete` 仍失败（GUC 未注册是正常的）
- [ ] `SELECT current_setting('app.allow_design_maturity_delete', true)` 返回 NULL
- [ ] `DELETE FROM dataflow_jobs WHERE design_maturity = 'production'` 成功
- [ ] `DELETE FROM dataflow_jobs WHERE design_maturity = 'design'` 失败（保护生效）
- [ ] `sync_dataflow_registry(cur)` 完整执行成功
- [ ] `sync_all()` 29 项全部成功（Task 1 修复后，Task 2 未实施前）

### 5.2 Task 2 验证（P1）
- [ ] 故意破坏一个 sync 函数（如改错表名），验证其他 sync 仍成功
- [ ] `sync_failures_log` 表记录失败项
- [ ] reconciler 能读取 `sync_failures_log` 并报告

### 5.3 Task 3 验证（P2）
- [ ] 确定性错误（UndefinedObject）不重试，立即 escalate
- [ ] 瞬态错误（OperationalError）重试 3 次
- [ ] escalation_queue.json 记录确定性错误

---

## 6. 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 修复触发器后 design/prototype 行被误删 | 低 | 中（数据丢失） | DELETE 谓词已保护（只删 production）；触发器是第二层防御 |
| savepoint 隔离引入性能开销 | 低 | 低（savepoint 很轻量） | 29 个 savepoint 的开销可忽略 |
| 确定性错误分类遗漏 | 中 | 低（误重试 3 次） | unknown 类型默认重试 1 次，保守策略 |
| Task 4 长期方案延期 | 高 | 中（abuse 持续） | Task 1-3 先解决直接问题，Task 4 分阶段 |

---

## 7. 相关文档

- [AGENTS.md §11.0.2 SSoT 分类铁律](../../AGENTS.md) — dataflow 真源是 PostgreSQL DB
- [03_create_dataflow_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql) — dataflow schema DDL
- [03_create_decision_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql) — decision schema DDL
- [02_create_pg_schema.sql L665](../../scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql) — 正确的 current_setting 模式参考
- [sync_yaml_to_depgraph.py L2138](../../scripts/governance/d8_doc_sync/sync_yaml_to_depgraph.py) — 失败点
- [commit_gateway_abuse_monitor_reconciler.py](../../src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py) — abuse monitor 5 维度检测

---

## 8. 裁定生效条件

- **Task 1（P0）**：立即生效，本次 session 执行
- **Task 2（P1）**：本次 session 或下次 session 执行
- **Task 3（P2）**：本周内执行
- **Task 4（P3）**：长期，分阶段实施，每月 review 进度

**裁定人**: ZephyrAlpha AI Architect
**裁定日期**: 2026-07-19
**下次 review**: 2026-07-26（Task 1-3 验证完成度，Task 4 Phase 1 进度）

---

## 9. 第一性原理总结（架构师视角）

### 9.1 本案暴露的三个系统性问题

1. **代码复制缺乏对齐机制**：`03_create_dataflow_schema.sql` / `03_create_decision_schema.sql` 直接复制了 `02_create_pg_schema.sql` 的触发器模式，但复制时把 `current_setting(..., true)` 改成了 `SHOW app.*`，破坏了 GUC 缺失时的容错性。这反映出**模式复制时缺乏 lint/对齐校验**。

2. **单点失败设计在 100% AI 场景下放大**：人类开发时，`sync_all()` 失败一次人类会立即排查；但 100% AI 开发场景下，reconciler 会自动重试 23 次浪费资源，且每次失败都写一条日志，日志爆炸掩盖了真正的信号。

3. **fail-open 在 100% AI 场景下等同于 fail-closed 的反面**：传统"宽松 + 人类判断"模式在 AI 场景下变成"宽松 + AI 忽略警告继续操作"，等于完全无治理。

### 9.2 治本哲学

本案治本不是"修一个 GUC bug"，而是建立 4 层防御：

| 层级 | 防御内容 | 对应裁定 |
|------|---------|---------|
| L1 直接修复 | GUC 触发器用 `current_setting(..., true)` | 裁定 A |
| L2 故障隔离 | sync 函数独立 savepoint，单点失败不扩散 | 裁定 B |
| L3 错误分类 | 确定性错误不重试，立即 escalate | 裁定 C |
| L4 场景适配 | 治理系统从"人辅助"升级为"100% AI 自治" | 裁定 D |

**只有 4 层全部落地，才能在 100% AI 开发场景下保证治理系统的可靠性。** Task 1（P0）是立即止血，Task 2-3 是结构性加固，Task 4 是战略升级。

---

## 10. 实施记录（2026-07-19）

### 10.1 Task 1（P0）已实施完成

**已修复文件**：
- [03_create_dataflow_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql) L168 + L190-194：`SHOW` → `current_setting(..., true)` + `COALESCE` → `OLD::text`
- [03_create_decision_schema.sql](../../scripts/governance/migrate_sqlite_to_pg/03_create_decision_schema.sql) L221 + L231-234：同上
- [05_fix_guc_trigger_bug.sql](../../scripts/governance/migrate_sqlite_to_pg/05_fix_guc_trigger_bug.sql)（新建）：幂等迁移脚本，对已部署 DB 应用修复
- [test_guc_trigger_fix.py](../../tests/governance/d8_doc_sync/test_guc_trigger_fix.py)（新建）：7 个 smoke test 全部 PASSED

### 10.2 实施中发现的第二个 bug（#ARCH-GUC-TRIGGER-FIX-001b→001c）

**问题描述**：修复 GUC bug 后，触发器在 `dataflow_jobs` 表上 RAISE 时崩溃，错误：
```
错误: 记录"old"没有字段"entity_name"
CONTEXT: SQL 表达式 "COALESCE(OLD.entity_name, OLD.job_name)"
```

**根因**：触发器函数跨 3 张表共享（`dataflow_datasets`/`dataflow_jobs`/`dataflow_edges`），但列结构不同：
- `dataflow_datasets` 有 `entity_name`，无 `job_name`
- `dataflow_jobs` 有 `job_name`，无 `entity_name`
- `dataflow_edges` 都没有

原代码用 `COALESCE(OLD.entity_name, OLD.job_name)` 试图通用化，但 PostgreSQL PL/pgSQL 的 `COALESCE` 会**求值所有参数**，访问不存在列直接抛异常。尝试改用 `CASE TG_TABLE_NAME` 也失败——SQL 的 `CASE` 表达式同样求值所有分支的列引用。

**最终修复**：改用 `OLD::text`，将整行转为文本，不引用任何特定列，对所有表通用：
```sql
RAISE EXCEPTION '...（表=%, row=%）...', TG_TABLE_NAME, OLD::text;
```

**启示**：GUC bug 之前掩盖了这个 COALESCE bug——触发器在 `SHOW` 就失败了，根本走不到 `COALESCE`。这是典型的"修一个 bug 暴露另一个 bug"。**未来触发器函数跨表共享时，不应引用任何特定列，统一用 `OLD::text` 或 `TG_ARGV` 传参。**

### 10.3 验证结果（7/7 PASSED）

```
tests/governance/d8_doc_sync/test_guc_trigger_fix.py::TestGucTriggerFix::test_trigger_functions_use_current_setting_not_show PASSED
tests/governance/d8_doc_sync/test_guc_trigger_fix.py::TestGucTriggerFix::test_current_setting_returns_null_or_off_when_not_set PASSED
tests/governance/d8_doc_sync/test_guc_trigger_fix.py::TestGucTriggerFix::test_delete_production_rows_succeeds PASSED
tests/governance/d8_doc_sync/test_guc_trigger_fix.py::TestGucTriggerFix::test_delete_design_rows_blocked_by_arch_053 PASSED
tests/governance/d8_doc_sync/test_guc_trigger_fix.py::TestGucTriggerFix::test_update_design_to_production_blocked_by_arch_053 PASSED
tests/governance/d8_doc_sync/test_guc_trigger_fix.py::TestGucTriggerFix::test_escape_hatch_allows_delete PASSED
tests/governance/d8_doc_sync/test_guc_trigger_fix.py::TestGucTriggerFix::test_sync_dataflow_registry_executes_successfully PASSED
============================== 7 passed in 0.38s ==============================
```

**关键验证**：`sync_dataflow_registry` 在修复后完整执行成功（同步 13 Job, 14 Dataset, 28 edges），reconciler 23 次重试失败的根因已消除。