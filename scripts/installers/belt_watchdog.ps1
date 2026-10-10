# [BLUEPRINT] MOD-INFRA-BELT-WATCHDOG | scripts/installers/belt_watchdog.ps1 | guard
# [DOMAIN] D_INFRA_OPS
# belt daemon watchdog (ZephyrAlpha_BeltDaemon PT1M) - ruling #7 hardening 2026-10-02.
# Stage 1: heartbeat file check (O(1), immune to CIM timeouts under load).
# Stage 2: CIM fallback only when heartbeat is stale/dead (covers heartbeat-writer crash).
# Spawn ONLY when both stages agree the daemon is dead. Prevents the pileup disease
# (CIM empty-return under load caused 6-8 duplicate daemons historically).
# ASCII-only per repo rule (PowerShell 5.1 GBK decode hazard).
# [TTL] permanent
# [A_module] module_id=MOD-SCRIPT-belt-watchdog | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable

$hbeat = 'D:\ZephyrAlpha\.runtime\commit_queue\belt_daemon.heartbeat'
$alive = $false

# Stage 1: heartbeat file (pid alive AND wall_ts fresh < 600s)
try {
    if (Test-Path $hbeat) {
        $raw = Get-Content $hbeat -Raw
        $j = $raw | ConvertFrom-Json
        # FIX 2026-10-10 st-maint1-20261010: clock-unit mismatch. The heartbeat writer
        # stamps wall_ts with unix time.time(); the old expression used
        # [DateTimeOffset]::UtcNow.UtcTicks / 1e7 (.NET epoch seconds since 0001-01-01),
        # so age evaluated to ~6.2e10 s (about 1969 years) and was ALWAYS > 600.
        # Stage 1 therefore always declared the daemon dead and Stage 2 (CIM, which can
        # return empty under load) spawned a duplicate every minute - the pileup disease
        # this file's own header warns about. Measured live: real age 6 s, computed 62135596806 s.
        $age = [DateTimeOffset]::Now.ToUnixTimeSeconds() - [double]$j.wall_ts
        if ($age -lt 600 -and [int]$j.pid -gt 0) {
            $p = Get-Process -Id ([int]$j.pid) -ErrorAction SilentlyContinue
            if ($p -and -not $p.HasExited) { $alive = $true }
        }
    }
} catch { $alive = $false }

# Stage 2: CIM fallback (only when heartbeat said dead/stale)
if (-not $alive) {
    $procs = Get-CimInstance Win32_Process -Filter "Name='pythonw.exe' OR Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'commit_belt_daemon' }
    if ($procs) { $alive = $true }
}

if (-not $alive) {
    Start-Process -FilePath 'C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe' `
        -ArgumentList '-m zephyr.gov_enforcement.rule_bridge.commit_belt_daemon D:\ZephyrAlpha' `
        -WorkingDirectory 'D:\ZephyrAlpha' -NoNewWindow
}
