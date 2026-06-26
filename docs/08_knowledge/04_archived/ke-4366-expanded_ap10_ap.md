---
module_id: KE-4204-------------ap10-ap-000
title: 7-EXPANDED. 第十二轮新增反模式 (AP10-AP21)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 7-EXPANDED. 第十二轮新增反模式 (AP10-AP21)

7-EXPANDED. 第十二轮新增反模式 (AP10-AP21)

| ID | 反模式 | 描述 | 破解方法 |
|----|--------|------|----------|
| AP10 | Bootstrap-by-God | 假定CE天生完整,忽视CE-MVP->FullCE自举路径 | CE-MVP验收通过->扩建FullCE (DD75) |
| AP11 | Token-Pipe | 只算token消耗,不算token产出价值 | KE ROI归因 (DD76). 高cost低ROI KE淘汰或降Hot->Warm |
| AP12 | Forever-Phase-1 | CE永远在单Phase,规模问题堆积到崩溃才进化 | Auto Phase毕业标准 (DD77) + shadow canary flag |
| AP13 | A/B-Tax | 每次策略变更启动A/B并行,双倍推理/双倍Budget消耗 | Canary mode (DD78): 只生成不注入, far cheaper |
| AP14 | Blind-Inject | Owner不知道这次inject给了什么,信任坍缩为直觉误差 | context_playground (DD79): dry-run = 透明验证 |
| AP15 | Metric-Soup | 15个独立指标 -> Owner 认知过载,无法决策优先 | Unified Health Score (DD80): 单一0-100分 |
| AP16 | Stuff-n-Pray | 一次性全部KE注入 -> Agent盲目求相关 -> token浪费 | Progressive Disclosure (DD81): 摘要先注 |
| AP17 | Untested-Shield | 假定DD24/DD51/safe3测试通过;攻击向量zero retest | Adversarial Robustness (DD82): 持续Fuzz+PenTest |
| AP18 | Flat-Security | 没有KE-level sensitivity标记,依赖"一视同仁"的管道级通用防护 | Sensitivity 4-tier classify (DD83): KE标记敏感性 |
| AP19 | KE-Hoarder | KE堆积不求精简;多次同类KE保留,降低信息密度 | Knowledge Distillation (DD84): 聚类->代表KE |
| AP20 | Blind-Alignment | 默认"build的context一定对齐TaskCard意图",从不实测 | Alignment Scoring (DD85): post-inject cosine check |
| AP21 | Black-Box-Service | CE是基础设施但不被可观测性系统管理 | OTEL+SRE (DD86): standard production observability |

---
