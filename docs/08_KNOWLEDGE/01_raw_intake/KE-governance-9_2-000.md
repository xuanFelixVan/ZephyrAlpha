---
module_id: KE-governance-9_2-000
title: 9.2 豁免签发格式
category: governance
---

# 9.2 豁免签发格式

9.2 豁免签发格式

commit message 必须使用 trailer 格式：

```
gate-exempt: G4-C01 | reason: 跨 Phase 依赖暂缺 | valid_until: 2026-05-01
```

| 字段 | 格式 | 说明 |
|------|------|------|
| `gate-exempt` | `G{N}-C{NN}` 或 `G{N}` | 被豁免的检查 ID |
| `reason` | 自由文本 ≥ 10 字 | 必须说明业务原因 |
| `valid_until` | ISO 日期 `YYYY-MM-DD` | 最多 30 天 |
