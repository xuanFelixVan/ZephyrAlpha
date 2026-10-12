---
ttl: task_bound
session: st-regsolo-20261010
landing_note: 本件由终清波三 st-fclean3-20261012 依统筹批复 M2 闸①代落，正文零改动，仅补 docs/_working 必需的 ttl frontmatter（原文无 frontmatter）；origin sha 见 wave3/26_件 §一
---

# T1 直写轨调用面普查（session=st-regsolo-20261010）

> 调研完成。主仓零写入；本文件为唯一输出。行号基于 2026-10-10 工作区快照。

## 结论（≤8 条）

1. **A件最大障碍不在 batch_creation_tokens 本身，而在断链的意图通道**：`scripts/governance/register_asset.py:170` 声称走「意图API正道」调 `scripts/governance/d3_metadata/register_tokens_ledger.py`，但该文件**全仓不存在**（rg --files 零命中）→ `rc != 0` 每次静默 fallback 回 batch_creation_tokens 直写（:176-191）。A件薄壳落地时必须一并修复或删除这条幻影客户端引用。
2. `batch_creation_tokens.py` 直写面唯一且集中：`insert_block`（:327-385，safe_write_text CAS :368）写 `capability_canonical_file_registry.yaml`。进程内消费方 3 家（scaffold.py、dead_letter_doctor.py、d8_doc_sync/algo_flow_reverse_orphan_reconciler.py）+ 子进程 2 家（register_asset.py、factory_intake_pipeline.py）+ 测试 2 件。
3. 七热册中**五册已无代码直写者或仅剩生成器**：ruling_registry / architecture_issue_registry / error_code_registry（architecture_model/contracts/）= 纯手工登记无代码写者；rule_catalog_registry（REG-DOC-001 已重定向并入 PS-REG-018）= generate_rule_catalog.py 合法生成器；**真正的活直写簇集中在 module_translation_registry.yaml（3 个直写者）与 candidate_module_registry.yaml（1 个）**，A 件收敛后应立 B/C 件跟进。
4. **第八个隐藏直写面**：`scripts/governance/registry_batch_edit.py`（TTL=permanent，自述「登记表 YAML 批量编辑统一入口」AI sessions 消费）——通用纯插入直写工具，若不限定作用域即可绕过 A 件写七热册；建议加七册 deny-list 或改道意图 API。
5. 守恒闸语义已有立法去处：`docs/_working/registry_migration/02_ledger_design.md:237` 明文「batch_creation_tokens 守恒闸语义下沉 API 同构保留」，`ledger_identity.py:28` 已声明与 B22 (file,token) 断言结构等价——删除工具内闸实现不丢语义。
6. 教直写的「活教程」真源是 `commit_guide_sources/file_type_checklists_registry.yaml`（:44/:129/:132，提交时经 --emit-guide 递送给每个会话）+ `generate_front_door.py:180` 机生首页——这两处改口后教学面自动收敛；docs/_working/ 下各战役案卷属史志保留只读。
7. 官方测试已迁址但模块头未跟：测试实际在 `tests/gov/governance/d3_metadata/test_batch_creation_tokens.py`，而模块头 `[TESTS]`（batch_creation_tokens.py:24）仍指旧路径 `tests/governance/d3_metadata/`——A件顺手修。
8. 附带发现：`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.heal.tmp` 残留临时文件（违反零临时文件精神），且 `wave1b/dead_letter_prescriptions.py:322` 处方文案路径写错（`scripts/governance/batch_creation_tokens.py` 缺 `d3_metadata/` 层级）。

## A件改造对象函数清单（保留/删除/改写三分）

被测签名兼容下限=两个测试文件的实调面（tests/gov/governance/d3_metadata/test_batch_creation_tokens.py:66-177 + tests/test_batch_creation_tokens_anchor.py:20+）。

