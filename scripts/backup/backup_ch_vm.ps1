<#
.SYNOPSIS
    Backup of the ClickHouse Hyper-V VM (config copy -> F:, full image -> G:) plus
    an opt-in ordered compaction window for the host-side .vhdx.
.DESCRIPTION
    [BLUEPRINT] MOD-INF-043 | Section 3.6
    Backs up the zephyr-ch VM with TWO homes, per the 2026-09-24 Owner ruling
    recorded in backup_config.yaml and expected by restore.ps1:
      boot.vhdx + VM config  -> F:\ch_vm_backup       (config-level, fast to restore)
      data.vhdx full image   -> G:\backup\ch_vm_backup (archive vault, DR point)
    The CH backup disk (F:\ch_backup_disk.vhdx) is deliberately EXCLUDED -- it is
    the backup target itself, not part of the VM's persistent state.

    Three modes:
      (default, -Force)  - Full backup: stop VM -> robocopy VHDX + config -> start VM.
                           Downtime ~30-90 min (data.vhdx is in the 400-600 GB range).
      -AutoCheck         - Smart weekly: SSH-check CH version + config hashes vs last
                           recorded state (backup_state.json). Unchanged = SKIP (zero
                           downtime). Changed = run full backup. Designed for weekly
                           scheduled task -- 99% of weeks skip with no downtime.

    Overwrite policy: robocopy copies the named VHDX files only (no /MIR -- see
    Step 2 for why /MIR hangs on VMMS-locked config files). Unchanged files (same
    size+timestamp) are skipped; changed files are fully re-copied (VHDX is a
    single monolithic file -- no partial copy possible).

    WHY -AutoCheck skips most weeks:
      data.vhdx changes daily (CH writes data), but the data itself is covered by
      daily BACKUP TO Disk (incremental). The VM backup's value is OS + CH program
      + CH config (static, only changes on upgrade). Checking CH version + config
      hash avoids copying hundreds of GB every week.

    -CompactWindow adds one ordered step in the middle of a full backup, because
    the host-side .vhdx only ever grows (Hyper-V dynamic disk semantics): guest
    space freed by CH is not returned to D: until Optimize-VHD runs with the VM
    Off. The order is enforced by the script, not by convention:
      preconditions -> stop VM -> copy fresh image to G -> verify image length ->
      Optimize-VHD -Mode Full -> start VM -> CH health probe -> state writeback ->
      only then retire the stale F copy (recycle bin, never a bare rm).
    Refusals are exit 6 (preconditions) / exit 7 (image not verified; VM restarted).
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
.PARAMETER CompactWindow
    Ordered host-space rescue window (see description). Requires the account to carry
    BUILTIN\Hyper-V Administrators so Get-VHD/Stop-VM/Optimize-VHD actually work; the
    gate probes that capability instead of an Administrator token claim. If
    Optimize-VHD alone still refuses (access denied), the VM is restarted, the run is
    reported failed, and the same command re-run from an elevated PowerShell is the
    only remaining action.
.PARAMETER SelfSession
    With -CompactWindow: session id to exclude from the "is any lane running?"
    precondition. Empty (default) counts every active session, so an operator who is
    also a registered session must pass their own sid here or be refused.
.EXAMPLE
    .\backup_ch_vm.ps1                  # interactive full backup
    .\backup_ch_vm.ps1 -Force           # full backup, no prompt
    .\backup_ch_vm.ps1 -AutoCheck       # weekly scheduled (skip if unchanged)
    .\backup_ch_vm.ps1 -RegisterTask    # register weekly task (run as Administrator)
    # Compaction window: all other lanes stopped, CH ingestion idle:
    .\backup_ch_vm.ps1 -CompactWindow -SelfSession st-fms-tc-20260927
#>
param([switch]$Force, [switch]$AutoCheck, [switch]$RegisterTask, [switch]$UnregisterTask, [switch]$TaskStatus, [switch]$CompactWindow, [string]$SelfSession = "")

