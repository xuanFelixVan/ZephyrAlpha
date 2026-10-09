---
ttl: permanent
doc_type: index
---

# docs/03_modules 局部宪法（投影，立法权在根宪法）

- 本目录是什么：全项目模块蓝图区——每模块一 blueprint.md（设计态叙述真源）+ algo_flow 机械视图。
- 真源指针：模块身份/依赖=PostgreSQL depgraph（读走 extract_depgraph.py，禁裸连）；本目录文件清单=docs/library/doc.md 馆页。
- 禁止：手改 `_domain_*/algo_flow/` 与 `algo_flow/*.yaml`（机生视图，手改必被覆盖）。
- 禁止：绕过 scaffold 新建模块；在 blueprint 里写计数散文（计数用字段，根宪法 §4.3）。
- 单口：查模块 `python -m zephyr.library.lookup <模块名>`。
- 单口：提取 `python scripts/governance/extract_depgraph.py --summary`；登记 `python scripts/governance/apply_depgraph.py --add-design-node`。
- 重命名：`git mv` 后 commit 前 MUST `python scripts/governance/generate_project_depgraph.py --force`（RENAME-DEPGRAPH-SYNC 硬拦）。
- 冲突裁决：本文件与根宪法冲突时，以根宪法为准；本文件仅局部提醒，不新增规则。
- 引用格式：引用根宪法用"根宪法 §N"字样（勿写 "AGENTS.md §N"，防悬空引用门误判）。
