# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] scripts.pre_commit.verify_dedup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_code_quality.code_dedup.cli
# [CONSUMERS] .pre-commit-config.yaml gate-dedup hook
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 委托 cli.py verify，不自实现检测逻辑
# [MODIFY-GUARD] code_dedup_engine blueprint §
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] subprocess returncode
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""pre_commit 验证脚本 — 委托给 code-dedup-engine CLI verify 子命令.

在 pre_commit hook 中调用：
  python scripts/pre_commit/verify_dedup.py [--staged]
  python scripts/pre_commit/verify_dedup.py --full-tree   （裁定#354 周期审计模式）

退出码：
  0 = GATE_PASSED（引擎正常）
  1 = GATE_WARN（引擎降级——需人工判断）
  2 = GATE_ERROR（引擎故障——需人工判断）

默认模式：委托 cli verify（引擎自检，提交面行为零变化）。
--full-tree 审计模式（裁定#354）：委托 cli scan --full --fail-on-duplicates——
全量扫描 src/+scripts/+tests() 暴露历史存量重复（staged-only 观测面对存量永久
不可见，#354 亲验）；发现高重复 exit 2（审计红）。

所有重复检测逻辑由 cli.py 统一执行，本文件仅作为 pre_commit 入口委托。
"""

from __future__ import annotations

# noqa: m11-perm-manual-legitimate  M11豁免: pre-commit/周期审计按需调用的 dedup 引擎委托入口，非常驻服务（裁定#354 --full-tree 审计由计划任务事件拉起）
import argparse
import subprocess
import sys
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parent.parent / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

SRC_DIR = REPO_ROOT / "src"


def main() -> int:
    parser = argparse.ArgumentParser(description="code-dedup-engine pre_commit 入口（委托 CLI）")
    parser.add_argument(
        "--full-tree",
        action="store_true",
        help="审计模式：委托 cli scan --full 全量暴露存量重复（裁定#354 周期审计；默认=verify 引擎自检零变化）",
    )
    args = parser.parse_args()

    if args.full_tree:
        subcmd = ["scan", "--full", "--fail-on-duplicates"]
    else:
        subcmd = ["verify"]
    result = subprocess.run(  # noqa: bare-subprocess  静态检查器读 git 状态,process_pool 在此场景不适用
        [sys.executable, "-m", "zephyr.gov_code_quality.code_dedup.cli", *subcmd],
        cwd=str(SRC_DIR.parent),
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
