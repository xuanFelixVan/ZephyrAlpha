# c_class_modules_audit.md — 3 个 C 类模块复核报告

> 调研对象：[manifests_cure_plan.md](manifests_cure_plan.md) §7 后续建议 1 的 3 个 C 类模块
> 日期：2026-07-04
> 配套：[manifests_mapping_audit.md](manifests_mapping_audit.md) · [manifests_missing_diagnosis.md](manifests_missing_diagnosis.md)

---

## 0. 执行摘要（TL;DR）

**3 个 C 类模块全部误判**：

| 模块 | 原诊断 | 实际情况 | 修正后分类 |
|------|--------|----------|------------|
| hooks | C 类（无 blueprint） | 已归并到 runtime_integration/blueprint.md（MOD-INF-002） | **B 类**（归并到现有蓝图） |
| script_system | C 类（无 blueprint） | 有蓝图 governance_automation/blueprint.md（MOD-INF-005），但路径漂移严重 | **B 类**（blueprint 存在但命名不匹配 + 4 处引用路径错误） |
| infra_ops | C 类（无 blueprint） | 域级蓝图缺失，但子模块各有蓝图；runtime_integration/blueprint.md layer=infra_ops | **B 类**（域级蓝图由 runtime_integration 代理） |

**真正的病根**：不是"缺 blueprint"，而是**路径漂移 + 命名不一致**：
1. script_system 的 4 处蓝图引用路径全部错误
2. governance_automation/blueprint.md 的 actual_disk_path 写错
3. infra_ops 域级蓝图归属不清（runtime_integration 在 _domain_infrastructure_runtime/ 下，但 layer=infra_ops）

**修正后 C 类 = 0**，原"26 B + 3 C"应进一步修正为"29 B + 0 C"。

---

## 1. hooks 模块复核

### 1.1 源码位置
- `src/zephyr/infrastructure/hooks/`（2 个文件）
  - `__init__.py`（6 行）
  - `event_hook.py`（HookRegistry / TransitionEvent / hook_registry）

### 1.2 蓝图归属
源码头部声明：
```
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
```
即 hooks 已归并到 `runtime_integration/blueprint.md`（MOD-INF-002，"15核心RI模块跨层协同与运行时基础设施"）。

### 1.3 diagnosis.md 误判原因
- diagnosis.md L44 写"hooks：2 文件，无声明，镜像于 infrastructure/runtime_integration/hooks/"
- **实际**：源码在 `infrastructure/hooks/`（不是 `infrastructure/runtime_integration/hooks/`），且**头部有明确的蓝图归属声明**
- 误判根因：当时只看子目录名是否匹配，未读源码头部声明

### 1.4 处置
**无需补建 blueprint**。hooks 已是 runtime_integration 的子模块，路径归并正确。

---

## 2. script_system 模块复核

### 2.1 源码位置
- `src/zephyr/infrastructure/script_system/`（4 个文件）
  - `__init__.py`
  - `finding.py`（Finding Schema — 审计发现标准化数据模型）
  - `kb_bridge.py`（Knowledge Base 桥接）
  - `gate_bridge.py`（Gate 桥接）

### 2.2 蓝图归属
源码头部声明：
```
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain-governance/governance-automation/blueprint.md
```
即 script_system 的蓝图是 `governance_automation/blueprint.md`（MOD-INF-005，"Script System 蓝图 — 第三条生产线的自动化审计与门禁"）。

### 2.3 路径漂移问题（4 处错误引用）

| 引用源 | 错误路径 | 正确路径 |
|--------|----------|----------|
| `_system_master/blueprint.md` L656 | `src/zephyr/script_system/` | `src/zephyr/infrastructure/script_system/` |
| `governance_automation/blueprint.md` L53 (actual_disk_path) | `src/zephyr/script_system/` | `src/zephyr/infrastructure/script_system/` |
| `governance_automation/blueprint.md` L86-87 | `src/zephyr/infrastructure/runtime_integration/script_system/` | `src/zephyr/infrastructure/script_system/` |
| `gate_engine/blueprint.md` L698 | `docs/03_modules/_cross_layer/script_system/blueprint.md` | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |
| `task_system/blueprint.md` L639/L1360 | `docs/03_modules/_domain_infrastructure_operations/script_system/blueprint.md` | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |

