# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_node_label_quality.py | §node-label-quality
# [MODULE] scripts.governance.d5_architecture.checkers.check_node_label_quality
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS] GATE-NODE-LABEL-QUALITY pre-commit hook（warn-only 观察期）；AI 人工审计域文档节点标签简介质量
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读扫描域文档 Mermaid 节点标签；检测五类坏简介（模板话/截断片段/消费者引用/术语堆砌/名称重复）；--ci 有问题 exit 1，--warn-only 全 exit 0；不修改任何文件
# [MODIFY-GUARD] BAD_PATTERNS_LOW_CJK 子串清单与五类坏简介判定阈值（CJK<6 等）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=PASS/干净或--warn-only；exit 1=FINDINGS（--ci 且有问题）；exit 2=ERROR（文件不存在/参数错误）
# [TESTS] (暂无)
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""check_node_label_quality.py — GATE-NODE-LABEL-QUALITY

审计域文档 Mermaid 节点标签的简介质量，检测五类坏简介（治本 2026-08-02）。

病根：generate_domain_doc.py 生成器有自动兜底链（plain_zh → desc_zh → docstring → 路径派生）
和五道过滤（_is_placeholder / is_generic_plain_zh / is_generic_plain_suffix /
_is_name_plus_trivial / _clean_intro_text），但只能过滤坏值+派生唯一值，不能凭空写出好简介。
坏简介（模板话/截断/消费者引用/术语堆砌/名称重复）的根治靠人工读源码后写入 YAML 真源。
本检查器是"生成后"的安全网，在域文档提交时验证节点标签简介质量，防止坏简介流入仓库。

五类坏简介（详见 visualization_view_template.md §十七）：
  ① 模板话    —— 多模块共用同一句（如"IO的控制器，协调组件按流程执行"）
  ② 截断代码片段 —— docstring 半句话（如"<path> <head>``。在 Windows"）
  ③ 消费者引用  —— "审批，供zephyr.governance.services.ada使用"
  ④ 技术术语堆砌 —— "SLO契约。SLO-Driven Escalation Contract — D-022-12."
  ⑤ 名称重复   —— plain_zh == name_zh

模式：
  --ci (默认): 有问题 → exit 1
  --warn-only: 全部 exit 0 (仅报告)

用法：
  python scripts/governance/d5_architecture/checkers/check_node_label_quality.py [--warn-only] [<域文档.md>...]
  无参数时扫描 docs/02_enterprise_architecture/02_domain_architecture_docs/ 下所有 .md
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

import argparse
import re

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT

__manifest__ = """
args:
- --ci
- --warn-only
description: GATE-NODE-LABEL-QUALITY - 审计域文档 Mermaid 节点标签简介质量（五类坏简介防复发）
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: true
"""

# 域文档默认扫描目录（相对 REPO_ROOT）
DOMAIN_DOCS_DIR = Path("docs/02_enterprise_architecture/02_domain_architecture_docs")

# ①②③④ 类坏模式子串：只在简介整体汉字少时才算坏（避免中文句子里含英文术语误报）
BAD_PATTERNS_LOW_CJK = [
    "供zephyr",
    "供GovernanceServer",
    "供behavioral",
    "供behavioraladmiss",
    "Re-export shim",
    "Backward-compat",
    "<path>",
    ".py —",
    "件2改",
    "治本遗留项",
    "SLO-Driven",
    "D-022",
    "CTR-ERR",
    "OCP 扩展点",
    "in-process",
]

# ⑤ 名称重复判定：简介（去末尾标点）== 名称
_TRIVIAL_TAIL = "。，；：、！？. ,;:!"


def _strip_trivial_tail(text: str) -> str:
    """去掉末尾无信息增量的标点，用于⑤名称重复判定。"""
    return text.rstrip(_TRIVIAL_TAIL).strip()


def _extract_nodes(text: str) -> list[str]:
    """提取所有域内节点定义的 label：<id>["label"]。

    节点 ID 覆盖两类生成器产出：
      - 域文档（generate_domain_doc.py）：小写 ID 如 ``mod_bt_001``
      - 决策流图（generate_decision_diagram.py）：大写前缀 ID 如 ``N1``/``L2A``
    跨域外部节点 ID 形如 ``D_RISK``/``D_FACTOR``（D_ 前缀全大写），其 label 结构
    不同（仅域名无简介），不在本审计范围——用 ``[NL]\\d+`` 前缀精确匹配决策节点，
    避免误纳入 D_ 前缀的跨域外部节点。
    """
    return re.findall(r'^\s*(?:[a-z0-9_]+|[NL]\d+[A-Z0-9_]*)\["([^"]*)"\]', text, re.M)


