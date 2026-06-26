---
module_id: KE-320
title: 4.10 门禁与校验条件禁止
category: documentation
ttl: permanent
---

# 4.10 门禁与校验条件禁止

4.10 门禁与校验条件禁止

| #       | 条件禁止行为                | 触发条件          | 替代方案                                                  | 来源               |
| ------- | --------------------- | ------------- | ----------------------------------------------------- | ---------------- |
| COND-33 | 门禁级别运行时动态升降级          | 运行时修改门禁级别时    | 级别调整仅能通过修改 YAML + 二次 review 完成                        | gate-strategy-standard.md |
| COND-34 | 门禁跳级（跳过 G1/G2 直接调 G3） | 调用门禁引擎时       | task 的 gate\_status 字段必须按顺序推进                         | gate-strategy-standard.md |
| COND-35 | 生产环境关闭门禁 disable 开关   | 生产环境启动时       | `TaskRepository(enable_gate=False)` 仅限单元测试/scaffold 补录 | gate-strategy-standard.md |
| COND-36 | AI 自行签发门禁豁免           | 自动化流程遇到需豁免场景时 | 必须 emit `manual_event(priority=HIGH)` 等待 Owner 批复     | gate-strategy-standard.md |
| COND-37 | Pydantic 校验失败静默吞掉     | AI 输出校验失败时    | 三级失败后禁止静默继续，必须由 Owner 或降级模型明确接管                       | adr-0040         |
