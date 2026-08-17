# [BLUEPRINT] MOD-GOV_COMMIT_GATE_REGISTRY | (auto-injected by S4 reconciler) | §
# [MODULE] zephyr.gov_enforcement.rule_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""

gov_enforcement.rule_bridge — auto-generated package init.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: rule_bridge 子模块源码
#   fields: commit_gate_registry / git_commit_gateway / session_claim / session_worktree / worktree_manager 五个模块
#   code: src/zephyr/gov_enforcement/rule_bridge/ 目录
# 层: 算法
# - id: A1
#   name_zh: ① 子模块导出聚合
#   name_en: zephyr.gov_enforcement.rule_bridge（包 __init__）
#   intro: 自动生成的包初始化——用 __all__ 声明五个子模块名，无运行逻辑
#   desc: __all__=[commit_gate_registry, git_commit_gateway, session_claim, session_worktree, worktree_manager] L5
#   inputs: I1
#   outputs: 包命名空间 + 子模块导出清单
#   invariant: __all__ 与子模块文件一一对应
# 层: 输出
# - id: O1
#   name_zh: rule_bridge 包命名空间
#   name_en: zephyr.gov_enforcement.rule_bridge
#   intro: 规则桥接子包的 import 挂载点，供治理代码引用网关/会话/提交注册等模块
#   downstream: session_worktree_cli.py、git_commit_gateway MOD-INF-035 及域内互导模块
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

__all__ = ['commit_gate_registry', 'git_commit_gateway', 'session_claim', 'session_worktree', 'worktree_manager']

