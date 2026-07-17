# PRE-COMMIT HOOK - Blueprint-code alignment gate
# Iron Law 6 + L3 prevention layer: force-validate blueprint construction_progress alignment with disk on any module code change
#
# Install: Copy-Item scripts/governance/d5_architecture/pre_commit_hook.ps1 .git/hooks/pre_commit
#
# Logic:
#   1. Detect which src/zephyr/ submodules are affected by staged changes
#   2. Map to corresponding blueprint.md paths
#   3. Run validate_blueprint_implementation_docs.py
#   4. If misaligned -> block commit (non-zero exit)
param()

$ErrorActionPreference = "Stop"
$REPO_ROOT = (git rev-parse --show-toplevel)

$STAGED_FILES = git diff --cached --name-only --diff-filter=ACM
$CHANGED_MODULES = @{}

foreach ($f in $STAGED_FILES) {
    if ($f -match '^src/zephyr/([^/]+)/') {
        $module = $Matches[1]
        $CHANGED_MODULES[$module] = $true
    }
}

if ($CHANGED_MODULES.Count -eq 0) {
    exit 0
}

Write-Host "[PRE-COMMIT] Iron Law 6/L3 check: detected code changes in modules: $($CHANGED_MODULES.Keys -join ', ')"
Write-Host "[PRE-COMMIT] Running blueprint-code alignment validation..."

$VALIDATE_SCRIPT = Join-Path $REPO_ROOT "scripts/governance/d5_architecture/validate_blueprint_implementation_docs.py"
$PYTHON_EXE = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PYTHON_EXE) {
    Write-Host "[PRE-COMMIT] Error: python not found"
    exit 1
}

$output = & $PYTHON_EXE $VALIDATE_SCRIPT 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    Write-Host $output
    Write-Host ""
    Write-Host "=" * 60
    Write-Host "[PRE-COMMIT] Iron Law 6 blocked: blueprint-code misaligned!"
    Write-Host "[PRE-COMMIT] Action guide:"
    Write-Host "  1. Confirm which modules your code changes affect"
    Write-Host "  2. Read the corresponding module's blueprint.md"
    Write-Host "  3. Update construction_progress and implementation status sections in blueprint.md"
    Write-Host "  4. Re-commit"
    Write-Host "=" * 60
    exit 1
}

Write-Host "[PRE-COMMIT] Blueprint-code alignment validation passed."
exit 0
