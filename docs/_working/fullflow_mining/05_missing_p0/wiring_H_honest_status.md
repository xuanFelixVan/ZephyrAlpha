---
ttl: task_bound
volume: wiring_H_honest_status
session: st-ailayer-final-20260924
creation_token: w6h-honest-status-wave2-20260926
---

# W6-H 施工记录：三件"报 ok=True 但其实什么都没判"改诚实读数

> 车道＝W6-H（波2 施工）；工作面=worktree `D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924`；
> 零提交、零入队、零 claim、零 release（只 `git add` 自家 6 个路径，index==worktree 已自证）。
> 判据真源＝红队案卷 `rb2_guard_attacks.md` §二（清洗）/§三.4（配比）/§六·§七（秘钥）/§十（修法清单 A1/A2/A6）。
> 共同原则（本车道唯一改判口径）：**`ok=True` 只能表示"跑过且判干净"**，不得表示"没跑/跑不动/跑了一部分"。
> 纪律自证：未改任何判据数值与阈值（承载册/秘钥册/权级表三张真源的数值面零改动，`config/cleaning_rules.yaml` 本车道未动）；
> 收紧断言处见 §四，无为变绿放宽处。

## 一、cleaning_rules_hosting（清洗托管腿）

### 修前四条绕过（红队实测）→ 修后拦它的测

| # | 修前说谎形态 | 修后读数 | 拦住它的测（全绿） |
|---|---|---|---|
| 1 | 两表之一恒失败仍 `ok=True`（口径只惩罚"全表 degraded"，加一张表即可稀释） | `status=degraded_partial`＋`ok=False`，`degraded_tables` 单列 | `test_one_degraded_table_never_dilutes_to_ok` |
| 2 | 查询回 0 行被当"已巡检且干净"（`ok=True` 零告警） | 该表记 `no_samples`→整体 `degraded_partial`＋`ok=False`＋**LEVEL_WARN"零样本"**＋进报告 | `test_zero_row_sample_is_not_inspected_clean` |
| 3 | `enabled=false`／`disabled_flag` 存在／节奏闸命中 三条"根本没跑"全回 `ok=True` 且零告警零留痕 | 统一 `not_run(reason)`＋`ok=False`＋WARN 出声＋状态台账（`*_cleaning_gate_status_ledger.json`，刻意不匹配报告文件名） | `test_not_run_paths_are_honest`（参数化 3 案） |
| 4 | 承载册非法字节抛未声明的 `UnicodeDecodeError`（CLI 只捕声明错型＝裸 traceback） | 归 `CleaningGateConfigError`，错型不外溢 | `test_illegal_bytes_raise_declared_error_type` |
| 附 | 节奏闸状态真源＝文件名前 10 字符，写一份当天命名的空 JSON 即可让本腿睡 7 天 | 报告正文须验（`gate` 自对＋`inspection_ran`），降级/零样本/未跑**都不占节奏闸** | `test_forged_report_cannot_hypnotise_cadence` |

结果面四态常量：`STATUS_RAN_CLEAN / STATUS_RAN_FINDINGS / STATUS_DEGRADED_PARTIAL / STATUS_NOT_RUN`，
`ok = (status == ran_and_clean)` 是**唯一**通路（`gate_status()` 集中判定，判序：降级/零样本 > 命中 > 干净）。
CLI 退出码同批对齐：`0=跑过且判干净｜N=命中表数｜252=未生效（降级/零样本/未跑）｜253=全表降级｜254=配置错`
（新增 `status_exit_code`，`_EXIT_PARTIAL_DEGRADED=252`）。

### ⚠ 结论消费面的处置＝**如实报半接线（未接）**，不写成"已执法"

- 实测坐标（本车道同分钟复跑，非记忆）：`src/zephyr/data/scheduler.py:250` 返回
  `{"data_supply_sentinel": bool(result.get("ok", False))}`——读的是**断供腿**的 ok；
  `supply_sentinel.py:541` 把本腿结论存进 `summary["cleaning_gate"]` 后**无任何读者**。
  ⇒ 本腿 `ok=False`（承载册坏／降级／命中脏数据）时排班面仍报绿，出声通道只有 Alerter 一条。
