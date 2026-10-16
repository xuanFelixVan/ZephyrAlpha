---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s13
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S13 作废 void（终态）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S13 行）
---

# D15-S13 作废 void（卡生命周期十三态之十三，终态）

## 1. 定义

- 语义（词表 value=void）：终态，挪门柱或中途加条目或 N_eff 破，本批结论作废。
- 状态机属性：terminal=true；credential_required=true；machine_readable=no；`config/strategy_card_lifecycle_map.yaml#D15-S13`（build_status=partial）。
- 判据真源：`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md:28`（"事后挪门柱=本批作废"）、`:29`（"中途加条目=重开预注册"）；23 张卡头自述"改动即作废重开"。
- 现状：全图唯一"判据要求存在、实践中零登记"的态（红条目 F-04）；唯一近似记录=代码注释（卡的状态记在脚本注释里）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M16 S1..S9→S13（actor=human，credential=挪门柱/加条目/N_eff 破/卡被改的事实认定，skeleton=❌ **零登记**，九态全域入口、全图扇入最宽的边） | `config/strategy_card_lifecycle_map.yaml#D15-M16`；`exam_policy.md:28-29`；近实录=`scripts/audit/t0_gpu_condition_pack.py:1`（"V2 已作废，其 §2.2 六段接线由 V3 §2 逐字继承"——V2/V3 谱系只存在于代码注释；本批核验该脚本 BLUEPRINT 锚已更新指向 `docs/04_research_records/data/t0_matrix/t0_conditional_v2_prereg_card.md`，锚卡在盘） |
| 输出面 | M17 S13→新卡 S1（重开=新预注册，非改旧卡）；无其他出口 | `config/strategy_card_lifecycle_map.yaml#D15-M17` |
| SSOT 真源 | 三面皆无实例：语料 30 种 status 串中无作废词元（by_token 实测：active 4/None 42/候选 1/frozen 58/已封卡 SEALED 1/draft_pending_owner 2/LOCK-PENDING 1/draft 2/"sample_cards_ready" 1）；宿主册无 void 行；唯一作废叙事在脚本注释 | `config/strategy_card_lifecycle_map.yaml#corpus.by_token`（本批实读 9 词元）；`scripts/audit/t0_gpu_condition_pack.py:1` |
| 代码模块 | 零实现：作废事实认定器、门柱漂移检测（考窗/阈值/桶边界改了即应触发 M16）均无；最近邻=X02 的 sha 指纹（同一工具链可反向用作"卡被改"探测器，`src/zephyr/backtest/run_archive.py:44` content_sha256） | `scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py`（CV-17 规格在、卡面 live 腿未接线） |
| 门禁约束 | 本态是三条禁边的执法终点（X02 静默改参→应转 M16/M05；X08 附录改 frozen 值→应转 M16；X09 N_eff 双计→族账应作废重开），但"违规发生→作废登记"最后一公里零机械化 | `config/strategy_card_lifecycle_map.yaml#D15-X02/X08/X09` |
| 自动化触发 | 零。理论触发源全在（sha 指纹/CV-08C 族账/CV-08 双卡），校验器已在 2026-10-15 实跑中产出对应红证（CV-08 ×1+CV-08C ×3），却无一转化为 M16 登记动作——检测在、执法断链 | 校验器实跑输出（本批留档）；`config/strategy_card_lifecycle_map.yaml#gaps.D15-G06`（真源完整性面，red_reason=ghost_ref） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | fail | 判据要求存在的态（V2 作废是已发生事实）零登记；F-04 原文"作废态存在（判据要求）但不可查" |
| 输出面 | warn | M17 语义清楚（重开=新预注册）且与复活三裁定一致；零实例 |
| SSOT 真源 | warn | 图/词表/骨架一致；G01 的 today_zh 散文（89 卡/60 有头/29 无头/23 种串）对 measured（112/70/42/30）已陈旧——本态所在图的缺口散文层有漂移（宪法 §4.4"文档矛盾=事故"边缘案例） |
| 代码模块 | fail | 无任何作废检测/登记代码；判据灭失面（G06）的修复有进展（t0_matrix 22 件 2026-10-09 裁定#496 死信清偿复活，BLUEPRINT 锚卡在盘），但作废登记面无对应进展 |
| 门禁约束 | fail | 三禁边执法终点悬空：校验器能红、无人转 M16；作废的"事实认定"凭证形态未定义 |
| 自动化触发 | fail | 触发源（指纹/族账）已在产出红证，执法断链=最典型的"检测自动化在、处置自动化无" |

## 4. 缺口与建议

1. 缺口（F-04 主文）：作废零登记。最小修法=把校验器现有红证转登记：对 CV-08/CV-08C 命中的族（FPOOL/MIDVAL/T0-PRERG），由 Owner 裁定择一（补登记修正账 vs 判作废重开），任一都让 M16 或修正动作首次落地。
2. 缺口：作废凭证形态未定义。建议照 RULE-RULING 先例：作废必须裁定登记（ruling_id+affected card_id+作废成因枚举 goalpost_moved/entries_added/n_eff_broken/card_tampered 四值），M16 的 credential 字段即有着落。
3. 建议：G01 today_zh 散文与 measured 漂移建议随生成器下轮回写消除（counts 块已有字段，散文删数留字段即可，符合宪法 §4.4 计数用字段纪律）。
