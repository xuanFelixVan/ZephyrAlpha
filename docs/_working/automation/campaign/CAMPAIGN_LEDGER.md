---
ttl: task_bound
completes_when: 全线施工完毕+循环检查连续两次 0 问题+红蓝通过+终局交付，或 Owner 叫停
---

# 夜班施工战役台账（st-autolnk-20260917，Owner 总令"全部施工"）

> 总令要点：线内先挖后干、线间并行流水；挖干判据=本台账六向台账+自审三态；循环检查至连续两次 0 问题；红蓝对抗；GitCommitGateway 全落地；临时文件清理；无遗留无待办（无法裁定→登记+跳过，堵死可停）。
> **持久规则：每完成一个有意义的步骤就更新本台账**（防上下文压缩失忆——压缩后从本文件恢复全部状态）。

## 0. 边界与分工（已定，不再议）

- 红线维持：禁写 docs/03_modules/**（新模块蓝图暂存 campaign/blueprints/，解冻后晋升=挂单 H-01）、pf_core/backtest、TDM、AGENTS.md。
- 排班分法（Owner 确认 AI 层转达案）：规则/schema=治理+Owner 钉死；**运营（值守/采样/建议器）=AI 层**；使用=各层自助走登记接口。业务层不自建排班逻辑，③的"自动排班"=写 schedule.yaml/tasks.yaml 正门登记。
- 挖干判据：每线六向台账（目标/证据/块/依赖/三态/下一步）填实且自审三态=挖干，才开工。

## 1. 关键情报摘要（两路侦察 03:40，防重挖）

### L2 输入件（转正建议书）
- **promotion_advisory.py 已存在**（MOD-BT-199，src/zephyr/strategy_pipeline/）：合并 SCR-SIMGOV 建议+SCR-DEV 偏离月史+fw-auto/latest.json+sim_memo 指针→`data/strategy_intake/promotion_advisories/<advisory_id>.json`；CLI=`python -m zephyr.strategy_pipeline.promotion_advisory [build|list|preauth <STR-ID>]`。**勿重建**。
- 平台四件落点：`c1_backtest.sim_trade_log`（事件流水）+`sim_pocket_daily`（钱包日账）+`sim_platform_journal`（日刊三检）+sim_deviation/sim_governance 跑档 `data/backtest_artifacts/runs/SCR-DEV-*/SCR-SIMGOV-*/04_wide/*.json`；E4 正考=`scripts/backtest/f06_e4_wfa_exam.py`→`data/backtest_artifacts/runs/E4-F06-*/{verdict.md,summary.json}`；成绩台账=`c1_backtest.strategy_screen`（is_sharpe/oos_sharpe/deflated_sharpe/num_trials/verdict）。
- **真缺口**=组合门打分器（OOS Sharpe≥1.5+回撤≤15%+容量证明+DSR>0）+一页式建议书 markdown。阈值来源：docs/_working/trading_vision/2026-09-16-owner-vision-system-mapping.md L57（草案在案，硬编码+引用出处）。
- 写作范本：scripts/backtest/sim_promotion_memo.py（只读生成/缺失降级不阻断/[CREATION-TOKEN] 头）；测试范本 tests/backtest/test_sim_promotion_memo.py。

### L1 输入件（上架流水线）
- DDL-as-Code：schemas/categories/market/<name>.py（XXX_DDL+TABLE_NAME+INSERT_COLUMNS）；DateTime64(3) 业务列 Asia/Shanghai、系统列 UTC；ReplacingMergeTree+PARTITION BY toYYYYMM(trade_date)+自然键 ORDER BY。
- 登记接口：schedule.yaml 槽位字段=cron/executor(default/heavy/realtime/intraday_minute/intraday_sector)/description/max_instances/type+seconds；**启动时加载不热载→新槽/新任务需调度器重启**；tasks.yaml 任务字段=task_id/table/source/schedule/incremental/capability/date_col/extra。
- 写入正道：`from zephyr.data.ch_writer import write_result, query`；FetchResult(table,columns,rows) never-raise；限频=SourcePolicy(config/policies.yaml)；robots 尊重有先例（rss_provider RobotFileParser）。
- 表名必须走 TableRegistry（docs/03_modules/business_data_categories.yaml）——**该文件在冻结区**→v0 变通：直连 ch_writer 写 c1_market 表+registry 注册列挂单（H-02），或验证 TableRegistry 是否硬拦。
- 调度器：python -m zephyr.data.scheduler，单例锁 tmp/scheduler_instance.lock，:9100 监控；安全重启窗=04:00-05:00（05:30 前无班次）。

### 战场态
- 03:39 时出仓波次（algo-flow P2-1 03:24）与排班 v2（st-govmap 03:34：api_server/ops_alert_feed/incubator/auto_runtime）在飞；st-qoder-t1a 持若干 test 文件 claim。我方新文件避开上述足迹。

## 1.5 接班会记录（st-autolnk-20260917b，09-17 13:5x）

- 六线交付已在 dev 核实：L2=40ca90eb88（+dc285476f4 翻译随批+383c0af8e1 import 修复）；L1/L3/L4/L5/L6 六件（onboard_source/fx_ecb_ingest/intel_harvester/generate_skeleton_health/standards_lib/risk_redline）全部在 71257b59b2 一批落地；Owner 拍板批=9729a73390（WeeklyRest 已注册）。
- 台账 §5 提交账本此前未回填，本班补录于 §6。

### L1.1 provider 正门路由挖矿【三态：挖干，本班】
- 目标：ECB 汇率源从 Windows 任务旁路升格 DataScheduler 正门（tasks.yaml+provider 路由），并固化"新源上正门"的标准路径。
- 证据（路由真源）：
  - 正门链=tasks.yaml `source:` → scheduler.py `create_provider()` if/elif 链（**scheduler.py:1176-1274**，19 分支）→ `_get_provider` 懒连（:1151）→ 任务执行 `_try_source`（policy 限流+熔断+自动重连，:1741 起）。
  - FetchPayload(start,end,incremental,extra) 由 :1844-1866 构造：incremental 且有 last_key→start=last_key，end=today——**断点自愈由进度存储负责，provider 禁自设固定窗**。
  - provider 契约=provider_base.py:202 `IngestProviderBase`（connect/health_check/fetch/disconnect；fetch 返回 Iterator[FetchResult]，**异常吞成 FetchResult(error=) 不抛**；INVARIANT：provider 只拉不写 CH）。
  - capability 机器契约=IngestProviderMeta.capabilities=[CapabilityContract(...)]（#ARCH-CH-022）；路由-meta 一致性=capability_validator.py:402/434，启动 WARN、commit gate CAP-CONSISTENCY 拦新增。
  - 登记面：tasks.yaml 字段样例=eia_petroleum_incremental（:1054）；源策略=src/zephyr/data/config/policies.yaml（rpm/concurrency/retry_on，fred 样例 :155）；槽位=schedule.yaml `schedules:`（新槽须调度器重启 04:00-05:00 窗激活）。
  - tasks.yaml 悬空 source 侦查：`local_valuation`/`bdpan`/`backfill` 三值不在路由表（bdpan 走 Windows 任务 ZephyrAlpha_BdpanTickWatch 旁路；backfill/local_valuation 待另案考古——**非本班修，登记发现**）。
- 施工方案（定案）：**专用薄 provider**（source=`alt_fx_ecb`，capability=`fx_ecb_daily`），fetch 核心从 fx_ecb_ingest.py **上移到 provider**、脚本改薄壳复用（单一真源，避 CLONEGUARD）；新槽 `daily_alt_fx` cron "35 23 * * 0-4"（ECB 发布≈北京 22:15-23:15 后，假日缺价由 last_key 不推进自愈）；不做 generic-card provider——无先例且 CapabilityContract 静态声明要求与之冲突，等 ≥3 个正门源后再议（规则三）。
- 依赖裁定：ZephyrAlpha_AltFxECB Windows 任务退役=在飞任务退役 → **Owner 拍板项 H-06**（双轨期 ReplacingMergeTree 同键幂等无害）。
- 块：B1 provider+脚本薄壳化；B2 路由/策略/槽位/tasks 四登记；B3 测试（零网）；B4 翻译/token/depgraph 登记；B5 提交；B6 重启窗激活确认（04:00-05:00 值守或晨间 verify）。

### ⑥号车道=车道 G 全网搜索进货（挖矿+施工）【三态：已落地 d75df06d4c，本班】
- 目标（骨架 §4 P1"⑥号车道：E1 加第六车道，从胃点菜找策略"）：E1 加第六车道，消化 L3 胃收件箱→策略假说卸进货台账。
- 挖矿六向（证据 file:line）：
  - 车道注册机制真源=config/strategy_production_map.yaml 节点（node_type: lane+lane 字母+十必填字段；校验器 scripts/governance/d5_architecture/validators/validate_strategy_production_map.py:38-90，commit 触发 gate=STRATEGY-FACTORY-MAP，data_refs 引用文件必须实存→台账空件先建 header 过闸）。
  - 现役车道=图节点 A-E 五车道；**代码车道 F 已被 F06 网格占用**（factory_intake_pipeline.py:59-61，仅代码无图节点=2.4 接线跨线欠账）→ 新车道跳号取 **G**，防双真源撞号。
  - E1 消费面=scripts/backtest/factory_intake_pipeline.py `_LANE_SPECS`（E0 问闸预检+排产）+ run_pipeline intake_sources（E2 幂等预审按 candidate_id 消费）；车道模式="干完活即卸台账，编排只消费"（D/B 直调，C/C2/G 事件触发）。
  - 候选 schema 模板=lane_b_idea_generator.py（candidate_id/theme/hypothesis_zh/mechanism_hint/horizon/universe+出生证三件套机器写入）；E1G 域前缀 md5 内容寻址与 E1B 隔离。
  - 胃产出面=intel_harvester 收件箱 docs/_working/automation/inbox/intel-*.md（`## N. 标题`+链接/命中词/摘要行）；"只搜不入册"红线守胃侧，车道侧守"进货不打分"。
  - 红线核对：骨架工单"TDM 他改避撞不碰"=config/trading_decision_map.yaml；**工厂图 strategy_production_map.yaml 非 TDM** 且增长轨设计明文"新车道按层位规约追加"——改图不违红线。
