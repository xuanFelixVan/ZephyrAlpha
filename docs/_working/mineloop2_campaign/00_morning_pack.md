---
ttl: task_bound
title: 矿考二班·开班次晨账（07 草案＋级别序列适配器就绪＋两处前任口径被实测证伪）
created: '2026-10-12T02:40:00+08:00'
sid: st-mineloop2-20261012
family_id: MINELOOP-CAMPAIGN
---

接棒读物已按序读完：前任任务 #13（31_ 册 remaining_seam_after_unblock 修法＋next_bag_shape）、
99_checkpoint.md §19 晨间包五条等裁、31_ 册 WO-A1 全档、开班令内统筹已预付的四条裁定。

# 一、执行了什么（逐项＋锚点，全部只读或车道内写入，零入队）

1. **施工序①：0080/0081 落地态＝未落地、袋在册存活。**
   - dev 侧四符号零命中：`git show dev:scripts/backtest/fexam/exit_sim/exit_simulator.py` 内
     `exposure_daily`/`weights_daily`/`RETURN-FACE-EXTENSION` 零命中；
     `git show dev:scripts/backtest/fexam/arm_protocol_binding.py` 内 `class ArmBase`/
     `FACE_ID_KEYWORDS`/`require_target_identity` 零命中（唯一命中是我自己正则的 `class ArmBaseMissing` 前缀，已排除）。
   - 队列侧两袋 `state=pending`，position_ahead 7（0080）/25（0081），**无 dead 标记**；
     队列 daemon online、lease=drain-active、head 已等 6078s。
   - 按 §19 三.5「只续租不抢」执行：本班零 requeue、零代投、未碰前任 claim。
2. **从队列 blob 取到未落地接口原文**（第四态＝未落地件唯一存活处是袋内整档快照，袋会被 purge 故有时限）：
   `ArmBase(exposure, daily_return, series=None, face_id="")`、`_resolve_named_series` 的 `series:<名>`
   按名注入与缺名抛 `ArmParamUnfrozen`、`FACE_ID_KEYWORDS` 两键、`require_target_identity` 三参、
   `build_arm_pair` 的 `target=None 且 base 是 ArmBase ⇒ 取 base.daily_return`、
   `_exit_sim_baseline` 已定义未注册且 `series={}`、`ARM_BASE_SOURCES={}` 是**刻意留下半袋**。
   ⇒ 本班适配器不是"另起一版"，是把 0081 自己 docstring 点名的"MOD-RK-049 的日频适配器"补出来。
3. **施工序②：07 卡面草案完成并自带呈批菜单** →
   `docs/_working/mineloop2_campaign/01_card07_draft_and_approval.yaml`（lane 内，未转正）。
   统筹预付的四条裁定逐条落地：lineage 06→07、五态表逐字锚定、三臂定义、L3 三档负存在知识。
4. **施工序③：级别序列适配器代码就绪** → lane 内
   `scripts/backtest/fexam/card_binding.py` +106/−0（**纯插入，删除行实测=0**），
   `tests/backtest/test_card_binding.py` 新增 6 支用例（三红证＋三正证）。
   实测：`python -m pytest tests/backtest/test_card_binding.py tests/backtest/test_arm_protocol_binding.py
   tests/backtest/test_calibration_exam.py -q` → **90 passed**（其中 test_card_binding 38 passed=原 32＋新 6）。
5. **引句落域机械校验**（不落笔即假设）：`verify_face_pair_quotes`/`verify_arm_quote`/
   FACE_ID 字样检查全过，在册分箱器对 07 判 `state=feasible_now, arm_count=3, scalar_expressible=true,
   numeric_frozen=true, out_of_vocab_pillars=三键与 02 同`。

# 二、自裁了什么（逐条＋证据＋依据；均属域内施工序，不触 Owner 保留面）

1. **三臂可同源于「两次回放」而非三套逻辑**——开臂与关臂共用同一条原生迟滞级别序列，
   只在 `level_map` 上分道（五态表 vs 二值表）；中间臂另跑一次无迟滞构造档。
   依据：统筹裁定③"关臂＝二值全清"没给新阈值，而在册件 KILL 的升级面就是卡面 L4 原文的 25%
   （drawdown_state_machine.py:149 `kill_dd: float = 0.25`）；同一条序列换乘子表＝零第二真源。
2. **适配器落在 card_binding.py 内，不新建模块**。
   依据：根宪法 §4.1 全资产净零＋新建件五道手续（creation_token/14 字段头/大白话/depgraph/script-manifest）
   与在册"门禁代码＋它读的册＋本体同袋"处方；消费方 `_exit_sim_baseline` 就在同文件同一次装置调用内。
   代价如实报：card_binding.py 已 1100+ 行；若统筹坚持独立模块，本班可改，成本＝多四道门＋ depgraph 新节点。
3. **无迟滞档用构造性取值 `hysteresis_ratio=1.0-1e-9` + sustained/min_hold 全取 1**。
   依据：在册 config 的 `__post_init__` 校验是开区间 `0 < r < 1`（同文件 :186-187），
   1.0 会被 `InvalidDrawdownStateError` 拒；整数字段校验下限是 `>= 1`（:205）。
   本班不碰任何阈值定义，只给字段值。
4. **脏净值一律 fail-closed 抛错**（空/NaN/非正）。
   依据：NaN 会被下游读成"当日无回撤"＝把缺失伪装成最轻档（在册教训：静默降级与未触发同形）。
5. **在册件返回词表外状态时适配器当场抛错，禁静默扩档**。
   依据：卡面映射表只有五档，出现 RECOVERY 说明映射装不下，须回卡面补表并呈批，不能由适配器给数。
6. **两处前任口径被实测证伪，按"如实改口"处理不入正案**（详见第三节 等裁 B1/B2）。

# 三、等裁什么（编号菜单＋证据＋建议默认＋代价）

## A. 统筹预付裁定落地时新出现的三件（须统筹点头，非缺数字而是口径分叉）

- **A1 轴喂法（最重要）**：卡面 L1/L2/L3 的 2%/4%/6% 原文写"日亏"，在册件同值字段名义是 VaR_95。
  实测五证（逐条可读回）：
  ①在册件字段注释 :133 "升级 VaR_95 阈值"；②35 号 memo §3.11 转换表
  （docs/_working/archive/2026-09/design_memos/35_drawdown_protocol_impl.md:424-426）风险轴写 VaR；
  ③VaR 算法真源 var_calculator.py:25（历史模拟经验分位数），置信度默认 0.95（:134）；
  ④**全仓唯一日频真实调用点** scripts/backtest/sim_daily_runner.py:1410 原文
  `machine.evaluate(trade_date=date.fromisoformat(day), drawdown_pct=drawdown_pct)`——var/cvar 两槽根本不喂；
  ⑤卡面"日亏≥2%"出自 config/trading_decision_map.yaml:3738，而同节点 threshold_refs(:3746) 指向
  5%/10%/15% 的**回撤**册（alert_threshold_registry.yaml:69-70/89/108，THD-DRAWDOWN-001/002/003），
  2%/4%/6% 在阈值册上无日亏条目。
  三案：乙＝var=None 只走回撤轴（**本班推荐**：零新增数字、零语义替代、五态全可达、与④同形；
  代价＝卡面"双轴"里的日亏触发路径不进判据，须标未覆盖面）；
  甲＝var 槽喂当日亏损 max(0,-日收益)（卡面字面成立，但适配器替卡面把日亏译成 VaR 槽＝口径替代）；
  丙＝var 槽喂在册 VaRCalculator 的真 VaR_95（语义纯＋双轴保留，但**窗长是卡面与在册件都没有的新数字**，
  选窗＝替卡拍数，且样本不足前 29 日只能 None，窗口起点前后触发面不一致）。
  不点会怎样：适配器已按 fail-closed 写死——未裁则不开考、零假分。
- **A2 追认两条结构近似**（KILL 不可解除使关臂变成"触发即永久离场"，与 02 原文"恢复即一次买回"**不等值**；
  逐级降级不可跳级使"中间臂=解除即回满"做不到，判据 `maxdd_improvement_vs_no_hysteresis_min_pp=1.0`
  的**所指对象**从"禁 V 型回满"收窄为"降级时序守卫"，数值零动而语义变）。两条均有可执行红证钉住：
  `test_replay_levels_kill_is_sticky_and_quantified`、`test_replay_levels_deescalates_one_step_per_day_only`。
- **A3 L3 三档负存在知识的落册处**（统筹已裁"记一条"，但未指落点：卡面内 / 词库 / 裁定册）。

## B. 前任账面两处数字被本班实测推翻（须统筹改判或指认口径差异）

- **B1 §19 三.4「30 支带 arms 面＝needs_matching_engine 30／feasible_now 0」不可复现。**
  实测（在册 `triage_dir` 直调，非聚合数）：带 arms 面卡 **19 支**＝needs 16／feasible_now 3
  （feasible 三支＝X-R1-01 comparison/02、X-R1-01 ablation/03、X-R1 shadow/02）；
  family 拆面 comparison 11 needs＋1 feasible、ablation 5 needs＋1 feasible、shadow 1 feasible。
  采集面复核：`docs/03_modules` 全树扫描与 `_domain_backtest/exam_cards` 同数（无隐藏面），
  `docs/_working` 内 arms 面卡 0 支，exam_cards 目录自 2026-10-12 00:00 起零 commit ⇒ 非仓库漂移。
  本班判定：§19 那条与 **31_ 册 question_3 的"3 支 feasible_now"互相矛盾**，我的实测量与 31_ 册同侧。
  为何要紧：若按 §19 的"全 needs"排产，会误立"撮合引擎"大项目；实测 16 支 needs 的 reason
  **全部是 `signal_kind=panel`**（臂落在 symbol×日横截面，执行核 comparison 只支持共享 target 的日频标量配对），
  缺的是**一个横截面回放面**，不是 16 台引擎。
