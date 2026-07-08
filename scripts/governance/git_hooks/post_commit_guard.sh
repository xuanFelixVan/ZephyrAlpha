#!/bin/sh
# =============================================================================
# POST-COMMIT-GUARD: non-GW commit 检测与自动 revert
# =============================================================================
# 裁定 #ARCH-050（2026-07-05）：强化 --no-verify 使用约束
#
# 病根：--no-verify 绕过 pre-commit hook，导致 GitCommitGateway 的
#   in-process gates + pre-commit 检查全部被绕过，产生 non-GW commit
#   （commit message 无 [GW: 标记）。commit_gw_audit reconciler 事后
#   审计为 warn-only，不阻断，无法有效约束。
#
# 治本：--no-verify 绕过 pre-commit，但不绕过 post-commit。
#   在 post-commit 中检测 commit message 是否含 [GW: 标记，
#   不含则自动 git reset --soft HEAD~1（保留修改在 staging area），
#   强制所有 commit 必须通过 GitCommitGateway。
#
# 合法标识（含 [GW: 标记的 commit）：
#   - GitCommitGateway 常规 commit: [GW:{session_id}]
#   - GitCommitGateway auto-commit: [GW:{session_id}:auto]
#   - session_worktree_commit: [GW:{session_id}:worktree]
#   - session_worktree_merge: [GW:{session_id}:merge]
#
# 豁免（不含 [GW: 但放行）：
#   - merge commit（subject 以 "merge " 开头，大小写不敏感）
#     注意：session_worktree merge 已修复为带 [GW: 标记，此处豁免为保险
#
# 安装：cp scripts/governance/git_hooks/post_commit_guard.sh .git/hooks/post-commit
#   或在 .git/hooks/post-commit 末尾追加调用本脚本
# =============================================================================

# 获取当前 commit message（subject + body）
commit_msg=$(git log -1 --format=%B)

# 检查是否含 [GW: 标记（GitCommitGateway / session_worktree_commit / session_worktree_merge 的合法标识）
if echo "$commit_msg" | grep -q '\[GW:'; then
    # === session_id 真实性验证（治本伪造标记，#ARCH-050 强化 2026-07-08）===
    # 解析 session_id：要求 sess- 前缀，避免匹配描述文本中误含的 [GW: 片段
    session_id=$(echo "$commit_msg" | sed -n 's/.*\[GW:\(sess-[^]:}]*\).*/\1/p' | head -1)

    # 解析失败 → 保守放行（避免误判）
    if [ -z "$session_id" ]; then
        exit 0
    fi

    # 获取主仓库根目录（worktree 内 git-common-dir 指向主仓库 .git）
    common_dir=$(git rev-parse --git-common-dir 2>/dev/null)
    if [ -n "$common_dir" ] && [ -d "$common_dir" ]; then
        repo_root=$(cd "$common_dir/.." && pwd)
        registry_file="$repo_root/.runtime/session_registry.json"
    else
        registry_file=".runtime/session_registry.json"
    fi

    # fail-open：注册表不存在 → 放行（避免环境问题阻断所有 commit）
    if [ ! -f "$registry_file" ]; then
        exit 0
    fi

    # 验证 session_id 在注册表中（register 写入/unregister 删除；merge commit 已被 ^merge 豁免）
    if grep -q "\"$session_id\"" "$registry_file" 2>/dev/null; then
        exit 0  # session_id 已注册 → 合法放行
    fi

    # session_id 未注册 → 伪造检测
    echo ""
    echo "[POST-COMMIT-GUARD] 检测到伪造 GW 标记（session_id=$session_id 未在 SessionRegistry 注册）"
    echo "[POST-COMMIT-GUARD] 自动执行 git reset --soft HEAD~1（保留修改在 staging area）"
    echo "[POST-COMMIT-GUARD] 请通过 GitCommitGateway/session_worktree_commit 重新提交（见 AGENTS.md §8）"
    echo ""

    # 记录违规到审计日志
    mkdir -p .runtime/reconcile_reports
    timestamp=$(date +%s)
    hash=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    report_file=".runtime/reconcile_reports/post_commit_guard_${timestamp}.json"
    escaped_sid=$(echo "$session_id" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n' | head -c 200)
    echo "{\"gate_id\":\"POST-COMMIT-GUARD\",\"timestamp\":$timestamp,\"hash\":\"$hash\",\"violation\":\"forged_gw_marker\",\"session_id\":\"$escaped_sid\",\"action\":\"reset_soft_HEAD~1\"}" > "$report_file"

    git reset --soft HEAD~1
    exit 1
fi

# 检查是否是 merge commit（merge commit 豁免）
subject=$(git log -1 --format=%s)
if echo "$subject" | grep -qi '^merge '; then
    exit 0
fi

# === non-GW commit 检测到，自动 revert ===
echo ""
echo "[POST-COMMIT-GUARD] 检测到 non-GW commit（未通过 GitCommitGateway）"
echo "[POST-COMMIT-GUARD] commit subject: $subject"
echo "[POST-COMMIT-GUARD] 自动执行 git reset --soft HEAD~1（保留修改在 staging area）"
echo "[POST-COMMIT-GUARD] 请通过 GitCommitGateway 重新提交（见 AGENTS.md §8）"
echo ""

# 记录违规到审计日志
mkdir -p .runtime/reconcile_reports
timestamp=$(date +%s)
hash=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
report_file=".runtime/reconcile_reports/post_commit_guard_${timestamp}.json"
# 转义 subject 中的特殊字符用于 JSON
escaped_subject=$(echo "$subject" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n' | head -c 200)
echo "{\"gate_id\":\"POST-COMMIT-GUARD\",\"timestamp\":$timestamp,\"hash\":\"$hash\",\"subject\":\"$escaped_subject\",\"action\":\"reset_soft_HEAD~1\"}" > "$report_file"

# 自动 revert（soft reset 保留修改在 staging area）
git reset --soft HEAD~1

exit 1
