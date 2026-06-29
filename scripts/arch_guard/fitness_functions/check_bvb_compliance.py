# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/check_bvb_compliance.py | §
# [MODULE] scripts.arch_guard.fitness_functions.check_bvb_compliance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard.fitness_functions.__init__
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
# [TTL] task_bound
"""check_bvb_compliance.py — BvB 五维评分合规检查（stub）

对标 architecture_principles.md §2 "开源优先与 Build-vs-Buy"。
检查新模块蓝图是否包含 "OSS Candidates" 小节。

当前状态：stub——需要 blueprint-registry 集成后才能实现完整检查。
exit: 0=合规或 stub 模式, 1=不合规, 2=基础设施错误
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def main() -> int:
    print("BvB 五维评分合规检查 (stub)\n")
    print("[STUB] 此适应度函数尚未实现完整检查逻辑。")
    print("  前置条件：blueprint-registry 集成 + OSS Candidates 小节标准化")
    print("  目标：每个新模块蓝图必须包含 OSS Candidates 调研结果")
    print("\n[OK] stub 模式——跳过检查")
    return 0


if __name__ == "__main__":
    sys.exit(main())
