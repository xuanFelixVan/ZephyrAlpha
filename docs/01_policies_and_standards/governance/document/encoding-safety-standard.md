---
module_id: GOV-DOC-005
title: 编码安全规范
doc_type: standard
status: active
version: 1.2.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "强制所有文件使用 UTF-8 编码，防止编辑器自动编码检测导致文件损坏。"
tags: [encoding, safety, utf-8, governance]
rule_form: declarative
scope: global
stability: stable
verifiability: automated
---

# 编码安全规范

> **目的**：强制所有文件使用 UTF-8 编码，防止 Trae 编辑器的自动编码检测导致文件损坏。
>
> **老树教训**：Trae 的 `files.autoGuessEncoding` 选项将 UTF-8 文件误判为 GBK/Latin-1，保存时以错误编码写回，产生双重编码乱码（表现为文件末尾出现阿拉伯文/西里尔文字符）。Cursor 以 UTF-8 重新读取后，乱码字节暴露。

## 〇、目的与范围

### 〇.1 目的

强制 ZephyrAlpha 项目中所有文件的编码格式为 UTF-8，并提供编码损坏的识别、修复和预防机制。确保无论使用 Trae 还是 Cursor 编辑器，文件内容不会被编辑器自动编码检测损坏。

### 〇.2 本标准管理以下内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | Trae/Cursor 编辑器的编码安全配置 | `files.autoGuessEncoding` 必须为 false |
| 2 | Python 文件的编码强制要求 | `open()` 必须显式指定 `encoding='utf-8'` |
| 3 | PowerShell 脚本的编码强制要求 | 禁止使用默认编码参数写文件 |
| 4 | 编码损坏的识别信号 | 4 种典型症状 |
| 5 | 编码损坏的唯一修复流程 | git checkout 恢复 + check_encoding.py 验证 |

### 〇.3 本标准**不**覆盖以下内容

| # | 排除项 | 以哪个文件为准 |
|---|--------|-------------|
| 1 | 文件的命名规范 | file-naming-standard.md（GOV-DOC-003） |
| 2 | 文件的存放路径 | file-path-standard.md（GOV-DOC-004） |
| 3 | 文件的生命周期管理 | document-lifecycle-standard.md（GOV-DOC-006） |
| 4 | 文件的删除安全门禁 | file-operation-safety-policy.md（GOV-DOC-007） |
| 5 | Python 代码风格（非编码相关） | PEP 8 |
| 6 | 编辑器选择和使用建议 | 本文档仅限于 Trae/Cursor 的编码配置 |

### 〇.4 专业对标

| 来源 | 对标内容 |
|------|---------|
| Unicode 标准 §2.5 | UTF-8 编码定义——4 字节可变长编码，ASCII 兼容。本文档的"强制 UTF-8"基于此标准 |
| W3C Character Model | "所有内容 MUST 使用 UTF-8 编码"——Web 标准中的编码铁律，本文档将其延伸至本地文件 |
| Python PEP 8 §Source File Encoding | "Python 3 默认 UTF-8，但仍建议显式声明 encoding 参数"——本文 §二.2 对应 |
| ITIL Change Control | 编辑器的自动编码检测是一个"计划外变更"风险——本文 §一 的根因分析即基于此视角 |

---

## 一、根因机制

```
正常 UTF-8 文件
    ↓ Trae autoGuessEncoding=true 误判为 GBK/Latin-1
    ↓ 以错误编码写入磁盘
    ↓ Cursor 以 UTF-8 读取
显示乱码（文件末尾出现阿拉伯/西里尔字符）
```

## 二、强制配置要求

### Trae 编辑器（必须配置）

```json
{
  "files.autoGuessEncoding": false,
  "files.encoding": "utf8"
}
```

**在开始任何 Trae session 之前，必须确认以上配置已生效。**

### Python 脚本（必须显式指定编码）

```python
# 正确
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 错误（禁止）
with open(file_path, 'w') as f:  # 使用系统默认编码
    f.write(content)
```

### PowerShell 脚本（禁止使用默认参数）

```powershell
# 正确
[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)

# 错误（禁止）
echo "content" > file.md          # Windows 默认 UTF-16 LE
Out-File -FilePath file.md        # 默认编码非 UTF-8
```

## 三、编码损坏的识别信号

| 信号 | 含义 |
|------|------|
| 文件末尾出现阿拉伯文/西里尔文字符 | 双重编码损坏 |
| frontmatter 字段值出现非中英文字符 | 主体可能全部损坏 |
| 正文标题出现非中英文字符 | 至少局部损坏 |
| 尾部出现重复 frontmatter 块 | 双重编码追加导致 |

## 四、编码损坏的修复流程（唯一合法方式）

```bash
# 步骤 1：确认损坏范围
python scripts/hooks/check_encoding.py

# 步骤 2：从 git 历史恢复（推荐）
git checkout HEAD -- <损坏文件路径>

# 步骤 3：若 HEAD 也已损坏，找干净版本
git log --oneline -- <损坏文件路径>
git show <干净commit>:<损坏文件路径> > temp.md
# 对比确认后替换

# 步骤 4：确认修复
python scripts/hooks/check_encoding.py
```

## 五、绝对禁止操作

| 禁止操作 | 替代方案 |
|---------|---------|
| 用文本编辑器逐字修改乱码字符 | `git checkout -- <file>` 整文件还原 |
| PowerShell `echo` / `Out-File` 默认参数写 `.md` | Python `Path(f).write_text(content, encoding='utf-8')` |
| Python `open(f, 'w')` 不指定 encoding | 必须加 `encoding='utf-8'` |
| 两个编辑器同时打开同一文件编辑 | 同一时刻只用一个编辑器 |
| 在损坏文件上追加"修复块"或混合段落 | 从 git 历史恢复整个文件 |
| 将损坏文件当作参考资料使用 | 内容不可信，必须先修复 |

## 六、与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| file-naming-standard.md（GOV-DOC-003） | 本标准不管理文件命名——但要求文件名不含非 UTF-8 字符 |
| document-lifecycle-standard.md（GOV-DOC-006） | 损坏文件的修复流程可能触发生命周期事件——如从 git 恢复后需重新审批 |
| file-operation-safety-policy.md（GOV-DOC-007） | 修复损坏文件前需通过安全三问——确认无引用丢失 |
| AGENTS.md §4 | 编码安全是三条硬规则之一——"禁止用 PowerShell echo/Out-File 默认参数写 .md 文件" |

## 七、变更记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-04-22 | 1.0.0 | 初始创建。定义 UTF-8 强制编码规则、Trae/Cursor 配置要求、Python/PowerShell 编码规范、损坏识别与修复流程。 |
| 2026-05-01 | 1.1.0 | 结构对齐。（1）新增 §〇 目的与范围（§〇.2 管理内容 + §〇.3 不覆盖内容 + §〇.4 专业对标）；（2）新增 §六 与其他规则的关系；（3）新增 §七 变更记录。对齐 templates/policy-template.md 强制结构。 |
