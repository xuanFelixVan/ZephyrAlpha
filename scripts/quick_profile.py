# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §5
# [MODULE] scripts.quick_profile
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES]
# [CONSUMERS] 模型快速画像;岗位匹配
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] Quick模式5-8min;岗位匹配Top-N;幻觉六维正常评分
# [MODIFY-GUARD] docs/03_modules/_cross_layer/model_profiler/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 护照不存在→exit 2;未知模式→exit 3
# [TESTS] tests/test_quick_profile.py
# [TTL] permanent
"""
模型快速能力画像脚本 (P2 三级模式 Quick 入口)。

用途:
    - 从已有护照生成 QuickProfile 视图 (零推断, 立即出岗位推荐)
    - 真实 Quick 考试入口 (需 Ollama 运行, 5-8 分钟)
    - 岗位匹配 Top-N 推荐

设计原则:
    - 幻觉率正常评分 (非硬门), 任何模型都有幻觉
    - 岗位匹配用粗分级 A/B/C/D/F, 能力轮廓 > 每题精度
    - Quick 模式: 29 题 + 5 能力幻觉检测 = ~39 次推断

运行示例:
    # 从已有护照生成画像 (零推断)
    python scripts/quick_profile.py --from-passport deepseek-v4-pro-thinking

    # 列出全部护照
    python scripts/quick_profile.py --list

    # 真实 Quick 考试 (需 Ollama)
    python scripts/quick_profile.py --model qwen2.5-coder:14b

退出码:
    0 = 成功
    2 = 护照不存在
    3 = 参数错误/未知模式
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 包外 bootstrap: 一次性极简 sys.path 注入（仅此一次, 后续路径常量必须用 REPO_ROOT）
_SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(_SRC))

from zephyr.intelligence.model_profiling.capability_passport import (
    GRADE_LEVEL,
    CapabilityPassport,
    HallucinationBreakdown,
    QuickProfile,
    compute_grade_simple,
)
from zephyr.intelligence.model_profiling.job_matcher import JobMatcher

# REPO_ROOT SSoT: 仓库根常量唯一真源为 zephyr.shared.io.paths.REPO_ROOT
# 本脚本作为包外消费者, 仅用上述一次性 bootstrap, 不再自行推算仓库根


def _list_passports() -> int:
    """列出全部已有护照。"""
    passports = CapabilityPassport.list_all()
    if not passports:
        print("(no passports found)")
        return 0
    print(f"Found {len(passports)} passports:")
    for p in passports:
        print(f"  - {p}")
    return 0


def _profile_from_passport(model_id: str, top_n: int) -> int:
    """从已有 CapabilityPassport 生成 QuickProfile 视图。

    零推断: 直接读取护照 depth/hallucination 数据, 转为粗分级 + 岗位推荐。
    """
    # CapabilityPassport.load(model_id) 内部构造路径: PASSPORTS_DIR/{safe_id}.json
    passport = CapabilityPassport.load(model_id)
    if passport is None:
        print(
            f"ERROR: passport not found for model_id={model_id!r}",
            file=sys.stderr,
        )
        print(f"  hint: use --list to see all passports", file=sys.stderr)
        return 2

    # 从 depth.capabilities 提取能力分数
    capability_scores: dict[str, float] = {}
    capability_grades: dict[str, str] = {}
    if passport.depth and passport.depth.capabilities:
        for cap_name, cap_result in passport.depth.capabilities.items():
            score = max(cap_result.f1, cap_result.exact_match_rate)
            capability_scores[cap_name] = round(score, 3)
            capability_grades[cap_name] = compute_grade_simple(score)

    # 从 passport.hallucination 转换 (旧护照 3 维, 补全 9 维)
    hallu = HallucinationBreakdown(
        fabrication=passport.hallucination.fabrication_rate if passport.hallucination else 0.0,
        inconsistency=passport.hallucination.inconsistency_rate if passport.hallucination else 0.0,
        refusal=passport.hallucination.refusal_rate if passport.hallucination else 0.0,
        # 旧护照无此六维, 默认 0 (未来 Quick/Deep 考试会填充)
        overclaim=0.0,
        context_drift=0.0,
        source_confusion=0.0,
        instruction_drift=0.0,
        format_hallucination=0.0,
        quantity_hallucination=0.0,
    )

    profile = QuickProfile(
        model_id=passport.model_id,
        exam_mode="from_passport",
        exam_timestamp=passport.exam_timestamp,
        exam_duration_seconds=passport.exam_duration_seconds,
        capability_grades=capability_grades,
        capability_scores=capability_scores,
        hallucination=hallu,
        cost=passport.cost,
        overall_score=passport.overall_score,
        overall_grade=compute_grade_simple(passport.overall_score),
        notes=["converted from CapabilityPassport (6 new dims=0)"],
    )

    # 岗位匹配
    try:
        matcher = JobMatcher()
        profile.recommendations = matcher.match_top(profile, n=top_n)
    except Exception as e:
        profile.notes.append(f"job_match_failed: {e}")

    _print_report(profile)
    return 0


def _run_quick_exam(model_id: str, top_n: int) -> int:
    """真实 Quick 考试 (需 Ollama 运行)。"""
    try:
        # 延迟导入: 避免无 Ollama 环境下 import 失败
        from zephyr.intelligence.model_profiling.exam_orchestrator import ExamOrchestrator
        # 尝试导入 OllamaChat (项目内可能有不同实现)
        try:
            from zephyr.integration.local_model.ollama_chat import OllamaChat
        except ImportError:
            print(
                "ERROR: OllamaChat not found. Quick exam requires a running Ollama instance.\n"
                "  Hint: use --from-passport <model_id> to generate profile from existing data.",
                file=sys.stderr,
            )
            return 3

        chat = OllamaChat(model=model_id)
        orch = ExamOrchestrator(chat, model_id=model_id)
        profile = orch.run_quick_exam()
        # 持久化第一个真实护照
        saved_path = profile.save()
        print(f"  护照已保存: {saved_path}")
        _print_report(profile)
        return 0
    except Exception as e:
        print(f"ERROR: quick exam failed: {e}", file=sys.stderr)
        return 3


def _print_report(profile: QuickProfile) -> None:
    """打印快速能力画像报告。"""
    print("=" * 70)
    print(f"  模型能力画像: {profile.model_id}")
    print(f"  模式: {profile.exam_mode}  耗时: {profile.exam_duration_seconds:.1f}s")
    print(f"  综合分: {profile.overall_score:.3f}  分级: {profile.overall_grade}")
    print("=" * 70)

    # 1. 能力雷达图 (文本表格)
    print("\n【能力轮廓】 A=精通 B=熟练 C=合格 D=初级 F=不胜任")
    print(f"  {'能力':<30} {'分数':>6} {'分级':>4} {'柱状图':<20}")
    print(f"  {'-'*30} {'-'*6} {'-'*4} {'-'*20}")
    # 按分数降序
    sorted_caps = sorted(
        profile.capability_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )
    for cap, score in sorted_caps:
        grade = profile.capability_grades.get(cap, "F")
        bar_len = int(score * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"  {cap:<30} {score:>6.3f} {grade:>4} {bar}")

    # 2. 幻觉九维
    h = profile.hallucination
    print(f"\n【幻觉九维】 综合幻觉率: {h.overall_rate:.3f}  幻觉得分: {h.hallucination_score:.3f}")
    print(f"  fabrication          事实编造:     {h.fabrication:.3f}")
    print(f"  inconsistency        输出不一致:   {h.inconsistency:.3f}")
    print(f"  refusal              过度拒绝:     {h.refusal:.3f}")
    print(f"  overclaim            过度声称:     {h.overclaim:.3f}")
    print(f"  context_drift        上下文漂移:   {h.context_drift:.3f}")
    print(f"  source_confusion     来源混淆:     {h.source_confusion:.3f}")
    print(f"  instruction_drift    指令偏离:     {h.instruction_drift:.3f}")
    print(f"  format_hallucination 格式幻觉:     {h.format_hallucination:.3f}")
    print(f"  quantity_hallucination 数量幻觉:    {h.quantity_hallucination:.3f}")

    # 3. 成本明细 (D-MCE-07: 成本是维度非硬门)
    c = profile.cost
    print(f"\n【成本明细】 模式: {c.deployment_mode}  供应商: {c.provider}  成本得分: {c.cost_score:.3f}")
    print(f"  总调用: {c.total_calls}  总 token: {c.total_tokens} (in={c.input_tokens}, out={c.output_tokens})")
    if c.deployment_mode == "api":
        print(f"  单价: ${c.price_per_1k_input:.4f}/1K(in) + ${c.price_per_1k_output:.4f}/1K(out)")
        print(f"  估算成本: ${c.estimated_cost_usd:.6f}")
    else:
        print(f"  估算成本: $0.000000 (本地模型)")

    # 4. 岗位推荐
    if profile.recommendations:
        print(f"\n【岗位推荐 Top{len(profile.recommendations)}】")
        print(f"  {'岗位':<18} {'匹配度':>8} {'合格':>4} {'幻觉':>6} {'说明':<30}")
        print(f"  {'-'*18} {'-'*8} {'-'*4} {'-'*6} {'-'*30}")
        for r in profile.recommendations:
            hallu_mark = "✓" if r.hallucination_passed else "✗"
            qualified_mark = "✓" if r.qualified else "✗"
            print(
                f"  {r.job_title:<18} {r.match_score:>7.1%} "
                f"{qualified_mark:>4} {hallu_mark:>6} {r.description[:30]:<30}"
            )
            if r.missing_required:
                print(f"    ↳ missing: {', '.join(r.missing_required)}")
            if r.bonus_summary and r.bonus_summary != "none":
                print(f"    ↳ bonus: {r.bonus_summary}")
    else:
        print("\n【岗位推荐】 (无 — JobMatcher 未运行或无匹配岗位)")

    # 5. 备注
    if profile.notes:
        print("\n【备注】")
        for note in profile.notes:
            print(f"  - {note}")

    print("\n" + "=" * 70)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="quick_profile",
        description="模型快速能力画像 + 岗位匹配 (P2 三级模式 Quick 入口)",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--model",
        help="真实 Quick 考试 (需 Ollama 运行), 指定模型 ID 如 qwen2.5-coder:14b",
    )
    group.add_argument(
        "--from-passport",
        metavar="MODEL_ID",
        help="从已有护照生成 QuickProfile 视图 (零推断, 立即出岗位推荐)",
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="列出全部已有护照",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="推荐岗位数 (默认 3)",
    )
    args = parser.parse_args(argv)

    if args.list:
        return _list_passports()
    elif args.from_passport:
        return _profile_from_passport(args.from_passport, args.top)
    elif args.model:
        return _run_quick_exam(args.model, args.top)
    else:
        parser.error("no action specified")
        return 3


if __name__ == "__main__":
    sys.exit(main())
