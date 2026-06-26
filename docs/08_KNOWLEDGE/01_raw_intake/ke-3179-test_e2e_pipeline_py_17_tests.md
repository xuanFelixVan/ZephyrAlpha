---
module_id: KE-3073
title: test_e2e_pipeline.py（17 tests）
category: session_log
ttl: permanent
---

# test_e2e_pipeline.py（17 tests）

test_e2e_pipeline.py（17 tests）
| 测试类 | 测试数 | 覆盖场景 |
|--------|--------|---------|
| TestE2EFullPipeline | 14 | L06 券商下单 / L05+L06 集成 / L04 风控 pre-trade+portfolio / L07 TCA / L04 止损 / L09 回测 / L10 安全网关 block+allow / L11 推理未加载模型 / L13 实验管线 |
| TestCrossLayerContractAlignment | 3 | CTR-003 / CTR-P1-003 / CTR-ERR-001 类型验证 |
| TestOrderManagerLifecycle | 2 | PENDING→FILLED 全生命周期 / TWAP 执行 |
