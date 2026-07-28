<#
.SYNOPSIS
    Backup of the ClickHouse Hyper-V VM to F: drive -- manual or smart weekly.
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.6
    Backs up the zephyr-ch VM (boot.vhdx + data.vhdx + VM config) to F:\ch_vm_backup\.
    The CH backup disk (F:\ch_backup_disk.vhdx) is deliberately EXCLUDED -- it is
    the backup target itself, not part of the VM's persistent state.

    Two modes:
      (default, -Force)  - Full backup: stop VM -> robocopy VHDX + config -> start VM.
                           Downtime ~30-90 min (555 GB data.vhdx). Use after CH upgrade.
      -AutoCheck         - Smart weekly: SSH-check CH version + config hashes vs last
                           recorded state (backup_state.json). Unchanged = SKIP (zero
                           downtime). Changed = run full backup. Designed for weekly
                           scheduled task -- 99% of weeks skip with no downtime.

    Overwrite policy: robocopy /MIR mirrors the source. Unchanged VHDX files
    (same size+timestamp) are skipped; changed files are fully re-copied
    (VHDX is a single monolithic file -- no partial copy possible).

    WHY -AutoCheck skips most weeks:
      data.vhdx (555GB) changes daily (CH writes data), but the data itself is
      covered by daily BACKUP TO Disk (incremental). The VM backup's value is
      OS + CH program + CH config (static, only changes on upgrade). Checking
      CH version + config hash avoids 99% of weekly 555GB copies.
.PARAMETER Force
    Skip the "VM is running" confirmation prompt (full backup mode).
.PARAMETER AutoCheck
    Smart mode: compare CH version + config hash, skip if unchanged.
.PARAMETER RegisterTask
    Register Windows Scheduled task "ZephyrAlpha-WeeklyVMBackup" (Saturday 06:00,
    RunLevel Highest -- REQUIRES ADMIN). Does NOT run backup immediately.
.PARAMETER UnregisterTask
    Remove the weekly scheduled task.
.PARAMETER TaskStatus
    Print weekly scheduled task status.
.EXAMPLE
    .\backup_ch_vm.ps1                  # interactive full backup
    .\backup_ch_vm.ps1 -Force           # full backup, no prompt
    .\backup_ch_vm.ps1 -AutoCheck       # weekly scheduled (skip if unchanged)
    .\backup_ch_vm.ps1 -RegisterTask    # register weekly task (run as Administrator)
#>
param([switch]$Force, [switch]$AutoCheck, [switch]$RegisterTask, [switch]$UnregisterTask, [switch]$TaskStatus)

$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"
$VmName = "zephyr-ch"
$VmRoot = "D:\HyperV\VMs\zephyr-ch"
$BackupRoot = "F:\ch_vm_backup"
$ChSshHelper = "$ProjectRoot\scripts\backup\ch_vm_ssh.py"
$StateFile = "$ProjectRoot\data\databases\backup_state.json"
$LogFile = "$ProjectRoot\logs\ch_vm_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$TaskName = "ZephyrAlpha-WeeklyVMBackup"

function Write-Stage($msg) { Write-Host "[CH-VM-BACKUP] $msg" -ForegroundColor Cyan }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

# -- Helper: read a single field from backup_state.json (top-level) --
function Get-StateField($name) {
    if (-not (Test-Path $StateFile)) { return $null }
    try {
        $st = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
        return $st.$name
    } catch { return $null }
}
function Set-StateField($name, $value) {
    $st = if (Test-Path $StateFile) {
        try { Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json } catch { [PSCustomObject]@{} }
    } else { [PSCustomObject]@{} }
    if (-not $st) { $st = [PSCustomObject]@{} }
    $st | Add-Member -NotePropertyName $name -NotePropertyValue $value -Force
    $j = ($st | ConvertTo-Json -Depth 3) -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($StateFile, $j, (New-Object System.Text.UTF8Encoding($false)))
}

