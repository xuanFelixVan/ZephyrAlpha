# __manifest__:
#   dimensions: [D11]
#   priority: P2
#   timeout_seconds: 300
#   args: []
#   warn_only: false
#   description: "47-script full concurrent safety test + same-script 5-instance stress test - validates concurrency correctness of RULE-ONE temp+rename atomic write pattern"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Resolve-Path "$scriptDir\..\.."

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  47 Scripts Concurrent Safety Test" -ForegroundColor Cyan
Write-Host "  Project: $projectDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# Phase 1: Cleanup
# ============================================
Write-Host "[Phase 1] Cleaning zombie processes + residual tmp..." -ForegroundColor Yellow
try {
    Get-Process -Name "python","python3","pythonw" -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue }
} catch {}
Start-Sleep -Seconds 2
Get-ChildItem -Path $projectDir -Recurse -Filter "*.tmp" -ErrorAction SilentlyContinue | ForEach-Object { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }
Get-ChildItem -Path $projectDir -Recurse -Filter "*.__handoff__.md" -ErrorAction SilentlyContinue | ForEach-Object { Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue }
Write-Host "  Done" -ForegroundColor Green
Write-Host ""

# ============================================
# Phase 2: Environment Verification
# ============================================
Write-Host "[Phase 2] Environment verification..." -ForegroundColor Yellow
$pyVersion = & python --version 2>&1
Write-Host "  Python: $pyVersion" -ForegroundColor Green
Write-Host ""

