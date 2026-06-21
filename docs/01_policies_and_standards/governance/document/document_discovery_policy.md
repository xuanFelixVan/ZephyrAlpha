---
module_id: GOV-DOC-010
title: 文档可发现性策略
doc_type: policy
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "定义 ZephyrAlpha 项目中文档的发现机制——AI 和人类如何快速定位需要的文档。界定三种发现路径（索引入口→注册表查询→工具搜索），以及每种路径的优先级和适用场景。文档治理 7 维度中的 Discovery（可发现性）维度。对标 ITIL SACM Discovery + ISO 9001 §7.5 文件化信息索引 + K8s API Discovery（OpenAPI）。"
tags: [document, discovery, index, registry, search, governance, policy]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§4", why: "DocStatus 枚举——只关注 active/draft 文件，deprecated 文件不在发现范围内"}
  - {target: PS-REG-001, at: "full", why: "规则注册表是 module_id 搜索的权威索引"}
ai_autonomy: human_gated
---

# 文档可发现性策略

> module_id: GOV-DOC-010 | version: 1.0.0 | status: active | layer: cross_layer

---

## 1. 目的与范围

### 1.1 目的

确保在 ZephyrAlpha 项目中，AI 和人类都能**快速、准确、不依赖"之前知道"**地找到需要的文档。

**核心问题**：项目中已有 70+ 文档文件，目标是 1500+ 模块 × 每模块 5~15 条规则 = 7500~22500 条规则。如果每次找文件都要靠"记忆"或"猜路径"，系统将不可用。

### 1.2 本标准管理以下内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | 三种发现路径及其优先级 | 索引入口 → 注册表查询 → 工具搜索 |
| 2 | index.md 作为全局入口的使用规范 | index.md 是 docs/ 的全目录树入口 |
| 3 | 注册表文件的发现角色 | document-metadata-index.yaml（原 governance-rules-master-registry.yaml 重命名，master-document-inventory.yaml 已废弃） |
| 4 | module_id 搜索范式 | 通过 GOV-DOC-XXX / PS-STD-XXX 等编号定位文件 |
| 5 | "文件不存在"的判定流程 | 如何确认一个文件确实不存在（vs 只是没找到） |

### 1.3 本标准**不**覆盖以下内容

| # | 排除项 | 以哪个文件为准 |
|---|--------|-------------|
| 1 | 文件的具体命名规则 | file-naming-standard.md（GOV-DOC-003） |
| 2 | 文件的具体存放路径规则 | file-path-standard.md（GOV-DOC-004） |
| 3 | 目录结构定义 | directory-structure-standard.md（GOV-DOC-002） |
| 4 | 注册表文件的格式和生成方式 | document-metadata-index.yaml |
| 5 | 文档生命周期状态定义 | document-lifecycle-standard.md（GOV-DOC-006） |
| 6 | 搜索工具（grep/SearchCodebase）的具体用法 | 各工具自身文档 |

### 1.4 专业对标

| 来源 | 对标内容 |
|------|---------|
| ITIL SACM → Discovery | 配置管理系统必须提供配置项的发现机制——不需要人工记忆每个 CI 在哪里 |
| ISO 9001 §7.5.3 | 文件化信息的控制包括"确保文件可被发现和检索" |
| K8s API Discovery | `kubectl api-resources` + OpenAPI schema——声明式资源发现，不靠记忆 |
| Anthropic CLAUDE.md | "项目上下文文件应作为 AI 的第一个读取点"——index.md 同理 |
| Vibe Coding 社区 | 零记忆重启标准——任何新 AI session 必须能仅凭当前文件找到所有需要的东西 |

---

## 2. 发现原则

### 2.1 不可协商原则

| # | 原则 | 说明 |
|---|------|------|
| P1 | **index.md 是一切发现的起点** | 任何 AI session 找文件的第一步是读 index.md。不允许跳过 index.md 直接猜测路径 |
| P2 | **module_id 是通用钥匙** | 每个文件有唯一 module_id（如 GOV-DOC-010），通过 module_id 搜索可以精确命中目标文件 |
| P3 | **注册表优先于人脑记忆** | 如果注册表和"我记得的"不一致，以注册表为准。记忆会错，注册表不会 |
| P4 | **"不存在"必须走三级判定** | 不能"搜不到就说不存在"——必须走完 §3.4 的三级判定流程 |

### 2.2 禁止行为