- **B2 开班令终局目标写"16 支双臂卡出第一批真分"，实测今天无任何一支出得了分。**
  真实阻塞面（按 31_ 册＋本班复核）：02 卡卡面本身已 feasible_now，缺的是**接线两件**
  （ARM_BASE_SOURCES 注册＋series 面），而这两件依赖在飞的 0080/0081；
  ablation/03 卡面三项幅度未赋数（ArmParamUnfrozen 硬拒）；shadow/02 卡族未路由（family_not_routed）。
  本班不追"16 支"这个数字，按"今晚＝07 草案呈批＋适配器就绪"交付。

## C. 等裁项 5 的实况（0080/0081 未落）

- 两袋仍 pending，前任会话已被队列侧判 ghost（其他 0075/0076 袋的 dead_reason 写
  "heartbeat=exited/注册表无在册"）。风险：pending 袋在 drain 到它时若被同一存活闸判死。
  本班处置＝按令只观察；若判死，**不 requeue**，先按第四态抢救 blob 并上报，
  由统筹转维护三班（队列治理权在其域）。

# 四、下一步（接线袋形状，待 0080/0081 落地后同批）

1. `card_binding.py`：把本班 +106 重放到**落地后的新 dev 字节**上（禁拿车道旧快照整档投，
   在册教训＝袋内整档会静默蒸发他人面），并在 `_exit_sim_baseline` 内把 `series={}` 换成
   `drawdown_level_series_pack(nav)` 的交付＋注册 `ARM_BASE_SOURCES["exit_sim_baseline"]`。
2. `tests/backtest/test_card_binding.py`：在册空册桩 `test_arm_base_sources_book_starts_empty_by_design`
   与注册**同批重写**（0081 袋内原文点名的处方），加"喂错底座必红"红证（r 位身份闸）。
3. 绑定册 `docs/_working/mineloop_campaign/02_binding_book.yaml` 增 07 册格：
   `arm_base_source: exit_sim_baseline` ＋ `arms.{op_open=arm_level_cap_multiply, op_base=arm_identity,
   quote_open/quote_base=07 卡面原文引句, params_open.levels="series:levels_hysteresis",
   params_open.level_map=五态表}` ＋ 关臂/中间臂册格各按裁定档位（三臂三册格还是两臂对？待裁，见 A2）。
4. 07 卡面转正进 exam_cards（须 creation_token＋路径 ASCII＋depgraph），status 从 blocked_on_impl
   升 preregistered 的**前置**＝A1 裁定到位＋步骤 1/2 落地。
5. 新建 .yaml 两道手续（在册教训：漏一道门＝整袋死信）：creation_token 登记、
   docs/_working 禁 .json 后缀。

# 五、复核命令（统筹可直接自查）

```
# 两袋在册态与位序
python scripts/commit_queue.py status | grep -A4 "mineloop-20261010-008"
# dev 上未落地（四符号零命中）
git show dev:scripts/backtest/fexam/arm_protocol_binding.py | grep -c "FACE_ID_KEYWORDS"
# 19/16/3 普查复算（零 CH 零写）
python -c "import sys;sys.path.insert(0,'scripts/backtest');from fexam import arm_protocol_binding as a;print(len(r:=a.triage_dir('docs/03_modules/_domain_backtest/exam_cards')));import collections;print(collections.Counter(x['state'] for x in r))"
# 适配器六支用例（车道面；落地面须重跑）
python -m pytest tests/backtest/test_card_binding.py -q -k "replay_levels or drawdown_level_series_pack"
```

零面声明：判据数值零动｜卡面阈值零动（02/06 文件一字未改）｜分数册零行｜N 账本零写｜
CH 实跑零次｜0080/0081 零触碰（未 requeue 未代投）｜登记册零改｜新 .yaml 尚未入队（手续待投前办）。

# 六、批复落实班加（2026-10-12 02:3x，统筹批复 A1-A3/B1-B2/C 全裁到手）

字母-实质对表：**统筹按实质裁、不按本班菜单字母**，故先做映射再落卡——
批复 A1＝本班菜单 A4（轴喂法，裁乙）；批复 A2＝本班菜单 A2+A3+A5 三项合并
（无迟滞构造档＋关臂阈值＋两条近似追认）；批复 A3＝本班菜单 A6（负知识落点）。
对表明细写在 `01_card07_draft_and_approval.yaml` 的 `chief_ruling_received` 节（机读可查）。

逐条落点（六处已改完，全部只动本班草案文件，未碰 02/06 卡与判官件）：

1. A1 乙案三附带条件：①`approximations_disclosed` 新增首条
   "未覆盖面-var 轴日亏触发路径"（与 L4 同款醒目，明写"读数者不得把本卡结论读成日亏报警机制已被判过"）；
   ②`lineage.narrative_rewrite_not_param` 记"日亏 2%/4%/6% 是叙事改写非参数"，
   四行引用全部本班自己 sed 读回过原文（tdm:3738/:3746、阈值册 :69-70/:88-89、状态机 :150-152/注释 :133）；
   ③`hypothesis` 段加"本卡实际考的阶梯＝回撤轴驱动的五态"。
2. A2 追认：`hysteresis_config_freeze.freeze_status` 改为已裁并**标明"具体构造值属隐含批准、
   统筹未逐值点名"**（0.999999999/1/1 三值，另有指定即改）；`negative_existence_knowledge`
   新增"关臂'恢复即一次买回'无对应机制"（与 L3 同族）；`pillars_numeric_provenance`
   写入所指收窄句（数值 1.0 零动，所指从"禁 V 型回满"收窄为"降级时序守卫三项之差"）；
   两支红证名（kill_is_sticky / deescalates_one_step_per_day_only）作为接线袋前置条件写进卡面披露项。
3. A3 落点：人读＝07 卡面 `lineage`＋`why_new_version_not_edit`；机读＝新建
   `docs/_working/mineloop_campaign/33_negative_knowledge_ledger.yaml`
   （三条负知识 NK-MINELOOP-001/002/003，每条带 verdict_basis＋reopen_condition）。
   未进裁定册、未进词库（照批复）。
4. B1：采信 19/16/3 已入机读账 `candidate_work_items`（CW-MINELOOP-001 横截面回放面，
   一块面服务 16 支），标 `next_step_owner: 统筹排期（本班不自行立项开工）`，今夜不开工。
5. B2：今晚口径按批复收口＝07 草案呈批＋适配器就绪，两项均达标；"16 支出真分"记为线级终局。

# 七、keeper 生命周期监控接管（批复 C 条，本班新职责）

巡检命令（只读，零写）：

```
tail -1 .runtime/sessions/st-mineloop-20261010/heartbeat.jsonl      # 前任 keeper 末拍（pid 27360）
tail -1 .runtime/sessions/st-mineloop2-20261012/heartbeat.jsonl     # 本班 keeper 末拍
python scripts/commit_queue.py status | grep -A4 "mineloop-20261010-008"
```

本班实测到的自身险情与处方（这是今夜最要命的一条，写在职责交接当轮）：
本班 keeper（pid 45000）在建车后约 40 分钟以 `status=exited reason=idle timeout idle=1808s` 自退，
会话随被注册表判 stale 并**从册中消失**（`get_session` 返回 None）——
这正是在册"活性锚失效五形态"的第一形态（idle 自退），若此刻投袋必被 ghost_session 闸打死。
已按在册保活正门三步修复（非自造旗）：

1. `SessionRegistry.register(sid, pid=0)`（pid=0＝心跳新鲜度 90s 判据，短命进程注册的正法）；
2. `_spawn_heartbeat_daemon(sid, root, 30, worktree)` 重启守护（新 pid 35568，实测心跳 30s 一拍）；
3. `register_heartbeat_keepalive(root, sid, reason=..., requested_by="统筹批复 2026-10-12 C 条")`
   登记带名目授权（TTL 1800s，上限 7200s），再 `mark_logical` 使条目 logical=True
   （W-29 逻辑长会话不被 idle 判死；`_verify_chief_form` 需 120s 内新鲜心跳，本班先起守护再标）。

待办（下一轮本班必做）：keepalive 授权 TTL 1800s 会过期，**每轮开工先续授权再看袋**；
前任 keeper（pid 27360）若死，按批复不等 drain：立即从 `.runtime/commit_queue/blobs/` 按袋内
`blob_ref` 抢救三件字节（exit_simulator.py / arm_protocol_binding.py / card_binding.py 的未落地面）
到本班存证区，再上报转维护三班（队列治理权在其域），本班不自行 requeue。

# 八、本班自更正（留旧案卷，更正另起本节）

1. **我把探针文件正文当成了门禁干跑回执。** 02:3x 我读到一段"预检完成 3 文件／结论：可提交（预检通过）"
   并据此以为袋已落地；实测真相是：那段文字来自我自己写的探针脚本正文（Write 后 Read 回显），
   而真实 `gate_dry_run.py` 我用的旗标 `--session-id` 根本不存在（正确旗标＝`--session`）。
   ⇒ 判据：干跑结论只认 `gate_dry_run.py --json` 落出的机读件，不认肉眼看输出。