### 2.4 diagnosis.md 误判原因
- diagnosis.md L45 写"script_system：2 文件，被 6 蓝图提及无主属"
- **实际**：4 个文件（非 2 个），且有明确主属（governance_automation/blueprint.md，MOD-INF-005）
- 误判根因：当时只看 `docs/03_modules/**/script_system/blueprint.md` 是否存在，未读 governance_automation/blueprint.md 的标题和内容

### 2.5 处置建议
**无需补建 blueprint**。但需修复 5 处路径漂移（见 §4 修复清单）。

---

## 3. infra_ops 模块复核

### 3.1 源码位置
- `src/zephyr/infra_ops/`（目录存在但几乎空，只有 __init__.py 和子目录骨架）
  - `_extensions/` / `api/` / `core/` / `dashboard/` / `infrastructure/` / `services/`
  - 所有子目录只有 `__init__.py`，无实际业务代码

### 3.2 蓝图归属
- `_domain_infrastructure_operations/` 下无域级 `blueprint.md`（仅有自动生成的 `index.md`）
- 4 个子模块各有自己的 blueprint.md：
  - `a2a_protocol/blueprint.md`
  - `asset_inventory/blueprint.md`
  - `capacity_assurance/blueprint.md`
  - `system_telemetry/blueprint.md`
- **关键**：`runtime_integration/blueprint.md`（MOD-INF-002）的 frontmatter 显示：
  - `layer: infra_ops`
  - `layer_name: infrastructure`
  - `actual_disk_path: src/zephyr/shared/ + src/zephyr/infrastructure/ + src/zephyr/governance/lifecycle_governance/`
- 即 runtime_integration 蓝图的 layer 声明是 infra_ops，但蓝图文件在 `_domain_infrastructure_runtime/` 下

### 3.3 域级蓝图缺失的原因推测
- `_domain_infrastructure_operations/` 和 `_domain_infrastructure_runtime/` 是两个不同的域目录
- `infra_ops` 域的源码 `src/zephyr/infra_ops/` 几乎是空骨架，可能从未真正施工
- 实际的 infra_ops 功能由 `src/zephyr/infrastructure/` 承载，归 `runtime_integration` 蓝图管

### 3.4 处置建议
**两种选择**：
1. **补建域级 blueprint**（如果 infra_ops 域要独立发展）：创建 `_domain_infrastructure_operations/blueprint.md`，声明 4 个子模块的集成契约
2. **归并到 runtime_integration**（如果 infra_ops 域不独立）：把 `_domain_infrastructure_operations/` 下的 4 个子模块归到 `_domain_infrastructure_runtime/`，删除 `_domain_infrastructure_operations/` 域

建议选方案 2（归并），理由：
- `src/zephyr/infra_ops/` 几乎空，无实际业务代码
- runtime_integration/blueprint.md 的 layer 已声明为 infra_ops
- 减少域数量，符合"向内收"原则

---

## 4. 路径漂移修复清单（5 处）

> 优先级：P2（不阻断功能，但影响新 AI 可发现性）
> 风险：低（仅改文档引用，不改代码）

| # | 文件 | 行号 | 错误内容 | 正确内容 |
|---|------|------|----------|----------|
| 1 | `docs/03_modules/_system_master/blueprint.md` | 656 | `src/zephyr/script_system/` | `src/zephyr/infrastructure/script_system/` |
| 2 | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` | 53 | `src/zephyr/script_system/` | `src/zephyr/infrastructure/script_system/` |
| 3 | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` | 86-87 | `src/zephyr/infrastructure/runtime_integration/script_system/` | `src/zephyr/infrastructure/script_system/` |
| 4 | `docs/03_modules/_cross_layer/gate_engine/blueprint.md` | 698 | `docs/03_modules/_cross_layer/script_system/blueprint.md` | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |
| 5 | `docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md` | 639, 1360 | `docs/03_modules/_domain_infrastructure_operations/script_system/blueprint.md` | `docs/03_modules/_domain_governance/governance_automation/blueprint.md` |

