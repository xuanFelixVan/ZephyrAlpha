---
ttl: task_bound
completes_when: Owner/Max 就保命旗标跨进程可达性与陈旧语义出裁，且 route_incident 唯一出手点有可施工口径
---

# 裁定申请书 req_rbsafe2_01 — 保命旗标跨进程可达性（P-1 案卷）

> 车道：`st-ff-rb-safe2-20260918`（接手已耗尽轮数的前手 `st-ff-rb-safe-20260918`）。
> **本件是案卷不是裁定**：本车道不取裁定号（宪法 §RULE-RULING / 协调账本 §4：裁定号总包统一分配）。
> 前手原文=`lanes/rbsafe_prescriptions.md` §P-1（本件复测并**部分推翻其归因**）。

## 0. 一句话

前手说"三套熔断旗标跨进程不可达"——**现象复测成立，但归因和处方要改**：
本仓**已经有**一个跨进程可达、带人工确认解除的持久化熔断载体（`zephyr.risk` 侧
`JsonStateStore(namespace="kill_switch")`，并有测试钉），真正缺的不是"发明落盘机制"，
而是 **`route_incident()` 的五个适配器里没有它**——保命轨把闸拉在了一具没人用的载体上。

## 1. 复测（R-019：全部本轮实跑，非引用前手快照）

| # | 载体 | 前手记载 | 本轮复测 | 判读 |
|---|---|---|---|---|
| 1 | `security/access_control/kill_switch.py` 系统级 | P1 True / P2 False | 同（`own.system_ks=True` → `reader.system_ks=False`） | **仍成立** |
| 2 | `trading/trading_contracts/risk/trading_kill_switch.py` 五级 | active 跨进程 False | 同（`reader.trading_daily_loss=False`） | **仍成立** |
| 3 | `governance/resilience_governance/last_resort_watchdog.py` | guardian 读腿 `(False,'')` | 同 | **仍成立** |
| 4 | `autonomy_core/kill_switch_orchestrator.py` | `route_incident` success=True 而 `is_tripped` False、`check_consistency()` consistent=True | 同（`reader.orch_trading=False`、`consistency.consistent=True`） | **仍成立** |
| 5 | 落盘真源 | `data/runtime/state*`、`data/runtime/**/kill*` 均不存在 | 实测仍 **0 件** | **仍成立** |
| 6 | reaper 周期 | "每 5 分钟" | 计划任务实注册 `PT10M`（`scripts/register_process_reaper_task.ps1:22,98`），`emergency_track_guardian.py:46` 注释亦写 10min | **前手数字错（不影响结论）** |
| 7 | 观测强度 | 前手=P1 拉闸后**退出**，P2 再读 | 本轮=`tests/security/test_kill_switch_cross_process_visibility.py`：**写腿存活时**起读腿 | **加强**：排除"进程退出才丢"这一弱化解释 |

复现：`python -m pytest tests/security/test_kill_switch_cross_process_visibility.py -q`
→ `2 passed, 2 xfailed`；仪器能红证据见 §5。

## 2. 严重面重划（本车道新增，比前手更窄也更硬）

**2.1 交易五级熔断在生产侧没有任何触发方，也没有任何解除方。**
- `trigger()`/`reset()`/`evaluate()`/`get_switch()` 的 src 侧消费者 = **只有编排器一处**
  （`grep -rn "get_switch(\|KILL_SWITCHES" src/` 命中仅 `kill_switch_orchestrator.py:189`）。
- `evaluate()`（唯一会读 `trigger_condition` 字符串的函数）**全仓零调用点**
  ⇒ `trading_kill_switch.py:72-111` 那五条 `trigger_condition`（"daily_pnl < -0.03*aum" 等）
  是**从未被机检的散文**。
- `cooldown_seconds` / `auto_reenable` 两字段**全仓零消费者**（`grep` 只命中同名异模块）
  ⇒ POSITION_LIMIT(300s/auto_reenable=True) 与 API_TIMEOUT(120s/auto_reenable=True)
  承诺的"自动到期恢复"**不存在**。
- ⇒ 攻面二"恢复路径"的机械答案：**不会自动解除**（符合 R-022 方向），
  但**也没有解除人**——`reset()` 零生产调用点，进程内一旦 active 就是单稳态直到重启。
  重启即归零（=静默解除，且无人签）。**两个方向同时坏**，这是比"永久卡死"更糟的组合。

