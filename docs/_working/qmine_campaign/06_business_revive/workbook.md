---
ttl: task_bound
title: QMine作业簿·业务扶正三件+文档漂移两件
session: st-qmine-20260925
---
# 06 业务扶正三件 + 文档漂移两件（M6 只读深挖）

> 边界：只读调查+只写本簿；禁改代码/禁 git 写/禁队列操作/禁改计划任务。基线=fullflow/workbook.md（绿8/黄3/红1）+red_light_diagnosis.md §5 黄灯三件。取证时点 2026-09-25（夜班，QMT 今日双触发窗已过）。

## 1 六向台账

### ①上游输入（证据源）
- 代码：src/zephyr/trading/__main__.py（111L）、auto_runtime_core.py（1300L）、runtime_config.py→shared/contracts/runtime_types.py；scripts/start_trading.ps1（188L）、register_guard_tasks.ps1、qmt_watchdog.ps1、deadman_switch.ps1（214L）、start_paper_session_daily.ps1/start_paper_session.py；src/zephyr/frontend/dashboard/api_server.py（4561L）、services_registry.py、app_panel.py 头注。
- 注册表：architecture_issue_registry.yaml #ARCH-142（L18045 起，TradingWatchdog）+#ARCH-QCURE-APPROVAL-CHAIN-001（L22511）；candidate_module_registry.yaml CAND-GOVSEC-002（L8134 起）；ruling_registry.yaml 裁定#410（L5642-5662）；runtime_types.RuntimeConfig。
- 运行面：schtasks /query /v 实测（QMTWatchdog/PaperSession/SimBridgeExecute result=0，TradingWatchdog N/A/267011）；data/runtime/qmt_watchdog.log；config/.env.qmt。
- 实测命令：python -m zephyr.data --help（Python 3.12.8）。

