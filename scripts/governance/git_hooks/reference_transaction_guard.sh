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
#   - 跳过真回退（new 是 old 的祖先，如 git reset --soft HEAD~1）
#     注（红队加固 st-ff-rb-gov-20260918）：分叉（old/new 互不为祖先）不再当回退放行
#   - 跳过 deletion（new 全零）；creation 仅在 ref 真不存在时豁免
#     （红队加固 st-ff-rb-gov-20260918：update-ref 不带 <old> 时 old 恒报全零，
#      原'跳过 creation'成了万能豁免，现先探 ref 真实值再定）
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
    repo_root=$(pwd)
    reports_dir=".runtime/reconcile_reports"
fi
# 会话注册表锚点（红队加固 st-ff-rb-gov-20260918：分叉/伪造标记判定需要会话键真源）
registry_file="$repo_root/.runtime/session_registry.json"

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

    # === 红队加固①（st-ff-rb-gov-20260918 A1-5 实弹，2026-09-18 全流通战役攻面一）===
    # 病根（实测，非推断）：`git update-ref <ref> <new>` **不带 <old>** 时，git 交给
    # reference-transaction hook 的事务行里 old 恒为全零——与"分支创建"不可区分。
    # 于是原"跳过 creation"分支成了**万能豁免**：本 guard 想堵的
    # `commit-tree + update-ref`（Phase 4 立病根的那条）从未被检查过。
    # 证据（scratch 实弹 hook stdin dump）：
    #   带 old 的 CAS 形式 → "bc3e... 1af7... refs/heads/dev"（真 old/new 齐全）
    #   不带 old 的形式   → "0000...000 edb2... refs/heads/dev"（假 creation）
    # 治本：old 全零时先探该 ref 在 prepared 时刻的真实值——ref 存在=伪装成创建的移动，
    # 用真实 old 继续审查；ref 确实不存在=真创建，维持豁免（本 guard 只管 refs/heads/dev，
    # 该分支恒存在，故此路径实际只在别的 ref 上生效，不影响现网）。
    # 合法通道影响面（已核）：emergency_commit L708 与队列落地 commit_queue_landing
    # 都用 `update-ref <ref> <new> <old>` CAS 形式 → 走真 old 路径，行为不变。
    if [ "$old_oid" = "$ZERO_OID" ]; then
        real_old=$(git rev-parse --verify -q "$ref_name" 2>/dev/null)
        if [ -n "$real_old" ]; then
            echo "[REFERENCE-TRANSACTION-GUARD] old 全零但 $ref_name 实际存在($real_old)——按移动而非创建审查" >&2
            old_oid="$real_old"
        else
            continue  # 真 creation（分支尚不存在）
        fi
    fi

    # 跳过 reset/rewind：new 是 old 的祖先 = 真回退（如 git reset --soft HEAD~1）
    #
    # === 红队加固（st-ff-rb-gov-20260918，2026-09-18 全流通战役攻面一 A1-5）===
    # 病根：原判定只有一条 `! merge-base --is-ancestor old new → continue`，
    # 把"old 不是 new 的祖先"**全**当作 reset/rewind 静默放行。但 ref 移动有三态：
    #   快进(new 含 old) / 回退(new 是 old 祖先) / **分叉(互不为祖先)**。
    # 第三态此前无判据 → `git commit-tree -p <HEAD~n>` + `git update-ref refs/heads/dev`
    # 可把一笔从未过任何闸的提交直落 dev，同时把 n 笔**他人已落地提交**挤出主线
    # （scratch 实弹：dev 上 1 笔已落 GW 提交被静默吞出主线，事后 git log 不可见）。
    # 治本：先认真回退（new 是 old 的祖先 → 放行，POST-COMMIT-GUARD 的 reset 走这条），
    # 其余非快进=分叉，按正向更新对待（继续查 merge/标记），merge-base 自身异常
    # 也归入分叉（fail-closed：读不懂的移动必须能说出它是回退才放行）。
    if git merge-base --is-ancestor "$new_oid" "$old_oid" 2>/dev/null; then
        continue  # 真回退（rewind）
    fi
    if ! git merge-base --is-ancestor "$old_oid" "$new_oid" 2>/dev/null; then
        echo "[REFERENCE-TRANSACTION-GUARD] 检测到分叉式 ref 移动（old/new 互不为祖先），按正向更新审查" >&2
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

    # 检查是否含 [GW: 标记——红队加固（st-ff-rb-gov-20260918 A1-5b）：
    # 原判据只看子串 [GW: 是否存在，故任意伪造尾注（含拿注册表字段名当 sid）都能买通行证；
    # 现与 post_commit_guard.sh 同口径：提取 sid 集合后必须命中注册表会话键。
    # 该两段判定（会话键解析 + 成员校验）与 post_commit_guard.sh 互为孪生真源，
    # 改一处 MUST 同步另一处（shell 无共享库，刻意内联，不留第二套语义）。
    # ★ 孪生段如实登记（st-ff-gov2 真注册表布局端到端冒烟，2026-09-18）：本收紧只关掉
    #   "注册表字段名当通行证"，**未**关掉"冒充任一在活他人会话键"——判据是
    #   sid ∈ 会话键，不是 sid == 本笔归属。详见 post_commit_guard.sh L98-110 同段说明，
    #   攻面已登记交总包裁定，勿据本文件宣称"标记不可伪造"。
    gw_tokens=$(echo "$commit_msg" | grep -o '\[GW:[A-Za-z0-9_][A-Za-z0-9_-]*' | sed 's/^\[GW://' | sort -u)
    # 文档性提及豁免：message 里有 [GW: 字样但解析不出标识符（`[GW: 空格` 这种散文写法）
    # → 与 post_commit_guard.sh L64-67 同口径保守放行。
    # 红队自纠（本车道首版收紧漏了这条）：初版直接按"无可信 sid=伪造"处理，
    # 实测把 message 里引用 "[GW: 标记不可伪造" 字样的合法提交也拦死（正门被打）。
    if [ -z "$gw_tokens" ] && echo "$commit_msg" | grep -q '\[GW:'; then
        continue
    fi
    if [ -n "$gw_tokens" ]; then
        if [ ! -f "$registry_file" ]; then
            continue  # fail-open：注册表不存在（与 post_commit_guard.sh 同语义）
        fi
        registered_sids=$(grep -oE '^[[:space:]]{2,4}"[A-Za-z0-9_][A-Za-z0-9_-]*"[[:space:]]*:[[:space:]]*\{' "$registry_file" 2>/dev/null \
            | sed -E 's/.*"([^"]+)".*/\1/' | grep -vx sessions | sort -u)
        forged_token=""
        for sid in $gw_tokens; do
            # -x 整行 + -F 定长串：会话键逐字相等，字段名/路径片段不再充当通行证
            if ! printf '%s\n' "$registered_sids" | grep -qxF "$sid"; then
                forged_token="$sid"
                break
            fi
        done
        if [ -z "$forged_token" ]; then
            continue  # 全部标记都是注册会话 → 合法 gateway/emergency commit
        fi
        # 两条既有合法通道不得被本收紧打死（红队自纠，与 post_commit_guard.sh 分层对齐）：
        #   ① ZEPHYR_COMMIT_GATEWAY=1 = GitCommitGateway/session_worktree 的进程内标记，
        #      其会话可能因 90s 心跳窗被 SessionRegistry 剪除（warn-only 语义同源）；
        #   ② [GW:<sid>:emergency] = emergency_commit 合法逃生通道（其存在前提恰是
        #      "注册表/锁不可用"，此处硬拦等于在最需要时掐断唯一出路），
        #      该通道另有 reconcile_execution_log + emergency_track.jsonl + 滥用监控三重留痕。
        # 两者都改为**落审计不静默**：可疑但不阻断，事后可查。
        if [ "$ZEPHYR_COMMIT_GATEWAY" = "1" ] || echo "$commit_msg" | grep -q ':emergency]'; then
            mkdir -p "$reports_dir"
            _ts=$(date +%s)
            echo "{\"gate_id\":\"REFERENCE-TRANSACTION-GUARD\",\"timestamp\":$_ts,\"old_oid\":\"$old_oid\",\"new_oid\":\"$new_oid\",\"ref\":\"$ref_name\",\"violation\":\"unregistered_gw_sid\",\"session_id\":\"$forged_token\",\"gw_env\":\"${ZEPHYR_COMMIT_GATEWAY:-0}\",\"action\":\"warn_only\"}" > "$reports_dir/reference_transaction_guard_${_ts}.json"
            echo "[REFERENCE-TRANSACTION-GUARD] WARN: sid=$forged_token 非注册会话，但命中合法逃生通道（GW env / emergency），落审计放行" >&2
            continue
        fi
        echo "[REFERENCE-TRANSACTION-GUARD] 伪造 GW 标记：sid=$forged_token 不在 SessionRegistry 会话键内" >&2
    fi

    # === 检测到 non-GW commit-tree 绕过，BLOCK ===
    subject=$(git log -1 --format=%s "$new_oid" 2>/dev/null)
    echo ""
    echo "[REFERENCE-TRANSACTION-GUARD] BLOCK: refs/heads/dev forward 更新未通过 GitCommitGateway"
    echo "[REFERENCE-TRANSACTION-GUARD] commit: $new_oid"
    echo "[REFERENCE-TRANSACTION-GUARD] subject: $subject"
    echo "[REFERENCE-TRANSACTION-GUARD] commit message 缺少合法 [GW: 标记（缺失或伪造）"
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
