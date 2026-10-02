# [BLUEPRINT] MOD-SCRIPT-run_factory_lane_c | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.run_factory_lane_c
# [DOMAIN] D_BACKTEST
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-SCRIPT-run_factory_lane_c | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# run_factory_lane_c.ps1 - One-shot wrapper for FAC-E1C formula mining (gplearn track).
# Fired by Task Scheduler ZephyrAlpha_FactoryLaneC (weekdays Mon-Fri 20:00, Owner plan-1
#   2026-10-01; was weekly Sat 10:00) or manually via schtasks /run /tn ZephyrAlpha_FactoryLaneC
# Discipline lives INSIDE the job: lane_c_formula_miner consults the E0 compute gate
# (trade_calendar, heavy only after close / non-trading days) and whitelist status.
# Log append-only: .runtime/logs/factory_lane_c.log (map FAC-E0 store_refs convention).
# rc discipline (2026-10-01 E2 repair, mirrors run_c4_exam.ps1): every segment's exit
# code is captured and checked; a failure logs "==== <seg> FAILED rc=N ====", raises an
# Alerter ERROR, short-circuits the remaining segments and the wrapper exits with that
# rc. (09-26 the mine segment crashed but the wrapper still exited 0 - swallowed error.)

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "factory_lane_c.log"

"==== FAC-E1C mine fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') ====" | Out-File -FilePath $log -Append -Encoding utf8

# Production defaults live in config/factor_mining_whitelist.yaml (pop 1000 x 50, seed 42).
# PS5.1 landmine fix (2026-09-15, MOD-SCRIPT-run_factory_lane_c): `$ErrorActionPreference
# = "Stop"` + `python ... 2>&1 | Out-File` turns ANY stderr line into an ErrorRecord
# that kills the script (09-15 15:35 first run died after the fired line, LastResult=1).
# cmd shell redirection keeps stderr as raw bytes into the log - no ErrorRecord.
cmd.exe /c "python scripts\backtest\lane_c_formula_miner.py mine --top 10 >> $log 2>&1"
$mineExit = $LASTEXITCODE
"==== mine exit code $mineExit ====" | Out-File -FilePath $log -Append -Encoding utf8
if ($mineExit -ne 0) {
  "==== mine FAILED rc=$mineExit - intake/construct/translate SKIPPED (short circuit) ====" | Out-File -FilePath $log -Append -Encoding utf8
  cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('factory_lane_c', 'mine FAILED rc=$mineExit (intake/construct/translate skipped)', 'ERROR')"" >> $log 2>&1"
  exit $mineExit
}

# Full supply chain (Owner 2026-09-15 full-automation mandate): intake all lanes ->
# E2 precheck all four -> E2->E3 auto-construct -> C3 translation (formula subset).
cmd.exe /c "python scripts\backtest\factory_intake_pipeline.py run --with-lane-b --limit-precheck 15 >> $log 2>&1"
$intakeExit = $LASTEXITCODE
"==== intake exit code $intakeExit ====" | Out-File -FilePath $log -Append -Encoding utf8
if ($intakeExit -ne 0) {
  "==== intake FAILED rc=$intakeExit - construct/translate SKIPPED (short circuit) ====" | Out-File -FilePath $log -Append -Encoding utf8
  cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('factory_lane_c', 'intake FAILED rc=$intakeExit (construct/translate skipped)', 'ERROR')"" >> $log 2>&1"
  exit $intakeExit
}

cmd.exe /c "python scripts\backtest\factory_intake_pipeline.py construct >> $log 2>&1"
$constructExit = $LASTEXITCODE
"==== construct exit code $constructExit ====" | Out-File -FilePath $log -Append -Encoding utf8
if ($constructExit -ne 0) {
  "==== construct FAILED rc=$constructExit - translate SKIPPED (short circuit) ====" | Out-File -FilePath $log -Append -Encoding utf8
  cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('factory_lane_c', 'construct FAILED rc=$constructExit (translate skipped)', 'ERROR')"" >> $log 2>&1"
  exit $constructExit
}

cmd.exe /c "python scripts\backtest\hypothesis_translator.py translate --seeds 5 >> $log 2>&1"
$translateExit = $LASTEXITCODE
"==== translate exit code $translateExit ====" | Out-File -FilePath $log -Append -Encoding utf8
if ($translateExit -ne 0) {
  "==== translate FAILED rc=$translateExit - E9 all-green heartbeat SKIPPED ====" | Out-File -FilePath $log -Append -Encoding utf8
  cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('factory_lane_c', 'translate FAILED rc=$translateExit', 'ERROR')"" >> $log 2>&1"
  exit $translateExit
}
$finalRc = $translateExit

# E9 monitoring heartbeat (2026-10-01 ops repair): all-green trace via Alerter INFO
# (notify logs only at INFO; the durable record is the log line above + this history).
"==== lane C full chain rc all green (mine/intake/construct/translate) - E9 heartbeat ====" | Out-File -FilePath $log -Append -Encoding utf8
cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('factory_lane_c', 'lane C full chain rc all green', 'INFO')"" >> $log 2>&1"

# Worktree application-system weekly audit (policy parallel_session_coordination v1.1.0 s10).
$count = (git log --format=%B --since="7 days ago" | Select-String "non-worktree").Count
"==== worktree audit: non-worktree commits last 7d = $count ====" | Out-File -FilePath $log -Append -Encoding utf8

# Exit with the pipeline's tracked rc (git above would otherwise overwrite $LASTEXITCODE).
"==== exit code $finalRc ====" | Out-File -FilePath $log -Append -Encoding utf8
exit $finalRc
