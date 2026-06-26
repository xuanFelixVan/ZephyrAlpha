---
module_id: KE-889
title: 4.1 调度表
category: governance
ttl: permanent
---

# 4.1 调度表

4.1 调度表

| 频率 | 审计类型 | 覆盖维度 | 等级 | 执行者 |
|------|---------|---------|------|--------|
| **每次 commit** | QUICK（自动） | pre-commit 25 hooks + GATE-01~18+SQ+ADM+IDX+COMMIT | L1 | 自动 |
| **每日** | QUICK | D3 + D5 + D6 + D7 | L1 | AI |
| **每周** | TARGETED | 上周变更涉及的维度 + script_manifest 新增脚本验证 | L1 | AI |
| **每两周** | FULL（轻量） | D1-D12（仅 P0 脚本 ~29个）| L1 | AI |
| **每月** | FULL | D1-D12（P0+P1 脚本 ~67个）| L2 | Owner + AI |
| **每季度** | FULL + 评分 | D1-D12 全量 177 脚本 + score_architecture.py | L2-L3 | Owner |
| **Phase 过渡时** | FULL + 评分 | D1-D12 全量 + Phase 退出门检查 | L2+ | Owner |
