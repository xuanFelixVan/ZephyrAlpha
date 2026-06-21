---
module_id: KE-323
title: 4.12 AI 工程条件禁止
category: documentation
---

# 4.12 AI 工程条件禁止

4.12 AI 工程条件禁止

| #       | 条件禁止行为                               | 触发条件             | 替代方案                                                                      | 来源                                                              |
| ------- | ------------------------------------ | ---------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------- |
| COND-42 | CoVe Step 2 使用与 Step 1 相同的模型         | 执行 CoVe Step 2 时 | 必须异构 cross-check（Sonnet → GLM，反之亦然）                                       | adr-0039                                                        |
| COND-43 | FLE 直接 import 实现类                    | FLE 模块引用外部服务时    | 必须定义本地 Protocol，调用方在 wiring 层注入                                           | feedback-loop-engine-interface.md                               |
| COND-44 | FLE Action 不记录 effective\_from + ttl | FLE 产出 Action 时  | 每个 Action 必须记录生效时间和 TTL，超 TTL 自动回滚                                        | feedback-loop-engine-interface.md                               |
| COND-45 | 服务降级不写入日志                            | 服务降级时            | 必须写入结构化 JSON（触发原因/时间戳/task\_id/降级码）                                       | context-engine-interface.md, vector-memory-service-interface.md |
| COND-46 | 知识库写入不传 provenance                   | 向知识库写入条目时        | `kb.write(topic, content, provenance)` — provenance 缺失抛 WriteTraceMissing | unified\_memory\_api.py                                         |
