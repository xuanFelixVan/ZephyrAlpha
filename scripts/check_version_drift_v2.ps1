$dir = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"
$indexPath = Join-Path $dir "00_index_trading_decision.md"
$index = Get-Content $indexPath -Raw
$files = Get-ChildItem -Path $dir -Filter '*.md' | Where-Object { $_.Name -ne '00_index_trading_decision.md' }

# Build a map of actual versions (strip quotes/whitespace)
$actualMap = @{}
foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw
    if ($content -match '(?m)^version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?') {
        $actualMap[$f.BaseName] = $matches[1]
    }
}

# Scan index for version references in current-state sections (lines before revision history)
# Revision history starts around "## 8." or the date/version table header row
$indexLines = Get-Content $indexPath
$revHistoryStart = 0
for ($i = 0; $i -lt $indexLines.Count; $i++) {
    if ($indexLines[$i] -match '^\|\s*\u65E5\u671F\s*\|') { $revHistoryStart = $i; break }
}
Write-Output "Revision history starts at line $($revHistoryStart + 1)"
Write-Output ""

$mismatches = @()
foreach ($name in $actualMap.Keys) {
    $actual = $actualMap[$name]
    # Search only in lines before revision history (current-state sections)
    for ($i = 0; $i -lt $revHistoryStart; $i++) {
        $line = $indexLines[$i]
        if ($line -match [regex]::Escape($name)) {
            # Find all version patterns on this line near the doc name
            $vers = [regex]::Matches($line, 'v?([0-9]+\.[0-9]+\.[0-9]+)')
            foreach ($v in $vers) {
                $refVer = $v.Groups[1].Value
                if ($refVer -ne $actual) {
                    $mismatches += "L$($i+1): $name | ref=$refVer | actual=$actual"
                }
            }
        }
    }
}

if ($mismatches.Count -eq 0) {
    Write-Output "NO MISMATCHES in current-state sections (before revision history)"
} else {
    Write-Output "=== Mismatches in current-state sections ==="
    $mismatches | ForEach-Object { Write-Output $_ }
}

Write-Output ""
Write-Output "=== All actual versions ==="
$actualMap.GetEnumerator() | Sort-Object Name | ForEach-Object { Write-Output "$($_.Key) => $($_.Value)" }
