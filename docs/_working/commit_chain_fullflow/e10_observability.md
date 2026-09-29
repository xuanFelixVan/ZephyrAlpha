---
created: 2026-09-30
ttl: task_bound
title: 提交链全流通·E10 观测与验证面
session: st-gate-rationalize-20260929
---

# E10 — 观测与验证面（挖矿册）

> 环节定义：不参与提交判定、只为"耗时可归因、堵点可溯源、修复可验证"存在的面——
> 三本耗时账、锁等待账、落地相位账、堵点横幅（推模式）、commit_perf_report（拉模式）、
> reconcile 观测产物、红蓝对抗套件、循环检查 SOP。
> 数据真源明细（各册写方/轮转/消费者六列）已归 **e09_telemetry_flags.md §1.A**，本册只记观测语义与验证闭环。

## §0 自审闸

**【挖干】**。三本耗时账起始日全部以账本首行时间戳实测核实（9/15、9/24、9/13，非凭记忆）；横幅/报表实现逐行有锚；红蓝套件两层（pkg14 七场景+战役回归钉）+史账（S1 验收 6000 verdict 零漂移）实锚；循环检查 SOP 有 Owner 晨令原文锚。缺口=lock_wait 账"100% 覆盖提交尝试"的 R2 定案判据未复核（86 行样本量待对提交总数），列 §4。

## §1 组件全清单

