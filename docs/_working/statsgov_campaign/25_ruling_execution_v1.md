---
ttl: task_bound
completes_when: 四件尾巴各有归属并被下一班/相应车道接走（规格件正式版／回补执行／款⑤ 原文／M6 待维护三班 C4）
---

# 统筹批复执行件（令⑥ 晚班·四裁逐条落点）

批复来源=统筹 2026-10-12 晚批复（非本班自拟）；本件只记"怎么落的、落在哪个字节、还差谁"。

## 一、PBO 撤统一门 ⇒ 已改规格件真源

- 落点：`trial_budget_registry_draft.yaml#caliber_declaration` →
  `pbo_gate_value: null` ＋ `pbo_role_after_revocation: in_family_diagnostic_only`（族内相对诊断，报告项非门）
  ＋ `promotion_gate_kept: DSR>=0.95 + 闭卷考试`；失效证据回指 `21_negative_results_family_v1.md` #2。
- 生成器侧同步：`cap_status` 与呈签片段 `04_numbers_table_for_signature.md` 重跑刷新（机生，未手填）。
- 未动项：`correlation_overfitting_audit.py:64` 的 `PBO_MAX=0.05` 常量**保留**（撤销的是"跨族统一门"地位，不是删数值）；
  该处是否加注释说明其新语义，归该件主人，本班不改他人文件。

## 二、数值表照签 ⇒ 六族帽已出正式版（C/D 的"帽待定"已被实测消解）

批复当时给的豁免是"C/D 判帽待定"。本班按"先修 row_rule 复跑"的正解当场修了计数口径，结果：

| 族 | 帽（=历史消耗×1） | 状态（机生） |
|---|---|---|
| A 信号/因子 | 1,733 | `owner_signed_20261012_measurement_incomplete`（12 支册里 1 支不可解析，见 `uncounted_files` ⇒ 该帽是**下界**） |
| B 策略配方 | 85,252 | `owner_signed_20261012` |
| C 组合/配置 | 9 | `owner_signed_20261012`（原报 5 且标待定，系 row_rule 猜错键名） |
| D 状态识别/环境 | 17 | `owner_signed_20261012`（**原报 0** ⇒ 若照签会误停 D 族；红旗解除方式＝修口径不是豁免） |
| E 工程件 | 194 | `owner_signed_20261012`（改用"一个 run 档案=一次可审计考"目录计数） |
| F 挖矿器元层 | 5,488 | `owner_signed_20261012` |

口径升级三条（都写进规格件，供复算）：①`row_rule` 由点名单键改为**候选键链**且逐件留 `key_used`；
②单体记录册（无容器键的 reexam/conditional 卡）按 `COUNTED_AS_SINGLE_RECORD=1` 计入，
**绝不返回 0**（0 会把真实试次读成零消耗——自家测试 `test_count_entries_distinguishes_absent_key_from_zero` 现钉死这两侧）；
③新增 `dir_glob` 面型。测试 10 passed；产物 `02_*.yaml`/`04_*.md` 已刷新。
- ⚑ 新暴露一条待统筹定归属的重计：A 族通配 `*exam*_v*.yaml` 与 B 族点名同时命中 `mom029_reexam_v2.yaml`（已写进 `overlap_notes`，建议归 A）。

## 三、更硬的阳性对照 ⇒ 出回补规格件（含本班自纠）

- 落点：`24_positive_control_backfill_spec_v1.md`。
- **本班自纠一条**：我 20:3x 口头说"只补 2019-2020 两年即可"，算错——所需 T≈1,651 交易日，
  两年只到 1,180（t≈2.62 仍不够）⇒ 批复三给的范围正确，我收回原建议并在该件 §0 留了认错记录。
