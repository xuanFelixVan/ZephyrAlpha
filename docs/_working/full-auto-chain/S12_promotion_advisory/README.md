---
ttl: task_bound
title: S12 转正建议生成与推送挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S12 转正建议生成与推送（证据包+告警推送 Owner）

> 骨架定位：整装回测完毕（S11）→ **机器自动生成转正建议包并推送给 Owner** → Owner 在前端
> 拍板（S13）。当前=❌ 断（sim_governance 建议只 print）。本环节挖矿核心三问：①建议怎么
> 自动生成并落档；②告警怎么真实送达 Owner（现有 AlertManager 是不是真通道）；③owner_token
> 机制全貌（决定拍板合法性）。
> **【施工班 2026-09-15 回填】C4 已落地：promotion_advisory 三路证据合流 builder（hold 不产包+safe_write 幂等）+decide 全链（token sha256 常量时间比对→FSM→注册表 CAS→台账只存指纹→alerter 回执，已决幂等拒）+OwnerTokenGuard 生产化（ZEPHYR_OWNER_APPROVAL_TOKEN+fail-closed）+decide 头部 KillSwitch 总闸（红蓝发现#1）。飞书/SMTP 凭据=Owner 侧唯一缺口。**

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 建议生成器——两件并存，均不上传不落档

- `scripts/backtest/sim_governance.py`（MOD-BT-094/140）：规则=`recommend` L68-77（连续 2 月
  monthly_pass→`promote_paper`；连续 2 月 breach/连续提案→`demote_decayed`；oos_years_decay
  ≥0.5 存疑标注）；输入=strategy_screen 的 SIM-DEV 月度判定史（`month_history` L58-65）；
  **输出仅 print/JSON**（main L93-98），无 run 档案、无告警——docstring L23 写"落 run 档案"
  为**文档-代码漂移实锤**。`[STARTUP] manual`（L6），无事件接线。
- `scripts/backtest/sim_promotion_memo.py`（MOD-BT-193）："Owner sim→production 签字前最后
  一眼"的机器备料，产出 `docs/_working/pipeline-research/sim-memos/sim-memo-<YYYYMM>.md`；
  **事件接线已通**（pipeline_events `sim_memo_monthly` 月度档，见 S10 §1.3），但它走
  screen 的 IS/OOS 视角，与 sim_governance 的判定史消费是**两条平行线未合流**——S12 的
  "统一建议包"就是要把两线+整装回测证据合流。
- 整装回测证据包：S11 施工 C3 产物 `docs/_working/pipeline-research/fw-backtests/` +
  `data/backtest_artifacts/bt-fw-*.json`（panel_reconciliation 独立对账字段自带验收）——
  转正建议的第三路证据输入（挖矿确认其落档契约已冻结，CTR-P1-017 十五字段）。

### 1.2 告警基建真相——AlertManager 是"假通道"，真通道在 data/alerter

