# ZephyrAlpha_WeeklyRest guard - Sunday rest window with skip fuse.
# Schedule: weekly SUN 05:00 (after tilib 02:30 batch ends ~04:30, before Monday).
# Approved by Owner 2026-09-17 (full-consent batch, session st-autolnk-20260917).
# Skip fuse: create D:\ZephyrAlpha\.runtime\weekly_rest_skip.flag to skip this week
#   (overnight construction crews / Owner work sessions write this flag).
# Abort within 120s grace: run  shutdown /a
# Log: D:\ZephyrAlpha\.runtime\logs\weekly_rest.log (append-only)

$ErrorActionPreference = "Continue"
$flag = "D:\ZephyrAlpha\.runtime\weekly_rest_skip.flag"
$log  = "D:\ZephyrAlpha\.runtime\logs\weekly_rest.log"
$ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

if (Test-Path $flag) {
    "$ts SKIP (fuse flag present) - no shutdown this week" | Out-File -FilePath $log -Append -Encoding utf8
    Remove-Item $flag -Force
    exit 0
}

"$ts SHUTDOWN issued (weekly rest, 120s grace; abort = shutdown /a)" | Out-File -FilePath $log -Append -Encoding utf8
shutdown.exe /s /t 120 /c "ZephyrAlpha weekly rest window (Owner-approved 2026-09-17). Abort: shutdown /a"
