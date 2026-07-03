# POST-COMMIT HOOK — 架构健康度仪表盘（第0期自动化检测基线）
# architecture_debt_registry.md §六 L5660-5667
#
# 安装：Copy-Item scripts/governance/d5_architecture/post_commit_architecture_health.ps1 .git/hooks/post_commit
#
# 逻辑：
#   1. commit 完成后事件触发（非阻断，第0期仅记录基线）
#   2. 运行 architecture_health_dashboard.py --snapshot
#   3. 快照保存到 data/architecture_health/dashboard_<ts>.json + latest.json
#   4. 不阻断 commit（exit 0 始终，第1期 AST 门禁才阻断）
#
# 设计原则：
#   - 事件触发（commit 事件），符合"永久系统必须全自动/事件触发"铁律
#   - 非阻断：第0期是基线建立，第1期才转 hard block
#   - 独立降级：仪表盘异常不影响 commit（try/catch exit 0）
param()
$ErrorActionPreference = "SilentlyContinue"

$REPO_ROOT = (git rev-parse --show-toplevel)
$DASHBOARD = Join-Path $REPO_ROOT "scripts\governance\architecture_health_dashboard.py"
$PYTHON_EXE = (Get-Command python -ErrorAction SilentlyContinue).Source

if (-not $PYTHON_EXE) {
    # 无 python 静默退出，不影响 commit
    exit 0
}

if (-not (Test-Path $DASHBOARD)) {
    exit 0
}

# 运行仪表盘（--snapshot 保存快照，非阻断）
# stdout/stderr 重定向到日志，不污染 commit 输出
$logDir = Join-Path $REPO_ROOT "data\architecture_health"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}
$logFile = Join-Path $logDir "post_commit_hook.log"

try {
    & $PYTHON_EXE $DASHBOARD --snapshot *> $logFile
} catch {
    # 仪表盘异常不影响 commit
    "post-commit dashboard failed: $_" | Out-File -FilePath $logFile -Append -Encoding utf8
}

exit 0