**保留（签名不变，非写面或过渡期兼容）**：
| 函数 | 消费方 | 理由 |
|---|---|---|
| `detect_file_type` (:416) | scripts/lock_files.py:1746 | 纯路径分类表驱动，与写道无关 |
| `print_guide_for_path` (:437) | CLI --emit-guide、main | 只读递送，独立价值 |
| `scan_unregistered` (:96) | main、官方测试:86 | 读侧发现面 |
| `load_registered` (:109) | main、dead_letter_doctor:619、官方测试:85 | 幂等判据；A件后可内部改读 PG/投影 |
| `TokenInsertError` (:81) | scaffold:1267、doctor:653、两测试 | 过渡期兼容；长期别名 APIError |
| `_creation_tokens_section` (:145) | scaffold:1274、doctor:650、algo_flow_reverse_orphan_reconciler:361、官方测试:157,170 | 段边界单点（跨文件消费，已成公共事实） |
| `_TOKEN_RE` (:75)、`_wide_prefix_issues` (:388) | doctor:634/:625 | 防呆判据同源复用 |
| `_REGISTRY` 常量 (:74) | doctor:649、测试 monkeypatch | 过渡期；A件后测试改 PG fixture |

**改写（薄壳化）**：
| 函数 | 处置 |
|---|---|
| `insert_block` (:327) | 保签名 `(block, anchor_capability, expect_files)`，函数体改三步：解析 block→`api.register`→`baseline.publish_snapshot`→`registry_projection_generator --render`；anchor 参数过渡期忽略（PG 无锚点概念），改道完成后 deprecate |
| `build_block` (:121) | 保签名（doctor:641+两测试消费），语义变为「渲染 entries 数据结构」供 API payload |
| `main`/CLI (:465) | argparse 面保留（会话肌肉记忆），实跑分支改调三步正道（可复用 register_asset._step_token 同款，:148-197）；--dry-run 改查 PG |

**删除（改道完成后，语义已立法下沉 API）**：
`resolve_anchor`(:166)、`_anchor_block_end`(:182)、`_post_write_issues`(:204，官方测试:177 在用——随测试同批改)、`_rollback`(:228)、`_entry_keys_of_text`(:253)、`_registry_rel`(:268)、`_head_entry_keys`(:276)、`_lost_entries_issue`(:284)、`_stale_base_issues`(:306)、`_mass_deletion_issues`(:291)。注：`commit_queue_landing.py:493` 仅注释引用 `_entry_keys_of_text` 立法先例（非 import），删时顺手改注释指向 `ledger_identity.entry_composite_key`。

## 直写调用点改道清单

### REG-CAPCAN-001 capability_canonical_file_registry.yaml
| file:line | 形态 | 处置 |
|---|---|---|
| scripts/governance/d3_metadata/batch_creation_tokens.py:327-385 (safe_write_text:368) | 直写本体 | **A件改薄壳** |
| scripts/scaffold.py:1266-1276 | 进程内 import insert_block/resolve_anchor | 改道三步 API（过渡期经薄壳零改动兼容） |
| scripts/governance/dead_letter_doctor.py:605-652 | 进程内 bct 函数级 import（load_registered/build_block/insert_block 等） | 同上；:352 处方文案随 A件改口 |
| scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py:444-491 | **裸 safe_write_text 删孤儿 token 条目**（反向删除操作） | 改道需 API 增 deactivate/删除意图语义；过渡期保留+登记豁免（事件触发 reconciler，非 cron） |
| scripts/governance/register_asset.py:148-197 | 子进程「幻影 intent client」→fallback batch 工具 | **修复断链**：register_tokens_ledger.py 不存在；新建 client 或直调 api.register 三步，删 fallback |
| scripts/backtest/factory_intake_pipeline.py:308-323 | 子进程 batch 工具 | 改道正道 client |
| scripts/governance/registry_batch_edit.py（全文） | 通用直写工具（AI 会话统一入口） | 七热册 deny-list 或改道意图 API（结论#4） |
| scripts/lock_files.py:1746 | import detect_file_type（只读） | 保留 |
| catalogs/capability_canonical_file_registry.heal.tmp | 残留 tmp | 呈报 Owner 清理 |

