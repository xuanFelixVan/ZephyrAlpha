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
