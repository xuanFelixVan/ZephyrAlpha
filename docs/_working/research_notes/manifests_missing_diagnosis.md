---
ttl: task_bound
---

# manifests_missing_diagnosis.md — STEP 2 根因诊断

> 调研对象：`docs/03_modules/_manifests/` 下 42 个 `*_manifest.md` 中 27 个"名称匹配不到 blueprint"的根因诊断
> 日期：2026-06-30
> 注意：本文件为 STEP 2 诊断记录（历史快照，分类为 25B+2C）。最终裁定（删除 manifest）见 [manifests_cure_plan.md](manifests_cure_plan.md)
>
> **⚠️ 最终结论指针（2026-07-04 二次复核）**：本文件中的"2 个 C 类（hooks/script_system）"经源码头部声明核实后**全部为误判**，3 个 C 类（含 infra_ops）应全部修正为 B 类，最终分类为 **A=13 / B=29 / C=0 / D=0**。详见 [c_class_modules_audit.md](c_class_modules_audit.md) 与 [manifests_cure_plan.md](manifests_cure_plan.md) §7.5。原根因 5"部分模块无蓝图"已取消。

## 0. 27 个 missing 的分类总览

| 类型 | 数量 | 含义 |
|------|------|------|
| **B**（名称不匹配但可推断） | 25 | 通过 ssot_path / path_ownership_map / 蓝图 §0.1 确认归属 |
| **C**（模块无 blueprint.md） | 2 | hooks、script_system |
| **D**（孤儿/废弃） | 0 | — |

> 结论：27 个 missing 无一是真正的"孤儿"，全部能找到归属或需补建。本质是**命名体系不一致**，非模块缺失。

## 1. 根因清单（6 条）

### 根因 1：命名体系不一致（影响全部 25 个 B 类）——主因

manifest 文件名 = **源码目录名**（简写/连字符），blueprint 子目录名 = **完整语义名**。无机械映射规则。

典型示例：a2a→a2a_protocol、telemetry→system_telemetry、db→database、kb→knowledge_base、gates→gate_engine、orchestrator→agent_orchestrator、runtime→auto_runtime_core、shared/core→shared_core。

### 根因 2：两套 module_id 体系并存（影响 30 个 05-09 manifest）

- manifest frontmatter module_id：MOD-041~070（旧顺序编号，已失效）
- blueprint module_id：MOD-INF-020、MOD-L00-001 等（语义编号，当前权威）
- 两套无映射表；manifest 的 blueprint_id 全为 MOD-GOVERNANCE（域级），对模块映射无用

### 根因 3：frontmatter schema 双版本

| 批次 | 数量 | 有 module_id | 有 ssot_path |
|------|------|--------------|--------------|
| 2026-05-09 | 30 | 是 | 否 |
| 2026-06-10 | 12 | 否 | 是 |

### 根因 4：源码路径分裂

多模块在 `src/zephyr/infrastructure/` 下有镜像副本（db/rollback/escalation/hooks/script_system 等），加剧映射难度。

### 根因 5：部分模块无蓝图（2 个 C 类）

- hooks：2 文件，无声明，镜像于 infrastructure/runtime_integration/hooks/
- script_system：2 文件，被 6 蓝图提及无主属

### 根因 6：生成器缺失（元问题，最关键）

42 个 manifest 全标"自动生成"但无提交生成器。ad-hoc 产出，不可重生。

## 2. 关键发现

1. "27 个 missing"不是模块缺失，是命名不一致。
2. 生成器缺失是元问题——直接否决方案 C"可重生"前提。
3. **更深层的元问题**（见 cure_plan.md）：manifest 本身是 blueprint §0.1 的过时冗余子集，无独有信息无消费者——最终裁定为**删除**而非迁移。

## 3. 对治本方案的输入

所有根因均指向同一病根：**manifest 是冗余真源**。治本方案为删除（方案 D），详见 [manifests_cure_plan.md](manifests_cure_plan.md)。
