---
ttl: task_bound
title: "NB1 B3 裁定卡：ml_serve 四件+model_drift_monitor（已净删·归档在册）——融合/储备终审"
session: st-nightsweep2-nb1-20260930
updated: 2026-09-30
---

# B3 机器学习服务 ml_serve 四件 + model_drift_monitor · 价值挖矿裁定卡

## 事项

Owner 点名"不能因为没人用就删"。对象：src/zephyr/ml_serve/ 四实体件（codegen_model_adapter 16.4KB / deep_review_model_adapter 17.5KB / model_compression_accelerator 14.1KB / core/model_drift_monitor.py 269 行 10.0KB）+ 双同名件 model_drift_monitor（ml_serve 269 行 vs gov_drift 68 行）。
**现场状态（本夜实测）**：SW5（794f16569b）已按 F130 案卷落退役标记；st-finaldel-retire（5ccc4c3cf1+42d286d116，2026-09-30 02:52）已物理净删 8 件（4 src+4 tests），先归档后删。本卡=追认复核+终审，非新裁。

## 六向台账快照

| 向 | 实测 |
|---|---|
| 通道 | F130 案卷（docs/_working/fullconnect_campaign/j_ai_design_gates/13_f130_ml_serve_adapters.md）→ SW5 退役标记 → C267a 物理净删（Owner 已批"先归档后删"） |
| 原料 | 归档真身：G:/zephyr_cold/retire_c267_20260930/F130_ml_serve/（同构镜像+逐件 sha256=MANIFEST.md，8 件 0 差异）；git 史 5ccc4c3cf1^ 可复现全文 |
| 状态 | 包壳 ml_serve/ 7 件 __init__ 仍在（204 行，[DEPRECATED]+successor=F129 ml_train 注记在）；四实体件已删；ZA-MLS-0001..0004 错误码随净删标 deprecated（a937e4c9c3） |
| 消费方 | 净删前 AST PROD=0/TC=0（F130 复核勘误：tests 4 件实消费，已随净删）；serve 现役=F129 ml_train（model_version_registry+default_inference_engine，后者被 intelligence/model_evaluation/implementations/default_inference_engine.py:36 真实消费） |
| 缺口 | ①登记面 5 册 52 条 dangling 引用待维护班官方通道清理（module_translation 17/candidate 10/capability_canonical 18/functional_domain 3/wiring 4）；②被删 269 行 model_drift_monitor 的设计能力（serving 四维漂移）在仓内无继任——gov_drift 68 行仅是配置表非检测器 |
| 处方 | 见下"三态裁定"：储备已执行✅+融合处方（复活落点=ml_train 非 ml_serve） |

## 三审结论

1. **价值审（通过，且高）**：被删的 core/model_drift_monitor.py（MOD-MLS-001，蓝图背书）=serving 模型**四维漂移检测**（PSI 输入特征/JS 散度输出分布/性能衰减/IC 衰减）+E-OP-02 域事件，纯内存确定性、阈值 warn<critical 强制、event_sink/clock 全注入、Fail-Closed（ZA-MLS-0002）。Owner 方向正确：量化系统未来接自训模型（qwen25-7b LoRA 已在产=C22 销账实证 ml_train 活）必有 serving 漂移监控需求。**全网佐证**：Evidently/alibi-detect/NannyML 只覆盖 PSI/JS/KL 通用分布漂移，"PSI+JS+性能衰减+IC 衰减"四维合一的量化 serving 监控无现货（IC 衰减全行业自建）——被删件是差异化设计非重复造轮。但同包另三件（codegen/deep_review 适配器、压缩加速器）是"未启用第二实现族"（真实 LLM 调用腿走 LSG/F88），无独占价值。
2. **真源唯一性审（通过）**：仓内三件漂移族各有其物——gov_drift/detector_core/model_drift_monitor.py（68 行，存活）=治理漂移配置表（CONCEPT/DATA/PREDICTION 三条 DriftConfig）；intelligence/model_drift_detector.py（169 行，MOD-INF-021）=LLM 输出分布基线漂移（exit 34）；被删 ml_serve 件=serving 量化模型四维。三者对象不同不并（宪法 §4.2 跨域不同对象）；"改错包"风险已由 successor 注记+F129 真源声明对冲。双同名 clone 以"归档留证=事实消解"收口（clone_guard 尺判定被归档动作代偿）。
3. **数据持续性审（数据类：不适用→事件类）**：漂移监控消费推理样本流，当前无 serving 流量=无持续数据；按 Owner 判据应"退役到能储备"。已储备于 G 盘（可 sha256 复核随时复活）。

## 三态裁定建议

**【储备·已执行】+【融合·附处方】（零删除追加动作）**：
- 储备：G:/zephyr_cold/retire_c267_20260930/F130_ml_serve/（8 件 sha256 在册）——维持现状，勿再动。
- 融合处方（复活条件触发时执行，落点=F129 ml_train 包内，**不重建 ml_serve 包**）：①触发条件=Owner 判"J 段 serve 需独立推理服务"或 ml_train 灰度发布（gray_release_shadow_deployer）上量；②动作=从归档取 model_drift_monitor.py（sha256 4ce61ec9…），剥离 ml_serve 包头改为 ml_train/core/model_drift_monitor.py，event_sink 接 E-OP-02 事件总线（infrastructure/events），阈值走 ml_train 现役 model_version_registry 键控；③同批在 module_translation/candidate 两册补"复活迁移"条目冲销 dangling；④红样先行：归档 tests 4 件同取，改 import 路径后须全绿再接。
- 附带：5 册 52 条 dangling 引用清单移交维护班（勿由本车道越权清册）。

## 自审闸三态

**挖干（置信度=高）**。可复算：净删两 commit（5ccc4c3cf1/42d286d116）+归档 MANIFEST 逐件 sha256+被删件全文（git show 5ccc4c3cf1^）+两存活件现读+F130/F129 案卷对照+全网三库（Evidently/alibi-detect/NannyML）无四维合一现货。未干残余：三适配器/压缩件**未逐行读实现体**（其"无独占价值"判自 F130 案卷的 PROD=0+同族对照，非本夜逐行重读）——若 Owner 翻案要求复活适配器族，须先补逐行尽调。
