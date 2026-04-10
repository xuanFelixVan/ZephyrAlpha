---
module_id: OPENCLAW_L1
---

# OpenClaw L1 文件系统层审计报告

> **run_id**: OPENCLAW_20260408_033500
> **生成时间**: 2026-04-08
> **数据来源**: `SENTINEL_L1_SCAN_20260408.json`、`overnight_runs/20260408_033240/invalid_links_detail_20260408_033240.md`、`overnight_runs/20260408_033240/module_id_duplicates_detail_20260408_033240.md`

---

## 一、无效内链（69 条）

### 1.1 按问题类型分类

| 问题类型 | 条数 | 严重度 | 说明 |
|----------|------|--------|------|
| 缺失目标文件 | 7 | P0 | 链接指向的 .md 文件不存在 |
| 路径层级错误（多拼了一层 docs/） | 6 | P1 | 蓝图中链接从 docs/ 内部又拼了 docs/ 前缀 |
| 伪链接（代码变量被误识别为链接） | 4 | P2 | `**value`、`df, fix_suggestion`、`service_name, dry_run`、`instances, service_name` |
| audit_state INDEX 缺少 `./` 前缀 | 22 | P1 | INDEX.md 中裸文件名链接，缺少相对路径前缀 |
| audit_state 内跨目录链接指向不存在蓝图 | 3 | P1 | `./DATA_FABRIC_BLUEPRINT.md`、`./DATA_MESH_BLUEPRINT.md` 在 audit_state 目录不存在 |
| LAYER8_GAP_ANALYSIS / COMPLETE_SUPPLEMENT 缺失 | 7 | P1 | 多篇 audit_state 文档引用但目标文件不存在 |
| 非 .md 目标（.py 文件） | 4 | P2 | notebooks INDEX 链到 .py 模板文件 |
| 外部评审包路径错误 | 7 | P1 | review_materials_package 内链接使用了错误相对路径 |
| 其他路径错误 | 9 | P1 | System_Manifest、LAYER2_PLAN、README 等路径问题 |

### 1.2 P0 无效链接明细

| 路径 | 问题链接 | 证据 | 严重度 | 建议动作 |
|------|----------|------|--------|----------|
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/CONFIG_CENTER_BLUEPRINT.md` | `05_IMPLEMENTATION/.../CONFIG_CENTER_BLUEPRINT.md` | 多拼了 docs/ 前缀导致双重路径 | P0 | 修正为 `./CONFIG_CENTER_BLUEPRINT.md` 或正确的相对路径 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/CONTAINER_ORCHESTRATION_BLUEPRINT.md` | 同上模式 | 同上 | P0 | 同上 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/LOAD_BALANCING_BLUEPRINT.md` | 同上模式 | 同上 | P0 | 同上 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SECURITY_SCANNING_BLUEPRINT.md` | 同上模式 | 同上 | P0 | 同上 |
| `docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/SERVICE_DISCOVERY_BLUEPRINT.md` | 同上模式 | 同上 | P0 | 同上 |
| `docs/System_Manifest.md` | `05_IMPLEMENTATION/04_OPERATIONS/audit_state/LAYER8_GAP_ANALYSIS_REPORT_20260407.md` | 目标文件不存在 | P0 | 确认文件是否应存在，若已归档则更新链接指向归档路径 |
| `docs/09_AUDIT/STATE/LAYER2_COMPLETE_IMPLEMENTATION_PLAN.md` | `09_AUDIT/STATE/LAYER2_DEEP_MISSING_ANALYSIS.md` | 从 STATE 目录内又拼了 09_AUDIT/STATE/ 前缀 | P0 | 修正为 `./LAYER2_DEEP_MISSING_ANALYSIS.md` |

### 1.3 P1 无效链接摘要（关键模式）

