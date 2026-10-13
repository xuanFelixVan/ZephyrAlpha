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

## 廿三、统筹裁定 2026-10-13 接收对表（字母↔实质，逐条落到哪一行）

| 裁定 | 本班实做 | 落点 |
|---|---|---|
| ③三柱机器面＝验收 | 已在 0014 袋（pending 中），本班不重投不 self-sign | `00_morning_pack.md §廿一` ＋ q-0014 |
| 三条自呈口径＝照准 | 照准文本回填进码内注释与卡面，未改一字读数 | `calibration_exam._judge_arm_context_pillars` 族内四函数 |
| 07b 裁①甲案（毕业准则无面入 not_judged） | 07b 卡面 `reset_rule.graduation_criteria_face_declared_no_face` 声明；**不新增无面数值键** | 07b 卡件 |
| 07b 裁②两档都跑（4 试次、两档同号取结论） | 07b `exam_scope_note` 钉死四跑与"跨括号取同号，不同号即判规则选择未过稳健，不挑好的那档报" | 07b 卡件 |
| 07b 裁③B 档自拟值随卡披露＋禁挪他卡 | 原文照写进 `entry_brackets.bracket_B_strict.provenance` | 07b 卡件 |
| `_span_dates` 多段缺陷＝裁修（动前先出盘点） | 先出盘点（§廿四），再修三处消费者＋统一到单一解析器；受影响 07 的 2 行按 only-append 新 run_id 重读（CH 窗见 §廿四.3） | `calibration_exam._span_pairs/_in_spans` |
| RUN_ROOT 机制转维护三班 | 已转（§廿一.4 在册＋本节复述），治法属他人件，本班不代改 | 本节 |
| "三面表"教训入册 | 已入 §二十；并写进本班长期记忆 | `00_morning_pack.md §二十` |

## 廿四、`_span_dates` 裁修：盘点→改→重读三段账

### 24.1 盘点先行（生成器产出，零手抄；宪法 §9.5）

尺：`.runtime/tmp/mineloop2/regime_multispan_inventory.py`（会话临时件，**不入库**——
若统筹要长期尺，须按新建 .py 的 14 字段＋creation_token＋模块翻译登记另立一件，属净零评估项，
本班不自立）。产出：`docs/_working/mineloop2_campaign/12_regime_multispan_impact_inventory.yaml`。

实测分母（主区卡面，2026-10-13 00:4x）：**扫卡 518 张**；带多段 regime 串 **12 张**；
其中**真被弃第二段 8 张**（全部落在 `crisis` 键）；另 4 张的串是**三个日期**（尾注里带日期），
`pairs_full=1` ⇒ 新旧解析结果逐字同值，故 dropped=0 不计入返工面。
按 regime 键分布：`crisis` 8／`bull` 2／`bear` 1／`unavailable` 1。
**已有分数行的受影响卡＝1 张（07）共 2 行** ⇒ 重读面很小，不是全库级返工。
一处既有语义如实登记、本班未动：`TDM-E-L9-G4` 的 `unavailable` 串本不是区间声明而是历史起注
（"概念成分历史仅自 2026-08-10、广度快照仅自 2026-08-24、涨跌停表仅自 2026-07-20 ⇒…"），
旧实现按前两个日期切＝取到 2026-08-10..2026-08-24 这一段；修后 `_span_pairs` 结果与旧值同
（三日期只成一对），所以这条**不因本次裁修而变**，是否该给它真正的"非区间"语义属另一件（登记不代修）。

### 24.2 改动（一处解析器＋三处消费者＋一把尺收编）

- `_span_dates`（只返回前两日期）→ **`_span_pairs`**（串内全部成对日期）＋ **`_in_spans`**（并段布尔掩码）；
  单段串与无日期串的返回值与旧行为**逐字同值**（旧 fallback `(span, span)` 原样保留）。
- 三处消费者改为按掩码切片：`_series_metrics`（regime_ic）、`_panel_metrics`（regime_ic）、
  `_event_metrics`（regime 面的 `_event_face`）。
- `_event_face` 加 `mask=` 关键字（`lo/hi` 路径原样保留＝向后兼容）；
  实现中抓到并修掉一个真实错位：掩码按调用方序列索引算，`df` 是 dropna 后的对齐面（长度可差 1），
  按位置硬切会炸 `Item wrong length 4000 instead of 3999`——现按标签 `reindex(fill_value=False)` 对齐。
- **收编**：本班 ③ 时为漏触发柱另写的 `_spans_dates_all` 删除，`_crisis_spans` 改读 `_span_pairs`
  （§4.2 同真源可派生→必并，禁仓内并存两把 regime 尺）。

### 24.3 测试与重读计划（CH 窗实测后执行）

新增 4 支：解析器三形正证（单段同值／两段全取／无日期退回旧语义）、`_in_spans` 两段都掩到且段间不误掩、
**判别力主证**＝把关系只放第二段（旧实现读到 nan，修后必须 >0.5）、事件面并段后 `n_event` 等于两段之和。
实测面：`tests/backtest` 全目录 **347 passed / 8 failed**（8 支＝`test_factory_wiring_night.py` 在册存量红，
与修前的 8 支同一集合，未增未减）。

重读＝统筹令"受影响读数按 only-append 新 run_id 重读，旧行保留"：目标 07 的 2 行（off/mid 两跑），
判官侧 `regime_ic.crisis` 读数会因并段而变化（本班 07 首考的 `metrics.arm_open.regime_ic` 面即在此）。
**窗约束实测**：`card_binding._in_ch_yield_window` 现在（00:5x）返回 `01:00-04:00 夜跑让路窗（矿考循环班令 §三红线）`
⇒ 本班不在窗内抢跑，重读排 04:00 之后，且照 07 首考成例走同进程两跑（CH 内存墙 7.14GiB 在册）。
试次照单：重读 2 跑＝再记 2 条批次（带 run_tag 判别位，禁与首考两条混记）。

### 24.4 07b 卡件（②裁定的落地面）

`docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__07b_reset_ladder_anchor.yaml`
已起（ASCII 名循根宪法 §8；无 front matter，与在册卡形制逐字一致）。
在册尺自检：`triage_card` → `state=feasible_now`、`pending_numeric_params=[]`（初稿曾报
`仓位映射@无相邻数值`，已把那处散文改为指向 `data_binding.level_to_cap_map` 后复净）、
`out_of_vocab_pillars=[]`（③的直接后果）、`arm_count=3`、`pillars_route=dual_arm`。
`status=blocked_on_impl` **是本班自钉**：implementation_gap 四条未闭合
（①复位档 `levels_with_reset` 适配器未产，且复位必须调在册 `request_manual_reset` 而非自写分支；
②`arm_level_cap_multiply`/`_cap_series` 现对 RECOVERY 档名"未覆盖即抛"＝有意 fail-closed，需按卡面
`recovery_ladder` 表扩；③两括号入口参数须逐跑由绑定册注入禁硬编；④`_span_dates` 修与本卡重读同批）。
本班不自翻状态——落地袋合并 ①②③ 后，才由该袋把 07b 转 preregistered 并开考。

## 廿五、路径 1 补丁备好（待 Owner 否决窗）＋两处自纠与一份待补袋清单

### 25.1 补丁内容（车道备好，**未投**——生产风控件，明晨无否决才走正门）

`src/zephyr/risk/core/drawdown_state_machine.py` 纯追加 **+36/−2**，被替换的两行全部点名＝
①`[INVARIANTS]` 头注一行（加长，不改任何既有子句）②阶梯调用点一行
（`if not self.graduation_criteria_met(...)` → `if not self._graduation_leg_satisfied(...)`）。
新增面＝`graduation_face`（缺省 `required`）、`graduation_face_skips` 计数、
`DRAWDOWN_GRADUATION_FACE_ABSENT` 打点、未知取值 `InvalidDrawdownStateError`。

行为面实测（**车道码面**，先打 `module under test` 路径，防主区预导入假绿）：

| 档 | 复位后 6 个评估日（recovered_pct 0.6/0.8/1.0…） | 计数 |
|---|---|---|
| 缺省 `required`（＝旧行为） | `step=0 cap=0.25` 全程不动 | skips=0 |
| 显式 `absent` | 晋升至 `step=1 cap=0.5` | skips=1 |
| 取值拼错 | — | 直接拒（`[ZA-RK-0060]`） |

配套契约测试 5 支（`tests/gov/risk/test_drawdown_state_machine.py` 纯追加 +76/−0，全件 **49 passed**），
含两条"不许放宽"的钉：recovered_pct 门槛在两档下同结果；给足笔级数据时两档逐日同结果。

### 25.2 我自纠的两处（都写进卡面留痕，不删旧话）

1. **"机器侧无对应在册值"不成立**：`DrawdownStateMachineConfig` 同一个 dataclass 里就摆着复位守卫四值
   （:170-173），且 `request_manual_reset`（:556-600）逐条强制；我不但漏读，还把
   `reset_window_days=20`（自然日窗）当成了"冷却 20 交易日"。处置＝两档不再自造冷却、
   "须创新高"从两档删除（无对应物就删，不自拟）。负存在断言前必须先把**同族容器整列读一遍**——已入长期记忆。
2. **盘点尺有一处静默跳**：`window.regimes` 不是键值映射的卡（他班在册实测 22 张散文串）
   被我的 `if not isinstance(regimes, dict): continue` 直接漏出分母。已改为**单列计数并落册**：
   重跑后 `cards_with_non_dict_regimes_skipped_from_span_test=22`，与另一班那条独立对上了。

### 25.3 下一袋（0016）清单——0015 落地后一次整包投

- 生产件补丁 + 其契约测试（**Owner 否决窗内不投**，明晨无否决随本袋同批，含 07b 复位档适配器）；
- 07b 卡面更正版（本班 01:2x 已改：甲案申报改裁定原句、括号去自造参数、锚点补守卫行号、gap 加第⑤条）；
- 12_ 盘点册更正版（含 25.2② 的 22 条单列）；
- 01 册 `card07b_path1_received` 节（已写）＋本节班账；
- 07 两行 only-append 重读的产物（监视器已在跑：每轮先对齐基底，再由三道闸拒/放行，
  零 override 旗；日志 `.runtime/tmp/mineloop2/reread_07.log`，首轮 01:25 实测 `REFUSED: 裁修件未落 dev`＝闸真会拦）。

**在途事实如实报**：q-0015 里的 07b 卡面与 12_ 盘点册都是**更正前**的版本（袋快照即当时字节），
由 0016 覆盖；本班不撤袋不硬解队列仲裁。

## 廿六、07b 接线袋（0018）实测记录＋两处自造闸误杀的更正（2026-10-13 03:00–04:15 夜班）

### 26.1 本袋内容（两件代码＋两支测试＋一册格＋一张卡）

| 件 | 动作 | 本袋自证 |
|---|---|---|
| `scripts/backtest/fexam/card_binding.py` | 档位属性册 `DRAWDOWN_LEVEL_TIERS`（档名唯一真源，`DRAWDOWN_LEVEL_SERIES_NAMES` 由它派生）＋两枚复位档；`replay_drawdown_levels` 增 `reset_recovered_pct` 入参，复位**只调在册件** `request_manual_reset`；`drawdown_level_series_pack` 改**按册格点名取档、无默认全集**；新增 `_validate_recovery_ladder`（阶梯乘子表逐字对卡面）；`arm_context_for_judge` 加 `card` 形参并**申报**档位属性/括号值；`load_binding_book` 变体选择器改"按卡冻结"语义 | `pytest tests/backtest/test_card_binding.py`（基座自证见 26.4） |
| `scripts/backtest/fexam/calibration_exam.py` | 三柱的"本跑是不是迟滞对照"改读绑定层申报的 `arm_context.base_is_no_hysteresis`，**缺申报即显式记败**（禁按档名字符串猜） | `pytest tests/backtest/test_calibration_exam.py` |
| `docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__07b_reset_ladder_anchor.yaml` | 卡面补两张"拼好的表"（`five_state_native_with_ladder`／`binary_full_clear_with_ladder`）＋ `ladder_join_provenance`；`implementation_gap` ①–⑤ 逐件去向；`status: blocked_on_impl → preregistered`；`after_reset_ladder` 记一条实测结构发现（26.3 末） | 卡面可解析＋RECOVERY 三行零新数值（逐字=卡面 `recovery_ladder`；关臂按声明取 1.0） |
| `docs/_working/mineloop_campaign/02_binding_book.yaml` | 追加 07b 格四跑 `arms_variants.{off_A,off_B,mid_A,mid_B}`，`reset_trigger_recovered_pct` 逐跑 0.50/0.75；**纯追加**（写盘前断言 `Counter(旧行)-Counter(新行)` 删除行=0，实测 +129 行、15→16 格；由 `.runtime/tmp/mineloop2/append_07b_book.py` 先校验后落盘） | `pytest -k real_book_carries_07_and_07b` |

### 26.2 两条自造闸误杀（都是本班自己上一批写的，实测暴露，不是他班）

**误杀一：`arm_levels_same_source` 把 off 配对整体拦死。**
07/07b 卡面 `buckets.on` 原文声明"臂间差异只允许出现在级别→cap 乘子表与解除/复位规则上"，
off 配对（开臂五态 vs 关臂二值全清）**本来就共用同一条级别序列**。上一批我把"同序列"一律判非法，
后果＝07 的 off 跑与 07b 的 off_A/off_B 三跑全部装配不出。
时间线可核：首批双臂出分的 `as_of` 是 `2026-10-12T23:04:28 / 23:05:17`
（`10_first_dualarm_off.yaml`／`11_first_dualarm_mid.yaml`），而这道闸进 dev 的 commit 是
`316a8bac16`（10-13 00:58，0014 袋）——**闸晚于那两跑**：首批分数是真分，
但 04:00 的 07 off 重读会当场弹（我在写 07b 四跑前的**零 CH 预演**里撞到它，不是事后编的归因）。
现按实质拆三面：同序列＋同乘子表＝两臂逐字全等⇒红；同序列＋无迟滞档＝迟滞对照跑两臂同形⇒红；
同序列＋不同表＋迟滞档（off 配对）⇒放行。`test_arm_context_same_level_series_three_faces` 三面各钉一次。

**误杀二：`load_binding_book` 要求全册每张双臂格都含被点名的档。**
07 词表 {off, mid}、07b 词表 {off_A, off_B, mid_A, mid_B} 共用一本册 ⇒ 跑 off_A 被 07 那格弹
`arms_variant_unknown`，跑 off 又被 07b 那格弹——四跑与 07 重读互相堵死。
改为：**档名在全册并集里都找不到＝打字错必红**（`arms_variant_typo`，防"静默少跑一张卡"的保护没弱化）；
找得到而某卡词表不含它＝该卡不参与本跑（跳过；双臂卡 classify 不出双臂面，绝不降级成单臂出分）。
`arms_variant_required`（禁默认取第一档）一字未松。`test_load_binding_book_variant_vocabularies_are_per_card`。