- 关键实测（决定工量）：市值表全表起于 2021-01-04；价量表 2016=234／2017=240／2018=237 只票（stub，
  且 `kline_daily_hfq` 同形＝两表互证）；2019=3,771、2020=4,366 已完整。
  ⇒ 缺口是**两段**：段一只补 basic（2019-2020，≈198 万行）；段二须价量＋市值同补（2017-2018，各≈173 万行）。
- 派工前必核实项（已写明）：`scripts/data/backfill_stock_daily_basic.py` 默认 `--start 20210101`，
  但其 `fetch_symbol` 调的是 `ak.stock_zh_a_hist`（价量接口）而表名是 daily_basic——文件名与数据源不一致，
  须数据域确认它产哪套字段，避免跑错口写错列。
- 执行面归数据域，本班不跑取数；月频 t 口径留档不采。

## 四、款⑤ 原文 ⇒ 停在 Owner 手里，本班未代写

`22_f06_archive_ruling2_v1.md` §款⑤ 的粘贴位仍空（四节标题占位）。统筹亦不转抄以防漂移。
待 Owner 逐字贴来即入册（原文不改）。

## 五、其余验收项的落点确认

- 款② 不重写他人事实源：已守（本班 0 次写 `f06_survivors.csv`）；**BOM 观察已转挖矿班**（该件表头带 `ef bb bf`，实测记录在 22 号件）。
- 试次入账与追加更正行：2,412＋8 已入账（账面 38,310→40,730，治理分母 91,400→93,820）；
  冒烟批 48 次那条的 note 误写以正式批 note 说明，未 UPDATE/DELETE。
  ⚑ 一条如实提示：这三条新记录目前**只在主区盘面**，尚未进 dev（热册由账本/册主车道落，非本班袋内件）。
- 病根 4"尾部追加型外科写"正解：本班实测支撑（追加单条成功、整册重放被拒），已作为建议写入 `03_*.md` §5 与晨/晚间包。
- M6 留证法：跑批件三份源码全文在 `90_calibration_runners_source.md`（含 sha256 与行数，可粘回）；
  待维护三班 C4 落 PG 第三源或册主 render 后，`scripts/backtest/statsgov_deflation_and_budget.py` ＋
  `tests/backtest/test_statsgov_deflation_and_budget.py` 与两份校准跑批件一并入正式目录（token 已登记）。

## 四件尾巴与归属

| 尾巴 | 归属 | 本班留了什么 |
|---|---|---|
| 规格件进 `catalogs/` ＋ ROOR 登记 | 册主车道（本班不代打投影） | 规格件真源已成文＋机生两面 |
| 回补执行 | 数据域 | 段/行量/字段/验收/复考协议全在 24 号件 |
| 款⑤ 四节原文 | Owner | 占位与"禁代写"声明在 22 号件 |
| 两个 .py 入库 | 维护三班 C4（M6） | 源码留证＋token/translation 均已进 PG |

## 五、批复四裁执行账（2026-10-12 晚 21:2x–21:5x，本班第二轮）

| 裁 | 执行到哪 | 可复算判据 |
|---|---|---|
| ① E 帽 | 终值 E=**399** 已在 `02_*.yaml`（族 E `consumption_total`）与 `04_*.md` 表行；随本袋落 dev | `git show dev:docs/_working/statsgov_campaign/02_trial_budget_inventory_v1.yaml` 内 E 族 = 399 ⇒ 即收班 |
| ② 派工单 | **`26_workorder_marketcap_backfill_v1.md`** 出单（两段合并、段一先行、**不含取数**）；Owner 点名的名实不符核查本班已代查并扩成四条同源缺陷（A 名实不符／B 默认腿有害／C 全表 `data_source` 假标签／D tushare 腿日期硬编码 2021-01-01），另列 E 引擎版本列 UNPROBED、F 源权限待测为跑前必补 | 每条带复核命令；A–D 的代码位=`:46`/`:54-60`/`:31-33`/`:131`/`:136-138`，`sed -n` 可验 |
| ③ 不可解析册"数进来" | 计数口径改造落地：点名键查无 ⇒ 取**最大容器 ∪ 计数型整数量级标量**作保守上界计入（只取容器会把 `family_size: 11` 低估）；逐件标 `pending_exact_count`、族级 `cap_status=owner_signed_20261012_conservative_estimate_pending_exact_count`；连容器与标量都没有才进 `uncounted` 并降 `PARTIAL_MEASURED`（**任何分支绝不返回 0**）。A 帽 1,733（下界）→ **1,749**（上界＋待精算），终值版待精算后照出；教训入册=设计总则 **P-4** ＋ `evening_ruling_20261012` 块 | `tests/backtest/test_statsgov_deflation_and_budget.py` 10 passed（含"上界件计入并标 conservative""裸件进 uncounted 不硬凑 1"两条）；生成器幂等复跑逐字节等值（除 mtime 戳） |
| ④ 款⑤ 原文 | **未动**——本班不转抄，占位仍在 22 号件等 Owner 贴原文 | 22 号件 §款⑤ 仍标 pending |

