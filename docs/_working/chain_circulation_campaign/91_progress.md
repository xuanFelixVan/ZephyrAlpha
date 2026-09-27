---
ttl: task_bound
---

# 91_progress — 业务链流通战役落地台账（哈希账）

> 各车道逐批登记：qid/commit 哈希/内容摘要/归属核验。追加式；哈希以 `git log -1 --name-only` 核归属后填写。

## EC3 灌水运行体检（st-ec3-water）

| # | qid | commit | 内容 | 归属核验 |
|---|---|---|---|---|
| 1 | q-20260927-st-ec3-water-0001 | `514698ba62` | S2 终章=tilib 夜回填任务重指向落地（scripts/register_tilib_backfill_task.ps1 新建+实跑生效：ACTION→HEAD tracked ps1 #399 分片件，NextRun 09-28 02:30 保位）+ 22 行健康表全行重探台账 ec3_water_health_ledger.md（现态/证据/处置/移交）+ CH 灌水实证 | `git log -1 --name-only`=恰好 2 文件 ✓（registry delta 零随批=会被队列去重，token 两件已由 92b3256fd0/edca5445b7 先行入 HEAD，53728/53748 行在案） |

### 随批入册（他册承载，此处留索引）
- creation_token ×2（chain-circulation-ec3-water-health-ledger / tilib-night-backfill-register-script）→ capability_canonical_file_registry.yaml（append-only 共册，FMS 总筹 92b3256fd0 批吸收落账，本会话 acquire 后队列去重零冲突）。
- `data/runtime/qmt_terminal_path.txt` 0x08 退格修复（QMTWatchdog SKIP 根因，09-15 起损坏）——runtime 配件不入 git，看门狗同款读路径 Test-Path=True 终验在台账 §四。

### 未落地依赖（诚实注记）
- 无。本车道袋全落地。

## 移交项速览（详见 ec3_water_health_ledger.md §二/§四）
1. ZephyrAlpha_EvaporationBlackbox 实例挂死 09-25 23:26 起（blackbox.jsonl 停更 27h+，IgnoreNew 拒补射）——禁 kill 只记录；处置=Stop-ScheduledTask 后 PT5M 自愈，归属 LANE-EV/AI 层。**09-27 03:2x 本会话亲历 capability 册被并发 lane 会话工作树快照压盘（我的 2 条 token 行一度被抹，幂等重登记+FMS 总筹吸收批落账）——黑匣子彼时盲态，未留 Minute 级现场，佐证其激活紧迫性。**
2. ollama serve：进程经在册任务拉起（pid 31688）但 API 40s 无响应——禁 kill 不再动，Owner/ML 面。
3. NightlySentiment 双源（计划任务+schedule.yaml 槽）——Owner 定单源。
4. kline_sector_intraday 断供起点 09-23（tdx provider 全服务器取 K 线失败；TCP 取证 3/6 现存可达）——数据链 09-28 盘中复测。
5. 空表三件：edb_data（FRED fetch 恒 0 行）/ etf_benchmark（catchup 日日补跑失败；已有 P3 批 b9c2a69005 修 date_col 声明——并行处置中）/ account_nav_daily（57 号文 GAP）。
6. tilib exit 0 终验：09-28 02:30 后看 LastTaskResult（晨检一行流）。

## EC1 股权穿透接线（st-ec1-equity）

| # | qid | commit | 内容 | 归属核验 |
|---|---|---|---|---|
| 1 | 直连正门（allow-overlap 通道，前置死信 -0001..-0004 payload 已覆盖=留档作废） | `9fa01551f0` | entity_graph 六表查询模块 chainmap_equity_graph.py（现行版本聚合+3跳穿透 pg_function 优先/42883 降级 WITH RECURSIVE+ACC-F-CHAINMAP-EQUITY-BADGE 契约兼容件+独立冒烟 CLI+ALGO_FLOW 外置块）+ tests/frontend/test_chainmap_equity_graph.py 15 例全绿 + ec1_equity_wire_ledger.md 台账（含 R1-R7 销账/实弹证据/接线补丁）+ algo_flow yaml | `git log -1 --name-only`=恰 6 文件 ✓ 零搭便车 |
| 2 | token/翻译共册随批 | 同袋 `9fa01551f0` | capability 册 +80 行（本车道 3 token + 他会话在途 15 条随批披露+metaq 16 条治伤补回）；翻译册 +312 行（本车道 1 条 + 他会话在途 38 条随批披露）——均 HEAD 纯追加零删行机检证明 | 归属核验 ✓ |

