---
ttl: task_bound
completes_when: G1+G3 24 件统一三方合并单袋落地且裁定#496 授权链在册（本交割包转落地回执留痕）
---
# 死信清偿 G1+G3 交割包（B-UNIFIED 统一三方合并落地回执）

- 车道: st-chiefc-20261009 BU｜落地: 单袋（见 commit）｜日期: 2026-10-09
- 授权锚: Owner 2026-10-09 批文原文「40 件全批 A：G1+G3 交总队并袋，其余专车直投；G9/G10 也 A」
  （来源: 本目录 10_owner_menu_deadcure40.md 批文记录；授权链裁定=裁定#496，同 commit 原子登记）
- 对拍数据: .runtime/tmp/st-chiefc-20261009/bu_merge_triage.md + bu_merge_triage_data.json（袋 JSON blob_sha256 × blobs/<sha> 哈希验证 × HEAD × b-606 分支 × 工作树 五方）
- 分支: ai/st-gomap-b-20261006/gomap-cluster-bag（c5024b0e=L1 吸收施工, 21fcdcc2=L2 六图批）, merge-base=4e53c6698

## 0. 件数对平

| 组 | 件数(袋) | 本批落地文件面 | 
|---|---:|---|
| G1 | 20 | config/strategy_production_map.yaml（SPM 手术面终版袋 c4f96ddcf1 五阶段演进收敛）+ docs/03_modules/path_ownership_map.yaml（ownership 册再生成 aaec9b25e9） |
| G3 | 4 | data_supply_chain/dev_delivery/governance_legislation/governance_operations 四图（+panorama_master/fig11/fig16 骨架随分支 21fcdcc2 同面） |
| B-1 | (分支) | src/zephyr/trading/boot_hooks.py + src/zephyr/governance/ops_governance/budget_engine.py + tests/trading/test_boot_hooks_selfcheck.py(17测) + tests/governance/ops_governance/test_budget_recover_invariant.py(3测) |

袋内其余文件（tests/research/ 等大快照面）不在本批：F1 车道范围（09_handoff_laneF1b.md 分工），未动。

## 1. G1 SPM 手术面（20 袋 → 单文件收敛）

演进六阶段（袋 blob sha256 全文，均经 blobs/<sha> 哈希验证）：

| 阶段 | blob_sha256 | 携带袋（qid） |
|---|---|---|
| 初版 | `c89d8cadb1ca1e3fb97858c9971706ba8fdbd33c71cc6dc714907ed30de2ee26` | q-20261004-st-map9-f4-20261003-0007; q-20261004-st-map9-f4-20261003-0008; q-20261004-st-map9-f4-20261003-0009; q-20261004-st-map9-f4-20261003-0010 |
| 二 | `f75e86df092baee018aaa76cfd6446d4a6fe9d158c260dab6d44a5422901108c` | q-20261005-st-map9-chief-20261004-0001; q-20261005-st-map9-chief-20261004-0003; q-20261005-st-sP-bottleneck-20261005-0137; q-20261006-st-closeout-basereq-20261006-0122 ... |
| 三 | `ab5408a5ca702699b097e32af6908a6bd1d1cd2f51247b788d60a6dd9dd6c3fe` | q-20261005-st-map9-chief-20261005-0001; q-20261006-st-closeout-basereq-20261006-0080; q-20261006-st-closeout-basereq-20261006-0175; q-20261006-st-cure-p01-20261006-0016 |
| 四 | `e1f4762698b5cad06001999713a7da229afb1f8ebac40974723326397899df79` | q-20261005-st-map9-f7-20261005-0001; q-20261006-st-f15-frombag-20261005-0176; q-20261007-st-cure-p01-20261006-0110 |
| 五(图手术) | `79e877dadc8cddac86190d7ad597503f99ba3e184f826ff785d7d120602b9574` | q-20261008-st-map9-chief-20261008-0002; q-20261008-st-map9-chief-20261008-0006 |
| 终版(图手术终版+ownership册再生成) | `c4f96ddcf13642cfb9e826abfd0e88f98f960aa6621c198767f080eb67d7ade3` | q-20261008-st-map9-chief-20261008-0009 |

收敛判定: 工作树现值=终版袋 c4f96ddcf1 字节全等；三方合并 base=4e53c6698 × ours=工作树(G1 终版) × theirs=分支 20a1f65e8b(G3: T7 编码归一 20 行+C2 卡生命周期 handoffs) merge-file **0 冲突**；FAC-E1F 双保重复去重（两侧字节全等）；validate_strategy_production_map.py **PASS nodes=341 edges=17**。

