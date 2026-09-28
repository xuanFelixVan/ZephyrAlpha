---
ttl: task_bound
volume: wiring_M_meter_hardening
session: st-ailayer-final-20260924
creation_token: fullflow-w6m-meter-hardening-20260926
---

# W6-M 施工记录：机生对账尺逐面修硬（靶件=generate_fullflow_crosscheck.py）

> 工单=`05_missing_p0/rb1_meter_attacks.md`（红队 RB-1 案卷七面）；判据=总筹波2 指挥册派单六条；
> 本卷只改三件靶件（尺/配对测试/机生产物），**未碰任何作业簿正文、未碰 catalogs、未碰 flag、
> 未碰 GATE-21 语义**（尺仍"只判生成物陈旧"）。零提交、零入队、零 claim。

## 一、六面修硬对照（每面：绕过复现 → 修后拦住）

对照台=`.runtime/tmp/wiring_M/rb_face_repro.py`（同一攻击夹具分别喂"改前尺"＝index blob
`b803a4cf` 与"改后尺"，只读生产）。改前/改后实测：

| 面 | 绕过（改前实测） | 修后（实测） |
|----|------------------|--------------|
| ①声明行反讽句 | `本册覆盖 F01 是事实…` 前缀匹配即记功（案卷 V1 行=True） | 严格式 `^本册覆盖(?:\s*F\d{2,3})(?:\s*[/、,]\s*F\d{2,3})*$`，行尾有散文⇒整行不记功＋报 `declaration_line_malformed`。夹具内 F01 不再被记功，只有纯声明行 F02 记功 |
| ①补 `covers:` 空格分隔 | 解析成字符串/失败仍记功（案卷 A8.3） | 必须 YAML 列表；非列表/整块不可解析⇒零记功＋`covers_surface_not_creditable`；流式与块式列表照常记功（反向自证） |
| ②标题行塞号 | 删通道前：一行标题塞 20 号→uncovered 45→25（案卷 V2.1） | **删掉"行首 `#` 也算认领"整条通道**；夹具中 `# 标题 F01 F03 F04 F05 F06 F123` 一行 → 一都不记；同册改写成严格式声明行后 4/4 全记（证明拦的是通道不是号） |
| ③非法长号 | `F_ID_RE` 无尾锚 ⇒ `F12345678` 被切成 `F123` 记功（案卷 A7.4，零成本零痕迹）；往总册塞 `F999` 行顶高 f_links 而零告警（A7.1） | 候选号整串数字吃掉、只禁"后面还有数字"⇒**无切片**；位数非 2-3 或不在总册号集⇒不记功且报 `illegal_f_token_in_claim_surface`（含 `too_many_digits/too_few_digits/not_in_total_book`）；总册侧新增号段不变式 `f_id_noncontiguous`/`f_id_not_started_at_F01` |
| ④WIP 簿入记录 | 尺读盘面（rglob）⇒他道未 `git add` 的簿被写进真源记录，WIP 一丢 YAML 留悬空证据且恒红（案卷 P4，最重一条） | 作业簿**集合**改为 `git -c core.quotePath=false ls-tree -r --name-only HEAD`；未落地件不记功、不进 census（夹具：改前 7 号全 covered→改后仅 1 号，WIP 记功=False）；`mining_books.measured` 改取 HEAD 数（6，盘面 158/7 只作 P-0 观测面） |
| ⑤无 `.git` 读外层 | 无 `.git` 的目录上溯外层仓 HEAD，`head_count=0` 却标 `status: ok`（案卷 P1.3）；git 不在 PATH 时 `status=partial` 不进 unavailable、不算红（P1.5/P2.5）；`core.quotePath` 默认值下 33 本非 ASCII 册从 HEAD 面消失（P1.1） | 三重前置：根下有 `.git`→`rev-parse --show-toplevel` 成功→toplevel==本仓根；任一不满足⇒`unavailable`+`measured=null`+`head_tracking_ok=false`+`red=true`。所有 git 调用带 `-c core.quotePath=false`。夹具实测：改前 `status=ok`，改后 `status=unavailable` |
| ⑥豁免清单孤儿 | 清单手工维护、无任何校验，实测躺一条盘上不存在的 `91_chief_command_wave2.md`（案卷 A2.4） | 已删该孤儿（12→11 条）；清单受尺自守：不在 HEAD⇒`non_workbook_exclusion_orphan`（盘上无此件）/`non_workbook_exclusion_not_landed`（已 staged 未落地），两态分开报。夹具实测：改前检出 0 条，改后检出 11 条 |
| ⑦自述与实现背离 | `definition.covered` 仍写"正文 grep"（案卷 V0.4/A8.5）；工厂面 method 自称"等价 grep -c"实为去重（P3） | 口径串改由 `CLAIM_SURFACE_DESC` 导出（三处声明位＋删掉的通道＋合法性判据全写进产物）；`mining_books.method` 写明 HEAD 面；工厂面 method 改写明"去重"并新增 `raw_line_count`/`duplicate_fac_lines` 观测＋`factory_fac_line_duplicates` 漂移 |
| 附：CRLF 恒红 | 检出被 renormalize 成 CRLF 的产物⇒`--check` rc=1 恒红（案卷 A6.4） | `--check` 比对前行尾归一（**不涉 uncovered**，只判陈旧的语义未变）；内容差异仍 rc=1 |

