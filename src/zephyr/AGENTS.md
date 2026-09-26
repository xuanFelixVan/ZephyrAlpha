# src/zephyr 局部宪法（投影，立法权在根宪法）

- 本目录是什么：运行时源码根（30+ 子域包：trading/data/gov_enforcement/governance/security/frontend 等）。
- 真源指针：模块身份=PostgreSQL depgraph；门禁实现=`gov_enforcement/commit_gates/`（GateSpec 代码注册）；14 字段头部规范真源=trae_047。
- 禁止：裸 `duckdb.connect`/裸 SQL 散落——一律 `zephyr.infrastructure.database_service`（根宪法 §9 条目 1）。
- 禁止：裸 LLM API 调用——必经 `zephyr.security.llm_defense.llm_security.gateway`。
- 禁止：`governance/` 根新增 .py（CREATE-GUARD 拦截）；生成器里 `datetime.now()`/`time.time()`（RULE-SCHEMA-TZ）。
- 单口：查能力 `python -m zephyr.library.lookup <关键词>`。
- 单口：提交 `python scripts/git_commit.py --session <sid> --files <清单>`（禁裸 git commit）。
- 新建 .py 三件套：creation_token 登记 + 头部 30 行内 14 字段标注 + `add_module_translation.py` 大白话简介（三道 gate 独立拦截）。
- 冲突裁决：以根宪法为准；本文件仅局部提醒，不新增规则。
- 引用格式：引用根宪法用"根宪法 §N"字样。
