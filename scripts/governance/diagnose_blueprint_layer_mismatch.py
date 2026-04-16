# AI-generated: 诊断蓝图文件的 layer 字段是否与其实际内容/路径一致
"""
Blueprint Layer Mismatch Diagnostician

主要问题：docs/01_FRAMEWORK/ 中大约 164 个蓝图的 layer 字段被设为 layer_01，
但 01_FRAMEWORK 是蓝图存储目录（非 Layer 01 的代码层），这些蓝图应该按内容标注实际层。

本脚本：
  1. 扫描所有蓝图，提取 layer 字段
  2. 根据文件名中的关键词推断正确 layer
  3. 输出需要修正的文件列表
  4. 可选：生成 --fix 建议（不自动执行，需 Owner 确认后手动运行）

用法:
    python scripts/governance/diagnose_blueprint_layer_mismatch.py
    python scripts/governance/diagnose_blueprint_layer_mismatch.py --fix-suggestions > fix_layer.sh
    python scripts/governance/diagnose_blueprint_layer_mismatch.py --apply-safe  # 只修正高置信度推断
"""

import sys
import re
import argparse
from pathlib import Path
from datetime import datetime


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

BLUEPRINT_DIRS = [
    "docs/01_FRAMEWORK",
    "docs/10_AI_WORKFLOW",
    "docs/11_STRATEGIC_DECISION",
    "docs/08_HUMAN_AI_INTERFACE",
    "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS",
]

SKIP_PATTERNS = ["06_ARCHIVE", "09_ARCHIVE", "99_ARCHIVE", ".audit_fix_backup"]

# 层关键词映射（文件名包含这些关键词 → 推断 layer）
LAYER_INFERENCE_RULES = [
    # L00 数据源层
    (0, ["data-source", "data_source", "ohlcv", "akshare", "market-data", "data-collection",
         "data-pipeline", "data-ingestion", "data-quality", "data-validation"]),
    # L01 基础设施层
    (1, ["infrastructure", "base-error", "configuration-management", "logging", "monitoring-infra",
         "devops", "deployment", "containerization", "ci-cd"]),
    # L02 Alpha 因子层
    (2, ["alpha-factor", "factor-research", "factor-effectiveness", "factor-case",
         "momentum-factor", "factor-library", "feature-engineering"]),
    # L03 舆情分析层
    (3, ["sentiment", "nlp", "text-analysis", "news-sentiment", "social-media-sentiment"]),
    # L04 ML 模型层
    (4, ["machine-learning", "ml-model", "model-training", "model-evaluation",
         "model-monitoring", "model-drift", "model-ab-testing", "model-performance",
         "model-version", "xgboost", "lightgbm", "deep-learning", "neural-network",
         "feature-store", "adaptive-model", "model-selection"]),
    # L05 策略层
    (5, ["strategy", "backtest", "signal-generation", "alpha-generation",
         "portfolio-construction", "strategy-lifecycle", "strategy-version"]),
    # L06 执行层
    (6, ["execution", "order-management", "risk-control", "position-management",
         "trade-execution", "transaction-cost", "best-execution", "circuit-breaker",
         "stop-loss", "turnover-control"]),
    # L07 AI 报告层
    (7, ["ai-report", "performance-analysis", "post-trade-review", "intelligent-scheduler",
         "intelligent-report", "portfolio-diagnostics", "attribution", "pnl",
         "reporting-system", "work-reporter", "report-generation",
         "historical-replay", "scenario-analysis", "stress-test"]),
    # L08 人机交互层
    (8, ["human-ai", "interface", "dashboard", "visualization", "user-interface",
         "alert-management", "notification", "ui", "hci"]),
    # L09 研究创新层
    (9, ["research", "innovation", "alternative-data", "academic", "experimental"]),
    # L10 治理合规层
    (10, ["compliance", "governance", "audit-trail", "regulation", "risk-management",
          "aml", "kyc", "mifid", "risk-budget"]),
    # L11 战略决策层
    (11, ["strategic", "strategy-decision", "meta-strategy", "portfolio-optimization-strategic"]),
]

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"


def infer_layer_from_filename(filename: str) -> tuple[int | None, str]:
    """从文件名推断正确 layer，返回 (layer_num, confidence)。"""
    name_lower = filename.lower()

    matches = []
    for layer_num, keywords in LAYER_INFERENCE_RULES:
        for kw in keywords:
            if kw in name_lower:
                matches.append((layer_num, kw))

    if not matches:
        return None, CONFIDENCE_LOW

    # 只有唯一匹配时才是高置信度
    layer_nums = list(set(m[0] for m in matches))
    if len(layer_nums) == 1:
        return layer_nums[0], CONFIDENCE_HIGH
    # 多个层匹配，取匹配词最长的
    best = max(matches, key=lambda m: len(m[1]))
    return best[0], CONFIDENCE_MEDIUM


