---
module_id: KE-module_blu-suitability_score-000
title: suitability_score 评估维度
category: module_blueprint
---

# suitability_score 评估维度

suitability_score 评估维度
suitability:
  extraction_safety_score: 0-100     # 综合适配性——< 40 = 绝对不提取
  dimensions:
    caller_compatibility: 85         # 所有调用方是否需要完全相同的逻辑？（越一致越好）
    divergence_risk: 15              # 调用方未来需求差异化的可能性？（越低越好）
    test_coverage_of_callers: 60     # 调用方的测试覆盖率？（越高越安全）
    public_api_stability: 100        # 提取后是否会破坏公开API契约？（不会被破坏 = 100）
    customization_need: 10           # 调用方是否有独特的定制需求？（越低越好）
    platform_specificity: 0          # 是否包含平台特定代码（sys.platform/os.name）？（包含 = 高风险）
    caller_count_safety: 90          # 调用方数量是否在安全范围？（< 20 = 安全，> 50 = 高风险）
    performance_sensitivity: 20      # 是否涉及性能热点路径？（越高越需要谨慎——提取 = 间接调用开销）
  verdict: "SAFE_TO_EXTRACT"         # SAFE_TO_EXTRACT | PARTIAL_EXTRACT | NEEDS_REVIEW | DO_NOT_EXTRACT
  partial_extraction_plan:           # 仅当 verdict=PARTIAL_EXTRACT 时有值
    common_core_pct: 60              # 可提取的公共核心占比 %
    divergent_parts:                 # 各调用方的差异化部分
      - caller: "caller_a.py"
        keep_local: "空字符串处理逻辑"
      - caller: "caller_b.py"
        keep_local: "性能优化的缓存逻辑"
```

**不安全提取模式目录**（以下模式 NEVER auto-extract）：

| 模式 | 为什么不能盲提取 | 策略 |
|------|---------------|------|
| **高调用方函数（caller_count > 50）** | 修改共享函数影响面巨大，一轮测试覆盖不到所有调用路径 | 需全量集成测试通过 + Owner 人工确认 |
| **平台条件代码**（含 `sys.platform` / `os.name`） | 提取后平台分支逻辑膨胀——共享函数变成 if/else 地狱 | 提取平台无关核心 + 保留平台适配层 |
| **公开 API 契约函数** | 提取 = 变更 import 路径 = 破坏下游依赖 | 保留原位置 + 内部委托到 shared（Adapter 模式） |
| **性能热点函数**（被高频调用） | 提取增加间接调用开销 + import 开销 | 仅在性能测试通过后提取 |
| **生成代码**（`# @generated` 标记） | 生成代码会被重新生成——提取会被覆盖 | **直接跳过——不检测、不报告** |
| **Vendored/第三方代码** | 每次升级需要重新合入 | 标记为 excluded，加入 config.py EXCLUSION_PATTERNS |
| **类型 stub 文件（`.pyi`）** | stub 文件本身就是类型声明重复——正常现象 | 豁免 |