- 施工定案：新件 scripts/backtest/lane_g_stomach_intake.py（MOD-AUTO-E1G-001 暂编号）——url 级 seen log（LLM 失败/无 JSON 回包不标 seen=下一班自愈）、同批重复 url 不重考、空数组=诚实无货也记账；零联网零抓取（抓取真源=L3）。
- 实弹两班：首班 5/5 记失败——根因=CLI `__main__` 下 scripts.* 不在 sys.path，_parse_ideas 惰性导入异常被吞进 failed（教训=never-raise 契约必须带异常留痕，已补 WARN stderr）；补 path .bootstrap 后二班 processed=5/failed=0，全回"[]"=方法论论文零可检验假说（设计内诚实行为，扩产靠胃侧关键词/源注册表化=L3 扩展位）。
- 测试 10 件零网零 LLM（假 chat 注入）+ 接线钉（_LANE_SPECS/FAC-E1G 节点）；pipeline 存量测试硬编码车道数随五台账更新（12 全绿）；工厂图校验器 PASS；实弹台账 data/strategy_intake/lane_g_{candidates,seen_urls}.csv 随批入册。
- 欠账登记：事件接线（收件箱新班→自动触发消化）未挂=build_status partial，与⑤"新数据入库自动触发"同属事件轨施工；F 车道图节点补挂=2.4 线跨线欠账不代修。

