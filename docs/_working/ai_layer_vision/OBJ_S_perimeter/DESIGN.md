---
ttl: task_bound
title: OBJ_S 红线与自由域——真源设计稿 v1（负面清单机检化+删除分级+安全度量+双指标看板）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# OBJ_S 红线与自由域——真源设计稿 v1

> **一句话**：把主文档附录 C 六条"永不触碰"逐条细化成可机检规则，把删除红线三档点名到
> 真源生成器，把"项目安全"和"不亏钱"变成两个有数据源的仪表，红线之外全自由。
> 上游客源=主文档 v2.0 §0.5 定调 #13+§五+附录 C；本卡骨架=[README.md](README.md)。
> **不发明新刹车**：本稿全部机检点优先复用已有闸（immutable_core/KillSwitch/五级交易熔断/
> RULE-GIT-SAFE/REGISTRY-MASS-DELETION），新建件仅补"已有闸没覆盖的缝"（见 §4 施工清单）。

## 0. 设计总原则（四条）

1. **负面清单是治理层资产**：清单内容（红线语义）归 Owner（变更走 OBJ_R 四步流水线）；
   清单的机检实现（gate 代码/探针）=普通代码域，AI 可自动迭代。尺与持尺分离。
2. **机检优先静态判据**：每条红线必须落到"文件路径/键名/SQL 模式/字段 diff"级别，
   禁"直觉判断型"规则；清单本体禁手写条目计数（§2 禁删清单一律生成器产出，AGENTS §9.5）。
3. **fail-closed 与 fail-open 分界**：红线检查点（负面清单命中）=硬阻断；安全探针
   （§3 告警链）=告警+降档，不阻断业务。与 risk_tier_registry"fail-open 分级、
   fail-closed 门禁"同构。
4. **两个 KillSwitch 勿混用**（P1-2 职责边界澄清在案）：AI 行为红线违例→
   `zephyr.security.access_control.kill_switch`（record_event，进程内存态）；交易资金异常→
   `zephyr.trading.trading_contracts.risk.trading_kill_switch`（五级，独立级联+持久化）。
   OBJ_S 两边都接，但各走各的，不交叉调用。

---

## ① 六向寻路台账表

| 向 | 矿脉 | 判定 | 关键产出（真实路径/键名） |
|----|------|------|--------------------------|
| 1 上游客源 | 主文档 v2.0（§0.5 定调 #8/#9/#13+§四+§五）+骨架 README 三轴+OBJ_S 卡 | signal | 附录 C 六条=本稿细化对象；"四必须留人底线"=付费/实名/转正/密钥知情 |
| 2 治理与门禁 | risk_tier_registry（REG-RISK-TIER-001）/immutable_core（MOD-SEC_IMMUTABLE_CORE）/git_safety_wrapper/REGISTRY-MASS-DELETION | signal | high 九域四门位；24 条 always_blocked_operations+protected_paths fnmatch；禁 reset --hard/push --force/filter-branch/reflog expire；mass-deletion 闸 priority=140 own_scope |
| 3 安全与密钥 | kill_switch.py（AI 行为）/trading_kill_switch（交易五级）/secrets.py（MOD-INF-016）/secret_registry.yaml/SECRETS.md | signal | KillSwitch 9 触发器（audit_log_tamper threshold=1）；五级=POSITION_LIMIT/DAILY_LOSS/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT；实盘键现名 QMT_REAL_PATH/QMT_REAL_ACCOUNT（config/.env.qmt）vs 模拟 QMT_SIM_* |
| 4 数据与账本 | sim_paper_ledger（scripts/backtest/）/DatabaseService（MOD-INF-002）/audit_key_eras.yaml | signal | 回撤数据源=c1_backtest.sim_pocket_daily（日账）+c1_backtest.sim_trade_log（事件溯源，rebuild() 可全量重建）；HMAC 分期真源=audit_key_eras+IntegrityVerifier.verify_chain |
| 5 资源与运营 | resource_optimization.yaml（MOD-INF-002）/budget_policy.yaml（MOD-INF-024）/ROOR | signal | 四级降级链（warning/critical/emergency 阈值+hysteresis：confirmation_count=2/cooldown 60s/振荡保护 3 次/时）=降档联动照抄先例；预算软硬限+分级动作已有口径 |
| 6 外部对标 | （可选向，未新搜）V0-V2 报告在档复用 | 在档复用 | MAPE-K 内监=§3 探针周期；Champion/Challenger 降档=§4 便宜模型顶上。内部矿脉全 signal，四闸交叉验证已满足，零新增搜索不判查无 |

