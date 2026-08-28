---
blueprint_id: MOD-SEC-EVENTBUS
module_name: security_event_bus
domain: D_SECURITY
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-SEC-EVENTBUS security_event_bus 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：16号文 §4.2 P0-1（统一事件 schema）/ P0-3（高危告警通道）+ §3.19（Event Schema Versioning 治理）+ 18号清单 §4.3 + #ARCH-161。
> 代码：`src/zephyr/security/security_event_bus.py`

## 0. 定位

统一安全事件总线：四域安全检测（LSG 安全栈 / 自治边界 gate / 治理门禁 / 运行时检测器与 ai_agent_monitor）各自产出格式各异的安全事件，无统一出口 = 无可观测性。本模块提供统一 schema + JSONL 落盘 + 四域 adapter + 高危飞书告警通道。只收口事件，不改动 LSG / access_control / FBL 检测器 / auto_fix_engine 任何本体逻辑（16号文 §5 第 6 条）。

## 1. 接口

```python
class SecurityEvent(BaseModel)   # pydantic 严格校验；from_raw(dict) / to_jsonl() / severity_at_least()
class SecurityEventBus(event_dir=None, alert_threshold=Severity.HIGH,
                       dry_run_alert=False, alerter=None)
    .register_adapter(adapter) / .register_default_adapters()
    .emit(event) -> SecurityEvent
    .emit_via_adapter(adapter_name, raw) -> SecurityEvent | None   # adapter 异常独立降级
    .iter_events() / .count_events() / .degraded
class FeishuAlertChannel(pending_path=..., dry_run=False, timeout_sec=5.0, webhook_url=None)
    .send(event) -> bool / .retry_pending() -> dict / .pending_count()
```

四域 adapter（DomainEventAdapter 子类，只实现 raw_mapping）：LsgSecurityStackAdapter（block/deny→high）/ AutonomyGateAdapter（拦截→high）/ GovernanceGateAdapter（verdict RED→high/YELLOW→medium/PASS→low）/ RuntimeDetectorAdapter（state=CRITICAL→critical；is_breached 或 risk_score≥0.6→high，MOD-RK-14 阈值口径）；显式 severity 优先。

## 2. 输出契约

- `SecurityEvent` 字段：event_id/ts（ISO8601）/source_domain（四域枚举）/threat_category（九类枚举）/severity（info~critical 五档）/evidence_ref（非空）/session_ref/schema_version（=1.0 拒收异版）/detail；extra="forbid" 未知字段拒收。
- 落盘：`.runtime/security_events/security_events.jsonl`（JSONL 追加，gitignored 运行时区）；`iter_events()` 机器遍历，坏行跳过不阻断。
- 告警：severity ≥ high 推飞书 webhook（secret 机制读 `ZEPHYR_FEISHU_WEBHOOK`，服务未登记降级环境变量）；未配置/不可达/非 200 → 写本地持久化队列 `alerts_pending.jsonl` 不丢；`retry_pending()` 成功出队、失败累计 retry_count、超 MAX_ALERT_RETRY=5 转死信保留；`dry_run=True` 只留痕 `alerts_dryrun.jsonl` 不真发（周六演练口径）。

## 3. 不变量

- schema 校验失败 MUST 拒收（SecurityEventValidationError，ValueError 子类），不落盘不告警
- 单 adapter 异常 MUST 独立降级（`degraded` 留痕），绝不阻塞总线与其他 adapter
- 高危告警 MUST 本地持久化不丢；告警通道异常绝不阻塞事件落盘主流程

## 4. 降级行为

- webhook 不可达属预期降级路径 → 本地队列；secret 机制不可用 → 降级环境变量读取，绝不阻断告警通道
- emit_via_adapter 未注册/转换异常 → 记 degraded 返回 None

## 5. 边界（不做）

- 不改动四域检测器本体；不做事件消费侧分析（落盘即出口）
- MODIFY-GUARD：16号文 §4.2

## 6. 测试

tests/security/test_security_event_bus.py（21 用例）；配套演练报告 docs/_working/reports/2026-08-22-tnr-drill.md（TNR 双达标，报告已随 2026-08-28 _working 大清理退役）+ docs/01_policies_and_standards/sop/2026-08-22-emergency-runbook.md（D-L1~D-L3 保命轨）。
