---
module_id: GOV-ENG-002
title: 文件头部标准（防幻觉/防漂移）
doc_type: standard
status: active
version: 1.0.0
date: "2026-05-16"
owner: Owner
layer: governance
classification: engineering
rule_form: declarative
stability: stable
safety_level: H
ai_autonomy: human_gated
depends_on:
  - GOV-ENG-001
  - PS-REG-012
  - PS-STD-001
---

# 文件头部标准 (GOV-ENG-002)

## §1 适用范围

在 100% AI 开发语境下，AI 可能读取或修改的所有文件 MUST 包含治理锚定表头。

### 需要表头

| file_category | 说明 | 示例 |
|---|------|------|
| code | 生产代码 | src/zephyr/**/*.py |
| script | 治理/工具脚本 | scripts/**/*.py |
| gate | 门禁定义 | src/zephyr/gates/*.yaml |
| registry | 注册表 | *_registry.yaml, *_manifest.yaml |
| contract | 契约定义 | shared/contracts/*.py, contracts/*.yaml |
| config | 配置文件 | config/*.yaml |
| data | 运行时数据 | data/**/*.yaml |
| doc | 文档 | docs/**/*.md |
| test | 测试 | tests/**/*.py |
| infra | 基础设施 | .sh, .ps1, .mmd |

### 豁免（不需要表头）

| 文件类型 | 豁免原因 |
|---------|---------|
| __init__.py | 仅做 import + __all__（按 §3.3 简化标记） |
| .db / .sqlite3 | 二进制数据库，AI 通过代码操作 |
| .bin / .index | 向量索引二进制产物 |
| .jsonl | append-only 日志，AI 只追加不修改 |
| .gitkeep / .gitignore | Git 内部文件 |
| .log | 只读日志 |
| test_fixtures/ 下的文件 | 测试夹具，故意模拟违规模式 |

---

## §2 文件类型→表头格式映射

| header_format | 格式 | 适用 file_category | 字段数 |
|---|------|---|:---:|
| A_full | .py 十字段注释头部 | code, script | 10 |
| A_test | .py 六字段简化版 | test | 6 |
| B_yaml | YAML 5 字段注释块 | gate, registry, contract(yaml), config, data | 5 |
| C_json | JSON _meta 字段 | contract(json), schema(json) | 5 |
| D_md | .md YAML frontmatter | doc | 已有规范 |
| E_shell | Shell/Mermaid 注释头部 | infra | 4 |
| exempt | 豁免 | — | 0 |

---

## §3 格式 A_full：.py 十字段注释头部

### 3.1 格式定义

```python
# [BLUEPRINT] {module_id} | {blueprint_path} | §{N}
# [MODULE] {full.module.path}
# [INVARIANTS] {不可违反的约束，分号分隔}
# [MODIFY-GUARD] {修改此文件必须同步更新的文件，分号分隔}
# [CONSUMERS] {依赖此文件的模块，分号分隔}
# [STABILITY] {frozen|stable|evolving|volatile}
# [SAFETY] {H|M|L}
# [AI_AUTONOMY] {immutable_core|human_gated|ai_modifiable}
# [ERROR_CONTRACT] {可抛异常列表，分号分隔}
# [TESTS] {测试文件路径，分号分隔}
```

### 3.2 各字段说明

| 字段 | 必填 | 说明 | 对齐 PS-REG-012 |
|---|:---:|------|:---:|
| [BLUEPRINT] | ✅ | 所属蓝图 module_id + 路径 + 章节号 | — |
| [MODULE] | ✅ | 完整 Python 模块路径 | — |
| [INVARIANTS] | ✅ | 此文件不可违反的约束 | — |
| [MODIFY-GUARD] | ✅ | 修改此文件必须同步更新的文件 | — |
| [CONSUMERS] | ⚠️ | 依赖此文件的模块 | — |
| [STABILITY] | ✅ | 文件稳定性 | ✅ |
| [SAFETY] | ✅ | 安全风险等级 | ✅ |
| [AI_AUTONOMY] | ✅ | AI 自治权限 | ✅ |
| [ERROR_CONTRACT] | ⚠️ | 此文件可抛出的异常列表 | — |
| [TESTS] | ⚠️ | 对应测试文件路径 | — |

### 3.3 __init__.py 简化标记

```python
"""[BLUEPRINT] MOD-INF-018
[AI_AUTONOMY] human_gated
"""
```

---

## §4 格式 A_test：.py 六字段简化版

```python
# [BLUEPRINT] {module_id} | {blueprint_path} | §{N}
# [MODULE] {full.module.path}
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
```