### 本班自报两条（同族病：改账不核结构）

1. 上一轮 `str.replace` 改面状态拆分**静默未生效**（无断言），出货码里仍是旧分支——发现后带断言显式重打。
2. 本轮一处 Edit 把 docstring 收尾的换行吃掉 ⇒ 文件语法崩，由 `ruff check` 抓到（非肉眼）。
⇒ 两条都是"改完只 grep 正文绿、没跑结构自证"的形态；本轮起改 .py 必带 `ruff check`＋`ast` 顶层函数计数＋测试三连，
   与在册"结构计数自证"纪律同族（`edit-append-anchor-consumes-heading`）。

### 派工单一件的登记实况（如实，别当已闭环）

- `26_*.md` 的 creation_token 已进 PG：`registry_entry` 行 `status=active`、
  token=`statsgov-trial-budget-26-workorder-marketcap-backfill-v1-20261012`、`created_by=st-statsgov-20261012`。
- ⚠ `publish_snapshot` 撞 `uq_registry_snapshot (REG-CAPCAN-001, 431)` 唯一键（他会话同版本已在），
  本班**未**代解他人快照、也未强推 render；⇒ 投影面暂不含该条，CREATE-GUARD 走 PG 第三源正证放行，
  投影重打归册主车道（禁出重打投影袋，同 M6 线）。

## 六、同夜第二次自纠（批复③的"上界"当时仍是下界）

上表③行记的 A 帽 1,749 出货后，本班复核"这个上界到底是不是上界"，实测两处硬证据：

1. `indicator_conditional_exam_scores_v1.yaml` 里真含 **22 条带 p/t 值的假设检验记录**
   （`per_indicator`×`pairs` 加上 `ref_window_report` 内的同族记录），而我那版上界取的是
   `family_size: 11`——**11 < 22，上界仍然是下界**，正是批复③点名的"过去太松"复发形态。
   ⇒ 上界候选加第三条：**带 p 值或 t 统计量的检验记录数**（命中即计 1 条、不下钻，防同条数两遍），
   取"最大容器 ∪ 计数型标量 ∪ 检验记录数"的**上包络**。A 帽 1,733（旧下界）→ **1,760**。
2. 新函数首版把"命中一条记录"写成了返回**该记录的键个数**（`len(o)`），一次把上界放大 ~8 倍
   （该册 22 条被算成 176）。我的合成件每条恰好只有一个键，`len(o)==1` 与正解同值 ⇒ **测试当时无判别力**；
   已把 fixture 换成多键记录，并按"判通过的脚本须先证明能红"补做双向验证：
   塞回缺陷实现 ⇒ 红（得 72 而非 12）；正解 ⇒ 绿（10 passed）。

顺带一条如实口径：**逐面读数会随他班写入自增**——F 族 `intake_ledger` 面在两个小时内
5,410 → 5,543 行（挖矿班在投），这不是本班口径改动。数值表因此是"带时间戳的快照"，
终签要按 `as_of_source_mtime` 那一次读数签，隔日复照请先重跑生成器。


