<#
.SYNOPSIS
    灾备恢复脚本——查看/验证/灾难恢复
.DESCRIPTION
    [BLUEPRINT] MOD-INF-027 | §3.5
    子命令:
      list              - 列出所有快照
      verify <id>       - 恢复到 D:\restore_test\ 供验证
      latest            - 灾难恢复最新快照到 D:\ZephyrAlpha\
      latest -target X  - 恢复到指定目录
#>
param(
    [Parameter(Position=0)]
    [ValidateSet("list","verify","latest")]
    [string]$Action = "list",

    [Parameter(Position=1)]
    [string]$SnapshotId,

    [string]$Target
)

$RepoPath = "F:\restic-zephyr"
$ProjectRoot = "D:\ZephyrAlpha"

switch ($Action) {
    "list" {
        Write-Host "=== Restic Snapshots ===" -ForegroundColor Cyan
        & restic -r $RepoPath snapshots
    }
    "verify" {
        if (-not $SnapshotId) { Write-Host "Usage: restore.ps1 verify <snapshot-id>" -ForegroundColor Red; exit 1 }
        $verifyDir = "D:\restore_test"
        Write-Host "Restoring snapshot $SnapshotId to $verifyDir for verification..." -ForegroundColor Cyan
        if (Test-Path $verifyDir) { Remove-Item $verifyDir -Recurse -Force }
        & restic -r $RepoPath restore $SnapshotId --target $verifyDir
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Files restored to $verifyDir" -ForegroundColor Green
            Write-Host "Verify key files:"
            @("AGENTS.md","config\sla_targets.yaml","src\zephyr") | ForEach-Object {
                $p = Join-Path $verifyDir $_
                if (Test-Path $p) { Write-Host "  [OK] $_" -ForegroundColor Green }
                else { Write-Host "  [MISSING] $_" -ForegroundColor Red }
            }
        }
    }
    "latest" {
        $restoreTarget = if ($Target) { $Target } else { $ProjectRoot }
        Write-Host "DISASTER RECOVERY: Restoring latest snapshot to $restoreTarget" -ForegroundColor Yellow
        $confirm = Read-Host "This will overwrite files in $restoreTarget. Continue? (yes/no)"
        if ($confirm -ne "yes") { Write-Host "Aborted."; exit 0 }
        & restic -r $RepoPath restore latest --target $restoreTarget
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK: Latest snapshot restored to $restoreTarget" -ForegroundColor Green
        }
    }
}