### ②下游消费（五件三态总表）
| # | 件 | 实勘结论 | 三态 |
|---|----|----------|------|
| ① | AutoRuntime Core 常驻化 | 入口=常驻服务设计（boot+reconcile 每 5s 轮询，非批处理）；TradingWatchdog 全套守护已建成但注册 Disabled（92 D3：启用=生产行为变更=Owner 窗口），启用有注册表明文前置（CAND-GOVSEC-002 ①）；sim 交易自动链已由 PaperSession 9:25 等绿件覆盖，常驻化≠自动交易 | **黄→推荐维持手动+宪法明示**（常驻化=有条件绿灯，前置未落） |
| ② | 仪表盘心跳 | api_server=FastAPI 8890 一体服务，零心跳写入；DeadmanSwitch 监控 3 进程+2 业务心跳（tmp/*.heartbeat 管道格式，5min 触发/stale>10min 告警） | **绿（可施工）**——最小方案见 §2② |
| ③ | QMT 桥巡检 | QMTWatchdog 在册就绪 result=0；今日 08:45:03+12:55:03 双写"OK process running"——黄灯"触发后应写"已兑现 | **绿（确认件）**——对账判据移交 M5 |
| ④ | 宪法"7 子命令"漂移 | 实测 `python -m zephyr.data --help`=**8 个**（cli.py:342-368 同证） | **黄（待批文）**——批准链已铺，见 §2④ |
| ⑤ | 宪法速查表抽查 | GitCommitGateway/commit_queue/DatabaseService 入口实存✓；**新发现漂移：§7 仪表盘入口指向 app_panel.py，而 app_panel 已 DEPRECATED（08-29 裁定 R22/R23），真源=api_server.py:8890（W6）**；commit_queue 实为 6 子命令 §7 只列 4 | **黄（与④同议题搭批文）** |

### ③机制现状
- TradingWatchdog 设计（#ARCH-142 已落地件）：Task Scheduler（AtLogOn 延 4m+Once，每 5min 重触发）→start_trading.ps1（while-true 守护+单实例锁+15s 心跳 tmp/trading.heartbeat+孤儿清理+防快速重启）→python -m zephyr.trading。注册 Disabled 幂等（create-if-absent，已存在不碰）。92 D3 裁定理由：实证无常驻交易生产进程在跑，enabled 注册=凭空拉起=生产行为变更；翻开=Owner 一键（Enable-ScheduledTask+schtasks /run）。
- DeadmanSwitch：一次性脚本，任务每 5min 重触发；监控清单实勘（deadman_switch.ps1 L58-60+L102+L144）=scheduler/tick_subscriber/ch_health_probe 三个进程心跳 + tick_subscriber_biz/live_strategy_biz 两个业务心跳（后两者盘中时段门控——**manual 服务缺文件不告警的条件门控先例已在库**）；告警=tmp/deadman_switch_alerts.log + Windows Event Log 9002，无推送通道。
- sim 模式真源：AutoRuntimeCore 全文零 broker/ex_core 引用——`python -m zephyr.trading` 本身无 sim/real 开关；sim/real 甄别在执行层：config/qmt_environments.yaml（#ARCH-QMT-ENV-DISAMBIG-001）+config/.env.qmt（QMT_SIM_ACCOUNT=8886156677 / QMT_REAL_ACCOUNT=8887871993），broker 装配 env="sim"（enable_sim=True, enable_real=False），生产路径=start_paper_session.py build_sim_broker（L271）。

### ④代码面（施工挂点）
- ②心跳挂点：api_server.py 模块级 app 定义处（L74 前）启动写一次 + daemon 线程每 60s 原子写（tmp 写+Move-Item 同卷原子，仿 start_trading.ps1 Write-Heartbeat L87-95）；格式=tmp/dashboard.heartbeat 管道格式 `ISO8601|<pid>|<pid>`（services_registry._read_heartbeat L250 即认此格式，零新增解析器）；巡检侧=deadman_switch.ps1 增第 6 路条件门控通道：仅当 8890 端口监听在而心跳 stale>10min 才告警（仿 live_strategy_biz 的门控式）——文件缺失+无监听=manual 常态，静默。
- QCure 处方（.runtime/dashboard/heartbeat.json）**不建议**：与 tmp/*.heartbeat 管道格式惯例不同构，deadman+services_registry 双处加解析=漂移温床。
- ④修正挂点：AGENTS.md §7 行；⑤同文件 §7 仪表盘行。两处修正合一个 ARCH 议题一次批文。

### ⑤运维/呈现面
- 今日 schtasks 实测：QMTWatchdog/PaperSession/SimBridgeExecute 全 result=0（next 9/26）；TradingWatchdog 267011（0x41303=从未运行，Disabled 态正常）；DeadmanSwitch 今日 20:52:46 触发 result=0。
- M5 对账件接入点：commit_queue.py 新增 `health` 子命令（四态计数/死因/最老项龄）可作对账数据源；ResourceMorningReport 6:31 可承载晨报级聚合。

### ⑥失败态与数据面
- qmt_watchdog.log 1265B，今日 08:45:03/12:55:03 双行 OK（pid 21512/25524）——QMT 终端进程两窗均存活，无 LAUNCHED/SKIP。
- trading_guard.log/trading.heartbeat/trading.lock 均不存在——TradingWatchdog 从未真跑，与 267011 互证。
- 内存红线：RuntimeConfig 自带 BrainResourceBudget max_brain_memory_mb=2048（D-INF035-08 裁定，boot 超 2GB 拒启动/运行超限降级）+__main__ RLIMIT 4GB（Windows 跳过）。20G 可用对 2GB 预算充裕，内存不是常驻化阻塞项——真正的阻塞项是 §2① 的护栏前置。

## 2 五件方案

### ① AutoRuntime Core 常驻化——推荐：维持手动+宪法明示（F6 取"明示"支）
**权衡**：常驻化挂计划任务（8:45 形态）收益=AI 大脑层 RTO<5min（宪章约束五）+消"手动启动=无名悬置"；风险/成本=（a）启用即上线 CAND-GOVSEC-002 ①盲区——trading 常驻进程内 retention.py/log_rotation 等 os.remove/rmtree 全量裸奔，启用后可无痕自毁审计链（8-23 型事件连取证都失去），注册表已写死"TradingWatchdog 计划任务启用前必须完成 ①"；（b）92 D3+#ARCH-142 双裁定封死"非 Owner 窗口翻开"的路；（c）boot 自起 Ollama/L2 模型族（auto_start_l2=True 默认），与夜间 GPU 训练矩阵争资源；（d）**关键事实：常驻化它不产生任何交易自动化收益**——sim 交易链（PaperSession 9:25→SimBridgeExecute 9:35→PostSettlement 15:30）已全自动且全绿，AutoRuntime 是 AI 任务系统不是下单引擎。
**推荐**：手动明示。落地=宪法 §7 行改注记（见 §2④ 批文搭车）："AutoRuntime Core | `python -m zephyr.trading`（AI 大脑，手动启动；交易执行自动链=PaperSession 9:25）"。**翻开路径**（条件成熟时，Owner 窗口）：落 CAND-GOVSEC-002 ① in-process ops_guard 装配→观测期→Enable-ScheduledTask ZephyrAlpha_TradingWatchdog+schtasks /run→同窗把 tmp/trading.heartbeat 加为 deadman 第 4 路（start_trading.ps1 L39-43 明示同窗义务，否则 MISSING 假警）。基础设施零新增——守护脚本/任务/心跳格式全部已建成待命，翻开只是两个 Owner 动作。

### ② 仪表盘心跳——最小方案（纯代码件，可施工）
1. api_server.py：模块加载完成处写首跳 + `threading.Thread(daemon=True)` 每 60s 写 `tmp/dashboard.heartbeat`（`ISO8601|<pid>|<pid>`，原子写仿 start_trading.ps1）。
2. deadman_switch.ps1：加第 6 路条件门控通道 `dashboard`——8890 有监听且心跳 stale>10min 才 CRITICAL（照 live_strategy_biz 门控模板）；8890 无监听=面板未开（manual 语义），不告警。
3. services_registry.py api_server 条目 `detect` 可选加 heartbeat 字段，面板自身状态页顺带显示新鲜度（非必需）。
改动 2 文件、零新任务、零新格式；兼修"断了几天无人知"（面板挂了端口死=静默，本方案对此仍盲——如需覆盖"该开没开"，属 F4 巡检面另议，不在最小方案内）。

### ③ QMT 桥巡检——确认件+判据移交
QMTWatchdog 在册（\ZephyrAlpha_QMTWatchdog，Ready，8:45+12:55 双触发，交互登录态，result=0）✓。今日触发后日志验证机制（给 M5 对账件的三判据）：①`data/runtime/qmt_watchdog.log` mtime>当日触发时点；②末行 stamp=当日且前缀∈{OK,LAUNCHED}；③schtasks Last Result=0。升级红灯条件：末行=SKIP exe not found / path config missing，或触发窗后 2h 仍无当日行。**今日双窗已验**：08:45:03/12:55:03 双 OK（XtItClient 存活 pid 21512→25524 有重启）。与 M5 schtasks 对账件是同一件——本件只确认在清单+给判据，不另建巡检。

### ④ 宪法"7 子命令"漂移——实测 8 个，批准链建议
实测：`python -m zephyr.data --help` 列 8 子命令 status/list/run/rerun-failed/pause/resume/start/speed-test（cli.py:342-368 结构同证）。
**修正文案（两案）**：A=改"（8 子命令）"——最快但下次加子命令再漂；B=改"（子命令见 --help）"——推荐，合宪法 §4.4"计数用字段不写死在散文"+净零纪律（计数真源永远是 --help）。
**审批路径**：AGENTS.md 在 PROTECTED_PATTERNS（check_protected_paths.py L73"重大修改须 Owner 审批"）。PROTECTED-PATHS 三通道：[ARCH-APPROVAL:<已登记issue>] 标记（id 防伪必查册）/ 活跃裁定 approved_paths fnmatch / 阻断。**不能复用 ARCH-QCURE-APPROVAL-CHAIN-001**：其依赖的裁定#410 approved_paths=["docs/01_policies_and_standards/rules/"]（ruling_registry.yaml L5658）不含 AGENTS.md；而扩 #410 的 approved_paths 须改裁定册——裁定册经 #ARCH-QCURE-APPROVAL-CHAIN-001 刚入保护清单，改它同样要 ARCH 批文，绕一圈仍归新议题。**建议**：新立一个 ARCH 议题（建议号 #ARCH-AGENTS-SSOT-DRIFT-001）打包 ④+⑤ 两处 AGENTS.md 修正+①的 §7 注记（三处一文件一批文一次 commit），commit message 带 [ARCH-APPROVAL:ARCH-AGENTS-SSOT-DRIFT-001]；议题登记面=architecture_issue_registry.yaml（按 #ARCH-142 同款格式），立议题动作本身留总包/Owner 执行（本班禁 git 写）。

### ⑤ 宪法速查表其他条目抽查（3 条+顺带）
| §7 条目 | 宪法描述 | 实况 | 判定 |
|---------|---------|-----|------|
| GitCommitGateway | zephyr.gov_enforcement.rule_bridge.git_commit_gateway | 模块实存✓ | 无漂移 |
| 提交队列 | scripts/commit_queue.py（enqueue/status/drain/requeue） | 实存✓，但子命令实为 **6 个**（+cleanup/health，L2854-2917） | 轻度漂移（列举不全非计数错误；health 对巡检面有用，建议补列） |
| 数据库服务 | zephyr.infrastructure.database_service | 模块实存✓ | 无漂移 |
| 仪表盘（顺带发现） | src/zephyr/frontend/dashboard/app_panel.py | **app_panel 已 DEPRECATED**（头注明示 2026-08-29 Owner 裁定 R22/R23，新版正式家=dashboard/web/；W6 后一体服务真源=api_server.py:8890） | **实质漂移**——宪法指向弃用入口，修正="src/zephyr/frontend/dashboard/api_server.py（8890 一体服务）"，与④同议题 |

## 3 自审闸三态裁定
- ①常驻化：**维持手动+明示**（推荐已给，翻开后置条件已铺）；②仪表盘心跳：**可施工**（纯代码 2 文件）；③QMT 桥：**已确认绿**（判据移交 M5）；④⑤宪法漂移：**待批文**（新 ARCH 议题打包三处修正，批准链已铺好，材料齐备）。
- 本环节未改任何代码/任务/注册表；新建本簿 .md 的 CREATE-GUARD creation_token 登记义务随总包提交批文一并落。

## 4 长尾清单
- CAND-GOVSEC-002 ①（交易进程 ops_guard 装配）是 TradingWatchdog 翻开的硬前置，建议总包把它登记为独立矿脉（估 1-2 人天，注册表自带施工法）。
- deadman 告警只落 tmp/deadman_switch_alerts.log+Event Log，无主动推送——可挂 F4/M5 晨报聚合面。
- commit_queue `health` 子命令（四态计数/死因/最老项龄）可作 M5 对账件数据源。
- app_panel.py 弃用文件本体退役（Owner 确认 web 版完全涵盖后）另案，勿与宪法改行混做。
- TradingWatchdog 残留观测点：services_registry.py L175 仍有其 detect 条目+services.html"已注册未启用"注记——翻开时同步改面板文案。
- 裁定#410 expires_at=2026-10-08——QCure 授权链到期日，总包台账应记。
