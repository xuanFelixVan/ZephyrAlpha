<#
.SYNOPSIS
    Disaster backup system main script (v2.0 -- robocopy + CH incremental)
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.2
    Stages: Pre-check -> DB dump (+PG/CH config sync) -> CH backup (incremental) -> Code backup (robocopy /MIR) -> Report

    Overwrite policy (no version accumulation):
    - Code: robocopy /MIR -- only copies changed files, overwrites in place
    - PG/SQLite: full dump, overwrite (small files, trivial)
    - CH: incremental backup (base + daily inc overwrite) -- only writes changed parts

    Triggers: daily Task Scheduler (6AM) + post-commit reconciler (8h)
    Lock file (.runtime/backup.lock) prevents concurrent runs.
.PARAMETER Force
    Skip interval/cadence protection (for manual / scheduled trigger)
.PARAMETER Mode
    all  - Full pipeline (PG + SQLite + CH + code) [default]
    ch   - ClickHouse backup only (skip PG/SQLite/code)
    code - Code backup only (skip CH stage)
#>
param([switch]$Force, [ValidateSet("all","ch","code")][string]$Mode = "all")

$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"
$ConfigFile = "$ProjectRoot\scripts\backup\backup_config.yaml"
$LogFile = "$ProjectRoot\logs\backup_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$LockFile = "$ProjectRoot\.runtime\backup.lock"
$StateFile = "$ProjectRoot\data\databases\backup_state.json"
$DumpDir = "D:\tmp_db_dumps"
$ChSshHelper = "$ProjectRoot\scripts\backup\ch_vm_ssh.py"

# -- Utility functions --
function Write-Stage($msg) { Write-Host "[BACKUP] $msg" -ForegroundColor Cyan }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

# -- Lock file (prevent concurrent runs from daily task + post-commit) --
function Test-BackupLock {
    if (Test-Path $LockFile) {
        $lockAge = ((Get-Date) - (Get-Item $LockFile).LastWriteTime).TotalHours
        if ($lockAge -lt 4) {
            Write-Warn "Another backup is running (lock age $([math]::Round($lockAge,1))h < 4h). Exiting."
            return $true
        }
        Write-Warn "Stale lock found (age $([math]::Round($lockAge,1))h >= 4h). Proceeding."
    }
    return $false
}
function Acquire-Lock {
    $lockDir = Split-Path $LockFile
    if (-not (Test-Path $lockDir)) { New-Item -ItemType Directory -Path $lockDir -Force | Out-Null }
    [System.IO.File]::WriteAllText($LockFile, "PID:$PID START:$(Get-Date -Format 'o')", (New-Object System.Text.UTF8Encoding($false)))
}
function Release-Lock {
    if (Test-Path $LockFile) { Remove-Item $LockFile -Force -ErrorAction SilentlyContinue }
}

# -- Load config (simple regex parse, avoid powershell-yaml dependency) --
if (-not (Test-Path $ConfigFile)) { Write-Err "config not found: $ConfigFile"; exit 1 }
$yamlContent = Get-Content $ConfigFile -Raw -Encoding UTF8