### REG-MODULE-TRANSLATION-001 module_translation_registry.yaml
| file:line | 形态 | 处置 |
|---|---|---|
| scripts/governance/d3_metadata/add_module_translation.py:466-486 (_write_registry, safe_write_text:478) | 直写者（plain_zh 登记正门） | **B件候选**：同 A件模式薄壳化（api.register REG-MODULE-TRANSLATION-001） |
| scripts/governance/_shared/algo_flow_translation_sync.py:96-103 | safe_write_text 派生段（algo_submodules 段整体重建） | 派生段生成器语义——并入投影生成器链或声明豁免（生成器类直写，非违建但需归口） |
| scripts/governance/harvest_candidates_from_drafts.py:27,66-67 (TTL=permanent/production) | 追加直写双册 | 改道 api.register（C件） |
| scripts/governance/dead_letter_doctor.py:672-703 | 经 amt.add_translation | 随 add_module_translation 改道 |

### 其余五册
| 册 | 代码写者 | 处置 |
|---|---|---|
| ruling_registry.yaml (REG-RULING-001) | **无**（纯手工登记，RULE-RULING 同 commit 原子；next_ruling_id.py 只读取号器 :INVARIANTS 明示永不写册） | 接 api.register 意图通道收口手工面 |
| architecture_issue_registry.yaml (REG-ARCH-ISSUE-001) | **无**（reconciliation_registry.py 只读+写 .runtime 报告 :1508） | 同上 |
| architecture_model/contracts/error_code_registry.yaml (REG-ERRCODE-001) | **无**（errcode_consistency_gate 等 8+ 只读） | 同上 |
| rule_catalog_registry.yaml (REG-DOC-001→PS-REG-018) | scripts/governance/d3_metadata/generate_rule_catalog.py（幂等生成器+保育语义 :8） | **合法生成器保留**；需声明与 PG 投影的边界（保育语义 vs 投影重生成双源风险，呈战役裁定） |
| candidate_module_registry.yaml (REG-CAND-001) | harvest_candidates_from_drafts.py:66 | 改道 api.register（C件） |
| data_asset_registry.yaml（自declared REG-DATAFLOW-001，**非 P0 七册**） | generate_data_asset_coverage.py:60（自述 datasets 段增量唯一写者） | 合法生成器保留（P0 外观察项） |
| （合法写侧基准）scripts/governance/registry_projection/registry_projection_generator.py | 唯一合法 YAML 重生成器 | 保留 |

## 教程勘误清单

| 位置 | 现文 | 勘误建议 |
|---|---|---|
| docs/01_policies_and_standards/sop/governance_sop/commit_guide_sources/file_type_checklists_registry.yaml:44 | 「token 先行：batch_creation_tokens.py --prefix 登记」 | 改为三步正道（api.register→publish_snapshot→render 或等价 CLI）；此册是提交时 --emit-guide 递送真源，改此处=全量会话教学面收敛（最高优先） |
| 同上:129 | 「纯插入；条目插既有根键列表尾（creation_tokens 尾、di_seam_exemptions 行之前）」 | 删除段锚教学（PG 无段锚概念），改「意图登记+投影重生成」 |
| 同上:132 | 「token 批量走 batch_creation_tokens.py（守恒闸防吃条目）」 | 改新通道名；守恒闸已下沉 API |
| scripts/governance/generators/generate_front_door.py:180 | 「新建文件 先 creation_token（batch_creation_tokens.py），再写」 | 改生成器源串（机生 front_door 自动跟新） |
| src/zephyr/gov_enforcement/commit_gates/create_guard.py:51,1220 | 门禁文案教 `batch_creation_tokens.py --merge-evaluation 登记` | 改口新正道（门禁文案=最高频接触面） |
| src/zephyr/gov_enforcement/rule_bridge/commit_preflight.py:586 | 处方教 batch CLI | 改口 |
| src/zephyr/gov_enforcement/commit_gates/registry_yaml_parse_gate.py:116,174 | 注释「登记正门仍是 batch_creation_tokens 直写」 | 随 W5 执法翻转更新（03_projection_design.md:261 已立法） |
| scripts/commit_queue.py:3596 | 死因处方「batch_creation_tokens.py 登记 token 后重投」 | 改口 |
| scripts/governance/dead_letter_doctor.py:352 | 处方模板教 batch CLI | 改口 |
| scripts/governance/wave1b/dead_letter_prescriptions.py:322 | 处方教直写且**路径错**（缺 d3_metadata/） | 改口+修路径 bug |
| scripts/governance/d3_metadata/generate_rule_catalog.py:149 | 注释「add_module_translation/batch_creation_tokens 等 YAML 侧通道写入」 | 措辞随改道更新 |
| scripts/governance/meta_question/wo_intake_reconcile/patches/README.md:14 | README 教 batch_creation_tokens | 勘误（活文档） |
| docs/_working/2026-09-18_vocab_consolidation_campaign/w1_mining/w1c_gates.md:94-105 | 完整教程「§3.2 creation_token 登记流程」通道A/B | 活 campaign 教程→勘误；archive/2026-09/ 副本=史志保留 |
| docs/_working/night_sweep/00_orchestration.md:52 | 编排手册教 batch 命令 | 同上（archive 副本保留） |
| docs/_working/{three_piece_infra,total_command_closeout,recovered_task_cards,commit_speedup_campaign,registry_migration 等} 各案卷 | 教/记录 batch 用法 | **史志保留只读**（task_bound 案卷，registry_migration/03_projection_design.md:76 本身已立法改道方向） |
| batch_creation_tokens.py:34-46 模块 docstring 用法段 | 教 CLI 直写 | 随 A件改写为三步正道用法 |

