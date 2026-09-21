---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-GAP1-MASTER-SWITCH
completes_when: E2E 两圈通过+红蓝零问题
---

# gaps_fixed_01 手动总扳手（缺口①施工实证）

## 建了什么
`src/zephyr/plan_engine/daily_loop_master_switch.py`（MOD-PLAN-033，号段核实无撞号）：
一条命令串整圈——数据就绪门(fail-closed)→regime新鲜度(消费方口径)→warroom→晨间预案→
次日概率→pf_alloc→盘中L1→盘中归类→收盘验证→三表结算→日度拍板。

## 铁律合规
- **REUSE 优先**：全部 11 段=薄委托既有产出者（run_daily_warroom_pipeline/maybe_emit_daily_plan/
  maybe_track_intraday_state/verify_for_session/settle_all/run_daily_decision…），零平行实现、
  编排层零自建幂等键（对账发现 maybe_ 钩子内建 plan_date/trade_date/bar_key 查重，直调
  emit_for_trade_date 会追加修订行——E2E 首圈实证后已改用钩子）。
- **MANUAL-ONLY**：不挂调度器不进 tasks.yaml（挂表=Owner 门位，申请单在 owner_gate_list.md A）。
- **零下单**：观察/记录模式；拍板体=#305 安全态（GRADUATED_PACKAGES 恒空），结构性无实盘行为。
- **fail-open**：单段炸留痕继续，summary 如实计 ok/skipped/error；唯二 fail-closed=数据就绪门+输入校验。
- **regime 新鲜度按消费方口径**：编排器 D1（滞后>1交易日=缺）而非供给方 _REGIME_STALE_DAYS=3
  （阈值错位=断供根因）；缺则走官方逃生口 print_regime_history.py 子进程补印缺口窗。

## 登记链
- depgraph 设计节点 node_id=14905528（blueprint_id=MOD-PLAN-033，D_PLAN，testing，module 粒度）；
- 模块翻译 plain_zh 已登记（add_module_translation.py，entries 7154）；
- capability_lookup 审计已留（冷启动 §1）；
- 测试 `tests/plan_engine/test_daily_loop_master_switch.py` 5 用例全绿（新增文件，未改旧测试）：
  段序契约（verify 恒先于 settle）/输入校验 fail-closed/dry-run 零执行/就绪门阻断/单段 fail-open。

## E2E 实证（首圈 2026-09-18，05:41）
11/11 段 ok：regime fresh（required≥09-17 实际 09-18）→warroom premarket ok（scenario_plan
史上首次落库）→预案+次日概率落库→pf_alloc 记号幂等 skipped→盘中 no_new_bar（幂等）→
verify no_plan（09-15 无 plan_date:09-17 计划，诚实欠账）→settle 扫描→**拍板体出非降级行：
state=expansion@1.00 cap=60.00% no_trade=0 packages=∅ degraded=1(D2:L2)——regime 修复直接解锁**。
