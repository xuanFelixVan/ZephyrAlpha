---

## 7. 指标参数配置

```yaml
breadth_indicators:
  adr:
    window: 10
    overbought_threshold: 1.5   # ADR > 1.5 谨慎
    oversold_threshold: 0.67     # ADR < 0.67 关注

  mcl:
    short_period: 19
    long_period: 39
    bullish_threshold: 50        # MCL > 50 看涨
    bearish_threshold: -50      # MCL < -50 看跌

  adl:
    bullish_confirmation: "ADL创新?
    bearish_confirmation: "ADL创新?

  alerts:
    - condition: "ADR连续3?> 1.5"
      message: "市场可能过热"
    - condition: "ADR连续3?< 0.67"
      message: "市场可能见底"
    - condition: "MCL从负转正"
      message: "广度动量转多"
```

---

**版本**: 1.0 | **更新**: 2026-03-28

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
