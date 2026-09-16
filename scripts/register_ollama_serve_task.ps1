# [BLUEPRINT] MOD-SCRIPT-register_ollama_serve | docs/03_modules/_domain_integration/blueprint.md
# [MODULE] scripts.register_ollama_serve_task
# [DOMAIN] D_INTEGRATION
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_ollama_serve | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_ollama_serve_task.ps1 - Register the ZephyrAlpha_OllamaServe Task Scheduler task.
#
# Why: factory E2 hypothesis precheck (MOD-BT-091) and lane B idea generation (MOD-BT-150)
# depend on a local Ollama server (port 11434). The Ollama Windows installer only registers
# a user-level startup item that dies at logoff (community-documented gap, ollama/ollama#10713:
# no services.msc entry). House pattern (mirrors register_pattern_mining_task.ps1):
# Task Scheduler AtLogOn trigger running "ollama serve" detached.
#
# Idempotency: a second "ollama serve" bind fails on port 11434 and exits immediately,
# so AtLogOn re-fires are harmless (no double-instance, no port squatting).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\register_ollama_serve_task.ps1
# Verify: schtasks /query /tn ZephyrAlpha_OllamaServe /v /fo LIST
# Health: curl http://localhost:11434/api/tags

$ErrorActionPreference = "Stop"

$TaskName = "ZephyrAlpha_OllamaServe"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"
$OllamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"
if (-not (Test-Path $OllamaExe)) {
    $OllamaExe = "C:\Users\fanzi\AppData\Local\Programs\Ollama\ollama.exe"
}
if (-not (Test-Path $OllamaExe)) {
    throw "ollama.exe not found; install Ollama first"
}

# --- Version precondition (machine-checked, 2026-09-16) -------------------
# Root cause of the old manual "upgrade Ollama" to-do: Ollama builds <= 0.32.1 embed a
# llama-server.exe with a deterministic access violation (AV at libllama.dll+0x2a230);
# evidence = docs/_working/forensics/llama_server_crash_forensics_202609.md.
# Registering a keep-alive task for a crash-bearing build only feeds the crash-respawn
# loop, so registration refuses. Floor must equal CRASH_BEARING_CEILING in
# scripts/ops/ollama_version_guard.py -- the equality is pinned by
# tests/ops/test_ollama_version_guard.py (drift shows up as a failing test, never as a
# silent divergence between the two files).
$MinOllamaVersion = "0.32.1"
$versionText = (& $OllamaExe --version 2>&1 | Out-String)
$versionMatch = [regex]::Match($versionText, "(\d+)\.(\d+)\.(\d+)")
if (-not $versionMatch.Success) {
    Write-Warning ("ollama version unparseable from output '" + $versionText.Trim() + "'; " +
        "proceeding, but run: python scripts/ops/ollama_version_guard.py --check")
} else {
    $installed = [version]$versionMatch.Value
    $floor = [version]$MinOllamaVersion
    if ($installed -le $floor) {
        throw ("Ollama $installed <= crash-bearing ceiling $MinOllamaVersion (known llama-server " +
            "access violation). Upgrade first with one command (software install = Owner gate): " +
            "python scripts/ops/ollama_version_guard.py --upgrade --installer-path <exe> " +
            "--expected-sha256 <hex> ; verify with --check")
    }
    Write-Output "OK ollama version $installed (above crash-bearing ceiling $MinOllamaVersion)"
}
# --- end version precondition --------------------------------------------

$Action = New-ScheduledTaskAction -Execute $OllamaExe -Argument "serve"
$Trigger = New-ScheduledTaskTrigger -AtLogOn -User $CurrentUser
$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries
# ExecutionTimeLimit zero = no limit (a server must not be killed by the scheduler).
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
    -Settings $Settings -Principal $Principal -Force | Out-Null
Write-Output "OK registered $TaskName (AtLogOn, no time limit, port-conflict self-exit = idempotent)"
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status"
