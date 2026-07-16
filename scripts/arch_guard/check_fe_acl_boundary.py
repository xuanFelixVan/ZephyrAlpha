# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/check_fe_acl_boundary.py | §
# [MODULE] scripts.arch_guard.check_fe_acl_boundary
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
check_fe_acl_boundary.py — INV-006 前端 ACL（仓库内有前端树则启用）

  - 若存在 .tsx/.vue 等前端源文件：禁止直接 fetch 内网后端裸端口（须走 API Gateway，启发式）
  - 当前仓库无前端：仅输出基线通过

exit: 0=pass, 1=violation
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

FE_EXTS = {".tsx", ".ts", ".jsx", ".js", ".vue"}
_SKIP_DIRS = {"node_modules", ".git", "dist", "build", "coverage", "__pycache__"}

# 绕过 API Gateway 直连内网服务（启发式；排除 localhost + 非标准 API 路径）
_BAD_FETCH = re.compile(
    r"fetch\s*\(\s*['\"](https?://(127\.0\.0\.1|localhost):\d{2,5}/[^'\"]*)['\"]",
    re.IGNORECASE,
)

def main() -> int:
    fe_files: list[Path] = []
    for p in REPO_ROOT.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in FE_EXTS:
            continue
        if any(s in p.parts for s in _SKIP_DIRS):
            continue
        fe_files.append(p)

    if not fe_files:
        print("OK: 仓库内无前端源树 — INV-006 基线通过（待 D_FRONTEND FE 落地后自动收紧）")
        return 0

    bad: list[str] = []
    for f in fe_files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if _BAD_FETCH.search(text):
            bad.append(str(f.relative_to(REPO_ROOT)))

    if bad:
        print("FAIL: 前端疑似直连内网端口（应经 D_FRONTEND api_gateway）:")
        for b in bad:
            print(f"  - {b}")
        return 1

    print(f"OK: 已扫描 {len(fe_files)} 个前端文件，未发现典型内网裸连 fetch")
    return 0

if __name__ == "__main__":
    sys.exit(main())
