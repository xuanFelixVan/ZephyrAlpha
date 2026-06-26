---
title: 派生产物治理病根调研报告 + 裁定 + 治本方案
doc_type: report
status: draft
ttl: task_bound
created: 2026-06-26
owner: ZephyrAlpha-Owner
---

# 派生产物治理病根调研报告

## 一、调研背景

GOV-FSTR-001 蓝图路径迁移（OPS-2026062652）完成后，发现 3 项遗留事项。本报告对 3 项遗留事项进行深度调研，定位病根，对标社区实践，给出裁定和治本方案。

项目特征：**100% AI 开发**，多 AI session 并发，无人工代码审查环节，治理完全依赖门禁自动化。

## 二、遗留事项逐项调研

### 遗留事项 #1：asset_index 派生产物仍引用旧路径 `_restructuring`

#### 2.1 派生产物清单与生成器映射

| 派生产物 | 旧路径引用行 | 生成器 | 生成器状态 | 输入真源 |
|---|---|---|---|---|
| `data/asset_index/target_path_tree.yaml` | L20659-20660, L48629 | `generate_target_path_tree.py` | ✅ 存活 | depgraph.db (L51) |
| `data/asset_index/project_entity_depgraph.yaml` | L3903, L3924, L464492 | `generate_project_depgraph_artifact.py` | ✅ 存活 | depgraph.db (L64) |
| `data/asset_index/blueprint_domain_mapping.yaml` | L61-67 | `dm101_blueprint_domain_mapping.py` | ❌ 已归档 `_archive/` | blueprint_registry + panorama |
| `data/asset_index/project_entity_depgraph_v3_domain_draft.yaml` | L115081-115082 | **无活跃生成器** | ❌ 孤儿 | 不明 |

#### 2.2 病根定位

**直接病根**：真源（depgraph.db）已更新，但没人运行生成器重新生成派生产物。

**根因病根（5 层）**：

| 层级 | 病根 | 证据 |
|---|---|---|
| L1 直接 | 真源改了，生成器没跑 | `generate_target_path_tree.py --write` 未运行 |
| L2 机制 | 无自动化触发器 | pre-commit 无 GATE 校验 asset_index↔depgraph.db 一致性 |
| L3 流程 | post_sync_standard 不含重生成 | task_repo.py 的 post_sync_standard 只跑 `diagnose_depgraph.py` |
| L4 规范 | 无"派生产物清单" | AGENTS.md 无"真源→派生"映射表，AI 不知道改了真源要跑哪些生成器 |
| L5 架构 | 孤儿派生产物 | `dm101` 生成器已归档但 `blueprint_domain_mapping.yaml` 仍在库中，且被 `dm106_p2b_verification.py` (L282/L571) 消费 |

**关键证据**：提交 `8260147e4`（2026-06-26 09:23）在路径迁移**之前**重生成了 `project_entity_depgraph.yaml`（改了 302 行），但当时 depgraph.db 路径还是旧的，所以产物中仍是旧路径。这说明**有人跑过生成器，但跑在了真源更新之前**——时序倒置。

---

### 遗留事项 #2：历史文档引用旧路径

#### 2.3 涉及文件

| 文件 | git 状态 | ttl | 性质 |
|---|---|---|---|
| `.trae/documents/` | `??` 未跟踪 | task_bound | IDE 临时区，非项目正式文件 |
| `docs/02_enterprise_architecture/phase_d_ai_prompts.md` | 已跟踪 | permanent | 阶段 D 历史 prompt 快照 |
| `docs/02_enterprise_architecture/.../core_function_dependency_design.md` | 已跟踪 | permanent | 架构设计历史文档 |

#### 2.4 病根定位

**这不是病根，是设计选择**。历史文档是"时间快照"——记录的是当时的路径状态。追溯修改历史文档会造成"历史被篡改"，违反审计完整性原则。

**唯一真正的缺口**：`.trae/documents/` 中的文件未跟踪但仍留在磁盘上，属于"工作区残留"——已有 GATE-ZR（零残留门禁）覆盖但仅扫描 `.py/.yaml/.md` 扩展名。

---

### 遗留事项 #3：apply_depgraph.py 138 行未提交改动

#### 2.5 事实核实

