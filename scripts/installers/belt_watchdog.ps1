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
        $age = [DateTimeOffset]::UtcNow.UtcTicks / 10000000.0 - [double]$j.wall_ts
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