## 证据（file:line 引用）

- 幻影客户端：register_asset.py:149-151（自称意图正道）/:170（调 register_tokens_ledger.py）/:176-191（fallback batch）；rg --files -g 'register_tokens_ledger*' 全仓零命中。
- 直写本体：batch_creation_tokens.py:74（_REGISTRY 路径）、:327-385（insert_block）、:368（safe_write_text CAS）。
- 进程内消费：scaffold.py:1266-1276；dead_letter_doctor.py:605-652（:619 load_registered/:625 _wide_prefix_issues/:634 _TOKEN_RE/:649 _REGISTRY/:650 _creation_tokens_section）；algo_flow_reverse_orphan_reconciler.py:4（DEPENDENCIES 声明）/:361（import _creation_tokens_section）/:488-491（safe_write_text+回滚）。
- 子进程消费：factory_intake_pipeline.py:311-323；register_asset.py:179-191。
- 只读消费：lock_files.py:1733,1746（detect_file_type）；commit_queue_landing.py:493（注释引立法）。
- 测试签名面：tests/gov/governance/d3_metadata/test_batch_creation_tokens.py:27,66-177（main/build_block/insert_block/load_registered/scan_unregistered/TokenInsertError/_creation_tokens_section/resolve_anchor/_post_write_issues）；tests/test_batch_creation_tokens_anchor.py:20+（build_block/insert_block）。
- 七册 id↔文件映射：baseline.py:102-110（P0_REGISTRY_IDS）；registry_master_index.yaml:37,61,69,117（physical_path）；ROOR:283-291（REG-DOC-001 重定向 rule_catalog_registry）、:490-493（REG-ERRCODE-001→architecture_model/contracts/error_code_registry.yaml）；data_asset_registry.yaml 头部 module_id=REG-DATAFLOW-001（非 P0）。
- 其余册写者判定：generate_rule_catalog.py:8,18（幂等生成器+保育语义）；generate_data_asset_coverage.py:5,60；harvest_candidates_from_drafts.py:24-29,66-67；add_module_translation.py:466-486；algo_flow_translation_sync.py:8,96-103；next_ruling_id.py（INVARIANTS 永不写册）；registry_batch_edit.py 头部（通用直写工具）。
- 改道立法先例：registry_migration/03_projection_design.md:76,169,261,285；02_ledger_design.md:237（守恒闸下沉 API）；ledger_identity.py:28。
- 残留物：catalogs/capability_canonical_file_registry.heal.tmp；模块头 [TESTS] 旧路径 batch_creation_tokens.py:24 vs 实际 tests/gov/governance/d3_metadata/。
