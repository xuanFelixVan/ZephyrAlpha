# tilib nightly indicator backfill (2026-09-22 tracked runner, ruling #399)
# shard runner = per-shard subprocess memory isolation (Code 241 cure)
# pure ASCII required (PowerShell 5.1 GBK decode trap)
$ErrorActionPreference = "Continue"
Set-Location D:\ZephyrAlpha
$env:PATH = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312;C:\Users\fanzi\AppData\Local\Programs\Python\Python312\Scripts;" + $env:PATH
if (Test-Path data\runtime\dwm_shard_state) { Remove-Item -Recurse -Force data\runtime\dwm_shard_state }
python scripts\data\tilib_dwm_shard_runner.py --periods daily 2>&1 | Add-Content data\runtime\tilib_nightly_run.log
# night_probe line removed 2026-09-25 (st-commitspeed-tbl-20260924, M5 mining 04 S2):
# it referenced .runtime/tmp/tilib-probe/night_probe.py, wiped by tmp hygiene; b10
# report 2026-09-22 pre-authorized deleting the line. A surviving untracked copy of
# the probe sits at scripts/data/night_probe.py - reviving it as a tracked asset is
# the data lane's call (04 S2 fix ownership), not this lane's. .runtime/tmp
# references stay banned in persistent chains.
# Propagate the runner exit code (st-commitspeed-tbl-20260924, 04 S2): without an
# explicit exit, powershell -File always returns 0 and a dead backfill is invisible
# in LastTaskResult - the exact silent-failure disease this case book documents.
exit $LASTEXITCODE
