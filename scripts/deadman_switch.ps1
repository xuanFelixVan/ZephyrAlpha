# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/boot_autostart_architecture.md
# [MODULE] scripts.deadman_switch
# [DOMAIN] D_DATA
# [TTL] permanent
# deadman_switch.ps1 - Dead-man switch: independent heartbeat staleness monitor (#ARCH-BOOT-002 E)
#
# Architecture (stateless one-shot Task Scheduler task, NOT a guard):
# Task Scheduler "ZephyrAlpha_DeadmanSwitch" (AtLogOn + PT5M repeat, interactive user)
# -> this script (one-shot: read heartbeats -> alert if stale -> exit, no while-true)
#
# Independence principle (first-principles, #ARCH-BOOT-002 E):
# This monitor is NOT one of the 3 monitored services. It only READS heartbeat files
# written by others. If all 3 services die, this task still fires (separate Task Scheduler
# task) and alerts. Closes the "total layer failure, nobody knows" loop (08-06/08-07 outage:
# 2-day stall discovered by a human, not the system).
#
# Fail-safe: if this task itself dies, system degrades to pre-E state (no monitoring) -
# not a regression. No infinite regress needed (its failure is fail-safe, not fail-deadly).
#
# Why .ps1 not .py: independence from the Python stack. If the failure is caused by broken
# Python (bad import, venv crash), a .py monitor would also die. .ps1 reads files + sends
# webhook with zero Python dependency.
#
# Alert channels:
# 1. Local alert log: tmp/deadman_switch_alerts.log (always, full audit)
# 2. Feishu webhook: ZEPHYR_FEISHU_WEBHOOK env (push to phone, survives service failure)
# 3. Windows Event Log: Application log (visible in Event Viewer, survives process crash)
# Cooldown: Feishu webhook sent at most every DEADMAN_ALERT_COOLDOWN_MIN (default 30) per
# stale-service-set, prevents spamming phone during a multi-hour outage. Local log + Event
# Log always fire (full audit). Alert latency: check every 5min, alert when stale >10min
# -> worst case 10-15min after service death.
#
# Config (env, optional):
# DEADMAN_STALE_MIN stale threshold minutes (default 10)
# DEADMAN_ALERT_COOLDOWN_MIN webhook cooldown minutes (default 30)
# ZEPHYR_FEISHU_WEBHOOK Feishu bot webhook URL (same as Alerter)
#
# Deploy: registered by scripts/register_guard_tasks.ps1 (4th task ZephyrAlpha_DeadmanSwitch).
# Manual run: powershell -ExecutionPolicy Bypass -File scripts\deadman_switch.ps1

$ErrorActionPreference = "Stop"

# ============== Paths ==============
$RepoRoot = "D:\ZephyrAlpha"
$TmpDir = Join-Path $RepoRoot "tmp"
$AlertLog = Join-Path $TmpDir "deadman_switch_alerts.log"
$StateFile = Join-Path $TmpDir "deadman_switch_state.json"

if (-not (Test-Path $TmpDir)) {
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null
}

# ============== Config ==============
$StaleMin = 10
if ($env:DEADMAN_STALE_MIN -match '^\d+$') { $StaleMin = [int]$env:DEADMAN_STALE_MIN }
$CooldownMin = 30
if ($env:DEADMAN_ALERT_COOLDOWN_MIN -match '^\d+$') { $CooldownMin = [int]$env:DEADMAN_ALERT_COOLDOWN_MIN }

# Heartbeat files to monitor. Extend when adding new permanent services.
$Heartbeats = @(
    @{ Service = "scheduler";       File = Join-Path $TmpDir "scheduler.heartbeat" },
    @{ Service = "tick_subscriber"; File = Join-Path $TmpDir "tick_subscriber.heartbeat" },
    @{ Service = "ch_health_probe"; File = Join-Path $TmpDir "ch_health_probe.heartbeat" }
)

# ============== Logging ==============
function Write-AlertLog {
    param([string]$Message)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$ts $Message" | Out-File -FilePath $AlertLog -Append -Encoding utf8
}

# ============== Check heartbeats ==============
$now = Get-Date
$staleServices = @()