| 组件 | 功能 | 锚点 file:line | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|---|
| **耗时账① gate_execution_stats.jsonl** | 逐 gate 计时/成败/复用态，每链 flush 一行（n_specs/failed/reused/ms/total_ms）；宪法 §4.2 触发率退役审计的数据燃料 | 写方 commit_gate_registry.py:76-115（P1-E G10，st-commitspeed-20260916） | 每次 gate 链执行完 | **9/15 起**（首行 2026-09-15T18:19Z 实测）；现 5.0MB | 自动（fail-safe 静默） |
| **耗时账② precommit_channel_stats.jsonl** | pre-commit 通道分段计时（total_ms/fast_subset_ms/rc/skipped/infra_error）；独立成册因 commit_block_events 是"只记异常"阈值化册 | 写方 git_commit_gateway.py:1946-1962（A1 装表） | 每次通道执行 | **9/24 起**（首行 2026-09-24T14:26Z 实测）；187 行 | 自动 |
| **耗时账③ commit_block_events.jsonl** | 阈值化堵点账：仅 gate 链**阻断**（commit_blocked，gate_chain_ms 白跑耗时）或成功但墙钟 >60s（commit_slow，total_ms）才写一行；gate_id 判定=status 映射>message 正则（UNKNOWN×6 治本） | git_commit_gateway.py:1930-1944/1964-1994/1996-2012；阈值 _SLOW_COMMIT_THRESHOLD_S=60.0（:347）；触发点 ：2760/2812（阻断）/2818-2819（慢） | 阻断或慢提交 | **9/13 起**（首行 2026-09-13T11:14Z 实测，D5）；2504 行 | 自动 |
| **0ms 黑洞史（账③已知口径坑）** | GATE-PRECOMMIT-RUN 阻断行 gate_chain_ms=0——成本全记在 precommit 通道（账②），跨册加总会双漏；另有 gate_id="-" ×67 详情缺失 | deep_dive_r1.md:75-78（C 节近窗 TOP） | 历史数据 | 白烧链全史 2574min/近窗 723min | 已识别未修（埋点缺口） |
| **GAP-1 成功提交采样** | 成功且 <60s 零留痕=分位盲区→sha 尾 hex ≥0xE 确定性采样 12.5% | git_commit_gateway.py:2820-2834 | 成功提交 | 采样行入账③同册 | 自动 |
| **锁等待账 lock_wait_events.jsonl** | Rx-2（st-finaldel-crx2-20260929）：锁轮询等待落账（lock_wait/lock_timeout，waited_ms/holder/timeout 六字段）；R2 定案判据=100% 覆盖提交尝试；env ZEPHYR_LOCK_WAIT_LEDGER 缺省 ON | git_commit_gateway.py:560-600（写入器）；lock_timeout 路径 ：2767-2778 | 每次提交尝试拿锁 | 9/29 起；86 行实测 | 自动（env 可一键回退） |
| **落地相位账 landing_phase_stats.jsonl** | A2 装表：单件落地八相位分段计时，按 _worker_tag 归因到工号（"三路工熄火 9 小时看不见"的补课） | commit_queue_landing.py:1360-1375 | 每件每相位 | 落地窗内（lane 册）；H5 前主体 597-2800s/件 | 自动 |
| **堵点横幅 _print_bottleneck_banner** | D5 推模式：近 24h 账③有堵点→提交输出醒目横幅（TOP3 gate×次数+P50）+"专人专事"协议指引（施工 AI 不修，维护班清账）；修复后 24h 滚动窗自动消失 | git_commit_gateway.py:769-815；触发点 ：2761/2813（阻断时 context=post_commit） | 每次阻断提交 | 整读账③（993KB，e09 §3.4） | 自动 |
| **commit_perf_report.py（24h 堵点报表）** | 维护班入口：四数据源（git log 提交构成/hook_tracked_drift 竞态/worktree_drift_watchdog 漂移/账③ block_events）→四维判级（正式占比≥70%/机器伴生≤30%/竞态≤4 日绿/>50 红/watchdog 条数）+aggregate_verdict（任一红→红；B2 治本：旧公式竞态 211/日仍判绿） | scripts/governance/commit_perf_report.py:6-22（真源/指标/用法）/50-116（取数）/118-130（折算防小窗放大） | 手动/横幅指引（--hours 24） | 整读两册+git log | 手动触发报表 |
| **reconcile 观测产物** | status 文件（pending→running→done/failed+reconcilers_total/warn/auto_committed+errors 全文）；worker 日志落盘（S3 观测层：wipe 事故 4 worker 启动即死无日志的治本）；DB reconcile_execution_log | reconcile_runner.py:127/640-667（inflight 计数）/816-823（log 落盘）；reconcile_worker.py:82-130；盘面 .runtime/reconcile_reports/=779 文件/89 status | 每笔异步对账 | 单 worker 实测 459s/22 台（e08 §1） | 自动 |
| **abuse/守卫观测产物** | commit_gateway_abuse_monitor（五维滥用 warn-only，priority=875）+post_commit_guard 快照 json+worktree_status_snapshots | reconciliation_registry 注册 gateway:1761-1763；.runtime/reconcile_reports/post_commit_guard_*.json 盘面实证 | post-commit | - | 自动 |
| **红蓝套件·包14** | 7 场景极限对抗：s1_worker_revival/s2_dual_writer/s3_fault_injection/s4_forged_marker/s5_cache_poison（缓存投毒）/s6_starvation（饿死）/s7_cross_lane；红方=产品文件字节副本手术+importlib 独立装载（原文件 sha256 不动），蓝方=现行码沙盒跑，全 tmp 隔离 | tests/governance/red_blue_pkg14/（_common.py:19-30 沙盒三件套+INVARIANTS :9-13）；报告真源 docs/_working/commit_speedup_campaign/90_verification/red_blue_pkg14_report.md（_common.py:3 BLUEPRINT 锚） | 手动 pytest（改链必跑） | 全 tmp，秒-分钟级/场景 | 手动套件 |
| **红蓝套件·战役回归钉** | st-commitchain-20260922 六项改进回归：R2 大批硬顶/R5 status 三块/D6 死信告警/D7 renew 终止+requeue/D1 预检内联/D4 epoch/D3 快败子集 | tests/governance/test_commit_chain_campaign_20260922.py:8（INVARIANTS 全清单）/22 | 手动 pytest | tmp_path 隔离 | 手动套件 |
| **红蓝史账·S1 验收** | 6000 verdict（30 commits×100 台×own_tree/shared_index_sim 双口径）逐台全等零漂移+7.1× 读面收益——"证据=全量落盘，非全绿式虚报" | docs/_working/commit_speedup_campaign/90_verification/s1_acceptance_20260929.md:17-33/51-52 | 发布绊线（已清零 2026-09-29） | 重放 2860.8s | 台账 |
| **红蓝史账·缓存转正** | gate_result_cache/gate_preflight 转正判据：7 笔实弹零异常+红蓝#2 投毒/失效攻击 4/4 全防+reconciler 永久对账兜底 | config/flags.yaml:101/106（转正记录） | 2026-09-12 结项 | - | flag 描述内史账 |
| **循环检查 SOP** | Owner 晨令（2026-09-30）：挖矿→封矿→施工→**循环检查×2 零**→红蓝对抗→全绿交付；连续两轮检查零问题=过；红线四条（不抹他会话成果/已完成的交叉验证不重做/净零内收/无法裁定登记跳过） | docs/_working/commit_chain_fullflow/00_skeleton.md:10（晨令原文）/37（D 段）/41-44（红线） | 每轮施工完成后 | - | 流程 SOP |
| **git 性能监控 reconciler** | git status 计时持续采样→.runtime/git_performance_log.jsonl+stale worktree 累积预警+退化趋势检测（priority=870 warn-only） | git_performance_monitor_reconciler.py:22/47/97；注册 gateway:1758-1760 | post-commit 事件触发 | 每次采样 1 行 | 自动 |

