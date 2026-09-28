---
ttl: task_bound
session: st-ec2-p0
---

# 99_skipped_for_owner — Owner 门位登记（EC2 车道）

> 纪律：资金/净删/production 流转/flag 出厂翻转/人工报送=Owner 门位，车道只登记不代裁（宪章 §二.6）。

## SKIP-1 · F62 合规门接线（C-002 三门+C-004 三闸 12 件零注入）
## SKIP-1 · F62 合规门接线（C-002 三门+C-004 三闸 12 件零注入）

> **✅ 2026-09-27 解锁更新**：Owner 经认证对话确认 **2025 年 12 月开通 QMT 时已按券商流程报送全部六项**
> （账户/软件/策略类型/申报速率/单日笔数/变更义务）。登记表 v1.0.1 已回填（broker_ack=true ×6、
> reported_at 月锚 "2025-12"、溯源注记在册），ReportGate 实测 **BLOCK→PASS**。SKIP-1 的"报送前置"消灭，
> 剩余工程接线（12 件注入）转为**普通施工任务**（预估 1-2 人日），下方原始记录保留作背景。


- **判定**：Owner 门位，登记跳过（EC2 九项销账之 F62）。
- **现态证据（2026-09-27 复核）**：
  - `grep -rn "OrderManager(" src/zephyr scripts --include="*.py" | grep -v test` = 6 处裸构造全在
    （qmt_trading_session.py:115 / qmt_file_bridge_integration.py:52 / app_panel.py:524 /
    start_paper_session.py:492 / construction/demo_e2e_pipeline.py:326 / construction/qmt_bridge_regression_smoke.py:230）；
  - compliance_report_registry.yaml `broker_ack: false` ×6、`broker_ack: true` ×0——报告从未报送；
  - `ProgrammaticTradingGuard(` 非测试命中=仅自身 :278 示例。
- **为何 Owner 门**：接线顺序强约束（m7_live_execution/06_compliance_gates.md B1）——
  ReportGate 接线即生效，而 6 项义务 broker_ack 全 false→第一笔单即 BLOCK（fail-closed 正确）。
  正确序列=**Owner 先走券商人工报送程序化交易报告→人工回填 YAML 确认位→再接线**；
  人工报送=外部周期动作，工程侧不可代行。当前未实盘（S-1 锁），无在险违规。
- **移交**：Owner 报送完成后，工程侧接线（assemble_session 注入三门三闸+monitor 同实例、
  programmatic_trading_guard 挂 live 档）按 B1②③ 处方施工，1-2 天，G5 实盘准入前必闭。

## SKIP-2 · F74 堵点3（唯一人工门带外通知通道）

- **判定**：Owner 门位裁定项，登记跳过（03_promotion_gate.md §五堵点3）。
- **现态**：飞书/SMTP 09-15 裁撤后通知唯一出口=前端 #promotion 页横幅+data/failures/ 落文件；
  Owner 不开屏=建议无限期滞留（fail-safe 但无人知）。
- **为何 Owner 门**：补邮件/死件开关/晨报承接三选一=触达通道裁定（Owner 自身触达面）。
- **移交**：裁定后 F74 方可宣 built（本役已修堵点1/2，剩④处女链彩排随首自然班次）。

---

## 日班新增（总筹 st-chief6-20260927，2026-09-27）

### SKIP-3 · 黑匣子 EvaporationBlackbox 盲态 34.6h（处置需 Owner 或 LANE-EV 授权）
- **实测**：`.runtime/evaporation_blackbox/blackbox.jsonl` 末行 `2026-09-25T23:26:01+08:00`（本地 10:03 取证=停更 34.6h）；任务 `State=Running`、`MultipleInstances=IgnoreNew`、`ExecutionTimeLimit=PT72H`、每 5min 触发被拒（LastResult 2147946720），`Execute=cmd`（任务定义未坏，是挂死实例占位——EC3 原判仍成立）。
- **为何要 Owner 点头**：EC3 原令"禁 kill 只记录"，故当班未动运行态。但黑匣子是本仓防"热注册表静默蒸发"的**唯一现场取证件**，而 09-27 03:2x 本役亲历过 capability 册被并发车道工作树快照压盘一次——**该窗内它正盲着**。
- **不点的后果**：继续盲；下次热册蒸发仍只能靠事后 git 反推（历史上"主区改注册表必死、git 不可回取"案例在案）。
- **处置**：`Stop-ScheduledTask` 后 `PT5M` 自愈（EC3 已给处方），可逆、非破坏。
> **2026-09-28 夜终态**：已修（Stop-ScheduledTask 11:38 + ExecutionTimeLimit PT72H→PT30M 防复发，见裁7）。

