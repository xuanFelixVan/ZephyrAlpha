<#
.SYNOPSIS
    Disaster recovery script -- inventory / verify / restore (v2.0 -- robocopy + CH incremental)
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.5
    v2.0 (2026-07-28): restic removed. Backup inventory now lives on F: drive:
      F:\code_backup\          <- code + config + PG config + CH config (robocopy /MIR)
      F:\db_dumps\             <- PG dump + SQLite dump + pg_globals.sql
      F:\ch_backup_disk.vhdx   <- CH data backup (VHDX, base + inc)
      F:\ch_vm_backup\         <- CH VM (boot.vhdx + data.vhdx + config)

    Subcommands:
      inventory        - List all backup artifacts on F: with sizes + freshness
      verify           - Verify F: backup integrity (key files + CH base/inc exist)
                         WITHOUT overwriting anything (read-only, safe)
      code [-target X] - Restore code to D:\ZephyrAlpha\ (or -target X) via robocopy /MIR
      pg [-drop]       - Restore PostgreSQL (depgraph.dump + pg_globals.sql)
      sqlite           - Restore SQLite databases (governance.db + session_continuity.db)
      ch [-skip-inc]   - Restore ClickHouse c1_market + c3_fundamental
                         Step 1: RESTORE base market.zip
                         Step 2: RESTORE inc.zip (if exists and -skip-inc not set)
      vm               - Restore CH Hyper-V VM (Import-VM from F:\ch_vm_backup\)
      all              - Full disaster recovery: vm -> ch -> pg -> sqlite -> code
                         (interactive confirmation at each stage)

    Triggers: manual only. AI should follow docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/dr_runbook.md step-by-step.

.PARAMETER Target
    Override restore target for "code" subcommand (default D:\ZephyrAlpha)
.PARAMETER Drop
    For "pg": DROP DATABASE depgraph before pg_restore (destructive)
.PARAMETER SkipInc
    For "ch": skip inc.zip restore (base only, for partial recovery)
.PARAMETER Force
    Skip confirmation prompts (DANGER: auto-overwrites). Used by automated tests.
.EXAMPLE
    .\restore.ps1 inventory
    .\restore.ps1 verify
    .\restore.ps1 code
    .\restore.ps1 pg -drop
    .\restore.ps1 ch
    .\restore.ps1 all -Force
#>
param(
    [Parameter(Position=0)]
    [ValidateSet("inventory","verify","code","pg","sqlite","ch","vm","all")]
    [string]$Action = "inventory",

    [string]$Target,
    [switch]$Drop,
    [switch]$SkipInc,
    [switch]$Force
)

$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"
$FDrive = "F:"
$CodeBackup = "F:\code_backup"
$DbDumps = "F:\db_dumps"
$ChVmBackup = "F:\ch_vm_backup"
$ChSshHelper = "$ProjectRoot\scripts\backup\ch_vm_ssh.py"
$StateFile = "$ProjectRoot\data\databases\backup_state.json"

# -- CH config (HTTP endpoint + base/inc filenames) --
$chBk = @{}
$chBkEnvFile = "$ProjectRoot\config\.env.ch_backup"
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

# CH base/inc filenames: single source of truth = backup_config.yaml (same as backup.ps1)
$ChBaseFile = "market.zip"; $ChIncFile = "inc.zip"
$cfgFile = "$ProjectRoot\scripts\backup\backup_config.yaml"
if (Test-Path $cfgFile) {
    $cfg = Get-Content $cfgFile -Raw -Encoding UTF8
    if ($cfg -match 'base_file:\s*"([^"]+)"') { $ChBaseFile = $matches[1].Trim() }
    if ($cfg -match 'inc_file:\s*"([^"]+)"')  { $ChIncFile  = $matches[1].Trim() }
}

# -- Helpers --
function Write-Stage($msg) { Write-Host "[RESTORE] $msg" -ForegroundColor Cyan }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

function Confirm-Action($prompt) {
    if ($Force) { return $true }
    $resp = Read-Host "$prompt (yes/no)"
    return ($resp -eq "yes")
}