- 处置：**未接**。理由＝宿主文件在 `src/zephyr/data/**`（92 册 §一.4 列为在途热件，车道禁触），
  且"接哪一行、以什么强度进排班判定"属 production 流转，不该由施工车道自裁。
- 已做的最小诚实面（都在本件自身，零越界）：结论字典与报告/台账都带
  `enforcement_state="advisory_only_half_wired"`＋`enforcement_note`（自述"只进告警面与台账，
  不进排班判定，禁称已执法"），并新增一条**把"半接线"钉成可证伪事实**的测：
  `test_host_stores_conclusion_but_scheduling_reads_it_not`（宿主 summary 收结论但 `ok` 不受影响）。
  ⇒ 将来总筹真接那一行时，这条测必红，逼改测的人当面核对口径（防"接了没接"再糊一次）。
- 待登项（给总筹的一行）：`scheduler.py` L13 分支把 `result["cleaning_gate"]["ok"]` 并入
  `data_supply_sentinel` 结论（或在 `schedule.yaml` 明确"本腿只出声、不参与判定"并同批改
  `cleaning_rules_hosting.py [CONSUMERS]` 与 `config/schedule.yaml:231` 描述＝rb2 清单 B4）。

## 二、weight_ssot（配比单头尺）

| 修前 | 修后 | 拦住它的测 |
|---|---|---|
| `classify_path` 认不出作者→回 `None`→`scan_weight_writers` 直接 `continue`＝**野生写手隐身**（rb2 §三.4 判为"最大结构性逃生"，第二头探测器只有测试调用） | 认不出→一律判 `WILD_WRITER`（永不 None）；新增 `find_weight_writing_sites/find_wild_weight_writers`（严判据：同行须同现 `strategy_ref` 与 weight 写入形状），产物经 `wild_writer_intents` **进 `authority_census` 的 conflicts 面**，`attributable=False` 且计入 `census["wild_writer_sites"]`/`clean=False`/`unattributable`；宿主 `alloc_authority_guard` 本就 `raise if census["conflicts"]`⇒拒写图 | `test_classify_path_never_returns_none_anymore`／`test_lone_wild_writer_is_a_conflict_not_a_non_event`／`test_census_surfaces_wild_writers_and_is_not_clean` |
| 反向隐身：把 `PRODUCER_PATH_KEYS["auto_mount"]` 改成自己文件的别名，即可从 census 消失且写点一起消失 | 改别名后该文件立刻以**野生**身份被 census 抓住（隐身＝自曝） | `test_self_alias_to_hide_now_surfaces_as_wild` |
| 未登记源文件读不到时静默 `continue`（与件自设 INVARIANTS ④"读不到=报错"相反） | 抛 `WeightAuthorityError`（fail-closed） | `test_unreadable_source_fails_closed_not_silently_skipped` |
| — | 真仓自证：新口径下 wild=0、`clean=True`、`conflicts==[]`（出厂面未被放宽） | `test_real_repo_census_still_clean_after_wild_rule` ＋既有 `test_repo_census_reports_single_effective_path` |

扫描口径诚实披露：`census["wild_scan_dirs"]=["src","scripts"]`（写进结论，不装作全仓无死角）；
野生面用严判据是刻意的（宽判据 `_WRITE_PATTERNS` 用在未登记文件上＝满屏局部变量噪音→告警疲劳→被拔线）。
内收自证：`discover_weight_writers` 改为复用同一扫描器（未复制第二份循环），输出键面逐字不变。

## 三、ai_secret_exposure（秘钥面机检）

