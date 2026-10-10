# [BLUEPRINT] MOD-INF-043 | backup_shadow.ps1
# SHADOW chain of scripts/backup/backup.ps1 (st-backfix-20261010, work order T1+T2).
#
# SHADOW CONTRACT (G4-6: shadow parallel >= 7 days + auto-rollback criteria + change trace):
#   - ZERO writes to production backup targets (no G:\backup, no F:\*, no prod vault).
#     Every stage target lives under -TargetRoot (default .runtime/tmp/backfix_shadow/).
#   - ZERO writes to production state: uses backup_state_shadow.json + backup_shadow.lock.
#   - CH stage is PROBE-ONLY by default (reads system.backups via HTTP SELECT; never
#     fires BACKUP). -AllowChWrite exists for the future promotion rehearsal only.
#   - Source tree is a parameter (-SourceRoot); drills point it at a small tree.
#   - Stage semantics mirror backup.ps1 v2.1 (same stage names/order, guarded mirror
#     probe/additive logic, versioned-vault diff via robocopy, bundle cadence 7d/keep2).
#
# T1 MECHANISM UNDER TEST (the production fix this shadow validates):
#   1. checkpoint on start (status=running, pid+ts) / after EVERY stage (stage+ts+artifact
#      sha256) / on finish (status=finished). Written atomically (tmp+move).
#   2. cadence gate READS CHECKPOINTS: a run killed after stage X does not re-burn
#      stage X on the next run - per-stage checkpoint freshness (CH 24h, full 8h).
#      This is the cure for "state never written back because death precedes STAGE 4".
#   3. resume: stages with a fresh ok checkpoint are skipped and logged as
#      checkpoint_skip (resumability), idempotent stages re-verify instead of redoing.
#
# T2 MECHANISM UNDER TEST:
#   - lock carries holder PID + START (same format as prod); holder-liveness is the
#     primary judgment, age only a fallback (prod form, 2026-09-25); a DEAD holder is
#     recorded as LOCK_TAKEOVER in the run log before proceeding (never a silent
#     "lock file exists => fast-exit forever" path).
#
# ASCII-only (PS5.1 non-BOM safe). Observational safety valve: deleting the shadow
# [TTL] task_bound
# scheduled task (ZephyrAlpha-BackupShadow) fully disables the shadow chain - that IS
# the registered auto-rollback action.
param(
  [ValidateSet("all", "ch", "code")][string]$Mode = "all",
  [switch]$Force,                        # bypass per-stage checkpoint cadence (drill reset)
  [string]$SourceRoot = "D:\ZephyrAlpha\scripts\backup",
  [string]$TargetRoot = "D:\ZephyrAlpha\.runtime\tmp\backfix_shadow\targets",
  [string]$StateFile = "D:\ZephyrAlpha\data\databases\backup_state_shadow.json",
  [string]$LockFile = "D:\ZephyrAlpha\.runtime\backup_shadow.lock",
  [int]$StageDelaySeconds = 0,           # per-stage artificial delay: kill-mid-run drills
  [switch]$AllowChWrite,                 # promotion rehearsal only; default probe-only
  [switch]$IncludeBundle,                # default on; heavy stages can be shed in rapid drills
  [switch]$IncludeMirrors
)
$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\ZephyrAlpha"
$RunAt = Get-Date
$RunId = $RunAt.ToString("yyyyMMdd_HHmmss")
$LogFile = "$ProjectRoot\logs\backup_shadow_report_$RunId.json"
$ChHttpHost = "localhost"; $ChHttpPort = 8123

$script:StageLog = @()
function Write-Stage($msg) {
    if ($backupStartTime) {
        $script:StageLog += [ordered]@{ stage = $msg; t_seconds = [math]::Round(((Get-Date) - $backupStartTime).TotalSeconds, 1) }
    }
    Write-Host "[SHADOW] $msg" -ForegroundColor Cyan
}
function Write-OK($msg)   { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR] $msg" -ForegroundColor Red }