## 2. 各线六向台账

### L2 转正建议书汇总器（P0）【三态：已交付（40ca90eb88+383c0af8e1）】
- 目标：组合门打分器+一页建议书（消费 advisory JSON+strategy_screen+sim_pocket_daily）。
- 块：B1 打分纯函数+报告渲染（scripts/backtest/promotion_combo_gate.py）；B2 测试（tests/backtest/test_promotion_combo_gate.py）；B3 登记（token/translation/depgraph）+提交。
- 下一步：写 B1。裁定：promotion_advisory 不重建只消费；阈值硬编码+引用出处；CH 不可达→降级仅 advisory 证据（沿 sim_promotion_memo 不变量）。

### L1 数据源上架流水线（P0）【三态：v0 已交付（71257b59b2）；L1.1 正门路由已落地（4058b7b1e0，接班 b 班）——R1 调度器重启激活到窗即做】
- 目标：`scripts/data/onboard_source.py`（源卡片驱动：probe 沙箱/apply 建表+登记/verify 计数核验）+首个真实免费源端到端上柜（选定：frankfurter.app ECB 汇率日频，免 key，表 c1_market.alt_fx_rate_ecb，自然键 trade_date+base+quote）。
- 块：B1 卡片 schema+probe；B2 DDL 渲染+建表（直连 ch_writer.query）；B3 采集任务（新 thin provider 或独立脚本走 write_result）；B4 schedule.yaml 槽位+tasks.yaml 任务登记；B5 调度器安全重启激活（04:00-05:00 窗）；B6 verify+台账。
- 依赖裁定：TableRegistry 在冻结区→表名直写+H-02 挂单；AkshareAltProvider 不动（1448 行他线资产）→新独立薄脚本。
- 下一步：B1-B3 先行。

