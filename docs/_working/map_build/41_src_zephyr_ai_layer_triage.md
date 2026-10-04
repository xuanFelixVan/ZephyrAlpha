---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.ai_layer（22 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.ai_layer（22 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=1，wired=18，wired_by_header=3；初判汇总：dispute=1，mount=21

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/ai_layer/__init__.py` | ai_layer — AI 层（自我进化引擎）顶层包：七段一常数（L1-L7 + OBJ_M/R/S/T）工程落点。 | 2026-09-19（15天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 15 天内有 commit（活着但零线零引）；①mount→GOMAP（治理/安全域） ②retire→Owner 门位） |
| `src/zephyr/ai_layer/cleaning/auditor.py` | auditor — L3 清洗质量抽验审计器：采样 → 机检前置 → 裁判 → rubric 判分 → 退回流转。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/cleaning/local_prefill.py` | local_prefill — L3 工序①本地预洗器：解析/元数据/查重预检/分块计量/骨架预填。 | 2026-09-26（8天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/cleaning/policy.py` | policy — L3 清洗考尺装载器：config/cleaning_policy.yaml → 冻结策略对象。 | 2026-09-26（8天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/comparator/policy.py` | policy — L4 判据常量层加载器：config/comparison_policy.yaml 的唯一读取入口。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/comparator/too_good.py` | too_good — "好得不像真"三查执行器：触发线检测 + 三查 checklist + 三出口流转建议。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/heritage/closure_check.py` | closure_check — 关单强制传承登记机检（对接主文档 §三 关单四闸）。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/heritage/policy.py` | policy — config/heritage_policy.yaml 装载器（L7 规则参数唯一读取口）。 | 2026-09-26（8天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/intake/__init__.py` | intake — AI 层 L2 收集段（原材料库）工程包：入库闸 / 卡库 / 查重 / 事件 / KPI 五件。 | 2026-09-19（15天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/perceive/__init__.py` | perceive — AI 层 L1 感知段（外扫+内监）工程包：源注册表 / 搜索任务单 / 内监翻译器 三件。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/perceive/search_orders.py` | search_orders — L1 搜索任务单登记件：schema v1 + journal + 状态机 + TTL 过期（施工项 5）。 | 2026-09-26（8天） | in=4/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/perceive/source_registry.py` | source_registry — L1 外部源注册表加载与结构校验器（施工项 1 的机检面）。 | 2026-09-26（8天） | in=3/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/perceive/translator.py` | translator — L1 内监接线件：探测器信号 → 定向搜索任务单（施工项 6）。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/redline/annual_review.py` | annual_review — 负面清单年审流水线挂接（OBJ_S 施工项 S8，DESIGN §6）。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/redline/dashboard_pipeline.py` | dashboard_pipeline — "不亏钱"双指标看板数据链（OBJ_S 施工项 S5）。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/redline/freedom_weekly_report.py` | freedom_weekly_report — 自由域透明度周报生成器（OBJ_S 施工项 S7，DESIGN §5）。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/redline/no_delete_manifest.py` | no_delete_manifest — 禁删清单生成器×2（OBJ_S 施工项 S4，DESIGN §2 档 A）。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/redline/sev_router.py` | sev_router — SEV 探针聚合分级路由（OBJ_S 施工项 S6，DESIGN §3）。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/scheduling/maturity.py` | maturity — L5 区域成熟度门闸（D-L5-03，T0 门闸）：M1-M4 可配置判定 + 区域聚合 + 挂起转正。 | 2026-09-26（8天） | in=2/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/scheduling/router.py` | router — L5 骨架级分流器（D-L5-05）：三证据机检 + Owner 门位路由。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/switch_engine/approval_router.py` | approval_router — 切换审批分流器（S6 施工件）：债类 × risk_tier 九域映射三道分流。 | 2026-09-28（6天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
| `src/zephyr/ai_layer/switch_engine/rollout_tiers.py` | rollout_tiers — 灰度三档执行件（S8 施工件）：升降档机检+渐进收敛校验+裁定登记载荷。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→GOMAP（治理/安全域）（活线在身未挂线） |
