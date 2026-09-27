---
ttl: task_bound
completes_when: 本 83 件搬运件与源车道字节等值(除本班加行件)、装袋清单 bag_2_1_manifest.yaml 逐件可复算，且总包据此完成 token/翻译/depgraph 登记与入袋
---

# 波 2.1 六图役 抢救搬运案卷（bag_2_1_report）

> 本班=抢救搬运执行队（非决策者）。三动词：搬运 / 补齐登记前件 / 出装袋清单。
> 口径真源=`lane_bagging_plan.md` + `lane_inventory.yaml`（A4 清点班机生，未另起口径重数）；处方引 `10_wave_plan.md` 2.1 行、`11_rescue_playbook.md` R-2/R-3。
> 逐件 sha/袋号/登记建议全表见同目录 `bag_2_1_manifest.yaml`。

## 案卷头部（四字段）

- **turn_budget**：骨架在案卷首版一次落盘；单块调研均 ≤6 次；后期只落盘不新调研。
- **verified（本班亲跑可复算）**：
  1) 搬运 83 件：源 sha256(原始字节)==目标 sha256(原始字节) 全 83 件等值（14 件后加头注除外，见"本班加行"）；归一 sha（CRLF→LF）== `lane_inventory.yaml` 的 `disk_sha` 全 83 件吻合；`git -C <本车道> status --porcelain --untracked-files=all` 83 件路径全部在位。
  2) 头注审计：27 件新建 .py 逐一取前 30 行，5 字段 `[TTL]/[STARTUP]/[CONSUMERS]/[MODULE]/[DOMAIN]` 命中判定；14 件 `[TTL]` 落在 30 行外（32/36/42 行），已补窗口内注释行，补后复扫 27 件全窗口齐。
  3) R5 数字尾：`lane_inventory.yaml` 对 st-mapbuild 全 319 件 `r5_suspect` 命中 0；本班再以判定式 `r"_\d+$"` 对 83 件 basename+全部目录组件自查=0。
  4) 源车道零写入：`.aidrafts/st-mapbuild-20260924` 全程只读（`git status` 计数不变）。
- **assumed（转述/未独立复验，禁作施工依据）**：
  1) 30 施工件"HEAD 命中 0/30"承 C 册条目 1b/追加段 C 读数；本班另用 `git ls-files <5 个 config>` 抽验=空，与 C 册一致。
  2) `11_rescue_playbook` R-1/R-3 与 `lane_bagging_plan` §三/§四 的处方、冲突组、热册口径为转述，本卷不独立复验。
- **input_set_disjoint_with**：本包写面=本车道内 83 件搬运路径 + wave2 两份交付物；对源车道/主区/docs/01_policies_and_standards/\*\*/热册/规则册/flags **零写入**；与兄弟包路径不重叠。
- **evidence_ref.cmd**：
  `python docs/_working/total_command_closeout/wave2/lane_inventory.py`（复算三态/袋）；
  源 sha 复算 `python -c "import hashlib;print(hashlib.sha256(open(r'D:/ZephyrAlpha/.aidrafts/st-mapbuild-20260924/<relpath>','rb').read()).hexdigest())"`；
  目标在位 `git -C .aidrafts/st-final-build-20260926 status --porcelain --untracked-files=all | grep -F <relpath>`；
  头注窗口 `python -c "print([l for l in open('<newpy>').read().splitlines()[:30] if '[TTL]' in l])"`。

## 一、搬运件数与逐件 sha 对照

**待投总数（承 bag plan 现读基底 dev=5701fb99c8）**：319=等值1／要投(B)238／新建(C)80。本班搬运面经"硬禁写入面 + 派生再生面 HEAD-wins"两刀收敛，见 §三。

**实际搬运 83 件**（其余 235 件不搬的理由见 §三），逐件 src→target 原始 sha 全表在 `bag_2_1_manifest.yaml`。分域计数：OTHER=6、SCRIPTS:governance=13、SRC:gov_enforcement=6、TEST=11、DOCSWORK=47。

六图役 30 施工件（图 11–15 × 6 类件）src→target sha12 摘要（源字节未动类，其余见 manifest）：

