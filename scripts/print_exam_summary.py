# [BLUEPRINT] MOD-CD-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""输出所有模型考试成绩清单（中文版）"""

import json
from datetime import date
from pathlib import Path

passports_dir = Path("data/brain/passports")
files = sorted(passports_dir.glob("*.json"))

rows = []
for f in files:
    d = json.loads(f.read_text(encoding="utf-8"))
    ce = d.get("cost_efficiency", {})
    safe_caps = d.get("recommendations", {}).get("safe_capabilities", [])
    rows.append(
        {
            "model_id": d.get("model_id", f.stem),
            "timestamp": d.get("exam_timestamp", "")[:10],
            "grade": d.get("overall_grade", ""),
            "score": d.get("overall_score", 0.0),
            "breadth_passed": d.get("breadth", {}).get("passed", 0),
            "breadth_total": d.get("breadth", {}).get("total", 0),
            "depth_score": d.get("depth", {}).get("overall_score", 0.0),
            "hallucination": d.get("hallucination", {}).get("overall_rate", 0.0),
            "speed_p50": d.get("speed", {}).get("latency_p50_ms", 0.0),
            "safe_count": len(safe_caps),
            "safe_caps": safe_caps,
            "cost": ce.get("exam_cost_cny", 0.0),
            "input_tokens": ce.get("input_tokens", 0),
            "output_tokens": ce.get("output_tokens", 0),
            "total_tokens": ce.get("total_tokens", 0),
            "cost_per_question": ce.get("cost_per_question", 0.0),
            "exam_questions": ce.get("exam_questions_asked", 0),
            "deployment_mode": ce.get("deployment_mode", ""),
            "duration": d.get("exam_duration_seconds", 0.0),
        }
    )

# 按分数降序
rows.sort(key=lambda r: r["score"], reverse=True)

# 能力中文名
CAP_CN = {
    "task_classification": "任务分类",
    "tag_completion": "标签补全",
    "summary_extraction": "摘要提取",
    "naming_suggest": "命名建议",
    "anomaly_triage": "异常分诊",
    "code_edit_precision": "代码编辑精度",
    "refactor": "重构",
    "code_generate": "代码生成",
    "dead_code_removal": "死代码移除",
    "rule_comprehension": "规则理解",
    "safety_judgment": "安全判断",
    "self_review": "自审自纠",
    "error_recovery": "错误恢复",
    "dependency_trace": "依赖追踪",
    "circular_dependency_detect": "循环依赖检测",
    "impact_analysis": "影响分析",
    "task_decomposition": "任务分解",
    "incremental_execution": "增量执行",
    "architecture_design": "架构设计",
    "context_consistency": "上下文一致性",
    "hallucination_detect": "幻觉检测",
    "ambiguity_detect": "歧义识别",
    "tool_selection": "工具选择",
    "dependency_ordering": "依赖排序",
    "cross_file_refactor": "跨文件重构",
    "long_context_recall": "长上下文召回",
    "rollback_boundary_design": "回滚边界设计",
    "parallel_planning": "并行规划",
    "context_management": "上下文管理",
    "multi_step_reasoning": "多步推理",
    "constraint_solving": "约束求解",
    "causal_analysis": "因果分析",
    "counterfactual_reasoning": "反事实推理",
}

print("=" * 120)
print(f"  AI 模型入职考试成绩清单（{date.today().isoformat()}）")
print("=" * 120)
print()
print(
    f"{'排名':<4} {'模型':<32} {'等级':<4} {'总分':<8} {'横轴':<8} {'纵轴':<8} {'幻觉率':<8} {'延迟P50':<10} {'安全能力':<8} {'费用(元)':<12} {'Tokens':<10} {'每题成本':<10} {'模式':<6}"
)
print("-" * 120)

for i, r in enumerate(rows, 1):
    print(
        f"{i:<4} "
        f"{r['model_id']:<32} "
        f"{r['grade']:<4} "
        f"{r['score']:<8.3f} "
        f"{r['breadth_passed']}/{r['breadth_total']:<6} "
        f"{r['depth_score']:<8.3f} "
        f"{r['hallucination']:<8.3f} "
        f"{r['speed_p50']:<10.0f}ms "
        f"{r['safe_count']:<8} "
        f"¥{r['cost']:<11.6f} "
        f"{r['total_tokens']:<10} "
        f"¥{r['cost_per_question']:<9.6f} "
        f"{r['deployment_mode']:<6}"
    )

# 能力对比矩阵
print()
print("=" * 120)
print("  能力通过矩阵（✓=通过 ✗=未通过 — =未考）")
print("=" * 120)

all_caps = list(CAP_CN.keys())
# 表头
header = f"{'能力':<28}"
for r in rows:
    name = r["model_id"][:18]
    header += f"{name:<20}"
print(header)
print("-" * (28 + 20 * len(rows)))

for cap in all_caps:
    cn = CAP_CN[cap]
    row = f"{cap[:26]:<28}"
    for r in rows:
        safe_set = set(r["safe_caps"])
        if cap in safe_set:
            row += f"{'✓':<20}"
        else:
            row += f"{'✗':<20}"
    print(row)

# 能力中文
print()
print("=" * 120)
print("  能力中文名对照")
print("=" * 120)
for cap in all_caps:
    print(f"  {cap:<28} → {CAP_CN[cap]}")

# 费用汇总
print()
print("=" * 120)
print("  费用汇总")
print("=" * 120)

local_models = [r for r in rows if r["deployment_mode"] == "local"]
api_models = [r for r in rows if r["deployment_mode"] == "api"]

print("\n本地模型（Ollama，免费）:")
total_local_tokens = sum(r["total_tokens"] for r in local_models)
print(f"  数量: {len(local_models)} 个模型")
print("  费用: ¥0.000000（全部免费）")
print(f"  Token消耗: {total_local_tokens:,}（其中仅 qwen2.5-coder_14b 有统计）")

print("\nAPI模型（DeepSeek V4，付费）:")
total_api_cost = sum(r["cost"] for r in api_models)
total_api_tokens = sum(r["total_tokens"] for r in api_models)
print(f"  数量: {len(api_models)} 个模型")
print(f"  费用: ¥{total_api_cost:.6f}（约 ${total_api_cost * 0.14:.4f} USD）")
print(f"  Token消耗: {total_api_tokens:,}")
print(f"  平均每模型: ¥{total_api_cost / len(api_models):.6f}")

print("\n总计:")
print(f"  模型数: {len(rows)} 个（{len(local_models)} 本地 + {len(api_models)} API）")
print(f"  总费用: ¥{total_api_cost:.6f}")
print(f"  总Token: {total_local_tokens + total_api_tokens:,}")