$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"
$VmName = "zephyr-ch"
$VmRoot = "D:\HyperV\VMs\zephyr-ch"
# Homes per the 2026-09-24 Owner ruling already recorded in backup_config.yaml:67-68
# and expected by restore.ps1 ($ChVmImageHome): F keeps the CONFIG-LEVEL copy
# (boot.vhdx + VM config), the FULL data.vhdx image belongs to the G archive.
# Before this change the writer still copied data.vhdx to F -- that is what filled
# F by 599 GiB on 2026-09-26 (LEDGER_final.md prescription P-6). Writer now obeys.
$BackupRoot = "F:\ch_vm_backup"          # config-level home (boot.vhdx + VM config)
$ImageHome = "G:\backup\ch_vm_backup"    # full data.vhdx image home
$ChSshHelper = "$ProjectRoot\scripts\backup\ch_vm_ssh.py"
$StateFile = "$ProjectRoot\data\databases\backup_state.json"
$LogFile = "$ProjectRoot\logs\ch_vm_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$TaskName = "ZephyrAlpha-WeeklyVMBackup"

function Write-Stage($msg) { Write-Host "[CH-VM-BACKUP] $msg" -ForegroundColor Cyan }
function Write-OK($msg)    { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERR] $msg" -ForegroundColor Red }

# -- AutoCheck decision (pure function; consumer = the -AutoCheck branch below) --
# Fail-CLOSED by design (2026-09-27 cure of the 09-26 incident): an unknown VM
# state must never be interpreted as "changed, therefore copy 599 GB".
# Returns one of: skip | proceed | blocked_unprobeable | blocked_unparsable
function Get-AutoCheckDecision {
    param(
        [bool]$ProbeOk,
        [string]$Version,
        [string]$Hash,
        [string]$LastVersion,
        [string]$LastHash
    )
    if (-not $ProbeOk) { return "blocked_unprobeable" }
    if (-not $Version -or -not $Hash) { return "blocked_unparsable" }
    if ($Version -eq $LastVersion -and $Hash -eq $LastHash) { return "skip" }
    return "proceed"
}

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

# ==================== -CompactWindow: ordered stop/refresh/compact window ====================
# Pure decision helper (unit-testable, no side effects).
function Get-CompactionPrereqDecision {
    param(
        [bool]$HyperVUsable,
        [bool]$VmFound,
        [double]$ImageFreeGB,
        [double]$ImageNeedGB,
        [int]$ActiveSessions,
        [bool]$BackupFresh
    )
    # Gate on the capability actually needed (Hyper-V cmdlets can open the disk),
    # not on an Administrator token claim: this account is in
    # BUILTIN\Hyper-V Administrators yet IsInRole(Administrator) is False, and the
    # 2026-09-26 incident run itself stopped the VM under a Limited task token
    # (ZephyrAlpha-WeeklyVMBackup RunLevel=Limited, rc=0) -- so "not elevated" is
    # not evidence of "cannot do it". If Optimize-VHD still refuses, Step 3.5
    # reports permission_denied distinctly and the VM is restarted.
    if (-not $HyperVUsable) { return "blocked_not_hyperv_usable" }
    if (-not $VmFound) { return "blocked_vm_missing" }
    # A negative count means the session registry could not be read at all. Unknown
    # must never be read as "nobody is running" -- that is the same fail-open shape
    # that cost 599 GiB on 2026-09-26.
    if ($ActiveSessions -lt 0) { return "blocked_sessions_unreadable" }
    if ($ActiveSessions -gt 0) { return "blocked_lanes_active" }
    if (-not $BackupFresh) { return "blocked_backup_stale" }
    if ($ImageFreeGB -lt $ImageNeedGB) { return "blocked_image_space" }
    return "proceed"
}

# -- Retirement predicate for the stale config-level copy (pure, unit-testable). --
# Fail-closed: only retire when the G image is provably at least as complete AND
# provably not older, so the DR point is never nailed to a stale base.
function Get-RetireDecision {
    param(
        [bool]$StaleExists,
        [bool]$FreshExists,
        [double]$StaleGB,
        [double]$FreshGB,
        [double]$StaleAgeDays,
        [double]$FreshAgeDays
    )
    if (-not $StaleExists) { return "skipped_no_stale" }
    if (-not $FreshExists) { return "skipped_no_fresh_image" }
    if ($FreshGB + 0.01 -lt $StaleGB) { return "skipped_fresh_smaller" }
    if ($FreshAgeDays -gt $StaleAgeDays) { return "skipped_fresh_older" }
    return "retire"
}