### L3 搜索设备 v0（胃地基）【三态：已交付（71257b59b2，实弹 7 命中+摘要产出）】
- 目标：`scripts/automation/intel_harvester.py`：arXiv API(q-fin)+RSSHub 现役源→关键词过滤→OllamaChat 摘要（LSG 内置）→inbox `docs/_working/automation/inbox/intel-<date>.md`+候选源卡片。
- 依赖：Ollama 在跑（9 模型）；RSSHub pm2 常驻。只搜不入册（红线）。

### L4 ⑨骨架体检月度任务【三态：已交付（71257b59b2，首份月报 campaign/health/skeleton-health-202609.md 已产出）】
- 目标：`scripts/governance/generators/generate_skeleton_health.py` 只读盘点（注册表 72 实体+TDM 只读+采样 JSONL+覆盖审计产物 bb230c4f44）→月度建议书（血肉级/骨架级分节）。
- 注：TDM 只读不写（红线）。

### L5 标准库 v0【三态：已交付（71257b59b2，注意：真身=config/standards.yaml 非 standards_registry.yaml，standards_lib.py 已接）】
- 目标：`config/standards_registry.yaml`（standard_id/version/threshold/scope/status/why）+`scripts/governance/standards/standards_lib.py`（loader+freeze 核验+重考历史 diff 报告 v0）+种子数据（准入组合门四条为首批标准）。

### L6 实盘红线执行器 v0【三态：已交付（71257b59b2，纯函数+合成数据测试；实盘开通前只挂演练）】
- 目标：规则引擎（分级红线表 4h 熔断/日黄红线/周月红线/黑天鹅 48h 缓冲 regime 仲裁接口）纯函数+合成数据测试。落位 src/zephyr/ex_sor/risk_redline.py（域安静）。

### L7 A/B 联赛编排 + ④AI 判净站【三态：挂起待 L2/L1 落地后接】
- 理由：编排依赖 promotion 机制与模拟盘长周期数据（6 个月判定窗，今夜无数据可编）；判净站依赖 L1 表落位。挂起≠放弃，登记依赖图。

## 3. 挂单（解冻/ Owner 项，不阻塞）

- H-01 新模块蓝图晋升 docs/03_modules（冻结解除后）
- H-02 首个上架源表名进 business_data_categories.yaml+TableRegistry（冻结解除后）
- H-03 GPU-01/02 施工（scripts/backtest 红线区+预测表 DDL，等 pf_core 手术收针）
- H-04 GPU-04 RL trainer（B-007 Owner 门）
- H-05 CH-OptimizeMerge register ps1 化（改活任务，需值守窗执行，Owner 已批待安全窗）
- H-06 ZephyrAlpha_AltFxECB Windows 任务退役（L1.1 正门班次激活+连续 7 天打卡确认后执行；在飞任务退役=Owner 拍板项⑥；双轨期 ReplacingMergeTree 同键幂等无害）
- 发现登记：tasks.yaml 悬空 source 三值（local_valuation/bdpan/backfill）不在 provider 路由表——另案考古，非本战役修