### 端点切换登记跳过（R3，诚实口径）
- api_server.py 共享热文件存在 1079 行非本会话外来未提交改动（作者不可归因，无人 claim），按车道纪律只在独立模块实现+测试；**接线补丁（2 处小改）已备好在台账 §3**，api_server 空闲后施用即完成六表切换，前端 js 零改动。
- 实弹验收已用"直接调函数"（切换后同代码路径）完成：600566/600927 三跳穿透非空、20 边对源 20/20 PASS。

### 未落地依赖（诚实注记）
- 无。本车道袋全落地。

## EC2 P0 断链处置（st-ec2-p0）

| # | qid | commit | 内容 | 归属核验 |
|---|-----|--------|------|----------|
| 1 | q-20260927-st-ec2-p0-0001 | `3522eb8c6d`（chief 双归属袋吸收）+0009 残件 | F34 知识汇聚落地（聚合器+DDL+16 测+TDM module_ref 回填，死会话 st-chief4x-know 遗产核验落地；主袋与 chief 3522eb8c6d 内容重合已防回退弃用）+sim_observe_daily 回归补落（09-24 契约在 tests 钉死、执行体快照回退丢失）+L9 钩子测试隔离（残件 q-0009） | `git log -1 --name-only` 3522eb8c6d=8 文件恰含五件+chief 增强版 ✓；0009 残件落地后回填 |
| 2 | q-20260927-st-ec2-p0-0002→（v9袋=q-0021，内容门全过余 landing 环境死因重投链） | 落地后回填（v9=最终内容：v2 尺+combo 传动+ALGO_FLOW 锚+F821 治本）| F74 堵点1+2：combo v2 frozen 尺（STD-SIM-ACCESS-002/裁定#337，dsr 0.5+ρ̄+换手腿+suspect 注记）+combo 事件入口（advisory due 执行体尾传动渲染） | 待 drain 后核 |
| 3 | q-20260927-st-ec2-p0-0003（v2袋=0013） | 落地后回填（v2 修 SSOT-REDEFINITION+NO-BARE-SQL）| FL1/FL2 回灌边消费端 MOD-BT-223 feedback_prior（E6/E9 digest→E2 先验注记+E1 方向面）+两消费端接线+翻译/token 共册随批 | 待 drain 后核 |
| 4 | q-20260927-st-ec2-p0-0004（v2袋=4ce7dd9ced） | F20 事件沿落地 | F20 车道G 事件沿：intel_harvester 落新班 fire-and-forget 触发 lane_g 消化（零 cron 事件沿） | 待 drain 后核 |

### 九项销账（证据全录=ec2_p0_breaks_ledger.md）
F34 本役落地｜F74 本役修（堵点3 Owner/堵点4 自然时间）｜F20 本役修（胃停摆属 F96）｜F26/F04 **他线已落地**（88f62e893e，本役让位+重复件内收全撤净）｜
st-chief4x-promo2-20260927（MOD-BT-225 活跃施工，本役重复件已按内收全撤净）｜F62 **Owner 门位登记跳过**
（broker_ack 人工报送前置，99_skipped SKIP-1）｜F82 已销账（判据"保持不存在"成立=EC3 row11 同判）｜
F04 他线已落地（88f62e893e，本役让位）｜FL1/FL2 本役修。超计划：sim_observe_daily 接线回归修复
（HEAD 即红 5 测，快照回退事故丢件）。测试累计：126 绿（七套件）+54 绿（回归复验）。

## 终局段（总筹 st-chief5-20260927，2026-09-27 08:5x）

