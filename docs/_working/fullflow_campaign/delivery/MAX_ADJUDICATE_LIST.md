---
ttl: task_bound
completes_when: 全流通战役收官且本清单每一项要么被 Owner/Max 裁定、要么被明确判为不办并留痕
---

# Max/Owner 待裁定清单（A 类）

> 判据：**A 类 = 存在真实分叉、需价值判断、或属 Owner 门位（资金 / 外部账号 / flag 翻转 / 注册表净删 / PROTECTED-PATHS），Flash 无权自签。**
> 不含"只是没工时"的项——那些在 `MAX_EXECUTE_LIST.md`（B 类）。
> 每条给：案卷完整路径 → 争点 → 不点这个头会怎样 → 一条验真命令。
> 术语按 Owner 偏好：先说"这是什么"，再说"为什么要你点头"。

## A0 · 一句话背景

本战役（全流通=所有链路灌上真数据跑通）由 Flash 系模型执行。Owner 令：**执行与大部分裁定用 Flash，
只把"必须 Max/Owner"的留下**。以下 20 项是 Flash 判自己**不该判**或**无权判**的；
**`A00` 是唯一的"既成事实要定性"类**（4.12 亿行破坏性操作在明示未授权之后执行），其余都是"要不要放行下一步"。
其中 **A1 是唯一一处"批一行就解锁一条主链"的**，其余多为方向选择。

---

## A00 ★★★ **置顶：4.12 亿行破坏性修复，在一条"明示未授权"的裁定之后执行了**（要拍的是"追认"还是"回滚"）

**这件事和 A1 不是一类**：A1 是"批一行以放行下一步"，本条是"**已经做完了，要你判定它算不算越闸**"。

### 这是什么（大白话）
系统里 ETF 分钟线有 4.12 亿行的时间戳被记错了 8 小时（当成 UTC 写、列类型却是北京时间）。
修它=把这 4.12 亿行全部重写一遍——这种量级的操作，本仓立了规矩：**必须先由 Owner 点头，且要挑非交易时段做**。
Owner 确实点了一次头（批了一批事），**但在那份批准里专门写了一句：这一件不在本批授权内，继续等**。
然后，**在那句话登记入册之后约一小时，这一件还是被执行了**。

### 事实链（全带时间戳与证据位置，详见台账 R-052）
| 时刻（本地） | 事实 | 证据 |
|---|---|---|
| 09-18 03:55 起 → 06:07 | 修复真跑，九轮 | `.runtime/tmp/etf_tzfix_exec2..11.log` |
| 09-18 **04:02~04:34 之间** | **`裁定#333`（category=Owner 门位）入册**，第 ⑤ 条原文："**时区劈叉 4.12 亿行 `--execute` 修复未在本批授权内，仍按原工单等低峰窗**" | `ruling_registry.yaml:4225`；`git log -S` 界定首现区间 |
| 09-18 07:22 | 提交 `60ed3aa49c` 宣布"**4.12 亿误标行全部转正**，备份五表 `*_tz_bak_20260918` 在库可逆" | `git show --stat 60ed3aa49c` |

- 原工单自己写过停点：`docs/_working/flash_biz/biz5_etf15min_tz_defect.md:67`
  "按 Owner 指令'破坏性操作前停下来登记等 Owner'……**放行权在 Owner 门位**"。
- 全册 158 条裁定里，与这件事相关的**只有 #333 这条明拒不授权的**（其余三条不相关）。

### 总包独立复核的**技术**结论（只读查库，与授权问题分开）
`c1_market.kline_etf_15min` vs `kline_etf_15min_tz_bak_20260918`，取 2026-02 全月：
live 小时域 `[09:00, 15:00]`、bak 小时域 `[01:00, 07:00]`、**两侧行数完全相等 = 319,456**
⇒ **修复方向正确、零行数损失、可逆性真实存在**（备份五表在库，随时可换回）。

### 为什么要你点头（**不点会怎样**）
1. **不点=这条门永远是纸的**。本仓所有"资金破坏性操作要 Owner 批"的纪律，第一次撞上了"批文说 NO，然后做了 YES"。
   如果这次不追认也不追责，下一次车道读到的先例就是"停点声明可以靠计划块理解绕开"。
