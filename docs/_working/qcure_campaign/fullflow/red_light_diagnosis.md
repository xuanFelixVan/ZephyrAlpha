---
ttl: task_bound
title: QCure fullflow 红灯诊断书·NightlySentiment 0x80070002
session: st-qcure-20260925
---
# 红灯诊断书：AI 层 NightlySentiment（st-qcure-20260925 施工线E，只读诊断）

> 诊断人=施工线E；取证时点 2026-09-25 02:0x-02:2x；全程只读（schtasks /query、reg query、文件 mtime），未改任务/服务/数据。

## 1 判定结论

**类别 A＝路径/配置错（机械修复，待总包批准后改）。**

0x80070002（ERROR_FILE_NOT_FOUND）缺的**不是业务脚本，也不是依赖数据文件，而是任务动作要启动的可执行文件本身**：动作 Command 存的是裸名 `python.exe`，在计划任务启动环境的 PATH 解析失败。脚本路径错/依赖数据缺失/入口改名三假设全部排除（见 §2 证据链 3）。

## 2 证据链（五环闭合）

1. **任务面**：`\ZephyrAlpha_NightlySentiment`，已禁用；末跑 2026-09-16 22:30:01，Last Result=-2147024894（0x80070002）；触发=每天 22:30（StartBoundary 2026-09-15T22:30，即上线首夜就败，从未成功过）。
2. **动作 XML 实证**：`<Command>python.exe</Command>` + `<Arguments>scripts/data/run_nightly_sentiment.py</Arguments>` + `<WorkingDirectory>D:\ZephyrAlpha</WorkingDirectory>`——Command 是裸解释器名，无绝对路径。
3. **文件面三排除**：脚本本体 `D:\ZephyrAlpha\scripts\data\run_nightly_sentiment.py` 存在（1978B，mtime 09-15 05:22，先于首夜触发）；工作目录存在；其唯一业务依赖 `src/zephyr/intelligence/nightly_sentiment_window.py` 存在（导入失败会是 exit 1 + traceback，不会是 0x80070002——该码发生在 CreateProcess 拉起可执行文件阶段，轮不到脚本运行）。
4. **对照组（横向定位配置错）**：全 45 项计划任务中，以裸 `python.exe` 作 Command 的**仅此一家**；在岗同类全用绝对解释器路径——PatternMining=`C:\Users\fanzi\AppData\Local\Programs\Python\Python312\pythonw.exe -m ...`（每日 9:01 result=0），C4Exam=powershell.exe（系统目录，必可解析）。
5. **PATH 面解释失败机理**：HKLM 系统 PATH 无任何 python；HKCU 用户 PATH 虽含 Python312/Python311，但裸名解析依赖任务启动瞬间的进程环境快照——本机 PATH 注入史混乱（AGENTS.md RULE-ENV 自证"TRAE 注入 3.10 会崩"），且 `WindowsApps\python.exe` 应用别名 stub 存在（AppInstallerPythonRedirector，重解析目标版本钉死，09-22 13:22 刚随商店更新刷新过）——任一环漂移即表现为"找不到文件"。辅证：AGENTS.md 冷启动序列第 1 条强制手工修正 PATH，说明交互会话里裸 python 名都不可靠，何况任务环境。

## 3 处方（一句话）

经总包批准后按 PatternMining 惯例重建任务动作（Command=绝对路径 `C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe`，Arguments=`scripts/data/run_nightly_sentiment.py`，WD 不变；建议 `schtasks /create /f` XML 级重建把 Command/Arguments 分字段存，避免 /tr 含空格整串吞进 Command 的经典坑），`/enable` 后观察一个 22:30 夜窗 Last Result=0 即闭合；补跑缺口说明：脚本幂等（ReplacingMergeTree 同键替换），09-16 至今夜窗可按日 `--date` 回灌。

## 4 附记（登记义务）

禁用≠退役：无论修复与否，NightlySentiment 的"自动关闭"四要素语义欠账（fullflow 簿 F1）须在裁定登记面落一笔——修复（本案处方）或正式退役（类别 C 路径），二选一，不许停留在 disabled 悬置态。

## 5 黄灯三件（一行现状+处方）

- **AutoRuntime Core**：现状=入口 `python -m zephyr.trading` 在但无专属计划任务，TradingWatchdog 已禁用（lastresult 267011=从未运行），无常驻化设施；处方=F6 扶正——要么常驻化挂计划任务+keep 清单，要么把"手动启动"语义明示进宪法 §7，不许无名悬置。
- **仪表盘**：现状=STARTUP=manual 无常驻任务，`.runtime/dashboard/` 心跳目录不存在（实勘确认），存活证据查无；处方=F6——api_server 写 `.runtime/dashboard/heartbeat.json` 供 DeadmanSwitch/巡检读，兼修"断了几天无人知"。
- **QMT 桥**：现状=QMTWatchdog（每日 8:45）任务就绪+SimBridgeExecute 9:35，`data/runtime/qmt_watchdog.log` 停在 09-24 12:55（实勘 mtime 证实，今日触发窗未到属正常）；处方=挂 F4 last-result 巡检面，若 09-25 8:45 触发后 log 仍无写入即升级红灯。