| 件 | 位置 | 本体 | 能否真实送达 |
|----|------|------|------------|
| AlertManager | `src/zephyr/shared/alerts/alert_manager.py` L73-106（MOD-INF-016） | **纯内存 list**（上限 1000），API=create/raise_alert/acknowledge/get_active/get_by_severity | ❌ 无持久化无外发；`sim_platform_journal.py:87-97` alert_if_degraded 每次 new 一个实例→塞内存→进程退出即消失=**告警假送达** |
| DualChannelAlert | `shared/alerts/dual_channel_alert.py` L67-93 | 内存对象打 dashboard_sent/messaging_sent 旗标 | ❌ 同上 |
| alert_senders | `shared/alerts/alert_senders.py`（WeChatWebhookSender/EmailSmtpSender） | 企业微信 webhook markdown+SMTP 实发，**显式构造注入才生效**、best-effort、凭据脱敏 | ✅ 可用但**默认未启用**（55 号文"首批策略实盘上线前必须注入实现"） |
| Alerter | `src/zephyr/data/alerter.py`（MOD-L00-004） | notify（L139）/notify_channels（L232）；飞书 webhook（ZEPHYR_FEISHU_WEBHOOK）+SMTP（ZEPHYR_SMTP_*）经 secrets 读 .env；失败文件 data/failures/*.json；ERROR/CRITICAL 才触达 IM/邮件（300s 冷却）；全链不抛异常 | ✅ **现成可用真通道**（数据调度器在用） |
| NotificationRouter | `src/zephyr/frontend/notification_router.py`（MOD-FE-004） | 严重级→通道路由表+wecom/feishu 发送器注入（secrets:// 引用）+静默时段（critical 不静默）+超时未 ack 升级；Alertmanager 路由思想 | ⚠️ 件已成熟但**全仓无生产装配点**（grep 无实例化） |
| l6_feishu_alert | `security/llm_defense/llm_security/layers/` | webhook 不可达时写 alerts_pending.jsonl 本地持久化"告警不丢" | ✅ LSG 域内专用，模式可借鉴 |

**结论：C4 推送的最小路径=Alerter.notify（飞书），零新基建；AlertManager 只适合作进程内
聚合器，不可当送达通道。**

### 1.3 owner_token 机制全貌（必答①，本挖矿核心答案）

- **现状全貌 = "非空即真"的一个 guard**：`lifecycle_fsm.py` L76-81 `OwnerTokenGuard.check`
  仅做 `bool(context and context.get("owner_token"))`——**无签发方、无密钥绑定、无校验逻辑、
  无存储**；secrets.py（`zephyr/shared/security/secrets.py`，get_secret/get_required_secret，
  Env/DotEnv provider）里**没有** owner token 相关键。
- FSM 的 sim→production 边（L99）**没有任何生产驱动方**：全仓 `build_strategy_fsm` 消费仅
  `intake.py:279-310`（只驱 candidate→sim 预授权三条件）；sim→production 仅存在于单测
  （`tests/strategy_pipeline/test_lifecycle_fsm.py` L67-74 验证空 token 拒门）。
  **停门成立的原因是"机器流程根本不生成 token"，不是 token 难伪造。**
- 生产级令牌门先例已存在：`LiveSimulationSwitcher`（MOD-EX-035，`ex_core/
  live_simulation_switcher.py`）`switch_to_live` 要求注入 token_verifier（"生产接线=Owner
  签发的一次性令牌"），验签失败/空令牌→LiveSwitchError 停留模拟盘，留痕只存 sha256 前 12
  位指纹（L111-122）——**C4/C5 的 owner_token 校验应复用该模式**，并从"非空即真"升级为
  "secrets 常量时间比对（或 HMAC(advisory_id) 一次性令牌）"。

### 1.4 建议→拍板→执行链的断口汇总

sim_deviation（月判）→sim_governance（建议，print 即散）→**[断]** 建议包落档→**[断]** 告警
推送（AlertManager 假送达）→前端拍板（S13 未建）→**[断]** owner_token 无签发校验→FSM
sim→production 无执行器（intake 只到 sim）。

## 2 六向挖矿日志表

| 轮 | 矿脉（方向） | 动作与证据 | 判定 |
|----|-------------|-----------|------|
| R1 | ④后端：建议器解剖 | sim_governance recommend L68-77/main L93-98 仅 print/docstring L23 漂移；sim_promotion_memo 事件线（S10） | **signal** |
| R2 | ④后端：AlertManager 全貌 | alert_manager.py L73-106 纯内存；alert_if_degraded（sim_platform_journal L87-97）fire-and-forget=假送达 | **signal**（关键） |
| R3 | ②下游/③机制：推送通道盘点 | data/alerter.py 真通道（飞书+SMTP+failures 文件）；alert_senders 注入式待启用；NotificationRouter 无生产装配；l6_feishu_alert 不丢模式 | **signal** |
| R4 | ③机制：owner_token 全貌 | lifecycle_fsm L76-81 非空即真；无签发无密钥；intake 只驱 candidate→sim；MOD-EX-035 token_verifier+sha256=可复用生产门 | **signal** |
| R5 | ①上游：建议证据三路源 | SIM-DEV 判定史（strategy_screen）+sim_memo 月报+bt-fw-* 整装证据（CTR-P1-017） | **signal** |
| R6 | ③机制（外部）：审批工作流 | four-eyes 原则（flagsmith.com/blog/what-is-the-four-eyes-principle，访问 2026-09；help.sap.com four-eye workflow，访问 2026-09）；OMS 治理证明惯例（limina.com，访问 2026-09） | **signal** |
| R7 | ③机制（外部）：下单授权分层 | Futu OpenAPI 模拟户免解锁/实盘户需 unlock_trade 两层门（openapi.futunn.com/futu-api-doc/en/trade/unlock.html，访问 2026-09）——与本项目"模拟自动、实盘令牌"同构 | **signal** |

轮次判定：7 signal / 0 noise。三问全部有答案，封批转施工。

## 3 业界与开源对照

- **审批工作流**：four-eyes/maker-checker 原则=关键动作至少两人复核（Flagsmith/Devolutions，
  URL 见 R6；SAP 给出工作流配置形态：发起→第二人独立核验→生效）。本项目 Owner 一人兼任
  发起链与终裁，无法真四人——业界等价物=**机器准备证据包（maker=机器）+人终裁（checker=
  Owner）+令牌授权+全程留痕**，与 C4/C5 设计一致。
- **OMS 治理证明**：Limina/Charles River（URL 见 R6）把"给投资人的治理证明"列为 OMS 一等
  公民——对应本项目审批台账（advisory→decision→执行回执）必须落档可检索，不能止步于告警。
- **授权分层**：Futu unlock 两层门（URL 见 R7）验证本项目 LiveSimulationSwitcher"模拟自动、
  实盘令牌"的分层正当性；IBKR 把安全锚在网关会话层（2FA 一次、下单免密，interactivebrokers
.com/docs/tws-api/doc/introduction，访问 2026-09）——本项目的 api_server 无会话体系，拍板
  令牌走"每动作一次"比"会话一次"更贴合现状且半径更小。

## 4 堵点与欠账清单

| # | 堵点 | 证据 | 后果 |
|---|------|------|------|
| 1 | sim_governance 输出即蒸发 | main L93-98 仅 print；无 run 档案（docstring L23 漂移） | 建议无人看见，判定史白攒 |
| 2 | AlertManager 假送达 | 纯内存 L75；alert_if_degraded 即弃 | 平台日刊的"告警"从未送达过任何人 |
| 3 | owner_token 无签发无校验 | lifecycle_fsm L76-81 非空即真；secrets.py 无键 | 任何带非空字符串的调用都能过 FSM 门；前端拍板无合法凭据可带 |
| 4 | 建议-拍板间无统一建议包载体 | sim_memo 与 governance 两线平行；整装证据第三路未合流 | Owner 拍板缺一份完整证据卷宗 |
| 5 | FSM 无 paper 态承接 promote_paper | lifecycle_fsm L48-52 五态（S10 §1.4） | 建议词表无 FSM 边落点 |
| 6 | NotificationRouter 无生产装配 | grep 无实例化 | 多通道路由/静默/升级能力停纸面 |
| 7 | 审批台账无存储 | 无 advisory/decision 表或档案目录 | 拍板后证据链断，治理证明缺失 |

## 5 施工项建议（C4 转正建议生成+推送方案雏形）

1. **统一建议包生成器 `scripts/backtest/promotion_advisory_builder.py`**（新件，只读聚合）：
   输入三路——sim_governance.recommend 判定史、sim_promotion_memo 月报（若已产出）、
   最近一次 bt-fw-* 整装证据（读 data/backtest_artifacts 最新产物+panel_reconciliation）；
   输出 `docs/_working/pipeline-research/promotion-advisories/advisory-<SID>-<YYYYMM>.json
   +.md`（safe_write_text CAS 落盘），字段=advisory_id/strategy_id/当前 lifecycle_status/
   建议(promote_paper|promote_production|demote_decayed|hold)/证据指针（screen 批次+memo
   路径+bt-fw 产物名）/生成时间。验收=给定 SIM-DEV 两期判定史重放生成零 diff；无建议策略
   不产包。
2. **推送接真通道**：builder 末尾对"有流转建议"的包调 `data/alerter.Alerter.notify`
   （level=ERROR 级触达飞书；消息体=advisory_id+SID+建议+前端页 hash `#promotion`）；
   同时写一条 data/failures/*.json 类台账文件作站内真源。**不动 AlertManager**（其假送达
   问题另开小票修复：给 alert_manager 补可选持久化 sink 或降级标注）。
   验收=未配 webhook 时静默跳过不抛（alerter 原语义）；配 webhook 后 Owner 手机收到建议。
3. **owner_token 签发/校验（必答①落地）**：secrets 增键 `ZEPHYR_OWNER_APPROVAL_TOKEN`
   （.env，Owner 私有）；校验件 `zephyr/strategy_pipeline/owner_token.py` 新增
   `verify_owner_token(token, advisory_id) -> bool`——常量时间比对
   `HMAC(ZEPHYR_OWNER_APPROVAL_TOKEN, advisory_id)` 前缀或整串比对；`OwnerTokenGuard.check`
   升级为调该校验（保持机器不带 token 必拒）；留痕只存 sha256 指纹（抄 MOD-EX-035 L111-122）。
   验收=错 token/空 token/重放他单 advisory 的 token 全拒；单测覆盖。
4. **事件接线**：pipeline_events 增 kind `promotion_advisory_due`，在 S10 的
   `sim_deviation_monthly` handler 之后串行触发（判定史先落、建议后出），复用月度 marker
   与重 kind 子进程模式（S10 §5.1-5.2 同款）。
5. **与 S13 的接口契约**：advisory JSON 即 API 真源（`GET /api/promotion-advisories` 直接
   扫目录）；拍板端点见 S13 §5.2——C4 只保证"包在盘上+告警送达"，C5 保证"看得见+拍得了"。
6. **远期登记（不在 C4）**：NotificationRouter 生产装配（多通道+静默窗+ack 升级）；
   FSM paper 态统一（S10 §5.3 承接）。

## 6 封矿结论

- 矿脉层面：7 signal/0 noise，建议器、告警通道、owner_token、证据源、外部对照五向闭环，封批。
- 方案层面：C4 = 建议包生成器+真通道推送+owner_token 签发校验三件，全部复用现成件
  （alerter/secrets/MOD-EX-035 模式），无新规范对象；消灭"人肉跑 governance+人肉汇总证据+
  建议无人知晓"三段人工，终局有位，**施工**；NotificationRouter 装配与 FSM 词表统一
  **挂起排期**（解锁条件=C4 单通道稳定运行一个月 / S10 施工 3 落地）。
- 一句话结论：**告警的真通道是 data/alerter（飞书/SMTP）而非 AlertManager（纯内存假送达）；
  owner_token 目前只是"非空即真"的门闩，C4 必须把它升级为 secrets 绑定的一次性令牌校验，
  否则前端拍板（S13）无合法凭据可带。**

## 7 施工班状态回填（2026-09-15）

- 建议包 builder✅：三路证据合流（SCR-SIMGOV/SIM-DEV 偏离/bt-fw-auto 整装证据+sim_memo 指针），hold 不产包，safe_write 幂等。
- 推送✅（真通道=data/alerter）：管线告警全量接 Alerter（7f57726331）；飞书 webhook/SMTP 双通道内建于 Alerter.notify_channels，**Owner 凭据未配=当前降级本地告警文件**（Alerter 原语义，不抛异常）。
- owner_token✅：secrets 键 ZEPHYR_OWNER_APPROVAL_TOKEN（secret_registry 106→107，4cb9d58dd7；密钥本体仓根 .env，gitignore 覆盖已验）；校验=sha256 常量时间比对+未配置 fail-closed+非字符串 token isinstance 拒（红蓝加固）；decide 台账只存 token 指纹前 12 位。
- 新增（挖矿未预列）：decide 头部 KillSwitch 总闸（红蓝发现#1——最敏感流转反无总闸，对齐 intake 同款 fail-closed 探针）。
- §4 堵点状态：1/2/3/4 已解；5（FSM paper 态）维持挂起；6（NotificationRouter 装配）维持挂起；7（审批台账）已解（decision 台账在 decide 链内落档）。