def _rebuild_intro(label: str) -> tuple[str, str]:
    """从节点 label 重建（名称, 完整简介）。

    label 格式（generate_domain_doc.py 产出，<br/> 分隔）：
        名称行<br/>简介段（可能多段，预折行）<br/>文件: ...<br/>(生产态 / production)
        或设计态追加 ⛔ 受限原因

    重建逻辑：从第 2 段起拼含中文的段，遇到纯英文段（name_en/desc_en）、
    文件路径行、成熟度行、⛔ 行即停止。治本：旧版只查首段，预折行后首段
    可能只有几个汉字导致误报"技术/过短"。
    """
    parts = label.split("<br/>")
    if len(parts) < 2:
        return (label.strip(), "")

    name = parts[0].strip()
    intro_parts: list[str] = []
    for p in parts[1:]:
        p = p.strip()
        if (
            p.startswith("文件:")
            or p.startswith("(生产态")
            or p.startswith("(设计态")
            or p.startswith("(未知")
            or p.startswith("⛔")
        ):
            break
        has_cjk = bool(re.search(r"[\u4e00-\u9fff]", p))
        if not has_cjk and intro_parts:
            # 已有中文简介段，遇到纯英文段（name_en/desc_en）→ 停止
            break
        intro_parts.append(p)
    full_intro = "".join(intro_parts).strip()
    return (name, full_intro)


def _audit_doc(doc_path: Path) -> list[tuple[str, str]]:
    """审计单个域文档，返回 [(flag, detail), ...] 问题列表。"""
    text = doc_path.read_text(encoding="utf-8")
    nodes = _extract_nodes(text)
    bad: list[tuple[str, str]] = []

    for label in nodes:
        name, full_intro = _rebuild_intro(label)

        # 简介缺失
        if not full_intro:
            bad.append(("简介缺失", name))
            continue

        # ⑤ 名称重复（去末尾标点后比较，过滤"名称。"这种无信息增量重复）
        if _strip_trivial_tail(full_intro) == _strip_trivial_tail(name):
            bad.append(("名称重复", name + " | " + full_intro[:60]))
            continue

        # ④ 技术术语堆砌 / 过短：完整简介的汉字 < 6
        cjk = len(re.findall(r"[\u4e00-\u9fff]", full_intro))
        if cjk < 6:
            bad.append(("技术/过短", name + " | " + full_intro[:60]))
            continue

        # ①②③ 含坏模式（只在完整简介里查）
        for p in BAD_PATTERNS_LOW_CJK:
            if p in full_intro:
                bad.append(("含模板/术语: " + p, name + " | " + full_intro[:60]))
                break

    return bad


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="审计域文档 Mermaid 节点标签简介质量（五类坏简介）")
    parser.add_argument(
        "files",
        nargs="*",
        help="待审计的域文档 .md（无参数时扫描 DOMAIN_DOCS_DIR 下全部 .md）",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--warn-only",
        action="store_true",
        help="仅报告，全部 exit 0（观察期；转硬阻断时改用 --ci）",
    )
    mode.add_argument(
        "--ci",
        action="store_true",
        help="有问题即 exit 1（硬阻断模式，默认）",
    )
    args = parser.parse_args()

    # 默认 --ci
    ci_mode = not args.warn_only

    # 收集待审计文档
    if args.files:
        docs = [Path(f) for f in args.files]
    else:
        docs = sorted((REPO_ROOT / DOMAIN_DOCS_DIR).glob("*.md"))

    if not docs:
        print("无可审计文档。")
        return EXIT_PASS

    total_nodes = 0
    total_bad = 0
    doc_findings: list[tuple[Path, int, int, list[tuple[str, str]]]] = []

    for doc in docs:
        if not doc.exists():
            print("ERROR: 文档不存在: %s" % doc)
            return 2
        bad = _audit_doc(doc)
        # 节点数从原文重算（_audit_doc 内部已提取，这里复算用于汇总）
        n_nodes = len(_extract_nodes(doc.read_text(encoding="utf-8")))
        total_nodes += n_nodes
        total_bad += len(bad)
        doc_findings.append((doc, n_nodes, len(bad), bad))

    # 汇总
    print("=" * 60)
    print("GATE-NODE-LABEL-QUALITY 节点标签简介质量审计")
    print("模式: %s" % ("--warn-only (仅报告)" if args.warn_only else "--ci (硬阻断)"))
    print("文档数: %d, 节点总数: %d, 问题节点: %d" % (len(docs), total_nodes, total_bad))
    print("=" * 60)

    has_findings = False
    for doc, n_nodes, n_bad, bad in doc_findings:
        rel = doc.relative_to(REPO_ROOT) if doc.is_absolute() else doc
        status = "✓" if n_bad == 0 else "✗"
        print("%s %s — 节点 %d, 问题 %d" % (status, rel, n_nodes, n_bad))
        if n_bad:
            has_findings = True
            for flag, detail in bad:
                print("    [%s] %s" % (flag, detail))
    print("-" * 60)

    if has_findings and ci_mode:
        print("结论: 发现 %d 个问题节点，--ci 模式阻断提交。" % total_bad)
        print("修复指引：见 visualization_view_template.md §十七（人工补齐 SOP）。")
        return EXIT_FINDINGS
    elif has_findings:
        print("结论: 发现 %d 个问题节点，--warn-only 模式仅报告不阻断。" % total_bad)
        return EXIT_PASS
    else:
        print("结论: 全部节点简介质量合格，无五类坏简介。")
        return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
