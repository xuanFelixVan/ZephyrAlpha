---
module_id: KE-module_blu-dedup_report_yaml-003
title: dedup_report.yaml —— 完整检测报告
category: module_blueprint
---

# dedup_report.yaml —— 完整检测报告

dedup_report.yaml —— 完整检测报告
dedup_report:
  scan_metadata:
    generated_at: "2026-05-05T..."
    scan_mode: "incremental"          # full | incremental
    trigger: "pre-commit"            # pre-commit | weekly | manual
    scope: "src/zephyr/"
    total_functions: 342
    scanned_functions: 12             # 本次只扫描了12个变更函数（增量模式）
    cached_functions: 330             # 其余330个来自缓存
    scan_duration_ms: 2147
    exit_code: 1                      # 0=无重复 / 1=发现重复(WARN) / 2=严重重复(ERROR) / 3=工具故障 / 4=降级运行
    degradation_level: "none"        # none | stage1_only | stage0.5_only | no_ast | no_cache ——降级运行标记

  health_score:                       # 代码健康仪表盘数据（新增——Wave 1 即产出，v0.5.0 扩展）
    overall: 87                       # 0-100，综合代码健康度
    trend: "up"                       # up | down | flat（较上次扫描的趋势）
    components:
      duplication_rate: 3.5           # 重复函数占比 %
      shared_coverage: 45             # shared/ 中函数占比 %
      signature_collisions: 0         # 签名碰撞数
      import_health: 85               # import 健康度
      stale_shared_count: 0           # 过期共享函数数（v0.5.0 新增）
      auto_fix_success_rate: 100      # 自动修复成功率 %（v0.5.0 新增）
    introduction_velocity: 2.0         # 新重复引入速率——组/周（v0.5.0 新增——暴露 Prevent 阶段是否有效）
    debt_projection_weeks: 4          # 按当前速率预计 N 周还清去重债务（v0.5.0 新增）
    engine_observability:              # 引擎自观指标（v0.5.0 新增——用于调试引擎自身）
      scan_duration_p50_ms: 1200      # 增量扫描中位数耗时
      cache_hit_ratio: 0.94           # 缓存命中率——增量扫描复用缓存比例
      detection_latency_hours: 4.2    # 从重复引入到检测发现的平均延迟
      false_positive_rate_7d: 0.03    # 最近 7 天误报率（需 Owner 确认标记来更新）
    hotspot_categories:               # AI 健忘热点 Top 3
      - category: "time_utils"
        duplicate_count: 3
        trend: "down"
      - category: "path_utils"
        duplicate_count: 2
        trend: "flat"

  summary:
    duplicate_groups_total: 3
    signature_collisions: 1           # Stage 0.5 检测到的签名碰撞数（新增）
    high_confidence: 2                # similarity > 0.95
    medium_confidence: 1              # 0.85~0.95
    low_confidence: 0                 # 0.70~0.85
    affected_files: 7
    auto_fixable: 2                   # 可自动修复的组数
    roi_top_pick: "DUP-20260505-001"  # ROI最高的修复组（prioritizer.py 产出）——新增

  duplicate_groups:
    - group_id: "DUP-20260505-000"
      similarity: 1.0   # 签名碰撞——函数体可能完全不同但签名相同
      confidence: 90
      category: "needs_review"          # 签名碰撞默认 needs_review——可能是 Vibe Coding 重实现
      detection_method: "signature_collision"   # Stage 0.5
      clone_type: "Type-2 (signature)" # 签名相同但实现可能完全不同
      signature_fingerprint: "a1b2c3d4e5f6"
      signature: "() -> str"
      members:
        - id: "func-001"
          file: "orchestrator/state_synchronizer.py"
          function: "_now_iso"
          loc: "45-48"
        - id: "func-015"
          file: "orchestrator/file_task_mapper.py"
          function: "_now_iso"
          loc: "45-48"
        - id: "func-023"
          file: "context_engine/context_injector.py"
          function: "_default_no
