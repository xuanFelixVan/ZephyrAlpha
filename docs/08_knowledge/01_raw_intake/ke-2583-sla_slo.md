---
module_id: KE-2488
title: 8.4 SLA/SLO 度量指标
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 8.4 SLA/SLO 度量指标

8.4 SLA/SLO 度量指标

> 对标 ITIL 服务级别管理——量化脚本系统的服务水平目标，让"系统是否健康"有数字可查。

| 指标 | 目标值 | 测量方式 | 当前基线 |
|------|:---:|---------|:---:|
| **系统可用性** | ≥ 99% | `run_all.py` 全维度成功率 | 待测量 |
| **MTTR（平均修复时间）** | CRITICAL ≤ 24h / HIGH ≤ 72h | Finding 创建→关闭时间差 | 待测量 |
| **扫描覆盖率** | 100% 文件被至少一个维度覆盖 | 被扫描文件数 / 项目总文件数 | 待测量 |
| **假阳性率** | ≤ 5% | 人工确认后标记为 FALSE_POSITIVE 的 Finding 占比 | 待测量 |
| **门禁阻断率** | ≤ 2%（正常提交被误阻断） | pre-commit 被阻断后人工判定为误杀的占比 | 待测量 |
| **脚本健康度** | 100% 脚本可正常运行（exit ≤ 1） | `run_all.py` 全维度 warn-only 通过率 | 待测量 |

---
