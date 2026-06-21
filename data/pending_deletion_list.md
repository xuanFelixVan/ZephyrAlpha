# 待删除/待补全清单

> 来源：§4.4 最终交付命令 `audit_registration.py` exit 1（733 issues）
> 处置规则：§6 异常处理矩阵第17项 "audit_registration.py exit≠0 → 读孤儿文件列表→记录到待删除清单→继续"
> 生成时间：2026-06-18
> Session：session-20260618-001

## 1. ORPHAN SCRIPTS（8个，已完成RULE-THREE三步审判）

> ✅ 审判完成时间：2026-06-18
> 审判结果：5个已删除，3个已注册到script_manifest.yaml

### 1.1 已删除脚本（5个）

| # | 脚本路径 | 删除原因 |
|---|---------|---------|
| 1 | `scripts/construction/_dm014_analyze_remain.py` | 一次性只读诊断脚本，任务已完成，重建成本低 |
| 2 | `scripts/construction/_dm014_analyze_v2.py` | 一次性只读诊断脚本（v2迭代），任务已完成 |
| 3 | `scripts/database/audit_migration_completeness.py` | 脚本已损坏（同库连3次），迁移已完成 |
| 4 | `scripts/database/update_all_db_references.py` | 脚本已损坏（dict键重复），迁移已完成 |
| 5 | `scripts/database/update_db_references.py` | 脚本已失效（old=new=空操作），迁移已完成 |

### 1.2 已注册脚本（3个）

| # | 脚本路径 | 注册到 | 保留原因 |
|---|---------|--------|---------|
| 1 | `scripts/dm90971_add_test_headers.py` | script_manifest.yaml | 批量治理头工具，遵循RULE-SEVEN/ONE/FIVE，可复用 |
| 2 | `scripts/construction/create_db_alignment_tasks.py` | script_manifest.yaml | DB对齐任务卡创建工具，有模板价值 |
| 3 | `scripts/construction/dm014_orphan_edge_repair.py` | script_manifest.yaml | 5策略孤儿补边修复工具，含exit code门禁，可持续复用 |

> 注：script_manifest.yaml的total_scripts已从430更新为433

## 2. MISSING __all__（8个，待人工补全）

> 这8个 `__init__.py` 缺少 `__all__` 条目，属于注册不完整。
> 需人工补全 `__all__` 导出列表。

| # | __init__.py 路径 |
|---|----------------|
| 1 | `src/zephyr/data/persistence/__init__.py` |
| 2 | `src/zephyr/governance/persistence/__init__.py` |
| 3 | `src/zephyr/shared/shared_services/__init__.py` |
| 4 | `src/zephyr/shared/shared_services/events/__init__.py` |
| 5 | `src/zephyr/shared/shared_services/infra_06/__init__.py` |
| 6 | `src/zephyr/shared/shared_services/lifecycle/__init__.py` |
| 7 | `src/zephyr/shared/shared_services/observability_02/__init__.py` |
| 8 | `src/zephyr/shared/shared_services/queue/__init__.py` |

## 3. 未注册模块（717个，项目既有问题，非本次施工引入）

> 这些是 `src/zephyr/` 下的 `.py` 文件，未在对应 `__init__.py` 的 `__all__` 中导出。
> 属于项目历史遗留问题，非本次依赖全景图施工引入。
> 处置：记录存档，不影响本次§4.4交付。后续可由专项治理任务处理。

### 主要分布（按包统计）：

| 包路径 | 未注册模块数 |
|--------|------------|
| `ops/` | ~15 |
| `trading/` | ~40 |
| `governance/persistence/` | ~12 |
| `governance/implementations/` | ~1 |
| `shared/shared_services/` | ~20 |
| `shared/` (各子包) | ~30 |
| `simulation/` | ~3 |
| `reporting/` | ~2 |
| `portfolio_allocation/` | ~1 |
| `infra_ops/dashboard/` | ~6 |
| `infra_runtime/observability/` | ~2 |
| `integration/governance/` | ~4 |
| `data/persistence/` | ~2 |
| 其他 | ~579 |

## 4. 处置结论

- **本次§4.4施工未引入新的孤儿/未注册问题**
- 733个issues均为项目历史遗留问题
- 按§6异常处理矩阵第17项：记录到本清单后继续执行剩余§4.4命令
- 后续治理建议：立项专项治理任务，分批注册/补全/删除

---

## 待删除文件追加区（后续session可追加）

> 格式：`| 日期 | Session | 文件路径 | 原因 | 状态 |`

| 日期 | Session | 文件路径 | 原因 | 状态 |
|------|---------|---------|------|------|
| 2026-06-18 | session-20260618-001 | `scripts/governance/repair/_query_gov_db.py` | P1-2临时查询脚本，查询governance.db表结构，已完成用途，无独立价值 | ✅ 已删除 |
| 2026-06-18 | session-20260618-001 | `scripts/governance/repair/_query_dm_tasks.py` | P1-2临时查询脚本，查询DM-开头任务卡，已完成用途，无独立价值 | ✅ 已删除 |
| 2026-06-18 | session-20260618-001 | `scripts/governance/repair/_query_dm200.py` | P1-2临时查询脚本，查询DM-200%任务卡，已完成用途，无独立价值 | ✅ 已删除 |
| 2026-06-18 | session-20260618-001 | `scripts/governance/repair/_check_status_enum.py` | P1-3临时查询脚本，查询tasks表status枚举和触发器，已完成用途，无独立价值 | ✅ 已删除 |
| 2026-06-18 | session-20260618-001 | `scripts/governance/repair/_p1_3_verify_tasks.py` | P1-3临时脚本，批量UPDATE任务卡status为VERIFIED，已完成用途，无独立价值 | ✅ 已删除 |
| 2026-06-18 | session-20260618-001 | `scripts/governance/repair/_gen_unregistered_registry.py` | P2-1临时脚本，生成未注册模块注册表，717治理需重新生成 | 📌 保留（RULE-THREE审判：3c=YES） |
