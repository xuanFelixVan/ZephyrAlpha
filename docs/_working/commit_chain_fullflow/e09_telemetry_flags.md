---
created: 2026-09-30
ttl: task_bound
title: 提交链全流通·E9 遥测/旗标/缓存面
session: st-gate-rationalize-20260929
---

# E9 — 遥测 jsonl 族 / flags.yaml 旗标全景 / gate 缓存与预检 / S1 视图（挖矿册）

> 盘面时点：2026-09-30 06:20-06:45 实测（ls -la + 首行时间戳 + 写方源码锚）。
> 目录约定：`.runtime/audit/`=提交链主遥测区；`.runtime/gate_audit/`=gate/漂移细分区；
> 轮转设施=`zephyr.shared.io.audit_jsonl_writer`（50MB 阈值，`.1/.2` 移位保留，audit_jsonl_writer.py:59/65-78/107）。

## §0 自审闸

**【挖干】**。jsonl 族 18 册全部实测（盘面大小/首行起始日/写方 file:line/每笔行数/轮转态/整读消费者六列齐）；flags.yaml **19 键全键表实读当前盘面**（非凭记忆）；gate_cache_preflight 白名单 15 台+指纹键+TTL 实锚；S1 CommitTreeView 构造/审计/验收台账实锚。缺口=部分大文件精确行数未逐行 wc（2.1GB/50MB 级仅报盘面大小），消费方中"临时分析脚本（.runtime/tmp/csx_*）"不逐枚举——列 §4。

## §1 组件全清单

### 1.A jsonl 遥测族全清点（实测盘面）

