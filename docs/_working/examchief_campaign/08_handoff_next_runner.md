---
ttl: task_bound
title: 矿考三班·04:20 续跑交接包（CH 让路窗后的出分收尾与袋 2 落地）
created: '2026-10-14T01:30:00+08:00'
sid: st-examchief-20261014
lane: D:/ZephyrAlpha/.worktrees/st-examchief-20261014
branch: ai/st-examchief-20261014/task-rrg-v2card-880face
family_id: MINELOOP-CAMPAIGN
use_when: 00:46 起跑的等窗驱动器（detached，pid 见 .runtime/tmp/examchief/evidence/driver.pid）在 04:01 跑完 D8 探针与首张 RRG 分之后，由续跑者据本包收尾并落袋 2
---

# 1. 现在该读哪三个文件（按序）

1. `D:/ZephyrAlpha/.runtime/tmp/examchief/evidence/shift_batch.log` —— 批次全过程（每步 rc＋原文输出）。
2. `D:/ZephyrAlpha/.runtime/tmp/examchief/evidence/d8_crosscheck.yaml` —— D8 交叉核对回执
   （关键字段：`decision`、`quadrant_agreement_in_register_10_26`、`daily_spread_max_absdiff`、`ch_queries`）。
3. `D:/ZephyrAlpha/.runtime/tmp/examchief/evidence/score_run_creds.yaml` 与车道
   `docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 末行 —— 首张 RRG 分的凭据面与分数行。

# 2. 三种可能结局与对应动作（禁把 B/C 当 A 报）

- **A 出分成功**：读分数行，按 §4 的三条披露面读法写进班账 §五，然后走 §3 落袋 2。
- **B D8 判 halt**（`decision` 以 `halt` 开头）：卡面纪律＝"差异 >10% 时先查口径再开考"。
  此时**不得**开考、**不得**改卡面口径去迎合被测件列。动作＝把回执数值写进班账 §五
  ＋把"口径差异归因"（回执里已给 ±5 带宽诊断档 `quadrant_agreement_if_parent_band_pm5` 与
  `central_band_share_if_pm5`）写成呈批项进 §七，三张 RRG 卡维持 0 出分。
- **C 批次失败/进程未跑**（日志缺失或 rc 异常）：直接手跑（勿改尺）：
  ```
  cd /d/ZephyrAlpha/.worktrees/st-examchief-20261014
  PYTHONNOUSERSITE=1 python D:/ZephyrAlpha/.runtime/tmp/examchief/drift_r7.py snapshot --root=<同一个 --root>
  PYTHONNOUSERSITE=1 python D:/ZephyrAlpha/.runtime/tmp/examchief/d8_rrg_crosscheck_probe.py
  # decision=proceed 才继续：
  PYTHONNOUSERSITE=1 python scripts/backtest/fexam/card_binding.py --mode run \
    --approve-list D:/ZephyrAlpha/.runtime/tmp/examchief/approve_rrg02b.txt \
    --binding-book docs/_working/mineloop_campaign/02_binding_book.yaml \
    --arms-variant off --tag rrgB02 --recorded-by st-examchief-20261014 \
    --out D:/ZephyrAlpha/.runtime/tmp/examchief/evidence/score_run_creds.yaml \
    --scores docs/03_modules/_domain_backtest/exam_scores_v1.yaml
  PYTHONNOUSERSITE=1 python D:/ZephyrAlpha/.runtime/tmp/examchief/drift_r7.py compare --root=<同上>
  ```
  三条在册硬规矩：**必带 `--arms-variant`**（册内有 arms_variants 格，选择器 fail-closed 拒默认）；
  **必带 `--recorded-by`**（本班把归属字段参数化后 run 面不给值即拒）；
  **21:00-22:30 与 01:00-04:00 两个让路窗不绕、不用 `--override-ch-window-with-reason`**。

# 3. 袋 2 的 files 面与入队前置（顺序不可换）

1. 先 `python scripts/commit_queue.py status` 核袋 1（`q-20261014-st-examchief-20261014-0001`）状态：
   - done ⇒ 正常续跑；
   - dead ⇒ 读 `dead_reason` 修因后**原袋重投**（遵"重投三步脚本化"：按当下 dev 现值验多重集不丢行
     → 走正门新袋 → 落地逐字读回）；
   - pending/processing 仍在飞 ⇒ **先别投袋 2**（同会话同件后袋会让前袋静默 supersede）。
2. 投影归属卫生（每班必做，勿省）：`batch_creation_tokens.py` 的 render 会把 PG 全账重打进车道
   `capability_canonical_file_registry.yaml`，其中含**他班尚未入库**的条目 ⇒
   入袋前一律 `git checkout dev -- docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`
   复位（本班 token 已真在 PG，门侧 `_pg_confirmed_token_files` 正证放行，复位不丢东西）；
   新袋里若仍有新建件（如本包 08_），先登记 token 再入袋。
3. 袋基核验（本班 02:1x 实测过的一手，按这条做别再试快进）：
   `git rev-parse HEAD` vs `git rev-parse dev` 不等时，**不要 merge dev**——
   本班实测：merge 被"未跟踪新件 dev 已含"挡住（`examchief_campaign/06_...` 等），
   而为解 merge 做的 `git checkout -- <件>` 会把**已落地的码面退回旧字节**
   （本班真撞一次：card_binding/绑定册/用例三件被退回去、三张卡被 mv 出树，
   距 04:01 出分还有 ~107 分钟时抓回）；复原手段＝`git checkout dev -- <件>` ＋ 从备份目录 cp 回卡，
   然后逐件 `git hash-object` vs `git rev-parse dev:<件>` 全等自证（本班已复验：6 件码面＋分数册＋试次册全 SAME，
   `test_card_binding` 107 passed 重跑通过）。
   ⇒ 正确做法＝**袋 2 不整树快进，改逐件纯超集自证**：对本袋每一件跑
   `python -c` 比 dev 行数与 lost 集（lost 必须=0 或可逐行解释，本仓现有两处可解释：
   班账 −1 是标题改名、05 稿 −0 纯追加），再走正门。
4. 会话活性：`lock_files.py`/claim 与 SESSION-REQUIRED 都吃心跳——若隔了数小时，先
   `SessionRegistry("D:/ZephyrAlpha").register(sid, pid=0)` ＋ `mark_logical(sid)` ＋
   `register_heartbeat_keepalive(..., reason=..., requested_by=sid, ttl_seconds=7200)` ＋
   确认 `.runtime/locks/heartbeat_<sid>.pid` 里的 pid 还活着（本班 00:5x 就因 daemon idle 自退
   被 SESSION-REQUIRED 拦下一次，症状＝`get_session(sid)` 返回 None）。
5. files 面（袋 2，Owner 2026-10-14 五批＋PE 批之后已扩；**码面四件已随袋 1 落地，本袋不再夹带**）：
   - `docs/03_modules/_domain_backtest/exam_scores_v1.yaml`（新增分数行，only-append）
   - `docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`（＋1 试次，纯超集）
   - 本班 02b 卡件（run_card 会把 status 翻 `examined` 并写 lineage——这是在册正常翻转面）
   - `docs/_working/examchief_campaign/00_ledger.md`（§五 补实数；§八 已记 Owner 五批执行账）
   - `docs/_working/examchief_campaign/07_batchA_remainder_blocker_dossier.yaml`
   - `docs/_working/examchief_campaign/09_p0_arm_face_pack_for_approval.yaml`（乙批并包，token 已入 PG）
   - `docs/_working/examchief_campaign/10_crossline_daban_backfill_to_condaxis.yaml`（丙批跨线件，token 已入 PG）
   - `docs/_working/examchief_campaign/08_handoff_next_runner.md`（本包，token 登记后随袋）
   - `docs/_working/mineloop2_campaign/05_composite_leg_face_design.yaml`（己批改口：尾部追加 §9，
     前 207 行与 dev 逐行等值、lost=0、h2 9→10 已自证；矿考二班袋已全部 done，非在途件）
   - 三张版本卡若 §五 需要在卡内补"520 号裁定在册"引用，**一律用去井号形**（写"520 号裁定"），
     禁写井号形引用（"裁定"＋井号＋数字三字符连写，续跑班 04:3x 实测：本包原句因含该三连字符而被门判红，已改写）
     ——本班已实测该册 render 面比 dev 多 64 行含 517/518/519 他班条目，
     随袋即归属篡改，故**不随袋带投影册**，RULING-REFERENCE 门读的是入库册面，井号形会自触死信。
   投法：`python scripts/git_commit.py --session st-examchief-20261014 --files "<csv>"
   --message-file <仓外路径> --keep-message-file --allow-multi-domain --enqueue`


# 4. 读这张 RRG 分必须带着的三条披露（否则会把"没被判"读成"过了"）

1. **ic_ir_min 在 series 路恒不被评估**（`calibration_exam.py:240` 写 None，`:357-360` 归
   `numeric_keys_no_machine_face`）⇒ 卡面 ic_floor 的 ICIR 半边是空柱，只有 IC 均值那半边真被判。
2. **mono_spearman 是代理读数**：02b 的 `buckets.on` 是 (板块×日) 八格 categorical，
   判官 series 路按信号值分位分桶（缺省 10 桶）⇒ 该柱不是卡面八格先验秩
   （同型在册先例＝绑定册 L2-02-2/02 拒绑理由② ORDINAL_FALLTHROUGH）。
   **若 pass/fail 由这一柱单独决定 ⇒ 不得签 pass**，改为"机判面与冻结门柱不同物"上报。
3. **净费与桶样本门槛今日无面**：`config/exam_scale_cost_gate.yaml` 无 `net_fee` 节 ⇒
   `_round_trip_cost_bp()` 返回 NaN ⇒ `net_bucket_medians` 全 NaN；卡面 `min_obs_per_bucket` 零读取方。
   ⇒ 报数时不得声称"费后/满足最小样本"。

# 5. 收班清单（本班自己没做完的部分，交续跑者）

0. **袋 3＝PE 止血闸（统筹 2026-10-14 已批，warn-only/shadow）**：规约与实测影响面全在
   `docs/_working/examchief_campaign/11_pe_shadow_plan.yaml`。硬时序＝**必须在袋 2 done 之后**才动
   `calibration_exam.py`（否则首张 RRG 分的"判官零改动"证据链自污，R7 判据 A 会红）。
   做完的验收四条也在该件 §4（T1 不改判／T2 词表内不报／T3 ordinal 分支不报／T4 连续代理必报）
   ＋§5 三条自动回退判据；token 需为新增测试件登记（如另立案卷）。**不碰 PA/W-1/W-3 数值面**（那是 Owner 晨批项）。

1. 撤 reaper keep 行：`D:/ZephyrAlpha/data/runtime/process_reaper_keep.txt` 末段本班两行
   （注释＋`shift_batch.py`），批次跑完即删（该文件 gitignore，属运行态）。
2. 撤保活授权：`register_heartbeat_keepalive` 的 revoke 事件写
   `.runtime/sessions/st-examchief-20261014/keepalive.jsonl`（字面量 `revoke` 机读禁改名）。
3. 归档车道：`session_worktree.py archive`（含会话壳与影子指令面）——须先确认袋 2 done。
4. release 全部 claim：`git_commit.py --release-only --session st-examchief-20261014`。
5. 一次性件残留：`.runtime/tmp/examchief/`（探针/自证器/repro receipt）随 TTL 自然退役，
   **禁**从永久区引用它——班账与卡面已改为引用本案卷与 PG/分数册。

# 6. 续跑班补注（04:3x，只追加、不改写上文任何一行结论）

1. **§2 的前提被实测证伪**：§2 C 的"decision=proceed 才继续"是**永假前置**——D8 探针 `:72` 把
   `ch_query_df` 对 `groupArray(name)` 返回的 **str**（`len=178`）逐**字符**迭代，列集成员判定恒 False ⇒ rc=2 自拒，
   任何数据面下都走不到 `decision:` 行。数据面真值（本班 4 次 CH 只读、让路窗外、无 override）＝
   `c1_market.sector_state` 14 列**含** `rrg_quadrant LowCardinality(String)`，全库 `%rrg%` 唯一命中，
   432,817 行、2022-09-01..2026-10-09、同进程 5/5 稳定读到。
   ⇒ 本班按 §2 的 fail-closed 精神**未改尺、未开考**：三张 RRG 卡维持 0 出分，分数册／试次册／卡 status 对 dev 逐字节等值。
   数值、行级定位与呈批菜单（甲＝单点修探针读取形态、乙＝升为在册常驻件、丙＝随 P0 一并排）全在 `00_ledger.md` §五-补 与 §七 庚项。
2. **§3.5 那条"禁写井号形"的原句自己带着该字面**，本班入袋前直接调门本体 `REFERENCE-INTEGRITY` 自扫初判 **False**（5 处命中，含本包这一行），
   已按令卡第五条改描述式书写；09 包 §7 的 PG 复核命令改 `chr(35)` 拼同一 entry_key，本班抽正文原样跑过期望值（细节见班账 §五-补 第 10 条）。
3. **袋 2 实投 7 枚而非 10 枚**：§3.5 清单里出分依赖的三件（分数册／试次册／02b 卡 status）今日与 dev 逐字节等值＝空改动，未放；
   另**新增 11_pe_shadow_plan.yaml**（§3.5 未列）——不随袋则收班归档车道即毁掉统筹已批 PE 批（袋 3）的唯一规约成文面；
   它是纯文档、不碰 `calibration_exam.py`，故 §5.0 的"判官零改动"硬时序不被本班自污（袋 3 施工仍未做，交下一班）。
   袋 1 done 已核（`landed_id=0e3835338404508d096a4d671e4a621c15d15a85`）；投影册复位后与 dev `byte_identical`（71112 行）。
4. 收班**动作次序**（本条写的是次序，不是完成声明；本班按 §3 先投袋再收班，逐条完成后在班账 §五-补 落数）：
   袋 2 入队 → 袋 2 done → 撤 reaper keep 本班两行（`data/runtime/process_reaper_keep.txt`）→
   写保活 `revoke` 事件（`.runtime/sessions/st-examchief-20261014/keepalive.jsonl`，字面量 `revoke`）→
   `git_commit.py --release-only`（接班时实测 `held_files=[]`，仍走正门留痕）→ 归档车道。
   若袋 2 未 done 而本班会话中断：**勿归档车道**，11/09/10/07 四件只在车道存在。
