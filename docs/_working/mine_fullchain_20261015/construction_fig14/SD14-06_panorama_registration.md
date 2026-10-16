---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-06
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-2-全景图登记设计态先行 + 附录 D 锚块
---

# SD14-06 全景图登记·设计态先行（policy Step 2）

## 1. 定义

Step 1.8 通过（或豁免）后触发：apply_depgraph.py 登记模块依赖到设计态 status=planned + 模块准入四级筛选（MAD-001~005：层归属/Phase 相关性/依赖合规/接口来源/P0 额外条件）。L1 铁律=写第 1 行业务代码前必须已登记设计态，禁"先施工后补登记"；L2 铁律=写入设计态前确保运营态已就绪。禁直接 SQL 写 depgraph（必须走 apply_depgraph.py）；架构升级期禁跑 generate_project_depgraph.py --force。本段是全图 6 个 verified_scope=production 之一（骨架 ✅）。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | Step 1.8 通过/豁免结论；设计备忘（蓝图 ID/依赖关系）；运营态就绪读数 | 政策 L270-296；图 rollback/fallback 条款 |
| 输出面 | depgraph planned 节点+设计态边（存储=PostgreSQL depgraph.nodes，key=module_id） | 图 store_refs（图 YAML #D14-06）；`scripts/governance/apply_depgraph.py#--add-design-node/--add-design-edge`（本批 grep 选项集实证命中） |
| SSOT 真源 | `trae_080_panorama_alignment.yaml#panorama_alignment` + `trae_056#phase_2_design_state` + `trae_032#mod_001` + `trae_054_depgraph_access_protocol.yaml` | `docs/01_policies_and_standards/rules/` 四件 |
| 代码模块 | `scripts/governance/apply_depgraph.py`（module_id=MOD-GOV_SCRIPTS）——本批实证含 --add-design-node/--add-design-edge/--add-edge 等选项；**无 --query-production 选项**（全选项集 grep-i query 零命中，D14-G05 实证成立） | 同左 |
| 门禁约束 | `DEPGRAPH-ENFORCEMENT`（in_process+gate_registry 双册）+ `DEPGRAPH-PRE-REGISTRATION`（gate_registry 在册）+ `NEW-FILE-DEPGRAPH-ENFORCEMENT`（gate_registry 在册）——三台本批 grep 实证（分工：1 台网关内联+2 台 pre-commit 通道） | `docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`；`.../gate_registry.yaml` |
| 自动化触发 | apply_depgraph 执行后默认自动触发 sync_panorama_module 派生三图；生成器重建时 restore_design_data 保护设计态节点（`scripts/governance/generate_project_depgraph.py` §restore_design_data）；提交期三台 gate 拦未登记新建 | 政策 L295；图 YAML #D14-06 gates |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 前置链条（D14-02/03/04/05）接口清晰 |
| 输出面 | pass | planned 节点+边落 PG 存储面在册，CLI 选项实证 |
| SSOT 真源 | pass | 四规则册在册，锚块 D14-06 在册 |
| 代码模块 | pass | apply_depgraph 选项集实证（含两 design 选项） |
| 门禁约束 | pass | 三台 gate 双册实证在册 |
| 自动化触发 | pass | sync 自动派生+restore_design_data 保护+提交期拦截三层 |

## 4. 缺口与建议

- 缺口1（D14-G05）：L2 铁律"写入设计态前确保运营态已就绪"的 `--query-production` 选项不存在（argparse 直接拒绝）。建议：按 G05 note 补法——复用既有只读通道（DatabaseService 程序化直查或 generate+diagnose 现算），不新造选项（净零）；政策 L293 已带 R-04 更正注记，锚块应同步。
- 缺口2（D14-G06）：模块准入四级筛选的留痕宿主 `module-id-registry.json` 全仓不存在（本批根目录核验），现行留痕=depgraph 设计态节点+任务卡/ARCH 条目（政策 L285-286 已自报 R-05）。建议：裁定唯一留痕面（推荐任务卡 admission 字段或 ARCH 条目），删政策对幽灵件的指认。
- 缺口3：三台 gate 分散两册（1+2），own-diff 作用域按 gate_registry own_scope 字段——建议保持，但政策 Step 2 散文应注明分工，防误以为三台都在网关内联。
