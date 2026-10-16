---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s1
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S1 草案 draft"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S1 行）
---

# D15-S1 草案 draft（卡生命周期十三态之一）

## 1. 定义

- 语义（`docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml` value=draft, map_state=D15-S1）：卡已立、判据未写死，可自由改。
- 状态机属性：非终态；`credential_exemption: true`（起草自由，无凭证要求）；`machine_readable: partial`（词元可扫、语义在括号散文里）；`config/strategy_card_lifecycle_map.yaml#D15-S1`（states[0]，terminal=false）。
- 契约真源：`docs/_working/map_build/fig15_cardlife/00_skeleton.md` §1 表行 D15-S1。
- 决策问题（图内原文）：这张卡当前是否处于「草案 draft」？谁有权把它推出去、凭什么凭证？

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M01 ∅→S1（actor=ai，credential=none，skeleton_status=✅，verified_scope=production）：AI/人起草卡，S3 预注册卡段 | `config/strategy_card_lifecycle_map.yaml#D15-M01`；`docs/01_policies_and_standards/sop/mining_sop/factor_mining_sop_policy.md:55-58`；活体= `docs/_working/sector_line/sector_prereg_exam_cards_v0.md`（frontmatter status: draft）、`docs/_working/emotion_line/prereg_exam_cards_v0.md` |
| 输出面 | M03 S1→S3（Owner 批/快签，gated=true，credential_required=owner_sign，observed=SECTOR-PRERG-DECK-01、T0-CONDITIONAL）；M16 S1→S13（作废通道） | `config/strategy_card_lifecycle_map.yaml#D15-M03/#D15-M16`；案例 C= `docs/_working/sector_line/sector_prereg_exam_cards_v0.md` → `sector_prereg_exam_cards_v1_frozen.md`（v0 draft/v1 frozen 两文件同卡号） |
| SSOT 真源 | 图=派生件（禁手改后不回生成）；词表=值唯一真源（13 值动态加载）；宿主册=实例登记真源（registered_state）；语料口径=91 号件档案 | `config/strategy_card_lifecycle_map.yaml`（anchor_source=registry，generated 2026-10-09）；`docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml`（REG-CARDSTATE-VOCAB-001）；`docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml`（REG-EXP-001）；`docs/_working/map_build/fig15_cardlife/91_registry_host_proposal.yaml` |
| 代码模块 | 生成器+校验器（值集 100% 从词表装载，禁硬编码）；无专门"起草"模块（人的编辑面） | `scripts/governance/d5_architecture/generators/generate_strategy_card_lifecycle_map.py`；`scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py`（CV-02 枚举闭集） |
| 门禁约束 | 起草免凭证（credential_exemption=true）是唯一豁免态之一；约束=词表闭集（自造值=CV-02 红）+ 卡语料扫描口径 | `docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml`（credential_required: false）；`scripts/governance/d5_architecture/validators/validate_strategy_card_lifecycle_map.py` CV-02/CV-03 |
| 自动化触发 | M01 起草自由、无门；上游进货面实物：`data/strategy_intake/web_cards/`（19 张 SIC-* intake 卡，intake_stage=C1 盘点归一，未实现禁引用为已证信号）——SIC-* 键空间不在图 instance_key_space（属 draft 之前的进货层） | `data/strategy_intake/web_cards/20261015_p04_ofi_l1.yaml`（card_id: SIC-20261015-P04-01）；`config/strategy_card_lifecycle_map.yaml#instance_key_space`（card_id 空间= T0-PRERG-*/P3-E1C-*/P3-B-*/ALGO-*，disjoint_with 候选/策略等键） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | M01 有活体（sector/emotion v0 卡在盘，status: draft 可扫）；语料 by_state draft=4、登记面 draft=3（`config/strategy_card_lifecycle_map.yaml#corpus`） |
| 输出面 | pass | M03 observed_in_registered_ledger=2 条（SECTOR-PRERG-DECK-01、T0-CONDITIONAL，后者带裁定#399 凭证 seq1 draft→frozen） |
| SSOT 真源 | pass | 词表/宿主册/骨架三面齐备且校验器结构面全绿（CV-01..CV-13 结构项无违规） |
| 代码模块 | pass | 生成器+校验器实存实跑（本挖矿批 2026-10-15 实跑校验器成功） |
| 门禁约束 | pass | draft 是免凭证态，无禁边从 S1 出发指向执行面（X06 拦 S1→S5 在校验器 CV-04 有规格） |
| 自动化触发 | warn | SIC-* 进货卡（19 张）与 lane 筛选 CSV 均在卡键空间之外，进货→draft 的立卡动作全人工；无"立卡即登记"的自动写路径 |

## 4. 缺口与建议

1. 缺口：语料 by_state draft=4 对 registered draft=3，差 1 条未登记（图内 instances_by_card 只列 EXIT-FAMILY-12NODES、T0-MATERIAL-DRAFT 两名）；建议生成器下一轮回填时核对差值。
2. 缺口：web_cards 19 张 SIC-* 与 lane_p0_obi_candidates.csv 的 CAND-* 都不进卡键空间，图对"进货层→draft"的入口无环节表达（骨架 §3 缺口 13 同族）。建议在图 boundary 增一行"intake 层（SIC-*/CAND-*）不属于本图对象"，防后续误挂。
3. 建议：M03 快签通道（裁定#389 ②）走卡面 frozen+批文的既定形态，draft 面无需新闸；保持现状即可。
