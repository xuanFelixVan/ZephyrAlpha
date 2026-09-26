# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md
# [MODULE] scripts.governance.meta_question.apply_pending_patch
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] yaml; subprocess(git apply / git apply --check); 读 *.pending_patch.yaml 的 diff 字段
# [CONSUMERS] 总包落地链（在 Prereq 袋落 HEAD 后施加各车道待落地补丁）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 补丁一律以 .pending_patch.yaml 承载（scripts/ 目录契约 allowed 不含 .patch/.diff，
#              DCR-005 实证），本件把 diff 字段还原为临时 .patch 后交 git apply，语义与直接
#              git apply 等价；先 --check 再施加（不匹配即拒绝，禁半apply）；施加前后各打印
#              git status 摘要，可复核零意外覆写。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] --check 失败→退出码 2 且不施加（基线字节不符即拒绝，防错基线半改）。
# [TESTS] 无（运维施加器；验收=施加后目标件测试与门自检通过）
# [A_module] module_id=MOD-METAQ-PATCH-APPLIER | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
# noqa-rationale: 本文件无 SQL；.patch 临时件写在 .runtime/tmp
"""apply_pending_patch — 把 *.pending_patch.yaml 里承载的补丁施加到工作区。

用法：
    python scripts/governance/meta_question/apply_pending_patch.py <patch.yaml> [--check-only] [--reverse]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="施加待落地补丁（yaml 承载 diff）")
    ap.add_argument("patch", help="*.pending_patch.yaml 路径")
    ap.add_argument("--check-only", action="store_true", help="只验不施加")
    ap.add_argument("--reverse", action="store_true", help="反向撤销已施加的补丁")
    args = ap.parse_args()

    doc = yaml.safe_load(Path(args.patch).read_text(encoding="utf-8"))
    diff = doc.get("diff")
    if not isinstance(diff, str) or not diff.strip():
        print(f"[ERROR] {args.patch} 无 diff 字段", file=sys.stderr)
        return 2
    prereq = doc.get("apply_prerequisite") or "(未声明前置，请人工确认基线)"
    print(f"前置声明：{prereq}")

    tmp = Path(tempfile.gettempdir()) / (Path(args.patch).stem + ".tmp.patch")
    tmp.write_text(diff, encoding="utf-8", newline=chr(10))
    flags = ["--reverse"] if args.reverse else []
    chk = _git("apply", "--check", *flags, str(tmp))
    if chk.returncode != 0:
        print(f"[CHECK-FAIL] 基线不匹配，拒绝施加：{chk.stderr.strip()[:400]}", file=sys.stderr)
        tmp.unlink(missing_ok=True)
        return 2
    print("[CHECK-OK] 基线匹配")
    if args.check_only:
        tmp.unlink(missing_ok=True)
        return 0
    ap_res = _git("apply", *flags, "--index", str(tmp))
    tmp.unlink(missing_ok=True)
    if ap_res.returncode != 0:
        print(f"[APPLY-FAIL] {ap_res.stderr.strip()[:400]}", file=sys.stderr)
        return 1
    print("[APPLIED] 已施加并暂存；请跑目标件测试与门自检确认")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免 按需手工点火CLI非常驻自动任务
    sys.exit(main())
