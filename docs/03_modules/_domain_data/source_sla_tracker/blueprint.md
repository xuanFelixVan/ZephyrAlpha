---
blueprint_id: MOD-DATA-066
module_name: source_sla_tracker
domain: D_DATA
doc_type: blueprint
ttl: permanent
status: retired
superseded_by: MOD-L00-004
retired_date: 2026-10-04
retired_reason: >
  Owner 2026-10-04 裁定退役（图12挂图SOP升级 E-3 判定批，st-vm12e-20261004）。功能已被彻底
  代替：①源停供定性=supply_sentinel 表侧停更检测（业务日主腿/交易日折算/行数地板，MOD-L00-004-SS
  在岗在产）+error_classifier+源熔断三道防线实质覆盖；②本模块探测记录装配批自 2026-08-26
  登记起从未落地（全仓零外部调用方实测 2026-10-03），台账 data/sla/ 停更 38 天且无读者；
  ③融合判定否决：给它建输入管线=违 R-021 裁定精神（哨兵族不另开管线，全走 sentinel 托管），
  且未来若需源侧质量趋势，supply_sentinel 的 row_filter 按源切维能力可加配置行实现，
  不需要本模块代码。处置=纸面退役（文件在盘未摘，先例 storage_tiering.py 裁定#383）；
  data/sla/ 16 件停更残件随冷库例行归档，不挂任何图 casebooks（casebook_registry 已注记）。
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: human_gated
version: "0.2.0"
created: 2026-08-26
last_updated: 2026-10-04
owner: ZephyrAlpha-Owner
priority: P2
blueprint_level: module
domain_id: D_DATA
path: src/zephyr/data/source_sla_tracker.py
granularity: file
---

# MOD-DATA-066 source_sla_tracker 蓝图（数据源可用性SLA追踪器）【已退役 2026-10-04】

> ⚠️ **退役通告（Owner 2026-10-04 批，st-vm12e-20261004）**：本模块功能已被 MOD-L00-004
> supply_sentinel 族彻底代替（判定依据见 frontmatter retired_reason），纸面退役=文件在盘未摘、
> 测试已 skip、禁再新增调用；替代能力索引=supply_sentinel（表侧停更检测）+error_classifier+源熔断。
> 若未来需要"源侧 SLA 质量趋势"形态，走 supply_sentinel 配置加腿（row_filter 按源切维），
> 不复活本模块。

> **module_id**: MOD-DATA-066 | **域**: D_DATA | **优先级**: P2
> **来源**: B13-04332（AUD-DRAFT-001-DIGEST P2 波 P2-W02，CAND-DAT-020，A3数据架构）
> 代码：`src/zephyr/data/source_sla_tracker.py`

## 0. 定位

SLA追踪器：按源聚合可用率/延迟P50P99/失败原因分布（注入性能记录序列），日周报生成（周期报表字典）+SLA达标率判定（目标注入）+看板数据输出。Prometheus SLI/SLO思想。

## 1. 规则（确定性）

- 纯内存/DI 设计：外部副作用（OS 调用/网络/进程控制）全部经注入回调，默认空操作或内存记录。
- 非法输入 Fail-Closed 抛专用 Error（占位错误码，波末统一转正）。
- 同输入必同输出（确定性）；时钟/随机源全注入。

## 2. 接口

见代码 `__all__` 与 docstring。消费方=运行时装配批（统一注入点装配）。

## 3. 测试

`tests/data/test_source_sla_tracker.py` —— 内存替身全覆盖：正常路径 + 边界 + Fail-Closed 分支 + 确定性。
