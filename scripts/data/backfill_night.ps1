# tilib nightly indicator backfill (2026-09-22 tracked runner, ruling #399)
# shard runner = per-shard subprocess memory isolation (Code 241 cure)
# pure ASCII required (PowerShell 5.1 GBK decode trap)
$ErrorActionPreference = "Continue"
Set-Location D:\ZephyrAlpha
$env:PATH = "C:\Users\fanzi\AppData\Local\Programs\Python\Python312;C:\Users\fanzi\AppData\Local\Programs\Python\Python312\Scripts;" + $env:PATH
# Shard-state wipe REMOVED 2026-10-09 (st-dexp-20261009, dexp campaign root cause R1;
# zongtongchou ruling, P2 first cut). Wiping the whole state dir every night was the
# crude way to force a re-pass, and it is what made every nightly pass re-insert the
# entire daily history: measured 11,227,985 rows inserted by one pass on 2026-10-09
# (48.6% of the daily partition, unmerged versions per key up to 7).
# The runner now decides staleness itself: shard_already_done() in
# scripts\data\tilib_dwm_shard_runner.py skips a shard only when its recorded
# finished_at is the current day and exit was 0, so a same-night restart re-inserts
# nothing while the next trading day still gets a full recompute.
# Rollback = git revert this commit (single hunk, both files land together).
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