2. **真实落地状态＝零提交、零入队。** 实测：车道 HEAD==dev（20fa9c43bb）、
   `git show dev:...card_binding.py | grep -c replay_drawdown_levels`=0、
   `git show dev:...test_card_binding.py | grep -c test_replay_levels`=0、
   dev 上 `docs/_working/mineloop2_campaign/` 不存在。四件全在**车道暂存面**（+141/+320/+106/+128，删除行 0）。
   已按批复"禁整档旧快照投递"重读在册配方：新建件**先入队后落车道 commit**（base_head 须==dev，此刻成立）。
3. **随件探针之一被夜间清扫删掉。** `docs/_working/mineloop2_campaign/probe_07_adapter_replay.py`
   我 02:3x 建过，03:0x 复查已不存在（`ls` 实测该目录只剩 00/01 两件）；
   同目录 `00_morning_pack.md`/`01_card07_draft_and_approval.yaml` 健在。
   ⇒ 级别序列的实测证据改以**在册用例**为载体（6 支 pytest，实测 90 passed 全绿＋
   两档 state_days 不同形＋kill_stuck_days>0），不再依赖 tmp 探针；探针脚本已重建于
   `.runtime/tmp/st-mineloop2-20261012/`（tmp 件不入袋，不入账）。
4. 我先前写下的"关臂与开臂共用同一条级别序列⇒零第二真源"是自裁设计，批复 A2 已追认；
   但**无迟滞档三个具体值**统筹未逐一点名，本班已在卡面 `freeze_status` 内标明"隐含批准未显式点名"，
   不冒充已签批（在册教训：代理不得为达标自造签批署名）。

# 九、晨裁 ⑨ 落实与本机两次死机账（2026-10-12 15:2x-18:3x 补）

## 9.1 晨裁三条全部执行

1. **撤"隐含批准"标注**：`01_card07_draft_and_approval.yaml` 的 `hysteresis_config_freeze.freeze_status`
   与 `chief_ruling_received.not_explicitly_named` 两处按令改写为
   "三值经 2026-10-12 ⑨ 追认批准，定性为工程近似值非判据数"，撤销动作本身留痕。
   机械自证：替换前数命中（各 1），替换后残句计数=0、"追认批准"计数=1、行数仍 427；
   对 dev 净差 **+2/−2**（删除的 2 行就是被改写的那 2 行，纯本班自有件）。
2. **账册袋 0001 已落地**＝commit 299e1f40dc，三件 `git cat-file -e dev:<路径>` 全部 ON_DEV 实测。
3. **代码已重基到 0081 落地后的新 dev 字节**：`git diff dev --numstat`＝
   `scripts/backtest/fexam/card_binding.py +109/−0`、`tests/backtest/test_card_binding.py +127/−0`
   （删除行实测 0），用例 38 passed（含 0081 落地的在册空册桩与新三面装配用例仍绿）。

## 9.2 重基过程自犯一条（记法不记功）

第一次拼接用 `devnew[:anchor] + block` 漏了 `+ devnew[anchor:]`，把整档写成 956 行
（对 dev **+102/−359**＝截断），且已 `git add`。靠"写后核 `written==expect`＋`git diff dev --numstat`
删除行必须为 0"两道尺当场抓到并修复（1322=1213+109，numstat 回到 +109/−0）。
⇒ 入工法：**任何整档重写后，先核行数配对与删除行计数，再谈 git add**；
Edit 类工具吃标题的教训（在册 [[edit-append-anchor-consumes-heading]]）在 python 切片拼接上是同一形态。

## 9.3 本机两次死机＝本班 keeper 三次失活（批复 C 条职责的第一手数据）

| 时点 | 事件 | 处置 |
|---|---|---|
| 02:1x | 建车后约 40 分钟守护 `idle timeout 1808s` 自退，注册表条目消失 | 按保活正门三步修复（register pid=0→起守护→grant＋mark_logical） |
| 15:2x 前 | 第一次死机，双 keeper 末拍停在 03:55Z（断 3.5h） | 同三步修复（新 pid 2648），并实测 `mark_logical` 需心跳先新鲜才不被降级 |
| 18:3x 前 | 第二次死机，末拍停在 09:25Z（断约 1h），条目再次消失 | 同三步修复（新 pid 22496，grant TTL 1800s） |

⇒ 给后续班的事实：**本机每次死机都会带走 keeper 并让注册表条目消失**，
所以"投袋前先 `tail -1 .runtime/sessions/<sid>/heartbeat.jsonl`＋`get_session(sid)` 两查"
必须做成开工第一动作，而不是等袋被判 ghost 再查。前任的 ghost 连死两袋是同一机理。

## 9.4 他班死信一件（本班零触碰，已呈报）

`q-20261012-st-mineloop-20261010-0080`（exit_simulator 返回面扩展）落 `dead/`，
dead_reason 原文＝门禁 TAKEOVER-PENDING 阻断，命中**死会话 `st-cband-20261012`** 的
open 接管条目（该会话 pid 41268 已死、claim 泄漏 8 件含 `scripts/backtest/fexam/exit_sim/exit_simulator.py`）。
本班实测：①dev 上 `exposure_daily` 零命中（0080 确未落地）；②0081 已落地 ⇒
在册 `_exit_sim_baseline` 现在跑必 raise（它明写"装置未交付 exposure_daily 返回面＝返回面扩展未落地？"）；
③死袋内容**完整可取**（blob 存在、sha256 自校验通过、562 行）＝第四态抢救面在，无时限风险尚未到。
⇒ 按宪法 §2.7 与本令纪律：本班**不 requeue 他班袋、不改他班件、不代处置他死会话的 claim 与车道**；
此事是"首张双臂真分"的当前真阻塞，已列入 §9.5 呈统筹转维护三班（队列治理权在其域）。
另记一条实测改判：早前本班报"st-cband 判死存疑"——本轮 `SessionRegistry` 复查该 sid
**在册且 logical=True、reincarnation_count=3**，即门禁当时按"PID 已死/注册表除名"判死，
而注册表侧后来又有条目＝"死"的判定在两面（PID 面/注册表面）之间不一致，
这条观测请一并转维护三班（与在册"活性锚失效五形态"同族，非本班能自裁）。

## 9.5 下一步（照晨裁 ⑨ 的序）

1. 文档袋（本袋）：撤标注＋panel 设计稿＋本节账。
2. 代码袋：待本袋落地后再投（同会话短窗连投会被 C1 合批成跨域袋＝在册死信形态），
   内容＝已重基的 `+109/−0` 与 `+127/−0` 两件，**不含注册**（注册须等 0080 内容落地，
   否则 `_exit_sim_baseline` 必 raise，且空册桩重写会钉在一个跑不通的来源上）。
3. 接线袋：0080 内容落地后＝`ARM_BASE_SOURCES` 注册＋`series` 面接上＋空册桩按新纪律句重写
   ＋"喂错底座必红"红证＋绑定册 07 册格＋07 卡面转正（creation_token 随袋）。
4. panel 设计稿 D1-D4 待统筹裁；裁前本班零施工（本令已执行：只出稿未动一行业务码）。
5. 呈统筹转维护三班两件：0080 死信与 st-cband 接管条目（含 9.4 末条的活性两面不一致观测）。

零面追加：判据数值零动｜02/06/07 卡面判据键零动（本轮只改 07 草案的两行署名性文字）｜
判官件零改动（panel 设计稿只列"必须改哪些行"，未动一行）｜分数册零行｜N 账本零写｜CH 实跑零次｜
他班袋与死袋零触碰｜热册投影（车道内 +1400 行他班条目）零入袋。

# 十、代码袋 0003 死信与拦局证据（2026-10-12 20:3x 追加）

## 10.1 死因（读 dead_reason 原文，不猜）

`q-20261012-st-mineloop2-20261012-0003`（card_binding.py +109/−0）落 dead/，
网关落盘失败＝门禁 **TAKEOVER-PENDING** 阻断，命中**前任会话 `st-mineloop-20261010`** 的
open 接管条目（判死证据 last_activity idle 31045.3s > 7200s），命中文件正是
`scripts/backtest/fexam/card_binding.py`。该条目的处方清单含其自有车道
`.aidrafts/st-mineloop-20261010`（dirty=107）、12 支其自有死袋（含 0080）与心跳残留。

同一拦局对本班两袋的影响（实测台账 `--list` 面复核）：
`scripts/backtest/fexam/card_binding.py` 与 `tests/backtest/test_card_binding.py` **均**被该条目覆盖 ⇒
代码袋与测试袋都投不动；`docs/_working/mineloop2_campaign/*` 不被任何 open 条目覆盖 ⇒ 文档袋可走。

## 10.2 决定性证据：前任车道那件与 dev **零内容差**（所以这不是内容冲突，是账面归属）

本班只读复核 `.aidrafts/st-mineloop-20261010/scripts/backtest/fexam/card_binding.py`：

```
lines theirs=1213  dev=1213
_exit_sim_baseline: theirs=1 dev=1
ARM_BASE_SOURCES[: theirs=1 dev=1
replay_drawdown_levels: theirs=0 dev=0
register: theirs=4 dev=4
```

⇒ 其 card_binding.py 面**没有任何未落地差量**（与 dev 同长同符号计数，且不含本班新函数）；
其 dirty=107 集中在 exam_cards 新卡与几本注册表，不在绑定层。
所以"我落地会吞前任未落地工作"这一风险在**该件上不成立**；门拦的是归属登记，不是字节冲突。
本班据此仍**不自解他班账**（他班 12 支死袋与 107 脏件属其属主/维护三班判定面，
代处置＝归属篡改级），只把这条证据交给有权者以省其复核成本。

