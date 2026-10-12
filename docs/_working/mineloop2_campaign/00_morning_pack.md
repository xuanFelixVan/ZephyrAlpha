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