$CodeSource = "$ProjectRoot";  $CodeTarget = "F:\code_backup"
$DumpsTarget = "F:\db_dumps"
$ChBaseFile = "market.zip"; $ChIncFile = "inc.zip"; $RebaseThreshold = 0.5
if ($yamlContent -match 'source:\s*"([^"]*ZephyrAlpha[^"]*)"') { $CodeSource = $matches[1] -replace '\\\\','\' }
if ($yamlContent -match 'code_backup:[\s\S]*?target:\s*"([^"]+)"') { $CodeTarget = $matches[1] -replace '\\\\','\' }
if ($yamlContent -match 'db_dumps:[\s\S]*?target:\s*"([^"]+)"') { $DumpsTarget = $matches[1] -replace '\\\\','\' }
if ($yamlContent -match 'dump_dir:\s*"([^"]+)"') { $DumpDir = $matches[1] -replace '\\\\','\' }
if ($yamlContent -match 'base_file:\s*"([^"]+)"') { $ChBaseFile = $matches[1].Trim() }
if ($yamlContent -match 'inc_file:\s*"([^"]+)"') { $ChIncFile = $matches[1].Trim() }
if ($yamlContent -match 'rebase_threshold:\s*([\d.]+)') { $RebaseThreshold = [double]$matches[1] }

# Parse exclude lists (inline YAML format: [item1, item2, ...])
$ExcludeDirs = @(".git","node_modules","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache",".runtime",".aidrafts","tmp",".venv")
$ExcludeFiles = @("*.pyc","*.db-wal","*.db-shm")
if ($yamlContent -match 'exclude_dirs:\s*\[([^\]]+)\]') {
    $ExcludeDirs = $matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"').Trim("'") } | Where-Object { $_ }
}
if ($yamlContent -match 'exclude_files:\s*\[([^\]]+)\]') {
    $ExcludeFiles = $matches[1] -split ',' | ForEach-Object { $_.Trim().Trim('"').Trim("'") } | Where-Object { $_ }
}

$dbStatus = @{}

# -- Acquire lock --
if (Test-BackupLock) { exit 0 }
Acquire-Lock
$backupStartTime = Get-Date

try {

# ==================== STAGE 1: Pre-check ====================
if ($Mode -ne "ch") {
    Write-Stage "Stage 1: Pre-check"
    $targetDrive = $CodeTarget.Substring(0,2)
    if (-not (Test-Path $targetDrive)) { Write-Err "Target drive $targetDrive not online"; exit 1 }
    Write-OK "Target drive $targetDrive online"

    $robocopy = Get-Command robocopy -ErrorAction SilentlyContinue
    if (-not $robocopy) { Write-Err "robocopy not found (should be built-in on Windows)"; exit 1 }
    Write-OK "robocopy found: $($robocopy.Source)"
}

# ==================== STAGE 2: DB dump + config sync ====================
if ($Mode -ne "ch") {
    Write-Stage "Stage 2: Database dump + config sync"
    New-Item -ItemType Directory -Path $DumpDir -Force | Out-Null

    # -- PostgreSQL dump --
    $pgDumpCmd = Get-Command pg_dump -ErrorAction SilentlyContinue
    if (-not $pgDumpCmd) {
        $pgDumpCmd = Get-ChildItem "C:\Program Files\PostgreSQL\*\bin\pg_dump.exe" -ErrorAction SilentlyContinue |
            Sort-Object { [int]($_.FullName -replace '.*\\PostgreSQL\\(\d+)\\.*', '$1') } -Descending |
            Select-Object -First 1 -ExpandProperty FullName
    } else { $pgDumpCmd = $pgDumpCmd.Source }
    if ($pgDumpCmd) {
        try {
            $pgEnvFile = "$ProjectRoot\config\.env.postgres"
            $pgUser = "postgres"; $pgPassword = ""
            if (Test-Path $pgEnvFile) {
                foreach ($line in (Get-Content $pgEnvFile -Encoding UTF8)) {
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
            # PG globals (roles)
            $psqlCmd = $pgDumpCmd -replace 'pg_dump\.exe$', 'psql.exe'
            if (Test-Path $psqlCmd) {
                $roleQuery = "SELECT 'CREATE ROLE ' || quote_ident(rolname) || ' WITH ' || CASE WHEN rolcanlogin THEN 'LOGIN' ELSE 'NOLOGIN' END || CASE WHEN rolsuper THEN ' SUPERUSER' ELSE '' END || CASE WHEN rolcreatedb THEN ' CREATEDB' ELSE '' END || CASE WHEN rolcreaterole THEN ' CREATEROLE' ELSE '' END || ';' FROM pg_roles WHERE rolname !~ '^pg_' AND rolname <> 'postgres' ORDER BY rolname;"
                $globalsOut = & $psqlCmd -h localhost -U $pgUser -d postgres -t -A -c $roleQuery 2>$null
                if ($LASTEXITCODE -eq 0) {
                    $header = "-- PG cluster roles (passwords masked; reset from config/.env.postgres after restore)"
                    [System.IO.File]::WriteAllText("$DumpDir\pg_globals.sql", "$header`n$($globalsOut -join "`n")`n", (New-Object System.Text.UTF8Encoding($false)))
                    $dbStatus.postgres_globals = @{status="ok"}
                    Write-OK "PostgreSQL globals dump: ok"
                } else { $dbStatus.postgres_globals = @{status="failed"; error="psql exit $LASTEXITCODE"} }
            }
        } catch {
            $dbStatus.postgres = @{status="error"; error=$_.Exception.Message}
            Write-Warn "PostgreSQL dump error: $($_.Exception.Message)"
        }
    } else { $dbStatus.postgres = @{status="skipped"; reason="pg_dump not found"}; Write-Warn "pg_dump not found" }

    # -- SQLite backup --
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
            if (-not $sqlite3 -or $LASTEXITCODE -ne 0) {
                $pyResult = & python -c "import sqlite3; src=r'$($db.src)'; dst=r'$DumpDir\$($db.dump)'; con=sqlite3.connect(src); con.backup(sqlite3.connect(dst)); con.close(); print('ok')" 2>&1
                if ($pyResult -match 'ok') { $sqliteOk++ } else { Write-Warn "Python SQLite backup also failed: $($db.src)" }
            }
        }
    }
    $dbStatus.sqlite = @{status=$(if($sqliteOk -gt 0){"ok"}else{"skipped"}); count=$sqliteOk}
    Write-OK "SQLite dump: $sqliteOk databases"

    # -- PG config copy (pg_hba.conf, postgresql.conf, pg_ident.conf) --
    $pgConfigSrc = "C:\Program Files\PostgreSQL\16\data"
    $pgConfigDst = "$ProjectRoot\config\system_configs\pg"
    if (Test-Path $pgConfigSrc) {
        New-Item -ItemType Directory -Path $pgConfigDst -Force | Out-Null
        foreach ($f in @("pg_hba.conf","postgresql.conf","pg_ident.conf","postgresql.auto.conf")) {
            $srcPath = Join-Path $pgConfigSrc $f
            if (Test-Path $srcPath) { Copy-Item $srcPath $pgConfigDst -Force }
        }
        Write-OK "PG config synced to config/system_configs/pg/"
    } else { Write-Warn "PG config source not found: $pgConfigSrc" }

    # -- CH config sync (SSH: config.xml, users.xml, backup_disk.xml, fstab) --
    $chConfigDst = "$ProjectRoot\config\system_configs\ch"
    if (Test-Path "$ProjectRoot\config\.env.ch_backup") {
        $syncResult = & python $ChSshHelper --sync-config $chConfigDst 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-OK "CH config synced to config/system_configs/ch/"
        } else { Write-Warn "CH config sync failed: $syncResult" }
    } else { Write-Warn "config/.env.ch_backup not found, skipping CH config sync" }
}

# ==================== ClickHouse backup (incremental) ====================
# Architecture: CH runs in Hyper-V VM. 1TB dynamic VHDX (F:\ch_backup_disk.vhdx)
# attached to VM as /dev/sdc, mounted at /mnt/chbackup_local. CH named disk
# "backups" -> /mnt/chbackup_local/ (config.d/backup_disk.xml).
#
# Incremental: market.zip = full base (one-time, rebased when inc grows);
# inc.zip = daily incremental (overwritten each run). CH BACKUP SETTINGS
# base_backup captures only changed parts since base.
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
try { curl.exe -s --max-time 5 $chBaseUrl --data-binary "SELECT 1" | Out-Null; $chAlive = ($LASTEXITCODE -eq 0) } catch { $chAlive = $false }

# CH 24h cadence gate: last_ch_backup_time only advances on SUCCESS. -Force bypasses.
$chCadenceDue = $true; $chPrevBytes = 0
if (Test-Path $StateFile) {
    try {
        $prevState = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if (-not $Force -and $prevState.last_ch_backup_time) {
            $chElapsedH = ((Get-Date) - [datetime]::Parse($prevState.last_ch_backup_time)).TotalHours
            if ($chElapsedH -lt 24) { $chCadenceDue = $false }
        }
        if ($prevState.last_ch_backup_bytes) { $chPrevBytes = [int64]$prevState.last_ch_backup_bytes }
    } catch { }
}

if ($Mode -eq "code") {
    $dbStatus.clickhouse = @{status="skipped"; reason="Mode=code, CH stage skipped"}
    Write-OK "ClickHouse: Mode=code, stage skipped"
} elseif (-not $chAlive) {
    $dbStatus.clickhouse = @{status="skipped"; reason="service down"}
    Write-Warn "ClickHouse not reachable ($chBaseUrl), skipping"
} elseif ($chBk.Count -eq 0) {
    $dbStatus.clickhouse = @{status="skipped"; reason="config/.env.ch_backup missing"}
    Write-Warn "config/.env.ch_backup not found, skipping ClickHouse backup"
} elseif (-not $chCadenceDue) {
    $dbStatus.clickhouse = @{status="skipped"; reason=("24h cadence (last {0:N1}h ago)" -f $chElapsedH)}
    Write-OK ("ClickHouse: last backup {0:N1}h ago (< 24h cadence), stage skipped" -f $chElapsedH)
} else {
    try {
        # 1. Pre-backup manifest
        $manifestQ = "SELECT database, name, total_rows FROM system.tables WHERE database IN ('c1_market','c3_fundamental') AND engine NOT LIKE '%View%' FORMAT JSONEachRow"
        $chManifest = curl.exe -s --max-time 30 $chBaseUrl --data-binary $manifestQ
        $chTableCount = ($chManifest -split "`n" | Where-Object { $_.Trim() }).Count
        Write-OK "Pre-backup manifest: $chTableCount tables"

        # 2. Decide full vs incremental (stat base + inc via SSH)
        $baseStat = & python $ChSshHelper --stat-backup $ChBaseFile --json 2>&1 | ConvertFrom-Json
        $incStat  = & python $ChSshHelper --stat-backup $ChIncFile --json 2>&1 | ConvertFrom-Json
        $incRatio = if ($baseStat.exists -and $baseStat.bytes -gt 0 -and $incStat.exists) { [double]$incStat.bytes / [double]$baseStat.bytes } else { 0.0 }

        if (-not $baseStat.exists) {
            $chMode = "full"; $chTarget = $ChBaseFile; $chDeleteFiles = @($ChIncFile)
            $chReason = "base missing (first run or after rebase)"
        } elseif ($incRatio -ge $RebaseThreshold) {
            $chMode = "full"; $chTarget = $ChBaseFile; $chDeleteFiles = @($ChIncFile, $ChBaseFile)
            $chReason = "inc ratio $('{0:N2}' -f $incRatio) >= $RebaseThreshold, rebasing"
        } else {
            $chMode = "incremental"; $chTarget = $ChIncFile; $chDeleteFiles = @($ChIncFile)
            $chReason = "incremental (ratio $('{0:N2}' -f $incRatio))"
        }
        Write-Stage "CH backup mode: $chMode -- $chReason"

        # 3. Delete files before backup (overwrite policy)
        foreach ($f in $chDeleteFiles) {
            & python $ChSshHelper --delete-backup $f 2>&1 | Out-Null
        }
        if ($chDeleteFiles.Count -gt 0) { Write-OK "Removed previous file(s): $($chDeleteFiles -join ', ')" }

        # 4. Fire async BACKUP
        if ($chMode -eq "full") {
            $backupQuery = "BACKUP DATABASE c1_market, DATABASE c3_fundamental TO Disk('backups', '$chTarget') ASYNC"
        } else {
            $backupQuery = "BACKUP DATABASE c1_market, DATABASE c3_fundamental TO Disk('backups', '$chTarget') SETTINGS base_backup = Disk('backups', '$ChBaseFile') ASYNC"
        }
        $fireResp = curl.exe -s --max-time 60 $chBaseUrl --data-binary $backupQuery
        if ($LASTEXITCODE -ne 0 -or $fireResp -notmatch '([0-9a-f-]{36})') { throw "BACKUP fire failed: $fireResp" }
        $backupId = $Matches[1]
        Write-Stage "ClickHouse BACKUP ($chMode) async id=$backupId"

        # 5. Poll system.backups (max 3h)
        $chFinal = "TIMEOUT"; $chErr = ""
        for ($elapsed = 0; $elapsed -lt 10800; $elapsed += 60) {
            Start-Sleep -Seconds 60
            $stJson = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT status, substring(error,1,300) as error FROM system.backups WHERE id='$backupId' FORMAT JSON"
            try {
                $stObj = $stJson | ConvertFrom-Json
                if ($stObj.data.Count -gt 0) {
                    $stStatus = $stObj.data[0].status
                    if ($stStatus -eq 'BACKUP_CREATED') { $chFinal = "OK"; break }
                    if ($stStatus -eq 'BACKUP_FAILED')  { $chFinal = "FAILED"; $chErr = $stObj.data[0].error; break }
                }
            } catch { }
        }
        if ($chFinal -ne "OK") { throw "ClickHouse backup $chFinal`: $chErr" }

        # 6. Verification
        $bkMetaJson = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT total_size, num_files FROM system.backups WHERE id='$backupId' FORMAT JSON"
        $bkMeta = $bkMetaJson | ConvertFrom-Json
        $chTotalSize = if ($bkMeta.data.Count -gt 0) { [int64]$bkMeta.data[0].total_size } else { 0 }
        $chNumFiles = if ($bkMeta.data.Count -gt 0) { [int64]$bkMeta.data[0].num_files } else { 0 }

        $statJson = & python $ChSshHelper --stat-backup $chTarget --json 2>&1 | ConvertFrom-Json
        $fileExists = [bool]$statJson.exists
        $fileBytes = if ($fileExists) { [int64]$statJson.bytes } else { 0 }

        if ($chMode -eq "incremental") {
            # Incremental: just check file exists and > 1MB (inc can be small)
            if (-not $fileExists -or $fileBytes -lt 1MB) { throw "$chTarget missing or too small ($fileBytes bytes)" }
            $sizeVerified = $true; $sizeMatch = $true; $sizeRatio = 1.0
        } else {
            # Full: check > 1GB, compression sanity, size ratio vs previous
            if (-not $fileExists -or $fileBytes -lt 1GB) { throw "$chTarget missing or too small ($fileBytes bytes)" }
            $sizeMatch = if ($chTotalSize -gt 0) { $fileBytes -le ($chTotalSize * 1.05) } else { $true }
            $sizeRatio = if ($chPrevBytes -gt 0) { $fileBytes / $chPrevBytes } else { 1.0 }
            $sizeVerified = ($sizeRatio -gt 0.5 -and $sizeRatio -lt 2.0)
            if (-not $sizeVerified -and $chPrevBytes -gt 0) {
                Write-Warn "Size ratio unusual: $([math]::Round($sizeRatio,3)) (current=$([math]::Round($fileBytes/1GB,2))GB prev=$([math]::Round($chPrevBytes/1GB,2))GB)"
            }
            if (-not $sizeMatch) { Write-Warn "File size ($fileBytes) exceeds CH uncompressed total_size ($chTotalSize)" }
        }

        $dbStatus.clickhouse = @{
            status="ok"; mode=$chMode; target=$chTarget
            file="/mnt/chbackup_local/$chTarget"; bytes=$fileBytes
            ch_total_size=$chTotalSize; ch_num_files=$chNumFiles
            size_match=$sizeMatch; verified=($fileExists -and $sizeVerified -and $sizeMatch)
            table_count=$chTableCount; manifest=$chManifest
            prev_bytes=$chPrevBytes; size_ratio=[math]::Round($sizeRatio,4)
            base_bytes=if($baseStat.exists){[int64]$baseStat.bytes}else{0}
        }
        Write-OK ("ClickHouse dump ($chMode): ok ({0:N1} GiB, {1} files, {2} tables, verified={3})" -f ($fileBytes/1GB), $chNumFiles, $chTableCount, ($fileExists -and $sizeVerified -and $sizeMatch))
    } catch {
        $dbStatus.clickhouse = @{status="failed"; error=$_.Exception.Message}
        Write-Warn "ClickHouse backup failed: $($_.Exception.Message)"
    }
}

# ==================== STAGE 3: Code backup (robocopy /MIR) ====================
if ($Mode -eq "ch") {
    Write-Stage "Mode=ch, skipping code backup (Stage 3)"
    $codeResult = @{status="skipped"}
} else {
    Write-Stage "Stage 3: Code backup (robocopy /MIR)"
    # 3a. Code: D:\ZephyrAlpha -> F:\code_backup
    # /XJ excludes junction points (e.g. metadata/system -> ../store/, avoids ERROR 1920)
    $rcArgs = @($CodeSource, $CodeTarget, "/MIR", "/XJ", "/R:2", "/W:5", "/MT:8", "/NFL", "/NDL", "/NP")
    if ($ExcludeDirs)  { $rcArgs += "/XD"; $rcArgs += $ExcludeDirs }
    if ($ExcludeFiles) { $rcArgs += "/XF"; $rcArgs += $ExcludeFiles }
    & robocopy @rcArgs 2>&1 | Out-Null
    $rcCode = $LASTEXITCODE
    if ($rcCode -ge 8) { Write-Err "robocopy code failed (exit $rcCode)" } else { Write-OK "Code robocopy done (exit $rcCode, <8=ok)" }

    # 3b. DB dumps: D:\tmp_db_dumps -> F:\db_dumps
    if (Test-Path $DumpDir) {
        & robocopy $DumpDir $DumpsTarget "/MIR" "/R:2" "/W:5" "/MT:8" "/NFL" "/NDL" "/NP" 2>&1 | Out-Null
        $rcDumps = $LASTEXITCODE
        if ($rcDumps -ge 8) { Write-Warn "robocopy dumps failed (exit $rcDumps)" } else { Write-OK "DB dumps robocopy done (exit $rcDumps)" }
    }
    $codeResult = @{status=$(if($rcCode -lt 8){"ok"}else{"failed"}); robocopy_exit=$rcCode}
}

# ==================== STAGE 4: Report ====================
Write-Stage "Stage 4: Report"
$duration = (Get-Date) - $backupStartTime
$report = @{
    timestamp = (Get-Date).ToString("o")
    duration_seconds = [math]::Round($duration.TotalSeconds, 1)
    mode = $Mode
    force_mode = $Force.IsPresent
    databases = $dbStatus
    code_backup = $codeResult
}

New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
$report | ConvertTo-Json -Depth 5 | Out-File $LogFile -Encoding UTF8
Write-OK "Report saved: $LogFile"

# Update state file
$state = if (Test-Path $StateFile) { Get-Content $StateFile -Raw | ConvertFrom-Json } else { [PSCustomObject]@{} }
if (-not $state) { $state = [PSCustomObject]@{} }
if ($Mode -ne "ch") {
    $state | Add-Member -NotePropertyName last_backup_time -NotePropertyValue (Get-Date).ToString("o") -Force
    $state | Add-Member -NotePropertyName last_backup_status -NotePropertyValue "ok" -Force
}
if ($dbStatus.clickhouse) {
    $chSt = [string]$dbStatus.clickhouse.status
    $state | Add-Member -NotePropertyName last_ch_backup_status -NotePropertyValue $chSt -Force
    if ($chSt -eq "ok") {
        $state | Add-Member -NotePropertyName last_ch_backup_time -NotePropertyValue (Get-Date).ToString("o") -Force
        $state | Add-Member -NotePropertyName last_ch_backup_verified -NotePropertyValue ([bool]$dbStatus.clickhouse.verified) -Force
        $state | Add-Member -NotePropertyName last_ch_backup_mode -NotePropertyValue ([string]$dbStatus.clickhouse.mode) -Force
        $state | Add-Member -NotePropertyName last_ch_backup_target -NotePropertyValue ([string]$dbStatus.clickhouse.target) -Force
        $state | Add-Member -NotePropertyName last_ch_backup_file -NotePropertyValue ([string]$dbStatus.clickhouse.file) -Force
        $state | Add-Member -NotePropertyName last_ch_backup_bytes -NotePropertyValue ([int64]$dbStatus.clickhouse.bytes) -Force
        $state | Add-Member -NotePropertyName last_ch_backup_base_bytes -NotePropertyValue ([int64]$dbStatus.clickhouse.base_bytes) -Force
        if ($state.PSObject.Properties['last_ch_backup_error']) { $state.PSObject.Properties.Remove('last_ch_backup_error') }
    } elseif ($chSt -eq "failed") {
        $state | Add-Member -NotePropertyName last_ch_backup_verified -NotePropertyValue $false -Force
        $state | Add-Member -NotePropertyName last_ch_backup_error -NotePropertyValue ([string]$dbStatus.clickhouse.error) -Force
    }
}
$stateJson = ($state | ConvertTo-Json -Depth 3) -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($StateFile, $stateJson, (New-Object System.Text.UTF8Encoding($false)))

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-OK "Backup completed in $([math]::Round($duration.TotalSeconds,1))s"
Write-Host "==========================================" -ForegroundColor Green

$chFailed = ($dbStatus.clickhouse -and $dbStatus.clickhouse.status -eq "failed")
if ($chFailed) { exit 2 }

} finally {
    Release-Lock
}
