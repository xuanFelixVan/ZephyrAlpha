# tilib nightly indicator backfill (2026-09-22 tracked runner, ruling #399)
# shard runner = per-shard subprocess memory isolation (Code 241 cure)
# pure ASCII required (PowerShell 5.1 GBK decode trap)
$ErrorActionPreference = "Continue"
Set-Location D:\ZephyrAlpha
$env:PATH = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312;C:\Users\fanzi\AppData\Local\Programs\Python\Python312\Scripts;" + $env:PATH
if (Test-Path data\runtime\dwm_shard_state) { Remove-Item -Recurse -Force data\runtime\dwm_shard_state }
python scripts\data\tilib_dwm_shard_runner.py --periods daily 2>&1 | Add-Content data\runtime\tilib_nightly_run.log
python .runtime\tmp\tilib-probe\night_probe.py 2>&1 | Out-File .runtime\tmp\tilib-probe\night_probe_result.txt -Encoding utf8
