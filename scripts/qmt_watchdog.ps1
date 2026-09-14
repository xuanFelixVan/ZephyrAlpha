# [BLUEPRINT] MOD-SCRIPT-run_post_settlement | scripts/run_post_settlement.py
# [MODULE] scripts.qmt_watchdog
# [DOMAIN] D_TRADING
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-qmt_watchdog | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# qmt_watchdog.ps1 - One-shot QMT terminal watchdog (launched by Task Scheduler)
#
# Background (Owner 2026-09-15 blanket automation directive, opens the B1 window):
#   B1 required the Owner to manually start the QMT terminal every trading day.
#   This watchdog removes the "is it running?" leg: at trigger time it checks for
#   XtItClient.exe and relaunches it when absent.
#
# Boundary (honest scope note):
#   Interactive broker login (credentials + possible device captcha) stays OUT of
#   scope by security ruling: no stored passwords, no UI automation of credential
#   entry. If the terminal expired its session, it sits at its login window - the
#   remaining human step is the login click, typically rare (session expiry), not
#   a daily action.
#
# Path handling: the terminal install path contains non-ASCII characters and this
#   file must stay pure ASCII (PowerShell 5.1 GBK decoding rule). The real path is
#   stored UTF-8 in data\runtime\qmt_terminal_path.txt by the registration step.
#
# Design (stateless one-shot, mirrors the reaper pattern):
#   Task Scheduler "ZephyrAlpha_QMTWatchdog" (daily 08:45 + 12:55, interactive user)
#     -> this script: if process absent AND exe exists -> start it; log one line.
#   No resident process, no loop, no pid lock. Safe to run any number of times.
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\qmt_watchdog.ps1

$ErrorActionPreference = "SilentlyContinue"

$repoRoot = Split-Path -Parent $PSScriptRoot
$logPath = Join-Path $repoRoot "data\runtime\qmt_watchdog.log"
$pathFile = Join-Path $repoRoot "data\runtime\qmt_terminal_path.txt"
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if (-not (Test-Path $pathFile)) {
    Add-Content -Path $logPath -Value "$stamp SKIP path config missing: $pathFile"
    exit 1
}
$qmtExe = (Get-Content -Path $pathFile -Encoding UTF8 | Select-Object -First 1).Trim()

$proc = Get-Process -Name "XtItClient" -ErrorAction SilentlyContinue
if ($proc) {
    Add-Content -Path $logPath -Value "$stamp OK process running (pid=$($proc.Id))"
    exit 0
}
if (Test-Path -LiteralPath $qmtExe) {
    Start-Process -FilePath $qmtExe -WorkingDirectory (Split-Path -Parent $qmtExe)
    Add-Content -Path $logPath -Value "$stamp LAUNCHED (was absent; login window expected)"
    exit 0
}
Add-Content -Path $logPath -Value "$stamp SKIP exe not found: $qmtExe"
exit 1