function Get-DirSizeGB($path) {
    if (-not (Test-Path $path)) { return 0.0 }
    $bytes = (Get-ChildItem $path -Recurse -File -ErrorAction SilentlyContinue |
              Measure-Object -Property Length -Sum).Sum
    if (-not $bytes) { return 0.0 }
    return [math]::Round($bytes / 1GB, 2)
}

function Test-ChAlive {
    try {
        $r = curl.exe -s --max-time 5 $chBaseUrl --data-binary "SELECT 1" 2>$null
        return ($LASTEXITCODE -eq 0 -and $r -match "1")
    } catch { return $false }
}

# ==================== inventory ====================
function Do-Inventory {
    Write-Host "=== ZephyrAlpha Backup Inventory (F: drive) ===" -ForegroundColor Cyan
    Write-Host ""

    # F: drive free space
    $fVol = Get-Volume F -ErrorAction SilentlyContinue
    if ($fVol) {
        $totalGB = [math]::Round($fVol.Size / 1GB, 1)
        $freeGB  = [math]::Round($fVol.SizeRemaining / 1GB, 1)
        Write-Host "F: drive: ${totalGB}GB total, ${freeGB}GB free" -ForegroundColor White
    } else { Write-Warn "F: drive not online" }
    Write-Host ""

    # Code backup
    Write-Host "[Code backup]" -ForegroundColor Cyan
    if (Test-Path $CodeBackup) {
        $codeGB = Get-DirSizeGB $CodeBackup
        $lastWrite = (Get-Item $CodeBackup).LastWriteTime
        Write-Host "  Path:    $CodeBackup"
        Write-Host "  Size:    ${codeGB} GB"
        Write-Host "  Updated: $lastWrite"
        # Key files present?
        foreach ($f in @("AGENTS.md","pyproject.toml","config\.env.postgres","config\.env.ch_backup")) {
            $p = Join-Path $CodeBackup $f
            if (Test-Path $p) { Write-Host "  [OK] $f" -ForegroundColor Green }
            else { Write-Host "  [MISSING] $f" -ForegroundColor Red }
        }
    } else { Write-Warn "  $CodeBackup not found" }
    Write-Host ""

    # DB dumps
    Write-Host "[DB dumps]" -ForegroundColor Cyan
    if (Test-Path $DbDumps) {
        Write-Host "  Path: $DbDumps"
        Get-ChildItem $DbDumps -File | ForEach-Object {
            $sizeMB = [math]::Round($_.Length / 1MB, 2)
            Write-Host ("  {0,-30} {1,10} MB  {2}" -f $_.Name, $sizeMB, $_.LastWriteTime)
        }
    } else { Write-Warn "  $DbDumps not found" }
    Write-Host ""

    # CH backup (on VHDX attached to VM)
    Write-Host "[ClickHouse backup (VHDX)]" -ForegroundColor Cyan
    $vhdx = "F:\ch_backup_disk.vhdx"
    if (Test-Path $vhdx) {
        $vhdxGB = [math]::Round((Get-Item $vhdx).Length / 1GB, 2)
        Write-Host "  VHDX:    $vhdx (${vhdxGB} GB)"
    } else { Write-Warn "  $vhdx not found" }
    if (Test-Path "$ProjectRoot\config\.env.ch_backup") {
        foreach ($f in @($ChBaseFile, $ChIncFile)) {
            $stat = & python $ChSshHelper --stat-backup $f --json 2>&1 | ConvertFrom-Json
            if ($stat.exists) {
                $gb = [math]::Round($stat.bytes / 1GB, 2)
                Write-Host "  [OK] $f (${gb} GiB)" -ForegroundColor Green
            } else {
                Write-Host "  [MISSING] $f" -ForegroundColor Yellow
            }
        }
    } else { Write-Warn "  config/.env.ch_backup not found (cannot stat CH backups)" }
    Write-Host ""

    # CH VM backup
    Write-Host "[CH VM backup]" -ForegroundColor Cyan
    if (Test-Path $ChVmBackup) {
        Write-Host "  Path: $ChVmBackup"
        foreach ($f in @("boot.vhdx","data.vhdx")) {
            $p = Join-Path $ChVmBackup $f
            if (Test-Path $p) {
                $gb = [math]::Round((Get-Item $p).Length / 1GB, 2)
                Write-Host "  [OK] $f (${gb} GB)" -ForegroundColor Green
            } else {
                Write-Host "  [MISSING] $f" -ForegroundColor Red
            }
        }
        if (Test-Path "$ChVmBackup\zephyr-ch") {
            Write-Host "  [OK] VM config dir zephyr-ch\" -ForegroundColor Green
        } else { Write-Host "  [MISSING] VM config dir zephyr-ch\" -ForegroundColor Red }
    } else { Write-Warn "  $ChVmBackup not found (run backup_ch_vm.ps1 first)" }
    Write-Host ""

    # Last backup state
    if (Test-Path $StateFile) {
        Write-Host "[Last backup state]" -ForegroundColor Cyan
        $st = Get-Content $StateFile -Raw | ConvertFrom-Json
        $st | Format-List
    }
}

# ==================== verify ====================
function Do-Verify {
    Write-Host "=== Backup Integrity Verification (read-only) ===" -ForegroundColor Cyan
    $issues = @()

    # 1. Code backup key files
    foreach ($f in @("AGENTS.md","pyproject.toml","config\.env.postgres","config\.env.ch_backup","config\.env.clickhouse")) {
        $p = Join-Path $CodeBackup $f
        if (Test-Path $p) { Write-OK "code: $f" }
        else { Write-Err "code: $f MISSING"; $issues += "code:$f" }
    }

    # 2. PG/SQLite dumps
    foreach ($f in @("depgraph.dump","pg_globals.sql","governance_backup.db","session_backup.db")) {
        $p = Join-Path $DbDumps $f
        if (Test-Path $p) {
            $mb = [math]::Round((Get-Item $p).Length / 1MB, 2)
            Write-OK "dumps: $f (${mb}MB)"
        } else { Write-Err "dumps: $f MISSING"; $issues += "dumps:$f" }
    }

    # 3. CH base backup (required)
    if (Test-Path "$ProjectRoot\config\.env.ch_backup") {
        $baseStat = & python $ChSshHelper --stat-backup $ChBaseFile --json 2>&1 | ConvertFrom-Json
        if ($baseStat.exists -and $baseStat.bytes -gt 1GB) {
            $gb = [math]::Round($baseStat.bytes / 1GB, 2)
            Write-OK "ch: $ChBaseFile (${gb} GiB)"
        } else {
            Write-Err "ch: $ChBaseFile missing or too small"
            $issues += "ch:$ChBaseFile"
        }
        # inc is optional (first run or just rebased)
        $incStat = & python $ChSshHelper --stat-backup $ChIncFile --json 2>&1 | ConvertFrom-Json
        if ($incStat.exists) {
            $mb = [math]::Round($incStat.bytes / 1MB, 2)
            Write-OK "ch: $ChIncFile (${mb} MB)"
        } else {
            Write-Warn "ch: $ChIncFile missing (optional -- base only recovery)"
        }
    } else {
        Write-Err "config/.env.ch_backup not found -- cannot verify CH backups"
        $issues += "config:.env.ch_backup"
    }

    # 4. CH VM backup
    foreach ($f in @("boot.vhdx","data.vhdx")) {
        $p = Join-Path $ChVmBackup $f
        if (Test-Path $p) {
            $gb = [math]::Round((Get-Item $p).Length / 1GB, 2)
            Write-OK "vm: $f (${gb} GB)"
        } else { Write-Err "vm: $f MISSING"; $issues += "vm:$f" }
    }

    Write-Host ""
    if ($issues.Count -eq 0) {
        Write-OK "ALL CHECKS PASSED -- backup is ready for disaster recovery"
    } else {
        Write-Err "ISSUES FOUND ($($issues.Count)):"
        $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        exit 1
    }
}

# ==================== code ====================
function Do-Code {
    $restoreTarget = if ($Target) { $Target } else { $ProjectRoot }
    Write-Stage "Restoring code: $CodeBackup -> $restoreTarget"
    if (-not (Test-Path $CodeBackup)) { Write-Err "Source not found: $CodeBackup"; exit 1 }
    if (-not (Confirm-Action "robocopy /MIR will overwrite $restoreTarget?")) { Write-Host "Aborted."; exit 0 }

    # robocopy /MIR mirrors source to target (deletes target extras, copies changed files only)
    # /XJ excludes junction points (same as backup.ps1, avoids ERROR 1920 on metadata/system)
    # Same exclude rules as backup.ps1 to keep restore symmetric
    $ExcludeDirs = @(".git","node_modules","__pycache__",".pytest_cache",".mypy_cache",".ruff_cache",".runtime",".aidrafts","tmp",".venv")
    $ExcludeFiles = @("*.pyc","*.db-wal","*.db-shm")
    $rcArgs = @($CodeBackup, $restoreTarget, "/MIR", "/XJ", "/R:2", "/W:5", "/MT:8", "/NFL", "/NDL", "/NP")
    $rcArgs += "/XD"; $rcArgs += $ExcludeDirs
    $rcArgs += "/XF"; $rcArgs += $ExcludeFiles
    & robocopy @rcArgs 2>&1 | Out-Null
    $rc = $LASTEXITCODE
    if ($rc -ge 8) { Write-Err "robocopy failed (exit $rc)"; exit 1 }
    Write-OK "Code restored (robocopy exit=$rc, <8=ok)"

    # Post-restore: key files presence check
    foreach ($f in @("AGENTS.md","pyproject.toml")) {
        if (Test-Path (Join-Path $restoreTarget $f)) { Write-OK "$f present" }
        else { Write-Err "$f missing after restore" }
    }
    Write-Host ""
    Write-Host "Next: pip install -e . (rebuild Python env from pyproject.toml)" -ForegroundColor Yellow
}

# ==================== pg ====================
function Do-Pg {
    Write-Stage "Restoring PostgreSQL (depgraph.dump + pg_globals.sql)"
    $dump = Join-Path $DbDumps "depgraph.dump"
    $globals = Join-Path $DbDumps "pg_globals.sql"
    if (-not (Test-Path $dump)) { Write-Err "depgraph.dump not found in $DbDumps"; exit 1 }

    # Locate pg_restore + psql
    $pgRestore = Get-Command pg_restore -ErrorAction SilentlyContinue
    if (-not $pgRestore) {
        $pgRestore = Get-ChildItem "C:\Program Files\PostgreSQL\*\bin\pg_restore.exe" -ErrorAction SilentlyContinue |
            Sort-Object { [int]($_.FullName -replace '.*\\PostgreSQL\\(\d+)\\.*', '$1') } -Descending |
            Select-Object -First 1 -ExpandProperty FullName
    } else { $pgRestore = $pgRestore.Source }
    if (-not $pgRestore) { Write-Err "pg_restore not found"; exit 1 }

    $psql = $pgRestore -replace 'pg_restore\.exe$', 'psql.exe'
    if (-not (Test-Path $psql)) { Write-Err "psql not found alongside pg_restore"; exit 1 }

    # PG credentials
    $pgUser = "postgres"; $pgPassword = ""
    $pgEnvFile = "$ProjectRoot\config\.env.postgres"
    if (Test-Path $pgEnvFile) {
        foreach ($line in (Get-Content $pgEnvFile -Encoding UTF8)) {
            if ($line -match '^POSTGRES_USER=(.+)$') { $pgUser = $matches[1].Trim() }
            if ($line -match '^POSTGRES_PASSWORD=(.+)$') { $pgPassword = $matches[1].Trim() }
        }
    }
    $env:PGPASSWORD = $pgPassword

    if (-not (Confirm-Action "Restore PG depgraph from $dump (user=$pgUser)?")) { Write-Host "Aborted."; exit 0 }

    # 1. Restore globals (roles) first -- passwords masked, must reset from .env.postgres
    if (Test-Path $globals) {
        Write-Stage "Restoring PG globals (roles, passwords masked)"
        & $psql -h localhost -U $pgUser -d postgres -f $globals 2>&1 | Out-Null
        Write-OK "Globals restored (reset role passwords from config/.env.postgres)"
        Write-Host "  ALTER ROLE zephyr PASSWORD '...';  (run for each role per .env.postgres)" -ForegroundColor Yellow
    }

    # 2. Optional DROP (RESTORE requires clean target for some objects)
    if ($Drop) {
        Write-Stage "Dropping existing depgraph database"
        & $psql -h localhost -U $pgUser -d postgres -c "DROP DATABASE IF EXISTS depgraph;" 2>&1 | Out-Null
        & $psql -h localhost -U $pgUser -d postgres -c "CREATE DATABASE depgraph OWNER $pgUser;" 2>&1 | Out-Null
        Write-OK "depgraph recreated"
    }

    # 3. pg_restore
    Write-Stage "Running pg_restore (may take a few minutes)"
    & $pgRestore -h localhost -U $pgUser -d depgraph --no-owner --no-privileges $dump
    $rc = $LASTEXITCODE
    # pg_restore returns non-zero for warnings (e.g., role ownership); 0 or 1 acceptable
    if ($rc -le 1) {
        Write-OK "pg_restore complete (exit=$rc, 0/1=ok)"
    } else {
        Write-Err "pg_restore failed (exit=$rc)"
        exit 1
    }

    # 4. Verify: row counts
    Write-Stage "Post-restore verification"
    & $psql -h localhost -U $pgUser -d depgraph -c "SELECT schemaname, n_live_tup AS approx_rows FROM pg_stat_user_tables ORDER BY n_live_tup DESC LIMIT 10;" 2>&1
}

# ==================== sqlite ====================
function Do-Sqlite {
    Write-Stage "Restoring SQLite databases"
    $targets = @(
        @{src="$DbDumps\governance_backup.db"; dst="$ProjectRoot\data\databases\governance.db"}
        @{src="$DbDumps\session_backup.db";    dst="$ProjectRoot\data\databases\session_continuity.db"}
    )
    foreach ($t in $targets) {
        if (-not (Test-Path $t.src)) { Write-Warn "$($t.src) not found, skipping"; continue }
        $dstDir = Split-Path $t.dst
        if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Path $dstDir -Force | Out-Null }
        if (-not (Confirm-Action "Overwrite $($t.dst) with $($t.src)?")) { continue }
        Copy-Item $t.src $t.dst -Force
        Write-OK "$($t.dst) restored"
    }
}

