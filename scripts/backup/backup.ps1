<#
.SYNOPSIS
    Disaster backup system main script (v2.1 -- robocopy + CH incremental + versioned code vault)
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.2
    Stages: Pre-check -> DB dump (+PG/CH config sync) -> CH backup (incremental) -> Code backup (versioned) -> Report

    Overwrite policy:
    - Code: VERSIONED daily snapshots (v2.1, 2026-09-14). Target <vault>\<yyyyMMdd>\,
      hardlink-deduped from the latest previous snapshot (unchanged files share disk
      blocks; only changed/new files are physically copied). Intra-day deletions are
      NOT propagated into the day's snapshot. Retention: <retention_days> days.
      Rationale: the old robocopy /MIR single mirror propagated deletions (2026-09-14
      docs/_working deletion incident proved /MIR destroyed the last recovery copy).
    - PG/SQLite: full dump, overwrite (small files, trivial)
    - CH: incremental backup (base + daily inc overwrite) -- only writes changed parts
    - DB dumps: robocopy /MIR (overwrite by design; each dump replaces the old one)

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

# Working vault (versioned code snapshots, v2.1): base + retention days
$VaultBase = "F:\working_vault"
$VaultRetentionDays = 14
if ($yamlContent -match 'working_vault:[\s\S]*?base:\s*"([^"]+)"') { $VaultBase = $matches[1] -replace '\\\\','\' }
if ($yamlContent -match 'working_vault:[\s\S]*?retention_days:\s*(\d+)') { $VaultRetentionDays = [int]$matches[1] }
if ($yamlContent -match 'working_vault:[\s\S]*?free_floor_gb:\s*([\d.]+)') { $VaultFreeFloorGB = [double]$matches[1] }
if ($yamlContent -match 'working_vault:[\s\S]*?min_keep_days:\s*(\d+)') { $VaultMinKeepDays = [int]$matches[1] }

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
if (Test-BackupLock) {
    # Silent-exit hardening (2026-09-15): a lock-skip used to leave zero trace
    # (no report, no state change), which masked a whole missed daily backup.
    # Write a skip record so skipped runs are observable in logs/.
    try {
        $lockMtime = (Get-Item $LockFile).LastWriteTime
        $lockAgeH = [math]::Round(((Get-Date) - $lockMtime).TotalHours, 2)
        $skipLog = "$ProjectRoot\logs\backup_skipped_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
        $skipObj = [ordered]@{
            timestamp  = (Get-Date -Format 'o')
            reason     = "lock_held"
            mode       = $Mode
            force      = [bool]$Force
            lock_age_hours = $lockAgeH
            lock_mtime = $lockMtime.ToString('o')
        }
        $skipObj | ConvertTo-Json | Out-File $skipLog -Encoding utf8
    } catch { }
    exit 0
}
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
$chCadenceDue = $true; $chPrevBytes = 0; $chPrevFullBytes = 0
if (Test-Path $StateFile) {
    try {
        $prevState = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
        if (-not $Force -and $prevState.last_ch_backup_time) {
            $chElapsedH = ((Get-Date) - [datetime]::Parse($prevState.last_ch_backup_time)).TotalHours
            if ($chElapsedH -lt 24) { $chCadenceDue = $false }
        }
        if ($prevState.last_ch_backup_bytes) { $chPrevBytes = [int64]$prevState.last_ch_backup_bytes }
        if ($prevState.last_ch_backup_full_bytes) { $chPrevFullBytes = [int64]$prevState.last_ch_backup_full_bytes }
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

        # 3b. Self-heal: clear stale *.zip.lock (#ARCH-BACKUP-LOCK-STALE, 2026-08-13)
        # Root cause: on abnormal BACKUP abort, inc.zip deleted but inc.zip.lock remains,
        # causing subsequent BACKUP to fail-fast with BACKUP_ALREADY_EXISTS.
        # Unconditionally clean before firing new BACKUP (idempotent; rm -f silent if no lock).
        & python $ChSshHelper --cmd "rm -f /mnt/chbackup_local/*.zip.lock" --sudo 2>&1 | Out-Null
        Write-OK "Self-heal: cleared stale *.zip.lock (if any)"

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
            # Full: check > 1GB, compression sanity, size ratio vs previous FULL
            # (like-for-like; full-vs-incremental ratio false-alarmed on rebase, 2026-09-15)
            if (-not $fileExists -or $fileBytes -lt 1GB) { throw "$chTarget missing or too small ($fileBytes bytes)" }
            $sizeMatch = if ($chTotalSize -gt 0) { $fileBytes -le ($chTotalSize * 1.05) } else { $true }
            if ($chPrevFullBytes -gt 0) {
                $sizeRatio = $fileBytes / $chPrevFullBytes
                $sizeVerified = ($sizeRatio -gt 0.5 -and $sizeRatio -lt 2.0)
                if (-not $sizeVerified) {
                    Write-Warn "Size ratio unusual: $([math]::Round($sizeRatio,3)) (current=$([math]::Round($fileBytes/1GB,2))GB prev_full=$([math]::Round($chPrevFullBytes/1GB,2))GB)"
                }
            } else {
                # No previous full on record -> nothing comparable, skip ratio check
                $sizeRatio = 1.0; $sizeVerified = $true
                Write-OK "No previous full backup recorded - size ratio check skipped"
            }
            if (-not $sizeMatch) { Write-Warn "File size ($fileBytes) exceeds CH uncompressed total_size ($chTotalSize)" }
        }

        $dbStatus.clickhouse = @{
            status="ok"; mode=$chMode; target=$chTarget
            file="/mnt/chbackup_local/$chTarget"; bytes=$fileBytes
            ch_total_size=$chTotalSize; ch_num_files=$chNumFiles
            size_match=$sizeMatch; verified=($fileExists -and $sizeVerified -and $sizeMatch)
            table_count=$chTableCount; manifest=$chManifest
            prev_bytes=$chPrevBytes; prev_full_bytes=$chPrevFullBytes; size_ratio=[math]::Round($sizeRatio,4)
            base_bytes=if($baseStat.exists){[int64]$baseStat.bytes}else{0}
        }
        Write-OK ("ClickHouse dump ($chMode): ok ({0:N1} GiB, {1} files, {2} tables, verified={3})" -f ($fileBytes/1GB), $chNumFiles, $chTableCount, ($fileExists -and $sizeVerified -and $sizeMatch))

        # ---- Dual-write second chain (a3 stage 4.7, 2026-09-21): sync backup zips to
        # /mnt/chbackup2 (G-disk vhdx) so both chains carry the day's increment.
        # rsync is incremental; market.zip only re-copied when rebuilt. Failure = warn
        # (first chain remains source of truth; second chain self-heals next run).
        try {
            Write-Stage "ClickHouse dual-write sync (chbackup_local -> chbackup2)"
            $dualSync = & python $ChSshHelper --cmd "sudo -n rsync -a /mnt/chbackup_local/market.zip /mnt/chbackup_local/inc.zip /mnt/chbackup2/ && ls -la /mnt/chbackup2/*.zip | tail -2" 2>&1
            $dualLast = ($dualSync | Select-Object -Last 2) -join " | "
            if ($LASTEXITCODE -eq 0 -and "$dualSync" -match "inc.zip") { Write-OK "Dual-write sync ok: $dualLast" }
            else { Write-Warn "Dual-write sync inconclusive (exit=$LASTEXITCODE): $dualLast" }
        } catch { Write-Warn ("Dual-write sync failed: " + $_.Exception.Message) }
    } catch {
        $dbStatus.clickhouse = @{status="failed"; error=$_.Exception.Message}
        Write-Warn "ClickHouse backup failed: $($_.Exception.Message)"
    }
}