| # | 禁止 | 说明 |
|---|------|------|
| ❌ 1 | 凭记忆猜测文件路径 | "这个文件应该在 governance/ai/ 下吧"——不允许 |
| ❌ 2 | 跳过 index.md 直接搜索 | 除非 index.md 中发现文件确实未注册，否则指数优先于搜索 |
| ❌ 3 | 因为一次搜索失败就声称"文件不存在" | 必须走完三级判定 |
| ❌ 4 | 手动维护注册表 | 注册表应由脚本自动生成（蓝图 D-004），手动维护会产生双写不一致 |

---

## 3. 三种发现路径

### 3.1 优先级排序

```
路径 1（首选）：index.md 入口 → 目录树定位 → 精确路径
    ↓ 如果 index.md 中未注册该文件
路径 2（次选）：注册表查询 → module_id 搜索 → 精确路径
    ↓ 如果注册表中也未找到
路径 3（兜底）：工具搜索 → grep / SearchCodebase → 手动确认
```

### 3.2 路径 1：index.md 全局入口 [首选]

**入口文件**：`docs/01_policies_and_standards/index.md`

**操作流程**：

```
1. 读取 index.md
   └── 查看 docs/ 全目录树 → 判断目标文件所在的大目录
2. 进入对应子目录
   └── 查看该目录下的文件列表 → 精确匹配文件名
3. 读取目标文件
   └── 验证 frontmatter module_id 与预期一致
```

**适用场景**：
- 找已知类别的文件（如"文档命名规则"→ governance/document/ 下）
- 浏览某个目录下的所有文件
- 新 AI session 初始对齐

**一票否决**：如果 index.md 中明确标注某文件不存在/已废弃，则路径 2 和 3 不需要继续——文件确实不存在。

### 3.3 路径 2：注册表查询 [次选]

**注册表文件**：

| 注册表 | 路径 | 覆盖范围 |
|--------|------|---------|
| 文档元数据索引 | `_registry/catalogs/document-metadata-index.yaml` | 所有 governance/ + meta/ 下的规则文件 |
| 文档清单 | `_registry/catalogs/document-metadata-index.yaml` | 所有文档文件的 inventory（auto-generated，取代已废弃的 master-document-inventory.yaml） |
| 规则注册表 | PS-REG-001 `_registry/catalogs/rule-registry.md` | 所有规则的索引 |

**操作流程**：

```
1. 根据目标文件的 module_id 前缀判断注册表
   └── PS-STD-XXX → meta/ 注册表
   └── GOV-XXX-XXX → governance/ 注册表
   └── DOM-LXX-XXX → domains/ 注册表
   └── OPS-XXX-XXX → operational/ 注册表
2. 打开对应注册表 → 搜索 module_id
   └── 找到 → 获取完整路径 → 读取文件
3. 如果注册表中未找到
   └── 该文件可能：（a）尚未注册 （b）已废弃 （c）不存在 → 进入路径 3
```

**适用场景**：
- 知道文件 module_id 但不知道路径（如 GREP 结果中引用了 GOV-DOC-010）
- index.md 中没有该文件的条目（新文件尚未更新到 index）
- 批量验证某个目录下应有哪些文件

### 3.4 路径 3：工具搜索 [兜底]

**可用工具**：

| 工具 | 适用场景 | 示例 |
|------|---------|------|
| `grep` / Grep | 搜索文件内容中的关键字或 module_id | `grep "GOV-DOC-010" --files-with-matches` |
| SearchCodebase | 自然语言搜索代码和文档 | "文档发现机制" |
| Glob | 按文件命名模式搜索 | `Glob "**/document-discovery*"` |
| `dir /s` 或 `find` | 按文件名搜索 | `dir /s /b *discovery*` |

**操作流程**：

```
1. 优先搜索 module_id（精确匹配）
   └── grep "GOV-DOC-010" -r --files-with-matches
2. 如果 module_id 未知，搜索关键字
   └── grep "文档发现" -r -l
3. 搜到结果 → 验证 frontmatter module_id → 确认是否正确文件
4. 搜索无结果 → 走三级"不存在"判定
```

### 3.5 "文件不存在"的三级判定

```
级别 1：index.md 显式声明不存在
    ├── 判定：文件确实不存在
    └── 处理：停止搜索，记录"已确认不存在"

级别 2：index.md 中未注册 + 注册表中也未找到
    ├── 判定：大概率不存在
    └── 处理：执行路径 3（工具搜索确认），仍找不到 → 确认不存在

级别 3：Gre/Grep/SearchCodebase 均无结果
    ├── 判定：确认不存在
    └── 处理：在 Session Log 中记录"已确认文件 X 不存在，进行了三级判定"

反模式：grep 一次没找到就说"文件不存在" ❌
```

