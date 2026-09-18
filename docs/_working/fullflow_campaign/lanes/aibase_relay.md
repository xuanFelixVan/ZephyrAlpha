---
ttl: task_bound
completes_when: 接力车道据本表销完 L2 余项并完成 OBJ_M 主干
---

# 车道 aibase · 接力说明（sid=st-ff-aibase-20260918，2026-09-18 20:1x）

## 0. 一句话
L2 九项里 **C1/C2/C3/C4/C5/C6/C7/C8 全部落地并已入队提交**（q-20260918-st-ff-aibase-20260918-0001，14 文件），
C9 测试 5 文件**只完成 2 个**（conftest + test_dedup），OBJ_M 及后续 9 本**未开工**，只出派工图。

## 1. 已落盘勿回退（逐文件）
| 文件 | 状态 | 本会话做过什么（勿重复/勿回退） |
|---|---|---|
| `scripts/ai_layer/apply_ai_intake_ddl.py` | 在队 | SQL_SEED_DOMAIN 提常量（原函数内 f-string INSERT 触 NO-BARE-SQL）；`--verify` 实测 OK；PG 上 schema 已真部署 |
| `src/zephyr/ai_layer/intake/card_store.py` | 在队 | 9 处 `SQL_X: Final=` → `SQL_X =`（AnnAssign 不被 gate 豁免）；**遗留缺陷**：`IntakeCard` 读模型不暴露 novelty/mechanism |
| `src/zephyr/ai_layer/intake/dedup.py` | 在队 | 5 处同上；**遗留缺陷见 req_aibase_02（k=3 对短卡失效）** |
| `src/zephyr/ai_layer/intake/gate.py` | 在队 | 1 处同上；**新增** `candidate_from_mapping()` + `run_ingest()`（L1 staging→过闸→入库回执） |
| `src/zephyr/ai_layer/intake/events.py` | 在队 | `intake_ingest_due` 原返 `ingest_runner_not_wired`（假通道），已真接 `run_ingest`；`IntakeJournal` 新增 `schema` 参数并透传 CardStore |
| `src/zephyr/ai_layer/intake/kpi.py` | 在队 | 4 处 SQL 常量同上；阈值现可读（THD-INTAKE-001..004 已入 alert_threshold_registry） |
| `scripts/ai_layer/gen_intake_ref_snapshots.py` | 在队 | 已实跑两遍：3595 条真指纹入 T4（chart287/indicator102/algoflow3206） |
| `docs/01.../catalogs/alert_threshold_registry.yaml` | 在队 | +4 条 THD-INTAKE（safe_write_text CAS，entries 38→42） |
| `docs/01.../catalogs/capability_canonical_file_registry.yaml` | 在队 | 9 个 creation_token 批次登记 |
| `docs/01.../catalogs/module_translation_registry.yaml` | 在队 | 9 模块 name-zh + plain-zh 登记（主仓跑，entries=7133） |
| `tests/ai_layer/intake/conftest.py` + `test_dedup.py` | 在队 | 12 passed（含 known-gap 钉） |
| `adjudications/req_aibase_01_init_basename.md` / `req_aibase_02_simhash_k3_short_text.md` | 已 staged 未提交 | 交 Max/Owner |

## 2. C9 余项（3 个文件，内容已定，照抄即可）
- `test_gate.py`：闸机检矩阵（labor 六态/四闸缺键/provenance/单来源封顶 cap_stage=L1/来源不足拒/data_eng quality_gaps/
  license 六态含 lgpl 只标 read_only_limited 不拒/年份六态含 2000 与 3000 边界/`candidate_from_mapping` 忽略未知键/
  超配额拒（在 `test_schema` 插 T5 daily_quota=0）/被拒零副作用 `stage_of() is None`/`run_ingest` 拒缺失与坏 JSON）。
- `test_card_store.py`：状态机 LEGAL 5 边 + ILLEGAL 8 边 + 入 rejected 5 边 + unknown stage + 同态 noop；
  `render/parse_simhash` 回环与越界 ValueError；`CardStore(schema='public')` 拒；
  insert/get/transition 回环 + 跳跃 RuntimeError + 缺卡 RuntimeError；rejected 终态禁复活；
  **record_score 四人同格→rank 1,2,3 active / 4 benched**；主键冲突；`count_today_by_source`/`list_by_stage`。
- `test_events.py`：7 kind 常量等值；emit 先落盘（读 JOURNAL_NAME 文本）；未知 kind/缺必填键/错挂 handler 三拒；
  drain 幂等（二次 processed==[] 且 handler 只被调一次）；毒丸 MAX_ATTEMPTS=3 后 `status()['poison']` 含该 id
  且幸存事件仍在 pending，`purge_poison` 返回 True；KillSwitch **不翻转生产闸**，改断言
  `drain()['stop_reason'] == (None if probe_kill_switch()[0] else why)`；ingest 坏 staging 计入 failed 不静默成功。