```
git diff --stat scripts/governance/apply_depgraph.py
→ 输出为空，EXIT=0
```

**apply_depgraph.py 工作区完全干净，无未提交改动。**

那 138 行已在提交 `8260147e4`（2026-06-26 09:23:59）中提交，commit message 明确记录：
> "新增cmd_propagate_node_paths精确值映射+触发器通行证"

#### 2.6 结论

**遗留事项 #3 是误报**——基于过时信息。在更早的会话中检查时确实存在未提交改动，但后来已被提交（8260147e4）。本报告后续不再讨论此项。

---

## 三、社区实践对标

### 3.1 专业机构实践（SSoT + Derived Artifact 治理）

| 实践体系 | 核心原则 | 对标差距 |
|---|---|---|
| **Bazel** | 声明式构建图：源文件 → action → 派生物。派生物不入库（`.gitignore`），CI 按需重建 | ❌ 本项目派生产物入库，无 `.gitignore` |
| **Terraform / Terramate** | `terraform-docs` 从 state 自动生成 README，pre-commit hook 触发 | ❌ 本项目无 pre-commit 触发生成器 |
| **OpenAPI Codegen** | spec → 类型自动生成，CI 校验 `--check` 模式阻断漂移 | ⚠️ 有 `--check` 模式但未接入 pre-commit |
| **K8s CRD** | Go 类型 → CRD schema 自动派生，controller-gen 在 make 时触发 | ❌ 无 make/CI 触发 |
| **docs-as-code** | 文档从代码生成，CI 校验一致性 | ⚠️ generate_derived_files.py 有 `--check` 但只覆盖 vocabulary |

### 3.2 量化社区实践（CI/CD 派生产物治理）

| 实践 | 量化指标 | 本项目状态 |
|---|---|---|
| **GitHub Actions** 派生物校验 | PR 中 `make check-generated` 阻断合并 | ❌ 无 CI pipeline |
| **Buf** (protobuf) | `buf breaking` 校验 API 兼容性 | N/A |
| **Buildkite** 动态 pipeline | 源文件变更 → 自动重生成 → diff 校验 | ❌ 无 |
| **pre-commit generated-files-identity** | 校验生成文件的 `// @generated` 标记 | ❌ 派生产物无 `@generated` 标记 |

### 3.3 氛围编程社区实践（100% AI 开发场景）

| 实践 | 核心理念 | 本项目状态 |
|---|---|---|
| **Cursor / Windsurf** | AI 改源文件后自动跑 formatter/linter | ⚠️ 有 pre-commit 但不跑生成器 |
| **GitHub Copilot Workspace** | 任务完成检查清单（checklist）含"重生成派生物"步骤 | ❌ 无此清单 |
| **Devin** | 任务完成后自动 commit + push，含生成物同步 | ⚠️ 有 GitCommitGateway 但不含生成器 |
| **AugmentCode spec-driven** | spec 变更 → 代码生成 → 验证三件对齐 | ⚠️ 有 G-TRIPLE-ALIGN 但不含派生产物 |
| **Cline / Roo** | .clinerules 要求 AI 任务完成前跑 build | ❌ AGENTS.md 无此要求 |

### 3.4 对标结论

本项目在"规则数据 SSoT"（YAML→DB）层面已达专业机构水平，但在"派生产物 SSoT"（DB→asset_index）层面存在**明显的第二层断裂**：

```
YAML (规则真源) ──sync_yaml_to_depgraph.py──→ depgraph.db (全景真源) ──✂断裂✂──→ asset_index (派生产物)
                     ↑ 有门禁保护                                    ↑ 无门禁、无触发器、无清单
```

---

## 四、裁定结果

### 裁定 #1：asset_index 派生产物——运行生成器更新

| 派生产物 | 裁定 | 理由 |
|---|---|---|
| `target_path_tree.yaml` | **运行 `generate_target_path_tree.py --write`** | 生成器存活，输入源 depgraph.db 已更新 |
| `project_entity_depgraph.yaml` | **运行 `generate_project_depgraph_artifact.py --write`** | 生成器存活，CQRS 只读模型 |
| `blueprint_domain_mapping.yaml` | **删除或重新接入生成器** | 生成器已归档，产物成孤儿；dm106 仍消费它 |
| `project_entity_depgraph_v3_domain_draft.yaml` | **评估后删除或归档** | 无活跃生成器，文件名含 `_draft` 表明是草稿 |

