---
module_id: KE_025_ENCODING_DEADLINKS_POSTMORTEM
version: 1.0.0
status: Active
created_date: 2026-04-16
last_updated: 2026-04-16
owner: Project Owner
layer: layer_08
category: postmortem
tags:
  - encoding-corruption
  - dead-links
  - dual-editor
  - file-elimination-pipeline
  - governance
parent_document: ../INDEX.md
---

# KE-025：编码损坏 & 断链积累的根因分析与预防规则

> **类型**：事后复盘（Post-mortem）+ 永久规则提炼
> **适用范围**：所有 AI 工具（Cursor / Trae）在本项目的任何操作
> **核心原则**：此文档记录"为什么会发生"，并提炼出"永远不能再发生"的操作规则

---

## 一、编码损坏问题

### 1.1 事件描述

`docs/09_AUDIT/STANDARDS/` 下共 8 个核心标准文档（含 `adr-standard.md`、
`quality-standard.md`、`path-and-reference-standard.md` 等）出现系统性编码损坏：
frontmatter 字段值及正文标题中出现大量阿拉伯文、西里尔文、波斯文字符，正文内容
变为不可读的乱码块。

**损坏程度**：多个文件从第 11 行起即出现乱码，主体内容完全损坏，并非仅尾部追加块。
之前执行的"尾部伪造块切除"只移除了文件末尾的重复 frontmatter 块，主体损坏未修复。

### 1.2 根因链

```
触发条件：Trae 的 files.autoGuessEncoding = true（或未显式设为 false）

执行路径：
  UTF-8 编码的中文文档
    │
    ▼  Trae 打开文件时，autoGuessEncoding 将文件误判为 GBK / Latin-1 / Windows-1256
    │
    ▼  Trae 在此错误编码假设下渲染文件内容（显示正常，但内部字节解释已错误）
    │
    ▼  Trae 保存文件时，以"猜测到的编码"将内容回写磁盘
    │
    ▼  磁盘上的文件变为 GBK/Latin-1 编码（或 UTF-8 但内容为 mojibake）
    │
    ▼  Cursor 以 UTF-8 重新打开文件
    │
    ▼  字节序列被 UTF-8 解释，产生阿拉伯文/西里尔文乱码
```

**关键放大因素**：
1. 损坏发生时尚无 `doc-guard-pre-commit` D-05 编码检测 hook，损坏文件直接入库
2. 损坏的文件被后续 session 继续引用，被当作"权威标准"读取但内容实际是乱码
3. 历史修复操作（尾部切除）只处理症状（重复 frontmatter），未识别主体已损坏

### 1.3 检测工具

```bash
# 全量编码扫描（运行后输出损坏文件列表）
python scripts/hooks/doc_guard_pre_commit.py --scan-encoding

# pre-commit 拦截（每次 commit 自动执行，类型 D-05）
# 已注册于 .pre-commit-config.yaml: id: doc-guard-pre-commit
```

### 1.4 永久规则（提炼自本事件）

| 规则 | 说明 |
|------|------|
| **R-ENC-01** | 发现乱码文件，必须用 `git checkout HEAD -- <file>` 整文件还原，禁止手动修改乱码字符 |
| **R-ENC-02** | 若 HEAD 版本也已损坏，向前追溯 `git log --oneline -- <file>` 找干净版本 |
| **R-ENC-03** | 若所有历史版本均已损坏，使用同目录健康文件为模板，按标准名称/用途**人工重写全文**，不得修补 |
| **R-ENC-04** | Trae 每次打开项目第一步：确认 `files.autoGuessEncoding = false` 且 `files.encoding = utf8` |
| **R-ENC-05** | 切换编辑器后必须运行编码扫描，再开始编辑 |
| **R-ENC-06** | 所有 Python 脚本创建/写入文件必须显式声明 `encoding='utf-8'` |

---

## 二、断链积累问题

### 2.1 事件描述

`SENTINEL_L1_SCAN_LATEST.md`（生成于 2026-04-16T09:25Z）报告 **435 条无效内链**，
占总 Markdown 内链（4165 条）的 10.4%。

`BROKEN_LINK_THRESHOLD` 被临时上调至 500（原为 100），以允许在治理重构期间提交。
这是主动接受的技术债务，不是系统失控。

### 2.2 断链的三类根因

#### A 类：文件消除流水线清理不彻底（占比最大，约 60%）

```
操作：Wave 1 删除 307 个 openclaw-l2-* 扫描产物文件
问题：只删除了文件，未同步更新所有指向它们的 INDEX.md 引用
结果：docs/01_FRAMEWORK/INDEX.md、docs/02_FACTOR_LIBRARY/INDEX.md 等
      仍包含指向已删除文件的链接 → 批量产生断链
```

**规则**：文件消除流水线的每个 wave 必须包含"引用清理"步骤，不得只删文件。

#### B 类：蓝图归档迁移索引未同步（约 15%）

