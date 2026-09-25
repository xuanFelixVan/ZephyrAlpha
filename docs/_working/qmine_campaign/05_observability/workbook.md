---
ttl: task_bound
title: QMine作业簿·M5观测面四矿
session: st-qmine-20260925
---
# M5 观测面四矿作业簿（残差计时/trigger注入校验/预检缓存/schtasks对账）

基线：docs/_working/qcure_campaign/observability/workbook.md（四本账盘点）。本簿只读调查，零代码改动；全部数字为 2026-09-25 实测。

## 1 六向台账（四矿共用观测面）
### ①上游输入
- landing_phase_stats.jsonl：commit_queue_landing.py:909-939 写（phases 分段+residual_ms），落各工 worktree `.runtime/audit/`；`_timed_phase` 装饰器（:892-906）按方法 def 位挂载，现有 8 相=worktree/sync/conflict/snapshot/prestage/cas/converge/baseline（:1070-1835）；emit 挂 pool worker finally（:2869）覆盖成功/死信/环境失败三出口。
- in_process_gate_registry.yaml：102 条目=total_gates 声明（机械对账在 registrar:240-242）；files_trigger 字段 26 门声明、76 门无（=always-fire，其中 72 门 enabled）。
- commit_preflight.py:170-171 双册路径常量；`_head_registry_yaml_data`（:174-194）=git show+yaml.safe_load 单一咽喉（capability+translation 两册都走它）；`_head_tracked_relset`（:197-202）已跑 `ls-tree -r HEAD --name-only`（实测 47ms）。
- Windows 计划任务面：49 个 ZephyrAlpha* 任务在册（Get-ScheduledTask 实测）；登记真源散在 scripts/register_*.ps1 + backup_daily_trigger.ps1（grep 提取=35 个声明名）。
### ②下游消费
- landing_phase_stats：仍零消费方（qcure 簿已记）；residual_ms 是"下一轮装表靶子"（写者自注 :910）——本簿矿①即其收口件。
- files_trigger 消费=commit_gate_registry.py:280-292 `_files_trigger_hit`，**四路 OR 语义**：目录前缀(`p/`+startswith)｜精确(rel==p.rstrip('/'))｜fnmatch 通配｜子串(p in rel)——不是纯子串匹配，校验规则须按四路语义设计。
- 预检解析结果：无任何缓存（gate_cache_preflight.py 缓存的是 gate **结果**，key=gate_id×own_scope×staged树指纹×HEAD_sha×flags mtime，白名单只收纯内容扫描 gate——注册表解析不属其层）。
- LastTaskResult 全仓消费：**零**（仅 backup_ch_vm.ps1:87 / backup_daily_trigger.ps1:110 单任务自检打印；backfill_night.ps1:17 注释点名"LastTaskResult 静默失败病"）。
### ③机制现状
- 残差构成：gateway.commit（全门禁链）在 `__call__` 体内调用（:2104 主路径+:2152 Mode B 自愈重试），不落任何 _timed_phase 相；实测 fixture 样本残差 17.8-45.8%，生产样本（qcure 簿）total 101984/accounted 2563=残差 97.5%——门禁链段是残差主身。
- registrar 对 files_trigger 的处理（L221-223）：`tuple(ft) if isinstance(ft,list) else (str(ft),)`——非 list 标量静默 str() 化（dict/数字→垃圾模式）、无任何语法校验；册侧笔误=静默改触发面（变大：误触发噪音；变小：**门禁静默免检**，危险方向）。
- 预检成本实测（本机 HEAD）：capability 册 show 31ms+parse 2969ms；translation 册 show 63ms+parse 3469ms——**解析占 99%**（合计≈6.5s，与 QCure-B 实测 5.6s 同量级）；`git show` 本身可忽略。
- DeadmanSwitch（deadman_switch.ps1:56-102）：只读 tmp/ 下 3 心跳（scheduler/tick_subscriber/ch_health_probe）+tick biz 心跳；**不读 LastTaskResult、不覆盖 belt_daemon.heartbeat**——schtasks 对账件与其监控对象不同层，无第二监测重复。
### ④代码面（施工挂点）
- 矿①：`_record_phase(landing, name, ms)`（:883-889）累加语义现成；env 守卫 try/finally（:2101-2174）天然包住两次 gateway.commit。
- 矿②：校验可插 L219 现有 try 块内——异常自动流入 failures 收集→GateAutoRegistrationError（裁定#351 fail-closed 通道零新增控制流）；`_read_roster`（:97-123）是 load/auto 两入口共用结构校验位（备选）。
- 矿③：单咽喉 `_head_registry_yaml_data` 改造即可双册同治；blob sha 可从既有 ls-tree 顺带取（`--name-only` 去掉即带 sha，同成本）。
- 矿④：scripts/task_board.py 不读 schtasks；无既有 fleet 级消费方——生成器脚本为净新增（红线 §9-5 允许：生成器产出合法，禁的是手工清单）。
### ⑤运维/呈现面
- 49 任务命名两制：`ZephyrAlpha-`（连字符 5 个）与 `ZephyrAlpha_`（下划线）混用；4 个 Disabled one-shot（C4Exam_Full0916/OneShot0915、FactoryLaneC_Full0916/OneShot0915）+WeeklyRest Disabled。
- 对账报表无宿主：ConfigCheck（日 08:05）/GateFullTreeAudit（日 03:30）等既有日任务可作挂靠宿主，零新计划任务。
### ⑥失败态与数据面（2026-09-25 实测）
- 【红】DailyBackup LastTaskResult=267014（超时被终止，今 06:00）——DailyBackup 断 3 天历史教训**正在复发形态**；ResourceRegenCheck=3（ERROR_PATH_NOT_FOUND）；F06Grid=1、GateFullTreeAudit=1、**ProcessReaper=1（宪法 RULE-GUARDIAN 承重件退出码非零，建议 Owner 优先核查）**。
- 【黄】LibraryLedgerDrill=267011（从未运行，LastRunTime=1999 哨兵）；TradingWatchdog Disabled+从未运行。
- 【漂移】声明但不在册 4 个：BudgetReport/MetaqAuditReconcile/ModelExam/ModelIntelScan（register 脚本在、任务不在）；在册但无声明 17 个（含 4 个 Disabled one-shot）。
- 【注入面】files_trigger 六条零命中模式（对当前 tracked 树）：NO-BARE-GETENV/BARE-SUBPROCESS/NO-SECRET-HARDCODE 三门的 `password`、`api_key`——现网永不触发（内容语义型前向防御 or 死触发，需 Owner 认知）；超宽子串：`governance`=2377 文件、`docs/`=7858、`.py`=8764、`secret`=34（子串语义下 "secretary" 也命中）。结构违例（空串/反斜杠/纯glob/控制符）：**0 条**——现行名册可全量通过本簿提出的 fail-closed 规则。