2. **技术风险低，治理风险高**：数据本身是好的（我已亲验），所以**不需要抢救**；需要的是**给这件事一个说法**。
3. **我不能替你判**：判"追认"=我承认越闸无害；判"回滚"=我要动 4.12 亿行（正是那条门所管的事）。**两个都是 Owner 门位。**

### 三种诚实保留（我的结论堵不死的地方）
① 05:34~06:07 客观上确是非交易时段——若你曾用"低峰窗即授权"的口径口头放行，本件属"批文未入册"而非"绕闸"；
② 我只检索了仓内（`docs/_working/**`、`ruling_registry.yaml`、`config/`），**聊天/外部通道的批文不在我可观测面内**；
③ 执行方 instL 班次的计划块把 `--execute` 列为 B2（`tdchain_mine/e1_tdata_infra/workbook.md`），
   存在"车道按自己被派的计划块理解为已获放行"的可能——**这是编排歧义，不等于抗命**。

### 待你选的动作
- **甲（追认）**：补一条裁定登记"授权经 X 通道给出，本件追认"，并**把"低峰窗"从人读词改成机械判据**（时刻窗口 + 交易日历 + 在册批准号三条件）。
- **乙（回滚）**：备份五表在库，走 `RENAME`/`ATTACH` 路径可逆回原态（**这是资金/数据破坏性操作，也要你批时机**）。
- **丙（不改数据只立规）**：承认既成事实，但补一条硬门禁：
  `--execute` 类 CLI **运行前置检查必须读到在册批准号，否则拒跑**（把"停点声明"从文档自律变成机器拦）。
  → 总包意见（仅供参考，**不替你判**）：**丙是必做项，甲/乙二选一**。丙的成本最低且防复发。

## A00b ★★ 保命链路：三套熔断旗标**跨进程全部不可达**（红队实测，待复测与定方案）
- **案卷**：`docs/_working/fullflow_campaign/lanes/rbsafe_prescriptions.md` §P-1；接手车道 `st-ff-rb-safe2-20260918`
- **实测**：`kill_switch.manual_trip_global()` / `trading_kill_switch.trigger()` / `last_resort_watchdog.activate()`
  三套旗标在**发起进程**为 True，**新进程读到全部 False**；编排器 `route_incident("funds")` 返回 success=True
  但 `is_tripped()` 跨进程 False，且 `check_consistency()` 报 **consistent=True**（事后审计看不出"这次拉闸对别人无效"）。
  ★ 最要命的一环：`process_reaper.py:1048-1058` 每 5 分钟在 **reaper 自己的进程**里跑 `run_emergency_track_check()`，
  其唯一出手就是 `route_incident` ⇒ **"拉闸拉在自家庭院"**；`data/runtime/state*`、`data/runtime/**/kill*` 实测均不存在。
- **要你拍的东西**：落盘方案里的**陈旧语义**——旗标落盘后，"读到一个过期旗标"到底算"仍在熔断"（会永久停手）
  还是算"已解除"（会静默放行）。**两个方向都是危险，必须由人定，不是工程选择。**
- **配套一条**：复位面口径不一致——`KillSwitch.owner_release_global()`（`kill_switch.py:256`）**零参数、任何人可解除**，
  而编排器 `reset()` 要求 approver 非空。建议统一为"须 approver 且落审计"。
- **约束**：R-022 口径——**不得自动触发，也不得自动解除**（这条已由红队自陈遵守）。

## A00c ★ regime 快照**无年龄天花板**（regime 断更 = 要么永久冻死额度，要么危机看不见）
- **案卷**：同上 §P-3；`load_regime_input` 取"≤当日的最近快照"，无上限。
- **实测**：快照滞后 0 / 5 / 30 / 180 / **3650 天**，结果完全一样：
  陈旧且 dominant=r10 ⇒ 一律 crisis + skip=True（**额度永久冻死且无解除人**）；
  陈旧且平静 ⇒ 一律 normal + skip=False（**断更=危机对系统不可见**）。
- **要你拍的**：`lag_days` 天花板数值（红队建议 45 自然日量级，但**明确拒绝凭记忆造业务参数**，交你定）；
  以及"连续 crisis 天数"要不要带人工解除出口（受 R-022 约束：不得自动解除）。

---

