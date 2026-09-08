# run_ttl_rejudge_daily.ps1 - hidden-launch target for scheduled task ZephyrAlpha_TTLRejudgeDaily
# 2026-09-08 no-flash sweep (#ARCH-BOOT-WINDOW-FLASH): the old task action was an inline
# `powershell.exe -Command <blob>` which cannot be passed through launch_hidden.vbs (it
# requires a -File ps1 path). Behavior below is identical to the previous inline command.
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
Set-Location D:\ZephyrAlpha
New-Item -ItemType Directory -Path logs -Force | Out-Null
Add-Content logs\ttl_rejudge_daily.log ('=== ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ===')
& 'C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe' scripts\governance\d3_metadata\backfill_ttl_metadata.py --rejudge --check docs/ architecture_model/ *>> logs\ttl_rejudge_daily.log
exit $LASTEXITCODE
