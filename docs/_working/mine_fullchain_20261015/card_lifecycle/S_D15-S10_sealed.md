---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s10
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S10 封卡 SEALED（终态）"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S10 行）
---

# D15-S10 封卡 SEALED（卡生命周期十三态之十，终态）

## 1. 定义

- 语义（词表 value=sealed）：终态，不再重开、不再改参重跑，证据定版。
- 状态机属性：terminal=true；credential_required=true；machine_readable=no；`config/strategy_card_lifecycle_map.yaml#D15-S10`（build_status=partial）。
- 铁律（laws 第三条）：封卡即终——任何就地复活边一律非法，复活=新 card_id+revives 指针。
- 唯一实例：T0-PRERG-02（funding carry，全链七步 credential 流水+rejudge_used=true 令牌消耗卡）。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M11 S6\|S7\|S8→S10（actor=human，credential_required=ruling，gated=true，RULE-RULING 同 commit 原子，✅ 1 例=funding，裁定#363） | `config/strategy_card_lifecycle_map.yaml#D15-M11`；`ruling_registry.yaml`（裁定#363 条目 :2572 起；裁定#390 条目 :2950 起："funding 封卡效力维持，任何会话禁以 #389 为凭重跑两卡"）；卡面=`docs/_working/archive/2026-09/bizmine_night/t0_regime/t0_prereg_funding_carry.md:9`（`status: 已封卡 SEALED（…裁定#363；修订见 §7，禁静默改）`——骨架实测全仓 1/68） |
| 输出面 | M17 S10→**新卡**S1 跨实例边（新卡必填 revives 指针，旧卡状态不变，✅ 活体链完整：funding SEALED → `docs/_working/archive/2026-10/t0_revival/t0_conditional_prereg_card.md`，family_id=T0-CONDITIONAL，parent_context 引裁定#399 二）；无其他出口 | `config/strategy_card_lifecycle_map.yaml#D15-M17`；`ruling_registry.yaml`（裁定#399 :3068 起"复活轴=新预注册假设卡+考试制维持"；裁定#404 R4"复活唯一口=预注册新假设"） |
| SSOT 真源 | 封卡效力真源=裁定登记（#363/#390 双裁定钉死）；卡面 status 是镜像；宿主册 credential 七步流水+verdict_bindings（RED，evidence=rejudge 件） | `experiment_registry.yaml`（CARD-T0-PRERG-02：card_state=sealed、rejudge_used=true、credential seq1-7、verdict_bindings ruling_id=裁定#363）；`config/strategy_card_lifecycle_map.yaml#revival_authorizations`（裁定#331/#399/#404 三授权在册） |
| 代码模块 | 封卡本体无代码（=裁定+卡头镜像）；证据定版借 run 档案"只增不改"形态（`src/zephyr/backtest/run_archive.py` + `sop_d_run_archive_naming.md:28` errata 同构）；代码/配置面 SEALED 词零命中（骨架 grep 实测，命中皆为涨停封板 close_sealed 语义） | `src/zephyr/backtest/run_archive.py`；`docs/01_policies_and_standards/sop/backtest_system_sop/sop_d_run_archive_naming.md` |
| 门禁约束 | X03 S10→S5 就地复活重跑（enforcement=live_incident_observed——#389 批准开测时两卡早已测毕、#390 即日勘误，本禁边是真实事故后立的，全图唯一有实弹案例的禁边）；X12 对话/战役令改判已封卡（CV-09 在册性机验规格） | `config/strategy_card_lifecycle_map.yaml#D15-X03/#D15-X12`；`ruling_registry.yaml` 裁定#390 summary（"Owner 记忆正确，方案班核实失职"） |
| 自动化触发 | 零自动化；封卡动作=裁定登记+卡头改写两件人工动作；复活授权三裁定（#331/#399/#404）在图 revival_authorizations 块在册 | `config/strategy_card_lifecycle_map.yaml#revival_authorizations`（本批实读 3 条） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | M11 唯一实例证据链全闭合（判定书→重判→RED 变硬→裁定封卡→卡头镜像），且禁边 X03 有事故实弹背书 |
| 输出面 | warn | M17 复活链在人间层完整（新卡+parent_context 散文指旧），但 revives 机读键缺失（F-05 现行，见门禁行） |
| SSOT 真源 | pass | 裁定双保险（#363 封+#390 维持）+宿主册流水+卡面镜像三面一致（T0-PRERG-02 无 CV-10 违规） |
| 代码模块 | warn | 无封卡状态代码面（词零命中）——终态靠裁定纪律维持；借用的 run_archive 形态只作证据定版,不作状态真源（F-11 判定书面 gitignored 的否据已在骨架 O5 处置） |
| 门禁约束 | fail | 校验器实跑 `CV-06——T0-CONDITIONAL 命中复活判据（引用了复活授权 裁定#331,裁定#399）而 revives 缺省`——X13 禁边（复活新卡不带 revives 指针）的现行活违规，即 F-05 未修 |
| 自动化触发 | warn | 复活授权已结构化入图（revival_authorizations 3 条），校验器 CV-06 已能自动捕获缺指针——捕获自动化在、修复执行缺 |

## 4. 缺口与建议

1. 缺口（本态最硬，也是 8 条 ERROR 之一）：CV-06 活违规——T0-CONDITIONAL 引用复活授权却无 revives 键。修复成本一行：在宿主册 CARD-T0-CONDITIONAL 的 revives 字段（现为 null）填 `T0-PRERG-02`（骨架 J7/案例 A 已实证该指向即事实谱系）。
2. 缺口：SEALED 在代码/配置面零词元=机器永远认不出封卡态。建议词表加载已到位（校验器），进一步让 exam 件启动时自查 BLUEPRINT 锚卡的登记态=sealed 即拒跑（把 #390 事故的防线从人核变机拦）。
3. 建议：X03 是全图唯一有实弹案例的禁边，建议在校验器红证输出中标注 incident 出处（#389/#390 行号），供审计叙事复用。
