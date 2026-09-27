---
ttl: task_bound
completes_when: 波1A/1B/2 建卡入 governance.db.tasks 且 21 字段校验全过；VERIFIED 升态校验器能红（抽验+canary 测试）；一条命令视图样本入册
---

# 波 1A 交付卡案卷（建卡 / VERIFIED 判据 / 交接视图）

- turn_budget: 计划 30，实际用量见文末 §五；超支项=建卡写入面缺口定位与双锚修正（值得）。
- verified（本机实测，命令见 evidence_ref）:
  - Python 3.12.8；车道外主仓库 `D:/ZephyrAlpha/data/databases/governance.db` 的 `tasks` 表实测 **76 列 / 2546 行**（册面称 73 列——差异在册保留，以本实测为准）；`TaskStatus` 实测 **14 态**（PENDING/CREATED/LOCKED/ASSIGNED/READY/IN_PROGRESS/REVIEWING/COMPLETED/**VERIFIED**/FAILED/BLOCKED/WAITING/RETRY/CANCELLED），`COMPLETED`＝自称完成、`VERIFIED`＝独立核验，且全库现 **0 张 VERIFIED**——本包未把任何既有卡改成 VERIFIED。
  - 建卡入口 `TaskRepository.create_and_ready()`（`task_repo.py:1785`，册面点名 `:1290` 为 class 起点，实测相符）；GOV-TASK-001 v3.2.0 实执 **18** 个 `TEMPLATE_REQUIRED_FIELDS`（`task_repo.py:1446`，缺即抛），包要求 21＝18＋本包追加 `session_id / artifact_paths / approval_required`（建卡器 `self_check_21` 强制，且路径字段全为绝对路径）。
  - 建卡 **20 张**全部落库（RUN1 created=20, all_21_pass=True）；幂等复跑 RUN2 created=0/exists_skipped=20；修锚后 RUN3 created=0/synced=13/skipped=7。
  - 20 张 COMPLETED 抽验：**20/20 REJECT、0 张 ELIGIBLE**（判据①空 artifact ×13，判据②锚不在 HEAD ×7，含 `scripts/governance/d7_code/fix_n*` 七件盘面无锚件）⇒ 红证成立。
  - canary 测试 `tests/governance/test_delivery_card_canary.py` **4 passed**（缺锚拒/空锚拒/rb 无证据锚拒/正控放行——校验器既能红也能绿）。
- assumed（引用册面，未独立复算）:
  - 10 册波 1A/1B/2 各包行的内容描述与判据（口径冲突以 02 册为准）；
  - "700 封死信 / 103 名册 / 99 实载"等 1B 包现场读数（属对应包施工时复验，本包只建卡不验现场）。
- input_set_disjoint_with: 本包写入面＝车道内 5 个文件（builder/checker/view/canary 测试/本案卷）＋ governance.db `tasks` 表 **20 张新行**；其中 13 张的 tags 补锚经官方 `TaskRepository.update()`（仅动本会话新建行）；未动既有他话行、未动 `docs/01_policies_and_standards/**`、`config/flags.yaml`，无 git commit / 无 enqueue / 无删除。
- evidence_ref.cmd:
  - `PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src python D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/scripts/governance/wave1a/build_delivery_cards.py`（幂等建卡器；`--check-only` 不落库）
  - `... python D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/scripts/governance/wave1a/verified_promotion_check.py --sample-completed 20`
  - `... python D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/scripts/governance/wave1a/cross_session_view.py --session st-final-build-20260926`
  - `... python -m pytest D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/tests/governance/test_delivery_card_canary.py -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning"`
  - 取数 JSON 快照：车道 `tmp/create1.json / create2.json / create3.json / sample20.json / sample20b.json / view.json`（带取数时刻，属状态快照，真源仍是 tasks 表）。

## §一 建卡（1A.1）：20 张，不是"约 30"