# ==================== ch ====================
function Restore-ChFile($filename, $label) {
    <# RESTORE a single backup file via CH RESTORE ASYNC + poll. Returns $true on success. #>
    $stat = & python $ChSshHelper --stat-backup $filename --json 2>&1 | ConvertFrom-Json
    if (-not $stat.exists) {
        Write-Warn "$label : $filename not found on VHDX, skipping"
        return $false
    }
    $gb = [math]::Round($stat.bytes / 1GB, 2)
    Write-Stage "$label : RESTORE $filename (${gb} GiB)"

    $q = "RESTORE DATABASE c1_market, DATABASE c3_fundamental FROM Disk('backups', '$filename') ASYNC"
    $fireResp = curl.exe -s --max-time 60 $chBaseUrl --data-binary $q
    if ($LASTEXITCODE -ne 0 -or $fireResp -notmatch '([0-9a-f-]{36})') {
        Write-Err "$label RESTORE fire failed: $fireResp"
        return $false
    }
    $id = $Matches[1]
    Write-Stage "$label : async id=$id (may take hours for base)"

    $final = "TIMEOUT"; $err = ""
    for ($elapsed = 0; $elapsed -lt 14400; $elapsed += 60) {  # 4h max for base restore
        Start-Sleep -Seconds 60
        $stJson = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT status, substring(error,1,300) as error FROM system.backups WHERE id='$id' FORMAT JSON"
        try {
            $stObj = $stJson | ConvertFrom-Json
            if ($stObj.data.Count -gt 0) {
                $st = $stObj.data[0].status
                if ($st -eq 'RESTORED')        { $final = "OK"; break }
                if ($st -eq 'RESTORE_FAILED')  { $final = "FAILED"; $err = $stObj.data[0].error; break }
            }
        } catch { }
    }
    if ($final -ne "OK") { Write-Err "$label RESTORE $final : $err"; return $false }
    Write-OK "$label RESTORE complete"
    return $true
}