# ==================== T1: segmented checkpoint state ====================
# Atomic JSON state write: tmp file + File.Move (same crash-safety class as
# file_utils.safe_write_text; ps1 side keeps it dependency-free).
function Write-ShadowState {
    param([hashtable]$State)
    $State.updated_at = (Get-Date).ToString("o")
    $tmp = "$StateFile.tmp"
    $json = ($State | ConvertTo-Json -Depth 6) -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($tmp, $json, (New-Object System.Text.UTF8Encoding($false)))
    if (Test-Path $StateFile) { Remove-Item $StateFile -Force -ErrorAction SilentlyContinue }
    [System.IO.File]::Move($tmp, $StateFile)
}

# One checkpoint = one stage boundary. status: running | stage_ok | stage_skip | failed | finished
function Write-Checkpoint {
    param(
        [hashtable]$State,
        [string]$Stage,
        [string]$Status,
        [string]$ArtifactSha = "",
        [string]$Detail = ""
    )
    $entry = [ordered]@{
        stage = $Stage; status = $Status; ts = (Get-Date).ToString("o")
        artifact_sha256 = $ArtifactSha; detail = $Detail
    }
    if (-not $State.ContainsKey("stages")) { $State.stages = @() }
    # same stage re-entry (resume pass): keep history, latest entry is authoritative
    $State.stages = @($State.stages) + $entry
    $State.run_id = $RunId
    $State.pid = $PID
    $State.status = $(if ($Status -eq "finished") { "finished" } elseif ($Status -eq "failed") { "failed" } else { "running" })
    if ($Status -eq "finished") { $State.finished_at = $entry.ts }
    Write-ShadowState -State $State
    Write-OK ("checkpoint: {0} = {1}{2}" -f $Stage, $Status, $(if ($Detail) { " ($Detail)" } else { "" }))
}

# Read the latest OK checkpoint entry for a stage (freshness basis). A later
# checkpoint_skip/running entry must NOT erase the freshness a completed stage_ok
# recorded - resume passes re-stamp skip entries, the ok evidence stays authoritative.
# $null when the stage has never completed ok.
function Get-LatestCheckpoint {
    param([hashtable]$State, [string]$Stage)
    if (-not $State.ContainsKey("stages")) { return $null }
    $latest = $null
    foreach ($e in @($State.stages)) {
        if ($e.stage -eq $Stage -and $e.status -eq "stage_ok") { $latest = $e }
    }
    return $latest
}

# T1 cadence: a stage is FRESH when its latest checkpoint is ok/skip-with-evidence
# within its cadence window (ch=24h, everything else follows the full-run 8h gate).
# A killed run leaves its completed stages fresh - the cure for re-burn loops.
function Test-StageFresh {
    param([hashtable]$State, [string]$Stage, [double]$CadenceHours)
    $e = Get-LatestCheckpoint -State $State -Stage $Stage
    if (-not $e) { return $false }
    if ($e.status -ne "stage_ok") { return $false }
    try {
        $ageH = ((Get-Date) - [datetime]::Parse($e.ts)).TotalHours
        return ($ageH -lt $CadenceHours)
    } catch { return $false }
}

