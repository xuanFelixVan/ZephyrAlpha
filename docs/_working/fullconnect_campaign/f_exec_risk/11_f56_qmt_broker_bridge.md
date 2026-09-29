---
ttl: task_bound
title: "F56 QMT/miniQMT 桥——文件桥 broker/行情/会话/链路探针/通道退役（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
updated: 2026-09-29
---

# F56 · QMT/miniQMT 桥（ex_core/adapters 桥面 11 件）

> 上游=F53 订单生命周期（供单）；下游=券商柜台镜像（供持仓/资金/成交真源给 TradingSession/position_reconciler/execution_report）。
> 证据基线：m7 01 册+本日（09-27）活体复核（watchdog log/SimBridge 子命令/E: 路径三向实勘）。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | OrderManager.register_broker（qmt_file_bridge_integration.py:148）；行情注入=QmtFileBridgeQuoteProvider（quote.csv 尾读 64KB+残行回退+mtime 新鲜度）|
| 下游消费 | CounterStateMirror（get_counter_* 接口族 qmt_file_bridge_broker.py:727-755）；execution_report 生产端（attach :427，E4 默认开 :103）；check_broker_health→前端监控（:913）|
| 自动化触发 | ZephyrAlpha_QMTWatchdog Daily 08:45+12:55（qmt_watchdog.ps1）；ZephyrAlpha_SimBridgeExecute 09:35+13:05（**执行腿仍断，见 §三**）；会话本体=manual（start_paper_session 09:25 拉起）**〔过时标记 2026-09-29：执行腿已由 dd3b17f9fd 重建，见卷末刷新批注〕**|
| 真源与注册表 | 桥蓝图=blueprint_qmt_file_bridge.md（MOD-L06-001）；迁移台账=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md（未结案保留）；退役冻结注记=miniqmt_channel_manager.py:56-62（RETIRED_DATE=2026-09-18）|
| 门禁与质量尺 | R-H5E-1 sim 进桥前风控 fail-closed（:571-620，real 显式不注入=裁定#338⑤）；双实例物理隔离 env=real/sim（:336-351）；幂等拦截 :514-517；health 三档 ok/degraded/down |
| 当前运行状态 | **黄**。**终端活体本日新观测**：watchdog log 09-21..09-25 连续 OK（pid 活体），但 09-26 两班 SKIP exe not found（E:\国金证券QMT交易端\bin.x64\XtItClient.exe）——而本日 ls 实证该 exe **存在**；SKIP 均落周末（09-20/09-26），疑 E: 盘周末离线或瞬时 Test-Path 失败，**下一交易日 09-28 复核是否自愈**；桥代码绿（test_qmt_file_bridge_broker.py 在册）；**SimBridgeExecute 执行腿红**（子命令从未存在，M7-01 B1 本日复核未修）**〔过时标记 2026-09-29：执行腿已重建+实弹 exit 0 正常行出现；SKIP 自愈判定成立（09-28/29 四班连续 OK），见卷末刷新批注〕**|

## 二、子模块三级枚举（本日实扫 wc -l）

- **adapters**：qmt_file_bridge_broker.py 995（HTTP 18901 快路径 32ms fail-open 降级文件桥 5.7s；sysid 回填/撤单终态保护/#SENDING→#DONE 状态机）｜qmt_file_bridge_integration.py 253（一键装配双实例+LocalOrderQueue+E4）｜qmt_file_bridge_quote.py 320（反向行情桥）｜miniqmt_broker.py 1401（**退役通道残留**，券商清退 XtMiniQmt）｜okx_broker.py 600（testing，95 号 Phase 2 挂起）
- **会话/探针**：qmt_trading_session.py 185（策略层无感知会话；**:115 OrderManager() 裸构造=合规门零注入**）｜broker_link_probe.py 210（连接/下单/回报三延迟探针，**未接线**：生产装配点仓内未见）
- **通道管理**：miniqmt_channel_manager.py 278（五态状态机 DISCONNECTED→…→DOWN fail-closed，退役保留作参照实现）
- **脚本**：scripts/qmt_watchdog.ps1（无状态 one-shot，禁凭证 UI 自动化；路径 UTF-8 读 data/runtime/qmt_terminal_path.txt :45，-LiteralPath 探测 :52）

## 三、接线四态独立复核

| 面 | 四态 | 复核证据（本日） |
|---|---|---|
| 桥执行腿（SimBridgeExecute） | **断链未修** | run_sim_bridge_execute_daily.ps1:18/:76 仍调 `bridge-execute`；sim_daily_runner.py:871 子命令表仍只有 plan-bridge/plan-execute/e4-replay/report/settle 五个——bridge-execute 从未存在（git log -S 零命中在案）**〔过时标记 2026-09-29：dd3b17f9fd 已按 delivery_report_20260923 §3 处方重建 bridge-execute，见卷末刷新批注〕**|
| 终端活体 | 黄（周末 SKIP 疑环境性） | watchdog log 09-26 SKIP vs 本日 ls exe 存在；09-20 同款 SKIP 后 09-21 自愈先例 |
| 终态保护/sysid 回填 | 已落 | broker :193-204/:858-865/:903-910 |
| 探针/自愈 | 半接线 | broker_link_probe 零装配；degraded 只进前端读数无自动动作（M7-01 B2）|