### 总筹亲施袋
| 袋 | 内容 | 哈希 |
|---|---|---|
| 接管袋 | 战役宪章+token 同袋 | 401203858d |
| tests/frontend 治本袋 | conftest 收集死锁防+冒烟事件行装置适配 | 7530bd74 |
| api_server 三合一袋 | SQL 集中化 43 块（§5.160.2+ARCH-CH-024，TableRegistry 真源 8 常量）+孤儿工作采纳 1079 行（st-qmine-20260925/st-ailayer-final-20260924 遗产，三代投死于 PERM-TRIGGER）+EC1 端点切换收官（_cm_equity 委托/簇徽章六表/_SQL_CM_EQ_AGG 删/entity_type 契约） | 8f03ef44bf |
| 排班哨兵追认袋 | 22/31 基线追认+历史回归测试合成化 | d623e5ac50 |

### EC1 股权穿透链终态（本役核心命题）
底座（六表 150 万边，c007caac86）→ 查询模块（9fa01551f0）→ API 端点切换（8f03ef44bf）→ **前端全链真源切换完成**。
实弹验收：/api/chainmap-company?symbol=600566 → source=entity_graph n_held=59；/api/chainmap-cluster?cid=C14 → 节点 equity.out=24 明细带 stake_pct；红队三探测（非法 symbol/空簇/越界参）全部优雅降级；600927 复跑 n_held=34。ig_equity_edge 退役=Owner 门位（99_skipped 登记）。

### 红蓝两轮零（本线范围）
- 第 1 轮：tests/frontend 556 绿（3 败=排班哨兵待追认）+E2E 端点实弹 200×2+红队探测降级面全过。
- 修复回环：哨兵 22/31 追认+weekend 历史回归测试合成化（d623e5ac50）。
- 第 2 轮：tests/frontend **559 passed / 0 failed 终局绿**（该目录此前因收集死锁结构性不可跑）+端点复跑 200。

### 零遗留声明
七断链+两回灌边：5 修（F34/F74/F20 本役线+F26/F04 chief4x）+1 设计态销账（F82）+1 Owner 门位带处方（F62=99_skipped SKIP-1）+2 回灌边消费端落地（MOD-BT-223）。移交项全部登记 99_skipped_for_owner.md（6+2 项）。tests/frontend 三个预存潜病（收集死锁/冒烟装置/哨兵漂移）全部治本。无待裁定、无悬空 claim、临时件已清。

### 更正（EC2 终报到账后）
- **F82 order_daemon 状态升级**：终局段所记"设计态销账"已被超越——chief4x-cplx 线会末落地接线 `d0257693f1`（六件捞回+order_daemon 接线，COMPLEXITY-GUARD 治理）。七断链终态改判：**6 修 + 1 Owner 门位（F62）**。
- **F74 q-0021（v9 袋，5 文件）**在队列 pending，内容门全过待 drain——EC2 车道自收尾中。
- ⚠️ **死袋禁 requeue 清单**（内容均被取代，requeue=回退事故）：q-20260927-st-ec2-p0-0002/0006/0010/0011/0014/0017/0019/0020。
- 超计划修复：promotion_combo_gate F821 潜伏 bug（_safe_id 未定义）治本；sim_observe_daily 5 长红测复绿。

### 审计更正二（09-27 09:4x，Owner 令全面复审后）
- **q-0021（F74 v9 袋）死因=cascade_stale（fms q-0043 推移基底）→ 改判禁 requeue**：MOD-AUTO-L2 线已并行落地 F74 本体（`40ca90eb88` 组合门打分器+一页式建议书 + `383c0af8e1` import 修复，28 测绿且其循环检查在岗）。重投 q-0021=覆盖他线在养实现。**禁 requeue 清单扩至九袋**：+q-0021。
- **F74 双实现收敛（日班任务）**：已落地版缺两增量=①combo v2 frozen 尺 STD-SIM-ACCESS-002（裁定#337：dsr≥0.5+ρ̄≤0.7+换手≤12× 腿）②combo 事件入口（advisory due 执行体尾传动渲染）。EC2 v9 最终内容完整保存于 q-0021 bag blobs（.runtime/commit_queue/blobs/：3978a77f770fd991…/babf24b62199680f…），日班择优并入或裁定取舍——blob 一旦 gc 即消失，宜先捞。
- **孤儿测试收编**：tests/frontend/test_api_server_heartbeat.py（QMine 06 09-25 未跟踪件，套件依赖且 559 绿含之）保护性入 HEAD，零内容改动。