### SKIP-4 · 清单闸（C-004 checklist_checker）无生产真源=二选一硬局
- **盘上实证**：`HARD_BLOCK → return []` 整批吞且不重放（`trading_session.py:809` → 消费侧 `:555-564` 仅 log `submitted=0`）；INTRADAY 三必需 key（`signal_compliance_check/risk_param_confirm/position_limit_verify`）**全仓仅模块自身+4 测试文件命中，无任何生成器/注册表/DB 生产写入侧**。
- **待裁**：①本批不装（零风险，登 backlog）；②先建"盘前完成态"真源再接（治本，跨模块排期）；③把 `state_store` 当半真源派生 `risk_param_confirm`（需先定义写入侧，否则等价空集=每轮全拒）。
- **附带需新裁定的判据**：INTRADAY 在 paper 环境能否放宽为 Warning——`discipline_must_do_checker.py:24` 头注"盘中执行除外，Hard Block"是**裁定值**，改判需新裁定（本役不自行放宽）。
> **2026-09-28 夜终态**：已治本（写侧三腿+装配落地，详见 chief8 台账 docs/_working/chief8_night/91_progress.md）。

### SKIP-5 · 纪律闸（C-004 discipline_guard）降级形态是否可接受
- **盘上实证**：`DisciplineContext` 九字段中 **4 个真源全仓查无**（30min 涨幅/持仓成本价/20 日 freq+size 双基线/成交连击）；零新增数据源只能写成 `tests/compliance/test_runtime_wiring.py:85-98` 模板形态＝追高/补仓/报复三条**全跳过**、只剩骄傲 Warning。
- **待裁**：①装"模板式 provider"但审计口径须自认 MVP 仅骄傲提醒（防"有闸"错觉）；②补 4 真源后全装（施工量大，且 provider 内每字段须自带 try→None 降级，否则一抛即逐单拒 `:1011-1018`）；③本批不装。
- **口径边界待 Owner 定**："xtdata 已连接"算不算零新增数据源（30min 涨幅可否走既有 xtdata 通道）。
> **2026-09-28 夜终态**：诚实两把已装、其余腿待源（xtdata 追高腿见 chief8 台账待办①）。

### SKIP-6 · `total_gates` 手工派生计数=结构性复发点（立法项）
- 名册标量与实长不一致已实测致 `auto_register_gates` fail-closed 抛、入队预检整体 degraded 放行、reconcile worker 启动即失败；FMS `38168467d1` 的"条目+计数同批原子修"**标量未落**（队列合并器对标量恒取 ours），本役以 dev 字节重放单行修（袋 q-0004）。
- **治本待裁**：`total_gates` 改机生或加后置重算钩子（根宪法 §9 条目 5"凡条目列表+计数清单必须生成器产出"）。**在治本落地前，任何改门禁名册条数的批次都必须自查 `int(total_gates)==len(gates)`**，否则该批预检静默降级。
- 建议登记为治理立法提案，勿只当一次性 heal。
> **2026-09-28 夜终态**：治本落地（落地期自愈读回 + total_* 自动发现器 af7e492276，见裁6）。

### 更正与消灭（对上方原始记录）
1. **原 Owner 待裁⑤"NightlySentiment 双源"→ 消灭**：实测 `config/schedule.yaml` 零 sentiment 命中（文件存在），仅剩 Windows 计划任务 `NextRun=09-27 22:30 result=0`＝**已单源**，无需裁定。
2. **F62 站点数 6→5**：`qmt_file_bridge_integration.py:52` 系 `QmtFileBridgeAssembly` 类 docstring 的 Usage 示例，非代码构造点。
3. **F62 熔断锁"不存在→全拒"更正**：`_load()` 对文件不存在返回 `{}` →`is_blocked()` **放行**（`discipline_prohibition_checker.py:187-189`/`:170-176`）；真·全拒路径是"存在但 JSON 烂"（`:192-193`→None→`:171-172`）。盘上实测 `data/compliance_log/` 无 `kill_switch_lite_state.json` ⇒ 装这把闸现状不误伤。`is_blocked()` 亦无 escalate 副作用。
4. **SKIP-1（F62 报送前置）状态推进**：broker_ack 实测 true×6/false×0，Owner 令"接零风险一半+排雷+施工"已开工（三门注入在途）。
5. **SKIP-2（F74 堵点3 通知通道）不变**：仍待裁；F74 堵点1/2 已随 `a46e1fbc3f` 落地。