foreach ($hb in $Heartbeats) {
    $path = $hb.File
    if (-not (Test-Path $path)) {
        $staleServices += "$($hb.Service): heartbeat file MISSING (service never started or tmp cleaned)"
        continue
    }
    try {
        $line = (Get-Content $path -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
        if (-not $line) {
            $staleServices += "$($hb.Service): heartbeat file EMPTY"
            continue
        }
        $hbTs = ($line -split '\|')[0]
        $hbDate = [datetime]$hbTs
        $ageMin = ($now - $hbDate).TotalMinutes
        if ($ageMin -gt $StaleMin) {
            $staleServices += "$($hb.Service): stale ${ageMin}min (threshold ${StaleMin}min)"
        }
    } catch {
        $staleServices += "$($hb.Service): heartbeat parse error ($($_.Exception.Message))"
    }
}

# ============== tick_subscriber biz heartbeat (#ARCH-DATA-017 ruling C: live-process-zero-collection) ==============
# Process-level aliveness is covered by tick_subscriber.heartbeat (guard-written) above;
# this section checks BUSINESS aliveness: last_tick_ts stale beyond threshold during
# market hours (weekday 09:30-15:00 and is_trading_day). Off-hours/weekend/holiday are
# skipped (no false alerts); guard side has Test-BizHeartbeatStale restart self-healing.
$BizHb = Join-Path $TmpDir "tick_subscriber_biz.heartbeat"
$BizStaleMin = 10
if ($env:DEADMAN_TICK_BIZ_STALE_MIN -match '^\d+$') { $BizStaleMin = [int]$env:DEADMAN_TICK_BIZ_STALE_MIN }
$isWeekday = $now.DayOfWeek -ne 'Saturday' -and $now.DayOfWeek -ne 'Sunday'
$hmNow = $now.Hour * 60 + $now.Minute
$isMarketHours = $isWeekday -and $hmNow -ge (9 * 60 + 30) -and $hmNow -le (15 * 60)
if ($isMarketHours) {
    if (-not (Test-Path $BizHb)) {
        $staleServices += "tick_subscriber_biz: biz heartbeat MISSING during market hours (subscriber not writing / pre-fix version)"
    } else {
        try {
            $biz = Get-Content $BizHb -Raw -Encoding utf8 | ConvertFrom-Json
            $skipBiz = ($null -ne $biz.is_trading_day -and -not [bool]$biz.is_trading_day)  # holiday (business-side calendar ground truth)
            if (-not $skipBiz) {
 # last_tick_ts null (never received): anchor = max(started_ts, today 09:30) (preopen-start grace)
                $anchor = $null
                if ($biz.last_tick_ts) {
                    $anchor = [datetime]$biz.last_tick_ts
                } else {
                    $open = Get-Date -Hour 9 -Minute 30 -Second 0
                    $anchor = $open
                    if ($biz.started_ts -and ([datetime]$biz.started_ts) -gt $open) { $anchor = [datetime]$biz.started_ts }
                }
                $bizAgeMin = ($now - $anchor).TotalMinutes
                if ($bizAgeMin -gt $BizStaleMin) {
                    $staleServices += "tick_subscriber_biz: no tick for $([int]$bizAgeMin)min in market hours (threshold ${BizStaleMin}min; today_rows=$($biz.today_rows), resub_count=$($biz.resub_count)) -- live-process-zero-collection (#ARCH-DATA-017)"
                }
            }
        } catch {
            $staleServices += "tick_subscriber_biz: biz heartbeat parse error ($($_.Exception.Message))"
        }
    }
}

# ============== live_strategy_biz heartbeat (A6 : 57 GAP-2 , tracker #273) ==============
# Process-level aliveness of the paper-session service is covered by Task Scheduler
# ZephyrAlpha_PaperSession (Daily 09:25, register_paper_session_task.ps1); this section
# checks BUSINESS aliveness: LiveStrategyAdapter biz heartbeat (JSON written by the
# adapter itself every 15s) stale beyond threshold during market hours
# (weekday 09:30-15:00). Off-hours/weekend are skipped (no false alerts); holiday
# gating uses business-side is_trading_day when the heartbeat carries it, else
# weekday+hours only (paper session does not embed a calendar).
$LiveBizHb = Join-Path $TmpDir "live_strategy_biz.heartbeat"
$LiveBizStaleMin = 10
if ($env:DEADMAN_LIVE_STRATEGY_BIZ_STALE_MIN -match '^\d+$') { $LiveBizStaleMin = [int]$env:DEADMAN_LIVE_STRATEGY_BIZ_STALE_MIN }
if ($isMarketHours) {
    if (-not (Test-Path $LiveBizHb)) {
        $staleServices += "live_strategy_biz: biz heartbeat MISSING during market hours (paper session service not running / adapter not writing)"
    } else {
        try {
            $liveBiz = Get-Content $LiveBizHb -Raw -Encoding utf8 | ConvertFrom-Json
            $skipLiveBiz = ($null -ne $liveBiz.is_trading_day -and -not [bool]$liveBiz.is_trading_day)  # holiday (if adapter stamps it)
            if (-not $skipLiveBiz) {
 # anchor = heartbeat ts (adapter writes every 15s; stale = adapter died / hung)
                $liveAnchor = $null
                if ($liveBiz.ts) {
                    $liveAnchor = [datetime]$liveBiz.ts
                } elseif ($liveBiz.started_ts) {
                    $liveAnchor = [datetime]$liveBiz.started_ts
                }
                if ($null -eq $liveAnchor) {
                    $staleServices += "live_strategy_biz: biz heartbeat has no ts/started_ts (malformed)"
                } else {
                    $liveBizAgeMin = ($now - $liveAnchor).TotalMinutes
                    if ($liveBizAgeMin -gt $LiveBizStaleMin) {
                        $staleServices += "live_strategy_biz: biz heartbeat stale $([int]$liveBizAgeMin)min in market hours (threshold ${LiveBizStaleMin}min; running=$($liveBiz.running)) -- restart: schtasks /run /tn ZephyrAlpha_PaperSession"
                    }
                }
            }
        } catch {
            $staleServices += "live_strategy_biz: biz heartbeat parse error ($($_.Exception.Message))"
        }
    }
}

# All fresh -> exit silently
if ($staleServices.Count -eq 0) { exit 0 }

# ============== Alert ==============
$ts = $now.ToString("yyyy-MM-dd HH:mm:ss")
$detail = $staleServices -join "`n"
$staleKey = ($staleServices | ForEach-Object { ($_ -split ':')[0] } | Sort-Object) -join ","
$body = @"
[ZephyrAlpha Dead-man Switch ALERT]
Level: CRITICAL
Time: $ts
Stale services ($($staleServices.Count)/$($Heartbeats.Count)):
$detail

One or more permanent service heartbeats are stale > ${StaleMin} min.
Possible total-layer failure (08-06/08-07 outage root cause recurrence).
Check: schtasks /query /tn ZephyrAlpha_DataScheduler /fo LIST
       schtasks /query /tn ZephyrAlpha_TickSubscriber /fo LIST
       schtasks /query /tn ZephyrAlpha_CHHealthProbe /fo LIST
       schtasks /query /tn ZephyrAlpha_PaperSession /fo LIST  (live_strategy_biz 4th channel, DISABLED at registration = expected when not enabled)
Restart: schtasks /run /tn ZephyrAlpha_DataScheduler ; schtasks /run /tn ZephyrAlpha_TickSubscriber ; schtasks /run /tn ZephyrAlpha_CHHealthProbe
         live_strategy_biz stale only: Enable-ScheduledTask ZephyrAlpha_PaperSession ; schtasks /run /tn ZephyrAlpha_PaperSession
"@

# 1. Local alert log (always, full audit - no cooldown)
Write-AlertLog "CRITICAL: $($staleServices.Count) stale service(s). Key=$staleKey"
Write-AlertLog $body

# 2. Windows Event Log (always, visible in Event Viewer)
try {
    $msg = "ZephyrAlpha dead-man switch: $($staleServices.Count) service(s) stale > ${StaleMin}min: $staleKey. Details: $AlertLog"
    Write-EventLog -LogName Application -Source "ZephyrAlpha" -EntryType Error -EventId 9002 -Message $msg -ErrorAction SilentlyContinue
} catch {
 # Event source may not be registered (needs admin one-time: New-EventLog). Silently fall back to log only.
    Write-AlertLog "Windows Event Log write skipped (source not registered): $($_.Exception.Message)"
}

# 3. Feishu webhook (with cooldown per stale-service-set, push to phone)
$webhook = $env:ZEPHYR_FEISHU_WEBHOOK
if (-not $webhook) {
    Write-AlertLog "Feishu webhook not configured (ZEPHYR_FEISHU_WEBHOOK), phone alert skipped. Local log + Event Log only."
    exit 0
}

# Cooldown check: read state, skip webhook if same staleKey alerted within cooldown
$shouldAlert = $true
if (Test-Path $StateFile) {
    try {
        $state = Get-Content $StateFile -Raw -Encoding utf8 | ConvertFrom-Json
        if ($state.stale_key -eq $staleKey) {
            $lastAlert = [datetime]$state.last_alert_ts
            if (($now - $lastAlert).TotalMinutes -lt $CooldownMin) {
                $shouldAlert = $false
                Write-AlertLog "Feishu webhook skipped (cooldown: same staleKey alerted $([int]($now - $lastAlert).TotalMinutes)min ago < ${CooldownMin}min)"
            }
        }
    } catch {
 # State file corrupt -> alert anyway (fail-safe)
        Write-AlertLog "State file parse error, alerting anyway (fail-safe): $($_.Exception.Message)"
    }
}

if ($shouldAlert) {
    try {
        $payload = @{ msg_type = "text"; content = @{ text = $body } } | ConvertTo-Json -Depth 3
        Invoke-RestMethod -Uri $webhook -Method Post -ContentType "application/json; charset=utf-8" -Body $payload -TimeoutSec 5 | Out-Null
        Write-AlertLog "Feishu webhook sent (staleKey=$staleKey)"
    } catch {
        Write-AlertLog "Feishu webhook FAILED: $($_.Exception.Message)"
    }
 # Update state (always, even on send failure - retry cooldown still applies to avoid spam)
    $newState = @{ stale_key = $staleKey; last_alert_ts = $now.ToString("o"); stale_count = $staleServices.Count } | ConvertTo-Json -Depth 2
    $newState | Out-File -FilePath $StateFile -Encoding utf8 -NoNewline
}

exit 0