if ($CompactWindow) {
    Write-Stage "Compaction window: precondition gate (stop -> refresh G image -> Optimize-VHD -> start)"
    $hvPath = Join-Path $VmRoot "data.vhdx"
    $hvUsable = $false
    try {
        $hvProbe = Get-VHD -Path $hvPath -ErrorAction Stop
        $hvUsable = [bool]($hvProbe -and $hvProbe.FileSize -gt 0)
    } catch { $hvUsable = $false }
    $vmObj = Get-VM -Name $VmName -ErrorAction SilentlyContinue
    $sess = 0
    try {
        $sess = (& python -c "import sys;sys.path.insert(0,r'$ProjectRoot\src');from zephyr.gov_enforcement.rule_bridge.session_worktree import SessionRegistry as R;print(len([s for s in R().list_active() if s.session_id != '$SelfSession']))") -join ''
    } catch { $sess = -1 }
    if ($sess -notmatch '^-?\d+$') { $sess = -1 }
    $st = $null
    try { $st = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $st = $null }
    $backupFresh = [bool]($st -and $st.last_backup_status -eq 'ok')
    $imgVol = Get-Volume -DriveLetter (Split-Path -Qualifier $ImageHome).TrimEnd(':') -ErrorAction SilentlyContinue
    $imgFreeGB = if ($imgVol) { [math]::Round($imgVol.SizeRemaining / 1GB, 1) } else { 0 }
    $dataVhdx = Join-Path $VmRoot "data.vhdx"
    $dataGB = if (Test-Path $dataVhdx) { [math]::Round((Get-Item $dataVhdx).Length / 1GB, 1) } else { 0 }
    $imgNeedGB = $dataGB + 20
    $decision = Get-CompactionPrereqDecision -HyperVUsable $hvUsable -VmFound ([bool]$vmObj) -ImageFreeGB $imgFreeGB -ImageNeedGB $imgNeedGB -ActiveSessions ([int]$sess) -BackupFresh $backupFresh
    Write-Host "  hyperv_usable=$hvUsable vm=$([bool]$vmObj) active_lanes=$sess backup_fresh=$backupFresh image_free=$imgFreeGB GB image_need=$imgNeedGB GB" -ForegroundColor White
    Write-Host "  decision: $decision" -ForegroundColor White
    if ($decision -ne "proceed") {
        Write-Err "Compaction window refused ($decision). Nothing was stopped and nothing was copied."
        Write-Err "  Meaning: the stop-the-VM step needs working Hyper-V cmdlets, an empty session registry, a fresh full backup and room on $ImageHome for one more full image."
        exit 6
    }
    Write-OK "Preconditions green: VM will be stopped; every ClickHouse consumer must already be idle."
    $Force = $true
    $script:DoCompact = $true
}

