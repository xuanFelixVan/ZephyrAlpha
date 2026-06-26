---
module_id: KE-2307
status: active
title: 5.3 顺序依赖
category: module_blueprint
ttl: permanent
---

# 5.3 顺序依赖

5.3 顺序依赖

维度不是独立运行的——它们存在依赖链：

```
D1 STRUCT → D3 META → D5 ARCH → D8 SYNC
D2 LINK   → D4 PATH → D11 COMPL → D9 KNOW → D12 HALLU
D6 SEC    → D7 CODE → D10 PERF
```

**调度规则**：
- 同一依赖链上的维度必须**串行执行**（前一个维度修复完成，后一个维度才能正确解析）
- 不同依赖链之间可以**并行执行**
- D1 是最前置依赖——文件结构损坏会导致所有下游维度误报
