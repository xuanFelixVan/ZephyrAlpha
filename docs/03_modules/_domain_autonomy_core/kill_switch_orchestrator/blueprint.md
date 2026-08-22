---
blueprint_id: MOD-AU-002
module_name: kill_switch_orchestrator
domain: D_AUTONOMY_CORE
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-AU-002 kill_switch_orchestrator 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：15号文 §3.4（收敛规则）/ §4.1-S0.3 + 16号文 §4.2 P0-1（统一事件 schema）+ 18号清单 §4.2 + #ARCH-160。
> 代码：`src/zephyr/autonomy_core/kill_switch_orchestrator.py`

## 0. 定位

Kill Switch 两级编排器：系统级总开关（security/access_control/kill_switch.py，MOD-INF-018）+ 域级分开关（skills 熔断 / trading 五级 / rollback 三级 / capacity 保障）的统一路由与收敛。治理"五套 Kill Switch 各自独立无编排"缺口。编排器只做适配器包装（lazy import），不改写既有 5 套实现。

## 1. 接口

```python
class KillSwitchOrchestrator(runtime_dir=None, repo_root=None, *,
                             register_defaults=True, system_switch=None, project_root=None)
    .trip(level, scope, reason="") -> OrchestrationResult        # 拉闸
    .reset(level, scope, approver="") -> OrchestrationResult     # 复位（approver 非空=Owner 批准）
    .route_incident(incident_kind, reason="", target="") -> OrchestrationResult
    .is_tripped(level, scope="") -> bool                         # 有效状态查询（支配语义）
    .check_consistency() -> dict                                 # 两级一致性检查
class SwitchAdapter(Protocol)   # name/supports_global_trip + trip/reset/is_tripped
```

scope 语法：level="system" 时 scope 为自由标签（默认 "global"）；level="domain" 时为 `<域名>` 或 `<域名>:<目标>`——skills→skill_id；trading→KillSwitchLevel 值（空=全部五级）；rollback→`L1_SESSION:<id>`/`L2_SKILL:<id>`/`L3_GLOBAL:<target>`（L3 需 BREAK_GLASS token）；capacity→忽略目标（单实例 fuse）。

## 2. 输出契约

- `OrchestrationResult`（frozen）：event_id/action（trip|reset）/level/scope/success/reason/approver/tripped/skipped/errors/timestamp。单开关失败不阻断其余传播，失败收入 errors。
- 留痕：`.runtime/audit/kill_switch_orchestrator.jsonl`（16号文统一事件 schema，source_domain=access_control；系统级 trip severity=critical，域级 elevated，reset info）。
- `check_consistency()` 报告：system_tripped/domains{own_tripped,supports_global_trip}/errors/consistent。

## 3. 不变量

- 编排器不持有开关状态：状态分散在各开关本体，is_tripped/check_consistency 每次实时查询；编排器故障/销毁则各开关独立可用（fail-open 分散态）
- 系统级 TRIPPED ⇒ 域级一致生效：对支持全域拉闸的域级开关传播 trip（不支持者记 skipped）；查询面走支配语义（系统级 TRIPPED 时域级查询一致 True）；系统级 TRIPPED 时域级禁止单独复位（先复位系统级）
- 复位须 approver 非空（Owner 批准语义），空 approver 直接失败留痕
- 收敛规则（§3.4）：①影响资金 → 交易级先行、失败系统级兜底；②影响代码库/会话 → 系统级；③域内故障 → 域级先行；④全局事故 → 只拉系统级总开关（域级一致由传播保障）

## 4. 降级行为

- ERROR_CONTRACT：trip/reset/route_incident/is_tripped/check_consistency 永不抛异常；失败收入 OrchestrationResult.errors
- 默认开关注册单套导入失败不阻断其余（返回失败表 WARNING）
- 查询面 fail-open：开关本体异常返回 False 并告警（拉闸/复位权威判定走 errors 通道）；审计写失败不阻断动作

## 5. 边界（不做）

- 不改写既有 5 套开关本体（只适配器包装）；不引入新开关状态存储
- MODIFY-GUARD：Owner approval required；变更须同步 15号文 §3.4 收敛规则

## 6. 测试

tests/autonomy/test_kill_switch_orchestrator.py（#ARCH-160：2 文件 34 用例之一；KS 内联查询 P95≤0.8µs 实测达标；三类事故仿真全过）。