- `test_kpi.py`：`load_kpi_thresholds()` 生产值==(5.0,30.0,2,4)；**tmp YAML 换值即变**（证非硬编码）；缺条目 fail-closed；
  `evaluate_series` 健康带空/连2周 DEMOTE/连4周 LONGTAIL/>30 TIGHTEN/None 不判；`test_schema` 构造 6 卡（5 rejected+1 L0）
  → V3 视图 cards_total==6 且 rates_by_domain 出数。
- 跑法：`python -m pytest tests/ai_layer/intake/<f> -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning" --basetemp=.runtime/tmp/ff-aibase-pc`

## 3. 变异证据（能红证明，§3.4）
本轮未做全量变异批；**已内建一条自证红的钉**：`test_known_gap_single_edit_escapes_k3` —— 任何人把
`HAMMING_K` 改大或对短文本放宽，该测试即红。补齐 C9 三文件后请对 `check_labor_killed` 长度阈值与
`check_stage_transition` 前进一步判据各做一次变异（改 → 必须红 → 按字节还原）。

## 4. 下一步（按 Owner 序）
OBJ_M 模型线（worklist 未出，先挖后干照 ailayerB 格式落 `lanes/ailayerB_OBJM_worklist.md`）→ OBJ_R S4/S5 → L1 → L4 → L6 → L3 → L5 → L7 → OBJ_T → OBJ_S。
派工图=`lanes/aibase_dispatch_map.md`。

## 5. R-019 复跑结论（供后续车道少走弯路）
- worklist 声称"已登记 `req_ailayerB_02.md` 备查" → **实测不存在**（adjudications/ 仅 tdchainJ×3 + wiresafe×1）。
- worklist 声称 C1-C7 未开工 → **实测 7 个 .py 已在盘（untracked）且 PG schema 已真部署**（含 `ai_intake_test_smoke`/`_smoke2` 两个残留测试 schema 未清）。
- 三项登记（token/翻译/depgraph）实测 **0 命中** → 本车道补做。

## 6. 接力车道 st-ff-ailayer2-20260918 补记（2026-09-18 21:5x，救回件落地批）

### 6.1 本车道实测纠正（R-019 复跑纪律，逐条命令级）
| 上游记载 | 本车道实测 | 处置 |
|---|---|---|
| §1 "conftest + test_dedup 在队，12 passed" | 两件从队列 blob 救回后 **test_dedup 收集期 ImportError**：`from conftest import needs_pg`，而盘上 conftest 已被改写为不含 `needs_pg` 的版本（归 `st-ff-alarm2-20260918` 在办） | 本件自带 `needs_pg`（同判据：PG 不可达=skip 而非假绿），**不 import 在途 conftest**、不 claim、不代修；12 passed 实测复现 |
| §1/§20 "THD-INTAKE-001..004 已入 alert_threshold_registry" | **worktree 存活**（:813-881，mtime 19:47，76 行纯 append，全文件无第五个 threshold_id 混入），但 **HEAD 0 命中** ⇒ kpi.py 的 fail-closed 阈值读在 HEAD 里必崩 | 该 76 行随本批同落（纯 insert 已核）；`load_kpi_thresholds()` 实测返回 (5.0, 30.0, 2, 4) |
| §24 "module_translation_registry 9 模块登记 entries=7133" | 本车道开工实测 **HEAD 与 worktree 均 0 命中**（该册的 aibase 增补被同一轮抹除带走） | 9 件重新登记（entries 7122→7130），TRANSLATION-COVERAGE 前置转绿 |
| §57 "depgraph 0 命中 → 本车道补做" | **depgraph 9 节点已在 DB**（`planned`，node_id 14830705-14830713；架构数据=DB 真源，未被工作区抹除波及） | 无需补做；NEW-FILE-DEPGRAPH / DEPGRAPH-PRE-REGISTRATION 实测已满足 |
| 队列死因（dead_reason 现值） | CREATE-GUARD **CLASS-UNIQUENESS**：`gate.py::IntakeVerdict` 与 HEAD 已存的 `trading/manual_instruction_channel.py::IntakeVerdict` 同名不同义 | 治本改名 `AdmissionVerdict`（全仓 worktree 零同名；非合法 re-export 故不走 `# class-name-alias` 逃生，符 R-002/R-017） |
| §16/§17/§19 "遗留缺陷" | 逐件新 class 名预扫：14 个新类中**只有 IntakeVerdict 一处撞名**，其余 13 个全仓唯一 | 只改这一处，未顺手扩大改动面 |