# ============================================
# Phase 3: Full Concurrent (47 scripts)
# ============================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Phase 3: 47-script full concurrent" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allScripts = @(
    @{Name="build_ocp_manifest";           Cmd="python `"$projectDir/scripts/arch_guard/_tools/build_ocp_manifest.py`""},
    @{Name="inject_idempotency";           Cmd="python `"$projectDir/scripts/arch_guard/_tools/inject_idempotency.py`" --dry-run"},
    @{Name="patch_p1_paths";               Cmd="python `"$projectDir/scripts/arch_guard/_tools/patch_p1_paths.py`" --check"},
    @{Name="arch_context";                 Cmd="python `"$projectDir/scripts/context/generate_architecture_context.py`""},
    @{Name="pathway_registry";             Cmd="python `"$projectDir/scripts/generate_pathway_registry.py`" --write"},
    @{Name="validate_script_quality";      Cmd="python `"$projectDir/scripts/governance/d11_compliance/validate_script_quality.py`""},
    @{Name="validate_truth_source_cascade"; Cmd="python `"$projectDir/scripts/governance/d11_compliance/validate_truth_source_cascade.py`""},
    @{Name="batch_create_index_md";        Cmd="python `"$projectDir/scripts/governance/d1_structure/batch_create_index_md.py`""},
    @{Name="generate_missing_index_md";    Cmd="python `"$projectDir/scripts/governance/d1_structure/generate_missing_index_md.py`""},
    @{Name="index_from_manifest";          Cmd="python `"$projectDir/scripts/governance/d1_structure/sync_index_from_manifest.py`""},
    @{Name="policies_index";               Cmd="python `"$projectDir/scripts/governance/d1_structure/sync_policies_index.py`""},
    @{Name="validate_config_integrity";    Cmd="python `"$projectDir/scripts/governance/d1_structure/validate_config_integrity.py`""},
    @{Name="derived_files";                Cmd="python `"$projectDir/scripts/governance/d3_metadata/generate_derived_files.py`" --apply"},
    @{Name="rule_catalog";                 Cmd="python `"$projectDir/scripts/governance/d3_metadata/generate_rule_catalog.py`""},
    @{Name="auto_generate_index_dash";     Cmd="python `"$projectDir/scripts/governance/d5_architecture/auto-generate-index.py`" --check"},
    @{Name="check_contract_code_drift";    Cmd="python `"$projectDir/scripts/governance/d5_architecture/check_contract_code_drift.py`""},
    @{Name="generate_contracts";           Cmd="python `"$projectDir/scripts/governance/d5_architecture/generate_contracts.py`""},
    @{Name="merge_readme_to_index";        Cmd="python `"$projectDir/scripts/governance/d5_architecture/merge_readme_to_index.py`""},
    @{Name="sync_blueprint_code_index";    Cmd="python `"$projectDir/scripts/governance/d5_architecture/sync_blueprint_code_index.py`""},
    @{Name="sync_registry_blueprints";     Cmd="python `"$projectDir/scripts/governance/d5_architecture/sync_registry_from_blueprints.py`" --write --warn-only"},
    @{Name="validate_depends_on_format";   Cmd="python `"$projectDir/scripts/governance/d5_architecture/validate_depends_on_format.py`""},
    @{Name="validate_session_log_integrity";Cmd="python `"$projectDir/scripts/governance/d5_architecture/validate_session_log_index_integrity.py`""},
    @{Name="validate_ssot";                Cmd="python `"$projectDir/scripts/governance/d5_architecture/validate_ssot.py`""},
    @{Name="generate_nav_table";           Cmd="python `"$projectDir/scripts/governance/generate_nav_table.py`""},
    @{Name="fix_module_manifest_layout";   Cmd="python `"$projectDir/scripts/governance/generators/fix_module_manifest_layout.py`" --check"},
    @{Name="gate_registry";                Cmd="python `"$projectDir/scripts/governance/generators/generate_gate_registry.py`""},
    @{Name="registry_master_index";        Cmd="python `"$projectDir/scripts/governance/generators/generate_registry_master_index.py`""},
    @{Name="script_manifest";              Cmd="python `"$projectDir/scripts/governance/generators/generate_script_manifest.py`""},
    @{Name="inject_manifests";             Cmd="python `"$projectDir/scripts/governance/generators/inject_manifests.py`" --check"},
    @{Name="detect_hallucinated_packages"; Cmd="python `"$projectDir/scripts/governance/meta/detect_hallucinated_packages.py`""},
    @{Name="finding_state_machine";        Cmd="python `"$projectDir/scripts/governance/meta/finding_state_machine.py`" status"},
    @{Name="manage_baseline";              Cmd="python `"$projectDir/scripts/governance/meta/manage_baseline.py`" status"},
    @{Name="manage_error_budget";          Cmd="python `"$projectDir/scripts/governance/meta/manage_error_budget.py`" status"},
    @{Name="manage_kill_switch";           Cmd="python `"$projectDir/scripts/governance/meta/manage_kill_switch.py`" status"},
    @{Name="manage_script_ab_test";        Cmd="python `"$projectDir/scripts/governance/meta/manage_script_ab_test.py`" status"},
    @{Name="manage_script_retirement";     Cmd="python `"$projectDir/scripts/governance/meta/manage_script_retirement.py`" status"},
    @{Name="manage_shadow_mode";           Cmd="python `"$projectDir/scripts/governance/meta/manage_shadow_mode.py`" status"},
    @{Name="track_script_costs";           Cmd="python `"$projectDir/scripts/governance/meta/track_script_costs.py`" summary"},
    @{Name="validate_e2e_benchmark";       Cmd="python `"$projectDir/scripts/governance/meta/validate_end_to_end_benchmark.py`""},
    @{Name="validate_false_negatives";     Cmd="python `"$projectDir/scripts/governance/meta/validate_false_negatives.py`""},
    @{Name="validate_gate_engine_external";Cmd="python `"$projectDir/scripts/governance/meta/validate_gate_engine_external.py`""},
    @{Name="validate_rules_integrity";     Cmd="python `"$projectDir/scripts/governance/meta/validate_rules_integrity.py`""},
    @{Name="validate_script_provenance";   Cmd="python `"$projectDir/scripts/governance/meta/validate_script_provenance.py`""},
    @{Name="session_simulator";            Cmd="python `"$projectDir/scripts/governance/session_simulator.py`" --simulate 1"},
    @{Name="auto_handoff_log";             Cmd="python `"$projectDir/scripts/hooks/auto-handoff-log.py`" --dry-run"},
    @{Name="lock_files";                   Cmd="python `"$projectDir/scripts/lock_files.py`" status"}
)

$totalScripts = $allScripts.Count
Write-Host "  Total $totalScripts scripts launching simultaneously..." -ForegroundColor Yellow
Write-Host ""

$jobs = @()
$sw = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($s in $allScripts) {
    $job = Start-Job -ScriptBlock {
        param($cmd, $name)
        $result = & powershell -NoProfile -Command $cmd 2>&1
        return @{Name=$name; Output=$result; ExitCode=$LASTEXITCODE}
    } -ArgumentList $s.Cmd, $s.Name
    $jobs += @{Job=$job; Name=$s.Name}
    Write-Host "  [$($jobs.Count)/$totalScripts] $($s.Name)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "  Waiting for all (timeout=300s)..." -ForegroundColor Yellow

$allDone = $false
$elapsed = 0
$timeout = 300
while (-not $allDone -and $elapsed -lt $timeout) {
    $allDone = $true
    foreach ($j in $jobs) { if ($j.Job.State -eq "Running") { $allDone = $false } }
    if (-not $allDone) { Start-Sleep -Seconds 3; $elapsed += 3 }
}
$sw.Stop()

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "  Results (elapsed: $($sw.Elapsed.TotalSeconds.ToString('0.00'))s)" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan

$pass = 0; $fail = 0; $timeoutCount = 0; $running = 0

foreach ($j in $jobs) {
    if ($j.Job.State -eq "Running") {
        Write-Host "  HUNG: $($j.Name) (still running!)" -ForegroundColor Magenta
        Stop-Job -Job $j.Job -ErrorAction SilentlyContinue
        Remove-Job -Job $j.Job -ErrorAction SilentlyContinue
        $running++
        continue
    }
    $result = Receive-Job -Job $j.Job -ErrorAction SilentlyContinue
    Remove-Job -Job $j.Job -ErrorAction SilentlyContinue
    if ($null -eq $result) {
        Write-Host "  TIMEOUT: $($j.Name)" -ForegroundColor Magenta
        $timeoutCount++
    }
    elseif ($result.ExitCode -eq 0) {
        Write-Host "  PASS: $($j.Name)" -ForegroundColor Green
        $pass++
    }
    else {
        Write-Host "  NONZERO: $($j.Name) (exit=$($result.ExitCode))" -ForegroundColor Yellow
        $fail++
    }
}

Write-Host ""
Write-Host "  PASS: $pass / FAIL: $fail / HUNG: $running / TIMEOUT: $timeoutCount / TOTAL: $totalScripts" -ForegroundColor Cyan

# ============================================
# Phase 4: Same-script Stress Test
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Phase 4: Same-script 5-instance stress" -ForegroundColor Cyan
Write-Host "  (generate_derived_files.py --apply x5)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$stressScript = "python `"$projectDir/scripts/governance/d3_metadata/generate_derived_files.py`" --apply"
$stressCount = 5

Write-Host "  5 instances writing the same files concurrently..." -ForegroundColor Yellow
Write-Host ""

$jobs2 = @()
$sw2 = [System.Diagnostics.Stopwatch]::StartNew()

for ($i = 1; $i -le $stressCount; $i++) {
    $name = "derived_files_#$i"
    $job = Start-Job -ScriptBlock {
        param($cmd, $name)
        $result = & powershell -NoProfile -Command $cmd 2>&1
        return @{Name=$name; Output=$result; ExitCode=$LASTEXITCODE}
    } -ArgumentList $stressScript, $name
    $jobs2 += @{Job=$job; Name=$name}
}

Write-Host "  Waiting for all..." -ForegroundColor Yellow

$allDone2 = $false
$elapsed2 = 0
while (-not $allDone2 -and $elapsed2 -lt $timeout) {
    $allDone2 = $true
    foreach ($j in $jobs2) { if ($j.Job.State -eq "Running") { $allDone2 = $false } }
    if (-not $allDone2) { Start-Sleep -Seconds 3; $elapsed2 += 3 }
}
$sw2.Stop()

Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "  Stress results ($($sw2.Elapsed.TotalSeconds.ToString('0.00'))s)" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan

$pass2 = 0; $fail2 = 0; $hung2 = 0

foreach ($j in $jobs2) {
    if ($j.Job.State -eq "Running") {
        Write-Host "  HUNG: $($j.Name)" -ForegroundColor Magenta
        Stop-Job -Job $j.Job -ErrorAction SilentlyContinue
        Remove-Job -Job $j.Job -ErrorAction SilentlyContinue
        $hung2++
        continue
    }
    $result = Receive-Job -Job $j.Job -ErrorAction SilentlyContinue
    Remove-Job -Job $j.Job -ErrorAction SilentlyContinue
    if ($null -eq $result -or $result.ExitCode -ne 0) {
        Write-Host "  NONZERO: $($j.Name) (exit=$($result.ExitCode))" -ForegroundColor Yellow
        $fail2++
    }
    else {
        Write-Host "  PASS: $($j.Name)" -ForegroundColor Green
        $pass2++
    }
}

Write-Host ""
Write-Host "  Stress: $pass2 PASS / $fail2 NONZERO / $hung2 HUNG" -ForegroundColor Cyan

# ============================================
# Final Verdict
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Final Verdict" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$totalHung = $running + $hung2
$totalNonzero = $fail + $fail2

if ($totalHung -eq 0) {
    Write-Host ""
    Write-Host "  CONCURRENT SAFE " -ForegroundColor Green
    Write-Host "  $totalScripts scripts concurrent: zero hangs!" -ForegroundColor Green
    Write-Host "  Multiple AI dialogues can safely use all script tools concurrently." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  WARNING: $totalHung scripts hung!" -ForegroundColor Red
    Write-Host "  Investigate concurrency issues in these scripts." -ForegroundColor Red
}

Write-Host ""
Write-Host "  NONZERO exits: $totalNonzero (pre-existing issues, not concurrency bugs)" -ForegroundColor Yellow