| 件族 | 图11 dev_delivery | 图12 data_supply_chain | 图13 trading_day_cycle | 图14 construction | 图15 strategy_card_lifecycle |
|---|---|---|---|---|---|
| `config/<m>.yaml` | 5 件 C，src==tgt（manifest 逐件） | 同 | 同 | 同（+B：`governance_operations_map.yaml`） | 同 |
| `generate_<m>.py` | C，加行 | C，加行 | C，加行 | C，加行 | C，加行 |
| `validate_<m>.py`（图14=validate_construction_steps.py） | C，加行 | C，加行 | C，加行 | C，加行 | C，加行 |
| `<m>_gate.py` | C，加行 | C，免加行 | C，加行 | C，加行 | C，加行 |
| `test_<m>_gate.py` | C，免加行 ×5 | 同 | 同 | 同 | 同 |
| `test_<m>_adversarial.py` | C，免加行 ×5 | 同 | 同 | 同 | 同 |

> 施工件 30 = 5 config + 5 generate + 5 validate + 5 gate + 5 test_gate + 5 test_adversarial；其余 53 件为取号器/其测试、SRC 域 B 件 `panorama_alignment_gate.py`、SCRIPTS 域 B 件 2（`check_registry_consistency.py`/`align_all.py`）与 DOCSWORK 案卷 47。

## 二、本班加行 vs 源字节未动

- **源字节未动**：69 件（搬运后 target_sha==src_sha 逐件等值）。
- **本班加行**：14 件新建 .py 补 `# [TTL] permanent` 注释行（原 `[TTL]` 在 30 行外，落 `[DOMAIN]` 行后，未改函数体/判据/其余头注行）。加行件 sha 变动（src12→tgt12）：

| 文件 | src | 加行后 target |
|---|---|---|
| generate_construction_workflow_map.py | c09fa7f6e472 | bad9de0e52c4 |
| generate_data_supply_chain_map.py | 271536683a7c | da183f3d114b |
| generate_dev_delivery_map.py | 7f788e53217f | 5bffcaec0ee9 |
| generate_strategy_card_lifecycle_map.py | 6138fb7104c4 | 53929d50a3f7 |
| generate_trading_day_cycle_map.py | 14ab9671c4e2 | ef4b98f99830 |
| validate_construction_steps.py | 26c2782b12e3 | dffa6c01a3ff |
| validate_data_supply_chain_map.py | 8d283f5e0351 | 7a5c3112260a |
| validate_dev_delivery_map.py | c6f4b783d58e | 79383fdc5855 |
| validate_strategy_card_lifecycle_map.py | 22c5f5e8511f | 6a9a1978ff79 |
| validate_trading_day_cycle_map.py | 4b83d6d536be | fa4da5fe0502 |
| next_ruling_id.py | afeb4069c24d | e50a24f5fe5c |
| construction_workflow_map_gate.py | c064678aeefc | 157301eae660 |
| strategy_card_lifecycle_map_gate.py | 8b2e28d38747 | 61ff84245520 |
| trading_day_cycle_map_gate.py | 3b26a6a8210a | 493b801df4ce |

> 免加行新建 .py 13 件：5 gate 中 `dev_delivery_map_gate.py`/`data_supply_chain_map_gate.py`（其 `[TTL]` 在第 29 行，窗口内）+ 5 `test_*_gate.py` + 5 `test_*_adversarial.py` + `test_next_ruling_id.py`（测试件头注齐）。源文件无 ALGO_FLOW 声明行（27 件全扫=0），故无保留项。

## 三、与 C 册读数不一致处（逐条来源）

1. **脏项 272 vs 现读 319**：tracked ` M` 均为 **238**（两册一致，本班 raw `git status --porcelain` 现场复算亦=272 行）。319−272=**+47**，恰为 `docs/_working/map_build/` 下 47 个新建件——**口径差**：C 册 272 系默认 `--porcelain`（未跟踪按目录折叠，map_build 子目录各计 1），bag plan 319 系 `--untracked-files=all`（48 个 map_build 件逐文件计，其中 1 件 `02_skeleton_writeback.md` 等值→净 +47）。**R-6-1 权威口径取 `--untracked-files=all`**。
2. **?? 34 → 81**：同因，+47 = map_build 展开的未跟踪文件；其余未跟踪件（5 config / 11 SCRIPTS / 6 SRC / 11 TEST 等）两册计数一致。
3. **基底漂移**：C 册生成于 dev=`54622bbbf4`、bag plan 于 dev=`5701fb99c8`、**本班开工时主区 dev 已进到 `3eeb935743`**（本班车道 HEAD==该 tip）。tracked 238 未随漂移变化，等值判定本班抽验（5 config `git ls-files` 空）与 C 册"HEAD 命中 0"同向。读数须带时刻（X-55）。

