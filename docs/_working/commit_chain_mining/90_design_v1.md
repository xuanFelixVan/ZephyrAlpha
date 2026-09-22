---
ttl: task_bound
---

# 设计 v1.0——提交链六项改进施工图（自审闸放行版）

> 依据：11 环节挖矿文档+301 死信语料。自审闸三态已逐项裁定（各环节文档 G 节）；本文只收"施工"项。全部改动向后兼容（flag/白名单/增量输出），不 kill 常驻守护（epoch re-exec 换血），队列零依赖不变量不碰。

## D1 入队面预检扩容（=Owner R1；环节1 E1/E3/E6+环节5 F1）

文件：`src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py`（主）+ 纯读 gate 模块。
- PREFLIGHT_GATES 增 6 道（逐 gate 输入面审计注记随行）：`RULING-REFERENCE`/`ARCH-REFERENCE`/`CREATE-GUARD`/`NO-BARE-SQL`/`EXEMPT-ZONE-FM`/`TRANSLATION-COVERAGE`。
- 共享内联助手 `_inline_added_lines(files, project_root)`：磁盘 vs HEAD blob 的 difflib 增行提取（零子进程、零暂存依赖；HEAD=git show 批量）。
- CREATE-GUARD 内联化：新文件判定=`git ls-tree -r HEAD --name-only` 批量集（1 子进程）∩ 非测试豁免；token=registry 精确路径比对（复用 create_guard 内部函数）；14 字段头=首 30 行文本。
- NO-BARE-SQL：复用 bare_sql_gate 的行级正则+docstring 常量豁免，喂内联增行。
- 失败反馈：一过式清单+逃生旗指引（register_creation_token/add_module_translation/裁定补登文案），exit 8（既有语义）。
- requeue 通道同享：requeue CLI 调 run_preflight（环节1 E3）。
- 语义红线：预检只快败不豁免，锁内权威链照跑（模块 INVARIANTS 原文）。

## D2 大批硬顶（=Owner R2；SC-3）

文件：`scripts/git_commit.py`（_enqueue_mode）+`scripts/commit_queue.py`（enqueue_item+EnqueueOptions）。
- 交互车道 >40 文件→拒绝+拆批指引；逃生旗 `--allow-oversize-batch`（argparse+EnqueueOptions.allow_oversize_batch→meta_extra 留痕）。
- enqueue_item 兜底同判（护 CLI/requeue 通道）；machine 车道豁免。

## D3 两段式 precommit 通道（=Owner R3；环节5 F2）

文件：`src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`（_run_precommit_channel）。
- 全通道前增 Phase-A：确定性子集 7 hooks（check-merge-conflict-marker/detect-private-key-local/gate-algo-flow-marker/gate-any-abuse/gate-naming/gate-encoding-safety/ruff）逐台 `pre-commit run <id> --files`，首败即断进既有归因段（复用同临时索引）；全过→Phase-B 全通道照旧（保 own/foreign 归因）。
- 禁 config 顶部 fail_fast（foreign 掩蔽 own=误放行——环节5 F6 封矿项）。
- 子集常量+注释锚；不改 55 hooks 的 config 顺序（time=Σ全部，顺序无收益）。

## D4 租约释放唤醒+守护换血闭环（=Owner R4；环节2 E2+环节3 E1/E3）

文件：`src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py`。
- watchdog 增观察队列根（recursive=False）：serializer.lease deleted/created→poke（封漏唤醒窄缝）；DAEMON 头注 [MODIFY-GUARD] 同步登记。
- epoch 第三子树：scripts/commit_queue.py 纳入纪元合成（改判据必换血）。
- LeaseUnavailable 静默→补 debug 日志（可观测）。

## D5 status 增强（=Owner R5；环节7 C1-C3）

文件：`scripts/commit_queue.py`（queue_status）。
- 增量输出三块：`lease{holder_pid,alive,acquired_age_s,renewed_age_s,over_ttl,state}`；`head{qid,session_id,files,created_at,waiting_s}`；`--session` 时 items 增 `position_ahead`。`daemon{online}` 键（belt_daemon.lock 探测）。纯增量向后兼容。

## D6 死信升级告警（=Owner R6；环节6 E1-E5）

文件：`docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml`（safe_write）+`scripts/commit_queue.py`。
- 注册表新增 THD-ALERT-005（单日死信增量≥50）/006（单会话连败≥10）/007（升级冷却 21600s），结构照抄 003。
- drain 收尾（emit_dead_backlog_alert 旁）增 `_check_dead_burst`：当日新增+当日单会话链长，超阈→堵点本 alert 行+task_board 打标；日期键冷却（每类型每天 1 声）。
- env 标记补盲：+=「拒绝访问」「WinError 5」「WinError 206」「文件名或扩展名太长」。
- queue_health 增 max_session_death_chain/per_session_top 两键。

## D7 快赢捆绑（环节2/9 【快】项）

- CQ:1132 消费 renew() 返回值（False→CRITICAL log+本轮立即终止，项留 processing 等孤儿回收）。
- 单项墙钟挂账：drain 循环记单项耗时，>300s 写 bottleneck_ledger（kind=slow_item）。
- _sync_worktree reset 短路（HEAD==dev 且 porcelain 干净→跳过 reset --hard）。
- requeue 透明化：快照=当前工作区时打显式 notice+`--from-bag` 原袋选项（默认行为不变——修-重试工作流依赖现语义，SC-7）。
- enqueue_item 分步计时（blob/compact/seq ms→审计 jsonl）。
- git_commit.py 头部 [TESTS] 指针修正；process_reaper_keep.txt 重复行去重（若在 git 内）。
- 挂起登记（不施工）：k=4 通道池（S18-R3 Owner）、字典序 FIFO→created_at（动 66号不变量须 Owner）、blobs GC（Owner）、TRANSLATION-COVERAGE 预检化（视 D1 后死信率复测）、收敛批量化/reset 短路后续、reconciler worktree 禁 auto-commit、gate_cache_preflight 启用、own_scope 五台补登记（机生通道）。

## 测试计划（两轮零判据）

- 单测：test_commit_preflight.py（6 新 gate 内联模式×正反例）；test_commit_queue.py（cap/逃生旗/status 新键/dead_burst/env 标记/renew 失败终止/墙钟挂账/requeue notice）；test_commit_belt_daemon.py（lease 观察 poke/epoch 第三子树）；GW 通道两段式（既有通道测试文件扩 Phase-A 正反例）。
- 集成：既有 test_commit_queue_integration.py 全量回归（隔离 ZEPHYR_COMMIT_QUEUE_DIR）。
- 红蓝：独立红队子代理对抗（预检误杀面/归因语义/租约竞态/status 输出解析），两轮零。

## 落地批次（全部走队列——改善对象自己验证自己）

B-a 卫生批：两件孤儿 diff 代偿（SC-2：.pre-commit-config.yaml 注记行+alert 注册表路径修正，归因原会话）。
B-b 代码批：D1/D2/D3/D4/D5/D6/D7+全部测试。
B-c 文档批：本战役 12 份文档+capability_canonical token 登记。
（B-b 内部按 gate 友好度拆 2-3 个队列项，单项 ≤40 文件——自食 D2 狗粮）