---

## ② 真源设计

### §1 负面清单 v1 定稿——附录 C 六条逐条机检化

> 每条四元组：**红线语义 / 违规判定技术判据 / 检查点位置 / 违例动作**。
> 编号 NL-1…NL-6 与附录 C 顺序一致，机检输出统一 `negative_list.rule_id` 留审计。

**NL-1 付费动作**（资金流出唯一确认人=Owner）

- 违规判据：①`config/secret_registry.yaml` 全表不存在任何支付通道凭证键（AI 不持支付
  凭证是结构性前提，年审复核项）；②AI 会话运行时命中支付确认页特征（URL/页面指纹含
  checkout|cashier|pay.confirm|验证码+金额同页），或对浏览器会话发出"提交支付表单"类指令；
  ③任何会话试图绕过"备料+推送"直接完成下单提交动作。
- 检查点：运行时 KillSwitch `register_trigger(TriggerDefinition(trigger="payment_confirm_action",
  default_threshold=1))`（新建注册，一触即断）；浏览器自动化层前置检查（OBJ_T 施工时接线）。
- 违例动作：BLOCK_AGENT（单会话阻断）+审计事件+前端通知 Owner。AI 侧正确姿态=充值预警
  备料（建议额+直达链接推前端），支付按钮永远留人（主文档 §四.2）。

**NL-2 实盘资金凭证**（AI 会话环境永不发放实盘 API/QMT 实盘密钥）

- 现状锚点（已挖实）：`config/secret_registry.yaml` 中实盘键=**QMT_REAL_PATH**（category=config）、
  **QMT_REAL_ACCOUNT**（category=credential），均在 `config/.env.qmt`；模拟键=QMT_SIM_PATH/
  QMT_SIM_ACCOUNT 同文件。`_REAL_`/`_SIM_` 命名分野已存在，隔离有现成抓手。
- 违规判据：①AI 会话进程环境变量命中禁发名单（`QMT_REAL_*` 前缀 + `ZEPHYR_AUDIT_HMAC_SECRET`
  + 未来注册的 `*_LIVE_*` 键）=违例；②AI 会话 own-diff 中出现 `QMT_REAL` 字样引用
  （源码/脚本/配置/文档）=违例；③实盘未开通期间 registry 中 `required: false` 且值为空——
  若发现 AI 会话 env 中出现非空 `QMT_REAL_*` 值=最高级违例（泄密事故，§3 SEV-3）。
- 检查点：①会话启动器 env 白名单（新建，施工项 S1：AI 会话 spawn 时对 env 做 deny-list
  过滤，deny=`QMT_REAL_*`/`ZEPHYR_AUDIT_HMAC_SECRET`/`*_LIVE_*`）；②own-scope 提交闸
  （新建，施工项 S2：GATE 实名 `REAL-KEY-REFERENCE-SCAN`，扫 own-diff 中 `QMT_REAL`
  引用，白名单仅 secret_registry.yaml 本体与 SECRETS.md 文档行）；③年审：registry 新增键
  时机械核对 category=credential 的实盘键必须带 `_REAL_`/`_LIVE_` 命名（补列进 §6 年审单）。
- 违例动作：闸拦=阻断提交；env 命中=拒绝启动该会话+审计；值泄露=KillSwitch 全局熔断建议
  +Owner 立即轮换（secrets.py sanitize 纪律：任何日志只出现 `***REDACTED*** (len=N)`）。

**NL-3 宪法权限语义**（宪法正文与规则 YAML 权限语义，Owner 门位+等长替换）

