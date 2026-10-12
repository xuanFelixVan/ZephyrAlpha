# [BLUEPRINT] MOD-SCRIPT-register_sft_train_window | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] scripts.register_sft_train_window_task
# [DOMAIN] D_ML_TRAIN
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-register_sft_train_window_task | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# register_sft_train_window_task.ps1 - Register the ZephyrAlpha_SftTrainWindow task.
#
# Purpose (work order GPU-03 step 2, Owner order 2026-10-11): reserve a **Sunday daytime**
# window on the gpu_default mutex group for the sentiment SFT full run, so the resource week
# view and the conflict gate can see it and refuse to overlap it with
# manual_kronos_finetune (240min) / manual_convert_gguf (60min) on the same GPU.
#
# Deviation from the order's wording, with reason (declared weekly, not biweekly):
#   the Owner order asked for a biweekly Sunday window. The registry generator reads triggers with
#   _RE_WEEKLY (scripts/governance/generators/generate_resource_profile_registry.py:903), which
#   matches "-Weekly -DaysOfWeek X -At HH:MM" only and knows nothing about WeeksInterval. Registering
#   a biweekly trigger would make the machine-generated registry declare "every Sunday" while the
#   task actually fires every other Sunday = a silent declaration/reality drift, which is the class
#   of defect this shift is supposed to report rather than add to. So the schedule is declared and
#   registered as weekly; the cost is one extra no-op fire per fortnight (the wrapper exits 0 within
#   seconds when the Owner authorization file is absent), and the benefit is declaration==reality.
#
# Architecture:
#   Task Scheduler ZephyrAlpha_SftTrainWindow (weekly Sunday 10:00)
#   -> powershell -File scripts\tasks\run\run_sft_train_task.ps1
#   -> guard wrapper: refuses without the Owner authorization file, then runs
#      scripts\ml\run_sft_train.py (full) and scripts\ml\convert_gguf_ollama.py --dry-run
#
# Key design:
# - The timer reserves the window; it does NOT press the training button. Real QLoRA training is
#   a B-007 human-gate item (sentiment_sft_entry INVARIANTS: AI must not self-trigger real LLM
#   training), and scripts/ml/run_sft_train.py bypasses that entry, so the button lives in
#   run_sft_train_task.ps1 (data/runtime/sft_train_authorization.txt).
# - 10:00 start + 5h limit = 10:00-15:00, clear of the Sunday 05:00 machine_blackout weekly rest
#   and clear of the 01:00-04:00 ClickHouse yield window (the wrapper also re-checks the clock).
# - ExecutionTimeLimit=5h: registry estimate for manual_run_sft_train is 240min, plus 60min plan leg.
# - MultipleInstances=IgnoreNew: a second fire while the 4h run is alive must not stack a QLoRA job.
# - Idempotent non-destructive: Set-ScheduledTask in-place update when present (NEVER Unregister+Register).
#
# Usage: powershell -ExecutionPolicy Bypass -File scripts\tasks\register\register_sft_train_window_task.ps1
#        (registers DISABLED by default; add -Enable to arm the calendar)
# Verify: schtasks /query /tn ZephyrAlpha_SftTrainWindow /v /fo LIST
# Then regenerate the resource registry: python scripts\governance\generators\generate_resource_profile_registry.py
#
# Two independent locks, both must be true before a training run happens:
# 1) the calendar is armed (this file with -Enable, or schtasks /change /enable);
# 2) data/runtime/sft_train_authorization.txt contains RUN_SFT_TRAIN_FULL_APPROVED (Owner's button;
#    the run script consumes it once and renames it .consumed).
# Why the calendar is disabled by default: measured on the live registry face (see
# docs/_working/gpuwo_campaign/11_resource_declaration_and_overlap_precheck.yaml), this sch_* entity
# lands as resource_class=light / pool=default / exclusive_group=[] because the generator has no
# per-schedule GPU class channel, and Sunday 10:00+300min sits inside sch_f06_grid's
# Saturday 23:00+1440min window. The conflict gate would call that "zero red" only because it is blind.

param([switch]$Enable)

$ErrorActionPreference = "Stop"

$RepoRoot = "D:\ZephyrAlpha"
$TaskName = "ZephyrAlpha_SftTrainWindow"
$CurrentUser = "$env:USERDOMAIN\$env:USERNAME"

$Action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File $RepoRoot\scripts\tasks\run\run_sft_train_task.ps1"

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "10:00"
# Deliberately no WeeksInterval here: see the deviation note above (generator cannot see it).

$Settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 5) `
    -MultipleInstances IgnoreNew -StartWhenAvailable
$Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Principal $Principal | Out-Null
    Write-Output "OK updated $TaskName in place (weekly Sunday 10:00, 5h limit)"
} else {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger `
        -Settings $Settings -Principal $Principal -Force | Out-Null
    Write-Output "OK registered $TaskName (weekly Sunday 10:00, 5h limit)"
}
if ($Enable) {
    Enable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Output "STATE enabled (calendar armed; training still needs data/runtime/sft_train_authorization.txt)"
} else {
    Disable-ScheduledTask -TaskName $TaskName | Out-Null
    Write-Output "STATE disabled (default; arm with -Enable or: schtasks /change /tn $TaskName /enable)"
}
schtasks /query /tn $TaskName /fo LIST | Select-String "TaskName|Status|Next"