## 2. G1 ownership 册再生成

| 文件 | 袋版 blob_sha256 | 袋 | 处置 |
|---|---|---|---|
| path_ownership_map.yaml | ``dc37e00215b26a7f9383f1a187e7d957040ed7294d7a5b7e23ea7f62db1d634a`` | q-20261005-st-map9-f7-20261005-0001 | 工作树=aaec9b25e9（-0009 再生成终版）字节全等，直落 |
| path_ownership_map.yaml | ``dc37e00215b26a7f9383f1a187e7d957040ed7294d7a5b7e23ea7f62db1d634a`` | q-20261006-st-f15-frombag-20261005-0176 | 工作树=aaec9b25e9（-0009 再生成终版）字节全等，直落 |
| path_ownership_map.yaml | ``dc37e00215b26a7f9383f1a187e7d957040ed7294d7a5b7e23ea7f62db1d634a`` | q-20261007-st-cure-p01-20261006-0110 | 工作树=aaec9b25e9（-0009 再生成终版）字节全等，直落 |
| path_ownership_map.yaml | ``aaec9b25e90cf543621be58104edff65d580549297b71b68fa83fd845f2563bd`` | q-20261008-st-map9-chief-20261008-0002 | 工作树=aaec9b25e9（-0009 再生成终版）字节全等，直落 |
| path_ownership_map.yaml | ``aaec9b25e90cf543621be58104edff65d580549297b71b68fa83fd845f2563bd`` | q-20261008-st-map9-chief-20261008-0006 | 工作树=aaec9b25e9（-0009 再生成终版）字节全等，直落 |
| path_ownership_map.yaml | ``aaec9b25e90cf543621be58104edff65d580549297b71b68fa83fd845f2563bd`` | q-20261008-st-map9-chief-20261008-0009 | 工作树=aaec9b25e9（-0009 再生成终版）字节全等，直落 |

## 3. G3 六图批（4 袋，袋 blob 与分支版字节全等收敛）

| 文件 | 袋/分支 blob_sha256 | HEAD | 工作树 | 处置 |
|---|---|---|---|---|
| config/data_supply_chain_map.yaml | `a980bd9c338b3898796585780ac24b95707ac2b2a40c937e998f0e31a5cca851` | `f703e510b31c4526149fa0efb8037b52d03cd084e54ce2e7916defed43148008` | `f703e510b31c4526149fa0efb8037b52d03cd084e54ce2e7916defed43148008` | 直落分支版（袋=分支字节等）; 残留: 语义注解层系袋面手改痕迹, 生成器重放剥离, 需回灌 fig12 skeleton 真源 |
| config/dev_delivery_map.yaml | `1ac5125aa6355184adbc26345ff9e7f6d8f1c99021dd52a510e9839e160724e7` | `58aa7ae8367ddca11c227f7ae382217544b9252e76bdb198e6af72acea048584` | `4de059519000d3688ffa2c9b60ddd08ab83c5d8418af6ae1bdc8ddd0fb60fe94` | 采生成器重放版（10-09 07:48 新于分支 01:13 与 wt 12:00 终刷, 仅时戳+3 item_count 刷新; 机生权威）; validate PASS nodes=30 edges=31 |
| config/governance_legislation_map.yaml | `8f93d14566fd8fc2bdc4642b5ebde5782851e237e1981630a2e457b6ccc2d399` | `2966512f8913b27cc62e7e4e539ee72b6c325a0646f41ddc186f00fc9d901cb6` | `2966512f8913b27cc62e7e4e539ee72b6c325a0646f41ddc186f00fc9d901cb6` | 生成器回灌重刷（分支 counts 落后账本 306→312; 刷新后 active=291, validator PASS 零 error） |
| config/governance_operations_map.yaml | `628c1825fb2d3d80e8b2168791902d8ed55a36b05d918a7db1bb6882a349085e` | `ed96c1bcf4f95c4c4204dc817b4658c0fcf17a8a9d700bb729a7eeadcfb0cbdf` | `ed96c1bcf4f95c4c4204dc817b4658c0fcf17a8a9d700bb729a7eeadcfb0cbdf` | 直落分支版（10-07T18:42 新于 HEAD 10-04T14:51; 1672+/1785- 重生成面） |
| config/panorama_master_map.yaml | `c7f99b5e3ec43ac352e2c753e0f50928d6af8aa22f88d64823e4056cad5eda19` | `67a21707903e217464cdaebc2287cd9bbcb76c1efdf02852054fda4741220e45` | `67a21707903e217464cdaebc2287cd9bbcb76c1efdf02852054fda4741220e45` | 直落分支版（B-pan 过期注记更正 2 行）; 残留: 更正需回灌 generator master 输入 |
| docs/_working/map_build/fig11_delivery/00_skeleton.md | `a18b0437c34dfeb69fdaf7687bc44306570bc049847408039f9a53742fc224fd` | `2330fc12575618b8167120a0d746aaa7b00fa5293cd573b8efc5e8b7b7b9bfbf` | `2330fc12575618b8167120a0d746aaa7b00fa5293cd573b8efc5e8b7b7b9bfbf` | 直落分支版（C4 upstream_map_ref Step10 入边, 骨架真源） |
| docs/_working/map_build/fig16_legislation/00_skeleton.md | `c4b5a6a1c5426cd8e14567e7cd7789d274dc8f959b5153d22078cb2a3935e5d5` | `c29553a93614e5a48f963c5e1b55519a55c0bc1c2d4523475984bb39e1231689` | `c29553a93614e5a48f963c5e1b55519a55c0bc1c2d4523475984bb39e1231689` | 直落分支版（B-16 立法→运行时归属边注, 骨架真源） |

