---
ttl: task_bound
title: "F56 QMT/miniQMT 桥——文件桥 broker/行情/会话/链路探针/通道退役（L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F56 · QMT/miniQMT 桥（ex_core/adapters 桥面 11 件）

> 上游=F53 订单生命周期（供单）；下游=券商柜台镜像（供持仓/资金/成交真源给 TradingSession/position_reconciler/execution_report）。
> 证据基线：m7 01 册+本日（09-27）活体复核（watchdog log/SimBridge 子命令/E: 路径三向实勘）。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | OrderManager.register_broker（qmt_file_bridge_integration.py:148）；行情注入=QmtFileBridgeQuoteProvider（quote.csv 尾读 64KB+残行回退+mtime 新鲜度）|
| 下游消费 | CounterStateMirror（get_counter_* 接口族 qmt_file_bridge_broker.py:727-755）；execution_report 生产端（attach :427，E4 默认开 :103）；check_broker_health→前端监控（:913）|
| 自动化触发 | ZephyrAlpha_QMTWatchdog Daily 08:45+12:55（qmt_watchdog.ps1）；ZephyrAlpha_SimBridgeExecute 09:35+13:05（**执行腿仍断，见 §三**）；会话本体=manual（start_paper_session 09:25 拉起）|
| 真源与注册表 | 桥蓝图=blueprint_qmt_file_bridge.md（MOD-L06-001）；迁移台账=docs/_working/2026-09-08-qmt-bridge-migration-ledger.md（未结案保留）；退役冻结注记=miniqmt_channel_manager.py:56-62（RETIRED_DATE=2026-09-18）|
| 门禁与质量尺 | R-H5E-1 sim 进桥前风控 fail-closed（:571-620，real 显式不注入=裁定#338⑤）；双实例物理隔离 env=real/sim（:336-351）；幂等拦截 :514-517；health 三档 ok/degraded/down |
| 当前运行状态 | **黄**。**终端活体本日新观测**：watchdog log 09-21..09-25 连续 OK（pid 活体），但 09-26 两班 SKIP exe not found（E:\国金证券QMT交易端\bin.x64\XtItClient.exe）——而本日 ls 实证该 exe **存在**；SKIP 均落周末（09-20/09-26），疑 E: 盘周末离线或瞬时 Test-Path 失败，**下一交易日 09-28 复核是否自愈**；桥代码绿（test_qmt_file_bridge_broker.py 在册）；**SimBridgeExecute 执行腿红**（子命令从未存在，M7-01 B1 本日复核未修）|

## 二、子模块三级枚举（本日实扫 wc -l）

- **adapters**：qmt_file_bridge_broker.py 995（HTTP 18901 快路径 32ms fail-open 降级文件桥 5.7s；sysid 回填/撤单终态保护/#SENDING→#DONE 状态机）｜qmt_file_bridge_integration.py 253（一键装配双实例+LocalOrderQueue+E4）｜qmt_file_bridge_quote.py 320（反向行情桥）｜miniqmt_broker.py 1401（**退役通道残留**，券商清退 XtMiniQmt）｜okx_broker.py 600（testing，95 号 Phase 2 挂起）
- **会话/探针**：qmt_trading_session.py 185（策略层无感知会话；**:115 OrderManager() 裸构造=合规门零注入**）｜broker_link_probe.py 210（连接/下单/回报三延迟探针，**未接线**：生产装配点仓内未见）
- **通道管理**：miniqmt_channel_manager.py 278（五态状态机 DISCONNECTED→…→DOWN fail-closed，退役保留作参照实现）
- **脚本**：scripts/qmt_watchdog.ps1（无状态 one-shot，禁凭证 UI 自动化；路径 UTF-8 读 data/runtime/qmt_terminal_path.txt :45，-LiteralPath 探测 :52）

## 三、接线四态独立复核

| 面 | 四态 | 复核证据（本日） |
|---|---|---|
| 桥执行腿（SimBridgeExecute） | **断链未修** | run_sim_bridge_execute_daily.ps1:18/:76 仍调 `bridge-execute`；sim_daily_runner.py:871 子命令表仍只有 plan-bridge/plan-execute/e4-replay/report/settle 五个——bridge-execute 从未存在（git log -S 零命中在案）|
| 终端活体 | 黄（周末 SKIP 疑环境性） | watchdog log 09-26 SKIP vs 本日 ls exe 存在；09-20 同款 SKIP 后 09-21 自愈先例 |
| 终态保护/sysid 回填 | 已落 | broker :193-204/:858-865/:903-910 |
| 探针/自愈 | 半接线 | broker_link_probe 零装配；degraded 只进前端读数无自动动作（M7-01 B2）|

### 骨架勘误
无状态级勘误（总册 built/P0 与"桥代码绿"相符，且总册已注"SimBridge 取证线索在案"）。**新观测登记**（非勘误）：终端 SKIP 周末模式——若 09-28 复跑仍 SKIP 则升级 P0（终端活体断=桥不可用）；本次按环境性暂记。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | bridge-execute 子命令从未存在，ps1 调空 | 按 delivery_report_20260923 §3 全参数路径重建并入册提交+幂等预扫+quote 新鲜度闸（0.5-1 天；M7 施工，调度面归 M5）| **P0** |
| 2 | watchdog 周末 SKIP（09-26 新观测） | 09-28 复跑核验；若复现→查 E: 盘挂载/ps1 编码；顺带核 log 中文路径回显乱码（E:\国金...端in.x64 缺 b 字样=日志编码损伤）| P1 |
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
sed -n '869,872p' scripts/backtest/sim_daily_runner.py   # 子命令表无 bridge-execute
ls "E:/国金证券QMT交易端/bin.x64/XtItClient.exe"   # exe 实存 vs SKIP 矛盾
sed -n '56,62p' src/zephyr/ex_core/miniqmt_channel_manager.py   # 退役冻结注记
```
