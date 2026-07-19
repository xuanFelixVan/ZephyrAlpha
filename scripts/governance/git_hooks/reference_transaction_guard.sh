#!/bin/sh
# =============================================================================
# REFERENCE-TRANSACTION-GUARD: git commit-tree + update-ref 绕过堵漏
# =============================================================================
# Phase 4 治本（2026-07-19）：堵漏 git commit-tree plumbing 命令绕过
# pre-commit AND post-commit hooks 的治理盲区。
#
# 病根（第一性原理）
# ------------------
# git 分两层：
#   - porcelain 命令（git commit / git merge / git reset）：触发 hook
#   - plumbing 命令（git commit-tree / git update-ref / git write-tree）：
#     不触发任何 hook
#
# POST-COMMIT-GUARD (#ARCH-050) 只在 post-commit hook 中运行，能拦截
# `git commit --no-verify`（--no-verify 跳 pre-commit，不跳 post-commit）。
# 但完全无法拦截 `git commit-tree` + `git update-ref` 组合——这俩 plumbing
# 命令不触发任何 hook，POST-COMMIT-GUARD 永远不会运行。
#
# P2-1 落地的 emergency_commit 就是用 commit-tree 实现的合法逃生通道，
# 但同样的路径可被 AI 用于绕过所有治理。需要 reference-transaction hook
# 在 ref update 时统一拦截。
#
# 治本（Phase 4）
# ---------------
# reference-transaction 是 git 2.45+ 的 hook，在 ref 事务提交时触发：
#   - prepared 状态：事务即将提交，exit non-zero 回滚整个事务
#   - committed 状态：事务已提交，informational only
#
# 本脚本在 prepared 状态检查 refs/heads/dev 的 forward 更新：
#   - 跳过 reset/rewind（old 不是 new 的祖先，如 git reset --soft HEAD~1）
#   - 跳过 deletion/creation（OID 含全零）
#   - 跳过 merge commit（2+ parents，已被 merge gate 校验）
#   - 跳过含 [GW: 标记的 commit（GitCommitGateway / session_worktree_*
#     / emergency_commit 的合法标识）
#   - 其余 → block（exit 1），事务回滚
#
# 合法标识（含 [GW: 标记的 commit）
#   - GitCommitGateway 常规 commit: [GW:{session_id}]
#   - GitCommitGateway auto-commit: [GW:{session_id}:auto]
#   - session_worktree_commit: [GW:{session_id}:worktree]
#   - session_worktree_merge: [GW:{session_id}:merge]
#   - emergency_commit: [GW:{session_id}:emergency]
#
# 豁免（不含 [GW: 但放行）
#   - merge commit（subject 以 "merge " 开头 OR 2+ parents）
#   - reset/rewind（POST-COMMIT-GUARD 的 git reset --soft HEAD~1 走这条路径）
#
# 安装：cp scripts/governance/git_hooks/reference_transaction_guard.sh .git/hooks/reference-transaction
#   或在 .git/hooks/reference-transaction 末尾追加调用本脚本
#
# 兼容性：git 2.45+（reference-transaction hook 引入版本）
# =============================================================================

# 处理状态参数：prepared / committed
state="$1"

# Debug log（启用 REF_TX_GUARD_DEBUG=1 时写调用日志，便于排查是否被 git 调用）
if [ "$REF_TX_GUARD_DEBUG" = "1" ]; then
    common_dir_dbg=$(git rev-parse --git-common-dir 2>/dev/null)
    if [ -n "$common_dir_dbg" ] && [ -d "$common_dir_dbg" ]; then
        repo_root_dbg=$(cd "$common_dir_dbg/.." && pwd)
    else
        repo_root_dbg=$(pwd)
    fi
    mkdir -p "$repo_root_dbg/.runtime"
    echo "[$(date +%s)] reference_transaction_guard invoked state=$state pid=$$ args=$*" >> "$repo_root_dbg/.runtime/ref_tx_guard_debug.log"
fi

# committed 状态：事务已落盘，无法回滚，仅 informational
if [ "$state" != "prepared" ]; then
    exit 0
fi