# ==================== -TaskStatus ====================
if ($TaskStatus) {
    Write-Stage "Scheduled task status: $TaskName"
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $task) { Write-Warn "Task '$TaskName' not registered. Run as Admin: -RegisterTask"; exit 0 }
    $info = $task | Get-ScheduledTaskInfo
    Write-Host "  State:              $($task.State)"
    Write-Host "  LastRunTime:        $($info.LastRunTime)"
    Write-Host "  LastTaskResult:     0x$('{0:X8}' -f $info.LastTaskResult) ($($info.LastTaskResult))"
    Write-Host "  NextRunTime:        $($info.NextRunTime)"
    Write-Host "  NumberOfMissedRuns: $($info.NumberOfMissedRuns)"
    Write-Host "  Principal RunLevel: $($task.Principal.RunLevel)"
    exit 0
}

# ==================== -UnregisterTask ====================
if ($UnregisterTask) {
    Write-Stage "Unregistering task: $TaskName"
    $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($task) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-OK "Task '$TaskName' removed"
    } else { Write-Warn "Task '$TaskName' not found" }
    exit 0
}

# ==================== -RegisterTask ====================
if ($RegisterTask) {
    Write-Stage "Registering scheduled task: $TaskName"
    $self = $MyInvocation.MyCommand.Path
    if (-not $self) { $self = "$ProjectRoot\scripts\backup\backup_ch_vm.ps1" }
    if (-not (Test-Path $self)) { Write-Err "Script not found: $self"; exit 1 }

    # Verify admin (RunLevel Highest requires elevation)
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Err "Registering a RunLevel Highest task requires Administrator."
        Write-Host "  Re-run this in an elevated PowerShell:" -ForegroundColor Yellow
        Write-Host "    powershell -ExecutionPolicy Bypass -File `"$self`" -RegisterTask" -ForegroundColor White
        exit 1
    }

    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$self`" -AutoCheck" `
        -WorkingDirectory $ProjectRoot

    # Weekly Saturday 06:00
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 6:00am

    $settings = New-ScheduledTaskSettingsSet `
        -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
        -StartWhenAvailable `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -DontStopOnIdleEnd `
        -RestartCount 1 `
        -RestartInterval (New-TimeSpan -Minutes 30)

    # RunLevel Highest: Hyper-V Stop-VM/Start-VM require admin.
    # AutoCheck skips (zero downtime) when CH unchanged -- the common path.
    # Full backup (Stop/robocopy/Start) runs only when CH version/config changes.
    $principal = New-ScheduledTaskPrincipal `
        -UserId $env:USERNAME `
        -LogonType Interactive `
        -RunLevel Highest

    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($existing) {
        Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal | Out-Null
        Write-OK "Task '$TaskName' updated"
    } else {
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "ZephyrAlpha weekly CH VM backup (Saturday 06:00, AutoCheck skips if unchanged)" | Out-Null
        Write-OK "Task '$TaskName' registered"
    }

    $task = Get-ScheduledTask -TaskName $TaskName
    $info = $task | Get-ScheduledTaskInfo
    Write-Host "  State:         $($task.State)" -ForegroundColor White
    Write-Host "  NextRunTime:   $($info.NextRunTime)" -ForegroundColor White
    Write-Host "  RunLevel:      $($task.Principal.RunLevel)" -ForegroundColor White
    Write-Host "  Trigger:       Weekly Saturday 06:00 (AutoCheck)" -ForegroundColor White
    exit 0
}