| # | 修前契约说谎 | 修后 | 拦住它的测 |
|---|---|---|---|
| 1 | 头注承诺"册内无任何 `ai_exposure` 标注 ⇒ 抛 `AiExposureError`"，**分支根本不存在**（现网真册 106 条 0 条标注即此形态） | 契约与实现对齐：不虚构抛错；改为 `machine_check_state=outlet_only_field_unused`＋`widened=False`＋`as_dict()["outlet_not_guard"]=True`＋**logger.warning"插座未接线，非护栏"**；CLI 打 `[OUTLET]` 行 | `test_field_unused_is_reported_as_outlet_not_guard`／`test_real_registry_today_creates_no_ledger` |
| 2 | 撤掉 YAML 标注＝静默把禁读名单缩回基线（实测 4→3 条），零拒绝零留痕＝违反本件自设"只扩不缩"硬不变量 | 真不变量落地：append-only 台账 `.runtime/gate_audit/obj_s_ai_exposure_forbidden.jsonl`（同族先例＝`session_env_guard.DEFAULT_AUDIT_PATH`）；名单变窄→**抛 `AiExposureError`**，除非显式给 `allow_shrinkage_reason`（理由＋差集一并落台账＝显式留痕）；台账写不进=名单不可信=同样抛错；关闸须自报 `ratchet_state=not_checked` 并出声 | `test_shrinking_forbidden_list_is_rejected`／`test_shrinkage_needs_explicit_reason_and_leaves_trace`／`test_ledger_off_is_self_reported_not_silently_enforced` |
| 3 | `secrets: []`／条目全标量→"无人被禁"不报错 | 缺章／空表／条目全非映射／非法编码＝一律抛 `AiExposureError` | `test_empty_table_raises_instead_of_no_one_banned`／`test_all_scalar_entries_raise`／`test_missing_section_still_raises`／`test_illegal_bytes_raise_declared_error` |
| 4 | 两读端打架：筛查面把键名当 fnmatch 模式（`QMT_R**_*` 会拦）、`assert_key_not_forbidden` 用精确集合（同一盖章一处拒一处放） | 共用唯一 matcher `key_matches_forbidden`（fnmatch，与 S1 基线同形状）；`combined_deny_patterns_from` 单一并集实现，`as_dict` 不再二次读册（去掉双读） | `test_two_read_sides_share_one_matcher` |

**两件分开表述（红队点名"把插座记成护栏"）**：本件现在能证伪的是"字段真能扩面"（`test_field_widens_the_interception_face`，
标 forbidden 后基线放行的键被拒）与"现网 marked=0 故零行为变化"（`test_real_registry_today_has_no_field_yet`
＋新 `machine_check_state`）——两句各自有测钉，互不冒充。**面 A 结论未改**：`combined_deny_patterns`／
`screen_session_env_with_registry`／`assert_key_not_forbidden` 在 `src/scripts/tools` 仍**零生产调用点**
（本车道禁触在途热件，接线一行属总筹，见 rb2 §一.5 与 94 册 AI-4 批）⇒ 修后状态是"会说谎的插座改成
**诚实的插座＋可证伪的判据面**"，不是"已执法"。

## 四、断言变化账（收紧清单，无一放宽）

| 文件 | 变化 | 性质 |
|---|---|---|
| `tests/zephyr/data/test_cleaning_rules_hosting.py` | 既有 28 例断言零改动；新增 9 例 | 纯增 |
| 同上（本次开发过程中） | 我对 `inspection_ran` 的一条**新**断言先写反（期望降级读数为 True），按件内已写明口径（降级不占节奏闸，须下一班重跑）改正 | 自我纠错，非放宽他人断言 |
| `tests/backtest/test_weight_ssot_single_authority.py` | 既有 17 例零改动；新增 6 例 | 纯增 |
| `tests/ai_layer/redline/test_ai_secret_exposure.py` | 既有 7 例断言零改动；新增 10 例；加 autouse `_ledger_in_tmp` 把台账指 tmp_path（测试禁写生产 `.runtime`） | 纯增＋隔离 |

## 五、盘面与副作用自证

- 只写自家 6 个路径（3 源＋3 测）＋本文件；未触碰禁触清单
  （`shared/vocab/**`、`state_vocab_registry_gate.py`、`confirm_gate.py`、`OrderFileStore`、
  `price_cage.py` 与两 broker 腿、`intelligence/comparator/**`、`config/flags.yaml`、`catalogs/**`）。
