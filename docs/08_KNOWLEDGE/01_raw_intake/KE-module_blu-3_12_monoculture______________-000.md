---
module_id: KE-module_blu-3_12_monoculture______________-000
title: 3.12 Monoculture 免疫——去重成功的根本性悖论（v0.7.0 终极审视——外部取证审计师发现 #1）
category: module_blueprint
---

# 3.12 Monoculture 免疫——去重成功的根本性悖论（v0.7.0 终极审视——外部取证审计师发现 #1）

3.12 Monoculture 免疫——去重成功的根本性悖论（v0.7.0 终极审视——外部取证审计师发现 #1）

**发现**：前三次审计围绕"如何更好地检测/安全地修复重复"。但从未有人问一个根本问题：
**如果去重引擎 100% 成功了，代码库是更安全了还是更脆弱了？**

**悖论**：去重消除重复 → 所有 caller 共享同一个 shared 函数实现 → 这个 shared 函数中的任何一个 bug 现在影响 N 个 caller 而非 1 个。
去重前：N 个 caller 各自有各自的实现 → bug 被隔离在单个 caller。去重后 → **Monoculture**——单一实现成为全系统单点故障。

**Blast Radius Score（BRS）——爆炸半径评分 0-100**：

```
BRS = min(
  100,
  (caller_count / max_caller_threshold) * 40 +                    // 调用方越多，爆炸越大
  (cross_layer_ratio / max_cross_layer) * 30 +                    // 跨层调用越多，破坏越深
  (is_critical_path ? 20 : 0) +                                   // 关键路径=炸弹
  (has_no_independent_test ? 10 : 0)                              // 无独立测试=安全性更低
)

max_caller_threshold: 当前=10, max_cross_layer: 当前=0.5
```

| BRS | 等级 | 含义 | 引擎行为 |
|:---:|:---:|------|------|
| 0-25 | **SAFE** | 爆炸半径低 | 正常去重 |
| 26-50 | **CAUTION** | 开始形成单点依赖 | 去重但标记 `blast_radius: CAUTION`——强烈建议为该 shared 函数增加独立单元测试 |
| 51-75 | **RISKY** | 单点故障可能引发级联故障 | ①去重后必须在 Session Log 中高亮 ②Health Score 中 BRS 权重=15% ③自动生成 TaskCard BRS-AUDIT-{N}——"N 模块依赖同一实现——建议故障注入测试" |
| 76-100 | **DANGEROUS** | 该提取创造了比重复更高的风险 | ①**停止去重**——引擎建议"该重复应保持原状——风险优先于简洁" ②生成"为什么不修复"的报告 ③只有 Owner 手动 `--force-monoculture` 可覆盖 |

```yaml