G3 袋清单: q-20261008-st-gomap-b-20261006-0006; q-20261008-st-gomap-b-20261006-0007; q-20261008-st-gomap-chief-20261004-0034; q-20261008-st-gomap-chief-20261004-0035

## 4. B-1 L1 吸收施工成品（分支 c5024b0e）

| 文件 | 分支/袋 blob_sha256 | HEAD | 处置 |
|---|---|---|---|
| src/zephyr/trading/boot_hooks.py | `eee7fe766d1d418393f7cfabd73333c89e75854573f9fbe66e789ea4388b2655` | `6dff8a0b87b43703e8444e03343d9cb05d9126d613f13d2c0ede6fb42a1a3b4b` | T8a tech_stack 组件自检（裁定#485）; HEAD 自 merge-base 未动=纯快进（diff 仅 +189/-2 头注升级） |
| src/zephyr/governance/ops_governance/budget_engine.py | `a484a944257d4ac7ebd9e312c24024a6c1f2e092261292c5df4af1035b8a3f00` | `842a8d353049021ed278287004dbd4f1fdedac6385ae513303e4a2af50879a57` | T8b R12 聚合不变式 INVARIANT-BUDGET-AGG-CONSISTENCY; diff +36/-0 分支版=HEAD 纯超集 |
| tests/trading/test_boot_hooks_selfcheck.py | `fc2da14b8c05b8c84bf8bcf1f85bdc0b47c80a1465c2592ff3d1ad28fe05fe4e` | `无` | 17 用例; 袋 fc2da14b8c=分支字节等(4 袋收敛); pytest 17 passed |
| tests/governance/ops_governance/test_budget_recover_invariant.py | `fc74705d26488ed2e965dfcf8096aff2dfa7ac2f8abb87e83ad570ce73f1fe00` | `无` | 3 用例; pytest 3 passed |

## 5. D6 无主变更恢复记录（st-fc-spm 死会话）

- st-fc-spm 不在 .runtime/session_registry（无 json）且 lock_files 无其 claim → 会话死。
- 其工作树未暂存面: SPM 终版(c4f96ddcf1)/dev_delivery 12:00 终刷(4de0595190)/path_ownership 再生成版(aaec9b25e9) —— 全部并入本批零丢弃。
- 其 index 中间态: SPM index=4f319bc357(与 79e877dadc 相似度 0.9977=同族中间演进版)、DSC index=9137189d35(与 HEAD 相似度 0.9933) —— 均无独有内容，被终版超集覆盖，存档 .runtime/tmp/st-chiefc-20261009/merge_ws/index_*.yaml。

## 6. 验证证据

- validate_strategy_production_map.py: PASS nodes=341 edges=17（WARN 2 条为既有非阻断）
- validate_data_supply_chain_map.py: PASS nodes=43 edges=62｜validate_dev_delivery_map.py: PASS nodes=30 edges=31｜validate_governance_legislation_map.py: PASS 零 error（回灌后）
- pytest tests/trading/test_boot_hooks_selfcheck.py + tests/governance/ops_governance/test_budget_recover_invariant.py: 20 passed
- 生成器对拍: legislation 实刷回灌｜dev_delivery 重放采纳｜DSC 重放非等效(注解剥离)保留袋面+残留登记｜panorama 无 --out 真跑有回退风险保留袋面+残留登记

## 7. 净零声明

零新 gate/零新注册表/零新模块（两测试文件为分支成品随批, tests/ 豁免）; creation_token 登记 1 条（本文件）。