function Do-Ch {
    Write-Stage "Restoring ClickHouse c1_market + c3_fundamental"
    if (-not (Test-Path "$ProjectRoot\config\.env.ch_backup")) {
        Write-Err "config/.env.ch_backup not found (need CH_VM_HOST/USER/PASSWORD)"; exit 1
    }
    if (-not (Test-ChAlive)) { Write-Err "ClickHouse not reachable at $chBaseUrl -- start VM first (restore.ps1 vm)"; exit 1 }
    Write-OK "ClickHouse reachable"

    if (-not (Confirm-Action "DROP + RESTORE c1_market, c3_fundamental? This is destructive.")) { Write-Host "Aborted."; exit 0 }

    # 1. Drop existing databases (RESTORE requires clean target)
    Write-Stage "Dropping existing c1_market and c3_fundamental"
    curl.exe -s --max-time 60 $chBaseUrl --data-binary "DROP DATABASE IF EXISTS c1_market" | Out-Null
    curl.exe -s --max-time 60 $chBaseUrl --data-binary "DROP DATABASE IF EXISTS c3_fundamental" | Out-Null
    Write-OK "Databases dropped"

    # 2. RESTORE base (required)
    $baseOk = Restore-ChFile $ChBaseFile "BASE"
    if (-not $baseOk) { Write-Err "Base restore failed -- cannot continue without base"; exit 1 }

    # 3. RESTORE inc (optional, skipped if missing or -SkipInc set)
    if (-not $SkipInc) {
        $incStat = & python $ChSshHelper --stat-backup $ChIncFile --json 2>&1 | ConvertFrom-Json
        if ($incStat.exists) {
            Restore-ChFile $ChIncFile "INC" | Out-Null
        } else {
            Write-Warn "inc.zip not found -- base-only restore (acceptable if just rebased)"
        }
    } else {
        Write-Warn "-SkipInc set -- skipping inc.zip restore"
    }

    # 4. Post-restore verification
    Write-Stage "Post-restore verification"
    curl.exe -s $chBaseUrl --data-binary "SELECT database, name, total_rows FROM system.tables WHERE database IN ('c1_market','c3_fundamental') AND engine NOT LIKE '%View%' ORDER BY database, name FORMAT PrettyCompact"
    Write-Host ""
    curl.exe -s $chBaseUrl --data-binary "SELECT database, formatReadableSize(sum(bytes_on_disk)) as size FROM system.parts WHERE active AND database IN ('c1_market','c3_fundamental') GROUP BY database FORMAT PrettyCompact"
    Write-OK "ClickHouse restore complete (verify row counts above)"

    # 5. RBAC reminder (configuration-as-code)
    Write-Host ""
    Write-Host "Next: python apply_rbac.py  (rebuild CH users/roles from YAML)" -ForegroundColor Yellow
}

