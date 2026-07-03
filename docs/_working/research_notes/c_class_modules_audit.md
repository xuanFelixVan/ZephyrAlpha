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

### 6.2 新建议 1：修复 script_system 路径漂移（5 处）
见 §4 修复清单。建议作为独立任务卡执行（DM-XXXXXX），因为这涉及多个蓝图文件改动，需逐个验证。

### 6.3 新建议 2：infra_ops 域归属决策
建议归并到 `_domain_infrastructure_runtime/`，但需 architecture 裁定（涉及域合并，影响 43 域方案）。

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