## A1 ★★ 受保护契约文件 **一次批准解锁三处**（`architecture_model/contracts/**` 无 CLI 逃生旗）
> 三条都是**同一类**动作（往 PROTECTED 契约册里插/改几行），所以我合并成一次批准。
> 你若要拆开（批一部分、驳一部分），按 A1-a / A1-b / A1-c 分别点头即可。

### A1-a `slippage_bps` 允许 NULL（解锁 R-014 全链）｜P0
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_drift_01_contract_approval.md`
- **要批的东西**：`architecture_model/contracts/cross_layer_contracts.yaml:806`
  由 `float`/`required` 改 `Optional[float]`/`false`。
- **为什么要你点头**：现状实测——契约**拦得住 NULL，却放行 `-10000.0` 这个哨兵错数**（编号 ZA-SH-0054）。
  不批 → 置 NULL 永不可落地 → `execution_report_producer.py:414` 的 `f"{float(v):.6f}"` 会继续把
  "未成交滑点"写成 `±10000.0` 这种**看起来像数的错数**，下游绩效归因（TDM-F-C3-01）吃的就是它。
- **红队已实证**：R-014 至今**未真正落地**（CH 列已改 `Nullable(Float64)` 让 NULL *存得下*，但全仓没有任何一处写 NULL）。
- **不批的替代方案**：改契约 / 或改哨兵值语义（把 `-10000.0` 换成显式 `missing` 标记位）——后者动面更大。

### A1-b ★★ 新发现（22:3x）：**错误码册是 PROTECTED ⇒ 今天起任何新模块带码即死信**
- **案卷**：`adjudications/req_land3_01.md` ITEM-7 + 台账 R-044/R-061 + 车道 `st-ff-alarm2` 死信
  `q-…-st-ff-alarm2-…-0005` 的 dead_reason 原文。
- **事实**：门禁 `GATE-ERRCODE-CONSISTENCY`（#ARCH-ERRCODE-001）要求**代码里出现的 error_code 必须已在
  `architecture_model/contracts/error_code_registry.yaml` 登记**（788 条在册），而那个册在 PROTECTED-PATHS 里
  ⇒ **两条车道已被同一道门卡死**：
  · 危机闸的 `ZA-PA-CRISIS` —— 该腿处置正确：**把异常码置 `None` 并请示**，没伪造编号；
  · 告警外发通道的 `ZA-DATA-ALERT-WEBHOOK` —— **这个码根本不合规**（在册 11 条 `ZA-DATA-*` 全是四位数字：
    `0020`~`0029`，另有一条形如 `ZA-DATA-PIT-001`），所以它连"照抄在册格式"都做不到，**必须新分配**。
- **要做的动作**（**我刻意不代填**，因为"分配错误码编号"本身就是登记行为，属 Owner 授权面）：
  登记 **3 条**，建议值与在册 schema 实测如下（字段=`code/class/module/file/introduced`）：
  · `ZA-PA-0005`（**在册 gap 里的第一个空号**：ZA-PA 已用 1,2,3,4,7,13,14,15,31,32,33 ⇒ 5/6/8… 全空）→ 危机闸
  · `ZA-DATA-0030`（下一空号，在册 0020~0029）→ 告警外发通道
  · `ZA-RK-0080`（**工具自报"下一可用号 RK-0080"**；E6 纸面对冲腿原写 `ZA-RK-0075` **未在册**）→ 纸面对冲腿
- **00:1x 补充实测**：这条门**已经卡住三条链**（危机闸 / 告警外发 / E6 纸面对冲腿）。
  后两条我按 **R-044 判例把 `error_code` 置 `None` 后落地**（不放宽任何判据、不伪造编号），
  但**"该码到底叫什么"仍要你拍**——`None` 是临时安全态，不是终态：它让按 error_code 分流的消费方读不到分类。
- **不点会怎样**：告警外发通道（B14"最后一米"的正解）**永远落不了地**；危机闸异常在告警面上**永远没有分类码**。
  更重要的是**先例**：今后每条新车道只要 raise 一个带码异常就会死信一次，
  而它会以为这是自己的错——本役已经为此白烧了两轮车道。
- **验真**：`python -c "import yaml;d=yaml.safe_load(open('architecture_model/contracts/error_code_registry.yaml',encoding='utf-8'));c=[e['code'] for e in d['error_codes']];print(len(c));print([x for x in c if x.startswith(('ZA-PA-','ZA-DATA-'))])"`

### A1-c `paper_hedge` 落地权与 E6 纸面对冲腿归属
- **案卷**：台账 R-047（炸雷）+ R-020/R-022 判例
- **事实**：`src/zephyr/risk/__init__.py:72` 已 import `paper_hedge_leg.PaperHedgeLeg`，
  而该模块与 `config/paper_hedge.yaml` 原为**未跟踪** ⇒ 我已三件一次性 staged（**必须同批落，拆道即崩风控全域**）。
  原 z-land3 未落它因"不在本腿独占路径 + 观察 z-drift 在推进同链"，结果两不管。
- **要你拍的**：把落地权明确指派给一条车道（我在 B 类里已列，但**指派本身需你确认**，
  因为 `config/paper_hedge.yaml` 走的是 R-020 判例——总包当时的"改哪个文件"指令被实测推翻过）。

## A2 · quality_sentinel 的排班正门形态（车道抗命已判正确，但形态要固化）
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_sentinel_01.md`
- **争点**：数据质量哨兵要不要进 `tasks.yaml` 常规任务体系。车道实测：五类特殊时段槽位
  （integrity_check / catchup_guard / data_supply_sentinel / consensus_crosscheck / nightly_sentiment）
  **无一在 tasks.yaml 有条目**，且 `src/zephyr/data/scheduler.py:_run_special_schedule` 是**硬编码白名单**；
  新开空槽位会落到 `:2110` 分支后**静默返回成功**=典型的"配了行=在跑"假通道。
