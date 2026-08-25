---
blueprint_id: MOD-FE-003
module_name: alert_center
domain: D_FRONTEND
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_FRONTEND
path: src/zephyr/frontend/dashboard/components/alert_center.py
granularity: file
---

# MOD-FE-003 alert_center 蓝图（D-FRONTEND-08 Alert Visualization 告警可视化）

> **module_id**: MOD-FE-003 | **域**: D_FRONTEND | **优先级**: P1
> **来源**: B14-04625（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-FE-002，A9运维架构 §8.3.2）
> 代码：`src/zephyr/frontend/dashboard/components/alert_center.py`

## 0. 定位

告警中心面板组件：AL-P1~P4 分级实时列表 + 6 维收敛视图（时间 / 空间 /
根因 / 抑制 / 升级 / 静默）+ MTTR 与日均告警统计 + 确认率 / 误报率追踪。
数据源**复用 alert_router 数据源**（运行时经 DI 注入记录序列，本组件不
import 告警后端）。

查重分工（W-P1-24 铁律③探查）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| shared/alerts/alert_manager | MOD-INF-016 | 告警 CRUD 后端（创建/确认/查询） | 本件=前端**可视化**，经 DI 消费其数据不重建后端 |
| feedback_loop/actors/alert_router | MOD-FEEDBACK_LOOP | 严重度→渠道路由决策 | 本件复用其产出数据形态做收敛视图，不重路由 |
| gov_drift/alert_router | D_GOV_DRIFT | 治理漂移告警路由 | 同为后端，数据源之一 |
| dashboard 既有 12 组件 | MOD-L08-001 族 | 任务/知识/门禁/Fitness/OLAP/回测/Tick/盘口/持仓/交易面板 | 均无告警中心面板；本件与 gate_statistics 同形态（dataclass+fetch+render dict payload，panel 可选） |
| dashboard_feeds | MOD-FE-002 | 前端结论级查询接口层（9 查询函数） | 本件=面板组件（数据→视图），不建查询接口层 |

TSV 裁定原文："告警后端齐备，前端告警中心面板缺；属核心监控告警面"——
施工形态=1 个新面板组件。

## 1. 规则（确定性，测试环境零 panel 依赖）

- **输入** AlertCenterRecord（告警记录，DI 注入）：alert_id/title/
  severity(AL-P1~P4)/source/status(active|acknowledged|resolved|silenced)/
  created_at/acknowledged_at/resolved_at/root_cause/suppressed/escalated/
  false_positive。
- **6 维收敛视图**：by_time（按小时桶计数）、by_space（按 source 计数）、
  by_root_cause（按根因计数 TopN）、suppressed（抑制清单）、escalated
  （升级清单）、silenced（静默清单）。
- **统计**：active_by_severity（P1~P4 在野计数）、mttr_seconds（resolved
  记录 resolved_at−created_at 均值，无 resolved → None）、daily_average
  （总记录/覆盖天数，<1 天按 1 天）、ack_rate（acknowledged+resolved /
  total）、false_positive_rate（false_positive / total）。
- **输出**：fetch_alert_center(records, now) → AlertCenterData；
  render_alert_center(data) → JSON 可序列化 dict payload（panel 可用时
  组 Panel 布局，测试环境仅 dict，与 gate_statistics 同模式）。
- Fail-Closed：severity/status 非法、时间戳倒挂（resolved<created）、
  records 非序列 → AlertCenterInputError。

## 2. 接口

```python
@dataclass(frozen=True) class AlertCenterRecord: 上列字段
@dataclass(frozen=True) class AlertCenterStats: total/active_by_severity/mttr_seconds/daily_average/ack_rate/false_positive_rate
@dataclass(frozen=True) class AlertCenterData: stats + views(by_time/by_space/by_root_cause/suppressed/escalated/silenced) + active_list

fetch_alert_center(records, now_utc=None, top_n_root_cause=10) -> AlertCenterData
render_alert_center(data) -> dict  # JSON 可序列化；panel 可用时附 layout
class AlertCenterInputError(Exception): 占位 ZA-FE-UNREGISTERED-ALERT-CENTER
```

## 3. 错误契约

- `AlertCenterInputError`（未登记错误码-申请中，占位
  ZA-FE-UNREGISTERED-ALERT-CENTER，建议顺延 ZA-FE-0006 见 W-P1-24 fragment）

## 4. 测试

- `tests/frontend/test_alert_center.py`
- 覆盖：分级在野计数、6 维视图计数、MTTR/日均/确认率/误报率已知答案、
  空记录、非法 severity/时间倒挂 Fail-Closed、render dict 可序列化

## 5. 依赖

- 标准库（statistics/datetime）；panel 可选（try/except，测试环境 None）
- 下游（运行时装配，不 import）：app_panel 挂「告警中心」Tab；
  alert_manager/alert_router 数据经 DI 适配注入