1. **audit_state INDEX.md 裸文件名链接**（22 条）：`docs/05_IMPLEMENTATION/04_OPERATIONS/audit_state/INDEX.md` 中使用 `LAYER5_XXX.md` 而非 `./LAYER5_XXX.md`，导致解析路径错误。建议统一加 `./` 前缀。

2. **LAYER8 系列缺失目标**（7 条）：多篇文档引用 `./LAYER8_GAP_ANALYSIS_REPORT_20260407.md` 和 `./LAYER8_COMPLETE_SUPPLEMENT_PLAN_20260407.md`，但目标文件在 `04_OPERATIONS/audit_state/` 下不存在。可能已归档或从未创建。

3. **review_materials_package 路径错误**（7 条）：外部评审包内链接使用了 `../04_EXECUTION/` 等路径，但评审包不在 docs/ 树内，解析后路径不存在。

---

## 二、module_id 重复（238 组）

### 2.1 Top 10 重复组

| module_id | 重复文件数 | 严重度 | 说明 |
|-----------|-----------|--------|------|
| `05_IMPLEMENTATION_07_OPERATIONS_AUDIT_STATE_001` | 29 | P0 | audit_state 下多轮审计报告共享同一 ID |
| `05_IMPLEMENTATION_04_OPERATIONS_AUDIT_STATE_001` | 18 | P0 | 同上，另一 audit_state 目录 |
| `02_FACTOR_LIBRARY_01_STANDARDS_001` | 18 | P1 | 09_ARCHIVE/duplicates 下归档文件与活跃文件 ID 冲突 |
| `02_FACTOR_LIBRARY_04_DATA_SOURCE_001` | 14 | P1 | 同上 |
| `09_AUDIT_REPORTS_001` | 11 | P0 | REPORTS 目录多份报告共享同一 ID |
| `[模块ID]` | 10 | P0 | 模板占位符未替换，10 篇文件仍含字面 `[模块ID]` |
| `09_AUDIT_STATE_001` | 10 | P0 | STATE 目录多份报告共享同一 ID |
| `DATA_VERSION_CONTROL_001` | 5 | P1 | 同一蓝图在 FRAMEWORK/IMPLEMENTATION/ARCHIVE 多处存在 |
| `SIMPLIFIED_RISK_BUDGET_SYSTEM_001` | 5 | P1 | 同上 |
| `02_FACTOR_LIBRARY_05_BACKTEST_001` | 5 | P1 | 归档重复 |

### 2.2 重复类型分析

| 类型 | 组数 | 典型表现 |
|------|------|----------|
| A. 审计报告批量共享 ID | ~60 | audit_state 下多轮报告使用同一目录级 ID |
| B. 归档副本 ID 冲突 | ~80 | 09_ARCHIVE/duplicates 保留原 ID |
| C. 模板占位符未替换 | 10 | `[模块ID]` 字面值 |
| D. 蓝图跨目录重复 | ~30 | 同一蓝图在 FRAMEWORK + IMPLEMENTATION + ARCHIVE 三处 |
| E. 其他 | ~58 | 各类零散冲突 |

---

## 三、未检出 module_id（74 篇）

这些文件在前 120KB 扫描范围内未找到 YAML `module_id` 字段。可能原因：
- 缺少 YAML front matter
- YAML 格式损坏（双 YAML 头、编码问题）
- 非标准文档（README、CHANGELOG、数据文件）

---

## 四、L1 总结与建议

| 严重度 | 问题数 | 建议优先动作 |
|--------|--------|-------------|
| P0 | ~17 | 修复蓝图中双重路径链接；消除 `[模块ID]` 占位符；为 audit_state 报告分配唯一 ID |
| P1 | ~40 | 修复 audit_state INDEX 裸文件名链接；确认 LAYER8 缺失目标；消解归档副本 ID 冲突 |
| P2 | ~12 | 清理伪链接（代码变量误识别）；notebooks .py 链接可保留但标注 |

**下一步**: 进入 L2 分批深度审计，按目录逐批回答五问。