# ==================== STAGE 3: Code backup (versioned daily vault, v2.1) ====================
# Hardlink-deduped daily snapshots: <VaultBase>\<yyyyMMdd>\
# - Unchanged files (same rel path + size + mtimeUtc as prev snapshot) -> hardlink
#   from the previous day's file (same NTFS volume, ~1x total space).
# - Changed/new files -> fresh physical copy (never overwrite a link in place:
#   both robocopy and CopyFile overwrite hardlinked destinations in place and
#   would corrupt the previous snapshot -- self-tested 2026-09-14).
# - Files deleted from source -> not propagated into the day's snapshot (they
#   remain recoverable from previous days). Old /MIR propagated deletions.
# - Rotation: dated dirs older than $VaultRetentionDays are removed.
if ($Mode -eq "ch") {
    Write-Stage "Mode=ch, skipping code backup (Stage 3)"
    $codeResult = @{status="skipped"}
} else {
    Write-Stage "Stage 3: Code backup (versioned vault, hardlink dedup, retention ${VaultRetentionDays}d)"

    # Space guard (v2.1.1): while free space below floor, evict OLDEST snapshots
    # first, but never keep fewer than $VaultMinKeepDays pre-today snapshots.
    # Steady-state size depends on daily churn (unknowable in advance) -- this
    # makes the vault self-limiting: retention_days=14 is the ceiling, actual
    # retention shrinks under pressure, and persistent shortfall fails LOUD
    # (throw -> nonzero exit -> scheduler report) instead of filling the drive.
    $spaceEvicted = @()
    $floorBytes = $VaultFreeFloorGB * 1GB
    $vaultDrive = $VaultBase.Substring(0, 1)
    $freeBytes = (Get-PSDrive -Name $vaultDrive).Free
    if ($freeBytes -lt $floorBytes) {
        Write-Stage ("Space guard: {0:N1} GB free < floor {1:N1} GB -- evicting oldest snapshots (min keep {2})" -f ($freeBytes / 1GB), $VaultFreeFloorGB, $VaultMinKeepDays)
        $datedDirs = @(Get-ChildItem -LiteralPath $VaultBase -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^\d{8}$' -and $_.Name -lt (Get-Date).ToString("yyyyMMdd") } |
            Sort-Object Name)
        $evictCount = [Math]::Max(0, $datedDirs.Count - $VaultMinKeepDays)
        foreach ($d in ($datedDirs | Select-Object -First $evictCount)) {
            if ((Get-PSDrive -Name $vaultDrive).Free -ge $floorBytes) { break }
            Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction SilentlyContinue
            if (-not (Test-Path -LiteralPath $d.FullName)) { $spaceEvicted += $d.Name }
        }
        $freeBytes = (Get-PSDrive -Name $vaultDrive).Free
        if ($freeBytes -lt $floorBytes) {
            $dbStatus.code_space_guard = @{status="failed"; free_gb=[math]::Round($freeBytes/1GB,2)}
            throw ("VaultFreeSpaceBelowFloor: {0:N1} GB free < floor {1:N1} GB even at min keep {2} -- code snapshot aborted to avoid filling the drive" -f ($freeBytes / 1GB), $VaultFreeFloorGB, $VaultMinKeepDays)
        }
        Write-OK ("Space guard: {0:N1} GB free after evicting {1} snapshot(s)" -f ($freeBytes / 1GB), $spaceEvicted.Count)
    }

    function Get-SourceFileIndex([string]$Root, [string[]]$ExclDirs, [string[]]$ExclFiles) {
        # Walk source tree (skip excluded dir names at any depth, skip reparse
        # points/junctions to avoid loops, skip excluded file-name patterns).
        # Returns hashtable: relpath(lowercase) -> @(fullPath, size, mtimeUtc)
        $idx = @{}
        $exclLower = @(); foreach ($d in $ExclDirs) { $exclLower += $d.ToLower() }
        $stack = [System.Collections.Stack]::new()
        $stack.Push($Root)
        while ($stack.Count -gt 0) {
            $dir = $stack.Pop()
            $entries = [System.IO.Directory]::EnumerateFileSystemEntries($dir)
            foreach ($e in $entries) {
                $name = [System.IO.Path]::GetFileName($e)
                try { $attr = [System.IO.File]::GetAttributes($e) } catch { continue }
                if (($attr -band [System.IO.FileAttributes]::Directory) -ne 0) {
                    if ($exclLower -contains $name.ToLower()) { continue }
                    if (($attr -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { continue }
                    $stack.Push($e)
                } else {
                    $skip = $false
                    foreach ($p in $ExclFiles) { if ($name -like $p) { $skip = $true; break } }
                    if ($skip) { continue }
                    $fi = [System.IO.FileInfo]::new($e)
                    $rel = $e.Substring($Root.Length).TrimStart('\').ToLower()
                    $idx[$rel] = @($e, $fi.Length, $fi.LastWriteTimeUtc)
                }
            }
        }
        return $idx
    }

    $today = (Get-Date).ToString("yyyyMMdd")
    $dayTarget = Join-Path $VaultBase $today
    New-Item -ItemType Directory -Path $dayTarget -Force | Out-Null

    # Mode A (first run of the day): seed from the latest older snapshot.
    # Mode B (same-day re-run): diff against today's own dir -- changed files
    # are replaced (their old dir entry is removed first; if it was a hardlink
    # into an older day, that day keeps its own entry and stays intact), and
    # files deleted from source are intentionally KEPT (no intra-day deletion
    # propagation; the file remains recoverable from this day's snapshot).
    $dayHasContent = [bool](Get-ChildItem -LiteralPath $dayTarget -Recurse -File -Force -ErrorAction SilentlyContinue | Select-Object -First 1)
    $prevDay = $null
    if ($dayHasContent) {
        $prevDay = $dayTarget
        Write-Stage "Same-day snapshot exists -> incremental refresh (Mode B)"
    } else {
        $prevDirs = Get-ChildItem -LiteralPath $VaultBase -Directory -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -match '^\d{8}$' -and $_.Name -lt $today } |
            Sort-Object Name
        if ($prevDirs) { $prevDay = $prevDirs[-1].FullName }
    }

    $linked = 0; $copied = 0; $linkFail = 0; $replaced = 0; $vanished = 0; $errors3 = @()
    $rcCode = 0

    if (-not $prevDay) {
        # Very first run: no previous snapshot -> plain full copy via robocopy /E
        # (empty destination: no hardlinks exist, in-place overwrite is impossible)
        Write-Stage "No previous snapshot -> full copy (robocopy /E)"
        $rcArgs = @($CodeSource, $dayTarget, "/E", "/XJ", "/R:2", "/W:5", "/MT:8", "/NFL", "/NDL", "/NP")
        if ($ExcludeDirs)  { $rcArgs += "/XD"; $rcArgs += $ExcludeDirs }
        if ($ExcludeFiles) { $rcArgs += "/XF"; $rcArgs += $ExcludeFiles }
        & robocopy @rcArgs 2>&1 | Out-Null
        $rcCode = $LASTEXITCODE
        if ($rcCode -ge 8) { Write-Err "robocopy full copy failed (exit $rcCode)" } else { Write-OK "Full copy done (exit $rcCode, <8=ok)" }
    } else {
        # Seed/refresh the day's snapshot: link unchanged + copy changed/new
        Write-Stage ("Diff source vs snapshot: {0}" -f $prevDay)
        $srcIndex = Get-SourceFileIndex -Root $CodeSource -ExclDirs $ExcludeDirs -ExclFiles $ExcludeFiles
        $prevIndex = Get-SourceFileIndex -Root $prevDay  -ExclDirs $ExcludeDirs -ExclFiles $ExcludeFiles
        Write-OK ("Source files: {0}, snapshot files: {1}" -f $srcIndex.Count, $prevIndex.Count)

        foreach ($rel in $srcIndex.Keys) {
            $e = $srcIndex[$rel]
            $srcFull = $e[0]; $srcSize = $e[1]; $srcMtime = $e[2]
            $dstFull = Join-Path $dayTarget $rel
            $dstDir = Split-Path $dstFull -Parent
            $isUnchanged = $false
            $prevFull = $null
            if ($prevIndex.ContainsKey($rel)) {
                $p = $prevIndex[$rel]
                $prevFull = $p[0]
                if ($p[1] -eq $srcSize -and $p[2] -eq $srcMtime) { $isUnchanged = $true }
            }
            $dstExists = Test-Path -LiteralPath $dstFull
            if ($dstExists -and $isUnchanged) { continue }  # already in the day's snapshot

            try {
                if (-not (Test-Path -LiteralPath $dstDir)) {
                    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
                }
                if ($dstExists) {
                    # Changed file: break the old day entry first (never overwrite
                    # a hardlink in place -- it would corrupt the older snapshot)
                    Remove-Item -LiteralPath $dstFull -Force -ErrorAction Stop
                    $replaced++
                }
                if ($isUnchanged -and $prevFull -and (Split-Path $prevFull -Qualifier) -eq (Split-Path $dayTarget -Qualifier)) {
                    # Same NTFS volume as prev snapshot -> hardlink (shares blocks)
                    New-Item -ItemType HardLink -Path $dstFull -Value $prevFull -ErrorAction Stop | Out-Null
                    $linked++
                } else {
                    [System.IO.File]::Copy($srcFull, $dstFull, $false)
                    # Guarantee mtime parity with source (diff consistency)
                    (Get-Item -LiteralPath $dstFull -Force).LastWriteTimeUtc = $srcMtime
                    $copied++
                }
            } catch {
                # Link/replace failed -> fall back to a fresh physical copy
                try {
                    if (Test-Path -LiteralPath $dstFull) { Remove-Item -LiteralPath $dstFull -Force -ErrorAction SilentlyContinue }
                    if (-not (Test-Path -LiteralPath $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
                    [System.IO.File]::Copy($srcFull, $dstFull, $true)
                    (Get-Item -LiteralPath $dstFull -Force).LastWriteTimeUtc = $srcMtime
                    $copied++
                } catch {
                    if (-not (Test-Path -LiteralPath $srcFull)) {
                        # Source vanished mid-run (temp/lock files churn during the
                        # snapshot window) -> transient, not an integrity failure.
                        # Was: counted as failure and flipped status to failed (2026-09-15).
                        $vanished++
                        Write-Warn "Source vanished mid-run, skipped: $rel"
                    } else {
                        $linkFail++
                        $errors3 += "$rel : $($_.Exception.Message)"
                    }
                }
            }
        }
        Write-OK ("Snapshot: linked={0}, copied={1}, replaced={2}, failures={3}, vanished={4}" -f $linked, $copied, $replaced, $linkFail, $vanished)
        if ($errors3.Count -gt 0) {
            foreach ($msg in ($errors3 | Select-Object -First 10)) { Write-Warn "Snapshot failure: $msg" }
        }
    }

    # Rotation: remove dated dirs older than retention window
    $rotated = @()
    $cutoff = (Get-Date).AddDays(-$VaultRetentionDays).ToString("yyyyMMdd")
    foreach ($d in (Get-ChildItem -LiteralPath $VaultBase -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d{8}$' -and $_.Name -lt $cutoff } | Sort-Object Name)) {
        Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction SilentlyContinue
        if (-not (Test-Path -LiteralPath $d.FullName)) { $rotated += $d.Name }
    }
    if ($rotated.Count -gt 0) { Write-OK ("Rotation: removed {0} old snapshot(s): {1}" -f $rotated.Count, ($rotated -join ',')) }

    # DB dumps: versioned dated snapshots (ruling #380-7/#381: 14-day rolling by default;
    # rotation gated on CH backup ok -- oldest snapshot only removed when data body is in DB
    # and doubly backed up. Legacy /MIR files at target root stay as frozen extra copy.)
    if (Test-Path $DumpDir) {
        $dumpsDay = (Get-Date).ToString("yyyyMMdd")
        $dumpsDayTarget = Join-Path $DumpsTarget $dumpsDay
        New-Item -ItemType Directory -Path $dumpsDayTarget -Force | Out-Null
        & robocopy $DumpDir $dumpsDayTarget "/E" "/COPY:DAT" "/R:2" "/W:5" "/MT:8" "/NFL" "/NDL" "/NP" 2>&1 | Out-Null
        $rcDumps = $LASTEXITCODE
        if ($rcDumps -ge 8) { Write-Warn "robocopy dumps failed (exit $rcDumps)" } else { Write-OK ("DB dumps snapshot done: {0}" -f $dumpsDayTarget) }
        $rotatedDumps = @()
        $dumpsStateOk = $false
        try {
            $sJson = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
            $dumpsStateOk = ([string]$sJson.last_ch_backup_status -eq "ok")
        } catch { $dumpsStateOk = $false }
        if ($dumpsStateOk) {
            $dumpsRetention = 14
            $cutoffDumps = (Get-Date).AddDays(-$dumpsRetention).ToString("yyyyMMdd")
            foreach ($d in (Get-ChildItem -LiteralPath $DumpsTarget -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d{8}$' -and $_.Name -lt $cutoffDumps } | Sort-Object Name)) {
                Remove-Item -LiteralPath $d.FullName -Recurse -Force -ErrorAction SilentlyContinue
                if (-not (Test-Path -LiteralPath $d.FullName)) { $rotatedDumps += $d.Name }
            }
            if ($rotatedDumps.Count -gt 0) { Write-OK ("DB dumps rotation: removed {0} old snapshot(s)" -f $rotatedDumps.Count) }
        } else {
            Write-Warn "DB dumps rotation skipped (CH backup not ok -- oldest snapshot kept as insurance)"
        }
    }
    $vaultOk = ($rcCode -lt 8) -and ($linkFail -eq 0)
    $codeResult = @{
        status=$(if($vaultOk){"ok"}else{"failed"}); mode="versioned"
        vault_base=$VaultBase; day_target=$dayTarget; prev_snapshot=$prevDay
        retention_days=$VaultRetentionDays; hardlinked=$linked; copied=$copied; failures=$linkFail; vanished=$vanished
        robocopy_exit=$rcCode; rotated=$rotated
    }
}

# ==================== STAGE 3b: Git bundle refresh (git history disaster backup) ====================
# The v2.1 code vault excludes .git; git history is disaster-backed up as a single
# bundle file (<vault>\git_bundles\). Re-create when the newest bundle is older
# than 7 days, keep the newest 2. pack.windowMemory=256m: pack-objects is the only
# memory-heavy native op in this window (died with default window on 2026-09-15).
$bundleResult = @{status="skipped"; reason="Mode=ch"}
if ($Mode -ne "ch") {
    Write-Stage "Stage 3b: Git bundle refresh"
    # a3 stage 4.4: bundle home is config-driven (git_bundle.base); fallback = legacy <vault>\git_bundles
    $bundleDir = $null
    if ($yamlContent -match 'git_bundle:[\s\S]*?base:\s*"([^"]+)"') { $bundleDir = $matches[1] -replace '\\\\','\' }
    if (-not $bundleDir) { $bundleDir = Join-Path $VaultBase "git_bundles" }
    New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null
    $latestBundle = Get-ChildItem "$bundleDir\*.bundle" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $bundleAgeDays = if ($latestBundle) { [math]::Round(((Get-Date) - $latestBundle.LastWriteTime).TotalDays, 2) } else { 999 }
    $bundleTarget = Join-Path $bundleDir ("zephyralpha_full_{0}.bundle" -f (Get-Date -Format 'yyyyMMdd'))

    if ($bundleAgeDays -lt 7) {
        Write-OK ("Bundle fresh ({0}d old), skipping" -f $bundleAgeDays)
        $bundleResult = @{status="skipped"; reason="fresh"; latest=$latestBundle.Name; age_days=$bundleAgeDays}
    } else {
        # Today's file may exist from a partial/failed prior attempt -- verify or rebuild
        if (Test-Path $bundleTarget) {
            & git bundle verify $bundleTarget 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-OK "Bundle for today already exists and verifies, skipping"
                $bundleResult = @{status="ok"; action="existing"; bundle=$bundleTarget}
            } else {
                Write-Warn "Today's bundle exists but fails verify -- rebuilding"
                Remove-Item $bundleTarget -Force -ErrorAction SilentlyContinue
            }
        }
        if (-not (Test-Path $bundleTarget)) {
            Write-Stage "Creating bundle (latest is $bundleAgeDays days old)"
            & git -c pack.windowMemory=256m -c pack.threads=2 bundle create $bundleTarget --all 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0 -and (Test-Path $bundleTarget)) {
                & git bundle verify $bundleTarget 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    $old = @(Get-ChildItem "$bundleDir\*.bundle" -File |
                        Sort-Object LastWriteTime -Descending | Select-Object -Skip 2)
                    foreach ($b in $old) { Remove-Item $b.FullName -Force -ErrorAction SilentlyContinue }
                    Write-OK ("Bundle created + verified ({0:N0} MB, rotated {1} old)" -f ((Get-Item $bundleTarget).Length / 1MB), $old.Count)
                    $bundleResult = @{status="ok"; action="created"; bundle=$bundleTarget; rotated=$old.Count}
                } else {
                    Write-Warn "Bundle verify failed -- removing suspect file, retry next run"
                    Remove-Item $bundleTarget -Force -ErrorAction SilentlyContinue
                    $bundleResult = @{status="failed"; reason="verify"}
                }
            } else {
                Write-Warn "Bundle creation failed (exit $LASTEXITCODE) -- will retry next backup run"
                $bundleResult = @{status="failed"; reason="create"; git_exit=$LASTEXITCODE}
            }
        }
    }
}

# ==================== STAGE 3c: Off-repo critical assets mirror ====================
# Added 2026-09-08 (Owner approved): mirror off-repo critical assets (C/E drive)
# to F:\offrepo_backup\<id>\. Registry source: config/asset_inventory.yaml
# offrepo_assets (backup: mirror entries). Section config: backup_config.yaml
# offrepo_backup (base + targets, line-state-machine parse, no powershell-yaml dep).
# NOTE: keep comments ASCII-only in this file (PS5.1 parses non-BOM UTF-8 as ANSI).
if ($Mode -eq "ch") {
    Write-Stage "Mode=ch, skipping off-repo mirror (Stage 3c)"
    $offrepoResult = @{status="skipped"; reason="Mode=ch"}
} else {
    Write-Stage "Stage 3c: Off-repo assets mirror"
    $offrepoBase = "F:\offrepo_backup"
    if ($yamlContent -match 'offrepo_backup:[\s\S]*?base:\s*"([^"]+)"') { $offrepoBase = $matches[1] -replace '\\\\','\' }

    # Line-state-machine: parse (id, source) pairs from offrepo_backup.targets
    $offrepoTargets = @()
    $curId = $null; $inOffrepo = $false
    foreach ($line in (Get-Content $ConfigFile -Encoding UTF8)) {
        if ($line -match '^[A-Za-z_][A-Za-z0-9_]*:') { $inOffrepo = ($line -match '^offrepo_backup:'); continue }
        if (-not $inOffrepo) { continue }
        if ($line -match '-\s+id:\s*(\S+)') { $curId = $matches[1].Trim() }
        elseif ($curId -and $line -match 'source:\s*"([^"]+)"') {
            $offrepoTargets += [pscustomobject]@{ id = $curId; source = ($matches[1] -replace '\\\\','\') }
            $curId = $null
        }
    }

    $offrepoStatus = @{}
    foreach ($t in $offrepoTargets) {
        if (-not (Test-Path $t.source)) {
            $offrepoStatus[$t.id] = @{status="failed"; error="source missing: $($t.source)"}
            Write-Err "Off-repo [$($t.id)]: source missing: $($t.source)"
            continue
        }
        $tgt = Join-Path $offrepoBase $t.id
        & robocopy $t.source $tgt "/MIR" "/XJ" "/R:2" "/W:5" "/MT:8" "/NFL" "/NDL" "/NP" 2>&1 | Out-Null
        $rc = $LASTEXITCODE
        if ($rc -ge 8) {
            $offrepoStatus[$t.id] = @{status="failed"; robocopy_exit=$rc}
            Write-Err "Off-repo [$($t.id)] robocopy failed (exit $rc)"
        } else {
            $tgtBytes = (Get-ChildItem $tgt -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
            $offrepoStatus[$t.id] = @{status="ok"; robocopy_exit=$rc; bytes=[int64]$tgtBytes}
            Write-OK ("Off-repo [{0}]: ok ({1:N2} GB)" -f $t.id, ($tgtBytes/1GB))
        }
    }
    $offrepoResult = @{
        status = $(if (($offrepoStatus.Values | Where-Object status -eq "failed").Count -gt 0) {"failed"} elseif ($offrepoTargets.Count -eq 0) {"skipped"; reason="no targets parsed"} else {"ok"})
        targets = $offrepoStatus
    }
}

# ==================== STAGE 3d: G-drive fallback mirror (3-2-1 G-side, ruling #380-6/#381) ====================
# Added 2026-09-20: mirror F backup artifacts to G:\zephyr_backup_mirror\<id>\ for the
# 3-2-1 G-side fallback. Section config: backup_config.yaml g_mirror (same line-state-machine
# parse as 3c, no powershell-yaml dep). G is USB HDD (70MB/s) - mirror only, never online path.
# First full sync done 2026-09-20 overnight by st-disk-ch-20260921.
$gMirrorResult = @{status="skipped"; reason="Mode=ch"}
if ($Mode -eq "ch") {
    Write-Stage "Mode=ch, skipping G-drive mirror (Stage 3d)"
} else {
    Write-Stage "Stage 3d: G-drive fallback mirror"
    $gMirrorBase = "G:\zephyr_backup_mirror"
    if ($yamlContent -match 'g_mirror:[\s\S]*?base:\s*"([^"]+)"') { $gMirrorBase = $matches[1] -replace '\\\\','\' }

    $gMirrorTargets = @()
    $curGId = $null; $inGMirror = $false
    foreach ($line in (Get-Content $ConfigFile -Encoding UTF8)) {
        if ($line -match '^[A-Za-z_][A-Za-z0-9_]*:') { $inGMirror = ($line -match '^g_mirror:'); continue }
        if (-not $inGMirror) { continue }
        if ($line -match '-\s+id:\s*(\S+)') { $curGId = $matches[1].Trim() }
        elseif ($curGId -and $line -match 'source:\s*"([^"]+)"') {
            $gMirrorTargets += [pscustomobject]@{ id = $curGId; source = ($matches[1] -replace '\\\\','\'); target = $null }
        }
        elseif ($curGId -and $line -match 'target:\s*"([^"]+)"') {
            # a3 4.6: explicit per-target destination (isolates from sibling mirror dirs)
            if ($gMirrorTargets.Count -gt 0) {
                $gMirrorTargets[-1] = $gMirrorTargets[-1] | Add-Member -NotePropertyName target -NotePropertyValue ($matches[1] -replace '\\\\','\') -Force -PassThru
            }
        }
    }

    $gMirrorStatus = @{}
    foreach ($t in $gMirrorTargets) {
        if (-not (Test-Path $t.source)) {
            $gMirrorStatus[$t.id] = @{status="failed"; error="source missing: $($t.source)"}
            Write-Err "G-mirror [$($t.id)]: source missing: $($t.source)"
            continue
        }
        # a3 4.6: per-target explicit target: overrides base\id derivation
        $gTgt = if ($t.PSObject.Properties['target'] -and $t.target) { [string]$t.target } else { Join-Path $gMirrorBase $t.id }
        & robocopy $t.source $gTgt "/MIR" "/XJ" "/COPY:DAT" "/R:2" "/W:5" "/MT:8" "/NFL" "/NDL" "/NP" 2>&1 | Out-Null
        $rcG = $LASTEXITCODE
        if ($rcG -ge 8) {
            $gMirrorStatus[$t.id] = @{status="failed"; robocopy_exit=$rcG}
            Write-Err "G-mirror [$($t.id)] robocopy failed (exit $rcG)"
        } else {
            $gMirrorStatus[$t.id] = @{status="ok"; robocopy_exit=$rcG}
            Write-OK "G-mirror [$($t.id)]: ok"
        }
    }
    $gMirrorResult = @{
        status = $(if (($gMirrorStatus.Values | Where-Object status -eq "failed").Count -gt 0) {"failed"} elseif ($gMirrorTargets.Count -eq 0) {"skipped"} else {"ok"})
        targets = $gMirrorStatus
    }
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
    git_bundle = $bundleResult
    offrepo_backup = $offrepoResult
    g_mirror = $gMirrorResult
}

New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
$report | ConvertTo-Json -Depth 5 | Out-File $LogFile -Encoding utf8
Write-OK "Report saved: $LogFile"

# Update state file
$state = if (Test-Path $StateFile) { Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json } else { [PSCustomObject]@{} }
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
        if ($dbStatus.clickhouse.mode -eq "full") {
            $state | Add-Member -NotePropertyName last_ch_backup_full_bytes -NotePropertyValue ([int64]$dbStatus.clickhouse.bytes) -Force
        }
        if ($state.PSObject.Properties['last_ch_backup_error']) { $state.PSObject.Properties.Remove('last_ch_backup_error') }
    } elseif ($chSt -eq "failed") {
        $state | Add-Member -NotePropertyName last_ch_backup_verified -NotePropertyValue $false -Force
        $state | Add-Member -NotePropertyName last_ch_backup_error -NotePropertyValue ([string]$dbStatus.clickhouse.error) -Force
    }
}
$stateJson = ($state | ConvertTo-Json -Depth 3) -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($StateFile, $stateJson, (New-Object System.Text.UTF8Encoding($false)))

# ==================== STAGE 4b: Rolling archive evaluation ====================
# Backup-success event hook (contract v1.3.0 INV-RET-002 / ruling #380-#384).
# Event-triggered only - NO new scheduled task (constitution red line; the daily
# 06:00 task already exists as the Owner-approved fallback carrier). The
# reconciler re-checks all five safety valves itself; failure degrades to warn.
$rollingOk = ($Mode -ne "ch")
$chOkRolling = ($dbStatus.clickhouse -and [string]$dbStatus.clickhouse.status -eq "ok")
if ($rollingOk -and $chOkRolling) {
    try {
        $raScript = Join-Path $ProjectRoot "scripts\ch\rolling_archive_reconciler.py"
        if (Test-Path $raScript) {
            Write-Stage "Stage 4b: Rolling archive evaluation (backup-success hook)"
            $raOut = & python $raScript --mode full_auto 2>&1
            $raOut | Select-Object -Last 5 | ForEach-Object { Write-Host "[rolling-archive] $_" }
            # vhdx quarterly compaction precheck (ruling #380-4: REMINDER ONLY, never auto-run)
            $raPre = & python $raScript --precheck 2>&1
            $raPre | Select-Object -Last 3 | ForEach-Object { Write-Host "[vhdx-precheck] $_" }
        }
    } catch { Write-Warn ("rolling archive evaluation failed: " + $_.Exception.Message) }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-OK "Backup completed in $([math]::Round($duration.TotalSeconds,1))s"
Write-Host "==========================================" -ForegroundColor Green

$chFailed = ($dbStatus.clickhouse -and $dbStatus.clickhouse.status -eq "failed")
if ($chFailed) { exit 2 }

} finally {
    Release-Lock
}
