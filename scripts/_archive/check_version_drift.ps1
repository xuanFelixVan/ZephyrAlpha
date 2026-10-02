$ErrorActionPreference = "Stop"
$dir = "d:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos"
$indexPath = Join-Path $dir "00_index_trading_decision.md"
$index = Get-Content $indexPath -Raw
$files = Get-ChildItem -Path $dir -Filter '*.md' | Where-Object { $_.Name -ne '00_index_trading_decision.md' }

$mismatchCount = 0
$checkedCount = 0

foreach ($f in $files) {
    $content = Get-Content $f.FullName -Raw
    if ($content -match '(?m)^version:\s*([^\s\r\n]+)') {
        $actualVersion = $matches[1].Trim()
        $name = $f.BaseName
        $pattern = [regex]::Escape($name)
        $regex = [regex]"($pattern)[^\|`r`n]*v?([0-9]+\.[0-9]+\.[0-9]+)"
        $matches_in_index = $regex.Matches($index)
        $seen = @{}
        foreach ($m in $matches_in_index) {
            $refVersion = $m.Groups[2].Value
            $key = "$name|$refVersion"
            if (-not $seen.ContainsKey($key)) {
                $seen[$key] = $true
                $checkedCount++
                if ($refVersion -ne $actualVersion) {
                    Write-Output "MISMATCH: $name | index_ref=$refVersion | actual=$actualVersion"
                    $mismatchCount++
                }
            }
        }
    }
}

Write-Output ""
Write-Output "=== Summary ==="
Write-Output "Total version references checked: $checkedCount"
Write-Output "Mismatches found: $mismatchCount"
