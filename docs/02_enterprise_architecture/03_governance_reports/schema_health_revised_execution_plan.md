---
ttl: permanent
doc_type: construction_plan
---

# Schema 健康度治本方案：修订执行计划（v2）

> **文档定位**：本计划是对 `schema_health_root_cure_plan.md`（v1）的**修订执行版**。v1 的 6 层调研报告（事实层/根因/行业基准/裁定）仍然有效，本文件聚焦"剩余施工"，并修正 v1 在事实复核中暴露的 5 处判定错误。
> **修订日期**：2026-06-26
> **触发原因**：上下文丢失后重新进入 Plan Mode，对 v1 已批准计划做事实复核（循环审查），发现 5 处与代码/DB 现状不符的事实错误。按用户要求"循环审查文档是否有前后冲突的地方，至到文档问题=0"，必须修正后才能施工。
> **适用语境**：100% AI 开发项目；客观专业架构师独立裁定（用户授权"判断价值，是否删除，还是混合"）。

---

## 0. 与 v1 的关系：5 处事实修正

复核方法：直接读 `depgraph_schema.py`、`sync_yaml_to_depgraph.py`、`auto_runner.py`、`depgraph_reader.py` 真源 + DB 实测 + 全量 grep 读者。**v1 的 P0 裁定（contracts 漂移 / gates 写入断裂 / gen_depgraph 残留）全部成立且有效**；P2 死表清理部分有事实错误，修订如下：

| # | v1 判定 | 复核真相 | 修订裁定 |
|---|---------|----------|----------|
| C1 | cross_registry_rules"无 sync 函数 / 0% 填充 / 永远空表"→ 标注 deprecated | **有 sync 函数** `sync_registry_of_registries()`（sync_yaml_to_depgraph.py:608，在 sync_all L1035 被调用，L641 INSERT）；DB 实测 **6 行**=YAML `registry_of_registries.yaml` 的 6 条 CR 规则；且在 `READONLY_TABLES` 受只读触发器保护 | **KEEP**（健康的只读缓存表，非 deprecated） |
| C2 | governance_audit_logs"假审计"→ 删除 + 移除 auto_runner 写入路径 | auto_runner 是 **production 级**模块，`_write_audit_log`（L194）在 `_auto_close`（L184）被调用，`audit_logged` 是 `success` 契约的一部分（L60）。迁移目标 v1 误标为 `data/audit-trail/events.jsonl`，**实际 WORM 审计基础设施是 `src/zephyr/audit-trail/` 模块**（writer/signer/integrity），迁移是独立大任务 | **KEEP 本轮**（避免破坏 production 组件的 success 契约；迁移至 audit-trail 模块列为后续独立任务） |
| C3 | verify_schema_health.py 放 `d7_code/` 目录，DDL 引用 `_DDL_NODES_V5` 等 | `d7_code/` 目录**不存在**；verify 脚本惯例是 `scripts/governance/verify_*.py` 顶层（verify_audit_integrity.py 等）。v1 migration（L632）用 `_DDL_NODES`/`_DDL_EDGES`/`_DDL_ARCH_DIRECTORY_TREE`（非 `_V5`），这些是当前真源；`_V5` 变体是旧快照 | 放 `scripts/governance/verify_schema_health.py`；DDL 映射全部用非 `_V5` 常量 |
| C4 | v14 删除 4 张表（含 governance_audit_logs） | governance_audit_logs KEEP（见 C2），cross_registry_rules KEEP（见 C1） | v14 删除 **3 张**表：arch_bottlenecks / arch_layers / invariants |
| C5 | verify 脚本 ddl_map 含全部表 | 删除的 3 张表若仍在 ddl_map 会报假阳性 `[DDL-DRIFT] 表不存在` | ddl_map 只含**保留表**（19 张），删除的 3 张不入映射 |

---

## 1. 当前状态核实（实测，非引用 v1）