- 违规判据：①写目标命中 `config/immutable_core.yaml` protected_paths
  （AGENTS.md / project_rules.md / docs/01_policies_and_standards/rules/** / _registry/** 等，
  is_protected_path fnmatch 判定）且无 Owner 裁定关联=违例；②AGENTS.md 修改后行数>300
  （宪法 ≤300 行硬上限，等长替换的机械面）=违例；③修宪 commit message 无 ruling_registry
  裁定号引用=违例。
- 检查点：immutable_core（已有，运行时）；宪法行数核对（已有规则，施工项 S2 顺带把它
  从"纪律"落成 gate 断言）；commit message 裁定号核对（GW POST 链已有 forged 标记纪律）。
- 违例动作：拒绝写+提示"AI 只有提案权，走 OBJ_R 四步流水线（提案→治理立案→Owner 修标
  →重考历史）"；破改未遂计审计。

**NL-4 审计链**（events.jsonl 及 HMAC 密封逻辑）

- 现状锚点（已挖实）：HMAC 分期真源=`config/audit_key_eras.yaml`（era 边界+过渡窗 0
  收窄，裁定#287）；验证器=`zephyr.gov_audit.integrity.IntegrityVerifier.verify_chain`；
  密钥键名=**ZEPHYR_AUDIT_HMAC_SECRET**（.env）。
- 违规判据：①操作名命中 immutable_core always_blocked_operations（delete_audit_trail/
  reset_audit_trail/delete_audit_logs 已列）=违例；②非 AuditWriter 进程向审计链文件追加/
  改写=违例；③AI 会话 env 出现 ZEPHYR_AUDIT_HMAC_SECRET=违例（NL-2 白名单同一闸）；
  ④verify_chain 出现 mismatch（非 known_loss era）=审计断链事故（§3 SEV-1）。
- 检查点：immutable_core（已有）+ KillSwitch `audit_log_tamper` trigger（已有，
  threshold=1 全表最高灵敏）+ env 白名单（新建 S1）。
- 违例动作：threshold=1 即 BLOCK_AGENT；≥3 agent 被阻自动全局 TRIPPED（KillSwitch 原生
  级联）；mismatch=SEV-1 告警链（§3）。

**NL-5 验收判据自改**（施工会话无权改自己的判据）

- 违规判据：同一会话 own-diff 中同时包含 ①施工产物文件 与 ②该会话任务书
  （TO-*.yaml）的 `definition_of_done` / `red_lines` / `acceptance` 任一字段的结构性变更
  （YAML 解析级 diff，非字符串比对）。判据预注册后即锁定（主文档 §3.1）。
- 检查点：GitCommitGateway in-process 闸（新建，施工项 S2 合并实现，gate 实名
  `TASK-ORDER-DOCS-LOCK`，own_scope，与 REGISTRY-MASS-DELETION 同一挂载面）。
- 违例动作：阻断提交；判据变更唯一合法路径=独立复核会话出判据修订案或 Owner 改判
  （复核级/终审级协议，主文档 §3.2）。

**NL-6 删除红线三档** → 全量枚举见 §2。

### §2 删除分级全量枚举（三档+守卫闸对照）

> **机械判定总纲**：删没删看"真源是否失 dereference"。禁删对象清单一律生成器产出
> （AGENTS §9.5 静态清单禁手工维护），本节只点名**枚举真源**与**必须覆盖的类**。

**档 A：物理删除=Owner 门位**（risk_tier high 域 human_gate"注册表/真源条目净删行"已有）

| 类 | 枚举真源（不手工点名全表） | 必须覆盖的点名件 | 守卫闸 |
|----|---------------------------|------------------|--------|
| 生产库 | DatabaseService 接线清单（governance.db=sqlite DB_PATH / depgraph=PG / ClickHouse 全库 reader+writer 分角色 / redis）+ DDL 真源（schemas/ 与 ch schema 目录，施工项 S4 生成器输入） | governance.db；c1_backtest.sim_trade_log（事件溯源源，删=账本永不可重建）；c1_backtest.sim_pocket_daily（日账本体） | RULE-DATA-OPS 三步验证（已有）；**DROP-GATE（需新建 S3）**：own-diff 中静态扫描 `DROP TABLE|DROP DATABASE|TRUNCATE|DROP COLUMN` SQL→拦+Owner 门 |
| 注册表 | docs/registry_of_registries.yaml（ROOR）tier 0-2 全部 physical_path，施工项 S4 生成器产出禁删清单 | ROOR 本体；gate_registry.yaml；risk_tier_registry.yaml；secret_registry.yaml；immutable_core.yaml；audit_key_eras.yaml；ruling_registry.yaml | REGISTRY-MASS-DELETION（已有，CommitGate priority=140 own_scope）；REGISTRY-YAML-PARSE（已有） |
| 审计件 | audit 链路径真源=zephyr.gov_audit.integrity + audit_key_eras.yaml | .runtime 审计链文件（gate_audit/audit_jsonl 写面）；config/audit_key_eras.yaml；data/databases/governance.db | immutable_core always_blocked_operations 三条（已有）+KillSwitch audit_log_tamper（已有） |
| git history | .git/** + reflog | .git 全体（immutable_core protected_paths 已列 .git/**） | git_safety_wrapper（已有：reset --hard/--merge、push --force（无 --force-with-lease）、filter-branch/repo、reflog expire 全拦）+ RULE-GIT-SAFE |

**档 B：退役/墓碑=AI 自动**（老东西退役不删）

- 语义：deprecated 链墓碑法（在案）+ L6"A 组退役不删观察期"同一纪律；AI 可执行退役标记
  （状态位/墓碑注记），不可执行物理删除。
- 守卫闸：已有（gate 退役审计+触发率季度审计，宪法 §4.2）；墓碑统一标记约定列为核实项
  （施工项 S8 顺带核对各域 deprecation 字段一致性，不新建机制）。

**档 C：临时物=TTL 自动清**

- 语义：.runtime/tmp 24h、.runtime/sessions/&lt;sid&gt;/staging 24h TTL（已有）；项目根目录
  零临时文件（运维红线已有）。守卫闸：已有（reaper+TTL 清扫）。AI 享有"造临时物"自由，
  无需审批——这是负面清单制的正面样本。

### §3 "项目安全"可度量定义（四类安全事件→告警链→自动动作）

> **可度量定义**：项目安全 = 四类探针在观察窗内**开放（未处置）安全事件数 = 0** 且
> 审计链验证绿（verify_chain mismatch=0，known_loss era 除外）。这是 OBJ_S 对定调 #13
> "项目安全"前提的操作化——不可度量即不可守护。

| 分级 | 事件类 | 信号=不安全（探针位置，全部已有模块） | 自动动作 | 上行 |
|------|--------|--------------------------------------|----------|------|
| SEV-1 | 审计断链 | verify_chain mismatch&gt;0（非 known_loss）；audit writer 停写超窗（排班告警监测）；audit_key_eras era 覆盖缺口 | 停写类操作降级只读；纠察行使熔断建议权 | KillSwitch manual_trip_global（建议）+前端 Owner 通知 |
| SEV-2 | 资金异常 | trading_kill_switch 五级任一 trigger()=True（POSITION_LIMIT/DAILY_LOSS/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT 原生条件）；模拟盘组合日回撤越 §4 降档线 | **五级熔断原生动作**（REDUCE_ONLY/CANCEL_ALL+DISABLE_NEW/DISCONNECT/FULL_SHUTDOWN/AUTO_KILL——不发明新刹车） | 告警+前端；解锁=Owner（资金域 high 门位） |
| SEV-3 | 权限逃逸 | immutable_core protected path 拒绝计数异常升；KillSwitch permission_boundary_probe 达阈值；env 白名单外密钥访问尝试（S1 白名单拒绝日志）；NL-2 命中 | BLOCK_AGENT（KillSwitch record_event 原生级联：≥3 agent→全局） | 前端 Owner 通知+审计 |
| SEV-4 | 数据损坏 | check_tick_duplication 判重异常率越限；CH 写失败率越限；sim 账本自愈校验不一致（sim_trade_log rebuild() 重算 vs sim_pocket_daily 现值 diff） | 停写+走 restore 流程（档 B 墓碑/备份可回切） | 告警+Owner；RULE-DATA-OPS 三步验证复盘 |

- 告警通道：复用 config/alert_rules.yaml + ops_alert_feed（resource_optimization.yaml §
  ops_alerting 已有兜底先例）+前端面板；SEV 探针周期对齐 MAPE-K Monitor（在档先例）。
- 本节**零新建刹车**：四类信号全部挂已有模块输出，新建件只有"聚合+分级路由"（施工项 S6）。

### §4 "不亏钱"双指标看板设计

> 定调 #13 两个前提之一。看板=日刷新双列：日运行成本 × 模拟盘组合回撤；
> 任一越限→自动降档（不问 AI 意见）。

**指标 1：日运行成本**

- 数据源（按可得性分级）：①各渠道账单余额/用量 API（DEEPSEEK/GLM/OPENROUTER 等后台，
  充值预警"余额监控挂排班告警"先例直接扩展）；②兜底估算=LLM 网关遥测 token 用量×
  registry 单价（secrets.py CONSUMERS 中 infrastructure.asset_inventory.telemetry/
  llm_gateway 已在遥测链上）；③口径对齐 config/budget_policy.yaml（MOD-INF-024
  软/硬限+action_on_exceed 既有词汇，不另造预算语义）。
- 落点：AI 层成本日账新表（施工项 S5 建表走 DDL 真源正门）。

**指标 2：模拟盘组合回撤**

- 数据源（已挖实）：`c1_backtest.sim_pocket_daily`（策略钱包日账，sim_daily/replay_demo
  幂等替换写）——组合日回撤=Σ 各钱包 equity 对组合高水位的回撤；事件流
  `c1_backtest.sim_trade_log` 兼作对账真源（rebuild() 可重建，数据可信度有锚）。
- 策略不碰真钱（模拟盘先行+实盘密钥物理隔离）在案，本指标是"不亏钱"在 AI 层的代理量尺。

**越限降档联动（阈值沿用 resource_optimization.yaml 先例结构）**

| 档 | 触发（任一指标） | 动作清单（按序生效） |
|----|------------------|----------------------|
| 注意 | 日成本>软线 或 组合回撤&gt;注意线 | 告警+看板黄灯（不停活） |
| 降档 | 日成本>硬线 或 组合回撤>降档线 | ①重活停（heavy 档任务暂停入队，L6 排产挂起语义）→②便宜模型顶上（OBJ_M 路由表降档 flash/fallback）→③挖矿暂停（L1 外扫/挖矿频次归零，配额池冻结增量） |
| 恢复 | 连续 N 日回线 + hysteresis | 按序逆向恢复；防振荡照抄先例三件套（confirmation_count=2 / cooldown / 每小时振荡上限 3 次） |

- **待 Owner**：软线/硬线/注意线/降档线的具体数值（金额与百分比）——Owner 定价权，
  AI 只建管道。建议随 OBJ_M 预算分析首月数据后定标。
- 阈值真源落新 YAML（施工项 S5 一并落，命名 obj_s_degradation.yaml，热加载照抄
  resource_optimization 先例"mtime 变化下一监控周期生效"）。

### §5 自由域透明度周报（给 Owner 的可读格式）

> 负面清单制的对价=透明。AI 每周交一份"我用了哪些自由"报告，Owner 只看一屏。

```yaml
freedom_weekly_report:
  week_id: YYYY-Wnn
  free_domain_usage:        # 自由域实际使用（新增自动化能力，无需审批故全部留痕）
    - {capability: 一句话, first_used: date, runs: N, domain: D_XXX}
  near_miss_events:         # 擦边：负面清单检查 warn 命中但未构成阻断
    - {rule_id: NL-x, what: 一句话, why_warn_not_block: 判据说明, count: N}
  negative_list_hits:       # 机检阻断计数（by rule_id 汇总）
    - {rule_id: NL-x, blocks: N}
  quota_consumption:        # 配额池实际 vs 配额（token/GPU 档/提交数/子代理槽）
    - {resource: llm_token, used: N, quota: M, pct: 0.xx}
  sev_incidents: {sev1: 0, sev2: 0, sev3: 0, sev4: 0}   # §3 四类开放事件
  owner_calls: N            # Owner 本周被叫次数（终局校验 KPI ≤4，主文档 §六）
  degradation_events: N     # 双指标降档触发次数与档位
  next_week_proposals: []   # 下周想新增的自由（自动过负面清单预检后才上会）
```

- 生成=施工项 S7（生成器产出，禁手工写）；交付=前端面板段落+md 双格式。

### §6 负面清单年审机制（挂 OBJ_R 标准流水线）

- **挂接**：负面清单本体=治理层标准库资产，年审走 OBJ_R 四步流水线原样：
  AI 年审报告提案→治理立案→Owner 修标→重考历史（新清单对历史拦截集重放，
  误拦率不升才准换）。红线语义变更零直改。
- **年审输入（三个探测口）**：①年内人工紧急叫停/KillSwitch 触发事件全归类——同类≥2 次
  而负面清单未列=**事实红线候选**（应有而未列→补列提案）；②near_miss warn 高频模式
  （≥阈值/季）=判据细则化候选；③清单条目机检连续 4 季度零触发=退役审计候选
  （净删=Owner 门位，宪法 §4.2 对齐）。
- **年审固定核对项**：secret_registry 新增实盘键命名合规（NL-2）；protected_paths 与
  宪法/规则真源一致性（NL-3）；HMAC era 覆盖完整性（NL-4）；禁删清单生成器 freshness（NL-6）。
- 产出=`negative_list_annual_review` 立案包→ruling_registry 关联→清单 v(n+1)。

---

## ③ 接线图（与既有件的契约）

```
                    ┌──────────────────────────────────────────────┐
                    │ OBJ_S 负面清单机检面（NL-1..6 闸+白名单+探针）  │
                    └───────┬──────────────┬───────────────┬───────┘
          红线语义变更(修宪笔)│              │降档指令        │违例事件
                    ┌───────▼──────┐ ┌─────▼─────────┐ ┌───▼────────────┐
                    │ OBJ_R        │ │ OBJ_M 路由表   │ │ KillSwitch(AI) │
                    │ 四步流水线    │ │ 降档 flash/    │ │ record_event   │
                    │ (提案→立案→   │ │ fallback 档    │ │ (内存态,9触发器)│
                    │  Owner 修标→  │ │ +成本审计三把尺 │ │ payment_confirm │
                    │  重考历史)    │ │ 回供看板数据    │ │ 等新 trigger 注册│
                    └───────┬──────┘ └─────┬─────────┘ └───┬────────────┘
                            │              │               │≥3 agent→全局 TRIPPED
                    ┌───────▼──────────────▼───────────────▼────────────┐
                    │ L6 切换段：pause_lane/resume_lane（重活停/恢复）      │
                    │ trading_kill_switch 五级（SEV-2 专用，勿与上混用）    │
                    └───────────────────────────────────────────────────┘
```

- **OBJ_R 契约**：OBJ_S 拥有红线"内容定义+机检实现"，OBJ_R 拥有红线"变更流程"。
  OBJ_S 年审报告（§6）与清单修订提案一律以 OBJ_R 立案包形式提交；OBJ_S 不得因机检
  实现迭代而偷改语义（语义 diff 审查=治理立案环节）。
- **L6 契约**：降档动作"重活停"=调用 L6 排产挂起语义（B 组暂停≠删除，档 B 纪律互通）；
  L6 恢复窗口受 §4 hysteresis 约束。OBJ_S 不绕过 L6 直接停具体任务。
- **OBJ_M 契约**：看板发 `degrade_model_tier` 事件→OBJ_M 路由表切 fallback（champion→
  flash）；OBJ_M 成本审计三把尺（能力考试/双跑/成本）回供看板指标 1 单价口径。
  双向只走事件与路由表，不直改对方状态。
- **KillSwitch 契约**：NL-1/NL-3/NL-4/NL-5 违例与 SEV-3 信号→`record_event(TriggerEvent)`；
  新 trigger（payment_confirm_action 等）走 `register_trigger` 注册。已知局限成文：
  KillSwitch 纯进程内存态、进程崩归零——故 OBJ_S 的持久防线=闸（immutable/gate 体系）
  +审计链，KillSwitch 只是运行时加速断路器，与 P1-2 澄清一致。

## ④ 施工项清单（8 项，待开单；本稿零代码零配置改动）

| # | 项 | 内容一句话 | 依赖/门位 |
|---|----|-----------|----------|
| S1 | 会话 env 白名单启动器 | AI 会话 spawn 时 deny `QMT_REAL_*`/`ZEPHYR_AUDIT_HMAC_SECRET`/`*_LIVE_*`，拒绝即审计 | medium |
| S2 | 负面清单 gate 组 | `REAL-KEY-REFERENCE-SCAN`（own-scope 扫 QMT_REAL 引用）+`TASK-ORDER-DOCS-LOCK`（判据字段锁定）+宪法行数断言，挂 GitCommitGateway | medium（gate 新建走 own-scope 纪律） |
| S3 | DROP-GATE | own-diff 静态扫描 DROP TABLE/DATABASE/TRUNCATE/DROP COLUMN→拦+Owner 门 | medium 实现+high 触发后果 |
| S4 | 禁删清单生成器×2 | 从 DDL 真源产生产库禁删表清单；从 ROOR 产出注册表禁删清单；输出 freshness 进年审 | low |
| S5 | 双指标看板数据链 | 成本日账表+sim 回撤探针+obj_s_degradation.yaml 阈值真源（热加载照抄先例） | low；阈值数值=**待 Owner** |
| S6 | SEV 探针聚合路由 | 四类安全信号聚合分级→告警链+自动动作+Owner 通知 | medium |
| S7 | 透明度周报生成器 | §5 schema 落生成器，前端面板+md 双输出 | low |
| S8 | 年审流水线挂接 | §6 三探测口+固定核对项落 OBJ_R 立案模板；顺带核对墓碑标记一致性 | low |

## ⑤ 挖矿日志+自审闸三态裁定

| 轮 | 矿脉 | 判定 | 备注 |
|----|------|------|------|
| S-R1 | 上游三源（主文档 v2.0/骨架 README/OBJ_S 卡） | signal | 附录 C 六条+§四§五全量吸收 |
| S-R2 | risk_tier/immutable_core/git_safe/mass-deletion 闸 | signal | 删除档 A 四类守卫闸三个已有、一个需新建 |
| S-R3 | 双 KillSwitch+五级熔断职责边界 | signal | P1-2 澄清直接引用，§0 原则 4 成文 |
| S-R4 | secrets 键名考古（QMT_REAL_*/QMT_SIM_*/ZEPHYR_AUDIT_HMAC_SECRET） | signal | NL-2 隔离有现成命名抓手；零密钥值入档 |
| S-R5 | sim_paper_ledger 账本结构 | signal | sim_pocket_daily+sim_trade_log（事件溯源可重建）=回撤指标真源 |
| S-R6 | resource_optimization 降级链+budget_policy 词汇 | signal | 降档三件套（hysteresis/热加载/软硬限动作）全部照抄先例 |
| S-R7 | 外部对标（可选向） | 在档复用 | V0-V2 引文（MAPE-K/Champion-Challenger）够用，未新搜 |

