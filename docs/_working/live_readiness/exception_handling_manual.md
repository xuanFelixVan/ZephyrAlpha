---
ttl: task_bound
completes_when: Owner 对手册点单后转 archived；首次实弹演练后按实测回填 v2
session: st-live-readiness-20260922
date: '2026-09-22'
---

# 异常处置手册 — 小资金实盘准入准备班 · 件3

> 班次：st-live-readiness-20260922（通宵令 §3 分包2）
> **编写纪律**：每个"系统行为"均对照已有代码/配置实测写出（证据=文件:行号），**禁编造**；凡系统未实现的行为，如实标"系统无此行为"，人工动作补位。本手册适用于 pilot 档当班 AI+Owner。
> 通用升级律：任何异常先**保命三动作**（①不重试绕行 ②如有在途单先确认撤干净 ③按对应条目留痕），再修因。

---

## E1 行情/交易断链（QMT 侧）

**现象**：下单被拒、回报中断、行情停更、Broker 连接断。

**系统实测行为**（有代码背书）：
- 连续拒单≥5 或价格偏离>5% → 五级熔断 CIRCUIT_BREAKER：**断开 Broker 连接**，冷却 600s，不自动重连（`trading_kill_switch.py:90-97`）。
- Broker API 超时>10s 或心跳丢≥3 → API_TIMEOUT 级：自动终止当前 Session，冷却 120s，**此级自动恢复**（`:106-113`）。
- 引擎层 HALT 级违规直接拒单抛错（`execution_engine.py:217-220`）。
- 行情侧：tick_subscriber 启动即跑 smoke_test_guard，TCP 配对辨识对端；判定连到 live → ERROR 告警（行情只读不阻断）（`config/qmt_environments.yaml` smoke_test_guard 节）。

**人工动作**：①查熔断级（`python -c "import sys; sys.path.insert(0,'src'); from zephyr.trading.trading_contracts.risk import trading_kill_switch as t; print([k.level.value for k in t.active_switches()])"`——注意内存态语义，须在**同一常驻进程**内查）②不手动重连，等冷却或 Owner 复位（H1）③当日第二次 CIRCUIT_BREAKER=终止当日交易，次日复盘。
**已知缺口**：熔断触发态无持久化——进程重启后熔断"失忆"（件1-R3 红），故进程崩溃后**当日禁自动恢复交易**，人工复核后重启。

## E2 数据断供（regime/行情/板块数据缺）

**系统实测行为**（有代码背书）：
- regime 快照缺 → crisis_gate fail-closed 平坦→判 normal 不误触；数据列退化→至少 warning（`pf_alloc/crisis_gate.py:267-277`）。
- 盘前门快照 L1 PIT 无行→absent 诚实降级；L2 板块门无持久化状态→**恒 absent，依赖 L2 门的策略包当日禁用**（`daily_gate_snapshot.py:160-162`，D2 口径：不伪造门态）。
- L5 kill_switch 读态失败→按已熔断保守侧处理（`daily_gate_snapshot.py:14,227-231`，D6）。
- 历史先例：regime 断供根因=供需阈值错位（3 日 vs 1 日），2026-09-21 丁线治本 `_REGIME_STALE_DAYS 3→1`（丁线 dloop-v2 批，be05d1b01f）。

**人工动作**：①门快照出现 absent→当日对应策略包禁用是**正常安全态**，不补伪造数据 ②regime 断供连续>1 交易日→按 data_ops 断供流程报数据线，不盘中手补 ③核实是否重演"阈值错位"型根因（看 `_REGIME_STALE_DAYS` 与消费方判据是否错位）。

## E3 模型/信号异常（信号缺、置信崩、包异常）

**系统实测行为**（有实证背书）：
- 无毕业包→零执行单：GRADUATED_PACKAGES 恒空、enabled_packages=∅（E2E 实证 `e2e_manual_run_report.md:78-79`）——**模型层整个挂掉的最坏结果=不交易**，这是设计行为不是事故。
- no_trade 三源合成：编排器三源任一成立即当日不开仓（daily-orchestrator-blueprint.md:30 口径）。
- 幸存者包翻车先例：E4 死刑 2 条（beta 伪装/运气候选）组队时剔除（IBT 台账 §1 策略资产行）。

**人工动作**：①信号缺=当日 no_trade，不手填信号（禁手填=裁定#305 语境铁律）②已毕业包行为异常→先降该包（Owner 门位），再走考试链复考 ③严禁"临时用旧信号顶一下"。

## E4 kill_switch / crisis_gate 触发后

