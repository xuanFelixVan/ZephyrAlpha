---
ttl: task_bound
title: J 段·AI 层链挖矿档（W3-3）
session: st-ffchief-20261001
date: 2026-10-01
status: mined
---

# J 段·AI 层链（F86-F96+F130，12 环节+1 Owner 门注）

> 方法同 SEG_I。运行态源=automation_panorama.md（10-01 快照）。
> 本轮要点：F88 LSG 挖干但**防御层数与拦截覆盖两口径漂移**；F87 redline **外部零消费**实锚；F130 ml_serve **7 py 全空壳**（骨架 11 py 口径失真）。

## 六向台账

| 环节id | 名称 | 上游 | 下游 | 生产者路径:行 | 消费者 | 自动化态 | 运行态 | 三态复核(骨架→本轮) |
|--------|------|------|------|--------------|--------|----------|--------|--------------------|
| J-01(F86) | AI 六族管线 | F96 | 演进闭环/L-02 | src/zephyr/ai_layer/ 9 子包（perceive/intake/cleaning/comparator/scheduling/switch_engine/heritage/redline/tools，ls 实测）；DDL=scripts/ai_layer/apply_ai_layer_scheduling_ddl.py:11(幂等)/:87(ai_work_order) | api_server.py:5393-5455 三端点、pipeline_events spawn（F82） | 事件 | DDL 部署运行态未证（脚本在 script-manifest.yaml:401） | 存疑(M4 DDL 未部署)→存疑——详见 F86.md |
| J-02(F87) | AI 红线 | 治理层 | F86 | src/zephyr/ai_layer/redline/ 9+ 件（drop_gate/negative_list/no_delete_manifest/sev_router/annual_review/ai_secret_exposure/negative_list_gates/dashboard_pipeline/freedom_weekly_report） | **外部零消费实锚**（全仓 grep 命中仅 redline 自身 6 文件） | 骨架称"事件" | 自封闭未接线 | 存疑→存疑（加重：消费面为零）——详见 F87.md |
| J-03(F88) | LSG 安全网关 | — | 全部 LLM 面 | src/zephyr/security/llm_defense/llm_security/gateway.py:139(LSGSecurityGateway)；:28-32 layers l0_supply_chain…l8_multi_agent（10 层模块实锚） | 25 文件/10 顶层域（grep -l 实测：ai_layer/autonomy_core/data/data_security/feedback_loop/governance/infrastructure/integration/orchestrator/security） | 常驻（横切） | 在岗（OllamaServe Running+10 域引用） | 挖干→挖干（两口径漂移：五层→L0-L8 十层；拦截面"4 库注记"→实测 10 域 25 件） |
| J-04(F89) | 本地模型与嵌入 | 模型源 | F86/F16 | data/capability_cards/{ollama_chat,embedding_router}.yaml（45 卡中 2 件，ls 实测） | LSG/嵌入消费面 | 定时（24/7） | ZephyrAlpha_OllamaServe Running（全景 §1.1） | 挖干→挖干 |
| J-05(F90) | Agent 编排与 A2A | F90 | 全链 | src/zephyr/orchestrator/（agent_orchestrator.py 等）+ autonomy_core/（**skills 64 件** ls 实测）+ integration/（api_gateway/llm_bridge 等） | 全链编排 | 事件 | autonomy_core/integration 常驻面在全景未单列（横切库形态） | 挖干→挖干（skills 数 60+→64 实测吻合） |
| J-06(F91) | 能力反查渐进披露 | — | 施工前置 | src/zephyr/governance/capability_lookup.py:892(def find)/:1077(find_files_by_module_path) | 施工 AI（宪法 RULE-CAPABILITY-LOOKUP） | 手动（施工时反查） | 随用随查 | 挖干→挖干 |
| J-07(F92) | 原问题账本 | F35 | 研究闭环 | src/zephyr/governance/meta_question/（snapshot.py/meta_question_registry.py/exam_ops.py/exam_loop） | 研究闭环/审计 | 事件 | 审计账 .runtime/chain_piling/meta_question_audit.jsonl=**1177 行**（审计有量）；"entry_count=0 空转"**未获代码/数据直证**（entry_count 全仓无代码锚；PG 三表量未核） | 存疑(P2)→存疑（空转判定证据不足）——详见 F92.md |
| J-08(F93) | PG 图书馆 | F92 | 知识面 | src/zephyr/library/（librarian.py/lookup.py/ledger_cache/ledger_fingerprint/ledger_schema/library_regen_reconciler/relations，7 件实测） | 宪法 §6 检索序 `python -m zephyr.library.lookup` | 事件+手动 | 在用（宪法入口） | 挖干→挖干 |
| J-09(F94) | 七段循环设计面 | — | F86 施工 | docs/_working/ai_layer_vision/L1_perceive…L7_heredity/DESIGN.md ×7（find 实测） | 施工批次 | **无**（design） | 纸面 | 存疑(design)→存疑(design)——详见 F94.md |
| J-10(F95) | OBJ 四对象设计面 | F94 | 施工批次 | docs/_working/ai_layer_vision/OBJ_{M_models,T_tools,S_perimeter,R_rules_standards}/DESIGN.md ×4（find 实测） | 施工批次 | **无**（design） | 纸面 | 存疑(design)→存疑(design)——详见 F95.md |
| J-11(F96) | 胃·全网搜索消化 | F31 | F20/F02 | scripts/backtest/lane_g_stomach_intake.py:70(parse_inbox_entries)/:97(build_extraction_prompt)/:117(load_seen_urls)；慢路径=scheduler.py:543-545（总闸 data/runtime/lane_g_intake_sweep.disabled） | F14 车道G 假说 | 事件（快路径 Popen+慢路径槽位兜底，scheduler.py:537-542 注记） | inbox 存量=2 件（index.md+intel-20260916.md，ls 实测） | 存疑→存疑（v0 在跑但存量稀薄）——详见 F96.md |
| J-12(F130) | ml_serve 模型服务 | J 段 | F19 数值族 | src/zephyr/ml_serve/ **7 py 且全为 `__init__.py` 空壳包**（find+ls 实测：api/core/infrastructure/models/services/_extensions 根） | 无 | 无 | 空壳 | 盲区(P1)→盲区坐实（骨架"11 py"口径失真，实为 7 全空壳）——详见 F130.md |
| 注 | knowledge 域（Owner 门） | — | — | src/zephyr/knowledge/（15 py，ls 实测） | 未定 | 未定 | 未定 | 盲区(Owner 门挂起，裁-6 与 F93 边界未裁)——不计号，维持挂起 |

## 段内小结

- 环节 12+注：挖干 5（F88/F89/F90/F91/F93）+ 存疑 5（F86/F87/F92/F96 + design 双件 F94/F95 计 2）+ 盲区坐实 1（F130）+ Owner 门 1（knowledge）。
- **新证据级发现**：F87 redline 外部消费=0（比骨架"存疑"更重）；F130 全空壳；F92 "entry_count=0" 无代码锚（审计账反有 1177 行）。
- F82 相关的 scheduling 子包接线证据在 ../I_scheduler/F82.md，不重复。
