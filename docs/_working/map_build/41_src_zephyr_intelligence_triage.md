---
ttl: task_bound
completes_when: 孤儿分诊战役终裁落地（chief 终审+处置执行）后本册随 30/31 号转归档
title: 孤儿分诊证据包：src.zephyr.intelligence（53 台）
owner: st-orphtriage-20261004
---

# 41 号·分诊证据包：src.zephyr.intelligence（53 台）

> 宇宙口径=裁定#481；数据真源=30_attribution_table.yaml（join checker 机生）；处置=证据班建议，终裁归 GLM-5.3 chief，退役执行归 Owner 门位。
>
> tier 分布：suspect_orphan=7，wired=27，wired_by_header=19；初判汇总：dispute=7，mount=46

## 逐台证据（四字段+初判）

| file | 干什么的 | last_commit（距今） | import 信号 | 初判建议 |
|---|---|---|---|---|
| `src/zephyr/intelligence/_extensions/__init__.py` | intelligence/_extensions | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 intelligence 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/intelligence/api/__init__.py` | intelligence/api | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 intelligence 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/intelligence/core/__init__.py` | intelligence/core | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 intelligence 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/intelligence/infrastructure/__init__.py` | intelligence/infrastructure | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 intelligence 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/intelligence/model_evaluation/target_lib/__init__.py` | （无文档头，按文件名语义：__init__） | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 intelligence 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/intelligence/models/__init__.py` | intelligence/models | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 intelligence 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/intelligence/services/__init__.py` | intelligence/services | 2026-09-16（18天） | in=0/out=0·suspect_orphan | **dispute**（suspect_orphan 但 18 天内有 commit（活着但零线零引）；①mount→chief 判（域 intelligence 无预设映射） ②retire→Owner 门位） |
| `src/zephyr/intelligence/__init__.py` | Intelligence Domain | 2026-09-23（11天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/canonical_hash.py` | canonical_hash — 规范化 JSON sha256 公共底座（判据冻结/防篡改指纹共用）。 | 2026-09-26（8天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/event_anomaly_detector.py` | MOD-INT-EVENT-ANOMALY — 异动识别器（国盛证券异动雷达 2026-03 施工化，26 号 §2.5）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/event_chain_causal_graph.py` | EventChainCausalGraph — 事件链推理因果图（MOD-INT-EVENT-CHAIN）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/event_dragon_tiger.py` | MOD-INT-EVENT-DT — 龙虎榜佐证修正因子（26 号 §2.5 v1.8.0，2026 失效校准）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/event_factor_matrix.py` | MOD-INT-EVENT-FACTOR — 事件驱动六因子矩阵数值项（26 号 §2.4 v1.5.0 施工化）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/event_geopolitical_map.py` | MOD-INT-EVENT-GEO — 地缘/宏观事件→A 股板块受益传导链（26 号 §2.5b 施工化）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/event_ipo_siphon.py` | MOD-INT-EVENT-IPO — IPO 虹吸效应量化算法（26 号 §2.5a 施工化）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/human_trust_model.py` | HumanTrustModel — 人机信任模型（MOD-INT-HUMAN-TRUST）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/llm_research_agent.py` | LlmResearchAgent — LLM 研究助手（MOD-INT-RESEARCH-AGENT）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/llm_self_evaluation.py` | LlmSelfEvaluation — LLM 自评估与交叉验证（MOD-INT-LLM-SELFEVAL）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_drift_detector.py` | ModelDriftDetector — LLM 模型行为漂移检测。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_evaluation/__init__.py` | Intelligence — Model Evaluation Domain | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_evaluation/_memory_backend.py` | Backend protocol & shared data classes for the unified memory layer. | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_evaluation/implementations/default_inference_engine.py` | D_INTELLIGENCE — Default Inference Engine（兼容 shim） | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_evaluation/inference_base.py` | MIGRATED: SSoT moved to zephyr.ml_train.trainer_base and zephyr.ml_train.inference_base | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_evaluation/reranker.py` | Cross-Encoder 重排序层 — BGE-reranker-v2-m3 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_intel/__init__.py` | model_intel — OBJ_M M1 模型情报扫描包：情报卡 schema+四闸校验+simhash 查重（intel_card）；源注册表读取+抓取+diff 建卡（scanner）。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_intel/intel_card.py` | intel_card — M1 情报卡 schema 与四闸校验（OBJ_M DESIGN §2.3）。 | 2026-09-26（8天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_intel/scanner.py` | scanner — M1 情报源扫描器：读源注册表→抓取→价快照 diff→建卡→四闸校验→simhash 去重→落 JSONL。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/__init__.py` | Model Profiling — 本地 + 远程模型性能基准测试 | 2026-09-18（16天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/benchmark_suite.py` | BenchmarkSuite — 多维度模型性能测试用例集 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/case_assembler.py` | 真实多文件注入装配器（Phase 3 极限深度）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/cli.py` | model-profiler.cli — 模型性能检测命令行入口 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/dual_run.py` | dual_run — M3 同任务双跑执行器（纯函数库，DESIGN §4.2/§4.4）。 | 2026-09-26（8天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/exam_checks.py` | exam_checks.py — 考试检测纯函数模块（Stage 4 试点：从 exam_orchestrator 提取） | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/exam_judge.py` | ExamJudge --- LLM-as-judge 评分器 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/exam_rubric.py` | ExamRubric --- 奥赛题结构化多维清单评分（v3.0.5）。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/exam_test_cases.py` | ExamTestCases --- v3.0.5 扩展考试题库（96 题 / 29 能力 / 5 难度） | 2026-09-16（18天） | in=5/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/model_discovery.py` | ModelDiscovery — 枚举所有本地 Ollama 模型 + 远程 API 模型 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/profiler.py` | ModelProfiler — 核心性能分析引擎 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/provider_data.py` | （无文档头，按文件名语义：provider_data） | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/results_writer.py` | Results Writer — 持久化 benchmark 结果，支持历史对比（漂移检测） | 2026-09-16（18天） | in=4/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/model_profiling/task_model_learner.py` | ModelTaskMatrix — 任务×模型性能学习引擎 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/__init__.py` | 自反Agent 包 —— 12号文 Phase 0(P0-1~P0-4) + Phase 1(P1-1/P1-2/P1-3)。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/batch_runner.py` | 盘后批量反思入口 —— 12号文 §4.2 P0-4(手动+计划任务挂点)。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/l1_reflector.py` | L1 单轨迹反思器 —— 12号文 §4.2 P0-3(执行层, 触发频率最高/成本最低)。 | 2026-09-16（18天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/preflect_store.py` | PreFlect 失败模式库（12号文 §3.3/§4.3 P1-3）. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/reflctrl_gate.py` | ReflCtrl 反思频率闸门（12号文 §3.4/§4.3 P1-1）. | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/reflection_schema.py` | 反思记录 Schema —— 12号文 §4.2 P0-1 结构化反思记录契约。 | 2026-09-16（18天） | in=5/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/roles.py` | 三角色骨架 —— 12号文 §3.2/§4.2 P0-2(Actor→Evaluator→SelfReflection)。 | 2026-09-16（18天） | in=3/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/reflexion/vote_review_shell.py` | 投票评审壳（12号文 §3.6/§4.3 P1-2）——可选模式设施，人手动触发. | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/sentinel_hallucination_detector.py` | sentinel 幻觉检测器（MOD-INF-050）——intelligence 域哨兵封装。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/switch_engine/criteria.py` | criteria — L6 判据预注册 YAML 加载器 + sha256 冻结哈希（S2 施工件）。 | 2026-09-26（8天） | in=2/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/universal_fact_ledger.py` | UniversalFactLedger — 通用事实账本与双重锚定（MOD-INT-FACT-LEDGER）。 | 2026-09-16（18天） | in=0/out=0·wired_by_header | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
| `src/zephyr/intelligence/venra_double_lock_anchor.py` | VENRA 双锁锚定器（MOD-INF-049）。 | 2026-09-16（18天） | in=1/out=0·wired | **mount**→chief 判（域 intelligence 无预设映射）（活线在身未挂线） |
