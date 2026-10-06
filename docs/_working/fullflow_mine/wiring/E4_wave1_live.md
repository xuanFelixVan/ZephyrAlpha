---
ttl: task_bound
title: "策略第一波实弹上线执行报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-05
---

# E4 波 1 实弹上线执行报告（E-TIMING-001 / TSMALL-001 / DABAN-023）

> 依据=D4_rollout_plan.md §5 机械步骤清单 + Owner 批件（2026-10-04"全部批准现在施工"+"全部执行"，13 张实弹转正）。
> 结论先行：**三卡=部署就绪（frozen 已落盘，待 10-08 首交易日补最后 Flip）**；实弹通道真桥已验证；执行段存在 3 项缺口（§4），按铁律"禁止伪造实弹"如实停在下述水位，缺口补齐+10-08 开盘后首笔最小单即上线。

## 1. 实弹通道勘察结论（真桥，非模拟桥层级）

| 面板 | 证据 | 判定 |
|------|------|------|
| 实盘桥目录 | E:\qmt_bridge 在位；`config/asset_inventory.yaml` L122 `OFFREPO-QMT-BRIDGE-REAL` type=trade_bridge criticality=critical（成交与回执历史不可再生） | 真源在册 |
| 实盘执行器 | ZEPHYR_EXEC_REAL.txt（账户 8887871993，tick 级 dumb executor，读 orders_real.csv 写 ack_real.csv，两阶段 rename+计数确认+重试幂等） | 在位 |
| 真实下单通道 | ack_real.csv 24 条 SENT/CANCEL_SENT 回执，含真实柜台委托号（635209413 / xt1090585409 / xt1090586364）=2026-08 实弹探针真成；非只到模拟桥层级 | **已验证开通过** |
| QMT 终端 | 勘察时点 XtMiniQmt.exe(PID 4540)+XtItClient.exe(PID 40176) 在跑 | 在线 |
| 仓内执行段 | QmtFileBridgeBroker 双实例物理隔离 env=real/sim（`src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py`）；QmtTradingSession(env) 切换点 `enable_real=(env=="real")`；断点 E4 execution_report 生产端默认接线；订单九态桥=saga_session_orchestrator（BROKER_STATE_TO_ORDER_STATUS 唯一真源，未知九态 fail-closed） | 正门在位 |
| sim/live 切换点 | ①`qmt_file_bridge_integration.py` enable_real 默认 False；②`qmt_trading_session.py:132` env 参数；③`scripts/backtest/sim_daily_runner.py` bridge-execute 执行腿 `_BRIDGE_ENV="sim"` 恒定（裁定#338⑤ real=Owner 门）；④dashboard `app_panel.py:542` enable_real=False | 四点定位，未改模拟盘行为 |
| 总闸 | reaper 存活（last_run=2026-10-05 02:27，emergency_track_state=normal）；trading_kill_switch 5 级（DAILY_LOSS daily_pnl<-3%*aum→cancel_all+disable_new 实证 L83） | 在岗 |

## 2. 三卡三证核验与状态翻转（逐卡）

三证判据=card_state 可转+code_path 代码在位+考试成绩在案。**三卡三证全过，无一延后**。

| 卡 | status/lifecycle/algo（与计划 §3 一致） | code_path 在位 | 考试成绩（evidence 在案） | card_state 翻转 |
|----|----|----|----|----|
| STR-E-TIMING-001 | active/sim/quantized | scripts/backtest/lane_e_quantile_baseline.py | 三窗全绿 IS 1.15/OOS 0.83/S3 0.98（run=SCR-C4-OOS2-20260913；CH CAND-e3da6fa71af1） | **frozen**（E4W1-ETIMING001-CRED-20261005） |
| STR-TSMALL-001 | active/candidate/quantized | scripts/backtest/translated/c4_dc5b80aa3614_tsmall100.py | 双窗 IS 1.066(DSR 0.888)/OOS 0.694（run=SCR-C4-20260914） | **frozen**（E4W1-TSMALL001-CRED-20261005） |
| STR-DABAN-023 | active/candidate/quantized | scripts/backtest/translated/c4_4440d07f973f_ultrashort.py | 双窗 IS 0.070/OOS 0.795（run=SCR-C4-20260913+14） | **frozen**（E4W1-DABAN023-CRED-20261005） |

