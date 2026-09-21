---
ttl: task_bound
completes_when: Owner 对六面检查表逐面点单后转 archived
session: st-live-readiness-20260922
date: '2026-09-22'
---

# 实盘准入检查表（六面）— 小资金实盘准入准备班 · 件1

> 班次：st-live-readiness-20260922（通宵令 §3 分包1）
> **红线声明**：本班零实盘触碰。本表全部"现状实测"来自**只读探针**（探针窗口 2026-09-22 01:50–03:00），未翻转任何配置、未建立任何交易连接、未触碰任何下单通道。
> 状态图例：**绿**=已达标/安全锁定｜**黄**=在册但有条件（未实跑/待 Owner/待产物）｜**红**=缺口，补齐前不得挂实盘旗｜**白**=超出仓库知识，须 Owner 外部确认
> 配套：件2=SOP草案 `small_capital_live_sop_draft.md`｜件3=异常处置手册 `exception_handling_manual.md`｜件4=门禁设计 `admission_gate_design.md`（含依赖项清单分列）

---

## 面1 风控

| # | 项 | 判据 | 现状实测（证据） | 状态 |
|---|----|------|------------------|------|
| R1 | 交易侧五级熔断**定义**在册 | 五级（位置/日亏/断路器/秒级/API超限）各有触发条件+动作+冷却 | `src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py:74-142` 五级齐全：POSITION_LIMIT→REDUCE_ONLY(300s,自恢复)；DAILY_LOSS `daily_pnl<-0.03*aum`→撤全部挂单+禁新单(86400s,不自动恢复)；CIRCUIT_BREAKER 连续拒单≥5或价偏>5%→断Broker(600s)；SECOND_LEVEL 延迟>1s或成交率<50%→全系统暂停(300s)；API_TIMEOUT >10s或心跳丢≥3→杀当前Session(120s,自恢复) | 绿 |
| R2 | 五级熔断**接线**到逐单路径 | 逐单前有 fail-closed 检查器实跑 | `src/zephyr/ex_core/pre_execution_checker.py:176-206` 闸门1 kill_switch_gate：探针异常=Fail-Closed 拒单(:183-194)、激活=拒全部新单(:196-203)；经 `trading_session.py:318,360,472` 注入生效——但 :51-55 自注"此前全仓零调用方"，**实盘链路从未实弹跑过** | 黄 |
| R3 | 熔断状态**持久化** | 触发态进程崩溃不丢 | `trading_kill_switch.py` 为 Pydantic 类级内存态（模块内 KILL_SWITCHES 字典），**无文件/DB 持久化**；系统级 kill_switch.py:32-33 明文"进程崩溃即归零，禁用于交易资金安全"。触发态随进程死而丢 → 须进程守护或补持久化 | 红 |
| R4 | 危机闸（crisis_gate）在岗 | enabled=true 且参数已校准 | `config/crisis_gate.yaml:15` enabled: true；`:19` warning_theta: 0.5（注释原文：**O1 待 Owner 校准**，建议 0.5 起步、月度演练回看误报率后定）；crisis 口径=regime dominant==r10 硬编码登记备查 | 黄 |
| R5 | 破产地板单一仲裁点 | 回撤/破产触发有唯一仲裁与强清动作 | `src/zephyr/ex_core/risk_layer_orchestrator.py:76-85` check_bankruptcy_floor；`:114` A1 单一仲裁点 _engage_kill_switch（回撤 EMERGENCY/破产底线/系统性 LEVEL_3/流动性→trigger_kill_switch+强清） | 绿 |
| R6 | 组合准入门（L2）阈值预注册 | 四阈值冻结、判据机械可证 | `scripts/backtest/promotion_combo_gate.py:56-61` 阈值冻结：OOS Sharpe≥1.5 / 最大回撤≤15% / 纸面成交≥30 笔 / DSR>0；`:9` `[STARTUP] manual`——**未挂自动化**；`:15` promote_ready≠决定，仍须 Owner 门 | 黄 |
| R7 | 纸面/实盘通道物理锁 | real_channel_locked 恒真，代码拒绝 false | `config/paper_hedge.yaml:42` real_channel_locked: true（Owner high 门位，禁代码侧翻转；解锁=纸面闭环≥3 次演练+Owner 批准）；`src/zephyr/risk/paper_hedge_leg.py:182-185` 置 false 直接抛 PaperHedgeLegError（fail-closed）。实测 `data/runtime/paper_hedge_state.json` **不存在**=演练 0 次 | 绿（锁定）/黄（演练 0 次） |
| R8 | 下单引擎 HALT 拒单 | 引擎层有硬拒单断言 | `src/zephyr/ex_core/execution_engine.py:217-220` HALT 级违规拒单抛错 | 绿 |

