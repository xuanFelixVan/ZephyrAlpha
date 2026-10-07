---
ttl: task_bound
completes_when: 镜像树迁移 W0 备料定版并按 C490 裁定开工 R1-R3 试点批
created: 2026-10-07
sid: st-mastertc-l9
status: W0 备料重建（登记不执行迁移）
reconstruction: 备料簿原件蒸发（未落地即失），本件为 W0 先写者改造方案重建版
---

# M3 镜像树迁移 · W0 备料簿（重建版）

> 依据：裁定#488 B 段「C490 镜像树迁移批 W0+165GiB 豁免按归档处方批」；规格真源=domain_naming_rules.yaml NR-006..010（#ARCH-360 已落册）+ S3 簿 §4.1/§4.3。
> 本簿只备料+登记，**不执行任何迁移**（执行=R1-R3 试点批，另开施工会话）。

## W0 先写者改造方案（30 行判据+批次模板）

### 1. 现态计量（check_mirror_tree.py 2026-10-07 实测，只读）

- src/zephyr 顶层包 57；包级文档覆盖 56/57=98.2%；**镜像位精确命中 0/57=0.0%**。
- 体系 B yaml 认领 3364 件全部非镜像位（=R4 迁移积压 3364，与 09-27 首测 3295 同口径增长）；同源双目录漂移 2 源文件/8 包。

### 2. 判据（每批迁移的放行门，四条合取）

1. **批前**：目标包在 NR-006 映射函数 M 下逐一可解析（`resolve_doc_path` 单写者，禁改名典）。
2. **批中**：git mv 同 commit 完成 S3 §4.3 R2 四连（锚行重写+doc 归位镜像位+`generate_project_depgraph.py --force`+index/ownership regen），缺一即回滚整批。
3. **批后**：`regenerate && diff --exit-code` 零漂移 + check_mirror_tree 镜像位覆盖数严格递增（棘轮只增不减）+ GATE-ALGO-FLOW/algo_flow_link_gate/RENAME-DEPGRAPH-SYNC 全绿。
4. **回退**：任一门红 → 整批 revert（一批一 commit，禁跨批混交）。

### 3. 批次模板（每批一行登记，照抄填空）

```
| 批次 | src包 | 文件数 | commit | 镜像位覆盖(前→后) | 四连验证 | 棘轮增量 | 红蓝门 |
| R3-1 | runtime | 2  | <hash> | 0→1/57 | pass | +2 | green |
```

- R1（零风险首波）：体系 A 残件 2 件墓碑化（MOD-ALT-EMOTION-INDEX-BUILDER.md / MOD-CHAINPILE-METAQ/）+ blueprint_registry 死指向清偿。
- R3（试点三包，验证工具链）：runtime(2)/red_blue_validator(1)/infra_ops(5)，全链 regen-clean 双向通过才放大。
- R4（后波，按包升序）：首批积压读数见 §1 分布表（feedback_loop 340 最大）；同包双目录先并筒（_domain_plan→_domain_plan_engine、_domain_portfolio_alloc→_domain_pf_alloc）。
- R5 硬前置：S7 regen-clean 框架就绪，不满足则停在 R3（S3 簿 §4.3 原判据）。

### 4. 本夜边界

迁移零执行；165GiB 归档豁免按 #488 归档处方归总筹/数据车道，本簿不碰盘面。
