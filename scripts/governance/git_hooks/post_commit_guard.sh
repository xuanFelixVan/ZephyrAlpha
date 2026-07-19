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
# session_id 未注册时的双层检测（修复 2026-07-09）：
#   1. ZEPHYR_COMMIT_GATEWAY=1 → 通过 GitCommitGateway 的合法 commit
#      （session 过期/allow_overlap 逃生通道）→ warn-only，不 reset
#   2. ZEPHYR_COMMIT_GATEWAY 未设置 → 伪造 GW 标记 → reset
#   原逻辑：session_id 未注册一律 reset，导致 allow_overlap 逃生通道的
#   合法 commit 被误判为伪造，连带回滚主 commit + auto-sync commits
#
# 高基数 --no-verify 阻断（ARCH-TOOL-HEALTH-V1 Phase 5，2026-07-19；裁定 B 修复 2026-07-19）：
#   warn-only 路径（ZEPHYR_COMMIT_GATEWAY=1 + session 未注册）是逃生通道，
#   但短时间内反复触发 = 系统性问题（注册表 bug 或 --no-verify 滥用）。
#
#   原设计（per-session 24h ≥3）：上线后实测 0 次 block——session 典型寿命 1-3 commits，
#   prior_warn_count 实测 max=2 永远到不了阈值 3，结构性失效。
#
#   治本（per-hour aggregate）：统计 1 小时滚动窗口内全局 warn-only 次数（不限 session），
#   超阈值（默认 10，可由 POST_COMMIT_GUARD_NO_VERIFY_THRESHOLD 环境变量覆盖）则升级为阻断（reset）。
#   计数真源：.runtime/reconcile_reports/post_commit_guard_*.json 中
#   violation=unregistered_session_id + action=warn_only 的报告。
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

    # session_id 未注册 → 检查环境变量确认是否通过 GitCommitGateway
    # ZEPHYR_COMMIT_GATEWAY=1 由 GitCommitGateway._run_git 设置，post-commit hook 继承
    # 修复 bug（2026-07-09）：allow_overlap=True 逃生通道不注册 session，
    # 导致合法 commit 被误判为伪造并 reset，连带回滚主 commit + auto-sync commits
    if [ "$ZEPHYR_COMMIT_GATEWAY" = "1" ]; then
        # 环境变量确认通过 GitCommitGateway → warn-only（session 过期/allow_overlap 逃生通道）
        #
        # === 高基数 --no-verify 检测（ARCH-TOOL-HEALTH-V1 Phase 5 治本；裁定 B 修复 2026-07-19）===
        # 病根：warn-only 是 allow_overlap 逃生通道（session 过期+合法 GW commit），
        # 但短时间内反复触发 = 系统性问题（session 注册表 bug 或滥用 --no-verify）。
        # 治本（per-hour aggregate）：统计 1h 滚动窗口内全局 warn-only 次数（不限 session），
        # 超阈值则升级为阻断（reset）。阈值默认 10（可由 POST_COMMIT_GUARD_NO_VERIFY_THRESHOLD 覆盖）。
        # 原设计（per-session 24h ≥3）结构性失效：session 典型寿命 1-3 commits，prior_warn_count max=2 永远到不了 3。

        NO_VERIFY_BLOCK_THRESHOLD="${POST_COMMIT_GUARD_NO_VERIFY_THRESHOLD:-10}"
        NO_VERIFY_WINDOW_SECONDS="${POST_COMMIT_GUARD_NO_VERIFY_WINDOW_SECONDS:-3600}"
        now_ts=$(date +%s)
        window_start_ts=$((now_ts - NO_VERIFY_WINDOW_SECONDS))
        prior_warn_count=0

        # 解析 reports 目录（复用上方 repo_root 逻辑，处理 worktree 场景）
        if [ -n "$repo_root" ]; then
            reports_dir="$repo_root/.runtime/reconcile_reports"
        else
            reports_dir=".runtime/reconcile_reports"
        fi

        if [ -d "$reports_dir" ]; then
            # === 7天前报告清理（ARCH-TOOL-HEALTH-V1 Phase 5 优化，2026-07-19）===
            # 病根：reports_dir 中旧报告永不清理，for 循环随文件数增长变慢
            # 治本：每次 post-commit 事件触发时顺带清理 7 天前的 post_commit_guard_*.json
            # 事件触发（非时间触发），符合永久系统全自动原则
            find "$reports_dir" -name "post_commit_guard_*.json" -mtime +7 -delete 2>/dev/null || true

            for rpt in "$reports_dir"/post_commit_guard_*.json; do
                [ -f "$rpt" ] || continue
                # 提取字段：grep 模式容忍可选空格（兼容紧凑/空格两种 JSON 格式）
                # timestamp：提取所有数字（sed 去除非数字字符，兼容 "ts":123 与 "ts": 123）
                rpt_ts=$(grep -o '"timestamp": *[0-9]*' "$rpt" 2>/dev/null | head -1 | sed 's/[^0-9]//g')
                rpt_sid=$(grep -o '"session_id": *"[^"]*"' "$rpt" 2>/dev/null | head -1 | cut -d\" -f4)
                rpt_violation=$(grep -o '"violation": *"[^"]*"' "$rpt" 2>/dev/null | head -1 | cut -d\" -f4)
                rpt_action=$(grep -o '"action": *"[^"]*"' "$rpt" 2>/dev/null | head -1 | cut -d\" -f4)
                # 数值比较（rpt_ts 非空且为数字时才比较；2>/dev/null 抑制非数字报错）
                if [ -n "$rpt_ts" ] && [ "$rpt_ts" -ge "$window_start_ts" ] 2>/dev/null; then
                    # 提取 prior_warn_count 字段（阈值上线前的旧版报告无此字段）
                    # 过滤旧版报告避免历史遗留污染新 session 累计（ARCH-TOOL-HEALTH-V1 Phase 5 优化，2026-07-19）
                    rpt_prior=$(grep -o '"prior_warn_count": *[0-9]*' "$rpt" 2>/dev/null | head -1 | sed 's/[^0-9]//g')
                    # 裁定 B 修复（2026-07-19）：取消 per-session 过滤 [ "$rpt_sid" = "$session_id" ]，
                    # 改为 per-hour aggregate——统计窗口内所有 session 的 warn-only 事件，
                    # 才能真正捕捉"短时间内反复逃生"的系统性问题。
                    # rpt_prior 非空 = 新版报告（阈值上线后），计入累计；为空 = 旧版报告，跳过
                    if [ -n "$rpt_prior" ] && [ "$rpt_violation" = "unregistered_session_id" ] && [ "$rpt_action" = "warn_only" ]; then
                        prior_warn_count=$((prior_warn_count + 1))
                    fi
                fi
            done
        fi

        # 超阈值 → 升级为阻断（ARCH-TOOL-HEALTH-V1 Phase 5）
        if [ "$prior_warn_count" -ge "$NO_VERIFY_BLOCK_THRESHOLD" ]; then
            echo ""
            echo "[POST-COMMIT-GUARD] BLOCK: 1h 内全局累计 $prior_warn_count 次 warn-only（阈值 $NO_VERIFY_BLOCK_THRESHOLD）"
            echo "[POST-COMMIT-GUARD] 疑似 session 注册表异常或 --no-verify 滥用，强制升级为阻断"
            echo "[POST-COMMIT-GUARD] 自动执行 git reset --soft HEAD~1（保留修改在 staging area）"
            echo "[POST-COMMIT-GUARD] 排查：①SessionRegistry 是否正常运行 ②是否频繁 allow_overlap 逃生"
            echo ""
            mkdir -p "$reports_dir"
            timestamp=$(date +%s)
            hash=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
            report_file="$reports_dir/post_commit_guard_${timestamp}.json"
            escaped_sid=$(echo "$session_id" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n' | head -c 200)
            echo "{\"gate_id\":\"POST-COMMIT-GUARD\",\"timestamp\":$timestamp,\"hash\":\"$hash\",\"violation\":\"unregistered_session_id_high_rate\",\"session_id\":\"$escaped_sid\",\"gw_env\":\"1\",\"prior_warn_count\":$prior_warn_count,\"threshold\":$NO_VERIFY_BLOCK_THRESHOLD,\"window_seconds\":$NO_VERIFY_WINDOW_SECONDS,\"action\":\"reset_soft_HEAD~1\"}" > "$report_file"

            git reset --soft HEAD~1
            exit 1
        fi

        # 未超阈值 → warn-only（保留 commit，显示累计计数）
        echo ""
        echo "[POST-COMMIT-GUARD] WARN: session_id=$session_id 未在 SessionRegistry 注册"
        echo "[POST-COMMIT-GUARD] ZEPHYR_COMMIT_GATEWAY=1 确认通过 GitCommitGateway，commit 保留"
        echo "[POST-COMMIT-GUARD] warn-only 累计（1h 全局）: $prior_warn_count/$NO_VERIFY_BLOCK_THRESHOLD（超阈值将阻断）"
        echo ""

        # 记录到审计日志
        mkdir -p "$reports_dir"
        timestamp=$(date +%s)
        hash=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
        report_file="$reports_dir/post_commit_guard_${timestamp}.json"
        escaped_sid=$(echo "$session_id" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n' | head -c 200)
        echo "{\"gate_id\":\"POST-COMMIT-GUARD\",\"timestamp\":$timestamp,\"hash\":\"$hash\",\"violation\":\"unregistered_session_id\",\"session_id\":\"$escaped_sid\",\"gw_env\":\"1\",\"prior_warn_count\":$prior_warn_count,\"threshold\":$NO_VERIFY_BLOCK_THRESHOLD,\"action\":\"warn_only\"}" > "$report_file"

        exit 0
    fi

    # 环境变量不存在 → 伪造 GW 标记 → reset
    echo ""
    echo "[POST-COMMIT-GUARD] 检测到伪造 GW 标记（session_id=$session_id 未注册且 ZEPHYR_COMMIT_GATEWAY 未设置）"
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