```
操作：将 smart-order-router-blueprint.md、portfolio-optimization-layer-blueprint.md、
      strategy-execution-layer-blueprint.md 归档至 docs/06_ARCHIVE/
问题：docs/03_BLUEPRINTS/INDEX.md、docs/00_OVERVIEW/INDEX.md 等原有引用
      未从旧路径更新到新归档路径，也未移除已归档条目
结果：指向 docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/ 的旧链接断裂
```

**规则**：任何 `git mv` 操作后，必须立即对旧路径执行反向引用扫描并批量更新。

#### C 类：预规划"占位链接"（约 25%）

```
场景：docs/02_ARCHITECTURE/MODULE_INVENTORY.md 等文件包含指向尚未创建的
      CONSTRUCTION_PLAN_L01-L07 的链接，这些是故意写入的"规划链接"
问题：链接检测器无法区分"规划中的占位"和"真实断链"
结果：被统计为断链，推高断链总数
```

**规则**：规划链接必须使用注释语法或约定前缀标记，避免被检测器误判：
```markdown
<!-- PLANNED: ../04_CONSTRUCTION/PLANS/CONSTRUCTION_PLAN_L01_DATA_PROCESSING.md -->
```
或在 frontmatter 中声明 `link_status: planned`。

### 2.3 永久规则（提炼自本事件）

| 规则编号 | 触发时机 | 操作要求 |
|---------|---------|---------|
| **R-LINK-01** | 删除任何 `.md` 文件前 | 必须先运行 `scripts/audit/mandatory_inbound_guard.py` 找到所有指向此文件的引用，并在同一 commit 中更新这些引用 |
| **R-LINK-02** | `git mv` / 文件归档 / 路径变更 | 移动后立即搜索旧路径的所有引用（用 `rg "旧文件名"` 全库搜索），同一 commit 内完成引用更新 |
| **R-LINK-03** | 文件消除流水线每个 wave | wave 完成后必须运行 `python scripts/audit/sentinel_l1_governance_scan.py` 确认断链数量未超出本 wave 操作的预期增量 |
| **R-LINK-04** | 写入"规划中"的链接 | 使用 HTML 注释格式 `<!-- PLANNED: path -->` 或加 `_planned` 后缀，不得用普通 Markdown 链接写入尚不存在的文件路径 |
| **R-LINK-05** | 断链阈值 | 正常生产状态目标 ≤ 100 条；治理重构过渡期最高 500 条（当前临时值）；完成流水线后必须压回 100 |

---

## 三、两类问题的共同根因

两个问题表面不同，底层有同一个结构性原因：

> **AI 工具执行了"只完成直接任务"的操作，没有执行"维持完整性的副作用操作"**

| 直接任务（被执行） | 完整性副作用操作（被遗漏） |
|------------------|------------------------|
| 删除 openclaw-l2-* 文件 | 更新所有引用这些文件的 INDEX.md |
| 归档蓝图文件 | 更新所有指向旧路径的引用 |
| Trae 保存编辑的文件 | 验证保存后文件编码仍为 UTF-8 |
| 修复文件尾部伪造块 | 检查正文是否同样存在编码损坏 |

**预防原则**：任何涉及文件路径变化（删除/移动/归档）或文件内容变化（保存/编码）的操作，
都必须将"完整性维护"作为同一操作的组成部分，而非后续可选步骤。

---

## 四、修复路径（当前技术债务的处置方案）

### 4.1 标准文档修复（8 个损坏文件）

优先级顺序：
1. `git log --oneline -- <file>` 找最近的干净版本
2. 若无干净历史版本 → 使用 `docs/09_AUDIT/STANDARDS/decision-record-standard.md`
   等健康文件为结构模板，按标准名称人工重写
3. 不可接受的方案：在损坏文件上追加修复块、混合中文与乱码段落

相关工具：
```bash
# 确认哪些标准文件仍有损坏
python scripts/hooks/doc_guard_pre_commit.py --scan-encoding
```

### 4.2 断链修复（435 条 → 目标 ≤ 100）

见配套 Playbook：`docs/01_GOVERNANCE/PLAYBOOKS/dead-link-repair-playbook.md`

处置顺序：
1. **先清 A 类**（openclaw-l2-* 引用残留）：批量从 INDEX.md 中移除指向已删文件的条目，效果最大
2. **再清 B 类**（归档迁移）：将指向旧路径的链接更新为 `docs/06_ARCHIVE/` 下的新路径
3. **最后处理 C 类**（规划占位）：将规划链接改写为 `<!-- PLANNED: -->` 注释格式

---

## 五、关联资源

| 资源 | 路径 |
|------|------|
| 编码检测工具 | `scripts/hooks/doc_guard_pre_commit.py --scan-encoding` |
| 断链扫描工具 | `scripts/audit/sentinel_l1_governance_scan.py` |
| 当前断链状态 | `docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_LATEST.md` |
| 断链修复 Playbook | `docs/01_GOVERNANCE/PLAYBOOKS/dead-link-repair-playbook.md` |
| 编码安全规则 | `AGENTS.md` § 八、编码安全规则 |
| 链接维护规则 | `AGENTS.md` § 十一、链接维护契约 |