- `config/cleaning_rules.yaml` **未改**（四态与台账不需要新键；键集仍由 dataclass 派生）。
- 测试全走 tmp_path，零生产 `data/` 写、零 CH 连接（假执行器注入）、零 DDL/DELETE。
- 生产台账 `.runtime/gate_audit/obj_s_ai_exposure_forbidden.jsonl` **未被创建**（现网零标注→
  `no_stamps_yet`→不写；CLI 手跑后复核为无）。
- 项目根零临时文件；产物落 `docs/_working/fullflow_mining/05_missing_p0/`。

## 六、待登项（交总筹单点，本车道未自登）

1. creation_token 补齐＋翻译册登记：本文件 1 个新 md（token=`w6h-honest-status-wave2-20260926`）；
   无新建 .py（6 个文件均为改）。
2. depgraph：无新模块/新产物路径；`cleaning_rules_hosting.py` 的 `[CONSUMERS]` 行需加"结论尚未进排班判定"
   一句（本车道已在代码注释与 `ENFORCEMENT_NOTE` 里写清，改不改册由总筹定）。
3. 排班册描述（rb2 清单 B4）：`config/schedule.yaml` 的 `data_supply_sentinel` 描述补"托管第二段=cleaning_rules
   ＋四态读数（not_run/degraded_partial 均报红）＋停用台账文件"。
4. 接线一行（本车道未做，production 流转）：`scheduler.py:250` 是否并入 `cleaning_gate.ok`；
   若决定"只出不并"，须同批改 §一 的钉测口径并在回执里改判为"设计如此"。
5. 秘钥面接线一行（rb2 §一.5/§七.5）：S1 启动器与 secrets 读取面尚无生产调用点，点火批随 94 册 AI-4。
6. 净零声明：本车道未新增 gate/脚本/注册表册；新增文件仅 1 个 .md（本记录），无平行判据面。

## 七、复核命令（可粘）

```powershell
# 前置：cwd 在 worktree，且自证 zephyr.__file__ 落本 worktree（防主区包假绿）
cd D:\ZephyrAlpha\.worktrees\st-ailayer-final-20260924
$env:PYTHONPATH = "$PWD\src"
python -c "import zephyr; print(zephyr.__file__)"     # 期望 …\.worktrees\st-ailayer-final-20260924\src\…
python -m pytest tests/zephyr/data/test_cleaning_rules_hosting.py tests/backtest/test_weight_ssot_single_authority.py tests/ai_layer/redline/test_ai_secret_exposure.py -p no:cacheprovider -c py.ini -q --timeout=300
python -m ruff check src/zephyr/data/cleaning_rules_hosting.py src/zephyr/ai_layer/redline/ai_secret_exposure.py scripts/backtest/weight_ssot.py
python -m zephyr.ai_layer.redline.ai_secret_exposure report   # 期望 machine_check_state=outlet_only_field_unused、[OUTLET] 行、生产台账仍不存在
```

实测读数（2026-09-26 04:1x，本车道收口前；真册现读 total=106 / marked=0 / state=outlet_only_field_unused）：
37＋23＋17=77 例全绿；ruff "All checks passed"；
`tests/zephyr/data`、`tests/backtest`、`tests/ai_layer/redline` 三目录合跑另有 10 失败＋9 错，
**全部属他道在途面**（akshare 取数腿、`tasks.yaml` task_id 重复 271≠270、kronos pkl、策略生产地图引用、
screen 归档存在性）——六支文件均不 import 本车道三件（`grep -l weight_ssot|cleaning_rules_hosting|ai_secret_exposure` 为空）。

## 八、三态结论

- **完工**：三件的"ok=True 说谎面"全部改成诚实四态读数并各配红测（本车道判据数值/阈值零改动）。
- **待挖（非本车道能闭）**：① cleaning 结论进排班判定＝**半接线如实登记**（宿主文件属在途热件）；
  ② 秘钥面三入口仍零生产调用点＝诚实插座，点火批随 94 册 AI-4。
- **待裁（Owner 门位，本车道未自裁、未署名）**：无新增待裁案；§六 第 4 项"是否让本腿 ok 参与排班判定"
  属 production 流转，需 Owner 或总筹在窗口内定，已按"可逆登记＋未改动"三段式处理。