**张数口径**（10 册点名实数，禁照抄册面"约 30"与"122"）：波 1A 六行（1A.1–1A.6）＋ 波 1B 十行（1.1–1.8 含 1.7b/1.7c；**1.9 为"不做"行不建卡**）＋ 波 2 四行（2.1–2.4）＝ **20**。波 0/3–9 不在本包范围（00 册 §一基线＋任务书限定波 1A/1B/2）。

| task_key | task_id | 态（建出） | rb | approval | 说明 |
|---|---|---|---|---|---|
| 1A.1 | OPS-9260101 | READY | – | – | 建卡器本体即交付件 |
| 1A.2 | OPS-9260102 | READY | ✓ | – | 升态校验器＋canary 红证 |
| 1A.3 | OPS-9260103 | READY | – | – | 触发面三列对账表 |
| 1A.4 | OPS-9260104 | READY | – | **True/H** | 规则↔执法面对账；"退役"支属注册表净删→Owner |
| 1A.5 | OPS-9260105 | READY | – | **True/H** | 死库清理；退役/改规则库路径→Owner |
| 1A.6 | OPS-9260106 | READY | – | – | 交接视图脚本即交付件 |
| 1B.1.1 | OPS-9260107 | BLOCKED | ✓ | **True/H** | 恢复禁用门属 ⚑-6-3，禁自裁 |
| 1B.1.2 | OPS-9260108 | BLOCKED | ✓ | **True/H** | CAND 双条合并含注册表净删支→Owner |
| 1B.1.3–1.8 | OPS-9260109…116 | BLOCKED | 1.7c/1.8 外均 ✓ | – | 各按 10 册判据行 |
| 2.1–2.4 | OPS-9260117…120 | BLOCKED | ✓ | – | 抢救落地四役 |

- 依赖链已机读化：1B 全部 `depends_on=blocked_by=[6 张 1A 卡]`；2.x 依赖 10 张 1B 卡（波间硬依赖串行不再靠散文叙述）。
- 21 字段核验：建卡器对每卡跑 `self_check_21`（18 模板字段 + session_id/artifact_paths/approval_required + 四个路径字段绝对性），三态输出 PASS×20（`tmp/create1.json`）。
- directive 全部写成 `10册-<section>（总指挥战役 Owner 排产指令）` 文字，**不引用任何 #NNN 裁定号**（未逐号 grep ruling_registry 即不自赋，防悬空号——本役 dead 0040 的前车）。
- **建卡过程挖出的执法洞（登记，不代修）**：`requires_rb_check` 在 Task 模型与表列都存在，但 `SQL_INSERT_TASKS_COUNT` 列面不含它 ⇒ 官方建卡 API 写不进（实测 20 卡该列全 0）；`approval_required` 正常入库（OPS-9260107=1 实证）。声明面有、写入面无＝"脱钩病"新样本。处方：判据③改双锚（列 OR tags 含 `rb-required`），tags 经官方 `create()`/`update()` 均可达；仓储 INSERT 补列属后续包（禁裸 SQL）。

## §二 VERIFIED 判据（1A.2）：能拒的状态机约束

`verified_promotion_check.py`（只读，绝不 transition）三判据：
① `artifact_paths` 非空；② 逐件 `git -C <主仓根> cat-file -e HEAD:<rel>` 为真（绝对路径转仓内相对，仓外件直接点名）；③ rb 触发者（`requires_rb_check` 列或 `rb-required` tag）须有**已入 HEAD 的红蓝证据锚**——锚约定＝artifact_paths 中至少一件文件名匹配 `(rb|red|红证|红蓝|canary)` 且同样过判据②。

