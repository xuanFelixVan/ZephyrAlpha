---
ttl: task_bound
session: st-regsolo-20261010
landing_note: 本件由终清波三 st-fclean3-20261012 依统筹批复 M2 闸①代落，正文零改动，仅补 docs/_working 必需的 ttl frontmatter（原文无 frontmatter）；origin sha 见 wave3/26_件 §一
---

# T4 lane：PG 账本欠账基线 + 当日三事故时间线（st-regsolo-20261010）

> 主仓只读；本文件为唯一可写输出。所有 PG/盘面读数=时刻切片（22:45–22:54 +08），期间他会话在写（CAP 册 22:45:18 刚被本专班主会话发布 v132）。

## 结论（≤8 条）

1. C7b 判据面=仅 capability 册（REG-CAPCAN-001 family=creation_tokens，身份键=(file,token) 复合）；C7b=「下一次 render 会从盘面删掉的、且非合法 retired 的行数」。最新互认值：v130 后 C7b=3（全合法退役），监视器 22:46:07 cycle5 仍 CLEAR（ARMED=0/ FIRED=0）——**死信二期清零态保持**。
2. CAP 版本链今日 7 连发：v126/v127(libfront)→**v128(18:47 deadcure2 拆除#1)**→v129(19:30 chiefc)→**v130(19:42 deadcure2 拆除#2，192 充气后回填)**→v131(21:58 deadcure2)→**v132(22:45:18 本专班 st-regsolo-20261010)**，最新 entry_count=14819、ledger_version=132。
3. 七册基线（22:46–22:48）：CAP creation_tokens active 14423/retired 169；MODT entries 8089；DOC files 306；ARCH-ISSUE 817；ERRCODE 794；CAND 623；RULING entries 310+rulings 1。除 CAP 今日活跃外其余六册最新 snapshot 停在 10-04/10-05/10-08。
4. 欠账抽核（HEAD yaml vs PG active，归一键归一）：CAP 未解释欠账=0（3 条 head-only 全为 PG retired 合法退役：quant_methodology 07/08/12 placeholder）；PG 独有 1 条=本专班 regsolo-99-delivery token（已登记未物化进 HEAD yaml）。**真增量欠账在另两册：MODT 缺 2（phase_discriminator.py、graduated_package_feed.py——恰是 chiefc C-4/C-5 件）；RULING 缺 5（裁定#494~#498）**，两册 pg-only=0（无反向）。
5. 新发现（A 车道输入）：CAP 册被畸形整档写册污染出 **6 个垃圾 family_key**（chiefc-99-delivery-20261009/file_token/t2-handover-claim-grid0926/t2-subspace-json-grid0926/t2-subspace-meta-grid0926 各 1 条 active + HEAD yaml 顶层同名杂键）——顶层杂键被账本当族登记，双轨病残余实证。
6. 三事故定谳：①token 蒸发=PG 14145 严格子集缺 56（半径 58），v128 拆除→3；②-271 回滚险情=21:35 终报 commit c61765bf25 对 capability 册 numstat **1397+/271-**（54 条目删/278 增），其更危险形态（删 290/lost 3）19:33 被 REGISTRY-MASS-DELETION 两次 block 拦下；③A-12 充气=19:07→19:40 仅 35 分钟盘面 +193 行（192 PG 无，examchief 188 考试卡为主），v130 回填拆弹。
7. belt 守护在岗：pid 32804，heartbeat 22:45:47（查询时 6s 新鲜，30s 窗）；a12 监视器 cycle5 CLEAR 在岗；22:22 belt 曾做 projection_regen quadrant=conflict（removed 3，全部合法退役面）。附带：deadcure2 主会话已退出（hb_age 3609s），其 keeper 仍在循环 respawn（TTL 窗缺陷后遗症，仅观测）。
8. 与本战役映射：A=断增量源（MODT/RULING 未走 PG 直改 HEAD yaml 的 2+5 条 + 6 垃圾族 = 直写轨残余）；B=物化改道（CAP 正道 api.register→publish→render 已被 v132 走通）；C=全族门禁（mass-deletion 19:33 拦截=门在起作用；MODT/RULING 无 CAP 同款投影门=全族缺口）。

## C7b 口径与死信二期互认值（版本号表）

- 判据真源：`.runtime/tmp/st-deadcure2-20261009/tools/cycle_check2.py`（§docstring+L151-152）
  - C7（A-12 不变量）：PG snapshot creation_tokens ⊇ HEAD 面（剔除合法 retired）。`C7_head_missing_from_pg`。
  - **C7b（武装条件）**：render 删的是 DISK-only 行 → `C7b_disk_rows_render_would_delete = len(disk_keys - pg_keys)`，unexplained=不在 retired 集。判据面=**单册** capability_canonical_file_registry.yaml（REG-CAPCAN-001，family=creation_tokens，复合键 file|token）。
  - C7b=0/CLEAR = 盘面没有任何「下一次 render 会被删」的未解释行（disk ⊆ PG∪legal-retired）。
- CAP（REG-CAPCAN-001）snapshot 版本链（只读 SQL，2026-10-09 22:50）：

| 版本 | 时刻(+08) | published_by | entry_count | git_ref | 备注 |
|---|---|---|---|---|---|
| v126 | 14:46:24 | st-libfront-20261009 | 14540 | — | |
| v127 | 15:01:24 | st-libfront-20261009 | 14540 | — | deadcure2 开工时 latest=此版（面 14145） |
| **v128** | 18:47:46 | st-deadcure2-20261009 | 14598 | ea69f4816ae3 | **拆除#1**（53 GAP+3 补票+2 护票，面 14145→14203，半径 58→3） |
| v129 | 19:30:40 | st-chiefc-20261009 | 14600 | — | |
| **v130** | 19:42:09 | st-deadcure2-20261009 | 14789 | 218636c1b37a | **拆除#2**（192 充气后 backfill 189，面→14393，C7b=3 全合法退役） |
| v131 | 21:58:27 | st-deadcure2-20261009 | 14818 | 769c59bda14d | |
| v132 | 22:45:18 | **st-regsolo-20261010** | 14819 | — | 本专班主会话发布（面 14423） |

- 其余六册 latest snapshot：MODT v10（10-08 20:59:57，8759，st-vm12final-20261007-chief）｜DOC v7（10-04 20:33:22，302，st-wm1-wave0）｜ARCH-ISSUE v7（10-04 20:52:43，815，st-wm1-wave0）｜ERRCODE v4（10-04 11:24:31，800，st-sI-identity）｜CAND v5（10-04 11:24:33，623，st-sI-identity）｜RULING v9（10-05 18:08:27，302，st-fig16-20261005）。各册 ledger_version=最新 snapshot_version（132/10/7/7/4/5/9）。

## PG 基线快照表（查询时刻+七册读数）

- 查询时刻：2026-10-09T14:46:55Z / 14:48:00Z / 14:49:00Z（=22:46–22:49+08），DatabaseService().get_depgraph_conn(read_only=True)，零写。
- registry_ledger.registry_entry active 计数（active/retired）：

| 册 | family：active/retired | ledger_version | catalog updated_at(+08) |
|---|---|---|---|
| REG-CAPCAN-001 | creation_tokens **14423**/169；capabilities 391/5；垃圾族 6 个各 1（chiefc-99-delivery-20261009、file_token、t2-handover-claim-grid0926、t2-subspace-json-grid0926、t2-subspace-meta-grid0926） | 132 | **2026-10-09 22:45:18**（v132 刚落） |
| REG-MODULE-TRANSLATION-001 | entries **8089**/637；algo_submodules 405/308；battle_map_steps 341/340；battle_map_cross_cutting 17/13 | 10 | 10-08 20:59:57 |
| REG-DOC-001 | files **306**/1 | 7 | 10-04 20:33:22 |
| REG-ARCH-ISSUE-001 | entries **817**/815 | 7 | 10-04 20:52:43 |
| REG-ERRCODE-001 | error_codes **794**；known_issues 3；related_systems 3/3 | 4 | 10-04 11:24:31 |
| REG-CAND-001 | entries **623** | 5 | 10-04 11:24:33 |
| REG-RULING-001 | entries **310**/41；rulings 1/2 | 9 | 10-05 18:08:27 |

- 并发注记：查询窗口内 CAP 册在动（22:22 belt render removed3 → 22:45:18 v132 publish → 22:46:07 监视器 pg_snapshot 14423）；MODT/RULING/其余册窗口内无写入迹象。

## 欠账抽核结果（HEAD yaml vs PG active，22:52–22:54）

1. **CAP（capability_canonical_file_registry.yaml，HEAD creation_tokens=14425 vs PG 14423，差 3）**：HEAD-only 3 条全部 PG status=retired（`docs/_working/quant_methodology/07|08|12_placeholder_skeleton.md`，token=quant-methodology-…-20261006）→ **未解释欠账=0**（与监视器 ARMED=0 互证，死信二期清零态保持）。反向 PG-only 1 条：`docs/_working/regsolo_campaign/99_delivery.md|regsolo-99-delivery-20261009`（本专班 token 已入 PG 未物化进 HEAD yaml，待本战役 B 车道物化，非欠账）。
2. **MODT（module_translation_registry.yaml，HEAD entries=8091 vs PG 8089，差 2，pg-only=0）**，缺失身份：`src/zephyr/ex_core/phase_discriminator.py`、`src/zephyr/strategy_pipeline/graduated_package_feed.py`（=chiefc 车道 D C-4/C-5 终报件随 21:35 大批进 HEAD yaml，未走 PG 登记 → **A 车道断增量源的现存样本**）。algo_submodules 405/341/17 三族 HEAD=PG 零差。
3. **RULING（ruling_registry.yaml，HEAD entries=315 vs PG 310，差 5，pg-only=0）**，缺失身份：**裁定#494/#495/#496/#497/#498**（修宪+G1G3+死信二期车道裁定，YAML 已进 HEAD、PG 未登记）。
4. 数据质量新发现：CAP 册 6 个垃圾 family_key（各 1 条 active，HEAD yaml 顶层同名杂键）=畸形整档写册被账本当族收编（见结论 5）。
5. 注意：C7b 判据面只护 CAP 册；MODT/RULING 的 HEAD-only 即「若对这两册做 PG-wins render 就会被删」的同构武装——目前两册无 render 门/投影链，故不爆，但属同病灶欠账。

## 三事故时间线（各≤10 行；时刻均 2026-10-09 +08）

### ① creation_tokens 蒸发（存量欠账暴露与拆除）
- 开工五面对账（deadcure2 §四）：HEAD 14201／盘面 14203／**PG(v127) 14145=严格子集缺 56**；下一次 belt render 即删 56 条已入库条目（含 deadcure 一期台账、dexp/chiefc 战役册、exam-cost 产物），预演半径 **58**。
- 18:47:46 **v128**（st-deadcure2，event 111867–111928）：意图 API 补登 53 GAP+3 车道补票+2 在途护票 → 面 14203，半径 **58→3**；3 条 GAP 被账本按 retired 正确拒收。
- 机制证据：`.runtime/gate_audit/registry_yaml_parse.jsonl`（末写 11:09）block 三连——「顶层根键重复」「creation_tokens 不是 list(NoneType)」「**staged 内容与投影状态文件指纹不符（私改投影册无效）——此文件是 PG 账本投影：改动请走意图 API 登记+生成器重打**」。
- 双轨病定性原文（chiefc 99_delivery **§六.5**——注：§八 实为「复核命令原文」，系统性发现面在 §六/§七）："token 双轨病：batch 直写 yaml vs api.register 入 PG——A-12 B 门已倒逼账实同步，直写轨退役建议走裁定登记"；§七："capability 册=PG 投影：手改必被 REGISTRY-YAML-PARSE 拦；正道=api.register→publish_snapshot→--render；token 先行袋=2a/2b 正解"；§九①："A-12 携证重修（复发三证，蒸发者=belt 旧代码守护已重启根治）"。
- 伤害面：56+2 条在册条目（尚未真删，引信在膛被拆除）。当日处置=v128 物化。**映射=A（直写轨是欠账源）+B（PG 投影物化正道）**。

### ② -271 回滚险情（chiefc 终报落地批）
- 19:33:24 + 19:34:31：REGISTRY-MASS-DELETION **block ×2**（st-chiefc-20261009，capability 册 staged 面：deleted=290/added=311，entries_head 14596→staged 14600，lost_identity_count=3=quant_methodology 07/08/12 placeholder）→ 危险形态被门硬拦。
- 21:35 **c61765bf25**「[99_delivery·终报落地=deadcure-2 Phase1 开门信号]」落地：capability 册 numstat **1397+/271-**（271=删除行数），条目级 **删 54 块/增 278 块**（净 +224=HEAD 面 14201→14425 对平）。
- 删除样本：deadcure 一期台账族 token（00_charter/01_ledger/02_P0_tests_hole/03_ticket_register/04_pending_owner/05_tests_restore_manifest）、g_lane_r01_r16_ledger、MOD-SELL-020/blueprint 等——同 commit 内以新身份/新 token 重登（身份串换），HEAD 现存 quant placeholder 引用 2 行，PG 侧对应 3 token 已 retired（退役合法化，与 §四.2 账本拒收同源）。
- 伤害面：热册单批大改（-271 行）若按 19:33 原形态落地=290 条目蒸发级回滚。当日处置=门 block 逼出收窄形态（串换+合法退役）后落地。**映射=C（全族门禁——mass-deletion 门当日实弹咬住；MODT/RULING 缺同款门=全族缺口）**。

### ③ A-12 充气/蒸发机制
- 机制本体：`src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py:468`（projection drift probe）——盘检 `disk_sha != state.content_sha256` 即 `projection_run(mode="render")`，PG-wins 整档覆写盘面（未武装/cutover 前空转）。
- 19:07→**19:40（35 分钟）二次充气**：盘面 14203→14396（+193 行，其中 **192 条 PG 无**：st-examchief 188 考试卡 token + st-mastertc-l7 3 + st-chiefc 1）→ render 杀伤半径重新充到 192（deadcure2 §四.3）。
- 19:42:09 **v130**（st-deadcure2）：`token_backfill_disk.py --execute` 预登 189（3 拒=retired）→ 面 14393，复测 **C7b=3**（全合法退役），未解释=0。
- 20:00:54 起 `monitor_a12.py` 在岗（300s 一采）：cycle0 head 14201/disk 14393/pg 14393 CLEAR → 22:46:07 cycle5 head 14425/disk 14422/pg 14423 **CLEAR**（ARMED=0/FIRED=0 全程）。
- 22:22:36 bottleneck ledger：`registry_drift … projection_regen quadrant=conflict revision=130 actor=belt_daemon`（added 0/removed 3）——belt 当日实际开过一次火，删的 3 行=合法退役面（对应 diff `registry_drift_20261009T142229486786.diff`）。
- 根因定性：同判据修复 10-07 做过一次（账本事件 111099，actor=st-mastertc-l0），缺口 36h 内长回 → 病灶在**写入侧仍允许直改 YAML**（token 先行袋整档写册）；「盘面⊇HEAD 不变量进门」尚未落地。附带取证：examchief keeper 同窗 idle-timeout(1800s) 误杀退出=keeper 判据缺陷全会话级。
- 伤害面：两次合计 58+192 行武装半径（均拆除在删除前）。当日处置=v128/v130 两次拆除+监视器上岗+99_delivery §九① 呈报携证重修。**映射=A（增量源=直写轨未断）+B（render/物化路径改道）+C（门禁护族）**。

## belt 守护现状（只读，22:45–22:48）

- queue root=`.runtime/commit_queue`（`commit_belt_daemon.py:85-86` `_queue_root`）；心跳文件 `belt_daemon.heartbeat`：`{"pid": 32804, "wall_ts": 1791557147.747}` = 22:45:47（查询 22:45:53，**6 秒新鲜**，30s 心跳窗）→ **守护在岗**。
- 单例锁 `belt_daemon.lock`：pid 32804（mtime 22:22，与 22:22 render 事件吻合）。tasklist python.exe 十余进程；wmic cmdline 匹配 belt 返空=已知查询面误差（deadcure2 §9-2 教训：以心跳文件实读为准，勿以模式串猜进程）。
- a12 监视器在岗（cycle5 22:46:07 CLEAR）；deadcure2 keeper 循环 respawn（cycle29 22:48:19，`RESPAWN(last_status=exited reason=session not in registry)`，其会话 hb_age 3609s——死信二期主会话已退场，仅观测不动作）。

## 证据（路径+锚点）

- C7b 判据：`.runtime/tmp/st-deadcure2-20261009/tools/cycle_check2.py`（docstring C7/C7b；L151-152）
- 死信二期口径与 A-12 全段：`docs/_working/deadcure_campaign2/01_phase0_ledger.md` §四.1-4.3、§五、§九
- 双轨病定性：`docs/_working/chiefc_campaign/99_delivery.md` §六.5、§七、§九残留①
- A-12 机制：`src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py:468`（projection drift probe）、`:85-86`（queue root）
- 蒸发/充气 diff：`.runtime/gate_audit/registry_drift_20261009T114049946408.diff`（19:40）、`…T114312726373.diff`（19:43，+936 行 exam_card 面）、`…T142229486786.diff`（22:22 belt 开火）
- 投影门拦截：`.runtime/gate_audit/registry_yaml_parse.jsonl`（末写 11:09 block 三连）
- mass-deletion 拦截：`.runtime/gate_audit/registry_mass_deletion.jsonl`（19:33:24/19:34:31 block×2）
- -271 提交：`git show c61765bf25 --numstat`（capability 册 1397+/271-；条目删 54/增 278）
- belt 活性：`.runtime/commit_queue/belt_daemon.heartbeat`、`belt_daemon.lock`；监视 `.runtime/tmp/st-deadcure2-20261009/lanes/a12_monitor.jsonl`（cycle0-5）；`.runtime/audit/bottleneck_ledger.jsonl`（22:22:36 registry_drift 行）
- PG 读数：registry_ledger.registry_entry/registry_snapshot/registry_catalog（DatabaseService read_only，22:46-22:54 五次查询，时刻均已在正文标注）