| 册（路径） | 盘面大小 | 写方锚点 file:line | 每笔追加 | 轮转 | 整读消费者 |
|---|---|---|---|---|---|
| .runtime/audit/gate_execution_stats.jsonl | 5.0MB | commit_gate_registry.py:85-115（_stat_flush，每链 flush 一行：n_specs/failed/reused/ms/total_ms） | 1 行/次 gate 链 | **无**（裸 open "a"） | 挖矿临时脚本；usage_stats/standard_checkup（引用级） |
| .runtime/audit/precommit_channel_stats.jsonl | 48KB/187 行 | git_commit_gateway.py:1946-1962（A1 装表） | 1 行/次 pre-commit 通道（total_ms/fast_subset_ms/rc/infra_error） | 无 | **暂无固定报表**（deep_dive 临时脚本消费） |
| .runtime/audit/lock_wait_events.jsonl | 14KB/86 行 | git_commit_gateway.py:565-600（Rx-2 _append_lock_wait_event；env ZEPHYR_LOCK_WAIT_LEDGER 缺省 ON） | 1 行/次锁等待（lock_wait/lock_timeout） | 无 | 02_prescriptions.md Rx-2 定案（锁等待归因） |
| .runtime/audit/commit_block_events.jsonl | 993KB/2504 行 | git_commit_gateway.py:1930-1944（共用写入器）+1964-1994（blocked）+1996-2012（slow）；commit_preflight/session_worktree 亦写 | 1 行/次阻断或 >60s 慢提交（阈值化） | 无 | **每次阻断全读**：堵点横幅 gateway:783-787 p.read_text 整文件；commit_perf_report.py:93-116（整读后窗口过滤） |
| .runtime/gate_audit/worktree_status_snapshots.jsonl | 25.2MB | git_commit_gateway.py:2115-2150（经 append_audit_jsonl） | 1 行/笔成功提交 | **有**（50MB 阈值将首触）；史 bomb=449 万行（audit_jsonl_writer.py:29-32） | generate_dev_delivery_map.py |
| .runtime/gate_audit/derived_write_attribution.jsonl | 57KB | git_commit_gateway.py:257-294（record_derived_write，R-04） | 1 行/笔派生写入（files 数组内联） | 无 | lookup_derived_write_owners gateway:297-322（**每次查证整读**，CLAIM/FOREIGN-CHANGE 判定用） |
| landing_phase_stats.jsonl（**仅在 worktree lane**：.runtime/commit_queue/worktrees/w*/…） | lane 级 KB | commit_queue_landing.py:1360-1375（A2 装表：_PHASE_ACC/_PHASE_FILE） | 每件每相位 1 行（按工号 _worker_tag 归因） | 无 | csx 深挖脚本（八相位 accounted 账） |
| .runtime/audit/bottleneck_ledger.jsonl | **50.5MB** | scripts/commit_queue.py:2575/3076（slow_item 等）+ commit_belt_daemon.py:60（3 kind：registry_drift/landing_staleness/phantom_staging）+ reconcile_generators.py:113/310（卡死表）+ order_daemon | 1 行/堵点事件（阈值化只记异常） | **无** | belt_daemon 告警检查 **read_text 整读 50MB**（commit_belt_daemon.py:108 附近）；commit_queue status |
| .runtime/audit/hook_tracked_drift.jsonl | 2.2MB | git_commit_gateway.py:3089-3104（GATE-TRACKED-DRIFT，#55 族） | 1 行/次 tracked 漂移违规 | 无 | commit_perf_report.py:36+65-91（竞态窗口事件数/日判级） |
| .runtime/gate_audit/allow_overlap_usage.jsonl | 640KB | git_commit_gateway.py:820-855（O2/#ARCH-264） | 1 行/次 --allow-overlap 使用 | 无 | gateway:873 滚动读（热文件 24h≥5 次→hard block）；abuse monitor |
| .runtime/gate_audit/gateway_index_hygiene.jsonl | 46KB | git_commit_gateway.py:757-767/4511/4581（临时索引清扫/异常） | 1 行/次清扫事件 | 无 | generate_dev_delivery_map.py |
| .runtime/audit/preflight_events.jsonl | 1.26MB | commit_preflight.py:599/648-655（每轮 1 行 ts/session/event/gates/ms）+846（快败拦截才写） | 1 行/次预检 | 无 | qcure_offset_report.py / enqueue_preflight.py |
| **.runtime/audit/feature_flags.jsonl** | **2.1GB（全场最大炸弹）** | flags.py:223-242（_record_audit 裸 open "a"）+**flags.py:310（global_flag_registry=FlagRegistry(persist_audit=True)）** | 1 行/次 flag register/unregister/set | **无** | 无消费方（纯审计） |
| .runtime/audit/write_audit.jsonl（+.1/.2/.3 各 ~52MB） | 12MB×4 段 | write_audit_daemon.py:73/224（RDCW 热目录事件→五要素+三层归因） | 1 行/次热区写事件 | **有**（50MB 移位实证） | write_audit_daemon.py:338（**尾部读**，近 N 秒归因） |
| .runtime/audit/safe_write.jsonl | 39.7MB | file_utils.py:509（safe_write_text CAS 写审计，_SAFE_WRITE_AUDIT_REL :427） | 1 行/次热文件 CAS 写 | **无** | 无固定消费方 |
| .runtime/audit/worktree_drift_watchdog.jsonl | 10.7MB | worktree_drift_watchdog.py（看门狗扫描） | 1 行/次漂移条目 | 无 | commit_perf_report.py:37；coordination_state_board；dashboard services_registry |
| .runtime/git_performance_log.jsonl（根） | 466KB | git_performance_monitor_reconciler.py:97（PERF_LOG_SUBPATH，reconciler priority=870） | 1 行/次 git status 计时采样 | 无 | 同 reconciler 趋势检测（stale worktree 预警/退化趋势） |
| .runtime/commit_queue/main_workspace_sync.jsonl | KB 级 | commit_queue_landing.py:139（名册）+2280-2295（冲突跳过留痕） | 1 行/次收敛跳过 | 无 | 队列侧诊断 |

### 1.B flags.yaml 全键表（config/flags.yaml 实读当前盘面，19 键）