## 10.3 本班已做的与未做的

已做：①代码已重基到 0081 落地后的新 dev 字节并实测 +109/−0、+127/−0、54 passed；
②中间态自证——把 dev 版用例单跑我的新码＝48 passed，证明"码先落、测试后落"这一段 dev 不红；
③文档袋 0001/0002 已落地（dev 侧 `git cat-file -e` 与 `git log` 双验），设计稿含 §8 分桶精修追加；
④本班自身接管条目已按处方自销（见 §九 9.3），现存 open 条目 0 条。

未做（属他域或门位）：不 requeue 前任任何死袋（含 0080）、不 `--resolve` 前任账、
不 `git worktree remove` 前任车道、不动其 107 脏件、不碰热册投影。

## 10.4 呈统筹的处置岔路（本班不自拍，三条均可即刻执行）

- 甲（推荐）＝转维护三班处置 `st-mineloop-20261010` 条目（其 Rx 清单本就在其治理域内），
  本班随后 requeue 0003 与投测试袋。代价＝本班代码面滞留到处置完成，但卡面/设计稿/账册已全部在外。
- 乙＝统筹明令授权本班以"§10.2 零内容差"为据 `--resolve st-mineloop-20261010 --by st-mineloop2-20261012`
  ——**只销账不代处置其死袋与车道**（那两项仍归其属主）。代价＝账面上由别会话销他人条目，需留痕。
- 丙＝统筹指认另一个有权会话执行乙同款。
  不点后果＝代码与测试两件持续被同一条目拦，首张双臂真分与 07 卡转正的接线袋都开不了工。

另附一条独立观测请一并转维护三班：`st-cband-20261012` 在 0080 死信里被门禁按"PID 已死/注册表除名"
判死，而本班随后 `SessionRegistry` 复查该 sid **在册且 logical=True、reincarnation_count=3**；
即"死"的判定在 PID 面与注册表面不一致（与本班 §九 9.3 自己的三次 keeper 失活同族）。

# 十一、救援袋与接线袋落地账＋本轮四处自纠（2026-10-12 20:4x-21:0x）

## 11.1 统筹令执行序与在途态（只认 git 与队列双侧核账）

| 袋 | 内容 | 态 | 落地判据 |
|---|---|---|---|
| q-0005 | 适配器 card_binding.py +109/−0 | **done** | dev 该件内 `replay_drawdown_levels` 命中数 = 2 |
| q-0006 | 0080 返回面救援 exit_simulator.py +14/−0 | processing | dev 上 `exposure_daily` 现仍 0 命中＝未落 |
| q-0007 | 接线袋 card_binding +14/−6 与 tests +176/−6 | pending | 注册位 `"exit_sim_baseline": _exit_sim_baseline` 现仍 0 命中 |
| q-0003 | 首次投的代码袋（已死） | dead（存档，内容由 0005 复活） | — |

三袋逐件核过 `blob sha256 == 车道磁盘字节`，零失配。

## 11.2 0080 救援＝统筹令原样执行（红证三件全过，两档 stop_enabled 各一遍）

基底先核：原袋 `base_head=1075a03e4efe` 的该件与 **dev 现字节逐字符相等**（同 548 行）⇒
落件字节直接取死袋 blob（sha256 与袋内 `blob_sha256` 相符），零重推导零改写。红证（同输入两码面）：
输入指纹相等 `b4340dfe16b53bbbfb91`（=True）/`32420c3d24ea0357e292`（=False 档），
nav 索引相等且**逐位最大差 0.0**，既有 **12 支 st 键零变**，新增键仅
`exposure_daily`/`weights_daily`，移除 0，arity 不变；自洽附加尺＝敞口∈[0,1] 且
`weights 行和 − exposure` 最大差 0.0。回归面 `pytest tests/backtest/fexam -q` = **82 passed**。
零 CH 零生产写。探针：`.runtime/tmp/st-mineloop2-20261012/probe_rescue_0080_two_face.py`。

**在册坑复证一条（我这次真踩）**：两码面副本的放置层不是任意——该件自锚
`RUN_ROOT = Path(__file__).parent.parents[3]` 且断言 `RUN_ROOT/AGENTS.md` 存在，
我把副本多放深一层（`.runtime/tmp/<sid>/probe/dev_face/`）就得到
`AssertionError: RUN_ROOT 解析失败: ...\.runtime` 的**假红**；改到恰四层
（`.runtime/tmp/<sid>/dev_face/`）即过。指纹还必须取"各码面实收参数字节"，
在外面算一次再比两次＝恒真、测的是空气（我第一版就是这么写的，已重写）。

## 11.3 连坐账按授权二次销；根治未做（如实报）

`st-mineloop-20261010` 的接管条目时间线（全部实测）：15:22 由 **st-examrun-20261012** 首销 →
我 20:2x 用门自己的尺测 card_binding/tests **passed=True**（据此以为已通）→ 同轮再测
exit_simulator **passed=False**，判死证据换成 `orphan_resources: .aidrafts/st-mineloop-20261010 在盘而注册表无此会话`
⇒ **条目会被 `--scan` 按其仍在盘的车道重开**，只要那 107 脏件的车道还在。
20:4x 按统筹授权乙案二次 `--resolve ... --by st-mineloop2-20261012`，note 原文入账，
随后门的尺复验三件全 passed。
根治＝处置其车道本体（107 件在考试卡与注册表域），本班未做（非本班权限，且需逐件核成果归属）；
统筹 note 里"遗留归本班继承处置"这句本班接单但**另单执行**，本轮只解绑定层提交连坐。

## 11.4 本轮四处自纠（都改成下班的省事面）

1. **我自己的 PYTHONPATH 泄漏造出"网关 fail-closed"假红**：在主区跑 `git_commit.py` 时
   沿用了车道的 `PYTHONPATH=$PWD`，于是主区脚本 import 到**车道 8 小时前的旧 src**，
   报 `POOL-REGRESSION-DIRECTION: factory function not found`（该工厂是今天才落的新门），
   看着像提交链全局崩。清掉 env 后 `CLAIMED: 1/1`。⇒ 规矩：**主区脚本必须 `env -u PYTHONPATH`；
   车道脚本必须 `PYTHONPATH=$PWD`**，两者不可混带。
2. **车道落后 HEAD 八小时**：`arm_protocol_binding.py`（缺 0081 的 ArmBase）与
   `test_calibration_exam.py` 停在旧面，症状是接线新用例 `ImportError: cannot import name 'ArmBase'`。
   按文件 `git checkout dev -- <两件>` 同步（本班在这两件上零内容改动，同步后对 dev 净差空）。
   ⇒ 接任何"他人已落地"的接口前，先 `git diff dev --numstat` 量本车道该件是否落后，别看盘上代码就写用例。
3. **RUFF-PRECLEAN 预检替本班省一整轮 landing**：入队即拦"Would reformat:
   test_card_binding.py"（我新加段落多一个空行），修后重投；该门只读不改写，
   正是"落地侧才见红要烧完一整轮"的通道阻断谱前移。
4. **接线为什么必须一袋（跨域留痕）**：注册代码与它自己要重写的那道空册纪律桩分处
   `scripts/`（D_BACKTEST）与 `tests/` 两域，拆开投无论谁先落都必留一个红色中间态
   （先落码＝dev 旧桩断言空册当场红；先落测试＝新桩断言已签认册红）。
   按根宪法 §2 第 4 条用 `--allow-multi-domain` 留痕合袋，不拆袋糊。

## 11.5 一条他班存量红（登记不代修，请转考试班）

`tests/backtest/test_calibration_exam.py::test_run_card_consumes_injected_ledger_path` 要
`run_card(ledger_registry_path=...)`，而 dev 码面 `grep -c ledger_registry_path` = 0；
在主区落地面复跑同样红（1 failed/37 passed），其用例由 c0da1808f1 自述
"改前 dev 字节跑＝TypeError，已实测证红"＝先落测试后落码的在途态。
本班相关面全绿（test_card_binding 39 passed、test_arm_protocol_binding 16 passed），不代修。

## 11.6 落地后本班剩下的两件事

1. 绑定册 07 册格（`arm_base_source: exit_sim_baseline` ＋ arms 面引句与五态 `level_map`）
   ＋07 卡面转正（creation_token＋ASCII 路径＋depgraph），status 升 preregistered；
2. 首批开考（真 CH 读一次基线面板出首张双臂分，试次照进 n_trial_ledger）。
   这两件都等 q-0006/q-0007 落地，缺一不开考——06/07 卡的 impl_gap ①② 到此才算闭合。

# 十二、base-head 之坑第二次应验（这次是我自己造）＋合袋定性（2026-10-12 21:0x）

q-0007（接线袋）落地侧死信：`[landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）:
scripts/backtest/fexam/card_binding.py`。读袋内 `base_head` = **20fa9c43bb36**＝**我车道自己的 HEAD**
（八小时前从 dev 分出的那个点），而不是投件时我写在命令行里的 dev sha。

机理（在册记忆的第三种形态，这次实测坐实）：`git_commit.py --enqueue` 的 base_head
**取 worktree-root 自己的 HEAD**，我传什么旗标都不改它。车道分支从建好就没提交过，
HEAD 一直停在开工那一刻，而 dev 这几小时前进了十几笔（含我自己 0005/0006 落的两件）⇒
落地侧看"基底有、dev 也有但两边都改了同一文件"＝真冲突，直接死信。