**面1 小结**：绿 4 / 黄 3 / 红 1（R3 熔断态持久化缺位）。

---

## 面2 仓位

| # | 项 | 判据 | 现状实测（证据） | 状态 |
|---|----|------|------------------|------|
| P1 | 总仓位硬顶与预算带**经 Owner 确认** | proposed→confirmed | `docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md:30` 六段预算带（capitulation 0-10% / accumulation 20-30% / ignition 30-50% / expansion 50-70% / euphoria≤30% 只卖不买 / distribution 0%）×过渡带 0.5-0.7；总仓位=min(预算带, **60% 硬顶**)；`:187` 自注等参数 **proposed→confirmed 需 Owner** | 红（未 confirmed） |
| P2 | 金字塔建仓规则**接电** | TD 阶值驱动建仓/减仓有代码消费方 | Owner 原话口径（`trading_vision/2026-09-16-owner-vision-system-mapping.md:65` 附录A）：日线 TD 阶<0 金字塔建仓、波段上沿分批减仓；但 `trading_vision/2026-09-16-skeleton-coverage-audit.md:245` 实测 **pyramiding_rules 仅包导出、无消费方** | 红 |
| P3 | L4 组合层接电 | "今天开不开仓/用哪个包/总仓位"有 production 主人 | `owner_gate_list.md:40-41`（daily_loop_campaign）：pf_alloc 已上事件链接线状态、缺口⑤条件已满足；但 `trading_vision/2026-09-16-owner-vision-system-mapping.md:42` 三缺件① production 主人仍缺 | 黄 |
| P4 | 零下单安全态有效 | 无毕业包=不产执行单 | E2E 实证（`daily_loop_campaign/e2e_manual_run_report.md:78-79`）：GRADUATED_PACKAGES 恒空、enabled_packages=∅、不产执行单；解除唯一合法路径=策略卡经 S-OWNER 考试链毕业（`owner_gate_list.md:33-34`，禁手填，裁定#305 语境） | 绿 |
| P5 | 风险预算倒推仓位口径在册 | "无规则的全仓才是错"有规则载体 | `trading_vision/2026-09-16-owner-vision-system-mapping.md:26-28`：风险预算倒推仓位（Owner 三差异②）；具体单笔风险百分比**待 Owner 定**（本班 SOP 草案给建议档，见件2 §4） | 黄 |

**面2 小结**：绿 1 / 黄 2 / 红 2（P1 仓位参数未 confirmed、P2 金字塔规则未接电）。

---

## 面3 监控

| # | 项 | 判据 | 现状实测（证据） | 状态 |
|---|----|------|------------------|------|
| M1 | 日循环端到端 | 编排链有实证绿圈 | `daily_loop_campaign/e2e_manual_run_report.md:16,37-51`：圈1=09-18 历史日；圈2=09-21 实时（16:52 事件链自动 9 棒→17:30 总扳手 16 段="15 ok+1 skipped+0 error"）；`:94` 扩面后两轮循环检查零回归 | 绿 |
| M2 | 验证环闭环 | 判定有结算回写 | 同上 `:66`：judgment_plan_verification 0→6——验证环从 0 到常态；段序契约 close_verify→settle（`gaps_fixed_02_verification_loop.md:14-21`） | 绿 |
| M3 | 盘前五层门快照 | L1-L5 门态一行 JSON 可审计 | `src/zephyr/strategy_pipeline/daily_gate_snapshot.py:29-47`：L1 regime PIT 读/L2 板块门/L3 六段×四开关/L4 预算日切片/L5 kill_switch 读态；**L2 板块门恒 absent v1**（:160-162 无持久化日度状态，依赖 L2 门的包当日禁用，D2 口径——如实降级不伪造） | 黄 |
| M4 | 交易运行时心跳监控 | 断连/卡死有独立监测主体 | 五级熔断的 API_TIMEOUT 定义了 heartbeat_miss≥3 触发（trading_kill_switch.py），但交易运行时**无独立心跳守护在跑**；`heartbeat_daemon.py`（gov_enforcement）是会话/worktree 治理心跳，非交易心跳 | 红 |
| M5 | 作战室（warroom） | 盘前/盘后双段上链 | `src/zephyr/plan_engine/daily_warroom_pipeline.py` 已上链（capability_canonical_file_registry.yaml:10837-10841）；E2E 双段 ok；但组件 `src/zephyr/frontend/dashboard/components/warroom.py:17` 自注**全通道 fail-open**（监控自身失效不拦交易） | 黄 |