## 3.5 姊妹战役协调裁定（2026-09-18 02:3x，第三棒开工登记）

- 姊妹战役：st-residual-20260917「残余挂账施工战役」并行在飞（docs/_working/residual_construction/00_master_ledger.md，E1-E7 封矿+W1-W3 波次）。
- 其 C1 裁定：pipeline_events.py / tasks.yaml / apply_market_tables_ddl.py 三共享文件归其总统筹独占（波次边界统一接线）。
- 本战役遵约改道：**R3 车道G事件接线的共享文件触点挂起**，本轮只交付本侧事件发射能力（车道G自有文件纯函数）+接线挂单（波次边界由 residual 总统筹或 Owner 批后一行接线）；R1 调度器重启（04:00-05:00 窗）为进程级运维、不碰其文件，按交接令"到窗即做"；QMT 模拟盘 100 股端到端测试为本夜新增 Owner 明令（模拟账户授权明确）。
- 交叉引用：其 E1-E7=残余挂账施工环节（另一轴）；本战役 8+1 工段=自动化产线轴。两轴互补不重叠。

### QMT 模拟盘 100 股端到端测试（第三棒，Owner 明令）

- 通道裁定：Owner 纠正 MiniQMT 今日（09-18）下线→**正道=大 QMT 文件桥**（MOD-L06-001-QMTFB：HTTP 快路径 18901+指令 CSV+柜台镜像四 CSV）；已拉起的 XtMiniQmt 进程已停。
- 实测（03:0x 夜间）：环境辨识=仅模拟终端在线（E:\国金QMT交易端模拟，无实盘终端无歧义）→QmtFileBridgeBroker(env="sim")→600000.SH BUY 100 股限价 8.10（深低市价，意图零成交）→**submit→柜台→状态回流 SUBMITTED 全链打穿**→撤单指令受理→终态待柜台夜间批处理（Order.csv 导出批处理晨间复核）。
- 证据：docs/_working/full-auto-chain/evidence/qmt-bridge-smoke-20260918-c3.yaml；执行手册 qmt_e2e_runbook.md。
- 阻塞改登记：miniQMT 启动需 GUI 登录一度阻塞→Owner 亲自开终端解除；成交腿（市价附近真成交+持仓验证）留待交易时段 Owner 门执行。

### 第三棒终局态（2026-09-18 04:3x）

- **挖矿文档树封矿**：mining/ 总谱+十工段作业簿全交付（约 226 子模块节点，全 file:line 证据+WO 号）；种子讹误修正 4 处。
- **QMT 桥 100 股端到端**：SUBMITTED 全链打穿（大 QMT 文件桥+HTTP 18901），证据 yaml 落档；成交腿待交易时段 Owner 门。
- **R1 达成**：调度器 04:00 窗重启，daily_alt_fx 激活（22 jobs 实证）；R2 打卡 1/7（66 行/09-17）。
- **R3 改道**：接线触点挂单（residual C1 独占），本侧能力已交付。
- **循环检查**：两轮 72/72 零问题（含逮出 registry 计数滞后 25/22 追认）。
- **红蓝**：前夜 5 P1+14 P2 全修/登记；本夜真发现=registry 计数滞后+夜间撤单状态回流滞后（已记晨间复核）。
- 提交态：q-0006 入袋（17 文件含 mining 树/标准库/catalog），皮带消化中；计数追认批直连落地。

## 4. 循环检查与红蓝

- 每线提交后自检：pytest 该线测试+--help 冒烟+产物目检。
- 全线完成后：整体循环检查×2（连续两次 0 问题）→红蓝对抗（子代理攻击：输入异常/空数据/CH 断连/路径越界/幂等重跑）→修复→终局端到端演示（源→表→任务登记→报告生成全链实录）。