# ==================== T2: lock with holder-liveness + takeover trace ====================
function Test-ShadowLock {
    if (-not (Test-Path $LockFile)) { return $false }
    $lockAge = ((Get-Date) - (Get-Item $LockFile).LastWriteTime).TotalHours
    $holderPid = 0; $holderStart = $null
    try {
        $lockRaw = Get-Content $LockFile -Raw -ErrorAction Stop
        if ($lockRaw -match 'PID:(\d+)') { $holderPid = [int]$matches[1] }
        if ($lockRaw -match 'START:(\S+)') { try { $holderStart = [datetime]$matches[1] } catch { $holderStart = $null } }
    } catch { $holderPid = 0 }
    if ($holderPid -gt 0) {
        $holder = Get-Process -Id $holderPid -ErrorAction SilentlyContinue
        if (-not $holder) {
            Write-Warn "LOCK_TAKEOVER: holder PID $holderPid is dead (lock age $([math]::Round($lockAge,1))h) - taking over (T2: dead holder never means fast-exit-forever)"
            return $false
        }
        $pidRecycled = $false
        if ($holderStart) {
            try { $pidRecycled = ([Math]::Abs(($holder.StartTime - $holderStart).TotalMinutes) -gt 5) } catch { $pidRecycled = $false }
        }
        if ($pidRecycled) {
            Write-Warn "LOCK_TAKEOVER: holder PID $holderPid is a recycled PID (start mismatch) - taking over"
            return $false
        }
        Write-Warn "Another SHADOW backup is running (holder PID $holderPid alive, lock age $([math]::Round($lockAge,1))h). Exiting."
        return $true
    }
    if ($lockAge -lt 4) {
        Write-Warn "Another SHADOW backup is running (lock age $([math]::Round($lockAge,1))h < 4h, holder PID unreadable). Exiting."
        return $true
    }
    Write-Warn "LOCK_TAKEOVER: stale lock (age $([math]::Round($lockAge,1))h >= 4h, holder PID unreadable) - taking over"
    return $false
}
function Acquire-ShadowLock {
    $lockDir = Split-Path $LockFile
    if (-not (Test-Path $lockDir)) { New-Item -ItemType Directory -Path $lockDir -Force | Out-Null }
    [System.IO.File]::WriteAllText($LockFile, "PID:$PID START:$(Get-Date -Format 'o')", (New-Object System.Text.UTF8Encoding($false)))
}
function Release-ShadowLock {
    if (Test-Path $LockFile) { Remove-Item $LockFile -Force -ErrorAction SilentlyContinue }
}

# artifact hash for dir stages: sha256 over "relpath|len|mtime" lines (order-stable)
function Get-TreeFingerprint {
    param([string]$Root)
    $items = @(Get-ChildItem -LiteralPath $Root -Recurse -File -Force -ErrorAction SilentlyContinue | Sort-Object FullName)
    $sw = [System.IO.StringWriter]::new()
    foreach ($i in $items) {
        # format OUTSIDE the .NET method call: inside method parens, the comma splits
        # ARGUMENTS before -f can bind its RHS list (FormatError: index out of range)
        $line = "{0}|{1}|{2}" -f $i.FullName.Substring($Root.Length), $i.Length, $i.LastWriteTimeUtc.Ticks
        $sw.WriteLine($line)
    }
    $sw.Flush()
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($sw.ToString())
    return ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace "-", "").ToLower()
}

# ==================== main ====================
$backupStartTime = $RunAt
if (Test-ShadowLock) {
    try {
        $skipLog = "$ProjectRoot\logs\backup_shadow_skipped_$RunId.json"
        $skipObj = [ordered]@{ timestamp = (Get-Date -Format "o"); reason = "lock_held"; mode = $Mode }
        [System.IO.File]::WriteAllText($skipLog, (($skipObj | ConvertTo-Json) -replace "`r`n", "`n"), (New-Object System.Text.UTF8Encoding($false)))
    } catch { }
    exit 0
}
Acquire-ShadowLock

# load or init shadow state
$shadow = @{}
if (Test-Path $StateFile) {
    try {
        $loaded = Get-Content $StateFile -Raw -Encoding UTF8 | ConvertFrom-Json
        foreach ($prop in $loaded.PSObject.Properties) { $shadow[$prop.Name] = $prop.Value }
    } catch { $shadow = @{} }
}
if (-not $shadow.ContainsKey("stages")) { $shadow.stages = @() }