**系统实测行为**（有代码背书，按层级）：
| 层级 | 触发 | 行为 | 证据 |
|------|------|------|------|
| 逐单闸 | 任一级交易熔断激活 | 拒**全部新单**；探针本身异常也 fail-closed 拒单 | `pre_execution_checker.py:183-203` |
| 日度额度 | crisis（regime dominant==r10） | 冻结**新**额度，**存量不强平**（skip 语义）；warning 档照跑+缩额至 CRISIS_SHRINKAGE_FLOOR=0.05+告警 | `crisis_gate.py:339-357`；`allocation_orchestrator.py:787-826` |
| 保命仲裁 | 回撤 EMERGENCY/破产地板击穿/系统性风险/流动性 | A1 单一仲裁点：trigger_kill_switch+**强清** | `risk_layer_orchestrator.py:27-31,76-85,114` |
| 复位 | 上述任一触发后 | **复位属 Owner**（AI 禁自复位）；DAILY_LOSS 冷却 86400s 不自动恢复；系统级 reset 需 Owner 语义 | `trading_kill_switch.py`（各级 cooldown）；系统级 `kill_switch.py:300-318` |

**人工动作**：①先分级（哪层触发？查 crisis_gate_log 表+熔断 active_switches）②crisis 档触发=当日新仓冻结为正常态，不做"解冻"操作 ③破产地板/EMERGENCY 触发=立即报 Owner，强清结果人工复核 ④复位一律走 H1 Owner 门位；复位前必须先定位根因（修因不复位，复位不修因=复发）。

## E5 双终端在线/误连实盘终端

**系统实测行为**（有实测背书，2026-08-03 双终端实证）：
- 两个 QMT 终端 exe 同名，LISTEN 58610 二义（SO_REUSEADDR 重复绑定），**"谁 LISTEN 端口"判型禁用**——曾把实盘误报成模拟盘（`qmt_environments.yaml` tcp_pair_authority 节）。
- 唯一权威=TCP 配对法（本进程 ESTABLISHED 连接 ↔ 对端进程配对→对端 exe 路径判 sim/live）；`tick_subscriber._identify_qmt_peer_via_tcp` 已实现。
- smoke 测试在 live 终端→ERROR 告警+**拒绝继续**（smoke_test_guard）。

**人工动作**：①任何连接前先跑 `Get-Process XtMiniQmt | Select Id,Path` 单终端初判 ②双终端在线必须 TCP 配对法 ③判出 live→当班 AI 停止一切连接动作并告警（禁区四条：`QMT_REAL_*`/`enable_real`/`ZEPHYR_ENV=live`/`switch_to_live` 全禁）④Owner 说"开的是模拟盘"也必须实测确认——common_mistake 节原文：用户易点错。

## E6 告警链故障（告警发不出/warroom 挂）

**系统实测行为**（有代码背书）：
- crisis 告警失败**不阻断**主流程，留痕 crisis_gate_log 表（`crisis_gate.py:402,450`）。
- warroom 组件全通道 fail-open（`warroom.py:17`）——作战室挂了不拦交易。
- 语义结论：**告警是尽力而为，保命靠熔断与人工巡检**；告警链故障≠交易安全事件。

**人工动作**：①发现告警链故障→查 crisis_gate_log 表补读未送达告警 ②当班提高人工巡检频次（盘前/盘中午/盘后三次→逐小时）③报治理线修通知通道，不当场改告警配置。

## E7 模拟终端未运行/Owner 四类事阻塞

**系统实测行为**（在案先例）：qmt_e2e_runbook 状态=**阻塞于模拟终端未运行**（`:8`）；终端 GUI 登录密码属 Owner 四类事，AI 不可代登。
**人工动作**：①当班 AI 报阻塞+等 Owner，不绕过（禁代输密码/禁改登录流程）②阻塞期间 paper 档台账任务照跑（纯数据侧不受影响）。

## E8 撤单/回报契约缺口（已知未闭环项）

**登记在案**（裁定#339 数据源切换裁决语境，2026-09-18）：桥客户端撤单 id 契约+隔夜单静默丢弃两缺口——**本班未复核其闭环状态**，列入 G 门复核（建议并入件4-G5 演练清单：演练必须含"撤单+隔夜单"两个用例）。
**人工动作**：演练/实盘前对这两个用例**先在 sim 实测**：撤单回报 id 是否对得上、隔夜挂单开盘前状态是什么；实测结果回填本条目 v2。

---

## 附：当班异常速查卡（贴作战室用）

| 症状 | 第一动作 | 禁止动作 |
|------|----------|----------|
| 下单全被拒 | 查 active_switches+pre_execution 拒单理由码 | 禁重试绕行、禁改阈值 |
| 当日浮亏逼近 -3% | 预告 Owner（熔断将至） | 禁手动减仓"防熔断"（熔断自动处置更优） |
| regime 数据 absent | 当日按 no_trade 倾向处理 | 禁手补数据 |
| 发现连的是 live 终端 | 停一切连接+告警 | 禁任何"只查一下"操作 |
| 告警发不出 | 查 crisis_gate_log+提高巡检频次 | 禁当场改告警配置 |
| 模拟终端没开 | 报 Owner 等 | 禁代登 |
