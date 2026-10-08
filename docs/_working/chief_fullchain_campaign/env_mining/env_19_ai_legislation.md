---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_19_ai_legislation.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-19 AI 立法与门禁挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **覆盖坐标**：图16 治理立法流（`config/governance_legislation_map.yaml`，2026-10-05 新生，准入=裁定#486）+ ROOR 中央注册表索引（`docs/registry_of_registries.yaml`，94 册）+ 裁定册 REG-RULING-001（303 条，PG 账本 7f0beccac4 cutover）。
- **真源锚**：图16 骨架 §1-§3（`docs/_working/map_build/fig16_legislation/00_skeleton.md`）+ PG 账本（文件 yaml=只读投影，PG-wins）；ROOR summary 段由 `scripts/governance/d3_metadata/check_registry_consistency.py --refresh-summary` 机生。
- **职责一句话**：Owner 意图如何变成被门禁机械执行的规则——立法流 9 transitions（∅→draft/active/decided/void、draft→active、active→superseded/deprecated/decided、跨实例复活 ∅→active）全链机械锚定。
- **状态总判**：图16 结构面完备（6 态/9 件/9 迁移/7 禁边，逐条带 source_anchors）；闭环链 3 条代码级实证（§2）；**本环境唯一红灯=ROOR broken:1 REG-CASEBOOK-001（物理册缺失）**，根因已定位（§1"新"向①）。

## §1 六向台账

| 向 | 内部反查发现（带路径） | 外部 | 判定 |
|---|---|---|---|
| 上（触发面——立法入口逐件证） | D16-N1 呈报口（立项卡/总包令/呈裁件；裁定#486 ② 后 GO/NO-GO 权归 Owner）→D16-N2 取号器 `scripts/governance/next_ruling_id.py`（--next 幂等/--claim O_EXCL 独占/--release 仅本会话，编号不回收）→D16-N3 意图API `src/zephyr/governance/registry_ledger/api.py`（register/update/retire，接口负面清单禁整册写，CAS 409 记事件）。三件全部在盘且被图16 逐条锚定 | fig16 T1-T5 source_anchors 指向 api.py/next_ruling_id.py | wired |
| 下（消费面——立法产物谁在吃） | D16-N7 消费方索引三族：①审批通道 `src/zephyr/gov_enforcement/commit_gates/approval_resolver.py`（_ruling_channel：active+expires_at+approved_paths，仅 active 放行）；②reference 类 gate=RULING-REFERENCE（74 号，见"新"②）；③取号分母+对齐清单挂轴。发布面=`src/zephyr/governance/registry_ledger/baseline.py`（publish 快照 snapshot_version 9，同 content_sha 幂等） | 图16 counts 段：entries_total 303/ledger_rows_active 302/by_status active 282+decided 13+draft 1+superseded 4+void 2=302 自洽 | wired |
| 内（一致性面——计数与投影对拍） | 303 vs 302 之差=图16 :243-244 明示的 render 在途窗口允许偏差（D16-N6 投影非真源）；superseded_by_chains 5（D16-T6 取代链在册）；零 deprecated 实例（D16-S4 结构性预留非自造）；7 条禁边 D16-X1~X7 每条带机械判据（409 拒/PG-wins 回滚/O_EXCL） | 判红机制=`scripts/governance/d5_architecture/validators/validate_governance_legislation_map.py`（counts 一致性判红，文件头 :3） | pass |
| 旁（同名不同物——两套门禁不混） | 图10 GOMAP=治理**运行**面 vs 图16=立法**条目**面（boundary :29 词汇零交 w5_1 不并）；GateEngine 静态册 `src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml`（91 gates）与 commit gate 链是两套系统（ROOR ISS-003 自证预期）——**RULING-REFERENCE 走 commit_gate_registry 不入 _registry.yaml**（本簿实测 grep -i ruling 于 _registry.yaml 零命中），"查册查不到"≠"门不存在" | — | signal |
| 史（数字三代与机判替代） | ROOR 88→94 实证：`git show HEAD~3:docs/registry_of_registries.yaml` :1005 `total_registries: 88`→今 94（tier0 12+tier1 47+tier2 35），增量含 8 张 REG-MAP-*（ROOR :579-:663，图11/12/TDM/工厂/GOMAP/图14/图15/图16）等；summary.legacy_manual_claims_replaced 段自陈旧值 19/5/1"无机械真源"、broken 已改由 `_roor_entry_health` 机判——散文计数退役史在册 | 骨架 `01_skeleton_environments.md:76` 仍写"ROOR(88 册)"=骨架数字漂移（宪法 §4.3 计数勿写死的活案例） | signal |
| 新（本簿 2026-10-06 三条） | ①**broken=1 根因定位**：REG-CASEBOOK-001（ROOR :535，status: active，entry_count: 5，Owner 2026-10-04 上户口批 st-vm12e-20261004）声明的 physical_path `docs/01_policies_and_standards/_registry/catalogs/casebook_registry.yaml` **全仓 find 零命中**——户口已上、身子未落；判红机制=`check_registry_consistency.py:771 _roor_entry_health`（文件型路径不存在→broken）→summary.broken:1；悬空引用面 2 处（`rule_catalog_registry.yaml:4949` 引该路径、`capability_canonical_file_registry.yaml:35469` 自陈"casebook_registry 物理化待上户口批"）。②闭环实证链 3 条（§2）。③宪法 RULE-RULING 一行=立法流散文投影、图16=机械面，两层一致性今日首验通过 | — | signal |