try {
    Write-Checkpoint -State $shadow -Stage "start" -Status "running" -Detail "pid=$PID mode=$Mode force=$($Force.IsPresent)"

    # ==================== STAGE 1: pre-check (shadow targets only) ====================
    Write-Stage "Stage 1: Pre-check (shadow targets)"
    New-Item -ItemType Directory -Path $TargetRoot -Force | Out-Null
    foreach ($d in @("$TargetRoot\vault", "$TargetRoot\db_dumps", "$TargetRoot\offrepo", "$TargetRoot\gmirror", "$TargetRoot\bundles")) {
        New-Item -ItemType Directory -Path $d -Force | Out-Null
    }
    $robocopy = Get-Command robocopy -ErrorAction SilentlyContinue
    if (-not $robocopy) { Write-Err "robocopy not found"; exit 1 }
    Write-OK "robocopy found; targets under $TargetRoot (zero production paths)"
    if ($StageDelaySeconds -gt 0) { Start-Sleep -Seconds $StageDelaySeconds }

    # ==================== STAGE 2: DB dump (shadow-scaled: config snapshot) ====================
    # Production dumps (pg_dump/sqlite) are Owner-data; shadow proves the checkpoint +
    # cadence mechanics with a scaled artifact: a robocopy snapshot of small config dirs.
    $dbDumpFresh = (Test-StageFresh -State $shadow -Stage "db_dump" -CadenceHours 8) -and (-not $Force)
    if ($Mode -eq "ch") {
        Write-Stage "Mode=ch, skipping db_dump"
    } elseif ($dbDumpFresh) {
        Write-Stage "db_dump checkpoint fresh (within 8h) -> checkpoint_skip (T1 resume, no re-burn)"
        Write-Checkpoint -State $shadow -Stage "db_dump" -Status "stage_skip" -Detail "checkpoint fresh, resume path"
    } else {
        Write-Stage "Stage 2: DB dump (shadow-scaled: config snapshot)"
        $dumpDir = "$TargetRoot\db_dumps\$($RunAt.ToString('yyyyMMdd'))"
        New-Item -ItemType Directory -Path $dumpDir -Force | Out-Null
        & robocopy "$ProjectRoot\scripts\backup" $dumpDir "/E" "/XJ" "/R:0" "/W:0" "/NFL" "/NDL" "/NP" 2>&1 | Out-Null
        $rc = $LASTEXITCODE
        if ($rc -ge 8) {
            Write-Checkpoint -State $shadow -Stage "db_dump" -Status "failed" -Detail "robocopy exit $rc"
            throw "shadow db_dump failed (robocopy exit $rc)"
        }
        $sha = Get-TreeFingerprint -Root $dumpDir
        Write-Checkpoint -State $shadow -Stage "db_dump" -Status "stage_ok" -ArtifactSha $sha -Detail "dumpdir=$dumpDir"
        # legacy-shaped mirror keys so the shadow reconciler reads production shape
        $shadow.last_backup_time = (Get-Date).ToString("o")
        $shadow.last_ch_backup_status = $shadow.last_ch_backup_status
        if ($StageDelaySeconds -gt 0) { Start-Sleep -Seconds $StageDelaySeconds }
    }

    # ==================== CH stage: PROBE-ONLY (unless -AllowChWrite) ====================
    $chEnvFile = "$ProjectRoot\config\.env.clickhouse"
    if (Test-Path $chEnvFile) {
        foreach ($line in (Get-Content $chEnvFile -Encoding UTF8)) {
            if ($line -match '^CLICKHOUSE_HOST=(.+)$')      { $chHttpHost = $matches[1].Trim() }
            if ($line -match '^CLICKHOUSE_HTTP_PORT=(.+)$') { $chHttpPort = [int]$matches[1].Trim() }
        }
    }
    $chBaseUrl = "http://${chHttpHost}:${chHttpPort}/"
    if ($Mode -eq "code") {
        Write-Stage "Mode=code, CH stage skipped"
    } else {
        $chFresh = (Test-StageFresh -State $shadow -Stage "ch" -CadenceHours 24) -and (-not $Force)
        if ($chFresh) {
            Write-Stage "ch checkpoint fresh (within 24h) -> checkpoint_skip (T1: killed run does not re-burn CH)"
            Write-Checkpoint -State $shadow -Stage "ch" -Status "stage_skip" -Detail "checkpoint fresh, resume path"
        } else {
            Write-Stage "CH stage (shadow=probe-only, read-only SELECT)"
            $chAlive = $false
            try { curl.exe -s --max-time 5 $chBaseUrl --data-binary "SELECT 1" | Out-Null; $chAlive = ($LASTEXITCODE -eq 0) } catch { $chAlive = $false }
            if (-not $chAlive) {
                Write-Checkpoint -State $shadow -Stage "ch" -Status "stage_skip" -Detail "probe: service down (not failure-grade in shadow)"
            } else {
                # read-only evidence: latest BACKUP_CREATED from system.backups
                $probeJson = curl.exe -s --max-time 15 $chBaseUrl --data-binary "SELECT id, status, substring(error,1,200) as error, end_time, total_size FROM system.backups WHERE status='BACKUP_CREATED' ORDER BY end_time DESC LIMIT 1 FORMAT JSON"
                $probeOk = $false; $probeDetail = "no BACKUP_CREATED row"
                try {
                    $probe = $probeJson | ConvertFrom-Json
                    if ($probe.data -and $probe.data.Count -gt 0) {
                        $row = $probe.data[0]
                        $probeOk = $true
                        $probeDetail = "id=$($row.id) end_time=$($row.end_time) size=$($row.total_size)"
                    }
                } catch { $probeDetail = "probe parse error" }
                if ($AllowChWrite) {
                    Write-Warn "-AllowChWrite is a promotion-rehearsal switch; real BACKUP firing is NOT implemented in shadow v1 (by design, G:/F: red line)"
                }
                if ($probeOk) {
                    $sha = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($probeDetail))) -replace "-", ""
                    Write-Checkpoint -State $shadow -Stage "ch" -Status "stage_ok" -ArtifactSha ($sha.ToLower()) -Detail "probe ok: $probeDetail"
                    $shadow.last_ch_backup_time = (Get-Date).ToString("o")
                    $shadow.last_ch_backup_status = "ok"
                } else {
                    # no fresh CH evidence on the server: shadow records skip, NOT ok -
                    # cadence must not advance on missing evidence (INV-11 discipline)
                    Write-Checkpoint -State $shadow -Stage "ch" -Status "stage_skip" -Detail "probe: $probeDetail (cadence NOT advanced)"
                }
            }
            if ($StageDelaySeconds -gt 0) { Start-Sleep -Seconds $StageDelaySeconds }
        }
    }

    # ==================== STAGE 3: versioned vault (real diff/hardlink logic, scaled) ====================
    if ($Mode -eq "ch") {
        Write-Stage "Mode=ch, skipping vault"
    } else {
        $vaultFresh = (Test-StageFresh -State $shadow -Stage "vault" -CadenceHours 8) -and (-not $Force)
        if ($vaultFresh) {
            Write-Stage "vault checkpoint fresh -> checkpoint_skip (T1 resume)"
            Write-Checkpoint -State $shadow -Stage "vault" -Status "stage_skip" -Detail "checkpoint fresh, resume path"
        } else {
            Write-Stage "Stage 3: Code vault (versioned daily snapshot, shadow source=$SourceRoot)"
            $today = $RunAt.ToString("yyyyMMdd")
            $dayTarget = "$TargetRoot\vault\$today"
            New-Item -ItemType Directory -Path $dayTarget -Force | Out-Null
            & robocopy $SourceRoot $dayTarget "/E" "/XJ" "/R:1" "/W:1" "/MT:4" "/NFL" "/NDL" "/NP" 2>&1 | Out-Null
            $rcCode = $LASTEXITCODE
            if ($rcCode -ge 8) {
                Write-Checkpoint -State $shadow -Stage "vault" -Status "failed" -Detail "robocopy exit $rcCode"
            } else {
                $sha = Get-TreeFingerprint -Root $dayTarget
                Write-Checkpoint -State $shadow -Stage "vault" -Status "stage_ok" -ArtifactSha $sha -Detail "day_target=$dayTarget"
                $shadow.last_backup_time = (Get-Date).ToString("o")
            }
            if ($StageDelaySeconds -gt 0) { Start-Sleep -Seconds $StageDelaySeconds }
        }
    }

    # ==================== STAGE 3b: git bundle (real bundle, shadow home) ====================
    if ($Mode -eq "ch" -or -not $IncludeBundle) {
        Write-Stage "Stage 3b: git bundle skipped (mode/light drill)"
        Write-Checkpoint -State $shadow -Stage "git_bundle" -Status "stage_skip" -Detail "mode or drill shed"
    } else {
        $bundleFresh = (Test-StageFresh -State $shadow -Stage "git_bundle" -CadenceHours 24) -and (-not $Force)
        if ($bundleFresh) {
            Write-Stage "git_bundle checkpoint fresh -> checkpoint_skip"
            Write-Checkpoint -State $shadow -Stage "git_bundle" -Status "stage_skip" -Detail "checkpoint fresh, resume path"
        } else {
            Write-Stage "Stage 3b: Git bundle refresh (shadow home)"
            $bundleDir = "$TargetRoot\bundles"
            $latestBundle = Get-ChildItem "$bundleDir\*.bundle" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            $bundleAgeDays = if ($latestBundle) { [math]::Round(((Get-Date) - $latestBundle.LastWriteTime).TotalDays, 2) } else { 999 }
            $bundleCount = @(Get-ChildItem "$bundleDir\*.bundle" -File -ErrorAction SilentlyContinue).Count
            $bundleTarget = Join-Path $bundleDir ("zephyralpha_full_{0}.bundle" -f $RunAt.ToString("yyyyMMdd"))
            if ($bundleAgeDays -lt 7 -and $bundleCount -ge 2) {
                Write-OK ("bundle fresh ({0}d, {1} on hand) -> skip" -f $bundleAgeDays, $bundleCount)
                Write-Checkpoint -State $shadow -Stage "git_bundle" -Status "stage_skip" -Detail "7d cadence not due"
            } else {
                & git -c pack.windowMemory=256m -c pack.threads=2 bundle create $bundleTarget --all 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0 -and (Test-Path $bundleTarget)) {
                    & git bundle verify $bundleTarget 2>&1 | Out-Null
                    if ($LASTEXITCODE -eq 0) {
                        $old = @(Get-ChildItem "$bundleDir\*.bundle" -File | Sort-Object LastWriteTime -Descending | Select-Object -Skip 2)
                        foreach ($b in $old) { Remove-Item $b.FullName -Force -ErrorAction SilentlyContinue }
                        $sha = (Get-FileHash $bundleTarget -Algorithm SHA256).Hash.ToLower()
                        Write-Checkpoint -State $shadow -Stage "git_bundle" -Status "stage_ok" -ArtifactSha $sha -Detail "bundle=$bundleTarget rotated=$($old.Count)"
                    } else {
                        Write-Warn "bundle verify failed - removing suspect file"
                        Remove-Item $bundleTarget -Force -ErrorAction SilentlyContinue
                        Write-Checkpoint -State $shadow -Stage "git_bundle" -Status "failed" -Detail "verify"
                    }
                } else {
                    Write-Checkpoint -State $shadow -Stage "git_bundle" -Status "failed" -Detail "create exit $LASTEXITCODE"
                }
            }
            if ($StageDelaySeconds -gt 0) { Start-Sleep -Seconds $StageDelaySeconds }
        }
    }

    # ==================== STAGE 3c/3d: mirrors (guarded probe + additive sync, tiny trees) ====================
    if ($Mode -eq "ch" -or -not $IncludeMirrors) {
        Write-Stage "Stage 3c/3d: mirrors skipped (mode/light drill)"
        Write-Checkpoint -State $shadow -Stage "offrepo" -Status "stage_skip" -Detail "mode or drill shed"
        Write-Checkpoint -State $shadow -Stage "g_mirror" -Status "stage_skip" -Detail "mode or drill shed"
    } else {
        foreach ($mirror in @(@{ id = "offrepo"; src = "$ProjectRoot\config"; tgt = "$TargetRoot\offrepo\config" },
                              @{ id = "g_mirror"; src = "$ProjectRoot\logs"; tgt = "$TargetRoot\gmirror\logs" })) {
            $stageName = $mirror.id
            $mFresh = (Test-StageFresh -State $shadow -Stage $stageName -CadenceHours 8) -and (-not $Force)
            if ($mFresh) {
                Write-Stage "$stageName checkpoint fresh -> checkpoint_skip"
                Write-Checkpoint -State $shadow -Stage $stageName -Status "stage_skip" -Detail "checkpoint fresh, resume path"
                continue
            }
            Write-Stage ("Stage (mirror {0}): guarded probe + additive sync" -f $stageName)
            New-Item -ItemType Directory -Path $mirror.tgt -Force | Out-Null
            # guarded-mirror discipline: /L probe counts would-purge; over cap => additive /E
            $probeRaw = & robocopy $mirror.src $mirror.tgt "/MIR" "/L" "/XJ" "/R:0" "/W:0" "/NFL" "/NDL" "/NP" 2>&1
            $probeExit = [int]$LASTEXITCODE
            $purge = 0
            if ($probeExit -lt 8) { foreach ($raw in ($probeRaw | Out-String) -split "`n") { if ($raw.Trim().StartsWith("*")) { $purge += 1 } } }
            $mode2 = "mirror"; if ($purge -gt 200) { $mode2 = "additive_over_cap" }
            $sw = @("/XJ", "/R:1", "/W:1", "/MT:4", "/NFL", "/NDL", "/NP")
            if ($mode2 -eq "mirror") { $sw = @("/MIR") + $sw } else { $sw = @("/E") + $sw }
            & robocopy $mirror.src $mirror.tgt @sw 2>&1 | Out-Null
            $rcM = [int]$LASTEXITCODE
            if ($rcM -ge 8) {
                Write-Checkpoint -State $shadow -Stage $stageName -Status "failed" -Detail "robocopy exit $rcM"
            } else {
                $sha = Get-TreeFingerprint -Root $mirror.tgt
                Write-Checkpoint -State $shadow -Stage $stageName -Status "stage_ok" -ArtifactSha $sha -Detail "mode=$mode2 would_purge=$purge"
            }
        }
        if ($StageDelaySeconds -gt 0) { Start-Sleep -Seconds $StageDelaySeconds }
    }

    # ==================== STAGE 4: report + finished checkpoint ====================
    Write-Stage "Stage 4: Report"
    $duration = (Get-Date) - $backupStartTime
    $failedStages = @()
    foreach ($e in @($shadow.stages)) {
        if ($e.status -eq "failed" -and $e.ts -ge $backupStartTime.ToString("o")) { $failedStages += $e.stage }
    }
    $overall = "ok"; if ($failedStages.Count -gt 0) { $overall = "failed" }
    $report = [ordered]@{
        timestamp = (Get-Date).ToString("o")
        duration_seconds = [math]::Round($duration.TotalSeconds, 1)
        mode = $Mode; force_mode = $Force.IsPresent
        run_id = $RunId; overall = $overall
        failed_stages = $failedStages
        stage_timeline = $script:StageLog
        checkpoints = $shadow.stages
    }
    $reportJson = ($report | ConvertTo-Json -Depth 6) -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($LogFile, $reportJson, (New-Object System.Text.UTF8Encoding($false)))
    Write-OK "Report saved: $LogFile"

    # legacy-shaped keys on shadow state (reconciler-shadow reads production shape)
    $shadow.last_backup_status = $overall
    $shadow.last_attempt_status = $overall
    $shadow.last_attempt_time = (Get-Date).ToString("o")
    if ($overall -eq "ok") { $shadow.last_success_time = (Get-Date).ToString("o"); $shadow.last_success_status = "ok" }
    Write-Checkpoint -State $shadow -Stage "report" -Status "finished" -ArtifactSha "" -Detail "report=$LogFile overall=$overall"

    Write-Host ""
    Write-OK "SHADOW backup completed in $([math]::Round($duration.TotalSeconds,1))s (overall=$overall)"
} finally {
    Release-ShadowLock
}
