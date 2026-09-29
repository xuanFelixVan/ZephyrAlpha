---
ttl: task_bound
title: TRD-A10 模拟盘沙箱 v16→v17 换版 runbook（Owner 亲手清单 + 观察窗判据）
---

# TRD-A10 模拟盘沙箱 v16→v17 换版 runbook

> 台账 #29 · Owner 已批（2026-09-29）· 编制会话 st-zc9-lane-s-20260929（AI 只做仓内准备+只读探测，**未动 E 盘任何文件、未启停任何进程**）。
> 配套：观察窗台账=[observation_ledger.md](observation_ledger.md)；日终哨兵=`src/zephyr/ex_core/ghost_order_sentinel.py`（托管腿挂 `scripts/run_post_settlement.py`，15:30 结算链自动出报告）。

## 〇、探测结论（2026-09-29 凌晨，只读）

| 面 | 现状 | 判定 |
|---|---|---|
| 模拟盘执行器 | `E:\qmt_bridge_sim\ZEPHYR_EXEC_v16.txt`（13,342 B，2026-09-04，v16.4 含 HTTP 桥 127.0.0.1:18901） | **在运版本=v16** |
| v17 执行器 | `ZEPHYR_EXEC_v17.txt` 在 E 盘**不存在** | **v17 尚未构建**——换版前必须先有 v17 构建件 |
| 行情线 | `ZEPHYR_QUOTE_v17.txt`（2026-09-03）已在盘 | 行情线与执行线版本号独立，本 runbook 不动行情线 |
| 实盘侧 | `E:\qmt_bridge\ZEPHYR_EXEC_REAL.txt`（v14 方言） | **本 runbook 不触**（实盘四禁；env=real 拒单开关挂起等合规门验收，另行流程） |
| 仓内侧（B7） | broker `_reconcile_unconfirmed_claims` 运行时执法腿 + `order_manager` 撤单腿；判定尺（parse_instruction/duplicate_remark_violations）只读解析副本内联于 `src/zephyr/ex_core/ghost_order_sentinel.py`（唯一消费方=本哨兵）。原 `bridge_instruction_kernel.py` 及其复现用例已葬（78982c4c81 判定/葬法裁定 #420 同期），内核文件不落仓 | **仓内侧已就绪**（F56 沙箱内内核路线已葬且内核文件不落仓，仓内以 broker 腿+哨兵内联只读副本为现行真源） |
| v17 补丁规格 | `docs/_working/decision_map_campaign_20260924/links/L07_exec/trd_a10_bridge_client_defects.md` §五（4 条最小改动，语义与内核一一对应） | **构建 v17 的唯一真源** |

## 一、步骤清单（AI 可代办 / Owner 亲手）

| # | 步骤 | 谁 | 验证判据 | 失败处置 |
|---|------|----|----------|----------|
| S0 | **构建 v17**：按 §五补丁规格把 v16 改成 `E:\qmt_bridge_sim\ZEPHYR_EXEC_v17.txt`（纯 ASCII；①线程路径删除"下发即写 #DONE"只写 #SENDING ②周期末回写=写前重读+按 order_id 逐行合并+标号只升不降+临时文件 rename ③撤单行柜台 cancel 成功即 #DONE+CANCEL_SENT ack ④可选加固：盘外/is_last_bar 为假直接 #FAIL,out_of_session） | **Owner 亲手**（或 Owner 显式授权施工车道产出构建件；建议同时裁"选项 A"=沙箱执行器真源收编仓内，消除 E 盘不可审计面） | 静态对拍：四条改点逐一 grep 到位；与内核 [INVARIANTS] 逐条对拍；与 v16 diff 只含规格内改动 | 停在 v16，不换版（换版无 v17 可换） |
| S1 | **QMT 加载 v17**：模拟客户端停 v16 策略 → 粘贴/加载 v17 源码 → 盘外启动空转 | **Owner 亲手** | QMT 策略面板零报错、诊断打印正常、orders_sim.csv 零新增盖章 | 客户端停策略即回 v16 态 |
| S2 | **首日微单验证**（盘中 9:30-15:00）：1 手最小单走全链 | **Owner 亲手** | 该行 `#SENDING→#DONE` 且柜台 `Stock\Order.csv` 可见同 remark；无裸行复现、无重复合同 | 当日撤单/人工处理，不进观察窗 |
| S3 | **换版日登记**：台账 D0=换版日，观察窗=此后连续 30 交易日 | AI 可代办（Owner 口令后） | observation_ledger.md 首行填写 | — |
| S4 | **每日观察**：15:30 结算链托管腿自动出 `data/reports/ghost_order_sentinel_<date>_sim.json`；台账抄 ghost_count/status | 自动（托管腿）+ AI 每日核数 | 每日一行台账，禁漏记 | 托管腿异常看结算日志 `[ALERT]`/exception 行 |
| S5 | **（可选）盘上竞态复验**：换版后 submit→cancel 压测 | Owner 决定是否盘上复验 | 仓内 TestCancelRaceStress100 已 100×2 轮 0 漏单（19/19 绿） | — |

## 二、观察窗成功判据（17 号文 §四，一字未改）

TRD-A10 = **复现用例入库 ✓ + 修复后连续 30 个交易日零静默丢弃 + 撤单竞态压测 100 次 0 漏单 ✓**。

- 观察窗起点 = **换版日（D0）**，数 D0 起连续 30 个交易日。
- 每日"零静默丢弃"的机械判据 = 当日哨兵报告 `status=ran_and_clean` 且 `ghost_count=0`。
- 幽灵单口径 = 执行器已盖章（#SENDING/#DONE=声称已发）且该 remark 在柜台 `Order.csv` **全天全量行**（含已成/已撤/废单）零收录。
- **禁判日不算归零也不算失败**：`judgement_suspended`（柜台导出缺失/非当日）或 `bridge_missing` 日如实标注，待 Owner 决定补数或顺延；连续性中断与否由 Owner 裁定，台账禁填 0 冒绿。
- `ran_with_findings`（ghost>0）= 当日判据破坏：连续计数归零重数，当日必须 tracker 登记闭环。

## 三、回退步骤（Owner 亲手）

1. QMT 模拟客户端停 v17 策略（v16 文件未删，`ZEPHYR_EXEC_v16.txt` 仍在盘）。
2. 重新加载 v16 → S2 微单复验通过 = 回到换版前基线态。
3. 台账备注回退原因；观察窗作废，下次换版重计。
4. 若 v17 本身缺陷需改：改 E 盘文件属 Owner 亲手动作；语义改动必须先回仓内内核/补丁规格（禁沙箱单方面另写一套=第二真源）。

## 四、本车道已交付的仓内件（AI 部分，均已提交）

| 件 | 说明 |
|---|---|
| `src/zephyr/ex_core/ghost_order_sentinel.py` | 日终读侧对账尺（只读统计，不判单不复单）；判定复用内核同一把尺；柜台导出停摆=禁判不假绿 |
| `scripts/run_post_settlement.py` 挂腿 | `_run_ghost_order_sentinel_step` 托管腿（28d596cf96 hosted cleaning gate 同款：出声不阻断、不改退出码）；**无新建 cron/Timer**，自动触发=既有 15:30 结算宿主槽位 |
| `tests/ex_core/test_ghost_order_sentinel.py` | 10/10 绿：红（幽灵 N>0）/绿（干净=0）/停摆禁判/桥缺失降级/托管腿注入隔离 |
| `data/reports/ghost_order_sentinel_<date>_sim.json` | 每日报告（托管腿自动产出），台账抄数源 |
