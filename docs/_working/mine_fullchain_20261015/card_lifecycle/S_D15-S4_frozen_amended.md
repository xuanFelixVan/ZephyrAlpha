---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s4
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S4 冻结带附录 frozen-amended"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S4 行）
---

# D15-S4 冻结带附录 frozen_amended（卡生命周期十三态之四）

## 1. 定义

- 语义（词表 value=frozen_amended）：只增不改，勘误与修订以带日期附录追加，frozen 参数零改动。
- 状态机属性：非终态；credential_required=true；machine_readable=no（`config/strategy_card_lifecycle_map.yaml#D15-S4` build_status=partial）。
- 禁边挂钩：D15-X08 S4→S4 无日期附录 / 附录里改 frozen 值（checker=CV-07，机验=附录缺 `YYYY-MM-DD` 前缀即红）。
- 同构先例：run 档案 errata"只增不改"（`docs/01_policies_and_standards/sop/backtest_system_sop/sop_d_run_archive_naming.md:28`）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M05 S3→S4（人，credential=带日期附录+同批入册，frozen 参数零改动，✅ ≥5 卡实测）；M10 S7→S4 一次性重判（**裁定必备**+全局唯一令牌 `rejudge_used=true`+只许改裁定明示项，✅ 全仓唯一活体） | `config/strategy_card_lifecycle_map.yaml#D15-M05/#D15-M10`；`docs/_working/archive/2026-09/bizmine_night/t0_regime/t0_prereg_funding_carry.md` §6 勘误+§7 修订附录（"其余 frozen 参数零改动"）；`docs/_working/archive/2026-09/bizmine_night/crypto_probe/funding_carry_rejudge.md`（frontmatter ruling: 裁定#363，§1"授权与唯一 diff"） |
| 输出面 | M06 S4→S5（重判后复测的进测口，T0-PRERG-02 走过两次）；M11 S6\|S7\|S8→S10 封卡；**禁回 S1**（就地复活非法） | `config/strategy_card_lifecycle_map.yaml#D15-M06/#D15-M11`；card_ledger CARD-T0-PRERG-02 credential seq1-7（frozen→frozen_amended→executing→red→frozen_amended→executing→red→sealed，rejudge_used=true 令牌消耗点 seq4） |
| SSOT 真源 | 本态无常驻实例（instances_observed=0），只存在于迁移流水中；真源=宿主册 credential 流水 + 卡面附录文本 | `config/strategy_card_lifecycle_map.yaml#D15-S4`（instances_by_card: []）；`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（CARD-T0-PRERG-02 credential 7 步流水）；`docs/_working/archive/2026-09/bizmine_night/algo_mining/tick_t0_prereg_card.md`（status 头逐字"修订=带日期附录，禁静默改卡"） |
| 代码模块 | 无专模块；形态同构件=`src/zephyr/backtest/run_archive.py`（_STEP_FILES 含 verdict/errata，`src/zephyr/backtest/run_archive.py:53-61`）；判据模板=`factor_mining_sop_policy.md:105-126` | 上述两件实存 |
| 门禁约束 | X08（CV-07 日期前缀机验规格）+ X02 联动（附录改 frozen 值=第二处红）；M10 凭证=裁定#363（`ruling_registry.yaml` ruling_id: 裁定#363 条目，含 approved_paths/affected_files） | `config/strategy_card_lifecycle_map.yaml#D15-X08`；`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（裁定#363） |
| 自动化触发 | 零自动化：附录=人写；rejudge_used 令牌消耗靠人记（宿主册字段），无"令牌已耗再判 M10 即拦"的机械闸 | `docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（rejudge_used 字段，CARD-T0-PRERG-02=true 其余全 false） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | M05/M10 判据与活体俱在，但全仓仅 1 张卡真走过（T0-PRERG-02）；其余 4-5 张"附录承载修订"未在登记面留 credential 行 |
| 输出面 | pass | S4→S5 与 S4→S10 两口都有完整实证（案例 A 八步全链复原在骨架 §5） |
| SSOT 真源 | pass | credential 流水 7 步与卡面 §6/§7 附录逐条对得上（骨架案例 A 复核） |
| 代码模块 | warn | errata 同构件在（run_archive），但卡面附录无指纹工具挂接（附录新增内容不改变 frozen 段 sha 的判定逻辑未实现） |
| 门禁约束 | warn | X08 有机验规格、无 commit 接线；本态未见在册活违规（校验器 ERROR 不落本态） |
| 自动化触发 | fail | 一次性重判令牌（rejudge_used）是全图唯一的"全局唯一消耗型令牌"，但其消耗判定纯靠人记——第二次 M10 无机械拦截 |

## 4. 缺口与建议

1. 缺口（本态最硬）：M10 令牌无机械互斥。建议校验器加一条：credential 流水内 from=red,to=frozen_amended 的行数 ≥2 即红（纯结构判，零新依赖）。
2. 缺口：S4 无常驻实例导致"当前处于 S4 的卡"不可查询（machine_readable=no）。建议最低限度在宿主册把途经 S4 且未离场的卡 card_state 标 frozen_amended（T0-PRERG-02 已封卡不受影响；未来重判卡即时标）。
3. 建议：附录日期前缀机验（CV-07 规格已有）可在 --live 腿一次实现：扫卡内 `## YYYY-MM-DD` 前缀标题缺失即红，成本一个正则。