### 裁定 #2：历史文档——不修改

历史文档（`phase_d_ai_prompts.md`、`core_function_dependency_design.md`）是时间快照，追溯修改违反审计完整性。`.trae/documents/` 未跟踪文件属工作区残留，已有 GATE-ZR 覆盖。

### 裁定 #3：apply_depgraph.py——无需处置

工作区干净，138 行已提交（8260147e4）。误报，关闭。

### 裁定 #4（治本）：建立派生产物治理机制

这是核心裁定——**不仅要修补当前 4 个文件，还要建立机制防止未来再发生**。

---

## 五、治本施工方案

### 5.1 方案总览

```
治本 = ①立即修补 + ②机制建设 + ③规范补全
```

| 阶段 | 动作 | 产物 | 验收 |
|---|---|---|---|
| ① 立即修补 | 运行存活生成器 + 处置孤儿产物 | 4 个 asset_index 文件更新 | grep `_restructuring` 在 asset_index 中 = 0 命中（排除 ct_restructuring_safety.py 真实文件） |
| ② 机制建设 | 新增 GATE-DERIVED + post_sync_standard 扩展 | pre-commit hook + task_repo 集成 | 改 depgraph.db 后不跑生成器 → commit 被阻断 |
| ③ 规范补全 | AGENTS.md 新增"派生产物清单"章节 | 规范文档 | AI 查到清单知道改了真源要跑哪些生成器 |

### 5.2 阶段①：立即修补（当前 3 个遗留事项）

#### Step 1：重生成存活派生产物

```bash
# target_path_tree.yaml
python scripts/governance/generate_target_path_tree.py --write

# project_entity_depgraph.yaml
python scripts/governance/generate_project_depgraph_artifact.py --write
```

#### Step 2：处置孤儿派生产物

- `blueprint_domain_mapping.yaml`：检查 `dm106_p2b_verification.py` 是否仍需要它。若需要，将 `dm101` 从 `_archive` 恢复或新建替代生成器；若不需要，删除产物 + 更新 dm106。
- `project_entity_depgraph_v3_domain_draft.yaml`：确认是否仍被消费。若否，归档到 `data/asset_index/archive/`。

#### Step 3：验证

```bash
# 验证旧路径清除（排除 ct_restructuring_safety.py 等真实文件名）
grep -rn "docs/03_modules/_restructuring" data/asset_index/
# 期望：0 命中
```

### 5.3 阶段②：机制建设（治本核心）

#### 2.1 新增 GATE-DERIVED：派生产物一致性门禁

**文件**：`scripts/governance/d5_architecture/checkers/check_derived_artifacts.py`（新建）

**职责**：
- 检测 depgraph.db 变更时，触发 asset_index 派生产物 `--check` 校验
- 对标 `generate_project_depgraph_artifact.py --check` + `generate_target_path_tree.py --check`

**pre-commit 接入**：

```yaml
# .pre-commit-config.yaml 新增
- id: gate-derived-artifacts
  name: "GATE-DERIVED: 派生产物一致性（depgraph.db ↔ asset_index）"
  entry: python scripts/governance/d5_architecture/checkers/check_derived_artifacts.py
  args: ["--check", "--warn-only"]
  language: system
  pass_filenames: false
  always_run: false
  files: "^data/databases/depgraph\\.db$"
  description: "depgraph.db 变更时校验 asset_index 派生产物一致性，warn-only 骨架阶段（mutation testing≥80%+触发≥10次零误报后转硬阻断）"
```

#### 2.2 扩展 post_sync_standard：任务完成时重生成

**变更文件**：`src/zephyr/governance/task_repo.py`

在 `transition(COMPLETED)` 的 post_sync_standard 循环验收中，新增可选的 `post_sync_derived` 字段——任务完成时自动运行生成器。

```python
# task_repo.py 新增字段
post_sync_derived: list[str]  # 任务完成时运行的派生产物生成器命令
# 默认值：["python scripts/governance/generate_project_depgraph_artifact.py --write"]
```