| 键 | 当前值 | 用途一句话（锚点=flags.yaml 行号） |
|---|---|---|
| metrics | enabled=true（subsystems system/pipeline/db/ai/telemetry 全 true） | 指标采集主开关（:16-24） |
| logs | enabled=true；structured=true；jsonl_export=false；trace_id_injection=true | 结构化日志主开关（:26-31） |
| traces | enabled=true；sampling_rate=0.10；w3c；beta | 分布式追踪 span_stub（:33-38） |
| ai_behavior | enabled=true；beta | AI 行为监控 event_sink（:40-43） |
| git_operations | enabled=true；**regen_scope=any_worktree**；**immutable_tree=true**（S1 已翻 ON） | 提交链操作旗组（:45-56） |
| archive | **enabled=false** | 遥测归档未实现占位（:58-63） |
| health | enabled=true；beta | module_health（:65-68） |
| alerts | enabled=true；auto_escalation=false | 告警基础评估（:70-73） |
| schema_validation | enabled=true；strict=false；dlq=false | YAML 加载校验（:75-79） |
| auto_bootstrap | enabled=true | 遥测 hooks monkey-patch 注入（:81-83） |
| red_blue_validator | enabled=true；auto_game_day=true；ai_attack_generation=true；tier_6_advanced=true；blind_test=false | 红蓝对抗主开关（:85-92） |
| commit_queue_serializer | **enabled=true**（2026-08-22 翻开，281b7f469）；gated_mvp | reconciler auto-commit 改道入队，dev 单写者（:94-97） |
| gate_result_cache | **enabled=true**；production（2026-09-12 转正） | P2⑧门禁结果持久缓存：白名单命中跳现算；回滚=OFF+删 .runtime/gate_cache/（:99-102） |
| gate_preflight | **enabled=true**；production（2026-09-12 转正） | P2⑦锁外预跑+锁内指纹 F′==F 采信；回滚=OFF（:104-107） |
| gate_precommit_run | **enabled=true**；production（#341 方案②） | 落地前 staged 面 run pre-commit（55 台补获执行权）；SKIP=gate-commit-gw/gate-worktree-required（:109-112） |
| commit_queue_interactive | **enabled=true**；production（2026-09-12 P0-1 批） | --enqueue 快照+LOCK_TIMEOUT 自动改道入队（:114-117） |
| commit_queue_c1_debounce | **enabled=true**；gated_mvp；env ZEPHYR_CQ_C1_DEBOUNCE 即时回退 | C1 同会话 <20min 短窗自动合批（:119-122） |
| integrity_baseline_mode | **enabled=true；mode=head**（[翻转 2026-09-30·Owner批] snapshot→head；实现+测试随 SW19 袋 228ce95188 落地，head_baseline12 19/19 绿；省 46.1s/件同步刷新） | GATE-RULES-INTEGRITY 基线真源=HEAD blob 派生（:124-128） |
| duckdb_runtime_gate | **enabled=true；mode=warn**；kill-switch=ZEPHYR_RUNTIME_GATE=0 | 裸 duckdb.connect 运行时拦截（放行+审计）（:130-135） |

### 1.C gate 缓存与预检设施

| 组件 | 功能 | 锚点 file:line | 触发时机 | 耗时账 | 自动化属性 |
|---|---|---|---|---|---|
| CONTENT_SCAN_CACHE_WHITELIST | 缓存准入白名单 **15 台**：实证复用面 10（ENCODING-SAFETY/DATETIME-NOW-FORBIDDEN/NO-DOMAIN-NAME-ZH-DIRECT-ACCESS/NO-BARE-SQL/NO-UPWARD-IMPORT/NO-IMPORT-SIDE-EFFECT/UNDEFINED-NAME/RELATIVE-PATH-LITERAL/UNSAFE-DICT-SPREAD/ASYNCIO-RUN-IN-CONTEXT）+实证耗时面 5（BLUEPRINT-HEADER 1781s/CH-BATCH-SIZE 872s/BLUEPRINT-FORMAT 725s/FILE-COPY 136s/NO-HARDCODED-URL 124s） | gate_cache_preflight.py:102-127 | 模块常量 | - | 白名单准入=禁拍脑袋（:57 注释） |
| GATE_INPUT_MANIFEST | 门级注册表输入清单（防篡改判失）；**当前空置**（top15 全纯 staged 扫描器） | gate_cache_preflight.py:131-136 | 准入注册表读取类门前必填 | - | 机械前置 |
| 缓存键+TTL | key=gate_id×own_scope×write-tree 树指纹×HEAD_sha×flags mtime（任一变全失效）+TTL 600s；只缓存 passed=True（fail-open 不放大）；目录 .runtime/gate_cache/（盘面实证 sha 名 json 存量） | gate_cache_preflight.py:138-139/186-204/303-360（lookup 335/store 348） | 锁外预跑/锁内采信 | 命中≈0ms vs 原算 124-1781s/台 | flag gate_result_cache 门控 |
| commit_preflight 主预检 | 锁外对 --files 试跑 PREFLIGHT_GATES 白名单子集+内联适配层；快败一次给全 | commit_preflight.py:28-66/109/166 | git_commit.py 拿锁前 | 每轮 1 行 preflight_events（实测 1.26MB/9 天） | flag gate_preflight 门控 |
| S1 CommitTreeView（own-tree 视图） | 门禁链输入源改读不可变双树（HEAD^=父提交 base + git write-tree=index 冻结树）；fail-safe 回退本体 gateway；树内外来 staged 恒 0 指标（>0 warn+审计 own_tree_scope_foreign_staged.jsonl） | git_commit_gateway.py:3108-3134（构造）+3152-3175（foreign 审计）；实现=commit_gates/_tree_view.py | flag git_operations.immutable_tree=true 时每次 gate 链（:3202 接线点） | **验收 7.1×**：30 笔 own 10,934ms vs shared 77,853ms | flag 门控（Owner 已翻 ON） |
| S1 验收台账 | 6000 verdict（30 commits×100 台×2 口径）零漂移：verdict/hits/detail 三列 100/100 diverged=0，verdict_drifts_with_index_size=False | docs/_working/commit_speedup_campaign/90_verification/s1_acceptance_20260929.md:17-33/51-52 | 发布前绊线（已清零） | 重放实测 2860.8s | 台账 |