# ==================== -AutoCheck: smart skip-when-unchanged ====================
# Compares current CH version + config hash against last recorded state.
# Unchanged -> exit 0 (zero downtime). Changed -> fall through to full backup.
if ($AutoCheck) {
    Write-Stage "AutoCheck: probing CH version + config hash via SSH"
    $probeOk = $false
    $version = ""
    $hash = ""
    $blockReason = ""
    if (-not (Test-Path "$ProjectRoot\config\.env.ch_backup")) {
        $blockReason = "config/.env.ch_backup missing -- cannot decide"
    } else {
        # Single SSH round-trip: CH version + sha256 of config files + fstab
        $probeCmd = "sudo sh -c '" +
            "echo =V=; clickhouse-server --version 2>/dev/null | head -1; " +
            "echo =H=; sha256sum /etc/clickhouse-server/config.xml /etc/clickhouse-server/users.xml /etc/clickhouse-server/config.d/backup_disk.xml /etc/fstab 2>/dev/null | sha256sum" +
            "'"
        $probe = & python $ChSshHelper --cmd $probeCmd --sudo --json 2>&1 | ConvertFrom-Json
        if ($probe.exit_code -ne 0) {
            $blockReason = "SSH probe failed (exit $($probe.exit_code)): $($probe.stderr)"
        } else {
            $probeOk = $true
            $out = $probe.stdout
            if ($out -match '=V=\s*(.*)') { $version = $matches[1].Trim() }
            if ($out -match '=H=\s*([0-9a-f]{64})') { $hash = $matches[1].Trim() }
        }
    }
    $lastVersion = Get-StateField "last_ch_vm_version"
    $lastHash     = Get-StateField "last_ch_vm_config_hash"
    $decision = Get-AutoCheckDecision -ProbeOk $probeOk -Version $version -Hash $hash `
        -LastVersion ([string]$lastVersion) -LastHash ([string]$lastHash)

    Write-Host "  Probe ok:   $probeOk" -ForegroundColor White
    Write-Host "  Current version: $version" -ForegroundColor White
    Write-Host "  Current hash:    $hash" -ForegroundColor White
    Write-Host "  Last version:    $lastVersion" -ForegroundColor White
    Write-Host "  Last hash:       $lastHash" -ForegroundColor White
    Write-Host "  Decision:        $decision" -ForegroundColor White

    $nowIso = (Get-Date).ToString("o")
    if ($decision -eq "skip") {
        Write-OK "AutoCheck: CH version + config unchanged since last VM backup. SKIP (zero downtime)."
        # Record the skip so scheduled-task history shows it
        Set-StateField "last_ch_vm_autocheck_time" $nowIso
        Set-StateField "last_ch_vm_autocheck_result" "skipped_unchanged"
        $report = @{
            timestamp = $nowIso
            mode = "autocheck"
            result = "skipped_unchanged"
            version = $version; config_hash = $hash
        }
        New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
        $report | ConvertTo-Json -Depth 3 | Out-File $LogFile -Encoding utf8
        Write-Host "  Log: $LogFile" -ForegroundColor White
        exit 0
    }
    if ($decision -like "blocked*") {
        # 09-26 incident cure: previously every one of these paths fell through to a
        # full 599 GB copy (fail-open). Unknown state now stops loudly instead -- the
        # daily CH incremental chain is untouched, so nothing is lost by abstaining.
        if (-not $blockReason) {
            $blockReason = "probe returned but version/config hash unparsable (empty =V= or =H=)"
        }
        Write-Err "AutoCheck: $decision -- REFUSING full backup on unknown VM state. $blockReason"
        Write-Err "  Why refusing: an unprobeable VM must not be read as 'config changed'."
        Write-Err "  2026-09-26 this path copied data.vhdx (599 GiB) onto F: and broke the"
        Write-Err "  F>=700 GiB cold-store red line (see LEDGER_final.md prescription P-6)."
        Write-Err "  Next: fix SSH probe / .env.ch_backup, then re-run -AutoCheck or -Force."
        Set-StateField "last_ch_vm_autocheck_time" $nowIso
        Set-StateField "last_ch_vm_autocheck_result" $decision
        $report = @{
            timestamp = $nowIso
            mode = "autocheck"
            result = $decision
            reason = $blockReason
            probe_ok = $probeOk
            version = $version; config_hash = $hash
        }
        New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
        $report | ConvertTo-Json -Depth 3 | Out-File $LogFile -Encoding utf8
        Write-Host "  Log: $LogFile" -ForegroundColor White
        exit 3
    }
    $reason = if ($version -ne $lastVersion) { "version changed ($lastVersion -> $version)" } else { "config hash changed" }
    Write-Warn "AutoCheck: $reason -- proceeding to full backup"
    # Fall through to full backup below (AutoCheck decided a backup is needed).
    $Force = $true  # AutoCheck runs unattended via scheduled task -- no interactive prompt
}

# -- Capacity guard decision (pure function; consumer = pre-check block below) --
# The four-drive red lines (F>=700 / G>=500 free GB) lived ONLY in the off-repo audit
# SOP prose -- no code reader, so a 599 GB full copy could legally blow through them
# (2026-09-26 incident). Numbers now come from scripts/backup/backup_config.yaml
# (capacity_guard.min_free_gb), and a missing/unreadable key falls back to the
# constant below instead of silently disabling the guard.
$MinFreeFallbackGB = 700

function Get-CapacityGuardDecision {
    param(
        [double]$FreeGB,
        [double]$NeedGB,
        [double]$MinFreeGB
    )
    if ($FreeGB -lt $NeedGB) { return "refuse_too_small" }
    if (($FreeGB - $NeedGB) -lt $MinFreeGB) { return "refuse_below_red_line" }
    return "proceed"
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

# Image volume free space check: data.vhdx lands on $ImageHome (G vault), so the
# red line that must hold is G's; the config-level F copy is only boot.vhdx + config.
# Target volume free space check (need ~data.vhdx size + buffer)
$TargetDrive = (Split-Path -Qualifier $ImageHome).TrimEnd(':')
$tVol = Get-Volume -DriveLetter $TargetDrive -ErrorAction SilentlyContinue
if (-not $tVol) { Write-Err "Drive $TargetDrive`: not online (BackupRoot=$BackupRoot)"; exit 1 }
$freeGB = [math]::Round($tVol.SizeRemaining / 1GB, 1)
$needGB = $dataSizeGB + 20  # data + boot + config + buffer

# Red line source: backup_config.yaml capacity_guard.min_free_gb.<drive>;
# unreadable/missing => fallback constant + loud source marker (never 0 = never off).
$guardSource = "config"
$minFreeGB = 0.0
try {
    $cfgText = Get-Content "$ProjectRoot\scripts\backup\backup_config.yaml" -Raw -Encoding UTF8 -ErrorAction Stop
    $cfg = ($cfgText | & python -c "import sys,yaml;d=yaml.safe_load(sys.stdin.read()) or {};print((d.get('capacity_guard') or {}).get('min_free_gb',{}).get('$TargetDrive',''))") -join ''
    if ($cfg -match '^[0-9]+(\.[0-9]+)?$') { $minFreeGB = [double]$cfg } else { $guardSource = "fallback" }
} catch { $guardSource = "fallback" }
if ($guardSource -eq "fallback") {
    $minFreeGB = $MinFreeFallbackGB
    Write-Warn "capacity_guard.min_free_gb.$TargetDrive`: not readable from backup_config.yaml -- using built-in fallback ${minFreeGB}GB (guard stays ON)"
}

$guardDecision = Get-CapacityGuardDecision -FreeGB $freeGB -NeedGB $needGB -MinFreeGB $minFreeGB
if ($guardDecision -ne "proceed") {
    Write-Err "Capacity guard [$guardDecision] on $TargetDrive`: free=${freeGB}GB need=${needGB}GB red_line=${minFreeGB}GB (source=$guardSource)"
    Write-Err "  Refusing to copy $dataSizeGB GB: a full VM image here would breach the registered drive red line."
    Write-Err "  See docs/_working/disk_reorg_campaign/LEDGER_final.md prescription P-6 and the 2026-09-26 F-drive incident."
    $report = @{
        timestamp = (Get-Date).ToString("o")
        mode = "capacity_guard"
        result = $guardDecision
        drive = $TargetDrive
        free_gb = $freeGB; need_gb = $needGB; min_free_gb = $minFreeGB
        guard_source = $guardSource
    }
    New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
    $report | ConvertTo-Json -Depth 3 | Out-File $LogFile -Encoding utf8
    exit 4
}
Write-OK "$TargetDrive`: drive free = ${freeGB}GB (need ~${needGB}GB, red line ${minFreeGB}GB, source=$guardSource)"

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

# -- Step 2: copy VHDX files to their ruled homes --
Write-Stage "Step 2: copy boot.vhdx -> $BackupRoot (config-level), data.vhdx -> $ImageHome (full image)"
New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
New-Item -ItemType Directory -Path $ImageHome -Force | Out-Null
# NO /MIR here -- /MIR traverses ALL subdirectories including the zephyr-ch\ config
# folder, where .vmcx/.vmgs/.VMRS are locked by Hyper-V VMMS (causes indefinite hang).
# We only need to copy 2 specific files, so plain copy with /R:2 /W:5 is sufficient.
# /NFL /NDL no file/dir list (less noise for huge files), /NP no progress %, /BYTES raw sizes
#
# The two files go to DIFFERENT drives on purpose: F free sits at the 700 GB cold
# storage red line, G is the backup vault. Copying each separately also means a
# failed image copy never silently leaves a half-written data.vhdx on F.
$rcBoot = & robocopy $VmRoot $BackupRoot "boot.vhdx" "/R:2" "/W:5" "/NFL" "/NDL" "/NP" "/BYTES"
$rcBootExit = $LASTEXITCODE
$rcData = & robocopy $VmRoot $ImageHome "data.vhdx" "/R:2" "/W:5" "/MT:4" "/NFL" "/NDL" "/NP" "/BYTES"
$rcDataExit = $LASTEXITCODE
# robocopy exit codes: 0=no change, 1=ok copied, <8 success, >=8 failure
if ($rcBootExit -ge 8 -or $rcDataExit -ge 8) {
    Write-Err "robocopy VHDX failed (boot=$rcBootExit data=$rcDataExit)"
    $steps.vhdx = @{status="failed"; boot_exit=$rcBootExit; data_exit=$rcDataExit}
    # Attempt to restart VM even on failure
    Write-Warn "Attempting to restart VM despite copy failure..."
    Start-VM -Name $VmName -ErrorAction SilentlyContinue
    $report = @{timestamp=(Get-Date).ToString("o"); steps=$steps; success=$false; error="robocopy boot=$rcBootExit data=$rcDataExit"}
    $report | ConvertTo-Json -Depth 4 | Out-File $LogFile -Encoding utf8
    exit 1
}
$copiedDataGB = [math]::Round((Get-Item (Join-Path $ImageHome "data.vhdx")).Length / 1GB, 2)
Write-OK "VHDX copy done (boot=$rcBootExit data=$rcDataExit, data.vhdx=${copiedDataGB}GB at $ImageHome)"
$steps.vhdx = @{status="ok"; boot_exit=$rcBootExit; data_exit=$rcDataExit; data_vhdx_gb=$copiedDataGB; image_home=$ImageHome}

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

# -- Step 3.5: ordered compaction (only inside an explicit -CompactWindow, VM is Off here) --
if ($script:DoCompact) {
    Write-Stage "Step 3.5: Optimize-VHD Full on $dataVhdx (VM is Off, fresh image just verified at $ImageHome)"
    $imgFile = Join-Path $ImageHome "data.vhdx"
    if (-not (Test-Path $imgFile)) {
        Write-Err "Refusing to compact: no freshly copied image at $imgFile (a compaction without a verified copy is how archives get lost)."
        Start-VM -Name $VmName -ErrorAction SilentlyContinue
        exit 7
    }
    $vhdxMeta = Get-VHD -Path $dataVhdx
    $before = $vhdxMeta.FileSize
    $imgBytes = (Get-Item $imgFile).Length
    $srcBytes = $vhdxMeta.FileSize
    if ($imgBytes -lt $srcBytes) {
        Write-Err "Refusing to compact: image at $imgFile is $([math]::Round($imgBytes/1GB,2)) GB but source was $([math]::Round($srcBytes/1GB,2)) GB -- copy is short, aborting before any shrink."
        Start-VM -Name $VmName -ErrorAction SilentlyContinue
        exit 7
    }
    $compactErr = ""
    try {
        Optimize-VHD -Path $dataVhdx -Mode Full -ErrorAction Stop
    } catch {
        # Never let a failed compaction leave the VM powered off: record the cause and
        # fall through to Step 4 (start VM); the run reports failure in its log.
        $compactErr = "$($_.Exception.Message)"
    }
    $after = (Get-VHD -Path $dataVhdx).FileSize
    $reclaimedGB = [math]::Round(($before - $after) / 1GB, 2)
    if ($compactErr) {
        $looksDenied = $compactErr -match '(?i)access|denied|permission|privile'
        Write-Err "Compaction FAILED, VM will still be restarted. Error: $compactErr"
        if ($looksDenied) {
            Write-Err "  Looks like a permission refusal -- re-run the same command from an elevated PowerShell."
        }
        $steps.compact = @{status="failed"; error=$compactErr; permission_denied=[bool]$looksDenied; before_bytes=$before; after_bytes=$after}
        Set-StateField "last_vhdx_compaction" (Get-Date).ToString("o")
        Set-StateField "last_vhdx_compaction_result" "failed"
    } else {
        Write-OK "Compaction done: $([math]::Round($before/1GB,2)) GB -> $([math]::Round($after/1GB,2)) GB (reclaimed ${reclaimedGB} GB)"
        $steps.compact = @{status="ok"; before_bytes=$before; after_bytes=$after; reclaimed_gb=$reclaimedGB; image_verified_bytes=$imgBytes}
        Set-StateField "last_vhdx_compaction" (Get-Date).ToString("o")
        Set-StateField "last_vhdx_compaction_result" "ok"
        Set-StateField "last_vhdx_compaction_reclaimed_gb" $reclaimedGB
    }
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
    success = ($steps.vhdx.status -eq "ok" -and $steps.start.status -eq "ok" -and ((-not $script:DoCompact) -or $steps.compact.status -eq "ok"))
    compaction = if ($script:DoCompact) { $steps.compact } else { $null }
    ch_version = $recordedVersion
    ch_config_hash = $recordedHash
}
New-Item -ItemType Directory -Path "$ProjectRoot\logs" -Force | Out-Null
$report | ConvertTo-Json -Depth 4 | Out-File $LogFile -Encoding utf8

# Update backup_state.json with VM backup timestamp + version/hash baseline
Set-StateField "last_ch_vm_backup_time" (Get-Date).ToString("o")
Set-StateField "last_ch_vm_backup_path" $BackupRoot
Set-StateField "last_ch_vm_backup_success" ([bool]$report.success)
if ($recordedVersion) { Set-StateField "last_ch_vm_version" $recordedVersion }
if ($recordedHash)    { Set-StateField "last_ch_vm_config_hash" $recordedHash }
Set-StateField "last_ch_vm_autocheck_time" (Get-Date).ToString("o")
Set-StateField "last_ch_vm_autocheck_result" "full_backup_done"

# -- Step 7: retire the stale config-level data.vhdx on F, only after a verified image exists on G --
# This is the O-1 orphan (2026-09-26 accident copy). Order matters: the G image was
# copied while the VM was Off and byte-length verified above, so deleting the F copy
# cannot leave us without a full image. Recycle-bin first, never a bare rm.
if ($script:DoCompact) {
    $staleOnF = Join-Path $BackupRoot "data.vhdx"
    $freshImage = Join-Path $ImageHome "data.vhdx"
    $staleExists = Test-Path $staleOnF
    $freshExists = Test-Path $freshImage
    $staleGB = if ($staleExists) { [math]::Round((Get-Item $staleOnF).Length / 1GB, 2) } else { 0 }
    $freshGB = if ($freshExists) { [math]::Round((Get-Item $freshImage).Length / 1GB, 2) } else { 0 }
    $now = Get-Date
    $staleAgeDays = if ($staleExists) { ($now - (Get-Item $staleOnF).LastWriteTime).TotalDays } else { 0 }
    $freshAgeDays = if ($freshExists) { ($now - (Get-Item $freshImage).LastWriteTime).TotalDays } else { 0 }
    $retireDecision = Get-RetireDecision -StaleExists $staleExists -FreshExists $freshExists -StaleGB $staleGB -FreshGB $freshGB -StaleAgeDays $staleAgeDays -FreshAgeDays $freshAgeDays
    Write-Host "  retire decision: $retireDecision (F=${staleGB}GB/${staleAgeDays}d  G=${freshGB}GB/${freshAgeDays}d)" -ForegroundColor White
    if ($retireDecision -eq "retire") {
        $shell = New-Object -ComObject Shell.Application
        $shell.Namespace(0).ParseName($staleOnF).InvokeVerb("delete")
        Start-Sleep -Seconds 5
        if (Test-Path $staleOnF) {
            Write-Warn "Stale F image still present (recycle verb refused) -- leaving it in place, reporting only."
            $steps.retire = @{status="warn"; path=$staleOnF; stale_gb=$staleGB; decision=$retireDecision}
        } else {
            Write-OK "Retired stale config-level image to recycle bin: $staleOnF (${staleGB} GB, superseded by the $ImageHome copy)"
            $steps.retire = @{status="ok"; path=$staleOnF; stale_gb=$staleGB; evidence="recycle-bin"}
        }
    } else {
        if ($staleExists) { Write-Warn "Not retiring F image: decision=$retireDecision (see counters above)" }
        $steps.retire = @{status="skipped"; reason=$retireDecision; stale_gb=$staleGB; fresh_gb=$freshGB}
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-OK "CH VM backup completed in $([math]::Round($duration.TotalMinutes,1)) min"
Write-Host "  Path: $BackupRoot" -ForegroundColor White
Write-Host "  Log:  $LogFile" -ForegroundColor White
Write-Host "  Success: $($report.success)" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green
if (-not $report.success) { exit 2 }