## 日班段（总筹 st-chief6-20260927 接替 st-chief5，2026-09-27 09:3x–）

### 一、F74 双实现收敛＝已落地 `a46e1fbc3f`（交接书第一优先任务关闭）
**收敛依据不是"择优判断"而是 blob 相等实证**：q-0021 四件 `base_blob`（combo=ef7cfdf19e / test_combo=8761b849fa / advisory=6da980fe4f / test_adv=657182709b）与当时 dev HEAD 四件 blob SHA **逐件相等** ⇒ v9 非竞争实现，是 MOD-AUTO-L2 已落地字节的严格超集。故按 v9 内容并入=快进，不需取舍裁定，也不覆盖他线在养实现（禁 requeue 令仍守：走新袋非 requeue）。

| 增量 | 落地内容 | 实证 |
|---|---|---|
| ①combo v2 frozen 尺 | dsr_min 0→0.5 且 `>`→`≥`（族 N_eff）+ρ̄≤0.7 腿+年化单边换手≤12× 腿+THRESHOLD_SOURCE 改指 `config/standards.yaml#STD-SIM-ACCESS-002`+v1 suspect 注记+报告表头补两列 | 裁定#337/#306；`test_v2_thresholds_pinned`/`test_score_dsr_v2_boundary` 绿 |
| ②combo 事件入口 | 新增 `run_promotion_combo_gate`（空目录静默跳过/run_subprocess_hidden 隔离重活/rc≠0 只 warning）挂 `run_promotion_advisory_due` 执行体尾，返回体补 `combo_rc/combo_skipped` | `test_combo_hook_skips_when_advisory_dir_empty`+`test_combo_hook_downgrades_no_raise_and_due_tail_survives` 绿 |
| ③F821 治本 | **HEAD 现存缺陷非"潜伏注记"**：`_safe_id` 用而未定义（HEAD 文件 :224 用、全文件零 def），`--strategy-id` 分支一按参数必 NameError；`383c0af8e1` 补的是 now_utc 腿，此腿漏 | `git show HEAD:… \| ruff check` = `promotion_combo_gate.py:224:18 F821`；补 def 后 ruff 全绿 |
| ④F821 回归钉 | 新增 `test_strategy_id_cli_path_survives`——**判别力实测**：临时换回 HEAD 版该文件 → 6 红（含本钉与 v2 钉值四腿）；v9 版 → 12 绿；测毕按 sha256 字节验还原 | 该分支此前**零测覆盖**，正是 F821 能混过落地的根因 |

**v9 袋两处"内容门已过"记载不实（本次由落地死因逮出，防下任再信）**：
1. `daily_gate_snapshot.yaml` 缺 `# [/ALGO_FLOW]` 收标记与 `# 边:` 段，且层名自造 `"处理"`（全仓 canonical 输入/算法/输出=3304:3304:3304，"处理"**仅此 1 处**）⇒ `ALGO-FLOW-LINK` 直调实测判红"2 处锚/卡片链接断裂"。本版补收标记+9 条边+层名归 canonical+按 `validate_file` 补齐算法/输出层 intro/inputs/outputs（新件不欠字段账）。creation_token 早由 st-dloop-20260921 在册（capability 册 daily_gate_snapshot 条）⇒ **本批零热册改动**。
2. `# [ALGO_FLOW] external:` 锚被写在**文件头注释区**，而 `GATE-ALGO-FLOW`（pre-commit hook=`check_algo_flow.py`）判据是 **AST module docstring** 含该标记（全仓实证 3394 件在 docstring 内 vs 12 件仅头注=欠账，`venue_replay.py` 亦在那 12 件里）⇒ q-0002 落地死因即此。本版删头注副本、锚按 `externalize_algo_flow.py` 口径置于 docstring 末行；双门同验（`check_algo_flow` exit 0 **且** `ALGO-FLOW-LINK` PASS，非只过其一）。
3. 另清 HEAD 存量裸 `Any` 2 处（`_file_base`/`_rel` 无行级豁免被 `check_any_abuse --staged` 全文扫连坐）——改具体类型 `str|Path|None`/`str|Path`，不贴 `# noqa: any-abuse` 了事。

