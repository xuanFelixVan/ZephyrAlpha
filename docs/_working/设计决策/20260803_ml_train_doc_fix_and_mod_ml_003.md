---
ttl: task_bound
---

# 设计决策备忘录：训练域文档结构修正 + MOD-ML-003 设计态节点登记

> **日期**: 2026-08-03
> **域**: D-ML-TRAIN
> **触发**: 用户要求核查 `docs/_working/依赖图/12-D-ML-TRAIN-训练域.md` 数据源路径引用

## 1. 文档结构修正（5处）

核查发现 `12-D-ML-TRAIN-训练域.md` 存在以下结构问题，已全部修正：

| # | 问题 | 位置 | 修正 |
|---|------|------|------|
| 1 | §8 章节号重复 | L794 | `## §8 运维架构(A9)规格` → `## §12 运维架构(A9)规格`（§8 已被安全架构约束占用） |
| 2 | 中文编号章节错位 | L523 | `### 四十六、决策树与强化学习交易决策架构` → `### §9.4 决策树与强化学习交易决策架构`（归属 §9 S4） |
| 3 | 中文编号章节错位 | L756 | `### 四十二、交易绩效归因与策略退化检测模型` → `### §10.3 交易绩效归因与策略退化检测模型`（归属 §10 S6） |
| 4 | 无编号章节 | L828 | `## 来自Agent架构(A7)的内容` → `## §13 来自Agent架构(A7)的内容` |
| 5 | 无编号章节 | L997 | `## 数据架构域模块补充` → `## §14 数据架构域模块补充` |

**根因**：§9.4 和 §10.3 的内容从主架构文档（使用中文章节编号"四十六""四十二"）粘贴而来，未重新编号适配本文档的 §N 体系。§12 和 §13/§14 是后续追加内容未编号。

## 2. D-ML-TRAIN-01 → MOD-L11-001 映射错误修正

### 问题

文档 L1005 声称 `D-ML-TRAIN-01 Training Dataset Manager` 的蓝图是 `MOD-L11-001已建设(部分)`，但 depgraph 中 MOD-L11-001 实际是 `trainer_base.py`（ModelTrainerBase ABC + ModelRegistry + ModelMetadata），职责是**训练器基座**，不是**训练数据集管理器**。两者是完全不同的能力。

### 修正

在 depgraph 中新增 `MOD-ML-003` 设计态节点承载 Training Dataset Manager 职责：

| 属性 | 值 |
|------|-----|
| blueprint_id | MOD-ML-003 |
| path | src/zephyr/ml_train/training_dataset_manager/ |
| domain_id | D_ML_TRAIN |
| build_status | planned |
| granularity | directory |
| design_maturity | design |
| design_evidence | docs/_working/依赖图/12-D-ML-TRAIN-训练域.md §14 §17.5 |

文档 L1005 蓝图备注已更新为：`📐已登记设计态节点 MOD-ML-003 (planned)，path=src/zephyr/ml_train/training_dataset_manager/`

## 3. 数据源路径引用核查结论

### ✅ 正确引用

| 引用 | 路径 | 文件系统 | depgraph |
|------|------|:--------:|:--------:|
| BM-MT-01-A (MOD-L11-001) | src/zephyr/ml_train/trainer_base.py | ✅ 存在 | ✅ generated |
| CAND-HARVEST-0728~0732, 0922 | candidate_module_registry.yaml | ✅ 存在 | ✅ DB anchors 有记录 |

### ⚠️ 设计态路径（非错误，模块尚未实现）

| 引用 | 路径 | 文件系统 | depgraph |
|------|------|:--------:|:--------:|
| BM-MT-01 (MOD-ML-001) | src/zephyr/ml_train/training_pipeline/ | ❌ 不存在 | planned |
| BM-MT-01-B (MOD-ML-002) | src/zephyr/ml_train/ai_operator/ | ❌ 不存在 | planned |

这两个路径是**规划中的目标路径**，模块 build_status=planned，file_path 为空。作战地图已用 🟧设计态 标记区分，引用本身不算错误。

## 4. depgraph 变更记录

```
操作: apply_depgraph.py --add-design-node
命令: python scripts/governance/apply_depgraph.py \
      --add-design-node "src/zephyr/ml_train/training_dataset_manager/" \
      "MOD-ML-003" "D_ML_TRAIN" "planned" \
      --granularity directory \
      --design-evidence "docs/_working/依赖图/12-D-ML-TRAIN-训练域.md §14 §17.5"
结果: build_status=planned, design_maturity=design（node_id 略，查 depgraph 获取）
备份: tmp/pg_backups/depgraph_20260803_111235.json
```
