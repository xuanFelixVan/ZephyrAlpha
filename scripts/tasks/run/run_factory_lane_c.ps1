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
#   (trade_calendar, heavy only after close / non-trading days) and whitelist status.
# Log append-only: .runtime/logs/factory_lane_c.log (map FAC-E0 store_refs convention).
# rc discipline (2026-10-01 E2 repair, mirrors run_c4_exam.ps1): every segment's exit
#   code is captured and checked; a failure logs "==== <seg> FAILED rc=N ====", raises an
#   Alerter ERROR, short-circuits the remaining segments and the wrapper exits with that
#   rc. (09-26 the mine segment crashed but the wrapper still exited 0 - swallowed error.)
#
# 2026-10-12 fake-green repair, two parts (Owner order 2026-10-12 broadened this shift's scope
# to exactly these two defects; st-gpuwo-20261011). Both are measured facts, not design guesses.
#
# (1) Ollama can no longer masquerade as a green run. Measured on the night 2026-10-08: EVERY
#     candidate in the translate leg carried refusal_reason=llm_error:ConnectionError and
#     exam_files=[], yet hypothesis_translator still returned 0, so this wrapper printed
#     "lane C full chain rc all green" and exited 0 - monitoring saw "chain green",
#     reality was "translation leg produced nothing". Now: a health probe (/api/tags) runs before
#     any work; if it fails we kick the standing ZephyrAlpha_OllamaServe task once and re-probe;
#     if it still fails we SKIP translate and exit with sentinel rc=90 (never green).
#     Even when Ollama answers, if translate prints "translated": 0 while "negative" > 0 the run
#     is judged failed with rc=91 - a zero-output exit code 0 is not a success.
#
# (2) A killed run can no longer pass silently. Measured on 2026-10-09: after the fired banner the
#     log held nothing but 150 spearmanr warning lines, not one of the four segment-completion
#     banners was written, and the task's own 4h ExecutionTimeLimit cut it at 00:00; LastTaskResult
#     stayed non-terminal and the intake face gained 0 rows for two nights with nobody told.
#     Now: each start appends a start record to .runtime/logs/factory_lane_c.run_state and every
#     terminal path appends a matching end record. On the NEXT fire, an unpaired start is surfaced
#     as orphan_detected plus an Alerter ERROR - a run that was killed cannot write its own
#     epitaph, so the next shift digs it up instead of counting it as having run.
#
# Sentinel rc values owned by this wrapper (resource/alert side should read them this way):
#   90 = translate SKIPPED because Ollama is unreachable (infrastructure failure, not strategy)
#   91 = translate exited 0 but produced zero usable rows (the fake-green shape)
# Every other rc is the python segment's own exit code; no judgement threshold was changed.

$ErrorActionPreference = "Stop"
$RepoRoot = "D:\ZephyrAlpha"
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;$env:LOCALAPPDATA\Programs\Python\Python312\Scripts;" + $env:PATH
Set-Location -Path $RepoRoot

$logDir = Join-Path $RepoRoot ".runtime\logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$log = Join-Path $logDir "factory_lane_c.log"
$runState = Join-Path $logDir "factory_lane_c.run_state"

function Write-Log([string]$Line) {
    $Line | Out-File -FilePath $log -Append -Encoding utf8
}

function Write-State([string]$Line) {
    $Line | Out-File -FilePath $runState -Append -Encoding utf8
}

function Notify([string]$Msg, [string]$Level) {
    cmd.exe /c "python -c ""from zephyr.data.alerter import Alerter; Alerter().notify('factory_lane_c', '$Msg', '$Level')"" >> $log 2>&1"
}

