---
ttl: permanent
doc_type: blueprint
title: MOD-CHAINPILE-METAQ — meta_question_registry 原问题中央登记表基建蓝图
owner: ZephyrAlpha-Owner
session: st-chainpile-20260922
date: 2026-09-22
---

# MOD-CHAINPILE-METAQ 蓝图（极简登记件）

> 本蓝图是 depgraph 设计态节点（--add-design-node）的挂锚件。设计真源=定桩战役 W1 挖矿包（docs/_working/chain_piling_campaign/infra_mining/ 五份），此处只做挂锚与索引，不重复设计内容。

## 模块构成

| 件 | 路径 | 粒度 |
|----|------|------|
| 写入 API | src/zephyr/governance/meta_question/（registry.py/snapshot.py/__init__.py） | module |
| DDL 部署器 | scripts/governance/apply_meta_question_ddl.py | file |

## 状态

- W2 施工：代码+测试 38 passed（2026-09-22，见战役台账 a1）
- DDL 部署：待本蓝图同批裁定追认后执行 `python scripts/governance/apply_meta_question_ddl.py`
- 设计真源：10_intake_gate_design.md（API 契约）/30_blindspot_audit.md C 章（schema 收口 R1-R6）/20_management_policy.md（审计与权限）