def read_current_layer(filepath: Path) -> tuple[str, str]:
    """读取文件当前 layer 字段，返回 (raw_value, normalized)。"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        if not content.startswith("---"):
            return "", "unknown"
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return "", "unknown"
        yaml_str = content[3:end_idx]
        for line in yaml_str.split("\n"):
            if line.strip().startswith("layer:"):
                val = line.partition(":")[2].strip().strip("'\"")
                num_match = re.search(r"(\d{1,2})", val.lower())
                if num_match:
                    return val, f"layer_{int(num_match.group(1)):02d}"
                if "cross" in val.lower():
                    return val, "cross_layer"
                return val, val.lower()
    except Exception:
        pass
    return "", "unknown"


def apply_layer_fix(filepath: Path, new_layer: str) -> bool:
    """修正文件的 layer 字段（谨慎模式：只处理高置信度）。"""
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
        if not content.startswith("---"):
            return False
        # 替换 layer 字段
        new_content = re.sub(
            r"(^layer:\s*).*$",
            f"layer: {new_layer}",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        if new_content != content:
            filepath.write_text(new_content, encoding="utf-8")
            return True
    except Exception:
        pass
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose and optionally fix blueprint layer field mismatches")
    parser.add_argument("--fix-suggestions", action="store_true", help="Output fix commands (to stdout)")
    parser.add_argument("--apply-safe", action="store_true", help="Apply HIGH confidence fixes only")
    parser.add_argument("--min-confidence", choices=["HIGH", "MEDIUM", "LOW"], default="HIGH")
    args = parser.parse_args()

    results = []

    for dir_rel in BLUEPRINT_DIRS:
        dir_path = REPO_ROOT / dir_rel
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.rglob("*.md")):
            if md_file.stem.upper() in ("INDEX", "README", "SITEMAP"):
                continue
            rel = str(md_file.relative_to(REPO_ROOT)).replace("\\", "/")
            if any(skip in rel for skip in SKIP_PATTERNS):
                continue

            current_raw, current_norm = read_current_layer(md_file)
            inferred_num, confidence = infer_layer_from_filename(md_file.stem)

            if inferred_num is None:
                continue

            inferred = f"layer_{inferred_num:02d}"

            # 只报告不匹配的
            if current_norm == inferred:
                continue

            results.append({
                "path": rel,
                "current": current_norm,
                "inferred": inferred,
                "confidence": confidence,
                "file": md_file,
            })

    # 统计
    high = [r for r in results if r["confidence"] == CONFIDENCE_HIGH]
    medium = [r for r in results if r["confidence"] == CONFIDENCE_MEDIUM]
    low = [r for r in results if r["confidence"] == CONFIDENCE_LOW]

    print(f"=== Blueprint Layer Mismatch Report ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"")
    print(f"Total mismatches found: {len(results)}")
    print(f"  HIGH confidence: {len(high)}")
    print(f"  MEDIUM confidence: {len(medium)}")
    print(f"  LOW confidence: {len(low)}")
    print()

    for confidence_group, items in [("HIGH", high), ("MEDIUM", medium)]:
        if not items:
            continue
        print(f"--- {confidence_group} confidence fixes ---")
        for r in items[:30]:  # show first 30
            print(f"  {r['current']:12s} → {r['inferred']:12s}  {r['path']}")
        if len(items) > 30:
            print(f"  ... and {len(items) - 30} more")
        print()

    if args.fix_suggestions:
        print("# Fix commands (review before running):")
        for r in results:
            if r["confidence"] in ("HIGH", "MEDIUM"):
                print(f"# [{r['confidence']}] {r['path']}")
                cur = r['current']
                inf = r['inferred']
                p = r['path']
                print(f"# sed: {cur} -> {inf} in {p}")
        return

    if args.apply_safe:
        fixed = 0
        for r in results:
            if r["confidence"] == CONFIDENCE_HIGH:
                if apply_layer_fix(r["file"], r["inferred"]):
                    print(f"  Fixed: {r['path']}: {r['current']} → {r['inferred']}")
                    fixed += 1
        print(f"\nApplied {fixed} high-confidence layer fixes")

    # 保存报告
    date_str = datetime.now().strftime("%Y%m%d")
    report_path = REPO_ROOT / f"docs/09_AUDIT/STATE/blueprint-layer-mismatch-{date_str}.md"
    lines = [
        f"# Blueprint Layer Mismatch Report - {datetime.now().strftime('%Y-%m-%d')}",
        "",
        f"Total mismatches: {len(results)}",
        f"HIGH confidence: {len(high)}",
        f"MEDIUM confidence: {len(medium)}",
        "",
        "## HIGH Confidence (Safe to Auto-fix)",
        "",
    ]
    for r in high:
        lines.append(f"- `{r['path']}`: `{r['current']}` → `{r['inferred']}`")
    lines += ["", "## MEDIUM Confidence (Review Required)", ""]
    for r in medium[:50]:
        lines.append(f"- `{r['path']}`: `{r['current']}` → `{r['inferred']}`")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[OK] Report saved: {report_path}")


if __name__ == "__main__":
    main()