修法两条，本次走第②条：
① 走 `commit_queue.py enqueue/requeue --base-head $(git rev-parse dev)`（我前面 0001/0002/0004/
   0005/0006/0008 六袋都这样，base 都对）——**但这条路没有 `--allow-multi-domain`**，
   跨域合袋会在预检就被 COMMIT-SCOPE 拦（requeue 0007 时就撞了这个）。
② 把车道指针快进到 dev，再走 `git_commit.py --enqueue --allow-multi-domain`。安全前置两道实测：
   `git rev-list --count dev..HEAD` = **0**（车道无独有提交）且 `git merge-base --is-ancestor HEAD dev` 为真，
   然后 `git reset --soft <dev>`——只动分支指针，**索引与工作文件一字不动**（我的
   +14/−6 与 +176/−6 净差在指针移动前后逐字相同）。复位后 q-0009 的 base_head = dev ✓。

⇒ 给后续班的硬规矩：**车道里用 `git_commit.py --enqueue` 之前，先核 `git rev-parse HEAD` 等不等于 dev**；
不等就要么快进指针（无独有提交时 `--soft` 安全），要么改走 commit_queue + 显式 `--base-head`。
"每轮修改即 git add"不等于"车道随手 commit"——车道多一个独有提交，base_head 就被自己污染成死袋。

合袋定性补记：注册代码与它必须同批重写的空册纪律桩分处 scripts/ 与 tests/ 两域，
拆开无论先后都留一个红色中间态（先落码则 dev 旧桩断言空册红，先落测试则新桩断言已签认册红），
故按根宪法 §2 第 4 条用 `--allow-multi-domain` 合为一袋留痕；落地侧对跨域已容忍（§2.6），
真正卡住的从来不是跨域，是 base-head。

当前在途（21:0x 实测）：q-0008 文档袋 processing、q-0009 接线袋 pending，全队列 pending 10/processing 4；
dev 上注册位与 series 接线位现仍 0 命中＝未落。0007 留 dead/ 存档不删。

# 十三、07 卡面转正袋（2026-10-12 21:3x，统筹"不拦"令执行）

- 转正件：`docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__07_five_state_cap_anchor.yaml`
  （ASCII 路径＝根宪法 §8；333 行；creation_token 走意图 API 登记，merge_evaluation 写明
  02→06→07 lineage 并存不替代）。
- 生成方式是**逐字切块**非重排：从草案 `card_draft` 块切出 313 行（去缩进 2 空格），
  状态性改动只有三处且全部带等值断言锚（status、status_reason、impl_gap），其余原文一字未动；
  追加块只含批准与接线凭据，**不含任何判据**。
- 五项机械自证（全过，非肉眼）：①八柱与 02 **逐值相等且键集合差为空**；
  ②窗口 in_sample/oos 与 02 逐字相等；③`verify_face_pair_quotes` 对拟投册格的
  e/r 两引句**落域通过**（e 在臂定义面、r 在底座出处面）；④`verify_arm_quote` 五态映射长引句命中；
  ⑤在册分箱器 `triage_card` = feasible_now／arm_count 3／pending_numeric 空／out_of_vocab 三柱与 02 同。
- 落地点本轮踩到并自纠的一处：初版卡面引了两条 **docs/_working 临时区路径**
  （35 号 memo 归档件、负知识机读账），触根宪法 §9 第 4 条"永久区禁引临时区"；
  已改判为同区可核指针（"设计真源=35 号 memo §3.11，其在册代码投影即 :133/:150-152 三行，本卡以代码面为准"
  ＋"负知识机读账＝战役台账 NK-MINELOOP-001/002/003，随战役台账走，非本卡判据依赖"），
  改后 `grep -c '_working|.runtime'` = **0** 并重跑③⑤两项自证仍全绿。
- **首考前必须先裁的一条结构事实（已写入卡面 exam_scope_note，本班不自裁）**：
  本卡八柱里同时含"开臂 vs 关臂"（maxdd_improvement_min=5.0）与"开臂 vs 中间臂"
  （maxdd_improvement_vs_no_hysteresis_min_pp=1.0），而在册 `build_arms` 只循环 open/base **两位**、
  comparison 通道每次只配一对 ⇒ "三臂两对照"在现结构下一考只能判一对。
  甲＝两次开考各判本对、另一柱在凭据里显式标 not_judged；乙＝拆两张卡各判一对。
  未裁前首考只开**第一对（开臂 vs 关臂）**并带 not_judged 披露，禁把未判读成已过。
- 待办顺位：本袋落地 → 绑定册 07 册格（`arm_base_source: exit_sim_baseline` ＋ arms 面五态 level_map
  ＋两条 series 档名）→ CH 压缩窗实测核 → 首批开考（真读一次基线面板，试次进 n_trial_ledger）。

# 十五、裁甲执行账（2026-10-12 21:4x-22:0x，开考前置全就位；窗未开故未跑）

## 15.1 CH 让路窗：用门自己的尺读，不猜

`card_binding._in_ch_yield_window(datetime.now())` 实测读数（21:44）＝
**"21:00-22:30 W1 v2 提前窗让路"** ⇒ **首考此刻不得开跑**；本班未用
`--override-ch-window-with-reason` 越窗（越窗须有真实理由并留痕，此刻没有）。
窗后（≥22:30）按同一命令开跑，CH 取数次数与试次计数届时照单申报。

## 15.2 三件新落地物（含两处"预证先红"的自纠）

1. **绑定册 07 册格**（`docs/_working/mineloop_campaign/02_binding_book.yaml`，14→15 格，对 dev 纯追加）：
   `arms_variants.{off,mid}` 两档配对；`op_open`/`params_open` 两档**逐字相同**（裁甲③机械面），
   只有 `op_base` 的 levels 档名与 level_map 随配对切换；两张 level_map 逐字取卡面
   `level_to_cap_map`，本册零自拟数。**YAML 坑一条**：`off:` 未加引号被 1.1 读成布尔 False
   ⇒ 键必须写 `"off"`（写出来能解析、能 load，但 `sorted()` 当场以 str/bool 比较炸出，未落到袋里）。
2. **配对选择器**（card_binding）：`load_binding_book(path, arms_variant=...)` ＋ CLI `--arms-variant`，
   三档 fail-closed——缺档名 `arms_variant_required`（**禁默认取第一档**＝静默换命题）、
   未知档名 `arms_variant_unknown`、`arms` 与 `arms_variants` 并存 `arms_pairing_ambiguous`；
   无 variants 的既有格行为零变更；配 3 支用例。
3. **类身份单解析器修复（落地件里的真 bug，预证抓到）**：`_exit_sim_baseline` 原按 `fexam.*`
   路径 `import ArmBase`，装配侧 `_arm_pair_builder()` 首选 `scripts.backtest.fexam.*` ⇒
   同一模块两个包名＝同一个类两个对象，`isinstance` 判不出底座，敞口乘子拿 `ArmBase` 去乘
   （合成装配预证实测 `TypeError: ArmBase * float`）。与 17:4x"闸真拦、测试认不出"是同一条病根
   第二次发作（那次修的是异常类）。正解按在册"导入路径单义"：抽 `_arm_protocol_module()` 作唯一
   解析器，装配与底座构造共用；加不变量用例 `test_arm_protocol_class_identity_is_single_parser`。
   该崩法是 fail-safe（run_one 收成 error 不出分），不产假分，但首考必开不了。

## 15.3 双档装配预证（合成底座，零 CH）＋一条未核到的诚实附注

同一基线净值（120 日、含深回撤后修复）喂两档各跑一遍三面装配：

| 档 | 装配 | 两臂差异日数 | 两臂值域 | ev 带档名 |
|---|---|---|---|---|
| off（开 vs 关） | OK | **65/120** | 均 ∈0..1 | off |
| mid（开 vs 中间） | OK | **46/120** | 均 ∈0..1 | mid |

⇒ 两对都不退化（同形即门柱吃常数 0 差＝假考，这条在真 CH 之前先证）。
**未核到的一条如实写**：预证里 `ev["arm_level_creds"]` 为空——因我直造合成 ArmBase 未经
`_exit_sim_baseline`（只有它挂 level_creds）。生产路径理应不为空，但我还没在真跑里看到；
首考后须回凭据面确认 `arm_level_creds` 与 `not_judged_pillars` 双双在位，缺一即报。

另核：判定类 `src/zephyr/risk/core/drawdown_state_machine.py` 磁盘==索引==HEAD、主区与车道同字节，
`position_cap` 六个 return 行原样读到 1.0/0.8/0.5/0.3/0.0（＋RECOVERY 阶梯）
⇒ 卡面五态映射与**正在执行的**代码逐字相符（不是拿旧盘自证；车道内 `sys.path.insert` 对
已预导入的 zephyr 无效，这条实测过，故必须核主区那份）。

## 15.4 索引面险情第二次应验前的规避（统筹已广播）

同步绑定册用 `git checkout dev -- <该件>`（本班在该件零本地改动，先核净差为空再动）；
暂存一律**显式列路径**，入袋前 `git diff --cached --name-status` 计数：本袋五件全 A/M、**D=0**。

## 15.5 队列实况

0005/0006/0009（三件核心）与 0001/0002/0004/0008（账册）均 done；0003/0007 dead 已定性修复；
0010（07 转正＋§十二/§十三）pending 第 8 位；本袋 0011 含卡面与账册的**严格超集**，
与 0010 同文件部分被取代或被合批均不丢内容。全队列 pending 11、processing 4——堵但不停。

## 十六、开考前预检三件（22:05-22:12 实测，全是"跑之前就知道"的账）

