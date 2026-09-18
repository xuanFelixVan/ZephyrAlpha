---
ttl: task_bound
completes_when: 应急保命轨完整决策图落地并接入 TDM 四轨仲裁
---

# 施工包 · BRK-078 应急保命轨（CC_07）完整决策图落地

> 车道 `st-ff-wiresafe-20260918` 交付边界：**最小可运行实体已落地**（判据+动作+留痕+窗口闸），
> 本包给的是"从最小实体到完整 CC_07 决策图"的余量，接手者**不需重新勘察即可开工**。

## 1. 已落地（勿重做，先读这些 file:line）

| 件 | 路径:行 | 作用 |
|---|---|---|
| 判据+动作 | `src/zephyr/governance/resilience_governance/emergency_track_guardian.py`（`EmergencyTrackGuardian.evaluate` / `read_legs` / `_in_active_window` / `_execute_trip`） | 三腿心跳判失效 → `route_incident` 拉系统级 |
| 判据真源 | `config/emergency_track.yaml`（legs/evidence_horizon_seconds/active_window/action/crisis_snapshot） | 阈值与窗口，未知键=硬错 |
| 自动触发宿主 | `src/zephyr/trading/process_reaper.py`（`_run_safety_wires`，`reap()` 第 4 步） | 复用 OS 计划任务 10min 心跳（`schtasks` 实测 `PT10M`） |
| 动作下游 | `src/zephyr/autonomy_core/kill_switch_orchestrator.py:429`（`route_incident`）→ `:541`（`_trip_system` 向域级传播） | 唯一保命入口 |
| 旗标消费端 | `src/zephyr/governance/resilience_governance/last_resort_watchdog.py`（`active`）；写方 `src/zephyr/governance/escalation/escalation_engine.py:383-401` | BRK-005 |
| 测试钉 | `tests/governance/resilience/test_emergency_track_guardian.py`（13 测，含"盘外不动作/隔夜旧心跳不算失效/旗标计一票/拉闸失败必须出声"） | 变异证据见战役台账 |

## 2. 缺哪几件（CC_07 蓝图 vs 实码 的差）

蓝图真源：`docs/02_enterprise_architecture/07_trading_decision_architecture/battle_map/battle_map_12_cross_cutting.md`
§应急保命降级路径（CC_07），现仍 `class CC_07 design`。蓝图要求"**逐级**降级、每层失效都有硬编码兜底"，
本车道只落了"全失效 → 拉闸"这一末级。缺四件：

1. **分级降级阶梯**（蓝图 §CC_07 逐级）：L1 只停新增开仓（trading 域五级）→ L2 平掉日内高频回路
   （skills 域熔断）→ L3 回滚到最近安全态（rollback 域 L2_SKILL）→ L4 系统级总闸。
   改法：`emergency_track_guardian` 增 `ladder` 配置块（每级 = 一组 `route_incident` 参数 + 该级
   判据子集），`evaluate()` 按"确认等级"逐级下闸并记录当前级；**复位仍须 Owner approver**
   （`kill_switch_orchestrator.reset(..., approver=)`，15号文 §4.1 S0.3 不变量，禁自动降级复位）。
2. **决策图节点落地**（depgraph）：现在只有 `decision_tracks` 一行 `emergency`（priority=4），
   `decision_nodes` 213 行全 `planned`（BRK-023）。改法：`scripts/governance/apply_depgraph.py`
   的 decision_node 登记面补 4 个节点（L1..L4），`build_status` 从 `planned` → `production`
   仅当对应代码路径有测试钉；`activation_condition` 文本须与本册判据口径一致（否则蓝图↔代码再漂移）。
3. **仲裁接线**：`module_translation_registry` 已记载四轨优先级"应急保命轨一旦触发即压制全部其他轨"
   （条目 `name_zh: 应急保命轨` / BM-BUY-02 子环节）。落地=在四轨融合层读
   `get_emergency_track_guardian().last_verdict()`，非 normal 时压制其余三轨输出。
   融合层入口见 `docs/03_modules` 内 BM-BUY-02 锚定模块（本车道禁写 docs/03_modules，未取 file:line）。
4. **自动维护/自动关闭的证据面**：现在每次评估落 JSONL，但无"多久没评估=保命轨失能"的反看。
   改法：把 `.runtime/audit/emergency_track.jsonl` 末行时间纳入 reaper 自检（>30min 未更新即
   `report.errors` 记 `emergency_track_stalled`）——**这条不做就是 #ARCH-327 的复现形态**
   （加固代码在 except 里空转而无人知晓）。

## 3. 验收判据（必须能红）

- 注入：三腿心跳 mtime=now-1800s 且 `active_window` 覆盖当前时刻 → 连续两轮 reaper 后
  `.runtime/audit/emergency_track.jsonl` 出现 `state=activated` 且 `action.tripped` 非空、
  `.runtime/audit/kill_switch_orchestrator.jsonl` 同批多一行。
- 反证 1：把 `evidence_horizon_seconds` 改 1 → 隔夜旧心跳必须判 unknown（不拉闸）。
- 反证 2：窗口外必须 `state=outside_active_window` 且零下单。
- 反证 3：`_execute_trip` 抛异常必须 `action.failed=true` + breach `killswitch_trip_failed`。

## 4. 风险与回滚

- **误熔断**（最高风险）：已有三闸（unknown 不计/证据视界/盘外窗口）+ 连续确认；仍建议
  Owner 决定是否需要"仅盘中且持仓非空才动作"第四闸（需交易日历，本车道未引 calendar 依赖）。
- 回滚=`git revert` 本批 commit；紧急旁路=`config/emergency_track.yaml` 置 `enabled: false`
  （显式回退真值开关，仍留痕 `state=disabled`，非删码）。
- 门位：动作方向=停止交易（fail-closed），不涉资金转出；但**默认启用**是否可接受属 Owner 判断，
  已登记 `adjudications/req_wiresafe_01.md`。
