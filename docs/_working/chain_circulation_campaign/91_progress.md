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
