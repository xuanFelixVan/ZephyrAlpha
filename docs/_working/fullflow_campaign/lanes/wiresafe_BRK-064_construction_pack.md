---
ttl: task_bound
completes_when: 生产链出现首个真实 respond() 调用点或 Owner 裁定保留 boot 注册态
---

# 施工包 · BRK-064 熔断族入口收敛（KS×5 / CB×9）

## 1. 实测结论：谁在决定用哪套开关（普查只给了"重复"，没给"入口"）

**三层结构在代码里早就存在**，缺的是"运行时是否真挂上"与"是否真被调用"：

| 层 | 件 | 实测状态 |
|---|---|---|
| 策略层（该停什么） | `src/zephyr/autonomy_core/killswitch_response_levels.py`（MOD-AU-004，`respond()`/`_SEVERITY_MAP` p1→level_1…global_critical→level_3，`:73-79`） | 本批前=零生产消费（仅 `autonomy_core/__init__.py:30` 的 `__all__` 与测试）；本批后=**boot 注册**（`src/zephyr/trading/boot_hooks.py:_init_kill_switch_orchestrator` 第二段，`_KILLSWITCH_DISPATCHER` 进程级持有）；`respond()` 生产调用点仍 **0** |
| 路由层（停哪里） | `src/zephyr/autonomy_core/kill_switch_orchestrator.py`（MOD-AU-002，`route_incident:429`、`register_default_switches:311`） | 2026-09-16 A3 已挂 boot（`49dde8fda5`），实测注册 system+skills/trading/rollback/capacity 四域；本批新增生产调用方=应急保命轨 |
| 执行机构（怎么停） | 5 套本体：`security/access_control/kill_switch.py`、`infrastructure/rollback/kill_switch.py`、`infrastructure/capacity_assurance/kill_switch.py`、`trading/trading_contracts/risk/trading_kill_switch.py`、`autonomy_core/skills/skill_kill_switch.py` | 全部经适配器包装，不被业务直接 import 拉闸 |

**入口唯一性的机械证据**（不是口头声明）：
`grep -rn "manual_trip_" --include=*.py src` 全仓命中文件 = {`security/access_control/kill_switch.py`（定义处）,
`autonomy_core/killswitch_response_levels.py`（策略层，唯一裁决者}，且该判据已固化成测试钉
`tests/governance/resilience/test_emergency_track_guardian.py::test_killswitch_trip_entry_is_unique`
→ 任何人新写一条绕过编排器的直接拉闸，测试即红。

## 2. 仍不唯一的部分（如实列，未自审为绿）

1. **`src/zephyr/infrastructure/kill_switch_sim.py`** —— 第 6 个 KillSwitch 语义件，GOMAP 的
   "KS×5" 口径未含它。**未删**（注册表/模块净删=Owner 门位，宪法 §5 + COORDINATION_LEDGER §7）。
   → 交总包作为 Owner 净删候选登记，判据：`grep -rn kill_switch_sim --include=*.py src scripts` 的
   消费面（本车道实测：src 内除自身外零 import）。
2. **`capacity_assurance/kill_switch` 域 vs `capacity` 熔断** 语义重叠（GOM-L3 note 已记载），
   收敛需 Owner 决定保留哪一侧的 fuse 口径。
3. **CB×9** 本车道**未动**（预算让位于保命链）：活链 4（`shared.resilience`、
   `governance/resilience_governance`、`gov_enforcement/rule_enforcement`、
   `security/adversarial_validation`）中，`adversarial_validation/circuit_breaker.py:117` 有
   `self.trip()` 自触发——属 CB 内部语义，非跨件旁路，但 CB 的"唯一 dispatcher"尚未指定
   （KS 有 MOD-AU-002/004，CB 没有对等路由层）→ **这是下一手：为 4 个活 CB 补一个路由层，
   或把 CB 并入编排器的第五域**。
4. **`escalation_engine` 的 L4 末端**目前只点亮 last_resort 旗标（`escalation_engine.py:383-401`，
   裁定#254 明令 `emergency_shutdown` 不得自动调用），**没有** 走 `respond()`。把升级协议终态映射到
   `ResponseIncident(severity="global_critical", ...)` 是天然的第一调用点，但那要改
   `escalation_engine`（human_gated 边界外）+ 需 Owner 确认"升级耗尽=系统级熔断"这一语义，
   故未做，登记为待裁。

## 3. 下一步改法（接手可直接开工）

- 件 1：Owner 批净删 → 走注册表净删正式通道；批前不动代码。
- 件 3：新建 `zephyr.shared.resilience.breaker_orchestrator`（**先 grep 预扫类名防撞**），
  把 4 个活 CB 包成与 `_XxxSwitchAdapter` 同形的适配器，公开 `trip_breaker(domain, target, reason)`；
  配 own-scope 测试钉（同 §1 的 grep 型反绕过测试）。
- 件 4：`escalation_engine` L4 末端补 `KillSwitchResponseLayer.respond(...)` 调用（须在
  `_KILLSWITCH_DISPATCHER` 已注册的前提下），并要求"旗标 + 拉闸"双写、失败出声。

## 4. 验收与回滚

- 验收：`git grep -n "manual_trip_\|\.trip(" src` 的文件集合 ⊆ {本体定义, 策略层, 路由层}；
  `python -m zephyr.trading` boot 日志出现"KillSwitch 响应策略层已注册"与
  "KillSwitchOrchestrator booted: system=True domains=[...]"（两行都在 boot_hooks 内）。
- 回滚=revert。boot 注册失败已被 try 隔离，不会拖死启动链（`_init_kill_switch_orchestrator` 首段
  失败即 `return`，第二段只在编排器注册成功时执行）。
