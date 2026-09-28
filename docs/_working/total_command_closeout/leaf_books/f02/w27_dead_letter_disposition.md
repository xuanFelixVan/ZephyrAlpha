---
ttl: task_bound
---

# 叶簿 W-27 · 死信终局处置（内容驱动四态：复活/废弃/回队/代投）

> 族 2（提交链解锁与治本）· 骨架行锚=`00_master_skeleton.md` L71（态 🌑部分，出处「提交链终局令§三」，案卷 A）
> 编译：2026-09-28，会话 st-zcloseout-20260928（Agent-H），lane HEAD=`325b69a193`。
> 状态标记：🌑 Owner 门位（骨架册 §六 硬约束③：死信袋只做「捞回未落地字节」，不做归档/废弃工程；「废弃」态须 Owner）。
> 素材真源：`dossier_A_commit_chain.md` §1 条 1a-2c、§2 附表、§3 附引；`wave1b/dead_letter_census.yaml`；`wave1b/dead_letter_prescription_matrix.md`。

## 1. 六向台账（对象=`.runtime/commit_queue/dead/` 的处置面）

| 向 | 内容 | 锚 |
|---|---|---|
| 上游供数 | 落地失败即入 dead/：门禁阻断（GATE-PRECOMMIT-RUN/CREATE-GUARD/TRANSLATION-COVERAGE…）、注册表三向合并失败、LandingEnvironmentError、NOTHING_TO_COMMIT 快照不符等 | dossier_A §2 附表 top20 签名 |
| 下游消费 | `commit_queue.py requeue <qid>`（读 dead_reason 修正后重投）；处方矩阵按簇给四态建议 | `wave1b/dead_letter_prescription_matrix.md` §1（生成器=scripts/governance/wave1b/dead_letter_prescriptions.py，重跑即覆盖） |
| 名册声明 | census 分母=dead/ 顶层 *.json；归档子目录单列披露（ls 会 +1 的坑在册） | `wave1b/dead_letter_census.yaml` `_meta.denominator_note`/`dir_counts.ls_dead_wc_l_pitfall` |
| 读声明的代码 | status 与盘上顶层计数互证通道在册（`cross_check.status_dead_equals_dir_dead_top: true`） | 同上 `_meta.cross_check` |
| 覆盖测试 | 在册处方覆盖 18 簇（11 册 §R-3），本包新拟 45 簇/352 封；引用工具路径审计 20 条缺失 0 | `wave1b/dead_letter_prescription_matrix.md` 头部 |
| 执法门禁 | 入队可拦簇已标 `enqueue_preventable`（如 CREATE-GUARD 68 封/TRANSLATION-COVERAGE 55 封=是；GATE-PRECOMMIT-RUN 85 封/三向合并 72 封=否） | 同上 §1 表「入队可拦」列（assumed：按预检面判断，未实测真跑成功率） |

## 2. 现状实测（三代读数并列，取数时刻在锚）

| # | 断言 | 基线 | 本会话复读（2026-09-28） |
|---|---|---|---|
| M1 | 死信规模 | 700 封（status 口径）/ 顶层 701 含 1 归档子目录 / 递归 714 json——「701 封」系 ls 计数坑 | dossier_A §1-1a/1b/1d + census `_meta`；**本会话现读=982 封顶层 json + 1 归档子目录**（`ls /d/ZephyrAlpha/.runtime/commit_queue/dead/*.json \| wc -l`=982；status 四态 pending=10/processing=4/done=776/dead=982，queue-root=主区） |
| M2 | 簇分布 | 110 个 distinct 首签簇，top5：GATE-PRECOMMIT-RUN 85 / 注册表三向合并 71 / CREATE-GUARD 48 / TRANSLATION-COVERAGE 47 / LandingEnvironmentError 36；top20 覆盖 483 袋（69%） | dossier_A §1-2a/§2 |
| M3 | 指名身份键 | 「三向合并+CAND-GOVTEST-005」全文匹配=7 封（首 60 字符签名截断致 0 命中的口径坑在册） | dossier_A §1-2b/§3（candidate_module_registry 合计 7 袋，3 袋键可读） |
| M4 | 会话分布 | top：st-cmd-20260924 115、st-commitspeed-tbl-20260924 88、st-mapbuild-20260924 33… | dossier_A §1-2c |
| M5 | 处方矩阵现读 | 矩阵生成时现读 730 封/63 处方簇（census 分身口径 84 簇全部映射） | `wave1b/dead_letter_prescription_matrix.md` 头部——本会话未重跑矩阵（IO 纪律），982-730 的增量归簇留给施工班重跑生成器 |
| M6 | 处置是否已做 | — | **未做且持续恶化**：700→730→982 单调增长（M1/M5 三读数），处置通道未消费 |

## 3. 缺口与根因（转述）

- 增量未断：dead 增长未停（M6），先处置存量、后断增量，否则处置完即过期；入队可拦簇（§1 执法向）应先接预检（矩阵已标）。
- 口径三坑在册：①ls+1 归档子目录（census `_meta`）；②首 60 字符签名截断（M3）；③「700 vs 701 vs 递归 714」三数并存（M1）——施工班引用任何数须带取数时刻与口径（X-55 在册要求，census `_meta.denominator_note` 同旨）。
- 单会话独占簇：NOTHING_TO_COMMIT 29 封 100% 出自 st-stress-20260923，指向 `docs/_working/registry_migration/stress/`（dossier_A §6 第 3 条）——四态处置时该簇宜整簇同态。

## 4. 施工项（带锚）

1. 重跑处方矩阵到现值：`python scripts/governance/wave1b/dead_letter_prescriptions.py --dead-dir D:/ZephyrAlpha/.runtime/commit_queue/dead --out-dir <lane 波1b 输出>`（矩阵头 evidence_ref.cmd 原文），把 982 封重归簇。
2. 按簇四态分流呈裁：「复活/回队」AI 可动（requeue 通道在）；「废弃/代投」=Owner 门位（骨架册硬约束③禁 AI 自裁归档/废弃）。
3. 入队可拦簇接 enqueue 预检（矩阵「入队可拦」列=是 的簇），断增量。
4. 与 W-20 解耦：本项只处置袋，不动 candidate 册撞号（W-20/W-71 别混袋，`three_piece_infra/mining/family02_commit_chain_detox/W-20.md` §6 禁止条在册）。

## 5. 复验命令（可重跑）

```bash
# 中心命题复验：死信规模与处置态（数字随时间漂，引用必带取数时刻）
ls /d/ZephyrAlpha/.runtime/commit_queue/dead/*.json | wc -l   # 本会话 2026-09-28 读数=982
python scripts/commit_queue.py --queue-root "D:\ZephyrAlpha\.runtime\commit_queue" status | python -c "import json,sys; print(json.load(sys.stdin)['counts'])"
# 期望：两口径互证；若 dead 不再增长且矩阵重跑后簇数覆盖现值，M6 的「未做且恶化」判定失效须重挖
```

## 6. 自审闸三态

- **挖干**：已干——规模（M1 三口径）、簇分布（M2/M5）、身份键面（M3）、会话面（M4）、处方工具链（§1 下游/覆盖两向）齐锚；982 增量的逐簇归因如实标「未跑，施工项 §4-1」。
- **施工中**：部分——处方矩阵与 census 两件**成品已在册**（wave1b/），但处置动作本身未消费任何簇（M6）。
- **未开工**：四态分流的实际执行（§4-2/3）——证据=dead 持续增长至 982 且「废弃/代投」挂 Owner 门位（🌑）。
