---

## 5. 告警规则

```yaml
factor_alerts:
  icir_threshold:
    warning: 0.5
    critical: 0.3

  decay_rate_threshold:
    warning: 0.3  # 5日衰减超?0%
    critical: 0.5  # 5日衰减超?0%

  turnover_threshold:
    warning: 0.5  # 日换手率超过50%
    critical: 0.8
```

---

**版本**: 1.0 | **更新**: 2026-03-28

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
