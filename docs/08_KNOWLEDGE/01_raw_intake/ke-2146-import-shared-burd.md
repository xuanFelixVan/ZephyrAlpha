---
module_id: KE-2054--------shared-burd-000
status: active
title: 3.11 Import表面积负债追踪（Shared Burden Score — v0.6.0 新增 — Wave 2 落地）
category: module_blueprint
---

# 3.11 Import表面积负债追踪（Shared Burden Score — v0.6.0 新增 — Wave 2 落地）

3.11 Import表面积负债追踪（Shared Burden Score — v0.6.0 新增 — Wave 2 落地）

**核心问题**：每一次去重提取到 shared，都创造了一个新的耦合点。项目从 A→B、A→C 的简单依赖变成 A→shared、B→shared、C→shared——代码行数减少了，但**导入边数**增加了。
当有 30+ 模块 import 同一个 shared 函数时，修改这个函数的影响面比原来分散在各处的重复函数更严重。

**Shared Burden Score（SBS）——0-100**：

```
SBS = min(
  100,
  (shared_import_total / max_safe_shared_imports) * 50 +
  (max_dependents_per_func / max_safe_per_func) * 30 +
  (cross_layer_dependency_pct / max_safe_cross_layer) * 20
)

其中：
- shared_import_total: 项目中所有 "from zephyr.shared" 的 import 次数
- max_safe_shared_imports: 项目安全上限（当前=80）
- max_dependents_per_func: 单个 shared 函数被最多模块依赖的数量
- max_safe_per_func: 单个函数安全上限（当前=15）
- cross_layer_dependency_pct: 跨层 shared 引用占所有 shared 引用的比例
- max_safe_cross_layer: 跨层引用安全上限（当前=40%）
```

| SBS | 等级 | 引擎行为 |
|:---:|:---:|------|
| 0-30 | **LIGHT** | 正常去重→提取——shared 负担轻 |
| 31-55 | **MODERATE** | 去重正常但新提取需 Suitability Score ≥ 70（而非默认 60）——提高提取门槛 |
| 56-75 | **HEAVY** | 仅提取 similarity ≥ 0.98 的重复 + partial-extract 优先（而非全量提取）+ Health Score 中 SBS 权重提升至 20% |
| 76-100 | **CRITICAL** | ①停止自动提取——引擎建议"shared 债务清算优先级 > 去重" ②生成 TaskCard SHARED-REFACTOR——建议分拆 shared 为 shared-core / shared-utils / shared-contracts ③Owner 需手动解冻 shared 提取 |

```yaml
