# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3,§4
# [MODULE] scripts.governance.run_semantic_audit
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance.semantic_audit.orchestrator
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 审计产物落 .runtime/semantic_audit/（untracked 运行时区）；detect-only 模式零副作用
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SemanticAuditor.audit() never raises（stages 失败降级跳过返回 partial report）；本脚本参数错误 exit 2
# [TESTS] none（入口脚本；被审计逻辑由 tests/semantic_auditor/test_semantic_auditor.py 覆盖）
# [A_module] module_id=MOD-INF-028 | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""run_semantic_audit.py — SemanticAuditor 9 阶段管道 CLI 入口（B7 接线，2026-09-06 Owner 批"接线不删"）。

职责：为零消费的 src/zephyr/governance/semantic_audit/orchestrator.py（MOD-INF-028）
提供可执行入口，跑通 9 阶段语义审计管道并产出 JSON 报告。

用法：
  python scripts/governance/run_semantic_audit.py <doc_path>                    # full 模式单文档
  python scripts/governance/run_semantic_audit.py <doc_path> --stage 4          # 单阶段冒烟（1-9）
  python scripts/governance/run_semantic_audit.py <doc_path> --mode detect-only # 检测模式（跳过 LLM/自愈）
  python scripts/governance/run_semantic_audit.py --health                      # 管道健康检查

输出：
  JSON 报告 → .runtime/semantic_audit/<时间戳>-<audit_id>.json + 终端摘要
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

OUT_DIR = REPO_ROOT / ".runtime" / "semantic_audit"

STAGE_INTRO = {
    1: "ReferenceExtractor — 9 种引用维度提取",
    2: "TriggerEngine — F+G 两类纯语义触发检测",
    3: "SafetyBoundary — 禁碰规则过滤+置信度阈值",
    4: "AlignmentEngine — 注册表↔磁盘双向对齐",
    5: "IssueAggregator — 去重聚合问题清单",
    6: "LLMBridge — LLM 修复文本生成+模板降级",
    7: "SelfHealer — 自愈闭环(修复->自测->回滚)",
    8: "FixPrioritizer — 修复优先级排序+批处理分组",
    9: "BlastRadius — 影响爆炸半径+级联过时检测",
}


def _dump_report(report) -> Path:  # noqa: ANN001 — SemanticAuditReport pydantic 模型
    """JSON 报告落盘 .runtime/semantic_audit/，返回产物路径。"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = OUT_DIR / f"{ts}-{report.audit_id or 'audit'}.json"
    out.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    return out


def _print_summary(report, out_path: Path) -> None:  # noqa: ANN001
    print("=== SemanticAudit 摘要 ===")
    print(f"audit_id      : {report.audit_id}")
    print(f"rule_document : {report.rule_document}")
    print(f"total_triggers: {report.total_triggers}")
    print(f"red_issues    : {len(report.red_issues)}")
    print(f"yellow_issues : {len(report.yellow_issues)}")
    print(f"duration_ms   : {report.duration_ms}")
    print(f"token_used    : {report.token_used}")
    print(f"report_json   : {out_path}")


def run_stage_smoke(doc_path: Path, stage: int) -> int:
    """单阶段冒烟：实例化管道并执行指定阶段的最小路径。"""
    from zephyr.governance.semantic_audit.orchestrator import SemanticAuditor

    auditor = SemanticAuditor(project_root=REPO_ROOT)
    stage_names = {
        1: lambda: auditor._extractor.extract(doc_path),  # noqa: SLF001 — 入口脚本访问受保护阶段组件
        2: lambda: auditor._trigger_engine.evaluate([str(doc_path)]),  # noqa: SLF001
        3: lambda: auditor._safety_boundary.filter(
            auditor._trigger_engine.evaluate([str(doc_path)]).results  # noqa: SLF001
        ),
        4: lambda: [
            auditor._alignment_engine.align(auditor._extract_module_id(doc_path))  # noqa: SLF001
        ],
        5: None,  # Stage 5 聚合需 1-4 全量输出，走完整 audit()
        6: None,
        7: None,
        8: None,
        9: None,
    }
    if stage in (5, 6, 7, 8, 9):
        # Stage 5+ 依赖前序阶段全量产物（聚合/修复/自愈），单阶段冒烟以完整 audit(detect-only) 等价覆盖
        print(f"[stage {stage}] 依赖前序全量产物，等价跑完整管道（detect-only）……")
        report = auditor.audit(doc_path, mode="detect-only")
        out_path = _dump_report(report)
        _print_summary(report, out_path)
        return 0
    fn = stage_names.get(stage)
    if fn is None:
        print(f"[stage {stage}] 组件未初始化（init 降级），冒烟失败", file=sys.stderr)
        return 1
    result = fn()
    print(f"[stage {stage}] {STAGE_INTRO[stage]}")
    payload = result.model_dump_json(indent=2) if hasattr(result, "model_dump_json") else json.dumps(
        result, ensure_ascii=False, default=str
    )
    print(payload[:2000])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="SemanticAuditor 9 阶段管道 CLI 入口（MOD-INF-028）")
    parser.add_argument("doc_path", nargs="?", help="待审计规则文档路径")
    parser.add_argument("--mode", default="full", choices=["full", "incremental", "detect-only"], help="审计模式")
    parser.add_argument("--stage", type=int, choices=range(1, 10), help="单阶段冒烟（1-9）")
    parser.add_argument("--health", action="store_true", help="管道健康检查")
    args = parser.parse_args()

    from zephyr.governance.semantic_audit.orchestrator import SemanticAuditor

    auditor = SemanticAuditor(project_root=REPO_ROOT)

    if args.health:
        status = auditor.health_check()
        payload = status.model_dump_json(indent=2) if hasattr(status, "model_dump_json") else str(status)
        print(payload)
        return 0

    if not args.doc_path:
        parser.error("需要 doc_path（或 --health）")
        return 2

    doc_path = Path(args.doc_path)
    if not doc_path.is_absolute():
        doc_path = REPO_ROOT / doc_path
    if not doc_path.exists():
        print(f"文档不存在: {doc_path}", file=sys.stderr)
        return 2

    if args.stage:
        return run_stage_smoke(doc_path, args.stage)

    report = auditor.audit(doc_path, mode=args.mode)
    out_path = _dump_report(report)
    _print_summary(report, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