## 七、四裁（第二轮）执行账 ＋ 两袋连坐死因（2026-10-12 夜 23:2x–23:5x）

| 裁 | 执行到哪 | 证据等级 |
|---|---|---|
| ① 等落地 | 本班不刷投。**但 0009/0010 两袋已于 22:4x–23:1x 双双阵亡**（死因见下），故 dev 仍显 E=194；已按在册正法重投 0011（基底钉 dev） | 实测（队列面 `dead/` 两件＋`git show dev` 读数） |
| ② A 帽按 1,760 签、消费时再精算 | 已入册 `evening_ruling2_20261012.N2`；精算推迟判据与"试次单位口径随预登记件定"一并登记 | 已登记 |
| ③ 段二附件照附 | **`27_segment2_channel_probe_and_acceptance_v1.md`**：2017-2018 三通道实测（B-1 禁用／B-2 baostock 可用有条件／B-3 因子源非瓶颈）＋回补验收核账（追1 PASS／追2 FAIL／追3 未闭合）＋T 账（**还差 471 个交易日**） | 本班亲手复测（CH 只读口） |
| ④ 数值表绑时戳 | 生成器改造落地：`04` 表头自动带 `as_of_source_mtime / spec_sha16 / 账本快照 trials·floor` 三件戳，并注明"不绑时戳的签名＝假精度"；已用两次复跑证漂移为事实（见下） | 实测 |
| ④尾 六缺陷升硬前置＋C 独立工作件 | 26 号件 §1 头部改判"六条全部为硬前置"；§1-C 登记新工作件**存量来源标签完整性核查**（失真面 711.3 万→**1,050.6 万行**），与 26 号件一并交**数据车道二班** | 实测＋已入册 |

### 两袋连坐死因（外来件，非本班内容冲突）

签名：`门禁 TEST-SOURCE-CONSISTENCY 阻断 … tests/pf_alloc/test_allocation_team_wiring.py:41 … REGIME_TO_SEGMENT/SOURCE_NOT_IN_TEAM 符号不存在`
——报的是**别人的文件**。本班取证四条：

1. 该件**不在 dev**（`git cat-file -e dev:tests/pf_alloc/…` = N）；
2. 主区工作树**干净且无此件**（`git status --porcelain tests/pf_alloc/` 空、盘上只有 `__pycache__`）；
3. 全 git 历史**从没有过该路径**（`git log --all --diff-filter=AD -- <该路径>` 空）；
4. 该路径只出现在 **st-combine-20260923 的 10＋ 枚旧死袋**里，而 0009/0010 两次落地读到的**行号还不一样**
   （0009 报 `:41`，0010 报 `:54/:87/:232`）⇒ 落地瞬间序列化器工作树里存在过一份该件的 transient 面，之后消失
   （`.runtime/commit_queue/worktree/tests/pf_alloc/` 现只剩 `__pycache__`）。

⇒ 定性：**内容扫描型门在非 own-diff 面上拦住了无辜提交人**（根宪法 §3.1 应"warn＋审计"，§3.4 "他会话在途违规不代修"）。
本班**不代修 pf_alloc 的测试、不弱化该门**；上报请路由：①维护三班清序列化器工作树的 transient 面；
②该门的 own_scope 归属由册主车道定性（`gate_registry.yaml` 的 `own_scope` 字段机生勿手改）。
重投处方照在册正解：`commit_queue.py enqueue --base-head <dev sha> --no-bootstrap`（基底钉 dev，避免"基底无、dev 有"三方冲突）。

### 批复④ 的当场实证：同码同册两次读数差

| 时点 | A 帽 | 账本 trials | 说明 |
|---|---|---|---|
| 22:16 一次跑 | 1,760 | 40,730 | 呈 Owner 签的那版 |
| 23:5x 二次跑 | **1,762** | **40,732** | 他会话入账 2 次试次＋册面自增 2 行 |