**自审闸三态裁定：PASS（全绿）**

- 真源可施工性：8 施工项全部有已挖实锚点（键名/表名/闸 ID/先例文件），无臆造路径——过。
- 硬边界遵守：仅写 OBJ_S_perimeter 目录内 2 文件；零代码/零配置/零注册表改动；零 git；
  零 token 登记；零密钥值入档（仅键名）——过。
- 不发明新刹车：新建 8 项中 6 项为"聚合/扫描/生成器"性质，刹车动作全部复用五级熔断/
  KillSwitch/L6 挂起/OBJ_M 降档原生动件——过。
- **待 Owner 项（2 个）**：①§4 双指标软/硬线数值（金额+回撤百分比，建议 OBJ_M 首月数据
  后定标）；②secret_registry.yaml 是否增设 `ai_exposure: forbidden` 字段（registry 修改
  =Owner 门位；不增设则 S1 白名单 deny-list 为唯一机检面，功能等价、少一层结构保证）。


**验收标准补全（红蓝 R1-F4）**：S1 白名单=含 QMT_REAL_* 的环境在代理会话被拒且留证；S2 负面清单 gate=六条各有一条违例样例被拦的测试；S3 DROP-GATE=对禁删清单样例路径的 DROP 语句被阻断；S4 生成器×2=产出与 DDL 真源/ROOR 逐条一致（幂等再生）；S5 看板=双指标日更且数据源可追溯；S6 SEV 探针=四级事件样例各一可聚合成"开放事件数"；S7 周报=样例周报含自由使用/擦边/配额三节；S8 年审=流程挂 OBJ_R 流水线有登记。
