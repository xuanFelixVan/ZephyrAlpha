---
asset_id: "DOC:docs/_working/night_sweep/fig14_fig15_spec.md"
ttl: "task_bound"
title: "夜战 SW13·图14/图15 图本体与卡状态词表 最终规格卡（收编落地版）"
session: st-nightsweep-sw13-20260929
completes_when: "两图本体+词表落 HEAD 且红蓝 18/18 过即归档（规格面），债务段移交战役整合车道"
---

# 图14 construction_workflow / 图15 strategy_card_lifecycle 最终规格卡

> **产线说明**：本卡是 SW13 车道的挖矿结论与落地规格。两图本体与词表**非本车道新造**——
> 六图战役（st-mapbuild-20260924）已产出终版成品但从未入库（其 worktree 内 untracked 孤儿件，
> 会话已亡、无活跃 claim、无在队袋）。SW13 按"先挖后干+内收"收编该成品落地 HEAD，
> sha16 与提案件 `execution_record.idempotency` 锚定值逐字核对（见 §3）。

## 0. 避让边界（实测裁定，2026-09-29）

| 面 | 归属 | SW13 处置 |
|---|---|---|
| 两图本体 yaml + card_state_vocabulary.yaml | SW13（chief7 两袋均不含，git log --all 全分支无 commit） | **本批落地** |
| validate_strategy_card_lifecycle_map.py | chief7 袋 q-…-0329（blob a3115a818e8a2f10，已预放主区盘面未提交） | 禁碰，只读复用 |
| validate_construction_steps.py + test_construction_workflow_map_adversarial.py | chief7 袋 q-…-0329 | 禁碰 |
| test_strategy_card_lifecycle_map_adversarial.py + fig14_construction/00、01 簿 | chief7 袋 q-…-0369 | 禁碰 |
| 生成器五件 / gate 三件 / alignment_checklist / construction policy 锚块 / ruling #414、#415（战役编号） | st-mapbuild 战役整合批（272 件，未落地） | 禁碰，登记待整合 |
| experiment_registry.yaml 2.2 迁移（+56 CARD 条目） | L-HOST15 已按总包裁定执行（提案件 §10 留痕），主区仍是 2.1/11 条 | **SW13 作为 fig15 一致性依赖代落地**（基线 blob 132f7b33 与本批相同=纯增量重放） |
| st-s52-dispatch2 / st-secbatch-dispatch2 | 无在队袋（pending 目录实测零命中） | 无撞车 |

## 1. 图14 construction_workflow_map.yaml

- **落点**：`config/construction_workflow_map.yaml`（与在库三图 dev_delivery/data_supply_chain/trading_day_cycle 同位同模式）。
- **对象**：AI 施工升级流。29 节点（17 stage + 12 gap，`node_id=D14-*`）× 34 边 × 7 反馈环（`loop_id=B*`）。
- **分层**：8 段——前置/判定/设计登记/施工/验收/文档/文档转正/落地收尾；`by_skeleton_status` ✅6 / 🔨7 / ⬜4，`by_build_status` built6/partial7/pending16，`by_verifiability` automated4/inspection4/manual21。
- **数据源（anchor 面）**：`anchor_source: proposal`，锚块真源=`docs/_working/map_build/fig14_construction/91_step_anchor_block_proposal.yaml`（主区在库）；派生自 `docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md`。`pending_anchors` 诚实开账 17 条（D14-01..D14-17 政策锚块未落，属战役整合批债务，图内显性申报不隐身）。
- **挂接关系**：
  - depgraph/TDM 轴=对齐键 `step_id(D14-*)`（instance_key_space 与 D14 轴、TDM node_id(TDM-*)、BM-* 轴显式不相交）；节点 `module_id` 已挂 10 个在册模块（MOD-INF-005/037、MOD-GATE_ENGINE、MOD-GOV-ALIGN-ALL 等），19 个 null（gap 类为主，`red_reason` 逐节点声明）；
  - alignment_checklist §3 图14 行 + align_all 新节=战役整合批件，本批不落（图内 `machine_facts`/`counts` 已含对账所需全部实数）。

## 2. 图15 strategy_card_lifecycle_map.yaml + card_state_vocabulary.yaml