# ==================== -AutoCheck: smart skip-when-unchanged ====================
# Compares current CH version + config hash against last recorded state.
# Unchanged -> exit 0 (zero downtime). Changed -> fall through to full backup.
if ($AutoCheck) {
    Write-Stage "AutoCheck: probing CH version + config hash via SSH"
    if (-not (Test-Path "$ProjectRoot\config\.env.ch_backup")) {
        Write-Warn "config/.env.ch_backup not found -- cannot AutoCheck, forcing full backup"
    } else {
        # Single SSH round-trip: CH version + sha256 of config files + fstab
        $probeCmd = "sudo sh -c '" +
            "echo =V=; clickhouse-server --version 2>/dev/null | head -1; " +
            "echo =H=; sha256sum /etc/clickhouse-server/config.xml /etc/clickhouse-server/users.xml /etc/clickhouse-server/config.d/backup_disk.xml /etc/fstab 2>/dev/null | sha256sum" +
            "'"
        $probe = & python $ChSshHelper --cmd $probeCmd --sudo --json 2>&1 | ConvertFrom-Json
        if ($probe.exit_code -ne 0) {
            Write-Warn "AutoCheck SSH probe failed (exit $($probe.exit_code)) -- forcing full backup. stderr: $($probe.stderr)"
        } else {
            $out = $probe.stdout
            $version = ""
            $hash = ""
            if ($out -match '=V=\s*(.*)') { $version = $matches[1].Trim() }
            if ($out -match '=H=\s*([0-9a-f]{64})') { $hash = $matches[1].Trim() }
            $lastVersion = Get-StateField "last_ch_vm_version"
            $lastHash     = Get-StateField "last_ch_vm_config_hash"

            Write-Host "  Current version: $version" -ForegroundColor White
            Write-Host "  Current hash:    $hash" -ForegroundColor White
            Write-Host "  Last version:    $lastVersion" -ForegroundColor White
            Write-Host "  Last hash:       $lastHash" -ForegroundColor White

            if ($version -and $hash -and $version -eq $lastVersion -and $hash -eq $lastHash) {
                Write-OK "AutoCheck: CH version + config unchanged since last VM backup. SKIP (zero downtime)."
                # Record the skip so scheduled-task history shows it
                Set-StateField "last_ch_vm_autocheck_time" (Get-Date).ToString("o")
                Set-StateField "last_ch_vm_autocheck_result" "skipped_unchanged"
                $report = @{
                    timestamp = (Get-Date).ToString("o")
                    mode = "autocheck"
                    result = "skipped_unchanged"
                    version = $version; config_hash = $hash
                }
                New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
                $report | ConvertTo-Json -Depth 3 | Out-File $LogFile -Encoding UTF8
                Write-Host "  Log: $LogFile" -ForegroundColor White
                exit 0
            } else {
                $reason = if ($version -ne $lastVersion) { "version changed ($lastVersion -> $version)" } else { "config hash changed" }
                Write-Warn "AutoCheck: $reason -- proceeding to full backup"
            }
        }
    }
    # Fall through to full backup below (AutoCheck decided a backup is needed).
    $Force = $true  # AutoCheck runs unattended via scheduled task -- no interactive prompt
}

# -- Pre-checks --
Write-Stage "Pre-check"
if (-not (Get-Command Get-VM -ErrorAction SilentlyContinue)) {
    Write-Err "Hyper-V module not available. Run as Administrator on the host."
    exit 1
}
$vm = Get-VM -Name $VmName -ErrorAction SilentlyContinue
if (-not $vm) { Write-Err "VM '$VmName' not found"; exit 1 }

# Verify VHDX files exist (only boot + data -- NOT ch_backup_disk.vhdx)
$bootVhdx = Join-Path $VmRoot "boot.vhdx"
$dataVhdx = Join-Path $VmRoot "data.vhdx"
$configDir = Join-Path $VmRoot $VmName  # config folder (Virtual Machines\, Snapshots\)
foreach ($f in @($bootVhdx, $dataVhdx, $configDir)) {
    if (-not (Test-Path $f)) { Write-Err "Required path not found: $f"; exit 1 }
}
$dataSizeGB = [math]::Round((Get-Item $dataVhdx).Length / 1GB, 2)
Write-OK "VM '$VmName' found. data.vhdx = $dataSizeGB GB"