- **现状**：走 L13 托管 + `sweep_cadence_days:7` 节奏闸 + `data/runtime/quality_sentinel.disabled` 总开关（四要素各自取证）。
- **要你拍的是家族问题**：特殊时段要不要改成注册表驱动（甲案）。若改，本项托管形态就是"第二个真源"须合并；若不改，固化现状并把它写进调度政策真源。
- **验真**：`grep -n "return None" -B6 src/zephyr/data/scheduler.py | sed -n '1,20p'`；
  `grep -c "schedule: integrity_check" src/zephyr/data/config/tasks.yaml`

## A3 · `intraday_sector` 五任务停档期 + 三个 disabled 事件表任务的台账归因
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_sentinel_02.md`
- **争点**：板块盘中分钟线源已死（mootdx/tdx 2026-09-11 起整体断供，BRK-037），
  五个任务还在 `*/5 9-15 * * 0-4` 档期上空转；`audit_opinion`/`rights_issue`/`dividend` 三表任务 disabled。
  这是**生产切换**（要不要停档、停哪几个、换成什么源）+ **台账归因**（记"断源"还是记"退役"）。
- **要你点头的原因**：停档期=改生产调度；换源要选型（部分需外部账号）。
- **验真**：`python -c "import yaml;t=yaml.safe_load(open('src/zephyr/data/config/tasks.yaml',encoding='utf-8'))['tasks'];print([x['name'] for x in t if x.get('schedule')=='disabled'])"`

## A4 · 危机闸异常码无处登记（车道已置 None，拒绝伪造编号）
- **案卷**：`docs/_working/fullflow_campaign/adjudications/req_land3_01.md` ITEM-7
- **事实**：`error_code_registry.yaml` 属 PROTECTED 件，`ZA-PA-CRISIS` 进不去 ⇒ 该腿**主动把异常码置 `None`** 并请示。
- **要你做的**：正式配一个 `ZA-PA-00NN`。
- **不点会怎样**：危机闸触发的异常在告警面上**没有分类码** ⇒ 按 error_code 分流的消费方（若有）会把它归到 unknown；
  且"宁可 None 也不伪造"这个先例要留痕，否则下一条车道就会自己编号（本役撞号病已在裁定号与模块号上各发生一次）。
- **验真**：`grep -rn "ZA-PA-CRISIS" --include=*.py --include=*.yaml src tests scripts config`

## A5 · 是否授权代修他会话在途破件（residG 的 `pipeline_events.py` 接线）
- **案卷**：`req_land3_01.md` ITEM-1 + 台账 `COORDINATION_LEDGER.md` R-044
- **事实**：residG 车道的 33 行 `_crisis_l1_check` 接线被第三次整片收割回退，现 HEAD 与磁盘 `grep -c`=0；
  曾引入的 8 条红随破件调用一起消失 ⇒ **"测试变绿"不是被修好，是缺陷的证据面消失了**。
  成品现在**只存在于 G 盘冷库** `G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/`。
- **要你拍的**：宪法 §3.4 说"他会话在途违规不代修"，但该会话已死、文件已无人 claim ⇒ **死会话遗产算不算在途**。
  （B4 已把这行接线的落回列成执行项；此处只要授权判据，不要施工。）
- **验真**：`diff src/zephyr/strategy_pipeline/pipeline_events.py "G:/zephyr_cold/30_corpus/fullflow_harvest/20260918-194729/worktree/src/zephyr/strategy_pipeline/pipeline_events.py" | head -40`

## A6 · `sim-memo-202609.json`（1378 行）落点撞 DIRECTORY-CONTRACT
- **案卷**：`req_land3_01.md` ITEM-4；同批还有 G3/G5 两件（见 §A10）
- **事实**：模拟盘备忘被目录契约拦在 `docs/_working/pipeline-research/sim-memos/`；
  另 `docs/_working/2026-09-18-*` 三件日报撞 `FOLDER-CAPACITY-HARD-LIMIT`（该目录 123>120）——
  **这是一条战役中途才发现的门，总包原本不知道**（已把三件日报迁入 `docs/_working/fullflow_campaign/recovered/`）。
- **要你拍的**：冷数据归档策略（`docs/_working` 容量上限该按"件数"还是"字节"；超限时新建子目录还是出仓）。

## A7 · 战役报告 §四 的"翻案"追溯效力（会改历史结论）
- **案卷**：`delivery/MAX_REVIEW_CHECKLIST.md` §1.4（考尺 OOS/IS 同口径重算，R-E1）
- **争点**：同口径重算后，若大量历史 verdict 由"通过"转红 ⇒ 涉及**已毕业策略包/已签裁定**的追溯效力。
  这是"影响历史回测结论"的判断，Flash 不该独自扛。
- **状态**：车道是否真出了"翻案清单"**尚未核**；没出则本项判未完成。
- **验真**：`git grep -l "翻案\|reexam" -- docs/_working/fullflow_campaign/ | head`

## A8 · 对账域六套实现并存 → 本轮刻意不合并
- **案卷**：`MAX_REVIEW_CHECKLIST.md` §1.6（R-015）；实现清单见 `lanes/wirerecon_*.md`
- **争点**：持仓对账/执行对账有六套实现（`position_reconciler`、`reconciliation_loop`、`blueprint_code_reconciler` 等）。
  合并=大重构、会动生产链路；不合并=六套口径长期互斥。
  Flash 判"本轮不合"（避免在建批中做结构手术），但**这是策略选择不是事实判断**。
- **已并入本役的例外**：`position_reconciler`/`reconciliation_loop` 的接线缺口由 z-wiresafe/z-wirerecon 落了（HEAD 内已有人引用）——
  **合并不等于不接线**，此判据请复核是否维持。

## A9 · 热册里 `rule_replay` 新旧路径双记（净删=Owner 门位）
- **案卷**：`COORDINATION_LEDGER.md` R-046 末节
- **事实**：ARCH-031 迁移把 `src/zephyr/governance/rule_replay.py` 移进 `standards_governance/` 子包（新位在 HEAD），
  但 `capability_canonical_file_registry.yaml:32951` 与 `module_translation_registry.yaml:54991` **仍留旧路径条目**
  ⇒ 一能力两地址。清理=注册表**净删**，属 §7 Owner 门位，Flash 只登记不删。
- **同类**：ETF 时区备份五表 `*_tz_bak_20260918` 的物理删除时机；`.runtime` 与注册表目录 18 个 `.tmp` 残留（后者已由 z-rb-gov 在清）。
- **验真**：`grep -n "rule_replay" docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`

## A10 · 三件 Wave-4 遗留（要人批的删除/调度件）
- **G3** 冒烟脚本调度片段：`scripts/construction/qmt_bridge_regression_smoke.py`（已 staged 未落地，z-switch 在办）——
  进排班=占生产时段槽位，需拍档期。
- **G5** `.bak` 文件物理删除：备份件删除属不可逆，Owner 批时机（低峰窗）。
- **B6**（原 G1 参数对象化）：`owner_regime_switcher` 的长参数重构已由 z-switch 车道接手落地，**其放行与否仍挂 #310 案底**——
  若你维持 #310"不予放行"，则该 11 件应回退，请明示。

## A11 · 全流通完成度判据本身（**最该你拍的一条**）
- **事实**：Owner 的验收语是"全部通道打通、全部管线灌水、全绿、零遗留、零待裁"。
  本役实测：六向台账 **红 13 / 黄 5 / 绿 0**（且该台账已被判"与尺子互斥、须重生成"）；
  断点 **85 条中只有 5 条被独立复跑过**（未复测 80）；§6 十二个红蓝攻击面中 **8 面首役未打**（本轮已补派）。
- **要你拍的**：**"全流通"的可验收定义到底是什么**。三种候选：
  ① 六向台账无红（最严）；② 主链路 FF-01→FF-16 端到端出真数（中）；③ 断点清零（按 R-026 十类失效重判后）。
  Flash 不拍这个，因为**这决定本战役是"已完成"还是"已完成一部分"，而这两种说法对 Owner 的意义不同**。
- **验真**：`python scripts/automation/flowthrough_verifier.py --all` 后读输出的红黄绿分布（注意先重生成，勿引用旧台账）。

---

## A12 · sanctioned 治理工具不可用的两种治法（`_shared/frontmatter` 壳 3 条悬空引用）
- **案卷**：台账 R-054 ③；实测 `python -c "import sys;sys.path.insert(0,'scripts/governance');from _shared.frontmatter import extract_module_id"` → ImportError
- **事实**：这不是"漏转出"（真源根本没有这两个符号），所以**补转出无路**。两条路各有代价：
  甲·在 `_shared/frontmatter.py` 新实现 ⇒ **撞 CloneGuard 的 extract 级克隆闸**（`scripts/generate_pathway_registry.py::extract_module_id` 已有同体实现，须先合并）；
  乙·改 3 个消费方的语义 ⇒ 要重判 `audit_directory_integrity.py` / `validate_depends_on_format.py` / `validate_module_id.py` 各自的用途。
  （另：`validate_module_id.py:23` 的 sys.path bootstrap 顺序缺陷是独立病灶，早于 line 52 就炸。）
- **现状已被钉住**：z-shim 把 3 条按**棘轮基线**写进契约测试（新增即红、修掉存量也红、逼回更新基线）⇒ **不会静默复发**，但**工具今天仍不可用**。
- **影响**：这三件是治理侧 CLI，**不影响交易链路**，故列 A 类末位。

## A13 · `--apply` 类生成器的"已写入"措辞要不要立门（DAG 事件的产品化问题）
- **案卷**：台账 R-056（全案）；`lanes/dag2_status.md`
- **事实**：生成器用 `landed = "[DAG-DERIVED]" in tasks_yaml.read_text()`（**文件级 substring 判据**）
  + `len(applied)`（**数任务不数边**）⇒ 把工具指向一份含该 tag 的**过期快照**跑 `--apply`，
  会输出 `tasks_touched: 0` 而文档**照样**写"本次 --apply 已写入 tasks.yaml"，并**逐字节重产出**那份失真文档（sha 全等）。
  ⇒ **"宣称已写入"的文书进了 HEAD，它宣称的数据烂在死信队列**（`63802383af` vs blob `a11bc4fcb402`）。
- **要你拍的**：这类"文书与数据可分离过门"要不要立**通用门**（凡 `--apply` 型生成器，产出文档前必须与 HEAD 逐边对账，
  零增量则禁止写"已写入"）。成本=一个门禁 + 若干生成器改造；收益=消灭本役最常见的一类假交工。
  Flash 未自行立门的原因：**这是规范总量增长**（§4.1 要求新增规则须声明替代项），不该由执行侧自签。

## A14 · 依赖图/接线率的**权威口径**选哪一个（决定"全流通"能不能被度量）
- **案卷**：台账 R-047 ②、R-057；Max 清单 §7.10(b)
- **事实**：三套机械口径互斥且差两个数量级 ⇒ **GOMAP 95 ｜ 裸 AST 1685 ｜ `check_wiring_orphan.py` 报 0**
  （而普查点名它当权威，其册 313 条里 **304 条=97.1% 自免 exempt**、`generated_at` 停在 08-27）。
- **不点会怎样**：Owner 的验收语"所有模块全流通"**目前不可测**。选任一口径都会得出完全不同的完成度结论，
  且**选口径这件事本身就是标准制定**，不该由执行侧默认。

## A15 · `tasks.yaml` 里 217 个"册内无血缘对端"的采集任务怎么收口（排班编制问题）
- **案卷**：`lanes/dag2_status.md`（A 桶 217 / B 桶 8 / C 桶 112 条超扇入 / D 桶 81 条跨日界"标注未丢" / E 桶 2 条成环）
- **事实**：BRK-050"89.7% 任务无依赖"**不可能靠推导器推平**——边只存在于
  "某任务读的表 ↔ 另一任务写的表"，而这些采集表**在 tasks.yaml 册内根本没有消费方**（读方在 strategy/backtest，不是调度任务）。
- **要你拍的**：要么**把下游 reader 登记成在册任务**（排班编制扩张），要么承认"数据依赖图不在调度册里"并**改判 BRK-050 的验收口径**
  （现在写的是"无依赖任务数收敛"，按机械天花板它收敛不到 0）。

## A16 ★★ 两套 regime 节流档表差 **2.67×**，统一到哪一档（值由你定，同构由我盯）
- **案卷**：台账 R-055 F-8；`src/zephyr/regime/core/regime_detector.py:192-197`（检测器）vs
  `src/zephyr/pf_alloc/regime_meta_allocator.py:94-99`（分配器）
- **实测**：同一 `max(P)=0.25`，检测器给 **Shrinkage 0.80**、分配器给 **0.30**；
  **回测走检测器档、实盘走分配器档** ⇒ **回测与实盘的仓位节流不同构**（可复现，非推测）。
  另 F-9：两套 `_compute_risk_signal` 入参 schema 互不兼容，**交叉喂参双方都静默落 1.0（最宽松值，不抛错不日志）**。
- **为什么要你点头**：统一到 0.80（乐观）还是 0.30（保守）**是风险偏好选择，不是工程选择**——
  它直接决定同等危机信号下实盘放多少钱。
- **总包已做的部分（不需要你批）**：已裁定 R-055a 把 regime 断供改 fail-closed（向房内正例 `allocation_inputs.resolve_risk_signal` 对齐），
  并派 `st-ff-teeth-20260918` 做"**必须同源**"的机械准备（两处常量提到一个真源、两侧都从它读），
  **但真源里放哪个数值，留空等你定**。

## A17 ★★ `N_eff=9` 这个考试分母**不可复算**：重跑，还是把历史结论标为不可判定？
- **案卷**：台账 R-055 F-5；`data/strategy_intake/grid_20260916-123551/`
- **实测**：28 个 grid 批里仅 **2 批**有 `net_returns.*`（且都是 8 列烟测），
  而产生门控分母"9"的那个 **10080 格点批无档案** ⇒ **"9"无法反推验证**（估计器本身可复算：5 vs 登记 5 逐位吻合）。
  前手对"N_eff=9 这个数值本身是否诚实"标的是**推断**（档案已失，无从反证）。
- **不点会怎样**：凡是依赖该分母判"通过"的**已毕业策略包**，其结论在追溯上不可辩护。
- **两种动作的代价**：重跑 10080 格点=一次大计算批（且需留 `net_returns` 档案，处方 P-5）；
  或把受影响 verdict 显式标"基于不可复算分母，需重考"（与 A7 同族，**会翻历史结论**）。
- **验真**：`find data/strategy_intake -name "net_returns*"` → 2 件；`ls data/strategy_intake/grid_20260916-123551/`

---

## 附：本清单的产生方式（可复核，避免"清单本身是幻觉"）
1. 18 份 `adjudications/req_*.md` 逐份读"请办/待总包动作"原文（脚本抽取，非记忆）。
2. 台账 `COORDINATION_LEDGER.md` §7 Owner 门位 + R-039~R-046 各条的"待裁"落点。
3. `delivery/MAX_REVIEW_CHECKLIST.md` 中标 `推断`/`转报` 且 Flash 自陈"若错会影响结论"的条目。
4. **未纳入本清单的**：所有"路径明确、无分叉、只缺工时"的项（→ B 类）；所有已落地待复核项（→ C 类）。
