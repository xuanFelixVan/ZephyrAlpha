---
module_id: KE-408
title: 5.2.2 DOMAIN 命名规则
category: documentation
ttl: permanent
---

# 5.2.2 DOMAIN 命名规则

5.2.2 DOMAIN 命名规则

| 规则 | 说明 | 正确 | 错误 |
|------|------|------|------|
| 大写字母 + 连字符 | DOMAIN 部分用大写，层级用连字符分隔 | `GOV-SEC` | `gov-sec`, `GOV_SEC` |
| 层级编码 | 顶级域（PS/GOV/OPS/DOM）+ 子域缩写 | `GOV-SEC` | `SECURITY` |
| 子域缩写 2~4 字符 | 短到可读，长到无歧义 | `SEC`, `CMP`, `ARCH` | `SECURITY`, `COMPLIANCE` |
| 与物理目录一一对应 | 看到前缀就知道文件在哪 | `GOV-SEC` → `governance/security/` | 前缀和目录不对应 |