## 二、生产读数（修前 → 修后，同盘面同 HEAD 实测）

| 字段 | 修前（盘面料＋宽认领面） | 修后（HEAD 面＋严格声明位） | 为什么这样变 |
|------|--------------------------|------------------------------|--------------|
| `coverage_matrix.totals` | links 122 / covered 101 / uncovered 21 | links 122 / **covered 49 / uncovered 73** | 两处收紧叠加：①40 本册只在 index 未入 HEAD（未落地不记功）；②标题行/散文通道删除，`本册覆盖 …（带括号散文）` 的 21 行不再记功。**判据只变严，无任何放宽** |
| `counts.mining_books.measured` | 156（盘面 rglob） | **118（HEAD 跟踪集）**，盘面 158-161 降为 `detail.disk_count` 观测（在途件随盘变动，本行只作时点记录） | 实测面改锚落地面；`not_in_head_count=40-43` 即 P-0 敞口 |
| `workbook_count / tracked` | 146 / — | 112 / 118（差 6＝清单排除面） | 作业簿集合换源 |
| `drift_summary.total_drifts` | 5 | 31（5 条原有 claimed≠measured ＋21 条 `declaration_line_malformed` ＋5 条 `non_workbook_exclusion_not_landed`） | 新增"不认且必报"面；`unavailable_metrics=[]`、`head_tracking_ok=true` |
| 号段不变式 | 无对照 | 通过（F01..F122 连续、首号 F01，无 `f_id_noncontiguous`） | 新增能力，当前真源干净 |
| `--check` / GATE-21 | 开工时 STALE rc=1（盘面上他道 WIP 引起） | `fresh` rc=0；GATE-21 整台 PASS | 盘面 WIP 不再进认领面⇒产物不再被在途件翻红（观测面仍会变，见下"落地次序"） |

**预期行为提醒（回执同句）**：改成读 HEAD 后，本机盘上新写的册**不再改变产物**——已在夹具上验证：
`coverage_matrix` 的 `totals/covered_ids/uncovered_ids/segments` 与 `f_token_census_per_workbook`
在新增/删除一本未落地册时逐字节不变，只有 `detail.disk_count`/`not_in_head_*`/
`untracked_books_ignored_*` 这些 P-0 观测面随之变化。

## 三、落地次序（总筹须知的唯一副作用）

