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

# -- Dynamic port selection --
# Hyper-V Host Network Service dynamically reserves random tcp ranges (2026-07-19
# incident: 9101-9200 reserved -> WinError 10013, MinIO would not start and the CH
# stage silently skipped). .env ports are preferences only; bind-test is the only
# reliable check.
function Test-PortFree([int]$Port) {
    $listener = $null
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        return $true
    } catch {
        return $false
    } finally {
        if ($listener) { $listener.Stop() }
    }
}

function Get-FreePort([int]$Preferred, [int[]]$Exclude = @()) {
    # Scan window +2000: HNS exclusion clusters observed 300+ ports wide
    # (9101-9400 on 2026-07-19), a +200 window cannot escape them (2026-07-19 fix).
    if (($Exclude -notcontains $Preferred) -and (Test-PortFree $Preferred)) { return $Preferred }
    for ($p = $Preferred + 1; $p -le [math]::Min($Preferred + 2000, 65535); $p++) {
        if ($Exclude -contains $p) { continue }
        if (Test-PortFree $p) { return $p }
    }
    throw "no free tcp port in [$Preferred, $($Preferred + 2000)] (HNS excluded ranges shifting?)"
}

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

# ClickHouse (c1_market + c3_fundamental) via MinIO S3 bridge
# Architecture: CH server runs in Hyper-V VM whose data disk (588G, 211G free) cannot
# hold a 315GiB full backup. MinIO runs on the HOST (localhost-only, Windows Firewall
# auto-blocks minio.exe so a python TCP relay on :9100 - already firewall-allowed -
# exposes it to the VM). CH streams BACKUP ... TO S3 straight out of the VM onto F:.
# Same object key "market.zip" every run: restic content-defined chunking dedups
# unchanged CH parts, so daily restic cost ~= new market data (~9GiB/day).
# Credentials: config/.env.ch_backup (gitignored), CH host: config/.env.clickhouse.
$chBkEnvFile = "$ProjectRoot\config\.env.ch_backup"
$chBk = @{}
if (Test-Path $chBkEnvFile) {
    foreach ($line in (Get-Content $chBkEnvFile -Encoding UTF8)) {
        if ($line -match '^([A-Z0-9_]+)=(.+)$') { $chBk[$matches[1]] = $matches[2].Trim() }
    }
}
$chHttpHost = "localhost"; $chHttpPort = 8123
$chEnvFile = "$ProjectRoot\config\.env.clickhouse"
if (Test-Path $chEnvFile) {
    foreach ($line in (Get-Content $chEnvFile -Encoding UTF8)) {
        if ($line -match '^CLICKHOUSE_HOST=(.+)$')      { $chHttpHost = $matches[1].Trim() }
        if ($line -match '^CLICKHOUSE_HTTP_PORT=(.+)$') { $chHttpPort = [int]$matches[1].Trim() }
    }
}
$chBaseUrl = "http://${chHttpHost}:${chHttpPort}/"
$chAlive = $false
try {
    curl.exe -s --max-time 5 $chBaseUrl --data-binary "SELECT 1" | Out-Null
    $chAlive = ($LASTEXITCODE -eq 0)
} catch { $chAlive = $false }

# CH 24h cadence gate (2026-07-19 fix): a full CH backup is ~315GiB/3h, so it is
# decoupled from the 8h code-backup cadence. last_ch_backup_time only advances on
# SUCCESS - a failed run retries at the next scheduled window. -Force bypasses
# (manual drills).
$chCadenceDue = $true
if (-not $Force) {
    $chStateFile = "$ProjectRoot\data\databases\backup_state.json"
    if (Test-Path $chStateFile) {
        try {
            $prevState = Get-Content $chStateFile -Raw -Encoding UTF8 | ConvertFrom-Json
            if ($prevState.last_ch_backup_time) {
                $chElapsedH = ((Get-Date) - [datetime]::Parse($prevState.last_ch_backup_time)).TotalHours
                if ($chElapsedH -lt 24) {
                    $chCadenceDue = $false
                }
            }
        } catch { }  # corrupt state -> treat as due
    }
}