## 2 四方案
### 方案① 残差计时：门禁链补相
**裁定：侵入最小=调用边界装表（A 案），弃 join 案（B）。**
- A 案（推荐）：在 `__call__` 的 env 守卫段（:2101-2103）前置 `t0=time.monotonic()`，在既有 finally（:2170-2174）加一行 `_record_phase(self, "gates", (time.monotonic()-t0)*1000)`。复用累加器+既有 finally，主路径与 Mode B 重试两分支自动同桶；drain/pool 两路都过 `__call__`，单点覆盖。**约 3 行+1 测试**。
- B 案（弃）：_emit_landing_phase_stat 里 join gate_execution_stats 的 total_ms——需记录项起点文件偏移/行数、重试双 flush 去重、跨账格式耦合，复杂度与脆弱面均高于 A；且 gate_execution_stats 有独立消费方（usage_stats/standard_checkup），不该被装表路径耦合。
- 注意：`@_timed_phase` 不能挂 `__call__` 本身（=整单耗时，与 total_ms 同义）；不拆函数（COMPLEXITY-GUARD 拆名丢豁免死信实证，:868-869 自注）。残差补相后仍余 claim/release 小头，可后续加 "claim" 相，非本轮必做。
### 方案② files_trigger 注入校验（fail-closed）
**合法条目定义（按 _files_trigger_hit 四路语义）**：files_trigger 缺省/null（=always-fire，合法）｜list[str]，每条：非空且 strip(self)=自｜禁 `\`（匹配器虽归一化，名册 canonical 强制 posix）｜禁控制符（\n\r\t，YAML 多行事故面）｜禁纯 glob（字符集⊂`*/?[]!` 的条目如 `*`/`**/*`，恒真=触发面爆炸，P5 条件触发形同虚设）。**非 list 标量（dict/int/str）一律拒收**（替换现 `(str(ft),)` 静默 coercion）。
- 插点：`_validate_files_trigger(gate_id, ft) -> tuple[str,...]` 在 L219-224 try 块内调用，异常入 failures→GateAutoRegistrationError——裁定#351 同款 fail-closed，零新增控制流。**约 15-20 行+测试**。
- 零命中（死触发）与超宽子串**不进 fail-closed**（warn+audit）：前者有"前向防御"合法用例（硬拦会误杀现网 6 条），后者阈值难定；先可见再治理。
- 存量实测结论：102 门禁全量扫——结构违例 0，现行名册全量通过；6 条零命中模式集中 3 个 secrets 门，随 warn 通道显性化后由 Owner 定夺（删或标注 content-trigger 语义）。
### 方案③ 预检册解析缓存
**键=（registry rel，blob sha），内容寻址零失效逻辑；弃"HEAD commit sha"键**（落地池每落一件 HEAD 即动，commit-sha 键在池内全 miss，等于没缓存）。
- 最小方案：`git ls-tree -r HEAD`（去掉 --name-only，成本同 47ms，顺带取每路径 blob sha——可复用 `_head_tracked_relset` 既有调用）→ `_head_registry_yaml_data` 内模块级 memo dict（rel+blob_sha→parsed dict，容量 2-8 即够，仅两册）。**约 15-20 行，单咽喉改造双册同治**。
- 内存缓存够不够：落地池=长命进程（WorktreeLanding 跨项复用 gateway）→ 第二件起全 hit，每件省≈6.5s；直连 CLI（git_commit.py 一命一进程）→ 内存缓存零收益（恒 1 miss=现状+0ms）。直连占预检事件 42%（1871/4476）。
- 跨进程（二期可选，需 Owner 点火）：blob sha 内容寻址落 `.runtime/cache/`（原子 os.replace 写、陈旧条目无害、无需 TTL）——直连路径也省 6.5s；代价=缓存目录卫生归属。一期先内存，实测直连等待占比后再议二期。
- 正确性论证：blob sha=内容哈希，HEAD:rel 内容对给定 sha 不可变——缓存命中恒等价于现算，无失效窗口；与 gate_cache_preflight 的 HEAD_sha-in-key 原则同源（复用思想不复用代码，不新增账本）。
### 方案④ schtasks 三色对账件
- 生成器（建议 scripts/schtasks_health_report.py 或 .ps1，一次性只读）：`Get-ScheduledTask` 取全部 ZephyrAlpha* 的 State/LastRunTime/LastTaskResult；期望清单**从既有真源导出**=grep register_*.ps1+backup_daily_trigger.ps1 的任务名声明（实测可提出 35 名），禁新建登记册（净零）；输出三色报表（绿=0 或 Running 件 267009；黄=267008/267011 哨兵/267012/267014/Disabled/节奏陈旧 LastRunTime 超 2×周期——DailyBackup 断 3 天型由此捕获；红=其余非零 win32 退出码如 1/3）。
- 防重复监测核验：DeadmanSwitch 只读 3 服务心跳（tmp/*.heartbeat），不读 LastTaskResult——对象不同层，无第二监测；belt_daemon.heartbeat 缺口属 qcure 簿矿脉 2，不相交。
- 宿主：并入既有日任务（ConfigCheck/GateFullTreeAudit）尾步，**零新计划任务**；报表落盘+.runtime/tmp 留样，前端接线不在本轮。**约 100-150 行**。

## 3 三态裁定汇总
| 矿 | 裁定 | 方案一句话 | 施工规模 |
|---|------|-----------|---------|
| ① 残差计时 | 施工 | env 守卫 finally 加一行 _record_phase("gates")，复用累加器 | ~3 行+1 测试（commit_queue_landing.py） |
| ② trigger 注入 | 施工（存量 0 违例可先落规则） | _validate_files_trigger 插 L219 try 块走 #351 fail-closed 既有通道；死触发/超宽走 warn+audit | ~15-20 行+测试（gate_auto_registrar.py） |
| ③ 预检缓存 | 施工（一期内存） | blob sha 内容寻址 memo 挂 _head_registry_yaml_data 单咽喉，ls-tree 顺带取 sha | ~15-20 行（commit_preflight.py）；实测 6.5s→<0.1s/件 |
| ④ schtasks 对账 | 施工（挂期：宿主任务归属待 Owner） | 只读生成器+register 脚本导出期望清单+三色规则；并既有日任务零新计划任务 | ~100-150 行新脚本；今日实测已 5 红 1 黄+4 声明漂移 |

## 4 长尾清单
- ProcessReaper=1 退出码非零（宪法 RULE-GUARDIAN 承重件）——建议立即人工核查，不等对账件落地。
- 计划任务命名两制（`-` vs `_`）漂移；4 个 register 脚本声明但任务不存在（BudgetReport/MetaqAuditReconcile/ModelExam/ModelIntelScan）——期望清单导出器应同时报双向漂移。
- files_trigger 子串语义的误伤面（`secret` 命中 secretary 类路径）与零命中 6 条的语义定性（前向防御 vs 死触发），待 Owner 裁定后可升级为名册字段（如 content_trigger 注记）。
- claim/release 段仍未装相（矿①余量）；landing_phase_stats 消费方仍缺（qcure 簿矿脉 3 的后半）。
- 预检直连路径 42% 占比下，二期磁盘缓存的卫生归属（谁建谁清）未定。
- 对账件黄类"节奏陈旧"阈值（2×周期）需按各任务 cadence 分档，首轮上线可先只报红+漂移，避免黄类噪音淹没有效信号。