⇒ 这不是"把 1,760 改成 1,762 请您重签"，而是**两版各自绑各自时戳**。要哪种口径生效请点一下：
(A) 冻结 22:16 那版为签字值（此后数值表按 `as_of_source_mtime=2026-10-12T22:16:05` 引用）；
(B) 签最新版（每次收班/呈签前重跑生成器，绑当次时戳）。本班默认走 (B) 并把重跑命令写进表头，不自作 (A)。



## 八、统筹裁定两裁执行账（2026-10-12 夜 23:4x–23:5x）

| 裁 | 执行到哪 | 证据等级 |
|---|---|---|
| ① 口径＝B（绑时戳重跑，表头三件戳形态照准） | 落地并**补强**：新增第四枚戳 `as_of_newest_input_mtime` ＋ `n_inputs_read`（本班实测 110 件输入）。原因：`as_of_source_mtime` 只记**规格件自己**的动作——实测两次重跑间成绩册面 1,726 行未动，而账本被他会话入账 34→36（trials 40,730→40,732）令 A 帽 1,760→1,762；只绑规格件 mtime 就签不到这类自增。生效值改按"最新输入 mtime＋已读输入数"为准（同输入同输出，不读时钟） | 实测（`02` 第 7-8 行＋`04` 表头） |
| ② 路由授权＝批 | **`28_workorder_landing_face_and_gate_scope_v1.md`** 已出单：W-1 序列化器工作树 transient 面（先定源再清面，不动 lock、不整树破坏性清理、不代 requeue 他班袋）／W-1b 存活闸把活会话判幽灵的回收来源／W-2 `TEST-SOURCE-CONSISTENCY` 的 own_scope 定性（走 registrar 重打，禁手改机生字段）。本班**不动门、不改他班件、不加白名单**，只交输入面问题与可执行完成判据 | 已登记（token 进 PG active，snapshot v437） |

### 三袋连死的完整死因链（本班不粉饰）

| 袋 | 死因 | 定性 |
|---|---|---|
| 0009 | `TEST-SOURCE-CONSISTENCY`（报 `tests/pf_alloc/test_allocation_team_wiring.py` 符号漂移，非本班件） | 外来面连坐（工单 W-2） |
| 0010 | 同上，但**行号变成 :54/:87/:232** | 同上＋证明读到的是 transient 版本（工单 W-1） |
| 0011 | `ghost_session: 属主会话已死（heartbeat=exited / 注册表无在册）`——**而本班当时正在跑** | 注册条目在 22:05 被回收、守护因 "session not in registry" 自退（工单 W-1b） |

本班自救四步（按在册正门，全部读回验证）：`register(sid, pid=0)` → 起 detached
`python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <sid> <root> 30 <wt>` → keepalive 复批 →
用**门自己的尺**判活（`list_active_readonly` 命中＋hb_age 2s≤90s＋open 接管条目 0）。
⚑ 一条给后来者的工具事实：`scripts/heartbeat_daemon.py` **不存在**，旧配方里的脚本路径是错的，入口在包模块（本班第一次起守护就踩了这个空，`Popen` 起了个不存在的脚本、rc 无人报错）。

### 重投三步已按 Owner 追认脚本补齐

1. 按**当下** HEAD 做行级 Counter 多重集对拍（7 件：仅 dev=71 行，逐条归因＝02 的 66 行为本机重跑替换旧读数、04 的 4 行为旧 A/E/F 行与旧限制①段、draft 的 1 行为 E 面旧 dir_glob；其余四件仅 dev=0）；
2. **在车道暂存面跑真钩子**（本班前两次只跑了 in-process 预检，漏了这步）；
3. 走正门新袋，基底钉 dev，死因与归因写进袋内讯息；落地后逐字读回 dev 字节。