**面3 小结**：绿 2 / 黄 2 / 红 1（M4 交易运行时心跳缺位）。

---

## 面4 告警

| # | 项 | 判据 | 现状实测（证据） | 状态 |
|---|----|------|------------------|------|
| A1 | 交易级告警专条 | 价格/仓位级异常有阈值条目 | `docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml`（v1.4.0，887 行）：42 条阈值、12 类（ALERT/AUDIT/DEVIATION/DRAWDOWN/DRIFT/GPU/HEALTH/INTAKE/OPRISK/PLV/REPORT/RETIRE）——**全部为治理/运维/风控进程域，无行情价格/仓位级交易告警专条**（DRAWDOWN 3 条属 MOD-RK-011 进程域） | 红 |
| A2 | Owner 通知器 | 多渠道通知件 production | `src/zephyr/infrastructure/observability/notifier.py`（MOD-INF-016，capability_lookup 实测 production/alive） | 绿 |
| A3 | 熔断态被告警链消费 | kill_switch 态进告警分发 | `alert_webhook_dispatch.py:362`、`intake_events.py:131` 消费系统级 kill_switch 态 | 绿 |
| A4 | 告警失败语义明确 | 告警通道挂了系统行为已知 | crisis_gate 告警失败不阻断、留痕 crisis_gate_log 表（`pf_alloc/crisis_gate.py:402,450`）；warroom fail-open（M5）——语义=**告警是尽力而为，保命靠熔断与人工巡检**，准入须知悉 | 黄（须知悉语义） |

**面4 小结**：绿 2 / 黄 1 / 红 1（A1 交易级告警缺口）。

---

## 面5 密钥依赖

| # | 项 | 判据 | 现状实测（证据） | 状态 |
|---|----|------|------------------|------|
| K1 | 密钥轮换完成 | 09-18 .env 曝光后全量轮换+核对 | `docs/_working/recovered_task_cards/tc10_owner_report.md:16`（步骤5）：**催办 Owner，曝光后超 3 天未轮换**。必换=OKX（只读+IP 白名单+禁提币）/iFind/百度网盘 token；建议换=付费 LLM key+TUSHARE_TOKEN（裁定#392 同口径）。轮换后须 Owner 主动叫核对（AI 只报键名/格式绝不打印值） | 红 |
| K2 | 密钥三道 gate 在岗 | commit-time fail-closed 不可绕过 | `SECRETS.md:99-103,125`：NO-BARE-GETENV（diff-aware）+SECRET-REGISTRY-CONSISTENCY+NO-SECRET-HARDCODE，`--no-verify` 不可绕过；代码真源 `src/zephyr/shared/security/secrets.py`（542 行） | 绿 |
| K3 | 密钥账本对齐 | 注册表与实际键数一致 | SECRETS.md:48-49：8 文件共 100 KEY（.env=62）；.env 实测 293 行（本班未读取任何键值） | 绿 |
| K4 | 实盘账号参数受控 | live 账号不落入 AI 可写配置 | `config/qmt_environments.yaml:54` live `account: ''`（注释：实盘立项时填入）；连接参数在 .env.qmt（gitignore） | 绿（当前锁定） |

**面5 小结**：绿 3 / 红 1（K1 轮换未办——**准入门禁第一依赖**）。

---

## 面6 合规

