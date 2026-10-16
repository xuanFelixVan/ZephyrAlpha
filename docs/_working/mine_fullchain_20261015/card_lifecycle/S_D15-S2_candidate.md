---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s2
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S2 候选卡 candidate"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S2 行）
---

# D15-S2 候选卡 candidate（卡生命周期十三态之二）

## 1. 定义

- 语义（词表 value=candidate）：机器筛出、未升格，禁出任何 PASS 语义。
- 状态机属性：非终态；credential_exemption=true；machine_readable=partial；`config/strategy_card_lifecycle_map.yaml#D15-S2`。
- 禁边挂钩：D15-X05 S2→S6 候选卡直接出 PASS（凭裁定#366 条件③，checker=CV-07）；唯一升格出口 M04 需 Owner 快签。
- 决策问题：这张卡当前是否处于「候选卡 candidate」？谁有权把它推出去、凭什么凭证？

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M02 ∅→S2（actor=machine，credential=封闭族声明+不得写 PASS，skeleton=✅，production）：有界矩阵/宽筛产出候选卡 | `config/strategy_card_lifecycle_map.yaml#D15-M02`；`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（ruling_id: 裁定#366 条目，map 锚 :4755）；活体= `docs/_working/archive/2026-09/bizmine_night/algo_mining/candidate_card_open_momentum_market.md:9`（status: 候选（…升格=Owner 快签通道）） |
| 输出面 | M04 S2→S3（人/Owner 快签，skeleton=⬜ 无活体——候选卡至今停在 S2）；M16 S2→S13 | `config/strategy_card_lifecycle_map.yaml#D15-M04/#D15-M16`；校验器实测：candidate 卡无迁移流水 |
| SSOT 真源 | 同全图三面：图 YAML（派生）+ 词表（值真源）+ 宿主册（登记真源 registered_state=candidate 恰 1 条） | `config/strategy_card_lifecycle_map.yaml#corpus.by_registered_state`（candidate: 1）；`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（CARD-ALGO-CAND-MOM-01 条目 card_state: candidate） |
| 代码模块 | 矩阵面=网格跑批产物（`data/strategy_intake/grid_*/` 目录族 + `grid_t0_conditional_v1/`）；候选键空间=CAND-*（与卡键 disjoint） | `data/strategy_intake/lane_p0_obi_candidates.csv`（candidate_id: CAND-P0-OBI-001…，birth_channel/birth_batch 列）；`config/strategy_card_lifecycle_map.yaml#instance_key_space.disjoint_with`（candidate_id(CAND-*) 显式判 disjoint） |
| 门禁约束 | X05 禁 S2→S6（checker CV-07 机验规格）；现实执行靠候选卡头自述逐字声明，无 commit 闸 | `config/strategy_card_lifecycle_map.yaml#D15-X05`；`docs/_working/archive/2026-09/bizmine_night/algo_mining/candidate_card_open_momentum_market.md`（卡头"矩阵只产候选卡不出 PASS"） |
| 自动化触发 | M02 actor=machine 有实证（bounded_matrix_wave1_report → candidate 卡）；lane CSV 族（lane_b/c/c2/chain/e/f/g/p0_obi + three_high）是候选供应面，逐行带 birth 通道三元组 | `data/strategy_intake/lane_p0_obi_candidates.csv`；`docs/_working/map_build/fig15_cardlife/00_skeleton.md` §2.1 M02 行 |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | M02 有全仓唯一活体 ALGO-CAND-MOM-01（登记+卡面双在） |
| 输出面 | warn | M04 零活体：候选卡停滞 S2，升格通道从未被走过（skeleton ⬜），出口判据同 M03 但无实例可验 |
| SSOT 真源 | pass | 词表/宿主册/图三面一致（candidate 恰 1 条，无漂移） |
| 代码模块 | pass | 候选供应面实物在盘（lane CSV 9 件 + web_cards 19 件 + grid 目录 60+），birth 通道三元组可追溯 |
| 门禁约束 | warn | X05 只有卡头自述+校验器结构规格（CV-07），无 commit 期强制；STRATEGY-CARD-LIFECYCLE-MAP 门=墓碑（gate_registry 明载"实现从未落位"） |
| 自动化触发 | warn | 机器产候选有实证，但"候选卡立卡即登记宿主册"无自动写路径（登记靠生成器回扫语料，非迁移时点写入） |

## 4. 缺口与建议

1. 缺口：lane CSV 的 CAND-* 候选与图15 候选卡（card 契约层）是两级对象——CAND-* 是 E2/E5 候选因子，升考时才立预注册卡（M02 的"矩阵产候选卡"是 card 级）；两层的升格链路（CAND-* → 立卡）无环节图承载。建议在骨架 §3 缺口清单挂一条"CAND→card 立卡边无图"。
2. 缺口：X05 无实例级机验（无 PASS 语义出现过的活例验证）；建议校验器 CV-07 加一条"candidate 卡文本含 PASS 语义词元即红"的廉价腿。
3. 建议：M04 升格一旦发生，凭证应记 Owner 快签通道（裁定#389 ②），与 M03 同款 credential 结构，复用现有 credential 流水即可。
