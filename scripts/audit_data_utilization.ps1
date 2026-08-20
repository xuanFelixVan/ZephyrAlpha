# ============================================================================
# audit_data_utilization.ps1
# ----------------------------------------------------------------------------
# Continuous validation script for design memo 63 (business data asset
# utilization audit). For each dataset entry in data_asset_registry.yaml:
#   1. derive the physical table name from entity_name (last dot segment)
#   2. count word-boundary references in src/zephyr (recursive, *.py)
#   3. count word-boundary references in design_memos (*.md, memo 63 excluded
#      to avoid self-reference bias)
#   4. classify coverage status per entry:
#        covered   = src_refs > 0 and memo_refs > 0
#        code_only = src_refs > 0 and memo_refs = 0  (documentation gap)
#        doc_only  = src_refs = 0 and memo_refs > 0  (planned/registered)
#        zero_ref  = both zero                       (idle candidate)
# Output: docs/_working/data_utilization_audit_snapshot_<yyyy-MM-dd>.md
#         frontmatter is exactly three lines (--- / ttl: task_bound / ---)
#         per EXEMPT-ZONE-FM gate rules for the docs/_working/ zone.
# Policy: warn-only, always exits 0 on success (memo 63 section 9 states the
#         documentation coverage gate must not block CI, warn only).
# Note: comments and output labels are kept pure ASCII per ENCODING-SAFETY.
# ============================================================================

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$registry = Join-Path $repoRoot 'docs\01_policies_and_standards\_registry\catalogs\data_asset_registry.yaml'
$srcDir   = Join-Path $repoRoot 'src\zephyr'
$memoDir  = Join-Path $repoRoot 'docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos'
$outDir   = Join-Path $repoRoot 'docs\_working'
$selfMemo = '63_data_utilization_audit.md'
$date     = Get-Date -Format 'yyyy-MM-dd'
$outFile  = Join-Path $outDir "data_utilization_audit_snapshot_$date.md"

# --- Step 1: parse dataset entries (dataset_id + entity_name) from registry --
$entries = New-Object System.Collections.Generic.List[object]
$currentId = $null
foreach ($line in Get-Content $registry) {
    if ($line -match '^\s*-\s*dataset_id:\s*(\S+)\s*$') {
        $currentId = $Matches[1]
        continue
    }
    if ($line -match '^\s*entity_name:\s*(\S+)\s*$' -and $currentId) {
        $entity = $Matches[1]
        $table  = ($entity -split '\.')[-1]
        $entries.Add([pscustomobject]@{ DatasetId = $currentId; EntityName = $entity; Table = $table })
        $currentId = $null
    }
}
if ($entries.Count -eq 0) {
    Write-Host 'ERROR: no dataset entries parsed from registry'
    exit 1
}

# Unique table list, longest first so regex alternation prefers longer names.
$tables = $entries | Select-Object -ExpandProperty Table -Unique | Sort-Object { $_.Length } -Descending
$pattern = '\b(' + ($tables -join '|') + ')\b'

# --- Step 2/3: count references, one combined-regex pass per file set --------
$srcCounts  = @{}
$memoCounts = @{}
foreach ($t in $tables) { $srcCounts[$t] = 0; $memoCounts[$t] = 0 }

Get-ChildItem -Path $srcDir -Recurse -Filter '*.py' -File | ForEach-Object {
    $c = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($c) {
        foreach ($m in [regex]::Matches($c, $pattern)) { $srcCounts[$m.Groups[1].Value]++ }
    }
}
Get-ChildItem -Path $memoDir -Filter '*.md' -File | Where-Object { $_.Name -ne $selfMemo } | ForEach-Object {
    $c = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
    if ($c) {
        foreach ($m in [regex]::Matches($c, $pattern)) { $memoCounts[$m.Groups[1].Value]++ }
    }
}

# --- Step 4: classify and build result rows ----------------------------------
$rows = foreach ($e in ($entries | Sort-Object DatasetId)) {
    $s = $srcCounts[$e.Table]
    $d = $memoCounts[$e.Table]
    $status = 'zero_ref'
    if ($s -gt 0 -and $d -gt 0) { $status = 'covered' }
    elseif ($s -gt 0)           { $status = 'code_only' }
    elseif ($d -gt 0)           { $status = 'doc_only' }
    [pscustomobject]@{
        Id     = $e.DatasetId
        Entity = $e.EntityName
        Table  = $e.Table
        Src    = $s
        Memo   = $d
        Status = $status
    }
}

$nCovered  = ($rows | Where-Object Status -eq 'covered').Count
$nCodeOnly = ($rows | Where-Object Status -eq 'code_only').Count
$nDocOnly  = ($rows | Where-Object Status -eq 'doc_only').Count
$nZeroRef  = ($rows | Where-Object Status -eq 'zero_ref').Count

# --- Step 5: write markdown snapshot -----------------------------------------
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('ttl: task_bound')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('# Data Utilization Audit Snapshot (memo 63 continuous validation)')
[void]$sb.AppendLine('')
[void]$sb.AppendLine("- date: $date")
[void]$sb.AppendLine('- script: scripts/audit_data_utilization.ps1')
[void]$sb.AppendLine('- registry: docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml')
[void]$sb.AppendLine('- scope: src/zephyr (*.py) + design_memos (*.md, memo 63 self excluded), word-boundary match')
[void]$sb.AppendLine('- policy: warn-only, exit 0 (memo 63 section 9: no blocking gate)')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Summary')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| metric | value |')
[void]$sb.AppendLine('|---|---|')
[void]$sb.AppendLine("| dataset entries parsed | $($rows.Count) |")
[void]$sb.AppendLine("| unique tables | $($tables.Count) |")
[void]$sb.AppendLine("| covered (src>0 and memo>0) | $nCovered |")
[void]$sb.AppendLine("| code_only / doc gap (src>0, memo=0) | $nCodeOnly |")
[void]$sb.AppendLine("| doc_only / planned only (src=0, memo>0) | $nDocOnly |")
[void]$sb.AppendLine("| zero_ref / idle candidate | $nZeroRef |")
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Matrix')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| dataset_id | entity_name | table | src_refs | memo_refs | status |')
[void]$sb.AppendLine('|---|---|---|---|---|---|')
foreach ($r in $rows) {
    [void]$sb.AppendLine("| $($r.Id) | $($r.Entity) | $($r.Table) | $($r.Src) | $($r.Memo) | $($r.Status) |")
}

# Write UTF-8 without BOM so the three-line frontmatter stays byte-clean.
[System.IO.File]::WriteAllText($outFile, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))

# --- Console summary ----------------------------------------------------------
Write-Host "snapshot written: $outFile"
Write-Host "entries=$($rows.Count) tables=$($tables.Count) covered=$nCovered code_only=$nCodeOnly doc_only=$nDocOnly zero_ref=$nZeroRef"
if ($nCodeOnly -gt 0) {
    Write-Host "WARN: $nCodeOnly dataset entries are code_only (documentation gap), see snapshot matrix"
}
exit 0