| # | 项 | 判据 | 现状实测（证据） | 状态 |
|---|----|------|------------------|------|
| C1 | AI 操作禁区四条在册 | 实盘通道四入口全禁 | 术语"实盘四禁"全仓 grep 无此原文；权威清单=`docs/_working/automation/campaign/qmt_e2e_runbook.md:28-30` 禁区四条：①`QMT_REAL_*` ②`enable_real` ③`ZEPHYR_ENV=live` ④`LiveSimulationSwitcher.switch_to_live` **全禁**（本班通宵令 §4 沿用此口径） | 绿 |
| C2 | live 环境门禁**接线** | 配置门禁有代码消费方 | `config/qmt_environments.yaml:62` live 档 `blocks_live_trading: true # 实盘门禁：未验证前阻断`——**本班 grep 复核 src/ scripts/ 零消费方**（exit 1），属配置声明未接线=门禁空转 | 红 |
| C3 | 换档阶梯人工审批 | AI 不可自动升档 | `system_charter.md:106` B-007 五档阶梯 shadow→paper→pilot→daily_review→auto，换档唯一人工审批，初始档=paper | 绿 |
| C4 | 高危域门位注册 | high 域四类操作→Owner | `risk_tier_registry.yaml:42-47` &high_human_gate（production 流转/注册表净删/flag 出厂翻转/资金破坏性操作）；`:55-92` high 域 9 个（D_EX_CORE/D_POSITION/D_RISK/D_TRADING/D_PLAN/D_DATA/D_GOV_ENFORCEMENT/D_GOVERNANCE/D_GOV_SCRIPTS） | 绿 |
| C5 | 模拟→实盘切换器锁死 | 须 Owner 一次性令牌，失败 fail-closed | `src/zephyr/ex_core/live_simulation_switcher.py:8,26-30`；`qmt_file_bridge_integration.py:54,66` enable_real=False 默认安全 | 绿 |
| C6 | 环境辨识纪律 | 连接前 MUST 辨识 sim/live | `config/qmt_environments.yaml` disambiguation 节：TCP 配对法为双终端在线唯一权威（LISTEN 58610 二义禁用）；smoke_test_guard 判 live→ERROR 告警+拒绝继续 | 绿 |
| C7 | 外部合规义务 | 程序化交易报备/券商合规要求已确认 | 仓库内无此知识载体（grep 无程序化交易报备登记）——程序化交易监管报备、券商 QMT 实盘准入条件、税负等**超出仓库知识** | 白 |

**面6 小结**：绿 5 / 红 1（C2 门禁声明未接线）/ 白 1（C7 外部合规待 Owner）。

---

## 总计与结论

| 面 | 绿 | 黄 | 红 | 白 |
|----|----|----|----|----|
| 1 风控 | 4 | 3 | 1 | 0 |
| 2 仓位 | 1 | 2 | 2 | 0 |
| 3 监控 | 2 | 2 | 1 | 0 |
| 4 告警 | 2 | 1 | 1 | 0 |
| 5 密钥 | 3 | 0 | 1 | 0 |
| 6 合规 | 5 | 0 | 1 | 1 |
| **合计** | **17** | **8** | **7** | **1** |

**七红（补齐前不得挂实盘旗）**：
1. R3 交易熔断触发态无持久化（进程崩=熔断失忆）
2. P1 总仓位 60% 硬顶+六段预算带未获 Owner confirmed
3. P2 TD 金字塔建仓规则无代码消费方（仅导出）
4. M4 交易运行时心跳监控缺位
5. A1 告警注册表无行情价格/仓位级交易专条
6. K1 密钥轮换未办（09-18 曝光后超 3 天）
7. C2 `blocks_live_trading` 配置声明零代码消费方（门禁空转）

一白：C7 程序化交易外部合规义务，须 Owner 向券商/监管侧确认。

## 附：本班只读探针清单（全部零写操作）

| 探针 | 命令/方式 | 结果 |
|------|-----------|------|
| reaper 存活 | `python -m zephyr.trading.process_reaper --status` | last_run=2026-09-22 01:50:30，killed=0 |
| 能力反查（审计留痕） | `CapabilityLookup.find(kill_switch/crisis_gate/paper_hedge/live_trading/qmt/real_channel_locked, session_id=st-live-readiness-20260922)` | notifier/qmt_file_bridge_broker 命中；其余关键词零登记（如实记录） |
| 五级熔断态 | 代码审读（内存态，新进程恒缺省） | active_switches() 空=无激活（进程内存语义） |
| paper_hedge 状态文件 | `ls data/runtime/paper_hedge_state.json` | 不存在=演练 0 次 |
| paper_hedge 留痕目录 | `ls data/backtest_artifacts/paper_hedge/` | 不存在 |
| blocks_live_trading 消费方 | `grep -rn blocks_live_trading src/ scripts/ config/` | 仅 yaml 自身，零消费方 |
| live 账号 | 读 qmt_environments.yaml:54 | account=''（空，未启用） |
| .env 规模 | `wc -l .env`（未读内容） | 293 行；键数真源=secret_registry 100 KEY/.env 62 |
