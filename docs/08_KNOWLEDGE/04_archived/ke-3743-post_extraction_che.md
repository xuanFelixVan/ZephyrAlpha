---
module_id: KE-3593------post-extraction-che-000
title: 4.5.3 后验检查（post_extraction_checks，写完后执行）
category: governance
ttl: permanent
---

# 4.5.3 后验检查（post_extraction_checks，写完后执行）

4.5.3 后验检查（post_extraction_checks，写完后执行）

| 检查 | 通过条件 |
|------|---------|
| 提取内容非空 | `len(body.strip()) > 0` |
| 提取 frontmatter 合法 | 符合 `kms-entry-schema` |
| 无数据丢失 | 源文档关键段落抽查命中率 ≥ 90% |
| 交叉引用有效 | 新 KE 中所有 `[[KE-XXX]]` 可解析 |

后验失败任一条 → 回滚 `git checkout HEAD -- <target_path>`，task 降回 `FAILED`。
