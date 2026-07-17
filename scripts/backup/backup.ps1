<#
.SYNOPSIS
    Disaster backup system main script - six-stage pipeline
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.2
    Stages: Pre-check -> DB dump -> Restic backup -> Retention cleanup -> Integrity check -> Report
    Auto-trigger: backup_reconciler.py post-commit call
    Manual trigger: run backup_manual.ps1 (with -Force to skip interval protection)
.PARAMETER Force
    Skip interval protection (for manual trigger)
#>
param([switch]$Force)

# Note: not using 'Stop' - native command (restic/pg_dump) writing to stderr triggers NativeCommandError that terminates script
$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"
$ConfigFile = "$ProjectRoot\scripts\backup\backup_config.yaml"
$LogFile = "$ProjectRoot\logs\backup_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

# -- Utility functions --
function Write-Stage($msg) { Write-Host "[BACKUP] $msg" -ForegroundColor Cyan }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

# -- Load config --
if (-not (Test-Path $ConfigFile)) { Write-Err "config not found: $ConfigFile"; exit 1 }
$yamlContent = Get-Content $ConfigFile -Raw -Encoding UTF8

# Read RESTIC_PASSWORD from config/.env.restic (env var unavailable when auto-triggered)
$resticEnvFile = "$ProjectRoot\config\.env.restic"
if (-not $env:RESTIC_PASSWORD -and (Test-Path $resticEnvFile)) {
    $envContent = Get-Content $resticEnvFile -Encoding UTF8
    foreach ($line in $envContent) {
        if ($line -match '^RESTIC_PASSWORD=(.+)$') {
            $env:RESTIC_PASSWORD = $matches[1].Trim()
            break
        }
    }
}
if (-not $env:RESTIC_PASSWORD) {
    Write-Err "RESTIC_PASSWORD not set. Set env var or create config/.env.restic"
    exit 1
}