尺的实测面＝HEAD，而产物本身要随册一起提交，故存在一次性自指：**每波首个提交**若把新册与
YAML 同袋提交，提交后 HEAD 变了 ⇒ 下一轮再生成必然 STALE 一次。处方（不必改尺、不改门禁语义）：
落地序列写成"提交册 → 重跑尺 → 再提交 YAML"，或直接把"重跑尺"放在带齐全部新册的那个 HEAD 之后。
若总筹认为须为此放宽（例如改读 index），那是门禁语义改动，**本车道不自裁**，已列 §五待裁。

## 四、新增/改动的回归测（配对测试 27 条真跑真绿）

钉入的六面绕过（先证绕过、再证拦住，每面配反向自证）：
1. `test_rb_face1_sarcastic_declaration_line_is_not_credit` — 反讽句不记功＋留 2 条 `declaration_line_malformed`；同册纯声明行仍记功
2. `test_covers_surface_must_be_a_yaml_list` — 空格分隔不记功且报 `covers_not_a_list`；流式/块式列表记功；坏 frontmatter 报 `frontmatter_unparsable`
3. `test_rb_face2_title_line_cannot_launder_twenty_ids` — 标题行塞一排号零记功（covered=0）；改写为严格式后全覆盖
4. `test_rb_face3_illegal_long_number_cannot_launder_and_reports` — `F5/F678/F0506/文件名 F12345678` 全部不记功且各报漂移；合法号照常记功
5. `test_rb_face3b_illegal_id_inserted_into_total_book_is_reported` — 总册塞 `F999` ⇒ `f_id_noncontiguous` 报缺号清单
6. `test_rb_face4_uncommitted_wip_book_never_enters_the_record` — 未落地 WIP 零记功、不进 census、被观测在 `untracked_books_ignored_*`；WIP 丢弃后矩阵逐字段不变（无悬空证据）；同一册落地后立刻记功
7. `test_rb_face4b_no_quiet_degradation_when_git_is_unusable` — PATH 清空 ⇒ `unavailable`+`measured=null`+进 `unavailable_metrics`+red
8. `test_rb_face5_no_git_dir_must_not_read_outer_repo` — 内层无 `.git`（外层 HEAD 看得见内层路径）⇒ unavailable 且不算绿；坏 `.git` 目录亦 unavailable
9. `test_rb_face5b_non_ascii_books_survive_head_listing` — 中文目录册在 HEAD 面不消失、并出现八进制引号即判失败
10. `test_rb_face6_exemption_list_orphan_is_reported` ＋ `test_shipped_exemption_list_has_no_true_orphans` — 塞孤儿必报；未落地报 not_landed；出厂清单零真孤儿（生产树自证）
11. `test_definition_text_matches_implementation` / `test_factory_duplicate_fac_lines_are_reported` / `test_check_is_eol_insensitive` / `test_check_passes_on_fresh_and_fails_on_hand_edit` — 自述一致、去重背离现形、只判陈旧语义与手改必红

保留的"能红族"与反向自证（防修过头谁都不算）：`test_clean_fixture_reports_zero_drift`、
`test_caught_claimed_ne_measured_roor`、`test_caught_stale_tdm_node_claim`、
`test_unavailable_metric_is_reported_not_guessed`、`test_duplicate_f_rows_are_flagged`、
`test_coverage_goes_red_when_a_workbook_is_removed`、`test_skeleton_index_books_do_not_count_as_coverage`、
`test_ruling_book_listing_gaps_does_not_claim_coverage`、幂等两测。
夹具新增 `git_land()`（真 `git init/add/commit`），git 不可用即 assert 失败——**测试不许静默走降级路径**。

## 五、待登 / 待裁（本车道不自裁）

- 待登：尺的 depgraph 产物声明新增消费面（`git ls-tree HEAD` 读 HEAD、`-c core.quotePath=false`）；
  `NON_WORKBOOK_RELS` 生成器化（按册型判定）未做——本轮只加"自守校验"，清单仍手工 11 条，
  是否退役成生成器请总筹排期（案卷 §十.2）。