**测试与零回归证明**：本批 29 绿（combo 12+advisory 17，原 28 全保持）+消费端 `test_pipeline_events` 38 绿=**67 passed / 0 failed**；机械面 ruff check/format 全过+`validate_graph` CLEAN+`validate_file` CLEAN。`tests/strategy_pipeline/test_fw_backtest.py`(21)+`test_decision_orchestrator.py`(3)=24 红**在纯 HEAD 独立基座 worktree 上同数同名单复现**（根因=`config/.env.clickhouse` 不入 git，worktree 侧无该件→`get_client_strict` 抛），非本批引入；基座 worktree 用后即删。归属核验：`git log -1 --name-only a46e1fbc3f`=**恰好 5 文件**，五件 dev blob 与我的工作树 hash-object **逐件相等**，零搭便车。

### 二、q-0021 归档销案（交接书第三优先任务关闭）
五 blob 已于 09:37 全量捞至 `.runtime/sessions/st-chief6-20260927/staging/f74_rescue/`（**sha256 逐件等于袋内 blob_sha256 双证**），内容已随 `a46e1fbc3f` 落 dev ⇒ q-0021 维持 dead 不 requeue，**禁 requeue 清单第 10 袋正式销案**（内容已入 HEAD，重投=回退）。袋 json 保留在 `dead/` 不删（四态留档纪律）。

### 三、⚑跨线 systemic 风险：门禁名册标量 103≠104 令预检降级（当班修）
dev 面 `in_process_gate_registry.yaml`：`gates:` 实长 **104** vs 声明 `total_gates: 103` ⇒ `auto_register_gates` fail-closed 抛（判据源 `gate_auto_registrar.py:373`）。实测连带两处降效：①每袋入队预检 `[registration-inline] 网关构造失败，degraded 放行`＝**这段时间所有车道提交少一道预检**；②`RECONCILE-WORKER-BOOT: reconcile_worker boot failed (commit=3f9b600d21)`＝对账后台起不来。
**关键取证**：FMS 车道 `38168467d1` 提交说明自述"条目+total_gates 103→104 计数声明同批"，但**落盘字节里该标量仍 103**——派生标量被队列合并器取 ours 吞掉（同款先例 `407c399a8c`"标量 heal 102→103·净零纯标量"；历史 cf9a416d24/f3cac8b95c/d89e6295c4/4a0eac79dd 五笔同型漂移）。A/B 对照已做：104/104 面不抛、103/104 面抛。
本役处置=以 **dev 字节为基**单行重放（逐行 diff 命中==1 且行数不变、yaml 读回 `int(total_gates)==len(gates)`、`safe_write_text`+进程外读回），袋 `q-20260927-st-chief6-20260927-0004`（单文件）。**未假装治本**：`total_gates` 仍是手工派生计数，违根宪法 §9 条目 5，合并器吞标量的结构性缺陷不修则必复发——后置重算钩子/机生化=立法项，已登 99_skipped 待裁。**若复核仍见 103，即证本袋也被吞，以 `git show dev:该册` 判活死勿信本段叙述。**