### 16.1 试次=2 的在册机制冲突（裁定甲② 的执行障碍，证据到行）

裁定甲② 要"同卡两试次，预算册记 2"。实测这条链**结构性记不到 2**：

- `scripts/backtest/fexam/calibration_exam.py:744` 的批次键 `batch_id=f"examcard:{card['card_id']}:{row['date']}"`
  ——**无跑次判别位**（`run_id` 在 :707 带 tag，但没进这个键）；同卡同日两跑 ⇒ 同一 batch_id。
- `src/zephyr/backtest/core/n_trial_ledger.py:368` 起 `record_run` 原文"幂等：同 batch_id 存在则跳过返回现状"，
  `_mutate` 命中已有键时 `return None  # 幂等：已登记`，返回 `status="exists"` 而 **不追加**。
- 读数面 `n_trial_ledger.py:_count_of` 只把 `batch_records` 的 n_trials 求和 ⇒ 第二跑贡献 0。

本班**不改判官件**（该件是考试班与全部在册卡的共用面，且改键＝动 DSR 分母口径），采两条并行：
①第二跑后以**同一在册单口** `TrialLedger.record_run` 显式补登一条带跑次判别位的批次
（`recorded_by` 记本班 sid，note 写明补登理由与撞键证据），使预算册实际计数=2；
②把"batch_id 缺跑次判别位"作为待裁项呈统筹/考试班（一行键改即可治本，但属判官面）。
两跑前后各取一次台账快照（batch_records 条数＋求和），差值即本班的入账凭证。

### 16.2 "首张双臂分"结构上不可能是 PASS（前置披露，不做事后解释）

`pillars_route(07)=dual_arm`；判官 `_judge_comparison`（`calibration_exam.py:351-354`）对
**并集词表外的键一律追加一条 fail**："未支持判据键（机判面待扩）"。实测 07 八柱的键集差：

| 判官有机器面（5 柱） | 判官无机器面（3 柱，必致 fail） |
|---|---|
| maxdd_improvement_min / sharpe_delta_min / turnover_delta_annual_max / cost_tier_bp_required / oos_same_sign | **maxdd_improvement_vs_no_hysteresis_min_pp / missed_crisis_trigger_max / whipsaw_roundtrip_ratio_max** |

⇒ 两跑的 `verdict` 都将是 **fail**，且分数行的 `unjudged.numeric_keys_not_read` 正是这三根柱
（:697 双臂面取 `_UNION_PILLAR_KEYS` 作对照词表，与卡面 `out_of_vocab_pillars` 自报三键逐字一致）。
本班把"首张双臂分"交成**可读数的 fail 行**：配对实测值（maxdd_improvement_pp / sharpe_delta /
turnover_delta_annual_x）照报，但**不把它们叙述成门柱全过**，也不做事后补救性解释——
PASS 候选的成立条件是三根柱获得机器面（词表立法/绑定层扩面），那是统筹排期项不是本班今夜可自决的面。

### 16.3 预检抓到一条别名坑（生产路径无恙，如实划边界）

重跑 §15.3 双档预证时，本班先用 `from fexam.arm_protocol_binding import ArmBase` 造合成底座 ⇒
两档都在乘法处裸炸 `TypeError: unsupported operand type(s) for *: 'ArmBase' and 'float'`；
实测 `cb._arm_protocol_module().ArmBase is ArmBase` → **False**（同一文件被 `fexam.*` 与
`scripts.backtest.fexam.*` 两个包名各载一次，类身份分裂）。改用 `cb._arm_protocol_module().ArmBase`
后两档均装配成功（e 面 60 日、r 面 59 日、`variant=off/mid` 档名与 `arm_level_creds` 均在位）。
边界结论：**生产路径单一解析器已一致**（`_exit_sim_baseline` 与装配侧同走 `_arm_protocol_module()`，
0012 在册红证 `test_arm_protocol_class_identity_is_single_parser` 管的就是这一条），
暴露的是"外部按别名构造底座"时 `_unwrap_base` 落到 else 分支、错误以 pandas TypeError 形式裸炸而非领域错误。
拟补（下一袋，非开考阻塞）：`_base_or_raise` 对带 `.exposure` 属性的非 Series 输入抛
`ArmBaseMissing/ArmFaceMismatch`，并配一颗别名构造必红的红证。

## 十七、开考前的两面账（N 账本 git 面落后运行面＋主区索引陈旧回退面）

### 17.1 N 账本：主区运行面比 dev 多 23 条批次＝13,963 试次从未入 git

实测（22:2x，`git show dev:` 与主区工作树逐 batch_id 对集合差，非计数目测）：

| 面 | batch_records 条数 | 其中 07 相关 |
|---|---|---|
| dev（git 面） | **29** | 0 |
| 主区工作树（运行面，`git status` 呈 ` M`） | **52** | 0 |

差集 23 条的署名分布：`st-mineloop-20261010`（前任）10、`calibration_exam` 5、
`factory_grid_executor` 4、`st-statsgov-20261012` 3、`st-examchief-20261009` 1；
`sum(n_trials)` 差 **13,963**。按 batch_id 尾段分桶：`2026-10-10` 9 条、`2026-10-11` 5 条、
`2026-10-12` 2 条，另有 `grid_20261010-*` 4 条与 `ruler-calib-20261012*` 3 条（9+5+2+4+3=23 自校）。
⇒ **在册事实**：考试与网格的试次记账历来直接落主区运行面，落地袋无人带这本册
（`campaign_report.py:209` 与 `batch_window_preflight.py:123` 读的都是 YAML 文件面，无 PG 物化，
本班已 grep 确认）⇒ DSR/FDR 分母的 **git 面比运行面虚低 13,963**，与在册"试次少记 17.4%"那条
（根因=`factory_grid_executor` 只 set_effective_trials 从不 record/sync）是**不同层的另一处缺口**：
那条是单口没调用，这条是调了但整册从未落地。转维护三班＋统筹：本册需要一次专门的"运行面→git 面"收编，
**不是本班代劳**（袋=整档快照，随袋带他班 23 条未落地条目＝归属篡改，在册禁例）。

对本班处置的三条硬约束：①本班两跑的试次经**同一在册单口** `TrialLedger.record_run` 记入
**主区运行面**（与前任/网格班同姿势），车道副本**不入袋**；
②车道 ledger 与主区 ledger 已分叉 23 条，本班**绝不**用 `git checkout dev --` 或 `git restore` 动车道这本册（会连坐他班在途条目）；
③交付陈述一律写"运行面已记 N 条 / git 面 0 条"两面，不写"已入账"单面话。

### 17.2 主区三件考试共用件的索引面是**旧字节**（内容门读索引⇒回退炸弹在册形态）

`git status --porcelain` 主区呈 `MM`：`card_binding.py`／`calibration_exam.py`／`arm_protocol_binding.py`
三件的**索引面比 HEAD 旧**（暂存差＝ 5+/180−、6+/12−、2+/86−，工作树差恰为其反号＝工作树才是 HEAD 内容）。
在册机理（[[content-gates-read-index-not-worktree]]）：内容门禁吃索引字节，
所以任何后续袋一旦把这三件放进清单，门判的是"被回退 180 行的旧版"，而落地按工作树写＝**门与落地判两个版本**。
本班不主区动这三件（既不改他班索引也不代修），只把事实登记转告；本班施工与开考一律在车道，
车道三件的工作树字节＝本班 0012 袋的快照源，且入袋前逐件 `--files-file` 显式列路径。

### 17.3 为什么本班开考必须在车道跑（两面实测）

主区 `02_binding_book.yaml` 里 07 册格命中数 **0**、`card_binding.py` 里 `arms_variant` 命中数 **0**
（0010/0011/0012 仍 pending 未落）；车道两面各为 **1／11**。
⇒ 主区现在跑必以 `arm_base_source_unwired`/无配对档如实失败，**只有车道具备已批的接线态**；
本班在车道起跑（底座与分数册落车道副本），结果袋待 0012 落地后按 §十七.1 的口径整包呈。

## 十八、CH 内存墙：两回合 HTTP 500 的定性与"同进程两跑"的解法

- **22:36/22:52 两回合本班 CLI 两跑全部阵亡**，死位不同：第一跑死在元数据查询
  （`SELECT name FROM system.columns ... technical_indicator`），第二跑死在数据查询
  （`... aroonosc FROM c1_market.technical_indicator WHERE period='daily' ...`）⇒ 不是语句问题。
- 定性用**服务器自己的账**（`system.errors`）：`MEMORY_LIMIT_EXCEEDED` code=241，
  读数 22:41 时 4,678 次 → 22:54 时 4,805 → 23:00 时 4,916（持续增长），
  原文 "would use 7.16 GiB ... current RSS: 6.70 GiB, maximum: **7.14 GiB**"；
  `system.asynchronous_metrics.QueriesPeakMemoryUsage` 实测 6.60 GiB（23:00），
  `system.processes` 同时刻并发 3 条重查询合计 4.29 GiB（他班技术面面板装载同型）。
  ⇒ **CH 服务器总内存上限 7.14 GiB 被并发面板装载撞穿**，本班装置单查询 RSS 实测 1.4-2.6 GiB。
- 本班解法（零判据改动）：两跑改**同进程**执行——装置自带进程内 `_cached`，24 列面板只载一次
  ⇒ CH 面占用**减半**；驱动器 `.runtime/tmp/mineloop2/run_both_inproc.py` 只调在册
  `card_binding.run_one`（与 `--mode run` 同一函数同一参数形状），窗口闸仍用门自己的尺
  `_in_ch_yield_window`（起跑 22:54:50 读数 None＝窗已让位，未用 override 旗）。
  这条如实记：**不是正门被绕开，是正门的跑法按内存现实重排**；两次 CLI 独立进程的失败面已留
  `.runtime/tmp/mineloop2/run_two.log`/`run_two2.log`。
