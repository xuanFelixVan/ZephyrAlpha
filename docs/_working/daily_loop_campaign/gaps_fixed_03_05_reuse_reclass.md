---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-GAP-RECLASS
completes_when: 归档随对账总账
---

# gaps_fixed_03_05 对账改判（原缺口单 vs 实物）+ 裁定号勘误

## 缺口③ intraday_l1_tracker"零调用方则接线"→ **改判 REUSE（已挂，勿接线）**
- 原判（蓝图审计 09-16 时点）"仓库内零调用方"已过时：`pipeline_events.wire_data_scheduler`
  现挂 `maybe_track_intraday_state`（60min bar 到达=自然唤醒，bar_key 查重幂等）。
- 实证：09-18 盘中 4 行（run_id intraday-track:2026-09-18T10:30/11:30/14:00/15:00）=
  事件链自动产出；本班总扳手 intraday 段=手动等价触发（幂等，no_new_bar 如实返回）。
- **再接线动作=零**（净零铁律：无缺口不新增）。

## 缺口⑤ pf_alloc"接线或触发路径说明"→ **改判 REUSE（接线条件已满足）**
- 事件链在役：maybe_emit_pf_alloc_daily（journal FIFO 先于账本入队——分配先落钱包才有额度）；
- 实证：09-18 16:34 alloc-2026-09-18-82cb50 落地（总盘 200 万/Σbudget=0.5206/钱包
  STR-E-TIMING-001=37.4 万+STR-VREV-025=66.8 万，budget_daily/shrinkage_daily/budget_change_log
  三表 ch_committed）；记号幂等（同日重触发=skipped:already_queued_or_done）。
- 裁定#257② 口径：接线条件（regime 快照供给+蓝图过审）已满足且已在产——无需施工，
  触发路径说明见 owner_gate_list.md F 项确认单。

## 缺口④ 路由表 → 设计稿已出
- routing_table_v1_draft.md（六段↔五态映射提议+三级路由结构+落地路径）；config 落地=Owner 门。

## 裁定号勘误（引用纪律）
- **#304 ≠ 砍做T**：现行 ruling_registry 里 #304=regime HMM 组件锚定重校准（regime_detector.py
  代码不变式绑定）；"做T现形态砍掉"终局裁定=**#331**（原 #304 撞号改号，renumber_note 在册）。
- 本班全部新引用按 #331/#390 口径；历史文档残留旧号不回改（以 registry 为准）。

## T 管道验活结论（REUSE 禁重做；策略槽空置）
- tick_t0/tick_matrix=文档战役资产已终局（#390 五卡全测毕，无未测卡；复活唯一口=新假设新卡快签）；
- cohort_daily_ledger=模块完好未接线（投产=Owner 门位，tasks.yaml 注册 cohort_ledger_daily）；
- intraday_tomorrow_forecast(MOD-PLAN-025)=纯函数封存（三消费点未接线，与做T无关勿被名字误导）。