## §2 挖干自评

- **闭环实证链（裁定→规则→gate）3 条代码级**：
  - **链A 引用原子性**：裁定#20-A/B（病根=全项目 493 处"裁定#NNN"引用无中央登记，`ruling_reference_gate.py` 文件头自陈）→裁定#20-G 2026-07-18 阶段2 hard block（`ruling_reference_gate.py:90 _MANUAL_STAGE=False`）→gate RULING-REFERENCE（`:301 GateSpec(gate_id="RULING-REFERENCE", check=_check, priority=74)`，L1 编号空洞 warn+L2 同 commit 原子 hard block）→消费方 `git_commit_gateway.__init__`（文件头 [CONSUMERS]）→图16 收编为 D16-N4+禁边 D16-X4。
  - **链B 图16 准入**：裁定#486 ①② → `governance_legislation_map.yaml` admission_ruling 字段（:12）→gate `src/zephyr/gov_enforcement/commit_gates/map_family/governance_legislation_map_gate.py` + 校验器 `scripts/governance/d5_architecture/validators/validate_governance_legislation_map.py`——裁定→图→门→校验四层同锚。
  - **链C 规则-门配对**：`docs/01_policies_and_standards/rules/trae_063_data_ops_discipline.yaml:133 paired_gate_id: "NO-BARE-SQL"`（Phase 3.5 规则-执行配对字段）+ `:138` 裁定#372 锚——86 个 `rules/trae_*.yaml` 的 paired_gate_id 是规则→gate 机械挂接的通用字段。
- **三扫收敛**：①立法流 9 transitions 逐条锚定✅；②ROOR 94 册三层（tier/medium/status）清点✅；③闭环链反向（gate 文件头→裁定号→账本/意图API）✅。
- **长尾（如实登记）**：PG 账本 live 对拍未跑（本簿只读约束；图16 laws 自陈"实例对拍只对生成时点负责"，计数采 counts 段口径）；draft 态 1 条身份未展开（非本簿义务，留 PG 侧）。

## §3 挖后自审闸三态裁定

**挂起排期**（唯一施工候选卡 Owner 门位，非卡证据）。
- **候选施工件**：REG-CASEBOOK-001 物理化——落 `docs/01_policies_and_standards/_registry/catalogs/casebook_registry.yaml`，收编 CASEBOOK-001~005 五本路径身份（ROOR :539 description 已载明清单）。
- **理由**：broken=1 证据链闭合（上户口批文+两处悬空引用+判红源码三证齐全），但 `capability_canonical_file_registry.yaml:35469` 明载"物理化**待上户口批**"——物理化批≠2026-10-04 上户口批，Owner 门位（宪法 §5.2 注册表类）未过；本簿禁新建文件，不硬闯。
- **解锁条件**：Owner 对物理化的显式批（裁定或批文）→施工走 CREATE-GUARD 登记（ROOR 已有登记不重复）→落地后 `check_registry_consistency.py --refresh-summary` 复跑验 broken 归零。**随批小件（low）**：骨架 :76 "88 册"去字面（当日可办）。

## §4 挖矿日志

- **轮1（2026-10-06）**：全读图16 244 行（6 态/9 件/9 迁移/7 禁边/counts 逐项）+ROOR summary 段——发现 broken:1 与骨架"88 册"漂移两信号。
- **轮2**：broken 根因三步实证（ROOR 条目→物理路径全仓 find 零命中→`_roor_entry_health` :771-783 判据源码）；闭环链反向核查（gate 文件头 INVARIANTS/MODIFY-GUARD→裁定#20 族/#486→api.py/baseline.py/next_ruling_id.py）。
- **轮3**：git 纵向证 88→94（HEAD~3 :1005 对比）；链C 抽样验证（trae_063 paired_gate_id）；确认 RULING-REFERENCE 不在 GateEngine 静态册的两套门禁分界（ISS-003）。
