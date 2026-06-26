---
module_id: KE-976
status: active
title: 6.1 HiL 触发点
category: governance
ttl: permanent
---

# 6.1 HiL 触发点

6.1 HiL 触发点

每个 stage 过渡**必须**有一次人工审核，无法跳过：

```
自动校验全绿 ─── 必须 ───▶  HiL 审核会议 ─── 批准 ───▶  启动下一个 stage
                              │
                              ▼
                       产出：stage-N-acceptance.md
                              │
                              ▼
                        包含：
                          - 退出门校验结果摘要
                          - 准入门校验结果摘要
                          - 用户签字（文本格式：已审核，批准进入 Stage N+1）
                          - 日期
                          - 已知风险清单
```
