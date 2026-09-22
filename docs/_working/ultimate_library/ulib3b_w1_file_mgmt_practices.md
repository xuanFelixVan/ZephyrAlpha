---
asset_id: "DOC:docs/_working/ultimate_library/ulib3b_w1_file_mgmt_practices.md"
ttl: "task_bound"
---

# W+1 量化机构文件管理实践挖矿（任务 D·可选件，喂 regulations.md 素材）

- 班次：st-ulib3b-20260923（Owner 复职令"新需求不设限"）；两轮全网检索 2026-09-23
- 方法：EDMC/BCBS239/DORA/SRE 四系对标检索，摘要经本班核读；产出=可吸收进藏书规程的对照清单

## 一、四系核心实践

### BCBS 239（巴塞尔风险数据聚合 14 原则）

- 端到端数据血缘（source system → risk report 全链可追溯）+ 自动化数据质量闸
- 报告"消防演练"制：定期重演/对账测试（对应我馆 coverage 双向对账+restore_drill）
- 原则文：[BIS 官方](https://www.bis.org)（实施审查持续更新至 2026）

### SR 11-7（美联储模型风险管理）

- 模型清单制（model inventory）：版本化文档=假设/局限/验证结论/缓解控制
- 模型变更完整审计轨（对应我馆 MOD 蓝图+ALGO_FLOW 外锚+lib_events 事件流水）

### DORA（欧盟数字运营韧性法，Article 8 识别）

- **全量 ICT/信息资产登记**（含远程站点/网络资源/硬件），必须分类分级
- 资产登记册=文档化清单，**全部文档至少每年复审一次**（review-at-least-annually）
- 条文：[DORA Article 8](https://www.digital-operational-resilience-act.com)；[CloudQuery 年审义务解读](https://www.cloudquery.io)；[Legiscope 条款清单](https://www.legiscope.com)

### SRE runbook 纪律

- 单一目的/具体/可执行；统一模板+编号步骤+时间估计+链到仪表盘/脚本/日志
- 捕获时戳/版本/作者/最近复审日；先文档化手工 runbook 再自动化
- 参考：[FireHydrant](https://docs.firehydrant.com)、[Nobl9](https://www.nobl9.com)、[Rootly](https://rootly.com)

## 二、对照终极图书馆现状（已有✓/可吸收△）

| 实践 | 我馆现状 |
|---|---|
| 资产全量登记+分类 | ✓ lib_assets 9841+（kind 12 类/owner_domain/status 状态机） |
| 血缘（lineage） | ✓ ALGO_FLOW 外锚（source_of_truth+上下游边）+ TDM 传导链 |
| 事件审计轨 | ✓ lib_events（register/read/update/move/delete 全记 actor） |
| 死亡证明/注销授权 | ✓ 08 §3.1 authority 必填 |
| 恢复演练（fire drill） | ✓ restore_drill 月度 schtasks（T2） |
| 双向对账 | ✓ check_library_coverage blind/ghost |
| **年度复审制** | △ DORA 式"全部文档至少年审"——目前仅 TTL 元数据+task_bound 语义，无年审循环（HYGIENE 月批管日志/缓存，不管文档复审）→ 可呈 Owner 立项 |
| **模型清单版本化验证结论** | △ MOD 蓝图有版本无"验证结论"字段——与 potential_consumers 增枝同型（字段词典 §6 增枝制候选） |
| **runbook 统一模板** | △ SOP 馆有九族但无 runbook 专用模板（步骤/时估/回滚段） |

## 三、建议（呈 Owner 三条，不施工）

1. 年度复审循环：复用 TTL-METADATA 面，加"复审到期"扫描进 HYGIENE 月批（报告不处置，Owner 月批勾选）。
2. 模型资产验证结论字段：随 potential_consumers 增枝同窗评估（一次 DDL 两个候选字段一起裁）。
3. runbook 模板入 SOP 九族（doc_type: template）。