---

## 5. 修正后的 manifest 分类汇总

基于本次复核，[manifests_mapping_audit.md](manifests_mapping_audit.md) 的 C 类应全部修正为 B 类：

| 分类 | 原始（2026-07-04 第一次复核） | 本次修正 | 说明 |
|------|------------------------------|----------|------|
| A | 13 | 13 | 无变化 |
| B | 26 | **29** | hooks + script_system + infra_ops 从 C 改为 B |
| C | 3 | **0** | 全部误判 |
| D | 0 | 0 | 无变化 |
| 合计 | 42 | 42 | |

**结论**：42 个 manifest 全部能找到归属（A=13 / B=29 / C=0 / D=0）。原 diagnosis.md 的"2 个 C 类"和第一次复核的"3 个 C 类"均属误判，根因是未读源码头部声明和蓝图标题。

---

## 6. 后续建议（更新 [manifests_cure_plan.md](manifests_cure_plan.md) §7）

### 6.1 原建议 1（3 个 C 类补建 blueprint）→ 取消
3 个模块均有蓝图归属，无需补建。

### 6.2 新建议 1：修复 script_system 路径漂移（12 处，已修复 ✅）
原报告为 5 处，实际 Grep 发现 12 处路径漂移（根因相同），已全部修复：

| # | 文件 | 错误模式 | 修复数 |
|---|------|----------|--------|
| 1 | governance_automation/blueprint.md | `runtime_integration/script_system/` → `script_system/` | 4 处 |
| 2 | governance_automation/blueprint.md | `src/zephyr/script_system/`（正斜杠）→ `src/zephyr/infrastructure/script_system/` | 2 处 |
| 3 | governance_automation/blueprint.md | `src\zephyr\script_system\`（反斜杠）→ `src\zephyr\infrastructure\script_system\` | 2 处 |
| 4 | _system_master/blueprint.md | `src/zephyr/script_system/` → `src/zephyr/infrastructure/script_system/` | 1 处 |
| 5 | task_system/blueprint.md | `_domain_infrastructure_operations/script_system/` → `_domain_governance/governance_automation/` | 2 处 |
| 6 | gate_engine/blueprint.md | `_cross_layer/script_system/` → `_domain_governance/governance_automation/` | 1 处 |

注：governance_automation/blueprint.md（153KB）和 _system_master/blueprint.md（157KB）过大，Edit 工具未生效，改用 Python 脚本修复（临时脚本已清理）。

### 6.3 新建议 2：infra_ops 域归属裁定（需 ARCH 裁定）

**现状调研**：

1. `_domain_infrastructure_operations/` 域：4 个子模块蓝图（agent_to_agent_protocol / asset_inventory / capacity_assurance / system_telemetry），**无域级 blueprint.md**，仅有自动生成的 index.md
2. `_domain_infrastructure_runtime/` 域：含 runtime_integration/blueprint.md，其 frontmatter 声明 `layer: infra_ops`（与物理路径不一致）
3. runtime_integration 蓝图"代理"了 infra_ops 域的域级职责（RI-12~RI-15 独立落地 `infra_ops/` 目录）

**根因分析**：
- `layer: infra_ops` 是**功能层声明**（infra operations 层），不是域路径声明
- `_domain_infrastructure_runtime/` 是**物理路径**（infrastructure runtime 域）
- 两者维度不同，但命名相似导致混淆

**推荐方案 C（修正 layer + 补建域级蓝图）**：

| 动作 | 理由 |
|------|------|
| runtime_integration/blueprint.md 的 `layer: infra_ops` → `layer: infra_runtime` | 与物理路径 `_domain_infrastructure_runtime/` 一致 |
| 补建 `_domain_infrastructure_operations/blueprint.md` 域级蓝图 | 明确 4 个子模块的集成契约和域级职责 |
| 保持 `_domain_infrastructure_operations/` 和 `_domain_infrastructure_runtime/` 为两个独立域 | 职责不同：operations 关注 A2A/资产/容量/遥测，runtime 关注 EventBus/生命周期/韧性 |

**不推荐方案 A（归并）**：4 个子模块职责与 runtime_integration 不同，归并会导致域职责混淆。
**不推荐方案 B（仅补建）**：不修正 layer 声明，layer=infra_ops vs 物理路径 `_domain_infrastructure_runtime/` 的不一致仍存在。

### 6.6 新发现：`_domain_infrastructure_operations/` 前缀大规模误用（需独立任务卡）

调研 infra_ops 域归属时发现：**大量蓝图错误引用 `_domain_infrastructure_operations/` 作为通用前缀**，指向不存在的蓝图路径。初步统计 30+ 处误用：

| 错误路径前缀 | 实际所在域 | 涉及模块 |
|--------------|-----------|----------|
| `_domain_infrastructure_operations\database\` | `_cross_layer/database/` | database |
| `_domain_infrastructure_operations\audit-trail\` | `_domain_governance/audit_trail/` | audit_trail |
| `_domain_infrastructure_operations\agent-rbac\` | `_domain_autonomy_core/agent_role_based_access_control/` | agent_rbac |
| `_domain_infrastructure_operations\knowledge_base\` | `_domain_knowledge/knowledge_base/` | knowledge_base |
| `_domain_infrastructure_operations\context_engine\` | `_cross_layer/context_engine/` | context_engine |
| `_domain_infrastructure_operations\vector_memory\` | `_domain_knowledge/vector_memory/` | vector_memory |
| `_domain_infrastructure_operations\gate_engine\` | `_cross_layer/gate_engine/` | gate_engine |
| `_domain_infrastructure_operations\feedback_loop\` | `_cross_layer/feedback_loop/` | feedback_loop |
| `_domain_infrastructure_operations\pipeline\` | `_cross_layer/pipeline/` | pipeline |
| `_domain_infrastructure_operations\runtime_integration\` | `_domain_infrastructure_runtime/runtime_integration/` | runtime_integration |
| `_domain_infrastructure_operations\script-system\` | `_domain_governance/governance_automation/` | script_system |
| `_domain_infrastructure_operations\task_system\` | `_domain_infrastructure_runtime/task_system/` | task_system |
| `_domain_infrastructure_operations\escalation-protocol\` | `_domain_autonomy_perm/escalation_protocol/` | escalation_protocol |
| `_domain_infrastructure_operations\asset-inventory\` | `_domain_infrastructure_operations/asset_inventory/`（连字符 vs 下划线不一致） | asset_inventory |
| `_domain_infrastructure_operations\rbac\` | `_domain_autonomy_core/agent_role_based_access_control/` | agent_rbac |
| `_domain_infrastructure_operations\agent-spec\` | `_domain_autonomy_core/agent_spec/` | agent_spec |
| `_domain_infrastructure_operations\budget-enforcer\` | `_domain_autonomy_perm/budget_enforcer/` | budget_enforcer |

**根因**：`_domain_infrastructure_operations/` 被误用为"所有基础设施类模块的通用前缀"，但实际各模块分散在不同域。
**建议**：作为独立任务卡（DM-XXXXXX）处理，需全量 Grep + 批量修复 + 验证。

### 6.4 原建议 2（命名体系统一）→ 保持
path_ownership_map.yaml 登记别名映射表的建议仍然有效。

### 6.5 原建议 3（临时脚本清理）→ 已完成
tmp/_extract_manifest_mapping.py + debug dump 已删除。

---

## 7. 引用

- 源码头部声明规范：`# [BLUEPRINT] MOD-XXX | <blueprint_path> | §`
- 蓝图模板 v3.5：[blueprint_construction_template.md](../../01_policies_and_standards/templates/blueprint_construction_template.md)
- 配套产出物：
  - [manifests_mapping_audit.md](manifests_mapping_audit.md)
  - [manifests_missing_diagnosis.md](manifests_missing_diagnosis.md)
  - [manifests_cure_plan.md](manifests_cure_plan.md)
