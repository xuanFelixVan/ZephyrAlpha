---
module_id: KE-950
status: active
title: 5.2 修改数据结构的流程
category: governance
---

# 5.2 修改数据结构的流程

5.2 修改数据结构的流程

1. 修改 SSoT YAML（`cross_layer_contracts.yaml`）
2. 运行生成脚本重新生成 Python 代码
3. 递增 `schema_version`
4. 审计所有下游模块的适配需求
5. Breaking change → 一篇 ADR

**禁止跳过第 1 步直接修改 Python 文件。**

---
