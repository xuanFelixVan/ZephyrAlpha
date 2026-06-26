---
module_id: KE-643
status: active
title: Step 3：运行分析管线
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# Step 3：运行分析管线

Step 3：运行分析管线

1. 执行交易执行分析
2. 执行策略绩效分析
3. 执行风控合规分析
4. 每个步骤独立运行，互不依赖
5. **部分失败处理**：如个别步骤失败（如策略绩效分析报错），成功步骤的结果正常产出，失败步骤标记 `FAILED` 并在报告中注明"部分数据缺失"。所有步骤失败 → 整体标记失败，重新调度
