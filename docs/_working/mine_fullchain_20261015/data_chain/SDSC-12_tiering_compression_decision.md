---
ttl: task_bound
---
# SDSC-12 冷热分层 / 压缩决策（契约驱动，结构上不可能产数 ✅）

> 挖矿工程：全链路图12 数据供给链 S4 冷备段 4/4｜真源=config/data_supply_chain_map.yaml#DSC-12｜挖矿时点=2026-10-15
> 自审闸口径：pass=证据实存且复核一致；warn=在册但有未证项/漂移/限定；fail=结构性断裂且无兜底证据。

## 1. 定义

- 环节全名（图12）：冷热分层/压缩决策（契约驱动，结构上不可能产数 ✅），node_type=stage，build_status=partial，verified_scope=structure，wiring_status=decision_only。
- 职责一句话：本环节是 DSC-10B 的输入节点（决策 vs 执行），不是并列环节——契约参数（分层线/批限量/excluded_tables）驱动滚动归档执行；真源=data_retention_contract.yaml §rolling_archive+INV-RET-003/005。两死件（storage_tiering 裁定#383 纸面退役、data_compression_archiver 零调用方）已自 source_anchors 摘除（IN1-20 修剪）。
- 决策问句（图原文）：分层决策的真源件还活着吗？压缩比数据在哪里？

## 2. 六向台账

| 向 | 台账要点 | 文件路径证据 |
|---|---|---|
| 输入面 | 输入=契约文件本体（retention_lines_months/批限量/熔断阈值/kill switch）；无数据入边（决策件） | docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml（本批确认存在+被消费） |
| 输出面 | 输出=rolling_archive_reconciler 读契约限量执行（DSC-12→DSC-10B control 边）；压缩比度量=archive_manifest.jsonl 字段 compress_ratio（archiver 顺带产出） | config/data_supply_chain_map.yaml edges DSC-12→10B；F:/zephyr_cold/50_archive/by_project/zephyralpha/archive_manifest.jsonl（含 compress_ratio 字段，本批 tail 证实行结构） |
| SSOT 真源 | 真源=data_retention_contract.yaml（规则真源 YAML）；注意：总纲骨架原指 config/compression_policy.yaml 为本环节参数册——该件在盘（本批 ls 存在）但其消费方=validate_config_integrity/sync_blueprint_code_index/doc_compressor（均非本环节运行时），即骨架指针与图真源分叉，图侧换挂正确 | docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml；config/compression_policy.yaml（在盘，非本环节消费）；scripts/governance/d1_structure/validate_config_integrity.py（compression_policy 消费方 grep 实证） |
| 代码模块 | module_id=null/module_ref=null（决策件无执行体=合法）；两退役件在盘未摘：src/zephyr/data/storage_tiering.py（裁定#383 纸面退役）、src/zephyr/data/data_compression_archiver.py（零调用方）——"建成/在盘≠在岗"判例 | src/zephyr/data/storage_tiering.py；src/zephyr/data/data_compression_archiver.py（本批 ls 证实"在盘"事实） |
| 门禁约束 | load_contract_params 契约参数缺失即拒绝启动（decision_only fallback）；"本环节永远不可能用产数新鲜度标 ✅"（图原文）；退役件不得充当活锚（IN1-20 修剪纪律） | config/data_supply_chain_map.yaml#DSC-12 fallback/note_zh |
| 自动化触发 | decision_only：无运行面、无档期、无事件——执行面在 DSC-10B（事件触发）与 DSC-10A（人工） | config/data_supply_chain_map.yaml#DSC-12 wiring_status |

## 3. 自审闸三态

| 向 | 三态 | 判据（本批复核 2026-10-15） |
|---|---|---|
| 输入面 | pass | 契约文件实存且被 rolling_archive_reconciler/optimize_merge 消费（grep 实证） |
| 输出面 | pass | 决策经 control 边落地为 10B 执行（今日 manifest 在产=决策面间接活着）；compress_ratio 字段在 manifest 行结构中 |
| SSOT 真源 | warn | 图真源（data_retention_contract）正确，但总纲骨架仍写 config/compression_policy.yaml——骨架行与图节点指针分叉未回写（骨架 2.5 表 DSC-12 行原文"config/compression_policy.yaml"） |
| 代码模块 | warn | module_ref=null 合法，但两退役件在盘未物理摘除（裁定#383 判"物理摘除归后续批次"至今未执行）——纸面退役件持续承担误认风险 |
| 门禁约束 | pass | 契约缺失拒启+决策件不产数定性在册，双死件已摘出活锚面（IN1-20） |
| 自动化触发 | warn | decision_only=by design 无触发面；执行面节拍见 SDSC-10B（alive）——本格无独立可证触发，状态天花板 🔨 属实 |

## 4. 缺口与建议

1. 【warn 骨架对齐】骨架 §2.5 DSC-12 行的 SSOT 指针（config/compression_policy.yaml）与图真源（data_retention_contract.yaml）分叉：建议总纲下一版改挂契约真源（compression_policy.yaml 实为配置完整性校验面的参数册，另一域）。
2. 【warn 退役收尾】storage_tiering.py+data_compression_archiver.py 物理摘除归后续批次（裁定#383）至今未执行：建议排一个半日批做物理删除（或至少文件头加 RETIRED 横幅），终结"在盘即像活着"的误认源。
3. 【正向证据】"两件的建成/在盘都不等于在岗"判例（图原文）在本批复跑中再次成立：两件在盘、零消费方、执行面靠契约+reconciler 正常滚动。