---

## 4. module_id 驱动的发现

### 4.1 module_id 即地址

每个文件的 `module_id` 是一个**语义地址**——看到它就知道该文件属于哪个体系、哪个子域、序号。

```
GOV-DOC-010
 │   │   └── 序号（010）
 │   └────── 子域（DOC = document）
 └────────── 顶层域（GOV = governance）
```

**搜索模式**：

| 你想找 | 用这个搜索 |
|--------|----------|
| 所有文档治理文件 | `GOV-DOC-` |
| 所有元标准 | `PS-STD-` |
| 所有 AI 治理文件 | `GOV-AI-` |
| 所有任务治理文件 | `GOV-TASK-` |
| L02 层所有域规则 | `DOM-L02-` |
| 所有操作规则 | `OPS-` |

### 4.2 编号前缀速查表

> 完整前缀体系见 unified-numbering-standard.md（GOV-DOC-001）§二。

| 前缀 | 含义 | 文件位置 |
|------|------|---------|
| `PS-STD-` | 元标准 | meta/ |
| `PS-REG-` | 元注册表 | meta/ |
| `GOV-DOC-` | 文档治理 | governance/document/ |
| `GOV-AI-` | AI 治理 | governance/ai/ |
| `GOV-TASK-` | 任务治理 | governance/task/ |
| `GOV-SEC-` | 安全治理 | governance/security/ |
| `GOV-CMP-` | 合规治理 | governance/compliance/ |
| `GOV-ARCH-` | 架构治理 | governance/architecture/ |
| `GOV-DATA-` | 数据治理 | governance/data/ |
| `GOV-MOD-` | 模块治理 | governance/module/ |
| `DOM-L{XX}-` | 层域治理 | domains/L{XX}_*/ |
| `OPS-VC-` | VC 操作 | operational/vibe_coding/ |
| `OPS-DEV-` | DevOps 操作 | operational/devops/ |
| `OPS-MIG-` | 迁移操作 | operational/migration/ |

---

## 5. 发现效率约束

### 5.1 发现链深度限制

| 约束 | 值 | 对标 |
|------|---|------|
| 发现链最大深度 | 3 层 | GOV-DOC-009 引用链 ≤ 3 层；index → 注册表 → 文件 = 3 层 |
| 单次发现的注册表查询上限 | 2 个注册表文件 | PS-STD-011 AI 操作预算意识 |
| "找不到"的搜索尝试上限 | 3 次（3 种路径各 1 次） | 防止无限搜索消耗 Token |

**解释**：
- 如果 index.md → 注册表 → grep 都找不到，文件不存在
- 不要第四个工具、第五个工具继续搜——"找不到"本身就是发现结果

### 5.2 缓存规则

| 缓存内容 | 有效期 | 说明 |
|---------|--------|------|
| index.md 的目录树 | 本 Session 内有效 | 如果 session 中创建/删除了文件，需重新读取 index.md |
| 注册表中的文件→路径映射 | 本 Session 内有效 | 注册表文件本身被修改时需刷新 |
| Gre/SearchCodebase 结果 | 不缓存 | 磁盘随时变化，每次发现操作都重新搜索 |

---

## 6. 与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| index.md | 本标准指定的首要发现入口。index.md 是发现的第一步 |
| unified-numbering-standard.md | 本标准依赖其编号前缀体系来构建 module_id 搜索范式（§4.2） |
| directory-structure-standard.md | 本标准 §3.2 的路径 1 直接消费其目录树定义 |
| file-naming-standard.md | 文件命名规范确保文件名可被 Glob 模式发现 |
| file-path-standard.md | 路径规范确保文件位置可预测、可被路径映射发现 |
| document-lifecycle-standard.md | 生命周期状态决定文件是否在发现范围内（deprecated 文件不在发现范围） |
| document-control-policy.md | 本标准的 P3（注册表优先于记忆）→ DOC-001（SSoT 唯一原则） |
| document-metadata-index.yaml | 本标准 §3.3 路径 2 的主注册表 |

---

## 7. 变更记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-01 | 1.0.0 | 初始创建 + 同日审批。（1）定义三种发现路径（索引→注册表→搜索）、module_id 搜索范式、"文件不存在"三级判定流程；（2）对标 ITIL SACM Discovery + ISO 9001 §7.5 + K8s API Discovery；（3）补齐 7 维度中缺失的 Discovery 维度；（4）Owner 审批通过，`status: draft` → `active`。 |