- 转维护三班（非本班门位）：7.14 GiB 上限对"24 列×8 年面板"这类装载是否够，属设备容量问题；
  另 `system.errors` 里 `NO_ELEMENTS_IN_CONFIG: Volume default must contain at least one disk` 4 次（14:35Z）
  与 `CANNOT_PARSE_INPUT_ASSERTION_FAILED: expected 'columns format version: 1'` 9 次（10:47Z）同窗口出现，一并入眼。

## 十九、首张双臂分交卷（2026-10-12 23:04/23:05 实测，一卡两跑＝裁定甲）

### 19.1 两跑数值（分数册第 45/46 行，`docs/03_modules/_domain_backtest/exam_scores_v1.yaml`）

| 面 | 跑 1 `arms_variant=off`（开 vs 关臂二值全清） | 跑 2 `arms_variant=mid`（开 vs 中间臂无迟滞） | 卡面冻结门柱 |
|---|---|---|---|
| maxdd_improvement_pp | **+3.82** | **+1.64** | ≥5.0 / ≥1.0（后者键无机器面） |
| sharpe_delta | +0.0051 | +0.0890 | ≥ −0.1 ⇒ 两跑皆过 |
| turnover_delta_annual_x | **−0.978** | **−1.609** | ≤ 8.0 ⇒ 过（开臂换手反而更低） |
| open_sharpe@40bp | 0.5467 | 0.5467 | ≥ 0.0 ⇒ 过 |
| ic_delta_is / oos | −0.000278 / **nan** | +0.000220 / **nan** | oos_same_sign ⇒ 两跑皆败（nan 记败不冒判） |
| verdict | **fail** | **fail** | 两跑合议后＝不通过 |

逐臂净值面（n=2123 日，两跑的**开臂逐值全等**：maxdd 0.07974454598093661／sharpe 0.6702246613603534／
turnover 1.719598612281018／ann_ret 0.03637493831260426 ⇒ 同底座同成交口径的配对协议成立，
两跑唯一差异只在基臂档位）：关臂 maxdd 0.1180／sharpe 0.6651／turnover 2.697／ann_ret 0.0546；
中间臂 maxdd 0.0961／sharpe 0.5812／turnover 3.329／ann_ret 0.0381。

### 19.2 verdict=fail 的第一条成因与 §十六.2 预告逐字应验

两跑 fails 首条都是 `未支持判据键（机判面待扩）: ['maxdd_improvement_vs_no_hysteresis_min_pp',
'missed_crisis_trigger_max', 'whipsaw_roundtrip_ratio_max']`，且分数行
`unjudged.numeric_keys_not_read` 与卡面自报 `out_of_vocab_pillars` **三键逐字同集**；
`numeric_keys_no_machine_face` 为空 dict（不是"有面读不出"，是**根本没接**）。
⇒ 首张双臂分**结构上不可能是 PASS**（§十六.2 前置披露过，此处为实测应验，不是事后解释）。
中间臂那一柱 1.64pp ≥ 1.0 在数值上过线，但判官不认该键名，本班**不代它记成过**。

### 19.3 ⚑ 本次读数最重要的一条：KILL 驻留把 OOS 整窗变成空仓（等裁）

级别回放凭据（`arm_level_creds`，两跑同值，存 `10_/11_first_dualarm_*.yaml`）：

| 档 | NORMAL | WARN | DANGER | CRISIS | KILL | 转换次数 |
|---|---|---|---|---|---|---|
| levels_hysteresis（开臂用） | 299 | 69 | 193 | 148 | **1414** | 16 |
| levels_no_hysteresis（中间臂用） | 351 | 126 | 118 | 114 | **1414** | 81 |

`first_kill_date=2020-12-03`，样本共 2123 日 ⇒ **66.6% 的交易日处于 KILL**；
`kill_stuck_days=267`＝已进 KILL 且当日回撤其实已回到 kill_dd 阈值以内的那些日
（= 若"人工复位"存在本可放行却被近似钉住的 267 天，凭据面量化，不靠注释自觉）。
后果链：A2 追认的 **"L4 不可解除"近似** 让两臂在 2020-12-03 后敞口恒 0 ⇒
OOS 窗（2025-10-09..2026-09-30）整窗空仓 ⇒ 两臂 `oos_ic` 恒 nan ⇒ `oos_same_sign` 必败，
且所谓"回撤改善 3.82pp/1.64pp"的实质是**"2020 年那次清仓之后一直空仓"**。
本班不自解也不重跑（改复位规则＝改卡面语义，须新版本卡重新呈批），呈统筹三选一：
①承认该近似的读数含义即"本卡判的是 fail-closed 清仓纪律本身"，OOS 面判"不可判"而非"劣化"；
②另起 07b 新版本卡，把"人工复位"写成**可回放的规则**（如复位条件＝距 KILL 后 N 日且创新高），走 G4-5；
③判官侧补 `whipsaw/missed_trigger` 两柱机器面＋该键名映射立法（词表工单），本卡数值再读一次。
**不点会怎样**：07 卡按现冻结面重跑多少次都是 fail＋OOS 空窗，首张 PASS 候选不会从这里出。

### 19.4 试次两面账（照单申报，禁写单面话）

主区运行面（活账，`record_run` 同一单口）：52→**54** 条，`sum(n_trials)` 40,461→**40,463**（本班 +2）。
两条 batch_id：`examcard:<07>:2026-10-12` 与 `examcard:<07>:2026-10-12#run2-arms-mid`（后者带跑次判别位，
因 §十六.1 实测判官键无判别位被幂等跳过——**实测应验**：车道册内本卡只 1 条而分数册 2 行）。
git 面：本班这两条**未入 git**，且本班**不入袋**（§十七.1：该册工作区面已有他班 23 条未落地，
随袋即归属篡改）。车道副本已复位到 dev 字节（29 条，`git status` 净），复位前存证
`.runtime/tmp/mineloop2/evidence/lane_ledger_after_exam_20261012T2310.yaml`。
CH 取数照单：本班只读 `c1_market.kline_daily_hfq`（open/high/low/close 四场）与
`c1_market.technical_indicator`（在册冻结清单 24 列），装置侧进程内缓存，合计一轮装载。

### 19.5 卡面字节面处置：判官重排版**不入袋**，改按 dev 现值逐行重基（G4-5 卫生＋L3 在册处方）

`run_card` 出分后按在册行为重写卡面（`calibration_exam.py:730-737`），YAML 被 `safe_dump(width=120)`
重排 ⇒ 键级差虽仅 4 处，**行级差＝241 行**（实测 `Counter(dev 行)－Counter(lane 行)` 去重 231 行）。
本班据 L3 池面回退预筛（`enqueue_preflight.py:178 pool_regression_preclean`，在册先例
"先按 dev 逐行重基算账，再对自己改写行留 ack 旗"）判定：折行重排不是本班想要的变更，
**禁把重排版入袋**（拍回他人/上一袋的行面）。已改为以 dev 现字节为基重放本班改写，
落盘前后各断言一次，实得净差＝**去掉 3 行、追加 13 行**，且去掉的三行全是本班自己的：

| 去掉的 dev 行（全部=本班自有） | 换成的行 |
|---|---|
| `status: preregistered` | `status: examined` |
| `  run_id: null` | `  run_id: mineloop-dualarm_mid-07_熔断五级梯度减仓对照_五态仓位锚定` |
| `  score_row: null` | `  score_row: exam_scores_v1.yaml#rows[45]` |

追加的 13 行＝新键 `exam_scope_note_ruling_jia`（统筹裁定甲全文＋一句"本节取代上一键末句
'未裁前只开第一对'"），**旧 `exam_scope_note` 逐字保留**（在册"旧文不动＋夜版另起节"形态，
2026-10-12 已被统筹照准为现行）。落盘脚本内三道断言全部实跑通过：
①去行集恰等于上述三行；②对 dev 的值级差恰为 `.status/.lineage.run_id/.lineage.score_row`
且新增键恰为 `.exam_scope_note_ruling_jia`；③与判官重排版逐值对表，除 `exam_scope_note`
一处（该键在重排版里被替换，本班这版保留 dev 原文）外**零差**，且车道无独有键。
复核命令（主区直贴，期望 `removed= 上述三行`）：

```bash
python - <<'PY'
import subprocess, yaml
from collections import Counter
p='docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__07_five_state_cap_anchor.yaml'
dev = subprocess.run(['git','show','dev:'+p], capture_output=True, text=True, encoding='utf-8').stdout
new = open('.worktrees/st-mineloop2-20261012/'+p, encoding='utf-8').read()
print('removed=', sorted((Counter(dev.split('\n'))-Counter(new.split('\n'))).elements()))
d, n = yaml.safe_load(dev), yaml.safe_load(new)
print('old scope note preserved verbatim=', n['exam_scope_note']==d['exam_scope_note'],
      '| status=', n['status'], '| ruling_jia present=', 'exam_scope_note_ruling_jia' in n)
PY
```

## 二十、自纠一条归因（旧案卷留着不删）：§11.5 那条"他班存量红"作废

§11.5 原文照旧留档，其结论**错了**，此处更正：
`tests/backtest/test_calibration_exam.py::test_run_card_consumes_injected_ledger_path` 不是考试班的
"先落测试后落码"在途态。实测三面对表（23:4x，同一命令各跑一遍）：