#### 2.3 派生产物清单注册表

**文件**：`docs/01_policies_and_standards/_registry/catalogs/derived_artifact_registry.yaml`（新建）

```yaml
# 派生产物清单——AI 改了真源后 MUST 运行对应生成器
derived_artifacts:
  - artifact: data/asset_index/project_entity_depgraph.yaml
    generator: scripts/governance/generate_project_depgraph_artifact.py
    source: data/databases/depgraph.db
    command: "python scripts/governance/generate_project_depgraph_artifact.py --write"
    check_command: "python scripts/governance/generate_project_depgraph_artifact.py --check"

  - artifact: data/asset_index/target_path_tree.yaml
    generator: scripts/governance/generate_target_path_tree.py
    source: data/databases/depgraph.db
    command: "python scripts/governance/generate_target_path_tree.py --write"
    check_command: "python scripts/governance/generate_target_path_tree.py --check"

  - artifact: data/asset_index/unified-asset-index.yaml
    generator: scripts/governance/generate_asset_index.py
    source: 文件系统扫描
    command: "python scripts/governance/generate_asset_index.py --write"
    check_command: "python scripts/governance/generate_asset_index.py --check"
```

### 5.4 阶段③：规范补全

#### 3.1 AGENTS.md 新增"派生产物同步"章节

在 AGENTS.md §6 系列中新增 §6.20：

```markdown
## §6.20 派生产物同步铁律

**原则**：改了 depgraph.db（全景真源），MUST 运行对应生成器更新派生产物。

**派生产物清单**：见 _registry/catalogs/derived_artifact_registry.yaml

**AI 任务完成检查清单**（MUST 在 transition(COMPLETED) 前执行）：
1. [ ] 本任务是否改了 depgraph.db？
2. [ ] 若是，是否运行了 derived_artifact_registry.yaml 中所有生成器？
3. [ ] grep 验证旧路径/旧值在 asset_index 中已清除？
```

#### 3.2 派生产物标记 `@generated`

所有派生产物文件头部添加标记，便于 GATE-ZR 区分生成物与手写文件：

```yaml
# @generated DO NOT EDIT — 本文件由 generate_project_depgraph_artifact.py 自动生成
# 真源：data/databases/depgraph.db
# 重生成命令：python scripts/governance/generate_project_depgraph_artifact.py --write
```

### 5.5 施工任务卡建议

| 任务卡 | 内容 | 依赖 |
|---|---|---|
| OPS-2654 | 阶段①立即修补：重生成 2 个存活产物 + 处置 2 个孤儿产物 | 无 |
| OPS-2655 | 阶段②机制建设：GATE-DERIVED + derived_artifact_registry.yaml | 2654 |
| OPS-2656 | 阶段②机制建设：post_sync_derived 字段 + task_repo 集成 | 2655 |
| OPS-2657 | 阶段③规范补全：AGENTS.md §6.20 + @generated 标记 | 2655 |

## 六、风险与回退

| 风险 | 缓解 |
|---|---|
| GATE-DERIVED 误阻断（生成器有 bug） | warn-only 骨架阶段，mutation testing 检出率≥80% + 实际触发≥10次零误报后转硬阻断（事件驱动，非时间触发） |
| post_sync_derived 延长任务完成时间 | 生成器 < 5s（CQRS 只读投影），可接受 |
| 派生产物清单维护成本 | 清单本身是 YAML，由 GATE-19 漂移检测保护 |

## 七、对标总结

| 维度 | 社区标杆 | 本项目当前 | 治本后 |
|---|---|---|---|
| 派生产物不入库 | Bazel `.gitignore` | ❌ 入库 | ⚠️ 仍入库但加 `@generated` 标记 + `--check` 门禁 |
| CI 校验一致性 | `make check-generated` | ❌ 无 | ✅ GATE-DERIVED pre-commit hook |
| 任务完成重生成 | Copilot Workspace checklist | ❌ 无 | ✅ post_sync_derived 字段 |
| 派生产物清单 | Buf `buf.gen.yaml` | ❌ 无 | ✅ derived_artifact_registry.yaml |
| 孤儿产物治理 | Bazel `unused_outputs` | ❌ 无 | ✅ 清单注册 + 定期审计 |