- 待登：案卷 §十.4"结论面闸"（YAML `uncovered_ids` 与分诊册二分表逐格互证）未做——它会把
  GATE-21 从"只判陈旧"扩成"判世界"，属门禁语义改动，须裁。
- 待登：`--auto-fix` 通道仍会让各 check 直写本 YAML（案卷 A6.7，防固化他道 WIP 的一半风险）。
  修法在 `commit_gates`/validators 侧＝本车道禁触面，交总筹。
- 待裁：§三 的落地次序副作用是否用"读 index"消掉（改语义，本车道不动）。
- 待办移交（**不是本车道活**）：21 条 `declaration_line_malformed` 分布在 20 本**已落地**册
  （`m1_data/01_ingest.md` 2 条，`02_cleaning/04_cold_storage/05_tdm_crossaxis/01_auto_runtime/
  04_gpu_matrix/05_cost_gates/01_runtime_guards/03_registry_families/01_ai_layer_six_families/
  02_capability_lookup/04_meta_question_pg/01_windows_schedtasks/02_inrepo_daemons/
  03_backup_coldstore/01_dashboard/02_kill_switch/04_ex_core_ladder/05_ex_sor/06_compliance_gates`
  各 1 条）——它们的"本册覆盖 Fnn（解释…）"行尾带散文，严格式即拦。册的声明行由别道补，
  补完 uncovered 自然回落；本轮未改任何册正文。
- 并发提示：本车道施工期间 `generate_fullflow_crosscheck.py` 被外来进程加过两处注解
  （头部 `# [TTL] permanent`、尾部 `# noqa: m11-perm-manual-legitimate  M11豁免: …`），
  均**原样保留**未改（改他人标记＝归属篡改）；`ruff check` 对后者报一条"noqa 指令格式"warning
  （非 error，且带中文尾巴），也不由本车道代修。`scripts/governance/fullflow/__init__.py`
  亦有他道 +3 行改动（非本车道所写）。若别道同时改此三件靶件，落地前须先逐字节比对。
- 未落地面观测（施工中途实测）：`m1_data/01_ingest.md` 等 20 本已落地册的工作树副本正被别道
  +2 行补声明行（＝§五 移交清单的同一批），其字节未进 HEAD 故对本轮读数无影响——这正是尺改读
  HEAD 后想要的行为（在途修补不再翻动产物）。

## 六、文件清单与复核命令

改动文件（全部在 worktree，零新增生产件；本卷与对照台是车道产物）：
- `scripts/governance/fullflow/generate_fullflow_crosscheck.py`（尺，六面修硬）
- `tests/governance/fullflow/test_fullflow_crosscheck_generator.py`（27 测）
- `docs/_working/fullflow_mining/00_skeleton/91_machine_crosscheck.yaml`（机生产物，重生成）
- `docs/_working/fullflow_mining/05_missing_p0/wiring_M_meter_hardening.md`（本卷）
- `.runtime/tmp/wiring_M/{rb_face_repro.py,pre_gen.py,repo_pre,repo_post,face5}`（临时区，不入库）

```bash
cd D:/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:$PATH"
export PYTHONPATH="$PWD/src"          # 自证 zephyr 落在 worktree（裸 python 会导主区包＝假绿源）
python -c "import zephyr;print(zephyr.__file__)"      # → ...\st-ailayer-final-20260924\src\zephyr\__init__.py
python -m pytest tests/governance/fullflow/test_fullflow_crosscheck_generator.py -q     # 27 passed
python .runtime/tmp/wiring_M/rb_face_repro.py                                            # 改前/改后逐面对照
python scripts/governance/fullflow/generate_fullflow_crosscheck.py --check --quiet       # rc=0 fresh
python scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py   # GATE-21 PASS
```

三态结论：**完工**（六面全部修硬＋回归测真跑真绿＋产物重生成幂等）；
残余＝§五 移交项（21 条声明行待别道补、落地次序待总筹定、结论面闸与 auto-fix 待裁）。