| 阶段 | 状态 | 证据 |
|------|------|------|
| 阶段0 备份 | ✓ HEAD=`6d68fcb8` 已记录 | `git rev-parse HEAD` = 6d68fcb8 |
| 阶段1 contracts 漂移(#ARCH-008) | ✓ 已完成 | depgraph_schema.py:204 `_DDL_CONTRACTS` 含 13 列；L920 migration v13；DB `PRAGMA table_info(contracts)`=13 列、380 行 |
| 阶段2 gates.event_driven(#ARCH-009) | ✓ 已完成 | sync_yaml_to_depgraph.py:311-313 写 11 列 + 11 个 `?`；DB gates=129 行 |
| 阶段3 gen_depgraph(#ARCH-010) | ✗ 未完成 | generate_project_depgraph.py 仍有 3 处 `module_lifecycle_state`：L2673 / L2692 / L2721 |
| 阶段4 删表 | ✗ 未开始 | DB 实测：arch_bottlenecks=3 行、arch_layers=4 行、invariants=255 行、cross_registry_rules=6 行、governance_audit_logs=67 行 |
| 阶段5 verify 脚本 | ✗ 未开始 | `scripts/governance/verify_schema_health.py` 不存在 |
| 阶段6 注册门禁 | ✗ 未开始 | `.pre-commit-config.yaml` 无 gate-schema-health |
| 阶段7 同步文档 | ✗ 未开始 | panorama 文档仍列旧表、旧列数 |

**DB schema_version 复核**：`SELECT COALESCE(MAX(version),0) FROM _schema_version` 应为 13（v13 已跑）。contracts 表 13 列印证 v13 生效。

---

## 2. 修订裁定汇总表

| #ARCH | 对象 | v1 裁定 | v2 修订裁定 | 阶段 | 优先级 |
|-------|------|---------|-------------|------|--------|
| #ARCH-008 | contracts | 修复 DDL + v13 | （已完成，不变） | 1 | P0 |
| #ARCH-009 | gates.event_driven | 修复 sync | （已完成，不变） | 2 | P0 |
| #ARCH-010 | generate_project_depgraph.py | 清理残留 INSERT | （不变） | 3 | P0 |
| #ARCH-011 | cross_registry_rules | 标注 deprecated | **KEEP**（健康缓存，撤回 deprecated） | — | — |
| #ARCH-012 | governance_audit_logs | 删除 + 迁移 auto_runner | **KEEP 本轮**（迁移至 audit-trail 模块列为后续任务） | — | — |
| #ARCH-013 | arch_layers | 删除 + 清理 reader | 删除 + 移除 depgraph_reader.get_architecture_layers 方法 | 4 | P1 |
| #ARCH-014 | arch_bottlenecks | 删除 | （不变）删除 | 4 | P2 |
| #ARCH-015 | invariants | 删除 DB 表 | （不变）删除 DB 表 + 清理 apply_depgraph/create_d_signal_rename_tasks 引用 + 测试 | 4 | P1 |
| #ARCH-016 | verify_schema_health.py | 新建门禁 | 新建（修正 DDL 常量引用 + 路径 + ddl_map） | 5 | P0 |
| #ARCH-017 | .pre-commit-config.yaml | 注册 GATE-SCHEMA-HEALTH | （不变，修正脚本路径） | 6 | P0 |
| #ARCH-018 | 文档同步 | 同步 | 同步（移除 3 张已删表、保留 2 张 KEEP 表、更新列数） | 7 | P1 |

**修订净影响**：v1 删 4 表 + 废 1 表；v2 删 3 表 + KEEP 2 表。降低破坏 production 组件（auto_runner）的风险，撤回对健康缓存表（cross_registry_rules）的错误 deprecated 标注。

---

## 3. 剩余施工方案（动作级）

### 施工总原则
1. **备份先行**：HEAD `6d68fcb8` 已记录为回滚锚点
2. **DDL 真源优先**：结构变更先改 `depgraph_schema.py` 的 `_DDL_*` + migration，再改写入代码
3. **一次一个动作**：每动作独立可验证、可回滚
4. **GitCommitGateway 提交**：禁止裸 git commit（HARD CONSTRAINT）

---

### 阶段3：修复 generate_project_depgraph.py（#ARCH-010）

**动作3.1**：读取 `scripts/governance/generate_project_depgraph.py` 的 L2660-2730 区域，定位 3 处 `module_lifecycle_state` 引用：
- L2673：`type_specific` keys 列表中的 `"module_lifecycle_state"`
- L2692：INSERT 列名列表中的 `module_lifecycle_state`
- L2721：VALUES 元组中的 `node.get("module_lifecycle_state", "")`

**编辑**：删除这三处引用。删除后 INSERT 应为 28 列 + 28 个 `?` + VALUES 28 个值（三者计数必须一致）。

**动作3.2**：验证生成器可运行
```bash
python scripts/governance/generate_project_depgraph.py --dry-run
```
**验证**：无 `sqlite3.OperationalError: no such column: module_lifecycle_state`
**回滚**：`git checkout -- scripts/governance/generate_project_depgraph.py`

---

### 阶段4：删除 3 张死表（#ARCH-013/014/015）

> 删除 arch_bottlenecks（真死表）、arch_layers（仅 1 个无生产调用者的 reader 方法）、invariants（DB 255 行 vs YAML 20 条已漂移，无 src 读取者）。**保留** cross_registry_rules、governance_audit_logs（见 §0 C1/C2）。

**动作4.1**：在 `src/zephyr/governance/depgraph_schema.py` 的 `_MIGRATIONS` 列表（v13 之后、`]` 之前）添加 migration v14
```python
    (
        14,
        "v14: Drop 3 dead/drifted tables (arch_bottlenecks/arch_layers/invariants) — fix #ARCH-013~015. "
        "KEEP cross_registry_rules (healthy sync) and governance_audit_logs (auto_runner active writer).",
        [
            "DROP TABLE IF EXISTS arch_bottlenecks",
            "DROP TABLE IF EXISTS arch_layers",
            "DROP TABLE IF EXISTS invariants",
        ],
    ),
```

**动作4.2**：移除已删表的 DDL 声明与 v1 引用
- 移除 `_DDL_ARCH_BOTTLENECKS`（L256-268 区域）
- 移除 `_DDL_ARCH_LAYERS`（L300-308 区域）
- 移除 `_DDL_INVARIANTS`（L226-234 区域）
- 从 v1 migration 语句列表（L632-644 区域）移除 `_DDL_ARCH_BOTTLENECKS`、`_DDL_ARCH_LAYERS`、`_DDL_INVARIANTS` 三行引用 → fresh clone 不再创建这 3 张表
- 更新文件头部注释（L26-39 表清单）：移除 arch_bottlenecks/arch_layers/invariants 的编号项，并修正表总数与注释

**动作4.3**：清理读取已删表的代码
- `src/zephyr/governance/depgraph_reader.py`：移除 `get_architecture_layers` 方法（L201-205 区域，SELECT * FROM arch_layers 的唯一 reader；已确认无生产调用者）
- `scripts/governance/apply_depgraph.py`：从改名扫描元组列表中移除含 `"invariants"` 的条目（L1550 区域 `(11, "invariants", "domain_id", False)`）—— 表已删，扫描会报错
- `scripts/governance/create_d_signal_rename_tasks.py`：从 UPDATE 覆盖表清单（L133 区域）移除 `invariants.domain_id`
- `scripts/governance/audit_rename_completeness.py`：移除注释中 `invariants.invariant_id` 提及（L20）及 `EXCLUDE_TABLES` 中 governance_audit_logs/invariants 相关条目（L73-74）—— 注意 governance_audit_logs 保留，仅移除 invariants 引用

**动作4.4**：清理测试中对已删表的引用
- `tests/test_depgraph_db.py`：移除对 `invariants`（L135-144, L203）、`arch_layers`（L155-157）、`arch_bottlenecks`（L171-173）的测试用例
- governance_audit_logs 测试（test_f18_redblue.py / test_f18_automation.py）**不动**（表保留）

**动作4.5**：运行迁移并验证
```bash
python -c "from zephyr.governance.depgraph_schema import init_db; init_db(echo=True)"
# 验证 3 张表已删除、2 张保留表仍在
python -c "import sqlite3; c=sqlite3.connect(r'data/databases/depgraph.db'); cur=c.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\"); print([r[0] for r in cur])"
```
**验证**：输出不含 `arch_bottlenecks`/`arch_layers`/`invariants`；仍含 `cross_registry_rules`/`governance_audit_logs`
**回滚**：`git reset --hard 6d68fcb8` + `python -c "from zephyr.governance.depgraph_schema import init_db; init_db()"`

---

### 阶段5：创建 verify_schema_health.py 门禁（#ARCH-016，修正版）

**动作5.1**：新建 `scripts/governance/verify_schema_health.py`（顶层，与 verify_audit_integrity.py 同级；**不放 d7_code/**）

3 项校验：
1. **DDL 列一致性**：DB 实际列（`PRAGMA table_info`）vs `_DDL_*` 声明列（仅保留表，**排除已删 3 表**）
2. **只读触发器存在性**：`READONLY_TABLES` 9 张表 × 3 触发器（insert/update/delete）
3. **Schema 版本一致性**：`SELECT COALESCE(MAX(version),0) FROM _schema_version` == `len(_MIGRATIONS)`

**关键修正（vs v1）**：
- DDL 映射用非 `_V5` 常量：`_DDL_NODES`/`_DDL_EDGES`/`_DDL_ARCH_DIRECTORY_TREE`（v1 migration L632 用的就是这些，是当前真源）
- ddl_map 只含 19 张保留表，**不含** arch_bottlenecks/arch_layers/invariants（否则报假阳性 DDL-DRIFT）

完整脚本设计：

```python
#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOV-SCRIPTS
# [MODULE] scripts.governance.verify_schema_health
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance._shared.constants
# [CONSUMERS] .pre-commit-config.yaml gate-schema-health
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] depgraph_schema.py 是 DDL 真源; DB 物理状态必须与 DDL 声明一致
# [MODIFY-GUARD] depgraph_schema.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 漂移→exit 1; 健康→exit 0; 脚本自身错误→exit 2
# [TESTS] tests/test_verify_schema_health.py
"""
verify_schema_health.py — depgraph.db Schema 健康度校验门禁（#ARCH-016 治本）

校验内容：
  1. DDL 列一致性：DB 实际列 vs _DDL_* 声明列（仅保留表）
  2. 只读触发器存在性：READONLY_TABLES 的 9 张表 × 3 触发器
  3. Schema 版本一致性：MAX(_schema_version) == len(_MIGRATIONS)

退出码：
  0 = 健康（PASS）
  1 = 发现漂移（FAIL）
  2 = 脚本错误（ERROR）

模式：
  --ci          硬阻断模式（默认行为，与其他 GATE 一致；显式传入便于阅读）
  --warn-only   软警告模式（发现漂移仍 exit 0）——用于观察期
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, EXIT_FINDINGS, EXIT_ERROR, DEPGRAPH_DB_PATH  # noqa: E402

_REPO_ROOT = str(next(p for p in _THIS_FILE.parents if (p / "src" / "zephyr").exists()))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, str(Path(_REPO_ROOT) / "src"))
from zephyr.governance import depgraph_schema  # noqa: E402


def parse_ddl_columns(ddl: str) -> list[str]:
    """从 CREATE TABLE DDL 文本中解析列名列表（跳过表级约束 PRIMARY/FOREIGN/CHECK/UNIQUE/CONSTRAINT）。"""
    match = re.search(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)\s*\((.*)\)", ddl, re.DOTALL)
    if not match:
        return []
    body = match.group(2)
    columns = []
    depth = 0
    current = ""
    for char in body:
        if char == "(":
            depth += 1
            current += char
        elif char == ")":
            depth -= 1
            current += char
        elif char == "," and depth == 0:
            col_def = current.strip()
            if col_def and not col_def.upper().startswith(
                ("PRIMARY", "FOREIGN", "CHECK", "UNIQUE", "CONSTRAINT")
            ):
                columns.append(col_def.split()[0])
            current = ""
        else:
            current += char
    col_def = current.strip()
    if col_def and not col_def.upper().startswith(
        ("PRIMARY", "FOREIGN", "CHECK", "UNIQUE", "CONSTRAINT")
    ):
        columns.append(col_def.split()[0])
    return columns


# v2 修正：仅含 19 张保留表；DDL 常量全部用非 _V5（v1 migration L632 真源）
# 已删 3 表（arch_bottlenecks/arch_layers/invariants）不在映射中
_DDL_MAP = {
    "nodes": depgraph_schema._DDL_NODES,
    "edges": depgraph_schema._DDL_EDGES,
    "domains": depgraph_schema._DDL_DOMAINS,
    "domain_dependencies": depgraph_schema._DDL_DOMAIN_DEPS,
    "domain_events": depgraph_schema._DDL_DOMAIN_EVENTS,
    "contracts": depgraph_schema._DDL_CONTRACTS,
    "rule_bindings": depgraph_schema._DDL_RULE_BINDINGS,
    "arch_constraints": depgraph_schema._DDL_ARCH_CONSTRAINTS,
    "arch_directory_tree": depgraph_schema._DDL_ARCH_DIRECTORY_TREE,
    "arch_path_mappings": depgraph_schema._DDL_ARCH_PATH_MAPPINGS,
    "gates": depgraph_schema._DDL_GATES,
    "governance_audit_logs": depgraph_schema._DDL_GOVERNANCE_AUDIT_LOGS,
    "blueprint_links": depgraph_schema._DDL_BLUEPRINT_LINKS,
    "business_streams": depgraph_schema._DDL_BUSINESS_STREAMS,
    "cross_registry_rules": depgraph_schema._DDL_CROSS_REGISTRY_RULES,
    "field_vocabularies": depgraph_schema._DDL_FIELD_VOCABULARIES,
    "hard_boundaries": depgraph_schema._DDL_HARD_BOUNDARIES,
    "infrastructure_components": depgraph_schema._DDL_INFRASTRUCTURE_COMPONENTS,
    "model_capabilities": depgraph_schema._DDL_MODEL_CAPABILITIES,
    "registries": depgraph_schema._DDL_REGISTRIES,
    "domain_mapping": depgraph_schema._DDL_DOMAIN_MAPPING,
}


def check_ddl_columns(conn, issues: list) -> None:
    """校验1：DB 实际列 vs DDL 声明列。"""
    for table, ddl in _DDL_MAP.items():
        declared = set(parse_ddl_columns(ddl))
        cursor = conn.execute(f"PRAGMA table_info({table})")
        actual = {row[1] for row in cursor.fetchall()}
        if not actual:
            issues.append(f"[DDL-DRIFT] 表 '{table}' 不存在于 DB 中")
            continue
        missing_in_db = declared - actual
        extra_in_db = actual - declared
        if missing_in_db:
            issues.append(f"[DDL-DRIFT] 表 '{table}' DB 缺少列: {sorted(missing_in_db)}")
        if extra_in_db:
            issues.append(f"[DDL-DRIFT] 表 '{table}' DB 多出列（DDL 未声明）: {sorted(extra_in_db)}")


def check_readonly_triggers(conn, issues: list) -> None:
    """校验2：只读触发器存在性（READONLY_TABLES 9 张表 × 3 触发器）。"""
    readonly_tables = [
        "gates", "field_vocabularies", "registries", "cross_registry_rules",
        "hard_boundaries", "business_streams", "infrastructure_components",
        "model_capabilities", "blueprint_links",
    ]
    for table in readonly_tables:
        for action in ("insert", "update", "delete"):
            trig_name = f"readonly_{table}_{action}"
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger' AND name=?",
                (trig_name,),
            )
            if cursor.fetchone() is None:
                issues.append(
                    f"[TRIGGER-MISSING] 只读触发器 '{trig_name}' 不存在（表 {table} 未受只读保护）"
                )


def check_schema_version(conn, issues: list) -> None:
    """校验3：Schema 版本一致性。"""
    expected = len(depgraph_schema._MIGRATIONS)
    cursor = conn.execute("SELECT COALESCE(MAX(version), 0) FROM _schema_version")
    actual = cursor.fetchone()[0]
    if actual != expected:
        issues.append(
            f"[VERSION-DRIFT] _schema_version MAX={actual} 但 _MIGRATIONS 有 {expected} 条迁移"
            f"（差 {expected - actual} 条未执行）"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="depgraph.db Schema 健康度校验")
    parser.add_argument("--db", default=str(DEPGRAPH_DB_PATH), help="depgraph.db 路径")
    parser.add_argument("--ci", action="store_true", help="硬阻断模式（默认行为，显式传入便于阅读）")
    parser.add_argument("--warn-only", action="store_true", help="软警告模式（发现漂移仍 exit 0）")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"[ERROR] DB 不存在: {db_path}")
        return EXIT_ERROR

    conn = sqlite3.connect(str(db_path))
    issues: list[str] = []
    try:
        check_ddl_columns(conn, issues)
        check_readonly_triggers(conn, issues)
        check_schema_version(conn, issues)
    except Exception as e:
        print(f"[ERROR] 校验脚本异常: {e}")
        return EXIT_ERROR
    finally:
        conn.close()

    if issues:
        print(f"[FAIL] 发现 {len(issues)} 项 Schema 健康度问题:")
        for issue in issues:
            print(f"  {issue}")
        # --warn-only 优先；默认（无 flag 或 --ci）硬阻断
        return EXIT_PASS if args.warn_only else EXIT_FINDINGS

    print("[PASS] depgraph.db Schema 健康度校验通过")
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
```

**动作5.2**：验证脚本可运行
```bash
python scripts/governance/verify_schema_health.py --warn-only
```
**验证**：无 ImportError；阶段3-4 完成后应输出 `[PASS]`
**回滚**：删除 `scripts/governance/verify_schema_health.py`

---

### 阶段6：注册 GATE-SCHEMA-HEALTH（#ARCH-017）

**动作6.1**：在 `.pre-commit-config.yaml` 的 local hooks 列表中添加（路径修正为顶层）
```yaml
      # ── GATE-SCHEMA-HEALTH: depgraph.db Schema 健康度校验（#ARCH-016 治本）──
      # 权威依据：depgraph_schema.py 是 DDL 真源，DB 物理状态必须与 DDL 声明一致
      # 检测内容：DDL 列一致性 + 只读触发器存在性 + Schema 版本一致性
      # 模式：--ci 硬阻断（漂移 exit 1 拒绝提交）
      - id: gate-schema-health
        name: "GATE-SCHEMA-HEALTH: depgraph.db Schema 健康度校验"
        entry: python scripts/governance/verify_schema_health.py
        args: ["--ci"]
        language: system
        pass_filenames: false
        always_run: false
        files: "^(src/zephyr/governance/depgraph_schema\\.py|scripts/governance/sync_yaml_to_depgraph\\.py|scripts/governance/verify_schema_health\\.py)$"
        description: "depgraph.db Schema 健康度校验——DDL 列一致性 + 只读触发器 + 版本一致性，漂移即阻断。对标 #ARCH-016 治本"
```

**动作6.2**：验证门禁可触发
```bash
pre-commit run gate-schema-health --all-files
```
**验证**：输出 `[PASS] depgraph.db Schema 健康度校验通过`（阶段3-5 完成后）
**回滚**：从 `.pre-commit-config.yaml` 移除 gate-schema-health 条目

---

### 阶段7：同步文档与索引（#ARCH-018）

**动作7.1**：更新 `docs/02_enterprise_architecture/dependency_architecture_panorama.md` §4.4 表归属矩阵
- 移除已删 3 张表（arch_bottlenecks / arch_layers / invariants）
- **保留** cross_registry_rules（注明：健康只读缓存，sync 自 registry_consistency_contract.yaml，6 条 CR 规则）
- **保留** governance_audit_logs（注明：auto_runner 运行摘要审计；后续迁移至 src/zephyr/audit-trail/ WORM 模块为独立任务）
- 更新 contracts 表列数：7 → 13

**动作7.2**：更新 `scripts/governance/script_manifest.yaml`
- 添加 `verify_schema_health.py` 条目

**动作7.3**：更新 `.trae/rules/project_rules.md` RULE-SIXTEEN
- 在 depgraph.db 修改规则中追加："结构变更必须先改 `depgraph_schema.py` 的 `_DDL_*` 声明 + 添加 migration；禁止直接改写入代码跳过 DDL。GATE-SCHEMA-HEALTH 自动校验 DB↔DDL 一致性"

**动作7.4**：更新 gate 注册表（若由生成器管理）
- 若 `.pre-commit-config.yaml` 的门禁由生成器同步到 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`，运行生成器；否则手动确认 gate-schema-health 不需进入 YAML 注册表（pre-commit local hook 即可）

**动作7.5**：在治理报告索引添加本治本方案文档链接
- `docs/02_enterprise_architecture/03_governance_reports/` 索引中添加 v2 修订执行计划链接

---

## 4. 验收标准

| 验收项 | 验证命令 | 预期结果 |
|--------|----------|----------|
| migration v14 已执行 | `python -c "import sqlite3;c=sqlite3.connect(r'data/databases/depgraph.db');print(c.execute('SELECT COALESCE(MAX(version),0) FROM _schema_version').fetchone()[0])"` | `14` |
| contracts 13 列 | `python -c "import sqlite3;c=sqlite3.connect(r'data/databases/depgraph.db');print(len(c.execute('PRAGMA table_info(contracts)').fetchall()))"` | `13` |
| 3 张死表已删除 | `python -c "import sqlite3;c=sqlite3.connect(r'data/databases/depgraph.db');print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('arch_bottlenecks','arch_layers','invariants')\")])"` | `[]` |
| 2 张保留表仍在 | `python -c "import sqlite3;c=sqlite3.connect(r'data/databases/depgraph.db');print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('cross_registry_rules','governance_audit_logs')\")])"` | `['cross_registry_rules','governance_audit_logs']` |
| 生成器可运行 | `python scripts/governance/generate_project_depgraph.py --dry-run` | 无 OperationalError |
| verify 脚本 PASS | `python scripts/governance/verify_schema_health.py` | `exit 0`，`[PASS]` |
| 门禁已注册 | `grep "gate-schema-health" .pre-commit-config.yaml` | 有匹配 |
| 测试不破坏 | `python -m pytest tests/test_depgraph_db.py tests/test_auto_runner.py -q` | 无新增失败（auto_runner 测试不受影响，表保留） |

---

## 5. 回滚方案

**单阶段回滚**：每个阶段独立 `git checkout -- <file>` + 重跑 `init_db()`

**整体回滚**（若施工后发现严重问题）：
```bash
# 通过 GitCommitGateway 执行
git reset --hard 6d68fcb8
python -c "from zephyr.governance.depgraph_schema import init_db; init_db()"
# v1 migration 的 CREATE TABLE IF NOT EXISTS 会重建已删表
python scripts/governance/sync_yaml_to_depgraph.py
```

---

## 6. 受影响文件矩阵

| # | 文件路径 | 变更类型 | 关联议题 | 阶段 |
|---|----------|----------|----------|------|
| 1 | `scripts/governance/generate_project_depgraph.py` | 改：移除 INSERT 中 module_lifecycle_state（3 处） | #ARCH-010 | 3 |
| 2 | `src/zephyr/governance/depgraph_schema.py` | 改：添加 migration v14 + 移除 3 表 DDL + v1 引用 + 注释 | #ARCH-013~015 | 4 |
| 3 | `src/zephyr/governance/depgraph_reader.py` | 改：移除 get_architecture_layers 方法 | #ARCH-013 | 4 |
| 4 | `scripts/governance/apply_depgraph.py` | 改：移除改名扫描中 invariants 条目 | #ARCH-015 | 4 |
| 5 | `scripts/governance/create_d_signal_rename_tasks.py` | 改：移除 UPDATE 清单中 invariants.domain_id | #ARCH-015 | 4 |
| 6 | `scripts/governance/audit_rename_completeness.py` | 改：移除 invariants 注释引用 | #ARCH-015 | 4 |
| 7 | `tests/test_depgraph_db.py` | 改：移除 invariants/arch_layers/arch_bottlenecks 测试用例 | #ARCH-013~015 | 4 |
| 8 | `scripts/governance/verify_schema_health.py` | 新建：Schema 健康度校验脚本 | #ARCH-016 | 5 |
| 9 | `.pre-commit-config.yaml` | 改：注册 gate-schema-health | #ARCH-017 | 6 |
| 10 | `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | 改：移除 3 表 + 更新 contracts 列数 + 标注 2 表保留 | #ARCH-018 | 7 |
| 11 | `scripts/governance/script_manifest.yaml` | 改：添加 verify_schema_health.py 条目 | #ARCH-018 | 7 |
| 12 | `.trae/rules/project_rules.md` | 改：RULE-SIXTEEN 追加 Schema 健康度门禁说明 | #ARCH-018 | 7 |

**不动文件**（明确排除）：
- `sync_yaml_to_depgraph.py` 的 `sync_registry_of_registries`（cross_registry_rules 保留，sync 不动）
- `auto_runner.py`（governance_audit_logs 保留，写入路径不动）
- `tests/test_f18_*.py`（governance_audit_logs 测试不动）

---

## 7. 后续任务（明确排除出本轮，记录待办）

| 待办 | 说明 | 触发条件 |
|------|------|----------|
| governance_audit_logs → audit-trail 模块迁移 | 将 auto_runner._write_audit_log 改为写 `src/zephyr/audit-trail/writer.py`（WORM + 哈希链），然后删表 | audit-trail 模块 API 稳定后单独建任务卡 |
| invariants YAML 真源对齐 | YAML 20 条 vs 原 DB 255 行的差异需核对（DB 已删，YAML 是唯一真源） | 后续 invariants.yaml 治理时处理 |

---

## 8. 循环审查记录

**本轮审查（v1→v2）**：发现并修正 5 处事实冲突（§0 C1-C5）。修正后 v2 内部无前后冲突：
- 裁定表（§2）与施工方案（§3 阶段4）一致：删 3 表、KEEP 2 表
- verify 脚本 ddl_map（§3 阶段5）与 v14 删表清单一致：不含已删 3 表
- 验收标准（§4）与裁定一致：3 表删除、2 表保留
- 受影响矩阵（§6）"不动文件"与 KEEP 裁定一致