function Complete-Run([int]$Rc, [string]$Note) {
    Write-State ("{""event"":""end"",""run_id"":""" + $script:RunId + """,""rc"":" + $Rc + ",""note"":""" + $Note + """}")
    Write-Log ("==== exit code " + $Rc + " (" + $Note + ") ====")
    exit $Rc
}

$script:RunId = Get-Date -Format "yyyyMMdd-HHmmss"
Write-Log "==== FAC-E1C mine fired at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') run_id=$($script:RunId) ===="

# --- (2) orphan digger: an unpaired start means the previous run was killed and never closed ---
if (Test-Path $runState) {
    $tail = @(Get-Content -Path $runState -Tail 200)
    $starts = @($tail | Select-String -Pattern '"event":\s*"start"' -SimpleMatch:$false)
    $ends = @($tail | Select-String -Pattern '"event":\s*"end"' -SimpleMatch:$false)
    if ($starts.Count -gt $ends.Count) {
        $orphanStart = $starts[-1].Line
        Write-State ("{""event"":""orphan_detected"",""run_id"":""" + $script:RunId + """,""orphaned_start_line"":""" + ($orphanStart -replace '"', '') + """}")
        Write-Log "==== ORPHAN RUN DETECTED: previous start has no matching end (killed / never finished) - flagged, not silently counted as a run ===="
        Notify "orphan run detected from run_state (previous run never closed)" "ERROR"
    }
}
Write-State ("{""event"":""start"",""run_id"":""" + $script:RunId + """}")

# --- (1) Ollama health probe (kick the standing service once, then re-probe) ---
$ollamaOk = $false
try {
    Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 | Out-Null
    $ollamaOk = $true
} catch {
    Write-Log "==== preflight: Ollama not responding, trying to kick ZephyrAlpha_OllamaServe ===="
    cmd.exe /c "schtasks /run /tn ZephyrAlpha_OllamaServe >> $log 2>&1"
    Start-Sleep -Seconds 20
    try {
        Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 | Out-Null
        $ollamaOk = $true
        Write-Log "==== preflight: Ollama up after kick ===="
    } catch {
        Write-Log "==== preflight FAILED: Ollama still unreachable - translate leg will be SKIPPED and the run marked failed (rc=90), never green ===="
    }
}

# Production defaults live in config/factor_mining_whitelist.yaml (pop 1000 x 50, seed 42).
# PS5.1 landmine fix (2026-09-15, MOD-SCRIPT-run_factory_lane_c): `$ErrorActionPreference
# = "Stop"` + `python ... 2>&1 | Out-File` turns ANY stderr line into an ErrorRecord
# that kills the script (09-15 15:35 first run died after the fired line, LastResult=1).
# cmd shell redirection keeps stderr as raw bytes into the log - no ErrorRecord.
cmd.exe /c "python scripts\backtest\lane_c_formula_miner.py mine --top 10 >> $log 2>&1"
$mineExit = $LASTEXITCODE
Write-Log "==== mine exit code $mineExit ===="
if ($mineExit -ne 0) {
    Write-Log "==== mine FAILED rc=$mineExit - intake/construct/translate SKIPPED (short circuit) ===="
    Notify "mine FAILED rc=$mineExit (intake/construct/translate skipped)" "ERROR"
    Complete-Run $mineExit "mine failed"
}

# Full supply chain (Owner 2026-09-15 full-automation mandate): intake all lanes ->
# E2 precheck all four -> E2->E3 auto-construct -> C3 translation (formula subset).
cmd.exe /c "python scripts\backtest\factory_intake_pipeline.py run --with-lane-b --limit-precheck 15 >> $log 2>&1"
$intakeExit = $LASTEXITCODE
Write-Log "==== intake exit code $intakeExit ===="
if ($intakeExit -ne 0) {
    Write-Log "==== intake FAILED rc=$intakeExit - construct/translate SKIPPED (short circuit) ===="
    Notify "intake FAILED rc=$intakeExit (construct/translate skipped)" "ERROR"
    Complete-Run $intakeExit "intake failed"
}

cmd.exe /c "python scripts\backtest\factory_intake_pipeline.py construct >> $log 2>&1"
$constructExit = $LASTEXITCODE
Write-Log "==== construct exit code $constructExit ===="
if ($constructExit -ne 0) {
    Write-Log "==== construct FAILED rc=$constructExit - translate SKIPPED (short circuit) ===="
    Notify "construct FAILED rc=$constructExit (translate skipped)" "ERROR"
    Complete-Run $constructExit "construct failed"
}

if (-not $ollamaOk) {
    Write-Log "==== translate SKIPPED rc=90 (Ollama unavailable) - infrastructure failure is NOT a green run ===="
    Notify "translate skipped rc=90 Ollama unavailable (chain not green)" "ERROR"
    Complete-Run 90 "ollama unavailable"
}

# Translate stdout goes to its own file so the outcome can be MEASURED, not just trusted
# from an exit code (10-08 lesson: rc=0 with every candidate refused by ConnectionError).
$trOut = Join-Path $RepoRoot (".runtime\tmp\factory_lane_c_translate_" + $script:RunId + ".json")
$trDir = Split-Path $trOut
if (-not (Test-Path $trDir)) { New-Item -ItemType Directory -Path $trDir | Out-Null }
cmd.exe /c "python scripts\backtest\hypothesis_translator.py translate --seeds 5 > $trOut 2>> $log"
$translateExit = $LASTEXITCODE
Write-Log "==== translate exit code $translateExit ===="
if ($translateExit -ne 0) {
    Write-Log "==== translate FAILED rc=$translateExit - E9 all-green heartbeat SKIPPED ===="
    Notify "translate FAILED rc=$translateExit" "ERROR"
    Complete-Run $translateExit "translate failed"
}

# Zero-output detector: parse the printed record's counters; translated=0 with negatives>0
# means the leg ran and produced nothing usable - that is a failure, not a success.
$translated = -1
$negatives = -1
if (Test-Path $trOut) {
    $trText = Get-Content -Path $trOut -Raw
    $mT = [regex]::Match($trText, '"translated":\s*(\d+)')
    $mN = [regex]::Match($trText, '"negative":\s*(\d+)')
    if ($mT.Success) { $translated = [int]$mT.Groups[1].Value }
    if ($mN.Success) { $negatives = [int]$mN.Groups[1].Value }
    # keep the record in the history log too
    Get-Content -Path $trOut | Out-File -FilePath $log -Append -Encoding utf8
}
Write-Log "==== translate measured output: translated=$translated negative=$negatives ===="
if ($translated -eq 0 -and $negatives -gt 0) {
    Write-Log "==== translate rc=0 but ZERO productive output (all candidates refused) - judged FAILED rc=91, the all-green banner is suppressed ===="
    Notify "translate zero-productive rc=91 (all candidates refused despite exit 0)" "ERROR"
    Complete-Run 91 "translate zero output"
}
if ($translated -lt 0) {
    Write-Log "==== translate stdout unreadable - judged FAILED rc=91 (cannot certify green without a measurement) ===="
    Notify "translate stdout unparsable rc=91 (no measurement, no green)" "ERROR"
    Complete-Run 91 "translate stdout unreadable"
}

$finalRc = $translateExit

# E9 monitoring heartbeat (2026-10-01 ops repair): all-green trace via Alerter INFO
# (notify logs only at INFO; the durable record is the log line above + this history).
Write-Log "==== lane C full chain rc all green (mine/intake/construct/translate measured non-zero output) - E9 heartbeat ===="
Notify "lane C full chain rc all green" "INFO"

# Worktree application-system weekly audit (policy parallel_session_coordination v1.1.0 s10).
$count = (git log --format=%B --since="7 days ago" | Select-String "non-worktree").Count
Write-Log "==== worktree audit: non-worktree commits last 7d = $count ===="

# Exit with the pipeline's tracked rc (git above would otherwise overwrite $LASTEXITCODE).
Complete-Run $finalRc "all green"
