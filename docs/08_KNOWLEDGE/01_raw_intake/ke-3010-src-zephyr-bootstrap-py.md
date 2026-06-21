---
module_id: KE-2910
status: active
title: src/zephyr/bootstrap.py
category: module_blueprint
---

# src/zephyr/bootstrap.py

src/zephyr/bootstrap.py

async def build_services():
    vm = get_vm()
    ce = InProcessContextEngine(config=..., vm=vm, entity_graph_path=...)
    orc = InProcessOrchestrator(config=...)
    lsg = InProcessLLMSecurityGateway(config=...)

    # FLE 注入下游 Protocol 适配器
    fle = InProcessFeedbackLoop(
        config=...,
        context_action=CEAdjustAdapter(ce),      # 适配器：把 FLE FeedbackSignal 转 CE FeedbackSignal
        orchestrator_action=OrcControlAdapter(orc),
        vms_action=VMSControlAdapter(vm),
        lsg_action=LSGControlAdapter(lsg),
    )

    # Orchestrator 反向注入 FLE 作为 FeedbackSinkProtocol
    orc.set_feedback_sink(FLEMetricSinkAdapter(fle))
    # CE 反向注入同理
    ce.set_feedback_sink(FLEMetricSinkAdapter(fle))

    return vm, ce, orc, lsg, fle
```
