---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-12
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-7-更新施工文档 + 附录 D 锚块
---

# SD14-12 更新施工文档（policy Step 7）

## 1. 定义

Step 6 长清单审查通过后触发：设计备忘 frontmatter 升版（status→active/version+1/last_updated）+正文"已施工（commit XXXXX）"标注+已施工设施盘点补模块路径+00_index 同步+跨蓝图变更通知（RULE-ELEVEN 三步：Grep 消费方→同步更新→端到端验证）。配套：文档规格化三清单（可删 11/不可删 18/必须补 10 类）、纯陈述原则、删除安全门禁三问三步、架构版本化 X.Y.Z。wiring=partial。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 审查通过+遗留项已登记；设计备忘本体 | 政策 L484-509；图 rollback_to=D14-09（文档代码漂移回施工，回边 B11） |
| 输出面 | 更新后的设计备忘+00_index——**两目标件已整体归档**（`00_index_trading_decision.md` 随裁定#384 归档至 `docs/_working/archive/2026-09/design_memos/`；活跃施工文档索引面现由各册 index.md 与 alignment_checklist.md 承担，政策 L494 自述） | 政策 L494；D14-G12 ghost_refs 五件（design_memos 旧路径全不在原位，本批归档侧实证） |
| SSOT 真源 | `01_design_memo_management_spec.md §5.3`（归档侧）+`trae_052#rule_eleven`+`trae_030#GOV-DOC-011/016/017`+`trae_029`（删除三问三步）+`trae_037#GOV-ARCH-003`（版本化） | `docs/_working/archive/2026-09/design_memos/01_design_memo_management_spec.md`；rules 四件在册 |
| 代码模块 | `scripts/governance/d5_architecture/validators/lifecycle/validate_module_lifecycle.py`（module_ref，在盘）+`scripts/governance/d8_doc_sync/update_progress.py`+`scripts/governance/d8_doc_sync/auto_sync_all_registries.py`（三件本批 ls 实证） | 三件在盘 |
| 门禁约束 | `TTL-METADATA`+`FILE-PLACEMENT-TTL`（双册在册，本批 grep 实证）；断链阈值（生产≤100/过渡≤500） | 两册；trae_029 |
| 自动化触发 | auto_sync 面在盘（d8_doc_sync）；workspace_hygiene_reconciler post-commit 自动还原派生文件；checklist 第 15 项=commit_derived_sync.py 派生残留收口 | 政策 L808（checklist 15） |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 审查通过链条闭合 |
| 输出面 | warn | 判据"三处对齐+索引同步"的两目标件已归档——不是没人做，是目的地没了（图 note 原文）；活跃替代面（册 index/alignment_checklist）未回写进政策判据 |
| SSOT 真源 | warn | 管理规范真源在归档侧（D14-G12）；rules 四件在册正常 |
| 代码模块 | pass | 三执行件在盘实证 |
| 门禁约束 | pass | 两台 gate 双册在册 |
| 自动化触发 | warn | 派生收口/reconciler 自动面在盘，但"整体文档对齐"无单一机械判据 |

## 4. 缺口与建议

- 缺口1（D14-G12 主宿主段）：设计备忘体系整体搬家（49 件归档）早于政策改版 5 天未跟进，全仓大批文件引旧路径。建议：总包裁定设计备忘体系存续性（invalidation 条款原文："被裁定为终止⇒本段判据须改写"）——若终止，本段改写为"活跃施工文档=各册 index.md+alignment_checklist"；若存续，从 archive 复活管理规范至永久区。
- 缺口2：RULE-ELEVEN 跨蓝图通知的 STEP3"端到端测试验证"无机械判据。建议：并入 D14-10 测试面清单纪律（消费方测试进清单）。
- 缺口3：00_index 替代面（各册 index.md）无生成器统一保障——静态清单禁手工维护红线（宪法 §9.5）风险点。建议：核对各册 index.md 是否已有机生通道（`python -m zephyr.library.lookup` 面），无则补。
