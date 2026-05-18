"""[BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan-judge/blueprint.md


[MODULE] zephyr.orphan_judge


[INVARIANTS] 蓝图 §4 文件清单与代码双向对齐


[MODIFY-GUARD] orphan-judge/blueprint.md; orphan_judge/__init__.py __all__


[CONSUMERS] 见蓝图 §4 接口契约


[STABILITY] evolving


[SAFETY] M


[AI_AUTONOMY] ai_modifiable


[ERROR_CONTRACT] OrphanJudgeError


[TESTS] tests/orphan_judge/





orphan_judge — MOD-INF-029 · 孤儿审判器


========================================


蓝图: docs/03_modules/_cross_layer/orphan-judge/blueprint.md


actual_disk_path: src/zephyr/orphan_judge/





职责


----


  孤儿文件五层判定——L0 注册表对齐 / L1 引用图可达 / L2 功能覆盖


  / L3 代码价值 / L4 安全围栏


  整合自 runtime/orphan_detector.py





模块结构


--------


  orphan_detector     — 孤儿检测器(从 runtime/ 整合)


  five_layer_judge    — 五层判定引擎


  reference_graph     — 引用图引擎


  judgment_cache      — 判定结果缓存


  safety_fence        — 安全围栏(批量删除保护)


  incremental_scanner — 增量扫描引擎


  script_scheduler    — 脚本调度器


  mcp_handler         — MCP 调用治理


"""



from zephyr.orphan_judge.orphan_detector import OrphanDetector, OrphanReport





from zephyr.orphan_judge.orphan_detector import OrphanReport, OrphanDetector





__all__ = [


    "orphan_detector",


    "five_layer_judge",


    "reference_graph",


    "judgment_cache",


    "safety_fence",


    "incremental_scanner",


    "script_scheduler",


    "mcp_handler",


    "OrphanDetector",


    "OrphanReport",


]