省略 [INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[ERROR_CONTRACT]——测试文件不定义不变量、不被消费、不抛业务异常。

---

## §5 格式 B_yaml：YAML 5 字段治理锚定

### 5.1 格式定义

```yaml
# --- 治理锚定 ---
# blueprint: {module_id} | {blueprint_path} | §{N}
# module_id: {module_id}
# stability: {frozen|stable|evolving|volatile}
# safety_level: {H|M|L}
# ai_autonomy: {immutable_core|human_gated|ai_modifiable}
# --- 治理锚定结束 ---
```

### 5.2 适用文件清单

| file_category | 路径模式 | 示例 |
|---|---------|------|
| gate | src/zephyr/gates/*.yaml | g1_ingest.yaml |
| registry | *_registry.yaml, *_manifest.yaml | _registry.yaml, script_manifest.yaml |
| contract(yaml) | docs/.../contracts/*.yaml | architecture-contract.yaml |
| config | config/*.yaml | flags.yaml, budget_policy.yaml |
| data | data/**/*.yaml | capability_cards/*.yaml, work_dags/*.yaml |
| architecture | architecture-model/**/*.yaml | _index.yaml, l00_data_source.yaml |

### 5.3 设计决策

用注释块而非 YAML 字段——避免破坏现有 YAML schema 解析。门禁有 gate_id/checks，能力卡有 capability_id/input_schema，直接加字段会导致解析失败。

---

## §6 格式 C_json：JSON _meta 字段

### 6.1 格式定义

```json
{
  "_meta": {
    "blueprint": "{module_id} | {blueprint_path} | §{N}",
    "module_id": "{module_id}",
    "stability": "{frozen|stable|evolving|volatile}",
    "safety_level": "{H|M|L}",
    "ai_autonomy": "{immutable_core|human_gated|ai_modifiable}"
  },
  ...
}
```

### 6.2 适用文件清单

| file_category | 路径模式 | 示例 |
|---|---------|------|
| contract(json) | *_manifest.json | ocp_manifest.json |
| schema(json) | schemas/*.json | frontmatter-schema.json |
| finding(json) | findings/*.json | SEC-LEAK-*.json |

---

## §7 格式 D_md：.md YAML frontmatter

已有规范，引用 [frontmatter-field-registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/frontmatter-field-registry.yaml)（REG-FRONTMATTER-001）。

必填字段：module_id, title, doc_type, status, version, date, owner。

---

## §8 格式 E_shell：Shell/Mermaid 注释头部

### 8.1 格式定义

```bash
# [BLUEPRINT] {module_id} | {blueprint_path} | §{N}
# [STABILITY] {frozen|stable|evolving|volatile}
# [SAFETY] {H|M|L}
# [AI_AUTONOMY] {immutable_core|human_gated|ai_modifiable}
```

### 8.2 适用文件清单

| 文件类型 | 路径模式 | 示例 |
|---------|---------|------|
| .sh | scripts/hooks/*.sh | contract-fingerprint-hook.sh |
| .ps1 | scripts/**/*.ps1 | test_concurrent_safety.ps1 |
| .mmd | docs/**/diagrams/*.mmd | c4-l1-system-context.mmd |

---

## §9 枚举值定义（SSoT）

### 9.1 stability 枚举

| 值 | 含义 | AI 行为约束 |
|---|------|-----------|
| frozen | 冻结——不可变更 | 禁止修改 |
| stable | 稳定——通过变更门控可修改 | 需门控 |
| evolving | 演进中——可频繁修改 | — |
| volatile | 易变——AI 可自主调整 | — |

### 9.2 safety_level 枚举

| 值 | 含义 | AI 行为约束 |
|---|------|-----------|
| H | 高风险——涉及安全关键路径 | 修改前 MUST 触发安全检查 |
| M | 中风险——影响系统稳定性 | 修改后 MUST 验证 |
| L | 低风险——辅助功能 | — |

### 9.3 ai_autonomy 枚举

| 值 | 含义 | AI 行为约束 |
|---|------|-----------|
| immutable_core | 不可变核心——AI 只能读 | 禁止任何修改 |
| human_gated | 人工闸门——AI 可提议，需 Owner 批准 | 未批准禁止修改 |
| ai_modifiable | AI 可修改 | — |

### 9.4 header_format 枚举（新增）

| 值 | 含义 | 适用文件 |
|---|------|---------|
| A_full | .py 十字段完整版 | code, script |
| A_test | .py 六字段简化版 | test |
| B_yaml | YAML 5 字段注释块 | gate, registry, contract(yaml), config, data |
| C_json | JSON _meta 字段 | contract(json), schema(json) |
| D_md | .md YAML frontmatter | doc |
| E_shell | Shell/Mermaid 注释 | infra |
| exempt | 豁免 | — |

### 9.5 file_category 枚举（新增）

| 值 | 含义 | 示例 |
|---|------|------|
| code | 生产代码 | src/zephyr/**/*.py |
| script | 治理/工具脚本 | scripts/**/*.py |
| gate | 门禁定义 | src/zephyr/gates/*.yaml |
| registry | 注册表 | *_registry.yaml |
| contract | 契约定义 | shared/contracts/*.py |
| config | 配置文件 | config/*.yaml |
| data | 运行时数据 | data/**/*.yaml |
| doc | 文档 | docs/**/*.md |
| test | 测试 | tests/**/*.py |
| infra | 基础设施 | .sh, .ps1, .mmd |

### 9.6 对齐声明

stability / safety_level / ai_autonomy 三个枚举与 PS-REG-012 完全一致，零冲突。修改此标准 MUST 同步检查 PS-STD-001 对应章节。

---

## §10 表头状态机

### 10.1 状态定义

| 状态 | 含义 | 表头特征 |
|---|------|---------|
| UNHEADERED | 文件存在但无表头 | 无任何治理锚定标记 |
| ANCHORED | 文件有表头 + 蓝图引用 + 注册表覆盖 | 表头完整，蓝图 §0.1/§11 已更新 |
| STABILIZED | 文件通过门控验证，stability 提升 | [STABILITY] 为 stable 或 frozen |
| LOCKED | 文件锁定，禁止 AI 修改 | [STABILITY]=frozen 或 [AI_AUTONOMY]=immutable_core |

### 10.2 状态转换

| 转换 | 触发条件 | 必须操作 |
|---|---------|---------|
| UNHEADERED → ANCHORED | 执行锚定 7 步操作 | 添加表头 + 更新蓝图 §0.1/§11 + 更新注册表 + 验证双向对齐 |
| ANCHORED → STABILIZED | stability 从 evolving/volatile 提升为 stable | 更新表头 [STABILITY] + 蓝图 §0.1 状态列 |
| STABILIZED → LOCKED | stability=frozen 或 ai_autonomy=immutable_core | 更新表头 + freeze_manifest.yaml 注册 |
| 任何 → UNHEADERED | 蓝图重构/文件迁移导致蓝图引用失效 | 重新执行锚定 7 步 |
| 任何 → REMOVED | 文件被删除（通过 RULE-THREE 三步审判） | 蓝图 §0.1 移除条目 + 注册表移除条目 |

### 10.3 状态与 AI 行为映射

| 状态 | AI 能做什么 |
|---|---------|
| UNHEADERED | 只读。禁止修改——先完成锚定 |
| ANCHORED | 按 [AI_AUTONOMY] 和 [STABILITY] 约束操作 |
| STABILIZED | 按 [AI_AUTONOMY] 约束操作，修改需通过门控 |
| LOCKED | 只读。任何修改必须经 Owner 批准 |

---

## §11 锚定操作清单

锚定一个文件时 MUST 执行以下 7 步，任何一步失败 → 不算完成：

| 步骤 | 操作 | 验证 |
|---|------|------|
| 1 | 判断归属蓝图 | 蓝图 module_id 和路径已确定 |
| 2 | 给文件添加表头 | 表头格式与 header_format 映射一致 |
| 3 | 更新蓝图 §0.1 文件清单 | 文件条目已添加 |
| 4 | 更新蓝图 §11 产出物存放目录 | 产出物条目已添加 |
| 5 | 更新蓝图 §10 依赖（如引入新依赖） | 依赖声明已添加 |
| 6 | 更新注册表 | script_manifest.yaml / __init__.py / _registry.yaml 已更新 |
| 7 | 验证双向对齐 | Grep 蓝图→文件 + Grep 文件→蓝图 均命中 |

---

## §12 验证

| 验证方式 | 命令/方法 |
|---------|---------|
| 表头完整性检查 | `python scripts/governance/validate_file_headers.py`（待创建） |
| 枚举值一致性 | [STABILITY]/[SAFETY]/[AI_AUTONOMY] ↔ PS-REG-012 定义 |
| 蓝图-代码双向对齐 | 蓝图 §0.1 文件清单 ↔ 代码 [BLUEPRINT] 字段互相验证 |
| 状态机合规 | LOCKED 文件无 AI 修改记录 |
| CI 集成 | pre-commit hook 检查表头完整性 |

---

## §13 与其他标准的关系

| 标准 | module_id | 关系 |
|---|-----------|------|
| 代码构建标准 | GOV-ENG-001 | GOV-ENG-001 §7 引用本标准 |
| 元数据注册表 | PS-REG-012 | 枚举值 SSoT，修改 MUST 同步 |
| 元标准 | PS-STD-001 | 修改本标准 MUST 同步检查 PS-STD-001 |
| 压缩工作流标准 | GOV-DOC-011 | 规格化时 STEP 5 检查表头完整性 |
| frontmatter 字段注册表 | REG-FRONTMATTER-001 | 字段数据 SSoT，新增枚举 MUST 同步 |