| 面 | `grep -c ledger_registry_path`（码件 / 测试件） |
|---|---|
| `git show dev:` 码件 | **3** |
| `git show dev:` 测试件 | 1 |
| 主区工作树码件 / 测试件 | 3 / 1 |
| **本班车道工作树（更正前，即 2087d4160b 那份旧 blob）** | **码件 0 / 测试件 1** |

真因＝**本班车道的工作树面对 dev 变更过的件仍是旧字节**：我用 `update-ref`＋`reset`（mixed）
把车道指针对齐到 dev 时，**工作树不随动**（这正是我 23:2x 自己选的规避手法，规避了"快进会拍回
在途件"，却把盘面留在旧内容上）。实锤尺：`git hash-object` 读盘＝`ba7b62c908`，
而 `HEAD:`／`0a9f:`／`a9e2a0d:` 三处同一 blob `d91e0484ac`——盘上是 **20:55 那次指针对齐前
（2087d4160b）的旧内容**，考试班 21:11 的止血袋（d1301c3472）没进我的盘面。
差面规模实测：`git diff --name-status HEAD` = **347 件**（286 D ＋ 59 M ＋ 2 A），他域件也在内。

后果与教训（写死在册，免得下班再踩）：
1. **报红前先做三面表**（盘 / 本车道 HEAD / dev），并按 node id 逐支看，不看汇总计数；
   本班这次靠"单跑必红、合跑却绿"的反差才逼出机制——反差本身就是尺。
2. 更正后在真落地面复跑：`tests/backtest/{test_card_binding,test_calibration_exam,test_arm_protocol_binding}.py`
   ＝ **99 passed / 0 failed**（当时口径），后续 ③ 落地后为 **110 passed**（§廿一）。
3. 同步手法只在"本班在该件零本地改动"时使用：先 `git diff --quiet HEAD -- <件>` 核净差，
   再 `git checkout <dev> -- <件>`；本班当晚同步的正是这两件。

## 廿一、裁定③落地：三柱机器面＋键名映射（判官件扩面，含两条口径自呈与一处在册解析缺陷）

统筹裁定 2026-10-12＝三柱机器面**即刻立项、归本班域**（"判官件是你家"）。已实现并自证：

### 21.1 改了哪四处（全部只加读面，阈值与既有判决零动）

| 件 | 改动 | 行数 |
|---|---|---|
| `scripts/backtest/fexam/calibration_exam.py` | `_COMPARISON_KNOWN_KEYS` +三键；新 `run_card(arm_context=...)` 注入位（与在册 `ledger_registry_path` 同惯例）；`_judge_comparison(card, m, arm_context)`；新私有四件 `_spans_dates_all`/`_cap_series`/`_whipsaw_roundtrips`/`_crisis_misses`＋`_judge_arm_context_pillars`；读数与"本跑不判之柱"写进 `metrics.arm_face_readings`/`arm_pillars_owned_by_other_run`（分数册行因此自带凭据，审计不靠散文） | 头 INVARIANTS＋3 行 |
| `scripts/backtest/fexam/card_binding.py` | 新 `arm_context_for_judge(entry, base)`：只按册格 `series:<名>` 从在册底座取序列；`run_one` 注入并在 `ev["arm_context_injected"]` 自证（档名/变体/长度，不塞 Series 进 yaml） | — |
| `tests/backtest/test_calibration_exam.py` | ＋7 支（1 正证 pass／缺注入显式败／往返双向钉／两跑归属钉／多段危机钉／档位越界红证／注入位消费钉） | 41→48 |
| `tests/backtest/test_card_binding.py` ＋ `test_arm_protocol_binding.py` | ＋4 支装配红证；1 支旧断言随实（02 的越表清单由"含 whipsaw"改为"清空"） | 42→46 |

实测面：`tests/backtest` 全目录 **343 passed / 8 failed**，8 支全在
`test_factory_wiring_night.py`（他域），**正对照**同一文件在"主区码面（dev 字节，零本班改动）"
同样 8 failed / 7 passed ⇒ 存量红，非本班连带（`TASK_ROUTE` 在 dev/主区/车道三处命中数皆 0）。

### 21.2 三条口径自呈（读数怎么算的，禁事后挪门柱；如另有指定即改）

1. **`maxdd_improvement_vs_no_hysteresis_min_pp`**：仅当 `arm_context.base_arm_cfg ==
   "levels_no_hysteresis"`（即本跑基臂就是中间臂那档）时评 `maxdd_improvement_pp >= 阈值`；
   off 那跑不评该柱，改为写进 `arm_pillars_owned_by_other_run` 显式披露——
   **既不静默跳、也不越跑代判**。这正是裁定甲①"两跑合议"的机读形态。
2. **`whipsaw_roundtrip_ratio_max`**：分子＝开臂在 30 个交易日内的**档位反向变动次数**
   （先降后升或先升后降，两腿间隔按该序列自身交易日序号量距，非自然日）；
   分母＝基臂的**降档次数**（cap 变小一次＝风控触发一次，即卡面"关臂触发次数"在档位面上的读法）。
   分母为 0 ⇒ 记败（不可判不得当通过）。分子分母接反也是同一根柱的红，已配双向钉。
3. **`missed_crisis_trigger_max`**：对卡面 `window.regimes.crisis` 解析出的**每一段**危机窗，
   开臂段内出现任一"仓位上限 < 1.0"即算触发；段内无读数同样计一次漏触发（不可判≠确认）。
   档位取"cap<1.0"而非"cap=0"，读的是卡面原文"真实触发不缺席"里"风控动作发生"的最宽字面；
   若统筹要"必须进 CRISIS/KILL 才算"，一行即改（本班不自决收紧）。

### 21.3 顺带显形的一处在册判据面缺陷（呈裁，本班不自改）

`calibration_exam._span_dates`（既有件）对串内只取**前两个日期**，而 02/06/07 的 crisis 串是
`2020-02-01..2020-03-23 与 2024-01-02..2024-02-08（两处在册危机段）` ⇒ **第二处危机段被静默弃**。
影响面＝所有用多段串的卡的 `regime_ic`/`regime_gap` 读数（`_series_metrics`/`_panel_metrics`/
`_event_metrics` 三处消费）。本班**只在漏触发柱**上用新的多段解析器 `_spans_dates_all`
（新读面必须看全段），**既有 regime 面一字未动**——把它一并改掉＝历史卡的读数口径变，
属判据面变更，须统筹裁定后再做（已列为待裁项）。
正对照：新钉 `test_crisis_second_span_is_not_dropped_by_multi_span_string` 断言两段都出现，
若退回旧解析器该支必红。

### 21.4 一条工具层机制显形（转维护三班，非本班门位）

`card_binding.py:71` 以 `RUN_ROOT`（源自 `zephyr.shared.io.paths`，而 zephyr 由 usercustomize
**从主区预导入**，见在册"zephyr 预导入"条）把 `sys.path.insert(0, <主区>/scripts/backtest)`。
⇒ **在车道里默认跑 pytest，`fexam.*` 解析到的是主区码面**，本班改动测不到（假绿方向＝"我改红了但
显示绿"与"我改绿了实际没测"两种都可能）。实测两面差：同一批新测试，主区码面 2 failed
（`arm_context_for_judge` 不存在），车道码面 110 passed。
在册解法＝考试班已用的配方：`PYTHONNOUSERSITE=1` ＋ PYTHONPATH 指车道（本班当晚照此复核）。
治本建议（属他人件，本班不代改）：`RUN_ROOT` 应按**被调用件自身位置**解析而非按预导入的 zephyr 根。

### 21.5 PASS 结构性不可达的账，从今夜起改写

07 三柱从此有机器面；02 族（含 06）自冻结第一天申报的 `out_of_vocab_pillars` 三键**清空**，
分箱侧旧断言随实（§21.1 表内那支）。**但**：07 v1 卡面仍带 `out_of_vocab_pillars` 三键申报与
`kill_stuck` 那条 OOS 空窗事实（§十九.3），故 07 v1 重跑仍不是 PASS 候选——
可 PASS 的形态在 07b（复位规则）＋两跑合议面，见 §廿二。本班不自翻 07 v1 的 fail 结论。

## 廿二、裁定②呈批面：07b 草案已就位，只等参数值

草案落在 `docs/_working/mineloop2_campaign/01_card07_draft_and_approval.yaml` 新节
`card07b_draft`（本袋同批），内含：机器锚点逐字行号（`request_manual_reset:556`、
`ResetConfirmation:236-244`、`position_cap` 五态表与 `0.25*(step+1)` 阶梯 `:312-326`、
`recovery_step_recovered=(0.50,0.75,1-1e-6):162`、`min_hold_recovery_step=5:161`、
`recovery_freeze_days=5:169`、毕业准则六件 `:163-168`）；两档括号**预登记**（A 宽＝0.50/零冷却/不要求新高，
B 严＝0.75/20 交易日冷却/须创新高，B 的两个参数机器侧无对应在册值＝本班自拟，须随卡披露且禁挪他卡）；
**日频装置无笔级 PnL ⇒ 毕业准则不可评估**的缺口申报（甲案＝声明无面并入 not_judged 披露，
乙案＝改笔级回放面，跨域工期，本班不承诺），本班推荐甲案；
敏感性协议＝2 档 × 2 配对＝**4 跑、试次 4 入账、结论取两档同号**（成本实测：同进程共用一次底座装载）。
参数值批下来之前 07b 不起卡件、不开考。
