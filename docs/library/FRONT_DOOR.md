---
ttl: permanent
doc_type: index
generated_by: scripts/governance/generators/generate_front_door.py
---

<!-- GENERATED FILE — regenerate: python scripts/governance/generators/generate_front_door.py && git diff --exit-code；手改必被覆盖 -->

# ZephyrAlpha 前台门口（FRONT-DOOR）

> 使命：任何 AI/人从本页出发，最多 2 跳抵达任意资产真源。本页是派生视图，真源见各链接；先单口后 Grep，路径禁凭记忆书写（根宪法 §8）。

## 查询五单口

| 你要找 | 唯一入口 | 备注 |
|---|---|---|
| 能力/文件/模块（关键词） | `python -m zephyr.library.lookup <关键词>` | 全馆在编资产；表级真源暂走下行数据册（缺口移交 S5） |
| 注册表（哪个册管什么） | `docs/registry_of_registries.yaml`（ROOR）；册数总索引=`docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml` | 注册表发现唯一真源；总数以字段为准勿背数 |
| 模块/依赖全景 | `python scripts/governance/extract_depgraph.py --summary` | PostgreSQL depgraph，禁裸连 |
| 全图全库对齐 | `alignment_checklist.md`；`python scripts/governance/align_all.py` | 对齐键=module_id/step_id |
| 数据表真源 | 表名 grep `docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml`（REG-DATAFLOW-001）；库连接走 `zephyr.infrastructure.database_service` | lookup 暂不索引表名 |

## 图书馆七馆（计数由生成器注入，勿手填）

| 馆 | 页 | 在编数 |
|---|---|---|
| 代码馆 | docs/library/code.md | 28000 |
| 数据馆 | docs/library/data.md | 345 |
| 文档馆 | docs/library/doc.md | 5458 |
| 制度馆 | docs/library/rule.md | 88 |
| 闸门馆 | docs/library/gate.md | 303 |
| 管线馆 | docs/library/pipeline.md | 89 |
| 基建与备份馆 | docs/library/backup.md | 0 |

## 高频紧急路径

| 场景 | 直达 |
|---|---|
| 宪法（必读 L0） | `AGENTS.md`（IDE 同时注入 `.trae/rules/project_rules.md`） |
| 门禁定义 | commit 门=`src/zephyr/gov_enforcement/commit_gates/`（代码 GateSpec 注册）+ 机生总册 `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`；规则管线门=`src/zephyr/gov_enforcement/rule_enforcement/_registry.yaml` |
| 提交 | `python scripts/git_commit.py --session <sid> --files <清单>`（禁裸 git commit；锁忙走 `scripts/commit_queue.py --enqueue`） |
| 编辑消失/告警 | 先查 `.runtime/workspace_alerts/stash_notice.json`（stash 保存非丢失）；reaper 状态 `python -m zephyr.trading.process_reaper --status` |
| 新建文件 | 先 creation_token（`scripts/governance/d3_metadata/batch_creation_tokens.py`），再写；7 格式全覆盖（tests/ 豁免） |

## 十年机制五支柱（一行索引；真源=根宪法与本战役骨架）

1. 棘轮：坏指标只降不升，存量入基线豁免。2. 单写者：每类事实一个真源平面，读侧唯一入口=图书馆 lookup。3. 生成闭环：生成物必过 `regenerate && diff --exit-code`。4. 生命周期隔离：永久区禁引临时区（根宪法 §9 条目 4）。5. 墓碑去向：死亡资产留 successor_of 指针。

## 维护说明

- 本页由 generate_front_door.py 从 ROOR/registry_master_index/INDEX.md/根宪法 §7 派生，禁手改。
- 发现本页与真源不一致 = 立即 regenerate；仍不一致 = 真源有病，修真源而非本页。