### 26.3 复位档实测读数（设计路径，非随机游走）

夹具 `_crash_then_climb_nav()`：平顶 20 日 → 10 日跌到 0.65（进 KILL）→ 60 日单调爬回 1.05，共 90 交易日。

| 档 | 复位入口 | 放行 | 守卫拒 | 阶梯晋升 | KILL 驻留 | RECOVERY@0/@1 |
|---|---|---|---|---|---|---|
| levels_with_reset | 0.50（括号 A） | 3 | 3 | 1 | 33 | 19 / 11 |
| levels_with_reset | 0.75（括号 B） | 1 | 0 | 1 | 42 | 10 / 11 |

三条要如实报的：
1. **拒因来自在册件原文**：`RefuseResetError: [ZA-RK-0061] 距上次复位不足 3 日冷却期（已过 1 日）`——
   适配器零守卫分支，`refusals_first8` 凭据面逐条带日期，可复核。
2. **负对照**：同一适配器跑随机游走 700 日（`rng(7)` 负漂移）时四档全部 `resets_granted=0`、KILL=667 天
   ⇒ 复位入口不是无条件放行；哪天 granted 恒 >0 就是这道闸漂了（方向由
   `test_replay_bracket_b_resets_fewer_times_than_a` 钉）。
3. **路径 1 留痕可见**：`graduation_face=absent`＋`graduation_face_skips>=1`＋生产打点
   `DRAWDOWN_GRADUATION_FACE_ABSENT step=0 total_skips=1`，与统筹批准的申报文字一致。

**实测结构发现**（已写进 07b 卡面 `after_reset_ladder`，属在册件性质非本卡缺陷）：阶梯第 2 档→NORMAL
的门槛 `recovery_step_recovered[2]=1.0-1e-6` 在**任何日频净值回放面上不可达**——在册回补比例
（`src/zephyr/ex_core/risk_layer_orchestrator.py:884-888`）在 `dd>=0` 时返回 0.0，而 `recovered=1.0`
要求 `nav==peak` 即 `dd=0`；创新高当日峰/谷同时重置、比值归 0 ⇒ 深回撤后开臂长期停在 RECOVERY@2（cap 0.75）。
本班**不自拟替代门槛**（改 1.0-1e-6＝改判据，越权）。**转维护三班**核"生产面同样不可达"是否有意。

### 26.4 基座自证（不写这句就是假绿）

`PYTHONNOUSERSITE=1`＋`PYTHONPATH=<车道>/src` 下 `python -m pytest tests/backtest/test_card_binding.py
tests/backtest/test_calibration_exam.py tests/backtest/test_arm_protocol_binding.py` = **131 passed**；
`tests/gov/risk/test_drawdown_state_machine.py` = **49 passed**（0017 契约面）。
`card_binding.__file__` 打印为车道路径（在册坑复证：不设 `PYTHONNOUSERSITE` 时同命令加载主区码面，
见记忆 `fexam-pytest-in-lane-reads-main-code-20261013`）。⚠终验仍须落地后在主区复跑，本表不等价于落地面。

### 26.5 主区现场观测两条（都不是本班改的，如实登记＋证据）

1. **主区 index 有 9 条 `D ` 暂存删除**，其一正是本班刚落地的 07b 卡面
   （`D  docs/03_modules/_domain_backtest/exam_cards/exit_flow/X1/TDM-X-R1-01__comparison__07b_reset_ladder_anchor.yaml` 与同路径 `??` 并存＝`git rm --cached` 形状；
   HEAD `a1e8866ecd` 仍持有 blob `1f767cd567`）。本班未动主区 index、未 `git add`、未裸 commit；
   本袋经队列正门落地（serializer 从 dev 起面），落地本身即恢复该件。其余 8 条属他班，
   按"他役净删不代裁"只登记。复核：`git status --porcelain | grep -c '^D '`。
2. **他班测试面存量红 8 支（交叉验证，非本班引起）**：`tests/backtest/test_factory_wiring_night.py::TestMonthlyWindowBroadcast`
   在主区字节上（本班改动不在场）同样 8 failed / 7 passed，首因
   `AttributeError: module 'c4_batch_screen_wiring' has no attribute '_prev_oos_window_end'`
   （测试引用位：该文件 :224/:232/:250/:262；全仓 grep 该符号**只有测试与 `docs/_working/examrun_campaign/00_ledger.md:902,953`
   的自述**，无定义位）⇒ 是"测试件已落而码件腿未落/改名"的断链，**不是时间敏感 flaky**（
   失败点是被调符号不存在，与负载/时钟无关，复跑必同形）。owner=考试班，本班不代修。

### 26.6 本袋之后的在途动作（按通宵令自走，不等指示）

1. 0017（路径 1 生产件补丁）落地确认 → 0018（本袋）落地 → 在主区复跑 26.4 两条 pytest；
2. CH 让路窗（01:00–04:00）已过 ⇒ 单进程驱动连跑 6 次：07 重读（off/mid，only-append 新 run_id、旧行保留）
   ＋07b 四跑（off_A/off_B/mid_A/mid_B）；试次入账：07b 四条进 `n_trial_ledger`（预算册记 4），
   07 重读两条按 07 成例以带判别位 batch_id 补记并照单申报；
3. 两档同号取合议结论（跨括号不同号＝本卡判"规则选择未过稳健性"，不挑好的那档报）；
   分数册/卡状态/结果总表/凭据面（`arm_level_creds` 含复位与阶梯计数＋`not_judged_pillars`）同袋落；
4. 散文 22 卡转换：引用解锁班配方件落地后的路径节号（两道防线照案卷），未落地前不硬转。

## 廿七、散文 22 卡 `window.regimes` 表示层转换（解锁班甲案接手，2026-10-13 03:40–03:46）

**令源**：统筹通宵总令（02:30）预签附项——"散文 22 卡修法接手（转换配方待解锁班件落地后引用其路径节号，
两道防线照案卷）"。配方件已于 `35428dc00e`（10-13 02:58）落地，本节引用的节号逐条可 grep：
`docs/_working/examunlock_campaign/13_run_path_block_regimes_representation.yaml` 的
`symptom` / `root_cause` / `option_a_card_side_representation_fix` / `option_b_judge_side_tolerant_parser` /
`this_shift_recommendation: 甲` / `evidence_files` / `discipline`。
解锁班不自改的两条理由原文在册（①卡面 `impl_gap` 禁改卡面凑通＋`window` 属 JUDGMENT_KEYS；
②卡件属主=挖矿二班且当时判官件正被本班 0014 在途改）。本班接手是受统筹令授权，**署名本班、属主仍记挖矿二班**。

**普查复现（本班实测，零 CH）**：主区 527 张卡 `window.regimes` 形态 = dict 319 / NoneType 186 / **str 22**。
解锁班当时数是 518/310/186/22——**str 数一致（22）**，总数差 9 张＝这 40 分钟内他班又落了新卡（不是口径差）。

**动作**：22 张卡的 `regimes:` 那一行（单行标量）→ 两行映射，`bull`/`bear` 各一段：

```
  regimes:
    bull: 2019-01-04..2021-06-30
    bear: 2021-07-01..2024-01-31
```

| 防线 | 判据 | 实测 |
|---|---|---|
| 一 表示层等值 | 段名序一致＋日期串逐字相同＋散文内日期集合闭合；任一不合该卡不动 | 22 张全过：`skipped=0`（无一"顺手补段"） |
| 二 零判据漂移 | **行级替换**（禁整档 `yaml.dump` 重排他班卡字节）；`status`/`pillars`/`pillars_numeric`/`buckets`/`data_binding`/`card_id`/`window` 其余键逐字相等 | 22 张全过；Counter 差集里被去掉的行 100% 是 `regimes:` 那一行（脚本内 assert） |

**注记不丢**：原散文里括号注记（"（流动性牛）/（贴现率熊+微盘熊）——逐字继承 16 卡先例窗"）按配方丢弃于判据面，
但 22 条**原散文全文逐张留在** `.runtime` 生成器产出的日志册
`docs/_working/mineloop2_campaign/13_regimes_prose_conversion_log.yaml` 的 `original_prose` 字段
（该日志的 `as_of`/`discipline` 两键是本班在生成器改版前手工补记，已在件内 `manual_note` 如实声明；
`rows`/`counts`/`two_defenses` 全部生成器产出）。

**转换后实测（零 CH，只验表示层喂得进判官）**：对 `TDM-E-L1-S2__calibration__17_...` 调用
`calibration_exam._span_pairs` → `[('2019-01-04','2021-06-30'), ('2021-07-01','2024-01-31')]`（两段都在），
`_in_spans` 掩码命中 1324 个交易日；`tests/backtest/test_calibration_exam.py` = **54 passed**（车道码面）。
⚠ 本班**没有**对这 22 张卡开考（真缺口另两件＝物化件＋绑定册格，属解锁班/挖矿二班侧；
且解锁班已实测同一条链转换后判 **fail 不是 pass**，这条正是"非凑通"的证据）。

**车道前置动作（不做这条就是假普查）**：本班车道指针虽已对齐 dev，但工作树磁盘对这 22 张卡是旧面
（`glob` 实测：车道 497 张 / 0 张散文 vs 主区 527 张 / 22 张散文）——在册坑复现
（记忆 `lane-pointer-align-leaves-stale-worktree-20261013`）。本班先 `git checkout dev -- <22 件>`
把车道重基到 dev 现值（逐件校验 lane==dev 后才动手），转换器开头也有一道
"普查数不等于 22 即拒"的闸（实测：重基前该闸真的会拒）。

**主区 index 污染的第二条观测**（同一夜、同样非本班所改）：见 §廿六.5 的 9 条 `D ` 暂存删除。
本袋（0021）走队列正门，不动主区 index。

## 廿八、零 CH 预演挖出的两条本班自错＋一条 P0 口径事实（2026-10-13 04:00–04:10）

方法本身值得记：本班照解锁班的做法做了一次**零 CH 全链路预演**
（`.runtime/tmp/mineloop2/dryrun_07b_synthetic_face.py`，合成净值面喂真判官，scores/ledger 全指 tmp，
生产分数册 44918 字节一字节未动），六跑全通、`arm_face_readings` 与 `unjudged` 两面都在位。
就是这次预演挖出了下面两条——**如果直接上真 CH 跑，这两条会在"分数已写进册"之后才暴露**。

### 28.1 P0 口径事实：双臂跑的 r 位曾被外部指数面**无条件覆盖**（现已修，红证在册）

`card_binding.run_one` 里那行 `tgt = index_next_day_return()` 早于双臂接线（10-10 落，
`66d02fca0e0` 袋），双臂分支从 `arms_from_binding_book` 拿到的**底座日收益**被它盖掉，
判官实际吃的是 CSI300 指数次日收益（`index_next_day_return` docstring 自述）。
后果：双臂分数量的是"敞口 × 指数次日收益"＝**择时面**，而卡面声明的是
"三臂共用同一底层组合净值路径"＝**风控面**；`require_target_identity` 验完就把结果丢了——
它要防的正是这颗雷，而它没防住是因为**校验对象随后被换掉**（判"已防护"必测"谁调它＋能否改变行为"，
在册教训 `decorative-guards-without-callers-20260925` 今夜复证）。

改前红证（`tests/backtest/test_card_binding.py::test_arms_path_target_is_base_daily_return_not_index`）：
```
    tgt = index_next_day_return()
E   AssertionError: 双臂跑不许取外部指数面（r 位须＝底座日收益）
```
钉法是双道的：①`index_next_day_return` 换成"一调用就抛"的哨兵（实现若回退成无条件覆盖，
先炸在哨兵上，不会静默换面）；②间谍接住 `run_card` 收到的 target 逐值等于底座日收益，并核
`signal/signal_b/arm_context` 三件同时到位。修法＝把该行改成 `if tgt is None:` 兜底
（单臂/册格通道仍用指数面＝那些卡面本就如此声明，零变更）。

**已落地读数的影响（不粉饰）**：本班 10-12 23:04/23:05 那两张首批双臂分数（07 的 off/mid）
是在**指数面**上出的分，因此它们的正确读法是"择时面读数"，不是卡面命题的读数；
本班不撤行（分数册 only-add），改用 §廿六.6 的 07 重读（同一卡、修正后的面、新 run_id）作为
命题面读数，两代行并列在册。⚠同一条覆盖对所有走 `run_one` 双臂通道的卡生效，
**他班（如 06 卡双臂）若也经此路径出分，同样是指数面**——判据：
分数行的卡面声明"三臂共用同一基线净值路径"而落地码在 04:00 前含无条件 `tgt = index_next_day_return()`。
本班不代裁他班读数，登记供统筹/属主班复核。

### 28.2 混合档位 pack 自弹（本班 0018 内自错，同袋修）

`drawdown_level_series_pack` 曾把复位入口参数逐档原样递下去 ⇒
"一臂复位＋一臂不复位"的混合 pack 被自家 `reset_param_on_non_reset_tier` 弹死。
现改为：pack 级两道红先过（全非复位却给参数／有复位档却缺参数，都保留），
再**只把参数发给复位档**。新测试 `test_pack_mixed_reset_and_non_reset_tiers` 钉四点
（两条序列等长、非复位那条无 RECOVERY 档名、复位那条凭据带括号值且真放行过、两种错配仍红）。
07/07b 两张卡当前都不走混合 pack，所以这条不影响今晚六跑——但它是埋在码里的下一张卡的地雷。

### 28.3 交叉验证他班已完成件（通宵铁则"用你自己的尺实测验证一遍"）

- 解锁班 `docs/_working/examunlock_campaign/03_binding_book_event20.yaml` 20 格 ×
  本班 §廿七 转换后的卡面：**20/20 全通**（卡件存在、`window.regimes` 已是映射、
  `prose_quote` 仍逐字命中 `data_binding` 面）⇒ 本班这次转换没有打断他们的待跑清单，
  反而把他们诊断的表示层拦路解掉了。