# ==================== vm ====================
function Do-Vm {
    Write-Stage "Restoring ClickHouse Hyper-V VM from $ChVmBackup"
    if (-not (Get-Command Get-VM -ErrorAction SilentlyContinue)) {
        Write-Err "Hyper-V module not available. Run as Administrator on the host."; exit 1
    }
    if (-not (Test-Path "$ChVmBackup\zephyr-ch")) {
        Write-Err "VM config not found at $ChVmBackup\zephyr-ch. Run backup_ch_vm.ps1 first."; exit 1
    }
    foreach ($f in @("boot.vhdx","data.vhdx")) {
        if (-not (Test-Path "$ChVmBackup\$f")) { Write-Err "$f missing in $ChVmBackup"; exit 1 }
    }

    # Locate .vmcx config file
    $vmcx = Get-ChildItem "$ChVmBackup\zephyr-ch\Virtual Machines\*.vmcx" -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $vmcx) { Write-Err ".vmcx not found in $ChVmBackup\zephyr-ch\Virtual Machines\"; exit 1 }

    $existingVm = Get-VM -Name "zephyr-ch" -ErrorAction SilentlyContinue
    if ($existingVm) {
        if (-not (Confirm-Action "VM 'zephyr-ch' already exists. Delete and re-import?")) { Write-Host "Aborted."; exit 0 }
        if ($existingVm.State -eq 'Running') {
            Write-Warn "Stopping existing VM..."
            Stop-VM -Name "zephyr-ch" -Force
        }
        Remove-VM -Name "zephyr-ch" -Force
        Write-OK "Existing VM removed (VHDX files kept in $ChVmBackup)"
    }

    if (-not (Confirm-Action "Import-VM from $ChVmBackup (register in-place)?")) { Write-Host "Aborted."; exit 0 }

    # Import-VM: register in-place (VHDX paths point to F:\ch_vm_backup\)
    # Note: this registers the VM at its backed-up location. For production,
    # consider copying VHDX back to D:\HyperV\VMs\zephyr-ch\ first.
    Write-Stage "Importing VM from $vmcx"
    Import-VM -Path $vmcx.FullName -ErrorAction Stop
    if ($LASTEXITCODE -ne 0 -and -not $?) { Write-Err "Import-VM failed"; exit 1 }
    Write-OK "VM imported"

    Write-Stage "Starting VM 'zephyr-ch'"
    Start-VM -Name "zephyr-ch" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 15
    $vmState = (Get-VM -Name "zephyr-ch").State
    Write-OK "VM state: $vmState"

    # Wait for CH to be reachable (the backup VHDX is auto-attached via VM config)
    Write-Stage "Waiting for ClickHouse HTTP (port $chHttpPort)..."
    $chOk = $false
    for ($i = 0; $i -lt 120; $i++) {  # 10 min
        if (Test-ChAlive) { $chOk = $true; break }
        Start-Sleep -Seconds 5
    }
    if ($chOk) { Write-OK "ClickHouse reachable -- proceed to 'restore.ps1 ch'" }
    else { Write-Warn "ClickHouse not reachable after 10 min (check VM console / network)" }
}