**2.2 唯一真出手点接不到真载体。**
`emergency_track_guardian.py:562` 的 `route_incident()` 是保命轨唯一动作，宿主是 reaper 进程
（`src/zephyr/trading/process_reaper.py` `_run_safety_wires`，注释明写"不新建 cron/Timer"，合规）。
`kill_switch_orchestrator.register_default_switches()`（314-354 行）注册的五套 =
`security.kill_switch` / `skills` / `trading_kill_switch` / `infrastructure.rollback` /
`capacity_assurance` —— **不含 `zephyr.risk` 侧那套已持久化的 kill switch**。
⇒ reaper 拉闸对真实交易进程的有效动作数 = **0**。

**2.2bis 唯一留痕面在"记账成功"上，且无见证字段（假绿的可审计形态）。**
`route_incident` 唯一持久化产物 = `.runtime/audit/kill_switch_orchestrator.jsonl`
（`kill_switch_orchestrator.py:693-723 _trace`）。本轮两次实跑落的两行原文均为：
`"action":"trip", "level":"domain", "scope":"trading", "success":true,
"evidence":{"tripped":["trading"],"skipped":[],"errors":{}}`，
同时**同进程内** `check_consistency()` 报 `consistent:true`。
⇒ 事后审计者读这个 jsonl 会得到"资金事故已拉交易闸"的**确定结论**，
而记录里没有任何字段能否证它（无写入者 PID、无被保护进程见证、无 TTL）。
`session_id` 恒空 ⇒ **连"谁拉的"都查不到**。裁 J-1/J-3 时建议一并规定
留痕必带 `writer_pid` + `witnessed_by`（读腿进程回报），否则落盘只是把假绿搬到磁盘上。

**2.3 已存在的正确载体（处方应指向它，而不是新造）。**
- `src/zephyr/shared/state_store.py:117 JsonStateStore`：原子写（pid-tmp + `os.replace`）、
  读侧**三分语义**（`None`=从未发生 / `dict`=记录 / `StateCorruptError`=损坏必须 fail-closed），
  docstring 第 121 行原文即"**适用于 kill switch 熔断状态**"，示例落点 `data/runtime/state`。
- 已在产消费者：`risk/implementations/default_risk_validator.py:67 KILL_SWITCH_STATE_NAMESPACE="kill_switch"`
  （157-172 行三分 boot 语义，损坏→`_kill_switch_active=True`），`reset_kill_switch(confirmation)`
  须人工确认（`risk/stop_loss.py:153`）。
- 测试钉已在：`tests/risk/test_kill_switch_state_persistence.py`（"熔断后杀进程重启，熔断状态仍在"）。
- **但缺省不接线**：`ex_core/risk_layer_orchestrator.py:537 state_store=None`（注释 562 行自陈
  "None=仅内存态，既有行为"），而纸面会话生产入口 `scripts/start_paper_session.py:457` 构造
  `RiskLayerOrchestrator(...)` **未传 `state_store=`** ⇒ 连这条唯一可达终态的载体，
  在真实启动路径上也是内存态。
- `JsonStateStore` 无 CAS/expected-base、无 TTL/心跳/写入者 PID 字段 ⇒ 三要素里**只有"原子写"已有**，
  另两样要新建（这正是必须裁的部分，见 §3）。多写者并发下 `save` 是 last-writer-wins，
  落点选择必须先定单写者，否则新增的持久化面本身又是一个竞态源。

## 3. 请裁的四件事（本车道判为 Owner/Max 级，不自签）

**J-1 落点与写入者（谁有资格写这面旗）。**
候选：①`data/runtime/state/kill_switch.json`（与 `DefaultRiskValidator` 同 namespace，
把编排器五域 + `risk` 侧统一成**一条**记录）；②各域各自 namespace 一文件；③Redis 后端
（`state_store.py:337` 已有 `RedisStateStore` 工厂）。
代价：①最收敛但把"AI 行为风控闸"和"交易资金闸"并册，前手已注明二者职责不同
（`kill_switch.py:27-33` 自陈"禁作为任何交易资金安全场景的依赖"）⇒ 若走①须先承认口径合并。
**本车道建议**：②按域分文件 + 编排器 `is_tripped` 做"任一域外置记录即支配"的读侧收敛。缺=单写者不变量。