- 解锁班 13_ 件的普查数复现：他们 518/310/186/22，本班 04:00 实测 527/319/186/**22**
  ——**str=22 一致**，总数差 9 张＝这 40 分钟内他班新落卡（不是口径差，已按此读）。
- 考试班测试面存量红 8 支的归因见 §廿六.5.2（被调符号不存在＝断链，非 flaky）。

### 28.4 两条口径披露（读数时必须带着看）

1. **阶梯档进 whipsaw/漏触发柱的形状**：`_whipsaw_roundtrips` 数的是 cap 序列的升降往返，
   RECOVERY@0→@1 的**阶梯晋升也是一次"升"**；`_crisis_misses` 的触发判据是"当日 cap<1.0"，
   阶梯档（0.25/0.5/0.75）**天然计为触发**（＝复位后仍在降风险，语义正确）。
   这两条不是 bug，但 07b 的抖动柱比 07 多算一类事件 ⇒ 跨卡比较 whipsaw 绝对数时禁不报此口径。
2. **07/07b 卡面各有一处引 `docs/_working/` 盘点册**（永久区引临时区，根宪法 §9.4 知识红线）：
   该指针是 0015/0016 已落地内容，本班本轮**未新增**同类引用；若判违规，删指针改述为
   "盘点见班账 §廿三/§廿六"即可，零判据影响。

### 28.5 ⚠本班自犯并自救一次：监视器的"按 dev 重基"把未落地工作面冲掉了

为了"落地面就绪就自动六跑"，本班起了一个监视器（`.runtime/tmp/mineloop2/run_six_watcher.sh`），
它每轮先 `git checkout dev -- <件>` 把车道重基到 dev 现值再跑预演闸——**这个动作本身是对的**
（在册坑 `lane-pointer-align-leaves-stale-worktree`：指针等于 dev 不等于盘面等于 dev），
但它漏了一条前提：**这批件里有本班尚未落地的编辑**（0018/0019/0021 三只袋此刻都在队列 pending）。
于是第 1 轮（04:14:58）就把车道盘面上的这些件拍回 dev 旧面——包含 07b 卡的状态转换、
双臂接线、复位档适配器、0019 的 `graduation_face` 补丁，以及**比 0021 快照还新的一处加固**
（阶梯 cap 非数值须具名红，见 §廿八.2 同族错的第二次）。

- 为什么没有真丢：入袋即快照，字节在队列 blobs 里（`pending/<qid>.json` 的 `blob_sha256`/`blob_ref`），
  本班按"按时间升序、后袋覆盖前袋"从 blobs 把 6 件写回车道，逐件校验 sha256==袋内值；
  回写后 `pytest tests/backtest/{test_card_binding,test_calibration_exam,test_arm_protocol_binding}.py
  tests/gov/risk/test_drawdown_state_machine.py` = **183 passed**，特征位逐项复核
  （`if tgt is None:`=1、四档档位册=在、07b `status: preregistered`、册格 07b=1 条、`graduation_face`=11 处）。
- 唯一需要手工重打的是"比快照还新"的那一处加固，已重打并补测试
  `test_ladder_caps_must_be_numeric_not_silently_coerced`（None/布尔/带引号数字/缺键四形态各红一次）。
- 监视器已用完成标记 `run_six.done` 令其在下一轮开头自行退出（不动别的进程），
  **六跑改由本班在袋全落地后亲手跑**；这条教训入记忆：任何"先重基再干活"的自动器，
  重基清单必须先排除"本会话有未落地编辑的件"，否则它就是个定时删除器。
- 顺带一条现场事实：车道 `git status` 此刻有 332 条 `D ` 与 87 条 `M`——`D ` 是
  在册的"soft 快进指针＋目录式 add ⇒ 索引呈假删除"形态（记忆 `soft-reset-index-phantom-deletions`），
  本班袋内一律显式列文件、从不传目录，故未受影响；他班件的本班一律不碰。

## 廿九、三段式晨间包（执行／自裁／等裁）——截至 04:30 的本班全量交底

> 通宵总令要求：三段式，理想态＝等裁段为空。本班此刻**等裁段不为空**（一件，见 29.3），如实写。

### 29.1 执行了什么（全部走队列正门，无绕门提交；每袋 `ENQUEUED` 后可用
> `python scripts/commit_queue.py status --session st-mineloop2-20261012` 复核）

| 袋 | 内容 | 状态（04:30 实测） |
|---|---|---|
| q-…-0018 | 07b 接线：复位档适配器（复位只调在册 `request_manual_reset`）＋判官申报位＋阶梯乘子表对卡面校验＋四跑册格＋卡面 `blocked_on_impl→preregistered`＋18 支新测试 | pending |
| q-…-0019 | 路径 1 生产件补丁 `graduation_face`（重投 0017；死因 GATE-ANY-ABUSE 整文件扫命中存量 `_trade_field`，按门自家行级逃生口加 `# noqa: any-abuse`＋在册理由，零行为改动） | pending |
| q-…-0020 | 散文 22 卡 `window.regimes` → 映射（解锁班甲案，两道防线）＋转换日志（生成器产出，22 条原散文全文留存）＋token 只注入本班一条 | pending |
| q-…-0021 | P0 修复：双臂 r 位不再被外部指数面覆盖 ＋ 混合档位 pack 自弹修复 ＋ 班账 §廿八 | pending |
| q-…-0022 | 红蓝加固：阶梯档值非数值须具名红（None/布尔/带引号数字/缺键四形态）＋ §廿八.5 自犯自记 | pending |

另已完成、不占袋的动作：零 CH 全链路预演（生产分数册 44918 字节零改动）、
解锁班 20 格 × 本班转换卡 的交叉验证 20/20 过、他班测试面 8 支红的归因复测（非 flaky，断链）、
主区 index 9 条 `D ` 暂存删除的登记（含本班 07b 卡一件，本班未动主区 index）、
reaper 防误杀登记（`run_six_watcher.sh`/`supplement_trial_six.py`）、记忆三条新增/复证。

测试账（车道码面自证，`PYTHONNOUSERSITE=1`＋`PYTHONPATH=车道/src`，`__file__` 打印为车道路径）：
`tests/backtest/test_card_binding.py`＋`test_calibration_exam.py`＋`test_arm_protocol_binding.py`
＋`tests/gov/risk/test_drawdown_state_machine.py` = **183 passed**；`ruff format --check` 与 `ruff check` 全清。

### 29.2 自裁了什么（按"预签裁定＞既定默认＞最保守可行"，逐件可回退）

1. **0017 死信不 requeue，改重投 0019**（统筹对 0011 的先例是"读 dead_reason 转维护班，不 requeue 不删件"；
   本班这条死因是门整文件扫命中**存量**违规，与本班内容无关，重投才是对症处置——
   修法是门自家登记的行级逃生口，不改判据、不加白名单、不动阈值）。
2. **`graduation_face` 补丁按预签令投**（否决窗今夜到期＝条件成就；补丁内容自 0017 起未变，
   新增只有那一行 `# noqa: any-abuse`）。
3. **两条自造闸误杀按实质修**（off 配对同序列／一册多卡变体词表）——保护面一条没松：
   同序列＋同乘子表仍红、迟滞对照跑同序列仍红、`arms_variant_required` 仍红、
   打字错改成全局并集判定后仍红（`arms_variant_typo`）。
4. **P0 r 位覆盖当场修并自曝影响面**（含"本班首两张双臂分实为指数面"这条不利自证；
   分数册 only-add 不撤旧行，用新 run_id 重读作命题面读数）。
5. **RECOVERY 第 2 档→NORMAL 不可达不自拟门槛**，按"改门槛＝改判据"越权红线，转维护三班核设计意图。
6. **散文 22 卡转换照解锁班甲案执行**（统筹令明文接手），署名本班、属主记挖矿二班，
   原散文全文逐张留册；两案中的乙案（放宽判官解析）未采用——它放宽的是判据面。
7. **监视器自犯冲掉未落地工作面一次**：立即停（写 `run_six.done` 令其下轮退出，不动别的进程）、
   从队列 blobs 按"后袋覆盖前袋"写回 6 件并逐件 sha256 校验、重打丢失的那处加固、补测试、
   183 passed 复测。**残余风险如实写明**：监视器的重基清单里仍含代码件——此刻安全，是因为本班已无
   未落地代码编辑（0018–0022 五袋快照含全部代码面，后续只动数据件与账目件，二者都不在重基清单内）；
   但这条前提是状态性的：**任何人（含本班）若要再改 `scripts/backtest/fexam/*` 或风控件，
   必须先 `touch D:/ZephyrAlpha/.runtime/tmp/mineloop2/run_six.done` 让监视器在下一轮开头退出**，
   否则它会把那件拍回 dev 旧面。六跑本身按"就绪才跑、跑一次即写标记退出"的单向门执行。

### 29.3 等裁什么（一件，且本班可自足推进）

**唯一等裁项：0018–0022 五袋的落地序与六跑的时窗。** 本班不能加速 serializer，
而六跑必须在落地码面上跑（车道绿不等价落地面绿）。为此已备：
`.runtime/tmp/mineloop2/run_six.py`（闸一逐件 lane==dev＋五枚特征位含 `_rung_cap`；闸二 CH 让路窗；
闸三六跑册格＋引句＋配对选择器零 CH 预装配）与 `.runtime/tmp/mineloop2/run_six_watcher.sh`
（就绪即跑一次、跑完即写 `run_six.done` 退出，禁重复跑），试次判别位补记器
`supplement_trial_six.py` 已备（默认 dry-run）。
**若统筹/Owner 先行落袋**：日志 `.runtime/tmp/mineloop2/run_six_watcher.log` 与
`.runtime/tmp/mineloop2/evidence/six_*.yaml` 即读数凭据，合议结论按裁定②"两档同号"读。
**若今晨袋仍未落**：本班读数缺口就如实挂红，不做任何"用旧面读数冒充新面"的替代（那是假绿）。

### 29.4 一条提请统筹注意的横向事实（非本班能自裁）

`run_one` 的 r 位覆盖是**通道级**缺陷，凡经该通道出分的双臂卡都在同一口径下（他班 06 卡双臂亦然）。
本班只修码面＋自曝本班读数，**不代判他班分数行的有效性**；建议由统筹定一条
"双臂分数须按 run 落地时刻标注 r 面"的统一读法（判据与本案位置见 §廿八.1）。

## 卅、增量三段式（05:1x–06:3x；§廿九 之后到本带的全部执行/自裁/等裁，读晨间包可只看本节＋§卅二）

### 30.1 执行了什么（逐项带实测锚点）

1. **路径 1 生产件补丁已落地**：袋 0019 done，`dev:src/zephyr/risk/core/drawdown_state_machine.py`
   含 `graduation_face` 11 处命中（Owner「投」的落地凭据）；commit 尾标 `[GW:st-mineloop2-20261012]` 在册。
2. **监视器 A 的重基从 `git checkout` 换成判据式对齐**（`align_lane_to_landed.py`，SKIP/ALIGN/PROTECT），
   判别力 5/5（含"被回退面必判 ALIGN"正对照）；首轮实测 `{'SKIP': 4, 'ALIGN': 0, 'PROTECT': 5}`＝在途零写入。
3. **恢复他人被回退的落地内容一枚**：`mineloop_campaign/99_checkpoint.md` 少 46 行 → 按 HEAD 归位，
   前后两版存证（517/471 行）。
4. **认腿之洞当场闭合（改道）**：绑定层 `base_arm_cfg` 契约改判为迟滞族档名，袋 0026（−1/+9＋4 条断言）；
   变异自证＝退回原写法即 `AssertionError: ('mid_A', 'levels_no_hysteresis_with_reset')`。
5. **22 卡散文转换重投**＝袋 0027（0020 死于热册连坐）：先按 dev 逐件重基（22/23）→ 重跑转换器
   （planned=22/skipped=0/yielded=0）→ 三道独立复验 22/22＋端到端 `_span_pairs` 44/44 `SPANPARSE PASS`；
   并自我更正为**段内标注逐字保留**（07 家形）。
6. **试次补记器修掉一处少记**（跨卡累加⇒六跑会少记 1 只）：改逐卡差额各算，红证 4 例
   （新 4／旧 3／幂等 0／未落地 0）。
7. **交付门加固＋红证**：B 增闸⓪（等 A 的 `run_six.done`，防"分数齐、试次半套"投递）；
   弃建 `14_07b_four_run_results.yaml`（CREATE-GUARD 连坐面＋净零）；红证 8/8。
8. **卡面/册格对抗改写 12/12 具名拒绝**（`adversarial_07b_face.py`），并如实更正本班探针自己的三处误判。
9. 两个监视器轮询上限抬高（A 200 轮、B 400 分钟）后重启在岗；keep 册补 `reread_watcher.sh`。

### 30.2 自裁了什么（逐条带依据）

1. **不与他班抢 `calibration_exam.py`**：判官扩面腿 parked（`evidence/judge_leg_park/`，含 92 行补丁），
   车道该两件已按 HEAD 归位；依据＝通宵铁则"遇同文件他班在编＝登记后置或改道"＋他们车道该件 +50/−1 实测。
2. **误收他班活锁后即刻 release 归还**，不代签、不趁占；依据＝同条铁则＋"锁不在册≠对方写完了"。
3. **0021/0022 不救**：它们带的是箭头未修的前像字节，随落地序自然死（在册"在途袋会因车道自己后落地
   变成回退弹，让它死勿 requeue"）；代价如实登记＝各占传送带一格（当下 16–20 分钟/格）。
4. **主区 index 的陈旧混合池不自理**：那是共享暂存面，`git reset` 会冲掉他会话正当暂存内容＝抹他人在途；
   依据＝宪法 §3.4 owner 责任制＋"不抹不退"。只登记＋移交＋自带两道 canary。
5. **弃件而非补册**：不新建读数件，读数真源＝分数册当日行（依据＝§4.1 全资产净零；零消费者＝净增资产）。
6. **族名归一的语义自裁**：`base_arm_cfg` 从"册内序列名"改判为"迟滞族档名"，真实册名另键保留；
   这不是改判据（阈值/柱定义零动），是把"绑定期交出去的档名"与"判官认腿的档名"对齐——
   07 面族名==册名逐字不变，故历史读数不受影响。

### 30.3 等裁/等他人什么（本带新增四条，全部非本班权限）

1. **死会话 st-gpuwo-20261011 的接管台账**：它的开条目把 `capability_canonical_file_registry.yaml`
   锁在 TAKEOVER-PENDING 门外（判据实测：其 worktree dirty=52、三只死袋待处置、pid 30476 亡）。
   后果＝任何"需要携带该热册"的袋都会死。处置面＝该 sid owner／统筹／维护三班（Rx 已在 dead_reason 里）。
2. **主区 index 的 11 枚纯删除**（含本班 07b 卡与 8 张 agg 卡）与 68 件陈旧副本：谁落地谁负责，
   但**清理权不在本班**；数字与复核命令见 §32.7 事件 B。
3. **判官腿的投与时机**：待 st-minedig2 复 claim 或其面落地（§32.6 三步＋三查已备好）。
4. **§29.4 那条横向事实仍无回复**（双臂分数行的 r 面按 run 落地时刻统一标注——统筹定读法，
   本班只修码面＋自曝本班读数，不代判他班分数行有效性）。
5. §廿九 唯一等裁项（袋序与六跑时窗）本带仍在走：0023–0027 在队，六跑由监视器 A 在落地面追平后自动开考。

## 卅一、整块交接卡（上下文若断，接手者按本节继续；每条命令都已在 04:3x 实测跑过）

编号说明：§卅 号段未用——六跑终局读数由交付生成器写成 §卅二（它按落地顺序在最后追加，见 31.3 的 B 条），
空一个号是编排选择，不是丢节。

### 31.1 现在这台流水的状态（一句话）

五只袋在队列里排着，两只监视器在等它们落地：A 负责**跑六次**，B 负责**出交付袋**。
两者都写成"就绪才动、不满足就拒、只动一次"，都不会把没跑成的东西投成已交付。

### 31.2 在途袋（`python scripts/commit_queue.py status --session st-mineloop2-20261012` 可复核）

| qid 尾号 | 装的是什么 | 若死的处置 |
|---|---|---|
| 0018 | 07b 接线（复位档适配器＋判官申报位＋四跑册格＋卡面转 preregistered） | 读 dead_reason；若是"双侧皆改真冲突"＝他班同期改了 `card_binding.py`，按 dev 现值重基后**新袋**重投（勿 requeue 旧袋） |
| 0019 | 路径 1 生产件补丁 `graduation_face`（含 `# noqa: any-abuse` 存量豁免） | 同上；这条不死，07b 复位档就跑不了（config 会 TypeError） |
| 0020 | 散文 22 卡表示层转换＋转换日志＋token 单条 | 死了不影响 07b；重投前先 `git checkout dev -- <那 22 件>` |
| 0021 | P0：双臂 r 位不再被指数面覆盖＋混合 pack 修复＋班账 §廿八 | 死了则六跑**不得**跑（r 面仍是错的）——监视器 A 的特征位会自己拒 |
| 0022 | 阶梯 cap 非数值须具名红＋班账 §廿八.5 | 死了不影响读数，只少一支测试 |

### 31.3 两只监视器（路径／日志／停法／预算）

- A：`D:/ZephyrAlpha/.runtime/tmp/mineloop2/run_six_watcher.sh`，日志
  `D:/ZephyrAlpha/.runtime/tmp/mineloop2/run_six_watcher.log`；每 180s 一轮，满 60 轮（≈3h）自停。
  就绪判据在 `run_six.py` 闸一里（逐件 lane==dev ＋ 五枚特征位：四档档位册、三参 `arm_context_for_judge`、
  `graduation_face`、`if tgt is None:`、`def _rung_cap(`）。
  **停法**：`touch D:/ZephyrAlpha/.runtime/tmp/mineloop2/run_six.done`（下一轮开头自己退，不动别的进程）。
- B：`D:/ZephyrAlpha/.runtime/tmp/mineloop2/deliver_six_results.py --watch`，日志
  `D:/ZephyrAlpha/.runtime/tmp/mineloop2/deliver_six.log`；每 60s 一轮，满 180 轮自停。
  拒投条件（任一）：07b 四跑缺任一／某跑 verdict 为空／闭环两面（分数册行 `unjudged`、
  metrics `arm_face_readings`）缺任一／**分数册旧行少任何一条**（内容级回退直接拒）。
  **停法**：`touch D:/ZephyrAlpha/.runtime/tmp/mineloop2/delivered_07b.done`。
- 两条已在 `data/runtime/process_reaper_keep.txt` 登记子串（`run_six_watcher.sh`/
  `supplement_trial_six.py`/`deliver_six_results.py`），防被 reaper 误杀。

### 31.4 接手者要做的三件事（顺序不能换）

1. 等 A 的日志出现 `DONE 标记已写`，再看 `D:/ZephyrAlpha/.runtime/tmp/mineloop2/evidence/six_summary.yaml`
   与同目录 `six_<跑次>.yaml` 六个证据件；合议结论按裁定②读（两档同号才算稳健，
   不同号＝判"规则选择未过稳健性"，**不挑好的那档报**）。
2. 核 B 是否已投出交付袋（日志末行 `投递完成` 或队列里新增一只袋）；若 B 报了拒投理由，
   **先补跑/先修，禁手工拼一个"看起来齐"的交付**。
3. 落地后在**主区码面**复跑一次测试（车道绿不等价落地面绿）：
   ```
   cd /d/ZephyrAlpha && PYTHONNOUSERSITE=1 python -m pytest \
     tests/backtest/test_card_binding.py tests/backtest/test_calibration_exam.py \
     tests/backtest/test_arm_protocol_binding.py tests/gov/risk/test_drawdown_state_machine.py -q
   ```
   期望：全部 passed（本班 04:2x 在车道码面实测 183 passed，主区落地面同一命令**尚未跑过**——
   这句就是留给接手者的活，别替它背书）。

### 31.5 本班名下未闭的账（不装完）

- 07b 六跑读数与合议结论（等 A/B）。
- 主区落地面复跑 31.4 第 3 条（等落地）。
- 转维护三班两条：`RUN_ROOT` 机制（§廿五已转，复述于此）、RECOVERY 第 2 档→NORMAL 门槛不可达（§廿六.3 末）。
- 转维护四班一条：ALGO-NOTE-SYNC 对折叠块内改注不认（改键行才归属得到）。
- 提请统筹一条横向：双臂 r 面"按 run 落地时刻标注"的统一读法（§廿九.4）。
- 临时件清理：`.runtime/tmp/mineloop2/` 下本班脚本在收官前**不删**（两只监视器正在用），
  监视器退出且交付袋落地后再清；项目根目录当前零临时件（`git status --porcelain` 抽看过，
  未跟踪仅 `.runtime` 内）。

### 31.6 Owner 裁定「投」入账（04:40，否决窗关闭）

原文与处置逐字记在 `docs/_working/mineloop2_campaign/01_card07_draft_and_approval.yaml` 的
`owner_ruling_tou` 节（含"未带裁定号故本班不自行往 ruling_registry 编号"这一条）。
对本班的**实际增量＝零**：路径 1 补丁早已按预签令备成袋 q-…-0019 在队，字节一字未改；
Owner 这道令关掉的是否决窗，不是新增动作。既定链保持自走：
07b 冻结稿已随 0018 在途 → 绑定册四跑格已随 0018 → CH 让路窗已过（04:00 后）→ 四跑由监视器 A 在落地码面上跑 →
两档同号取合议（不同号就按裁定②读作"规则选择未过稳健性"，不挑好的那档报）。
04:40 队列实测：dev 每几分钟前进一笔、13 只在途 1 只 processing＝convoy 不是楔死，
本班不动 serializer 租约、不加急插队（避免他班袋被我的优先级挤后）。

### 31.7 0018 落地利器打死在 MSG-STYLE 一次（05:04），对症修后重投为 0025

死因（`dead_reason` 原文）：`门禁 MSG-STYLE 阻断 ... card_binding.py:1018 raise RuntimeError(...)
[unicode_arrow]`——我写的复位阶梯越界消息里用了 `0→1→2→NORMAL` 的 Unicode 箭头。
这条门是 2026-09-23 起 own 化的 AST 级检查（只查 raise 的异常消息，tests/ 豁免），
所以 docstring/注释里的箭头不受影响，**只有那一行违规**。

处置与自查：
- 修法＝把该条消息改成 ASCII `0->1->2->NORMAL`（零语义改动，禁加 `noqa: MSG-STYLE` 绕过——
  门给了行级豁免口，但这条不是误报，是我不合现行风格规范）；
- 重投前把三只码件（`card_binding.py`/`calibration_exam.py`/风控件）的**全部 raise 消息**
  按门的判据自扫一遍（AST：含 U+2192 或以「。」结尾）＝**违例 0**；
- 一次恢复踩到的第二个坑要说清：我第一次按"袋 json 的 mtime"取最新面，而 0018 恰好在 05:04 转 dead
  改写了它自己的 json ⇒ 把 0022 的新内容倒灌成 0018 旧内容（少了三支测试）。
  已改按 **qid 序号**取最新并逐件 sha256 对袋内值，特征位复核：`if tgt is None:`=在、
  `def _rung_cap(`=在、三支新测试=3/3、`pytest tests/backtest` 三件=**134 passed**；
  教训＝"mtime 等于新旧"在这种会被系统改写的元数据上不成立，取版本要用**编号**不用时间戳。
- 0021/0022 两只袋带的还是带箭头那份，落地时会同门同死——不撤不回，0025 是它们的严格超集
  （含 r 面修复＋混合 pack 修复＋阶梯具名红＋本次风格修），落地后一切以 0025 为准。

### 31.8 后置登记：判官件 `calibration_exam.py` 一条腿让给在编他班（05:1x）

claim 实测：`scripts/backtest/fexam/calibration_exam.py` 由 **st-minedig2-20261012**
持有（task 串＝"通宵总令§四 聚合8卡可考（复算＋物化＋转态）"，剩余 68.4 分钟）⇒
按通宵铁则"遇同文件他班在编＝登记后置或改道，禁硬闯"，本班把这一腿**拆出 0025 袋**，
其余 5 件（双臂适配器/两支测试/07b 卡/绑定册/班账）先走；判官腿待锁释放后单独一袋投。

为什么不能"先跑起来再说"：0025 落地后 `card_binding` 会把 `base_is_no_hysteresis` 申报进上下文，
而**旧判官仍按档名字符串匹配** ⇒ 07b 的 mid 跑会把三柱读成"归另一跑"（两跑都不判＝静默少判，
不是假绿就是漏判）。所以本班同时在 `run_six.py` 闸一里加了一枚硬特征位
（`calibration_exam.py` 文本须含 `if "base_is_no_hysteresis" not in arm_context`），
判官腿未落地 ⇒ 六跑**照旧拒跑**。这条与"0018 死了不许半套开跑"是同一道纪律。

## 卅二、落地面自动器的自我排雷＋七条护栏变异自证（2026-10-13 05:1x–05:3x）

> 缺号如实登记：§廿九 之后本班把交接卡直接编为 §卅一，**§卅 从未写入**（`grep -n "^## "` 号差集
> 已核：dev 33 节 → 车道 38 节，新增恰为 廿六/廿七/廿八/廿九/卅一）；本节按顺延编号卅二，
> 监视器 B 的终局读数节相应改为 **卅三**。不回填占位、不改旧节号（在册"更正另起、留旧案卷"）。

### 32.1 监视器 A 的"重基"从 `git checkout` 换成判据式对齐（同根因第三次自伤后收口）

- 事实：A 原第 20 行 `git checkout dev -- $FILES` 无差别重基 9 件，而清单里同时含本班 4 件**未落地在途件**
  （card_binding/07b 卡/绑定册/判官腿）。今夜该机制已两次把未落地成果洗回旧面（案卷＝§卅一.7）。
- 修法：新增 `.runtime/tmp/mineloop2/align_lane_to_landed.py`，三态判据
  SKIP（逐字等值）／ALIGN（车道相对 dev **零新增行**＝纯滞后或被回退→取 dev 现值，写前先快照 `evidence/`）
  ／PROTECT（车道含 dev 没有的行＝在途作者面；或该件出现在本班 pending/processing 袋 files 清单里，无条件保护）。
  袋态按**目录名**判定，不按袋内 `state` 字段（该字段实测恒缺）。
- 判别力自证（尺子须能红）：
  `python D:/ZephyrAlpha/.runtime/tmp/mineloop2/align_lane_to_landed.py --selftest`
  → `SELFTEST PASS`（5 例：等值/纯删/加行/改行/正对照"被回退面必判 ALIGN"）。
- 落地面实测（A 于 05:19:48 起第一轮）：`SUMMARY {'SKIP': 4, 'ALIGN': 0, 'PROTECT': 5}`——
  在途 5 件零写入，滞后 0 件；A 已换新脚本重启，keep 册子串 `run_six_watcher.sh` 在册。

### 32.2 交叉验证挖出"他班已落地内容被本班车道回退"一枚（不抹不退，已复原）

- 事实：`docs/_working/mineloop_campaign/99_checkpoint.md` 车道盘面比 dev **少 46 行**
  （整节 §19"通宵执行与晨间裁定包"消失），git 侧呈"未提交的纯删除"，且该件不在本班任何袋里。
  根因＝§卅一.7 同一根因的第二个受害者：按袋 JSON **mtime** 复原时把旧快照搬进了非在途件。
- 处置：`git checkout HEAD -- docs/_working/mineloop_campaign/99_checkpoint.md`（HEAD==dev，
  纯恢复他人落地内容，零手改）；前后两版存证
  `.runtime/tmp/mineloop2/evidence/99_checkpoint_{dev_head_0518,lane_with_46line_deletion_0518}.md`
  （517 行 vs 471 行），复原后复核 `lane==dev OK`。
- 教训升级（写进 32.5）：按 mtime/按目录批量取回＝跨件污染；复原必须**逐件**先判"本班是否在其上作者"。

### 32.3 监视器 B 两处加固：不抢跑试次账、不新增净零外资产

- 闸⓪（新增）：B 原只看 `evidence/six_summary.yaml` 就绪即投，而 A 是在六跑**之后**才补试次
  ⇒ 存在"分数齐、试次半套"的投递窗口。现要求 A 的 `run_six.done` 先落，否则拒投。
- 弃件：原计划机生 `docs/_working/mineloop2_campaign/14_07b_four_run_results.yaml` **不投**。两条理由：
  ①新建 .yaml 须 CREATE-GUARD creation_token，而 token 在热册里 ⇒ 与热册同袋即"整档快照回退他人 token"
  的在册连坐面（热册蒸发族）；②读数真源已是分数册，§卅三 是人读面，第三份拷贝**零消费者**＝违 §4.1 全资产净零。
  B 改为：§卅三 的数字直接回指分数册当日行＋试次台账，`art["machine_source"]` 记真源指针。
- 红证八例全判别：`python D:/ZephyrAlpha/.runtime/tmp/mineloop2/probe/redproof_deliver_b.py`
  → `REDPROOF PASS`／`SUMMARY {"cases": 8, "fail": []}`——
  逐条命中"A 未写 run_six.done"/"six_summary 缺失"/"07b 四跑缺 ['off_B']"/"verdict=None 未出分"/
  "闭环 unjudged 缺位"/"闭环 arm_face_readings 缺位"/"分数册丢他人行"，并含一条"全绿对照⇒必须放行"。
  合成输入全在 `tempfile.TemporaryDirectory()`，零生产路径写入（§9.6）。

### 32.4 变异自证：把七条护栏挨个关掉，要求配套测试必红

基线＝车道三测试件 `167 passed in 8.14s`（`PYTHONNOUSERSITE=1 PYTHONPATH=<lane>/src`，
在册坑"车道裸 python 导主区包"已避）。命令：
`python D:/ZephyrAlpha/.runtime/tmp/mineloop2/probe/mutation_proof.py`

| # | 关掉的护栏 | 位置 | 实测 |
|---|-----------|------|------|
| M1 | 双臂 r 位不再被指数收益覆盖（P0） | card_binding.py:1575 `if tgt is None:`→`if True:` | 1 failed / 63 passed |
| M2 | 引句逐字落在卡面臂协议域 | arm_protocol_binding.py:161 →恒假 | 1 failed / 79 passed |
| M3 | `graduation_face=absent` 跳过必计数 | drawdown_state_machine.py:549 →恒假 | 1 failed / 48 passed |
| M4 | 判官只读绑定层申报位，禁按档名猜档 | calibration_exam.py:503 →退回旧字符串匹配 | 1 failed / 53 passed |
| M5 | 阶梯档值非数值必红（`float(None)` 洗错） | card_binding.py:1317 →恒假 | 1 failed / 63 passed |
| M6 | 册格阶梯须等于卡面冻结过的三元组 | card_binding.py:1367 →恒假 | 2 failed / 62 passed |
| M7 | 复位档乘子表须整表覆盖三档 | card_binding.py:1362 →恒假 | 2 failed / 62 passed |

- 结论：**7/7 被配套测试抓到**（`MUTATIONPROOF PASS`，non-binding=∅）；每轮跑完即按 sha256 逐字还原，
  四件还原后 diffstat 与跑前一致（card_binding +464／calibration_exam +16／state_machine +40／
  arm_protocol_binding 零差），锚点计数 `if tgt is None:`/`0->1->2->NORMAL`/`def _rung_cap(`/
  `if "base_is_no_hysteresis" not in arm_context`/`if q not in _squash(arm_blob(card)):` 均=1。
- 判读口径（不夸大）：这条证的是"本班测试**bind** 这些护栏"，不是"护栏覆盖全部错型"；
  后者仍需 §卅一 移交项（RUN_ROOT、step-2 毕业不可达）在落地面复跑才算。

### 32.5 自设纪律（今夜同根因第三次后才写死）

凡在**共享件或本班在途件**上做写操作的自动器（重基、复原、补记、投递），必须先给出
"该件此刻是否本班在途"的机械判据，缺判据即拒写；判据本身须有正对照（能红）才准上岗。

**上岗后的第一轮实测回报（06:2x）**：自检回路七项在 §32.13 恢复之后全绿
`SELFCHECK PASS`（引用面 69 缺件 0｜遗留标记 0｜项目根零临时件｜yaml 26 件全可解析｜
袋与车道同调：末袋吞未知行 0｜持锁：过期 0｜尾标陈述）。
其中"持锁"一项全绿是靠**清掉本班五枚陈旧 claim** 换来的——`config/trading_decision_map.yaml`、
`drawdown_state_machine.py`、`test_drawdown_state_machine.py`（0019 已落地）与
`test_calibration_exam.py`、`capability_canonical_file_registry.yaml`（腿已 parked／袋已死，不再需要）；
释放清单与命令＝`.runtime/tmp/mineloop2/claims_release_stale.txt` ＋
`python scripts/lock_files.py release-batch st-mineloop2-20261012 --files-from <该清单> --no-warn`。
判据口径：claim 的存续期＝"该件仍在 pending/processing 袋里"，袋落地即释放（占着不放＝挡别人）。
第二轮同项复绿才算"两轮连续干净"（完工判据 2），届时在 §卅三 之后追记。

### 32.6 待投件（唯一剩余本班腿）＝判官腿 0027（原编 0026，因 §32.8 改道袋占号），一键已备好

现值实测：`scripts/backtest/fexam/calibration_exam.py` 车道相对 dev ＝ **+16/−1**
（把 `arm_context.get("base_arm_cfg") == "levels_no_hysteresis"` 的档名猜档，换成只读绑定层申报位
`base_is_no_hysteresis`，申报位缺位即如实记败）；`tests/backtest/test_calibration_exam.py` ＝ **+40/−0**
（5 处引用该申报位，M4 变异实测 `1 failed / 53 passed`）。
占用实测：该件由 **st-minedig2-20261012** 持锁（05:14 复测剩余 64.8 分钟 ⇒ 约 06:20 到期）。

锁一释放即按下列三步投（禁在主区直改，禁抢他班锁）：

```
python scripts/lock_files.py check scripts/backtest/fexam/calibration_exam.py
python scripts/lock_files.py acquire-batch st-mineloop2-20261012 \
  --files-from .runtime/tmp/mineloop2/files_27.txt --session st-mineloop2-20261012 --ttl 120
python scripts/git_commit.py --session st-mineloop2-20261012 \
  --files scripts/backtest/fexam/calibration_exam.py,tests/backtest/test_calibration_exam.py \
  --message-file .runtime/tmp/mineloop2/bag_msg_27.txt --keep-message-file \
  --allow-multi-domain --enqueue
```

`files_27.txt`/`bag_msg_27.txt` 已随本批写好（见 `.runtime/tmp/mineloop2/`；`_26` 号已被 §32.8 的
改道袋占用——本腿是 0027，改道袋是 0026，勿混）。
0026 落地是六跑闸一的最后一枚特征位；在它落地前 A/B 两个监视器**照旧拒跑**（§卅一.8 同一道纪律）。

### 32.7 两起对外事件（都不是我造的损害，但都经本班之手被看清）

**事件 A｜本班续租时收走了他班**未过期**的 claim（05:40，已即刻归还）**

- 动作与后果：`lock_files.py acquire-batch` 续 31 件，其中 `scripts/backtest/fexam/calibration_exam.py`
  的持有者由 **st-minedig2-20261012** 变成本班。读数对不上工具谓词：05:14 `list` 显示该锁"剩余 64.8m"、
  05:32 `check` 显示"已锁定 118.4m"，而 05:40 批量收购成功——即 `_claim_expired_and_idle`
  在本路径上把一个按 `expires_at` 尚未过期的他班 claim 判成了可回收。
- 本班处置：05:41 `release` 归还为 FREE；期间**零字节写入该件、零袋含该件**（0025 袋投时就已把它拆出，
  §卅一.8）；随后主动把待投判官腿改道（§32.8），不与他们的在编面抢同一件。
- 他们侧现状（只读实测）：该件车道面相对 dev **+50/−1**（`target` 多日标的前向面申报位，未落地、未见其后袋）；
  三查＝末袋 02:00（done）／60min 内零新写／最近 60 笔 commit 无本班外尾标命中他们。
  三查只证"此刻没动"，不证"写完了"——所以**"锁现在不在册"绝不被本班当作可以占用的理由**。
- 呈请：① st-minedig2 复 claim；② 维护三班核 `acquire-batch` 与单件 `acquire` 的过期谓词是否同一实现
  （在册工具级缺陷候选：静默窗判定读的是目录态还是 `expires_at`）。

**事件 B｜主区 index 是一池陈旧混合面（含 11 枚纯删除，波及本班 07b 卡）**

- 实测（05:45 存证 `.runtime/tmp/mineloop2/evidence/main_index_stale_pool_20261013.json`）：
  staged **79 件＝68 M ＋ 11 D**；这 79 件里有 **68 件的 index 字节 ≠ dev**；11 枚纯删除中含
  本班 `TDM-X-R1-01__comparison__07b_reset_ladder_anchor.yaml`（−177）与 8 张 `40–47_agg_*` 卡
  （各 −96，claim 属 st-minedig2 且已过期约 98min），另含 `.gitignore`、`config/flags.yaml`、
  `capability_canonical_file_registry.yaml`、两册他会话 ledger 的陈旧截断面。
- 主区**磁盘面 == dev**（逐件 sha256 核过），故此刻无人丢字节；风险面是"任何从主区直提（不走队列正门）
  的宽 filelist 会把这 11 枚删除与 68 份陈旧副本一起落地"＝批量回退他人成果。
- 本班不自理（宪法 §3.4 他会话在途违规 owner 责任制，且动共享 index 就是改别人的暂存态）；
  **移交＝统筹＋维护三班**。本班侧两道天然防线：闸一逐件 `lane==dev`（被回退即拒跑）、
  B 的"分数册丢他人行即拒投"（红证 §32.3 第⑦例）。
- 复核命令（两值已实测）：
  `git -c core.quotepath=false diff --cached --name-status | grep -c "^D"` ＝ 11；
  `git -c core.quotepath=false diff --cached --name-status | wc -l` ＝ 79。
- 在册同型先例（不是新病）：本战役 10-12 晚在**车道**面量到过 267 D＋40 M，根因＝
  `git reset --soft <dev>` 只动指针不动索引 ⇒ 索引对新 HEAD 呈"dev 有、旧树没有"的假删除；
  在册处方＝动过车道 HEAD 后先 `git reset`（mixed，只复位索引、不碰工作文件），暂存只写显式文件路径。
  本轮差别只在**面**：这次量到的是主区共享 index，故不可照抄处方——`git reset` 会把其他会话
  正当的暂存面一起冲掉（＝抹他人在途），所以本班只登记不动，处置权在共享面的 owner 侧。

### 32.8 认腿之洞的两道封口与"改道不硬闯"的取径（本批 0026 袋的内容）

- 洞（落在地上、非假想）：`_pillar_no_hysteresis_gain/_pillar_whipsaw` 只在 `is_mid_pair` 为真时判柱一/柱二，
  否则把键塞进 `owned`（＝本跑不判、归另一跑）。dev 面 `is_mid_pair` 由
  `arm_context.get("base_arm_cfg") == "levels_no_hysteresis"` 决定，而 07b 的基臂真实册名是
  `levels_no_hysteresis_with_reset` ⇒ **off 与 mid 两跑都判 False ⇒ 两跑互推 ⇒ 柱一柱二零判**，
  出分照常、fails 照常、只是那两柱永不落地——正是"会出假分不报错"那颗雷。
- 封口 A（待投）＝判官扩面腿：只读绑定层申报位 `base_is_no_hysteresis`，缺位即如实记败。
  因该件与他班在编同件，**本班不占**，已 parked：
  `evidence/judge_leg_park/{calibration_exam.py,test_calibration_exam.py,judge_leg_0026.patch}`
  （996 行/994 行/92 行补丁，投前 sha 已核；车道那两件已按 HEAD 归位，`lane==dev` 实测 True）。
- 封口 B（本袋 0026 投）＝绑定层**族名归一**：`base_arm_cfg` 的契约从"册内序列名"改判为"迟滞族档名"，
  真实册名保留在 `base_arm_cfg_tier` 与 `level_source`；于是连**未扩面的落地面判官**那句
  `== "levels_no_hysteresis"` 也认得对。改动＝card_binding −1/+9（被删那行是本班自有的
  `ctx["base_arm_cfg"] = ctx["level_source"]["base"]`），测试 ＋4 条断言。
- 红证（尺子能红）：把 B 退回原写法 ⇒ `test_real_book_carries_07_and_07b_variant_vocabularies`
  报 `AssertionError: ('mid_A', 'levels_no_hysteresis_with_reset')`，`1 failed / 63 passed`；
  还原后 sha256 与改前逐字相同，基线 `165 passed`（三测试件，车道面）。
- 闸一相应改为"两道封口任一落地即可开考"（`run_six.py` 现判据：`cb_txt` 含
  `ctx["base_arm_cfg_tier"] = ctx["level_source"]["base"]`，否则要求判官腿文本在场）。
- 口径声明：判据数值/阈值零动；07（无复位）面族名==册名逐字不变 ⇒ 历史分数行的读法不受影响；
  A 腿落地后 B 的族名归一不撤（两道封口并存＝申报位优先，族名兜底）。

### 32.9 补记器自查出一处少记缺陷（会吞掉六跑里的 1 个试次），已修＋已证可红

- 缺陷：`supplement_trial_six.py` 的差额上限原先写成 `if len(have) + len(plan) >= len(mine)`，
  而 `plan` 是**跨卡累加**的列表——处理第二张卡时，第一张卡的补记数被算进了它的额度。
  六跑形态（07：2 行/1 记；07b：4 行/1 记）下正确应是 1＋3＝4 只，旧式只补到 3 只 ⇒
  今日试次分母少 1，正是在册 `trial-ledger-undercount`（DSR/PBO 分母虚低）的同一形状，只是这次是我自己写的。
- 修法：差额**逐卡各算**（`need = max(0, len(mine) - len(have))`，卡内累加器 `added_here` 独立），
  并把每卡的 `分数行/台账记录/需补/计划补` 四个数打进日志（长耗时腿起始日志须自带归因输入，在册纪律）。
- 判别力自证：`python D:/ZephyrAlpha/.runtime/tmp/mineloop2/probe/redproof_trial_six.py`
  → `TRIALREDPROOF PASS`，四例＝
  ①正常形态 新实现补 4／旧实现补 3（同一输入下旧式必少 1，本探针因此能红）；
  ②全已记形态补 0（幂等，跑第二遍不重复记）；
  ③六跑未落地补 0（补记器不替没发生的跑背书）。合成面全在 tempdir，零生产写入（§9.6）。
- 顺带把两处"跑起来才会知道"的闸也读了码面确认（非推测）：
  `run_one`（card_binding.py:1513）与 `run_card`（calibration_exam.py:854）都吃 `force`，
  run_six 传 `force=True` ⇒ 07 已 examined 的续考合法、分数册 only-add 旧行保留；
  判官跑完会把卡面 `status` 写成 examined 并加 lineage——这一面在交付袋里如实随附，并在 §卅三 声明。
- 对齐器的时间窗（同一轮里的自我威胁，已核实不存在）：监视器 A 的调用序是
  `align → preflight → (READY 才) 六跑 → 退出`，即**判官写完卡面/分数册之后不再有 align 步**；
  而即便有，重排后的 yaml 必含 dev 里没有的行 ⇒ 落入 PROTECT 分支而非 ALIGN。
  本班不依赖这条巧合：A 在 READY 后即 break，`run_six.done` 落位后 B 才动（§32.3 闸⓪）。

### 32.10 卡面/册格对抗改写：12/12 具名拒绝（含我自己探针的三处误判更正）

命令：`python D:/ZephyrAlpha/.runtime/tmp/mineloop2/probe/adversarial_07b_face.py` ⇒ `ADVERSARIAL07B 12/12 具名拒绝 PASS`
（零 CH、零写生产：卡与册读在册字节后在内存深拷篡改）

| # | 篡改 | 具名拒绝 |
|---|------|---------|
| T1 | 册格删掉 RECOVERY@2 | `recovery_rung_cap_unfrozen:open:['RECOVERY@2']` |
| T2 | 阶梯 0.25 改成 0.30（替卡面拍数） | `recovery_rung_cap_off_card_face:open（册格=(0.3,0.5,0.75) 卡面只冻结过 …）` |
| T3 | 阶梯写成文字 "0.25" | `recovery_rung_cap_not_numeric:open:RECOVERY@0` |
| T4 | 卡面撤掉整张阶梯表 | `recovery_ladder_face_missing:<07b card_id>` |
| T5 | 开臂三档全 1.0（复位即回满＝与关臂同形） | `reset_not_full_reentry_violated:open` |
| T6 | 复位档不给触发括号值 | `reset_tier_entry_param_missing:['levels_with_reset','levels_no_hysteresis_with_reset']` |
| T7 | 括号值直接喂给非复位回放面 | `reset_param_on_non_reset_tier:levels_hysteresis` |
| T8 | 臂引句改一字 | `ArmQuoteNotFound:arm_quote_not_found_on_card:arm_level_cap_multiply:…` |
| T9 | 两臂连乘子表都相同（单臂冒充双臂） | `arms_identical_source_and_map:levels_with_reset` |
| T10 | 级别序列名不在档位册 | 装配不出上下文＝拒（判官随后按"未注入"如实记败） |
| T11 | 敞口位喂负 cap（收益/净值面误喂 e 位） | `ArmFaceMismatch:not_exposure_face:params_open.level_map:…` |
| T12 | 册级 pack 把括号值喂给两臂都非复位的档 | `reset_param_on_non_reset_tier:['levels_hysteresis','levels_no_hysteresis']` |

- 如实更正（第一版探针把三例误报成"护栏未拦"，错在**我的调用面认错**而非码面）：
  ①T5 期望码写错（真码是 `reset_not_full_reentry_violated`，我一直在改的那条柱名）；
  ②T7 前提写错——07b 的 off_A/off_B **本就该**带括号值（其开臂是复位档 `levels_with_reset`），
  把"给它括号值"当篡改是错的；改成直接回放面/册级 pack 两条真路径才测到该护栏；
  ③T11 原本调了一个本班并不存在的函数名（`_level_source_to_cfg`），换成在册 `require_exposure_face`。
  教训同型：判"护栏缺位"前先确认**自己调的是那条腿的入口**（在册 decorative-guards 的反向形态）。
- 为什么这组对抗是"卡面冻结"的可执行含义：T2/T3/T4/T5 四条正是"不替卡面拍数"的四条文字柱，
  现在每条都有一个能红的机判面；T1/T12 守的是"逐跑参数不许缺位或错位"。

### 32.11 两只袋的死讯与一处自我更正（22 卡转换重投＝0027；0021 死因是它自己带的旧字节）

**0020（22 卡转换袋）死于热册连坐，06:07 判死，重投走 0027**

- 死因实测：`dead_signature=item:TAKEOVER-PENDING`、`recurrence_count=79`、`recurrence_fused=true`。
  阻断点不是转换本身，而是这袋**顺带携带**了 `capability_canonical_file_registry.yaml`
  （为本机生新件登记 creation_token）——该热册正被一个死会话的接管开条目挡在门外。
  接管处置属该 sid 的 owner 面与队列治理面（宪法 §3.4 owner 责任制），本班不代裁、不动他人暂存面。
- 改道依据（**直接调拦截那条路径的函数**，不靠"应该可以"）：
  `create_guard._pg_confirmed_token_files(["docs/_working/mineloop2_campaign/13_regimes_prose_conversion_log.yaml"], set())`
  实测返回该件 ⇒ token 的在册第三源（PG 账本）可正证放行 ⇒ 0027 袋**不携带热册**，只含 22 卡＋盘点册。
- 自我更正（这一条很重要）：第一版转换把卡面散文里的**段内标注**（"（流动性牛）——逐字继承 16 卡先例窗"）
  抹掉了，而本班对这一改的自许是"只动表示层、零信息损失"；07 卡的在册家写法本就带尾注，
  判官 `_span_pairs` 也是从串内取全部成对日期、容许尾注。故本版按 07 家形把整余文入值。
  留旧案卷：0020 的袋内字节仍是抹注版（已 dead，不会落地），更正面在 0027。
- 三道独立复验（不引用生成器自述，另起一把尺现算，22/22 过）：
  ①日期集合 dev==转换后逐张相等；②dev 每个全角括注都出现在转换后某个值内；
  ③`status/pillars/pillars_numeric/buckets/data_binding/card_id` 与 `window` 其余键逐张等值，
  且行级 Counter 差集显示被删行**只**是 `regimes:` 那一行（整档重排被禁）。
  命令：读 dev 与车道两面做上述三项，输出 `VERIFY22 PASS`。
- 第四道（端到端消费面）：拿**落地面判官自己的** `_span_pairs`（dev 现值，含统筹 10-13 的多段裁修）
  逐段跑转换后的值：22 卡 44 段全部解析回卡面声明的 `A..B` 对，输出 `SPANPARSE PASS`。
  尺的第一版误把"整串 A..B"当成一个 token，量出 0/44 的假红（在册"强正则 0 命中＝假红尺"复证），
  改成与判官同形的单日期口径后才成立——记此以免后人把这条当成"转换破坏了消费面"。
- 前置动作：23 件先按 dev 现值逐件重基（`rebase_22cards_from_dev.py`，rebased=22/23，
  新建件 dev 无此件属预期），再重跑转换器（幂等，`planned=22 skipped=0 yielded=0`）；
  claim 实测 `acquired=23 denied=0`；入袋 `ENQUEUE-RENEW: claim 续租 23/23 件`。

**0021 死于 MSG-STYLE（是它自己携带的旧字节，不是新伤）**

- 死因：`item:MSG-STYLE scripts/backtest/fexam/card_binding.py:1018 raise RuntimeError(...) [unicode_arrow]`，
  recurrence=4 熔断跳。0021 是 04:06 投的袋，带的是箭头未改 ASCII 的旧面；
  该违规已在 05:1x 修复并随 0025/0026 重投（案卷 §卅一.7）。
- 处置：按在册"在途袋会因车道自己后落地而变回退弹，让它死、勿 requeue"——**不重投 0021**。
  同型预期：0022（04:19 投，同样带旧字节）大概率同因死，也**不救**；收敛面＝0025→0026 的落地字节。
- 队列副作用如实登记：这两只必死袋各占传送带一格（当下每格实测 16–20 分钟），
  是六跑延后的主因之一；本班不插队、不抢租、不改优先级（在册纪律）。

### 32.12 开考前的端到端零 CH 预演（把"六跑会不会半路炸"提前撞掉）与一条正向凭据披露

命令（车道 cwd，`PYTHONNOUSERSITE=1 PYTHONPATH=<lane>/src`）：
`python D:/ZephyrAlpha/.runtime/tmp/mineloop2/dryrun_07b_synthetic_face.py`

- 合成净值面（确定性 seed=11，含三段人为深回撤 32%/38%/30% 后接单调回补）喂**真判官**，
  分数册与试次台账全指 tempdir——生产分数册字节未动（44918 前后一致）。
- 认腿归属实测（这是 §32.8 改道的端到端正证，不是靠断言推断）：
  `mid_A / mid_B / mid` 的 `owned_by_other_run=[]` ⇒ 柱一/柱二**在本跑判**；
  `off_A / off_B / off` 的 `owned_by_other_run=['maxdd_improvement_vs_no_hysteresis_min_pp',
  'whipsaw_roundtrip_ratio_max']` ⇒ 正确地推给 mid 跑。两跑互推的零判形态消失。
- 闭环两面：六行 `unjudged` 键全部在位，内容含 `numeric_keys_not_read=[]`、
  `pillars_prose_keys=[drawdown_floor, oos_stability, paired_arm_protocol, reset_not_full_reentry,
  sharpe_floor, turnover_cost_gate, whipsaw_gate]` 与 mapping 面；`arm_face_readings` 在位。
  ⇒ 交付门 B 的"两面缺一即拒投"条件在合成面上先走通一遍（不是等真跑才发现拒投）。
- 一处自我更正（同一枚在册教训第二次生效）：预演脚本原来读的是 `not_judged_pillars` 这个**不存在的键**，
  于是打印"在位=False"，差点被我当成"闭环面缺失、真跑会被 B 拒投"；
  改成真键 `unjudged` 后六行全 True。存在性判据必须先核键名，否则尺子自己造红。
- 复位凭据实测（合成面）：`resets_granted=5 / resets_refused=433 / ladder_promotions=0`、
  `recovery_rung_days={'RECOVERY@0': 67}`、`graduation_face='absent'`、`graduation_face_skips=0`，
  并在 5 次复位后触发 `DRAWDOWN_PERMANENT_LOCK total_resets=5 threshold=5`（在册 5 次永久锁面照跑）。
- **正向凭据的披露位**：`reset_not_full_reentry` 这条文字柱在落地码面上是"违例即中止"的**否决面**
  （对抗 T5 实测 `reset_not_full_reentry_violated:open`），但判官不把 `recovery_ladder` 抄进 readings，
  所以分数册行内看不见"三档严格递增且首档<1.0"的正向凭据；该凭据实际存在于绑定面
  （实测 `rung_caps=[0.25,0.5,0.75]／strictly_increasing=True／first_below_1.0=True`）。
  本班不自立新键（那要改卡面 numeric 面＋判官扩面），改为：把这条如实写进交付披露
  （已随监视器 B 的 `disclosure.ladder_positive_face_not_in_readings` 进 §卅三），
  并把"写进 readings"列为待投判官腿的扩面之一。

### 32.13 本班自曝：零 CH 预演把两张真卡面写脏了（被完工自检回路第 5 项抓住，已恢复＋已加永久闸）

- 怎么发现的：不是人眼，是 §32.5 之后上的自检回路第 5 项"袋与车道同调"突然报
  `末袋吞未知行=1 ['…07b…:147 行]'`——袋内字节里有 147 行在车道已不存在。
  第一反应是"谁回退了我"，实测才是"我自己把卡面改了形"。
- 根因（一句话）：判官 `run_card` 跑完会**重写卡文件本身**（`status→examined` ＋ `lineage.run_id/score_row`
  ＋整档 `yaml.safe_dump` 重排），而我的预演脚本把**车道真卡路径**直接交给了它；
  分数册与试次台账我确实指到了 tmp（实测两面 lane==dev、生产分数册 44918 字节未动），
  唯独漏了"卡面自己也是输出面"这一条。
- 污染面与危害：`07b` 被写成 `status: examined` ＋ `lineage.run_id: dry-mid_B`，
  `07` 被写成 `lineage.run_id: dry-mid`——两个 lineage 指向的是 **tmp 分数册的行号**，
  而那张 tmp 册一清就没；若让它随交付袋落地，就是**给一张没真考过的行号作保**（假凭据，比报错更坏）。
  另外它会直接掐死六跑：闸一要求 `lane==dev`，脏面永远追不平。
- 恢复（全部按"取回用 cp、不裸 checkout"的在册手法）：
  `07b ← 0025 袋内 blob 字节`（本班作者面，也正是将要落地的字节），`07 ← dev 现值`（该件本班无在途袋）；
  恢复后逐字核 `07b lane==袋 blob=True`、`07 lane==dev=True`、两张卡均查无 `dry-mid` 残留，
  status 回到 `preregistered`（07b）与真实的 `examined`（07，10-12 两次真跑的合法状态）。
  被污染的现面**留证不删**：`.runtime/tmp/mineloop2/evidence/dry07b_contamination/contaminated_{07,07b}.yaml`。
- 永久闸（改在预演件里，不靠自觉）：`dryrun_07b_synthetic_face.py` 现先把两张卡 `shutil.copyfile` 进
  tmpdir、只把**副本路径**交给判官，结束时按 sha256 复核两张真面零改动并 `assert`——
  真面一旦被移动，预演直接算失败（不再"跑通了就算数"）。修好后复跑一次：六行读数与改前逐字同、
  `真面零改动复核` 通过、rc=0。
- 顺带把一条披露补齐：07b 的 `reset_not_full_reentry` 正向凭据只在绑定面（`rung_caps/strictly_increasing/
  first_below_1.0`），落地面判官不抄进 readings ⇒ 已加进 B 的 `disclosure`（§卅三 自动带上第四条披露）。
- 判读口径：这条是**我造的险**，不是我发现的别人的险；抓它的是自检回路的机械判据。
  把它写进晨间包而不是抹掉，是因为"预演=只读"这个直觉错得很典型——**任何调用真判官的预演都是写操作**。

### 32.14 三只袋同时死于**我自己造的三方冲突**（同一本班账被四只袋带着走），重投改为"一件一袋"分袋

- 事实（11:02 接手实测）：`0024/0025/0026` 全部 dead，`dead_signature=other:landing 异常`，
  三只的 dead_reason 同一句：`[landing] 非注册表族件双侧皆改真冲突（整文件三方，死信回退人工）:
  docs/_working/mineloop2_campaign/00_morning_pack.md`；recurrence 387/389/393 熔断已跳。
  后果＝**双臂适配器＋07b 卡面＋绑定册＋01 批复件至今没落地**（dev 面 `DRAWDOWN_LEVEL_TIERS`
  与 `base_arm_cfg_tier`、册内 `off_A` 全部 0 命中），六跑从 06:31 起一路拒跑到 11:0x（第 89 轮）。
- 根因（本班自己的编排错，不是别人的门）：06:30 前我把同一本 `00_morning_pack.md` 同时放进
  0024/0025/0026 三只袋，每只袋存的是**当时**的整档快照；0023 先落地后 dev 的班账前进了，
  剩下三只就成了"base 与 ours 双侧皆改"——落地仲裁对非注册表族件**不做多重集超集判定**，
  直接判三方真冲突回死信。这正是"同件多轮并一袋"那条在册纪律的反面教材，
  也是 §30.2 第 3 条"让旧袋自然死"判断里没料到的形态（我预期它死于门，实际死于仲裁）。
- 一处必须澄清的假信号（差点让我以为被他人回退）：`card_binding.py` 相对 dev 有 46 行"dev 独有"、
  `test_card_binding.py` 15 行、`07b` 卡 18 行。逐件 `git log -2` 实测：这几件**最后一次触碰全是本班自己**
  （316a8bac16 裁定③袋 00:58、0162c49420 文书修正袋 02:49、e74617f8ac 裁修袋 01:40），
  差集内容是我自己被替换的旧写法（如 `DRAWDOWN_LEVEL_SERIES_NAMES = ("levels_h…` 元组字面量
  → 现改为 `tuple(DRAWDOWN_LEVEL_TIERS)`）。⇒ 重投不会回退任何人。判据口径：
  **"dev 独有行"必须再用 git log 归因，才等于"他人成果"**，否则一把尺会把自己演进误判成被抹。
- 重投编排（改为**一件一袋**，三只互不重叠）：
  R1＝`card_binding.py＋test_card_binding.py＋07b 卡＋02_binding_book.yaml＋01 批复件`（代码与卡面册格，六跑的唯一前置）；
  R2＝`calibration_exam.py＋test_calibration_exam.py`（判官扩面腿，见下）；
  R3＝`00_morning_pack.md` 单件（班账今后只允许单独成袋）。
  三只都以**投时 dev 为新基**（新鲜 base ⇒ 单侧改，仲裁不再判三方）。
- 判官腿的状态变化（§32.6 的前置三查逐条重跑）：`lock_files.py check` 实测 **FREE**；
  `git log` 实测 dev 面该件最后仍是我本班 01:40 的裁修袋 ⇒ st-minedig2 的 +50 行（多日标的前向面申报位）
  **至今未落地也未持锁**。本班据此改变自裁：占件投腿（不属硬闯——锁空且我已完成"误收即归还"的登记），
  并在袋文里显式提请他们**按 dev 现值重基后再投**（我的 +16 是一处独立函数体内的小 hunk，
  他们的面在 target/前向聚合区，文本域不相交，正常合并可共存）。
  投前实测：车道恢复 parked 面后 sha256 与存证逐字相同（4fdb3c497384／974c4500318a），
  `167 passed` 复现，四件 ruff format 全绿。
- 时窗如实呈报：六跑从 06:30 拖到 11:1x 仍未开考，全部损耗来自上述自撞与传送带当下 16–20 分钟/格；
  合议结论要等 R1 落地后由监视器 A 自动产出（`evidence/six_*.yaml`＋§卅三）。

### 32.15 双臂码面被"死会话接管台账"硬挡（12:0x 起）＝本班唯一不可自解的堵塞

- 现象：重投的代码袋 `q-…-0028`（card_binding＋测试＋07b 卡＋绑定册＋01）入队 3 分钟即死，
  `sig=item:TAKEOVER-PENDING`，`recurrence=80`，命中文件＝`scripts/backtest/fexam/card_binding.py`。
- 台账事实（`.runtime/takeover_ledger.jsonl` open 条目，ts=2026-10-12T21:45:47Z）：
  死会话 **st-minedig2-20261012**，判死证据＝`idle 7984.1s > 7200s`、心跳末行 `exited`、
  无任何存活旁证；资源面＝26 件 dirty 车道（其中**正撞本班四件**：
  `card_binding.py` +56 行、`calibration_exam.py` +56 行、`test_card_binding.py` +64 行、
  `test_calibration_exam.py` +78 行；另含 8 张 agg 卡、其战役册、6 枚 csv、`agg8_series_materialize.py` +317 行）
  ＋13 件死袋 `q-20261013-st-minedig2-20261012-0005` ＋1 枚 ghost 心跳。
  全仓 open 接管条目 **175 条**＝这是系统性积压，不是本班一家的偶遇。
- 本班已做的绕行（把不被挡的面先落）：`0029`＝07b 卡＋绑定册四档格＋01 单文档化（这三件不在其资源清单），
  `0030`＝班账单件袋。⇒ 解锁后只差"码面一格"即可开考，不必再等整链。
- 本班**不做**的两件事（都属自洗可见性）：
  ① 不自签 `session_takeover_ledger.py --resolve st-minedig2-20261012 --by 本班`——
  他们四件码面各有 56–78 行未落地成果，"resolve" 等于替他人资产盖章销账；
  ② 不 `--sweep-absorbed --execute`（干跑实测 115s 未出结果、零写；且"absorbed"对本条不成立：
  其 dirty 内容与 dev 并不同源）。
- 抢救性存证（只读拷出，不动他们工作树）：`.runtime/tmp/mineloop2/evidence/deadlane_st-minedig2/`
  ＋ `_manifest.txt`（逐件 sha256 与相对 dev 的新增/独有行数）。若其车道日后被清理，
  他们的成果仍可从这里逐字取回；本班不代投其面（归属须由接管者或他们自己认领）。
- 呈请（唯一能解锁的动作，须统筹或有权限的接管者执行）：
  按台账 Rx 处置 st-minedig2 的 26 件 dirty＋死袋＋ghost 心跳，再
  `python scripts/governance/session_takeover_ledger.py --resolve st-minedig2-20261012 --by <接管者> --note <处置结论>`。
  解锁后本班一条命令即续跑（清单与袋文已备好，勿重复劳动）：
  `python scripts/git_commit.py --session st-mineloop2-20261012 --files "$(paste -sd, .runtime/tmp/mineloop2/files_R1code.txt)" --message-file .runtime/tmp/mineloop2/bag_msg_R1code.txt --keep-message-file --allow-multi-domain --enqueue`

### 32.16 更正一处本班先前的半对诊断（四连死真因＝袋基取车道 HEAD 而非 dev）＋接管命中面的假阳性定位

- **更正**：§32.14 把 0024/0025/0026/0030 的死因记为"同一本账被多袋携带"。那是**半因**。
  实测袋基：`0030 base_head=624cb3d1e3`（= 06:2x 的 dev，投袋时刻 dev 已是 63c2800251），
  而 `0031 base_head=3d136da494`（新鲜）⇒ **同一件、同一内容，换新鲜基即一次落地成功**。
  机制：`git_commit.py --enqueue` 把 base_head 记成**车道 HEAD**，车道指针落后 dev 时，
  仲裁就看到"base→ours 期间 dev 也改过这本账"＝双侧皆改，非注册表族件判真冲突回死信（在册死法
  lane-base-head-three-way-conflict：解＝让基等于 dev）。
- 本班动作（无损）：`git -C <lane> reset --soft dev` ＋ `git -C <lane> reset`（mixed，只冲索引）——
  八件关键文件（两码面＋两测试＋两卡/册＋班账＋01）复位前后 sha256 **逐字不变**（实测打印 `True`），
  车道 HEAD 由 624cb3d1e3 → 3d136da494 与 dev 同点；随后 `0031`（班账单件袋）done。
  在册坑再确认：`--soft` 后索引对 dev 呈大量假删除（本班车道 350 → 385 条），
  故本班暂存**只写显式文件路径**，禁目录形式。
- **接管命中面的假阳性（值得队列治理班一刀）**：
  `scripts/governance/session_takeover_ledger.py:165-193 _worktree_dirty()` 用
  `git -C <那条车道> status --porcelain` 取 dirty_files——这是**对该车道自己的 HEAD 比**，
  不是对 dev 比。于是"车道指针落后 dev、磁盘内容其实已等于 dev"的文件也被计入命中面。
  实测本案：`st-minedig2-20261012` 车道的 `card_binding.py` 磁盘 sha256 前缀 `bb14e4c9`
  与 `dev:` 同值、`test_card_binding.py` 同理（`4b80544a`），**零作者内容**，
  却仍进 dirty 清单并把本班的码面袋挡死（0032，recurrence 83）。
  建议修法（改台账不改门语义，方向保守）：`_worktree_dirty` 收完清单后，
  对每个路径比 `git show dev:<path>` 字节，逐字相等者从 `dirty_files` 移出并记
  `excluded_dev_identical=<n>` 留痕；真在途成果（字节不等于 dev）一律保留。
  反向自证：该排除只会缩小命中面，不会放行"他人未落地内容被覆盖"——因为要覆盖的字节
  与落地面本来就一致。门侧无需改动（其 INVARIANTS 要求判据/命中面变更与台账同批）。
- **门里已有一条正解，但只有属主能用**：`takeover_pending_gate.py` 的 C11 活性复核
  （统筹裁定 2026-10-12）——"提交人 sid ＝ 条目属主 sid 且 verdict∈{alive,degraded}"才降级 warn＋留痕，
  **他班/死会话条目一律照拦**。本班不是该条目属主，故无路可走。
  统筹 13:3x 裁定"minedig2 心跳活着＝活班不代销"，与台账判死（idle 7984s、心跳末行 exited）并存；
  若他们确为活班，则最省事的解锁是**他们自己**落/撤该条目（C11 对他们软化），
  或按上面那一刀把本班这类"零内容假命中"摘掉。
- 本班拒绝执行的两步（都会造成真内容损失或代签）：
  ① 把 `calibration_exam.py` 复位成 dev 字节——他们车道该件有 **58 行非空独有内容**
  （整段 `_forward_face` 函数与其中"多日标的前向面申报位……统筹署名批准"的申报语义），
  复位＝抹掉一份署名批准的未落地成果；字节已存证 `evidence/deadlane_st-minedig2/`；
  ② 自签 `--resolve`。
- 落地序现状（15:1x）：dev 已含 `off_A` 册格、07b `five_state_native_with_ladder`、
  `preregistered` 与 40 节班账；**只差 `card_binding.py` 一格**，六跑即由监视器 A 自动开考。
  本班不再重复投码面袋轰炸熔断位（0028/0032 已各计一次），等命中面缩小或属主自解后，
  一条命令续跑（`.runtime/tmp/mineloop2/files_R1code.txt` ＋ `bag_msg_R1code.txt`）。

### 32.17 追加型热件的投袋铁则：袋基必须晚于"自己上一次同件落地"（0033 死于基太新但不新鲜）

- 反直觉的一处：0033 只带班账一件、内容对 dev 是纯尾追加，仍死于
  `非注册表族件双侧皆改真冲突`。查袋基：`base_head=3d136da494`（= 14:35 我车道对齐时的 dev），
  而 0031（同一本账）在 14:4x–15:0x 之间落地，**dev 因此又前进了一次**；
  于是 0033 的"base→ours"窗口里 dev 侧确实改过这本账（改它的人就是我自己的上一袋）。
  ⇒ 半因修完还剩另一半：**袋基不仅要"等于 dev 曾经的一个点"，还要不早于该件最近一次落地**。
- 本班固化的三步（每件追加型热件投前都跑，写死成动作不靠记忆）：
  ① `git -C <lane> reset --soft dev && git -C <lane> reset`（只动指针与索引，工作树字节不动，
     投前后按 sha256 逐件复核＝实测八件零改动）；
  ② 形态自检：`dev 现值 == 车道现值的前缀` ⇒ 本次是**纯尾追加**（在册仲裁只认这个形）；
     若不是前缀，说明我在中间改了旧行 ⇒ 必须先把改动拆到别的面或改走整档重排之外的路；
  ③ **同件在飞只允许一袋**：0033 死掉之前我并没有第二本账在飞，但 0031 落地本身就是那次 dev 前进，
     所以规则补一句——上一袋落地后必须重新做 ①② 再投下一袋。
- 实测回报（15:2x）：`lane HEAD=1e9794182a==dev`，班账 `dev 1759 行 / 车道 1800 行`、前缀判真＝`True`；
  本袋（0034）按上述三步投出，内容＝§32.16＋本节。
- 另记一条**假警报的自我更正**：我在 15:1x 用 `127.0.0.1:8123/9000` 探 CH 连通性，三端口全超时，
  差点上报"ClickHouse 停了"。走真调用路径后 `DatabaseService.get_clickhouse_conn(role='reader')`
  返回 `clickhouse_driver.client.Client`，`execute("SELECT 1")→[(1,)]`（0.04s）、
  `hostName()='zephyr-ch' version()='26.6.1.1193'`、`SHOW DATABASES→c0_meta/c1_backtest/c1_market/
  c3_fundamental/system`——CH 活着，主机/库名都是我凭记忆猜的（我猜的 `zephyr` 库根本不存在，
  报"DB 不存在"是**我的尺错**不是环境错）。判据口径：连通性/存在性一律走在册单口与真表名，
  禁拿 localhost 端口探测当"服务在不在"的证据（在册同型：`config-consumed-by-only-one-code-path`、
  `zero-hit-ruler-needs-known-positive-control`）。


### 32.18 统筹裁定收悉（15:4x）＋治本刀已做成"可验证交接件"，本班不自签不越权

- 裁定三条并行：①治本刀转维护线（死信清零班/接任班谁先领谁做）；②C 监视器照跑，
  等 st-minedig2 自己把 calibration_exam 的多日前向面（其已批代码）落袋，M 行一消失本班自动续投；
  ③统筹另发催落令给他们。**"哪条先到走哪条"**，本班不再等任何一项。
- 本班对被推翻的前提如实入册：我上一版把五连死归给"同件多袋"是半因，真因＝袋基取车道 HEAD
  （§32.17 已固化三步）；而统筹原裁定"复位四件为 dev 字节"建立在"dirty＝内容差"上，
  实测 dirty 里含**与 dev 逐字节相同**的文件（车道指针落后 56 笔），复位是 no-op——
  该实测双证已升级为治本刀的立项依据。
- 治本刀交付物（本班**不改生产工具**，等领用方落地）：
  `evidence/takeover_fix_patch/` 下四件——
  `takeover_dev_identical_exclusion.patch`（对当前 dev 的 `session_takeover_ledger.py` 可 `git apply --check`）、
  `session_takeover_ledger.py.patched`（全量对照件）、
  `README_howto_apply.md`（一行落地命令＋三条必查坑）、
  两把反证靶件（`*.before_text_false`、`*.before_import_fix`）。
  判据：工作树字节==`dev:<path>` 者移出命中面并记 `excluded_dev_identical=n`＋`excluded_files` 留痕；
  不等/新建/删除/读不到/异常一律保留（fail-closed 朝照挡方向）。
- 验收尺已备且**自证有判别力**：
  `python D:/ZephyrAlpha/.runtime/tmp/mineloop2/probe/redproof_takeover_patch.py` → `PATCHREDPROOF PASS`；
  合成仓五断言（`equal.py` 移出、`real.py`/`gone.py`/`brand_new.py` 仍挡、计数=1）
  ＋两把反证（未加 `text=False`、helper 缺 import 的版本在同一输入下一件都缩不掉）。
  过程中本班又踩并当场记下两处工具口径：`run_subprocess_hidden` 缺省 `text=True`（bytes 比较必须显式
  `text=False`）；Windows 下 `write_text` 写 CRLF 令判据假阴（第四把口径，改 `write_bytes`＋`core.autocrlf=false`）。
- 现状（15:43）：dev 已含 `0034`（§32.16–§32.17，落地凭据走 `git log -- <册>`）；
  六跑仍差 `card_binding.py` 一格，A/B/C 三只监视器全部在岗（A≤700 轮、B≤1500 分钟、C≤360 轮）。


### 32.19 统筹续令（19:4x）逐条复测＋四件码面"逐函数三方归因"重基＋新的唯一挡点换成孤儿资源

**令中前提复测（全过，未照单全收）**：①`a67009f3ef`/`3d4f8b51db`＝挖矿二班 B1/B2 确在 dev（16:06/16:09）✓；
②`st-gpuwo` 接管条目已在 `.runtime/takeover/resolved/`（该目录 521 条，本班命中面已消）✓；
③本班交出的台账补丁确被维护五班同题抢先落地 `9348d8d90d`（17:31，落地面已带 `excluded_dev_identical` 字段）
 ⇒ 本班交接件**作废留档**，不再投，也不再自签任何 resolve ✓；④A 监视器实测已空转到第 148 轮并报
 FATAL（pending 空＝在飞袋全死），按令停：三只监视器全部 kill（`kill_ab2.ps1`＋`kill_c.ps1`），
 停后日志末次活动 19:58:3x，无残留。

**车道重基（令②的"与 dev 现值对齐"）**：
- `git -C <lane> restore --source=dev --pathspec-from-file=<删除清单>` 只补"dev 有而车道无"的 385 件
  （纯新增，绝不覆盖本班作者面）：脏条目 464 → 90，删除态 350 → 0，**本班八件 sha 逐字不变**；
  其中 8 张 `4*_agg_*` 卡恢复后，挖矿二班随 B1/B2 落地的 `test_agg8_declared_names_are_registered_hints`
  由红转绿——即"车道缺件"曾让他班测试在我的面上假红。
- 四件码面合并法（令②"重放增量"的可执行版）：**逐函数/逐常量三方归因**而非文本 merge-file
  （`git merge-file` 在中块冲突处把缩进弄坏，本班当场弃用）——
  对每个顶层定义：`dev==基线` ⇒ 用我的；`我==基线` ⇒ 用 dev 的；双方都动 ⇒ 保守留 dev（本案只有
  `_series_metrics`，且实测我那 1 行已在 dev 内，不丢）；dev 没有的 ⇒ 尾追加；
  常量额外做**依赖定序＋插到首处引用之前**（否则 `tuple(DRAWDOWN_LEVEL_TIERS)` 这类初值求值即 NameError）。
  另补回我独有 import 两支（`copy`/`numpy`）。合并后实测 **186 passed**；合并前车道另存
  `evidence/pre_rebase_1959/`，合并后快照存 `evidence/merged_face_20261013_2014/`（防车道被清扫）。
- 被本班改道取代的旧测试摘除 1 支：`test_arm_context_refuses_both_arms_reading_the_same_level_series`
  （它断言 `arm_levels_same_source` 必抛，而 off 配对"两臂同序列不同乘子表"是本班 §廿六 更正后的合法形；
  替代面 `test_arm_context_same_level_series_three_faces` 在册，摘的是被推翻的旧断言而非删除覆盖面）。

**MSG-STYLE 的尺我要更正一处（本班先宽后准）**：门实际只有两个违规码
`unicode_arrow` 与 `cn_period_end`（`msg_style_gate.py:133/160/217`），**全角标点不是违规**。
我第一次按"全角皆违规"扫出 29 处并改了 81 行——那是过宽改写（会平白扩大 diff 面），已全部推倒重做，
现值＝最小改动（唯一必需项 `0→1→2→NORMAL` 早已在 05:1x 改为 ASCII）。顺带量到
`scripts/backtest/fexam/arm_protocol_binding.py:298` 在**已落地 dev 面**存在同类违规（非本班件、本班不改），
登记移交：该文件下次由属主触碰时一并修。

**唯一剩余挡点（换了对象，这次是真差不是测量误差）**：门实测"命中文件 2 件"来自孤儿工作树
`.aidrafts/st-mineloop-20261010`（dirty=43，且该条目已带新剔除字段＝剩下的确是字节不同者）。
符号级核对结论：其 `card_binding.py` 独有 22 行涉及的 5 个符号在 dev 全部存在（同义已落地）；
其 `calibration_exam.py` 独有 22 行的关键差异是旧 `def _span_dates`——已被 `_span_pairs` 裁修取代。
故建议 **abort（放弃孤儿面）＋ `--resolve`**，而非 merge 回主区（merge 会把 `_span_pairs` 打回旧行为＝回退他人成果）。
完整处置建议与执行命令：`evidence/orphan_st-mineloop-20261010_disposition_note.md`。
本班不自签 resolve、不代删 worktree（物理移除须走裁定通道）。

**解锁后自动链（一步不落地）**：码面袋 kit 已备好（`files_R1code.txt`＋`bag_msg_R1code.txt`，
内容＝上面的合并面，186 passed＋MSG-STYLE 净＋ruff format 待跑）；resolve 一出现即投，
落地后重装 A/B（就绪判据不变：闸一 lane==dev＋两道封口任一＋CH 窗），六跑合议按裁定②读，
r 面按统筹新定案"以 run 落地时刻标注"随件披露；随后主区复跑四件套 pytest，再接任务②复合入口 CW-MINELOOP-001。
（本链 21:2x 已走完前三步：resolve 出现→0037 投出并落地 `790520df35`→A/B 重装在岗，详见 §卅三。）

## 卅三、码面落地＋主区回退弹排雷＋任务②挖矿段交卷（2026-10-13 20:5x–21:3x）

### 33.1 执行面（做完的，逐件带证据）

- **码面袋 0037 落地**：`790520df35`（21:20，四件 card_binding/calibration_exam＋两支自家测试），
  入队 20:56、闸门耗时 23.5 分钟。落地前 RUFF-PRECLEAN 预检拦下一次 import 序（`I001`，
  本班插入 `import copy`/`import numpy as np` 未排序）——**预检拦下＝省掉一整轮 landing**，
  修后 186 passed、ruff check 全绿再投。
- **车道快进**：`git checkout -- <交集四件>` 复位后 `merge --ff-only dev`；复位前两件事先对拍过
  车道磁盘 sha vs `git show dev:<件>`——**四件全等值**（本班磁盘字节就是落地字节，复位零损失），
  另 1 件 `tests/meta/scripts/test_blob_gc_phase2.py` 是他班新件、车道缺（非本班义务）。
  快进后 `HEAD..dev=0`。
- **主区班账回退弹（本班自挖自排）**：主区磁盘与 index 里的 `00_morning_pack.md` 是 **1291 行旧快照**，
  而 HEAD 侧 **1898 行**（§卅二 607 行只在已落地一侧）——磁盘非 HEAD 前缀（是 14:37 那一版的完整体，
  blob `d4ff636cc7` 命中历史 `e3d42622973`），独有行仅 1 行且是已落地行的措辞变体。
  若随任何"主区裸 commit"入袋＝**把本班 §卅二 整节抹掉**。处置＝先快照
  `.runtime/tmp/mineloop2/evidence/morning_pack_mainarea_stale_20261013_2124.md`（sha 前缀 4aae8814），
  再 `git checkout HEAD -- <本档>` 单档复位，复位后磁盘==HEAD（1898 行）。**只动本班这一档**，
  主区 index 里其余 ~百档旧快照不属本班、不代裁（转统筹/巡检知悉：主区暂存面存在多会话旧快照，
  裸 commit 必批量回退他班落地件——在册 `main-index-auto-staged-mixed-pool` 形态今日复现）。
- **两只监视器重装并已在岗**：A=`run_six_watcher.sh`（180s 轮询，就绪判据不变），B=`deliver_six_results.py --watch`。
  round 9（21:23:49）实测：**闸一"落地面逐字==dev"OK（9 件）**，随后被在册让路窗拦下
  `REFUSED: 21:00-22:30 W1 v2 提前窗让路`——即六跑最早 22:30 起跑（不是卡死，是闸在岗）。
  B 侧同步每 60s 报"未就绪：A 尚未写 run_six.done"，两向都不抢先（单向依赖未被破坏）。
- **任务②（CW-MINELOOP-001 复合族入口）挖矿段交卷**：产物两份入车道
  `14_composite_leg_census.yaml`（生成器所出，机读）＋`05_composite_leg_face_design.yaml`（呈批设计稿，零施工）。
  生成器 `.runtime/tmp/mineloop2/composite_leg_census.py`，谓词 P1-P7 全部机械判、零阈值零 CH，
  内建阳/阴/哨兵三重对照（L1-AGG/02 必判可绑、L2-09/04 必判不可绑、kline_index 品类必解析）。
  能力反查已留审计：四条查询零命中＋一条命中（尺在岗证明），结论=无在册复合入口可复用。

### 33.2 自裁面（本班域内拍的，附代价）

- 复合面与逐臂净值面**解耦呈批**：04_ 稿的 P0 要动判官 17 行（Owner/统筹门位），本面零判官改动；
  继续捆在一起＝8 张能出分的卡陪 16 张一起等门位。
- 分档：批-A 8 张（键面全冻＋腿品类可解析，只欠 3 张表进配方册＋合成算子）／
  批-B 5 张（22 册自标 `joinable_now:false`，未覆盖输入腿并集 6 张表点名在册）／批-C 1 张（22 册未登记）。
  放量前只做 1 张校准（L1-AGG/02，最薄的一条路）。
- **钉-2 两卡按 blocked_on_caliber 呈批，本班不绑、不出分**：`c1_market.sentiment_panel` 品类名原文
  "币圈宏观情绪面板"（business_data_categories.yaml:2563-2576），被两张 A股水温卡当情绪腿引用＝异轴顶替；
  卡面改写须走新版本卡（G4-5），不属本班自改面。**宁可 0 出分，不拿顶替面出假分。**
- `sector_state` 在 RRG 两卡只作交叉核对（卡面原文"禁直读…rrg_quadrant"）⇒ 谓词里从输入腿剔除；
  交叉核对面按"一次性探针留 receipt"设计（§6 D8 待裁，未批则两卡按不可出分处理）。

### 33.3 自我更正一条（谓词失真，留旧案不遮）

首版 census 用"该卡**每一对** pair 都得冻结"口径 ⇒ bindable=6。实测失真：RRG 两卡的 `sector_state`
被算成输入腿，而卡面明令禁直读——"每对全冻"把"交叉核对腿未冻键"误判成堵卡。改成
**P7 输入腿口径**（卡面 signal_table ∪ (22 册 join 表 − 禁直读 − 仅目标面表)，输入腿被任一冻 pair 覆盖即算通）
⇒ bindable=**8**。失真方向是**保守侧**（少报 2 张，不会造成假绿出分），但排产分母少报即工时误判；
首版册未入库即删除（`rm` 本班本轮自建件），本次只出修正版，谓词与两版差异都写在本节与 `ruler` 字段。

### 33.4 等裁（呈统筹/Owner，见 05_ 稿 §6）

D5 批-A 放行｜D6 钉-1 品类未注册归口｜D7 钉-2 顶替腿归口｜D8 交叉核对面形制（探针 vs 常驻审计腿）｜
D9 承 04_ 稿 D1-D4（逐臂净值面仍未批，16 支双臂卡与本面互不阻塞，请一并处理别让两件事互相等）。

### 33.5 本班名下未闭的账（更新 §31.5）

- 六跑开考：最早 22:30 起跑（让路窗），A 跑完写 `run_six.done`→B 投递→试次补记 `--apply`→合议结论。
- 主区落地面复跑（§31.4 第 3 条）：现在具备条件了（落地面字节已在主区磁盘），随六跑批一起做。
- 05_/14_ 两件新档的 creation_token 与大白话登记：走 `register_asset.py` 单口，与本批同袋。
- 孤儿工作树 `.aidrafts/st-mineloop-20261010` 处置建议（abort＋resolve）仍在等属主/统筹执行。
- 临时件清理：`.runtime/tmp/mineloop2/` 收官前不删（两只监视器正在用）。

### 33.6 21:3x–21:5x 补记：呈批袋落地＋自纠袋＋一条更正（判官腿结案）

- **0038 已落地**（设计稿 05_＋普查册 14_＋两件 token 同袋）：dev 面 `11 files changed` 那笔即本班四件＋他班同批；
  车道随后 `merge --ff-only` 追平到 `2bd481a551`（`HEAD..dev=0`），§卅三 与两件新档均已回到车道跟踪面。
  快进前挡道的两类面已按"先证无损再动"处理：4 件跟踪件（含本班班账与能力册）磁盘值逐件 sha 对拍＝旧 dev 快照，
  `git checkout --` 复位；2 件未跟踪新档（05_/14_，磁盘值与 dev 逐字节等值）先 `mv` 到
  `.runtime/tmp/mineloop2/evidence/pre_ff/` 再让 git 以跟踪态恢复——**没用裸 stash**（共享 worktree 禁令在册）。
- **他班未落地面一件，已快照非销毁**：车道磁盘 `scripts/backup/backup.ps1` 相对 HEAD 有 11 条独有行，
  且与 dev 现值也不同（第三种形状：既非 HEAD 也非 dev）。判据＝`git hash-object` 后 `--find-object` 查史，
  命中 `ad04467aa7f`（10-12 06:03 备份链追凶三班）⇒ **是旧落地面残留（本班重基时整片拷盘带进来的）**，非他人在写工作。
  处置＝快照 `evidence/backup_ps_from_lane_stmineloop2_20261013_2155.ps1`（sha 前缀 45a7dd16）＋`git checkout --`，
  交还属主面在此留名：备份链追凶三班（若他们要看车道里那份旧值，快照路径即取处）。
- **判官腿（§31.5 旧账 0028）结案：无需再投**。双证不同强度，分开记：
  判官件 `calibration_exam.py` 面 `git apply -R --check` 对 HEAD **干净**＝patch 逐字节已在册；
  测试件 `test_calibration_exam.py` 面反向套用**不净**（hunk 起点 853 行位置对不上），
  但 40/40 增行**全部存在**于 HEAD＝0037 三方归并时重了排版。⇒ 内容在、形状异，据"存在性≠内容判据"纪律
  不把它写成"逐字节已落地"。**更正一条先前措辞**：§31.5 曾把这条列为"parked 等他班复 claim"，
  实际阻塞早已随 0037 解除。
- **⚑ 本班自纠：先前"车道 N passed"的绿读证明力缩了一档**。21:4x 在主区做落地面复跑时，
  `tests/backtest/test_card_binding.py` 撞 45s Timeout（栈=pathlib `os.scandir`，点名 1404 行），
  而车道同一支 1.85s 过。两个因都查实了：
  ① 该测试写的是 `_P(".").rglob("docs/03_modules/**/…")`——从 CWD **整树下穿**，
     主区 CWD 下有 `.runtime/commit_queue/blobs` 27,083 枚＋`git worktree list` 50 只（每只都是整份仓库副本）；
     修法＝走查面绑到模块自带 `cb.CARDS_DIR`（有界），主区实测新面命中 8 耗时 **0.004s**，命中集与旧面同形（40..47）；
     已入 **0039 自纠袋**（files=1，ruff check/format 全绿，四件套 202 passed 重取）。零断言弱化：`len(cards)==8` 原样。
  ② **测量前提被证伪**：车道 `py.ini` 相对 HEAD 少 10 行、`pyproject.toml` 少 34 行
     （缺统筹当日追加③的六支 `--deselect` 名单），而主区配置面==HEAD。
     ⇒ **本班此前所有"车道 passed"读数是在旧 pytest 配置面上取的，对"落地面绿"不构成完整证明**；
     现已 `git checkout HEAD -- py.ini pyproject.toml` 追平后重取（202 passed in 14.71s 是追平后的数）。
     由此定一条收班核验判据：**车道追平与否要逐件 sha 对拍，且配置件必须显式列入对拍清单**——
     件数相同≠字节相同，这条比"车道绿≠落地面绿"的老话更具体（老话只讲代码件，今晚栽在配置件上）。
- **下一步（无需人盯）**：22:30 CH 让路窗一关，监视器 A 自动开六跑（round 9 实测"闸一 落地面逐字==dev OK（9 件）"
  已就绪，只等窗）；A 写 `run_six.done` 后 B 投递，随后补记器 `--apply` 进试次单口，合议按裁定②读。