### 四、EC3 移交六项·日班实测（只读探针，未 kill 未改运行态）
| 项 | 实测现态（本地时钟 09-27） | 处置 |
|---|---|---|
| ⑤EvaporationBlackbox | **恶化且根因改判**：`blackbox.jsonl` 末行 `2026-09-25T23:26:01+08:00`，实测 10:03 时**停更 34.6h**；任务 `State=Running`+`MultipleInstances=IgnoreNew`+`ExecutionTimeLimit=PT72H`，触发器每 5min 照跳但全被拒（LastResult 2147946720）；`Execute=cmd`（EC3 所记"实例挂死"仍成立，非任务定义坏） | **禁 kill 只记录**照守（EC3 原令）。⚠后果：黑匣子正是防热册蒸发的唯一现场取证件，而本役 09-27 03:2x 亲历过 capability 册被并发压盘——**该窗内它盲着**。升 Owner/LANE-EV 门位（处置=Stop-ScheduledTask 后 PT5M 自愈） |
| ①tilib 晨检 | 任务已重注册生效，`LastRunTime=09-27 02:30:01 result=1`，`NextRun=09-28 02:30`。**result=1 可解释**：重注册 commit `514698ba62` 落在 09-27 **03:53**，晚于当日 02:30 那次运行 ⇒ 今晨跑的是旧定义，新定义首验仍是 09-28。零写入预检已过：`tilib_dwm_shard_runner.py --help` exit 0、`backfill_night.ps1` PSParser parse_errors=0；`data/runtime/tilib_nightly_run.log` 0 字节 mtime 09-25 01:48（旧腿无输出） | 09-28 02:30 后看 `LastTaskResult` 一行流不变；本役不手动跑（会写生产表，宪章 §二.5 禁） |
| ③NightlySentiment 双源 | **EC3 记载已过时，实测已单源**：`config/schedule.yaml` 内 sentiment **零命中**（该文件存在），仅剩 Windows 计划任务 `ZephyrAlpha_NightlySentiment` `NextRun=09-27 22:30 result=0` | **Owner 待裁项⑤消灭**，无需裁定；如另有第二触发源则属我未查面 |
| ②ollama | 未复测（`tasklist /FI` 被 Git Bash 路径展开吃掉参数，需换 `tasklist //FI` 或 PS 侧取证） | 待复测，禁 kill 照守 |
| ④tdi 断供 / ⑥空表三件 | 需 CH 只读查，本役把 CH 查询并入终局体检批 | 未做，非消灭 |

### 五、F62 合规门·实测更正（Owner 令"接零风险一半+排雷+施工"，两子代理并发中）
**先更正我自己向 Owner 转述错的一条**：我说过"熔断锁状态文件不存在→读不到就判一律不许下单"。**盘上实证相反**：`KillSwitchLite._load()` 对"文件不存在"返回 `{}`（`discipline_prohibition_checker.py:187-189`）→`is_blocked()` 查无条目 **return False 放行**（:170-176）；真·全拒路径是**"文件存在但 JSON 烂"**（:192-193→None→:171-172 return True）。盘上实测 `data/compliance_log/` 存在但**无** `kill_switch_lite_state.json` ⇒ 现状装这把闸=放行，不误伤；且 `is_blocked()` **无** escalate 副作用（escalate 只在 `trigger()` :147-149/:158-160，会话侧唯一调用点 `trading_session.py:999` 只读）。烂文件成因（推断）：:157 `write_text` 非原子，进程被 kill 在半写点。
**另两条雷坐实且比案卷更硬**：
- 雷一纪律闸：`DisciplineContext` 九字段里 **4 个真源全仓查无**（30min 涨幅/持仓成本价/20 日双基线/成交连击），零新增数据源只能写成测试模板形态（`tests/compliance/test_runtime_wiring.py:85-98`＝追高/补仓/报复全跳过，只剩骄傲 Warning）＝**装了等于没装**；成对约束是**装配期 raise**（`trading_session.py:323-326`）故不存在"装了没 provider 盘中全拒"，但 provider 自身抛=**逐单拒**（:1011-1018 在 for 内）。
- 雷三清单闸：`HARD_BLOCK → return []` **整批吞且不重放**（:809 → 消费侧 :555-564 只 log `submitted=0`），而 INTRADAY 三必需 key（`signal_compliance_check/risk_param_confirm/position_limit_verify`）**全仓仅模块自身+4 测试命中，无任何生产生成器/注册表/DB 写它** ⇒ 二选一硬局：接查不到东西的 provider=**每轮全拒**；接恒真 provider=**假闸**。无中间态，除非先建完成态真源。
- 站点数更正：案卷"6 处裸构造"中 `qmt_file_bridge_integration.py:52` 在 `QmtFileBridgeAssembly` 类 docstring 的 Usage 示例块内，**真实生产站点=5 处**。
- `REPO_ROOT` 判据（影响测试在哪跑）：`compliance_report_registry.py:48-57` 用 `REPO_ROOT`，解析序=`ZEPHYR_WORKTREE_ROOT` env 优先，否则从 `paths.py.__file__` 上溯（**与 cwd 无关，取决于 import 哪份 zephyr**）⇒ worktree 里起会话读的是 worktree 陈旧副本；`KillSwitchLite:137` 用 `MAIN_REPO_ROOT` 恒锚主仓无此问题。