- **落点**：`config/strategy_card_lifecycle_map.yaml` + `docs/01_policies_and_standards/_registry/vocabularies/card_state_vocabulary.yaml`。
- **对象**：策略卡生命周期状态机——三类对象非 DAG：13 状态（D15-S1..S13，一一映射词表 13 值）+ 17 合法迁移（D15-M01..M17，`edge_kind: permitted`）+ **13 禁止边**（D15-X01..X13，`edge_kind: forbidden`，本图一半价值）；另有 6 gap、4 终态（S10 封卡/S11 判死/S12 毕业/S13 作废）。
- **词表**：REG-CARDSTATE-VOCAB-001，13 值闭集（draft/candidate/frozen/frozen_amended/executing/green/red/insufficient/suspended/sealed/condemned/graduated/void），host=REG-EXP-001；green/red/insufficient 直译在册 `viability_verdict` 三值=零新枚举。ROOR 行已同步（tier_2，owned_by governance）。
- **数据源（anchor 面）**：`registry_host: experiment_registry`（REG-EXP-001，schema 2.2，CARD-* 契约条目 56 条=card_ledger），`anchor_source: registry`，`anchor_block_origin: card_state_vocabulary.yaml`（词表装载点），`caliber_source: fig15_cardlife/91_registry_host_proposal.yaml`（语料口径/别名规则/分裂面继续由提案件供给，禁双源回读状态面）。
- **实例台账口径**：语料 89 卡（headed60/headless29/23 种自由串）→ 在册 56（seeds10+batch46）+ 判死不入册三形分列（headless29 / needs_adjudication2 / non_domain2），`pending_registration.state_undeclared_headless` 逐条列名。
- **挂接关系**：
  - 对齐键=`state_id(D15-S*) + card_id`；`instance_key_space.disjoint_with` 与 TDM node_id(TDM-*)、BM-*、D14-*、MOD-*、DS-*、CAND-* 轴全部显式不相交；
  - revival_authorizations=[裁定#331, #399, #404]（在册裁定号，复活判据 CV-06 触发输入）；known_misref_rulings=[裁定#304] 留总包勘误；
  - depgraph/module_translation：三代码件（validator/generator/gate）设计态登记=战役整合批件；图内 module_id 取 null+`red_reason: pending_registration` 诚实申报，在册后生成器换挂。

## 3. 收编哈希锚（落地即验，禁漂移）

| 件 | sha256[0:16] | 锚定出处 |
|---|---|---|
| config/construction_workflow_map.yaml | `254732370135ad20` | 本批实测（2221 行） |
| config/strategy_card_lifecycle_map.yaml | `3297a22f83934c81` | 91 提案件 §10 `execution_record.idempotency.sha16` 逐字一致（3 runs same_sha256） |
| docs/.../card_state_vocabulary.yaml | `288ef273321f89df` | 本批实测（131 行） |
| docs/.../catalogs/experiment_registry.yaml | 迁移批整拷 | 基线 blob 132f7b33 相同=纯增量（2.1→2.2，-3 行=版本三键，+1565 行=56 CARD 条目+字段声明） |
| docs/registry_of_registries.yaml | 增量重放 | +REG-CARDSTATE-VOCAB-001 行、REG-EXP-001 entry_count 11→67、summary 由 check_registry_consistency.py --refresh-summary 机生（total 80=12/33/35，active70，broken0） |

## 4. 判据与红蓝面（SW13 自带，独立于 chief7 对抗测试）

- **测试落点**：`tests/governance/d5_architecture/test_fig14_fig15_map_bodies_adversarial.py`（路径与 chief7 在飞两测错开；tests/ 豁免 CREATE-GUARD）。
- **判据**：结构自含（不依赖 chief7 validator/generator）——节点/状态引用完整性（悬空必红）、边端点封闭（孤立必红）、counts 与实数一致（伪造必红）、词表闭集（图15 状态值越出 card_state_vocabulary 必红）、终态单调（就地复活边必红）、罗宾 innocent（好图必须全绿）。
- **红蓝四向量**：杀节点 / 断边 / 伪造计数 / 坏枚举，mutant 全部构造于 tmp_path 副本，不碰生产路径。

## 5. 债务与移交（不隐身）

1. chief7 两袋落地后其对抗测试（≥14 类红案+绿组控制组）将接管深度校验；其 `_GOOD` 控制组读 `config/construction_workflow_map.yaml`——本批落地即解除其控制组缺图状态。
2. 战役整合批（272 件）含 alignment_checklist 图14/15 行、construction policy 17 锚块、三 gate、五生成器、ruling #414/#415（战役编号，与主区已占用 #414/#415 撞号待重编）——待其会话整合，SW13 不代落。
3. fig15 两条判据口径待总包裁（CV-10 第四腿终态绑法 / CV-08C 族成员轴 FPOOL/MIDVAL 两族）——91 提案件 §10 已留痕，SW13 未动阈值。