**J-2 陈旧旗标语义（★ 本车道明确不拍）。**
落盘引入的新危险：文件在、进程没了。前手已写"陈旧旗标既不得当作仍在熔断（会永久停手），
也不得当作已解除"——这是三态而非两态，**属 Owner 判据**。要裁的机械形式：
读侧遇到 `now - written_at > TTL` 时，返回第三态 `UNKNOWN_STALE`，并规定
（a）交易主链遇 UNKNOWN_STALE 是 fail-closed 停手还是（b）降级为人工确认（谁确认、确认落哪）。
`JsonStateStore.load` 的 `StateCorruptError→fail-closed` 已经把 (a) 的先例立好了，
但 TTL 越界≠损坏，是否并档须 Owner 点。**不点则任何落盘实现都会替 Owner 做这个决定。**

**J-3 复位面口径统一（实测两处不一致）。**
- `security/access_control/kill_switch.py:256 owner_release_global()` **零参数、零凭据**，
  任何 import 方调用即解除；`reset()`（300 行）同样零参数；
- 编排器 `reset()`（`kill_switch_orchestrator.py:393-406`）却要求 `approver` 非空。
⇒ 同一语义两个面，松的那个是有效的那个（谁都能绕过编排器直接解总闸）。
**建议裁**：`owner_release_global()/reset()` 加 approver+落审计（属**加严**，不触 #321 禁止）；
并裁 `owner_revoke_override()` 的"覆盖-撤销"半态是否允许跨进程存在（今天它也是内存态）。

**J-4 route_incident 是否必须包含 `risk` 侧持久化闸（=保命动作有效性的正门）。**
不裁则：reaper 每 10min 评估一次、三腿全 stale 才动作、动作了也没人受影响=**整条 BRK-078
是观测件而非保命件**。若裁"必经"，则施工面是"给编排器加第 6 个适配器（包 `DefaultRiskValidator`）"，
改动小、语义清楚，**但它是会主动动钱的闸**，按 R-022③ 先例（同域 `enabled:true` 已被上送 Owner）
仍须 Owner 点头，本车道不自动接。

## 4. 本车道实际做了什么（边界：不改行为，只加可观测）

做了：`tests/security/test_kill_switch_cross_process_visibility.py`——跨进程可达性**探测器 + 两条
strict-xfail 缺陷钉**。没做：不改 `kill_switch_orchestrator.py`（`[MODIFY-GUARD] Owner approval required`
`[AI_AUTONOMY] human_gated` `[SAFETY] H`）、不改三套旗标本体、不加 TTL 阈值（避免凭记忆造业务参数，
同前手 P-3 纪律）。
**为什么不在 `check_consistency()` 里加自检**：它是被审对象之一（§1 第 4 行的假绿面就出自它），
在 human_gated 件里由红队车道加判据=让被审者自己长眼睛，正是本件要防的"第二个自证清白的面"；
判据（"加完必须能红"）在测试侧已经满足（§5），故无需动生产件即可达到同等观测强度。

## 5. 能红证据（变异实跑）

工装=把读腿指向错误 namespace（模拟"落盘关了/读侧改瞎"）：
`_render(_READER).replace(_NAMESPACE, "BLINDED")` →
`1 failed, 1 passed, 2 xfailed`，失败即 `test_control_leg_externalized_flag_is_cross_process_visible`，
断言消息原文：`对照组失败：JsonStateStore 落盘旗标跨进程读不到 ⇒ 本探测器本身失效，另两条的判据不可信`。
⇒ 探测器**能红**；因此它报"三套旗标不可达"是检出而非恒真。
还原=按字节 `cp` 回滚（`restored byte-identical = True`）。
两条 strict xfail 的性质：治本落地当天 **XPASS→硬报错**，逼销案；不会悄悄变绿。

## 6. 需要 Max 的一条验真命令

```
python -m pytest tests/security/test_kill_switch_cross_process_visibility.py -q -rs
```
期望 `2 passed, 2 xfailed`；若哪天变成 `2 passed, 2 xpassed`（实为 FAILED）=P-1 治本已落地，
本申请书可关闭。