$minioProc = $null; $relayProc = $null
if (-not $chAlive) {
    $dbStatus.clickhouse = @{status="skipped"; reason="service down"}
    Write-Warn "ClickHouse not reachable ($chBaseUrl), skipping"
} elseif ($chBk.Count -eq 0) {
    $dbStatus.clickhouse = @{status="skipped"; reason="config/.env.ch_backup missing"}
    Write-Warn "config/.env.ch_backup not found, skipping ClickHouse backup"
} elseif (-not $chCadenceDue) {
    $dbStatus.clickhouse = @{status="skipped"; reason=("24h cadence (last {0:N1}h ago)" -f $chElapsedH)}
    Write-OK ("ClickHouse: last CH backup {0:N1}h ago (< 24h cadence), stage skipped" -f $chElapsedH)
} else {
    try {
        # 1. Delete previous market.zip object BEFORE MinIO starts (plain FS delete in
        #    single-drive mode) so CH does not fail with BACKUP_ALREADY_EXISTS.
        $objDir = "$($chBk.MINIO_ROOT)\$($chBk.MINIO_BUCKET)\market.zip"
        if (Test-Path $objDir) { Remove-Item $objDir -Recurse -Force }
        # Stale write-lock + aborted multipart leftovers from a killed BACKUP run also
        # trigger BACKUP_ALREADY_EXISTS ("being written already") - remove them too.
        # (2026-07-18 incident: KILLed 315GiB BACKUP left market.zip.lock behind.)
        $objLock = "$objDir.lock"
        if (Test-Path $objLock) { Remove-Item $objLock -Recurse -Force }
        $mpDir = "$($chBk.MINIO_ROOT)\.minio.sys\multipart"
        if (Test-Path $mpDir) {
            Get-ChildItem $mpDir -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        }

        # 2. Kill stale MinIO/relay from previous runs, pick HNS-safe ports via
        #    bind-test, then start MinIO (localhost only) + python TCP relay
        #    (VM-facing, ports passed as argv). .env ports are preferences only -
        #    HNS reserved ranges shift across reboots.
        Get-Process -Name minio -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
        Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -match 'minio_tcp_relay' } |
            ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
        $minioPref = 9101; $consolePref = 9102; $relayPref = 9100
        if ($chBk.MINIO_ADDRESS -match ':(\d+)$')         { $minioPref = [int]$Matches[1] }
        if ($chBk.MINIO_CONSOLE_ADDRESS -match ':(\d+)$') { $consolePref = [int]$Matches[1] }
        if ($chBk.CH_S3_ENDPOINT -match ':(\d+)\s*$')     { $relayPref = [int]$Matches[1] }
        $minioPort = Get-FreePort $minioPref
        $consolePort = Get-FreePort $consolePref @($minioPort)
        $relayPort = Get-FreePort $relayPref @($minioPort, $consolePort)
        $minioAddress = "127.0.0.1:$minioPort"
        $consoleAddress = "127.0.0.1:$consolePort"
        $s3EndpointHost = ($chBk.CH_S3_ENDPOINT -replace '^https?://', '') -replace ':\d+\s*$', ''
        $s3Endpoint = "http://${s3EndpointHost}:$relayPort"

        # 3. Start MinIO + relay, wait for health
        $env:MINIO_ROOT_USER = $chBk.CH_S3_ACCESS_KEY
        $env:MINIO_ROOT_PASSWORD = $chBk.CH_S3_SECRET_KEY
        $minioProc = Start-Process -FilePath $chBk.MINIO_EXE `
            -ArgumentList 'server', "`"$($chBk.MINIO_ROOT)`"", '--address', "`"$minioAddress`"", '--console-address', "`"$consoleAddress`"" `
            -WindowStyle Hidden -PassThru
        $relayProc = Start-Process -FilePath "python" -ArgumentList "`"$($chBk.RELAY_SCRIPT)`"", "$relayPort", "$minioPort" -WindowStyle Hidden -PassThru
        $minioReady = $false
        for ($i = 0; $i -lt 30 -and -not $minioReady; $i++) {
            Start-Sleep -Seconds 1
            curl.exe -s --max-time 2 "http://$minioAddress/minio/health/live" -o NUL
            $minioReady = ($LASTEXITCODE -eq 0)
        }
        if (-not $minioReady) { throw "MinIO failed to start on $minioAddress" }
        Write-OK "MinIO + relay started (endpoint $s3Endpoint)"

        # 4. Fire async BACKUP to S3 (path style: endpoint is a bare IP, virtual-hosted
        #    style would require bucket-as-subdomain DNS which does not exist here).
        $s3Url = "$s3Endpoint/$($chBk.MINIO_BUCKET)/market.zip"
        $backupQuery = "BACKUP DATABASE c1_market, DATABASE c3_fundamental TO S3('$s3Url', '$($chBk.CH_S3_ACCESS_KEY)', '$($chBk.CH_S3_SECRET_KEY)') ASYNC"
        $fireResp = curl.exe -s --max-time 60 "${chBaseUrl}?s3_uri_style=path" --data-binary $backupQuery
        if ($LASTEXITCODE -ne 0 -or $fireResp -notmatch '([0-9a-f-]{36})') { throw "BACKUP fire failed: $fireResp" }
        $backupId = $Matches[1]
        Write-Stage "ClickHouse BACKUP async id=$backupId (315GiB, may take hours)"

        # 5. Poll system.backups until done (max 3h)
        $chFinal = "TIMEOUT"
        for ($elapsed = 0; $elapsed -lt 10800; $elapsed += 60) {
            Start-Sleep -Seconds 60
            $st = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT status FROM system.backups WHERE id='$backupId'"
            if ($st -match 'BACKUP_CREATED') { $chFinal = "OK"; break }
            if ($st -match 'BACKUP_FAILED')  { $chFinal = "FAILED"; break }
        }
        if ($chFinal -ne "OK") {
            $chErr = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT substring(error,1,300) FROM system.backups WHERE id='$backupId'"
            throw "ClickHouse backup $chFinal`: $chErr"
        }

        # 6. Verify object landed on F: and is non-empty (institutional practice: verify)
        $sizeSum = (Get-ChildItem $objDir -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
        if (-not $sizeSum -or $sizeSum -lt 1MB) { throw "market.zip missing or too small ($sizeSum bytes)" }
        $dbStatus.clickhouse = @{status="ok"; method="BACKUP TO S3(MinIO relay)"; file="market.zip"; bytes=$sizeSum}
        Write-OK ("ClickHouse dump: ok ({0:N1} GiB)" -f ($sizeSum/1GB))
    } catch {
        $dbStatus.clickhouse = @{status="failed"; error=$_.Exception.Message}
        Write-Warn "ClickHouse backup failed: $($_.Exception.Message)"
    } finally {
        # 7. Always stop MinIO + relay (on-demand only, not a resident service)
        if ($relayProc -and -not $relayProc.HasExited) { Stop-Process -Id $relayProc.Id -Force -ErrorAction SilentlyContinue }
        if ($minioProc -and -not $minioProc.HasExited) { Stop-Process -Id $minioProc.Id -Force -ErrorAction SilentlyContinue }
    }
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
# CH backup store (MinIO root on F:) included when CH stage succeeded; same market.zip
# key each run -> restic CDC dedups unchanged CH parts (~9GiB/day incremental).
$backupSources = @($ProjectRoot, $DumpDir)
if ($dbStatus.clickhouse -and $dbStatus.clickhouse.status -eq "ok" -and $chBk.MINIO_ROOT) {
    $backupSources += $chBk.MINIO_ROOT
}
$backupResult = & restic -r $RepoPath backup @backupSources @excludeArgs --exclude ".minio.sys/" --json | ConvertFrom-Json
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
# CH stage outcome (2026-07-19 fix: failure visible, 24h cadence tracked separately).
# last_ch_backup_time advances ONLY on success - a failure retries at the next window.
if ($dbStatus.clickhouse) {
    $chSt = [string]$dbStatus.clickhouse.status
    $state | Add-Member -NotePropertyName last_ch_backup_status -NotePropertyValue $chSt -Force
    if ($chSt -eq "ok") {
        $state | Add-Member -NotePropertyName last_ch_backup_time -NotePropertyValue (Get-Date).ToString("o") -Force
        if ($state.PSObject.Properties['last_ch_backup_error']) {
            $state.PSObject.Properties.Remove('last_ch_backup_error')
        }
    } elseif ($chSt -eq "failed") {
        $state | Add-Member -NotePropertyName last_ch_backup_error -NotePropertyValue ([string]$dbStatus.clickhouse.error) -Force
    }
}
# Write UTF-8 without BOM + LF (ENCODING-SAFETY INJ-007; PS5.1 Out-File -Encoding UTF8 emits BOM)
$stateJson = ($state | ConvertTo-Json -Depth 3) -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($stateFile, $stateJson, (New-Object System.Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-OK "Backup completed in $([math]::Round($duration.TotalSeconds,1))s"
Write-Host "==========================================" -ForegroundColor Green

# CH stage failed but code/PG/SQLite/restic succeeded -> exit 2 so backup_reconciler
# reports warn (failure must be visible; 2026-07-19 incident: CH silently skipped
# twice while state recorded ok). exit 0 = all ok or CH skipped as planned;
# exit 1 = pipeline fatal; exit 2 = CH stage failed.
$chFailed = ($dbStatus.clickhouse -and $dbStatus.clickhouse.status -eq "failed")
if ($chFailed) { exit 2 }
