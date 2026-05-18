---
module_id: GOV-AI-004
title: 双编辑器协作规则
doc_type: policy
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义 Cursor �?Trae 两个编辑器的分工规则、文件锁定机制和编码安全规范�?
tags: [ai, dual-editor, collaboration, governance]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
depends_on:
  - {target: AGENTS.md, at: "§4", why: "编码安全硬规则——PowerShell echo/Out-File 禁止 + Python encoding 强制UTF-8"}
---

# 双编辑器协作规则

> **目的**：定�?Cursor �?Trae 两个编辑器的分工规则、文件锁定机制和编码安全规范，防止双编辑器并行工作导致的编码损坏和文件冲突�?
>
> **铁律**：MUST 设置 `files.autoGuessEncoding=false`——否则 UTF-8 被误判为 GBK/Latin-1 → 双重编码乱码（文件末尾出现阿拉伯文/西里尔文字符）。

## 一、Cursor vs Trae 分工

| 任务类型 | 使用编辑�?| 原因 |
|---------|----------|------|
| 架构设计、ADR 编写 | Cursor | 需要高级推理能�?|
| 规范文档编写 | Cursor | 需要高级推理能�?|
| 代码实现（src/�?| Cursor | 代码质量要求�?|
| 批量文件操作�?5 个文件） | Trae | 免费模型适合批量操作 |
| 文件消除流水�?| Trae | 免费模型适合批量操作 |
| 蓝图安全流水�?| Trae | 免费模型适合批量操作 |
| 校验脚本执行 | Trae | 简单执行任�?|
| 编码扫描 | Trae | 简单执行任�?|

## 二、编码安全规则（强制�?

### Trae 必须配置

```json
{
  "files.autoGuessEncoding": false,
  "files.encoding": "utf8"
}
```

**在开始任�?Trae session 之前，必须确认以上配置已生效�?*

### 切换编辑器前的检查清�?

切换�?Cursor �?Trae 之前�?
- [ ] 确认 Cursor 中所有文件已保存并关�?
- [ ] 确认没有未提交的修改（或已暂存）

切换�?Trae �?Cursor 之前�?
- [ ] 确认 Trae 中所有文件已保存并关�?
- [ ] 运行编码扫描：`python scripts/hooks/check_encoding.py`（如果脚本不存在，用 `Get-Content -Encoding UTF8 <文件路径> -First 5` 手动验证�?
- [ ] 确认没有编码损坏文件

### 禁止操作

| 禁止操作 | 原因 |
|---------|------|
| 两个编辑器同时打开同一文件进行编辑 | 编码损坏风险 |
| �?Trae 中编�?`.cursor/rules/` 下的文件 | Trae 无权修改 Cursor 规则 |
| 使用 `echo` 重定向创�?`.md` 文件 | Windows 默认 UTF-16 LE �?GBK |
| 使用 PowerShell `Out-File` 默认参数创建文件 | 默认编码�?UTF-8 |
| Python `open(f, 'w')` 不指�?encoding | 必须�?`encoding='utf-8'` |

## 三、编码损坏的识别信号

| 信号 | 含义 |
|------|------|
| 文件末尾出现阿拉伯文/西里尔文字符 | 双重编码损坏 |
| frontmatter 字段值出现非中英文字�?| 主体可能全部损坏 |
| 正文标题出现非中英文字符 | 至少局部损�?|

## 四、编码损坏的修复流程（唯一合法方式�?

```bash
# 1. 确认损坏范围
python scripts/hooks/check_encoding.py

# 2. �?git 历史恢复（推荐）
git checkout HEAD -- <损坏文件路径>

# 3. �?HEAD 也已损坏，找干净版本
git log --oneline -- <损坏文件路径>
git show <干净commit>:<损坏文件路径> > temp.md
# 对比确认后替�?

# 4. 确认修复（如�?check_encoding.py 不存在，参见 §�?fallback 手動驗證�?
python scripts/hooks/check_encoding.py
```

### 绝对禁止

| 禁止操作 | 替代方案 |
|---------|---------|
| 用文本编辑器逐字修改乱码字符 | `git checkout -- <file>` 整文件还�?|
| 在损坏文件上追加"修复�? | �?git 历史恢复整个文件 |
| 将损坏文件当作参考资料使�?| 内容不可信，必须先修�?|

## 五、文件锁定机�?

当某个文件正在被一个编辑器编辑时，另一个编辑器不得同时编辑该文件�?

**实现方式**（当前为手动约定，未来可自动化）�?
- �?Session Log 中记录当前正在编辑的文件列表
- 切换编辑器前，确认对方编辑器没有打开相同文件

---

## 六、编辑器故障应�?

### Cursor 崩溃 / 无响�?

1. 确认 Cursor 的本地未保存更改是否还在——重�?Cursor 后通常会自动恢复未保存文件
2. 如果文件已保存但怀疑内容损坏：优先运行 `python scripts/hooks/check_encoding.py` 验证编码完整�?
3. **如果 `check_encoding.py` 不存�?*（脚本尚未实现）：在 PowerShell 中运�?`Get-Content -Encoding UTF8 <文件路径> -First 5` 手动验证文件�?5 行是否正常，确认无乱码或 BOM 异常
4. 如果重启后文件列表异常（如打开文件丢失）：记录�?Session Log，标�?CURSOR-CRASH-YYYYMMDD"，后�?session 续接时需逐文件验证状�?

### Trae 假死 / 卡住

1. 等待 30 秒——Trae 在执行批量操作时可能出现短暂无响�?
2. 如果 30 秒后仍未恢复：强制终�?Trae 进程
3. 重启 Trae 后：运行编码扫描确认无残留损坏文�?
4. 记录�?Session Log：标�?TRAE-HANG-YYYYMMDD"，明确标注假死时正在执行的任�?

### 通用原则

- 故障后切换到另一编辑器继续工作前，必须先完成上述恢复步骤和编码扫�?
- 故障事件必须写入 Session Log，供下一�?session 确认状�?
- 如果同一编辑器在 1 小时内崩�?�?2 次，暂停工作并通知 Owner