# F: drive free space check (need ~data.vhdx size + buffer)
$fVol = Get-Volume F -ErrorAction SilentlyContinue
if (-not $fVol) { Write-Err "F: drive not online"; exit 1 }
$freeGB = [math]::Round($fVol.SizeRemaining / 1GB, 1)
$needGB = $dataSizeGB + 20  # data + boot + config + buffer
if ($freeGB -lt $needGB) {
    Write-Err "F: free space ${freeGB}GB < needed ${needGB}GB. Free space on F: before VM backup."
    exit 1
}
Write-OK "F: drive free = ${freeGB}GB (need ~${needGB}GB)"

# Confirm if VM is running (downtime warning)
if ($vm.State -eq 'Running' -and -not $Force) {
    Write-Warn "VM '$VmName' is Running. This backup requires stopping the VM (CH downtime ~$([math]::Round($dataSizeGB/130,1))h at 130MB/s)."
    $confirm = Read-Host "Stop VM, copy ${dataSizeGB}GB, restart? (yes/no)"
    if ($confirm -ne "yes") { Write-Host "Aborted."; exit 0 }
}

$backupStart = Get-Date
$steps = @{}

# -- Step 1: Stop VM gracefully --
Write-Stage "Step 1: Stopping VM '$VmName' (graceful shutdown)..."
if ($vm.State -eq 'Running') {
    Stop-VM -Name $VmName -ErrorAction Stop
    # Wait up to 5 min for shutdown
    $waited = 0
    while ((Get-VM -Name $VmName).State -ne 'Off' -and $waited -lt 300) {
        Start-Sleep -Seconds 5; $waited += 5
    }
    $finalState = (Get-VM -Name $VmName).State
    if ($finalState -ne 'Off') {
        Write-Err "VM did not stop gracefully within 5 min (state=$finalState). Aborting to avoid dirty copy."
        exit 1
    }
    Write-OK "VM stopped (waited ${waited}s)"
    $steps.stop = @{status="ok"; waited_seconds=$waited}
} else {
    Write-OK "VM already Off"
    $steps.stop = @{status="already_off"}
}

# -- Step 2: robocopy VHDX files --
Write-Stage "Step 2: robocopy VHDX files (boot + data) -> $BackupRoot"
New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
# NO /MIR here -- /MIR traverses ALL subdirectories including the zephyr-ch\ config
# folder, where .vmcx/.vmgs/.VMRS are locked by Hyper-V VMMS (causes indefinite hang).
# We only need to copy 2 specific files, so plain copy with /R:2 /W:5 is sufficient.
# /NFL /NDL no file/dir list (less noise for huge files), /NP no progress %, /BYTES raw sizes
$rcArgs = @($VmRoot, $BackupRoot, "boot.vhdx", "data.vhdx",
            "/R:2", "/W:5", "/MT:8", "/NFL", "/NDL", "/NP", "/BYTES")
$rcLog = & robocopy @rcArgs
$rcExit = $LASTEXITCODE
# robocopy exit codes: 0=no change, 1=ok copied, <8 success, >=8 failure
if ($rcExit -ge 8) {
    Write-Err "robocopy VHDX failed (exit $rcExit)"; $steps.vhdx = @{status="failed"; exit=$rcExit}
    # Attempt to restart VM even on failure
    Write-Warn "Attempting to restart VM despite copy failure..."
    Start-VM -Name $VmName -ErrorAction SilentlyContinue
    $report = @{timestamp=(Get-Date).ToString("o"); steps=$steps; success=$false; error="robocopy exit $rcExit"}
    $report | ConvertTo-Json -Depth 4 | Out-File $LogFile -Encoding UTF8
    exit 1
}
$copiedDataGB = [math]::Round((Get-Item (Join-Path $BackupRoot "data.vhdx")).Length / 1GB, 2)
Write-OK "VHDX copy done (exit=$rcExit, data.vhdx=${copiedDataGB}GB)"
$steps.vhdx = @{status="ok"; exit=$rcExit; data_vhdx_gb=$copiedDataGB}