### 6.2 T2 接电实测结论：**零 src 外部消费者，本车道不接，判 ④向=红**
- 复跑判据命令（本次实跑）：
  `grep -rn "from zephyr.ai_layer|import ai_layer|ai_layer\\.intake" --include=*.py src scripts | grep -v "^src/zephyr/ai_layer/"`
  → 命中**只有 4 行且全在 `scripts/ai_layer/`**（其中 3 行是头注文字），唯一真 import 在 scripts 侧。**src/ 侧外部消费者 = 0。**
- 族内互引（gate↔card_store↔dedup↔events↔kpi）**足以骗过 ORPHAN-MODULE 门**：该门只做 `git grep src/**/*.py`
  文本匹配、且只排除文件自身不排除同族 ⇒ **本族落地时 ORPHAN-MODULE 会绿，绿的是门不是流**。
  这是"门判据弱于验收判据"的一例：验收规范 §1 第④向还要求"追到生产入口或调度任务为止"，本族追不到。
- 三条候选接法**逐条判为不该接**（R-013"接错比不接更糟"）：
  1. **接 `data/scheduler.py` 的 `task_completed` 轻唤醒**（原 [CONSUMERS] 的声明）→
     本包两处硬不变式明文"产线（业务层）代码禁 import 本包"，且 `DESIGN.md:45` 写明
     "任何产线代码禁读 ai_intake（可 grep 的红线，未来挂 gate）"→ 接上去=**当场破自己写的红线**。
  2. **接 L5 排产闸消费体 `intake_e2_handoff`** → `lanes/aibase_dispatch_map.md:29` 明文
     "消费体待建 + tasks.yaml/schedule.yaml 归 z-dag 独占，勿代写"；且 KPI 的 `handle_alert()`
     会 `UPDATE ai_intake_source_quota` **主动改配额**（自己开始动作的闸），按 R-022③ 同例不在车道权限。
  3. **接 `internal_compute_provider` 路由**（手册 §7 对零入度的标准正解）→ 语义错位：
     该 provider 按 `payload.table == "<库.表>"` 路由 **ClickHouse 采集能力**，ai_intake 是 **PG 生食库**，
     接上去就是 R-013 那一型"看起来接了、实际语义错位"的假闭环。
- 处方（谁该接、接哪一处）：
  - **L1 感知段**（`ai_layer_vision/L1_perceive/DESIGN.md`）落"源注册表 v0"后 emit `intake_ingest_due`
    成为①②③向的真上游（dispatch_map:25 已写接缝契约，`run_ingest(staging_path)` 已通）；
  - **周巡检**接 `IntakeKpi` 只读投影（kpi 的 [CONSUMERS] 已声明"周巡检 CLI 后续接线批"），
    只读不触配额写 ⇒ **风险最低的下一步，建议总包优先派这一条**；
  - **L5 排班闸**建成时才接 `intake_e2_handoff`，那才是跨生熟边界的唯一合法出口；
  - 任一接法必须事件触发（宪法 §9.3），禁 cron/Timer/sleep-loop。

### 6.3 仍欠账（本批**不**计入完成）
- **C9 测试 4 件未建**：`test_gate.py` / `test_card_store.py` / `test_events.py` / `test_kpi.py`
  （§2 内容规格已定，照抄即可）。本批已把 5 件头注里的 `[TESTS]/[CONSUMERS]` 假声明改成"在册缺口"注记。
  能红证据只覆盖 dedup 面：μ1 放宽 `HAMMING_K` 3→8→1 failed；μ2 去 NFKC 归一→1 failed；
  μ3 `REF_FAMILIES` 摘 L7→2 failed；μ4 `simhash64` 恒返 0→3 failed；按字节还原后 12 passed。
  **gate/card_store/events/kpi 四件的判据至今没有任何变异证据**（无测试可红）。
- **PG 残留测试 schema `ai_intake_test_smoke` / `ai_intake_test_smoke2` 未清**（登记不执行：
  `apply_ai_intake_ddl.py --drop-test-schema` 属破坏性操作，按 RULE-DATA-OPS 需三步验证，非本批必要项）。
- **`scripts/ai_layer/*` 两件的排班归属未定**：`gen_intake_ref_snapshots.py` 是静态清单生成器（宪法 §9.5
  要求排班驱动而非人工），两件 `[TTL] permanent` + manual 触发走 m11 合法豁免注记，
  真解=进 schedule.yaml/tasks.yaml 档期，载体归 z-dag 独占 ⇒ 本车道不代写。
- **simhash k=3 短文本漏检**：判据缺陷未修，已由 `test_known_gap_single_edit_escapes_k3` 钉住
  （裁定书 `adjudications/req_aibase_02_simhash_k3_short_text.md` 实测仍在盘）。