**20 张 COMPLETED 抽验（确定性取样：有 artifact 者优先、task_id 升序）**：20/20 REJECT。
- 7 张 `OPS-2026062103…09`：artifact 为 `scripts/governance/d7_code/fix_n*.py`，**HEAD 无 blob** → 判据②拒（这就是"自称完成无证据"的现行形态）；
- 13 张（CP-025911/050781/056441/060341/073961/098371/1001/1002/109211/110011/122021/127661/128311）：artifact_paths 为空 → 判据①拒。
⇒ "COMPLETED 不算交付"自此有可复算尺；92 册 G-05 散尺并入本判据（净零对价）。全量 1990 张 COMPLETED 中 artifact 非空者仅 **7** 张（实测），其余按判据一律升不动。

**红证 canary**（tests/governance/test_delivery_card_canary.py，tmp_path 临时库 + 官方仓储 API 建卡，不触生产库）4 例全过：缺锚→拒、空锚→拒、rb 无证据锚→拒、有锚无 rb→放行（证明尺既能红也能绿，不是恒拒摆设）。

## §三 交接视图（1A.6）：一条命令

```
PYTHONPATH=D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/src \
python D:/ZephyrAlpha/.aidrafts/st-final-build-20260926/scripts/governance/wave1a/cross_session_view.py \
       --session st-final-build-20260926
```
输出样本（实测 `tmp/view.json` 摘要，取数时刻 2026-09-26 本会话内）：
```json
{ "total": 20,
  "view_by_session": {"st-final-build-20260926": {"READY": 6, "BLOCKED": 14, "_total": 20}},
  "view_by_verification": {"unverified": {"READY": 6, "BLOCKED": 14}},
  "view_blocked_by": [{"task_id": "OPS-9260107",
      "blocked_by": ["OPS-9260101","OPS-9260102","OPS-9260103","OPS-9260104","OPS-9260105","OPS-9260106"], ...}],
  "db": "D:\\ZephyrAlpha\\data\\databases\\governance.db" }
```
三视图＝`--session`（按会话）/ `view_blocked_by`（阻塞链，可加 `--wave 1B` 过滤）/ `view_by_verification`（核验态分布）。

**"散文只承载为什么、不承载状态"纪律的落地位置**：
1. 状态唯一真源＝tasks 表机读列（`status/verification_status/blocked_by/approval_required/artifact_paths`），本节所有数字都由 §头部命令现出，下一班跑同一条命令即得现势，无需归并散文；
2. 本案卷（及后继案卷）凡状态数字必须**带取数时刻**且标注"快照，非真源"（本册已按此执行）；裁定理由/口径改判留在散文（如 §一 张数口径、rb 双锚缘由）；
3. 硬约束写进卡：1A.6 卡（OPS-9260106）的 acceptance 即"下一次多会话合并人工归并工时≤1 小时"。

## §四 净零对价与内收声明

- 本包新增脚本 3（builder/checker/view）＋测试 1＝1A.1/1A.2/1A.6 三包交付物本身；1A 波预算"净增脚本 1"指对账表生成器（`gate_rule_face_reconcile.py`，属 1A.3/1A.4 卡，本包只建卡未实施）。
- 对价：替代 G-05 散尺（升态判据吸收）、替代散文交接书整类工件（视图命令吸收）、复用既有 73→76 列 tasks 表与 14 态枚举——零新库、零新册、零新增门禁台数。

## §五 合规自证与用量

- 无 git commit / 无 enqueue / 无删除动作 / 未动 `docs/01_policies_and_standards/**`、`rules/**`、`config/flags.yaml`；未跑 `test_ops_guard_red_team.py`；未 kill 进程；未改任何阈值/skip/xfail。
- governance.db 写面＝20 张本会话新行（追加）＋其中 13 张 tags 补锚（官方 `update()`，仅本会话新建行，"既有行"零触碰）；测试全部 tmp_path。
- 工具调用实测 ≈37（预算 30 超支主因：requires_rb_check 写入面缺口的根因定位与双锚修正，属必要红→修）。
- 回报口径：建卡 20 张 / 21 字段 20/20 PASS / 20 张抽验 20 张升不了 VERIFIED / 红证 canary 4 passed。
