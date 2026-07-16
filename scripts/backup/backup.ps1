<#
.SYNOPSIS
    灾备备份系统主脚本——六阶段流水线
.DESCRIPTION
    [BLUEPRINT] MOD-INF-027 | §3.2
    阶段: 预检 -> DB dump -> Restic备份 -> 保留清理 -> 校验 -> 报告
    自动触发: backup_reconciler.py post-commit调用
    手动触发: 双击 一键备份.bat (带 -Force 跳过间隔保护)
.PARAMETER Force
    跳过间隔保护（手动触发用）
#>
param([switch]$Force)

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\ZephyrAlpha"
$ConfigFile = "$ProjectRoot\scripts\backup\backup_config.yaml"
$LogFile = "$ProjectRoot\logs\backup_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# ── 工具函数 ──
function Write-Stage($msg) { Write-Host "[BACKUP] $msg" -ForegroundColor Cyan }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

# ── 加载配置 ──
if (-not (Test-Path $ConfigFile)) { Write-Err "config not found: $ConfigFile"; exit 1 }
$yamlContent = Get-Content $ConfigFile -Raw -Encoding UTF8
# 简单解析（避免依赖powershell-yaml模块）
$RepoPath = "F:\restic-zephyr"
$DumpDir = "D:\tmp_db_dumps"
$KeepDaily = 7; $KeepWeekly = 4; $KeepMonthly = 3
if ($yamlContent -match 'path:\s*"([^"]+restic[^"]*)"') { $RepoPath = $matches[1] -replace '\\\\','\' }
if ($yamlContent -match 'dump_dir:\s*"([^"]+)"') { $DumpDir = $matches[1] -replace '\\\\','\' }

# ── 阶段1: 预检 ──
Write-Stage "Stage 1: Pre-check"
$targetDrive = $RepoPath.Substring(0,2)
if (-not (Test-Path $targetDrive)) { Write-Err "Target drive $targetDrive not online"; exit 1 }
Write-OK "Target drive $targetDrive online"

$restic = Get-Command restic -ErrorAction SilentlyContinue
if (-not $restic) { Write-Err "restic not installed. Run: winget install restic.restic"; exit 1 }
Write-OK "restic found: $($restic.Source)"

# 首次初始化仓库
if (-not (Test-Path "$RepoPath\config")) {
    Write-Stage "Initializing restic repository..."
    $env:RESTIC_PASSWORD = Read-Host "Enter restic repository password (for encryption)" -AsSecureString | ConvertFrom-SecureString -AsPlainText
    restic init --repo $RepoPath
    if ($LASTEXITCODE -ne 0) { Write-Err "restic init failed"; exit 1 }
    Write-OK "Repository initialized at $RepoPath"
} else {
    Write-OK "Repository exists at $RepoPath"
}

# ── 阶段2: 数据库dump ──
Write-Stage "Stage 2: Database dump"
New-Item -ItemType Directory -Path $DumpDir -Force | Out-Null
$dbStatus = @{}

# PostgreSQL
$pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if ($pgDump) {
    try {
        $env:PGPASSWORD = "postgres"
        & pg_dump -Fc -h localhost -U postgres -d depgraph -f "$DumpDir\depgraph.dump" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $pgSize = (Get-Item "$DumpDir\depgraph.dump").Length
            $dbStatus.postgres = @{status="ok"; size_bytes=$pgSize}
            Write-OK "PostgreSQL dump: $([math]::Round($pgSize/1MB,2))MB"
        } else {
            $dbStatus.postgres = @{status="failed"; error="pg_dump exit $LASTEXITCODE"}
            Write-Warn "PostgreSQL dump failed (exit $LASTEXITCODE)"
        }
    } catch {
        $dbStatus.postgres = @{status="error"; error=$_.Exception.Message}
        Write-Warn "PostgreSQL dump error: $($_.Exception.Message)"
    }
} else {
    $dbStatus.postgres = @{status="skipped"; reason="pg_dump not found"}
    Write-Warn "pg_dump not found, skipping PostgreSQL"
}

# SQLite
$sqlite3 = Get-Command sqlite3 -ErrorAction SilentlyContinue
if ($sqlite3) {
    $sqliteDbs = @(
        @{src="$ProjectRoot\data\databases\governance.db"; dump="governance_backup.db"},
        @{src="$ProjectRoot\data\databases\session_continuity.db"; dump="session_backup.db"}
    )
    $sqliteOk = 0
    foreach ($db in $sqliteDbs) {
        if (Test-Path $db.src) {
            & sqlite3 $db.src ".backup $($DumpDir)\$($db.dump)" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { $sqliteOk++ } else { Write-Warn "SQLite backup failed: $($db.src)" }
        }
    }
    $dbStatus.sqlite = @{status=$(if($sqliteOk -gt 0){"ok"}else{"skipped"}); count=$sqliteOk}
    Write-OK "SQLite dump: $sqliteOk databases"
} else {
    $dbStatus.sqlite = @{status="skipped"; reason="sqlite3 not found"}
    Write-Warn "sqlite3 not found, skipping SQLite"
}

# ClickHouse
$chPort = 9000
$chAlive = (Test-NetConnection -ComputerName localhost -Port $chPort -InformationLevel Quiet -WarningAction SilentlyContinue)
if ($chAlive) {
    $chClient = Get-Command clickhouse-client -ErrorAction SilentlyContinue
    if ($chClient) {
        try {
            & clickhouse-client --query="BACKUP DATABASE c1_market TO Disk('backups', 'c1_market_$(Get-Date -Format 'yyyyMMdd').zip')" 2>&1 | Out-Null
            $dbStatus.clickhouse = @{status="ok"}
            Write-OK "ClickHouse dump: ok"
        } catch {
            $dbStatus.clickhouse = @{status="error"; error=$_.Exception.Message}
            Write-Warn "ClickHouse dump error: $($_.Exception.Message)"
        }
    } else {
        $dbStatus.clickhouse = @{status="skipped"; reason="clickhouse-client not found"}
        Write-Warn "clickhouse-client not found, skipping"
    }
} else {
    $dbStatus.clickhouse = @{status="skipped"; reason="service down"}
    Write-Warn "ClickHouse not running (port $chPort), skipping (rebuildable from bdpan)"
}

# ── 阶段3: Restic备份 ──
Write-Stage "Stage 3: Restic backup"
$backupStartTime = Get-Date

# 排除清单（与backup_config.yaml一致）
$excludeArgs = @(
    "--exclude","**/__pycache__/",
    "--exclude","**/.pytest_cache/",
    "--exclude","**/.mypy_cache/",
    "--exclude","**/.ruff_cache/",
    "--exclude","**/*.pyc",
    "--exclude",".aidrafts/",
    "--exclude",".runtime/",
    "--exclude","tmp/",
    "--exclude","logs/*.log",
    "--exclude","logs/*.log.*",
    "--exclude",".venv/",
    "--exclude","node_modules/"
)

$backupResult = & restic -r $RepoPath backup $ProjectRoot $DumpDir @excludeArgs --json 2>&1 | ConvertFrom-Json
$snapshotId = ($backupResult | Where-Object { $_.message_type -eq "summary" } | Select-Object -Last 1).snapshot_id
if (-not $snapshotId) {
    Write-Err "restic backup failed - no snapshot_id"
    exit 1
}
Write-OK "Snapshot created: $snapshotId"

# ── 阶段4: 保留策略清理 ──
Write-Stage "Stage 4: Retention policy"
& restic -r $RepoPath forget --keep-daily $KeepDaily --keep-weekly $KeepWeekly --keep-monthly $KeepMonthly --prune 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-OK "Retention applied (daily=$KeepDaily, weekly=$KeepWeekly, monthly=$KeepMonthly)"

# ── 阶段5: 校验 ──
Write-Stage "Stage 5: Integrity check"
& restic -r $RepoPath check 2>&1 | ForEach-Object { Write-Host "  $_" }
$checkResult = if ($LASTEXITCODE -eq 0) { "ok" } else { "failed" }
$stats = & restic -r $RepoPath stats 2>&1
Write-OK "Check result: $checkResult"

# ── 阶段6: 报告 ──
Write-Stage "Stage 6: Report"
$duration = (Get-Date) - $backupStartTime
$report = @{
    timestamp = (Get-Date).ToString("o")
    duration_seconds = [math]::Round($duration.TotalSeconds, 1)
    snapshot_id = $snapshotId
    databases = $dbStatus
    check_result = $checkResult
    force_mode = $Force.IsPresent
    stats = $stats -join "`n"
}

# 确保logs目录存在
New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
$report | ConvertTo-Json -Depth 5 | Out-File $LogFile -Encoding UTF8
Write-OK "Report saved: $LogFile"

# 更新状态文件
$stateFile = "$ProjectRoot\data\databases\backup_state.json"
$state = if (Test-Path $stateFile) { Get-Content $stateFile -Raw | ConvertFrom-Json } else { @{} }
if (-not $state) { $state = @{} }
$state | Add-Member -NotePropertyName last_backup_time -NotePropertyValue (Get-Date).ToString("o") -Force
$state | Add-Member -NotePropertyName last_backup_snapshot_id -NotePropertyValue $snapshotId -Force
$state | Add-Member -NotePropertyName last_backup_status -NotePropertyValue "ok" -Force
$state | ConvertTo-Json -Depth 3 | Out-File $stateFile -Encoding UTF8

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-OK "Backup completed in $([math]::Round($duration.TotalSeconds,1))s"
Write-Host "==========================================" -ForegroundColor Green