## §2 六向台账（按组件群）

**① 遥测写入面**：上游=gate 链/预检通道/锁/落地/watchdog/CAS 写；下游=E10 报表面（perf_report/横幅/belt 告警）；输入=运行时事件；输出=jsonl 追加行；真源锚=§1.A 表逐行；耗时账=写失败静默（可观测性永不阻断主链，gateway:1933/1952 等）。
**② 旗标面**：上游=config/flags.yaml（YAML 真源，宪法 RULE-SSOT）；下游=gate_cache_preflight.flag_enabled（:142-160）+各接线点；翻转纪律=出厂翻转属 Owner 门位（high tier，宪法 §5.2）；真源锚=§1.B 表。
**③ 缓存面**：上游=write-tree/HEAD/flags mtime 三锚；下游=check_all 采信路径（gateway:2756 preflight_results）；失效=任一锚变+TTL 10min+仅 passed=True；真源锚=.runtime/gate_cache/+gate_cache_preflight.py。
**④ S1 视图**：上游=immutable_tree flag；下游=100 台门禁 read 面；输入=HEAD 树+index 树；输出=CommitTreeView 契约（提交前仓库态=父提交）；真源锚=_tree_view.py+验收台账。

## §3 缺陷与已修

1. **史 bomb 族**（audit_jsonl_writer.py:26-32 实录）：ops_guard_delete.jsonl 42h 膨胀 3.7GB（333 万条）；worktree_status_snapshots.jsonl 449 万行；post_claim_modifications.jsonl 175 万行。已修：append_audit_jsonl 统一写入器（50MB 轮转、移位保留、fail-open，audit_jsonl_writer.py:36-44）。
2. **#55 族**：flags.py 门禁运行期向 tracked feature_flags.jsonl 写审计→pre-commit 结构性误报。已修：审计迁出 tracked 区（flags.py:174-176，gateway:3068-3074 报警面）。
3. **【现存·本次挖出】feature_flags.jsonl 2.1GB 无轮转**：flags.py:310 全局注册表 persist_audit=True，register/set 每次追加裸 open "a"（:239），零轮转零采样零消费——历史上最大单体（全场 .runtime 的 20 倍）。待办见 §4.1。
4. **【现存】整读消费者随册膨胀**：堵点横幅每次阻断整读 commit_block_events（gateway:783，993KB 尚可）；belt_daemon 告警检查整读 bottleneck_ledger **50.5MB**（commit_belt_daemon.py:108 附近）——后者已是真实税。
5. **【现存】五册无轮转无上限**：gate_execution_stats 5.0MB、safe_write 39.7MB、bottleneck_ledger 50.5MB、hook_tracked_drift 2.2MB、feature_flags 2.1GB——均绕过 audit_jsonl_writer 裸写。
6. **【现存】precommit_channel_stats 零固定消费**：A1 装表后无报表接入（187 行沉睡账）。

## §4 待办移交

1. feature_flags.jsonl 2.1GB 处置：改走 append_audit_jsonl（或加采样/关 persist_audit 中无消费 action）——净零内收判据下建议"退役或轮转"二选一，Owner 门位（涉及全局 flag 注册表行为）。
2. bottleneck_ledger 告警读改尾部读（对齐 write_audit_daemon.py:338 先例）：50.5MB 整读×每次告警检查。
3. gate_execution_stats/safe_write/bottleneck_ledger 三册迁 audit_jsonl_writer（机械改写，风险低）。
4. precommit_channel_stats 接入 commit_perf_report（补第二本耗时账的固定消费面）。
5. 缓存白名单扩容判据材料已在锚点（24h total_ms top 注释），扩容须先填 GATE_INPUT_MANIFEST（gate_cache_preflight.py:131-136 机械前置）。
6. worktree_status_snapshots 轮转首触后验证 `.1` 段生成与 generate_dev_delivery_map 消费兼容性。
7. seed 勘误两处：integrity head 翻转实施 commit=**228ce95188**（flags.yaml:126，非 d2446aff——后者只是触发最后一条 reconcile worker 的普通提交）；immutable_tree=ON 当前盘面=true（flags.yaml:52）。
