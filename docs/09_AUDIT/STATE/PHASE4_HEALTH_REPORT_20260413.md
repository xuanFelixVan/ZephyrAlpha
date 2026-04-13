---
module_id: AUDIT_PHASE4_HEALTH_REPORT
standard_type: audit_state
generated_at: 20260413
---

# Phase 4 文档治理健康度最终报告

> **生成时间**: 20260413
> **扫描标签**: L2_POST_FIX

## 核心指标对比

| 指标 | Phase 1 扫描（修复前）| L2 扫描（修复后）| 改善 |
|------|----------------------|----------------|------|
| 断链总数 | 5310 | 0 | -5310 (100%) |
| 重复 module_id | ≥0 | 0 | 已清零 |
| 孤儿文件 | 2134 | ~1144 (TIER_3) | -990 |
| MD 文件总数 | - | 4941 | - |

## Phase 3 修复汇总

| 子阶段 | 任务 | 执行结果 |
|--------|------|----------|
| Phase 3.1a | 断链批量修复 | 2676 条链接修复（高+中置信度）|
| Phase 3.1b | F3 Basename 碰撞核查 | 0 需操作（无实际 ARCHIVE 冗余）|
| Phase 3.1c | F4 孤儿文件解决 | 943 补充入链 + 47 归档 |
| Phase 3.1d | F5 TIER_A 重叠删除 | 12 冗余副本删除 |

## 残余待处理项

| 类别 | 数量 | 说明 | 建议 |
|------|------|------|------|
| 低置信度断链 | ~1819 | global_closest_basename 匹配，需人工确认 | Owner 审查后手动修复 |
| TIER_B D-类重叠 | 388 对 | score 0.5–0.85，需二审 | 见 SECOND_PASS_QUEUE_20260413.jsonl |
| 孤儿 TIER_3 | 0 | 无法自动决策 | 已清零 |

## 文件统计

- **总 Markdown 文件数**: 4941
- **docs/06_ARCHIVE/ 归档文件**: 47+ (Phase 3.1c)
- **删除冗余副本**: 12 (Phase 3.1d)

## 治理工具清单

| 脚本 | 功能 |
|------|------|
| `scripts/audit/sentinel_l1_governance_scan.py` | 内链完整性 + module_id 扫描 |
| `scripts/audit/fix_dead_links.py` | 断链批量修复（6 策略渐进匹配） |
| `scripts/audit/report_basename_collisions.py` | Basename 碰撞决策报告 |
| `scripts/audit/report_orphan_files.py` | 孤儿文件分层决策报告 |
| `scripts/audit/triage_blueprint_d_overlap_pairs.py` | D-类蓝图重叠 triage 分档 |
| `scripts/audit/resolve_basename_collisions.py` | Basename 碰撞执行脚本 |
| `scripts/audit/resolve_orphan_files.py` | 孤儿文件解决执行脚本 |
| `scripts/audit/resolve_tier_a_overlaps.py` | TIER_A 重叠删除执行脚本 |

## 下一步建议

1. **低置信度断链（~1819 条）**: 人工二审，重点检查 `global_closest_basename` 匹配结果
2. **TIER_B D-类重叠（388 对）**: 按 `SECOND_PASS_QUEUE_20260413.jsonl` HIGH 优先级（42 对）依次 triage
3. **定期 L3 扫描**: 建议每次大批量文档更新后重跑 `sentinel_l1_governance_scan.py`
4. **frontmatter 完整性扫描**: 下一步可运行 `check_frontmatter_completeness.py` 检查 module_id 缺失情况
