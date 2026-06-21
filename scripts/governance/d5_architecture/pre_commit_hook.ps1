﻿﻿﻿﻿﻿﻿# PRE-COMMIT HOOK — 蓝图-代码对齐闸门
# 铁律六 + L3 预防层：任何模块代码变更时，强制验证蓝图 construction_progress 与磁盘对齐
#
# 安装：Copy-Item scripts/governance/d5_architecture/pre_commit_hook.ps1 .git/hooks/pre_commit
#
# 逻辑：
#   1. 检测 staged 变更中涉及哪些 src/zephyr/ 子模块
#   2. 映射到对应的 blueprint.md 路径
#   3. 运行 validate_blueprint_implementation_docs.py
#   4. 发现不对齐 → 阻止提交（exit 非零）
param()

$ErrorActionPreference = "Stop"
$REPO_ROOT = (git rev-parse --show-toplevel)

$STAGED_FILES = git diff --cached --name-only --diff-filter=ACM
$CHANGED_MODULES = @{}

foreach ($f in $STAGED_FILES) {
    if ($f -match '^src/zephyr/([^/]+)/') {
        $module = $Matches[1]
        $CHANGED_MODULES[$module] = $true
    }
}

if ($CHANGED_MODULES.Count -eq 0) {
    exit 0
}

Write-Host "[PRE-COMMIT] 铁律六/L3 检查：检测到以下模块有代码变更：$($CHANGED_MODULES.Keys -join ', ')"
Write-Host "[PRE-COMMIT] 运行蓝图-代码对齐验证..."

$VALIDATE_SCRIPT = Join-Path $REPO_ROOT "scripts/governance/d5_architecture/validate_blueprint_implementation_docs.py"
$PYTHON_EXE = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PYTHON_EXE) {
    Write-Host "[PRE-COMMIT] 错误：找不到 python"
    exit 1
}

$output = & $PYTHON_EXE $VALIDATE_SCRIPT 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host $output
    Write-Host ""
    Write-Host "=" * 60
    Write-Host "[PRE-COMMIT] 铁律六阻断：蓝图-代码不对齐！"
    Write-Host "[PRE-COMMIT] 行动指南："
    Write-Host "  1. 确认你的代码变更涉及哪些模块"
    Write-Host "  2. 阅读对应模块的 blueprint.md"
    Write-Host "  3. 更新 blueprint.md 中 construction_progress 和实现状态节"
    Write-Host "  4. 重新提交"
    Write-Host "=" * 60
    exit 1
}

Write-Host "[PRE-COMMIT] 蓝图-代码对齐验证通过。"
exit 0