# -- Step 3: Copy VM config folder --
# .vmcx/.vmgs/.VMRS are locked by Hyper-V VMMS even when VM is stopped.
# Strategy: Copy-Item -Force (handles most files), then robocopy for anything Copy-Item misses.
# Locked files are non-fatal -- VHDX is the critical part. For DR, a new VM can be
# created and VHDX files attached manually if .vmcx is unavailable (see dr_runbook Sec.3.1).
Write-Stage "Step 3: Copy VM config -> $BackupRoot\$VmName"
$configDst = Join-Path $BackupRoot $VmName
New-Item -ItemType Directory -Path $configDst -Force | Out-Null
$configFilesCopied = 0; $configFilesLocked = @()
# Copy each file individually (Copy-Item can sometimes read files robocopy can't)
$configSrcDir = Join-Path $configDir "Virtual Machines"
$configDstDir = Join-Path $configDst "Virtual Machines"
if (Test-Path $configSrcDir) {
    New-Item -ItemType Directory -Path $configDstDir -Force | Out-Null
    # Also copy subdirectories (e.g., GUID-named dirs)
    $configSrcItems = Get-ChildItem $configSrcDir -Recurse -Force -ErrorAction SilentlyContinue
    foreach ($item in $configSrcItems) {
        $relPath = $item.FullName.Substring($configSrcDir.Length)
        $dstPath = Join-Path $configDstDir $relPath
        if ($item.PSIsContainer) {
            New-Item -ItemType Directory -Path $dstPath -Force | Out-Null
            continue
        }
        try {
            Copy-Item $item.FullName $dstPath -Force -ErrorAction Stop
            $configFilesCopied++
        } catch {
            $configFilesLocked += $item.Name
        }
    }
}
# Also copy Snapshots directory if it exists
$snapSrc = Join-Path $configDir "Snapshots"
if (Test-Path $snapSrc) {
    Copy-Item $snapSrc (Join-Path $configDst "Snapshots") -Recurse -Force -ErrorAction SilentlyContinue
}
if ($configFilesLocked.Count -gt 0) {
    Write-Warn "Config copy: $configFilesCopied files copied, $($configFilesLocked.Count) locked by VMMS: $($configFilesLocked -join ', ')"
    Write-Warn "Locked config files are non-fatal. For DR, create new VM + attach VHDX manually (dr_runbook Sec.3.1)."
    $steps.config = @{status="warn"; files_copied=$configFilesCopied; locked=$configFilesLocked}
} else {
    Write-OK "Config copy done ($configFilesCopied files)"
    $steps.config = @{status="ok"; files_copied=$configFilesCopied}
}

# -- Step 4: Start VM --
Write-Stage "Step 4: Starting VM '$VmName'..."
Start-VM -Name $VmName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 10
$vmState = (Get-VM -Name $VmName).State
if ($vmState -ne 'Running') {
    Write-Err "VM failed to start (state=$vmState)"
    $steps.start = @{status="failed"; state=$vmState}
} else {
    Write-OK "VM started"
    $steps.start = @{status="ok"}
}

