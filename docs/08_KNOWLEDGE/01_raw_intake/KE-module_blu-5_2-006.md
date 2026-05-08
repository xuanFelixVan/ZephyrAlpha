---
module_id: KE-module_blu-5_2-006
title: 5.2 禁碰规则列表（绝对不碰的东西）
category: module_blueprint
---

# 5.2 禁碰规则列表（绝对不碰的东西）

5.2 禁碰规则列表（绝对不碰的东西）

| 禁碰 ID | 描述 | 检测方式 | 示例 |
|:---:|------|---------|------|
| F-001 | 架构决策 | 关键词: "选择"/"决定用"/"架构"/"为什么" | "选择 SQLite 而不是 PostgreSQL" |
| F-002 | 跨模块契约 | 关键词: "CT-"/"契约"/"depends_on" | "MOD-INF-007 必须依赖 MOD-INF-012" |
| F-003 | 性能参数 | 关键词: "TTL"/"超时"/"配额"/"max_" | "TTL=30min" |
| F-004 | 安全策略 | 关键词: "密钥"/"加密"/"L4"/"secret" | "Secrets(L4) MUST 有轮替计划" |
| F-005 | 人为定义的阈值 | 关键词: ">"/"<"/"≥"/"阈值"/"门限" | "相似度 > 0.85" |
| F-006 | Owner/Maintainer 声明 | 关键词: "owner"/"belongs_to" | "owner: ZephyrAlpha-Owner" |

```python
FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    (r"(选择|决定(?:使用|采用)|架构选型)", "F-001 架构决策"),
    (r"(CT-\d|契约|depends_on.*MOD)", "F-002 跨模块契约"),
    (r"(TTL\s*=|超时\d+|配额\d+|max_\w+\s*=)", "F-003 性能参数"),
    (r"(secret|密钥|加密|L4\s+数据)", "F-004 安全策略"),
    (r"([><≥]+\s*\d+|阈值|门限|threshold)", "F-005 人为阈值"),
    (r"(owner:|belongs_to:|maintainer)", "F-006 Owner声明"),
]
```

---