# Simple parsing (avoid depending on powershell-yaml module)
$RepoPath = "F:\restic-zephyr"
$DumpDir = "D:\tmp_db_dumps"
$KeepDaily = 7; $KeepWeekly = 4; $KeepMonthly = 3
if ($yamlContent -match 'path:\s*"([^"]+restic[^"]*)"') { $RepoPath = $matches[1] -replace '\\\\','\' }
if ($yamlContent -match 'dump_dir:\s*"([^"]+)"') { $DumpDir = $matches[1] -replace '\\\\','\' }

# -- Stage 1: Pre-check --
Write-Stage "Stage 1: Pre-check"
$targetDrive = $RepoPath.Substring(0,2)
if (-not (Test-Path $targetDrive)) { Write-Err "Target drive $targetDrive not online"; exit 1 }
Write-OK "Target drive $targetDrive online"

$restic = Get-Command restic -ErrorAction SilentlyContinue
if (-not $restic) { Write-Err "restic not installed. Run: winget install restic.restic"; exit 1 }
Write-OK "restic found: $($restic.Source)"

# Initialize repository on first run
if (-not (Test-Path "$RepoPath\config")) {
    Write-Stage "Initializing restic repository..."
    restic init --repo $RepoPath
    if ($LASTEXITCODE -ne 0) { Write-Err "restic init failed"; exit 1 }
    Write-OK "Repository initialized at $RepoPath"
} else {
    Write-OK "Repository exists at $RepoPath"
}

# -- Stage 2: Database dump --
Write-Stage "Stage 2: Database dump"
New-Item -ItemType Directory -Path $DumpDir -Force | Out-Null
$dbStatus = @{}

# PostgreSQL
# Resolve pg_dump: PATH first, fallback to standard install dirs (highest version wins)
$pgDumpCmd = $null
$pgDumpInPath = Get-Command pg_dump -ErrorAction SilentlyContinue
if ($pgDumpInPath) {
    $pgDumpCmd = $pgDumpInPath.Source
} else {
    $pgDumpCmd = Get-ChildItem "C:\Program Files\PostgreSQL\*\bin\pg_dump.exe" -ErrorAction SilentlyContinue |
        Sort-Object { [int]($_.FullName -replace '.*\\PostgreSQL\\(\d+)\\.*', '$1') } -Descending |
        Select-Object -First 1 -ExpandProperty FullName
}
if ($pgDumpCmd) {
    try {
        # Read PostgreSQL credentials from config/.env.postgres (avoid hardcoding)
        $pgEnvFile = "$ProjectRoot\config\.env.postgres"
        $pgUser = "postgres"; $pgPassword = ""
        if (Test-Path $pgEnvFile) {
            $pgEnv = Get-Content $pgEnvFile -Encoding UTF8
            foreach ($line in $pgEnv) {
                if ($line -match '^POSTGRES_USER=(.+)$') { $pgUser = $matches[1].Trim() }
                if ($line -match '^POSTGRES_PASSWORD=(.+)$') { $pgPassword = $matches[1].Trim() }
            }
        }
        $env:PGPASSWORD = $pgPassword
        & $pgDumpCmd -Fc -h localhost -U $pgUser -d depgraph -f "$DumpDir\depgraph.dump" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $pgSize = (Get-Item "$DumpDir\depgraph.dump").Length
            $dbStatus.postgres = @{status="ok"; size_bytes=$pgSize}
            Write-OK "PostgreSQL dump: $([math]::Round($pgSize/1MB,2))MB"
        } else {
            $dbStatus.postgres = @{status="failed"; error="pg_dump exit $LASTEXITCODE"}
            Write-Warn "PostgreSQL dump failed (exit $LASTEXITCODE)"
        }
        # Dump cluster globals (roles) - pg_dumpall -g requires superuser (zephyr has no pg_authid
        # access), so generate CREATE ROLE from the public pg_roles view. Passwords are masked in
        # pg_roles; restore runbook: reset passwords from config/.env.postgres after restore.
        $psqlCmd = $pgDumpCmd -replace 'pg_dump\.exe$', 'psql.exe'
        if (Test-Path $psqlCmd) {
            $roleQuery = "SELECT 'CREATE ROLE ' || quote_ident(rolname) || ' WITH ' || CASE WHEN rolcanlogin THEN 'LOGIN' ELSE 'NOLOGIN' END || CASE WHEN rolsuper THEN ' SUPERUSER' ELSE '' END || CASE WHEN rolcreatedb THEN ' CREATEDB' ELSE '' END || CASE WHEN rolcreaterole THEN ' CREATEROLE' ELSE '' END || ';' FROM pg_roles WHERE rolname !~ '^pg_' AND rolname <> 'postgres' ORDER BY rolname;"
            $globalsOut = & $psqlCmd -h localhost -U $pgUser -d postgres -t -A -c $roleQuery 2>$null
            if ($LASTEXITCODE -eq 0) {
                $globalsHeader = "-- PG cluster roles from pg_roles (passwords masked; reset from config/.env.postgres after restore)"
                [System.IO.File]::WriteAllText("$DumpDir\pg_globals.sql", "$globalsHeader`n$($globalsOut -join "`n")`n", (New-Object System.Text.UTF8Encoding($false)))
                $dbStatus.postgres_globals = @{status="ok"}
                Write-OK "PostgreSQL globals dump: ok"
            } else {
                $dbStatus.postgres_globals = @{status="failed"; error="psql exit $LASTEXITCODE"}
                Write-Warn "PostgreSQL globals dump failed (exit $LASTEXITCODE)"
            }
        } else {
            $dbStatus.postgres_globals = @{status="skipped"; reason="psql not found"}
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
$sqliteDbs = @(
    @{src="$ProjectRoot\data\databases\governance.db"; dump="governance_backup.db"},
    @{src="$ProjectRoot\data\databases\session_continuity.db"; dump="session_backup.db"}
)
$sqliteOk = 0
foreach ($db in $sqliteDbs) {
    if (Test-Path $db.src) {
        if ($sqlite3) {
            & sqlite3 $db.src ".backup $($DumpDir)\$($db.dump)" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { $sqliteOk++ } else { Write-Warn "sqlite3 backup failed: $($db.src), trying Python fallback" }
        }
        # Python fallback (when sqlite3 unavailable or failed)
        if (-not $sqlite3 -or $LASTEXITCODE -ne 0) {
            $pyResult = & python -c "import sqlite3; src=r'$($db.src)'; dst=r'$DumpDir\$($db.dump)'; con=sqlite3.connect(src); con.backup(sqlite3.connect(dst)); con.close(); print('ok')" 2>&1
            if ($pyResult -match 'ok') { $sqliteOk++ } else { Write-Warn "Python SQLite backup also failed: $($db.src)" }
        }
    }
}
$dbStatus.sqlite = @{status=$(if($sqliteOk -gt 0){"ok"}else{"skipped"}); count=$sqliteOk}
Write-OK "SQLite dump: $sqliteOk databases"

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

# -- Stage 3: Restic backup --
Write-Stage "Stage 3: Restic backup"
$backupStartTime = Get-Date

# Exclude list (aligned with backup_config.yaml)
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
    "--exclude","node_modules/",
    "--exclude","metadata/",
    "--exclude","access/",
    "--exclude","preprocessed_configs/",
    "--exclude","status",
    "--exclude","uuid"
)

# restic --json outputs JSON to stdout, progress info to stderr; avoid 2>&1 to prevent stderr mixing into stdout causing ConvertFrom-Json failure
$backupResult = & restic -r $RepoPath backup $ProjectRoot $DumpDir @excludeArgs --json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne 3) { Write-Err "restic backup failed (exit $LASTEXITCODE)"; exit 1 }
if ($LASTEXITCODE -eq 3) { Write-Warn "restic backup completed with warnings (some files could not be read)" }
$snapshotId = ($backupResult | Where-Object { $_.message_type -eq "summary" } | Select-Object -Last 1).snapshot_id
if (-not $snapshotId) {
    Write-Err "restic backup failed - no snapshot_id in summary"
    exit 1
}
Write-OK "Snapshot created: $snapshotId"

# -- Stage 4: Retention policy cleanup --
Write-Stage "Stage 4: Retention policy"
& restic -r $RepoPath forget --keep-daily $KeepDaily --keep-weekly $KeepWeekly --keep-monthly $KeepMonthly --prune 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-OK "Retention applied (daily=$KeepDaily, weekly=$KeepWeekly, monthly=$KeepMonthly)"

# -- Stage 5: Integrity check --
Write-Stage "Stage 5: Integrity check"
& restic -r $RepoPath check 2>&1 | ForEach-Object { Write-Host "  $_" }
$checkResult = if ($LASTEXITCODE -eq 0) { "ok" } else { "failed" }
$stats = & restic -r $RepoPath stats 2>&1
Write-OK "Check result: $checkResult"

# -- Stage 6: Report --
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

# Ensure logs directory exists
New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
$report | ConvertTo-Json -Depth 5 | Out-File $LogFile -Encoding UTF8
Write-OK "Report saved: $LogFile"

# Update state file
$stateFile = "$ProjectRoot\data\databases\backup_state.json"
# Note: $state must be PSCustomObject - ConvertTo-Json drops note properties attached to a hashtable
$state = if (Test-Path $stateFile) { Get-Content $stateFile -Raw | ConvertFrom-Json } else { [PSCustomObject]@{} }
if (-not $state) { $state = [PSCustomObject]@{} }
$state | Add-Member -NotePropertyName last_backup_time -NotePropertyValue (Get-Date).ToString("o") -Force
$state | Add-Member -NotePropertyName last_backup_snapshot_id -NotePropertyValue $snapshotId -Force
$state | Add-Member -NotePropertyName last_backup_status -NotePropertyValue "ok" -Force
# Write UTF-8 without BOM + LF (ENCODING-SAFETY INJ-007; PS5.1 Out-File -Encoding UTF8 emits BOM)
$stateJson = ($state | ConvertTo-Json -Depth 3) -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($stateFile, $stateJson, (New-Object System.Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-OK "Backup completed in $([math]::Round($duration.TotalSeconds,1))s"
Write-Host "==========================================" -ForegroundColor Green