## §2 六向台账（按组件群）

**① 三本耗时账（ms 级逐台）**：上游=gate 链/precommit 通道/锁与提交全流程；下游=commit_perf_report、横幅、deep_dive 类归因分析；输入=每次链执行/通道运行/异常事件；输出=jsonl 追加；真源锚=e09 §1.A 行号列；耗时账=9/15·9/24·9/13 三起点实测（本册 §1）。三账互补：账①=锁内逐 gate ms、账②=precommit 通道分段、账③=全流程墙钟与白跑（慢而未阻）。
**② 推模式（横幅）**：上游=账③ 24h 窗；下游=每个走提交通道的 AI 会话（必然看见）；真源锚=gateway:769-815；零事件零输出。
**③ 拉模式（报表）**：上游=四数据源；下游=维护班清账流程（专人专事）；真源锚=commit_perf_report.py:6-22；判级=四维聚合任一红即红。
**④ 验证面（红蓝+循环检查）**：上游=施工完成/修复落地；下游=全绿交付门位；输入=tmp 沙盒+字节副本手术；输出=verdict 台账；真源锚=pkg14/_common.py+验收台账+skeleton 晨令。
**⑤ reconcile 观测产物**：上游=异步对账 worker；下游=RECONCILER-HEALTH 探针/人工巡检；真源锚=.runtime/reconcile_reports/+.runtime/logs/reconcile_worker_*.log。

## §3 缺陷与已修

1. **UNKNOWN×6 归因失效**（2026-09-13）：纯正则提取把 FOREIGN_CHANGE/COMMIT_SCOPE 等专用 status 全吞成 UNKNOWN（近 24h 6/25 失真）。已修：status 映射优先+正则兜底（git_commit_gateway.py:1972-1984）。
2. **B2 判级失真**：旧公式只看正式占比/机器伴生比，竞态 211/日仍判绿。已修：四维判级+任一红→红（commit_perf_report.py:16-19/125-130）。
3. **小窗放大误判**：48h 窗 211 事件直对标 ≤4/日阈值漏判。已修：_per_day 折算（commit_perf_report.py:118-130）。
4. **wipe 事故观测盲**（2026-08-14）：4 worker 启动即死无日志。已修：stdio 从 DEVNULL 改落盘 reconcile_worker_<sha>.log（reconcile_runner.py:816-823）。
5. **0ms 黑洞+“-”埋点缺口（未修）**：账③ GATE-PRECOMMIT-RUN 行 gate_chain_ms=0（成本在账②，跨册不重不漏但单册读会低估）；gate_id="-" ×67 缺 detail（deep_dive_r1.md:76/172 附.1）。
6. **账②零固定消费（未修）**：precommit_channel_stats 装表后无报表接入，187 行沉睡（e09 §3.6）。
7. **横幅/报表整读税（未修，随册增长）**：每次阻断整读账③、报表整读账③+hook_tracked_drift+watchdog 三册（当前 993KB/2.2MB/10.7MB，尚可；增长趋势见 e09 §4.3）。

## §4 待办移交

1. "-" 埋点补全：67 次阻断事件缺 gate_id/detail（deep_dive_r1.md:172 附.1）——补 _audit_commit_block_event 对无门号 status 的归因位。
2. precommit_channel_stats 接入 commit_perf_report（第三数据源组），补 9/24 后 precommit 通道趋势的固定报表。
3. Rx-2 R2 定案复核：lock_wait 账 86 行 vs 同窗提交尝试总数，验证"100% 覆盖"判据后出锁等待归因终账（与 E8 §4.1 插桩联动）。
4. residual 123s/笔 定案（deep_dive_r1.md:172 附.2）：落地侧逐相位插桩（全局锁等待单独计时）——定案后横幅/报表可加"锁等待"维。
5. 红蓝 pkg14 场景扩展建议：本次挖出的 feature_flags.jsonl 2.1GB（e09 §3.3）与整读税可作为新红方攻击面（膨胀攻击/告警风暴）。
6. 循环检查×2 零执行时建议带上本三册 §3"现存未修"清单作为核对基线（0ms 黑洞、整读税、沉睡账②）。