# 获取主仓库根目录（worktree 内 git-common-dir 指向主仓库 .git）
common_dir=$(git rev-parse --git-common-dir 2>/dev/null)
if [ -n "$common_dir" ] && [ -d "$common_dir" ]; then
    repo_root=$(cd "$common_dir/.." && pwd)
    reports_dir="$repo_root/.runtime/reconcile_reports"
else
    reports_dir=".runtime/reconcile_reports"
fi

# 零 OID（40 个 0）— deletion/creation 标识
ZERO_OID="0000000000000000000000000000000000000000"

# 读取 stdin：每行 "<old-oid> <new-oid> <ref-name>"
while read -r old_oid new_oid ref_name; do
    # Windows CRLF 兼容：strip 尾部 \r（Python subprocess / 文本模式 pipe 可能注入）
    old_oid=$(echo "$old_oid" | tr -d '\r')
    new_oid=$(echo "$new_oid" | tr -d '\r')
    ref_name=$(echo "$ref_name" | tr -d '\r')

    # 跳过空行
    [ -z "$ref_name" ] && continue

    # 只检查 refs/heads/dev（protected branch）
    # session/* 是 worktree 分支，不检查
    # stash / tags / HEAD 不检查
    if [ "$ref_name" != "refs/heads/dev" ]; then
        continue
    fi

    # 跳过 deletion（new 是全零）
    if [ "$new_oid" = "$ZERO_OID" ]; then
        continue
    fi

    # 跳过 creation（old 是全零）
    if [ "$old_oid" = "$ZERO_OID" ]; then
        continue
    fi

    # 跳过 reset/rewind：old 不是 new 的祖先 = backward 移动
    # POST-COMMIT-GUARD 的 git reset --soft HEAD~1 走这条路径
    if ! git merge-base --is-ancestor "$old_oid" "$new_oid" 2>/dev/null; then
        continue
    fi

    # === Forward commit — 应用治理检查 ===

    # 检查是否 merge commit（2+ parents）
    parent_line=$(git log -1 --format=%P "$new_oid" 2>/dev/null)
    parent_count=$(echo "$parent_line" | wc -w)
    if [ "$parent_count" -ge 2 ]; then
        continue  # Merge commit，已被 merge gate 校验
    fi

    # 获取 commit message
    commit_msg=$(git log -1 --format=%B "$new_oid" 2>/dev/null)

    # 检查是否含 [GW: 标记
    if echo "$commit_msg" | grep -q '\[GW:'; then
        continue  # 合法 gateway commit
    fi

    # === 检测到 non-GW commit-tree 绕过，BLOCK ===
    subject=$(git log -1 --format=%s "$new_oid" 2>/dev/null)
    echo ""
    echo "[REFERENCE-TRANSACTION-GUARD] BLOCK: refs/heads/dev forward 更新未通过 GitCommitGateway"
    echo "[REFERENCE-TRANSACTION-GUARD] commit: $new_oid"
    echo "[REFERENCE-TRANSACTION-GUARD] subject: $subject"
    echo "[REFERENCE-TRANSACTION-GUARD] commit message 缺少 [GW: 标记"
    echo "[REFERENCE-TRANSACTION-GUARD] 禁止用 git commit-tree + git update-ref 绕过 hook"
    echo "[REFERENCE-TRANSACTION-GUARD] 合法通道：GitCommitGateway / session_worktree_commit / emergency_commit"
    echo ""

    # 审计日志
    mkdir -p "$reports_dir"
    timestamp=$(date +%s)
    report_file="$reports_dir/reference_transaction_guard_${timestamp}.json"
    escaped_subject=$(echo "$subject" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n' | head -c 200)
    echo "{\"gate_id\":\"REFERENCE-TRANSACTION-GUARD\",\"timestamp\":$timestamp,\"old_oid\":\"$old_oid\",\"new_oid\":\"$new_oid\",\"ref\":\"$ref_name\",\"subject\":\"$escaped_subject\",\"action\":\"block\"}" > "$report_file"

    # exit 1 在 prepared 状态 → 整个事务回滚
    exit 1
done

exit 0
