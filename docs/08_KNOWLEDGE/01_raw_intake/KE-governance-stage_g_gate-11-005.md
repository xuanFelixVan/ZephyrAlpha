---
module_id: KE-governance-stage_g_gate-11-005
title: 五、违规检测规则（Stage G GATE-11 实施范围）
category: governance
---

# 五、违规检测规则（Stage G GATE-11 实施范围）

五、违规检测规则（Stage G GATE-11 实施范围）

pre-commit hook 将检测以下违规：

| 违规类型 | 检测规则 | 豁免白名单 |
|---|---|---|
| 新建文件名包含大写字母 | 正则 `[A-Z]` 命中文件名主体 | `AGENTS.md` / `README.md` |
| 新建文件名包含版本号后缀 | 正则 `-v\d+` / `-round\d+` / `-iteration\d+` | **技术栈专有名词词组**（见 §2.8） |
| 新建状态快照文件带日期后缀 | 正则 `-\d{8}` | LATEST 白名单 |
| ADR 使用嵌套编号 | 正则 `adr-\d+-\d+` | — |
| ADR 缺失 kebab 尾缀 | 正则 `adr-\d{4}\.md` (无中间连字符) | `_template.md` |
| module_id 含 `EA-` / `PROD-` 等 scope 前缀 | frontmatter 字段正则 | 历史 archive/ 目录 |
| ADR module_id 与文件名编号不一致 | 对比 frontmatter 与文件名 | — |

---