翻转落盘方式=strategy_registry.yaml 卡字段真实变更（claim st-datasop-20260930；safe_write_text CAS 写入+进程外 YAML 复核：161 条目守恒、仅三卡 +15 行、其余 158 卡零携带）。每卡写死：frozen_at=2026-10-05、frozen_basis（考窗=evidence 既有值禁现场调参）、observation（观察 5 交易日卡级熔断线：E-TIMING 日>1.5% 或 5 日>3%；TSMALL 5 日>4%；DABAN 单日>2%——计划 §4.4；起步仓=额定 1/3，首笔=起步仓再取 1/2，滑点<模型 1.5 倍）。

TDM 挂点（D4 §5.3）已核：E-TIMING→TDM-E-L1（L379 verified）、TSMALL→TDM-E-L3-07-3（verified）、DABAN→TDM-P-P2（verified）；`decision_map validate` 过（仅既有 R22 warning，零 error）。

## 3. 首单证据与 10-08 配置现状

- 今日 2026-10-05 休市（`trading_calendar.is_trading_day(2026-10-05)=False` 实测；首交易日=2026-10-08=True 实测）→ 今日物理不可发真实市价单，如实不留痕假单。
- 首笔最小单（100 股或 1 手）触发链已勘察定形：委托批次文件（data/runtime/qmt_bridge/orders/orders_<day>.csv，`symbol,action,shares[,limit_px]`）→ bridge-execute（窗口闸 09:30-11:25/13:00-14:55+幂等批次指纹+三闸 OrderManager/R-H5E-1）→ QMT 文件桥 → 实盘执行器 → 订单九态回执。scheduled 通道（ZephyrAlpha_SimBridgeExecute 09:35/13:05）现网为 sim 腿。
- **首单未发生=非"上线成功"，判"部署就绪"**：执行腿 env 翻转与三卡信号生成件未接（§4），10-08 前补齐即可在窗口内自动出首笔。

## 4. 缺口工单（部署就绪→上线的最后 Flip 清单）

1. **GAP-1 执行腿 env 翻转**：sim_daily_runner bridge-execute `_BRIDGE_ENV="sim"`→real 装配（enable_real=True，broker_id=qmt_real；Owner 北极星门位=本批件授权面，裁定#338⑤）。硬约束：sim 腿行为零变更（默认参数不动，实弹走显式通道）；实盘 broker 不注入 risk_validator（装配层现状，裁定#338⑤）。
2. **GAP-2 三卡信号生成件**：三卡 code_path 为回测重放接口（build(start,end)），实弹侧需 T 日信号→订单批次文件生产件（TSMALL/DABAN 有 translated 件可按 e4-replay 同构出目标仓位；E-TIMING 按 lane_e 件出中证 1000 姿态）；sleeve 族（multifactor/daban_sleeve）为家族级复合体，与卡的等价性须先核证，禁默认等同。
3. **GAP-3 卡级监控消费面**：卡级熔断线已写死卡字段（card_state_observation），消费方=执行腿接入时读字段注册 kill_switch signal_group 触发与 crisis_gate_log 卡级行（现表 schema 无 card_id 列，须扩 DDL 或独立卡级台账）；dashboard /api/strategies 现服务在码策略类，card_state 可视化挂点随执行腿一并接。
4. **GAP-4 台账面**：首笔成交后 sim_pocket_daily 同构实弹台账行落 CH；credential 三行（E4W1-*-CRED-20261005）在执行件首跑时换正式 credential 台账。
5. 观察期结转（D4 §5.7）：5 个交易日达标→card_state→green+升满额定；破线→suspended（§6 回滚预案，含 A 族合并闸联动）。

## 5. 合规留痕

- 改前 claim：strategy_registry.yaml @ st-datasop-20260930（lock_files）。
- 写入：safe_write_text CAS（before/after sha256 记录于 git_commit 附记）；.runtime/tmp/e4_card_state_freeze.py 手术件（首版锚点吞缩进致 YAML 破损，git checkout 回滚后整行锚点重做，破损零残留）。
- 本报告=新文件，creation_token 经 batch_creation_tokens.py 登记（拒收则留盘移交，见提交消息）。
- 提交：git_commit.py --session st-datasop-20260930（--adopt-prior-work --allow-non-worktree --skip-preflight --no-auto-enqueue），提交后 `git log -1 --name-only` 核实归属。
