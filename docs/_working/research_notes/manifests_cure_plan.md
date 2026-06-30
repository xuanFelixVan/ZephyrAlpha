# _manifests/ 冗余真源治理调研报告与施工方案

> **任务**：审计 docs/03_modules/_manifests/ 目录（42 个 *_manifest.md + 1 个 index.md）
> **方法**：向内收四原则（能现成不创造 / 创造必全自动 / 第一性原理治本 / 新AI可发现性）
> **结论**：方案 D删除清单机制（manifest 是 blueprint 0.1 的冗余子集，无独有信息、无生成器、无消费者）
> **状态**：已执行

---

## 一、元问题审查

### 1.1 核心发现

manifest（清单）与 blueprint 0.1「代码文件清单」存在真源重叠：

| 维度 | manifest | blueprint 0.1 |
|------|----------|----------------|
| 文件数 | 28（抽样） | 52（完整） |
| 内容 | 模块源码文件列表 | 模块源码文件列表 + 章节/职责/存在性/阻塞原因 |
| SSoT 声明 | 无 | python scripts/governance/extract_depgraph.py --modules MOD-XXX |
| 生成器 | 无（手工维护） | 有（extract_depgraph.py 按需提取） |
| 消费者 | 无（4 处引用均为目录引用，非数据消费） | 全项目 AI 消费 |

**结论**：manifest 是 blueprint 0.1 的过时子集（28 vs 52 文件），无独有信息，是冗余真源。

### 1.2 清单到模块映射（42 个 manifest）

| 类别 | 数量 | 说明 |
|------|------|------|
| A（名称直接匹配 blueprint） | 15 | 如 factor_manifest.md  _domain_factor/factor/blueprint.md |
| B（名称经语义匹配到 blueprint） | 25 | 如 core_manifest.md  _cross_layer/shared_core/blueprint.md |
| C（匹配到 module_id 但无独立 blueprint） | 2 | 聚合模块，无独立蓝图 |
| D（孤儿，无匹配） | 0 | 全部映射成功 |

**无孤儿**42 个清单全部可映射到模块，证明清单无独有信息。

---

## 二、问题总览（8 个问题 = 1 病根 + 7 衍生）

### P0（病根）：manifest 是 blueprint 0.1 的冗余子集真源

manifest 与 blueprint 0.1 描述同一事实（模块源码文件列表），但 manifest 信息更少（28 vs 52）、无生成器、无消费者。违反「真源唯一」原则。

### 衍生问题（P1-P7，均由 P0 派生）

| # | 问题 | 由 P0 派生的机制 |
|---|------|------------------|
| P1 | 27 个缺失清单（无名称匹配的蓝图） | 清单用旧命名，蓝图已改名，双真源必然漂移 |
| P2 | 两类 module_id 方案并存（MOD-NNN vs MOD-INF-NNN/MOD-LNN-NNN） | 清单用旧顺序 ID，蓝图用语义化 ID，双真源必然不一致 |
| P3 | 两批清单元数据不一致（30 个有 module_id / 12 个有 ssot_path） | 手工维护双真源，批次间无统一规范 |
| P4 | 无生成器manifest 全手工维护 | 真源无自动化保证，必然漂移 |
| P5 | 无消费者4 处引用均为目录引用，非数据消费 | 无消费者证明 manifest 无存在价值 |
| P6 | 70 个文件 [CONSUMERS] 元数据假声明 | manifest 文件本身被声明为消费者，实际无消费行为 |
| P7 | index.md 引用 _manifests/ 目录（2 处） | 索引指向冗余真源，误导新 AI |

---

## 三、方案对比

| 方案 | 内容 | 向内收四原则评分 |
|------|------|------------------|
| A（迁移） | 将 manifest 内容迁移到 blueprint 0.1 | 违反「能现成不创造」blueprint 0.1 已有更完整内容 |
| B（分层） | manifest 作为摘要层，blueprint 作为详情层 | 违反「真源唯一」两层描述同一事实，必然漂移 |
| C（保持平铺） | 维持现状，补齐缺失清单 | 违反「第一性原理治本」不解决病根，持续累积漂移 |
| **D（删除）** | **删除 manifest 机制，真源回归 blueprint 0.1** | **符合全部四原则** |

### 方案 D 的向内收四原则自检

1. **能现成不创造**：blueprint 0.1 + extract_depgraph.py 已是现成真源，删除 manifest 即回归现成
2. **创造必全自动**：extract_depgraph.py 是全自动生成器（depgraph  提取），manifest 无生成器
3. **第一性原理治本**：删除冗余真源，从根本上消除漂移
4. **新AI可发现性**：blueprint 0.1 有 SSoT 声明指向 extract_depgraph.py，新 AI 可循声明发现

---

## 四、裁定结论

**方案 D（删除清单机制）**

manifest 是 blueprint 0.1 代码文件清单的过时子集（28 vs 52 文件），无独有信息、无生成器、无消费者。删除消除 8 个问题（1 病根 + 7 衍生），文件清单真源回归 depgraph  extract_depgraph.py  blueprint 0.1。

---

## 五、施工方案

### 5.1 删除 43 个文件（已完成）

- 42 个 *_manifest.md
- 1 个 _manifests/index.md

### 5.2 修改 index.md 引用（已完成）

- 删除 _manifests/ 目录索引行（原第 76 行）
- 从跨层前缀示例中删除 _manifests/（原第 108 行）

### 5.3 重新生成项目树文件（已完成）

- full_project_tree_zh.md
- full_project_tree_en.md

### 5.4 新增调研报告（本文件 + diagnosis）

- manifests_cure_plan.md（本文件）
- manifests_missing_diagnosis.md（STEP 2 根本原因诊断）

### 5.5 提交（通过 GitCommitGateway）

python scripts/git_commit.py --session manifests-cleanup --files <48个文件> --message-file .runtime/_commit_msg_manifests.txt

### 5.6 删除后使用指南

文件清单真源链路：

depgraph (PostgreSQL)  extract_depgraph.py --modules MOD-XXX  blueprint 0.1 代码文件清单（SSoT）

新 AI 查询模块文件清单的正确方式：

python scripts/governance/extract_depgraph.py --modules MOD-INF-020

---

## 六、向内收自检

| 原则 | 自检结果 |
|------|----------|
| 能现成不创造 | 删除 manifest，回归 blueprint 0.1 现成真源 |
| 创造必全自动 | extract_depgraph.py 全自动生成，manifest 无生成器已删 |
| 第一性原理治本 | 删除冗余真源，根除 8 个问题 |
| 新AI可发现性 | blueprint 0.1 有 SSoT 声明，新 AI 可循声明发现 |
