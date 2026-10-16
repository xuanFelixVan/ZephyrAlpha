---
ttl: task_bound
creation_token: mine-fullchain-cardlife-20261015-d15s3
created_by: mine-fullchain-cardlife-20261015
title: "图15 环节子文档 D15-S3 冻结 frozen"
map_lineage: 派生自 docs/_working/mine_fullchain_20261015/00_skeleton.md §2.2（D15-S3 行）
---

# D15-S3 冻结 frozen（卡生命周期十三态之三，全图最大驻留态）

## 1. 定义

- 语义（词表 value=frozen）：考窗/阈值/桶边界/N_eff 全部写死，参数不可再改。
- 状态机属性：非终态；credential_exemption=true（词表标 false 需凭证，但态本身驻留免凭证）；machine_readable=partial；`config/strategy_card_lifecycle_map.yaml#D15-S3`。
- 禁边挂钩：D15-X02 S3→S3 静默改 frozen 参数（checker=CV-17，机验=frozen 段字节级 sha 变更而未过 M05/M16 即红）；先例工具=`src/zephyr/backtest/run_archive.py:44`（content_sha256，本挖矿批实存）。
- 判据真源（INV-1 禁复制）：`docs/01_policies_and_standards/sop/mining_sop/factor_mining_sop_policy.md:105-126` 卡模板（`status: frozen # 启动后不得改动`）+ `docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md:24-30` §1 准入。

## 2. 六向台账

| 向 | 内容 | 文件路径证据 |
|---|---|---|
| 输入面 | M03 S1→S3（owner_sign，gated，✅，observed=SECTOR-PRERG-DECK-01/T0-CONDITIONAL）；M04 S2→S3（⬜ 零活体）。冻结语义=开工令即冻结（案例 C：v0→v1 同卡号换文件版本） | `config/strategy_card_lifecycle_map.yaml#D15-M03/#D15-M04`；`docs/_working/sector_line/sector_prereg_exam_cards_v1_frozen.md`；`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml`（裁定#389 快签通道条目） |
| 输出面 | M06 S3→S5（机，test_evidence，四条准入）；M05 S3→S4（带日期附录）；M16 S3→S13。观察：M05/M06 各有 T0-PRERG-02 实证 | `config/strategy_card_lifecycle_map.yaml#D15-M05/#D15-M06`；`docs/01_policies_and_standards/sop/backtest_system_sop/exam_policy.md:24-30` |
| SSOT 真源 | 语料 by_token frozen=58（最大词元簇）；登记面 frozen=55；台账 card_state=frozen=53（single_hypothesis 50+family 4+narrowing 1 中取 frozen 者） | `config/strategy_card_lifecycle_map.yaml#corpus.by_token`（frozen: 58）/#corpus.by_registered_state（frozen: 55）/#card_ledger（60 条 CARD-*） |
| 代码模块 | 考试执行件以 frozen 卡为判据真源（BLUEPRINT 反向锚）：`scripts/audit/t0_conditional_e4_exam.py:1`（`# [BLUEPRINT] SH-SCRIPT-001 \| docs/_working/t0_revival/t0_conditional_prereg_card.md \| §2 状态门+§5 判据`）、INVARIANTS 行 `:8`、MODIFY-GUARD `:9`；指纹先例 `src/zephyr/backtest/run_archive.py:44,127` | 上述四文件（本批实存核验） |
| 门禁约束 | X02（CV-17 sha 指纹）+ X09 同假设双卡并行考（CV-08，live_incident_observed：T0-PRERG-01 与 ALGO-VWAP-03 同 hypothesis_key=vwap_reversion_t0）+ N_eff 封闭族账（CV-08C） | `config/strategy_card_lifecycle_map.yaml#D15-X02/#D15-X09`；校验器 2026-10-15 实跑 ERROR：CV-08 ×1 + CV-08C ×3（FPOOL-20260919-TOP20/MIDVAL-20260919-TOP10/T0-PRERG 族账不平） |
| 自动化触发 | 无状态写自动化：冻结=人写卡面+裁定/快签凭证；族账与指纹全靠生成器回扫+校验器事后判 | `scripts/governance/d5_architecture/generators/generate_strategy_card_lifecycle_map.py`（corpus 现算）；校验器 CV-17（--skip-live 降腿） |

## 3. 自审闸三态（逐向）

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | warn | M03 有活体但 M04 零活体；by_token frozen=58 对 registered frozen=55 差 3（冻结卡未全数登记） |
| 输出面 | pass | M05（≥5 卡附录修订）、M06（T0-PRERG-02 两轮进测）各有实证流水 |
| SSOT 真源 | warn | 族账三处 CV-08C 判不平（单假设成员数≠声明 n_eff）；卡号↔文件非一一映射（v0/v1 双文件）靠 versions 语义消化，登记面未见 versions[] 字段实例 |
| 代码模块 | warn | 执行件 BLUEPRINT 锚全在（判据反向锚扎实），但 X02 的 sha 指纹机验未接线（仅先例工具在，无卡面 checker） |
| 门禁约束 | fail | 校验器实跑 4 条 ERROR 落在本态相关面（CV-08 X09 双卡 N_eff 双计 + CV-08C ×3 族账）；且专闸 STRATEGY-CARD-LIFECYCLE-MAP=墓碑（`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml` STRATEGY-CARD-LIFECYCLE-MAP 条目：status=deprecated，"实现从未落位"，取证=`docs/_working/libghost_campaign/00_ledger.md` 班账 K8） |
| 自动化触发 | fail | 58 张冻结卡的状态登记全部靠生成器回扫，无迁移时点自动登记；族账不平正是无实时对账的直接后果 |

## 4. 缺口与建议

1. 缺口（最重）：X09 双卡 N_eff 双计与 CV-08C 三族账不平是**在册活违规**——建议按校验器红证开裁定议题，先把 FPOOL/MIDVAL/T0-PRERG 三族 n_eff 声明改齐（或补成员登记）。
2. 缺口：CV-08B 卡号↔文件↔判决三元错绑（T0-PRERG-01 的 RED 证据实为 ALGO-VWAP-03 的文件，F-07 现行）——建议以 card_id 主键+versions[] 收敛，清理 #390 affected_files 错引。
3. 建议：X02 落地最低成本路径=校验器 --live 腿复用 `run_archive.content_sha256`，把 60 张在册卡的 body_fingerprint 纳入 commit 期比对（配合墓碑门复活：实现 `src/zephyr/gov_enforcement/commit_gates/map_family/strategy_card_lifecycle_map_gate.py` 后删墓碑条目，gate_registry 注明的复活方式）。