# -- Step 5: Wait for ClickHouse to be reachable --
# Read CH host from .env.clickhouse (CH runs inside VM at 172.24.30.100, NOT localhost)
$chHttpHost = "localhost"; $chHttpPort = 8123
$chEnvFile = "$ProjectRoot\config\.env.clickhouse"
if (Test-Path $chEnvFile) {
    foreach ($line in (Get-Content $chEnvFile -Encoding UTF8)) {
        if ($line -match '^CLICKHOUSE_HOST=(.+)$')      { $chHttpHost = $matches[1].Trim() }
        if ($line -match '^CLICKHOUSE_HTTP_PORT=(.+)$') { $chHttpPort = [int]$matches[1].Trim() }
    }
}
$chBaseUrl = "http://${chHttpHost}:${chHttpPort}/"
Write-Stage "Step 5: Waiting for ClickHouse HTTP ($chBaseUrl)..."
$chOk = $false
for ($i = 0; $i -lt 60; $i++) {  # 5 min
    try {
        $resp = curl.exe -s --max-time 5 $chBaseUrl --data-binary "SELECT 1" 2>$null
        if ($LASTEXITCODE -eq 0 -and $resp -match "1") { $chOk = $true; break }
    } catch { }
    Start-Sleep -Seconds 5
}
if ($chOk) {
    Write-OK "ClickHouse reachable"
    $steps.ch_reachable = @{status="ok"}
} else {
    Write-Warn "ClickHouse not reachable after 5 min (VM may still be booting -- check manually)"
    $steps.ch_reachable = @{status="timeout"}
}

# -- Step 6: Record CH version + config hash (for future AutoCheck comparison) --
# Probe AFTER VM restart so the recorded state matches what's actually running.
$recordedVersion = ""; $recordedHash = ""
if ($chOk -and (Test-Path "$ProjectRoot\config\.env.ch_backup")) {
    $probeCmd = "sudo sh -c '" +
        "echo =V=; clickhouse-server --version 2>/dev/null | head -1; " +
        "echo =H=; sha256sum /etc/clickhouse-server/config.xml /etc/clickhouse-server/users.xml /etc/clickhouse-server/config.d/backup_disk.xml /etc/fstab 2>/dev/null | sha256sum" +
        "'"
    try {
        $probe = & python $ChSshHelper --cmd $probeCmd --sudo --json 2>&1 | ConvertFrom-Json
        if ($probe.exit_code -eq 0) {
            if ($probe.stdout -match '=V=\s*(.*)') { $recordedVersion = $matches[1].Trim() }
            if ($probe.stdout -match '=H=\s*([0-9a-f]{64})') { $recordedHash = $matches[1].Trim() }
            Write-OK "Recorded CH version + config hash (for next AutoCheck)"
        }
    } catch { Write-Warn "Could not probe CH version/hash after backup: $($_.Exception.Message)" }
}

# -- Report --
$duration = (Get-Date) - $backupStart
$report = @{
    timestamp = (Get-Date).ToString("o")
    duration_seconds = [math]::Round($duration.TotalSeconds, 1)
    vm_name = $VmName
    backup_path = $BackupRoot
    data_vhdx_gb = $copiedDataGB
    steps = $steps
    success = ($steps.vhdx.status -eq "ok" -and $steps.start.status -eq "ok")
    ch_version = $recordedVersion
    ch_config_hash = $recordedHash
}
New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
$report | ConvertTo-Json -Depth 4 | Out-File $LogFile -Encoding UTF8

# Update backup_state.json with VM backup timestamp + version/hash baseline
Set-StateField "last_ch_vm_backup_time" (Get-Date).ToString("o")
Set-StateField "last_ch_vm_backup_path" $BackupRoot
Set-StateField "last_ch_vm_backup_success" ([bool]$report.success)
if ($recordedVersion) { Set-StateField "last_ch_vm_version" $recordedVersion }
if ($recordedHash)    { Set-StateField "last_ch_vm_config_hash" $recordedHash }
Set-StateField "last_ch_vm_autocheck_time" (Get-Date).ToString("o")
Set-StateField "last_ch_vm_autocheck_result" "full_backup_done"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-OK "CH VM backup completed in $([math]::Round($duration.TotalMinutes,1)) min"
Write-Host "  Path: $BackupRoot" -ForegroundColor White
Write-Host "  Log:  $LogFile" -ForegroundColor White
Write-Host "  Success: $($report.success)" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green
if (-not $report.success) { exit 2 }