- **本族六向三态（车道建议，裁定权在总包）**：①黄（PG 9 表+3 视图在库、ref_snapshot 3595 行、card 6 行，
  但 `ai_intake_source_quota` 0 行 ⇒ 配额走上界默认；上游 L1 未建=入口靠人工 staging）②黄（test_dedup 12 passed
  真跑 + `apply_ai_intake_ddl.py --verify` rc=0 + `load_kpi_thresholds()` 出真值；**生产入口 `run_ingest`/`drain`
  从未由真事件触发过**）③绿（落点实测：`ai_intake.ai_intake_card` 6 行 / `ai_intake_ref_snapshot` 3595 行 /
  V1 6 行 / V3 4 行）④**红**（src 外部零消费者，见 §6.2）⑤红（`ai_intake` 全族在
  `src/zephyr/data/config/data_supply_sentinel.yaml` 与 `config/quality_sentinel_tables.yaml` 双册实测 0 命中，
  本车道未代写他道在册册），⑥黄（代码面 fail-closed 写得很硬：
  KillSwitch 探针失败停消费、阈值缺条目抛 `AlertThresholdConfigError`、毒丸 MAX_ATTEMPTS=3 留档，
  但**除 dedup 外无任何变异证据**，故按 R-041"能红是每轮跑出来的事实不是交工宣称"判黄不判绿）。

### 6.4 ★ 第二道闸实测：`events.py` 撞能力册裸词别名 → 改名 `intake_events.py`（附一条门禁缺陷案卷）
- 第一笔入队 `q-20260918-st-ff-ailayer2-20260918-0001` 判 dead，死因**不是**类名（那条本车道已治本），
  而是 CREATE-GUARD 的 **GATE-SSOT L2 basename 碰撞**：
  `src/zephyr/ai_layer/intake/events.py 是 drift_detection_events 的 sibling duplicate（canonical=src/zephyr/gov_drift/events.py）`。
- 机械根因（读判据函数本体定论，非猜）：`CapabilityLookup._derive_canonical_and_duplicates` 按
  `basename ∈ {capability_id} ∪ aliases` 收候选，而能力册里 `drift_detection_events` 的 **aliases 就是裸词 `events`**；
  canonical 由成熟度排序选出（gov_drift=production > 本件=evolving），故本件被降为 duplicate → 硬阻断。
- 车道判定＝"门禁说的是半真问题"：
  - 真的一半：`events.py` 是**通名**，与漂移域事件层确实构成"同名不同义"隐患，与 §6.1 的 `IntakeVerdict` 同型 ⇒ **治本改名**；
  - 缺陷的一半：别名 `events` 是裸词，等于宣布"任何目录下任何叫 events.py 的新文件都是漂移域的重复实现"，
    判据不看语义；且只在新增时触发（bootstrap 豁免）——实测 HEAD 里 basename 恰为 `events.py` 的**只有 1 件**
    （`src/zephyr/gov_drift/events.py`），即该别名当前唯一的杀伤对象就是"以后新写 events.py 的车道"。
- 处置：改名 `src/zephyr/ai_layer/intake/intake_events.py`（件内语义、七个 kind、journal 路径、类名全部不变），
  并补齐该新路径的三件套（token `capability: ai_intake_l2` / 翻译 plain_zh / depgraph node_id=14830723）；
  同步改 5 处引用（`intake/__init__.py` 的 `__all__`、`kpi.py` 的 import 与 [DEPENDENCIES]/[CONSUMERS]、
  `card_store.py` 与 `gate.py` 的 [CONSUMERS]）。本地复跑判据函数 `check_capability_duplicates` → **0 信号**。
- **与 DESIGN 的偏差（如实登记，本车道不代改他段设计真源）**：
  `docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md:218` 与
  `L5_schedule_gate/DESIGN.md:33/47/212` 仍写 `src/zephyr/ai_layer/intake/events.py`。
  改名理由与死信编号已写进件内头注，设计稿的路径更正留给 AI 层愿景线（本车道未越权）。
- ⚠️ **连坐预警（必须传下去）**：`L5_schedule_gate/DESIGN.md:212` 计划新建
  `src/zephyr/ai_layer/scheduling/events.py`，落地时会撞**同一道闸、同一个死因**。
  请 L5 车道直接改叫 `scheduling_events.py`（或总包/Max 先把 `drift_detection_events` 的 alias
  由裸词 `events` 收窄为 `drift_events`——后者是改判据面，不在车道权限，列 Max 复查/裁定）。
- 另登记一条在册问题：9 件头的 `[BLUEPRINT] MOD-INF-037` 经 `apply_depgraph.py` 实测报
  "蓝图文件不存在 `docs/03_modules/MOD-INF-037/blueprint.md`"，而 `docs/03_modules/**` 全员禁写 ⇒
  本车道只能登记不能自修（同 §6.3 的 ALGO_FLOW 欠账同族：声明面不可自修的受限面）。


