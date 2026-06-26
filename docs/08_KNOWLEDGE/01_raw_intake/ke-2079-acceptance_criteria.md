---
module_id: KE-1988
status: active
title: 3. Acceptance Criteria
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3. Acceptance Criteria

3. Acceptance Criteria

- AP1: 注释 inject() 中的 lsg_passed 断言 → 测试失败
- AP2: CompressedContext 无 raw_text → 类型检查失败
- AP3: format_context() 输出含 "Layer1:", "Layer2:", ... 标记
- AP4: 同一 query 两次 build() → 第二次命中缓存
- AP5: 注入不存在的路径 → 触发 auto_fix (移除 source)
- AP6: 2 天前的 KE 权重 < 1 天前的 KE 权重
- AP7: 预算 7601 tokens → 不再追加 context
