---
module_id: KE-module_blu-3_8_______dogfooding_v0_6_0___-000
title: 3.8 引擎自保护与Dogfooding（v0.6.0 新增 — Wave 1 即落地自我扫描，Wave 2 落地Codegen防护）
category: module_blueprint
---

# 3.8 引擎自保护与Dogfooding（v0.6.0 新增 — Wave 1 即落地自我扫描，Wave 2 落地Codegen防护）

3.8 引擎自保护与Dogfooding（v0.6.0 新增 — Wave 1 即落地自我扫描，Wave 2 落地Codegen防护）

**核心问题**：引擎本身也是 Vibe Coding AI 生成的代码，可能包含重复函数。顶尖设计必须"吃自己的狗粮"。

**三层自保护机制**：

| 层级 | 触发 | 检查内容 | 失败策略 |
|:---:|------|------|------|
| **L1: 引擎自扫描** | 每次全量扫描后自动运行 | 对 `l01_infrastructure/code_dedup_engine/` 下所有 Python 文件运行去重检测（Stage 0.5+1） | 发现重复 → 标记 "SELF-DUP-*" + 报告 + 不自动修复（引擎自己修自己 = 递归噩梦） |
| **L2: Codegen 覆盖防护** | 每次全量扫描 + 每次 CI 运行 | 检查所有层 `__init__.py` 的 SHA256 哈希是否有已知修复（对比 `codegen_fix_manifest.json` 中的"已修复哈希白名单"）。检测到覆盖 → "CODEGEN-OVERWRITE-DETECTED" 信号 | ①告警不阻断 ②写入 Session Log ③生成修复diff——AI session 可一键重新应用修复 |
| **L3: 引擎依赖自检** | 每次加载时 | 检查 Tree-sitter/MinHash 库版本是否在锁定范围内 + 校验依赖 hash（poetry.lock 对比） | 版本漂移 → exit code 4（DEGRADED）+ 降级运行 |

**Codegen 覆盖防护清单**：

```yaml