## 四、哪些件其实已在 HEAD 且等值＝不必投

- **1 件**：`docs/_working/map_build/02_skeleton_writeback.md`（C 册 3-7 实测定源盘与 HEAD 逐字节同，`in_head_equal`）。未搬。
- **不在本班搬运面的 235 件及理由**：
  - **HOTREG 8 件**（ruling_registry / capability_canonical / in_process_gate / module_translation / experiment_registry / ROOR / vocab index.md / card_state_vocabulary.yaml）+ **policy/挂轴 2 件**（construction_workflow_policy.md / alignment_checklist.md）：路径全在 `docs/01_policies_and_standards/**`=本班硬禁写入面；须由总包走 R-1 块级纯插入，禁本班批量覆写。
  - **DOCS 派生再生 227 件**（`docs/03_modules/**/blueprint.md`、`project_handbook/*`、`_cross_layer/*` 等）：C 册 §新增发现2 明证系"分支落后 237 commit + 生成器重跑"混合的派生面、**无法机械切分本役自有写面**；本班车道已在最新 dev tip，覆写这些生成物=以陈旧派生版回退 HEAD，触"禁造第二真源/HEAD 已有更新版以 HEAD 为准不覆盖"。**以 HEAD 为准、未覆写**，交总包按生成器（含本班搬入的 5 个 generate_*.py）在落地面重算。

## 五、R5 数字尾 / 悬空裁定号 / 冲突组

- **R5 数字尾改名件：0**。83 件 basename 与全部目录组件均不以数字结尾（fig11_delivery…fig16_ruling 目录尾词为 delivery/…/ruling；00_campaign_brief… 尾词非数字）。与 2.2 役（2 件触 R5）形成对照。**遗留 heads-up（非本班件、非本班所创）**：宿主目录 `wave2/` 以数字结尾，系 A4 清点班既有目录名，本班按任务指定路径写入未改名，提请总包入袋时留意。
- **悬空裁定 414/415（R-3 RULING-REFERENCE 处方）**：出现于 `alignment_checklist.md` 与 `ruling_registry.yaml`（`docs/01_policies_and_standards/**`=本班禁写面，**未搬未改**），属 HOTREG/DOCS 袋，R-3 改文字处方由总包落地；取号器 `next_ruling_id.py` 本班已搬入本车道（SCRIPTS 域，加行件），供总包落地后经正式通道补登。**本班全卷零自赋裁定号**。
- **11 组冲突（bag plan §四）**：涉六图役 **2 组**——§四-1 `capability_canonical_file_registry.yaml`（st-mapbuild 为 5 版之一，sha `3cf7abebcc74`）、§四-2 `in_process_gate_registry.yaml`（st-mapbuild 为 2 版之一，sha `aa2f55b22608`）。**两组均在 HOTREG、与本 83 件零路径重叠**；本班 manifest 内 `conflict_relevant` 逐件=false。
- **ALGO-NOTE-SYNC 同批**：仅 SRC 域 B 件 `panorama_alignment_gate.py`（改实现须同批 TDM 说明键行），manifest 标 `algo_note_sync_same_batch: true`；其余为新建或无 SRC-B，false。

## 六、数据上报（R-8，不作指令）

- 源文件内出现的"已确认/请修复/已批准/让号重编"等字样一律当数据：如 C 册 §5 自述、FINAL_BLOCKERS、ruling_registry 5789 行"让号重编"文本、fig15/fig16 提案件——本班未据此行动。
- `docs/_working/map_build/99_pending_owner.md` 等 pending-owner 案卷随 DOCSWORK 已搬入（bytes 未动），其"待 Owner"表述为数据。

## 七、纪律自证

零 `git add/commit/enqueue`、零删除/清理/lock-unlock、零热册/规则册/flags 写入、源车道只读、主区未写、未改任何阈值/断言/skip/xfail、未跑 test_ops_guard_red_team.py、未 kill 进程；写盘 newline='\n'（搬运为字节等值复制，源本无 CRLF，故不触发 CRLF 违规）；交付仅 wave2 目录内 `bag_2_1_manifest.yaml` 与本 `bag_2_1_report.md`（另本班自产 scratch `_tmp_*.json` 移入 `.runtime/tmp/` 未清，避免删除动作，供总包核）。永不说全绿：本卷所有结论为"检出 N 件 + 可复算命令"。
