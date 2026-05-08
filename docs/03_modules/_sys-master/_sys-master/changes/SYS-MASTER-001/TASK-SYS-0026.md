---
task_id: "TASK-SYS-0026"
source_blueprint: "SYS-MASTER-001"
source_section: "§37 模型漂移监控 + §42 量化ML工程 + §85 经济体制检测与宏观因子"

title: "模型漂移三型监控(概念漂移IC/数据漂移KL/预测漂移Sharpe) + 量化ML工程全链路(特征存储/训练推理分离/6项数据泄漏检查/HMM) + 经济体制五维宏观因子(增长/货币/通胀/信用/风险偏好)体系搭建"
description: |
  将 §37 模型漂移监控 + §42 量化ML工程 + §85 经济体制检测三合一落地为ML管线完整性锚点。
  §37 定义 3 种漂移检测：
  （1）概念漂移（Concept）——Factor IC 30日滚动均值下降 > 1σ → 因子审查（§65）。
  （2）数据漂移（Data）——市场数据分布变化（KL散度 > 阈值）→ 重新训练。
  （3）预测漂移（Prediction）——Sharpe 30日 < 0 → 策略退役评估（§50）。
  §42 定义：
  （1）特征存储 SQL——symbol/date/factor_name/value/computed_at（PRIMARY KEY symbol+date+factor_name）。
  （2）训练/推理分离——Training Pipeline（历史数据 2016-2024 → 因子计算 → 模型训练）vs Inference Pipeline（实时数据 → 因子计算 → 模型预测）→ 严禁训练时 access ≥ inference dated→防Look-ahead bias。
  （3）数据泄漏六项检查：①因子计算日期>行情日期?永不·②训练/测试时序交错?训练<测试·③未来数据可达因子Store?不可达·④Factor analysis用了未来IC?用历史IC only·⑤组内信号提前?延后1日·⑥财报/拆分日期ex-ante vs ex-post?ex-ante only。
  （4）HMM 市场状态切换——隐状态=3（牛市/震荡/熊市）自动切换策略权重。
  §85 定义 5 维宏观因子框架：
  经济增长（PMI/GDP nowcast/工业用电）· 货币政策（Fed Funds/央行资产负债表/利率期货隐含概率）· 通胀（CPI/PCE+TIPS盈亏平衡+商品指数）· 信用条件（HY-OAS/IG spread/CDX）· 风险偏好（VIX term structure/SKEW/资金流动）。
  4 种宏观体制映射：扩张（Momentum+Growth+SmallCap）/滞胀（Commodities+Quality+LowVol）/紧缩（Cash+ShortDuration+Defense）/危机（Cash+Gold+Volatility long）。
  体制切换预警 4 信号→ 3/4 触发 = 体制切换预警。
  本卡搭建 model_drift_monitor.py + ml_engineering.py + regime_detector.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\model_drift_monitor.py"
    description: "§37 3型漂移——概念漂移(IC 30日均值>1σ)/数据漂移(KL散度)/预测漂移(Sharpe 30日<0)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ml_engineering.py"
    description: "§42 特征存储SQL + Training/Inference分离 + 6项数据泄漏检查 + HMM 3状态切换"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\regime_detector.py"
    description: "§85 5维宏观因子(增长/货币/通胀/信用/风险偏好) + 4体制映射 + 切换预警4信号"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\model_drift_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\ml_engineering.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\regime_detector.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§37 概念/数据/预测漂移 + §42 特征存储/训练推理分离/6泄漏检查/HMM + §85 5宏观因子/4体制/切换预警"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 24000
timeout_minutes: 65

acceptance_criteria:
  - "model_drift_monitor.py 实现 DriftDetector——concept_drift（IC 30日滚动均值 tracking→diff>1σ→flag）· data_drift（KL divergence market dist vs baseline→>threshold→retrain）· prediction_drift（Sharpe_30d<0→retirement assess）——output drift_alert with 类型+阈值+建议"
  - "ml_engineering.py 实现 FeatureStore——schema(symbol,date,factor_name,value,computed_at) PRIMARY KEY· TrainingPipeline（历史2016-2024→因子→训练）· InferencePipeline（实时→因子→预测）——enforce(训练data < 推理data)时间墙"
  - "ml_engineering.py 实现 LeakageAudit——6项检查清单(日期时序/因子Store可达性/历史IC only/信号延后1日/ex-ante财报)→逐项 PASS/FAIL→任何FAIL=阻断"
  - "ml_engineering.py 实现 HMMStateDetector——3隐状态(牛市/震荡/熊市)→自动切换策略权重"
  - "regime_detector.py 实现 MacroFactorFetcher——5因子(经济增长/货币/通胀/信用/风险偏好)→各自代理指标(PMI/FedFunds/CPI/HY-OAS/VIX)→合成→ RegimeClassifier 输出(扩张/滞胀/紧缩/危机)+probability"
  - "regime_detector.py 实现 RegimeSwitchAlert——4信号(信用利差扩大+1σ/VIX期限结构倒挂/国债利差异常/央行转向)→≥3/4→预警→策略权重重校准+Owner通知"
  - "script_manifest.yaml 注册全部 3 个 .py"

rollback_instructions: |
  1. 删除 model_drift_monitor.py / ml_engineering.py / regime_detector.py
  2. 从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0012"
blocked_by: []
status: "done"
tags_fn:
  - "ml"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