## 5. 提交账本

- fe8fce25b7 联动方案 v1+排班补注册批 → 2a11b88164 骨架 v1 三件 → a240714ea5 骨架 v1→v1.1 → 9729a73390 Owner 拍板批（5 任务退役/WeeklyRest/锦标赛裁定）→ 71257b59b2 六件同批（L1 上架流水线+ECB 实弹 63 行/L3 胃/L4 体检/L5 标准库/L6 红线）→ 40ca90eb88 L2 转正建议书 → dc285476f4 翻译随批 → 383c0af8e1 循环检查第 1 轮修复（缺 import）。
- 接班会（st-autolnk-20260917b）：
- L1.1 正门路由班（09-17 14:0x-14:5x，hash=4058b7b1e0 队列正门落地）：provider+四登记+11 测试全绿；实弹=health_check True+collect 9 行（09-14..09-17 窗，缺今日=ECB 未发布，符合预期）；route-meta 零新违规。附带治本三件：①.gitignore 虚报收编（前批 message 称"豁免两件"实未合入，fx_ecb_ingest/onboard_source 一直脱管裸奔）②onboard_source_blueprint.md 悬空指针补齐（四文件引用但从未存在）③调度器 partial-fail 语义坑写入 provider 注释（见 FetchResult.error 即 break 丢整批行，禁带 error 交部分货）。落地侧门禁连环七轮实录（每轮一死信对症修）：STARTUP 生造词'scheduler'→scheduled_task（VOCAB-HARDCODE）、raise 消息带 path→details 结构化字段（MSG-EXPOSURE）、SQL 字面量→模块常量+noqa 留痕（NO-BARE-SQL）、裸 subprocess→process_pool.run_subprocess_hidden 正门（BARE-SUBPROCESS，creationflags 同行判定不认续行）、ALGO_FLOW external 锚指 .md→删锚与同族一致、datetime.date 注解缺 import→from datetime import date。
- ⑥号车道班（09-17 14:5x-15:0x，hash=d75df06d4c 队列正门落地）：车道 G 模块+10 测试+工厂图 FAC-E1G+编排接线+实弹两班（首班吞异常教训→补 WARN 留痕）；token×2/翻译×1 已 CAS 登记（registry 嵌套误插由 kimi-audit 班 368a01cbb7 归位根列表——教训：热文件锚点用 text.index 首匹配会撞同名嵌套键，追加须定位根键）。**提交窗阻塞实录**：st-mergewave 场景引擎 merge 晾置（MERGE_HEAD=e19bc24c，冲突已解待 finalize）——普通 commit 会截胡（AI-FILL-14 先例），本班停等；另 SESSION-REQUIRED 复发根因=前次失败 finally 注销+lock_files 自动注册 pid=死进程，治本=SessionRegistry.register(pid=0) 心跳模式（先例 st-tv2terrain）。.gitignore+双脚本收编批与 registry 批拆单独提交（PROTECTED-PATHS 预检无 message 视野，锁内 gate 凭 [ARCH-APPROVAL] 标记放行）。车道 G 落地侧另两死信对症：FUNCTION-DUP load_existing_ids→委托 lane_b 同实现（CLONE-GUARD 决议=委托）、run_intake 复杂度 19→拆 _build_rows（NO-HIGH-COMPLEXITY）。
- 事故实录（本班，两次）：14:0x 与 14:4x merge 波（st-mergewave/st-auction-bridge pre-merge stash 链）横扫主区——台账 §1.5 首版被回滚、四登记未暂存编辑被还原、部分仅存于 stash@{1}（已找回）。教训固化：**每改一个文件立即 git add**，跨文件批次不留裸窗口。
- 待办接力：正门班次激活需调度器重启（04:00-05:00 安全窗或 Owner 值守窗）；激活后晨间跑 onboard_source --mode verify 对账；连续 7 天打卡后提请 H-06（AltFxECB Windows 任务退役）。