# ==================== all ====================
function Do-All {
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host " FULL DISASTER RECOVERY (interactive)" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "Order: vm -> ch -> pg -> sqlite -> code"
    Write-Host "Each stage will prompt for confirmation unless -Force"
    Write-Host ""

    Write-Host "[1/5] VM restore" -ForegroundColor Cyan
    Do-Vm
    Write-Host ""
    Write-Host "[2/5] ClickHouse restore" -ForegroundColor Cyan
    Do-Ch
    Write-Host ""
    Write-Host "[3/5] PostgreSQL restore" -ForegroundColor Cyan
    Do-Pg
    Write-Host ""
    Write-Host "[4/5] SQLite restore" -ForegroundColor Cyan
    Do-Sqlite
    Write-Host ""
    Write-Host "[5/5] Code restore" -ForegroundColor Cyan
    Do-Code
    Write-Host ""
    Write-OK "FULL DISASTER RECOVERY COMPLETE"
    Write-Host "Final steps:" -ForegroundColor Yellow
    Write-Host "  1. pip install -e .   (rebuild Python env)"
    Write-Host "  2. python apply_rbac.py   (rebuild CH RBAC)"
    Write-Host "  3. Run verification: .\restore.ps1 verify"
}

# ==================== dispatch ====================
switch ($Action) {
    "inventory" { Do-Inventory }
    "verify"    { Do-Verify }
    "code"      { Do-Code }
    "pg"        { Do-Pg }
    "sqlite"    { Do-Sqlite }
    "ch"        { Do-Ch }
    "vm"        { Do-Vm }
    "all"       { Do-All }
}