### 骨架勘误
无状态级勘误（总册 built/P0 与"桥代码绿"相符，且总册已注"SimBridge 取证线索在案"）。**新观测登记**（非勘误）：终端 SKIP 周末模式——若 09-28 复跑仍 SKIP 则升级 P0（终端活体断=桥不可用）；本次按环境性暂记。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | bridge-execute 子命令从未存在，ps1 调空 **〔09-29 已闭合，见刷新批注〕** | 按 delivery_report_20260923 §3 全参数路径重建并入册提交+幂等预扫+quote 新鲜度闸（0.5-1 天；M7 施工，调度面归 M5）| **P0** |
| 2 | watchdog 周末 SKIP（09-26 新观测）**〔09-29 自愈判定成立，见刷新批注〕** | 09-28 复跑核验；若复现→查 E: 盘挂载/ps1 编码；顺带核 log 中文路径回显乱码（E:\国金...端in.x64 缺 b 字样=日志编码损伤）| P1 |
| 3 | degraded 无自动动作 | degraded 持续 N 轮→事件触发 cancel 在飞单+告警（1 天可施工）| P1 |
| 4 | broker_link_probe 零装配 | 装配时挂 sync loop 采样+deadman 新通道（0.5 天）| P1 |
| 5 | ENV_CONFIG 实盘账号明文 + CSV 列位硬编码 | env 文件化（0.5 天，待裁涉 real 配置）| P2 |
| 6 | 迁移台账三未结（Owner 验证 9/18 逾期等） | Owner 催办 | P2 |

## 五、自审闸三态
**挖干可施工**（桥面 11 件全实证；缺口 1 是 M7-01 已立案未修的最高优先施工项，本日复核确认仍未修；缺口 2 为本卷新增观测，处置有判据）。

## 六、复跑命令
```bash
tail -4 data/runtime/qmt_watchdog.log   # SKIP/OK 活体
grep -n "bridge-execute" scripts/run_sim_bridge_execute_daily.ps1 | head -2
sed -n '869,872p' scripts/backtest/sim_daily_runner.py   # 子命令表无 bridge-execute **〔过时标记 2026-09-29：该窗口现为 bridge-execute 实现段（:881 起），子命令表已六选〕**
ls "E:/国金证券QMT交易端/bin.x64/XtItClient.exe"   # exe 实存 vs SKIP 矛盾
sed -n '56,62p' src/zephyr/ex_core/miniqmt_channel_manager.py   # 退役冻结注记
```

## 刷新批注（2026-09-29 st-finaldel-freshb）

> 刷新基线：HEAD dev @ 0cacd4a64d（09-29）；对卷内真源跑 `git log --since=2026-09-28` 复核＋活体日志/CCR 现读。

- **翻面 commit（三件）**：
  - `dd3b17f9fd`（09-28 15:05，F56 断腿重建）：`scripts/backtest/sim_daily_runner.py` 新增 **bridge-execute 子命令**（SimBridgeExecute 执行腿，+308 行，:42 用法/:881 实现段）+ `tests/backtest/test_bridge_execute.py`（327 行）；按 delivery_report_20260923 §3 处方，正门装配三闸+env=sim ONLY+交易日闸。
  - `78982c4c81`（09-28 08:41，B7 超集袋）：`qmt_file_bridge_broker.py` +660（phantom_grace_s/cancel_hold_s 幻影宽限与撤单持有修复）+ integration +42 + 红样 384 行——桥面绿态加固。
  - `edf0788dfb`（09-29 04:21，三选一终局）：**kernel 竞体葬法选 c=墓碑收口**——CCR `f56_bridge_instruction_kernel` 条目 merge_evaluation 补墓碑（已退役，被 B7 实现 qmt_file_bridge_broker 取代，判定 commit=78982c4c81）；kernel 字节封存 `.runtime/commit_queue/blobs` 死袋 q-20260927-st-c7-f56-20260927-0001（blob_sha256 索引，永不丢失）；Owner 2026-09-29 批文③授权。**遗留：99 #36 行未回填墓碑终局（台账滞后一处，归总筹收口）**。
- **实弹探活（.runtime/logs/sim_bridge_execute.log 现读）**：09-28 13:05 班 `exit_code=2`（argparse invalid choice——子命令 15:05 才落，时序性一次性历史行）；09-29 09:35 班 SKIP（XtItClient not running，终端离线）；**09-29 13:05:23 班 `bridge-execute day=2026-09-29 exited: exit_code=0`（honest orders_file_missing 正常行）——执行腿复活达证**；带真实订单全链实弹仍未发生（无单可执行，属 F72 缺口1 处方延续）。
- **缺口状态修订**：缺口1 P0→**已闭合**（重建+实弹 exit 0 达证）｜缺口2 P1→**自愈判定成立**（watchdog log 09-28 08:45/12:55+09-29 08:45/12:55 四班连续 OK，与 09-20→09-21 自愈先例同型；编码乱码小项保留）｜缺口3-6 维持原状。
- **自审闸三态（刷新后）**：**挖干可施工（维持；卷内最高优先施工项已终局，三选一裁渠道墓碑收口）**——卷作 B7 现役实现的基线快照+kernel 退役登记锚使用；缺口1 处方对施工面失效。
- **复跑**：`python scripts/backtest/sim_daily_runner.py bridge-execute --help`（子命令在）｜`tail -4 .runtime/logs/sim_bridge_execute.log`（09-29 exit_code=0 行）｜`grep -n "f56_bridge_instruction_kernel" -A3 docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`（墓碑在册）。
